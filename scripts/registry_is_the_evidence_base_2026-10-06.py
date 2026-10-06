#!/usr/bin/env python3
"""Can the registry be cleared or exported without destroying what was measured?

THE FOUNDER'S QUESTION, 2026-10-06: *"when the UX is built, a user may wish to either
clear all records like these from the registry, or to export/conserve them. Does that
make sense in the current design paradigm of the registry? That would be a clear
registry, export all, or view/export a single entry for study."*

THIS SCRIPT ANSWERS 3 FACTUAL SUB-QUESTIONS, because the design answer turns on them:

  1. HOW BIG is the thing a user would clear or export, per run?
  2. ARE THE DERIVED SERIES STORED SEPARATELY from the entries they were derived
     from? If they are, clearing the entries leaves the numbers standing with
     nothing behind them -- the stored history stops being reproducible.
  3. DOES AN ENTRY CARRY WHAT AN EXPORT WOULD NEED to be read back: a stable
     identity, its round, and its provenance?

Every proportion carries a Wilson 95% interval, computed by statsmodels AND an
independent closed form that must agree.

Run: python3 scripts/registry_is_the_evidence_base_2026-10-06.py
"""
from __future__ import annotations

import glob
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Series stored in runner_state ALONGSIDE the registry rather than inside it.
DERIVED_SERIES = ("gamma_history", "gamma_critical_history", "gate_history",
                  "rho_history", "novelty_counts", "raw_counts",
                  "open_ch_history", "stall_history")

#: What an exported entry would need to be read back and studied on its own.
EXPORT_KEYS = ("canonical_id", "status", "severity", "source_model",
               "open_since_round", "description")


def _wilson(k, n):
    """Wilson 95%, closed form, cross-checked against statsmodels by the caller."""
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054
    p = k / n
    c = 1.0 / (1.0 + z * z / n)
    centre = c * (p + z * z / (2 * n))
    half = c * z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - half, centre + half)


def _agree(k, n):
    from statsmodels.stats.proportion import proportion_confint
    lo_s, hi_s = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_c, hi_c = _wilson(k, n)
    assert abs(lo_s - lo_c) < 1e-12 and abs(hi_s - hi_c) < 1e-12, (
        f"statsmodels and the closed form disagree on {k}/{n}")
    return lo_c, hi_c


def main(argv=None) -> int:
    # ARGUMENTS ARE PARSED BEFORE ANY MEASUREMENT RUNS. Without this, `--help`
    # walked all 59 archived runs and printed the full report, which is the shape
    # the project forbids: a flag must never cost what the command costs.
    import argparse
    ap = argparse.ArgumentParser(
        prog="registry_is_the_evidence_base_2026-10-06.py",
        description=__doc__.split("\n\n")[0])
    ap.add_argument("--quiet", action="store_true",
                    help="print only the 2 design answers, not the per-key table")
    args = ap.parse_args(argv)

    import numpy as np

    states = sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json")))
    sizes, with_series, with_entries = [], 0, 0
    key_present = {k: 0 for k in EXPORT_KEYS}
    n_entries_total = 0
    series_but_no_entries = []

    for f in states:
        try:
            d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        entries = ((d.get("registry") or {}).get("entries") or {})
        has_series = any(d.get(s) for s in DERIVED_SERIES)
        with_series += bool(has_series)
        with_entries += bool(entries)
        if has_series and not entries:
            series_but_no_entries.append(pathlib.Path(f).parent.name)
        if entries:
            sizes.append(len(entries))
            for e in entries.values():
                n_entries_total += 1
                for k in EXPORT_KEYS:
                    key_present[k] += (k in e)

    n_runs = len(states)
    print("=" * 84)
    print(f"REGISTRY SHAPE across {n_runs} archived runs")
    print("=" * 84)

    if sizes:
        a = np.array(sizes)
        # NumPy and a pure-Python computation must agree (2-tool rule).
        mean_np, med_np = float(a.mean()), float(np.median(a))
        mean_py = sum(sizes) / len(sizes)
        srt = sorted(sizes)
        med_py = (srt[len(srt)//2] if len(srt) % 2
                  else (srt[len(srt)//2 - 1] + srt[len(srt)//2]) / 2)
        assert abs(mean_np - mean_py) < 1e-9 and abs(med_np - med_py) < 1e-9, \
            "NumPy and the pure-Python summary disagree"
        print(f"  runs carrying entries : {len(sizes)}")
        print(f"  entries per run       : min {a.min()}, median {med_np:.1f}, "
              f"mean {mean_np:.2f}, max {a.max()}")
        print(f"  entries in total      : {n_entries_total:,}")
        print(f"  (NumPy and a pure-Python summary agree to 1e-9)")

    print()
    print("Q2. ARE THE DERIVED SERIES STORED SEPARATELY FROM THE ENTRIES?")
    k, n = with_series, n_runs
    lo, hi = _agree(k, n)
    print(f"  runs storing a derived series alongside the registry: {k} of {n} = "
          f"{100*k/n:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
    print(f"  runs already holding a series with NO entries behind it: "
          f"{len(series_but_no_entries)}")
    for r in series_but_no_entries[:5]:
        print(f"      {r}")
    print("  If the series live OUTSIDE the registry, clearing the registry leaves")
    print("  every stored number standing with nothing behind it. The run would")
    print("  still report a gamma it can no longer derive.")

    print()
    print("Q3. COULD AN EXPORTED ENTRY BE READ BACK ON ITS OWN?")
    if args.quiet:
        return 0
    for key in EXPORT_KEYS:
        kk = key_present[key]
        lo, hi = _agree(kk, n_entries_total) if n_entries_total else (0, 0)
        print(f"  {key:20s} present in {kk:6,} of {n_entries_total:,} = "
              f"{100*kk/max(1,n_entries_total):8.4f}%  "
              f"Wilson [{100*lo:.4f}%, {100*hi:.4f}%]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
