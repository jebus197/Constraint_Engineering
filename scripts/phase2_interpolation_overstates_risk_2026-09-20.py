#!/usr/bin/env python3
"""The three-phase Phase 2 interpolation OVERSTATES residual risk. Derivation + measurement.

WHAT IS CLAIMED, PRECISELY
--------------------------
`compute_rk` (bench/reference_runner_v3.py) implements the appendix "Three-Phase
Extension" Phase 2 as

    R_base = sk * R_det + (1 - sk) * R_old,      R_det = R(1-q)/(1-qR)

i.e. it interpolates between the NON-DETECTION posterior and the PRIOR.

The exact expected post-review, pre-re-injection risk for the process the
appendix describes in words -- "a pass with detection probability q; where the
flaw is detected, a fix that removes it with probability sigma" -- is obtained
by enumerating the two actual branches:

    detected      w.p. q*R        -> flaw survives w.p. (1 - sigma)
    not detected  w.p. 1 - q*R    -> flaw survives w.p. R(1-q)/(1-qR)

    E[R] = q*R*(1-sigma) + (1-q*R) * R(1-q)/(1-qR) = R * (1 - q*sigma)

The difference is exact and signed:

    R_base - R*(1 - q*sigma) = R^2 * q * sigma * (q - 1) / (R*q - 1)

Numerator <= 0 (q <= 1); denominator <= 0 (R,q <= 1); so the quotient is >= 0,
strictly positive whenever 0 < q < 1, sigma > 0, R > 0. Shipped Phase 2 is
ALWAYS >= the exact expectation and never below it.

WHY IT MATTERS OPERATIONALLY
----------------------------
`check_sk_threshold_corrected` -- the LIVE fix-admission gate, promoted from
shadow 2026-09-07 -- decides by `compute_rk(R,q,sk,nu_b,nu_f) <= R`. An
overstated R_k makes that inequality harder to satisfy, so the live gate REFUSES
fixes the exact expectation calls net-beneficial. This script measures how often,
over the reachable parameter box, and in which direction.

TWO TOOLS PER CLAIM. SymPy for the algebra; an independent brute-force branch
enumeration in floating point (no shared code with SymPy) for the identity;
statsmodels + a closed-form mpmath Wilson for every proportion.

NOTHING HERE CHANGES A LIVE VERDICT. This script measures; it does not patch.
"""
from __future__ import annotations

import sys

import mpmath as mp
import sympy as sp
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, ".")
from bench import reference_runner_v3 as rr  # noqa: E402


def wilson_mpmath(k, n, z=1.959963984540054):
    """Closed-form Wilson interval; shares no code with statsmodels."""
    if n == 0:
        return (mp.mpf(0), mp.mpf(1))
    p = mp.mpf(k) / n
    z = mp.mpf(z)
    d = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / d
    half = (z / d) * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(mp.mpf(0), centre - half), min(mp.mpf(1), centre + half))


def _nu_eff(sk, nu_b, nu_f):
    return 1.0 - (1.0 - nu_b) * (1.0 - (1.0 - sk) * nu_f)


def compute_rk_exact_phase2(R, q, sk, nu_b=0.05, nu_f=0.20):
    """compute_rk with Phase 2 replaced by the exact branch expectation.

    IDENTICAL parameter list. NO new free parameter. Only Phase 2 changes:
        R_base = R * (1 - q * sk)        instead of   sk*R_det + (1-sk)*R
    Phases 1 and 3 and the nu_b+nu_f<=1 rescale are the shipped behaviour, so
    the two are comparable at every point.
    """
    R = max(0.0, min(1.0, float(R)))
    q = max(0.0, min(1.0, float(q)))
    sk = max(0.0, min(1.0, float(sk)))
    nu_b = max(0.0, min(1.0, float(nu_b)))
    nu_f = max(0.0, min(1.0, float(nu_f)))
    if nu_b + nu_f > 1.0:
        scale = 1.0 / (nu_b + nu_f)
        nu_b *= scale
        nu_f *= scale
    R_base = R * (1.0 - q * sk)
    ne = _nu_eff(sk, nu_b, nu_f)
    return max(0.0, min(1.0, R_base * (1.0 - ne) + ne))


def symbolic_check():
    R, q, s = sp.symbols("R q sigma", nonnegative=True)
    R_det = R * (1 - q) / (1 - q * R)
    shipped = s * R_det + (1 - s) * R
    exact = q * R * (1 - s) + (1 - q * R) * R_det
    print("[sympy] exact branch enumeration simplifies to:", sp.simplify(exact))
    diff = sp.factor(sp.simplify(shipped - exact))
    print("[sympy] shipped_phase2 - exact =", diff)
    num, den = sp.fraction(sp.together(diff))
    print("[sympy] numerator  =", sp.factor(num), " (<= 0 for q<=1)")
    print("[sympy] denominator=", sp.factor(den), " (<= 0 for R,q<=1)")
    bad = 0
    tot = 0
    for Rv in [i / 20 for i in range(21)]:
        for qv in [i / 20 for i in range(21)]:
            for sv in [i / 20 for i in range(21)]:
                if abs(1 - qv * Rv) < 1e-12:
                    continue
                tot += 1
                d = float(diff.subs({R: Rv, q: qv, s: sv}))
                if d < -1e-12:
                    bad += 1
    print(f"[sympy-sample] points where shipped < exact: {bad} of {tot}")


def brute_force_identity():
    """Confirm E[R] = R(1-q*sigma) by explicit two-branch arithmetic in floats."""
    worst = 0.0
    n = 0
    for Ri in range(1, 20):
        R = Ri / 20
        for qi in range(1, 20):
            q = qi / 20
            for si in range(0, 21):
                s = si / 20
                det = q * R
                surv_miss = R * (1 - q) / (1 - q * R)
                e = det * (1 - s) + (1 - det) * surv_miss
                worst = max(worst, abs(e - R * (1 - q * s)))
                n += 1
    print(f"[brute-force] max |two-branch E[R] - R(1-q*sigma)| over {n} pts = {worst:.3e}")


def gate_disagreement():
    """How often does the LIVE gate disagree with exact-Phase-2 semantics, and how?"""
    grid_R = [i / 20 for i in range(1, 20)]
    grid_q = [i / 20 for i in range(1, 20)]
    grid_sk = [i / 20 for i in range(1, 21)]
    nu_pairs = [(0.05, 0.20), (0.02, 0.10), (0.10, 0.30), (0.05, 0.05)]

    n = live_refuse_exact_admit = live_admit_exact_refuse = agree = 0
    overstates = 0
    for nb, nf in nu_pairs:
        for R in grid_R:
            for q in grid_q:
                for sk in grid_sk:
                    n += 1
                    live_r = rr.compute_rk(R, q, sk, nb, nf)
                    exact_r = compute_rk_exact_phase2(R, q, sk, nb, nf)
                    if live_r >= exact_r - 1e-12:
                        overstates += 1
                    live_pass = live_r <= R
                    exact_pass = exact_r <= R
                    if live_pass == exact_pass:
                        agree += 1
                    elif exact_pass and not live_pass:
                        live_refuse_exact_admit += 1
                    else:
                        live_admit_exact_refuse += 1

    def report(label, k):
        lo, hi = proportion_confint(k, n, method="wilson")
        mlo, mhi = wilson_mpmath(k, n)
        ok = abs(float(mlo) - lo) < 1e-9 and abs(float(mhi) - hi) < 1e-9
        print(f"  {label:<46} {k:6d}/{n} = {100*k/n:7.4f}%  "
              f"Wilson [{100*lo:7.4f}%, {100*hi:7.4f}%]  mpmath agrees={ok}")

    print(f"\n[gate] reachable grid points: {n}")
    report("live R_k >= exact R_k (overstatement)", overstates)
    report("verdicts agree", agree)
    report("LIVE REFUSES, exact-Phase-2 ADMITS", live_refuse_exact_admit)
    report("LIVE ADMITS, exact-Phase-2 REFUSES (harmful)", live_admit_exact_refuse)

    print("\n[gate] the SHIPPED DEFAULT operating point "
          "(R=0.5 uniform prior, q=0.5, nu_b=0.05, nu_f=0.20):")
    for sk in (0.1, 0.3, 0.5, 0.7, 0.9, 1.0):
        lr = rr.compute_rk(0.5, 0.5, sk)
        er = compute_rk_exact_phase2(0.5, 0.5, sk)
        print(f"   sk={sk:4.2f}  live R_k={lr:.6f} -> {'ADMIT' if lr<=0.5 else 'REFUSE':6s}"
              f"   exact R_k={er:.6f} -> {'ADMIT' if er<=0.5 else 'REFUSE':6s}")


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    symbolic_check()
    brute_force_identity()
    gate_disagreement()
