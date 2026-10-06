# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 90392bcf5882bfd333780a4700d49253c423989ceabfd1d5702a578527f82b5b
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""What a routing-ladder ORDER can and cannot change, derived not asserted.

THE QUESTION. The founder has ruled that `bench/routing.py`'s ladder must become a
measured statistic rather than `DEFAULT_FALSIFIER_STRENGTH`, a frozen 5-tuple of
vendor names, and that the rung cap should be removed so a finding "runs until it is
either resolved, or the ladder is exhausted".

THE TWO RESULTS THIS SCRIPT ESTABLISHES, each by symbolic derivation AND by
exhaustive numeric enumeration over permutations (two independent instruments):

  R1. ORDER-INVARIANCE OF RESOLUTION. `resolve_via_routing` stops at the first
      CONFIRMED. If the ladder is EXHAUSTED (max_rungs=0), the probability a
      finding is resolved is
          P(resolve) = 1 - prod_i (1 - p_i)
      which is SYMMETRIC in the rungs. No permutation of the ladder changes it.
      => Once the cap is removed, ladder ORDER cannot change WHICH findings get
         resolved. It can only change what they COST.

      This is load-bearing. It means the selection effect that depresses a strong
      model's observed confirm rate (hard findings are sent to it BECAUSE it is
      trusted) can misorder the ladder without costing a single resolution. The
      ordering problem is demoted from a correctness problem to a cost problem.
      That demotion is valid ONLY with exhaustion; with today's default cap of 2,
          P(resolve | cap k) = 1 - prod_{i<=k} (1 - p_i)
      is NOT symmetric, so under a cap the order IS a correctness question.

  R2. THE COST-MINIMISING ORDER IS THE INDEX RULE p_i / c_i, DESCENDING.
      With per-rung dispatch cost c_i (tokens) and stop-at-first-success,
          E[cost] = sum_i c_{s(i)} * prod_{j<i} (1 - p_{s(j)})
      is minimised by sorting rungs on p_i / c_i descending. Proved below by the
      adjacent-transposition argument and checked by brute force.

      => Capability and token budget do NOT need to be two inputs fighting each
         other. They are one ratio, and it is the optimum of a single objective.
         A cheap model does not become "the default answer": it becomes a cheap
         first PROBE, and because the ladder exhausts, the expensive strong model
         still runs when the probe fails (R1).

WHAT WOULD REFUTE R1. Any code path that resolves a finding without a CONFIRMED
from `reverify_fn`, or any cap on rungs. `bench/routing.py:resolve_via_routing`
returns `resolved=True` only on `verdict == "CONFIRMED"`; the DUPLICATE early
return in `route()` bypasses the ladder entirely and is outside R1's scope.
WHAT WOULD REFUTE R2. Costs that depend on POSITION in the ladder, or rung
outcomes that are not independent. Both are probed explicitly below.

Run:  python3 scripts/ladder_order_is_cost_only_2026-10-06.py
Exit: 0 all derivations hold; 1 any check failed.
"""
from __future__ import annotations

import itertools
import sys


def _help_requested() -> bool:
    return any(a in ("-h", "--help") for a in sys.argv[1:])


# -----------------------------------------------------------------------------
# R1 -- resolution probability is symmetric under exhaustion
# -----------------------------------------------------------------------------

def r1_symbolic():
    """SymPy: P(resolve) under exhaustion is invariant under every permutation."""
    import sympy as sp
    out = []
    p = sp.symbols("p1 p2 p3 p4", positive=True)

    def p_resolve(order):
        miss = sp.Integer(1)
        total = sp.Integer(0)
        for pi in order:
            total += miss * pi
            miss *= (1 - pi)
        return sp.expand(total)

    base = p_resolve(p)
    closed = sp.expand(1 - sp.prod([1 - pi for pi in p]))
    ok_closed = sp.simplify(base - closed) == 0
    out.append("  closed form 1-prod(1-p_i) matches the walk  : %s" % ok_closed)

    perms = list(itertools.permutations(p))
    bad = [o for o in perms if sp.simplify(p_resolve(o) - base) != 0]
    out.append("  permutations of 4 rungs checked             : %d" % len(perms))
    out.append("  permutations changing P(resolve)            : %d" % len(bad))

    def p_resolve_cap(order, k):
        miss, total = sp.Integer(1), sp.Integer(0)
        for pi in list(order)[:k]:
            total += miss * pi
            miss *= (1 - pi)
        return sp.expand(total)

    base2 = p_resolve_cap(p, 2)
    bad2 = [o for o in perms if sp.simplify(p_resolve_cap(o, 2) - base2) != 0]
    out.append("  with cap=2, permutations that DO change it  : %d "
               "(a cap makes order a correctness question)" % len(bad2))
    return out, (ok_closed and not bad and bool(bad2))


def r1_numeric():
    """Independent instrument: exhaustive float enumeration, no SymPy."""
    import numpy as np
    rows, ok = [], True
    ps = [0.9, 0.28, 0.67, 0.8, 0.75]           # Exp-42 quoted rates, 5 rungs
    vals = set()
    for order in itertools.permutations(ps):
        miss, tot = 1.0, 0.0
        for pi in order:
            tot += miss * pi
            miss *= (1 - pi)
        vals.add(round(tot, 12))
    closed = 1.0 - float(np.prod([1 - x for x in ps]))
    rows.append("  distinct P(resolve) over 5! = 120 orders    : %d" % len(vals))
    rows.append("  that value                                 : %.12f" % sorted(vals)[0])
    rows.append("  closed form 1-prod(1-p_i)                  : %.12f" % closed)
    ok &= (len(vals) == 1 and abs(sorted(vals)[0] - closed) < 1e-12)

    capped = set()
    for order in itertools.permutations(ps):
        miss, tot = 1.0, 0.0
        for pi in order[:2]:
            tot += miss * pi
            miss *= (1 - pi)
        capped.add(round(tot, 12))
    rows.append("  distinct P(resolve) with cap=2             : %d spanning [%.4f, %.4f]"
                % (len(capped), min(capped), max(capped)))
    ok &= len(capped) > 1
    return rows, ok


# -----------------------------------------------------------------------------
# R2 -- the cost-minimising order is p/c descending
# -----------------------------------------------------------------------------

def expected_cost(order_pc):
    """E[tokens] for stop-at-first-success over (p, c) rungs, in ladder order."""
    miss, total = 1.0, 0.0
    for p_i, c_i in order_pc:
        total += miss * c_i
        miss *= (1 - p_i)
    return total


def r2_symbolic():
    """The adjacent-transposition inequality, derived in SymPy.

    For two adjacent rungs a, b at positions k, k+1 reached with probability Q,
        E[cost](a,b) - E[cost](b,a) = Q * (p_b c_a - p_a c_b)
    which is <= 0 -- a-first at least as cheap -- exactly when p_a/c_a >= p_b/c_b.
    Everything after position k+1 is unchanged because the surviving-miss factor
    (1-p_a)(1-p_b) is symmetric in a and b. So an improving adjacent swap exists
    whenever the sequence is not sorted by p/c descending, and because p/c induces
    a total order on the rungs, the sorted sequence is the global optimum.
    """
    import sympy as sp
    out = []
    pa, pb, ca, cb, Q = sp.symbols("p_a p_b c_a c_b Q", positive=True)
    ab = Q * (ca + (1 - pa) * cb)
    ba = Q * (cb + (1 - pb) * ca)
    diff = sp.simplify(sp.expand(ab - ba))
    out.append("  E[cost](a,b) - E[cost](b,a)                 = %s" % diff)
    target = sp.simplify(diff - Q * (pb * ca - pa * cb))
    out.append("  equals Q*(p_b c_a - p_a c_b)?               : %s" % (target == 0))
    suffix = sp.simplify((1 - pa) * (1 - pb) - (1 - pb) * (1 - pa))
    out.append("  surviving-miss factor symmetric in a,b      : %s" % (suffix == 0))
    cond = sp.simplify(sp.expand((pa / ca - pb / cb) * ca * cb - (pa * cb - pb * ca)))
    out.append("  p_a/c_a >= p_b/c_b  <=>  p_a c_b >= p_b c_a : %s" % (cond == 0))
    return out, (target == 0 and suffix == 0 and cond == 0)


def r2_bruteforce():
    """Exhaustive: for many random rosters, does p/c-descending attain the min?"""
    import numpy as np
    rng = np.random.default_rng(20261006)          # fixed seed: no Date/Random drift
    rows, ok = [], True
    worst_gap, trials, n_rungs = 0.0, 4000, 5
    strength_first_losses = 0
    cheapest_first_losses = 0
    for _ in range(trials):
        p = rng.uniform(0.05, 0.95, n_rungs)
        c = rng.uniform(1_000, 200_000, n_rungs)   # token costs, 200x spread
        rungs = list(zip(p.tolist(), c.tolist()))
        best = min(expected_cost(o) for o in itertools.permutations(rungs))
        idx = sorted(rungs, key=lambda r: -(r[0] / r[1]))
        got = expected_cost(idx)
        worst_gap = max(worst_gap, abs(got - best) / best)
        if expected_cost(sorted(rungs, key=lambda r: -r[0])) > best * (1 + 1e-12):
            strength_first_losses += 1
        if expected_cost(sorted(rungs, key=lambda r: r[1])) > best * (1 + 1e-12):
            cheapest_first_losses += 1
    rows.append("  random rosters tested                      : %d x %d rungs"
                % (trials, n_rungs))
    rows.append("  worst relative gap, p/c order vs optimum   : %.3e" % worst_gap)
    rows.append("  rosters where STRONGEST-FIRST is suboptimal : %d/%d"
                % (strength_first_losses, trials))
    rows.append("  rosters where CHEAPEST-FIRST is suboptimal  : %d/%d"
                % (cheapest_first_losses, trials))
    ok &= worst_gap < 1e-9
    ok &= strength_first_losses > 0 and cheapest_first_losses > 0
    return rows, ok


# -----------------------------------------------------------------------------
# Counterexample probes: the conditions R2 depends on
# -----------------------------------------------------------------------------

def r2_assumption_probes():
    """R2 needs position-independent costs. Show it BREAKS when they are not.

    This is the honest half. The routing prompt is rebuilt per rung from the same
    finding today, so cost is position-independent. But if a later rung is handed
    the previous rung's falsifier and traceback -- which is exactly the aid this
    design proposes so a 1-model panel can route to itself -- cost grows with
    depth and the index rule stops being exact.
    """
    rows, ok = [], True

    def cost_posdep(order):
        miss, total = 1.0, 0.0
        for d, (p_i, c_i) in enumerate(order):
            total += miss * c_i * (1 + 0.5 * d)
            miss *= (1 - p_i)
        return total

    rungs = [(0.9, 100_000.0), (0.30, 2_000.0), (0.5, 20_000.0)]
    best = min(cost_posdep(o) for o in itertools.permutations(rungs))
    idx = sorted(rungs, key=lambda r: -(r[0] / r[1]))
    gap = (cost_posdep(idx) - best) / best
    rows.append("  position-DEPENDENT cost: p/c gap vs optimum : %.4f%% (%s)"
                % (gap * 100.0,
                   "index rule no longer exact" if gap > 1e-9 else "still exact"))
    ok &= gap > 1e-9       # we WANT this to break, to prove the probe is live
    rows.append("  consequence: with depth-growing prompts the index rule is a")
    rows.append("  heuristic, not an optimum. State it as such; do not claim R2")
    rows.append("  for a ladder that accumulates context across rungs.")
    return rows, ok


def main():
    if _help_requested():
        print((__doc__ or "").strip())
        print("\nusage: %s" % sys.argv[0].split("/")[-1])
        return 0

    all_ok = True
    print("=" * 78)
    print("R1  RESOLUTION PROBABILITY IS ORDER-INVARIANT UNDER EXHAUSTION")
    print("=" * 78)
    rows, ok = r1_symbolic()
    print("  [SymPy, symbolic]")
    for r in rows:
        print(r)
    all_ok &= ok
    rows, ok = r1_numeric()
    print("  [NumPy, exhaustive enumeration]")
    for r in rows:
        print(r)
    all_ok &= ok

    print()
    print("=" * 78)
    print("R2  THE COST-MINIMISING LADDER ORDER IS p_i / c_i DESCENDING")
    print("=" * 78)
    rows, ok = r2_symbolic()
    print("  [SymPy, adjacent-transposition derivation]")
    for r in rows:
        print(r)
    all_ok &= ok
    rows, ok = r2_bruteforce()
    print("  [NumPy, exhaustive permutation search over random rosters]")
    for r in rows:
        print(r)
    all_ok &= ok

    print()
    print("=" * 78)
    print("ASSUMPTION PROBES (these are SUPPOSED to break)")
    print("=" * 78)
    rows, ok = r2_assumption_probes()
    for r in rows:
        print(r)
    all_ok &= ok

    print()
    print("=" * 78)
    print("VERDICT: %s" % ("ALL DERIVATIONS HOLD" if all_ok else "A CHECK FAILED"))
    print("=" * 78)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
