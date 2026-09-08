#!/usr/bin/env python3
"""Measure how much archived run output sits inside the production scan surface.

Written 2026-09-08 after the full suite went red because a structural checker
read a panel seat's archived rewrite of bench/dm/_memory.py as production code.
The rate travels with this script per `measured-rate-travels-with-its-script`.

Two tools per proportion: statsmodels for the intervals, mpmath for a
closed-form Wilson that does not share statsmodels' implementation.
"""
from __future__ import annotations

import glob
import os
import subprocess

import mpmath as mp
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def wilson_closed_form(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    mp.mp.dps = 30
    z = mp.mpf(str(sps.norm.ppf(1 - (1 - conf) / 2)))
    p, N = mp.mpf(k) / n, mp.mpf(n)
    centre = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    half = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    return float(centre - half), float(centre + half)


def report(label: str, k: int, n: int) -> None:
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, alpha=0.05, method="beta")
    lo_m, hi_m = wilson_closed_form(k, n)
    print(f"{label}")
    print(f"    {k} of {n} = {k/n:.4%}")
    print(f"    Wilson 95%          [statsmodels] : [{lo_w:.4%}, {hi_w:.4%}]")
    print(f"    Wilson 95%          [mpmath     ] : [{lo_m:.4%}, {hi_m:.4%}]   agree={abs(lo_w-lo_m)<1e-12 and abs(hi_w-hi_m)<1e-12}")
    print(f"    Clopper-Pearson 95% [statsmodels] : [{lo_c:.4%}, {hi_c:.4%}]")


def main() -> int:
    paths = glob.glob(os.path.join(ROOT, "bench", "**", "*.py"), recursive=True)
    rels = [os.path.relpath(p, ROOT) for p in paths]
    in_logs = [r for r in rels if r.startswith("bench/logs/")]
    report("Files matching bench/**/*.py that are archived run output, not source:",
           len(in_logs), len(rels))

    # How many predate the archive commit that exposed this?
    new_dir = "bench/logs/target_mutation_watch_2026-09-08/"
    pre_existing = [r for r in in_logs if not r.startswith(new_dir)]
    report("\nOf those, the share that predates commit 3c4987d:",
           len(pre_existing), len(in_logs))
    print("    pre-existing files:")
    for r in sorted(pre_existing):
        print(f"      {r}")

    # Model-written code inside the scan surface.
    quarantined = [r for r in in_logs if "QUARANTINE" in r]
    print(f"\n  archived files whose path declares them model-written/quarantined: {len(quarantined)}")
    for r in sorted(quarantined):
        print(f"      {r}")

    # Which sibling scanners already excluded logs?
    print("\n  scanners that walk bench/ for .py and their logs handling:")
    for f, note in [
        ("bench/tests/test_immune_memory_evaluation.py", "FIXED 2026-09-08 — was the only one without it"),
        ("bench/tests/test_panel_sandbox_2026-09-07.py", "already skipped '/logs/'"),
        ("bench/tests/test_python_floor_2026-09-07.py", "already skipped 'bench/logs/'"),
    ]:
        print(f"      {f}: {note}")
    print("  2 of 3 already had the exclusion; 1 did not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
