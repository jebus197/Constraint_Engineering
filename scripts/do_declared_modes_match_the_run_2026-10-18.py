#!/usr/bin/env python3
"""Across the archive, do declared modes match what the run actually did? -- B28.

Runs `bench/runner_mode_detection.reconcile` over every archived report and
reports, per mode, how often the declaration and the run's own output agree,
disagree, or cannot be compared.

WHY THE UNDECIDABLE COLUMN IS REPORTED RATHER THAN DROPPED. A mode that could not
be checked is not a mode that passed. Dropping it would turn "we cannot tell" into
silent agreement, which is the same substitution his ruling exists to prevent.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.runner_mode_detection import (  # noqa: E402
    AGREE, DECLARED_NOT_OPERATING, OPERATING_NOT_DECLARED, UNDECIDABLE,
    MODES, reconcile,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs", default=str(REPO / "bench" / "logs"))
    args = ap.parse_args()

    per_mode: dict[str, Counter] = defaultdict(Counter)
    offenders: dict[str, list[str]] = defaultdict(list)
    reports = 0
    for p in sorted(Path(args.logs).rglob("*_report.json")):
        if "sandbox_harvest" in str(p):
            continue
        try:
            d = json.loads(p.read_text(errors="ignore"))
        except Exception:                                          # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        reports += 1
        for f in reconcile(d):
            per_mode[f.mode][f.verdict] += 1
            if f.verdict in (DECLARED_NOT_OPERATING, OPERATING_NOT_DECLARED):
                offenders[f.mode].append(f"{p.parent.name} [{f.verdict}] "
                                         f"declared={f.declared} operating={f.operating}")

    print(f"archived reports reconciled: {reports}")
    if not reports:
        print("none found -- the question could not be asked, which is not a pass")
        return 2
    print()
    hdr = f"{'mode':36} {'AGREE':>6} {'DECL_NOT_OP':>12} {'OP_NOT_DECL':>12} {'UNDEC':>6}"
    print(hdr)
    print("-" * len(hdr))
    for mode in MODES:
        c = per_mode[mode.name]
        print(f"{mode.name:36} {c[AGREE]:6} {c[DECLARED_NOT_OPERATING]:12} "
              f"{c[OPERATING_NOT_DECLARED]:12} {c[UNDECIDABLE]:6}")
    print()
    total_dis = sum(len(v) for v in offenders.values())
    if total_dis:
        print(f"★ {total_dis} DISAGREEMENT(S), each a run that did something its "
              f"record does not explain:")
        for mode, rows in offenders.items():
            print(f"  {mode}:")
            for r in rows[:8]:
                print(f"    - {r}")
            if len(rows) > 8:
                print(f"    ... and {len(rows) - 8} more")
    else:
        print("no disagreement in the archive. Every mode that COULD be compared")
        print("agrees with what the run did.")
        print()
        print("READ THE UNDECIDABLE COLUMN CORRECTLY. It is NOT a list of modes that")
        print("cannot be checked. Under entry B32 the runner now writes a `mode_effects`")
        print("record -- the rounds where the location-keyed series actually overwrote")
        print("the gate's input, whether a refuted finding was actually annihilated, and")
        print("whether the sk pipeline ran or was overridden by the target. No ARCHIVED")
        print("report carries it, because it did not exist when they were written, so")
        print("every archived row for those modes is undecidable BY CONSTRUCTION and")
        print("will stay so. The comparison begins with the NEXT run; the constructed")
        print("cases in bench/tests/test_a_declared_mode_is_reconciled_2026-10-18.py are")
        print("what demonstrate the detectors meanwhile.")
        print()
        print("1 mode remains genuinely uncheckable and it is worse than undecidable:")
        print("hierarchical_novelty_convergence is INERT -- its flag is read once, at the")
        print("line publishing a copy of it, and the series it computes reaches a report")
        print("key and nothing else. There is no effect to record. Wire it or retire it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
