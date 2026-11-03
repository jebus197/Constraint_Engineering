#!/usr/bin/env python3
"""Revert the scorer's 3 repaired properties and require its guard to go red.

THE SUBJECT is `scripts/score_the_orchestrator_arm_2026-11-03.py`, which scores
the bound-orchestrator arm's pre-registered predictions. All 3 properties
reverted here were DEFECTS found by exercising that scorer against the archive
before the arm existed, so each mutation restores a state the scorer actually
shipped in during drafting.

  M1  the verdict rule returns to 2 values, lower bound only
      -> a run with EVERY adjudication tool-made but n < 16 reads FALSIFIED
  M2  the probe reads `*_report.json` instead of `runner_state.json`
      -> O1 returns NOT SCORABLE everywhere, as it did in 347 of 347 runs
  M3  an entry carrying a tool's OUTPUT but no adjudicator counts as tool-made
      -> the predicate that returned 79 of 79 instead of 77

M1 IS THE ONE THAT MATTERS MOST. It is statistically plausible, it reads as
rigour, and it silently converts sample size into evidence: 7 of the 10 runs it
called FALSIFIED have a point estimate of exactly 1.0.

THE SUBJECT IS RESTORED BY HASH, NOT BY HOPE, per
`feedback_a_harness_must_restore_what_it_found_2026-11-01`.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "score_the_orchestrator_arm_2026-11-03.py"
GUARD = (REPO / "bench" / "tests"
         / "test_the_orchestrator_scorer_rule_2026-11-03.py")

MUTATIONS = [
    ("M1 the verdict rule returns to 2 values, lower bound only",
     "the 3-valued rule that keeps a wide interval from reading as a "
     "falsification",
     '''    verdict = ("HOLDS" if wl >= O1_FLOOR
               else "FALSIFIED" if wh < O1_FLOOR
               else "INDETERMINATE")''',
     '''    verdict = "HOLDS" if wl >= O1_FLOOR else "FALSIFIED"  # MUTANT'''),
    ("M2 the probe reads the report file instead of the runner state",
     "reading the file the adjudication fields actually live in",
     "    classify = _classifier()\n    s = _state(run)",
     "    classify = _classifier()\n    s = _report(run)  # MUTANT"),
    ("M3 a mechanism without an adjudicator counts as tool-made",
     "the rule that carrying a tool's output is not being decided by one",
     '''        verdict = classify(e)
        if verdict == "tool":''',
     '''        verdict = classify(e)
        if not verdict or verdict == "unknown":
            verdict = "tool" if e.get("status_mechanism") else verdict  # MUTANT
        if verdict == "tool":'''),
]


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=600,
    )
    lines = [ln for ln in (r.stdout + r.stderr).strip().splitlines() if ln.strip()]
    return r.returncode == 0, (lines[-1] if lines else "")


def main() -> int:
    argparse.ArgumentParser(
        description=("Revert the scorer's 3 repaired properties and require "
                     "its guard to go red.")).parse_args()

    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED scorer passes its guard", green, tail))
        if not green:
            print(f"  The guard fails unmutated; mutating proves nothing. {tail}")
            return 1
        text = original.decode()
        for name, reverts, find, repl in MUTATIONS:
            n = text.count(find)
            if n != 1:
                results.append((f"{name} [NOT APPLIED]", False,
                                f"its anchor occurs {n} times, not 1"))
                continue
            SUBJECT.write_text(text.replace(find, repl, 1), encoding="utf-8")
            red, tail = _run_guard()
            SUBJECT.write_bytes(original)
            results.append((name, not red,
                            tail if not red else
                            f"GAP: the guard stayed GREEN, so it does not hold "
                            f"{reverts}."))
    finally:
        SUBJECT.write_bytes(original)

    h1 = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    restored = h0 == h1
    print("=" * 76)
    print("DOES THE GUARD NOTICE THE SCORER'S REPAIRS BEING UNDONE?")
    print("=" * 76)
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  scorer restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    return 0 if (n_ok == len(results) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
