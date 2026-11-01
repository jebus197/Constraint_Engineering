#!/usr/bin/env python3
"""Can the R_k carry drive residual risk to exactly 1.0, where the admission
gate reads 1.0 as CORRUPTION rather than as high risk?

WHY THIS EXISTS. The carry tier was built on 2026-10-31 so that residual risk
accumulates across passes, which is what the founder's definition of severity
requires. It introduced a 4th precedence tier for `R_old`. Two comments in
`bench/reference_runner_v3.py` interact with it and were written BEFORE it:

  * `_sk_admits` (~:16979): "R == 1 IS A CORRUPTION SIGNAL, NOT AN OPERATING
    POINT (panel, cc2). ... `model_params` has 0 writers, so R_old is 0.5 on
    every real run and R == 1 is not otherwise reachable." At R == 1 the gate
    returns (False, 1.0) -- it refuses every fix.
  * the precedence block (~:17266): "the uniform base prior -- what every run
    from Exp 37 to Exp 49 actually used, because model_params is never
    populated."

THE CARRY FALSIFIES THE PREMISE OF THE FIRST COMMENT. `R_old` is no longer 0.5
on every real run: with the carry on it takes the value the run itself reached.
So "R == 1 is not otherwise reachable" has to be re-established, not assumed,
and the recursion's own fixed point is the reason to doubt it: with sk = 0 the
update is R <- 0.76*R + 0.24 under the default nu, whose fixed point is EXACTLY
1.0. The carry therefore pushes R toward the one value the gate treats as
corrupt.

WHAT THIS SCRIPT SETTLES, each claim with 2 independent tools:

  1. The exact conditions under which `compute_rk` returns 1.0 for FINITE
     inputs.                                            SymPy, then z3.
  2. Whether R_k < 1 strictly for R_old < 1 under the DEFAULT nu_b and nu_f,
     which are the only values reachable while `model_params` has 0 writers.
                                                        z3, then NumPy sweep.
  3. How many consecutive sk = 0 rounds it takes for the carried R to reach
     float64 1.0 exactly.                               NumPy, then mpmath.
  4. The margin against the configured round caps.      read from RunnerConfig.

DECISION RULE, fixed before the measurement:
  * LIVE DEFECT        if the rounds-to-latch is at or below a configured cap.
  * BOUNDED, RECORDED  if it exceeds every configured cap -- the carry cannot
                       latch the gate within a run, and the margin is stated.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import numpy as np
import sympy as sp
from mpmath import mp, mpf
import z3

from bench.reference_runner_v3 import compute_rk, RunnerConfig

NU_B_DEFAULT, NU_F_DEFAULT = 0.05, 0.20   # the model_params fallbacks


def rk_symbolic():
    """The recursion as SymPy expressions, mirroring compute_rk's 3 phases.

    ★ THE RESCALE IS PART OF THE FUNCTION AND WAS MISSING FROM THIS MODEL.
    `compute_rk` enforces a HARD CONSTRAINT nu_b + nu_f <= 1 by dividing BOTH by
    their sum when it exceeds 1. Without that, this model claimed nu_b = 1 was a
    route to R_k == 1 for any nu_f; EXECUTING the real function returned
    0.9305555555555556 for nu_b = 1, nu_f = 0.20. Modelling a function instead
    of executing it is the `execute-do-not-grep` failure in symbolic clothing,
    and the guard caught it, not the derivation.
    """
    R, q, sk, nb0, nf0 = sp.symbols("R q sk nu_b nu_f", nonnegative=True)
    # post-rescale parameters: divide by the sum only when it exceeds 1
    tot = nb0 + nf0
    nb = sp.Piecewise((nb0 / tot, tot > 1), (nb0, True))
    nf = sp.Piecewise((nf0 / tot, tot > 1), (nf0, True))
    R_det = R * (1 - q) / (1 - q * R)
    R_base = sk * R_det + (1 - sk) * R
    nu_eff = 1 - (1 - nb) * (1 - (1 - sk) * nf)
    return (R, q, sk, nb0, nf0), R_base * (1 - nu_eff) + nu_eff, nu_eff


def main():
    print("=" * 78)
    print("CAN THE R_k CARRY LATCH THE ADMISSION GATE AT R == 1?   2026-10-31")
    print("=" * 78)

    # ---- CLAIM 1: when is R_k == 1 with finite inputs? ------------------
    print("\nCLAIM 1. Exact conditions for R_k == 1 (finite inputs).")
    print("  compute_rk rescales nu_b and nu_f to satisfy nu_b + nu_f <= 1, so")
    print("  the parameter routes can only sit at the CORNERS of that constraint.")

    # z3, with the rescale encoded exactly as the function applies it.
    zR, zq, zsk, znb0, znf0 = z3.Reals("R q sk nu_b nu_f")
    ztot = znb0 + znf0
    znb = z3.If(ztot > 1, znb0 / ztot, znb0)
    znf = z3.If(ztot > 1, znf0 / ztot, znf0)
    zdet = zR * (1 - zq) / (1 - zq * zR)
    zbase = zsk * zdet + (1 - zsk) * zR
    znu = 1 - (1 - znb) * (1 - (1 - zsk) * znf)
    zrk = zbase * (1 - znu) + znu
    in_unit = z3.And(*[z3.And(v >= 0, v <= 1)
                       for v in (zR, zq, zsk, znb0, znf0)])
    s = z3.Solver()
    # Exclude the 3 known routes and ask for a 4th.
    s.add(in_unit, 1 - zq * zR != 0, zrk == 1, zR < 1,
          z3.Not(z3.And(znb == 1, znf == 0)),
          z3.Not(z3.And(zsk == 0, znf == 1, znb == 0)))
    r = s.check()
    print(f"  z3: a 4th route to R_k == 1 exists? {r}")
    assert r == z3.unsat, f"z3 found an unaccounted route: {s.model() if r == z3.sat else r}"
    print("  z3: the routes are R_old = 1, (nu_b, nu_f) = (1, 0), and")
    print("      (nu_b, nu_f) = (0, 1) with sk = 0 -- and nothing else.")

    # EXECUTION as the second tool, on the REAL function, including the cases
    # the un-rescaled model got wrong.
    print("  executing the REAL compute_rk on each:")
    for label, args, want_one in (
            ("R_old = 1",                (1.0, 0.5, 0.0, NU_B_DEFAULT, NU_F_DEFAULT), True),
            ("nu_b = 1, nu_f = 0",       (0.5, 0.5, 0.0, 1.0, 0.0), True),
            ("nu_f = 1, nu_b = 0, sk=0", (0.5, 0.5, 0.0, 0.0, 1.0), True),
            ("nu_b = 1, nu_f = 0.20",    (0.5, 0.5, 0.0, 1.0, NU_F_DEFAULT), False),
            ("nu_f = 1, nu_b = 0.05",    (0.5, 0.5, 0.0, NU_B_DEFAULT, 1.0), False),
            ("the live defaults",        (0.5, 0.5, 0.0, NU_B_DEFAULT, NU_F_DEFAULT), False)):
        got = compute_rk(*args)
        ok = (got == 1.0) == want_one
        print(f"    {label:26s} -> {got!r:22s} "
              f"{'== 1' if got == 1.0 else '< 1'}  {'ok' if ok else 'MISMATCH'}")
        assert ok, f"{label}: z3 and execution disagree"
    print("  z3 AND execution AGREE, including on the 2 cases the un-rescaled")
    print("  model called routes to 1 and the real function does not.")

    # ---- CLAIM 2: strict R_k < 1 under the DEFAULT nu ----------------------
    print("\nCLAIM 2. Under the default nu_b = 0.05, nu_f = 0.20, is R_k < 1 "
          "for every R_old < 1?")
    s2 = z3.Solver()
    s2.add(z3.And(zR >= 0, zR < 1), z3.And(zq >= 0, zq <= 1),
           z3.And(zsk >= 0, zsk <= 1), 1 - zq * zR != 0,
           znb0 == z3.RealVal(5) / 100, znf0 == z3.RealVal(20) / 100, zrk >= 1)
    r2 = s2.check()
    print(f"  z3: any R_old < 1 reaching R_k >= 1 at default nu? {r2}")
    assert r2 == z3.unsat, f"z3 counter-example: {s2.model() if r2 == z3.sat else r2}"
    # NumPy sweep as the second tool, executing the REAL function.
    grid = np.linspace(0.0, 1.0, 51)
    worst, worst_at = 0.0, None
    for r_old in grid[:-1]:
        for qq in grid:
            for s_k in grid:
                v = compute_rk(float(r_old), float(qq), float(s_k),
                               NU_B_DEFAULT, NU_F_DEFAULT)
                if v > worst:
                    worst, worst_at = v, (r_old, qq, s_k)
    print(f"  NumPy sweep over {len(grid)-1}x{len(grid)}x{len(grid)} = "
          f"{(len(grid)-1)*len(grid)**2} points of the REAL compute_rk:")
    print(f"    max R_k = {worst:.17g} at (R_old, q, sk) = {worst_at}")
    assert worst < 1.0, "the sweep reached 1.0, contradicting z3"
    print("  BOTH AGREE: strictly below 1 while model_params stays unpopulated.")

    # ---- CLAIM 3: does the sk = 0 iteration actually REACH 1.0? ----------
    # THE FIRST VERSION OF THIS CLAIM WAS WRONG IN BOTH DIRECTIONS AND THE 2
    # TOOLS DISAGREEING IS WHAT EXPOSED IT. It drove the real `compute_rk` in a
    # loop and reported "100000 rounds", which was its own iteration GUARD and
    # not a latch; and the mpmath closed form said 132, which is when the EXACT
    # error falls below 2^-53. Neither number was the answer, because in float64
    # the map R <- R*0.76 + 0.24 has an ATTRACTING FIXED POINT STRICTLY BELOW
    # 1.0: at R = 1 - 2*2^-53 the product rounds back to R, so the sequence
    # stalls there for ever. 1.0 is absorbing but UNREACHABLE FROM BELOW.
    print("\nCLAIM 3. Does the sk = 0 iteration REACH 1.0, or stall below it?")
    # SymPy derives the EXACT fixed point rather than this script asserting it.
    # `rk_symbolic` is called here, so the symbolic model is reached by something
    # instead of sitting unused beside the z3 one.
    (symR, symq, symsk, symnb, symnf), symRk, _symnu = rk_symbolic()
    at_sk0 = symRk.subs({symsk: 0, symnb: sp.Rational(5, 100),
                         symnf: sp.Rational(20, 100)})
    fixed = sp.solve(sp.Eq(at_sk0, symR), symR)
    print(f"  SymPy: at sk = 0 and the default nu, R_k(R) = {sp.simplify(at_sk0)}")
    print(f"  SymPy: its exact fixed points are {fixed}")
    assert sp.Integer(1) in fixed, (
        "the exact fixed point is no longer 1; the whole concern was that the "
        "carry climbs toward the value the gate reads as corrupt")
    nu_eff_0 = 1 - (1 - NU_B_DEFAULT) * (1 - NU_F_DEFAULT)
    print(f"  with sk = 0 the update is R <- R*(1-{nu_eff_0:.2f}) + {nu_eff_0:.2f}; "
          f"the EXACT fixed point is 1")
    r_np, n_np, stalled_at = 0.5, 0, None
    seen = set()
    while n_np < 100000:
        nxt = compute_rk(r_np, 0.5, 0.0, NU_B_DEFAULT, NU_F_DEFAULT)
        n_np += 1
        if nxt == r_np:            # a true float fixed point, bit for bit
            stalled_at = nxt
            break
        if nxt in seen:            # a cycle, not a fixed point
            stalled_at = nxt
            break
        seen.add(nxt)
        r_np = nxt
    print(f"  NumPy/float64 driving the REAL compute_rk: stationary after "
          f"{n_np} rounds")
    print(f"    stalled at R = {stalled_at!r}")
    print(f"    reached 1.0 exactly: {stalled_at == 1.0}")
    print(f"    distance below 1.0 in units of 2^-53: "
          f"{(1.0 - stalled_at) / 2 ** -53:.6g}")
    # mpmath SECOND TOOL, on the statement that actually matters: is the stall
    # point a fixed point of the ROUNDED map, and is it strictly below 1?
    mp.dps = 60
    nu = 1 - (mpf(1) - mpf("0.05")) * (1 - mpf("0.20"))
    exact_next = (mpf(stalled_at) * (1 - nu) + nu)
    print(f"  mpmath exact image of the stall point: {mp.nstr(exact_next, 20)}")
    print(f"    exact image exceeds the stall point:  "
          f"{exact_next > mpf(stalled_at)}")
    print(f"    yet rounds back to it in float64:     "
          f"{float(exact_next) == stalled_at}")
    assert stalled_at < 1.0, "the iteration reached 1.0, contradicting z3"
    assert float(exact_next) == stalled_at, "not a fixed point of the rounded map"
    print("  BOTH AGREE: the sequence rises, then STALLS strictly below 1.0. "
          "1.0 is")
    print("  absorbing but unreachable from below, so the carry cannot produce it.")

    # ---- CLAIM 4: the ROUND caps, and only the round caps ---------------
    # THE FIRST VERSION COMPARED A ROUND COUNT AGAINST 28800, WHICH IS SECONDS.
    # It collected every int attribute whose name contained "round" or "cap",
    # which swept in `wall_clock_cap_s = 28800` (an 8-hour wall clock) and, because
    # `isinstance(True, int)` is True in Python, the boolean
    # `sk_carry_rk_across_rounds` as well. Comparing rounds to seconds is the
    # wrong-unit failure this project's own record names: a right figure under
    # the wrong denominator reads perfectly.
    print("\nCLAIM 4. The round budget, named explicitly rather than matched.")
    cfg = RunnerConfig()
    ROUND_FIELDS = ("max_rounds", "extension_cap")
    budget = 0
    for k in ROUND_FIELDS:
        v = getattr(cfg, k)
        assert isinstance(v, int) and not isinstance(v, bool), f"{k} is not an int"
        print(f"    {k:18s} {v}")
        budget += int(v)
    print(f"  most rounds a single run can execute: {budget}")
    print("  (excluded by name, not by pattern: wall_clock_cap_s is SECONDS, and "
          "sk_carry_rk_across_rounds is a bool)")

    print("\n" + "=" * 78)
    print(f"stationary after {n_np} rounds at R = {stalled_at!r}, which is "
          f"{(1.0 - stalled_at) / 2 ** -53:.0f} ulp below 1.0")
    print(f"a run executes at most {budget} rounds")
    print("VERDICT: NOT REACHABLE — and NOT because of the round budget")
    print("  -> z3 proves R_k < 1 strictly for every R_old < 1 at the default nu,")
    print("     and float64 iteration stalls 2 ulp below 1.0 for ever. So the")
    print("     carry cannot put the gate into its R == 1 branch at all.")
    print("  -> the carry is also per-run: `_rk_carry` is created immediately")
    print("     before the round loop, so nothing survives into another run.")
    print("\nWHAT IS NONETHELESS OWED, AND IT IS A COMMENT RATHER THAN CODE:")
    print("  the note at `_sk_admits` justifies 'R == 1 is not otherwise")
    print("  reachable' with 'model_params has 0 writers, so R_old is 0.5 on")
    print("  every real run'. Its CONCLUSION survives; its PREMISE does not,")
    print("  because the carry makes R_old the value the run reached.")
    print("\nAND A PRECONDITION ON THE model_params BUILD, WHICH IS THE NEXT ONE:")
    print("  R_k == 1 IS reachable with finite inputs when nu_b = 1, or when")
    print("  sk = 0 with nu_f = 1. Both are unreachable only because")
    print("  `model_params` is never populated and the fallbacks are 0.05 and")
    print("  0.20. Whoever populates it must either keep nu_b < 1 and nu_f < 1")
    print("  or stop treating R == 1 as proof of corruption.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
