"""Falsify the five results of PANEL_BRIEF_2026-09-20 Section 3.
Tools: SymPy (exact symbolic) + mpmath (independent high-precision) + Fraction
(the package's own exact arithmetic).  Two independent tools per claim.
Run: python3 scripts/cc_falsify_section3_2026-09-20.py
"""
import sys, itertools
from fractions import Fraction as F
import sympy as sp
import mpmath as mp
sys.path.insert(0, "docs/maths_revision_review_2026-09-10/outputs")
from CDSFL_revised_core import update, action_gain   # the package's own arithmetic

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

mp.mp.dps = 50
R, p, s, b, z, d, L = sp.symbols("R p s b z d L", positive=True)
out = {}
def rep(k, ok, note=""):
    out[k] = ok
    print(("PASS " if ok else "FAIL ") + k + ("  " + note if note else ""))

# ---------------------------------------------------------------- 3.1
# CC1: b = (z - s*z - d)/(z-1) solves (1-s)z + b(1-z) = d.
step = (1 - s) * z + b * (1 - z)
b_sol = sp.solve(sp.Eq(step, d), b)[0]
cc1_b = (z - s * z - d) / (z - 1)
rep("3.1 algebra: CC1 b-formula == SymPy solve", sp.simplify(b_sol - cc1_b) == 0)

# CC1's three worked points, exact.
pts = {F(1,10): F(11,30), F(7,10): F(17,30), F(9,10): F(19,30)}
ok = all(sp.nsimplify(cc1_b.subs({z: sp.Rational(1,4), d: sp.Rational(1,2), s: sp.Rational(si)}))
         == sp.Rational(bi) for si, bi in pts.items())
rep("3.1 CC1's three worked (s,b) points reproduce exactly", ok)

# FALSIFICATION ATTEMPT: is the degeneracy ALWAYS a line?
# Admissible s-set for target d at posterior z:  s in [0,1] with b(s) in [0,1].
def admissible_s_measure(zv, dv):
    """Lebesgue measure of {s in [0,1] : b(s)=(d-(1-s)z)/(1-z) in [0,1]}."""
    zv, dv = mp.mpf(zv), mp.mpf(dv)
    if zv == 1: return None
    # b(s) = (d - (1-s)z)/(1-z) is increasing in s. b(0)=(d-z)/(1-z), b(1)=d/(1-z)
    lo_s, hi_s = mp.mpf(0), mp.mpf(1)
    # b>=0  =>  d-(1-s)z >= 0 => s >= 1 - d/z   (if z>0)
    if zv > 0: lo_s = max(lo_s, 1 - dv / zv)
    # b<=1  =>  d-(1-s)z <= 1-z => s <= (1 - z + d - z... ) solve:
    if zv > 0: hi_s = min(hi_s, (1 - zv + dv - zv) / zv + 1 - 1 + 0) if False else hi_s
    # solve d - (1-s)z <= 1-z  ->  -(1-s)z <= 1-z-d -> (1-s)z >= z+d-1 -> s <= 1-(z+d-1)/z
    if zv > 0: hi_s = min(hi_s, 1 - (zv + dv - 1) / zv)
    return max(mp.mpf(0), hi_s - lo_s)

m_mid = admissible_s_measure(0.25, 0.5)
m_d1  = admissible_s_measure(0.25, 1.0)
m_d0  = admissible_s_measure(0.25, 0.0)
print(f"   admissible-s measure: d=0.5 -> {float(m_mid):.6f} | d=1.0 -> {float(m_d1):.6f} | d=0.0 -> {float(m_d0):.6f}")
# Brute-force independent confirmation by direct search over a grid (NumPy-free, exact-ish).
def brute(zv, dv, n=20001):
    hits = 0
    for i in range(n):
        sv = i / (n - 1)
        bv = (dv - (1 - sv) * zv) / (1 - zv)
        if -1e-12 <= bv <= 1 + 1e-12: hits += 1
    return hits / n
rep("3.1 degeneracy is a LINE at an interior target (d=0.5)",
    m_mid > 0.99 and abs(brute(0.25, 0.5) - float(m_mid)) < 1e-3,
    f"brute={brute(0.25,0.5):.5f}")
rep("3.1 COUNTEREXAMPLE: at d=1 the solution set collapses to a POINT",
    float(m_d1) < 1e-12 and brute(0.25, 1.0) < 1.1e-4,
    f"measure={float(m_d1):.2e} brute={brute(0.25,1.0):.6f}")
rep("3.1 COUNTEREXAMPLE: at d=0 the solution set collapses to a POINT",
    float(m_d0) < 1e-12, f"measure={float(m_d0):.2e}")

# ---------------------------------------------------------------- 3.2
# Existing collapse form R(1-p)/(1-pR) over p in [0,1] reaches exactly [0,R].
coll = R * (1 - p) / (1 - p * R)
dcoll = sp.simplify(sp.diff(coll, p))
rep("3.2 collapse form is monotone NON-INCREASING in p (dR/dp = R(R-1)/(1-pR)^2 <= 0)",
    sp.simplify(dcoll - R * (R - 1) / (1 - p * R) ** 2) == 0)
rep("3.2 endpoints: p=0 -> R, p=1 -> 0 (so range = [0,R]) for R<1",
    sp.simplify(coll.subs(p, 0) - R) == 0 and sp.simplify(coll.subs(p, 1)) == 0)
# EDGE CASE the brief does not state: at R=1 the form is 1 for all p<1 and 0/0 at p=1.
r1 = sp.simplify(coll.subs(R, 1))
rep("3.2 EDGE: at R=1 the collapse form is identically 1 (range is {1}, not [0,1])",
    sp.simplify(r1 - 1) == 0, f"expr={r1}")

# Revised action step over (s,b) in [0,1]^2 reaches [0,1].
lo = min(float(((1 - sv) * 0.25 + bv * 0.75)) for sv in (0, 1) for bv in (0, 1))
hi = max(float(((1 - sv) * 0.25 + bv * 0.75)) for sv in (0, 1) for bv in (0, 1))
rep("3.2 revised step over (s,b) reaches [0,1] at z=0.25", lo == 0.0 and hi == 1.0)
# b=0 constraint -> [0,z]
lo2 = min(float((1 - sv) * 0.25) for sv in (0, 1)); hi2 = max(float((1 - sv) * 0.25) for sv in (0, 1))
rep("3.2 with b=0 the revised step reaches [0,z] only", lo2 == 0.0 and hi2 == 0.25)

# NEW RESULT (CC-derived, strengthens 3.2): with b=0 but p ALSO free, the revised
# model reaches EXACTLY the existing model's set [0,R].  So s adds NO reachability
# over the existing model's own free parameter; the entire expansion is b's.
zp = R * (1 - p) / (1 - p * R)            # posterior under clean-review likelihoods
reach = sp.simplify((1 - s) * zp)
rep("3.2+ s is REACHABILITY-REDUNDANT: sup_{s,p}(1-s)z(p) = R, inf = 0 (= existing set)",
    sp.simplify(reach.subs({s: 0, p: 0}) - R) == 0 and sp.simplify(reach.subs({s: 1})) == 0)

# ---------------------------------------------------------------- 3.3 containment
mism = 0
for i in range(1, 21):
    Rv, pv = F(i, 23), F((7 * i) % 19 + 1, 20)
    got = update(Rv, 1 - pv, 1, 0, 0).risk_after_action
    want = Rv * (1 - pv) / (1 - pv * Rv)
    if got != want: mism += 1
rep("3.3 update() reproduces R(1-p)/(1-pR) exactly, 20 rational steps", mism == 0, f"mismatches={mism}")
mp_max = max(abs(mp.mpf(str(float(update(F(i,101), 1-F(j,97), 1,0,0).risk_after_action)))
                 - (mp.mpf(i)/101*(1-mp.mpf(j)/97))/(1-(mp.mpf(j)/97)*(mp.mpf(i)/101)))
             for i in range(1,21) for j in range(1,21))
rep("3.3 mpmath independent agreement", mp_max < mp.mpf("1e-15"), f"max|diff|={mp.nstr(mp_max,3)}")

# ---------------------------------------------------------------- 3.4  THE KEY ONE
# CC1 states the flat-curve residual is R* = b/p.  Derive the fixed point of the
# REVISED MODEL'S OWN recursion and compare.
Rn_revised = (1 - p) * R + b * (1 - R)          # revised: introduction acts on the CLEAN fraction
fp_revised = sp.solve(sp.Eq(Rn_revised, R), R)[0]
Rn_cc1 = (1 - p) * R + b                        # unconditional introduction
fp_cc1 = sp.solve(sp.Eq(Rn_cc1, R), R)[0]
print(f"   fixed point (revised model, b on clean fraction) = {sp.simplify(fp_revised)}")
print(f"   fixed point (unconditional introduction)          = {sp.simplify(fp_cc1)}")
rep("3.4 CC1's b/p is the fixed point of the UNCONDITIONAL recursion",
    sp.simplify(fp_cc1 - b / p) == 0)
rep("3.4 REFUTED as stated: the revised model's own fixed point is b/(p+b), NOT b/p",
    sp.simplify(fp_revised - b / (p + b)) == 0)
print("   CC1 figures vs the revised model's own equation, p=0.35:")
rows = []
for bv in (0.02, 0.10, 0.20):
    cc1v = bv / 0.35
    rev = bv / (0.35 + bv)
    # independent: iterate the revised recursion with mpmath to convergence
    x = mp.mpf(0)
    for _ in range(4000): x = (1 - mp.mpf("0.35")) * x + mp.mpf(str(bv)) * (1 - x)
    rows.append((bv, cc1v, rev, float(x)))
    print(f"     b={bv:<5} CC1 b/p={cc1v:6.2%}   revised b/(p+b)={rev:6.2%}   mpmath iterate={float(x):6.2%}")
rep("3.4 mpmath iteration of the revised recursion agrees with b/(p+b), not b/p",
    all(abs(r[2] - r[3]) < 1e-12 and abs(r[1] - r[3]) > 1e-6 for r in rows))
# Direction of the error: CC1 OVERSTATES residual risk in every case.
rep("3.4 CC1's b/p is an UPPER BOUND on the revised model's residual (overstates)",
    all(r[1] > r[2] for r in rows))
# But the qualitative claim survives: flat decay is consistent with LARGE residual.
rep("3.4 QUALITATIVE claim survives: flat curve compatible with >30% residual",
    rows[2][2] > 0.30, f"b=0.20 -> {rows[2][2]:.2%} under the revised model")

print("\n" + "=" * 62)
print(f"{sum(out.values())}/{len(out)} checks passed")
print("FAILED: " + (", ".join(k for k, v in out.items() if not v) or "none"))
