#!/usr/bin/env python3
"""Every proportion quoted from the 2026-10-12 free-panel harvest, with its interval.

WHY THIS EXISTS. `measured-rate-travels-with-its-script`: a rate quoted to the
founder in prose is a claim ABOUT evidence, not evidence. Every figure in the
harvest report is recomputed here, each by TWO independent tools, and the
logical claim about the repaired door is discharged by z3 rather than argued.

Usage: python3 scripts/the_panel_harvest_numbers_2026-10-12.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402


def intervals(k: int, n: int, label: str) -> None:
    """Wilson and Clopper-Pearson, statsmodels against scipy."""
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    import numpy as np

    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_cp, hi_cp = proportion_confint(k, n, alpha=0.05, method="beta")
    # SECOND TOOL: Wilson in closed form via numpy, Clopper-Pearson via the
    # scipy beta quantiles the method is defined by.
    z = stats.norm.ppf(0.975)
    p = k / n
    den = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    lo_w2, hi_w2 = centre - half, centre + half
    lo_cp2 = stats.beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi_cp2 = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0

    agree_w = max(abs(lo_w - lo_w2), abs(hi_w - hi_w2))
    agree_cp = max(abs(lo_cp - lo_cp2), abs(hi_cp - hi_cp2))
    print(f"{label}: {k} of {n} = {p:.4%}")
    print(f"    Wilson 95%          [{lo_w:.4%}, {hi_w:.4%}]  "
          f"(statsmodels vs numpy closed form agree to {agree_w:.2e})")
    print(f"    Clopper-Pearson 95% [{lo_cp:.4%}, {hi_cp:.4%}]  "
          f"(statsmodels vs scipy.beta agree to {agree_cp:.2e})")


def the_door_cannot_open_on_a_ruling() -> None:
    """z3: no assignment opens the door while any ladder record is a ruling.

    THE CLAIM. The repaired predicate opens only when EVERY routing_history
    record both resolved nothing and carries a no-reading verdict. The property
    that matters for safety is the converse: if ANY record is a ruling, the door
    must be shut. Proved over 3 records, which is enough because the predicate
    is a universal quantification over an unbounded list and a counterexample
    for any length projects to one of length <= 3.
    """
    import z3

    n = 3
    resolved = [z3.Bool(f"resolved_{i}") for i in range(n)]
    no_reading = [z3.Bool(f"no_reading_{i}") for i in range(n)]
    present = [z3.Bool(f"present_{i}") for i in range(n)]

    # The live predicate: for every present record, not resolved AND no_reading.
    door_open = z3.And([z3.Implies(present[i],
                                   z3.And(z3.Not(resolved[i]), no_reading[i]))
                        for i in range(n)])
    # A ruling is a present record that either resolved or is not no-reading.
    a_ruling_exists = z3.Or([z3.And(present[i],
                                    z3.Or(resolved[i], z3.Not(no_reading[i])))
                             for i in range(n)])

    s = z3.Solver()
    s.add(door_open, a_ruling_exists)
    r = s.check()
    print(f"z3: door_open AND a_ruling_exists -> {r}")
    assert r == z3.unsat, f"z3 found a counterexample: {s.model()}"
    print("    UNSAT: a ruling of any kind closes the door. Proved, not argued.")

    # And the door IS reachable -- an addition nothing reaches is not additive.
    s2 = z3.Solver()
    s2.add(door_open, z3.Or(present))
    r2 = s2.check()
    print(f"z3: door_open AND at least one record present -> {r2}")
    assert r2 == z3.sat, "the door is unreachable; it would be a dead addition"
    print("    SAT: a served-and-no-reading record still opens it.")

    # SECOND TOOL: SymPy over the same propositions.
    import sympy
    from sympy.logic.boolalg import And as sAnd, Or as sOr, Not as sNot, Implies
    from sympy.logic.inference import satisfiable
    rs = sympy.symbols("r0 r1 r2")
    nr = sympy.symbols("n0 n1 n2")
    pr = sympy.symbols("p0 p1 p2")
    s_open = sAnd(*[Implies(pr[i], sAnd(sNot(rs[i]), nr[i])) for i in range(n)])
    s_rule = sOr(*[sAnd(pr[i], sOr(rs[i], sNot(nr[i]))) for i in range(n)])
    sat = satisfiable(sAnd(s_open, s_rule))
    print(f"SymPy satisfiable(door_open & a_ruling_exists) -> {sat}")
    assert sat is False, "SymPy disagrees with z3"
    print("    SymPy agrees with z3: unsatisfiable.")


def main() -> int:
    answer_help(__doc__, __file__)
    print("=== INTERPRETER ALLOWLIST COVERAGE "
          "(scripts/interpreter_allowlist_coverage_2026-10-12.py) ===")
    for k, label in ((1, "baseline, no fix"), (2, "fable's probe"),
                     (3, "cc2's declared roots"), (4, "composed fix")):
        intervals(k, 4, f"  interpreters fully covered, {label}")
    print("\n=== THE SEATS' TESTS AGAINST THE UNFIXED TREE ===")
    intervals(21, 31, "  seat tests that FAILED without their own fix")
    print("\n=== THE REPAIRED DOOR, AS A LOGICAL CLAIM ===")
    the_door_cannot_open_on_a_ruling()
    return 0


if __name__ == "__main__":
    sys.exit(main())
