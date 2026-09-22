#!/usr/bin/env python3
"""FALSIFIER: the gamma-threshold reachability recalibration pools SIMULATED
runs into its LIVE population, the provenance failure its own document
(bench/exp40_baseline/THRESHOLD_REACHABILITY_2026-09-05.md, "LIVE AND
SIMULATED ARE SEPARATED, ALWAYS") prohibits.

Imports the REAL scripts/recalibrate_gamma_threshold_reachability.py and calls
its collect(). A run is simulated when its own archived report declares
severity_provenance == "simulated" or dispatches only *-SIM seat labels. The
4 commissioning_arm* runs of 2026-09-21/22 declare exactly that, yet the
classifier is `run.lower().startswith("sim")`, so all 4 land in LIVE and move
the headline from 10/13 to 12/17.

Fails (AssertionError / FALSIFIED) iff any self-declared-simulated run is in
the LIVE population. Exits 0 when LIVE is clean.
"""
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "recal", REPO / "scripts" / "recalibrate_gamma_threshold_reachability.py")
m = importlib.util.module_from_spec(spec)
sys.modules["recal"] = m
spec.loader.exec_module(m)

live, simulated = m.collect()

def declared_simulated(run_name: str) -> bool:
    for p in (REPO / "bench" / "logs").rglob("*report*.json"):
        if p.parent.name != run_name:
            continue
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        prov = (d.get("severity_admissibility") or {}).get("severity_provenance")
        models = d.get("models") or []
        if prov == "simulated":
            return True
        if models and all(str(x).upper().endswith("-SIM") for x in models):
            return True
    return False

polluters = [r["run"] for r in live if declared_simulated(r["run"])]
if polluters:
    print("FALSIFIED")
    for r in polluters:
        print("  simulated run pooled into LIVE:", r)
    raise AssertionError(
        "LIVE reachability population contains self-declared simulated runs: "
        + ", ".join(polluters))
print("clean: LIVE population contains no self-declared simulated run "
      f"(live={len(live)}, simulated={len(simulated)})")
