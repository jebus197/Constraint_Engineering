#!/usr/bin/env python3
"""Undo each of the actuator's guarantees and require its guard to go red.

THE SUBJECT is `bench/tools/cy_actuator_2026-11-03.py`, a thin outer supervisor
that drives the resume of a run which paused itself for human review. It
declares 5 guarantees as data. A declaration is worth nothing unless reverting
it is detected, so each mutation here removes exactly one property.

7 MUTATIONS, EACH UNDOING A DIFFERENT PROPERTY:
  M1  G2 removed        -> a RESUME is issued while the run's process is alive
  M2  G4 inverted       -> an unrecognised exit code reaches RESUME
  M3  G3 removed        -> the resume budget stops bounding the loop
  M4  G1 removed        -> a launch happens with nothing recorded
  M5  the unknown case  -> the no-pulse HOLD reclaims the known-alive reason
  M6  --act ignored     -> acting stops being opt-in
  M7  G5 broken         -> the decision log is truncated instead of appended

M5 IS THE ONE THAT MATTERS MOST. It is the actual defect this file's own P-pass
found: with no pulse on disk the decision was right (HOLD) and the recorded
reason asserted the process was alive, which was never measured. If the guard
does not go red on M5 then that repair is not held and the record can state an
unmeasured fact again.

THE SUBJECT IS RESTORED BY HASH, NOT BY HOPE, per
`feedback_a_harness_must_restore_what_it_found_2026-11-01`: the original bytes
are held in memory, written back in a `finally`, and the sha256 compared before
the exit code is decided.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "bench" / "tools" / "cy_actuator_2026-11-03.py"
GUARD = (REPO / "bench" / "tests"
         / "test_the_actuator_holds_its_contract_2026-11-03.py")

MUTATIONS = [
    ("M1 G2 removed: a live process no longer blocks a resume",
     "the refusal to resume a run whose process is still running",
     "        if alive and pid_known:",
     "        if False and alive and pid_known:  # MUTANT"),
    ("M2 G4 inverted: an unrecognised exit code reaches RESUME",
     "the rule that anything unclassified HOLDS",
     '''    return {"decision": "HOLD",
            "reason": (f"the run exited {exit_code}, which is a failure and not a "''',
     '''    return {"decision": "RESUME",  # MUTANT
            "reason": (f"the run exited {exit_code}, which is a failure and not a "'''),
    ("M3 G3 removed: the resume budget stops bounding the loop",
     "the bound that stops the actuator driving for ever",
     '        if row["decision"] == "RESUME" and resumes >= max_resumes:',
     '        if False and resumes >= max_resumes:  # MUTANT'),
    ("M4 G1 removed: a launch happens with nothing recorded",
     "the rule that no action is taken without a recorded decision",
     "        record(log_dir, row)\n        rows.append(row)",
     "        rows.append(row)  # MUTANT: the record is skipped"),
    ("M5 the no-pulse HOLD reclaims the known-alive reason",
     "the separation of an OBSERVED live process from an UNKNOWN one",
     '''        if alive:
            return {"decision": "HOLD",
                    "reason": ("the run reported PAUSED but no pulse names a "
                               "process, so whether it has exited is UNKNOWN "
                               "rather than known; a resume could collide with a "
                               "live run and is not driven on an unknown"),
                    "evidence": ev}''',
     '''        if alive:
            return {"decision": "HOLD",
                    "reason": ("the run reported PAUSED but its process is still "
                               "alive, which is a contradiction; nothing is driven "
                               "until it is understood"),  # MUTANT
                    "evidence": ev}'''),
    ("M6 --act ignored: acting stops being opt-in",
     "the opt-in nature of acting, so a dry classification now drives a resume",
     '        if row["decision"] != "RESUME" or not act:\n            break',
     '        if row["decision"] != "RESUME":  # MUTANT\n            break'),
    ("M7 G5 broken: the decision log is truncated rather than appended",
     "the append-only property of the decision log",
     '    with out.open("a", encoding="utf-8") as fh:',
     '    with out.open("w", encoding="utf-8") as fh:  # MUTANT'),
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
        description=("Revert each of the actuator's 5 guarantees and require "
                     "its guard to go red.")).parse_args()

    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED actuator passes its guard", green, tail))
        if not green:
            print("  The guard fails on the unmutated actuator; mutating it")
            print(f"  would prove nothing. {tail}")
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
    print("DOES THE GUARD NOTICE THE ACTUATOR'S CONTRACT BEING UNDONE?")
    print("=" * 76)
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  actuator restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    if not restored:
        print("  THE ACTUATOR WAS NOT RESTORED. Fix that before anything else.")
    return 0 if (n_ok == len(results) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
