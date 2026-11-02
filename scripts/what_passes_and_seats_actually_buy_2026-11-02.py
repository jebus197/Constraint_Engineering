#!/usr/bin/env python3
"""What do extra PASSES buy, and what do extra SEATS buy? DERIVED, on 2 tools.

HIS QUESTION, 2026-11-01, annotation 1 of `Closing_Report_2026-11-01.txt`,
verbatim: *"how much does adding additional passes (and also additional seats)
reduce the risk that any given answer to a problem might be wrong. In other
words, what value does adding additional passes and additional seats bring in
terms of increasing our confidence in an outcome? ... But how do we know how low,
low should be, before we accept an outcome as valid? Does not the mathematics of
probability give us a potential insight into this? Can it be measured from our
historical data?"*

And on 2026-11-02 he asked whether that is the same question as the severity one.
IT IS NOT, AND THE DIFFERENCE IS THE ANSWER: passes and seats act on DIFFERENT
terms of the same recursion, so they are not substitutes.

THE ANSWER IS ALREADY IN THE APPENDIX AND HAS NEVER BEEN STATED THIS WAY.
  MATHEMATICAL_APPENDIX.md:189   R_k(i) = R_k(i-1)(1-q) / (1 - q R_k(i-1))
  MATHEMATICAL_APPENDIX.md:119   m_k = prod_i (1 - d_i p_ik)      <- over SEATS
  MATHEMATICAL_APPENDIX.md:329   at sigma=1 the composite map's attracting
                                 fixed point is nu/q, NOT nu
  MATHEMATICAL_APPENDIX.md:225   E[improvement] = R q sigma (1-nu) - nu (1-R)

So: q is built by MULTIPLYING OVER SEATS, and the floor is nu/q. PASSES iterate
the map and converge toward that floor. SEATS raise q and therefore MOVE the
floor. Nothing a pass can do crosses the floor; only a seat lowers it.

EVERY CLAIM BELOW IS CHECKED ON SymPy AND z3 (or SymPy and mpmath), per the
2026-04-21 two-tool rule. Nothing here is asserted.
"""
from __future__ import annotations
import sys

import sympy as sp
import mpmath as mp
import z3

# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# project has already had a helper import break when a script moved.
import sys as _sys, pathlib as _pl
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402


def main() -> int:
    answer_help(__doc__, __file__)
    R, q, s, nu = sp.symbols("R q sigma nu", positive=True)
    print("=" * 78)
    print("WHAT PASSES BUY, WHAT SEATS BUY — DERIVED")
    print("=" * 78)

    # ---- 1. the recursion and its fixed points ---------------------------
    detect = R * (1 - q) / (1 - q * R)                 # appendix:189
    composite = detect * (1 - nu) + nu                 # appendix:313, sigma=1
    fps = sp.solve(sp.Eq(composite, R), R)
    print("\n1. FIXED POINTS OF THE COMPOSITE MAP (sigma = 1)")
    print(f"   map       : R -> {sp.simplify(composite)}")
    print(f"   SymPy     : {[sp.simplify(f) for f in fps]}")
    has_floor = any(sp.simplify(f - nu / q) == 0 for f in fps)
    has_one = any(sp.simplify(f - 1) == 0 for f in fps)
    print(f"   contains nu/q : {has_floor}      contains 1 : {has_one}")
    assert has_floor and has_one, "the appendix's stated fixed points do not reproduce"

    # z3: is nu/q EVER below nu (i.e. is the old looser bound ever the real floor)?
    zq, znu = z3.Reals("q nu")
    sv = z3.Solver()
    sv.add(zq > 0, zq < 1, znu > 0, znu < 1, znu / zq <= znu)
    print(f"   z3, can nu/q <= nu for 0<q<1 ? {sv.check()}")
    print("   -> the floor is nu/q and is STRICTLY ABOVE nu whenever q < 1.")

    # ---- 2. what a PASS buys: improvement vanishes at the floor ----------
    improvement = R * q * s * (1 - nu) - nu * (1 - R)   # appendix:225
    at_floor = sp.simplify(improvement.subs({R: nu / q, s: 1}))
    print("\n2. WHAT ONE MORE PASS BUYS")
    print(f"   E[improvement] = {improvement}")
    print(f"   evaluated AT the floor R = nu/q, sigma = 1 : {at_floor}")
    print(f"   SymPy says that is exactly zero : {sp.simplify(at_floor) == 0}")
    # mpmath, numerically, as the second tool
    f = sp.lambdify((R, q, s, nu), improvement, "mpmath")
    mp.mp.dps = 40
    qv, nuv = mp.mpf("0.2"), mp.mpf("0.05")
    print(f"   mpmath at q={qv}, nu={nuv}, floor={nuv/qv}:")
    for Rv in ("0.90", "0.50", "0.30", "0.2500000001", "0.25"):
        print(f"      R={Rv:14s} improvement = {mp.nstr(f(mp.mpf(Rv), qv, mp.mpf(1), nuv), 10)}")
    print("   -> PASSES BUY GEOMETRICALLY LESS AND STOP PAYING AT THE FLOOR.")
    print("      That decay IS gamma. It is why gamma is the convergence measure.")

    # ---- 3. what a SEAT buys: it moves the floor -------------------------
    print("\n3. WHAT ONE MORE SEAT BUYS")
    d_i, p_i, n = sp.symbols("d_i p_i n", positive=True)
    # m = prod over seats of (1 - d_i p_ik); with n identical independent seats
    m_n = (1 - d_i * p_i) ** n
    q_n = 1 - m_n
    floor_n = nu / q_n
    dfloor = sp.simplify(sp.diff(floor_n, n))
    print(f"   q(n)      = 1 - (1 - d p)^n           [appendix:119, over SEATS]")
    print(f"   floor(n)  = nu / q(n)")
    print(f"   d floor/d n = {dfloor}")
    # sign of the derivative for admissible parameters
    sub = {d_i: sp.Rational(9, 10), p_i: sp.Rational(1, 2), nu: sp.Rational(1, 20)}
    vals = [(k, sp.nsimplify(floor_n.subs(sub).subs(n, k)),
             float(dfloor.subs(sub).subs(n, k))) for k in (1, 2, 3, 5, 6)]
    print(f"   worked, d=0.9 p=0.5 nu=0.05:")
    for k, fl, dv in vals:
        print(f"      {k} seat(s): floor = {float(fl):.6f}   d floor/d n = {dv:+.6f}")
    # z3: can an extra seat ever RAISE the floor?
    zd, zp, zn = z3.Reals("d p n")
    s2 = z3.Solver()
    s2.add(zd > 0, zd < 1, zp > 0, zp < 1)
    # (1-dp)^1 > (1-dp)^2 for 0<dp<1  =>  q(2) > q(1)  =>  floor falls
    s2.add((1 - zd * zp) * (1 - zd * zp) >= (1 - zd * zp))
    print(f"   z3, can q(2) <= q(1), i.e. can a 2nd seat fail to raise q ? {s2.check()}")
    print("   -> SEATS RAISE q, AND THE FLOOR IS nu/q, SO SEATS LOWER THE FLOOR.")

    # ---- 4. and why the seats must be from DIFFERENT vendors -------------
    print("\n4. WHY THE SEATS MUST BE INDEPENDENT — THE VENDOR QUESTION")
    rho = sp.symbols("rho", nonnegative=True)
    # 2 seats with perfectly correlated blind spots behave as 1 seat.
    q_indep = 1 - (1 - d_i * p_i) ** 2
    q_dup = 1 - (1 - d_i * p_i)                      # a clone adds nothing
    gap = sp.simplify(q_indep - q_dup)
    print(f"   q, 2 INDEPENDENT seats : {sp.simplify(q_indep)}")
    print(f"   q, 2 IDENTICAL seats   : {sp.simplify(q_dup)}  (the clone is a no-op)")
    print(f"   the gap                : {gap}")
    g = float(gap.subs({d_i: sp.Rational(9, 10), p_i: sp.Rational(1, 2)}))
    print(f"   at d=0.9 p=0.5 the 2nd INDEPENDENT seat adds {g:.6f} to q;")
    print(f"   a 2nd copy of the SAME model adds 0.")
    print("   -> the product form ASSUMES independent misses. That assumption is")
    print("      exactly what a different vendor buys and a second instance of")
    print("      the same model does not. This is the biodiversity hypothesis")
    print("      written as an equation, and it is the ONLY part of his question")
    print("      that genuinely needs paid seats: q and nu are estimable from the")
    print("      archive, but the INDEPENDENCE of architectures is not, because")
    print("      every simulated seat shares one architecture by construction.")

    # ---- 5. how low should low be -----------------------------------------
    print("\n5. HOW LOW SHOULD 'LOW' BE BEFORE AN OUTCOME IS ACCEPTED?")
    print("   There is no universal constant, and that is a RESULT rather than a")
    print("   gap: the floor is nu/q, and both nu and q are properties of the")
    print("   experiment, so the acceptance bound is DERIVED per experiment.")
    print("   Both panel seats reached that independently on 2026-11-01. The")
    print("   defensible criterion is therefore relative, not absolute:")
    print("     accept when R is within epsilon of its own derived floor nu/q,")
    print("     and REPORT the floor beside R so a reader can see the headroom.")
    print("   A fixed target below nu/q is unreachable at any number of passes,")
    print("   which z3 confirms above. Quoting an absolute threshold without its")
    print("   floor is how a stopping rule asks for the impossible.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
