#!/usr/bin/env python3
"""
Confer: Novelty/Discovery Extension to Refined Unified Equation
================================================================
Dispatches to Gemini 3.1 Pro and Codex GPT-5.4 under combined 4-layer schema:
  Layer 1: Meta Structured Prompting (arXiv 2603.01896)
  Layer 2: CDSFL constraints (core formal directives)
  Layer 3: FFAFP (Find-Follow-Analyse-Fix with P-pass, up to 5 passes)
  Layer 4: Conversational fallback

Date: 9 April 2026
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import call_openrouter, call_gemini

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_novelty_extension"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

# ---------------------------------------------------------------------------
# 4-Layer System Prompt
# ---------------------------------------------------------------------------

FOUR_LAYER_SYSTEM = f"""{CDSFL_TEXT}

---

## Interaction Protocol: Combined 4-Layer Schema

You are operating under a combined 4-layer interaction schema. Apply ALL four
layers simultaneously. They are complementary, not alternatives.

### Layer 1 — Meta Structured Prompting (arXiv 2603.01896)

For EVERY claim, finding, or proposed extension, you MUST provide:

1. **STRUCTURED CERTIFICATE:** State your premises explicitly. Trace execution
   through concrete examples (with specific inputs and expected outputs). Derive
   a formal conclusion.

2. **FIND-FOLLOW-ANALYSE-FIX (FFAF):** For every issue —
   FIND: State the issue, its location in the mathematics, and your evidence.
   FOLLOW: Before proposing any change, trace consequences through the entire
   equation system. What depends on this term? What special cases does it affect?
   What boundary conditions shift?
   ANALYSE: State dispassionately whether this is CONFIRMED, UNCERTAIN, or
   REJECTED based on mathematical proof, not intuition.
   FIX: For CONFIRMED issues only, propose the simplest sufficient correction
   that preserves all verified special cases.

3. **SELF-FALSIFICATION:** Actively try to disprove your own conclusions before
   presenting them. Retract claims you can disprove. Only present claims that
   survive your own attempted falsification.

4. **MATHEMATICAL RIGOUR:** Provide formal proofs (symbolic, set-theoretic, or
   by contradiction) for every mathematical claim. "I believe" is not evidence.

### Layer 2 — CDSFL Constraints

The full CDSFL core formal directives above apply. Classify every constraint as
HARD or SOFT. Physics and mathematics take precedence. The falsification loop
(P-pass) is mandatory for all non-trivial claims.

### Layer 3 — FFAFP with Iterated P-Pass

You MUST P-pass your own results up to 5 times, or until you assess diminishing
returns (two consecutive passes producing no new findings above consequence
threshold). Each P-pass must attempt to break your previous conclusions.

Structure your response as:
  PASS 1: Initial analysis and findings
  PASS 2: Falsification of Pass 1
  PASS 3: Falsification of Pass 2 survivors
  ...continue until convergence or pass 5

Only present conclusions that survive ALL passes. Retracted claims must be
explicitly listed with the reason for retraction.

### Layer 4 — Conversational Fallback

Where structured format does not naturally apply (context-setting, qualitative
discussion, boundary identification), use natural conversational prose. Do not
force structure where it adds no rigour. Depth over format compliance.

---

## Standing Constraint

Discovery and novelty are encouraged — but ONLY within the Popperian framework
of CDSFL. Every proposed extension must be falsifiable. Every mathematical claim
must be verified symbolically. The goal is an equation that is both internally
consistent (all special cases hold, all reductions verified) and externally
complete (captures the phenomena it claims to capture, with honest boundaries
stated for what it does not).

You are not being asked to agree. You are being asked to find what is wrong,
propose what is missing, and verify that your proposals survive falsification.
"""

# ---------------------------------------------------------------------------
# User Prompt: The Mathematical Context and Ask
# ---------------------------------------------------------------------------

USER_PROMPT = """
# Context: Extending the Refined Unified Self-Assessment Equation

## Background

We have derived a unified self-assessment equation for model-level metacognition
under the CDSFL (Constraint-Driven Scientific Falsification Layer) framework.
The equation models how a model's residual risk estimate evolves across
falsification cycles.

## The Refined Equation (verified SymPy + Wolfram, 8 April 2026)

**Phase 1 — Detection (Find + Falsify):**

  R_det = R_k(i-1) · (1 − q_ik) / (1 − q_ik · R_k(i-1))

where q_ik = clamp(d_ik · p_ik, 0, 1)

Log-odds form: logit(R_det) = logit(R_k(i-1)) + log(1 − q_ik)

**Phase 2 — Resolution (Fix):**

  R_k(i) = R_det · (1 − ν_k) + ν_k

**Combined single-step:**

  R_k(i) = [R_k(i-1)·(1−q_ik)/(1−q_ik·R_k(i-1))]·(1−ν_k) + ν_k

**Total weighted residual risk:**

  R_n = Σ_k w_k · R_k(n)

**Critical re-injection rate (verified across 12 numerical cases):**

  ν* = q · R   (break-even: above this, cycles do net harm)

**Terms:**
| Symbol | Meaning |
|--------|---------|
| R_k    | Residual risk for flaw class k (recursive) |
| q_ik   | Effective detection = d_ik · p_ik |
| p_ik   | Detection capability for class k |
| d_ik   | Diversity of approach (independence from prior passes) |
| ν_k    | Re-injection rate (fix introduces new flaw) |
| w_k    | Consequence weight for flaw class k |
| π_k    | Prior flaw rate (set once → vanishes from recursion) |

**Verified special cases (all confirmed SymPy + Wolfram):**
- ν=0 → original detection-only equation
- ν=1 → R_new = 1 (fix always re-injects)
- q=0, ν=0 → R unchanged (useless pass)
- q=1, ν=0 → R = 0 (perfect detection + clean fix)
- q=1, ν>0 → R = ν (re-injection is the floor)
- R=0, ν>0 → R = ν (fix creates risk from nothing)
- K=1, d=1, uniform p, π=0.5, ν=0 → standard Bayesian posterior C(n)

**Provenance:** Independently verified by Gemini 3.1 Pro and Codex GPT-5.4
(8 April 2026). Both confirmed core equation, both identified same boundary
(does not capture Ising Branch 2). Extensions: Codex proposed log-odds form,
Gemini proposed re-injection term ν. Both incorporated.


## The Problem: Blind Spots

The refined equation is a risk minimisation engine. Two structural blind spots
have been identified:

**Blind Spot A — Novelty is invisible.** If a model restates an existing finding
word-for-word, the equation treats it identically to a genuine novel discovery.
The diversity term d_ik partially captures this (repeated approaches lower d),
but d measures approach independence, not output novelty. A model can use a
different approach and produce the same finding — d is high but the finding
contributes nothing new.

**Blind Spot B — Solution quality is unmodelled.** The resolution phase (ν term)
asks only "did the fix re-inject a flaw?" It does not ask "was the fix actually
correct?" A model that detects a real flaw but proposes a wrong fix gets full
detection credit. The flaw persists but R decreases — the model's epistemic
state diverges from reality.


## Proposed Extension (CC1, verified SymPy + Wolfram, 9 April 2026)

Two new terms:

**Term 1 — Novelty coefficient η_ik ∈ [0,1]:**

Replace q_ik = d_ik · p_ik with:

  q_ik = η_ik · d_ik · p_ik

η measures whether the detection output is genuinely novel (η=1) or a complete
rehash of existing findings (η=0). This is the individual-model analog of ρ
(discovery efficiency, a system-level metric tracking novel/total findings).

η flows through the entire equation without structural change.

**Term 2 — Solution efficacy σ_ik ∈ [0,1]:**

Replace the resolution phase with:

  R_k(i) = σ_ik · [R_det · (1 − ν_k) + ν_k] + (1 − σ_ik) · R_k(i-1)

σ measures the probability that the proposed fix actually resolves the detected
flaw. When σ=1, the equation reduces to the refined form. When σ=0, the equation
reverts to R_k(i-1) — as if the cycle never happened. The detection gain was
real epistemically, but the fix failed, so the actual risk is unchanged.

**Combined extended equation:**

  q_ik = η_ik · d_ik · p_ik
  R_det = R_k(i-1) · (1 − q_ik) / (1 − q_ik · R_k(i-1))
  R_k(i) = σ_ik · [R_det · (1 − ν_k) + ν_k] + (1 − σ_ik) · R_k(i-1)

**Verified special cases (SymPy + Wolfram, all confirmed):**

| Condition | Result | Meaning |
|-----------|--------|---------|
| η=0, σ=0 | R unchanged | Rehash + no fix = wasted cycle |
| η=1, σ=1, ν=0 | R = R_det | Novel, perfect fix, clean → detection-only |
| η=1, σ=1, ν=1 | R = 1 | Fix always re-injects |
| η=1, σ=0 | R unchanged | Found something but fix is useless |
| η=0, σ=1, ν=0 | R unchanged | Rehash, fix applied but nothing to fix |
| q=1, σ=1, ν=0 | R = 0 | Perfect detect + perfect fix |
| σ=1 (any η,ν) | Reduces to refined equation | σ=1 is the baseline |

**Per-cycle gain (factored, verified SymPy + Wolfram):**

  ΔR_cycle = σ · (R − 1) · (R·q − ν) / (R·q − 1)

Sign analysis: since (R−1)<0 and (R·q−1)<0 for R,q ∈ (0,1):
  - ΔR > 0 iff R·q > ν  (beneficial)
  - ΔR < 0 iff R·q < ν  (divergent)
  - ΔR = 0 iff R·q = ν  (break-even)
  σ scales magnitude only — does NOT affect break-even point.

**Critical re-injection rate (PRESERVED):**

  ν* = q · R   (σ cancels — same as baseline!)

**Log-odds form:**
  Detection phase: logit(R_det) = logit(R) + log(1 − η·d·p) — additive, PRESERVED
  Resolution phase: breaks additive structure (same as baseline ν term)

**Protective property of low σ:**
  When a cycle is divergent (R·q < ν), low σ limits the damage.
  σ=0 in divergent territory → no damage at all (don't apply the bad fix).
  This captures the real-world insight: when unsure, detect-and-report without
  attempting resolution.

**Numerical verification (12 cases, SymPy and Wolfram agree to machine precision):**

| Label | R | q_eff | σ | ν | R_det | R_new | ΔR | ν* | Status |
|-------|-----|-------|-----|------|-------|-------|------|------|--------|
| Novel, good fix | 0.400 | 0.350 | 0.90 | 0.020 | 0.3023 | 0.3247 | +0.0753 | 0.1400 | BENEFICIAL |
| Rehash (η=0.1) | 0.400 | 0.035 | 0.90 | 0.020 | 0.3915 | 0.4033 | −0.0033 | 0.0140 | DIVERGENT |
| Good det, bad fix | 0.400 | 0.350 | 0.20 | 0.020 | 0.3023 | 0.3833 | +0.0167 | 0.1400 | BENEFICIAL |
| Divergent (σ=1) | 0.293 | 0.125 | 1.00 | 0.050 | 0.2661 | 0.3028 | −0.0098 | 0.0366 | DIVERGENT |
| Divergent (σ=0.3) | 0.293 | 0.125 | 0.30 | 0.050 | 0.2661 | 0.2959 | −0.0029 | 0.0366 | DIVERGENT |
| Baseline, no reinj | 0.400 | 0.350 | 1.00 | 0.000 | 0.3023 | 0.3023 | +0.0977 | 0.1400 | BENEFICIAL |
| Baseline, w/reinj | 0.400 | 0.350 | 1.00 | 0.020 | 0.3023 | 0.3163 | +0.0837 | 0.1400 | BENEFICIAL |
| No detect, no fix | 0.400 | 0.000 | 0.00 | 0.020 | 0.4000 | 0.4000 | 0.0000 | 0.0000 | BREAK-EVEN |
| Perfect detect+fix | 0.400 | 1.000 | 1.00 | 0.000 | 0.0000 | 0.0000 | +0.4000 | 0.4000 | BENEFICIAL |
| η=0.9, σ=0.85 | 0.400 | 0.315 | 0.85 | 0.020 | 0.3135 | 0.3381 | +0.0619 | 0.1260 | BENEFICIAL |
| η=0.5, σ=0.7 | 0.400 | 0.175 | 0.70 | 0.020 | 0.3548 | 0.3774 | +0.0226 | 0.0700 | BENEFICIAL |
| η=0.1, σ=0.2 | 0.400 | 0.035 | 0.20 | 0.020 | 0.3915 | 0.4007 | −0.0007 | 0.0140 | DIVERGENT |


## Your Task

1. **VERIFY** the proposed extension. Check the algebra independently. Confirm or
   deny that all stated special cases hold. Verify the factored gain formula and
   the preservation of ν* = q·R.

2. **FALSIFY** the extension. Try to break it. Look for:
   - Over-parameterisation (can η and σ be distinguished from each other and from d?)
   - Identifiability (can a model reliably estimate η and σ during self-assessment?)
   - Missing interactions (should η and σ interact with each other or with ν?)
   - Edge cases where the extension produces absurd results
   - Whether the extension actually solves the stated blind spots or merely
     papers over them with extra parameters

3. **ASSESS** completeness. Is the extended equation now a sufficient
   self-assessment tool for a model operating under CDSFL falsification? What
   remains unmodelled? Are there phenomena the equation should capture but doesn't?

4. **PROPOSE** improvements if you see genuine utility. Not changes for the sake
   of changes — only extensions that capture real phenomena that the current form
   misses, with mathematical proof that they work.

5. **P-PASS** your results up to 5 times or until diminishing returns. Each pass
   must genuinely attempt to break your previous conclusions. Only present
   conclusions that survive all passes.

Report your final assessment: is the extended equation internally consistent,
externally complete, and fit for purpose as the operational self-assessment
equation for CDSFL model-level metacognition?
"""


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def dispatch_gemini() -> dict:
    """Dispatch to Gemini 3.1 Pro."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    t0 = time.monotonic()
    try:
        text = call_gemini(
            model_id=GEMINI_MODEL,
            system_prompt=FOUR_LAYER_SYSTEM,
            user_prompt=USER_PROMPT,
            max_tokens=32768,
            timeout=600,
            max_retries=3,
        )
        elapsed = time.monotonic() - t0
        result = {
            "model": "Gemini 3.1 Pro",
            "model_id": GEMINI_MODEL,
            "timestamp": ts,
            "elapsed_s": round(elapsed, 1),
            "chars": len(text),
            "response": text,
            "status": "ok",
        }
    except Exception as e:
        elapsed = time.monotonic() - t0
        result = {
            "model": "Gemini 3.1 Pro",
            "model_id": GEMINI_MODEL,
            "timestamp": ts,
            "elapsed_s": round(elapsed, 1),
            "error": str(e),
            "status": "error",
        }
    # Save
    out_path = LOGS_DIR / f"novelty_ext_gemini_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    # Also save plain text
    if result["status"] == "ok":
        txt_path = LOGS_DIR / f"novelty_ext_gemini_{ts}.txt"
        with open(txt_path, "w") as f:
            f.write(result["response"])
    return result


def dispatch_cx() -> dict:
    """Dispatch to Codex GPT-5.4 via OpenRouter."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    t0 = time.monotonic()
    try:
        text = call_openrouter(
            model_id=CX_MODEL,
            system_prompt=FOUR_LAYER_SYSTEM,
            user_prompt=USER_PROMPT,
            max_tokens=32768,
            timeout=600,
            max_retries=3,
        )
        elapsed = time.monotonic() - t0
        result = {
            "model": "Codex GPT-5.4",
            "model_id": CX_MODEL,
            "timestamp": ts,
            "elapsed_s": round(elapsed, 1),
            "chars": len(text),
            "response": text,
            "status": "ok",
        }
    except Exception as e:
        elapsed = time.monotonic() - t0
        result = {
            "model": "Codex GPT-5.4",
            "model_id": CX_MODEL,
            "timestamp": ts,
            "elapsed_s": round(elapsed, 1),
            "error": str(e),
            "status": "error",
        }
    # Save
    out_path = LOGS_DIR / f"novelty_ext_cx_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    # Also save plain text
    if result["status"] == "ok":
        txt_path = LOGS_DIR / f"novelty_ext_cx_{ts}.txt"
        with open(txt_path, "w") as f:
            f.write(result["response"])
    return result


def main():
    print(f"CDSFL Confer: Novelty Extension — {datetime.now().isoformat()}")
    print(f"System prompt: {len(FOUR_LAYER_SYSTEM)} chars")
    print(f"User prompt: {len(USER_PROMPT)} chars")
    print(f"Logs: {LOGS_DIR}")
    print()

    # Dispatch concurrently
    results = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(dispatch_gemini): "Gemini",
            pool.submit(dispatch_cx): "CX",
        }
        for future in as_completed(futures):
            label = futures[future]
            try:
                result = future.result()
                results[label] = result
                status = result["status"]
                if status == "ok":
                    print(f"  [{label}] OK — {result['elapsed_s']}s, {result['chars']} chars")
                else:
                    print(f"  [{label}] ERROR — {result.get('error', 'unknown')[:100]}")
            except Exception as e:
                print(f"  [{label}] EXCEPTION — {str(e)[:100]}")
                results[label] = {"status": "exception", "error": str(e)}

    print()
    print("Done. Logs saved to:", LOGS_DIR)
    return results


if __name__ == "__main__":
    main()
