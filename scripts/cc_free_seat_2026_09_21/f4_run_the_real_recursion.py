"""F4. Run the REAL compute_rk. Section 3: a seat that has not executed the recursion has not answered."""
import sys, math, numpy as np, mpmath as mp
sys.path.insert(0, ".")
from bench.reference_runner_v3 import compute_rk, RK0_PI_BASE

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
mp.mp.dps = 40

print("A. compute_rk AT THE sigma=0 ENDPOINT UNDER REVIEW (nu_b=nu_f=0 to isolate Phase 2)")
for R0 in (0.2, 0.5, 0.8):
    for qq in (0.3, 0.7):
        got = compute_rk(R0, qq, 0.0, nu_b=0.0, nu_f=0.0)
        post = R0*(1-qq)/(1-qq*R0)
        print(f"   R_old={R0} q={qq}: compute_rk={got:.12f}  R_old={R0:.12f}  posterior={post:.12f}"
              f"   -> reverts to prior: {abs(got-R0)<1e-12}")
        assert abs(got - R0) < 1e-12
print("   CONFIRMED IN CODE: the implementation reverts to the prior at sk=0.")

print("\nB. compute_rk AT sigma=1, nu=0 REDUCES TO THE STAGE-4 DETECTION RECURSION")
for R0, qq in ((0.5,0.3),(0.8,0.6),(0.1,0.9)):
    got = compute_rk(R0, qq, 1.0, nu_b=0.0, nu_f=0.0)
    ref = float(mp.mpf(R0)*(1-mp.mpf(qq))/(1-mp.mpf(qq)*mp.mpf(R0)))
    print(f"   R_old={R0} q={qq}: compute_rk={got:.15f} stage4={ref:.15f} agree={abs(got-ref)<1e-12}")
    assert abs(got-ref) < 1e-12

print("\nC. ORBIT CONVERGENCE AND THE nu_b VS q THRESHOLD, IN THE REAL CODE (sk=1 -> nu_eff=nu_b)")
for qq, nb in ((0.40,0.05),(0.20,0.05),(0.10,0.30),(0.05,0.05)):
    R = RK0_PI_BASE
    for _ in range(4000):
        R = compute_rk(R, qq, 1.0, nu_b=nb, nu_f=0.0)
    pred = 1.0 if nb >= qq else nb/qq
    tol = 1e-2 if abs(nb-qq) < 1e-12 else 1e-6   # nu==q is a PARABOLIC fixed point
    note = "  [nu==q: f'(1)=1, parabolic, approach is O(1/n) not geometric]" if abs(nb-qq)<1e-12 else ""
    print(f"   q={qq} nu_b={nb}: orbit limit={R:.10f}  predicted nu_b/q (or 1)={pred:.10f}"
          f"  agree={abs(R-pred)<tol}{note}")
    assert abs(R-pred) < tol
print("   THE nu > q CERTAIN-FAILURE THRESHOLD IS REAL IN THE SHIPPED CODE.")
print("   NOTE: the appendix's stated floor 'lim R >= nu' is LOOSE; the exact")
print("         attracting limit is nu/q. At q=0.20, nu_b=0.05 it is 0.25, not 0.05.")

print("\nD. NumPy x mpmath CROSS-CHECK OF THE CONSERVATION DEFICIT, 200000 POINTS")
rng = np.random.default_rng(20260921)
N = 200000
R0 = rng.uniform(1e-6, 1-1e-6, N); qq = rng.uniform(1e-6, 1-1e-6, N)
post = R0*(1-qq)/(1-qq*R0)
deficit = R0 - post                      # what CC1's revision loses at sigma=0
closed  = qq*R0*(1-R0)/(1-qq*R0)         # F1's derived closed form
print(f"   max |deficit - closed form| = {np.max(np.abs(deficit-closed)):.3e}")
print(f"   deficit > 0 at all {N} points : {bool(np.all(deficit>0))}")
print(f"   mean deficit {np.mean(deficit):.6f}  max deficit {np.max(deficit):.6f}")
assert np.all(deficit > 0) and np.max(np.abs(deficit-closed)) < 1e-12
i = int(np.argmax(deficit))
mR, mq = mp.mpf(float(R0[i])), mp.mpf(float(qq[i]))
mp_def = mR - mR*(1-mq)/(1-mq*mR)
print(f"   mpmath@40dps at the worst point: {mp_def}")
print(f"   NumPy agrees to 1e-12: {abs(float(mp_def)-deficit[i])<1e-12}")
print("\nALL ASSERTIONS PASSED.")
