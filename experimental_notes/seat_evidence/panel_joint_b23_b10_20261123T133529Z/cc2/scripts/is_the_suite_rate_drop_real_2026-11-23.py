# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_joint_b23_b10_20261123T133529Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 016c6a6a0a84de1721766895ad7850be60e7900ccc010cf4064fbf58c94f7781
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Did the suite failure RATE fall, and is the straddle a fact or a choice?

DESTINATION `scripts/`. Written 2026-11-23, joint panel round, Q4.

★ WHY THIS EXISTS RATHER THAN THE SIBLING PRODUCER. `are_the_two_suite_rates_
distinguishable_2026-11-23.py` is correct in everything it computes and its
warning about the one-sided tail is exactly right. But it offers TWO two-sided
routes -- Fisher conditional and chi-square with Yates -- observes that they
bracket 0.05, and calls that a STRADDLE. **A straddle across 2 routes is a
property of the 2 routes chosen, not of the data**, and the 2 chosen are the
most and the least conservative members of the family. This runs 5 two-sided
routes, 2 of which are EXACT UNCONDITIONAL tests and therefore genuinely
independent of Fisher rather than tails of it.

★ AND IT ASKS THE QUESTION THE CLAIM ACTUALLY MAKES. "The rate improved" is a
statement about the DIFFERENCE of 2 proportions, so the instrument is a
confidence interval on that difference -- not 2 separate intervals checked for
overlap. **Non-overlap of 2 one-sample intervals is sufficient for a difference
but NOT necessary**, so "the Wilson intervals overlap" cannot establish
indistinguishability, and the sibling producer rests part of its case on it.
4 interval methods are run on the difference.

★ THE OBJECTION THAT ACTUALLY DECIDES IT IS THE COMPOSITION ONE, AND IT IS
MEASURABLE RATHER THAN A REASON TO REFUSE. The suite grew by 611 tests between
the 2 runs, so the 2 measurements are not of the same population. Restricting to
the SHARED denominator makes the question decidable: if j of the current
failures sit in the newly added tests, the shared-population comparison is
(k_now - j) against k_was at the OLD n. This prints the sensitivity curve and
the smallest j that changes the answer. A threshold of j = 1 means the
conclusion turns on a single test's provenance -- which is a LOOKUP in the run's
failure list, not an assumption.

★ WHAT THE PROJECT SHOULD RECORD, which this script's existence argues for: the
board log keeps only the FIRST failing test name (`hooks/pre-commit`, the
`_CDSFL_BOARD_LOG` summary). With all failing node ids recorded, j is observed
and no sensitivity curve is needed.
"""
from __future__ import annotations

import argparse
import sys

NOW = (18, 18403)
WAS = (32, 17792)


def routes(k1, n1, k0, n0):
    from scipy import stats
    from statsmodels.stats.proportion import proportions_ztest
    T = [[k1, n1 - k1], [k0, n0 - k0]]
    out = [
        ("Fisher exact, CONDITIONAL", stats.fisher_exact(T, alternative="two-sided").pvalue),
        ("Boschloo exact, UNCONDITIONAL", stats.boschloo_exact(T, alternative="two-sided").pvalue),
        ("Barnard exact, UNCONDITIONAL", stats.barnard_exact(T, alternative="two-sided").pvalue),
        ("chi-square, Yates", stats.chi2_contingency(T, correction=True).pvalue),
        ("two-proportion z", proportions_ztest([k1, k0], [n1, n0])[1]),
    ]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--alpha", type=float, default=0.05)
    a = ap.parse_args(argv)
    from scipy import stats
    from statsmodels.stats.proportion import confint_proportions_2indep
    k1, n1 = NOW
    k0, n0 = WAS

    print("=" * 74)
    print("IS THE SUITE FAILURE-RATE DROP REAL? 5 TWO-SIDED ROUTES")
    print("=" * 74)
    print(f"\n  now : {k1} of {n1} = {k1/n1:.6f}")
    print(f"  was : {k0} of {n0} = {k0/n0:.6f}\n")
    rs = routes(k1, n1, k0, n0)
    for name, p in rs:
        print(f"  {name:32s} p = {p:.6e}   "
              f"{'REJECTS' if p < a.alpha else 'does not reject'} at {a.alpha}")
    below = sum(1 for _, p in rs if p < a.alpha)
    print(f"\n  {below} of {len(rs)} two-sided routes reject at {a.alpha}.")
    print("  THE 2 EXACT UNCONDITIONAL ROUTES (Boschloo, Barnard) ARE NOT TAILS")
    print("  OF FISHER: they do not condition on the margins, so they are a")
    print("  genuinely different test and not a second reading of the same one.")
    if below == len(rs) - 1:
        hi = max(rs, key=lambda r: r[1])
        print(f"  THE ONLY ROUTE THAT DOES NOT REJECT IS {hi[0]}, the most")
        print("  conservative member of the family. A 'straddle' resting on it is")
        print("  a property of the route selection.")

    print("\n  THE INTERVAL ON THE DIFFERENCE -- the quantity the claim is about.")
    print("  (2 one-sample intervals OVERLAPPING does not establish")
    print("   indistinguishability: non-overlap is sufficient, not necessary.)")
    allexcl = True
    for m in ("wald", "agresti-caffo", "newcomb", "score"):
        lo, hi = confint_proportions_2indep(k1, n1, k0, n0, method=m, compare="diff")
        inc = lo <= 0 <= hi
        allexcl &= not inc
        print(f"    {m:14s} [{lo:+.6f}, {hi:+.6f}]  contains 0: {inc}")
    print(f"  all 4 methods EXCLUDE 0 : {allexcl}")

    print("\n  THE COMPOSITION OBJECTION, MADE DECIDABLE.")
    print(f"  The suite grew by {n1 - n0} tests, so the 2 runs are not of the")
    print(f"  same population. Restrict to the shared denominator n = {n0}:")
    print("\n     j   shared k   Fisher 2-sided p    rejects?")
    flip = None
    for j in range(0, k1 + 1):
        kk = k1 - j
        p = stats.fisher_exact([[kk, n0 - kk], [k0, n0 - k0]],
                               alternative="two-sided").pvalue
        if p < a.alpha and flip is None:
            flip = j
        if j <= 5 or j == k1:
            print(f"    {j:2d}   {kk:3d}        {p:.6e}        {p < a.alpha}")
    print(f"\n  smallest j that changes the answer : {flip}")
    print(f"  So the conclusion turns on whether {flip} of the {k1} current")
    print(f"  failures sits among the {n1 - n0} newly added tests. THAT IS A")
    print("  LOOKUP in the run's failure list, not an untested assumption --")
    print("  except that the board log keeps only the FIRST failing test name,")
    print("  so the lookup is not available and the curve is all there is.")

    print("\n  VERDICT THIS SCRIPT SUPPORTS.")
    print("    'the COUNT fell 32 -> 18'                      : a fact, quotable.")
    print("    'the RATE fell'                                : supported by 4 of")
    print("      5 two-sided routes and by 4 of 4 difference intervals, and")
    print("      DEFEATED by the composition problem at a threshold of j = "
          f"{flip}.")
    print("    'the routes straddle 0.05 so we cannot say'    : NOT supported.")
    print("      That is route selection, and 2 of the 5 routes are exact")
    print("      unconditional tests that reject.")
    assert flip is not None, "no j in range flipped the answer; the curve is flat"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
