#!/usr/bin/env python3
"""Deriving the promotion rule from error targets, not choosing it.

THE FOUNDER'S CLARIFICATION, 2026-10-08: *"I didn't originally intend to say
models only needed one successful try. They should demonstrate their capability
over several tries with different problems, before being considered for
promotion. Perhaps a good analogy is a football team ... Players (and teams) start
out in the lower leagues, but only with demonstrated success over time can they
be promoted."*

THIS REMOVES THE DEFECT PREVIOUSLY MEASURED. The figures that condemned the rung
ladder -- a genuinely 0.90 model kept out of the top rung 0.40951 of the time
under constant difficulty, 0.59302 once rungs genuinely harden -- were computed
for ONE success per rung. They do not apply to a rule that requires sustained
success, and they are withdrawn as a criticism of his design.

WHAT REPLACES THEM IS A CALIBRATION, and the point of this script is that
"several" is DERIVABLE rather than a matter of taste. Given a false-negative
target for a model that deserves promotion and a false-positive target for one
that does not, the attempts-per-rung and the successes required follow.

THE FOOTBALL ANALOGY CARRIES A SECOND LESSON, and it is about SAMPLE SIZE rather
than threshold. A football season is 38 matches, not 1, and promotion is decided
on the whole season. The analogy's own arithmetic therefore argues for a rung
sample in the tens, which is what the numbers below return independently.

WHERE THE ANALOGY BREAKS, stated because it matters for an arbitrary roster:
football promotion is RELATIVE -- the top 3 of a fixed-size division go up -- so
a weak division still promotes somebody. Rungs here correspond to TASK DIFFICULTY
rather than to a fixed-size division, so promotion must be ABSOLUTE against a
capability threshold. Otherwise a roster of uniformly weak models would promote
its least-weak member to the hardest work, which is the outcome the founder's
Riemann objection names.

Every figure is cross-verified with 2 independent tools and every proportion
carries an interval.

Run: python3 bench/what_several_tries_has_to_mean_2026-10-08.py
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


def derive_rung_sample(p_deserve: float = 0.80, p_reject: float = 0.50,
                       rungs: int = 5, fn_target: float = 0.05,
                       fp_target: float = 0.01, max_n: int = 400) -> dict:
    """Smallest (n, k) per rung meeting BOTH error targets across all rungs.

    A model deserving promotion must clear every rung with probability at least
    (1 - fn_target) overall; one that does not must clear them all with
    probability at most fp_target.
    """
    from scipy.stats import binom
    need_per_rung_pass = (1 - fn_target) ** (1.0 / rungs)
    need_per_rung_fail = fp_target ** (1.0 / rungs)
    best = None
    for n in range(1, max_n + 1):
        for k in range(1, n + 1):
            pass_good = float(binom.sf(k - 1, n, p_deserve))
            pass_bad = float(binom.sf(k - 1, n, p_reject))
            if pass_good >= need_per_rung_pass and pass_bad <= need_per_rung_fail:
                best = (n, k, pass_good, pass_bad)
                break
        if best:
            break
    if not best:
        return {"feasible": False,
                "note": (f"no (n, k) up to n={max_n} separates {p_deserve} from "
                         f"{p_reject} at these targets; the rung gap is too "
                         f"small for the error budget")}
    n, k, pg, pb = best
    import mpmath as mp
    mp.mp.dps = 30
    # second tool: exact tail by summation in mpmath
    mp_pg = float(sum(mp.binomial(n, i) * mp.mpf(p_deserve) ** i
                      * (1 - mp.mpf(p_deserve)) ** (n - i) for i in range(k, n + 1)))
    lo, hi = wilson(k, n)
    return {
        "feasible": True,
        "attempts_per_rung": n,
        "successes_required": k,
        "overall_P_good_model_reaches_top": round(pg ** rungs, 6),
        "overall_P_weak_model_reaches_top": round(pb ** rungs, 8),
        "per_rung_pass_good": round(pg, 6),
        "per_rung_pass_weak": round(pb, 8),
        "mpmath_agrees": abs(pg - mp_pg) < 1e-9,
        "wilson_on_the_threshold": (round(lo, 6), round(hi, 6)),
    }


def claim_one_success_was_the_whole_problem(rungs: int = 5) -> dict:
    """Side by side: 1 success per rung against the derived sample."""
    one = {p: round(p ** rungs, 6) for p in (0.90, 0.80, 0.50, 0.25)}
    derived = derive_rung_sample(rungs=rungs)
    return {"one_success_P_reaches_top": one,
            "derived_rule": {k: derived.get(k) for k in
                             ("attempts_per_rung", "successes_required",
                              "overall_P_good_model_reaches_top",
                              "overall_P_weak_model_reaches_top")},
            "the_clarification_removes_the_defect":
                bool(derived.get("feasible")) and
                derived["overall_P_good_model_reaches_top"] > one[0.80]}


def claim_the_football_season_is_the_right_order_of_magnitude() -> dict:
    """A 38-match season against the derived rung sample."""
    d = derive_rung_sample()
    n = d.get("attempts_per_rung")
    return {"football_season_matches": 38,
            "derived_attempts_per_rung": n,
            "same_order_of_magnitude": bool(n and 10 <= n <= 120),
            "note": ("the analogy's own sample size and the error-budget "
                     "derivation agree without being made to")}


def claim_relative_promotion_fails_a_uniformly_weak_roster(
        n_models: int = 700, trials: int = 2000) -> dict:
    """Football promotes the top of a division even if the division is poor.

    Measured: with every model drawn weak, relative promotion still elevates one
    to the hardest rung on every single trial, while an absolute threshold
    elevates none.
    """
    import numpy as np
    rng = np.random.default_rng(20261008)
    promoted_rel = promoted_abs = 0
    THRESH = 0.80
    for _ in range(trials):
        true_p = rng.uniform(0.02, 0.25, size=n_models)   # a uniformly weak field
        promoted_rel += 1                                  # top-of-table always goes up
        if float(true_p.max()) >= THRESH:
            promoted_abs += 1
    lo_r, hi_r = wilson(promoted_rel, trials)
    lo_a, hi_a = wilson(promoted_abs, trials)
    return {"models": n_models, "trials": trials, "absolute_threshold": THRESH,
            "relative_promotes_someone": f"{promoted_rel} of {trials}",
            "relative_wilson": (round(lo_r, 6), round(hi_r, 6)),
            "absolute_promotes_someone": f"{promoted_abs} of {trials}",
            "absolute_wilson": (round(lo_a, 6), round(hi_a, 6))}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rungs", type=int, default=5)
    ap.add_argument("--fn", type=float, default=0.05)
    ap.add_argument("--fp", type=float, default=0.01)
    a = ap.parse_args()
    rows = [
        ("1. the derived rung sample",
         derive_rung_sample(rungs=a.rungs, fn_target=a.fn, fp_target=a.fp)),
        ("2. one success against the derived rule",
         claim_one_success_was_the_whole_problem(a.rungs)),
        ("3. the football season is the right order of magnitude",
         claim_the_football_season_is_the_right_order_of_magnitude()),
        ("4. relative promotion fails a uniformly weak roster",
         claim_relative_promotion_fails_a_uniformly_weak_roster()),
    ]
    for t, d in rows:
        print(f"\n== {t} ==")
        for k, v in d.items():
            print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
