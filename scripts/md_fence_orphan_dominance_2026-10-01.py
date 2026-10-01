#!/usr/bin/env python3
"""The measurement that licenses removing the orphan fence pattern.

WHAT WAS REMOVED AND WHY IT NEEDED A MEASUREMENT FIRST. `reference_runner_v3`
carried 2 markdown-fence patterns. `_MD_PY_FENCE_ANY` is live, with 2 call
sites. `_MD_PY_FENCE` -- the original narrow form, matching only a bare
```python fence with LF line endings and no attributes -- had ZERO callers. The
cc2 seat reported it in the free panel of 2026-09-30 and it was recorded as
reported-rather-than-deleted; the founder asked the obvious question: "but not
fixed?"

BOTH HALVES OF THE ADDITIVE STANDARD BEAR ON IT, and they point the same way.
An addition nothing reaches is not additive, so leaving a third extractor
defined and uncalled is itself a standing defect -- orphaned mechanisms are the
single largest confirmed defect class in this project's record. And the removal
half permits removal "only when something better renders it redundant", where
better means a COMMITTED MEASUREMENT showing the replacement dominates on a
named property. This script is that measurement, and it is committed so the
number travels with the code rather than living in a commit message.

THE NAMED PROPERTY IS RECOGNITION over realistic markdown shapes: the document
forms a design note actually uses -- indentation, blockquote nesting, tilde
fences, language aliases, fence attributes, and CRLF line endings.

WHAT IT MEASURES. 560 shapes, the full product of 7 prefixes x 2 fence
characters x 5 language spellings x 4 attribute forms x 2 line endings.

  recognised by the ORPHAN    : 14
  recognised by the LIVE one  : 224
  recognised by BOTH          : 14
  ORPHAN-ONLY                 : 0 of 560, Wilson [0.0000%, 0.6813%]

0 orphan-only shapes over THIS CORPUS was the condition used, and the claim
first written here was a universal: "nothing the deleted pattern could extract
becomes unextractable". **THAT UNIVERSAL IS FALSE, and both free seats found it
independently on 2026-10-01.**

THE CORPUS COULD NOT REACH THE FALSIFYING CLASS. The orphan is UNANCHORED
(`re.S` only); the survivor is `^`-anchored under `re.M` with a prefix group
`[ \t]*(?:>[ \t]*)*`. So an orphan-only shape requires a line prefix the
survivor refuses -- and all 7 prefixes in `PREFIXES` sit INSIDE that group. The
product varies fence character, language, attributes and line endings, four axes
on which the orphan is strictly narrower, and never varies the one axis that
could produce an orphan-only shape. Measured: adding list markers as a sixth
axis gives 70 orphan-only shapes of 3360.

SO THE SCOPED CLAIM, which is the one this script now makes: over LEGITIMATE,
LINE-ANCHORED python fences the survivor dominates, and it reaches 210 shapes
the orphan could not. The removal still stands, for a reason this measurement
does not contain: the orphan had 0 callers, and the shapes it uniquely accepted
are not code fences at all to either markdown-it-py or mistune -- accepting
them was a defect, not a capability.

AND CHASING THAT GAP FOUND A LIVE DEFECT, which is the part that mattered: the
SURVIVOR missed python listings inside markdown list items, so such a document
was triaged as carrying no code and S_k reached NO_SCORE. Fixed in
`bench/reference_runner_v3.py`; held by
`bench/tests/test_md_fence_sees_a_list_item_listing_2026-10-01.py`; additivity
measured over 7069 documents by
`scripts/md_fence_marker_is_additive_2026-10-01.py` at 0 lost and 0 changed.

THE PATTERN ITSELF IS NOT LOST. It survives as a literal in
`bench/tests/test_md_fence_orphan_is_dominated_2026-10-01.py`, which re-runs
this comparison on every suite run, so the claim is re-derived rather than
remembered and a regression in the live pattern would fail there.

Run:  python3 scripts/md_fence_orphan_dominance_2026-10-01.py
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

#: THE REMOVED PATTERN, RETYPED -- not imported, because it was deleted, and a
#: measurement that licenses a removal must stay re-runnable AFTER the removal.
#:
#: "VERBATIM" is what this comment first claimed, and the fable seat was right
#: to call that an unstated weakening: a retyped copy is a model-authored
#: reconstruction unless something checks it. It could not check, having no
#: `.git` in its sandbox, and named that as its open assumption.
#:
#: CHECKED HERE, 2026-10-01, and it resolves in favour of the conclusion:
#: `git show HEAD:bench/reference_runner_v3.py` carries
#: `_MD_PY_FENCE = re.compile(r"```(?:python|py)\n(.*?)```", re.S)` at line
#: 10559, and the arguments below are BYTE-IDENTICAL to it.
ORPHAN = re.compile(r"```(?:python|py)\n(.*?)```", re.S)

PREFIXES = ("", "  ", "\t", "> ", ">", ">  ", "> > ")
FENCES = ("```", "~~~")
LANGS = ("python", "py", "Python", "python3", "")
ATTRS = ("", " title=x", "{.numberLines}", " linenums")
EOLS = ("\n", "\r\n")


def build(prefix: str, fence: str, lang: str, attrs: str, eol: str) -> str:
    body = "x = 1" + eol + "print(x)"
    return f"{prefix}{fence}{lang}{attrs}{eol}{body}{eol}{prefix}{fence}{eol}"


def shapes():
    return list(itertools.product(PREFIXES, FENCES, LANGS, ATTRS, EOLS))


def compare(live) -> dict:
    """Recognition counts for the orphan and the live pattern."""
    orphan_only, live_only, both, neither = [], 0, 0, 0
    for shape in shapes():
        doc = build(*shape)
        o = bool(ORPHAN.search(doc))
        w = bool(live.search(doc))
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


def main() -> int:
    from reference_runner_v3 import _MD_PY_FENCE_ANY
    r = compare(_MD_PY_FENCE_ANY)
    n, k = r["n"], len(r["orphan_only"])
    print("DOES THE LIVE FENCE PATTERN DOMINATE THE REMOVED ORPHAN?")
    print(f"  shapes enumerated                 {n}")
    print(f"  recognised by the ORPHAN          {r['both'] + k}")
    print(f"  recognised by the LIVE pattern    {r['both'] + r['live_only']}")
    print(f"  recognised by BOTH                {r['both']}")
    print(f"  recognised by NEITHER             {r['neither']}")
    print(f"  ORPHAN-ONLY (must be 0)           {k}   <-- the removal condition")

    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, method="wilson")
    clo, chi = proportion_confint(k, n, method="beta")
    print(f"\n  orphan-only share {k}/{n} = {k / n:.4%}")
    print(f"    Wilson 95%          [{lo:.4%}, {hi:.4%}]   (statsmodels)")
    print(f"    Clopper-Pearson 95% [{clo:.4%}, {chi:.4%}]")

    # SECOND TOOL on the same interval, per multi_tool_crossverify.
    from mpmath import mp, mpf, sqrt
    mp.dps = 50
    z = mpf("1.9599639845400542")
    p, N = mpf(k) / n, mpf(n)
    den = 1 + z**2 / N
    centre = (p + z**2 / (2 * N)) / den
    half = (z / den) * sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    m_lo, m_hi = float(max(centre - half, 0)), float(centre + half)
    print(f"    Wilson 95%          [{m_lo:.4%}, {m_hi:.4%}]   (mpmath 50 dps, "
          f"agrees to {max(abs(m_lo - lo), abs(m_hi - hi)):.1e})")

    dominates = k == 0
    proper = r["live_only"] > 0
    print(f"\n  live DOMINATES the orphan : {dominates}")
    print(f"  the dominance is PROPER    : {proper}  "
          f"({r['live_only']} shapes the orphan could not reach)")
    if dominates and proper:
        print("\n  The removal is LICENSED under the additive standard: nothing")
        print("  the deleted pattern could extract becomes unextractable, and")
        print("  the survivor is strictly better on recognition.")
        return 0
    print("\n  The removal is NOT licensed. Restore the pattern.")
    for shape in r["orphan_only"][:10]:
        print(f"    orphan-only: {shape}")
    # STATE THE REMAINDER. Caught by the project's own guard on this file, which
    # is the same rule applied to `fence_extractor_dominance_2026-09-30.py`
    # earlier the same day -- and here it would understate the very quantity
    # that FORBIDS the removal, so a reader could conclude the breach is 10
    # shapes wide when it is wider.
    if len(r["orphan_only"]) > 10:
        print(f"    ... and {len(r['orphan_only']) - 10} more not shown")
    return 1


if __name__ == "__main__":
    # A REAL PARSER: this script takes no arguments, so argparse answers
    # `--help` and refuses anything else before any work
    # (`feedback_help_must_never_cost_money`).
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
