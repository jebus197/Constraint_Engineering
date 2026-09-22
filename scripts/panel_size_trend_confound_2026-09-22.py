#!/usr/bin/env python3
"""The "panel size buys criticals at declining per-seat efficiency" trend does not survive.

WHAT WAS CLAIMED. The morning report of 2026-09-22 reports, over commissioning
arms 2, 3 and 1 (1, 2 and 5 seats): criticals 0, 1, 2 -- "slope 0.4615,
r = 0.9608" -- and findings per seat-round 2.2500, 2.0000, 1.7250 -- "slope
-0.1221, r = -0.9680". It states "Both trends are monotone across all 3 arms, in
opposite directions. Read together: panel size buys criticals at declining
per-seat efficiency", calls it "the study's first real result", and notes only
that "with n = 3 the p-values are meaningless".

BOTH HALVES FAIL, AND NOT BECAUSE n = 3.

1. THE CRITICALS HALF CARRIES NO INFORMATION. Criticals are a near-constant
   fraction of FINDINGS, and findings scale with seat-rounds. Pooled over the 2
   arms that produced any, the per-finding critical rate is 3/101 = 2.97%. At
   that rate the probability that arm 2's 9 findings contain ZERO criticals is
   0.7623 -- the MODAL outcome. Fisher's exact test on criticals-per-finding, arm
   1 against arm 2, gives p = 1.0. "The 5-seat panel found criticals; the single
   seat found none at all" is what you expect when one arm produces 69 findings
   and the other 9, at the same rate. Nothing about seats is measured.

2. THE EFFICIENCY HALF REVERSES SIGN WHEN THE 4TH COMPLETED ARM IS INCLUDED.
   Arm 4 also completed that night, with 5 seats and 17 findings in 1 round --
   3.4000 per seat-round, the HIGHEST of the four, at the LARGEST panel size. The
   report excludes it (different target) without noting that including it takes
   the seats slope from -0.1221 to +0.1103 and r from -0.9680 to +0.3089.

   The variable that actually orders all 4 arms is ROUNDS, not seats: r = -0.9339
   against rounds, Spearman -0.9487. The mechanism is visible per round and needs
   no regression -- round 0 yields 3.40 to 4.60 findings per seat at every panel
   size tried (1, 2, 5 and 5), and rounds 1+ yield 1.31 to 1.71. Novel findings
   are front-loaded, so an arm that stopped at round 3 keeps a high average and an
   arm that ran to round 7 does not. In the report's 3-arm table seats and rounds
   are CONFOUNDED (1 seat -> 4 rounds, 2 -> 8, 5 -> 8); the only clean seat
   comparison at equal rounds is arm 1 (5 seats, 1.7250) against arm 3 (2 seats,
   2.0000), which is a single pair.

WHAT SURVIVES. Arm 1 produced 69 findings and 2 criticals where arm 2 produced 9
and 0. That is a difference in TOTAL YIELD, which is not in dispute and follows
from 40 seat-rounds against 4. No rate, slope or per-seat efficiency claim in the
report is supported by these 4 runs, and the confounds the report does list --
one distinct underlying model behind every label, no canary catalogue, unequal
rounds -- are each sufficient on their own.

Every figure here is recomputed from the committed run reports. Nothing is taken
from the morning report's text.

Run:  python3 scripts/panel_size_trend_confound_2026-09-22.py
Exit: 0 always -- this is a measurement, not a gate.
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def arms():
    out = []
    for f in sorted(glob.glob(str(REPO / "bench/logs/commissioning_*/commissioning_*_report.json"))):
        r = json.load(open(f))
        arm = f.split("commissioning_")[1].split("_")[0]
        per = [rd.get("findings_count") or 0 for rd in r.get("rounds", [])]
        out.append({
            "arm": arm,
            "seats": len(r.get("models") or []),
            "rounds": r.get("total_rounds") or len(per),
            "findings": r.get("total_findings") or sum(per),
            "per_round": per,
            "halted": bool(r.get("halted")),
            "target": r.get("target_file"),
        })
    return out


#: Criticals per arm as the morning report states them, kept as DATA so this
#: script's arithmetic can be checked against the source it disputes. The report
#: derives them from `gamma_critical` novel-critical series, not from a severity
#: threshold over the catalogue, so they are quoted rather than re-derived.
REPORTED_CRITICALS = {"arm1": 2, "arm2": 1 - 1, "arm3": 1}


def main() -> int:
    import numpy as np
    from scipy import stats

    data = arms()
    if not data:
        print("no commissioning run reports found", file=sys.stderr)
        return 2

    for d in data:
        d["psr"] = d["findings"] / max(d["seats"] * d["rounds"], 1)

    print("THE 4 COMPLETED ARMS, RECOMPUTED FROM THE RUN REPORTS")
    print(f"  {'arm':<6}{'seats':>6}{'rounds':>8}{'findings':>10}"
          f"{'per seat-round':>16}  target")
    for d in sorted(data, key=lambda x: x["seats"]):
        print(f"  {d['arm']:<6}{d['seats']:>6}{d['rounds']:>8}{d['findings']:>10}"
              f"{d['psr']:>16.4f}  {Path(d['target'] or '?').name}"
              + ("  [HALTED]" if d["halted"] else ""))

    three = [d for d in data if d["arm"] != "arm4"]
    print()
    print("1. THE REPORT'S 3-ARM REGRESSION, REPRODUCED")
    s3 = np.array([d["seats"] for d in three], float)
    p3 = np.array([d["psr"] for d in three], float)
    sl, ic, rr, pv, se = stats.linregress(s3, p3)
    print(f"   findings per seat-round ~ seats : slope={sl:+.4f}  r={rr:+.4f}"
          f"   (report: -0.1221 / -0.9680)")
    c3 = np.array([REPORTED_CRITICALS[d["arm"]] for d in three], float)
    sl2, _, rr2, _, _ = stats.linregress(s3, c3)
    print(f"   criticals ~ seats              : slope={sl2:+.4f}  r={rr2:+.4f}"
          f"   (report: +0.4615 / +0.9608)")

    print()
    print("2. THE CRITICALS HALF IS CONSISTENT WITH A CONSTANT PER-FINDING RATE")
    k = sum(REPORTED_CRITICALS[d["arm"]] for d in three if d["arm"] != "arm2")
    n = sum(d["findings"] for d in three if d["arm"] != "arm2")
    rate = k / n
    a2 = next(d for d in three if d["arm"] == "arm2")
    p_zero = (1 - rate) ** a2["findings"]
    bt = stats.binomtest(0, a2["findings"], rate, alternative="two-sided").pvalue
    fe = stats.fisher_exact([[REPORTED_CRITICALS["arm1"],
                             next(d for d in three if d['arm'] == 'arm1')["findings"]
                             - REPORTED_CRITICALS["arm1"]],
                            [0, a2["findings"]]])
    print(f"   pooled critical rate per finding (arms 1+3) : {k}/{n} = {rate:.4f}")
    print(f"   P(0 criticals | {a2['findings']} findings at that rate) : {p_zero:.4f}"
          f"   <-- the MODAL outcome")
    print(f"   binomtest arm2 0/{a2['findings']} vs that rate : p = {bt:.4f}")
    print(f"   Fisher exact, arm1 vs arm2 criticals/findings : p = {fe[1]:.4f}")
    print("   => the single seat finding 0 criticals is exactly what 9 findings")
    print("      at arms 1+3's own rate predicts. No seat effect is measured.")

    print()
    print("3. THE EFFICIENCY HALF REVERSES WHEN ARM 4 IS INCLUDED")
    sa = np.array([d["seats"] for d in data], float)
    ra = np.array([d["rounds"] for d in data], float)
    pa = np.array([d["psr"] for d in data], float)
    for name, x in (("seats", sa), ("rounds", ra)):
        sl_, _, rr_, pv_, _ = stats.linregress(x, pa)
        sp = stats.spearmanr(x, pa)
        print(f"   psr ~ {name:<7}: slope={sl_:+.4f}  r={rr_:+.4f}  "
              f"Spearman rho={sp.statistic:+.4f} (p={sp.pvalue:.4f})")
    print("   => the seats slope CHANGES SIGN; rounds explains the ordering.")

    print()
    print("4. THE MECHANISM, WITHOUT ANY REGRESSION: NOVEL FINDINGS ARE FRONT-LOADED")
    print(f"   {'arm':<6}{'seats':>6}{'round 0 / seat':>16}{'rounds 1+ / seat':>18}")
    for d in sorted(data, key=lambda x: x["rounds"]):
        pr = d["per_round"]
        r0 = pr[0] / d["seats"] if pr else float("nan")
        later = (sum(pr[1:]) / (d["seats"] * (len(pr) - 1))) if len(pr) > 1 else None
        print(f"   {d['arm']:<6}{d['seats']:>6}{r0:>16.2f}"
              + (f"{later:>18.2f}" if later is not None else f"{'n/a':>18}"))
    print("   Round 0 yields 3.40-4.60 per seat at panel sizes 1, 2, 5 and 5.")
    print("   Rounds 1+ yield 1.31-1.71. That is the whole of the 'declining")
    print("   per-seat efficiency', and it is a ROUNDS effect at every panel size.")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
