#!/usr/bin/env python3
"""Does the marking-clause guard actually go red when the fix is reverted?

★ WHY THIS EXISTS. On 2026-11-12 `scripts/the_windows_work_list_2026-11-12.py`
printed `exit 0 -- the loop ends here` while B145 through B150 all still read
`state: OPEN`, because the 21 predicates measure whether the WORK is done and
none of them asked whether the ENTRY had been marked done. His instruction had
3 clauses and the enumeration covered 2. The repair folds a marking check into
`blocking_open`, so the gap reaches the EXIT CODE and not merely a printed line.

★ WHAT THIS SCRIPT ANSWERS. A guard added beside a fix is a hypothesis until a
reverted fix makes it fail. Each mutation below reverts one property of the
repair and the guard must go red. A mutation that leaves the suite green names
a property nothing is testing.

★ IT RESTORES BYTE-EXACTLY OR IT FAILS LOUDLY. The sha256 of every mutated file
is recorded before the edit and asserted after the restore, because a harness
that does not restore what it found destroys the subject it was measuring --
and `git checkout --` is NOT used, since these files are staged-and-modified and
a checkout would discard real work.

Costs nothing beyond local pytest on 1 file. Dispatches to no model.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUNNER = REPO / "scripts" / "the_windows_work_list_2026-11-12.py"
GUARD = "bench/tests/test_the_work_list_loop_can_terminate_2026-11-12.py"

#: (name, find, replace_with) -- each reverts ONE property of the repair.
MUTATIONS = [
    ("the gap never reaches the exit code",
     "            blocking_open.append(n)",
     "            pass  # MUTANT: computed and discarded"),
    ("marking_gap always reports nothing",
     "    gap, missing = [], []",
     "    gap, missing = [], []\n    return [], ''  # MUTANT"),
    ("it fires regardless of whether the work is done",
     '        if items.get(n, {}).get("verdict") not in SETTLED:\n'
     "            continue                      # the work itself is still open",
     "        if False:  # MUTANT\n            continue"),
    ("an unreadable list passes silently instead of saying UNVERIFIED",
     '        return [], ("UNVERIFIED: the task list could not be parsed, so his "\n'
     '                    "marking clause was NOT checked on this run")',
     '        return [], ""  # MUTANT'),
    ("a declared pair points at an entry that does not exist",
     '    15: "B145",   # the severity brief through BOTH halves, blind and joint',
     '    15: "B9999",  # MUTANT'),
    ("a missing entry is no longer named",
     '            missing.append(f"item {n} names {ident}, which is not in the list")',
     "            pass  # MUTANT"),
]


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_guard() -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q",
                        "-p", "no:cacheprovider", GUARD],
                       cwd=REPO, capture_output=True, text=True, timeout=900)
    return r.returncode == 0, (r.stdout or "").strip().splitlines()[-1:][0] \
        if (r.stdout or "").strip() else ""


def main() -> int:
    original = RUNNER.read_text(encoding="utf-8")
    before = sha(RUNNER)

    green, line = run_guard()
    print(f"baseline: {'GREEN' if green else 'RED'}  {line}")
    if not green:
        print("REFUSED: the guard is already red, so a mutation proves nothing.")
        return 2

    red = 0
    try:
        for name, find, repl in MUTATIONS:
            if original.count(find) != 1:
                print(f"  [SKIP ] {name}: anchor appears "
                      f"{original.count(find)} time(s), expected 1")
                continue
            RUNNER.write_text(original.replace(find, repl, 1), encoding="utf-8")
            ok, ln = run_guard()
            if ok:
                print(f"  [GREEN] {name}  <-- NOTHING TESTS THIS")
            else:
                red += 1
                print(f"  [RED  ] {name}  ({ln})")
            RUNNER.write_text(original, encoding="utf-8")
            assert sha(RUNNER) == before, "restore did not reproduce the original"
    finally:
        RUNNER.write_text(original, encoding="utf-8")
        after = sha(RUNNER)
        print(f"\nrestored byte-exactly: {after == before}  sha256 {after[:16]}")
        assert after == before, "THE SUBJECT WAS NOT RESTORED"

    n = len(MUTATIONS)
    print(f"{red} of {n} mutation(s) red")
    return 0 if red == n else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    raise SystemExit(main())
