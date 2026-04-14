#!/usr/bin/env python3
"""
Confer Round 2: Two-Dimensional (ν_k, c_ext) Stage 6 Review
============================================================
Second confer round after the founder's two-dimensional redesign.
Reviews the revised mathematical model where ν_k and c_ext are
independent dimensions (never collapsed), H/H_max is context only,
and shadow calibration hooks collect per-finding triples.

Date: 14 April 2026
Protocol: CDSFL + FFAFP
Previous: confer_stage6_model.py (Round 1, 7 corrections applied)
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_stage6_r2"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

APPENDIX_PATH = REPO_ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
APPENDIX_TEXT = APPENDIX_PATH.read_text(encoding="utf-8")

SHADOW_STAGE6_PATH = REPO_ROOT / "bench" / "dm" / "_shadow_stage6.py"
SHADOW_STAGE6_CODE = SHADOW_STAGE6_PATH.read_text(encoding="utf-8")

# Extract revised sections
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


# Primary review targets: the revised Stage 5->6 derivation and all Stage 6 sections
SECTION_11 = extract_section(lines, "### Literature-Calibrated Extension (Stage 5", "## 1.2 FFAFP", max_lines=120)
SECTION_16 = extract_section(lines, "## 1.6 Literature Novelty", "## 1.7 Source Diversity", max_lines=80)
SECTION_17 = extract_section(lines, "## 1.7 Source Diversity", "## 1.8 E-value", max_lines=80)
SECTION_18 = extract_section(lines, "## 1.8 E-value Verification", "## 7.13 Convergence", max_lines=100)
SECTION_LINEAGE = extract_section(lines, "## Intellectual Lineage", "## Attribution", max_lines=80)
SECTION_NOTATION = extract_section(lines, "## Notation Summary", "## Intellectual Lineage", max_lines=80)

REVIEW_SECTIONS = f"""
=== §1.1 STAGE 5 -> 6 DERIVATION (REVISED: two-dimensional) ===

{SECTION_11}

---

=== §1.6 LITERATURE NOVELTY SCORE ===

{SECTION_16}

---

=== §1.7 SOURCE DIVERSITY AND CORROBORATION ===

{SECTION_17}

---

=== §1.8 E-VALUE VERIFICATION GATE ===

{SECTION_18}

---

=== NOTATION SUMMARY (new symbols) ===

{SECTION_NOTATION}

---

=== INTELLECTUAL LINEAGE ===

{SECTION_LINEAGE}
"""

# ---------------------------------------------------------------------------
# Confer prompt — focused on the two-dimensional revision
# ---------------------------------------------------------------------------

CONFER_PROMPT = f"""## Task

You are reviewing the REVISED Stage 6 extension to the CDSFL mathematical model.
This is the SECOND confer round. The first round (Gemini + Codex) produced 7
corrections (3 HARD, 4 SOFT), all applied and SymPy-verified. The critical change
since Round 1: the founder rejected collapsing nu_k and c_ext into a single score
via abstraction adjustment and demanded two-dimensional reporting.

Your task: apply FFAFP to the REVISED design as an integrated system, focusing on
the two-dimensional (nu_k, c_ext) architecture and the shadow calibration approach.

## What Changed Since Round 1

### HARD change: Abstraction collapse removed

Round 1 included: `confidence = c_ext + beta_abs * (1 - c_ext) * (H / H_max)`
with beta_abs = 0.5 cap. The founder challenged this:

> "That's 50% confidence that an abstraction/principle is genuinely novel with
> no verified sources and no diversity confirmation? How do you justify that?"

Then refined to: "We can maintain two scores. A high novelty rating + a low
corroboration rating. Just as OSF is full of 'highly novel' content with low
scores in terms of formal corroboration, this observation can also be formalised."

### Resolution: Two-dimensional novelty reporting

nu_k and c_ext are now independent dimensions, never collapsed. H/H_max is
reported alongside as context (explains WHY c_ext might be low) but does not
modify either score.

Per-finding novelty report: (nu_k, c_ext, H/H_max) — three independent views.

| nu_k | c_ext | Quadrant         | Interpretation |
|------|-------|------------------|----------------|
| High | High  | Verified novel   | Genuinely new, well-evidenced |
| High | Low   | Unverified novel | Appears new, search was weak |
| Low  | High  | Verified known   | Confirmed rediscovery |
| Low  | Low   | Unverified known | Least informative |

The eta decomposition is unchanged: eta_combined = eta_int * (1 - c_ext * (1 - nu_k)).
The two-dimensional reporting is about PRESENTATION and DECISION-MAKING, not the
state equation.

### Shadow calibration hooks for Exp 39

A ShadowStage6Calibrator has been implemented and hooked into the experiment runner.
It collects per-finding (nu_k_proxy, c_ext, H_ratio) triples, per-source coverage
(c_s = r_s * q_s * a_s), per-tool FPR tracking, and shadow eta_combined deltas.
All observation-only, zero pipeline effect.

## Existing Model Context

The existing model (Stages 1-5) provides recursive Bayesian risk estimation:

  R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))

with three-phase extension (Stage 5):
  Phase 1: q = eta * d * p  (detection with novelty)
  Phase 2: R_base = sigma * R_det + (1 - sigma) * R_old  (fix efficacy)
  Phase 3: R_k(i) = R_base * (1 - nu) + nu  (re-injection)

Stage 6 decomposes eta into (eta_int, nu_k, c_ext) and adds literature calibration.

## SymPy Verification Results (Two-Dimensional Formulation)

All boundary conditions verified:
- nu_k=1 -> eta_int (novel finding, no penalty)
- nu_k=0, c_ext=1 -> 0 (known result, full coverage)
- nu_k=0, c_ext=0 -> eta_int (no search, degrade to Stage 5)
- c_ext=0 -> eta_int (graceful degradation)

Quadrant ordering (numerical, R=0.3, d=0.9, p=0.85, eta_int=0.9):
- Verified novel (nu_k=0.85, c_ext=0.679): R = 0.141
- Unverified novel (nu_k=0.85, c_ext=0.1): R = 0.119 (closer to Stage 5)
- Verified known (nu_k=0.2, c_ext=0.679): R = 0.219
- Unverified known (nu_k=0.2, c_ext=0.1): R = 0.123

## Revised Mathematical Appendix Sections

{REVIEW_SECTIONS}

## Shadow Stage 6 Calibrator Code

```python
{SHADOW_STAGE6_CODE}
```

## Questions for FFAFP Review

Focus on the TWO-DIMENSIONAL ARCHITECTURE and SHADOW CALIBRATION:

1. **FIND:** Does the two-dimensional (nu_k, c_ext) reporting introduce any
   mathematical risks? Are the quadrant boundaries well-defined? Are there
   edge cases in the shadow calibrator?

2. **FOLLOW:** How does the decision NOT to collapse the dimensions interact
   with the eta decomposition? The eta formula still collapses them
   (eta_combined = eta_int * (1 - c_ext * (1 - nu_k))). Is there tension
   between "report independently" and "combine in the state equation"?

3. **ANALYSE:**
   a. Is the two-dimensional reporting a genuine improvement over the
      beta_abs collapse? What information is preserved? What is lost?
   b. Is the OSF analogy (highly novel + low corroboration is a meaningful
      state) mathematically sound? Does the eta formula handle it correctly?
   c. Does "abstraction as context, not adjustment" leave any gap in the
      model? Prior design used abstraction to boost confidence — removing
      it means high-abstraction findings with low c_ext get no special
      treatment. Is this the right call?
   d. Is the shadow calibrator design sound? Are the proxy estimates
      (nu_k from result counts, c_ext from source metadata) reasonable
      for calibration purposes?
   e. Are the per-source c_s = r_s * q_s * a_s estimates and the
      gamma_src = 0.7 discount well-justified?
   f. Does the E-value gate (section 1.8) interact correctly with the
      two-dimensional reporting? Are there edge cases?

4. **FIX:** Propose corrections for any issues found. Classify as HARD
   (mathematical error, violated bound, incorrect reduction) or SOFT
   (calibration, presentation, completeness).

5. **P-PASS:** Falsify the integrated two-dimensional + shadow calibration
   design. Under what conditions does the two-dimensional approach give
   WORSE outcomes than the collapsed approach? Is there a case where
   preserving both dimensions misleads rather than informs?

## Format

Structure your response as:
- FIND section (numbered findings)
- FOLLOW section (interaction analysis)
- ANALYSE section (answers to a-f above)
- FIX section (specific corrections, HARD/SOFT classified)
- P-PASS section (falsification attempts with outcomes)

Be concrete. Reference specific equations and boundary conditions.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'='*72}")
    print(f"  CONFER R2: Two-Dimensional Stage 6 Review — {ts}")
    print(f"  Protocol: CDSFL + FFAFP")
    print(f"  Models: Codex GPT-5.4 (cx), Gemini 3.1 Pro (ge)")
    print(f"  Focus: (nu_k, c_ext) independence + shadow calibration")
    print(f"{'='*72}\n")

    results = {}

    # --- Codex first (cx before ge in the user's request) ---
    print("Dispatching to Codex GPT-5.4 (cx)...")
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

    # Save Codex result immediately
    cx_log = LOGS_DIR / f"codex_{ts}.json"
    cx_log.write_text(json.dumps(results.get("codex", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved: {cx_log}")

    # --- Gemini ---
    print("\nDispatching to Gemini 3.1 Pro (ge)...")
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
        t0b = time.monotonic()
        try:
            ge_response = call_openrouter(
                model_id="google/gemini-3.1-pro",
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=300,
                max_retries=3,
            )
            ge_time2 = time.monotonic() - t0b
            print(f"  Gemini (OpenRouter) responded in {ge_time2:.1f}s ({len(ge_response)} chars)")
            results["gemini"] = {
                "model": "google/gemini-3.1-pro (via OpenRouter)",
                "response": ge_response,
                "time_s": round(ge_time + ge_time2, 1),
                "chars": len(ge_response),
            }
        except Exception as e2:
            ge_time2 = time.monotonic() - t0b
            print(f"  Gemini (OpenRouter) also FAILED: {e2}")
            results["gemini"] = {"error": str(e2), "time_s": round(ge_time + ge_time2, 1)}

    # Save Gemini result
    ge_log = LOGS_DIR / f"gemini_{ts}.json"
    ge_log.write_text(json.dumps(results.get("gemini", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved: {ge_log}")

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
