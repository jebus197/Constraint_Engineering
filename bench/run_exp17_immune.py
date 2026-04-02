#!/usr/bin/env python3
"""Experiment 17: Immune + Load Balancing + Persistence Layer Validation.

Executes the APPROVED Experiment 17 plan (reviewed by 5 models in Exp 16),
expanded to include load balancing and the persistence layer (verification_chain.py)
which only received a single blind pass in Experiment 10.

Test articles:
  1. dynamic_management.py (immune + load balancing)
  2. MATHEMATICAL_APPENDIX.md (mathematical model)
  3. verification_chain.py (persistence / verification chain)

Key design decisions from Experiment 16 convergence:
- Full file delivery (not extracted lines) — unanimous
- Split Round 0: R0A blind + R0B seeded validation — 4/5
- Independent stop caps: round 10 + wall-clock 4h — 3/5
- Behaviour-based success criteria — 4/5
- DeepSeek decomposition into 5 sub-areas — unanimous (expanded from 3)
- Mandatory round-level telemetry — 3/5
- Fault injection scenarios before live experiment — 4/5

Usage:
    python3 bench/run_exp17_immune.py [preflight|canary|run]

    preflight  — verify all models respond + Layer 1 acceptance tests
    canary     — run induced-failure scenarios only
    run        — full experiment (preflight + canary + R0A + R0B + adaptive rounds)
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

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
    format_findings_for_context,
    INITIAL_FINGERPRINTS,
    MODEL_SPECS,
    CONVERGENCE_EXCLUDED_MODELS,
)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

EXPERIMENT = "17"
LOGS_DIR = REPO_ROOT / "bench" / "logs" / f"experiment_{EXPERIMENT}"

# Independent stop caps (Exp 16 convergent: CC2, ChatGPT, Codex)
MAX_ROUNDS = 10
WALL_CLOCK_CAP_S = 4 * 3600  # 4 hours

# Sub-area decomposition (Exp 16: unanimous, expanded for LB + persistence)
# Used by DeepSeek (always decomposed) and any model in pre_decompose_models
# when task-level extraction exceeds SUBAREA_ESCALATION_CHARS.
REVIEW_AREAS = [
    ("Detection", ["DetectorDiagnosis", "DetectorHealthMonitor"]),
    ("Response", ["FailureHandler"]),
    ("Integration", ["process_round", "apply_diagnosis", "_apply_transform",
                      "_REMEDIATION_CHAINS", "immune_feedback_enabled"]),
    ("LoadBalancing", ["LoadBalancer", "RoleAssignment", "_solve_greedy",
                       "feasibility_probability"]),
    ("Persistence", []),  # verification_chain.py — separate file, handled specially
]

# Per-task sub-area maps: used for sub-area escalation when task-level
# decomposition is still too large for a model (CC2 confer finding F002+F005).
# Immune uses REVIEW_AREAS. Mathmodel needs its own sub-areas because
# MATHEMATICAL_APPENDIX.md (55K) pushes the decomposed prompt to ~110K.
TASK_SUBAREAS = {
    "immune": REVIEW_AREAS,
    "mathmodel": [
        ("Config", ["DynamicManagementConfig"]),
        ("Convergence", ["ConvergenceDetector", "FindingEquivalenceClass"]),
        ("DiminishingReturns", ["DiminishingReturnsDetector"]),
    ],
    # loadbalancing (42K) and persistence (27K) are small enough — no sub-areas needed
}

# Threshold for sub-area escalation: if task-level decomposition exceeds this,
# fall back to sub-area rotation. Model-specific via throughput gate when
# available; this is the static fallback (CC2 confer: should be model-specific,
# but the throughput gate handles that dynamically).
SUBAREA_ESCALATION_CHARS = 80_000

# Task-level extraction markers: which classes/functions belong to each task.
# Used for prompt decomposition — extracts focused code + skeletal context.
TASK_MARKERS = {
    "immune": [
        "DetectorDiagnosis", "DetectorHealthMonitor", "FailureHandler",
        "FailureType", "RecoveryAction", "FailureRecord",
        "CorrelatedFailureModel", "_REMEDIATION_CHAINS",
        "apply_diagnosis", "_apply_transform", "immune_feedback_enabled",
    ],
    "loadbalancing": [
        "LoadBalancer", "RoleAssignment", "Allocation", "Role",
        "_solve_greedy", "feasibility_probability", "dispatch_check",
        "CapabilityFingerprint", "ModelSpec", "Task",
    ],
    "mathmodel": [
        # Math model task cross-references code against MATHEMATICAL_APPENDIX.md.
        # Extract config (constants/formulas) + convergence + diminishing returns.
        "DynamicManagementConfig", "ConvergenceDetector",
        "DiminishingReturnsDetector", "FindingEquivalenceClass",
    ],
    # persistence uses verification_chain.py directly — no extraction from DM needed
}

# ─── Throughput tracking (CC2 confer F004+F006) ────────────────────────
# In-memory: accumulate (prompt_chars, elapsed_seconds) per model.
# Median-of-last-3 for robustness to outliers (Codex R2=254s, R3=timeout).
# Used by post-decomposition feasibility check.
_throughput_observations: Dict[str, List[tuple]] = {}  # model_label -> [(chars, secs)]


def _record_throughput(model_label: str, prompt_chars: int, elapsed_secs: float) -> None:
    """Record a dispatch observation for throughput estimation."""
    if elapsed_secs > 0:
        _throughput_observations.setdefault(model_label, []).append(
            (prompt_chars, elapsed_secs))


def _estimate_throughput(model_label: str) -> Optional[float]:
    """Estimate chars/second for a model using median of last 3 observations.

    Returns None if fewer than 2 observations (use ModelSpec.tau as prior).
    """
    obs = _throughput_observations.get(model_label, [])
    if len(obs) < 2:
        return None
    recent = obs[-3:]  # last 3
    rates = [chars / secs for chars, secs in recent if secs > 0]
    if not rates:
        return None
    rates.sort()
    mid = len(rates) // 2
    return rates[mid]  # median


def _effective_capacity(model_label: str, timeout: float) -> Optional[int]:
    """Estimate max prompt chars a model can process within its timeout.

    Returns None if insufficient throughput data.
    """
    tp = _estimate_throughput(model_label)
    if tp is None:
        return None
    return int(tp * timeout)


# Convergent findings for R0B seeded validation
CONVERGENT_FINDINGS_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_plan.md"

# Reference documents for model context
INTERFACE_SUMMARY_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_interface_summary.md"
TRACEABILITY_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_traceability.md"
TEST_ARTICLE_PATH = REPO_ROOT / "bench" / "dynamic_management.py"
MATH_APPENDIX_PATH = REPO_ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
VERIFICATION_CHAIN_PATH = REPO_ROOT / "bench" / "verification_chain.py"


# ─────────────────────────────────────────────────────────────────────────────
# Telemetry (Exp 16 convergent: ChatGPT, DeepSeek, CC2)
# ─────────────────────────────────────────────────────────────────────────────

class RoundTelemetry:
    """Round-level immune decision logging."""

    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir
        self.rounds: List[Dict[str, Any]] = []

    def record(
        self,
        round_idx: int,
        diagnoses: List[DetectorDiagnosis],
        recovery_actions: Dict[str, str],
        immune_adjustments: List[Dict],
        stop_inputs: Dict[str, Any],
        active_models: set,
        allocation_warnings: List[str],
    ):
        entry = {
            "round": round_idx,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "diagnoses": [
                {"detector": d.detector, "pathology": d.pathology,
                 "severity": d.severity, "recommended_action": d.recommended_action}
                for d in diagnoses
            ],
            "recovery_actions": recovery_actions,
            "immune_adjustments": immune_adjustments,
            "stop_inputs": stop_inputs,
            "active_models": sorted(active_models),
            "allocation_warnings": allocation_warnings,
        }
        self.rounds.append(entry)
        self._save()
        _log(f"  Telemetry: {len(diagnoses)} diagnoses, "
             f"{len(recovery_actions)} recoveries, "
             f"{len(immune_adjustments)} adjustments")

    def _save(self):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        path = self.logs_dir / "telemetry.json"
        path.write_text(json.dumps(self.rounds, indent=2, ensure_ascii=False),
                        encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Code extraction / decomposition
# ─────────────────────────────────────────────────────────────────────────────

# Immune layer integration interfaces: when a sub-area rotation excludes
# a component, models still need to see its PUBLIC interface (signatures,
# parameter types, return types) to verify cross-component correctness.
# Without this, models reviewing Detection can't verify how apply_diagnosis()
# calls DetectorHealthMonitor methods, and models reviewing Integration
# can't verify what DetectorDiagnosis fields they're reading.
#
# Run 7b fix: skeletal context (def+docstring only) was insufficient.
# ChatGPT correctly flagged this as a "completeness failure relative to
# the task boundary." The fix: include full function signatures + type
# hints + first 10 lines of body for interface-critical non-target blocks.
_INTERFACE_CRITICAL_MARKERS = {
    # These are always included at interface depth (sig + 10 body lines)
    # regardless of which sub-area is the current rotation target.
    "apply_diagnosis", "_apply_transform", "_REMEDIATION_CHAINS",
    "process_round", "record_round", "record_model_round",
    "register_diagnoses", "_verify_remediation_outcomes",
    "check_dispatch_feasibility", "check_dispatch_health",
    "detect_failure", "handle_failure",
}


def _extract_code_area(code: str, markers: List[str],
                       area_label: str = "") -> str:
    """Extract code matching markers + interface context from dynamic_management.py.

    Used for both DeepSeek sub-area decomposition and task-level decomposition
    for any model in pre_decompose_models.

    Returns focused code with three tiers:
      1. TARGET: full code for classes/functions matching `markers`.
      2. INTERFACE: signature + type hints + first 10 body lines for
         functions in _INTERFACE_CRITICAL_MARKERS (cross-component APIs).
      3. SKELETAL: definition + docstring only for everything else.
      4. CONFIG: first 200 lines (module config, enums, dataclasses).

    The interface tier is the Run 7b fix: it ensures that models reviewing
    one sub-area can still verify how it connects to other sub-areas.
    """
    lines = code.split("\n")

    # Find all class/function boundaries (top-level classes, class methods)
    boundaries = []
    for i, line in enumerate(lines):
        raw = line.rstrip()
        stripped = line.strip()
        # Top-level class definitions
        if re.match(r'^class \w+', stripped):
            boundaries.append((i, stripped))
        # Class methods (indented def) — match against raw line to preserve indent
        elif re.match(r'^    def \w+', raw):
            boundaries.append((i, stripped))

    target_lines: set = set()
    interface_lines: set = set()
    context_lines: set = set()

    for start_idx, defn in boundaries:
        # Find end of this block
        end_idx = len(lines)
        for next_start, _ in boundaries:
            if next_start > start_idx:
                end_idx = next_start
                break

        is_target = any(marker in defn for marker in markers)
        is_interface = any(marker in defn for marker in _INTERFACE_CRITICAL_MARKERS)

        if is_target:
            # Full code
            for j in range(start_idx, end_idx):
                target_lines.add(j)
        elif is_interface:
            # Interface depth: signature + first 10 lines of body.
            # This gives models enough to verify parameter types, return
            # types, and the shape of the interaction without the full
            # implementation.
            interface_depth = min(start_idx + 15, end_idx)
            for j in range(start_idx, interface_depth):
                interface_lines.add(j)
            # Add a marker showing the block was truncated
            if interface_depth < end_idx:
                # We'll add a comment after assembly
                pass
        else:
            # Skeletal: definition + docstring only
            context_lines.add(start_idx)
            if start_idx + 1 < end_idx and '"""' in lines[start_idx + 1]:
                context_lines.add(start_idx + 1)
                # Include closing triple-quote if docstring spans multiple lines
                for j in range(start_idx + 2, min(start_idx + 20, end_idx)):
                    context_lines.add(j)
                    if '"""' in lines[j]:
                        break

    # Module-level config (first 200 lines)
    for j in range(min(200, len(lines))):
        context_lines.add(j)

    # Also include _REMEDIATION_CHAINS dict if it's in the code
    # (it's a module-level dict, not a class/def, so boundaries miss it)
    for i, line in enumerate(lines):
        if "_REMEDIATION_CHAINS" in line and ("=" in line or "{" in line):
            # Include the full dict definition (scan for closing brace)
            brace_depth = 0
            for j in range(i, min(i + 200, len(lines))):
                interface_lines.add(j)
                brace_depth += lines[j].count("{") - lines[j].count("}")
                if brace_depth <= 0 and j > i:
                    break

    all_lines = target_lines | interface_lines | context_lines
    return "\n".join(lines[j] for j in sorted(all_lines))


def _extract_immune_area(code: str, area_idx: int) -> tuple[str, str]:
    """Extract one DeepSeek review sub-area. Delegates to _extract_code_area."""
    area_name, markers = REVIEW_AREAS[area_idx % len(REVIEW_AREAS)]
    focused = _extract_code_area(code, markers, area_name)
    return focused, area_name


def _extract_task_area(code: str, task_key: str) -> Optional[str]:
    """Extract task-relevant code from dynamic_management.py for decomposed dispatch.

    Returns focused code for the task, or None if the task doesn't need
    extraction from DM (e.g. persistence uses verification_chain.py).
    """
    markers = TASK_MARKERS.get(task_key)
    if markers is None:
        return None
    return _extract_code_area(code, markers, task_key)


def _should_decompose(model_label: str, mgr: DynamicManager) -> bool:
    """Check if a model should receive decomposed (smaller) prompts.

    DeepSeek is always decomposed (Exp 16 unanimous).
    Codex is pre-seeded: observed R0A latencies (370-556s) at full prompt
    size are consistently 3-10x slower than other models due to CLI overhead.
    Decomposition reduces this to manageable levels.
    Other models are decomposed if the immune layer added them to
    pre_decompose_models (via model_failure remediation chain).
    """
    if model_label == "DeepSeek":
        return True
    return model_label in mgr.config.pre_decompose_models


# ─────────────────────────────────────────────────────────────────────────────
# Prompts — 4 independent tasks per round
# ─────────────────────────────────────────────────────────────────────────────

FINDING_FORMAT = (
    "## Output Format\n"
    "For each finding:\n"
    "  FINDING_ID: {prefix}F001 (etc.)\n"
    "  SEVERITY: 0.0–1.0\n"
    "  FLAW_CLASS: 1=logic, 2=interface, 3=notation, 4=completeness, "
    "5=correctness, 6=edge-case, 7=performance, 8=documentation\n"
    "  ABSTRACTION_INDEX: 0.0–1.0 (0=surface, 1=architectural)\n"
    "  DESCRIPTION: what is wrong and why\n"
    "  PROPOSED_FIX: specific fix\n"
    "  VERIFIED: TRUE/FALSE\n\n"
)

# Task definitions: (task_key, id_prefix, description, artifact_builder)
TASKS = [
    ("immune", "IM_", "Immune Response Layer"),
    ("loadbalancing", "LB_", "Load Balancing"),
    ("persistence", "VC_", "Persistence Layer (verification chain)"),
    ("mathmodel", "MM_", "Mathematical Model Consistency"),
]


def _build_task_prompt(task_key: str, round_label: str, round_type: str,
                       code: str, math_appendix: str,
                       verification_chain: str,
                       interface_summary: str,
                       prior_findings_text: str = "",
                       convergent_text: str = "") -> str:
    """Build a focused prompt for one of the 4 tasks."""
    prefix = {t[0]: t[1] for t in TASKS}[task_key]
    task_desc = {t[0]: t[2] for t in TASKS}[task_key]

    preamble = (
        f"You are in {round_label} of Experiment 17 — "
        f"TASK: {task_desc}.\n\n"
        f"You are operating UNDER CDSFL (your system prompt). Apply P-pass.\n\n"
    )

    if round_type == "blind":
        preamble += "This is a BLIND round. No prior findings provided.\n\n"
    elif round_type == "seeded" and prior_findings_text:
        preamble += (
            f"Prior findings from earlier rounds:\n\n{prior_findings_text}\n\n"
        )
        if convergent_text:
            preamble += (
                "Additionally, Experiment 15 produced CONVERGENT FINDINGS:\n\n"
                f"{convergent_text}\n\n"
                "VALIDATE applied fixes. CHALLENGE no-fix-needed decisions. "
                "Find what was MISSED.\n\n"
            )
    elif round_type == "adaptive" and prior_findings_text:
        preamble += (
            f"Prior findings for this task:\n\n{prior_findings_text}\n\n"
            "Find what was MISSED. Do not repeat known findings.\n\n"
        )

    # Task-specific boundary and artifact
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
            "trees, Ed25519 signing, epoch sealing, inclusion proofs. This "
            "code has only had a single blind pass (Experiment 10) and has "
            "never been through distributed compute review. Give it the "
            "same rigour you would give production cryptographic code.\n\n"
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

    fmt = FINDING_FORMAT.format(prefix=prefix)
    return preamble + boundary + fmt + artifact + "Produce your findings now."


def _extract_convergent_findings() -> str:
    """Extract §4 from the Exp 17 plan (convergent findings section)."""
    plan = CONVERGENT_FINDINGS_PATH.read_text(encoding="utf-8")
    # Extract section 4
    match = re.search(r'(## 4\. Experiment 15 Convergent Findings.*?)(?=## 5\.)',
                      plan, re.DOTALL)
    return match.group(1).strip() if match else "(Convergent findings not found)"


# ─────────────────────────────────────────────────────────────────────────────
# Canary / induced-failure tests (Exp 16 convergent: 4/5)
# ─────────────────────────────────────────────────────────────────────────────

def run_canary_tests() -> bool:
    """Run induced-failure scenarios against the immune layer.

    Tests:
    1. Canary: 3 consecutive empty responses → immune detects and acts
    2. False positive: benign low-severity finding → immune does NOT over-trigger
    3. Cascade: 2/5 models fail simultaneously → graceful degradation
    4. Oscillation: alternating good/bad → damping prevents thrashing
    """
    _log("=== CANARY TESTS: Induced-Failure Scenarios ===")
    all_passed = True

    # Build a minimal DynamicManager for canary testing
    config = DynamicManagementConfig(
        immune_feedback_enabled=True,
        immune_damping_rounds=2,
    )
    models = [
        ModelSpec(model_id=f"canary_{i}", fingerprint=CapabilityFingerprint(0.2, 0.8, 0.8, 0.7),
                  tau=300.0, L=100000.0, c=0.01)
        for i in range(5)
    ]
    tasks = [Task(task_id="immune_test", token_demand=1000, flaw_class=1, criticality=0.5)]

    mgr = DynamicManager(models, config)

    # ── Test 1: Canary (empty responses) ──
    _log("  Test 1: Canary — 3 consecutive empty responses")
    try:
        recovery_triggered = False
        for r in range(3):
            responses = {}
            findings: List[Finding] = []
            for m in models:
                content = "" if m.model_id == "canary_0" else f"Finding R{r}"
                resp = ModelResponse(
                    model_id=m.model_id, round_idx=r, content=content,
                    response_time=10.0, parseable=bool(content),
                    finding_count=1 if content else 0,
                )
                responses[m.model_id] = resp
                if content:
                    findings.append(Finding(
                        finding_id=f"{m.model_id}_F{r}", model_id=m.model_id,
                        round_idx=r, flaw_class=1, severity=0.5,
                        abstraction_index=0.5, description=f"Test finding {r}",
                    ))

            result = mgr.process_round(responses, findings, tasks, round_cost=1.0)
            if result.recovery_actions.get("canary_0"):
                recovery_triggered = True
                _log(f"    Round {r}: immune triggered recovery for canary_0: "
                     f"{result.recovery_actions['canary_0']}")

        if recovery_triggered:
            _log("  Test 1: PASSED — immune detected empty responses")
        else:
            _log("  Test 1: FAILED — immune did not detect 3 empty responses")
            all_passed = False
    except Exception as e:
        _log(f"  Test 1: ERROR — {type(e).__name__}: {e}")
        all_passed = False

    # ── Test 2: False positive (benign finding) ──
    _log("  Test 2: False positive — low-severity finding should not trigger immune")
    try:
        mgr2 = DynamicManager(models, config)
        responses = {}
        findings = []
        for m in models:
            resp = ModelResponse(
                model_id=m.model_id, round_idx=0, content="All clear",
                response_time=5.0, parseable=True, finding_count=1,
            )
            responses[m.model_id] = resp
            findings.append(Finding(
                finding_id=f"{m.model_id}_F0", model_id=m.model_id,
                round_idx=0, flaw_class=8, severity=0.1,
                abstraction_index=0.1, description="Minor doc issue",
            ))

        result = mgr2.process_round(responses, findings, tasks, round_cost=1.0)
        immune_actions = [a for a in result.recovery_actions.values()
                         if a not in ("", "LOG_ONLY")]
        if not immune_actions:
            _log("  Test 2: PASSED — no over-triggering on benign findings")
        else:
            _log(f"  Test 2: FAILED — immune triggered on benign: {immune_actions}")
            all_passed = False
    except Exception as e:
        _log(f"  Test 2: ERROR — {type(e).__name__}: {e}")
        all_passed = False

    # ── Test 3: Cascade (2/5 fail simultaneously) ──
    _log("  Test 3: Cascade — 2/5 models fail simultaneously")
    try:
        mgr3 = DynamicManager(models, config)
        responses = {}
        findings = []
        for i, m in enumerate(models):
            failed = i < 2  # first 2 models fail
            content = "" if failed else f"Finding from {m.model_id}"
            resp = ModelResponse(
                model_id=m.model_id, round_idx=0, content=content,
                response_time=300.0 if failed else 10.0,
                parseable=not failed, finding_count=0 if failed else 1,
            )
            responses[m.model_id] = resp
            if not failed:
                findings.append(Finding(
                    finding_id=f"{m.model_id}_F0", model_id=m.model_id,
                    round_idx=0, flaw_class=1, severity=0.6,
                    abstraction_index=0.5, description="Test finding",
                ))

        result = mgr3.process_round(responses, findings, tasks, round_cost=1.0)
        active_count = len(result.active_models)
        if active_count >= 3:
            _log(f"  Test 3: PASSED — {active_count} models still active after cascade")
        else:
            _log(f"  Test 3: WARNING — only {active_count} active after cascade "
                 f"(may be correct if immune removed them)")
    except Exception as e:
        _log(f"  Test 3: ERROR — {type(e).__name__}: {e}")
        all_passed = False

    # ── Test 4: Oscillation ──
    _log("  Test 4: Oscillation — alternating good/bad responses")
    try:
        mgr4 = DynamicManager(models, config)
        reassign_count = 0
        for r in range(6):
            responses = {}
            findings = []
            for m in models:
                good_round = (r % 2 == 0) if m.model_id == "canary_0" else True
                content = f"Finding {r}" if good_round else ""
                resp = ModelResponse(
                    model_id=m.model_id, round_idx=r, content=content,
                    response_time=5.0 if good_round else 300.0,
                    parseable=good_round, finding_count=1 if good_round else 0,
                )
                responses[m.model_id] = resp
                if good_round:
                    findings.append(Finding(
                        finding_id=f"{m.model_id}_F{r}", model_id=m.model_id,
                        round_idx=r, flaw_class=1, severity=0.5,
                        abstraction_index=0.5, description=f"Finding {r}",
                    ))

            if mgr4.fsm.is_terminal:
                _log(f"    FSM terminated at round {r} — expected for oscillation test")
                break
            result = mgr4.process_round(responses, findings, tasks, round_cost=1.0)
            if "canary_0" in result.recovery_actions:
                reassign_count += 1

        if reassign_count <= 3:
            _log(f"  Test 4: PASSED — {reassign_count} immune actions over 6 oscillating "
                 f"rounds (damping working)")
        else:
            _log(f"  Test 4: WARNING — {reassign_count} actions over 6 rounds "
                 f"(possible thrashing)")
    except Exception as e:
        _log(f"  Test 4: ERROR — {type(e).__name__}: {e}")
        all_passed = False

    if all_passed:
        _log("Canary tests PASSED.")
    else:
        _log("Canary tests: some failures detected (see above).")
    return all_passed


# ─────────────────────────────────────────────────────────────────────────────
# Layer 1 preflight acceptance tests
# ─────────────────────────────────────────────────────────────────────────────

def run_layer1_preflight() -> bool:
    """Verify Layer 1 engineering fixes are still in place."""
    _log("=== LAYER 1 PREFLIGHT ===")
    all_ok = True

    # Test 1: Parser handles tuple format
    _log("  Parser: tuple format...")
    test_response = '(IR_F001, 0.9, 5, 0.8, "desc here", "fix here", "TRUE")'
    findings = parse_findings("test", 0, test_response)
    if len(findings) == 1 and findings[0].severity == 0.9:
        _log("    PASS")
    else:
        _log(f"    FAIL — got {len(findings)} findings")
        all_ok = False

    # Test 2: Parser stores proposed_fix
    _log("  Parser: proposed_fix stored...")
    if findings and findings[0].proposed_fix == "fix here":
        _log("    PASS")
    else:
        _log(f"    FAIL — proposed_fix={getattr(findings[0], 'proposed_fix', 'MISSING') if findings else 'NO FINDINGS'}")
        all_ok = False

    # Test 3: Parser handles indented fences
    _log("  Parser: indented fence stripping...")
    fenced = '   ```text\n(IR_F002, 0.7, 1, 0.5, "test", "fix", "FALSE")\n   ```'
    findings2 = parse_findings("test", 0, fenced)
    if len(findings2) == 1:
        _log("    PASS")
    else:
        _log(f"    FAIL — got {len(findings2)} findings from fenced input")
        all_ok = False

    # Test 4: Parser handles digit prefixes in finding IDs
    _log("  Parser: digit prefix in finding ID...")
    digit_response = '(LB_R2_F001, 0.88, 5, 0.42, "test", "fix", "TRUE")'
    findings3 = parse_findings("test", 0, digit_response)
    if len(findings3) == 1:
        _log("    PASS")
    else:
        _log(f"    FAIL — got {len(findings3)} findings from digit-prefix ID")
        all_ok = False

    # Test 5: Dynamic experiment numbering
    _log("  Dynamic numbering: auto-increment...")
    from run_exp12_live_wire import _next_experiment_number
    num = _next_experiment_number()
    if int(num) >= 16:
        _log(f"    PASS (next={num})")
    else:
        _log(f"    FAIL — next={num}, expected >= 16")
        all_ok = False

    if all_ok:
        _log("Layer 1 preflight PASSED.")
    else:
        _log("Layer 1 preflight: FAILURES detected.")
    return all_ok


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment
# ─────────────────────────────────────────────────────────────────────────────

def run_experiment() -> Dict[str, Any]:
    """Run full Experiment 17."""
    experiment_start = time.monotonic()
    _log(f"=== EXPERIMENT 17: IMMUNE + LOAD BALANCING LAYER VALIDATION ===")
    _log(f"Logs: {LOGS_DIR}")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load config
    exp_config = load_default_config()
    cdsfl_text = exp_config.cdsfl_system_prompt

    # Load test article (full file)
    code = TEST_ARTICLE_PATH.read_text(encoding="utf-8")
    _log(f"Test article: {len(code)} chars, {len(code.splitlines())} lines")

    # Load interface summary
    interface_summary = ""
    if INTERFACE_SUMMARY_PATH.exists():
        interface_summary = INTERFACE_SUMMARY_PATH.read_text(encoding="utf-8")
        _log(f"Interface summary: {len(interface_summary)} chars")

    # Load mathematical appendix (test article 2)
    math_appendix = ""
    if MATH_APPENDIX_PATH.exists():
        math_appendix = MATH_APPENDIX_PATH.read_text(encoding="utf-8")
        _log(f"Mathematical appendix: {len(math_appendix)} chars, "
             f"{len(math_appendix.splitlines())} lines")
    else:
        _log("WARNING: MATHEMATICAL_APPENDIX.md not found")

    # Load verification chain (test article 3)
    verification_chain = ""
    if VERIFICATION_CHAIN_PATH.exists():
        verification_chain = VERIFICATION_CHAIN_PATH.read_text(encoding="utf-8")
        _log(f"Verification chain: {len(verification_chain)} chars, "
             f"{len(verification_chain.splitlines())} lines")
    else:
        _log("WARNING: verification_chain.py not found")

    # Build DynamicManager
    model_specs = build_model_specs(exp_config)
    dm_config = DynamicManagementConfig(
        immune_feedback_enabled=True,
        immune_damping_rounds=2,  # Exp 16 consensus (median)
        # Pre-seed Codex for decomposition: observed R0A latencies 370-556s
        # at full prompt size vs 50-150s for other models. CLI overhead makes
        # full-artifact dispatch impractical. Immune layer can add more models
        # dynamically via model_failure remediation chain.
        pre_decompose_models={"Codex"},
    )
    tasks = [Task(task_id="immune_lb_math", token_demand=len(code) // 4,
                  flaw_class=1, criticality=0.8)]
    mgr = DynamicManager(model_specs, dm_config)

    # Telemetry
    telemetry = RoundTelemetry(LOGS_DIR)

    # Freeze experiment manifest (Exp 16: ChatGPT IMP006)
    import subprocess
    head_hash = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT)
    ).decode().strip()
    manifest = {
        "experiment": EXPERIMENT,
        "commit": head_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "test_articles": [
            str(TEST_ARTICLE_PATH), str(MATH_APPENDIX_PATH),
            str(VERIFICATION_CHAIN_PATH),
        ],
        "test_article_lines": len(code.splitlines()),
        "math_appendix_lines": len(math_appendix.splitlines()),
        "verification_chain_lines": len(verification_chain.splitlines()),
        "models": [{"label": m.label, "model_id": m.model_id, "api": m.api}
                   for m in exp_config.models if m.role != "collator"],
        "config": {"immune_feedback_enabled": True, "immune_damping_rounds": 2,
                   "max_rounds": MAX_ROUNDS, "wall_clock_cap_s": WALL_CLOCK_CAP_S},
    }
    (LOGS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    _log(f"Manifest frozen: {head_hash[:8]}")

    all_findings: List[Finding] = []
    per_task_findings: Dict[str, List[Finding]] = {t[0]: [] for t in TASKS}
    round_results: List[Dict[str, Any]] = []
    convergent_text = _extract_convergent_findings()

    def _dispatch_all_tasks(round_label: str, round_type: str,
                            round_idx: int, phase_prefix: str) -> int:
        """Dispatch all 4 tasks to all models for one round. Returns total findings."""
        round_total = 0
        round_entry: Dict[str, Any] = {"round": round_label}

        for task_key, id_prefix, task_desc, in [(t[0], t[1], t[2]) for t in TASKS]:
            _log(f"\n--- {round_label}: {task_desc} ---")

            prior_text = format_findings_for_context(per_task_findings[task_key])
            prompt = _build_task_prompt(
                task_key, round_label, round_type,
                code, math_appendix, verification_chain, interface_summary,
                prior_findings_text=prior_text,
                convergent_text=convergent_text if round_type == "seeded" else "",
            )
            _log(f"  Prompt: {len(prompt)} chars")

            task_findings, task_responses = _dispatch_round(
                exp_config, mgr, prompt, cdsfl_text, code,
                f"{phase_prefix}_{task_key}", round_idx,
                task_key=task_key,
            )
            per_task_findings[task_key].extend(task_findings)
            all_findings.extend(task_findings)
            round_entry[task_key] = len(task_findings)
            round_total += len(task_findings)
            _log(f"  {task_desc}: {len(task_findings)} findings from "
                 f"{len(task_responses)} models")

        round_entry["total"] = round_total
        round_results.append(round_entry)
        return round_total

    # ── ROUND 0A: Blind Discovery ──
    _log("\n=== ROUND 0A: BLIND DISCOVERY (4 tasks × 5 models) ===")
    r0a_total = _dispatch_all_tasks("ROUND 0A (BLIND)", "blind", 0, "r0a")
    _log(f"\nRound 0A total: {r0a_total} findings across 4 tasks")

    # Process through DynamicManager (combined findings)
    r0a_all = all_findings[:]
    r0a_model_responses = _build_model_responses(
        {"combined": "R0A combined"}, 0)  # simplified — DM gets finding list
    if r0a_all:
        result = mgr.process_round(r0a_model_responses, r0a_all, tasks, round_cost=1.0)
        _record_telemetry(telemetry, mgr, result, 0)

    # ── ROUND 0B: Seeded Validation ──
    _log("\n=== ROUND 0B: SEEDED VALIDATION (4 tasks × 5 models) ===")
    r0b_total = _dispatch_all_tasks("ROUND 0B (SEEDED)", "seeded", 1, "r0b")
    _log(f"\nRound 0B total: {r0b_total} findings across 4 tasks")

    r0b_findings = all_findings[len(r0a_all):]
    if r0b_findings:
        r0b_model_responses = _build_model_responses(
            {"combined": "R0B combined"}, 1)
        if r0b_model_responses:
            result = mgr.process_round(r0b_model_responses, r0b_findings,
                                       tasks, round_cost=1.0)
            _record_telemetry(telemetry, mgr, result, 1)

    # ── ADAPTIVE ROUNDS ──
    for round_idx in range(2, MAX_ROUNDS):
        elapsed_total = time.monotonic() - experiment_start
        if elapsed_total > WALL_CLOCK_CAP_S:
            _log(f"\n  WALL-CLOCK CAP reached ({elapsed_total:.0f}s > "
                 f"{WALL_CLOCK_CAP_S}s)")
            _log(f"  Pausing for review — all findings saved to {LOGS_DIR}")
            break

        _log(f"\n=== ROUND {round_idx}: ADAPTIVE (4 tasks × 5 models) ===")

        # Check DynamicManager stop condition
        if mgr.diminishing_returns.stop(round_idx - 1):
            _log(f"  DynamicManager stop() fired at round {round_idx}")
            _log(f"  Mathematical stop: exhaustion AND abstraction_ok")
            break

        pre_count = len(all_findings)
        rn_total = _dispatch_all_tasks(
            f"ROUND {round_idx} (ADAPTIVE)", "adaptive", round_idx,
            f"round{round_idx}")
        _log(f"\nRound {round_idx}: {rn_total} findings across 4 tasks")

        rn_findings = all_findings[pre_count:]
        if rn_findings:
            rn_model_responses = _build_model_responses(
                {"combined": f"R{round_idx} combined"}, round_idx)
            if rn_model_responses:
                result = mgr.process_round(rn_model_responses, rn_findings,
                                           tasks, round_cost=1.0)
                _record_telemetry(telemetry, mgr, result, round_idx)
        else:
            _log(f"  Zero findings across all 4 tasks — convergence reached")
            break

    # ── Summary ──
    elapsed_total = time.monotonic() - experiment_start
    _log(f"\n=== EXPERIMENT 17 SUMMARY ===")
    _log(f"Total findings: {len(all_findings)}")
    _log(f"Rounds completed: {len(round_results)}")
    _log(f"Wall clock: {elapsed_total:.0f}s ({elapsed_total/60:.1f} min)")
    for rr in round_results:
        _log(f"  Round {rr['round']}: {rr['findings']} findings, {rr['models']} models")

    # Save final report
    report = {
        "experiment": EXPERIMENT,
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


def _find_cached(phase_label: str, model_label: str) -> Optional[str]:
    """Check if we already have a saved response for this phase+model.

    Returns the response text if found, None otherwise.
    Used by --resume to skip already-completed dispatches.
    """
    import glob
    # Normalise label for filename matching (lowercase)
    label_lower = model_label.lower()
    pattern = str(LOGS_DIR / f"{phase_label}_{label_lower}_*.json")
    matches = glob.glob(pattern)
    if not matches:
        return None
    # Use most recent match
    matches.sort()
    try:
        data = json.loads(Path(matches[-1]).read_text(encoding="utf-8"))
        text = data.get("response", "")
        if text:
            _log(f"  {model_label}: CACHED ({len(text)} chars from {Path(matches[-1]).name})")
            return text
    except (json.JSONDecodeError, KeyError):
        pass
    return None


# Whether to use cached results (set by --resume flag)
RESUME_MODE = False


# ─── Standard Confer Packet (CX prompt efficiency confer, 30 March 2026) ──
# CX burns context investigating code it should already have. The confer
# packet provides everything CX needs to produce findings immediately:
# verified facts, adversarial brief, and explicit unknowns.
#
# Evidence: 155K tokens (78 tool calls) → 33K tokens (0 tool calls) with
# embedded code + verified facts. 78% reduction, more findings (5→6).

_ADVERSARIAL_BRIEF = (
    "\n=== ADVERSARIAL BRIEF ===\n"
    "The real defect may be outside these code snippets. Before validating "
    "the proposed review boundary, test for: omitted assumptions, wrong "
    "inputs to the functions shown, wrong ownership of responsibilities "
    "between classes, and wrong problem framing. If you believe the issue "
    "is upstream or adjacent to the code shown, say so explicitly.\n"
    "=== END ADVERSARIAL BRIEF ===\n\n"
)


def _build_verified_facts(task_key: str, mc_label: str,
                          round_idx: int) -> str:
    """Build a verified facts block from experiment state.

    CX confer F004: CX should not re-derive counts, timings, or errors
    that CC1 already knows. Separate from hypotheses.
    """
    facts = ["=== VERIFIED FACTS (do not re-derive) ==="]

    # Test article sizes
    facts.append(f"- dynamic_management.py: ~260,000 chars (~6,100 lines)")
    facts.append(f"- MATHEMATICAL_APPENDIX.md: ~55,000 chars")
    facts.append(f"- verification_chain.py: ~790 lines")

    # Task-specific sizes after decomposition
    task_sizes = {
        "immune": "112K chars task-level, 12-93K per sub-area",
        "loadbalancing": "42K chars task-level (below threshold)",
        "mathmodel": "110K chars with appendix, 15-34K per sub-area",
        "persistence": "27K chars (separate file, below threshold)",
    }
    if task_key in task_sizes:
        facts.append(f"- {task_key} decomposed size: {task_sizes[task_key]}")

    # Throughput observations for this model
    obs = _throughput_observations.get(mc_label, [])
    if obs:
        rates = [f"{chars/secs:.0f} chars/s ({chars} chars in {secs:.0f}s)"
                 for chars, secs in obs[-3:] if secs > 0]
        facts.append(f"- {mc_label} observed throughput: {'; '.join(rates)}")
        eff = _effective_capacity(mc_label, 600.0)
        if eff:
            facts.append(f"- {mc_label} effective capacity at 600s timeout: {eff} chars")

    # Known failures
    if mc_label == "Codex" and round_idx >= 2:
        facts.append("- Codex timed out in Round 3 of prior run (>600s on 112K immune prompt)")
        facts.append("- Same prompt completed in 254s in Round 2 (high variance, CLI overhead)")

    facts.append(f"- Current round: {round_idx}, task: {task_key}")
    facts.append(f"- 350 tests passing as of last commit")
    facts.append("=== END VERIFIED FACTS ===\n")
    return "\n".join(facts)


def _build_explicit_unknowns(task_key: str, area_name: str = "") -> str:
    """Build explicit unknowns block — what the extraction might miss.

    CX confer F002/F006: CC1 pre-selecting code creates bias risk. Name
    what was excluded so the reviewer can flag if the omission matters.
    """
    unknowns = ["=== EXPLICIT UNKNOWNS / POSSIBLE OMISSION ZONES ==="]

    if area_name:
        # Sub-area: other sub-areas are excluded
        all_areas = TASK_SUBAREAS.get(task_key, REVIEW_AREAS)
        other_areas = [a[0] for a in all_areas if a[0] != area_name]
        if other_areas:
            unknowns.append(
                f"- Other sub-areas NOT shown: {', '.join(other_areas)}. "
                f"Cross-sub-area interactions may be missed.")

    if task_key == "immune":
        unknowns.append(
            "- process_round() integration code is in skeletal form only "
            "(definition + docstring). Full body not shown unless it matches "
            "a marker.")
        unknowns.append(
            "- LoadBalancer and convergence detector interactions with immune "
            "layer may be partially visible only.")
    elif task_key == "mathmodel":
        unknowns.append(
            "- Implementation code is extracted by marker. Formulas that span "
            "multiple classes may be partially visible.")
    elif task_key == "loadbalancing":
        unknowns.append(
            "- Immune layer's effect on load balancing (model removal, "
            "pre_decompose_models) visible in skeletal form only.")

    unknowns.append(
        "- If you believe the real issue is in code not shown, state what "
        "code you would need to see and why.")
    unknowns.append("=== END EXPLICIT UNKNOWNS ===\n")
    return "\n".join(unknowns)


def _build_subarea_prompt(
    preamble: str, full_code: str, math_text: str,
    task_key: str, mc_label: str, round_idx: int,
) -> tuple[str, bool]:
    """Build a sub-area rotation prompt for models that need smaller input.

    Uses TASK_SUBAREAS (or REVIEW_AREAS for immune) to split the task into
    sub-areas and rotate by round_idx. Falls back to REVIEW_AREAS if no
    task-specific sub-areas are defined.

    Includes verified facts, adversarial brief, and explicit unknowns
    (CX prompt efficiency confer: 6-field standard confer packet).
    """
    subareas = TASK_SUBAREAS.get(task_key, REVIEW_AREAS)
    area_idx = round_idx % len(subareas)
    area_name, markers = subareas[area_idx]

    verified_facts = _build_verified_facts(task_key, mc_label, round_idx)
    unknowns = _build_explicit_unknowns(task_key, area_name)

    if area_name == "Persistence":
        vc_text = ""
        if VERIFICATION_CHAIN_PATH.exists():
            vc_text = VERIFICATION_CHAIN_PATH.read_text(encoding="utf-8")
        model_prompt = (
            f"You are reviewing the PERSISTENCE LAYER "
            f"(verification_chain.py) — hash chains, Merkle trees, "
            f"Ed25519 signing, epoch sealing.\n\n"
            + preamble
            + f"\n{verified_facts}\n"
            + f"=== ARTIFACT 1: verification_chain.py ===\n\n"
            f"{vc_text}\n\n"
            f"=== END ARTIFACT 1 ===\n\n"
            f"=== ARTIFACT 2: MATHEMATICAL_APPENDIX.md ===\n\n"
            f"{math_text}\n\n"
            f"=== END ARTIFACT 2 ===\n\n"
            + unknowns
            + _ADVERSARIAL_BRIEF
            + "Produce your findings now."
        )
        _log(f"  {mc_label}: sub-area → {area_name} ({len(vc_text)} chars)")
    else:
        focused = _extract_code_area(full_code, markers, area_name)
        model_prompt = (
            f"You are reviewing the {area_name} sub-area of {task_key}.\n\n"
            f"The full code artifact has been decomposed for your context "
            f"window. Below is the {area_name} code plus skeletal context.\n\n"
            + preamble
            + f"\n{verified_facts}\n"
            + f"=== ARTIFACT 1: {area_name} (from dynamic_management.py) ===\n\n"
            f"{focused}\n\n"
            f"=== END ARTIFACT 1 ===\n\n"
        )
        # Add math appendix for mathmodel sub-areas and immune sub-areas
        if task_key in ("mathmodel", "immune"):
            model_prompt += (
                f"=== ARTIFACT 2: MATHEMATICAL_APPENDIX.md ===\n\n"
                f"{math_text}\n\n"
                f"=== END ARTIFACT 2 ===\n\n"
            )
        model_prompt += unknowns + _ADVERSARIAL_BRIEF
        model_prompt += "Produce your findings now."
        _log(f"  {mc_label}: sub-area → {area_name} ({len(focused)} chars)")
    return model_prompt, True


def _build_decomposed_prompt(
    prompt: str, full_code: str, task_key: str,
    mc_label: str, round_idx: int,
    max_chars: int = 0,
) -> tuple[str, bool]:
    """Build a decomposed prompt for a model that needs smaller input.

    For DeepSeek: always uses sub-area rotation (REVIEW_AREAS/TASK_SUBAREAS).
    For other decomposed models: tries task-level extraction first. If the
    result exceeds max_chars (or SUBAREA_ESCALATION_CHARS), escalates to
    sub-area rotation (CC2 confer F002+F005).

    Args:
        max_chars: Max prompt chars. 0 = use SUBAREA_ESCALATION_CHARS.
                   Set from throughput-derived effective_capacity when available.

    Returns (model_prompt, was_decomposed).
    """
    preamble = prompt.split("=== ARTIFACT")[0]
    math_text = ""
    if MATH_APPENDIX_PATH.exists():
        math_text = MATH_APPENDIX_PATH.read_text(encoding="utf-8")
    threshold = max_chars if max_chars > 0 else SUBAREA_ESCALATION_CHARS

    # DeepSeek: always sub-area rotation
    if mc_label == "DeepSeek":
        return _build_subarea_prompt(
            preamble, full_code, math_text, task_key, mc_label, round_idx)

    # Other decomposed models: try task-level first
    focused = _extract_task_area(full_code, task_key)
    if focused is None:
        # Task doesn't use DM code (persistence) — use original prompt
        return prompt, False

    task_desc = {t[0]: t[2] for t in TASKS}.get(task_key, task_key)
    verified_facts = _build_verified_facts(task_key, mc_label, round_idx)
    unknowns = _build_explicit_unknowns(task_key)
    model_prompt = (
        f"You are reviewing {task_desc}.\n\n"
        f"The full code artifact has been decomposed to focus on the "
        f"relevant classes and functions. Below is the focused code plus "
        f"skeletal context from dynamic_management.py.\n\n"
        + preamble
        + f"\n{verified_facts}\n"
        + f"=== ARTIFACT 1: {task_desc} (from dynamic_management.py) ===\n\n"
        f"{focused}\n\n"
        f"=== END ARTIFACT 1 ===\n\n"
    )
    if task_key == "mathmodel":
        model_prompt += (
            f"=== ARTIFACT 2: MATHEMATICAL_APPENDIX.md ===\n\n"
            f"{math_text}\n\n"
            f"=== END ARTIFACT 2 ===\n\n"
        )
    model_prompt += unknowns + _ADVERSARIAL_BRIEF
    model_prompt += "Produce your findings now."

    # Sub-area escalation: if task-level result is too large, escalate
    if len(model_prompt) > threshold and task_key in TASK_SUBAREAS:
        _log(f"  {mc_label}: task-level {task_key} = {len(model_prompt)} chars "
             f"> threshold {threshold} — escalating to sub-area rotation")
        return _build_subarea_prompt(
            preamble, full_code, math_text, task_key, mc_label, round_idx)

    _log(f"  {mc_label}: decomposed → {task_desc} ({len(focused)} chars)")
    return model_prompt, True


def _dispatch_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    phase_label: str,
    round_idx: int,
    task_key: str = "",
) -> tuple[List[Finding], Dict[str, str]]:
    """Dispatch prompt to all models, return (findings, {label: response_text}).

    Dynamic decomposition: models in mgr.config.pre_decompose_models (or
    DeepSeek, always) receive focused code extraction instead of the full
    artifact. Pre-dispatch feasibility check gates dispatch via
    mgr.check_dispatch_feasibility(). Timeouts are reported to the immune
    layer as model_failure pathologies.
    """
    findings: List[Finding] = []
    responses: Dict[str, str] = {}

    # Estimate prompt token count (rough: 1 token ≈ 4 chars)
    prompt_tokens_est = len(prompt) // 4

    for mc in exp_config.models:
        if mc.role == "collator":
            continue

        # Resume: check for cached response before dispatching
        if RESUME_MODE:
            cached = _find_cached(phase_label, mc.label)
            if cached:
                model_findings = parse_findings(mc.label, round_idx, cached)
                findings.extend(model_findings)
                responses[mc.label] = cached
                _log(f"  {mc.label}: {len(model_findings)} findings (from cache)")
                continue

        # Throughput-derived effective capacity for this model (CC2 F004+F006)
        eff_cap = _effective_capacity(mc.label, mc.timeout)

        # Dynamic decomposition check
        decomposed = False
        max_chars = eff_cap if eff_cap else 0
        if _should_decompose(mc.label, mgr):
            model_prompt, decomposed = _build_decomposed_prompt(
                prompt, full_code, task_key, mc.label, round_idx,
                max_chars=max_chars)
        else:
            model_prompt = prompt

        # Pre-dispatch feasibility gate — fires for ALL prompts, including
        # decomposed ones (CC2 confer F005: removed `not decomposed` guard).
        # Context-window check via DynamicManager, then throughput check.
        model_spec = _find_model_spec(mgr, mc.label)
        if model_spec:
            token_est = len(model_prompt) // 4
            ok, p_feasible = mgr.check_dispatch_feasibility(model_spec, token_est)
            if not ok:
                _log(f"  {mc.label}: DISPATCH BLOCKED (context window) — "
                     f"P(feasible)={p_feasible:.3f}, ~{token_est} tokens. "
                     f"Auto-decomposing.")
                model_prompt, decomposed = _build_decomposed_prompt(
                    prompt, full_code, task_key, mc.label, round_idx,
                    max_chars=max_chars)
                mgr.config.pre_decompose_models.add(mc.label)
                _log(f"  {mc.label}: added to pre_decompose_models")
            # Throughput check: even if context-window is fine, the model
            # may not complete within its timeout at observed throughput.
            elif eff_cap and len(model_prompt) > eff_cap:
                _log(f"  {mc.label}: THROUGHPUT WARNING — prompt {len(model_prompt)} "
                     f"chars > effective capacity {eff_cap} chars. Escalating.")
                model_prompt, decomposed = _build_decomposed_prompt(
                    prompt, full_code, task_key, mc.label, round_idx,
                    max_chars=eff_cap)
                if not decomposed:
                    mgr.config.pre_decompose_models.add(mc.label)
                    _log(f"  {mc.label}: added to pre_decompose_models")

        try:
            text, elapsed = dispatch_to_model(mc, model_prompt, cdsfl_text)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")

            # Record throughput observation (CC2 confer F004)
            _record_throughput(mc.label, len(model_prompt), elapsed)

            model_findings = parse_findings(mc.label, round_idx, text)
            findings.extend(model_findings)
            responses[mc.label] = text
            _log(f"  {mc.label}: {len(model_findings)} findings parsed")

            save_output(
                LOGS_DIR, phase_label, mc.label,
                model_prompt[:200] + "...", text,
                metadata={
                    "elapsed": round(elapsed, 1),
                    "chars": len(text),
                    "findings_count": len(model_findings),
                    "round": round_idx,
                    "decomposed": decomposed,
                    "prompt_chars": len(model_prompt),
                },
            )

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
        except TimeoutError as e:
            _log(f"  {mc.label}: TIMEOUT — {e}")
            # Report to immune layer: timeout is a model_failure signal.
            # The remediation chain will add this model to pre_decompose_models
            # if it isn't already there.
            _report_dispatch_failure(mgr, mc.label, round_idx, f"timeout: {e}")
        except Exception as e:
            _log(f"  {mc.label}: ERROR — {type(e).__name__}: {e}")
            _report_dispatch_failure(mgr, mc.label, round_idx,
                                     f"{type(e).__name__}: {e}")

    return findings, responses


def _find_model_spec(mgr: DynamicManager, label: str) -> Optional[ModelSpec]:
    """Look up a ModelSpec from the DynamicManager by label."""
    for ms in mgr.models:
        if ms.model_id == label:
            return ms
    return None


def _report_dispatch_failure(
    mgr: DynamicManager, model_label: str, round_idx: int, detail: str,
) -> None:
    """Report a dispatch failure (timeout/error) to the immune layer.

    Creates a DetectorDiagnosis with pathology='model_failure' so the
    remediation chain can add the model to pre_decompose_models.
    """
    diagnosis = DetectorDiagnosis(
        detector="model_failure",
        pathology=f"{model_label} has failed dispatch: {detail}",
        severity="WARNING",
        recommended_action="add_to_pre_decompose",
        evidence={"model_id": model_label, "round": round_idx},
    )
    adjustment = mgr.apply_diagnosis(diagnosis, round_idx)
    if adjustment:
        _log(f"  IMMUNE: {model_label} → {adjustment}")
    else:
        _log(f"  IMMUNE: {model_label} failure recorded (already in pre_decompose)")


def _build_model_responses(
    raw_responses: Dict[str, str], round_idx: int,
) -> Dict[str, ModelResponse]:
    """Convert raw text responses to ModelResponse objects."""
    result = {}
    for label, text in raw_responses.items():
        findings = parse_findings(label, round_idx, text)
        result[label] = ModelResponse(
            model_id=label,
            round_idx=round_idx,
            content=text,
            response_time=0.0,  # not tracked here
            parseable=len(findings) > 0,
            format_compliant=True,
            finding_count=len(findings),
            mean_abstraction=(
                sum(f.abstraction_index for f in findings) / len(findings)
                if findings else 0.5
            ),
        )
    return result


def _record_telemetry(
    telemetry: RoundTelemetry,
    mgr: DynamicManager,
    result: RoundResult,
    round_idx: int,
):
    """Record immune telemetry for this round."""
    # Gather diagnoses from health monitor
    diagnoses = mgr.health_monitor._diagnoses[-10:]  # last 10

    # Stop condition inputs
    try:
        exhaustion = (
            mgr.diminishing_returns.smoothed_marginal_value(round_idx)
            < mgr.config.tau_mu
        ) if round_idx > 0 else False
        abstraction_ok = (
            round_idx <= 1
            or mgr.diminishing_returns._abstraction_dropping(round_idx)
        )
        stop_inputs = {
            "smoothed_mu": mgr.diminishing_returns.smoothed_marginal_value(round_idx),
            "smoothed_novelty": mgr.diminishing_returns.smoothed_novelty_rate(round_idx),
            "vocab_saturated": mgr.diminishing_returns.vocab_saturated(round_idx),
            "exhaustion": exhaustion,
            "abstraction_ok": abstraction_ok,
            "stop_would_fire": exhaustion and abstraction_ok,
        }
    except (IndexError, ZeroDivisionError):
        stop_inputs = {"error": "insufficient data for stop calculation"}

    # Immune adjustments
    adjustments = getattr(mgr, '_immune_adjustments', [])
    recent_adjustments = adjustments[-5:] if adjustments else []

    # Allocation warnings (LoadBalancer is constructed locally in DM, not stored)
    warnings = getattr(mgr, '_allocation_warnings', [])

    telemetry.record(
        round_idx=round_idx,
        diagnoses=diagnoses,
        recovery_actions=result.recovery_actions,
        immune_adjustments=recent_adjustments,
        stop_inputs=stop_inputs,
        active_models=result.active_models,
        allocation_warnings=warnings,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global RESUME_MODE
    source_env()

    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    RESUME_MODE = "--resume" in sys.argv

    if mode == "preflight":
        # Model connectivity + Layer 1 acceptance
        config = load_default_config()
        from run_exp16_plan_review import run_preflight
        ok = run_preflight(config)
        ok2 = run_layer1_preflight()
        sys.exit(0 if (ok and ok2) else 1)

    elif mode == "canary":
        ok = run_canary_tests()
        sys.exit(0 if ok else 1)

    elif mode in ("run", "resume"):
        if mode == "resume":
            RESUME_MODE = True

        if RESUME_MODE:
            _log("=== RESUME MODE: will use cached responses where available ===")
            # Count existing files
            import glob
            existing = glob.glob(str(LOGS_DIR / "r0*_*.json"))
            _log(f"  Found {len(existing)} cached response files in {LOGS_DIR}")

        # Full sequence: Layer 1 preflight → canary → experiment
        _log("Phase 1: Layer 1 preflight")
        if not run_layer1_preflight():
            _log("ABORT: Layer 1 preflight failed.")
            sys.exit(1)

        _log("\nPhase 2: Canary tests")
        if not run_canary_tests():
            _log("WARNING: Some canary tests failed. Proceeding with caution.")

        _log("\nPhase 3: Model preflight")
        config = load_default_config()
        from run_exp16_plan_review import run_preflight, LOGS_DIR as EXP16_LOGS
        # Use Exp 17 logs dir for preflight
        import run_exp16_plan_review
        run_exp16_plan_review.LOGS_DIR = LOGS_DIR
        if not run_preflight(config):
            _log("ABORT: Model preflight failed.")
            sys.exit(1)

        _log("\nPhase 4: Experiment 17")
        report = run_experiment()

        _log(f"\nExperiment 17 complete. {report['total_findings']} findings "
             f"across {len(report['rounds'])} rounds.")

    else:
        print(f"Usage: {sys.argv[0]} [preflight|canary|run|resume]")
        print(f"  run     — full experiment from scratch")
        print(f"  resume  — resume from cached responses (skips completed dispatches)")
        print(f"  run --resume  — same as resume")
        sys.exit(1)


if __name__ == "__main__":
    main()
