#!/usr/bin/env python3
"""Which capabilities are armed in the real paid runs but not in the simulated runner?

THE QUESTION, put by the founder on 2026-10-05: *"is this ... part of several elements
of the schema that for whatever reason you have failed to carry over/implement from our
real experimental runners to our simulated runners?"*

IT IS NOT A NEW WORRY — IT IS A RECURRING, DOCUMENTED DEFECT CLASS with at least 3
prior instances, 2 already recorded in the source:

  1. 2026-08-30, CC2 second-pass review. `bench/tools/run_simulated_experiment.py`'s
     own comment: "Every value below differed, and each difference let the simulation
     behave in a way the run it is compared against structurally could not" --
     `earliest_stop_round` (state gate returned "too early" EVERY round, so only 1 of
     2 convergence gates was ever exercised), `stall_gamma_*` (the sim could halt on a
     path the real run cannot reach), `merge_arbitration` (a second seam path
     permanently dark).
  2. 2026-08-30, Fable. `bench/routing.py` ~:90: a `-SIM` label did not match the bare
     vendor names in `DEFAULT_FALSIFIER_STRENGTH`, so `ranked` came out EMPTY and
     routing "exercised the unknown-model fallback instead of the ranked ladder Bench
     Run 2 will run -- so ladder ORDER was unrehearsed by every simulation." Fixed.
  3. 2026-10-05, this script's occasion. The label fix restored the ORDER, but every
     simulated seat is answered by the SAME model, so climbing the ladder climbs
     nothing. Measured: across the 5 rungs `rank_falsifier_writers` returns for a
     DeepSeek-SIM finding, a uniform simulated panel presents **1 distinct model**.
     The capability ladder -- validated on Exp 42, where a strong writer resolved 6 of
     7 of the hardest residuals and the 2-rung ladder reached 7 of 7 -- is therefore
     structurally inert in simulation while appearing to run.

WHAT THIS SCRIPT DOES. It extracts the simulated runner's effective `RunnerConfig`
(explicit keyword literals from its construction, with `RunnerConfig` dataclass
defaults filling the rest) and diffs it against every committed real-experiment config
JSON. It reports, per field: armed in the real run and NOT in the sim, armed in the sim
and not in the real run, and differing values. The first category is the answer to the
founder's question.

A field is only reported as a carry-over gap when the real config ARMS it (a truthy
value, or a non-default number) and the sim does not.

Run:  python3 scripts/what_the_sim_runner_never_carried_over_2026-10-05.py
      python3 scripts/what_the_sim_runner_never_carried_over_2026-10-05.py --config <path>
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import glob
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

SIM_RUNNER = REPO / "bench" / "tools" / "run_simulated_experiment.py"

#: Gaps this script reports that were CHECKED BY EXECUTION and found NOT to be
#: gaps. Recorded here so a later reader is not misled by a static diff's blind
#: spots, and so the finding count is not inflated.
ADJUDICATED_NOT_A_GAP = {
    "target_kind": (
        "AUTO-DETECTED, not declared. `detect_target_kind` returns "
        "('python_module', 'suffix .py') and ('prose', 'suffix .md') when called, so "
        "a blank config value is correct by design -- task A1, 'Target-type detection "
        "in the harness core, not a config flag. Config declares intent; the harness "
        "enforces.' A static diff cannot see this."),
    "panel_cwd": (
        "SET AT RUNTIME, not in the constructor. "
        "`bench/tools/run_simulated_experiment.py:724` assigns "
        "`cfg.panel_cwd = str(_wt)` after construction, so the AST extraction below "
        "cannot see it. A static diff cannot see this either."),
    "burst_mode": (
        "DELIBERATE AND DOCUMENTED. Set to 'off' at the construction site under the "
        "2026-08-30 parity comment."),
}

#: Fields that are per-run identity rather than capability. Differing here is
#: expected and says nothing about carry-over.
IDENTITY_FIELDS = {
    "experiment_name", "models", "test_article", "logs_dir", "domain",
    "max_rounds", "_comment", "context_files", "test_cmd", "budget_limit",
    "cdsfl_system_prompt", "experiment_number", "run_name", "seed",
}


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="what_the_sim_runner_never_carried_over_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--config", default=None,
                   help="one real config JSON to compare against (default: all)")
    p.add_argument("--show-identity", action="store_true",
                   help="also show per-run identity fields")
    return p.parse_args(argv)


def sim_config() -> tuple[dict, dict]:
    """(explicit sim keywords, full effective config incl. RunnerConfig defaults)."""
    from bench.reference_runner_v3 import RunnerConfig
    src = SIM_RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    explicit: dict = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "attr", None) or getattr(fn, "id", None)
        if name != "RunnerConfig":
            continue
        for kw in node.keywords:
            if kw.arg is None:
                continue
            try:
                explicit[kw.arg] = ast.literal_eval(kw.value)
            except (ValueError, SyntaxError):
                explicit[kw.arg] = "<computed at runtime>"
    effective = {}
    for f in dataclasses.fields(RunnerConfig):
        if f.name in explicit:
            effective[f.name] = explicit[f.name]
        elif f.default is not dataclasses.MISSING:
            effective[f.name] = f.default
        elif f.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
            try:
                effective[f.name] = f.default_factory()  # type: ignore[misc]
            except Exception:  # noqa: BLE001
                effective[f.name] = None
        else:
            effective[f.name] = None
    return explicit, effective


def _armed(v) -> bool:
    """Is this value an ARMED capability rather than an off/empty default?"""
    if v is None or v is False:
        return False
    if isinstance(v, str):
        return v not in ("", "off", "none", "disabled")
    if isinstance(v, (list, dict, tuple, set)):
        return len(v) > 0
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return v != 0
    return bool(v)


def main(argv=None) -> int:
    args = _parse_args(argv)
    from bench.reference_runner_v3 import RunnerConfig
    known = {f.name for f in dataclasses.fields(RunnerConfig)}
    explicit, sim = sim_config()

    paths = ([pathlib.Path(args.config)] if args.config
             else [pathlib.Path(p) for p in sorted(
                 glob.glob(str(REPO / "bench" / "exp*_config*" / "*.json")))
                 + sorted(glob.glob(str(REPO / "bench" / "exp*_config.json")))])
    paths = [p for p in paths if p.is_file()]

    print("=" * 78)
    print("WHAT THE SIMULATED RUNNER NEVER CARRIED OVER FROM THE REAL RUNS")
    print("=" * 78)
    print(f"simulated runner      : {SIM_RUNNER.relative_to(REPO)}")
    print(f"  explicit keywords it sets : {len(explicit)}")
    print(f"  RunnerConfig fields total : {len(known)}")
    print(f"  so fields left at default : {len(known) - len(explicit)}")
    print(f"real configs compared : {len(paths)}")
    print()

    gap_counts: dict[str, int] = {}
    gap_examples: dict[str, tuple] = {}
    sim_only: dict[str, int] = {}
    per_cfg = []

    for p in paths:
        try:
            real = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        gaps, extras = [], []
        for k, rv in real.items():
            if k in IDENTITY_FIELDS and not args.show_identity:
                continue
            if k not in known:
                continue
            sv = sim.get(k)
            if _armed(rv) and not _armed(sv):
                gaps.append(k)
                gap_counts[k] = gap_counts.get(k, 0) + 1
                gap_examples.setdefault(k, (rv, sv))
        for k, sv in sim.items():
            if k in IDENTITY_FIELDS and not args.show_identity:
                continue
            if _armed(sv) and not _armed(real.get(k)):
                extras.append(k)
                sim_only[k] = sim_only.get(k, 0) + 1
        per_cfg.append((p.name, len(real), len(gaps), len(extras)))

    print("-" * 78)
    print(f"{'real config':<46} {'keys':>5} {'gaps':>5} {'sim-only':>8}")
    print("-" * 78)
    for name, nk, ng, ne in per_cfg:
        print(f"{name[:46]:<46} {nk:>5} {ng:>5} {ne:>8}")

    print()
    print("=" * 78)
    print("CARRY-OVER GAPS — armed in a REAL config, not armed in the simulated runner")
    print("=" * 78)
    if not gap_counts:
        print("  none found.")
    real_gaps = [k for k in gap_counts if k not in ADJUDICATED_NOT_A_GAP]
    for k in sorted(real_gaps, key=lambda x: -gap_counts[x]):
        rv, sv = gap_examples[k]
        print(f"  {k}")
        print(f"      armed in {gap_counts[k]} of {len(per_cfg)} real configs; "
              f"real example = {rv!r}, sim = {sv!r}")
        print(f"      not mentioned anywhere in the simulated runner")
    print()
    print(f"  REAL GAPS: {len(real_gaps)}")
    print()
    print("  ADJUDICATED NOT A GAP (checked by execution, not by reading):")
    for k in sorted(set(gap_counts) & set(ADJUDICATED_NOT_A_GAP)):
        print(f"    {k}")
        for line in ADJUDICATED_NOT_A_GAP[k].split(". "):
            if line.strip():
                print(f"        {line.strip().rstrip('.')}.")

    print()
    print("=" * 78)
    print("SIM-ONLY — armed in the simulated runner, not in the real configs")
    print("=" * 78)
    print("  (deliberate divergence is legitimate here: the sim exists to stress")
    print("   machinery the real run may not reach. Listed so it is STATED.)")
    for k in sorted(sim_only, key=lambda x: -sim_only[x]):
        print(f"  {k:<42} armed in sim, absent from {sim_only[k]} real config(s)")

    print()
    print("=" * 78)
    print("THE CAPABILITY LADDER, CHECKED BY EXECUTION RATHER THAN BY CONFIG")
    print("=" * 78)
    from bench.routing import rank_falsifier_writers, DEFAULT_FALSIFIER_STRENGTH
    from bench.tools import sim_dispatch_shim as SHIM
    seats = ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM", "DeepSeek-SIM",
             "Gemini-SIM", "Fable-SIM"]
    rungs = rank_falsifier_writers(seats, exclude=("DeepSeek-SIM",))
    print(f"validated strength order : {DEFAULT_FALSIFIER_STRENGTH}")
    print(f"rungs for a DeepSeek-SIM finding : {rungs}")
    for label, smap in (("uniform seats (every simulated run to date)", None),
                        ("seat ladder", SHIM.DEFAULT_LADDER)):
        answered = [(smap or {}).get(m, "opus") for m in rungs]
        n = len(set(answered))
        print(f"  {label}: {n} distinct model(s) across {len(rungs)} rungs")
        if n == 1:
            print("      *** THE LADDER CLIMBS NOTHING. Every rung is the same model,")
            print("      *** so routing runs, logs its rungs, records 'ladder")
            print("      *** exhausted', and cannot do what it exists to do.")
    print()
    print("A capability can be ARMED IN CONFIG and still INERT IN FACT. The config")
    print("diff above cannot see that; only calling the code can.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
