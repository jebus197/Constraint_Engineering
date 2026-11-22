#!/usr/bin/env python3
"""Does the Open Brain hash chain cover a MAJORITY, and did it RISE? 2 questions.

WRITTEN 2026-11-22. **IT EXISTS BECAUSE THE FIGURES IT PRINTS WERE REAL AND HAD
NO PRODUCER.** Assertion A1 of `bench/tests/test_open_brain_assessment_2026-09-10.py`
was restated the same day from `lo < 0.5 < hi` to `lo > 0.5`, and the comment
justifying that restatement carried a Clopper-Pearson interval, a Fisher exact
p-value and a Yates chi-square p-value that **no committed script produced**.

Under `measured-rate-travels-with-its-script` a number existing only as prose in
a code comment is not evidence; it is a claim about evidence. The figures turn
out to reproduce EXACTLY, which is the point: the rule is not a suspicion that
the arithmetic is wrong, it is a requirement that it be RE-RUNNABLE. A correct
figure with no producer is still a figure nobody can check.

★ WHAT IS DELIBERATELY SPLIT HERE, because folding them is how a bigger
denominator gets reported as progress. These are 2 DIFFERENT questions:

  (1) IS THE SHARE ABOVE HALF?   -- a statement about today, answered by whether
      the interval's LOWER BOUND clears 0.5.
  (2) DID IT RISE?               -- a statement about 2 measurements, answered by
      a test between them, and NOT by either interval.

The answer to (1) is yes and the answer to (2) is NOT SHOWN. An interval that
clears 0.5 today while the comparison against the earlier measurement returns
p = 0.2 means the chain is above half AND nothing has been demonstrated to have
changed. Reporting only (1) invites the reader to supply (2) themselves.

★ THE COUNTS ARE READ FROM THE PRODUCER, NOT TYPED. `scripts/open_brain_assessment_2026-09-10.py`
prints `hashed and valid: V of T`, and this script parses that line, so the
counts cannot drift away from the instrument that measures them. The earlier
pair is a PINNED HISTORICAL OBSERVATION and is typed, because 2026-11-06's store
no longer exists to re-measure -- that asymmetry is named rather than hidden.

EVERY FIGURE ON 2 INDEPENDENT ROUTES: Wilson by `statsmodels.proportion_confint`
and by the closed form in `mpmath`; Clopper-Pearson by the beta quantile and by
inverting the EXACT binomial tails; the comparison by Fisher's exact test and by
a Yates-corrected chi-square. Disagreement between routes is printed, never
smoothed.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import mpmath as mp
import scipy.stats as st
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
PRODUCER = REPO / "scripts" / "open_brain_assessment_2026-09-10.py"

#: PINNED HISTORICAL OBSERVATION, 2026-11-06. Typed because that store state is
#: gone and cannot be re-measured. Named as a pin so it is never mistaken for a
#: live reading.
PRIOR_VALID, PRIOR_TOTAL = 125, 231
PRIOR_DATE = "2026-11-06"

mp.mp.dps = 40


def live_counts() -> "tuple[int, int]":
    """Parse `hashed and valid: V of T` out of the assessment producer."""
    r = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                       capture_output=True, text=True, timeout=900)
    m = re.search(r"hashed and valid:\s*(\d+)\s+of\s+(\d+)", r.stdout or "")
    if not m:
        raise SystemExit(
            "REFUSED: the assessment producer printed no 'hashed and valid: V of T' "
            "line, so there is no live count to measure. Nothing is assumed.")
    return int(m.group(1)), int(m.group(2))


def wilson_two_routes(v: int, t: int) -> "tuple[tuple[float, float], tuple[float, float], float]":
    lo1, hi1 = proportion_confint(v, t, method="wilson")
    z = mp.mpf(str(st.norm.ppf(0.975)))
    p, n = mp.mpf(v) / t, mp.mpf(t)
    den = 1 + z**2 / n
    ctr = (p + z**2 / (2 * n)) / den
    hw = (z / den) * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo2, hi2 = float(ctr - hw), float(ctr + hw)
    return (lo1, hi1), (lo2, hi2), max(abs(lo2 - lo1), abs(hi2 - hi1))


def clopper_two_routes(v: int, t: int):
    lo1, hi1 = proportion_confint(v, t, method="beta")

    def tail_ge(pp):
        return mp.nsum(lambda k: mp.binomial(t, int(k)) * pp**int(k) * (1 - pp)**(t - int(k)),
                       [v, t])

    def tail_le(pp):
        return mp.nsum(lambda k: mp.binomial(t, int(k)) * pp**int(k) * (1 - pp)**(t - int(k)),
                       [0, v])

    def bisect(f, target, a, b):
        for _ in range(200):
            m = (a + b) / 2
            if f(m) < target:
                a = m
            else:
                b = m
        return (a + b) / 2

    #: mpmath's `betainc` failed to converge at these parameters when this class
    #: of figure was first cross-checked on 2026-10-28, so the 2nd route inverts
    #: the exact binomial tails directly rather than calling an incomplete beta.
    lo2 = float(bisect(tail_ge, mp.mpf("0.025"), mp.mpf("0.0"), mp.mpf("1.0")))
    hi2 = float(bisect(lambda x: -tail_le(x), -mp.mpf("0.025"), mp.mpf("0.0"), mp.mpf("1.0")))
    return (lo1, hi1), (lo2, hi2), max(abs(lo2 - lo1), abs(hi2 - hi1))


def main() -> int:
    v, t = live_counts()
    (w1lo, w1hi), (w2lo, w2hi), wdiff = wilson_two_routes(v, t)
    (c1lo, c1hi), (c2lo, c2hi), cdiff = clopper_two_routes(v, t)

    print("=" * 74)
    print("IS THE HASH CHAIN MAJORITY REAL, AND DID IT RISE?")
    print("=" * 74)
    print(f"  live, read from the assessment producer : {v} of {t} = {v / t:.6f}")
    print(f"  Wilson  statsmodels : [{w1lo:.6f}, {w1hi:.6f}]")
    print(f"  Wilson  mpmath form : [{w2lo:.6f}, {w2hi:.6f}]   max abs diff {wdiff:.3e}")
    print(f"  C-P     beta        : [{c1lo:.6f}, {c1hi:.6f}]")
    print(f"  C-P     exact tails : [{c2lo:.6f}, {c2hi:.6f}]   max abs diff {cdiff:.3e}")

    print("\n  QUESTION 1 -- IS THE SHARE ABOVE HALF?")
    above = w1lo > 0.5 and c1lo > 0.5
    print(f"    Wilson lower bound {w1lo:.6f}, Clopper-Pearson lower bound {c1lo:.6f}")
    print(f"    ABOVE HALF ON BOTH ROUTES: {above}")

    tbl = [[v, t - v], [PRIOR_VALID, PRIOR_TOTAL - PRIOR_VALID]]
    odds, pf = st.fisher_exact(tbl)
    chi2v, pc, _dof, _exp = st.chi2_contingency(tbl, correction=True)
    print(f"\n  QUESTION 2 -- DID IT RISE SINCE {PRIOR_DATE}?")
    print(f"    then {PRIOR_VALID} of {PRIOR_TOTAL} = {PRIOR_VALID / PRIOR_TOTAL:.6f}   "
          f"(PINNED historical observation, not re-measurable)")
    print(f"    Fisher exact     p = {pf:.6e}   odds ratio {odds:.6f}")
    print(f"    Yates chi-square p = {pc:.6e}   chi2 {chi2v:.6f}")
    rose = bool(pf < 0.05)
    print(f"    DISTINGUISHABLE AT 0.05: {rose}")
    if not rose:
        print("    SO 'IT ROSE' MAY NOT BE SAID. The 2 measurements are not")
        print("    distinguishable. What changed is the DENOMINATOR, which narrowed")
        print("    the interval enough to clear 0.5; that is a gain in PRECISION,")
        print("    not a demonstrated gain in COVERAGE.")

    print("\n  THE 2 ANSWERS TOGETHER, which is the only honest form:")
    print(f"    above half = {above}; shown to have risen = {rose}")
    worst = max(wdiff, cdiff)
    print(f"\n  worst cross-route disagreement across all 4 interval bounds: {worst:.3e}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from _cli_help import answer_help
        answer_help(__doc__, __file__)
    except ImportError:
        pass
    sys.exit(main())
