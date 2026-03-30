#!/usr/bin/env python3
"""Experiment 17: Immune Response Layer Validation.

Executes the APPROVED Experiment 17 plan (reviewed by 5 models in Exp 16).
Full `dynamic_management.py` as test article, analytical boundary = immune subsystem.

Key design decisions from Experiment 16 convergence:
- Full file delivery (not extracted lines) — unanimous
- Split Round 0: R0A blind + R0B seeded validation — 4/5
- Independent stop caps: round 10 + wall-clock 4h — 3/5
- Behaviour-based success criteria — 4/5
- DeepSeek decomposition into 3 immune sub-areas — unanimous
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

# DeepSeek immune sub-area decomposition (Exp 16: unanimous)
IMMUNE_AREAS = [
    ("Detection", ["DetectorDiagnosis", "DetectorHealthMonitor"]),
    ("Response", ["FailureHandler"]),
    ("Integration", ["process_round", "apply_diagnosis", "_apply_transform",
                      "_REMEDIATION_CHAINS", "immune_feedback_enabled"]),
]

# Convergent findings for R0B seeded validation
CONVERGENT_FINDINGS_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_plan.md"

# Reference documents for model context
INTERFACE_SUMMARY_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_interface_summary.md"
TRACEABILITY_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_traceability.md"
TEST_ARTICLE_PATH = REPO_ROOT / "bench" / "dynamic_management.py"


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
                {"pathology": d.pathology, "severity": d.severity,
                 "detail": d.detail, "recommended_action": d.recommended_action}
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
# DeepSeek immune decomposition
# ─────────────────────────────────────────────────────────────────────────────

def _extract_immune_area(code: str, area_idx: int) -> tuple[str, str]:
    """Extract one immune sub-area's code + skeletal context.

    Areas: Detection (DetectorDiagnosis + DetectorHealthMonitor),
    Response (FailureHandler), Integration (process_round + apply_diagnosis).
    """
    area_name, markers = IMMUNE_AREAS[area_idx % len(IMMUNE_AREAS)]
    lines = code.split("\n")

    # Find all class/function boundaries
    boundaries = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^class \w+', stripped) or re.match(r'^    def \w+', stripped):
            boundaries.append((i, stripped))

    target_lines = set()
    context_lines = set()

    for start_idx, defn in boundaries:
        # Find end of this block
        end_idx = len(lines)
        for next_start, _ in boundaries:
            if next_start > start_idx:
                end_idx = next_start
                break

        is_target = any(marker in defn for marker in markers)
        if is_target:
            for j in range(start_idx, end_idx):
                target_lines.add(j)
        else:
            # Skeletal: definition + docstring only
            context_lines.add(start_idx)
            if start_idx + 1 < end_idx and '"""' in lines[start_idx + 1]:
                context_lines.add(start_idx + 1)

    # Module-level config (first 200 lines)
    for j in range(min(200, len(lines))):
        context_lines.add(j)

    all_lines = target_lines | context_lines
    focused = "\n".join(lines[j] for j in sorted(all_lines))
    return focused, area_name


# ─────────────────────────────────────────────────────────────────────────────
# Prompts
# ─────────────────────────────────────────────────────────────────────────────

def build_r0a_prompt(code: str, interface_summary: str) -> str:
    """Round 0A: blind discovery. No prior findings."""
    return (
        "You are in ROUND 0A (BLIND DISCOVERY) of Experiment 17: Immune Response "
        "Layer Validation.\n\n"
        "You are operating UNDER CDSFL (your system prompt). Apply P-pass to the "
        "immune subsystem code below.\n\n"
        "## Analytical Boundary\n"
        "Focus on the IMMUNE RESPONSE LAYER: DetectorDiagnosis, DetectorHealthMonitor, "
        "FailureHandler, _REMEDIATION_CHAINS, process_round() immune integration, "
        "apply_diagnosis(), _apply_transform(), and immune config parameters.\n"
        "The rest of the file is context — review interfaces but do not produce "
        "findings about non-immune components unless they affect immune behaviour.\n\n"
        "## Interface Summary\n"
        f"{interface_summary}\n\n"
        "## Output Format\n"
        "For each finding:\n"
        "  FINDING_ID: F001 (etc.)\n"
        "  SEVERITY: 0.0–1.0\n"
        "  FLAW_CLASS: 1=logic, 2=interface, 3=notation, 4=completeness, "
        "5=correctness, 6=edge-case, 7=performance, 8=documentation\n"
        "  ABSTRACTION_INDEX: 0.0–1.0 (0=surface, 1=architectural)\n"
        "  DESCRIPTION: what is wrong and why\n"
        "  PROPOSED_FIX: specific fix\n"
        "  VERIFIED: TRUE/FALSE\n\n"
        "This is a BLIND round. Find everything you can. No prior findings are "
        "provided — your independent perspective is the point.\n\n"
        "=== ARTIFACT: dynamic_management.py ===\n\n"
        f"{code}\n\n"
        "=== END ARTIFACT ===\n\n"
        "Produce your findings now."
    )


def build_r0b_prompt(code: str, r0a_findings_text: str,
                     convergent_findings_text: str) -> str:
    """Round 0B: seeded validation with convergent findings from Exp 15."""
    return (
        "You are in ROUND 0B (SEEDED VALIDATION) of Experiment 17.\n\n"
        "In Round 0A, the following findings were produced independently:\n\n"
        f"{r0a_findings_text}\n\n"
        "Additionally, Experiment 15 produced 6 CONVERGENT FINDINGS (independently "
        "identified by 2+ models). 4 were fixed, 2 confirmed no-fix-needed:\n\n"
        f"{convergent_findings_text}\n\n"
        "Your task:\n"
        "1. VALIDATE the 4 applied fixes — are they correct? Do they fully resolve "
        "   the issues?\n"
        "2. CHALLENGE the 2 no-fix-needed decisions — is the rationale sound?\n"
        "3. IDENTIFY what Round 0A missed that the convergent findings caught, "
        "   and vice versa.\n"
        "4. Find any REMAINING issues not covered by either set.\n\n"
        "Use the same structured format (FINDING_ID, SEVERITY, etc.).\n\n"
        "=== ARTIFACT: dynamic_management.py ===\n\n"
        f"{code}\n\n"
        "=== END ARTIFACT ===\n\n"
        "Produce your findings now."
    )


def build_adaptive_prompt(code: str, round_idx: int,
                          prior_findings_text: str) -> str:
    """Adaptive round prompt."""
    return (
        f"You are in ROUND {round_idx} of Experiment 17 (adaptive round).\n\n"
        f"Prior findings from all rounds:\n\n{prior_findings_text}\n\n"
        f"Focus on the IMMUNE RESPONSE LAYER (DetectorDiagnosis, "
        f"DetectorHealthMonitor, FailureHandler, apply_diagnosis, process_round "
        f"immune integration).\n\n"
        f"Find what was MISSED. Do not repeat known findings. Focus on:\n"
        f"- Flaws prior rounds did not catch\n"
        f"- Deeper analysis of superficially noted issues\n"
        f"- Cross-cutting concerns with other subsystems\n"
        f"- Edge cases in immune behaviour\n\n"
        f"Use the structured format (FINDING_ID, SEVERITY, etc.).\n"
        f"If you find nothing new, state that explicitly.\n\n"
        f"=== ARTIFACT: dynamic_management.py ===\n\n"
        f"{code}\n\n"
        f"=== END ARTIFACT ===\n\n"
        f"Produce your findings now."
    )


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
    _log(f"=== EXPERIMENT 17: IMMUNE RESPONSE LAYER VALIDATION ===")
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

    # Build DynamicManager
    model_specs = build_model_specs(exp_config)
    dm_config = DynamicManagementConfig(
        immune_feedback_enabled=True,
        immune_damping_rounds=2,  # Exp 16 consensus (median)
    )
    tasks = [Task(task_id="immune_layer", token_demand=len(code) // 4,
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
        "test_article": str(TEST_ARTICLE_PATH),
        "test_article_lines": len(code.splitlines()),
        "models": [{"label": m.label, "model_id": m.model_id, "api": m.api}
                   for m in exp_config.models if m.role != "collator"],
        "config": {"immune_feedback_enabled": True, "immune_damping_rounds": 2,
                   "max_rounds": MAX_ROUNDS, "wall_clock_cap_s": WALL_CLOCK_CAP_S},
    }
    (LOGS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    _log(f"Manifest frozen: {head_hash[:8]}")

    all_findings: List[Finding] = []
    round_results: List[Dict[str, Any]] = []

    # ── ROUND 0A: Blind Discovery ──
    _log("\n=== ROUND 0A: BLIND DISCOVERY ===")
    r0a_prompt = build_r0a_prompt(code, interface_summary)
    _log(f"Prompt: {len(r0a_prompt)} chars")

    r0a_findings, r0a_responses = _dispatch_round(
        exp_config, mgr, r0a_prompt, cdsfl_text, code, "r0a", 0,
    )
    all_findings.extend(r0a_findings)
    round_results.append({
        "round": "0A", "findings": len(r0a_findings),
        "models": len(r0a_responses),
    })
    _log(f"Round 0A: {len(r0a_findings)} findings from {len(r0a_responses)} models")

    # Process through DynamicManager
    r0a_model_responses = _build_model_responses(r0a_responses, 0)
    if r0a_model_responses:
        result = mgr.process_round(r0a_model_responses, r0a_findings, tasks, round_cost=1.0)
        _record_telemetry(telemetry, mgr, result, 0)

    # ── ROUND 0B: Seeded Validation ──
    _log("\n=== ROUND 0B: SEEDED VALIDATION ===")
    r0a_text = format_findings_for_context(r0a_findings)
    convergent_text = _extract_convergent_findings()
    r0b_prompt = build_r0b_prompt(code, r0a_text, convergent_text)
    _log(f"Prompt: {len(r0b_prompt)} chars")

    r0b_findings, r0b_responses = _dispatch_round(
        exp_config, mgr, r0b_prompt, cdsfl_text, code, "r0b", 1,
    )
    all_findings.extend(r0b_findings)
    round_results.append({
        "round": "0B", "findings": len(r0b_findings),
        "models": len(r0b_responses),
    })
    _log(f"Round 0B: {len(r0b_findings)} findings from {len(r0b_responses)} models")

    if r0b_findings:
        r0b_model_responses = _build_model_responses(r0b_responses, 1)
        if r0b_model_responses:
            result = mgr.process_round(r0b_model_responses, r0b_findings, tasks, round_cost=1.0)
            _record_telemetry(telemetry, mgr, result, 1)

    # ── ADAPTIVE ROUNDS ──
    for round_idx in range(2, MAX_ROUNDS):
        elapsed_total = time.monotonic() - experiment_start
        if elapsed_total > WALL_CLOCK_CAP_S:
            _log(f"\n  WALL-CLOCK CAP reached ({elapsed_total:.0f}s > {WALL_CLOCK_CAP_S}s)")
            break

        _log(f"\n=== ROUND {round_idx}: ADAPTIVE ===")

        # Check DynamicManager stop condition
        if mgr.diminishing_returns.stop(round_idx - 1):
            _log(f"  DynamicManager stop() fired at round {round_idx}")
            _log(f"  Reason: exhaustion={True}, abstraction_ok="
                 f"{mgr.diminishing_returns._abstraction_dropping(round_idx - 1)}")
            break

        prior_text = format_findings_for_context(all_findings)
        adaptive_prompt = build_adaptive_prompt(code, round_idx, prior_text)
        _log(f"Prompt: {len(adaptive_prompt)} chars")

        rn_findings, rn_responses = _dispatch_round(
            exp_config, mgr, adaptive_prompt, cdsfl_text, code,
            f"round{round_idx}", round_idx,
        )
        all_findings.extend(rn_findings)
        round_results.append({
            "round": round_idx, "findings": len(rn_findings),
            "models": len(rn_responses),
        })
        _log(f"Round {round_idx}: {len(rn_findings)} findings from {len(rn_responses)} models")

        if rn_findings:
            rn_model_responses = _build_model_responses(rn_responses, round_idx)
            if rn_model_responses:
                result = mgr.process_round(rn_model_responses, rn_findings, tasks, round_cost=1.0)
                _record_telemetry(telemetry, mgr, result, round_idx)
        else:
            _log(f"  No findings in round {round_idx} — checking if stop")
            # No findings = likely convergence
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


def _dispatch_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    phase_label: str,
    round_idx: int,
) -> tuple[List[Finding], Dict[str, str]]:
    """Dispatch prompt to all models, return (findings, {label: response_text})."""
    findings: List[Finding] = []
    responses: Dict[str, str] = {}

    for mc in exp_config.models:
        if mc.role == "collator":
            continue

        # DeepSeek decomposition
        if mc.label == "DeepSeek":
            area_idx = round_idx % len(IMMUNE_AREAS)
            focused, area_name = _extract_immune_area(full_code, area_idx)
            model_prompt = (
                f"You are reviewing the IMMUNE SUBSYSTEM, specifically the "
                f"{area_name} sub-area.\n\n"
                f"The full artifact has been decomposed for your context window. "
                f"Below is the {area_name} code plus skeletal context.\n\n"
                + prompt.split("=== ARTIFACT")[0]  # Take the preamble
                + f"=== ARTIFACT: {area_name} ===\n\n"
                f"{focused}\n\n"
                f"=== END ARTIFACT ===\n\n"
                f"Produce your findings now."
            )
            _log(f"  DeepSeek: decomposed → {area_name} ({len(focused)} chars)")
        else:
            model_prompt = prompt

        try:
            text, elapsed = dispatch_to_model(mc, model_prompt, cdsfl_text)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")

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
                    "decomposed": mc.label == "DeepSeek",
                },
            )

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
        except TimeoutError as e:
            _log(f"  {mc.label}: TIMEOUT — {e}")
        except Exception as e:
            _log(f"  {mc.label}: ERROR — {type(e).__name__}: {e}")

    return findings, responses


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

    # Allocation warnings
    warnings = getattr(mgr.load_balancer, '_allocation_warnings', [])

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
    source_env()

    mode = sys.argv[1] if len(sys.argv) > 1 else "run"

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

    elif mode == "run":
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
        print(f"Usage: {sys.argv[0]} [preflight|canary|run]")
        sys.exit(1)


if __name__ == "__main__":
    main()
