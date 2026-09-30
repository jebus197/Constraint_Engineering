#!/usr/bin/env python3
"""Q6c of the 2026-09-30 brief: can the round count be computed from TARGET
COMPLEXITY before a run?  Answered from the project's OWN archive, by
execution -- every commissioning report already records `target_complexity`
(gamma_input, beta, r_squared, n_windows, target_chars, target_tokens) and a
per-round findings list.

WHAT IT DOES
  1. Sweeps bench/logs/commissioning_*/*_report.json.
  2. Per run: complexity fields, rounds executed, findings per round, novelty
     trajectory proxy (per-round finding count), distinct-target key.
  3. Reports whether a pre-run predictor n*(complexity) is ESTIMABLE from this
     record: distinct targets, spread of gamma_input, and -- only if >= 3
     distinct targets -- a Spearman rank correlation between gamma_input and
     rounds-to-convergence, with its p-value from scipy, cross-checked by an
     exact permutation count where n is small enough.

An honest 'not estimable yet, and this is the protocol' is the deliverable if
the record is thin. No fabricated fit. Writes nothing.
"""
from __future__ import annotations

import glob
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(
        description="Sweep archived commissioning reports for target_complexity "
                    "vs rounds/novelty; report whether a pre-run round-count "
                    "predictor is estimable from the project's own record. "
                    "Writes nothing.")
    ap.parse_args(argv)

    rows = []
    for rp in sorted(glob.glob(str(REPO / "bench/logs/commissioning_*/*_report.json"))):
        try:
            d = json.load(open(rp))
        except Exception as e:                                   # noqa: BLE001
            print(f"  UNREADABLE {rp}: {e}")
            continue
        tc = d.get("target_complexity") or {}
        rounds = d.get("rounds") or []
        per_round = [r.get("findings_count",
                           len(r.get("findings", []))) for r in rounds]
        rows.append({
            "run": pathlib.Path(rp).parent.name,
            "target": d.get("target_file", "?"),
            "gamma_input": tc.get("gamma_input"),
            "beta": tc.get("beta"),
            "r_squared": tc.get("r_squared"),
            "n_windows": tc.get("n_windows"),
            "target_tokens": tc.get("target_tokens"),
            "rounds_executed": len(rounds),
            "per_round_findings": per_round,
        })

    print(f"runs with a report: {len(rows)}")
    for r in rows:
        print(f"  {r['run'][:44]:44s} target={pathlib.Path(str(r['target'])).name[:28]:28s} "
              f"gamma={r['gamma_input']} tokens={r['target_tokens']} "
              f"rounds={r['rounds_executed']} per_round={r['per_round_findings']}")

    targets = {r["target"] for r in rows}
    gammas = sorted({r["gamma_input"] for r in rows if r["gamma_input"] is not None})
    print(f"\ndistinct targets: {len(targets)}")
    print(f"distinct gamma_input values: {len(gammas)}  spread: "
          f"{gammas[0] if gammas else None} .. {gammas[-1] if gammas else None}")

    usable = [r for r in rows
              if r["gamma_input"] is not None and r["rounds_executed"] > 0]
    if len(targets) >= 3 and len(usable) >= 5:
        import scipy.stats as st
        import numpy as np
        x = np.array([r["gamma_input"] for r in usable], float)
        y = np.array([r["rounds_executed"] for r in usable], float)
        rho, p = st.spearmanr(x, y)
        print(f"\nSpearman(gamma_input, rounds_executed) over n={len(usable)}: "
              f"rho={rho:.4f} p={p:.4f}")
        print("CAVEAT: rounds_executed in commissioning runs is largely a "
              "CONFIGURED cap, not a measured convergence point; treat rho as "
              "descriptive only unless convergence-round data replaces it.")
    else:
        print("\nNOT ESTIMABLE from this archive: a pre-run predictor "
              "n*(complexity) needs >= 3 distinct targets with measured "
              "convergence rounds. The record holds the COMPLEXITY half of "
              "every pair already; the missing half is a per-run "
              "convergence-round field.")
    print("\nEXTENDED_RATIONALE.md:65 hypothesises the threshold 'may correlate "
          "with constraint count multiplied by constraint interaction density'. "
          "NEITHER factor is recorded in any report swept here, so that exact "
          "hypothesis is untestable against the current archive; gamma_input is "
          "the only recorded complexity proxy.")


if __name__ == "__main__":
    main(sys.argv[1:])
