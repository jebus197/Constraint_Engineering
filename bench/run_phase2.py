#!/usr/bin/env python3
"""
Phase 2 experiment runner — frontier test with checkpoint/resume and cost control.

CX remediation applied (2026-03-18):
  Fix 1: Fresh runs default; --resume requires manifest-compatible checkpoint
  Fix 2: Strict assessor parsing with returncode checks
  Fix 3: Transient vs fatal API error separation
  Fix 4: Schema C scoped to selected configs; all env keys pre-validated
  Fix 5: Mandatory preflight pilot before multi-task batch
  Fix 6: Atomic checkpoint/ledger writes (temp+rename)

Usage:
    # Fresh run (clears any existing checkpoint)
    source .env && python3 bench/run_phase2.py --cost-cap 100

    # Resume after crash (validates manifest compatibility)
    source .env && python3 bench/run_phase2.py --resume --cost-cap 100

    # Pilot: 3 tasks, one model (also used as mandatory preflight)
    source .env && python3 bench/run_phase2.py --pilot --config gpt-5.4

    # Dry run
    python3 bench/run_phase2.py --dry-run
"""

import argparse
import hashlib
import json
import os
import random
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_benchmark import (
    CDSFL_DIRECTIVES,
    PLACEBO_DIRECTIVES,
    PROVIDERS,
    AdaptiveThrottle,
    _err,
    compose_directives,
    estimate_call_cost,
    load_directives,
    load_domain_directives,
    make_throttle,
    run_adaptive,
    run_control,
    run_cross_model,
    run_placebo,
)

# ---------------------------------------------------------------------------
# Model configurations — API-only (no codex exec as benchmark provider)
# ---------------------------------------------------------------------------

# CC configs — models CC runs (non-Anthropic only).
# Anthropic models are run by CX.
CORE_CONFIGS: dict[str, dict[str, Any]] = {
    "gpt-5.4": {
        "model": "gpt-5.4",
        "provider": "openai",
        "description": "GPT-5.4 (OpenAI flagship)",
        "env_key": "OPENAI_API_KEY",
    },
    "gemini-3.1-pro": {
        "model": "gemini-3.1-pro-preview",
        "provider": "gemini",
        "description": "Gemini 3.1 Pro Preview (Google flagship)",
        "env_key": "GOOGLE_API_KEY",
    },
}

EXTENDED_CONFIGS: dict[str, dict[str, Any]] = {
    "o4-mini": {
        "model": "o4-mini",
        "provider": "openai-reasoning",
        "description": "OpenAI o4-mini (reasoning)",
        "env_key": "OPENAI_API_KEY",
    },
    "gemini-3-flash": {
        "model": "gemini-3-flash-preview",
        "provider": "gemini",
        "description": "Gemini 3 Flash Preview (Google fast frontier)",
        "env_key": "GOOGLE_API_KEY",
    },
    "llama-4-scout": {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "provider": "groq",
        "description": "Llama 4 Scout (via Groq)",
        "env_key": "GROQ_API_KEY",
    },
}

# CX-only configs — for Schema C coordination and --config override.
CX_CONFIGS: dict[str, dict[str, Any]] = {
    "sonnet-4.6": {
        "model": "claude-sonnet-4-6",
        "provider": "anthropic",
        "description": "Claude Sonnet 4.6 (standard) [CX-only]",
        "env_key": "ANTHROPIC_API_KEY",
    },
    "sonnet-4-thinking": {
        "model": "claude-sonnet-4-6",
        "provider": "anthropic-thinking",
        "description": "Claude Sonnet 4.6 (extended thinking) [CX-only]",
        "env_key": "ANTHROPIC_API_KEY",
    },
}

# Schema C model pairs (maximise training-bias diversity)
CROSS_MODEL_PAIRS = [
    ("sonnet-4-thinking", "gpt-5.4"),
    ("gpt-5.4", "gemini-3.1-pro"),
    ("gemini-3.1-pro", "sonnet-4-thinking"),
]

# Pilot subset (3 tasks for difficulty calibration)
PILOT_TASK_IDS = ["ft-002", "ft-010", "ft-021"]


# ---------------------------------------------------------------------------
# Fix 1: Run manifest — hash of configs + model IDs + directives
# ---------------------------------------------------------------------------

def _compute_manifest(
    configs: dict, directives: str, max_passes: int,
    task_ids: list[str] | None = None,
    domain_directives_hash: str | None = None,
    variant: str | None = None,
) -> str:
    """Deterministic hash of the run configuration for checkpoint compatibility.

    Includes task IDs so checkpoints from a different task selection are
    detected as incompatible (CX Round 2, defect 4).

    Gemini R5 fix 1: includes domain directives hash so changes to
    domain-specific instruction files invalidate the checkpoint.

    EPP M2 fix 2: includes variant so changing --variant invalidates
    the checkpoint (variant determines which domain directives load).
    """
    manifest_data = json.dumps({
        "configs": {k: {"model": v["model"], "provider": v["provider"]}
                    for k, v in sorted(configs.items())},
        "directives_hash": hashlib.sha256(directives.encode()).hexdigest()[:16],
        "domain_directives_hash": domain_directives_hash,
        "variant": variant,
        "max_passes": max_passes,
        "task_ids": sorted(task_ids) if task_ids else None,
    }, sort_keys=True)
    return hashlib.sha256(manifest_data.encode()).hexdigest()[:32]


def _hash_domain_directives(directives_dir: Path) -> str | None:
    """Hash all domain directive files for manifest reproducibility.

    Gemini R5 fix 1: ensures checkpoint invalidation when directives change.
    """
    if not directives_dir.is_dir():
        return None
    h = hashlib.sha256()
    for txt_file in sorted(directives_dir.rglob("*.txt")):
        # EPP M2 fix 7: use relative path, not just filename — moving a file
        # between domain folders (e.g. chemistry/ → physics/) must invalidate
        h.update(str(txt_file.relative_to(directives_dir)).encode())
        h.update(txt_file.read_bytes())
    digest = h.hexdigest()[:16]
    return digest if digest != hashlib.sha256(b"").hexdigest()[:16] else None


# ---------------------------------------------------------------------------
# Fix 6: Atomic file writes (temp + rename)
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, data: str) -> None:
    """Write data to path atomically via temp file + rename."""
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent, suffix=".tmp", prefix=path.stem + "_"
    )
    try:
        with os.fdopen(fd, "w") as f:
            f.write(data)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Cost ledger (Fix 6: atomic writes)
# ---------------------------------------------------------------------------

class CostLedger:
    """Track cumulative API spend with a hard cap."""

    def __init__(self, cap_usd: float = 70.0, ledger_path: Path | None = None):
        self.cap = cap_usd
        self.total = 0.0
        self.by_provider: dict[str, float] = {}
        self.by_config: dict[str, float] = {}
        self.ledger_path = ledger_path

    def load_existing(self) -> bool:
        """Explicitly load — only called when --resume is active.

        Returns True on success, False if the ledger was corrupt (CX R7 fix).
        """
        self.was_corrupt = False
        if self.ledger_path and self.ledger_path.exists():
            try:
                data = json.loads(self.ledger_path.read_text())
                self.total = data.get("total_usd", 0.0)
                self.by_provider = data.get("by_provider", {})
                self.by_config = data.get("by_config", {})
                return True
            except (json.JSONDecodeError, KeyError) as e:
                _err(f"  [ledger] WARNING: corrupt ledger file ({e})")
                self.was_corrupt = True
                self.total = 0.0
                self.by_provider = {}
                self.by_config = {}
                return False
        return True  # no ledger file = fresh start

    def record(self, provider: str, config_name: str, cost: float) -> None:
        self.total += cost
        self.by_provider[provider] = self.by_provider.get(provider, 0.0) + cost
        self.by_config[config_name] = self.by_config.get(config_name, 0.0) + cost
        self._save()

    def check_cap(self) -> bool:
        return self.total < self.cap

    def _save(self) -> None:
        if self.ledger_path:
            data = {
                "total_usd": round(self.total, 4),
                "cap_usd": self.cap,
                "remaining_usd": round(self.cap - self.total, 4),
                "by_provider": {k: round(v, 4) for k, v in self.by_provider.items()},
                "by_config": {k: round(v, 4) for k, v in self.by_config.items()},
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            _atomic_write(self.ledger_path, json.dumps(data, indent=2) + "\n")

    def summary(self) -> str:
        return (
            f"Cost: ${self.total:.4f} / ${self.cap:.2f} "
            f"(${self.cap - self.total:.4f} remaining)"
        )


# ---------------------------------------------------------------------------
# Checkpoint (Fix 1: manifest, Fix 6: atomic writes, corruption handling)
# ---------------------------------------------------------------------------

class Checkpoint:
    """Persist completed task results for crash-safe resume."""

    def __init__(self, checkpoint_path: Path, manifest: str = ""):
        self.path = checkpoint_path
        self.manifest = manifest
        self.completed: dict[str, dict[str, Any]] = {}

    def load(self) -> bool:
        """Load checkpoint. Returns True if compatible, False if incompatible.

        Sets self.was_corrupt if the checkpoint file existed but was unreadable,
        so the caller can also reset the ledger (CX R5 fix).
        """
        self.was_corrupt = False
        if not self.path.exists():
            return True  # no checkpoint = fresh start, compatible
        try:
            data = json.loads(self.path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            _err(f"  [checkpoint] WARNING: corrupt checkpoint ({e}), starting fresh")
            self.was_corrupt = True
            return True

        stored_manifest = data.get("manifest", "")
        if not stored_manifest:
            _err(f"  [checkpoint] INCOMPATIBLE: checkpoint has no manifest — "
                 f"cannot verify compatibility (pre-manifest checkpoint)")
            return False
        elif stored_manifest != self.manifest:
            _err(f"  [checkpoint] INCOMPATIBLE: manifest mismatch")
            _err(f"    stored:  {stored_manifest}")
            _err(f"    current: {self.manifest}")
            return False

        self.completed = data.get("completed", {})
        _err(f"  [checkpoint] loaded {len(self.completed)} completed task-configs")
        return True

    def clear(self) -> None:
        """Remove existing checkpoint file."""
        if self.path.exists():
            self.path.unlink()
        self.completed = {}

    def _save(self) -> None:
        data = {
            "manifest": self.manifest,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "completed_count": len(self.completed),
            "completed": self.completed,
        }
        _atomic_write(self.path, json.dumps(data, indent=2) + "\n")

    def key(self, config_name: str, task_id: str, condition: str) -> str:
        # Gemini R2 fix 3: escape colons to prevent key collisions
        # (e.g. task_id "ft:001" would collide with config "ft" + task "001")
        def _esc(s: str) -> str:
            return s.replace("\\", "\\\\").replace(":", "\\:")
        return f"{_esc(config_name)}:{_esc(task_id)}:{_esc(condition)}"

    def is_done(self, config_name: str, task_id: str, condition: str) -> bool:
        return self.key(config_name, task_id, condition) in self.completed

    def record(self, config_name: str, task_id: str, condition: str, result: dict) -> None:
        k = self.key(config_name, task_id, condition)
        self.completed[k] = result
        self._save()


# ---------------------------------------------------------------------------
# Fix 3: Fatal API error detection
# ---------------------------------------------------------------------------

class FatalAPIError(Exception):
    """Non-recoverable API error — do not retry."""
    pass


def _check_fatal_error(exc: Exception) -> None:
    """Raise FatalAPIError if the exception is non-recoverable."""
    exc_str = str(exc).lower()
    fatal_patterns = [
        "insufficient_quota",
        "invalid_api_key",
        "authentication",
        "permission",
        "invalid_request_error",
        "model_not_found",
        "billing_not_active",
        "account_deactivated",
    ]
    for pat in fatal_patterns:
        if pat in exc_str:
            raise FatalAPIError(f"Fatal API error (non-recoverable): {exc}") from exc


# ---------------------------------------------------------------------------
# Task loading (Phase 2 format — no seeded_faults required)
# ---------------------------------------------------------------------------

REQUIRED_P2_FIELDS = {"id", "domain", "prompt", "category", "verification_method"}


def load_frontier_tasks(tasks_dir: Path) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    if not tasks_dir.is_dir():
        _err(f"Frontier tasks directory not found: {tasks_dir}")
        return tasks
    for json_path in sorted(tasks_dir.rglob("*.json")):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                task = json.load(f)
            task["_source_file"] = str(json_path.relative_to(tasks_dir))
            tasks.append(task)
        except (json.JSONDecodeError, OSError) as exc:
            _err(f"WARNING: skipping {json_path}: {exc}")
    return tasks


def validate_frontier_task(task: dict[str, Any]) -> list[str]:
    errors = []
    source = task.get("_source_file", "<unknown>")
    missing = REQUIRED_P2_FIELDS - task.keys()
    if missing:
        errors.append(f"{source}: missing fields: {missing}")
    # CX R7 fix 2: enforce string type on task ID to prevent type-collision
    # in checkpoint keys (e.g. int 1 and string "1" would collide)
    tid = task.get("id")
    if tid is not None and not isinstance(tid, str):
        errors.append(f"{source}: 'id' must be a string, got {type(tid).__name__}: {tid}")
    return errors


# ---------------------------------------------------------------------------
# Fix 5: Preflight pilot
# ---------------------------------------------------------------------------

def run_preflight(
    tasks: list[dict[str, Any]],
    configs: dict[str, dict[str, Any]],
    directives: str,
    max_passes: int,
    ledger: CostLedger | None = None,
) -> bool:
    """Run one task with one config end-to-end. Returns True on success.

    CX R2 fix 7: preflight calls are metered through the ledger so the
    cost cap accounts for all API spend, not just main-loop calls.
    """
    _err(f"\n{'='*60}")
    _err(f"PREFLIGHT PILOT — validating infrastructure")
    _err(f"{'='*60}")

    # Pick cheapest config (prefer groq > gemini > openai)
    provider_priority = ["groq", "gemini", "openai", "openai-reasoning"]
    pilot_config_name = None
    pilot_config = None
    for prov in provider_priority:
        for name, cfg in configs.items():
            if cfg["provider"] == prov:
                pilot_config_name = name
                pilot_config = cfg
                break
        if pilot_config:
            break
    if not pilot_config:
        pilot_config_name = next(iter(configs))
        pilot_config = configs[pilot_config_name]

    pilot_task = tasks[0]
    _err(f"  Config: {pilot_config_name} ({pilot_config['description']})")
    _err(f"  Task: {pilot_task['id']} ({pilot_task['category']})")

    model = pilot_config["model"]
    provider = pilot_config["provider"]
    throttle = make_throttle(provider)

    try:
        # CX R3 fix 3: check cap before preflight API calls
        if ledger and not ledger.check_cap():
            _err(f"  [preflight] SKIPPED — cost cap already reached: {ledger.summary()}")
            return True  # Don't fail preflight on cap — just skip the spend

        # Test control call
        _err(f"  [preflight] control call ...")
        t0 = time.monotonic()
        ctrl = run_control(pilot_task, model, provider)
        elapsed = time.monotonic() - t0
        _err(f"  [preflight] control done ({elapsed:.1f}s, {len(ctrl.get('response',''))} chars)")

        # Meter preflight control call
        if ledger:
            cost = estimate_call_cost(provider, len(pilot_task["prompt"]),
                                      len(ctrl.get("response", "")))
            ledger.record(provider, f"preflight_{pilot_config_name}", cost)
            _err(f"  [preflight] metered: ${cost:.4f} | {ledger.summary()}")

        # CX R3 fix 3: check cap before CE call
        if ledger and not ledger.check_cap():
            _err(f"  [preflight] cost cap reached after control — skipping CE pass")
            _err(f"  [preflight] PASSED (partial — control only)")
            return True

        # Test one CE pass
        _err(f"  [preflight] CE pass 1 ...")
        t0 = time.monotonic()
        ce = run_adaptive(pilot_task, model, provider, directives, 1, throttle, confer_after=99)
        elapsed = time.monotonic() - t0
        _err(f"  [preflight] CE pass done ({elapsed:.1f}s)")

        # Meter preflight CE call
        if ledger:
            ce_resp = sum(len(p.get("response", "")) for p in ce.get("passes", []))
            cost = estimate_call_cost(provider, len(pilot_task["prompt"]), ce_resp)
            ledger.record(provider, f"preflight_{pilot_config_name}", cost)
            _err(f"  [preflight] metered: ${cost:.4f} | {ledger.summary()}")

        # Gemini R2 fix 7: smoke-test confer mechanism (CLI availability)
        _err(f"  [preflight] testing confer CLI availability ...")
        import subprocess as sp
        confer_ok = True
        try:
            sp.run(["claude", "--version"], capture_output=True, timeout=10)
        except (FileNotFoundError, sp.TimeoutExpired):
            _err(f"  [preflight] WARNING: 'claude' CLI not available — confer will use INFRA_FAIL fallback")
            confer_ok = False
        try:
            sp.run(["codex", "--version"], capture_output=True, timeout=10)
        except (FileNotFoundError, sp.TimeoutExpired):
            _err(f"  [preflight] WARNING: 'codex' CLI not available — confer will use INFRA_FAIL fallback")
            confer_ok = False
        if confer_ok:
            _err(f"  [preflight] confer CLIs available")
        else:
            _err(f"  [preflight] confer CLIs missing — adaptive passes will still run but cannot confer")

        _err(f"  [preflight] PASSED — infrastructure validated")
        return True

    except FatalAPIError as e:
        _err(f"  [preflight] FATAL: {e}")
        _err(f"  [preflight] FAILED — fix the error above before running")
        return False
    except Exception as e:
        _err(f"  [preflight] ERROR: {e}")
        _err(f"  [preflight] FAILED — fix the error above before running")
        return False


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_task_conditions(
    task: dict[str, Any],
    config_name: str,
    config: dict[str, Any],
    directives: str,
    max_passes: int,
    checkpoint: Checkpoint,
    ledger: CostLedger,
    throttle: AdaptiveThrottle,
) -> dict[str, Any]:
    """Run all 3 conditions (control, CDSFL, calibration baseline) for one task + config."""
    task_id = task["id"]
    model = config["model"]
    provider = config["provider"]
    results: dict[str, Any] = {"task_id": task_id, "config": config_name}

    # CX R3 fix 3: check cap before any API call, not just after
    if not ledger.check_cap():
        _err(f"  *** COST CAP REACHED (pre-call): {ledger.summary()} ***")
        return results

    # 1. Control (single pass, no directives)
    if not checkpoint.is_done(config_name, task_id, "control"):
        _err(f"    [control] ...")
        try:
            ctrl = run_control(task, model, provider)
        except Exception as e:
            _check_fatal_error(e)  # Fix 3: raise FatalAPIError if non-recoverable
            raise
        # EPP M2 fix 4: include directive length in cost estimate
        prompt_len = len(task["prompt"]) + len(directives)
        cost = estimate_call_cost(provider, prompt_len, len(ctrl.get("response", "")))
        ledger.record(provider, config_name, cost)
        checkpoint.record(config_name, task_id, "control", ctrl)
        results["control"] = ctrl
    else:
        _err(f"    [control] already done (checkpoint)")

    if not ledger.check_cap():
        _err(f"  *** COST CAP REACHED: {ledger.summary()} ***")
        return results

    # 2. CE (adaptive up to max_passes with confer)
    if not checkpoint.is_done(config_name, task_id, "cdsfl"):
        _err(f"    [cdsfl] ...")
        try:
            # Gemini R4 fix 3: pass cost cap check into adaptive loop
            cdsfl = run_adaptive(task, model, provider, directives, max_passes, throttle,
                                 cost_check_fn=ledger.check_cap)
        except Exception as e:
            _check_fatal_error(e)
            raise
        actual_passes = len(cdsfl.get("passes", []))
        total_resp = sum(len(p.get("response", "")) for p in cdsfl.get("passes", []))
        # Gemini R2 fix 2: estimate actual prompt size including growing drafts.
        # EPP M2 fix 4: include directive length in base prompt size.
        prompt_base = len(task["prompt"]) + len(directives)
        avg_draft_size = total_resp // max(actual_passes, 1)
        estimated_input = sum(prompt_base + avg_draft_size * i for i in range(actual_passes))
        cost = estimate_call_cost(provider, estimated_input, total_resp)
        ledger.record(provider, config_name, cost)
        checkpoint.record(config_name, task_id, "cdsfl", cdsfl)
        results["cdsfl"] = cdsfl
    else:
        _err(f"    [cdsfl] already done (checkpoint)")

    if not ledger.check_cap():
        _err(f"  *** COST CAP REACHED: {ledger.summary()} ***")
        return results

    # 3. Calibration baseline (adaptive with generic instructions)
    if not checkpoint.is_done(config_name, task_id, "placebo"):
        _err(f"    [placebo] ...")
        try:
            # Gemini R4 fix 3 + EPP M4 fix 4: pass cost cap check
            plc = run_placebo(task, model, provider, max_passes, throttle,
                              cost_check_fn=ledger.check_cap)
        except Exception as e:
            _check_fatal_error(e)
            raise
        actual_passes = len(plc.get("passes", []))
        total_resp = sum(len(p.get("response", "")) for p in plc.get("passes", []))
        # Gemini R2 fix 2: estimate actual prompt size including growing drafts
        # EPP M2 fix 4: include PLACEBO directive length
        prompt_base = len(task["prompt"]) + len(PLACEBO_DIRECTIVES)
        avg_draft_size = total_resp // max(actual_passes, 1)
        estimated_input = sum(prompt_base + avg_draft_size * i for i in range(actual_passes))
        cost = estimate_call_cost(provider, estimated_input, total_resp)
        ledger.record(provider, config_name, cost)
        checkpoint.record(config_name, task_id, "placebo", plc)
        results["placebo"] = plc
    else:
        _err(f"    [placebo] already done (checkpoint)")

    return results


def run_schema_c(
    task: dict[str, Any],
    pair_name: str,
    config_a: dict[str, Any],
    config_b: dict[str, Any],
    directives: str,
    max_passes: int,
    checkpoint: Checkpoint,
    ledger: CostLedger,
    throttle_a: AdaptiveThrottle,
    throttle_b: AdaptiveThrottle,
) -> dict[str, Any] | None:
    """Run Schema C cross-model adversarial for one task + model pair."""
    task_id = task["id"]
    cond_key = f"schema_c_{pair_name}"

    if checkpoint.is_done(cond_key, task_id, "cross_model"):
        _err(f"    [schema-c:{pair_name}] already done (checkpoint)")
        return None

    if not ledger.check_cap():
        _err(f"  *** COST CAP REACHED: {ledger.summary()} ***")
        return None

    _err(f"    [schema-c:{pair_name}] ...")
    try:
        result = run_cross_model(
            task,
            config_a["model"], config_a["provider"],
            config_b["model"], config_b["provider"],
            directives, max_passes,
            throttle_a, throttle_b,
            cost_check_fn=ledger.check_cap,  # EPP M4 fix 2: mid-run cost check
        )
    except Exception as e:
        _check_fatal_error(e)
        raise

    total_resp = sum(len(p.get("response", "")) for p in result.get("passes", []))
    cost_a = estimate_call_cost(config_a["provider"], len(task["prompt"]) * 3, total_resp // 2)
    cost_b = estimate_call_cost(config_b["provider"], len(task["prompt"]) * 3, total_resp // 2)
    ledger.record(config_a["provider"], f"schema_c_{pair_name}", cost_a)
    ledger.record(config_b["provider"], f"schema_c_{pair_name}", cost_b)
    checkpoint.record(cond_key, task_id, "cross_model", result)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CE Phase 2 — frontier test with checkpoint/resume and cost control.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", type=str, default=None,
                        help="Run a single config only")
    parser.add_argument("--task-ids", type=str, default=None,
                        help="Comma-separated task IDs")
    parser.add_argument("--passes", type=int, default=5, choices=range(3, 6),
                        help="Max P-passes (3-5, default: 5)",
                        metavar="N")
    parser.add_argument("--cost-cap", type=float, default=100.0,
                        help="Hard cost cap in USD (default: 100.0)")
    default_output_dir = str(Path(__file__).parent / "results" / "phase2")
    parser.add_argument("--output-dir", type=str, default=default_output_dir,
                        help="Output directory")
    default_tasks_dir = str(Path(__file__).parent / "tasks_frontier")
    parser.add_argument("--tasks-dir", type=str, default=default_tasks_dir,
                        help="Frontier tasks directory")
    parser.add_argument("--pilot", action="store_true",
                        help="Pilot mode: 3 tasks, core configs only")
    parser.add_argument("--core-only", action="store_true",
                        help="Run core configs only (skip extended)")
    parser.add_argument("--skip-schema-c", action="store_true",
                        help="Skip Schema C cross-model runs")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from compatible checkpoint (rejects incompatible)")
    parser.add_argument("--skip-preflight", action="store_true",
                        help="Skip preflight pilot (use only after a successful pilot)")
    parser.add_argument("--variant", type=str, default=None,
                        help="Select a specific domain directive variant (e.g. 'building'). "
                             "Gemini R2 fix 8: was previously hardcoded to None.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show plan without API calls")

    args = parser.parse_args()

    # Setup paths
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir = Path(args.tasks_dir)

    # Load tasks
    _err(f"Loading frontier tasks from {tasks_dir} ...")
    all_tasks = load_frontier_tasks(tasks_dir)
    if not all_tasks:
        _err("No frontier tasks found. Create them first.")
        sys.exit(1)

    errors = []
    for t in all_tasks:
        errors.extend(validate_frontier_task(t))

    # CX R6 fix 2: detect duplicate task IDs (would collide in checkpoint keys)
    seen_ids: dict[str, str] = {}
    for t in all_tasks:
        tid = t.get("id", "")
        source = t.get("_source_file", "<unknown>")
        if tid in seen_ids:
            errors.append(
                f"Duplicate task ID '{tid}': found in {seen_ids[tid]} and {source}"
            )
        else:
            seen_ids[tid] = source

    if errors:
        for e in errors:
            _err(f"  VALIDATION ERROR: {e}")
        sys.exit(1)

    # Filter tasks
    if args.pilot:
        task_ids = set(PILOT_TASK_IDS)
    elif args.task_ids:
        task_ids = set(args.task_ids.split(","))
    else:
        task_ids = None

    if task_ids:
        tasks = [t for t in all_tasks if t["id"] in task_ids]
        missing = task_ids - {t["id"] for t in tasks}
        if missing:
            _err(f"WARNING: task IDs not found: {sorted(missing)}")
    else:
        tasks = all_tasks

    if not tasks:
        _err("ERROR: no tasks matched the selection. Check --task-ids or --pilot.")
        sys.exit(1)

    # EPP M3 fix 4: randomize task order to prevent systematic attrition bias.
    # Fixed seed derived from manifest ensures reproducibility across resume.
    # Without randomization, tasks processed late (alphabetically) are
    # disproportionately likely to be truncated by cost cap exhaustion.
    task_seed = int(hashlib.sha256("task_order".encode()).hexdigest()[:8], 16)
    random.Random(task_seed).shuffle(tasks)

    _err(f"Selected {len(tasks)} frontier tasks (randomized order, seed={task_seed}).")

    # Determine configs
    if args.config:
        all_configs = {**CORE_CONFIGS, **EXTENDED_CONFIGS, **CX_CONFIGS}
        if args.config not in all_configs:
            _err(f"ERROR: unknown config '{args.config}'")
            sys.exit(1)
        configs = {args.config: all_configs[args.config]}
    elif args.pilot or args.core_only:
        configs = CORE_CONFIGS
    else:
        configs = {**CORE_CONFIGS, **EXTENDED_CONFIGS}

    # Fix 4 (R2) + CX R3 fix 1: Pre-validate env keys ONLY for configs that
    # will actually run. Schema C pairs only validated when:
    #   (a) --skip-schema-c is NOT set
    #   (b) NOT in --pilot mode
    #   (c) BOTH models in available configs
    #   (d) Selected tasks actually contain at least one schema_c task
    all_needed_configs = dict(configs)
    has_schema_c_tasks = any(t.get("schema_c", False) for t in tasks)
    if not args.skip_schema_c and not args.pilot and has_schema_c_tasks:
        available_for_schema_c = {**configs, **CX_CONFIGS}
        for pair_a_name, pair_b_name in CROSS_MODEL_PAIRS:
            if pair_a_name in available_for_schema_c and pair_b_name in available_for_schema_c:
                all_needed_configs[pair_a_name] = available_for_schema_c[pair_a_name]
                all_needed_configs[pair_b_name] = available_for_schema_c[pair_b_name]

    missing_keys = set()
    for name, cfg in all_needed_configs.items():
        if cfg.get("env_key") and not os.environ.get(cfg["env_key"]):
            missing_keys.add(f"{cfg['env_key']} (needed for {name})")
    if missing_keys and not args.dry_run:
        _err("ERROR: missing environment variables:")
        for mk in sorted(missing_keys):
            _err(f"  - {mk}")
        sys.exit(1)

    # Compute manifest (includes task IDs for checkpoint compatibility — CX R2 fix 4)
    # CX R3 fix 2: include CX_CONFIGS in manifest when Schema C is active
    directives = CDSFL_DIRECTIVES
    selected_task_ids = [t["id"] for t in tasks]
    manifest_configs = dict(configs)
    if not args.skip_schema_c and not args.pilot and has_schema_c_tasks:
        manifest_configs.update(CX_CONFIGS)
    # Gemini R5 fix 1: include domain directives in manifest
    directives_dir = Path(__file__).parent / "directives"
    dd_hash = _hash_domain_directives(directives_dir)
    manifest = _compute_manifest(manifest_configs, directives, args.passes, selected_task_ids, dd_hash, args.variant)

    # Dry run
    if args.dry_run:
        _err(f"\n=== DRY RUN ===")
        _err(f"Manifest: {manifest}")
        _err(f"Tasks: {len(tasks)}")
        _err(f"Configs: {len(configs)}")
        _err(f"Max passes: {args.passes}")
        _err(f"Cost cap: ${args.cost_cap}")
        calls_per_task = 1 + args.passes + args.passes
        total_calls = len(tasks) * len(configs) * calls_per_task
        _err(f"Estimated API calls (main): {total_calls}")
        if not args.skip_schema_c and not args.pilot:
            schema_c_tasks = [t for t in tasks if t.get("schema_c", False)]
            sc_calls = len(schema_c_tasks) * len(CROSS_MODEL_PAIRS) * args.passes
            _err(f"Schema C tasks: {len(schema_c_tasks)}, calls: {sc_calls}")
            total_calls += sc_calls
        _err(f"Total estimated API calls: {total_calls}")
        _err(f"\nConfigs:")
        for name, cfg in configs.items():
            _err(f"  {name}: {cfg['description']}")
        _err(f"\nTasks:")
        for t in tasks:
            sc = " [Schema C]" if t.get("schema_c", False) else ""
            sb = " [Schema B]" if t.get("schema_b", False) else ""
            _err(f"  {t['id']} ({t['category']}){sc}{sb}")
        sys.exit(0)

    # Fix 1: Checkpoint handling — fresh by default, resume requires compatibility
    checkpoint_path = output_dir / "checkpoint.json"
    ledger_path = output_dir / "cost_ledger.json"

    checkpoint = Checkpoint(checkpoint_path, manifest=manifest)
    ledger = CostLedger(cap_usd=args.cost_cap, ledger_path=ledger_path)

    if args.resume:
        compatible = checkpoint.load()
        if not compatible:
            _err("ERROR: existing checkpoint is incompatible with current config.")
            _err("Options:")
            _err("  1. Remove checkpoint and start fresh (drop --resume)")
            _err("  2. Use the same config that created the checkpoint")
            sys.exit(1)
        if checkpoint.was_corrupt:
            # CX R5 fix: don't load stale ledger when checkpoint was corrupt
            _err(f"  [resume] checkpoint was corrupt — ledger also reset to avoid asymmetry")
        else:
            # CX R6 fix 1: require ledger to exist when checkpoint has completed items
            if checkpoint.completed and ledger_path and not ledger_path.exists():
                _err("ERROR: checkpoint has completed items but ledger file is missing.")
                _err("  Cost cap cannot be enforced without spend history.")
                _err("  Options:")
                _err("    1. Start fresh (drop --resume)")
                _err("    2. Restore the ledger file from backup")
                sys.exit(1)
            ledger_ok = ledger.load_existing()
            # CX R7 fix 1: refuse resume if ledger is corrupt with completed items
            if not ledger_ok and checkpoint.completed:
                _err("ERROR: ledger file is corrupt and checkpoint has completed items.")
                _err("  Cost cap cannot be enforced without valid spend history.")
                _err("  Options:")
                _err("    1. Start fresh (drop --resume)")
                _err("    2. Restore the ledger file from backup")
                sys.exit(1)
            # Warn if ledger loaded but shows $0 despite completed checkpoint items
            if checkpoint.completed and ledger.total == 0.0:
                _err(f"  [resume] WARNING: checkpoint has {len(checkpoint.completed)} "
                     f"completed items but ledger shows $0 — possible ledger corruption")
        _err(f"  [resume] Resuming with {len(checkpoint.completed)} completed items")
    else:
        # Fresh run — clear any stale checkpoint
        if checkpoint_path.exists():
            _err(f"  [fresh] Clearing existing checkpoint ({checkpoint_path})")
            checkpoint.clear()
        if ledger_path.exists():
            ledger_path.unlink()

    # Fix 5: Mandatory preflight pilot (CX R2 fix 7: metered through ledger)
    if not args.skip_preflight and not args.pilot:
        preflight_ok = run_preflight(tasks, configs, directives, args.passes, ledger=ledger)
        if not preflight_ok:
            _err("\nPreflight FAILED. Fix errors above, then retry.")
            _err("To skip preflight after a successful pilot: --skip-preflight")
            sys.exit(1)

    _err(f"\n{'='*60}")
    _err(f"PHASE 2 FRONTIER TEST")
    _err(f"  Tasks: {len(tasks)} | Configs: {len(configs)} | Max passes: {args.passes}")
    _err(f"  Manifest: {manifest}")
    _err(f"  Cost cap: ${args.cost_cap} | {ledger.summary()}")
    _err(f"{'='*60}")

    directives_dir = Path(__file__).parent / "directives"
    experiment_start = time.monotonic()

    # Main loop: sequential by config, then by task
    cost_cap_hit = False
    for config_name, config in configs.items():
        provider = config["provider"]
        throttle = make_throttle(provider)

        _err(f"\n{'='*60}")
        _err(f"CONFIG: {config_name} — {config['description']}")
        _err(f"{'='*60}")

        for idx, task in enumerate(tasks, 1):
            task_id = task["id"]
            domain = task.get("domain", "")
            _err(f"\n  [{idx}/{len(tasks)}] Task {task_id} ({task['category']}, {domain})")

            domain_specific = load_domain_directives(directives_dir, domain, args.variant)
            task_directives = compose_directives(directives, domain_specific, "universal+domain")

            try:
                result = run_task_conditions(
                    task, config_name, config, task_directives,
                    args.passes, checkpoint, ledger, throttle,
                )
            except FatalAPIError as e:
                # Fix 3: graceful exit on fatal errors, state already saved
                _err(f"\n*** FATAL API ERROR: {e} ***")
                _err(f"All completed work has been checkpointed.")
                _err(f"Fix the error, then resume: --resume")
                sys.exit(2)
            except Exception as e:
                # EPP P5 fix 1: catch transient non-fatal errors (timeouts,
                # 5xx after retries, task-specific 400s) — log and continue
                # to next task instead of crashing the entire batch.
                _err(f"\n*** TASK ERROR: {e} ***")
                _err(f"  Skipping task {task_id} for config {config_name} — continuing")
                continue

            _err(f"  {ledger.summary()}")

            if not ledger.check_cap():
                _err(f"\n*** COST CAP REACHED — stopping safely ***")
                _err(f"All completed work has been checkpointed.")
                _err(f"Resume with: --resume --cost-cap {args.cost_cap + 20}")
                cost_cap_hit = True
                break

        if cost_cap_hit:
            break

    # Fix 4: Schema C scoped — only run pairs where both models are
    # in the selected configs OR explicitly in CX_CONFIGS
    if not args.skip_schema_c and not args.pilot and not cost_cap_hit and ledger.check_cap():
        schema_c_tasks = [t for t in tasks if t.get("schema_c", False)]
        if schema_c_tasks:
            _err(f"\n{'='*60}")
            _err(f"SCHEMA C: Cross-Model Adversarial ({len(schema_c_tasks)} tasks)")
            _err(f"{'='*60}")

            available_configs = {**configs, **CX_CONFIGS}

            for pair_a_name, pair_b_name in CROSS_MODEL_PAIRS:
                if pair_a_name not in available_configs or pair_b_name not in available_configs:
                    _err(f"  Skipping pair {pair_a_name} vs {pair_b_name} — config not available")
                    continue

                # Verify env keys for this pair — skip entire pair if any key missing
                config_a = available_configs[pair_a_name]
                config_b = available_configs[pair_b_name]
                skip_pair = False
                for pcfg in (config_a, config_b):
                    if pcfg.get("env_key") and not os.environ.get(pcfg["env_key"]):
                        _err(f"  Skipping pair {pair_a_name} vs {pair_b_name} — missing {pcfg['env_key']}")
                        skip_pair = True
                        break
                if skip_pair:
                    continue

                pair_name = f"{pair_a_name}_vs_{pair_b_name}"
                throttle_a = make_throttle(config_a["provider"])
                throttle_b = make_throttle(config_b["provider"])

                _err(f"\n  Pair: {pair_a_name} vs {pair_b_name}")

                for task in schema_c_tasks:
                    _err(f"    Task {task['id']}")
                    domain_specific = load_domain_directives(
                        directives_dir, task.get("domain", ""), args.variant
                    )
                    task_directives = compose_directives(
                        directives, domain_specific, "universal+domain"
                    )

                    try:
                        run_schema_c(
                            task, pair_name, config_a, config_b,
                            task_directives, args.passes,
                            checkpoint, ledger, throttle_a, throttle_b,
                        )
                    except FatalAPIError as e:
                        _err(f"\n*** FATAL API ERROR during Schema C: {e} ***")
                        _err(f"Checkpointed. Resume with --resume")
                        sys.exit(2)
                    except Exception as e:
                        # EPP P5 fix 1: log and continue
                        _err(f"\n*** SCHEMA C TASK ERROR: {e} ***")
                        _err(f"  Skipping task {task['id']} for pair {pair_name} — continuing")
                        continue

                    _err(f"    {ledger.summary()}")

                    if not ledger.check_cap():
                        _err(f"\n*** COST CAP REACHED during Schema C ***")
                        cost_cap_hit = True
                        break
                if cost_cap_hit:
                    break

    total_elapsed = time.monotonic() - experiment_start

    # --- Generate deferred-items report ---
    deferred_items = []
    resolved_count = 0
    infra_failure_count = 0
    total_confer_calls = 0
    total_cc_failures = 0
    total_cx_failures = 0

    for key, result in checkpoint.completed.items():
        if isinstance(result, dict):
            st = result.get("status", "")
            confer_stats = result.get("confer_stats", {})
            total_confer_calls += confer_stats.get("total_confer_calls", 0)
            total_cc_failures += confer_stats.get("cc_cli_failures", 0)
            total_cx_failures += confer_stats.get("cx_cli_failures", 0)
            if st == "DEFERRED":
                deferred_items.append({
                    "key": key,
                    "status": st,
                    "actual_passes": result.get("actual_passes", 0),
                    "last_confer_outcome": result.get("last_confer_outcome", ""),
                    "confer_logs": result.get("confer_logs", []),
                })
            elif st == "DEFERRED_INFRA":
                infra_failure_count += 1
                deferred_items.append({
                    "key": key,
                    "status": st,
                    "actual_passes": result.get("actual_passes", 0),
                    "last_confer_outcome": result.get("last_confer_outcome", ""),
                    "confer_logs": result.get("confer_logs", []),
                })
            elif st == "RESOLVED":
                resolved_count += 1

    # Gemini R3 fix 4: compare checkpoint count vs expected to detect "ghosting"
    # (incomplete runs that look complete in the report)
    # EPP M2 fix 3: include Schema C items in expected count
    conditions_per_task = 3  # control, cdsfl, placebo
    expected_items = len(tasks) * len(configs) * conditions_per_task
    if not args.skip_schema_c and not args.pilot:
        schema_c_tasks = [t for t in tasks if t.get("schema_c", False)]
        available_configs = {**configs, **CX_CONFIGS}
        active_pairs = sum(
            1 for a, b in CROSS_MODEL_PAIRS
            if a in available_configs and b in available_configs
        )
        expected_items += len(schema_c_tasks) * active_pairs
    completed_items = len(checkpoint.completed)
    completeness_pct = (completed_items / expected_items * 100) if expected_items > 0 else 0

    deferred_path = output_dir / "deferred_for_review.json"
    deferred_report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "manifest": manifest,
        "summary": {
            "resolved": resolved_count,
            "deferred": len(deferred_items),
            "infra_failures": infra_failure_count,
            "total_confer_calls": total_confer_calls,
            "cc_cli_failures": total_cc_failures,
            "cx_cli_failures": total_cx_failures,
            "cx_failure_rate": (
                f"{total_cx_failures/total_confer_calls*100:.1f}%"
                if total_confer_calls > 0 else "N/A"
            ),
            "completeness": {
                "expected_items": expected_items,
                "completed_items": completed_items,
                "completeness_pct": round(completeness_pct, 1),
                "cost_cap_hit": cost_cap_hit,
            },
        },
        "deferred_items": deferred_items,
    }
    if completeness_pct < 100:
        _err(f"\n  *** WARNING: run is {completeness_pct:.1f}% complete "
             f"({completed_items}/{expected_items} items) ***")
    _atomic_write(deferred_path, json.dumps(deferred_report, indent=2) + "\n")

    _err(f"\n{'='*60}")
    _err(f"PHASE 2 COMPLETE")
    _err(f"  Total time: {total_elapsed:.0f}s ({total_elapsed/60:.1f} min)")
    _err(f"  {ledger.summary()}")
    _err(f"  RESOLVED: {resolved_count} | DEFERRED: {len(deferred_items)}"
         f" | INFRA_FAIL: {infra_failure_count}")
    if total_confer_calls > 0:
        _err(f"  Confer calls: {total_confer_calls} "
             f"(CC failures: {total_cc_failures}, "
             f"CX failures: {total_cx_failures}, "
             f"CX failure rate: {total_cx_failures/total_confer_calls*100:.1f}%)")
    _err(f"  Checkpoint: {checkpoint.path}")
    _err(f"  Cost ledger: {ledger.ledger_path}")
    _err(f"  Deferred report: {deferred_path}")
    _err(f"{'='*60}")


if __name__ == "__main__":
    main()
