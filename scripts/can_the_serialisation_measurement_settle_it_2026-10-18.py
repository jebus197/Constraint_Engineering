#!/usr/bin/env python3
"""How many rounds the serialisation measurement needs -- and it is not cheap.

THE MEASUREMENT, the 13th and last outstanding item of the programme of study,
recorded in `experimental_notes/STUDY_IN_FLIGHT.json` as
`serialisation_cures_matched_failures`. Its design text: "Dispatch the free panel
BOTH WAYS on one brief -- seats in parallel, then seats serialised one at a time
-- and compare the matched failure rate." Founder ruling, 2026-10-05: "Then that
measurement should be added to our outstanding programme of study."

WHAT THIS ADDS, AND WHAT IT DELIBERATELY DOES NOT REDO. The mechanism question is
ALREADY SETTLED in the committed record by
`scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py`, which must be
read first: of the 3 co-failures that justified serialising the free seats, 2 are
both seats hitting ONE DEADLINE -- 1956.2/1956.0 at +8.68%/+8.67% of the 1800 s
cap and 902.0/902.0 at +0.22% of the 900 s cap -- and only 18.8/18.7 is genuine
simultaneity, at session-establishment time. Recomputed honestly that is 1 of 5,
Wilson [0.0362, 0.6245], one-sided exact p = 0.107550, NOT significant.

★ THIS SCRIPT EXISTS TO FALSIFY ONE SENTENCE OF THAT PRODUCER, which reads: "The
interventional test is cheap, because both seats are free." Free is not the same
as cheap. A round is free of MONEY and costs the founder's Max subscription quota
and 12 to 20 minutes per seat, and the number of rounds required is set by the
rate the parallel arm must reproduce. On the committed decomposition that rate is
1 in 68 rounds, not 3 in 68, so the experiment is about 3 times MORE expensive
than the discarded reading of the same archive implied.

AN EARLIER VERSION OF THIS SCRIPT GOT THE DECOMPOSITION WRONG and is worth
recording. It re-derived the cap check with an absolute 10-second window, which
classified 1956.0/1956.2 as "not at any recorded cap" because the overshoot is
156 s. The committed producer uses a PERCENTAGE of the cap and classifies it AT
the cap, which is the better instrument: a subprocess killed at a deadline
overshoots by its own teardown cost, and that cost scales with the deadline. The
figures below use the committed rate, 1 of 68, for that reason.

Every figure is cross-verified across scipy, statsmodels, an independent NumPy
closed form, mpmath and Wolfram (`wolframscript`), which agreed on all of them.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import mpmath as mp
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

#: 137 archived `claude_cli` seat replies, 2 free seats per round.
ROUNDS = 137 // 2
#: ★ 1, NOT 3. The committed decomposition
#: (`scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py`) attributes
#: 2 of the 3 co-failures to a shared deadline, leaving 1 genuine simultaneity.
CONTENTION_ROUNDS = 1
#: The reading this supersedes, kept so the 3x cost difference is visible.
SUPERSEDED_ROUNDS = 3
#: Observed wall-clock for one free seat on one brief, from the archive's
#: Kaplan-Meier: median 700.7 s, 90th percentile 1728.1 s.
SEAT_MINUTES = (12, 29)
SEATS = 2


def _wilson(k: int, n: int) -> tuple[float, float]:
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z, p = 1.959963984540054, k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    nlo, nhi = max(0.0, (c - h) / d), min(1.0, (c + h) / d)
    assert abs(nlo - lo) < 1e-12 and abs(nhi - hi) < 1e-12, (k, n)
    return float(lo), float(hi)


def _n_for_power(p0: float, power: float) -> int:
    return int(np.ceil(np.log(1 - power) / np.log(1 - p0)))


def _report(k: int, label: str, alpha: float) -> dict:
    p0 = k / ROUNDS
    lo, hi = _wilson(k, ROUNDS)
    n_clean = int(np.ceil(np.log(alpha) / np.log(1 - p0)))
    out = {"n_clean": n_clean,
           "n50": _n_for_power(p0, 0.50), "n80": _n_for_power(p0, 0.80)}
    p_mp = float(mp.power(mp.mpf(1) - mp.mpf(p0), n_clean))
    p_sp = float(stats.binom.pmf(0, n_clean, p0))
    print(f"{label}")
    print(f"    rate {k}/{ROUNDS} = {100 * p0:.4f}%  "
          f"Wilson [{100 * lo:.4f}%, {100 * hi:.4f}%]")
    print(f"    SERIALISED arm: a clean result is significant at n = {out['n_clean']}")
    print(f"        P(0 events | n, rate) = {p_sp:.6f} (scipy), {p_mp:.6f} (mpmath), "
          f"agreeing to {abs(p_sp - p_mp):.2e}")
    for n in (1, 5, 10):
        print(f"        at n = {n:2}: P(0 | no cure) = "
              f"{float(stats.binom.pmf(0, n, p0)):.4f}")
    print(f"    PARALLEL arm: 50% power at n = {out['n50']}, "
          f"80% power at n = {out['n80']}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--alpha", type=float, default=0.05)
    args = ap.parse_args()
    mp.mp.dps = 30

    print("READ FIRST: scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py")
    print("It establishes that 2 of the 3 co-failures are a shared deadline, not")
    print("contention, leaving 1 of 5 and p = 0.107550. This script takes that as")
    print("given and asks only what the remaining question COSTS.")
    print()
    live = _report(CONTENTION_ROUNDS,
                   "ON THE COMMITTED RATE -- 1 genuine simultaneity", args.alpha)
    print()
    old = _report(SUPERSEDED_ROUNDS,
                  "ON THE SUPERSEDED READING -- all 3 treated as contention, "
                  "shown only for contrast", args.alpha)
    print()
    print(f"THE DECOMPOSITION MAKES THE EXPERIMENT MORE EXPENSIVE, NOT LESS: "
          f"{live['n80']} rounds against {old['n80']} at 80% power, a factor of "
          f"{live['n80'] / old['n80']:.2f}.")
    print()

    print("WHAT THAT COSTS IN THE FOUNDER'S OWN RESOURCES")
    for power, n in (("50%", live["n50"]), ("80%", live["n80"])):
        lo_h = n * SEATS * SEAT_MINUTES[0] / 60.0
        hi_h = n * SEATS * SEAT_MINUTES[1] / 60.0
        print(f"    {power} power: {n:3} rounds x {SEATS} seats x "
              f"{SEAT_MINUTES[0]} to {SEAT_MINUTES[1]} min "
              f"= {lo_h:.1f} to {hi_h:.1f} hours of Max quota, serialised")
    print()
    print("THE BEST POSSIBLE 2x2 AT n = 1 PER ARM, which is the design as written")
    odds, p_f = stats.fisher_exact([[1, 0], [0, 1]], alternative="greater")
    print(f"    1 event in parallel against 0 in serialised: Fisher one-sided "
          f"p = {p_f:.4f} -- not significant even in the best case.")
    print()
    print("THE DECISION THIS LEAVES, which is the founder's and not this script's")
    print("  (a) spend the hours above for a 50% to 80% chance of 1 event; or")
    print("  (b) build the progress signal the dispatcher already names as the")
    print("      real repair -- consume the CLI's stream-json output incrementally")
    print("      so the CALL COUNT is observable mid-flight. That addresses the")
    print("      SHARED-DEADLINE mechanism, which the committed decomposition")
    print("      attributes 2 of the 3 co-failures to, and leaves only the")
    print("      establishment collision for scheduling to explain; or")
    print("  (c) accept the stagger on the evidence already in hand, which the")
    print("      2026-10-07 producer concludes is at least as well supported as")
    print("      the full lock and strictly cheaper.")
    print()
    print("Wolfram attribution: the binomial figures above were independently")
    print("reproduced with wolframscript on 2026-10-18 -- n = 203 and 47 and 109")
    print("on the committed rate, and 67 and 16 and 36 on the superseded one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
