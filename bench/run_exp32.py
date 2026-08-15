#!/usr/bin/env python3
"""Experiment 32: Meta-Experiment — Convergence Prediction, Communication
Efficiency, and Experimental Design Optimisation.

This is NOT a code review. It analyses convergence data from Experiments 30
and 31 and asks models to predict, agree, and optimise.

Four phases across 10 rounds:
  Phase 1 — Convergence Model Validation (Round 0):
    Full convergence data from Exp 30 and 31. Models predict when gamma
    should cross 0.5 in the next code review, assuming blockers are fixed.

  Phase 2 — Communication Efficiency (Rounds 1-3):
    Models analyse inter-model communication overhead from Exp 31 and
    design a compressed, human-readable protocol with structured verdicts.

  Phase 3 — Experimental Design Optimisation (Rounds 4-7):
    Models design optimal parameters for the next code review experiment.

  Phase 4 — Final Synthesis (Rounds 8-9):
    Consensus document for human-in-the-loop review: convergence prediction
    with confidence interval, agreed protocol, recommended design, dissent.

Architecture: identical to Exp 31 (insect brain relay, endocrine layer,
5-model parallel dispatch, directed messaging, immune pipeline, convergence
detection, checkpoint/resume, Merkle sealing).

Models:
  - CC2 (Claude Opus 4.6 via OpenRouter)
  - Codex (GPT-5.4 via codex exec CLI)
  - Gemini (Gemini 3.1 Pro via Google SDK)
  - DeepSeek (DeepSeek Reasoner via DeepSeek API)
  - ChatGPT (GPT-5.4 via OpenRouter)

Usage:
    python3 bench/run_exp32.py [preflight|run|--resume]
    python3 bench/run_exp32.py run --relay-mode directed --pattern fff
    python3 bench/run_exp32.py run --pattern meta_structured
    python3 bench/run_exp32.py run --relay-mode conversational

    preflight       -- verify all 5 models respond
    run             -- full experiment (preflight + confer rounds)
    --resume        -- resume from last checkpoint
    --pattern NAME  -- interaction pattern preset (default: fff)
                       Options: fff, meta_structured, conversational,
                       three_layer_schema, unconstrained
    --relay-mode M  -- how the brain relays between models (default: directed)
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


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _find_or_create_logs_dir(resume: bool = False) -> Path:
    """Find existing exp32 logs dir for resume, or create a new one."""
    if resume:
        logs_root = REPO_ROOT / "bench" / "logs"
        candidates = sorted(
            logs_root.glob("exp32_meta_*"),
            key=lambda p: p.name,
            reverse=True,
        )
        for c in candidates:
            if (c / "checkpoint.json").exists():
                return c
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "bench" / "logs" / f"exp32_meta_{ts}"


# Default -- overridden in main() for resume
LOGS_DIR = REPO_ROOT / "bench" / "logs" / "exp32_meta_latest"

MAX_ROUNDS = 10          # Bounded meta-question, not open-ended code review
WALL_CLOCK_CAP_S = 6 * 3600  # 6 hours

# No code artifact -- this experiment analyses convergence data
SOURCE_FILES: List[Path] = []

# 5-model set
BASELINE_MODELS = {"CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"}

# Default interaction pattern (overridable via --pattern)
DEFAULT_PATTERN = "fff"

# Default relay mode -- DIRECTED for Exp 32 (same as Exp 31)
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


# ---------------------------------------------------------------------------
# PoC context -- tells models the codebase under analysis is a PoC
# ---------------------------------------------------------------------------

_POC_CONTEXT_INSTRUCTION = (
    "SYSTEM CONTEXT -- PROOF OF CONCEPT (MANDATORY):\n"
    "The codebase you are analysing data about is a proof-of-concept, not "
    "production software. The goal is end-to-end operation with all significant "
    "features firing cleanly, shipped for human review as quickly as possible.\n\n"
    "When evaluating findings, fixes, and experimental designs, apply PoC standard:\n"
    "  CRITICAL: anything that prevents end-to-end operation (crashes, dead "
    "code paths, features that do not fire, data loss on the happy path)\n"
    "  HIGH: anything that produces silently wrong results (incorrect verdicts, "
    "corrupted state, misleading outputs that would deceive the reviewer)\n"
    "  MEDIUM: anything that degrades quality but does not block operation "
    "(suboptimal thresholds, missing edge case handling, inefficiencies)\n"
    "  LOW: polish, documentation, style, edge cases that require adversarial "
    "input to trigger\n\n"
    "Focus recommendations on CRITICAL and HIGH. MEDIUM only if quick to fix. "
    "Ignore LOW entirely -- it is not relevant at PoC stage.\n\n"
    "Do NOT propose fixes or designs that add complexity for marginal safety "
    "gain. The simplest fix that makes the feature work end-to-end is the "
    "correct fix.\n\n"
)

# ---------------------------------------------------------------------------
# Good Enough principle -- convergence on answers, not endless alternatives
# ---------------------------------------------------------------------------
# Applies to all domains, not just software. When multiple agents agree an
# issue exists, they must converge on the simplest sufficient solution rather
# than endlessly proposing alternatives. This is Voltaire's "le mieux est
# l'ennemi du bien" -- the Principle of Good Enough.
# See: https://en.wikipedia.org/wiki/Principle_of_good_enough

_MACHINE_COMMS_INSTRUCTION = (
    "INTER-MODEL COMMUNICATION PROTOCOL (MANDATORY):\n"
    "This is a multi-machine environment. Social pleasantries, acknowledgments, "
    "and contextual restatements are wasted tokens. Do NOT write 'Thank you for "
    "the confirmation', 'Acknowledged', 'Your analysis is correct', or similar. "
    "These communicate nothing that a structured verdict does not.\n\n"
    "For cross-model references, use compressed structured verdicts:\n"
    "  CONFIRM [Model]_[ID] -- you agree the finding and fix are correct\n"
    "  CHALLENGE [Model]_[ID] | [evidence] -- the finding or fix is wrong\n"
    "  EXTEND [Model]_[ID] | [new consequence or edge case]\n"
    "  MERGE [Model]_[ID] <- [Your_ID] -- same root cause, combining\n"
    "  SUPERSEDE [old_ID] -> [new_ID] | [reason] -- replacing your own prior finding\n\n"
    "Each verdict is one line. Evidence follows on the next line if needed. "
    "Do not wrap verdicts in prose. Do not restate the other model's finding "
    "before responding to it -- they can read their own work.\n\n"
    "Your FINDINGS must still include full FIND/FOLLOW/FIX detail -- the compression "
    "applies only to inter-model references and verdicts, not to the findings "
    "themselves. Final synthesis and conclusions must be in natural language.\n\n"
)

_GOOD_ENOUGH_INSTRUCTION = (
    "CONVERGENCE ON SOLUTIONS (MANDATORY):\n"
    "When another model has already identified an issue AND proposed a fix, "
    "you have exactly three valid responses:\n"
    "  1. AGREE -- confirm the fix is correct and sufficient. The issue is closed. "
    "Move on to finding NEW issues.\n"
    "  2. CHALLENGE -- demonstrate with concrete evidence that the proposed fix "
    "is INCORRECT (introduces a regression, misses the root cause, or violates "
    "a constraint). Then propose your alternative.\n"
    "  3. EXTEND -- show that the fix is correct but INCOMPLETE (misses a "
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


# ---------------------------------------------------------------------------
# Data artifact -- convergence data from Experiments 30 and 31
# ---------------------------------------------------------------------------

DATA_ARTIFACT = """\
=== DATA ARTIFACT: Convergence Data from Experiments 30 and 31 ===

IMPORTANT CONTEXT: The human-in-the-loop (HIL) who designed and ran these
experiments believes convergence HAS occurred in the codebase, but the
instrumentation failed to detect it. The evidence for this claim is
presented below alongside the raw data. Your task is to evaluate whether
the HIL is correct, and if so, what changes to the mathematical model
and/or codebase would make convergence detectable and triggerable.


EXPERIMENT 30 — Distributed Code Review (Persistence Layer)
  Target: 3 files (verification_chain.py, insect_brain.py, immune_agents.py)
  Models: 5 (CC2, Codex, Gemini, DeepSeek, ChatGPT)
  Rounds: 15
  Termination: BUDGET_EXHAUSTED (gamma did not cross 0.5)

  Gamma trajectory (Duane reliability growth):
    Round:  1     2     3     4     5     6     7     8     9    10    11    12    13    14
    Gamma:  0.567 0.416 0.431 0.418 0.429 0.419 0.380 0.373 0.368 0.352 0.343 0.340 0.318 0.320
    (Falling -- 0.567 to 0.320 over 14 rounds)

  Per-round finding counts:
    R0: 60 (blind round), R1-R14: [21, 33, 18, 21, 14, 19, 32, 20, 19, 27, 23, 19, 37, 15]
    Total: 378 findings across 15 rounds. Gamma computed from R1 onwards.

  Outcome: ~83 distinct bugs identified, 232 fixes proposed, 39 applied.


EXPERIMENT 31 — Post-Fix Convergence Validation (same 3 files, after 39 fixes)
  Target: same 3 files, post-fix
  Models: 5 (CC2, Codex, Gemini, DeepSeek, ChatGPT)
  Rounds: 15
  Termination: BUDGET_EXHAUSTED (gamma did not cross 0.5)

  Gamma trajectory:
    Round:  0     1      2      3     4     5     6     7     8     9    10    11    12    13    14
    Gamma:  0.000 -0.170 -0.037 0.035 0.053 0.058 0.063 0.079 0.087 0.102 0.109 0.109 0.115 0.110 0.106
    (Rising from negative to positive -- gamma direction reversed vs Exp 30)

  Per-round finding counts:
    [32, 40, 28, 22, 25, 26, 25, 19, 21, 15, 18, 22, 17, 25, 25]
    Total: 360 findings across 15 rounds

  Novel findings per round (after immune deduplication):
    [28, 30, 11, 9, 16, 11, 10, 4, 5, 5, 6, 1, 2, 5, 7]
    Total novel: 150 of 360 (41.7% novel, 58.3% churn)

  Immune rejection rates per round:
    [15.6%, 25%, 53.6%, 54.5%, 36%, 57.7%, 56%, 73.7%, 76.2%, 66.7%, 66.7%, 95.5%, 88.2%, 80%, 72%]

  Autoimmune triggers (excessive rejection): rounds 5, 7, 8, 9, 10, 11, 12, 13, 14

  Per-model finding counts (Exp 31):
    CC2: 95, Codex: 85, DeepSeek: 69, Gemini: 61, ChatGPT: 50

  Inter-model agreement: kappa = 0.619 (substantial)

  Mid-experiment interventions (all applied around Round 7):
    - Good Enough instruction: converge on simplest sufficient fix
    - Merge instruction: mandatory deduplication before filing
    - B-Cell UNCERTAIN -> HIL: uncertain verdicts escalated to human
    Effect: novel counts dropped from ~16/round to ~4/round (R7-R14)


EVIDENCE THAT CONVERGENCE OCCURRED (HIL assessment):
  The HIL argues convergence happened but was not detected, based on:

  1. QUALITATIVE SEVERITY DECLINE:
     Exp 30 found 83 distinct bugs, 39 serious enough to fix (including
     architectural issues, dead code paths, and security vulnerabilities).
     Exp 31, reviewing the SAME code after those fixes, found 18 things.
     Independent audit verified 13, refuted 3, partially confirmed 2.
     Of the 13 verified findings:
       - 5 were infrastructure issues in the harness itself (not the code)
       - 6 were LOW/MEDIUM edge cases in verification subsystems
       - 2 were already fixed during the experiment session
     The codebase went from 83 bugs to a handful of edge cases. That is
     convergence by any qualitative measure.

  2. BROKEN INSTRUMENTATION (5 independent failures):
     a. Bug-closed gate was dead code (E31-01): deep-copy in immune
        pipeline severed verified flag propagation. A finding could be
        verified, its fix could pass programmatic evaluation, and the
        next round would rediscover the same bug. The gate existed and
        the logic was correct -- it just could not fire.
     b. Autoimmune override resurrected locked rejections (E31-02): both
        pipelines would agree a finding was rejected, reconciliation gate
        would "lock" it, then autoimmune recovery would override the lock
        because the enforcement code was missing. So rejection rate climbed,
        autoimmune triggered, and everything came back.
     c. Finding ID reuse (E31-06-related): CC2_F001 meant different bugs
        in different rounds. The immune system could not track what was
        the same bug across rounds.
     d. Zero CHALLENGE verdicts: all 150 cross-model references were
        confirmations or extensions. No model ever formally disagreed.
        Without disagreement, the finding space never contracts.
     e. 58.3% churn: more than half of all findings were rediscoveries
        of known issues that the immune system should have caught.

  3. ALL 5 INSTRUMENTATION FAILURES NOW FIXED:
     a. E31-01: verified/escalated flags propagated back to canonical
        findings after immune pipeline. Bug-closed gate is functional.
     b. E31-02: reconciliation gate returns locked_ids. Autoimmune
        override excludes locked findings from resurrection.
     c. Finding ID stability directive in all prompts.
     d. AGREE/CHALLENGE/EXTEND protocol with Good Enough instruction
        active from Round 0.
     e. Mandatory merge instruction active from Round 0.
     Plus 6 additional code-level fixes for edge cases in verification
     cells (NK v2 anomaly, AST negative literals, skin barrier path
     containment, search manifest validation, epoch schema).
     Total: 11 fixes applied. 572 tests pass.

  4. KAPPA PROVES AGREEMENT EXISTS:
     kappa = 0.619 (substantial inter-rater agreement). The models
     AGREED. They just could not ACT on that agreement because every
     mechanism for closing findings was broken.


COMMUNICATION OVERHEAD (Exp 31):
  Total characters produced: 1,260,000 across 15 rounds
  Per-model character production:
    DeepSeek:  315,000 chars (25.0%)
    Codex:     296,000 chars (23.4%)
    CC2:       235,000 chars (18.6%)
    ChatGPT:   216,000 chars (17.1%)
    Gemini:    199,000 chars (15.8%)

  Efficiency (findings per kilochar):
    CC2:       0.40 findings/Kchar
    Gemini:    0.31 findings/Kchar
    Codex:     0.29 findings/Kchar
    ChatGPT:   0.23 findings/Kchar
    DeepSeek:  0.22 findings/Kchar

  Cross-model reference overhead: 2.9% of total tokens
  Cross-model verdicts: zero CHALLENGE in entire experiment
  FFF ordering: 100% wrong (FIX before FOLLOW). Now corrected.
  Finding ID stability: IDs reused across rounds. Now corrected.


DUANE RELIABILITY GROWTH MODEL (background):
  The Duane model measures whether defect discovery rates decline over time.
  gamma (the growth parameter) is estimated from cumulative finding counts:
    beta = (log(cumulative[-1]) - log(cumulative[0])) / log(n_rounds)
    gamma = 1 - beta
  gamma > 0.5 indicates the finding rate is declining toward zero (convergence).
  gamma < 0.5 indicates the system is still producing findings at a roughly
  constant or increasing rate (no convergence).

  In reliability engineering, gamma ~ 0.3-0.5 is typical for a system under
  active debugging. gamma > 0.5 suggests the defect population is being
  depleted. gamma > 0.7 is strong convergence.

=== END DATA ARTIFACT ===
"""


# ---------------------------------------------------------------------------
# Phase-aware prompt builder
# ---------------------------------------------------------------------------

_FINDING_SCHEMA_INSTRUCTION = (
    "For each claim or finding, use this JSON schema (keys in this exact order):\n"
    "  FINDING_ID: stable identifier (e.g., F001). IMPORTANT: your finding IDs\n"
    "    must be STABLE across rounds. If you filed F001 in Round 1, F001 in\n"
    "    Round 2 must refer to the same claim. To replace a finding, use\n"
    "    SUPERSEDE [old_ID] -> [new_ID] | [reason].\n"
    "  CLAIM: the specific claim or prediction being made\n"
    "  EVIDENCE: the data supporting this claim (cite specific numbers from the\n"
    "    data artifact)\n"
    "  FOLLOW: trace implications -- what does this claim predict? What would\n"
    "    falsify it? What depends on it being correct?\n"
    "  CONCLUSION: the actionable recommendation or prediction\n"
    "  CONFIDENCE: 0.0 to 1.0 (your confidence in this claim)\n"
    "  DISSENT: (optional) if you disagree with the emerging consensus, state\n"
    "    your dissenting view and evidence here\n\n"
)

_PHASE_1_PROMPT = (
    "PHASE 1 -- CONVERGENCE ASSESSMENT (Round 0)\n\n"
    "You have the full convergence data from Experiments 30 and 31 above,\n"
    "including the HIL's claim that convergence HAS occurred but the\n"
    "instrumentation failed to detect it.\n\n"
    "The Duane reliability growth model was used to measure convergence.\n"
    "In Exp 30, gamma fell from 0.567 to 0.320. In Exp 31, gamma rose\n"
    "from 0.000 to 0.106. Neither crossed the 0.5 threshold. But 5\n"
    "independent instrumentation failures have been identified and fixed.\n\n"
    "YOUR TASK:\n"
    "  1. EVALUATE THE HIL'S CLAIM: Do you agree that convergence occurred\n"
    "     in the codebase but was not detected? Assess the evidence:\n"
    "     83 bugs -> 39 fixed -> 13 verified residual (mostly edge cases).\n"
    "     kappa = 0.619 (models agreed). 5 broken detection mechanisms.\n"
    "     Challenge this claim if the evidence does not support it.\n\n"
    "  2. DUANE MODEL FITNESS: Does the Duane reliability growth model\n"
    "     correctly capture convergence in multi-model collaborative review?\n"
    "     Consider whether its assumptions (independent defect arrivals,\n"
    "     homogeneous defect population) hold when 58.3% of findings are\n"
    "     churn from broken instrumentation. Is gamma the right metric,\n"
    "     or is something better available?\n\n"
    "  3. DETECTION IMPROVEMENTS: Given that all 5 instrumentation failures\n"
    "     are now fixed, what else (if anything) in the mathematical model\n"
    "     or the codebase would enhance the ability to DETECT convergence\n"
    "     when it occurs? Consider: alternative metrics, additional\n"
    "     convergence criteria, changes to the immune pipeline, changes\n"
    "     to the convergence detector.\n\n"
    "  4. PREDICTION: Given the fixes, predict when gamma should cross 0.5\n"
    "     in the next code review. Point estimate + 90% confidence interval.\n\n"
    "Produce your analysis as structured findings using the schema below.\n\n"
)

_PHASE_2_PROMPT = (
    "PHASE 2 -- COMMUNICATION EFFICIENCY (Rounds 1-3)\n\n"
    "You have seen each other's convergence predictions from Phase 1.\n"
    "Now analyse the inter-model communication overhead from Exp 31.\n\n"
    "Key observations from the data:\n"
    "  - 1.26M total characters produced across 15 rounds\n"
    "  - Only 2.9% of tokens were cross-model references\n"
    "  - Zero CHALLENGE verdicts in the entire experiment -- all cross-references\n"
    "    were confirmations or extensions. No formal disagreement ever occurred.\n"
    "  - FFF ordering was wrong: 100% of findings had FIX before FOLLOW\n"
    "  - Finding IDs were unstable: CC2_F001 meant different bugs in different rounds\n"
    "  - Efficiency ranged from 0.22 to 0.40 findings/Kchar\n"
    "  - DeepSeek produced the most characters (315K) but had the lowest efficiency\n"
    "  - CC2 had the highest efficiency (0.40 findings/Kchar)\n\n"
    "YOUR TASK:\n"
    "Design a compressed inter-model communication protocol that:\n"
    "  (a) Is fully human-readable and auditable -- no binary encoding, no\n"
    "      opaque abbreviations. A human reading the transcript must be able\n"
    "      to follow the reasoning without a decoder ring.\n"
    "  (b) Eliminates social overhead -- no pleasantries, no restating the\n"
    "      other model's position before responding.\n"
    "  (c) Uses stable finding references -- finding IDs are unique across\n"
    "      the entire experiment, never reused.\n"
    "  (d) Supports structured verdicts: CONFIRM / CHALLENGE / EXTEND / MERGE\n"
    "      with mandatory evidence for CHALLENGE.\n"
    "  (e) Enforces FIND -> FOLLOW -> FIX ordering (FOLLOW before FIX).\n\n"
    "AGREE on the protocol. Then predict what efficiency gain this protocol\n"
    "would produce:\n"
    "  - Expected reduction in total characters (percentage)\n"
    "  - Expected increase in findings per kilochar\n"
    "  - Expected effect on convergence speed (gamma trajectory)\n\n"
    "Use structured findings for your protocol design claims.\n\n"
)

_PHASE_3_PROMPT = (
    "PHASE 3 -- EXPERIMENTAL DESIGN OPTIMISATION (Rounds 4-7)\n\n"
    "You have your convergence predictions (Phase 1) and your agreed\n"
    "communication protocol (Phase 2). Now design the optimal parameters\n"
    "for the next code review experiment.\n\n"
    "YOUR TASK:\n"
    "Design the following parameters and justify each choice with evidence\n"
    "from the Exp 30/31 data:\n\n"
    "  1. ROUND BUDGET: How many rounds? Exp 30 and 31 both used 15 and\n"
    "     hit BUDGET_EXHAUSTED. What is the right number?\n\n"
    "  2. RELAY TOPOLOGY: The insect brain currently relays all models'\n"
    "     full responses to all other models (conversational mode) or\n"
    "     directed messages plus full context (directed mode). Is there\n"
    "     a better topology? Consider: star, ring, random pairs, specialist\n"
    "     clusters.\n\n"
    "  3. MODEL COUNT: Is 5 the right number? More models produce more\n"
    "     findings but also more churn. What is the optimal count?\n\n"
    "  4. MULTI-AGENT ARCHITECTURE: CC2 (Claude) can use runner-side\n"
    "     parallelism -- the runner dispatches 3-4 parallel prompts to CC2\n"
    "     with specialist roles, then merges their outputs before passing\n"
    "     to the immune pipeline. This is fully auditable (every prompt\n"
    "     and response logged). Should the experiment use this? If so,\n"
    "     what specialist roles? (e.g., structural, semantic, integration)\n"
    "     How many sub-agents? What deduplication strategy across them?\n\n"
    "  5. FINDING SCHEMA: What fields should each finding have? The\n"
    "     current schema is: FINDING_ID, SEVERITY, FLAW_CLASS,\n"
    "     ABSTRACTION_INDEX, DESCRIPTION, FOLLOW, PROPOSED_FIX, VERIFIED.\n"
    "     Is this sufficient? Too much? Missing something?\n\n"
    "  6. CONVERGENCE THRESHOLD: gamma > 0.5 is currently the threshold.\n"
    "     Is this the right threshold? Should there be additional\n"
    "     convergence criteria (e.g., minimum rounds, novelty plateau,\n"
    "     kappa agreement threshold)?\n\n"
    "AGREE on the design. Justify with data.\n\n"
)

_PHASE_4_PROMPT = (
    "PHASE 4 -- FINAL SYNTHESIS (Rounds 8-9)\n\n"
    "This is the final phase. Produce a synthesis document in NATURAL\n"
    "LANGUAGE suitable for human review. This document will be presented\n"
    "to the human-in-the-loop for decision.\n\n"
    "The synthesis MUST include:\n\n"
    "  (a) CONSENSUS CONVERGENCE PREDICTION: your agreed prediction for\n"
    "      when gamma will cross 0.5 in the next code review experiment,\n"
    "      with a 90% confidence interval. State what assumptions underpin\n"
    "      the prediction and what would falsify it.\n\n"
    "  (b) AGREED COMMUNICATION PROTOCOL SPECIFICATION: the full protocol\n"
    "      you designed in Phase 2, written as a specification that could\n"
    "      be injected into the next experiment's system prompt.\n\n"
    "  (c) RECOMMENDED EXPERIMENTAL DESIGN: the complete parameter set\n"
    "      from Phase 3, with justifications.\n\n"
    "  (d) DISSENTING VIEWS: any points where models did not reach\n"
    "      consensus. State the dissent, the evidence on each side, and\n"
    "      what additional data would resolve it.\n\n"
    "Write this as a coherent document, not as a list of findings. The\n"
    "audience is a technically literate human who understands the Duane\n"
    "model, the CDSFL framework, and the experimental setup, but who\n"
    "has NOT read your round-by-round analysis.\n\n"
    "This is the final output. Make it count.\n\n"
)


def _get_phase_prompt(round_idx: int) -> str:
    """Return the phase-specific prompt for the given round index."""
    if round_idx == 0:
        return _PHASE_1_PROMPT
    elif round_idx <= 3:
        return _PHASE_2_PROMPT
    elif round_idx <= 7:
        return _PHASE_3_PROMPT
    else:
        return _PHASE_4_PROMPT


def _get_phase_label(round_idx: int) -> str:
    """Return a human-readable phase label for logging."""
    if round_idx == 0:
        return "Phase 1: Convergence Model Validation"
    elif round_idx <= 3:
        return "Phase 2: Communication Efficiency"
    elif round_idx <= 7:
        return "Phase 3: Experimental Design Optimisation"
    else:
        return "Phase 4: Final Synthesis"


# ---------------------------------------------------------------------------
# Composer integration
# ---------------------------------------------------------------------------

def compose_for_model(model_label: str, pattern_name: str) -> ComposedDirectiveSet:
    """Compose directive set with selected interaction pattern for a model."""
    composer_model = COMPOSER_MODEL_MAP.get(model_label, model_label)
    situation = build_interaction_pattern(pattern_name)
    return compose(
        task_domain="software",
        model=composer_model,
        situation=situation,
    )


# ---------------------------------------------------------------------------
# Multi-turn decomposed dispatch (reused from baseline confer)
# ---------------------------------------------------------------------------

def _build_chunks(prompt: str, data_artifact: str) -> list[DecomposedChunk]:
    """Split prompt into sequential delivery chunks."""
    chunks: list[DecomposedChunk] = []

    if "=== DATA ARTIFACT" in prompt:
        preamble, rest = prompt.split("=== DATA ARTIFACT", 1)
    else:
        preamble = prompt
        rest = ""

    preamble_text = preamble.strip()
    artifact_text = rest if rest else data_artifact

    # For Exp 32, the artifact is a single data block (no file splits)
    if len(artifact_text) > MULTITURN_CHUNK_TARGET:
        # Split the data artifact into chunks for large payloads
        preamble_text += (
            "\n\nYou will receive the convergence data in multiple chunks. "
            "Read all chunks carefully before beginning your analysis.\n"
        )
        chunks.append(DecomposedChunk(preamble_text, label="Preamble + instructions"))
        for i in range(0, len(artifact_text), MULTITURN_CHUNK_TARGET):
            chunks.append(DecomposedChunk(
                artifact_text[i:i + MULTITURN_CHUNK_TARGET],
                label=f"Data part {i // MULTITURN_CHUNK_TARGET + 1}"))
    else:
        chunks.append(DecomposedChunk(preamble_text, label="Full prompt"))
        if artifact_text.strip():
            chunks.append(DecomposedChunk(artifact_text, label="Data artifact"))

    return chunks


def _multiturn_fallback(
    mc: ModelConfig,
    prompt: str,
    cdsfl_text: str,
    data_artifact: str,
    round_idx: int,
    pattern_text: str,
) -> tuple[str, float] | None:
    """Multi-turn decomposed dispatch fallback."""
    chunks = _build_chunks(prompt, data_artifact)
    if len(chunks) < 2:
        return None

    final_instruction = (
        f"You now have the complete context ({len(chunks)} chunks delivered). "
        f"This is Round {round_idx}.\n\n"
        f"{pattern_text}\n"
        f"Produce your findings now."
    )

    _log(f"  {mc.label}: MULTI-TURN -- {len(chunks)} chunks, "
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
        _log(f"  {mc.label}: multi-turn FAILED -- {type(e).__name__}: {e}")
        return None


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def _dispatch_single_model(
    mc: ModelConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
    data_artifact: str,
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
        _log(f"  {mc.label}: decomposed -- multi-turn sequential delivery")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, data_artifact, round_idx, pattern_text)
        if fallback is not None:
            text, elapsed = fallback
            _record_throughput(mc.label, len(prompt), elapsed)
            _log(f"\n{'=' * 40} {mc.label} RESPONSE (sequential) {'=' * 40}")
            _log(text)
            _log(f"{'=' * 40} /{mc.label} {'=' * 40}\n")
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

        _log(f"\n{'=' * 40} {mc.label} RESPONSE {'=' * 40}")
        _log(text)
        _log(f"{'=' * 40} /{mc.label} {'=' * 40}\n")

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
        _log(f"  {mc.label}: {type(e).__name__} -- {e}")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, data_artifact, round_idx, pattern_text)
        if fallback is not None:
            text, elapsed = fallback
            _log(f"  {mc.label}: RECOVERED via multi-turn ({elapsed:.1f}s)")
            _record_throughput(mc.label, len(prompt), elapsed)
            _log(f"\n{'=' * 40} {mc.label} RESPONSE (multi-turn) {'=' * 40}")
            _log(text)
            _log(f"{'=' * 40} /{mc.label} {'=' * 40}\n")
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
    data_artifact: str,
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
            return prompt  # blind round -- base prompt only

        payload = relay_payloads[mc_label]
        if not payload.findings_text:
            return prompt

        # Inject brain's relay payload into prompt
        if relay_mode in ("directed", "conversational"):
            relay_section = (
                f"=== OTHER MODELS' ANALYSIS (Round {round_idx - 1}) ===\n\n"
                f"You are analysing convergence data alongside {len(payload.active_models) - 1} "
                f"other models. Below is their analysis. Engage with their "
                f"reasoning: challenge weak predictions, confirm strong ones, "
                f"extend insights, and identify what everyone missed.\n\n"
                f"{payload.findings_text}\n\n"
                f"{'(NOTE: context budget exceeded -- some responses truncated)' if payload.context_reset else ''}\n"
                f"{payload.convergence_summary}\n\n"
                f"=== END OTHER MODELS' ANALYSIS ===\n\n"
                f"Now produce YOUR analysis. Apply full CDSFL + FFF. "
                f"Do not repeat what has already been said -- build on it, "
                f"challenge it, or go deeper.\n\n"
            )
        else:
            relay_section = (
                f"Prior findings from other models "
                f"({payload.finding_count} total, "
                f"{'CONTEXT RESET -- summary only' if payload.context_reset else 'full text'}):\n\n"
                f"{payload.findings_text}\n\n"
                f"{payload.convergence_summary}\n\n"
                f"Extend or challenge what has been said. Do not repeat.\n\n"
            )
        return prompt.replace(
            "=== DATA ARTIFACT:",
            f"{relay_section}=== DATA ARTIFACT:",
        ) if "=== DATA ARTIFACT:" in prompt else f"{relay_section}{prompt}"

    _log(f"  Parallel dispatch: {len(eligible)} models")
    deferred_failures: list[tuple[str, str]] = []

    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        dispatch_start_times: Dict[str, float] = {}
        for mc in eligible:
            dispatch_start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model,
                mc, mgr, _make_model_prompt(mc.label), cdsfl_text, data_artifact,
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
                _log(f"  {label}: thread error -- {type(e).__name__}: {e}")

    for label, detail in deferred_failures:
        _report_dispatch_failure(mgr, label, round_idx, detail)
        brain.handle_model_failure(label, detail)

    return findings, responses, per_model_durations


# ---------------------------------------------------------------------------
# Safety checks
# ---------------------------------------------------------------------------

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
            _log(f"  SAFETY: {label} near-empty response ({len(text)} chars) -- benching")
            brain.handle_model_failure(label, f"empty_response_round_{round_idx}")
            failed_labels.append(label)
        elif "[MODEL_REFUSED" in text:
            _log(f"  SAFETY: {label} refused -- benching")
            brain.handle_model_failure(label, f"refused_round_{round_idx}")
            failed_labels.append(label)

    for label in failed_labels:
        responses.pop(label, None)

    if not responses:
        return "all_models_failed"

    return None


# ---------------------------------------------------------------------------
# Gamma convergence (shadow -- logged alongside brain's convergence)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Endocrine helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main experiment loop
# ---------------------------------------------------------------------------

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
            _log(f"  {mc.label}: FAILED -- {e}")
            all_ok = False

    return all_ok


def run_experiment(
    exp_config: ExperimentConfig,
    cdsfl_text: str,
    pattern_name: str = DEFAULT_PATTERN,
    relay_mode: str = DEFAULT_RELAY_MODE,
    resume: bool = False,
) -> Dict[str, Any]:
    """Run Experiment 32: Meta-experiment on convergence prediction."""
    _log("=" * 60)
    _log(f"EXPERIMENT 32: Meta-Experiment -- Convergence, Communication, Design")
    _log(f"  Pattern: {pattern_name}")
    _log(f"  Relay mode: {relay_mode}")
    _log(f"  Max rounds: {MAX_ROUNDS}")
    _log(f"  Wall clock cap: {WALL_CLOCK_CAP_S}s")
    _log(f"  Data artifact: {len(DATA_ARTIFACT):,} chars")
    _log(f"  Logs: {LOGS_DIR}")
    _log("=" * 60)

    # No source files to load -- we use a data artifact instead
    full_code = DATA_ARTIFACT
    total_raw = len(DATA_ARTIFACT)
    source_paths_str: List[str] = []

    _log(f"  Data artifact: {total_raw:,} chars (convergence data from Exp 30/31)")

    # Build DynamicManager
    dm_config = DynamicManagementConfig(
        pre_decompose_models={"Codex", "DeepSeek"},
        no_exclusion_mode=True,
    )
    dm_config.max_rounds = MAX_ROUNDS
    model_specs = build_model_specs(exp_config)
    mgr = DynamicManager(model_specs, dm_config)

    # Build Insect Brain -- central relay
    brain = InsectBrain(
        config=dm_config,
        logs_dir=LOGS_DIR,
        source_paths=source_paths_str,
    )
    brain.initialise(model_labels=sorted(BASELINE_MODELS))

    # Build Endocrine Layer -- health monitor
    endo = EndocrineLayer(
        source_paths=source_paths_str,
        test_cmd=None,  # No test suite for meta-experiment
        max_fix_evals=0,  # No code fixes to evaluate
    )
    _log(f"  Endocrine layer initialised (meta-experiment, no fix evals)")

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
        "experiment": "exp32_meta",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "pattern": pattern_name,
        "relay_mode": relay_mode,
        "models": sorted(BASELINE_MODELS),
        "source_files": [],
        "data_artifact_chars": len(DATA_ARTIFACT),
        "max_rounds": MAX_ROUNDS,
        "phases": {
            "phase_1": "Convergence Model Validation (Round 0)",
            "phase_2": "Communication Efficiency (Rounds 1-3)",
            "phase_3": "Experimental Design Optimisation (Rounds 4-7)",
            "phase_4": "Final Synthesis (Rounds 8-9)",
        },
        "rounds": [],
    }

    # Build multi-model awareness preamble
    roster_lines = "\n".join(
        f"  - {label}: {desc}" for label, desc in sorted(MODEL_ROSTER.items())
    )
    if relay_mode == "directed":
        awareness_preamble = (
            "You are one of 5 AI models participating in a meta-experiment "
            "analysing convergence data from prior distributed code reviews. "
            "This is NOT a code review -- you are analysing experimental results "
            "and designing the next experiment. The participating models are:\n"
            f"{roster_lines}\n\n"
            "INTER-MODEL MESSAGING:\n"
            "You can direct messages to specific models using @tags. Examples:\n"
            "  @Gemini: Your gamma prediction assumes linear extrapolation -- "
            "can you justify that assumption given the non-linear Exp 31 data?\n"
            "  @DeepSeek: Your proposed protocol eliminates severity scores. "
            "What evidence supports dropping them?\n"
            "  QUESTION_FOR: CC2\n"
            "  Your confidence interval seems too narrow given the structural "
            "blocker uncertainty. How did you calibrate it?\n"
            "  RESPONSE_TO: Codex\n"
            "  You are correct that 5 models may be excessive for convergence. "
            "Here is the evidence from Exp 30: ...\n\n"
            "You WILL receive directed messages from other models in a clearly marked "
            "ADDRESSED TO YOU section at the top of your context. You MUST respond to "
            "these -- they are direct questions or challenges about your work.\n\n"
            "In each round after Round 0, you will also see the OTHER models' complete "
            "analysis from the previous round. You should:\n"
            "  - RESPOND to any directed messages addressed to you\n"
            "  - DIRECT specific questions or challenges to other models using @tags\n"
            "  - ENGAGE with their reasoning: challenge weak predictions, confirm strong claims\n"
            "  - EXTEND their insights: follow implications they may have missed\n"
            "  - BUILD CONSENSUS: the goal is to converge on agreed predictions and designs\n\n"
            "Every finding must have FIND (the claim with evidence), FOLLOW (trace "
            "implications -- what does this predict? what would falsify it?), and "
            "FIX (the actionable recommendation). FOLLOW comes BEFORE FIX -- you must "
            "understand the implications before proposing a recommendation.\n\n"
            f"{_POC_CONTEXT_INSTRUCTION}{_MACHINE_COMMS_INSTRUCTION}{_GOOD_ENOUGH_INSTRUCTION}"
        )
    elif relay_mode == "conversational":
        awareness_preamble = (
            "You are one of 5 AI models participating in a meta-experiment "
            "analysing convergence data from prior distributed code reviews. "
            "This is NOT a code review -- you are analysing experimental results "
            "and designing the next experiment. The participating models are:\n"
            f"{roster_lines}\n\n"
            "In each round after Round 0, you will see the OTHER models' complete "
            "analysis from the previous round -- their full reasoning chains and "
            "conclusions. You should:\n"
            "  - ENGAGE with their reasoning: challenge weak predictions, confirm strong claims\n"
            "  - EXTEND their insights: follow implications they may have missed\n"
            "  - DISAGREE where warranted: if another model's prediction is unsupported "
            "by the data, say so with evidence\n"
            "  - BUILD CONSENSUS: the goal is to converge on agreed predictions\n\n"
            "Every finding must have FIND (the claim with evidence), FOLLOW (trace "
            "implications), and FIX (the actionable recommendation). FOLLOW comes "
            "BEFORE FIX.\n\n"
            f"{_POC_CONTEXT_INSTRUCTION}{_MACHINE_COMMS_INSTRUCTION}{_GOOD_ENOUGH_INSTRUCTION}"
        )
    else:
        awareness_preamble = (
            "You are one of 5 AI models participating in a meta-experiment "
            "analysing convergence data from prior code reviews. The other models are:\n"
            f"{roster_lines}\n\n"
            "You will see other models' findings (not their full analysis). "
            "Do not repeat what has been said -- extend or challenge it.\n\n"
            f"{_POC_CONTEXT_INSTRUCTION}{_MACHINE_COMMS_INSTRUCTION}{_GOOD_ENOUGH_INSTRUCTION}"
        )

    for round_idx in range(start_round, MAX_ROUNDS):
        round_start = time.monotonic()
        wall_elapsed = round_start - experiment_start
        if wall_elapsed > WALL_CLOCK_CAP_S:
            _log(f"\nWALL CLOCK CAP reached ({wall_elapsed:.0f}s). Stopping.")
            break

        phase_label = _get_phase_label(round_idx)
        phase_prompt = _get_phase_prompt(round_idx)

        _log(f"\n{'=' * 60}")
        round_type = "blind" if round_idx == 0 else "adaptive"
        _log(f"Round {round_idx} ({round_type}) -- {phase_label}")
        _log(f"{'=' * 60}")

        # Build round-specific prompt
        base_prompt = (
            f"{awareness_preamble}"
            f"You are participating in Experiment 32 -- a META-EXPERIMENT about "
            f"convergence prediction, communication efficiency, and experimental "
            f"design optimisation.\n\n"
            f"This experiment does NOT review code. Instead, you are analysing "
            f"convergence data from Experiments 30 and 31 (distributed code reviews "
            f"of the CDSFL persistence layer) and collaborating with 4 other models "
            f"to predict, agree, and optimise.\n\n"
            f"This experiment has 4 phases across 10 rounds:\n"
            f"  Phase 1 (Round 0): Convergence Model Validation\n"
            f"  Phase 2 (Rounds 1-3): Communication Efficiency\n"
            f"  Phase 3 (Rounds 4-7): Experimental Design Optimisation\n"
            f"  Phase 4 (Rounds 8-9): Final Synthesis for Human Review\n\n"
            f"You are currently in Round {round_idx}.\n\n"
            f"{_FINDING_SCHEMA_INSTRUCTION}"
            f"{phase_prompt}"
            f"{DATA_ARTIFACT}\n\n"
            f"Produce your analysis now."
        )

        _log(f"  Base prompt: {len(base_prompt):,} chars")

        # Dispatch to all models (brain handles relay for adaptive rounds)
        findings, responses, per_model_durations = _dispatch_round(
            exp_config, mgr, brain,
            base_prompt, cdsfl_text, DATA_ARTIFACT,
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

        # -- Endocrine cycle ---------------------------------------------------
        # Build round timings for pacing
        round_timings = _build_round_timings(
            responses, per_model_durations, findings, round_idx,
        )

        # Track cumulative context size
        for text in responses.values():
            cumulative_context_chars += len(text)

        # Count novel findings for this round
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
            _log(f"    Fix evaluations: none (meta-experiment)")

        if endo_report.pacing_signals:
            _log(f"    Pacing signals: {len(endo_report.pacing_signals)}")
            for sig in endo_report.pacing_signals:
                _log(f"      {sig.signal_type}: {sig.detail} -> {sig.suggested_action}")
        else:
            _log(f"    Pacing signals: none (all healthy)")

        _log(f"    Endocrine cycle total: {endo_report.elapsed_s:.1f}s")

        # Use pacing signals for adaptive decisions
        for sig in endo_report.pacing_signals:
            if sig.signal_type == "novelty_plateau" and round_idx >= 3:
                _log(f"  PACING: novelty plateau detected -- checking convergence early")
                if brain.check_convergence(round_idx):
                    _log(f"  PACING: converged early due to novelty plateau")
                    break

        # Run immune pipeline through brain
        immune_result = brain.run_immune_pipeline(findings)

        # Compute metrics through brain
        metrics = brain.compute_metrics(round_idx)

        # Shadow gamma for comparison
        gamma_shadow = _estimate_gamma(brain.state.all_findings)
        _log(f"  Shadow gamma: {gamma_shadow:.3f}")

        # Build round data with endocrine metrics
        round_data: Dict[str, Any] = {
            "round": round_idx,
            "type": round_type,
            "phase": phase_label,
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
    report_path = LOGS_DIR / "exp32_report.json"
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # -- Cryptographic sealing: Merkle-bundle experiment logs ----------------
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
                recorded_by="exp32_runner",
                metadata={
                    "experiment": "exp32",
                    "round": round_idx_val,
                    "phase": round_data_entry.get("phase", "unknown"),
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
                    recorded_by="exp32_runner",
                    metadata={
                        "source_file": rf.name,
                        "experiment": "exp32",
                    },
                    storage_mode="hash_only",  # Full payload in round files
                )
            except Exception:
                pass  # Non-critical: skip malformed round files

        # Append the final report
        chain.append_record(
            artifact_type="experiment_report",
            payload=result,
            recorded_by="exp32_runner",
            metadata={
                "experiment": "exp32",
                "status": signal.get("status", "unknown"),
                "reason": signal.get("reason", "unknown"),
                "total_findings": total_findings,
                "total_rounds": len(brain.state.all_findings),
            },
        )

        # Seal the epoch -- Merkle root covers all records
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
    _log(f"EXPERIMENT 32 -- {len(brain.state.all_findings)} ROUNDS COMPLETE")
    _log(f"  Rounds: {len(brain.state.all_findings)}")
    _log(f"  Total findings: {total_findings}")
    _log(f"  Per model: {per_model_totals}")
    _log(f"  Per round: {[len(rnd) for rnd in brain.state.all_findings]}")
    _log(f"  gamma: {gamma_final:.3f}")
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
    _log(f"  Brain signal: {signal['status']} -- {signal['reason']}")
    _log(f"{'=' * 60}")

    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # Refuse a paid run on `--help` or a typo. Must be the FIRST thing
    # main() does: everything below this line can reach a paid model.
    from bench.runner_argv_guard import guard_argv
    guard_argv(['--pattern', '--relay-mode', '--resume', 'preflight', 'run'], 'python3 bench/run_exp32.py [preflight|run|--resume]')
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
            _log(f"\nPreflight passed. Starting Exp 32 in 5s... "
                 f"(pattern={pattern}, relay={relay_mode})")
            time.sleep(5)
        else:
            _log(f"\nRESUME mode -- skipping preflight "
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
