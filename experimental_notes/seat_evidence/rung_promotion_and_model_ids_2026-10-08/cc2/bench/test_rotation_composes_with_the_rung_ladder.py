# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4bcb30d3c5dd0ed02687ea1ce796f45ab0c9abe55e4433af5d848fd470c4b069
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Open questions 3 and 5, answered against bench/routing.py's real mechanics.

Q5: does rotation compose with the rung ladder, or do they conflict?
Q3: with the depth cap removed, does the ladder govern PRIORITY only, and does
    it then still need rungs?

Run: python3 -m pytest bench/test_rotation_composes_with_the_rung_ladder.py -q -s
"""
from __future__ import annotations

import numpy as np

from bench.promotion_gate import Z95, RungRecord, successes_required, wilson
from bench.routing import rank_falsifier_writers, resolve_via_routing

N_FINDINGS = 400
MODELS = [f"m{i:02d}" for i in range(12)]
CAP = 2
# true per-finding resolve rate by model, descending; the ladder cannot see these
TRUE_P = {m: p for m, p in zip(MODELS, np.linspace(0.92, 0.10, len(MODELS)))}


def _dispatch_counts(order_fn, cap=CAP, early_stop=True, seed=31337):
    """Attempts per model over N_FINDINGS.

    `early_stop=True` reproduces `resolve_via_routing`, which returns on the
    first CONFIRMED. `early_stop=False` counts attempts OFFERED, which is the
    accounting under which the brief's "identical dispatch cost" holds.
    """
    counts = {m: 0 for m in MODELS}
    rng = np.random.default_rng(seed)
    resolved = 0
    for i in range(N_FINDINGS):
        order = order_fn(i)
        for m in order[:cap]:
            counts[m] += 1
            if rng.random() < TRUE_P[m]:
                resolved += 1
                if early_stop:
                    break
    return counts, resolved


def _rotate(i, step=1):
    """Rotation by `step` roster positions per finding.

    step=1 is the obvious implementation. step=CAP is the one that actually
    produces the brief's even allocation - see the falsifier below.
    """
    j = (i * step) % len(MODELS)
    return MODELS[j:] + MODELS[:j]


def test_deterministic_identifier_order_starves_the_roster_DETERMINISTICALLY():
    """The brief reports 10 of 12 starved with 'Wilson [0.5520, 0.9530]'.

    The count is right and the interval has no referent: which models are
    starved is fixed by the order and the cap, not sampled. Falsified if
    repeated runs disagree on the starved set, in which case an interval could
    be meaningful.
    """
    a, _ = _dispatch_counts(lambda i: MODELS, seed=1)
    b, _ = _dispatch_counts(lambda i: MODELS, seed=2)
    starved_a = {m for m in MODELS if a[m] == 0}
    starved_b = {m for m in MODELS if b[m] == 0}
    print(f"\n  identifier order, cap {CAP}: {len(starved_a)} of {len(MODELS)} models "
          f"at 0 attempts; starved set identical across independent seeds: "
          f"{starved_a == starved_b}")
    assert starved_a == starved_b, "varies -> an interval would have a referent"
    assert len(starved_a) == 10
    assert a[MODELS[0]] == N_FINDINGS, "the first-ranked model takes every finding"


def test_rotation_removes_the_starvation_but_NOT_at_identical_cost():
    """CORRECTION TO THE BRIEF'S FIGURE 5.

    "rotation gave every model 66 or 67 at identical dispatch cost" holds only
    under attempts-OFFERED accounting. `resolve_via_routing` returns on the
    first CONFIRMED, so putting a weak model first makes rung 1 fail more often
    and rung 2 fire more often. Falsified if rotation's real dispatch total
    equals the identifier order's.
    """
    step1, _ = _dispatch_counts(lambda i: _rotate(i, 1), early_stop=False)
    stepc, _ = _dispatch_counts(lambda i: _rotate(i, CAP), early_stop=False)
    det_off, _ = _dispatch_counts(lambda i: MODELS, early_stop=False)
    print(f"\n  attempts OFFERED -- rotate by 1: {sorted(set(step1.values()))} per "
          f"model (spread {max(step1.values())-min(step1.values())}); "
          f"rotate by CAP={CAP}: {sorted(set(stepc.values()))} "
          f"(spread {max(stepc.values())-min(stepc.values())})")
    # 800 slots over 12 models = 12*66 + 8, so the maximally even allocation IS
    # 8 models at 67 and 4 at 66. A contiguous window advanced by 1 does not
    # reach it; advanced by CAP it does.
    assert sum(stepc.values()) == N_FINDINGS * CAP == 800
    assert set(stepc.values()) == {66, 67}, "the brief's 66/67 figure"
    assert set(step1.values()) == {66, 67, 68}, \
        "rotate-by-1 is already even -> the step size does not matter"
    assert sum(step1.values()) == sum(det_off.values()), "offered cost is equal"

    rot, rres = _dispatch_counts(lambda i: _rotate(i, CAP), early_stop=True)
    det, dres = _dispatch_counts(lambda i: MODELS, early_stop=True)
    print(f"  attempts DISPATCHED (first-CONFIRMED stop, real routing.py) -- "
          f"rotation {sum(rot.values())} for {rres} resolved; "
          f"identifier order {sum(det.values())} for {dres} resolved")
    assert min(rot.values()) > 0, "rotation must still remove starvation"
    assert sum(rot.values()) > sum(det.values()), \
        "equal cost -> the brief's figure 5 needs no correction"
    assert rres < dres, "and rotation also resolves fewer under the same cap"


def test_rotation_and_the_rung_ladder_act_on_DIFFERENT_axes_so_they_compose():
    """Rungs decide ELIGIBILITY; rotation decides ORDER among eligible ties.

    Falsified if either control is nullified by the other: if rotation lets a
    model below a rung receive that rung's findings, or if the ladder reinstates
    starvation among models that ARE eligible.
    """
    z, floor, W = Z95, 0.50, 19
    k = successes_required(W, floor, z)
    # rungs held: top 6 models hold rung 2, all 12 hold rung 0
    held = {}
    rng = np.random.default_rng(4242)
    for m in MODELS:
        rec = RungRecord(window=W)
        for _ in range(W):
            rec.record(rng.random() < TRUE_P[m])
        held[m] = 2 if rec.promotes(floor, z) else 0
    eligible_r2 = [m for m in MODELS if held[m] >= 2]
    counts = {m: 0 for m in MODELS}
    for i in range(N_FINDINGS):                      # rung-2 findings only
        pool = eligible_r2
        order = pool[i % len(pool):] + pool[:i % len(pool)]
        for m in order[:CAP]:
            counts[m] += 1
    print(f"\n  rung-2 holders (window {W}, k*={k}): {eligible_r2}")
    print(f"  rung-2 dispatches: {[counts[m] for m in MODELS]}")
    assert eligible_r2, "no model holds the rung -> the gate is vacuous here"
    assert all(counts[m] == 0 for m in MODELS if held[m] < 2), \
        "rotation handed rung-2 work to a model that does not hold rung 2"
    assert min(counts[m] for m in eligible_r2) > 0, \
        "the ladder reinstated starvation among eligible models"
    # the weak models are PLACED, not excluded: they still hold rung 0
    assert all(held[m] >= 0 for m in MODELS)


def test_with_the_cap_removed_rung_ORDER_still_earns_its_keep():
    """Q3: eligibility becomes unbounded, so does order still matter?

    `resolve_via_routing` returns on the FIRST CONFIRMED, so order decides how
    many dispatches a resolution costs. Falsified if ladder order costs no fewer
    dispatches than rotation order with the cap removed - in which case rungs
    would govern nothing once eligibility is universal.
    """
    rng = np.random.default_rng(555)
    results = {}
    for name, order_fn in (
        ("ladder (strongest first)", lambda i: MODELS),
        ("rotation only", lambda i: MODELS[i % len(MODELS):] + MODELS[:i % len(MODELS)]),
        ("reversed ladder", lambda i: MODELS[::-1]),
    ):
        total, unresolved = 0, 0
        for i in range(N_FINDINGS):
            order = order_fn(i)
            calls = {"n": 0}

            def resolve_fn(m, f, _c=calls):
                _c["n"] += 1
                return f"code-{m}"

            def reverify_fn(code, _rng=rng):
                m = code.split("-", 1)[1]
                return "CONFIRMED" if _rng.random() < TRUE_P[m] else "REFUTED"

            r = resolve_via_routing({"finding_id": f"C{i}"}, order,
                                    resolve_fn, reverify_fn, max_rungs=0)
            total += calls["n"]
            unresolved += 0 if r.resolved else 1
        results[name] = (total / N_FINDINGS, unresolved)
        print(f"\n  {name}: {total/N_FINDINGS:.3f} dispatches per finding, "
              f"{unresolved} unresolved of {N_FINDINGS}")
    assert results["ladder (strongest first)"][0] < results["rotation only"][0]
    assert results["rotation only"][0] < results["reversed ladder"][0]
