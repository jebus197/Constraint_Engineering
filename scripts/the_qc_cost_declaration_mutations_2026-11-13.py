#!/usr/bin/env python3
"""Revert each part of the B172 repair and confirm a named test goes red.

B172: `qc` ran the full suite by default (D1) with a waiter 6.27x shorter
than the suite itself (D2), so it could only ever burn 30 minutes and warn
that it could not measure.

★ RESTORES WHAT IT FOUND. The subject may be uncommitted while this runs, so
`git checkout --` would discard the repair rather than the mutation. Original
bytes are read first, written back in a `finally`, SHA-256 compared at the end.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
QC = REPO / "scripts" / "cdsfl_qc.py"
TEST = REPO / "bench" / "tests" / "test_qc_declares_its_cost_2026-11-13.py"

MUTATIONS = [
    ("Q1 run the suite by default again",
     "def check_test_consistency(root: Path, with_suite: bool = False)",
     "def check_test_consistency(root: Path, with_suite: bool = True)",
     "qc spends hours of his machine unasked"),
    ("Q2 drop the flag from main()",
     "with_suite=args.with_suite", "with_suite=True",
     "the default is back to spending the suite"),
    ("Q3 report the deliberate skip as a failed measurement",
     '"category": "INFO",\n            "file": "bench/tests/",\n'
     '            "detail": (\n                f"Suite NOT run (default).',
     '"category": "WARN",\n            "file": "bench/tests/",\n'
     '            "detail": (\n                f"Suite NOT run (default).',
     "a fail-safe recorded as a fact: right decision, false reason"),
    ("Q4 pin the waiter back to the typed constant",
     "timeout=suite_timeout(root),", "timeout=PYTEST_SUITE_TIMEOUT_S,",
     "the waiter is 6.27x shorter than the suite again"),
    ("Q5 make the derivation return the floor always",
     "return max(floor, int(seconds * 2))", "return floor",
     "the derivation is decorative"),
    # ★ Q6 FIRST STRIPPED THE HELP *TEXT*, WHICH IS NOT A MUTATION: argparse
    # still prints the flag NAME, so --help still advertises it and the test
    # correctly stayed green. A mutation has to remove the capability, not its
    # prose. This one deletes the argument itself.
    ("Q6 remove the flag from the parser entirely",
     '"--with-suite", action="store_true",', '"--with-suite-DISABLED", action="store_true",',
     "the flag is gone and --help cannot advertise it"),
]


def _red() -> bool:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(TEST), "-x", "-q",
         "--no-header", "-p", "no:cacheprovider"],
        cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode != 0


def main() -> int:
    original = QC.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    caught = 0
    try:
        if _red():
            print("  ABORT: red before any mutation.")
            return 2
        print(f"  baseline GREEN; driving {len(MUTATIONS)} reversions\n")
        for name, find, repl, why in MUTATIONS:
            text = original.decode()
            if text.count(find) != 1:
                print(f"  {name:44s} ANCHOR MISS ({text.count(find)})")
                continue
            QC.write_text(text.replace(find, repl, 1))
            try:
                red = _red()
            finally:
                QC.write_bytes(original)
            caught += bool(red)
            print(f"  {name:44s} {'RED' if red else 'STILL GREEN'}")
            if not red:
                print(f"      NOT CAUGHT -- {why}")
    finally:
        QC.write_bytes(original)
        if hashlib.sha256(QC.read_bytes()).hexdigest() != digest:
            print("\n  ★ RESTORE FAILED")
            return 3
        print("\n  restore verified byte-identical by SHA-256")
    print(f"  {caught} of {len(MUTATIONS)} reversions caught")
    return 0 if caught == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
