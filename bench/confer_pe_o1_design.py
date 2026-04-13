#!/usr/bin/env python3
"""
Confer: FFAFP PE 3-Gate Architecture & O1 Calibration Design
=============================================================
Dispatches to Gemini 3.1 Pro under full CDSFL + FFAFP protocol.

Evaluates four design questions:
  Q1 — FFAFP PE 3-gate enforcement architecture (concrete implementation)
  Q2 — O1 sensitivity dial (internal [0,1], UX 1-11, separate from breaker)
  Q3 — O1 configurable circuit breaker (PE-configurable, not binary)
  Q4 — O1 semantic clustering (root-cause grouping before HIL logging)

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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_pe_o1_design"
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
following four design questions for CDSFL Exp 39 PE and O1 architecture.

Apply the full CDSFL + FFAFP protocol to your analysis. This means:
- Classify all constraints as HARD or SOFT before analysis.
- Apply the falsification loop (P-pass) to every non-trivial claim.
- Trace dependency chains to system boundaries.
- Flag [VERIFY:current] and [SPECULATIVE] where required.
- End with a definitive stance per question.

## Context

CDSFL Exp 39, 12 April 2026. All 9 implementation phases (0-8) are
complete. 784 tests pass. From the prior confer session, Gemini
identified:

1. "Advisory capacity" is a HIL overload RISK FACTOR, not mitigation.
2. O1 needs semantic clustering + circuit breaker before shadow promotion.
3. FFAFP PE enforcement needs a 3-gate architecture.
4. Gate 3 (LLM judgement) should fail-open to HIL queue, not fail-closed.

The founder has now decided:

- The O1 SENSITIVITY DIAL and the CIRCUIT BREAKER must be SEPARATE controls.
- The sensitivity dial directly addresses HIL overload: the USER decides
  what level of detail they can cope with and want to see.
- The circuit breaker is a safety switch but must still be queryable and
  configurable via the PE — not a binary on/off kill switch. It should be
  configurable by admins with meaningful parameters.
- Gate 3 fail-open to HIL queue is confirmed: the sensitivity dial then
  filters what actually reaches the user's attention.

The O1 ouroboros cell currently exists as a shadow-mode observer with
macrophage (anomaly hunting) and microglia (self-referential health) modes.
Each observation has: observation_id, mode, category, description, severity
(0-1), evidence dict, is_anomaly flag, timestamp.

---

## QUESTION 1 — FFAFP PE 3-Gate Enforcement Architecture

The FFAFP constraint set C_FFAFP = {S_min, G-completeness, d_tool,
sigma_measured, q_retest} is formalised in the mathematical appendix.
PE enforcement has NOT been built.

The prior confer proposed:
- Gate 1 (Mechanical - Strict): d_tool (tool logs exist), q_retest (test
  exit code == 0). Revised: assert specific structural outputs, not just
  invocation presence.
- Gate 2 (Heuristic - Strict): S_min (diff size, AST node counts).
- Gate 3 (Judgement - LLM PE Sub-agent): G-completeness, sigma_measured.
  Fail-open to HIL queue, not fail-closed.

### Questions:

a) Define the concrete data structures for each gate. What does a gate
   receive as input? What does it output (pass/fail/escalate)? What is the
   interface contract between gates and the pipeline?

b) Gate ordering: should gates be sequential (1→2→3) with early rejection,
   or parallel with aggregated verdict? What are the tradeoffs?

c) How does the sensitivity dial interact with Gate 3 escalations? Gate 3
   fail-open means uncertain findings go to HIL — but the sensitivity dial
   controls what the user actually sees. Define the interaction precisely.

d) Where in the existing immune pipeline (triage → Stage 2 cell dispatch →
   convergence → ImmuneResponse) should the PE gates be placed?

Apply FFAFP to your analysis. P-pass every architectural decision.

---

## QUESTION 2 — O1 Sensitivity Dial

The sensitivity dial is a user-configurable control that determines how
much O1 output reaches HIL attention.

Design parameters:
- Internal: float in [0.0, 1.0], name: o1_sensitivity
- UX: integer 1-11, mapping: sensitivity = (ux_value - 1) / 10
- At 11 (1.0): no filtering, everything O1 found reaches HIL
- At 1 (0.0): maximum filtering, only critical systemic anomalies surface
- Cultural reference: "This one goes to eleven" (Spinal Tap)

### Questions:

a) Define the importance scoring function for O1 observations. The current
   OuroborosObservation has a severity field (0-1) and is_anomaly flag.
   Is severity alone sufficient as the importance score, or do we need a
   composite? What factors should the composite include?

b) Define the filtering mechanism: min_importance = f(sensitivity). Is
   linear (1.0 - sensitivity) correct, or should the mapping be non-linear?
   Consider: at 11, the user genuinely wants EVERYTHING. At 1, they want
   only critical items. The middle range (5-8) is where most users will
   operate. Should the curve be steeper at low sensitivity and flatter at
   high?

c) Should certain anomaly categories ALWAYS bypass the sensitivity filter?
   E.g. should a "persistent_anomaly" (3+ consecutive rounds) always reach
   HIL regardless of the dial setting?

d) How does the sensitivity dial persist? PE config, per-user, per-project?

Apply FFAFP. P-pass the scoring function and filter mechanism.

---

## QUESTION 3 — O1 Configurable Circuit Breaker

The circuit breaker prevents O1 from flooding HIL during systemic events
(e.g. a base class API change causing 200 detected anomalies). It is
SEPARATE from the sensitivity dial — the breaker protects the human
regardless of dial setting.

The founder requires: the breaker must NOT be a binary on/off kill switch.
It must be PE-configurable with meaningful parameters that admins can tune.

### Questions:

a) Define the circuit breaker parameters. At minimum: rate threshold
   (exceptions per time window), window duration, cool-down period. What
   else? Should there be graduated response (warn → throttle → suspend)
   rather than a single trip point?

b) When the breaker trips, what exactly happens? Options:
   - O1 stops observing entirely (too aggressive?)
   - O1 continues observing but stops logging to HIL queue (data loss?)
   - O1 continues observing and logging locally, but HIL queue receives
     only a single "systemic anomaly" summary (Gemini's recommendation)

c) How does the breaker interact with semantic clustering? If clustering
   correctly groups 200 instances into 3 root causes, the breaker should
   NOT trip (3 clustered exceptions is fine). If clustering fails and 200
   raw exceptions hit the queue, the breaker SHOULD trip. Define the
   interaction.

d) Breaker recovery: how does it reset? Timer-based? Rate drop below
   threshold? Manual admin reset? Combination?

Apply FFAFP. P-pass the breaker design, especially the clustering
interaction.

---

## QUESTION 4 — O1 Semantic Clustering

Before O1 observations reach the HIL queue (and before the sensitivity
filter and circuit breaker evaluate them), identical or near-identical
anomalies should be grouped by root cause.

### Questions:

a) Define the clustering algorithm. The observations have category, description,
   severity, and evidence fields. What similarity measure groups them?
   Can we reuse the existing embedding similarity backend (bench/dm/_similarity.py
   with sentence-transformers / Jaccard fallback)?

b) Cluster representation: how is a cluster presented to HIL? A single
   representative observation + count? A summary? How much detail is
   preserved vs compressed?

c) Temporal scope: does clustering operate within a single round, across
   rounds, or both? Cross-round clustering would detect "same anomaly
   detected every round" as one persistent cluster rather than N separate
   alerts.

d) How does cluster size affect importance scoring? Should a cluster of 50
   identical anomalies score higher (systemic issue) or lower (redundant
   noise) than a single unique anomaly?

Apply FFAFP. P-pass the clustering design against the "base class API
change" scenario from the prior confer.

---

Respond with rigorous FFAFP analysis for ALL FOUR questions. Be concrete:
propose data structures, parameter ranges, pseudocode where helpful.
End with a definitive stance per question.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'='*72}")
    print(f"  CONFER: FFAFP PE 3-Gate Architecture & O1 Calibration Design")
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
            "topic": "pe_3gate_and_o1_calibration_design",
            "questions": [
                "Q1: FFAFP PE 3-gate enforcement architecture",
                "Q2: O1 sensitivity dial (internal [0,1], UX 1-11)",
                "Q3: O1 configurable circuit breaker",
                "Q4: O1 semantic clustering",
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
            "topic": "pe_3gate_and_o1_calibration_design",
            "error": str(e),
            "time_s": round(ge_time, 1),
        }

    # --- Save JSON results ---
    out_json = LOGS_DIR / f"pe_o1_design_{ts}.json"
    out_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nJSON saved to: {out_json}")

    # --- Save plaintext response ---
    if "response" in result:
        out_txt = LOGS_DIR / f"pe_o1_design_{ts}.txt"
        header = (
            f"CONFER: FFAFP PE 3-Gate Architecture & O1 Calibration Design\n"
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
