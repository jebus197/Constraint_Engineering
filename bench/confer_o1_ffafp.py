#!/usr/bin/env python3
"""
Confer: O1 FFAFP Enforcement and Exception-Based Auditing Review
================================================================
Dispatches to Gemini 3.1 Pro under full CDSFL + FFAFP protocol.

Evaluates two questions for Exp 39 preparation:
  Q1 — FFAFP: PE enforcement vs mathematical documentation
  Q2 — O1 exception-based auditing and HIL overload mitigation

Date: 12 April 2026
Protocol: CDSFL + FFAFP (Find, Follow, Analyse, Fix, P-pass)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo setup
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import call_gemini

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
            os.environ.setdefault(_k, _v)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_o1_ffafp"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"

# ---------------------------------------------------------------------------
# Load CDSFL directives as system prompt
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Confer prompt
# ---------------------------------------------------------------------------

CONFER_PROMPT = """## Task

Under CDSFL and FFAFP (Find, Follow, Analyse, Fix, P-pass), evaluate the
following two questions regarding CDSFL Exp 39 preparation.

Apply the full CDSFL + FFAFP protocol to your analysis. This means:
- Classify all constraints as HARD or SOFT before analysis.
- Apply the falsification loop (P-pass) to every non-trivial claim.
- Trace dependency chains to system boundaries.
- Flag [VERIFY:current] and [SPECULATIVE] where required.
- End with a definitive stance.

## Context

CDSFL Exp 39 preparation, 12 April 2026. We have just completed
implementation of 9 phases including: embedding similarity, continuous
suppression (permutation-invariant top-k), persistent immune memory with
blended prior, specialist B-Cell dispatch (shadow), ouroboros cell O1 (shadow
prototype with macrophage + microglia modes), FFAFP formalisation, and
mathematical appendix expansion (7 new sections).

---

## QUESTION 1 — FFAFP: PE Enforcement vs Mathematical Documentation

FFAFP (the 5-constraint admissibility set C_FFAFP = {S_min, G-completeness,
d_tool, sigma_measured, q_retest}) has been formalised in the mathematical
appendix section 1.2 as a calibration protocol for R_k(i). It explicitly
states "FFAFP is not a separate mathematical model" and documents what each
constraint means and why it matters.

However, the actual enforcement mechanism — hard constraints in the Policy
Engine that reject findings failing C_FFAFP before they enter R_k(i) — has
NOT been built. The founder's view is that FFAFP should be a hard PE
constraint, not just appendix documentation.

### Questions:

a) Is formalising FFAFP in the mathematical appendix appropriate as
   DOCUMENTATION of the constraint set, even though the enforcement belongs
   in the PE?

b) What would PE enforcement of FFAFP look like? Which constraints can be
   mechanically enforced vs which require human judgement?

c) Are there risks in having the specification (appendix) and enforcement
   (PE) in different locations?

Apply FFAFP to your analysis:
- FIND: Identify the current state — specification exists, enforcement does
  not. What are the implications?
- FOLLOW: Trace consequences of spec-enforcement separation through the
  pipeline. What breaks or degrades?
- ANALYSE: Under what conditions does the gap between specification and
  enforcement produce incorrect or unreliable outputs?
- FIX: Propose concrete PE enforcement architecture for C_FFAFP.
- P-PASS: Falsify your proposed enforcement architecture.

---

## QUESTION 2 — O1 Exception-Based Auditing and HIL Overload

You previously identified HIL cognitive overload (>50 claims/day) as a
genuine risk. The O1 ouroboros cell uses exception-based audit logging: only
anomalies are surfaced to HIL, not routine observations.

The founder argues that the HIL overload concern is further mitigated by
three containment layers:

1. SCOPE CONSTRAINT: Beyond Exp 39 (which has an unusually large problem
   set), O1 would typically be constrained within a specific, much smaller
   problem set.

2. ADVISORY CAPACITY: O1 behaves in an entirely advisory capacity — it flags
   potential issues but cannot override pipeline verdicts or modify pipeline
   state.

3. SHADOW + SCHEMA CONSTRAINT: O1 runs in purely shadow mode initially, and
   even when promoted, it operates within the full CDSFL schema (FFAFP,
   convergence detection, severity veto, etc.), which provides additional
   structural containment.

### Questions:

a) Do these three layers adequately address the HIL overload concern you
   raised?

b) What promotion criteria would you recommend for moving O1 from shadow to
   active mode?

c) Are there failure modes of exception-based auditing that these
   containment layers don't address?

Apply FFAFP to your analysis:
- FIND: Identify the HIL overload risk surface with and without the three
  containment layers.
- FOLLOW: Trace the information flow from O1 anomaly detection through
  exception logging to HIL review. Where are the bottlenecks?
- ANALYSE: Under what conditions do the containment layers fail to prevent
  overload? What is the residual risk?
- FIX: Propose specific promotion criteria and any additional safeguards.
- P-PASS: Falsify the claim that "exception-based auditing with three
  containment layers is sufficient." Under what conditions does it fail?

---

Respond with rigorous FFAFP analysis for BOTH questions. Be concrete and
specific. If a claim is flawed, say so and explain why. If it is sound,
state the conditions under which it remains sound and the boundaries beyond
which it breaks.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'='*72}")
    print(f"  CONFER: O1 FFAFP Enforcement & Exception-Based Auditing Review")
    print(f"  Timestamp: {ts}")
    print(f"  Protocol: CDSFL + FFAFP")
    print(f"  Model: Gemini 3.1 Pro")
    print(f"{'='*72}\n")

    # --- Gemini ---
    print("Dispatching to Gemini 3.1 Pro...")
    t0 = time.monotonic()
    try:
        ge_response = call_gemini(
            model_id=GEMINI_MODEL,
            system_prompt=CDSFL_TEXT,
            user_prompt=CONFER_PROMPT,
            max_tokens=32768,
            timeout=300,
            max_retries=5,
            backoff_base=3.0,
        )
        ge_time = time.monotonic() - t0
        print(f"  Gemini responded in {ge_time:.1f}s ({len(ge_response)} chars)")

        result = {
            "model": GEMINI_MODEL,
            "timestamp": ts,
            "protocol": "CDSFL + FFAFP",
            "topic": "o1_ffafp_enforcement_and_hil_overload",
            "questions": [
                "Q1: FFAFP PE enforcement vs mathematical documentation",
                "Q2: O1 exception-based auditing and HIL overload",
            ],
            "response": ge_response,
            "time_s": round(ge_time, 1),
            "chars": len(ge_response),
        }

    except Exception as e:
        ge_time = time.monotonic() - t0
        print(f"  Gemini FAILED after {ge_time:.1f}s: {e}")
        result = {
            "model": GEMINI_MODEL,
            "timestamp": ts,
            "protocol": "CDSFL + FFAFP",
            "topic": "o1_ffafp_enforcement_and_hil_overload",
            "error": str(e),
            "time_s": round(ge_time, 1),
        }

    # --- Save JSON results ---
    out_json = LOGS_DIR / f"o1_ffafp_{ts}.json"
    out_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nJSON saved to: {out_json}")

    # --- Save plaintext response ---
    if "response" in result:
        out_txt = LOGS_DIR / f"o1_ffafp_{ts}.txt"
        header = (
            f"CONFER: O1 FFAFP Enforcement & Exception-Based Auditing Review\n"
            f"Timestamp: {ts}\n"
            f"Model: {GEMINI_MODEL}\n"
            f"Protocol: CDSFL + FFAFP\n"
            f"Response time: {result['time_s']}s\n"
            f"Response length: {result['chars']} chars\n"
            f"{'='*72}\n\n"
        )
        out_txt.write_text(header + result["response"] + "\n", encoding="utf-8")
        print(f"Text saved to: {out_txt}")

    # --- Print response ---
    if "error" in result:
        print(f"\n{'='*72}")
        print(f"  GEMINI: ERROR -- {result['error']}")
        print(f"{'='*72}")
    else:
        print(f"\n{'='*72}")
        print(f"  GEMINI ({result['model']}) -- {result['time_s']}s")
        print(f"{'='*72}\n")
        print(result["response"])

    return result


if __name__ == "__main__":
    run_confer()
