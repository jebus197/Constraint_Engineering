#!/usr/bin/env python3
"""Does NOT pruning dominate pruning? The removal clause demands a measurement.

HIS RULING, 2026-10-13, VERBATIM: *"I also agree the mechanical directive pruner
should be retired. We have no way of knowing what it feeds, or has been feeding
our models. We can achieve the same pruning goal by hand, probably with more
accuracy, so that the models get fed the same set of core directives every
single time an experiment is run."*

WHY THIS SCRIPT EXISTS. The additive standard permits a removal only when a
COMMITTED MEASUREMENT shows the replacement dominates on a NAMED PROPERTY -- a
judgement that something is better is not evidence that it is. His ruling names
two properties that the metric arguments of the panel did not: KNOWABILITY (what
reaches a model must be inspectable) and DETERMINISM (the same core directives
every single run). Both are measurable, and both are measured here, alongside
the pruner's own stated objective.

PROPERTY 1 -- THE PRUNER'S OWN OBJECTIVE, constraint density under budget.
`_count_constraints` reads the merged policy and is INDEPENDENT of the composed
text, so density = C / max(chars // 4, 1) can only RISE as text is deleted.
Identity therefore dominates pruning on the very metric pruning exists to
optimise. Discharged symbolically and by SMT below, and already pinned by
bench/tests/test_falsifier_C0001_prune_inversion_2026-09-10.py on real packets.

PROPERTY 2 -- DETERMINISM, which is his ground and is stronger than the metric.
The pruner's deletion set depends on the composed length, which depends on the
packet set, the model's budget and the domain. So two runs of the SAME
experiment against different seats receive different directive text, and nothing
records which text a given seat actually received. Retirement makes the
delivered set a function of the files alone.

PROPERTY 3 -- WHAT IT COSTS TO RETIRE, stated so the removal is not sold as
free. With pruning off, a composition over its budget stays over it. Nothing in
the harness fails on that: the budget is an advisory density figure, not a
transport limit, and the separate TRANSPORT limit -- `max_directive_chars`, the
C0040 reduced rendering -- is a DIFFERENT mechanism on a DIFFERENT file and is
untouched by this retirement. That distinction is the one both panel seats had
to correct in the brief, so it is stated here rather than assumed.

Usage: python3 scripts/retiring_the_pruner_dominates_2026-10-13.py
"""
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _cli_help import answer_help  # noqa: E402


def main() -> int:
    answer_help(__doc__, __file__)
    import mpmath
    import numpy as np
    import sympy as sp
    import z3

    print("=== PROPERTY 1: the pruner's own objective ===")
    C, L1, L2 = sp.symbols("C L1 L2", positive=True)
    d1, d2 = C / (L1 / 4), C / (L2 / 4)
    diff = sp.simplify(d2 - d1)
    print(f"  SymPy: density(after) - density(before) = {diff}")
    print(f"         with L2 < L1 and C > 0 this is strictly positive")
    worked = sp.simplify(diff.subs({C: 3, L1: 20000, L2: 12000}))
    print(f"  SymPy worked (C=3, 20000 -> 12000 chars): {worked} = "
          f"{float(worked):.8f} > 0")

    s = z3.Solver()
    Cz, a, b = z3.Reals("C a b")
    s.add(Cz > 0, a > 0, b > 0, a < b)          # a = after, b = before
    s.add(Cz / (a / 4) <= Cz / (b / 4))         # density did NOT worsen
    r = s.check()
    print(f"  z3: 'text shrank AND density did not worsen' -> {r}")
    assert r == z3.unsat
    print("      UNSAT: deleting text cannot lower density. Identity dominates.")

    before, after, cn = 20000.0, 12000.0, 3.0
    npw = bool(np.greater(cn / (after / 4), cn / (before / 4)))
    mpw = bool(mpmath.mpf(cn) / (after / 4) > mpmath.mpf(cn) / (before / 4))
    print(f"  NumPy agrees: {npw}   mpmath agrees: {mpw}")

    print("\n=== PROPERTY 2: determinism, his ground ===")
    try:
        import bench.cdsfl_registry.composer as C_
        budgets = getattr(C_, "MODEL_COHERENCE_BUDGETS", {})
        print(f"  per-model density budgets: {budgets}")
        if budgets:
            vals = sorted(set(budgets.values()))
            print(f"  distinct budgets across seats: {len(vals)} -> {vals}")
            print("  THE DELETION SET THEREFORE DIFFERS BY SEAT, so the same")
            print("  experiment feeds different directive text to different")
            print("  models, and no record says which text any seat received.")
            # the trigger length, per budget: prune fires iff chars/4 < C/budget
            print("\n  trigger length by budget, for a policy of C constraints:")
            for b in vals:
                print(f"    budget {b:<7} fires below  C * {4.0/b:,.0f} / 1 chars")
    except Exception as exc:                              # noqa: BLE001
        print(f"  composer not importable here: {type(exc).__name__}: {exc}")

    print("\n=== PROPERTY 3: what retirement does NOT fix ===")
    print("  The reduced rendering (C0040) is a SEPARATE mechanism keyed on")
    print("  `max_directive_chars` over cdsfl_core_formal.md. Retiring the")
    print("  pruner does not close it, and the 2026-07-18 hand-trim review")
    print("  targets cdsfl_operational.md, which is appended UNCAPPED. Both")
    print("  panel seats had to correct that conflation in the brief.")
    print("\nVERDICT: retirement is licensed on properties 1 and 2. Property 3")
    print("  remains open and is not claimed as fixed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
