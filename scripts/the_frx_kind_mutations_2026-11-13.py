#!/usr/bin/env python3
"""Revert each part of the frx repair and confirm a named test goes red.

His ruling of 2026-11-13 created `frx` for a FIX REQUEST, leaving `fr` for a
FEATURE REQUEST. 2 things had to change: the store's kind vocabulary, and the
marker's SUFFIX -- his first use was followed by " (" which the old suffix did
not admit, so the ruling that created the kind was itself unreadable.

★ RESTORES WHAT IT FOUND. The subjects are uncommitted while this runs, so
`git checkout --` would discard the repair rather than the mutation. Original
bytes are read first, written back in a `finally`, digests compared at the end.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
STORE = REPO / "bench" / "ticket_store.py"
HARVEST = REPO / "scripts" / "harvest_tickets_2026-10-17.py"
TEST = REPO / "bench" / "tests" / "test_frx_is_its_own_kind_2026-11-13.py"

MUTATIONS = [
    ("F1 remove frx from the kind vocabulary", STORE,
     'KINDS = ("fr", "frx", "pf"', 'KINDS = ("fr", "pf"',
     "the kind his ruling created does not exist"),
    ("F2 remove frx from the marker alternation", HARVEST,
     "(frx|fr|pf|qs|wr|stm)", "(fr|pf|qs|wr|stm)",
     "frx is read as fr, which is the collision he asked to end"),
    ("F3 narrow the suffix back, losing his first use", HARVEST,
     r"|\s*[(\[]|$)", r"|$)",
     "his own frx sentence becomes invisible again"),
    ("F4 let fr mean frx as well", STORE,
     '"fr", "frx", "pf"', '"frx", "frx", "pf"',
     "the feature-request kind is gone and 311 historical rows are orphaned"),
    ("F5 widen the suffix to any character", HARVEST,
     r"(?:[:\]\)]|\s*[-—]\s|\s*[(\[]|$)", r"(?:.|$)",
     "ordinary prose beginning fr becomes a marker"),
]


def _red() -> bool:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(TEST), "-x", "-q", "--no-header",
         "-p", "no:cacheprovider"],
        cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode != 0


def main() -> int:
    originals = {p: p.read_bytes() for p in (STORE, HARVEST)}
    digests = {p: hashlib.sha256(b).hexdigest() for p, b in originals.items()}
    caught = 0
    try:
        if _red():
            print("  ABORT: red before any mutation.")
            return 2
        print(f"  baseline GREEN; driving {len(MUTATIONS)} reversions\n")
        for name, path, find, repl, why in MUTATIONS:
            text = originals[path].decode()
            if text.count(find) != 1:
                print(f"  {name:48s} ANCHOR MISS ({text.count(find)})")
                continue
            path.write_text(text.replace(find, repl, 1))
            try:
                red = _red()
            finally:
                path.write_bytes(originals[path])
            caught += bool(red)
            print(f"  {name:48s} {'RED' if red else 'STILL GREEN'}")
            if not red:
                print(f"      NOT CAUGHT -- {why}")
    finally:
        for p, b in originals.items():
            p.write_bytes(b)
        bad = [p.name for p, d in digests.items()
               if hashlib.sha256(p.read_bytes()).hexdigest() != d]
        if bad:
            print(f"\n  ★ RESTORE FAILED for {bad}")
            return 3
        print(f"\n  restore verified byte-identical by SHA-256 on {len(originals)} files")
    print(f"  {caught} of {len(MUTATIONS)} reversions caught")
    return 0 if caught == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
