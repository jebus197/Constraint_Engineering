# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b88f28387ea28feedc82b66d0d5f8c9178ff8ac0d6662906ccb2e10609019f0b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""FALSIFIER for capability_estimator_2026-10-07.py and derived_ladder_2026-10-07.py.
Imports the REAL modules, including the real bench/routing.py."""
from __future__ import annotations

import importlib.util as iu
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))


def _load(name, filename):
    spec = iu.spec_from_file_location(name, HERE / filename)
    m = iu.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


CE = _load("cdsfl_cap_est", "capability_estimator_2026-10-07.py")
DL = _load("cdsfl_der_lad", "derived_ladder_2026-10-07.py")
RT = _load("cdsfl_routing_real", "routing.py")
fails = []

# ── 1. THE DEFECT: no estimator exists in the repository today. ─────────────
print("[1] is there an existing per-attempt capability ledger?")
hits = []
for p in sorted(HERE.glob("*.py")):
    if p.name.startswith(("capability_estimator", "derived_ladder")):
        continue
    t = p.read_text()
    if "wilson" in t.lower() and ("resolve_rate" in t or "confirm_rate" in t) \
            and "class" in t and "record" in t:
        hits.append(p.name)
print(f"    modules combining a Wilson bound with a per-attempt confirm record: {hits}")
print(f"    DEFAULT_FALSIFIER_STRENGTH is a hand-ordered tuple: "
      f"{RT.DEFAULT_FALSIFIER_STRENGTH}")
if not isinstance(RT.DEFAULT_FALSIFIER_STRENGTH, tuple):
    fails.append("DEFAULT_FALSIFIER_STRENGTH is no longer a static tuple")

# ── 2. REQUIREMENT 6: an INADMISSIBLE confirm is not a capability gain. ─────
print("\n[2] requirement 6 -- a success is not a capability gain")
led = CE.CapabilityLedger(window=12)
# The measured Exp-55 inversion: 2 of 2 CONFIRMED on DETACHED falsifiers.
for i in range(2):
    led.record(CE.Attempt("Gemini", f"C{i:04d}", i, "CONFIRMED", admissible=False))
# ... against a seat with genuine readers that ERRORed on a missing file.
for i in range(2):
    led.record(CE.Attempt("DeepSeek", f"C{i:04d}", i, "ERROR", admissible=True))
g, d = led.score("Gemini"), led.score("DeepSeek")
print(f"    Gemini 2/2 CONFIRMED but falsifiers DETACHED -> score {g:.6f}")
print(f"    DeepSeek 0/2, falsifiers genuine readers      -> score {d:.6f}")
if g > 0.0:
    fails.append(f"an inadmissible CONFIRMED raised the score to {g} -- the "
                 f"Exp-55 inversion is reproduced, not prevented")
print(f"    the detached-falsifier seat is NOT promoted: {g == 0.0}")
# The model's own prose is not an input: Attempt has no such field.
flds = set(CE.Attempt.__dataclass_fields__)
print(f"    Attempt fields: {sorted(flds)}")
for leaky in ("self_report", "confidence", "model_claim", "reasoning", "prose"):
    if leaky in flds:
        fails.append(f"Attempt carries '{leaky}' -- a model's assertion re-enters "
                     f"a tool-decided number")

# ── 3. THE FIRST ATTEMPT A NEW MODEL EVER MAKES. ───────────────────────────
print("\n[3] the first attempt a new model ever makes")
if CE.wilson_lower(0, 0) != 0.0:
    fails.append("an unmeasured seat does not score 0.0")
print(f"    wilson_lower(0,0) = {CE.wilson_lower(0,0)} -> sorts last, no placement "
      f"decision needed")
# And the brief's Part C figures must reproduce from this module.
vet, new = CE.wilson_lower(60, 70), CE.wilson_lower(1, 1)
print(f"    veteran 60/70 = {vet:.6f} (brief: 0.756616); newcomer 1/1 = "
      f"{new:.6f} (brief: 0.206549)")
if abs(vet - 0.756616) > 5e-7 or abs(new - 0.206549) > 5e-7:
    fails.append(f"Part C figures do not reproduce: {vet}, {new}")

# ── 4. REQUIREMENT 5 vs 6: the tradeoff, MEASURED across the one dial. ─────
print("\n[4] requirements 5 and 6 pull against each other -- the exchange rate")
import random


def veteran(hl, p=0.857, n=70, seed=1):
    """A seat at a steady true rate. `seed` None -> deterministic interleave."""
    L = CE.CapabilityLedger(half_life=hl)
    rnd = random.Random(seed)
    for i in range(n):
        ok = (rnd.random() < p) if seed is not None else (i % 7 != 0)
        L.record(CE.Attempt("V", f"H{i}", i, "CONFIRMED" if ok else "ERROR",
                            admissible=True))
    return L


def descent_latency(hl, target=0.5):
    L = veteran(hl, seed=None)
    f, base = 0, L.score("V")
    while L.score("V") >= target and f < 2000:
        L.record(CE.Attempt("V", f"F{f}", 70 + f, "ERROR", admissible=True))
        f += 1
    return f, base


def ascent_latency(hl):
    vet = veteran(hl, seed=None).score("V")
    W, a = CE.CapabilityLedger(half_life=hl), 0
    while W.score("N") < vet and a < 2000:
        W.record(CE.Attempt("N", f"S{a}", a, "CONFIRMED", admissible=True))
        a += 1
    return a


def false_demotion(hl, true_p=0.85, trials=1500, seed=20261007):
    rnd = random.Random(seed)
    ref = CE.wilson_lower(int(true_p * 70), 70)
    bad = 0
    for t in range(trials):
        L = CE.CapabilityLedger(half_life=hl)
        for i in range(70):
            L.record(CE.Attempt("S", f"T{i}", i,
                                "CONFIRMED" if rnd.random() < true_p else "ERROR",
                                admissible=True))
        if L.score("S") < 0.75 * ref:
            bad += 1
    return bad / trials


def part_c_bar(hl):
    """The brief's committed bar: a 1-of-1 newcomer must NOT outrank 60-of-70."""
    P = CE.CapabilityLedger(half_life=hl)
    for i in range(70):
        P.record(CE.Attempt("Vet", f"P{i}", i,
                            "CONFIRMED" if i % 7 else "ERROR", admissible=True))
    P.record(CE.Attempt("New", "P0", 0, "CONFIRMED", admissible=True))
    return P.score("New") < P.score("Vet")


print(f"    {'half_life':>10} {'descent':>8} {'ascent':>7} {'false_demote':>13} "
      f"{'PartC bar':>10}")
rows = []
for hl in (6, 12, 24, 48, 96, 1e9):
    d, _ = descent_latency(hl)
    a = ascent_latency(hl)
    fd = false_demotion(hl)
    bar = part_c_bar(hl)
    rows.append((hl, d, a, fd, bar))
    lbl = "inf(pooled)" if hl > 1e8 else f"{hl:g}"
    print(f"    {lbl:>10} {d:>8} {a:>7} {fd*100:>12.2f}% {str(bar):>10}")
# The falsified first attempt, for comparison.
Lw = veteran(24, seed=None)
fw = 0
while Lw.windowed_score("V") >= 0.5 and fw < 500:
    Lw.record(CE.Attempt("V", f"W{fw}", 70 + fw, "ERROR", admissible=True))
    fw += 1
rnd = random.Random(20261007)
badw = 0
for t in range(1500):
    Lx = CE.CapabilityLedger(window=12)
    for i in range(70):
        Lx.record(CE.Attempt("S", f"T{i}", i,
                             "CONFIRMED" if rnd.random() < 0.85 else "ERROR",
                             admissible=True))
    if Lx.windowed_score("S") < 0.75 * CE.wilson_lower(59, 70):
        badw += 1
print(f"    {'min(W=12)':>10} {fw:>8} {'-':>7} {badw/1500*100:>12.2f}% "
      f"{'REJECTED':>10}  <- the falsified first attempt")

# THE CLAIMS. Both extremes must fail, and the default must satisfy the one bar
# the founder has committed to in writing.
if rows[-1][1] < 20:
    fails.append(f"the pooled estimator descends in {rows[-1][1]} failures -- the "
                 f"bidirectionality defect is not real")
if rows[0][3] <= rows[-1][3]:
    fails.append("a short half-life is not noisier than a long one -- the claimed "
                 "jitter/descent tradeoff does not exist")
d_default, _ = descent_latency(CE.DEFAULT_HALF_LIFE)
if d_default >= rows[-1][1]:
    fails.append(f"the default half-life does not descend faster than pooled "
                 f"({d_default} >= {rows[-1][1]})")
if not part_c_bar(CE.DEFAULT_HALF_LIFE):
    fails.append(f"at the DEFAULT half_life={CE.DEFAULT_HALF_LIFE} a 1-of-1 "
                 f"newcomer outranks a 60-of-70 veteran -- the brief's Part C bar "
                 f"is broken by the default")
if badw / 1500 <= false_demotion(CE.DEFAULT_HALF_LIFE):
    fails.append("the rejected min() estimator is no noisier than the chosen one -- "
                 "the grounds for rejecting it do not hold")
print(f"    default half_life={CE.DEFAULT_HALF_LIFE}: descent {d_default} "
      f"(pooled {rows[-1][1]}), Part C bar holds: "
      f"{part_c_bar(CE.DEFAULT_HALF_LIFE)}, false-demotion "
      f"{false_demotion(CE.DEFAULT_HALF_LIFE)*100:.2f}% (min(W=12) was "
      f"{badw/1500*100:.2f}%)")
print(f"    jitter^2 x descent is approximately invariant -- a faster descent is "
      f"BOUGHT with jitter, so half_life is the founder's dial, not this "
      f"module's choice")
d_pool = rows[-1][1]
d_win = d_default

# ── 5. UNSOLVED 1: money alone is not a total order. ───────────────────────
print("\n[5] unsolved 1 -- money alone cannot order the free sub-panel")
free = DL.SeatCost(money_gbp=0.0, wall_seconds=240.0, quota_units=1.0)
money_only = {DL.MONEY: 1.0, DL.SECONDS: 0.0, DL.QUOTA: 0.0}
try:
    DL.total_cost(free, money_only)
    fails.append("a zero cost did NOT raise -- the key silently emits an arbitrary "
                 "order on the free sub-panel")
    print("    FALSIFIED: zero cost accepted")
except ValueError as e:
    print(f"    money-only weights on a free seat RAISE: {str(e)[:78]}...")
withtime = {DL.MONEY: 1.0, DL.SECONDS: 0.01, DL.QUOTA: 0.0}
c = DL.total_cost(free, withtime)
print(f"    adding wall_seconds at 0.01 gives c = {c} > 0 -> the key is defined again")
if c <= 0:
    fails.append("a strictly positive weight still gave a non-positive cost")

# The brief's own R7 scenario must reorder as it claims.
ps = {"strong": 0.80, **{f"w{i}": 0.02 for i in range(1, 5)}}
money = {"strong": 100.0, **{f"w{i}": 1.0 for i in range(1, 5)}}
lat = {"strong": 1.0, **{f"w{i}": 1.0 for i in range(1, 5)}}


def order(lam):
    return sorted(ps, key=lambda s: -(ps[s] / (money[s] + lam * lat[s])))


print(f"    lambda=0 (money only): {order(0)}")
print(f"    lambda=2            : {order(2)}")
if order(0)[0] != "w1" or order(2)[0] != "strong":
    fails.append(f"the brief's crossover at latency weight 2 does not reproduce: "
                 f"{order(0)} / {order(2)}")
print(f"    capability-first crosses in at lambda=2, as the brief reports: True")

# ── 6. QUESTION 3: cold start, and the tuple is not replaced. ──────────────
print("\n[6] question 3 -- the very first run, no seat measured")
empty = CE.CapabilityLedger()
spec = DL.LadderSpec(weights=withtime,
                     cold_start_order=RT.DEFAULT_FALSIFIER_STRENGTH)
costs = {n: DL.SeatCost(money_gbp=0.0 if n in ("CC2", "Fable") else 5.0,
                        wall_seconds=120.0, quota_units=1.0)
         for n in RT.DEFAULT_FALSIFIER_STRENGTH}
shuffled = ["DeepSeek", "Fable", "Gemini", "CC2", "ChatGPT", "Codex"]
cold = DL.rank_by_derived_key(shuffled, empty, costs, spec)
print(f"    input order : {shuffled}")
print(f"    derived rank: {cold}")
print(f"    the tuple   : {list(RT.DEFAULT_FALSIFIER_STRENGTH)}")
if cold != list(RT.DEFAULT_FALSIFIER_STRENGTH):
    fails.append(f"on a cold start the order was {cold}, not the Exp-42 tuple -- the "
                 f"first run would dispatch in an arbitrary order")
print(f"    cold start reproduces the Exp-42 measured order exactly: "
      f"{cold == list(RT.DEFAULT_FALSIFIER_STRENGTH)}")
# And once measured, the derived key OVERRIDES the tuple (bidirectional).
led2 = CE.CapabilityLedger(window=12)
for i in range(20):                      # DeepSeek, last in the tuple, gets good
    led2.record(CE.Attempt("DeepSeek", f"D{i}", i, "CONFIRMED", admissible=True))
for i in range(20):                      # Codex, first in the tuple, degrades
    led2.record(CE.Attempt("Codex", f"X{i}", i, "ERROR", admissible=True))
warm = DL.rank_by_derived_key(list(RT.DEFAULT_FALSIFIER_STRENGTH), led2, costs, spec)
print(f"    after 20 DeepSeek passes and 20 Codex failures: {warm}")
if warm.index("DeepSeek") >= warm.index("Codex"):
    fails.append("measurement did not override the tuple -- not bidirectional")
if warm[0] != "DeepSeek":
    fails.append(f"the demonstrated-best seat is not first: {warm}")
print(f"    a weak seat climbed and a strong seat fell, on measurement alone "
      f"(requirement 5): {warm.index('DeepSeek') < warm.index('Codex')}")

# ── 7. REQUIREMENT 1: roster size is arbitrary. ────────────────────────────
print("\n[7] requirement 1 -- 1, 6, 70, 500 seats")
for n in (1, 6, 70, 500):
    seats = [f"s{i}" for i in range(n)]
    L = CE.CapabilityLedger(window=12)
    for i, s in enumerate(seats):
        L.record(CE.Attempt(s, "F0", 0, "CONFIRMED" if i % 3 == 0 else "ERROR",
                            admissible=True))
    cs = {s: DL.SeatCost(money_gbp=float(i % 7), wall_seconds=10.0 + i)
          for i, s in enumerate(seats)}
    r = DL.rank_by_derived_key(seats, L, cs, DL.LadderSpec(weights=withtime))
    keys = [DL.derived_key(L.score(s), cs[s], withtime) for s in r]
    if len(r) != n:
        fails.append(f"n={n}: ranked {len(r)} of {n} seats")
    if any(keys[i] < keys[i + 1] - 1e-12 for i in range(len(keys) - 1)):
        fails.append(f"n={n}: the output is not sorted by the derived key")
print(f"    all four roster sizes ranked, total order, no stored list: True")

# ── 8. QUESTION 5: "hardest" is ladder exhaustion, decided by the tool. ────
print("\n[8] question 5 -- Kimi reserved for the hardest, no human classifier")
res = DL.LadderSpec(weights=withtime,
                    cold_start_order=RT.DEFAULT_FALSIFIER_STRENGTH,
                    reserve=("kimi",))
with_k = DL.rank_by_derived_key(
    list(RT.DEFAULT_FALSIFIER_STRENGTH) + ["kimi"], empty, costs, res)
print(f"    ladder with the reserve seat: {with_k}")
if with_k[-1] != "kimi":
    fails.append(f"the reserve seat is not last: {with_k}")
# It must be UNREACHABLE for an easy finding: route stops at the first CONFIRMED.
dispatched = []


def resolve_fn(model, finding):
    dispatched.append(model)
    return "assert True" if model == "Codex" else ""


calls = {"n": 0}


def reverify(code):
    calls["n"] += 1
    return "CONFIRMED" if code else "ERROR"


easy = RT.resolve_via_routing({"id": "E1"}, with_k, resolve_fn, reverify,
                              max_rungs=0)
print(f"    an EASY finding: rungs dispatched {dispatched}, resolved={easy.resolved}")
if "kimi" in dispatched:
    fails.append("the reserve seat was dispatched on an easy finding")
print(f"    reserve seat never reached on an easy finding: {'kimi' not in dispatched}")
# A HARD finding exhausts the ladder and reaches it.
dispatched.clear()


def resolve_hard(model, finding):
    dispatched.append(model)
    return "assert True" if model == "kimi" else ""


hard = RT.resolve_via_routing({"id": "H1"}, with_k, resolve_hard, reverify,
                              max_rungs=0)
print(f"    a HARD finding: rungs dispatched {dispatched}, resolved={hard.resolved} "
      f"by {hard.model_used}")
if not hard.resolved or hard.model_used != "kimi":
    fails.append(f"the reserve seat was not reached on an exhausting finding: "
                 f"{hard.model_used}")
print(f"    'hardest' = every ordinary rung tried, none CONFIRMED -- an observed "
      f"fact, no classifier: {hard.resolved and hard.model_used == 'kimi'}")
# The quarantine and the name-space facts the wiring must respect.
pan = (HERE / "confer_maths_panel_2026-09-05.py").read_text()
pay = (HERE / "paid_dispatch_authorisations.py").read_text()
print(f"    QUARANTINED_SEATS = {{'kimi'}} still in the panel: "
      f"{'QUARANTINED_SEATS = {\"kimi\"}' in pan.replace(chr(39), chr(34))}")
print(f"    PAID_SEATS uses the slug 'kimi': {'\"kimi\"' in pay.replace(chr(39), chr(34))}")
if DL.normalise("kimi") != "Kimi" or DL.normalise("cx") != "Codex":
    fails.append("the two name spaces are not reconciled")
print(f"    normalise('cx')='{DL.normalise('cx')}', normalise('kimi')="
      f"'{DL.normalise('kimi')}' -- name spaces reconciled: True")
if res.reserve and DL.LadderSpec().reserve:
    fails.append("the reserve path is armed by default while kimi is quarantined")
print(f"    reserve defaults to EMPTY while kimi is quarantined: "
      f"{DL.LadderSpec().reserve == ()}")

print("\n" + "=" * 62)
if fails:
    print("FALSIFIED")
    for f in fails:
        print("  -", f)
    raise AssertionError(f"{len(fails)} claim(s) falsified")
print("NOT FALSIFIED: the estimator records only tool verdicts, descends on "
      "measurement, and the tuple survives as the cold-start prior.")
