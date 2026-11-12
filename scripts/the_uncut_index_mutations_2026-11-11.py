#!/usr/bin/env python3
"""Mutations against the uncut-index guard. Each must turn it RED.

★ IT RESTORES WHAT IT FOUND, never `git checkout --`. This project lost a
subject that way once: the harness restored the committed bytes and ate the
live edit it was testing.

★ ITS ANCHORS ARE DERIVED FROM THE SUBJECT, not typed. Each mutation locates
its target by reading the current source; a mutation whose anchor is absent is
reported as SKIPPED rather than silently counted as red, because a harness
that cannot find its target is not evidence that the target is guarded.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GEN = ROOT / "scripts" / "build_decisions_file_2026-11-07.py"
GUARD = ROOT / "bench" / "tests" / "test_his_copy_is_not_cut_to_fit_2026-11-11.py"

MUTATIONS = [
    # ★ NOT A MUTATION OF THE SIGNATURE'S ANNOTATION. The first version of this
    # harness reverted `limit: int | None` to `limit: int` and reported it as
    # NOT CAUGHT. That verdict was wrong about the guard: Python does not
    # enforce annotations at runtime, so `limit=None` still works and NOTHING
    # observable changes. A mutation that alters no behaviour cannot be caught
    # by any behavioural test, and counting it as a miss accuses a sound guard.
    # Replaced with the behavioural form of the same regression -- coercing an
    # absent limit back to the cap, which is how the defect would really return.
    ("coerce an absent limit back to the 150 cap",
     "    if limit is None or len(t) <= limit:",
     "    limit = 150 if limit is None else limit\n    if len(t) <= limit:"),
    ("reinstate the unconditional truncating return",
     "    if limit is None or len(t) <= limit:\n        return t\n    return t[:limit].rsplit(\" \", 1)[0] + \"...\"",
     "    return t if len(t) <= limit else t[:limit].rsplit(\" \", 1)[0] + \"...\""),
    ("drop the conditional at the call site",
     '        gist = (_gist(r["options"][k], limit=150 if detail else None)\n'
     '                if r["options"] else "no option recorded")',
     '        gist = _gist(r["options"][k]) if r["options"] else "no option recorded"'),
    ("invert the conditional so HIS copy is the capped one",
     '        gist = (_gist(r["options"][k], limit=150 if detail else None)\n'
     '                if r["options"] else "no option recorded")',
     '        gist = (_gist(r["options"][k], limit=None if detail else 150)\n'
     '                if r["options"] else "no option recorded")'),
]


def run_guard() -> bool:
    """True == GREEN."""
    d = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q",
                        "--no-header", "-x"],
                       capture_output=True, text=True, cwd=str(ROOT), timeout=900)
    return d.returncode == 0


def main() -> int:
    original = GEN.read_text(encoding="utf-8")
    if not run_guard():
        print("BASELINE IS RED -- fix the guard before mutating", file=sys.stderr)
        return 2
    print("baseline GREEN\n")
    red = skipped = 0
    try:
        for name, anchor, replacement in MUTATIONS:
            if anchor not in original:
                print(f"  SKIPPED  {name}\n           anchor absent from the subject")
                skipped += 1
                continue
            GEN.write_text(original.replace(anchor, replacement, 1), encoding="utf-8")
            green = run_guard()
            print(f"  {'GREEN -- NOT CAUGHT' if green else 'RED   -- caught'}  {name}")
            red += (not green)
            GEN.write_text(original, encoding="utf-8")
    finally:
        GEN.write_text(original, encoding="utf-8")
    total = len(MUTATIONS) - skipped
    print(f"\n{red} of {total} applicable mutation(s) RED "
          f"({skipped} skipped for an absent anchor)")
    assert GEN.read_text(encoding="utf-8") == original, "the subject was not restored"
    print("subject restored byte-for-byte")
    return 0 if red == total and total > 0 else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    raise SystemExit(main())
