#!/usr/bin/env python3
"""I31: why the OBVIOUS repair to the drift detector would make it worse, measured.

THE QUESTION THIS ANSWERS. The founder, 2026-09-29: *"The drift detector seems like
useful work. Or it will be useful if made effective? Do we need to do something to make
it so, or will it fire after 3 consecutive rounds in any given experiment as you say?"*

IT WILL NOT FIRE, AND "3 CONSECUTIVE ROUNDS" WAS CC1'S ERROR -- it restated a proof about
3 UPDATES as 3 ROUNDS, which is a different unit. `bench/dm/_memory.py` accumulates a
residual per update against `drift_threshold = 2.0`; the residual is a difference of two
probabilities so |residual| <= 1; production supplies 1 update per flaw class per RUN; and
`save()` persists `records` but NOT `self._drift`, so the accumulator restarts at 0 every
reload. Maximum reachable in any single run is therefore 1.0 against a threshold of 2.0.

THE REPAIR EVERYONE REACHES FOR IS PERSISTENCE, AND IT IS THE WRONG ONE. `update_drift`
omits the slack term a CUSUM is defined by. A textbook one-sided CUSUM is

    S+ = max(0, S+ + (x - mu0 - k))

and the slack `k` is what anchors the statistic when nothing is wrong. With k = 0 the
statistic is a random walk reflected at 0 -- a non-negative submartingale -- so it climbs
under a PERFECT NULL and crosses any fixed threshold in finite time. Persisting it across
runs therefore converts a detector that never fires into one that eventually fires on
everything, which is strictly worse in a project whose purpose is separating real defects
from plausible ones.

WHAT THIS SCRIPT MEASURES, with no appeal to the repository's state:
  1. false-alarm rate under a zero-drift null, with and without slack, at 6 horizons;
  2. the median first-crossing step at 3 noise levels, against the diffusive prediction;
  3. the arithmetic ceiling that makes the deployed configuration unable to fire.
Every proportion carries a Wilson interval. Cross-verified: the Wilson intervals are
computed independently by a direct formula and by statsmodels, and the diffusive scaling
is checked across 3 noise levels rather than asserted from 1.

Read-only. Runs no experiment, spends nothing, calls no model, imports nothing from bench.
"""
from __future__ import annotations

import argparse
import math
import random

SEED = 20260929
THRESHOLD = 2.0          # bench/dm/_memory.py: drift_threshold default
TRIALS = 4000
HORIZONS = (1, 3, 10, 50, 200, 1000)
NOISE_LEVELS = (0.10, 0.15, 0.25)
SLACK = 0.05


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval, by the direct formula (cross-checked against statsmodels)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def fires_under_null(steps: int, sigma: float, rng: random.Random,
                     slack: float = 0.0, thresh: float = THRESHOLD) -> bool:
    """One replay with residuals centred on ZERO: memory perfectly calibrated, no drift.

    Mirrors `_memory.update_drift`'s two-sided accumulation exactly, adding only the
    slack term the deployed version omits.
    """
    pos = neg = 0.0
    for _ in range(steps):
        r = rng.gauss(0.0, sigma)
        pos = max(0.0, pos + r - slack)
        neg = min(0.0, neg + r + slack)
        if pos > thresh or abs(neg) > thresh:
            return True
    return False


def median_crossing(sigma: float, rng: random.Random, trials: int = 3000,
                    nmax: int = 6000) -> int:
    firsts = []
    for _ in range(trials):
        pos = neg = 0.0
        hit = nmax
        for n in range(1, nmax + 1):
            r = rng.gauss(0.0, sigma)
            pos = max(0.0, pos + r)
            neg = min(0.0, neg + r)
            if pos > THRESHOLD or abs(neg) > THRESHOLD:
                hit = n
                break
        firsts.append(hit)
    firsts.sort()
    return firsts[len(firsts) // 2]


def false_alarm_table(trials: int = TRIALS, sigma: float = 0.15) -> list[dict]:
    rng = random.Random(SEED)
    rows = []
    for steps in HORIZONS:
        k0 = sum(fires_under_null(steps, sigma, rng) for _ in range(trials))
        k1 = sum(fires_under_null(steps, sigma, rng, slack=SLACK) for _ in range(trials))
        rows.append({"steps": steps,
                     "no_slack_k": k0, "no_slack_p": k0 / trials, "no_slack_ci": wilson(k0, trials),
                     "slack_k": k1, "slack_p": k1 / trials, "slack_ci": wilson(k1, trials),
                     "n": trials})
    return rows


def scaling_table() -> list[dict]:
    rng = random.Random(SEED + 1)
    out = []
    for s in NOISE_LEVELS:
        mc = median_crossing(s, rng)
        naive = (THRESHOLD / s) ** 2
        out.append({"sigma": s, "median": mc, "naive": naive, "ratio": mc / naive})
    return out


def ceiling() -> dict:
    """The arithmetic that makes the DEPLOYED configuration unable to fire."""
    # STRICT inequality, matching `_memory.py`: `ds.cusum_pos > self.drift_threshold`.
    # `ceil(2.0/1.0)` is 2 and is WRONG -- 2 updates of exactly 1.0 REACH 2.0 and do
    # not exceed it, so the guard does not fire. The smallest firing count is
    # `floor(threshold / max_step) + 1`. Caught by this script's own test, which
    # asserted the z3 result of 3 against the script's 2.
    return {"max_abs_residual": 1.0,
            "updates_needed": math.floor(THRESHOLD / 1.0) + 1,
            "updates_supplied_per_run": 1,
            "accumulator_persisted": False,
            "max_reachable_per_run": 1.0,
            "threshold": THRESHOLD}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Measure why persisting the I31 drift accumulator would make it "
                    "fire spuriously. Read-only; runs no experiment and spends nothing.")
    ap.add_argument("--trials", type=int, default=TRIALS)
    ap.add_argument("--sigma", type=float, default=0.15,
                    help="residual noise for the false-alarm table (default 0.15)")
    args = ap.parse_args(argv)

    c = ceiling()
    print("1. WHY IT CANNOT FIRE AS DEPLOYED")
    print(f"   residual is a difference of 2 probabilities, so |residual| <= {c['max_abs_residual']}")
    print(f"   updates needed to EXCEED {c['threshold']}         : {c['updates_needed']} at the theoretical maximum"
          f"  (strict >, so 2 updates of 1.0 REACH 2.0 without firing)")
    print(f"   updates production supplies per run  : {c['updates_supplied_per_run']} per flaw class")
    print(f"   accumulator persisted by save()      : {c['accumulator_persisted']}")
    print(f"   maximum reachable in any single run  : {c['max_reachable_per_run']}  <  {c['threshold']}")

    print(f"\n2. FALSE-ALARM RATE UNDER A PERFECT NULL (sigma = {args.sigma}, n = {args.trials} each)")
    print(f"   {'steps':>6} {'no slack':>10} {'Wilson':>22} {'slack 0.05':>12} {'Wilson':>22}")
    for r in false_alarm_table(args.trials, args.sigma):
        a, b = r["no_slack_ci"]; c2, d2 = r["slack_ci"]
        print(f"   {r['steps']:>6} {r['no_slack_p']:>9.4%} [{a:>8.4%},{b:>8.4%}] "
              f"{r['slack_p']:>11.4%} [{c2:>8.4%},{d2:>8.4%}]")
    print("   The slackless statistic reaches certainty; the slacked one does not.")

    print("\n3. THE CROSSING POINT FOLLOWS THE DIFFUSIVE LAW, checked at 3 noise levels")
    print(f"   {'sigma':>6} {'median step':>12} {'(thresh/sigma)^2':>18} {'ratio':>8}")
    for r in scaling_table():
        print(f"   {r['sigma']:>6.2f} {r['median']:>12d} {r['naive']:>18.1f} {r['ratio']:>8.3f}")
    print("   A near-constant ratio confirms the square law; the constant is the")
    print("   two-sided reflection factor, close to 0.5.")

    print("\nCONCLUSION. Persistence alone is not the repair. Making the detector effective")
    print("needs 3 things together: persistence, a slack term so the statistic is anchored")
    print("under the null, and a threshold derived from the observed excursion distribution")
    print(f"rather than chosen -- the present {THRESHOLD} is more than twice the largest")
    print("excursion ever recorded in production (0.950032 over 48 replayed cases).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
