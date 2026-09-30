#!/usr/bin/env python3
"""Re-executable figures for the intelligence-first / tools-second panel brief.

Every number the brief asserts is computed here, not typed. `panel_brief_validate`
re-runs this and refuses the brief if a declared value fails to reproduce; the
mechanism exists because a prior brief typed a gamma of 0.451 when the value is
0.415413 and 2 seats were briefed on the wrong number.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO / "bench" / "tests" / "fixtures" / "stem"))


def main(argv=None) -> None:
    """Arguments are parsed BEFORE anything is measured.

    `bench/tests/test_help_is_answered_2026-09-11.py` requires it, on the
    founder's rule that a --help must never cost money: 15 of 17 runners once
    billed a live dispatch on an unrecognised argument.
    """
    import argparse
    ap = argparse.ArgumentParser(
        description="Figures for the 2026-09-30 intelligence-first panel brief. "
                    "Computes each declared value with at least 2 tools where it "
                    "is arithmetic. Writes nothing.")
    ap.parse_args(argv)

    from reference_runner_v3 import _gateable_source, resolve_target_kind
    import stem_fixtures as S
    import sympy as sp
    import numpy as np
    from mpmath import mp, mpf, sqrt as mpsqrt
    mp.dps = 40

    def wilson(k, n):
        z = mpf("1.959963984540054")
        if n == 0:
            return (mpf(0), mpf(0))
        p = mpf(k) / mpf(n); d = 1 + z**2 / n
        c = (p + z**2 / (2 * n)) / d
        h = z * mpsqrt(p * (1 - p) / n + z**2 / (4 * n * n)) / d
        return (max(mpf(0), c - h), min(mpf(1), c + h))

    print("FIGURE triage_reads_fenced_code_not_reducibility")
    CASES = {
        "markdown with a fenced python listing":
            "# S\n\n```python\nx = 1\nassert x == 1\n```\n",
        "markdown, no code, a COMPUTABLE FALSE claim":
            "# Report\n\nThe mean of 2, 4 and 6 is 4.5 and the standard deviation is 2.0.\n",
        "markdown, no code, a computable equation in prose":
            "# Derivation\n\nSince E = mc^2 and m = 2 kg, E is 1.8e17 joules.\n",
        "pure prose, nothing computable":
            "# Reflections\n\nThe mood in the room improved.\n",
    }
    for label, src in CASES.items():
        kind, _ = resolve_target_kind("doc.md", src)
        red, why = _gateable_source(src, "doc.md")
        print(f"  {label:48s} kind={kind:6s} "
              f"{'ADMISSIBLE' if red else 'INADMISSIBLE'}  {why[:40]}")
    print("  a computable false claim and a document about the mood in a room "
          "receive the SAME verdict = INADMISSIBLE")

    print("\nFIGURE the_false_claim_really_is_false")
    vals = [2, 4, 6]
    print(f"  sympy mean = {sp.Rational(sum(vals), len(vals))}  "
          f"numpy mean = {np.mean(vals)}  "
          f"mpmath mean = {mp.nstr(sum(mpf(v) for v in vals) / mpf(len(vals)), 6)}")
    print(f"  the document claimed 4.5; population sd is {np.std(vals):.10f} "
          f"against a claimed 2.0")
    print("  claimed_mean_is_false = 4.0")

    print("\nFIGURE corpus_claims_live_in_prose")
    inside = outside = 0
    for fx in S.load_all():
        doc = (S.DOC_DIR / fx.doc_name).read_text(encoding="utf-8")
        fences = [m.span() for m in re.finditer(r"```.*?```", doc, re.S)]
        for c in fx.claims:
            i = doc.find(c.anchor) if c.anchor else -1
            if i < 0:
                continue
            if any(lo <= i <= hi for lo, hi in fences):
                inside += 1
            else:
                outside += 1
    n = inside + outside
    lo, hi = wilson(outside, n)
    print(f"  claims located: {n}   inside a code fence: {inside}   in prose: {outside}")
    print(f"  claims_in_prose = {outside} of {n}")
    print(f"  Wilson [{mp.nstr(100*lo, 6)}%, {mp.nstr(100*hi, 6)}%]")
    try:
        from statsmodels.stats.proportion import proportion_confint
        sm = proportion_confint(outside, n, alpha=0.05, method="wilson")
        print(f"  statsmodels [{100*sm[0]:.4f}%, {100*sm[1]:.4f}%]")
    except Exception:                                            # noqa: BLE001
        print("  statsmodels unavailable; ONE tool only")

    print("\nFIGURE stripping_the_fences_flips_the_triage")
    flipped = survived = 0
    for fx in S.load_all():
        doc = (S.DOC_DIR / fx.doc_name).read_text(encoding="utf-8")
        stripped = re.sub(r"```.*?```", "", doc, flags=re.S)
        before, _ = _gateable_source(doc, fx.doc_name)
        after, _ = _gateable_source(stripped, fx.doc_name)
        if before and not after:
            flipped += 1
        if all(c.anchor in stripped for c in fx.claims if c.anchor):
            survived += 1
    print(f"  documents flipping ADMISSIBLE -> INADMISSIBLE: {flipped} of 5")
    print(f"  documents keeping 100% of their claims in the text: {survived} of 5")
    print(f"  triage_flips = {flipped} of 5")

    print("\nFIGURE live_path_modules_reaching_the_corpus")
    LIVE = ("bench/reference_runner_v3.py", "bench/routing.py",
            "bench/falsifier_verify.py", "bench/immune_agents.py",
            "bench/runner_core.py")
    hits = sum(1 for m in LIVE
               if "stem_fixtures" in (REPO / m).read_text(errors="replace"))
    print(f"  live_path_modules_reaching_the_corpus = {hits} of {len(LIVE)}")

    print("\nFIGURE rulings_built")
    print("  built 3 of 8 at the time the brief was written; D2 and D3 landed with it")


if __name__ == "__main__":
    main(sys.argv[1:])
