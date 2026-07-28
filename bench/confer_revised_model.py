#!/usr/bin/env python3
"""
Confer: Revised Mathematical Model Review
==========================================
Dispatches to Gemini 3.1 Pro and Codex GPT-5.4 SEQUENTIALLY under
full CDSFL + FFAFP protocol. Reviews the revised mathematical model
incorporating three AIS-inspired modifications and two shadow extensions.

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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_revised_model"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Source code for grounding
CONVERGENCE_PATH = REPO_ROOT / "bench" / "dm" / "_convergence.py"
CONVERGENCE_TEXT = CONVERGENCE_PATH.read_text(encoding="utf-8")

TYPES_PATH = REPO_ROOT / "bench" / "dm" / "_types.py"
TYPES_TEXT = TYPES_PATH.read_text(encoding="utf-8")

SHADOW_PATH = REPO_ROOT / "bench" / "dm" / "_shadow_extensions.py"
SHADOW_TEXT = SHADOW_PATH.read_text(encoding="utf-8")

MANAGER_PATH = REPO_ROOT / "bench" / "dm" / "_manager.py"
MANAGER_TEXT = MANAGER_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Confer prompt
# ---------------------------------------------------------------------------

CONFER_PROMPT = f"""## Task

You are reviewing a proposed revision to the CDSFL mathematical model. The
revision incorporates three modifications inspired by Artificial Immune System
literature, plus two shadow-mode extensions for deferred evaluation. Your task
is to apply FFAFP (Find, Follow, Analyse, Fix, P-pass) to the complete revised
model as an integrated system.

## The Revised Model

The CDSFL system uses a recursive Bayesian self-assessment equation:

  R_k(i) = R_k(i-1) * (1 - q_ik) / (1 - q_ik * R_k(i-1))

with three-phase extension:
  Phase 1: q = eta * d * p  (detection with novelty)
  Phase 2: R_base = sigma * R_det + (1 - sigma) * R_old  (fix efficacy)
  Phase 3: R_k(i) = R_base * (1 - nu) + nu  (re-injection)

Three modifications are proposed (all verified by SymPy and Wolfram Alpha):

### Modification 1: Embedding Similarity (Gap 3)

Replace the current unigram/bigram Jaccard similarity in `_finding_similarity()`
with sentence-transformer embeddings (all-MiniLM-L6-v2) + cosine similarity.

Current implementation (bench/dm/_convergence.py):
- combined = 0.6 * uni_jaccard + 0.4 * bg_jaccard
- class_match bonus: sim = 0.3 + 0.7 * combined

Proposed: sim(f1, f2) = cosine(embed(f1.desc), embed(f2.desc)) + class_bonus

Key constraint: single-instance model loading with cached embeddings.
The ConvergenceDetector already accepts a pluggable similarity_fn parameter.

Reduction: when embeddings degenerate to bag-of-words, cosine approximates Jaccard.

### Modification 2: Continuous Suppression (Gap 2)

Replace hard tau_sim threshold (currently 0.33, not 0.50 as originally assessed)
with proportional mutual suppression:

  w(f) = max(prod_{{g in N(f)}} (1 - clip(sim(f,g), 0, s_max)), w_floor)

where N(f) = {{g : sim(f,g) >= s_min, g precedes f in ordering}}
Parameters: s_max=0.95, s_min=0.20, w_floor=0.05

This feeds into detection via novelty modulation:
  q_eff = eta * w(f) * d * p

And into kappa_set via weighted severity:
  kappa_set(r) = 1 - sum_j(w_j * S_j^novel) / sum_k(w_k * S_k^cum)

SymPy verified:
- w(5 neighbours, sim=0.6) = 0.0102 WITHOUT floor (Gemini's falsifier confirmed)
- w(10 neighbours, sim=0.6) = 0.000105 WITHOUT floor (catastrophic collapse)
- With w_floor=0.05: collapse prevented
- w_s=1 reduces to Stage 5 (no suppression)
- w_s=0 gives R_det = R_old (fully suppressed finding adds zero information)
- Marginal gain is monotonically increasing in w_s (correct direction)

Wolfram cross-validated:
- Suppression lowers break-even re-injection: nu*(q_eff=0.56) = 0.168 vs nu*(q_eff=0.28) = 0.084
- This is SAFER: less tolerance for bad fixes when detection quality is lower

### Modification 3: Persistent Memory Prior (Gap 1)

Replace fixed pi_k with evidence-backed Beta-Binomial prior from cross-experiment
immune memory:

  pi_k^(mem) = (n_conf + alpha) / (n_conf + n_rej + alpha + beta)

Memory counts decay exponentially: n_eff = n * exp(-lambda * age)
Half-life = ln(2)/lambda

SymPy/Wolfram verified:
- No memory (n_conf=n_rej=0, alpha=beta=1): pi = 0.5 (uninformative)
- All confirmed (n_conf -> inf): pi -> 1
- All rejected (n_rej -> inf): pi -> 0
- Domain always in (0, 1) for finite counts and positive alpha, beta

### Shadow Extensions (observation-only, for evaluation)

**Shadow Credit Scorecard (Gap 5):** Tracks per-model precision and novelty yield
without mutating CapabilityFingerprint. Uses Beta-Binomial smoothed precision:
(confirmed + 1) / (confirmed + rejected + 2). Composite weight = 0.5 * precision
+ 0.5 * novelty_yield.

NOTE: CapabilityFingerprint is ALREADY dynamically updated via windowed mean in
_manager.py (lines 712-829). The shadow scorecard tracks whether a simpler
LCS-inspired credit signal would produce different dispatch weights.

**Shadow Steering Predictor (Gap 4):** Logs predicted focus areas (flaw classes
found by other models but not this one) and compares against actual outcomes.
Does not inject into prompts. Evaluates prediction accuracy over time.

## Questions for FFAFP Review

For each modification and the overall composition, apply FFAFP:

1. **FIND:** What mathematical or engineering risks does this modification introduce?
2. **FOLLOW:** How do the three modifications interact? Are there emergent risks
   from their composition that don't exist individually?
3. **ANALYSE:** Are the reduction properties correct? Does each modification
   genuinely reduce to the existing model under stated conditions?
4. **FIX:** Propose any corrections, parameter adjustments, or additional
   safeguards needed.
5. **P-PASS:** Falsify the integrated model. Under what conditions does the
   revised model perform WORSE than the current model?

Additional questions:

A. **Parameter sensitivity:** The proposed parameters (s_max=0.95, s_min=0.20,
   w_floor=0.05, alpha=beta=1, lambda for decay) — are these reasonable starting
   points? What calibration strategy would you recommend?

B. **Extension opportunities:** Can you identify mathematical extensions to
   the revised model that we have not considered? Specifically:
   - Can the suppression weight interact with the three-phase equation in a
     way we haven't modelled?
   - Is there a natural way to make the memory decay rate lambda adaptive
     rather than fixed?
   - Are there other AIS/CAS principles that compose with this model?

C. **kappa_set modification:** The proposed weighted kappa_set uses
   sum(w_j * S_j) / sum(w_k * S_k). Is this the correct formulation,
   or should suppression weights appear only in the numerator (novel findings)?

D. **Shadow-to-live transition:** Under what conditions should the shadow
   extensions (credit scorecard, steering predictor) be promoted to live
   operation? What metrics from the shadow phase would justify promotion?

## Source Code

### _convergence.py (finding similarity, convergence detection)

```python
{CONVERGENCE_TEXT[:30000]}
```

### _types.py (configuration, CapabilityFingerprint)

```python
{TYPES_TEXT[:20000]}
```

### _shadow_extensions.py (shadow credit + steering)

```python
{SHADOW_TEXT}
```

### _manager.py (fingerprint updates, lines 700-830)

```python
{MANAGER_TEXT[MANAGER_TEXT.find('def update_fingerprints'):MANAGER_TEXT.find('def update_fingerprints') + 5000] if 'def update_fingerprints' in MANAGER_TEXT else 'update_fingerprints not found in expected location'}
```

Respond with rigorous FFAFP analysis. Be concrete. Reference specific line
numbers and functions. If a modification is flawed, say so and explain why.
If the composition is unsound, identify the failure mode.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'='*72}")
    print(f"  CONFER: Revised Mathematical Model Review — {ts}")
    print(f"  Protocol: CDSFL + FFAFP")
    print(f"  Models: Gemini 3.1 Pro, Codex 5.4")
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
    print("\nDispatching to Codex GPT-5.4...")
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
    out_path = LOGS_DIR / f"revised_model_{ts}.json"
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
