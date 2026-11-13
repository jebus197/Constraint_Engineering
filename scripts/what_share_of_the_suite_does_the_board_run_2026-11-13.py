#!/usr/bin/env python3
"""What share of the test suite does the commit board actually run?

PRODUCER for a figure 2 memory files record and which has MOVED. Both were
written on 2026-11-04 and say the board is about a SIXTH of the suite:
`a gate board is not the suite` records 2,532 of 15,423, and
`the gate's board is a sixth of the suite` records 2,569 of 15,431.

Measured again on 2026-11-13 the ratio is nearer a QUARTER. The suite grew while
the board grew faster, so the headline "a sixth" is no longer true and the gap
the 2 entries exist to name has narrowed substantially.

WHY A SCRIPT AND NOT A SENTENCE. `measured-rate-travels-with-its-script`: a
number that exists only as prose in a note is a claim about evidence, not
evidence. This one was first recomputed by hand while waiting on a full suite
run, which is exactly how the superseded figures came to be quoted for 9 days.

IT NEVER EXECUTES A TEST. `--collect-only` enumerates; it does not run. That
matters because the founder's machine allows 1 heavy process and a full suite
run costs over 2 hours, so a script that answered this by running the suite
could not be used while the suite was running -- which is the only time anyone
asks.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PRECOMMIT = REPO / "hooks" / "pre-commit"
SUITE_DIR = "bench/tests/"

#: The figures the 2 memory files carry, named so the drift is visible rather
#: than silently replaced.
RECORDED = {
    "feedback_a_gate_board_is_not_the_suite_2026-11-04": (2532, 15423),
    "feedback_the_gates_board_is_a_sixth_of_the_suite_2026-11-04": (2569, 15431),
}


def _collect(targets: list[str]) -> int | None:
    r = subprocess.run([sys.executable, "-m", "pytest", *targets, "-q",
                        "--collect-only", "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True, timeout=1800)
    m = re.search(r"(\d+)\s+tests?\s+collected", r.stdout)
    return int(m.group(1)) if m else None


def board_files() -> list[str]:
    """The test files the commit board names, read from the hook itself."""
    txt = PRECOMMIT.read_text(errors="replace")
    named = sorted(set(re.findall(r"bench/tests/[A-Za-z0-9_./-]+\.py", txt)))
    return [f for f in named if (REPO / f).is_file()]


def main() -> int:
    files = board_files()
    print(f"  test files named in hooks/pre-commit : {len(files)}")
    board = _collect(files)
    total = _collect([SUITE_DIR])
    if board is None or total is None:
        print("  collection failed; no figure produced")
        return 2
    print(f"  board_tests = {board}")
    print(f"  suite_tests = {total}")
    share = board / total
    print(f"  board_share = {share:.6f}   = 1 in {total / board:.2f}")
    print()
    print("  AGAINST WHAT THE MEMORY FILES RECORD:")
    for name, (b0, t0) in RECORDED.items():
        print(f"    {name}")
        print(f"      recorded {b0} of {t0} = {b0 / t0:.6f} = 1 in {t0 / b0:.2f}")
        print(f"      board grew {board - b0:+d} ({(board - b0) / b0:+.2%}), "
              f"suite grew {total - t0:+d} ({(total - t0) / t0:+.2%})")
    print()
    # The direction is the point: the board covering MORE is an improvement, and
    # the entries' own warning -- that a green board is not a green suite --
    # survives it, because the share is still well under 1.
    assert 0.0 < share < 1.0, "a degenerate share means the collection is wrong"
    print(f"  the board still covers well under the whole suite ({share:.2%}), so")
    print("  'a green board is not a green suite' stands; only the SIZE of the")
    print("  gap has changed, and it has narrowed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
