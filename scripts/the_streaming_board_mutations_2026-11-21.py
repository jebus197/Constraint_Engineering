#!/usr/bin/env python3
"""MUTATIONS FOR THE BOARD'S STREAMING GUARD PHASE (entry B202).

Each mutation reverses ONE property the guard claims. The headline mutation is
the `| tee` form, because that is the repair a reader would reach for and it
silently disables the gate -- a mutation harness that cannot catch the plausible
wrong fix is not protecting anything.

Anchors are derived by searching the live hook, never typed as line numbers, and
the original bytes are captured and restored rather than recovered by checkout.

Exit 0 only when every mutation turns the guard red.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "pre-commit"
GUARD = "bench/tests/test_the_boards_guard_phase_streams_2026-11-21.py"

MUTATIONS: list[tuple[str, str, str, str]] = [
    (
        "back to the capturing form",
        'tail -n +1 -f "$_CDSFL_BOARD_LOG" >&2 &\n_CDSFL_TAIL_PID=$!\n'
        'python3 -u -m pytest -q -p no:cacheprovider $GUARDS >> "$_CDSFL_BOARD_LOG" 2>&1',
        '_CDSFL_TAIL_PID=$$\n'
        'python3 -u -m pytest -q -p no:cacheprovider $GUARDS >> "$_CDSFL_BOARD_LOG" 2>&1',
        "output is observable before the child exits",
    ),
    (
        "the plausible wrong fix: pipe through tee",
        'python3 -u -m pytest -q -p no:cacheprovider $GUARDS >> "$_CDSFL_BOARD_LOG" 2>&1',
        'python3 -u -m pytest -q -p no:cacheprovider $GUARDS 2>&1 | tee -a "$_CDSFL_BOARD_LOG" >&2',
        "the exit code is the child's own",
    ),
    (
        "unbuffered python dropped",
        "python3 -u -m pytest -q -p no:cacheprovider $GUARDS",
        "python3 -m pytest -q -p no:cacheprovider $GUARDS",
        "redirected stdout does not block-buffer the progress away",
    ),
    (
        "the follower is killed before the exit code is captured",
        'CODE=$?\n# The tail is killed before anything reads $CODE',
        'kill "$_CDSFL_TAIL_PID" 2>/dev/null\nCODE=$?\n# The tail is killed before anything reads $CODE',
        "the order is: capture CODE, kill the follower, then read OUT",
    ),
    (
        "the capture is dropped so the downstream greps see nothing",
        'OUT=$(cat "$_CDSFL_BOARD_LOG" 2>/dev/null)',
        'OUT=""',
        "the captured text is what the downstream greps read",
    ),
    (
        "the committed measurement is no longer named",
        "scripts/the_board_can_stream_without_losing_its_verdict_2026-11-21.py",
        "a measurement taken at the time",
        "the measurement behind the choice is committed",
    ),
]


def run_guard() -> tuple[int, str]:
    pr = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", GUARD],
                        capture_output=True, text=True, cwd=ROOT)
    return pr.returncode, (pr.stdout.strip().splitlines() or ["<none>"])[-1]


def main(argv=None) -> int:
    #: `--help` answers with a usage line and runs NOTHING, per
    #: `bench/tests/test_help_is_answered_2026-09-11.py`. This harness mutates a
    #: live source file and runs pytest once per mutation, so a `--help` that
    #: did the work would edit the tree to answer a question about itself.
    argparse.ArgumentParser(
        description=__doc__.splitlines()[0]).parse_args(argv)
    original = HOOK.read_text(encoding="utf-8")
    try:
        rc, tail = run_guard()
        print(f"BASELINE: rc={rc}  {tail}")
        if rc != 0:
            print("!! the guard is red before any mutation")
            return 1
        red = 0
        for name, find, repl, prop in MUTATIONS:
            n = original.count(find)
            if n != 1:
                print(f"  [ANCHOR] {name}: found {n} times, expected 1 — "
                      f"the probe is broken, not the hook")
                continue
            HOOK.write_text(original.replace(find, repl, 1), encoding="utf-8")
            syn = subprocess.run(["sh", "-n", str(HOOK)], capture_output=True, text=True)
            rc, tail = run_guard()
            HOOK.write_text(original, encoding="utf-8")
            ok = rc != 0
            red += ok
            print(f"  [{'RED  ' if ok else 'GREEN'}] {name}"
                  f"{'  (and the shell no longer parses)' if syn.returncode else ''}")
            print(f"           reverses: {prop}")
            if not ok:
                print(f"           !! guard stayed green: {tail}")
        print(f"\n{red} of {len(MUTATIONS)} mutations turned the guard red")
        rc, tail = run_guard()
        print(f"RESTORED: rc={rc}  {tail}")
        return 0 if (red == len(MUTATIONS) and rc == 0) else 1
    finally:
        if HOOK.read_text(encoding="utf-8") != original:
            HOOK.write_text(original, encoding="utf-8")
            print("(hook restored in the finally block)")


if __name__ == "__main__":
    raise SystemExit(main())
