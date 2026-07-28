#!/usr/bin/env python3
"""
Confer: Stage 6 Literature-Calibrated Extension Review
=======================================================
Dispatches to Gemini 3.1 Pro and Codex GPT-5.4 SEQUENTIALLY under
full CDSFL + FFAFP protocol. Reviews the Stage 6 mathematical model
extension incorporating literature novelty (nu_k), source diversity
(c_ext), e-value verification gates, Holland/Jerne lineage, and
frequency-scaled confidence.

Date: 14 April 2026
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_stage6_model"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Mathematical appendix — the primary review target
APPENDIX_PATH = REPO_ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
APPENDIX_TEXT = APPENDIX_PATH.read_text(encoding="utf-8")

# Nu_k design notes
NUK_DESIGN_PATH = REPO_ROOT / "experimental_notes" / "Novelty_Scoring_nu_k_Design_2026-04-14.md"
NUK_TEXT = NUK_DESIGN_PATH.read_text(encoding="utf-8")

# Holland/Kohonen assessment
HOLLAND_PATH = REPO_ROOT / "experimental_notes" / "Holland_Kohonen_AIS_Assessment_2026-04-12.md"
HOLLAND_TEXT = HOLLAND_PATH.read_text(encoding="utf-8")

# Extract only the new/modified sections for focused review
# §1.1 model evolution + Stage 5→6 derivation (~lines 153-315)
# §1.4 continuous suppression (with Holland/Jerne update)
# §1.5 persistent memory (with frequency-scaled confidence)
# §1.6 literature novelty
# §1.7 source diversity
# §1.8 e-value gate
# Intellectual lineage
lines = APPENDIX_TEXT.splitlines()


def extract_section(lines, start_heading, end_heading=None, max_lines=200):
    """Extract a section from start_heading to end_heading (exclusive)."""
    start_idx = None
    for i, line in enumerate(lines):
        if start_heading in line:
            start_idx = i
            break
    if start_idx is None:
        return f"[Section '{start_heading}' not found]"
    if end_heading:
        end_idx = None
        for i, line in enumerate(lines[start_idx + 1:], start_idx + 1):
            if end_heading in line:
                end_idx = i
                break
        if end_idx is None:
            end_idx = min(start_idx + max_lines, len(lines))
    else:
        end_idx = min(start_idx + max_lines, len(lines))
    return "\n".join(lines[start_idx:end_idx])


SECTION_11 = extract_section(lines, "## 1.1 Unified Self-Assessment Equation", "## 1.2 FFAFP", max_lines=200)
SECTION_14 = extract_section(lines, "## 1.4 Continuous Suppression", "## 1.5 Persistent Memory", max_lines=80)
SECTION_15 = extract_section(lines, "## 1.5 Persistent Memory", "## 1.6 Literature Novelty", max_lines=120)
SECTION_16 = extract_section(lines, "## 1.6 Literature Novelty", "## 1.7 Source Diversity", max_lines=80)
SECTION_17 = extract_section(lines, "## 1.7 Source Diversity", "## 1.8 E-value", max_lines=80)
SECTION_18 = extract_section(lines, "## 1.8 E-value Verification", "## 7.13 Convergence", max_lines=80)
SECTION_LINEAGE = extract_section(lines, "## Intellectual Lineage", "## Attribution", max_lines=80)

REVIEW_SECTIONS = f"""
{SECTION_11}

---

{SECTION_14}

---

{SECTION_15}

---

{SECTION_16}

---

{SECTION_17}

---

{SECTION_18}

---

{SECTION_LINEAGE}
"""

# ---------------------------------------------------------------------------
# Confer prompt
# ---------------------------------------------------------------------------

CONFER_PROMPT = f"""## Task

You are reviewing a proposed Stage 6 extension to the CDSFL mathematical model.
This is a literature-calibrated extension that adds three new mechanisms to the
existing recursive Bayesian self-assessment equation R_k(i). Your task is to
apply FFAFP (Find, Follow, Analyse, Fix, P-pass) to the complete extension
as an integrated system.

## Background

The existing model (Stages 1-5) provides recursive Bayesian risk estimation:

  R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))

with three-phase extension (Stage 5):
  Phase 1: q = eta * d * p  (detection with novelty)
  Phase 2: R_base = sigma * R_det + (1 - sigma) * R_old  (fix efficacy)
  Phase 3: R_k(i) = R_base * (1 - nu) + nu  (re-injection)

Stage 6 was prompted by Hossenfelder (2026) demonstrating that AI "novelty"
claims are often rediscoveries of published work. It decomposes eta into
internal and external components and adds literature calibration.

## Stage 6 Extension Summary

1. **eta decomposition:**
   eta_combined = eta_int * (1 - c_ext * (1 - nu_k))

   where eta_int = within-session novelty (existing),
   nu_k = literature novelty (new, from O1 cell),
   c_ext = source diversity confidence (new).

2. **Source diversity corroboration:**
   c_ext = 1 - prod_s(1 - c_s)

   Isomorphic with Stage 1 C(n). Multiple literature sources compound
   like multiple reviewers.

3. **Abstraction-adjusted confidence:**
   confidence = c_ext + (1 - c_ext) * (H / H_max)

   Uses existing Abstraction Index H(x) from section 7.2. High-abstraction
   findings get full novelty credit even with incomplete search.

4. **Frequency-scaled detection confidence:**
   c_freq(k) = c_base(k) * (1 + alpha_freq * log(1 + N_k))

   Historical encounter counts boost detection confidence (Holland CAS).

5. **E-value verification gate:**
   E_combined = prod(e_i), reject H_0 when E_combined > 1/alpha

   Replaces binary pass/fail in S_k gate (Stanford POPPER framework).

6. **Holland/Jerne lineage:** Continuous suppression (section 1.4) now
   explicitly attributed to Jerne idiotypic networks and Holland CAS.

## SymPy + Wolfram Verification Results

All the following have been computationally verified:

- eta_combined boundary conditions: nu_k=1 -> eta_int, nu_k=0/c=1 -> 0,
  c=0 -> eta_int (graceful degradation)
- Monotonicity: d(eta)/d(nu_k) > 0, d(eta)/d(c_ext) < 0 when nu_k < 1
- c_ext boundary conditions: all sources zero -> 0, any source perfect -> 1
- Abstraction confidence: H=H_max -> 1, c=1 -> 1, H=0/c=0 -> 0
- Suppression weight: w in [w_floor, 1], negative derivative in similarity
- Frequency-scaled: concave, diminishing returns, c_freq(N=0) = c_base
- E-value composition: multiplicative, inconclusive (e=1) has no effect
- Stage 6 integration: R_known(0.250) > R_partial(0.141) > R_novel(0.118) = R_Stage5

## Sections Under Review

The following are the new and modified sections of the Mathematical Appendix:

{REVIEW_SECTIONS}

## Nu_k Design Notes (for context)

{NUK_TEXT[:4000]}

## Holland/Kohonen Assessment (for context)

{HOLLAND_TEXT[:4000]}

## Questions for FFAFP Review

For each new mechanism and the overall composition, apply FFAFP:

1. **FIND:** What mathematical or engineering risks does Stage 6 introduce?
   Are there boundary conditions not tested? Are the reduction properties
   complete?

2. **FOLLOW:** How do nu_k, c_ext, abstraction adjustment, frequency-scaled
   confidence, and e-values interact as a composed system? Are there emergent
   risks from composition?

3. **ANALYSE:**
   a. Is the eta decomposition mathematically sound? Does it introduce
      any violation of the [0,1] bounds on q?
   b. Is c_ext genuinely isomorphic with C(n)? Does the analogy hold
      under the assumption violations (source correlation)?
   c. Is the abstraction adjustment well-motivated, or does it create
      a backdoor for inflating novelty scores?
   d. Does frequency-scaled confidence interact correctly with FFAFP's
      d_tool requirement?
   e. Are e-values correctly applied? Is the mapping from tool outputs
      to e-values well-defined enough?
   f. Is the Intellectual Lineage section accurate? Are any claims
      about prior work overstated or understated?

4. **FIX:** Propose corrections for any issues found. Be specific about
   what should change and why.

5. **P-PASS:** Falsify the integrated Stage 6 model. Under what conditions
   does it perform WORSE than Stage 5? Are there parameter regimes where
   the extension is actively harmful?

## Format

Structure your response as:
- FIND section (numbered findings)
- FOLLOW section (interaction analysis)
- ANALYSE section (answers to a-f above)
- FIX section (specific corrections with rationale)
- P-PASS section (falsification attempts with outcomes)

Be concrete. Reference specific equations, boundary conditions, and sections.
If the extension is flawed, say so and explain why. If it is sound, confirm
which properties you verified and how.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'='*72}")
    print(f"  CONFER: Stage 6 Literature-Calibrated Extension Review — {ts}")
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
                model_id="google/gemini-3.1-pro",
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=300,
                max_retries=3,
            )
            ge_time = time.monotonic() - t0
            print(f"  Gemini (OpenRouter) responded in {ge_time:.1f}s ({len(ge_response)} chars)")
            results["gemini"] = {
                "model": "google/gemini-3.1-pro (via OpenRouter)",
                "response": ge_response,
                "time_s": round(ge_time, 1),
                "chars": len(ge_response),
            }
        except Exception as e2:
            ge_time2 = time.monotonic() - t0
            print(f"  Gemini (OpenRouter) also FAILED: {e2}")
            results["gemini"] = {"error": str(e2), "time_s": round(ge_time + ge_time2, 1)}

    # Save Gemini result immediately
    ge_log = LOGS_DIR / f"gemini_{ts}.json"
    ge_log.write_text(json.dumps(results.get("gemini", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved: {ge_log}")

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
            max_retries=5,
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
        results["codex"] = {"error": str(e), "time_s": round(cx_time, 1)}

    # Save Codex result
    cx_log = LOGS_DIR / f"codex_{ts}.json"
    cx_log.write_text(json.dumps(results.get("codex", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved: {cx_log}")

    # --- Combined log ---
    combined_log = LOGS_DIR / f"combined_{ts}.json"
    combined_log.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Combined log: {combined_log}")

    # --- Print summaries ---
    for model_name, model_result in results.items():
        print(f"\n{'='*72}")
        print(f"  {model_name.upper()} RESPONSE ({model_result.get('time_s', '?')}s)")
        print(f"{'='*72}")
        resp = model_result.get("response", model_result.get("error", "No response"))
        print(resp[:8000] if len(resp) > 8000 else resp)
        if len(resp) > 8000:
            print(f"\n  ... [{len(resp) - 8000} chars truncated, see full log] ...")

    return results


if __name__ == "__main__":
    run_confer()
