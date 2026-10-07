#!/usr/bin/env python3
"""The 8.49986 spurious-convergence ratio is an UPPER BOUND, not a measurement.

P-PASS OF THIS SESSION'S OWN BRIEF, 2026-10-07. `bench/a_shrinking_roster_converges_sooner_2026-10-07.py`
measures how much more likely K consecutive quiet rounds become as the roster
shrinks, and reports a factor of 8.49986 going from 6 seats to 4. That figure
was carried into the panel brief `bench/logs/dynamic_roster_and_derived_ladder_2026-10-07/BRIEF.md`
as though it were a property of the gate.

IT IS NOT. It assumes the seats are INDEPENDENT, and they are not: every seat in
a round receives a byte-identical brief and the same target, so a round is
plausibly productive or barren for all of them together. The independence
assumption is the most favourable possible case for the claim, which is exactly
the direction a claim should not be allowed to fail in.

MEASURED HERE with a shared per-round latent factor (Beta-Binomial, dispersion
set from a correlation rho by the method of moments):

    rho = 0.0   ratio 6 -> 4 = 8.5616   (independence, the brief's case)
    rho = 0.1   ratio 6 -> 4 = 3.8835
    rho = 0.3   ratio 6 -> 4 = 1.9047   (mpmath exact integral: 1.9200)
    rho = 0.5   ratio 6 -> 4 = 1.3920
    rho = 0.8   ratio 6 -> 4 = 1.0985

So the HAZARD SURVIVES -- the ratio stays above 1 at every correlation tested,
so a shrinking roster always goes quiet sooner -- but its MAGNITUDE falls by
nearly an order of magnitude over a plausible range of rho. The qualitative
conclusion holds and the quantitative one does not.

WHAT THIS MEANS FOR THE DESIGN, and it is not a retraction. The reason to record
the live roster beside the quiet-round count does not depend on the size of the
ratio at all: z3 establishes that 0 new criticals from a healthy panel and 0 from
a depleted one are the same integer, so the count alone cannot separate them
whatever rho is. The ratio sets how URGENT the fix is, not whether it is needed.

WHAT IS MISSING AND IS MEASURABLE. rho has never been measured in this project.
It can be, from the archive: per-round, per-seat new-critical counts are recorded,
so the intra-round correlation is an empirical quantity rather than a parameter
anyone has to choose. Until it is measured, any statement of the ratio must carry
its rho.

THE DISPATCHED BRIEF WAS DELIBERATELY NOT EDITED. Its sha256 is the star-topology
grouping key in `bench/star_topology_2026-10-06.py`, so rewriting it mid-flight
would make the blind round's recorded brief differ from the one the seats
received. The brief also instructs each seat to find where it is still wrong, so
the blind round is a live test of whether a seat catches this overstatement
independently. The amendment travels to the joint round instead.

Run: python3 bench/the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py
"""
from __future__ import annotations

import argparse

K_DEFAULT = 3
Q_DEFAULT = 0.3


def ratio_independent(n_hi: int = 6, n_lo: int = 4,
                      q: float = Q_DEFAULT, k: int = K_DEFAULT) -> float:
    """Closed form, the brief's case."""
    return ((1 - q) ** n_lo) ** k / ((1 - q) ** n_hi) ** k


def ratio_exact_beta_binomial(rho: float, n_hi: int = 6, n_lo: int = 4,
                              q: float = Q_DEFAULT, k: int = K_DEFAULT) -> float:
    """Exact integral over the latent round quality. mpmath, arbitrary precision."""
    import mpmath as mp
    mp.mp.dps = 30
    if rho <= 0:
        return ratio_independent(n_hi, n_lo, q, k)
    s = (1 / mp.mpf(rho)) - 1
    a, b = mp.mpf(q) * s, (1 - mp.mpf(q)) * s

    def quiet(n):
        f = lambda p: (1 - p) ** n * p ** (a - 1) * (1 - p) ** (b - 1)
        return mp.quad(f, [0, 1]) / mp.beta(a, b)

    return float(quiet(n_lo) ** k / quiet(n_hi) ** k)


def ratio_simulated(rho: float, n_hi: int = 6, n_lo: int = 4,
                    q: float = Q_DEFAULT, k: int = K_DEFAULT,
                    batches: int = 400, batch: int = 1000,
                    seed: int = 7) -> tuple[float, float, float]:
    """Monte Carlo, the second tool. Returns (ratio, P_quiet(hi), P_quiet(lo))."""
    import numpy as np
    rng = np.random.default_rng(seed)
    a = b = None
    if rho > 0:
        s = (1.0 / rho) - 1.0
        a, b = q * s, (1 - q) * s

    def p_quiet(n):
        quiet = 0
        for _ in range(batches):
            ok = np.ones(batch, dtype=bool)
            for _r in range(k):
                pr = (np.full(batch, q) if a is None
                      else rng.beta(a, b, size=batch))
                ok &= (rng.random((batch, n)) >= pr[:, None]).all(axis=1)
            quiet += int(ok.sum())
        return quiet / (batches * batch)

    hi, lo = p_quiet(n_hi), p_quiet(n_lo)
    return ((lo / hi) if hi > 0 else float("inf")), hi, lo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--batches", type=int, default=400)
    a = ap.parse_args()

    print(f"independence (the brief's figure): {ratio_independent():.6f}")
    print()
    print("with a shared per-round latent factor:")
    rows = {}
    for rho in (0.0, 0.1, 0.3, 0.5, 0.8):
        r, hi, lo = ratio_simulated(rho, batches=a.batches)
        rows[rho] = r
        print(f"  rho={rho:<4} simulated ratio 6->4 = {r:8.4f}   "
              f"P_quiet(6)={hi:.6f}  P_quiet(4)={lo:.6f}")
    print()
    print("mpmath exact integral, as the second tool:")
    for rho in (0.1, 0.3, 0.5):
        print(f"  rho={rho:<4} exact ratio 6->4 = "
              f"{ratio_exact_beta_binomial(rho):8.4f}")
    print()
    surv = all(v > 1.0 for v in rows.values())
    print(f"hazard survives every correlation tested: {surv}")
    print(f"ratio falls by a factor of {rows[0.0] / rows[0.8]:.4f} "
          f"from rho=0.0 to rho=0.8")
    print()
    print("THE QUALITATIVE CONCLUSION HOLDS AND THE QUANTITATIVE ONE DOES NOT.")
    print("The reason to record the live roster does not depend on the ratio at")
    print("all: z3 shows 0 new criticals from a healthy and a depleted panel are")
    print("the same integer. The ratio sets URGENCY, not necessity.")
    print("rho has never been measured here and is measurable from the archive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
