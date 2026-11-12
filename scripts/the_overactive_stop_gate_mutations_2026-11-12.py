#!/usr/bin/env python3
"""Revert each of the 4 fixes to the Stop gate and prove its guards go RED.

★ WHY. On 2026-11-12 he asked: *"Is the hook you are using overactive? Teminate
it and fix it if so."* and then *"It appears to firing every few seconds."* It
was. 4 faults were found and fixed, and he ruled that it may only be re-enabled
once a board is green and the fixes hold. A claim that the guards bite is a claim
about evidence, so the producer is committed beside it.

★ THE 4 FAULTS.
  B169   its residue predicate read a sentence DESCRIBING his authority over a
         KIND of thing as one CLAIMING this entry.
  B171   his mid-turn message silently discarded his own standing `d`, which is
         also why the gate's declared 40-refusal ceiling never bound.
  B173a  it named FINISHED work as "the next unstarted entry", and finished work
         can only leave OPEN via a commit, so working never cleared it.
  B173b  it never asked whether a tree write was POSSIBLE, though
         `blocker_triage.a_commit_board_is_running()` already existed.

★ 2 OF MY OWN FIXES WERE WORSE THAN THE DEFECT AND BOTH ARE PINNED AS TESTS
rather than merely described: the first B169 attempt excused any sentence citing
a rule and silenced his own merge decision by matching across a bracket; the
second checked only the first match per sentence. Both were caught by driving the
predicate over the live task list BEFORE anything was written.

★ ANCHORS DERIVED FROM THE LIVE FILE, and the restore is byte-exact AND
inode-checked, because this file shares an inode with the live Stop hook at
`~/.claude/hooks/` -- a careless restore would be a careless edit of the gate
that governs this session's own stopping.

Costs nothing but local CPU: 2 pytest files per mutation, no model dispatch.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
HOOK = REPO / "hooks" / "work_not_narrate.py"
GUARDS = [
    REPO / "bench" / "tests" / "test_work_not_narrate_hook_2026-09-10.py",
    REPO / "bench" / "tests"
    / "test_a_movable_entry_is_not_one_that_merely_asks_nothing_2026-11-12.py",
]


def mutations(src: str) -> list[tuple[str, str, str]]:
    m = []
    a = "    if _a_commit_board_is_running():\n        return 0"
    m.append(("B173b: the gate stops asking whether a tree write is possible",
              a, "    if False:\n        return 0"))

    b = '        return bool(mod.a_commit_board_is_running())'
    m.append(("B173b: the board detector always says no board is running",
              b, "        return False"))

    c = '        if worked_since and (_new or not _is_bare_question(c)):'
    m.append(("B171: the reset ignores whether his message was a bare question",
              c, "        if worked_since:"))

    d = '        return bool(stripped) and stripped.rstrip().endswith("?")'
    m.append(("B171: nothing counts as a bare question, so a `d` is always wiped",
              d, "        return False"))

    e = '        for ident in unstarted + started:'
    m.append(("B173a: finished work is named before unstarted work again",
              e, "        for ident in started + unstarted:"))

    f = '                    if _CLASS_OBJECT.search(sent):\n                        continue'
    if src.count(f) != 1:
        f = '                if m.group(0).lower().startswith("only he") \\\n                        and _CLASS_OBJECT.search(sent):\n                    continue'
    m.append(("B169: a class statement is read as a claim on the entry again",
              f, "                if False:\n                    continue"))

    g = '            for m in _HIS_RESIDUE.finditer(sent):'
    m.append(("B169: only the FIRST match per sentence is examined, which is "
              "the 2nd of my own failed attempts",
              g, "            for m in [_HIS_RESIDUE.search(sent)] if _HIS_RESIDUE.search(sent) else []:"))
    return m


def run_guards() -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-m", "pytest", *map(str, GUARDS),
                        "-q", "--no-header", "-p", "no:cacheprovider",
                        "-p", "no:randomly"],
                       capture_output=True, text=True, cwd=str(REPO))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    original = HOOK.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    ino = HOOK.stat().st_ino
    src = original.decode("utf-8")

    rc, out = run_guards()
    print(f"BASELINE: rc={rc}  "
          f"{out.strip().splitlines()[-1] if out.strip() else ''}")
    if rc != 0:
        print("REFUSED: the guards are not green before any mutation, so no "
              "kill can be attributed to a mutation.")
        return 2

    rows, applied, killed = [], 0, 0
    try:
        for name, find, repl in mutations(src):
            if src.count(find) != 1:
                rows.append((name, "NOT APPLIED",
                             f"anchor occurs {src.count(find)} times, not once"))
                continue
            applied += 1
            with open(HOOK, "w", encoding="utf-8") as fh:
                fh.write(src.replace(find, repl, 1))
            rc, out = run_guards()
            tail = out.strip().splitlines()[-1] if out.strip() else ""
            if rc != 0:
                killed += 1
                rows.append((name, "RED", tail))
            else:
                rows.append((name, "SURVIVED", tail))
    finally:
        with open(HOOK, "w", encoding="utf-8") as fh:
            fh.write(src)
        ok = hashlib.sha256(HOOK.read_bytes()).hexdigest() == sha
        same = HOOK.stat().st_ino == ino
        print(f"\nRESTORE: sha256 {'MATCHES' if ok else 'DIFFERS -- INVESTIGATE'}"
              f"  inode {'PRESERVED' if same else 'BROKEN -- THE LIVE HOOK IS UNLINKED'}")
        if not (ok and same):
            return 3

    print()
    for name, verdict, tail in rows:
        print(f"  [{verdict:11s}] {name}")
        if verdict != "RED":
            print(f"                {tail}")
    print(f"\n{killed} of {applied} applied mutation(s) RED"
          f"  ({len(rows) - applied} not applied)")
    return 0 if applied and killed == applied else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file in
    # place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    raise SystemExit(main())
