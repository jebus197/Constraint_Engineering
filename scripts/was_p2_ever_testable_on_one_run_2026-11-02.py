#!/usr/bin/env python3
"""P2 of the pre-registration was UNDER-POWERED BY CONSTRUCTION. I should have known.

WHAT HAPPENED. On 2026-11-02 I pre-registered 4 predictions for the simulated
validation run and committed them before it launched, which is the right form.
For 1 of them -- P2, that confirmed severities outrank refuted ones -- I never
checked whether a single run could produce enough REFUTED findings to decide it.
I had done exactly that calculation for the disagreement rate (289 findings) in
`scripts/how_many_simulated_runs_for_the_severity_defaults_2026-11-01.py` and
simply did not do it here.

THE PRE-REGISTRATION IS NOT AMENDED. It stays as committed, because a
pre-registration edited after the fact is worth nothing. This is a separate,
later finding about it.

AND IT CORRECTS A CLAIM I ALMOST MADE. Seeing 13 CONFIRMED and 0 REFUTED in the
live run, my first reading was that simulated seats never produce refutations --
a neater and far better-founded version of my original claim that a simulated run
cannot validate a severity design. THE ARCHIVE REFUTES IT: simulated runs refute
at 10 of 564 decided, 1.7730%, against real runs at 16 of 545, 2.9358%, and the
difference is not significant. The 0 of 13 is ordinary sampling.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
AUC_ASSUMED = 0.80          # the archive's measured value, 0.800922
N_CONFIRMED_ASSUMED = 60    # a run of the blocked one's size
FAILURES: list[str] = []


def archive_rates() -> dict:
    agg = collections.defaultdict(collections.Counter)
    for d in sorted(LOGS.iterdir()):
        f = d / "runner_state.json"
        if not f.is_file():
            continue
        try:
            s = json.loads(f.read_text())
        except Exception:                                      # noqa: BLE001
            continue
        seats = sorted(s.get("raw_counts_per_model") or {})
        if not seats:
            continue
        kind = "SIM" if any("sim" in x.lower() for x in seats) else "REAL"
        e = (s.get("registry") or {}).get("entries") or {}
        items = list(e.values()) if isinstance(e, dict) else list(e)
        agg[kind] += collections.Counter(
            str(x.get("falsifier_verdict") or "") for x in items)
    return agg


def hm_lower(auc: float, n1: int, n2: int) -> float:
    q1, q2 = auc / (2 - auc), 2 * auc ** 2 / (1 + auc)
    se = float(np.sqrt((auc * (1 - auc) + (n1 - 1) * (q1 - auc ** 2)
                        + (n2 - 1) * (q2 - auc ** 2)) / (n1 * n2)))
    return auc - stats.norm.ppf(0.975) * se


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="was_p2_ever_testable_on_one_run_2026-11-02.py",
        description="Was the pre-registered ordering prediction decidable at the "
                    "sample size one run produces? Reads the archive only.")
    ap.parse_args()

    agg = archive_rates()
    print("=" * 72)
    print("PART 1. DO SIMULATED RUNS PRODUCE REFUTATIONS AT ALL?")
    print("=" * 72)
    tbl = []
    for kind in ("REAL", "SIM"):
        c = agg[kind]
        conf, refu = c.get("CONFIRMED", 0), c.get("REFUTED", 0)
        dec = conf + refu
        tbl.append([refu, conf])
        lo, hi = proportion_confint(refu, dec, alpha=0.05, method="wilson")
        lo2, hi2 = proportion_confint(refu, dec, alpha=0.05, method="beta")
        print(f"  {kind:4s}: {refu} refuted of {dec} decided = {refu/dec:.6f}")
        print(f"        Wilson 95%          [{lo:.6f}, {hi:.6f}]  statsmodels")
        print(f"        Clopper-Pearson 95% [{lo2:.6f}, {hi2:.6f}]  scipy/beta")
    arr = np.array(tbl)
    odr, pf = stats.fisher_exact(arr)
    chi = stats.chi2_contingency(arr)
    print(f"\n  Fisher exact p = {pf:.6e}   chi-square p = {chi.pvalue:.6e}")
    if pf < 0.05:
        FAILURES.append("the 2 refutation rates now DIFFER significantly, so the "
                        "claim that simulation refutes like a real run is withdrawn")
    print("  -> the 2 rates are NOT distinguishable, so simulation does produce")
    print("     refutations and the live run's 0 of 13 is ordinary sampling.")
    sim_rate = agg["SIM"].get("REFUTED", 0) / (agg["SIM"].get("REFUTED", 0)
                                               + agg["SIM"].get("CONFIRMED", 0))

    print()
    print("=" * 72)
    print("PART 2. HOW MANY REFUTATIONS P2 NEEDED, AND HOW MANY A RUN YIELDS")
    print("=" * 72)
    need = next((n2 for n2 in range(1, 400)
                 if hm_lower(AUC_ASSUMED, N_CONFIRMED_ASSUMED, n2) > 0.5), None)
    assert need is not None, "no refutation count decides P2; check the model"
    print(f"  minimum refuted findings for P2 to clear chance at AUC "
          f"{AUC_ASSUMED}: {need}")
    for n2 in (1, 2, 3, 5, 10, 16):
        lo = hm_lower(AUC_ASSUMED, N_CONFIRMED_ASSUMED, n2)
        print(f"    {n2:2d} refuted -> 95% lower bound {lo:.4f} "
              f"{'clears' if lo > 0.5 else 'does NOT clear'} 0.5")
    print()
    for n in (13, 40, 75, 150, 300):
        exp = n * sim_rate
        p0 = float(stats.binom.pmf(0, n, sim_rate))
        pn = float(stats.binom.sf(need - 1, n, sim_rate))
        print(f"    {n:4d} decided -> expected {exp:5.2f} refutations, "
              f"P(zero) = {p0:.4f}, P(enough for P2) = {pn:.4f}")
    n_need = int(np.ceil(need / sim_rate))
    print()
    print(f"  SO P2 NEEDS ABOUT {n_need} DECIDED FINDINGS, roughly "
          f"{n_need/75:.1f} runs the size of the blocked one.")
    print("  A single run of 75 has a 26% chance of producing ZERO refutations.")
    print()
    print("  WHAT THIS DOES NOT SAY: that a PAID run would help. It would not --")
    print("  the real refutation rate is 2.9358%, so a paid run of 75 yields about")
    print("  2.2 refutations and is barely better. The archive, with 545 decided")
    print("  findings and 16 refutations, is where this property is measurable,")
    print("  which is what he said and what I argued against.")

    print()
    print("=" * 72)
    print(f"FAILURES: {len(FAILURES)}")
    for f in FAILURES:
        print("  -", f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
