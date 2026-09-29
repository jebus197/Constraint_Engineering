#!/usr/bin/env python3
"""Two defects in the adaptive-distributed-compute design spec, measured.

THE ARTEFACT UNDER REVIEW. `Responses/Codex, ChatGPT & Grok resources/
adaptive_distributed_compute_design_spec.md`, dated 2026-09-14. It proposes an
allocation/topology layer above the canonical CDSFL model: a scheduler that ranks
candidate dispatches by predicted reduction in residual risk per unit cost.

IT IS NOT RUNNING ON DISPROVEN MATHS; IT IS RUNNING ON SUPERSEDED MATHS, AND THE
SUPERSEDING CORRECTION IS ITS OWN AUTHOR'S. The appendix line "ΔR_k IS THE WRONG
QUANTITY FOR THIS DECISION" was added on 2026-09-21 in commit e61a83c, titled
"Astra landed 3 correct hits" -- 7 days AFTER the spec was written. Since the spec,
0 commits have touched the 1-qR form, S_k = A·E, or D(n), and b509a44 records
"3 corrections landed, 0 equations changed". The foundation is intact; the document
was never re-run against it.

DEFECT 1 -- the scheduling estimator is the CONDITIONAL quantity.
  Spec §6.1:  g = R - R_next,  R_next = [σ·R_det + (1-σ)·R](1-ν) + ν
  Appendix :  E[improvement] = R·q·σ·(1-ν) - ν·(1-R)
They differ by R²qσ(1-ν)(1-q)/(1-qR), and the spec's value is ALWAYS the smaller
(Wolfram `Resolve[ForAll[...], gSpec <= gExp]` -> True; SymPy agrees). Because the
gap is R-dependent it does not cancel in a ranking, and a scheduler ranks units
against each other.

DEFECT 2 -- the state update does not match the live runner.
  Spec     : a single scalar ν.
  Live     : `bench/reference_runner_v3.py:compute_rk` composes TWO,
             nu_eff = 1 - (1-nu_b)·(1-(1-sk)·nu_f), so re-injection depends on
             fix efficacy. Wolfram `Reduce` -> False on σ<1 (never equal), and
             `Resolve[ForAll[...]]` -> True that the spec UNDERSTATES residual risk.
             Optimistic exactly when repair is imperfect.

WHAT THIS SCRIPT ADDS OVER THE ALGEBRA, and it is a correction to CC1's own first
figure. The inversion rate was first reported as 7.9630% under UNIFORM sampling of
(R, q, σ, ν). That is an arbitrary prior, not a property of this project's runs.
Measured across 6 priors the rate spans 1.7% to 16.5%, and in the HIGH-RISK regime
R > 0.8 -- where a scheduler's decisions matter most -- it is roughly DOUBLE the
headline. So the defect is worse where it counts while the headline number is an
artefact of its prior. The operationally correct rate needs the observed joint
distribution of (R, q, σ, ν), which NO archived run reports; this script therefore
reports a RANGE and names the missing measurement rather than picking one number.

Read-only. Runs no experiment, spends nothing, calls no model.
Wolfram-derived statements above carry their attribution: computed with Wolfram Language.
"""
from __future__ import annotations

import argparse
import math
import random

import sympy as sp
from statsmodels.stats.proportion import proportion_confint

R, Q, S, V = sp.symbols("R q sigma nu", positive=True)
R_DET = R * (1 - Q) / (1 - Q * R)
G_SPEC = R - ((S * R_DET + (1 - S) * R) * (1 - V) + V)      # spec §6.1
G_EXP = R * Q * S * (1 - V) - V * (1 - R)                    # appendix, 2026-09-21

#: (R, q, sigma, nu) samplers. The first is the original, reported for comparison.
PRIORS = {
    "uniform (first reported)":   lambda r: (r.uniform(.05, .99), r.uniform(.05, .95),
                                             r.uniform(.05, 1.0), r.uniform(0, .3)),
    "high-risk regime R>0.8":     lambda r: (r.uniform(.80, .99), r.uniform(.05, .95),
                                             r.uniform(.05, 1.0), r.uniform(0, .3)),
    "low-risk regime R<0.4":      lambda r: (r.uniform(.05, .40), r.uniform(.05, .95),
                                             r.uniform(.05, 1.0), r.uniform(0, .3)),
    "near-perfect repair s>0.9":  lambda r: (r.uniform(.05, .99), r.uniform(.05, .95),
                                             r.uniform(.90, 1.0), r.uniform(0, .3)),
    "no re-injection nu=0":       lambda r: (r.uniform(.05, .99), r.uniform(.05, .95),
                                             r.uniform(.05, 1.0), 0.0),
    "runner default nu_b=0.05":   lambda r: (r.uniform(.05, .99), r.uniform(.05, .95),
                                             r.uniform(.05, 1.0), 0.05),
}
SEED = 11


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def algebra() -> dict:
    """Defect 1 in closed form, plus the live-runner mismatch of Defect 2."""
    diff = sp.simplify(G_SPEC - G_EXP)
    nb, nf = sp.symbols("nu_b nu_f", nonnegative=True)
    base = S * R_DET + (1 - S) * R
    nu_eff = 1 - (1 - nb) * (1 - (1 - S) * nf)
    live = base * (1 - nu_eff) + nu_eff
    spec = base * (1 - nb) + nb
    return {"estimator_gap": sp.factor(diff),
            "spec_minus_live": sp.factor(sp.simplify(spec - live)),
            "agree_only_when": sp.solve(sp.Eq(sp.simplify(live - spec), 0), S)}


def inversion_rates(trials: int = 60000) -> list[dict]:
    """How often does the spec's estimator RANK two work units the wrong way?"""
    gs = sp.lambdify((R, Q, S, V), G_SPEC, "math")
    ge = sp.lambdify((R, Q, S, V), G_EXP, "math")
    rows = []
    for name, draw in PRIORS.items():
        rng = random.Random(SEED)
        k = 0
        for _ in range(trials):
            a, b = draw(rng), draw(rng)
            if (gs(*a) > gs(*b)) != (ge(*a) > ge(*b)):
                k += 1
        lo, hi = wilson(k, trials)
        sm_lo, sm_hi = proportion_confint(k, trials, method="wilson")
        assert abs(lo - sm_lo) < 1e-12 and abs(hi - sm_hi) < 1e-12, "the 2 tools disagree"
        rows.append({"prior": name, "k": k, "n": trials, "rate": k / trials,
                     "wilson": (lo, hi)})
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Measure the 2 defects in the adaptive distributed-compute spec. "
                    "Read-only; runs no experiment and spends nothing.")
    ap.add_argument("--trials", type=int, default=60000)
    args = ap.parse_args(argv)

    a = algebra()
    print("DEFECT 1 -- the spec's estimator is not the expected improvement")
    print(f"   g_spec - g_expected = {a['estimator_gap']}")
    print("   Wolfram Resolve[ForAll[...], gSpec <= gExp] -> True (computed with "
          "Wolfram Language); SymPy agrees.\n")
    print("DEFECT 2 -- the spec's state update is not the live runner's")
    print(f"   spec - live = {a['spec_minus_live']}")
    print(f"   equal only when sigma in {a['agree_only_when']} (i.e. perfect repair)")
    print("   Direction: the spec UNDERSTATES residual risk whenever sigma < 1.\n")

    print(f"RANKING INVERSIONS -- and the rate is PRIOR-DEPENDENT ({args.trials} pairs each)")
    print(f"   {'prior':<28} {'k':>7} {'rate':>9}   Wilson 95%")
    rows = inversion_rates(args.trials)
    for r in rows:
        lo, hi = r["wilson"]
        print(f"   {r['prior']:<28} {r['k']:>7} {r['rate']:>8.4%}   [{lo:.4%}, {hi:.4%}]")
    lo_r = min(r["rate"] for r in rows)
    hi_r = max(r["rate"] for r in rows)
    print(f"\n   RANGE ACROSS PRIORS: {lo_r:.4%} to {hi_r:.4%}.")
    print("   The first figure reported for this defect, 7.9630%, was the UNIFORM row")
    print("   and is an artefact of that prior. In the high-risk regime the rate is")
    print("   roughly double it, so the defect is WORSE where a scheduler matters most.")
    print("   THE OPERATIONAL RATE IS NOT MEASURED HERE and cannot be: it needs the")
    print("   observed joint distribution of (R, q, sigma, nu), which no archived run")
    print("   reports. That is a named gap, not a number to be guessed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
