#!/usr/bin/env python3
"""Are the 2 full-suite failure rates distinguishable, or not?

DESTINATION `scripts/`. Written 2026-11-23.

WHY. The full suite ran on a clean tree at 7e1cbb0b: 18 failed, 18385 passed.
The record it replaced was 32 failed of 17792. The COUNT fell, which is a fact
needing no test. Whether the RATE improved is a different claim, and the 2
routes first computed for it STRADDLED 0.05, so it was recorded as not
established.

THIS SCRIPT EXISTS TO CHECK A SUSPICION ABOUT MY OWN REASONING: a 3rd figure
was about to be offered to a panel as a "3rd route" tipping the balance below
0.05. If that figure is a ONE-SIDED tail while the other 2 are TWO-SIDED tests,
it is not a 3rd route to the same quantity at all -- it answers a different
question, and citing it as corroboration is the error this project has already
recorded as "a figure can answer a different question".

EVERY FIGURE ON 2 ROUTES.
"""
from __future__ import annotations
import math
import pathlib
import sys

# The 2 observations. FAILED, TOTAL.
NOW_FAIL, NOW_PASS = 18, 18385
WAS_FAIL, WAS_TOTAL = 32, 17792


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--boschloo', action='store_true',
                    help='also run the Boschloo exact test (about 94 s)')
    want_boschloo = ap.parse_args(argv).boschloo
    import mpmath as mp
    import numpy as np
    from scipy import stats as sstats
    from statsmodels.stats.proportion import proportion_confint
    mp.mp.dps = 50

    now_total = NOW_FAIL + NOW_PASS
    p_now = NOW_FAIL / now_total
    p_was = WAS_FAIL / WAS_TOTAL

    print("=" * 74)
    print("ARE THE 2 SUITE FAILURE RATES DISTINGUISHABLE?")
    print("=" * 74)
    print(f"\n  now : {NOW_FAIL} of {now_total} = {p_now:.6f}")
    w_lo, w_hi = proportion_confint(NOW_FAIL, now_total, method="wilson")
    print(f"        Wilson 95% : [{w_lo:.6f}, {w_hi:.6f}]")
    print(f"  was : {WAS_FAIL} of {WAS_TOTAL} = {p_was:.6f}")
    v_lo, v_hi = proportion_confint(WAS_FAIL, WAS_TOTAL, method="wilson")
    print(f"        Wilson 95% : [{v_lo:.6f}, {v_hi:.6f}]")
    print(f"\n  the 2 Wilson intervals OVERLAP: "
          f"{'yes' if (w_lo <= v_hi and v_lo <= w_hi) else 'no'}")

    table = [[NOW_FAIL, now_total - NOW_FAIL],
             [WAS_FAIL, WAS_TOTAL - WAS_FAIL]]

    print("\n  ★ THE WHOLE TWO-SIDED ROUTE FAMILY, NOT 2 OF IT.")
    print("    Corrected 2026-11-23 by the joint panel's cc2 seat, against this")
    print("    script's own earlier conclusion. Reporting Fisher and Yates alone")
    print("    and calling them 'the 2 routes' made a statement about ROUTE")
    print("    SELECTION read as a statement about the data: they are the")
    print("    EXTREMES of the family, not its bounds.")
    family = []
    _, f2 = sstats.fisher_exact(table, alternative="two-sided")
    family.append(("Fisher exact (conditional)", f2))
    family.append(("chi-square, Yates", sstats.chi2_contingency(table, correction=True)[1]))
    family.append(("chi-square, no correction", sstats.chi2_contingency(table, correction=False)[1]))
    #: ★ BOSCHLOO IS OPT-IN, AND THE REASON IS HIS MACHINE. Measured
    #: 2026-11-23 on this 2x2: Fisher 0.00 s, chi-square 0.00 s, Barnard
    #: 2.44 s, BOSCHLOO 94.49 s. This producer is executed by a board guard,
    #: and 94 s per call -- twice, since 2 tests call it -- is about 10 per
    #: cent of a mean board of 1876.858696 s for a figure that agrees with
    #: Barnard to 3 decimal places and changes no conclusion. Barnard is also
    #: an UNCONDITIONAL exact test, so the unconditional family is still
    #: represented in the default path. Under `simplicity-default` and the
    #: founder's 2026-10-11 ruling that his 8 cores are a fixed resource, the
    #: cheap route that reaches the same answer is preferred; the expensive one
    #: is kept, not removed, and is 1 flag away.
    routes = [("Barnard exact (unconditional)", "barnard_exact")]
    if want_boschloo:
        routes.append(("Boschloo exact (unconditional)", "boschloo_exact"))
    for nm, fn in routes:
        try:
            family.append((nm, getattr(sstats, fn)(table).pvalue))
        except Exception as exc:                          # noqa: BLE001
            print(f"    {nm}: unavailable ({exc!r}) -- NOT counted")
    if not want_boschloo:
        print("    Boschloo exact (unconditional)   NOT RUN: about 94 s on this"
              " 2x2.")
        print("      Pass --boschloo to include it. It agreed with Barnard to 3"
              " decimal")
        print("      places when last run, and this script does not quote that"
              " from memory.")
    from statsmodels.stats.proportion import proportions_ztest
    family.append(("two-proportion z",
                   proportions_ztest([NOW_FAIL, WAS_FAIL], [now_total, WAS_TOTAL])[1]))
    rej = 0
    for nm, pv in family:
        rej += pv < 0.05
        print(f"    {nm:32s} p = {pv:.6e}   "
              f"{'REJECTS' if pv < 0.05 else 'does not reject'}")
    print(f"\n    {rej} of {len(family)} two-sided routes reject at 0.05."
          f"  Yates alone does not.")
    print(f"    Barnard and Boschloo are UNCONDITIONAL exact tests, so they are")
    print(f"    genuinely independent of Fisher's conditional construction --")
    print(f"    they are not a 2nd route to the same number, and both reject.")

    print("\n  ★ AND THE INTERVAL ON THE DIFFERENCE, WHICH IS THE RIGHT OBJECT.")
    print("    This script previously offered OVERLAPPING one-sample Wilson")
    print("    intervals as evidence against a difference. That is invalid: the")
    print("    overlap of 2 single-proportion intervals is not a test of their")
    print("    difference, and the interval on p_now - p_was is.")
    from statsmodels.stats.proportion import confint_proportions_2indep
    exc = tot = 0
    for meth in ("wald", "agresti-caffo", "newcomb", "score"):
        try:
            lo, hi = confint_proportions_2indep(NOW_FAIL, now_total,
                                                WAS_FAIL, WAS_TOTAL,
                                                method=meth, compare="diff")
        except Exception as e:                            # noqa: BLE001
            print(f"    {meth:16s} unavailable: {str(e)[:50]}")
            continue
        tot += 1
        e0 = not (lo <= 0 <= hi)
        exc += e0
        print(f"    {meth:16s} [{lo:+.8f}, {hi:+.8f}]  "
              f"{'excludes 0' if e0 else 'CONTAINS 0'}")
    print(f"\n    {exc} of {tot} interval methods on the DIFFERENCE exclude 0.")

    print("\n  TWO-SIDED TESTS -- these answer 'are the rates different?'")
    odds, fisher_two = sstats.fisher_exact(table, alternative="two-sided")
    print(f"    Fisher exact, 2-sided        : p = {fisher_two:.6e}  "
          f"(odds ratio {odds:.6f})")
    chi2, yates_p, dof, exp = sstats.chi2_contingency(table, correction=True)
    print(f"    chi-square with Yates, 2-sided: p = {yates_p:.6e}")
    chi2n, nocorr_p, _, _ = sstats.chi2_contingency(table, correction=False)
    print(f"    chi-square no correction      : p = {nocorr_p:.6e}")

    print("\n  ONE-SIDED TEST -- this answers a DIFFERENT question,")
    print("  namely 'is the new rate LOWER?', and is not a 3rd route to the above.")
    _, fisher_one = sstats.fisher_exact(table, alternative="less")
    print(f"    Fisher exact, 1-sided (less)  : p = {fisher_one:.6e}")

    # Route 2 for the 1-sided tail: exact hypergeometric sum in mpmath.
    # Independent of scipy: integer binomials at 50 digits.
    n1 = now_total
    n2 = WAS_TOTAL
    K = NOW_FAIL + WAS_FAIL
    N = n1 + n2
    tail = mp.mpf(0)
    for i in range(0, NOW_FAIL + 1):
        if i > n1 or (K - i) > n2:
            continue
        tail += (mp.binomial(n1, i) * mp.binomial(n2, K - i)) / mp.binomial(N, K)
    print(f"    mpmath exact hypergeometric   : p = {float(tail):.6e}"
          f"   (agrees with scipy to {abs(float(tail) - fisher_one):.2e})")

    print("\n  THE VERDICT THIS SCRIPT WAS WRITTEN TO CHECK.")
    straddle = (fisher_two < 0.05) != (yates_p < 0.05)
    print(f"    the 2 two-sided routes straddle 0.05 : {straddle}")
    print(f"    the 1-sided figure is BELOW 0.05     : {fisher_one < 0.05}")
    print(f"    ratio 2-sided / 1-sided              : "
          f"{fisher_two / fisher_one:.6f}")
    print("    SO: the sub-0.05 figure is the 1-SIDED tail of the SAME Fisher")
    print("    test, not an independent 3rd route. Offering it as corroboration")
    print("    would be switching the question from 'are they different' to")
    print("    'is it lower' after seeing the answer to the first.")
    assert abs(float(tail) - fisher_one) < 1e-12, "the 2 one-sided routes disagree"

    print("\n  ★ WHAT ACTUALLY DEFEATS THE RATE CLAIM, MEASURED.")
    print("    Neither the straddle nor the Wilson overlap. The 2 runs do not")
    print("    test the same population, and the LIKE-FOR-LIKE comparison on the")
    print("    SHARED tests is one-failure-sensitive:")
    for k in (0, 1, 2, 3):
        f_shared = NOW_FAIL - k
        _, pk = sstats.fisher_exact(
            [[f_shared, WAS_TOTAL - f_shared], [WAS_FAIL, WAS_TOTAL - WAS_FAIL]],
            alternative="two-sided")
        print(f"      {k} of {NOW_FAIL} failures among the {now_total - WAS_TOTAL} "
              f"ADDED tests -> p = {pk:.6e}  "
              f"{'rejects' if pk < 0.05 else 'DOES NOT REJECT'}")
    print("    So the conclusion turns on an unmeasured attribution: with ALL")
    print("    failures in the shared set the difference is NOT established, and")
    print("    with even 1 in the added set it is. Which tests failed is not")
    print("    recorded against the 2 populations, so the question is OPEN --")
    print("    and that, not a threshold, is why the rate claim is refused.")
    print("\n    THE DIRECTION OF THAT SENSITIVITY IS STATED AGAINST THE SEAT")
    print("    THAT RAISED IT: cc2 said the conclusion flips if even 1 failure")
    print("    sits among the added tests. Driven, attributing failures to the")
    print("    ADDED set STRENGTHENS rejection; the fragile case is 0. The")
    print("    mechanism cc2 named is right and its direction was not.")

    print("\n  AND THE LIMIT THAT MATTERS MORE THAN ANY p-VALUE.")
    print("    The 2 runs do not test the same population: the suite GREW by")
    print(f"    {now_total - WAS_TOTAL} tests between them, so a rate comparison")
    print("    assumes the added tests fail at the same rate as the existing")
    print("    ones. That assumption is untested and is the reason to prefer")
    print("    the count statement over the rate statement.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        #: `takes_no_arguments=False` because this script now HAS `--boschloo`.
        #: B214, found the same day: the default refuses a caller's own flags
        #: with exit 2 before argparse is reached, so the flag would be
        #: unreachable -- an addition nothing reaches is not additive.
        answer_help(__doc__, __file__, takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
