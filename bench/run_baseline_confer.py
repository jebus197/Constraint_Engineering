#!/usr/bin/env python3
"""Baseline CDSFL Confer: CC2 + CX + Gemini + DeepSeek + ChatGPT on immune task area.

Standard CDSFL schema with FFF situation directive (proven in Exp 18).
Sequential dispatch with multi-turn decomposed fallback. If single-turn
dispatch fails (timeout, circuit breaker, or any error), the prompt is
automatically split into WAIT-step chunks and delivered via multi-turn
decomposed dispatch. FFF instructions go in the final turn.

No model is ever excluded. EXCLUDE/ABORT signals from the immune layer
are intercepted and overridden with multi-turn decomposed dispatch.

FSM terminal state is caught and handled — the runner continues
collecting data even if the DynamicManager FSM enters a terminal state.

Models:
  - CC2 (Claude Opus 4.6 via OpenRouter)
  - Codex (GPT-5.4 via codex exec CLI)
  - Gemini (Gemini 3.1 Pro via Google SDK)
  - DeepSeek (DeepSeek Reasoner via DeepSeek API)
  - ChatGPT (GPT-5.4 via OpenRouter)

Usage:
    python3 bench/run_baseline_confer.py [preflight|run|--resume]

    preflight  — verify all 3 models respond
    run        — full confer (preflight + blind R1 + adaptive R2-R3 + stop)
    --resume   — resume from last checkpoint (skips preflight)
"""

from __future__ import annotations

import json
import math
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
from runner_core import (
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
from decomposed_dispatch import (
    decomposed_dispatch,
    DecomposedChunk,
    DecomposedResult,
    save_decomposed_result,
)
from bench.dm._convergence import _finding_similarity
from bench.verification_utils import run_quality_gate, QualityGateResult
from bench.immune_agents import run_immune_pipeline, ImmuneResponse
from input_complexity import (
    compute_gamma_input,
    compute_gamma_output,
    compute_amplification,
    recommend_dispatch,
    AmplificationHistory,
    AdaptiveQuestionOptimiser,
    HeapsResult,
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "baseline_confer_run10_20260403"

MAX_ROUNDS = 20         # Convergence is the real stop criterion; 20 is the review point
WALL_CLOCK_CAP_S = 8 * 3600  # 8 hours (convergence may take many rounds)

# Test article: immune task area (most recent fixes, highest coverage)
# Run 9: models receive the actual implementation files, not the re-export shim.
# The shim (dynamic_management.py) is only 78 lines / 3785 chars — useless for review.
TEST_ARTICLE_PATH = REPO_ROOT / "bench" / "dynamic_management.py"  # kept for backward compat
IMMUNE_SOURCE_FILES = [
    REPO_ROOT / "bench" / "dm" / "_immune.py",        # 102K — core immune layer
    REPO_ROOT / "bench" / "dm" / "_manager.py",        # 72K  — manager logic
    REPO_ROOT / "bench" / "dm" / "_failure_handler.py", # 25K  — failure handling
    REPO_ROOT / "bench" / "dm" / "_types.py",           # 27K  — type defs (immune portions)
    REPO_ROOT / "bench" / "dm" / "_convergence.py",     # 17K  — convergence detection
]
MATH_APPENDIX_PATH = REPO_ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
VERIFICATION_CHAIN_PATH = REPO_ROOT / "bench" / "verification_chain.py"
INTERFACE_SUMMARY_PATH = (
    REPO_ROOT / "bench" / "logs" / "experiment_17_interface_summary.md"
)

# 5-model set: all available frontier models
BASELINE_MODELS = {"CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"}

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
# Multi-turn decomposed dispatch: fallback when single-turn fails
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Context budget: IT Crowd fix — "turn it off and turn it back on again"
#
# When accumulated prior findings exceed a model's context budget, the model
# gets a CONTEXT RESET: only finding IDs + one-line summaries instead of full
# text. The model starts fresh but knows what's been found. This prevents
# the prompt bloat that killed DeepSeek in Run 7 R2 (300K+ chars of prior
# findings on top of a 190K base prompt).
# ─────────────────────────────────────────────────────────────────────────────


def _format_findings_summary_only(findings: List[Finding]) -> str:
    """One-line summary per finding — context reset mode.

    Used when full findings text exceeds a model's context budget.
    The model gets enough to avoid duplicates without the full text.
    """
    if not findings:
        return "(No findings from prior rounds.)"

    lines = [
        f"(CONTEXT RESET: {len(findings)} prior findings exist. "
        f"Showing ID + severity + one-line summary only. "
        f"Do NOT repeat these — find NEW issues.)\n"
    ]
    for f in findings:
        # Truncate description to first sentence or 120 chars
        desc = f.description
        first_sentence_end = desc.find(". ")
        if first_sentence_end > 0 and first_sentence_end < 120:
            desc = desc[:first_sentence_end + 1]
        elif len(desc) > 120:
            desc = desc[:120] + "..."
        lines.append(f"  {f.finding_id} (sev={f.severity:.2f}): {desc}")
    return "\n".join(lines)


def _format_findings_for_model(
    all_findings: List[List[Finding]],
    model_label: str,
    dm_config: DynamicManagementConfig,
) -> str:
    """Format prior findings with per-model context budget awareness.

    Strategy:
    1. Compute full findings text via format_findings_for_context().
    2. If it fits within the model's budget → use it.
    3. If not → CONTEXT RESET: switch to summary-only mode.

    Within the budget path, exclude the model's own prior findings
    (a model doesn't need its own output repeated back — the value is
    cross-pollination from OTHER models).
    """
    if not all_findings:
        return ""

    # Get this model's context budget
    budget = dm_config.context_budget_overrides.get(
        model_label, dm_config.context_budget_chars
    )

    # Flatten all prior findings, excluding this model's own
    cross_findings = [
        f for rnd in all_findings for f in rnd
        if f.model_id != model_label
    ]

    if not cross_findings:
        return "(No cross-model findings from prior rounds.)"

    # Try full text first
    full_text = format_findings_for_context(cross_findings)

    if len(full_text) <= budget:
        return full_text

    # Over budget — try last-round-only with full text
    max_round = max(f.round_idx for f in cross_findings)
    last_round = [f for f in cross_findings if f.round_idx == max_round]
    last_round_text = format_findings_for_context(last_round)

    if len(last_round_text) <= budget:
        # Last round fits — add summary of earlier rounds
        earlier = [f for f in cross_findings if f.round_idx < max_round]
        earlier_summary = _format_findings_summary_only(earlier)
        combined = earlier_summary + "\n\n" + last_round_text
        if len(combined) <= budget:
            return combined
        # Even combined is over budget — just use last round
        return last_round_text

    # Even last round alone exceeds budget → full context reset
    return _format_findings_summary_only(cross_findings)


# Target chunk size for multi-turn delivery (chars). Chosen to stay well
# within attention windows for all models (~30K tokens ≈ 120K chars).
MULTITURN_CHUNK_TARGET = 30_000  # ~7.5K tokens — well within Codex comfort zone


def _build_chunks(prompt: str, full_code: str, task_key: str) -> list[DecomposedChunk]:
    """Split a large prompt into WAIT-step chunks for multi-turn delivery.

    Strategy: separate the preamble/instructions from the code artifact and
    any appendices. Each becomes its own chunk. If any chunk exceeds
    MULTITURN_CHUNK_TARGET, split it at natural boundaries (class/def/blank
    line) or hard-split if no boundary found within target.

    Run 6 fix: previous threshold (80K) meant 100K artifacts landed in one
    chunk, causing Codex timeouts. Now 30K with guaranteed hard-split fallback.
    """
    chunks: list[DecomposedChunk] = []

    # Split at artifact boundary
    if "=== ARTIFACT" in prompt:
        preamble, rest = prompt.split("=== ARTIFACT", 1)
        chunks.append(DecomposedChunk(preamble.strip(), label="Preamble + instructions"))

        # Find each artifact block
        parts = rest.split("=== END ARTIFACT")
        for i, part in enumerate(parts):
            text = part.strip()
            if not text:
                continue
            # Re-add the delimiter prefix if it was split off
            if not text.startswith("=== ARTIFACT"):
                text = "=== ARTIFACT" + text
            text += "\n=== END ARTIFACT ==="

            if len(text) > MULTITURN_CHUNK_TARGET:
                # Split large artifact at class/def boundaries, with hard-split fallback
                sub_chunks = _split_artifact(text, MULTITURN_CHUNK_TARGET)
                for si, sc in enumerate(sub_chunks):
                    chunks.append(DecomposedChunk(
                        sc, label=f"Artifact {i+1} part {si+1}",
                    ))
            else:
                chunks.append(DecomposedChunk(text, label=f"Artifact {i+1}"))
    else:
        # No artifact structure — split by size
        if len(prompt) <= MULTITURN_CHUNK_TARGET:
            chunks.append(DecomposedChunk(prompt, label="Full prompt"))
        else:
            for i in range(0, len(prompt), MULTITURN_CHUNK_TARGET):
                chunk_text = prompt[i:i + MULTITURN_CHUNK_TARGET]
                chunks.append(DecomposedChunk(chunk_text, label=f"Part {i // MULTITURN_CHUNK_TARGET + 1}"))

    return chunks


def _split_artifact(text: str, target: int) -> list[str]:
    """Split a large artifact into chunks at natural boundaries.

    Priority: class/def boundaries > blank-line boundaries > hard split.
    Guarantees no chunk exceeds 2× target (hard split fallback).
    """
    lines = text.split("\n")
    result: list[str] = []
    current: list[str] = []
    current_len = 0

    for line in lines:
        # Natural boundary: class or top-level def (not indented)
        is_boundary = (
            line.startswith("class ") or
            (line.startswith("def ") and not line.startswith("    "))
        )
        # Soft boundary: blank line after exceeding target
        is_soft_boundary = (current_len > target and line.strip() == "")

        if current_len > target and (is_boundary or is_soft_boundary):
            result.append("\n".join(current))
            current = []
            current_len = 0

        current.append(line)
        current_len += len(line) + 1

        # Hard split: if we've reached 2× target with no boundary, force split
        if current_len > target * 2:
            result.append("\n".join(current))
            current = []
            current_len = 0

    if current:
        result.append("\n".join(current))

    return result


def _multiturn_fallback(
    mc: ModelConfig,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    task_key: str,
    round_idx: int,
    round_type: str,
) -> tuple[str, float] | None:
    """Attempt multi-turn decomposed dispatch for a model that failed single-turn.

    Returns (response_text, elapsed_seconds) on success, None on failure.
    """
    chunks = _build_chunks(prompt, full_code, task_key)
    if len(chunks) < 2:
        _log(f"  {mc.label}: prompt too small for multi-turn ({len(chunks)} chunks)")
        return None

    # FFF goes in the final instruction
    final_instruction = (
        f"You now have the complete context ({len(chunks)} chunks delivered). "
        f"This is Round {round_idx} ({round_type}).\n\n"
        f"{FFF_SITUATION_TEXT}\n"
        f"Produce your findings now using the FFF format above."
    )

    _log(f"  {mc.label}: MULTI-TURN FALLBACK — {len(chunks)} chunks, "
         f"~{sum(c.chars for c in chunks):,} chars total")

    try:
        result = decomposed_dispatch(
            api=mc.api,
            model_id=mc.model_id,
            system_prompt=cdsfl_text,
            chunks=chunks,
            final_instruction=final_instruction,
            max_tokens=mc.max_tokens,
            timeout=mc.timeout * 2,  # generous timeout for multi-turn
            cdsfl_directives=cdsfl_text,
        )
        _log(f"  {mc.label}: multi-turn succeeded ({result.elapsed_s}s, "
             f"{len(result.text):,} chars)")

        # Save the decomposed result
        save_decomposed_result(result, LOGS_DIR, mc.label, round_idx)

        return result.text, result.elapsed_s

    except Exception as e:
        _log(f"  {mc.label}: multi-turn ALSO FAILED — {type(e).__name__}: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch: sequential, one model at a time (existing infrastructure)
# ─────────────────────────────────────────────────────────────────────────────

def _dispatch_single_model(
    mc: ModelConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    task_key: str,
    round_type: str,
) -> tuple[List[Finding], str | None]:
    """Dispatch to one model. Returns (findings, response_text_or_None).

    Thread-safe: uses only local state + thread-safe _log writes.
    DynamicManager is read-only during dispatch (feasibility check only).
    """
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

        # Log full model response for live monitoring
        _log(f"\n{'─' * 40} {mc.label} RESPONSE {'─' * 40}")
        _log(text)
        _log(f"{'─' * 40} /{mc.label} {'─' * 40}\n")

        model_findings = parse_findings(mc.label, round_idx, text)
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

        return model_findings, text

    except (CircuitBreakerTripped, TimeoutError, Exception) as e:
        err_type = type(e).__name__
        _log(f"  {mc.label}: {err_type} — {e}")
        _log(f"  {mc.label}: attempting multi-turn decomposed fallback...")

        # Multi-turn fallback: never exclude, always try harder
        fallback = _multiturn_fallback(
            mc, model_prompt, model_cdsfl, full_code, task_key,
            round_idx, round_type,
        )
        if fallback is not None:
            text, elapsed = fallback
            _log(f"  {mc.label}: RECOVERED via multi-turn ({elapsed:.1f}s)")
            _record_throughput(mc.label, len(model_prompt), elapsed)

            _log(f"\n{'─' * 40} {mc.label} RESPONSE (multi-turn) {'─' * 40}")
            _log(text)
            _log(f"{'─' * 40} /{mc.label} {'─' * 40}\n")

            model_findings = parse_findings(mc.label, round_idx, text)
            _log(f"  {mc.label}: {len(model_findings)} findings parsed (multi-turn)")

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
                    "decomposed": True,
                    "multiturn": True,
                    "prompt_chars": len(model_prompt),
                })

            return model_findings, text
        else:
            # Multi-turn also failed — defer immune reporting to main thread
            # (DynamicManager.apply_diagnosis is not thread-safe)
            _log(f"  {mc.label}: ALL dispatch methods exhausted")
            return [], f"__DISPATCH_FAILED__:{err_type}: {e} (multi-turn also failed)"


def _dispatch_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    task_key: str = "immune",
    round_type: str = "blind",
    benched_models: Optional[set] = None,
    all_findings: Optional[List[List[Finding]]] = None,
    dm_config: Optional[DynamicManagementConfig] = None,
) -> tuple[List[Finding], Dict[str, str]]:
    """Dispatch prompt to all models. Returns (findings, responses).

    All rounds dispatch in parallel (ThreadPoolExecutor).
    Benched models (Ω churn guard) are excluded from dispatch.

    Context budget (IT Crowd fix): each model gets its own prior-findings
    text, capped to its context budget. Models exceeding their budget get
    a CONTEXT RESET with summary-only findings.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}

    eligible = [
        mc for mc in exp_config.models
        if mc.label in BASELINE_MODELS and mc.role != "collator"
        and (not benched_models or mc.label not in benched_models)
    ]

    # Per-model prompt construction: inject context-budgeted findings
    def _make_model_prompt(mc_label: str) -> str:
        if round_idx == 0 or not all_findings or dm_config is None:
            return prompt  # blind round or no findings — use base prompt

        findings_text = _format_findings_for_model(
            all_findings, mc_label, dm_config,
        )
        budget = dm_config.context_budget_overrides.get(
            mc_label, dm_config.context_budget_chars,
        )
        is_reset = findings_text.startswith("(CONTEXT RESET:")
        _log(f"  {mc_label}: findings context {len(findings_text):,} chars "
             f"(budget={budget:,}, {'RESET' if is_reset else 'full'})")

        # Inject findings into the preamble position.
        # The base prompt has prior_findings_text="" so we append findings
        # after the blind-round marker or adaptive-round marker.
        if findings_text:
            return prompt.replace(
                "This is a BLIND round. No prior findings provided.",
                "This is a BLIND round. No prior findings provided.",
            ).replace(
                # The prompt says "blind" for R0, but for adaptive rounds
                # _build_task_prompt with empty findings just omits the
                # findings section. We prepend findings to the prompt.
                "=== ARTIFACT:",
                f"Prior findings for this task:\n\n{findings_text}\n\n"
                f"Find what was MISSED. Do not repeat known findings.\n\n"
                f"=== ARTIFACT:",
            ) if round_idx > 0 else prompt
        return prompt

    # Run 6 optimisation: ALL rounds dispatch in parallel. Adaptive rounds
    # have no within-round data dependency (models see prior-round findings
    # only). Thread safety verified: _dispatch_single_model uses only local
    # state; immune failure reporting deferred via sentinel.
    parallel = True
    deferred_failures: list[tuple[str, str]] = []  # (label, detail)

    _log(f"  Parallel dispatch: {len(eligible)} models simultaneously")
    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {
            pool.submit(
                _dispatch_single_model,
                mc, mgr, _make_model_prompt(mc.label), cdsfl_text, full_code,
                round_idx, task_key, round_type,
            ): mc.label
            for mc in eligible
        }
        for future in as_completed(future_to_label):
            label = future_to_label[future]
            try:
                model_findings, text = future.result()
                findings.extend(model_findings)
                if text is not None and not text.startswith("__DISPATCH_FAILED__:"):
                    responses[label] = text
                elif text is not None and text.startswith("__DISPATCH_FAILED__:"):
                    deferred_failures.append((label, text[20:]))
            except Exception as e:
                _log(f"  {label}: unexpected thread error — {type(e).__name__}: {e}")

    # Apply deferred immune reports on main thread (DynamicManager not thread-safe)
    for label, detail in deferred_failures:
        _report_dispatch_failure(mgr, label, round_idx, detail)

    return findings, responses


# ─────────────────────────────────────────────────────────────────────────────
# Convergence check: γ-unified (replaces multi-proxy stop signal)
#
# SymPy-verified (1 April 2026): Heaps' law dV/dn = K·β·n^{β-1} has
# identical form to Duane intensity λ(n) = α·γ·n^{γ-1}. Vocabulary
# saturation and novelty window are both discretized approximations of
# γ monitoring. The abstraction guard (Y(t) = count × mean_depth) is
# independent — γ measures count decay, not depth increase.
#
# Unified stop: γ threshold + Y(t) monotonicity check.
# ─────────────────────────────────────────────────────────────────────────────

GAMMA_CONVERGENCE_THRESHOLD = 0.5  # γ > 0.5 = steep enough decay to stop
CLUSTER_THRESHOLD = 0.33           # Calibrated from Run 8: 67 clusters at 0.33 vs 30 ground-truth IDs
                                    # Run 8 validation: γ_novel=+0.134 (vs γ_raw=-0.041)
                                    # Centroid-based (not single-linkage), avoids flaw-class mega-chaining
MIN_ROUNDS_FOR_GAMMA = 2           # Need ≥2 rounds to estimate γ

def _estimate_gamma_from_findings(all_findings: List[List[Finding]]) -> float:
    """Estimate Duane γ from per-round finding counts.

    Duane model: N(t) = α·t^β (cumulative), so β = log(N(r)/N(1)) / log(r).
    γ = 1 - β. γ > 0 means decay (convergent). γ ≈ 0 means flat (churn).
    """
    n_rounds = len(all_findings)
    if n_rounds < MIN_ROUNDS_FOR_GAMMA:
        return 0.0

    # Cumulative finding counts per round
    per_round = [len(rnd) for rnd in all_findings]
    cumulative = []
    total = 0
    for c in per_round:
        total += c
        cumulative.append(total)

    if cumulative[0] <= 0 or cumulative[-1] <= cumulative[0]:
        # No growth or no initial findings — can't estimate
        return 0.0 if cumulative[-1] == 0 else 1.0

    r = n_rounds  # last round index (1-based)
    try:
        beta = (math.log(cumulative[-1]) - math.log(cumulative[0])) / math.log(r)
        return 1.0 - beta
    except (ValueError, ZeroDivisionError):
        return 0.0


def _estimate_gamma_from_clusters(
    all_findings: List[List[Finding]],
) -> tuple[float, List[int]]:
    """Estimate Duane γ from cumulative unique finding clusters.

    Models restate findings every round, so raw per-round counts stay flat
    and γ_raw never shows convergence. This function deduplicates by tracking
    cumulative unique clusters: a finding is "novel" only if its max similarity
    to all existing cluster centroids is <= CLUSTER_THRESHOLD.

    The growth rate of unique clusters naturally declines as the defect pool
    depletes — which is exactly what γ should measure.

    Returns (gamma, novel_per_round) where novel_per_round[i] is the count
    of genuinely new findings in round i.
    """
    n_rounds = len(all_findings)
    if n_rounds < MIN_ROUNDS_FOR_GAMMA:
        return 0.0, [len(rnd) for rnd in all_findings]

    # Cluster centroids: representative findings for each unique cluster
    centroids: List[Finding] = []
    novel_per_round: List[int] = []

    for rnd_findings in all_findings:
        novel_count = 0
        for finding in rnd_findings:
            # Check similarity against all existing centroids
            is_duplicate = False
            for centroid in centroids:
                sim = _finding_similarity(finding, centroid)
                if sim > CLUSTER_THRESHOLD:
                    is_duplicate = True
                    break
            if not is_duplicate:
                # Genuinely novel finding — new cluster
                centroids.append(finding)
                novel_count += 1
        novel_per_round.append(novel_count)

    # Compute γ on cumulative novel counts (same Duane formula)
    cumulative: List[int] = []
    total = 0
    for c in novel_per_round:
        total += c
        cumulative.append(total)

    if not cumulative or cumulative[0] <= 0:
        return 0.0 if total == 0 else 1.0, novel_per_round

    if cumulative[-1] <= cumulative[0]:
        return (0.0 if cumulative[-1] == 0 else 1.0), novel_per_round

    r = n_rounds  # last round index (1-based)
    try:
        beta = (math.log(cumulative[-1]) - math.log(cumulative[0])) / math.log(r)
        return 1.0 - beta, novel_per_round
    except (ValueError, ZeroDivisionError):
        return 0.0, novel_per_round


def _compute_cognitive_yield(findings: List[Finding]) -> float:
    """Compute Y = count × mean_abstraction for a round's findings.

    Y(t) captures ascending abstraction: fewer but deeper findings
    can increase total cognitive yield even as count drops.
    """
    if not findings:
        return 0.0
    mean_h = sum(f.abstraction_index for f in findings) / len(findings)
    return len(findings) * mean_h


def _check_convergence(
    all_findings: List[List[Finding]],
    round_idx: int,
) -> tuple[bool, str, Optional[List[int]]]:
    """γ-unified convergence check with Y(t) abstraction guard.

    Uses γ_novel (cluster-based) for the convergence decision.
    γ_raw (raw counts) is logged for comparison but not used for decisions.

    Stop when γ_novel exceeds threshold AND Y(t) is not ascending.
    Returns (converged: bool, reason: str, novel_per_round: list | None).
    """
    if round_idx < 1:
        return False, "min_rounds", None

    if len(all_findings) < MIN_ROUNDS_FOR_GAMMA:
        return False, "insufficient_data", None

    current = all_findings[-1]
    if not current:
        return True, "zero_findings", None

    # Estimate both γ values
    gamma_raw = _estimate_gamma_from_findings(all_findings)
    gamma_novel, novel_per_round = _estimate_gamma_from_clusters(all_findings)
    _log(f"  Convergence: γ_raw={gamma_raw:.3f}, γ_novel={gamma_novel:.3f} "
         f"(threshold={GAMMA_CONVERGENCE_THRESHOLD})")
    _log(f"  Novel findings per round: {novel_per_round}")

    # Use γ_novel (cluster-deduplicated) for the convergence decision
    if gamma_novel < GAMMA_CONVERGENCE_THRESHOLD:
        return False, (f"continuing(γ_novel={gamma_novel:.3f}"
                       f"<{GAMMA_CONVERGENCE_THRESHOLD})"), novel_per_round

    # γ_novel says converged — but check Y(t) abstraction guard.
    # If Y(t) is still ascending (findings getting deeper even as count
    # drops), we should NOT stop — the system is in ascending abstraction
    # mode, which is the most valuable analytical phase.
    if len(all_findings) >= 2:
        y_current = _compute_cognitive_yield(all_findings[-1])
        y_previous = _compute_cognitive_yield(all_findings[-2])
        _log(f"  Abstraction guard: Y(t-1)={y_previous:.2f}, Y(t)={y_current:.2f}")

        if y_current > y_previous * 1.1:  # 10% margin to avoid noise
            return False, (f"γ_novel_converged({gamma_novel:.3f}) but Y(t) ascending "
                          f"({y_previous:.2f}→{y_current:.2f})"), novel_per_round

    return True, f"γ_novel_converged({gamma_novel:.3f})", novel_per_round


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint/resume: survives process death, context exhaustion, Ctrl-C
# ─────────────────────────────────────────────────────────────────────────────

CHECKPOINT_FILE = "checkpoint.json"

def _save_checkpoint(
    logs_dir: Path,
    round_idx: int,
    all_findings: List[List[Finding]],
    result: Dict[str, Any],
) -> None:
    """Save checkpoint after each completed round."""
    # Serialise findings to JSON-safe format
    serialised_findings = []
    for rnd in all_findings:
        serialised_findings.append([
            {
                "finding_id": f.finding_id,
                "model_id": f.model_id,
                "round_idx": f.round_idx,
                "flaw_class": f.flaw_class,
                "severity": f.severity,
                "abstraction_index": f.abstraction_index,
                "description": f.description,
                "proposed_fix": f.proposed_fix,
                "verified": f.verified,
            }
            for f in rnd
        ])

    checkpoint = {
        "completed_round": round_idx,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "all_findings": serialised_findings,
        "result_so_far": result,
    }

    cp_path = logs_dir / CHECKPOINT_FILE
    cp_path.write_text(
        json.dumps(checkpoint, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _log(f"  Checkpoint saved: round {round_idx} → {cp_path.name}")


def _load_checkpoint(logs_dir: Path) -> Optional[Dict[str, Any]]:
    """Load checkpoint if it exists. Returns None if no checkpoint."""
    cp_path = logs_dir / CHECKPOINT_FILE
    if not cp_path.exists():
        return None

    try:
        checkpoint = json.loads(cp_path.read_text(encoding="utf-8"))
        _log(f"  Checkpoint found: round {checkpoint['completed_round']} "
             f"({checkpoint['timestamp']})")
        return checkpoint
    except (json.JSONDecodeError, KeyError) as e:
        _log(f"  Checkpoint corrupt ({e}), starting fresh")
        return None


def _restore_findings(checkpoint: Dict[str, Any]) -> List[List[Finding]]:
    """Reconstruct Finding objects from checkpoint data."""
    all_findings = []
    for rnd_data in checkpoint.get("all_findings", []):
        rnd = [
            Finding(
                finding_id=f["finding_id"],
                model_id=f["model_id"],
                round_idx=f["round_idx"],
                flaw_class=f["flaw_class"],
                severity=f["severity"],
                abstraction_index=f["abstraction_index"],
                description=f.get("description", ""),
                proposed_fix=f.get("proposed_fix", ""),
                verified=f.get("verified", False),
            )
            for f in rnd_data
        ]
        all_findings.append(rnd)
    return all_findings


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


def run_confer(
    exp_config: ExperimentConfig,
    cdsfl_text: str,
    resume: bool = False,
) -> Dict[str, Any]:
    """Run the baseline confer: blind R1 → adaptive R2+ → stop on convergence."""
    _log("=" * 60)
    _log("BASELINE CONFER RUN 9: CC2 + CX + Gemini + DeepSeek + ChatGPT, FFF + CDSFL + multi-turn fallback")
    _log(f"  Max rounds: {MAX_ROUNDS}")
    _log(f"  Wall clock cap: {WALL_CLOCK_CAP_S}s")
    _log(f"  Task: immune ({len(IMMUNE_SOURCE_FILES)} source files, ~244K chars)")
    _log(f"  Logs: {LOGS_DIR}")
    _log("=" * 60)

    # Load test articles — Run 9: concatenate actual implementation files.
    # The re-export shim (dynamic_management.py) is only 78 lines / 3785 chars.
    # Models need the real implementation (~244K chars total across 5 files).
    # Decomposed dispatch handles the size for context-limited models.
    full_code_parts = []
    total_raw = 0
    for src_path in IMMUNE_SOURCE_FILES:
        src_text = src_path.read_text(encoding="utf-8")
        rel = src_path.relative_to(REPO_ROOT)
        full_code_parts.append(f"=== FILE: {rel} ({len(src_text):,} chars) ===\n{src_text}")
        total_raw += len(src_text)
    full_code = "\n\n".join(full_code_parts)
    _log(f"  Immune source files: {len(IMMUNE_SOURCE_FILES)} files, "
         f"{total_raw:,} raw chars → {len(full_code):,} chars with headers")
    math_appendix = MATH_APPENDIX_PATH.read_text(encoding="utf-8")
    verification_chain = VERIFICATION_CHAIN_PATH.read_text(encoding="utf-8")
    interface_summary = ""
    if INTERFACE_SUMMARY_PATH.exists():
        interface_summary = INTERFACE_SUMMARY_PATH.read_text(encoding="utf-8")

    # Build DynamicManager
    # Pre-seed Codex and DeepSeek for decomposition. Codex CLI overhead
    # makes full-artifact dispatch impractical (370-556s observed in Exp 17).
    # DeepSeek always decomposed (Exp 16 unanimous). Without pre-seeding,
    # they get the full 122K prompt, hit timeout, and only THEN fall back
    # to multi-turn — wasting 600-900s per model per round.
    dm_config = DynamicManagementConfig(
        pre_decompose_models={"Codex", "DeepSeek"},
        no_exclusion_mode=True,  # Runner overrides ABORT → decomposed fallback
    )
    dm_config.max_rounds = MAX_ROUNDS
    model_specs = build_model_specs(exp_config)
    mgr = DynamicManager(model_specs, dm_config)
    telemetry = RoundTelemetry(LOGS_DIR)

    all_findings: List[List[Finding]] = []
    all_responses: List[Dict[str, str]] = []
    amp_history = AmplificationHistory()  # per-model A tracking (observation only)
    # Layer 3: Adaptive Question Optimiser (passive for Run 7, active for Run 8+)
    question_optimiser = AdaptiveQuestionOptimiser(active=True)
    # Compound objective Ω churn guard (Run 6 → Run 7)
    omega_history: Dict[str, List[float]] = {}  # model → [Ω per round]
    benched_models: set[str] = set()
    resolution_S = dm_config.resolution_threshold
    omega_tau = dm_config.convergence_omega_tau
    omega_window = dm_config.convergence_omega_window
    experiment_start = time.monotonic()
    start_round = 0
    result = {
        "experiment": "baseline_confer_run9",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "models": [mc.label for mc in exp_config.models
                    if mc.label in BASELINE_MODELS],
        "task": "immune",
        "max_rounds": MAX_ROUNDS,
        "rounds": [],
    }

    # Resume from checkpoint if available
    if resume:
        checkpoint = _load_checkpoint(LOGS_DIR)
        if checkpoint:
            all_findings = _restore_findings(checkpoint)
            result = checkpoint.get("result_so_far", result)
            start_round = checkpoint["completed_round"] + 1
            total_restored = sum(len(rnd) for rnd in all_findings)
            _log(f"  RESUMED from round {start_round} "
                 f"({total_restored} findings across "
                 f"{len(all_findings)} completed rounds)")

            # Replay findings into DynamicManager for state consistency
            for ri, rnd in enumerate(all_findings):
                replay_responses: Dict[str, ModelResponse] = {}
                for label in BASELINE_MODELS:
                    label_findings = [f for f in rnd if f.model_id == label]
                    if label_findings:
                        replay_responses[label] = ModelResponse(
                            model_id=label, round_idx=ri,
                            content="[restored from checkpoint]",
                            response_time=0.0, parseable=True,
                            format_compliant=True,
                            finding_count=len(label_findings),
                            mean_abstraction=(
                                sum(f.abstraction_index for f in label_findings)
                                / len(label_findings)
                            ),
                        )
                if replay_responses:
                    mgr.process_round(
                        replay_responses, rnd, [],
                        round_cost=0.0, duration=0.0,
                    )
            _log(f"  DynamicManager state replayed through round "
                 f"{start_round - 1}")
        else:
            _log("  No checkpoint found, starting fresh")

    for round_idx in range(start_round, MAX_ROUNDS):
        round_start = time.monotonic()
        wall_elapsed = round_start - experiment_start
        if wall_elapsed > WALL_CLOCK_CAP_S:
            _log(f"\nWALL CLOCK CAP reached ({wall_elapsed:.0f}s). Stopping.")
            break

        _log(f"\n{'─' * 60}")
        round_type = "blind" if round_idx == 0 else "adaptive"
        _log(f"Round {round_idx} ({round_type})")
        _log(f"{'─' * 60}")

        # Build base prompt (without findings — findings are per-model)
        base_prompt = _build_task_prompt(
            task_key="immune",
            round_label=f"R{round_idx} ({round_type})",
            round_type=round_type,
            code=full_code,
            math_appendix=math_appendix,
            verification_chain=verification_chain,
            interface_summary=interface_summary,
            prior_findings_text="",  # injected per-model in dispatch
        )

        # Layer 3: inject focus directive if optimiser is active
        focus_directive = question_optimiser.get_directive_text()
        if focus_directive:
            base_prompt = focus_directive + base_prompt
            _log(f"  AQO: focus directive injected ({len(focus_directive)} chars)")

        _log(f"  Base prompt (no findings): {len(base_prompt):,} chars")

        # ── Observation-only: γ_input measurement ────────────────────
        gamma_input_result = compute_gamma_input(base_prompt)
        dispatch_rec = recommend_dispatch(
            len(base_prompt), gamma_input_result.gamma,
            r_squared=gamma_input_result.r_squared,
        )
        _log(f"  γ_input: β={gamma_input_result.beta:.3f}, "
             f"γ={gamma_input_result.gamma:.3f}, "
             f"R²={gamma_input_result.r_squared:.3f}, "
             f"windows={gamma_input_result.n_windows}")
        _log(f"  Dispatch recommendation (observation): "
             f"{dispatch_rec.strategy} — {dispatch_rec.reasoning}")

        # Dispatch (benched models excluded from Ω churn guard)
        # Each model gets its own context-budgeted findings injection.
        findings, responses = _dispatch_round(
            exp_config, mgr, base_prompt, cdsfl_text, full_code, round_idx,
            round_type=round_type,
            benched_models=benched_models,
            all_findings=all_findings,
            dm_config=dm_config,
        )

        # Safety check
        problem = _safety_check(responses, round_idx)
        if problem:
            _log(f"\n*** PULL THE PLUG: {problem} ***")
            result["terminated"] = problem
            break

        all_findings.append(findings)
        all_responses.append(responses)

        # ── Quality gate (observation only) ──────────────────────────
        _immune_source_paths = [
            str(REPO_ROOT / "bench" / "dm" / "_immune.py"),
            str(REPO_ROOT / "bench" / "dm" / "_failure_handler.py"),
            str(REPO_ROOT / "bench" / "dm" / "_manager.py"),
        ]
        qg_result = run_quality_gate(
            findings,
            [f for rnd in all_findings[:-1] for f in rnd],  # exclude current round
            source_paths=_immune_source_paths,
            pm_enabled=False,
        )
        _log(f"  Quality gate: {qg_result.dedup_count} duplicates, "
             f"{len(qg_result.sympy_log)} SymPy checks, "
             f"{len(qg_result.ast_log)} AST checks")
        if qg_result.dedup_count > 0:
            _log(f"    Dedup rate: {qg_result.dedup_count}/{len(findings)} = "
                 f"{qg_result.dedup_count/max(1,len(findings)):.0%}")

        # ── Immune pipeline (Run 9: 6-cell parallel verification, active) ──
        immune_result = run_immune_pipeline(
            findings,
            [f for rnd in all_findings[:-1] for f in rnd],
            source_paths=_immune_source_paths,
            observation_only=False,  # Run 9+: active immune filtering
            ct_enabled=True,         # Run 9+: claude CLI tool enabled
            # tau_sim uses calibrated default from _types.py (0.33)
            # Run 9 bug: hardcoded 0.8 here overrode the calibration
        )
        _log(f"  Immune pipeline: {immune_result.rejection_rate:.0%} rejection rate, "
             f"autoimmune={'YES' if immune_result.autoimmune_flag else 'no'}")
        _log(f"    Tools: {immune_result.tool_usage}")
        _log(f"    Timings: {immune_result.stage_timings}")

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
            "quality_gate": {
                "dedup_count": qg_result.dedup_count,
                "dedup_rate": round(qg_result.dedup_count / max(1, len(findings)), 3),
                "sympy_checks": len(qg_result.sympy_log),
                "ast_checks": len(qg_result.ast_log),
                "stage_timings": qg_result.stage_timings,
            },
            "immune_pipeline": {
                "rejection_rate": immune_result.rejection_rate,
                "autoimmune_flag": immune_result.autoimmune_flag,
                "observation_only": immune_result.observation_only,
                "tool_usage": immune_result.tool_usage,
                "stage_timings": immune_result.stage_timings,
                "final_verdicts": {
                    k: v for k, v in immune_result.final_verdicts.items()
                },
            },
        }
        # Complexity observation data added after γ measurement below
        result["rounds"].append(round_data)

        _log(f"\n  Round {round_idx} summary: {len(findings)} findings from "
             f"{len(responses)} models ({round_elapsed:.1f}s)")
        for label in sorted(responses.keys()):
            model_count = len([f for f in findings if f.model_id == label])
            _log(f"    {label}: {model_count} findings")

        # ── Observation-only: γ_output + amplification per model ─────
        round_amplification = {}
        for label in sorted(responses.keys()):
            model_findings = [f for f in findings if f.model_id == label]
            if not model_findings:
                continue
            descriptions = [f.description for f in model_findings]
            gamma_out = compute_gamma_output(descriptions)
            amp = compute_amplification(gamma_input_result, gamma_out)
            amp_history.record(label, amp)
            round_amplification[label] = {
                "gamma_output": amp.gamma_output,
                "beta_output": amp.beta_output,
                "A": amp.A,
                "compound_obj": amp.compound_objective,
                "dist_from_optimal": amp.distance_from_optimal,
                "n_findings": len(model_findings),
                "r_sq_output": gamma_out.r_squared,
            }
            est_A = amp_history.estimated_A(label)
            _log(f"    {label}: γ_out={amp.gamma_output:.3f}, "
                 f"A={amp.A:.3f}, obj={amp.compound_objective:.3f}, "
                 f"est_A={est_A:.3f}" if est_A else
                 f"    {label}: γ_out={amp.gamma_output:.3f}, "
                 f"A={amp.A:.3f}, obj={amp.compound_objective:.3f}")
        round_data_complexity = {
            "gamma_input": {
                "beta": round(gamma_input_result.beta, 4),
                "gamma": round(gamma_input_result.gamma, 4),
                "r_squared": round(gamma_input_result.r_squared, 4),
                "n_windows": gamma_input_result.n_windows,
            },
            "dispatch_recommendation": dispatch_rec.strategy,
            "per_model_amplification": round_amplification,
        }
        round_data["complexity"] = round_data_complexity

        # ── Compound objective Ω churn guard (active) ──────────────────
        # Filter findings by resolution threshold S, then compute Ω.
        # Per-model benching when Ω < τ for omega_window consecutive rounds.
        for label in sorted(responses.keys()):
            model_findings = [f for f in findings if f.model_id == label]
            # Filter by resolution threshold S
            filtered = [f for f in model_findings
                        if getattr(f, "severity", 0.5) >= resolution_S]
            if not filtered:
                # No findings above threshold — Ω = 0 (exhausted)
                omega_val = 0.0
            else:
                descriptions = [f.description for f in filtered]
                gamma_out = compute_gamma_output(descriptions)
                amp = compute_amplification(gamma_input_result, gamma_out)
                omega_val = amp.compound_objective

            omega_history.setdefault(label, []).append(omega_val)

            # Check for benching
            history = omega_history[label]
            if (len(history) >= omega_window
                    and all(v < omega_tau for v in history[-omega_window:])
                    and label not in benched_models):
                benched_models.add(label)
                _log(f"  ★ BENCHED {label}: Ω < {omega_tau} for "
                     f"{omega_window} consecutive rounds "
                     f"(last {omega_window}: {[f'{v:.3f}' for v in history[-omega_window:]]})")

        # Add Ω data to round record
        round_data["omega"] = {
            label: omega_history.get(label, [0.0])[-1]
            for label in responses
        }
        round_data["benched_models"] = sorted(benched_models)

        # ── Layer 3: Adaptive Question Optimiser observation ─────────
        round_omega_for_optimiser = {
            label: omega_history.get(label, [0.0])[-1]
            for label in responses
        }
        q_outcome = question_optimiser.observe(round_idx, base_prompt, round_omega_for_optimiser)
        q_rec = question_optimiser.recommend()
        if q_rec and q_rec.reasoning:
            _log(f"  AQO: {q_rec.reasoning}")
            if q_rec.directive_text:
                _log(f"  AQO directive ({'ACTIVE' if question_optimiser.active else 'PASSIVE'}): "
                     f"{q_rec.directive_text[:80]}...")
        round_data["question_optimiser"] = {
            "features": {
                "referential_density": q_outcome.features.referential_density,
                "novelty_score": q_outcome.features.novelty_score,
                "specificity": q_outcome.features.specificity,
            },
            "mean_omega": q_outcome.mean_omega,
            "recommendation": q_rec.reasoning if q_rec else None,
            "confidence": q_rec.confidence if q_rec else None,
        }

        # Check for run termination: all non-benched models below threshold
        active_labels = set(responses.keys()) - benched_models
        if not active_labels and len(responses) > 0:
            _log(f"\n  ★ ALL MODELS BENCHED — run converged via Ω churn guard")
            result["converged_at"] = round_idx
            result["convergence_reason"] = "omega_churn_guard"
            result["benched_models"] = sorted(benched_models)
            break

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

        # Feed findings to DynamicManager — guarded against terminal FSM.
        # Run 4/9 bug: FSM enters FAILURE state from ABORT/EXCLUDE cascade.
        # The DM section is optional — convergence check MUST always run.
        dm_result = None
        try:
            dm_result = mgr.process_round(
                rn_responses,
                findings,
                [],  # no explicit task objects needed for convergence tracking
                round_cost=1.0,
                duration=round_elapsed,
            )
        except RuntimeError as e:
            if "terminal" in str(e).lower() or "FSM" in str(e):
                _log(f"  DM: FSM TERMINAL — {e}")
                _log(f"  DM: continuing without DM feedback (data preserved)")
            else:
                raise  # re-raise if it's a different RuntimeError

        # Process DM result if available (not available when FSM is terminal)
        dm_converged = False
        if dm_result is not None:
            # Log immune diagnostics from DynamicManager
            if dm_result.recovery_actions:
                _log(f"  Immune: {dm_result.recovery_actions}")

                # NO-EXCLUSION POLICY: intercept EXCLUDE/ABORT signals.
                for model_id, action_name in dm_result.recovery_actions.items():
                    if action_name in ("EXCLUDE", "ABORT"):
                        _log(f"  NO-EXCLUSION: overriding {action_name} for "
                             f"{model_id} → pre_decompose + multi-turn fallback")
                        mgr.config.pre_decompose_models.add(model_id)

            _log(f"  DM: kappa={dm_result.convergence_metric:.3f}, "
                 f"mu={dm_result.marginal_value:.3f}, "
                 f"converged={dm_result.converged}, stop={dm_result.stop}")
            if dm_result.converged:
                _log(f"\n  DM CONVERGED at round {round_idx}")
                result["converged_at"] = round_idx
                result["convergence_reason"] = "dm_converged"
                dm_converged = True
            elif dm_result.stop:
                _log(f"\n  DM STOP at round {round_idx}: diminishing returns")
                result["converged_at"] = round_idx
                result["convergence_reason"] = "dm_diminishing_returns"
                dm_converged = True

        # γ-unified convergence check — ALWAYS runs regardless of FSM state.
        # Run 9 bug: `continue` in FSM exception handler skipped this for
        # 15 of 20 rounds, making convergence detection impossible.
        converged, reason, novel_per_round = _check_convergence(all_findings, round_idx)
        _log(f"  Convergence (γ-unified): {reason}")

        # Finding-ID convergence: if zero novel base IDs for N consecutive
        # rounds, the models are restating. This is the simplest and most
        # reliable convergence signal — the models self-label their findings.
        if novel_per_round is not None:
            round_data["novelty"] = {
                "novel_this_round": novel_per_round[-1] if novel_per_round else 0,
                "novel_per_round": novel_per_round,
                "total_unique_clusters": sum(novel_per_round),
            }
            # Check for N consecutive zero-novel rounds
            zero_novel_window = 3  # declare convergence after 3 rounds of no novelty
            if len(novel_per_round) >= zero_novel_window:
                tail = novel_per_round[-zero_novel_window:]
                if all(n == 0 for n in tail):
                    _log(f"  FINDING-ID CONVERGENCE: {zero_novel_window} consecutive "
                         f"rounds with zero novel findings")
                    converged = True
                    reason = (f"finding_id_exhaustion({zero_novel_window}_rounds_"
                              f"zero_novel)")

        # Checkpoint after every round — survives process death
        _save_checkpoint(LOGS_DIR, round_idx, all_findings, result)

        if dm_converged or converged:
            _log(f"\n  CONVERGED at round {round_idx}: {reason}")
            if "converged_at" not in result:
                result["converged_at"] = round_idx
                result["convergence_reason"] = reason
            break

    if "converged_at" not in result:
        result["termination_reason"] = "MAX_ROUNDS"
        _log(f"\n  MAX_ROUNDS ({MAX_ROUNDS}) reached without convergence")

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

    # Decay analysis: γ estimation
    gamma_final = _estimate_gamma_from_findings(all_findings)
    per_round_counts = [len(rnd) for rnd in all_findings]
    result["gamma"] = round(gamma_final, 4)
    result["per_round_counts"] = per_round_counts

    # Cognitive yield Y(t) per round
    y_per_round = [round(_compute_cognitive_yield(rnd), 3) for rnd in all_findings]
    result["cognitive_yield_per_round"] = y_per_round

    # Amplification history summary (observation only — not used for dispatch)
    amp_summary = {}
    for model_id in sorted(amp_history.records.keys()):
        est_a = amp_history.estimated_A(model_id)
        est_c = amp_history.estimated_compound(model_id)
        amp_summary[model_id] = {
            "estimated_A": round(est_a, 4) if est_a else None,
            "estimated_compound": round(est_c, 4) if est_c else None,
            "n_observations": len(amp_history.records[model_id]),
        }
    result["amplification_summary"] = amp_summary
    _log(f"\n  Amplification summary (observation):")
    for mid, s in amp_summary.items():
        _log(f"    {mid}: A={s['estimated_A']}, "
             f"obj={s['estimated_compound']}, "
             f"n={s['n_observations']}")

    # Omega churn guard summary
    result["omega_history"] = {k: [round(v, 4) for v in vals]
                               for k, vals in omega_history.items()}
    result["question_optimiser"] = question_optimiser.summary()
    result["benched_models"] = sorted(benched_models)
    result["resolution_threshold"] = resolution_S
    result["omega_tau"] = omega_tau
    if benched_models:
        _log(f"\n  Ω churn guard: {len(benched_models)} models benched")
        for mid in sorted(benched_models):
            history = omega_history.get(mid, [])
            _log(f"    {mid}: final Ω trajectory = "
                 f"{[f'{v:.3f}' for v in history[-5:]]}")

    # ── Popper's Degree of Corroboration C(H,E) ──────────────────────
    #
    # C(H,E) ∝ (P(E|H) - P(E)) / (P(E|H) + P(E))
    #
    # P(E|H) = detection rate under CDSFL methodology (this run)
    # P(E)   = base rate from Control condition (Bench Run 1)
    #
    # SymPy-verified 1 April 2026: domain [-1,1], monotonic in P(E|H),
    # reduces to 0 when P(E|H)=P(E), ±1 at extremes.
    #
    # Control baseline from Bench Run 1 smoke test (24 March 2026):
    #   Control condition: 10 unique HARD findings in 5 rounds = 2.0/round
    #   CDSFL+HIL: 43 unique HARD findings in 5 rounds = 8.6/round
    # These are the only calibration points available pre-Run 2.
    #
    # We compute C(H,E) using per-round finding rates as the observable.
    CONTROL_BASELINE_RATE = 2.0  # findings/round, from smoke test Control

    if all_findings:
        cdsfl_rate = total_findings / len(all_findings)
        pe_h = cdsfl_rate   # P(E|H): detection rate under CDSFL
        pe = CONTROL_BASELINE_RATE  # P(E): base rate without methodology

        if pe_h + pe > 0:
            c_he = (pe_h - pe) / (pe_h + pe)
        else:
            c_he = 0.0

        result["popper_corroboration"] = {
            "C_HE": round(c_he, 4),
            "P_E_given_H": round(pe_h, 4),
            "P_E": round(pe, 4),
            "interpretation": (
                "strong_corroboration" if c_he > 0.5 else
                "moderate_corroboration" if c_he > 0.2 else
                "weak_corroboration" if c_he > 0 else
                "no_effect" if c_he == 0 else
                "methodology_harmful"
            ),
            "note": ("C(H,E) = Popper 1954 degree of corroboration. "
                     "Control baseline from Bench Run 1 smoke test "
                     "(10 HARD findings / 5 rounds = 2.0/round). "
                     "Recalibrate after Bench Run 2 with full Control data."),
        }
    else:
        result["popper_corroboration"] = {"C_HE": None, "note": "no_data"}

    # Save results
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = LOGS_DIR / "baseline_confer_report.json"
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    _log(f"\n{'=' * 60}")
    _log(f"BASELINE CONFER — {len(all_findings)} ROUNDS COMPLETE")
    _log(f"  Rounds: {len(all_findings)}")
    _log(f"  Total findings: {total_findings}")
    _log(f"  Per model: {per_model_totals}")
    _log(f"  Per round: {per_round_counts}")
    _log(f"  γ (Duane): {gamma_final:.3f}")
    _log(f"  Y(t): {y_per_round}")
    c_he_val = result.get("popper_corroboration", {}).get("C_HE")
    if c_he_val is not None:
        _log(f"  C(H,E) Popper: {c_he_val:.4f} "
             f"({result['popper_corroboration']['interpretation']})")
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
    resume = "--resume" in sys.argv

    if mode == "preflight":
        ok = run_preflight(exp_config, cdsfl_text)
        sys.exit(0 if ok else 1)

    elif mode in ("run", "--resume"):
        # Preflight first (skip on resume — models were already verified)
        if not resume:
            ok = run_preflight(exp_config, cdsfl_text)
            if not ok:
                _log("\nPREFLIGHT FAILED. Aborting.")
                sys.exit(1)
            _log("\nPreflight passed. Starting confer in 5s...")
            time.sleep(5)
        else:
            _log("\nRESUME mode — skipping preflight")

        result = run_confer(exp_config, cdsfl_text, resume=resume)

        if result.get("terminated"):
            _log(f"\nExperiment terminated: {result['terminated']}")
            sys.exit(2)

        sys.exit(0)

    else:
        print(f"Unknown mode: {mode}. Use: preflight | run | --resume")
        sys.exit(1)


if __name__ == "__main__":
    main()
