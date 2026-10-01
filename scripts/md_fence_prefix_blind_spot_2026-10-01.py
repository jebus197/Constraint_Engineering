#!/usr/bin/env python3
"""THE 560-SHAPE DOMINANCE CORPUS CANNOT REACH THE ONE SHAPE CLASS THAT MATTERS.

FOUND BY THE FREE PANEL, 2026-10-01, answering Q2 of the day-review brief.

`scripts/md_fence_orphan_dominance_2026-10-01.py` licenses the removal of
`_MD_PY_FENCE` with "ORPHAN-ONLY 0 of 560, Wilson [0.0000%, 0.6813%]". Attack the
ENUMERATION, not the arithmetic, as the brief asks, and the 0 is a property of
the corpus rather than of the patterns:

    ORPHAN = re.compile(r"```(?:python|py)\n(.*?)```", re.S)       # UNANCHORED
    LIVE   = r"^(?P<prefix>[ \t]*(?:>[ \t]*)*)(?P<f>```|~~~)..."   # ^-ANCHORED

The orphan is unanchored; the live pattern is `^`-anchored with a prefix group
that admits ONLY spaces, tabs and blockquote markers. An orphan-only shape
therefore requires an opening fence whose line prefix the live pattern REFUSES.
The corpus's `PREFIXES` tuple is

    ("", "  ", "\t", "> ", ">", ">  ", "> > ")

-- seven prefixes, every one of them inside `[ \t]*(?:>[ \t]*)*`. The axis that
could produce an orphan-only shape is the one axis the product does not vary.
0 of 560 was not measured; it was enumerated away.

WHAT THE CORPUS MISSES IS NOT EXOTIC. The script names its property as
"RECOGNITION over realistic markdown shapes: the document forms a design note
actually uses". A python listing inside a BULLET LIST is such a form.

AND THE CONSEQUENCE IS NOT CONFINED TO A RETIRED PATTERN. `_MD_PY_FENCE_ANY` is
live with 2 call sites, `_gateable_source` and `_gateable_hunks`. On a list-item
fence BOTH return empty, and `_gateable_source`'s empty return carries the
string "target carries no code; syntax gates not applicable" -- so a markdown
target whose python is in a list item is triaged as PURE PROSE. No syntax gate
runs on it, S_k reaches NO_SCORE, and the document is recorded as carrying no
code while carrying code. That is a wrong result from a real document form,
which is above the brief's threshold.

THIS FILE IS THE FALSIFIER AND THE MEASUREMENT. It raises AssertionError while
the blind spot is present and exits 0 once the live pattern recognises a
list-item fence. It also re-runs the dominance comparison over a corpus
EXTENDED by the missing axis, so any fix is licensed by a committed measurement
in the same shape the removal was.

Run:  python3 scripts/md_fence_prefix_blind_spot_2026-10-01.py
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

#: The removed pattern, verbatim, as `md_fence_orphan_dominance_2026-10-01.py`
#: carries it. Duplicated rather than imported for the reason that file gives:
#: a measurement about a deletion must survive the deletion.
ORPHAN = re.compile(r"```(?:python|py)\n(.*?)```", re.S)

#: THE AXIS THE DOMINANCE CORPUS DOES NOT VARY. Every entry is a line prefix a
#: real design note uses and `[ \t]*(?:>[ \t]*)*` refuses.
MARKERS = ("", "- ", "* ", "+ ", "1. ", "2) ")

#: The dominance corpus's own axes, unchanged, so the extension is a superset.
PREFIXES = ("", "  ", "\t", "> ", ">", ">  ", "> > ")
FENCES = ("```", "~~~")
LANGS = ("python", "py", "Python", "python3", "")
ATTRS = ("", " title=x", "{.numberLines}", " linenums")
EOLS = ("\n", "\r\n")


def build(prefix: str, marker: str, fence: str, lang: str, attrs: str,
          eol: str) -> str:
    """One document. `marker` is the new axis; marker="" reproduces the original."""
    body = "x = 1" + eol + "print(x)"
    return (f"{prefix}{marker}{fence}{lang}{attrs}{eol}{body}{eol}"
            f"{prefix}{fence}{eol}")


def shapes():
    return list(itertools.product(PREFIXES, MARKERS, FENCES, LANGS, ATTRS, EOLS))


def compare(live) -> dict:
    """Orphan-vs-live recognition over the EXTENDED corpus."""
    orphan_only, live_only, both, neither = [], 0, 0, 0
    for shape in shapes():
        doc = build(*shape)
        o, w = bool(ORPHAN.search(doc)), bool(live.search(doc))
        if o and w:
            both += 1
        elif o:
            orphan_only.append(shape)
        elif w:
            live_only += 1
        else:
            neither += 1
    return {"n": len(shapes()), "both": both, "orphan_only": orphan_only,
            "live_only": live_only, "neither": neither}


#: THE DOCUMENTS THE FINDING STANDS ON, AND THEIR VALIDITY IS NOT MY OPINION.
#: `markdown-it-py` (a port of the CommonMark reference implementation) and
#: `mistune` are the arbiters, per `multi_tool_crossverify`. A form is MATERIAL
#: only if a real parser extracts NON-EMPTY python from it; anything else is not
#: a listing and the live pattern is right to refuse it. Two cases are kept here
#: expressly BECAUSE they are not material, so this falsifier cannot report a
#: blind spot that is actually correct behaviour:
#:
#:   "fence after prose"  -- not a code fence at all (both parsers: 0 fences),
#:                           so the UNANCHORED orphan was WRONG to accept it.
#:   "marker, col-0 body" -- a valid fence whose content is EMPTY, because the
#:                           col-0 line closes the list item first.
CASES = {
    "marker, indented body":  "- ```python\n  x = 1\n  print(x)\n  ```\n",
    "ordered, indented body": "1. ```python\n   x = 1\n   ```\n",
    "quoted bullet, indented": "> - ```python\n>   x = 1\n>   ```\n",
    "nested under item (2sp)": "- item\n\n  ```python\n  x = 1\n  ```\n",
    "marker, col-0 body":     "- ```python\nx = 1\n```\n",
    "fence after prose":      "See: ```python\nx = 1\n```\n",
}


def parser_python_blocks(doc: str) -> list:
    """Every non-empty python listing a CommonMark parser finds. The arbiter."""
    from markdown_it import MarkdownIt
    md = MarkdownIt("commonmark")
    return [t.content for t in md.parse(doc)
            if t.type == "fence"
            and (t.info or "").strip().split(":")[0].lower()
            in ("python", "py", "python3")
            and t.content.strip()]


def mistune_python_blocks(doc: str) -> int:
    """The SECOND tool on the same question."""
    import mistune
    return len(re.findall(r'class="language-(?:python|py|python3)"',
                          mistune.html(doc)))


def main() -> int:
    from reference_runner_v3 import (_MD_PY_FENCE_ANY, _gateable_hunks,
                                     _gateable_source)

    print("DOES THE DOMINANCE CORPUS REACH THE ORPHAN-ONLY SHAPE CLASS?")
    print("=" * 74)

    r = compare(_MD_PY_FENCE_ANY)
    k, n = len(r["orphan_only"]), r["n"]
    print(f"  corpus EXTENDED by 1 axis (list markers)   {n} shapes "
          f"({len(PREFIXES)}x{len(MARKERS)}x{len(FENCES)}x{len(LANGS)}"
          f"x{len(ATTRS)}x{len(EOLS)})")
    print(f"  recognised by the ORPHAN                   {r['both'] + k}")
    print(f"  recognised by the LIVE pattern             {r['both'] + r['live_only']}")
    print(f"  ORPHAN-ONLY                                {k}"
          f"   (the original corpus reports 0 of 560)")

    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, method="wilson")
    clo, chi = proportion_confint(k, n, method="beta")
    from mpmath import mp, mpf, sqrt
    mp.dps = 50
    z = mpf("1.9599639845400542")
    p, N = mpf(k) / n, mpf(n)
    den = 1 + z**2 / N
    centre = (p + z**2 / (2 * N)) / den
    half = (z / den) * sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    m_lo, m_hi = float(max(centre - half, 0)), float(centre + half)
    print(f"    orphan-only share {k}/{n} = {k / n:.4%}")
    print(f"    Wilson 95%          [{lo:.4%}, {hi:.4%}]   (statsmodels)")
    print(f"    Wilson 95%          [{m_lo:.4%}, {m_hi:.4%}]   (mpmath 50 dps, "
          f"agrees to {max(abs(m_lo - lo), abs(m_hi - hi)):.1e})")
    print(f"    Clopper-Pearson 95% [{clo:.4%}, {chi:.4%}]")

    print("\n  THE LIVE EXTRACTOR vs TWO COMMONMARK PARSERS")
    print(f"    {'case':26s} {'md-it':6s} {'mistune':8s} {'LIVE':6s} {'gateable':9s} material")
    missed = []
    for name, doc in CASES.items():
        blocks = parser_python_blocks(doc)
        mt = mistune_python_blocks(doc)
        material = bool(blocks)
        seen = bool(_MD_PY_FENCE_ANY.search(doc))
        src, reason = _gateable_source(doc, "note.md")
        hunks = _gateable_hunks(doc, "note.md")
        if material and not seen:
            missed.append(name)
        print(f"    {name:26s} {len(blocks):<6d} {mt:<8d} {seen!s:6s} "
              f"{('None' if src is None else f'{len(hunks)} hunk'):9s} "
              f"{material!s}")
        if material and src is None:
            print(f"      -> {reason}   <-- A LISTING REPORTED AS NO CODE")
    n_material = sum(1 for d in CASES.values() if parser_python_blocks(d))
    print(f"\n    material forms (a parser extracts non-empty python): "
          f"{n_material} of {len(CASES)}")
    print(f"    of those, INVISIBLE to the live extractor: {len(missed)}")
    if n_material:
        mlo, mhi = proportion_confint(len(missed), n_material, method="wilson")
        print(f"      Wilson 95% [{mlo:.4%}, {mhi:.4%}]")

    print()
    if missed:
        print(f"  FALSIFIED: {len(missed)} of {n_material} PARSER-CONFIRMED "
              f"python listings are invisible to the live extractor.")
        for m in missed:
            print(f"    missed: {m}")
        if k:
            print(f"  And {k} of {n} extended shapes are ORPHAN-ONLY, so the "
                  f"removal's 0-of-560 is a property of the corpus.")
        raise AssertionError(
            f"_MD_PY_FENCE_ANY misses {len(missed)} realistic list-item fence "
            f"forms; {k} of {n} extended shapes are orphan-only (the committed "
            f"dominance corpus reports 0 of 560 because it never varies the "
            f"line-prefix axis)")
    print(f"  CLEAN: every form in CASES is recognised, and orphan-only is "
          f"{k} of {n} over the extended corpus.")
    return 0


if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
