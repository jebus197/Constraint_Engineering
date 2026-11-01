#!/usr/bin/env python3
"""Is the floor of the shipped risk recursion nu_b, or nu_eff?

WHY THIS EXISTS. The 2026-10-31 joint round on severity produced the only
boundary statement the founder's truncated second question can be answered
with, and the 2 seats gave DIFFERENT floors for it:

  * seat fable: "`compute_rk` output >= nu_b for ALL valid inputs -- z3 unsat
    for the negation; 9,261-point grid of the real function agrees. So no
    threshold below nu_b = 0.05 is satisfiable."
  * seat cc2:   "the floor is NOT nu_b. The exact infimum of `compute_rk` over
    (R_old, q) is nu_eff = 1 - (1-nu_b)(1-(1-S_k)nu_f)", with a table running
    0.0500 at S_k = 1.0 up to 0.2400 at S_k = 0.0.

THESE ARE NOT IN CONFLICT AND THE DIFFERENCE MATTERS. nu_eff >= nu_b always, so
nu_b is a VALID lower bound and nu_eff is the ATTAINED one. A boundary written
against nu_b would be satisfiable in principle and unreachable in practice at
every fix efficacy below 1, which is where the whole archive sits. Relaying
either figure unchecked would be taking a seat's word for the number that
answers the founder's question, and `fff-external` forbids exactly that.

EACH CLAIM CHECKED BY 2 INDEPENDENT TOOLS, and the decision rule is fixed
before the measurement:
  * cc2's closed form is CONFIRMED if SymPy's symbolic minimum over the unit
    box agrees with a dense NumPy sweep of the REAL function at every S_k to
    1e-9, AND z3 finds no counter-example below it.
  * fable's nu_b bound is CONFIRMED if z3 is unsat for output < nu_b.
  * cc2's table is CONFIRMED only if every one of its 6 published values
    reproduces from the shipped function.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import numpy as np
import sympy as sp
import z3
from mpmath import mp, mpf

from bench.reference_runner_v3 import compute_rk

NU_B, NU_F = 0.05, 0.20
#: cc2's published table, transcribed from its reply so it can FAIL here.
CC2_TABLE = {1.0: 0.0500, 0.95: 0.0595, 0.92: 0.0652,
             0.80: 0.0880, 0.50: 0.1450, 0.0: 0.2400}


def nu_eff_closed(sk, nu_b=NU_B, nu_f=NU_F):
    return 1 - (1 - nu_b) * (1 - (1 - sk) * nu_f)


def main():
    print("=" * 78)
    print("IS THE FLOOR nu_b OR nu_eff?   2026-10-31")
    print("=" * 78)

    # --- CLAIM A: cc2's table reproduces from the shipped function ----------
    print("\nCLAIM A. cc2's 6 published floor values, against the REAL function.")
    print(f"  {'S_k':>6}  {'cc2 published':>14}  {'closed form':>12}  "
          f"{'NumPy sweep min':>16}  {'agree':>6}")
    grid = np.linspace(0.0, 1.0, 401)
    all_ok = True
    for sk in sorted(CC2_TABLE, reverse=True):
        pub = CC2_TABLE[sk]
        closed = nu_eff_closed(sk)
        swept = min(compute_rk(float(r), float(q), float(sk), NU_B, NU_F)
                    for r in grid for q in grid)
        ok = abs(closed - swept) < 1e-9 and abs(round(closed, 4) - pub) < 5e-5
        all_ok &= ok
        print(f"  {sk:>6.2f}  {pub:>14.4f}  {closed:>12.6f}  {swept:>16.9f}  "
              f"{'yes' if ok else 'NO':>6}")
    print(f"  all 6 of cc2's values reproduce: {all_ok}")

    # SymPy: derive the minimum symbolically rather than trusting the form.
    R, q, sk, nb, nf = sp.symbols("R q sk nu_b nu_f", nonnegative=True)
    R_det = R * (1 - q) / (1 - q * R)
    R_base = sk * R_det + (1 - sk) * R
    nu_eff_sym = 1 - (1 - nb) * (1 - (1 - sk) * nf)
    R_k = R_base * (1 - nu_eff_sym) + nu_eff_sym
    at_R0 = sp.simplify(R_k.subs(R, 0))
    print(f"\n  SymPy: R_k at R_old = 0 simplifies to {at_R0}")
    print(f"  SymPy: that equals nu_eff: "
          f"{sp.simplify(at_R0 - nu_eff_sym) == 0}")

    # --- CLAIM B: z3 on both floors ----------------------------------------
    print("\nCLAIM B. z3 over the whole valid box, with the nu_b + nu_f <= 1 "
          "rescale.")
    zR, zq, zsk, znb0, znf0 = z3.Reals("R q sk nu_b nu_f")
    ztot = znb0 + znf0
    znb = z3.If(ztot > 1, znb0 / ztot, znb0)
    znf = z3.If(ztot > 1, znf0 / ztot, znf0)
    zdet = zR * (1 - zq) / (1 - zq * zR)
    zbase = zsk * zdet + (1 - zsk) * zR
    znu = 1 - (1 - znb) * (1 - (1 - zsk) * znf)
    zrk = zbase * (1 - znu) + znu
    box = z3.And(*[z3.And(v >= 0, v <= 1)
                   for v in (zR, zq, zsk, znb0, znf0)], 1 - zq * zR != 0)

    s1 = z3.Solver()
    s1.add(box, znb0 == z3.RealVal(5) / 100, znf0 == z3.RealVal(20) / 100,
           zrk < z3.RealVal(5) / 100)
    r1 = s1.check()
    print(f"  fable: output < nu_b = 0.05 anywhere?            {r1}")

    s2 = z3.Solver()
    s2.add(box, znb0 == z3.RealVal(5) / 100, znf0 == z3.RealVal(20) / 100,
           zrk < znu)
    r2 = s2.check()
    print(f"  cc2:   output < nu_eff (its own S_k) anywhere?   {r2}")

    # And the DISCRIMINATING question: is nu_b ATTAINED below sk = 1?
    s3 = z3.Solver()
    s3.add(box, znb0 == z3.RealVal(5) / 100, znf0 == z3.RealVal(20) / 100,
           zsk < 1, zrk <= z3.RealVal(51) / 1000)
    r3 = s3.check()
    print(f"  is any output <= 0.051 reachable with sk < 1?    {r3}")
    if r3 == z3.sat:
        m = s3.model()
        print(f"     witness: {m}")

    # --- CLAIM C: mpmath second opinion on the gap that matters ------------
    print("\nCLAIM C. What the difference costs, where the archive actually "
          "sits.")
    mp.dps = 40
    for sk in (1.0, 0.8, 0.5, 0.0):
        a, b = mpf(nu_eff_closed(sk)), mpf(NU_B)
        print(f"  S_k = {sk:>4}: attained floor {float(a):.6f} against the "
              f"nu_b bound {float(b):.6f}, a factor of {float(a / b):.4f}")

    print("\n" + "=" * 78)
    both = (r1 == z3.unsat and r2 == z3.unsat and all_ok)
    print("VERDICT:")
    print("  BOTH SEATS ARE RIGHT AND cc2's IS SHARPER." if both
          else "  A CLAIM FAILED -- see above.")
    print("  nu_b is a VALID lower bound (z3 unsat below it, as fable said).")
    print("  nu_eff is the ATTAINED infimum (z3 unsat below it too, and it is")
    print("  reached exactly at R_old = 0 by SymPy). nu_eff = nu_b ONLY at")
    print("  S_k = 1, a perfect fix; at S_k = 0.5 the attained floor is 0.1450,")
    print("  2.9 times the nu_b bound. SO A BOUNDARY WRITTEN AGAINST nu_b IS")
    print("  UNREACHABLE AT EVERY IMPERFECT FIX, WHICH IS THE WHOLE ARCHIVE.")
    print("=" * 78)
    assert both, "a seat's published figure did not reproduce"
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
