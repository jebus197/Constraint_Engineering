#!/usr/bin/env python3
"""Pre-flight CX + Gemini CDSFL review of run_exp36_evidence.py.

Dispatches the full runner to both models for FFF review, focusing on:
- CC2v verification agent wiring
- Stall-convergence detector logic
- Convergence gate softening (open_ch stability window)
- Any runtime-fatal bugs

This is a fitness check, not a full experiment.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    call_openrouter,
    call_gemini,
    _log,
)

# Load source env for API keys
from runner_core import source_env
source_env()

# Files
CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core.txt"
RUNNER_PATH = REPO_ROOT / "bench" / "run_exp36_evidence.py"

cdsfl_text = CDSFL_PATH.read_text(encoding="utf-8")
runner_code = RUNNER_PATH.read_text(encoding="utf-8")

REVIEW_PROMPT = f"""You are reviewing the experiment runner `run_exp36_evidence.py` for runtime correctness
before it is deployed for a full 5-model, 21-round CDSFL experiment.

This is a pre-flight fitness check. Focus on issues that would cause:
1. Runtime crashes (NameError, TypeError, missing imports, wrong signatures)
2. Logic errors in convergence detection (gate, stall detector, extension)
3. Wiring bugs (functions defined but not called, called with wrong args)
4. Data flow errors (checkpoint save/restore inconsistency, round_data missing keys)

The runner has these NEW components since the last review:
- CC2v verification agent: _VERIFICATION_PROMPT_TEMPLATE + _verification_step() — between-rounds
  FFF dispatch to CC2 for OPEN findings. Wired after immune bridge in main loop.
- Stall-convergence detector: _check_stall_convergence() — complementary secondary convergence
  signal checking open_ch + contested stasis cross-referenced with gamma. Two tiers (advisory/terminate).
  Wired after primary gate check.
- Convergence gate softening: open_ch stability window (not increasing for 3 rounds) replaces
  the old open_ch == 0 condition. open_ch_history tracked and checkpointed.

For each finding:
- State what the bug IS (concrete: file, function, line reference)
- FOLLOW: trace the consequence through the runner (what breaks at runtime?)
- Classify: RUNTIME_FATAL, LOGIC_ERROR, or MINOR
- If you cannot determine whether it is real, say UNCERTAIN

Do NOT report:
- Style preferences
- Hypothetical improvements
- Things that "could be" problems without concrete evidence

=== RUNNER CODE (run_exp36_evidence.py) ===

{runner_code}
"""

# Dispatch
results = {}

_log("=" * 60)
_log("Pre-flight review: run_exp36_evidence.py")
_log("=" * 60)

# CX (Codex / GPT-5.4 via OpenRouter)
_log("\nDispatching to CX (openai/gpt-5.4)...")
try:
    t0 = time.monotonic()
    cx_response = call_openrouter(
        model_id="openai/gpt-5.4",
        system_prompt=cdsfl_text,
        user_prompt=REVIEW_PROMPT,
        max_tokens=32768,
        timeout=300,
        max_retries=3,
    )
    cx_elapsed = time.monotonic() - t0
    results["CX"] = {
        "response": cx_response,
        "elapsed_s": round(cx_elapsed, 1),
        "chars": len(cx_response),
    }
    _log(f"CX done: {len(cx_response)} chars, {cx_elapsed:.1f}s")
except Exception as e:
    _log(f"CX failed: {e}")
    results["CX"] = {"error": str(e)}

# Gemini (3.1 Pro via Google API)
_log("\nDispatching to Gemini (gemini-3.1-pro-preview)...")
try:
    t0 = time.monotonic()
    gemini_response = call_gemini(
        model_id="gemini-3.1-pro-preview",
        system_prompt=cdsfl_text,
        user_prompt=REVIEW_PROMPT,
        max_tokens=32768,
        timeout=300,
        max_retries=5,
    )
    gemini_elapsed = time.monotonic() - t0
    results["Gemini"] = {
        "response": gemini_response,
        "elapsed_s": round(gemini_elapsed, 1),
        "chars": len(gemini_response),
    }
    _log(f"Gemini done: {len(gemini_response)} chars, {gemini_elapsed:.1f}s")
except Exception as e:
    _log(f"Gemini failed: {e}")
    results["Gemini"] = {"error": str(e)}

# Save results
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
out_path = REPO_ROOT / "bench" / "logs" / f"runner36_review_{ts}.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
_log(f"\nResults saved: {out_path}")

# Print responses
for model, data in results.items():
    _log(f"\n{'=' * 60}")
    _log(f"{model} RESPONSE:")
    _log("=" * 60)
    if "error" in data:
        _log(f"ERROR: {data['error']}")
    else:
        print(data["response"], file=sys.stderr)
