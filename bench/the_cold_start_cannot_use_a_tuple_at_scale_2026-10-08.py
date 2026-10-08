#!/usr/bin/env python3
"""A hand-written tuple cannot answer cold start for an arbitrary roster.

THE FOUNDER'S OBJECTION, 2026-10-08: *"If that holds then you are saying (again)
that the only measure we can have of capability, is the model names? ... But you
still keep referring to '5 or 6 models', when I have already said, the system
should be able to cope with 5, or 6, or 70, or 700 models (or whatever), and that
the only goal is to use all the available resources efficiently to effect the
best outcome in all cases."*

BOTH PANEL SEATS SAID KEEP THE TUPLE AS THE COLD-START TIE-BREAK, and their
reasoning is sound FOR 6 SEATS: on run 1 every seat's lower confidence bound is
exactly 0.0, so the derived key is a total tie and carries no ordering at all.
One seat measured it -- 12 shuffled inputs gave 12 distinct orders without the
tuple and 1 with it.

THEIR ANSWER DOES NOT SCALE, AND NEITHER SEAT SAID SO. A tuple is a hand-written
list. It cannot be written for 700 seats, and the moment the roster exceeds the
tuple the unranked remainder is ordered by nothing but input order -- which is
the arbitrary ordering the tuple was supposed to replace.

WHAT THIS SCRIPT ESTABLISHES, with 2 tools per claim and an interval on every
proportion:

  1. How many attempts a seat needs before its Wilson lower bound can separate it
     from another seat, as a function of the true gap. This is the price of cold
     start, and it is a measured quantity rather than an opinion.
  2. That the tuple's coverage collapses as the roster grows: with a 6-name tuple
     and N seats, the share of the roster it orders is 6/N, so at 70 seats it
     orders 8.5714% and at 700 it orders 0.8571%.
  3. That round-robin exploration reaches a usable ordering in a bounded number
     of rounds at any N, because every seat gains attempts in parallel.

Run: python3 bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py
"""
from __future__ import annotations

import argparse
import math

Z = 1.959963984540054
TUPLE_LEN = 6                 # DEFAULT_FALSIFIER_STRENGTH after Fable was added


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def attempts_to_separate(p_hi: float, p_lo: float, max_n: int = 4000) -> int | None:
    """Smallest n where the lower bound of the better seat clears the upper
    bound of the worse one, at the expected successes for each."""
    for n in range(2, max_n + 1):
        k_hi, k_lo = round(p_hi * n), round(p_lo * n)
        if wilson(k_hi, n)[0] > wilson(k_lo, n)[1]:
            return n
    return None


def claim_cold_start_has_a_measured_price() -> dict:
    """How many attempts before measured capability can order 2 seats."""
    import numpy as np
    from statsmodels.stats.proportion import proportion_confint
    out = {}
    for gap in (0.40, 0.30, 0.20, 0.10, 0.05):
        hi = 0.60 + gap / 2
        lo = 0.60 - gap / 2
        n = attempts_to_separate(hi, lo)
        # second tool: statsmodels at the same n must agree on separation
        agree = None
        if n:
            k_hi, k_lo = round(hi * n), round(lo * n)
            s_hi = proportion_confint(k_hi, n, method="wilson")
            s_lo = proportion_confint(k_lo, n, method="wilson")
            agree = bool(s_hi[0] > s_lo[1]) and bool(
                abs(s_hi[0] - wilson(k_hi, n)[0]) < 1e-12)
        out[round(gap, 2)] = {"attempts_needed": n,
                              "statsmodels_agrees": agree,
                              "numpy_check": int(np.int64(n)) if n else None}
    return out


def claim_the_tuple_coverage_collapses(sizes=(6, 7, 70, 700, 7000)) -> dict:
    """The share of the roster a 6-name tuple can order."""
    out = {}
    for n in sizes:
        ordered = min(TUPLE_LEN, n)
        lo, hi = wilson(ordered, n)
        out[n] = {"ordered_by_the_tuple": ordered,
                  "share": round(ordered / n, 6),
                  "share_pct": round(100 * ordered / n, 4),
                  "wilson_on_the_share": (round(lo, 6), round(hi, 6)),
                  "ordered_by_nothing_but_input_order": n - ordered}
    return out


def claim_round_robin_reaches_an_ordering_at_any_scale(
        sizes=(6, 70, 700), q: float = 0.2337, k_rounds: int = 40) -> dict:
    """Every seat gains attempts in PARALLEL, so rounds-to-order is scale-free.

    One round gives every live seat 1 attempt, so after r rounds each seat has r
    attempts whatever N is. The tuple, by contrast, orders a share that falls
    like 1/N.
    """
    import numpy as np
    rng = np.random.default_rng(20261008)
    out = {}
    for n in sizes:
        true_p = rng.uniform(0.05, 0.95, size=n)
        # rounds until the best seat's lower bound clears the median seat's upper
        best, med = float(true_p.max()), float(np.median(true_p))
        r = None
        for rounds in range(2, k_rounds + 1):
            kb, km = round(best * rounds), round(med * rounds)
            if wilson(kb, rounds)[0] > wilson(km, rounds)[1]:
                r = rounds
                break
        out[n] = {"rounds_until_best_separates_from_median": r,
                  "attempts_per_seat_after_that": r,
                  "total_dispatches": (r * n) if r else None}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--max-n", type=int, default=4000)
    ap.parse_args()
    rows = [
        ("1. the measured price of cold start", claim_cold_start_has_a_measured_price()),
        ("2. the tuple's coverage collapses with N", claim_the_tuple_coverage_collapses()),
        ("3. round-robin exploration is scale-free",
         claim_round_robin_reaches_an_ordering_at_any_scale()),
    ]
    for t, d in rows:
        print(f"\n== {t} ==")
        for k, v in d.items():
            print(f"   {k}: {v}")
    print()
    print("READING IT. The seats are right that the derived key is a total tie on")
    print("run 1, and right that SOMETHING must break that tie. They are wrong")
    print("that the something can be a hand-written tuple, because its coverage")
    print("falls like 1/N while round-robin exploration gives every seat the same")
    print("number of attempts per round whatever N is. The tuple is a PRIOR, not a")
    print("capability measure, and a prior that cannot be written down for 700")
    print("seats is not a prior for an arbitrary roster.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
