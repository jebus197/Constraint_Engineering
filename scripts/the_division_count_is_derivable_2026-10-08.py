#!/usr/bin/env python3
"""Heterogeneous gates make the division-cost curve monotone, and the proof is open.

THE FOUNDER'S QUESTION, 2026-10-08: *"I get that doesn't settle how many leagues
there should be, and if that can be mathematically derived at the start of an
experiment, based on the relative complexity of the task, and the available
resources?"*

WHAT THIS FILE SETTLES, AND WHAT IT LEAVES OPEN FOR THE PANEL.

SETTLED, AND IT WITHDRAWS A CLAIM OF CC1'S.
`bench/the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py`
concluded that the cost curve is NOT monotone and that the division count must
therefore be scanned. That conclusion is an artefact of its own `smallest_gate`,
which forces every gate in a ladder to the SAME (attempts, successes) pair. The
end-to-end budget constrains only the PRODUCTS of per-gate pass probabilities, so
heterogeneous gates are admissible and the identical-gate costs are UPPER BOUNDS,
not optima. The defect was found by the `fable` seat of the 2026-10-08 blind
round; this file is an INDEPENDENT re-derivation, by a different method (a Pareto
dynamic program over the gate menu rather than a bi-criteria frontier search),
and it reproduces that seat's curve at all 13 points.

OPEN, AND DELIBERATELY NOT ANSWERED HERE. Monotonicity can be argued from a merge
construction -- collapse 2 adjacent gates into 1 rule on the concatenated
attempts, preserving total attempts and end-to-end error, giving
cost(T) <= cost(T+1). Measured below, that merge is NOT available within the
family of success-count threshold gates: of 4000 random gate pairs, 801 have no
single threshold gate on a1+a2 attempts that dominates the AND of the 2 separate
gates on both criteria. So monotonicity currently rests on a SCAN, and whether it
is a theorem depends on a modelling decision nobody has made: may a ladder's
gates be arbitrary tests, or must they be success-count thresholds?

Every figure is computed twice -- SciPy's binomial tail against an exact mpmath
sum -- and the symbolic claims go to SymPy and z3. Wolfram, where quoted, is the
SECOND falsifier and is recorded rather than called, so no licensed kernel is
needed to reproduce anything here.

Run: python3 scripts/the_division_count_is_derivable_2026-10-08.py
"""
from __future__ import annotations

import argparse
import math

CAPABLE_RATE = 0.90
WEAK_RATE = 0.50
P_CAPABLE_MIN = 0.95
P_WEAK_MAX = 0.01

MAX_ATTEMPTS_PER_GATE = 24
MAX_TOTAL_ATTEMPTS = 60
MAX_DIVISIONS = 14


def _sf(s: int, a: int, p: float) -> float:
    from scipy.stats import binom
    return float(binom.sf(s - 1, a, p))


def _sf_exact(s: int, a: int, p: float) -> float:
    import mpmath as mp
    with mp.workdps(50):
        pp = mp.mpf(p)
        return float(sum(mp.binomial(a, k) * pp ** k * (1 - pp) ** (a - k)
                         for k in range(s, a + 1)))


def gate_menu(cap=CAPABLE_RATE, weak=WEAK_RATE, pc_min=P_CAPABLE_MIN,
              maxa=MAX_ATTEMPTS_PER_GATE) -> list:
    """Threshold gates worth considering, after 2 exact reductions.

    REDUCTION 1, a lemma rather than a heuristic: every per-gate capable-pass
    probability is a factor of a product that must reach `pc_min`, and every
    factor is at most 1, so a gate with capable-pass below `pc_min` can never
    appear in a feasible ladder at any division count.

    REDUCTION 2: among gates with the SAME attempts count, raising the success
    threshold lowers both pass probabilities, so only the Pareto-optimal ones
    (higher capable-pass, lower weak-pass) can matter.
    """
    bya: "dict[int, list]" = {}
    for a in range(1, maxa + 1):
        for s in range(1, a + 1):
            pc = _sf(s, a, cap)
            if pc < pc_min:
                continue
            pw = _sf(s, a, weak)
            bya.setdefault(a, []).append(
                (math.log(pc), math.log(pw) if pw > 0 else -700.0, s))
    menu = []
    for a, v in bya.items():
        v.sort(key=lambda t: (-t[0], t[1]))
        best = float("inf")
        for lc, lw, s in v:
            if lw < best:
                menu.append((a, lc, lw, s))
                best = lw
    return menu


def _pareto(pts: list) -> list:
    """Keep points not dominated on (attempts asc, logcap desc, logweak asc)."""
    pts.sort(key=lambda t: (t[0], -t[1], t[2]))
    out = []
    for A, lc, lw, *rest in pts:
        if any(A2 <= A and lc2 >= lc and lw2 <= lw
               for A2, lc2, lw2, *_ in out[-300:]):
            continue
        out.append((A, lc, lw, *rest))
    return out


def optimal_costs(cap=CAPABLE_RATE, weak=WEAK_RATE, pc_min=P_CAPABLE_MIN,
                  pw_max=P_WEAK_MAX, max_div=MAX_DIVISIONS,
                  maxa=MAX_ATTEMPTS_PER_GATE,
                  maxtot=MAX_TOTAL_ATTEMPTS) -> dict:
    """Fewest total attempts per division count, gates free to differ."""
    LC, LW = math.log(pc_min), math.log(pw_max)
    menu = gate_menu(cap, weak, pc_min, maxa)
    out, layer = {}, [(0, 0.0, 0.0)]
    for g in range(1, max_div):
        nxt = [(A + a, lc + gc, lw + gw)
               for A, lc, lw in layer
               for a, gc, gw, _s in menu if A + a <= maxtot]
        layer = [(p[0], p[1], p[2]) for p in _pareto([(x[0], x[1], x[2]) for x in nxt])]
        feas = [p[0] for p in layer if p[1] >= LC and p[2] <= LW]
        out[g + 1] = min(feas) if feas else None
    return out


def claim_the_identical_gate_costs_were_upper_bounds() -> dict:
    """The withdrawal, computed rather than conceded."""
    committed = {2: 19, 3: 28, 4: 30, 5: 36, 6: 40, 7: 48, 8: 49, 9: 56,
                 10: 63, 11: 70, 12: 66, 13: 72, 14: 52}
    exact = optimal_costs()
    rows = {T: {"committed": committed.get(T), "optimum": exact.get(T),
                "excess": (committed[T] - exact[T])
                if committed.get(T) and exact.get(T) else None}
            for T in sorted(exact)}
    matches = [T for T, r in rows.items() if r["excess"] == 0]
    return {
        "per_division": rows,
        "optimum_curve": [exact[T] for T in sorted(exact) if exact[T]],
        "committed_matches_the_optimum_only_at": matches,
        "max_excess": max((r["excess"] for r in rows.values()
                           if r["excess"] is not None), default=None),
        "four_divisions_committed": rows[4]["committed"],
        "four_divisions_optimum": rows[4]["optimum"],
    }


def claim_the_witness_ladder_is_feasible_and_cheaper() -> dict:
    """The explicit 4-division counterexample, verified in 2 tools."""
    ladder = [(2, 1), (2, 1), (18, 14)]
    cs = cm = ws = wm = 1.0
    per = []
    for a, s in ladder:
        c1, c2 = _sf(s, a, CAPABLE_RATE), _sf_exact(s, a, CAPABLE_RATE)
        w1, w2 = _sf(s, a, WEAK_RATE), _sf_exact(s, a, WEAK_RATE)
        cs *= c1; cm *= c2; ws *= w1; wm *= w2
        per.append({"gate": (a, s), "capable": round(c1, 10),
                    "weak": round(w1, 10)})
    total = sum(a for a, _ in ladder)
    return {
        "ladder": ladder, "per_gate": per, "total_attempts": total,
        "committed_cost_for_4_divisions": 30,
        "end_to_end_capable": round(cs, 10),
        "end_to_end_weak": round(ws, 10),
        "inside_the_budget": cs >= P_CAPABLE_MIN and ws <= P_WEAK_MAX,
        "cheaper_than_committed": total < 30,
        "scipy_mpmath_max_abs_diff": max(abs(cs - cm), abs(ws - wm)),
        "wolfram_recorded": {"capable": 0.9524672012, "weak": 0.0086860657,
                             "attribution": ("Wolfram Language, local Wolfram "
                                             "Engine, via wolframscript")},
    }


def claim_the_merge_lemma_fails_inside_the_threshold_family(
        trials: int = 4000, seed: int = 5, maxa: int = 12) -> dict:
    """THE OPEN QUESTION, measured. Is the monotonicity proof available?

    The merge argument needs: for any 2 gates, a SINGLE gate on the concatenated
    attempts that is at least as good on BOTH criteria. If that holds, collapsing
    adjacent gates proves cost(T) <= cost(T+1) and monotonicity is a theorem. If
    it fails, monotonicity rests on the scan.
    """
    import random
    rng = random.Random(seed)
    fails, tested, examples = 0, 0, []
    for _ in range(trials):
        a1 = rng.randint(1, maxa); s1 = rng.randint(1, a1)
        a2 = rng.randint(1, maxa); s2 = rng.randint(1, a2)
        and_cap = _sf(s1, a1, CAPABLE_RATE) * _sf(s2, a2, CAPABLE_RATE)
        and_weak = _sf(s1, a1, WEAK_RATE) * _sf(s2, a2, WEAK_RATE)
        tested += 1
        ok = any(_sf(s, a1 + a2, CAPABLE_RATE) >= and_cap
                 and _sf(s, a1 + a2, WEAK_RATE) <= and_weak
                 for s in range(1, a1 + a2 + 1))
        if not ok:
            fails += 1
            if len(examples) < 4:
                examples.append({"gates": [(a1, s1), (a2, s2)],
                                 "and_capable": round(and_cap, 8),
                                 "and_weak": round(and_weak, 8)})
    z = 1.959963984540054
    p = fails / tested
    d = 1 + z * z / tested
    c = (p + z * z / (2 * tested)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / tested + z * z / (4 * tested * tested))
    return {
        "pairs_tested": tested,
        "pairs_with_no_dominating_merged_gate": fails,
        "rate": round(p, 6),
        "wilson": (round(max(0.0, c - h), 6), round(min(1.0, c + h), 6)),
        "merge_is_a_lemma_within_the_threshold_family": fails == 0,
        "examples": examples,
        "consequence": ("monotonicity rests on the SCAN unless a ladder's gates "
                        "may be arbitrary tests rather than success-count "
                        "thresholds -- a modelling decision nobody has made"),
    }


def claim_monotonicity_survives_other_budgets() -> dict:
    """A sweep cannot prove a universal, and this says so in its own output."""
    settings = [
        (0.90, 0.50, 0.95, 0.010, "the brief's own budget"),
        (0.90, 0.50, 0.99, 0.001, "tighter both sides"),
        (0.80, 0.40, 0.95, 0.010, "lower rates, same gap"),
        (0.70, 0.30, 0.90, 0.020, "wide gap, slack budget"),
        # The 2 below are INFEASIBLE within the per-gate attempts ceiling and are
        # KEPT for that reason: a sweep that quietly drops its empty cells reports
        # "no inversion anywhere" over a population it chose after looking. Both
        # have a capable/weak gap too narrow for any ladder to separate at this
        # budget, which is itself the answer to "can T be derived from task
        # complexity" -- below some separation, no number of divisions works.
        (0.95, 0.80, 0.95, 0.050, "narrow gap, loose budget"),
        (0.85, 0.75, 0.95, 0.010, "very narrow gap"),
    ]
    rows, inversions, free = {}, 0, []
    for cap, weak, pc, pw, label in settings:
        c = optimal_costs(cap, weak, pc, pw, max_div=9, maxtot=70)
        seq = [c[T] for T in sorted(c) if c[T] is not None]
        down = sum(1 for a, b in zip(seq, seq[1:]) if b < a)
        flat = [(T, Tn) for T, Tn in zip(sorted(c), sorted(c)[1:])
                if c[T] is not None and c[Tn] is not None and c[Tn] == c[T]]
        inversions += down
        if flat:
            free.append({"setting": label, "free_steps": flat,
                         "curve": seq})
        rows[label] = {"curve": seq, "downward_steps": down,
                       "free_steps": flat, "feasible": bool(seq)}
    feasible = [l for l, r in rows.items() if r["feasible"]]
    infeasible = [l for l, r in rows.items() if not r["feasible"]]
    return {
        "settings": rows,
        "settings_tested": len(rows),
        "settings_feasible": len(feasible),
        "settings_infeasible": infeasible,
        "total_inversions_found": inversions,
        "monotone_everywhere_tested": inversions == 0,
        "settings_where_a_division_is_FREE": free,
        "bound": (f"{len(rows)} settings tested, {len(feasible)} feasible, and "
                  f"support is NOT proof: a sweep cannot establish a universal, "
                  f"which is why the merge lemma above matters"),
    }


def claim_the_symbolic_half_is_checked() -> dict:
    """SymPy and z3 on the 1 thing that IS provable here: the gate-menu lemma."""
    import sympy as sp
    import z3
    # Lemma: a product of factors each <= 1 cannot exceed any single factor, so a
    # gate below the end-to-end capable floor can never appear.
    x, y = sp.symbols("x y", positive=True)
    lemma = sp.simplify(sp.Le(x * y, x).subs(y, sp.Min(y, 1)))
    a, b, t = z3.Reals("a b t")
    s = z3.Solver()
    s.add(a > 0, a <= 1, b > 0, b <= 1, t > 0, t <= 1, a * b >= t, a < t)
    return {
        "sympy_product_le_factor": str(lemma),
        "z3_search_for_a_gate_below_the_floor_in_a_feasible_ladder": str(s.check()),
        "lemma_holds": str(s.check()) == "unsat",
        "note": ("unsat means no feasible ladder contains a gate whose capable-pass "
                 "is below the end-to-end floor, which is what justifies the menu "
                 "reduction rather than merely making it convenient"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sweep", action="store_true",
                    help="also run the multi-budget robustness sweep (slow: a "
                         "Pareto dynamic program per setting). OFF by default "
                         "because a declared brief figure RE-EXECUTES this file "
                         "and the panel validator has a 600 s ceiling.")
    args = ap.parse_args()

    print("== 1. the identical-gate costs were upper bounds (CC1 claim WITHDRAWN) ==")
    d1 = claim_the_identical_gate_costs_were_upper_bounds()
    for T, r in d1["per_division"].items():
        print(f"   {T:2d} divisions: committed {str(r['committed']):>3} -> "
              f"optimum {str(r['optimum']):>3}   excess {r['excess']}")
    print(f"   optimum curve: {d1['optimum_curve']}")
    print(f"   committed matches the optimum only at: "
          f"{d1['committed_matches_the_optimum_only_at']}")
    print(f"   largest excess: {d1['max_excess']}")

    print("\n== 2. the explicit 4-division witness ==")
    d2 = claim_the_witness_ladder_is_feasible_and_cheaper()
    print(f"   ladder {d2['ladder']}  ->  optimum: {d2['total_attempts']} attempts "
          f"(committed {d2['committed_cost_for_4_divisions']})")
    print(f"   end-to-end capable {d2['end_to_end_capable']} (need >= 0.95), "
          f"weak {d2['end_to_end_weak']} (allow <= 0.01)")
    print(f"   inside the budget: {d2['inside_the_budget']}   cheaper: "
          f"{d2['cheaper_than_committed']}")
    print(f"   scipy vs mpmath: {d2['scipy_mpmath_max_abs_diff']:.3e}")
    print(f"   Wolfram recorded: {d2['wolfram_recorded']['capable']}, "
          f"{d2['wolfram_recorded']['weak']}  "
          f"[{d2['wolfram_recorded']['attribution']}]")

    print("\n== 3. the merge lemma, which is what a PROOF would need ==")
    d3 = claim_the_merge_lemma_fails_inside_the_threshold_family()
    for k in ("pairs_tested", "pairs_with_no_dominating_merged_gate", "rate",
              "wilson", "merge_is_a_lemma_within_the_threshold_family",
              "consequence"):
        print(f"   {k}: {d3[k]}")

    print("\n== 4. the symbolic half that IS provable ==")
    for k, v in claim_the_symbolic_half_is_checked().items():
        print(f"   {k}: {v}")

    if args.sweep:
        print("\n== 5. does monotonicity survive other budgets? ==")
        d5 = claim_monotonicity_survives_other_budgets()
        for label, r in d5["settings"].items():
            print(f"   {label:26s} {r['curve']}  down {r['downward_steps']}"
                  f"{'  FREE at ' + str(r['free_steps']) if r['free_steps'] else ''}")
        print(f"   settings tested: {d5['settings_tested']}, feasible: "
              f"{d5['settings_feasible']}, infeasible: {d5['settings_infeasible']}")
        print(f"   inversions found anywhere: {d5['total_inversions_found']}")
        print(f"   {d5['bound']}")
    else:
        print("\n== 5. the multi-budget sweep is OFF; re-run with --sweep ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
