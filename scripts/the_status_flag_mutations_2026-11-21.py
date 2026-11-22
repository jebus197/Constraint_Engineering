#!/usr/bin/env python3
"""MUTATIONS FOR THE DECISION INDEX'S STATUS FLAG (his Desktop copy, 2026-11-21).

The mutation that matters most is the LENGTH ONE: reverting his copy to the full
render. That is the repair the defect invites and it undoes his own 2026-11-08
workload ruling, so a harness that does not catch it is not protecting the right
property. `test_his_copy_is_not_cut_to_fit_2026-11-11.py` is run alongside the
new guard for exactly that reason -- a fix for one of his rulings must not break
the other.

Anchors are searched for in the live file; the original bytes are captured and
restored rather than recovered by checkout.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "scripts" / "build_decisions_file_2026-11-07.py"
GUARDS = [
    "bench/tests/test_his_copy_carries_the_entrys_status_2026-11-21.py",
    "bench/tests/test_his_copy_is_not_cut_to_fit_2026-11-11.py",
]

MUTATIONS: list[tuple[str, str, str, str]] = [
    (
        "the flag is never computed",
        '        flag = status_flag(r["ident"], r, _states)',
        '        flag = ""',
        "his copy carries the flag in plain words",
    ),
    (
        "a dead premise is no longer recognised",
        'if "PREMISE OF THIS ENTRY NO LONGER HOLDS" in what:',
        'if "PREMISE OF THIS ENTRY HAS NEVER BEEN WRITTEN THIS WAY" in what:',
        "a dead premise is flagged from the row's own text",
    ),
    (
        "built-or-better no longer counts as built",
        '_BUILT_OR_BETTER = ("BUILT", "TESTED", "COMMITTED", "ENABLED")',
        '_BUILT_OR_BETTER = ("ENABLED",)',
        "every BUILT-or-better status is flagged",
    ),
    (
        "the status is flagged on CLOSED entries too",
        'if state == "OPEN" and status in _BUILT_OR_BETTER:',
        'if status in _BUILT_OR_BETTER:',
        "a closed entry is not flagged",
    ),
    (
        "the markdown surface loses the flag, so the 2 surfaces disagree",
        '        _mflag = f" **[{flag.upper()}]**" if flag else ""',
        '        _mflag = ""',
        "the markdown surface carries the same count",
    ),
    (
        "the spoken surface gains markdown decoration",
        '                + (f"{flag[0].upper()}{flag[1:]}. " if flag else "")',
        '                + (f"**[{flag.upper()}]**. " if flag else "")',
        "his copy stays free of markdown decoration",
    ),
    (
        "the status is re-derived instead of read from the canonical parser",
        "        return {e.ident: (e.state, e.status) for e in tlm.parse_entries()}",
        "        return {e.ident: (e.state, e.status) for e in tlm.parse_entries()[:5]}",
        "the states come from the canonical parser",
    ),
    (
        "★ his copy is reverted to the FULL render (undoes his workload ruling)",
        "    tts_index = render(mrb, rows, spoken=True, detail=False)",
        "    tts_index = render(mrb, rows, spoken=True, detail=True)",
        "his copy is still the index and not the full render",
    ),
]


def run_guards() -> tuple[int, str]:
    pr = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", *GUARDS],
                        capture_output=True, text=True, cwd=ROOT)
    return pr.returncode, (pr.stdout.strip().splitlines() or ["<none>"])[-1]


def main(argv=None) -> int:
    #: `--help` answers with a usage line and runs NOTHING, per
    #: `bench/tests/test_help_is_answered_2026-09-11.py`. This harness mutates a
    #: live source file and runs pytest once per mutation, so a `--help` that
    #: did the work would edit the tree to answer a question about itself.
    argparse.ArgumentParser(
        description=__doc__.splitlines()[0]).parse_args(argv)
    original = SUBJECT.read_text(encoding="utf-8")
    try:
        rc, tail = run_guards()
        print(f"BASELINE: rc={rc}  {tail}")
        if rc != 0:
            print("!! guards red before any mutation")
            return 1
        red = 0
        for name, find, repl, prop in MUTATIONS:
            n = original.count(find)
            if n != 1:
                print(f"  [ANCHOR] {name}: found {n} times, expected 1")
                continue
            SUBJECT.write_text(original.replace(find, repl, 1), encoding="utf-8")
            rc, tail = run_guards()
            SUBJECT.write_text(original, encoding="utf-8")
            ok = rc != 0
            red += ok
            print(f"  [{'RED  ' if ok else 'GREEN'}] {name}")
            print(f"           reverses: {prop}")
            if not ok:
                print(f"           !! guards stayed green: {tail}")
        print(f"\n{red} of {len(MUTATIONS)} mutations turned the guards red")
        rc, tail = run_guards()
        print(f"RESTORED: rc={rc}  {tail}")
        return 0 if (red == len(MUTATIONS) and rc == 0) else 1
    finally:
        if SUBJECT.read_text(encoding="utf-8") != original:
            SUBJECT.write_text(original, encoding="utf-8")
            print("(subject restored in the finally block)")


if __name__ == "__main__":
    raise SystemExit(main())
