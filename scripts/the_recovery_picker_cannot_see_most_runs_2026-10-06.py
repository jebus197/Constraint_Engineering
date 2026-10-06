#!/usr/bin/env python3
"""Nearly half the run directories are invisible to the recovery report's picker.

THE FOUNDER'S OBSERVATION, 2026-10-05: a state restore named a run from 23 August as
the latest experiment while the newest run on disk was from 3 October, so an agent
rebuilding context after an interruption read 6-week-old state as current.

TWO COMPOUNDING CAUSES, and the second is the larger:

  1. `cdsfl_utils.latest_experiment` selects by the highest experiment NUMBER rather
     than by date. That is deliberate for its 3 callers, which want the newest FORMAL
     experiment, and is not changed.
  2. It only considers directories matching `exp(\\d+)` AT ALL. Every commissioning
     arm, prose-convergence run, `sim45` and `study_run*` is invisible to it.

This script measures (2). `cdsfl_utils.newest_run` was added beside the original to
answer the question a recovering agent actually asks, and the recovery report now
prints both.

Run:  python3 scripts/the_recovery_picker_cannot_see_most_runs_2026-10-06.py
"""
from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="the_recovery_picker_cannot_see_most_runs_2026-10-06.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--logs", default=str(REPO / "bench" / "logs"))
    return p.parse_args(argv)


def _ci(k, n):
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import norm
    a = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = float(norm.ppf(0.975)); p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    agree = abs(a[0] - (c - h)) < 1e-9 and abs(a[1] - (c + h)) < 1e-9
    return a[0] * 100, a[1] * 100, agree


def main(argv=None) -> int:
    args = _parse_args(argv)
    logs = pathlib.Path(args.logs)
    if not logs.is_dir():
        print(f"no logs directory at {logs}")
        return 1
    with_state, numbered = [], []
    for d in sorted(logs.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if (d / "runner_state.json").is_file() or any(d.glob("*_report.json")):
            with_state.append(d)
            if re.match(r"exp(\d+)", d.name):
                numbered.append(d)
    n, k = len(with_state), len(with_state) - len(numbered)
    print("=" * 78)
    print("HOW MUCH OF THE RECORD THE NUMBERED-EXPERIMENT PICKER CANNOT SEE")
    print("=" * 78)
    print(f"run directories carrying a report or runner_state : {n}")
    print(f"  of those matching exp<N>                        : {len(numbered)}")
    if n:
        lo, hi, agree = _ci(k, n)
        print(f"  INVISIBLE to latest_experiment()                : {k} "
              f"= {100 * k / n:.4f}%, Wilson [{lo:.4f}%, {hi:.4f}%]"
              f"{'' if agree else '  *** TOOLS DISAGREE ***'}")
    print()
    try:
        from cdsfl_utils import latest_experiment, newest_run
    except ImportError as exc:
        print(f"cannot import the pickers: {exc}")
        return 1
    nr, le = newest_run(), latest_experiment()
    print(f"newest_run()        -> {nr['name'] if nr else None}")
    if nr:
        print(f"                       modified {nr['modified']}, "
              f"numbered={nr['is_numbered_experiment']}")
    print(f"latest_experiment() -> {(le or {}).get('name')}")
    if nr and le and nr["name"] != (le or {}).get("name"):
        print()
        print("  THE TWO DISAGREE, which is the condition the founder reported.")
        print("  Both are now printed by the recovery report, labelled, so a")
        print("  recovering agent is not handed one as though it were the other.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
