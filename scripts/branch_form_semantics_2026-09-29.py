#!/usr/bin/env python3
"""What the 2 branch forms MEAN, derived rather than asserted (item 4, 2026-09-29).

The shipped runner (`bench/reference_runner_v3.py::compute_rk`, phases 1-2) uses

    A(R) = sigma * B_minus + (1 - sigma) * R,    B_minus = R(1-q)/(1-qR)

Astra proposes the branch-weighted expectation

    M(R) = R * (1 - q*sigma)

The panel brief treats this as a choice between two candidate formulas. It is
not a choice between rival estimators of one quantity: the two are answers to
DIFFERENT questions, and this script derives which question each answers, from
the probability model alone.

MODEL. One latent flaw is present with prior probability R. A pass detects it
with probability q (no false positives: an absent flaw is never "detected").
When detected, the repair removes it with probability sigma.

    P(flaw & detected)     = R*q
    P(flaw & not detected) = R*(1-q)
    P(not detected)        = R*(1-q) + (1-R) = 1 - q*R

DERIVED BELOW, not asserted:

  1. M(R) is the UNCONDITIONAL (marginal) survival probability -- the pre-pass
     expectation, averaged over both branches:
         P(flaw survives) = R*[(1-q) + q*(1-sigma)] = R*(1-q*sigma) = M(R).

  2. B_minus is the POSTERIOR GIVEN THE NEGATIVE BRANCH, by Bayes:
         P(flaw | not detected) = R(1-q)/(1-qR) = B_minus.

  3. A(R) is a sigma-mixture of that negative-branch posterior with the prior:
         A = R + sigma*(B_minus - R),  exactly linear in sigma (d2A/dsigma2 = 0).
     At sigma=1 it IS B_minus and at sigma=0 it IS R.

     CORRECTED 2026-09-29, ON AN EXTERNAL REVIEW, AND THE ORIGINAL WORDING WAS
     WRONG. This paragraph used to conclude "so A is a CONDITIONAL quantity".
     That does not follow from an endpoint: a mixture that coincides with a
     posterior at one end of its range is not that posterior in between. The
     reviewer's counterexample, R=1/2, q=4/5, sigma=1/2, gives 4 DISTINCT values:
         B_minus (risk | negative) = 1/6
         M       (pre-pass expectation) = 3/10
         A       (the shipped blend) = 1/3
         M / P(negative) = 1/2
     A is none of the other three. SymPy and Wolfram Language both return
     sigma == 1 as the ONLY solution of A == B_minus on the open domain.
     A is therefore a RETAINED BLEND, not a calibrated conditional probability,
     and it is kept for gate compatibility rather than because it is one.

  4. A - M = sigma*q*R^2*(1-q)/(1-qR) >= 0 on [0,1]^3, so the shipped form is
     never below the expectation. Switching the runner from A to M can only
     LOWER reported residual risk, i.e. only ever make a convergence gate
     EASIER to pass. That asymmetry, not the algebra, is the decision.

  5. The identity that pins the interpretation, AND ITS SCOPE, which the
     original text of this docstring omitted: at sigma=1, and ONLY there,
         A = M / P(not detected).
     There A is the joint divided by the branch probability -- a conditional --
     and M is the joint, so they are quotient and numerator of one fraction.
     AWAY FROM sigma=1 THE QUOTIENT IS FALSE: at R=1/2, q=4/5, sigma=1/2 it
     gives 1/2 while A is 1/3. Wolfram Language returns sigma == 1 as the only
     solution on the open domain. What survives for ALL sigma is claim 4's
     inequality and the branch average q*R*(1-sigma) + (1-q*R)*B_minus == M.

Every claim above is checked with SymPy (primary), and claim 4's closed form was
independently confirmed with Wolfram Language (local Wolfram Engine, via
wolframscript) during the 2026-09-29 panel round. This STORED falsifier does not
call Wolfram, per the brief's rule.

Exit 0 and print FALSIFIER-CLEAN when every derivation holds; AssertionError
otherwise.
"""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

REPO = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    # A `--help` MUST NEVER RUN THE MEASUREMENT. Added by CC1 on adoption:
    # this script arrived from a panel seat without an argument parser, and
    # `test_help_is_answered_2026-09-11.py` caught it on the first full suite
    # run after it landed. The seat was not asked for one and the omission is
    # CC1's for adopting the file without checking the project's own rule.
    import argparse

    argparse.ArgumentParser(
        description="Derive and verify the 2 branch forms of the risk update: "
                    "the retained negative-branch blend A(R) and the pre-pass "
                    "expectation M(R). Read-only; spends nothing, calls no model."
    ).parse_args(argv)
    R, q, s = sp.symbols("R q sigma", nonnegative=True)

    B_minus = R * (1 - q) / (1 - q * R)
    A = s * B_minus + (1 - s) * R
    M = R * (1 - q * s)

    # --- 1. M is the marginal survival probability -------------------------
    marginal = R * ((1 - q) + q * (1 - s))
    assert sp.simplify(marginal - M) == 0, sp.simplify(marginal - M)
    print("1. M(R) = R[(1-q) + q(1-sigma)] = R(1-q*sigma)      -- marginal, VERIFIED")

    # --- 2. B_minus is the Bayes posterior on the negative branch ----------
    joint_not_detected = R * (1 - q)
    p_not_detected = R * (1 - q) + (1 - R)
    bayes = joint_not_detected / p_not_detected
    assert sp.simplify(bayes - B_minus) == 0, sp.simplify(bayes - B_minus)
    print("2. P(flaw | not detected) = R(1-q)/(1-qR) = B_minus -- Bayes,    VERIFIED")

    # --- 3. A is conditional: at sigma=1 it is exactly B_minus -------------
    assert sp.simplify(A.subs(s, 1) - B_minus) == 0
    assert sp.simplify(A.subs(s, 0) - R) == 0
    print("3. A(sigma=1) = B_minus and A(sigma=0) = R          -- mixture,  VERIFIED")

    # --- 4. the difference, and its sign ----------------------------------
    diff = sp.simplify(sp.together(A - M))
    want = s * q * R**2 * (1 - q) / (1 - q * R)
    assert sp.simplify(diff - want) == 0, diff
    print(f"4. A - M = {want}")
    # SIGN, DECIDED BY A SOLVER, NOT BY INSPECTION. The expression is
    # nonlinear in 3 variables; SymPy cannot reduce a multivariate inequality,
    # so the question "is A - M ever negative on the open unit cube" is put to
    # z3 as a satisfiability problem. UNSAT is a proof over the reals, not a
    # sample.
    import z3
    zR, zq, zs = z3.Reals("R q sigma")
    solver = z3.Solver()
    solver.add(zR > 0, zR < 1, zq > 0, zq < 1, zs > 0, zs < 1)
    # 1 - q*R > 0 on the cube, so multiplying through preserves the sign and
    # keeps the query polynomial.
    solver.add(zs * zq * zR * zR * (1 - zq) < 0)
    verdict = solver.check()
    assert verdict == z3.unsat, f"z3 found A - M < 0 at {solver.model()}"
    print(f"   z3: (A - M) < 0 on (0,1)^3 is {verdict} -- A >= M proved, VERIFIED")
    # independent numeric sweep, so a z3 API change cannot make this vacuous
    import itertools
    grid = [i / 20 for i in range(1, 20)]
    worst = min(float(want.subs({R: a, q: b, s: c}))
                for a, b, c in itertools.product(grid, grid, grid))
    assert worst >= 0.0, worst
    print(f"   sweep 19^3 = {len(grid)**3} points, min(A - M) = {worst:.6f} >= 0, "
          f"VERIFIED")

    # --- 5. the pinning identity ------------------------------------------
    ident = sp.simplify(A.subs(s, 1) - M.subs(s, 1) / p_not_detected)
    assert ident == 0, ident
    print("5. A = M / P(not detected) at sigma=1               -- cond/joint, VERIFIED")

    # --- the brief's worked numbers, exactly ------------------------------
    sub = {R: sp.Rational(1, 2), q: sp.Rational(4, 5), s: 1}
    a_val, m_val = sp.nsimplify(A.subs(sub)), sp.nsimplify(M.subs(sub))
    assert a_val == sp.Rational(1, 6), a_val
    assert m_val == sp.Rational(1, 10), m_val
    assert sp.nsimplify(B_minus.subs(sub)) == sp.Rational(1, 6)
    print(f"   at R=1/2, q=4/5, sigma=1:  A = {a_val}   M = {m_val}   "
          f"B_minus = {a_val}   -- brief's figures, VERIFIED")

    # --- the SHIPPED function agrees with A when re-injection is off -------
    # EXECUTE the repository's own code; do not retype it. nu_b=nu_f=0 strips
    # phase 3, exposing phases 1-2, which is the form under discussion.
    spec = importlib.util.spec_from_file_location(
        "rr3_branchcheck", REPO / "bench" / "reference_runner_v3.py")
    rr3 = importlib.util.module_from_spec(spec)
    sys.modules["rr3_branchcheck"] = rr3
    spec.loader.exec_module(rr3)
    checked = 0
    for Rv in (Fraction(1, 2), Fraction(1, 4), Fraction(9, 10)):
        for qv in (Fraction(4, 5), Fraction(1, 10)):
            for sv in (Fraction(1), Fraction(1, 2), Fraction(0)):
                got = rr3.compute_rk(float(Rv), float(qv), float(sv),
                                     nu_b=0.0, nu_f=0.0)
                want_a = float(A.subs({
                    R: sp.Rational(Rv.numerator, Rv.denominator),
                    q: sp.Rational(qv.numerator, qv.denominator),
                    s: sp.Rational(sv.numerator, sv.denominator)}))
                assert abs(got - want_a) < 1e-12, (Rv, qv, sv, got, want_a)
                checked += 1
    print(f"   compute_rk (nu off) == A(R) on {checked}/{checked} triples "
          f"-- the SHIPPED code is the blend form A, VERIFIED")

    # --- 6. THE COUNTEREXAMPLE THAT BOUNDS CLAIM 3 -------------------------
    # Added 2026-09-29 on an external review. Without this the file proved an
    # ENDPOINT and asserted a GENERAL interpretation, which is the shape of
    # error this project calls "a universal asserted after checking one member".
    Rv, qv, sv_ = sp.Rational(1, 2), sp.Rational(4, 5), sp.Rational(1, 2)
    sub = {R: Rv, q: qv, s: sv_}
    vals = {"B_minus (risk | negative)": B_minus.subs(sub),
            "M (pre-pass expectation)": (R * (1 - q * s)).subs(sub),
            "A (the shipped blend)": (s * B_minus + (1 - s) * R).subs(sub),
            "M / P(negative)": (R * (1 - q * s) / (1 - q * R)).subs(sub)}
    assert len(set(vals.values())) == 4, vals
    print("\n6. AT sigma=1/2 THE 4 QUANTITIES ARE DISTINCT -- A is none of the others:")
    for k, v in vals.items():
        print(f"     {k:<28} = {v}")
    only = sp.solve(sp.Eq(sp.simplify(s * B_minus + (1 - s) * R - B_minus), 0), s)
    assert only == [1], only
    print(f"   A == B_minus only at sigma = {only[0]}          -- endpoint, not identity, VERIFIED")

    print("\nFALSIFIER-CLEAN: all 6 derivations hold. A is a RETAINED BLEND that "
          "equals\n  the negative-branch posterior only at sigma=1; M is the pre-pass "
          "expectation;\n  A >= M always; and the quotient identity is an endpoint result.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
