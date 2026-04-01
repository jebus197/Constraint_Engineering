#!/usr/bin/env python3
"""Experiment 12: Live Wire Test — Dynamic Management Layer Validation.

First live test of the DynamicManager under real distributed compute.
CC1 is collator. DynamicManager makes all allocation, convergence, and
stop decisions. CC1 executes them via the API layer.

Usage:
    python3 bench/run_exp12_live_wire.py [preflight|blind|full]

    preflight  — verify all models respond correctly
    blind      — run blind round only (Phase 1)
    full       — run full experiment (blind + adaptive rounds until terminal)
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    Role,
)

# ─────────────────────────────────────────────────────────────────────────────
# Canonical imports from runner_core
# All shared infrastructure lives in runner_core.py. This module re-exports
# for backward compatibility — existing scripts importing from here continue
# to work, but new scripts should import from runner_core directly.
# ─────────────────────────────────────────────────────────────────────────────
from runner_core import (  # noqa: F401
    parse_findings,
    dispatch_to_model,
    format_findings_for_context,
    source_env,
    build_model_specs,
    build_task_prompt,
    next_experiment_number as _next_experiment_number,
    INITIAL_FINGERPRINTS,
    MODEL_SPECS,
    CONVERGENCE_EXCLUDED_MODELS,
    DECOMPOSITION_CONTEXT_THRESHOLD,
    _dispatch_worker,
)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULT_EXPERIMENT = "auto"  # "auto" = next available number
LOGS_DIR = REPO_ROOT / "bench" / "logs" / "experiment_12"  # reset by _set_experiment()


def _set_experiment(label: str) -> None:
    """Set the experiment label, updating LOGS_DIR and related paths.

    If label is "auto", auto-increments from existing experiment directories.
    Uses exist_ok=False on mkdir to catch races (CX finding 6).
    """
    global LOGS_DIR, CHECKPOINT_PATH, _EXPERIMENT_LABEL
    if label == "auto":
        label = _next_experiment_number()
        _log(f"Auto-assigned experiment number: {label}")
    _EXPERIMENT_LABEL = label
    LOGS_DIR = REPO_ROOT / "bench" / "logs" / f"experiment_{label}"
    CHECKPOINT_PATH = LOGS_DIR / "checkpoint.json"


_EXPERIMENT_LABEL = _DEFAULT_EXPERIMENT

def run_blind_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
) -> tuple[Dict[str, ModelResponse], List[Finding]]:
    """Phase 1: Blind round — same prompt to all feasible models.

    Returns (responses_dict, all_findings).
    """
    _log("=== PHASE 1: BLIND ROUND ===")
    responses: Dict[str, ModelResponse] = {}
    all_findings: List[Finding] = []

    for mc in exp_config.models:
        if mc.role == "collator":
            continue

        # Pre-dispatch feasibility check
        model_spec = next(
            (m for m in mgr.models if m.model_id == mc.label), None
        )
        if model_spec is None:
            _log(f"  {mc.label}: not in manager pool, skipping")
            continue

        prompt_tokens = len(prompt) // 4  # rough estimate
        feasible, p_feasible = mgr.check_dispatch_feasibility(model_spec, prompt_tokens)
        _log(f"  {mc.label}: feasibility P={p_feasible:.3f}, dispatch={'YES' if feasible else 'BLOCKED'}")

        if not feasible:
            # Check if this model should be pre-decomposed instead of blocked.
            # DeepSeek (threshold=0) can never fit the full artifact but works
            # fine with decomposed dispatch — blocking it is a false positive.
            threshold = DECOMPOSITION_CONTEXT_THRESHOLD.get(mc.label, 100000)
            if threshold == 0 or len(prompt) > threshold:
                area_idx = 0  # Blind round: start with Area 1
                focused_code, area_label = _extract_area_code(prompt, area_idx)
                decomposed_prompt = (
                    f"You are in ROUND 0 (blind round) of a distributed compute P-pass.\n"
                    f"The full artifact is too large for your context window, so you are "
                    f"reviewing AREA: {area_label}.\n\n"
                    f"Below is the full code for this area, plus skeletal signatures "
                    f"(class/method definitions only) of the other 5 areas for context.\n\n"
                    f"Your task: find all flaws you can identify in this area.\n\n"
                    f"Use the structured format (FINDING_ID, SEVERITY, FLAW_CLASS, "
                    f"ABSTRACTION_INDEX, DESCRIPTION, PROPOSED_FIX, VERIFIED).\n\n"
                    f"=== ARTIFACT: {area_label} ===\n\n"
                    f"{focused_code}\n\n"
                    f"=== END ARTIFACT ===\n\n"
                    f"Produce your findings now."
                )
                _log(f"  {mc.label}: BLOCKED → pre-decomposed blind dispatch "
                     f"(Area 1: {area_label}, {len(focused_code)} chars focused)")
                # Re-check feasibility with decomposed prompt
                decomp_tokens = len(decomposed_prompt) // 4
                d_feasible, d_p = mgr.check_dispatch_feasibility(model_spec, decomp_tokens)
                if not d_feasible:
                    _log(f"  {mc.label}: still infeasible after decomposition (P={d_p:.3f}), skipping")
                    continue
                try:
                    text, elapsed = dispatch_to_model(mc, decomposed_prompt, cdsfl_text)
                    _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s (decomposed blind)")
                    findings = parse_findings(mc.label, 0, text)
                    all_findings.extend(findings)
                    _log(f"  {mc.label}: {len(findings)} findings parsed")
                    responses[mc.label] = ModelResponse(
                        model_id=mc.label, round_idx=0, content=text,
                        response_time=elapsed, parseable=len(findings) > 0,
                        format_compliant=True, finding_count=len(findings),
                        mean_abstraction=(
                            sum(f.abstraction_index for f in findings) / len(findings)
                            if findings else 0.5
                        ),
                    )
                    save_output(
                        LOGS_DIR, "blind_decomposed", mc.label,
                        decomposed_prompt[:200] + "...", text,
                        metadata={"elapsed": round(elapsed, 1), "chars": len(text),
                                  "findings_count": len(findings), "round": 0,
                                  "area": area_label, "decomposed": True},
                    )
                except Exception as e:
                    _log(f"  {mc.label}: decomposed blind dispatch FAILED: {e}")
                continue
            else:
                # Genuinely infeasible and not a decomposition candidate
                continue

        # Pre-emptive decomposition: even if feasible, decompose when prompt
        # exceeds threshold.  Codex passes feasibility (GPT-5.4 context is large)
        # but `codex exec` CLI times out on 172K char prompts.
        threshold = DECOMPOSITION_CONTEXT_THRESHOLD.get(mc.label, 100000)
        if threshold > 0 and len(prompt) > threshold:
            area_idx = 0
            focused_code, area_label = _extract_area_code(prompt, area_idx)
            decomposed_prompt = (
                f"You are in ROUND 0 (blind round) of a distributed compute P-pass.\n"
                f"The full artifact is too large for efficient review, so you are "
                f"reviewing AREA: {area_label}.\n\n"
                f"Below is the full code for this area, plus skeletal signatures "
                f"(class/method definitions only) of the other 5 areas for context.\n\n"
                f"Your task: find all flaws you can identify in this area.\n\n"
                f"Use the structured format (FINDING_ID, SEVERITY, FLAW_CLASS, "
                f"ABSTRACTION_INDEX, DESCRIPTION, PROPOSED_FIX, VERIFIED).\n\n"
                f"=== ARTIFACT: {area_label} ===\n\n"
                f"{focused_code}\n\n"
                f"=== END ARTIFACT ===\n\n"
                f"Produce your findings now."
            )
            _log(f"  {mc.label}: context={len(prompt)} chars > threshold={threshold}, "
                 f"pre-emptive decomposed blind dispatch (Area 1: {area_label}, "
                 f"{len(focused_code)} chars focused)")
            try:
                text, elapsed = dispatch_to_model(mc, decomposed_prompt, cdsfl_text)
                _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s (decomposed blind)")
                findings = parse_findings(mc.label, 0, text)
                all_findings.extend(findings)
                _log(f"  {mc.label}: {len(findings)} findings parsed")
                responses[mc.label] = ModelResponse(
                    model_id=mc.label, round_idx=0, content=text,
                    response_time=elapsed, parseable=len(findings) > 0,
                    format_compliant=True, finding_count=len(findings),
                    mean_abstraction=(
                        sum(f.abstraction_index for f in findings) / len(findings)
                        if findings else 0.5
                    ),
                )
                save_output(
                    LOGS_DIR, "blind_decomposed", mc.label,
                    decomposed_prompt[:200] + "...", text,
                    metadata={"elapsed": round(elapsed, 1), "chars": len(text),
                              "findings_count": len(findings), "round": 0,
                              "area": area_label, "decomposed": True,
                              "reason": "pre-emptive (prompt > threshold)"},
                )
            except Exception as e:
                _log(f"  {mc.label}: pre-emptive decomposed dispatch FAILED: {e}")
            continue

        # Dispatch
        try:
            text, elapsed = dispatch_to_model(mc, prompt, cdsfl_text)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")

            # Parse findings
            findings = parse_findings(mc.label, 0, text)
            all_findings.extend(findings)
            _log(f"  {mc.label}: {len(findings)} findings parsed")

            responses[mc.label] = ModelResponse(
                model_id=mc.label,
                round_idx=0,
                content=text,
                response_time=elapsed,
                parseable=len(findings) > 0,
                format_compliant=True,
                finding_count=len(findings),
                mean_abstraction=(
                    sum(f.abstraction_index for f in findings) / len(findings)
                    if findings else 0.5
                ),
            )

            # Save output
            save_output(
                LOGS_DIR, "blind", mc.label, prompt[:200] + "...",
                text,
                metadata={
                    "elapsed": round(elapsed, 1),
                    "chars": len(text),
                    "findings_count": len(findings),
                    "round": 0,
                },
            )

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
            _log(f"  {mc.label}: Treating as model failure, continuing round")
            responses[mc.label] = ModelResponse(
                model_id=mc.label,
                round_idx=0,
                content="",
                response_time=mc.timeout + 1.0,
            )
        except Exception as e:
            _log(f"  {mc.label}: ERROR — {e}")
            responses[mc.label] = ModelResponse(
                model_id=mc.label,
                round_idx=0,
                content="",
                response_time=mc.timeout + 1.0 if "timeout" in str(e).lower() else 0.0,
            )

    _log(f"Blind round complete: {len(all_findings)} total findings from "
         f"{sum(1 for r in responses.values() if r.content)} models")

    return responses, all_findings


def _extract_area_code(artifact: str, area_idx: int) -> tuple[str, str]:
    """Extract one area's full code + skeletal signatures of other areas.

    Returns (focused_code, area_label).
    """
    import re as _re

    AREAS = [
        ("Role Assignment", ["class RoleAssignment", "class Role("]),
        ("Load Balancing", ["class LoadBalancer", "class Task("]),
        ("Round Progression / FSM", ["class RoundProgressionFSM", "class State("]),
        ("Convergence Detection", ["class ConvergenceDetector", "class FindingEquivalenceClass"]),
        ("Diminishing Returns", ["class DiminishingReturnsDetector"]),
        ("Failure Handling + Manager", ["class FailureHandler", "class DynamicManager"]),
    ]

    area_label = AREAS[area_idx % len(AREAS)][0]
    target_classes = AREAS[area_idx % len(AREAS)][1]
    lines = artifact.split("\n")

    # Find class boundaries
    class_ranges = []
    for i, line in enumerate(lines):
        if _re.match(r'^class \w+', line):
            class_ranges.append((i, line.strip()))

    target_lines = set()
    for start_idx, class_line in class_ranges:
        is_target = any(marker in class_line for marker in target_classes)
        end_idx = len(lines)
        for next_start, _ in class_ranges:
            if next_start > start_idx:
                end_idx = next_start
                break

        if is_target:
            for j in range(start_idx, end_idx):
                target_lines.add(j)
        else:
            # Skeletal: class def + method signatures (Gemini/CX recommendation)
            for j in range(start_idx, min(start_idx + 3, end_idx)):
                target_lines.add(j)
            for j in range(start_idx, end_idx):
                stripped = lines[j].strip()
                if stripped.startswith("def ") or stripped.startswith("async def "):
                    target_lines.add(j)
                    if j + 1 < end_idx and '"""' in lines[j + 1]:
                        target_lines.add(j + 1)

    # Module-level definitions (imports, config, dataclasses)
    first_class = class_ranges[0][0] if class_ranges else len(lines)
    for j in range(min(first_class, 200)):
        target_lines.add(j)

    focused = "\n".join(lines[j] for j in sorted(target_lines))
    return focused, area_label


def _deepseek_prior_findings(
    all_findings: List[Finding], area_label: str
) -> str:
    """Filter prior findings relevant to a specific area for DeepSeek."""
    area_keywords = {
        "Role Assignment": ["role", "assignment", "pm", "col", "par", "player manager"],
        "Load Balancing": ["load", "balance", "allocation", "task", "feasibility", "dispatch"],
        "Round Progression / FSM": ["fsm", "state", "round", "transition", "terminal"],
        "Convergence Detection": ["convergence", "kappa", "similarity", "equivalence", "novel"],
        "Diminishing Returns": ["diminishing", "marginal", "yield", "stop", "vcr", "mu"],
        "Failure Handling + Manager": ["failure", "timeout", "recovery", "fingerprint", "manager"],
    }
    keywords = area_keywords.get(area_label, [])
    relevant = [f for f in all_findings
                if any(kw in f.description.lower() for kw in keywords)]
    return format_findings_for_context(relevant[:30]) if relevant else "(No prior findings for this area.)"


# CONVERGENCE_EXCLUDED_MODELS and DECOMPOSITION_CONTEXT_THRESHOLD
# are now in runner_core.py (re-exported above).

# Model restart: track how many times each model has been restarted.
# After feasibility block, instead of permanent exclusion, restart with
# curated context (top findings by severity, deduplicated, capped).
MAX_RESTARTS_PER_MODEL = 2  # prevent infinite restart loops
RESTART_CONTEXT_CAP = 50  # max findings in restart context


def run_adaptive_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    round_idx: int,
    base_artifact: str,
    prior_findings_text: str,
    cdsfl_text: str,
    all_prior_findings: Optional[List[Finding]] = None,
) -> tuple[Dict[str, ModelResponse], List[Finding]]:
    """Phase 2+: Adaptive round with DeepSeek task decomposition.

    Standard models get the full artifact + all prior findings.
    DeepSeek gets one area's full code + skeletal signatures of other areas
    + area-relevant prior findings only, rotating through 6 areas.
    """
    _log(f"=== ROUND {round_idx}: ADAPTIVE ===")

    # Standard prompt for non-DeepSeek models
    prompt = (
        f"You are in ROUND {round_idx} of a distributed compute P-pass.\n\n"
        f"The following findings were produced in prior rounds:\n\n"
        f"{prior_findings_text}\n\n"
        f"Your task: review the artifact below and find what was MISSED. "
        f"Do not repeat findings already listed above. Focus on:\n"
        f"- Flaws the prior findings did not catch\n"
        f"- Deeper analysis of issues that were only superficially noted\n"
        f"- Cross-cutting concerns that span multiple areas\n"
        f"- Edge cases not yet tested\n\n"
        f"Use the same structured format (FINDING_ID, SEVERITY, etc.).\n\n"
        f"=== ARTIFACT UNDER REVIEW ===\n\n"
        f"{base_artifact}\n\n"
        f"=== END ARTIFACT ===\n\n"
        f"Produce your findings now. If you genuinely find nothing new, "
        f"state that explicitly."
    )

    responses: Dict[str, ModelResponse] = {}
    all_findings: List[Finding] = []
    decomposed_models: set[str] = set()  # Track which models used decomposed dispatch

    # Get allocation from the manager (uses live fingerprints)
    _log(f"  Live fingerprints:")
    for mid, fp in mgr._live_fingerprints.items():
        role = mgr.role_assignment.role_map.get(mid, Role.PAR)
        _log(f"    {mid} ({role.value}): D={fp.D_decay:.3f} v={fp.v_bar:.3f} "
             f"A={fp.A:.3f} C={fp.C:.3f}")

    for mc in exp_config.models:
        if mc.role == "collator":
            continue
        if mc.label not in mgr.failure_handler.active_models:
            _log(f"  {mc.label}: not active, skipping")
            continue

        model_spec = next(
            (m for m in mgr.get_live_models() if m.model_id == mc.label), None
        )
        if model_spec is None:
            continue

        # Context-adaptive dispatch: ANY model approaching context limits
        # gets decomposed dispatch.  Thresholds per model from Exp12 data.
        # Founder: "don't feed ALL context — decomposition should apply to
        # ALL models where relevant.  Turn it off and back on again!"
        use_decomposition = False
        threshold = DECOMPOSITION_CONTEXT_THRESHOLD.get(mc.label, 100000)
        if threshold == 0:
            use_decomposition = True  # Always decomposed (e.g., DeepSeek)
        else:
            all_context_chars = len(base_artifact) + len(prior_findings_text)
            if all_context_chars > threshold:
                use_decomposition = True
                _log(f"  {mc.label}: context={all_context_chars} chars > threshold={threshold}, "
                     f"switching to decomposed dispatch")

        if use_decomposition:
            decomposed_models.add(mc.label)
            area_idx = (round_idx - 1) % 6
            focused_code, area_label = _extract_area_code(base_artifact, area_idx)
            area_prior = _deepseek_prior_findings(
                all_prior_findings or [], area_label
            )
            model_prompt = (
                f"You are in ROUND {round_idx} of a distributed compute P-pass.\n"
                f"You are reviewing AREA: {area_label}.\n\n"
                f"Below is the full code for this area, plus skeletal signatures "
                f"(class/method definitions only) of the other 5 areas for context.\n\n"
                f"Prior findings relevant to this area:\n{area_prior}\n\n"
                f"Your task: find flaws in this area that prior reviewers missed. "
                f"If you see potential cross-component issues, flag them but note "
                f"they are unverified from your scope.\n\n"
                f"Use the structured format (FINDING_ID, SEVERITY, FLAW_CLASS, "
                f"ABSTRACTION_INDEX, DESCRIPTION, PROPOSED_FIX, VERIFIED).\n\n"
                f"=== ARTIFACT: {area_label} ===\n\n"
                f"{focused_code}\n\n"
                f"=== END ARTIFACT ===\n\n"
                f"Produce your findings now."
            )
            _log(f"  {mc.label}: decomposed — Area {area_idx+1}: {area_label} "
                 f"({len(focused_code)} chars focused, {len(model_prompt)} chars total)")
        else:
            model_prompt = prompt

        prompt_tokens = len(model_prompt) // 4
        feasible, p_feasible = mgr.check_dispatch_feasibility(model_spec, prompt_tokens)
        if not feasible:
            # Model restart logic (IT Crowd principle): instead of permanent
            # blocking, switch to decomposed dispatch with minimal context.
            # This gives the model a "fresh start" with manageable context.
            if mc.label not in decomposed_models and restart_counts.get(mc.label, 0) < MAX_RESTARTS_PER_MODEL:
                restart_counts[mc.label] = restart_counts.get(mc.label, 0) + 1
                _log(f"  {mc.label}: feasibility BLOCKED (P={p_feasible:.3f}) → "
                     f"RESTARTING with decomposed dispatch (restart #{restart_counts[mc.label]})")
                # Blend fingerprint: 50% initial + 50% pre-block (CC2 recommendation).
                # Gives the manager a reasonable prior while allowing adaptation.
                initial_fp = INITIAL_FINGERPRINTS.get(mc.label)
                pre_block_fp = mgr._live_fingerprints.get(mc.label)
                if initial_fp and pre_block_fp:
                    from dynamic_management import CapabilityFingerprint as _CFP
                    blended = _CFP(
                        D_decay=0.5 * initial_fp.D_decay + 0.5 * pre_block_fp.D_decay,
                        v_bar=0.5 * initial_fp.v_bar + 0.5 * pre_block_fp.v_bar,
                        A=0.5 * initial_fp.A + 0.5 * pre_block_fp.A,
                        C=0.5 * initial_fp.C + 0.5 * pre_block_fp.C,
                    )
                    mgr._live_fingerprints[mc.label] = blended
                    mgr._round_metrics[mc.label].clear()  # reset windowed history
                    _log(f"  {mc.label}: fingerprint blended (A={blended.A:.3f}, C={blended.C:.3f})")
                # Switch to decomposed dispatch with minimal context
                use_decomposition = True
                decomposed_models.add(mc.label)
                area_idx = (round_idx - 1) % 6
                focused_code, area_label = _extract_area_code(base_artifact, area_idx)
                # Minimal restart context: top findings by severity, capped
                top_findings = sorted(all_prior_findings or [], key=lambda f: f.severity, reverse=True)
                restart_context = format_findings_for_context(top_findings[:RESTART_CONTEXT_CAP])
                model_prompt = (
                    f"You are in ROUND {round_idx} of a distributed compute P-pass.\n"
                    f"You are reviewing AREA: {area_label}.\n\n"
                    f"Below is the full code for this area, plus skeletal signatures "
                    f"of the other 5 areas for context.\n\n"
                    f"Top prior findings (summary):\n{restart_context}\n\n"
                    f"Your task: find flaws in this area that prior reviewers missed.\n\n"
                    f"Use the structured format (FINDING_ID, SEVERITY, FLAW_CLASS, "
                    f"ABSTRACTION_INDEX, DESCRIPTION, PROPOSED_FIX, VERIFIED).\n\n"
                    f"=== ARTIFACT: {area_label} ===\n\n"
                    f"{focused_code}\n\n"
                    f"=== END ARTIFACT ===\n\n"
                    f"Produce your findings now."
                )
                prompt_tokens = len(model_prompt) // 4
                feasible, p_feasible = mgr.check_dispatch_feasibility(model_spec, prompt_tokens)
                if not feasible:
                    _log(f"  {mc.label}: still BLOCKED after restart (P={p_feasible:.3f}), skipping")
                    continue
            else:
                reason = "max restarts reached" if restart_counts.get(mc.label, 0) >= MAX_RESTARTS_PER_MODEL else "already decomposed"
                _log(f"  {mc.label}: feasibility BLOCKED (P={p_feasible:.3f}), {reason}")
                continue

        try:
            text, elapsed = dispatch_to_model(mc, model_prompt, cdsfl_text)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")

            findings = parse_findings(mc.label, round_idx, text)
            all_findings.extend(findings)
            _log(f"  {mc.label}: {len(findings)} findings parsed")

            responses[mc.label] = ModelResponse(
                model_id=mc.label, round_idx=round_idx, content=text,
                response_time=elapsed, parseable=len(findings) > 0,
                format_compliant=True, finding_count=len(findings),
                mean_abstraction=(
                    sum(f.abstraction_index for f in findings) / len(findings)
                    if findings else 0.5
                ),
            )

            save_output(
                LOGS_DIR, f"round{round_idx}", mc.label, prompt[:200] + "...",
                text,
                metadata={
                    "elapsed": round(elapsed, 1),
                    "chars": len(text),
                    "findings_count": len(findings),
                    "round": round_idx,
                },
            )

            # Checkpoint after each successful model dispatch
            save_checkpoint({
                "current_round": round_idx,
                "completed_models": list(responses.keys()),
                "total_findings": len(all_findings),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
            _log(f"  {mc.label}: Treating as model failure, continuing round")
            responses[mc.label] = ModelResponse(
                model_id=mc.label, round_idx=round_idx, content="",
                response_time=mc.timeout + 1.0,
            )
            continue
        except Exception as e:
            _log(f"  {mc.label}: ERROR — {e}")
            responses[mc.label] = ModelResponse(
                model_id=mc.label, round_idx=round_idx, content="",
                response_time=mc.timeout + 1.0 if "timeout" in str(e).lower() else 0.0,
            )

    _log(f"Round {round_idx} complete: {len(all_findings)} findings from "
         f"{sum(1 for r in responses.values() if r.content)} models")

    return responses, all_findings, decomposed_models


# format_findings_for_context is now in runner_core.py (re-exported above).

CHECKPOINT_PATH = LOGS_DIR / "checkpoint.json"


def save_checkpoint(data: Dict[str, Any]) -> None:
    """Save experiment state to disk after each dispatch."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    _log(f"  [CHECKPOINT] Saved ({len(data.get('completed_models', []))} models, "
         f"round {data.get('current_round', 0)})")


def load_checkpoint() -> Optional[Dict[str, Any]]:
    """Load checkpoint if it exists."""
    if CHECKPOINT_PATH.exists():
        data = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
        _log(f"  [CHECKPOINT] Resumed from round {data.get('current_round', 0)}, "
             f"{len(data.get('completed_models', []))} models completed")
        return data
    return None


def run_full_experiment():
    """Run the full Live Wire experiment."""
    source_env()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    exp_config = load_default_config()
    exp_config.logs_dir = LOGS_DIR
    cdsfl_text = exp_config.cdsfl_system_prompt

    # Build model specs for the DynamicManager
    model_specs = build_model_specs(exp_config)
    _log(f"Model pool: {[m.model_id for m in model_specs]}")

    # Load the artifact to review (needed for max_rounds scaling)
    artifact_path = REPO_ROOT / "bench" / "dynamic_management.py"
    artifact_text = artifact_path.read_text(encoding="utf-8")
    artifact_lines = artifact_text.count('\n')

    # Initialise DynamicManager
    events: List[ManagerEvent] = []
    def on_event(event: ManagerEvent) -> None:
        events.append(event)
        _log(f"  [EVENT] {event.event_type.value}: {event.detail}")

    # Scale max_rounds with artifact size (CC2 confer recommendation).
    # ceil(lines/200) for this artifact gives ~16, aligning with where
    # vocabulary novelty dropped below 10% in Exp12.  Minimum 10.
    import math as _math
    # Budget cap, not convergence criterion.  The real stop comes from
    # vocab saturation (Fix 1) or per-model mu (Fix 7).  Ceiling of 30
    # prevents runaway costs on large artifacts (CC2 confer recommendation).
    scaled_max_rounds = max(10, min(_math.ceil(artifact_lines / 200), 30))

    dm_config = DynamicManagementConfig(
        max_rounds=scaled_max_rounds,
        feasibility_threshold=0.90,
    )
    mgr = DynamicManager(model_specs, config=dm_config, event_callback=on_event)

    # Model restart tracking (IT Crowd principle: turn it off and back on again)
    restart_counts: Dict[str, int] = {m.model_id: 0 for m in model_specs}
    blocked_models: Dict[str, int] = {}  # model_id → round when first blocked

    _log(f"Roles assigned: {mgr.role_assignment.role_map}")
    _log(f"PM: {mgr.role_assignment.pm_model_id}")
    _log(f"Artifact: {artifact_path.name} ({len(artifact_text)} chars, "
         f"{artifact_lines} lines) → max_rounds={scaled_max_rounds}")

    # Build blind round prompt
    blind_prompt = build_task_prompt(artifact_text)
    _log(f"Blind prompt: {len(blind_prompt)} chars")

    # ── Phase 1: Blind Round ──
    responses, findings = run_blind_round(exp_config, mgr, blind_prompt, cdsfl_text)

    # Process through DynamicManager
    round_cost = sum(
        len(r.content) * 0.00001 for r in responses.values()  # rough cost estimate
    )
    result = mgr.process_round(
        responses, findings, [], round_cost=round_cost,
        duration=sum(r.response_time for r in responses.values()),
    )
    _log(f"Round 0 result: state={result.state}, "
         f"kappa={result.convergence_metric:.4f}, "
         f"mu={result.marginal_value:.4f}, "
         f"converged={result.converged}, stop={result.stop}")

    # Track all findings across rounds
    all_findings = list(findings)

    # ── Phase 2+: Adaptive Rounds ──
    round_idx = 1
    while not mgr.fsm.is_terminal:
        _log(f"\n{'='*60}")
        findings_context = format_findings_for_context(all_findings)

        responses, new_findings, decomposed_this_round = run_adaptive_round(
            exp_config, mgr, round_idx, artifact_text,
            findings_context, cdsfl_text,
            all_prior_findings=all_findings,
        )
        all_findings.extend(new_findings)

        round_cost = sum(
            len(r.content) * 0.00001 for r in responses.values()
        )
        # Filter out scope-limited models from convergence/D_decay calculations.
        # Only statically excluded models (DeepSeek — permanently scope-limited)
        # are excluded. Dynamically decomposed models still contribute valid
        # findings for convergence detection.
        #
        # Bug fix (Exp14a): previously, dynamically decomposed models were also
        # excluded. When ALL models are decomposed (large artifact + accumulated
        # context), the convergence detector received zero findings, causing
        # trivial convergence (kappa=1.0, mu=0.0 on empty set). The detector
        # declared CONVERGED after 2 consecutive empty rounds — not because
        # findings converged, but because it had no input.
        excluded_this_round = CONVERGENCE_EXCLUDED_MODELS.copy()
        convergence_findings = [
            f for f in new_findings if f.model_id not in excluded_this_round
        ]
        convergence_responses = {
            k: v for k, v in responses.items() if k not in excluded_this_round
        }
        result = mgr.process_round(
            convergence_responses, convergence_findings, [], round_cost=round_cost,
            duration=sum(r.response_time for r in convergence_responses.values()),
        )
        # Log all signals alongside each other for diagnostic comparison
        novelty = mgr.diminishing_returns.novelty_rate(round_idx - 1)
        vocab_growth = mgr.diminishing_returns.vocab_growth_rate(round_idx - 1)
        vocab_sat = mgr.diminishing_returns.vocab_saturated(round_idx - 1)
        _log(f"Round {round_idx} result: state={result.state}, "
             f"kappa={result.convergence_metric:.4f}, "
             f"mu={result.marginal_value:.4f}, "
             f"novelty={novelty:.4f}, "
             f"vocab_growth={vocab_growth:.4f}{' [SATURATED]' if vocab_sat else ''}, "
             f"converged={result.converged}, stop={result.stop}")
        if new_findings != convergence_findings:
            excluded_count = len(new_findings) - len(convergence_findings)
            excluded_names = sorted(excluded_this_round & set(r.model_id for r in new_findings if hasattr(r, 'model_id')))
            if not excluded_names:
                excluded_names = sorted(excluded_this_round)
            _log(f"  ({excluded_count} findings from {', '.join(excluded_names)} excluded "
                 f"from convergence calc, included in master list)")

        # Report immune response diagnoses
        recent_diagnoses = mgr.health_monitor.all_diagnoses
        if recent_diagnoses:
            for diag in recent_diagnoses[-3:]:  # last 3 to avoid spam
                _log(f"  [IMMUNE:{diag.severity}] {diag.detector}: {diag.pathology}")
                _log(f"    → {diag.recommended_action}")

        round_idx += 1

    # ── Final Report ──
    _log(f"\n{'='*60}")
    _log(f"EXPERIMENT COMPLETE")
    _log(f"  Termination: {mgr.fsm.termination_reason}")
    _log(f"  Rounds: {round_idx}")
    _log(f"  Total findings: {len(all_findings)}")
    _log(f"  Active models at end: {mgr.failure_handler.active_models}")
    _log(f"  Total events: {len(events)}")
    _log(f"  Model restarts: {restart_counts}")
    # Log final vocab stats
    vocab_sizes = mgr.diminishing_returns._vocab_sizes
    if vocab_sizes:
        final_vocab = max(vocab_sizes.values())
        _log(f"  Cumulative vocabulary: {final_vocab} unique terms")

    # Fingerprint evolution
    _log(f"\nFingerprint evolution:")
    for mid in sorted(mgr._live_fingerprints):
        initial = INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0, 0, 0, 0))
        final = mgr._live_fingerprints[mid]
        _log(f"  {mid}:")
        _log(f"    Initial: D={initial.D_decay:.3f} v={initial.v_bar:.3f} "
             f"A={initial.A:.3f} C={initial.C:.3f}")
        _log(f"    Final:   D={final.D_decay:.3f} v={final.v_bar:.3f} "
             f"A={final.A:.3f} C={final.C:.3f}")

    # Save final report
    report = {
        "experiment": f"{_EXPERIMENT_LABEL}_live_wire",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "termination_reason": mgr.fsm.termination_reason.value if mgr.fsm.termination_reason else None,
        "rounds": round_idx,
        "total_findings": len(all_findings),
        "active_models_at_end": sorted(mgr.failure_handler.active_models),
        "total_events": len(events),
        "model_restarts": restart_counts,
        "max_rounds_scaling": f"{artifact_lines} lines → {scaled_max_rounds} rounds",
        "vocab_trajectory": {
            str(r): {"size": s, "growth": round(mgr.diminishing_returns._vocab_growth_rates.get(r, 0), 4)}
            for r, s in sorted(mgr.diminishing_returns._vocab_sizes.items())
        },
        "fingerprint_evolution": {
            mid: {
                "initial": {
                    "D_decay": INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0,0,0,0)).D_decay,
                    "v_bar": INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0,0,0,0)).v_bar,
                    "A": INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0,0,0,0)).A,
                    "C": INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0,0,0,0)).C,
                },
                "final": {
                    "D_decay": round(fp.D_decay, 4),
                    "v_bar": round(fp.v_bar, 4),
                    "A": round(fp.A, 4),
                    "C": round(fp.C, 4),
                },
            }
            for mid, fp in mgr._live_fingerprints.items()
        },
        "round_results": [
            {
                "round": rr.round_idx,
                "state": rr.state,
                "kappa": round(rr.convergence_metric, 4),
                "mu": round(rr.marginal_value, 4),
                "converged": rr.converged,
                "stop": rr.stop,
                "findings_count": len(rr.findings),
                "active_models": sorted(rr.active_models),
            }
            for rr in mgr.round_results
        ],
        "event_log": [
            {
                "type": e.event_type.value,
                "model": e.model_id,
                "round": e.round_idx,
                "detail": e.detail,
                "timestamp": e.timestamp,
            }
            for e in events
        ],
    }

    report_path = LOGS_DIR / f"experiment_{_EXPERIMENT_LABEL}_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    _log(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="CDSFL Live Wire Experiment Runner",
    )
    parser.add_argument(
        "mode", nargs="?", default="full",
        choices=["preflight", "blind", "full"],
        help="Run mode (default: full)",
    )
    parser.add_argument(
        "--experiment", "-e", default=_DEFAULT_EXPERIMENT,
        help="Experiment label for logs directory and report naming "
             "(default: auto = next available number). "
             "E.g. --experiment 14 → logs/experiment_14/",
    )
    args = parser.parse_args()
    _set_experiment(args.experiment)

    if args.mode == "preflight":
        source_env()
        from experiment_11_orchestrator import run_preflight
        config = load_default_config()
        config.logs_dir = LOGS_DIR
        config.logs_dir.mkdir(parents=True, exist_ok=True)
        results = run_preflight(config)
        all_pass = all(
            r["identity_pass"] and r["compliance_pass"]
            for r in results.values()
        )
        sys.exit(0 if all_pass else 1)

    elif args.mode in ("blind", "full"):
        run_full_experiment()
    else:
        parser.print_help()
        sys.exit(1)
