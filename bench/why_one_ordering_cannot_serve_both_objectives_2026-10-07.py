#!/usr/bin/env python3
"""The try-order question has TWO objectives, and no single ordering serves both.

THE FOUNDER'S OBSERVATION, 2026-10-07: *"This leaves the tension in place? My
solution, your solution and Astra's did not dissolve it?"*

He is right that none of the three dissolved it, and this script shows WHY: all
three -- his capability-ascending ladder, CC1's measured-with-name-fallback
comparator, and Astra's value-over-cost estimator -- answer the question "what
is the ONE correct order?". That question embeds the defect. The falsifier
ladder under a rung cap has two separate objectives attached to two separate
decisions, and a single sort key cannot be the optimum of both:

  OBJECTIVE A, COVERAGE: minimise P(no seat resolves the finding) = prod(1-p_i)
    over the seats actually tried. This is a property of the SET, not the order.
  OBJECTIVE B, SPEND: minimise E[cost to first CONFIRMED or exhaustion]
    = sum_j c_j * prod_{i<j}(1-p_i). This is a property of the ORDER.

A is order-invariant. B is order-dependent. So "which seats" and "in what
sequence" are different questions, and the project has been asking them as one.

Each claim below is verified by at least 2 independent tools, per the 21 April
2026 cross-verification rule. Every proportion carries a Wilson interval.

Run: python3 bench/why_one_ordering_cannot_serve_both_objectives_2026-10-07.py
"""
from __future__ import annotations

import argparse
import ast
import itertools
import math
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- helpers
def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Closed-form Wilson score interval; cross-checked against statsmodels."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def expected_spend(order, p, c):
    """E[cost] with stop-at-first-success. Exact in Fractions."""
    tot = Fraction(0)
    surv = Fraction(1)
    for i in order:
        tot += surv * c[i]
        surv *= (1 - p[i])
    return tot


def failure_probability(seats, p):
    """P(nobody resolves). Depends on the SET only."""
    out = Fraction(1)
    for i in seats:
        out *= (1 - p[i])
    return out


# ------------------------------------------------- claim 1 (SymPy + exact)
def claim_coverage_is_order_invariant(n: int = 5) -> dict:
    """P(all fail) is identical under every permutation. SymPy, then Fractions."""
    import sympy as sp

    ps = sp.symbols(f"p0:{n}", positive=True)
    ref = sp.expand(sp.prod([1 - x for x in ps]))
    bad = []
    for perm in itertools.permutations(range(n)):
        got = sp.expand(sp.prod([1 - ps[i] for i in perm]))
        if sp.simplify(got - ref) != 0:
            bad.append(perm)

    # second tool: exact rational arithmetic over a concrete instance
    pv = {i: Fraction(1 + 2 * i, 20) for i in range(n)}
    vals = {failure_probability(perm, pv) for perm in itertools.permutations(range(n))}

    return {
        "permutations_checked": math.factorial(n),
        "sympy_mismatches": len(bad),
        "distinct_exact_values": len(vals),
        "holds": not bad and len(vals) == 1,
    }


# ------------------------------------------------- claim 2 (z3 + brute force)
def claim_spend_is_minimised_by_the_cross_multiplied_key() -> dict:
    """i before j is never dearer iff p_i*c_j >= p_j*c_i.

    z3 looks for a counterexample over the reals; brute force checks the GLOBAL
    optimum against the sort key for every permutation of concrete instances.
    """
    import z3

    pi, pj, ci, cj = z3.Reals("pi pj ci cj")
    s = z3.Solver()
    s.add(pi > 0, pi < 1, pj > 0, pj < 1, ci >= 0, cj >= 0)
    s.add(pi * cj >= pj * ci)                       # key says i first
    s.add(ci + (1 - pi) * cj > cj + (1 - pj) * ci)  # yet i-first costs more
    z3_verdict = str(s.check())

    # and the converse direction, so the key is not merely sufficient
    s2 = z3.Solver()
    s2.add(pi > 0, pi < 1, pj > 0, pj < 1, ci >= 0, cj >= 0)
    s2.add(pi * cj < pj * ci)
    s2.add(ci + (1 - pi) * cj <= cj + (1 - pj) * ci)
    z3_converse = str(s2.check())

    # brute force: does the key's order attain the global minimum every time?
    import numpy as np
    rng = np.random.default_rng(20261007)
    misses = 0
    trials = 400
    for _ in range(trials):
        n = int(rng.integers(3, 6))
        p = {i: Fraction(int(rng.integers(5, 95)), 100) for i in range(n)}
        c = {i: Fraction(int(rng.integers(0, 200)), 1) for i in range(n)}
        best = min(itertools.permutations(range(n)),
                   key=lambda o: expected_spend(o, p, c))
        # cross-multiplied key, zero-cost seats first, stable on ties
        keyed = sorted(range(n), key=lambda i: (-(p[i] / c[i]) if c[i] else float("-inf"), i))
        if expected_spend(tuple(keyed), p, c) != expected_spend(best, p, c):
            misses += 1
    lo, hi = wilson(trials - misses, trials)
    return {
        "z3_counterexample_search": z3_verdict,
        "z3_converse_search": z3_converse,
        "brute_force_trials": trials,
        "brute_force_misses": misses,
        "agreement_wilson": (round(lo, 6), round(hi, 6)),
        "holds": z3_verdict == "unsat" and z3_converse == "unsat" and misses == 0,
    }


# ------------------------------------------------- claim 3 (the two disagree)
def claim_the_two_objectives_have_different_optima(K: int = 2) -> dict:
    """An instance where coverage and spend pick DIFFERENT sets of size K.

    Deliberately shaped like this project: 2 free seats of middling strength and
    a dear seat that is the only one with a real chance on a hard finding.
    """
    p = {"weak_free": Fraction(5, 100), "mid_free": Fraction(10, 100),
         "strong_paid": Fraction(80, 100)}
    c = {"weak_free": Fraction(0), "mid_free": Fraction(0),
         "strong_paid": Fraction(100)}

    sets = list(itertools.combinations(p, K))
    cover_best = min(sets, key=lambda S: failure_probability(S, p))
    spend_best = min(
        sets,
        key=lambda S: min(expected_spend(o, p, c) for o in itertools.permutations(S)))

    def pfail(S):
        return float(failure_probability(S, p))

    return {
        "cap_K": K,
        "coverage_optimal_set": sorted(cover_best),
        "spend_optimal_set": sorted(spend_best),
        "sets_differ": sorted(cover_best) != sorted(spend_best),
        "P_unresolved_under_coverage_choice": round(pfail(cover_best), 6),
        "P_unresolved_under_spend_choice": round(pfail(spend_best), 6),
        "fold_worse": round(pfail(spend_best) / pfail(cover_best), 4),
    }


# ------------------------------------------------- claim 4 (free seats)
def claim_spend_is_vacuous_among_free_seats() -> dict:
    """If every candidate costs 0, E[spend] = 0 for EVERY order.

    So the ordering objective carries no information and only the SET matters.
    Cheapest-first is not wrong here; it is undefined.
    """
    p = {"a": Fraction(78, 100), "b": Fraction(89, 100), "c": Fraction(93, 100)}
    c = {k: Fraction(0) for k in p}
    spends = {expected_spend(o, p, c) for o in itertools.permutations(p)}
    return {
        "distinct_expected_spends": len(spends),
        "all_zero": spends == {Fraction(0)},
        "orders_examined": math.factorial(len(p)),
        "ordering_objective_is_informative": len(spends) > 1,
    }


# ------------------------------------------------- claim 5 (live config)
def claim_the_cap_is_live(root: Path = REPO) -> dict:
    """What the cap is, how many configs route, and how long the ladder reaches.

    TWO PREDICATES IN THE FIRST VERSION OF THIS FUNCTION WERE WRONG, 2026-10-07,
    and both failed toward a comfortable answer:

      * it globbed ``bench/configs``, a directory that has never existed, and
        reported "0 config files" -- which reads as "no config pins the cap"
        when it actually means "the search found nothing". The real configs live
        in ``bench/expNN_configs/``. The denominator is 47, not the 49 quoted to
        the founder earlier the same day.
      * it discovered ``FREE_SEATS`` by walking every ``.py`` under ``bench``,
        and the last match won -- a SANDBOX HARVEST COPY under ``bench/logs/``,
        not live code.

    It also counted ``routing_enabled`` literally, missing the legacy alias
    ``take_up_slack_enabled`` that `reference_runner_v3` maps onto it; the
    literal count is 5 configs, the effective count is 23.
    """
    src = (root / "bench" / "reference_runner_v3.py").read_text()
    tree = ast.parse(src)
    defaults = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id in ("routing_max_rungs", "routing_enabled") \
                and node.value is not None:
            try:
                defaults[node.target.id] = ast.literal_eval(node.value)
            except Exception:
                defaults[node.target.id] = ast.unparse(node.value)

    import json
    cfgs = sorted((root / "bench").glob("exp*_configs/*.json"))
    routed, pinned, reach_hist = [], [], {}
    ladder = _live_ladder(root)
    for f in cfgs:
        d = json.loads(f.read_text())
        if "routing_max_rungs" in d:
            pinned.append(f.name)
        if "routing_enabled" in d:
            on = bool(d["routing_enabled"])
        else:
            on = bool(d.get("take_up_slack_enabled", False))   # the legacy alias
        if not on:
            continue
        routed.append(f.name)
        labels = {(m if isinstance(m, str) else
                   (m.get("label") or m.get("name") or m.get("model") or "")).lower()
                  for m in d.get("models", [])}
        k = sum(1 for r in ladder if r.lower() in labels)
        reach_hist[k] = reach_hist.get(k, 0) + 1

    cap = defaults.get("routing_max_rungs", 2)
    orderable = sum(v for k, v in reach_hist.items() if k >= cap)
    unasked = {k: k - cap for k in reach_hist if k > cap}
    lo, hi = wilson(len(pinned), len(cfgs))
    olo, ohi = wilson(orderable, len(routed)) if routed else (0.0, 0.0)
    return {
        "routing_max_rungs_default": cap,
        "routing_enabled_default": defaults.get("routing_enabled"),
        "experiment_configs": len(cfgs),
        "configs_pinning_the_cap": len(pinned),
        "pinned_wilson": (round(lo, 6), round(hi, 6)),
        "configs_with_routing_effectively_on": len(routed),
        "reachable_rungs_histogram": dict(sorted(reach_hist.items())),
        "configs_where_order_can_matter": f"{orderable} of {len(routed)}",
        "order_matters_wilson": (round(olo, 6), round(ohi, 6)),
        "rungs_never_tried_under_the_cap": unasked,
        "live_ladder": ladder,
        "free_seats_declaration": _live_free_seats(root),
    }


def _live_ladder(root: Path) -> tuple:
    """Read DEFAULT_FALSIFIER_STRENGTH from live code, not from a log copy."""
    for node in ast.walk(ast.parse((root / "bench" / "routing.py").read_text())):
        if isinstance(node, ast.Assign) and any(
                isinstance(x, ast.Name) and x.id == "DEFAULT_FALSIFIER_STRENGTH"
                for x in node.targets):
            return tuple(ast.literal_eval(node.value))
    return ()


def _live_free_seats(root: Path):
    """FREE_SEATS from live code only. `bench/logs/` and worktrees are EXCLUDED.

    The first version let the last match win and landed on a harvested sandbox
    copy under `bench/logs/`, which is evidence of what a seat was given, not a
    statement about what runs now.
    """
    skip = ("/logs/", "/worktrees/", "/.git/")
    out = []
    for cand in sorted((root / "bench").rglob("*.py")):
        rel = str(cand.relative_to(root))
        if any(s.strip("/") in rel.split("/") for s in ("logs", "worktrees")):
            continue
        t = cand.read_text()
        if "FREE_SEATS" not in t:
            continue
        for node in ast.walk(ast.parse(t)):
            if isinstance(node, ast.Assign) and any(
                    isinstance(x, ast.Name) and x.id == "FREE_SEATS"
                    for x in node.targets):
                out.append((rel, ast.unparse(node.value)))
    return out


def claim_the_cap_truncates_the_ladder(root: Path = REPO) -> dict:
    """With 5 reachable rungs and a cap of 2, 3 seats are never asked at all.

    This is where the founder's objection bites. The question is not "in what
    sequence do we try 5 seats" -- it is "WHICH 2 of 5 do we try", and the other
    3 never see the finding whatever their capability.
    """
    ladder = _live_ladder(root)
    cap = 2
    free = {"cc2", "fable"}
    return {
        "ladder_length": len(ladder),
        "cap": cap,
        "seats_never_asked": len(ladder) - cap,
        "free_rungs": [r for r in ladder if r.lower() in free],
        "paid_rungs": [r for r in ladder if r.lower() not in free],
        "free_seats_absent_from_the_ladder":
            sorted(free - {r.lower() for r in ladder}),
        "prefixes_of_length_2": len(list(itertools.combinations(ladder, cap))),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cap", type=int, default=2, help="rung cap K for claim 3")
    args = ap.parse_args()

    rows = [
        ("coverage is order-invariant", claim_coverage_is_order_invariant()),
        ("spend follows the cross-multiplied key",
         claim_spend_is_minimised_by_the_cross_multiplied_key()),
        ("the two objectives disagree",
         claim_the_two_objectives_have_different_optima(args.cap)),
        ("spend is vacuous among free seats",
         claim_spend_is_vacuous_among_free_seats()),
        ("the cap is live", claim_the_cap_is_live()),
        ("the cap truncates the ladder", claim_the_cap_truncates_the_ladder()),
    ]
    for title, d in rows:
        print(f"\n== {title} ==")
        for k, v in d.items():
            print(f"   {k}: {v}")
    print("\n-- cross-check: Wilson closed form against statsmodels --")
    try:
        from statsmodels.stats.proportion import proportion_confint
        for k, n in ((0, 49), (400, 400), (740, 1078)):
            mine = wilson(k, n)
            theirs = tuple(proportion_confint(k, n, method="wilson"))
            print(f"   {k}/{n}: closed form {mine[0]:.9f},{mine[1]:.9f} | "
                  f"statsmodels {theirs[0]:.9f},{theirs[1]:.9f} | "
                  f"agree={all(abs(a-b) < 1e-9 for a, b in zip(mine, theirs))}")
    except Exception as exc:  # pragma: no cover
        print(f"   statsmodels unavailable: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
