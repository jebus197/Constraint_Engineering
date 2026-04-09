#!/usr/bin/env python3
"""Parameterised reference runner for CDSFL experiments (Exp 37+, Bench Run 2).

Extracts the parameterised entry point from run_exp36_evidence.py so future
experiments don't need per-experiment runner scripts. The test article,
context files, domain, and convergence parameters are all configurable.

All heavy lifting (dispatch, parsing, immune pipeline, convergence) is in
runner_core.py, immune_agents.py, insect_brain.py, etc. This runner
orchestrates those modules with configurable parameters.

Includes the A1-A5 fixes from Exp 36:
  A1: Registry windowing (OPEN/CONTESTED full detail, settled compact, hidden)
  A2: Rho as C6 convergence condition (discovery efficiency churn detector)
  A3: Contested -> HIL escalation after max_contested_rounds
  A4: Gamma-aware ITC (suppress DEGRADATION restart when rho is healthy)
  A5: Dedup-aware CC2v (skip already-confirmed/escalated findings)

Usage:
    python3 bench/reference_runner.py run --test-article bench/evidence.py
    python3 bench/reference_runner.py run --test-article bench/evidence.py \\
        --context bench/verification_chain.py --topology relay
    python3 bench/reference_runner.py run --config experiment.json
    python3 bench/reference_runner.py preflight
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Path setup
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    load_default_config,
    dispatch,
    save_output,
    _log,
    CircuitBreakerTripped,
    ExperimentConfig,
    ModelConfig,
)
from dynamic_management import (
    DynamicManager,
    DynamicManagementConfig,
    ModelSpec,
    CapabilityFingerprint,
    Task,
    Finding,
    ModelResponse,
)
from runner_core import (
    source_env,
    build_model_specs,
    parse_findings,
    dispatch_to_model,
    format_findings_for_context,
    INITIAL_FINGERPRINTS,
    MODEL_SPECS,
    CONVERGENCE_EXCLUDED_MODELS,
    CONTEXT_CHAR_BUDGET,
)
from run_exp17_immune import (
    TASKS,
    TASK_MARKERS,
    REVIEW_AREAS,
    FINDING_FORMAT,
    RoundTelemetry,
    run_layer1_preflight,
    _should_decompose,
    _build_verified_facts,
    _build_explicit_unknowns,
    _find_model_spec,
    _report_dispatch_failure,
    _record_throughput,
    _effective_capacity,
)
from decomposed_dispatch import (
    decomposed_dispatch,
    DecomposedChunk,
    DecomposedResult,
    save_decomposed_result,
)
from bench.insect_brain import InsectBrain
from bench.cdsfl_registry.composer import (
    compose,
    DirectivePacket,
    ComposedDirectiveSet,
    COMPOSER_MODEL_MAP,
    build_interaction_pattern,
    INTERACTION_PATTERN_PRESETS,
)
from input_complexity import (
    compute_gamma_input,
    compute_gamma_output,
    compute_amplification,
    AmplificationHistory,
    AdaptiveQuestionOptimiser,
)
from bench.endocrine import (
    EndocrineLayer,
    EndocrineReport,
    RoundTiming,
    HealthScan,
    FixEvaluation,
    PacingSignal,
)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration dataclass
# ─────────────────────────────────────────────────────────────────────────────

MODEL_ROSTER = {
    "CC2": "Claude Opus 4.6 (Anthropic)",
    "Codex": "GPT-5.4 Codex (OpenAI)",
    "Gemini": "Gemini 3.1 Pro (Google)",
    "DeepSeek": "DeepSeek Reasoner (DeepSeek)",
    "ChatGPT": "GPT-5.4 (OpenAI)",
}

FINGERPRINT_DIR = REPO_ROOT / "bench" / "fingerprints"


@dataclass
class RunnerConfig:
    """All parameters for a reference experiment run."""

    # Target and context
    test_article: str = ""
    context_files: List[str] = field(default_factory=list)

    # Topology
    topology: str = "star"
    relay_mode: str = "directed"

    # Prompt pattern
    pattern: str = "fff"

    # Round limits
    max_rounds: int = 21
    extension_cap: int = 24
    wall_clock_cap_s: int = 28800
    earliest_stop_round: int = 12

    # Models
    models: List[str] = field(
        default_factory=lambda: ["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"]
    )

    # Naming
    experiment_name: str = ""

    # Domain for directive composition
    domain: str = "software"

    # Resume from checkpoint
    resume: bool = False

    # Convergence tuning
    rho_threshold: float = 0.25
    rho_rolling_window: int = 3
    consecutive_rounds_required: int = 2

    # Derived constants (set from the above or left at defaults)
    max_novel_findings: int = 2
    open_ch_stability_window: int = 3
    max_open_crit_high: int = 0
    rho_earliest_round: int = 12
    stall_window: int = 3
    stall_earliest_round: int = 15
    stall_gamma_advisory: float = 0.30
    stall_gamma_terminate: float = 0.45
    verification_batch_size: int = 6
    verification_min_round: int = 6
    verification_confidence_threshold: float = 0.7
    gamma_telemetry_only_until: int = 14
    gamma_soft_gate_until: int = 19
    gamma_soft_threshold: float = 0.30
    gamma_hard_threshold: float = 0.35
    min_rounds_for_gamma: int = 3
    max_contested_rounds: int = 5
    multiturn_chunk_target: int = 30_000

    def __post_init__(self):
        if not self.experiment_name and self.test_article:
            stem = Path(self.test_article).stem
            self.experiment_name = f"ref_{stem}"
        if self.rho_earliest_round != self.earliest_stop_round:
            self.rho_earliest_round = self.earliest_stop_round

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RunnerConfig":
        """Build config from a JSON-compatible dict (ignores unknown keys)."""
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in valid})

    @classmethod
    def from_json(cls, path: str) -> "RunnerConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


# ─────────────────────────────────────────────────────────────────────────────
# FindingRegistry (identical to Exp 36 — A1 windowing, A3 HIL escalation)
# ─────────────────────────────────────────────────────────────────────────────

class FindingRegistry:
    """Canonical finding registry — runner-owned, models read/propose only.

    A1 fix: windowed build_summary (full detail for active, compact for
    settled, hidden for refuted/duplicate).
    A3 fix: escalate_stale_contested after max_contested_rounds.
    """

    def __init__(self):
        self.entries: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1
        self._alias_map: Dict[str, str] = {}

    def register(self, finding: Finding, model_id: str) -> str:
        canonical_id = f"C{self._next_id:04d}"
        self._next_id += 1
        self._alias_map[f"{model_id}:{finding.finding_id}"] = canonical_id
        self.entries[canonical_id] = {
            "canonical_id": canonical_id,
            "source_model": model_id,
            "source_aliases": [finding.finding_id],
            "severity": finding.severity,
            "description": finding.description[:500],
            "proposed_fix": finding.proposed_fix[:500] if finding.proposed_fix else "",
            "status": "OPEN",
            "open_since_round": getattr(finding, "round_idx", 0),
            "last_status_change_round": getattr(finding, "round_idx", 0),
            "verdicts": [],
            "verified": finding.verified,
            "escalated": finding.escalated,
            "flaw_class": getattr(finding, "flaw_class", 0),
        }
        return canonical_id

    def add_verdict(
        self, canonical_id: str, model_id: str, verdict: str,
        round_idx: int, evidence: str = "",
    ):
        if canonical_id not in self.entries:
            return
        self.entries[canonical_id]["verdicts"].append({
            "model": model_id, "verdict": verdict,
            "round": round_idx, "evidence": evidence[:200],
        })
        self.entries[canonical_id]["last_status_change_round"] = round_idx

    def resolve(
        self, canonical_id: str, status: str, round_idx: int,
        merged_into: Optional[str] = None,
    ):
        if canonical_id in self.entries:
            self.entries[canonical_id]["status"] = status
            self.entries[canonical_id]["last_status_change_round"] = round_idx
            if merged_into:
                self.entries[canonical_id]["merged_into"] = merged_into

    def mark_verified(self, canonical_id: str):
        if canonical_id in self.entries:
            self.entries[canonical_id]["verified"] = True

    def lookup_alias(self, model_id: str, local_id: str) -> Optional[str]:
        return self._alias_map.get(f"{model_id}:{local_id}")

    def open_crit_high_count(self) -> int:
        return sum(
            1 for e in self.entries.values()
            if e["status"] in ("OPEN", "CONTESTED") and e["severity"] >= 0.7
        )

    def contested_count(self, current_round: int) -> int:
        count = 0
        for e in self.entries.values():
            if e["status"] == "MERGED":
                continue
            challenges = [v for v in e["verdicts"] if v["verdict"] == "CHALLENGE"]
            if not challenges:
                continue
            confirms = [v for v in e["verdicts"] if v["verdict"] == "CONFIRM"]
            latest_confirm_round = max((v["round"] for v in confirms), default=-1)
            unresolved = [v for v in challenges if v["round"] > latest_confirm_round]
            if unresolved:
                oldest = min(v["round"] for v in unresolved)
                if current_round - oldest > 1:
                    count += 1
        return count

    def build_summary(self, round_idx: int) -> str:
        """A1 fix: windowed registry summary."""
        if not self.entries:
            return "(No findings registered yet.)"
        full_detail_statuses = ("OPEN", "CONTESTED", "REOPENED")
        compact_statuses = ("CONFIRMED", "UNCONFIRMED", "CLOSED", "MERGED")
        hidden_statuses = ("REFUTED", "DUPLICATE")
        full_detail = [e for e in self.entries.values() if e["status"] in full_detail_statuses]
        compact = [e for e in self.entries.values() if e["status"] in compact_statuses]
        hidden_count = sum(1 for e in self.entries.values() if e["status"] in hidden_statuses)

        lines = [
            f"=== FINDING REGISTRY (Round {round_idx}) ===",
            f"Total: {len(self.entries)} canonical findings",
            f"Active: {len(full_detail)} | Settled: {len(compact)} | Hidden: {hidden_count}",
            f"Open CRIT/HIGH: {self.open_crit_high_count()}",
            "",
        ]
        for status in full_detail_statuses:
            group = [e for e in full_detail if e["status"] == status]
            if not group:
                continue
            lines.append(f"--- {status} ({len(group)}) ---")
            for e in sorted(group, key=lambda x: -x["severity"]):
                verdict_summary = ", ".join(
                    f"{v['model']}:{v['verdict']}" for v in e["verdicts"][-3:]
                )
                lines.append(
                    f"  {e['canonical_id']} (sev {e['severity']:.2f}) "
                    f"[{e['source_model']}] {e['description'][:120]}"
                )
                if verdict_summary:
                    lines.append(f"    Verdicts: {verdict_summary}")
                if e.get("proposed_fix"):
                    lines.append(f"    Fix: {e['proposed_fix'][:100]}")
            lines.append("")
        if compact:
            lines.append(f"--- SETTLED ({len(compact)}) (do not re-describe) ---")
            lines.append(
                "These findings are confirmed, closed, or merged. "
                "Do not CHALLENGE or re-describe them. "
                "To reopen, issue REOPEN <ID> with specific new evidence."
            )
            for e in sorted(compact, key=lambda x: x["canonical_id"]):
                tag = e["status"]
                merged_note = f" -> {e['merged_into']}" if e.get("merged_into") else ""
                lines.append(
                    f"  [{tag}] {e['canonical_id']}{merged_note}: "
                    f"{e['description'][:80]}"
                )
            lines.append("")
        if hidden_count > 0:
            lines.append(f"({hidden_count} findings hidden: refuted or duplicate)")
            lines.append("")
        lines.append("=== END REGISTRY ===")
        return "\n".join(lines)

    def escalate_stale_contested(self, current_round: int, max_contested_rounds: int = 5) -> List[str]:
        """A3 fix: escalate CONTESTED findings to HIL after threshold."""
        escalated_ids = []
        for fid, entry in self.entries.items():
            if entry.get("status") != "CONTESTED":
                continue
            contested_since = entry.get("last_status_change_round", 0)
            rounds_contested = current_round - contested_since
            if rounds_contested >= max_contested_rounds:
                entry["status"] = "UNCONFIRMED"
                entry["hil_escalated"] = True
                entry["hil_reason"] = (
                    f"Contested for {rounds_contested} rounds "
                    f"(threshold: {max_contested_rounds})"
                )
                escalated_ids.append(fid)
                _log(f"  A3 HIL escalation: {fid} contested for "
                     f"{rounds_contested} rounds -> UNCONFIRMED + HIL flag")
        return escalated_ids

    def auto_resolve_contested(self, current_round: int):
        for fid, entry in self.entries.items():
            if entry.get("status") != "CONTESTED":
                continue
            recent_verdicts = [
                v for v in entry.get("verdicts", [])
                if v.get("round", 0) >= current_round - 2
            ]
            challenges = sum(1 for v in recent_verdicts if v.get("verdict") == "CHALLENGE")
            confirms = sum(1 for v in recent_verdicts if v.get("verdict") == "CONFIRM")
            if challenges >= 3 and confirms == 0:
                entry["status"] = "REFUTED"
                _log(f"  Auto-refuted {fid}: {challenges} challenges, 0 defences in last 3 rounds")

    def to_dict(self) -> dict:
        return {
            "entries": self.entries,
            "next_id": self._next_id,
            "alias_map": self._alias_map,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FindingRegistry":
        reg = cls()
        reg.entries = data.get("entries", {})
        reg._next_id = data.get("next_id", 1)
        reg._alias_map = data.get("alias_map", {})
        return reg


# ─────────────────────────────────────────────────────────────────────────────
# Verdict parser
# ─────────────────────────────────────────────────────────────────────────────

_VERDICT_RE = re.compile(
    r'^\s*(?:[*]{0,2}[-*]?\s*)?(CONFIRM|CHALLENGE|EXTEND|MERGE|REOPEN)\s+(C\d{4})'
    r'(?:\s*[*]{0,2}\s*[\|<\-\u2014\u2013\u2190]+\s*(.*))?',
    re.MULTILINE,
)


def _parse_verdicts(
    response_text: str, model_id: str, round_idx: int,
) -> List[Tuple[str, str, str]]:
    results: List[Tuple[str, str, str]] = []
    for m in _VERDICT_RE.finditer(response_text):
        results.append((m.group(1), m.group(2), (m.group(3) or "").strip()))
    return results


def _resolve_merge_source(
    evidence: str, model_id: str, registry: FindingRegistry,
) -> Optional[str]:
    m = re.search(r'(?:F|C)(\d+)', evidence)
    if not m:
        return None
    local_id = m.group(0)
    canonical = registry.lookup_alias(model_id, local_id)
    if canonical:
        return canonical
    if local_id in registry.entries:
        return local_id
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Gamma estimation and convergence
# ─────────────────────────────────────────────────────────────────────────────

def _estimate_gamma(novelty_counts: List[int], min_rounds: int = 3) -> float:
    n = len(novelty_counts)
    if n < min_rounds:
        return 0.0
    cumulative = []
    total = 0
    for c in novelty_counts:
        total += c
        cumulative.append(total)
    if total == 0:
        return 0.0
    log_x, log_y = [], []
    for i, cum in enumerate(cumulative):
        if cum > 0 and (i + 1) > 0:
            log_x.append(math.log(i + 1))
            log_y.append(math.log(cum))
    if len(log_x) < 2:
        return 0.0
    n_pts = len(log_x)
    sum_x = sum(log_x)
    sum_y = sum(log_y)
    sum_xy = sum(x * y for x, y in zip(log_x, log_y))
    sum_x2 = sum(x * x for x in log_x)
    denom = n_pts * sum_x2 - sum_x * sum_x
    if abs(denom) < 1e-12:
        return 0.0
    beta = (n_pts * sum_xy - sum_x * sum_y) / denom
    return max(0.0, min(1.0, 1.0 - beta))


GAMMA_BANDS = [
    (0.45, float("inf"), "Strong depletion — confirms state-based closure"),
    (0.30, 0.45, "Moderate depletion — consistent with PoC convergence"),
    (0.20, 0.30, "Weak depletion — state closure may be premature"),
    (0.00, 0.20, "Gamma disagrees with state closure — recommend HIL audit"),
]


def _interpret_gamma(gamma: float) -> str:
    for low, high, interpretation in GAMMA_BANDS:
        if low <= gamma < high:
            return interpretation
    return f"Gamma {gamma:.3f} — outside expected range"


def _check_gamma_gate(
    gamma: float, round_idx: int, cfg: RunnerConfig,
) -> Tuple[str, bool]:
    if round_idx <= cfg.gamma_telemetry_only_until:
        return "telemetry", True
    if round_idx <= cfg.gamma_soft_gate_until:
        if gamma < cfg.gamma_soft_threshold:
            return "soft", False
        return "soft", True
    if gamma < cfg.gamma_hard_threshold:
        return "hard", False
    return "hard", True


def _compute_rho(
    novelty_counts: List[int],
    raw_counts: List[int],
    cfg: RunnerConfig,
) -> Tuple[float, float, bool]:
    """A2 fix: discovery efficiency rho with configurable threshold."""
    if not raw_counts or raw_counts[-1] == 0:
        return 0.0, 0.0, False
    rho_current = novelty_counts[-1] / raw_counts[-1] if raw_counts[-1] > 0 else 0.0
    rho_values = []
    for i in range(max(0, len(raw_counts) - cfg.rho_rolling_window), len(raw_counts)):
        if raw_counts[i] > 0:
            rho_values.append(novelty_counts[i] / raw_counts[i])
        else:
            rho_values.append(0.0)
    rho_avg = sum(rho_values) / len(rho_values) if rho_values else 0.0
    round_idx = len(raw_counts) - 1
    churn = rho_avg < cfg.rho_threshold and round_idx >= cfg.rho_earliest_round
    return rho_current, rho_avg, churn


# ─────────────────────────────────────────────────────────────────────────────
# Status transitions and convergence gate
# ─────────────────────────────────────────────────────────────────────────────

def _update_finding_statuses(registry: FindingRegistry, round_idx: int):
    for canonical_id, entry in list(registry.entries.items()):
        if entry["status"] in ("MERGED", "CLOSED"):
            if entry["status"] == "CLOSED":
                reopen_verdicts = [
                    v for v in entry["verdicts"]
                    if v["verdict"] == "REOPEN" and v["round"] == round_idx
                ]
                if reopen_verdicts:
                    registry.resolve(canonical_id, "REOPENED", round_idx)
                    entry["escalated"] = True
                    _log(f"  REOPEN {canonical_id}: escalated to HIL")
            continue
        merge_verdicts = [v for v in entry["verdicts"] if v["verdict"] == "MERGE"]
        if merge_verdicts:
            merged_into = None
            for v in merge_verdicts:
                m = re.search(r'merged_into=(C\d{4})', v.get("evidence", ""))
                if m:
                    merged_into = m.group(1)
                    break
            registry.resolve(canonical_id, "MERGED", round_idx, merged_into=merged_into)
            continue
        confirms = [v for v in entry["verdicts"] if v["verdict"] == "CONFIRM"]
        challenges = [v for v in entry["verdicts"] if v["verdict"] == "CHALLENGE"]
        latest_confirm_round = max((v["round"] for v in confirms), default=-1)
        unresolved_challenges = [v for v in challenges if v["round"] > latest_confirm_round]
        if entry["status"] == "CONFIRMED" and entry.get("verified"):
            registry.resolve(canonical_id, "CLOSED", round_idx)
            _log(f"  CLOSED {canonical_id}: verified fix, challenge-resistant")
            continue
        if entry["status"] == "CONFIRMED" and unresolved_challenges:
            registry.resolve(canonical_id, "CONTESTED", round_idx)
            continue
        if entry["status"] == "CONTESTED" and not unresolved_challenges:
            registry.resolve(canonical_id, "CONFIRMED", round_idx)
            continue
        if entry["status"] == "REOPENED":
            entry["status"] = "OPEN"
        if entry["status"] in ("OPEN", "CONTESTED"):
            confirm_models = {v["model"] for v in confirms}
            independent_count = 1 + len(confirm_models - {entry["source_model"]})
            if independent_count >= 2 and not unresolved_challenges:
                registry.resolve(canonical_id, "CONFIRMED", round_idx)


def _evaluate_gate_conditions(
    round_idx: int,
    registry: FindingRegistry,
    novel_this_round: int,
    gamma: float,
    cfg: RunnerConfig,
    open_ch_history: Optional[List[int]] = None,
    rho_rolling_avg: float = 1.0,
    rho_churn: bool = False,
) -> Tuple[bool, str]:
    if round_idx < cfg.earliest_stop_round:
        return False, f"Too early (round {round_idx} < {cfg.earliest_stop_round})"
    failures = []
    if rho_churn:
        failures.append(f"rho_avg={rho_rolling_avg:.3f} < {cfg.rho_threshold} (churn)")
    open_ch = registry.open_crit_high_count()
    if open_ch_history is not None:
        open_ch_history.append(open_ch)
    if open_ch_history is None or len(open_ch_history) < cfg.open_ch_stability_window:
        if open_ch > 0:
            failures.append(f"open_ch={open_ch} (insufficient history)")
    else:
        window = open_ch_history[-cfg.open_ch_stability_window:]
        if window[-1] > window[0]:
            failures.append(
                f"open_ch={open_ch} (increasing: "
                f"{window[0]}->{window[-1]} over {cfg.open_ch_stability_window}r)"
            )
    if novel_this_round > cfg.max_novel_findings:
        failures.append(f"novel={novel_this_round}")
    contested = registry.contested_count(round_idx)
    if contested > 0:
        failures.append(f"contested={contested}")
    gate_level, gamma_passed = _check_gamma_gate(gamma, round_idx, cfg)
    if not gamma_passed:
        failures.append(f"gamma={gamma:.3f} ({gate_level})")
    if failures:
        return False, f"Gate failed: {', '.join(failures)}"
    return True, (
        f"All conditions met: open_ch={open_ch} (stable), novel={novel_this_round}, "
        f"contested={contested}, gamma={gamma:.3f} ({gate_level})"
    )


def _check_state_convergence(
    round_idx: int,
    registry: FindingRegistry,
    novel_this_round: int,
    gamma: float,
    gate_history: List[bool],
    cfg: RunnerConfig,
    open_ch_history: Optional[List[int]] = None,
    rho_rolling_avg: float = 1.0,
    rho_churn: bool = False,
) -> Tuple[bool, str]:
    passed, reason = _evaluate_gate_conditions(
        round_idx, registry, novel_this_round, gamma, cfg,
        open_ch_history=open_ch_history,
        rho_rolling_avg=rho_rolling_avg,
        rho_churn=rho_churn,
    )
    gate_history.append(passed)
    if not passed:
        return False, reason
    if len(gate_history) < cfg.consecutive_rounds_required:
        return False, f"Gate passed but need {cfg.consecutive_rounds_required} consecutive"
    recent = gate_history[-cfg.consecutive_rounds_required:]
    if all(recent):
        return True, (
            f"STATE_CONVERGED at round {round_idx} "
            f"({cfg.consecutive_rounds_required} consecutive passes): {reason}"
        )
    return False, f"Gate passed this round but not {cfg.consecutive_rounds_required} consecutive"


def _check_stall_convergence(
    round_idx: int,
    registry: FindingRegistry,
    gamma: float,
    stall_history: List[Dict[str, int]],
    cfg: RunnerConfig,
) -> Dict[str, Any]:
    open_ch = registry.open_crit_high_count()
    contested = registry.contested_count(round_idx)
    stall_history.append({"open_ch": open_ch, "contested": contested})
    result: Dict[str, Any] = {
        "round": round_idx, "open_ch": open_ch, "contested": contested,
        "gamma": round(gamma, 4), "stalled": False,
        "tier": "none", "terminate": False, "reason": "",
    }
    if round_idx < cfg.stall_earliest_round:
        result["reason"] = f"round {round_idx} < {cfg.stall_earliest_round}"
        return result
    if len(stall_history) < cfg.stall_window:
        result["reason"] = f"insufficient history ({len(stall_history)} < {cfg.stall_window})"
        return result
    window = stall_history[-cfg.stall_window:]
    open_values = [s["open_ch"] for s in window]
    contested_values = [s["contested"] for s in window]
    if not (all(v == open_values[0] for v in open_values) and
            all(v == contested_values[0] for v in contested_values)):
        result["reason"] = f"not static — open_ch {open_values}, contested {contested_values}"
        return result
    result["stalled"] = True
    if gamma >= cfg.stall_gamma_terminate:
        result["tier"] = "terminate"
        result["terminate"] = True
        result["reason"] = (
            f"STALL_CONVERGED: open_ch={open_ch} static {cfg.stall_window}r, "
            f"contested={contested} static {cfg.stall_window}r, "
            f"gamma={gamma:.3f} >= {cfg.stall_gamma_terminate}"
        )
    elif gamma >= cfg.stall_gamma_advisory:
        result["tier"] = "advisory"
        result["reason"] = (
            f"Stall advisory: open_ch={open_ch} static {cfg.stall_window}r, "
            f"gamma={gamma:.3f} >= {cfg.stall_gamma_advisory}"
        )
    else:
        result["tier"] = "stalled_low_gamma"
        result["reason"] = (
            f"Stalled but gamma={gamma:.3f} < {cfg.stall_gamma_advisory} "
            f"(discovery space may not be depleted)"
        )
    return result


def _check_budget_extension(
    round_idx: int,
    registry: FindingRegistry,
    gamma: float,
    gamma_prev: float,
) -> Tuple[bool, str]:
    reasons = []
    if registry.open_crit_high_count() > 0:
        reasons.append(f"open CRIT/HIGH: {registry.open_crit_high_count()}")
    if registry.contested_count(round_idx) > 0:
        reasons.append(f"contested: {registry.contested_count(round_idx)}")
    if 0.25 <= gamma <= 0.35 and gamma > gamma_prev:
        reasons.append(f"gamma trending up in caution zone: {gamma:.3f}")
    if reasons:
        return True, f"Budget extended: {'; '.join(reasons)}"
    return False, "No extension triggers"


# ─────────────────────────────────────────────────────────────────────────────
# ITC — Adaptive Recovery (A4: gamma-aware)
# ─────────────────────────────────────────────────────────────────────────────

ITC_CAPABILITY_MISMATCH = "CAPABILITY_MISMATCH"
ITC_TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
ITC_DEGRADATION = "DEGRADATION"

_itc_model_state: Dict[str, Dict[str, Any]] = {}
_itc_hil_flags: List[Dict[str, Any]] = []


def _itc_detect(
    model_label: str, round_idx: int,
    findings_count: int, response_text: str,
    prior_finding_ids: Set[str], current_finding_ids: Set[str],
    dispatch_error: Optional[str] = None,
) -> Optional[str]:
    if dispatch_error and ("context length" in dispatch_error.lower()
                           or "token" in dispatch_error.lower()):
        return ITC_CAPABILITY_MISMATCH
    if not response_text or len(response_text.strip()) < 50:
        return ITC_TRANSIENT_FAILURE
    if findings_count == 0 and len(response_text) > 200:
        history = _itc_model_state.get(model_label, {}).get("history", [])
        recent_empty = sum(1 for h in history[-2:] if h.get("findings") == 0)
        if recent_empty >= 1:
            return ITC_CAPABILITY_MISMATCH
        return ITC_TRANSIENT_FAILURE
    if prior_finding_ids and current_finding_ids:
        overlap = len(current_finding_ids & prior_finding_ids)
        if len(current_finding_ids) > 0:
            overlap_rate = overlap / len(current_finding_ids)
            if overlap_rate > 0.4:
                return ITC_DEGRADATION
    return None


def _itc_consecutive_failures(model_label: str) -> int:
    history = _itc_model_state.get(model_label, {}).get("history", [])
    count = 0
    for entry in reversed(history):
        if entry.get("classification"):
            count += 1
        else:
            break
    return count


def _itc_adapt(
    model_label: str, classification: str, round_idx: int,
    rho_rolling_avg: float = 1.0,
    rho_threshold: float = 0.25,
):
    """A4 fix: suppress DEGRADATION restart when rho is healthy."""
    state = _itc_model_state.setdefault(model_label, {
        "history": [], "adaptation": None, "retry_count": 0,
        "escalation_level": 0,
    })
    state["history"].append({
        "round": round_idx, "classification": classification, "findings": 0,
    })
    consecutive = _itc_consecutive_failures(model_label)
    if classification == ITC_TRANSIENT_FAILURE:
        if state["retry_count"] < 1:
            state["adaptation"] = "retry"
            state["retry_count"] += 1
        elif consecutive < 3:
            state["adaptation"] = "strip_context"
            state["retry_count"] = 0
        else:
            state["adaptation"] = "restart_fresh"
            state["retry_count"] = 0
    elif classification == ITC_CAPABILITY_MISMATCH:
        current = state.get("adaptation")
        if current != "strip_context" and current != "section_assign":
            state["adaptation"] = "strip_context"
        elif current == "strip_context":
            state["adaptation"] = "section_assign"
        else:
            state["adaptation"] = "restart_fresh"
    elif classification == ITC_DEGRADATION:
        if rho_rolling_avg >= rho_threshold:
            _log(f"  ITC [{model_label}]: {classification} suppressed — "
                 f"rho_avg={rho_rolling_avg:.3f} >= {rho_threshold} (normal depletion)")
            state["adaptation"] = None
        elif consecutive < 2:
            state["adaptation"] = "change_focus"
        else:
            state["adaptation"] = "restart_fresh"
    if consecutive >= 3:
        _itc_flag_underperformer(model_label, round_idx, classification, consecutive)


def _itc_flag_underperformer(
    model_label: str, round_idx: int, classification: str, consecutive: int,
):
    flag = {
        "model": model_label, "round": round_idx,
        "classification": classification, "consecutive_failures": consecutive,
        "message": (
            f"{model_label} has {consecutive} consecutive ITC interventions "
            f"(latest: {classification}). Flagged for HIL review."
        ),
    }
    _itc_hil_flags.append(flag)
    _log(f"  *** HIL FLAG: {flag['message']} ***")


def _itc_get_adaptation(model_label: str) -> Optional[str]:
    return _itc_model_state.get(model_label, {}).get("adaptation")


def _itc_clear_adaptation(model_label: str):
    state = _itc_model_state.get(model_label)
    if state:
        state["adaptation"] = None
        state["retry_count"] = 0


def _build_change_focus_instruction(registry: FindingRegistry, round_idx: int) -> str:
    status_counts: Dict[str, int] = {}
    for entry in registry.entries.values():
        s = entry["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    open_count = status_counts.get("OPEN", 0) + status_counts.get("CONTESTED", 0)
    confirmed = status_counts.get("CONFIRMED", 0)
    total = len(registry.entries)
    needs_verdict = []
    for cid, entry in registry.entries.items():
        if entry["status"] == "OPEN":
            confirm_count = sum(
                1 for v in entry.get("verdicts", []) if v.get("verdict") == "CONFIRM"
            )
            if confirm_count == 0:
                needs_verdict.append(f"{cid} ({entry['description'][:60]})")
    parts = [
        "=== FOCUS REDIRECT (you are repeating yourself) ===\n",
        f"The registry has {total} canonical findings: {confirmed} CONFIRMED, "
        f"{open_count} OPEN/CONTESTED.\n\nSTOP describing known bugs. Instead:\n",
    ]
    if needs_verdict:
        verdict_list = "\n".join(f"  - {nv}" for nv in needs_verdict[:8])
        parts.append(
            f"1. These {len(needs_verdict)} OPEN findings need verdicts:\n"
            f"{verdict_list}\n\n"
        )
    parts.append(
        "2. Issue MERGE <ID> <- <ID> for same-root-cause findings.\n\n"
        "3. File genuinely new findings only if not already in the registry.\n\n"
        "=== END FOCUS REDIRECT ===\n"
    )
    return "".join(parts)


def _itc_build_recovery_prompt(
    model_label: str, base_prompt: str,
    observed_fingerprints: Dict[str, Dict[str, Any]], round_idx: int,
) -> str:
    fp = observed_fingerprints.get(model_label, {})
    max_ok_chars = fp.get("max_successful_context_chars", 0)
    if max_ok_chars > 0 and len(base_prompt) > max_ok_chars:
        artifact_start = base_prompt.find("=== ARTIFACT:")
        if artifact_start > 0:
            preamble = base_prompt[:min(2000, artifact_start)]
            artifact = base_prompt[artifact_start:]
            return (
                f"{preamble}\n\n"
                f"(Recovery dispatch — context reduced to ~{max_ok_chars:,} chars.)\n\n"
                f"Focus on the most impactful findings. Quality over quantity.\n\n"
                f"{artifact}"
            )
    return f"{base_prompt}\n\n(Fresh instance — focus on your strongest area.)\n"


# ─────────────────────────────────────────────────────────────────────────────
# Fingerprints
# ─────────────────────────────────────────────────────────────────────────────

def _load_fingerprints() -> Dict[str, Dict[str, Any]]:
    fingerprints: Dict[str, Dict[str, Any]] = {}
    FINGERPRINT_DIR.mkdir(parents=True, exist_ok=True)
    for fp_file in FINGERPRINT_DIR.glob("*.json"):
        try:
            data = json.loads(fp_file.read_text(encoding="utf-8"))
            model_id = data.get("model_id", fp_file.stem)
            fingerprints[model_id] = data.get("observed", {})
        except (json.JSONDecodeError, OSError):
            pass
    return fingerprints


def _save_fingerprints(observed: Dict[str, Dict[str, Any]], experiment_name: str):
    FINGERPRINT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    for model_id, obs in observed.items():
        fp_data = {
            "model_id": model_id, "experiment": experiment_name,
            "timestamp": ts, "observed": obs,
        }
        fp_path = FINGERPRINT_DIR / f"{model_id}.json"
        fp_path.write_text(json.dumps(fp_data, indent=2), encoding="utf-8")
    _log(f"  Fingerprints saved: {len(observed)} models -> {FINGERPRINT_DIR}")


def _update_observed_fingerprint(
    observed: Dict[str, Dict[str, Any]], model_label: str, round_idx: int,
    findings_count: int, response_chars: int,
    dispatch_error: Optional[str] = None,
):
    fp = observed.setdefault(model_label, {
        "max_successful_context_chars": 0, "max_failed_context_chars": 0,
        "failure_modes": [], "total_findings": 0,
        "rounds_participated": 0, "avg_findings_per_round": 0.0,
    })
    fp["rounds_participated"] = fp.get("rounds_participated", 0) + 1
    fp["total_findings"] = fp.get("total_findings", 0) + findings_count
    fp["avg_findings_per_round"] = (
        fp["total_findings"] / fp["rounds_participated"]
        if fp["rounds_participated"] > 0 else 0.0
    )
    if dispatch_error:
        if "context length" in str(dispatch_error).lower():
            fp["max_failed_context_chars"] = max(
                fp.get("max_failed_context_chars", 0), response_chars)
            if "context_overflow" not in fp.get("failure_modes", []):
                fp.setdefault("failure_modes", []).append("context_overflow")
    elif response_chars > 0:
        fp["max_successful_context_chars"] = max(
            fp.get("max_successful_context_chars", 0), response_chars)


# ─────────────────────────────────────────────────────────────────────────────
# Topology instruction templates
# ─────────────────────────────────────────────────────────────────────────────

_POC_CONTEXT_INSTRUCTION = (
    "SYSTEM CONTEXT — PROOF OF CONCEPT (MANDATORY):\n"
    "This codebase is a proof-of-concept, not production software. Focus on "
    "CRITICAL (blocks operation) and HIGH (silently wrong results). File MEDIUM "
    "only if quick to fix. Ignore LOW entirely.\n\n"
)

_MACHINE_COMMS_INSTRUCTION = (
    "INTER-MODEL COMMUNICATION PROTOCOL (MANDATORY):\n"
    "No social pleasantries. For cross-model references, use structured verdicts:\n"
    "  CONFIRM C0001 — you agree the finding and fix are correct\n"
    "  CHALLENGE C0001 | [evidence] — the finding or fix is wrong\n"
    "  EXTEND C0001 | [new consequence or edge case]\n"
    "  MERGE C0001 <- [your_finding_id] — same root cause, combining\n"
    "Reference findings by CANONICAL ID (C0001, C0002, ...) from the registry.\n\n"
)

_GOOD_ENOUGH_INSTRUCTION = (
    "GOOD ENOUGH PRINCIPLE (MANDATORY):\n"
    "Converge on the simplest sufficient fix. Do NOT propose multiple alternatives. "
    "If another model has a correct fix, CONFIRM it. Before filing new findings, "
    "check the registry — CONFIRM or EXTEND instead of duplicating.\n\n"
)

_STAR_TOPOLOGY_INSTRUCTION = (
    "COMMUNICATION TOPOLOGY — STAR/BLACKBOARD (MANDATORY):\n"
    "You see a FINDING REGISTRY maintained by the runner, not other models' prose. "
    "File DISCOVERY findings for new bugs. Issue VERDICT payloads on existing entries. "
    "Do NOT address other models directly.\n\n"
)

_RELAY_TOPOLOGY_INSTRUCTION = (
    "COMMUNICATION TOPOLOGY — RELAY/DIRECT CONVERSATION:\n"
    "You see the FULL analysis from other models. CHALLENGE weak claims, CONFIRM "
    "strong findings, EXTEND insights, file new DISCOVERY findings for bugs nobody "
    "found. Use @ModelName for direct address. Also issue structured VERDICT "
    "payloads for registry tracking.\n\n"
)


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch helpers
# ─────────────────────────────────────────────────────────────────────────────

def _compose_for_model(
    model_label: str, pattern_name: str, domain: str,
) -> ComposedDirectiveSet:
    composer_model = COMPOSER_MODEL_MAP.get(model_label, model_label)
    situation = build_interaction_pattern(pattern_name)
    return compose(task_domain=domain, model=composer_model, situation=situation)


def _multiturn_fallback(
    mc: ModelConfig, prompt: str, cdsfl_text: str,
    full_code: str, round_idx: int, pattern_text: str,
    logs_dir: Path,
) -> Optional[Tuple[str, float]]:
    try:
        chunks = [
            DecomposedChunk(content=part, label=f"target_{i}")
            for i, part in enumerate(
                re.split(r'\n\n===\s+(?:TARGET|CONTEXT)\s+', full_code)
            )
            if part.strip()
        ]
        if not chunks:
            return None
        result = decomposed_dispatch(
            api=mc.api, model_id=mc.model_id, system_prompt=cdsfl_text,
            chunks=chunks, final_instruction=f"{pattern_text}\n\n{prompt}",
            max_tokens=mc.max_tokens, timeout=mc.timeout * 2,
            cdsfl_directives=cdsfl_text,
        )
        save_decomposed_result(result, logs_dir, mc.label, round_idx)
        return result.text, result.elapsed_s
    except Exception as e:
        _log(f"  {mc.label}: multi-turn FAILED — {type(e).__name__}: {e}")
        return None


def _dispatch_single_model(
    mc: ModelConfig, mgr: DynamicManager, prompt: str,
    cdsfl_text: str, full_code: str, round_idx: int,
    pattern_name: str, domain: str, logs_dir: Path,
) -> Tuple[List[Finding], Optional[str]]:
    try:
        composed = _compose_for_model(mc.label, pattern_name, domain)
        model_cdsfl = composed.rendered_text
    except Exception:
        model_cdsfl = cdsfl_text

    pattern_text = INTERACTION_PATTERN_PRESETS[pattern_name][0]

    if _should_decompose(mc.label, mgr):
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text, logs_dir)
        if fallback is not None:
            text, elapsed = fallback
            _record_throughput(mc.label, len(prompt), elapsed)
            model_findings = parse_findings(mc.label, round_idx, text)
            logs_dir.mkdir(parents=True, exist_ok=True)
            save_output(
                logs_dir, f"r{round_idx}", mc.label, prompt[:200] + "...", text,
                metadata={"round": round_idx, "elapsed": round(elapsed, 1),
                          "chars": len(text), "findings_count": len(model_findings),
                          "decomposed": True, "multiturn": True})
            return model_findings, text

    wall_limit = mc.timeout * 5 if mc.label == "CC2" else mc.timeout * 3
    try:
        text, elapsed = dispatch_to_model(mc, prompt, model_cdsfl, wall_clock_limit=wall_limit)
        _record_throughput(mc.label, len(prompt), elapsed)
        model_findings = parse_findings(mc.label, round_idx, text)
        logs_dir.mkdir(parents=True, exist_ok=True)
        save_output(
            logs_dir, f"r{round_idx}", mc.label, prompt[:200] + "...", text,
            metadata={"round": round_idx, "elapsed": round(elapsed, 1),
                      "chars": len(text), "findings_count": len(model_findings),
                      "decomposed": False})
        return model_findings, text
    except (CircuitBreakerTripped, TimeoutError, Exception) as e:
        _log(f"  {mc.label}: {type(e).__name__} — {e}")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text, logs_dir)
        if fallback is not None:
            text, elapsed = fallback
            _record_throughput(mc.label, len(prompt), elapsed)
            model_findings = parse_findings(mc.label, round_idx, text)
            logs_dir.mkdir(parents=True, exist_ok=True)
            save_output(
                logs_dir, f"r{round_idx}", mc.label, prompt[:200] + "...", text,
                metadata={"round": round_idx, "elapsed": round(elapsed, 1),
                          "chars": len(text), "findings_count": len(model_findings),
                          "decomposed": True, "multiturn": True})
            return model_findings, text
        return [], f"__DISPATCH_FAILED__:{type(e).__name__}: {e}"


def _dispatch_round_star(
    exp_config: ExperimentConfig, mgr: DynamicManager, brain: InsectBrain,
    base_prompt: str, registry_summary: str, cdsfl_text: str, full_code: str,
    round_idx: int, cfg: RunnerConfig,
    registry: Optional[FindingRegistry] = None,
) -> Tuple[List[Finding], Dict[str, str], Dict[str, float]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    per_model_durations: Dict[str, float] = {}
    baseline = set(cfg.models)
    eligible = [mc for mc in exp_config.models
                if mc.label in baseline and mc.role != "collator"]

    def _make_prompt(mc_label: str) -> str:
        if round_idx == 0:
            return base_prompt
        adaptation = _itc_get_adaptation(mc_label)
        focus_prefix = ""
        if adaptation == "change_focus" and registry is not None:
            focus_prefix = _build_change_focus_instruction(registry, round_idx)
        star_section = (
            f"{registry_summary}\n\n"
            f"This is Round {round_idx}. Review the registry above. "
            f"File new DISCOVERY findings. Issue VERDICT payloads on existing entries.\n"
        )
        combined = f"{focus_prefix}{star_section}"
        if "=== ARTIFACT:" in base_prompt:
            return base_prompt.replace("=== ARTIFACT:", f"{combined}=== ARTIFACT:")
        return f"{base_prompt}\n\n{combined}"

    logs_dir = brain.logs_dir
    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        start_times: Dict[str, float] = {}
        for mc in eligible:
            start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model, mc, mgr, _make_prompt(mc.label),
                cdsfl_text, full_code, round_idx, cfg.pattern, cfg.domain, logs_dir,
            )] = mc.label

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            elapsed = time.monotonic() - start_times[label]
            per_model_durations[label] = elapsed
            try:
                mf, text = future.result()
                findings.extend(mf)
                if text and not text.startswith("__DISPATCH_FAILED__:"):
                    responses[label] = text
            except Exception as e:
                _log(f"  {label}: thread error — {type(e).__name__}: {e}")

    return findings, responses, per_model_durations


def _dispatch_round_relay(
    exp_config: ExperimentConfig, mgr: DynamicManager, brain: InsectBrain,
    base_prompt: str, cdsfl_text: str, full_code: str,
    round_idx: int, cfg: RunnerConfig,
    registry: Optional[FindingRegistry] = None,
) -> Tuple[List[Finding], Dict[str, str], Dict[str, float]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    per_model_durations: Dict[str, float] = {}
    baseline = set(cfg.models)
    eligible = [mc for mc in exp_config.models
                if mc.label in baseline and mc.role != "collator"]

    relay_payloads = {}
    if round_idx > 0:
        if cfg.relay_mode == "directed":
            relay_payloads = brain.relay_directed(round_idx)
        elif cfg.relay_mode == "conversational":
            relay_payloads = brain.relay_conversational(round_idx)
        else:
            relay_payloads = brain.relay(round_idx)

    def _make_prompt(mc_label: str) -> str:
        if round_idx == 0 or mc_label not in relay_payloads:
            return base_prompt
        payload = relay_payloads[mc_label]
        if not payload.findings_text:
            return base_prompt
        adaptation = _itc_get_adaptation(mc_label)
        focus_prefix = ""
        if adaptation == "change_focus" and registry is not None:
            focus_prefix = _build_change_focus_instruction(registry, round_idx)
        if adaptation == "strip_context":
            relay_section = (
                f"=== OTHER MODELS' ANALYSIS (Round {round_idx - 1}) ===\n\n"
                f"(Context stripped. Summary of {payload.finding_count} findings.)\n\n"
                f"{payload.convergence_summary}\n\n"
                f"=== END OTHER MODELS' ANALYSIS ===\n\n"
            )
        else:
            relay_section = (
                f"=== OTHER MODELS' ANALYSIS (Round {round_idx - 1}) ===\n\n"
                f"{payload.findings_text}\n\n"
                f"{payload.convergence_summary}\n\n"
                f"=== END OTHER MODELS' ANALYSIS ===\n\n"
                f"Produce YOUR findings. Challenge weak claims, confirm strong ones.\n\n"
            )
        combined = f"{focus_prefix}{relay_section}"
        if "=== ARTIFACT:" in base_prompt:
            return base_prompt.replace("=== ARTIFACT:", f"{combined}=== ARTIFACT:")
        return f"{combined}{base_prompt}"

    logs_dir = brain.logs_dir
    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        start_times: Dict[str, float] = {}
        for mc in eligible:
            start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model, mc, mgr, _make_prompt(mc.label),
                cdsfl_text, full_code, round_idx, cfg.pattern, cfg.domain, logs_dir,
            )] = mc.label

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            elapsed = time.monotonic() - start_times[label]
            per_model_durations[label] = elapsed
            try:
                mf, text = future.result()
                findings.extend(mf)
                if text and not text.startswith("__DISPATCH_FAILED__:"):
                    responses[label] = text
            except Exception as e:
                _log(f"  {label}: thread error — {type(e).__name__}: {e}")

    return findings, responses, per_model_durations


# ─────────────────────────────────────────────────────────────────────────────
# Safety and telemetry helpers
# ─────────────────────────────────────────────────────────────────────────────

def _safety_check(responses: Dict[str, str]) -> Optional[str]:
    if not responses:
        return "all_models_failed"
    for label, text in list(responses.items()):
        if len(text.strip()) < 50:
            _log(f"  SAFETY: {label} near-empty — queued for ITC recovery")
            responses.pop(label, None)
        elif "[MODEL_REFUSED" in text:
            _log(f"  SAFETY: {label} refused — queued for ITC recovery")
            responses.pop(label, None)
    if not responses:
        return "all_models_failed"
    return None


def _build_round_timings(
    responses: Dict[str, str], per_model_durations: Dict[str, float],
    findings: List[Finding], round_idx: int,
) -> List[RoundTiming]:
    return [
        RoundTiming(
            model_id=label, round_idx=round_idx,
            duration_s=per_model_durations.get(label, 0.0),
            response_chars=len(text),
            finding_count=len([f for f in findings if f.model_id == label]),
        )
        for label, text in responses.items()
    ]


def _summarise_health_scan(scan: HealthScan) -> Dict[str, Any]:
    return {
        "total_diagnostics": scan.total,
        "by_category": dict(scan.counts_by_category),
        "by_severity": dict(scan.counts_by_severity),
        "elapsed_s": round(scan.elapsed_s, 2),
    }


def _summarise_fix_evaluations(evals: List[FixEvaluation]) -> Dict[str, Any]:
    verdict_counts: Dict[str, int] = {}
    for ev in evals:
        verdict_counts[ev.verdict] = verdict_counts.get(ev.verdict, 0) + 1
    return {"total_evaluated": len(evals), "verdicts": verdict_counts}


def _summarise_pacing_signals(signals: List[PacingSignal]) -> List[Dict[str, Any]]:
    return [
        {"type": s.signal_type, "detail": s.detail, "model_id": s.model_id,
         "metric_value": round(s.metric_value, 3),
         "threshold": round(s.threshold, 3),
         "suggested_action": s.suggested_action}
        for s in signals
    ]


# ─────────────────────────────────────────────────────────────────────────────
# CC2v verification (A5: dedup-aware)
# ─────────────────────────────────────────────────────────────────────────────

_VERIFICATION_PROMPT_TEMPLATE = """You are a verification agent (CC2v). FFF each finding and produce a verdict.

For each finding:
  CONFIRM <ID> | <confidence 0.0-1.0> | <one-line evidence>
  REJECT <ID> | <confidence 0.0-1.0> | <one-line counterexample>
  DUPLICATE <ID> OF <canonical_id> | <confidence 0.0-1.0> | <evidence>
  ESCALATE <ID> | <reason>

SOURCE CODE:
{source_code}

FINDINGS TO VERIFY:
{findings_block}

One verdict per line, nothing else.
"""


def _verification_step(
    registry: FindingRegistry, round_idx: int,
    source_code: str, model_configs: List[ModelConfig],
    cfg: RunnerConfig,
) -> Dict[str, Any]:
    """A5: dedup-aware CC2v — skip already-confirmed/escalated findings."""
    if round_idx < cfg.verification_min_round:
        return {"skipped": True, "reason": f"round {round_idx} < {cfg.verification_min_round}"}

    open_findings = []
    for cid, entry in registry.entries.items():
        if entry["status"] not in ("OPEN", "CONTESTED"):
            continue
        if entry.get("cc2v_escalated"):
            continue
        confirm_models = {
            v["model"] for v in entry.get("verdicts", [])
            if v.get("verdict") == "CONFIRM"
        }
        if len(confirm_models) >= 2:
            continue
        cc2v_verdicts = [v for v in entry.get("verdicts", []) if v.get("model") == "CC2v"]
        if cc2v_verdicts:
            continue
        open_findings.append((cid, entry))

    if not open_findings:
        return {"skipped": True, "reason": "no open findings"}

    open_findings.sort(key=lambda x: x[1].get("severity", 0), reverse=True)
    batch = open_findings[:cfg.verification_batch_size]

    findings_block = "\n\n".join(
        f"[{cid}] severity={entry.get('severity', 0):.2f}: {entry.get('description', '')[:500]}"
        for cid, entry in batch
    )
    prompt = _VERIFICATION_PROMPT_TEMPLATE.format(
        source_code=source_code[:80_000], findings_block=findings_block,
    )

    cc2_config = None
    for mc in model_configs:
        if mc.label == "CC2":
            cc2_config = mc
            break
    if cc2_config is None:
        return {"skipped": True, "reason": "CC2 config not found"}

    stats: Dict[str, Any] = {
        "round": round_idx, "batch_size": len(batch),
        "batch_ids": [cid for cid, _ in batch], "verdicts": {},
    }
    try:
        text, elapsed = dispatch_to_model(
            cc2_config, prompt, "", wall_clock_limit=cc2_config.timeout * 3)
        stats["elapsed_s"] = round(elapsed, 1)
    except Exception as e:
        _log(f"  CC2v: dispatch failed — {type(e).__name__}: {e}")
        stats["error"] = str(e)
        return stats

    verdict_re = re.compile(
        r"(CONFIRM|REJECT|DUPLICATE|ESCALATE)\s+(C\d+)"
        r"(?:\s+OF\s+(C\d+))?"
        r"(?:\s*\|\s*([\d.]+))?"
        r"(?:\s*\|\s*(.+))?",
        re.IGNORECASE,
    )
    confirmed = rejected = duplicates = escalated = 0
    batch_ids = {cid for cid, _ in batch}

    for line in text.split("\n"):
        m = verdict_re.search(line)
        if not m:
            continue
        action = m.group(1).upper()
        finding_id = m.group(2).upper()
        merge_target = m.group(3)
        confidence = float(m.group(4)) if m.group(4) else 0.5
        evidence = m.group(5) or ""

        if finding_id not in batch_ids:
            continue
        stats["verdicts"][finding_id] = {
            "action": action, "confidence": confidence, "evidence": evidence[:200],
        }
        if action == "ESCALATE":
            entry = registry.entries.get(finding_id)
            if entry:
                entry["cc2v_escalated"] = True
            escalated += 1
            continue
        if confidence < cfg.verification_confidence_threshold:
            continue
        if action == "CONFIRM":
            entry = registry.entries.get(finding_id)
            if entry and entry["status"] in ("OPEN", "CONTESTED"):
                registry.resolve(finding_id, "CONFIRMED", round_idx)
                confirmed += 1
        elif action == "REJECT":
            entry = registry.entries.get(finding_id)
            if entry and entry["status"] in ("OPEN", "CONTESTED"):
                registry.resolve(finding_id, "UNCONFIRMED", round_idx)
                rejected += 1
        elif action == "DUPLICATE" and merge_target:
            merge_target = merge_target.upper()
            if merge_target in registry.entries:
                entry = registry.entries.get(finding_id)
                if entry and entry["status"] in ("OPEN", "CONTESTED"):
                    registry.resolve(finding_id, "MERGED", round_idx)
                    entry["merged_into"] = merge_target
                    duplicates += 1

    stats.update(confirmed=confirmed, rejected=rejected,
                 duplicates=duplicates, escalated=escalated,
                 total_resolved=confirmed + rejected + duplicates)
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Preflight
# ─────────────────────────────────────────────────────────────────────────────

def run_preflight(
    exp_config: ExperimentConfig, cdsfl_text: str, cfg: RunnerConfig,
) -> bool:
    _log("=" * 60)
    _log("PREFLIGHT: Testing model connectivity")
    _log("=" * 60)
    test_prompt = (
        "This is a connectivity test. Respond with exactly:\n"
        "STATUS: OK\nMODEL: [your model name]\nNothing else."
    )
    baseline = set(cfg.models)
    all_ok = True
    for mc in exp_config.models:
        if mc.label not in baseline:
            continue
        _log(f"  Testing {mc.label}...")
        try:
            text, elapsed = dispatch_to_model(mc, test_prompt, cdsfl_text)
            ok = len(text.strip()) > 5
            _log(f"  {mc.label}: {'OK' if ok else 'FAILED'} ({elapsed:.1f}s)")
            if not ok:
                all_ok = False
        except Exception as e:
            _log(f"  {mc.label}: FAILED — {e}")
            all_ok = False
    return all_ok


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment loop
# ─────────────────────────────────────────────────────────────────────────────

def _find_or_create_logs_dir(cfg: RunnerConfig) -> Path:
    if cfg.resume:
        logs_root = REPO_ROOT / "bench" / "logs"
        candidates = sorted(
            logs_root.glob(f"{cfg.experiment_name}_*"),
            key=lambda p: p.name, reverse=True,
        )
        for c in candidates:
            if (c / "checkpoint.json").exists():
                return c
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "bench" / "logs" / f"{cfg.experiment_name}_{ts}"


def run_experiment(
    exp_config: ExperimentConfig,
    cdsfl_text: str,
    cfg: RunnerConfig,
) -> Dict[str, Any]:
    """Run a parameterised CDSFL experiment.

    This is the generic entry point for Exp 37+ and Bench Run 2.
    All experiment-specific parameters come from cfg (RunnerConfig).
    """
    logs_dir = _find_or_create_logs_dir(cfg)
    logs_dir.mkdir(parents=True, exist_ok=True)

    baseline = set(cfg.models)

    topo_desc = (
        f"relay/{cfg.relay_mode}" if cfg.topology == "relay"
        else "star/blackboard"
    )
    _log("=" * 60)
    _log(f"EXPERIMENT: {cfg.experiment_name}")
    _log(f"  Topology: {topo_desc}")
    _log(f"  Pattern: {cfg.pattern}")
    _log(f"  Max rounds: {cfg.max_rounds} (extension to {cfg.extension_cap})")
    _log(f"  Convergence: state-based, earliest R{cfg.earliest_stop_round}")
    _log(f"  Target: {cfg.test_article}")
    _log(f"  Context: {cfg.context_files}")
    _log(f"  Models: {sorted(baseline)}")
    _log(f"  Domain: {cfg.domain}")
    _log(f"  Logs: {logs_dir}")
    _log("=" * 60)

    # Load source files
    target_path = Path(cfg.test_article)
    if not target_path.is_absolute():
        target_path = REPO_ROOT / target_path
    target_text = target_path.read_text(encoding="utf-8")
    try:
        target_rel = target_path.relative_to(REPO_ROOT)
    except ValueError:
        target_rel = target_path

    context_parts = []
    context_paths = []
    for ctx in cfg.context_files:
        ctx_path = Path(ctx)
        if not ctx_path.is_absolute():
            ctx_path = REPO_ROOT / ctx_path
        context_paths.append(ctx_path)
        ctx_text = ctx_path.read_text(encoding="utf-8")
        try:
            ctx_rel = ctx_path.relative_to(REPO_ROOT)
        except ValueError:
            ctx_rel = ctx_path
        context_parts.append(
            f"=== CONTEXT FILE: {ctx_rel} ({len(ctx_text):,} chars) ===\n"
            f"(Read-only context — do NOT review this file)\n{ctx_text}"
        )

    full_code = (
        f"=== TARGET FILE (REVIEW THIS): {target_rel} "
        f"({len(target_text):,} chars) ===\n{target_text}\n\n"
        + "\n\n".join(context_parts)
    )
    source_paths_str = [str(target_path)] + [str(p) for p in context_paths]

    _log(f"  Target: {len(target_text):,} chars")
    _log(f"  Context: {len(context_parts)} files")
    _log(f"  Total: {len(full_code):,} chars with headers")

    # Build DynamicManager
    dm_config = DynamicManagementConfig(
        pre_decompose_models={"Codex", "DeepSeek"},
        no_exclusion_mode=True,
    )
    dm_config.max_rounds = cfg.max_rounds
    model_specs = build_model_specs(exp_config)
    mgr = DynamicManager(model_specs, dm_config)

    # Insect Brain
    brain = InsectBrain(config=dm_config, logs_dir=logs_dir, source_paths=source_paths_str)
    brain.initialise(model_labels=sorted(baseline))

    # Endocrine Layer
    endo = EndocrineLayer(source_paths=source_paths_str, test_cmd=None, max_fix_evals=20)

    # Finding registry
    registry = FindingRegistry()

    # Fingerprints
    observed_fingerprints = _load_fingerprints()

    # Resume
    start_round = 0
    novelty_counts: List[int] = []
    raw_counts: List[int] = []
    rho_history: List[float] = []
    cumulative_context_chars = 0
    per_model_context: Dict[str, int] = {}
    gamma_history: List[float] = []
    gate_history: List[bool] = []
    open_ch_history: List[int] = []
    stall_history: List[Dict[str, int]] = []

    if cfg.resume and brain.load_checkpoint():
        start_round = brain.state.current_round + 1
        _log(f"  RESUMED from round {start_round}")
        runner_ckpt = brain.logs_dir / "runner_state.json"
        if runner_ckpt.exists():
            ckpt_data = json.loads(runner_ckpt.read_text(encoding="utf-8"))
            registry = FindingRegistry.from_dict(ckpt_data.get("registry", {}))
            novelty_counts = ckpt_data.get("novelty_counts", [])
            raw_counts = ckpt_data.get("raw_counts", [])
            rho_history = ckpt_data.get("rho_history", [])
            gamma_history = ckpt_data.get("gamma_history", [])
            gate_history = ckpt_data.get("gate_history", [])
            open_ch_history = ckpt_data.get("open_ch_history", [])
            stall_history = ckpt_data.get("stall_history", [])
            cumulative_context_chars = ckpt_data.get("cumulative_context_chars", 0)
            _log(f"  Registry restored: {len(registry.entries)} entries")

    experiment_start = time.monotonic()
    effective_max = cfg.max_rounds
    loop_cap = cfg.extension_cap
    extended = False
    rho_avg = 1.0
    rho_churn = False

    # Build awareness preamble
    roster_lines = "\n".join(
        f"  - {label}: {MODEL_ROSTER.get(label, label)}"
        for label in sorted(baseline)
    )
    topo_instruction = (
        _RELAY_TOPOLOGY_INSTRUCTION if cfg.topology == "relay"
        else _STAR_TOPOLOGY_INSTRUCTION
    )
    awareness_preamble = (
        f"You are one of {len(baseline)} AI models in a distributed code review "
        f"under CDSFL constraints with FFF methodology. The models are:\n"
        f"{roster_lines}\n\n"
        f"{topo_instruction}"
        f"{_POC_CONTEXT_INSTRUCTION}"
        f"{_MACHINE_COMMS_INSTRUCTION}"
        f"{_GOOD_ENOUGH_INSTRUCTION}"
    )

    base_prompt = (
        f"{awareness_preamble}"
        f"YOUR TASK:\n"
        f"Review {target_rel} under full CDSFL + FFF constraints.\n\n"
        f"For each finding, provide (keys in this exact order):\n"
        f"  FINDING_ID: unique identifier (e.g., F001). STABLE across rounds.\n"
        f"  SEVERITY: 0.0 to 1.0\n"
        f"  FLAW_CLASS: integer (1=logic, 2=interface, 3=notation, "
        f"4=completeness, 5=correctness, 6=edge-case, 7=performance, 8=documentation)\n"
        f"  ABSTRACTION_INDEX: 0.0 to 1.0\n"
        f"  DESCRIPTION: FIND — what is wrong, where, evidence\n"
        f"  FOLLOW: trace downstream consequences before proposing a fix\n"
        f"  PROPOSED_FIX: FIX — the simplest sufficient correction\n"
        f"  VERIFIED: TRUE if proven, FALSE if assertion\n\n"
        f"Produce ALL findings. Do not hold back.\n\n"
        f"=== ARTIFACT: {target_rel} + Context ({len(full_code):,} chars) ===\n\n"
        f"{full_code}\n\n"
        f"=== END ARTIFACT ===\n\n"
        f"Produce your findings now."
    )

    result: Dict[str, Any] = {
        "experiment": cfg.experiment_name,
        "topology": cfg.topology,
        "relay_mode": cfg.relay_mode if cfg.topology == "relay" else None,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "pattern": cfg.pattern,
        "models": sorted(baseline),
        "target_file": str(target_rel),
        "context_files": [str(p) for p in cfg.context_files],
        "max_rounds": cfg.max_rounds,
        "extension_cap": cfg.extension_cap,
        "domain": cfg.domain,
        "convergence_config": {
            "earliest_stop": cfg.earliest_stop_round,
            "consecutive_required": cfg.consecutive_rounds_required,
            "rho_threshold": cfg.rho_threshold,
            "rho_rolling_window": cfg.rho_rolling_window,
        },
        "rounds": [],
    }

    # ── Main loop ──
    for round_idx in range(start_round, loop_cap):
        if round_idx >= effective_max:
            break

        round_start = time.monotonic()
        wall_elapsed = round_start - experiment_start
        if wall_elapsed > cfg.wall_clock_cap_s:
            _log(f"\nWALL CLOCK CAP reached ({wall_elapsed:.0f}s). Stopping.")
            break

        _log(f"\n{'---' * 20}")
        round_type = "blind" if round_idx == 0 else "adaptive"
        _log(f"Round {round_idx}/{effective_max - 1} ({round_type})")
        _log(f"{'---' * 20}")

        # Dispatch — topology-dependent
        if cfg.topology == "relay":
            findings, responses, per_model_durations = _dispatch_round_relay(
                exp_config, mgr, brain, base_prompt, cdsfl_text, full_code,
                round_idx, cfg, registry=registry,
            )
        else:
            registry_summary = registry.build_summary(round_idx) if round_idx > 0 else ""
            findings, responses, per_model_durations = _dispatch_round_star(
                exp_config, mgr, brain, base_prompt, registry_summary,
                cdsfl_text, full_code, round_idx, cfg, registry=registry,
            )

        # Safety check
        problem = _safety_check(responses)
        if problem:
            _log(f"\n*** ALL MODELS FAILED: {problem} ***")
            result["terminated"] = problem
            break

        # Register findings
        novel_this_round = 0
        for f in findings:
            existing = registry.lookup_alias(f.model_id, f.finding_id)
            if existing is None:
                registry.register(f, f.model_id)
                novel_this_round += 1
            else:
                registry.add_verdict(existing, f.model_id, "CONFIRM", round_idx)

        novelty_counts.append(novel_this_round)
        raw_counts.append(len(findings))

        # A2: Rho
        rho_current, rho_avg, rho_churn = _compute_rho(novelty_counts, raw_counts, cfg)
        rho_history.append(rho_current)
        _log(f"  Registry: {novel_this_round} novel / {len(findings)} raw, "
             f"{len(registry.entries)} total, "
             f"rho={rho_current:.3f}, rho_avg={rho_avg:.3f}"
             f"{' [CHURN]' if rho_churn else ''}")

        # Parse verdicts
        for model_id, raw_text in responses.items():
            for verdict_type, canonical_id, evidence in _parse_verdicts(raw_text, model_id, round_idx):
                if verdict_type == "MERGE":
                    source = _resolve_merge_source(evidence, model_id, registry)
                    if source and source != canonical_id:
                        registry.add_verdict(source, model_id, "MERGE", round_idx,
                                             f"merged_into={canonical_id}")
                    else:
                        registry.add_verdict(canonical_id, model_id, "CONFIRM", round_idx, evidence)
                else:
                    registry.add_verdict(canonical_id, model_id, verdict_type, round_idx, evidence)

        # Status transitions
        _update_finding_statuses(registry, round_idx)
        registry.auto_resolve_contested(round_idx)

        # A3: HIL escalation
        registry.escalate_stale_contested(round_idx, max_contested_rounds=cfg.max_contested_rounds)

        # Persist round
        round_elapsed = time.monotonic() - round_start
        brain.persist(round_idx, responses, findings, duration_s=round_elapsed)

        # Endocrine
        round_timings = _build_round_timings(responses, per_model_durations, findings, round_idx)
        for label, text in responses.items():
            per_model_context[label] = per_model_context.get(label, 0) + len(text)
            cumulative_context_chars += len(text)

        endo_report = endo.run(
            round_idx=round_idx, findings=findings,
            round_timings=round_timings,
            cumulative_context_chars=cumulative_context_chars,
            context_budget=max(CONTEXT_CHAR_BUDGET.values()),
            novelty_counts=novelty_counts,
        )

        # Immune pipeline
        immune_result = brain.run_immune_pipeline(findings)
        for f in findings:
            if f.verified:
                canonical = registry.lookup_alias(f.model_id, f.finding_id)
                if canonical:
                    registry.mark_verified(canonical)

        # CC2v verification (A5)
        verification_stats = _verification_step(
            registry, round_idx, full_code, exp_config.models, cfg)

        # ITC per-model
        for model_label in list(baseline):
            model_findings = [f for f in findings if f.model_id == model_label]
            model_text = responses.get(model_label, "")
            prior_ids: Set[str] = set()
            current_ids = {f.finding_id for f in model_findings}
            if brain.state.all_findings and len(brain.state.all_findings) >= 2:
                prior_ids = {
                    f.finding_id for f in brain.state.all_findings[-2]
                    if f.model_id == model_label
                }
            dispatch_err = "no_response" if model_label not in responses else None
            classification = _itc_detect(
                model_label, round_idx, len(model_findings), model_text,
                prior_ids, current_ids, dispatch_error=dispatch_err,
            )
            if classification:
                _itc_adapt(model_label, classification, round_idx,
                           rho_rolling_avg=rho_avg, rho_threshold=cfg.rho_threshold)
            elif model_label in _itc_model_state:
                _itc_clear_adaptation(model_label)
            _update_observed_fingerprint(
                observed_fingerprints, model_label, round_idx,
                len(model_findings), len(model_text), dispatch_error=dispatch_err,
            )

        # Directed messages (relay only)
        if cfg.topology == "relay" and cfg.relay_mode == "directed":
            for label, text in responses.items():
                if text:
                    brain.extract_directed_messages(label, text, round_idx)

        # Gamma
        gamma = _estimate_gamma(novelty_counts, cfg.min_rounds_for_gamma)
        gamma_history.append(gamma)
        gate_level, gamma_passed = _check_gamma_gate(gamma, round_idx, cfg)

        _log(f"  gamma: {gamma:.3f} ({gate_level}, "
             f"{'passed' if gamma_passed else 'BLOCKED'}) — {_interpret_gamma(gamma)}")
        _log(f"  Round {round_idx}: {len(findings)} findings, {round_elapsed:.1f}s")

        # Convergence gate
        converged, conv_reason = _check_state_convergence(
            round_idx, registry, novel_this_round, gamma, gate_history, cfg,
            open_ch_history=open_ch_history,
            rho_rolling_avg=rho_avg, rho_churn=rho_churn,
        )
        _log(f"  Convergence: {conv_reason}")

        # Stall detector
        stall_result = _check_stall_convergence(
            round_idx, registry, gamma, stall_history, cfg)

        # Checkpoint
        ckpt_path = brain.logs_dir / "runner_state.json"
        ckpt_path.write_text(json.dumps({
            "registry": registry.to_dict(),
            "novelty_counts": novelty_counts,
            "raw_counts": raw_counts,
            "rho_history": [round(r, 6) for r in rho_history],
            "gamma_history": [round(g, 6) for g in gamma_history],
            "gate_history": gate_history,
            "open_ch_history": open_ch_history,
            "stall_history": stall_history,
            "cumulative_context_chars": cumulative_context_chars,
        }, indent=2, default=str), encoding="utf-8")

        # Round data for report
        round_data: Dict[str, Any] = {
            "round": round_idx, "type": round_type,
            "findings_count": len(findings),
            "novel_this_round": novel_this_round,
            "registry_total": len(registry.entries),
            "models_responded": list(responses.keys()),
            "elapsed_s": round(round_elapsed, 1),
            "gamma": round(gamma, 4),
            "rho": round(rho_current, 4),
            "rho_avg": round(rho_avg, 4),
            "verification": verification_stats,
            "stall_detector": stall_result,
        }
        result["rounds"].append(round_data)

        if converged:
            _log(f"\n  CONVERGED at round {round_idx}: {conv_reason}")
            result["converged_at"] = round_idx
            result["convergence_reason"] = conv_reason
            break

        if stall_result.get("terminate"):
            _log(f"\n  STALL_CONVERGED at round {round_idx}: {stall_result['reason']}")
            result["converged_at"] = round_idx
            result["convergence_reason"] = "STALL_CONVERGED"
            break

        # Budget extension
        if round_idx == cfg.max_rounds - 1 and not extended:
            gamma_prev = gamma_history[-2] if len(gamma_history) >= 2 else 0.0
            should_extend, ext_reason = _check_budget_extension(
                round_idx, registry, gamma, gamma_prev)
            if should_extend:
                effective_max = cfg.extension_cap
                extended = True
                _log(f"\n  BUDGET EXTENDED to {cfg.extension_cap}: {ext_reason}")
                result["budget_extended"] = True

        # Extension stall
        if extended and round_idx > cfg.max_rounds and len(result["rounds"]) >= 2:
            prev = result["rounds"][-2]
            if (round_data.get("rho_avg", 1) <= prev.get("rho_avg", 0) and
                    registry.open_crit_high_count() >= prev.get("findings_count", 0)):
                _log("  Extension not improving. Terminating.")
                result["converged_at"] = round_idx
                result["convergence_reason"] = "EXTENSION_STALLED"
                break

    # Finalise
    final_round = len(brain.state.all_findings) - 1
    for canonical_id, entry in list(registry.entries.items()):
        if entry["status"] in ("OPEN", "CONTESTED"):
            registry.resolve(canonical_id, "UNCONFIRMED", final_round)

    _save_fingerprints(observed_fingerprints, cfg.experiment_name)
    signal = brain.signal_complete()

    total_elapsed = time.monotonic() - experiment_start
    total_findings = sum(len(rnd) for rnd in brain.state.all_findings)

    result["total_findings"] = total_findings
    result["total_rounds"] = len(brain.state.all_findings)
    result["total_elapsed_s"] = round(total_elapsed, 1)
    result["end_time"] = datetime.now(timezone.utc).isoformat()
    result["gamma_history"] = [round(g, 4) for g in gamma_history]
    result["registry"] = registry.to_dict()
    result["hil_flags"] = _itc_hil_flags[:]

    # Save report
    report_path = logs_dir / f"{cfg.experiment_name}_report.json"
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    _log(f"\n{'=' * 60}")
    _log(f"EXPERIMENT {cfg.experiment_name} — {len(brain.state.all_findings)} ROUNDS COMPLETE")
    _log(f"  Total findings: {total_findings}")
    _log(f"  Registry: {len(registry.entries)} canonical entries")
    _log(f"  gamma final: {gamma_history[-1]:.3f}" if gamma_history else "  gamma: N/A")
    _log(f"  Elapsed: {total_elapsed:.0f}s")
    _log(f"  Report: {report_path}")
    _log(f"{'=' * 60}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="CDSFL parameterised reference runner (Exp 37+, Bench Run 2)",
    )
    sub = p.add_subparsers(dest="command")

    # preflight
    sub.add_parser("preflight", help="Test model connectivity")

    # run
    run_p = sub.add_parser("run", help="Run an experiment")
    run_p.add_argument("--test-article", required=True,
                       help="Path to the file under review")
    run_p.add_argument("--context", nargs="*", default=[],
                       help="Paths to read-only context files")
    run_p.add_argument("--topology", default="star", choices=["star", "relay"])
    run_p.add_argument("--relay-mode", default="directed",
                       choices=["directed", "conversational", "findings"])
    run_p.add_argument("--pattern", default="fff")
    run_p.add_argument("--max-rounds", type=int, default=21)
    run_p.add_argument("--extension-cap", type=int, default=24)
    run_p.add_argument("--wall-clock-cap", type=int, default=28800,
                       help="Wall clock limit in seconds")
    run_p.add_argument("--earliest-stop", type=int, default=12)
    run_p.add_argument("--models", nargs="+",
                       default=["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"])
    run_p.add_argument("--experiment-name", default="")
    run_p.add_argument("--domain", default="software")
    run_p.add_argument("--resume", action="store_true")
    run_p.add_argument("--rho-threshold", type=float, default=0.25)
    run_p.add_argument("--rho-rolling-window", type=int, default=3)
    run_p.add_argument("--consecutive-rounds", type=int, default=2)
    run_p.add_argument("--config", help="JSON config file (overrides CLI args)")

    return p


def main():
    source_env()
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    exp_config = load_default_config()
    cdsfl_path = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
    cdsfl_text = cdsfl_path.read_text(encoding="utf-8")

    if args.command == "preflight":
        cfg = RunnerConfig(models=["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"])
        ok = run_preflight(exp_config, cdsfl_text, cfg)
        sys.exit(0 if ok else 1)

    # Build config from CLI args or JSON
    if getattr(args, "config", None):
        cfg = RunnerConfig.from_json(args.config)
        # CLI args override JSON for explicitly-provided values
        if args.test_article:
            cfg.test_article = args.test_article
        if args.resume:
            cfg.resume = True
    else:
        cfg = RunnerConfig(
            test_article=args.test_article,
            context_files=args.context or [],
            topology=args.topology,
            relay_mode=args.relay_mode,
            pattern=args.pattern,
            max_rounds=args.max_rounds,
            extension_cap=args.extension_cap,
            wall_clock_cap_s=args.wall_clock_cap,
            earliest_stop_round=args.earliest_stop,
            models=args.models,
            experiment_name=args.experiment_name,
            domain=args.domain,
            resume=args.resume,
            rho_threshold=args.rho_threshold,
            rho_rolling_window=args.rho_rolling_window,
            consecutive_rounds_required=args.consecutive_rounds,
        )

    if args.pattern not in INTERACTION_PATTERN_PRESETS:
        available = ", ".join(sorted(INTERACTION_PATTERN_PRESETS))
        print(f"Unknown pattern: {args.pattern!r}. Available: {available}",
              file=sys.stderr)
        sys.exit(1)

    if not cfg.resume:
        ok = run_preflight(exp_config, cdsfl_text, cfg)
        if not ok:
            _log("\nPREFLIGHT FAILED. Aborting.")
            sys.exit(1)
        _log(f"\nPreflight passed. Starting in 5s...")
        time.sleep(5)
    else:
        _log(f"\nRESUME mode — skipping preflight")

    result = run_experiment(exp_config, cdsfl_text, cfg)

    if result.get("terminated"):
        _log(f"\nExperiment terminated: {result['terminated']}")
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
