#!/usr/bin/env python3
"""The 4 reasons `_estimate_gamma` returns 0.0, and which one is a slope.

PRODUCER for the figures quoted in the panel brief
`bench/logs/gamma_gates_everywhere_2026-10-08/BRIEF.md`, so each travels with the
code that computes it rather than existing as prose.

THE POINT. A flat cumulative curve is MAXIMAL diminishing returns, and the
estimator says so for every flat-after-something case. For flat-at-ZERO it returns
the FLOOR -- the same value it gives a curve still climbing steeply -- because
log(0) is undefined and it bails. That is a wrong answer, not an unknowable one,
and conflating the 2 is what let gamma be described as "reported-not-gated".

Run: python3 bench/gamma_sentinel_versus_slope_2026-10-08.py
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

#: Series chosen to cover all 4 return-0.0 reasons plus 2 genuine slopes.
CASES = [
    ("found 1 then flat", [1, 0, 0, 0, 0]),
    ("found 5 then flat", [5, 0, 0, 0, 0]),
    ("found 2 then 1 then flat", [2, 1, 0, 0, 0]),
    ("still climbing", [1, 2, 3, 4, 5]),
    ("constant arrival rate", [2, 2, 2, 2, 2, 2]),
    ("nothing ever found", [0, 0, 0, 0, 0]),
    ("too few rounds", [1, 1]),
    ("sparse, window met, gamma low", [1, 3, 0, 0, 0]),
    ("sparse, window met, gamma lower", [1, 4, 0, 0, 0]),
]


def _runner():
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "rr_gsv", root / "bench" / "reference_runner_v3.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["rr_gsv"] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--theta", type=float, default=0.30,
                    help="the gate's gamma arm, for reference only")
    a = ap.parse_args()
    R = _runner()
    print(f"gate arm theta = {a.theta}")
    print()
    print("  label                        series                 cumulative            "
          "gamma     estimable")
    for label, s in CASES:
        cum, t = [], 0
        for c in s:
            t += c
            cum.append(t)
        g = R._estimate_gamma(s)
        e = R._gamma_is_estimable(s)
        print(f"  {label:27s} {str(s):22s} {str(cum):21s} {g:.4f}    {e}")
    print()
    flat = R._estimate_gamma([1, 0, 0, 0, 0])
    zero = R._estimate_gamma([0, 0, 0, 0, 0])
    climb = R._estimate_gamma([1, 2, 3, 4, 5])
    print(f"flat-after-something = {flat:.4f}  (the ceiling: fully decayed)")
    print(f"flat-at-zero         = {zero:.4f}  (the FLOOR, and wrong)")
    print(f"still climbing       = {climb:.4f}  (the floor, and right)")
    print()
    print("flat-at-zero and still-climbing are the SAME value for OPPOSITE reasons,")
    print("which is why the gate must separate the sentinel from a slope before it")
    print("compares anything to the arm.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
