#!/usr/bin/env python3
"""Anti-cooking condition (b): is the frozen gamma threshold actually REACHABLE?

WHY THIS EXISTS, AND WHY IT WAS MISSING FOR 111 DAYS
-----------------------------------------------------
The gamma-hardening confer of 2026-05-17 set 4 anti-cooking conditions. Condition
(b) reads, verbatim from
`experimental_notes/Exp41_Convergence_Investigation_2026-05-22.md`:

    "(b) thresholds recalibrated on held-out corpus or null-distribution,
     allowed to fail. bench/exp40_baseline/ contains the F6 critical-definition
     pre-registration but NO RECALIBRATION ARTEFACT. The 0.30 threshold was
     frozen/pre-registered (anti-cooking) but NEVER VALIDATED AS REACHABLE.
     Completing this is integrity-restoring, not bar-lowering."

Freezing a threshold in advance is correct practice: it stops the bar being moved
to fit the result. But a frozen bar nobody can clear is not a conservative
choice, it is a broken instrument -- and the difference is only visible if
somebody measures. Nobody had. Measured 2026-09-05: `bench/exp40_baseline/`
contains the pre-registration, `__init__.py` and 3 feedback slices, and 0 files
matching "recalib". The 2026-09-05 outstanding-work survey had ZERO coverage of
this condition across its entire 4.7-million-character output.

WHAT THIS MEASURES, AND WHAT IT DOES NOT
-----------------------------------------
It answers the reachability half of condition (b): across archived runs, did
`gamma_critical` ever reach 0.30?

It is NOT a held-out recalibration. Condition (b) offers 2 routes -- held-out
corpus, or null distribution -- and this is neither. It is a post-hoc
reachability check on runs that have already happened, which is strictly weaker:
it cannot say the threshold is well-CALIBRATED, only that it is not
unreachable. That limit is stated here rather than left for a reader to notice.
The condition's "allowed to fail" clause is honoured in the only way that means
anything: the answer was not known before the measurement ran, and this script
reports whatever it finds.

LIVE AND SIMULATED ARE SEPARATED, ALWAYS.
A first pass at this measurement mixed them and got 17 of 24. The 5 highest
peaks were all `sim45_*` runs at or near 1.0000. Reporting a reachability figure
that leans on simulated runs would be the provenance failure this project
already has a standing rule against. Simulated runs are reported, separately,
and never pooled.

THE ZEROS ARE NOT ALL EVIDENCE OF UNREACHABILITY. Two of the 3 live runs that
never reached 0.30 are `exp55_v3_control`, both closed by
HALTED_IRREDUCIBLE_QUEUE_ALARM at round 1. A run stopped at round 1 has no
opportunity to develop a gamma series at all, so counting it as a failure to
reach the threshold measures the halt, not the threshold. Both figures are
reported: with and without them.

Usage:
    python3 scripts/recalibrate_gamma_threshold_reachability.py [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOGS = REPO / "bench" / "logs"

# The pre-registered value. Frozen 2026-05-17, never moved, and NOT moved here.
GAMMA_ALT_THRESHOLD = 0.30

# Runs closed before a gamma series could develop. Excluding them is reported as
# a SEPARATE figure, never substituted for the headline.
HALTED_EARLY_MARKERS = ("HALTED_IRREDUCIBLE_QUEUE_ALARM",)


def wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def collect():
    live, simulated = [], []
    for path in sorted(LOGS.rglob("*report*.json")):
        run = path.parent.name
        try:
            d = json.loads(path.read_text())
        except Exception:
            continue
        hist = d.get("gamma_critical_history")
        if not isinstance(hist, list) or not hist:
            continue
        nums = [x for x in hist if isinstance(x, (int, float))]
        if not nums:
            continue
        row = {
            "run": run,
            "peak": max(nums),
            "rounds": len(nums),
            # THE KEY NAMES MATTER, AND GUESSING THEM MADE THIS GUARD VACUOUS.
            # The first version read `closed_by` / `close_reason`. Neither exists
            # in an archived report: the real fields are `halted`, `halted_at_round`
            # and `convergence_reason`. So the exclusion below matched nothing and
            # printed a figure identical to the headline while claiming to exclude
            # something -- a guard that cannot fire, reported as if it had.
            "closed_by": str(d.get("convergence_reason")
                             or d.get("closed_by") or d.get("close_reason") or ""),
            "halted_flag": bool(d.get("halted")),
            "halted_at_round": d.get("halted_at_round"),
        }
        row["halted_early"] = (
            any(m in row["closed_by"] for m in HALTED_EARLY_MARKERS)
            or (row["halted_flag"] and (row["halted_at_round"] or 0) <= 1)
        )
        (simulated if run.lower().startswith("sim") else live).append(row)
    return live, simulated


def summarise(rows, label):
    n = len(rows)
    k = sum(1 for r in rows if r["peak"] >= GAMMA_ALT_THRESHOLD)
    lo, hi = wilson(k, n)
    print(f"  {label}: {k} of {n} runs reached {GAMMA_ALT_THRESHOLD}"
          + (f" = {100*k/n:.1f}%   Wilson 95% [{100*lo:.1f}%, {100*hi:.1f}%]" if n else ""))
    return {"n": n, "reached": k, "wilson": [lo, hi]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    live, simulated = collect()
    if not live:
        print("no live runs carry a gamma_critical series", file=sys.stderr)
        return 2

    print("Anti-cooking condition (b) — is the frozen threshold reachable?")
    print("=" * 70)
    print(f"  pre-registered threshold: {GAMMA_ALT_THRESHOLD} (frozen 2026-05-17, not moved here)")
    print()
    head_live = summarise(live, "LIVE")
    head_sim = summarise(simulated, "SIMULATED (reported separately, never pooled)")
    print()

    eligible = [r for r in live if not r["halted_early"]]
    excluded = [r for r in live if r["halted_early"]]
    sub = summarise(eligible, "LIVE, excluding runs halted before a series could form")
    if excluded:
        print(f"     excluded {len(excluded)}: "
              + ", ".join(f"{r['run']} ({r['rounds']} round(s))" for r in excluded))
    print()

    print("  LIVE peaks:")
    for r in sorted(live, key=lambda x: -x["peak"]):
        mark = "  <- halted early" if r["halted_early"] else ""
        print(f"    {r['peak']:.4f}  {r['rounds']:>3} rounds  {r['run']}{mark}")

    print()
    verdict = ("REACHABLE" if head_live["reached"] else "NOT REACHABLE")
    print(f"  CONDITION (b), REACHABILITY HALF: {verdict}")
    print("  LIMIT: this is a post-hoc reachability check, NOT the held-out")
    print("  recalibration or null-distribution the condition also offers. It can")
    print("  say the bar is not unreachable; it cannot say it is well calibrated.")

    if args.json:
        print(json.dumps({"threshold": GAMMA_ALT_THRESHOLD, "live": head_live,
                          "simulated": head_sim, "live_excluding_halted": sub,
                          "rows": live}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
