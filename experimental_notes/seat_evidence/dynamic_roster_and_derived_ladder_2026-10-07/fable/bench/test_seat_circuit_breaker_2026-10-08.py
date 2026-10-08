# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4f4e006ace1ba2ddaff53788627280faad8bc04095031bd41b0ee765f38b8418
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for bench/seat_circuit_breaker.py. Imports the real module;
AssertionError / FALSIFIED iff a claimed property fails."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import seat_circuit_breaker as scb
from seat_circuit_breaker import BreakerState, RosterBreakers

# 1. No terminal state exists: the type cannot express benching.
names = {m.name for m in BreakerState}
assert names == {"CLOSED", "OPEN", "HALF_OPEN"}, f"FALSIFIED: extra state {names}"
assert not any("bench" in n.lower() or "removed" in n.lower() or "retired" in n.lower()
               for n in names)
# ... and no removal API on the roster or the breaker.
api = [a for a in dir(RosterBreakers) if not a.startswith("_")]
assert not any(k in a.lower() for a in api for k in ("remove", "drop", "bench", "retire")), \
    f"FALSIFIED: removal API present: {api}"

# 2. Requirement 8: a mid-run failure does not block the round -- the rest of
#    the roster is dispatched the same round.
r = RosterBreakers(["A", "B", "C"])
r["B"].record_dispatch_failure(2, "HTTP 402 cascade")
live = r.dispatchable(3, {"A": lambda: True, "B": lambda: False, "C": lambda: True})
assert live == ["A", "C"], f"FALSIFIED: round blocked or wrong roster: {live}"

# 3. Requirement 9: the seat is re-probed EVERY round boundary and readmitted
#    the moment the probe passes -- recovery is automatic, not operator policy.
probe_results = iter([False, False, True])
for rnd in (4, 5, 6):
    live = r.dispatchable(rnd, {"A": lambda: True,
                                "B": lambda: next(probe_results),
                                "C": lambda: True})
assert live == ["A", "B", "C"], "FALSIFIED: recovered seat not readmitted"
assert r["B"].state is BreakerState.CLOSED
assert any("readmitted" in h for h in r["B"].history)
assert r["B"].reopened_count == 3  # every failed probe (r3,r4,r5) counted, not hidden

# 4. Requirement 6: an outage is not a capability signal -- this module never
#    touches the estimator. Structural: it imports nothing from
#    capability_estimator and writes no capability field.
src = Path(scb.__file__).read_text()
assert "capability_estimator" not in src.replace("bench/degradation", "")
assert "wilson" not in src.lower()

# 5. A CLOSED seat is never probed (no wasted dispatches): its probe callable
#    is not invoked.
calls = {"n": 0}
def counting_probe():
    calls["n"] += 1
    return True
r2 = RosterBreakers(["X"])
r2.dispatchable(1, {"X": counting_probe})
assert calls["n"] == 0, "FALSIFIED: healthy seat probed every round (spend)"

print("OK: circuit-breaker third state holds every claimed property")
print("  states:", sorted(names), " history(B):", r["B"].history)
