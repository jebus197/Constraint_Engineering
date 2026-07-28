#!/usr/bin/env python3
"""Confer Round 2: contextual vs static rules for runner judgment calls.

Round 1 reviewed 14 bug fixes. Both models confirmed the mechanical fixes
(timer, ordering, resolve bypass) and flagged 4 judgment-call fixes as
using static rules where contextual evidence-based decisions would be better.

This round asks CX and GE to design the contextual versions.

Scoped tightly: 4 fixes only, with the specific findings from Round 1.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runner_core import source_env
from experiment_11_orchestrator import call_openrouter, call_gemini

REPO_ROOT = Path(__file__).resolve().parent.parent
CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core.txt"
LOGS_DIR = REPO_ROOT / "bench" / "logs"

CONFER_PROMPT = """You are designing contextual decision logic for 4 fixes in the CDSFL
experimental runner. This is Round 2 of a confer — Round 1 confirmed the fixes are
correct as safety floors but identified that static rules are suboptimal where the
system has evidence to make contextual decisions.

DESIGN PRINCIPLE (from the project founder, a non-developer):
"If every condition has a counter-condition that could be more effective in a given
circumstance, the models should prefer that condition instead. Where doubt and
uncertainty are meaningful factors, prefer the stronger measure. Where the evidence
is clear, prefer the more permissive path. Pick the best tool for the particular job."

The runner already has: a FindingRegistry with per-finding verdict history, model
attribution, confidence scores, round timestamps, and severity ratings. The immune
pipeline provides cell-type verdicts with evidence strings.

For each of the 4 fixes below, design:
1. The FLOOR (hard minimum that can never be bypassed — the safety gate)
2. The CONTEXTUAL RULE (how evidence should modulate the decision)
3. The ESCALATION PATH (what happens when evidence is ambiguous)

Keep designs minimal. State what evidence the runner should inspect, what thresholds
apply, and what happens at each decision point. Pseudocode is fine. Do not over-engineer.

=== FIX 1: F8 — Merge Quorum ===

Current static rule: require 2+ distinct models to agree on merge.

Round 1 findings:
- CX: On small panels (<2 external models), merge becomes impossible. Duplicates
  pile up and block convergence.
- GE (HIGH): Even with 2 models, they might vote to merge into DIFFERENT targets.
  Naive count passes without consensus on target. This is a logic bug.

Questions to answer:
- When is a single high-confidence merge vote sufficient?
- How should target disagreement be handled?
- What is the floor below which merge should never proceed?

=== FIX 2: F11 — Confirmation Quorum ===

Current static rule: require 2 independent external confirmations (source model excluded).

Round 1 finding:
- CX: Correct and defensible. But combined with other tightening, may slow convergence.

Questions to answer:
- Should confirmation threshold vary with finding severity?
- Should it vary with experiment phase (early vs late rounds)?
- What is the floor?

=== FIX 3: F7/F23 — max_open_crit_high Convergence Gate ===

Current static rule: block convergence if open critical/high findings exceed
cfg.max_open_crit_high. Previously dead config, now enforced.

Round 1 findings:
- CX (HIGH): Highest regression risk. Changes convergence criteria. If default
  too strict, runner stalls where Exp 37 converged.

Questions to answer:
- Should this threshold be dynamic based on experiment phase?
- Should it count only non-terminal active findings?
- How does it interact with the escalation mechanism?

=== FIX 4: F14/F17/F22 — Terminal Status in contested_count ===

Current static rule: skip all terminal statuses (MERGED, CLOSED, REFUTED,
DUPLICATE, UNCONFIRMED) in contested_count.

Round 1 finding:
- CX (MEDIUM): Is UNCONFIRMED truly terminal? If it can be reopened by new
  evidence, excluding it could allow premature convergence.

Questions to answer:
- Which statuses are genuinely irrecoverable vs potentially recoverable?
- Should UNCONFIRMED findings be tracked separately?
- What is the correct contested_count semantics?

=== ALSO VERIFY ===

GE-8 from Round 1 flagged that resolve() might reject non-terminal states.
I have verified: resolve() at line 309-317 accepts any status string with no
guard. GE-8 is a NON-ISSUE. Do not revisit.

CX-13 flagged incomplete timer audit. I will grep separately. Do not revisit.

Present your design for each fix. Be concrete. State the evidence the runner
should inspect and the decision logic. Minimal pseudocode is preferred over
prose descriptions.
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
            max_tokens=16384,
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
    log_path = LOGS_DIR / f"confer_exp38_contextual_{ts}.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"CDSFL Confer Round 2: Contextual Decision Design\n")
        f.write(f"Timestamp: {ts}\n")
        f.write(f"Branch: exp38-experimental\n")
        f.write(f"Subject: Contextual vs static rules for F8, F11, F7/F23, F14/F17/F22\n")
        f.write(f"Models: CX (GPT-5.4), GE (Gemini 3.1 Pro)\n")
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

    for label, data in results.items():
        if data["response"]:
            model_name = "Codex GPT-5.4" if label == "cx" else "Gemini 3.1 Pro"
            print(f"\n{'='*72}")
            print(f"  {model_name} ({label.upper()}) — {data['elapsed']:.1f}s")
            print(f"{'='*72}\n")
            print(data["response"])


if __name__ == "__main__":
    main()
