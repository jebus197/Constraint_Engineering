#!/usr/bin/env python3
"""
Exp 40 Pre-launch Panel Re-audit — Round 1
===========================================

A single-round compelled-convergence panel audit under CORRECTED framing,
following the revert (commit 5c81f33) of a previous five-round convergence
that carried a wrong "v1 preservation" framing.

The prior convergence (reverted commit b3d9420) introduced "P2. Runner v1
preservation" as a standing policy and used it as the decisive argument
on several questions. The policy was invalid: it conflated
reference_runner.py (v1, retained on disk as historical reference to the
first Exp-38 demonstration of the full Stage 6 mathematical model) with
reference_runner_v2.py (v2, 4922 lines, the actual Exp 40 runner, actively
extended through Phase A commit 8b8682d and Phase B commit bdfc93a).

This audit asks four narrow questions under corrected framing. All five
panel models answer independently under CDSFL + FFAFP + star topology.
No menu-for-founder: the panel should converge on a single position per
question, with reasoning visible.

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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_reaudit_round1"
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
# Corrected framing preamble (load-bearing, panel reads before every question)
# ---------------------------------------------------------------------------

CORRECTED_FRAMING = r"""
## Corrected framing for Exp 40 pre-launch (load-bearing)

A prior five-round convergence on Exp 40 pre-launch was REVERTED on
2026-04-20 because the briefing carried a wrong framing. The error was
introduced as "P2. Runner v1 preservation" — a purported standing policy
treating Exp 40 as a "preservation run" for runner v1.

The correct facts are:

1. `bench/reference_runner.py` (v1) is retained on disk as a HISTORICAL
   REFERENCE to the first Exp-38 demonstration of the full Stage 6
   mathematical model. It is NOT the Exp 40 runner. It has no
   preservation policy attached to it.

2. `bench/reference_runner_v2.py` (v2, 4922 lines) IS the Exp 40 runner.
   It is NOT frozen. It has been actively extended through:
   - Phase A (commit 8b8682d, 14 April): 1D.5, 1D.6, 1E.6, 1E.7, 1E.10
     library-form wrapper (98 tests).
   - Phase B (commit bdfc93a, 17 April): 1D.3, 1E.3 audit, 1E.4, 1E.5,
     1E.8, 1E.9, 1E.11, 1E.12 (200+ tests).

3. Exp 40's real acceptance criterion per `bench/exp40_configs/40_gate.json`:
   `"pass_condition": "gamma >= 0.30 OR (3 consecutive rounds with 0 novel
   CRITICAL findings). Gamma-alt implemented in
   reference_runner_v2._check_gamma_alt_convergence."`
   Additional logged signals: all 5 models parseable with R_k, R_k adoption
   ≥ 80% across models, §17 and §18 admissibility rates logged.

4. Test article: `bench/dm/_feedback.py` (the §17 feedback channel
   implementation, ~22K chars). Context: `bench/dm/_types.py` (~30K).
   Directives live: §17 feedback channel, §18 divergence. Deferred to
   Exp 54: `eta_int_modulator` wiring into `compute_rk`.

5. The 14-experiment single-target series (Exp 40-53) is followed by Exp 54,
   the integration run with 2×2 factorial for §17/§18 attribution. Lessons
   from each single-target experiment fold into the next experiment's
   runner configuration, not back into v2's runtime logic during the run.

No "preservation" policy exists. The panel should answer the four
questions below as if the only valid anchors are the 40_gate.json
acceptance criterion and the Stage 6 mathematical model. Ignore any
instinct, memory, or argument that presumes v1 preservation — that
framing has been refuted.
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
# Fix ledger (condensed) — shared with the panel
# ---------------------------------------------------------------------------

LEDGER_BRIEF = r"""
## Audit summary (for context, not for re-litigation)

An agent audit classified every fix proposed across the five reverted
confer rounds. Ledger summary (16 entries deduplicated):

- ALREADY_IN_V2 (5): SMT sandbox fix, verdict-combination alpha rule,
  star topology (40_gate.json line 7).
- MISSING_VALID (6): 1E.10 wrapper activation, K/L/M specialist flip,
  a minimal reason-trace instrumentation, a counterfactual-protocol fix
  (ceil not floor), a scoped-challenge topology idea for Exp 41.
- MISSING_FRAMING_DEPENDENT (3): four-family preservation criteria,
  10-field schema "preservation" enum hard-coding, conditional-ceiling
  runtime wiring as "preservation guard".
- OFF-TARGET (2): conditional novelty ceiling in Exp 40 scope, full
  10-field reason-trace schema as Exp 40 gate.

The four questions below target only the residual doubt under corrected
framing. They are NOT asking to re-run the full five-round convergence.
They are asking whether the previously-locked answers survive when the
"v1 preservation" framing is removed.
"""

# ---------------------------------------------------------------------------
# The four narrow questions
# ---------------------------------------------------------------------------

QUESTIONS = r"""
## Four residual questions under corrected framing

### RQ1. Activation-sequence gate — blocking or not?

Three items were flagged as outstanding before Exp 40 launch:

  (a) SMT sandbox fix for `_verify_sympy` (currently returns UNCERTAIN
      on every claim because the subprocess init sets
      `global_dict={'__builtins__': {}}`, which prevents SymPy from
      constructing Integer literals).
  (b) 1E.10 runtime wrapper activation at `reference_runner_v2.py:3510`
      (replace bare `compute_rk` with `compute_rk_with_eta_channel`, m_div
      = 1.0 hardcoded until Exp 54's `eta_int_modulator` wiring).
  (c) K/L/M specialist cell live-promotion (extending LIVE_SPECIALIST_DOMAINS
      at `immune_agents.py:334` to include physics, chemistry, engineering).

For each of (a), (b), (c), answer under CORRECTED framing:

  Is this item REQUIRED for Exp 40 to validate §17 feedback channel +
  §18 divergence admissibility rates against `bench/dm/_feedback.py`,
  under the acceptance criterion `gamma >= 0.30 OR (3 consecutive rounds
  with 0 novel CRITICAL findings)`?

  - REQUIRED: name the specific admissibility signal or γ-alt path it
    enables.
  - NOT REQUIRED: state whether it should still be activated (shadow-
    promotion-now directive) or deferred; reason briefly.
  - PARTIALLY REQUIRED: name the subset of §17/§18 signals it affects.

### RQ2. Reason-trace instrumentation — Exp 40 or Exp 54?

The reverted convergence locked a 10-field reason-trace schema with closed
enums and a runner-derived compliance flag. Under corrected framing
(§17 + §18 admissibility, not v1 preservation), answer:

  Does Exp 40's acceptance criterion (γ-alt + admissibility-rate logging)
  require any per-finding reason-trace logging of model-level
  disagreement, yield, or refute? If yes, give the MINIMUM field set
  (≤5 fields) strictly necessary for §17 admissibility attribution.
  If no, state so plainly and name which later experiment (Exp 41? 54?)
  is the correct home for reason-trace instrumentation.

### RQ3. Four predicate families — diagnostic or gating?

The reverted convergence locked four predicate families as a "preservation"
gate: math-path fidelity, correction fidelity, counterfactual sensitivity,
convergence stability. Under corrected framing, answer PER FAMILY:

  Does this family belong in Exp 40 as
  - post-hoc diagnostic instrumentation (log, analyse after the run, do
    NOT gate acceptance), or
  - additional acceptance gate (in addition to the γ-alt criterion in
    40_gate.json), or
  - not part of Exp 40 at all (defer to Exp 41 or Exp 54 harness)?

  Justify each choice against the 40_gate.json pass_condition explicitly.

### RQ4. Conditional novelty ceiling — Exp 40 scope or not?

The ceiling `nu_max(R_min) = 1 - ((1 - ((R - R_min) / (R * (1 - R_min) *
eta_int * d * p))) / c_ext)` is a valid Stage 6 algebraic artefact given
fixed eta_int, d, p, c_ext and a chosen validity floor R_min. Under
corrected framing, answer:

  Does this ceiling belong in Exp 40 scope? Pick exactly one:
  - YES, as runtime guard (new code path in v2): not allowed if it alters
    what the γ-alt evidence is evidence of.
  - YES, as post-hoc sanity instrumentation (computed from the Exp 40 log
    after the run): acceptable if it does not gate acceptance.
  - NO, not part of Exp 40 scope: defer to which experiment?
"""

# ---------------------------------------------------------------------------
# Response format
# ---------------------------------------------------------------------------

RESPONSE_FORMAT = r"""
## Response format (mandatory)

For each question RQ1–RQ4:

1. FFAFP workings (Find, Follow, Analyse, Fix, P-pass). Keep short.
2. One final definitive position, bolded as "**Final position:** ...".
3. Anchor every acceptance-criterion claim to the exact 40_gate.json
   pass_condition quote or to the Stage 6 orthogonality rule.

Compelled-convergence rules:

- Do NOT offer a menu of alternatives. Offer a single answer per
  sub-question.
- If you believe the question is malformed under corrected framing, say so
  in one sentence and answer the closest well-formed question.
- Explicitly refute any temptation to reuse the "v1 preservation" framing.
  If you catch yourself relying on it, flag the slip and correct.
- Word budget: 1500 words total across RQ1–RQ4.

Target: panel should converge on a single position per question.
Divergence after this round will require a yield-or-refute follow-up.
"""

# ---------------------------------------------------------------------------
# Compose full prompt
# ---------------------------------------------------------------------------

def build_user_prompt() -> str:
    return (
        CORRECTED_FRAMING
        + "\n\n"
        + STAGE6_MATH
        + "\n\n"
        + LEDGER_BRIEF
        + "\n\n"
        + QUESTIONS
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
    print(f"Dispatching to {len(MODELS)} models, prompt {total_chars} chars "
          f"(system {len(system_prompt)} + user {len(user_prompt)})")
    print(f"Timestamp: {timestamp}")
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
