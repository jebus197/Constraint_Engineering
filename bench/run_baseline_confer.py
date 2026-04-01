#!/usr/bin/env python3
"""Baseline CDSFL Confer: CC2 + CX + Gemini on immune task area.

Standard CDSFL schema with FFF situation directive (proven in Exp 18).
NO novel dispatch changes — sequential dispatch, existing infrastructure.
Purpose: validate all Exp 17/18 code fixes under live multi-model review
and establish a clean baseline for subsequent incremental changes.

Models:
  - CC2 (Claude Opus 4.6 via OpenRouter)
  - Codex (GPT-5.4 via codex exec CLI)
  - Gemini (Gemini 3.1 Pro via Google SDK)

Usage:
    python3 bench/run_baseline_confer.py [preflight|run]

    preflight  — verify all 3 models respond
    run        — full confer (preflight + blind R1 + adaptive R2-R3 + stop)
"""

from __future__ import annotations

import json
import os
import sys
import time
from copy import deepcopy
from dataclasses import asdict
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
from run_exp17_immune import (
    TASKS,
    TASK_MARKERS,
    TASK_SUBAREAS,
    REVIEW_AREAS,
    FINDING_FORMAT,
    SUBAREA_ESCALATION_CHARS,
    RoundTelemetry,
    run_layer1_preflight,
    _extract_code_area,
    _extract_task_area,
    _should_decompose,
    _build_task_prompt,
    _build_decomposed_prompt,
    _build_verified_facts,
    _build_explicit_unknowns,
    _find_model_spec,
    _report_dispatch_failure,
    _record_throughput,
    _effective_capacity,
)
from cdsfl_registry.composer import (
    compose,
    DirectivePacket,
    ComposedDirectiveSet,
    COMPOSER_MODEL_MAP,
)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "baseline_confer_20260331"

MAX_ROUNDS = 5          # Conservative — baseline, not endurance test
WALL_CLOCK_CAP_S = 2 * 3600  # 2 hours

# Test article: immune task area (most recent fixes, highest coverage)
TEST_ARTICLE_PATH = REPO_ROOT / "bench" / "dynamic_management.py"
MATH_APPENDIX_PATH = REPO_ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
VERIFICATION_CHAIN_PATH = REPO_ROOT / "bench" / "verification_chain.py"
INTERFACE_SUMMARY_PATH = (
    REPO_ROOT / "bench" / "logs" / "experiment_17_interface_summary.md"
)

# 3-model subset: CC2, Codex (CX), Gemini
BASELINE_MODELS = {"CC2", "Codex", "Gemini"}

# FFF situation directive (proven in Exp 18)
FFF_SITUATION_TEXT = (
    "## Find-Fix-Follow Protocol (MANDATORY for this round)\n\n"
    "For EVERY finding, you MUST provide all three steps:\n\n"
    "**FIND:** Describe the issue precisely. Include the specific location "
    "(file, section, line if applicable), what is wrong, and evidence that "
    "it is wrong.\n\n"
    "**FIX:** Provide the exact corrected text, code, or formula. Not a "
    "suggestion -- the actual replacement. Use <<<< (old) ==== (new) >>>> "
    "markers for code fixes.\n\n"
    "**FOLLOW:** After writing your fix, trace its consequences through ALL "
    "other sections, functions, or formulas that reference the same variables, "
    "interfaces, or assumptions. Report any new issues your fix creates or "
    "reveals.\n\n"
    "If your fix creates no consequences, state \"FOLLOW: No downstream "
    "impact identified\" -- but this should be rare for non-trivial fixes.\n"
)


# ─────────────────────────────────────────────────────────────────────────────
# Composer integration
# ─────────────────────────────────────────────────────────────────────────────

def compose_for_model(model_label: str) -> ComposedDirectiveSet:
    """Compose directive set with FFF situation layer for a model."""
    composer_model = COMPOSER_MODEL_MAP.get(model_label, model_label)
    situation = DirectivePacket(
        layer="situation",
        name="baseline_fff_protocol",
        text=FFF_SITUATION_TEXT,
        constraint_class="HARD",
        tags={"baseline", "fff"},
    )
    return compose(
        task_domain="software",
        model=composer_model,
        situation=situation,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch: sequential, one model at a time (existing infrastructure)
# ─────────────────────────────────────────────────────────────────────────────

def _dispatch_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    task_key: str = "immune",
    round_type: str = "blind",
) -> tuple[List[Finding], Dict[str, str]]:
    """Dispatch prompt to 3 models sequentially. Returns (findings, responses)."""
    findings: List[Finding] = []
    responses: Dict[str, str] = {}

    for mc in exp_config.models:
        if mc.label not in BASELINE_MODELS:
            continue
        if mc.role == "collator":
            continue

        # Compose directives for this model
        try:
            composed = compose_for_model(mc.label)
            model_cdsfl = composed.rendered_text
            _log(f"  {mc.label}: composed directives "
                 f"({len(model_cdsfl)} chars, CID={composed.cid[:12]}...)")
        except Exception as e:
            _log(f"  {mc.label}: composer failed ({e}), using raw CDSFL")
            model_cdsfl = cdsfl_text

        # Dynamic decomposition check
        model_prompt = prompt
        decomposed = False
        eff_cap = _effective_capacity(mc.label, mc.timeout)
        if _should_decompose(mc.label, mgr):
            model_prompt, decomposed = _build_decomposed_prompt(
                prompt, full_code, task_key, mc.label, round_idx,
                max_chars=eff_cap or 0)
            _log(f"  {mc.label}: decomposed={decomposed}")

        # Pre-dispatch feasibility gate
        model_spec = _find_model_spec(mgr, mc.label)
        if model_spec:
            token_est = len(model_prompt) // 4
            ok, p_feasible = mgr.check_dispatch_feasibility(model_spec, token_est)
            if not ok:
                _log(f"  {mc.label}: DISPATCH BLOCKED (P={p_feasible:.3f}, "
                     f"~{token_est} tokens). Auto-decomposing.")
                model_prompt, decomposed = _build_decomposed_prompt(
                    prompt, full_code, task_key, mc.label, round_idx,
                    max_chars=eff_cap or 0)

        # Generous wall-clock: 3× timeout for large prompts
        wall_limit = mc.timeout * 3
        try:
            text, elapsed = dispatch_to_model(
                mc, model_prompt, model_cdsfl, wall_clock_limit=wall_limit)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")
            _record_throughput(mc.label, len(model_prompt), elapsed)

            model_findings = parse_findings(mc.label, round_idx, text)
            findings.extend(model_findings)
            responses[mc.label] = text
            _log(f"  {mc.label}: {len(model_findings)} findings parsed")

            # Save individual output
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            phase_label = f"r{round_idx}_{round_type}"
            save_output(
                LOGS_DIR, phase_label, mc.label,
                model_prompt[:200] + "...", text,
                metadata={
                    "round": round_idx,
                    "elapsed": round(elapsed, 1),
                    "chars": len(text),
                    "findings_count": len(model_findings),
                    "decomposed": decomposed,
                    "prompt_chars": len(model_prompt),
                })

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
            _report_dispatch_failure(
                mgr, mc.label, round_idx, f"circuit_breaker: {e}")
        except TimeoutError as e:
            _log(f"  {mc.label}: TIMEOUT — {e}")
            _report_dispatch_failure(mgr, mc.label, round_idx, f"timeout: {e}")
        except Exception as e:
            _log(f"  {mc.label}: ERROR — {type(e).__name__}: {e}")
            _report_dispatch_failure(
                mgr, mc.label, round_idx,
                f"{type(e).__name__}: {e}")

    return findings, responses


# ─────────────────────────────────────────────────────────────────────────────
# Convergence check (simplified for baseline)
# ─────────────────────────────────────────────────────────────────────────────

def _check_convergence(
    all_findings: List[List[Finding]],
    round_idx: int,
) -> tuple[bool, str]:
    """Simple convergence check: stop if novelty drops below threshold.

    Returns (converged: bool, reason: str).
    """
    if round_idx < 1:
        return False, "min_rounds"

    if len(all_findings) < 2:
        return False, "insufficient_data"

    current = all_findings[-1]
    previous_all = [f for rnd in all_findings[:-1] for f in rnd]

    if not current:
        return True, "zero_findings"

    # Novelty rate: fraction of new findings not similar to any prior
    novel = 0
    for f in current:
        is_novel = True
        for pf in previous_all:
            # Simple text overlap check
            f_words = set(f.description.lower().split())
            pf_words = set(pf.description.lower().split())
            if f_words and pf_words:
                overlap = len(f_words & pf_words) / max(len(f_words | pf_words), 1)
                if overlap > 0.5:
                    is_novel = False
                    break
        if is_novel:
            novel += 1

    novelty_rate = novel / len(current) if current else 0
    _log(f"  Convergence check: {novel}/{len(current)} novel "
         f"(rate={novelty_rate:.2f})")

    if novelty_rate < 0.15:
        return True, f"low_novelty({novelty_rate:.2f})"

    return False, f"continuing(novelty={novelty_rate:.2f})"


# ─────────────────────────────────────────────────────────────────────────────
# Pull-the-plug checks
# ─────────────────────────────────────────────────────────────────────────────

def _safety_check(responses: Dict[str, str], round_idx: int) -> Optional[str]:
    """Check for problems that warrant stopping the experiment.

    Returns a reason string if we should stop, None otherwise.
    """
    # All models failed
    if not responses:
        return "all_models_failed"

    for label, text in responses.items():
        # Empty or near-empty response
        if len(text.strip()) < 50:
            _log(f"  SAFETY: {label} returned near-empty response ({len(text)} chars)")
            return f"{label}_empty_response"

        # Model refused
        if "[MODEL_REFUSED" in text:
            _log(f"  SAFETY: {label} refused the prompt")
            return f"{label}_refused"

        # Gibberish detection: if response has no recognizable finding structure
        # AND no coherent English, flag it
        lower = text.lower()
        has_structure = any(
            kw in lower for kw in
            ["find:", "fix:", "follow:", "severity:", "finding_id:", "description:"]
        )
        has_english = len(text.split()) > 20
        if not has_structure and not has_english:
            _log(f"  SAFETY: {label} returned apparent gibberish")
            return f"{label}_gibberish"

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment loop
# ─────────────────────────────────────────────────────────────────────────────

def run_preflight(exp_config: ExperimentConfig, cdsfl_text: str) -> bool:
    """Quick preflight: dispatch a trivial prompt to each model."""
    _log("=" * 60)
    _log("PREFLIGHT: Testing 3-model connectivity")
    _log("=" * 60)

    test_prompt = (
        "This is a connectivity test. Respond with exactly:\n"
        "STATUS: OK\n"
        "MODEL: [your model name]\n"
        "Nothing else."
    )

    all_ok = True
    for mc in exp_config.models:
        if mc.label not in BASELINE_MODELS:
            continue
        _log(f"  Testing {mc.label}...")
        try:
            text, elapsed = dispatch_to_model(mc, test_prompt, cdsfl_text)
            ok = len(text.strip()) > 5
            _log(f"  {mc.label}: {'OK' if ok else 'FAILED'} "
                 f"({elapsed:.1f}s, {len(text)} chars)")
            if not ok:
                all_ok = False
        except Exception as e:
            _log(f"  {mc.label}: FAILED — {e}")
            all_ok = False

    return all_ok


def run_confer(exp_config: ExperimentConfig, cdsfl_text: str) -> Dict[str, Any]:
    """Run the baseline confer: blind R1 → adaptive R2+ → stop on convergence."""
    _log("=" * 60)
    _log("BASELINE CONFER: CC2 + CX + Gemini, FFF + CDSFL")
    _log(f"  Max rounds: {MAX_ROUNDS}")
    _log(f"  Wall clock cap: {WALL_CLOCK_CAP_S}s")
    _log(f"  Task: immune (dynamic_management.py)")
    _log(f"  Logs: {LOGS_DIR}")
    _log("=" * 60)

    # Load test articles — use task-extracted code, NOT the full file.
    # The full dynamic_management.py is 269K chars (~67K tokens). Sending
    # that raw caused CC2 and Gemini to timeout in the first attempt.
    # Task extraction focuses on immune-relevant code + skeletal context.
    full_code_raw = TEST_ARTICLE_PATH.read_text(encoding="utf-8")
    full_code = _extract_task_area(full_code_raw, "immune") or full_code_raw
    _log(f"  Immune extraction: {len(full_code_raw):,} → {len(full_code):,} chars "
         f"({100*(1-len(full_code)/len(full_code_raw)):.0f}% reduction)")
    math_appendix = MATH_APPENDIX_PATH.read_text(encoding="utf-8")
    verification_chain = VERIFICATION_CHAIN_PATH.read_text(encoding="utf-8")
    interface_summary = ""
    if INTERFACE_SUMMARY_PATH.exists():
        interface_summary = INTERFACE_SUMMARY_PATH.read_text(encoding="utf-8")

    # Build DynamicManager
    dm_config = DynamicManagementConfig()
    dm_config.max_rounds = MAX_ROUNDS
    model_specs = build_model_specs(exp_config)
    mgr = DynamicManager(model_specs, dm_config)
    telemetry = RoundTelemetry(LOGS_DIR)

    all_findings: List[List[Finding]] = []
    all_responses: List[Dict[str, str]] = []
    experiment_start = time.monotonic()
    result = {
        "experiment": "baseline_confer",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "models": [mc.label for mc in exp_config.models
                    if mc.label in BASELINE_MODELS],
        "task": "immune",
        "max_rounds": MAX_ROUNDS,
        "rounds": [],
    }

    for round_idx in range(MAX_ROUNDS):
        round_start = time.monotonic()
        wall_elapsed = round_start - experiment_start
        if wall_elapsed > WALL_CLOCK_CAP_S:
            _log(f"\nWALL CLOCK CAP reached ({wall_elapsed:.0f}s). Stopping.")
            break

        _log(f"\n{'─' * 60}")
        round_type = "blind" if round_idx == 0 else "adaptive"
        _log(f"Round {round_idx} ({round_type})")
        _log(f"{'─' * 60}")

        # Build prompt
        prior_findings_text = ""
        if round_idx > 0 and all_findings:
            # Aggregate all prior findings for context
            prior_flat = [f for rnd in all_findings for f in rnd]
            prior_findings_text = format_findings_for_context(prior_flat)

        prompt = _build_task_prompt(
            task_key="immune",
            round_label=f"R{round_idx} ({round_type})",
            round_type=round_type,
            code=full_code,
            math_appendix=math_appendix,
            verification_chain=verification_chain,
            interface_summary=interface_summary,
            prior_findings_text=prior_findings_text,
        )

        _log(f"  Prompt: {len(prompt):,} chars")

        # Dispatch
        findings, responses = _dispatch_round(
            exp_config, mgr, prompt, cdsfl_text, full_code, round_idx,
            round_type=round_type,
        )

        # Safety check
        problem = _safety_check(responses, round_idx)
        if problem:
            _log(f"\n*** PULL THE PLUG: {problem} ***")
            result["terminated"] = problem
            break

        all_findings.append(findings)
        all_responses.append(responses)

        round_elapsed = time.monotonic() - round_start
        round_data = {
            "round": round_idx,
            "type": round_type,
            "findings_count": len(findings),
            "models_responded": list(responses.keys()),
            "elapsed_s": round(round_elapsed, 1),
            "per_model": {
                label: len([f for f in findings if f.model_id == label])
                for label in responses
            },
        }
        result["rounds"].append(round_data)

        _log(f"\n  Round {round_idx} summary: {len(findings)} findings from "
             f"{len(responses)} models ({round_elapsed:.1f}s)")
        for label in sorted(responses.keys()):
            model_count = len([f for f in findings if f.model_id == label])
            _log(f"    {label}: {model_count} findings")

        # Feed findings to DynamicManager — ONE call per round with ALL
        # responses (FSM advances once per process_round call; calling it
        # per-model would corrupt the round index and convergence state).
        rn_responses: Dict[str, ModelResponse] = {}
        for label, text in responses.items():
            model_findings_for_label = [
                f for f in findings if f.model_id == label
            ]
            rn_responses[label] = ModelResponse(
                model_id=label,
                round_idx=round_idx,
                content=text,
                response_time=round_elapsed,
                parseable=len(model_findings_for_label) > 0,
                format_compliant=True,
                finding_count=len(model_findings_for_label),
                mean_abstraction=(
                    sum(f.abstraction_index for f in model_findings_for_label)
                    / len(model_findings_for_label)
                    if model_findings_for_label else 0.5
                ),
            )

        dm_result = mgr.process_round(
            rn_responses,
            findings,
            [],  # no explicit task objects needed for convergence tracking
            round_cost=1.0,
            duration=round_elapsed,
        )

        # Log immune diagnostics from DynamicManager
        if dm_result.recovery_actions:
            _log(f"  Immune: {dm_result.recovery_actions}")
        _log(f"  DM: kappa={dm_result.convergence_metric:.3f}, "
             f"mu={dm_result.marginal_value:.3f}, "
             f"converged={dm_result.converged}, stop={dm_result.stop}")
        if dm_result.converged:
            _log(f"\n  DM CONVERGED at round {round_idx}")
            result["converged_at"] = round_idx
            result["convergence_reason"] = "dm_converged"
            break
        if dm_result.stop:
            _log(f"\n  DM STOP at round {round_idx}: diminishing returns")
            result["converged_at"] = round_idx
            result["convergence_reason"] = "dm_diminishing_returns"
            break

        # Fallback convergence check (simple novelty rate)
        converged, reason = _check_convergence(all_findings, round_idx)
        _log(f"  Convergence (fallback): {reason}")
        if converged:
            _log(f"\n  CONVERGED at round {round_idx}: {reason}")
            result["converged_at"] = round_idx
            result["convergence_reason"] = reason
            break

    # Final summary
    total_elapsed = time.monotonic() - experiment_start
    total_findings = sum(len(rnd) for rnd in all_findings)
    result["total_findings"] = total_findings
    result["total_rounds"] = len(all_findings)
    result["total_elapsed_s"] = round(total_elapsed, 1)
    result["end_time"] = datetime.now(timezone.utc).isoformat()

    # Per-model summary
    per_model_totals = {}
    for rnd in all_findings:
        for f in rnd:
            per_model_totals[f.model_id] = per_model_totals.get(f.model_id, 0) + 1
    result["per_model_totals"] = per_model_totals

    # Save results
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = LOGS_DIR / "baseline_confer_report.json"
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    _log(f"\n{'=' * 60}")
    _log(f"BASELINE CONFER COMPLETE")
    _log(f"  Rounds: {len(all_findings)}")
    _log(f"  Total findings: {total_findings}")
    _log(f"  Per model: {per_model_totals}")
    _log(f"  Elapsed: {total_elapsed:.0f}s")
    _log(f"  Report: {report_path}")
    _log(f"{'=' * 60}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    source_env()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load config and filter to 3 models
    exp_config = load_default_config()

    # Read CDSFL text
    cdsfl_path = (REPO_ROOT / "bench" / "directives" / "universal"
                  / "cdsfl_core_formal.md")
    cdsfl_text = cdsfl_path.read_text(encoding="utf-8")

    mode = sys.argv[1] if len(sys.argv) > 1 else "run"

    if mode == "preflight":
        ok = run_preflight(exp_config, cdsfl_text)
        sys.exit(0 if ok else 1)

    elif mode == "run":
        # Preflight first
        ok = run_preflight(exp_config, cdsfl_text)
        if not ok:
            _log("\nPREFLIGHT FAILED. Aborting.")
            sys.exit(1)

        _log("\nPreflight passed. Starting confer in 5s...")
        time.sleep(5)

        result = run_confer(exp_config, cdsfl_text)

        if result.get("terminated"):
            _log(f"\nExperiment terminated: {result['terminated']}")
            sys.exit(2)

        sys.exit(0)

    else:
        print(f"Unknown mode: {mode}. Use: preflight | run")
        sys.exit(1)


if __name__ == "__main__":
    main()
