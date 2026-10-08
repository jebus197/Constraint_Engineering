#!/usr/bin/env python3
"""What serialising the 2 shared-subscription seats costs, and why 20 s.

THE FOUNDER'S QUESTION, 2026-10-07: *"Is back to back necessary? It doubles the
duration of a panel review. Isn't it the case that all that is needed is a few
second[s] between dispatching each model?"* And his ruling, 2026-10-08:
*"staggered dispatch as normal."*

WHAT THIS PRODUCES, so that no figure in the dispatcher, the guard or the brief
exists only as prose. `measured-rate-travels-with-its-script`.

  * The wall clock a free panel pays under strict serialisation against a
    stagger, over every archived round where BOTH free seats answered.
  * The shortest first-seat duration in that record, which is the ceiling on a
    usable stagger: SymPy reduces `max(d1, s+d2) <= d1+d2` to exactly `s <= d1`,
    and z3 returns `unsat` searching for a counterexample, so a stagger above
    the shortest first-seat duration is the one case where staggering LOSES to
    serialising.
  * Whether the chosen 20 s is never-slower across the whole record.

THE FLOOR ON THE STAGGER COMES FROM ELSEWHERE and is not recomputed here:
18.7 s, the single genuinely simultaneous co-failure in the record, measured by
`scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py`. The other 2
matched co-failures are both seats hitting 1 shared deadline, which is
arithmetic rather than contention.

NO MODEL NAMES ARE NEEDED FOR THE RESULT: the quantity is per-seat duration on
the shared route. The 2 seat labels are read from the archive only to pair the
2 durations within a round.

Run: python3 scripts/serialising_the_free_seats_costs_40_percent_2026-10-08.py
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: The 2 seats that ride 1 subscription, so the 2 whose dispatch was serialised.
SHARED_SEATS = ("cc2", "fable")

#: The collision a stagger must clear. Produced elsewhere; cited, not recomputed.
ESTABLISHMENT_COLLISION_S = 18.7

#: The value in force in bench/confer_maths_panel_2026-09-05.py.
CHOSEN_STAGGER_S = 20.0


def collect_pairs(repo: Path = REPO) -> dict:
    """Rounds where BOTH shared seats answered, with each one's duration."""
    rows: "dict[str, dict[str, float]]" = defaultdict(dict)
    for seat in SHARED_SEATS:
        for f in sorted(glob.glob(str(repo / "bench" / "logs" / "*" / f"{seat}.json"))):
            try:
                d = json.load(open(f))
            except Exception:
                continue
            if not isinstance(d, dict) or not d.get("ok"):
                continue
            e = d.get("elapsed_s")
            if isinstance(e, (int, float)) and e > 0:
                rows[Path(f).parent.name][seat] = float(e)
    return {k: v for k, v in rows.items() if len(v) == len(SHARED_SEATS)}


def claim_the_condition_is_exactly_s_le_d1() -> dict:
    """SymPy and z3 on when staggering beats serialising. 2 tools, 1 claim."""
    import sympy as sp
    import z3

    d1, d2, s = sp.symbols("d1 d2 s", positive=True)
    reduced = sp.simplify(sp.Le(s + d2, d1 + d2))          # the binding half
    a, b, c = z3.Reals("d1 d2 s")
    solver = z3.Solver()
    staggered = z3.If(a > c + b, a, c + b)                 # max(d1, s+d2)
    solver.add(a > 0, b > 0, c > 0, c <= a, staggered > a + b)
    counterexample = str(solver.check())
    # And the converse: ABOVE d1 a counterexample must EXIST, or the condition
    # would be sufficient but not necessary and 20 s would be arbitrary.
    conv = z3.Solver()
    conv.add(a > 0, b > 0, c > 0, c > a, staggered > a + b)
    return {
        "sympy_reduction": str(reduced),
        "z3_counterexample_under_s_le_d1": counterexample,
        "z3_counterexample_above_d1": str(conv.check()),
        "condition_is_necessary_and_sufficient": (
            counterexample == "unsat" and str(conv.check()) == "sat"),
    }


def claim_serialising_costs_wall_clock(stagger_s: float = CHOSEN_STAGGER_S,
                                       reps: int = 20000,
                                       seed: int = 3) -> dict:
    import numpy as np

    pairs = collect_pairs()
    if not pairs:
        return {"rounds": 0, "note": "no archived round has both seats landing"}
    first = np.array([pairs[k][SHARED_SEATS[0]] for k in sorted(pairs)])
    second = np.array([pairs[k][SHARED_SEATS[1]] for k in sorted(pairs)])
    serial = first + second
    staggered = np.maximum(first, stagger_s + second)
    saving = (serial - staggered) / serial
    rng = np.random.default_rng(seed)
    boot = [saving[rng.integers(0, len(saving), len(saving))].mean()
            for _ in range(reps)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    # An independent second computation of the same mean, in exact rationals.
    from fractions import Fraction
    exact = sum(
        (Fraction(float(a) + float(b)) - Fraction(max(float(a), stagger_s + float(b))))
        / Fraction(float(a) + float(b))
        for a, b in zip(first, second)) / len(first)
    return {
        "rounds_with_both_seats": len(pairs),
        "stagger_s": stagger_s,
        "median_serial_wall_clock_s": round(float(np.median(serial)), 1),
        "median_staggered_wall_clock_s": round(float(np.median(staggered)), 1),
        "mean_saving_fraction": round(float(saving.mean()), 4),
        "mean_saving_bootstrap_ci": (round(float(lo), 4), round(float(hi), 4)),
        "exact_fraction_agrees": abs(float(exact) - float(saving.mean())) < 1e-12,
        "shortest_first_seat_s": round(float(first.min()), 1),
        "never_slower_over_the_record": bool((staggered <= serial).all()),
    }


def claim_the_chosen_value_sits_between_both_bounds() -> dict:
    d = claim_serialising_costs_wall_clock()
    floor_ok = CHOSEN_STAGGER_S > ESTABLISHMENT_COLLISION_S
    ceil_ok = CHOSEN_STAGGER_S < d["shortest_first_seat_s"]
    # The widest stagger that is still never-slower, scanned rather than argued.
    import numpy as np
    pairs = collect_pairs()
    first = np.array([pairs[k][SHARED_SEATS[0]] for k in sorted(pairs)])
    second = np.array([pairs[k][SHARED_SEATS[1]] for k in sorted(pairs)])
    serial = first + second
    widest = None
    for s in range(1, 121):
        if (np.maximum(first, s + second) <= serial).all():
            widest = s
    return {
        "floor_s": ESTABLISHMENT_COLLISION_S,
        "ceiling_s": d["shortest_first_seat_s"],
        "chosen_s": CHOSEN_STAGGER_S,
        "clears_the_establishment_collision": floor_ok,
        "stays_under_the_shortest_first_seat": ceil_ok,
        "widest_never_slower_stagger_s": widest,
        "window_is_non_empty": floor_ok and ceil_ok,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stagger", type=float, default=CHOSEN_STAGGER_S)
    args = ap.parse_args()

    print("== 1. when staggering beats serialising, in 2 tools ==")
    for k, v in claim_the_condition_is_exactly_s_le_d1().items():
        print(f"   {k}: {v}")

    print("\n== 2. what serialisation costs over the archive ==")
    for k, v in claim_serialising_costs_wall_clock(args.stagger).items():
        print(f"   {k}: {v}")

    print("\n== 3. the chosen 20 s sits inside both bounds ==")
    for k, v in claim_the_chosen_value_sits_between_both_bounds().items():
        print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
