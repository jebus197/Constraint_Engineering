#!/usr/bin/env python3
"""Does the B20-instrument guard go red when each constant is restored?

3 REVERSIONS, each putting back one of the constants the repair removed, each run
against `bench/tests/test_b20s_status_instrument_measures_2026-11-04.py`. A guard
that stays green under all 3 guards nothing.

The harness restores the subject from the bytes it FOUND, in a `finally`, and
verifies the restore by sha256 before reporting.

Usage: python3 scripts/the_b20_instrument_mutations_2026-11-04.py
"""
import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "has_the_bound_orchestrator_been_built_or_run_2026-11-02.py"
GUARD = REPO / "bench" / "tests" / "test_b20s_status_instrument_measures_2026-11-04.py"

MUTATIONS = [
    ("1. restore the hardcoded monitoring_loop verdict",
     '''    if not (wd.is_file() and gate.is_file()):
        verdicts["monitoring_loop"] = "ABSENT"
    elif act_ok and act_tests:''',
     '''    if not (wd.is_file() and gate.is_file()):
        verdicts["monitoring_loop"] = "ABSENT"
    elif False:'''),

    ("2. restore the say()-only vocabulary count",
     '        kinds = sorted(_ev | _say)',
     '        kinds = sorted(_say)'),

    ("3. restore the unconditional WHAT REMAINS paragraph",
     '    if _ml.startswith("BUILT AND TESTED, NOT ENABLED"):',
     '    if False:'),
]


def run_guard():
    r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q",
                        "--no-header"], capture_output=True, text=True, cwd=str(REPO))
    tail = [l for l in r.stdout.splitlines() if l.strip()][-1:] or [""]
    return r.returncode, tail[0][:80]


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    base_rc, base_line = run_guard()
    print(f"BASELINE: rc={base_rc}  {base_line}")
    if base_rc != 0:
        print("  not green before mutation; nothing can be concluded.")
        return 2

    original = SUBJECT.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    red = 0
    try:
        for name, old, new in MUTATIONS:
            src = SUBJECT.read_text(encoding="utf-8")
            if old not in src:
                print(f"  SKIP  {name}: anchor absent")
                continue
            SUBJECT.write_text(src.replace(old, new, 1), encoding="utf-8")
            try:
                rc, line = run_guard()
            finally:
                SUBJECT.write_bytes(original)
            if rc != 0:
                red += 1
            print(f"  {'RED (good)' if rc else 'GREEN -- NOT CAUGHT':<20}{name}")
            print(f"  {'':<20}{line}")
    finally:
        SUBJECT.write_bytes(original)
        ok = hashlib.sha256(SUBJECT.read_bytes()).hexdigest() == sha
        print(f"\nRESTORED byte-identical (sha256): {ok}")

    post_rc, post_line = run_guard()
    print(f"AFTER RESTORE: rc={post_rc}  {post_line}")
    good = red == len(MUTATIONS) and post_rc == 0
    print(f"{red} of {len(MUTATIONS)} reversions turned the guard red.")
    print("VERDICT:", "every constant is caught." if good
          else "A CONSTANT SURVIVES; the guard is incomplete.")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
