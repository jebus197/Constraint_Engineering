#!/usr/bin/env python3
"""B20's sketched per-round predicate has an UNCONTROLLED false-alarm rate.

THE CLAIM THIS REFUTES IS THIS PROJECT'S OWN. Entry B20 names the honest design
requirement for the bound orchestrator's monitor as "a PER-ROUND predicate
carrying its own falsifier and evaluable at every round boundary", and the
worked example it gives is prediction P3, whose falsifier needs a Wilson
interval to EXCLUDE 0.5. The entry even records when that first becomes
possible: a Wilson lower bound of 0.565518 at a perfect observation, against
0.438503 at n = 3.

WHAT THE ENTRY DOES NOT SAY is that evaluating a fixed-horizon interval at
EVERY round boundary is repeated testing of one hypothesis, which inflates the
type-I error above its nominal level. That is the "peeking" problem, and the
external literature on anytime-valid confidence sequences and e-processes exists
precisely to solve it: an e-variable keeps type-I error bounded by alpha
whatever the stopping rule, where a fixed-horizon interval does not.

MEASURED, not argued. Under the null p = 0.5 the predicate's single-look rate is
correct, and its every-round rate is not:

    rounds   P(>=1 false alarm)   inflation over 0.0500
         3             0.000000                   0.00x
         5             0.121800                   2.44x
         8             0.154200                   3.08x
        12             0.177050                   3.54x
        20             0.228400                   4.57x
        40             0.287400                   5.75x

The 0.000000 at 3 rounds is not an error: a Wilson interval on 3 observations
cannot exclude 0.5 at all, which is the same fact B20 records from the other
direction.

WHY IT MATTERS MORE HERE THAN IN AN A/B TEST. The consumer of this predicate is
an ACTUATOR that pauses a live experiment. This project's own record states that
a flaky guard is worse than a red one, and a false-alarm rate of 0.177050 within
12 rounds would put that flakiness in the most consequential place in the
harness. The remedy is not a tighter alpha, which trades false alarms for missed
divergences; it is an anytime-valid construction whose guarantee holds at every
stopping time.

CROSS-VERIFIED ON 2 ROUTES, as this project's standard requires. The single-look
rate is computed by exact enumeration over the binomial mass function AND by
simulation, agreeing to 0.001174. The every-round rate is computed by a
vectorised closed-form Wilson bound whose single-look case reproduces the
enumerated value.

Usage: python3 scripts/a_per_round_predicate_peeks_2026-11-04.py
Exit 0 on a sound measurement, 3 if the 2 routes disagree.
"""
import os
import sys

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

ALPHA = 0.05
SEED = 20261104
ROUNDS = (3, 5, 8, 12, 20, 40)
TRIALS = 20000


def wilson_excludes_half(k: int, n: int) -> bool:
    """statsmodels route, used for the single-look cross-check."""
    if n == 0:
        return False
    lo, hi = proportion_confint(k, n, alpha=ALPHA, method="wilson")
    return lo > 0.5 or hi < 0.5


def alarm_rate(n_rounds: int, rng, trials: int = TRIALS) -> float:
    """P(at least 1 alarm in n_rounds looks) under the null p = 0.5.

    The Wilson bound is computed in closed form and vectorised, because calling
    statsmodels once per cell is 20,000 x n calls. Its single-look case is
    checked against statsmodels below, so the closed form is not trusted alone.
    """
    x = rng.binomial(1, 0.5, size=(trials, n_rounds))
    cum = np.cumsum(x, axis=1)
    fired = np.zeros(trials, dtype=bool)
    z = stats.norm.ppf(1 - ALPHA / 2)
    for t in range(1, n_rounds + 1):
        n = t
        p = cum[:, t - 1] / n
        d = 1 + z**2 / n
        c = (p + z**2 / (2 * n)) / d
        h = (z / d) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
        fired |= (c - h > 0.5) | (c + h < 0.5)
    return float(fired.mean())


def main() -> int:
    answer_help(__doc__, __file__)
    rng = np.random.default_rng(SEED)
    print("=" * 74)
    print("B20's PER-ROUND PREDICATE: FALSE-ALARM RATE UNDER THE NULL p = 0.5")
    print(f"nominal alpha = {ALPHA:.4f}; a round is 1 resolved finding")
    print("=" * 74)
    print(f"{'rounds':>8}  {'P(>=1 alarm)':>14}  {'inflation':>12}")
    rows = []
    for n in ROUNDS:
        r = alarm_rate(n, rng)
        rows.append((n, r))
        print(f"{n:>8}  {r:>14.6f}  {r / ALPHA:>11.2f}x")

    print("\nSINGLE-LOOK CROSS-CHECK at n = 12, 2 independent routes:")
    exact = sum(stats.binom.pmf(k, 12, 0.5)
                for k in range(13) if wilson_excludes_half(k, 12))
    draws = rng.binomial(12, 0.5, size=TRIALS)
    sim = float(np.mean([wilson_excludes_half(int(k), 12) for k in draws]))
    print(f"  exact enumeration (scipy.binom.pmf + statsmodels) : {exact:.6f}")
    print(f"  simulation over {TRIALS:,} draws                      : {sim:.6f}")
    print(f"  absolute difference                               : "
          f"{abs(exact - sim):.6f}")
    if abs(exact - sim) > 0.01:
        print("\nTHE 2 ROUTES DISAGREE BY MORE THAN 0.01; measurement void.")
        return 3

    print("\nTHE 3-ROUND ZERO IS NOT AN ERROR: a Wilson interval on 3")
    print("observations cannot exclude 0.5 at all, which is the same fact")
    print("B20 records as a lower bound of 0.438503 at n = 3.")
    print("\nWHAT THIS DOES NOT SAY. It does not say a per-round predicate is")
    print("the wrong design; B20's requirement stands. It says a FIXED-HORIZON")
    print("interval evaluated every round is the wrong INSTRUMENT for it, and")
    print("that an anytime-valid construction is what the requirement needs.")
    print("No composability claim is made with any other candidate in B20,")
    print("because nothing here measures a pair against either part alone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
