#!/usr/bin/env python3
"""Experiment 20: Sequential Confer with Attributed Findings.

Architectural evolution from Experiment 17's parallel broadcast to sequential
confer within each round. Models see attributed prior findings and produce
three types of output per dispatch:
  1. NOVEL findings (new issues not previously raised)
  2. VALIDATION of prior findings (independent confirmation with evidence)
  3. CHALLENGE of prior findings (disagreement with evidence)

Dispatch order within each round is determined by capability fingerprint
per task — strongest model goes first, player_manager (CC2) goes last
to arbitrate.

Test articles: same as Experiment 17 (dynamic_management.py, MATHEMATICAL_APPENDIX.md,
verification_chain.py) with Exp 17 fixes integrated.

Key design decisions (from Whole Body Architecture plan, 2026-03-30):
- Sequential dispatch within rounds (not parallel broadcast)
- Attributed findings: every finding carries source_model explicitly
- Three output types: NOVEL, VALIDATION, CHALLENGE
- Fingerprint-based dispatch ordering per task
- Player_manager arbitrates last
- Dynamic decomposition inherited from Exp 17 (pre_decompose_models)
- Immune layer integration inherited from Exp 17
- Same stop caps: round 10 + wall-clock 4h

Usage:
    python3 bench/run_exp20_confer.py [preflight|canary|run|resume]

    preflight  — verify all models respond + Layer 1 acceptance tests
    canary     — run induced-failure scenarios only
    run        — full experiment
    resume     — resume from cached responses
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

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
    ManagerEvent,
    ManagerEventType,
    FailureType,
    RecoveryAction,
    Role,
    RoundResult,
    DetectorDiagnosis,
)
from run_exp12_live_wire import (
    source_env,
    build_model_specs,
    parse_findings,
    dispatch_to_model,
    INITIAL_FINGERPRINTS,
    MODEL_SPECS,
    CONVERGENCE_EXCLUDED_MODELS,
)
# Inherit decomposition machinery from Exp 17
from run_exp17_immune import (
    TASKS,
    TASK_MARKERS,
    REVIEW_AREAS,
    _extract_code_area,
    _extract_immune_area,
    _extract_task_area,
    _should_decompose,
    _build_decomposed_prompt,
    _find_model_spec,
    _report_dispatch_failure,
    _find_cached,
    run_canary_tests,
    run_layer1_preflight,
)
from run_exp16_plan_review import run_preflight as _run_model_preflight

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

EXPERIMENT = "20"
LOGS_DIR = REPO_ROOT / "bench" / "logs" / f"experiment_{EXPERIMENT}"

# Same stop caps as Exp 17
MAX_ROUNDS = 10
WALL_CLOCK_CAP_S = 4 * 3600  # 4 hours

# Convergent findings from Exp 17 (integrated after Exp 17 completes)
EXP17_FINDINGS_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17"

# Reference documents
INTERFACE_SUMMARY_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_interface_summary.md"
TEST_ARTICLE_PATH = REPO_ROOT / "bench" / "dynamic_management.py"
MATH_APPENDIX_PATH = REPO_ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
VERIFICATION_CHAIN_PATH = REPO_ROOT / "bench" / "verification_chain.py"


# ─────────────────────────────────────────────────────────────────────────────
# Attributed findings format
# ─────────────────────────────────────────────────────────────────────────────

CONFER_FINDING_FORMAT = (
    "## Output Format\n"
    "For each output item, specify its TYPE first:\n\n"
    "### NOVEL findings (issues you found independently):\n"
    "  TYPE: NOVEL\n"
    "  FINDING_ID: {prefix}F001 (etc.)\n"
    "  SEVERITY: 0.0–1.0\n"
    "  FLAW_CLASS: 1=logic, 2=interface, 3=notation, 4=completeness, "
    "5=correctness, 6=edge-case, 7=performance, 8=documentation\n"
    "  ABSTRACTION_INDEX: 0.0–1.0 (0=surface, 1=architectural)\n"
    "  DESCRIPTION: what is wrong and why\n"
    "  PROPOSED_FIX: specific fix\n"
    "  VERIFIED: TRUE/FALSE\n\n"
    "### VALIDATION of a prior finding (you independently confirm it):\n"
    "  TYPE: VALIDATION\n"
    "  VALIDATES: <finding_id from prior findings>\n"
    "  EVIDENCE: why you agree (must be independent reasoning, not just repetition)\n\n"
    "### CHALLENGE of a prior finding (you disagree with evidence):\n"
    "  TYPE: CHALLENGE\n"
    "  CHALLENGES: <finding_id from prior findings>\n"
    "  EVIDENCE: why the finding is wrong or incomplete\n"
    "  PROPOSED_CORRECTION: what should be said instead (if applicable)\n\n"
)


def format_attributed_findings(
    findings: List[Finding],
    max_findings: int = 150,
    recency_rounds: int = 3,
) -> str:
    """Format findings with source attribution for sequential confer.

    Each finding shows which model produced it, enabling downstream models
    to validate or challenge specific findings by ID and source.
    """
    if not findings:
        return "(No findings from prior rounds.)"

    if len(findings) <= max_findings:
        selected = findings
    else:
        max_round = max(f.round_idx for f in findings)
        recent_cutoff = max(0, max_round - recency_rounds + 1)
        recent = [f for f in findings if f.round_idx >= recent_cutoff]
        older = [f for f in findings if f.round_idx < recent_cutoff]
        remaining_slots = max(0, max_findings - len(recent))
        older_sorted = sorted(older, key=lambda f: f.severity, reverse=True)
        selected = recent + older_sorted[:remaining_slots]

    lines = [f"(Showing {len(selected)} of {len(findings)} total findings: "
             f"most recent rounds + highest severity from earlier rounds)\n"]
    for f in selected:
        lines.append(
            f"FINDING_ID: {f.finding_id}  [source: {f.model_id}]\n"
            f"  SEVERITY: {f.severity:.2f}\n"
            f"  FLAW_CLASS: {f.flaw_class}\n"
            f"  ABSTRACTION: {f.abstraction_index:.2f}\n"
            f"  VERIFIED: {'TRUE' if f.verified else 'FALSE'}\n"
            f"  DESCRIPTION: {f.description[:300]}\n"
        )
    return "\n".join(lines)


def format_within_round_findings(
    findings: List[Finding],
) -> str:
    """Format findings from earlier steps in the SAME round for sequential confer.

    These are the findings the current model should validate/challenge.
    Includes full description and proposed_fix for informed response.
    """
    if not findings:
        return ""

    lines = [f"=== FINDINGS FROM THIS ROUND (from models dispatched before you) ===\n"]
    for f in findings:
        lines.append(
            f"FINDING_ID: {f.finding_id}  [source: {f.model_id}]\n"
            f"  SEVERITY: {f.severity:.2f}\n"
            f"  FLAW_CLASS: {f.flaw_class}\n"
            f"  ABSTRACTION: {f.abstraction_index:.2f}\n"
            f"  DESCRIPTION: {f.description}\n"
            f"  PROPOSED_FIX: {f.proposed_fix}\n"
            f"  VERIFIED: {'TRUE' if f.verified else 'FALSE'}\n"
        )
    lines.append("=== END FINDINGS FROM THIS ROUND ===\n")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch ordering
# ─────────────────────────────────────────────────────────────────────────────

# Task-to-fingerprint dimension mapping: which capability dimension
# matters most for each task type.
TASK_FINGERPRINT_KEY = {
    "immune": "A",       # Analytical capability
    "loadbalancing": "A",
    "persistence": "A",
    "mathmodel": "C",    # Correctness / precision
}


def get_dispatch_order(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    task_key: str,
) -> List[ModelConfig]:
    """Determine sequential dispatch order for a task.

    Strongest model on the relevant fingerprint dimension goes first.
    Player_manager (CC2) always goes last to arbitrate.

    Returns ordered list of ModelConfig objects (excluding collator).
    """
    fp_key = TASK_FINGERPRINT_KEY.get(task_key, "A")

    # Get active (non-collator) models
    active = [mc for mc in exp_config.models if mc.role != "collator"]

    # Separate player_manager — always goes last
    manager = [mc for mc in active if mc.role == "player_manager"]
    participants = [mc for mc in active if mc.role != "player_manager"]

    # Sort participants by relevant fingerprint dimension (descending)
    def _fp_score(mc: ModelConfig) -> float:
        fp = INITIAL_FINGERPRINTS.get(mc.label, CapabilityFingerprint(0.2, 0.7, 0.7, 0.5))
        return getattr(fp, fp_key, 0.5)

    participants.sort(key=_fp_score, reverse=True)

    return participants + manager


# ─────────────────────────────────────────────────────────────────────────────
# Telemetry (inherited from Exp 17 with confer extensions)
# ─────────────────────────────────────────────────────────────────────────────

class ConferTelemetry:
    """Round-level telemetry with confer-specific metrics."""

    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir
        self.rounds: List[Dict[str, Any]] = []

    def record(
        self,
        round_idx: int,
        task_key: str,
        dispatch_order: List[str],
        novel_counts: Dict[str, int],
        validation_counts: Dict[str, int],
        challenge_counts: Dict[str, int],
        diagnoses: List[DetectorDiagnosis],
        recovery_actions: Dict[str, str],
    ):
        entry = {
            "round": round_idx,
            "task": task_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dispatch_order": dispatch_order,
            "novel_counts": novel_counts,
            "validation_counts": validation_counts,
            "challenge_counts": challenge_counts,
            "diagnoses": [
                {"detector": d.detector, "pathology": d.pathology,
                 "severity": d.severity}
                for d in diagnoses
            ],
            "recovery_actions": recovery_actions,
        }
        self.rounds.append(entry)
        self._save()

    def _save(self):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        path = self.logs_dir / "confer_telemetry.json"
        path.write_text(json.dumps(self.rounds, indent=2, ensure_ascii=False),
                        encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Confer prompt construction
# ─────────────────────────────────────────────────────────────────────────────

def _build_confer_prompt(
    task_key: str,
    round_label: str,
    round_type: str,
    code: str,
    math_appendix: str,
    verification_chain: str,
    interface_summary: str,
    prior_findings_text: str = "",
    within_round_text: str = "",
    dispatch_position: int = 0,
    total_models: int = 5,
    is_arbitrator: bool = False,
) -> str:
    """Build a confer prompt for one task, one model, one position in sequence.

    Unlike Exp 17's _build_task_prompt, this includes:
    - Within-round findings from models dispatched before this one
    - Explicit instructions to produce NOVEL, VALIDATION, CHALLENGE outputs
    - Arbitrator instructions for the player_manager (last in sequence)
    """
    prefix = {t[0]: t[1] for t in TASKS}[task_key]
    task_desc = {t[0]: t[2] for t in TASKS}[task_key]

    preamble = (
        f"You are in {round_label} of Experiment 20 — "
        f"TASK: {task_desc}.\n"
        f"You are model {dispatch_position + 1} of {total_models} "
        f"in this round's sequential dispatch.\n\n"
        f"You are operating UNDER CDSFL (your system prompt). Apply P-pass.\n\n"
    )

    # Prior round findings (attributed)
    if round_type == "blind":
        preamble += "This is a BLIND round. No prior findings provided.\n\n"
    elif prior_findings_text:
        preamble += (
            f"## Findings from prior rounds (attributed):\n\n"
            f"{prior_findings_text}\n\n"
        )

    # Within-round findings (from models dispatched before this one)
    if within_round_text:
        preamble += (
            f"{within_round_text}\n\n"
        )

    # Role-specific instructions
    if is_arbitrator:
        preamble += (
            "## Your Role: ARBITRATOR\n"
            "You are the last model in this round's sequence. You have seen "
            "all other models' findings. Your task:\n"
            "1. Produce any NOVEL findings the other models missed.\n"
            "2. VALIDATE findings where multiple models agree (state the consensus).\n"
            "3. CHALLENGE findings where models disagree (adjudicate with evidence).\n"
            "4. Produce a ROUND SYNTHESIS at the end: list the top 5 highest-"
            "confidence findings from this round, ranked by independent "
            "validation count.\n\n"
        )
    elif dispatch_position == 0:
        preamble += (
            "## Your Role: FIRST REVIEWER\n"
            "You are the first model dispatched this round. No other models "
            "have reviewed this task yet in this round. Produce your NOVEL "
            "findings. Later models will validate or challenge them.\n\n"
        )
    else:
        preamble += (
            "## Your Role: CONFER\n"
            "Models dispatched before you have produced findings (shown above). "
            "Your task:\n"
            "1. Produce your own NOVEL findings (issues not yet raised).\n"
            "2. VALIDATE prior findings you independently confirm (with evidence).\n"
            "3. CHALLENGE prior findings you disagree with (with evidence).\n"
            "Do not repeat findings — if you agree, validate explicitly.\n\n"
        )

    # Task-specific boundary and artifact (same as Exp 17)
    if task_key == "immune":
        boundary = (
            "## Analytical Boundary\n"
            "IMMUNE RESPONSE LAYER: DetectorDiagnosis, DetectorHealthMonitor, "
            "FailureHandler, _REMEDIATION_CHAINS, process_round() immune "
            "integration, apply_diagnosis(), _apply_transform(), and immune "
            "config parameters.\n\n"
            "The rest of dynamic_management.py is context — focus findings "
            "on immune behaviour.\n\n"
        )
        if interface_summary:
            boundary += f"## Interface Summary\n{interface_summary}\n\n"
        artifact = (
            f"=== ARTIFACT: dynamic_management.py ===\n\n{code}\n\n"
            f"=== END ARTIFACT ===\n\n"
        )
    elif task_key == "loadbalancing":
        boundary = (
            "## Analytical Boundary\n"
            "LOAD BALANCING: LoadBalancer, RoleAssignment, _solve_greedy(), "
            "feasibility_probability(), capability scoring, role allocation, "
            "task decomposition, model selection.\n\n"
            "The rest of dynamic_management.py is context — focus findings "
            "on load balancing correctness and efficiency.\n\n"
        )
        artifact = (
            f"=== ARTIFACT: dynamic_management.py ===\n\n{code}\n\n"
            f"=== END ARTIFACT ===\n\n"
        )
    elif task_key == "persistence":
        boundary = (
            "## Analytical Boundary\n"
            "PERSISTENCE LAYER: verification_chain.py — hash chains, Merkle "
            "trees, Ed25519 signing, epoch sealing, inclusion proofs.\n\n"
        )
        artifact = (
            f"=== ARTIFACT: verification_chain.py ===\n\n"
            f"{verification_chain}\n\n"
            f"=== END ARTIFACT ===\n\n"
        )
    elif task_key == "mathmodel":
        boundary = (
            "## Analytical Boundary\n"
            "MATHEMATICAL MODEL: MATHEMATICAL_APPENDIX.md — verify internal "
            "mathematical consistency. Also cross-reference against the code "
            "in dynamic_management.py to verify that formulas are implemented "
            "correctly. Flag any discrepancies between model and code.\n\n"
        )
        artifact = (
            f"=== ARTIFACT 1: MATHEMATICAL_APPENDIX.md ===\n\n"
            f"{math_appendix}\n\n"
            f"=== END ARTIFACT 1 ===\n\n"
            f"=== ARTIFACT 2: dynamic_management.py (for cross-reference) ===\n\n"
            f"{code}\n\n"
            f"=== END ARTIFACT 2 ===\n\n"
        )
    else:
        raise ValueError(f"Unknown task_key: {task_key}")

    fmt = CONFER_FINDING_FORMAT.format(prefix=prefix)
    return preamble + boundary + fmt + artifact + "Produce your output now."


# ─────────────────────────────────────────────────────────────────────────────
# Sequential confer dispatch
# ─────────────────────────────────────────────────────────────────────────────

# Whether to use cached results (set by --resume flag)
RESUME_MODE = False


def _dispatch_confer_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    task_key: str,
    round_label: str,
    round_type: str,
    round_idx: int,
    phase_prefix: str,
    code: str,
    math_appendix: str,
    verification_chain: str,
    interface_summary: str,
    prior_findings: List[Finding],
    cdsfl_text: str,
) -> Tuple[List[Finding], Dict[str, str]]:
    """Dispatch one task to all models SEQUENTIALLY with confer.

    Models are dispatched in fingerprint-based order. Each model after the
    first sees the findings from all models dispatched before it in this
    round. The last model (player_manager) acts as arbitrator.

    Returns (all_findings_this_task, {label: response_text}).
    """
    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    within_round_findings: List[Finding] = []

    # Determine dispatch order
    ordered_models = get_dispatch_order(exp_config, mgr, task_key)
    order_labels = [mc.label for mc in ordered_models]
    _log(f"  Dispatch order: {' → '.join(order_labels)}")

    prior_text = format_attributed_findings(prior_findings)

    for step_idx, mc in enumerate(ordered_models):
        phase_label = f"{phase_prefix}_{task_key}"
        is_last = (step_idx == len(ordered_models) - 1)

        # Resume: check for cached response
        if RESUME_MODE:
            cached = _find_cached(phase_label, mc.label)
            if cached:
                model_findings = parse_findings(mc.label, round_idx, cached)
                findings.extend(model_findings)
                within_round_findings.extend(model_findings)
                responses[mc.label] = cached
                _log(f"  {mc.label} (step {step_idx + 1}): "
                     f"{len(model_findings)} findings (from cache)")
                continue

        # Build within-round context (findings from previous steps)
        within_round_text = format_within_round_findings(within_round_findings)

        # Build the confer prompt
        prompt = _build_confer_prompt(
            task_key=task_key,
            round_label=round_label,
            round_type=round_type,
            code=code,
            math_appendix=math_appendix,
            verification_chain=verification_chain,
            interface_summary=interface_summary,
            prior_findings_text=prior_text if round_type != "blind" else "",
            within_round_text=within_round_text,
            dispatch_position=step_idx,
            total_models=len(ordered_models),
            is_arbitrator=(is_last and mc.role == "player_manager"),
        )

        # Dynamic decomposition (inherited from Exp 17)
        decomposed = False
        if _should_decompose(mc.label, mgr):
            prompt, decomposed = _build_decomposed_prompt(
                prompt, code, task_key, mc.label, round_idx)

        # Pre-dispatch feasibility gate
        model_spec = _find_model_spec(mgr, mc.label)
        if model_spec and not decomposed:
            token_est = len(prompt) // 4
            ok, p_feasible = mgr.check_dispatch_feasibility(model_spec, token_est)
            if not ok:
                _log(f"  {mc.label} (step {step_idx + 1}): DISPATCH BLOCKED — "
                     f"P(feasible)={p_feasible:.3f}. Auto-decomposing.")
                prompt, decomposed = _build_decomposed_prompt(
                    prompt, code, task_key, mc.label, round_idx)
                mgr.config.pre_decompose_models.add(mc.label)

        _log(f"  {mc.label} (step {step_idx + 1}/{len(ordered_models)}): "
             f"prompt {len(prompt):,} chars{' [decomposed]' if decomposed else ''}"
             f"{' [ARBITRATOR]' if is_last and mc.role == 'player_manager' else ''}")

        try:
            text, elapsed = dispatch_to_model(mc, prompt, cdsfl_text)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")

            model_findings = parse_findings(mc.label, round_idx, text)
            findings.extend(model_findings)
            within_round_findings.extend(model_findings)
            responses[mc.label] = text
            _log(f"  {mc.label}: {len(model_findings)} findings parsed")

            save_output(
                LOGS_DIR, phase_label, mc.label,
                prompt[:200] + "...", text,
                metadata={
                    "elapsed": round(elapsed, 1),
                    "chars": len(text),
                    "findings_count": len(model_findings),
                    "round": round_idx,
                    "step": step_idx,
                    "dispatch_position": f"{step_idx + 1}/{len(ordered_models)}",
                    "decomposed": decomposed,
                    "is_arbitrator": is_last and mc.role == "player_manager",
                    "within_round_findings_seen": len(within_round_findings) - len(model_findings),
                    "prompt_chars": len(prompt),
                },
            )

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
        except TimeoutError as e:
            _log(f"  {mc.label}: TIMEOUT — {e}")
            _report_dispatch_failure(mgr, mc.label, round_idx, f"timeout: {e}")
        except Exception as e:
            _log(f"  {mc.label}: ERROR — {type(e).__name__}: {e}")
            _report_dispatch_failure(mgr, mc.label, round_idx,
                                     f"{type(e).__name__}: {e}")

    return findings, responses


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment
# ─────────────────────────────────────────────────────────────────────────────

def run_experiment() -> Dict[str, Any]:
    """Run full Experiment 20."""
    experiment_start = time.monotonic()
    _log(f"=== EXPERIMENT 20: SEQUENTIAL CONFER WITH ATTRIBUTED FINDINGS ===")
    _log(f"Logs: {LOGS_DIR}")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load config
    exp_config = load_default_config()
    cdsfl_text = exp_config.cdsfl_system_prompt

    # Load test articles
    code = TEST_ARTICLE_PATH.read_text(encoding="utf-8")
    _log(f"Test article: {len(code)} chars, {len(code.splitlines())} lines")

    interface_summary = ""
    if INTERFACE_SUMMARY_PATH.exists():
        interface_summary = INTERFACE_SUMMARY_PATH.read_text(encoding="utf-8")
        _log(f"Interface summary: {len(interface_summary)} chars")

    math_appendix = ""
    if MATH_APPENDIX_PATH.exists():
        math_appendix = MATH_APPENDIX_PATH.read_text(encoding="utf-8")
        _log(f"Mathematical appendix: {len(math_appendix)} chars")

    verification_chain = ""
    if VERIFICATION_CHAIN_PATH.exists():
        verification_chain = VERIFICATION_CHAIN_PATH.read_text(encoding="utf-8")
        _log(f"Verification chain: {len(verification_chain)} chars")

    # Build DynamicManager with Codex pre-decomposed (inherited from Exp 17)
    model_specs = build_model_specs(exp_config)
    dm_config = DynamicManagementConfig(
        immune_feedback_enabled=True,
        immune_damping_rounds=2,
        pre_decompose_models={"Codex"},
    )
    tasks = [Task(task_id="confer_review", token_demand=len(code) // 4,
                  flaw_class=1, criticality=0.8)]
    mgr = DynamicManager(model_specs, dm_config)

    telemetry = ConferTelemetry(LOGS_DIR)

    # Freeze manifest
    import subprocess as _sp
    head_hash = _sp.check_output(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT)
    ).decode().strip()
    manifest = {
        "experiment": EXPERIMENT,
        "architecture": "sequential_confer",
        "commit": head_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "test_articles": [
            str(TEST_ARTICLE_PATH), str(MATH_APPENDIX_PATH),
            str(VERIFICATION_CHAIN_PATH),
        ],
        "models": [{"label": m.label, "model_id": m.model_id, "api": m.api,
                     "role": m.role}
                   for m in exp_config.models if m.role != "collator"],
        "config": {
            "immune_feedback_enabled": True,
            "immune_damping_rounds": 2,
            "max_rounds": MAX_ROUNDS,
            "wall_clock_cap_s": WALL_CLOCK_CAP_S,
            "dispatch_mode": "sequential_confer",
            "pre_decompose_models": list(dm_config.pre_decompose_models),
        },
    }
    (LOGS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    _log(f"Manifest frozen: {head_hash[:8]}")

    all_findings: List[Finding] = []
    per_task_findings: Dict[str, List[Finding]] = {t[0]: [] for t in TASKS}
    round_results: List[Dict[str, Any]] = []

    def _dispatch_all_tasks(round_label: str, round_type: str,
                            round_idx: int, phase_prefix: str) -> int:
        """Dispatch all 4 tasks sequentially-within-task for one round."""
        round_total = 0
        round_entry: Dict[str, Any] = {"round": round_label}

        for task_key, id_prefix, task_desc in [(t[0], t[1], t[2]) for t in TASKS]:
            _log(f"\n--- {round_label}: {task_desc} ---")

            task_findings, task_responses = _dispatch_confer_round(
                exp_config=exp_config,
                mgr=mgr,
                task_key=task_key,
                round_label=round_label,
                round_type=round_type,
                round_idx=round_idx,
                phase_prefix=phase_prefix,
                code=code,
                math_appendix=math_appendix,
                verification_chain=verification_chain,
                interface_summary=interface_summary,
                prior_findings=per_task_findings[task_key],
                cdsfl_text=cdsfl_text,
            )

            per_task_findings[task_key].extend(task_findings)
            all_findings.extend(task_findings)
            round_entry[task_key] = len(task_findings)
            round_total += len(task_findings)
            _log(f"  {task_desc}: {len(task_findings)} findings from "
                 f"{len(task_responses)} models (sequential confer)")

        round_entry["total"] = round_total
        round_entry["findings"] = round_total
        round_entry["models"] = len([m for m in exp_config.models if m.role != "collator"])
        round_results.append(round_entry)
        return round_total

    # ── ROUND 0A: Blind Discovery (sequential but no confer — first pass) ──
    _log("\n=== ROUND 0A: BLIND DISCOVERY (4 tasks × 5 models, sequential) ===")
    r0a_total = _dispatch_all_tasks("ROUND 0A (BLIND)", "blind", 0, "r0a")
    _log(f"\nRound 0A total: {r0a_total} findings across 4 tasks")

    # Process through DynamicManager
    r0a_all = all_findings[:]
    if r0a_all:
        r0a_responses = {f.model_id: ModelResponse(
            model_id=f.model_id, round_idx=0, response_text="",
            findings=[f]) for f in r0a_all}
        result = mgr.process_round(r0a_responses, r0a_all, tasks, round_cost=1.0)

    # ── ROUND 0B: Seeded Confer (sequential with attributed findings) ──
    _log("\n=== ROUND 0B: SEEDED CONFER (4 tasks × 5 models, sequential) ===")
    r0b_total = _dispatch_all_tasks("ROUND 0B (SEEDED)", "seeded", 1, "r0b")
    _log(f"\nRound 0B total: {r0b_total} findings across 4 tasks")

    r0b_findings = all_findings[len(r0a_all):]
    if r0b_findings:
        r0b_responses = {f.model_id: ModelResponse(
            model_id=f.model_id, round_idx=1, response_text="",
            findings=[f]) for f in r0b_findings}
        result = mgr.process_round(r0b_responses, r0b_findings, tasks, round_cost=1.0)

    # ── ADAPTIVE CONFER ROUNDS ──
    for round_idx in range(2, MAX_ROUNDS):
        elapsed_total = time.monotonic() - experiment_start
        if elapsed_total > WALL_CLOCK_CAP_S:
            _log(f"\n  WALL-CLOCK CAP reached ({elapsed_total:.0f}s > "
                 f"{WALL_CLOCK_CAP_S}s)")
            break

        _log(f"\n=== ROUND {round_idx}: ADAPTIVE CONFER (4 tasks × 5 models) ===")

        if mgr.diminishing_returns.stop(round_idx - 1):
            _log(f"  DynamicManager stop() fired at round {round_idx}")
            break

        pre_count = len(all_findings)
        rn_total = _dispatch_all_tasks(
            f"ROUND {round_idx} (ADAPTIVE)", "adaptive", round_idx,
            f"round{round_idx}")
        _log(f"\nRound {round_idx}: {rn_total} findings across 4 tasks")

        rn_findings = all_findings[pre_count:]
        if rn_findings:
            rn_responses = {f.model_id: ModelResponse(
                model_id=f.model_id, round_idx=round_idx, response_text="",
                findings=[f]) for f in rn_findings}
            result = mgr.process_round(rn_responses, rn_findings, tasks, round_cost=1.0)
        else:
            _log(f"  Zero findings across all 4 tasks — convergence reached")
            break

    # ── Summary ──
    elapsed_total = time.monotonic() - experiment_start
    _log(f"\n=== EXPERIMENT 20 SUMMARY ===")
    _log(f"Architecture: sequential confer with attributed findings")
    _log(f"Total findings: {len(all_findings)}")
    _log(f"Rounds completed: {len(round_results)}")
    _log(f"Wall clock: {elapsed_total:.0f}s ({elapsed_total/60:.1f} min)")
    for rr in round_results:
        _log(f"  {rr['round']}: {rr.get('total', '?')} findings")

    report = {
        "experiment": EXPERIMENT,
        "architecture": "sequential_confer",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit": head_hash,
        "total_findings": len(all_findings),
        "rounds": round_results,
        "wall_clock_s": round(elapsed_total, 1),
        "stop_reason": "convergence" if len(round_results) < MAX_ROUNDS else "cap",
    }
    (LOGS_DIR / f"experiment_{EXPERIMENT}_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")

    return report


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    source_env()

    mode = sys.argv[1] if len(sys.argv) > 1 else "run"

    if mode == "preflight":
        ok1 = run_layer1_preflight()
        config = load_default_config()
        ok2 = _run_model_preflight(config)
        sys.exit(0 if (ok1 and ok2) else 1)
    elif mode == "canary":
        ok = run_canary_tests()
        sys.exit(0 if ok else 1)
    elif mode in ("run", "resume"):
        if mode == "resume":
            RESUME_MODE = True
            _log("=== RESUME MODE: will use cached responses where available ===")
            import glob
            cached = glob.glob(str(LOGS_DIR / "*.json"))
            _log(f"  Found {len(cached)} cached response files in {LOGS_DIR}")

        _log("Phase 1: Layer 1 preflight")
        if not run_layer1_preflight():
            _log("Layer 1 preflight FAILED — aborting")
            sys.exit(1)

        _log("\nPhase 2: Canary tests")
        if not run_canary_tests():
            _log("WARNING: Some canary tests failed. Proceeding with caution.")

        _log("\nPhase 3: Model preflight")
        config = load_default_config()
        # Point preflight logs at Exp 20 dir
        import run_exp16_plan_review
        run_exp16_plan_review.LOGS_DIR = LOGS_DIR
        if not _run_model_preflight(config):
            _log("Model preflight FAILED — aborting")
            sys.exit(1)

        _log("\nPhase 4: Experiment 20 (sequential confer)")
        report = run_experiment()
        _log(f"\nExperiment 20 complete. {report['total_findings']} findings "
             f"across {len(report['rounds'])} rounds.")
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python3 bench/run_exp20_confer.py [preflight|canary|run|resume]")
        sys.exit(1)
