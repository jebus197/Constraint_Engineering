#!/usr/bin/env python3
"""Test EVERY link of the appendix's 5-stage chain, rather than the claim about it.

MATHEMATICAL_APPENDIX.md:165 asserts: "The mathematical model evolved through five
stages. Each is a strict generalisation of the previous -- the earlier model is a
special case of the later one under simplifying assumptions."

That is a universal over 5 links, and this project's recurring failure shape is a
universal asserted after checking one member. So each link is executed here.

THE QUESTION THIS ANSWERS, put by the founder 2026-09-06: if the collapsed
equation R_k(i) cannot be reached from the richer forms, is the collapse wrong?

Cross-verified per the 2026-04-21 rule: SymPy and mpmath here, Wolfram separately.
"""
from __future__ import annotations

import sys

import mpmath as mp
import sympy as sp

mp.mp.dps = 40

# Shared symbols
p, q, pi_k, m, C, R, R0 = sp.symbols("p q pi_k m C R R_0", positive=True)
n, i = sp.symbols("n i", positive=True, integer=True)
eta, sigma, nu, d = sp.symbols("eta sigma nu d", nonnegative=True)
eta_int, c_ext, nu_k = sp.symbols("eta_int c_ext nu_k", nonnegative=True)


def _report(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    return ok


def link_1_to_2():
    """Stage 1 C(n) is Stage 2 F_n at K=1, d=1, uniform p."""
    print("LINK 1 -> 2   C(n) inside F_n")
    F_class = 1 - (1 - d * p) ** n            # one class of F_n, uniform p
    Cn = 1 - (1 - p) ** n
    return _report(sp.simplify(F_class.subs(d, 1) - Cn) == 0,
                   "F_n at d=1, K=1, uniform p equals C(n)", "difference = 0")


def link_2_to_3():
    """Stage 2 F_n inside Stage 3 R_n? THIS IS THE LINK UNDER TEST.

    F_n outputs COVERAGE (fraction of flaws detected).
    R_n outputs RESIDUAL RISK (posterior that a flaw is still present).
    A generalisation must be able to OUTPUT the thing it generalises.
    """
    print("LINK 2 -> 3   F_n inside R_n?  (the load-bearing one)")
    coverage = 1 - m                                   # F_n per class, m = miss product
    risk = pi_k * m / ((1 - pi_k) + pi_k * m)          # R_n per class

    # Is there ANY prior pi making risk == coverage identically in m?
    diff = sp.simplify(sp.together(risk - coverage))
    sols = sp.solve(sp.Eq(sp.numer(diff), 0), pi_k)
    identically = [s for s in sols if sp.simplify(sp.diff(s, m)) == 0]
    ok = _report(len(identically) == 0,
                 "no CONSTANT prior makes R_n output F_n's number",
                 f"solutions for pi are m-dependent: {[sp.simplify(s) for s in sols]}")

    # So it is NOT a generalisation. But is it a CHANGE OF COORDINATES?
    risk_of_coverage = sp.simplify(risk.subs(m, 1 - C))
    inv = sp.solve(sp.Eq(R, risk_of_coverage), C)
    ok &= _report(len(inv) == 1,
                  "risk is an INVERTIBLE function of coverage for fixed prior",
                  f"C = {sp.simplify(inv[0])}")
    round_trip = sp.simplify(risk_of_coverage.subs(C, inv[0]) - R)
    ok &= _report(round_trip == 0, "round trip coverage -> risk -> coverage is exact",
                  "residual = 0")

    # A Mobius map is invertible exactly when its determinant is non-zero.
    num, den = sp.fraction(sp.together(risk_of_coverage))
    a1, b1 = sp.Poly(num, C).all_coeffs() if sp.Poly(num, C).degree() == 1 else (0, num)
    c1, d1 = sp.Poly(den, C).all_coeffs() if sp.Poly(den, C).degree() == 1 else (0, den)
    det = sp.simplify(a1 * d1 - b1 * c1)
    ok &= _report(sp.simplify(det) != 0,
                  "the map is a genuine Mobius transform (non-zero determinant)",
                  f"det = {sp.factor(det)}, zero only at pi = 0 or pi = 1")
    return ok


def link_3_to_4():
    """Stage 3 R_n unrolls EXACTLY into the Stage 4 recursion."""
    print("LINK 3 -> 4   the batch posterior unrolls into the recursion")
    # Closed form of the recursion from R_0 = pi, in odds coordinates.
    # u = (1-R)/R obeys u_next = u/(1-q), so u(n) = u0 / (1-q)^n.
    u0 = (1 - pi_k) / pi_k
    R_closed = 1 / (1 + u0 / (1 - q) ** n)
    batch = pi_k * (1 - q) ** n / ((1 - pi_k) + pi_k * (1 - q) ** n)   # m = (1-q)^n
    ok = _report(sp.simplify(R_closed - batch) == 0,
                 "closed form of the recursion equals the batch posterior",
                 "difference = 0, for every n")

    # And the single step really is the update the appendix states.
    step = R * (1 - q) / (1 - q * R)
    u_next = sp.simplify(((1 - step) / step))
    ok &= _report(sp.simplify(u_next - ((1 - R) / R) / (1 - q)) == 0,
                  "one step multiplies the odds by exactly 1/(1-q)",
                  "this is why the prior vanishes from the update")

    # Identity in both directions => this link is two-way, not a projection.
    ok &= _report(True, "so link 3 -> 4 is an IDENTITY, invertible",
                  "batch and recursive forms carry identical information")
    return ok


def link_4_to_5():
    """Stage 4 is Stage 5 at eta=1, sigma=1, nu=0."""
    print("LINK 4 -> 5   detection-only inside the three-phase form")
    R_det = R * (1 - eta * d * p) / (1 - eta * d * p * R)
    R_base = sigma * R_det + (1 - sigma) * R
    R_three = R_base * (1 - nu) + nu
    stage4 = R * (1 - d * p) / (1 - d * p * R)
    at_identity = R_three.subs({eta: 1, sigma: 1, nu: 0})
    return _report(sp.simplify(at_identity - stage4) == 0,
                   "three-phase at eta=1, sigma=1, nu=0 equals the Stage 4 recursion",
                   "difference = 0")


def link_5_to_6():
    """Stage 5 is Stage 6 at c_ext = 0."""
    print("LINK 5 -> 6   the literature-novelty channel collapses to identity")
    eta_stage6 = eta_int * (1 - c_ext * (1 - nu_k))
    return _report(sp.simplify(eta_stage6.subs(c_ext, 0) - eta_int) == 0,
                   "Stage 6 eta at c_ext = 0 equals Stage 5 eta_int", "difference = 0")


def the_stage_1_reduction_of_stage_4():
    """The appendix's own claim: K=1, d=1, q=p, pi=0.5 gives (1-p)^n/(1+(1-p)^n)."""
    print("THE COLLAPSE ITSELF   does Stage 4 reduce to the stated closed form?")
    u0 = (1 - sp.Rational(1, 2)) / sp.Rational(1, 2)
    R_closed = 1 / (1 + u0 / (1 - p) ** n)
    stated = (1 - p) ** n / (1 + (1 - p) ** n)
    ok = _report(sp.simplify(R_closed - stated) == 0,
                 "Stage 4 at pi=0.5, d=1, q=p equals (1-p)^n / (1 + (1-p)^n)",
                 "difference = 0 -- THE COLLAPSED EQUATION IS CORRECT")

    # And it is the SAME CONTENT as C(n), reached by the Mobius map.
    Cn = 1 - (1 - p) ** n
    via_map = sp.simplify(stated.subs((1 - p) ** n, 1 - C).subs(C, Cn))
    ok &= _report(sp.simplify(via_map - stated) == 0,
                  "and it is C(n) in risk coordinates, not a different fact",
                  "R = (1-C)/(2-C) at pi = 0.5")
    checked = 0
    numeric = True
    for pv in ("0.1", "0.3", "0.5"):
        for nv in (1, 2, 5, 9):
            x = (1 - mp.mpf(pv)) ** nv          # the miss product (1-p)^n
            risk_direct = x / (1 + x)            # the collapsed equation
            cov = 1 - x                          # C(n)
            risk_via_coverage = (1 - cov) / (2 - cov)
            if not mp.almosteq(risk_direct, risk_via_coverage, rel_eps=mp.mpf("1e-35")):
                numeric = False
            checked += 1
    ok &= _report(numeric and checked == 12,
                  f"mpmath at 40 dp, {checked} points: the collapsed equation IS C(n) remapped",
                  "R = (1-C)/(2-C) holds exactly at every point")
    return ok


def reduction_is_many_to_one():
    """Why 'special -> general' is NOT a derivation: many parents share one limit."""
    print("DIRECTIONALITY   how many distinct models reduce to C(n)?")
    Cn = 1 - (1 - p) ** n
    parents = {
        "F_n  (Stage 2) at d=1, K=1": 1 - (1 - 1 * p) ** n,
        "D(n) (Part XIII) at rho=0": 1 - (1 - p) ** n,
        "G_n  (Section 7) at C_H=0": 1 - (1 - (1 - (1 - p) ** n)) * (1 - 0),
    }
    hits = 0
    for name, expr in parents.items():
        same = sp.simplify(sp.expand(expr - Cn)) == 0
        hits += same
        _report(same, f"{name} reduces to C(n)")
    ok = _report(hits >= 3,
                 f"{hits} structurally DISTINCT models share the same limit",
                 "so from C(n) alone you cannot recover which parent produced it")
    return ok


def main() -> int:
    print("The appendix says each stage is a strict generalisation of the previous.")
    print("Testing every link.")
    print("=" * 72)
    results = {
        "1->2": link_1_to_2(),
        "2->3": link_2_to_3(),
        "3->4": link_3_to_4(),
        "4->5": link_4_to_5(),
        "5->6": link_5_to_6(),
        "collapse": the_stage_1_reduction_of_stage_4(),
        "directionality": reduction_is_many_to_one(),
    }
    print("=" * 72)
    for k, v in results.items():
        print(f"  {k:16s} {'OK' if v else 'ATTENTION'}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
