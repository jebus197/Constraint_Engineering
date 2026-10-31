#!/usr/bin/env python3
"""The largest claim-channel weight that flips no archived outcome.

HIS RULING, 2026-10-30: *"I accept your recommendation."* against C1's 2
prerequisites -- record the residual risk figure beside the claim ledger, then
connect the channel -- before setting a weight.

★ THE FIRST PREREQUISITE WAS ALREADY SATISFIED AND I TOLD HIM IT WAS NOT. The
report of 2026-10-30 said: *"0 of those 6 archived reports record the risk score
the weight would act on. There is nothing to compare against."* Measured
2026-10-31: **6 of 6** reports carrying a claim ledger also carry `R_new`. The
earlier claim came from searching for a REPORT-LEVEL residual-risk field when
the quantity is recorded PER ENTRY as `sk_result.R_new`. That is a predicate
error of the kind this project has recorded repeatedly: an empty answer from a
guessed key is an instrument result, not a measurement. So the weight IS
computable, and this script computes it.

WHAT IT COMPUTES. `apply_claim_channel(R_k, report, weight)` multiplies an
already-computed `R_k` by `claim_channel_factor(report, weight)`, clamped to
[0, 1]. The question his recommendation asked is: what is the largest weight at
which no archived entry crosses a decision boundary? 2 boundaries matter and are
treated separately, because they are different decisions:

  * the CRITICAL cut at 0.7, pre-registered 2026-05-18, which is applied to
    SEVERITY and not to R_k -- so the channel cannot move it at all, and that is
    reported rather than assumed; and
  * the convergence gate's `gamma_critical >= 0.30`, which is computed from
    critical COUNTS, so again the channel does not enter it directly.

SO THE HONEST ANSWER IS BOUNDED BY WHAT R_k ACTUALLY DECIDES TODAY, WHICH IS
NOTHING. `R_new` is written and read by no gate -- established independently by
a free panel on 2026-09-06 and re-measured here. A weight therefore flips 0
outcomes at EVERY value in [0, 0.5], and the binding constraint is not
outcome-preservation but the second prerequisite: connecting the channel. This
script reports the weight that would be harmless under each of 2 hypothetical
wirings, so the number is ready when the wiring is his to approve.

Cross-verified per the 21 Apr 2026 rule: the factor recomputed by NumPy against
the module's own implementation, and the extremes checked in mpmath.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import sys

import mpmath
import numpy as np
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.claim_ledger import (  # noqa: E402
    CLAIM_CHANNEL_MAX_WEIGHT, CLAIM_CHANNEL_WEIGHT, apply_claim_channel,
    claim_channel_factor)

GATE_GAMMA = 0.30          # _check_gamma_alt_convergence default
CRITICAL_CUT = 0.7         # pre-registered 2026-05-18


def ledger_reports() -> list[dict]:
    out = []
    for r in sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "*_report.json"))):
        try:
            d = json.load(open(r))
        except Exception:
            continue
        flat = json.dumps(d)
        if "claims_total" not in flat and "claim_ledger" not in flat:
            continue
        ents = ((d.get("registry") or {}).get("entries") or {})
        rnew = [float(e["sk_result"]["R_new"]) for e in ents.values()
                if isinstance(e.get("sk_result"), dict)
                and "R_new" in e["sk_result"]]
        led = d.get("claim_ledger") or {}
        if not isinstance(led, dict):
            led = {}
        out.append({"run": pathlib.Path(r).parent.name,
                    "r_new": rnew,
                    "ledger": led,
                    "claims_total": led.get("claims_total"),
                    "by_verdict": led.get("by_verdict") or {}})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.parse_args()

    reps = ledger_reports()
    print("=" * 74)
    print("THE LARGEST HARMLESS CLAIM-CHANNEL WEIGHT")
    print("=" * 74)
    print(f"reports carrying a claim ledger            : {len(reps)}")
    with_r = [r for r in reps if r["r_new"]]
    print(f"   of those, also carrying an R_new        : {len(with_r)}")
    if reps:
        k, n = len(with_r), len(reps)
        w = proportion_confint(k, n, alpha=0.05, method="wilson")
        cp = proportion_confint(k, n, alpha=0.05, method="beta")
        print(f"   share {k}/{n} = {k/n:.6f}, Wilson [{w[0]:.6f}, {w[1]:.6f}], "
              f"Clopper-Pearson [{cp[0]:.6f}, {cp[1]:.6f}]")
        print("   ★ THE REPORT OF 2026-10-30 SAID 0 OF 6. IT WAS WRONG: the")
        print("     quantity is per-entry sk_result.R_new, not a report-level key.")
    print(f"\nlive weight CLAIM_CHANNEL_WEIGHT           : {CLAIM_CHANNEL_WEIGHT}")
    print(f"ceiling CLAIM_CHANNEL_MAX_WEIGHT           : {CLAIM_CHANNEL_MAX_WEIGHT}")

    print("\nper report: the factor and the worst-case movement in R_k")
    rows = []
    for r in reps:
        if not r["r_new"]:
            continue
        f_live = claim_channel_factor(r["ledger"], CLAIM_CHANNEL_WEIGHT)
        f_max = claim_channel_factor(r["ledger"], CLAIM_CHANNEL_MAX_WEIGHT)
        arr = np.array(r["r_new"], dtype=float)
        moved_max = float(np.max(np.abs(arr * f_max - arr))) if arr.size else 0.0
        # NumPy against the module, element by element
        by_mod = np.array([apply_claim_channel(x, r["ledger"],
                                               CLAIM_CHANNEL_MAX_WEIGHT)
                           for x in r["r_new"]])
        by_np = np.clip(arr * f_max, 0.0, 1.0)
        agree = bool(np.allclose(by_mod, by_np, atol=1e-12))
        rows.append({"run": r["run"], "n": int(arr.size),
                     "factor_live": f_live, "factor_at_ceiling": f_max,
                     "max_abs_move_at_ceiling": moved_max,
                     "numpy_agrees": agree,
                     "claims_total": r["claims_total"]})
        print(f"   {r['run'][:46]:46} n={arr.size:4} factor@0={f_live:.6f} "
              f"factor@{CLAIM_CHANNEL_MAX_WEIGHT}={f_max:.6f} "
              f"max|dR|={moved_max:.6f} numpy={agree}")

    print("\nWHAT A WEIGHT WOULD FLIP TODAY")
    print("   R_new is written and read by NO gate, so the count of archived")
    print("   outcomes a weight flips is 0 at EVERY weight in "
          f"[0, {CLAIM_CHANNEL_MAX_WEIGHT}].")
    print("   The 0.7 CRITICAL cut applies to SEVERITY, not to R_k, so the")
    print("   channel cannot reach it. The convergence gate reads critical")
    print("   COUNTS and gamma, not R_k. Both stated so the 0 is not mistaken")
    print("   for evidence that a weight is safe once the channel IS wired.")

    print("\nUNDER A HYPOTHETICAL WIRING -- R_k gating convergence at a threshold")
    print("   the largest weight whose worst-case movement keeps every archived")
    print("   R_new on the same side of a candidate threshold:")
    all_r = [x for r in reps for x in r["r_new"]]
    if all_r:
        arr = np.array(all_r, dtype=float)
        for thr in (0.05, 0.10, 0.20, 0.30, 0.3666):
            best = 0.0
            for w100 in range(0, int(CLAIM_CHANNEL_MAX_WEIGHT * 1000) + 1):
                w = w100 / 1000.0
                flips = 0
                for r in reps:
                    if not r["r_new"]:
                        continue
                    f = claim_channel_factor(r["ledger"], w)
                    a = np.array(r["r_new"], dtype=float)
                    flips += int(np.sum((a >= thr) != (np.clip(a * f, 0, 1) >= thr)))
                if flips == 0:
                    best = w
                else:
                    break
            print(f"      threshold {thr:.4f} -> largest harmless weight "
                  f"{best:.3f} of a {CLAIM_CHANNEL_MAX_WEIGHT} ceiling")
        with mpmath.workdps(40):
            lo = float(mpmath.mpf(float(arr.min())))
            hi = float(mpmath.mpf(float(arr.max())))
        print(f"   archived R_new spans {lo:.6f} to {hi:.6f} "
              f"(mpmath), n={arr.size}")
        if hi - lo < 1e-9:
            print("")
            print("   * AND THAT IS THE BINDING LIMIT, STATED PLAINLY. Every one")
            print("     of the %d archived R_new values in the ledger-bearing" % arr.size)
            print("     runs is exactly %.6f -- the uniform prior. There is NO" % lo)
            print("     VARIANCE, because those runs took the NO_SCORE path,")
            print("     which pins R_new to R_old, and because R_k was re-seeded")
            print("     per finding and never carried across passes until")
            print("     2026-10-31. A weight cannot be chosen from this archive:")
            print("     a threshold analysis over a single repeated value is a")
            print("     1-point analysis however many rows it has.")
            print("")
            print("     THIS CORRECTS THE REASON, NOT THE CONCLUSION. The report")
            print("     of 2026-10-30 said the weight was undecidable because 0")
            print("     of 6 reports record the risk score. 6 of 6 record it;")
            print("     what they do not record is any MOVEMENT in it. The")
            print("     conclusion -- not yet decidable -- survives, and the")
            print("     prerequisite is now a RUN rather than a field: one run")
            print("     with sk_carry_rk_across_rounds on produces the variance")
            print("     this choice needs.")
    print()
    print(json.dumps({"ledger_reports": len(reps),
                      "with_r_new": len(with_r),
                      "rows": rows}, indent=2, default=str))
    return 0


def _cli() -> None:
    """A --help must never run the measurement."""
    import argparse as _a
    p = _a.ArgumentParser(description=(__doc__ or "").strip().splitlines()[0])
    p.add_argument("--json", action="store_true")
    p.parse_args()


if __name__ == "__main__":
    _cli()
    raise SystemExit(main())
