#!/usr/bin/env python3
"""OPEN-ROUND seat check: is bounded recursion a theorem under 7.12?

Verifies with SymPy (symbolic) and mpmath (40-digit numeric) each step of the
brief's Section 4 sketch, including 2 steps this seat believes are wrong as
written:
  (S1) "D* strictly positive whenever eps > 0 OR nu > 0" -- FALSE for
       eps = 0, nu > 0 (then D* = 0, per 7.12's own text).
  (S3) "the appendix's marginal gain dR = qR(1-R)/(1-qR) tends to 0 as risk
       approaches that floor" -- FALSE at a positive floor: the collapse-model
       dR tends to qD*(1-D*)/(1-qD*) > 0 there. What DOES tend to 0 is the net
       per-cycle decrease under 7.12's own recursion:
       g_n = D_n - D_{n+1} = (1-nu)(D_n - D*).
Then verifies the corrected theorem (finite optimal stopping).
Exit 0 iff every check passes.
"""
import sympy as sp
import mpmath as mp

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

fails = []
def check(name, ok):
    print(f"   [{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        fails.append(name)

nu, eps, D0, n, q, c, kappa = sp.symbols('nu epsilon D_0 n q c kappa', positive=True)
R = sp.Symbol('R')

Dstar = eps / (1 - nu)
Dn    = Dstar + nu**n * (D0 - Dstar)
Dn1   = Dstar + nu**(n + 1) * (D0 - Dstar)

print("A. closed form of D_{n+1} = nu*D_n + eps")
check("D_n = D* + nu^n (D0 - D*) satisfies the recursion exactly",
      sp.simplify((nu * Dn + eps) - Dn1) == 0)
check("D_n -> D* for nu = 1/3",
      sp.simplify(sp.limit(Dn.subs(nu, sp.Rational(1,3)), n, sp.oo)
                  - Dstar.subs(nu, sp.Rational(1,3))) == 0)

print("B. sketch step S1: 'D* > 0 whenever eps > 0 OR nu > 0'")
check("eps > 0, nu in [0,1) => D* > 0  (true half)",
      Dstar.subs([(eps, sp.Rational(1,10)), (nu, sp.Rational(1,2))]) > 0)
check("eps = 0, nu = 9/10 => D_n -> 0: 'or nu > 0' clause is FALSE",
      sp.limit((nu**n * D0).subs([(nu, sp.Rational(9,10)), (D0, 1)]), n, sp.oo) == 0)

print("C. sketch step S3: collapse-model dR at a positive floor")
dR = q * R * (1 - R) / (1 - q * R)
val = dR.subs([(R, sp.Rational(1,4)), (q, sp.Rational(1,2))])
check("dR at R = 1/4, q = 1/2 equals 3/28 > 0 (does NOT tend to 0 at a positive floor)",
      sp.simplify(val - sp.Rational(3,28)) == 0 and val > 0)
g_n = sp.simplify(Dn - (nu * Dn + eps))
check("net gain under 7.12 itself: g_n = (1-nu)(D_n - D*)",
      sp.simplify(g_n - (1 - nu) * (Dn - Dstar)) == 0)
check("g_n = nu^n (1-nu)(D0 - D*), geometric in n",
      sp.simplify(g_n - nu**n * (1 - nu) * (D0 - Dstar)) == 0)
check("g_n -> 0 for nu = 1/3, eps = 1/10, D0 = 1",
      sp.limit(g_n.subs([(nu, sp.Rational(1,3)), (eps, sp.Rational(1,10)), (D0, 1)]),
               n, sp.oo) == 0)

print("D. corrected theorem: finite n* for every c > 0")
nstar = sp.log(c / (kappa * (1 - nu) * (D0 - Dstar))) / sp.log(nu)
subs = [(nu, sp.Rational(1,2)), (eps, sp.Rational(1,20)), (D0, sp.Rational(9,10)),
        (kappa, 1), (c, sp.Rational(1,100))]
nv = sp.N(nstar.subs(subs))
check(f"n* = {nv} is finite and real at nu=1/2, eps=1/20, D0=9/10, c=1/100",
      nv.is_real and nv < sp.oo)
n_int = int(sp.ceiling(nv))
g = lambda k: (nu**k * (1 - nu) * (D0 - Dstar)).subs(subs)
check(f"V_n < c at n = {n_int+1}; V_n >= c at n = {n_int-1} (n* is tight)",
      g(n_int + 1) < sp.Rational(1,100) and g(n_int - 1) >= sp.Rational(1,100))

D_div = mp.mpf(1)
for _ in range(50):
    D_div = mp.mpf('1.1') * D_div + mp.mpf('0.05')
check("nu = 1.1 diverges (D_50 > 100): domain nu in [0,1) is necessary",
      D_div > 100)

print("E. mpmath 40-digit cross-check")
mp.mp.dps = 40
nu_m, eps_m, D0_m = mp.mpf(1)/3, mp.mpf(1)/10, mp.mpf('0.8')
Ds = eps_m / (1 - nu_m)
D = D0_m; worst = mp.mpf(0)
for k in range(80):
    worst = max(worst, abs(D - (Ds + nu_m**k * (D0_m - Ds))))
    D = nu_m * D + eps_m
check(f"worst |iterated - closed| over 80 steps = {mp.nstr(worst, 3)} < 1e-35",
      worst < mp.mpf('1e-35'))
g79 = nu_m**79 * (1 - nu_m) * (D0_m - Ds)
check(f"g_79 = {mp.nstr(g79, 3)} < 1e-30: gains collapse below any real cost",
      g79 < mp.mpf('1e-30'))

print()
if fails:
    print(f"FAILED: {fails}"); raise SystemExit(1)
print("ALL CHECKS PASS (13 checks)")
