#!/usr/bin/env python3
"""Is the shipped S* biased LOW everywhere, or only where it clamps to zero?

WHY. The 2026-09-05 finding was that S* clamps to 0 at the default operating
point (q=0.5, R=0.5, nu_b=0.05, nu_f=0.20), where it evaluates to the exact
rational -1/19. That framing leaves open a benign reading: a clamping artefact at
one corner. Fable (panel, 2026-09-06) showed it is not -- at q=0.21, R=0.3 the
shipped S* is 0.9316, does not clamp, and the true break-even is 0.9478. This
measures whether the understatement is systematic across the reachable space.

The true break-even is the s solving compute_rk(R, q, s) == R exactly: the fix
that leaves residual risk unchanged. Anything below it RAISES risk. So a gate
whose threshold sits below the true break-even admits harmful fixes by
construction.

Cross-verified per the 2026-04-21 two-tool rule: scipy.optimize.brentq and
mpmath.findroot for every root; statsmodels and scipy for both intervals.

Run: python3 scripts/measure_sstar_understates_breakeven.py
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import mpmath as mp
import numpy as np
from scipy.optimize import brentq
from scipy.stats import beta as beta_dist
from statsmodels.stats.proportion import proportion_confint

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "bench" / "reference_runner_v3.py"


def _load_runner() -> types.ModuleType:
    mod = types.ModuleType("_rr")
    mod.__file__ = str(RUNNER)
    sys.modules["_rr"] = mod
    try:
        exec(compile(RUNNER.read_text(), str(RUNNER), "exec"), mod.__dict__)
    except SystemExit:
        pass
    return mod


def main() -> int:
    rr = _load_runner()
    compute_rk, check_sk = rr.compute_rk, rr.check_sk_threshold
    NU_B, NU_F = 0.05, 0.20        # the literal defaults at reference_runner_v3.py:9417

    rows, understated, admits_harm = [], 0, 0
    for q in np.linspace(0.05, 0.95, 19):
        for R in np.linspace(0.05, 0.95, 19):
            f = lambda s: compute_rk(float(R), float(q), s, NU_B, NU_F) - float(R)
            if f(0.0) * f(1.0) >= 0:
                continue                      # no interior break-even at this point
            true_be = brentq(f, 0.0, 1.0, xtol=1e-14)
            true_mp = float(mp.findroot(lambda s: compute_rk(float(R), float(q),
                                                             float(s), NU_B, NU_F) - float(R), 0.5))
            assert abs(true_be - true_mp) < 1e-9, (q, R, true_be, true_mp)
            _, shipped = check_sk(0.5, NU_B, NU_F, float(q), float(R))
            rows.append((q, R, shipped, true_be))
            if shipped < true_be - 1e-12:
                understated += 1
                # Does a fix in the admitted-but-harmful band actually exist?
                probe = (shipped + true_be) / 2.0
                passes, _ = check_sk(probe, NU_B, NU_F, float(q), float(R))
                if passes and compute_rk(float(R), float(q), probe, NU_B, NU_F) > float(R):
                    admits_harm += 1

    n = len(rows)
    print(f"Reachable grid points with an interior break-even: {n}")
    for label, k in (("shipped S* BELOW the true break-even", understated),
                     ("a harmful fix demonstrably admitted", admits_harm)):
        lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
        lo_cp, hi_cp = (beta_dist.ppf(0.025, k, n - k + 1) if k else 0.0,
                        beta_dist.ppf(0.975, k + 1, n - k) if k < n else 1.0)
        print(f"  {label}: {k} of {n} = {100*k/n:.2f}%  "
              f"Wilson [{100*lo_w:.2f}%, {100*hi_w:.2f}%]  "
              f"Clopper-Pearson [{100*lo_cp:.2f}%, {100*hi_cp:.2f}%]")

    gaps = [t - s for _, _, s, t in rows]
    print(f"  understatement gap: min {min(gaps):.6f}  median {np.median(gaps):.6f}  "
          f"max {max(gaps):.6f}")
    over = [(q, R, s, t) for q, R, s, t in rows if s > t + 1e-12]
    print(f"  grid points where shipped S* OVERstates (would be conservative): {len(over)}")
    print("\nWorked points:")
    for q, R in ((0.5, 0.5), (0.21, 0.3)):
        m = [r for r in rows if abs(r[0] - q) < 1e-9 and abs(r[1] - R) < 1e-9]
        if m:
            _, _, s, t = m[0]
            print(f"  q={q}, R={R}: shipped S* = {s:.6f}, true break-even = {t:.12f}, "
                  f"gap = {t - s:+.6f}")
    return 0 if understated == n else 1


if __name__ == "__main__":
    sys.exit(main())
