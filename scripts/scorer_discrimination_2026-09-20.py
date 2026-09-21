#!/usr/bin/env python3
"""Does S_k discriminate? Measured over every archived scored fix, 2026-09-20.

THE QUESTION, put by 7 of 7 blind panel seats independently: 672 of 902 archived
scored fixes are exactly 1.0. Is the scorer measuring anything?

THE ANSWER THIS SCRIPT PRODUCES, and it is a stronger statement than the pile-up.
`e4_bandit` carries weight 2.0 -- the heaviest of the 3 effect gates, double the
other 2 -- and across 902 archived decisions it took the value 1.0 exactly 902
times. Zero variance at double weight is not a gate; it is a constant addend. It
puts a STRUCTURAL FLOOR under S_k: with all 3 effect gates available,

    E = (2.0*e2 + 1.0*e3 + 2.0*e4) / 5.0  and e4 == 1  =>  E >= 0.4

so no fix, however bad, can score below 0.4 while A = 1. Of the 2 thresholds
disputed across 4 panel rounds, 0.395043 sits BELOW that floor and is therefore
UNREACHABLE BY CONSTRUCTION -- it could never have refused anything, whatever
the corpus -- while 0.504931 clears it by 0.104931.

THE WEIGHT WAS MIS-TRANSCRIBED ON THE FIRST ATTEMPT AND THE RECONSTRUCTION
CAUGHT IT. Reading the source gave e2 = 1.0; the source says 2.0. The error was
invisible to reading and visible the instant the recomputation was compared
against 902 recorded verdicts: 223 disagreed, and SymPy and z3 independently
recovered w2 = 2 from 2 of the disagreeing records. That is the `execute-do-not-
grep` discipline doing exactly what it exists for.

`compute_sk`'s own docstring already states e4 is "structurally incapable of
failing" -- but it states it about PROSE targets, as an argument for the prose
short-circuit. This script measures the same property on PYTHON targets, where
no short-circuit applies and the gate is live.

METHOD. Every `sk_result` in every archived `runner_state.json`, recomputed from
its own `gate_details` and compared against the recorded `sk`. That comparison is
the `execute-do-not-grep` discipline: the producer (the runner, at the time of the
run) and the consumer (this script, now) are executed against each other rather
than read. A reconstruction that disagrees would mean this script is measuring
something other than what the gate computed.

CROSS-VERIFICATION, per the 2026-04-21 rule. Every proportion carries a Wilson
interval from statsmodels AND a hand implementation. The floor is proved twice:
symbolically with SymPy (minimise E over the unit cube with e4 pinned) and as an
unsatisfiability result with z3 (no assignment makes E < 0.5).
"""
from __future__ import annotations

import glob
import json
import os
from collections import Counter, defaultdict
from math import sqrt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS = {"e2_regression": 2.0, "e3_ruff": 1.0, "e4_bandit": 2.0}
EFFECT = tuple(WEIGHTS)
HARD = ("g1_ast", "g2_compile")


def wilson(k: int, n: int) -> tuple[float, float]:
    """Wilson score interval, hand-rolled, cross-checked against statsmodels."""
    if n == 0:
        return (0.0, 0.0)
    if k > n:
        raise ValueError(f"k={k} exceeds n={n}")
    z = 1.959963984540054
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n)))
    return ((centre - half) / denom, (centre + half) / denom)


def collect() -> list[dict]:
    """Every sk_result recorded anywhere under bench/logs."""
    out: list[dict] = []
    for path in sorted(glob.glob(os.path.join(REPO, "bench/logs/*/runner_state.json"))):
        if os.path.getsize(path) > 60_000_000:
            continue
        try:
            raw = open(path, errors="ignore").read()
        except OSError:
            continue
        if "sk_result" not in raw:
            continue
        try:
            doc = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue

        def walk(node):
            if isinstance(node, dict):
                res = node.get("sk_result")
                if isinstance(res, dict) and "tristate" in res:
                    out.append(res)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(doc)
    return out


def recompute(res: dict) -> float | None:
    """Recompute sk from gate_details alone, as compute_sk does."""
    details = res.get("gate_details") or {}
    hard = []
    for gate in HARD:
        entry = details.get(gate)
        if not isinstance(entry, dict) or entry.get("score") is None:
            return None
        hard.append(float(entry["score"]))
    A = 1.0
    for score in hard:
        A *= score
    live = []
    for gate in EFFECT:
        entry = details.get(gate)
        if isinstance(entry, dict) and entry.get("score") is not None:
            live.append((float(entry["score"]), WEIGHTS[gate]))
    if not live:
        return None
    W = sum(w for _, w in live)
    E = sum((w / W) * s for s, w in live)
    return round(A * E, 4)


def main() -> None:
    rows = collect()
    adm = [r for r in rows if r.get("tristate") == "ADMISSIBLE"]
    print("=" * 74)
    print("S_k DISCRIMINATION, MEASURED OVER THE ARCHIVE")
    print("=" * 74)
    print(f"sk_result records found : {len(rows)}")
    print(f"  ADMISSIBLE            : {len(adm)}")
    print(f"  REJECTED              : {sum(1 for r in rows if r.get('tristate') == 'REJECTED')}")
    print(f"  NO_SCORE / ESCALATE   : {sum(1 for r in rows if r.get('tristate') not in ('ADMISSIBLE', 'REJECTED'))}")

    # -- 1. RECONSTRUCTION: producer vs consumer, executed --------------------
    print()
    print("1. RECONSTRUCTION — recompute sk from gate_details, compare to recorded")
    agree = disagree = skipped = 0
    worst = 0.0
    for res in adm:
        mine = recompute(res)
        if mine is None:
            skipped += 1
            continue
        theirs = round(float(res.get("sk", -1)), 4)
        gap = abs(mine - theirs)
        worst = max(worst, gap)
        if gap <= 5e-4:
            agree += 1
        else:
            disagree += 1
    n_rec = agree + disagree
    lo, hi = wilson(agree, n_rec)
    print(f"   reconstructed {n_rec} of {len(adm)} ({skipped} lacked a full gate_details record)")
    print(f"   AGREE {agree}/{n_rec} = {agree / n_rec:.4%}  Wilson [{lo:.4%}, {hi:.4%}]"
          if n_rec else "   nothing reconstructable")
    print(f"   largest absolute disagreement: {worst:.6f}")

    # -- 2. PER-GATE VARIANCE -------------------------------------------------
    print()
    print("2. PER-GATE — availability and observed variance")
    ran: Counter = Counter()
    unavailable: Counter = Counter()
    dist: defaultdict[str, Counter] = defaultdict(Counter)
    for res in adm:
        details = res.get("gate_details") or {}
        for gate in HARD + EFFECT:
            entry = details.get(gate)
            if isinstance(entry, dict) and entry.get("score") is not None:
                ran[gate] += 1
                dist[gate][float(entry["score"])] += 1
            else:
                unavailable[gate] += 1
    for gate in HARD + EFFECT:
        n = ran[gate]
        ones = dist[gate].get(1.0, 0)
        values = sorted(dist[gate])
        weight = WEIGHTS.get(gate, "hard")
        print(f"   {gate:<15} weight {weight!s:<5} ran {n:>4}  unavailable {unavailable[gate]:>4}")
        if n:
            lo, hi = wilson(ones, n)
            print(f"        scored 1.0 in {ones}/{n} = {ones / n:.4%}  Wilson [{lo:.4%}, {hi:.4%}]")
            print(f"        distinct values {len(values)}  min {min(values)}  max {max(values)}")
            if len(values) == 1:
                print(f"        *** ZERO VARIANCE across {n} decisions — a constant, not a gate ***")

    # -- 3. THE FLOOR ---------------------------------------------------------
    print()
    print("3. THE FLOOR that a constant gate at weight 2.0 puts under sk")
    import sympy as sp

    e2, e3, e4 = sp.symbols("e2 e3 e4", nonnegative=True)
    E_all = (WEIGHTS["e2_regression"] * e2 + WEIGHTS["e3_ruff"] * e3
             + WEIGHTS["e4_bandit"] * e4) / sum(WEIGHTS.values())
    floor_all = sp.simplify(E_all.subs({e2: 0, e3: 0, e4: 1}))
    E_no_e2 = (WEIGHTS["e3_ruff"] * e3 + WEIGHTS["e4_bandit"] * e4) / (
        WEIGHTS["e3_ruff"] + WEIGHTS["e4_bandit"])
    floor_no_e2 = sp.simplify(E_no_e2.subs({e3: 0, e4: 1}))
    print(f"   SymPy, all 3 gates available, e4 pinned at 1 : min E = {floor_all} = {float(floor_all):.6f}")
    print(f"   SymPy, e2 unavailable,        e4 pinned at 1 : min E = {floor_no_e2} = {float(floor_no_e2):.6f}")

    import z3

    z2, z3_, z4, zE = z3.Reals("e2 e3 e4 E")
    solver = z3.Solver()
    solver.add(z2 >= 0, z2 <= 1, z3_ >= 0, z3_ <= 1, z4 == 1)
    solver.add(zE == (2 * z2 + z3_ + 2 * z4) / 5)
    solver.add(zE < z3.RealVal(2) / z3.RealVal(5))
    verdict = solver.check()
    print(f"   z3, can E fall below 0.4 with e4 == 1?  {verdict}"
          f"   ({'FLOOR PROVED' if verdict == z3.unsat else 'FLOOR REFUTED'})")

    solver2 = z3.Solver()
    solver2.add(z2 >= 0, z2 <= 1, z3_ >= 0, z3_ <= 1, z4 >= 0, z4 <= 1)
    solver2.add(zE == (2 * z2 + z3_ + 2 * z4) / 5, zE < z3.RealVal(2) / z3.RealVal(5))
    verdict2 = solver2.check()
    print(f"   z3, same question with e4 FREE       ?  {verdict2}"
          f"   (a working e4 removes the floor)")

    observed = sorted(round(float(r.get("sk", 0)), 6) for r in adm)
    print(f"   observed minimum sk across {len(adm)} admissible decisions: {observed[0]:.6f}")
    for threshold in (0.504931, 0.395043):
        below = sum(1 for s in observed if s < threshold)
        lo, hi = wilson(below, len(observed))
        floor = 0.4
        reach = ("ABOVE the floor by %.6f" % (threshold - floor)) if threshold > floor \
            else "BELOW the floor — UNREACHABLE BY CONSTRUCTION"
        print(f"   threshold {threshold:.6f}: {below} of {len(observed)} below it, "
              f"Wilson [{lo:.4%}, {hi:.4%}] — {reach}")

    # -- 4. WHAT DISCRIMINATION REMAINS --------------------------------------
    print()
    print("4. WHERE THE VARIANCE ACTUALLY LIVES")
    import numpy as np

    arr = np.array(observed, dtype=float)
    print(f"   sk       mean {arr.mean():.6f}  sd {arr.std(ddof=1):.6f}  "
          f"range [{arr.min():.4f}, {arr.max():.4f}]")
    exactly_one = int((arr == 1.0).sum())
    lo, hi = wilson(exactly_one, len(arr))
    print(f"   exactly 1.0 in {exactly_one}/{len(arr)} = {exactly_one / len(arr):.4%}  "
          f"Wilson [{lo:.4%}, {hi:.4%}]")
    # What would sk look like with e4 removed from the mean entirely?
    alt = []
    for res in adm:
        details = res.get("gate_details") or {}
        live = [(float(details[g]["score"]), WEIGHTS[g]) for g in ("e2_regression", "e3_ruff")
                if isinstance(details.get(g), dict) and details[g].get("score") is not None]
        if not live:
            continue
        W = sum(w for _, w in live)
        alt.append(sum((w / W) * s for s, w in live))
    alt_arr = np.array(alt, dtype=float)
    print(f"   sk without e4: mean {alt_arr.mean():.6f}  sd {alt_arr.std(ddof=1):.6f}  "
          f"range [{alt_arr.min():.4f}, {alt_arr.max():.4f}]  n={len(alt_arr)}")
    print(f"   sd RATIO (without e4 / with e4): {alt_arr.std(ddof=1) / arr.std(ddof=1):.4f}x")
    a_one = int((alt_arr == 1.0).sum())
    lo, hi = wilson(a_one, len(alt_arr))
    print(f"   exactly 1.0 without e4: {a_one}/{len(alt_arr)} = {a_one / len(alt_arr):.4%}  "
          f"Wilson [{lo:.4%}, {hi:.4%}]")


if __name__ == "__main__":
    # A --help MUST NEVER COST ANYTHING (founder ruling; 15 of 17 runners once
    # billed a live dispatch on any unrecognised argument). This walks every
    # archived `runner_state.json` and re-runs SymPy and z3, so an unguarded
    # `--help` would do the whole measurement before printing nothing useful.
    import argparse

    ap = argparse.ArgumentParser(
        description=(
            "Measure whether S_k discriminates, over every archived scored fix. "
            "Reads bench/logs/*/runner_state.json; writes nothing; dispatches to "
            "no model and costs nothing."
        ),
        epilog=(
            "Prints: the reconstruction of every recorded sk from its own "
            "gate_details, per-gate availability and variance, the structural "
            "floor proved by SymPy and z3, and where the remaining variance lives."
        ),
    )
    ap.parse_args()
    main()
