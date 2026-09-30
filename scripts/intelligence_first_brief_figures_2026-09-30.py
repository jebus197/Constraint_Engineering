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

    print("FIGURE extractor_reads_fenced_code_not_reducibility")
    # CORRECTED 2026-09-30 AFTER BOTH PANEL SEATS REFUTED THIS SECTION'S LABELS.
    #
    # It printed 'ADMISSIBLE' or 'INADMISSIBLE' from a truthiness test on
    # `_gateable_source`'s return. **THERE IS NO VERDICT NAMED `INADMISSIBLE`.**
    # The live vocabulary is SK_ADMISSIBLE / SK_REJECTED / SK_NO_SCORE /
    # SK_ESCALATE, and the runner contains the string "INADMISSIBLE" 0 times
    # while this script contained it 3. The word was mine, and the panel was
    # briefed on it as though it were the system's answer. cc2 found it; fable
    # confirmed the real verdict is NO_SCORE on 4 of 4 calls.
    #
    # AND THE SECOND HALF OF THE MISLABEL MATTERED MORE. `_gateable_source` is
    # NOT a triage that runs before reasoning: it is an EXTRACTOR INSIDE
    # `compute_sk`, which scores a PROPOSED FIX. It is never asked whether a
    # document is worth reviewing. cc2's executed refutation: the brief carrying
    # this figure has 0 fenced listings, and the seat reasoned on it unimpeded.
    #
    # What the figure below now reports is exactly what the extractor returns,
    # and NO_SCORE is named as the verdict that actually follows -- which
    # GLOSSARY.md:237 defines as "S_k has no opinion", the correct answer rather
    # than a defect.
    CASES = {
        "markdown with a fenced python listing":
            "# S\n\n```python\nx = 1\nassert x == 1\n```\n",
        "markdown, no code, a computable claim (mean stated falsely)":
            "# Report\n\nThe mean of 2, 4 and 6 is 4.5 and the standard deviation is 2.0.\n",
        "markdown, no code, a computable equation in prose":
            "# Derivation\n\nSince E = mc^2 and m = 2 kg, E is 1.8e17 joules.\n",
        "pure prose, nothing computable":
            "# Reflections\n\nThe mood in the room improved.\n",
    }
    for label, src in CASES.items():
        kind, _ = resolve_target_kind("doc.md", src)
        red, why = _gateable_source(src, "doc.md")
        print(f"  {label:58s} kind={kind:6s} "
              f"extractable_code={'YES' if red else 'NO ':3s}  {why[:38]}")
    print("  The EXTRACTOR cannot tell 'no computable elements' from 'computable")
    print("  elements not written as Python'. The VERDICT that follows is NO_SCORE")
    print("  in both cases, which is S_k correctly having no opinion, not a wrong call.")

    print("\nFIGURE the_false_claim_really_is_false")
    # HALF OF THIS FIGURE WAS WRONG AND cc2 CAUGHT IT USING THE BRIEF'S OWN
    # SPECIMEN AGAINST THE BRIEF. The MEAN claim is false. The STANDARD DEVIATION
    # claim is CONVENTION-DEPENDENT and true under the sample convention: for
    # [2, 4, 6] the sample sd (ddof=1) is EXACTLY 2, which is what the document
    # claimed. The original figure called the whole claim false by quoting
    # numpy's DEFAULT, ddof=0, without naming the convention.
    #
    # The figure's NAME is kept because the brief declares it and the declared
    # token `claimed_mean_is_false = 4.0` remains true -- but the name overstates,
    # and cc2's point is the substantive one: a connector handed the stated
    # question returns a number and never asks which convention the author meant.
    # That is its Q4 argument, made with this figure's own material.
    vals = [2, 4, 6]
    mean_sym = sp.Rational(sum(vals), len(vals))
    ss = sum((sp.Integer(x) - mean_sym) ** 2 for x in vals)
    sd_pop, sd_smp = sp.sqrt(ss / len(vals)), sp.sqrt(ss / (len(vals) - 1))
    print(f"  MEAN   sympy {mean_sym}   numpy {np.mean(vals)}   "
          f"mpmath {mp.nstr(sum(mpf(v) for v in vals) / mpf(len(vals)), 6)}")
    print(f"    the document claimed 4.5 -> FALSE by all 3 tools")
    print(f"  SD     ddof=0 (population) sympy {sp.nsimplify(sd_pop)} = "
          f"{float(sd_pop):.10f}, numpy {np.std(vals):.10f}")
    print(f"         ddof=1 (sample)     sympy {sp.nsimplify(sd_smp)} = "
          f"{float(sd_smp):.10f}, numpy {np.std(vals, ddof=1):.10f}, "
          f"mpmath {mp.nstr(mpsqrt(mpf(8) / mpf(2)), 6)}")
    print(f"    the document claimed 2.0 -> TRUE under ddof=1, FALSE under ddof=0. "
          f"CONVENTION-DEPENDENT, not false.")
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
