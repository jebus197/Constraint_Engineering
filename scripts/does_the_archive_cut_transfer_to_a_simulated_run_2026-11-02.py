#!/usr/bin/env python3
"""Does the archive-derived 0.7 severity cut transfer to a simulated run?

WHY. `scripts/the_severity_bounds_from_the_archive_2026-11-01.py` set
LIVE_CRITICAL_CUT = 0.7 from 28 real-seat runs, where it is Youden-optimal
(sensitivity 0.7316, specificity 0.8125, J 0.5441). Pre-registered prediction P3
of `experimental_notes/data/severity_bounds_prereg_2026-11-02.json` required
sensitivity above 0.5 on the validation run. It came in at 0.600000, which HELD
P3 and is visibly below 0.7316. This script decides whether that gap is a
finding or noise, BEFORE the gap is reported as either.

THE TRAP THIS AVOIDS. 0.600000 against 0.7316 reads like a 13-point shortfall and
would make a good sentence. At n = 20 it is not distinguishable from the archive
rate, and reporting the shortfall as a result would be the flattering-measure
failure this project has recorded 3 times. Equally, "the cut transfers" may NOT
be concluded: the same n cannot establish that either. The honest verdict is that
the run has no power on this question, and the script states the n that would.

TOOLS, 2 per claim per the 2026-04-21 rule.
    exact binomial test  : scipy.stats.binomtest vs an mpmath exact two-sided
                           tail, required to agree to 1e-9
    interval             : closed-form Wilson vs statsmodels proportion_confint,
                           required to agree to 1e-12
    power                : a normal-approximation closed form, REPORTED AS
                           APPROXIMATE because the closed form is known in this
                           project to run optimistic (the 63-adjudication figure
                           of 2026-10-29: closed form said 35, simulation said
                           0.6472 power at that n), cross-checked by simulation.

PROVENANCE CAVEAT, carried from the run's own log: severity provenance is
SIMULATED, so severity MAGNITUDES are uncalibrated against a real panel and do
not transfer. This script therefore tests the DECISION RATE at a fixed cut, not
the magnitudes, which is the only part of the comparison the provenance permits.
"""
from __future__ import annotations

import argparse
import sys

ARCHIVE_SENSITIVITY = 0.7316      # from the 28 real-seat-run archive, at cut 0.7
CUT = 0.7


def _wilson_closed(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (max(0.0, c - h), min(1.0, c + h))


def _exact_two_sided(k: int, n: int, p0: float) -> float:
    import mpmath as mp
    mp.mp.dps = 40

    def pmf(i):
        return (mp.binomial(n, i) * mp.mpf(p0) ** i
                * (1 - mp.mpf(p0)) ** (n - i))

    obs = pmf(k)
    tol = 1 + mp.mpf("1e-30")
    return float(sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs * tol))


def _n_for_power(p0: float, p1: float, power: float = 0.80) -> int:
    from scipy.stats import norm
    num = (norm.ppf(0.975) * (p0 * (1 - p0)) ** 0.5
           + norm.ppf(power) * (p1 * (1 - p1)) ** 0.5) ** 2
    return int(num / (p0 - p1) ** 2) + 1


def _simulated_power(p0: float, p1: float, n: int, draws: int = 20000) -> float:
    """The closed form is optimistic here by this project's own record, so the
    power figure that may be QUOTED is this one."""
    import numpy as np
    from scipy import stats
    rng = np.random.default_rng(20261102)
    ks = rng.binomial(n, p1, size=draws)
    # two-sided exact test at alpha 0.05, vectorised over the distinct k values
    rej = {k: stats.binomtest(int(k), n, p0).pvalue <= 0.05 for k in set(ks.tolist())}
    return float(np.mean([rej[int(k)] for k in ks]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--confirmed", type=int, default=20,
                    help="confirmed findings in the run (denominator)")
    ap.add_argument("--at-or-above-cut", type=int, default=12,
                    help="of those, how many carried severity >= the cut")
    ap.add_argument("--archive", type=float, default=ARCHIVE_SENSITIVITY)
    a = ap.parse_args()

    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint

    n, k, p0 = a.confirmed, a.at_or_above_cut, a.archive
    if n == 0:
        print("0 confirmed findings: this comparison is VACUOUS.")
        return 1
    p = k / n

    lo_c, hi_c = _wilson_closed(k, n)
    lo_s, hi_s = proportion_confint(k, n, alpha=0.05, method="wilson")
    iv_agree = abs(lo_c - lo_s) < 1e-12 and abs(hi_c - hi_s) < 1e-12

    p_scipy = stats.binomtest(k, n, p0, alternative="two-sided").pvalue
    p_mp = _exact_two_sided(k, n, p0)
    t_agree = abs(p_scipy - p_mp) < 1e-9

    print("=" * 76)
    print("DOES THE ARCHIVE-DERIVED 0.7 CUT TRANSFER TO A SIMULATED RUN?")
    print("=" * 76)
    print(f"\n  cut                  : {CUT}")
    print(f"  run sensitivity      : {k}/{n} = {p:.6f}")
    print(f"  archive sensitivity  : {p0:.4f}  (28 real-seat runs)")
    print(f"  Wilson 95% closed    : [{lo_c:.6f}, {hi_c:.6f}]")
    print(f"  Wilson 95% statsmod. : [{lo_s:.6f}, {hi_s:.6f}]   agree={iv_agree}")
    if not iv_agree:
        print("  ★ interval tools disagree; no interval may be quoted.")
        return 4
    print(f"  archive INSIDE the run's interval: {lo_c <= p0 <= hi_c}")
    print(f"\n  exact two-sided binomial vs {p0}:")
    print(f"      scipy  p = {p_scipy:.6f}")
    print(f"      mpmath p = {p_mp:.6f}")
    print(f"      agree to 1e-9: {t_agree}")
    if not t_agree:
        print("  ★ test tools disagree; no p-value may be quoted.")
        return 4

    n80 = _n_for_power(p0, p, 0.80)
    sim = _simulated_power(p0, p, n)
    sim80 = _simulated_power(p0, p, n80)
    print(f"\n  POWER at this run's size (n={n}), simulated : {sim:.6f}")
    print(f"  closed-form n for 80% power                 : {n80}  (APPROXIMATE)")
    print(f"  simulated power at that n                   : {sim80:.6f}")
    print(f"  runs of this size to reach it               : "
          f"{-(-n80 // max(1, n))}")

    print("\nVERDICT")
    if p_scipy > 0.05:
        print(f"  NOT DISTINGUISHABLE from the archive rate (p = {p_scipy:.6f}).")
        print(f"  The apparent shortfall from {p0} to {p:.6f} is within sampling")
        print(f"  noise at n={n}, so this run is NO evidence that the cut fails to")
        print("  transfer -- AND NO EVIDENCE THAT IT DOES. The run has power")
        print(f"  {sim:.6f} against the observed rate, so it could not have")
        print("  detected this difference even if it were real.")
        print("\n  WHAT THE 0.7 CUT IS STILL ENTITLED TO CLAIM: it is Youden-optimal")
        print("  on the archive, which is a real-seat corpus. The simulated run")
        print("  neither strengthens nor weakens that, and the run's own log")
        print("  records that simulated severity MAGNITUDES do not transfer.")
    else:
        print(f"  SIGNIFICANTLY BELOW the archive rate (p = {p_scipy:.6f}):")
        print("  the archive-derived cut may not transfer to simulated severities.")
    return 0


if __name__ == "__main__":
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
    # ★ THE HELP-INTERCEPTING CALL IS REMOVED, 2026-11-03. It answered
    # `--help` BEFORE this script's own parser ran, so argparse never listed
    # the flags: measured across the 6 scripts that had both, 0 of 16 defined
    # flags were visible. The comment that stood here recorded the same
    # finding on 2026-11-02 and tried to fix it with `takes_no_arguments=False`,
    # which stops the helper REFUSING a flag but not from answering `--help`
    # first. Removing the call is what actually reaches it, and argparse's own
    # help is enabled, so the capability is improved rather than lost.
    sys.exit(main())
