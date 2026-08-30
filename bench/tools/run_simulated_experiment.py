#!/usr/bin/env python3
"""A REAL experimental run — `run_experiment()` itself — with agents for models.

    LABELS CARRY THE MANDATORY `-SIM` SUFFIX (founder ruling 2026-08-08) AT
    SOURCE. `VENDORS` is already CC2-SIM, DeepSeek-SIM and so on, so the
    ModelConfig labels, cfg.models, every finding ID, the log directory and
    the report all carry it by construction -- there is no relabelling step
    left for anything to drop. Nothing here is an experimental result.


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
import os
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

#: Named with the mandatory ``-SIM`` suffix AT SOURCE (founder ruling
#: 2026-08-08) so every downstream consumer -- ModelConfig labels,
#: cfg.models, parse_findings, finding IDs, the log directory and the report
#: -- carries it by construction. A relabelling map has somewhere to be
#: dropped; a correct name at source does not.
VENDORS = [f"{v}-SIM" for v in
           ("CC2", "DeepSeek", "ChatGPT", "Gemini", "Codex", "Fable")]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default="bench/dm/_memory.py")
    # 7, NOT 4 (2026-08-30). `verification_min_round` is 6, so at 4 rounds the
    # verification stage returned {"skipped": True, "reason": "round N < 6"} in
    # EVERY round of the v3.1 run and `verified` was False on all 19 entries.
    # Raising the harness rather than lowering the runner's threshold keeps the
    # simulation faithful to what Bench Run 2 will actually do.
    # 16, matching the real exp45 (which converged at round 3, so this costs
    # nothing in practice and lets convergence rather than the cap decide).
    # NOTE: `verification_min_round` is 6 and rounds are 0-based, so CC2v will
    # NOT fire on a run that converges at 3 -- and that is FAITHFUL: the real
    # exp45 never fired it either, reaching verified 24/39 through the
    # falsifier path. Recorded so the absence is not read as a defect.
    ap.add_argument("--rounds", type=int, default=16)
    ap.add_argument("--models", type=int, default=6)
    # 300s timed out 7 of 20 dispatches (35%, Wilson CI [18.1%, 56.7%]) on a
    # 20KB target, and two of those left a model with three consecutive ITC
    # interventions. 900 matches the live CC2 timeout in the real panel.
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--test-cmd", dest="test_cmd",
                    default=("python3 -m pytest bench/tests/test_immune_memory_consumption.py "
                             "bench/tests/test_immune_memory_evaluation.py -q"),
                    help="command S_k runs for its e2_regression gate")
    ap.add_argument("--name", default="sim45_memory")
    args = ap.parse_args()

    if os.path.isabs(args.target):
        # `REPO / <absolute>` lets the absolute path WIN, which would then reach
        # _build_discrimination_overlay and be rejected there. The default is
        # safe; the flag was not (Fable, 2026-08-30).
        print(f"    FATAL: --target must be repo-relative, got {args.target!r}",
              flush=True)
        return 2
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
    # CORRECTED PATH, 2026-08-30 (found by Fable in panel review). This pointed
    # at bench/cdsfl_core_formal.md, WHICH DOES NOT EXIST -- the real file is
    # bench/directives/universal/cdsfl_core_formal.md. The `if is_file()` guard
    # below then silently passed system_prompt_path=None, the composer raised
    # FileNotFoundError, that was swallowed, and the whole simulated panel ran
    # WITHOUT its core directive for the entire v3.1 run. A guard that turns a
    # wrong path into a quiet None is worse than no guard.
    cdsfl_path = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
    if not cdsfl_path.is_file():
        print(f"    FATAL: core directive not found at {cdsfl_path}", flush=True)
        print("    A simulated panel briefed without its directive is not a "
              "simulation of this schema.", flush=True)
        return 2
    models = [R.ModelConfig(label=v, model_id="sim", api="sim",
                            role="player_manager" if i == 0 else "player",
                            system_prompt_path=str(cdsfl_path),
                            timeout=args.timeout, max_retries=1)
              for i, v in enumerate(VENDORS[:args.models])]
    exp_cfg = R.ExperimentConfig(models=models, logs_dir=str(logs),
                                 budget_limit=0.0, cdsfl_system_prompt="")
    cfg = R.RunnerConfig(
        experiment_name=args.name,
        # BOTH lists, or the runner counts a different panel than it dispatches.
        models=VENDORS[:args.models],
        # REPO-RELATIVE, not absolute (CC2, panel review 2026-08-30).
        # `_build_discrimination_overlay` raises
        # "discrimination control: target must be repo-relative" on an absolute
        # path, and `cfg.test_article` reaches it raw. So even with the
        # falsifier supply repaired, the discrimination control could not have
        # fired in ANY simulated run. Verified by forcing both forms:
        # relative -> DISCRIMINATES, absolute -> INDETERMINATE_ERROR.
        test_article=str(args.target),
        # "statistics", matching the REAL exp45 this run is compared against
        # (verified in its report). The composer renders domain-specific
        # directives, so "software" briefed the simulated panel differently
        # from the run it is measured against (Fable, 2026-08-30).
        domain="statistics",
        max_rounds=args.rounds,
        falsifier_gate_enabled=True,
        routing_enabled=True,
        sk_enabled=True,
        location_keyed_convergence=True,
        # PARITY WITH THE REAL exp45 CONFIG (bench/exp45_configs/
        # 45_memory_statistics_live.json), measured by CC2 in second-pass
        # review 2026-08-30. Every value below differed, and each difference
        # let the simulation behave in a way the run it is compared against
        # structurally could not:
        #   earliest_stop_round   default 12 > max_rounds, so the STATE GATE
        #                         returned "too early" every round and only ONE
        #                         of the two convergence gates was ever exercised
        #   stall_gamma_*         exp45 pins both at 1.01, ABOVE the gamma
        #                         ceiling, so its stall detector can never fire
        #                         via gamma; the sim left them live at
        #                         0.45/0.30 and could halt on a path the real
        #                         run cannot reach
        #   merge_arbitration     exp45 True, default False -- a second seam
        #                         path (_arb_dispatch) was permanently dark
        pattern="four_layer",
        consecutive_rounds_required=3,
        max_contested_rounds=3,
        burst_mode="off",
        gamma_telemetry_only_until=20,
        stall_gamma_terminate=1.01,
        stall_gamma_advisory=1.01,
        earliest_stop_round=3,
        merge_arbitration_enabled=True,
        # DELIBERATE SIMULATION-ONLY DIVERGENCES, so that machinery the real
        # exp45 never reaches is still stress-tested. Each is stated rather
        # than silently inherited:
        #
        #  verification_min_round  exp45 uses 6 and rounds are 0-based, so a run
        #                          converging at 3 NEVER fires the verification
        #                          stage -- true of the real exp45 too. Lowered
        #                          here so the stage is exercised at all.
        #  post_convergence_sweep  0 in the earlier sim, which left one of the
        #                          dispatch paths permanently dark.
        #  discrimination_control_ask  wired 2026-08-30 and enabled here: the
        #                          main panel has NEVER been asked for a
        #                          corrected copy, which is why the control has
        #                          0 of 58 entries carrying both its inputs.
        verification_min_round=2,
        post_convergence_sweep_rounds=1,
        # RE-ARMED (founder ruling 2026-08-30, decision 2 option A).
        #
        # It was disarmed for exactly one reason: the DISC_FAILED branch ran
        # registry.resolve(cid, "UNCONFIRMED", ...) UNCONDITIONALLY, so supplying
        # the control its missing input would have let it reverse sound verdicts
        # about half the time it fired (126 of 246 archived fixes do not silence
        # their own falsifier -- 51.2%, Wilson [45.0%, 57.4%]).
        #
        # That reversal is now behind discrimination_control_blocks, which
        # defaults False. The control can therefore RUN and RECORD -- which it
        # has never once done in this project's life, for want of a corrected
        # copy -- without being able to silently un-confirm anything. That is the
        # whole point of the ruling, so the ask goes back on.
        discrimination_control_ask=True,
        extension_cap=args.rounds,
        # Set so S_k's e2_regression is a reading rather than a null. Measured
        # 2026-08-30: e2_regression was None on all 19 entries because no test
        # command was configured, so one of S_k's gates never contributed.
        test_cmd=args.test_cmd,
        # Shadow cells observe and log; they never touch the verdict path.
        # `_run_shadow_cells` returns {} unless these sections exist, so the
        # v3.1 run reported "B Cell v2: 0 claims checked" purely because the
        # harness omitted them. Shape copied from
        # bench/exp47_configs/47_divergence_locationkey_live.json.
        #
        # `_ouroboros` is deliberately NOT enabled: it reaches arXiv and
        # Semantic Scholar, and a simulated run should not depend on an external
        # service being up. Stated rather than silently dropped.
        shadow_cell_config={"_macrophage": {"mode": "patrol"}},
    )

    print(f"=== SIMULATED EXPERIMENT (runner {R.RUNNER_VERSION}) ===", flush=True)
    print(f"    target  {args.target}  ({target.stat().st_size:,} bytes)", flush=True)
    print(f"    panel   {len(models)} agents as {VENDORS[:args.models]}", flush=True)
    print(f"    map     {SHIM.LABEL_MAP}", flush=True)
    print(f"    rounds  max {args.rounds}", flush=True)
    print(f"    logs    {logs}", flush=True)
    print(f"    started {datetime.now().strftime('%H:%M:%S')}", flush=True)

    # PAID-DISPATCH TRIPWIRE (CC2, panel review 2026-08-30, ranked 7th).
    # If the shim ever fails to install, or a path is added that bypasses the
    # seam, this run would dispatch to REAL models and bill for it. The whole
    # point of a simulated run is that it cannot. So the harness refuses at the
    # transport layer rather than trusting the seam.
    import socket as _sock
    from live_dispatch_policy import PAID_HOSTS as _PAID   # ONE canonical copy
    _orig_gai = _sock.getaddrinfo

    def _no_paid(host, port, *a, **kw):
        h = str(host).lower().rstrip(".")
        if any(h == d or h.endswith("." + d) for d in _PAID):
            raise RuntimeError(
                f"SIMULATED RUN ATTEMPTED A PAID DISPATCH to {h}. The seam has "
                f"a hole. Refusing rather than billing.")
        return _orig_gai(host, port, *a, **kw)

    _sock.getaddrinfo = _no_paid
    original = SHIM.install(timeout=args.timeout)
    t0 = time.monotonic()
    try:
        # THE CORE DIRECTIVE, NOT "" (Fable, second-pass review 2026-08-30).
        # `system_prompt_path` is read ZERO times in reference_runner_v2 and
        # runner_core -- the panel's directive arrives only via the composer, or
        # via THIS argument when the composer fails. Passing "" meant the loud
        # composer fallback handed a panellist NOTHING: Fable-SIM has no
        # composer .toml, so it would have run on an empty system prompt while
        # the core directive sat verified-on-disk in this same function.
        result = R.run_experiment(exp_cfg, cdsfl_path.read_text(encoding="utf-8"), cfg)
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
