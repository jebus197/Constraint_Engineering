#!/usr/bin/env python3
"""A REAL experimental run — `run_experiment()` itself — with agents for models.

    LABELS ARE SIM-A..SIM-F IN THE RECORD. The six ModelConfigs carry the vendor
    labels because the runner keys on them, but the shim stamps every dispatch
    with its SIM- label and the report is post-processed to record both. Nothing
    here is an experimental result.

WHY: founder, 2026-08-30 — "test all recent fixes as they unfold and not risk
burning real money, only to discover in the actual runs that things aren't
working as specified. The remaining runway remains short."

TARGET: `bench/dm/_memory.py`, the smallest target in the experimental series
(20,605 bytes, 489 lines, 20 archived findings). Its experiment, exp45, is the
shortest on record — 4 rounds, converged at round 3 by CRITICAL_QUIESCENCE via
the two-sided gate — so there is a clean reference outcome to compare against.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v2 as R                       # noqa: E402
from bench.tools import sim_dispatch_shim as SHIM     # noqa: E402

VENDORS = ["CC2", "DeepSeek", "ChatGPT", "Gemini", "Codex", "Fable"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default="bench/dm/_memory.py")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--models", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--name", default="sim45_memory")
    args = ap.parse_args()

    target = REPO / args.target
    if not target.is_file():
        print(f"target not found: {target}", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logs = REPO / "bench" / "logs" / f"{args.name}_{stamp}"
    logs.mkdir(parents=True, exist_ok=True)

    # Roles mirror the live panel: one player-manager, the rest players. The
    # labels are the VENDOR labels because the runner keys on them; the shim maps
    # each to its SIM- stand-in and the report records both.
    cdsfl_path = REPO / "bench" / "cdsfl_core_formal.md"
    models = [R.ModelConfig(label=v, model_id="sim", api="sim",
                            role="player_manager" if i == 0 else "player",
                            system_prompt_path=str(cdsfl_path) if cdsfl_path.is_file() else None,
                            timeout=args.timeout, max_retries=1)
              for i, v in enumerate(VENDORS[:args.models])]
    exp_cfg = R.ExperimentConfig(models=models, logs_dir=str(logs),
                                 budget_limit=0.0, cdsfl_system_prompt="")
    cfg = R.RunnerConfig(
        experiment_name=args.name,
        # BOTH lists, or the runner counts a different panel than it dispatches.
        models=VENDORS[:args.models],
        test_article=str(target),
        domain="software",
        max_rounds=args.rounds,
        falsifier_gate_enabled=True,
        routing_enabled=True,
        sk_enabled=True,
        location_keyed_convergence=True,
        post_convergence_sweep_rounds=0,
        extension_cap=args.rounds,
    )

    print(f"=== SIMULATED EXPERIMENT (runner {R.RUNNER_VERSION}) ===", flush=True)
    print(f"    target  {args.target}  ({target.stat().st_size:,} bytes)", flush=True)
    print(f"    panel   {len(models)} agents as {VENDORS[:args.models]}", flush=True)
    print(f"    map     {SHIM.LABEL_MAP}", flush=True)
    print(f"    rounds  max {args.rounds}", flush=True)
    print(f"    logs    {logs}", flush=True)
    print(f"    started {datetime.now().strftime('%H:%M:%S')}", flush=True)

    original = SHIM.install(timeout=args.timeout)
    t0 = time.monotonic()
    try:
        result = R.run_experiment(exp_cfg, "", cfg)
    finally:
        SHIM.restore(original)
    el = time.monotonic() - t0

    result["_simulated"] = True
    result["_sim_label_map"] = SHIM.LABEL_MAP
    result["_sim_dispatches"] = SHIM.calls()
    result["_wall_seconds"] = round(el, 1)
    out = logs / f"{args.name}_report.json"
    out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    gh = result.get("gamma_critical_history") or result.get("gamma_history") or []
    print(f"\n=== RESULT ===", flush=True)
    print(f"    runner_version : {result.get('runner_version')}", flush=True)
    print(f"    rounds run     : {len(gh)}", flush=True)
    print(f"    converged_at   : {result.get('converged_at')}", flush=True)
    print(f"    reason         : {(result.get('convergence_reason') or '(none)')[:120]}", flush=True)
    print(f"    findings       : {len((result.get('registry') or {}).get('entries', {}))}", flush=True)
    print(f"    wall           : {el/60:.1f} min", flush=True)
    print(f"    report         : {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
