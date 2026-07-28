#!/usr/bin/env python3
"""
Exp 40-54 Consolidated Plan — Final Panel Review
=================================================

A single-round compelled-convergence panel review of the consolidated
Exp 40-54 execution plan, dispatched before Exp 40 launches.

Plan under review:
    experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md

Framing anchors (load-bearing):
    - bench/exp40_configs/40_gate.json pass_condition
    - Stage 6 orthogonality: R_k / nu_k / c_ext as independent dimensions

Prior framing refuted (2026-04-20): "v1 preservation". Do NOT reuse.

Six scoped questions target only the 40-54 arc. Proposals for post-Exp-54
work are out of scope.

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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40to54_consolidated_plan_review_2026-04-21"
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
# Consolidated plan (full content injected into user prompt)
# ---------------------------------------------------------------------------

PLAN_PATH = REPO_ROOT / "experimental_notes" / "Exp40_to_54_Consolidated_Plan_2026-04-21.md"
PLAN_TEXT = PLAN_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Corrected framing preamble
# ---------------------------------------------------------------------------

CORRECTED_FRAMING = r"""
## Corrected framing for Exp 40-54 consolidated plan review (load-bearing)

A prior pre-launch audit on 2026-04-20 converged under a wrong framing.
That framing treated reference_runner.py (v1) as if it carried a
"preservation" policy. It does not. v1 is retained on disk ONLY as a
HISTORICAL REFERENCE to the first Exp-38 demonstration of the full
Stage 6 mathematical model. reference_runner_v2.py (v2, 4922 lines) IS
the Exp 40 runner and has been actively extended through Phase A
(commit 8b8682d) and Phase B (commit bdfc93a).

The panel is to reason ONLY from two anchors:

1. `bench/exp40_configs/40_gate.json` acceptance criterion for Exp 40:
   `"pass_condition": "gamma >= 0.30 OR (3 consecutive rounds with 0
   novel CRITICAL findings). Gamma-alt implemented in
   reference_runner_v2._check_gamma_alt_convergence."`

2. Stage 6 orthogonality (canonical Stage 6 mathematical model).
   R_k measures VALIDITY, nu_k measures NOVELTY, c_ext measures
   SEARCH QUALITY. The three are independent reporting dimensions
   and MUST NEVER be collapsed into a single score before reporting.

If you catch an argument drifting back to the "v1 preservation"
framing, flag the slip explicitly and correct. That framing has been
refuted; reasoning from it invalidates the answer.
"""

# ---------------------------------------------------------------------------
# Stage 6 math block (canonical)
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

### Divergence modulator channel

    m_div in {1.00, 0.85, 0.70, 0.60}
    eta_int_modulated = m_div * eta_int
    eta_combined = eta_int_modulated * (1 - c_ext * (1 - nu_k))

    FORBIDDEN: m_div as pre-factor on R_k.
    FORBIDDEN: m_div counting toward nu_k.
    FORBIDDEN: w(f) in q_eff.
"""

# ---------------------------------------------------------------------------
# Six scoped questions (Exp 40-54 arc only)
# ---------------------------------------------------------------------------

QUESTIONS_SCOPED = r"""
## Panel review — six scoped questions (Exp 40-54 arc only)

Scope guardrail: the panel is asked to find what breaks within the
Exp 40-54 arc. Proposals for experiments beyond Exp 54 are OUT OF SCOPE
and will be ignored. Do not propose additional experiments; this is a
plan review, not a plan expansion.

### RQ1. Unaddressed fix against 40_gate.json

The four fold-in-now items (F1 SymPy sandbox restoration; F2 wrapper
activation at reference_runner_v2.py:3510; F3 debug assertion on q at
call site; F4 closure state stratification) are scheduled before Exp 40
launches.

Is there any additional fix not on the F1-F4 list whose absence would
compromise Exp 40's §17 feedback-channel admissibility or §18 divergence
admissibility signals against `bench/dm/_feedback.py`, under the
40_gate.json pass_condition?

If YES, name the specific fix and the specific admissibility signal it
gates.
If NO, state so plainly and cite the pass_condition clause that confirms
sufficiency.

### RQ2. Cross-experiment interaction missed in the lessons-forward chain

Each experiment in the 40-53 arc folds its lessons into the NEXT
experiment's runner configuration, not back into v2's runtime logic
during the current run. Named risks already tracked: Exp 36 specialist
routing imbalance (3/4 under-routing, 1 over-routing), Exp 39 composer
format disagreement (fixed, verified in Exp 42), Macrophage wiring
repair (Exp 43), Ouroboros query quality prerequisite for Microglia
(Exp 50).

Is there a cross-experiment interaction NOT already tracked that the
lessons-forward chain would miss, with consequences that would distort
the Exp 54 factorial attribution?

If YES, name the interaction and the experiment pair(s) it crosses.
If NO, state so plainly.

### RQ3. Exp 54 factorial — attribution sufficiency

Exp 54 design:
  Cell A: archived Exp 36-38 data (pre-§17, pre-§18).
  Cell B: §17 on, §18 off.
  Cell C: §17 off, §18 on.
  Cell D: §17 on, §18 on (what has been running since Exp 40).

Known risk: §17 and §18 have been co-live for 14 experiments by the time
Exp 54 runs. Tier calibration (severity thresholds for finding
classification) is therefore §17+§18-conditional. Cell A's data quality
is load-bearing: if the archive is corrupted, the factorial collapses
to interaction-only.

Does the Cell A/B/C/D design produce attribution statistics sufficient
to separate §17 main effect, §18 main effect, and §17×§18 interaction?

If YES, identify the specific statistical test pattern that yields each
attribution (e.g. ANOVA on round-4 admissibility rate, two-way ANOVA
with interaction term, etc.).
If NO, identify which effect is unidentifiable and name the single
additional cell or archive check that would restore identifiability.

### RQ4. Shadow-promotion-now — offsetting risk

Policy (standing rule 2026-04-20): reviewed shadow components activate
now, not later. Reason: deferred items risk being forgotten when the
working context rolls forward, whereas activation carries a measurable
noise cost in the next experiment. Applied in the consolidated plan to
F2 (1E.10 wrapper) and, pending their own review gate, to K/L/M
specialists (physics, chemistry, engineering) after Exp 53.

Does shadow-promotion-now create an offsetting risk that outweighs the
context-loss risk it was adopted to prevent? Candidate offsetting risks
to consider: premature tier calibration entrenched before the factorial;
uncontrolled specialist-specialist interaction before Exp 49's
cross-domain synthesis test; silent noise injection into the γ-alt
signal that makes the 3-consecutive-rounds convergence clause
unreliable.

Answer: POLICY SAFE (offsetting risk is smaller than context-loss risk);
POLICY UNSAFE (offsetting risk is larger, with named mechanism); or
POLICY CONDITIONALLY SAFE (with a named bounding condition).

### RQ5. Ordering of Exp 41-53

Current ordering:
  41 math — 42 composer — 43 macrophage — 44 composition —
  45 stats — 46 CS/§18 — 47 bio — 48 info — 49 cross-domain —
  50 microglia — 51 physics — 52 chemistry — 53 engineering.

Known hard dependencies:
  - 50 Microglia requires Ouroboros query-quality fix verified (shadow
    calibrator hooked 14 April).
  - 49 Cross-domain requires 41, 45, 46 outputs.
  - 44 Composition requires 41, 42, 43 outputs.

Is there a re-ordering of Exp 41-53 that reduces cross-experiment
contamination risk or tightens the attribution for Exp 54, WITHOUT
changing the target-article set?

If YES, give the proposed ordering and name the risk it reduces.
If NO, state that the current ordering is optimal under the known
dependencies, and briefly defend why.

### RQ6. Target-article candidates for Exp 47, 51, 52, 53

Targets for these four experiments are TBC. Selection criteria:
  - 15-25K chars of native project code (not external fetch).
  - Exercises the specialist's tool set:
    - Exp 47 (biology): biopython sequence validation.
    - Exp 51 (physics): pint for dimensional analysis, astropy for
      constants.
    - Exp 52 (chemistry): RDKit for stoichiometry and molecular
      validity.
    - Exp 53 (engineering): safety-factor calculations.
  - Sufficient density of domain-specific claims that the specialist's
    routing rate is informative (not zero-activation).

Name any candidate file(s) in the Constraint_Engineering/ repository
that plausibly meet these criteria for each of Exp 47, 51, 52, 53.

If NO native candidate exists for one or more of these experiments,
state so plainly and recommend either (a) an adapter layer to present
external scientific content under the same schema, or (b) synthesising
a minimal native module specifically for the target, with the cost and
risk of each named.
"""

# ---------------------------------------------------------------------------
# Response format
# ---------------------------------------------------------------------------

RESPONSE_FORMAT = r"""
## Response format (mandatory)

For each question RQ1-RQ6:

1. FFAFP workings (Find, Follow, Analyse, Fix, P-pass). Keep short.
2. One final definitive position, bolded as `**Final position:** ...`.
3. Anchor every acceptance-criterion claim to the exact 40_gate.json
   pass_condition quote or to the Stage 6 orthogonality rule.

Compelled-convergence rules:

- Do NOT offer a menu of alternatives. Offer a single answer per
  question.
- If you believe a question is malformed under corrected framing, say
  so in one sentence and answer the closest well-formed question.
- Explicitly refute any temptation to reuse the "v1 preservation"
  framing. If you catch yourself relying on it, flag the slip and
  correct.
- Word budget: 2000 words total across RQ1-RQ6.

Scope guardrail reminder: proposals for experiments beyond Exp 54 are
out of scope and will be ignored.

Target: panel should converge on a single position per question.
Divergence after this round will require a yield-or-refute follow-up.
"""

# ---------------------------------------------------------------------------
# Compose full user prompt
# ---------------------------------------------------------------------------

def build_user_prompt() -> str:
    return (
        CORRECTED_FRAMING
        + "\n\n"
        + STAGE6_MATH
        + "\n\n"
        + "## Consolidated plan under review (full text)\n\n"
        + PLAN_TEXT
        + "\n\n"
        + QUESTIONS_SCOPED
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
            response = call_claude_cli(model_id, system_prompt, user_prompt)
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
    user_prompt = build_user_prompt()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    total_chars = len(system_prompt) + len(user_prompt)
    print(f"Dispatching Exp 40-54 consolidated plan review to {len(MODELS)} models")
    print(f"Prompt size: {total_chars} chars "
          f"(system {len(system_prompt)} + user {len(user_prompt)})")
    print(f"Plan under review: {PLAN_PATH.name} ({len(PLAN_TEXT)} chars)")
    print(f"Timestamp: {timestamp}")
    print(f"Logs: {LOGS_DIR}")
    print()

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = {
            ex.submit(_dispatch, label, mid, api, system_prompt, user_prompt): label
            for (label, mid, api) in MODELS
        }
        for fut in concurrent.futures.as_completed(futures):
            label = futures[fut]
            result = fut.result()
            results[label] = result
            if "error" in result:
                print(f"  {label}: ERROR in {result['time_s']}s — {result['error'][:200]}")
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
