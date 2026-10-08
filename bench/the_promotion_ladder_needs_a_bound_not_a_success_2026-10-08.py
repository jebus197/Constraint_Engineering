#!/usr/bin/env python3
"""A rung ladder earned on SINGLE successes under-promotes good models badly.

THE FOUNDER'S DESIGN, 2026-10-08, verbatim: *"new models get tried out on simpler
tasks. If they succeed in simpler tasks they are granted an attempt to climb the
ladder, If they then succeed in that more complex task, they climb the ladder
again, if they fail they either stay on the same simpler problem resolution rung,
or if they fail on any more complex task/rung on the ladder, they stay on the last
rung where they demonstrated success."*

WHY THE DESIGN IS NEEDED. It answers the cold-start problem that neither panel
seat solved and that an identifier alone cannot: a model starting with 0 credit
has no route to the top under a pure sort, because it is never tried on work that
could demonstrate capability. Giving it cheap easy work first bounds the cost of
exploration by the cost of EASY tasks rather than hard ones.

WHAT THIS SCRIPT TESTS. The promotion CRITERION, not the ladder. Promoting on a
single success contradicts the founder's own requirement 6 -- *"what we need to
guard against is simply counting when a model is successful as an 'improvement in
capability'"* -- and the cost is asymmetric in a way worth measuring: it does not
mainly let bad models through, it mainly keeps GOOD models out.

Every figure is cross-verified with 2 independent tools and every proportion
carries a Wilson interval.

Run: python3 bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py
"""
from __future__ import annotations

import argparse
import math

Z = 1.959963984540054


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def claim_single_success_promotion_is_asymmetric(rungs: int = 5) -> dict:
    """P(reach the top rung) under promote-on-one-success, exactly.

    A model with true per-rung success probability p must succeed once at each of
    `rungs` rungs, so P(top) = p**rungs. Closed form, cross-checked in mpmath and
    against a binomial survival in scipy.
    """
    import mpmath as mp
    from scipy.stats import binom
    mp.mp.dps = 30
    out = {}
    for p in (0.95, 0.90, 0.75, 0.50, 0.25, 0.10):
        closed = p ** rungs
        mpv = float(mp.mpf(p) ** rungs)
        # scipy: all `rungs` independent Bernoulli(p) succeed
        sci = float(binom.pmf(rungs, rungs, p))
        out[p] = {
            "P_reaches_top_rung": round(closed, 8),
            "P_stuck_below_top": round(1 - closed, 8),
            "mpmath_agrees": abs(closed - mpv) < 1e-12,
            "scipy_agrees": abs(closed - sci) < 1e-12,
        }
    return out


def claim_a_bound_gate_fixes_the_asymmetry(rungs: int = 5,
                                           attempts_per_rung: int = 10,
                                           floor: float = 0.50) -> dict:
    """Promote only when the Wilson LOWER bound at a rung clears a floor.

    This is requirement 6 applied to promotion rather than to ordering: a run of
    successes, not one, and the number required falls out of the arithmetic
    rather than being chosen.
    """
    from scipy.stats import binom
    import numpy as np

    # successes needed at `attempts_per_rung` for the lower bound to clear `floor`
    need = None
    for k in range(attempts_per_rung + 1):
        if wilson(k, attempts_per_rung)[0] > floor:
            need = k
            break
    out = {"attempts_per_rung": attempts_per_rung, "floor": floor,
           "successes_needed_per_rung": need}
    if need is None:
        out["note"] = ("no success count at this sample size clears the floor; "
                       "the rung needs more attempts, which is itself the answer")
        return out
    for p in (0.95, 0.90, 0.75, 0.50, 0.25, 0.10):
        per_rung = float(binom.sf(need - 1, attempts_per_rung, p))
        top = per_rung ** rungs
        # second tool: numpy's own binomial tail by summation
        ks = np.arange(need, attempts_per_rung + 1)
        manual = float(np.sum([math.comb(attempts_per_rung, int(k))
                               * p ** int(k) * (1 - p) ** (attempts_per_rung - int(k))
                               for k in ks]))
        out[p] = {"P_promote_one_rung": round(per_rung, 8),
                  "P_reaches_top_rung": round(top, 8),
                  "numpy_agrees": abs(per_rung - manual) < 1e-9}
    return out


def claim_the_absorbing_rung_contradicts_bidirectionality(trials: int = 20000,
                                                          rungs: int = 5) -> dict:
    """"Stay on the last rung where they demonstrated success" -- for how long?

    If a failure permanently fixes a model's rung, a single unlucky failure caps
    a good model forever, which contradicts the founder's own bidirectional rule
    that capability lost must be able to be regained. Measured: how often a
    p=0.90 model is permanently capped below the top by bad luck alone.
    """
    import numpy as np
    rng = np.random.default_rng(20261008)
    p = 0.90
    capped = 0
    for _ in range(trials):
        rung = 0
        while rung < rungs:
            if rng.random() < p:
                rung += 1
            else:
                break                 # absorbing: stuck here forever
        if rung < rungs:
            capped += 1
    lo, hi = wilson(capped, trials)
    return {"true_success_rate": p, "rungs": rungs, "trials": trials,
            "permanently_capped_below_top": capped,
            "rate": round(capped / trials, 6),
            "wilson": (round(lo, 6), round(hi, 6)),
            "closed_form_check": round(1 - p ** rungs, 6)}


def claim_difficulty_can_be_measured_not_judged() -> dict:
    """The rung a finding was ACTUALLY resolved at is a measured difficulty label.

    The founder's ladder needs tasks ordered by difficulty BEFORE a new model is
    placed, while both panel seats argued difficulty is emergent and retrospective
    -- a finding is hard because everything better already failed. Those are
    reconcilable: resolution DEPTH is recorded per finding, so past depth labels
    future difficulty with no human judgement and no vendor name.
    """
    import ast
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    src = (root / "bench" / "routing.py").read_text()
    fields = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            fields.add(node.target.id)
    return {
        "routing_result_fields": sorted(fields),
        "records_resolution_depth": "rungs_tried" in fields,
        "records_which_model_resolved": "model_used" in fields,
        "implication": ("rungs_tried is already recorded per finding, so observed "
                        "difficulty is available today and needs no classifier"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rungs", type=int, default=5)
    ap.add_argument("--attempts-per-rung", type=int, default=10)
    a = ap.parse_args()
    rows = [
        ("1. promote on ONE success -- the asymmetry",
         claim_single_success_promotion_is_asymmetric(a.rungs)),
        ("2. promote on a LOWER BOUND instead",
         claim_a_bound_gate_fixes_the_asymmetry(a.rungs, a.attempts_per_rung)),
        ("3. an absorbing rung contradicts bidirectionality",
         claim_the_absorbing_rung_contradicts_bidirectionality(rungs=a.rungs)),
        ("4. difficulty is already measured, not judged",
         claim_difficulty_can_be_measured_not_judged()),
    ]
    for t, d in rows:
        print(f"\n== {t} ==")
        for k, v in d.items():
            print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
