"""F1. Does Phase 2's revert-to-prior at sigma=0 follow from probability, or is it a modelling error?

The brief's own script ends: "whether reverting to the prior at sigma = 0 is
CORRECT ... no amount of algebra decides it." That is true of algebra COMPARING
THE TWO MAPS. It is not true of a derivation FROM THE GENERATIVE MODEL, which is
what this file does.

Generative model already committed to by the appendix (it is what makes
R_det = R_old(1-q)/(1-q*R_old) the posterior P(flaw | no detection)):
    F  = "flaw of class k present",  P(F) = R_old
    D  = "the pass detects it",      P(D|F) = q,  P(D|not F) = 0   (no false positives)
Sanity: P(not D) = R_old(1-q) + (1-R_old) = 1 - q*R_old.

A CYCLE HAS TWO BRANCHES, and the appendix names only one of them.
  Branch A (no detection), prob 1 - q*R_old : posterior = R_det. NO FIX IS
      ATTEMPTED -- nothing was found. Risk after = R_det.
  Branch B (detection),    prob q*R_old     : posterior = 1 (no false positives).
      A fix is attempted and resolves with probability sigma. Risk after = 1-sigma.

Expected risk after the resolution step is the total-probability mixture.
FALSIFIED if the mixture does not equal R_old at sigma = 0.
"""
import sympy as sp

# WIRED 2026-09-24 (CC1). Module-level work, so no main() to intercept `--help`.
import sys as _s, pathlib as _p
_s.path.insert(0, str(_p.Path(__file__).resolve().parents[1]))
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

R, q, s, nu, z = sp.symbols('R_old q sigma nu z', nonnegative=True)

R_det   = R*(1-q)/(1-q*R)
p_nodet = 1 - q*R
p_det   = q*R

# --- the derivation -------------------------------------------------------
marginal = sp.simplify(p_nodet*R_det + p_det*(1-s))
print("1. TOTAL-PROBABILITY MIXTURE OVER BOTH BRANCHES")
print("   E[risk after resolution] =", sp.factor(marginal))
assert sp.simplify(marginal - R*(1-q*s)) == 0, "mixture is not R_old(1-q*sigma)"
print("   proved equal to           R_old*(1 - q*sigma)   [SymPy residual 0]")

print("\n2. THE sigma = 0 ENDPOINT -- THE QUESTION UNDER REVIEW")
m0 = sp.simplify(marginal.subs(s, 0))
print("   mixture at sigma=0        =", m0)
assert sp.simplify(m0 - R) == 0
print("   -> EXACTLY R_old. The appendix's revert-to-prior is DERIVED, not assumed.")

print("\n3. CONSERVATION OF EXPECTED EVIDENCE (tower property) -- independent route")
#   E[P(F | observation)] = P(F).  Check the two-branch posteriors average to R_old.
tower = sp.simplify(p_nodet*R_det + p_det*1)
print("   E[posterior over both branches] =", sp.simplify(tower))
assert sp.simplify(tower - R) == 0
print("   -> = R_old. An observation with NO action cannot move expected risk.")
print("      Any rule that returns something < R_old at sigma=0 manufactures")
print("      a free decrease from an observation nobody acted on.")

print("\n4. WHAT CC1's REVISION DOES AT sigma = 0")
#   revision: R_new = (1-s_r)*z + b*(1-z), s_r = sigma(1-nu), b = nu, z = R_det
rev = (1-s*(1-nu))*z + nu*(1-z)
rev0 = sp.simplify(rev.subs([(s, 0), (nu, 0)]).subs(z, R_det))
print("   revision at sigma=0, nu=0 =", sp.simplify(rev0))
print("   appendix at sigma=0, nu=0 =", R)
gap = sp.simplify(R - rev0)
print("   deficit vs conservation   =", sp.factor(gap))
assert sp.simplify(gap - q*R*(1-R)/(1-q*R)) == 0
print("   -> q*R_old*(1-R_old)/(1-q*R_old) > 0 for all q,R_old in (0,1):")
print("      the revision STRICTLY violates conservation of expected evidence.")

print("\n5. WHAT CC1's REVISION DOES AT sigma = 1, nu = 0  (the other endpoint)")
rev1 = sp.simplify(rev.subs([(s, 1), (nu, 0)]))
print("   revision at sigma=1, nu=0 =", rev1)
assert rev1 == 0
print("   -> IDENTICALLY 0, for every z, every q, every R_old.")
print("      One successful fix asserts ZERO residual risk. That contradicts")
print("      the appendix's own substrate ceiling (lim R >= nu_k, and")
print("      lim R = pi_risk,k when capability is absent).")

print("\n6. WHERE THE APPENDIX IS *NOT* EXACT: the sigma = 1 endpoint")
appendix_base = s*R_det + (1-s)*R
err = sp.factor(sp.simplify(appendix_base - marginal))
print("   appendix R_base - exact marginal =", err)
assert sp.simplify(err - s*q*R**2*(1-q)/(1-q*R)) == 0
print("   = sigma*q*R_old^2*(1-q)/(1-q*R_old)  >= 0  everywhere on the cube.")
print("   -> the appendix NEVER understates risk. It is a conservative")
print("      (risk-overstating) approximation, tight at sigma=0, loosest at sigma=1.")
print("\nALL ASSERTIONS PASSED.")
