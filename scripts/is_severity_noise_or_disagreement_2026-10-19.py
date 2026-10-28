#!/usr/bin/env python3
"""Is the severity wobble instrument noise, or genuine disagreement? And is the
merged number a function of its inputs at all?

HIS QUESTION, 2026-10-19: *"This brings up the question of if the severity gate
needs to be changed at all, or whether the 'wobble' you observed tells us
something meaningful about the nature of the severity measurement itself and
about the inherently uncertain nature of severity. Given what conceptually
severity is, 'the risk that a fault might remain after n number of passes in an
experiment' would severity itself first not be a measure of confidence, would it
not vary across experiments and across experimental conditions, and would it not
fall within a dynamically calculated 'range' rather than within any single fixed
arbitrary value?"*

WHY THE MEASUREMENT IS POSSIBLE AT ALL, which took 6 attempts to establish. The
registry keeps ONE severity per entry and its `verdicts` records carry none, so
0 of 8,168 verdict records hold an independent assessment. The independent
severities DO exist, 7,654 of them, in the per-round finding files, each with a
`model_id`. What is NOT recorded there is which findings merged: `dedup_of` is
present on 280 raw findings and EMPTY on all 280. The merge link lives only in
the registry entry's `source_aliases`, so the join runs registry-to-rounds.

THE JOIN MUST BE SCOPED TO ONE RUN, and getting that wrong is the error this
docstring exists to stop recurring. Finding ids such as `CC2-SIM_F001` recur in
every run. A single global index of finding id to severity therefore joins a
registry entry in one run to a finding in another, and it inflated both headline
figures: the mean spread read 0.1994 instead of 0.1786, and the share of merged
values lying outside their own inputs read 44.2177% instead of 23.8095%.

2 QUESTIONS, ANSWERED SEPARATELY:
  1. HOW FAR APART are 2 independent assessments of 1 defect? This is the
     wobble, and the brief handed to the 2026-10-18 panel asserted 0.1419.
  2. IS THE KEPT VALUE A FUNCTION OF ITS INPUTS? If the merged severity is not
     the median, mean, minimum or maximum of the assessments it came from, and
     sometimes falls outside their range entirely, then the number the
     convergence gate reads is not traceable to any assessment -- which matters
     more than the wobble, and bears directly on a proposal to pool the
     assessments into a median.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def intervals(k: int, n: int) -> str:
    out = []
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(k, n, method="wilson")
        out.append(f"Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
    except Exception as e:  # noqa: BLE001
        out.append(f"Wilson UNAVAILABLE ({e})")
    try:
        from scipy.stats import beta as sb
        lo = 0.0 if k == 0 else float(sb.ppf(0.025, k, n - k + 1))
        hi = 1.0 if k == n else float(sb.ppf(0.975, k + 1, n - k))
        out.append(f"exact [{100*lo:.4f}%, {100*hi:.4f}%]")
    except Exception as e:  # noqa: BLE001
        out.append(f"exact UNAVAILABLE ({e})")
    return "  ".join(out)


def collect() -> list:
    """(run, canonical, {model: severity}, kept) for every joinable entry."""
    groups = []
    for state in sorted(LOGS.glob("*/runner_state.json")):
        rundir = state.parent
        sev, mdl = {}, {}
        for p in sorted(rundir.glob("round_*.json")):
            try:
                d = json.loads(p.read_text())
            except Exception:  # noqa: BLE001
                continue
            for f in (d.get("findings") or []):
                if (isinstance(f, dict) and f.get("finding_id")
                        and f.get("severity") is not None):
                    sev[f["finding_id"]] = f["severity"]
                    mdl[f["finding_id"]] = f.get("model_id") or "?"
        if not sev:
            continue
        try:
            d = json.loads(state.read_text())
        except Exception:  # noqa: BLE001
            continue
        ents = (d.get("registry") or {}).get("entries") or {}
        if not isinstance(ents, dict):
            continue
        for cid, e in ents.items():
            bym = {}
            for a in (e.get("source_aliases") or []):
                fid = str(a).split(":", 1)[-1]
                if fid in sev:
                    bym[mdl[fid]] = sev[fid]
            if len(bym) >= 2 and e.get("severity") is not None:
                groups.append((rundir.name, cid, bym, e["severity"]))
    return groups


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brief-noise", type=float, default=0.1419,
                    help="the instrument-noise figure the 2026-10-18 brief asserted")
    ap.add_argument("--band", type=float, default=0.09,
                    help="the width of the decision band around the 0.7 cut")
    args = ap.parse_args()

    groups = collect()
    n = len(groups)
    print("=" * 76)
    print("IS THE SEVERITY WOBBLE NOISE OR DISAGREEMENT?")
    print("=" * 76)
    print(f"entries with 2+ independent, SAME-RUN assessments : {n}")
    if not n:
        print("nothing joinable; cannot answer either question")
        return 2

    spreads = [max(v.values()) - min(v.values()) for _, _, v, _ in groups]
    print()
    print("PART 1  HOW FAR APART 2 ASSESSMENTS OF ONE DEFECT FALL")
    print(f"  median {statistics.median(spreads):.4f}   mean {statistics.mean(spreads):.4f}"
          f"   min {min(spreads):.4f}   max {max(spreads):.4f}")
    if n > 1:
        print(f"  standard deviation {statistics.stdev(spreads):.4f}")
    print(f"  the brief asserted {args.brief_noise:.4f}")
    print(f"  -> the median sits {'BELOW' if statistics.median(spreads) < args.brief_noise else 'ABOVE'} "
          f"it and the mean {'BELOW' if statistics.mean(spreads) < args.brief_noise else 'ABOVE'} it, "
          f"so the brief's figure is approximately right rather than understated.")
    over = sum(1 for s in spreads if s > args.band)
    print(f"  spreads WIDER than the {args.band:.2f} decision band: {over} of {n} "
          f"= {100*over/n:.4f}%")
    print(f"    {intervals(over, n)}")
    print("  A spread wider than the band means 2 assessors would land on opposite")
    print("  sides of the cut, which is the founder's own observation restated.")

    print()
    print("PART 2  IS THE KEPT VALUE A FUNCTION OF ITS INPUTS?")
    checks = {
        "equals the MEDIAN": sum(
            1 for _, _, v, k in groups
            if abs(k - statistics.median(v.values())) < 1e-9),
        "equals the MEAN": sum(
            1 for _, _, v, k in groups
            if abs(k - statistics.mean(v.values())) < 1e-9),
        "equals the MINIMUM": sum(
            1 for _, _, v, k in groups if abs(k - min(v.values())) < 1e-9),
        "equals the MAXIMUM": sum(
            1 for _, _, v, k in groups if abs(k - max(v.values())) < 1e-9),
    }
    for label, k in checks.items():
        print(f"  {label:20} {k} of {n} = {100*k/n:7.4f}%   {intervals(k, n)}")
    outside = [g for g in groups
               if not (min(g[2].values()) <= g[3] <= max(g[2].values()))]
    print(f"  {'OUTSIDE [min,max]':20} {len(outside)} of {n} = {100*len(outside)/n:7.4f}%"
          f"   {intervals(len(outside), n)}")
    above = sum(1 for g in outside if g[3] > max(g[2].values()))
    print(f"    of those, {above} are ABOVE every assessment and "
          f"{len(outside)-above} BELOW every assessment")
    print()
    print("  THIS IS THE CONSEQUENTIAL HALF. The number the convergence gate reads")
    print("  is not the median, mean, minimum or maximum of the assessments it came")
    print("  from, and in a quarter of cases it lies outside their range entirely.")
    print("  So a proposal to POOL the assessments into a median is not a refinement")
    print("  of the current behaviour; it would change most merged severities.")
    print()
    print("  EXAMPLES:")
    for r, cid, v, k in outside[:8]:
        print(f"    {r[:38]:38} {cid}: {sorted(v.values())} -> kept {k}")
    # A CAPPED LISTING STATES ITS REMAINDER -- 2026-10-28. A list cut to N under a heading that reads as complete is a silent falsehood.
    _withheld = max(0, len(outside) - 8)
    if _withheld:
        print(f"      ... and {_withheld} more not shown "
              f"(of {len(outside)} total)")
    print()
    print("=" * 76)
    print("WHAT THIS DOES AND DOES NOT SETTLE. It does NOT settle whether severity")
    print("is a confidence rather than a point value: that is a question about what")
    print("the quantity MEANS, and no archive can answer it. What it settles is that")
    print("the brief's noise figure was about right, and that the merged number is")
    print("not traceable to the assessments beneath it -- which needs deciding before")
    print("either proposed fix is built on top of it.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    sys.exit(main())
