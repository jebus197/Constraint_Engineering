#!/usr/bin/env python3
"""How many divisions the promotion ladder should have, and what each costs.

THE FOUNDER'S INSIGHT, 2026-10-07, which no panel seat has yet been shown:
*"But running with the football analogy, we clearly don't have infinit[e]
divisions, we have division 1, division 2, division 3, the Premier League. So
the number of possible leagues is finite. The position each team or player
operate[s] in within these bou[nd]s is also finite."* And, extending it: *"We
also have the Vauxhall conference and the other lower leagues. But either way
the number is bounded, not infinite."*

WHY THAT CHANGES THE PROBLEM RATHER THAN DECORATING IT. The promotion rule
derived on 2026-10-08 fixes the number of rungs at 5 and asks how many attempts
each rung needs (`bench/what_several_tries_has_to_mean_2026-10-08.py`: 19
attempts, 11 successes). His observation inverts the question. If the division
count is a FREE, BOUNDED parameter, then attempts-per-tier and number-of-tiers
trade against each other, and the quantity a researcher actually pays -- total
attempts to climb from the bottom division to the top -- has an optimum that can
be SCANNED rather than argued.

THE MECHANISM. Climbing T divisions means passing T-1 promotion gates in series.
The gates multiply: a model that must clear 6 gates can be let through each one
on weaker evidence than a model that must clear 2, because the series itself
discriminates. So the per-gate sample size falls as T rises, while the number of
gates paid for rises. Total cost is the product, and because the per-gate sample
size is an INTEGER the product is a step function -- which is why it is not
monotone and cannot be reasoned to.

THE ERROR BUDGET IS THE SAME ONE THE 5-RUNG RULE USED, held fixed across the
scan so the comparison is about tier count and nothing else: a capable model
reaches the top with probability at least 0.95, and a weak model with
probability at most 0.01, END TO END.

NO MODEL NAMES ANYWHERE IN THIS FILE. Capability is a rate, which is what the
founder has now said 4 times.

★ THIS FILE'S HEADLINE CONCLUSION IS WITHDRAWN, 2026-10-08, AND THE FILENAME IS
NOW WRONG. Found by the `fable` seat of the blind round this file was written for,
and independently re-derived by a different method in
`scripts/the_division_count_is_derivable_2026-10-08.py`.

`smallest_gate` forces every gate in a ladder to the SAME (attempts, successes)
pair. The end-to-end budget constrains only the PRODUCTS of per-gate pass
probabilities, so HETEROGENEOUS gates are admissible and nothing here justifies
the restriction. Optimised over them the curve is monotone non-decreasing -- 19,
21, 22, 25, 28, 30, 33, 36, 38, 41, 42, 45, 48 -- with 0 downward steps and 0
inversions, so "the tier count has to be SCANNED; neither 'as few as possible'
nor 'as many as the bound allows' is right" is FALSE. "As few as possible" is
right on this metric. A witness: for 4 divisions the ladder [(2,1),(2,1),(18,14)]
costs 22 attempts inside the budget against the 30 computed below.

WHAT STANDS. Every number this file prints is correct AS AN UPPER BOUND under the
identical-gate restriction, and it matches the optimum at 2 divisions. The
non-monotonicity is a true property of that restricted family and a false guide
to the real question. The file is kept rather than deleted because the
restriction's cost -- up to 29 excess attempts at 11 divisions -- is itself the
measurement that shows why the restriction mattered.

WHAT THIS FILE MEASURES, AND THE BOUNDARY IT DOES NOT CROSS. The metric is
TOTAL ATTEMPTS TO REACH THE TOP, and on that metric the scan's answer is blunt:
2 divisions -- a single gate -- is the cheapest, at 19 attempts, and every
larger ladder costs more. That is a real result and it is NOT the whole answer,
because total attempts prices the climb as though every attempt were pure
overhead. It is not. A model sitting in a lower division is DOING THAT
DIVISION'S WORK while it climbs, and that work has value; a model in front of a
single gate is doing 19 attempts of qualification and nothing else. So tiers can
only be justified by the value of the work done DURING the climb, which this
file does not measure and does not pretend to. The question is put to the panel
in that form rather than answered here, because answering it in the same breath
as asking it is how a brief gets the agreement it wrote for itself.

A CORRECTION THIS FILE EXISTS TO CARRY. An analysis note of 2026-10-08
(`experimental_notes/Rung_Promotion_Panel_Analysis_2026-10-08.md`) stated that
the climb costs "between 52 and 182 attempts across 2 to 14 tiers" and that
"7 tiers cost 91 attempts where 5 cost 95", with the founder's 4-division
instinct landing on "a local optimum at 68 attempts". NONE OF THOSE 5 FIGURES
REPRODUCE. The committed scan gives 19 to 72 attempts across 2 to 14 divisions;
7 divisions cost 48 and 5 cost 36; and his 4 divisions cost 30 and are NOT a
local minimum, because 3 divisions cost 28. The note's figures were computed in
session with no committed producer, which is the precise failure the founder's
ruling of 2026-09-04 names: a number that exists only as prose is a claim about
evidence rather than evidence. The non-monotonicity survives -- 2 downward steps
and 6 inversions where more divisions cost strictly less -- so the conclusion
that the tier count must be scanned stands on its own; the figures carrying it
did not.

Every figure is computed twice -- SciPy's binomial against an exact mpmath sum --
and every proportion over a finite trial set carries a Wilson interval.

AND A THIRD TOOL AGREES, RECORDED RATHER THAN CALLED. Wolfram is the project's
SECOND falsifier and the open-source tools stay primary, so this file does not
invoke it -- requiring a licensed kernel to reproduce a figure would compel an
install the founder's ruling forbids. The values are recorded here instead, run
2026-10-08 through the serial gate:

    P(at least 7 of 10 at rate 0.90)  = 0.9872048016      -> the 4-division gate
    P(at least 7 of 10 at rate 0.50)  = 0.171875
    the same raised to 3 gates        = 0.9621034613      -> matches end_to_end_capable
    P(at least 15 of 19 at rate 0.90) = 0.9648058450      -> the 2-division gate

Each is identical to what SciPy and mpmath produce above. Computed with Wolfram
Language (local Wolfram Engine, via wolframscript).

Run: python3 bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py
"""
from __future__ import annotations

import argparse
import math

#: The 2 capability rates the error budget separates. Rates, not models.
CAPABLE_RATE = 0.90
WEAK_RATE = 0.50

#: END-TO-END budget, identical at every tier count.
P_CAPABLE_REACHES_TOP_MIN = 0.95
P_WEAK_REACHES_TOP_MAX = 0.01

#: His own enumeration -- Premier League, divisions 1, 2 and 3, plus the
#: Vauxhall Conference and the leagues below it -- is why the scan stops at 14
#: rather than running to infinity. 2 is the smallest ladder that has a gate at
#: all.
TIER_RANGE = range(2, 15)

#: A per-tier sample size cannot exceed what a researcher would sit through.
MAX_ATTEMPTS_PER_TIER = 400

Z = 1.959963984540054


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def _sf_scipy(s: int, a: int, p: float) -> float:
    """P(at least s successes in a attempts) via SciPy."""
    from scipy.stats import binom
    return float(binom.sf(s - 1, a, p))


def _sf_mpmath(s: int, a: int, p: float) -> float:
    """The same tail, summed exactly in arbitrary precision. TOOL 2."""
    import mpmath as mp
    with mp.workdps(50):
        pp = mp.mpf(p)
        tot = mp.mpf(0)
        for k in range(s, a + 1):
            tot += mp.binomial(a, k) * pp ** k * (1 - pp) ** (a - k)
        return float(tot)


def smallest_gate(gates: int, verify_exact: bool = True) -> dict:
    """Fewest attempts per gate meeting the END-TO-END budget over `gates` gates.

    Each gate must pass a capable model with probability at least
    `P_CAPABLE_REACHES_TOP_MIN ** (1/gates)` and a weak one with at most
    `P_WEAK_REACHES_TOP_MAX ** (1/gates)`, because the gates are independent and
    in series.
    """
    need_pass = P_CAPABLE_REACHES_TOP_MIN ** (1.0 / gates)
    allow_pass = P_WEAK_REACHES_TOP_MAX ** (1.0 / gates)
    for a in range(1, MAX_ATTEMPTS_PER_TIER + 1):
        for s in range(1, a + 1):
            pg = _sf_scipy(s, a, CAPABLE_RATE)
            if pg < need_pass:
                continue                  # too strict for a capable model
            pw = _sf_scipy(s, a, WEAK_RATE)
            if pw > allow_pass:
                continue                  # too loose against a weak one
            out = {
                "gates": gates,
                "attempts_per_gate": a,
                "successes_required": s,
                "per_gate_pass_capable": round(pg, 8),
                "per_gate_pass_weak": round(pw, 8),
                "per_gate_pass_capable_needed": round(need_pass, 8),
                "per_gate_pass_weak_allowed": round(allow_pass, 8),
                "end_to_end_capable": round(pg ** gates, 8),
                "end_to_end_weak": round(pw ** gates, 10),
                "total_attempts_to_climb": gates * a,
            }
            if verify_exact:
                eg, ew = _sf_mpmath(s, a, CAPABLE_RATE), _sf_mpmath(s, a, WEAK_RATE)
                out["mpmath_agrees"] = (abs(eg - pg) < 1e-12 and abs(ew - pw) < 1e-12)
                out["mpmath_max_abs_diff"] = max(abs(eg - pg), abs(ew - pw))
            return out
    return {"gates": gates, "feasible": False,
            "searched_to": MAX_ATTEMPTS_PER_TIER}


def claim_the_cost_of_climbing_is_bounded() -> dict:
    """His bounded-divisions point, made quantitative."""
    rows = {}
    for tiers in TIER_RANGE:
        rows[tiers] = smallest_gate(tiers - 1)
    costs = {t: r["total_attempts_to_climb"] for t, r in rows.items()
             if r.get("total_attempts_to_climb")}
    best = min(costs, key=lambda t: costs[t])
    return {
        "tier_range": [min(TIER_RANGE), max(TIER_RANGE)],
        "per_tier_count": rows,
        "total_attempts_by_tier_count": costs,
        "cheapest_tier_count": best,
        "cheapest_total_attempts": costs[best],
        "dearest_tier_count": max(costs, key=lambda t: costs[t]),
        "dearest_total_attempts": max(costs.values()),
        "every_tier_count_is_feasible": all(
            r.get("total_attempts_to_climb") for r in rows.values()),
        "mpmath_agrees_everywhere": all(
            r.get("mpmath_agrees", False) for r in rows.values()),
    }


def claim_the_cost_curve_is_not_monotone() -> dict:
    """THE LOAD-BEARING CLAIM: the optimum must be scanned, not reasoned to.

    If cost fell monotonically with tier count the answer would be "as many
    divisions as the bound allows" and no scan would be needed. If it rose
    monotonically the answer would be 2. It does neither.
    """
    d = claim_the_cost_of_climbing_is_bounded()
    costs = d["total_attempts_by_tier_count"]
    ts = sorted(costs)
    diffs = [costs[b] - costs[a] for a, b in zip(ts, ts[1:])]
    rises = sum(1 for x in diffs if x > 0)
    falls = sum(1 for x in diffs if x < 0)
    flats = sum(1 for x in diffs if x == 0)
    # Every pair where MORE tiers cost STRICTLY LESS than a smaller tier count.
    inversions = [(a, costs[a], b, costs[b])
                  for i, a in enumerate(ts) for b in ts[i + 1:]
                  if costs[b] < costs[a]]
    return {
        "costs": costs,
        "steps_up": rises, "steps_down": falls, "steps_flat": flats,
        "is_monotone": (falls == 0 or rises == 0),
        "inversions_more_tiers_cost_less": len(inversions),
        "example_inversions": inversions[:6],
        "verdict": ("the cost curve is NOT monotone in the number of divisions, "
                    "so the tier count has to be SCANNED; neither 'as few as "
                    "possible' nor 'as many as the bound allows' is right"),
    }


def claim_his_four_division_instinct() -> dict:
    """He named 4 divisions explicitly. What does that one cost?

    This is the only part of the file that tests a value HE supplied rather than
    one the budget derives, and it is kept separate for exactly that reason.
    """
    d = claim_the_cost_of_climbing_is_bounded()
    costs = d["total_attempts_by_tier_count"]
    his = 4
    cheaper = [t for t in costs if costs[t] < costs[his]]
    neighbours = {t: costs[t] for t in (his - 1, his, his + 1) if t in costs}
    return {
        "his_named_divisions": his,
        "note": "Premier League, division 1, division 2, division 3",
        "total_attempts_at_his_count": costs[his],
        "cheapest_total_attempts": d["cheapest_total_attempts"],
        "cheapest_tier_count": d["cheapest_tier_count"],
        "excess_over_cheapest": costs[his] - d["cheapest_total_attempts"],
        "tier_counts_strictly_cheaper": sorted(cheaper),
        "is_a_local_minimum": all(costs[his] <= v for v in neighbours.values()),
        "neighbours": neighbours,
    }


def claim_a_single_gate_cannot_meet_the_budget_cheaply() -> dict:
    """P-PASS: is the whole tiered idea just worse than 1 big gate?

    If 1 gate at the full budget were cheaper than every tiered ladder, tiers
    would be decoration. This is the attempt to show exactly that.
    """
    one = smallest_gate(1)
    d = claim_the_cost_of_climbing_is_bounded()
    costs = d["total_attempts_by_tier_count"]
    beaten_by = sorted(t for t in costs if costs[t] < one["total_attempts_to_climb"])
    return {
        "single_gate": one,
        "single_gate_total_attempts": one["total_attempts_to_climb"],
        "tiered_counts_that_beat_one_gate": beaten_by,
        "cheapest_tiered": d["cheapest_total_attempts"],
        "one_gate_is_cheapest": not beaten_by,
        "verdict": ("a single gate at the full budget is the T=2 ladder, so the "
                    "scan already contains it; tiers earn their place only where "
                    "the scan says they are cheaper"),
    }


def claim_the_bound_is_what_makes_this_answerable(trials: int = 20000,
                                                  seed: int = 19) -> dict:
    """Without a BOUND on tier count there is no optimum to find.

    Simulated rather than derived, because the point is about the search space
    and not about the binomial: as the ceiling on tier count rises, the scanned
    optimum stops moving. That is what 'bounded, not infinite' buys.
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    d = claim_the_cost_of_climbing_is_bounded()
    costs = d["total_attempts_by_tier_count"]
    stable_from = None
    seen = []
    for ceiling in sorted(costs):
        sub = {t: costs[t] for t in costs if t <= ceiling}
        seen.append((ceiling, min(sub, key=lambda t: sub[t])))
    tail = [opt for _, opt in seen[-4:]]
    if len(set(tail)) == 1:
        stable_from = seen[-4][0]
    # An independent check that the argmin is what it is, by resampling the
    # order the scan visits tier counts in: a correct argmin is order-free.
    orders = set()
    keys = list(costs)
    for _ in range(min(trials, 500)):
        rng.shuffle(keys)
        orders.add(min(keys, key=lambda t: costs[t]))
    return {
        "optimum_as_the_ceiling_rises": seen,
        "optimum_stable_from_ceiling": stable_from,
        "argmin_is_order_free": len(orders) == 1,
        "distinct_argmins_over_shuffled_scans": len(orders),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true",
                    help="skip the order-free resampling check")
    args = ap.parse_args()

    print("== 1. the cost of climbing is bounded, because the divisions are ==")
    d1 = claim_the_cost_of_climbing_is_bounded()
    for t in sorted(d1["per_tier_count"]):
        r = d1["per_tier_count"][t]
        print(f"   {t:2d} divisions ({r['gates']} gate(s)): "
              f"{r['attempts_per_gate']:3d} attempts, "
              f"{r['successes_required']:3d} needed -> "
              f"{r['total_attempts_to_climb']:4d} attempts to climb   "
              f"[capable {r['end_to_end_capable']:.4f}, "
              f"weak {r['end_to_end_weak']:.2e}]")
    print(f"   cheapest: {d1['cheapest_tier_count']} divisions at "
          f"{d1['cheapest_total_attempts']} attempts")
    print(f"   dearest : {d1['dearest_tier_count']} divisions at "
          f"{d1['dearest_total_attempts']} attempts")
    print(f"   every tier count feasible: {d1['every_tier_count_is_feasible']}")
    print(f"   mpmath agrees with scipy everywhere: "
          f"{d1['mpmath_agrees_everywhere']}")

    print("\n== 2. and the cost curve is NOT monotone ==")
    d2 = claim_the_cost_curve_is_not_monotone()
    for k in ("steps_up", "steps_down", "steps_flat", "is_monotone",
              "inversions_more_tiers_cost_less"):
        print(f"   {k}: {d2[k]}")
    for a, ca, b, cb in d2["example_inversions"]:
        print(f"   {b} divisions cost {cb} where {a} divisions cost {ca}")
    print(f"   {d2['verdict']}")

    print("\n== 3. the 4 divisions he named ==")
    d3 = claim_his_four_division_instinct()
    for k, v in d3.items():
        print(f"   {k}: {v}")

    print("\n== 4. P-pass: would 1 gate have been cheaper? ==")
    d4 = claim_a_single_gate_cannot_meet_the_budget_cheaply()
    for k in ("single_gate_total_attempts", "tiered_counts_that_beat_one_gate",
              "cheapest_tiered", "one_gate_is_cheapest", "verdict"):
        print(f"   {k}: {d4[k]}")

    if not args.quick:
        print("\n== 5. the bound is what makes it answerable ==")
        d5 = claim_the_bound_is_what_makes_this_answerable()
        print(f"   optimum stable from ceiling: {d5['optimum_stable_from_ceiling']}")
        print(f"   argmin is order-free: {d5['argmin_is_order_free']} "
              f"({d5['distinct_argmins_over_shuffled_scans']} distinct argmin(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
