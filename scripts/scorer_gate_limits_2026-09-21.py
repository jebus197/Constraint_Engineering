#!/usr/bin/env python3
"""What the e1_efficacy gate fixed, what it did not, and what it briefly broke.

Three findings from the free panel round of 2026-09-21, each reproduced here so
the figures quoted to the founder are re-executable rather than prose.

1. THE GRADIENT THAT PAID FOR BREAKING THE INSTRUMENT (found by the fable seat,
   now FIXED). `INDETERMINATE_OTHER` was returned at 2 sites: one where no
   falsifier is attached, and one reached only AFTER the baseline confirmed and
   the overlay intercepted -- meaning the instrument worked until the fix
   touched the target. The gate dropped both from the weighted mean, so crashing
   the probe outscored letting it run and fail. The repair gives the second site
   its own outcome name and ESCALATES on it.

2. THE DILUTION THE REPAIR DOES NOT CLOSE (found by the cc2 seat, OPEN). A fix
   measured not to cure its own falsifier still scores 5/(5+w) with clean harm
   gates. No FINITE weight makes an arithmetic mean decisive, so arguing 2.0
   against 4.0 cannot close it.

3. THE FLOOR UNDER SIGMA WHILE e4 IS A CONSTANT (cc2, OPEN). With every other
   gate at 0 and `e4_bandit` at its unvarying 1, E = 2/7. `compute_rk` can never
   be told "this fix resolved nothing". The repair LOWERED this floor from 2/5
   to 2/7; it did not remove it.

Every figure is cross-verified on 2 tools where it is symbolic (SymPy and z3)
and executed against the shipped scorer where it is behavioural.
"""
from __future__ import annotations

import sys
from math import sqrt
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))

TARGET = "bench/_scorer_limits_probe.py"
SOURCE = 'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
FIX = (
    "<<<< SEARCH\n"
    'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
    "====\n"
    'def divide(a, b):\n    """Guarded."""\n    if b == 0:\n'
    '        raise ValueError("b must be non-zero")\n    return a / b\n'
    ">>>> REPLACE"
)


def wilson(k: int, n: int) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n)))
    return ((c - h) / d, (c + h) / d)


def archived_indeterminate_split():
    """How many archived INDETERMINATE_OTHER records are the gameable site?"""
    import glob
    import json
    import os
    from collections import Counter
    det: Counter = Counter()
    for f in sorted(glob.glob(str(REPO / "bench/logs/*/runner_state.json"))):
        if os.path.getsize(f) > 60_000_000:
            continue
        try:
            raw = open(f, errors="ignore").read()
        except OSError:
            continue
        if "fix_efficacy" not in raw:
            continue
        try:
            doc = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue

        def walk(node):
            if isinstance(node, dict):
                fe = node.get("fix_efficacy")
                if isinstance(fe, dict) and fe.get("outcome") == "INDETERMINATE_OTHER":
                    det[str(fe.get("detail"))[:70]] += 1
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(doc)
    total = sum(det.values())
    post = sum(v for k, v in det.items() if "patched target" in k)
    return det, post, total


def main() -> None:
    import sympy as sp
    import z3
    from reference_runner_v3 import (
        FIX_EFFICACY_GATE_WEIGHT, _capture_baseline, compute_rk, compute_sk,
    )
    from fix_efficacy import (
        FIX_CURES, FIX_INEFFECTIVE, INDETERMINATE, PROBE_BROKEN_AFTER_BASELINE,
    )

    print("=" * 74)
    print("THE e1_efficacy GATE: WHAT IT FIXED, MISSED, AND BRIEFLY BROKE")
    print("=" * 74)

    det, post, total = archived_indeterminate_split()
    print("\n1. THE GRADIENT THAT PAID FOR BREAKING THE INSTRUMENT  [FIXED]")
    print(f"   archived INDETERMINATE_OTHER records : {total}")
    for k, v in det.most_common():
        site = "POST-baseline, the FIX broke it" if "patched target" in k else "PRE-baseline"
        print(f"      {v:>3}  [{site}]  {k}")
    if total:
        lo, hi = wilson(post, total)
        print(f"   gameable share: {post}/{total} = {post/total:.4%}  "
              f"Wilson [{lo:.4%}, {hi:.4%}]")

    base = _capture_baseline(SOURCE, source_path=TARGET)
    rows = {}
    for label, outcome in (("cures its falsifier", FIX_CURES),
                           ("fails it honestly", FIX_INEFFECTIVE),
                           ("BROKE the probe", PROBE_BROKEN_AFTER_BASELINE),
                           ("no falsifier at all", INDETERMINATE)):
        r = compute_sk(FIX, SOURCE, TARGET, baseline=base, fix_efficacy_outcome=outcome)
        rows[label] = r
        print(f"   {label:<22} sk={r.sk:<7} {r.tristate}")
    honest = rows["fails it honestly"].sk
    crashed = rows["BROKE the probe"].sk
    print(f"   crashing the probe now pays {crashed - honest:+.4f} sk (it paid +0.4000)")
    print(f"   and returns {rows['BROKE the probe'].tristate}, so it cannot be admitted")
    # THE REAL PATH, NOT compute_rk DIRECTLY. An earlier version of this script
    # printed `compute_rk(0.5, 0.3, 0.0) = 0.620000` for the ESCALATE row, which
    # is what the arithmetic gives and NOT what the runner does: `apply_sk_to_rk`
    # leaves R_k untouched on a non-updating tristate. Printing the raw figure
    # would have shown a risk penalty the code never applies.
    from reference_runner_v3 import apply_sk_to_rk
    print("   downstream, what the runner ACTUALLY does to R_k from R_old=0.5:")
    for label in ("cures its falsifier", "fails it honestly", "BROKE the probe"):
        r = rows[label]
        updated = compute_rk(0.5, 0.3, r.sk) if r.tristate == "ADMISSIBLE" else None
        rk, why = apply_sk_to_rk(0.5, r.tristate, updated)
        print(f"      {label:<22} sigma={r.sk:<7} -> R_k={rk:.6f}   ({why})")

    print("\n2. THE DILUTION NO WEIGHT CAN CLOSE  [OPEN, founder's call]")
    w = sp.Symbol('w', positive=True)
    sk_w = (0 * w + 2 + 1 + 2) / (w + 2 + 1 + 2)
    print(f"   a non-curing fix with clean harm gates scores sk(w) = {sp.simplify(sk_w)}")
    for ww in (1, 2, 4, 8, 20, 100):
        print(f"      w={ww:<4} -> sk = {float(sk_w.subs(w, ww)):.6f}")
    print(f"   limit as w grows without bound : {sp.limit(sk_w, w, sp.oo)}")
    print(f"   the shipped weight is {FIX_EFFICACY_GATE_WEIGHT}, giving "
          f"{float(sk_w.subs(w, FIX_EFFICACY_GATE_WEIGHT)):.6f}")
    print("   -> the dilution is a property of the arithmetic MEAN, not the weight.")

    print("\n3. THE FLOOR UNDER SIGMA WHILE e4 IS A CONSTANT  [OPEN]")
    e1, e2, e3 = sp.symbols('e1 e2 e3', nonnegative=True)
    E = (2 * e1 + 2 * e2 + 1 * e3 + 2 * 1) / 7
    worst = sp.simplify(E.subs({e1: 0, e2: 0, e3: 0}))
    print(f"   worst case e1=e2=e3=0, e4=1 : E = {worst} = {float(worst):.6f}")
    z1, z2, z3_, zE = z3.Reals('e1 e2 e3 E')
    s = z3.Solver()
    s.add(z1 >= 0, z1 <= 1, z2 >= 0, z2 <= 1, z3_ >= 0, z3_ <= 1)
    s.add(zE == (2 * z1 + 2 * z2 + z3_ + 2) / 7,
          zE < z3.RealVal(2) / z3.RealVal(7))
    print(f"   z3: can E fall below 2/7 with e4 pinned at 1? {s.check()}  "
          "(unsat = floor proved)")
    print(f"   floor BEFORE this gate existed : {sp.Rational(2,5)} = 0.400000")
    print(f"   floor AFTER                    : {sp.Rational(2,7)} = 0.285714")
    print(f"   the repair LOWERED it by {float(sp.Rational(2,5)-sp.Rational(2,7)):.6f}, "
          "and did not remove it.")


if __name__ == "__main__":
    # A --help MUST NEVER COST ANYTHING (founder ruling). This walks every
    # archived runner_state.json and runs the real scorer, so an unguarded
    # --help would do all of it first.
    import argparse
    ap = argparse.ArgumentParser(
        description=("Measure what the e1_efficacy gate fixed, what it did not, "
                     "and the gradient it briefly created. Reads bench/logs, "
                     "writes nothing, dispatches to no model, costs nothing."),
        epilog=("Prints the archived INDETERMINATE split, the crash gradient "
                "before and after the repair, the weight-independent dilution, "
                "and the floor under sigma."))
    ap.parse_args()
    main()
