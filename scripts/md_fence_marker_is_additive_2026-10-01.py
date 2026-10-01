#!/usr/bin/env python3
"""IS THE LIST-MARKER WIDENING OF `_MD_PY_FENCE_ANY` STRICTLY ADDITIVE?

The additive standard forbids an addition that takes something away. This file
is the committed measurement for the 2026-10-01 widening: it compares the OLD
pattern (carried here verbatim) with the LIVE one over three populations and
asserts the live one is a PROPER SUPERSET on every document, with every
previously-extracted body BYTE-IDENTICAL.

  1. the 560-shape corpus of `md_fence_orphan_dominance_2026-10-01.py`;
  2. the 3360-shape extension that varies the line-prefix axis;
  3. EVERY `.md` FILE IN THE TREE -- the population the extractor actually
     meets, and the one neither synthetic corpus stands in for.

A body that changed is the failure this guards: relaxing a closing fence can
make a non-greedy body stop EARLIER and silently truncate a listing. That is
why the relaxation is conditional on `marker` having been consumed.

Run:  python3 scripts/md_fence_marker_is_additive_2026-10-01.py
"""
from __future__ import annotations

import itertools
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: `_MD_PY_FENCE_ANY` AS IT STOOD BEFORE THE WIDENING, verbatim.
OLD = re.compile(
    r"^(?P<prefix>[ \t]*(?:>[ \t]*)*)(?P<f>```|~~~)[ \t]*(?:python|py)\b[^\n]*\n"
    r"(?P<body>.*?)^(?P=prefix)?(?P=f)",
    re.S | re.M)

ORIG_PREFIXES = ("", "  ", "\t", "> ", ">", ">  ", "> > ")
MARKERS = ("", "- ", "* ", "+ ", "1. ", "2) ")
FENCES = ("```", "~~~")
LANGS = ("python", "py", "Python", "python3", "")
ATTRS = ("", " title=x", "{.numberLines}", " linenums")
EOLS = ("\n", "\r\n")


def _doc(prefix, marker, fence, lang, attrs, eol):
    body = "x = 1" + eol + "print(x)"
    return (f"{prefix}{marker}{fence}{lang}{attrs}{eol}{body}{eol}"
            f"{prefix}{fence}{eol}")


def _bodies(pat, doc):
    return [m.group("body") for m in pat.finditer(doc)]


def _check(live, docs, label):
    """Returns (n, lost, changed). lost/changed must both be 0."""
    lost = changed = 0
    examples = []
    for name, doc in docs:
        o, w = _bodies(OLD, doc), _bodies(live, doc)
        if len(w) < len(o):
            lost += 1
            examples.append(("LOST", name))
            continue
        # every OLD body must still appear, byte-identical, in the NEW set
        for b in o:
            if b not in w:
                changed += 1
                examples.append(("CHANGED", name))
                break
    print(f"  {label:34s} n={len(docs):<6d} lost={lost:<4d} changed={changed}")
    for kind, name in examples[:5]:
        print(f"      {kind}: {name!r}")
    if len(examples) > 5:
        print(f"      ... and {len(examples) - 5} more not shown")
    return len(docs), lost, changed


def main() -> int:
    from reference_runner_v3 import _MD_PY_FENCE_ANY as LIVE

    print("IS THE LIST-MARKER WIDENING STRICTLY ADDITIVE?")
    print("=" * 74)

    orig = [(repr(s), _doc(s[0], "", *s[1:]))
            for s in itertools.product(ORIG_PREFIXES, FENCES, LANGS, ATTRS, EOLS)]
    ext = [(repr(s), _doc(*s))
           for s in itertools.product(ORIG_PREFIXES, MARKERS, FENCES, LANGS,
                                      ATTRS, EOLS)]
    md_files = sorted(REPO.rglob("*.md"))
    real = [(str(p.relative_to(REPO)),
             p.read_text(encoding="utf-8", errors="replace")) for p in md_files]

    totals = [_check(LIVE, orig, "original 560-shape corpus"),
              _check(LIVE, ext, "3360-shape extension"),
              _check(LIVE, real, "every .md file in the tree")]

    gained_real = sum(1 for _n, d in real
                      if len(_bodies(LIVE, d)) > len(_bodies(OLD, d)))
    blocks_old = sum(len(_bodies(OLD, d)) for _n, d in real)
    blocks_new = sum(len(_bodies(LIVE, d)) for _n, d in real)
    print(f"\n  real .md files gaining a listing   {gained_real} of {len(real)}")
    print(f"  python listings extracted tree-wide OLD={blocks_old} "
          f"NEW={blocks_new}  (delta {blocks_new - blocks_old:+d})")

    lost = sum(t[1] for t in totals)
    changed = sum(t[2] for t in totals)
    n = sum(t[0] for t in totals)
    print(f"\n  documents compared {n}; LOST {lost}; BODIES CHANGED {changed}")
    if lost or changed:
        raise AssertionError(
            f"the widening is NOT additive: {lost} document(s) lost a listing "
            f"and {changed} had a previously-extracted body change. Revert it.")
    print("  ADDITIVE: recognition is a superset and every prior body is "
          "byte-identical.")
    return 0


if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
