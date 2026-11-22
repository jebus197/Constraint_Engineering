#!/usr/bin/env python3
"""Would the guard NOTICE if the restore helper stopped restoring?

DRAFTED 2026-11-22; destination `scripts/`. Run it after `_restore.py` and its
guard are promoted into `bench/tests/`.

SUBJECT: `bench/tests/_restore.py`.
GUARD:   `bench/tests/test_a_restore_returns_the_timestamp_too_2026-11-22.py`.

A suite says whether the code passes. A harness says whether the suite would
notice if it stopped. This project has been caught by the difference: 3
assertions were made conditional, the suite stayed green, and the harness
reported 5 of 8 with 2 properties silently unguarded.

THE 5 MUTATIONS, each a way this helper could plausibly be written wrong:

  1. the `os.utime` call removed -- the defect as found in 81 guards
  2. the stamp applied BEFORE the write instead of after, so the write undoes
     it. This is the ordering hazard the helper's own comment names, and it is
     the one that fails without raising.
  3. a file created inside the block recreated EMPTY instead of removed, so a
     path every later reader treats as real is left behind
  4. `is_restored` reduced to a bytes check -- the weak form that let this class
     stay invisible in 81 guards for months
  5. the restore moved out of the `finally`, so an exception skips it entirely

ANCHORS ARE DERIVED FROM THE SUBJECT. Each `old` is asserted to appear EXACTLY
ONCE before the edit; one that no longer matches is reported as a HARNESS FAILURE
rather than silently skipped.

IT RESTORES WHAT IT FOUND, verified by sha256 after every mutation, and ABORTS
rather than continuing against a corrupted subject. The irony of a harness that
fails to restore the file teaching restoration is not lost, and is why the check
is unconditional.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "bench" / "tests" / "_restore.py"
GUARD = "bench/tests/test_a_restore_returns_the_timestamp_too_2026-11-22.py"

MUTATIONS: list[tuple[str, str, str]] = [
    ("the os.utime call removed -- the defect as found",
     "            os.utime(p, times)",
     "            pass  # mutation: timestamp not restored"),
    ("the stamp applied BEFORE the write, so the write undoes it",
     "            if p.read_bytes() != original:\n"
     "                p.write_bytes(original)\n"
     "            os.utime(p, times)",
     "            os.utime(p, times)\n"
     "            if p.read_bytes() != original:\n"
     "                p.write_bytes(original)"),
    ("a file created inside recreated EMPTY instead of removed",
     "            p.unlink(missing_ok=True)",
     '            p.write_bytes(b"")'),
    ("is_restored reduced to a bytes check",
     "    st = p.stat()\n"
     "    return abs(st.st_mtime - times[1]) <= mtime_tolerance",
     "    return True  # mutation: the weak form"),
    ("the restore moved out of the finally",
     "    finally:\n"
     "        if not existed:",
     "    except BaseException:\n"
     "        raise\n"
     "    else:\n"
     "        if not existed:"),
]


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _guard_passes() -> bool:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", GUARD],
        cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode == 0


def main() -> int:
    if not SUBJECT.is_file():
        print(f"REFUSED: no subject at {SUBJECT}.")
        print("Promote `_restore.py` into bench/tests/ first; there is nothing to mutate.")
        return 2

    original = SUBJECT.read_text()
    sha0 = _sha(SUBJECT)
    print(f"subject sha256 {sha0[:16]}  ({len(original)} bytes)")

    print("\nbaseline: the guard must PASS against the unmutated helper")
    if not _guard_passes():
        print("  BASELINE RED -- nothing here is measurable. Stop.")
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
            SUBJECT.write_text(original.replace(old, new, 1))
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
        print("Every way this helper could stop restoring is held by the guard.")
        return 0
    print("A GREEN mutation names a property the guard does not hold.")
    return 1


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__)
    except ImportError:
        pass
    sys.exit(main())
