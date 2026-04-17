#!/usr/bin/env python3
"""Experiment 40 launcher.

First of the 14-experiment coverage sweep (Exp 40 through Exp 53) derived
from the Exp 39 sub-experiments. Target: bench/dm/_feedback.py (§17 module).

This entry script loads bench/exp40_configs/40_gate.json, constructs a
RunnerConfig from it, and dispatches reference_runner_v2.run_experiment.
It does NOT touch bench/reference_runner.py; the Exp 39 runner is frozen.

Usage:
    python3 bench/launch_exp40.py                # full run
    python3 bench/launch_exp40.py --dry-run      # show plan, do not dispatch
    python3 bench/launch_exp40.py --preflight    # connectivity check only
    python3 bench/launch_exp40.py --resume       # resume from checkpoint

Exit codes:
    0  = experiment converged cleanly
    1  = wall-clock or parse error
    42 = HIL review pause (intentional)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Resolve bench/ to sys.path so absolute imports work from any cwd.
_HERE = Path(__file__).resolve().parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def _load_exp40_config() -> dict:
    config_path = _HERE / "exp40_configs" / "40_gate.json"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Expected Exp 40 config at {config_path}"
        )
    return json.loads(config_path.read_text(encoding="utf-8"))


def _build_runner_config(exp_cfg: dict, args: argparse.Namespace):
    """Map JSON keys to RunnerConfig fields."""
    from bench.reference_runner_v2 import RunnerConfig  # noqa: E402

    # Only the fields we know RunnerConfig supports; extras preserved in
    # exp_cfg for runner-side use (e.g., _macrophage, _directives_live).
    kwargs = {
        "experiment_name": exp_cfg["experiment_name"],
        "models": exp_cfg["models"],
        "max_rounds": exp_cfg.get("max_rounds", 8),
        "extension_cap": exp_cfg.get("extension_cap", 10),
        "wall_clock_cap_s": exp_cfg.get("wall_clock_cap_s", 3600),
        "earliest_stop_round": exp_cfg.get("earliest_stop_round", 3),
        "rho_threshold": exp_cfg.get("rho_threshold", 0.25),
        "rho_rolling_window": exp_cfg.get("rho_rolling_window", 3),
        "consecutive_rounds_required": exp_cfg.get(
            "consecutive_rounds_required", 2
        ),
        "sk_enabled": exp_cfg.get("sk_enabled", False),
        "test_cmd": exp_cfg.get("test_cmd"),
        "sk_s_floor": exp_cfg.get("sk_s_floor", 0.0),
        "burst_mode": exp_cfg.get("burst_mode", "auto"),
        "topology": exp_cfg.get("topology", "star"),
        "pattern": exp_cfg.get("pattern", "four_layer"),
        # Resume
        "resume": bool(getattr(args, "resume", False)),
    }

    # γ-alt convergence fields (Exp 40 fix 1A.3)
    for gf in (
        "gamma_alt_threshold",
        "gamma_alt_consecutive_zero_crit",
        "gamma_alt_earliest_round",
    ):
        if gf in exp_cfg:
            kwargs[gf] = exp_cfg[gf]

    # Round-context helpers (1D.1, 1D.2, 1D.4)
    for cf in (
        "prior_fix_summary_enabled",
        "prior_fix_summary_max_entries",
        "prior_fix_summary_max_chars",
        "consolidation_rounds",
        "windowed_context_enabled",
        "windowed_context_full_rounds",
        "windowed_context_max_chars",
    ):
        if cf in exp_cfg:
            kwargs[cf] = exp_cfg[cf]

    # Shadow cell config passthrough
    shadow: dict = {}
    if "_macrophage" in exp_cfg:
        shadow["_macrophage"] = exp_cfg["_macrophage"]
    if "_ouroboros" in exp_cfg:
        shadow["_ouroboros"] = exp_cfg["_ouroboros"]
    if shadow:
        kwargs["shadow_cell_config"] = shadow

    return RunnerConfig(**{k: v for k, v in kwargs.items()
                           if hasattr(RunnerConfig, k) or True})


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Experiment 40 launcher (runner v2)."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show the execution plan and exit.")
    parser.add_argument("--preflight", action="store_true",
                        help="Run model connectivity preflight only.")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint.")
    args = parser.parse_args()

    exp_cfg = _load_exp40_config()

    if args.dry_run:
        print("=" * 60)
        print("EXPERIMENT 40 — DRY RUN")
        print("=" * 60)
        print(f"  Experiment: {exp_cfg['experiment_name']}")
        print(f"  Test article: {exp_cfg['test_article']}")
        print(f"  Context files: {exp_cfg.get('context_files', [])}")
        print(f"  Models: {exp_cfg['models']}")
        print(f"  Max rounds: {exp_cfg['max_rounds']}")
        print(f"  Wall clock cap: {exp_cfg['wall_clock_cap_s']}s")
        print(f"  Convergence:")
        crit = exp_cfg.get("_convergence_criteria", {})
        print(f"    - {crit.get('pass_condition', 'unspecified')}")
        print(f"  Directives live:")
        dl = exp_cfg.get("_directives_live", {})
        for k, v in dl.items():
            if not k.startswith("_"):
                print(f"    - {k}: {v}")
        print(f"  Specialist cells:")
        sc = exp_cfg.get("_specialist_cells", {})
        print(f"    - live: {sc.get('live', [])}")
        print(f"    - functional_shadow: {sc.get('functional_shadow', [])}")
        print("")
        print("  Runner: bench/reference_runner_v2.py (Exp 39 runner frozen)")
        print("=" * 60)
        return 0

    if args.preflight:
        # Preflight lives inside reference_runner_v2.run_experiment; a
        # lightweight stand-alone path checks model dispatch availability.
        try:
            from bench.reference_runner_v2 import run_preflight
            from bench.reference_runner_v2 import (
                ExperimentConfig,  # noqa: F401
            )
        except ImportError as e:
            print(f"Preflight import failed: {e}")
            return 1
        print("Preflight not wired as stand-alone in v2; use --dry-run "
              "and then run without flags to invoke preflight in context.")
        return 0

    # Full run
    try:
        from bench.reference_runner_v2 import run_experiment  # noqa: E402
    except ImportError as e:
        print(f"ERROR: could not import reference_runner_v2: {e}")
        return 1

    runner_cfg = _build_runner_config(exp_cfg, args)

    # Delegate to the runner's own entry. The runner expects to receive
    # the experiment config (test_article path, context_files list) from
    # wrapper infrastructure; we pass the dict in exp_cfg directly.
    result = run_experiment(runner_cfg, exp_cfg)

    if result.get("terminated"):
        print(f"\nExperiment terminated: {result['terminated']}")
        return 1

    converged = any(r.get("converged") for r in result.get("rounds", []))
    if converged:
        print("\nExperiment 40 converged cleanly.")
        return 0

    print("\nExperiment 40 ended without convergence (likely wall-clock).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
