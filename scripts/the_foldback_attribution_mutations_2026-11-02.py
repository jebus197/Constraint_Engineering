#!/usr/bin/env python3
"""Does the fold-back attribution guard bite? 3 reversions, each expected RED.

Restores the original bytes read into memory first, never `git checkout --`.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = "bench/tests/test_a_foldback_credits_the_origin_not_the_copy_2026-11-02.py"
PV = REPO / "bench" / "proof_verify.py"
G = REPO / GUARD

MUTATIONS = [
    ("the origin credit is removed from the folded-back file", PV,
     "★ AUTHORED BY panel seat `cc2`, corrected 2026-11-02: the byte-identical",
     "★ Corrected 2026-11-02: the byte-identical",
     "the file would credit only the copy it was drawn from"),
    ("the authorship pattern widens back to any mention", G,
     'r"(written by|taken from the copy[^.]{0,40}?under|authored by)"\n'
     '    r"[^.]{0,80}?\\b(cc2|fable|gemini|codex|chatgpt|deepseek)\\b", re.I)',
     'r"()"\n'
     '    r"[^.]{0,0}?\\b(cc2|fable|gemini|codex|chatgpt|deepseek)\\b", re.I)',
     "a bare mention would count as an authorship claim and the "
     "'First reported by' false positive would return"),
    ("the pattern loses case-insensitivity", G,
     'r"[^.]{0,80}?\\b(cc2|fable|gemini|codex|chatgpt|deepseek)\\b", re.I)',
     'r"[^.]{0,80}?\\b(cc2|fable|gemini|codex|chatgpt|deepseek)\\b")',
     "a correction written in capitals would not be seen, which is the "
     "defect this pattern was fixed for"),
]


def green() -> bool:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description="Reverse each attribution fix and check the guard turns red. "
                    "Restores the tree.")
    ap.parse_args()

    print("=" * 74)
    print("MUTATION TEST: 3 reversions, each expected RED")
    print("=" * 74)
    if not green():
        print("  BASELINE ALREADY RED -- fix that first")
        return 1
    print("  baseline: GREEN\n")

    originals = {PV: PV.read_text(), G: G.read_text()}
    red = 0
    try:
        for name, path, find, repl, why in MUTATIONS:
            src = originals[path]
            if find not in src:
                print(f"  [ANCHOR GONE] {name}")
                continue
            path.write_text(src.replace(find, repl, 1))
            ok = green()
            path.write_text(src)
            if ok:
                print(f"  [GREEN -- BAD] {name}\n                 {why}")
            else:
                red += 1
                print(f"  [RED  -- GOOD] {name}")
    finally:
        for path, text in originals.items():
            path.write_text(text)

    restored = green()
    print()
    print("=" * 74)
    print(f"  {red} of {len(MUTATIONS)} turned the guard RED")
    print(f"  tree restored and guard green again: {restored}")
    return 0 if (red == len(MUTATIONS) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
