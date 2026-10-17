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
        print("agrees with what the run did. The undecidable column is where the")
        print("remaining work is: those modes cannot be checked from a report at all.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
