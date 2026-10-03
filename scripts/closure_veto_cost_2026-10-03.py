#!/usr/bin/env python3
"""What would promoting the fix-efficacy probe from RECORD to VETO actually cost?

THE QUESTION, and it is the founder's. `attempt_close` asks whether a fix BROKE
anything; it never asks whether the fix CURED the defect it was written for.
Measured 2026-10-02: 126 of 246 fixes do not silence their own falsifier
(51.2195%, Wilson [45.0027%, 57.3989%]) and every one of them closed anyway.
`fix_efficacy_mode` can be `record` (the shipped default) or `veto`. The founder
deferred arming it, and the decision needs the COST of arming stated in the
units that matter: how many closures would not have happened, and on which
findings.

WHY A SEPARATE SCRIPT FROM THE 2026-10-02 MEASUREMENT. That one measured the
RATE -- how often a fix fails to cure. This one measures the CONSEQUENCE -- how
many terminal closures the veto would have withheld, split by severity, because
withholding a closure on a critical is a different cost from withholding one on
a cosmetic finding. A rate does not tell you what arming would do.

WHAT IT CANNOT TELL YOU, stated rather than discovered later. A withheld closure
is not a lost finding: the entry returns to the routing ladder and a later round
may close it properly. This measures the FIRST-ORDER cost -- closures withheld
at the moment the veto fires -- and cannot measure whether the ladder would then
have cured them, because that counterfactual did not run. The honest form of
the answer is a bound, not a point.

Usage:  python3 scripts/closure_veto_cost_2026-10-03.py [--json]
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

CRITICAL = 0.7
TERMINAL = ("CLOSED", "CONFIRMED", "CORROBORATED", "MERGED")


def wilson(k: int, n: int) -> dict:
    if n == 0:
        return {"k": k, "n": n, "pct": None}
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    assert abs(float(c - h) - lo) < 1e-9 and abs(float(c + h) - hi) < 1e-9, (
        f"statsmodels and mpmath disagree on Wilson for {k}/{n}")
    return {"k": k, "n": n, "pct": round(100.0 * k / n, 4),
            "wilson": [round(100 * lo, 4), round(100 * hi, 4)]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    from bench.fix_efficacy import FIX_CURES, FIX_INEFFECTIVE

    probed = withheld = 0
    by_sev = collections.Counter()
    by_outcome = collections.Counter()
    instances = []
    for f in sorted((REPO / "bench" / "logs").rglob("*_report.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
            if not isinstance(e, dict):
                continue
            fe = e.get("fix_efficacy") or {}
            outcome = fe.get("outcome") or e.get("fix_efficacy_outcome")
            if not outcome:
                continue
            probed += 1
            by_outcome[outcome] += 1
            if outcome != FIX_INEFFECTIVE:
                continue
            if e.get("status") not in TERMINAL:
                continue          # the veto would have changed nothing here
            withheld += 1
            sev = float(e.get("severity") or 0.0)
            by_sev["critical" if sev >= CRITICAL else "sub-critical"] += 1
            instances.append({"run": f.parent.name, "cid": cid,
                              "status": e.get("status"), "severity": sev})

    out = {
        "entries_carrying_an_efficacy_verdict": probed,
        "outcome_counts": dict(by_outcome),
        "closures_the_veto_would_withhold": wilson(withheld, max(probed, 1)),
        "withheld_by_severity": dict(by_sev),
        "cures_name": FIX_CURES, "ineffective_name": FIX_INEFFECTIVE,
        "bound_not_point": ("a withheld closure returns to the routing ladder; "
                            "whether a later round would have cured it did not "
                            "run, so this is a first-order cost, not a net one"),
        "instances": instances[:40],
    }
    if a.json:
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    print("COST OF PROMOTING FIX-EFFICACY FROM record TO veto")
    print(f"  entries carrying an efficacy verdict : {probed}")
    for k in sorted(by_outcome):
        print(f"    {k:40s} {by_outcome[k]}")
    w = out["closures_the_veto_would_withhold"]
    if w["pct"] is None:
        print("  no entry carries an efficacy verdict, so the cost of arming "
              "cannot be measured from the archive yet.")
    else:
        print(f"  closures the veto WOULD have withheld: {w['k']} of {w['n']} "
              f"= {w['pct']}%, Wilson [{w['wilson'][0]}%, {w['wilson'][1]}%]")
        print(f"    by severity: {dict(by_sev)}")
    print(f"  NOTE: {out['bound_not_point']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
