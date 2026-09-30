#!/usr/bin/env python3
"""COMMITTED MEASUREMENT for the additive standard's removal clause: does
`_MD_PY_FENCE_ANY` (reference_runner_v3) DOMINATE `_PY_FENCE` (bugzilla_loop)
on the named property FENCE SHAPES RECOGNISED?

Run from the repository root:

    python3 scripts/fence_extractor_dominance_2026-09-30.py

The additive standard forbids removing a feature unless a committed
measurement shows the replacement dominates on a NAMED property. The proposed
change -- bugzilla_loop stops carrying its own regex and calls the runner's
extractor -- is a REMOVAL of a live code path, so it needs this.

NAMED PROPERTY: `recognises(extractor, document)`.
DOMINANCE CLAIM: over the full cartesian product of realistic fence shapes,
    recognised(B) is a SUBSET of recognised(A), and the subset is PROPER.
That is the exact condition under which B is redundant: B recognises nothing
A misses, and A recognises shapes B misses.

FALSIFIED (AssertionError) iff dominance FAILS -- i.e. some shape B recognises
and A does not, or the two sets are equal so the replacement is not better.
Exits cleanly iff dominance HOLDS, because in that case there is no defect to
report and the removal is licensed.

NOTE THE INVERTED POLARITY, deliberately. This script's clean exit is the
RESULT WANTED. It is written as a falsifier of the DOMINANCE claim so that a
failure of the claim is loud, per the rule that a verdict must be computed and
not asserted.
"""
from __future__ import annotations

import itertools
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

PREFIXES = ["", "  ", "    ", "> ", ">  "]
FENCES = ["```", "~~~"]
LANGS = ["python", "py", "Python", "python3", "", "{python}"]
ATTRS = ["", ' title="a.py"', " {.numberLines}"]
EOLS = ["\n", "\r\n"]


def build(prefix, fence, lang, attrs, eol):
    body = f"{prefix}x = 1"
    return eol.join([
        "# D", "",
        f"{prefix}{fence}{lang}{attrs}",
        body,
        f"{prefix}{fence}",
        "",
    ])


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Cartesian dominance measurement over fence shapes. "
                    "Writes nothing.")
    ap.parse_args(argv)

    from reference_runner_v3 import _gateable_source
    from bugzilla_loop import _PY_FENCE

    only_a, only_b, both, neither = [], [], [], []
    cases = list(itertools.product(PREFIXES, FENCES, LANGS, ATTRS, EOLS))
    for shape in cases:
        doc = build(*shape)
        a = _gateable_source(doc, "doc.md")[0] is not None
        b = bool(_PY_FENCE.findall(doc))
        tag = f"prefix={shape[0]!r} fence={shape[1]} lang={shape[2]!r} " \
              f"attrs={shape[3]!r} eol={'CRLF' if shape[4]=='\r\n' else 'LF'}"
        (both if (a and b) else only_a if a else only_b if b else neither
         ).append(tag)

    n = len(cases)
    print(f"shapes enumerated               {n}")
    print(f"  recognised by BOTH            {len(both)}")
    print(f"  recognised by A only          {len(only_a)}")
    print(f"  recognised by B only          {len(only_b)}   <-- must be 0")
    print(f"  recognised by NEITHER         {len(neither)}")
    print(f"\n  |recognised(A)| = {len(both)+len(only_a)}"
          f"   |recognised(B)| = {len(both)+len(only_b)}")

    if only_b:
        print("\nSHAPES B RECOGNISES AND A DOES NOT (dominance breakers):")
        for t in only_b[:10]:
            print("   ", t)

    subset = (len(only_b) == 0)
    proper = (len(only_a) > 0)
    print(f"\n  recognised(B) subset of recognised(A) = {subset}")
    print(f"  the subset is PROPER                  = {proper}")

    # Second, independent tool on the same counts: an exact binomial-free
    # combinatorial check plus a Wilson interval on the coverage gap, so the
    # proportion travels with an interval per `measured-rate-travels-with-its-script`.
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(len(only_a), n, method="wilson")
        print(f"  A-only coverage = {len(only_a)}/{n} "
              f"statsmodels Wilson [{lo*100:.4f}%, {hi*100:.4f}%]")
    except ImportError:
        print("  statsmodels unavailable; interval not computed")
    try:
        from mpmath import mpf, sqrt as msqrt
        z = mpf("1.959963984540054"); p = mpf(len(only_a)) / mpf(n)
        d = 1 + z**2 / n; c = (p + z**2 / (2 * n)) / d
        h = z * msqrt(p * (1 - p) / n + z**2 / (4 * n * n)) / d
        print(f"  mpmath  Wilson [{float(c-h)*100:.4f}%, {float(c+h)*100:.4f}%]"
              f"   (independent recomputation)")
    except ImportError:
        print("  mpmath unavailable")

    if subset and proper:
        print("\nDOMINANCE HOLDS. B recognises nothing A misses, and A "
              "recognises shapes B misses. The removal clause is satisfied: "
              "bugzilla_loop's private `_PY_FENCE` is redundant and may be "
              "replaced by a call to the runner's extractor.")
        print("NOT FALSIFIED")
        return 0

    print("\nFALSIFIED")
    raise AssertionError(
        f"dominance fails: {len(only_b)} shape(s) recognised by B and not by "
        f"A; proper-subset={proper}. The removal is NOT licensed."
    )


if __name__ == "__main__":
    sys.exit(main())
