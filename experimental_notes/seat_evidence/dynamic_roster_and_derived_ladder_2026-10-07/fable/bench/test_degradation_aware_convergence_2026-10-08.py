# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 375e335fe1d739d2ac61b38fce0267923a15f9a6d248062496f131a466694c73
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for bench/degradation_aware_convergence.py. Imports the real
module; AssertionError / FALSIFIED iff a claimed property fails."""
import sys
from pathlib import Path
from fractions import Fraction
sys.path.insert(0, str(Path(__file__).resolve().parent))
from degradation_aware_convergence import (
    RoundAttendance, quiet_window_state, convergence_record,
    required_seat_rounds, equivalent_quiet_rounds)

SIX = tuple("ABCDEF")
K = 3

def att(r, live):
    return RoundAttendance(r, SIX, tuple(SIX[:live]))

# 1. ADDITIVE: full roster, K quiet rounds -> converges exactly as today.
crit = [2, 1, 0, 0, 0]
a = [att(i, 6) for i in range(5)]
s = quiet_window_state(crit, a, K)
assert s["quiet_ok"] and s["seat_rounds_quiet"] == 18 and not s["degraded_in_window"]
# ... and K-1 quiet rounds do NOT converge (unchanged strictness).
s2 = quiet_window_state([2, 1, 0, 0], [att(i, 6) for i in range(4)], K)
assert not s2["quiet_ok"], "FALSIFIED: full-roster gate loosened"

# 2. THE HAZARD IS CLOSED: 4 live seats, 3 quiet rounds = 12 seat-rounds < 18
#    -> NOT converged, where the current gate would converge.
crit = [2, 0, 0, 0]
a = [att(0, 6), att(1, 4), att(2, 4), att(3, 4)]
s = quiet_window_state(crit, a, K)
assert not s["quiet_ok"], "FALSIFIED: depleted roster still converges on K rounds"
assert s["seat_rounds_quiet"] == 12 and s["seat_rounds_needed"] == 18
# ... but 5 quiet rounds at 4 live (20 >= 18) DO converge: requirement 8,
#     dropout does not block convergence, it prices it.
crit = [2, 0, 0, 0, 0, 0]
a = [att(0, 6)] + [att(i, 4) for i in range(1, 6)]
s = quiet_window_state(crit, a, K)
assert s["quiet_ok"], "FALSIFIED: degraded run blocked from converging"
assert s["degraded_in_window"] == [1, 2, 3, 4, 5]
rec = convergence_record(s, a)
assert rec["degraded_convergence"] is True
assert rec["verdict_suffix"] == "_DEGRADED_ROSTER"
assert all("n_live" in r and "n_configured" in r for r in rec["roster_by_round"])

# 3. SEPARABILITY (the z3 point, re-proved by exhaustion here): for every
#    observed quiet-round count 0..10, the OLD gate's inputs are identical for
#    intact and depleted rosters; the NEW record differs on every one.
for quiet_rounds in range(11):
    crit = [1] + [0] * quiet_rounds
    intact = [att(i, 6) for i in range(quiet_rounds + 1)]
    depleted = [att(0, 6)] + [att(i, 2) for i in range(1, quiet_rounds + 1)]
    old_view_intact = crit            # the count is all the old gate sees
    old_view_depleted = crit
    assert old_view_intact == old_view_depleted   # indistinguishable (unsat)
    ri = convergence_record(quiet_window_state(crit, intact, K), intact)
    rd = convergence_record(quiet_window_state(crit, depleted, K), depleted)
    if quiet_rounds:
        assert ri["roster_by_round"] != rd["roster_by_round"], "FALSIFIED: records identical"
        assert ri["degraded_convergence"] != rd["degraded_convergence"]

# 4. THE DESIGN POINT HOLDS AT EVERY ROSTER SIZE (exact rationals):
#    P(spurious quiet) under independence <= (1-q)^(n0*K0) for n_live = 1..6.
q = Fraction(3, 10)
design = (1 - q) ** required_seat_rounds(6, K)
for n_live in range(1, 7):
    k_eff = equivalent_quiet_rounds(6, n_live, K)
    p_spur = (1 - q) ** (n_live * k_eff)
    assert p_spur <= design, f"FALSIFIED: design point broken at n_live={n_live}"
# and the OLD gate breaks it everywhere below 6 (the measured 8.49986-fold at 4):
old_4 = (1 - q) ** (4 * K)
assert old_4 / design == Fraction(10, 7) ** 6, "FALSIFIED: hazard arithmetic wrong"

# 5. A novel critical resets the window regardless of roster.
crit = [0, 0, 1, 0, 0, 0]
a = [att(i, 6) for i in range(6)]
s = quiet_window_state(crit, a, K)
assert s["window_rounds"] == [3, 4, 5] and s["seat_rounds_quiet"] == 18

# 6. Zero live seats: evidence is unobtainable and the helper refuses.
try:
    equivalent_quiet_rounds(6, 0, K)
    print("FALSIFIED: zero-seat run produced an evidence requirement")
    sys.exit(1)
except ValueError:
    pass

print("OK: degradation-aware quiet window holds every claimed property")
print("  fold restored at n_live=4:", float(old_4 / design), "-> 1.0 with K_eff =",
      equivalent_quiet_rounds(6, 4, K))
