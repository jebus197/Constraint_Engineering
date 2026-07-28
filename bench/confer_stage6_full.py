#!/usr/bin/env python3
"""
Full 5-Model Confer: Literature-Calibrated Extension + Shadow Calibrator
========================================================================
All five panel models review the complete revised mathematical model and
shadow calibrator with all instrumentation (E-values, c_freq, epistemic
marking, d_eff coupling, source co-occurrence).

Date: 14 April 2026
Protocol: CDSFL + FFAFP
Models: Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Claude Opus 4.6),
        ChatGPT GPT-5.4, DeepSeek R1-0528
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    call_openrouter, call_gemini, call_claude_cli, call_deepseek,
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
            os.environ.setdefault(_k, _v)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_stage6_full"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("gemini",  "gemini-3.1-pro-preview", "gemini_native"),
    ("codex",   "openai/gpt-5.4",         "openrouter"),
    ("cc2",     "opus",                    "claude_cli"),
    ("chatgpt", "openai/gpt-5.4",         "openrouter"),
    ("deepseek","deepseek/deepseek-r1-0528","openrouter"),
]

# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

APPENDIX_PATH = REPO_ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"
APPENDIX_TEXT = APPENDIX_PATH.read_text(encoding="utf-8")

SHADOW_CODE = (REPO_ROOT / "bench" / "dm" / "_shadow_stage6.py").read_text(encoding="utf-8")

# Extract key sections
lines = APPENDIX_TEXT.splitlines()


def extract_section(lines, start_heading, end_heading=None, max_lines=200):
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


SEC_STAGE6 = extract_section(lines, "### Literature-Calibrated Extension (Stage 5", "## 1.2 FFAFP", max_lines=120)
SEC_16 = extract_section(lines, "## 1.6 Literature Novelty", "## 1.7 Source Diversity", max_lines=80)
SEC_17 = extract_section(lines, "## 1.7 Source Diversity", "## 1.8 E-value", max_lines=80)
SEC_18 = extract_section(lines, "## 1.8 E-value Verification", "## 7.13 Convergence", max_lines=100)
SEC_14 = extract_section(lines, "## 1.4 Continuous Suppression", "## 1.5 Persistent Memory", max_lines=80)
SEC_15 = extract_section(lines, "## 1.5 Persistent Memory", "## 1.6 Literature Novelty", max_lines=120)

# ---------------------------------------------------------------------------
# Confer prompt
# ---------------------------------------------------------------------------

CONFER_PROMPT = f"""## Task

You are reviewing the complete literature-calibrated extension to the CDSFL
mathematical model and its shadow calibration instrumentation. This is a full
FFAFP review of the integrated system.

Two prior confer rounds (Gemini + Codex) produced 12 corrections (10 HARD,
2 SOFT), all applied and verified. This round reviews the COMPLETE system
including 5 new shadow instrumentation features added after those rounds.

## System Overview

The CDSFL self-assessment equation R_k(i) uses recursive Bayesian updates:

  R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))

with three-phase extension:
  Phase 1: q = eta * d * p  (detection with novelty)
  Phase 2: R_base = sigma * R_det + (1 - sigma) * R_old  (fix efficacy)
  Phase 3: R_k(i) = R_base * (1 - nu) + nu  (re-injection)

The literature-calibrated extension decomposes eta into:

  eta_combined = eta_int * (1 - c_ext * (1 - nu_k))

where nu_k (literature novelty) and c_ext (search corroboration) are
DISTINCT reporting dimensions, never collapsed into a single score.
Per-finding report: (nu_k, c_ext, H/H_max) — three views.
H/H_max is context only (explains why c_ext might be low), does NOT
modify either score.

## What Is Under Review

### 1. Mathematical model (appendix sections)

{SEC_STAGE6}

---

{SEC_16}

---

{SEC_17}

---

{SEC_18}

---

{SEC_14}

---

{SEC_15}

### 2. Shadow calibrator (complete implementation)

This code runs observation-only alongside each experiment round,
collecting calibration data for all extension parameters. Zero
pipeline effect. All 5 new shadow features are included:

```python
{SHADOW_CODE}
```

### 3. Shadow features under review

a. **E-value shadow computation**: Uses cumulative fail_fraction as FPR
   proxy. Per-tool e = 1/fail_fraction on PASS, 0 on FAIL, 1 on
   INCONCLUSIVE. E_combined = product across tools. Logged per round.

b. **Frequency-scaled detection confidence (c_freq)**: Tracks flaw class
   encounter counts N_k. c_freq = c_base * (1 + alpha_freq * log(1+N_k)).
   alpha_freq = 0.1. Bounded at 1.0. Logged per finding.

c. **Epistemic marking**: Findings with (nu_k >= 0.6, c_ext <= 0.4) are
   shadow-tagged as SPECULATIVE. Count and fraction in summary.

d. **E-value to d coupling**: shadow_d_eff = min(1, E_combined/threshold)
   where threshold = 1/alpha = 20. Logged per round.

e. **Source co-occurrence logging**: Tracks which source pairs both return
   results vs one-only vs neither. For post-experiment estimation of
   pairwise correlation to potentially replace the global gamma_src
   discount.

## Questions for FFAFP Review

### FIND
What mathematical, engineering, or calibration risks does this integrated
system introduce? Check boundary conditions, reduction properties,
composition effects. Check the shadow code for bugs, semantic mismatches,
or calibration pitfalls.

### FOLLOW
How do the 5 shadow features interact with each other and with the
existing (nu_k, c_ext) framework? Are there emergent risks from
combining E-values, c_freq, and epistemic marking in one calibrator?

### ANALYSE
a. Is the two-dimensional (nu_k, c_ext) architecture mathematically
   coherent given the scalar eta_combined projection?
b. Is the E-value shadow computation valid as a calibration proxy?
   What are the limits of using fail_fraction as FPR?
c. Is c_freq correctly bounded? Does alpha_freq = 0.1 produce
   reasonable scaling? Does it interact with c_ext or nu_k?
d. Are the epistemic marking thresholds (nu_k >= 0.6, c_ext <= 0.4)
   well-chosen? What happens at the boundaries?
e. Is shadow_d_eff a useful calibration target? Does the linear
   normalisation (E_combined/threshold) make physical sense?
f. Is the source co-occurrence matrix sufficient for estimating
   pairwise correlation? What sample size is needed?

### FIX
Propose corrections. Classify as HARD (mathematical error, violated
bound, incorrect reduction) or SOFT (calibration, naming, completeness).

### P-PASS
Falsify the integrated system. Under what conditions does it fail?
What parameter regimes produce actively harmful outcomes? Can the
shadow instrumentation mislead post-experiment analysis?

## Format

Structure your response as FIND, FOLLOW, ANALYSE (a-f), FIX (HARD/SOFT),
P-PASS sections. Be concrete — reference specific equations, code lines,
and boundary conditions. If the system is sound, confirm which properties
you verified and how.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def dispatch_model(label, model_id, api, ts):
    """Dispatch to one model and return result dict."""
    t0 = time.monotonic()
    print(f"  Dispatching to {label} ({model_id} via {api})...")

    try:
        if api == "gemini_native":
            response = call_gemini(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=300,
                max_retries=5,
                backoff_base=3.0,
            )
        elif api == "claude_cli":
            response = call_claude_cli(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=600,
                max_retries=2,
            )
        elif api == "openrouter":
            response = call_openrouter(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=300,
                max_retries=3,
            )
        else:
            raise ValueError(f"Unknown API: {api}")

        elapsed = time.monotonic() - t0
        print(f"  {label} responded in {elapsed:.1f}s ({len(response)} chars)")
        return {
            "model": model_id,
            "label": label,
            "api": api,
            "response": response,
            "time_s": round(elapsed, 1),
            "chars": len(response),
        }

    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"  {label} FAILED after {elapsed:.1f}s: {e}")

        # Fallback: if Gemini native fails, try OpenRouter
        if api == "gemini_native":
            print(f"  Falling back to Gemini via OpenRouter...")
            try:
                t0b = time.monotonic()
                response = call_openrouter(
                    model_id="google/gemini-3.1-pro",
                    system_prompt=CDSFL_TEXT,
                    user_prompt=CONFER_PROMPT,
                    max_tokens=32768,
                    timeout=300,
                    max_retries=3,
                )
                elapsed2 = time.monotonic() - t0b
                print(f"  Gemini (OpenRouter) responded in {elapsed2:.1f}s ({len(response)} chars)")
                return {
                    "model": "google/gemini-3.1-pro (via OpenRouter fallback)",
                    "label": label,
                    "api": "openrouter_fallback",
                    "response": response,
                    "time_s": round(elapsed + elapsed2, 1),
                    "chars": len(response),
                }
            except Exception as e2:
                print(f"  Gemini (OpenRouter) also FAILED: {e2}")

        return {"label": label, "error": str(e), "time_s": round(elapsed, 1)}


def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'='*72}")
    print(f"  FULL CONFER: Literature-Calibrated Extension + Shadow Calibrator")
    print(f"  Timestamp: {ts}")
    print(f"  Protocol: CDSFL + FFAFP")
    print(f"  Models: ge, cx, cc2, cgpt, ds")
    print(f"{'='*72}\n")

    results = {}

    for label, model_id, api in MODELS:
        result = dispatch_model(label, model_id, api, ts)
        results[label] = result

        # Save each result immediately
        log_path = LOGS_DIR / f"{label}_{ts}.json"
        log_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  Saved: {log_path}\n")

    # Combined log
    combined_path = LOGS_DIR / f"combined_{ts}.json"
    combined_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n  Combined log: {combined_path}")

    # Print summaries
    for label, result in results.items():
        print(f"\n{'='*72}")
        print(f"  {label.upper()} ({result.get('time_s', '?')}s, {result.get('chars', '?')} chars)")
        print(f"{'='*72}")
        resp = result.get("response", result.get("error", "No response"))
        if isinstance(resp, str):
            print(resp[:6000] if len(resp) > 6000 else resp)
            if len(resp) > 6000:
                print(f"\n  ... [{len(resp) - 6000} chars truncated, see full log] ...")

    return results


if __name__ == "__main__":
    run_confer()
