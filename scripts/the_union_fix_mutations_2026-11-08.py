#!/usr/bin/env python3
"""Reverse each half of the 2026-11-08 Stop-gate repair and prove the guard reds.

A fix whose guard stays green when the fix is removed tests nothing. 4 reversions
are applied to `hooks/work_not_narrate.py`, one at a time, and
`bench/tests/test_his_command_is_the_union_over_the_turn_2026-11-08.py` must fail
for each.

ANCHORS ARE DERIVED, NOT TYPED. `feedback_a_mutation_harness_must_derive_its_anchors_2026-11-04`
records 2 of 5 misses being the probe rather than the subject, so each reversion
asserts its anchor is present before editing and asserts the text changed after.

THE SUBJECT IS RESTORED FROM BYTES HELD HERE AND VERIFIED BY SHA-256, never by
`git checkout --`, which has destroyed the file it was meant to restore
(`feedback_a_harness_must_restore_what_it_found_2026-11-01`). THE FILE IS
HARDLINKED INTO `~/.claude/hooks`, so a failed restore leaves the LIVE Stop hook
mutated: the restore is therefore verified by hash AND by inode before exit.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
HOOK = REPO / "hooks" / "work_not_narrate.py"
LIVE = pathlib.Path.home() / ".claude/hooks/work_not_narrate.py"
GUARD = REPO / "bench/tests/test_his_command_is_the_union_over_the_turn_2026-11-08.py"

#: (name, anchor that must be present, replacement, the test(s) expected to red)
MUTATIONS = [
    ("union -> last-wins",
     "        if worked_since:\n            cmds = set()\n"
     "        cmds |= set(founder_commands(c))",
     "        cmds = set(founder_commands(c))",
     "a_later_line_of_his_does_not_cancel"),
    ("drop the machine-origin rejection",
     "    if not_his(d):\n        return False\n",
     "",
     "a_notification_is_rejected"),
    ("drop the turn bound (a spent `d` leaks forward)",
     "        if worked_since:\n            cmds = set()\n",
     "",
     "work_between_his_messages_starts_a_fresh"),
    ("window stops at the first founder line (the production failure)",
     "        first = next((i for i, ln in enumerate(lines)\n"
     "                      if _looks_like_founder_line(ln)), None)\n"
     "        if first is not None and any(_looks_like_assistant_line(ln)\n"
     "                                     for ln in lines[:first]):\n"
     "            return lines",
     "        if any(_looks_like_founder_line(ln) for ln in lines):\n"
     "            return lines",
     "both_of_his_messages_are_read_across_a_chunk_boundary"),
    ("reject on an ABSENT field (fail closed, against his ruling)",
     '    if d.get("promptSource") == "system":',
     '    if d.get("promptSource") != "sdk":',
     "an_entry_with_no_provenance_fields_is_accepted"),
]


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    # ★ `--help` MUST NOT DO THE WORK. Added 2026-11-08: 8 scripts of this
    # date wrote files while answering `--help`, which
    # `bench/tests/test_help_never_acts_2026-09-11.py` forbids and which
    # `feedback_help_must_never_cost_money` records as 15 of 17 runners
    # billing for a help request. A parser is used rather than
    # `_cli_help.answer_help` because an unrecognised argument then exits 2
    # instead of being ignored, and because it cannot be made unreachable
    # under `python3 -m`, which is how 5 of 9 earlier repairs failed.
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    good = HOOK.read_bytes()
    good_sha = hashlib.sha256(good).hexdigest()
    good_ino = HOOK.stat().st_ino
    print(f"subject : {HOOK.relative_to(REPO)}")
    print(f"sha256  : {good_sha}")
    print(f"inode   : {good_ino}  (live copy: {LIVE.stat().st_ino})")
    if HOOK.stat().st_ino != LIVE.stat().st_ino:
        print("REFUSING: the repo copy and the live hook are not the same inode.")
        return 1

    base = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                          capture_output=True, text=True, cwd=REPO)
    print(f"\nbaseline: {'GREEN' if base.returncode == 0 else 'RED'} "
          f"({base.stdout.strip().splitlines()[-1] if base.stdout.strip() else ''})")
    if base.returncode != 0:
        print("REFUSING: the guard is not green before mutation.")
        return 1

    failures = []
    try:
        for name, anchor, repl, expect in MUTATIONS:
            txt = good.decode("utf-8")
            if anchor not in txt:
                failures.append(f"{name}: ANCHOR ABSENT -- the probe is wrong, not the subject")
                print(f"\n[{name}] ANCHOR ABSENT; skipped")
                continue
            mutated = txt.replace(anchor, repl, 1)
            if mutated == txt:
                failures.append(f"{name}: replacement changed nothing")
                continue
            HOOK.write_text(mutated, encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                               capture_output=True, text=True, cwd=REPO)
            red = r.returncode != 0
            named = expect in r.stdout
            tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            print(f"\n[{name}]\n  guard: {'RED' if red else 'GREEN'}   {tail}")
            print(f"  the expected test is named in the output: {named}")
            if not red:
                failures.append(f"{name}: guard stayed GREEN -- it does not test this")
            elif not named:
                failures.append(f"{name}: red, but {expect!r} is not the failing test")
            HOOK.write_text(txt, encoding="utf-8")
    finally:
        HOOK.write_bytes(good)
        back = sha(HOOK)
        same_ino = HOOK.stat().st_ino == good_ino == LIVE.stat().st_ino
        print(f"\nrestored: sha256 matches = {back == good_sha}; "
              f"inode preserved = {same_ino}")
        if back != good_sha or not same_ino:
            print("★ THE LIVE STOP HOOK MAY BE MUTATED. Restore it by hand.")
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
