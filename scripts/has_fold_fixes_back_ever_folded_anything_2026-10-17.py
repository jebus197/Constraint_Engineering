#!/usr/bin/env python3
"""Has fold-fixes-back ever actually folded a fix? Measured across the archive.

WHY THIS WAS ASKED. His ruling of 2026-10-11 has 2 conditions: the facility
should be ON BY DEFAULT, and it should fold AT THE END of an experiment rather
than between rounds, because a target that changes under the models makes
convergence unreachable. Task B18 recorded both as unmet.

Tracing who enables it turned up something B18 missed. `bench/tools/
run_simulated_experiment.py:710` sets `apply_fixes_back_enabled=True` in CODE,
not in a config file, so the 3 shakedown legs of 2026-10-15 all ran with it ON --
against B18's claim that it is armed in only 1 of 49 configs, which counted JSON
configs alone. The legs each logged 2 or 3 `apply-back` lines.

AND EVERY ONE OF THOSE LINES IS A REJECTION, with the same cause:
"apply-back REJECT C00NN: ast:unterminated string literal (detected at line 47)".
So the facility was enabled, it attempted promotions, and it folded nothing. That
is why convergence was unaffected: the moving target never moved.

THE SAME ERROR AT THE SAME LINE ACROSS INDEPENDENT RUNS is the part worth
measuring. 3 separate runs, different findings, different models, and an
identical parse failure at line 47 is not 3 models writing bad fixes; it points
at the EXTRACTION producing malformed source. This script establishes the rate
and the shape of the failures instead of inferring it.

`--help` runs no measurement and costs nothing.
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LOGS = REPO / "bench" / "logs"

LINE = re.compile(r"apply-back\s+(REJECT|APPLIED|applied|repaired|accept\w*)\s*"
                  r"([A-Za-z0-9_]+)?:?\s*(.*)$", re.IGNORECASE)


def main() -> int:
    argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()

    runs = sorted(LOGS.glob("*/console.log"))
    verdicts = collections.Counter()
    causes = collections.Counter()
    per_run = collections.Counter()
    lines_seen = 0
    for c in runs:
        try:
            text = c.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for ln in text.splitlines():
            if "apply-back" not in ln:
                continue
            lines_seen += 1
            m = LINE.search(ln)
            if not m:
                verdicts["unparsed"] += 1
                continue
            verdict = m.group(1).upper()
            verdicts["REJECT" if verdict == "REJECT" else "APPLIED"] += 1
            per_run[c.parent.name] += 1
            if verdict == "REJECT":
                cause = m.group(3).split("(")[0].strip()[:60] or "unstated"
                causes[cause] += 1

    print("=" * 76)
    print("HAS FOLD-FIXES-BACK EVER FOLDED A FIX?")
    print("=" * 76)
    print(f"\nrun logs scanned      : {len(runs)}")
    print(f"apply-back lines found: {lines_seen}")
    print(f"verdicts              : {dict(verdicts)}")

    applied = verdicts.get("APPLIED", 0)
    rejected = verdicts.get("REJECT", 0)
    n = applied + rejected
    if n:
        print(f"\nREJECTION RATE = {rejected} of {n} = {rejected/n*100:.4f}%")
        try:
            from statsmodels.stats.proportion import proportion_confint
            from scipy.stats import beta
            lo, hi = proportion_confint(rejected, n, 0.05, "wilson")
            blo = 0.0 if rejected == 0 else float(beta.ppf(0.025, rejected, n-rejected+1))
            bhi = 1.0 if rejected == n else float(beta.ppf(0.975, rejected+1, n-rejected))
            print(f"  Wilson (statsmodels)    [{lo*100:.4f}%, {hi*100:.4f}%]")
            print(f"  Clopper-Pearson (scipy) [{blo*100:.4f}%, {bhi*100:.4f}%]")
            if rejected == n:
                import mpmath as mp
                mp.mp.dps = 40
                exact = float(1 - mp.power(mp.mpf("0.025"), mp.mpf(1)/n))
                print(f"  closed form, all-reject case (mpmath 40 dps): lower bound "
                      f"{(1-exact)*100:.4f}%  agrees with Clopper-Pearson to "
                      f"{abs((1-exact)-blo):.2e}")
        except Exception as exc:                        # noqa: BLE001
            print(f"  interval unavailable: {exc}")

    print(f"\nREJECTION CAUSES:")
    for cause, k in causes.most_common(8):
        print(f"  {k:>4d}  {cause}")

    print(f"\nRUNS THAT ATTEMPTED A PROMOTION: {len(per_run)}")
    for name, k in per_run.most_common(8):
        print(f"  {k:>3d} attempt(s)  {name[:58]}")

    print("\n" + "=" * 76)
    if applied == 0 and rejected > 0:
        print("VERDICT: the facility has NEVER folded a fix. It is enabled in the")
        print("simulated launcher, it attempts promotions, and the gate refuses")
        print("every one. So B18's 2 conditions are necessary but NOT sufficient:")
        print("flipping the default and moving the call to the close would still")
        print("fold nothing until the extraction stops producing unparseable")
        print("source. That is a 3rd condition B18 did not record.")
    else:
        print(f"VERDICT: {applied} promotion(s) did land; re-read before citing.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    sys.exit(main())
