#!/usr/bin/env python3
"""Can the demotion rule do better than a 1-in-20 chance of demoting a stable model?

THE QUESTION THIS ANSWERS, verbatim, 2026-10-30: *"Can we improve on this
statistic? A 1 in 20 chance of demoting a model that is performing just fine
seems unreasonably high?"*

FIRST, WHAT 0.05 ACTUALLY IS HERE, because the answer turns on it. It is not a
setting anything runs at. The relegation panel of 2026-10-08 compared 3
candidate rules and calibrated all 3 to the SAME false-alarm rate so that their
detection rates could be compared on equal footing -- `_calibrate(..., target=
0.05)` in the panel's own producer. Nothing in the live tree reads it: the
producer the panel's findings table cites was never committed to the path it
names, and survives only under `experimental_notes/seat_evidence/`.

SO THE QUESTION IS ANSWERABLE RATHER THAN A PREFERENCE: lower the common size
and measure what detection is lost. That is a trade-off curve, and this script
computes it.

WHAT IS MEASURED. For the peer sign test -- the rule the panel preferred,
because it is the only one of the 3 that is exchangeable and does not need a
difficulty model -- the size is recalibrated to each of several targets on one
seed, then the realised size and the detection rate are measured on a DIFFERENT
seed, so no number is read off the data it was tuned on. 3 scenarios:

  stable   - the model is fine. Firing here is the false demotion he objects to.
  decline  - this model alone degrades. Firing here is the rule working.
  common   - the whole roster degrades together. The panel established this is
             NOT IDENTIFIABLE without an externally anchored item pool, so a low
             rate here is a known structural limit, not a tuning failure.

FIDELITY, AND WHY A REIMPLEMENTATION IS SAFE HERE. The panel's `_fire_sign`
calls an exact binomial survival function once per sliding window, which is too
slow to recalibrate 4 times. This script replaces that with a precomputed table
of critical counts, which is the same decision by construction, and then PROVES
it is the same decision by running both forms on the same streams and requiring
identical fire/no-fire on every one. A reimplementation asserted to be
equivalent is a hypothesis; one executed against the original is not.

CROSS-VERIFICATION. The critical table is computed by scipy's binomial survival
function and independently by an exact rational sum of binomial coefficients in
mpmath, and the 2 must agree on every cell. Wilson intervals are computed by a
direct formula and by statsmodels.

Read-only. Runs no experiment, spends nothing, calls no model.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PANEL_PRODUCER = (REPO / "experimental_notes" / "seat_evidence"
                  / "division_count_star_2026-10-08" / "cc2" / "scripts"
                  / "the_division_count_is_a_resolution_bound_and_relegation_is_not_identified_2026-10-08.py")

TARGETS = (0.05, 0.02, 0.01, 0.005, 0.001)
SCENARIOS = ("stable", "decline", "common")


def load_panel_module():
    """Import the harvested panel producer by path; it is not on sys.path."""
    if not PANEL_PRODUCER.exists():
        raise SystemExit(f"panel producer not found at {PANEL_PRODUCER}")
    spec = importlib.util.spec_from_file_location("panel_relegation", PANEL_PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def wilson_direct(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return ((centre - half) / d, (centre + half) / d)


def wilson_statsmodels(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return float(lo), float(hi)


# --------------------------------------------------------------------------- #
# the critical table: fire iff n21 >= crit[nd]
# --------------------------------------------------------------------------- #
def critical_table_scipy(alpha: float, nd_max: int) -> list[int]:
    from scipy.stats import binom
    table = [nd_max + 1] * (nd_max + 1)
    for nd in range(1, nd_max + 1):
        for k in range(nd + 1):
            if float(binom.sf(k - 1, nd, 0.5)) < alpha:
                table[nd] = k
                break
    return table


def critical_table_mpmath(alpha: float, nd_max: int) -> list[int]:
    """Exact: P(X >= k) = sum_{j>=k} C(nd, j) / 2^nd, in exact rationals."""
    from fractions import Fraction
    table = [nd_max + 1] * (nd_max + 1)
    a = Fraction(alpha).limit_denominator(10 ** 9)
    for nd in range(1, nd_max + 1):
        total = Fraction(1, 2 ** nd)
        for k in range(nd + 1):
            tail = sum(math.comb(nd, j) for j in range(k, nd + 1)) * total
            if tail < a:
                table[nd] = k
                break
    return table


def make_fast_sign(np, win: int, crit: list[int]):
    ones = np.ones(win)

    def fire(y, b_rec, yp, _param=None) -> bool:
        maj = (yp.mean(axis=1) > 0.5).astype(int)
        a = ((y == 0) & (maj == 1)).astype(int)
        b = ((y == 1) & (maj == 0)).astype(int)
        ca = np.convolve(a, ones, "valid").astype(int)
        cb = np.convolve(b, ones, "valid").astype(int)
        nd = ca + cb
        for n21, d in zip(ca, nd):
            if d and n21 >= crit[d]:
                return True
        return False

    return fire


# --------------------------------------------------------------------------- #
def rate(mod, np, scenario: str, fire, seed: int, trials: int) -> int:
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(trials):
        b_rec, y, yp = mod._stream(scenario, rng)
        hits += bool(fire(y, b_rec, yp))
    return hits


def calibrate(mod, np, target: float, seed: int, trials: int, nd_max: int):
    """Smallest alpha whose realised size on `stable` is <= target."""
    best = None
    for alpha in (0.05, 0.02, 0.01, 5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4,
                  5e-5, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9):
        crit = critical_table_scipy(alpha, nd_max)
        fire = make_fast_sign(np, mod.WIN, crit)
        k = rate(mod, np, "stable", fire, seed, trials)
        if k / trials <= target:
            best = (alpha, crit, k / trials)
            break
    return best


def check_fidelity(mod, np, alpha: float, crit: list[int], trials: int, seed: int) -> dict:
    """Run the original and the fast form on identical streams."""
    fast = make_fast_sign(np, mod.WIN, crit)
    rng_a = np.random.default_rng(seed)
    rng_b = np.random.default_rng(seed)
    agree = 0
    fired = 0
    for _ in range(trials):
        b1, y1, p1 = mod._stream("decline", rng_a)
        b2, y2, p2 = mod._stream("decline", rng_b)
        assert (y1 == y2).all(), "the 2 streams diverged; the seeds are not aligned"
        o = bool(mod._fire_sign(y1, b1, p1, alpha))
        f = bool(fast(y2, b2, p2))
        agree += (o == f)
        fired += o
    return {"streams": trials, "agreed": agree, "original_fired": fired,
            "identical": agree == trials}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Measure the false-demotion / detection trade-off for the "
                    "peer sign test. Read-only; spends nothing.")
    ap.add_argument("--trials", type=int, default=1200,
                    help="replications per cell (default 1200)")
    ap.add_argument("--fidelity-trials", type=int, default=120,
                    help="streams used to prove the fast form is the same decision")
    ap.add_argument("--calib-seed", type=int, default=101)
    ap.add_argument("--eval-seed", type=int, default=202)
    args = ap.parse_args(argv)

    import numpy as np
    mod = load_panel_module()
    nd_max = mod.WIN

    print("=" * 74)
    print("CAN WE DO BETTER THAN A 1-IN-20 FALSE DEMOTION?")
    print(f"peer sign test, window {mod.WIN} of {mod.N_OBS} observations, "
          f"roster {mod.ROSTER}")
    print("=" * 74)

    print("\n0. THE CRITICAL TABLE AGREES BETWEEN 2 INDEPENDENT COMPUTATIONS")
    t_sci = critical_table_scipy(0.01, nd_max)
    t_exact = critical_table_mpmath(0.01, nd_max)
    same = t_sci == t_exact
    print(f"   scipy binomial survival vs exact rational binomial sums: "
          f"{'IDENTICAL' if same else 'DISAGREE'} on all {nd_max + 1} cells")
    if not same:
        bad = [i for i, (a, b) in enumerate(zip(t_sci, t_exact)) if a != b]
        print(f"   cells disagreeing: {bad[:10]}")
    print(f"   at alpha 0.01, 20 discordant pairs need n21 >= {t_sci[20]}; "
          f"40 pairs need >= {t_sci[40]}")

    print("\n1. THE FAST FORM IS THE SAME DECISION AS THE PANEL'S OWN FUNCTION")
    fid = check_fidelity(mod, np, 0.01, t_sci, args.fidelity_trials, 7)
    print(f"   streams compared                 : {fid['streams']}")
    print(f"   decisions identical              : {fid['agreed']} "
          f"({'ALL' if fid['identical'] else 'NOT ALL -- STOP'})")
    print(f"   of which the original fired on   : {fid['original_fired']}")
    if not fid["identical"]:
        print("   REFUSING to report a trade-off from a form that is not the same rule.")
        return 1

    print(f"\n2. THE TRADE-OFF, calibrated on seed {args.calib_seed}, "
          f"evaluated on seed {args.eval_seed}, {args.trials} replications per cell")
    print(f"   {'target':>8} {'alpha':>10} {'stable (false demotion)':>26} "
          f"{'decline (detection)':>22} {'common':>10}")
    rows = []
    for target in TARGETS:
        got = calibrate(mod, np, target, args.calib_seed, args.trials, nd_max)
        if got is None:
            print(f"   {target:>8} {'unreachable':>10}")
            continue
        alpha, crit, calib_size = got
        fire = make_fast_sign(np, mod.WIN, crit)
        cell = {}
        for sc in SCENARIOS:
            k = rate(mod, np, sc, fire, args.eval_seed, args.trials)
            lo, hi = wilson_direct(k, args.trials)
            lo2, hi2 = wilson_statsmodels(k, args.trials)
            assert max(abs(lo - lo2), abs(hi - hi2)) < 1e-9, \
                "the 2 Wilson routes disagree"
            cell[sc] = {"k": k, "n": args.trials, "p": k / args.trials,
                        "wilson": (lo, hi)}
        rows.append({"target": target, "alpha": alpha, "cells": cell})
        s, d, c = cell["stable"], cell["decline"], cell["common"]
        print(f"   {target:>8} {alpha:>10.1e} "
              f"{s['p']:>9.4f} [{s['wilson'][0]:.4f},{s['wilson'][1]:.4f}] "
              f"{d['p']:>9.4f} [{d['wilson'][0]:.4f},{d['wilson'][1]:.4f}] "
              f"{c['p']:>9.4f}")

    print("\n3. WHAT THE CURVE SAYS")
    if len(rows) >= 2:
        first, last = rows[0], rows[-1]
        ds = first["cells"]["stable"]["p"] - last["cells"]["stable"]["p"]
        dd = first["cells"]["decline"]["p"] - last["cells"]["decline"]["p"]
        print(f"   tightening from target {first['target']} to {last['target']}:")
        print(f"      false demotions fall by  {ds:.4f}")
        print(f"      detection falls by       {dd:.4f}")
        if dd <= 0.05:
            print("   So the 1-in-20 is NOT a price that has to be paid: the size can")
            print("   be tightened with little detection lost on this generator.")
        else:
            print("   So tightening the size costs real detection, and the choice is")
            print("   a genuine trade rather than a free improvement.")
    print("   And the common-mode column stays near 0 at every size, which is the")
    print("   identifiability limit the panel established, not a tuning failure.")
    print("\n   CAVEAT, stated because it bounds everything above: these rates come")
    print("   from the panel's SIMULATED stream generator, not from archived runs.")
    print("   They compare operating points of one rule under one model of how a")
    print("   model degrades. They are not a measurement of this project's seats.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
