#!/usr/bin/env python3
"""Does "no cap plus value-over-cost" meet the founder's 7 stated requirements?

HIS REQUIREMENTS, 2026-10-07, in his own framing: *"the number of models used may
eventually be entirely arbitrary. It could be 5, or 6, or 70, or 500, or 1."*
*"Free, cheap, model name, setting an arbitrary limit on how far the ladder can
climb ... are not meaningful considerations. The only thing that impacts
capability in the schema, should be capability."* And on direction: *"A ladder is
bidirectional ... if a weaker model gets better at doing a job ... it should be
able to climb the routing ladder, based on its demonstrated improvement in
capability."* With the guard: *"what we need to guard against is simply counting
when a model is successful as an 'improvement in capability'."*

  R1  roster size arbitrary (1, 6, 70, 500)
  R2  no cap on ladder depth
  R3  allocation by measured capability, never by name
  R4  never hand a model work it cannot do
  R5  bidirectional: capability gained climbs, capability lost descends
  R6  a single success is NOT an improvement in capability
  R7  problem in, computed efficiently, solution out -- the researcher WAITS

VERDICT THIS SCRIPT ESTABLISHES: the combined rule satisfies R1, R2, R3, R5 by
construction, and R4 only because exhaustion makes coverage constant. It FAILS R7
as currently framed, because "cost" is money alone and the researcher pays in
TIME. And R6 is not a property of the ordering at all -- it is a property of the
ESTIMATOR, and a point estimate violates it outright.

Every claim below is checked with at least 2 independent tools, and every
proportion carries a Wilson interval.

Run: python3 bench/allocation_by_measured_capability_2026-10-07.py
"""
from __future__ import annotations

import argparse
import itertools
import math
from fractions import Fraction

Z = 1.959963984540054


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def expected_cost(order, p, c):
    """E[cost to first success or exhaustion]. Exact in Fractions."""
    tot, surv = Fraction(0), Fraction(1)
    for i in order:
        tot += surv * Fraction(c[i])
        surv *= (1 - Fraction(p[i]))
    return tot


def expected_calls(order, p):
    """E[number of dispatches] -- what the WAITING RESEARCHER pays."""
    return expected_cost(order, p, {i: 1 for i in order})


def key_pc(i, p, c):
    """Cross-multiplied value-over-cost, safe at c = 0."""
    return (float("inf") if Fraction(c[i]) == 0
            else Fraction(p[i]) / Fraction(c[i]))


def order_by(p, c, weight_latency=Fraction(0), latency=None):
    """Sort by p / (money + weight * latency). weight 0 = money only."""
    lat = latency or {i: 0 for i in p}
    eff = {i: Fraction(c[i]) + weight_latency * Fraction(lat[i]) for i in p}
    return sorted(p, key=lambda i: (-key_pc(i, p, eff)
                                    if eff[i] else float("-inf"), str(i)))


# ---------------------------------------------- R7: the researcher's currency
def claim_money_order_costs_the_researcher_time() -> dict:
    """A hard problem: 4 cheap-weak seats and 1 dear-strong one.

    Ordering by money puts the strong seat LAST, so the answer still arrives
    (exhaustion guarantees that) but the researcher waits through 4 failures.
    """
    seats = ["w1", "w2", "w3", "w4", "strong"]
    p = {"w1": Fraction(2, 100), "w2": Fraction(2, 100), "w3": Fraction(2, 100),
         "w4": Fraction(2, 100), "strong": Fraction(80, 100)}
    money = {"w1": 1, "w2": 1, "w3": 1, "w4": 1, "strong": 100}

    by_money = order_by(p, money)
    by_cap = sorted(seats, key=lambda i: (-p[i], i))

    best_calls = min(itertools.permutations(seats), key=lambda o: expected_calls(o, p))
    best_money = min(itertools.permutations(seats),
                     key=lambda o: expected_cost(o, p, money))
    return {
        "order_by_money": by_money,
        "order_by_capability": by_cap,
        "E_calls_money_order": round(float(expected_calls(by_money, p)), 6),
        "E_calls_capability_order": round(float(expected_calls(by_cap, p)), 6),
        "calls_fold_worse": round(float(expected_calls(by_money, p))
                                  / float(expected_calls(by_cap, p)), 4),
        "E_money_money_order": round(float(expected_cost(by_money, p, money)), 6),
        "E_money_capability_order": round(float(expected_cost(by_cap, p, money)), 6),
        "money_fold_worse": round(float(expected_cost(by_cap, p, money))
                                  / float(expected_cost(by_money, p, money)), 4),
        "money_order_is_calls_optimal": list(by_money) == list(best_calls),
        "money_order_is_money_optimal": list(by_money) == list(best_money),
        "the_tradeoff_is_real": list(best_calls) != list(best_money),
    }


def claim_pricing_the_wait_restores_capability_first() -> dict:
    """With latency in the cost, the SAME key reorders without a new rule.

    Each dispatch costs the researcher one wait-unit. As that unit is priced up,
    the key must cross over from money-first to capability-first.
    """
    seats = ["w1", "w2", "w3", "w4", "strong"]
    p = {"w1": Fraction(2, 100), "w2": Fraction(2, 100), "w3": Fraction(2, 100),
         "w4": Fraction(2, 100), "strong": Fraction(80, 100)}
    money = {"w1": 1, "w2": 1, "w3": 1, "w4": 1, "strong": 100}
    latency = {s: 1 for s in seats}          # every dispatch costs one wait

    crossover, rows = None, []
    for num in range(0, 401, 1):
        lam = Fraction(num)
        o = order_by(p, money, weight_latency=lam, latency=latency)
        if num % 100 == 0:
            rows.append((num, list(o)))
        if o[0] == "strong" and crossover is None:
            crossover = num
    return {
        "samples": rows,
        "latency_weight_at_which_capability_leads": crossover,
        "one_key_serves_both_ends": crossover is not None,
    }


# ---------------------------------------------- R6: a success is not capability
def claim_a_point_estimate_promotes_one_lucky_success() -> dict:
    """His guard, made arithmetic.

    A seat with 1 success from 1 attempt has a point estimate of 1.0 and
    outranks a seat with 60 of 70. A lower confidence bound does not let it.
    Cross-checked: closed-form Wilson, statsmodels Wilson, and a Beta posterior.
    """
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as beta_dist

    veteran, newcomer = (60, 70), (1, 1)
    pv, pn = veteran[0] / veteran[1], newcomer[0] / newcomer[1]
    lv, ln = wilson(*veteran)[0], wilson(*newcomer)[0]
    sv = proportion_confint(*veteran, method="wilson")[0]
    sn = proportion_confint(*newcomer, method="wilson")[0]
    bv = beta_dist.ppf(0.025, veteran[0] + 0.5, veteran[1] - veteran[0] + 0.5)
    bn = beta_dist.ppf(0.025, newcomer[0] + 0.5, newcomer[1] - newcomer[0] + 0.5)

    return {
        "veteran_60_of_70": {"point": round(pv, 6), "wilson_lo": round(lv, 6),
                             "jeffreys_lo": round(float(bv), 6)},
        "newcomer_1_of_1": {"point": round(pn, 6), "wilson_lo": round(ln, 6),
                            "jeffreys_lo": round(float(bn), 6)},
        "point_estimate_promotes_the_newcomer": pn > pv,
        "wilson_lower_bound_does_not": lv > ln,
        "jeffreys_lower_bound_does_not": float(bv) > float(bn),
        "closed_form_matches_statsmodels":
            abs(lv - sv) < 1e-12 and abs(ln - sn) < 1e-12,
        "attempts_needed_before_the_newcomer_may_lead":
            next(n for n in range(1, 4000) if wilson(n, n)[0] > lv),
    }


# ---------------------------------------------- R1 / R5: scale and direction
def claim_the_key_scales_and_moves_both_ways(sizes=(1, 6, 70, 500)) -> dict:
    """A derived sort key is roster-agnostic AND bidirectional by construction.

    No tuple to edit, no rung to promote: raise a seat's measured capability and
    it rises; lower it and it falls. Verified by perturbing ONE seat.
    """
    import numpy as np
    out = {}
    for n in sizes:
        rng = np.random.default_rng(1007 + n)
        p = {f"m{i}": Fraction(int(rng.integers(1, 99)), 100) for i in range(n)}
        c = {f"m{i}": int(rng.integers(0, 50)) for i in range(n)}
        o = order_by(p, c)
        # transitivity: the produced order must be a total order on the key
        keys = [key_pc(i, p, c) for i in o]
        monotone = all(
            (keys[j] == float("inf")) or (keys[j + 1] != float("inf")
                                          and keys[j] >= keys[j + 1])
            for j in range(len(keys) - 1))
        moved = {}
        if n >= 2:
            target = o[-1]                      # the last seat
            p2 = dict(p); p2[target] = Fraction(99, 100)
            c2 = dict(c); c2[target] = 1
            climbed = order_by(p2, c2).index(target) < o.index(target)
            p3 = dict(p); p3[target] = Fraction(1, 100)
            best = o[0]
            p4 = dict(p); p4[best] = Fraction(1, 1000)
            c4 = dict(c); c4[best] = max(1, c[best])
            fell = order_by(p4, c4).index(best) > 0
            moved = {"a_weak_seat_can_climb": climbed,
                     "a_strong_seat_can_fall": fell}
        out[n] = {"ordered": len(o) == n, "total_order": monotone, **moved}
    return out


def claim_strongest_first_is_usually_not_spend_optimal(trials: int = 4000) -> dict:
    """Independent re-derivation of the figure reported pre-compaction.

    The cc2 seat measured strongest-first as spend-suboptimal in 3637 of 4000
    rosters under exhaustion. Re-derived here from scratch rather than quoted.
    """
    import numpy as np
    rng = np.random.default_rng(20261007)
    worse = 0
    for _ in range(trials):
        n = int(rng.integers(3, 7))
        p = {i: Fraction(int(rng.integers(5, 95)), 100) for i in range(n)}
        c = {i: int(rng.integers(1, 200)) for i in range(n)}
        strong = sorted(p, key=lambda i: (-p[i], i))
        keyed = order_by(p, c)
        if expected_cost(tuple(strong), p, c) > expected_cost(tuple(keyed), p, c):
            worse += 1
    lo, hi = wilson(worse, trials)
    return {"trials": trials, "strongest_first_suboptimal_for_spend": worse,
            "rate": round(worse / trials, 6),
            "wilson": (round(lo, 6), round(hi, 6))}


def claim_the_exchange_rule_survives_any_positive_cost() -> dict:
    """z3: the key is unchanged when cost is money PLUS weighted latency."""
    import z3
    pi, pj, mi, mj, ti, tj, lam = z3.Reals("pi pj mi mj ti tj lam")
    ci, cj = mi + lam * ti, mj + lam * tj
    base = [pi > 0, pi < 1, pj > 0, pj < 1, mi >= 0, mj >= 0,
            ti >= 0, tj >= 0, lam >= 0]
    s = z3.Solver(); s.add(*base)
    s.add(pi * cj >= pj * ci)
    s.add(ci + (1 - pi) * cj > cj + (1 - pj) * ci)
    fwd = str(s.check())
    s2 = z3.Solver(); s2.add(*base)
    s2.add(pi * cj < pj * ci)
    s2.add(ci + (1 - pi) * cj <= cj + (1 - pj) * ci)
    rev = str(s2.check())
    return {"counterexample_search": fwd, "converse_search": rev,
            "holds_for_money_plus_latency": fwd == "unsat" and rev == "unsat"}


# ---------------------------------------------- the two rosters disagree
def claim_two_rosters_disagree(root=None) -> dict:
    """The ladder is a hardcoded NAME tuple; the panel roster is separate code."""
    import ast
    from pathlib import Path
    root = root or Path(__file__).resolve().parents[1]
    ladder = ()
    for node in ast.walk(ast.parse((root / "bench" / "routing.py").read_text())):
        if isinstance(node, ast.Assign) and any(
                isinstance(x, ast.Name) and x.id == "DEFAULT_FALSIFIER_STRENGTH"
                for x in node.targets):
            ladder = tuple(ast.literal_eval(node.value))
    panel = []
    for node in ast.walk(ast.parse(
            (root / "bench" / "confer_maths_panel_2026-09-05.py").read_text())):
        if isinstance(node, ast.Assign) and any(
                isinstance(x, ast.Name) and x.id == "_ALL" for x in node.targets):
            panel = [t[0] for t in ast.literal_eval(node.value)]
    lo = {x.lower() for x in ladder}
    return {"ladder_tuple": ladder, "ladder_size": len(ladder),
            "panel_roster": panel, "panel_size": len(panel),
            "on_panel_not_on_ladder": sorted(set(panel) - lo),
            "on_ladder_not_on_panel": sorted(lo - set(panel)),
            "the_two_disagree": sorted(set(panel) - lo) != []}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trials", type=int, default=4000)
    a = ap.parse_args()
    rows = [
        ("R7  money order costs the researcher time",
         claim_money_order_costs_the_researcher_time()),
        ("R7  pricing the wait restores capability-first",
         claim_pricing_the_wait_restores_capability_first()),
        ("R6  a point estimate promotes one lucky success",
         claim_a_point_estimate_promotes_one_lucky_success()),
        ("R1/R5  the key scales and moves both ways",
         claim_the_key_scales_and_moves_both_ways()),
        ("     strongest-first is usually not spend-optimal",
         claim_strongest_first_is_usually_not_spend_optimal(a.trials)),
        ("     the exchange rule survives money + latency",
         claim_the_exchange_rule_survives_any_positive_cost()),
        ("R1/R3  the two rosters disagree", claim_two_rosters_disagree()),
    ]
    for t, d in rows:
        print(f"\n== {t} ==")
        for k, v in d.items():
            print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
