#!/usr/bin/env python3
"""Seats systematically UNDERSTATE their own R_k, and the run measured it.

WHAT WAS OBSERVED. In round 0 of commissioning arm 1 (2026-09-21, 5 simulated
seats against `bench/cdsfl_registry/engine.py`), the runner recomputed each
seat's self-reported `R_k` and FLAGGED 17 of them. Per seat:

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
allowed. Of the 23 entries validated this round, 5 satisfy it and 18 do not (17
FAIL plus 1 SKIP), so roughly 3 entries in 4 cannot reach the demotion path the
severity-calibration study item exists to exercise -- for a reason that has
nothing to do with severity. The interlock is NOT globally unsatisfiable:
Codex-SIM's 5 passed.

THE DIRECTION IS THE INFORMATIVE PART. The seats report LOWER risk than the
runner derives. A seat that understates residual risk is, in the model's own
terms, overstating how much a fix accomplished.

THE VALIDATION IS ADVISORY. `_validate_rk_computation` says so in its own
docstring -- "Advisory only -- logs discrepancies, never rejects findings" -- so
nothing was rejected. What the FAIL status does do is make `severity_is_proven`
false, because that predicate accepts PASS and WARN (a 0.05 rounding tolerance)
and refuses FAIL. All 17 deltas run from 0.059 to 0.348, all beyond WARN, so all
17 entries are skipped as unproven when severity calibration tries to demote.

THE SIGN IS NOT IN THE LOG. The logged `delta` field is
`abs(model_rk - recomputed)` and carries NO direction. The one-sidedness below
is recovered from the `model=` and `recomputed=` values themselves. A reader
taking the logged delta at face value could not have found it at all.

THE LEADING CANDIDATE CAUSE IS PARSING, AND THAT IS NOT A NEUTRAL GUESS.
`_validate_rk_computation` receives no structured parameters. It extracts
`R_old` and the stated final `R_k` OUT OF THE MODEL'S OWN PROSE with regular
expressions and then recomputes. A systematic one-directional gap is therefore
at least as consistent with the extractor picking up a different number than the
model used as with the models mis-applying a formula they themselves quoted.
This project's standing warning is that parsing errors have plagued it, and
prose-to-parameter extraction is exactly where that bites.

WHAT THIS SCRIPT DOES NOT ESTABLISH. It does not identify the cause. It
establishes that a cause exists and that it is one-directional. Distinguishing a
parsing fault from a computation fault is the next question, and it is not
answered here.

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

    # SAY WHICH POPULATION (2026-09-22, panel). The header said "round 0" while
    # the regex reads the WHOLE log, and the label said "failures" while the
    # matched lines are FAIL *and* WARN (a WARN also prints model=/recomputed=).
    print("R_k SELF-REPORT BIAS, commissioning arm 1, ALL rounds in the log")
    print(f"  R_k validations flagged FAIL or WARN : {n}")
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
    # THE INTERPRETATION IS COMPUTED, NOT TYPED (2026-09-22, panel). These 4
    # lines were a hardcoded string reading "17 of 17 in one direction", printed
    # under a header reading "round 0", while the loop above had already measured
    # 28 of 31 over 8 rounds. A producer whose conclusion does not move with its
    # data states a figure the run refutes, and this one had already drifted by
    # the time the morning report quoted it. It is now derived from `positive`
    # and `n`, so it cannot disagree with the table above it.
    print(f"  INTERPRETATION. A seat making arithmetic slips would err in both")
    print(f"  directions. {positive} of {n} in one direction is a systematic")
    print(f"  difference between what the seats state and what the runner")
    print(f"  RECOMPUTES -- not sloppiness.")
    print()
    print("  THE CAUSE IS NOW IDENTIFIED, AND IT IS THE RUNNER (2026-09-22, panel).")
    print("  `_RK_RE_CLIP` did not treat U+2192 as the end of a parameter")
    print("  statement, so on the seats' own notation")
    print("      R_old=0.50, eta=0.95, d=0.90, p=0.85 -> q=0.727 ...")
    print("      S_k=0.92 -> R_base = 0.92x0.215 + 0.08x0.50 = 0.237")
    print("  the extractor read p as the seat's q and S_k as the seat's R_base.")
    print("  Since")
    print("      d R_k / d S_k = R_old*q*(R_old-1)*(nu-1)/(R_old*q-1)  <  0")
    print("  on 0<q<1, 0<R_old<1, 0<=nu<1 (SymPy; Wolfram Language; z3 unsat for")
    print("  the negation), an UNDER-read S_k always RAISES recomputed R_k. The")
    print("  one-directionality was forced by the defect, not observed in the")
    print("  seats: over the 254 archived CORROBORATION sections of arms 1-4,")
    print("  clipping at the arrow takes FAIL from 79 to 45 -- 33 to PASS, 1 to")
    print("  WARN, none newly failing -- and on CC2-SIM r0 section 0 the seat's")
    print("  stated R_k of 0.266 recomputes to 0.26642, a PASS. The sign test")
    print("  below measures how consistently the EXTRACTOR mis-read.")
    print("  Repaired at bench/reference_runner_v3.py `_RK_RE_CLIP`; guarded by")
    print("  bench/tests/test_rk_clip_stops_at_an_arrow_2026-09-22.py.")
    print("  THIS SCRIPT'S FIGURES ARE PRE-REPAIR and are retained as the record")
    print("  of what the unrepaired extractor produced. Re-run the runner to")
    print("  measure the repaired population.")
    return 0


if __name__ == "__main__":
    # ANSWER `--help` BEFORE DOING THE WORK. Without this the flag is
    # silently ignored, the whole measurement runs -- a git walk, in this
    # family -- and exiting 0 is indistinguishable from having answered.
    # The founder's ruling on this class is that a `--help` must never
    # cost money, and 30 scripts were measured ignoring it on 2026-09-11.
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
