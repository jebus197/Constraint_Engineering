"""F3. Derive Section 5's bounded-recursion theorem from scratch. Do not accept the statement."""
import sympy as sp

# WIRED 2026-09-24 (CC1). Module-level work, so no main() to intercept `--help`.
import sys as _s, pathlib as _p
_s.path.insert(0, str(_p.Path(__file__).resolve().parents[1]))
from _cli_help import answer_help  # noqa: E402
# GUARDED 2026-09-24 (CC1). At MODULE level this read the HOST's argv:
# the operational-script probe imports via `python3 -c "..." <path>`, so
# sys.argv[1] was the script's own path and the guard refused it, exit 2.
# `__name__` is still "__main__" when the file is RUN, so `--help` answers
# exactly as before; on IMPORT it is skipped and argv is never inspected.
if __name__ == "__main__":
    answer_help(__doc__, __file__)
R, q, s, nu = sp.symbols('R q sigma nu', positive=True)

f = ((s*(R*(1-q)/(1-q*R)) + (1-s)*R))*(1-nu) + nu      # full appendix cycle

print("A. STRICTLY INCREASING CONTINUOUS SELF-MAP OF [0,1]")
d = sp.simplify(sp.diff(f, R))
print("   f'(R) =", sp.factor(d))
d_at = sp.factor(sp.simplify(d - (1-nu)*(s*(1-q)/(1-q*R)**2 + (1-s))))
assert d_at == 0
print("   = (1-nu)*[ sigma*(1-q)/(1-q*R)^2 + (1-sigma) ]  -> every factor > 0")
print("     for q<1, nu<1, sigma in [0,1]. STRICTLY INCREASING: HOLDS.")
print("   f(0) =", sp.simplify(f.subs(R,0)), " f(1) =", sp.simplify(f.subs(R,1)))
print("   f(0)=nu>=0 and f(1)=1 -> maps [0,1] into [nu,1] subset [0,1]. SELF-MAP: HOLDS.")
print("   => orbit x_{n+1}=f(x_n) is MONOTONE (order-preserving map) and BOUNDED,")
print("      hence convergent by monotone convergence. NO CONTRACTION NEEDED: HOLDS.")

print("\nB. TELESCOPING BOUND ON CYCLES WORTH RUNNING")
print("   sum_n (R_n - R_{n+1}) = R_0 - lim R_n  <=  1 - 0 = 1.")
print("   So #{cycles with gain > theta} < 1/theta. HOLDS (trivially, but it is true).")

print("\nC. THE PREMISE-INVERSION: log-odds gain with nu=0, sigma=1")
O  = R/(1-R)
Rn = (R*(1-q)/(1-q*R))
On = sp.simplify(Rn/(1-Rn))
print("   odds after one cycle =", sp.factor(On), " = O*(1-q) exactly:",
      sp.simplify(On - O*(1-q)) == 0)
assert sp.simplify(On - O*(1-q)) == 0
print("   -> log-odds DECREASES BY THE CONSTANT log(1/(1-q)) EVERY cycle, forever.")
print("      Under log utility each cycle is worth the SAME fixed amount and the")
print("      economic stopping rule NEVER fires. Convergence (R_n -> 0) happens")
print("      anyway. So nu>0 is NOT needed for convergence; it is what makes the")
print("      ECONOMIC step terminate. SECTION 5's INVERSION CLAIM: HOLDS.")

print("\nD. CRITICAL RE-INJECTION RATE (sigma = 1)")
fp = sp.solve(sp.Eq(f.subs(s,1), R), R)
print("   fixed points of f at sigma=1:", [sp.simplify(x) for x in fp])
print("   -> R = 1 and R = nu/q.")
print("   nu/q lies in (0,1) iff nu < q; if nu > q it exceeds 1 and leaves the")
print("      interval, so R=1 (CERTAIN FAILURE) is the ONLY fixed point in [0,1].")
slope1 = sp.simplify(sp.diff(f.subs(s,1), R).subs(R,1))
print("   f'(1) =", sp.simplify(slope1), "-> <1 (attracting) iff nu > q.")
assert sp.simplify(slope1 - (1-nu)/(1-q)) == 0
print("   CRITICAL RATE IS nu* = q. SECTION 5's SECOND CONDITION: HOLDS.")

print("\nE. A SHARPENING THE APPENDIX DOES NOT STATE")
print("   Appendix says lim R >= nu_k. The EXACT attracting limit at sigma=1 is")
print("   nu/q, and nu/q >= nu since q<=1. The stated floor is LOOSE by 1/q.")
print("   At q=0.2, nu=0.05 the true floor is 0.25, five times the stated 0.05.")
