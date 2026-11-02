#!/usr/bin/env python3
"""Does the roster-description guard bite? 3 reversions, each expected RED.

Restores the original bytes read into memory first, never `git checkout --`,
which would discard uncommitted work in the same file.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = "bench/tests/test_two_seats_cannot_share_one_description_2026-11-02.py"
RUNNER = REPO / "bench" / "reference_runner_v3.py"

MUTATIONS = [
    ("Codex described as GPT-5.5 again (the pre-ruling state)",
     '    "Codex": "GPT-5.3-codex (OpenAI)",',
     '    "Codex": "GPT-5.5 (OpenAI)",',
     "2 seats would share one description, which his 2026-09-20 ruling corrected"),
    ("Fable removed from the roster again",
     '    "Fable": "Fable 5.1 (Anthropic)",\n',
     '',
     "a dispatchable seat would describe itself in a report"),
    ("Fable present but described as the bare label",
     '    "Fable": "Fable 5.1 (Anthropic)",',
     '    "Fable": "Fable",',
     "a simulated stand-in would name no model it stood in for"),
]


def green() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description="Reverse each roster-description fix and check the guard "
                    "turns red. Restores the tree.")
    ap.parse_args()

    print("=" * 74)
    print("MUTATION TEST: 3 reversions, each expected RED")
    print("=" * 74)
    if not green():
        print("  BASELINE ALREADY RED -- fix that before mutating")
        return 1
    print("  baseline: GREEN\n")

    original = RUNNER.read_text()
    red = 0
    try:
        for name, find, repl, why in MUTATIONS:
            if find not in original:
                print(f"  [ANCHOR GONE] {name}")
                continue
            RUNNER.write_text(original.replace(find, repl, 1))
            ok = green()
            RUNNER.write_text(original)
            if ok:
                print(f"  [GREEN -- BAD] {name}\n                 {why}")
            else:
                red += 1
                print(f"  [RED  -- GOOD] {name}")
    finally:
        RUNNER.write_text(original)

    restored = green()
    print()
    print("=" * 74)
    print(f"  {red} of {len(MUTATIONS)} turned the guard RED")
    print(f"  tree restored and guard green again: {restored}")
    return 0 if (red == len(MUTATIONS) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
