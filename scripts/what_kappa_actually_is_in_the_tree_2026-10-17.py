#!/usr/bin/env python3
"""Enumerate every `kappa` identifier in the live tree, by kind.

HIS CORRECTION, 2026-10-16: *"A code comment about the symbol kappa is false by
count, and the coherence penalty itself does appear in the tree inside a prompt
used for a mathematics audit, which both seats' comments drop."*

THE CLAIM UNDER TEST is a comment in the composer saying that every `kappa` in
the live tree is `kappa_set`, the set-level convergence metric. If true, the
symbol carries no detection-penalty meaning anywhere and the glossary's
kappa(m,g) sentence describes nothing. If false, the glossary sentence may
still be wrong for a different reason, and the comment is wrong too.

This counts rather than asserts, and it separates the 2 questions the comment
runs together: how many DISTINCT kappa identifiers exist, and whether any of
them is a coherence penalty rather than a convergence or pathology key.
"""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: Directories that are not the live tree: archived run output and caches.
SKIP = ("bench/logs", ".git", "__pycache__", "node_modules", ".cdsfl-superseded")

IDENT = re.compile(r"\bkappa[A-Za-z0-9_]*\b|\u03ba[_A-Za-z0-9]*")

#: The one meaning the glossary attributes to the symbol: a penalty on
#: effective detection, written kappa(m,g). Matched as a CALL-SHAPED use, which
#: is how the mathematics writes it, rather than as an identifier.
#:
#: BOTH SPELLINGS, CORRECTED 2026-10-17. A first version matched only the ASCII
#: word and reported the penalty meaning absent from the live tree, which would
#: have contradicted his correction. `bench/gemini_math_audit.py` writes it with
#: the GREEK letter -- 7 occurrences, 0 ASCII -- so the ASCII-only pattern read
#: a real site as empty. My instrument was wrong and his correction was right.
PENALTY = re.compile(r"(?:kappa|\u03ba)\s*\(\s*m\s*,\s*g\s*\)")

#: This script quotes the symbol in its own prose, so it would otherwise count
#: itself as a live site -- which the first run did, reporting 3 sites all of
#: which were these very lines.
SELF = Path(__file__).relative_to(REPO).as_posix()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    counts: collections.Counter = collections.Counter()
    penalty_sites: list[str] = []
    files = 0
    for path in sorted(REPO.rglob("*.py")):
        rel = path.relative_to(REPO).as_posix()
        if any(rel.startswith(s) or f"/{s}/" in f"/{rel}" for s in SKIP):
            continue
        if rel == SELF:
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        files += 1
        for m in IDENT.finditer(text):
            counts[m.group(0)] += 1
        for m in PENALTY.finditer(text):
            line = text[:m.start()].count("\n") + 1
            penalty_sites.append(f"{rel}:{line}")

    total = sum(counts.values())
    print(f"python files scanned (live tree) ..... {files}")
    print(f"kappa identifier occurrences ......... {total}")
    print(f"distinct kappa identifiers ........... {len(counts)}")
    print()
    if not a.quiet:
        print("EVERY DISTINCT IDENTIFIER, so none hides behind the total:")
        for name, n in counts.most_common():
            print(f"  {n:>5}  {name}")
    print()
    set_only = {"kappa_set"}
    others = {k: v for k, v in counts.items() if k not in set_only}
    print(f"THE COMMENT'S CLAIM: every kappa in the live tree is kappa_set.")
    print(f"  kappa_set occurrences .............. {counts.get('kappa_set', 0)}")
    print(f"  occurrences that are NOT kappa_set . {sum(others.values())}"
          f"  across {len(others)} identifiers")
    print(f"  VERDICT: {'TRUE' if not others else 'FALSE BY COUNT'}")
    print()
    print(f"THE COHERENCE PENALTY kappa(m,g), which both comments drop:")
    if penalty_sites:
        print(f"  found at {len(penalty_sites)} site(s):")
        for s in penalty_sites:
            print(f"    {s}")
        print("  So the symbol DOES carry the penalty meaning in the live tree.")
    else:
        print("  not found in the live tree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
