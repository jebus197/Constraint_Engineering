#!/usr/bin/env python3
"""
Confer: AIS/Holland/Kohonen Gap Integration Review
===================================================
Dispatches to Gemini 3.1 Pro and Codex 5.6 SEQUENTIALLY under
full CDSFL + FFAFP protocol. Reviews 5 identified gaps from
Holland/Kohonen/AIS literature assessment and evaluates integration
feasibility, extension potential, and whether work should proceed.

Date: 12 April 2026
Protocol: CDSFL + FFAFP (Find, Follow, Analyse, Fix, P-pass)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import call_openrouter, call_gemini

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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_ais_integration"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"  # Codex via OpenRouter (gpt-5.4 is the valid ID)

# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Load the assessment for context
ASSESSMENT_PATH = REPO_ROOT / "experimental_notes" / "Holland_Kohonen_AIS_Assessment_2026-04-12.md"
ASSESSMENT_TEXT = ASSESSMENT_PATH.read_text(encoding="utf-8")

# Load key source files for grounding
IMMUNE_PATH = REPO_ROOT / "bench" / "immune_agents.py"
IMMUNE_TEXT = IMMUNE_PATH.read_text(encoding="utf-8")

RUNNER_CORE_PATH = REPO_ROOT / "bench" / "runner_core.py"
RUNNER_CORE_TEXT = RUNNER_CORE_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Confer prompt
# ---------------------------------------------------------------------------

CONFER_PROMPT = f"""## Context

You are reviewing a literature assessment that evaluated three research lineages
(John Henry Holland's CAS/LCS, Teuvo Kohonen's SOMs, Artificial Immune Systems)
against the CDSFL system. The assessment identified 5 gaps worth investigating.

**Your task:** Apply FFAFP (Find, Follow, Analyse, Fix, P-pass) to each gap.
For each:
- FIND: What exactly is the gap? Where in the codebase does it manifest?
- FOLLOW: What are the downstream consequences if this gap is closed? What
  interfaces change? What existing components are affected?
- ANALYSE: Is the proposed integration sound? Use the actual source code below
  to ground your analysis — do not speculate about code you haven't read.
- FIX: Propose a concrete implementation. Specify file paths, functions to
  modify, approximate LOC, and any new dependencies.
- P-PASS: Falsify your own proposal. What could go wrong? What assumptions
  are you making? Under what conditions would this make things worse?

## The 5 Gaps

1. **Persistent immune memory across experiments** — Currently within-experiment
   only. The NK Cell false-positive database is manually curated. Proposed:
   auto-persist confirmed false positives and validated finding patterns with
   encounter counts and outcome records across experiments.

2. **Continuous suppression function (idiotypic network-inspired)** — Replace
   the hard tau_sim threshold (currently 0.50, adjusted twice) with proportional
   mutual suppression: weight = base × ∏(1 - sim). Maintains diversity without
   a threshold.

3. **Embedding-based similarity** — Replace unigram/bigram Jaccard in
   `_finding_similarity()` with sentence-transformer embeddings + cosine
   similarity. The code already flags this as a known limitation in a docstring.
   `sentence-transformers` is available in the environment.

4. **Anticipatory dispatch (Holland's internal models)** — Predict what each
   model will find next round based on per-model novelty rates and steer
   prompts toward unexplored areas. The DiminishingReturnsDetector already
   tracks per-model mu values.

5. **Credit assignment loop (LCS-inspired)** — Feed confirmation/rejection
   verdicts back into model dispatch weighting. Currently the CapabilityFingerprint
   is static.

## Additional Questions

A. How can these 5 gaps be composed? Are there dependencies between them
   (e.g., does embedding similarity enable better persistent memory)?

B. Are there extension opportunities beyond the 5 gaps that the assessment
   missed?

C. For each gap, give a clear GO / NO-GO / DEFER recommendation with reasoning.

D. What is the correct implementation order if we proceed?

## Assessment Document

{ASSESSMENT_TEXT}

## Source Code: immune_agents.py (finding similarity, immune pipeline)

```python
{IMMUNE_TEXT[:40000]}
```

## Source Code: runner_core.py (finding parsers, convergence)

```python
{RUNNER_CORE_TEXT[:40000]}
```

Respond with structured FFAFP analysis per gap, then the composition/extension/
ordering questions. Be rigorous. Do not force connections. If a gap is not worth
closing, say so and explain why.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'='*72}")
    print(f"  CONFER: AIS Integration Review — {ts}")
    print(f"  Protocol: CDSFL + FFAFP")
    print(f"  Models: Gemini 3.1 Pro, Codex 5.6")
    print(f"{'='*72}\n")

    results = {}

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
        results["gemini"] = {
            "model": GEMINI_MODEL,
            "response": ge_response,
            "time_s": round(ge_time, 1),
            "chars": len(ge_response),
        }
    except Exception as e:
        ge_time = time.monotonic() - t0
        print(f"  Gemini FAILED after {ge_time:.1f}s: {e}")
        # Fallback: try via OpenRouter
        print("  Falling back to Gemini via OpenRouter...")
        t0 = time.monotonic()
        try:
            ge_response = call_openrouter(
                model_id="google/gemini-3.1-pro-preview",
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=300,
                max_retries=3,
                backoff_base=3.0,
                extra_body={"reasoning": {"effort": "high"}},
            )
            ge_time = time.monotonic() - t0
            print(f"  Gemini (OpenRouter) responded in {ge_time:.1f}s ({len(ge_response)} chars)")
            results["gemini"] = {
                "model": "google/gemini-3.1-pro-preview (OpenRouter fallback)",
                "response": ge_response,
                "time_s": round(ge_time, 1),
                "chars": len(ge_response),
            }
        except Exception as e2:
            print(f"  Gemini (OpenRouter) also FAILED: {e2}")
            results["gemini"] = {"error": str(e2)}

    # --- Codex ---
    print("\nDispatching to Codex 5.6...")
    t0 = time.monotonic()
    try:
        cx_response = call_openrouter(
            model_id=CX_MODEL,
            system_prompt=CDSFL_TEXT,
            user_prompt=CONFER_PROMPT,
            max_tokens=32768,
            timeout=300,
            max_retries=3,
            backoff_base=3.0,
        )
        cx_time = time.monotonic() - t0
        print(f"  Codex responded in {cx_time:.1f}s ({len(cx_response)} chars)")
        results["codex"] = {
            "model": CX_MODEL,
            "response": cx_response,
            "time_s": round(cx_time, 1),
            "chars": len(cx_response),
        }
    except Exception as e:
        cx_time = time.monotonic() - t0
        print(f"  Codex FAILED after {cx_time:.1f}s: {e}")
        results["codex"] = {"error": str(e)}

    # --- Save results ---
    out_path = LOGS_DIR / f"ais_integration_{ts}.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"\nResults saved to: {out_path}")

    # Print responses
    for model_key in ["gemini", "codex"]:
        data = results.get(model_key, {})
        if "error" in data:
            print(f"\n{'='*72}")
            print(f"  {model_key.upper()}: ERROR — {data['error']}")
            print(f"{'='*72}")
        elif "response" in data:
            print(f"\n{'='*72}")
            print(f"  {model_key.upper()} ({data.get('model', '?')}) — {data['time_s']}s")
            print(f"{'='*72}\n")
            print(data["response"])

    return results


if __name__ == "__main__":
    run_confer()
