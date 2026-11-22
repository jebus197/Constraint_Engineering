#!/usr/bin/env python3
"""Would the guard NOTICE if the second-person widening were reverted or weakened?

DRAFTED 2026-11-22 while batch 1's board ran. Run it AFTER the widening lands in
`hooks/work_not_narrate.py`; before that the guard is correctly red and there is
nothing to mutate.

SUBJECT: `hooks/work_not_narrate.py`, the `_HIS_RESIDUE` alternation.
GUARD:   `bench/tests/test_the_second_person_marker_is_his_2026-11-22.py`.

A suite says whether the code passes. A harness says whether the suite would
notice if it stopped. This project has already been caught by the difference:
3 assertions were made conditional, the suite stayed green, and the mutation
harness reported 5 of 8 with 2 properties silently unguarded.

THE MUTATIONS, each reverting or weakening one part of the repair:

  1. the second-person form removed entirely -- the defect as found
  2. the bracket requirement dropped, so DESCRIBING a marker reads as carrying
     one. This is the B169 defect class and the guard must refuse it.
  3. case-sensitivity forced, so `[needs your ruling]` is missed
  4. the phrase form removed, leaving only the bracketed marker

ANCHORS ARE DERIVED FROM THE SUBJECT, NEVER TYPED FROM MEMORY. Each `old` string
is asserted to appear EXACTLY ONCE before the edit; an anchor that no longer
matches is reported as a HARNESS FAILURE rather than silently skipped, which is
how 2 of 5 misses were mis-attributed on 2026-11-04.

IT RESTORES WHAT IT FOUND, verified by sha256 after every mutation, and ABORTS
rather than continuing against a corrupted subject.

★ THE HOOK SHARES AN INODE WITH ITS COPY UNDER `~/.claude/hooks/`, so a write
here is the same write there. `pathlib.write_text` truncates in place and keeps
the link; never replace the file, and never use an editor that writes a new one.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "hooks" / "work_not_narrate.py"
GUARD = "bench/tests/test_the_second_person_marker_is_his_2026-11-22.py"

#: Filled in once the widening lands: the exact alternation text added, so the
#: mutations below revert precisely it. Left as a placeholder on purpose --
#: guessing the final wording would make every anchor a HARNESS FAILURE.
ADDED = "<<<the alternation added by the widening>>>"

MUTATIONS: list[tuple[str, str, str]] = [
    ("the second-person form removed entirely", ADDED, ""),
    ("the bracket requirement dropped",
     r"\[NEEDS YOUR RULING\]", r"NEEDS YOUR RULING"),
    ("case-sensitivity forced on the new form",
     r"\[NEEDS YOUR RULING\]", r"(?-i:\[NEEDS YOUR RULING\])"),
    ("the phrase form removed", r"|AWAITING (?:HIS|YOUR) OWN FINAL RULING", ""),
]


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _guard_passes() -> bool:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", GUARD],
        cwd=REPO, capture_output=True, text=True, timeout=900)
    return r.returncode == 0


def main() -> int:
    original = SUBJECT.read_text()
    sha0 = _sha(SUBJECT)
    print(f"subject sha256 {sha0[:16]}  ({len(original)} bytes)")
    print(f"inode {SUBJECT.stat().st_ino}  links {SUBJECT.stat().st_nlink}  "
          f"(a hard link to ~/.claude/hooks means a write here is a write there)")

    if ADDED in original:
        print("\nREFUSED: the placeholder ADDED constant is still unfilled.")
        print("Fill it with the exact text the widening added, then re-run.")
        return 2

    print("\nbaseline: the guard must PASS against the unmutated subject")
    if not _guard_passes():
        print("  BASELINE RED -- either the widening has not landed yet, or the")
        print("  guard is failing for an unrelated reason. Nothing is measurable.")
        return 2
    print("  baseline green")

    red = 0
    harness_failures: list[str] = []
    print()
    for i, (name, old, new) in enumerate(MUTATIONS, start=1):
        n = original.count(old)
        if n != 1:
            harness_failures.append(f"{i}. {name}: anchor appears {n} times, not 1")
            print(f"  {i}. {name}\n     HARNESS FAILURE: anchor appears {n} times")
            continue
        try:
            SUBJECT.write_text(original.replace(old, new, 1))  # truncates in place
            noticed = not _guard_passes()
        finally:
            SUBJECT.write_text(original)
            if _sha(SUBJECT) != sha0:
                print("  RESTORE FAILED -- subject bytes differ. ABORTING.")
                return 3
        red += 1 if noticed else 0
        print(f"  {i}. {name}")
        print("     " + ("RED -- the guard noticed" if noticed
                         else "GREEN -- THE GUARD DID NOT NOTICE"))

    total = len(MUTATIONS) - len(harness_failures)
    print(f"\n{red} of {total} mutations red.")
    if harness_failures:
        print("HARNESS FAILURES (anchors that no longer match the subject):")
        for h in harness_failures:
            print(f"  {h}")
    if red == total and not harness_failures:
        print("Every reverted half of the widening is held by the guard.")
        return 0
    print("A GREEN mutation names a property the guard does not hold.")
    return 1


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
