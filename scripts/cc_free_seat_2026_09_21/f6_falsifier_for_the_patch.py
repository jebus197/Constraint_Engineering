"""F6. FALSIFIER for every claim in PATCH_appendix_phase2_and_floor.md.

Imports the REAL bench.reference_runner_v3. Raises AssertionError / prints
FALSIFIED if any claim in the patch is wrong. Exits clean if the patch is right.
"""
import sys, math, sympy as sp, numpy as np
sys.path.insert(0, ".")
from bench.reference_runner_v3 import compute_rk

# WIRED 2026-09-24 (CC1). Module-level work, so no main() to intercept `--help`.
import sys as _s, pathlib as _p
_s.path.insert(0, str(_p.Path(__file__).resolve().parents[1]))
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

fail = []
def claim(name, ok):
    print(f"  [{'OK ' if ok else 'BAD'}] {name}")
    if not ok: fail.append(name)

R, q, s, nu = sp.symbols('R q sigma nu', positive=True)
R_det = R*(1-q)/(1-q*R)
mixture = sp.simplify((1-q*R)*R_det + q*R*(1-s))
appendix = s*R_det + (1-s)*R

print("PATCH CORRECTION 1 — Phase 2 justification")
claim("mixture equals R_old*(1 - q*sigma)", sp.simplify(mixture - R*(1-q*s)) == 0)
claim("mixture at sigma=0 is exactly R_old", sp.simplify(mixture.subs(s,0) - R) == 0)
claim("free-decrease term is q*R(1-R)/(1-qR)",
      sp.simplify((R - R_det) - q*R*(1-R)/(1-q*R)) == 0)
claim("appendix excess is sigma*q*R^2(1-q)/(1-qR)",
      sp.simplify((appendix - mixture) - s*q*R**2*(1-q)/(1-q*R)) == 0)
# "never understates risk" — numeric sweep on the REAL code vs the exact mixture
rng = np.random.default_rng(7)
N = 200000
R0, qq, ss = (rng.uniform(1e-9, 1-1e-9, N) for _ in range(3))
code = np.array([compute_rk(a, b, c, nu_b=0.0, nu_f=0.0) for a, b, c in
                 zip(R0[:20000], qq[:20000], ss[:20000])])
exact = (R0*(1-qq*ss))[:20000]
claim("shipped compute_rk NEVER understates the exact mixture (20000 pts)",
      bool(np.all(code >= exact - 1e-12)))

print("\nPATCH CORRECTION 2 — the floor")
f1 = ((R*(1-q)/(1-q*R)))*(1-nu) + nu       # sigma = 1 cycle
roots = sp.solve(sp.Eq(f1, R), R)
claim("fixed points are {1, nu/q}", set(map(sp.simplify, roots)) == {sp.Integer(1), nu/q})
claim("f'(1) = (1-nu)/(1-q)", sp.simplify(sp.diff(f1,R).subs(R,1) - (1-nu)/(1-q)) == 0)
# the exact attracting limit, in the SHIPPED code
for qv, nv in ((0.2,0.05),(0.4,0.05),(0.5,0.10)):
    x = 0.5
    for _ in range(6000): x = compute_rk(x, qv, 1.0, nu_b=nv, nu_f=0.0)
    claim(f"shipped orbit q={qv} nu={nv} -> nu/q = {nv/qv:.4f} (got {x:.6f})",
          abs(x - nv/qv) < 1e-7)
x = 0.5
for _ in range(6000): x = compute_rk(x, 0.1, 1.0, nu_b=0.3, nu_f=0.0)
claim("nu>q -> orbit goes to 1 (certain failure)", abs(x-1.0) < 1e-9)
claim("stated floor nu is LOOSE: nu/q > nu at q=0.2,nu=0.05 (0.25 vs 0.05)",
      abs(0.05/0.2 - 0.25) < 1e-12)

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k/n; d = 1+z*z/n; c = (p+z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return (max(0.0,c-h), min(1.0,c+h))
lo, hi = wilson(0, 1247)
print(f"\nWILSON, brief's 0-of-1247 new-REJECTED reach: [{100*lo:.4f}%, {100*hi:.4f}%]"
      f"  (brief states [0.0000%, 0.3071%])")
claim("Wilson upper bound reproduces the brief's 0.3071%", abs(100*hi - 0.3071) < 0.01)

print()
if fail:
    print("FALSIFIED:", fail); raise AssertionError(fail)
print("PATCH CLAIMS ALL HOLD — no FALSIFIED token, clean exit.")
