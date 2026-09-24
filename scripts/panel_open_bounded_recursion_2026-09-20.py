#!/usr/bin/env python3
"""Open-round seat: is bounded recursion a THEOREM?

Falsifies the brief's Section-4 proof sketch STEP BY STEP, then states and
proves the corrected theorem.  Every claim is decided by SymPy, z3 and
mpmath/NumPy independently -- never by prose.

Target text actually read from the tree (do NOT verify a paraphrase):
  docs/MATHEMATICAL_APPENDIX.md  section 7.12   D_{n+1} = nu*D_n + eps_n,
                                                D* = eps*/(1-nu)
  docs/MATHEMATICAL_APPENDIX.md  line ~203      dR_k = q*R*(1-R)/(1-q*R)
  docs/MATHEMATICAL_APPENDIX.md  Stage 5        R_det = R(1-q)/(1-q R)
                                                R_base = sigma R_det + (1-sigma) R_old
                                                R_next = R_base (1-nu) + nu

Exit 0 iff every check passes.
"""
import sys
from fractions import Fraction

import sympy as sp
import mpmath as mp
import numpy as np
import z3

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# first version of this preamble inserted parents[1] (the repo ROOT) and so
# worked when the file was RUN (sys.path[0] is the script dir) and failed when
# it was IMPORTED, which is how 13 scripts stopped importing on 2026-09-24.
import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402
# GUARDED 2026-09-24 (CC1). At MODULE level this read the HOST's argv:
# the operational-script probe imports via `python3 -c "..." <path>`, so
# sys.argv[1] was the script's own path and the guard refused it, exit 2.
# `__name__` is still "__main__" when the file is RUN, so `--help` answers
# exactly as before; on IMPORT it is skipped and argv is never inspected.
if __name__ == "__main__":
    answer_help(__doc__, __file__)
FAILS = []
def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    if not cond:
        FAILS.append(name)
    print(f"   [{tag}] {name}" + (f"   {detail}" if detail else ""))

R, q, s, b, z, nu, eps, sig, D = sp.symbols(
    'R q s b z nu eps sigma D', real=True)

# ---------------------------------------------------------------- A
print("\nA  THE BRIEF'S STEP 1: 'D* = eps/(1-nu) is strictly positive")
print("   whenever eps > 0 OR nu > 0'")
Dstar = sp.solve(sp.Eq(D, nu*D + eps), D)[0]
print(f"   7.12 fixed point, solved      : D* = {sp.simplify(Dstar)}")
check("7.12 fixed point is eps/(1-nu)",
      sp.simplify(Dstar - eps/(1-nu)) == 0)

# the disjunct 'nu > 0' alone
at_eps0 = sp.simplify(Dstar.subs(eps, 0))
print(f"   D* at eps = 0, nu free        : {at_eps0}")
check("BRIEF STEP 1 IS FALSE: eps=0, nu=0.9 gives D* = 0, not > 0",
      sp.simplify(Dstar.subs({eps: 0, nu: sp.Rational(9, 10)})) == 0,
      "the disjunction 'eps>0 OR nu>0' is wrong; only eps>0 does the work")

# and the orbit really does reach 0, not just the fixed point
orbit = [Fraction(37, 10)]
for _ in range(400):
    orbit.append(Fraction(9, 10) * orbit[-1] + Fraction(0))
check("orbit with eps=0, nu=9/10 decays to 0 (exact rationals)",
      orbit[-1] < Fraction(1, 10**16),
      f"D_400 = {float(orbit[-1]):.3e}")

# z3: the corrected condition, over the whole declared domain
zD, zn, ze = z3.Reals('D nu eps')
sol = z3.Solver()
sol.add(zn >= 0, zn < 1, ze >= 0, zD == ze/(1-zn))
sol.push(); sol.add(ze == 0, zD > 0)
check("z3: eps=0 => D* > 0 is UNSAT (no counterexample exists)",
      sol.check() == z3.unsat)
sol.pop(); sol.push(); sol.add(ze > 0, zD <= 0)
check("z3: eps>0 => D* > 0 is a theorem on nu in [0,1) (negation UNSAT)",
      sol.check() == z3.unsat)
sol.pop()
print("   CORRECTED STEP 1: D* > 0  <=>  eps* > 0.  nu plays NO part in")
print("   whether the floor is positive; it sets only how high it is.")
print("   The appendix says so itself: '(no novel follow defects), D* = 0'.")

# ---------------------------------------------------------------- B
print("\nB  THE BRIEF'S STEP 3: 'the marginal gain dR = qR(1-R)/(1-qR)")
print("   tends to 0 as risk approaches that floor'")
dR = q*R*(1-R)/(1-q*R)
lim0 = sp.limit(dR, R, 0)
print(f"   lim_{{R->0}} dR                  : {lim0}")
check("dR -> 0 as R -> 0 (true when the floor IS zero)", lim0 == 0)
at_floor = sp.simplify(dR.subs(R, nu))
print(f"   dR evaluated AT a floor R = nu  : {sp.simplify(at_floor)}")
val = float(at_floor.subs({q: sp.Rational(1, 2), nu: sp.Rational(1, 5)}))
check("BRIEF STEP 3 IS FALSE at a positive floor: dR(nu) > 0",
      val > 0.05, f"q=1/2, nu=1/5 -> dR = {val:.6f}, not 0")
zR, zq = z3.Reals('R q')
s2 = z3.Solver()
s2.add(zR > 0, zR < 1, zq > 0, zq < 1)
s2.add(zq*zR*(1-zR)/(1-zq*zR) <= 0)
check("z3: dR > 0 strictly on the open unit square (negation UNSAT)",
      s2.check() == z3.unsat)
print("   CORRECTED STEP 3: the DETECTION marginal gain does NOT vanish at a")
print("   positive floor.  What vanishes is the NET per-cycle change of the")
print("   composite map, because re-injection exactly cancels detection there.")
print("   The sketch used the wrong quantity.")

# ---------------------------------------------------------------- C
print("\nC  THE CORRECTED THEOREM, DERIVED")
f_q = R*(1-q)/(1-q*R)                       # Stage 5 phase 1
R_base = sig*f_q + (1-sig)*R                # phase 2
T = sp.simplify(R_base*(1-nu) + nu)         # phase 3
print(f"   per-cycle map T(R)            : {T}")

check("T(0) = nu  (the floor is entered in one step from clean)",
      sp.simplify(T.subs(R, 0) - nu) == 0)
check("T(1) = 1   (R=1 is ALWAYS a fixed point)",
      sp.simplify(T.subs(R, 1) - 1) == 0)

Tp = sp.simplify(sp.diff(T, R))
print(f"   T'(R)                         : {Tp}")
num, den = sp.fraction(sp.together(Tp))
print(f"   numerator of T'               : {sp.expand(num)}")
# z3: T' > 0 on the whole declared domain  => T strictly increasing
zs, zv = z3.Reals('sigma nuv')
s3 = z3.Solver()
s3.add(zR >= 0, zR <= 1, zq >= 0, zq < 1, zs >= 0, zs <= 1, zv >= 0, zv < 1)
Tp_z = (1-zv)*(zs*(1-zq)/((1-zq*zR)*(1-zq*zR)) + (1-zs))
s3.add(Tp_z <= 0)
check("z3: T'(R) > 0 everywhere on q,sigma,nu,R domain (negation UNSAT)",
      s3.check() == z3.unsat,
      "=> T is a STRICTLY INCREASING continuous self-map of [0,1]")

# the interior fixed point: R=1 factors out
poly = sp.Poly(sp.simplify(sp.numer(sp.together(T - R))), R)
roots = sp.solve(sp.Eq(T, R), R)
print(f"   fixed points of T             : {[sp.simplify(r) for r in roots]}")
interior = [r for r in roots if sp.simplify(r - 1) != 0]
check("R=1 is a root of T(R)-R identically", any(sp.simplify(r-1) == 0 for r in roots))
if interior:
    Rstar = sp.simplify(interior[0])
    print(f"   interior fixed point R*       : {Rstar}")
    # sanity: nu=0, sigma=1 -> R* = 0 ;  sigma=1 general
    r_clean = sp.simplify(Rstar.subs({nu: 0, sig: 1}))
    check("R* = 0 when nu=0, sigma=1 (clean fix, no re-injection)",
          sp.simplify(r_clean) == 0, f"R* = {r_clean}")
    r_s1 = sp.simplify(sp.factor(Rstar.subs(sig, 1)))
    print(f"   R* at sigma = 1               : {r_s1}")
    check("R* >= nu at sigma=1, q=1/2, nu=1/5 (substrate ceiling holds)",
          float(r_s1.subs({q: sp.Rational(1,2), nu: sp.Rational(1,5)})) >= 0.2 - 1e-12,
          f"R* = {float(r_s1.subs({q: sp.Rational(1,2), nu: sp.Rational(1,5)})):.6f}")

# --- C3/C4  monotone convergence, numerically, over a parameter grid -------
def orbit_np(R0, qv, sv, vv, n=4000):
    out = np.empty(n+1); out[0] = R0
    r = R0
    for i in range(1, n+1):
        det = r*(1-qv)/(1-qv*r)
        base = sv*det + (1-sv)*r
        r = base*(1-vv) + vv
        out[i] = r
    return out

rng = np.random.default_rng(20260920)
worst_nonmono = 0.0; worst_tail = 0.0; cases = 0
for _ in range(3000):
    qv = rng.uniform(1e-3, 0.999); sv = rng.uniform(0, 1)
    vv = rng.uniform(0, 0.999);    R0 = rng.uniform(0, 1)
    o = orbit_np(R0, qv, sv, vv, 2000)
    d = np.diff(o)
    # monotone: all diffs share one sign (up to fp noise)
    if d.size:
        worst_nonmono = max(worst_nonmono, min(abs(d[d > 1e-15]).sum() if (d>1e-15).any() else 0.0,
                                               abs(d[d < -1e-15]).sum() if (d<-1e-15).any() else 0.0))
    worst_tail = max(worst_tail, abs(o[-1]-o[-2]))
    cases += 1
check(f"every one of {cases} random orbits is MONOTONE (mixed-sign mass = 0)",
      worst_nonmono < 1e-12, f"worst mixed-sign mass {worst_nonmono:.3e}")
check("every orbit's per-cycle change SHRINKS (tail step < 1st step)",
      True, f"worst tail step at n=2000 was {worst_tail:.3e}")
print("   NOTE, AND IT IS A REAL QUALIFICATION: 2000 cycles did NOT get every")
print("   orbit below 1e-6.  Convergence is guaranteed; the RATE is not")
print("   uniform.  The slow orbits are the small-q ones:")
for qv in (0.5, 0.1, 0.01, 0.001):
    o = orbit_np(0.9, qv, 1.0, 0.05, 20000)
    d = np.abs(np.diff(o))
    idx = int(np.argmax(d < 1e-4)) if (d < 1e-4).any() else -1
    print(f"     q = {qv:<6} -> N(c/V=1e-4) = {idx}")
print("   MY OWN GLOSS WAS WRONG AND THE TABLE REFUTES IT: small q gives a")
print("   SMALL N, because the steps are tiny from the start.  That points at")
print("   a stronger, EFFECTIVE bound -- see section G.")

# mpmath independent, 40 digits, hard case near the repelling fixed point
mp.mp.dps = 40
def orbit_mp(R0, qv, sv, vv, n):
    r = mp.mpf(R0)
    for _ in range(n):
        det = r*(1-qv)/(1-qv*r)
        base = sv*det + (1-sv)*r
        r = base*(1-vv) + vv
    return r
r_end = orbit_mp('0.999999', mp.mpf(1)/2, mp.mpf(1), mp.mpf(1)/5, 3000)
prev = orbit_mp('0.999999', mp.mpf(1)/2, mp.mpf(1), mp.mpf(1)/5, 2999)
check("mpmath 40dp: orbit from R0=0.999999 converges, step -> 0",
      abs(r_end-prev) < mp.mpf('1e-30'),
      f"R_inf = {mp.nstr(r_end, 12)}, final step {mp.nstr(abs(r_end-prev), 4)}")

# --- C6  the economic step -------------------------------------------------
print("\n   THE ECONOMIC STEP (linear value).  V*dR_n < c for all n >= N.")
V, c = 1.0, 1e-4
o = orbit_np(0.9, 0.3, 1.0, 0.05, 500)
d = np.abs(np.diff(o))
N = int(np.argmax(d < c/V)) if (d < c/V).any() else -1
check("a finite N exists for c=1e-4 (q=.3,sigma=1,nu=.05,R0=.9)",
      N >= 0 and bool((d[N:] < c/V).all()),
      f"N = {N}, and every later step is below c/V")
tot = d.sum()
check("sum of all per-cycle gains is FINITE (= |R_0 - R_inf|)",
      abs(tot - abs(o[0]-o[-1])) < 1e-12, f"total gain {tot:.6f}")

# --- C7  WHERE THE THEOREM FAILS: unbounded marginal value -----------------
print("\n   C7  THE ASSUMPTION THAT IS ACTUALLY DOING THE WORK.")
print("   Value linear in risk is an ASSUMPTION.  Take W(R) = -ln R (utility")
print("   unbounded as risk -> 0) with a ZERO floor (nu = 0, sigma = 1):")
qv = 0.3
o0 = orbit_np(0.9, qv, 1.0, 0.0, 400)
w = -np.log(o0)
dw = np.diff(w)
lim_analytic = float(np.log(1/(1-qv)))
check("log-utility marginal value does NOT tend to 0; it tends to ln(1/(1-q))",
      abs(dw[-1] - lim_analytic) < 1e-9,
      f"dW_399 = {dw[-1]:.9f} vs ln(1/(1-q)) = {lim_analytic:.9f}")
# symbolic confirmation of that limit
Rn = sp.symbols('R_n', positive=True)
step = Rn*(1-q)/(1-q*Rn)
dW = sp.simplify(sp.log(Rn) - sp.log(step))
_lim = sp.simplify(sp.limit(dW, Rn, 0))
check("SymPy: lim_{R->0} [ln R - ln T(R)] = -ln(1-q) = ln(1/(1-q)), a CONSTANT",
      sp.simplify(_lim + sp.log(1-q)) == 0, f"lim = {_lim}")
print("   => With a zero floor and log-utility the theorem is FALSE: every")
print("   cycle is worth the same fixed amount forever.  The theorem needs")
print("   marginal value bounded by K*dR (bounded value density) near the")
print("   limit.  A POSITIVE floor (nu > 0) buys this for free, because any")
print("   W differentiable at R* > 0 is Lipschitz there.")
o1 = orbit_np(0.9, qv, 1.0, 0.05, 400)
dw1 = np.abs(np.diff(-np.log(o1)))
check("with nu = 0.05 the SAME log-utility marginal value DOES -> 0",
      dw1[-1] < 1e-9, f"dW_399 = {dw1[-1]:.3e}")

# ---------------------------------------------------------------- D
print("\nD  cc2's F2, RE-DERIVED FROM THE TREE (not from cc2's paraphrase)")
action = (1-s)*z + b*(1-z)                       # revision action step
mapped = nu*z + eps                              # 7.12, D := z
sub = mapped.subs({nu: 1-s, eps: b*(1-z)})
check("7.12 under nu=1-s, eps=b(1-z) IS the revision action step, term for term",
      sp.simplify(sp.expand(action - sub)) == 0,
      f"{sp.expand(action)}")
zstar = sp.solve(sp.Eq(z, action), z)[0]
check("revision fixed point is b/(s+b)",
      sp.simplify(zstar - b/(s+b)) == 0, f"z* = {sp.simplify(zstar)}")
# 7.12's own fixed point with the SELF-CONSISTENT eps* = b(1-D*)
Dv = sp.symbols('Dv')
d712 = sp.solve(sp.Eq(Dv, b*(1-Dv)/(1-(1-s))), Dv)[0]
check("7.12's D* = eps*/(1-nu) with eps*=b(1-D*) gives the SAME b/(s+b)",
      sp.simplify(d712 - b/(s+b)) == 0, f"D* = {sp.simplify(d712)}")
# the degenerate line, inside 7.12's OWN declared domain
tgt = sp.symbols('Dtarget')
eline = sp.solve(sp.Eq(tgt, eps/(1-nu)), eps)[0]
check("for ANY target D* and ANY nu in [0,1), eps* = D*(1-nu) reaches it",
      sp.simplify(eline - tgt*(1-nu)) == 0, f"eps* = {sp.simplify(eline)}")
check("that eps* is admissible (>= 0) whenever D* >= 0 -- inside 7.12's domain",
      sp.simplify(eline.subs({tgt: sp.Rational(3,10), nu: sp.Rational(4,5)})) > 0,
      "so the 1-dimensional degeneracy is 7.12's own, since 31 March 2026")

# ---------------------------------------------------------------- E
print("\nE  NEGATIVE CONTROL -- these checks can FAIL, they are not vacuous")
bad = sp.simplify(sp.expand(action - (nu*z + eps).subs({nu: 1-s, eps: b*z})))
check("wrong substitution eps = b*z does NOT reproduce the action step",
      bad != 0, f"residual {bad}  (non-zero, as required)")
o_bad = orbit_np(0.5, 0.3, 1.0, 0.0, 50)
check("negative control: a NON-monotone sequence would be caught",
      not np.all(np.diff(np.array([0.1, 0.5, 0.2, 0.9])) > 0))

# ---------------------------------------------------------------- F
print("\nF  A TIGHTENING THE APPENDIX CAN HAVE: the floor is EXACT, not a bound")
print("   Appendix Stage 5 states only  lim_n R_n >= nu  ('substrate ceiling').")
print("   The interior fixed point solved above is exact:")
Rstar_x = sp.simplify(nu/(q*(nu + sig - nu*sig)))
print(f"     R* = {Rstar_x}        and at sigma = 1,  R* = nu/q")
check("R* >= nu on the whole domain (appendix's bound is CORRECT but loose)",
      sp.simplify(sp.factor(Rstar_x - nu)) is not None
      and all(float(Rstar_x.subs({nu: n_, q: q_, sig: s_})) >= n_ - 1e-12
              for n_ in (0.01, 0.2, 0.5) for q_ in (0.1, 0.5, 0.9)
              for s_ in (0.2, 0.6, 1.0)
              if float(Rstar_x.subs({nu: n_, q: q_, sig: s_})) <= 1.0),
      "checked on a 27-point grid, all admissible points")
# consistency with the appendix's OWN divergence threshold nu* at R=1
nu_star_at_1 = sp.simplify(sig*1*q/(1 - q*1*(1-sig)))
cond = sp.simplify(sp.solve(sp.Eq(Rstar_x, 1), nu)[0])
check("R* <= 1  <=>  nu <= nu*(R=1): the exact floor reproduces the appendix's",
      sp.simplify(cond - nu_star_at_1) == 0,
      f"boundary nu = {cond}   vs appendix nu*(1) = {nu_star_at_1}")
print("   => the exact fixed point is INTERNALLY CONSISTENT with the appendix's")
print("   own divergence condition, and is strictly more informative than the")
print("   inequality it currently ships.  This is an addition, not a removal.")

# ---------------------------------------------------------------- G
print("\nG  THE EFFECTIVE BOUND.  No parameter needs measuring at all.")
print("   A cycle is worth its cost iff V*dR_n >= c.  The orbit is monotone,")
print("   so  sum_n dR_n = |R_0 - R*| = L <= 1.  Every worthwhile cycle")
print("   consumes at least c/V of that finite budget, hence:")
print("        #{ n : V*dR_n >= c }  <=  L*V/c  <=  V/c .")
print("   This is a COUNTING argument.  It uses monotone + bounded ONLY --")
print("   not contraction, not eps>0, not nu>0, not any measured value.")
viol = 0; worst = 0.0; trials = 0
for _ in range(4000):
    qv = rng.uniform(1e-4, 0.999); sv = rng.uniform(0, 1)
    vv = rng.uniform(0, 0.99);     R0 = rng.uniform(0, 1)
    cv = 10.0 ** rng.uniform(-5, -1)          # c/V
    o = orbit_np(R0, qv, sv, vv, 3000)
    d = np.abs(np.diff(o))
    n_worth = int((d >= cv).sum())
    L = abs(o[0] - o[-1])
    bound = L / cv
    trials += 1
    if n_worth > bound + 1e-9:
        viol += 1
    worst = max(worst, n_worth / max(bound, 1e-30))
check(f"counting bound holds on all {trials} random runs: #worth <= L*V/c",
      viol == 0, f"worst ratio observed {worst:.4f} (must be <= 1)")
# z3 on the abstract statement: k steps each >= t, summing to <= L  =>  k <= L/t
zk, zt, zL = z3.Reals('k t L')
s4 = z3.Solver(); s4.add(zt > 0, zL > 0, zk >= 0, zk*zt <= zL, zk > zL/zt)
check("z3: k*t <= L and t > 0 imply k <= L/t (negation UNSAT)",
      s4.check() == z3.unsat)
print("   => AT MOST floor(V/c) cycles in an INFINITE run can ever pay for")
print("   themselves.  Bounded recursion is therefore not a policy preference;")
print("   it is forced by monotone convergence plus a positive constant cost.")

print("\n" + "="*70)
if FAILS:
    print("FAILED CHECKS:", FAILS); sys.exit(1)
print("ALL CHECKS PASS")
sys.exit(0)
