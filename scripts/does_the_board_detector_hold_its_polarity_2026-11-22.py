#!/usr/bin/env python3
"""Does `a_commit_board_is_running` still fail toward WRITING, as it documents?

RAISED BY THE PANEL, NOT ADOPTED FROM IT. Seat cc2 reported on 2026-11-22 that
the B205(c) repair inverted this predicate's documented fail-safe direction. The
founder's standing instruction is that a panel's proposal is TESTED before it is
implemented, and a seat's verdict is not evidence here under the project's own
no-model-voting rule. So this script reproduces the claim independently instead
of taking the seat's word for either arm.

THE DOCUMENTED CONTRACT. `a_commit_board_is_running` says of itself: *"FAIL-SAFE
TOWARD WRITING: any failure of this predicate returns '', so a fault here costs
the protection and never the triage."* The two helpers it leans on document the
OPPOSITE direction, each correctly for its own caller: `_own_process_chain` is
*"FAIL-SAFE TOWARD DETECTING A BOARD"* and `cy._is_shell` returns False, *"KEEP,
fail toward refusing"*, when `ps` cannot answer.

WHY IT MATTERS BEYOND THE TRIAGE. `hooks/work_not_narrate.py` stands its ENTIRE
Stop gate down when this predicate is truthy. A predicate that over-reports a
board therefore switches off the gate that compels continued work -- disabling a
feature, which the additive standard forbids, by way of a repair whose stated
purpose was the opposite.

METHOD. `pgrep` and `ps` are both resolved from PATH, so a stub directory
prepended to PATH controls them without touching the subject. Two arms differ in
ONE variable, whether `ps` can answer:

    arm A   ps answers normally      -- `_is_shell` can see a shell is a shell
    arm B   ps exits non-zero        -- `_is_shell` returns False for everything

A real shell is planted and `pgrep` is stubbed to name only that pid, so the
only question asked is what the predicate does with a pid that is NOT a board.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys
import tempfile
import time

# `_cli_help` lives in scripts/. Located rather than assumed at a fixed depth,
# so the import works when this file is IMPORTED as well as when it is RUN.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
#: Which copy of the predicate to measure. Defaults to the working tree.
#: A second copy can be named to establish whether a defect PREDATES a
#: change -- attribution is a claim and needs its own measurement.
SUBJECT = REPO / "scripts" / "blocker_triage.py"

PROBE = r'''
import os, sys, importlib.util

os.environ.pop("CDSFL_BT_BOARD", None)
spec = importlib.util.spec_from_file_location("bt_probe", r"{subject}")
m = importlib.util.module_from_spec(spec)
sys.modules["bt_probe"] = m
spec.loader.exec_module(m)
print(repr(m.a_commit_board_is_running()))
'''


def make_stubs(d: pathlib.Path, pid: str, ps_works: bool):
    pg = d / "pgrep"
    pg.write_text(f"#!/bin/sh\necho {pid}\nexit 0\n")
    pg.chmod(0o755)
    ps = d / "ps"
    if ps_works:
        ps.write_text('#!/bin/sh\nexec /bin/ps "$@"\n')
    else:
        ps.write_text('#!/bin/sh\nexit 1\n')     # denied by policy
    ps.chmod(0o755)


def arm(label: str, pid: str, ps_works: bool) -> str:
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        make_stubs(d, pid, ps_works)
        env = dict(os.environ)
        env["PATH"] = f"{d}:{env.get('PATH','')}"
        env.pop("CDSFL_BT_BOARD", None)
        out = subprocess.run(
            [sys.executable, "-c", PROBE.format(subject=SUBJECT)],
            capture_output=True, text=True, timeout=120, env=env, cwd=REPO)
        val = (out.stdout or "").strip()
        if out.returncode != 0:
            return f"<probe failed rc={out.returncode}: {(out.stderr or '')[-200:]}>"
        return val


def main():
    global SUBJECT
    #: ★ A REAL PARSER, NOT A HAND-ROLLED argv READ — 2026-11-22.
    #: `test_operational_scripts.py` requires that an unrecognised flag be
    #: REJECTED rather than ignored, in its own words "a script that accepts
    #: `--fix-timestamps` and does nothing with it is the 118-day no-op
    #: again". The first repair reached for `answer_help(...,
    #: takes_no_arguments=False)`, which answers `--help` but accepts anything
    #: else silently, so it swapped one defect for another. argparse answers
    #: help AND refuses the unknown, which is both obligations in one object.
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.add_argument("--subject", default=None,
                    help="a second copy of blocker_triage.py to measure "
                         "instead of the working tree, for establishing "
                         "whether a defect PREDATES a change")
    args = ap.parse_args()
    if args.subject:
        SUBJECT = pathlib.Path(args.subject).resolve()
    print(f"subject: {SUBJECT}")
    # A REAL shell, so `ps -o comm=` genuinely reports one. Its command line also
    # names pytest and bench/tests, so an unstubbed pgrep would match it too.
    # ★ THE PLANT MUST STAY A SHELL, AND THE FIRST VERSION OF THIS PROBE DID
    # NOT. `/bin/zsh -c "sleep 90"` is a SINGLE command, so zsh exec-optimises
    # itself away and `ps -o comm=` reports `sleep`. Arm A then failed because
    # the plant was not a shell, not because the discriminator is broken -- a
    # probe manufacturing its own failure, which this project has recorded
    # before. A loop keeps zsh resident, and the assertion below refuses to
    # report anything unless `comm` actually says so.
    shell = subprocess.Popen(
        ["/bin/zsh", "-c",
         "while true; do sleep 1; done  # pytest -q -p no:cacheprovider bench/tests/x.py"])
    time.sleep(0.6)
    pid = str(shell.pid)
    try:
        comm = subprocess.run(["ps", "-p", pid, "-o", "comm="],
                              capture_output=True, text=True).stdout.strip()
        print(f"planted a shell at pid {pid}; `ps -o comm=` reports {comm!r}")
        if comm.strip().lstrip("-").rsplit("/", 1)[-1] not in ("zsh", "bash", "sh", "ksh", "dash"):
            print(f"PROBE INVALID: the plant is not a shell ({comm!r}); arm A would")
            print("measure the discriminator against the wrong subject.")
            return 2
        print("pgrep is stubbed to name ONLY that pid, so the sole question is")
        print("what the predicate does with a pid that is not a board.\n")

        a = arm("A", pid, ps_works=True)
        b = arm("B", pid, ps_works=False)
        print(f"  arm A, ps answers normally : {a}")
        print(f"  arm B, ps denied by policy : {b}")
        print()

        # ★ ARM C, THE ANTI-VACUITY DIRECTION. A predicate repaired by making it
        # answer '' more readily can be repaired into uselessness, and a test
        # suite that only checks the '' cases would call that a success. So a
        # REAL non-shell process is planted and must still be detected.
        board = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(90)"])
        time.sleep(0.6)
        try:
            c = arm("C", str(board.pid), ps_works=True)
        finally:
            board.terminate()
            try:
                board.wait(timeout=5)
            except Exception:                                # noqa: BLE001
                board.kill()
        print(f"  arm C, a real non-shell process : {c}")
        print()

        bad = []
        if c.strip("'\"") != str(board.pid):
            bad.append(f"arm C: a real board at pid {board.pid} was NOT detected "
                       f"(got {c}); the repair has blinded the predicate")
        if a not in ("''", '""'):
            bad.append("arm A: a real shell was reported as a running commit board "
                       "even though ps could identify it")
        if b not in ("''", '""'):
            bad.append("arm B: with ps unable to answer, the predicate returned a pid "
                       "where its own docstring promises ''")
        if bad:
            for line in bad:
                print(f"FALSIFIED — {line}")
            print("\nThe documented fail-safe direction does NOT hold.")
            return 1
        print("Arms A and B returned '' and arm C detected a real board. The "
              "documented fail-toward-writing direction holds, and the "
              "predicate has not been repaired into uselessness.")
        return 0
    finally:
        shell.terminate()
        try:
            shell.wait(timeout=5)
        except Exception:                                    # noqa: BLE001
            shell.kill()


if __name__ == "__main__":
    sys.exit(main())
