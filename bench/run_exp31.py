#!/usr/bin/env python3
"""Experiment 31: Post-Fix Convergence Validation.

Re-reviews the same 3 persistence layer files as Exp 31 (verification_chain.py,
insect_brain.py, immune_agents.py) AFTER 39 bug fixes and 3 architectural
changes were applied from Exp 31 findings.

Purpose: Demonstrate genuine epistemic convergence. Models are told which
bugs were fixed, told NOT to rediscover them, and asked to:
  1. Verify that applied fixes hold (no regressions)
  2. Find any residual bugs the fixes missed
  3. Identify new issues introduced by the fixes themselves

Key differences from Exp 31:
  - Bug-closed gate active in NK cell (first verified fix wins)
  - Programmatic fix evaluation (Stage 4) wired into immune pipeline
  - Auto-escalation (Stage 5) for unfixable bugs
  - BUDGET_EXHAUSTED terminates honestly (not false convergence)
  - Context formatting shows CLOSED/ESCALATED/PENDING/OPEN status
  - Base prompt includes summary of 39 applied fixes

Architecture: identical to Exp 31 (insect brain relay, endocrine layer,
5-model parallel dispatch, directed messaging, immune pipeline, convergence
detection, checkpoint/resume).

Models:
  - CC2 (Claude Opus 4.6 via OpenRouter)
  - Codex (GPT-5.4 via codex exec CLI)
  - Gemini (Gemini 3.1 Pro via Google SDK)
  - DeepSeek (DeepSeek Reasoner via DeepSeek API)
  - ChatGPT (GPT-5.4 via OpenRouter)

Usage:
    python3 bench/run_exp31.py [preflight|run|--resume]
    python3 bench/run_exp31.py run --relay-mode directed --pattern fff
    python3 bench/run_exp31.py run --pattern meta_structured
    python3 bench/run_exp31.py run --relay-mode conversational

    preflight       — verify all 5 models respond
    run             — full experiment (preflight + confer rounds)
    --resume        — resume from last checkpoint
    --pattern NAME  — interaction pattern preset (default: fff)
                      Options: fff, meta_structured, conversational,
                      three_layer_schema, unconstrained
    --relay-mode M  — how the brain relays between models (default: directed)
                      findings: parsed findings only (IDs, severities, descriptions)
                      conversational: full model responses (reasoning chains visible)
                      directed: conversational + @tag directed inter-model messaging
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from copy import deepcopy
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
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

def _find_or_create_logs_dir(resume: bool = False) -> Path:
    """Find existing exp31 logs dir for resume, or create a new one."""
    if resume:
        logs_root = REPO_ROOT / "bench" / "logs"
        candidates = sorted(
            logs_root.glob("exp31_postfix_*"),
            key=lambda p: p.name,
            reverse=True,
        )
        for c in candidates:
            if (c / "checkpoint.json").exists():
                return c
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "bench" / "logs" / f"exp31_postfix_{ts}"


# Default — overridden in main() for resume
LOGS_DIR = REPO_ROOT / "bench" / "logs" / "exp31_postfix_latest"

MAX_ROUNDS = 15          # Same as Exp 29
WALL_CLOCK_CAP_S = 6 * 3600  # 6 hours

# Test article: same 3 files as Exp 29 (re-reviewing after fixes applied)
SOURCE_FILES = [
    REPO_ROOT / "bench" / "verification_chain.py",   # Merkle tree persistence
    REPO_ROOT / "bench" / "insect_brain.py",          # relay module under test
    REPO_ROOT / "bench" / "immune_agents.py",         # 6-cell pipeline (context)
]

# 5-model set
BASELINE_MODELS = {"CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"}

# Default interaction pattern (overridable via --pattern)
DEFAULT_PATTERN = "fff"

# Default relay mode — DIRECTED for Exp 31 (was conversational in Exp 29)
DEFAULT_RELAY_MODE = "directed"

# Model roster for awareness preamble
MODEL_ROSTER = {
    "CC2": "Claude Opus 4.6 (Anthropic)",
    "Codex": "GPT-5.4 Codex (OpenAI)",
    "Gemini": "Gemini 3.1 Pro (Google)",
    "DeepSeek": "DeepSeek Reasoner (DeepSeek)",
    "ChatGPT": "GPT-5.4 (OpenAI)",
}

# Multi-turn chunk target for decomposed dispatch
MULTITURN_CHUNK_TARGET = 30_000

# ─────────────────────────────────────────────────────────────────────────────
# Good Enough principle — convergence on fixes, not endless alternatives
# ─────────────────────────────────────────────────────────────────────────────
# Applies to all domains, not just software. When multiple agents agree an
# issue exists, they must converge on the simplest sufficient solution rather
# than endlessly proposing alternatives. This is Voltaire's "le mieux est
# l'ennemi du bien" — the Principle of Good Enough.
# See: https://en.wikipedia.org/wiki/Principle_of_good_enough

_GOOD_ENOUGH_INSTRUCTION = (
    "CONVERGENCE ON SOLUTIONS (MANDATORY):\n"
    "When another model has already identified an issue AND proposed a fix, "
    "you have exactly three valid responses:\n"
    "  1. AGREE — confirm the fix is correct and sufficient. The issue is closed. "
    "Move on to finding NEW issues.\n"
    "  2. CHALLENGE — demonstrate with concrete evidence that the proposed fix "
    "is INCORRECT (introduces a regression, misses the root cause, or violates "
    "a constraint). Then propose your alternative.\n"
    "  3. EXTEND — show that the fix is correct but INCOMPLETE (misses a "
    "downstream consequence or edge case). Propose the minimal addition.\n\n"
    "You may NOT propose an alternative fix simply because yours is 'better', "
    "'more elegant', or 'more robust' when an existing fix is correct and "
    "sufficient. The simplest sufficient fix wins. First correct solution "
    "closes the issue.\n\n"
    "This is the Principle of Good Enough. Endless iteration on alternative "
    "solutions to solved problems is wasted compute and prevents convergence. "
    "Your value is in finding what is STILL WRONG, not in re-solving what "
    "is already fixed.\n\n"
    "FINDING DEDUPLICATION (MANDATORY):\n"
    "Before filing a new finding, check whether another model has already "
    "reported the same underlying issue. If your finding overlaps with an "
    "existing one, you MUST explicitly merge rather than filing a separate "
    "entry. State: 'This overlaps with [Model]_[FindingID]. I confirm their "
    "finding and merge.' If your finding adds new evidence or traces a new "
    "consequence, extend the existing finding rather than creating a duplicate. "
    "Five separate finding IDs for one bug is five times the wasted compute "
    "and zero additional insight.\n\n"
)


# ─────────────────────────────────────────────────────────────────────────────
# Composer integration
# ─────────────────────────────────────────────────────────────────────────────

def compose_for_model(model_label: str, pattern_name: str) -> ComposedDirectiveSet:
    """Compose directive set with selected interaction pattern for a model."""
    composer_model = COMPOSER_MODEL_MAP.get(model_label, model_label)
    situation = build_interaction_pattern(pattern_name)
    return compose(
        task_domain="software",
        model=composer_model,
        situation=situation,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Multi-turn decomposed dispatch (reused from baseline confer)
# ─────────────────────────────────────────────────────────────────────────────

def _build_chunks(prompt: str, full_code: str) -> list[DecomposedChunk]:
    """Split prompt into sequential file-delivery chunks."""
    chunks: list[DecomposedChunk] = []

    if "=== ARTIFACT" in prompt:
        preamble, rest = prompt.split("=== ARTIFACT", 1)
    else:
        preamble = prompt
        rest = ""

    preamble_text = preamble.strip()
    artifact_text = rest if rest else full_code

    if "=== FILE:" in artifact_text:
        import re
        n_files = artifact_text.count("=== FILE:")
        preamble_text += (
            f"\n\nYou will receive {n_files} source files delivered one at a "
            f"time. Read each file carefully in sequential order. Only begin "
            f"your analysis once you have seen all files.\n"
        )
        chunks.append(DecomposedChunk(preamble_text, label="Preamble + instructions"))

        file_blocks = re.split(r"(?==== FILE:)", artifact_text)
        for block in file_blocks:
            block = block.strip()
            if not block or not block.startswith("=== FILE:"):
                continue
            header_match = re.match(r"=== FILE: (.+?) ===", block)
            label = header_match.group(1) if header_match else "Source file"

            if len(block) > MULTITURN_CHUNK_TARGET:
                lines = block.split("\n")
                current: list[str] = []
                current_len = 0
                part_idx = 0
                for line in lines:
                    is_boundary = (
                        line.startswith("class ") or
                        (line.startswith("def ") and not line.startswith("    "))
                    )
                    if current_len > MULTITURN_CHUNK_TARGET and (is_boundary or line.strip() == ""):
                        part_idx += 1
                        chunks.append(DecomposedChunk(
                            "\n".join(current), label=f"{label} part {part_idx}"))
                        current = []
                        current_len = 0
                    current.append(line)
                    current_len += len(line) + 1
                if current:
                    part_idx += 1
                    chunks.append(DecomposedChunk(
                        "\n".join(current), label=f"{label} part {part_idx}"))
            else:
                chunks.append(DecomposedChunk(block, label=label))
    else:
        chunks.append(DecomposedChunk(preamble_text, label="Full prompt"))
        if len(artifact_text) > MULTITURN_CHUNK_TARGET:
            for i in range(0, len(artifact_text), MULTITURN_CHUNK_TARGET):
                chunks.append(DecomposedChunk(
                    artifact_text[i:i + MULTITURN_CHUNK_TARGET],
                    label=f"Part {i // MULTITURN_CHUNK_TARGET + 1}"))
        elif artifact_text.strip():
            chunks.append(DecomposedChunk(artifact_text, label="Artifact"))

    return chunks


def _multiturn_fallback(
    mc: ModelConfig,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    pattern_text: str,
) -> tuple[str, float] | None:
    """Multi-turn decomposed dispatch fallback."""
    chunks = _build_chunks(prompt, full_code)
    if len(chunks) < 2:
        return None

    final_instruction = (
        f"You now have the complete context ({len(chunks)} chunks delivered). "
        f"This is Round {round_idx}.\n\n"
        f"{pattern_text}\n"
        f"Produce your findings now."
    )

    _log(f"  {mc.label}: MULTI-TURN — {len(chunks)} chunks, "
         f"~{sum(c.chars for c in chunks):,} chars total")

    try:
        result = decomposed_dispatch(
            api=mc.api,
            model_id=mc.model_id,
            system_prompt=cdsfl_text,
            chunks=chunks,
            final_instruction=final_instruction,
            max_tokens=mc.max_tokens,
            timeout=mc.timeout * 2,
            cdsfl_directives=cdsfl_text,
        )
        _log(f"  {mc.label}: multi-turn OK ({result.elapsed_s:.1f}s, "
             f"{len(result.text):,} chars)")
        save_decomposed_result(result, LOGS_DIR, mc.label, round_idx)
        return result.text, result.elapsed_s
    except Exception as e:
        _log(f"  {mc.label}: multi-turn FAILED — {type(e).__name__}: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────

def _dispatch_single_model(
    mc: ModelConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    pattern_name: str,
) -> tuple[List[Finding], str | None]:
    """Dispatch to one model. Returns (findings, response_text_or_None)."""
    # Compose directives with interaction pattern
    try:
        composed = compose_for_model(mc.label, pattern_name)
        model_cdsfl = composed.rendered_text
        _log(f"  {mc.label}: composed directives "
             f"({len(model_cdsfl)} chars, pattern={pattern_name})")
    except Exception as e:
        _log(f"  {mc.label}: composer failed ({e}), using raw CDSFL")
        model_cdsfl = cdsfl_text

    # Get the pattern text for multi-turn final instruction
    pattern_text = INTERACTION_PATTERN_PRESETS[pattern_name][0]

    # Decomposed models go to multi-turn sequential delivery
    if _should_decompose(mc.label, mgr):
        _log(f"  {mc.label}: decomposed — multi-turn sequential delivery")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text)
        if fallback is not None:
            text, elapsed = fallback
            _record_throughput(mc.label, len(prompt), elapsed)
            _log(f"\n{'─' * 40} {mc.label} RESPONSE (sequential) {'─' * 40}")
            _log(text)
            _log(f"{'─' * 40} /{mc.label} {'─' * 40}\n")
            model_findings = parse_findings(mc.label, round_idx, text)
            _log(f"  {mc.label}: {len(model_findings)} findings parsed")
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            save_output(
                LOGS_DIR, f"r{round_idx}", mc.label,
                prompt[:200] + "...", text,
                metadata={
                    "round": round_idx, "elapsed": round(elapsed, 1),
                    "chars": len(text), "findings_count": len(model_findings),
                    "decomposed": True, "multiturn": True,
                })
            return model_findings, text

    # Single-turn dispatch
    wall_limit = mc.timeout * 5 if mc.label == "CC2" else mc.timeout * 3
    try:
        text, elapsed = dispatch_to_model(
            mc, prompt, model_cdsfl, wall_clock_limit=wall_limit)
        _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")
        _record_throughput(mc.label, len(prompt), elapsed)

        _log(f"\n{'─' * 40} {mc.label} RESPONSE {'─' * 40}")
        _log(text)
        _log(f"{'─' * 40} /{mc.label} {'─' * 40}\n")

        model_findings = parse_findings(mc.label, round_idx, text)
        _log(f"  {mc.label}: {len(model_findings)} findings parsed")

        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        save_output(
            LOGS_DIR, f"r{round_idx}", mc.label,
            prompt[:200] + "...", text,
            metadata={
                "round": round_idx, "elapsed": round(elapsed, 1),
                "chars": len(text), "findings_count": len(model_findings),
                "decomposed": False,
            })
        return model_findings, text

    except (CircuitBreakerTripped, TimeoutError, Exception) as e:
        _log(f"  {mc.label}: {type(e).__name__} — {e}")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text)
        if fallback is not None:
            text, elapsed = fallback
            _log(f"  {mc.label}: RECOVERED via multi-turn ({elapsed:.1f}s)")
            _record_throughput(mc.label, len(prompt), elapsed)
            _log(f"\n{'─' * 40} {mc.label} RESPONSE (multi-turn) {'─' * 40}")
            _log(text)
            _log(f"{'─' * 40} /{mc.label} {'─' * 40}\n")
            model_findings = parse_findings(mc.label, round_idx, text)
            _log(f"  {mc.label}: {len(model_findings)} findings parsed (multi-turn)")
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            save_output(
                LOGS_DIR, f"r{round_idx}", mc.label,
                prompt[:200] + "...", text,
                metadata={
                    "round": round_idx, "elapsed": round(elapsed, 1),
                    "chars": len(text), "findings_count": len(model_findings),
                    "decomposed": True, "multiturn": True,
                })
            return model_findings, text
        else:
            _log(f"  {mc.label}: ALL dispatch methods exhausted")
            return [], f"__DISPATCH_FAILED__:{type(e).__name__}: {e}"


def _dispatch_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    brain: InsectBrain,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    pattern_name: str,
    relay_mode: str = DEFAULT_RELAY_MODE,
) -> tuple[List[Finding], Dict[str, str], Dict[str, float]]:
    """Dispatch to all models in parallel.

    Returns (findings, responses, per_model_durations).
    per_model_durations maps model_label -> elapsed_s for endocrine pacing.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    per_model_durations: Dict[str, float] = {}

    eligible = [
        mc for mc in exp_config.models
        if mc.label in BASELINE_MODELS and mc.role != "collator"
    ]

    # Get relay payloads from insect brain (round > 0 only)
    if round_idx > 0:
        if relay_mode == "directed":
            relay_payloads = brain.relay_directed(round_idx)
        elif relay_mode == "conversational":
            relay_payloads = brain.relay_conversational(round_idx)
        else:
            relay_payloads = brain.relay(round_idx)
    else:
        relay_payloads = {}

    def _make_model_prompt(mc_label: str) -> str:
        if round_idx == 0 or mc_label not in relay_payloads:
            return prompt  # blind round — base prompt only

        payload = relay_payloads[mc_label]
        if not payload.findings_text:
            return prompt

        # Inject brain's relay payload into prompt
        if relay_mode in ("directed", "conversational"):
            relay_section = (
                f"=== OTHER MODELS' ANALYSIS (Round {round_idx - 1}) ===\n\n"
                f"You are reviewing the same artifact as {len(payload.active_models) - 1} "
                f"other models. Below is their full analysis. Engage with their "
                f"reasoning: challenge weak claims, confirm strong ones, extend "
                f"insights, and find what everyone missed.\n\n"
                f"{payload.findings_text}\n\n"
                f"{'(NOTE: context budget exceeded — some responses truncated)' if payload.context_reset else ''}\n"
                f"{payload.convergence_summary}\n\n"
                f"=== END OTHER MODELS' ANALYSIS ===\n\n"
                f"Now produce YOUR findings. Apply full CDSFL + FFF. "
                f"Do not repeat what has already been found — build on it, "
                f"challenge it, or go deeper.\n\n"
            )
        else:
            relay_section = (
                f"Prior findings from other models "
                f"({payload.finding_count} total, "
                f"{'CONTEXT RESET — summary only' if payload.context_reset else 'full text'}):\n\n"
                f"{payload.findings_text}\n\n"
                f"{payload.convergence_summary}\n\n"
                f"Find what was MISSED. Do not repeat known findings.\n\n"
            )
        return prompt.replace(
            "=== ARTIFACT:",
            f"{relay_section}=== ARTIFACT:",
        ) if "=== ARTIFACT:" in prompt else f"{relay_section}{prompt}"

    _log(f"  Parallel dispatch: {len(eligible)} models")
    deferred_failures: list[tuple[str, str]] = []

    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        dispatch_start_times: Dict[str, float] = {}
        for mc in eligible:
            dispatch_start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model,
                mc, mgr, _make_model_prompt(mc.label), cdsfl_text, full_code,
                round_idx, pattern_name,
            )] = mc.label

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            elapsed = time.monotonic() - dispatch_start_times[label]
            per_model_durations[label] = elapsed
            try:
                model_findings, text = future.result()
                findings.extend(model_findings)
                if text is not None and not text.startswith("__DISPATCH_FAILED__:"):
                    responses[label] = text
                elif text is not None and text.startswith("__DISPATCH_FAILED__:"):
                    deferred_failures.append((label, text[20:]))
            except Exception as e:
                _log(f"  {label}: thread error — {type(e).__name__}: {e}")

    for label, detail in deferred_failures:
        _report_dispatch_failure(mgr, label, round_idx, detail)
        brain.handle_model_failure(label, detail)

    return findings, responses, per_model_durations


# ─────────────────────────────────────────────────────────────────────────────
# Safety checks
# ─────────────────────────────────────────────────────────────────────────────

def _safety_check(
    responses: Dict[str, str],
    round_idx: int,
    brain: InsectBrain,
) -> Optional[str]:
    """Check for problems that warrant stopping.

    Per-model failures bench the model (via brain.handle_model_failure)
    rather than killing the experiment. Only stop if ALL models fail.
    """
    if not responses:
        return "all_models_failed"

    failed_labels = []
    for label, text in responses.items():
        if len(text.strip()) < 50:
            _log(f"  SAFETY: {label} near-empty response ({len(text)} chars) — benching")
            brain.handle_model_failure(label, f"empty_response_round_{round_idx}")
            failed_labels.append(label)
        elif "[MODEL_REFUSED" in text:
            _log(f"  SAFETY: {label} refused — benching")
            brain.handle_model_failure(label, f"refused_round_{round_idx}")
            failed_labels.append(label)

    for label in failed_labels:
        responses.pop(label, None)

    if not responses:
        return "all_models_failed"

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Gamma convergence (shadow — logged alongside brain's convergence)
# ─────────────────────────────────────────────────────────────────────────────

GAMMA_THRESHOLD = 0.5
MIN_ROUNDS_FOR_GAMMA = 2
CLUSTER_THRESHOLD = 0.33


def _estimate_gamma(all_findings: List[List[Finding]]) -> float:
    """Estimate Duane gamma from per-round finding counts."""
    n = len(all_findings)
    if n < MIN_ROUNDS_FOR_GAMMA:
        return 0.0
    per_round = [len(rnd) for rnd in all_findings]
    cumulative = []
    total = 0
    for c in per_round:
        total += c
        cumulative.append(total)
    if cumulative[0] <= 0 or cumulative[-1] <= cumulative[0]:
        return 0.0 if cumulative[-1] == 0 else 1.0
    try:
        beta = (math.log(cumulative[-1]) - math.log(cumulative[0])) / math.log(n)
        return 1.0 - beta
    except (ValueError, ZeroDivisionError):
        return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Endocrine helpers
# ─────────────────────────────────────────────────────────────────────────────

def _build_round_timings(
    responses: Dict[str, str],
    per_model_durations: Dict[str, float],
    findings: List[Finding],
    round_idx: int,
) -> List[RoundTiming]:
    """Build RoundTiming list from dispatch results for endocrine pacing."""
    timings = []
    for label, text in responses.items():
        model_findings = [f for f in findings if f.model_id == label]
        timings.append(RoundTiming(
            model_id=label,
            round_idx=round_idx,
            duration_s=per_model_durations.get(label, 0.0),
            response_chars=len(text),
            finding_count=len(model_findings),
        ))
    return timings


def _summarise_health_scan(scan: HealthScan) -> Dict[str, Any]:
    """Produce a JSON-serialisable summary of a health scan."""
    return {
        "total_diagnostics": scan.total,
        "by_category": dict(scan.counts_by_category),
        "by_tool": dict(scan.counts_by_tool),
        "by_severity": dict(scan.counts_by_severity),
        "by_file": dict(scan.counts_by_file),
        "tools_available": dict(scan.tools_available),
        "elapsed_s": round(scan.elapsed_s, 2),
    }


def _summarise_fix_evaluations(evals: List[FixEvaluation]) -> Dict[str, Any]:
    """Produce a JSON-serialisable summary of fix evaluations."""
    verdict_counts: Dict[str, int] = {}
    for ev in evals:
        verdict_counts[ev.verdict] = verdict_counts.get(ev.verdict, 0) + 1
    return {
        "total_evaluated": len(evals),
        "verdicts": verdict_counts,
        "details": [
            {
                "finding_id": ev.finding_id,
                "verdict": ev.verdict,
                "net_type_errors": ev.net_type_errors,
                "net_ruff_errors": ev.net_ruff_errors,
                "net_bandit_issues": ev.net_bandit_issues,
                "elapsed_s": round(ev.elapsed_s, 2),
            }
            for ev in evals
        ],
    }


def _summarise_pacing_signals(signals: List[PacingSignal]) -> List[Dict[str, Any]]:
    """Produce a JSON-serialisable list of pacing signals."""
    return [
        {
            "type": s.signal_type,
            "detail": s.detail,
            "model_id": s.model_id,
            "metric_value": round(s.metric_value, 3),
            "threshold": round(s.threshold, 3),
            "suggested_action": s.suggested_action,
        }
        for s in signals
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Exp 30 fix summary for base prompt injection
# ─────────────────────────────────────────────────────────────────────────────

def _build_exp30_fix_summary() -> str:
    """Build a concise summary of the 39 fixes applied from Exp 30.

    Loaded from the deduped bugs JSON if available, otherwise falls back
    to a hardcoded summary. Models need to know WHAT was fixed so they
    don't waste rounds rediscovering it.
    """
    deduped_path = REPO_ROOT / "bench" / "logs" / "exp30_deduped_bugs.json"
    if deduped_path.exists():
        try:
            bugs = json.loads(deduped_path.read_text(encoding="utf-8"))
            # Only include bugs that had code fixes applied
            applied_ids = {
                1, 2, 3, 4, 5, 6, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20,
                22, 33, 34, 36, 38, 40, 41, 46, 48, 52, 56, 58, 62, 63,
                67, 69, 70, 72, 76, 79, 82,
            }
            lines = []
            for b in bugs:
                if b["bug_id"] in applied_ids:
                    desc = b["description"][:200].strip()
                    sev = b["max_severity"]
                    lines.append(f"  BUG #{b['bug_id']} (sev {sev}): {desc}")
            if lines:
                return (
                    f"{len(lines)} bugs fixed across 3 files "
                    f"(immune_agents.py: 18, insect_brain.py: 10, "
                    f"verification_chain.py: 8).\n"
                    "Plus 3 architectural changes: bug-closed gate in NK cell, "
                    "programmatic fix evaluation (Stage 4), BUDGET_EXHAUSTED status.\n\n"
                    + "\n".join(lines)
                )
        except Exception as e:
            _log(f"  WARNING: Could not load deduped bugs: {e}")

    # Hardcoded fallback
    return (
        "39 bugs fixed across 3 files "
        "(immune_agents.py: 18, insect_brain.py: 10, verification_chain.py: 8).\n"
        "Plus 3 architectural changes: bug-closed gate in NK cell, "
        "programmatic fix evaluation (Stage 4), BUDGET_EXHAUSTED status.\n\n"
        "Key fixes include: SMT-LIB multi-condition negation (#1), "
        "checkpoint recovery model_responses (#2/#3), CLI thread lock (#4), "
        "skin barrier citation pattern (#5), gamma_hat div-by-zero (#6), "
        "Z3 if/then verification (#9), NK v1 control flow leak (#10), "
        "load_json validation (#12), immune serialisation (#13), "
        "lazy tool discovery sync (#14), newline handling (#15), "
        "reconciliation margin (#16), dendritic AND join (#17), "
        "exception specificity (#19), dead code removal (#20), "
        "handle_model_failure checkpoint (#22), log-odds sign (#33), "
        "sympy regex (#34), max_rounds=0 guard (#36), "
        "orphan epoch check (#38), deep copy properties (#40), "
        "skin barrier line-only (#41), barrier rejection counting (#46), "
        "truncation marker (#48), CLI/API contract (#52), "
        "autoimmune override (#56), epoch ordering (#58), "
        "atomic write (#62), docstring (#63), AST caching (#67), "
        "basename ambiguity (#69), sub-second timestamps (#70), "
        "statistical claims (#72), error truncation (#76), "
        "seal_epoch idempotency (#79), tool_usage counting (#82)."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment loop
# ─────────────────────────────────────────────────────────────────────────────

def run_preflight(exp_config: ExperimentConfig, cdsfl_text: str) -> bool:
    """Quick preflight: dispatch a trivial prompt to each model."""
    _log("=" * 60)
    _log("PREFLIGHT: Testing 5-model connectivity")
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


def run_experiment(
    exp_config: ExperimentConfig,
    cdsfl_text: str,
    pattern_name: str = DEFAULT_PATTERN,
    relay_mode: str = DEFAULT_RELAY_MODE,
    resume: bool = False,
) -> Dict[str, Any]:
    """Run Experiment 31: endocrine layer integration test."""
    _log("=" * 60)
    _log(f"EXPERIMENT 31: Endocrine Layer Integration Test")
    _log(f"  Pattern: {pattern_name}")
    _log(f"  Relay mode: {relay_mode}")
    _log(f"  Max rounds: {MAX_ROUNDS}")
    _log(f"  Wall clock cap: {WALL_CLOCK_CAP_S}s")
    _log(f"  Source files: {len(SOURCE_FILES)}")
    _log(f"  Logs: {LOGS_DIR}")
    _log("=" * 60)

    # Load source files
    full_code_parts = []
    total_raw = 0
    source_paths_str = []
    for src_path in SOURCE_FILES:
        src_text = src_path.read_text(encoding="utf-8")
        rel = src_path.relative_to(REPO_ROOT)
        full_code_parts.append(f"=== FILE: {rel} ({len(src_text):,} chars) ===\n{src_text}")
        total_raw += len(src_text)
        source_paths_str.append(str(src_path))
    full_code = "\n\n".join(full_code_parts)
    _log(f"  Source: {len(SOURCE_FILES)} files, "
         f"{total_raw:,} raw chars → {len(full_code):,} with headers")

    # Build DynamicManager
    dm_config = DynamicManagementConfig(
        pre_decompose_models={"Codex", "DeepSeek"},
        no_exclusion_mode=True,
    )
    dm_config.max_rounds = MAX_ROUNDS
    model_specs = build_model_specs(exp_config)
    mgr = DynamicManager(model_specs, dm_config)

    # Build Insect Brain — central relay
    brain = InsectBrain(
        config=dm_config,
        logs_dir=LOGS_DIR,
        source_paths=source_paths_str,
    )
    brain.initialise(model_labels=sorted(BASELINE_MODELS))

    # Build Endocrine Layer — health monitor
    endo = EndocrineLayer(
        source_paths=source_paths_str,
        test_cmd=None,  # No test suite for the test article itself
        max_fix_evals=20,
    )
    _log(f"  Endocrine layer initialised: {len(source_paths_str)} source paths")

    # Resume from checkpoint if available
    start_round = 0
    if resume and brain.load_checkpoint():
        start_round = brain.state.current_round + 1
        total_restored = sum(len(rnd) for rnd in brain.state.all_findings)
        _log(f"  RESUMED from round {start_round} "
             f"({total_restored} findings, {len(brain.state.all_findings)} rounds)")

    experiment_start = time.monotonic()
    # Track novelty counts across rounds for pacing signals
    novelty_counts: List[int] = []
    # Track cumulative context chars for pacing signals
    cumulative_context_chars = 0
    # Track directed message stats
    total_directed_messages = 0
    directed_sent_per_model: Dict[str, int] = {}
    directed_received_per_model: Dict[str, int] = {}

    result: Dict[str, Any] = {
        "experiment": "exp31_postfix",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "pattern": pattern_name,
        "relay_mode": relay_mode,
        "models": sorted(BASELINE_MODELS),
        "source_files": [str(p.relative_to(REPO_ROOT)) for p in SOURCE_FILES],
        "max_rounds": MAX_ROUNDS,
        "rounds": [],
    }

    # Build multi-model awareness preamble
    roster_lines = "\n".join(
        f"  - {label}: {desc}" for label, desc in sorted(MODEL_ROSTER.items())
    )
    if relay_mode == "directed":
        awareness_preamble = (
            "You are one of 5 AI models participating in a distributed code review "
            "under full CDSFL constraints with FFF methodology. The participating models are:\n"
            f"{roster_lines}\n\n"
            "INTER-MODEL MESSAGING:\n"
            "You can direct messages to specific models using @tags. Examples:\n"
            "  @Gemini: Your F003 claims the Merkle root is recomputed on every read — "
            "can you provide evidence? I see caching at line 142.\n"
            "  @DeepSeek: Your FOLLOW trace for F007 stops at the immune pipeline. "
            "What happens to rejected findings downstream?\n"
            "  QUESTION_FOR: CC2\n"
            "  Your proposed fix for F012 changes the checkpoint schema. "
            "Have you traced whether load_checkpoint() handles the old format?\n"
            "  RESPONSE_TO: Codex\n"
            "  You are correct that the budget calculation double-counts. "
            "Here is a concrete fix: ...\n\n"
            "You WILL receive directed messages from other models in a clearly marked "
            "ADDRESSED TO YOU section at the top of your context. You MUST respond to "
            "these — they are direct questions or challenges about your work.\n\n"
            "In each round after Round 0, you will also see the OTHER models' complete "
            "analysis from the previous round. You should:\n"
            "  - RESPOND to any directed messages addressed to you\n"
            "  - DIRECT specific questions or challenges to other models using @tags\n"
            "  - ENGAGE with their reasoning: challenge weak evidence, confirm strong claims\n"
            "  - EXTEND their insights: follow implications they may have missed\n"
            "  - FIND what everyone missed: the highest-value findings are the ones "
            "no other model has identified\n\n"
            "You remain under full CDSFL + FFF constraints. Every finding must have "
            "FIND (evidence), FIX (concrete correction), and FOLLOW (downstream trace). "
            "The conversation is rigorous, not chatty.\n\n"
            f"{_GOOD_ENOUGH_INSTRUCTION}"
        )
    elif relay_mode == "conversational":
        awareness_preamble = (
            "You are one of 5 AI models participating in a distributed code review "
            "under full CDSFL constraints with FFF methodology. The participating models are:\n"
            f"{roster_lines}\n\n"
            "In each round after Round 0, you will see the OTHER models' complete "
            "analysis from the previous round — their full reasoning chains, "
            "FIND/FOLLOW/FIX traces, and conclusions. You should:\n"
            "  - ENGAGE with their reasoning: challenge weak evidence, confirm strong claims\n"
            "  - EXTEND their insights: follow implications they may have missed\n"
            "  - DISAGREE where warranted: if another model's FOLLOW trace is incomplete "
            "or their FIX introduces new problems, say so with evidence\n"
            "  - FIND what everyone missed: the highest-value findings are the ones "
            "no other model has identified\n\n"
            "You remain under full CDSFL + FFF constraints. Every finding must have "
            "FIND (evidence), FIX (concrete correction), and FOLLOW (downstream trace). "
            "The conversation is rigorous, not chatty.\n\n"
            f"{_GOOD_ENOUGH_INSTRUCTION}"
        )
    else:
        awareness_preamble = (
            "You are one of 5 AI models participating in a distributed code review "
            "under full CDSFL constraints. The other models are:\n"
            f"{roster_lines}\n\n"
            "You will see other models' findings (not their full analysis). "
            "Do not repeat known findings — find what was missed.\n\n"
            f"{_GOOD_ENOUGH_INSTRUCTION}"
        )

    # Load Exp 30 fix summary for injection into base prompt
    exp30_fix_summary = _build_exp30_fix_summary()

    # Build base prompt
    base_prompt = (
        f"{awareness_preamble}"
        "You are participating in Experiment 31 — a distributed compute P-pass "
        "under CDSFL reviewing the PERSISTENCE LAYER of the CDSFL testbench.\n\n"
        "The persistence layer provides:\n"
        "  1. Merkle tree verification chain (verification_chain.py)\n"
        "  2. Insect brain relay — reactive mechanical coordinator (insect_brain.py)\n"
        "  3. Immune pipeline — 6-cell verification (immune_agents.py)\n\n"
        "IMPORTANT CONTEXT — PRIOR EXPERIMENT RESULTS:\n"
        "These files were reviewed in Experiment 30 by 5 AI models over 15 rounds. "
        "That experiment identified ~83 distinct bugs and proposed 232 fixes. "
        "39 bug fixes and 3 architectural changes have been APPLIED to the code "
        "you are now reviewing. All 571 tests pass after changes.\n\n"
        "=== APPLIED FIXES (DO NOT REDISCOVER) ===\n\n"
        f"{exp30_fix_summary}\n\n"
        "=== END APPLIED FIXES ===\n\n"
        "These bugs are CLOSED. Do NOT rediscover, re-report, or propose "
        "alternative fixes for any of the above. The bug-closed gate will "
        "reject such findings automatically.\n\n"
        "YOUR TASK:\n"
        "  1. VERIFY that the applied fixes hold — check for regressions, "
        "incomplete patches, or edge cases the fixes missed.\n"
        "  2. FIND RESIDUAL BUGS — issues that were NOT in the 39 fixed bugs "
        "and remain in the codebase.\n"
        "  3. FIND NEW ISSUES — bugs introduced BY the fixes themselves.\n"
        "  4. Focus on what is STILL WRONG, not what was already fixed.\n\n"
        "For each finding, provide:\n"
        "  FINDING_ID: unique identifier (e.g., F001)\n"
        "  SEVERITY: 0.0 to 1.0 (1.0 = critical)\n"
        "  FLAW_CLASS: integer category (1=logic, 2=interface, 3=notation, "
        "4=completeness, 5=correctness, 6=edge-case, 7=performance, 8=documentation)\n"
        "  ABSTRACTION_INDEX: 0.0 to 1.0 (0=surface, 1=architectural)\n"
        "  DESCRIPTION: what is wrong and why it matters\n"
        "  PROPOSED_FIX: how to fix it\n"
        "  VERIFIED: TRUE if you have a proof/test, FALSE if this is an assertion\n\n"
        "Produce ALL NEW findings you can identify. Do not hold back. "
        "Do not repeat known fixed issues.\n\n"
        f"=== ARTIFACT: Persistence Layer ({len(SOURCE_FILES)} files, "
        f"{total_raw:,} chars) ===\n\n"
        f"{full_code}\n\n"
        "=== END ARTIFACT ===\n\n"
        "Produce your findings now."
    )

    # Add sequential read instruction
    n_files = full_code.count("=== FILE:")
    if n_files > 0:
        base_prompt += (
            f"\n\nIMPORTANT: This prompt contains {n_files} source files. "
            f"Read each file carefully from start to finish before beginning "
            f"your analysis.\n"
        )

    _log(f"  Base prompt: {len(base_prompt):,} chars")

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

        # Dispatch to all models (brain handles relay for adaptive rounds)
        findings, responses, per_model_durations = _dispatch_round(
            exp_config, mgr, brain,
            base_prompt, cdsfl_text, full_code,
            round_idx, pattern_name,
            relay_mode=relay_mode,
        )

        # Safety check (benches individual models, only stops if ALL fail)
        problem = _safety_check(responses, round_idx, brain)
        if problem:
            _log(f"\n*** PULL THE PLUG: {problem} ***")
            result["terminated"] = problem
            break

        # Persist round via brain
        round_elapsed = time.monotonic() - round_start
        brain.persist(round_idx, responses, findings, duration_s=round_elapsed)

        # Extract directed messages from model responses
        round_directed_count = 0
        if relay_mode == "directed":
            for model_label, response_text in responses.items():
                if response_text:
                    directed = brain.extract_directed_messages(
                        model_label, response_text, round_idx,
                    )
                    if directed:
                        _log(f"  {model_label}: {len(directed)} directed message(s) extracted")
                        round_directed_count += len(directed)
                        # Track per-model sent counts
                        directed_sent_per_model[model_label] = (
                            directed_sent_per_model.get(model_label, 0) + len(directed)
                        )
                        # Track per-model received counts
                        for dm in directed:
                            directed_received_per_model[dm.recipient] = (
                                directed_received_per_model.get(dm.recipient, 0) + 1
                            )
            total_directed_messages += round_directed_count

        # ── Endocrine cycle ──────────────────────────────────────────────
        # Build round timings for pacing
        round_timings = _build_round_timings(
            responses, per_model_durations, findings, round_idx,
        )

        # Track cumulative context size
        for text in responses.values():
            cumulative_context_chars += len(text)

        # Count novel findings for this round (simple: all findings are
        # "novel" in the first round; in subsequent rounds, brain's dedup
        # gives us the actual count via immune pipeline)
        novelty_counts.append(len(findings))

        # Run endocrine cycle
        endo_report = endo.run(
            round_idx=round_idx,
            findings=findings,
            round_timings=round_timings,
            cumulative_context_chars=cumulative_context_chars,
            context_budget=max(CONTEXT_CHAR_BUDGET.values()),
            novelty_counts=novelty_counts,
        )

        # Log endocrine results
        _log(f"\n  Endocrine cycle (round {round_idx}):")
        _log(f"    Health scan: {endo_report.health_scan.total} diagnostics "
             f"({endo_report.health_scan.elapsed_s:.1f}s)")
        for cat, count in sorted(endo_report.health_scan.counts_by_category.items()):
            _log(f"      {cat}: {count}")

        if endo_report.fix_evaluations:
            verdict_counts: Dict[str, int] = {}
            for ev in endo_report.fix_evaluations:
                verdict_counts[ev.verdict] = verdict_counts.get(ev.verdict, 0) + 1
            _log(f"    Fix evaluations: {len(endo_report.fix_evaluations)} evaluated")
            for verdict, count in sorted(verdict_counts.items()):
                _log(f"      {verdict}: {count}")
        else:
            _log(f"    Fix evaluations: none (no proposed fixes)")

        if endo_report.pacing_signals:
            _log(f"    Pacing signals: {len(endo_report.pacing_signals)}")
            for sig in endo_report.pacing_signals:
                _log(f"      {sig.signal_type}: {sig.detail} → {sig.suggested_action}")
        else:
            _log(f"    Pacing signals: none (all healthy)")

        _log(f"    Endocrine cycle total: {endo_report.elapsed_s:.1f}s")

        # Use pacing signals for adaptive decisions
        for sig in endo_report.pacing_signals:
            if sig.signal_type == "novelty_plateau" and round_idx >= 3:
                _log(f"  PACING: novelty plateau detected — checking convergence early")
                if brain.check_convergence(round_idx):
                    _log(f"  PACING: converged early due to novelty plateau")
                    # Convergence will be detected again below, but log the cause
                    break

        # Run immune pipeline through brain
        immune_result = brain.run_immune_pipeline(findings)

        # Compute metrics through brain
        metrics = brain.compute_metrics(round_idx)

        # Shadow gamma for comparison
        gamma_shadow = _estimate_gamma(brain.state.all_findings)
        _log(f"  Shadow γ: {gamma_shadow:.3f}")

        # Build round data with endocrine metrics
        round_data: Dict[str, Any] = {
            "round": round_idx,
            "type": round_type,
            "findings_count": len(findings),
            "models_responded": list(responses.keys()),
            "elapsed_s": round(round_elapsed, 1),
            "per_model": {
                label: len([f for f in findings if f.model_id == label])
                for label in responses
            },
            "brain_metrics": metrics,
            "gamma_shadow": round(gamma_shadow, 4),
            "immune_pipeline": {
                "rejection_rate": immune_result.rejection_rate,
                "autoimmune_flag": immune_result.autoimmune_flag,
                "survivors": len(immune_result.filtered_findings),
            },
            # Endocrine metrics
            "endocrine": {
                "health_scan": _summarise_health_scan(endo_report.health_scan),
                "fix_evaluations": _summarise_fix_evaluations(endo_report.fix_evaluations),
                "pacing_signals": _summarise_pacing_signals(endo_report.pacing_signals),
                "elapsed_s": round(endo_report.elapsed_s, 2),
            },
            # Directed messaging metrics
            "directed_messages": {
                "count": round_directed_count,
            },
        }
        result["rounds"].append(round_data)

        _log(f"\n  Round {round_idx}: {len(findings)} findings from "
             f"{len(responses)} models ({round_elapsed:.1f}s)")
        for label in sorted(responses.keys()):
            model_count = len([f for f in findings if f.model_id == label])
            _log(f"    {label}: {model_count} findings")
        if round_directed_count > 0:
            _log(f"    Directed messages this round: {round_directed_count}")

        # Check convergence through brain
        if brain.check_convergence(round_idx):
            _log(f"\n  CONVERGED at round {round_idx}: "
                 f"{brain.state.convergence_reason}")
            result["converged_at"] = round_idx
            result["convergence_reason"] = brain.state.convergence_reason
            break

    # Signal complete
    signal = brain.signal_complete()

    # Final summary
    total_elapsed = time.monotonic() - experiment_start
    total_findings = sum(len(rnd) for rnd in brain.state.all_findings)
    result["total_findings"] = total_findings
    result["total_rounds"] = len(brain.state.all_findings)
    result["total_elapsed_s"] = round(total_elapsed, 1)
    result["end_time"] = datetime.now(timezone.utc).isoformat()
    result["completion_signal"] = signal

    # Per-model totals
    per_model_totals: Dict[str, int] = {}
    for rnd in brain.state.all_findings:
        for f in rnd:
            per_model_totals[f.model_id] = per_model_totals.get(f.model_id, 0) + 1
    result["per_model_totals"] = per_model_totals

    # Gamma
    gamma_final = _estimate_gamma(brain.state.all_findings)
    result["gamma"] = round(gamma_final, 4)
    result["per_round_counts"] = [len(rnd) for rnd in brain.state.all_findings]

    # Popper C(H,E)
    CONTROL_BASELINE_RATE = 2.0
    if brain.state.all_findings:
        cdsfl_rate = total_findings / len(brain.state.all_findings)
        pe_h = cdsfl_rate
        pe = CONTROL_BASELINE_RATE
        c_he = (pe_h - pe) / (pe_h + pe) if (pe_h + pe) > 0 else 0.0
        result["popper_corroboration"] = {
            "C_HE": round(c_he, 4),
            "P_E_given_H": round(pe_h, 4),
            "P_E": round(pe, 4),
        }

    # Directed messaging summary
    result["directed_messaging"] = {
        "total_count": total_directed_messages,
        "sent_per_model": directed_sent_per_model,
        "received_per_model": directed_received_per_model,
    }

    # Endocrine health trend
    result["endocrine_health_trend"] = endo.health_trend()

    # Save report
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = LOGS_DIR / "exp31_report.json"
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── Cryptographic sealing: Merkle-bundle experiment logs ────────
    # Take machine reasoning out of the black box. Every round's model
    # responses, findings, and the final report are appended to a
    # verification chain and sealed into a Merkle epoch. This produces
    # a tamper-evident, cryptographically signed record of the entire
    # reasoning process.
    chain_path = LOGS_DIR / "experiment_chain.json"
    try:
        from bench.verification_chain import VerificationChain

        chain = VerificationChain()

        # Append each round's data as a record
        for round_data_entry in result.get("rounds", []):
            round_idx_val = round_data_entry.get("round", "?")
            chain.append_record(
                artifact_type="experiment_round",
                payload=round_data_entry,
                recorded_by="exp31_runner",
                metadata={
                    "experiment": "exp31",
                    "round": round_idx_val,
                    "models": round_data_entry.get("models_responded", []),
                },
            )

        # Append per-round model responses (full transcripts)
        round_files = sorted(LOGS_DIR.glob("r*_*.json"))
        for rf in round_files:
            try:
                rf_data = json.loads(rf.read_text(encoding="utf-8"))
                chain.append_record(
                    artifact_type="model_response",
                    payload=rf_data,
                    recorded_by="exp31_runner",
                    metadata={
                        "source_file": rf.name,
                        "experiment": "exp31",
                    },
                    storage_mode="hash_only",  # Full payload in round files
                )
            except Exception:
                pass  # Non-critical: skip malformed round files

        # Append the final report
        chain.append_record(
            artifact_type="experiment_report",
            payload=result,
            recorded_by="exp31_runner",
            metadata={
                "experiment": "exp31",
                "status": signal.get("status", "unknown"),
                "reason": signal.get("reason", "unknown"),
                "total_findings": total_findings,
                "total_rounds": len(brain.state.all_findings),
            },
        )

        # Seal the epoch — Merkle root covers all records
        epoch = chain.seal_epoch()

        # Persist the chain
        chain.save_json(str(chain_path))

        _log(f"\n  Merkle chain sealed: {len(chain.records)} records, "
             f"epoch merkle_root={epoch['merkle_root'][:24]}...")
        _log(f"  Chain saved: {chain_path}")
        result["merkle_chain"] = {
            "path": str(chain_path),
            "records": len(chain.records),
            "merkle_root": epoch["merkle_root"],
        }

        # Re-save report with chain reference
        report_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    except Exception as e:
        _log(f"\n  WARNING: Merkle sealing failed (non-fatal): {e}")
        import traceback
        _log(f"  {traceback.format_exc()}")

    _log(f"\n{'=' * 60}")
    _log(f"EXPERIMENT 31 — {len(brain.state.all_findings)} ROUNDS COMPLETE")
    _log(f"  Rounds: {len(brain.state.all_findings)}")
    _log(f"  Total findings: {total_findings}")
    _log(f"  Per model: {per_model_totals}")
    _log(f"  Per round: {[len(rnd) for rnd in brain.state.all_findings]}")
    _log(f"  γ: {gamma_final:.3f}")
    c_he_val = result.get("popper_corroboration", {}).get("C_HE")
    if c_he_val is not None:
        _log(f"  C(H,E): {c_he_val:.4f}")
    _log(f"  Pattern: {pattern_name}")
    _log(f"  Relay mode: {relay_mode}")
    _log(f"  Directed messages: {total_directed_messages}")
    _log(f"    Sent: {directed_sent_per_model}")
    _log(f"    Received: {directed_received_per_model}")
    _log(f"  Endocrine health trend: {endo.health_trend()}")
    _log(f"  Elapsed: {total_elapsed:.0f}s")
    _log(f"  Report: {report_path}")
    _log(f"  Brain signal: {signal['status']} — {signal['reason']}")
    _log(f"{'=' * 60}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global LOGS_DIR
    source_env()

    exp_config = load_default_config()
    cdsfl_path = (REPO_ROOT / "bench" / "directives" / "universal"
                  / "cdsfl_core_formal.md")
    cdsfl_text = cdsfl_path.read_text(encoding="utf-8")

    # Parse arguments
    args = sys.argv[1:]
    mode = "run"
    resume = False
    pattern = DEFAULT_PATTERN
    relay_mode = DEFAULT_RELAY_MODE

    i = 0
    while i < len(args):
        if args[i] == "--resume":
            resume = True
            mode = "run"
        elif args[i] == "--pattern" and i + 1 < len(args):
            pattern = args[i + 1]
            i += 1
        elif args[i] == "--relay-mode" and i + 1 < len(args):
            relay_mode = args[i + 1]
            i += 1
        elif args[i] in ("preflight", "run"):
            mode = args[i]
        i += 1

    # Validate pattern
    if pattern not in INTERACTION_PATTERN_PRESETS:
        available = ", ".join(sorted(INTERACTION_PATTERN_PRESETS))
        print(f"Unknown pattern: {pattern!r}. Available: {available}",
              file=sys.stderr)
        sys.exit(1)

    # Validate relay mode
    if relay_mode not in ("findings", "conversational", "directed"):
        print(f"Unknown relay mode: {relay_mode!r}. "
              f"Options: findings, conversational, directed",
              file=sys.stderr)
        sys.exit(1)

    # Set logs directory
    LOGS_DIR = _find_or_create_logs_dir(resume=resume)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if mode == "preflight":
        ok = run_preflight(exp_config, cdsfl_text)
        sys.exit(0 if ok else 1)

    elif mode == "run":
        if not resume:
            ok = run_preflight(exp_config, cdsfl_text)
            if not ok:
                _log("\nPREFLIGHT FAILED. Aborting.")
                sys.exit(1)
            _log(f"\nPreflight passed. Starting Exp 31 in 5s... "
                 f"(pattern={pattern}, relay={relay_mode})")
            time.sleep(5)
        else:
            _log(f"\nRESUME mode — skipping preflight "
                 f"(pattern={pattern}, relay={relay_mode})")

        result = run_experiment(
            exp_config, cdsfl_text,
            pattern_name=pattern, relay_mode=relay_mode, resume=resume)

        if result.get("terminated"):
            _log(f"\nExperiment terminated: {result['terminated']}")
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
