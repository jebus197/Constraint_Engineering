#!/usr/bin/env python3
"""
Confer: S_k Solution Reliability Extension + Exp 38 Design
===========================================================
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

# Load .env (handles 'export KEY=val' format)
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_solution_reliability"
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
# User Prompt
# ---------------------------------------------------------------------------

USER_PROMPT = """
# Context: S_k Solution Reliability Extension + Experiment 38 Design

## Background — Experiment 37 Results (9 April 2026)

The CDSFL framework just completed its most successful experiment. Five frontier
AI models (Claude/CC2, ChatGPT/GPT-5.4, Codex/GPT-5.4, DeepSeek Reasoner,
Gemini 3.1 Pro) collaboratively reviewed `evidence.py` under structured
Popperian falsification.

**Key results:**
- 16 rounds, 22 minutes, 222 canonical findings, 81 confirmed (36%)
- γ final = 0.467 (strong depletion, textbook Duane curve)
- ALL 5 models computed R_k self-assessment equation numerically, quality 7/7
- R_k adoption: 0% in Exp 36 → ~100% in Exp 37
- 2.9× canonical yield/round, 18× confirmation rate vs Exp 36
- Converged with 2 consecutive passes at the stricter bar (before reduction to 1)

**Critical gap identified:** The system excels at FINDING problems but has a
vestigial solution pipeline. In R14-R15, the CC2v Fix Extractor extracted 6
fixes total. 1 was applied successfully. 5 failed. Fixes are proposed in natural
language, then an agent tries to convert them to code. This is backwards.

The constraint box principle states: "The tool output IS the evidence. LLM
reasoning selects and interprets tool output — it does not substitute for it."
This applies to findings. It does NOT currently apply to fixes.

## The Current Mathematical Model (verified SymPy + Wolfram + z3)

**Detection phase:**
  q_ik = η_ik · d_ik · p_ik
  R_det = R_k(i-1) · (1 − q_ik) / (1 − q_ik · R_k(i-1))

**Resolution phase:**
  R_k(i) = σ_ik · [R_det · (1 − ν_k) + ν_k] + (1 − σ_ik) · R_k(i-1)

**Problem:** σ (solution efficacy) is model-estimated, not tool-verified. The
model assesses its own fix quality. This violates the constraint box principle.

## Proposed Extension: S_k (Solution Reliability)

**Core idea:** σ should be DERIVED from tool verification, not model-estimated.

**S_k — Tool-verified solution reliability:**
  S_k(i) = Π_j v_j(i)

where v_j are tool gate scores, each ∈ [0,1]:
  v_1 = parse_valid (does the fix parse/compile? Tool: AST, SymPy parse)
  v_2 = test_pass_rate (tests pass after fix? Tool: pytest, dim analysis)
  v_3 = target_resolved (finding-specific test confirms fix? Tool: targeted test)
  v_4 = regression_free (no new failures? Tool: full regression suite)

**Bridge to R_k:**
  σ_ik = S_k(i)  (σ becomes tool-derived)

**Extended re-injection (bad fixes inject more risk):**
  ν_eff(i) = ν_base + (1 − S_k(i)) · ν_fail

**Combined extended equation:**
  q_ik = η_ik · d_ik · p_ik
  R_det = R_k(i-1) · (1 − q_ik) / (1 − q_ik · R_k(i-1))
  S_k(i) = Π_j v_j(i)
  ν_eff(i) = ν_base + (1 − S_k(i)) · ν_fail
  R_k(i) = S_k(i) · [R_det · (1 − ν_eff) + ν_eff] + (1 − S_k(i)) · R_k(i-1)

**Verified special cases (SymPy + z3 + Wolfram, ALL confirmed):**

| Condition | Result | Meaning |
|-----------|--------|---------|
| S=0 | R unchanged | No fix → detection-only |
| S=1, ν_f=0 | Refined equation | Reduces to original |
| q=1, S=1, ν=0 | R = 0 | Perfect detect + perfect fix |
| S=1, ν_b=1 | R = 1 | Fix always re-injects |
| q=0, S=1, ν=0 | R unchanged | No detection |
| η=0, S=0 | R unchanged | Rehash + no fix |

**Break-even S*:** S* = (ν_b + ν_f − q·R) / ν_f
  When S < S*, applying the fix does more harm than good.
  When ν_f = 0, S* ≤ 0 — any fix helps (original behaviour).

**ν* preserved:** ν* = q·R (unchanged from original equation at S=1).

**z3 formal properties (all verified):**
  1. R_new ∈ [0, 1] for all valid inputs ✓
  2. S=0 → R_new = R (identity) ✓
  3. S=1, ν_f=0 → reduces to refined equation ✓
  4. Higher S → lower R when detection helps ✓

**Wolfram cross-validation:**
  S* = (nb + nf − q·r) / nf ✓ (matches SymPy)
  ν* = q·r ✓ (preserved)
  dR/ds = ((r−1)·(nb + nf − q·r − 2·nf·s)) / (q·r − 1) ✓

## Your Task

You are being asked to:

1. **FALSIFY the proposed S_k extension.** Find what is wrong with it. Does it
   introduce any inconsistency? Does it break any verified property of the
   existing R_k model? Are the special cases complete? Is the product-of-gates
   form for S_k correct, or is there a better mathematical structure?

2. **PROPOSE the optimal form** for solution reliability measurement within the
   CDSFL framework. If S_k as proposed is correct, confirm it. If it needs
   modification, provide the modified form with proof. If it should be replaced
   entirely, propose the replacement with full derivation.

3. **ADDRESS THE FIX PIPELINE:** How should fixes be extracted from models in a
   tool-verified way? The current approach (natural language → agent conversion)
   fails 83% of the time. The models have access to: AST, pytest, ruff, mypy,
   bandit, SymPy, z3, NumPy, SciPy. How should fixes be structured so they are
   tool-verifiable from the start?

4. **DESIGN EXPERIMENT 38:** Given this extension, how should Experiment 38 be
   structured to test the complete finding-AND-solution pipeline? What should the
   target be? What convergence criteria should include solution quality? How do
   we measure whether the S_k extension improves outcomes?

5. **GENERALISATION:** The CDSFL framework aims to be a general-purpose STEM
   analysis tool, not just a code reviewer. Expert encodings for different
   domains (mathematics, physics, chemistry, engineering) are planned for
   Bench Run 2 (27 tasks). How does S_k generalise? In mathematics, a "fix"
   is a corrected proof step (SymPy-verifiable). In physics, it might be a
   dimensional correction. In chemistry, stoichiometric balance. What is the
   minimal interface between domain-specific verification and the S_k framework?

6. **DISTRIBUTED COMPUTE:** How does the model behave with more models (10, 20)?
   Different topologies (relay, mesh vs star)? Does R_k or S_k need modification?

Apply FFAFP to ALL proposals. P-pass up to 5 times. Only present survivors.
"""

# ---------------------------------------------------------------------------
# Dispatch Functions
# ---------------------------------------------------------------------------

def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def dispatch_gemini(system: str, user: str) -> dict:
    """Call Gemini 3.1 Pro via Google GenAI API."""
    ts = _ts()
    print(f"[{ts}] Dispatching to Gemini 3.1 Pro...", flush=True)
    t0 = time.monotonic()
    try:
        response = call_gemini(
            model_id=GEMINI_MODEL,
            system_prompt=system,
            user_prompt=user,
        )
        elapsed = time.monotonic() - t0
        result = {
            "model": "Gemini",
            "model_id": GEMINI_MODEL,
            "timestamp": ts,
            "elapsed_s": round(elapsed, 1),
            "response": response,
            "response_length": len(response),
        }
        # Save
        out_path = LOGS_DIR / f"solution_reliability_gemini_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        # Also save raw text
        txt_path = LOGS_DIR / f"solution_reliability_gemini_{ts}.txt"
        txt_path.write_text(response, encoding="utf-8")
        print(f"[{_ts()}] Gemini done ({elapsed:.0f}s, {len(response)} chars)")
        return result
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"[{_ts()}] Gemini FAILED after {elapsed:.0f}s: {e}")
        return {"model": "Gemini", "error": str(e), "elapsed_s": round(elapsed, 1)}


def dispatch_codex(system: str, user: str) -> dict:
    """Call Codex GPT-5.4 via OpenRouter API."""
    ts = _ts()
    print(f"[{ts}] Dispatching to Codex GPT-5.4...", flush=True)
    t0 = time.monotonic()
    try:
        response = call_openrouter(
            model_id=CX_MODEL,
            system_prompt=system,
            user_prompt=user,
        )
        elapsed = time.monotonic() - t0
        result = {
            "model": "Codex",
            "model_id": CX_MODEL,
            "timestamp": ts,
            "elapsed_s": round(elapsed, 1),
            "response": response,
            "response_length": len(response),
        }
        out_path = LOGS_DIR / f"solution_reliability_cx_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"solution_reliability_cx_{ts}.txt"
        txt_path.write_text(response, encoding="utf-8")
        print(f"[{_ts()}] Codex done ({elapsed:.0f}s, {len(response)} chars)")
        return result
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"[{_ts()}] Codex FAILED after {elapsed:.0f}s: {e}")
        return {"model": "Codex", "error": str(e), "elapsed_s": round(elapsed, 1)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("CDSFL Confer: S_k Solution Reliability Extension")
    print(f"Started: {_ts()}")
    print("Models: Gemini 3.1 Pro, Codex GPT-5.4")
    print("Protocol: 4-layer (Meta + CDSFL + FFAFP + Conversational)")
    print("=" * 60)
    print()

    # Dispatch both in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(dispatch_gemini, FOUR_LAYER_SYSTEM, USER_PROMPT): "Gemini",
            pool.submit(dispatch_codex, FOUR_LAYER_SYSTEM, USER_PROMPT): "Codex",
        }
        for future in as_completed(futures):
            label = futures[future]
            try:
                results[label] = future.result()
            except Exception as e:
                print(f"[{_ts()}] {label} exception: {e}")
                results[label] = {"model": label, "error": str(e)}

    # Summary
    print()
    print("=" * 60)
    print("CONFER COMPLETE")
    print("=" * 60)
    for label, r in results.items():
        if "error" in r:
            print(f"  {label}: FAILED — {r['error']}")
        else:
            print(f"  {label}: {r['response_length']} chars, {r['elapsed_s']}s")
    print(f"\nLogs: {LOGS_DIR}")


if __name__ == "__main__":
    main()
