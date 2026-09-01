#!/usr/bin/env python3
"""
Exp 40-54 Consolidated Plan — Panel Review Round 2 (compelled convergence)
==========================================================================

Round 1 produced splits the hub (CC1) MUST NOT synthesise into "consensus"
in its own head. This round re-dispatches to the same five models with
every model's Round 1 position made visible, and an explicit instruction:
yield to the opposing position with reasons that address the opposing
argument directly, OR refute the opposing position with reasons that
address the opposing argument directly. Splitting-and-moving-on is not
accepted as a terminal state.

Round 1 outcome:
    experimental_notes/Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md

Plan under review:
    experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md

Framing anchors:
    - bench/exp40_configs/40_gate.json pass_condition
    - Stage 6 orthogonality (R_k / nu_k / c_ext independent)
    - 15-experiment arc: 14 component studies (Exp 40-53) + 1 integration
      (Exp 54). Exp 54 is NEVER "the next experiment after Exp 40".
    - Reference runner v1 = bench/reference_runner.py (frozen Exp 38/39
      historical baseline). Reference runner v2 = bench/reference_runner_v3.py
      (4922 lines, active for Exp 40-54). Name v2 explicitly.
    - Cell types (DENDRITIC, CYTOTOXIC_T, B_CELL, NK_CELL, HELPER_T,
      REGULATORY_T) are dispatch units; tools (~20 entries in
      bench/cdsfl_registry/tool_manifest.toml) are verifier primitives.
      Cell types are NOT tools. "Biology specialist biopython routing"
      is a category error. A specialist routes claims across MULTIPLE
      tools per the domain config at
      bench/cdsfl_registry/domains/immune/<domain>.toml.

Models:   Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4,
          DeepSeek R1-0528
Dispatch: parallel via ThreadPoolExecutor(max_workers=5), star topology
          (each model talks only to CC1; no cross-model leakage)
"""

from __future__ import annotations

import concurrent.futures
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli,
    call_gemini,
    call_openrouter,
)

# Load .env
_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#"):
            continue
        if _line.startswith("export "):
            _line = _line[7:]
        if "=" in _line:
            _k, _, _v = _line.partition("=")
            _k = _k.strip()
            _v = _v.strip().strip("'\"")
            import os  # noqa: E402
            os.environ.setdefault(_k, _v)

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40to54_plan_review_round2_2026-04-21"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("gemini",   "gemini-3.1-pro-preview",     "gemini_native"),
    ("codex",    "openai/gpt-5.4",             "openrouter"),
    ("cc2",      "opus",                       "claude_cli"),
    ("chatgpt",  "openai/gpt-5.4",             "openrouter"),
    ("deepseek", "deepseek/deepseek-r1-0528",  "openrouter"),
]

# ---------------------------------------------------------------------------
# CDSFL system prompt
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Round 1 outcome (per-RQ per-model positions)
# ---------------------------------------------------------------------------

ROUND1_PATH = REPO_ROOT / "experimental_notes" / "Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md"
ROUND1_TEXT = ROUND1_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Corrected framing preamble (standing anchors + Round 2 corrections)
# ---------------------------------------------------------------------------

CORRECTED_FRAMING = r"""
## Corrected framing for Exp 40-54 plan review Round 2 (load-bearing)

This is Round 2 of a compelled-convergence plan review. Round 1 produced
splits on every question. The hub (CC1) MUST NOT synthesise "consensus"
from a 3-2 or 2-3 split in its own head — that is CC1-synthesis
masquerading as panel convergence, and has been flagged as a failure
mode. The panel itself must converge. This round asks each model to
either YIELD to the opposing position with reasons that directly address
the opposing argument, or REFUTE the opposing position with reasons
that directly address the opposing argument. Splitting and moving on
is not an accepted terminal state.

Standing anchors (all apply unchanged from Round 1):

1. `bench/exp40_configs/40_gate.json` acceptance criterion for Exp 40:
   `"pass_condition": "gamma >= 0.30 OR (3 consecutive rounds with 0
   novel CRITICAL findings). Gamma-alt implemented in
   reference_runner_v3._check_gamma_alt_convergence."`

2. Stage 6 orthogonality (canonical). R_k measures VALIDITY, nu_k
   measures NOVELTY, c_ext measures SEARCH QUALITY. The three are
   independent reporting dimensions and MUST NEVER be collapsed into
   a single score before reporting.

3. The "v1 preservation" framing (refuted 2026-04-20) is forbidden.
   `bench/reference_runner.py` is v1, frozen on disk ONLY as a
   historical baseline for the Exp 38/39 Stage 6 demonstration.
   `bench/reference_runner_v3.py` is v2, 4922 lines, actively extended,
   and IS the Exp 40 runner through to Exp 54. Any argument that
   depends on v2 "preserving v1 behaviour" is invalid.

Round 2 additional corrections (load-bearing):

A. The plan contains 15 experiments, not 1. Exp 40-53 are 14 component
   studies each examining a distinct aspect of the framework; Exp 54
   is the final overall integration round. "Exp 54 is the next
   experiment after Exp 40" is WRONG. There are thirteen intervening
   component experiments (Exp 41-53), and the primary landing zone for
   a fix or a runtime-check activation is usually one of those
   thirteen, not deferral to Exp 54. When a Round 1 answer deferred
   behavioural decisions "to Exp 54", re-examine whether one of the
   thirteen component experiments is the correct landing zone.

B. Cell types are NOT tools. Cell types (DENDRITIC, CYTOTOXIC_T,
   B_CELL, NK_CELL, HELPER_T, REGULATORY_T) are defined in
   `bench/immune_agents.py` as a `CellType` enum. They are dispatch
   units that return `CellVerdict` objects. Tools (~20 entries) are
   verifier primitives defined in
   `bench/cdsfl_registry/tool_manifest.toml` —
   `sympy`, `z3`, `statsmodels`, `scipy`, `dimensional_analysis`
   (pint), `uncertainty_propagation` (uncertainties),
   `stoichiometric_balance`, `linear_programming` (PuLP),
   `astronomical` (astropy), `chemistry_structure` (RDKit),
   `biological_sequence` (Biopython), `ml_claim` (sklearn),
   `graph_property` (NetworkX), `type_checker` (mypy), `lint_check`
   (ruff), `security_scan` (bandit), `bytecode_analysis` (dis),
   `symbolic_execution` (crosshair), `deepseek_formal`. The B-Cell
   specialist for a given domain routes claims across the tool list
   declared in `bench/cdsfl_registry/domains/immune/<domain>.toml`,
   grouped by claim_type. The biology B-Cell specialist, for example,
   routes mathematical claims to `sympy + biological_sequence +
   dimensional_analysis`, logical claims to `z3`, and statistical
   claims to `statsmodels + scipy + uncertainty_propagation`. Writing
   "biology specialist biopython routing" is a category error.
   Arguments that equate a specialist with a single tool are invalid
   and must be re-grounded in the three-layer cell/tool/domain-config
   architecture before the panel's Round 2 position is finalised.

C. Compelled convergence: no menu-for-hub. Each model gives one
   definitive Round 2 position per question. Divergence after Round 2
   must be declared explicitly with its reasoning; it will then be
   addressed in a Round 3 rather than synthesised by the hub.
"""

# ---------------------------------------------------------------------------
# Stage 6 math block (canonical, unchanged from Round 1)
# ---------------------------------------------------------------------------

STAGE6_MATH = r"""
## CDSFL Stage 6 — Unified Self-Assessment Equation (canonical)

### Recursive state

    R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))
    q     = eta * d * p

### Stage 6 eta decomposition (literature-calibrated novelty)

    eta_combined = eta_int * (1 - c_ext * (1 - nu_k))

where:
    eta_int  in [0,1]   internal novelty (within session)
    nu_k     in [0,1]   literature novelty (per-finding, Ouroboros)
    c_ext    in [0,1]   source-diversity corroboration = 1 - prod_s (1 - c_s)

### Orthogonality (load-bearing)

    R_k    measures VALIDITY
    nu_k   measures NOVELTY
    c_ext  measures SEARCH QUALITY

### Divergence modulator channel

    m_div in {1.00, 0.85, 0.70, 0.60}
    eta_int_modulated = m_div * eta_int
    eta_combined = eta_int_modulated * (1 - c_ext * (1 - nu_k))

    FORBIDDEN: m_div as pre-factor on R_k.
    FORBIDDEN: m_div counting toward nu_k.
    FORBIDDEN: w(f) in q_eff.
"""

# ---------------------------------------------------------------------------
# Round 1 per-RQ positions (for yield-or-refute prompting)
# ---------------------------------------------------------------------------

ROUND1_POSITIONS = r"""
## Round 1 positions — per RQ, per model

The full Round 1 outcome document is appended below for reference.
Per-RQ position summaries:

### RQ1 — Unaddressed fix against 40_gate.json
- Gemini: NO — F1-F4 sufficient
- Codex: YES — add live-path preflight for section-17 admissibility parser on bench/dm/_feedback.py
- CC2: NO — F1-F4 sufficient (argued from codebase grounding: admissibility/divergence signal generation independent of F2 wrapper wiring; gamma-alt convergence path via reference_runner_v3._check_gamma_alt_convergence at line 1064 reads thresholds already present in 40_gate.json)
- ChatGPT: NO — F1-F4 sufficient
- DeepSeek: YES — add section-17 [VERIFY:current] flag handling and section-18 cosmetic-rewrite suppression
Split: 3 NO / 2 YES.

### RQ2 — Cross-experiment interaction missed in the lessons-forward chain
- Gemini: YES — Exp 46 (section-18 target) alters modulation engine, invalidating Exp 41-45 calibrations
- Codex: YES — treatment-conditioned tier-calibration drift crossing Exp 40-49 into Exp 54
- CC2: NO — math-stats overlap is subcase of routing imbalance, caught at Exp 44 / Exp 49 integration
- ChatGPT: YES — threshold-calibration drift across Exp 40-53 under co-live section-17 plus section-18, reused in Exp 54 B and C cells
- DeepSeek: NO — S_k-Microglia interaction already gated by Exp 42
Split: 3 YES / 2 NO.

### RQ3 — Exp 54 factorial attribution sufficiency
- Gemini: NO — Cell A confounded by 14 experiments of runner evolution; propose fresh Cell A run at Exp 54 codebase with section-17 and section-18 both off
- Codex: YES conditional on archive comparability — two-way ANOVA sufficient
- CC2: YES conditional on Gate C Cell A integrity check — two-way ANOVA on round-level metrics
- ChatGPT: YES conditional on frozen scoring rules across cells — two-way GLM with interaction
- DeepSeek: YES — linear mixed model; if Cell A corrupt, use Cell B and C early rounds as proxy baseline
Split: 4 YES conditional / 1 NO. Gemini's dissent raises runner-version confound, not merely archive integrity.

### RQ4 — Shadow-promotion-now offsetting risk
- Gemini: POLICY SAFE unconditionally
- Codex: CONDITIONALLY SAFE — promoted channels auditable against Stage 6 orthogonality; F3 debug assertion catches hidden coupling in q
- CC2: CONDITIONALLY SAFE — F2 1e-9 regression gate plus Exp 49 cross-domain recalibration checkpoint
- ChatGPT: CONDITIONALLY SAFE — promoted component must be pipeline-neutral w.r.t. pass_condition before live
- DeepSeek: POLICY SAFE — noise contained to logs; calibration uses late-session data
Split: 2 SAFE / 3 CONDITIONALLY SAFE.

### RQ5 — Ordering of Exp 41-53
- Gemini: YES — move Exp 46 (section-18 target) to Exp 41 position
- Codex: NO — current ordering optimal under stated hard dependencies (Exp 50 requires Ouroboros fix; Exp 49 requires Exp 41 / Exp 45 / Exp 46; Exp 44 requires Exp 41 / Exp 42 / Exp 43)
- CC2: NO — current ordering optimal under stated hard dependencies
- ChatGPT: YES — move Exp 48 (info) before Exp 46 (CS / section-18)
- DeepSeek: YES — move Exp 45 (stats) immediately after Exp 41
Split: 2 NO / 3 YES. The three YES proposals are mutually incompatible.

### RQ6 — Target-article candidates for Exp 47, 51, 52, 53
- Gemini: NO native for any; synthesise minimal modules
- Codex: NO native for any; adapter layer over external content
- CC2: NO native for any; synthesise (rejects adapter on orthogonality grounds — adapter blurs c_ext with target-module validity)
- ChatGPT: NO native for any; synthesise (rejects adapter)
- DeepSeek: NO native for 47/52/53, but YES for physics (bench/cdsfl_registry/composer.py — uses units); synthesise for 47/52/53
Split for physics: 4 NO native / 1 YES. For fallback method: 3 synthesise / 1 adapter / 1 synthesise-with-physics-exception.
"""

# ---------------------------------------------------------------------------
# Round 2 questions (yield-or-refute, per RQ)
# ---------------------------------------------------------------------------

QUESTIONS_R2 = r"""
## Round 2 — yield or refute (six RQs)

For each RQ below, your task is one of:

- YIELD: state that you adopt the opposing position, with reasons that
  directly address the argument made by the models holding that
  position. Generic "I reconsider" is not acceptable — name the
  specific reasoning that moved you.
- REFUTE: state that you hold your Round 1 position, with reasons that
  directly address the opposing argument (not merely restate your own
  argument). Name the specific weakness in the opposing argument.

Do not offer new alternative positions. This round is for convergence
on the positions already surfaced.

Compelled-convergence rule: your response to each RQ must end with a
single bolded `**Round 2 position: YIELD to X / REFUTE X**` line
naming the position you hold and, if you yielded, which position you
yielded to.

### RQ1 — Unaddressed fix against 40_gate.json pass_condition

Round 1: 3 NO (Gemini, CC2, ChatGPT) / 2 YES (Codex, DeepSeek).

The NO position is that F1-F4 are sufficient for 40_gate.json
pass_condition. The YES positions are that additional fixes are
needed: Codex argues for a live-path preflight for the section-17
admissibility parser on bench/dm/_feedback.py; DeepSeek argues for
section-17 [VERIFY:current] flag handling and section-18
cosmetic-rewrite suppression.

Your task: YIELD to the NO position (F1-F4 sufficient), OR YIELD to
Codex's preflight YES (as a Gate C pre-launch step, not an F-item),
OR YIELD to DeepSeek's flag-handling YES, OR REFUTE the opposing
positions. Address the specific argument, not a restatement.

### RQ2 — Cross-experiment interaction missed

Round 1: 3 YES (Gemini, Codex, ChatGPT) / 2 NO (CC2, DeepSeek).

The YES position, as expressed by three models, is that tier /
threshold calibration drift learned under co-live section-17 plus
section-18 during Exp 40-53 will be reused when evaluating Exp 54
single-channel Cells B and C, contaminating main-effect attribution.
The NO position (CC2) is that this is a subcase of routing imbalance
already caught at Exp 44 / Exp 49 integration; DeepSeek's NO addresses
a different interaction (S_k-Microglia) rather than refuting the
threshold-drift argument.

Your task: YIELD to the YES position (pre-Exp-54 threshold-freeze
required), OR YIELD to the CC2 NO (Exp 44 / Exp 49 catches this), OR
REFUTE. If you are CC2 or DeepSeek, address specifically whether
Exp 44 / Exp 49 actually FREEZE thresholds or merely detect
specialist-specialist inconsistency — those are different guarantees.

### RQ3 — Exp 54 factorial attribution sufficiency

Round 1: 4 YES conditional (Codex, CC2, ChatGPT, DeepSeek) / 1 NO
(Gemini).

The YES-conditional position is that the 2x2 factorial is
mathematically identifiable via two-way ANOVA or equivalent GLM,
given an archive integrity check. Gemini's NO argues the issue is
not integrity but confound-by-runner-version: Cell A's archived data
reflects 14 experiments of runner evolution, not just section-17 and
section-18 absence.

Your task: YIELD to the YES-conditional position (main path proceeds
if Cell A integrity holds, with Gemini's fresh-run proposal as
fallback if it fails), OR YIELD to the Gemini NO (fresh run required
unconditionally), OR REFUTE. The four YES-conditional models must
address directly whether "archive integrity" covers runner-version
confound or not — those are distinct failure modes.

### RQ4 — Shadow-promotion-now offsetting risk

Round 1: 2 POLICY SAFE (Gemini, DeepSeek) / 3 CONDITIONALLY SAFE
(Codex, CC2, ChatGPT).

The POLICY SAFE position is that the context-loss risk prevented by
activating now strictly outweighs any offsetting risk. The
CONDITIONALLY SAFE position is that activation is safe subject to a
non-distortion check against the 40_gate.json pass_condition for each
promoted component — activation must not silently alter the "3
consecutive rounds with 0 novel CRITICAL findings" clause through
unintended channel coupling.

Your task: YIELD to POLICY SAFE unconditional, OR YIELD to
CONDITIONALLY SAFE with the named non-distortion check, OR REFUTE.
Gemini and DeepSeek: address directly whether your unconditional
position survives the counterexample where an activated component
DOES silently alter the pass_condition clause. The other three:
address directly whether the non-distortion check is practically
definable and measurable with the current shadow-audit logging, or
whether it requires enrichment first.

### RQ5 — Ordering of Exp 41-53

Round 1: 2 NO (Codex, CC2) / 3 YES (Gemini, ChatGPT, DeepSeek) —
but the three YES proposals are mutually incompatible (Gemini: move
Exp 46 first; ChatGPT: swap Exp 46 and Exp 48; DeepSeek: move Exp 45
right after Exp 41).

Three mutually incompatible YES positions do not constitute a
converged YES. Your task in Round 2:

- If you proposed a YES re-ordering in Round 1, either REFUTE the
  other two YES proposals (name the specific weakness in each), OR
  YIELD to the NO-current-ordering position with reasons that address
  the hard-dependency argument.
- If you argued NO in Round 1 (current ordering optimal), either hold
  your position (REFUTE all three YES proposals) or YIELD to one
  specific YES proposal by name.

The three YES proposers cannot all be right; at least two must yield
or converge.

### RQ6 — Target-article candidates for Exp 47, 51, 52, 53

Round 1: 5 NO native for bio (Exp 47), chemistry (Exp 52), engineering
(Exp 53). For physics (Exp 51): 4 NO native / 1 YES (DeepSeek cites
bench/cdsfl_registry/composer.py as using units). For fallback method
on non-physics: 3 synthesise / 1 adapter (Codex) / 1 synthesise with
physics-exception (DeepSeek).

Your task: YIELD or REFUTE on two sub-questions:

(a) For Exp 51 physics: does bench/cdsfl_registry/composer.py contain
dimensional content of sufficient density to serve as the Exp 51
target article? This is a verifiable claim. DeepSeek must defend it
with specifics (which lines, which functions, what dimensional
arithmetic); the other four must examine the claim and yield or
refute.

(b) For fallback method on Exp 47, 52, 53: synthesise minimal native
modules, or adapter layer over external content? Codex is the lone
adapter vote; the other four hold synthesise (with CC2 and ChatGPT
rejecting adapter on Stage 6 orthogonality grounds — adapter blurs
c_ext / SEARCH QUALITY with target-module validity).

A note on recently-corrected framing: references to specialists by
their cell type must not equate the cell type with a single tool.
The Exp 47 biology target must exercise the biology B-Cell
specialist's FULL tool set as declared in
bench/cdsfl_registry/domains/immune/biology.toml (mathematical -> sympy
plus biological_sequence plus dimensional_analysis; logical -> z3;
statistical -> statsmodels plus scipy plus uncertainty_propagation),
not only biopython. Similarly for physics, chemistry, engineering
specialists. Frame your answer in these terms.
"""

# ---------------------------------------------------------------------------
# Response format
# ---------------------------------------------------------------------------

RESPONSE_FORMAT = r"""
## Response format (mandatory)

For each RQ1-RQ6:

1. Name the Round 1 position you held.
2. State YIELD or REFUTE for Round 2.
3. Reasoning (2-4 short sentences) that addresses the opposing
   argument DIRECTLY (not a restatement of your own).
4. End with a single bolded line:
   `**Round 2 position: YIELD to X / REFUTE X**`
   where X names the position.

Compelled-convergence rules:

- Do NOT offer new alternative positions. This round is for
  convergence on the positions already surfaced in Round 1.
- Do NOT offer multiple Round 2 positions per question. One per RQ.
- Word budget: 1500 words total across RQ1-RQ6.

Divergence after Round 2 will be addressed in Round 3, not synthesised
by the hub. Therefore this round is the chance to end the disagreement
on the merits.
"""

# ---------------------------------------------------------------------------
# Per-model identity preambles (Round 2 fix: each model must know who it is)
# ---------------------------------------------------------------------------

MODEL_IDENTITY: dict[str, str] = {
    "gemini": r"""
## YOUR IDENTITY FOR THIS ROUND (load-bearing — do not ignore)

You are **Gemini 3.1 Pro**. You are one of five panel models in a
compelled-convergence review. The hub (CC1) dispatches to you; you do
NOT synthesise across models — you give YOUR position only.

Your Round 1 positions were:
- RQ1: NO — F1-F4 sufficient
- RQ2: YES — Exp 46 (section-18 target) alters modulation engine, invalidating Exp 41-45 calibrations
- RQ3: NO — Cell A confounded by 14 experiments of runner evolution; propose fresh Cell A run at Exp 54 codebase with section-17 and section-18 both off
- RQ4: POLICY SAFE unconditionally
- RQ5: YES — move Exp 46 (section-18 target) to Exp 41 position
- RQ6: NO native for any; synthesise minimal modules

Answer from these positions. YIELD or REFUTE as instructed.
""",
    "codex": r"""
## YOUR IDENTITY FOR THIS ROUND (load-bearing — do not ignore)

You are **Codex GPT-5.4** (via OpenRouter). You are one of five panel
models in a compelled-convergence review. The hub (CC1) dispatches to
you; you do NOT synthesise across models — you give YOUR position only.

Your Round 1 positions were:
- RQ1: YES — add live-path preflight for section-17 admissibility parser on bench/dm/_feedback.py
- RQ2: YES — treatment-conditioned tier-calibration drift crossing Exp 40-49 into Exp 54
- RQ3: YES conditional on archive comparability — two-way ANOVA sufficient
- RQ4: CONDITIONALLY SAFE — promoted channels auditable against Stage 6 orthogonality; F3 debug assertion catches hidden coupling in q
- RQ5: NO — current ordering optimal under stated hard dependencies
- RQ6: NO native for any; adapter layer over external content

Answer from these positions. YIELD or REFUTE as instructed.
""",
    "cc2": r"""
## YOUR IDENTITY FOR THIS ROUND (load-bearing — do not ignore)

You are **CC2 (Claude Opus 4.6)** running via CLI piped mode. You are
one of five panel models in a compelled-convergence review. The hub
(CC1) dispatches to you; you are NOT CC1. You do NOT synthesise across
models — you give YOUR position only.

Your Round 1 positions were:
- RQ1: NO — F1-F4 sufficient (argued from codebase grounding: admissibility/divergence signal generation independent of F2 wrapper wiring; gamma-alt convergence path via reference_runner_v3._check_gamma_alt_convergence at line 1064 reads thresholds already present in 40_gate.json)
- RQ2: NO — math-stats overlap is subcase of routing imbalance, caught at Exp 44 / Exp 49 integration
- RQ3: YES conditional on Gate C Cell A integrity check — two-way ANOVA on round-level metrics
- RQ4: CONDITIONALLY SAFE — F2 1e-9 regression gate plus Exp 49 cross-domain recalibration checkpoint
- RQ5: NO — current ordering optimal under stated hard dependencies
- RQ6: NO native for any; synthesise (rejects adapter on orthogonality grounds — adapter blurs c_ext with target-module validity)

Answer from these positions. YIELD or REFUTE as instructed.
""",
    "chatgpt": r"""
## YOUR IDENTITY FOR THIS ROUND (load-bearing — do not ignore)

You are **ChatGPT GPT-5.4** (via OpenRouter). You are one of five panel
models in a compelled-convergence review. The hub (CC1) dispatches to
you; you do NOT synthesise across models — you give YOUR position only.

Your Round 1 positions were:
- RQ1: NO — F1-F4 sufficient
- RQ2: YES — threshold-calibration drift across Exp 40-53 under co-live section-17 plus section-18, reused in Exp 54 B and C cells
- RQ3: YES conditional on frozen scoring rules across cells — two-way GLM with interaction
- RQ4: CONDITIONALLY SAFE — promoted component must be pipeline-neutral w.r.t. pass_condition before live
- RQ5: YES — move Exp 48 (info) before Exp 46 (CS / section-18)
- RQ6: NO native for any; synthesise (rejects adapter)

Answer from these positions. YIELD or REFUTE as instructed.
""",
    "deepseek": r"""
## YOUR IDENTITY FOR THIS ROUND (load-bearing — do not ignore)

You are **DeepSeek R1-0528** (via OpenRouter). You are one of five panel
models in a compelled-convergence review. The hub (CC1) dispatches to
you; you do NOT synthesise across models — you give YOUR position only.

Your Round 1 positions were:
- RQ1: YES — add section-17 [VERIFY:current] flag handling and section-18 cosmetic-rewrite suppression
- RQ2: NO — S_k-Microglia interaction already gated by Exp 42
- RQ3: YES — linear mixed model; if Cell A corrupt, use Cell B and C early rounds as proxy baseline
- RQ4: POLICY SAFE — noise contained to logs; calibration uses late-session data
- RQ5: YES — move Exp 45 (stats) immediately after Exp 41
- RQ6: NO native for 47/52/53, but YES for physics (bench/cdsfl_registry/composer.py — uses units); synthesise for 47/52/53

Answer from these positions. YIELD or REFUTE as instructed.
""",
}

# ---------------------------------------------------------------------------
# Compose full user prompt (per-model: identity preamble injected)
# ---------------------------------------------------------------------------

def build_user_prompt(model_label: str) -> str:
    identity = MODEL_IDENTITY.get(model_label, "")
    return (
        identity
        + "\n\n"
        + CORRECTED_FRAMING
        + "\n\n"
        + STAGE6_MATH
        + "\n\n"
        + ROUND1_POSITIONS
        + "\n\n"
        + "## Round 1 outcome document (full text for reference)\n\n"
        + ROUND1_TEXT
        + "\n\n"
        + QUESTIONS_R2
        + "\n\n"
        + RESPONSE_FORMAT
    )


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def _dispatch(model_label: str, model_id: str, api: str,
              system_prompt: str, user_prompt: str) -> dict:
    start = time.time()
    try:
        if api == "gemini_native":
            response = call_gemini(model_id, system_prompt, user_prompt)
        elif api == "claude_cli":
            # WP4a: 900s timeout / 1 retry to prevent CC2 timeout cascade
            response = call_claude_cli(model_id, system_prompt, user_prompt,
                                       timeout=900, max_retries=1)
        elif api == "openrouter":
            response = call_openrouter(model_id, system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown api: {api}")
        elapsed = time.time() - start
        return {
            "model": model_id,
            "label": model_label,
            "api": api,
            "response": response,
            "time_s": round(elapsed, 1),
            "chars": len(response) if response else 0,
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "model": model_id,
            "label": model_label,
            "api": api,
            "error": str(e),
            "time_s": round(elapsed, 1),
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }


def main() -> int:
    system_prompt = CDSFL_TEXT
    # Build per-model prompts (identity preamble differs per model)
    per_model_prompts = {label: build_user_prompt(label) for (label, _, _) in MODELS}
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sample_prompt = per_model_prompts[MODELS[0][0]]
    total_chars = len(system_prompt) + len(sample_prompt)
    print(f"Dispatching Exp 40-54 plan review ROUND 2 (with identity fix) to {len(MODELS)} models")
    print(f"Prompt size (approx): {total_chars} chars "
          f"(system {len(system_prompt)} + user ~{len(sample_prompt)})")
    print(f"Round 1 outcome loaded: {ROUND1_PATH.name} ({len(ROUND1_TEXT)} chars)")
    print(f"Timestamp: {timestamp}")
    print(f"Logs: {LOGS_DIR}")
    print()

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = {
            ex.submit(_dispatch, label, mid, api, system_prompt,
                      per_model_prompts[label]): label
            for (label, mid, api) in MODELS
        }
        for fut in concurrent.futures.as_completed(futures):
            label = futures[fut]
            result = fut.result()
            results[label] = result
            if "error" in result:
                print(f"  {label}: ERROR in {result['time_s']}s - {result['error'][:200]}")
            else:
                print(f"  {label}: {result['chars']} chars in {result['time_s']}s")

            per_model_path = LOGS_DIR / f"{label}_{timestamp}.json"
            per_model_path.write_text(json.dumps(result, indent=2))

    combined_path = LOGS_DIR / f"combined_{timestamp}.json"
    combined_path.write_text(json.dumps(results, indent=2))
    print()
    print(f"Combined log: {combined_path}")

    errors = [label for label, r in results.items() if "error" in r]
    if errors:
        print(f"ERRORS: {errors}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
