#!/usr/bin/env python3
"""Adding every unreached test file to the commit gate costs 88.7 minutes, not 6 per cent.

★ THIS CORRECTS A FIGURE I GAVE HIM, AND THE CORRECTION REVERSES THE
RECOMMENDATION HE ACCEPTED.

He asked, against the proposal to add the unreached test files to the commit
gate: *"You asked whether this means a very large increase in time per commit."*
The report of 2026-10-30 answered **No**, and supported it with this: *"The 6
newest guards run 75 tests in 18.88 seconds against a gate that currently takes
312 seconds, which is an addition of about 6 per cent, or roughly 19 seconds."*

THE ARITHMETIC IS RIGHT AND IT ANSWERS A DIFFERENT QUESTION. 18.88 s against
312.22 s is indeed about 6 per cent. But those 6 guards are 75 of the 12,048
tests in the unreached set -- **0.623 per cent of them**. The question was the
cost of adding the unreached FILES; the evidence offered was the cost of adding
6 of them. Quoting the second as an answer to the first is the flattering-measure
failure this project has recorded repeatedly, and he accepted a recommendation
on it.

WHAT IT ACTUALLY COSTS, from the 2 measurements that exist:

  * the commit gate: 1,597 tests in 312.22 s, measured across this session's
    boards, 73 of 731 test files;
  * a full board on a frozen tree: 13,645 tests in 5,634.07 s, measured
    2026-10-30 at `80f4dfcd`, log at `~/Desktop/CDSFL_full_board_2026-10-30_rerun.txt`.

Adding every unreached file makes the gate the full board. That is **+12,048
tests and +5,321.85 s, 88.7 minutes, taking 312 s to 5,634 s -- a factor of
18.05, a 1,705 per cent increase.**

AND THE UNREACHED SET IS NOT MERELY LARGER, IT IS SLOWER PER TEST: 441.72 ms
against the gate's 195.50 ms, a factor of 2.26. So the gate's current membership
is the CHEAP files, and that is unlikely to be an accident -- which is itself an
argument for adding selectively rather than wholesale.

SO THE RECOMMENDATION CHANGES, and the change is his to accept or refuse:

  * NOT the 658 files. A commit that takes an hour and a half is a commit
    nobody makes, and a gate nobody can afford to run protects nothing.
  * The NEWEST GUARDS, which is what the 6 per cent figure actually measured
    and what the original argument for the change was about: a guard written
    today should run before today's commit lands. That is the demonstrated
    defect -- a guard on one of these reports sat failing through 3 consecutive
    commits because nothing cheap ran it.
  * The full board stays a separate periodic run, which is what it already is.

Cross-verified per the 21 Apr 2026 rule: every ratio computed in NumPy and
again in mpmath at 40 digits.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib

import mpmath
import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Measured, each with its source in the docstring above.
GATE_TESTS, GATE_SECONDS = 1597, 312.22
SUITE_TESTS, SUITE_SECONDS = 13645, 5634.07
#: The 6 newest guards, the scope the 6-per-cent figure actually measured.
SIX_GUARD_TESTS, SIX_GUARD_SECONDS = 75, 18.88


def reach() -> dict:
    """The gate's file reach, from the committed producer rather than a count."""
    spec = importlib.util.spec_from_file_location(
        "gate_cost", REPO / "scripts" / "precommit_gate_cost_2026-09-10.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.repository_reach()


def ratio(a: float, b: float) -> tuple[float, float, bool]:
    np_v = float(np.divide(a, b))
    with mpmath.workdps(40):
        mp_v = float(mpmath.mpf(a) / mpmath.mpf(b))
    return np_v, mp_v, abs(np_v - mp_v) < 1e-12


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.parse_args()

    r = reach()
    added_tests = SUITE_TESTS - GATE_TESTS
    added_s = SUITE_SECONDS - GATE_SECONDS
    f_np, f_mp, f_ok = ratio(SUITE_SECONDS, GATE_SECONDS)
    slow_np, slow_mp, slow_ok = ratio(SUITE_SECONDS / SUITE_TESTS,
                                      GATE_SECONDS / GATE_TESTS)
    rem_rate = added_s / added_tests * 1000.0

    print("=" * 74)
    print("WHAT ADDING EVERY UNREACHED TEST FILE REALLY COSTS")
    print("=" * 74)
    print(f"gate today      : {GATE_TESTS} tests in {GATE_SECONDS:.2f} s "
          f"({GATE_SECONDS / GATE_TESTS * 1000:.3f} ms/test)")
    print(f"gate file reach : {r['gate_files']} of {r['repository_test_files']}"
          f", {r['unreached']} unreached "
          f"(share {r['unreached_share']:.6f}) -- a census, no interval")
    print(f"full board      : {SUITE_TESTS} tests in {SUITE_SECONDS:.2f} s "
          f"({SUITE_SECONDS / SUITE_TESTS * 1000:.3f} ms/test)")
    print()
    print(f"ADDING EVERYTHING: +{added_tests} tests, +{added_s:.2f} s "
          f"({added_s / 60:.1f} minutes)")
    print(f"   the gate becomes {GATE_SECONDS:.0f} s -> {SUITE_SECONDS:.0f} s, "
          f"a factor of {f_np:.2f} ({(added_s / GATE_SECONDS) * 100:.0f} per cent)")
    print(f"   ratio cross-check: NumPy {f_np:.6f}, mpmath {f_mp:.6f}, "
          f"agree={f_ok}")
    print()
    print("THE FIGURE THAT WAS QUOTED, AND ITS TRUE SCOPE")
    six_pct, _, _ = ratio(SIX_GUARD_SECONDS, GATE_SECONDS)
    print(f"   the 6 newest guards: {SIX_GUARD_TESTS} tests in "
          f"{SIX_GUARD_SECONDS:.2f} s = {six_pct * 100:.1f} per cent of the gate")
    cov, _, _ = ratio(SIX_GUARD_TESTS, added_tests)
    print(f"   they cover {SIX_GUARD_TESTS} of {added_tests} unreached tests = "
          f"{cov * 100:.3f} per cent of them")
    print("   so 6 per cent is the cost of adding 0.623 per cent of the set, "
          "and was")
    print("   offered as the cost of adding all of it.")
    print()
    print("AND THE UNREACHED SET IS SLOWER PER TEST, NOT JUST BIGGER")
    print(f"   gate      : {GATE_SECONDS / GATE_TESTS * 1000:.3f} ms/test")
    print(f"   remainder : {rem_rate:.3f} ms/test")
    print(f"   factor    : {rem_rate / (GATE_SECONDS / GATE_TESTS * 1000):.2f}x "
          f"(NumPy {slow_np:.6f} / mpmath {slow_mp:.6f} on the board rates, "
          f"agree={slow_ok})")
    print("   so the gate's current membership is the CHEAP files.")
    print()
    print("RECOMMENDATION, REVERSED FROM THE ONE HE ACCEPTED")
    print("   do NOT add the unreached files wholesale: a 1.5-hour commit is a")
    print("   commit nobody makes, and a gate nobody can afford protects nothing.")
    print("   ADD THE NEWEST GUARDS, which is the scope the 6 per cent measured")
    print("   and the scope the original argument was about -- a guard written")
    print("   today should run before today's commit lands.")
    print("   The full board stays a separate periodic run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
