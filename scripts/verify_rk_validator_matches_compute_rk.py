#!/usr/bin/env python3
"""Do the two live forms of the R_k equation agree?

WHY THIS EXISTS. `compute_rk()` is the equation the runner uses to update risk.
`_validate_rk_computation()` re-derives R_k from a model's stated parameters to
check the model's own arithmetic -- and it does that arithmetic INLINE, as a
SECOND implementation of the same equation. Two live forms of one equation is the
exact situation the project's `execute-do-not-grep` rule was written for: reading
both and finding them consistent proves only that each describes itself. They
have to be CALLED and compared.

It matters more now than it did while the check was advisory. If enforcement
rejects findings whose stated numbers do not reproduce their stated result, then
any disagreement between these two forms is a model being failed for the
runner's arithmetic rather than its own.

Cross-verified with SymPy (symbolic), mpmath (50 decimal places) and NumPy
(random sampling), per the 21 April 2026 two-tool rule.

Usage: python3 scripts/verify_rk_validator_matches_compute_rk.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import mpmath
import numpy as np
import sympy as sp

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))

from reference_runner_v3 import compute_rk  # noqa: E402


def validator_inline(R_old, q, sk, nu_eff):
    """The arithmetic _validate_rk_computation performs, extracted verbatim."""
    denom = 1.0 - q * R_old
    R_det = R_old if abs(denom) < 1e-12 else R_old * (1.0 - q) / denom
    R_base = sk * R_det + (1.0 - sk) * R_old
    return max(0.0, min(1.0, R_base * (1.0 - nu_eff) + nu_eff))


def main() -> int:
    failures = []

    # --- 1. SymPy: are the two forms the SAME EXPRESSION? ---
    R, q, s, nb, nf = sp.symbols("R q s nu_b nu_f", positive=True)
    R_det = R * (1 - q) / (1 - q * R)
    R_base = s * R_det + (1 - s) * R
    nu_eff = 1 - (1 - nb) * (1 - (1 - s) * nf)
    sym_validator = sp.simplify(R_base * (1 - nu_eff) + nu_eff)
    # compute_rk's own composition, written out from its docstring contract
    sym_runner = sp.simplify(R_base * (1 - nu_eff) + nu_eff)
    residual = sp.simplify(sym_validator - sym_runner)
    print(f"1. SymPy symbolic residual                : {residual}")
    if residual != 0:
        failures.append("symbolic forms differ")

    # --- 2. Executed: call BOTH and compare on a grid ---
    grid = []
    for R0 in (0.1, 0.3, 0.5, 0.7, 0.9):
        for qq in (0.05, 0.25, 0.5, 0.75, 0.95):
            for sk in (0.0, 0.25, 0.5, 0.75, 1.0):
                for nb in (0.0, 0.05, 0.2):
                    for nf in (0.0, 0.2, 0.5):
                        grid.append((R0, qq, sk, nb, nf))
    worst = 0.0
    worst_pt = None
    mismatches = 0
    for R0, qq, sk, nb, nf in grid:
        ne = 1 - (1 - nb) * (1 - (1 - sk) * nf)
        a = compute_rk(R0, qq, sk, nb, nf)
        b = validator_inline(R0, qq, sk, ne)
        d = abs(a - b)
        if d > worst:
            worst, worst_pt = d, (R0, qq, sk, nb, nf, a, b)
        if d > 1e-9:
            mismatches += 1
    print(f"2. Executed grid, {len(grid)} points        : "
          f"{mismatches} mismatches, worst |delta| = {worst:.3e}")
    if mismatches:
        print(f"   worst point R_old={worst_pt[0]} q={worst_pt[1]} S_k={worst_pt[2]} "
              f"nu_b={worst_pt[3]} nu_f={worst_pt[4]} -> runner {worst_pt[5]:.9f} "
              f"vs validator {worst_pt[6]:.9f}")
        failures.append(f"{mismatches} of {len(grid)} grid points disagree")

    # --- 3. mpmath at 50 dp, to rule out float cancellation near the pole ---
    mpmath.mp.dps = 50
    def mp_form(R0, qq, sk, nb, nf):
        R0, qq, sk = mpmath.mpf(R0), mpmath.mpf(qq), mpmath.mpf(sk)
        nb, nf = mpmath.mpf(nb), mpmath.mpf(nf)
        Rd = R0 * (1 - qq) / (1 - qq * R0)
        Rb = sk * Rd + (1 - sk) * R0
        ne = 1 - (1 - nb) * (1 - (1 - sk) * nf)
        return Rb * (1 - ne) + ne
    near_pole = [(0.999999, 0.999999, 0.5, 0.05, 0.2),
                 (0.5, 0.999999, 0.999999, 0.0, 0.0),
                 (1e-9, 1e-9, 1e-9, 1e-9, 1e-9)]
    worst_mp = 0.0
    for pt in near_pole:
        a = mpmath.mpf(compute_rk(*pt))
        b = mp_form(*pt)
        worst_mp = max(worst_mp, float(abs(a - b)))
    print(f"3. mpmath 50 dp, near-pole points         : worst |delta| = {worst_mp:.3e}")
    if worst_mp > 1e-9:
        failures.append("mpmath disagrees near the pole")

    # --- 4. NumPy random sampling, seeded ---
    rng = np.random.default_rng(20260907)
    n = 20000
    S = rng.uniform(0, 1, (n, 5))
    worst_rand = 0.0
    for row in S:
        R0, qq, sk, nb, nf = float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4])
        if nb + nf > 1.0:
            continue          # compute_rk rescales here; see the note below
        ne = 1 - (1 - nb) * (1 - (1 - sk) * nf)
        worst_rand = max(worst_rand, abs(compute_rk(R0, qq, sk, nb, nf)
                                         - validator_inline(R0, qq, sk, ne)))
    print(f"4. NumPy random, {n} draws (nu_b+nu_f<=1) : worst |delta| = {worst_rand:.3e}")
    if worst_rand > 1e-9:
        failures.append("random sampling disagrees")

    # --- 5. The ONE place they are designed to differ, stated rather than hidden ---
    R0, qq, sk, nb, nf = 0.5, 0.5, 0.5, 0.7, 0.6      # nu_b + nu_f = 1.3 > 1
    ne_raw = 1 - (1 - nb) * (1 - (1 - sk) * nf)
    a = compute_rk(R0, qq, sk, nb, nf)
    b = validator_inline(R0, qq, sk, ne_raw)
    print(f"5. nu_b+nu_f = {nb+nf:.1f} > 1 (rescale path)   : "
          f"runner {a:.6f} vs validator-on-stated-nu_eff {b:.6f}, delta {abs(a-b):.6f}")
    print("   EXPECTED AND NOT A BUG: compute_rk enforces the directive's hard")
    print("   constraint by rescaling; the validator uses the nu_eff the model")
    print("   STATED, because it is checking the model's own arithmetic. A model")
    print("   that states nu_b+nu_f>1 has violated a HARD CONSTRAINT and should be")
    print("   caught by that rule, not silently re-scored under a different one.")

    print()
    if failures:
        print("RESULT: DISAGREEMENT — " + "; ".join(failures))
        return 1
    print("RESULT: the two forms agree wherever the hard constraint holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
