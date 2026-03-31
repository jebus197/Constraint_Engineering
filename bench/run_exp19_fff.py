#!/usr/bin/env python3
"""Experiment 19: Find-Fix-Follow Hypothesis Test.

2-condition experiment: Standard CDSFL confer vs CDSFL + Find-Fix-Follow.
Tests whether the FFF obligation (find issue -> fix it -> trace consequences)
produces higher-quality findings and faster convergence than standard confer.

Condition A (control): Standard CDSFL -- models report findings only.
Condition B (treatment): CDSFL + FFF -- models must find, fix, and follow.

Same test articles, same models, same stop caps, same immune layer.
The ONLY difference is the situation-layer directive.

Usage:
    python3 bench/run_exp19_fff.py [preflight|canary|run]

    preflight  -- verify all models respond + Layer 1 acceptance tests
    canary     -- run induced-failure scenarios only
    run        -- full experiment (preflight + canary + Condition A + Condition B)
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from copy import deepcopy
from dataclasses import asdict
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
    run_canary_tests,
    run_layer1_preflight,
    _extract_code_area,
    _extract_task_area,
    _extract_convergent_findings,
    _should_decompose,
    _build_task_prompt,
    _build_decomposed_prompt,
    _build_subarea_prompt,
    _build_verified_facts,
    _build_explicit_unknowns,
    _build_model_responses,
    _record_telemetry,
    _find_model_spec,
    _report_dispatch_failure,
    _find_cached,
    _record_throughput,
    _effective_capacity,
    _ADVERSARIAL_BRIEF,
)
import run_exp17_immune
from cdsfl_registry.composer import (
    compose,
    compose_for_dispatch,
    DirectivePacket,
    ComposedDirectiveSet,
    COMPOSER_MODEL_MAP,
)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

EXPERIMENT = "19"
LOGS_DIR = REPO_ROOT / "bench" / "logs" / f"experiment_{EXPERIMENT}"

# Independent stop caps (inherited from Exp 16/17 convergent design)
MAX_ROUNDS = 10
WALL_CLOCK_CAP_S = 4 * 3600  # 4 hours

# Test articles (same as Exp 17)
TEST_ARTICLE_PATH = REPO_ROOT / "bench" / "dynamic_management.py"
MATH_APPENDIX_PATH = REPO_ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
VERIFICATION_CHAIN_PATH = REPO_ROOT / "bench" / "verification_chain.py"
INTERFACE_SUMMARY_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_interface_summary.md"
CONVERGENT_FINDINGS_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_plan.md"


# ─────────────────────────────────────────────────────────────────────────────
# Situation directives — the ONLY difference between conditions
# ─────────────────────────────────────────────────────────────────────────────

# Condition A: Standard CDSFL finding format (control)
STANDARD_SITUATION_TEXT = (
    "## Standard CDSFL Finding Protocol (this round)\n\n"
    "For each finding, report:\n"
    "  SEVERITY: 0.0-1.0\n"
    "  CATEGORY: the domain area affected\n"
    "  FLAW_CLASS: 1=logic, 2=interface, 3=notation, 4=completeness, "
    "5=correctness, 6=edge-case, 7=performance, 8=documentation\n"
    "  ABSTRACTION_INDEX: 0.0-1.0 (0=surface, 1=architectural)\n"
    "  DESCRIPTION: what is wrong and why\n"
    "  PROPOSED_FIX: specific fix\n"
    "  VERIFIED: TRUE/FALSE\n\n"
    "Report as many genuine findings as you can identify. "
    "Do not repeat known findings. Do not fabricate findings.\n"
)

# Condition B: Find-Fix-Follow protocol (treatment)
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


def _build_situation_directive(condition: str) -> DirectivePacket:
    """Build the condition-specific situation directive packet.

    This packet is injected into the composer as a Layer 4 (situation)
    directive — the ONLY experimental variable between conditions.
    """
    if condition == "A":
        return DirectivePacket(
            layer="situation",
            name="exp19_standard_finding_protocol",
            text=STANDARD_SITUATION_TEXT,
            constraint_class="HARD",
            tags={"exp19", "control"},
        )
    elif condition == "B":
        return DirectivePacket(
            layer="situation",
            name="exp19_fff_protocol",
            text=FFF_SITUATION_TEXT,
            constraint_class="HARD",
            tags={"exp19", "treatment", "fff"},
        )
    else:
        raise ValueError(f"Unknown condition: {condition}")


# ─────────────────────────────────────────────────────────────────────────────
# Composer integration
# ─────────────────────────────────────────────────────────────────────────────

def compose_for_condition(
    model_label: str,
    condition: str,
    *,
    review_target: str = "",
    code_extracts: str = "",
    verified_facts: str = "",
    explicit_unknowns: str = "",
    adversarial_brief: str = "",
) -> ComposedDirectiveSet:
    """Compose directive set with condition-specific situation layer.

    Calls compose() directly (not compose_for_dispatch) so we can inject
    the custom situation DirectivePacket.
    """
    composer_model = COMPOSER_MODEL_MAP.get(model_label, model_label)
    situation = _build_situation_directive(condition)

    # Append review target and context to the situation text so that
    # the situation packet carries both the protocol AND the per-dispatch
    # context (verified facts, unknowns, adversarial brief).
    context_parts = []
    if review_target:
        context_parts.append(f"\n=== REVIEW TARGET ===\n{review_target}")
    if code_extracts:
        context_parts.append(f"\n=== CODE EXTRACTS ===\n{code_extracts}")
    if verified_facts:
        context_parts.append(f"\n=== VERIFIED FACTS ===\n{verified_facts}")
    if explicit_unknowns:
        context_parts.append(f"\n=== EXPLICIT UNKNOWNS ===\n{explicit_unknowns}")
    if adversarial_brief:
        context_parts.append(f"\n=== ADVERSARIAL BRIEF ===\n{adversarial_brief}")
    if context_parts:
        situation.text += "\n".join(context_parts)

    return compose(
        task_domain="software",
        model=composer_model,
        situation=situation,
    )


# ─────────────────────────────────────────────────────────────────────────────
# FFF-specific output parser
# ─────────────────────────────────────────────────────────────────────────────

_FFF_BLOCK_RE = re.compile(
    r'\*{0,2}FIND[:\s]*\*{0,2}\s*'          # FIND: header (optional bold)
    r'(?P<find>.*?)'                          # find content
    r'\*{0,2}FIX[:\s]*\*{0,2}\s*'            # FIX: header
    r'(?P<fix>.*?)'                           # fix content
    r'\*{0,2}FOLLOW[:\s]*\*{0,2}\s*'         # FOLLOW: header
    r'(?P<follow>.*?)'                        # follow content
    r'(?=\*{0,2}FIND[:\s]|\Z)',              # lookahead: next FIND or end
    re.DOTALL | re.IGNORECASE,
)

# Diff marker pattern within FIX blocks
_DIFF_RE = re.compile(
    r'<{4}\s*(?P<old>.*?)\s*={4}\s*(?P<new>.*?)\s*>{4}',
    re.DOTALL,
)


def parse_fff_blocks(response: str) -> List[Dict[str, Any]]:
    """Parse FIND/FIX/FOLLOW blocks from a Condition B response.

    Returns a list of dicts with keys: find, fix, follow, has_diff,
    has_follow_impact, cross_section_refs.
    """
    blocks = []
    for m in _FFF_BLOCK_RE.finditer(response):
        find_text = m.group("find").strip()
        fix_text = m.group("fix").strip()
        follow_text = m.group("follow").strip()

        # Check for diff markers in fix
        diffs = _DIFF_RE.findall(fix_text)

        # Check for downstream impact in follow
        no_impact_phrases = (
            "no downstream impact",
            "no downstream effect",
            "no further consequences",
            "no additional impact",
        )
        has_follow_impact = not any(
            phrase in follow_text.lower() for phrase in no_impact_phrases
        )

        # Count cross-section references (mentions of other files, functions,
        # classes, or sections in the FOLLOW block)
        cross_refs = set()
        for token in re.findall(r'[A-Z][a-z]+(?:[A-Z][a-z]+)+', follow_text):
            cross_refs.add(token)  # CamelCase class/function names
        for token in re.findall(r'\b\w+\.py\b', follow_text):
            cross_refs.add(token)  # .py file references
        for token in re.findall(r'\b(?:def|class)\s+(\w+)', follow_text):
            cross_refs.add(token)

        blocks.append({
            "find": find_text,
            "fix": fix_text,
            "follow": follow_text,
            "has_diff": len(diffs) > 0,
            "diff_count": len(diffs),
            "has_follow_impact": has_follow_impact,
            "cross_section_refs": sorted(cross_refs),
            "cross_section_count": len(cross_refs),
        })

    return blocks


# ─────────────────────────────────────────────────────────────────────────────
# Fingerprint tracking: (D, v_bar, A, C) per condition
# ─────────────────────────────────────────────────────────────────────────────

def compute_condition_fingerprint(
    findings: List[Finding],
    rounds_completed: int,
) -> Dict[str, float]:
    """Compute aggregate capability fingerprint for a condition's findings.

    D (decay rate): inverse of rounds-to-convergence (fewer rounds = higher D)
    v_bar (mean severity): average severity of genuine findings
    A (abstraction): mean abstraction index
    C (coverage): fraction of flaw classes represented (out of 8)
    """
    if not findings:
        return {"D": 0.0, "v_bar": 0.0, "A": 0.0, "C": 0.0}

    # D: higher = converged faster. 1/rounds normalised to [0,1] via 1/max_rounds.
    d_value = (1.0 / max(rounds_completed, 1)) / (1.0 / MAX_ROUNDS)
    d_value = min(d_value, 1.0)

    # v_bar: mean severity
    v_bar = sum(f.severity for f in findings) / len(findings)

    # A: mean abstraction index
    a_value = sum(f.abstraction_index for f in findings) / len(findings)

    # C: coverage — fraction of flaw classes seen
    flaw_classes = {f.flaw_class for f in findings}
    c_value = len(flaw_classes) / 8.0

    return {"D": round(d_value, 4), "v_bar": round(v_bar, 4),
            "A": round(a_value, 4), "C": round(c_value, 4)}


# ─────────────────────────────────────────────────────────────────────────────
# Duane gamma estimation
# ─────────────────────────────────────────────────────────────────────────────

def estimate_duane_gamma(
    cumulative_findings_per_round: List[int],
) -> Optional[float]:
    """Estimate Duane reliability growth exponent gamma.

    The Duane model: N(t) = a * t^gamma, where N is cumulative findings,
    t is round number. Log-log linear regression gives slope = gamma.

    Steeper gamma = faster convergence (finding rate decays faster).
    Returns None if insufficient data (< 3 rounds).
    """
    if len(cumulative_findings_per_round) < 3:
        return None

    # Build log-log pairs: (log(t), log(N(t))) for t >= 1, N(t) >= 1
    log_t = []
    log_n = []
    cumulative = 0
    for i, count in enumerate(cumulative_findings_per_round):
        cumulative += count
        t = i + 1
        if cumulative > 0:
            log_t.append(math.log(t))
            log_n.append(math.log(cumulative))

    if len(log_t) < 3:
        return None

    # Simple linear regression: log(N) = log(a) + gamma * log(t)
    n = len(log_t)
    sum_x = sum(log_t)
    sum_y = sum(log_n)
    sum_xy = sum(x * y for x, y in zip(log_t, log_n))
    sum_xx = sum(x * x for x in log_t)

    denom = n * sum_xx - sum_x * sum_x
    if abs(denom) < 1e-12:
        return None

    gamma = (n * sum_xy - sum_x * sum_y) / denom
    return round(gamma, 4)


# ─────────────────────────────────────────────────────────────────────────────
# Throughput tracking (delegated to Exp 17 infrastructure)
# ─────────────────────────────────────────────────────────────────────────────

# Re-use Exp 17's throughput module-level state. _record_throughput and
# _effective_capacity are already imported.


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch for one condition
# ─────────────────────────────────────────────────────────────────────────────

def _dispatch_round_with_composer(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    prompt: str,
    condition: str,
    full_code: str,
    phase_label: str,
    round_idx: int,
    task_key: str,
    logs_dir: Path,
    verified_facts_text: str = "",
    unknowns_text: str = "",
) -> Tuple[List[Finding], Dict[str, str], List[Dict[str, Any]]]:
    """Dispatch prompt to all models with composer-generated system prompt.

    Returns (findings, {label: response_text}, fff_blocks).
    fff_blocks is populated only for Condition B.
    """
    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    fff_blocks_all: List[Dict[str, Any]] = []

    prompt_tokens_est = len(prompt) // 4

    for mc in exp_config.models:
        if mc.role == "collator":
            continue

        # Resume: check for cached response
        if run_exp17_immune.RESUME_MODE:
            cached = _find_cached(phase_label, mc.label)
            if cached:
                model_findings = parse_findings(mc.label, round_idx, cached)
                findings.extend(model_findings)
                responses[mc.label] = cached
                if condition == "B":
                    blocks = parse_fff_blocks(cached)
                    for b in blocks:
                        b["model"] = mc.label
                    fff_blocks_all.extend(blocks)
                _log(f"  {mc.label}: {len(model_findings)} findings (from cache)")
                continue

        # Compose system prompt via dynamic composer with condition directive
        composed = compose_for_condition(
            mc.label,
            condition,
            review_target=f"Experiment 19 Condition {condition}: {task_key}",
            verified_facts=verified_facts_text,
            explicit_unknowns=unknowns_text,
            adversarial_brief=_ADVERSARIAL_BRIEF.strip(),
        )
        system_prompt = composed.rendered_text
        _log(f"  {mc.label}: composed system prompt {len(system_prompt)} chars "
             f"(CID: {composed.cid}, density: {composed.constraint_density:.4f})")

        # Throughput-derived effective capacity
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

        # Pre-dispatch feasibility gate
        model_spec = _find_model_spec(mgr, mc.label)
        if model_spec:
            token_est = len(model_prompt) // 4
            ok, p_feasible = mgr.check_dispatch_feasibility(model_spec, token_est)
            if not ok:
                _log(f"  {mc.label}: DISPATCH BLOCKED (context window) -- "
                     f"P(feasible)={p_feasible:.3f}, ~{token_est} tokens. "
                     f"Auto-decomposing.")
                model_prompt, decomposed = _build_decomposed_prompt(
                    prompt, full_code, task_key, mc.label, round_idx,
                    max_chars=max_chars)
                mgr.config.pre_decompose_models.add(mc.label)
            elif eff_cap and len(model_prompt) > eff_cap:
                _log(f"  {mc.label}: THROUGHPUT WARNING -- prompt {len(model_prompt)} "
                     f"chars > effective capacity {eff_cap} chars. Escalating.")
                model_prompt, decomposed = _build_decomposed_prompt(
                    prompt, full_code, task_key, mc.label, round_idx,
                    max_chars=eff_cap)
                if not decomposed:
                    mgr.config.pre_decompose_models.add(mc.label)

        try:
            # Use composer system prompt instead of static cdsfl_text
            text, elapsed = dispatch_to_model(mc, model_prompt, system_prompt)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")

            _record_throughput(mc.label, len(model_prompt), elapsed)

            model_findings = parse_findings(mc.label, round_idx, text)
            findings.extend(model_findings)
            responses[mc.label] = text
            _log(f"  {mc.label}: {len(model_findings)} findings parsed")

            # Parse FFF blocks for Condition B
            if condition == "B":
                blocks = parse_fff_blocks(text)
                for b in blocks:
                    b["model"] = mc.label
                    b["round"] = round_idx
                fff_blocks_all.extend(blocks)
                _log(f"  {mc.label}: {len(blocks)} FFF blocks parsed "
                     f"({sum(1 for b in blocks if b['has_diff'])} with diffs, "
                     f"{sum(1 for b in blocks if b['has_follow_impact'])} with follow impact)")

            save_output(
                logs_dir, phase_label, mc.label,
                model_prompt[:200] + "...", text,
                metadata={
                    "elapsed": round(elapsed, 1),
                    "chars": len(text),
                    "findings_count": len(model_findings),
                    "round": round_idx,
                    "decomposed": decomposed,
                    "prompt_chars": len(model_prompt),
                    "condition": condition,
                    "composer_cid": composed.cid,
                    "constraint_density": composed.constraint_density,
                },
            )

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER -- {e}")
        except TimeoutError as e:
            _log(f"  {mc.label}: TIMEOUT -- {e}")
            _report_dispatch_failure(mgr, mc.label, round_idx, f"timeout: {e}")
        except Exception as e:
            _log(f"  {mc.label}: ERROR -- {type(e).__name__}: {e}")
            _report_dispatch_failure(mgr, mc.label, round_idx,
                                     f"{type(e).__name__}: {e}")

    return findings, responses, fff_blocks_all


# ─────────────────────────────────────────────────────────────────────────────
# Run one condition (A or B)
# ─────────────────────────────────────────────────────────────────────────────

def run_condition(
    condition: str,
    exp_config: ExperimentConfig,
    code: str,
    math_appendix: str,
    verification_chain: str,
    interface_summary: str,
    condition_logs_dir: Path,
    head_hash: str,
) -> Dict[str, Any]:
    """Run one experimental condition (A=standard or B=FFF).

    Returns a report dict with findings, rounds, fingerprint, metrics.
    """
    condition_start = time.monotonic()
    condition_label = "STANDARD CDSFL" if condition == "A" else "CDSFL + FFF"
    _log(f"\n{'='*72}")
    _log(f"CONDITION {condition}: {condition_label}")
    _log(f"{'='*72}")
    _log(f"Logs: {condition_logs_dir}")
    condition_logs_dir.mkdir(parents=True, exist_ok=True)

    # Build DynamicManager (fresh per condition — independent state)
    model_specs = build_model_specs(exp_config)
    dm_config = DynamicManagementConfig(
        immune_feedback_enabled=True,
        immune_damping_rounds=2,
        pre_decompose_models={"Codex"},
    )
    tasks = [Task(task_id=f"exp19_{condition}", token_demand=len(code) // 4,
                  flaw_class=1, criticality=0.8)]
    mgr = DynamicManager(model_specs, dm_config)

    telemetry = RoundTelemetry(condition_logs_dir)

    all_findings: List[Finding] = []
    per_task_findings: Dict[str, List[Finding]] = {t[0]: [] for t in TASKS}
    all_fff_blocks: List[Dict[str, Any]] = []
    round_results: List[Dict[str, Any]] = []
    findings_per_round: List[int] = []
    convergent_text = _extract_convergent_findings()

    def _dispatch_all_tasks(round_label: str, round_type: str,
                            round_idx: int, phase_prefix: str) -> int:
        """Dispatch all 4 tasks to all models for one round."""
        round_total = 0
        round_entry: Dict[str, Any] = {
            "round": round_label,
            "condition": condition,
        }

        for task_key, id_prefix, task_desc in [(t[0], t[1], t[2]) for t in TASKS]:
            _log(f"\n--- {round_label}: {task_desc} ---")

            prior_text = format_findings_for_context(per_task_findings[task_key])
            prompt = _build_task_prompt(
                task_key, round_label, round_type,
                code, math_appendix, verification_chain, interface_summary,
                prior_findings_text=prior_text,
                convergent_text=convergent_text if round_type == "seeded" else "",
            )
            _log(f"  Prompt: {len(prompt)} chars")

            verified_facts = _build_verified_facts(task_key, "all", round_idx)
            unknowns = _build_explicit_unknowns(task_key)

            task_findings, task_responses, task_fff = _dispatch_round_with_composer(
                exp_config, mgr, prompt, condition, code,
                f"{phase_prefix}_{task_key}", round_idx, task_key,
                condition_logs_dir,
                verified_facts_text=verified_facts,
                unknowns_text=unknowns,
            )
            per_task_findings[task_key].extend(task_findings)
            all_findings.extend(task_findings)
            all_fff_blocks.extend(task_fff)
            round_entry[task_key] = len(task_findings)
            round_total += len(task_findings)
            _log(f"  {task_desc}: {len(task_findings)} findings from "
                 f"{len(task_responses)} models")

        round_entry["total"] = round_total
        round_results.append(round_entry)
        findings_per_round.append(round_total)
        return round_total

    # ── ROUND 0A: Blind Discovery ──
    _log(f"\n=== CONDITION {condition} ROUND 0A: BLIND DISCOVERY ===")
    r0a_total = _dispatch_all_tasks("ROUND 0A (BLIND)", "blind", 0, "r0a")
    _log(f"\nRound 0A total: {r0a_total} findings across 4 tasks")

    r0a_all = all_findings[:]
    r0a_model_responses = _build_model_responses({"combined": "R0A combined"}, 0)
    if r0a_all:
        result = mgr.process_round(r0a_model_responses, r0a_all, tasks, round_cost=1.0)
        _record_telemetry(telemetry, mgr, result, 0)

    # ── ROUND 0B: Seeded Validation ──
    _log(f"\n=== CONDITION {condition} ROUND 0B: SEEDED VALIDATION ===")
    r0b_total = _dispatch_all_tasks("ROUND 0B (SEEDED)", "seeded", 1, "r0b")
    _log(f"\nRound 0B total: {r0b_total} findings across 4 tasks")

    r0b_findings = all_findings[len(r0a_all):]
    if r0b_findings:
        r0b_model_responses = _build_model_responses({"combined": "R0B combined"}, 1)
        if r0b_model_responses:
            result = mgr.process_round(r0b_model_responses, r0b_findings,
                                       tasks, round_cost=1.0)
            _record_telemetry(telemetry, mgr, result, 1)

    # ── Adaptive Rounds ──
    for round_idx in range(2, MAX_ROUNDS):
        elapsed = time.monotonic() - condition_start
        if elapsed > WALL_CLOCK_CAP_S:
            _log(f"\n  WALL-CLOCK CAP reached ({elapsed:.0f}s > {WALL_CLOCK_CAP_S}s)")
            break

        _log(f"\n=== CONDITION {condition} ROUND {round_idx}: ADAPTIVE ===")

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
            rn_model_responses = _build_model_responses(
                {"combined": f"R{round_idx} combined"}, round_idx)
            if rn_model_responses:
                result = mgr.process_round(rn_model_responses, rn_findings,
                                           tasks, round_cost=1.0)
                _record_telemetry(telemetry, mgr, result, round_idx)
        else:
            _log(f"  Zero findings across all 4 tasks -- convergence reached")
            break

    # ── Condition summary ──
    elapsed_total = time.monotonic() - condition_start
    rounds_completed = len(round_results)

    # Fingerprint
    fingerprint = compute_condition_fingerprint(all_findings, rounds_completed)

    # Duane gamma
    gamma = estimate_duane_gamma(findings_per_round)

    # Abstraction distribution
    if all_findings:
        ai_values = [f.abstraction_index for f in all_findings]
        ai_mean = sum(ai_values) / len(ai_values)
        ai_deep = sum(1 for v in ai_values if v >= 0.7) / len(ai_values)
    else:
        ai_mean = 0.0
        ai_deep = 0.0

    # Cross-section findings (Condition B only)
    cross_section_count = 0
    fff_metrics: Dict[str, Any] = {}
    if condition == "B" and all_fff_blocks:
        cross_section_count = sum(
            1 for b in all_fff_blocks if b["cross_section_count"] > 0)
        fff_metrics = {
            "total_fff_blocks": len(all_fff_blocks),
            "blocks_with_diffs": sum(1 for b in all_fff_blocks if b["has_diff"]),
            "blocks_with_follow_impact": sum(
                1 for b in all_fff_blocks if b["has_follow_impact"]),
            "cross_section_findings": cross_section_count,
            "mean_cross_refs_per_block": round(
                sum(b["cross_section_count"] for b in all_fff_blocks)
                / len(all_fff_blocks), 2),
        }

    _log(f"\n=== CONDITION {condition} SUMMARY ===")
    _log(f"Total findings: {len(all_findings)}")
    _log(f"Rounds completed: {rounds_completed}")
    _log(f"Wall clock: {elapsed_total:.0f}s ({elapsed_total/60:.1f} min)")
    _log(f"Fingerprint: D={fingerprint['D']}, v_bar={fingerprint['v_bar']}, "
         f"A={fingerprint['A']}, C={fingerprint['C']}")
    _log(f"Duane gamma: {gamma}")
    if fff_metrics:
        _log(f"FFF metrics: {json.dumps(fff_metrics)}")

    # Build condition report
    report: Dict[str, Any] = {
        "condition": condition,
        "condition_label": condition_label,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit": head_hash,
        "total_findings": len(all_findings),
        "rounds_completed": rounds_completed,
        "findings_per_round": findings_per_round,
        "rounds": round_results,
        "wall_clock_s": round(elapsed_total, 1),
        "stop_reason": (
            "convergence" if rounds_completed < MAX_ROUNDS + 2  # +2 for R0A/R0B
            else "cap"
        ),
        "fingerprint": fingerprint,
        "duane_gamma": gamma,
        "abstraction_index_mean": round(ai_mean, 4),
        "abstraction_index_deep_fraction": round(ai_deep, 4),
        "cross_section_findings": cross_section_count,
    }
    if fff_metrics:
        report["fff_metrics"] = fff_metrics

    # Save condition report
    (condition_logs_dir / f"condition_{condition}_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save all FFF blocks (Condition B)
    if all_fff_blocks:
        (condition_logs_dir / "fff_blocks.json").write_text(
            json.dumps(all_fff_blocks, indent=2, ensure_ascii=False),
            encoding="utf-8")

    # Save all findings
    findings_data = []
    for f in all_findings:
        findings_data.append({
            "finding_id": f.finding_id,
            "model_id": f.model_id,
            "round_idx": f.round_idx,
            "flaw_class": f.flaw_class,
            "severity": f.severity,
            "abstraction_index": f.abstraction_index,
            "description": f.description,
            "proposed_fix": getattr(f, "proposed_fix", ""),
        })
    (condition_logs_dir / f"condition_{condition}_findings.json").write_text(
        json.dumps(findings_data, indent=2, ensure_ascii=False), encoding="utf-8")

    return report


# ─────────────────────────────────────────────────────────────────────────────
# Comparison summary
# ─────────────────────────────────────────────────────────────────────────────

def produce_comparison(report_a: Dict, report_b: Dict) -> Dict[str, Any]:
    """Produce head-to-head comparison of Condition A vs B."""
    comparison: Dict[str, Any] = {
        "experiment": EXPERIMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "condition_a": {
            "label": report_a["condition_label"],
            "total_findings": report_a["total_findings"],
            "rounds": report_a["rounds_completed"],
            "wall_clock_s": report_a["wall_clock_s"],
            "fingerprint": report_a["fingerprint"],
            "duane_gamma": report_a["duane_gamma"],
            "abstraction_mean": report_a["abstraction_index_mean"],
            "abstraction_deep_frac": report_a["abstraction_index_deep_fraction"],
        },
        "condition_b": {
            "label": report_b["condition_label"],
            "total_findings": report_b["total_findings"],
            "rounds": report_b["rounds_completed"],
            "wall_clock_s": report_b["wall_clock_s"],
            "fingerprint": report_b["fingerprint"],
            "duane_gamma": report_b["duane_gamma"],
            "abstraction_mean": report_b["abstraction_index_mean"],
            "abstraction_deep_frac": report_b["abstraction_index_deep_fraction"],
            "cross_section_findings": report_b.get("cross_section_findings", 0),
            "fff_metrics": report_b.get("fff_metrics", {}),
        },
    }

    # Delta calculations
    a_findings = report_a["total_findings"]
    b_findings = report_b["total_findings"]
    a_rounds = report_a["rounds_completed"]
    b_rounds = report_b["rounds_completed"]

    comparison["deltas"] = {
        "findings_delta": b_findings - a_findings,
        "findings_ratio": round(b_findings / max(a_findings, 1), 3),
        "rounds_delta": b_rounds - a_rounds,
        "rounds_compression": round(
            1 - b_rounds / max(a_rounds, 1), 3) if a_rounds > 0 else 0.0,
        "gamma_delta": (
            round((report_b["duane_gamma"] or 0) - (report_a["duane_gamma"] or 0), 4)
        ),
        "abstraction_delta": round(
            report_b["abstraction_index_mean"] - report_a["abstraction_index_mean"], 4),
        "fingerprint_delta": {
            k: round(report_b["fingerprint"][k] - report_a["fingerprint"][k], 4)
            for k in ("D", "v_bar", "A", "C")
        },
    }

    # Verdict
    fff_better_count = 0
    if b_findings > a_findings:
        fff_better_count += 1
    if b_rounds < a_rounds:
        fff_better_count += 1
    gamma_a = report_a["duane_gamma"] or 0
    gamma_b = report_b["duane_gamma"] or 0
    if gamma_b > gamma_a:
        fff_better_count += 1
    if report_b["abstraction_index_mean"] > report_a["abstraction_index_mean"]:
        fff_better_count += 1
    if report_b.get("cross_section_findings", 0) > 0:
        fff_better_count += 1

    comparison["verdict"] = {
        "fff_better_on_n_metrics": fff_better_count,
        "total_metrics": 5,
        "hypothesis_supported": fff_better_count >= 3,
        "summary": (
            f"FFF outperformed standard on {fff_better_count}/5 metrics. "
            f"{'Hypothesis SUPPORTED' if fff_better_count >= 3 else 'Hypothesis NOT SUPPORTED'}."
        ),
    }

    return comparison


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment
# ─────────────────────────────────────────────────────────────────────────────

def run_experiment() -> Dict[str, Any]:
    """Run full Experiment 19: both conditions sequentially."""
    experiment_start = time.monotonic()
    _log(f"=== EXPERIMENT 19: FIND-FIX-FOLLOW HYPOTHESIS TEST ===")
    _log(f"Logs: {LOGS_DIR}")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load config
    exp_config = load_default_config()

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
    else:
        _log("WARNING: MATHEMATICAL_APPENDIX.md not found")

    verification_chain = ""
    if VERIFICATION_CHAIN_PATH.exists():
        verification_chain = VERIFICATION_CHAIN_PATH.read_text(encoding="utf-8")
        _log(f"Verification chain: {len(verification_chain)} chars")
    else:
        _log("WARNING: verification_chain.py not found")

    # Freeze manifest
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
        "config": {
            "max_rounds": MAX_ROUNDS,
            "wall_clock_cap_s": WALL_CLOCK_CAP_S,
            "conditions": ["A (Standard CDSFL)", "B (CDSFL + FFF)"],
            "immune_feedback_enabled": True,
            "immune_damping_rounds": 2,
        },
        "hypothesis": (
            "FFF (Find-Fix-Follow) produces higher-quality findings and faster "
            "convergence than standard CDSFL confer by forcing models to provide "
            "exact fixes and trace downstream consequences."
        ),
    }
    (LOGS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    _log(f"Manifest frozen: {head_hash[:8]}")

    # ── Condition A: Standard CDSFL (control) ──
    condition_a_dir = LOGS_DIR / "condition_a"
    report_a = run_condition(
        "A", exp_config, code, math_appendix, verification_chain,
        interface_summary, condition_a_dir, head_hash,
    )

    # ── Condition B: CDSFL + FFF (treatment) ──
    condition_b_dir = LOGS_DIR / "condition_b"
    report_b = run_condition(
        "B", exp_config, code, math_appendix, verification_chain,
        interface_summary, condition_b_dir, head_hash,
    )

    # ── Comparison ──
    elapsed_total = time.monotonic() - experiment_start
    comparison = produce_comparison(report_a, report_b)
    comparison["total_wall_clock_s"] = round(elapsed_total, 1)

    _log(f"\n{'='*72}")
    _log(f"EXPERIMENT 19: COMPARISON SUMMARY")
    _log(f"{'='*72}")
    _log(f"Condition A (Standard): {report_a['total_findings']} findings, "
         f"{report_a['rounds_completed']} rounds, "
         f"{report_a['wall_clock_s']:.0f}s")
    _log(f"Condition B (FFF):      {report_b['total_findings']} findings, "
         f"{report_b['rounds_completed']} rounds, "
         f"{report_b['wall_clock_s']:.0f}s")
    _log(f"\nFingerprint A: {report_a['fingerprint']}")
    _log(f"Fingerprint B: {report_b['fingerprint']}")
    _log(f"Duane gamma A: {report_a['duane_gamma']}")
    _log(f"Duane gamma B: {report_b['duane_gamma']}")
    _log(f"\nDeltas: {json.dumps(comparison['deltas'], indent=2)}")
    _log(f"\nVerdict: {comparison['verdict']['summary']}")
    _log(f"Total wall clock: {elapsed_total:.0f}s ({elapsed_total/60:.1f} min)")

    # Save comparison
    (LOGS_DIR / "experiment_19_comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save combined report
    full_report = {
        "experiment": EXPERIMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit": head_hash,
        "total_wall_clock_s": round(elapsed_total, 1),
        "condition_a": report_a,
        "condition_b": report_b,
        "comparison": comparison,
    }
    (LOGS_DIR / "experiment_19_report.json").write_text(
        json.dumps(full_report, indent=2, ensure_ascii=False), encoding="utf-8")

    return full_report


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    source_env()

    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    run_exp17_immune.RESUME_MODE = "--resume" in sys.argv

    if mode == "preflight":
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
            run_exp17_immune.RESUME_MODE = True

        if run_exp17_immune.RESUME_MODE:
            _log("=== RESUME MODE: will use cached responses where available ===")

        # Full sequence: Layer 1 preflight -> canary -> experiment
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
        import run_exp16_plan_review
        run_exp16_plan_review.LOGS_DIR = LOGS_DIR
        if not run_preflight(config):
            _log("ABORT: Model preflight failed.")
            sys.exit(1)

        _log("\nPhase 4: Experiment 19")
        report = run_experiment()

        total = (report["condition_a"]["total_findings"]
                 + report["condition_b"]["total_findings"])
        _log(f"\nExperiment 19 complete. {total} total findings across both conditions.")
        _log(f"Verdict: {report['comparison']['verdict']['summary']}")

    else:
        print(f"Usage: {sys.argv[0]} [preflight|canary|run|resume]")
        print(f"  preflight -- verify all models respond + Layer 1 tests")
        print(f"  canary    -- run induced-failure scenarios only")
        print(f"  run       -- full experiment (both conditions)")
        print(f"  resume    -- resume from cached responses")
        sys.exit(1)


if __name__ == "__main__":
    main()
