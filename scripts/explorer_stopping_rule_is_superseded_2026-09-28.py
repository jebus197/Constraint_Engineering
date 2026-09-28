#!/usr/bin/env python3
"""Does the PUBLISHED explorer apply a stopping rule the appendix has retired?

THE QUESTION, the founder's, 2026-09-28: does `explorer/index.html` need revising
in light of the maths-model work, and do Astra's earlier proposed revisions still
apply?

WHAT THE EXPLORER DOES, read from the file. Line 83 labels its slider
`theta  stopping threshold on ΔR`. Line 294 colours a pass green exactly when
`s.dR >= o.theta`. Line 176 defines `dR = R_old - R_new` over the recursion
`R_det = R(1-q)/(1-qR)`, `R_base = sigma*R_det + (1-sigma)*R_old`,
`R_new = R_base*(1-nu) + nu`. So dR IS presented to a reader as a stop/continue
decision.

WHAT THE APPENDIX SAYS. `docs/MATHEMATICAL_APPENDIX.md` line 205 states the same
rule -- "continue while sum_k w_k * dR_k > theta". Line 217, added 2026-09-21,
RETIRES it: dR is the change conditional on the non-detection branch, while the
decision is taken before the branch is known. Line 225 gives the general
expected improvement, and line 223 records that `R*q` -- the quantity Astra's
review proposed -- is only the sigma=1, nu=0 corner and overstates elsewhere.

WHAT THIS SCRIPT ESTABLISHES, rather than asserts:
  1. the explorer's dR is algebraically the conditional quantity (SymPy identity);
  2. how often the explorer's rule and the appendix's general rule DISAGREE about
     stopping, over the explorer's own slider ranges;
  3. the DIRECTION of each disagreement, because a rule that stops too early and
     one that runs too long are different defects.

Cross-checked on SymPy (symbolic) and mpmath at 50 dps (numeric), per the
project's 2-tool requirement. Wolfram is deliberately NOT called: this file is a
committed falsifier and a falsifier may not require an installed kernel.
"""
from __future__ import annotations

import itertools

import mpmath as mp
import sympy as sp

mp.mp.dps = 50


def explorer_dR_sym(R, q, sigma, nu):
    """The explorer's per-pass change, transcribed from explorer/index.html:176."""
    R_det = R * (1 - q) / (1 - q * R)
    R_base = sigma * R_det + (1 - sigma) * R
    R_new = R_base * (1 - nu) + nu
    return R - R_new


def appendix_expected(R, q, sigma, nu):
    """MATHEMATICAL_APPENDIX.md:225 -- the general expected improvement."""
    return R * q * sigma * (1 - nu) - nu * (1 - R)


def identity_check() -> None:
    R, q, sigma, nu = sp.symbols("R q sigma nu", positive=True)
    dR = explorer_dR_sym(R, q, sigma, nu)

    corner = sp.simplify(dR.subs({sigma: 1, nu: 0}))
    astra_conditional = sp.simplify(R * q * (R - 1) / (R * q - 1))
    same = sp.simplify(corner - astra_conditional) == 0
    print("1. IS THE EXPLORER'S dR THE CONDITIONAL QUANTITY?")
    print(f"   explorer dR at sigma=1, nu=0   {sp.simplify(corner)}")
    print(f"   conditional R*q*(R-1)/(R*q-1)  {astra_conditional}")
    print(f"   symbolically identical         {same}")

    gen = sp.simplify(appendix_expected(R, q, sigma, nu))
    diff = sp.simplify(sp.expand(gen - dR))
    print()
    print("2. GENERAL EXPECTED IMPROVEMENT MINUS THE EXPLORER'S dR")
    print(f"   appendix general form          {gen}")
    print(f"   difference (general - dR)      {sp.factor(diff)}")
    print(f"   zero everywhere?               {sp.simplify(diff) == 0}")


def disagreement_sweep(theta: float = 0.005) -> None:
    """How often, and in which direction, the 2 rules disagree about stopping.

    theta defaults to the explorer's own default (index.html:84, value="0.005").
    Grids are the explorer's own slider ranges.
    """
    Rs = [mp.mpf(x) / 100 for x in range(5, 100, 5)]
    qs = [mp.mpf(x) / 100 for x in range(5, 100, 5)]
    sigmas = [mp.mpf(x) / 10 for x in range(1, 11)]
    nus = [mp.mpf(0), mp.mpf("0.02"), mp.mpf("0.05"), mp.mpf("0.1")]
    th = mp.mpf(str(theta))

    n = stop_early = run_long = 0
    worst_early = (mp.mpf(0), None)
    for R, q, s, v in itertools.product(Rs, qs, sigmas, nus):
        d = explorer_dR_sym(R, q, s, v)
        e = appendix_expected(R, q, s, v)
        exp_continue = d >= th          # what the explorer shows as "good"
        app_continue = e >= th          # what the appendix's rule says
        n += 1
        if app_continue and not exp_continue:
            stop_early += 1
            gap = e - d
            if gap > worst_early[0]:
                worst_early = (gap, (R, q, s, v, d, e))
        elif exp_continue and not app_continue:
            run_long += 1

    print()
    print(f"3. DISAGREEMENT OVER THE EXPLORER'S OWN SLIDER RANGES, theta={theta}")
    print(f"   grid points                    {n}")
    print(f"   explorer STOPS, appendix CONTINUES   {stop_early} = {100.0*stop_early/n:.4f}%")
    print(f"   explorer CONTINUES, appendix STOPS   {run_long} = {100.0*run_long/n:.4f}%")
    if worst_early[1]:
        R, q, s, v, d, e = worst_early[1]
        print(f"   widest premature stop          R={float(R):.2f} q={float(q):.2f} "
              f"sigma={float(s):.1f} nu={float(v):.2f}")
        print(f"       explorer dR                {mp.nstr(d, 8)}  (below theta -> shown grey)")
        print(f"       appendix expected          {mp.nstr(e, 8)}  (above theta -> continue)")
        print(f"       ratio                      {mp.nstr(e/d, 8)}x")

    # The founder's own worked point, from the 2026-09-24 correction.
    R, q = mp.mpf("0.99"), mp.mpf("0.3")
    d = explorer_dR_sym(R, q, mp.mpf(1), mp.mpf(0))
    e = appendix_expected(R, q, mp.mpf(1), mp.mpf(0))
    print()
    print("4. THE WORKED POINT R=0.99, q=0.3, sigma=1, nu=0")
    print(f"   explorer dR                    {mp.nstr(d, 12)}")
    print(f"   appendix expected (= R*q)      {mp.nstr(e, 12)}")
    print(f"   ratio                          {mp.nstr(e/d, 12)}x")
    print(f"   at theta=0.005 the explorer shows {'GREY (stop)' if d < mp.mpf('0.005') else 'GREEN (continue)'}"
          f", the appendix says {'CONTINUE' if e >= mp.mpf('0.005') else 'STOP'}")


def main() -> int:
    print("EXPLORER STOPPING RULE vs THE APPENDIX'S GENERAL FORM")
    print("=" * 62)
    identity_check()
    disagreement_sweep()
    print()
    print("Astra's proposed R*q is the sigma=1, nu=0 corner only (appendix:223),")
    print("so it is not the revision to apply either.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
