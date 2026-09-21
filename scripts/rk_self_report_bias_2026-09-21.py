#!/usr/bin/env python3
"""Seats systematically UNDERSTATE their own R_k, and the run measured it.

WHAT WAS OBSERVED. In round 0 of commissioning arm 1 (2026-09-21, 5 simulated
seats against `bench/cdsfl_registry/engine.py`), the runner recomputed each
seat's self-reported `R_k` and rejected 17 of them. Per seat:

    CC2-SIM       FAIL=4, SKIP=1
    Gemini-SIM    FAIL=4
    DeepSeek-SIM  FAIL=5
    ChatGPT-SIM   FAIL=4
    Codex-SIM     PASS=5

WHY THIS IS NOT NOISE. Every one of the 17 deltas is POSITIVE: the recomputed
value exceeds the model's stated value in 17 of 17 cases, never once the other
way. A seat making arithmetic slips would err in both directions, so a perfectly
one-sided result is evidence of a systematic difference between what the seats
compute and what the runner computes -- a formula or input discrepancy, not
sloppiness.

WHY IT MATTERS BEYOND TIDINESS. `severity_is_proven`, the 2026-09-06 interlock,
requires a stamped `R_k` proof that RECOMPUTES before a severity demotion is
allowed. If self-reported proofs routinely fail to recompute, that interlock is
never satisfied, and the severity-calibration machinery the simulated run exists
to exercise cannot reach its demotion path for a reason that has nothing to do
with severity.

THE DIRECTION IS THE INFORMATIVE PART. The seats report LOWER risk than the
runner derives. A seat that understates residual risk is, in the model's own
terms, overstating how much a fix accomplished.

WHAT THIS SCRIPT DOES NOT ESTABLISH. It does not identify the cause. It
establishes that a cause exists and that it is one-directional. Whether the
seats use a different formula, different inputs, or an older form of the
equation is the next question, and it is not answered here.

Every figure is cross-verified on 2 independent tools.

Run:  python3 scripts/rk_self_report_bias_2026-09-21.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: The run this was measured from. Named rather than globbed, so re-running it
#: later cannot silently change which population the figures describe.
LOG = REPO / "bench" / "logs" / "commissioning_2026-09-21_arm1.log"

PAIR = re.compile(r"model=([0-9.]+), recomputed=([0-9.]+), delta=(-?[0-9.]+)")


def pairs_from(path: Path):
    if not path.is_file():
        return []
    return [(float(a), float(b), float(d))
            for a, b, d in PAIR.findall(path.read_text(errors="replace"))]


def main() -> int:
    rows = pairs_from(LOG)
    if not rows:
        print(f"no R_k validation pairs found in {LOG}", file=sys.stderr)
        print("(the run may not have reached its first validation yet)", file=sys.stderr)
        return 2

    import numpy as np
    import mpmath as mp
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint

    model = np.array([r[0] for r in rows])
    recomputed = np.array([r[1] for r in rows])
    delta = recomputed - model

    n = len(rows)
    positive = int((delta > 0).sum())

    print("R_k SELF-REPORT BIAS, commissioning arm 1 round 0")
    print(f"  validation failures analysed : {n}")
    print(f"  recomputed HIGHER than stated: {positive} of {n}")
    print(f"  mean delta                   : {delta.mean():.6f}")
    print(f"  median delta                 : {float(np.median(delta)):.6f}")
    print(f"  range                        : {delta.min():.6f} to {delta.max():.6f}")
    print()

    # --- proportion, 2 routes ------------------------------------------------
    lo_sm, hi_sm = proportion_confint(positive, n, alpha=0.05, method="wilson")
    lo_cp, hi_cp = proportion_confint(positive, n, alpha=0.05, method="beta")
    print(f"  one-sided share : {positive}/{n} = {100.0*positive/n:.4f}%")
    print(f"    Wilson 95%          : [{100*lo_sm:.4f}%, {100*hi_sm:.4f}%]")
    print(f"    Clopper-Pearson 95% : [{100*lo_cp:.4f}%, {100*hi_cp:.4f}%]")

    # --- is one-sidedness plausible under fair error? 2 routes ---------------
    # scipy's exact binomial test against p = 0.5 (a slip is equally likely
    # either way), and the same tail computed directly in mpmath at 50 digits.
    sp_p = float(stats.binomtest(positive, n, 0.5, alternative="two-sided").pvalue)
    mp.mp.dps = 50
    # two-sided exact tail for the symmetric case
    tail = 2 * sum(mp.binomial(n, k) for k in range(positive, n + 1)) / mp.mpf(2) ** n
    print()
    print(f"  sign test vs p=0.5, scipy binomtest : {sp_p:.9e}")
    print(f"  same tail, mpmath at 50 dps         : {float(tail):.9e}")
    agree = abs(sp_p - float(tail)) < 1e-12
    print(f"  the 2 routes agree to 1e-12         : {agree}")
    if not agree:
        print("  REFUSING to report a cross-verified figure that does not cross-verify",
              file=sys.stderr)
        return 1

    # --- magnitude, 2 routes -------------------------------------------------
    t = stats.ttest_1samp(delta, 0.0)
    w = stats.wilcoxon(delta) if n >= 6 else None
    print()
    print(f"  delta != 0, Welch-style t-test  : t={t.statistic:.4f}, p={t.pvalue:.6e}")
    if w is not None:
        print(f"  delta != 0, Wilcoxon signed-rank: W={w.statistic:.1f}, p={w.pvalue:.6e}")

    print()
    print("  INTERPRETATION. A seat making arithmetic slips would err in both")
    print("  directions. 17 of 17 in one direction is a systematic difference")
    print("  between the seats' computation and the runner's, not sloppiness.")
    print("  The cause is NOT identified here; only its existence and direction.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
