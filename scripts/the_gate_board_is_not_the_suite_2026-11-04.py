#!/usr/bin/env python3
"""The commit gate's board is a SUBSET of the suite, and a figure from it must not be called the suite.

WHY THIS EXISTS. On 2026-11-04 a board result of "2502 passed, 11 skipped, 0
failed" was reported to the founder as a fully green board, in answer to his
explicit instruction to give him a fully green, honest board and not to cut
corners to make it green. That figure is the COMMIT GATE's board -- the static
`GUARDS` list in `hooks/pre-commit` -- and not `bench/tests/`. The suite collects
several times as many tests, and a test that had been red for 26 commits sits
outside the gate's list, which is exactly why nothing noticed it.

This is the `feedback_true_sentence_wrong_frame` shape repeated: an earlier
report of "2,333 passed" was 120 files of 759 rather than the suite. The sentence
was true of what it measured and wrong about what it claimed to measure.

WHAT IT MEASURES, by collection rather than by assertion:
  * tests collected from the gate's own GUARDS list, read out of `hooks/pre-commit`
  * tests collected from the whole of `bench/tests/`
  * the share, exactly, as a census and therefore with no sampling interval
  * every guard file the gate lists that is absent from disk

Usage: python3 scripts/the_gate_board_is_not_the_suite_2026-11-04.py
Exit 0 on a clean measurement, 3 if either collection fails.
"""
import os
import pathlib
import re
import subprocess
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
GATE = REPO / "hooks" / "pre-commit"
SUITE = REPO / "bench" / "tests"

COUNT = re.compile(r"(\d+)\s+tests?\s+collected")


def guard_list() -> list:
    """The gate's own list, read from the gate rather than duplicated here."""
    m = re.search(r'^GUARDS="(.*?)"', GATE.read_text(encoding="utf-8"),
                  re.S | re.M)
    if not m:
        return []
    return [l.strip() for l in m.group(1).splitlines() if l.strip()]


def collect(targets) -> int:
    """Tests pytest COLLECTS for these targets. Collection, not execution."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *[str(t) for t in targets],
         "--collect-only", "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO))
    for line in reversed(r.stdout.splitlines()):
        m = COUNT.search(line)
        if m:
            return int(m.group(1))
    return -1


def main() -> int:
    answer_help(__doc__, __file__)
    guards = guard_list()
    if not guards:
        print("the gate's GUARDS list could not be read; measurement void.")
        return 3
    missing = [g for g in guards if not (REPO / g).is_file()]
    present = [REPO / g for g in guards if (REPO / g).is_file()]

    gate_n = collect(present)
    suite_n = collect([SUITE])
    if gate_n < 0 or suite_n < 0:
        print("a collection did not report a count; measurement void.")
        return 3

    files_on_disk = len(sorted(SUITE.glob("test_*.py")))
    share = Fraction(gate_n, suite_n)
    print(f"guard files the gate lists        : {len(guards)}")
    print(f"  of those, absent from disk      : {len(missing)} "
          f"{missing if missing else ''}")
    print(f"test FILES in bench/tests/        : {files_on_disk}")
    print()
    print(f"tests collected, gate's list      : {gate_n}")
    print(f"tests collected, whole suite      : {suite_n}")
    print(f"share the gate's board covers     : {gate_n}/{suite_n} = "
          f"{float(share):.6f}  ({share.limit_denominator(40)} as a fraction)")
    print(f"tests the gate's board NEVER RUNS : {suite_n - gate_n}")
    print()
    print(f"file share                        : {len(guards)}/{files_on_disk} = "
          f"{len(guards)/files_on_disk:.6f}")
    print()
    print("THE RULE THIS SUPPORTS: a count from the gate's board is a statement")
    print("about the gate's board. Calling it the suite overstates coverage by")
    print(f"a factor of {suite_n / gate_n:.4f}, and the tests outside it are")
    print("where a regression can sit unnoticed for many commits.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
