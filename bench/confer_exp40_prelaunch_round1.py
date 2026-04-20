#!/usr/bin/env python3
"""
Exp 40 Pre-launch Panel Review — Round 1 of 3
==============================================

Five-model (star-topology) review of the Phase A + Phase B work
(commits 8b8682d + bdfc93a + docs sync 6580737 + sv 7326a04).

Round 1 charge: assess Phase A + B code closures, outstanding issues,
and answer three architectural / methodological meta-questions that
have emerged:

  M1. Specialist-cell cross-domain composability — should the per-domain
      tool lists be siloed (as now), or should domains loan tools to one
      another and/or should claims be multi-domain-tagged?

  M2. Runner topology — Exp 40 uses star/blackboard. Runner v2 also
      offers relay/direct-conversation. Which is most productive for
      which experiment class, and is there a third pattern worth
      exploring?

  M3. Correctness ratio, empirical novelty, external DCY material, and
      the 'just doing maths' objection — what does the invention-engine
      goal require mathematically, without reframing the goal and
      without amplifying the framework beyond what the evidence
      supports?

Rounds 2 and 3 will follow once Round 1 findings are in. Round 2:
expert-system assessment of per-domain TOMLs under the cross-domain
framing. Round 3: promotion criteria for physics/chemistry/engineering.

Protocol: CDSFL + FFAFP, Stage 6 math exclusively, prose-only formal
          conclusions, workings shown.
Models:   Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4,
          DeepSeek R1-0528
Dispatch: parallel via ThreadPoolExecutor(max_workers=5)
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_prelaunch_round1"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("gemini",   "gemini-3.1-pro-preview",     "gemini_native"),
    ("codex",    "openai/gpt-5.4",             "openrouter"),
    ("cc2",      "opus",                       "claude_cli"),
    ("chatgpt",  "openai/gpt-5.4",             "openrouter"),
    ("deepseek", "deepseek/deepseek-r1-0528",  "openrouter"),
]

# ---------------------------------------------------------------------------
# Load CDSFL system prompt
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Stage 6 math (canonical, same block used in round-3 §18 review)
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

The three are independent reporting dimensions; MUST NEVER be collapsed
into a single score before reporting.

### Continuous suppression w(f) (separate channel)

    w(f) = max(exp(-lambda_s * sum TopK sim), w_floor)
    CRITICAL: w(f) MUST NEVER enter q_eff in the Bayesian update.

### kappa_set (convergence)

    kappa_set(r) = 1 - sum(w_c * Sev_novel_c) / (sum Sev_cumulative + eps)

### Divergence modulator channel (round-2 unanimous, round-3 verified)

    m_div in {1.00, 0.85, 0.70, 0.60}
    eta_int_modulated = m_div * eta_int
    eta_combined = eta_int_modulated * (1 - c_ext * (1 - nu_k))
    q = eta_combined * d * p
    R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))

    FORBIDDEN: m_div as pre-factor on R_k.
    FORBIDDEN: m_div counting toward nu_k.
    FORBIDDEN: w(f) in q_eff.
"""

# ---------------------------------------------------------------------------
# Technical findings brief (condensed from CDSFL Stage 3 Closure Explained)
# ---------------------------------------------------------------------------

TECHNICAL_BRIEF = r"""
## Phase A + B closures — what landed between Exp 39 and Exp 40

Branch `exp39-experimental`, HEAD `7326a04`, pushed to origin.
Tests: 1,250 passing. mypy strict: clean. ruff: clean.

### Phase A (commit 8b8682d, 98 new tests)

- **1D.5** S_k format pre-check: if a model returns a malformed S_k
  sub-equation, the runner re-prompts for reformat instead of parse-error.
- **1D.6** Gemini verdict extractor: Gemini's output format leaked
  through as parse errors; dedicated extractor added.
- **1E.6** Decomposition sizing: target split sized by actual payload,
  not a fixed constant.
- **1E.7** Cross-model diversity metric: paraphrase-vs-genuine-divergence
  signal logged per round (compliance-theatre detector).
- **1E.10 (library form)** `compute_rk_with_eta_channel` wrapper that
  validates the channel invariant and raises `ChannelViolationError`
  when broken. Production call site still bypasses this wrapper (see
  outstanding issue below).

### Phase B (commit bdfc93a, 200+ new tests)

- **1D.3** Per-model rho tracking: ITC (interstitial conclusion check)
  can now target the stuck model, not fire globally.
- **1E.3 (audit)** Physics/chemistry/engineering specialist audit
  complete. LIVE_SPECIALIST_DOMAINS frozenset at `immune_agents.py:334`
  still contains {mathematics, statistics, biology, information_science}
  only — single-line flip available, not applied.
- **1E.4** Physics/chemistry/engineering specialists functionalised
  (astropy, RDKit, pint, stoichiometric balance) — shadow-wired.
- **1E.5** Fingerprint attention metrics populated from ITC + parse-yield
  history.
- **1E.8** Ouroboros query-quality fix: literal finding IDs no longer leak
  into arXiv queries — uses description text. Live arXiv network test
  confirms status=live.
- **1E.9** Cross-round recidivism: near-identical alternatives across
  rounds are flagged and demoted.
- **1E.11** OpenRouter structured tool-use (`bench/openrouter_tools.py`):
  sympy/z3/pytest/ruff/mypy registered for Codex/Gemini/ChatGPT/DeepSeek.
  Subprocess-isolated dispatch, path-safety gatekeeper, 6-iteration cap.
- **1E.12** DeepSeek R1 formal-verification specialist: confidence capped
  at 0.5, invoked only when both z3 and SymPy return UNCERTAIN.

### Specialist-cell tool coverage (per-domain TOML, 10 domains)

    chemistry     8 tools   (RDKit, pint, stoichiometry, ...)
    cs_software   9 tools
    physics       7 tools   (astropy, pint, SymPy, ...)
    biology       6 tools   (biopython, sklearn, ...)
    engineering   6 tools   (pint, PuLP, ...)
    mathematics   5 tools   (SymPy, z3, deepseek_formal, mpmath, Wolfram)
    information_science  4 tools
    statistics    3 tools

Global `tool_manifest.toml` registers 20+ tools. Per-domain TOMLs select
priorities from the global pool; the default dispatch walks the per-domain
list left-to-right and the first definitive verdict wins.

### Classifier (two-layer, hybrid)

Layer 1 `_classify_claim_v2` (`immune_agents.py:3954`): regex-based, from
per-domain TOML patterns, returns (claim_type, confidence).
Layer 2 `typed_llm_classifier` (`immune_agents.py:4559`): Claude Haiku via
local CLI (Max subscription). For `software` domain, Haiku is PRIMARY. For
non-software, Haiku is an override when confidence >= 0.70 and a math guard
passes. Fails open — regex classification preserved if Haiku unavailable.

### Topology

Runner v2 supports TWO topologies, set in `bench/exp40_configs/40_gate.json`:
  - `star` (default, used in Exp 40) — models see a shared finding registry
    and file DISCOVERY / VERDICT payloads against it. No model-to-model prose.
  - `relay` — models see full analysis from other models; @-address allowed.
No round-robin option in the runner.

Confer scripts (for panel review, like this one) dispatch 5 models in
parallel from a single coordinator — star-within-round, sequential across
rounds.

---

## Outstanding issues before Exp 40 launch

1. **Runner v2 promotion** (founder decision). Runner v1 frozen on founder
   directive until v2 approved. 1,250 tests passing on v2.

2. **K/L/M live-promotion flip** (optional; not blocking Exp 40 because
   Exp 40 targets `bench/dm/_feedback.py`, a software module). One-line
   edit at `immune_agents.py:334`. Audit landed; promotion held pending
   empirical exercise on real physics/chemistry/engineering claims.

3. **1E.10 runtime call-site assertion**: wrapper `compute_rk_with_eta_channel`
   exists and passes tests, but the production call site at
   `reference_runner_v2.py:3510` still calls the bare `compute_rk`. Reason:
   `m_div` does not currently flow into `compute_rk` — that wiring is
   deferred to Exp 54 (2×2 factorial attribution). Activating the wrapper
   now would produce a dead assertion.

4. **SymPy specialist silent regression** (separate background task):
   sandboxed subprocess uses `global_dict={'__builtins__': {}}`, which
   prevents SymPy from constructing Integer literals during parsing.
   Every SymPy specialist verdict in the live pipeline currently returns
   UNCERTAIN regardless of claim truth. Fix is in progress — must not
   re-open the RCE vector that the sandbox lockdown closed.

5. **Adversarial-panel P-pass not yet run on Phase A + B code.** Mechanical
   verification (pytest/mypy/ruff) clean. Multi-model adversarial review —
   that is this script's purpose — not yet done.

6. **Cross-domain diversity metric + cross-round recidivism**: both are
   populated every round but remain log-only (see
   `reference_runner_v2.py:4473` code comment). Folding them into scoring
   or admissibility would require Exp 54 attribution + explicit calibration.
"""

# ---------------------------------------------------------------------------
# Meta-questions for the panel (this is what changes between rounds)
# ---------------------------------------------------------------------------

META_QUESTIONS = r"""
## Architectural meta-questions (the core ask of this round)

### M1 — Bidirectional informing between specialist B-cells and domain encodings

The framework has TWO pluggable entities that are currently decoupled:

  1. Specialist B-cells (runtime code, `bench/immune_agents.py`): the
     `_verify_*` functions that execute tool dispatch for a given finding.
     These are the MECHANISM.

  2. Domain-level encodings (declarative data, `bench/cdsfl_registry/
     domains/immune/*.toml`): claim-type regex patterns, ordered tool
     lists, routing preferences per domain. These are EXCHANGEABLE
     PROFILES ("exchangeable domain-level encodings", a foundational
     project concept).

Currently the coupling is read-once: cell loads config at boot, uses it
statically. There is no feedback between them, and configs do not share
with one another, nor do cells share with one another. The architecture
is four-way siloed:

    configs <-(missing)-> cells
    configs <-(missing)-> configs
    cells   <-(missing)-> cells

The founder's intuition is that each entity could inform the other
bidirectionally, making each inherently more capable. This would mirror
at the SPECIALIST level what CDSFL already does at the PANEL level —
cross-informing between the five frontier models makes findings more
reliable; cross-informing between specialist cells + their configs
should make verifications more reliable.

Four candidate flows:

  (A) Configs -> Cells (already happens).
      Config tells cell its claim-type patterns + tool ordering.
      Cell starts with a reasoned profile rather than defaults.

  (B) Cells -> Configs (missing).
      Cell emits telemetry per dispatch: which tool fired, which
      returned DEFINITIVE vs UNCERTAIN, per-claim-type yield rate,
      per-tool latency. Telemetry updates config priorities.
      A tool that is always UNCERTAIN on claim-type X gets demoted;
      a tool that rarely fires but is always definitive when it does
      gets promoted. Config becomes empirical, not a hand-authored
      guess.

  (C) Configs -> Configs (missing).
      Configs loan each other their regex patterns. A claim is
      classified against its primary domain's patterns AND against
      secondary domains' patterns. Each match yields a
      (domain, claim_type, confidence) tag. Most real claims are
      multi-domain: "ATP yield is 30.5 kJ/mol" is biology +
      chemistry + dimensional (pint). Single-domain routing loses
      the other two lenses.

  (D) Cells -> Cells (missing).
      Cell encountering a sub-claim during dispatch hands it to a
      sibling cell rather than rejecting or swallowing it. E.g.
      chemistry cell encounters a dimensional statement mid-
      verification -> hands to pint via engineering cell -> receives
      verdict -> folds into its own verdict. Verification becomes
      compositional, not monolithic.

These are not mutually exclusive; (B), (C), (D) are independently
valuable.

Panel charge:

  - Which of (B), (C), (D) should land first? Rank and justify.
  - Are there failure modes — redundant verdicts, conflicting
    verdicts, priority inversions, telemetry noise drowning
    genuine-signal priority updates, regex cross-contamination
    (one domain's patterns polluting another's classification) —
    that the current siloed design is implicitly protecting
    against? If so, what guards are needed in the composed
    architecture?
  - For (C): what is the rule for combining N domain verdicts on
    one claim? Majority? First-definitive? Weighted by classifier
    confidence? Unanimous-required for DEFINITIVE? Name the rule
    and show it is consistent with the Stage 6 orthogonality
    constraint.
  - For (B): what is the update rule that prevents catastrophic
    priority flips from small telemetry samples? (e.g. EMA with
    what half-life? hysteresis? minimum-sample gate?)
  - Stage 6 interaction: if a claim is independently verified
    across N domains, does the evidence density legitimately raise
    eta_int (more independent verification = more internal
    evidence), does it raise p (detection probability, the
    validity channel), or is it orthogonal to both? Derive.
  - Is this architecture a strict superset of the current one, or
    are there experiments (e.g. Exp 40 itself, which targets a
    software module) where siloed verification is preferable
    because the claim domain is narrow? If so, what is the
    activation rule?

### M2 — Runner topology

Exp 40 uses star/blackboard topology (models see only a shared finding
registry, file DISCOVERY + VERDICT payloads). Relay/direct-conversation
topology is also implemented but not used in Exp 40.

Panel charge:

  - Star enforces structured findings and discourages model-to-model
    politeness drift. Relay enables direct challenge and extension. Which
    is more productive for which experiment class — infrastructure gate
    (Exp 40) vs attribution factorial (Exp 54) vs K/L/M specialist
    promotion runs?
  - Is there a third topology worth exploring? (e.g. hub-and-spoke with
    rotating hub, or star-with-side-channels for paired challenge, or
    sequential pipeline where model N sees models 1..N-1 only.)
  - Does topology choice interact with the Stage 6 math in ways that
    require explicit derivation — e.g. does relay topology bias eta_int
    through conversational reinforcement, and if so how should that be
    modelled?

### M3 — Correctness ratio, empirical novelty, and the 'just doing maths' objection

The project's stated goal is an 'invention engine' / 'science calculator'
— a tool that helps competent engineers and scientists produce
technically correct AND novel outputs under structured falsification.
Not AGI, not ASI. Two measurable claims live inside that goal, and an
external reviewer predictably objects to the framing. This meta-question
asks the panel to constrain itself tightly to the immediate problem —
no reframing of the goal, no concession that it is simply a more
elaborate form of retrieval, and no rhetorical elevation of the
framework beyond what the evidence supports.

(i) CORRECTNESS. Exp 40 is a software-gate infrastructure experiment.
Bench Run 2 (27 STEM problems) is the next empirical test on tasks
that are not software-engineering tickets. Candidate metric: of N
solution paths proposed by the panel on a given task, how many are
independently verifiable as correct? If 49 of any 50 solutions in a
round were independently correct, is the ratio M/N itself a metric
worth tracking? Does it fold into the R_k validity channel as
additional evidence, or does it warrant an orthogonal reporting
channel alongside R_k, nu_k, c_ext?

(ii) NOVELTY EXTENSION. Stage 6 novelty (nu_k, c_ext) is literature-
grounded, not self-assessed. Bench Run 2 exercises it outside the
software-engineering corpus the framework was calibrated on. What
signals, if any, in the Exp 40 2x2 factorial would predict Bench
Run 2 success or failure on the novelty channel specifically (not
on correctness)? Is there a derivable boundary between constraint-
density regimes that induce novelty and those that induce
hallucination, or is that boundary purely empirical and must be
measured?

(iii) EXTERNAL DCY MATERIAL (panel to verify independently).
External material reaching the founder proposes a "Divergence
Compliance Yield" as a continuous within-model diversity metric,
framed as a replacement for the discrete divergence modulator
m_div in {1.00, 0.85, 0.70, 0.60}:

    DCY = max_k [ (1 - sim(f, A_k)) * (1 - Jaccard(Deps(f), Deps(A_k))) * I_FFF ]

where sim is the bounded embedding similarity from Appendix §1.3,
Deps(x) is described as the set of downstream dependencies/modules
affected by the fix for finding x, and I_FFF is an indicator (1 if
the FFF consequence trace is active, 0 pre-Follow). The panel is
asked to independently verify:

  (a) Is the formulation mathematically sound given that §1.3
      similarity s(f1, f2) = (1 - beta) * content_sim + beta * b_class
      with CLASS_BONUS = 0.3 and beta = 0.2 caps at s = 0.86, not 1.0
      by construction? In particular, is the claimed compliance-theatre
      boundary ("sim = 1, Jaccard = 1 therefore DCY = 0") reachable, or
      is sim = 1 unreachable and the boundary therefore mis-specified?
  (b) Does the I_FFF = 0 case behave as the prose describes ("relies
      entirely on the embedding semantic distance") or as the formula
      computes (DCY = 0 regardless of sim)? If these disagree, which
      is the intended semantics?
  (c) Is Deps(.) an object the architecture actually has, or is the
      dependency set being imported from outside the framework? §7.12
      in the appendix covers FFF defect-flux convergence, not a
      per-finding downstream dependency set — clarify whether the
      attribution is correct.
  (d) Does a continuous form add reasoning value beyond the discrete
      m_div tier already in production, for Exp 40 specifically and
      Bench Run 2 in prospect, or is the discrete tier sufficient?

If the formulation is salvageable, propose the correction that makes
its boundary behaviour match its stated intent. If not, reject it
with reasons.

(iv) THE 'JUST DOING MATHS' OBJECTION. An external reviewer will
ask: is the panel generating genuine technical synthesis, or is it
executing sophisticated retrieval-and-recombination of training-
data patterns dressed in mathematical formalism? The question is
operational, not rhetorical. Panel charge: what measurable signal
— collectable during or after a run, not asserted about a run —
would distinguish genuine synthesis from sophisticated retrieval-
and-recombination? If no such signal exists within the current
framework, say so and state plainly whether the invention-engine
goal requires the distinction to be resolvable, or whether the
goal is achievable even if the distinction is empirically
indistinguishable.

Panel charge (summary):

  - M/N correctness ratio: formal metric, folklore, or already
    subsumed by R_k? If a metric, where does it sit in Stage 6?
  - Novelty extension to Bench Run 2: is there a derivable boundary
    between novelty-inducing and hallucination-inducing constraint
    density, or is it purely empirical? What Exp 40 signals, if
    any, would predict Bench Run 2 novelty performance?
  - External DCY material: independently verify sub-claims (a)-(d)
    above; propose the correction that makes it sound or reject it
    with reasons. Judge whether a continuous form supersedes m_div
    or duplicates it.
  - 'Just doing maths' objection: name the operational signal that
    would settle it, or declare the distinction empirically
    indistinguishable and explain why that is acceptable (or not)
    for the invention-engine goal.
"""

# ---------------------------------------------------------------------------
# Charge
# ---------------------------------------------------------------------------

CHARGE = """
## Round-1 charge

You and four other frontier models are reviewing the Phase A + Phase B
work and answering the three meta-questions above (M1 architectural,
M2 architectural, M3 methodological / mathematical).

Requirements:

  1. Use CDSFL Stage 6 math EXCLUSIVELY as the mathematical arbiter.
     Do not import notation from other frameworks; do not re-derive unless
     necessary to answer a question, and if you do, show the derivation.
  2. Apply FFAFP: Find (what is the issue), Follow (trace consequences),
     Analyse (mechanically, with tools where possible), Fix (propose the
     concrete change), P-pass (falsify your own fix before presenting).
  3. Show your workings for any mathematical claim. Formal mathematics
     may be in equation form; formal conclusions and recommendations must
     be in prose.
  4. Be precise. Precision over prose. If the right answer is "I do not
     have enough information," say so and name the information you would
     need.

Output format (prose-only formal conclusions with workings shown):

  A. ASSESSMENT OF PHASE A + B CLOSURES
     - Any items where the closure is incomplete or where a hidden
       regression is plausible.
     - Any items where the implementation is correct but the rationale
       (as summarised above) is off.

  B. ASSESSMENT OF OUTSTANDING ISSUES (1-6 above)
     - Prioritisation: which must land before Exp 40 launch, which can
       defer, which are blockers in disguise.
     - For each, the concrete next step.

  C. META-QUESTION M1 (cross-domain composability)
     - Your recommended architecture: (i), (ii), (iii), or composite.
     - Failure modes and how to guard against them.
     - Interaction with Stage 6 math — in particular with eta_int and
       with the orthogonality constraint.

  D. META-QUESTION M2 (topology)
     - Your recommended topology per experiment class.
     - Whether a third topology is worth exploring.
     - Interaction with Stage 6 math.

  E. META-QUESTION M3 (correctness ratio, empirical novelty, external
     DCY material, 'just doing maths' objection)
     - Your stance on M/N correctness as either a formal Stage 6
       channel or a quantity subsumed by R_k.
     - Your stance on Exp 40 -> Bench Run 2 novelty-prediction signals
       and whether the constraint-density boundary between novelty-
       inducing and hallucination-inducing regimes is derivable or
       purely empirical.
     - Your independent verdict on the external DCY material (sub-
       claims a-d in M3 above), including either the correction that
       makes the formulation sound or reasons for rejection, and a
       verdict on whether a continuous form supersedes or duplicates
       the discrete m_div tier.
     - Your operational signal (or honest "no signal available") for
       distinguishing genuine synthesis from sophisticated retrieval-
       and-recombination, and whether the invention-engine goal
       requires the distinction to be resolvable.

  F. BEST OVERALL ROUTE FORWARD
     - One-paragraph prose recommendation: given the current state
       (1,250 tests, Phase A + B landed, runner v1 frozen, K/L/M in
       shadow, SymPy sandbox regression pending), what is the best next
       step and why?

  G. P-PASS
     - Falsify your own answers in A-F. Where might you be wrong?

Word budget: up to 2,500 words. Use the budget; do not pad to reach it.
"""

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

LABEL_DISPLAY = {
    "gemini":   "Gemini 3.1 Pro",
    "codex":    "Codex GPT-5.4",
    "cc2":      "CC2 (Claude Opus 4.6)",
    "chatgpt":  "ChatGPT GPT-5.4",
    "deepseek": "DeepSeek R1-0528",
}


def build_prompt(self_label: str) -> str:
    self_display = LABEL_DISPLAY[self_label]

    return f"""\
# Exp 40 Pre-launch Panel Review — Round 1 of 3

You ({self_display}) are one of five frontier models assessing the
pre-Exp-40 state of the CDSFL project. Four other models receive the
identical prompt in parallel. Your answers will be combined with theirs
for convergence analysis before Rounds 2 and 3.

Protocol: CDSFL + FFAFP. Mathematical arbiter: Stage 6 below. No other
framework. Formal conclusions in prose.

---

{STAGE6_MATH}

---

{TECHNICAL_BRIEF}

---

{META_QUESTIONS}

---

{CHARGE}
"""


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def dispatch_model(label: str, model_id: str, api: str) -> dict:
    t0 = time.monotonic()
    prompt = build_prompt(label)
    print(
        f"  [{label}] dispatching ({model_id} via {api}, "
        f"prompt={len(prompt)} chars)...",
        flush=True,
    )

    try:
        if api == "gemini_native":
            response = call_gemini(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=prompt,
                max_tokens=32768,
                timeout=300,
                max_retries=5,
                backoff_base=3.0,
            )
        elif api == "claude_cli":
            response = call_claude_cli(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=prompt,
                max_tokens=32768,
                timeout=900,
                max_retries=1,
            )
        elif api == "openrouter":
            response = call_openrouter(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=prompt,
                max_tokens=32768,
                timeout=300,
                max_retries=3,
            )
        else:
            raise ValueError(f"Unknown API: {api}")

        elapsed = time.monotonic() - t0
        print(
            f"  [{label}] responded in {elapsed:.1f}s ({len(response)} chars)",
            flush=True,
        )
        return {
            "model": model_id,
            "label": label,
            "api": api,
            "response": response,
            "time_s": round(elapsed, 1),
            "chars": len(response),
            "prompt_chars": len(prompt),
        }

    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"  [{label}] FAILED after {elapsed:.1f}s: {e}", flush=True)

        if api == "gemini_native":
            print(
                f"  [{label}] falling back to Gemini via OpenRouter...",
                flush=True,
            )
            try:
                t0b = time.monotonic()
                response = call_openrouter(
                    model_id="google/gemini-3.1-pro",
                    system_prompt=CDSFL_TEXT,
                    user_prompt=prompt,
                    max_tokens=32768,
                    timeout=300,
                    max_retries=3,
                )
                elapsed2 = time.monotonic() - t0b
                print(
                    f"  [{label}] (OpenRouter fallback) responded in "
                    f"{elapsed2:.1f}s ({len(response)} chars)",
                    flush=True,
                )
                return {
                    "model": "google/gemini-3.1-pro (via OpenRouter fallback)",
                    "label": label,
                    "api": "openrouter_fallback",
                    "response": response,
                    "time_s": round(elapsed + elapsed2, 1),
                    "chars": len(response),
                    "prompt_chars": len(prompt),
                }
            except Exception as e2:
                print(
                    f"  [{label}] OpenRouter fallback also FAILED: {e2}",
                    flush=True,
                )

        return {"label": label, "error": str(e), "time_s": round(elapsed, 1)}


def run_confer() -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'=' * 72}")
    print("  EXP 40 PRE-LAUNCH PANEL REVIEW — Round 1 of 3")
    print(f"  Timestamp: {ts}")
    print("  Protocol: CDSFL + FFAFP, Stage 6 math as arbiter")
    print("  Models: ge, cx, cc2, cgpt, ds (parallel, star dispatch)")
    print("  Charge: Phase A+B assessment + M1 cross-domain + M2 topology + M3 correctness/novelty/DCY")
    print(f"{'=' * 72}\n")

    results: dict[str, dict] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(dispatch_model, label, model_id, api): label
            for label, model_id, api in MODELS
        }
        for future in concurrent.futures.as_completed(futures):
            label = futures[future]
            try:
                result = future.result()
            except Exception as e:
                result = {"label": label, "error": f"future exception: {e}"}
            results[label] = result

            log_path = LOGS_DIR / f"{label}_{ts}.json"
            log_path.write_text(
                json.dumps(result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"  saved: {log_path}", flush=True)

    combined_path = LOGS_DIR / f"combined_{ts}.json"
    combined_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n  combined log: {combined_path}", flush=True)

    return results


if __name__ == "__main__":
    run_confer()
