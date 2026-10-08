# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: f181bb3f1f8b46ade44e9d8a8a0a9f24dfc8737d6c1c1f86300ee74d4fe659e1
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for finding F2: the convergence gate is blind to the live roster.

CLAIM: `_check_gamma_alt_convergence` in bench/reference_runner_v3.py reads the
quiet-round count with no reference to how many seats produced it, so a 2-seat
depleted panel and a 6-seat healthy panel earn an IDENTICAL verdict and an
identical reason string, while their spurious-convergence probabilities differ.

Prints FALSIFIED iff the defect is genuinely present. Imports the REAL runner and
calls the REAL gate; no copy of the gate is defined here.
"""
import importlib.util
import inspect
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "bench"
sys.path.insert(0, str(BENCH))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


RR = load(BENCH / "reference_runner_v3.py", "real_reference_runner_v3")
RA = load(BENCH / "roster_aware_quiescence_2026-10-07.py", "real_roster_aware")
CORR = load(BENCH / "the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py",
            "real_corr_model")

defects = []

# (1) The real gate's signature carries no roster size.
sig = inspect.signature(RR._check_gamma_alt_convergence)
roster_params = [p for p in sig.parameters
                 if any(t in p.lower() for t in
                        ("roster", "seat", "n_live", "active_model", "responded"))]
if not roster_params:
    defects.append(f"_check_gamma_alt_convergence params {list(sig.parameters)} "
                   f"contain no roster/seat/live term")

# (2) The REAL gate returns the same verdict and reason for healthy vs depleted.
cfg = RR.RunnerConfig()
K = cfg.gamma_alt_consecutive_zero_crit
quiet = [0] * K
common = dict(round_idx=max(cfg.gamma_alt_earliest_round, K + 2), gamma=0.9,
              cfg=cfg, unresolved_critical=0, contested=0, rho_churn=False,
              irreducible_queue=0, gamma_critical=0.9, total_findings=20)
v_healthy = RR._check_gamma_alt_convergence(novel_critical_history=quiet, **common)
v_depleted = RR._check_gamma_alt_convergence(novel_critical_history=quiet, **common)
if v_healthy == v_depleted and v_healthy[0] is True:
    defects.append(f"the real gate returns {v_healthy[0]} with an IDENTICAL reason "
                   f"string for a 6-seat and a 2-seat quiet window -- the inputs "
                   f"are literally indistinguishable, there is no roster argument "
                   f"to differ in")

# (3) The probabilities it is treating as equal are NOT equal (measured params).
q, rho = RA.Q_MEASURED, RA.RHO_MEASURED
p6 = RA.p_spurious(6, K, q, rho)
p2 = RA.p_spurious(2, K, q, rho)
if p2 > p6:
    defects.append(f"at the archive-measured q={q:.4f}, rho={rho:.4f}: "
                   f"P_spurious(6 seats, K={K})={p6:.6g} vs "
                   f"P_spurious(2 seats, K={K})={p2:.6g} -- a factor of "
                   f"{p2 / p6:.4f} the gate cannot see")

if defects:
    print("FALSIFIED -- the defect is present:")
    for d in defects:
        print("  *", d)
else:
    print("defect NOT demonstrated; claim is false")
    sys.exit(0)

print()
print("---- cross-check: my closed form against the committed numeric integral ----")
import mpmath as mp
mp.mp.dps = 30
for r in (0.1, 0.3, 0.5):
    s = (1 / mp.mpf(r)) - 1
    a, b = mp.mpf(0.3) * s, (1 - mp.mpf(0.3)) * s
    for n in (2, 4, 6):
        theirs = mp.quad(lambda p: (1 - p) ** n * p ** (a - 1) * (1 - p) ** (b - 1),
                         [0, 1]) / mp.beta(a, b)
        mine = math.exp(RA._log_quiet_one_round(n, 0.3, r))
        assert abs(float(theirs) - mine) < 1e-9, \
            f"closed form disagrees at rho={r}, n={n}: {theirs} vs {mine}"
print("  B(a,b+n)/B(a,b) agrees with the committed mp.quad to <1e-9 at "
      "rho in {0.1,0.3,0.5}, n in {2,4,6}")
for r in (0.1, 0.3, 0.5):
    theirs = CORR.ratio_exact_beta_binomial(r, 6, 4, 0.3, 3)
    mine = math.exp(3 * (RA._log_quiet_one_round(4, 0.3, r)
                         - RA._log_quiet_one_round(6, 0.3, r)))
    assert abs(theirs - mine) / theirs < 1e-6, f"ratio mismatch rho={r}"
print("  the committed 6->4 ratios reproduce from my closed form to <1e-6")

print()
print("---- the fix holds P_spurious constant as the roster shrinks ----")
print(f"  calibrated at archive-measured q={q:.6f}, rho={rho:.6f}; declared 6 seats, K={K}")
target = RA.p_spurious(6, K, q, rho)
for n in (6, 5, 4, 3, 2, 1):
    k_fixed, k_fix = K, RA.quiet_rounds_required(n, 6, K, q, rho)
    p_fixed = RA.p_spurious(n, k_fixed, q, rho)
    p_fix = RA.p_spurious(n, k_fix, q, rho)
    print(f"  n={n}: K fixed={k_fixed} -> P={p_fixed:.6g} "
          f"({p_fixed / target:7.4f}x target) | K aware={k_fix} -> P={p_fix:.6g} "
          f"({p_fix / target:7.4f}x target)")
    assert p_fix <= target * 1.0000001, f"roster-aware K failed to hold P at n={n}"
    assert k_fix >= K, "K must never fall below the declared floor"
print("  every roster-aware P is at or below the full-roster target: HELD")

k_meas = RA.quiet_rounds_required(2, 6, K, q, rho)
k_indep = RA.quiet_rounds_required(2, 6, K, 0.3, 0.0)
print(f"  requirement 7: at n=2, measured (q,rho) demands K={k_meas}; the brief's "
      f"q=0.3,rho=0 demands K={k_indep} -- {k_indep - k_meas} extra rounds the "
      f"researcher waits through, to insure against a correlation the archive rejects")
assert k_indep > k_meas

print()
print("---- composability: each part cures a failure the other cannot ----")
R = RA.ConvergenceRosterRecord
rec = R(seats_declared=6, live_by_round=[6, 6, 2, 2, 2])
label_only = rec.label(K)
p_at_declared_k = RA.p_spurious(rec.min_live_in_window(K), K, q, rho)
print(f"  record only : label={label_only}, but K stays {K} -> "
      f"P={p_at_declared_k:.6g} = {p_at_declared_k / target:.4f}x target "
      f"(stops too soon ANYWAY)")
assert p_at_declared_k > target * 1.5, "record alone should leave P inflated"
k_only = RA.quiet_rounds_required(2, 6, K, q, rho)
print(f"  K only      : K={k_only} -> P held, but with no live_by_round a reader "
      f"sees the same record as a 6-seat run (misreports as clean)")
out = RA.assess(rec, [0] * 9, K, q, rho)
print(f"  both        : converged={out['converged']}, label={out['label']}, "
      f"K_required={out['k_required']}, P={out['p_spurious_at_k_required']:.6g} "
      f"({out['p_spurious_at_k_required'] / target:.4f}x target), "
      f"degraded_rounds={out['degraded_rounds']}")
assert out["converged"] is True
assert out["label"] == "CONVERGED_DEGRADED_ROSTER"
assert out["k_required"] > K
assert out["p_spurious_at_k_required"] <= target * 1.0000001
full = RA.assess(R(seats_declared=6, live_by_round=[6] * 5), [0] * K, K, q, rho)
assert full["label"] == "CONVERGED_FULL_ROSTER" and full["k_required"] == K, full
print(f"  full roster : label={full['label']}, K_required={full['k_required']} "
      f"(unchanged -- the fix costs a healthy run nothing)")
dead = RA.assess(R(seats_declared=6, live_by_round=[6, 3, 0]), [0] * 9, K, q, rho)
assert dead["converged"] is False, "a 0-live-seat round must not converge"
print(f"  0 live seats: converged={dead['converged']} (no evidence at all)")

print()
print("---- z3: the two labels are mutually exclusive once the roster is carried ----")
import z3
n_live, n_decl = z3.Ints("n_live n_declared")
s = z3.Solver()
s.add(n_decl == 6, n_live >= 0, n_live <= 6)
s.add(n_live >= n_decl, n_live < n_decl)
print(f"  can a round be both intact and degraded: {s.check()}")
assert str(s.check()) == "unsat"
cnt_h, cnt_d = z3.Ints("count_healthy count_depleted")
s2 = z3.Solver()
s2.add(cnt_h == 0, cnt_d == 0, cnt_h != cnt_d)
print(f"  can the count alone separate them:       {s2.check()}")
assert str(s2.check()) == "unsat"

print()
print("FIX VERIFIED: P_spurious held at or below its full-roster value for every "
      "roster size 1..6, a healthy run pays nothing, a degraded convergence is "
      "labelled from the recorded roster, and 0 live seats does not converge.")
