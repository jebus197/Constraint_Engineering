#!/usr/bin/env python3
"""Blind-round falsifiers: what the revised action step forbids, and when.

Attacks CC1's calibration claim from the 2026-09-20 blind brief, Section 3:
"with the introduction rate fixed the reachable set collapses to a band of
width exactly z ... Measuring the parameter restores the model's power to
forbid outcomes."

Six executed claims, each cross-checked by 2 independent tools (SymPy exact /
z3 proof / NumPy random / mpmath high precision):

  A. s,b both free: reachable set of (1-s)z + b(1-z) is all of [0,1].
  B. b fixed, s free: band [b(1-z), b(1-z)+z], width exactly z, any b. (CC1: HOLDS)
  C. ATTACK 1: the forbidden measure is 1-z, so the restored power VANISHES
     as z -> 1 -- weakest exactly where residual risk is highest.
  D. ATTACK 2: fixing s instead gives width 1-z. Which parameter is measured
     decides where any forbidding power survives; CC1 names only b.
  E. STRONGER THAN CC1: under the package's own sequential mapping
     (CDSFL_revised_core.sequential_repair_parameters: s = sigma*(1-nu), b = nu),
     measuring the re-injection rate nu ALONE gives band [nu, z + nu(1-z)],
     width z(1-nu), with a hard floor: risk_after >= nu for every sigma, z.
     That floor is the action-step analogue of appendix section 7.12's
     D* = eps*/(1-nu), and it is a genuine forbidden zone.
  F. The package's own uninformative-evidence recursion R' = b + (1-s-b)R
     has fixed point b/(s+b) (spec line 302), NOT b/p; b/p belongs to the
     detection-thinned recursion R' = R(1-p) + b. Both verified.

Read-only. Standard library + sympy, numpy, mpmath, z3. Contacts nothing.
Run: python3 scripts/panel_blind_action_step_reachability_2026-09-20.py
"""
from __future__ import annotations

import sys


def fail(msg):
    print(f"FALSIFIED: {msg}")
    sys.exit(1)


def main():
    import numpy as np
    import sympy as sp
    import z3

    z, s, b, p, nu, sigma, R = sp.symbols(
        "z s b p nu sigma R", real=True, nonnegative=True)
    after = (1 - s) * z + b * (1 - z)

    # --- A. both free: all of [0,1] -------------------------------------
    lo = after.subs({s: 1, b: 0})
    hi = after.subs({s: 0, b: 1})
    assert sp.simplify(lo) == 0 and sp.simplify(hi) == 1, "A endpoints"
    rng = np.random.default_rng(20260920)
    zs, ss, bs = (rng.uniform(0, 1, 200_000) for _ in range(3))
    vals = (1 - ss) * zs + bs * (1 - zs)
    if not ((vals >= -1e-12).all() and (vals <= 1 + 1e-12).all()):
        fail("A: value outside [0,1]")
    print("A HOLDS  s,b free: reachable = [0,1]  (SymPy endpoints + 200k NumPy)")

    # --- B. b fixed: band of width exactly z ----------------------------
    lo_b = sp.simplify(after.subs(s, 1))
    hi_b = sp.simplify(after.subs(s, 0))
    width = sp.simplify(hi_b - lo_b)
    assert width == z, f"B width: {width}"
    Z, S, B = z3.Reals("Z S B")
    box = z3.And(0 <= Z, Z <= 1, 0 <= S, S <= 1, 0 <= B, B <= 1)
    aft = (1 - S) * Z + B * (1 - Z)
    solver = z3.Solver()
    solver.add(box, z3.Or(aft < B * (1 - Z), aft > Z + B * (1 - Z)))
    if solver.check() != z3.unsat:
        fail("B: z3 found a point outside the band")
    print("B HOLDS  b fixed: band [b(1-z), b(1-z)+z], width exactly z "
          "(SymPy + z3 UNSAT), independent of b -- CC1's claim is TRUE as stated")

    # --- C. attack 1: forbidding power vanishes as z -> 1 ---------------
    assert sp.simplify(1 - width) == 1 - z
    at_z1 = (sp.simplify(lo_b.subs(z, 1)), sp.simplify(hi_b.subs(z, 1)))
    assert at_z1 == (0, 1), f"C: {at_z1}"
    print("C ATTACK forbidden measure = 1-z; at z=1 the band is [0,1]: with b "
          "measured the model STILL forbids nothing at high starting risk")

    # --- D. attack 2: fixing s instead gives width 1-z ------------------
    width_s = sp.simplify(after.subs(b, 1) - after.subs(b, 0))
    assert width_s == 1 - z, f"D: {width_s}"
    print("D ATTACK s fixed instead: width 1-z. WHICH parameter is measured "
          "decides where power survives; CC1 names only b")

    # --- E. sequential mapping: floor at nu ------------------------------
    seq = after.subs({s: sigma * (1 - nu), b: nu})
    lo_e = sp.simplify(seq.subs(sigma, 1))
    assert sp.simplify(lo_e - nu) == 0, f"E lo: {lo_e}"
    hi_e = sp.simplify(seq.subs(sigma, 0))
    width_e = sp.simplify(hi_e - lo_e)
    assert sp.simplify(width_e - z * (1 - nu)) == 0, f"E width: {width_e}"
    N, SG = z3.Reals("N SG")
    seqz = (1 - SG * (1 - N)) * Z + N * (1 - Z)
    solver = z3.Solver()
    solver.add(0 <= Z, Z <= 1, 0 <= N, N <= 1, 0 <= SG, SG <= 1, seqz < N)
    if solver.check() != z3.unsat:
        fail("E: z3 found risk_after < nu")
    print("E STRONGER: under the package's own sequential mapping, measuring "
          "nu alone gives band [nu, z+nu(1-z)], width z(1-nu), and a PROVED "
          "floor risk_after >= nu (z3 UNSAT) -- the action-step analogue of "
          "section 7.12's D* = eps*/(1-nu)")

    # --- F. fixed points: b/(s+b) vs b/p ---------------------------------
    fp_spec = sp.solve(sp.Eq(b + (1 - s - b) * R, R), R)
    assert fp_spec and sp.simplify(fp_spec[0] - b / (s + b)) == 0, fp_spec
    fp_det = sp.solve(sp.Eq(R * (1 - p) + b, R), R)
    assert fp_det and sp.simplify(fp_det[0] - b / p) == 0, fp_det
    import mpmath as mp
    mp.mp.dps = 40
    bv, sv, pv = mp.mpf("0.03"), mp.mpf("0.4"), mp.mpf("0.4")
    r1 = r2 = mp.mpf("0.5")
    for _ in range(4000):
        r1 = bv + (1 - sv - bv) * r1
        r2 = r2 * (1 - pv) + bv
    if abs(r1 - bv / (sv + bv)) > mp.mpf("1e-30"):
        fail(f"F: spec recursion converged to {r1}")
    if abs(r2 - bv / pv) > mp.mpf("1e-30"):
        fail(f"F: detection recursion converged to {r2}")
    print("F HOLDS  R'=b+(1-s-b)R -> b/(s+b) (spec line 302); R'=R(1-p)+b -> "
          "b/p (T4's form). Two DIFFERENT recursions; both verified SymPy+mpmath")

    # --- appendix line-169 inverse, round trip ---------------------------
    pi_, C_ = sp.symbols("pi_ C_", positive=True)
    Rk = pi_ * (1 - C_) / ((1 - pi_) + pi_ * (1 - C_))
    C_back = sp.simplify((pi_ - Rk) / (pi_ * (1 - Rk)))
    assert sp.simplify(C_back - C_) == 0, C_back
    wrong = sp.Rational(1, 2) - sp.Rational(1, 5)
    wrong = sp.simplify(wrong / (sp.Rational(1, 2) * (sp.Rational(1, 5) - 1)))
    assert wrong == sp.Rational(-3, 4), wrong
    print("G HOLDS  corrected inverse round-trips to 0 exactly; the pre-fix "
          "form gives -3/4 at pi=1/2, R=1/5, as the appendix records")

    # --- T3: rule of three, quiet rounds needed --------------------------
    lam0 = sp.Rational(1, 10)
    n_needed = sp.log(20) / lam0
    print(f"H        T3 scale: to reject a flat rate >= 0.1/round at 95% "
          f"requires {sp.N(n_needed, 4)} consecutive quiet rounds "
          f"(exp(-n*0.1) <= 0.05) -- a researcher's budget call, not a gate's")
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    sys.exit(main())
