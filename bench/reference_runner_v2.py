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
import ast
import json
import math
import os
import py_compile
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

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
    set_panel_cwd,
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
    get_effective_context_budget,
)
from run_exp17_immune import (
    TASKS,
    TASK_MARKERS,
    REVIEW_AREAS,
    FINDING_FORMAT,
    RoundTelemetry,
    run_layer1_preflight,
    _should_decompose,
    _invalidate_fingerprint_cache,
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
from bench.dm._feedback import (
    FindingFeedback,
    build_feedback_records,
    build_feedback_sections,
    parse_admissibility_block,
)
# Exp 40 timing re-confer (2026-05-16): observation-only finding-ID
# collision detector accumulator. Cleared at experiment start (mirrors
# _itc_hil_flags) so the post-mortem reads only this run's collisions —
# the evidence gate for the deferred UUID-namespace decision (Exp 41).
from bench.dm import _feedback as _feedback_mod
# Exp 40 fix 1D.1, 1D.2, 1D.4: round-context helpers.
from bench.dm._round_context import (
    build_prior_fix_summary,
    build_consolidation_preamble,
    build_windowed_context,
)
# Exp 40 fix 1D.5: S_k SEARCH/REPLACE format pre-check + reformat request.
from bench.dm._sk_format import (
    check_sk_format_admissible,
    build_reformat_requests as build_sk_reformat_requests,
)
# Exp 40 fix 1E.7: cross-model diversity metric (compliance-theatre detector).
from bench.dm._diversity import diversity_signal_from_round
# Exp 40 fix 1E.7: per-finding alternative extraction for diversity metric.
from bench.dm._divergence import parse_alternative_block


# Exp 40 fix 1E.6: hard payload floor for decomposition decisions.
# Independent of fingerprint observed-capacity values — large monolithic
# dispatches degrade parse yield even when the model accepts them.
DECOMPOSE_HARD_FLOOR_CHARS = 80_000


def should_decompose_v2(
    model_label: str, mgr, payload_chars: int = 0,
) -> bool:
    """v2 decomposition decision with a fingerprint-agnostic hard floor.

    The underlying :func:`_should_decompose` is fingerprint-driven: a model
    whose fingerprint reports high observed capacity will accept large
    monolithic payloads, which in Exp 39-0 caused parse-yield collapse on
    369K dispatches to CC2/ChatGPT/Gemini (their fingerprints reported
    465K observed capacity × 0.9 safety margin = 418K ≥ 369K, no
    decompose, quality crashed).

    Layered decision:

    1. Payload > ``DECOMPOSE_HARD_FLOOR_CHARS`` (80K) → force decompose.
       This overrides the fingerprint's observed-capacity opinion. Even
       if the model has "proven" it can ingest more, quality collapses
       above the floor for ambient-noise reasons independent of
       successful-dispatch outcomes.
    2. Otherwise defer to :func:`_should_decompose` which still honours
       ``pre_decompose_models`` override, observed prompt limits, failure
       ceilings, and the static 80K fallback when fingerprint data is
       absent.

    Returns ``True`` iff the caller should decompose the payload.
    """
    if payload_chars > DECOMPOSE_HARD_FLOOR_CHARS:
        return True
    return _should_decompose(model_label, mgr, payload_chars=payload_chars)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration dataclass
# ─────────────────────────────────────────────────────────────────────────────

MODEL_ROSTER = {
    "CC2": "Claude Opus 4.7 (Anthropic)",
    "Codex": "GPT-5.5 (OpenAI)",
    "Gemini": "Gemini 3.1 Pro Preview (Google)",
    "DeepSeek": "DeepSeek V4 Pro (DeepSeek)",
    "ChatGPT": "GPT-5.5 (OpenAI)",
}

# Bugzilla CLOSED-loop verification cap per round (15 May 2026).
# Bounds wall-clock impact of programmatic fix verification — each
# attempt runs ruff + mypy + bandit + test_cmd against a sandbox copy
# of the target file (typically 30-120s per attempt). With 5 attempts
# per round the wall-clock impact is roughly 2.5-10 minutes per round.
# Findings not attempted this round remain CONFIRMED and become
# candidates next round (entry["bugzilla_attempted"] flag prevents
# re-attempting the same finding repeatedly).
BUGZILLA_PER_ROUND_LIMIT = 5

# Operational directive — R_k(i) self-assessment equation and working protocol.
# Appended AFTER composer phenotype transforms to bypass char caps. Models MUST
# compute R_k on their own output (§3, §6). Without this directive, models
# produce qualitative findings, not metacognitive self-assessment. Exp 37:
# 88-100% R_k adoption with directive, 0% without. (Exp37 line 185-194, 2195-2196)
_OPERATIONAL_DIRECTIVE_PATH = (
    REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
)
_OPERATIONAL_DIRECTIVE_TEXT = ""
if _OPERATIONAL_DIRECTIVE_PATH.exists():
    _OPERATIONAL_DIRECTIVE_TEXT = _OPERATIONAL_DIRECTIVE_PATH.read_text(encoding="utf-8")


# Gate-aware falsifier-format fix (2026-06-06). The operational directive's §2
# defines FALSIFICATION as a PROSE triad ("FALSIFIER: the specific condition that
# would disprove your claim / ATTEMPT / RESULT"). That prose definition dominates
# the model and steered all five models to prose (or no) falsifiers on the first
# live run — zero tool-testable findings (the 14-HIL failure). Redefining §2 to
# require a RUNNABLE falsifier made cc2/cx/chatgpt/gemini produce real,
# runner-CONFIRMED falsifiers (validated 2026-06-06; the adversarial audit found
# the result genuine, not gamed). Applied ONLY when the falsifier gate is on, so
# non-gate experiments keep the legacy prose FFAFP format byte-identically.
_RUNNABLE_FALSIFIER_S2 = (
    "FALSIFICATION: This section is mandatory. For every CRITICAL finding it MUST "
    "contain a RUNNABLE falsifier, NOT prose. Write the literal line \"FALSIFIER:\" "
    "on its own line, then a fenced python code block (```python ... ```) that "
    "imports the REAL target module and raises AssertionError or prints the token "
    "FALSIFIED if and only if the claimed defect is genuinely present (exit cleanly "
    "otherwise). Run it with the execute_python tool first. The runner RE-RUNS this "
    "exact python block and ITS result -- not your prose -- decides CONFIRMED or "
    "REFUTED. A prose-only or missing FALSIFIER cannot be confirmed and is sent to "
    "a human. "
    # FIX 5 (Exp 43, 2026-07-22): residual-clearing is an explicit panel duty.
    "RESIDUAL CLEARING: at the end of each round, review the registry's "
    "UNCONFIRMED findings. For each one you originated (any severity): either "
    "supply a corrected RUNNABLE falsifier for it, or explicitly declare it "
    "unfalsifiable and issue CHALLENGE with your reason so it can be closed. Do "
    "not leave your own findings parked as UNCONFIRMED round after round: an "
    "unfalsified claim earns zero corroboration and will not block convergence."
)
_S2_PROSE_RE = re.compile(
    r"FALSIFICATION: This section is mandatory\. It must contain:.*?Did you test it\?",
    re.DOTALL,
)


def _runnable_falsifier_s2(ask_corrected_copy: bool = False) -> str:
    """The §2 replacement, assembled at call time.

    The corrected-copy ask is appended here rather than baked into
    ``_RUNNABLE_FALSIFIER_S2`` so that the literal response form lives in ONE
    place (``_corrected_copy_instructions``) shared with the routing and sweep
    prompts. A model that sees three prompts must see one convention.

    GATED, default off (2026-08-12). This previously appended the ask
    unconditionally, which would have changed what every live run asked the
    panel for — and, with the discrimination control presence-gated downstream,
    would have armed that control the first time a model complied. The founder's
    decision on whether a non-discriminating falsifier may close a critical was
    still open at the time, so it would have been settled by side effect.
    Supplying the input is a separate decision from acting on it.
    """
    if not ask_corrected_copy:
        return _RUNNABLE_FALSIFIER_S2
    return (
        _RUNNABLE_FALSIFIER_S2 + " "
        + _CORRECTED_COPY_WHY + " Immediately after the FALSIFIER block, write:\n"
        + _corrected_copy_instructions() + "\n"
    )


def _gate_falsifier_directive(directive_text: str, ask_corrected_copy: bool = False) -> str:
    """Redefine the operational §2 FALSIFICATION block (prose -> runnable) when the
    falsifier gate is on. No-op if the §2 prose block is absent. Reversible: the
    directive file is untouched; the substitution happens per-dispatch in memory.

    The replacement is passed as a FUNCTION, not a string: the assembled text now
    carries sentinel lines, and a bare string replacement would interpret any
    backslash escape in it. A prompt corrupted by its own escaping is precisely
    the failure that renders as a confident success."""
    replacement = _runnable_falsifier_s2(ask_corrected_copy)
    new, n = _S2_PROSE_RE.subn(lambda _m: replacement, directive_text)
    return new if n else directive_text


# ─────────────────────────────────────────────────────────────────────────────
# Experimental factor switches (Exp 52 2x2 factorial, 2026-07-29)
# ─────────────────────────────────────────────────────────────────────────────
#
# See RunnerConfig for the semantics of "off". This block holds the shared
# vocabulary and the two helpers the run loop and the dispatch path consult.

DIRECTIVE_OFF_MODES = ("absent", "text_only", "pass_only")


class _DivergencePassDisabled(Exception):
    """Internal sentinel: the divergence runner pass is switched off.

    Raised (and caught) inside the round loop's divergence block so the
    switch shares one exit path with the block's defensive handler without
    being mistaken for a parse error in the round telemetry.
    """

# Factor key -> (enabled field, off-mode field) on RunnerConfig. The factor
# keys match bench/dm/_directive_sections.FACTOR_SPECS.
DIRECTIVE_FACTOR_FIELDS: Dict[str, Tuple[str, str]] = {
    "feedback": ("feedback_channel_enabled", "feedback_off_mode"),
    "divergence": ("divergence_channel_enabled", "divergence_off_mode"),
}

# Module mirror of the per-run directive-omission decision, set from
# RunnerConfig at experiment start (mirrors the _INROUND_REASK / _merge_arb_ctx
# pattern) so _dispatch_single_model need not have cfg threaded into it.
# Empty tuple => every factor's directive text ships, i.e. legacy behaviour.
_DIRECTIVE_OMISSION: Dict[str, Any] = {"factors": ()}


def _directive_factor_state(cfg: "RunnerConfig", factor: str) -> Tuple[bool, bool]:
    """Return ``(directive_text_present, runner_pass_active)`` for `factor`.

    A factor that is ON has both halves. A factor that is OFF loses both
    halves under the default ``"absent"`` mode, and exactly one half under
    the narrower modes. Missing attributes read as ON, so a RunnerConfig
    built by older code behaves exactly as it did before this switch existed.
    """
    enabled_field, mode_field = DIRECTIVE_FACTOR_FIELDS[factor]
    enabled = bool(getattr(cfg, enabled_field, True))
    if enabled:
        return True, True
    mode = getattr(cfg, mode_field, "absent")
    if mode == "text_only":
        return False, True
    if mode == "pass_only":
        return True, False
    return False, False  # "absent"


def _suppressed_directive_factors(cfg: "RunnerConfig") -> Tuple[str, ...]:
    """Factor keys whose directive SECTION must be omitted from the prompt."""
    return tuple(
        f for f in DIRECTIVE_FACTOR_FIELDS
        if not _directive_factor_state(cfg, f)[0]
    )


def _apply_directive_omission(model_cdsfl: str) -> str:
    """Strip suppressed factors' directive text from an assembled prompt.

    Reads the module mirror rather than cfg (see `_DIRECTIVE_OMISSION`).
    No-op — and therefore byte-identical to the pre-switch runner — when no
    factor is suppressed, which is every run whose config omits the new keys.

    Strict by construction: if a suppressed factor's section cannot be found
    the omission raises rather than shipping the mechanism the config said to
    remove. The same call is made once at experiment start, so a mid-run
    surprise here would mean the directive file changed under a live run.
    """
    factors = _DIRECTIVE_OMISSION.get("factors") or ()
    if not factors:
        return model_cdsfl
    from bench.dm._directive_sections import omit_directive_sections
    return omit_directive_sections(model_cdsfl, factors, strict=True)


def arm_directive_omission(cfg: "RunnerConfig", exp_config=None) -> Tuple[int, int]:
    """Set the per-run omission mirror, then PROVE it removes something.

    Called once at experiment start, before any paid dispatch. Two jobs:

    1. Publish the suppressed-factor list to the module mirror that
       :func:`_apply_directive_omission` reads on every dispatch.
    2. Run the omission against the real assembled prompt — the same
       composer output plus operational directive the models will receive —
       and refuse to proceed if it removed nothing.

    The second job is the point. An ablation cell whose prompt is identical
    to its control is a guaranteed null result wearing the costume of a
    measurement, and it costs a full experiment to discover. Fail here,
    loudly and cheaply, or not at all.

    Returns ``(chars_before, chars_after)`` for the probe prompt; ``(0, 0)``
    when no factor is suppressed (the default, and every pre-2026-07-29 run).
    """
    _DIRECTIVE_OMISSION["factors"] = _suppressed_directive_factors(cfg)
    factors = _DIRECTIVE_OMISSION["factors"]
    if not factors:
        return 0, 0

    probe = _OPERATIONAL_DIRECTIVE_TEXT
    if exp_config is not None:
        try:
            wanted = set(getattr(cfg, "models", []) or [])
            probe_model = next(
                (mc.label for mc in exp_config.models if mc.label in wanted),
                None)
            if probe_model:
                probe = (
                    _compose_for_model(
                        probe_model, cfg.pattern, cfg.domain).rendered_text
                    + "\n\n" + _OPERATIONAL_DIRECTIVE_TEXT
                )
        except Exception:
            pass  # composer unavailable: validate the operational text alone

    before = len(probe)
    after = len(_apply_directive_omission(probe))
    if after >= before:
        raise RuntimeError(
            f"directive-section omission removed nothing for factors "
            f"{factors} — refusing to run an ablation cell whose prompt is "
            f"identical to the control."
        )
    for f in factors:
        text_on, pass_on = _directive_factor_state(cfg, f)
        _log(f"  §-factor {f}: directive text "
             f"{'PRESENT' if text_on else 'OMITTED'}, runner pass "
             f"{'ACTIVE' if pass_on else 'DISABLED'}")
    _log(f"  directive omission verified: {before} -> {after} chars "
         f"({before - after} removed)")
    return before, after


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
    max_open_crit_high: int = 5  # Was 0 (unreachable). Exp 39-0 fix.
    # γ-alt convergence path (Exp 40 fix, Item 1A.3 remainder from Exp 40 plan).
    # Fires when EITHER gamma >= gamma_alt_threshold OR
    # gamma_alt_consecutive_zero_crit consecutive rounds with zero novel CRITICAL.
    # Documented in Exp 39 sub-experiment configs as pass_condition.
    gamma_alt_threshold: float = 0.30
    gamma_alt_consecutive_zero_crit: int = 3
    gamma_alt_earliest_round: int = 3
    # Hardened convergence gate (F4/F6/conjunction, 2026-05-18,
    # founder-directed; pre-reg
    # bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md).
    # Default OFF — existing experiments keep the legacy γ-alt OR gate
    # unchanged; Exp 40 slice configs opt in. When ON: γ is computed on
    # the SETTLED post-reconciliation registry (not the live-at-round
    # transient that flipped 0.305→0.231); the gate is the CONJUNCTION
    # (γ_critical ≥ threshold, sustained, leave-one-round-out robust)
    # AND (N consecutive zero-novel-critical rounds, settled);
    # all-novelty γ is logged as a diagnostic only; if the critical
    # pool is too small for a stable slope the gate falls back to the
    # count-based zero-novel-critical criterion alone (γ reported, not
    # gated).
    hardened_gate_enabled: bool = False
    gamma_crit_sustain_rounds: int = 2
    gamma_crit_min_cumulative: int = 8
    gamma_crit_loo_tol: float = 0.05
    # G7 merge-deadlock arbitration (Exp 40 continuation, 15 May 2026).
    # Design: experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md.
    # Default DISABLED — the design stages enablement for Exp 41
    # (single specialist, low MERGE expected, low blast radius). When
    # enabled: on the Nth consecutive defer of a finding the runner
    # dispatches a compelled-convergence single-answer query to the
    # panel; ≥3/5 agreement merges or keeps-distinct, otherwise the
    # finding stays deferred. Per-round dispatch cap bounds cost
    # (~$0.50/dispatch ⇒ ≤ ~$1.50/round at the default cap of 3).
    # tiebreaker_gamma adds the round-level trigger (Gemini confer
    # input): when γ < tiebreaker_gamma AND γ-alt is not met, sweep
    # unresolved deadlocks through arbitration at round close.
    merge_arbitration_enabled: bool = False
    merge_arbitration_min_defer_count: int = 2
    merge_arbitration_max_per_round: int = 3
    merge_arbitration_tiebreaker_gamma: float = 0.05
    # In-round re-ask (Exp 40 plan-B, 2026-05-16, founder-directed —
    # supersedes the 1e next-round-only deferral). When a model returns
    # finding-declaration content that fails to parse (>= min_markers
    # raw markers, 0 parsed findings), re-dispatch ONCE to that model in
    # the dispatch phase with a STRUCTURE_VIOLATION corrective prompt,
    # before reconciliation. Bounded (1 retry/model/round), idempotent
    # (replaces the round's output for that model on success; no
    # double-count). 1e (next-round reformat) remains the fallback.
    inround_reask_enabled: bool = True
    inround_reask_min_markers: int = 2
    # Apply-verified-fixes-back (Exp 40 plan-C, 2026-05-16,
    # founder-directed structural cure). When enabled, a finding that
    # reaches full BUGZILLA close has its SEARCH/REPLACE patch promoted
    # into a PER-RUN working copy that the NEXT round reviews — so the
    # error space actually exhausts (the precondition the decay model
    # needs to terminate). Promotion is gated on the FULL canonical
    # test suite passing cumulatively (NOT the run-time S_k score,
    # which the C0001 collation finding showed tolerates regressions).
    # The repo file is never written; the pristine original is kept.
    # Changes Exp 40 from static-stimulus to iterative repair-and-
    # reconverge — an intended, recorded design change. Default OFF.
    apply_fixes_back_enabled: bool = False
    apply_fixes_back_seed: str = ""  # optional cleaned-baseline seed path
    # Round-context helpers (Exp 40 1D.1, 1D.2, 1D.4).
    prior_fix_summary_enabled: bool = True
    prior_fix_summary_max_entries: int = 20
    prior_fix_summary_max_chars: int = 4000
    consolidation_rounds: int = 3
    windowed_context_enabled: bool = True
    windowed_context_full_rounds: int = 2
    windowed_context_max_chars: int = 6000
    rho_earliest_round: int = 12
    stall_window: int = 3
    stall_earliest_round: int = 15
    stall_gamma_advisory: float = 0.30
    stall_gamma_terminate: float = 0.45
    # Settled design (2026-05-29): gamma REPORTS, it never TRIGGERS termination.
    # The stall detector may still flag a stall as advisory telemetry, but it
    # must not END a run on a gamma threshold — that is a second hidden gamma
    # gate contradicting the convergence redesign. Default OFF: a genuinely
    # stuck run runs to max_rounds and terminates as BUDGET_EXHAUSTED (honest),
    # rather than being reported as a gamma-driven STALL_CONVERGED. The flag
    # exists only so the legacy behaviour can be re-enabled for a controlled
    # ablation; do not enable it in the Exp 41+ convergence regime.
    stall_gamma_termination_enabled: bool = False
    # ── DISCRIMINATION CONTROL (2026-08-12) ─────────────────────────────────
    # Two switches, both default OFF, because they are two different decisions.
    #
    # `_ask` appends the corrected-copy request to the §2 falsification
    # directive. Off by default so no live run silently changes what the panel
    # is asked, and no run pays for output nobody ruled on.
    #
    # `_blocks` decides whether a non-discriminating falsifier is refused the
    # right to close a critical. That is a change to the most load-bearing rule
    # in the system — CONFIRM-only — and it is the founder's open decision, so
    # it must never arrive as a side effect of wiring the supply side.
    #
    # Why separated: with `_ask` on and `_blocks` off, the control runs and
    # RECORDS its outcome without changing any verdict, which is the evidence
    # needed to rule on `_blocks` at all. Collapsing them into one flag would
    # make gathering that evidence require arming the instrument first.
    #
    # The 2026-08-12 panel review refuted the blocking design as originally
    # proposed: the check is satisfied by ACCESS rather than DEPENDENCE, so it
    # is defeated by `open(TARGET).read()` with the contents discarded — and it
    # fails GREEN, reporting full coverage while discriminating nothing. Treat
    # `_blocks` as unsafe to enable until a dependence-based test replaces it.
    discrimination_control_ask: bool = False
    discrimination_control_blocks: bool = False
    verification_batch_size: int = 6
    verification_min_round: int = 6
    verification_confidence_threshold: float = 0.7
    gamma_telemetry_only_until: int = 14
    gamma_soft_gate_until: int = 19
    # "tools decide, not votes" gate (2026-06-03). When True, a finding's truth is
    # set by the runner independently re-running the model-attached falsifier
    # (apply_falsifier_verdicts), overriding the CONFIRM/CHALLENGE vote: CONFIRMED
    # if the falsifier demonstrates the defect, REFUTED if not, HIL-escalated if
    # un-toolable/broken — never auto-confirmed. Default OFF: byte-identical
    # (vote-based) behaviour until an experiment opts in.
    falsifier_gate_enabled: bool = False
    # Capability-aware routing (2026-06-07, gated; renamed from take_up_slack 2026-07-12).
    # When True, an un-confirmed CRITICAL escalated by the falsifier gate is routed to a
    # stronger writer (with the execute_python tool loop) before the HIL is accepted.
    # Requires falsifier_gate_enabled. Default-off => byte-identical. The legacy config key
    # ``take_up_slack_enabled`` is still accepted (launcher_core back-compat alias).
    routing_enabled: bool = False
    # Code-location novelty series (2026-06-08). Computes a per-round critical-novelty
    # series keyed by target-file code location (the verified fix for the cross-round
    # dedup failure) alongside the ID-proxy count, logging both.
    #
    # NOT TELEMETRY WHENEVER ``location_keyed_convergence`` IS ALSO SET. This flag
    # computes the series; that one promotes it to the COUNT side of the two-sided gate.
    # Sixteen configs set both, from Exp 42 on. Turning THIS flag off in such a config
    # therefore does not "disable telemetry" — it silently reverts the convergence gate
    # to the ID-proxy series, i.e. reinstates the cross-round dedup failure the location
    # key exists to fix. This comment claimed "It NEVER feeds a convergence gate" until
    # 2026-08-08, which was false from the first location-keyed live run.
    #
    # Default-on. Set False ONLY when location_keyed_convergence is also False.
    location_shadow_enabled: bool = True
    # Promote the code-location key from shadow telemetry to the ACTUAL convergence
    # trigger (2026-06-09, gated default-off). When True, the γ-alt critical-quiescence
    # gate reads the location-keyed novel-critical series instead of the ID-proxy one,
    # so a re-found defect under a fresh model id no longer resets the zero-streak. This
    # does NOT touch gamma: gamma remains the reported decay-curve measure on the same
    # deduplicated stream; the count is simply the threshold-free detector of that curve's
    # zero-slope (fully-decayed) endpoint for critical findings. Requires
    # location_shadow_enabled (the series it consumes). Default-off => byte-identical.
    location_keyed_convergence: bool = False
    # HIERARCHICAL NOVELTY (2026-08-04). Location decides the coarse call; only
    # WITHIN an already-flagged location is the STEM signature asked to split.
    # Recorded in SHADOW on every run at no cost; this flag promotes it to
    # GATING and defaults off, so behaviour is unchanged unless set.
    hierarchical_novelty_convergence: bool = False
    hierarchical_within_threshold: float = 0.20
    # Severity calibration (over-production bounding, 2026-06-10, gated default-off).
    # Lowers the EFFECTIVE severity of a finding that the falsifier gate CONFIRMED
    # as a REAL defect but that is explicitly flagged LATENT/conditional (it needs a
    # trigger absent from the usage contract) to just below the critical threshold,
    # so it stops perpetually re-blocking convergence / piling up in HIL — WITHOUT
    # being deleted (original severity + reason recorded on the entry). NEVER demotes
    # a safety/core-functionality finding. Default OFF => byte-identical (no entry is
    # mutated). NOTE: inert without an upstream producer that tags entries
    # `latent`/`finding_category`; the flag alone is a safe no-op (fail-safe).
    severity_calibration_enabled: bool = False
    # Severity a demoted finding is pinned to (must be < CRITICAL_SEVERITY_THRESHOLD).
    severity_calibration_floor: float = 0.69
    # LATENT TAGGER (2026-07-31) — the upstream producer severity calibration has
    # always been missing. Runs BEFORE the calibration sweep and sets `latent` /
    # `finding_category` on each registry entry from explicit evidence only (a
    # panel-emitted REACHABILITY/TRIGGER field, or an explicit prose claim of
    # unreachability); absent evidence it sets latent=False, so calibration stays
    # a no-op. See bench/latent_tagger.py. Default OFF => byte-identical. Enabling
    # this WITHOUT severity_calibration_enabled is safe and purely observational:
    # the tags are written and logged, nothing reads them.
    latent_tagger_enabled: bool = False
    gamma_soft_threshold: float = 0.30
    gamma_hard_threshold: float = 0.35
    min_rounds_for_gamma: int = 3
    max_contested_rounds: int = 5
    # POST-CONVERGENCE SWEEP (founder-approved 2026-07-28): after the terminal
    # convergence verdict is RECORDED, run up to this many bounded epilogue
    # rounds whose ONLY duty is clearing residual non-terminal findings
    # (runnable falsifier or reasoned withdrawal). 0 = off (byte-identical).
    post_convergence_sweep_rounds: int = 0
    # IMMUNE MEMORY (founder-approved 2026-07-28; CONSUMPTION added 2026-07-31).
    # The cross-experiment ImmuneMemory (bench/dm/_memory.py, appendix §1.5)
    # has TWO separable jobs, and they are separately switched — see below.
    #
    # RECORDING. The run's per-flaw-class confirmed/rejected tallies are written
    # to the memory at run end. This is what `immune_memory_enabled` has meant
    # since 2026-07-28, and it is true in eleven shipped configs.
    immune_memory_enabled: bool = False
    # CONSUMPTION. The memory's blended prior SEEDS R_k(0) — the appendix §1.1
    # initial condition R_k(0) = π_k — per finding flaw class.
    #
    # This is deliberately a SEPARATE switch, defaulting off, and the separation
    # is load-bearing rather than tidiness. Consumption first shipped gated on
    # `immune_memory_enabled`, which is already true in all four factorial cells,
    # the zero-plant control, and the physics and biology exams — none of which
    # was written with any intention of consuming a prior. Two consequences, both
    # silent:
    #   * The memory ACCUMULATES between runs, so cell D's starting estimate
    #     would depend on cells A-C having already run. The 2x2 factorial's
    #     entire design rests on its four cells being independent; coupling them
    #     makes the comparison it exists to draw worthless, and the run would
    #     complete and produce numbers regardless.
    #   * The zero-plant control would stop being a control, its starting
    #     estimate shaped by memory accumulated over three earlier experiments —
    #     an uncontrolled variable inside the one instrument built to have none.
    # Recording is harmless everywhere and stays on. Consuming is a measurement
    # decision and must be made per experiment, deliberately, never inherited.
    immune_memory_consume_rk0: bool = False
    immune_memory_path: str = "bench/state/immune_memory.json"
    # ρ (rho) — appendix §1.5 memory blending weight in π(k) = (1-ρ)·π_base +
    # ρ·π_mem(k). 0.0 = ignore memory entirely (blended prior collapses to
    # π_base, i.e. byte-identical to consumption-off). Default 0.2 matches
    # the appendix default and DMConfig.rho_memory.
    immune_memory_rho: float = 0.2
    # PANEL WORKING DIRECTORY (2026-07-29, after a confirmed key access in Exp 48).
    # The shell-bearing routes otherwise inherit the runner's cwd — this repo —
    # which for an exam run hands the panel a tree that names the scoring key's
    # location and holds superseded keys in git history. Exam configs point this
    # at the staged target directory, which contains modules and nothing else.
    # Empty = inherited (the code-experiment default, byte-identical).
    panel_cwd: str = ""
    # Static-queue closure (2026-06-09): the automated loop may converge while handing a
    # SMALL queue of ladder-exhausted irreducible criticals to the human. A queue larger
    # than this is treated as a mechanical-failure ALARM (routing/dedup), not genuine
    # irreducibility, and refuses convergence. For code review, genuinely-irreducible
    # defects are rare, so the bound is small.
    max_irreducible_queue: int = 2
    exhausted_round_threshold: int = 8  # rounds stalled before EXHAUSTED bypass
    multiturn_chunk_target: int = 30_000

    # S_k pipeline
    sk_enabled: bool = False
    test_cmd: Optional[str] = None
    sk_s_floor: float = 0.0  # domain-specific minimum S*

    # TARGET TYPE — a DECLARATION OF INTENT ONLY (A1, 2026-08-01).
    # "" (the default) means "do not declare". Any other value must equal what
    # ``detect_target_kind`` reads off the actual path and bytes, or the harness
    # raises TargetKindMismatch and refuses to start. The harness NEVER takes
    # this field as the answer: enforcement lives in ``resolve_target_kind`` and
    # in ``compute_sk``, which classify from the target itself. This is
    # deliberate — the launcher has silently dropped config keys six times, so a
    # safety property whose enforcement depends on a config flag is not enforced.
    target_kind: str = ""

    # Burst decomposition: "auto" (decide based on fingerprints),
    # "on" (always decompose), "off" (monolithic)
    burst_mode: str = "auto"

    # Shadow cell configuration (Macrophage + Ouroboros, cell type split 12 April 2026)
    shadow_cell_config: Dict[str, Any] = field(default_factory=dict)

    # HIL review gate (13 April 2026, agreed scope refinement).
    # When True, the runner saves checkpoint and exits with code 42 after
    # each round (monolithic mode) or phase transition (burst mode).
    # Resume with --resume to continue.  This enables the collaborative
    # test-discover-analyse-fix-fold cycle between the operator and CC.
    hil_review: bool = False

    # ── Experimental factor switches (Exp 52 2x2 factorial, 2026-07-29) ──
    #
    # Two mechanisms, each with TWO halves: a directive-text half (the
    # section of cdsfl_operational.md that tells the model the mechanism
    # exists) and a runner-pass half (the code that acts on it). A factor
    # that is half-present measures nothing coherent, so ONE knob per factor
    # governs BOTH halves.
    #
    # WHAT "OFF" MEANS — the load-bearing judgement.
    # The factorial asks whether the mechanism AS DEPLOYED causes the recall
    # improvement. "As deployed" is directive text plus runner pass together;
    # that pair is the treatment. So the default reading of `False` is THE
    # MECHANISM ABSENT ENTIRELY: the model receives no directive section for
    # it, and the runner performs no pass for it — the cell is what CDSFL
    # would be if the mechanism had never been built. The alternative
    # readings (suppress only the prompt-level mandate, or only the
    # machinery) answer narrower questions and are reachable through
    # *_off_mode, but they are NOT the factorial's default.
    #
    #   off_mode = "absent"    (DEFAULT) no directive section, no runner pass
    #   off_mode = "text_only" no directive section, runner pass still runs
    #                          — "does the prompt-level mandate matter, given
    #                            the machinery runs anyway?"
    #   off_mode = "pass_only" directive section retained, no runner pass
    #                          — "does the machinery matter, given the model
    #                            was told the mechanism exists?"
    #
    # off_mode is INERT while the corresponding *_enabled is True.
    #
    # §17 feedback channel. Defaults True — the whole point of CDSFL is
    # corrective feedback, not measurement for its own sake.
    feedback_channel_enabled: bool = True
    feedback_off_mode: str = "absent"
    feedback_top_k: int = 10
    feedback_max_chars_per_model: int = 8000

    # §18 divergence directive. Defaults True — CDSFL's invention-engine arm.
    # Before 2026-07-29 there was no switch at all: the runner hard-coded
    # DivergenceConfig(enabled=True) and the §18 text shipped unconditionally,
    # so the factorial's divergence-off cells were unrunnable.
    divergence_channel_enabled: bool = True
    divergence_off_mode: str = "absent"

    def __post_init__(self):
        if not self.experiment_name and self.test_article:
            stem = Path(self.test_article).stem
            self.experiment_name = f"ref_{stem}"
        # Bug 5 fix: removed silent override of rho_earliest_round.
        # These parameters serve different purposes and must be
        # independently configurable.
        # Fail loud on a mistyped off_mode: silently falling back to a
        # default would make an ablation cell measure something other than
        # what its config declares.
        for _fname in ("feedback_off_mode", "divergence_off_mode"):
            _val = getattr(self, _fname)
            if _val not in DIRECTIVE_OFF_MODES:
                raise ValueError(
                    f"{_fname}={_val!r} is not a valid off-mode; "
                    f"expected one of {sorted(DIRECTIVE_OFF_MODES)}"
                )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RunnerConfig":
        """Build config from a JSON-compatible dict (ignores unknown keys)."""
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        # Back-compat alias (routing rename 2026-07-12): the legacy config key
        # take_up_slack_enabled maps to the renamed field routing_enabled. Applied on
        # BOTH config-ingestion boundaries — here (the runner's own --config CLI) and
        # launcher_core.build_runner_config_from_dict — so the unchanged Exp 42/43
        # configs (which still carry take_up_slack_enabled) stay byte-identical in
        # behaviour regardless of launch path. New key wins if both are present.
        if "take_up_slack_enabled" in d and "routing_enabled" not in d:
            d = {**d, "routing_enabled": d["take_up_slack_enabled"]}
        kwargs = {k: v for k, v in d.items() if k in valid}
        # Capture shadow cell config from underscore-prefixed sections
        shadow = {}
        if "_macrophage" in d:
            shadow["_macrophage"] = d["_macrophage"]
        if "_ouroboros" in d:
            shadow["_ouroboros"] = d["_ouroboros"]
        if shadow:
            kwargs["shadow_cell_config"] = shadow
        return cls(**kwargs)

    @classmethod
    def from_json(cls, path: str) -> "RunnerConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


# ─────────────────────────────────────────────────────────────────────────────
# TARGET TYPE — the harness decides, the config only declares (A1, 2026-08-01)
# ─────────────────────────────────────────────────────────────────────────────
#
# WHY THIS EXISTS. Every mechanism in this runner that treats the target as
# compilable Python was written when every target WAS a Python module. Targets
# are now prose documents carrying claims plus fenced Python listings, and each
# of those mechanisms fails on prose SILENTLY — the S_k hard gates rejected 100%
# of fixes on the 2026-08-01 control, ruff error-recovered over markdown and
# reported ~2752 phantom diagnostics as a baseline, and bandit could not parse
# the file at all so it reported "0 HIGH / 0 MEDIUM" forever at the heaviest
# weight. Measured end to end, a fix injecting
# ``subprocess.call("rm -rf ...", shell=True)`` into a fenced listing scored
# sk=1.0000 ADMISSIBLE while a correct prose fix scored 0.6667: the ranking was
# inverted and nothing was ever rejected.
#
# WHY IT IS NOT A CONFIG FLAG. The launcher has silently dropped config keys six
# times (routing, max_contested_rounds, feedback_channel_enabled, the gamma/stall
# trio, and twenty latent fields found by sweep on 2026-08-01). A safety property
# whose enforcement depends on a key surviving two ingestion paths is not
# enforced. The config MAY declare `target_kind`; the harness reads the actual
# path and the actual bytes and DECIDES, and a declaration that disagrees with
# what is on disk is an error that stops the run.

TARGET_KIND_PYTHON = "python_module"
TARGET_KIND_PROSE = "prose"
TARGET_KINDS = (TARGET_KIND_PYTHON, TARGET_KIND_PROSE)

# Suffixes that name a Python module, and suffixes that name a prose document.
# Anything else is decided on content alone.
_PY_SUFFIXES = frozenset({".py", ".pyi"})
_PROSE_SUFFIXES = frozenset({
    ".md", ".markdown", ".mdown", ".mkd", ".rst", ".txt", ".text", ".org",
})
# A fenced block opener at the start of a line. Markdown's most reliable
# machine-detectable marker, and the one that matters here because a fenced
# Python listing inside prose is exactly what makes prose look scoreable.
_FENCE_OPEN_RE = re.compile(r"^[ \t]*(?:```|~~~)", re.M)


class TargetKindMismatch(RuntimeError):
    """The config declared one target kind and the target on disk is another.

    Raised, never logged-and-continued. A mismatch means the person who wrote
    the config believes the run is doing something other than what it is about
    to do, and every prose-versus-code mechanism in the runner branches on the
    answer. There is no safe default for "the two disagree".
    """


def _parses_as_python(text: str) -> bool:
    """True iff the whole text is syntactically valid Python."""
    try:
        ast.parse(text)
    except (SyntaxError, ValueError, MemoryError, RecursionError):
        return False
    return True


def detect_target_kind(
    path: str, text: Optional[str] = None,
) -> Tuple[str, str]:
    """Classify a target from its PATH and its CONTENT. Returns (kind, reason).

    The rule is deliberately ASYMMETRIC, and the asymmetry is the whole safety
    argument. Misreading prose as a Python module is the failure that inverted
    the fix ranking and admitted a shell-injection fix at sk=1.0. Misreading a
    Python module as prose only forgoes S_k scoring on that run — degraded, and
    loudly so, but not dangerous. So every ambiguous case resolves to `prose`.

    Concretely:

    * A ``.py`` / ``.pyi`` suffix means `python_module` — UNLESS the bytes
      refuse to parse as Python *and* carry fenced blocks, which is a prose
      document wearing a code extension.
    * A prose suffix (``.md``, ``.txt``, ``.rst``, …) means `prose`,
      unconditionally. A markdown file that happens to parse as Python (a short
      one easily can — ``Hello`` is a valid expression statement) is still
      prose, because its *fences* are what the panel and the gates will meet.
    * No recognised suffix: the content decides, and only content that parses
      as Python AND carries no fences AND is non-empty earns `python_module`.
    * No content supplied and no recognised suffix: `prose`, the safe side.

    `text` is optional so that a caller holding only a path can still classify;
    passing the bytes is strictly better and every in-runner caller does.
    """
    suffix = Path(path).suffix.lower() if path else ""
    has_fence = bool(text is not None and _FENCE_OPEN_RE.search(text))

    if suffix in _PY_SUFFIXES:
        if text is not None and has_fence and not _parses_as_python(text):
            return TARGET_KIND_PROSE, (
                f"suffix {suffix} claims Python, but the content does not parse "
                f"as Python and carries fenced blocks — a prose document under a "
                f"code extension")
        return TARGET_KIND_PYTHON, f"suffix {suffix}"

    if suffix in _PROSE_SUFFIXES:
        return TARGET_KIND_PROSE, f"suffix {suffix}"

    if text is None:
        return TARGET_KIND_PROSE, (
            f"unrecognised suffix {suffix or '(none)'} and no content available "
            f"— classified prose, the side that disables scoring")
    if not text.strip():
        return TARGET_KIND_PROSE, "empty target"
    if has_fence:
        return TARGET_KIND_PROSE, (
            f"unrecognised suffix {suffix or '(none)'}; content carries fenced "
            f"blocks")
    if _parses_as_python(text):
        return TARGET_KIND_PYTHON, (
            f"unrecognised suffix {suffix or '(none)'}; content parses as Python "
            f"with no fenced blocks")
    return TARGET_KIND_PROSE, (
        f"unrecognised suffix {suffix or '(none)'}; content does not parse as "
        f"Python")


def resolve_target_kind(
    path: str, text: Optional[str] = None, declared: Optional[str] = None,
) -> Tuple[str, str]:
    """Detect the target kind and check any declaration against it.

    Returns (kind, reason). Raises :class:`TargetKindMismatch` when `declared`
    is a value this module does not know, or when it names a kind other than
    the one detected. The detected kind is what is returned in every case that
    returns at all — a declaration can veto a run, never redirect it.
    """
    kind, reason = detect_target_kind(path, text)
    if declared in (None, ""):
        return kind, reason
    if declared not in TARGET_KINDS:
        raise TargetKindMismatch(
            f"config declares target_kind={declared!r}, which is not one of "
            f"{list(TARGET_KINDS)}. The harness classifies "
            f"{path!r} as {kind} ({reason})."
        )
    if declared != kind:
        raise TargetKindMismatch(
            f"REFUSING TO START: config declares target_kind={declared!r} but "
            f"the harness classifies {path!r} as {kind!r} ({reason}). The "
            f"harness decides; a declaration exists only so that a disagreement "
            f"is loud. Fix the config or the target, not this check."
        )
    return kind, reason


# ─────────────────────────────────────────────────────────────────────────────
# S_k Solution Verification — Data Structures
# ─────────────────────────────────────────────────────────────────────────────

# S_k outcome values. NO_SCORE is NOT a third grade of admissibility — it is the
# statement that S_k has no opinion, because the target is not the substrate S_k
# was defined over. Kept distinct from ADMISSIBLE (a scored pass), REJECTED (a
# scored fail) and ESCALATE (scoreable, but the evidence gates went silent).
SK_ADMISSIBLE = "ADMISSIBLE"
SK_REJECTED = "REJECTED"
SK_ESCALATE = "ESCALATE"
SK_NO_SCORE = "NO_SCORE"


@dataclass
class FixBlock:
    """A single SEARCH/REPLACE edit block parsed from model output."""
    file_path: str
    search: str
    replace: str


@dataclass
class SkResult:
    """Result of S_k computation for a proposed fix."""
    sk: float
    A: float  # product of hard gates (binary admissibility)
    E: float  # weighted effect evidence aggregate
    # ADMISSIBLE | REJECTED | ESCALATE | NO_SCORE.
    # Historically three values, hence the name. NO_SCORE (2026-08-01) is the
    # fourth and is not a grade: it means S_k did not run because the target is
    # not Python. Readers that branch on this field MUST handle it explicitly —
    # folding it into REJECTED slanders a fix that was never assessed, and
    # folding it into ADMISSIBLE admits one.
    tristate: str
    gate_details: Dict[str, Any] = field(default_factory=dict)
    blocks_parsed: int = 0
    blocks_applied: int = 0


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
        # Set once per run by the runner (see `registry.target_kind = ...`).
        # Defaults to Python so an un-updated caller gets the historical prompt
        # rather than a wrong one. Read only by build_summary.
        self.target_kind: str = TARGET_KIND_PYTHON

    def register(self, finding: Finding, model_id: str) -> str:
        canonical_id = f"C{self._next_id:04d}"
        self._next_id += 1
        self._alias_map[f"{model_id}:{finding.finding_id}"] = canonical_id
        self.entries[canonical_id] = {
            "canonical_id": canonical_id,
            "source_model": model_id,
            "source_aliases": [finding.finding_id],
            "severity": finding.severity,
            # RAISED 500 -> 2000 on 2026-08-17. The 500 had been in place since
            # commit 54d956e (2026-04-17) and clipped 661 of 2247 archived
            # descriptions, 29% of the corpus.
            #
            # This is the STORED value, and three live consumers read it: the
            # location-keyed convergence count (:4288), the CC2 verification pass
            # where a model casts CONFIRM/REFUTE/DUPLICATE/ESCALATE (:6271), and
            # the routing ladder (:2982). The ladder asks for [:1200] and, with a
            # 500-char store, could never receive more than 500 — it requested
            # more than the system was capable of holding and got no signal that
            # it had been short-changed.
            #
            # 2000 rather than unbounded: it clears the largest downstream request
            # with headroom, and worst-case archive growth is about 1 MB. Nothing
            # keys off the value 500 — the other two occurrences in this file
            # (:6271, :9466) are each a consumer's own prompt/report budget and
            # are deliberately left alone, since those are separate decisions
            # about what to SHOW, not about what to KEEP.
            "description": finding.description[:2000],
            "proposed_fix": finding.proposed_fix[:5000] if finding.proposed_fix else "",
            # "tools decide" gate: the model-attached runnable falsifier + the
            # runner's independent re-run verdict (see apply_falsifier_verdicts).
            "falsifier_code": getattr(finding, "falsifier_code", ""),
            "falsifier_verdict": getattr(finding, "falsifier_verdict", ""),
            "status": "OPEN",
            "open_since_round": getattr(finding, "round_idx", 0),
            "last_status_change_round": getattr(finding, "round_idx", 0),
            "verdicts": [],
            "verified": finding.verified,
            "escalated": finding.escalated,
            "flaw_class": getattr(finding, "flaw_class", 0),
            "origin_type": getattr(finding, "origin_type", ""),
            "source_ref": getattr(finding, "source_ref", ""),
            "retrieval_query": getattr(finding, "retrieval_query", ""),
            "retrieved_at": getattr(finding, "retrieved_at", ""),
            "source_hash": getattr(finding, "source_hash", ""),
            "source_diversity": getattr(finding, "source_diversity", 0.0),
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
        # F2/F5/F9 fix: do NOT update last_status_change_round here.
        # Verdicts are evidence, not status transitions. Only resolve()
        # should update the timer, preventing escalation timer corruption.

    def resolve(
        self, canonical_id: str, status: str, round_idx: int,
        merged_into: Optional[str] = None,
    ):
        if canonical_id not in self.entries:
            return
        # MERGE GUARDS, added 2026-08-18. Applied here rather than at each call
        # site because this is the single chokepoint every merge passes through.
        #
        # `cdsfl_topology_formal.md:110-111` requires the target to exist and be
        # live before any MERGE, and :129-131 requires the merge graph be acyclic.
        # Neither was enforced. Measured on the archive: exp37 carries a finding
        # MERGED INTO ITSELF at severity 0.86, and 21 of exp36's 86 merged entries
        # sit inside a cycle, so the pointer chain never reaches a surviving entry
        # and the whole family disappears from the gate.
        #
        # A refused merge leaves the finding where it was — OPEN and visible —
        # which is the safe direction. A merge into a phantom, a self, or a cycle
        # silently deletes a finding that may be real.
        if merged_into:
            if merged_into == canonical_id:
                return                                    # self-merge
            if merged_into not in self.entries:
                return                                    # phantom target
            # Walk the existing chain; refuse if it leads back to this finding.
            seen, cur = {canonical_id}, merged_into
            while cur is not None and cur not in seen:
                seen.add(cur)
                cur = (self.entries.get(cur) or {}).get("merged_into")
            if cur is not None:
                return                                    # would close a cycle
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
        """Count active non-terminal critical/high findings.

        Pure reader — no state mutation. Exhausted findings (marked by
        _update_finding_statuses) are excluded from the count.
        Gate threshold stays fixed; finding eligibility changes.
        """
        _NON_TERMINAL = ("OPEN", "CONTESTED", "REOPENED")
        count = 0
        for e in self.entries.values():
            if e["status"] not in _NON_TERMINAL or e["severity"] < 0.7:
                continue
            if e.get("exhausted"):
                continue
            count += 1
        return count

    def unverified_critical_count(self) -> int:
        """A4 fail-safe signal: UNCONFIRMED critical-severity candidates.

        Pure reader — no state mutation. Counts entries with status
        UNCONFIRMED and severity >= CRITICAL_SEVERITY_THRESHOLD: critical
        candidates the system gave up on (finalize sweep / grace-period
        reopen) WITHOUT verification. These are excluded from the settled
        novelty series, so they would otherwise silently count as "zero
        new critical." The convergence count path must not accrue while
        any of these are pending. CONFIRMED/CLOSED (resolved) and
        MERGED/DUPLICATE/REFUTED (adjudicated terminal) are NOT counted;
        OPEN/CONTESTED/REOPENED are in-play and visible to the settled
        series + state gate, so they are NOT counted here either.
        """
        count = 0
        for e in self.entries.values():
            if e.get("status") != "UNCONFIRMED":
                continue
            # Static-queue closure (2026-06-09): a critical locked as irreducible AFTER
            # the full routing ladder was exhausted (no model could write a runnable test)
            # is HANDED OFF to the human, not "pending verification". It must NOT block the
            # automated loop forever (else the run hits the round cap instead of converging).
            # It is counted separately by irreducible_queue_count() and guarded by the
            # small-queue alarm.
            if e.get("irreducible_escalation"):
                continue
            if (e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD:
                count += 1
        return count

    def irreducible_queue_count(self) -> int:
        """Static HIL queue: criticals locked as irreducible AFTER the full routing
        ladder was exhausted without any model producing a runnable test. These are
        handed to the human outside the automated loop (the substrate-agnostic final
        falsifier). They are excluded from the A4 'unverified pending' blocker so the
        loop can close around them — BUT a LARGE such queue is a mechanical-failure
        alarm (routing/dedup), not genuine irreducibility, and refuses convergence."""
        # Exp 44 post-run fix (2026-07-27, founder-approved): exclude terminal
        # statuses — a later-round routing success CLOSES the entry, and a
        # resolved item must not keep occupying the queue (6 stale flags read
        # as "6 irreducible" where the truth was 0, and on the gamma-alt path
        # the stale count would have FALSELY refused a genuine convergence).
        _TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
        return sum(
            1 for e in self.entries.values()
            if e.get("irreducible_escalation")
            and e.get("status") not in _TERMINAL
            and (e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD
        )

    def contested_count(self, current_round: int, grace_period: int = 2,
                        subcritical_exclusion: bool = False) -> int:
        """Count actively contested non-terminal findings.

        Pure reader — no state mutation. UNCONFIRMED reopens are handled
        by _update_finding_statuses() before this is called.

        - MERGED/CLOSED/REFUTED/DUPLICATE: irrecoverable terminal, always excluded.
        - UNCONFIRMED: counted during grace period only.
        """
        _IRRECOVERABLE = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
        count = 0
        for e in self.entries.values():
            if e["status"] in _IRRECOVERABLE:
                continue
            # UNCONFIRMED: grace period read-only check
            if e["status"] == "UNCONFIRMED":
                # FIX 1 (Exp 43, 2026-07-22): an UN-DEMONSTRATED SUB-CRITICAL
                # must not gate convergence. The falsifier gate + routing are
                # critical-only, so a sub-critical whose falsifier errored or
                # is absent can never be tool-resolved; counting it as
                # "contested" hands an unfalsified claim veto power over the
                # gate — contra "unfalsified earns zero corroboration". It is
                # excluded here and surfaced via undemonstrated_subcritical_ids()
                # as a residual review queue instead. Criticals keep full
                # protection (grace count here + open_crit_high_count).
                # z3-verified: this never lets a critical-contested finding pass.
                # Adversarial-pass repairs (2026-07-27): (FM-2) exclusion is
                # OPT-IN via subcritical_exclusion (threaded from
                # cfg.falsifier_gate_enabled) — default-off keeps legacy/gate-off
                # runs byte-identical; (FM-1) an entry carrying an UNRESOLVED
                # CHALLENGE is genuine model disagreement and is NEVER excluded,
                # whatever its severity or falsifier state.
                sev = float(e.get("severity") or 0.0)
                if (subcritical_exclusion
                        and sev < CRITICAL_SEVERITY_THRESHOLD
                        and e.get("falsifier_verdict") != "CONFIRMED"):
                    _ch = [v for v in e["verdicts"] if v["verdict"] == "CHALLENGE"]
                    _cf = max((v["round"] for v in e["verdicts"]
                               if v["verdict"] == "CONFIRM"), default=-1)
                    if not any(v["round"] >= _cf for v in _ch):
                        continue
                rounds_in_status = current_round - e.get("last_status_change_round", 0)
                if rounds_in_status < grace_period:
                    count += 1
                # else: grace expired — excluded (reopen handled elsewhere)
                continue
            # Non-terminal, non-UNCONFIRMED: standard contested logic
            challenges = [v for v in e["verdicts"] if v["verdict"] == "CHALLENGE"]
            if not challenges:
                continue
            confirms = [v for v in e["verdicts"] if v["verdict"] == "CONFIRM"]
            latest_confirm_round = max((v["round"] for v in confirms), default=-1)
            unresolved = [v for v in challenges if v["round"] >= latest_confirm_round]
            if unresolved:
                oldest = min(v["round"] for v in unresolved)
                if current_round - oldest >= grace_period:
                    count += 1
        return count

    def undemonstrated_subcritical_ids(self) -> List[str]:
        """FIX 1 residual queue: UNCONFIRMED sub-criticals with no CONFIRMED
        demonstration (falsifier errored/absent). Excluded from
        contested_count(); surfaced here for logging + human review."""
        out = []
        for cid, e in self.entries.items():
            if (e["status"] == "UNCONFIRMED"
                    and float(e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD
                    and e.get("falsifier_verdict") != "CONFIRMED"):
                out.append(cid)
        return out

    # Cap full-detail active entries to bound context growth.
    # Overflow entries get compact one-line treatment.
    # (Ported from run_exp37_evidence.py line 227 + 444-478)
    MAX_FULL_DETAIL_OPEN = 20

    def build_summary(self, round_idx: int) -> str:
        """A1 fix: windowed registry summary with overflow cap."""
        if not self.entries:
            return "(No findings registered yet.)"
        full_detail_statuses = ("OPEN", "CONTESTED", "REOPENED")
        compact_statuses = ("CONFIRMED", "UNCONFIRMED", "CLOSED", "MERGED")
        hidden_statuses = ("REFUTED", "DUPLICATE")
        full_detail = [e for e in self.entries.values() if e["status"] in full_detail_statuses]
        compact = [e for e in self.entries.values() if e["status"] in compact_statuses]
        hidden_count = sum(1 for e in self.entries.values() if e["status"] in hidden_statuses)

        # Bugzilla paradigm header (added 15 May 2026). Make the finding
        # state machine explicit to the panel so models understand which
        # findings are still in play, which are settled, and how settled
        # findings reached terminal state. Without this, models would
        # rediscover and re-describe canonical entries indefinitely.
        closed_count = sum(
            1 for e in self.entries.values()
            if e.get("status") == "CLOSED"
        )
        bugzilla_verified_count = sum(
            1 for e in self.entries.values()
            if e.get("bugzilla_verified")
        )
        lines = [
            f"=== FINDING REGISTRY (Round {round_idx}) ===",
            "State machine (Bugzilla paradigm):",
            "  OPEN -> CONFIRMED (>=2 independent verifications)",
            "  CONFIRMED + verified fix -> CLOSED (terminal, challenge-resistant)",
            "  CONFIRMED + late challenge -> CONTESTED",
            "  CLOSED -> REOPENED (only with new evidence via REOPEN verdict)",
            "  DUPLICATE -> MERGED into the canonical entry",
            "",
            # This paragraph is what the panel is told about how a finding
            # settles, every model, every round. It described ruff + mypy +
            # bandit + pytest unconditionally. On a prose target NONE of that
            # runs — the tri-state repair of 2026-08-01 made a clean parse
            # return NO_APPLICABLE_CHECKS, which does not close — so the panel
            # was being briefed on a state machine that no longer exists and
            # would reasonably conclude a proposed fix was the route to closure.
            # It is not. On a prose target the route is a runnable falsifier.
            *([
                "This target is a PROSE DOCUMENT, not Python source. A proposed",
                "fix is NOT tool-verified here: ruff/mypy/bandit/pytest have no",
                "purchase on prose, so a fix alone cannot close a finding. A",
                "finding settles when it carries a RUNNABLE FALSIFIER that the",
                "runner re-runs itself and confirms — a test that opens this",
                "document by path and asserts on its text, or on a value",
                "recomputed from it, or on a listing extracted from it.",
                "Propose fixes as usual; they are recorded for the human. But",
                "the falsifier is what settles the finding.",
            ] if self.target_kind == TARGET_KIND_PROSE else [
                "When a CONFIRMED finding carries a parseable proposed_fix in",
                "SEARCH/REPLACE format, the runner applies it to a sandbox copy",
                "of the target file and runs ruff + mypy + bandit + the",
                "experiment's test suite. On clean pass, the finding transitions",
                "to CLOSED and is removed from the active discovery pool.",
            ]),
            "Findings already CLOSED below: do not re-describe them.",
            "",
            f"Total: {len(self.entries)} canonical findings",
            f"Active: {len(full_detail)} | Settled: {len(compact)} | Hidden: {hidden_count}",
            f"Open CRIT/HIGH: {self.open_crit_high_count()} | "
            f"CLOSED: {closed_count} ({bugzilla_verified_count} via programmatic fix-verification)",
            "",
        ]
        # Cap full-detail entries by severity to bound context growth.
        all_active_sorted = sorted(full_detail, key=lambda x: -x["severity"])
        full_detail_shown = all_active_sorted[:self.MAX_FULL_DETAIL_OPEN]
        full_detail_overflow = all_active_sorted[self.MAX_FULL_DETAIL_OPEN:]
        for status in full_detail_statuses:
            group = [e for e in full_detail_shown if e["status"] == status]
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
                # A10 (panel-converged MUST list). The machinery rejected 50
                # proposed fixes across 4 rounds of Exp 53 and told no model
                # why — so every round the panel re-proposed into a gate it
                # could not see. This is the founder's own design point: when
                # the machinery declines something, the claim goes BACK to the
                # panel rather than being quietly filed. A rejection the panel
                # can read is a rejection it can answer.
                for _line in _rejection_lines(e):
                    lines.append(f"    {_line}")
            lines.append("")
        # Overflow active findings: compact one-line (lower severity)
        if full_detail_overflow:
            lines.append(
                f"--- ACTIVE OVERFLOW ({len(full_detail_overflow)}) "
                f"(lower severity, compact) ---"
            )
            for e in full_detail_overflow:
                lines.append(
                    f"  {e['canonical_id']} (sev {e['severity']:.2f}) "
                    f"[{e['status']}] {e['description'][:80]}"
                )
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

    def escalate_stale_contested(self, current_round: int, max_contested_rounds: int = 5,
                                 grace_period: int = 2) -> List[str]:
        """A3 fix: escalate stale contested findings to HIL after threshold.

        D2 fix (Exp 38): also covers OPEN findings with old unresolved
        challenges — matching what contested_count() actually reports.
        Previously only checked explicit CONTESTED status, missing findings
        that contested_count counted via verdict history.
        """
        _SKIP = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
        escalated_ids = []
        for fid, entry in self.entries.items():
            if entry["status"] in _SKIP:
                continue
            # Path 1: explicit CONTESTED status (original logic)
            if entry["status"] == "CONTESTED":
                contested_since = entry.get("last_status_change_round", 0)
                rounds_contested = current_round - contested_since
                if rounds_contested >= max_contested_rounds:
                    self.resolve(fid, "UNCONFIRMED", current_round)
                    entry["hil_escalated"] = True
                    entry["hil_reason"] = (
                        f"Contested for {rounds_contested} rounds "
                        f"(threshold: {max_contested_rounds})"
                    )
                    escalated_ids.append(fid)
                    _log(f"  D2 HIL escalation: {fid} CONTESTED for "
                         f"{rounds_contested}r -> UNCONFIRMED + HIL flag")
                continue
            # Path 2: OPEN/REOPENED with stale unresolved challenges
            if entry["status"] in ("OPEN", "REOPENED"):
                challenges = [v for v in entry["verdicts"] if v["verdict"] == "CHALLENGE"]
                if not challenges:
                    continue
                confirms = [v for v in entry["verdicts"] if v["verdict"] == "CONFIRM"]
                latest_confirm = max((v["round"] for v in confirms), default=-1)
                unresolved = [v for v in challenges if v["round"] >= latest_confirm]
                if not unresolved:
                    continue
                oldest = min(v["round"] for v in unresolved)
                if current_round - oldest >= max_contested_rounds:
                    self.resolve(fid, "UNCONFIRMED", current_round)
                    entry["hil_escalated"] = True
                    entry["hil_reason"] = (
                        f"Unresolved challenge from R{oldest}, age "
                        f"{current_round - oldest} rounds "
                        f"(threshold: {max_contested_rounds})"
                    )
                    escalated_ids.append(fid)
                    _log(f"  D2 HIL escalation: {fid} unresolved challenge "
                         f"since R{oldest} -> UNCONFIRMED + HIL flag")
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
                # F6 fix: use resolve() instead of direct mutation.
                self.resolve(fid, "REFUTED", current_round)
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
    # F13 fix: C\d{4,} supports IDs beyond 9999
    # F19 fix: bare | inside character class (no backslash needed)
    # 1D.6 fix: broadened Gemini format coverage. Original missed
    # bold-wrapped keyword alone (**CONFIRM**), bullet+bold combinations,
    # numbered-list prefixes (1. / 1)), blockquote prefixes (>), and
    # colon/period separators after the canonical ID.
    r'^[ \t]*'                                  # line start + indent
    r'(?:>[ \t]*)?'                             # optional blockquote
    r'(?:[-*][ \t]+|\d+[.)][ \t]+)?'            # optional bullet or numbered-list prefix
    r'(?:\*{1,2}|_{1,2})?'                      # optional bold/italic opener
    r'(CONFIRM|CHALLENGE|EXTEND|MERGE|REOPEN)'
    r'(?:\*{1,2}|_{1,2})?'                      # optional bold/italic closer on keyword
    r'[ \t]+'
    r'(?:\*{1,2}|_{1,2})?'                      # optional bold opener on canonical ID
    r'(C\d{4,})'
    r'(?:\*{1,2}|_{1,2})?'                      # optional bold closer on canonical ID
    # Optional description separator + description.
    # Separators now include `:` and `.` (Gemini uses both), in addition to
    # `|`, `<`, `-`, em-dash, en-dash, left-arrow.
    r'(?:[ \t]*(?:\*{1,2}|_{1,2})?[ \t]*[|<:.\-\u2014\u2013\u2190]+[ \t]*(.*))?',
    re.MULTILINE,
)


_VERDICT_TRAILING_FORMAT = re.compile(r'[\s*_]+$')


def _parse_verdicts(
    response_text: str, model_id: str, round_idx: int,
) -> List[Tuple[str, str, str]]:
    results: List[Tuple[str, str, str]] = []
    for m in _VERDICT_RE.finditer(response_text):
        description = (m.group(3) or "").strip()
        # Strip trailing markdown format chars (** / __) when the whole
        # verdict line was bold-wrapped.
        description = _VERDICT_TRAILING_FORMAT.sub("", description).strip()
        results.append((m.group(1), m.group(2), description))
    return results


def _resolve_merge_source(
    evidence: str, model_id: str, registry: FindingRegistry,
) -> Optional[str]:
    m = re.search(r'(?:F|C)(\d+)', evidence)
    if not m:
        return None
    local_id = m.group(0)
    # ALIAS-KEY NORMALISATION, repaired 2026-08-18.
    #
    # The regex above strips any model prefix, so `Codex_F001` reduces to `F001`.
    # But `parse_findings` mints finding ids ALREADY PREFIXED — it returns
    # `Codex_F001`, not `F001` — so `register()` writes the alias key
    # `Codex:Codex_F001`. Looking up `Codex:F001` therefore missed every time,
    # and BOTH forms a model can plausibly write failed:
    #
    #     MERGE C0001 <- F001         -> None      (the form FINDING_FORMAT teaches)
    #     MERGE C0001 <- Codex_F001   -> None      (the form the runner itself mints)
    #     MERGE C0001 <- C0001        -> C0001     (canonical only)
    #
    # An unresolved source is not dropped: `cdsfl_topology_formal.md:126-127`
    # MANDATES treating it as a CONFIRM on the target. So the failure was silent
    # and it inverted the verdict — a model saying "these two are the same defect"
    # was recorded as a model AGREEING the target is real. The spec is right and
    # the resolver was wrong, which is why the repair belongs here and not at the
    # call site.
    for candidate in (local_id, f"{model_id}_{local_id}"):
        canonical = registry.lookup_alias(model_id, candidate)
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
    if not raw_counts:
        return 0.0, 0.0, False
    # Bug 1 fix: compute rolling average even when current round has zero raw.
    # A zero-raw round should drive the average DOWN, not freeze it.
    rho_current = novelty_counts[-1] / raw_counts[-1] if raw_counts[-1] > 0 else 0.0
    rho_values = []
    for i in range(max(0, len(raw_counts) - cfg.rho_rolling_window), len(raw_counts)):
        if raw_counts[i] > 0:
            rho_values.append(novelty_counts[i] / raw_counts[i])
        else:
            rho_values.append(0.0)
    rho_avg = sum(rho_values) / len(rho_values) if rho_values else 0.0
    # Bug 4 fix: len(raw_counts) is 1-based (one entry per completed round).
    # Using len-1 compared against a 1-based threshold delays churn by one round.
    round_number = len(raw_counts)
    churn = rho_avg < cfg.rho_threshold and round_number >= cfg.rho_earliest_round
    return rho_current, rho_avg, churn


# ─────────────────────────────────────────────────────────────────────────────
# G7 merge-arbitration integration seam
# ─────────────────────────────────────────────────────────────────────────────

def _try_merge_arbitration(
    entry: dict, canonical_id: str, by_target: dict,
    registry: "FindingRegistry", round_idx: int, defer_count: int,
) -> Optional[str]:
    """Attempt G7 compelled-convergence arbitration for one deferred
    finding.

    Inert unless `_merge_arb_ctx` is populated AND enabled AND the
    finding has hit the min-defer threshold AND per-round budget
    remains. Returns:
        "MERGED"        — arbitration merged it (caller should continue)
        "KEEP_DISTINCT" — arbitration kept it distinct (caller continue)
        None            — no arbitration (caller falls through to the
                           existing defer/deadlock logic, unchanged)
    """
    ctx = _merge_arb_ctx
    if not ctx or not ctx.get("enabled"):
        return None
    if defer_count < ctx.get("min_defer_count", 2):
        return None
    if ctx.get("used_this_round", 0) >= ctx.get("max_per_round", 3):
        return None
    panel = ctx.get("panel") or []
    dispatch_fn = ctx.get("dispatch_fn")
    if not panel or dispatch_fn is None:
        return None

    try:
        from bench.merge_arbitration import dispatch_merge_arbitration
    except Exception as e:  # module missing — degrade to legacy defer
        _log(f"  G7 arbitration unavailable ({e}) — falling back to "
             f"MERGE DEFERRED for {canonical_id}")
        return None

    # Build the new-finding + candidate dicts from registry state.
    new_finding = {
        "finding_id": canonical_id,
        "description": entry.get("description", ""),
        "proposed_fix": entry.get("proposed_fix", ""),
        "target_file": entry.get("target_file", ""),
        "severity": entry.get("severity", ""),
    }
    candidates = []
    for tid in by_target:
        if tid == "__unknown__":
            continue
        tgt = registry.entries.get(tid)
        if tgt is None:
            continue
        candidates.append({
            "canonical_id": tid,
            "description": tgt.get("description", ""),
        })
    if len(candidates) < 2:
        # Arbitration only meaningful with ≥2 real candidates.
        return None

    ctx["used_this_round"] = ctx.get("used_this_round", 0) + 1
    result = dispatch_merge_arbitration(
        new_finding, candidates, panel, dispatch_fn,
        majority=ctx.get("majority", 3), log_fn=_log,
    )
    ctx.setdefault("log", []).append({
        "round": round_idx, **result.to_dict(),
    })

    if result.decision == "MERGE" and result.target:
        registry.resolve(canonical_id, "MERGED", round_idx,
                          merged_into=result.target)
        _log(f"  G7 MERGE ARBITRATED {canonical_id} -> "
             f"{result.target}: {result.rationale}")
        return "MERGED"
    if result.decision == "KEEP_DISTINCT":
        # Abandon the auto-merge attempt; the finding stays its own
        # canonical entry. Clear pending MERGE verdicts so the
        # deadlock does not re-trigger next round on stale votes.
        entry["verdicts"] = [
            v for v in entry.get("verdicts", [])
            if v.get("verdict") != "MERGE"
        ]
        entry["merge_defer_count"] = 0
        entry["g7_kept_distinct_round"] = round_idx
        _log(f"  G7 KEEP DISTINCT {canonical_id}: {result.rationale}")
        return "KEEP_DISTINCT"
    # DEFER — caller falls through to existing logic unchanged.
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Status transitions and convergence gate
# ─────────────────────────────────────────────────────────────────────────────

def _update_finding_statuses(registry: FindingRegistry, round_idx: int,
                             cfg: Optional[RunnerConfig] = None):
    # Bugzilla close-the-loop attempt counter for this call. Reset at
    # the start of every _update_finding_statuses invocation (i.e. once
    # per round) so the per-round cap is enforced independently of any
    # caller-side state.
    _bugzilla_attempts_this_call = 0

    # ── Pre-pass 1: Mark/clear EXHAUSTED on critical/high findings ──
    # Derived fresh each call — not sticky. Requires review activity.
    exhausted_threshold = cfg.exhausted_round_threshold if cfg else 0
    for e in registry.entries.values():
        if e["status"] in ("OPEN", "CONTESTED") and e["severity"] >= 0.7:
            age = round_idx - e.get("last_status_change_round", 0)
            has_reviews = len(e.get("verdicts", [])) > 0
            if exhausted_threshold > 0 and age >= exhausted_threshold and has_reviews:
                e["exhausted"] = True
            else:
                e["exhausted"] = False
        else:
            e.pop("exhausted", None)

    # ── Pre-pass 2: Reopen UNCONFIRMED findings with new evidence ──
    grace_period = 2
    for cid, e in list(registry.entries.items()):
        if e["status"] == "UNCONFIRMED":
            rounds_in_status = round_idx - e.get("last_status_change_round", 0)
            if rounds_in_status >= grace_period:
                status_round = e.get("last_status_change_round", 0)
                new_verdicts = [v for v in e["verdicts"] if v["round"] > status_round]
                if new_verdicts:
                    registry.resolve(cid, "OPEN", round_idx)
                    _log(f"  REOPEN {cid}: new evidence after UNCONFIRMED")

    # ── Main pass ──
    for canonical_id, entry in list(registry.entries.items()):
        # ── Terminal statuses: only CLOSED can be reopened ──
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

        # ── MERGE: contextual quorum (Round 2 confer design) ──
        # Floor: never merge without target consensus. Never merge on 0 votes.
        # Contextual: 2+ models on same target = pass. 1 model on small panel
        # with high confidence = pass + HIL flag. Target disagreement = defer.
        merge_verdicts = [v for v in entry["verdicts"] if v["verdict"] == "MERGE"]
        if merge_verdicts:
            # Extract per-vote targets
            by_target: dict[str, list] = {}
            for v in merge_verdicts:
                m = re.search(r'merged_into=(C\d{4,})', v.get("evidence", ""))
                target = m.group(1) if m else "__unknown__"
                by_target.setdefault(target, []).append(v)

            if len(by_target) > 1:
                # D4 fix: quorum-based merge arbitration.
                # If one target has strictly more votes, merge to it.
                # On genuine tie, defer with HIL escalation after threshold.
                sorted_targets = sorted(by_target.items(),
                                        key=lambda kv: len(kv[1]), reverse=True)
                top_target, top_votes = sorted_targets[0]
                second_votes = len(sorted_targets[1][1]) if len(sorted_targets) > 1 else 0
                if (len(top_votes) > second_votes
                        and top_target != "__unknown__"):
                    distinct = {v["model"] for v in top_votes}
                    if len(distinct) >= 2:
                        registry.resolve(canonical_id, "MERGED", round_idx,
                                         merged_into=top_target)
                        _log(f"  D4 MERGE QUORUM {canonical_id} -> {top_target}: "
                             f"{len(top_votes)} votes vs {second_votes}")
                        continue
                # Genuine tie or insufficient quorum — defer
                defer_count = entry.get("merge_defer_count", 0) + 1
                entry["merge_defer_count"] = defer_count
                max_defer = cfg.max_contested_rounds if cfg else 5
                # G7 (Exp 40 continuation): before logging DEFERRED or
                # escalating to D4 HIL deadlock, attempt compelled-
                # convergence arbitration. Inert unless explicitly
                # enabled via cfg.merge_arbitration_enabled (default
                # False → this is a no-op and the legacy defer/deadlock
                # logic below runs unchanged).
                _g7 = _try_merge_arbitration(
                    entry, canonical_id, by_target, registry,
                    round_idx, defer_count,
                )
                if _g7 in ("MERGED", "KEEP_DISTINCT"):
                    continue
                if defer_count >= max_defer:
                    # Deadlock: escalate to HIL, remove from active merge
                    entry["hil_escalated"] = True
                    entry["hil_reason"] = (
                        f"MERGE deadlock for {defer_count} rounds, "
                        f"targets: {', '.join(by_target.keys())}"
                    )
                    _log(f"  D4 MERGE DEADLOCK {canonical_id}: "
                         f"escalated to HIL after {defer_count} rounds")
                else:
                    _log(f"  MERGE DEFERRED {canonical_id}: target disagreement "
                         f"({', '.join(by_target.keys())}) [{defer_count}/{max_defer}]")
            else:
                target_id = next(iter(by_target))

                # R3-1 fix: block merge on unknown/unparseable targets
                if target_id == "__unknown__":
                    _log(f"  MERGE DEFERRED {canonical_id}: no parseable merge target")
                else:
                    target_votes = by_target[target_id]
                    distinct_models = {v["model"] for v in target_votes}
                    # R3-2 fix: panel size from config, not per-finding verdicts
                    external_panel_size = (
                        len(set(cfg.models) - {entry["source_model"]})
                        if cfg else len({v["model"] for v in entry["verdicts"]} - {entry["source_model"]})
                    )

                    if len(distinct_models) >= 2:
                        # Clear consensus — merge
                        registry.resolve(canonical_id, "MERGED", round_idx, merged_into=target_id)
                        continue
                    elif external_panel_size < 2 and len(distinct_models) == 1:
                        # Small panel: allow single vote + HIL flag + reversion gate
                        registry.resolve(canonical_id, "MERGED", round_idx, merged_into=target_id)
                        entry["hil_escalated"] = True
                        entry["hil_reason"] = (
                            f"Single-model merge (small panel, {external_panel_size} "
                            f"external models). Reversion available."
                        )
                        _log(f"  MERGED {canonical_id} (small panel, HIL flagged)")
                        continue
                    # else: insufficient quorum, do not merge this round

        # ── Collect verdict evidence ──
        confirms = [v for v in entry["verdicts"] if v["verdict"] == "CONFIRM"]
        challenges = [v for v in entry["verdicts"] if v["verdict"] == "CHALLENGE"]
        latest_confirm_round = max((v["round"] for v in confirms), default=-1)
        # F24 fix: use >= so same-round challenges count as unresolved.
        # Previously strict > meant a challenge in the same round as the
        # latest confirm was silently treated as resolved.
        unresolved_challenges = [v for v in challenges if v["round"] >= latest_confirm_round]

        # ── F0/F4 fix: check challenges BEFORE closing ──
        # Previously, CONFIRMED+verified closed immediately, skipping the
        # challenge check. Now: unresolved challenges take priority.
        if entry["status"] == "CONFIRMED" and unresolved_challenges:
            registry.resolve(canonical_id, "CONTESTED", round_idx)
            continue

        # ── Bugzilla CLOSED-loop (added 15 May 2026) ──
        # If CONFIRMED and not yet verified, attempt to programmatically
        # verify the proposed_fix: extract a SEARCH/REPLACE block, apply
        # to a sandbox copy of the target file, run ruff + mypy + bandit
        # + the experiment's test_cmd. If verification passes, mark
        # verified=True so the next check transitions to CLOSED.
        # Rate-limited per-round (BUGZILLA_PER_ROUND_LIMIT) to keep
        # wall-clock bounded. Exception-safe — Bugzilla errors don't
        # break the state machine. Module: bench/bugzilla_loop.py.
        if (
            entry["status"] == "CONFIRMED"
            and not entry.get("verified")
            and not entry.get("bugzilla_attempted")
            and entry.get("proposed_fix", "").strip()
        ):
            if _bugzilla_attempts_this_call < BUGZILLA_PER_ROUND_LIMIT:
                _bugzilla_attempts_this_call += 1
                entry["bugzilla_attempted"] = True
                try:
                    target_file = (
                        entry.get("target_file")
                        or (cfg.test_article if cfg else None)
                    )
                    if target_file:
                        from pathlib import Path as _Path
                        target_path = _Path(target_file)
                        if not target_path.is_absolute():
                            target_path = REPO_ROOT / target_file
                        if target_path.exists():
                            from bugzilla_loop import attempt_close
                            attempt = attempt_close(
                                {"finding_id": canonical_id,
                                 "proposed_fix": entry["proposed_fix"]},
                                target_path,
                                test_cmd=(cfg.test_cmd if cfg else None),
                                timeout=120,
                            )
                            if attempt.closed:
                                entry["verified"] = True
                                entry["bugzilla_verified"] = True
                                _log(
                                    f"  BUGZILLA CLOSED-loop verified "
                                    f"{canonical_id}: {attempt.reason[:160]}"
                                )
                            else:
                                _log(
                                    f"  BUGZILLA close-the-loop failed for "
                                    f"{canonical_id}: {attempt.reason[:160]}"
                                )
                except Exception as _bz_exc:
                    _log(
                        f"  BUGZILLA close-the-loop error for "
                        f"{canonical_id}: "
                        f"{type(_bz_exc).__name__}: {str(_bz_exc)[:160]}"
                    )

        if entry["status"] == "CONFIRMED" and entry.get("verified"):
            registry.resolve(canonical_id, "CLOSED", round_idx)
            _log(f"  CLOSED {canonical_id}: verified fix, no unresolved challenges")
            continue

        if entry["status"] == "CONTESTED" and not unresolved_challenges:
            registry.resolve(canonical_id, "CONFIRMED", round_idx)
            continue

        # F18 fix: use resolve() instead of direct mutation for REOPENED → OPEN.
        # Direct entry["status"] = "OPEN" bypassed last_status_change_round update.
        if entry["status"] == "REOPENED":
            registry.resolve(canonical_id, "OPEN", round_idx)

        if entry["status"] in ("OPEN", "CONTESTED"):
            confirm_models = {v["model"] for v in confirms}
            # F11 contextual: severity-based confirmation quorum.
            # Floor: at least 1 independent external confirmation (source excluded).
            # Critical/High: require 2. Medium/Low: require 1.
            # R3-4 fix: cap by available external panel size to prevent stalls.
            independent_count = len(confirm_models - {entry["source_model"]})
            sev = entry.get("severity", 0.5)
            external_panel_size = (
                len(set(cfg.models) - {entry["source_model"]})
                if cfg else 99
            )
            required = min(2, external_panel_size) if sev >= 0.7 else 1
            if independent_count >= required and not unresolved_challenges:
                registry.resolve(canonical_id, "CONFIRMED", round_idx)


# ─────────────────────────────────────────────────────────────────────────────
# DISCRIMINATION CONTROL — the false-CONFIRMED detector (founder ruling, 2026-08-08)
# ─────────────────────────────────────────────────────────────────────────────
#
# THE PROBLEM. A falsifier can be valid, runnable code and still be LOGICALLY
# WRONG — firing for a reason unconnected to the claim it purports to test. The
# runner sees it fire, marks the finding CONFIRMED, and closes it AGAINST A CLAIM
# THAT IS TRUE. C0012 is the archived instance: it fired because it read a file,
# not because the chemistry was wrong. Nothing in `reverify_falsifier` can catch
# this, and nothing should be asked to: the re-run is a faithful measurement of
# "did this code fire", and it answers that question correctly. The unasked
# question is "did it fire BECAUSE OF THE CLAIM".
#
# THE TEST. Run the SAME falsifier a second time against a CORRECTED copy of the
# target — one in which the claim under test has been fixed. A sound falsifier
# must now go QUIET. If it still fires, it is not testing that claim at all.
#
# WHERE THE CORRECTED COPY COMES FROM. It is ASKED FOR from the panel alongside
# the falsifier, and read here from ``entry["corrected_copy"]``. It is NEVER
# synthesised by applying the model's proposed fix: a fix with a bad indent or a
# missing import makes the falsifier CRASH, the crash reads as "still fires", and
# a genuine defect is silently un-confirmed. Two independent reviews killed that
# route on 2026-08-04 and the reasoning is recorded here so it is not re-invented.
#
# THE THIRD OUTCOME IS THE ONE THAT MATTERS. "Fires on the corrected copy" is not
# merely a veto of one finding — it is diagnostic output about the INSTRUMENT, in
# the founder's framing, verbatim: "Machinery that highlights an established
# truth as a fault, is something that may indeed warrant our attention." It is
# recorded as a MECHANICAL FAULT and surfaced as such. "Errors on the corrected
# copy" is a different thing entirely and renders differently: an error is not
# evidence, so nothing is concluded and nothing is vetoed. "Fires on both" and
# "crashed" must never render identically — that distinction is this project's
# single most repeated lesson.
#
# WHY THE APPARATUS PROVES ITSELF BEFORE IT REPORTS. Every step below can fail in
# the house style — rendering a failure as a confident success. A falsifier that
# never reads the target through the overlay would run against the ORIGINAL file
# on both passes, fire twice, and mint a FALSE mechanical fault against a sound
# instrument. So the control does not trust the overlay; it MEASURES that the
# overlay is load-bearing (the tripwire probe) and that the falsifier is
# deterministic (the repeat probe) and that the falsifier still reproduces its
# CONFIRMED verdict under the control's own apparatus (the baseline check).
# Any of those failing yields a distinct INDETERMINATE_* outcome and NO verdict.
#
# COST AND GATING. The control is PRESENCE-GATED: it runs if and only if the
# entry carries a corrected copy. There is no config flag, deliberately — a new
# key in RunnerConfig.from_dict is the exact shape of a defect this project has
# now shipped three times (routing 2026-07-12, max_contested 2026-07-27, the
# factorial's primary factor 2026-07-29), where the runner honours a key the
# launcher silently drops. Nothing supplies a corrected copy today, so this is a
# strict no-op on every existing config and every archived run.

DISC_TRIPWIRE_TOKEN = "CDSFL_DISCRIMINATION_TRIPWIRE"
DISC_TRIPWIRE_BODY = (
    "# " + DISC_TRIPWIRE_TOKEN + "\n"
    'raise ImportError("' + DISC_TRIPWIRE_TOKEN + ': overlay reached")\n'
)

# Outcomes. These strings are deliberately NOT collapsible into a boolean: the
# whole point is that "fired on both" and "crashed" are different findings about
# different things, and a reader that folds them together has thrown away the
# distinction the control exists to draw.
DISC_PASSED = "DISCRIMINATES"                  # quiet on the corrected copy
DISC_FAILED = "NO_DISCRIMINATION"              # fired on the corrected copy
DISC_ERROR = "INDETERMINATE_ERROR"             # crashed on the corrected copy
DISC_NOT_INTERCEPTED = "INDETERMINATE_NOT_INTERCEPTED"   # never read the target
DISC_NONDETERMINISTIC = "INDETERMINATE_NONDETERMINISTIC"  # unstable output
DISC_BASELINE = "INDETERMINATE_BASELINE"       # apparatus not faithful
DISC_COPY_UNCHANGED = "INDETERMINATE_COPY_UNCHANGED"  # nothing was corrected
DISC_ABSENT = "NO_CONTROL"                     # no corrected copy was supplied

DISC_INDETERMINATE = frozenset({
    DISC_ERROR, DISC_NOT_INTERCEPTED, DISC_NONDETERMINISTIC, DISC_BASELINE,
    DISC_COPY_UNCHANGED,
})


def _disc_sha(text: str) -> str:
    import hashlib as _hashlib
    return _hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()[:16]


def _discrimination_mirror_except(real_dir: Path, over_dir: Path, skip: str) -> None:
    """Mirror one directory as symlinks, omitting `skip`.

    Symlinks, not copies: the repo is large and the control runs per finding.
    The links are absolute, so they resolve identically from the sandbox's
    throwaway cwd. `shutil.rmtree` does not follow symlinks when deleting, so
    tearing an overlay down cannot reach the real tree.
    """
    over_dir.mkdir(parents=True, exist_ok=True)
    for child in real_dir.iterdir():
        if child.name == skip:
            continue
        link = over_dir / child.name
        if link.exists() or link.is_symlink():  # pragma: no cover — defensive
            continue
        os.symlink(child, link)


def _build_discrimination_overlay(repo_root: Path, target_rel: str,
                                  content: str) -> Path:
    """A throwaway repo root identical to `repo_root` except for ONE file.

    Returns the overlay root; the caller owns it and must rmtree it. Raises
    rather than degrading: an overlay that silently failed to replace the target
    would make every downstream verdict wrong in the confident direction.
    """
    rel = (target_rel or "").strip()
    if not rel:
        raise ValueError("discrimination control: no target path")
    if os.path.isabs(rel):
        raise ValueError(f"discrimination control: target must be repo-relative, got {rel!r}")
    parts = Path(rel).parts
    if not parts or ".." in parts:
        raise ValueError(f"discrimination control: unusable target path {rel!r}")
    real_target = repo_root / rel
    if not real_target.is_file():
        raise FileNotFoundError(f"discrimination control: target not found: {real_target}")
    root = Path(tempfile.mkdtemp(prefix="cdsfl_disc_"))
    real_dir, over_dir = repo_root, root
    for comp in parts[:-1]:
        _discrimination_mirror_except(real_dir, over_dir, comp)
        real_dir = real_dir / comp
        over_dir = over_dir / comp
    _discrimination_mirror_except(real_dir, over_dir, parts[-1])
    leaf = over_dir / parts[-1]
    leaf.write_text(content, encoding="utf-8")
    if leaf.is_symlink() or leaf.read_text(encoding="utf-8") != content:  # pragma: no cover
        raise RuntimeError("discrimination control: overlay leaf did not take")
    return root


def _retarget_falsifier(code: str, repo_root: Path, overlay_root: Path) -> Tuple[str, int]:
    """Point a falsifier's absolute repo references at the overlay.

    A prose falsifier reaches its target by absolute path
    (``open('/…/Constraint_Engineering/bench/…/SW-21-REF-04.md')``), which
    PYTHONPATH cannot redirect. Substituting the repo root is a literal
    string swap between two absolute directory paths — it cannot change the
    falsifier's syntax or logic. It is never trusted on its own: whether the
    substitution was load-bearing is MEASURED by the tripwire probe, so a swap
    that missed produces INDETERMINATE_NOT_INTERCEPTED, not a verdict.
    """
    real = str(repo_root)
    n = (code or "").count(real)
    if not n:
        return code or "", 0
    return (code or "").replace(real, str(overlay_root)), n


def _normalise_probe_output(text: str, roots) -> str:
    """Strip run-to-run noise so two probe outputs are comparable.

    Overlay roots and sandbox temp paths differ by construction on every run;
    leaving them in would make every comparison report "different" and every
    falsifier look intercepted.
    """
    out = text or ""
    for r in roots:
        out = out.replace(str(r), "<ROOT>")
    out = re.sub(r"/[^\s'\"]*cdsfl_(?:falsifier|reverify|disc)[^\s'\"]*", "<TMP>", out)
    out = re.sub(r"0x[0-9a-fA-F]+", "<ADDR>", out)
    return re.sub(r"\s+", " ", out).strip()


# ─────────────────────────────────────────────────────────────────────────────
# CORRECTED-COPY INGEST — the supply side of the control (wired 2026-08-12)
# ─────────────────────────────────────────────────────────────────────────────
#
# UNTIL NOW `entry["corrected_copy"]` HAD NO WRITER ANYWHERE OUTSIDE TESTS. The
# control above is presence-gated on that field, so it was inert in production
# and had never fired on a real run. The apparatus was built and never connected.
#
# THE CONVENTION IS THE FALSIFIER'S CONVENTION. A model already answers a
# labelled `FALSIFIER: <id>` + payload form in the round directive, the routing
# prompt and the sweep prompt. The corrected copy uses the same shape —
# `CORRECTED_COPY: <id>` + payload — so a model faces ONE convention, not two.
# The payload is sentinel-delimited rather than fence-delimited for the reason
# recorded in `_sweep_prompt`: a markdown target carries its own ``` fences, so
# a fence cannot delimit a passage taken out of one.
#
# WHAT IS ASKED FOR, AND WHAT IS NEVER READ. The model supplies the PASSAGE as
# it stands and the SAME PASSAGE with the claim corrected. The runner locates
# the first inside the target and substitutes the second. The model's
# `proposed_fix` / FIX SEARCH-REPLACE block is NEVER a source here, and nothing
# below reads it: two reviews killed that route on 2026-08-04 because a fix with
# a bad indent or a missing import makes the falsifier CRASH, and a crash that
# read as "still fires" would silently un-confirm a genuine defect.
#
# WHY AN ANCHORED PASSAGE RATHER THAN A PASTED WHOLE DOCUMENT. The field is
# consumed as the ENTIRE content of the target (`_build_discrimination_overlay`
# writes it as the file). A pasted whole document is therefore one truncation
# away from a corrected copy that is missing most of the target — and a
# falsifier reading a mostly-absent document goes quiet, which renders as
# DISCRIMINATES. That is this project's house failure mode exactly: a failure
# arriving as a confident success. A splice CANNOT truncate: everything outside
# the anchor is the target's own bytes, unread and unretyped. The whole-document
# form is not lost, it is subsumed — a model may anchor on the whole document,
# which occurs exactly once in itself.
#
# EVERY REFUSAL IS LOUD. A copy that cannot be located, that is ambiguous, that
# changes nothing, or that does not parse, is REFUSED with a named reason: it is
# logged, stamped on the finding, and rendered back to the panel so the next
# attempt can be correct. It is never silently dropped and never half-stored.

_CORRECTED_ORIGINAL_SENTINEL = "<<<CDSFL_ORIGINAL>>>"
_CORRECTED_CORRECTED_SENTINEL = "<<<CDSFL_CORRECTED>>>"
_CORRECTED_END_SENTINEL = "<<<CDSFL_END>>>"

# Shortest anchor accepted. A two-character anchor that happens to occur once
# today is an accident waiting for the next round's rewrite; requiring a real
# passage makes the "occurs exactly once" check mean what it says.
_CORRECTED_ANCHOR_MIN = 12

_CORRECTED_COPY_RE = re.compile(
    r"CORRECTED_COPY\s*:\s*[`*\"' ]*(?P<key>[A-Za-z0-9_.\-]{1,40})[`*\"' ]*[^\S\n]*\n"
    r"[^\S\n]*" + re.escape(_CORRECTED_ORIGINAL_SENTINEL) + r"[^\S\n]*\n"
    r"(?P<original>.*?)\n"
    r"[^\S\n]*" + re.escape(_CORRECTED_CORRECTED_SENTINEL) + r"[^\S\n]*\n"
    r"(?P<corrected>.*?)\n"
    r"[^\S\n]*" + re.escape(_CORRECTED_END_SENTINEL),
    re.S,
)


def _corrected_copy_instructions(indent: str = "") -> str:
    """The literal response form, rendered identically in every prompt.

    One string, three call sites (round directive, routing, sweep), so the
    convention cannot drift apart between them — which is how the sweep prompt
    and the routing prompt came to disagree about prose targets on 2026-08-01.
    """
    i = indent
    return (
        f"{i}CORRECTED_COPY: <the same id>\n"
        f"{i}{_CORRECTED_ORIGINAL_SENTINEL}\n"
        f"{i}<the passage EXACTLY as it stands in the target now, copied "
        f"character for character, long enough to occur only once>\n"
        f"{i}{_CORRECTED_CORRECTED_SENTINEL}\n"
        f"{i}<the same passage with THIS claim, and only this claim, corrected>\n"
        f"{i}{_CORRECTED_END_SENTINEL}"
    )


_CORRECTED_COPY_WHY = (
    "A falsifier that fires has proved that it fired -- not that it fired "
    "BECAUSE OF YOUR CLAIM. So with every falsifier, supply the corrected "
    "passage: the runner splices it into its own copy of the target and re-runs "
    "YOUR falsifier against it, and a sound falsifier goes QUIET. Send the "
    "corrected TEXT ITSELF, not a patch, not a diff, and not your FIX block. Do "
    "not indent or re-wrap the original passage -- it is located by exact match, "
    "and if it cannot be found, or occurs more than once, the corrected copy is "
    "refused and you are told so."
)


def _extract_corrected_copies(text: str) -> Dict[str, Tuple[str, str]]:
    """Pull every labelled corrected passage out of one model reply.

    Returns ``{key: (original, corrected)}`` with the key AS THE MODEL WROTE IT
    — a canonical id (``C0007``) or its own finding id (``F002``). Case is
    preserved because the alias map is case-sensitive; duplicates are collapsed
    case-insensitively so ``c0007`` and ``C0007`` cannot both be offered.
    Resolving a key to a canonical id is the caller's job, because only the
    caller knows which model is speaking. First label wins, mirroring
    ``extract_falsifiers``. Pure text: nothing is executed and nothing is stored.
    """
    out: Dict[str, Tuple[str, str]] = {}
    if not text or "CORRECTED_COPY" not in text:
        return out
    seen = set()
    for m in _CORRECTED_COPY_RE.finditer(text):
        key = (m.group("key") or "").strip()
        if key and key.lower() not in seen:
            seen.add(key.lower())
            out[key] = (m.group("original"), m.group("corrected"))
    return out


def _resolve_finding_key(registry, model_id: str, key: str) -> str:
    """Map whatever id a model wrote onto a canonical id, or return "".

    Models label with the canonical id the registry summary shows them
    (``C0007``), with their own stable finding id (``F002``), or with the
    prefixed form the parser records (``codex_F002``). All three resolve here;
    an id that resolves to nothing is reported, never guessed at.
    """
    k = (key or "").strip()
    if not k:
        return ""
    if k.upper() in registry.entries:
        return k.upper()
    for cand in (k, k.upper(), k.lower(),
                 f"{model_id}_{k}", f"{model_id.lower()}_{k}"):
        cid = registry.lookup_alias(model_id, cand)
        if cid:
            return cid
    return ""


def _splice_corrected_copy(
    target_text: str, original: str, corrected: str, target_rel: str = "",
) -> Tuple[str, str]:
    """Build the full corrected copy, or refuse and say why.

    Returns ``(copy, reason)``. ``copy`` is ``""`` if and only if the passage was
    REFUSED, and ``reason`` is then a sentence naming the refusal. On acceptance
    ``reason`` describes what was spliced. There is no third state and no silent
    partial acceptance: the caller stores the field only on a non-empty copy.
    """
    if not (target_text or "").strip():
        return "", ("the target could not be read, so the passage could not be "
                    "located in it")
    if len((original or "").strip()) < _CORRECTED_ANCHOR_MIN:
        return "", (f"the original passage is shorter than "
                    f"{_CORRECTED_ANCHOR_MIN} characters, which is too short to "
                    f"locate reliably; quote a whole line or more")
    if original == corrected:
        return "", ("the original and corrected passages are identical, so "
                    "nothing was corrected and the control would decide nothing")
    n = target_text.count(original)
    if n == 0:
        return "", ("the original passage does not occur in the target "
                    "verbatim, so it could not be located; copy it character "
                    "for character, without re-indenting or re-wrapping it")
    if n > 1:
        return "", (f"the original passage occurs {n} times in the target, so "
                    f"the runner cannot tell which one this claim is about; "
                    f"quote more surrounding text so it is unique")
    copy = target_text.replace(original, corrected, 1)
    if copy == target_text:  # pragma: no cover — excluded by original != corrected
        return "", ("splicing the corrected passage changed nothing in the "
                    "target")
    if str(target_rel or "").lower().endswith(".py"):
        # THE FAILURE MODE THIS CLOSES is the one that killed the synthesise-
        # from-the-fix route: a bad indent makes the falsifier crash rather than
        # go quiet. A copy that does not parse is refused HERE, before it can be
        # measured, instead of being read as evidence about the falsifier.
        import ast as _ast
        try:
            _ast.parse(copy)
        except SyntaxError as exc:
            return "", (f"the corrected copy does not parse as Python "
                        f"({type(exc).__name__}: {exc}); a copy that cannot be "
                        f"imported tells the control nothing about the falsifier")
    return copy, (f"corrected passage of {len(original)} chars spliced into "
                  f"{target_rel or 'the target'} ({len(copy)} chars)")


def _accept_corrected_copy(
    entry: dict, original: str, corrected: str, target_text: str,
    *, target_rel: str = "", by: str = "", cid: str = "",
) -> bool:
    """Verify one offered passage and store it, or refuse it loudly.

    The ONLY writer of ``entry["corrected_copy"]`` in production. Returns True
    if the field was written. A refusal writes ``corrected_copy_rejected`` and
    logs; it never writes a partial copy, and it never clears a copy that an
    earlier round accepted.
    """
    copy, reason = _splice_corrected_copy(
        target_text, original, corrected, target_rel)
    if not copy:
        entry["corrected_copy_rejected"] = reason
        _log(f"  corrected copy REFUSED {cid or '?'}"
             f"{f' from {by}' if by else ''}: {reason}")
        return False
    entry["corrected_copy"] = copy
    entry["corrected_copy_anchor"] = {"original": original, "corrected": corrected}
    entry["corrected_copy_source"] = by
    entry["corrected_copy_target_sha"] = _disc_sha(target_text)
    entry.pop("corrected_copy_rejected", None)
    return True


def _refresh_stale_corrected_copies(
    registry, target_text: str, *, target_rel: str = "",
) -> Dict[str, int]:
    """Re-splice, or drop, a corrected copy taken against an older target.

    `apply_fixes_back_enabled` rewrites the reviewed target between rounds. A
    corrected copy spliced from the PREVIOUS revision is then a document that no
    longer exists, and running the control against it would measure the rewrite
    rather than the claim — while reporting a verdict about the claim. So a copy
    whose recorded target hash no longer matches is re-spliced from its stored
    anchor, and DROPPED with a log line if the anchor no longer locates.
    """
    stats = {"resplit": 0, "dropped": 0}
    if not (target_text or "").strip():
        # A transient read failure is not evidence that a stored copy is stale.
        # Dropping every copy on an unreadable target would be a failure
        # rendering as housekeeping.
        return stats
    sha = _disc_sha(target_text)
    for cid, e in registry.entries.items():
        if not (e.get("corrected_copy") or "").strip():
            continue
        if e.get("corrected_copy_target_sha") == sha:
            continue
        anchor = e.get("corrected_copy_anchor") or {}
        copy, reason = _splice_corrected_copy(
            target_text, anchor.get("original", ""), anchor.get("corrected", ""),
            target_rel)
        if copy:
            e["corrected_copy"] = copy
            e["corrected_copy_target_sha"] = sha
            stats["resplit"] += 1
            continue
        e.pop("corrected_copy", None)
        e.pop("corrected_copy_target_sha", None)
        e["corrected_copy_rejected"] = (
            f"the target changed after this corrected copy was supplied and it "
            f"no longer applies: {reason}")
        stats["dropped"] += 1
        _log(f"  corrected copy DROPPED {cid}: the target was rewritten and the "
             f"stored passage no longer applies — {reason}")
    return stats


def _corrected_copy_owner(entry: dict) -> str:
    """The model whose INSTRUMENT is under control for this finding.

    ADVERSARIAL-PASS REPAIR (2026-08-12). The round ingest originally accepted a
    corrected copy from ANY model for ANY finding, keyed only on the canonical
    id, with the last writer in dispatch-completion order silently overwriting an
    already-verified copy. That is a live cross-model veto, reproduced end to end:
    with SIM-A's honest passage the control returned DISCRIMINATES and the
    finding stayed CONFIRMED; with SIM-B's cosmetic passage landing second in the
    same round it returned NO_DISCRIMINATION and the finding was un-confirmed to
    OPEN, `verified` False, `mechanical_fault` True — a model rejecting another
    model's critical, which this project's rules forbid, and the log blamed the
    instrument. `run_discrimination_control` names the mechanism in its own step
    0: a copy that "corrects a DIFFERENT claim in the same file" is undetectable
    from there and mints mechanical faults wholesale.

    It was also NONDETERMINISTIC: `responses` is filled by `as_completed`, so
    which model won the overwrite varied run to run.

    The rule is the routing ladder's own rule, applied to the round path: the
    copy and the falsifier it controls must describe the same instrument. The
    owner is whoever wrote the falsifier now attached — the routing rung that
    replaced it, else the model that reported the finding. An entry with no
    recorded owner is not guessed at: anyone may supply, as before.
    """
    return str(entry.get("resolved_by_routing") or entry.get("source_model") or "")


def _ingest_corrected_copies(
    registry, responses: dict, round_idx: int, cfg=None,
    repo_root: Optional[str] = None,
) -> Dict[str, int]:
    """Attach this round's corrected passages to their findings.

    Called once per round, immediately before the falsifier gate, so a copy
    offered in round K is available to the control in round K. Silent on a round
    where no model offered one — which is every archived round, so this is a
    strict no-op on the entire archive.
    """
    target_rel = (getattr(cfg, "test_article", "") or "") if cfg else ""
    try:
        target_text = (Path(repo_root or REPO_ROOT) / target_rel).read_text(
            encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        target_text = ""
    stats = {"offered": 0, "accepted": 0, "refused": 0, "unmatched": 0}
    for model_id, raw in (responses or {}).items():
        offered = _extract_corrected_copies(raw or "")
        for key, (original, corrected) in offered.items():
            stats["offered"] += 1
            cid = _resolve_finding_key(registry, model_id, key)
            entry = registry.entries.get(cid) if cid else None
            if entry is None:
                stats["unmatched"] += 1
                _log(f"  corrected copy UNMATCHED from {model_id}: no finding "
                     f"answers to id {key!r}; label it with the canonical id "
                     f"shown in the registry summary")
                continue
            owner = _corrected_copy_owner(entry)
            if owner and str(model_id) != owner:
                # Counted as a refusal rather than a new key so the census keeps
                # one shape; the log line is distinct so it cannot be confused
                # with a passage that failed to locate.
                stats["refused"] += 1
                if not (entry.get("corrected_copy") or "").strip():
                    entry["corrected_copy_rejected"] = (
                        f"a corrected copy for this finding was offered by "
                        f"{model_id}, but the falsifier under control was written "
                        f"by {owner}, and only {owner} may supply the passage that "
                        f"decides whether it discriminates. {owner}: send it in "
                        f"the CORRECTED_COPY form.")
                _log(f"  corrected copy REFUSED {cid} from {model_id}: not the "
                     f"owner of the falsifier under control ({owner}); a copy "
                     f"that corrects a different claim mints a mechanical fault "
                     f"against a sound instrument")
                continue
            if _accept_corrected_copy(
                    entry, original, corrected, target_text,
                    target_rel=target_rel, by=model_id, cid=cid):
                stats["accepted"] += 1
            else:
                stats["refused"] += 1
    stats.update(_refresh_stale_corrected_copies(
        registry, target_text, target_rel=target_rel))
    if stats["offered"] or stats.get("dropped"):
        _log(f"  corrected copies: {stats['accepted']} accepted, "
             f"{stats['refused']} refused, {stats['unmatched']} unmatched, "
             f"{stats.get('resplit', 0)} re-spliced after a target rewrite, "
             f"{stats.get('dropped', 0)} dropped")
    return stats


def run_discrimination_control(
    entry: dict, *, repo_root: Optional[str] = None,
    target_rel: str = "", timeout: Optional[int] = None,
) -> dict:
    """Re-run a CONFIRMED falsifier against a corrected copy of its target.

    Pure with respect to the registry — it mutates nothing and decides nothing.
    It returns a record; the caller applies it. Returned keys:

      outcome              one of the DISC_* constants above
      detail               one sentence a human can act on
      baseline_verdict     the falsifier's verdict under the control's own
                           apparatus with the target UNCHANGED (must be
                           CONFIRMED, else the apparatus is not faithful here)
      corrected_verdict    the falsifier's verdict against the corrected copy
      intercepted          True/False/None — did the falsifier actually read the
                           target through the overlay
      deterministic        True/False/None — did two identical runs agree
      retarget_substitutions  how many absolute repo references were redirected
      falsifier_sha / corrected_sha  identity of what was tested, so the caller
                           can skip a repeat and a human can tell two runs apart
    """
    from bench.falsifier_verify import execute_python, reverify_falsifier

    fcode = (entry.get("falsifier_code") or "").strip()
    corrected = entry.get("corrected_copy") or ""
    rec = {
        "outcome": DISC_ABSENT,
        "detail": "",
        "target": target_rel,
        "falsifier_sha": _disc_sha(fcode),
        "corrected_sha": _disc_sha(corrected),
        "baseline_verdict": "",
        "corrected_verdict": "",
        "intercepted": None,
        "deterministic": None,
        "retarget_substitutions": 0,
    }
    if not fcode:
        rec["detail"] = "no falsifier to control"
        return rec
    if not corrected.strip():
        rec["detail"] = (
            "no corrected copy was supplied with this falsifier, so the control "
            "did not run and the CONFIRMED verdict is unchecked for discrimination")
        return rec

    root = Path(repo_root or REPO_ROOT)
    kwargs = {} if timeout is None else {"timeout": timeout}
    overlays = []
    try:
        try:
            real_text = (root / target_rel).read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError) as exc:
            rec["outcome"] = DISC_ERROR
            rec["detail"] = (f"the target could not be read, so no control was "
                             f"possible: {type(exc).__name__}: {exc}")
            return rec

        # 0. IS ANYTHING ACTUALLY CORRECTED? MEASURED 2026-08-08 on the archive:
        #    with the "corrected" copy set to the target's own unchanged text,
        #    12 of 12 archived CONFIRMED falsifiers were stamped
        #    NO_DISCRIMINATION — every one of them a sound instrument. A panel
        #    that echoes the target back, or corrects a DIFFERENT claim in the
        #    same file, would therefore mint mechanical faults wholesale. Byte
        #    equality is the one case that is decidable here and it is the most
        #    likely lazy failure, so it is refused rather than scored. (A copy
        #    that differs but fixes the wrong claim is NOT detectable from here
        #    and remains a real limitation — see the note in the module docs.)
        if corrected == real_text:
            rec["outcome"] = DISC_COPY_UNCHANGED
            rec["detail"] = (
                "the supplied corrected copy is byte-identical to the target, so "
                "nothing was corrected and a falsifier that fires on it has "
                "demonstrated nothing. Nothing is concluded. Supply a copy in "
                "which THIS claim is fixed.")
            return rec

        # 1. BASELINE. The same falsifier, the same content, run through the
        #    control's own apparatus. If it does not reproduce the CONFIRMED
        #    verdict here, the apparatus is not faithful for this falsifier and
        #    every later comparison would be measuring the apparatus.
        try:
            real_overlay = _build_discrimination_overlay(root, target_rel, real_text)
        except (OSError, ValueError, RuntimeError) as exc:
            rec["outcome"] = DISC_ERROR
            rec["detail"] = (f"the control apparatus could not be built: "
                             f"{type(exc).__name__}: {exc}")
            return rec
        overlays.append(real_overlay)
        real_code, nsub = _retarget_falsifier(fcode, root, real_overlay)
        rec["retarget_substitutions"] = nsub
        rec["baseline_verdict"] = reverify_falsifier(
            real_code, repo_root=str(real_overlay), **kwargs)
        if rec["baseline_verdict"] != "CONFIRMED":
            rec["outcome"] = DISC_BASELINE
            rec["detail"] = (
                f"the falsifier does not reproduce its CONFIRMED verdict against "
                f"an UNCHANGED copy of the target under the control's apparatus "
                f"(got {rec['baseline_verdict']}). The apparatus is not faithful "
                f"for this falsifier, so nothing is concluded about it.")
            return rec

        # 2. DETERMINISM. A comparison-based control is meaningless on a
        #    falsifier whose output varies between identical runs.
        probe_a = execute_python(real_code, repo_root=str(real_overlay), **kwargs)
        probe_a2 = execute_python(real_code, repo_root=str(real_overlay), **kwargs)
        norm_a = _normalise_probe_output(probe_a, (real_overlay, root))
        rec["deterministic"] = (
            norm_a == _normalise_probe_output(probe_a2, (real_overlay, root)))
        if not rec["deterministic"]:
            rec["outcome"] = DISC_NONDETERMINISTIC
            rec["detail"] = (
                "two identical runs of this falsifier produced different output, "
                "so comparing its behaviour on two copies of the target decides "
                "nothing. Nothing is concluded.")
            return rec

        # 3. INTERCEPTION. Replace the target with a file that cannot be read or
        #    imported normally. If the falsifier's behaviour is UNCHANGED, it
        #    never read the target through the overlay — so the corrected-copy
        #    run would have exercised the ORIGINAL file, and "fires on both"
        #    would be a false mechanical fault against a sound instrument.
        try:
            trip_overlay = _build_discrimination_overlay(
                root, target_rel, DISC_TRIPWIRE_BODY)
        except (OSError, ValueError, RuntimeError) as exc:  # pragma: no cover
            rec["outcome"] = DISC_ERROR
            rec["detail"] = (f"the interception probe could not be built: "
                             f"{type(exc).__name__}: {exc}")
            return rec
        overlays.append(trip_overlay)
        trip_code, _ = _retarget_falsifier(fcode, root, trip_overlay)
        probe_b = execute_python(trip_code, repo_root=str(trip_overlay), **kwargs)
        norm_b = _normalise_probe_output(probe_b, (trip_overlay, root))
        rec["intercepted"] = (norm_b != norm_a)
        if not rec["intercepted"]:
            rec["outcome"] = DISC_NOT_INTERCEPTED
            rec["detail"] = (
                "this falsifier behaves identically when the target file is "
                "replaced wholesale, so the control cannot reach the target it "
                "reads and cannot test whether it discriminates. Nothing is "
                "concluded — this is NOT a finding against the falsifier.")
            return rec

        # 4. THE CONTROL ITSELF.
        try:
            corr_overlay = _build_discrimination_overlay(root, target_rel, corrected)
        except (OSError, ValueError, RuntimeError) as exc:  # pragma: no cover
            rec["outcome"] = DISC_ERROR
            rec["detail"] = (f"the corrected copy could not be staged: "
                             f"{type(exc).__name__}: {exc}")
            return rec
        overlays.append(corr_overlay)
        corr_code, _ = _retarget_falsifier(fcode, root, corr_overlay)
        rec["corrected_verdict"] = reverify_falsifier(
            corr_code, repo_root=str(corr_overlay), **kwargs)

        if rec["corrected_verdict"] == "REFUTED":
            rec["outcome"] = DISC_PASSED
            rec["detail"] = (
                "the falsifier went quiet against a corrected copy of the target, "
                "so it does test the claim it is attached to.")
        elif rec["corrected_verdict"] == "CONFIRMED":
            rec["outcome"] = DISC_FAILED
            rec["detail"] = (
                "the falsifier fires just as hard against a CORRECTED copy of the "
                "target, so it is not testing this claim at all. Machinery that "
                "highlights an established truth as a fault, is something that "
                "may indeed warrant our attention.")
        else:
            rec["outcome"] = DISC_ERROR
            rec["detail"] = (
                f"the falsifier did not run to a verdict against the corrected "
                f"copy ({rec['corrected_verdict']}). An error is not evidence: "
                f"nothing is concluded and nothing is vetoed.")
        return rec
    finally:
        for ov in overlays:
            shutil.rmtree(ov, ignore_errors=True)


def _apply_discrimination_control(
    cid: str, entry: dict, registry: FindingRegistry, round_idx: int,
    *, cfg: Optional[RunnerConfig] = None, repo_root: Optional[str] = None,
    tally: Optional[dict] = None,
) -> str:
    """Run the control on a just-CONFIRMED finding and apply its record.

    SAFETY. A veto ESCALATES, never deletes. CONFIRM-only is the most
    load-bearing rule in this system and this is the first mechanism that can
    un-confirm anything, so every branch fails toward the human:

      * DISCRIMINATES     -> the CONFIRMED verdict stands, unchanged.
      * NO_DISCRIMINATION -> the finding is NOT closed. It returns to the same
                            state as any un-demonstrated critical (UNCONFIRMED +
                            escalated), which is the state the routing ladder
                            already absorbs — a stronger writer gets a chance to
                            produce a falsifier that DOES discriminate. Nothing
                            is deleted, no severity is touched, and the
                            mechanical fault is recorded as instrument
                            diagnostics in its own right.
      * INDETERMINATE_*   -> the CONFIRMED verdict stands, unchanged, and the
                            finding is flagged so a human sees that the control
                            could not speak. An error is not evidence.

    The record is preserved via `_record_computed_evidence` in ALL outcomes —
    the same channel the 2026-08-03 ruling built, extended rather than
    duplicated, so a human reading a finding sees one evidence trail.
    """
    fcode = (entry.get("falsifier_code") or "").strip()
    corrected = entry.get("corrected_copy") or ""
    if not corrected.strip():
        if tally is not None:
            tally["no_control"] = tally.get("no_control", 0) + 1
        return DISC_ABSENT

    # Idempotence: the gate re-runs every round. Re-running the control on an
    # unchanged (falsifier, corrected copy, TARGET) triple costs four sandbox
    # executions and cannot change its own answer. The target belongs in the key
    # because `apply_fixes_back_enabled` rewrites the reviewed target between
    # rounds — a cache keyed on the falsifier alone would answer a question
    # about a file that no longer exists.
    target_rel = (getattr(cfg, "test_article", "") or "") if cfg else ""
    try:
        target_sha = _disc_sha(
            (Path(repo_root or REPO_ROOT) / target_rel).read_text(
                encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        target_sha = ""
    prior = entry.get("discrimination") or {}
    fresh = not (prior.get("falsifier_sha") == _disc_sha(fcode)
                 and prior.get("corrected_sha") == _disc_sha(corrected)
                 and prior.get("target_sha") == target_sha
                 and prior.get("outcome"))

    if fresh:
        try:
            rec = run_discrimination_control(
                entry, repo_root=repo_root, target_rel=target_rel)
        except Exception as exc:  # noqa: BLE001
            # The control must not be able to kill a round — and it must not be
            # able to go quiet either. A crash here is INDETERMINATE, named and
            # logged, never a silent pass and never a veto.
            rec = {"outcome": DISC_ERROR,
                   "detail": (f"the discrimination control itself crashed: "
                              f"{type(exc).__name__}: {str(exc)[:200]}. Nothing "
                              f"is concluded and nothing is vetoed."),
                   "falsifier_sha": _disc_sha(fcode),
                   "corrected_sha": _disc_sha(corrected),
                   "baseline_verdict": "", "corrected_verdict": "",
                   "intercepted": None, "deterministic": None,
                   "retarget_substitutions": 0, "target": ""}
        rec["round"] = round_idx
        rec["target_sha"] = target_sha
        entry["discrimination"] = rec
        _record_computed_evidence(
            entry, kind=f"discrimination_control:{rec['outcome']}",
            by="discrimination_control", detail=rec["detail"], falsifier=fcode)
    else:
        rec = prior

    outcome = rec["outcome"]
    if tally is not None:
        tally[outcome] = tally.get(outcome, 0) + 1

    # The stamps below are re-applied on a cached hit as well as a fresh run.
    # The gate rewrites `falsifier_verdict` to CONFIRMED at the top of every
    # round before calling here; an early return on the cache would leave a
    # non-discriminating falsifier stamped CONFIRMED, which is the stamp routing
    # reads to decide the finding needs no further work — a quiet regression to
    # exactly the state this control exists to prevent.

    if outcome == DISC_FAILED:
        # The founder's third outcome. This is diagnostic output about the
        # INSTRUMENT, not merely a veto of one finding.
        entry["falsifier_verdict"] = "NON_DISCRIMINATING"
        entry["verified"] = False
        entry["escalated"] = True
        entry["hil_escalated"] = True
        entry["mechanical_fault"] = True
        entry["hil_reason"] = (
            "MECHANICAL FAULT: the falsifier fires against a CORRECTED copy of "
            "the target, so it does not test this claim. The finding is NOT "
            "closed and NOT dropped — it returns to the human, and the "
            "instrument itself warrants attention.")
        if entry.get("status") == "CONFIRMED":
            registry.resolve(cid, "UNCONFIRMED", round_idx)
        _log(f"  ★ MECHANICAL FAULT {cid}: falsifier fires on a CORRECTED copy "
             f"— NOT closed, escalated to human. {rec['detail'][:200]}")
    elif outcome in DISC_INDETERMINATE:
        # No veto. An error is not evidence, and "fires on both" must never
        # render the same as "crashed".
        entry["discrimination_indeterminate"] = True
        entry["hil_escalated"] = True
        entry.setdefault(
            "hil_reason",
            f"discrimination control {outcome}: {rec['detail']}")
        if fresh:
            # Only when the measurement was actually taken. A benign flag
            # reprinted every round for sixteen rounds buries the one line that
            # matters; the per-round tally still reports the standing count, and
            # the panel sees the flag in its own prompt every round regardless.
            _log(f"  discrimination control {outcome} {cid}: CONFIRMED stands, "
                 f"flagged for a human. {rec['detail'][:200]}")
    return outcome


def apply_falsifier_verdicts(
    registry: FindingRegistry, round_idx: int,
    cfg: Optional[RunnerConfig] = None, repo_root: Optional[str] = None,
):
    """GATED "tools decide, not votes" override (2026-06-03).

    When ``cfg.falsifier_gate_enabled`` a finding's truth is set by the RUNNER
    independently re-running the model-attached falsifier
    (:func:`bench.falsifier_verify.reverify_falsifier`) — NOT by the
    CONFIRM/CHALLENGE vote. Called AFTER ``_update_finding_statuses`` so the
    falsifier verdict wins:

      * falsifier CONFIRMED -> status CONFIRMED (verified=True);
      * falsifier REFUTED on a NON-critical -> status REFUTED (trusted to drop a
                               non-critical claim; no real-defect-masking risk);
      * REFUTED on a CRITICAL, ERROR, UNTOOLABLE, or a CRITICAL with NO falsifier
                               -> escalated to HIL; a vote-CONFIRMED critical is
                               demoted to UNCONFIRMED. CONFIRM-only (2026-06-07):
                               a critical is resolved ONLY by a CONFIRMED
                               demonstration. A REFUTED critical is NOT trusted to
                               drop the finding, because a logically-broken falsifier
                               clean-exits and yields a FALSE REFUTED that masks a
                               real defect (Exp 42 audit: 2/3 of REFUTED criticals
                               were false vs 7/7 CONFIRMED correct). A CONFIRMED
                               needs an active AssertionError/FALSIFIED demonstration
                               (unfakeable); REFUTED is a passive clean exit. This
                               removes the one place a real critical could be faked
                               away.

    Default-off no-op: when the flag is unset this returns immediately and
    vote-based behaviour is byte-identical. Hard-terminal findings
    (MERGED/CLOSED/DUPLICATE) are left untouched.
    """
    if not (cfg and getattr(cfg, "falsifier_gate_enabled", False)):
        return
    from bench.falsifier_verify import reverify_falsifier
    _HARD_TERMINAL = {"MERGED", "CLOSED", "DUPLICATE"}
    tally = {"CONFIRMED": 0, "REFUTED": 0, "HIL": 0}
    disc_tally: dict = {}
    for cid, e in list(registry.entries.items()):
        if e.get("status") in _HARD_TERMINAL:
            continue
        fcode = (e.get("falsifier_code") or "").strip()
        is_critical = (e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD
        if not fcode:
            # No falsifier -> cannot be tool-decided. A critical claim goes to
            # HIL and is never left standing as a vote-CONFIRMED genuine critical.
            if is_critical:
                e["falsifier_verdict"] = "UNTOOLABLE"
                e["escalated"] = True
                if e.get("status") == "CONFIRMED":
                    registry.resolve(cid, "UNCONFIRMED", round_idx)
                tally["HIL"] += 1
            continue
        verdict = reverify_falsifier(fcode, repo_root=repo_root)
        e["falsifier_verdict"] = verdict
        if verdict == "CONFIRMED":
            # DISCRIMINATION CONTROL (founder ruling 2026-08-08). "It fired" is
            # not "it fired because of the claim". Before a CONFIRMED closes a
            # finding, the same falsifier is re-run against a corrected copy of
            # the target and must go quiet. Presence-gated: a no-op unless the
            # panel supplied a corrected copy with the falsifier.
            disc = _apply_discrimination_control(
                cid, e, registry, round_idx, cfg=cfg, repo_root=repo_root,
                tally=disc_tally)
            if disc == DISC_FAILED and getattr(cfg, "discrimination_control_blocks", False):
                # Not closed, not dropped, already escalated by the helper.
                tally["HIL"] += 1
                continue
            if disc == DISC_FAILED:
                # RECORD ONLY (default). The outcome is already in the tally and
                # the computed-evidence channel; the verdict is left alone.
                #
                # Blocking here changes CONFIRM-only, which is the founder's open
                # decision and not one to make by wiring. The 2026-08-12 panel
                # refuted the blocking design as proposed: the test is satisfied
                # by ACCESS rather than DEPENDENCE, so `open(TARGET).read()` with
                # the contents discarded defeats it — and it fails GREEN, showing
                # full coverage while discriminating nothing. Recording it costs
                # nothing and is what makes the decision evidence-based.
                _log(f"    disc: {cid} did not discriminate (recorded, not blocking)")
            registry.resolve(cid, "CONFIRMED", round_idx)
            e["verified"] = True
            tally["CONFIRMED"] += 1
        elif verdict == "REFUTED" and not is_critical:
            # A non-critical refutation is trusted to drop the finding — there is
            # no real-defect-masking risk for a non-critical claim.
            registry.resolve(cid, "REFUTED", round_idx)
            tally["REFUTED"] += 1
        else:
            # CONFIRM-only for criticals (2026-06-07). A critical is resolved ONLY
            # by a CONFIRMED demonstration. A REFUTED critical is NOT trusted to
            # drop the finding: a logically-broken falsifier clean-exits, producing
            # a FALSE REFUTED that silently masks a real defect (Exp 42 audit:
            # C0028/C0040 were real defects, falsely REFUTED — 2/3 of the REFUTED
            # criticals were wrong, vs 7/7 of the CONFIRMED being correct).
            # CONFIRMED requires the active AssertionError/FALSIFIED demonstration,
            # which is essentially unfakeable; REFUTED is a passive clean exit. So
            # an un-demonstrated critical (REFUTED, ERROR, or UNTOOLABLE) is
            # escalated, never dropped — eliminating the one place faking can occur.
            e["escalated"] = True
            if e.get("status") == "CONFIRMED":
                registry.resolve(cid, "UNCONFIRMED", round_idx)
            tally["HIL"] += 1
    if any(tally.values()):
        _log(f"  falsifier gate (tools decide): {tally['CONFIRMED']} CONFIRMED, "
             f"{tally['REFUTED']} REFUTED, {tally['HIL']} -> HIL")
    if disc_tally:
        # Printed whenever the gate confirmed anything, INCLUDING the all-
        # NO_CONTROL case. "0 corrected copies supplied" is the reading that
        # tells a human the control is silent rather than passing, and a silent
        # control that looks like a passing one is this project's house defect.
        _log("  discrimination control: " + ", ".join(
            f"{k}={v}" for k, v in sorted(disc_tally.items())))


# ── Routing: capability-aware falsifier routing (2026-06-07, gated; renamed from
# take_up_slack 2026-07-12) ──
# When the falsifier gate escalates an un-confirmed CRITICAL to HIL (a weak model
# wrote a broken/missing falsifier), route falsification to a STRONGER writer with
# the execute_python tool loop before accepting the HIL. Validated out-of-band on
# the 7 hardest Exp-42 residuals (weak source 0/7; strong+tool-loop 6/7; 2-rung
# ladder 7/7). Default-off => byte-identical when disabled.
# THE DEFECT (found 2026-08-01 by an 11-agent offline falsification, ~2 months
# after this ladder shipped; it was on no queue)
# -----------------------------------------------------------------------------
# This ladder is the ONLY absorber between the falsifier gate and the HIL queue.
# Its prompt was code-only: the system message told the model to
# `from bench.cdsfl_registry import <mod>`, and the finding dict passed to it
# carried id / description / source_model / severity AND NOTHING ELSE — no target
# path, no target text. So a model asked to demonstrate a defect in "Listing A"
# of a markdown document was told to import a module that does not exist, and was
# never told where the document was. Both rungs failed and _apply_routing stamped
# `hil_reason = "routing ladder exhausted (no model produced a runnable test)"`.
# That reason string is FALSE: no model was ever given the target.
#
# MEASURED, from the archives:
#   Exp 48 (chem) + Exp 49 (eng), prose with NO fenced listings, 0 listing-
#     referencing findings:            routing resolved 16/37 and 25/38 = 41 for 41
#   Exp 53 control, prose WITH 7 fenced listings, 23 and 14 listing-referencing
#     findings:                        routing resolved 0 for 25, 25 locked
#                                      irreducible, run halted R3 of 16
# A 14-line falsifier that merely opens SW-21-REF-04.md BY PATH, extracts the
# TokenBucket listing and calls allow(-10) returns CONFIRMED from the runner's own
# reverify_falsifier — for a finding this ladder had locked as impossible.
#
# The asymmetry that made it unambiguous: _sweep_prompt was made prose-aware on
# 2026-08-01 (A4). This prompt was not. Same run, same target, two prompts, one
# told the truth about the document and the other did not.
#
# Both prompts now branch on the SAME resolved target_kind, and the prose branch
# reuses _sweep_prompt's non-collidable sentinel — a markdown target carries its
# own ``` fences, so a fence cannot delimit it.
def _routing_sentinels(src: str) -> tuple:
    """Sentinel pair that provably does not occur in `src`. Mirrors _sweep_prompt."""
    import hashlib as _hashlib
    nonce = _hashlib.sha256((src or "").encode("utf-8", "replace")).hexdigest()[:12]
    begin, end = f"<<<CDSFL_TARGET_BEGIN {nonce}>>>", f"<<<CDSFL_TARGET_END {nonce}>>>"
    while begin in (src or "") or end in (src or ""):  # pragma: no cover
        nonce += "X"
        begin, end = f"<<<CDSFL_TARGET_BEGIN {nonce}>>>", f"<<<CDSFL_TARGET_END {nonce}>>>"
    return begin, end


_ROUTING_SYSTEM_PYTHON = (
    "You are a senior engineer resolving a code-review finding by writing a "
    "runnable falsifier. Use the execute_python tool to read the real source "
    "(import inspect; from bench.cdsfl_registry import <mod>; "
    "print(inspect.getsource(...))) and to RUN and iterate your falsifier before "
    "answering."
)

_ROUTING_SYSTEM_PROSE = (
    "You are a senior engineer resolving a review finding against a PROSE "
    "DOCUMENT — a technical reference in markdown, NOT Python source. There is "
    "no module to import. The document is given to you by path and reproduced "
    "verbatim in the prompt. Your falsifier OPENS THE DOCUMENT BY PATH and "
    "asserts on its text, or on a value you recompute from it. Where the claim "
    "concerns a fenced code listing printed inside the document, extract that "
    "listing from the document text and exercise it. Use the execute_python "
    "tool to RUN and iterate your falsifier before answering."
)


def _routing_system(target_kind: str) -> str:
    return (_ROUTING_SYSTEM_PROSE if target_kind == TARGET_KIND_PROSE
            else _ROUTING_SYSTEM_PYTHON)


# Back-compat alias: several tests and one external caller import this name.
_ROUTING_SYSTEM = _ROUTING_SYSTEM_PYTHON

_ROUTING_TARGET_LIMIT = 60000


def _routing_resolve_prompt(
    finding: dict,
    target_rel: str = "",
    target_src: str = "",
    target_kind: str = TARGET_KIND_PYTHON,
) -> str:
    """Prompt for one rung of the routing ladder.

    `target_rel` / `target_src` / `target_kind` default to the pre-2026-08-01
    behaviour so that any caller that has not been updated still produces the
    old code-only prompt rather than a broken one. The runner always passes them.
    """
    desc = (finding.get("description") or "")[:1200]
    if target_kind == TARGET_KIND_PROSE:
        src = target_src or ""
        truncated = len(src) > _ROUTING_TARGET_LIMIT
        if truncated:
            src = src[:_ROUTING_TARGET_LIMIT]
        begin, end = _routing_sentinels(src)
        header = (
            f"TARGET DOCUMENT: {target_rel}\n"
            f"It is a PROSE DOCUMENT, not Python source — there is NO module to "
            f"import. It is reproduced verbatim between the two sentinel lines "
            f"below. It contains its own ``` fenced listings; those fences belong "
            f"to the document and do NOT end it. Only the closing sentinel ends it."
        )
        if truncated:
            header += (
                f" TRUNCATED: only the first {_ROUTING_TARGET_LIMIT} characters "
                f"of {len(target_src)} are shown; open the path for the rest."
            )
        return (
            f"A review finding against the target document:\n\n{desc}\n\n"
            f"{header}\n{begin}\n{src}\n{end}\n\n"
            "Resolve it, using execute_python:\n"
            f"1. Open the document by path: "
            f"open({target_rel!r}, encoding='utf-8').read().\n"
            "2. Write a falsifier that asserts on the document's text, or on a "
            "value you recompute from it. If the claim concerns a fenced listing "
            "printed in the document, EXTRACT that listing from the text and "
            "exercise it. Raise AssertionError / print FALSIFIED if and ONLY IF "
            "the defect is genuinely present (exit clean if absent).\n"
            "3. RUN it via execute_python; iterate until it correctly tests the "
            "claim.\n"
            "Then give your FINAL falsifier as a single fenced ```python block. "
            "Do NOT put a ``` fence alone on its own line inside it — the block ends at "
            "fence matching and a nested fence truncates your falsifier.\n\n"
            + _CORRECTED_COPY_WHY
            + f" After the block, write:\n{_corrected_copy_instructions()}\n"
            f"Use the id {finding.get('id', '<id>')!s} on the CORRECTED_COPY line."
        )
    return (
        f"A code-review finding against the target module"
        f"{f' ({target_rel})' if target_rel else ''}:\n\n{desc}\n\n"
        "Resolve it, using execute_python:\n"
        "1. Read the real code via inspect (absolute import from the real package).\n"
        "2. Write a falsifier that imports the REAL module by absolute path, sets up "
        "the precondition, SNAPSHOTS any value before an in-place-mutating call, "
        "reaches the real buggy path, and raises AssertionError / prints FALSIFIED "
        "if and ONLY IF the defect is genuinely present (exit clean if absent).\n"
        "3. RUN it via execute_python; iterate until it correctly tests the claim.\n"
        "Then give your FINAL falsifier as a single fenced ```python block. "
        "Do NOT put a ``` fence alone on its own line inside it — the block ends at fence "
        "matching and a nested fence truncates your falsifier.\n\n"
        + _CORRECTED_COPY_WHY
        + f" After the block, write:\n{_corrected_copy_instructions()}\n"
        f"Use the id {finding.get('id', '<id>')!s} on the CORRECTED_COPY line."
    )


def _extract_routing_falsifier(text: str) -> str:
    """Pull the model's final runnable falsifier out of a routing reply.

    THE DEFECT (A5, prose-adaptation, 2026-08-01)
    ---------------------------------------------
    The old filter was ``"import" in block``. That is a *proxy* for "this block
    is runnable code", and the proxy holds for a code target, where a falsifier
    must import the module under review. It does NOT hold for a prose target.
    The only form a prose falsifier can take is to open the document by path and
    assert on its text::

        doc = open("/.../SW-21-REF-04.md", encoding="utf-8").read()
        assert "0.29 mm" not in doc, "the retracted clearance is still stated"

    No import appears anywhere. The block was discarded, this function returned
    "", and the routing ladder recorded a rung that had genuinely reached a
    model and produced nothing — minting a false "ladder exhausted".

    WHAT REPLACES IT
    ----------------
    The filtering is not dropped; it is turned into a real test of runnability,
    and the test is *derived from what the runner can actually do with the block
    downstream* rather than guessed. ``falsifier_verify.reverify_falsifier``
    returns CONFIRMED on exactly two signals: an ``AssertionError`` reaching
    stderr, or the literal token ``FALSIFIED`` on stdout. A block able to
    produce neither can never confirm anything. So a block is kept iff:

      1. it PARSES as Python (``ast.parse``). Prose commentary does not — a far
         stronger filter than the ``import`` substring ever was; AND
      2. it can reach a verdict: an ``assert`` or ``raise`` statement anywhere
         in the tree, or the ``FALSIFIED`` token inside a *string constant*
         (i.e. something a ``print`` can emit — not a bare word, because
         ``Result: FALSIFIED`` parses as an annotation and would otherwise
         sneak a chat line through). ``import`` is retained as a third
         accepting signal so that nothing the old rule admitted is newly
         rejected: this change is strictly widening.

    Fenced blocks of every language tag are now considered — the old code looked
    at bare ``` blocks only when there were no ```python blocks at all — and the
    LAST qualifying block still wins, matching the prompt's instruction to give
    the final falsifier last.
    """
    import ast as _ast
    import re as _re
    blocks = _re.findall(r"```[^\n]*\n(.*?)```", text or "", _re.S)
    cand = []
    for raw in blocks:
        block = raw.strip()
        if not block:
            continue
        try:
            tree = _ast.parse(block)
        except Exception:  # noqa: BLE001 — SyntaxError/ValueError/etc: not code
            continue
        runnable = False
        for node in _ast.walk(tree):
            if isinstance(node, (_ast.Assert, _ast.Raise,
                                 _ast.Import, _ast.ImportFrom)):
                runnable = True
                break
            if (isinstance(node, _ast.Constant)
                    and isinstance(node.value, str)
                    and "FALSIFIED" in node.value):
                runnable = True
                break
        if runnable:
            cand.append(block)
    return cand[-1] if cand else ""


def _routing_similarity(a: dict, b: dict) -> float:
    ta = set((a.get("description", "") or "").lower().split())
    tb = set((b.get("description", "") or "").lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _apply_routing(registry, round_idx, exp_config, cfg=None, repo_root=None):
    """GATED capability-aware routing for un-confirmed criticals (was _apply_take_up_slack).

    Runs AFTER ``apply_falsifier_verdicts``. For each critical the gate escalated
    to HIL (escalated=True, not CONFIRMED), route falsification up a ladder of
    progressively stronger writers (excluding the failed source model) with the
    execute_python tool loop; the runner's ``reverify_falsifier`` decides. Dedup
    against already-CONFIRMED findings first. CONFIRMED resolves it; otherwise it
    stays HIL (genuinely-hard). Default-off no-op => byte-identical."""
    if not (cfg and getattr(cfg, "routing_enabled", False)):
        return
    from bench.routing import route
    from bench.falsifier_verify import reverify_falsifier

    models = [mc.label for mc in exp_config.models]
    cfg_by_label = {mc.label: mc for mc in exp_config.models}
    confirmed = [
        {"id": cid, "description": e.get("description", "")}
        for cid, e in registry.entries.items()
        if e.get("falsifier_verdict") == "CONFIRMED"
    ]

    _routing_attempts: list = []

    # The target, resolved ONCE per round and handed to every rung. Before
    # 2026-08-01 no rung received it at all; see the block above _routing_system.
    _target_rel = getattr(cfg, "test_article", "") or ""
    try:
        _target_src = (Path(repo_root or REPO_ROOT) / _target_rel).read_text(
            encoding="utf-8", errors="replace")
    except OSError:
        _target_src = ""
    try:
        _target_kind, _ = resolve_target_kind(
            _target_rel, _target_src or None,
            getattr(cfg, "target_kind", None),
        )
    except TargetKindMismatch:
        # A declaration/detection conflict is the launch preflight's business,
        # not this ladder's. Fall back to detection so routing still gets the
        # right prompt rather than dying inside a round.
        _target_kind, _ = detect_target_kind(_target_rel, _target_src or None)

    # Corrected passages offered by a rung, keyed by the finding the rung was
    # asked about. Held here rather than written straight onto the entry because
    # a rung that FAILS to resolve must not leave a corrected copy attached to a
    # falsifier that was never adopted — the copy and the falsifier it controls
    # have to describe the same instrument.
    _routing_corrected: Dict[str, Tuple[str, str, str]] = {}

    def resolve_fn(model_label, finding):
        mc = cfg_by_label.get(model_label)
        if mc is None:
            return ""
        try:
            resp, _ = dispatch_to_model(
                mc,
                _routing_resolve_prompt(
                    finding, _target_rel, _target_src, _target_kind),
                _routing_system(_target_kind),
                enable_tools=True,
            )
        except Exception:  # noqa: BLE001 — a failed rung just advances the ladder
            return ""
        _routing_attempts.append(model_label)  # a model was genuinely reached
        offered = _extract_corrected_copies(resp or "")
        if offered:
            _orig, _corr = next(iter(offered.values()))
            _routing_corrected[str(finding.get("id") or "")] = (
                _orig, _corr, model_label)
        return _extract_routing_falsifier(resp)

    tally = {"resolved": 0, "dup": 0, "hil": 0}
    for cid, e in list(registry.entries.items()):
        if not e.get("escalated"):
            continue
        if (e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
            # FIX 2 (Exp 43, 2026-07-22): a finding whose falsifier ERRORED is
            # un-demonstrated through no fault of the claim (broken test code,
            # C0013 class). Route it ONCE to a stronger writer regardless of
            # severity, then confirm or leave it in the residual queue — no
            # indefinite limbo. One attempt only (error_routed flag) so
            # sub-criticals cannot consume the ladder round after round.
            if e.get("falsifier_verdict") != "ERROR" or e.get("error_routed"):
                continue
            # Adversarial-pass repair (2026-07-27): consume the one attempt only
            # if a rung actually REACHED a model (transport-dead rounds — the
            # 402-cascade class — must not burn the attempt nor mint a false
            # "ladder exhausted" record). _routing_attempts is appended by
            # resolve_fn on any successful dispatch return.
            e["_error_route_pending"] = True
        if e.get("falsifier_verdict") == "CONFIRMED":
            continue
        finding = {
            "id": cid, "description": e.get("description", ""),
            "source_model": e.get("source_model"), "severity": e.get("severity"),
        }
        _n0 = len(_routing_attempts)
        result = route(
            finding, models, confirmed, resolve_fn, reverify_falsifier,
            _routing_similarity,
        )
        if e.pop("_error_route_pending", None):
            if len(_routing_attempts) > _n0:
                e["error_routed"] = True
            elif not result.resolved and result.verdict != "DUPLICATE":
                continue  # transport-dead: no model reached; retry a later round
        if result.verdict == "DUPLICATE":
            e["routing_duplicate_of"] = result.duplicate_of
            e["escalated"] = False
            registry.resolve(cid, "MERGED", round_idx, merged_into=result.duplicate_of)
            tally["dup"] += 1
        elif result.resolved:
            e["falsifier_code"] = result.falsifier_code
            e["falsifier_verdict"] = "CONFIRMED"
            e["verified"] = True
            e["escalated"] = False
            e["resolved_by_routing"] = result.model_used
            # The corrected passage from the rung that actually resolved it,
            # verified against the target and refused loudly if it does not fit.
            _rc = _routing_corrected.get(cid)
            if _rc and _rc[2] == result.model_used:
                _accept_corrected_copy(
                    e, _rc[0], _rc[1], _target_src,
                    target_rel=_target_rel, by=_rc[2], cid=cid)
            # Exp 44 post-run fix (2026-07-27): a later-round success must clear
            # the stale irreducible/HIL stamps from an earlier exhausted ladder,
            # so queue counts and reports read truth (the 6-stale-flags episode).
            e["irreducible_escalation"] = False
            e["hil_escalated"] = False
            e.pop("hil_reason", None)
            registry.resolve(cid, "CONFIRMED", round_idx)
            tally["resolved"] += 1
        else:
            # Full routing ladder exhausted (no model wrote a runnable test). LOCK this
            # critical as an irreducible HIL item: handed to the human (the final
            # falsifier), excluded from the A4 convergence blocker so the loop can close
            # around a SMALL such queue — guarded by the small-queue alarm.
            e["irreducible_escalation"] = True
            e["hil_escalated"] = True
            # The old text asserted "no model produced a runnable test". Until
            # 2026-08-01 that was false on every prose target — no model was ever
            # given the target. Say only what is observed: the ladder ran out.
            e.setdefault(
                "hil_reason",
                f"routing ladder exhausted after {len(_routing_attempts) - _n0} "
                f"rung(s) reached a model; no rung returned a falsifier the "
                f"runner could confirm (target_kind={_target_kind}) -> HIL static queue",
            )
            tally["hil"] += 1  # genuinely-hard: handed to the HIL static queue
    if any(tally.values()):
        _log(f"  routing: {tally['resolved']} resolved by strong writer, "
             f"{tally['dup']} dedup'd, {tally['hil']} -> HIL")


_SWEEP_SYSTEM = (
    "You are completing a code review that has ALREADY CONVERGED. The "
    "convergence verdict is recorded and cannot change. Your ONLY task is to "
    "clear the residual findings listed in the prompt: for each, either "
    "supply a runnable falsifier or withdraw it with a reason. Any NEW "
    "finding you write will be ignored. Use the execute_python tool to read "
    "the real module and RUN your falsifier before answering."
)


def _sweep_prompt(residuals: dict, target_rel: str, target_src: str) -> str:
    """Build the post-convergence sweep prompt.

    THE DEFECT (A4, prose-adaptation, 2026-08-01)
    ---------------------------------------------
    The target was pasted inside a ```python fence. Correct for a module; fatal
    for a markdown document, because the document carries its own fences and its
    FIRST ``` closes the wrapper. Measured on the zero-plant control document
    (307 lines, 14 fence lines): the first fence opens at line 46, so only 45 of
    307 lines — 14.7% — were inside the block. Everything after it was loose
    text the panel had no reason to read as the target at all. Findings were
    then asked to be cleared against a document the panel had mostly not seen.

    THE FIX
    -------
    No markdown fence. The target is delimited by a sentinel pair carrying a
    nonce derived from the source itself, and the sentinel is *proved* not to
    collide: while either sentinel occurs in the source it is lengthened, which
    terminates because a string longer than the source cannot be a substring of
    it. The label states what the target actually is — prose document or Python
    module — instead of asserting ``python`` over prose, and for a prose target
    the response template asks for a falsifier that opens the document by path,
    which is the only form a prose falsifier can take. Truncation, if it
    happens, is now declared rather than silent.
    """
    src = target_src or ""
    _LIMIT = 60000
    truncated = len(src) > _LIMIT
    if truncated:
        src = src[:_LIMIT]
    _suffix = str(target_rel or "").rsplit(".", 1)[-1].lower()
    is_prose = _suffix in {
        "md", "markdown", "rst", "txt", "text", "org", "tex", "adoc", "asciidoc",
    }
    # Non-collidable delimiter. The nonce makes an accidental clash effectively
    # impossible; the loop makes a deliberate one impossible, and terminates
    # because each pass lengthens the sentinel and the source is finite.
    import hashlib as _hashlib
    _nonce = _hashlib.sha256(src.encode("utf-8", "replace")).hexdigest()[:12]
    begin = f"<<<CDSFL_TARGET_BEGIN {_nonce}>>>"
    end = f"<<<CDSFL_TARGET_END {_nonce}>>>"
    while begin in src or end in src:  # pragma: no cover — adversarial only
        _nonce += "X"
        begin = f"<<<CDSFL_TARGET_BEGIN {_nonce}>>>"
        end = f"<<<CDSFL_TARGET_END {_nonce}>>>"
    if is_prose:
        _header = (
            f"TARGET DOCUMENT ({target_rel}) — a PROSE DOCUMENT, not Python "
            f"source. It is reproduced verbatim between the two sentinel lines "
            f"below. It contains its own ``` fenced listings; those fences "
            f"belong to the document and do NOT end it. Only the closing "
            f"sentinel ends it."
        )
        _template = (
            "  # runnable test that OPENS THE TARGET DOCUMENT BY PATH (the path "
            "named above) and asserts on its text or on a value recomputed from "
            "it; AssertionError/FALSIFIED"
        )
    else:
        _header = (
            f"TARGET MODULE ({target_rel}) — Python source, reproduced verbatim "
            f"between the two sentinel lines below."
        )
        _template = (
            "  # runnable test importing the REAL module; AssertionError/FALSIFIED"
        )
    if truncated:
        _header += (
            f" TRUNCATED: only the first {_LIMIT} characters of "
            f"{len(target_src)} are shown."
        )
    lines = [
        "This is what was found during the run and remains unresolved. "
        "Now clear the residuals.",
        "",
        _header,
        begin, src, end, "",
        "RESIDUAL FINDINGS TO CLEAR:",
    ]
    for cid, e in residuals.items():
        lines.append(
            f"- {cid} (severity {e.get('severity')}, status {e['status']}): "
            f"{(e.get('description') or '')[:400]}"
        )
    lines += [
        "",
        "For EACH residual above, respond with exactly one of:",
        "  FALSIFIER: <id>",
        "  ```python",
        _template,
        "  # iff the defect is present; clean exit otherwise",
        "  ```",
        "then, on its own lines and WITHOUT indentation:",
        _corrected_copy_instructions(),
        "or:",
        "  WITHDRAW <id>: <one-line reason it is not a real/testable defect>",
        "Nothing else counts. New findings are ignored.",
        "",
        _CORRECTED_COPY_WHY,
    ]
    return "\n".join(lines)


def _settle_confirmed_findings(registry, round_idx):
    """Apply the CONFIRMED+verified -> CLOSED transition one last time.

    THE DEFECT THIS FIXES. That transition lives in the per-round reconciliation
    pass (`if entry["status"] == "CONFIRMED" and entry.get("verified")`), which
    runs at the START of a round. A finding demonstrated in the FINAL round
    therefore never meets it: the run stops, and the finding is recorded as
    CONFIRMED when every one of its peers is recorded as CLOSED.

    Measured across the six completed runs: 158 of 160 criticals reached CLOSED.
    The two that did not — Exp 45 `C0031` and Exp 47 `C0070` — are both
    CONFIRMED, both `verified`, both with zero unresolved challenges, and both
    opened at the exact round their run converged. They are one bookkeeping step
    from settled, and the step never ran.

    This matters beyond tidiness because those two findings were read, from the
    status field alone, as demonstrated criticals left UNRESOLVED at close. They
    were not. Nothing escaped. The record was one transition behind, and the
    difference between "a critical escaped" and "a label lagged" is the
    difference between an unsafe instrument and an untidy one.

    The condition replicated here is exactly the reconciliation's, unresolved
    challenges included, so this can never close something the normal path would
    have held open. Returns the ids it settled, for the run report.
    """
    settled = []
    for cid, e in registry.entries.items():
        if e.get("status") != "CONFIRMED" or not e.get("verified"):
            continue
        confirms = [v for v in e.get("verdicts", []) if v.get("verdict") == "CONFIRM"]
        challenges = [v for v in e.get("verdicts", []) if v.get("verdict") == "CHALLENGE"]
        latest_confirm = max((v["round"] for v in confirms), default=-1)
        if [v for v in challenges if v["round"] >= latest_confirm]:
            continue  # unresolved challenge — the normal path would hold it open
        registry.resolve(cid, "CLOSED", round_idx)
        e["settled_post_convergence"] = True
        settled.append(cid)
    if settled:
        _log(f"  post-convergence settle: {len(settled)} CONFIRMED+verified "
             f"finding(s) closed that the final round had no successor to close "
             f"({', '.join(sorted(settled))})")
    return settled


def _post_convergence_sweep(registry, exp_config, cfg, round_idx, repo_root=None):
    """Bounded epilogue: panel clears residual non-terminal findings AFTER the
    convergence verdict is recorded. Guards (founder malady-proofing,
    2026-07-28): (1) runs strictly after the verdict — can never block,
    reverse, or improve convergence; (2) registers NO new findings (only the
    two labelled forms below are parsed); (3) bounded rounds; leftovers are
    reported honestly. Criticals can only be cleared by a CONFIRMED runnable
    demonstration — never by withdrawal (CONFIRM-only discipline holds)."""
    import re as _re
    n_rounds = int(getattr(cfg, "post_convergence_sweep_rounds", 0) or 0)
    if n_rounds <= 0:
        return {}
    from bench.falsifier_verify import reverify_falsifier
    # CONFIRMED is admitted as a residual (2026-07-31), but only the kind that is
    # genuinely unresolved. `_settle_confirmed_findings` runs immediately before
    # this and converts every CONFIRMED+verified finding with no unresolved
    # challenge to CLOSED — those are settled, not residual, and asking the panel
    # to re-falsify them would just burn dispatch. What survives here is the
    # CONTESTED-to-CONFIRMED case (reference_runner_v2.py ~1655), which reaches
    # CONFIRMED without `verified` and therefore never settles on its own.
    _TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE"}
    stats = {"cleared": 0, "withdrawn": 0, "rounds": 0, "remaining": 0}
    # Ids this sweep has already disposed of. Needed because clearing a residual
    # sets it to CONFIRMED, which is no longer in `_TERMINAL` — so without this
    # the next sweep round re-offers the same finding to the panel, clears it a
    # second time, and double-counts `cleared`. Caught 2026-07-31 by
    # test_exp43_fixes.py::test_falsifier_reattachment_clears_residual, which
    # went red the moment CONFIRMED left the terminal set. The cost of missing it
    # would have been a wasted panel dispatch per sweep round, per finding.
    _handled: set = set()
    try:
        target_src = (Path(repo_root or REPO_ROOT) / cfg.test_article).read_text(
            encoding="utf-8", errors="replace")
    except OSError:
        target_src = ""
    for _sweep_i in range(n_rounds):
        residuals = {cid: e for cid, e in registry.entries.items()
                     if e["status"] not in _TERMINAL and cid not in _handled}
        if not residuals:
            break
        stats["rounds"] += 1
        _log(f"  sweep round {_sweep_i + 1}/{n_rounds}: "
             f"{len(residuals)} residual(s) -> panel")
        prompt = _sweep_prompt(residuals, cfg.test_article, target_src)
        for mc in exp_config.models:
            live = {cid: e for cid, e in residuals.items()
                    if registry.entries[cid]["status"] not in _TERMINAL
                    and cid not in _handled}
            if not live:
                break
            try:
                resp, _ = dispatch_to_model(mc, prompt, _SWEEP_SYSTEM,
                                            enable_tools=True)
            except Exception:  # noqa: BLE001 — a dead model just skips its turn
                continue
            # (a0) labelled corrected passages, ingested BEFORE the falsifier
            # blocks below so a finding cleared in this same reply carries its
            # corrected copy from the moment it is cleared. The sweep runs after
            # the convergence verdict and clears nothing on the strength of a
            # corrected copy; this records the supply so the control has it.
            for _key, (_orig, _corr) in _extract_corrected_copies(resp or "").items():
                _cid = _key.upper()
                _e = registry.entries.get(_cid)
                if _e is None:
                    _log(f"  corrected copy UNMATCHED in sweep from "
                         f"{mc.label if hasattr(mc, 'label') else mc}: no "
                         f"finding answers to id {_key!r}")
                    continue
                _accept_corrected_copy(
                    _e, _orig, _corr, target_src,
                    target_rel=cfg.test_article,
                    by=mc.label if hasattr(mc, "label") else str(mc), cid=_cid)
            # (a) labelled falsifier re-attachment
            for m in _re.finditer(
                    r"FALSIFIER:\s*(C\d{4})\s*```(?:python)?\s*\n(.*?)```",
                    resp or "", _re.S):
                cid, code = m.group(1), m.group(2).strip()
                e = registry.entries.get(cid)
                if e is None or e["status"] in _TERMINAL or not code:
                    continue
                verdict = reverify_falsifier(code, repo_root=repo_root)
                if verdict == "CONFIRMED":
                    e["falsifier_code"] = code
                    e["falsifier_verdict"] = "CONFIRMED"
                    e["verified"] = True
                    e["resolved_by_sweep"] = mc.label if hasattr(mc, "label") else str(mc)
                    registry.resolve(cid, "CONFIRMED", round_idx)
                    stats["cleared"] += 1
                    _handled.add(cid)
                    stats.setdefault("items", {})[cid] = {
                        "disposition": "cleared",
                        "by": e.get("resolved_by_sweep")}
                elif (verdict == "REFUTED"
                        and float(e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD):
                    e["falsifier_verdict"] = "REFUTED"
                    e["withdrawn_by_sweep"] = mc.label if hasattr(mc, "label") else str(mc)
                    registry.resolve(cid, "REFUTED", round_idx)
                    stats["withdrawn"] += 1
                    _handled.add(cid)
                    stats.setdefault("items", {})[cid] = {
                        "disposition": "refuted_by_falsifier",
                        "by": e.get("withdrawn_by_sweep")}
                elif verdict == "REFUTED":
                    # FOUNDER RULING 2026-08-03. A critical cannot be CLEARED by a
                    # refutation — CONFIRM-only stands, and the Exp 42 evidence
                    # behind it (2 of 3 REFUTED criticals were themselves wrong) is
                    # untouched. But the computation RAN and produced an answer, and
                    # discarding that answer is the absurdity: the human adjudicating
                    # a permanent item never saw what the instrument already worked
                    # out, and a sound fix could be binned for scoring 0.71 rather
                    # than 0.69. The verdict is now RECORDED and travels to the human
                    # WITH the fix the panel devised. Nothing is cleared automatically.
                    _record_computed_evidence(
                        e, kind="falsifier_refuted",
                        by=mc.label if hasattr(mc, "label") else str(mc),
                        detail="a runnable falsifier ran and did NOT demonstrate the "
                               "defect; the claim may be sound",
                        falsifier=e.get("falsifier_code", ""))
                    stats["computed_evidence"] = stats.get("computed_evidence", 0) + 1
                    stats.setdefault("items", {})[cid] = {
                        "disposition": "critical_refuted_evidence_recorded",
                        "by": mc.label if hasattr(mc, "label") else str(mc)}
                # ERROR: leave for the residual report.
            # (b) reasoned withdrawal — SUB-CRITICAL ONLY
            for m in _re.finditer(r"WITHDRAW\s+(C\d{4})\s*:\s*(.{3,300})",
                                  resp or ""):
                cid, reason = m.group(1), m.group(2).strip()
                e = registry.entries.get(cid)
                if e is None or e["status"] in _TERMINAL:
                    continue
                if float(e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD:
                    # Same ruling. A reasoned withdrawal may not RETIRE a critical,
                    # but the reasoning is evidence a human should see rather than
                    # something the machine swallows without trace.
                    _record_computed_evidence(
                        e, kind="reasoned_withdrawal",
                        by=mc.label if hasattr(mc, "label") else str(mc),
                        detail=reason[:200])
                    stats["computed_evidence"] = stats.get("computed_evidence", 0) + 1
                    continue
                e["withdrawn_by_sweep"] = mc.label if hasattr(mc, "label") else str(mc)
                e["withdraw_reason"] = reason[:200]
                registry.resolve(cid, "REFUTED", round_idx)
                stats["withdrawn"] += 1
                _handled.add(cid)
                stats.setdefault("items", {})[cid] = {
                    "disposition": "withdrawn",
                    "by": e.get("withdrawn_by_sweep"),
                    "reason": reason[:200]}
    _TERMINAL2 = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
    stats["remaining"] = sum(1 for e in registry.entries.values()
                             if e["status"] not in _TERMINAL2)
    _log(f"  sweep complete: {stats['cleared']} cleared, "
         f"{stats['withdrawn']} withdrawn, {stats['remaining']} remaining")
    return stats


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
    # F7/F23 contextual gate (GE EXHAUSTED design): gate threshold stays fixed.
    # EXHAUSTED marking now done by _update_finding_statuses() pre-pass.
    open_ch = registry.open_crit_high_count()

    # F12 fix: guard against duplicate entries if called multiple times per round.
    if open_ch_history is not None:
        if not open_ch_history or open_ch_history[-1] != open_ch:
            open_ch_history.append(open_ch)

    # F7/F23 fix: enforce cfg.max_open_crit_high threshold (gate stays fixed).
    if open_ch > cfg.max_open_crit_high:
        failures.append(
            f"open_ch={open_ch} > max={cfg.max_open_crit_high}"
        )
    elif open_ch_history is None or len(open_ch_history) < cfg.open_ch_stability_window:
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
    contested = registry.contested_count(round_idx, subcritical_exclusion=bool(getattr(cfg, 'falsifier_gate_enabled', False)))
    if contested > 0:
        failures.append(f"contested={contested}")
    # FIX 1 residual queue visibility: excluded un-demonstrated sub-criticals
    # are logged (never gate) so the review queue is explicit, not silent.
    residuals = registry.undemonstrated_subcritical_ids()
    if residuals:
        if len(residuals) > 6:
            _log(f"  WARNING: residual queue size {len(residuals)} > 6 — "
                 f"a LARGE un-demonstrated queue signals a mechanical fault "
                 f"(intake/falsifier), not genuine residue. Review before trusting convergence.")
        _log(f"  residual queue (un-demonstrated sub-criticals, non-gating): "
             f"{len(residuals)} -> {', '.join(residuals[:8])}"
             f"{'...' if len(residuals) > 8 else ''}")
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


# A7 (2026-08-01): the irreducible-queue alarm is a HALT, not a veto ──────────
IRREDUCIBLE_QUEUE_HALT = "HALTED_IRREDUCIBLE_QUEUE_ALARM"


def build_irreducible_queue_alarm(
    registry: "FindingRegistry", cfg: RunnerConfig, round_idx: int,
) -> Optional[Dict[str, Any]]:
    """Build the evidence bundle for an over-bound irreducible queue, or None.

    Returns None while the queue is within ``cfg.max_irreducible_queue``.

    WHAT CHANGED AND WHY (A7). The bound itself was CORRECT on 2026-08-01: the
    zero-plant control locked 13 criticals as irreducible, and the cause was
    mechanical — the S_k hard gates were parsing prose as Python, so no fix
    could be admitted, so nothing could close. The alarm named a real
    instrument failure. It was then SUPPRESSED TWICE, by raising the bound,
    because of what it *did*: it returned "not converged" from the convergence
    checker and nothing else. That is the worst available response. It does not
    say why, it does not stop the run, it does not hand anyone the evidence —
    it just quietly denies a finish and lets the loop burn its round budget
    against a fault no further round can fix. An alarm that only obstructs gets
    turned off, and being turned off is how it lost twice to a real defect.

    So it now HALTS, NOTIFIES, and ATTACHES:

      * HALT — the run stops at this round with
        ``convergence_reason=HALTED_IRREDUCIBLE_QUEUE_ALARM`` and
        ``converged=False``. Distinct from convergence AND from a stall: it is
        neither a finish nor exhaustion, it is an instrument fault called by
        the instrument. Stopping is also the cheap option — the alternative
        spends paid dispatch on rounds that cannot close.
      * NOTIFY — a block-formatted message naming the count, the bound, the
        round, and what to look at first.
      * ATTACH — the per-finding evidence below, carried in the run report so
        the human adjudicating it does not have to reconstruct anything.

    The bound stays at its default of 2. Raising it is how this was suppressed;
    the answer to a loud alarm is to read the bundle, not to move the line.
    """
    count = registry.irreducible_queue_count()
    bound = int(getattr(cfg, "max_irreducible_queue", 2))
    if count <= bound:
        return None

    _TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
    evidence: List[Dict[str, Any]] = []
    for cid, e in registry.entries.items():
        if not e.get("irreducible_escalation"):
            continue
        if e.get("status") in _TERMINAL:
            continue
        if (e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
            continue
        sk = e.get("sk_result") or {}
        evidence.append({
            "canonical_id": cid,
            "status": e.get("status"),
            "severity": e.get("severity"),
            "source_model": e.get("source_model"),
            "open_since_round": e.get("open_since_round"),
            "last_status_change_round": e.get("last_status_change_round"),
            "description": (e.get("description") or "")[:300],
            # The three things that decide whether this is genuine
            # irreducibility or a mechanical failure wearing its clothes.
            "falsifier_present": bool(e.get("falsifier_code")),
            "falsifier_verdict": e.get("falsifier_verdict") or "",
            "sk_tristate": sk.get("tristate", ""),
            "sk_gate_details": sk.get("gate_details", {}),
            "verdicts": e.get("verdicts", [])[-4:],
            "routing_history": e.get("routing_history", []),
        })

    # The single most useful summary for a human opening this: if the whole
    # queue shares one S_k outcome or one empty-falsifier signature, the cause
    # is one mechanism, not thirteen independent hard problems.
    sk_states = sorted({(x["sk_tristate"] or "(none)") for x in evidence})
    no_falsifier = sum(1 for x in evidence if not x["falsifier_present"])

    notify = (
        f"IRREDUCIBLE-QUEUE ALARM at round {round_idx}: {count} criticals are "
        f"locked as irreducible, over the bound of {bound}.\n"
        f"Genuinely irreducible criticals are rare, so a queue this size is "
        f"overwhelmingly a MECHANICAL failure — routing, dedup, or a gate that "
        f"cannot speak to this target — presenting as irreducibility.\n"
        f"The run is HALTED, not merely blocked from converging. Nothing "
        f"further can close while the cause stands.\n"
        f"Evidence for all {len(evidence)} item(s) is attached under "
        f"'irreducible_queue_alarm' in the run report.\n"
        f"First things to read: S_k outcomes across the queue are "
        f"{sk_states or ['(none)']}; {no_falsifier} of {len(evidence)} carry no "
        f"falsifier at all. A single shared value in either column is the "
        f"mechanism.\n"
        f"Do NOT raise max_irreducible_queue to clear this — that is how the "
        f"same alarm was suppressed twice on 2026-08-01 while it was right."
    )

    return {
        "alarm": "IRREDUCIBLE_QUEUE",
        "action": "halt_notify_attach",
        "round": round_idx,
        "count": count,
        "bound": bound,
        "sk_states_in_queue": sk_states,
        "items_without_falsifier": no_falsifier,
        "notify": notify,
        "evidence": evidence,
    }


def _check_gamma_alt_convergence(
    round_idx: int,
    gamma: float,
    novel_critical_history: List[int],
    cfg: RunnerConfig,
    unresolved_critical: int = 0,
    contested: int = 0,
    rho_churn: bool = False,
    irreducible_queue: int = 0,
    gamma_critical: float = 1.0,
    total_findings: int = 0,
) -> Tuple[bool, str]:
    """Critical-quiescence convergence path (panel redesign 2026-05-23; TWO-SIDED gate
    2026-06-10).

    Documented in Exp 39 sub-experiment configs as an alternative pass
    condition. The Exp 39-0 post-mortem flagged the main gate's
    ``open_ch <= max_open_crit_high`` as effectively unreachable, so a
    complementary count-based criterion is needed.

    Convergence on this path = critical decay flattened AND review clean.
    It REQUIRES ALL of:
      (a) gamma_alt_consecutive_zero_crit consecutive rounds with zero
          NEW genuine critical findings on the SETTLED/verifier-filtered
          series (critical decay has flattened), AND
      (b) no unresolved/unverified critical candidate (A4 fail-safe), AND
      (c) not contested, AND
      (d) not churning.
    All-severity novelty is deliberately NOT required to be low: a clean
    critical run must not be held open by non-critical footnotes.

    γ IS REPORTED, NEVER A TRIGGER OR BLOCKER (panel ruling 2026-05-23).
    The former γ-threshold trigger (condition 1) is DELETED: a Duane
    depletion estimate rising is not, on its own, evidence that critical
    discovery has stopped, and γ is telemetry-only everywhere. γ does NOT
    appear in the convergence condition; it is accepted only so the reason
    string can report it.

    A4 VERIFIER FAIL-SAFE (correctness-critical): an UNVERIFIED
    critical-severity candidate (status UNCONFIRMED, severity >= 0.7)
    must NOT silently count as "zero new critical." Such a candidate is
    excluded from the settled novelty series, so without this guard a
    critical the system gave up on (finalize sweep / grace-period reopen)
    would vanish from the count and let the streak accrue. When
    ``unresolved_critical > 0`` the streak does NOT accrue this round and
    convergence is blocked; the caller logs the count for HIL. OPEN /
    CONTESTED / REOPENED criticals are still in play (the settled series
    counts them) and are governed by the state gate's open-critical
    machinery — they are NOT silent and are not what A4 targets.

    ``contested`` and ``rho_churn`` come from the same registry / rho
    machinery the state gate uses, so the count path enforces (c) and (d)
    directly rather than relying on the OR with the state gate.

    Returns (converged, reason).
    """
    if round_idx < cfg.gamma_alt_earliest_round:
        return False, (
            f"critical-quiescence too early (round {round_idx} < "
            f"{cfg.gamma_alt_earliest_round})"
        )

    window = cfg.gamma_alt_consecutive_zero_crit
    recent_tail = (
        novel_critical_history[-window:]
        if len(novel_critical_history) >= window
        else novel_critical_history
    )

    # A4 fail-safe (b): an unverified (UNCONFIRMED) critical candidate
    # must not let the zero-critical streak accrue silently. Block
    # regardless of the count tail; surface for HIL via the reason string.
    if unresolved_critical > 0:
        return False, (
            f"A4 BLOCK: {unresolved_critical} unverified critical-severity "
            f"candidate(s) (status UNCONFIRMED, sev>=0.7) pending at round "
            f"{round_idx} — zero-critical streak does NOT accrue "
            f"(novel_crit_recent={recent_tail}). HIL review required."
        )

    # Small-queue alarm (static-queue closure, 2026-06-09; RETARGETED A7,
    # 2026-08-01). The loop MAY close while handing a SMALL queue of
    # ladder-exhausted irreducible criticals to the human. A queue larger than
    # the bound is overwhelmingly a routing/dedup MECHANICAL FAILURE
    # masquerading as irreducibility.
    #
    # This function NO LONGER REFUSES CONVERGENCE on that condition, and the
    # removal is not a weakening. Refusing here was a silent veto: it denied a
    # finish, gave no evidence, and let the loop keep spending rounds against a
    # fault no round could fix — which is precisely why the alarm was
    # suppressed twice on 2026-08-01 by raising the bound, while it was right
    # both times. The condition is now enforced EARLIER and HARDER, by
    # ``build_irreducible_queue_alarm`` in the round loop, which halts the run
    # outright, prints the notification and attaches the per-finding evidence
    # bundle to the report. The run therefore never reaches this check with an
    # over-bound queue; the note below exists so that a reader of a reason
    # string is told the queue size rather than left to infer it.
    _queue_note = ""
    if irreducible_queue > cfg.max_irreducible_queue:
        _queue_note = (
            f" [NOTE: irreducible queue {irreducible_queue} > bound "
            f"{cfg.max_irreducible_queue} — the run-loop alarm halts on this "
            f"condition before convergence is assessed; see "
            f"build_irreducible_queue_alarm]")

    # Review-clean gates (c) not contested, (d) not churning. A clean
    # critical tail does not mean convergence while the panel is still
    # contesting findings or churning re-derivations.
    if contested > 0:
        return False, (
            f"critical-quiescence blocked: contested={contested} at round "
            f"{round_idx} (novel_crit_recent={recent_tail})"
        )
    if rho_churn:
        return False, (
            f"critical-quiescence blocked: churn (rho_avg below "
            f"{cfg.rho_threshold}) at round {round_idx} "
            f"(novel_crit_recent={recent_tail})"
        )

    # Convergence (a): K consecutive rounds with zero novel CRITICAL on
    # the settled/genuine series — the only trigger on this path.
    if len(novel_critical_history) >= window:
        recent = novel_critical_history[-window:]
        if all(n == 0 for n in recent):
            # TWO-SIDED GATE (founder ruling 2026-06-10). Convergence requires BOTH sides of
            # the same diminishing-returns coin to AGREE, neither alone:
            #   (1) gamma_critical >= gamma_alt_threshold  — the decay curve has flattened
            #       (gamma is an ACTIVE convergence condition, NOT merely "reported"); AND
            #   (2) window consecutive zero-new-critical rounds — the strict, threshold-free
            #       'insurance' endpoint of that same curve.
            # The threshold is conservative (the whole-history Duane slope saturates below 1.0,
            # so a high cutoff would be unreachable); the count supplies the precision. On the
            # 9 June live run both held first at round 6 (gamma_critical 0.607 >= 0.30, count
            # [0,0,0]) — identical to the count-only result, confirming the two naturally agree.
            theta = cfg.gamma_alt_threshold
            # VACUOUS-CURVE CASE (2026-07-29, found pre-launch on the zero-plant
            # control). GAMMA REMAINS AN ACTIVE, LOAD-BEARING CONDITION — this
            # narrows the estimator's DOMAIN, it does not weaken the gate.
            #
            # _estimate_gamma fits a Duane decay to the cumulative critical
            # series. Where no critical was EVER found, that series is all
            # zeros: there is no curve to fit, and the estimator returns 0.0 —
            # numerically identical to the worst possible case, a constant
            # arrival rate with no decay at all ([2,2,2,2,2,2] also returns
            # ~0.0). Those two are opposites. Comparing an undefined estimate
            # against a threshold as though it were a measurement means a panel
            # that reviewed a genuinely clean document perfectly can never
            # converge, and would burn its full round budget and report
            # non-convergence — halting the arc on a document with nothing in it.
            #
            # Diminishing returns is satisfied here in the strongest possible
            # sense: the critical error space was exhausted before round one.
            # So the gamma side is satisfied by vacuity, under two guards:
            #   * cumulative critical over the WHOLE history must be zero — a
            #     constant-rate series has a positive cumulative count and stays
            #     blocked, which is the case this must never be confused with;
            #   * the panel must have produced findings of SOME severity, so
            #     "nothing was critical" is distinguishable from "nothing came
            #     back" (a dead panel, or severity classification broken such
            #     that nothing is ever critical).
            # It is logged distinctly and never silently, and the reason string
            # carries both counts so a reader can judge the run for themselves.
            cumulative_critical = sum(novel_critical_history)
            if cumulative_critical == 0 and gamma_critical < theta:
                if total_findings > 0:
                    return True, (
                        f"CRITICAL_QUIESCENCE_CONVERGED (two-sided gate, VACUOUS CURVE): "
                        f"zero critical findings across the ENTIRE run "
                        f"(history={novel_critical_history}) over {total_findings} finding(s) "
                        f"of some severity, so the critical decay curve does not exist and "
                        f"gamma_critical={gamma_critical:.3f} is undefined rather than low. "
                        f"The critical error space was exhausted before round one; the "
                        f"{window}-round zero-critical condition holds. REVIEW THIS RUN: a "
                        f"clean target and a broken severity classifier look alike from here."
                        + _queue_note
                    )
                return False, (
                    f"two-sided gate: gamma_critical={gamma_critical:.3f} < threshold "
                    f"{theta}, and zero critical findings across the entire run — but the "
                    f"panel produced NO findings of any severity either. That is a dead "
                    f"panel or a broken review, not an exhausted error space, so the "
                    f"vacuous-curve path does NOT apply. Convergence refused at round "
                    f"{round_idx}; diagnose the dispatch."
                )
            if gamma_critical < theta:
                return False, (
                    f"two-sided gate: {window} zero-new-critical rounds met, but "
                    f"gamma_critical={gamma_critical:.3f} < threshold {theta} — the decay curve "
                    f"has not yet flattened. BOTH sides of the gate must agree."
                )
            return True, (
                f"CRITICAL_QUIESCENCE_CONVERGED (two-sided gate): gamma_critical="
                f"{gamma_critical:.3f} >= {theta} (decay curve flattened) AND {window} "
                f"consecutive zero-new-critical rounds (history tail={recent}) at round "
                f"{round_idx} — the two sides of the same diminishing-returns measure agree"
                + _queue_note
            )

    return False, (
        f"two-sided gate not met: novel_crit_recent={recent_tail}, "
        f"gamma_critical={gamma_critical:.3f} (convergence needs gamma_critical >= "
        f"{cfg.gamma_alt_threshold} AND {window} consecutive zero-new-critical rounds)"
        + _queue_note
    )


# F6 (pre-registered 2026-05-18): the critical/structural severity
# boundary. The AUTHORITATIVE definition is consequence-based, in
# bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md; this
# numeric is the operational proxy for that rubric. Legacy scattered
# `0.7` critical-severity literals remain a tracked migration item; the
# hardened gate uses this named constant.
CRITICAL_SEVERITY_THRESHOLD = 0.7

# ── Severity calibration (over-production bounding, 2026-06-10, gated default-off) ──
# Markers a finding must carry to be ELIGIBLE for demotion, and markers that make it
# INELIGIBLE no matter what. Read off the registry dict, so no Finding-dataclass change.
# A reconciliation/panel step (or a future severity-classifier cell) sets `latent=True`
# and/or `finding_category`; absent those keys NOTHING is ever demoted (fail-safe).
_SEVERITY_CALIB_NEVER_DEMOTE_CATEGORIES = frozenset(
    {"safety", "core", "core_functionality", "security", "data_loss"}
)


def _is_demotion_eligible(entry: Dict[str, Any]) -> bool:
    """Conservative, principled criterion for lowering an over-rated finding.

    Demotion-eligible iff ALL hold:
      (1) currently critical: severity >= CRITICAL_SEVERITY_THRESHOLD;
      (2) a REAL defect by independent demonstration: falsifier_verdict ==
          "CONFIRMED" (the unfakeable active-demonstration signal — a finding
          without it is NEVER demoted: a broken/absent falsifier could have
          masked a real, non-latent defect);
      (3) explicitly flagged LATENT/conditional: entry["latent"] truthy (the
          defect is genuine but requires a trigger absent from the usage contract);
      (4) NOT in a never-demote category (safety / core-functionality / security /
          data_loss).
    The conjunction (2) AND (3) — proven-real AND explicitly-conditional — is the
    safeguard the brief requires. Safety/core defects are categorically excluded.
    """
    if (entry.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
        return False
    if entry.get("falsifier_verdict") != "CONFIRMED":
        return False
    if not entry.get("latent"):
        return False
    category = str(entry.get("finding_category") or "").strip().lower()
    if category in _SEVERITY_CALIB_NEVER_DEMOTE_CATEGORIES:
        return False
    return True


def _calibrate_finding_severity(
    entry: Dict[str, Any], floor: float, round_idx: int,
) -> bool:
    """Lower one over-rated-but-genuine finding's severity below critical.

    Records the calibration on the entry (never deletes it): severity_calibrated,
    severity_original, severity (= floor, clamped < threshold), calibration_reason,
    calibration_round. Idempotent: a re-sweep on a later round never double-lowers
    or overwrites the original. Returns True iff this call performed the demotion.
    """
    if entry.get("severity_calibrated"):
        return False
    original = entry.get("severity") or 0.0
    safe_floor = min(floor, CRITICAL_SEVERITY_THRESHOLD - 0.01)
    entry["severity_original"] = original
    entry["severity"] = safe_floor
    entry["severity_calibrated"] = True
    entry["calibration_round"] = round_idx
    entry["calibration_reason"] = (
        f"severity calibrated {original:.2f} -> {safe_floor:.2f}: falsifier-CONFIRMED "
        f"REAL defect flagged LATENT/conditional (requires a trigger absent from the "
        f"usage contract). Retained in registry; no longer a convergence-blocking "
        f"critical. Calibrated at round {round_idx}."
    )
    return True


def _apply_severity_calibration(registry, cfg: "RunnerConfig", round_idx: int) -> int:
    """GATED sweep: demote every demotion-eligible over-rated critical.

    Default-off no-op (byte-identical): returns 0 and mutates nothing when
    cfg.severity_calibration_enabled is False. When on, demotes each eligible
    entry. Because every critical-counting channel (_settled_novelty_series,
    unverified_critical_count, open_crit_high_count) reads entry["severity"]
    against CRITICAL_SEVERITY_THRESHOLD at call-time, running this sweep BEFORE
    those reads removes each demoted finding from the critical counts with no
    per-channel change. Hard-terminal entries are skipped. Returns the number
    demoted this round (0 when the gate is off).
    """
    if not getattr(cfg, "severity_calibration_enabled", False):
        return 0
    floor = getattr(cfg, "severity_calibration_floor", 0.69)
    _terminal = {"MERGED", "CLOSED", "DUPLICATE", "REFUTED"}
    demoted = 0
    entries = registry.entries if hasattr(registry, "entries") else {}
    for cid, e in list(entries.items()):
        if e.get("status") in _terminal:
            continue
        if not _is_demotion_eligible(e):
            continue
        if _calibrate_finding_severity(e, floor, round_idx):
            demoted += 1
            _log(
                f"  severity-calibration: {cid} demoted "
                f"{e['severity_original']:.2f} -> {e['severity']:.2f} "
                f"(falsifier-CONFIRMED real, flagged latent) — retained, "
                f"no longer a blocking critical"
            )
    if demoted:
        _log(
            f"  severity-calibration: {demoted} over-rated-but-genuine critical(s) "
            f"demoted below {CRITICAL_SEVERITY_THRESHOLD} this round (retained with "
            f"reason; convergence no longer blocked by them)"
        )
    return demoted


# F4: post-reconciliation statuses that are NOT genuine novelty —
# stripped before γ sees them (mirrors the runner's existing per-round
# γ-input correction and bench/exp40_gamma_findings_audit.py).
_NON_NOVEL_TERMINAL_STATUSES = {
    "MERGED", "DUPLICATE", "UNCONFIRMED", "REFUTED",
}


def _settled_novelty_series(
    registry, max_round: int,
) -> Tuple[List[int], List[int]]:
    """Production-faithful per-round novelty from the SETTLED registry.

    For each round r in 0..max_round, count canonical entries whose
    open_since_round == r and whose FINAL (post-reconciliation) status
    is genuinely novel. Returns (all_per_round, critical_per_round),
    critical = severity >= CRITICAL_SEVERITY_THRESHOLD. This is the F4
    fix: the gate reads the settled registry, not the live-at-round
    accumulator that produced the 0.305-vs-0.231 flip.
    """
    entries = registry.entries if hasattr(registry, "entries") else {}
    vals = (list(entries.values())
            if isinstance(entries, dict) else list(entries))
    all_s = [0] * (max_round + 1)
    crit_s = [0] * (max_round + 1)
    for e in vals:
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in _NON_NOVEL_TERMINAL_STATUSES:
            continue
        all_s[r] += 1
        if (e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD:
            crit_s[r] += 1
    return all_s, crit_s


# Two unlocated criticals are the SAME finding iff their hard-token signatures
# (numbers, claim IDs, backticked identifiers — the content a model cannot
# paraphrase away) overlap by at least this Jaccard fraction. 0.20 is the
# repo's measured within-location cut (convergence_location.WITHIN_LOCATION_THRESHOLD),
# reused here because it answers the same question: two findings that code
# location cannot separate — do their hard tokens agree? Held as a LOCAL
# constant rather than imported so a future recalibration of the within-location
# cut cannot silently move the convergence gate.
#
# HONEST LIMIT: 0.20 was swept against within-location pairs, NOT against
# unlocated pairs specifically — that sub-population has never been swept, and
# this number is therefore a reasoned reuse, not a measured optimum for it.
# What IS measured: over the six faithfully-replayable archived runs
# (exp42/43/44/45/46/47 location-keyed live), the count-side convergence round is
# IDENTICAL for every cut in [0.15, 0.40]. At >= 0.50 exp46 loses its
# convergence. At the degenerate end (identity keying, i.e. no merging at all)
# exp46 loses it too. The outcome is insensitive across the band; the band's
# edges are where it stops being.
_UNLOCATED_MERGE_THRESHOLD = 0.20

# Prefix for the fallback identity of a critical naming no code location.
# NOT a single shared bucket — see _unlocated_novelty_key.
_UNLOCATED_KEY_PREFIX = "<unlocated:"


def _unlocated_novelty_key(description: str, buckets: List[Tuple[str, Any]]) -> str:
    """The novelty key for a critical from which NO code location could be extracted.

    THE DEFECT THIS CLOSES (found 2026-08-04, fixed 2026-08-08). This branch used
    to return the single constant ``"<generic>"`` for every unlocated finding. The
    first such critical claimed it; every later one was therefore non-novel
    FOREVER, whatever it said. Reported as 42 of 288 criticals (14.6%) across 9
    runs of the modern falsifier-live regime; re-measured independently
    2026-08-08 over all 11 Exp 42-49 runs carrying a registry at 50 of 351
    (14.2%), and both agree on the worst case, Exp 47 at 11 of 44 (25.0%). A
    PARSING failure silently promoted to an identity judgement. It is not the
    co-location trade-off, which is a deliberate conservative choice with a
    stated rationale; this had none.

    WHY THE PARSE FAILS, measured on Exp 47: ``target_symbols`` extracts only AST
    function/method/class names, so a finding about a module-level constant (the
    ``_ALT_HEADER_RE`` / ``_CONTRAST_RE`` / ``_DIM_LINE_RE`` regex family) names
    no extractable symbol. Ten distinct criticals about four different regexes
    collapsed to one.

    THE RULE. Fall back to the finding's own STEM signature — numbers, claim IDs
    and backticked identifiers, the content a model cannot re-word away. A finding
    joins an existing bucket iff its signature is at least
    ``_UNLOCATED_MERGE_THRESHOLD`` Jaccard-similar to that bucket's; otherwise it
    opens a new one. So two DIFFERENT unlocated findings are two keys, and the
    same finding re-worded is one. A finding with an EMPTY signature falls back to
    a hash of its own normalised text — never to a shared constant.

    HOW OFTEN THAT FALLBACK FIRES, corrected 2026-08-08 by the adversarial pass.
    This docstring cited 2.5%, carried over from ``stem_signature``'s own
    measurement (160 findings, 97.5% carry a hard token). That figure is for a
    different and smaller population. Re-measured over all 351 critical entries in
    the Exp 42-49 archive: 5.7% of criticals have an empty signature, and among
    the UNLOCATED sub-population this branch actually serves it is 12.0% (6 of
    50) — roughly five times the figure previously stated here. The direction is
    safe (a per-finding hash splits, so it can only delay), but the hash path
    carries more of this fix than the old number implied.

    DIRECTION OF ERROR: this errs toward SPLITTING. It can only partition the old
    single bucket into more keys, and located findings are untouched, so every
    per-round count is >= the old count. A zero round can therefore only become
    non-zero: convergence can be DELAYED but never brought forward. Delay costs
    rounds; the direction it replaces cost a permanently invisible critical.
    Measured on the archive, no run's convergence outcome changes (see
    bench/tests/test_generic_location_bucket.py).

    ``buckets`` is the caller's accumulator of ``(key, signature)`` pairs and is
    APPENDED TO in place when a new bucket opens.
    """
    import hashlib

    from bench.convergence_location import signature_similarity, stem_signature

    sig = stem_signature(description or "")
    if not sig:
        # No hard token to key on. A per-finding text hash still errs toward
        # splitting; falling back to a shared constant here would reinstate
        # exactly the defect above.
        norm = re.sub(r"\s+", " ", (description or "").strip().lower())
        digest = hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]
        return f"{_UNLOCATED_KEY_PREFIX}text:{digest}>"
    for key, prev in buckets:
        if signature_similarity(sig, prev) >= _UNLOCATED_MERGE_THRESHOLD:
            return key
    key = f"{_UNLOCATED_KEY_PREFIX}{len(buckets)}>"
    buckets.append((key, sig))
    return key


def _location_keyed_critical_series(registry, max_round, symbols) -> List[int]:
    """Per-round NEW critical count keyed by code LOCATION — the target-file
    symbol(s) a finding names — instead of the model-chosen finding-id used by the
    legacy path. A critical is NEW iff it names a code location not previously
    flagged (conservative S3 rule; locations accumulate across all criticals).
    Criticals naming no extractable location are keyed by content instead — see
    _unlocated_novelty_key.

    Verified 2026-06-08 (four independent computations + adversarial workflow wf_88bbdd46-194)
    to converge Exp 42 (~round 6) where the ID-proxy series never does.

    THIS SERIES GATES whenever ``location_keyed_convergence`` is set: the caller
    overwrites ``novel_critical_history[-1]`` with it, feeding the COUNT side of
    the two-sided gate (K consecutive zero-new-critical rounds). Sixteen configs
    set it, starting Exp 42. It does NOT touch gamma_critical, which is computed
    independently from the settled series. This docstring said "SHADOW
    (telemetry-only, NEVER gates)" until 2026-08-08 — false since the first
    location-keyed live run, and precisely the kind of stale safety claim that
    makes a real gate look like telemetry to a reader.

    KNOWN LIMITATION, unchanged: location-only keying cannot see a SECOND distinct
    defect in an already-flagged function. That is a deliberate conservative
    trade-off; see bench/audit_closing_window.py, which reports when it could have
    bitten. See experimental_notes/Convergence_Consolidation_Plan_2026-06-08.md.
    """
    from bench.convergence_location import finding_locations
    entries = registry.entries if hasattr(registry, "entries") else {}
    vals = (list(entries.values()) if isinstance(entries, dict) else list(entries))

    def _ord(e):
        r = e.get("open_since_round")
        return (r if r is not None else 1_000_000, str(e.get("canonical_id", "")))

    seen: set = set()
    unlocated_buckets: List[Tuple[str, Any]] = []
    series = [0] * (max_round + 1)
    for e in sorted(vals, key=_ord):
        r = e.get("open_since_round")
        if r is None or r < 0 or r > max_round:
            continue
        if e.get("status") in _NON_NOVEL_TERMINAL_STATUSES:
            continue
        if (e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
            continue
        desc = e.get("description", "") or ""
        locs = finding_locations(desc, symbols)
        key = (set(locs) if locs
               else {_unlocated_novelty_key(desc, unlocated_buckets)})
        if key - seen:
            series[r] += 1
        seen |= key
    return series


def _check_hardened_convergence(
    round_idx: int, registry, cfg: RunnerConfig,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Hardened gate (F4 + F6 + conjunction + dual-series + sparsity).

    Converged iff, on the SETTLED critical/structural series:
      (A) γ_critical >= gamma_alt_threshold, AND
      (B) that crossing is SUSTAINED over gamma_crit_sustain_rounds
          consecutive settled recomputes (no single-round knife-edge),
          AND robust to leave-one-round-out within gamma_crit_loo_tol,
      AND
      (C) gamma_alt_consecutive_zero_crit consecutive settled rounds
          have zero novel critical findings.
    Sparsity fallback: if the cumulative critical count is below
    gamma_crit_min_cumulative the slope is unreliable, so γ_critical is
    reported but NOT gated and closure rests on (C) alone (the
    count-based criterion is robust to sparsity). All-novelty γ is
    computed and returned as a DIAGNOSTIC only — never gates.
    """
    telem: Dict[str, Any] = {}
    if round_idx < cfg.gamma_alt_earliest_round:
        return False, (f"hardened-gate too early (round {round_idx} < "
                       f"{cfg.gamma_alt_earliest_round})"), telem

    all_s, crit_s = _settled_novelty_series(registry, round_idx)
    g_all = _estimate_gamma(all_s)
    g_crit = _estimate_gamma(crit_s)
    cum_crit = sum(crit_s)
    theta = cfg.gamma_alt_threshold
    W = cfg.gamma_alt_consecutive_zero_crit
    zero_crit_ok = (len(crit_s) >= W and all(c == 0 for c in crit_s[-W:]))
    telem.update(gamma_all_settled=round(g_all, 4),
                 gamma_crit_settled=round(g_crit, 4),
                 cum_critical=cum_crit, zero_crit_ok=zero_crit_ok)

    # Sparsity fallback — critical pool too small for a stable slope.
    if cum_crit < cfg.gamma_crit_min_cumulative:
        telem["mode"] = "sparsity_fallback"
        if zero_crit_ok:
            return True, (
                f"HARDENED_CONVERGED (sparsity fallback): cum_critical="
                f"{cum_crit} < {cfg.gamma_crit_min_cumulative}; "
                f"γ_crit={g_crit:.3f} reported-not-gated; {W} consecutive "
                f"settled zero-novel-critical rounds met at R{round_idx} "
                f"[γ_all diag={g_all:.3f}]"), telem
        return False, (
            f"hardened not met (sparsity, cum_crit={cum_crit}): "
            f"zero-crit window not satisfied; γ_crit={g_crit:.3f} "
            f"reported-not-gated [γ_all diag={g_all:.3f}]"), telem

    telem["mode"] = "full"
    # (B) sustained over consecutive prior settled recomputes
    sustained = g_crit >= theta
    for k in range(1, max(1, cfg.gamma_crit_sustain_rounds)):
        prior = crit_s[: len(crit_s) - k]
        if len(prior) < 2 or _estimate_gamma(prior) < theta:
            sustained = False
            break
    # (B) leave-one-round-out robustness
    loo_min = g_crit
    for i in range(len(crit_s)):
        loo = crit_s[:i] + crit_s[i + 1:]
        if len(loo) >= 2:
            loo_min = min(loo_min, _estimate_gamma(loo))
    loo_ok = loo_min >= (theta - cfg.gamma_crit_loo_tol)
    gamma_crit_ok = (g_crit >= theta) and sustained and loo_ok
    telem.update(sustained=sustained, loo_min=round(loo_min, 4),
                 loo_ok=loo_ok, gamma_crit_ok=gamma_crit_ok)

    if gamma_crit_ok and zero_crit_ok:
        return True, (
            f"HARDENED_CONVERGED: γ_crit={g_crit:.3f} ≥ {theta} "
            f"(sustained {cfg.gamma_crit_sustain_rounds}r, loo_min="
            f"{loo_min:.3f}) AND {W} consecutive settled "
            f"zero-novel-critical at R{round_idx} "
            f"[γ_all diag={g_all:.3f}, cum_crit={cum_crit}]"), telem
    return False, (
        f"hardened not met: γ_crit={g_crit:.3f} (≥{theta}? "
        f"{g_crit >= theta}; sustained={sustained}; loo_ok={loo_ok}) "
        f"AND zero_crit_ok={zero_crit_ok} "
        f"[γ_all diag={g_all:.3f}, cum_crit={cum_crit}]"), telem


def _check_stall_convergence(
    round_idx: int,
    registry: FindingRegistry,
    gamma: float,
    stall_history: List[Dict[str, int]],
    cfg: RunnerConfig,
    consecutive_churn_rounds: int = 0,
) -> Dict[str, Any]:
    open_ch = registry.open_crit_high_count()
    contested = registry.contested_count(round_idx, subcritical_exclusion=bool(getattr(cfg, 'falsifier_gate_enabled', False)))
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

    # D1-B: churn-based stall detection.
    # Persistent churn with high gamma is a stall signal even when
    # open_ch/contested fluctuate — the system is producing re-derivations,
    # not genuine novelty.
    churn_stall_window = max(cfg.stall_window, 4)  # at least 4 rounds of churn
    if (consecutive_churn_rounds >= churn_stall_window
            and gamma >= cfg.stall_gamma_terminate
            and cfg.stall_gamma_termination_enabled):
        result["stalled"] = True
        result["tier"] = "terminate"
        result["terminate"] = True
        result["reason"] = (
            f"STALL_CONVERGED (churn): {consecutive_churn_rounds} consecutive "
            f"churn rounds, gamma={gamma:.3f} >= {cfg.stall_gamma_terminate}"
        )
        return result
    if (consecutive_churn_rounds >= churn_stall_window
            and gamma >= cfg.stall_gamma_advisory):
        result["stalled"] = True
        result["tier"] = "advisory"
        result["reason"] = (
            f"Stall advisory (churn): {consecutive_churn_rounds} consecutive "
            f"churn rounds, gamma={gamma:.3f} >= {cfg.stall_gamma_advisory}"
        )
        return result

    window = stall_history[-cfg.stall_window:]
    open_values = [s["open_ch"] for s in window]
    contested_values = [s["contested"] for s in window]
    if not (all(v == open_values[0] for v in open_values) and
            all(v == contested_values[0] for v in contested_values)):
        result["reason"] = f"not static — open_ch {open_values}, contested {contested_values}"
        return result
    result["stalled"] = True
    if (gamma >= cfg.stall_gamma_terminate
            and cfg.stall_gamma_termination_enabled):
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
    cfg: Optional["RunnerConfig"] = None,
) -> Tuple[bool, str]:
    """Decide whether to extend the round budget past ``cfg.max_rounds``.

    ``cfg`` became load-bearing in 1cec60d (27 July 2026), which added the
    gated sub-critical exclusion to the two ``contested_count`` calls below but
    did not add the parameter — so both lines read a name that exists in no
    enclosing scope and this function raised NameError on every call. It was
    never seen because it is only called at ``round_idx == cfg.max_rounds - 1``
    with ``extended`` still False, and Exp 44-49 all converged before that.
    A run that used its whole budget without converging would have died here.
    Default None keeps the exclusion off, which is the pre-1cec60d behaviour.
    """
    reasons = []
    if registry.open_crit_high_count() > 0:
        reasons.append(f"open CRIT/HIGH: {registry.open_crit_high_count()}")
    if registry.contested_count(round_idx, subcritical_exclusion=bool(getattr(cfg, 'falsifier_gate_enabled', False))) > 0:
        reasons.append(f"contested: {registry.contested_count(round_idx, subcritical_exclusion=bool(getattr(cfg, 'falsifier_gate_enabled', False)))}")
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

# Secondary-route fallback accumulators (2026-05-22, founder-directed).
# Populated by _dispatch_single_model's in-round fallback path when a
# model's primary route fails/empties and its secondary route is used.
# `_secondary_route_usage` logs each successful secondary dispatch (one
# entry per turn that used the secondary); `_persistent_empty_flags`
# logs turns where BOTH primary and secondary failed (the genuine
# "this round, this model contributed nothing" signal — never benched,
# raised to HIL at end of run). Cleared at experiment start (mirrors
# _itc_hil_flags pattern).
_secondary_route_usage: List[Dict[str, Any]] = []
_persistent_empty_flags: List[Dict[str, Any]] = []

# G7 merge-arbitration context (Exp 40 continuation, 15 May 2026).
# Follows the established module-state pattern (_itc_*) so
# _update_finding_statuses keeps a stable signature — its other
# callers/tests are unaffected. Populated by run_experiment at
# experiment start only when cfg.merge_arbitration_enabled is True;
# left empty otherwise, in which case every arbitration hook is inert
# and behaviour is byte-identical to pre-G7.
#   enabled        : bool
#   panel          : list[ModelConfig]
#   dispatch_fn    : callable(model_cfg, prompt) -> (response, elapsed)
#   min_defer_count: int (arbitrate on the Nth consecutive defer)
#   max_per_round  : int (per-round dispatch budget)
#   tiebreaker_gamma : float (round-level sweep trigger)
#   used_this_round: int (reset each round by run_experiment)
#   log            : list[dict] (audit trail of arbitration results)
_merge_arb_ctx: Dict[str, Any] = {}


_FINDING_DECL_RE = re.compile(
    r'(?:FINDING.ID\s*[:=]|<<<\s*FINDING\b|\(F\d{2,4}[,)])',
    re.IGNORECASE
)


def _itc_detect(
    model_label: str, round_idx: int,
    findings_count: int, response_text: str,
    prior_finding_ids: Set[str], current_finding_ids: Set[str],
    dispatch_error: Optional[str] = None,
    raw_finding_markers: int = 0,
    verdict_count: int = 0,
) -> Optional[str]:
    if dispatch_error and ("context length" in dispatch_error.lower()
                           or "token" in dispatch_error.lower()):
        return ITC_CAPABILITY_MISMATCH
    if not response_text or len(response_text.strip()) < 50:
        return ITC_TRANSIENT_FAILURE
    if findings_count == 0 and verdict_count == 0 and len(response_text) > 200:
        # Original false-positive case: model produced substantive output
        # but the parser extracted neither findings nor verdicts. That
        # IS a real signal (parser failure or model misbehaviour).
        # Verdict-heavy rounds (Codex Exp 40 rounds 3-4: 5,715 chars of
        # MERGE/CHALLENGE/REJECT verdicts on existing canonical findings)
        # are healthy late-arc behaviour, not CAPABILITY_MISMATCH — the
        # 15 May 2026 fix adds 'verdict_count == 0' to the gate so those
        # rounds are no longer falsely flagged.
        history = _itc_model_state.get(model_label, {}).get("history", [])
        recent_empty = sum(
            1 for h in history[-2:]
            if h.get("findings") == 0 and h.get("verdicts", 0) == 0
        )
        if recent_empty >= 1:
            return ITC_CAPABILITY_MISMATCH
        return ITC_TRANSIENT_FAILURE
    # D5 fix: output quality signal — adaptive, per-model.
    # Parse yield = (findings_count + verdict_count) / raw_finding_markers.
    # In late rounds, models shift from producing new findings to issuing
    # verdicts (CONFIRM/CHALLENGE) on existing findings.  Verdicts are
    # valid structured output that the parser captures, so they count
    # towards productive yield.  Without this, verdict-heavy rounds
    # deflate parse_yield and cause false DEGRADATION flags.
    #
    # Each model's baseline yield is computed from its own history.
    # Degradation = yield drops significantly below the model's own
    # baseline, OR falls below a hard floor (0.5) regardless of baseline.
    # "Significantly" = more than 0.25 below the rolling average.
    #
    # Cold start (< 3 history entries): use hard floor only.
    # This avoids penalising models during the first rounds before
    # a baseline exists, while still catching severe degradation.
    if raw_finding_markers >= 2:
        parse_yield = (findings_count + verdict_count) / raw_finding_markers
        # Record yield in ITC state for baseline computation.
        state = _itc_model_state.setdefault(model_label, {
            "history": [], "adaptation": None, "retry_count": 0,
            "escalation_level": 0,
        })
        yield_history = state.setdefault("parse_yield_history", [])
        yield_history.append(parse_yield)
        if len(yield_history) > 20:
            state["parse_yield_history"] = yield_history[-20:]
            yield_history = state["parse_yield_history"]

        # Hard floor: any model below 0.5 is degraded, no exceptions.
        _HARD_FLOOR = 0.5
        # Adaptive threshold: baseline minus deviation margin.
        _DEVIATION_MARGIN = 0.25

        if len(yield_history) >= 4:
            # Baseline = mean of the best 3 of last 5 yields (excludes
            # worst outliers while tracking recent performance).
            #
            # KNOWN TRADE-OFF: "best 3 of 5" is robust against single
            # bad rounds but blind to sustained gradual degradation.
            # At degradation rates below ~9% per round, the adaptive
            # threshold never fires before the hard floor — the filter
            # absorbs the decline by discarding the worst values, which
            # ARE the signal. At 9%+ per round, the adaptive threshold
            # catches the model 2-3 rounds before the floor would.
            #
            # The adaptive threshold detects sharp drops. The hard
            # floor (0.5) is the safety net for gradual decline.
            # Context overload — models fed more context than they
            # can handle — causes gradual decline, so the floor is
            # load-bearing in that scenario.
            #
            # Verified numerically, Exp 39 R3 confer (2026-04-11).
            recent = yield_history[-5:] if len(yield_history) >= 5 else yield_history[:]
            baseline = sum(sorted(recent, reverse=True)[:3]) / 3
            adaptive_threshold = max(_HARD_FLOOR, baseline - _DEVIATION_MARGIN)
        else:
            # Cold start: hard floor only.
            baseline = None
            adaptive_threshold = _HARD_FLOOR

        # Store threshold for the fingerprint quality gate (DRY:
        # avoids recomputing the same baseline/threshold there).
        state["last_adaptive_threshold"] = adaptive_threshold

        if parse_yield < adaptive_threshold:
            baseline_str = f"baseline={baseline:.2f}, " if baseline is not None else ""
            verdict_str = f", verdicts={verdict_count}" if verdict_count else ""
            _log(f"  ITC [{model_label}]: parse yield {parse_yield:.2f} "
                 f"({findings_count}+{verdict_count}/{raw_finding_markers} markers{verdict_str}, "
                 f"{baseline_str}threshold={adaptive_threshold:.2f}) — DEGRADATION")
            return ITC_DEGRADATION
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
    gamma_current: float = 1.0,
    gamma_converged_threshold: float = 0.10,
):
    """ITC (the "IT Crowd fix": restart-fresh on degradation, with
    fingerprint-informed scope) adaptation selection.

    A4 fix (Exp 40 1D.3): suppress the DEGRADATION restart when the
    per-model rho is healthy (still finding new things → low yield is
    not collapse).

    Exp 40 fix 1d (post-continuation 15 May 2026): two corrections.

    (i) γ-regime gate. The continuation reached deep convergence by
    γ-decay (terminal γ≈0.034) yet every panel member was flagged
    DEGRADATION because, in the converged regime, the panel naturally
    produces shorter, more verdict-heavy output (low parse yield). Low
    yield there is *convergence*, not *degradation*; an ITC restart
    would hand a fresh instance ground the panel has already settled,
    defeating the burst-reasoning rationale that motivates ITC.
    DEGRADATION is now also suppressed when γ is in the converged
    regime (γ < gamma_converged_threshold), independently of rho.

    (ii) Suppressed DEGRADATION must not feed the HIL underperformer
    flag. The A4 fix suppressed the restart *adaptation* but the
    DEGRADATION was still recorded as a `classification` in history
    *before* the suppression check, so `_itc_consecutive_failures`
    still counted it and `_itc_flag_underperformer` still fired the
    per-round HIL flag (continuation Anomaly 5 — all five models
    HIL-flagged every round despite no restart occurring). A
    suppressed round is now recorded with `classification=None` (and a
    separate `suppressed` marker for observability), so it neither
    feeds the consecutive-failure streak nor the HIL flag.
    """
    state = _itc_model_state.setdefault(model_label, {
        "history": [], "adaptation": None, "retry_count": 0,
        "escalation_level": 0,
    })

    # Decide DEGRADATION suppression BEFORE recording history so the
    # recorded classification reflects the suppression decision.
    suppressed = False
    suppress_reason = ""
    if classification == ITC_DEGRADATION:
        if rho_rolling_avg >= rho_threshold:
            suppressed = True
            suppress_reason = (
                f"rho_avg={rho_rolling_avg:.3f} >= {rho_threshold} "
                f"(normal depletion)"
            )
        elif gamma_current < gamma_converged_threshold:
            suppressed = True
            suppress_reason = (
                f"gamma={gamma_current:.3f} < "
                f"{gamma_converged_threshold} (converged regime — low "
                f"yield is convergence, not degradation; ITC restart "
                f"would defeat the burst-reasoning rationale)"
            )

    # Record history. A suppressed DEGRADATION is NOT a classification:
    # it must not feed _itc_consecutive_failures (line ~1457 counts
    # truthy 'classification') nor the HIL underperformer flag.
    state["history"].append({
        "round": round_idx,
        "classification": None if suppressed else classification,
        "suppressed": classification if suppressed else None,
        "findings": 0,
    })

    if suppressed:
        _log(f"  ITC [{model_label}]: {classification} suppressed — "
             f"{suppress_reason}")
        state["adaptation"] = None
        return

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
        # Reached only when NOT suppressed: rho unhealthy AND γ still
        # in the active regime — a genuine degradation signal.
        if consecutive < 2:
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
    # Fix C: use measured prompt size, not response size.
    # max_successful_context_chars was misnamed — it stored response length.
    # max_successful_prompt_chars stores actual prompt size sent to the model.
    # Fall back to the old field if prompt data hasn't accumulated yet.
    max_ok_chars = fp.get("max_successful_prompt_chars", 0)
    if max_ok_chars == 0:
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
    # Invalidate decomposition cache so next _should_decompose() call
    # sees the updated fingerprint data.
    _invalidate_fingerprint_cache()


def _update_observed_fingerprint(
    observed: Dict[str, Dict[str, Any]], model_label: str, round_idx: int,
    findings_count: int, response_chars: int,
    prompt_chars: int = 0,
    raw_finding_markers: int = 0,
    dispatch_error: Optional[str] = None,
):
    fp = observed.setdefault(model_label, {
        "max_successful_context_chars": 0, "max_failed_context_chars": 0,
        "max_successful_prompt_chars": 0, "max_failed_prompt_chars": 0,
        "prompt_chars_history": [],
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
            if prompt_chars > 0:
                fp["max_failed_prompt_chars"] = max(
                    fp.get("max_failed_prompt_chars", 0), prompt_chars)
            if "context_overflow" not in fp.get("failure_modes", []):
                fp.setdefault("failure_modes", []).append("context_overflow")
    elif response_chars > 0:
        fp["max_successful_context_chars"] = max(
            fp.get("max_successful_context_chars", 0), response_chars)
        if prompt_chars > 0:
            # Quality gate: compute FIRST, then apply to both
            # max_successful_prompt_chars AND history updates.
            # Exp 40 fix 1B.2: previously max_successful_prompt_chars was
            # updated unconditionally when response_chars > 0. That let
            # DeepSeek chunked-dispatch successes inflate the fingerprint
            # from the 0-char-chunk decomposition trap, causing
            # _should_decompose to re-decompose on subsequent monolithic
            # payloads of similar size. Now the update is gated on the
            # same parse-yield threshold as prompt_chars_history.
            quality_ok = True
            if raw_finding_markers >= 2:
                _py = findings_count / raw_finding_markers
                _state = _itc_model_state.get(model_label, {})
                _thresh = _state.get("last_adaptive_threshold", 0.5)
                if _py < _thresh:
                    quality_ok = False
            if quality_ok:
                fp["max_successful_prompt_chars"] = max(
                    fp.get("max_successful_prompt_chars", 0), prompt_chars)
            history = fp.setdefault("prompt_chars_history", [])
            if quality_ok:
                history.append(prompt_chars)
            # Cap history at 50 entries to bound memory.
            if len(history) > 50:
                fp["prompt_chars_history"] = history[-50:]


# Exp 40 fix 1E.5: per-model attention metrics computed from ITC +
# parse-yield history. These populate previously-null fingerprint fields
# so that burst_planner's D_decay quality gate has real data instead of
# the 0.0 default that was silently disabling it.
_PARSE_YIELD_HARD_FLOOR = 0.5


def _compute_attention_metrics(
    fp: Dict[str, Any],
    novelty_history: List[int],
    parse_yield_history: List[float],
) -> Dict[str, Any]:
    """Derive 6 attention metrics from observed fingerprint + ITC data.

    Writes directly into ``fp`` and returns it. All values are primitive
    numeric types (int / float / bool) so the fingerprint JSON stays
    round-trip safe. The 6 fields are:

    * ``measured_attention_span`` — largest prompt the model has handled
      with adequate quality (chars). Straight mirror of
      ``max_successful_prompt_chars``.
    * ``compression_threshold`` — smallest prompt size where the model
      has shown stress (either a dispatch failure or a parse-yield
      collapse). When no stress has been observed, the value equals
      ``max_successful_prompt_chars`` as an upper-bound proxy.
    * ``quality_at_capacity`` — mean of the three most recent parse
      yields. Proxy for quality at the current operating range.
    * ``decomposition_recommended`` — bool. True when the model has
      shown stress below the hard decomposition floor.
    * ``attention_ratio`` — ``max_successful / max_attempted``. 1.0 when
      no failures have been observed; < 1 once failures begin.
    * ``D_decay`` — Duane/geometric decay score from per-round novelty
      counts. Higher = steeper decay. 0.0 when decay cannot be measured
      (insufficient rounds or pure churn pattern).
    """
    from bench.decay_analysis import compute_d_score

    max_ok = int(fp.get("max_successful_prompt_chars", 0) or 0)
    max_fail = int(fp.get("max_failed_prompt_chars", 0) or 0)

    measured_attention_span = max_ok

    parse_yield_low = [y for y in parse_yield_history if y < _PARSE_YIELD_HARD_FLOOR]
    has_yield_stress = bool(parse_yield_low)

    if max_fail > 0:
        compression_threshold = max_fail
    elif has_yield_stress and max_ok > 0:
        compression_threshold = max_ok
    elif max_ok > 0:
        compression_threshold = max_ok
    else:
        compression_threshold = 0

    if parse_yield_history:
        recent = parse_yield_history[-3:]
        quality_at_capacity = sum(recent) / len(recent)
    else:
        quality_at_capacity = 1.0

    decomposition_recommended = False
    if max_fail > 0 and max_fail < DECOMPOSE_HARD_FLOOR_CHARS:
        decomposition_recommended = True
    if has_yield_stress and max_ok > 0 and max_ok < DECOMPOSE_HARD_FLOOR_CHARS:
        decomposition_recommended = True

    total_attempted = max(max_ok, max_fail)
    if total_attempted > 0:
        attention_ratio = max_ok / total_attempted
    else:
        attention_ratio = 1.0

    raw_d = compute_d_score(list(novelty_history)) if novelty_history else -1.0
    d_decay = 0.0 if raw_d < 0 else float(raw_d)

    fp["measured_attention_span"] = int(measured_attention_span)
    fp["compression_threshold"] = int(compression_threshold)
    fp["quality_at_capacity"] = round(float(quality_at_capacity), 4)
    fp["decomposition_recommended"] = bool(decomposition_recommended)
    fp["attention_ratio"] = round(float(attention_ratio), 4)
    fp["D_decay"] = round(float(d_decay), 4)
    return fp


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
    logs_dir: Path, enable_tools: bool = False,
) -> Optional[Tuple[str, float]]:
    # enable_tools (GATED, default OFF): forwarded to decomposed_dispatch so the
    # FINAL synthesis turn can give OpenAI-compatible / CLI models the
    # execute_python tool loop (runnable falsifiers). Per-chunk delivery turns
    # stay tool-less. Default OFF => byte-identical to the prior decomposed path.
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
            cdsfl_directives=cdsfl_text, enable_tools=enable_tools,
            # Forward the reasoning config (e.g. Gemini reasoning.effort) so the
            # decomposed Phase-1 chunk analysis gets adequate visible-content
            # budget. Without this the runner passed None and Gemini's Phase-1
            # emptied -> blind synthesis (2026-06-06 fix).
            extra_body=getattr(mc, "extra_body", None),
        )
        save_decomposed_result(result, logs_dir, mc.label, round_idx)
        return result.text, result.elapsed_s
    except Exception as e:
        _log(f"  {mc.label}: multi-turn FAILED — {type(e).__name__}: {e}")
        return None


# In-round re-ask (Exp 40 plan-B, 2026-05-16). Module-level config
# mirror set at experiment start from RunnerConfig (mirrors the
# _merge_arb_ctx pattern) so the dispatch-call chain need not be
# re-threaded. Safe default OFF until experiment start populates it.
_INROUND_REASK: Dict[str, Any] = {"enabled": False, "min_markers": 2}


def _build_inround_reask_prompt(original_prompt: str) -> str:
    """Prepend a STRUCTURE_VIOLATION corrective header to the original
    prompt (mirrors the 1e next-round wording for tone consistency,
    but acts in-round). The model is asked to re-emit the SAME analysis
    in the canonical finding format — no new analysis is requested."""
    header = (
        "=== STRUCTURE_VIOLATION — MANDATORY REFORMAT (in-round) ===\n\n"
        "Your previous response contained finding-style content but did "
        "NOT parse into a single valid finding. Unparseable output is "
        "treated as no output at all. Re-emit your SAME analysis now, "
        "in EXACTLY the canonical format — each finding declared as "
        "`FINDING_ID: <id>` with the required fields, no prose wrapper, "
        "no markdown fences around the finding block. Do not add new "
        "analysis; reformat what you already produced.\n\n"
        "=== ORIGINAL TASK (unchanged) ===\n\n"
    )
    return header + original_prompt


def _inround_reask(
    mc: ModelConfig, prompt: str, model_cdsfl: str, round_idx: int,
    text: str, model_findings: List[Finding], wall_limit: float,
) -> Tuple[List[Finding], str, bool]:
    """One bounded in-round re-dispatch on a structural parse failure.

    Trigger: enabled AND 0 findings parsed AND the raw text carried
    >= min_markers finding-declaration markers AND the text is a real
    model response (not a dispatch-failure sentinel). Returns
    (findings, text, did_reask). On a successful retry the retry's
    output REPLACES the round's output for this model (idempotent, no
    double-count); on failure the original is returned unchanged.
    """
    if not _INROUND_REASK.get("enabled"):
        return model_findings, text, False
    if model_findings:
        return model_findings, text, False
    if not text or text.startswith("__DISPATCH_FAILED__"):
        return model_findings, text, False
    markers = len(_FINDING_DECL_RE.findall(text))
    if markers < int(_INROUND_REASK.get("min_markers", 2)):
        return model_findings, text, False
    _log(f"  in-round re-ask [{mc.label}]: {markers} finding markers, "
         f"0 parsed — re-dispatching once (STRUCTURE_VIOLATION)")
    try:
        reask_prompt = _build_inround_reask_prompt(prompt)
        rtext, relapsed = dispatch_to_model(
            mc, reask_prompt, model_cdsfl, wall_clock_limit=wall_limit)
        _record_throughput(mc.label, len(reask_prompt), relapsed)
        rfindings = parse_findings(mc.label, round_idx, rtext)
    except (CircuitBreakerTripped, TimeoutError, Exception) as e:
        _log(f"  in-round re-ask [{mc.label}]: retry dispatch failed "
             f"({type(e).__name__}) — keeping original output")
        return model_findings, text, True
    if rfindings:
        _log(f"  in-round re-ask [{mc.label}]: RECOVERED "
             f"{len(rfindings)} findings on retry")
        return rfindings, rtext, True
    _log(f"  in-round re-ask [{mc.label}]: still 0 parsed after retry — "
         f"1e next-round reformat remains the fallback")
    return model_findings, text, True


# Apply-verified-fixes-back (Exp 40 plan-C, 2026-05-16). Module-level
# ctx set at experiment start (mirrors _merge_arb_ctx / _INROUND_REASK).
_APPLY_BACK_CTX: Dict[str, Any] = {}


def _apply_back_setup(cfg, target_path: "Path", logs_dir: "Path") -> "Path":
    """If enabled, create a per-run working copy of the target article
    (seeded from cfg.apply_fixes_back_seed if given, else the pristine
    target) and return its path so all rounds read the working copy.
    The repo file is never modified; the pristine original is recorded
    for provenance. Returns the original path when disabled."""
    _APPLY_BACK_CTX.clear()
    if not getattr(cfg, "apply_fixes_back_enabled", False):
        return target_path
    work_dir = logs_dir / "working"
    work_dir.mkdir(parents=True, exist_ok=True)
    working_path = work_dir / target_path.name
    seed = getattr(cfg, "apply_fixes_back_seed", "") or ""
    if seed:
        seed_path = Path(seed)
        if not seed_path.is_absolute():
            seed_path = REPO_ROOT / seed_path
        src_text = seed_path.read_text(encoding="utf-8")
        seed_desc = str(seed_path)
    else:
        src_text = target_path.read_text(encoding="utf-8")
        seed_desc = f"pristine {target_path}"
    working_path.write_text(src_text, encoding="utf-8")
    _APPLY_BACK_CTX.update({
        "enabled": True,
        "working_path": working_path,
        "pristine_path": target_path,
        "rel_target": _rel_to_repo(target_path),
        "cumulative_source": src_text,
        "test_cmd": getattr(cfg, "test_cmd", "") or "",
        "applied": [],   # canonical_ids promoted into the working copy
        "rejected": [],   # (canonical_id, reason) — gate/apply failures
    })
    _log(f"  apply-fixes-back ENABLED — working copy {working_path} "
         f"(seed: {seed_desc})")
    return working_path


def _rel_to_repo(p: "Path") -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def _apply_back_gate(candidate_source: str, rel_target: str,
                     test_cmd: str) -> Tuple[bool, str]:
    """Full canonical-suite gate: overlay candidate_source at rel_target
    in a sandbox repo copy and run test_cmd. Green-only promotion (the
    C0001 lesson: the run-time S_k score tolerates regressions)."""
    try:
        ast.parse(candidate_source)
    except (SyntaxError, ValueError) as e:
        return False, f"ast:{e}"
    if not test_cmd:
        return False, "no test_cmd configured (cannot gate)"
    with tempfile.TemporaryDirectory() as td:
        sb = Path(td) / "sb"
        shutil.copytree(
            REPO_ROOT, sb, symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "*.pyc", "logs"),
        )
        tgt = sb / rel_target
        tgt.parent.mkdir(parents=True, exist_ok=True)
        tgt.write_text(candidate_source, encoding="utf-8")
        try:
            r = subprocess.run(
                shlex.split(test_cmd), capture_output=True, text=True,
                cwd=str(sb), timeout=300,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
        except (subprocess.TimeoutExpired, Exception) as e:
            return False, f"gate_exec:{type(e).__name__}"
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip().splitlines()
            tail = next((ln for ln in reversed(out) if "failed" in ln),
                        out[-1] if out else "")
            return False, f"suite_fail:{tail[:120]}"
    return True, "ok"


def _apply_back_promote(registry, round_idx: int) -> Optional[str]:
    """Promote not-yet-applied CLOSED fixes into the working copy,
    cumulatively, each gated on the full canonical suite. Idempotent
    across rounds (tracks applied/rejected). Returns the new working
    source if anything was promoted this call, else None."""
    if not _APPLY_BACK_CTX.get("enabled"):
        return None
    applied = _APPLY_BACK_CTX["applied"]
    rejected_ids = {cid for cid, _ in _APPLY_BACK_CTX["rejected"]}
    seen = set(applied) | rejected_ids
    src = _APPLY_BACK_CTX["cumulative_source"]
    rel = _APPLY_BACK_CTX["rel_target"]
    test_cmd = _APPLY_BACK_CTX["test_cmd"]
    changed = False
    for cid, entry in sorted(registry.entries.items()):
        if cid in seen or entry.get("status") != "CLOSED":
            continue
        pf = entry.get("proposed_fix") or ""
        if not pf:
            continue
        blocks = parse_search_replace_blocks(pf)
        if not blocks:
            _APPLY_BACK_CTX["rejected"].append((cid, "no_parseable_block"))
            continue
        mod, n, err = apply_fix_blocks(src, blocks, str(rel))
        if mod is None:
            _APPLY_BACK_CTX["rejected"].append(
                (cid, f"apply:{err or 'failed'}"))
            continue
        ok, detail = _apply_back_gate(mod, rel, test_cmd)
        if not ok:
            _APPLY_BACK_CTX["rejected"].append((cid, detail))
            _log(f"  apply-back REJECT {cid}: {detail} "
                 f"(stays CLOSED in registry; not applied to artefact)")
            continue
        src = mod
        applied.append(cid)
        changed = True
        _log(f"  apply-back PROMOTE {cid} (round {round_idx}): "
             f"{n} block(s) applied + full suite green")
    if not changed:
        return None
    _APPLY_BACK_CTX["cumulative_source"] = src
    _APPLY_BACK_CTX["working_path"].write_text(src, encoding="utf-8")
    return src


def _dispatch_single_model(
    mc: ModelConfig, mgr: DynamicManager, prompt: str,
    cdsfl_text: str, full_code: str, round_idx: int,
    pattern_name: str, domain: str, logs_dir: Path,
    enable_tools: bool = False,
) -> Tuple[List[Finding], Optional[str]]:
    # enable_tools (GATED, default OFF): when the falsifier gate is on, the
    # primary dispatch gives OpenAI-compatible models the execute_python tool
    # loop so they can attach runnable falsifiers. Threaded in by the dispatch-
    # round callers from cfg.falsifier_gate_enabled (cfg is not in this scope).
    # Default OFF => byte-identical to vote-based behaviour.
    try:
        composed = _compose_for_model(mc.label, pattern_name, domain)
        model_cdsfl = composed.rendered_text
    except Exception:
        model_cdsfl = cdsfl_text
    # Append operational directive AFTER composer phenotype transforms.
    # The operational directive (R_k self-assessment, MUST-compute instruction)
    # is not subject to phenotype char caps — all models receive it in full.
    # (Mirrors run_exp37_evidence.py lines 2195-2196)
    if _OPERATIONAL_DIRECTIVE_TEXT:
        model_cdsfl += "\n\n" + _OPERATIONAL_DIRECTIVE_TEXT
    # I1 fix (gate-aware): when the falsifier gate is on, redefine §2 FALSIFICATION
    # from prose to a runnable falsifier (the 14-HIL fix). Gate-off => unchanged.
    if enable_tools:
        model_cdsfl = _gate_falsifier_directive(model_cdsfl)
    # Exp 52 factorial: directive-section selection. Applied LAST, to the fully
    # assembled prompt (composer phenotype + operational directive + any gate
    # rewrite), so it has the final say on what text reaches the model and so a
    # single call covers both the composed and the fallback branch above.
    # No-op unless a config switched a factor off — see RunnerConfig.
    model_cdsfl = _apply_directive_omission(model_cdsfl)

    pattern_text = INTERACTION_PATTERN_PRESETS[pattern_name][0]

    # Payload-aware decomposition (Exp 39 confound fix, 13 April 2026):
    # total payload = system prompt + user prompt (which already embeds full_code
    # via _build_prompt). Do NOT add full_code again — that double-counts ~64K.
    _total_payload_chars = len(model_cdsfl) + len(prompt)
    if should_decompose_v2(
        mc.label, mgr, payload_chars=_total_payload_chars,
    ):
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text,
            logs_dir, enable_tools=enable_tools)
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
        text, elapsed = dispatch_to_model(
            mc, prompt, model_cdsfl, wall_clock_limit=wall_limit,
            enable_tools=enable_tools)
        _record_throughput(mc.label, len(prompt), elapsed)
        model_findings = parse_findings(mc.label, round_idx, text)
        model_findings, text, _reasked = _inround_reask(
            mc, prompt, model_cdsfl, round_idx, text, model_findings,
            wall_limit)
        logs_dir.mkdir(parents=True, exist_ok=True)
        save_output(
            logs_dir, f"r{round_idx}", mc.label, prompt[:200] + "...", text,
            metadata={"round": round_idx, "elapsed": round(elapsed, 1),
                      "chars": len(text), "findings_count": len(model_findings),
                      "decomposed": False, "inround_reask": _reasked})
        return model_findings, text
    except (CircuitBreakerTripped, TimeoutError, Exception) as e:
        _log(f"  {mc.label}: {type(e).__name__} — {e}")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text, logs_dir)
        if fallback is not None:
            text, elapsed = fallback
            # Post-bypass-removal (commit 86470a5, 2026-05-20): decomposed
            # dispatch can return DecomposedResult.text="" when the
            # underlying model genuinely produces no usable content.
            # Treat that as primary-route failure and fall through to
            # the secondary route, not as a successful response.
            if text and text.strip():
                _record_throughput(mc.label, len(prompt), elapsed)
                model_findings = parse_findings(mc.label, round_idx, text)
                logs_dir.mkdir(parents=True, exist_ok=True)
                save_output(
                    logs_dir, f"r{round_idx}", mc.label, prompt[:200] + "...", text,
                    metadata={"round": round_idx, "elapsed": round(elapsed, 1),
                              "chars": len(text), "findings_count": len(model_findings),
                              "decomposed": True, "multiturn": True,
                              "route_used": "primary"})
                return model_findings, text
            _log(f"  {mc.label}: decomposed fallback returned empty content "
                 f"— escalating to secondary route")

        # Primary route (direct + decomposed) exhausted. Try secondary
        # if configured. (2026-05-22, founder-directed: "every model
        # has a secondary; no model misses a round" per
        # feedback_no_benching.md.)
        if mc.secondary_api and mc.secondary_model_id:
            import dataclasses as _dc
            secondary_mc = _dc.replace(
                mc,
                api=mc.secondary_api,
                model_id=mc.secondary_model_id,
                extra_body=None,
                secondary_api=None,
                secondary_model_id=None,
            )
            _log(f"  {mc.label}: SECONDARY ROUTE — primary "
                 f"{mc.api}/{mc.model_id} failed/empty; trying "
                 f"{mc.secondary_api}/{mc.secondary_model_id}")
            try:
                text2, elapsed2 = dispatch_to_model(
                    secondary_mc, prompt, model_cdsfl,
                    wall_clock_limit=wall_limit,
                )
                if text2 and text2.strip():
                    _record_throughput(mc.label, len(prompt), elapsed2)
                    model_findings = parse_findings(mc.label, round_idx, text2)
                    logs_dir.mkdir(parents=True, exist_ok=True)
                    save_output(
                        logs_dir, f"r{round_idx}", mc.label,
                        prompt[:200] + "...", text2,
                        metadata={"round": round_idx,
                                  "elapsed": round(elapsed2, 1),
                                  "chars": len(text2),
                                  "findings_count": len(model_findings),
                                  "route_used": "secondary",
                                  "primary_api": mc.api,
                                  "primary_model_id": mc.model_id,
                                  "secondary_api": mc.secondary_api,
                                  "secondary_model_id": mc.secondary_model_id})
                    _secondary_route_usage.append({
                        "round": round_idx, "model": mc.label,
                        "primary_api": mc.api,
                        "primary_model_id": mc.model_id,
                        "secondary_api": mc.secondary_api,
                        "secondary_model_id": mc.secondary_model_id,
                        "primary_error": f"{type(e).__name__}: {str(e)[:120]}",
                    })
                    return model_findings, text2
                _log(f"  {mc.label}: SECONDARY ROUTE also returned empty")
            except Exception as e2:
                _log(f"  {mc.label}: SECONDARY ROUTE failed — "
                     f"{type(e2).__name__}: {str(e2)[:120]}")

        # Both routes exhausted (or no secondary configured). Record an
        # HIL flag — the model did not produce content this round. The
        # model is NOT excluded from subsequent rounds; this is a per-
        # turn outcome, not benching. Persistent empties across rounds
        # raise the HIL signal at end-of-run review.
        _persistent_empty_flags.append({
            "round": round_idx, "model": mc.label,
            "primary_api": mc.api, "primary_model_id": mc.model_id,
            "primary_error": f"{type(e).__name__}: {str(e)[:120]}",
            "secondary_attempted": bool(mc.secondary_api),
            "secondary_api": mc.secondary_api,
            "secondary_model_id": mc.secondary_model_id,
        })
        return [], f"__DISPATCH_FAILED__:{type(e).__name__}: {e}"


def _dispatch_round_star(
    exp_config: ExperimentConfig, mgr: DynamicManager, brain: InsectBrain,
    base_prompt: str, registry_summary: str, cdsfl_text: str, full_code: str,
    round_idx: int, cfg: RunnerConfig,
    registry: Optional[FindingRegistry] = None,
    feedback_sections: Optional[Dict[str, str]] = None,
) -> Tuple[List[Finding], Dict[str, str], Dict[str, float]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    per_model_durations: Dict[str, float] = {}
    baseline = set(cfg.models)
    eligible = [mc for mc in exp_config.models
                if mc.label in baseline and mc.role != "collator"]

    # Feedback channel (cdsfl_operational.md §17): close the loop between
    # schema judgment and model behaviour by surfacing per-model flagged
    # findings from round K-1 at the top of round K's prompt. Models must
    # address these before resubmitting — hope-based compliance is over.
    feedback_sections = feedback_sections or {}

    def _make_prompt(mc_label: str) -> str:
        if round_idx == 0:
            return base_prompt
        adaptation = _itc_get_adaptation(mc_label)
        focus_prefix = ""
        if adaptation == "change_focus" and registry is not None:
            focus_prefix = _build_change_focus_instruction(registry, round_idx)
        feedback_prefix = feedback_sections.get(mc_label, "")
        if feedback_prefix:
            feedback_prefix = feedback_prefix + "\n"
        star_section = (
            f"{registry_summary}\n\n"
            f"This is Round {round_idx}. Review the registry above. "
            f"File new DISCOVERY findings. Issue VERDICT payloads on existing entries.\n"
        )
        combined = f"{feedback_prefix}{focus_prefix}{star_section}"
        if "=== ARTIFACT:" in base_prompt:
            return base_prompt.replace("=== ARTIFACT:", f"{combined}=== ARTIFACT:")
        return f"{base_prompt}\n\n{combined}"

    logs_dir = brain.logs_dir
    prompt_lengths: Dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        start_times: Dict[str, float] = {}
        for mc in eligible:
            prompt = _make_prompt(mc.label)
            prompt_lengths[mc.label] = len(prompt) + len(cdsfl_text)
            start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model, mc, mgr, prompt,
                cdsfl_text, full_code, round_idx, cfg.pattern, cfg.domain, logs_dir,
                getattr(cfg, "falsifier_gate_enabled", False),
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

    return findings, responses, per_model_durations, prompt_lengths


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
    prompt_lengths: Dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        start_times: Dict[str, float] = {}
        for mc in eligible:
            prompt = _make_prompt(mc.label)
            prompt_lengths[mc.label] = len(prompt) + len(cdsfl_text)
            start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model, mc, mgr, prompt,
                cdsfl_text, full_code, round_idx, cfg.pattern, cfg.domain, logs_dir,
                getattr(cfg, "falsifier_gate_enabled", False),
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

    return findings, responses, per_model_durations, prompt_lengths


# ─────────────────────────────────────────────────────────────────────────────
# Safety and telemetry helpers
# ─────────────────────────────────────────────────────────────────────────────

def _feedback_channel_enabled(cfg: "RunnerConfig") -> bool:
    """Read the feedback-channel switch from RunnerConfig.

    Defaults to True (feedback channel active) if the attribute is missing
    — the whole point of CDSFL is corrective feedback, so absence is
    interpreted as "run with defaults on". The config knob exists so that
    an experimenter can disable the channel for a controlled ablation
    without editing code.

    NOTE (2026-07-29): this reads the RAW switch only. To decide whether the
    feedback RUNNER PASS should run, use
    ``_directive_factor_state(cfg, "feedback")[1]`` — it also honours
    ``feedback_off_mode``, which can suppress the directive text while
    leaving the pass active (or vice versa). The run loop uses the latter.

    See `cdsfl_operational.md` §17 and `bench/dm/_feedback.py`.
    """
    return bool(getattr(cfg, "feedback_channel_enabled", True))


def _build_feedback_for_next_round(
    *,
    round_idx: int,
    findings: List[Finding],
    responses: Dict[str, str],
    immune_result,
    rk_validation: Dict[str, List[Tuple[str, str, str, str]]],
    cfg: "RunnerConfig",
) -> Dict[str, str]:
    """Assemble per-model feedback sections from round-K schema outputs.

    Called at the end of round K. Output is consumed at the top of round
    K+1's prompt. On any exception, returns an empty dict — feedback
    assembly is never allowed to crash the main loop.
    """
    try:
        # Extract duplicate pairs from TriagedFinding — NK Cell populates
        # `is_duplicate=True, duplicate_of=<id>, similarity=<float>` and the
        # triaged list is on the ImmuneResponse.
        duplicate_pairs: List[Tuple[str, str, float]] = []
        for triaged in getattr(immune_result, "triaged", []):
            if getattr(triaged, "is_duplicate", False) and triaged.duplicate_of:
                duplicate_pairs.append(
                    (triaged.finding.finding_id,
                     triaged.duplicate_of,
                     float(getattr(triaged, "similarity", 0.0))),
                )

        # Parse admissibility blocks from each model's raw response. The
        # parser is permissive (see bench/dm/_feedback.py) — missing blocks
        # generate a full-fail list (all 5 gates flagged), so models that
        # haven't yet adopted the §15 format get a clear pointer.
        admissibility_failures: Dict[str, List[str]] = {}
        for f in findings:
            model_text = responses.get(f.model_id, "")
            # Attempt to extract the specific finding's section before parsing
            # — findings are typically separated by "FINDING" markers.
            failed = parse_admissibility_block(_extract_finding_section(model_text, f.finding_id))
            if failed:
                admissibility_failures[f.finding_id] = failed

        records = build_feedback_records(
            round_idx=round_idx,
            findings=findings,
            immune_result=immune_result,
            rk_validation=rk_validation,
            duplicate_pairs=duplicate_pairs,
            admissibility_failures=admissibility_failures,
        )

        top_k = getattr(cfg, "feedback_top_k", 10)
        max_chars = getattr(cfg, "feedback_max_chars_per_model", 8000)
        return build_feedback_sections(
            records,
            round_idx=round_idx,
            top_k=top_k,
            max_chars_per_model=max_chars,
        )
    except Exception as exc:
        # Defensive: the feedback channel must never break the pipeline.
        # If something goes wrong (e.g. a novel immune_result shape), we log
        # once and continue with empty feedback. Next round runs without it.
        _log(f"  [feedback] build failed: {type(exc).__name__}: {exc}")
        return {}


def _extract_finding_section(full_text: str, finding_id: str) -> str:
    """Extract the text of a specific finding from a model's raw response.

    Returns the substring from the finding_id marker up to the next finding
    marker (or end of text). If the finding_id can't be located, returns
    the full text so the parser still has something to work with.

    Heuristic — models use varied phrasing ("FINDING f1", "Finding f1:",
    "f1:", etc.). We look for the id in several common formats.
    """
    if not full_text or not finding_id:
        return full_text
    import re
    # Case-insensitive, tolerant of punctuation around the id
    pattern = re.compile(
        rf"(?:FINDING\s+)?{re.escape(finding_id)}\b",
        re.IGNORECASE,
    )
    match = pattern.search(full_text)
    if not match:
        return full_text
    tail = full_text[match.start():]
    # Find the start of the next FINDING or similar terminator
    next_match = re.search(
        r"(?:^|\n)\s*(?:FINDING\s+\S+|---\s*FINDING|=+\s*FINDING)",
        tail[match.end() - match.start():],
        re.IGNORECASE | re.MULTILINE,
    )
    if next_match:
        return tail[: match.end() - match.start() + next_match.start()]
    return tail


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


# ─────────────────────────────────────────────────────────────────────────────
# Shadow cell runner (Macrophage + Ouroboros) — Exp 39
# ─────────────────────────────────────────────────────────────────────────────

# Persistent shadow cell instances (survive across rounds)
_shadow_macrophage = None
_shadow_ouroboros = None
_shadow_stage6_calibrator = None


def _run_shadow_cells(
    round_idx: int,
    immune_result: Any,
    findings: List[Finding],
    exp_config: Any,
    logs_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Run Macrophage and Ouroboros shadow cells after a round.

    SHADOW MODE ONLY: zero effect on the load-bearing verdict path.
    Both cells observe and log but never modify pipeline state.

    Args:
        round_idx: Current round index.
        immune_result: ImmuneResponse from run_immune_pipeline.
        findings: Findings from the current round.
        exp_config: Experiment config (checked for _macrophage/_ouroboros sections).
        logs_dir: Directory for shadow cell logs.

    Returns:
        Dict with shadow cell metrics for round reporting.
    """
    global _shadow_macrophage, _shadow_ouroboros, _shadow_stage6_calibrator

    config = exp_config if isinstance(exp_config, dict) else {}

    has_macrophage = "_macrophage" in config
    has_ouroboros = "_ouroboros" in config

    if not has_macrophage and not has_ouroboros:
        return {}

    shadow_data: Dict[str, Any] = {}

    # ── Macrophage: internal pipeline monitor ──
    if has_macrophage:
        try:
            from bench.macrophage_cell import MacrophageCell, MacrophageMode

            if _shadow_macrophage is None:
                _shadow_macrophage = MacrophageCell(
                    mode=MacrophageMode.PATROL, shadow=True,
                )

            # Extract verdicts from immune result. Exp 40 fix 1B.1:
            # previously the Macrophage saw 0 verdicts across all 6 rounds
            # of Exp 39-0 despite the pipeline producing 16+ per round.
            # Now two-path: primary = cell_verdicts dict (per-finding lists);
            # fallback = synthesise lightweight verdict-like objects from
            # final_verdicts when cell_verdicts is absent or empty, so the
            # Macrophage's cluster/severity/timing checks can still fire.
            all_verdicts: List[Any] = []
            cv_attr = hasattr(immune_result, "cell_verdicts")
            if cv_attr:
                for vid_list in immune_result.cell_verdicts.values():
                    all_verdicts.extend(vid_list)

            if not all_verdicts:
                # Fallback: synthesise from final_verdicts (Dict[str, str]).
                fv = getattr(immune_result, "final_verdicts", None)
                if fv:
                    from types import SimpleNamespace
                    for fid, verdict_str in fv.items():
                        # Mimic CellVerdict-like interface: .verdict, .confidence,
                        # .finding_id, .tool_used, .cell_type — Macrophage only
                        # reads .verdict and .confidence in _patrol_observe.
                        conf = 0.5
                        fc = getattr(immune_result, "final_confidences", None)
                        if fc and fid in fc:
                            conf = float(fc[fid])
                        all_verdicts.append(SimpleNamespace(
                            finding_id=fid,
                            verdict=verdict_str,
                            confidence=conf,
                            tool_used="synthesised_from_final_verdicts",
                            cell_type="synthesised",
                        ))

            if not all_verdicts:
                cv_keys = (
                    len(immune_result.cell_verdicts) if cv_attr else 0
                )
                per_fid_counts = (
                    {k: len(v) for k, v in immune_result.cell_verdicts.items()}
                    if cv_attr else {}
                )
                fv_attr = hasattr(immune_result, "final_verdicts")
                fv_keys = (
                    len(immune_result.final_verdicts) if fv_attr else 0
                )
                _log(
                    f"  Macrophage: 0 verdicts after both primary and "
                    f"fallback paths "
                    f"(cell_verdicts={'present' if cv_attr else 'missing'}, "
                    f"keys={cv_keys}, per_fid={per_fid_counts}, "
                    f"final_verdicts={'present' if fv_attr else 'missing'}, "
                    f"fv_keys={fv_keys}, "
                    f"type={type(immune_result).__name__})"
                )

            triaged = getattr(immune_result, "triaged", None)
            timings = getattr(immune_result, "stage_timings", None)

            # Extract provenance metadata from external-origin findings
            provenance = []
            for f in findings:
                if getattr(f, "origin_type", "") and f.origin_type != "model":
                    provenance.append({
                        "origin_type": f.origin_type,
                        "source_ref": getattr(f, "source_ref", ""),
                        "retrieval_query": getattr(f, "retrieval_query", ""),
                        "retrieved_at": getattr(f, "retrieved_at", ""),
                        "source_hash": getattr(f, "source_hash", ""),
                        "source_diversity": getattr(f, "source_diversity", 0.0),
                    })

            # Derive PE gate pass/fail statistics from immune verdicts
            gate_stats = None
            final_v = getattr(immune_result, "final_verdicts", None)
            if final_v:
                passed = sum(1 for v in final_v.values() if v in ("CONFIRMED", "UNCERTAIN", "UNSCORED"))
                failed = sum(1 for v in final_v.values() if v == "REJECTED")
                # Shadow-audit repair (2026-07-27): DUPLICATE = redundancy, not an
                # invalid finding — counting it as a gate failure masked the
                # macrophage's immune-deficiency check. Tracked separately:
                duplicates = sum(1 for v in final_v.values() if v == "DUPLICATE")
                by_origin: Dict[str, Dict[str, int]] = {}
                for f in findings:
                    ot = getattr(f, "origin_type", "model") or "model"
                    fid = f.finding_id
                    bucket = by_origin.setdefault(ot, {"passed": 0, "failed": 0})
                    v = final_v.get(fid, "UNCERTAIN")
                    if v in ("REJECTED", "DUPLICATE"):
                        bucket["failed"] += 1
                    else:
                        bucket["passed"] += 1
                gate_stats = {
                    "total_passed": passed,
                    "total_failed": failed,
                    "by_origin": by_origin,
                }

            # Ouroboros activity metrics from prior rounds (if available)
            ouroboros_metrics = None
            if _shadow_ouroboros is not None and hasattr(_shadow_ouroboros, "get_activity_metrics"):
                ouroboros_metrics = _shadow_ouroboros.get_activity_metrics()

            macro_summary = _shadow_macrophage.observe(
                verdicts=all_verdicts,
                triaged=triaged,
                timings=timings,
                provenance=provenance or None,
                gate_stats=gate_stats,
                ouroboros_metrics=ouroboros_metrics,
            )

            # Codex 5.3 confer fix (13 April 2026): Macrophage was counts-only
            # while Ouroboros wrote full per-round replay logs.  Now both
            # shadow cells produce equally inspectable output.
            shadow_data["macrophage"] = {
                "observations": len(macro_summary.observations),
                "anomalies": macro_summary.anomaly_count,
                "pipeline_modified": macro_summary.pipeline_modified,
                "mode": macro_summary.mode.value,
                "verdicts_received": len(all_verdicts),
                "observation_details": [
                    obs.to_dict() for obs in macro_summary.observations
                ],
            }

            # Write Macrophage shadow replay log to disk (parity with Ouroboros)
            if logs_dir:
                macro_log_path = logs_dir / f"macrophage_shadow_r{round_idx:02d}.json"
                macro_log_path.write_text(
                    json.dumps({
                        "round_idx": round_idx,
                        "mode": macro_summary.mode.value,
                        "anomaly_count": macro_summary.anomaly_count,
                        "pipeline_modified": macro_summary.pipeline_modified,
                        "verdicts_received": len(all_verdicts),
                        "observations": [
                            obs.to_dict() for obs in macro_summary.observations
                        ],
                    }, indent=2, default=str) + "\n",
                    encoding="utf-8",
                )

        except Exception as exc:
            import logging
            logging.getLogger("cdsfl.shadow_cells").warning(
                "Macrophage shadow cell failed (non-fatal): %s", exc,
            )
            shadow_data["macrophage"] = {"error": str(exc)}

    # ── Ouroboros: external research (between-round) ──
    if has_ouroboros:
        try:
            from bench.ouroboros_cell import OuroborosCell

            if _shadow_ouroboros is None:
                ouroboros_config = config.get("_ouroboros", {})
                allowed = ouroboros_config.get("api_access", ["arxiv", "semantic_scholar"])
                _shadow_ouroboros = OuroborosCell(
                    shadow=True,
                    allowed_sources=allowed if isinstance(allowed, list) else [allowed],
                    # New key (2026-07-31). Default "haiku" is the constructor
                    # default the cell has always used, so configs that do not
                    # set it behave exactly as before. "none" selects the
                    # deterministic extractive brief and spends nothing —
                    # which is what CI and the proof harness use.
                    reader_backend=str(
                        ouroboros_config.get("reader_backend", "haiku")),
                )

            # Collect Macrophage anomalies as research targets
            anomaly_descriptions = []
            if "macrophage" in shadow_data and _shadow_macrophage is not None:
                macro_summary_ref = _shadow_macrophage._round_history
                if macro_summary_ref:
                    last = macro_summary_ref[-1]
                    if last.get("anomaly_count", 0) > 0:
                        anomaly_descriptions.append(
                            f"round_{round_idx}_anomalies:{last['anomaly_count']}"
                        )

            shadow_log = _shadow_ouroboros.run_between_rounds(
                round_idx=round_idx,
                anomalies=anomaly_descriptions,
                immune_response=immune_result,
                round_findings=findings,
            )

            shadow_data["ouroboros"] = {
                "anomalies_observed": len(shadow_log.anomalies_observed),
                "queries_issued": len(shadow_log.queries_issued),
                "candidate_claims": len(shadow_log.candidate_claims),
                "would_have_injected": shadow_log.would_have_injected,
            }

            # ── Loop-close (2026-07-31): render the brief for the NEXT round's
            # prompt. OFF unless the experiment's _ouroboros block says
            # inject_brief: true, so the five archival configs that already
            # carry an _ouroboros block (Exp 45–49) stay byte-identical.
            _oc = config.get("_ouroboros", {}) or {}
            if _oc.get("inject_brief"):
                from bench.ouroboros_cell import build_brief_prompt_section
                _section = build_brief_prompt_section(
                    shadow_log.briefs,
                    round_idx=round_idx,
                    max_chars=int(_oc.get("brief_max_chars", 4000)),
                    min_relevance=str(_oc.get("brief_min_relevance", "LOW")),
                    require_model_reader=bool(
                        _oc.get("require_model_reader", True)),
                )
                shadow_data.setdefault("_ouroboros_wiring", {})
                shadow_data["_ouroboros_wiring"]["brief_section"] = _section
                shadow_data["ouroboros"]["brief_section_chars"] = len(_section)
                shadow_data["ouroboros"]["briefs_rendered"] = sum(
                    1 for b in (shadow_log.briefs or [])
                    if (b.get("relevance") or "").upper() not in ("", "NONE")
                )

            # Write shadow replay log to disk
            if logs_dir:
                shadow_log_path = logs_dir / f"ouroboros_shadow_r{round_idx:02d}.json"
                shadow_log_path.write_text(
                    json.dumps(shadow_log.to_dict(), indent=2, default=str) + "\n",
                    encoding="utf-8",
                )

        except Exception as exc:
            import logging
            logging.getLogger("cdsfl.shadow_cells").warning(
                "Ouroboros shadow cell failed (non-fatal): %s", exc,
            )
            shadow_data["ouroboros"] = {"error": str(exc)}

    # ── Stage 6 calibrator: shadow (ν_k, c_ext) data collection ──
    # Runs whenever any shadow cell is active. Collects per-finding
    # novelty triples and per-tool FPR tracking for post-experiment
    # calibration. Zero pipeline effect.
    try:
        from bench.dm._shadow_stage6 import ShadowStage6Calibrator

        if _shadow_stage6_calibrator is None:
            _shadow_stage6_calibrator = ShadowStage6Calibrator()

        # Collect ouroboros data if available (for c_ext and nu_k estimation)
        ouroboros_shadow_data = None
        if "ouroboros" in shadow_data and _shadow_ouroboros is not None:
            # Get the full shadow log from the last run
            if hasattr(_shadow_ouroboros, "_last_shadow_log"):
                last_log = _shadow_ouroboros._last_shadow_log
                if last_log is not None:
                    ouroboros_shadow_data = last_log.to_dict()

        round_log = _shadow_stage6_calibrator.observe_round(
            round_idx=round_idx,
            findings=findings,
            immune_response=immune_result,
            ouroboros_data=ouroboros_shadow_data,
        )

        shadow_data["stage6_calibration"] = {
            "findings_assessed": len(round_log.findings),
            "mean_nu_k_proxy": round_log.mean_nu_k_proxy,
            "mean_c_ext": round_log.mean_c_ext,
            "mean_delta": round_log.mean_delta,
        }

        # ── Loop-close (2026-07-31): hand the calibrator's (c_ext, nu_k) to the
        # R_k channel. The calibrator has computed these from real retrieval
        # since 14 April; nothing consumed them, so the S_k path passed
        # c_ext=0.0 literal. Consumption is OFF unless the experiment's
        # _ouroboros block says c_ext_enabled: true.
        #
        # c_ext is a property of the SEARCH, not of a finding — the calibrator's
        # noisy-OR over per-source coverage is identical for every finding in a
        # round — so one round-level value is exact, not an average. nu_k IS
        # per-finding, so it is carried per finding_id with the round mean as
        # the fallback for entries whose alias is not in this round.
        _oc6 = (config.get("_ouroboros", {}) or {})
        if _oc6.get("c_ext_enabled") and round_log.findings:
            _c_ext_vals = {round(f.c_ext, 6) for f in round_log.findings}
            # Taking findings[0] is only exact while that set is a singleton.
            # If a future calibration made c_ext per-finding, silently keeping
            # the first finding's value would apply one finding's search
            # coverage to every other finding's risk. Fall back to the mean and
            # say so, rather than be quietly wrong.
            if len(_c_ext_vals) == 1:
                _c_ext = round_log.findings[0].c_ext
            else:
                _c_ext = round_log.mean_c_ext
                _log(f"  [ouroboros] WARNING: c_ext is no longer uniform "
                     f"across findings ({sorted(_c_ext_vals)[:4]}); using the "
                     f"round mean {_c_ext:.4f}. The per-finding join in "
                     f"_evaluate_sk_for_findings covers nu_k only.")
            _w = shadow_data.setdefault("_ouroboros_wiring", {})
            _w["c_ext"] = float(_c_ext)
            _w["c_ext_uniform"] = (len(_c_ext_vals) == 1)
            _w["nu_k_by_finding"] = {
                f.finding_id: float(f.nu_k_proxy) for f in round_log.findings
            }
            _w["nu_k_mean"] = float(round_log.mean_nu_k_proxy)
            _w["search_status"] = round_log.findings[0].search_status
            shadow_data["stage6_calibration"]["c_ext_consumed"] = float(_c_ext)

        # Write calibration log to disk
        if logs_dir:
            cal_path = logs_dir / f"stage6_calibration_r{round_idx:02d}.json"
            cal_path.write_text(
                json.dumps(round_log.to_dict(), indent=2, default=str) + "\n",
                encoding="utf-8",
            )

            # Also write cumulative summary
            summary_path = logs_dir / "stage6_calibration_summary.json"
            summary_path.write_text(
                json.dumps(
                    _shadow_stage6_calibrator.get_calibration_summary(),
                    indent=2, default=str,
                ) + "\n",
                encoding="utf-8",
            )

    except Exception as exc:
        import logging
        logging.getLogger("cdsfl.shadow_cells").warning(
            "Stage 6 calibrator failed (non-fatal): %s", exc,
        )
        shadow_data["stage6_calibration"] = {"error": str(exc)}

    return shadow_data


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
# S_k Solution Verification Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def _looks_like_fix_path(s: str) -> bool:
    """True if `s` looks like a file path rather than a line of code. A path has
    no whitespace AND either contains a directory separator or ends in a known
    source extension. Used to detect when a model omitted the file path on a
    '<<<< SEARCH' line (single-target review) and put code there instead."""
    s = s.strip()
    if not s or any(c.isspace() for c in s):
        return False
    if "/" in s or "\\" in s:
        return True
    return bool(re.search(
        r"\.(py|md|json|toml|txt|ya?ml|cfg|ini|js|ts|c|h|cpp|rs|go|java)$",
        s, re.IGNORECASE))


def parse_search_replace_blocks(text: str) -> List[FixBlock]:
    """Parse <<<< SEARCH file_path ... ==== ... >>>> REPLACE blocks.

    Uses a line-oriented state machine instead of regex so that delimiter-
    like content inside payloads (e.g. literal '====' lines) does not
    break parsing.

    P1 fix (Exp 38): falls back to markdown code block extraction when
    no <<<< SEARCH blocks found but ```python blocks with before/after
    structure are present.

    Returns list of FixBlock. Empty list if no valid blocks found.
    """
    blocks: List[FixBlock] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # Look for block start: <<<< SEARCH <filepath>
        if line.strip().startswith("<<<<") and "SEARCH" in line.upper():
            rest = line.strip()[4:].strip()
            # Remove the SEARCH keyword whether or not text follows on the line.
            rest = re.sub(r'^SEARCH\b[ \t]*', '', rest, flags=re.IGNORECASE).strip()
            # 2026-06-06: 'rest' is the file path ONLY if it looks like one. Some
            # models omit the path on a single-target review and put the first
            # search line right after SEARCH (e.g. "<<<< SEARCH _HARD_BLOCK = ("),
            # which the old parser grabbed as the path -> false no_blocks_for_target
            # AND a corrupted (first-line-missing) search. Treat a non-path 'rest'
            # as the first search line and leave the path empty; apply_fix_blocks
            # then defaults a path-less block to the single target.
            _prefix_search = None
            if rest and _looks_like_fix_path(rest):
                file_path = rest
            else:
                file_path = ""
                if rest:
                    _prefix_search = rest
            i += 1
            # Collect search lines until ==== separator (with or without trailing text).
            # The parser in runner_core stores "==== REPLACE" while the prompt
            # specifies bare "====".  Accept both.  (Exp 39-0 confound fix.)
            search_lines: List[str] = []
            if _prefix_search is not None:
                search_lines.append(_prefix_search)
            while i < len(lines):
                stripped = lines[i].rstrip()
                if stripped == "====" or stripped.startswith("==== "):
                    i += 1
                    break
                search_lines.append(lines[i])
                i += 1
            else:
                # Reached end without finding separator — skip this block
                continue
            # Collect replace lines until >>>> closer (with or without REPLACE).
            # Accept bare ">>>>" AND ">>>> REPLACE".  (Exp 39-0 confound fix.)
            replace_lines: List[str] = []
            while i < len(lines):
                if lines[i].strip().startswith(">>>>"):
                    i += 1
                    break
                replace_lines.append(lines[i])
                i += 1
            else:
                continue
            search = "\n".join(search_lines)
            replace = "\n".join(replace_lines)
            # Path-less blocks (file_path == "") are kept: apply_fix_blocks defaults
            # them to the single target. Only an empty search is rejected.
            if search:
                blocks.append(FixBlock(
                    file_path=file_path, search=search, replace=replace,
                ))
        else:
            i += 1

    # P1 fallback: extract from markdown code blocks with file path comments.
    # Models sometimes use ```python\n# file: path/to/file.py\n... instead of
    # <<<< SEARCH blocks. Look for paired "before"/"after" or "current"/"fixed"
    # code blocks.
    #
    # SHADOW MODE (Exp 39): log what the fallback would extract but do not
    # return the blocks. This gives empirical data on firing rate and
    # precision without confounding the Exp 39 fix validation.
    if not blocks:
        _MD_BLOCK_RE = re.compile(
            r'```\w*\n(?:#\s*(?:file|path|target):\s*([^\n]+)\n)?'
            r'(.*?)\n```',
            re.DOTALL
        )
        md_blocks = list(_MD_BLOCK_RE.finditer(text))
        if len(md_blocks) >= 2:
            shadow_blocks: List[FixBlock] = []
            for j in range(len(md_blocks) - 1):
                b1, b2 = md_blocks[j], md_blocks[j + 1]
                between = text[b1.end():b2.start()].lower()
                if any(kw in between for kw in ("after", "replace", "fixed", "corrected", "new")):
                    fp = b1.group(1) or b2.group(1) or ""
                    search = b1.group(2).strip()
                    replace_text = b2.group(2).strip()
                    if fp and search:
                        shadow_blocks.append(FixBlock(
                            file_path=fp.strip(),
                            search=search,
                            replace=replace_text,
                        ))
            if shadow_blocks:
                _log(f"  P1 SHADOW: fallback parser found {len(shadow_blocks)} "
                     f"block(s) from markdown — NOT applied. "
                     f"Files: {[b.file_path for b in shadow_blocks]}, "
                     f"search_lens: {[len(b.search) for b in shadow_blocks]}")
    return blocks


def apply_fix_blocks(
    source: str, blocks: List[FixBlock], target_path: str,
) -> Tuple[Optional[str], int, Optional[str]]:
    """Apply fix blocks to source.

    Returns (modified_source, blocks_applied, error_reason).

    Only applies blocks whose file_path matches target_path (by basename or
    full path). Returns modified_source=None on pre-gate failure with a
    machine-readable error_reason.
    """
    modified = source
    applied = 0
    matched = 0
    for block in blocks:
        # A path-less block (model omitted the path on a single-target review)
        # defaults to the target; an explicit path must match (full or basename).
        bp = (block.file_path or "").strip()
        if bp and not (bp == target_path or
                       Path(bp).name == Path(target_path).name):
            continue
        matched += 1
        if block.search not in modified:
            _log(f"  S_k: SEARCH block not found in source "
                 f"(first 60 chars: {block.search[:60]!r})")
            return None, 0, "search_not_found"
        occurrences = modified.count(block.search)
        if occurrences > 1:
            _log(f"  S_k: SEARCH block is ambiguous ({occurrences} "
                 f"occurrences, first 60 chars: {block.search[:60]!r})")
            return None, 0, "search_ambiguous"
        modified = modified.replace(block.search, block.replace, 1)
        applied += 1

    if matched == 0:
        return None, 0, "no_blocks_for_target"

    return modified, applied, None



_MD_PY_FENCE = re.compile(r"```(?:python|py)\n(.*?)```", re.S)


def _gateable_source(modified_source: str, source_path: str) -> Tuple[Optional[str], str]:
    """The Python the syntax gates should actually check, for any target type.

    THE DEFECT THIS FIXES. g1 (ast.parse) and g2 (py_compile) were handed the
    WHOLE modified target. For a Python module that is right. For the zero-plant
    control — a markdown design reference — ast.parse chokes on the prose
    ("leading zeros in decimal integer literals are not permitted", from a table
    of offsets) and returns 0. Since A = g1 * g2, EVERY proposed fix scored
    A=0.0 and was REJECTED. Fifty rejections on the 2026-08-01 run. No fix could
    be admitted, so no finding could be resolved, so the irreducible queue filled
    with criticals the machinery was structurally unable to close, and the run
    could not converge. This is the dominant cause of that halt; the
    close-the-loop failure found the same hour was the smaller half of it.

    Returns (source_to_gate, reason). A None source means the gates cannot speak
    to this target and the caller should not treat their silence as a failure.
    """
    if source_path.endswith(".py") or not source_path:
        return modified_source, "python target"
    blocks = _MD_PY_FENCE.findall(modified_source)
    if not blocks:
        # Nothing to break, so nothing for a syntax gate to say. The falsifier
        # and HIL carry a pure-prose finding; see bugzilla_loop.run_verification,
        # which refuses such a target rather than passing it silently.
        return None, "target carries no code; syntax gates not applicable"
    return "\n\n".join(b.rstrip() for b in blocks) + "\n", (
        f"gating {len(blocks)} fenced listing(s) extracted from a non-Python target")


def _run_hard_gate_ast(modified_source: str, source_path: str = "") -> Tuple[int, str]:
    """g1: AST parse of the target's CODE. Returns (score, detail)."""
    src, why = _gateable_source(modified_source, source_path)
    if src is None:
        return 1, f"AST parse not applicable ({why})"
    try:
        ast.parse(src)
        return 1, f"AST parse succeeded ({why})"
    except (SyntaxError, ValueError) as e:
        return 0, f"ParseError: {e} ({why})"


_SURROGATE_RE = re.compile(r"[\ud800-\udfff]")


def _write_report_json(path: Path, payload: Any) -> None:
    """Write a run report as UTF-8. A completed run must never fail to record itself.

    Text harvested from a PDF can carry a LONE SURROGATE — the unpaired half of a
    codepoint that survived extraction on its own. U+D835 is the common one, the
    high half of the mathematical-alphanumeric block, so it turns up in exactly
    the papers the retrieval cell fetches. Python holds such a string quite
    happily and then refuses to encode it, so the write raises UnicodeEncodeError
    AFTER the experiment has finished: hours of paid dispatch complete, and the
    report is never written. Found 2026-07-31 while wiring the retrieval cell's
    brief into the prompt; the brief reaches the report, so the character does too.

    The ordinary path is byte-identical to a plain strict write. Substitution
    fires only when the strict encode fails, and it announces itself in the log
    AND inside the report, because a silently scrubbed report is a corrupted
    record that reads as a clean one.
    """
    text = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        n = len(_SURROGATE_RE.findall(text))
        if isinstance(payload, dict):
            payload = {**payload, "_text_sanitised": {
                "unpaired_surrogates_replaced": n,
                "note": "Unpaired surrogate characters — typically from PDF text "
                        "extraction — were replaced with U+FFFD so this report "
                        "could be written. Affected strings are degraded; every "
                        "other value is unchanged. See _write_report_json.",
            }}
            text = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
        text = _SURROGATE_RE.sub("�", text)
        _log(f"  *** WARNING: {n} unpaired surrogate(s) replaced with U+FFFD to "
             f"write {path.name} — affected text is degraded ***")
    path.write_text(text, encoding="utf-8")


def _anchor_dir_for(source_path: str) -> Optional[str]:
    """Directory to place a scratch file in for ruff/bandit/compile checks.

    Anchoring beside the source lets those tools discover the project's config by
    walking upwards, which is right for a PYTHON target inside this repository.

    It is wrong for an exam target. Those are markdown, staged read-only in a
    directory deliberately set to refuse new files so a panel cannot drop anything
    beside the document it is reviewing. Writing a scratch .py there fails with
    EPERM — which is exactly what happened on the first launch of the zero-plant
    control, one second in. Both controls were correct; anchoring was simply the
    wrong default for a target that is not code we own.

    Returns None (system temp) unless the target is a writable .py path. There were
    four call sites with this logic inlined; a fifth would have been a matter of
    time, so it lives here now.
    """
    if not source_path:
        return None
    parent = Path(source_path).parent
    if source_path.endswith(".py") and os.access(parent, os.W_OK):
        return str(parent)
    return None


def _run_hard_gate_compile(modified_source: str, source_path: str) -> Tuple[int, str]:
    """g2: py_compile of the target's CODE. Returns (score, detail)."""
    modified_source, why = _gateable_source(modified_source, source_path)
    if modified_source is None:
        return 1, f"py_compile not applicable ({why})"
    # Anchor to source directory for context parity with ruff/bandit gates
    anchor_dir = _anchor_dir_for(source_path)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(modified_source)
        tmp_path = tmp.name
    try:
        py_compile.compile(tmp_path, doraise=True)
        return 1, "py_compile succeeded"
    except py_compile.PyCompileError as e:
        return 0, f"CompileError: {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass


def _run_effect_regression(
    modified_source: str, source_path: str, test_cmd: Optional[str] = None,
) -> Tuple[Optional[float], str]:
    """e2: Regression suite — run existing tests against modified source.

    Returns (score in [0,1] or None if unavailable, detail). Copies the
    entire repo into a sandbox, overlays the modified source, and runs
    tests there so that pytest evaluates the actual proposed fix, not
    the original.
    """
    if not test_cmd:
        return None, "no test command configured"
    target_path = Path(source_path).resolve()
    try:
        rel_target = target_path.relative_to(REPO_ROOT)
    except ValueError:
        return None, f"source not under REPO_ROOT"
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir) / "sandbox"
        shutil.copytree(
            REPO_ROOT, sandbox,
            symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "*.pyc", "logs",
            ),
        )
        # Overlay the modified source into the sandbox
        sandbox_target = sandbox / rel_target
        sandbox_target.parent.mkdir(parents=True, exist_ok=True)
        sandbox_target.write_text(modified_source, encoding="utf-8")
        try:
            result = subprocess.run(
                shlex.split(test_cmd),
                capture_output=True, text=True, timeout=120,
                cwd=str(sandbox),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            output = result.stdout + result.stderr

            m = re.search(r'(\d+)\s+passed', output)
            passed = int(m.group(1)) if m else 0
            m = re.search(r'(\d+)\s+failed', output)
            failed = int(m.group(1)) if m else 0
            collected_zero = bool(re.search(r'collected\s+0\s+items', output))

            total = passed + failed
            if total > 0:
                score = passed / total
                return score, f"{passed}/{total} passed (sandbox)"

            # Genuine "no tests" — pytest exit code 5 = no tests collected
            if collected_zero and result.returncode == 5:
                return 1.0, "no tests collected"

            # Unparseable output (collection error, crash, etc.) — unavailable
            return None, (
                f"test results unavailable: rc={result.returncode} "
                f"output={output[:200]!r}"
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            return None, f"test execution failed: {e}"


def _run_effect_ruff(
    modified_source: str, baseline_violations: Optional[int],
    source_path: str = "",
) -> Tuple[Optional[float], str]:
    """e3: Static analysis non-regression via ruff."""
    if baseline_violations is None:
        return None, "ruff baseline unavailable"
    # Anchor temp file to source directory so ruff picks up pyproject.toml
    anchor_dir = _anchor_dir_for(source_path)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(modified_source)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", tmp_path,
             "--output-format=json", "--quiet"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode not in (0, 1):
            return None, f"ruff failed: rc={result.returncode} stderr={result.stderr[:200]}"
        try:
            violations = json.loads(result.stdout)
            if not isinstance(violations, list):
                return None, "ruff output was not JSON list"
            total_count = len(violations)
        except (json.JSONDecodeError, TypeError) as e:
            return None, f"ruff output parse failed: {e}"
        # Delta-based: only NEW violations reduce score (0.1 penalty each)
        delta = max(0, total_count - baseline_violations)
        score = max(0.0, 1.0 - delta * 0.1)
        return score, f"{total_count} total, {delta} new (baseline: {baseline_violations})"
    except (subprocess.TimeoutExpired, OSError) as e:
        return None, f"ruff unavailable: {e}"
    finally:
        os.unlink(tmp_path)


def _run_effect_bandit(
    modified_source: str, baseline_findings: Optional[Dict[str, int]],
    source_path: str = "",
) -> Tuple[Optional[float], str]:
    """e4: Security non-regression via bandit.

    Scoring per Python encoding: -0.5 per new HIGH, -0.2 per new MEDIUM.
    baseline_findings is a dict with 'high' and 'medium' keys.
    """
    if baseline_findings is None:
        return None, "bandit baseline unavailable"
    # Anchor temp file to source directory for config discovery
    anchor_dir = _anchor_dir_for(source_path)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(modified_source)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", tmp_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode not in (0, 1):
            return None, f"bandit failed: rc={result.returncode} stderr={result.stderr[:200]}"
        try:
            data = json.loads(result.stdout)
            if not isinstance(data, dict):
                return None, "bandit output was not JSON object"
            results_list = data.get("results", [])
            high_count = sum(
                1 for r in results_list
                if r.get("issue_severity", "").upper() == "HIGH"
            )
            med_count = sum(
                1 for r in results_list
                if r.get("issue_severity", "").upper() == "MEDIUM"
            )
        except (json.JSONDecodeError, TypeError) as e:
            return None, f"bandit output parse failed: {e}"
        baseline_high = baseline_findings.get("high", 0)
        baseline_med = baseline_findings.get("medium", 0)
        new_high = max(0, high_count - baseline_high)
        new_med = max(0, med_count - baseline_med)
        score = max(0.0, 1.0 - new_high * 0.5 - new_med * 0.2)
        return score, (
            f"{high_count} HIGH/{med_count} MEDIUM "
            f"(baseline: {baseline_high}H/{baseline_med}M, "
            f"new: {new_high}H/{new_med}M)"
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return None, f"bandit unavailable: {e}"
    finally:
        os.unlink(tmp_path)


def _capture_baseline(source: str, source_path: str = "") -> Dict[str, Any]:
    """Capture baseline gate scores before fix application.

    Values are None when a tool is unavailable, so downstream gates
    can distinguish 'no violations' (0) from 'tool broken' (None).
    """
    baseline: Dict[str, Any] = {
        "ruff_violations": None,
        "bandit_findings": None,
    }
    # Anchor temp files to the source directory so ruff/bandit discover the
    # project's own config (pyproject.toml, setup.cfg) by walking upwards.
    #
    # That only makes sense for a PYTHON target inside this repository. An exam
    # target is markdown, staged read-only in a directory deliberately set to
    # refuse new files so a panel cannot drop anything beside the document it is
    # reviewing — and writing a scratch .py there fails with EPERM before the run
    # starts. Both controls are correct; anchoring is simply the wrong default
    # when the target is not code we own. Fall back to the system temp directory,
    # where there is no config to discover and none is wanted.
    anchor_dir = _anchor_dir_for(source_path)

    # Ruff violations on original source
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(source)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", tmp_path,
             "--output-format=json", "--quiet"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode in (0, 1):
            try:
                violations = json.loads(result.stdout)
                if isinstance(violations, list):
                    baseline["ruff_violations"] = len(violations)
            except (json.JSONDecodeError, TypeError):
                pass
    except (subprocess.TimeoutExpired, OSError):
        pass
    finally:
        os.unlink(tmp_path)

    # Bandit findings on original source
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(source)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", tmp_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode in (0, 1):
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    results_list = data.get("results", [])
                    baseline["bandit_findings"] = {
                        "high": sum(
                            1 for r in results_list
                            if r.get("issue_severity", "").upper() == "HIGH"
                        ),
                        "medium": sum(
                            1 for r in results_list
                            if r.get("issue_severity", "").upper() == "MEDIUM"
                        ),
                    }
            except (json.JSONDecodeError, TypeError):
                pass
    except (subprocess.TimeoutExpired, OSError):
        pass
    finally:
        os.unlink(tmp_path)

    return baseline


def compute_sk(
    fix_text: str,
    source: str,
    source_path: str,
    baseline: Optional[Dict[str, Any]] = None,
    test_cmd: Optional[str] = None,
    declared_target_kind: Optional[str] = None,
) -> SkResult:
    """Full S_k computation pipeline for a proposed fix.

    Parses SEARCH/REPLACE blocks, applies them, runs hard gates and
    effect evidence gates. Returns SkResult with tristate.

    PROSE SHORT-CIRCUIT (A2, 2026-08-01). Before anything else, the target is
    classified from its path and its bytes. If it is prose, S_k returns
    ``NO_SCORE`` and no gate runs. This is enforced HERE, at the computation,
    not at the call site and not by a config switch, because every one of the
    gates below is meaningless-to-actively-inverted on prose:

      * ``e3_ruff`` — ruff error-recovers over markdown and reported ~2752
        phantom diagnostics as the BASELINE on the 2026-08-01 control, so the
        delta it scores measures how much English the fix added.
      * ``e4_bandit`` — bandit cannot parse the file, returns an empty result
        set, and therefore reports "0 HIGH / 0 MEDIUM" forever, at weight 2.0,
        the heaviest in the set. It is structurally incapable of failing.
      * ``e2_regression`` — permanently unavailable: prose targets live outside
        the repository and no prose config sets ``test_cmd``.

    With the hard gates repaired to look at the fenced listings (A=1), those
    three combine to a measured sk=1.0000 ADMISSIBLE for a fix that injected
    ``subprocess.call("rm -rf ...", shell=True)`` into a listing, against
    0.6667 for a correct prose fix. Findings on prose targets are resolved by
    FALSIFIERS — runnable code that computes the true value and asserts against
    the claim — which is how Exp 48 and Exp 49 converged at rounds 5 and 6 with
    S_k rejecting 100% of fixes. That path is substrate-independent and is
    untouched by this short-circuit.
    """
    kind, kind_reason = resolve_target_kind(
        source_path, source, declared=declared_target_kind)
    if kind != TARGET_KIND_PYTHON:
        return SkResult(
            sk=0.0, A=0.0, E=0.0, tristate=SK_NO_SCORE,
            gate_details={
                "target_kind": kind,
                "target_kind_reason": kind_reason,
                "reason": (
                    "S_k is defined over Python source; this target is "
                    f"{kind}. No gate was run, so this fix is neither admitted "
                    "nor rejected — it is unscored. Resolution for this target "
                    "runs through the falsifier path."),
            },
            blocks_parsed=0, blocks_applied=0,
        )

    blocks = parse_search_replace_blocks(fix_text)
    if not blocks:
        return SkResult(
            sk=0.0, A=0.0, E=0.0, tristate=SK_ESCALATE,
            gate_details={"error": "no SEARCH/REPLACE blocks found"},
            blocks_parsed=0, blocks_applied=0,
        )

    modified, applied, apply_error = apply_fix_blocks(source, blocks, source_path)
    if modified is None or applied == 0:
        return SkResult(
            sk=0.0, A=0.0, E=0.0, tristate=SK_REJECTED,
            gate_details={"error": apply_error or "fix_blocks_not_applied"},
            blocks_parsed=len(blocks), blocks_applied=0,
        )

    # Hard gates
    details: Dict[str, Any] = {}
    g1_score, g1_detail = _run_hard_gate_ast(modified, source_path)
    details["g1_ast"] = {"score": g1_score, "detail": g1_detail}

    g2_score, g2_detail = _run_hard_gate_compile(modified, source_path)
    details["g2_compile"] = {"score": g2_score, "detail": g2_detail}

    A = g1_score * g2_score

    if A == 0:
        return SkResult(
            sk=0.0, A=0.0, E=0.0, tristate=SK_REJECTED,
            gate_details=details,
            blocks_parsed=len(blocks), blocks_applied=applied,
        )

    # Effect evidence gates
    if baseline is None:
        baseline = {}

    # Gate weights (from Python expert encoding)
    effect_gates: List[Tuple[str, float, float]] = []  # (name, score, weight)
    unavailable_gates: List[str] = []

    # e2: regression suite
    e2_score, e2_detail = _run_effect_regression(modified, source_path, test_cmd)
    details["e2_regression"] = {"score": e2_score, "detail": e2_detail}
    if e2_score is not None:
        effect_gates.append(("e2_regression", e2_score, 2.0))
    elif test_cmd:  # configured but unavailable
        unavailable_gates.append("e2_regression")

    # e3: ruff non-regression
    e3_score, e3_detail = _run_effect_ruff(
        modified, baseline.get("ruff_violations"), source_path=source_path)
    details["e3_ruff"] = {"score": e3_score, "detail": e3_detail}
    if e3_score is not None:
        effect_gates.append(("e3_ruff", e3_score, 1.0))
    else:
        unavailable_gates.append("e3_ruff")

    # e4: bandit security
    e4_score, e4_detail = _run_effect_bandit(
        modified, baseline.get("bandit_findings"), source_path=source_path)
    details["e4_bandit"] = {"score": e4_score, "detail": e4_detail}
    if e4_score is not None:
        effect_gates.append(("e4_bandit", e4_score, 2.0))
    else:
        unavailable_gates.append("e4_bandit")

    # ESCALATE if no effect gates produced evidence
    if not effect_gates:
        details["_unavailable"] = unavailable_gates
        return SkResult(
            sk=0.0, A=A, E=0.0, tristate=SK_ESCALATE,
            gate_details=details,
            blocks_parsed=len(blocks), blocks_applied=applied,
        )

    # Compute E: renormalised weighted arithmetic mean over available gates.
    # Arithmetic mean preserves graded semantics — a single zero score
    # reduces E proportionally rather than vetoing it entirely. If a gate
    # is genuinely non-negotiable, it belongs in the hard gates (A).
    W = sum(w for _, _, w in effect_gates)
    if W == 0:
        E = 0.0
    else:
        E = sum((w / W) * s for _, s, w in effect_gates)

    if unavailable_gates:
        details["_unavailable"] = unavailable_gates

    sk = A * E
    tristate = SK_ADMISSIBLE if sk > 0 else SK_REJECTED

    return SkResult(
        sk=round(sk, 4), A=A, E=round(E, 4), tristate=tristate,
        gate_details=details,
        blocks_parsed=len(blocks), blocks_applied=applied,
    )


class ChannelViolationError(RuntimeError):
    """Raised when the divergence modulator is passed in a forbidden channel slot.

    Channel contract (round-2 5/5 unanimous, round-3 converged):

        eta_int_modulated = m_div * eta_int
        eta_combined      = eta_int_modulated * (1 - c_ext * (1 - nu_k))
        q                 = eta_combined * d * p
        R_k update        = compute_rk(R_old, q, sk, ...)

    FORBIDDEN paths:
      * m_div as pre-factor on R_k (e.g. ``m_div * R_old``)
      * m_div entering q as an independent factor outside eta_int
      * m_div contributing to nu_k
    """


# R_k(0) = π_k (appendix §1.1 initial condition). π_base is the uniform,
# memory-free prior: a finding of an unseen flaw class is a coin flip. This
# was an inline literal 0.5 in the S_k pipeline from the start; naming it is
# what lets appendix §1.5's blended prior substitute for it without the two
# defaults drifting apart.
RK0_PI_BASE: float = 0.5


def compute_rk(
    R_old: float, q: float, sk: float,
    nu_b: float = 0.05, nu_f: float = 0.20,
) -> float:
    """Three-phase R_k update: detection -> resolution -> re-injection.

    Uses bounded nu_eff = 1 - (1-nu_b)*(1-(1-sk)*nu_f).

    Channel boundary: ``q`` must already include any divergence modulation
    via ``m_div * eta_int`` upstream. This function is the sink, not the
    site where the modulator is applied. Callers that need the channel
    check enforced at composition time should use
    :func:`compute_rk_with_eta_channel` which decomposes q and validates
    the assignment is on eta_int, not on R_k or q directly.
    """
    # Defensive cast and clamp all probability-space inputs to [0, 1]
    R_old = max(0.0, min(1.0, float(R_old)))
    q = max(0.0, min(1.0, float(q)))
    sk = max(0.0, min(1.0, float(sk)))
    nu_b = max(0.0, min(1.0, float(nu_b)))
    nu_f = max(0.0, min(1.0, float(nu_f)))
    # HARD CONSTRAINT: nu_b + nu_f <= 1
    if nu_b + nu_f > 1.0:
        scale = 1.0 / (nu_b + nu_f)
        nu_b *= scale
        nu_f *= scale

    # Phase 1: Detection
    denom = 1.0 - q * R_old
    if abs(denom) < 1e-12:
        R_det = R_old
    else:
        R_det = R_old * (1.0 - q) / denom

    # Phase 2: Resolution (S_k replaces sigma)
    R_base = sk * R_det + (1.0 - sk) * R_old

    # Phase 3: Re-injection (bounded form)
    nu_eff = 1.0 - (1.0 - nu_b) * (1.0 - (1.0 - sk) * nu_f)
    R_k = R_base * (1.0 - nu_eff) + nu_eff

    return max(0.0, min(1.0, R_k))


def apply_sk_to_rk(
    R_old: float, tristate: str, updated: Optional[float] = None,
) -> Tuple[float, str]:
    """The single sink where an S_k outcome is allowed to move R_k.

    Returns (R_new, why).

    A2 (2026-08-01). When S_k returns ``NO_SCORE`` — the target is prose, no
    gate ran — the fix's efficacy must enter R_k as ZERO MOVEMENT. R_k is
    RESIDUAL RISK, so "no movement" means R_new == R_old exactly.

    THE TRAP THIS AVOIDS. The obvious reading of "efficacy enters as 0" is
    ``compute_rk(R_old, q, sk=0.0)``. That is wrong, and wrong in the dangerous
    direction. With sk=0 the resolution phase is a no-op (``R_base = R_old``)
    but the re-injection phase is NOT: ``nu_eff = 1 - (1-nu_b)(1-(1-sk)nu_f)``
    is at its MAXIMUM when sk=0, because a worthless fix is modelled as maximally
    likely to inject a new defect. At the defaults (nu_b=0.05, nu_f=0.20) and
    R_old=0.5, that path returns 0.62 — risk PUSHED UP by 0.12 as a penalty for
    a fix nothing ever assessed. Repeat that once per prose finding per round
    and the run accrues a fabricated risk it can never work off, because on a
    prose target no S_k evaluation can ever move it back down.

    "Not scored" and "scored zero" are different statements. This function is
    what keeps them different.
    """
    R_old = max(0.0, min(1.0, float(R_old)))
    if tristate == SK_NO_SCORE:
        return R_old, (
            "NO_SCORE: R_k unchanged. The fix was never assessed, so its "
            "efficacy enters as zero MOVEMENT, not as a zero SCORE.")
    if updated is None:
        return R_old, f"{tristate}: no update computed; R_k unchanged"
    return max(0.0, min(1.0, float(updated))), f"{tristate}: R_k updated"


def compute_rk_with_eta_channel(
    R_old: float, sk: float,
    eta_int: float, m_div: float,
    c_ext: float, nu_k: float,
    d: float, p: float,
    nu_b: float = 0.05, nu_f: float = 0.20,
) -> float:
    """R_k update that enforces the eta_int channel for the divergence modulator.

    Exp 40 fix 1E.10: composes q from primitives with m_div applied ONLY
    as an eta_int multiplier. Ranges are validated at entry; if a caller
    accidentally passes m_div in a forbidden slot (e.g. by computing
    ``R_old_modulated = m_div * R_old`` and then supplying that), the
    range check on R_old catches it when m_div * R_old drifts out of
    [0, 1] and the input-clamp silently coerces it — which itself is a
    regression surface. To defend against that, we validate m_div and
    eta_int as separate inputs *here* before composing q.
    """
    # Explicit channel validation — inputs that would be silently clamped
    # by compute_rk are rejected here as channel violations.
    for name, value in (
        ("m_div", m_div), ("eta_int", eta_int),
        ("c_ext", c_ext), ("nu_k", nu_k), ("d", d), ("p", p),
    ):
        fval = float(value)
        if not (0.0 <= fval <= 1.0):
            raise ChannelViolationError(
                f"{name}={fval} must be in [0, 1]; the divergence modulator "
                f"(m_div) multiplies eta_int only, not R_k or q directly."
            )

    # Canonical channel composition — m_div only on eta_int.
    eta_int_modulated = m_div * eta_int
    eta_combined = eta_int_modulated * (1.0 - c_ext * (1.0 - nu_k))
    q = eta_combined * d * p

    # Final sanity: q is a probability; composition must not produce q > 1.
    # Given each factor is in [0, 1], q ∈ [0, 1] algebraically. If this
    # invariant is ever violated we have a numerical or input-ordering bug.
    if not (0.0 <= q <= 1.0 + 1e-9):
        raise ChannelViolationError(
            f"composed q={q} escaped [0, 1]; channel invariant broken."
        )

    return compute_rk(R_old, q, sk, nu_b=nu_b, nu_f=nu_f)


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic R_k recomputation validation (14 April 2026)
# ─────────────────────────────────────────────────────────────────────────────

# Regex patterns for extracting R_k parameters from model corroboration text.
# Models use varied notation (η vs eta, ν_eff vs nu_eff, × vs * vs ·).
_RK_RE_R_OLD = re.compile(
    r'R_?(?:old|prev|prior)\s*[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
_RK_RE_ETA = re.compile(
    r'(?:[ηη]|eta)\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
_RK_RE_D = re.compile(
    r'\bd\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)')
_RK_RE_P = re.compile(
    r'\bp\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)')
_RK_RE_Q_LINE = re.compile(
    r'^\s*q\s*[=:].*$', re.MULTILINE)
_RK_RE_SK = re.compile(
    r'S_?k\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
_RK_RE_NU_EFF = re.compile(
    r'(?:[νν]_?eff|nu_?eff)\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
_RK_RE_R_DET = re.compile(
    r'R_?(?:det|base)\s*[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
# For R_k final value: match lines starting with R_k and extract the last
# number.  Models write "R_k = 0.272 × (1 - 0.05) + 0.05 = 0.308" —
# the final value is always the last float on the R_k line.
_RK_RE_R_FINAL_LINE = re.compile(
    r'^[^\n]*R_?k\s*[=≈:].*$', re.IGNORECASE | re.MULTILINE)
_RK_RE_TRAILING_FLOAT = re.compile(r'([0-9]+\.?[0-9]*)\s*$')


def _validate_rk_computation(corroboration_text: str) -> Tuple[str, Optional[float], Optional[float]]:
    """Recompute R_k from stated parameters and compare with model's result.

    Returns (status, model_rk, recomputed_rk) where status is one of:
      PASS  — within tolerance 0.01
      WARN  — within tolerance 0.05 but outside 0.01
      FAIL  — beyond tolerance 0.05
      SKIP  — couldn't extract sufficient parameters

    Advisory only — logs discrepancies, never rejects findings.
    """
    if not corroboration_text:
        return "SKIP", None, None

    def _first_float(pattern: re.Pattern, text: str) -> Optional[float]:
        m = pattern.search(text)
        if m:
            try:
                return float(m.group(1))
            except (ValueError, IndexError):
                pass
        return None

    # Extract the model's stated final R_k.
    # Models write "R_k = 0.272 × (1 - 0.05) + 0.05 = 0.308" — the final
    # value is the last float on the last line containing "R_k =".
    model_rk = None
    for line_match in _RK_RE_R_FINAL_LINE.finditer(corroboration_text):
        line = line_match.group()
        trail = _RK_RE_TRAILING_FLOAT.search(line)
        if trail:
            try:
                model_rk = float(trail.group(1))
            except ValueError:
                pass
    if model_rk is None:
        return "SKIP", None, None

    # Extract R_old — required
    R_old = _first_float(_RK_RE_R_OLD, corroboration_text)
    if R_old is None:
        return "SKIP", model_rk, None

    # Extract q directly (trailing float on "q = ..." line), or compute
    # from eta * d * p.  Models write "q = 0.90 × 0.80 × 0.90 = 0.648"
    # where the final value is the trailing float, not the first number.
    q = None
    q_line = _RK_RE_Q_LINE.search(corroboration_text)
    if q_line:
        trail = _RK_RE_TRAILING_FLOAT.search(q_line.group())
        if trail:
            try:
                q = float(trail.group(1))
            except ValueError:
                pass
    if q is None:
        eta = _first_float(_RK_RE_ETA, corroboration_text)
        d = _first_float(_RK_RE_D, corroboration_text)
        p = _first_float(_RK_RE_P, corroboration_text)
        if eta is not None and d is not None and p is not None:
            q = eta * d * p
        else:
            return "SKIP", model_rk, None

    # Phase 1: Detection — R_det = R_old * (1-q) / (1 - q*R_old)
    denom = 1.0 - q * R_old
    if abs(denom) < 1e-12:
        R_det = R_old
    else:
        R_det = R_old * (1.0 - q) / denom

    # Extract S_k and nu_eff for full three-phase computation
    sk = _first_float(_RK_RE_SK, corroboration_text)
    nu_eff = _first_float(_RK_RE_NU_EFF, corroboration_text)

    if sk is not None and nu_eff is not None:
        # Full three-phase: detection -> resolution -> re-injection
        R_base = sk * R_det + (1.0 - sk) * R_old
        recomputed = R_base * (1.0 - nu_eff) + nu_eff
    elif sk is not None:
        # Two-phase only (no re-injection term)
        recomputed = sk * R_det + (1.0 - sk) * R_old
    else:
        # Detection phase only — R_k = R_det
        recomputed = R_det

    recomputed = max(0.0, min(1.0, recomputed))
    delta = abs(model_rk - recomputed)

    if delta <= 0.01:
        return "PASS", model_rk, recomputed
    elif delta <= 0.05:
        return "WARN", model_rk, recomputed
    else:
        return "FAIL", model_rk, recomputed


def _extract_corroboration_sections(response_text: str) -> List[str]:
    """Extract CORROBORATION sections from a model's raw response text.

    Each section runs from 'CORROBORATION' until the next finding boundary
    (FINDING_ID, VERIFIED, ---) or end of text.
    """
    sections: List[str] = []
    # Split on CORROBORATION header
    parts = re.split(r'CORROBORATION\s*[:\-]?\s*', response_text, flags=re.IGNORECASE)
    for part in parts[1:]:  # skip everything before first CORROBORATION
        # Truncate at next finding boundary
        end_match = re.search(
            r'\n\s*(?:FINDING_ID|VERIFIED|---|\n\s*\n\s*FINDING_ID'
            r'|SEVERITY|FIND\s*:|FOLLOW\s*:|\[\s*\{)',
            part, re.IGNORECASE)
        if end_match:
            sections.append(part[:end_match.start()])
        else:
            sections.append(part)
    return sections


def validate_round_rk(
    findings: List[Finding],
    responses: Dict[str, str],
) -> Dict[str, List[Tuple[str, str, Optional[float], Optional[float]]]]:
    """Validate R_k computations for all findings in a round.

    Returns dict keyed by model_id, each value a list of
    (finding_id, status, model_rk, recomputed_rk) tuples.

    Advisory only — logs WARN/FAIL but never rejects findings.
    """
    results: Dict[str, List[Tuple[str, str, Optional[float], Optional[float]]]] = {}

    for model_id, text in responses.items():
        sections = _extract_corroboration_sections(text)
        model_findings = [f for f in findings if f.model_id == model_id]
        model_results: List[Tuple[str, str, Optional[float], Optional[float]]] = []

        # Match sections to findings by position (both are in document order)
        for i, f in enumerate(model_findings):
            if i < len(sections):
                status, model_rk, recomputed = _validate_rk_computation(sections[i])
            else:
                status, model_rk, recomputed = "SKIP", None, None
            model_results.append((f.finding_id, status, model_rk, recomputed))

            if status == "WARN":
                _log(f"  R_k WARN: {f.finding_id} — model={model_rk:.3f}, "
                     f"recomputed={recomputed:.3f}, delta={abs(model_rk - recomputed):.3f}")
            elif status == "FAIL":
                _log(f"  R_k FAIL: {f.finding_id} — model={model_rk:.3f}, "
                     f"recomputed={recomputed:.3f}, delta={abs(model_rk - recomputed):.3f}")

        if model_results:
            results[model_id] = model_results

    return results


def check_sk_threshold(
    sk: float, nu_b: float, nu_f: float,
    q: float, R: float, s_floor: float = 0.0,
) -> Tuple[bool, float]:
    """Check if S_k exceeds the break-even threshold S*.

    Returns (passes, s_star). Fixes below S* do more harm than good
    (Valley of Bad Fixes).
    """
    # Defensive cast and clamp all probability-space inputs to [0, 1]
    sk = max(0.0, min(1.0, float(sk)))
    q = max(0.0, min(1.0, float(q)))
    R = max(0.0, min(1.0, float(R)))
    s_floor = max(0.0, min(1.0, float(s_floor)))
    nu_b = max(0.0, min(1.0, float(nu_b)))
    nu_f = max(0.0, min(1.0, float(nu_f)))
    if nu_b + nu_f > 1.0:
        scale = 1.0 / (nu_b + nu_f)
        nu_b *= scale
        nu_f *= scale

    # Bounded S*: (nu_b + nu_f - nu_b*nu_f - q*R) / (nu_f * (1 - nu_b))
    # Edge cases:
    #   nu_f ≈ 0: fix can't introduce problems → S* = 0 (any fix helps)
    #   nu_b ≈ 1: any modification is risky → S* = 1.0 (no fix good enough)
    if nu_f < 1e-12:
        s_star = 0.0  # no fix-induced re-injection; any positive S_k helps
    elif (1.0 - nu_b) < 1e-12:
        s_star = 1.0  # pathological: any modification introduces full risk
    else:
        denom = nu_f * (1.0 - nu_b)
        s_star = (nu_b + nu_f - nu_b * nu_f - q * R) / denom
        # Clamp to [0, 1]: values outside mean "always pass" or "never pass"
        s_star = max(0.0, min(1.0, s_star))

    effective_threshold = max(s_star, s_floor)
    return sk >= effective_threshold, round(s_star, 4)


def _evaluate_sk_for_findings(
    registry: FindingRegistry,
    source_code: str,
    source_path: str,
    baseline: Dict[str, Any],
    round_idx: int,
    test_cmd: Optional[str] = None,
    s_floor: float = 0.0,
    c_ext: float = 0.0,
    nu_k_by_finding: Optional[Dict[str, float]] = None,
    nu_k_default: float = 0.0,
    rk0_prior: Optional[Callable[[int], float]] = None,
) -> Dict[str, Any]:
    """Evaluate S_k for all findings with proposed fixes in SEARCH/REPLACE format.

    Returns stats dict for round telemetry.

    ``c_ext`` / ``nu_k_*`` (2026-07-31) carry the Ouroboros retrieval into the
    R_k channel: ``eta_combined = eta_int * (1 - c_ext * (1 - nu_k))``. The
    defaults (0.0) reproduce the identity path this function used from 21 April
    to 31 July, so a run without an ``_ouroboros`` block that opts in is
    byte-identical to before.

    ``rk0_prior`` (2026-07-31) supplies R_k(0) — the appendix §1.1 initial
    condition ``R_k(0) = π_k`` — from cross-experiment immune memory, keyed on
    the finding's flaw class. ``None`` (the default, and the state whenever
    ``immune_memory_enabled`` is off) falls back to the uniform base prior
    ``RK0_PI_BASE``, the literal 0.5 this function used from the start.
    """
    nu_k_by_finding = nu_k_by_finding or {}
    c_ext = max(0.0, min(1.0, float(c_ext)))
    stats: Dict[str, Any] = {
        "round": round_idx, "evaluated": 0, "admissible": 0,
        "rejected": 0, "escalated": 0,
        # A2: counted separately from every other outcome. A NO_SCORE tally
        # folded into "rejected" would read as 38 bad fixes where the truth is
        # 38 unassessed ones — which is the exact misreading that let the
        # 2026-08-01 control look like a panel failure rather than an
        # instrument failure.
        "no_score": 0,
        "results": {},
    }

    for cid, entry in registry.entries.items():
        if entry["status"] not in ("OPEN", "CONFIRMED", "CONTESTED"):
            continue
        fix_text = entry.get("proposed_fix", "")
        if not fix_text or "<<<<" not in fix_text:
            continue

        sk_result = compute_sk(
            fix_text, source_code, source_path,
            baseline=baseline, test_cmd=test_cmd,
        )
        stats["evaluated"] += 1

        # Store result on registry entry
        entry["sk_result"] = {
            "sk": sk_result.sk,
            "A": sk_result.A,
            "E": sk_result.E,
            "tristate": sk_result.tristate,
            "blocks_parsed": sk_result.blocks_parsed,
            "blocks_applied": sk_result.blocks_applied,
            "gate_details": sk_result.gate_details,
        }

        # Extract per-finding model parameters (fall back to defaults)
        meta = entry.get("model_params", {})
        nu_b = meta.get("nu_b", 0.05)
        nu_f = meta.get("nu_f", 0.20)
        q = meta.get("q", 0.5)
        # R_k(0) — appendix §1.1 initial condition R_k(0) = π_k. Precedence:
        #   1. a model-supplied R, which is an ALREADY-UPDATED estimate rather
        #      than an initial condition, so it outranks any prior;
        #   2. the §1.5 blended prior π(k) = (1-ρ)·π_base + ρ·π_mem(k) from
        #      cross-experiment immune memory, when consumption is on;
        #   3. the uniform base prior — what every run from Exp 37 to Exp 49
        #      actually used, because model_params is never populated.
        if "R" in meta:
            R_old, rk0_source = meta["R"], "model"
        elif rk0_prior is not None:
            R_old, rk0_source = rk0_prior(int(entry.get("flaw_class") or 0)), "memory"
            R_old = max(0.0, min(1.0, float(R_old)))
        else:
            R_old, rk0_source = RK0_PI_BASE, "uniform"

        # A2 (2026-08-01): a NO_SCORE result leaves the loop here. No S*
        # threshold check (S* is a statement about a score that does not
        # exist), no R_k update (apply_sk_to_rk pins R_new to R_old), and no
        # contribution to the admissible/rejected tallies. The finding is left
        # exactly as the falsifier path left it.
        if sk_result.tristate == SK_NO_SCORE:
            R_new, why = apply_sk_to_rk(R_old, SK_NO_SCORE)
            entry["sk_result"]["R_old"] = R_old
            entry["sk_result"]["R_new"] = R_new
            entry["sk_result"]["rk_note"] = why
            stats["no_score"] += 1
            _log(f"  S_k [{cid}]: NO_SCORE — "
                 f"{sk_result.gate_details.get('target_kind_reason', 'non-Python target')}"
                 f"; R_k held at {R_old:.3f}")
            stats["results"][cid] = entry["sk_result"]
            continue

        # S* threshold check
        if sk_result.tristate == SK_ADMISSIBLE:
            passes, s_star = check_sk_threshold(
                sk_result.sk, nu_b=nu_b, nu_f=nu_f,
                q=q, R=R_old, s_floor=s_floor,
            )
            entry["sk_result"]["s_star"] = s_star
            entry["sk_result"]["passes_threshold"] = passes
            if passes:
                # Close the R_k loop: compute updated risk
                # F2 (2026-04-21): route through compute_rk_with_eta_channel
                # in identity mode (m_div=1.0, c_ext=0, nu_k=0, d=1, p=1,
                # eta_int=q) so q flows through the channel validator. At
                # identity, eta_combined = 1.0 * q * (1 - 0*(1-0)) = q,
                # and q_out = q * 1 * 1 = q — mathematically equivalent
                # to the bare compute_rk(q) path. Verified as identity
                # across 1620 parameter combinations in the 20 April
                # pre-launch re-audit. Ships under
                # `eta_int_modulator_wired_into_compute_rk: true` in
                # bench/exp40_configs/40_gate.json.
                # Ouroboros loop-close (2026-07-31): c_ext / nu_k are no longer
                # literal zeros. nu_k is looked up per finding through the
                # registry's source_aliases (the calibrator keys on the model's
                # own finding_id, the registry on canonical id), falling back to
                # the round mean when this entry filed in an earlier round.
                _nu_k = nu_k_default
                if nu_k_by_finding:
                    for _alias in entry.get("source_aliases", []) or []:
                        if _alias in nu_k_by_finding:
                            _nu_k = nu_k_by_finding[_alias]
                            break
                _nu_k = max(0.0, min(1.0, float(_nu_k)))
                R_new = compute_rk_with_eta_channel(
                    R_old=R_old, sk=sk_result.sk,
                    eta_int=q, m_div=1.0,
                    c_ext=c_ext, nu_k=_nu_k,
                    d=1.0, p=1.0,
                    nu_b=nu_b, nu_f=nu_f,
                )
                if c_ext > 0.0:
                    entry["sk_result"]["c_ext"] = round(c_ext, 4)
                    entry["sk_result"]["nu_k"] = round(_nu_k, 4)
                    entry["sk_result"]["eta_combined"] = round(
                        q * (1.0 - c_ext * (1.0 - _nu_k)), 6)
                # The wrapper==bare identity holds only at c_ext=0; with a real
                # retrieval the two are SUPPOSED to differ, so the assert is
                # scoped to the identity configuration it was written for.
                if os.environ.get("DEBUG_CHANNEL_CHECK") and c_ext == 0.0:
                    _R_bare = compute_rk(R_old=R_old, q=q, sk=sk_result.sk,
                                         nu_b=nu_b, nu_f=nu_f)
                    assert abs(R_new - _R_bare) < 1e-9, (
                        f"F2 identity broken at cid={cid}: wrapper "
                        f"R_new={R_new} != bare R_bare={_R_bare} "
                        f"(q={q}, R_old={R_old}, sk={sk_result.sk})"
                    )
                entry["sk_result"]["R_old"] = R_old
                entry["sk_result"]["R_new"] = R_new
                # Provenance of R_k(0), written ONLY when memory supplied it,
                # so the consumption-off report is byte-identical to before.
                if rk0_source == "memory":
                    entry["sk_result"]["rk0_source"] = "memory"
                    entry["sk_result"]["rk0_flaw_class"] = int(
                        entry.get("flaw_class") or 0)
                    stats.setdefault("rk0_memory_seeded", 0)
                    stats["rk0_memory_seeded"] += 1
                stats["admissible"] += 1
                _log(f"  S_k [{cid}]: ADMISSIBLE sk={sk_result.sk:.3f} "
                     f"(S*={s_star:.3f}) R: {R_old:.3f} -> {R_new:.3f}"
                     + (f" [R_k(0) from immune memory, flaw class "
                        f"{int(entry.get('flaw_class') or 0)}]"
                        if rk0_source == "memory" else ""))
            else:
                stats["rejected"] += 1
                entry["sk_result"]["tristate"] = SK_REJECTED
                _log(f"  S_k [{cid}]: REJECTED sk={sk_result.sk:.3f} "
                     f"< S*={s_star:.3f} (Valley of Bad Fixes)")
        elif sk_result.tristate == SK_REJECTED:
            stats["rejected"] += 1
            _log(f"  S_k [{cid}]: REJECTED A={sk_result.A} "
                 f"({sk_result.gate_details})")
        else:
            stats["escalated"] += 1
            _log(f"  S_k [{cid}]: ESCALATE — {sk_result.gate_details}")

        stats["results"][cid] = entry["sk_result"]

    if stats["evaluated"] > 0:
        _log(f"  S_k pipeline: {stats['evaluated']} evaluated, "
             f"{stats['admissible']} ADMISSIBLE, "
             f"{stats['rejected']} REJECTED, "
             f"{stats['escalated']} ESCALATE, "
             f"{stats['no_score']} NO_SCORE")
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Preflight
# ─────────────────────────────────────────────────────────────────────────────

def _record_computed_evidence(entry: dict, *, kind: str, by: str, detail: str,
                              falsifier: str = "") -> None:
    """Attach a computed answer to a finding that may not be cleared automatically.

    FOUNDER RULING, 2026-08-03. The post-convergence sweep cannot clear a critical
    and structurally never has: the highest severity it has ever touched is 0.66
    against a 0.70 line. That much is deliberate — CONFIRM-only exists because on
    Exp 42 two of three REFUTED verdicts on criticals were themselves wrong, and
    nothing here weakens it.

    What was NOT deliberate is that when the computation ran and returned "this
    claim looks sound", the answer was thrown away. The founder's objection is
    exact: if it can be computed, the models should compute it — and the finding
    AND the fix they devised should both reach a human. Both, not either. A
    perfectly good fix was being binned for scoring 0.71 rather than 0.69, on a
    number assigned once at intake and never recomputed.

    So the finding stays open, stays critical, stays a human decision — and the
    computed answer, the model that produced it, and the proposed fix travel with
    it. Genuine human-review categories (safety, legal, core functionality, real
    irreducibility) are unaffected: this changes what a human SEES, never what
    the machine decides.
    """
    entry.setdefault("computed_evidence", []).append({
        "kind": kind,
        "by": by,
        "detail": detail,
        "falsifier_code": (falsifier or "")[:4000],
        "proposed_fix": (entry.get("proposed_fix") or "")[:4000],
    })
    entry["hil_has_computed_evidence"] = True


def _rejection_lines(entry: dict) -> list:
    """A10 — render, for the panel, why the machinery declined this fix.

    Returns [] when there is nothing to report, so a healthy finding costs no
    prompt budget. Kept deliberately terse: the panel needs the reason and the
    gate, not the whole evidence bundle.
    """
    out = []
    sk = entry.get("sk_result") or {}
    tri = sk.get("tristate")
    if tri == SK_REJECTED:
        details = sk.get("gate_details") or {}
        failed = [k for k, v in details.items()
                  if v is False or v == 0 or v == 0.0]
        why = ", ".join(sorted(failed)) if failed else "hard gate returned 0"
        # The OUTCOME and the failed gate, never the S_k value. The panel can
        # act on "the syntax gate rejected it"; it cannot act on "0.0", and a
        # score in the discovery prompt is a channel from the fix-admission
        # pipeline into the finding stream for no gain. See the non-distortion
        # guard in test_immune_memory_consumption.py.
        out.append(
            f"FIX REJECTED by fix-admission: {why}. The fix was NOT applied "
            f"and did not close this finding.")
    elif tri == SK_ESCALATE:
        out.append(
            "FIX NOT SCORED: the evidence gates went silent (no baseline, no "
            "test command). The fix was not applied.")
    elif tri == SK_NO_SCORE:
        out.append(
            "FIX NOT SCORED: fix-admission is undefined on this target, so a "
            "fix cannot close this finding. Attach a runnable falsifier "
            "instead — that is what settles it here.")
    v = entry.get("falsifier_verdict")
    if v == "ERROR":
        out.append(
            "FALSIFIER ERROR: your test did not run to a verdict (broken "
            "import, syntax error, truncation, or a setup guard firing). It "
            "demonstrated nothing. Re-write it so it runs.")
    elif v == "UNTOOLABLE":
        out.append(
            "NO FALSIFIER: nothing runnable was attached, so nothing was "
            "demonstrated. This finding cannot settle without one.")
    if entry.get("irreducible_escalation"):
        out.append(
            f"ESCALATED TO HUMAN: {entry.get('hil_reason', 'ladder exhausted')}")
    # Discrimination-control records render on their own terms. The generic
    # line below says the finding "is not cleared automatically", which is TRUE
    # of a refutation-on-a-critical and FALSE of a control that passed — and a
    # line that misdescribes its own evidence is worse than no line.
    # A refused corrected passage must reach the model that offered it, or the
    # next attempt repeats the same mistake and the refusal is invisible.
    if entry.get("corrected_copy_rejected"):
        out.append(
            f"CORRECTED COPY REFUSED: {entry['corrected_copy_rejected']}. "
            f"Re-send it in the CORRECTED_COPY form, copying the original "
            f"passage from the target character for character.")
    disc = entry.get("discrimination") or {}
    _disc_outcome = disc.get("outcome")
    if _disc_outcome == DISC_PASSED:
        out.append(
            "DISCRIMINATION CONTROL PASSED: the same falsifier went QUIET "
            "against a corrected copy of the target, so it does test this "
            "claim. The CONFIRMED verdict stands.")
    elif _disc_outcome == DISC_FAILED:
        out.append(
            "MECHANICAL FAULT — the falsifier fires just as hard against a "
            "CORRECTED copy of the target, so it does not test this claim. The "
            "finding is NOT closed and NOT dropped: it goes to a human, and so "
            "does the instrument. Machinery that highlights an established "
            "truth as a fault, is something that may indeed warrant our "
            "attention. Attach a falsifier that goes quiet when the claim is "
            "fixed, and supply the corrected copy with it.")
    elif _disc_outcome in DISC_INDETERMINATE:
        out.append(
            f"DISCRIMINATION CONTROL {_disc_outcome}: "
            f"{(disc.get('detail') or '')[:200]} The CONFIRMED verdict is "
            f"UNCHANGED — an error is not evidence and nothing was vetoed.")
    ce = [c for c in (entry.get("computed_evidence") or [])
          if not str(c.get("kind", "")).startswith("discrimination_control")]
    if ce:
        out.append(
            f"COMPUTED EVIDENCE ON FILE ({len(ce)}): {ce[-1].get('kind')} by "
            f"{ce[-1].get('by')} — {(ce[-1].get('detail') or '')[:120]}. This finding "
            f"is CRITICAL so it is not cleared automatically; it goes to a human "
            f"WITH this evidence and the proposed fix.")
    return out


class LaunchRefused(RuntimeError):
    """A9: the run was refused before anything was dispatched."""


def preflight_target_machinery(cfg, target_path, target_kind: str) -> list:
    """A9 — refuse a launch whose machinery contradicts its target.

    Returns a list of REFUSAL strings; empty means launch. The check exists
    because the cheapest possible discovery of a doomed configuration is before
    the first paid dispatch, and the alternative has been discovered at round 3
    of 16 with the money spent.

    It is deliberately SHORT. Everything the harness can correct by itself, it
    already corrects by itself: `resolve_target_kind` raises on a declaration
    that disagrees with the file, S_k forces itself off on a non-Python target,
    and the specialist router bypasses file-based Python tools. A preflight that
    re-litigates those would be noise. What is left is the class the harness
    CANNOT correct at runtime — a missing input, or a missing absorber.
    """
    refusals = []

    # 1. The target must exist and be non-empty. Five of the six prose targets
    #    named in the Exp 50/51/52 configs did not exist on disk on 2026-08-01.
    try:
        if not Path(target_path).is_file():
            refusals.append(
                f"target does not exist: {target_path}. The run would dispatch a "
                f"panel at a file that is not there.")
        elif not Path(target_path).read_text(encoding="utf-8", errors="replace").strip():
            refusals.append(f"target is empty: {target_path}")
    except OSError as exc:
        refusals.append(f"target is not readable: {target_path} ({exc})")

    # 2. On a prose target the routing ladder is the ONLY absorber between the
    #    falsifier gate and the HIL queue. Without it, every finding whose first
    #    falsifier fails goes straight to the human. Measured on Exp 53: that is
    #    50% of findings. A prose run with routing off is a run whose output is
    #    a queue, and it costs the same as one that converges.
    if target_kind == TARGET_KIND_PROSE and not getattr(cfg, "routing_enabled", False):
        refusals.append(
            "routing_enabled is false on a PROSE target. Routing is the only "
            "absorber between the falsifier gate and the HIL queue; without it "
            "every finding whose first falsifier fails is escalated to the "
            "human. Set routing_enabled (or the legacy take_up_slack_enabled).")

    # 3. The falsifier gate IS the settlement path on a prose target, because
    #    S_k is off and fix-verification cannot close. With the gate off there
    #    is no route to a terminal state at all.
    if target_kind == TARGET_KIND_PROSE and not getattr(cfg, "falsifier_gate_enabled", False):
        refusals.append(
            "falsifier_gate_enabled is false on a PROSE target. S_k is forced "
            "off and fix-verification cannot close on prose, so the falsifier "
            "gate is the ONLY route to a terminal state. The run cannot settle "
            "anything.")

    return refusals


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

def _build_rk0_prior(
    cfg: RunnerConfig,
) -> Tuple[Optional[Callable[[int], float]], Dict[str, float]]:
    """Build the R_k(0) seed function from cross-experiment immune memory.

    Returns ``(prior_fn, receipt)``. ``prior_fn`` is ``None`` whenever
    consumption is off or the memory cannot be loaded — the S_k pipeline then
    falls back to the uniform base prior and the run is byte-identical to
    every run before 31 July 2026. ``receipt`` accumulates, per flaw class,
    the blended prior values the pipeline actually drew, and is written into
    the run report as ``immune_memory.rk0_consumed``: an empty receipt on an
    enabled run is the visible signature of a prior that reached nothing.

    Appendix §1.1 gives the initial condition ``R_k(0) = π_k``; appendix §1.5
    gives ``π(k) = (1-ρ)·π_base + ρ·π_mem(k)``. This is the only place the two
    are joined.

    Separated from ``run_experiment`` so the seam is reachable without a live
    panel dispatch — the runner's own call chain is asserted structurally in
    bench/tests/test_immune_memory_consumption.py.
    """
    receipt: Dict[str, float] = {}
    # Gated on CONSUMPTION, not on recording. See RunnerConfig for why the two
    # are separate switches: consumption inherited from the recording flag would
    # couple the factorial's four cells and dissolve the zero-plant control.
    if not getattr(cfg, "immune_memory_consume_rk0", False):
        return None, receipt
    try:
        from bench.dm._memory import ImmuneMemory
        mem = ImmuneMemory.load(str(Path(REPO_ROOT) / cfg.immune_memory_path))
        rho = max(0.0, min(1.0, float(getattr(cfg, "immune_memory_rho", 0.2))))
    except Exception as exc:  # noqa: BLE001 — never kill a run over a prior
        _log(f"  WARNING: immune memory load failed ({exc}); "
             f"R_k(0) falls back to the uniform prior {RK0_PI_BASE}")
        return None, receipt

    def prior(flaw_class: int) -> float:
        pi = mem.blended_prior(flaw_class=flaw_class, pi_base=RK0_PI_BASE,
                               rho=rho)
        receipt[str(flaw_class)] = round(pi, 6)
        return pi

    known = sorted(mem._records)
    _log(f"  immune memory: loaded for CONSUMPTION (rho={rho}, "
         f"pi_base={RK0_PI_BASE}); R_k(0) seeded from the blended prior. "
         f"Known flaw classes {known}; "
         f"pi_mem={ {k: round(mem.pi_mem(k), 3) for k in known} }; "
         f"blended R_k(0)="
         f"{ {k: round(mem.blended_prior(k, RK0_PI_BASE, rho), 3) for k in known} }")
    return prior, receipt


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

    # Confine the shell-bearing panel routes before the first dispatch. Set for
    # exam runs to the staged target directory; unset for code runs, where the
    # panel legitimately needs this repo. set_panel_cwd refuses a missing
    # directory rather than falling back to the repo — failing open here would
    # silently reinstate the exposure that let a model read the key in Exp 48.
    set_panel_cwd(cfg.panel_cwd or None)

    # NO PLAINTEXT SCORING KEY MAY EXIST WHILE AN EXAM RUNS.
    #
    # This is the control that actually binds, and it has to live HERE. Panel
    # confinement, read-only staging and the vault all govern what the PANEL can
    # reach; none of them touch the two paths that run model-authored code with
    # the operator's own credentials — reverify_falsifier (falsifier_verify.py)
    # and the execute_python tool given to the OpenRouter/DeepSeek routes.
    # Adversarial audit, 2026-07-29: a falsifier read every answer key by
    # absolute path and wrote the planted sets to /tmp, where any panel model
    # could collect them on the next round, leaving nothing in the run directory
    # for the forensics to find. Against that, the only defence is that there is
    # no plaintext key to read.
    #
    # The gate previously existed only in arc_sequencer.sh, so any leg launched
    # directly — which is how every experiment in this arc has been started at
    # least once — bypassed it entirely.
    if cfg.panel_cwd:
        _vault = Path(REPO_ROOT) / "bench" / "vault_keys.sh"
        if _vault.exists():
            try:
                _vs = subprocess.run(["bash", str(_vault), "status"],
                                     capture_output=True, text=True, timeout=120)
                _out = (_vs.stdout or "") + (_vs.stderr or "")
            except Exception as _e:  # noqa: BLE001
                raise RuntimeError(
                    f"cannot verify the scoring keys are vaulted ({type(_e).__name__}); "
                    f"refusing to start an exam run"
                ) from _e
            if not _out.lstrip().startswith("VAULTED"):
                raise RuntimeError(
                    "REFUSING TO START: a plaintext scoring key is on disk and this "
                    "run executes model-authored code with the operator's own "
                    "credentials.\n" + _out.strip() +
                    "\nRun 'bash bench/vault_keys.sh vault' first."
                )
            _log("  [panel] scoring keys verified vaulted")
        else:
            raise RuntimeError(
                "REFUSING TO START: bench/vault_keys.sh is missing, so the "
                "no-plaintext-key precondition cannot be checked for an exam run."
            )

    # Load source files
    target_path = Path(cfg.test_article)
    if not target_path.is_absolute():
        target_path = REPO_ROOT / target_path
    # plan-C: swap to a per-run working copy (seeded if configured) so
    # promoted fixes accumulate and the error space can exhaust. No-op
    # (returns the same path) when apply_fixes_back_enabled is False.
    target_path = _apply_back_setup(cfg, target_path, logs_dir)
    target_text = target_path.read_text(encoding="utf-8")
    try:
        target_rel = target_path.relative_to(REPO_ROOT)
    except ValueError:
        target_rel = target_path

    # ── A1/A2: classify the target, then FORCE the machinery to match it ──────
    # Raises TargetKindMismatch and stops the run if the config declared a kind
    # that disagrees with what is on disk. Runs unconditionally: there is no
    # switch that turns this off, because the launcher has silently dropped six
    # config keys and a safety property behind a droppable key is not enforced.
    target_kind, target_kind_reason = resolve_target_kind(
        str(target_path), target_text, declared=(cfg.target_kind or None))
    _log(f"  Target kind: {target_kind} ({target_kind_reason})")

    # A9 (panel-converged MUST list): refuse before the first paid dispatch.
    _refusals = preflight_target_machinery(cfg, target_path, target_kind)
    if _refusals:
        for _r in _refusals:
            _log(f"  *** LAUNCH REFUSED: {_r}")
        raise LaunchRefused(
            f"{len(_refusals)} precondition(s) failed for target {target_path} "
            f"(kind={target_kind}): " + " | ".join(_refusals))
    sk_forced_off = False
    if target_kind != TARGET_KIND_PYTHON and cfg.sk_enabled:
        # Not a warning — an override. S_k over prose does not merely fail to
        # help; it inverts. Measured on the 2026-08-01 control: a fix injecting
        # a shell-injection call into a fenced listing scored sk=1.0000
        # ADMISSIBLE while a correct prose fix scored 0.6667, because ruff's
        # markdown baseline made the delta a measure of added English and
        # bandit — unable to parse the file at all — reported a clean bill at
        # the heaviest weight. compute_sk short-circuits to NO_SCORE anyway;
        # switching the pipeline off here additionally skips the baseline
        # capture, whose ~2752 phantom ruff diagnostics were the input to that
        # inversion.
        sk_forced_off = True
        cfg = replace(cfg, sk_enabled=False)
        _log("  *** S_k pipeline FORCED OFF: sk_enabled=true in config, but the "
             "target is not a Python module. S_k is defined over Python source; "
             "on prose its gates cannot fail and its ranking inverts. Findings "
             "on this target resolve through the falsifier path. ***")

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

    # Burst decomposition planning
    burst_plan = None
    burst_state: Optional[Dict[str, Any]] = None
    context_chars = sum(len(p) for p in context_parts)

    if cfg.burst_mode != "off":
        from bench.burst_planner import (
            should_burst, plan_phases, build_phase_code,
            build_integration_code, build_findings_summary,
            phase_convergence_overrides, integration_convergence_overrides,
            extract_signatures,
        )
        need_burst = cfg.burst_mode == "on"
        burst_reason = "burst_mode=on" if need_burst else ""

        if not need_burst:
            need_burst, burst_reason = should_burst(
                len(target_text), context_chars,
                MODEL_SPECS, INITIAL_FINGERPRINTS, sorted(baseline),
            )

        if need_burst:
            burst_plan = plan_phases(
                target_text, MODEL_SPECS, INITIAL_FINGERPRINTS,
                sorted(baseline), str(target_rel),
            )
            # Context file signatures for integration round
            ctx_sigs = ""
            for ctx_path in context_paths:
                try:
                    ctx_text = ctx_path.read_text(encoding="utf-8")
                    ctx_sigs += (
                        f"# === {ctx_path.name} ===\n"
                        + extract_signatures(ctx_text) + "\n"
                    )
                except Exception:
                    pass

            burst_state = {
                "phase_idx": 0,
                "phase_round_offset": 0,
                "phase_findings": {},  # {phase_name: findings_summary}
                "integration_started": False,
                "integration_done": False,
                "original_cfg_overrides": {},
                "context_signatures": ctx_sigs,
            }
            _log(f"\n  BURST MODE: {burst_reason}")
            _log(f"  Phases: {len(burst_plan.phases)} + integration round")
            _log(f"  Budget: {burst_plan.budget_chars_per_phase:,} chars/phase")
            _log(f"  Signatures: {len(burst_plan.signatures):,} chars")
            for p in burst_plan.phases:
                sections = [s.name for s in p.sections]
                _log(f"    Phase {p.index}: {p.name} "
                     f"({p.char_count:,} chars, {len(sections)} sections)")

            # Override full_code and base_prompt for first phase
            phase = burst_plan.phases[0]
            full_code = build_phase_code(
                phase, str(target_rel), burst_plan.signatures)
            _log(f"\n  Starting Phase 0: {phase.name}")

            # Apply Phase 0 convergence overrides at initialisation —
            # without this, Phase 0 runs with base config thresholds
            # and can consume the entire round budget.
            overrides = phase_convergence_overrides(0)
            cfg = replace(cfg, **overrides)
            _log(f"  Phase 0 overrides: earliest_stop={overrides['earliest_stop_round']}, "
                 f"rho_earliest={overrides['rho_earliest_round']}")

    # Build DynamicManager
    dm_config = DynamicManagementConfig(
        # Decomposition is now fingerprint-aware (13 April 2026):
        # _should_decompose() uses per-model observed prompt limits from
        # fingerprints, falling back to LENGTH_THRESHOLD (80K) when no
        # observation data exists. This set is for immune escalation only.
        pre_decompose_models=set(),
        no_exclusion_mode=True,
    )
    dm_config.max_rounds = cfg.max_rounds
    dm_config.domain = cfg.domain  # Exp 39 plumbing fix: propagate domain to InsectBrain → immune pipeline
    model_specs = build_model_specs(exp_config)
    mgr = DynamicManager(model_specs, dm_config)

    # Insect Brain
    brain = InsectBrain(config=dm_config, logs_dir=logs_dir, source_paths=source_paths_str)
    brain.initialise(model_labels=sorted(baseline))

    # Endocrine Layer
    endo = EndocrineLayer(source_paths=source_paths_str, test_cmd=None, max_fix_evals=20)

    # Finding registry
    registry = FindingRegistry()
    # The registry renders the panel's state-machine briefing every round;
    # what it says about how a finding settles depends on the target.
    registry.target_kind = target_kind

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
    # Dual-series γ report (panel redesign 2026-05-23): all-severity and
    # critical-only decay, both reported each round, neither gates.
    gamma_all_history: List[float] = []
    gamma_critical_history: List[float] = []
    gate_history: List[bool] = []
    open_ch_history: List[int] = []
    stall_history: List[Dict[str, int]] = []
    # Exp 40 fix 1A.3: track novel CRITICAL count per round for γ-alt gate.
    novel_critical_history: List[int] = []
    # Code-location novelty series (2026-06-08): per-round critical-novelty keyed by target
    # code location. REPLACES the ID-proxy series in novel_critical_history whenever
    # cfg.location_keyed_convergence is set; telemetry only when it is not.
    location_crit_history: List[int] = []
    try:
        from bench.convergence_location import target_symbols as _loc_target_symbols
        # Use the RAW target source (target_text), NOT full_code — full_code is the
        # wrapped review prompt ("=== TARGET FILE ... ===\n<src>"), which is not valid
        # Python and silently yielded zero symbols (the location key was inactive in every
        # real run until this was caught, 2026-06-09). Fail LOUD, never silent.
        _loc_symbols = _loc_target_symbols(target_text)
        if not _loc_symbols:
            _loc_symbols = _loc_target_symbols(str(target_path))  # path-mode fallback
        if not _loc_symbols:
            _log("  [location-key] WARNING: 0 symbols extracted from target — "
                 "location-keyed convergence/shadow is INACTIVE this run")
        else:
            _log(f"  [location-key] {len(_loc_symbols)} target symbols extracted; "
                 f"location_keyed_convergence={getattr(cfg, 'location_keyed_convergence', False)}")
    except Exception as _ls_exc:
        _loc_symbols = frozenset()
        _log(f"  [location-key] WARNING: symbol extraction failed ({_ls_exc}) — "
             "location-keyed convergence/shadow INACTIVE this run")
    consecutive_churn_rounds: int = 0  # D1: tracks sustained churn for phase transition
    # Exp 40 1D.3: per-model rho tracking for targeted ITC decisions.
    # Each list holds one entry per completed round for that model. Missing
    # rounds are zero-filled when the model produced no findings that round.
    novelty_counts_per_model: Dict[str, List[int]] = {}
    raw_counts_per_model: Dict[str, List[int]] = {}
    # Exp 40 1E.9: per-finding prior-round alternatives for cross-round
    # recidivism detection. Keyed by finding_id; value is the most recent
    # round's parsed alternatives. Consumed by build_divergence_record via
    # check_sibling_admissibility on the next round's build.
    prior_round_alternatives_by_finding: Dict[str, List[Any]] = {}

    if cfg.resume and brain.load_checkpoint():
        start_round = brain.state.current_round + 1
        # Partial-round contamination guard (Exp 43 lesson, 2026-07-22): the
        # 18 July OpenRouter-402 cascade left a checkpoint whose last "completed"
        # round held responses from only 2 of 5 models; a naive resume would have
        # built the next round on a broken panel round. The per-round response
        # files r{N}_{model}_*.json are the ground truth of who actually
        # responded — verify the last completed round has one per configured
        # model, and REFUSE the resume (fail loud, founder decides) otherwise.
        try:
            _last = brain.state.current_round
            _expected = {m.lower() for m in
                         (cfg.models if isinstance(cfg.models[0], str)
                          else [getattr(m, "label", str(m)) for m in cfg.models])}
            _expected |= {str(m).lower() for m in
                          getattr(brain.state, "active_models", []) or []}
            _seen = set()
            for _p in brain.logs_dir.glob(f"r{_last}_*_*.json"):
                _parts = _p.name.split("_")
                if len(_parts) >= 3:
                    _seen.add(_parts[1].lower())
            _missing = _expected - _seen
            if _missing:
                raise RuntimeError(
                    f"checkpoint round {_last} is PARTIAL — no response file for: "
                    f"{sorted(_missing)}. Refusing to resume on a contaminated "
                    f"round; re-run from scratch or repair the checkpoint."
                )
        except RuntimeError:
            raise
        except Exception as _grd_exc:  # noqa: BLE001 — guard must not break legacy resumes
            _log(f"  WARNING: partial-round guard inconclusive ({_grd_exc}); "
                 f"verify round {brain.state.current_round} coverage manually")
        _log(f"  RESUMED from round {start_round}")
        runner_ckpt = brain.logs_dir / "runner_state.json"
        if runner_ckpt.exists():
            try:
                ckpt_data = json.loads(runner_ckpt.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as _ckpt_err:
                _log(f"  WARNING: runner_state.json corrupted ({_ckpt_err}), "
                     f"falling back to brain checkpoint only")
                ckpt_data = {}
            registry = FindingRegistry.from_dict(ckpt_data.get("registry", {}))
            novelty_counts = ckpt_data.get("novelty_counts", [])
            raw_counts = ckpt_data.get("raw_counts", [])
            rho_history = ckpt_data.get("rho_history", [])
            gamma_history = ckpt_data.get("gamma_history", [])
            gate_history = ckpt_data.get("gate_history", [])
            open_ch_history = ckpt_data.get("open_ch_history", [])
            stall_history = ckpt_data.get("stall_history", [])
            novel_critical_history = ckpt_data.get("novel_critical_history", [])
            cumulative_context_chars = ckpt_data.get("cumulative_context_chars", 0)
            consecutive_churn_rounds = ckpt_data.get("consecutive_churn_rounds", 0)
            # Exp 40 1D.3: restore per-model rho history
            _pm_novel = ckpt_data.get("novelty_counts_per_model", {})
            if isinstance(_pm_novel, dict):
                novelty_counts_per_model = {
                    str(k): [int(x) for x in v] for k, v in _pm_novel.items()
                }
            _pm_raw = ckpt_data.get("raw_counts_per_model", {})
            if isinstance(_pm_raw, dict):
                raw_counts_per_model = {
                    str(k): [int(x) for x in v] for k, v in _pm_raw.items()
                }
            # R39-06: Restore ITC module state for quality tracking continuity
            _restored_itc = ckpt_data.get("itc_model_state")
            if _restored_itc and isinstance(_restored_itc, dict):
                _itc_model_state.clear()
                _itc_model_state.update(_restored_itc)
            _restored_hil = ckpt_data.get("itc_hil_flags")
            if _restored_hil and isinstance(_restored_hil, list):
                _itc_hil_flags.clear()
                _itc_hil_flags.extend(_restored_hil)
            # R39-04: Restore burst_state if it was persisted
            _restored_burst = ckpt_data.get("burst_state")
            if _restored_burst and isinstance(_restored_burst, dict):
                burst_state = _restored_burst
                _log(f"  Burst state restored: phase_idx={burst_state.get('phase_idx', 0)}")
            _log(f"  Registry restored: {len(registry.entries)} entries")

    experiment_start = time.monotonic()

    # Exp 40 timing re-confer (2026-05-16): reset the observation-only
    # finding-ID collision accumulator at experiment start so the
    # post-mortem reads only this run's collisions. This is the
    # evidence gate for the deferred UUID-namespace decision (Q2,
    # 2026-05-16 neutral confer → Exp 41). Not restored from
    # checkpoint: a --resume should report the resumed leg's
    # collisions, not stale ones.
    _feedback_mod._finding_id_collisions.clear()

    # Secondary-route fallback accumulators cleared at experiment start
    # (mirrors _finding_id_collisions: per-run scope, not restored from
    # checkpoint — a --resume should report only the resumed leg's
    # fallback usage). 2026-05-22, founder-directed.
    _secondary_route_usage.clear()
    _persistent_empty_flags.clear()

    # G7 merge-arbitration context setup (Exp 40 continuation). Inert
    # unless cfg.merge_arbitration_enabled. When enabled, the panel +
    # a short-prompt dispatch wrapper are registered in module state so
    # _try_merge_arbitration (called from _update_finding_statuses) and
    # the round-level tie-breaker can reach the models without
    # threading dispatch infra through the status-updater signature.
    # In-round re-ask (plan-B): set the module mirror from cfg at
    # experiment start (mirrors the _merge_arb_ctx pattern below).
    _INROUND_REASK["enabled"] = bool(
        getattr(cfg, "inround_reask_enabled", False))
    _INROUND_REASK["min_markers"] = int(
        getattr(cfg, "inround_reask_min_markers", 2))
    if _INROUND_REASK["enabled"]:
        _log(f"  in-round re-ask ENABLED (min_markers="
             f"{_INROUND_REASK['min_markers']})")

    # Exp 52 factorial — directive-section selection (2026-07-29).
    arm_directive_omission(cfg, exp_config)

    _merge_arb_ctx.clear()
    if getattr(cfg, "merge_arbitration_enabled", False):
        def _arb_dispatch(mc, prompt: str):
            # Arbitration queries are short + self-contained; send a
            # minimal system prompt rather than the full CDSFL text so
            # the call stays cheap. Bounded wall clock.
            return dispatch_to_model(
                mc, prompt,
                "You are a careful code-review panelist. Answer "
                "exactly as instructed.",
                wall_clock_limit=getattr(mc, "timeout", 120) * 2,
            )
        _merge_arb_ctx.update({
            "enabled": True,
            "panel": list(exp_config.models),
            "dispatch_fn": _arb_dispatch,
            "min_defer_count": getattr(
                cfg, "merge_arbitration_min_defer_count", 2),
            "max_per_round": getattr(
                cfg, "merge_arbitration_max_per_round", 3),
            "tiebreaker_gamma": getattr(
                cfg, "merge_arbitration_tiebreaker_gamma", 0.05),
            "majority": 3,
            "used_this_round": 0,
            "log": [],
        })
        _log(f"  G7 merge-arbitration ENABLED "
             f"(min_defer={_merge_arb_ctx['min_defer_count']}, "
             f"max/round={_merge_arb_ctx['max_per_round']}, "
             f"tiebreaker_γ<{_merge_arb_ctx['tiebreaker_gamma']})")

    effective_max = cfg.max_rounds
    loop_cap = cfg.extension_cap
    # Burst mode: extend loop cap to accommodate all phases + integration
    if burst_plan:
        phase_rounds_each = 8  # generous per-phase budget
        burst_total = (len(burst_plan.phases) + 1) * phase_rounds_each
        loop_cap = max(loop_cap, burst_total)
        effective_max = max(effective_max, burst_total)
        _log(f"  Burst loop cap: {loop_cap} rounds "
             f"({len(burst_plan.phases)} phases × {phase_rounds_each} + integration)")
    extended = False
    rho_avg = 1.0
    rho_churn = False

    # S_k baseline capture (before any fixes are applied)
    sk_baseline: Dict[str, Any] = {}
    if cfg.sk_enabled:
        _log("  S_k pipeline: capturing baseline gate scores...")
        sk_baseline = _capture_baseline(target_text, source_path=str(target_path))
        _log(f"  S_k baseline: ruff={sk_baseline.get('ruff_violations', '?')}, "
             f"bandit={sk_baseline.get('bandit_findings', '?')}")

    # ── IMMUNE MEMORY consumption (2026-07-31). The memory has RECORDED since
    # Exp 47 and fed nothing. Loading it HERE — at run start, before any round —
    # is what makes the appendix §1.5 blended prior available as the §1.1
    # initial condition R_k(0) = π_k for every finding this run evaluates.
    # A load failure degrades to the uniform prior and never kills the run.
    rk0_prior, rk0_priors_used = _build_rk0_prior(cfg)

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

    def _build_prompt(code_payload: str, artifact_label: str = "") -> str:
        """Build base prompt from awareness preamble + code payload."""
        label = artifact_label or f"{target_rel} + Context"
        return (
            f"{awareness_preamble}"
            f"YOUR TASK:\n"
            f"Review {target_rel} under full CDSFL + FFF constraints.\n\n"
            f"For each finding, provide (keys in this exact order):\n"
            f"  FINDING_ID: unique identifier (e.g., F001). IMPORTANT: your "
            f"finding IDs must be STABLE across rounds. If you filed F001 in "
            f"Round 3, F001 in Round 4 must refer to the same bug.\n"
            f"  SEVERITY: 0.0 to 1.0 (1.0 = critical)\n"
            f"  FLAW_CLASS: integer category (1=logic, 2=interface, 3=notation, "
            f"4=completeness, 5=correctness, 6=edge-case, 7=performance, "
            f"8=documentation)\n"
            f"  ABSTRACTION_INDEX: 0.0 to 1.0 (0=surface, 1=architectural)\n"
            f"  FIND: what is wrong, where, and what is the evidence\n"
            f"  FOLLOW: trace downstream consequences BEFORE proposing a fix\n"
            f"  ANALYSE: classify constraint as HARD or SOFT. State premises "
            f"explicitly, derive conclusion through concrete evidence "
            f"(Meta Structured Reasoning Protocol). "
            f"State CONFIRMED/UNCERTAIN/REJECTED.\n"
            f"  FIX: the simplest sufficient correction addressing root cause "
            f"AND FOLLOW consequences (for CONFIRMED findings only). Express "
            f"as SEARCH/REPLACE blocks so S_k can verify:\n"
            f"    <<<< SEARCH file_path\n"
            f"    [exact current content to replace — copy verbatim from source]\n"
            f"    ====\n"
            f"    [exact replacement content]\n"
            f"    >>>> REPLACE\n"
            f"  FALSIFICATION: (MANDATORY) state the FALSIFIER (what would "
            f"disprove your FIND), your ATTEMPT to satisfy it, and the RESULT. "
            f"Then try to break your FIX. Findings without this section "
            f"will be rejected.\n"
            f"  CORROBORATION: (MANDATORY) compute your residual risk R_k "
            f"using the self-assessment equation in the operational directive. "
            f"Show R_old, your numerical estimates for η, d, p, S_k, ν_eff, "
            f"and the resulting R_k. Qualitative-only assessment will be "
            f"flagged. Example format:\n"
            f"    R_old=0.50, η=0.80, d=0.70, p=0.60, S_k=0.75, ν_eff=0.15\n"
            f"    R_k = 0.50 × (1 - 0.80×0.70×0.60) × 0.75 + 0.15 = 0.32\n"
            f"  ADMISSIBILITY: (MANDATORY, FFAFP §15) state PASS/FAIL for "
            f"each of S_min, G-completeness, d_tool, σ_measured, q_retest. "
            f"Example format:\n"
            f"    S_min: PASS (location=bench/foo.py:42, mechanism=off-by-one, "
            f"evidence=test_case_7)\n"
            f"    G-completeness: PASS (verifier can reproduce from finding text)\n"
            f"    d_tool: PASS (pytest ran, 4 of 5 tests caught the class)\n"
            f"    σ_measured: PASS (pre-fix: 1 failure; post-fix: 0 failures)\n"
            f"    q_retest: PASS (η from similarity, d from pytest, p from domain)\n"
            f"  NOVELTY: (MANDATORY, Stage 6 §16) state (ν_k, c_ext, H/H_max) "
            f"as three independent scores. Do not collapse them. If you did "
            f"not perform an external search, set c_ext = 0 explicitly. "
            f"Example format:\n"
            f"    ν_k: 0.85 — searched arXiv for 'X in Y'; no matches for "
            f"this specific mechanism\n"
            f"    c_ext: 0.60 — arXiv + Semantic Scholar; Google Scholar skipped\n"
            f"    H/H_max: 0.75 — abstraction level is high (architectural)\n"
            f"    Citations: arXiv:2502.09858, 10.1234/example\n"
            f"  VERIFIED: TRUE if proven, FALSE if assertion\n\n"
            f"PRIOR REVIEW CONTEXT: Do not re-report issues already present "
            f"in the registry summary. Duplicate findings waste compute. "
            f"Focus on genuinely new issues and regressions.\n\n"
            f"Produce ALL findings. Do not hold back.\n\n"
            f"=== ARTIFACT: {label} ({len(code_payload):,} chars) ===\n\n"
            f"{code_payload}\n\n"
            f"=== END ARTIFACT ===\n\n"
            f"Produce your findings now."
        )

    base_prompt = _build_prompt(full_code)

    result: Dict[str, Any] = {
        "experiment": cfg.experiment_name,
        "topology": cfg.topology,
        "relay_mode": cfg.relay_mode if cfg.topology == "relay" else None,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "pattern": cfg.pattern,
        "models": sorted(baseline),
        "target_file": str(target_rel),
        # A1: what the harness decided the target IS, why, what the config
        # claimed, and whether that decision overrode the requested machinery.
        # In the report because a reader must be able to tell a run that scored
        # its fixes from one that could not, without re-deriving it.
        "target_kind": {
            "kind": target_kind,
            "reason": target_kind_reason,
            "declared_in_config": cfg.target_kind or None,
            "sk_enabled_requested": bool(sk_forced_off) or bool(cfg.sk_enabled),
            "sk_enabled_effective": bool(cfg.sk_enabled),
            "sk_forced_off_by_target_kind": sk_forced_off,
        },
        "context_files": [str(p) for p in cfg.context_files],
        "max_rounds": cfg.max_rounds,
        "extension_cap": cfg.extension_cap,
        "domain": cfg.domain,
        # A completed report must say WHICH rule closed the run and on WHICH
        # series. Until 2026-07-31 it recorded four keys, none of them the
        # counting rule: `convergence_reason` quoted the zero tail but not what
        # produced it, and the location-keyed series was written under
        # `location_crit_shadow_history` — still calling itself *shadow* — in
        # runs where the config had promoted it to gating. Determining which
        # rule closed a finished experiment meant going back to the launch
        # config. Every key below is now here so the report is self-describing
        # on the single most important input to its own verdict.
        "convergence_config": {
            "earliest_stop": cfg.earliest_stop_round,
            "consecutive_required": cfg.consecutive_rounds_required,
            "rho_threshold": cfg.rho_threshold,
            "rho_rolling_window": cfg.rho_rolling_window,
            # WHICH SERIES the zero-tail was counted on. `location_keyed` counts
            # a critical as new only if it names a code location not previously
            # flagged — which cannot see a second distinct defect in an
            # already-flagged function. `settled_id` is the older per-finding
            # series. This is the difference between "no new criticals" and "no
            # new criticals at previously unflagged locations", and a reader
            # cannot tell them apart without this key.
            "critical_series": ("location_keyed"
                               if getattr(cfg, "location_keyed_convergence", False)
                               else "settled_id"),
            "location_keyed_convergence": bool(
                getattr(cfg, "location_keyed_convergence", False)),
            # The two-sided gate's own parameters (γ side and count side).
            "gamma_alt_threshold": getattr(cfg, "gamma_alt_threshold", None),
            "gamma_alt_consecutive_zero_crit": getattr(
                cfg, "gamma_alt_consecutive_zero_crit", None),
            "gamma_alt_earliest_round": getattr(cfg, "gamma_alt_earliest_round", None),
            "hardened_gate_enabled": bool(getattr(cfg, "hardened_gate_enabled", False)),
            "critical_severity_threshold": CRITICAL_SEVERITY_THRESHOLD,
            # Named limitation, carried in the record rather than in a note that
            # travels separately from it.
            "known_limitation": (
                "location-keyed counting cannot distinguish a second distinct "
                "defect in an already-flagged function from a re-find, so a "
                "zero tail means 'no new criticals at previously unflagged "
                "locations'. Fired at the closing round in Exp 45 (C0031) and "
                "Exp 47 (C0070). See bench/audit_closing_window.py."
                if getattr(cfg, "location_keyed_convergence", False) else None),
        },
        # Exp 52 factorial: which experimental factors were on, and — when a
        # factor was off — which reading of "off" the cell actually used.
        # Recorded per run so a result file is self-describing and cells can
        # be compared without re-deriving anything from the config.
        "directive_factors": {
            _f: {
                "enabled": bool(getattr(cfg, DIRECTIVE_FACTOR_FIELDS[_f][0], True)),
                "off_mode": getattr(cfg, DIRECTIVE_FACTOR_FIELDS[_f][1], "absent"),
                "directive_text_present": _directive_factor_state(cfg, _f)[0],
                "runner_pass_active": _directive_factor_state(cfg, _f)[1],
            }
            for _f in DIRECTIVE_FACTOR_FIELDS
        },
        "rounds": [],
    }

    # Feedback channel state — populated at end of round K, consumed at start
    # of round K+1. cdsfl_operational.md §17. See bench/dm/_feedback.py for
    # the constructor; this variable holds the rendered per-model sections.
    feedback_sections_for_next_round: Dict[str, str] = {}
    # Runner-pass halves of the two experimental factors. Under the default
    # "absent" off-mode these follow the *_enabled switch exactly; the
    # narrower off-modes split text from pass (see RunnerConfig).
    feedback_enabled = _directive_factor_state(cfg, "feedback")[1]
    divergence_pass_enabled = _directive_factor_state(cfg, "divergence")[1]

    # Exp 40 fix 1D.5 — S_k SEARCH/REPLACE format pre-check.
    # Populated at end of round K with (canonical_id, diagnostic_reason)
    # pairs for findings whose proposed_fix did not parse as an S_k block.
    # Consumed at start of round K+1 as a reformat-request prompt section.
    sk_reformat_requests_for_next_round: List[Tuple[str, str]] = []

    # Ouroboros loop-close (2026-07-31). The cell runs BETWEEN rounds, so the
    # literature it retrieves after round K is what round K+1 sees — the
    # one-round lag is the cell's original design, not a compromise. Empty
    # string means "inject nothing", which is the OFF path and also the
    # "on, but nothing relevant came back" path: identical bytes either way.
    ouroboros_brief_section_for_next_round: str = ""
    # (c_ext, per-finding nu_k) from the Stage 6 calibrator's read of that same
    # retrieval, consumed by the S_k -> R_k channel later in the SAME round the
    # shadow cells run (shadow cells at 6666, S_k at 6681).
    ouroboros_rk_inputs: Dict[str, Any] = {}

    # ── Main loop ──
    for round_idx in range(start_round, loop_cap):
        if round_idx >= effective_max:
            break

        # G7: reset the per-round arbitration dispatch budget.
        if _merge_arb_ctx:
            _merge_arb_ctx["used_this_round"] = 0

        round_start = time.monotonic()
        wall_elapsed = round_start - experiment_start
        if wall_elapsed > cfg.wall_clock_cap_s:
            _log(f"\nWALL CLOCK CAP reached ({wall_elapsed:.0f}s). Stopping.")
            break

        _log(f"\n{'---' * 20}")
        round_type = "blind" if round_idx == 0 else "adaptive"
        _log(f"Round {round_idx}/{effective_max - 1} ({round_type})")
        _log(f"{'---' * 20}")

        # plan-C: promote the prior round's fully-closed fixes into the
        # working copy (full-suite gated, cumulative, idempotent) and
        # rebuild full_code so THIS round reviews the repaired artefact.
        # Loop-top placement avoids the many mid-body exit paths.
        if _APPLY_BACK_CTX.get("enabled") and round_idx > start_round:
            _new_src = _apply_back_promote(registry, round_idx - 1)
            if _new_src is not None:
                full_code = (
                    f"=== TARGET FILE (REVIEW THIS): {target_rel} "
                    f"({len(_new_src):,} chars) ===\n{_new_src}\n\n"
                    + "\n\n".join(context_parts)
                )
                _log(f"  apply-back: artefact repaired — "
                     f"{len(_APPLY_BACK_CTX['applied'])} fix(es) applied, "
                     f"{len(_APPLY_BACK_CTX['rejected'])} rejected; "
                     f"full_code rebuilt for round {round_idx}")

        # Update relay budgets from fingerprint data before dispatch.
        # Each model's budget adapts to its measured prompt performance.
        for _bl in cfg.models:
            brain.config.context_budget_overrides[_bl] = (
                get_effective_context_budget(_bl, observed_fingerprints)
            )

        # Dispatch — topology-dependent
        if cfg.topology == "relay":
            # Exp 40 fix 1D.5: attach S_k reformat requests to the relay
            # base_prompt so they reach every relay hop. Star branch injects
            # via registry_summary below; relay has no registry_summary slot.
            _relay_prompt = base_prompt
            if sk_reformat_requests_for_next_round:
                _sk_reformat = build_sk_reformat_requests(
                    sk_reformat_requests_for_next_round,
                )
                if _sk_reformat:
                    _relay_prompt = _sk_reformat + "\n\n" + base_prompt
            # Ouroboros brief from round K-1 rides ahead of the base prompt so
            # it reaches every relay hop, same slot as the S_k reformat request.
            if ouroboros_brief_section_for_next_round:
                _relay_prompt = (
                    ouroboros_brief_section_for_next_round + _relay_prompt)
            findings, responses, per_model_durations, prompt_lengths = _dispatch_round_relay(
                exp_config, mgr, brain, _relay_prompt, cdsfl_text, full_code,
                round_idx, cfg, registry=registry,
            )
        else:
            registry_summary = registry.build_summary(round_idx) if round_idx > 0 else ""
            # Per-round metrics injection — models use γ, ρ, registry state to
            # calibrate effort (cdsfl_operational.md §8, §13). Mirrors Exp 37
            # run_exp37_evidence.py lines 2310-2359.
            if round_idx > 0 and registry is not None:
                _rho_val = rho_history[-1] if rho_history else 0.0
                _rho_bar3 = (sum(rho_history[-3:]) / min(3, len(rho_history))
                             if rho_history else 0.0)
                _gamma_val = gamma_history[-1] if gamma_history else 0.0
                _n_open = sum(1 for e in registry.entries.values()
                              if e.get("status") in ("OPEN", "CONTESTED"))
                _n_confirmed = sum(1 for e in registry.entries.values()
                                   if e.get("status") == "CONFIRMED")
                _n_closed = sum(1 for e in registry.entries.values()
                                if e.get("status") in ("CLOSED", "MERGED"))
                _metrics = (
                    f"\n=== PANEL METRICS (Round {round_idx}) ===\n"
                    f"ρ (discovery efficiency / semantic novelty rate) = "
                    f"{_rho_val:.3f}\n"
                    f"ρ̄₃ (3-round rolling average) = {_rho_bar3:.3f}\n"
                    f"γ (Duane reliability growth) = {_gamma_val:.3f}\n"
                    f"Registry: {_n_open} OPEN, {_n_confirmed} CONFIRMED, "
                    f"{_n_closed} CLOSED/MERGED\n"
                    f"\nInterpretation: "
                )
                if _gamma_val >= 0.45:
                    _metrics += (
                        "Strong depletion — novel discoveries are rare. If you "
                        "cannot find genuinely new issues, report that honestly. "
                        "Redundant re-descriptions waste compute.\n"
                    )
                elif _gamma_val >= 0.30:
                    _metrics += (
                        "Moderate depletion — novel discoveries are slowing. "
                        "Focus on areas not yet covered by existing findings. "
                        "Check the registry before submitting.\n"
                    )
                else:
                    _metrics += (
                        "Productive phase — continue finding and falsifying.\n"
                    )
                # Semantic novelty feedback — 3 graduated signals
                # (Ported from run_exp37_evidence.py lines 2354-2371)
                if _rho_val >= 0.5:
                    _metrics += (
                        f"High semantic novelty (ρ={_rho_val:.3f}). Your recent "
                        f"findings are genuinely new. Continue this trajectory.\n"
                    )
                elif _rho_val > 0.0 and _gamma_val >= 0.30:
                    _metrics += (
                        f"Moderate novelty (ρ={_rho_val:.3f}) with depletion "
                        f"(γ={_gamma_val:.3f}). Concentrate on unexplored areas "
                        f"and deeper structural issues.\n"
                    )
                # ρ̄₃ redundancy warning
                if _rho_bar3 < 0.25 and round_idx >= 3:
                    _metrics += (
                        f"⚠ HIGH REDUNDANCY (ρ̄₃={_rho_bar3:.3f}). Your last 3 "
                        f"rounds averaged <25% novelty. Most findings are "
                        f"duplicating existing registry entries. Check the "
                        f"registry carefully before submitting.\n"
                    )
                _metrics += "=== END METRICS ===\n\n"
                registry_summary = _metrics + registry_summary

            # Exp 40 fix 1D.1 / 1D.2 / 1D.4: inject round-context helpers.
            # Consolidation preamble fires during the final
            # cfg.consolidation_rounds rounds. Prior-fix summary lists
            # closed canonical entries so models do not re-surface them.
            # Windowed context compresses older rounds into a one-line
            # summary for long runs.
            _context_prefix = ""
            _consolidation = build_consolidation_preamble(
                round_idx=round_idx,
                max_rounds=effective_max,
                consolidation_rounds=cfg.consolidation_rounds,
            )
            if _consolidation:
                _context_prefix += _consolidation
            if cfg.prior_fix_summary_enabled:
                _fix_summary = build_prior_fix_summary(
                    registry=registry,
                    round_idx=round_idx,
                    max_entries=cfg.prior_fix_summary_max_entries,
                    max_chars=cfg.prior_fix_summary_max_chars,
                )
                if _fix_summary:
                    _context_prefix += _fix_summary
            if cfg.windowed_context_enabled and result.get("rounds"):
                _window = build_windowed_context(
                    per_round_summaries=result["rounds"],
                    round_idx=round_idx,
                    window_full_rounds=cfg.windowed_context_full_rounds,
                    max_chars=cfg.windowed_context_max_chars,
                )
                if _window:
                    _context_prefix += _window
            # Exp 40 fix 1D.5: S_k reformat request — rendered at round K+1
            # from round K's pre-check results. Non-empty only when prior
            # round emitted unparseable proposed_fix entries.
            if sk_reformat_requests_for_next_round:
                _sk_reformat = build_sk_reformat_requests(
                    sk_reformat_requests_for_next_round,
                )
                if _sk_reformat:
                    _context_prefix += _sk_reformat + "\n\n"
            # Ouroboros brief from round K-1. Rides in the same context prefix
            # as the consolidation/fix-summary/window blocks, which _make_prompt
            # splices in immediately before "=== ARTIFACT:" — so it lands inside
            # the dispatched prompt, ahead of the code under review.
            if ouroboros_brief_section_for_next_round:
                _context_prefix += ouroboros_brief_section_for_next_round
            if _context_prefix:
                registry_summary = _context_prefix + registry_summary

            findings, responses, per_model_durations, prompt_lengths = _dispatch_round_star(
                exp_config, mgr, brain, base_prompt, registry_summary,
                cdsfl_text, full_code, round_idx, cfg, registry=registry,
                feedback_sections=(
                    feedback_sections_for_next_round if feedback_enabled else None
                ),
            )

        # Safety check
        problem = _safety_check(responses)
        if problem:
            _log(f"\n*** ALL MODELS FAILED: {problem} ***")
            result["terminated"] = problem
            break

        # R_k recomputation validation (advisory)
        rk_validation = validate_round_rk(findings, responses)
        rk_summary = {
            model: {s: sum(1 for _, st, _, _ in res if st == s)
                    for s in ("PASS", "WARN", "FAIL", "SKIP")}
            for model, res in rk_validation.items()
        }
        for model, counts in rk_summary.items():
            parts = []
            for s in ("PASS", "WARN", "FAIL", "SKIP"):
                if counts.get(s, 0):
                    parts.append(f"{s}={counts[s]}")
            if parts:
                _log(f"  R_k validation [{model}]: {', '.join(parts)}")

        # Register findings
        novel_this_round = 0
        novel_critical_this_round = 0  # Exp 40 1A.3: severity >= 0.7
        # Exp 40 fix 1D.5: collect findings whose proposed_fix is non-empty
        # but does not parse as an S_k block. Fed to next round as a
        # reformat-request prompt section.
        sk_reformat_requests_for_next_round = []
        # Exp 40 1D.3: per-model counters for this round (novel + raw).
        per_model_novel_this_round: Dict[str, int] = {}
        per_model_raw_this_round: Dict[str, int] = {}
        for f in findings:
            per_model_raw_this_round[f.model_id] = (
                per_model_raw_this_round.get(f.model_id, 0) + 1
            )
            existing = registry.lookup_alias(f.model_id, f.finding_id)
            if existing is None:
                cid = registry.register(f, f.model_id)
                novel_this_round += 1
                per_model_novel_this_round[f.model_id] = (
                    per_model_novel_this_round.get(f.model_id, 0) + 1
                )
                if getattr(f, "severity", 0.0) >= 0.7:
                    novel_critical_this_round += 1
                # 1D.5 pre-check: only for novel findings with a proposed fix.
                fix_text = getattr(f, "proposed_fix", "") or ""
                if fix_text.strip():
                    ok, reason = check_sk_format_admissible(fix_text)
                    if not ok:
                        sk_reformat_requests_for_next_round.append((cid, reason))
            else:
                registry.add_verdict(existing, f.model_id, "CONFIRM", round_idx)

        novelty_counts.append(novel_this_round)
        novel_critical_history.append(novel_critical_this_round)  # Exp 40 1A.3
        raw_counts.append(len(findings))
        # Exp 40 1D.3: extend per-model history arrays with this round's
        # tally. All known models (from baseline plus any new emitters)
        # receive an entry so the arrays stay aligned across rounds.
        _models_this_round = (
            set(baseline)
            | set(per_model_novel_this_round)
            | set(per_model_raw_this_round)
        )
        for _label in _models_this_round:
            novelty_counts_per_model.setdefault(_label, []).append(
                per_model_novel_this_round.get(_label, 0),
            )
            raw_counts_per_model.setdefault(_label, []).append(
                per_model_raw_this_round.get(_label, 0),
            )

        # A2: Rho
        rho_current, rho_avg, rho_churn = _compute_rho(novelty_counts, raw_counts, cfg)
        rho_history.append(rho_current)
        # D1: track consecutive churn rounds for phase transition
        if rho_churn:
            consecutive_churn_rounds += 1
        else:
            consecutive_churn_rounds = 0
        _log(f"  Registry: {novel_this_round} novel / {len(findings)} raw, "
             f"{len(registry.entries)} total, "
             f"rho={rho_current:.3f}, rho_avg={rho_avg:.3f}"
             f"{' [CHURN]' if rho_churn else ''}"
             f"{f' (churn x{consecutive_churn_rounds})' if consecutive_churn_rounds > 1 else ''}")

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
        _update_finding_statuses(registry, round_idx, cfg=cfg)
        # Corrected-copy ingest (2026-08-12). Runs BEFORE the gate so a passage
        # offered this round is available to the discrimination control this
        # round rather than next. A no-op on any round where no model offered
        # one — which is every archived round.
        _ingest_corrected_copies(
            registry, responses, round_idx, cfg=cfg, repo_root=str(REPO_ROOT))
        # "tools decide" override (gated, default-off): the runner re-runs each
        # model-attached falsifier and lets that verdict win over the vote.
        apply_falsifier_verdicts(registry, round_idx, cfg=cfg, repo_root=str(REPO_ROOT))
        # Capability-aware routing (gated, default-off): route the criticals
        # the gate escalated to HIL to a stronger writer before accepting the HIL.
        _apply_routing(registry, round_idx, exp_config, cfg=cfg,
                       repo_root=str(REPO_ROOT))
        registry.auto_resolve_contested(round_idx)

        # A3: HIL escalation
        registry.escalate_stale_contested(round_idx, max_contested_rounds=cfg.max_contested_rounds)

        # ── Gamma input fix (15 May 2026) ──
        # Post-reconciliation novelty: replace this round's novelty_count
        # with the count of canonical entries actually registered this
        # round whose post-reconciliation status is genuinely novel.
        # Previously novelty_counts[-1] was the pre-reconciliation raw
        # count (set at line ~4285 before state transitions), which
        # systematically overstated novelty when reconciliation later
        # merged findings into existing canonical entries.
        #
        # Bug surfaced in Exp 40: Round 9 had novel_this_round=58
        # (pre-reconciliation) but reconciliation flagged 72 findings as
        # 100% duplicates of canonical entries already in the registry —
        # gamma reported "still novel" while reconciliation said "fully
        # saturated". The two metrics measured the same underlying state
        # at different layers of the pipeline. Fix: align gamma's input
        # with the reconciliation pipeline's view of novelty.
        _NON_NOVEL_TERMINAL = {
            "MERGED", "DUPLICATE", "UNCONFIRMED", "REFUTED",
        }
        post_reconciliation_novel = sum(
            1 for e in registry.entries.values()
            if e.get("open_since_round") == round_idx
            and e.get("status") not in _NON_NOVEL_TERMINAL
        )
        pre_reconciliation_novel = novelty_counts[-1] if novelty_counts else 0
        if pre_reconciliation_novel != post_reconciliation_novel:
            _log(
                f"  γ-input correction: novel pre-reconciliation="
                f"{pre_reconciliation_novel}, "
                f"post-reconciliation={post_reconciliation_novel} "
                f"(replacing in novelty_counts)"
            )
            novelty_counts[-1] = post_reconciliation_novel

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
        # TARGET INTEGRITY GUARD (2026-07-29). A frozen target must stay frozen:
        # apply_fixes_back=false means the module under review is not to change
        # for the run's duration. Panel models are dispatched with Write/Edit in
        # their allowed tools (experiment_11_orchestrator.py:693), so a model CAN
        # mutate the target mid-run — observed 2026-07-29 04:07-04:09 on Exp 47's
        # target (mutated, then restored, leaving no trace in git or the round
        # files). Any falsifier re-verified during such a window would have run
        # against a different module than the one under review. Detective only:
        # hashes the target each round and logs a LOUD warning on change. It
        # cannot prevent the write and deliberately does not halt the run —
        # whether to remove model write access is a founder ruling.
        try:
            import hashlib as _hl
            _tgt_p = Path(REPO_ROOT) / cfg.test_article
            _tgt_h = _hl.sha256(_tgt_p.read_bytes()).hexdigest()
            _prev_h = locals().get("_target_hash_prev") or globals().get("_TARGET_HASH_PREV")
            if _prev_h and _prev_h != _tgt_h:
                _log(f"  *** TARGET INTEGRITY WARNING: {cfg.test_article} CHANGED "
                     f"mid-run (round {round_idx}): {_prev_h[:12]} -> {_tgt_h[:12]}. "
                     f"Findings/falsifiers from this round may reference a different "
                     f"module than earlier rounds. Review before trusting results. ***")
                result.setdefault("target_integrity_events", []).append(
                    {"round": round_idx, "from": _prev_h, "to": _tgt_h})
            globals()["_TARGET_HASH_PREV"] = _tgt_h
            result.setdefault("target_hashes", {})[str(round_idx)] = _tgt_h
        except Exception as _ti_exc:  # noqa: BLE001 — guard must never break a run
            _log(f"  WARNING: target integrity check failed ({_ti_exc})")

        immune_result = brain.run_immune_pipeline(findings)

        # PER-VERDICT SPECIALIST LOG (one-shot arc, 2026-07-29): the ratified
        # earn-their-keep gate for the exam experiments requires, per verdict,
        # {classified type, routed tool, verdict, finding id} so that recall,
        # non-distortion and decision-change can be attributed to the specialist
        # rather than to the surrounding panel. Ground truth is joined post-run
        # from the exam answer key. Pure telemetry: never read by the gate.
        try:
            _sv_rows = []
            for _fid, _vlist in (getattr(immune_result, "cell_verdicts", {}) or {}).items():
                _canon = None
                for _f in findings:
                    if _f.finding_id == _fid:
                        _canon = registry.lookup_alias(_f.model_id, _f.finding_id)
                        break
                for _v in (_vlist or []):
                    _sv_rows.append({
                        "round": round_idx,
                        "finding_id": _fid,
                        "canonical_id": _canon,
                        "cell_type": str(getattr(_v, "cell_type", "")),
                        "claim_type": str(getattr(_v, "claim_type", "")),
                        "tool_used": getattr(_v, "tool_used", ""),
                        "verdict": getattr(_v, "verdict", ""),
                        "confidence": getattr(_v, "confidence", None),
                        "evidence": (getattr(_v, "evidence", "") or "")[:300],
                    })
            if _sv_rows:
                _sv_path = logs_dir / f"specialist_verdicts_r{round_idx:02d}.json"
                _sv_path.write_text(json.dumps({
                    "round": round_idx,
                    "domain": cfg.domain,
                    "final_verdicts": dict(getattr(immune_result, "final_verdicts", {}) or {}),
                    "verdicts": _sv_rows,
                }, indent=2, default=str), encoding="utf-8")
                _log(f"  specialist verdict log: {len(_sv_rows)} verdicts -> "
                     f"{_sv_path.name}")
        except Exception as _sv_exc:  # noqa: BLE001 — telemetry must never break a run
            _log(f"  WARNING: specialist verdict logging failed ({_sv_exc})")

        for f in findings:
            if f.verified:
                canonical = registry.lookup_alias(f.model_id, f.finding_id)
                if canonical:
                    registry.mark_verified(canonical)

        # Feedback channel (cdsfl_operational.md §17) — close the loop by
        # assembling per-model feedback from round K's schema outputs. The
        # result is injected at the top of round K+1's prompt so flagged
        # findings receive corrective action, not silent repetition.
        # Runs after immune_result is available. Defensive: build failures
        # never crash the loop, they simply yield empty feedback.
        if feedback_enabled:
            feedback_sections_for_next_round = _build_feedback_for_next_round(
                round_idx=round_idx,
                findings=findings,
                responses=responses,
                immune_result=immune_result,
                rk_validation=rk_validation,
                cfg=cfg,
            )
            if feedback_sections_for_next_round:
                _log(
                    f"  [feedback] round {round_idx} → round {round_idx + 1}: "
                    f"{len(feedback_sections_for_next_round)} model(s) flagged"
                )

        # Shadow cells (Macrophage + Ouroboros) — run after main pipeline, zero verdict effect
        shadow_cell_data = _run_shadow_cells(
            round_idx=round_idx,
            immune_result=immune_result,
            findings=findings,
            exp_config=cfg.shadow_cell_config,
            logs_dir=brain.logs_dir,
        )

        # ── Ouroboros loop-close (2026-07-31): consume what the cell produced.
        # Both halves stay empty/zero unless the experiment's _ouroboros block
        # opted in, so a config without the opt-in keys runs the pre-31-July
        # code path exactly.
        _ouro_wiring = shadow_cell_data.get("_ouroboros_wiring", {}) or {}
        ouroboros_brief_section_for_next_round = _ouro_wiring.get(
            "brief_section", "") or ""
        ouroboros_rk_inputs = {
            "c_ext": float(_ouro_wiring.get("c_ext", 0.0) or 0.0),
            "nu_k_by_finding": _ouro_wiring.get("nu_k_by_finding", {}) or {},
            "nu_k_mean": float(_ouro_wiring.get("nu_k_mean", 0.0) or 0.0),
        }
        if ouroboros_brief_section_for_next_round:
            _log(f"  [ouroboros] round {round_idx} → round {round_idx + 1}: "
                 f"brief injected into prompt "
                 f"({len(ouroboros_brief_section_for_next_round):,} chars, "
                 f"{shadow_cell_data['ouroboros'].get('briefs_rendered', 0)} "
                 f"paper(s))")
        if ouroboros_rk_inputs["c_ext"] > 0.0:
            _log(f"  [ouroboros] c_ext={ouroboros_rk_inputs['c_ext']:.4f} "
                 f"(search={_ouro_wiring.get('search_status', '?')}), "
                 f"ν̄_k={ouroboros_rk_inputs['nu_k_mean']:.4f} → R_k channel")

        # CC2v verification (A5)
        verification_stats = _verification_step(
            registry, round_idx, full_code, exp_config.models, cfg)

        # S_k solution verification pipeline
        sk_stats: Dict[str, Any] = {}
        if cfg.sk_enabled:
            sk_stats = _evaluate_sk_for_findings(
                registry, target_text, str(target_rel),
                baseline=sk_baseline,
                round_idx=round_idx,
                test_cmd=cfg.test_cmd,
                s_floor=cfg.sk_s_floor,
                c_ext=ouroboros_rk_inputs.get("c_ext", 0.0),
                nu_k_by_finding=ouroboros_rk_inputs.get("nu_k_by_finding"),
                nu_k_default=ouroboros_rk_inputs.get("nu_k_mean", 0.0),
                rk0_prior=rk0_prior,
            )

        # Exp 40 1D.3: compute per-model rho BEFORE the ITC loop so each
        # model's DEGRADATION suppression uses its own discovery efficiency,
        # not the pooled panel-average. A model with collapsed per-model rho
        # (< rho_threshold) gets ITC restart; a model with healthy per-model
        # rho is left alone even if the panel as a whole is in churn.
        rho_avg_per_model: Dict[str, float] = {}
        for _label in baseline:
            _nv = novelty_counts_per_model.get(_label, [])
            _rw = raw_counts_per_model.get(_label, [])
            if _nv and _rw:
                _, _rho_m_avg, _ = _compute_rho(_nv, _rw, cfg)
                rho_avg_per_model[_label] = _rho_m_avg

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
            raw_markers = len(_FINDING_DECL_RE.findall(model_text))
            # Count verdicts for this model — verdicts are valid structured
            # output that should count towards parse yield (P2 fix).
            model_verdicts = len(_parse_verdicts(model_text, model_label, round_idx))
            # ORDERING INVARIANT: _itc_detect MUST run before
            # _update_observed_fingerprint. ITC detect populates
            # parse_yield_history in _itc_model_state; the fingerprint
            # quality gate reads it to decide whether to record prompt
            # size in budget history. Reversing the order would cause
            # stale/missing yield data in the quality gate.
            classification = _itc_detect(
                model_label, round_idx, len(model_findings), model_text,
                prior_ids, current_ids, dispatch_error=dispatch_err,
                raw_finding_markers=raw_markers,
                verdict_count=model_verdicts,
            )
            if classification:
                # Exp 40 1D.3: per-model rho gates DEGRADATION suppression.
                # Fall back to the pooled rho_avg when per-model history is
                # missing (cold start, or model joined mid-run).
                _model_rho = rho_avg_per_model.get(model_label, rho_avg)
                # Exp 40 fix 1d: γ-regime gate. gamma_history[-1] is the
                # last completed round's γ (this round's γ is appended
                # later in the loop). Default 1.0 (active regime, no
                # suppression) on cold start before any γ exists.
                _gamma_prev = gamma_history[-1] if gamma_history else 1.0
                _itc_adapt(model_label, classification, round_idx,
                           rho_rolling_avg=_model_rho,
                           rho_threshold=cfg.rho_threshold,
                           gamma_current=_gamma_prev,
                           gamma_converged_threshold=getattr(
                               cfg, "gamma_converged_threshold", 0.10))
            elif model_label in _itc_model_state:
                _itc_clear_adaptation(model_label)
            _update_observed_fingerprint(
                observed_fingerprints, model_label, round_idx,
                len(model_findings), len(model_text),
                prompt_chars=prompt_lengths.get(model_label, 0),
                raw_finding_markers=raw_markers,
                dispatch_error=dispatch_err,
            )
            # Exp 40 fix 1E.5: refresh the 6 derived attention metrics so
            # fingerprint consumers (burst_planner, B-Cell dispatcher,
            # decomposition heuristics) see up-to-date values each round.
            _compute_attention_metrics(
                observed_fingerprints.setdefault(model_label, {}),
                novelty_counts_per_model.get(model_label, []),
                _itc_model_state.get(model_label, {}).get(
                    "parse_yield_history", [],
                ),
            )

        # Directed messages (relay only)
        if cfg.topology == "relay" and cfg.relay_mode == "directed":
            for label, text in responses.items():
                if text:
                    brain.extract_directed_messages(label, text, round_idx)

        # Severity calibration (over-production bounding, 2026-06-10, gated
        # default-off). Demote any over-rated-but-genuine critical — a
        # falsifier-CONFIRMED REAL defect explicitly flagged LATENT/conditional and
        # NOT in a safety/core/security category — to just below the critical
        # threshold, recording the original severity + reason on the entry. MUST run
        # here: AFTER the falsifier gate has set falsifier_verdict (apply_falsifier_
        # verdicts, earlier this round) and BEFORE the settled-novelty recompute and
        # the unverified/open critical counts below, so the demoted finding drops out
        # of every critical-counting channel this same round while staying in the
        # registry. No-op (mutates nothing) when the flag is off.
        # LATENT TAGGER (2026-07-31, gated default-off). Severity calibration's
        # condition (3) — entry["latent"] — has never had a producer, so the
        # calibrator has been inert since it was written. This is that producer.
        # MUST run here: after apply_falsifier_verdicts (so a tag can never be
        # read as a verdict) and immediately before the calibration sweep that
        # consumes it. Sets latent=False on every entry lacking explicit evidence,
        # so turning the tagger on without the calibrator changes no outcome.
        if getattr(cfg, "latent_tagger_enabled", False):
            from bench.latent_tagger import tag_registry
            _latent_n = tag_registry(
                registry, skip_statuses={"MERGED", "CLOSED", "DUPLICATE"},
            )
            _log(f"  latent-tagger: {_latent_n} finding(s) tagged latent "
                 f"(explicit evidence only; silence reads as reachable)")
        _sev_calib_n = _apply_severity_calibration(registry, cfg, round_idx)
        if _sev_calib_n:
            _log(f"  severity-calibration: {_sev_calib_n} finding(s) recalibrated "
                 f"this round (retained, no longer blocking)")

        # Step 3 return-to-first-principles (founder-directed 2026-05-22):
        # the gate AND the gamma diagnostic must see GENUINE novelty, not raw
        # registrations. novel_this_round / novel_critical_this_round are
        # appended pre-verifier (registry.register runs before
        # run_immune_pipeline), so panel over-production and noise inflate them
        # — Exp 41 late-round raw novelty was 10/6/3, all unverifiable. Recompute
        # this round's novelty from the SETTLED series (open_since_round==r and
        # final status not in MERGED/DUPLICATE/UNCONFIRMED/REFUTED) and overwrite
        # the round's history entries so that: (a) gamma is a genuine decay-curve
        # DIAGNOSTIC; (b) the state gate's novel_this_round is genuine; (c) the
        # gamma-alt count path (novel_critical_history) sees GENUINE novel
        # criticals, so its "K consecutive zero-novel-critical" criterion can
        # actually reach zero and converge. "No new discoveries" therefore means
        # "no new GENUINE discoveries that survived reconciliation + the
        # (now-live) specialist verifier."
        _settled_all, _settled_crit = _settled_novelty_series(registry, round_idx)
        if round_idx < len(_settled_all):
            _raw_novel = novel_this_round
            novel_this_round = _settled_all[round_idx]
            if novelty_counts:
                novelty_counts[-1] = _settled_all[round_idx]
            if novel_critical_history and round_idx < len(_settled_crit):
                novel_critical_history[-1] = _settled_crit[round_idx]
            if novel_this_round != _raw_novel:
                _log(f"  novelty (settled/genuine): all={_settled_all[round_idx]} "
                     f"crit={_settled_crit[round_idx]} (raw all={_raw_novel})")

        # Code-location novelty series (2026-06-08). Computes the critical-novelty series
        # keyed by code location (the verified fix for the cross-round dedup failure) and
        # logs it beside the ID-proxy count. When cfg.location_keyed_convergence is set this
        # series GATES: it overwrites novel_critical_history[-1] and becomes the COUNT side
        # of the two-sided gate. This comment said "telemetry-only, NEVER gates" until
        # 2026-08-08 — false since the first location-keyed live run, three lines above the
        # promotion it denied.
        #
        # Wrapped so a computation failure can never break a run. That swallow is deliberate
        # and unchanged, but it is NOT free when the series gates: on failure the round's
        # gate input silently stays at the ID-proxy value set immediately above, so the
        # handler below must say so rather than report a skipped shadow computation.
        # _gates is read BEFORE the try so the handler can reach it.
        _gates = getattr(cfg, "location_keyed_convergence", False)
        try:
            if getattr(cfg, "location_shadow_enabled", True) and _loc_symbols:
                location_crit_history = _location_keyed_critical_series(
                    registry, round_idx, _loc_symbols)
                _loc_tail = location_crit_history[-cfg.gamma_alt_consecutive_zero_crit:]
                _idprox = _settled_crit[round_idx] if round_idx < len(_settled_crit) else "NA"
                if _gates and round_idx < len(location_crit_history) and novel_critical_history:
                    # PROMOTED: the location-keyed count is the convergence trigger.
                    novel_critical_history[-1] = location_crit_history[round_idx]
                _log(f"  [{'GATE' if _gates else 'shadow'}] location-keyed novel-crit this "
                     f"round={location_crit_history[round_idx]} (ID-proxy crit={_idprox}; "
                     f"series tail={_loc_tail}; "
                     f"{'FEEDS γ-alt convergence' if _gates else 'telemetry only, never gates'})")
        except Exception as _loc_exc:  # telemetry/gate-feed must never break a run
            if _gates:
                _log(f"  [GATE] location-keyed novelty FAILED: "
                     f"{type(_loc_exc).__name__}: {_loc_exc} — the run continues, but the "
                     f"COUNT side of the two-sided gate silently falls back to the ID-proxy "
                     f"series for round {round_idx}, which is the cross-round dedup failure "
                     f"the location key exists to fix. REVIEW THIS ROUND.")
            else:
                _log(f"  [shadow] location-keyed novelty skipped: "
                     f"{type(_loc_exc).__name__}: {_loc_exc} (telemetry only this run)")

        # Gamma — REPORTED, NEVER a trigger or blocker (panel redesign
        # 2026-05-23). Telemetry-only in the state gate (config:
        # gamma_telemetry_only_until >= max_rounds) and deleted as a
        # convergence trigger on the critical-quiescence path. Reported on
        # BOTH series each round: gamma_all (all-severity decay) and
        # gamma_critical (critical-only decay; reads ~1.0 at a clean
        # convergence where critical discovery has stopped). Both computed
        # from the SETTLED/genuine series via _estimate_gamma.
        gamma_all = _estimate_gamma(_settled_all, cfg.min_rounds_for_gamma)
        gamma_critical = _estimate_gamma(_settled_crit, cfg.min_rounds_for_gamma)
        gamma = gamma_all  # legacy name; all-series. Reported, never gates.
        gamma_history.append(gamma)
        gamma_all_history.append(gamma_all)
        gamma_critical_history.append(gamma_critical)
        gate_level, gamma_passed = _check_gamma_gate(gamma, round_idx, cfg)

        _log(f"  gamma_all: {gamma_all:.3f} ({gate_level}, "
             f"{'passed' if gamma_passed else 'BLOCKED'}) — "
             f"{_interpret_gamma(gamma_all)}")
        _log(f"  gamma_critical: {gamma_critical:.3f} (continuous decay-curve "
             f"diagnostic; the 3-round zero-new-critical count is its threshold-free "
             f"convergence endpoint — same diminishing-returns principle, ~1.0 at "
             f"clean critical convergence)")
        _log(f"  Round {round_idx}: {len(findings)} findings, {round_elapsed:.1f}s")

        # Convergence gate
        converged, conv_reason = _check_state_convergence(
            round_idx, registry, novel_this_round, gamma, gate_history, cfg,
            open_ch_history=open_ch_history,
            rho_rolling_avg=rho_avg, rho_churn=rho_churn,
        )
        _log(f"  Convergence: {conv_reason}")

        # Critical-quiescence convergence path (panel redesign
        # 2026-05-23). Fires SOLELY on K consecutive rounds with zero
        # novel CRITICAL on the settled series — the γ-threshold trigger
        # is deleted (γ is reported, never a trigger). A4 fail-safe: an
        # UNCONFIRMED critical-severity candidate (excluded from the
        # settled series) must not let the streak accrue silently, so the
        # count of such candidates is passed in and blocks/logs.
        _unresolved_crit = registry.unverified_critical_count()
        if _unresolved_crit > 0:
            _log(f"  A4: {_unresolved_crit} unverified critical-severity "
                 f"candidate(s) (UNCONFIRMED, sev>=0.7) pending — "
                 f"zero-critical streak blocked, HIL review required")
        # Static-queue closure: ladder-exhausted irreducible criticals handed to HIL.
        _irreducible_q = registry.irreducible_queue_count()
        if _irreducible_q > 0:
            _log(f"  static HIL queue: {_irreducible_q} ladder-exhausted irreducible "
                 f"critical(s) — excluded from the A4 blocker; HALT ALARM if "
                 f"> {cfg.max_irreducible_queue}")
        if getattr(cfg, "hardened_gate_enabled", False):
            # F4/F6/conjunction hardened gate: settled-registry γ,
            # critical/structural conjunction, all-novelty γ as
            # diagnostic only. Legacy γ-alt is bypassed entirely.
            gamma_alt_converged, gamma_alt_reason, _hg_telem = (
                _check_hardened_convergence(round_idx, registry, cfg)
            )
            _log(f"  hardened-gate telemetry: {_hg_telem}")
        else:
            # Critical-quiescence path enforces review-clean (not
            # contested, not churning) directly so it does not converge
            # via the OR while the state gate would have blocked on them.
            gamma_alt_converged, gamma_alt_reason = (
                _check_gamma_alt_convergence(
                    round_idx, gamma, novel_critical_history, cfg,
                    unresolved_critical=_unresolved_crit,
                    contested=registry.contested_count(round_idx, subcritical_exclusion=bool(getattr(cfg, 'falsifier_gate_enabled', False))),
                    rho_churn=rho_churn,
                    irreducible_queue=_irreducible_q,
                    gamma_critical=gamma_critical,  # TWO-SIDED gate: gamma is an ACTIVE condition
                    # Distinguishes "clean target, panel worked" from "panel
                    # returned nothing" when the critical series is all-zero.
                    total_findings=len(registry.entries),
                )
            )
        if gamma_alt_converged and not converged:
            _log(f"  γ-alt: {gamma_alt_reason}")
            converged = True
            conv_reason = gamma_alt_reason
        elif not gamma_alt_converged:
            # Log but don't promote — main gate governs until γ-alt fires.
            _log(f"  γ-alt: {gamma_alt_reason}")

        # G7 round-level tie-breaker (Gemini confer input, folded into
        # the G7 design). When the run is deep in the converged regime
        # by γ-decay yet γ-alt is NOT met (the exact continuation
        # pattern: γ≈0.03 but novel-CRIT bursts kept resetting the
        # zero-CRIT streak), force arbitration across the unresolved
        # MERGE deadlocks at round close — bounded by the remaining
        # per-round dispatch budget. Inert unless arbitration enabled.
        if (
            _merge_arb_ctx
            and _merge_arb_ctx.get("enabled")
            and not gamma_alt_converged
            and gamma < _merge_arb_ctx.get("tiebreaker_gamma", 0.05)
        ):
            _budget = (
                _merge_arb_ctx.get("max_per_round", 3)
                - _merge_arb_ctx.get("used_this_round", 0)
            )
            if _budget > 0:
                _deadlocked = [
                    (cid, e) for cid, e in registry.entries.items()
                    if e.get("merge_defer_count", 0)
                    >= _merge_arb_ctx.get("min_defer_count", 2)
                    and e.get("status") not in (
                        "MERGED", "CLOSED", "DUPLICATE")
                    and not e.get("g7_kept_distinct_round")
                ]
                if _deadlocked:
                    _log(f"  G7 tie-breaker: γ={gamma:.3f} < "
                         f"{_merge_arb_ctx['tiebreaker_gamma']} and "
                         f"γ-alt unmet — sweeping "
                         f"{min(_budget, len(_deadlocked))} of "
                         f"{len(_deadlocked)} deadlock(s)")
                for _cid, _e in _deadlocked[:_budget]:
                    _by_t: dict = {}
                    for _v in _e.get("verdicts", []):
                        if _v.get("verdict") != "MERGE":
                            continue
                        _m = re.search(
                            r'merged_into=(C\d{4,})',
                            _v.get("evidence", ""))
                        _tid = _m.group(1) if _m else "__unknown__"
                        _by_t.setdefault(_tid, []).append(_v)
                    _try_merge_arbitration(
                        _e, _cid, _by_t, registry, round_idx,
                        _e.get("merge_defer_count", 0),
                    )

        # Stall detector
        stall_result = _check_stall_convergence(
            round_idx, registry, gamma, stall_history, cfg,
            consecutive_churn_rounds=consecutive_churn_rounds)

        # Checkpoint — atomic write to prevent corruption on interrupt
        ckpt_path = brain.logs_dir / "runner_state.json"
        _ckpt_data = json.dumps({
            "registry": registry.to_dict(),
            "novelty_counts": novelty_counts,
            "raw_counts": raw_counts,
            # Exp 40 1D.3: per-model rho history persists across resumes
            "novelty_counts_per_model": novelty_counts_per_model,
            "raw_counts_per_model": raw_counts_per_model,
            "rho_history": [round(r, 6) for r in rho_history],
            "gamma_history": [round(g, 6) for g in gamma_history],
            "gate_history": gate_history,
            "open_ch_history": open_ch_history,
            "stall_history": stall_history,
            "novel_critical_history": novel_critical_history,
            "cumulative_context_chars": cumulative_context_chars,
            "consecutive_churn_rounds": consecutive_churn_rounds,
            "itc_model_state": _itc_model_state,
            "itc_hil_flags": _itc_hil_flags,
            "burst_state": burst_state if burst_state else None,
        }, indent=2, default=str)
        _ckpt_tmp = ckpt_path.with_suffix(".json.tmp")
        _ckpt_tmp.write_text(_ckpt_data, encoding="utf-8")
        _ckpt_tmp.replace(ckpt_path)

        # Round data for report
        # Gemini 3.1 Pro + Codex 5.3 confer (13 April 2026): round report was
        # counts-only, making HIL review of intermediate rounds impossible.
        # Now includes per-finding summaries with provenance.
        round_findings_detail = [
            {
                "finding_id": f.finding_id,
                "model_id": f.model_id,
                "flaw_class": f.flaw_class,
                "severity": f.severity,
                "description": f.description[:500],
                "verified": f.verified,
                "escalated": f.escalated,
                "origin_type": getattr(f, "origin_type", ""),
                "source_ref": getattr(f, "source_ref", ""),
                "target_file": getattr(f, "target_file", ""),
            }
            for f in findings
        ]
        # Exp 40 fix 1E.7: cross-model diversity (compliance-theatre detector).
        # For each finding, extract the §18 alternative blocks from the
        # emitting model's raw response; pool across the panel; compute mean
        # pairwise Jaccard. Logging-only — does not gate admission or R_k.
        # Exp 40 fix 1E.9: the same pass builds per-finding DivergenceRecord
        # objects so we can flag cross-round recidivism — a round K+1
        # alternative that replicates a round K alternative unchanged — and
        # surface the severe 0.60 tier through eta_int_modulator.
        # Exp 52 factorial (2026-07-29): this whole pass IS the runner half of
        # the divergence mechanism. Previously it ran unconditionally with a
        # hard-coded DivergenceConfig(enabled=True); it is now gated on the
        # config switch, so a divergence-off cell performs no alternative
        # extraction, computes no cross-model diversity, flags no recidivism,
        # and carries no alternatives into the next round.
        cross_model_diversity: Optional[Dict[str, Any]] = None
        recidivism_hits: List[Dict[str, Any]] = []
        current_round_alternatives_by_finding: Dict[str, List[Any]] = {}
        if not divergence_pass_enabled:
            # Recorded explicitly rather than left as a bare None, so a cell's
            # round file distinguishes "the pass was switched off" from "the
            # pass ran and found no alternatives".
            cross_model_diversity = {"divergence_pass": "disabled"}
        try:
            if not divergence_pass_enabled:
                raise _DivergencePassDisabled()
            from bench.dm._divergence import (
                build_divergence_record as _build_divergence_record,
                DivergenceConfig as _DivergenceConfig,
            )
            # Honoured at the construction site as well as at the branch guard:
            # if a later refactor drops the guard, the record builder itself
            # still returns the disabled no-op record.
            _div_cfg = _DivergenceConfig(enabled=divergence_pass_enabled)
            per_model_alts: List[Tuple[str, str]] = []
            for f in findings:
                raw = responses.get(f.model_id, "")
                if not raw:
                    continue
                prior_alts = prior_round_alternatives_by_finding.get(
                    f.finding_id, [],
                )
                rec = _build_divergence_record(
                    f.finding_id, f.description or "", raw,
                    config=_div_cfg,
                    prior_round_alternatives=prior_alts,
                )
                if rec.alternatives:
                    current_round_alternatives_by_finding[f.finding_id] = list(
                        rec.alternatives,
                    )
                for alt in rec.alternatives:
                    alt_text = getattr(alt, "alternative_text", "") or ""
                    if alt_text.strip():
                        per_model_alts.append((f.model_id, alt_text))
                    if (
                        getattr(alt, "prior_round_isomorphism", 0.0)
                        >= _div_cfg.near_copy_threshold
                    ):
                        recidivism_hits.append({
                            "finding_id": f.finding_id,
                            "model_id": f.model_id,
                            "prior_round_isomorphism": round(
                                float(alt.prior_round_isomorphism), 4,
                            ),
                            "reasons": list(alt.rejection_reasons),
                        })
            if per_model_alts:
                cross_model_diversity = diversity_signal_from_round(per_model_alts)
        except _DivergencePassDisabled:
            pass  # switched off by config; cross_model_diversity already set
        except Exception as _e:
            # Logging-only metric — never crash the loop on parse errors.
            cross_model_diversity = {"error": f"{type(_e).__name__}: {_e}"}

        if recidivism_hits:
            _log(f"  1E.9 recidivism: {len(recidivism_hits)} alt(s) flagged")
        prior_round_alternatives_by_finding = current_round_alternatives_by_finding

        round_data: Dict[str, Any] = {
            "round": round_idx, "type": round_type,
            "findings_count": len(findings),
            "findings": round_findings_detail,
            "novel_this_round": novel_this_round,
            "registry_total": len(registry.entries),
            "open_crit_high": registry.open_crit_high_count(),
            "unverified_critical": _unresolved_crit,
            "models_responded": list(responses.keys()),
            "elapsed_s": round(round_elapsed, 1),
            "gamma": round(gamma, 4),
            "gamma_all": round(gamma_all, 4),
            "gamma_critical": round(gamma_critical, 4),
            "location_crit_shadow": (location_crit_history[round_idx]
                                     if round_idx < len(location_crit_history) else 0),
            "rho": round(rho_current, 4),
            "rho_avg": round(rho_avg, 4),
            "verification": verification_stats,
            "sk_pipeline": sk_stats,
            "stall_detector": stall_result,
            "shadow_cells": shadow_cell_data,
            "cross_model_diversity": cross_model_diversity,
            "recidivism_hits": recidivism_hits,
        }
        result["rounds"].append(round_data)

        # ── A7: irreducible-queue alarm — HALT, NOTIFY, ATTACH ───────────────
        # Runs after this round's telemetry is recorded (the round record is
        # part of the evidence) and before EVERY path that can end or continue
        # a round: before the HIL pause, before the convergence action block,
        # before any burst phase transition. No gate arrangement — hardened,
        # γ-alt, burst — can route around it, because it does not consult any
        # of them.
        #
        # This is NOT a convergence verdict. The run stops, `converged` stays
        # False, `convergence_reason` records a halt distinct from both a
        # finish and a stall, and the per-finding evidence bundle rides in the
        # report. See build_irreducible_queue_alarm for why the previous
        # response — refusing convergence, silently, from inside the γ-alt
        # checker — was worse than useless and got itself suppressed twice
        # while it was right.
        _irq_alarm = build_irreducible_queue_alarm(registry, cfg, round_idx)
        if _irq_alarm is not None:
            _log("")
            for _line in _irq_alarm["notify"].splitlines():
                _log(f"  *** {_line}")
            _log("")
            result["irreducible_queue_alarm"] = _irq_alarm
            result["halted"] = True
            result["halted_at_round"] = round_idx
            result["convergence_reason"] = IRREDUCIBLE_QUEUE_HALT
            result["registry"] = registry.to_dict()
            converged = False
            brain._save_checkpoint()
            break

        # ── HIL review gate (13 April 2026, agreed scope refinement) ──
        # In monolithic mode: pause after every round.
        # In burst mode: pause only at phase transitions (handled below).
        # The operator reviews findings with CC, fixes issues, and resumes.
        if cfg.hil_review and not (burst_plan and burst_state):
            _log(f"\n  ═══ HIL REVIEW GATE — Round {round_idx} complete ═══")
            _log(f"  Findings this round: {len(findings)}, novel: {novel_this_round}")
            _log(f"  Registry total: {len(registry.entries)}")
            _log(f"  γ={gamma:.4f}, ρ={rho_current:.4f}, ρ_avg={rho_avg:.4f}")
            _log(f"  Checkpoint saved. Resume with --resume --hil-review")
            _log(f"  ═══════════════════════════════════════════════════\n")
            # Pre-launch review fix: save checkpoint AGAIN here to capture
            # immune pipeline results and convergence stats that occurred
            # after the initial persist() call (which only has raw findings).
            brain._save_checkpoint()
            # Write partial report for review
            result["hil_paused_at_round"] = round_idx
            result["hil_status"] = "paused_for_review"
            partial_report = logs_dir / f"{cfg.experiment_name}_hil_r{round_idx:02d}.json"
            _write_report_json(partial_report, result)
            sys.exit(42)

        # ── Phase transition or final convergence ──
        phase_transition = False

        # D1: churn-based phase transition in burst mode.
        # Sustained churn (3+ consecutive rounds) with gamma >= 0.45 signals
        # topic exhaustion — trigger phase transition without waiting for
        # convergence gate or stall detector.
        churn_transition = False
        if (burst_plan and burst_state and not burst_state["integration_done"]
                and consecutive_churn_rounds >= 3 and gamma >= 0.45
                and not converged and not stall_result.get("terminate")):
            churn_transition = True
            _log(f"  D1 churn transition: {consecutive_churn_rounds} consecutive "
                 f"churn rounds, gamma={gamma:.3f} — phase exhausted")

        if converged or stall_result.get("terminate") or churn_transition:
            reason_str = conv_reason if converged else stall_result.get("reason", "stall")
            if churn_transition:
                reason_str = (f"churn x{consecutive_churn_rounds}, gamma={gamma:.3f}")
            reason_type = ("CONVERGED" if converged
                           else "CHURN_EXHAUSTED" if churn_transition
                           else "STALL_CONVERGED")

            if burst_plan and burst_state and not burst_state["integration_done"]:
                # Burst mode: transition to next phase or integration
                phase_idx = burst_state["phase_idx"]
                current_phase_name = burst_plan.phases[phase_idx].name

                # Record phase findings
                burst_state["phase_findings"][current_phase_name] = (
                    build_findings_summary(registry.to_dict(), current_phase_name)
                )

                # ── HIL review gate at burst-mode phase boundary ──
                if cfg.hil_review:
                    _log(f"\n  ═══ HIL REVIEW GATE — Phase '{current_phase_name}' "
                         f"converged ({reason_type}) ═══")
                    _log(f"  Findings summary:\n{burst_state['phase_findings'][current_phase_name]}")
                    _log(f"  Registry total: {len(registry.entries)}")
                    remaining = len(burst_plan.phases) - phase_idx - 1
                    _log(f"  Phases remaining: {remaining} + integration")
                    _log(f"  Checkpoint saved. Resume with --resume --hil-review")
                    _log(f"  ═══════════════════════════════════════════════════\n")
                    result["hil_paused_at_round"] = round_idx
                    result["hil_paused_at_phase"] = current_phase_name
                    result["hil_status"] = "paused_for_review"
                    partial_report = logs_dir / f"{cfg.experiment_name}_hil_phase_{phase_idx}.json"
                    _write_report_json(partial_report, result)
                    sys.exit(42)

                if phase_idx + 1 < len(burst_plan.phases):
                    # Transition to next phase
                    next_idx = phase_idx + 1
                    next_phase = burst_plan.phases[next_idx]
                    burst_state["phase_idx"] = next_idx
                    burst_state["phase_round_offset"] = round_idx + 1

                    _log(f"\n  Phase {phase_idx} ({current_phase_name}) "
                         f"{reason_type} at round {round_idx}")
                    _log(f"  Transitioning to Phase {next_idx}: {next_phase.name}")

                    # Build prior findings summary for cross-phase awareness
                    prior_summary = "\n".join(
                        burst_state["phase_findings"].values())

                    full_code = build_phase_code(
                        next_phase, str(target_rel),
                        burst_plan.signatures, prior_summary)
                    base_prompt = _build_prompt(
                        full_code,
                        f"{target_rel} Phase {next_idx}: {next_phase.name}")

                    # Rebase convergence thresholds for new phase
                    overrides = phase_convergence_overrides(round_idx + 1)
                    cfg = replace(cfg, **overrides)

                    # Reset per-phase convergence state
                    gate_history.clear()
                    stall_history.clear()
                    novelty_counts.clear()
                    raw_counts.clear()
                    rho_history.clear()
                    gamma_history.clear()
                    open_ch_history.clear()
                    consecutive_churn_rounds = 0
                    extended = False

                    phase_transition = True
                    _log(f"  Phase {next_idx} starts at round {round_idx + 1}")

                elif not burst_state["integration_started"]:
                    # All phases done — start integration round
                    burst_state["integration_started"] = True
                    burst_state["phase_round_offset"] = round_idx + 1

                    _log(f"\n  Phase {phase_idx} ({current_phase_name}) "
                         f"{reason_type} at round {round_idx}")
                    _log("  All phases converged — starting integration round")

                    all_findings = "\n".join(
                        burst_state["phase_findings"].values())
                    full_code = build_integration_code(
                        target_text, str(target_rel), all_findings,
                        burst_state["context_signatures"])
                    base_prompt = _build_prompt(
                        full_code, f"{target_rel} Integration")

                    # Tight integration convergence
                    overrides = integration_convergence_overrides(
                        round_idx + 1)
                    cfg = replace(cfg, **overrides)

                    gate_history.clear()
                    stall_history.clear()
                    novelty_counts.clear()
                    raw_counts.clear()
                    rho_history.clear()
                    gamma_history.clear()
                    open_ch_history.clear()
                    extended = False

                    phase_transition = True
                    _log(f"  Integration starts at round {round_idx + 1}")

                else:
                    # Integration converged — done
                    burst_state["integration_done"] = True
                    _log(f"\n  INTEGRATION {reason_type} at round {round_idx}")
                    result["converged_at"] = round_idx
                    result["convergence_reason"] = f"BURST_{reason_type}"
                    result["burst_phases"] = len(burst_plan.phases)
                    # Propagate genuine convergence to brain.state so
                    # signal_complete() writes completion_signal.json
                    # status=CONVERGED (not INCOMPLETE). The hardened /
                    # gamma-alt gate previously set only the result dict,
                    # so post-mortem tooling read every hardened
                    # convergence as INCOMPLETE. Guarded on `converged`
                    # so churn/stall stops keep their own status.
                    # (Exp 40 Unit B->C seam, 2026-05-18.)
                    if converged:
                        brain.state.converged = True
                        brain.state.convergence_reason = f"BURST_{reason_type}"
                    break
            else:
                # Non-burst mode or integration done: final convergence
                _log(f"\n  {reason_type} at round {round_idx}: {reason_str}")
                result["converged_at"] = round_idx
                result["convergence_reason"] = reason_str
                # Propagate genuine convergence to brain.state so
                # signal_complete() writes completion_signal.json
                # status=CONVERGED (not INCOMPLETE). Guarded on
                # `converged` so churn/stall stops keep their own
                # status. (Exp 40 Unit B->C seam, 2026-05-18.)
                if converged:
                    brain.state.converged = True
                    brain.state.convergence_reason = reason_str
                break

        if not phase_transition:
            # Budget extension (only in non-burst or during integration)
            if (not burst_plan or (burst_state and
                    burst_state.get("integration_started"))) and \
                    round_idx == cfg.max_rounds - 1 and not extended:
                gamma_prev = (gamma_history[-2]
                              if len(gamma_history) >= 2 else 0.0)
                should_extend, ext_reason = _check_budget_extension(
                    round_idx, registry, gamma, gamma_prev, cfg)
                if should_extend:
                    effective_max = cfg.extension_cap
                    extended = True
                    _log(f"\n  BUDGET EXTENDED to {cfg.extension_cap}: "
                         f"{ext_reason}")
                    result["budget_extended"] = True

            # Extension stall
            if (extended and round_idx > cfg.max_rounds and
                    len(result["rounds"]) >= 2):
                prev = result["rounds"][-2]
                if (round_data.get("rho_avg", 1) <= prev.get("rho_avg", 0)
                        and round_data.get("open_crit_high", 0) >=
                        prev.get("open_crit_high", 0)):
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
    # Dual-series γ report (panel redesign 2026-05-23): reported, never gates.
    result["gamma_all_history"] = [round(g, 4) for g in gamma_all_history]
    result["gamma_critical_history"] = [
        round(g, 4) for g in gamma_critical_history
    ]
    # The location-keyed critical series. Emitted under BOTH names: the honest
    # one, and the legacy `..._shadow_...` key that every completed report and
    # every existing reader uses. The legacy name is actively misleading — it
    # says "shadow" in runs where the config had promoted this series to GATING
    # — but renaming it outright would silently break readers of six completed
    # runs, so it is deprecated in place rather than removed.
    # HIERARCHICAL NOVELTY — SHADOW. Computed from the final registry so it costs
    # nothing during the run and cannot affect it. Recorded so the two series can
    # be compared on real evidence before anyone promotes either.
    try:
        from bench.convergence_location import hierarchical_novelty_series
        _hier = hierarchical_novelty_series(
            registry.entries, round_idx, _loc_symbols or [],
            within_threshold=float(getattr(cfg, "hierarchical_within_threshold", 0.20)))
        result["hierarchical_crit_series"] = _hier
        result["hierarchical_crit_series_is_gating"] = bool(
            getattr(cfg, "hierarchical_novelty_convergence", False))
        result["hierarchical_within_threshold"] = float(
            getattr(cfg, "hierarchical_within_threshold", 0.20))
        # WHERE the rules disagree, so a human has specific findings to inspect
        # rather than two number sequences. These are the blind-spot candidates.
        from bench.convergence_location import novelty_rule_divergence
        result["novelty_rule_divergence"] = novelty_rule_divergence(
            registry.entries, _loc_symbols or [],
            within_threshold=float(getattr(cfg, "hierarchical_within_threshold", 0.20)))
    except Exception as _hx:  # noqa: BLE001 — shadow telemetry must never kill a run
        result["hierarchical_crit_series_error"] = f"{type(_hx).__name__}: {_hx}"

    result["location_crit_series"] = location_crit_history
    result["location_crit_series_is_gating"] = bool(
        getattr(cfg, "location_keyed_convergence", False))
    result["location_crit_shadow_history"] = location_crit_history  # DEPRECATED alias
    result["registry"] = registry.to_dict()
    result["hil_flags"] = _itc_hil_flags[:]
    # Secondary-route fallback accumulators (2026-05-22). Surfaced in
    # the report so end-of-run review can see per-turn fallback usage
    # (a successful secondary dispatch) and the persistent-empty events
    # (both primary and secondary failed — the model contributed
    # nothing this round, but was NOT excluded). These are the genuine
    # HIL signals for route-degradation review.
    result["secondary_route_usage"] = _secondary_route_usage[:]
    result["persistent_empty_flags"] = _persistent_empty_flags[:]

    # POST-CONVERGENCE SETTLE (2026-07-31): a finding demonstrated in the FINAL
    # round never meets the CONFIRMED+verified -> CLOSED transition, because that
    # transition runs at the start of a round and there is no next round. Runs
    # unconditionally — it is bookkeeping, needs no config, costs no dispatch,
    # and like the sweep it is strictly after the verdict, so it cannot touch
    # convergence. Must precede the sweep, so the sweep sees only findings that
    # are genuinely unresolved.
    if converged:
        try:
            _settled = _settle_confirmed_findings(registry, round_idx)
            if _settled:
                result["post_convergence_settled"] = _settled
                result["registry"] = registry.to_dict()  # refresh after the edit
        except Exception as _st_exc:  # noqa: BLE001 — never lose a run to tidying
            _log(f"  WARNING: post-convergence settle failed ({_st_exc})")

    # RESIDUAL-CLEARING SWEEP (2026-07-28 as post-convergence; widened 2026-08-01).
    # The verdict is already recorded above; the sweep can only clean the residual
    # ledger, never touch convergence.
    #
    # WHY IT NOW RUNS ON A HALT TOO
    # -----------------------------
    # It was gated on `converged`, so the cleaner was switched off in exactly the
    # runs whose residual ledger is worst. Exp 53 halted at round 3 of 16 with 20
    # of 40 findings escalated; `post_convergence_sweep_rounds: 2` was configured
    # in 53_control_zero_live.json and never executed, because the run did not
    # converge. The founder is relying on this pass to clear findings the
    # machinery mis-filed, and it was absent precisely when there were most of
    # them. It costs a bounded panel dispatch and it is the difference between
    # shipping a 20-item human queue and shipping whatever survives adjudication.
    #
    # It cannot rescue a failed run: it registers no new findings, it runs after
    # the verdict is written, and criticals remain CONFIRM-only inside it. What it
    # can do is stop a halt from also being an unswept halt.
    _sweep_reason = "convergence" if converged else "halt/round-cap exit"
    if getattr(cfg, "post_convergence_sweep_rounds", 0):
        if not converged:
            _log(f"  residual-clearing sweep on {_sweep_reason} "
                 f"(run did NOT converge — the verdict above stands unchanged)")
        result["sweep_trigger"] = _sweep_reason
        try:
            result["post_convergence_sweep"] = _post_convergence_sweep(
                registry, exp_config, cfg, round_idx)
        except Exception as _sw_exc:  # noqa: BLE001 — sweep must never kill the report
            _log(f"  WARNING: post-convergence sweep failed ({_sw_exc})")
            result["post_convergence_sweep"] = {"error": str(_sw_exc)}
        else:
            # Exp 46 lesson (2026-07-28): the last round checkpoint predates
            # the sweep — persist the post-sweep registry so the saved state
            # matches the report and the per-item audit trail survives exit.
            try:
                _rs_path = logs_dir / "runner_state.json"
                _rs = json.loads(_rs_path.read_text(encoding="utf-8")) if _rs_path.exists() else {}
                _rs["registry"] = registry.to_dict()
                _rs["post_convergence_sweep"] = result["post_convergence_sweep"]
                _rs_path.write_text(json.dumps(_rs, indent=2, default=str), encoding="utf-8")
                _log("  post-sweep registry persisted to runner_state.json")
            except Exception as _ps_exc:  # noqa: BLE001
                _log(f"  WARNING: post-sweep persistence failed ({_ps_exc})")

    # IMMUNE MEMORY recording (2026-07-28, staged wiring): learn this run's
    # per-flaw-class confirmed/rejected outcome. Advisory-only, never touches
    # verdicts or the gate; failure never kills the report.
    if getattr(cfg, "immune_memory_enabled", False):
        try:
            from bench.dm._memory import ImmuneMemory
            _mem_path = str(Path(REPO_ROOT) / cfg.immune_memory_path)
            _mem = ImmuneMemory.load(_mem_path)
            _flaw_counts: Dict[int, list] = {}
            _CONF = {"CONFIRMED", "CLOSED"}
            for _e in registry.entries.values():
                _fc = int(_e.get("flaw_class") or 0)
                _cell = _flaw_counts.setdefault(_fc, [0, 0])
                if _e["status"] in _CONF:
                    _cell[0] += 1
                elif _e["status"] == "REFUTED":
                    _cell[1] += 1
            _mem.record_experiment(
                exp_id=cfg.experiment_name,
                flaw_counts={k: (v[0], v[1]) for k, v in _flaw_counts.items()},
            )
            _mem.save(_mem_path)
            _pi = {k: round(_mem.pi_mem(k), 3) for k in sorted(_flaw_counts)}
            _log(f"  immune memory: recorded {sum(v[0] for v in _flaw_counts.values())}"
                 f" confirmed / {sum(v[1] for v in _flaw_counts.values())} rejected"
                 f" across {len(_flaw_counts)} flaw classes; pi_mem now {_pi}")
            result["immune_memory"] = {"recorded": True, "pi_mem": _pi}
        except Exception as _im_exc:  # noqa: BLE001
            _log(f"  WARNING: immune memory recording failed ({_im_exc})")
            result["immune_memory"] = {"recorded": False, "error": str(_im_exc)}
        # CONSUMPTION receipt (2026-07-31): which R_k(0) values this run actually
        # drew from memory, keyed by flaw class. Recorded separately from the
        # consumption SWITCH, because the two failure modes are different and a
        # reader of the report must be able to tell them apart:
        #   consumed=False              — this run deliberately did not consume.
        #   consumed=True, receipt {}   — consumption was on and reached NOTHING,
        #                                 the "recorded but never consumed" state
        #                                 this wiring exists to end.
        _consuming = bool(getattr(cfg, "immune_memory_consume_rk0", False))
        result["immune_memory"]["rk0_consumed"] = _consuming
        result["immune_memory"]["rk0_priors_used"] = dict(rk0_priors_used)
        result["immune_memory"]["rk0_pi_base"] = RK0_PI_BASE
        result["immune_memory"]["rk0_rho"] = float(
            getattr(cfg, "immune_memory_rho", 0.2))
        if _consuming:
            _log(f"  immune memory: R_k(0) seeded from blended prior for "
                 f"{len(rk0_priors_used)} flaw class(es): {rk0_priors_used}")
        else:
            _log("  immune memory: RECORDING only — R_k(0) used the uniform "
                 f"prior {RK0_PI_BASE}; consumption is off for this experiment")

    # ── VERIFICATION CHAIN — cryptographic signing of the run record ──────
    # REINSTATED 2026-07-29 (founder directive). Signing lapsed silently when
    # the arc moved to runner v2: the last sealed chain on disk is Exp 37
    # (9 April). Every experiment from Exp 40 onward — the whole modern
    # programme — ran UNSIGNED, while the project's own documentation presents
    # tamper-evident provenance as a core property. Faithful to the original
    # spec in run_exp37_evidence.py: per-round records, per-model-response
    # records (hash_only, so payloads are not duplicated), a whole-report
    # record, then an RFC 9162 Merkle epoch seal.
    try:
        from bench.verification_chain import VerificationChain

        def _floats_to_strings(obj):
            """Floats have platform-dependent repr; stringify for deterministic
            Merkle hashing (original spec, run_exp37_evidence.py)."""
            if isinstance(obj, float):
                return f"{obj:.6g}"
            if isinstance(obj, dict):
                return {k: _floats_to_strings(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_floats_to_strings(v) for v in obj]
            return obj

        _chain = VerificationChain()
        _who = cfg.experiment_name or "reference_runner_v2"

        for _rd in result.get("rounds", []):
            _chain.append_record(
                artifact_type="experiment_round",
                payload=_floats_to_strings(_rd),
                recorded_by=_who,
                metadata={"experiment": cfg.experiment_name,
                          "round": _rd.get("round", "?"),
                          "models": _rd.get("models_responded", [])},
            )
        for _rf in sorted(logs_dir.glob("r*_*.json")):
            if _rf.name == "runner_state.json":
                continue
            try:
                _chain.append_record(
                    artifact_type="model_response",
                    payload=_floats_to_strings(
                        json.loads(_rf.read_text(encoding="utf-8"))),
                    recorded_by=_who,
                    metadata={"source_file": _rf.name,
                              "experiment": cfg.experiment_name},
                    storage_mode="hash_only",
                )
            except Exception:  # noqa: BLE001 — one unreadable file must not void the chain
                continue
        _chain.append_record(
            artifact_type="experiment_report",
            payload=_floats_to_strings(result),
            recorded_by=_who,
            metadata={"experiment": cfg.experiment_name,
                      "convergence_reason": result.get("convergence_reason", ""),
                      "converged_at": result.get("converged_at"),
                      "total_findings": total_findings,
                      "registry_entries": len(registry.entries)},
        )
        _epoch = _chain.seal_epoch()
        _chain_path = logs_dir / "experiment_chain.json"
        _chain.save_json(str(_chain_path))
        _log(f"  verification chain SEALED: {len(_chain.records)} records, "
             f"merkle_root={_epoch['merkle_root'][:24]}...")
        result["merkle_chain"] = {
            "path": str(_chain_path),
            "records": len(_chain.records),
            "merkle_root": _epoch["merkle_root"],
        }
    except Exception as _vc_exc:  # noqa: BLE001 — never lose a completed run to signing
        _log(f"  *** WARNING: verification chain NOT sealed ({_vc_exc}) — "
             f"this run is UNSIGNED and must be reported as such ***")
        result["merkle_chain"] = {"sealed": False, "error": str(_vc_exc)}

    # Save report
    report_path = logs_dir / f"{cfg.experiment_name}_report.json"
    _write_report_json(report_path, result)

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
    run_p.add_argument("--test-article",
                       help="Path to the file under review (required unless --config provides it)")
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
    run_p.add_argument("--burst-mode", default=None,
                       choices=["auto", "on", "off"],
                       help="Burst decomposition: auto (fingerprint-driven), "
                            "on (always), off (monolithic)")
    run_p.add_argument("--hil-review", action="store_true",
                       help="HIL review gate: pause after each round/phase, "
                            "save checkpoint, exit 42. Resume with --resume.")

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
    # Operational directive — R_k(i) self-assessment equation and working protocol.
    # Models MUST compute R_k on their own output (§3, §6). Without this, models
    # produce qualitative findings — not metacognitive self-assessment. Exp 37
    # demonstrated 88-100% R_k adoption across all 5 models with this directive;
    # zero adoption without it. The equation inside the models' reasoning is the
    # contribution — external scoring alone is just calculation.
    _operational_path = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
    if _operational_path.exists():
        cdsfl_text += "\n\n" + _operational_path.read_text(encoding="utf-8")

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
        if getattr(args, "burst_mode", None) is not None:
            cfg.burst_mode = args.burst_mode
        if getattr(args, "hil_review", False):
            cfg.hil_review = True
    else:
        if not args.test_article:
            parser.error("--test-article is required when --config is not provided")
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
            burst_mode=args.burst_mode or "auto",
            hil_review=getattr(args, "hil_review", False),
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
