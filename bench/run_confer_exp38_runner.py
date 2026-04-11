#!/usr/bin/env python3
"""Confer: CX + GE review of Exp 38 experimental runner (14 bug fixes).

Tightly scoped — runner diff only. No immune pipeline, no endocrine.
Models receive CDSFL core directives as system prompt.
"""

from __future__ import annotations

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# Ensure bench/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from runner_core import source_env
from experiment_11_orchestrator import call_openrouter, call_gemini

REPO_ROOT = Path(__file__).resolve().parent.parent
CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core.txt"
LOGS_DIR = REPO_ROOT / "bench" / "logs"

RUNNER_DIFF = r"""
diff --git a/bench/reference_runner.py b/bench/reference_runner.py
--- (main: c2f9167, Exp 37 proven state)
+++ (exp38-experimental: 1703ed1)

14 bug fixes from Exp 38 Round 0 ouroboros (system reviewed itself).
All findings were HIL-verified before implementation.

=== F2/F5/F9: add_verdict() timer corruption ===
- REMOVED: self.entries[canonical_id]["last_status_change_round"] = round_idx
+ Verdicts are evidence, not status transitions. Only resolve() updates the timer.
  Without this fix, every verdict resets the escalation timer, preventing stale
  findings from ever being escalated.

=== F14/F17/F22: contested_count terminal status leak ===
- OLD: skipped only MERGED status
+ NEW: skips all terminal statuses (MERGED, CLOSED, REFUTED, DUPLICATE, UNCONFIRMED)
  Without this fix, terminal findings inflate contested_count and block convergence.

=== F24: same-round challenge silently resolved ===
- OLD: unresolved = [v for v in challenges if v["round"] > latest_confirm_round]
+ NEW: uses >= so a challenge in the same round as a confirm is treated as unresolved.
  Without this fix, simultaneous confirm+challenge silently drops the challenge.

=== F6: escalate/auto_resolve direct mutation ===
- OLD: entry["status"] = "UNCONFIRMED" / "REFUTED" (direct dict write)
+ NEW: self.resolve(fid, status, current_round) — ensures timer update.
  Same root cause as F2/F5/F9: bypassing resolve() corrupts the timer.

=== F8: single-model MERGE kill ===
- OLD: any merge verdict immediately merges the finding
+ NEW: requires 2+ distinct models to agree on merge
  Without this fix, one model can irrevocably kill any finding with no quorum.

=== F0/F4: challenge-before-close ordering ===
- OLD: CONFIRMED+verified -> CLOSED immediately, then check challenges
+ NEW: check unresolved challenges FIRST, only close if none remain
  Without this fix, verified findings close and skip pending challenges.

=== F11: confirmation quorum inflation ===
- OLD: independent_count = 1 + len(external) (source model counts as implicit +1)
+ NEW: independent_count = len(external) — source model excluded
  For 5-model panel, 2 external confirms required (was effectively 1).

=== F18: REOPENED -> OPEN bypass ===
- OLD: entry["status"] = "OPEN" (direct mutation)
+ NEW: registry.resolve(canonical_id, "OPEN", round_idx)
  Same class as F6: direct mutation bypasses timer.

=== F7/F23: dead config max_open_crit_high ===
- OLD: cfg.max_open_crit_high defined in RunnerConfig but never checked
+ NEW: enforced in _evaluate_gate_conditions — blocks convergence if exceeded

=== F12: idempotent gate history ===
- OLD: open_ch_history.append(open_ch) unconditionally
+ NEW: guards against duplicate entries if called multiple times per round

=== F13: regex 4-digit ID ceiling ===
- OLD: C\d{4} — fails for finding IDs >= C10000
+ NEW: C\d{4,} — supports 4+ digit IDs

=== F19: regex character class backslash ===
- OLD: [\|<\-...] — unnecessary backslash before |
+ NEW: [|<\-...] — clean character class
"""

CONFER_PROMPT = """You are reviewing 14 bug fixes applied to the CDSFL experimental runner
(reference_runner.py) on the exp38-experimental branch.

Context: CDSFL is a structured falsification system for AI-assisted technical work.
Experiment 38 is the "ouroboros" — the system reviews and improves its own runner.
Round 0 produced 26 findings. 14 were CONFIRMED by human-in-loop verification and
implemented as the fixes below. The proven runner (run_exp37_evidence.py, which
converged at Round 15 with 222 canonical findings) is preserved on main as the
known-good baseline.

Your task: Review these 14 fixes under CDSFL/FFAFP (Find-Follow-Fix with P-pass).
For each fix, apply FFF:
  FIND: Is the fix correct? Does it address the stated root cause?
  FOLLOW: Trace consequences. What depends on this? What could break downstream?
  FIX: If you find a problem, state the minimal correction.

Focus on:
1. Correctness: Does each fix do what it claims?
2. Interactions: Do any fixes conflict with each other?
3. Missing edge cases: Are there scenarios these fixes don't cover?
4. Convergence impact: Could any fix prevent or delay legitimate convergence?
5. Regression risk: Could any fix break working behavior?

Do NOT review the immune pipeline, endocrine layer, or classification system.
Runner logic only.

Here are the fixes:

""" + RUNNER_DIFF + """

Present your findings as a numbered list. For each finding:
- State what you found (FIND)
- Trace the consequence (FOLLOW)
- State the fix if needed (FIX)
- Mark severity: CRITICAL / HIGH / MEDIUM / LOW

If a fix is correct and you find no issues, say so briefly and move on.
Do not pad with filler. Be direct.
"""


def main():
    source_env()
    cdsfl = CDSFL_PATH.read_text(encoding="utf-8")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    results = {}

    # --- Codex (CX) via OpenRouter ---
    print(f"[{ts}] Dispatching to Codex (GPT-5.4) via OpenRouter...")
    t0 = time.monotonic()
    try:
        cx_response = call_openrouter(
            model_id="openai/gpt-5.4",
            system_prompt=cdsfl,
            user_prompt=CONFER_PROMPT,
            max_tokens=16384,  # Scoped prompt — 16K is generous
            timeout=300,
            max_retries=2,
        )
        cx_elapsed = time.monotonic() - t0
        results["cx"] = {"response": cx_response, "elapsed": cx_elapsed, "error": None}
        print(f"  CX done ({cx_elapsed:.1f}s, {len(cx_response)} chars)")
    except Exception as e:
        cx_elapsed = time.monotonic() - t0
        results["cx"] = {"response": None, "elapsed": cx_elapsed, "error": str(e)}
        print(f"  CX failed ({cx_elapsed:.1f}s): {e}")

    # --- Gemini (GE) via Google GenAI ---
    print(f"  Dispatching to Gemini 3.1 Pro via Google GenAI...")
    t0 = time.monotonic()
    try:
        ge_response = call_gemini(
            model_id="gemini-3.1-pro-preview",
            system_prompt=cdsfl,
            user_prompt=CONFER_PROMPT,
            max_tokens=16384,
            timeout=300,
            max_retries=3,
        )
        ge_elapsed = time.monotonic() - t0
        results["ge"] = {"response": ge_response, "elapsed": ge_elapsed, "error": None}
        print(f"  GE done ({ge_elapsed:.1f}s, {len(ge_response)} chars)")
    except Exception as e:
        ge_elapsed = time.monotonic() - t0
        results["ge"] = {"response": None, "elapsed": ge_elapsed, "error": str(e)}
        print(f"  GE failed ({ge_elapsed:.1f}s): {e}")

    # --- Save results ---
    log_path = LOGS_DIR / f"confer_exp38_runner_{ts}.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"CDSFL Confer: Exp 38 Experimental Runner Review\n")
        f.write(f"Timestamp: {ts}\n")
        f.write(f"Branch: exp38-experimental\n")
        f.write(f"Subject: 14 bug fixes to reference_runner.py\n")
        f.write(f"Models: CX (GPT-5.4 via OpenRouter), GE (Gemini 3.1 Pro via Google)\n")
        f.write(f"{'='*72}\n\n")

        for label, data in results.items():
            model_name = "Codex GPT-5.4" if label == "cx" else "Gemini 3.1 Pro"
            f.write(f"## {model_name} ({label.upper()})\n")
            f.write(f"Elapsed: {data['elapsed']:.1f}s\n")
            if data["error"]:
                f.write(f"ERROR: {data['error']}\n")
            else:
                f.write(f"Response length: {len(data['response'])} chars\n\n")
                f.write(data["response"])
            f.write(f"\n\n{'='*72}\n\n")

    print(f"\nConfer log saved: {log_path}")

    # Print to stdout for CC1 capture
    for label, data in results.items():
        if data["response"]:
            model_name = "Codex GPT-5.4" if label == "cx" else "Gemini 3.1 Pro"
            print(f"\n{'='*72}")
            print(f"  {model_name} ({label.upper()}) — {data['elapsed']:.1f}s")
            print(f"{'='*72}\n")
            print(data["response"])


if __name__ == "__main__":
    main()
