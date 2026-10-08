# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3886c45a757b482ed146911ddd9269d846c70a3053987cba99764ec825bbb7ab
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for the WIRING of the roster-aware window into the real gate.

The additive standard: *"an addition that nothing reaches is not additive either --
every new flag, gate or entry point must be wired to a caller and executed by a
test."* Measured on this project's record, 11 confirmed defects were additions that
did nothing. So this checks the hook is REACHED in the real function, that absent
the new argument the function is byte-identical in behaviour to before, and that a
failure to compute the window SAYS SO rather than silently falling back.
"""
import importlib.util, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; BENCH = ROOT / "bench"
def load(p, n):
    sp = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(sp); sys.modules[n] = m
    sp.loader.exec_module(m); return m
RR = load(BENCH / "reference_runner_v3.py", "wired_rrv3")
cfg = RR.RunnerConfig(); K = cfg.gamma_alt_consecutive_zero_crit
base = dict(round_idx=max(cfg.gamma_alt_earliest_round, 12), gamma=0.9, cfg=cfg,
            unresolved_critical=0, contested=0, rho_churn=False,
            irreducible_queue=0, gamma_critical=0.9, total_findings=20)

# 1) BACKWARD COMPATIBILITY: no new arg -> exactly the old behaviour.
old = RR._check_gamma_alt_convergence(novel_critical_history=[0]*K, **base)
assert old[0] is True, old
assert "roster" not in old[1].lower(), f"unwanted roster text when unwired: {old[1]}"
print(f"unwired call: converged={old[0]} (unchanged), no roster text in reason")
assert RR._check_gamma_alt_convergence(novel_critical_history=[1,0,0], **base)[0] is False

# 2) THE HOOK IS REACHED: a degraded roster raises the window and SAYS SO.
deg = RR._check_gamma_alt_convergence(novel_critical_history=[0]*K,
                                      live_by_round=[6,6,2,2,2], seats_declared=6,
                                      **base)
print(f"degraded, {K} quiet rounds: converged={deg[0]}")
print(f"  reason: ...{deg[1][-150:]}")
assert deg[0] is False, "a 2-seat roster must NOT converge on a 6-seat window"
assert "DEGRADED" in deg[1] and "window raised to 6" in deg[1], deg[1]

# 3) Given the RAISED window of quiet rounds, it does converge, and is LABELLED.
deg_ok = RR._check_gamma_alt_convergence(novel_critical_history=[0]*6,
                                         live_by_round=[6,6,2,2,2], seats_declared=6,
                                         **base)
print(f"degraded, 6 quiet rounds:  converged={deg_ok[0]}")
assert deg_ok[0] is True and "CONVERGED_DEGRADED_ROSTER" in deg_ok[1], deg_ok[1]

# 4) A FULL roster pays nothing.
full = RR._check_gamma_alt_convergence(novel_critical_history=[0]*K,
                                       live_by_round=[6]*5, seats_declared=6, **base)
assert full[0] is True and "CONVERGED_FULL_ROSTER" in full[1], full[1]
print(f"full roster, {K} quiet rounds: converged={full[0]}, label CONVERGED_FULL_ROSTER")

# 5) A failure to compute the window must announce itself, not fall back silently.
import cdsfl_roster_aware as _RA
_orig = _RA.quiet_rounds_required
_RA.quiet_rounds_required = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
try:
    brk = RR._check_gamma_alt_convergence(novel_critical_history=[0]*K,
                                          live_by_round=[6,6,2], seats_declared=6,
                                          **base)
    assert "ROSTER-AWARE WINDOW UNAVAILABLE" in brk[1], brk[1]
    print("broken estimator: reason says UNAVAILABLE rather than silently reverting")
finally:
    _RA.quiet_rounds_required = _orig

print("\nWIRING VERIFIED: the hook is reached in the real gate, absent the new "
      "argument behaviour is unchanged, a degraded roster is refused on the old "
      "window and labelled on the raised one, and a broken estimator is loud.")

# ─── 6) THE CALLER IS WIRED TOO: the hook is maintained, not just accepted. ───
import re
src = (BENCH / "reference_runner_v3.py").read_text()
assert "live_roster_history: List[int] = []" in src, "history never initialised"
assert "live_roster_history.append(len(responses))" in src, "history never appended"
assert "live_by_round=list(live_roster_history)" in src, "history never passed"
# the append must sit in the same loop body as the critical-history append
i_app = src.index("live_roster_history.append(len(responses))")
i_crit = src.index("novel_critical_history.append(novel_critical_this_round)")
assert 0 < i_app - i_crit < 200, "append is not beside the critical-history append"
# order: init < append < pass
i_init = src.index("live_roster_history: List[int] = []")
i_pass = src.index("live_by_round=list(live_roster_history)")
assert i_init < i_app < i_pass, "wiring is out of order"
print("CALLER WIRED: live_roster_history is initialised, appended from `responses` "
      "in the round loop beside novel_critical_history, and passed to the gate -- "
      "so the roster-aware window is reached by the real runner, not merely offered.")
