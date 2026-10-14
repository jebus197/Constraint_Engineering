#!/usr/bin/env python3
"""How often did sub-critical duplicates actually push novelty upward?

ITEM 2 OF THE 2026-10-13 FREE-PANEL BRIEF, the churn horn. The founder's
second fear, verbatim: "new sub-critical (and often mostly churn/dupe) issues
kept being discovered and kept pushing convergence beyond reach". This script
measures how large that effect actually is in the archive, so the fear can be
sized rather than felt.

WHAT COUNTS AS DUPLICATE PRESSURE ON THE NOVELTY SERIES. A duplicate the
dedup path CAUGHT at registration (alias fold, codiscovery) never entered
`novelty_counts` -- it inflated nothing. The inflating case is a canonical
that was REGISTERED AS NEW and only LATER recognised as a duplicate: it
carries `merged_into` (or status MERGED), and it contributed 1 to the novelty
series at its `open_since_round`. This is an UPPER bound on live inflation --
a late merge can also reflect two genuinely distinct findings converging.

Usage: python3 scripts/subcritical_duplicate_pressure_on_novelty_2026-10-13.py
"""
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
CRITICAL = 0.7


def runs():
    for root in (REPO / "bench" / "logs", REPO / "bench" / "logs_quarantine"):
        if not root.exists():
            continue
        for fp in sorted(root.glob("*/runner_state.json")):
            try:
                yield fp, json.loads(fp.read_text(encoding="utf-8",
                                                  errors="ignore"))
            except Exception:  # noqa: BLE001
                continue


def main() -> int:
    answer_help(__doc__, __file__)
    total_novel = 0        # sum of every run's novelty series
    inflat_sub = 0         # later-merged SUB-critical canonicals (the fear)
    inflat_crit = 0        # later-merged criticals (for contrast)
    runs_with_any = runs_seen = 0
    per_run = []
    for fp, d in runs():
        reg = ((d or {}).get("registry") or {}).get("entries") or {}
        series = d.get("novelty_counts") or []
        if not reg:
            continue
        runs_seen += 1
        nov = sum(int(x) for x in series) if series else 0
        total_novel += nov
        sub = crit = 0
        for e in reg.values():
            if not isinstance(e, dict):
                continue
            merged = bool(e.get("merged_into")) or e.get("status") == "MERGED"
            if not merged:
                continue
            sev = e.get("severity")
            if not isinstance(sev, (int, float)):
                continue
            if sev < CRITICAL:
                sub += 1
            else:
                crit += 1
        inflat_sub += sub
        inflat_crit += crit
        if sub:
            runs_with_any += 1
            per_run.append((fp.parent.name, sub, nov))
    if not runs_seen:
        print("no archived runs with a registry; measurement void.")
        return 3
    print(f"archived runs with a registry             : {runs_seen}")
    print(f"sum of all novelty series                 : {total_novel}")
    print(f"later-merged SUB-critical canonicals      : {inflat_sub}")
    print(f"later-merged critical canonicals          : {inflat_crit}")
    print(f"runs with ANY sub-critical late merge     : {runs_with_any}")
    if total_novel:
        from statsmodels.stats.proportion import proportion_confint
        from scipy import stats
        k, n = inflat_sub, total_novel
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        lo2 = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
        hi2 = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
        print(f"UPPER BOUND on novelty inflation by sub-critical duplicates:")
        print(f"  {k}/{n} = {k/n:.4%}")
        print(f"  Wilson 95%          [{lo:.4%}, {hi:.4%}]  (statsmodels)")
        print(f"  Clopper-Pearson 95% [{lo2:.4%}, {hi2:.4%}]  (scipy.beta)")
    _ranked = sorted(per_run, key=lambda t: -t[1])
    for name, sub, nov in _ranked[:8]:
        print(f"    {name:<48} {sub:>3} late-merged sub-crit of {nov} novel")
    # STATE THE REMAINDER: a truncated ranking read as the whole set otherwise.
    if len(_ranked) > 8:
        print(f"    ... and {len(_ranked) - 8} further run(s), of "
              f"{len(_ranked)} total, not shown")
    print()
    print("READING. The inflating case is the LATE merge; a duplicate caught at")
    print("registration never touched the series. The figure above is therefore")
    print("an upper bound on how much sub-critical duplication pushed novelty")
    print("(and with it any novelty-fed convergence input) upward.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
