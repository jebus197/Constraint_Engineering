#!/usr/bin/env python3
"""Execute the reduction properties PAPER.md states for G_n, rather than reading them.

WHY THIS EXISTS. PAPER.md:528 is what the appendix calls the canonical formal
statement of G_n, and on 2026-09-05 the appendix's version of the same paragraph
was corrected while this one was left standing. cc2 found the gap. Two of its 5
claims did not survive execution:

  CLAIM 4, "Under uniform assumptions (K=1, d=1, uniform p), it reduces to C(n)"
  -- FALSE as stated. It omits the independence condition. With rho_MH = 0 the
  reduction does hold and is STRONGER than the paper claimed: G_n reduces to
  C(n_M + n_H), so human passes simply add to the machine's pass count. With
  rho_MH strictly between 0 and 1 there is NO pass count n for which G_n = C(n).

  CLAIM 5, "Every simpler model in this paper is a special case of G_n"
  -- FALSE. R_k(i) is not. It is a Mobius recursion with a pole at R = 1/q and a
  novelty floor nu, and the G_n kernel is a degree-3 POLYNOMIAL with no pole and
  no floor parameter. PAPER.md:1281 says in terms that R_k(i) SUPERSEDES C(n);
  a superseding model is not a special case of a model that predates it.

Cross-verification per the 2026-04-21 rule: SymPy and mpmath here, and Wolfram
Language separately (results computed with Wolfram Language, local kernel) --
Wolfram independently returned residual = C_H(C_M-1)(rho-1)w, the same 4-branch
zero set, G - C(n_M+n_H) = 0 at rho = 0, and False for
Exists[n in PositiveIntegers, C(n) = G] at the interior worked point.

Run: python3 scripts/verify_paper_reduction_properties.py
Exit 0 if every claim the corrected paragraph makes holds; 1 otherwise.
"""
from __future__ import annotations

import sys

import mpmath as mp
import sympy as sp

mp.mp.dps = 40

C_M, C_H, rho, w, p, q, R0, nu, R_det = sp.symbols(
    "C_M C_H rho w p q R_0 nu R_det", nonnegative=True
)
n_M, n_H = sp.symbols("n_M n_H", positive=True, integer=True)

# The per-class kernel exactly as PAPER.md states it.
G_kernel = 1 - (1 - C_M) * (1 - C_H * (1 - rho))
F_kernel = C_M


def _report(ok: bool, label: str, detail: str) -> bool:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {detail}")
    return ok


def check_residual() -> bool:
    """The exact G_n - F_n residual and its 4-branch zero set."""
    print("1. The residual, and the complete condition under which G_n = F_n")
    residual = sp.factor(sp.simplify(w * G_kernel - w * F_kernel))
    expected = w * C_H * (1 - C_M) * (1 - rho)
    ok = _report(
        sp.simplify(residual - expected) == 0,
        "residual is w*C_H*(1-C_M)*(1-rho)",
        f"{residual}",
    )
    branches = {"C_H = 0 (no human passes)": {C_H: 0},
                "C_M = 1 (machine already certain)": {C_M: 1},
                "rho_MH = 1 (human fully primed)": {rho: 1},
                "w_k = 0 (degenerate: class carries no weight)": {w: 0}}
    for name, sub in branches.items():
        ok &= _report(sp.simplify(residual.subs(sub)) == 0, f"zero branch {name}", "residual = 0")
    # And that no OTHER branch exists: the factored form is a product of 4 factors.
    factors = sp.factor_list(residual)[1]
    ok &= _report(len(factors) == 4, "exactly 4 zero branches",
                  f"{len(factors)} irreducible factors: {[str(f) for f, _ in factors]}")
    return ok


def check_rho_endpoints() -> bool:
    """rho = 0 gives multiplicative independence; rho = 1 gives machine-only."""
    print("2. The two correlation endpoints")
    indep = 1 - (1 - C_M) * (1 - C_H)
    ok = _report(sp.simplify(G_kernel.subs(rho, 0) - indep) == 0,
                 "rho_MH = 0 -> fully multiplicative independence", "difference = 0")
    ok &= _report(sp.simplify(G_kernel.subs(rho, 1) - F_kernel) == 0,
                  "rho_MH = 1 -> machine-only detection", "difference = 0")
    return ok


def check_uniform_reduction() -> bool:
    """CLAIM 4, corrected: the uniform limit is C(n_M + n_H), and only at rho = 0."""
    print("3. The uniform limit (K=1, d=1, uniform p) -- the claim that was wrong")
    C_Mu = 1 - (1 - p) ** n_M
    C_Hu = 1 - (1 - p) ** n_H
    G_u = 1 - (1 - C_Mu) * (1 - C_Hu * (1 - rho))
    Cn = lambda n: 1 - (1 - p) ** n

    ok = _report(sp.simplify(sp.expand(G_u.subs(rho, 0) - Cn(n_M + n_H))) == 0,
                 "at rho_MH = 0, G_n = C(n_M + n_H)", "symbolic difference = 0")
    ok &= _report(sp.simplify(sp.expand(G_u.subs(rho, 0) - Cn(n_M))) != 0,
                  "at rho_MH = 0, G_n is NOT C(n_M)", "the paper's unqualified 'C(n)' is wrong")

    # The interior counterexample: no pass count reproduces G_n once rho > 0.
    sub = {p: sp.Rational(1, 5), n_M: 3, n_H: 2, rho: sp.Rational(1, 2)}
    g_val = sp.nsimplify(G_u.subs(sub))
    n = sp.symbols("n", positive=True)
    solved = sp.solve(sp.Eq(Cn(n).subs(p, sp.Rational(1, 5)), g_val), n)
    non_integer = all(not sp.simplify(s).is_integer for s in solved)
    ok &= _report(non_integer,
                  "at p=1/5, n_M=3, n_H=2, rho=1/2 no INTEGER n gives C(n) = G_n",
                  f"G_n = {g_val} = {sp.N(g_val, 12)}, solving C(n)=G_n gives "
                  f"n = {[sp.N(s, 12) for s in solved]}")

    # mpmath, independently of SymPy.
    def G_num(pv, nm, nh, r):
        cm, ch = 1 - (1 - pv) ** nm, 1 - (1 - pv) ** nh
        return 1 - (1 - cm) * (1 - ch * (1 - r))

    pv = mp.mpf("0.2")
    ok &= _report(mp.almosteq(G_num(pv, 3, 2, mp.mpf(0)), 1 - (1 - pv) ** 5),
                  "mpmath agrees at rho = 0", "G_n = C(5) to 40 dp")
    ok &= _report(not mp.almosteq(G_num(pv, 3, 2, mp.mpf("0.5")), 1 - (1 - pv) ** 5),
                  "mpmath agrees at rho = 1/2", "G_n != C(5)")
    return ok


def check_r_k_is_not_nested() -> bool:
    """CLAIM 5: R_k(i) is not a special case of G_n. Two independent reasons."""
    print("4. The universal claim -- R_k(i) does not nest inside G_n")
    R_next = R0 * (1 - q) / (1 - q * R0)
    pole = sp.solve(sp.Eq(sp.denom(sp.together(R_next)), 0), R0)
    ok = _report(pole == [1 / q], "R_k(i) has a pole in R_k(i-1)", f"pole at R = {pole[0]}")
    ok &= _report(sp.denom(sp.together(G_kernel)) == 1,
                  "the G_n kernel has no pole", "it is a polynomial; denominator = 1")
    ok &= _report(sp.Poly(sp.expand(G_kernel), C_M, C_H, rho).total_degree() == 3,
                  "the G_n kernel is degree 3 in (C_M, C_H, rho)", "a polynomial family")
    # The novelty floor G_n has no parameter for.
    R_nu = R_det * (1 - nu) + nu
    ok &= _report(sp.limit(R_nu, R_det, 0) == nu,
                  "R_k(i) carries a novelty floor nu as R_det -> 0", "limit = nu")
    ok &= _report(sp.simplify(G_kernel.subs(C_M, 1)) == 1,
                  "G_n has no free floor at perfect detection", "C_M = 1 forces G_n = 1")
    return ok


def check_which_models_nest() -> bool:
    """The corrected universal: name the set, do not assert over it blindly.

    PAPER.md contains 4 detection/state models below G_n. This enumerates all of
    them and checks each, because the original claim was a universal asserted
    without the enumeration -- the project's own recurring failure shape.
    """
    print("5. Which models actually nest inside G_n -- the whole set, enumerated")
    p_i, d_i = sp.symbols("p_i d_i", nonnegative=True)

    # D(n) (PAPER.md:1041) is F_n's kernel with d_i = 1.
    F_class = 1 - (1 - d_i * p_i)          # one factor of F_n's product
    D_class = 1 - (1 - p_i)                # one factor of D(n)'s product
    ok = _report(sp.simplify(F_class.subs(d_i, 1) - D_class) == 0,
                 "D(n) nests: it is F_n at d_i = 1", "difference = 0")

    # C(n) is F_n at K=1, d=1, uniform p (PAPER.md:137).
    n = sp.symbols("n", positive=True, integer=True)
    ok &= _report(sp.simplify((1 - (1 - p) ** n) - (1 - (1 - 1 * p) ** n)) == 0,
                  "C(n) nests: F_n at K=1, d=1, uniform p", "difference = 0")

    # F_n nests in G_n by the C_H = 0 branch, already shown in check 1.
    ok &= _report(sp.simplify(G_kernel.subs(C_H, 0) - F_kernel) == 0,
                  "F_n nests: G_n at C_H = 0", "difference = 0")

    # R_k(i) does NOT -- established in check 4 by pole and by floor.
    ok &= _report(True, "R_k(i) does NOT nest",
                  "shown in check 4: pole at 1/q and a novelty floor nu, "
                  "neither expressible in a polynomial kernel")
    return ok


def check_distributed_compute_reduction() -> bool:
    """PAPER.md:1111 says "Verified computationally" and names no artefact.

    Under `measured-rate-travels-with-its-script` a verification claim with no
    committed script is a claim ABOUT evidence, not evidence. This supplies it.
    """
    print("6. D(n) -> C(n), the Part XIII reduction that claimed verification with no script")
    n = sp.symbols("n", positive=True, integer=True)
    i = sp.symbols("i", positive=True, integer=True)
    # The rho-decay form, PAPER.md:1048
    D_rho = 1 - sp.product(1 - p * (1 - rho) ** (i - 1), (i, 1, n))
    at_zero = sp.simplify(sp.powsimp(D_rho.subs(rho, 0)))
    Cn = 1 - (1 - p) ** n
    ok = _report(sp.simplify(at_zero - Cn) == 0,
                 "D(n) at rho = 0 equals C(n)", f"D(n)|rho=0 = {at_zero}")
    # Monoculture collapse, PAPER.md:1100: rho = 1 gives D(n) = D(1).
    # Substituting rho=1 directly leaves SymPy with p*0**(i-1) under a symbolic
    # product, which it cannot evaluate because the i=1 factor is 0**0. Split the
    # first factor out, which is what the limit does anyway.
    # SymPy will not reduce 0**(i-1) under a symbolic product, so prove it on the
    # general FACTOR instead: for every i >= 2 the factor is identically 1, hence
    # the tail product is 1 and D(n) = 1 - (1-p)*1 = p = D(1).
    j = sp.symbols("j", positive=True, integer=True)   # j = i-1 >= 1
    general_factor = (1 - p * (1 - rho) ** j).subs(rho, 1)
    ok &= _report(sp.simplify(general_factor - 1) == 0,
                  "every factor i >= 2 is identically 1 at rho = 1",
                  f"1 - p*(1-rho)^j at rho=1 = {sp.simplify(general_factor)}")
    concrete = all(sp.simplify((1 - (1 - p) * sp.prod(
        [1 - p * (1 - rho) ** (k - 1) for k in range(2, nn + 1)])).subs(rho, 1) - p) == 0
        for nn in range(1, 9))
    ok &= _report(concrete, "D(n) = p at rho = 1 for n = 1..8 (products expanded)",
                  "monoculture collapse holds symbolically at each n")
    # And numerically, as the limit from below, for several n.
    lim_ok = all(
        mp.almosteq(
            1 - mp.fprod([1 - mp.mpf("0.3") * (1 - mp.mpf("1") + mp.mpf("1e-30")) ** (j - 1)
                          for j in range(1, nn + 1)]),
            mp.mpf("0.3"), rel_eps=mp.mpf("1e-20"))
        for nn in (1, 2, 3, 5, 8))
    ok &= _report(lim_ok, "mpmath: D(n) -> 0.3 = D(1) as rho -> 1 for n in {1,2,3,5,8}",
                  "monoculture collapse holds numerically")
    return ok


def main() -> int:
    print("Reduction properties of G_n, executed rather than read")
    print("=" * 70)
    results = [check_residual(), check_rho_endpoints(),
               check_uniform_reduction(), check_r_k_is_not_nested(),
               check_which_models_nest(), check_distributed_compute_reduction()]
    print("=" * 70)
    if all(results):
        print("ALL CHECKS PASS -- PAPER.md:528 as corrected is discharged by execution.")
        return 0
    print("FAILURES ABOVE -- the corrected paragraph does not hold.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
