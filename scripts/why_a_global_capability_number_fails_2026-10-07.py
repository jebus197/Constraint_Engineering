#!/usr/bin/env python3
"""Cheapest-first, strongest-first, and a single measured number per model all fail.

THE FOUNDER'S TENSION, 2026-10-07: *"Even if I say 'escalate from cheapest upward', how
does even this make sense when the point is to simply derive the solution efficiently
and effectively, based on a measure of the available resources? Why put for example a
highly complex problem, like the Riemann hypothesis, to a model like DeepSeek (or even
Haiku), when its resources are better suited to dealing with less complex problems? Can
you see the tension?"*

THE TENSION IS REAL, AND THE INTERESTING RESULT IS THAT MEASUREMENT ALONE DOES NOT
DISSOLVE IT. A measured statistic that is ONE NUMBER PER MODEL reproduces the same
failure as cheapest-first, because one number cannot tell a hard task from an easy one.
Only an estimate CONDITIONED ON THE TASK puts a weak model last on hard work -- and it
does so automatically, with no vendor name involved, which is what the founder's
standing ruling asks for.

This is also what `adaptive_distributed_compute_design_spec.md` section 6.1 already
specifies: the detection term is "task-, class-, tool-, and configuration-conditioned"
and must carry an uncertainty interval. The ladder as it stands is the degenerate case
of that spec with the conditioning removed and the estimate frozen to a tuple of names.

Run: python3 scripts/why_a_global_capability_number_fails_2026-10-07.py
"""
from __future__ import annotations

import argparse
import sys

#: Task-conditioned success probability on an EASY and a HARD unit, and relative cost.
#: Chosen to make the founder's case concrete: a cheap configuration that is good at
#: easy work and near-useless on hard work. The numbers are illustrative of the SHAPE,
#: not measured rates -- the archive does not yet carry enough provenance-clean
#: attempts to estimate per-task rates for any model, which is itself the finding.
CONFIGS = {
    "cheap":  (0.70, 0.02, 1.0),
    "mid":    (0.75, 0.25, 4.0),
    "strong": (0.80, 0.60, 10.0),
}

#: Share of easy work assumed when collapsing to ONE global number per model.
GLOBAL_MIX = 0.5


def _order(key):
    return sorted(CONFIGS, key=lambda m: -key(*CONFIGS[m]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="why_a_global_capability_number_fails_2026-10-07.py",
        description=__doc__.split("\n\n")[0])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    import sympy as sp

    rules = {
        "cheapest-first (ignores value)": _order(lambda pe, ph, c: -c),
        "strongest-first (ignores cost)": _order(lambda pe, ph, c: ph),
        "index on ONE global p": _order(
            lambda pe, ph, c: (GLOBAL_MIX * pe + (1 - GLOBAL_MIX) * ph) / c),
        "index on task-conditioned p, EASY": _order(lambda pe, ph, c: pe / c),
        "index on task-conditioned p, HARD": _order(lambda pe, ph, c: ph / c),
    }
    print("=" * 78)
    print("ORDERINGS")
    print("=" * 78)
    for name, order in rules.items():
        print(f"  {name:38s} {' > '.join(order)}")

    print()
    print("WHO IS TRIED FIRST ON THE HARD TASK")
    for name, order in rules.items():
        if name.endswith("EASY"):
            continue
        print(f"  {name:38s} -> {order[0]}")

    # 2-tool cross-check on the decisive ordering: SymPy exact rationals vs floats.
    sym = {m: sp.Rational(str(v[1])) / sp.Rational(str(v[2]))
           for m, v in CONFIGS.items()}
    sym_order = sorted(sym, key=lambda m: -sym[m])
    flt_order = sorted(CONFIGS, key=lambda m: -(CONFIGS[m][1] / CONFIGS[m][2]))
    assert sym_order == flt_order, (sym_order, flt_order)
    print()
    print(f"  SymPy exact and float agree on the hard-task order: {sym_order}")
    for m in sym_order:
        print(f"    {m:8s} p_hard/cost = {sym[m]} = {float(sym[m]):.6f}")

    print()
    print("=" * 78)
    print("THE POINT. A single measured number per model orders EVERY task the same")
    print("way, so it sends a hard problem to the cheap configuration exactly as")
    print("cheapest-first does. Conditioning the estimate on the task puts the cheap")
    print("configuration LAST on hard work without consulting any vendor name, and")
    print("selects neither extreme: `mid` returns more risk-reduction per unit cost")
    print("on hard work than `strong` does.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
