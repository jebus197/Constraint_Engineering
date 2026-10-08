# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6c53a01639c574f5f430eec2ae97ae68769dc89e141ba5d49f2df6e5fe34743b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for bench/capability_estimator.py.

Imports the REAL module. Raises AssertionError / prints FALSIFIED if any claimed
property is absent; exits cleanly if the fixes behave as specified.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from capability_estimator import (AttemptRecord, CapabilityEstimator,
                                  first_attempt_of_a_new_model)
from routing import DEFAULT_FALSIFIER_STRENGTH

est = CapabilityEstimator()
T = "2026-10-08T00:00:00Z"

def rec(seat, n_ok, n_fail, lat, money, prov=True):
    for i in range(n_ok):
        est.record_attempt(AttemptRecord(seat, f"C{i:04d}", "CONFIRMED", prov, lat, money, T))
    for i in range(n_fail):
        est.record_attempt(AttemptRecord(seat, f"F{i:04d}", "ERROR", prov, lat, money, T))

# R6 guard 1: a CONFIRMED with provenance_ok=False must NOT count as a success.
e2 = CapabilityEstimator()
e2.record_attempt(AttemptRecord("gem", "C0001", "CONFIRMED", False, 10, 0, T))
assert e2.capability("gem").successes == 0, "FALSIFIED: detached CONFIRMED counted as success"
assert e2.capability("gem").attempts == 1, "FALSIFIED: attempt not recorded"
# R6 guard 2: unchecked provenance (None) must not count either.
e2.record_attempt(AttemptRecord("gem", "C0002", "CONFIRMED", None, 10, 0, T))
assert e2.capability("gem").successes == 0, "FALSIFIED: unchecked CONFIRMED counted"
# R6 guard 3: the model's own verdict never enters -- only the field the
# runner's reverify wrote. (Structural: AttemptRecord has no model-verdict field.)
assert "model_verdict" not in AttemptRecord.__dataclass_fields__

# Part C: 1/1 does not outrank 60/70; 12 consecutive needed.
rec("veteran", 60, 10, 30, 1.0)
rec("lucky", 1, 0, 30, 1.0)
v = est.capability("veteran").wilson_lower
l = est.capability("lucky").wilson_lower
assert abs(v - 0.756616) < 1e-5 and abs(l - 0.206549) < 1e-5, "FALSIFIED: Wilson values"
assert v > l, "FALSIFIED: one lucky success outranked the veteran"
e3 = CapabilityEstimator()
n = 0
while e3.capability("new").wilson_lower <= v:
    e3.record_attempt(AttemptRecord("new", f"N{n}", "CONFIRMED", True, 30, 1.0, T)); n += 1
assert n == 12, f"FALSIFIED: needed {n} consecutive successes, claim is 12"

# R7: the brief's 4-weak+1-strong example. Wilson bounds need large n to
# approximate p=0.02 / p=0.8; use point-rate seats built from big samples.
e4 = CapabilityEstimator()
rec2 = lambda s, k, n, lat, money: [e4.record_attempt(
    AttemptRecord(s, f"{s}{i}", "CONFIRMED" if i < k else "REFUTED", True, lat, money, T))
    for i in range(n)]
rec2("strong", 8000, 10000, 60, 100.0)   # p_lo ~ 0.792
for w in ("w1", "w2", "w3", "w4"):
    rec2(w, 200, 10000, 60, 1.0)          # p_lo ~ 0.0174
money_only = e4.order_seats(["w1","w2","w3","w4","strong"], latency_weight=0.0)
waited     = e4.order_seats(["w1","w2","w3","w4","strong"], latency_weight=2.0)
assert money_only[0] != "strong", "FALSIFIED: money-only already strong-first (example broken)"
assert waited[0] == "strong", "FALSIFIED: latency-priced key did not restore capability-first"
# and the reorder came from the SAME key, no new rule: expected dispatches improve
assert e4.expected_dispatches(waited) < e4.expected_dispatches(money_only)

# Cold start: all bounds 0 -> order falls back to the measured Exp-42 tuple.
e5 = CapabilityEstimator()
cold = e5.order_seats(list(reversed(DEFAULT_FALSIFIER_STRENGTH)) + ["Kimi"],
                      strength_order=DEFAULT_FALSIFIER_STRENGTH)
assert cold[:6] == list(DEFAULT_FALSIFIER_STRENGTH), f"FALSIFIED: cold start ignored the measured tuple: {cold}"
assert cold[-1] == "Kimi", "FALSIFIED: unlisted new seat not tried last"

# New model's first attempt: bound 0, sorts last, climbs only on evidence.
info = first_attempt_of_a_new_model(e5, "Kimi")
assert info == {"seat": "Kimi", "attempts": 0, "wilson_lower": 0.0, "sorts_last": True}

# Q5: Kimi reserve emerges from arithmetic, and "last" is EARNED by the other
# seats' measured competence, not decreed by name (requirement 3). With
# realistic mid-capability seats (30-80% resolve, cheap), a Moonshot-priced
# Kimi lands last and is reached only on findings all of them failed.
e6 = CapabilityEstimator()
rec3 = lambda s, k, n, lat, money: [e6.record_attempt(
    AttemptRecord(s, f"{s}x{i}", "CONFIRMED" if i < k else "REFUTED", True, lat, money, T))
    for i in range(n)]
rec3("Codex", 800, 1000, 60, 2.0)
rec3("CC2", 700, 1000, 90, 0.0)      # free seat: latency term keeps c > 0
rec3("Gemini", 500, 1000, 60, 2.0)
rec3("DeepSeek", 300, 1000, 60, 1.0)
rec3("Kimi", 850, 1000, 120, 500.0)  # strong AND expensive
order = e6.order_seats(["DeepSeek","Kimi","CC2","Codex","Gemini"], latency_weight=1.0)
assert order[-1] == "Kimi", f"FALSIFIED: reserve depth not derived: {order}"
# the exchange rule itself: every adjacent pair satisfies p_i*c_j >= p_j*c_i
for a, b in zip(order, order[1:]):
    pa, pb = e6.capability(a).wilson_lower, e6.capability(b).wilson_lower
    ca, cb = e6.dispatch_cost(a, 1.0), e6.dispatch_cost(b, 1.0)
    assert pa*cb >= pb*ca - 1e-12, f"FALSIFIED: exchange rule violated at {a},{b}"
from math import prod
reach_kimi = prod(1 - e6.capability(s).wilson_lower for s in order[:-1])
assert reach_kimi < 0.05, "FALSIFIED: Kimi reached on an easy majority"
# and if every other seat is nearly useless, the key correctly REFUSES to waste
# the researcher's wait on them -- reserve is conditional on measured competence:
for w in ("w1","w2","w3","w4"):
    rec3(w, 20, 1000, 60, 1.0)   # near-useless: ~1.3% lower bound
order2 = e6.order_seats(["w1","w2","w3","w4","Kimi"], latency_weight=1.0)
assert order2[0] == "Kimi", "FALSIFIED: key wasted dispatches on near-useless seats"

# Bidirectional (R5): lower a strong seat's measured rate and it falls.
before = e4.order_seats(["strong","w1"], latency_weight=1.0)
for i in range(500000):
    e4.record_attempt(AttemptRecord("strong", f"bad{i}", "ERROR", True, 60, 100.0, T))
after = e4.order_seats(["strong","w1"], latency_weight=1.0)
assert before[0] == "strong" and after[0] == "w1", "FALSIFIED: ladder not bidirectional"

print("OK: all capability-estimator properties hold")
print("  veteran wilson_lo:", round(v,6), " lucky:", round(l,6),
      " consecutive-needed:", n)
print("  money-only order:", money_only, "\n  latency-priced  :", waited)
print("  cold-start order:", cold)
print("  P(reach Kimi):", round(reach_kimi, 4))
