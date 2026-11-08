#!/usr/bin/env python3
"""Reverse the runway fix and the reserve raise, and prove the guard reds.

2 reversions are applied to `scripts/cdsfl_sv.py`, one at a time, and
`bench/tests/test_the_runway_is_measured_against_its_own_refusal_2026-11-08.py`
must fail for each. Without this the fix is an addition nothing executes.

THE SUBJECT IS A LIVE TOOL, so it is restored from bytes held here and verified
by sha256 before exit -- never by `git checkout --`, which has destroyed the
file it was meant to restore (`feedback_a_harness_must_restore_what_it_found_2026-11-01`).
Anchors are asserted present before any edit
(`feedback_a_mutation_harness_must_derive_its_anchors_2026-11-04`).
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts/cdsfl_sv.py"
GUARD = (REPO / "bench/tests"
         / "test_the_runway_is_measured_against_its_own_refusal_2026-11-08.py")

MUTATIONS = [
    ("headroom measured against the loader's cut again (the overstatement)",
     "        return self.refuse_chars - self.chars",
     "        return _MEMORY_INDEX_LIMIT_CHARS - self.chars",
     "headroom_stops_at_the_refusal_not_the_loader_limit"),
    ("the reserve back to 0.95, against his ruling",
     "_MEMORY_INDEX_REFUSE_FRACTION = 0.98",
     "_MEMORY_INDEX_REFUSE_FRACTION = 0.95",
     "the_ruling_moved_the_reserve"),
]


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    good = SUBJECT.read_bytes()
    good_sha = hashlib.sha256(good).hexdigest()
    print(f"subject : {SUBJECT.relative_to(REPO)}\nsha256  : {good_sha}")
    base = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                          capture_output=True, text=True, cwd=REPO)
    print(f"baseline: {'GREEN' if base.returncode == 0 else 'RED'}")
    if base.returncode != 0:
        print(base.stdout[-1500:])
        return 1
    failures: list[str] = []
    try:
        for name, anchor, repl, expect in MUTATIONS:
            txt = good.decode("utf-8")
            if txt.count(anchor) != 1:
                failures.append(f"{name}: anchor appears {txt.count(anchor)} "
                                f"times, not 1 -- the probe is wrong")
                print(f"\n[{name}] ANCHOR COUNT WRONG; skipped")
                continue
            SUBJECT.write_text(txt.replace(anchor, repl, 1), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                               capture_output=True, text=True, cwd=REPO)
            red, named = r.returncode != 0, expect in r.stdout
            tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            print(f"\n[{name}]\n  guard: {'RED' if red else 'GREEN'}   {tail}")
            print(f"  the expected test is named: {named}")
            if not red:
                failures.append(f"{name}: guard stayed GREEN")
            elif not named:
                failures.append(f"{name}: red, but {expect!r} is not the failure")
            SUBJECT.write_bytes(good)
    finally:
        SUBJECT.write_bytes(good)
        back = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
        print(f"\nrestored: sha256 matches = {back == good_sha}")
        if back != good_sha:
            print("★ cdsfl_sv.py MAY BE MUTATED. Restore it by hand.")
            return 1
    print("\n" + "=" * 70)
    if failures:
        for f in failures:
            print("FAILURE:", f)
        return 1
    print(f"all {len(MUTATIONS)} reversions turn the guard red")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
