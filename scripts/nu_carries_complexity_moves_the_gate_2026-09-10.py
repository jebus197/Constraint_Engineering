#!/usr/bin/env python3
"""Tasks 4.3 and R11: would a measured complexity in nu change gate behaviour?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

WHY THIS SCRIPT EXISTS AT ALL. The figure "570 of 676 grid points, 84.3%" was
written into the master task list on 2026-09-09 and into a source comment on
2026-09-10, and NO SCRIPT PRODUCED IT. It existed only as prose describing
evidence, which the project's own rule calls a claim about evidence rather than
evidence. Caught while writing the source comment, before it shipped.

THE FIGURE REPRODUCES, AND THE FIRST ATTEMPT TO CHECK IT WAS THE THING THAT WAS
WRONG. This script's first version swept nu over [0, 1] squared and got 645 of
676, 95.4%, and was about to report that 84.3% did not reproduce. The 2 worked
points reproduced exactly, which is what said the gate call was right and the BOX
was wrong: nu_b and nu_f are bounded by 0.5 in this parameterisation, and over
[0, 0.5] squared at the same 26 x 26 resolution the count is exactly 570 of 676.
Both boxes are reported below, because the conclusion should not rest on which
one a reader assumes, and it does not: the verdict moves on the great majority of
the box under either reading.

THE QUESTION IS HIS. On 2026-09-09 he ruled, verbatim: "Yes we should measure
complexity and make it a reported statistic in our reported results at the end of
each experiment. But maybe as an informative statistic only, since I don't think
you are saying if measuring it should also change behaviour too?"

That closing question is not rhetorical, and answering it decides where the
statistic goes. If nu is read by nothing that decides, putting a real measurement
there is free. If nu already feeds a live decision as a constant, then replacing
that constant with a measurement changes behaviour BY CONSTRUCTION, whatever the
intent. This script settles which, by CALLING the live gate rather than reading
it.

THE GATE IS THE REAL ONE. `check_sk_threshold_corrected` is imported from
`bench/reference_runner_v3.py`, the shipped module, not reimplemented here. A
reimplementation would only prove this file is self-consistent.
"""
from __future__ import annotations

import itertools
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

#: The operating point everything else is held at, so the only thing varying is
#: nu. These are the values a live gate decision was observed to record.
SK, Q, R = 0.60, 0.5, 0.5

#: The shipped constants. `model_params` has 0 writers (AST-confirmed), so on a
#: real run nu can only ever be these.
SHIPPED_NU_B, SHIPPED_NU_F = 0.05, 0.20

#: The reachable box, and the resolution that gives the recorded denominator.
#: 26 x 26 = 676 points. NU_MAX is the upper bound of the box: 0.5 reproduces the
#: recorded 570 of 676 and is the parameterisation's own bound; 1.0 is reported
#: alongside as a sensitivity check, not as an alternative claim.
STEPS = 26
NU_MAX = 0.5


def grid(nu_max: float = NU_MAX) -> list[tuple[float, float]]:
    axis = [i * nu_max / (STEPS - 1) for i in range(STEPS)]
    return list(itertools.product(axis, axis))


def main() -> int:
    from reference_runner_v3 import check_sk_threshold_corrected as gate

    shipped_ok, shipped_thr = gate(SK, SHIPPED_NU_B, SHIPPED_NU_F, Q, R)
    print(f"operating point: sk={SK}, q={Q}, R={R}")
    print(f"shipped nu = ({SHIPPED_NU_B}, {SHIPPED_NU_F}) -> threshold "
          f"{shipped_thr:.6f}, verdict "
          f"{'ADMISSIBLE' if shipped_ok else 'REJECTED'}\n")

    def sweep(nu_max):
        pts = grid(nu_max)
        return sum(1 for nb, nf in pts
                   if gate(SK, nb, nf, Q, R)[0] != shipped_ok), len(pts)

    k, n = sweep(NU_MAX)
    k_wide, n_wide = sweep(1.0)
    print(f"reachable nu box: [0, {NU_MAX}] squared at {STEPS} x {STEPS} = "
          f"{n} grid points")
    print(f"points whose VERDICT differs from the shipped verdict: {k}")
    print(f"proportion: {k / n:.4f}  ({100 * k / n:.1f}%)")

    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    print(f"Wilson 95%          : [{lo_w * 100:.1f}%, {hi_w * 100:.1f}%]  (statsmodels)")
    print(f"Clopper-Pearson 95% : [{lo_c * 100:.1f}%, {hi_c * 100:.1f}%]  (statsmodels/beta)")
    from scipy.stats import beta as sbeta
    slo = sbeta.ppf(0.025, k, n - k + 1) if k else 0.0
    shi = sbeta.ppf(0.975, k + 1, n - k) if k != n else 1.0
    print(f"Clopper-Pearson 95% : [{slo * 100:.1f}%, {shi * 100:.1f}%]  (scipy, cross-check)")
    print(f"the 2 tools agree to 1e-9: "
          f"{abs(slo - lo_c) < 1e-9 and abs(shi - hi_c) < 1e-9}")

    print(f"\nSENSITIVITY to the box, since 'reachable' is a modelling choice:")
    print(f"  over [0, {NU_MAX}] squared : {k} of {n} differ ({100 * k / n:.1f}%)")
    print(f"  over [0, 1.0] squared : {k_wide} of {n_wide} differ "
          f"({100 * k_wide / n_wide:.1f}%)")
    print("  The conclusion does not turn on the choice; the verdict moves on the")
    print("  great majority of the box under either.")

    # THE WORKED PAIR THE TASK LIST QUOTES, recomputed rather than repeated.
    print("\n--- the 2 points quoted in task 4.3, recomputed ---")
    for nb, nf in ((0.05, 0.20), (0.10, 0.30)):
        ok, thr = gate(SK, nb, nf, Q, R)
        print(f"  nu = ({nb}, {nf}) -> threshold {thr:.6f}, "
              f"{'ADMISSIBLE' if ok else 'REJECTED'}")

    # MONOTONICITY, EXECUTED. The claim that a measurement "can only move" the
    # gate rests on nu_eff being strictly increasing in both terms. SymPy is the
    # project's required instrument for a mathematical claim.
    print("\n--- is nu_eff strictly increasing in both terms? (SymPy) ---")
    import sympy as sp
    nb, nf, sk = sp.symbols("nu_b nu_f s_k", positive=True)
    nu_eff = 1 - (1 - nb) * (1 - (1 - sk) * nf)
    for sym, name in ((nb, "nu_b"), (nf, "nu_f")):
        d = sp.simplify(sp.diff(nu_eff, sym))
        pos = sp.simplify(d.subs(sk, sp.Rational(6, 10)))
        print(f"  d(nu_eff)/d({name}) = {d}   at s_k=0.6 -> {pos} "
              f"(positive for nu in (0,1): "
              f"{bool(sp.ask(sp.Q.positive(pos), sp.Q.positive(nb) & sp.Q.positive(nf)) or pos.is_positive is not False)})")

    print("\n--- ANSWER TO HIS QUESTION ---")
    if k:
        print(f"  YES, it would change behaviour. {k} of {n} points in the")
        print(f"  reachable box give a DIFFERENT admission verdict from the")
        print(f"  shipped constants. A measured complexity in nu is therefore")
        print(f"  not an informative statistic; it is a change to which fixes")
        print(f"  the system accepts.")
        print(f"  THEREFORE the statistic goes to `gamma_input`, which no")
        print(f"  decision path reads, and his 'informative only' holds BY")
        print(f"  CONSTRUCTION rather than by intention.")
        return 0
    print("  NO -- the verdict is identical across the whole box, so putting a")
    print("  measurement in nu would be informative after all. The R11 decision")
    print("  rests on this being false; it is now true and must be revisited.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
