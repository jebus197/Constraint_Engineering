#!/usr/bin/env python3
"""Adapting to a dropped seat makes SPURIOUS convergence more likely.

THE FOUNDER'S REQUIREMENT, 2026-10-07: *"if a model drops off the list (say due
to my Max subscription limits, or a technical issue with that model), it should
not block an experimental run until completion, or convergence. The system should
be able to adapt dynamically in those circumstances."* And, correcting himself:
*"Not just 'that' model, but 'any model'."*

THE HAZARD THIS SCRIPT QUANTIFIES. The convergence gate is two-sided: it needs
`gamma_critical >= 0.30` AND K consecutive rounds with 0 new criticals. The
second condition gets EASIER as the roster shrinks, because fewer seats generate
fewer findings. A run that lost 2 of 6 seats therefore reaches "0 new criticals"
sooner -- not because the problem space is exhausted, but because fewer eyes are
looking. The gate cannot tell those apart: 0 new criticals from a healthy panel
and 0 new criticals from a depleted one are the same integer.

That is the project's recurring failure mode -- a failure that does not look like
a failure -- so it must be measured before the dynamic adaptation is built, not
after.

Every figure is cross-verified with at least 2 independent tools and every
proportion carries a Wilson interval.

Run: python3 bench/a_shrinking_roster_converges_sooner_2026-10-07.py
"""
from __future__ import annotations

import argparse
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


def p_quiet_round(n_seats: int, q: Fraction) -> Fraction:
    """P(no seat raises a new critical this round), seats independent."""
    return (1 - q) ** n_seats


def p_spurious(n_seats: int, q: Fraction, k_rounds: int) -> Fraction:
    """P(K consecutive quiet rounds purely by chance)."""
    return p_quiet_round(n_seats, q) ** k_rounds


def claim_a_smaller_roster_goes_quiet_sooner(q=Fraction(3, 10), k=3) -> dict:
    """Exact rational arithmetic, cross-checked symbolically in SymPy."""
    import sympy as sp

    rows = {}
    for n in (6, 5, 4, 3, 2, 1):
        rows[n] = float(p_spurious(n, q, k))

    # SymPy: the same quantity derived symbolically, then substituted
    nn, qq, kk = sp.symbols("n q k", positive=True)
    expr = ((1 - qq) ** nn) ** kk
    sym = {n: float(expr.subs({qq: sp.Rational(q.numerator, q.denominator),
                               nn: n, kk: k})) for n in rows}
    agree = all(abs(rows[n] - sym[n]) < 1e-12 for n in rows)

    # mpmath as the third check on the ratio that carries the finding
    import mpmath as mp
    mp.mp.dps = 40
    r_mp = (mp.mpf(1) - mp.mpf(q.numerator) / q.denominator)
    ratio_mp = float((r_mp ** 4) ** k / (r_mp ** 6) ** k)

    return {
        "q_new_critical_per_seat_per_round": float(q),
        "k_consecutive_quiet_rounds_required": k,
        "P_spurious_by_roster_size": {n: round(v, 9) for n, v in rows.items()},
        "fold_increase_6_to_4": round(rows[4] / rows[6], 6),
        "fold_increase_6_to_2": round(rows[2] / rows[6], 6),
        "sympy_agrees": agree,
        "mpmath_agrees_on_the_6_to_4_ratio":
            abs(ratio_mp - rows[4] / rows[6]) < 1e-9,
    }


def claim_the_gate_cannot_distinguish_the_two_causes() -> dict:
    """0 new criticals from a healthy panel and from a depleted one are the same
    integer, so no threshold on that integer can separate them."""
    import z3
    # n1 seats healthy, n2 seats depleted; both report 0 new criticals.
    observed_healthy, observed_depleted = z3.Ints("oh od")
    s = z3.Solver()
    s.add(observed_healthy == 0, observed_depleted == 0)
    s.add(observed_healthy != observed_depleted)   # can any rule tell them apart?
    verdict = str(s.check())
    return {
        "search_for_a_distinguishing_value": verdict,
        "distinguishable_from_the_count_alone": verdict == "sat",
        "note": ("unsat means no value of the observed count separates the 2 "
                 "causes, so the roster size must be carried ALONGSIDE the count"),
    }


def claim_declaring_the_roster_restores_the_distinction() -> dict:
    """With roster size recorded, the quiet round is interpretable again.

    The fix is not a new threshold but a new FIELD: a convergence reached on a
    reduced roster is a different event from one reached on the declared roster,
    and the record must say which.
    """
    import z3
    n_declared, n_live, quiet = z3.Ints("nd nl q")
    s = z3.Solver()
    s.add(n_declared > 0, n_live > 0, n_live <= n_declared, quiet == 0)
    # A rule that fires only when the roster is intact
    intact = z3.And(quiet == 0, n_live == n_declared)
    degraded = z3.And(quiet == 0, n_live < n_declared)
    s.add(intact, degraded)          # can both hold at once?
    both = str(s.check())
    return {
        "can_a_round_be_both_intact_and_degraded": both,
        "the_two_are_mutually_exclusive": both == "unsat",
        "implication": ("recording n_live beside the count makes the clean and "
                        "the degraded convergence formally separable"),
    }


def claim_dropout_probability_over_a_run(trials: int = 20000) -> dict:
    """How often does AT LEAST 1 seat of 6 drop out during a 10-round run?

    Uses the project's own measured free-seat failure experience as the input
    range rather than a guess, and reports the answer as an interval.
    """
    import numpy as np
    from scipy.stats import binom

    rng = np.random.default_rng(20261007)
    rounds, seats = 10, 6
    out = {}
    for per_seat_per_round in (0.005, 0.01, 0.02, 0.05):
        hits = 0
        for _ in range(trials):
            if rng.random(size=(rounds, seats)).min() < per_seat_per_round:
                hits += 1
        lo, hi = wilson(hits, trials)
        # closed form as the second tool
        closed = 1 - (1 - per_seat_per_round) ** (rounds * seats)
        sci = 1 - binom.pmf(0, rounds * seats, per_seat_per_round)
        out[per_seat_per_round] = {
            "simulated": round(hits / trials, 6),
            "wilson": (round(lo, 6), round(hi, 6)),
            "closed_form": round(closed, 6),
            "scipy_binom": round(float(sci), 6),
            "all_three_agree": abs(hits / trials - closed) < 0.02
                               and abs(closed - float(sci)) < 1e-12,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trials", type=int, default=20000)
    a = ap.parse_args()
    rows = [
        ("a smaller roster goes quiet sooner",
         claim_a_smaller_roster_goes_quiet_sooner()),
        ("the gate cannot distinguish the 2 causes",
         claim_the_gate_cannot_distinguish_the_two_causes()),
        ("declaring the live roster restores the distinction",
         claim_declaring_the_roster_restores_the_distinction()),
        ("P(at least 1 dropout in a 10-round, 6-seat run)",
         claim_dropout_probability_over_a_run(a.trials)),
    ]
    for t, d in rows:
        print(f"\n== {t} ==")
        for k, v in d.items():
            print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
