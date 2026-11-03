#!/usr/bin/env python3
"""Undo the execution-backing precondition 5 ways and require the guard to go red.

THE FIX UNDER TEST is 3 lines at the CONFIRMED/CORROBORATED -> CLOSED
transition in `bench/reference_runner_v3.py`: the entry's `verified` flag must
additionally be backed by an execution, meaning `falsifier_verdict ==
"CONFIRMED"` or a truthy `bugzilla_verified`. It was added 2026-11-03 after the
archive showed 34 of 412 closures resting on a flag a model had set in its own
reply JSON, every one of them recorded as `adjudicator="tool"`.

5 MUTATIONS, EACH UNDOING A DIFFERENT PROPERTY:
  M1  the conjunct is deleted              -> the model's word closes again
  M2  the backing test is always True      -> same hole, reached via the helper
  M3  the backing test is always False     -> NOTHING ever closes
  M4  any non-empty verdict counts         -> a voided instrument closes
  M5  `or` replaces `and`                  -> an UNVERIFIED but backed entry closes

M3 AND M5 ARE THE ONES THAT MATTER MOST, because M1 and M2 only restore a
defect the guard was written against, and a guard can hold those while being
blind to the opposite failure. M3 asks whether the guard notices the fix turning
into a blanket refusal to close anything -- that would be disabling a feature,
which the additive standard forbids, and a test suite that only checks "the bad
thing does not happen" passes happily while nothing good happens either. M4 asks
whether the 2026-10-03 voided-instrument control survived the change. M5 asks
whether `verified` is still required at all.

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
SUBJECT = REPO / "bench" / "reference_runner_v3.py"
GUARD = (REPO / "bench" / "tests"
         / "test_a_models_word_does_not_close_a_finding_2026-11-03.py")

HELPER = '''        _exec_backed = (entry.get("falsifier_verdict") == "CONFIRMED"
                        or bool(entry.get("bugzilla_verified")))'''
COND = '''        if (entry["status"] in ("CONFIRMED", "CORROBORATED")
                and entry.get("verified")
                and _exec_backed):'''

MUTATIONS = [
    ("M1 the conjunct is deleted outright",
     "the precondition entirely, which is the pre-fix behaviour",
     COND,
     '        if (entry["status"] in ("CONFIRMED", "CORROBORATED")\n'
     '                and entry.get("verified")):  # MUTANT'),
    ("M2 the backing test is always True",
     "the content of the backing test while keeping its shape",
     HELPER,
     '        _exec_backed = True  # MUTANT'),
    ("M3 the backing test is always False",
     "the close path altogether, which disables a feature",
     HELPER,
     '        _exec_backed = False  # MUTANT'),
    ("M4 any non-empty falsifier verdict counts as backing",
     "the 2026-10-03 voided-instrument control",
     HELPER,
     '        _exec_backed = (bool(entry.get("falsifier_verdict"))  # MUTANT\n'
     '                        or bool(entry.get("bugzilla_verified")))'),
    ("M5 `or` replaces `and` between verified and the backing",
     "the requirement that the entry be verified at all",
     COND,
     '        if (entry["status"] in ("CONFIRMED", "CORROBORATED")\n'
     '                and (entry.get("verified")\n'
     '                     or _exec_backed)):  # MUTANT'),
]


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=900,
    )
    lines = [ln for ln in (r.stdout + r.stderr).strip().splitlines() if ln.strip()]
    return r.returncode == 0, (lines[-1] if lines else "")


def main() -> int:
    argparse.ArgumentParser(
        description=("Undo the execution-backing precondition and require its "
                     "guard to go red.")).parse_args()

    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED runner passes the guard", green, tail))
        if not green:
            print("  The guard fails on the unmutated runner, so mutating it")
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
    print("=" * 78)
    print("DOES THE GUARD NOTICE THE EXECUTION-BACKING PRECONDITION BEING UNDONE?")
    print("=" * 78)
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  runner restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    if not restored:
        print("  THE RUNNER WAS NOT RESTORED. Fix that before anything else.")
    return 0 if (n_ok == len(results) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
