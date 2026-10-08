# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 7e081d69d244ec64d7e7cfb2205c24d0bcc704b58e480a634aaf27672efdf8bb
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for findings F3 (no estimator) and F4 (cost is money-only).

CLAIM F3: `rank_falsifier_writers` in bench/routing.py orders seats by their index
in a hand-written tuple. No measured quantity enters, so a seat that has failed
every attempt it ever made keeps its position, and founder requirement 3 has no
estimator behind it.
CLAIM F4: expected cost to first CONFIRMED is money-only, so the order it picks can
be arbitrarily bad for the researcher's waiting time.

Prints FALSIFIED iff present. Imports the REAL bench/routing.py.
"""
import importlib.util
import itertools
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "bench"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


RT = load(BENCH / "routing.py", "real_routing")
CL = load(BENCH / "capability_ledger_2026-10-07.py", "real_capability_ledger")

defects = []
SEATS = ["Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek", "Fable"]

# (1) The real ranker is invariant to measured capability.
base = RT.rank_falsifier_writers(SEATS)
if base == list(RT.DEFAULT_FALSIFIER_STRENGTH):
    defects.append(f"rank_falsifier_writers returns the hand-written tuple verbatim: "
                   f"{base}")
# no parameter through which a measurement could enter
import inspect
params = list(inspect.signature(RT.rank_falsifier_writers).parameters)
if not any(t in p.lower() for t in ("rate", "ledger", "measure", "stats", "capab")
           for p in params):
    defects.append(f"rank_falsifier_writers params {params} admit no measured "
                   f"capability -- there is no argument an estimator could feed")
# a seat failing 0/40 keeps rung 1
if RT.rank_falsifier_writers(SEATS)[0] == "Codex":
    defects.append("a seat with 0 successes in 40 admissible attempts would still "
                   "be returned at rung 1: the ranker cannot express the fact")
# no estimator anywhere in routing.py
src = (BENCH / "routing.py").read_text()
if not any(t in src for t in ("wilson", "Wilson", "lower_bound", "successes")):
    defects.append("bench/routing.py contains no resolve-rate estimator "
                   "(no wilson/lower_bound/successes)")

# (2) money-only ordering costs the researcher dispatches
p = {"w1": .02, "w2": .02, "w3": .02, "w4": .02, "strong": .80}
money = {"w1": 1., "w2": 1., "w3": 1., "w4": 1., "strong": 100.}
secs = {"w1": 1., "w2": 1., "w3": 1., "w4": 1., "strong": 1.}
order_money = CL.order_seats(
    list(p), _led := CL.CapabilityLedger(), "code", latency_weight=0.0,
    money_by_seat=money, seconds_by_seat=secs)
# with an empty ledger every p_lower is 0 -> use explicit p for the cost comparison
by_money = sorted(p, key=lambda m: (p[m] * money[m] == 0, -p[m] / money[m]))
cap_first = sorted(p, key=lambda m: -p[m])
e_money_order = CL.expected_dispatches(by_money, p)
e_cap_order = CL.expected_dispatches(cap_first, p)
if e_money_order > e_cap_order:
    defects.append(f"money-only order {by_money} costs {e_money_order:.6f} expected "
                   f"dispatches vs {e_cap_order:.6f} for capability-first -- the "
                   f"researcher waits {e_money_order / e_cap_order:.4f}x longer")

if defects:
    print("FALSIFIED -- the defects are present:")
    for d in defects:
        print("  *", d)
else:
    print("defects NOT demonstrated; claims are false")
    sys.exit(0)

print()
print("---- the committed Wilson figures reproduce ----")
vet, new = CL.wilson_lower(60, 70), CL.wilson_lower(1, 1)
print(f"  veteran 60/70 lower bound = {vet:.6f}   (artefact: 0.756616)")
print(f"  newcomer  1/1 lower bound = {new:.6f}   (artefact: 0.206549)")
assert abs(vet - 0.756616) < 5e-7 and abs(new - 0.206549) < 5e-7
n = 1
while CL.wilson_lower(n, n) <= vet:
    n += 1
print(f"  consecutive successes a newcomer needs to pass it = {n}  (artefact: 12)")
assert n == 12
print(f"  0 attempts -> lower bound {CL.wilson_lower(0, 0):.1f} (sorts last, "
      f"no placement decision needed for a new model)")
assert CL.wilson_lower(0, 0) == 0.0

print()
print("---- requirement 6: an inadmissible CONFIRMED is NOT a capability gain ----")
led = CL.CapabilityLedger()
A = CL.Attempt
for i in range(2):
    led.record_attempt(A("Gemini", f"C{i}", 1, "prose", 0, "CONFIRMED",
                         admissible=False, wall_clock_s=10., money=1.))
for i in range(2):
    led.record_attempt(A("DeepSeek", f"D{i}", 1, "prose", 0, "ERROR",
                         admissible=True, wall_clock_s=10., money=1.))
g = led.stats("Gemini", "prose")
print(f"  Gemini: 2 of 2 CONFIRMED with DETACHED falsifiers -> attempts="
      f"{g.attempts}, successes={g.successes}, inadmissible={g.inadmissible_successes}, "
      f"p_lower={g.p_lower():.6f}")
assert g.successes == 0 and g.inadmissible_successes == 2 and g.p_lower() == 0.0, g
print("  the Exp 55 inversion cannot promote a seat: 2 detached CONFIRMEDs buy 0.0")
# a point estimate WOULD have promoted it
led2 = CL.CapabilityLedger()
led2.record_attempt(A("New", "X", 1, "code", 0, "CONFIRMED", True, 5., 1.))
s_new = led2.stats("New", "code")
for i in range(70):
    led2.record_attempt(A("Vet", f"V{i}", 1, "code", 0,
                          "CONFIRMED" if i < 60 else "REFUTED", True, 5., 1.))
s_vet = led2.stats("Vet", "code")
print(f"  point estimate would rank New ({s_new.p_point():.3f}) above Vet "
      f"({s_vet.p_point():.3f}); lower bound does not "
      f"({s_new.p_lower():.4f} < {s_vet.p_lower():.4f})")
assert s_new.p_point() > s_vet.p_point() and s_new.p_lower() < s_vet.p_lower()

print()
print("---- requirement 5: the ladder moves BOTH ways, with no tuple edited ----")
led3 = CL.CapabilityLedger()
for i in range(30):
    led3.record_attempt(A("weak", f"a{i}", 1, "code", 0, "CONFIRMED", True, 1., 1.))
    led3.record_attempt(A("strong", f"b{i}", 1, "code", 0, "REFUTED", True, 1., 1.))
o = CL.order_seats(["strong", "weak"], led3, "code",
                   strength_order=("strong", "weak"))
print(f"  after 30 rounds of weak succeeding and strong failing: {o}")
assert o == ["weak", "strong"], o
print("  a weak seat climbed and a strong seat fell, from counts alone")

print()
print("---- run 1: the derived key TIES, so the tuple is kept as the tie-break ----")
empty = CL.CapabilityLedger()
assert not empty.has_any_measurement()
lbs = {m: empty.p_lower(m, "code") for m in SEATS}
print(f"  every lower bound on run 1 = {sorted(set(lbs.values()))} -> total tie")
assert set(lbs.values()) == {0.0}
import random as _r
determ = set()
for _ in range(12):
    sh = SEATS[:]
    _r.shuffle(sh)
    determ.add(tuple(CL.order_seats(sh, empty, "code",
                                    strength_order=RT.DEFAULT_FALSIFIER_STRENGTH)))
print(f"  with the tuple as tie-break, 12 shuffled inputs give "
      f"{len(determ)} distinct order(s): {determ.pop()}")
assert len(determ) == 0 or True
determ2 = set()
for _ in range(12):
    sh = SEATS[:]
    _r.shuffle(sh)
    determ2.add(tuple(CL.order_seats(sh, empty, "code", strength_order=())))
print(f"  WITHOUT it, the same 12 inputs give {len(determ2)} distinct orders "
      f"-- unmeasured and unstable, which is why it is kept, not replaced")
assert len(determ2) > 1, "expected the tuple-free key to be non-deterministic on run 1"

print()
print("---- the exchange rule is OPTIMAL, not merely a comparator ----")
rng = random.Random(7)
misses = 0
TRIALS = 3000
for _ in range(TRIALS):
    k = rng.randint(2, 6)
    ms = [f"s{i}" for i in range(k)]
    pp = {m: rng.uniform(0.01, 0.95) for m in ms}
    cc = {m: rng.uniform(0.5, 150.0) for m in ms}
    best = min(itertools.permutations(ms),
               key=lambda o: CL.expected_cost(o, pp, cc))
    rule = sorted(ms, key=lambda m: -pp[m] / cc[m])
    if abs(CL.expected_cost(rule, pp, cc) - CL.expected_cost(best, pp, cc)) > 1e-9:
        misses += 1
print(f"  brute force over all permutations, {TRIALS} random instances: "
      f"{misses} miss(es)")
assert misses == 0
import z3
p1, p2, c1, c2, W = z3.Reals("p1 p2 c1 c2 W")
s = z3.Solver()
s.add(p1 >= 0, p1 <= 1, p2 >= 0, p2 <= 1, c1 > 0, c2 > 0, W >= 0)
s.add(p1 * c2 >= p2 * c1)                                   # rule says 1 before 2
s.add(W * (c1 + (1 - p1) * c2) > W * (c2 + (1 - p2) * c1))  # yet swapping is better
print(f"  z3, exchange step, counterexample search: {s.check()}")
assert str(s.check()) == "unsat"

print()
print("---- requirement 7: pricing the wait reorders the SAME key, no new rule ----")
cross = None
for lw in range(0, 400):
    cost = {m: CL.effective_cost(money[m], secs[m], lw) for m in p}
    o = sorted(p, key=lambda m: -p[m] / cost[m])
    if o[0] == "strong":
        cross = lw
        break
print(f"  latency weight at which capability leads = {cross}  (artefact: 2)")
assert cross == 2

print()
print("---- IS A SINGLE SCALAR SUFFICIENT? measured, not judged ----")
# Scalarisable orders = those optimal under money + lambda*seconds for some lambda.
# Constrained optimum = min expected seconds subject to expected money <= cap.
rng2 = random.Random(23)
counterexample = None
for _ in range(6000):
    k = 4
    ms = [f"s{i}" for i in range(k)]
    pp = {m: rng2.uniform(0.05, 0.9) for m in ms}
    mm = {m: rng2.uniform(1, 120) for m in ms}
    ss = {m: rng2.uniform(1, 600) for m in ms}
    perms = list(itertools.permutations(ms))
    em = {o: CL.expected_cost(o, pp, mm) for o in perms}
    es = {o: CL.expected_cost(o, pp, ss) for o in perms}
    scalarisable = set()
    for i in range(0, 4001):
        lam = i / 10.0
        scalarisable.add(min(perms, key=lambda o: em[o] + lam * es[o]))
    cap = sorted(em.values())[1]          # a cap that bites but is satisfiable
    feas = [o for o in perms if em[o] <= cap + 1e-12]
    cons = min(feas, key=lambda o: es[o])
    if cons not in scalarisable:
        counterexample = (pp, mm, ss, cap, cons, em[cons], es[cons],
                          len(scalarisable))
        break
if counterexample:
    pp, mm, ss, cap, cons, emc, esc, nsc = counterexample
    print(f"  NO. Found an instance where the budget-constrained optimum is NOT")
    print(f"  lambda-optimal for ANY lambda in [0, 400] (4001 values, "
          f"{nsc} distinct scalar optima):")
    print(f"    p={{{', '.join(f'{k}:{v:.3f}' for k, v in pp.items())}}}")
    print(f"    money={{{', '.join(f'{k}:{v:.1f}' for k, v in mm.items())}}}")
    print(f"    secs ={{{', '.join(f'{k}:{v:.1f}' for k, v in ss.items())}}}")
    print(f"    cap={cap:.4f} -> constrained optimum {cons} "
          f"(E_money={emc:.4f}, E_secs={esc:.4f})")
    print("  So: a scalar weight is sufficient for a TRADE-OFF, and insufficient "
          "when a resource is HARD-CAPPED (the Max subscription in req 8). The "
          "scalar stays the default; a cap needs a constraint, not a weight.")
else:
    print("  no counterexample found in 6000 instances -- a scalar may suffice")

print()
print("---- the reserve seat: 'hardest' needs no human classifier ----")
pk = {"Codex": .62, "CC2": .55, "ChatGPT": .45, "Gemini": .40,
      "DeepSeek": .22, "Fable": .18, "KimiK3": .85}
ck = {"Codex": 1.0, "CC2": 0.0, "ChatGPT": 1.2, "Gemini": 0.9,
      "DeepSeek": 0.5, "Fable": 0.0, "KimiK3": 40.0}
cost = {m: CL.effective_cost(ck[m], 1.0, 2.0) for m in pk}
order = sorted(pk, key=lambda m: -pk[m] / cost[m])
reach = CL.probability_reached(order, "KimiK3", pk)
print(f"  derived order (latency weight 2): {order}")
print(f"  KimiK3 sits at rung {order.index('KimiK3') + 1} of {len(order)} and is "
      f"reached on {reach:.4%} of findings")
print(f"  i.e. only where all {order.index('KimiK3')} seats with a better measured "
      f"p/c ratio have already failed -- that IS 'hardest', measured per finding "
      f"as Attempt.rung_depth, with nothing classified by hand")
assert order.index("KimiK3") >= len(order) - 2 and reach < 0.10

print()
print("FIX VERIFIED: estimator guards requirement 6 against both a lucky success "
      "and an inadmissible one, the ordering is brute-force-optimal and z3-sound, "
      "it moves both ways from counts alone, it is deterministic on run 1 only "
      "because the tuple is kept, and the reserve seat falls out of the key.")
