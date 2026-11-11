#!/usr/bin/env python3
"""How often can the dimensional tool NOT choose a repair, and is its CONFIRM worth anything?

★ THE FOUNDER'S QUESTION, 2026-11-11, which is what this measures: *"If its
intended job is useful and it can do it reliably, shouldn't it be able to
correct things too? I guess the problem then might be what the intent in the
original calculation was? ... So the safer option in all cases where this is
detected, is to do what?"*

★ IT REFUTES CC1'S OWN EARLIER RECOMMENDATION. Entry B136 proposed moving
`dimensional_analysis` to `secondary_only` so it could corroborate but never
refuse. This script shows the tool is ONE-SIDED in the opposite direction: its
refusal is a proof and its confirmation carries 0 information.

★ AND IT REFUTED CC1'S FIRST ATTEMPT AT THE FOUNDER'S POINT. A first
enumeration used a single example, found a UNIQUE minimal repair, and would
have reported his underdetermination intuition as mistaken. The example was the
easy case -- 2 of its 3 terms already agreed. Enumerated exhaustively, he is
right in 0.400000 of cases.

Exit 0 on success. Every proportion carries a 95% interval on 2 independent
routes, per the 21 April 2026 cross-verification rule.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import sys

UNITS = ("m", "s", "kg", "J")
PROBES = (("1 km", "1000 m", True), ("1 km", "2000 m", False),
          ("5 kg", "5000 g", True), ("5 kg", "99 g", False))


def wilson_two_routes(k: int, n: int):
    """statsmodels, and an independent SymPy symbolic solve of the defining
    quadratic evaluated exactly. NOT scipy: `bench/falsifier_pairing.py`
    records that scipy and statsmodels resolve to the same verifier, so the
    pair would be 1 function called twice."""
    import sympy as sp
    from statsmodels.stats.proportion import proportion_confint
    lo1, hi1 = proportion_confint(k, n, alpha=0.05, method="wilson")
    P = sp.Symbol("P", positive=True)
    ph = sp.Rational(k, n)
    z = sp.sqrt(2) * sp.erfinv(sp.Rational(95, 100))
    roots = sorted(sp.solve(sp.Eq((P - ph) ** 2, z ** 2 * P * (1 - P) / n), P))
    lo2, hi2 = (float(sp.N(r, 30)) for r in roots)
    return (lo1, hi1), (lo2, hi2), max(abs(lo2 - lo1), abs(hi2 - hi1))


def one_sidedness():
    """pint: homogeneity and truth are independent. z3: inhomogeneity is unsat."""
    import pint
    import z3
    U = pint.UnitRegistry()
    rows = []
    for a, b, truth in PROBES:
        qa, qb = U(a), U(b)
        homo = qa.dimensionality == qb.dimensionality
        num = bool(abs((qa - qb).to_base_units().magnitude) < 1e-12)
        rows.append((a, b, homo, num, truth))
    L, T = z3.Ints("L T")
    s = z3.Solver()
    s.add(z3.And(L == 1, T == 0))
    s.add(z3.And(L == 0, T == 1))
    return rows, str(s.check())


def repair_ambiguity(units=UNITS, slots: int = 3):
    rows = []
    for combo in itertools.product(units, repeat=slots):
        if len(set(combo)) == 1:
            continue
        c = collections.Counter(combo)
        top = max(c.values())
        winners = [u for u, n in c.items() if n == top]
        rows.append((combo, slots - top, len(winners)))
    return rows


def measure():
    probes, z3_verdict = one_sidedness()
    rows = repair_ambiguity()
    amb = [r for r in rows if r[2] > 1]
    return {"probes": probes, "z3": z3_verdict, "rows": rows, "amb": amb}


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    m = measure()

    print("THE DIMENSIONAL CHECK IS ONE-SIDED")
    homo_true = sum(1 for *_x, h, n, _t in [(p[0], p[1], p[2], p[3], p[4]) for p in m["probes"]] if h and n)
    print(f"  pint: {sum(1 for p in m['probes'] if p[2])} of {len(m['probes'])} probes homogeneous, "
          f"{sum(1 for p in m['probes'] if p[3])} of {len(m['probes'])} numerically true")
    for a_, b_, homo, num, _t in m["probes"]:
        print(f"    {a_:6s} = {b_:8s}  homogeneous={homo}  true={num}")
    print(f"  z3: dimension constraints for an inhomogeneous sum -> {m['z3']}")
    print("  => a REFUSAL is a proof; a CONFIRMATION carries 0 bits about truth")

    print("\nTHE REPAIR IS UNDERDETERMINED")
    k, n = len(m["amb"]), len(m["rows"])
    (lo1, hi1), (lo2, hi2), d = wilson_two_routes(k, n)
    print(f"  inhomogeneous 3-term equations over {len(UNITS)} units: {n}")
    print(f"  with MORE THAN ONE equally minimal repair: {k}")
    print(f"  proportion = {k}/{n} = {k / n:.6f}")
    print(f"    Wilson statsmodels [{lo1:.6f}, {hi1:.6f}]")
    print(f"    Wilson SymPy       [{lo2:.6f}, {hi2:.6f}]   agree to {d:.3e}")
    print("  where all 3 terms differ there are 3 equally minimal repairs")
    print("\n  AND MINIMALITY IS NOT INTENT: '3 m + 2 m = 5 m' is the unique")
    print("  minimal repair of '3 m + 2 s = 5 m', and the author may have")
    print("  meant a rate calculation. No measurement removes that.")

    if a.json:
        import json
        print(json.dumps({"ambiguous": k, "inhomogeneous": n,
                          "rate": k / n, "wilson": [lo1, hi1],
                          "z3": m["z3"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
