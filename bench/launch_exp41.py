#!/usr/bin/env python3
"""Experiment 41 launcher (runner v2, clean launcher_core implementation).

Founder-directed 2026-05-22. Exp 41 is the first experiment under the
corrected methodology:

  1. STATIC TEST ARTICLE  — apply_fixes_back_enabled=false. The panel
     reviews bench/dm/_convergence.py (frozen) every round; fixes fold
     post-experiment, not mid-experiment.
  2. COMPELLED CONVERGENCE — cdsfl_core_formal.md §10 formalises the
     per-round sufficiency assessment. Sent to every model as part of
     the CDSFL system prompt automatically.
  3. PRIMARY/SECONDARY ROUTE FALLBACK — every model has a secondary;
     no model misses a round (feedback_no_benching.md).
  4. RECONSTRUCTION BYPASSES REMOVED — empties propagate honestly to
     ITC and FailureHandler.
  5. HARDENED GATE — F4 + F6 + conjunction + sparsity fallback; frozen
     pre-registered defaults identical to Exp 40.

This launcher uses bench/launcher_core.py — the clean shared
infrastructure that resolves the three latent bugs that affected
launch_exp40.py's early life. See launcher_core docstring.

Usage:
    python3 bench/launch_exp41.py --config 41_convergence.json
    python3 bench/launch_exp41.py --config 41_convergence.json --dry-run
    python3 bench/launch_exp41.py --config 41_convergence.json --resume
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from bench import launcher_core  # noqa: E402

EXP41_CONFIGS = REPO_ROOT / "bench" / "exp41_configs"


def _load_exp41_config(config_arg: str) -> dict:
    """Resolve config name → dict. Accepts a bare filename under
    exp41_configs/ or an absolute path."""
    if "/" in config_arg or config_arg.startswith("."):
        config_path = Path(config_arg).resolve()
    else:
        config_path = EXP41_CONFIGS / config_arg
    if not config_path.exists():
        raise FileNotFoundError(f"Exp 41 config not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Experiment 41 launcher (runner v2; static target + "
                    "compelled convergence + secondary-route fallback)."
    )
    parser.add_argument("--config", default="41_convergence.json",
                        help="Config file under exp41_configs/ (or absolute "
                             "path). Default 41_convergence.json.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show the execution plan and exit.")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint.")
    args = parser.parse_args()

    # launcher_core.load_env_file() is called at import time, so API keys
    # are already in os.environ. Re-invoke explicitly for safety on
    # repeat-launch / test contexts.
    launcher_core.load_env_file()

    exp_cfg = _load_exp41_config(args.config)

    if args.dry_run:
        print("=" * 60)
        print("EXPERIMENT 41 — DRY RUN")
        print("=" * 60)
        print(f"  Experiment: {exp_cfg['experiment_name']}")
        print(f"  Test article: {exp_cfg['test_article']}")
        print(f"  Context files: {exp_cfg.get('context_files', [])}")
        print(f"  Models: {exp_cfg['models']}")
        print(f"  Max rounds: {exp_cfg['max_rounds']}")
        print(f"  Wall clock cap: {exp_cfg['wall_clock_cap_s']}s")
        print(f"  apply_fixes_back_enabled: "
              f"{exp_cfg.get('apply_fixes_back_enabled', 'unspecified')} "
              f"(static target if False)")
        print(f"  hardened_gate_enabled: "
              f"{exp_cfg.get('hardened_gate_enabled', 'unspecified')}")
        print("  Convergence pass condition:")
        crit = exp_cfg.get("_convergence_criteria", {})
        print(f"    {crit.get('pass_condition', 'unspecified')}")
        print("  Directives live:")
        for k, v in exp_cfg.get("_directives_live", {}).items():
            print(f"    {k}: {v}")
        print(f"  Test cmd: {exp_cfg.get('test_cmd', '(unset)')}")
        print()
        print("  Runner: bench/reference_runner_v2.py")
        print("  Launcher infra: bench/launcher_core.py")
        print("=" * 60)
        return 0

    runner_cfg = launcher_core.build_runner_config_from_dict(exp_cfg, args)
    cdsfl_text = launcher_core.load_cdsfl_directive()
    exp_config_obj = launcher_core.load_experiment_config()
    result = launcher_core.dispatch_experiment(
        exp_config_obj, cdsfl_text, runner_cfg,
    )

    if result.get("terminated"):
        print(f"\nExperiment 41 terminated: {result['terminated']}")
        return 1

    # Authoritative convergence signal is result["converged_at"] /
    # result["convergence_reason"] (set by the runner's state /
    # hardened / γ-alt gate). Per-round dicts don't carry a
    # `converged` flag; the seam-fix commit (5fe9101) made the runner
    # set the top-level fields correctly. This logic mirrors the
    # corrected launch_exp40.py post-5fe9101.
    converged = (
        result.get("converged_at") is not None
        or bool(result.get("convergence_reason"))
    )
    if converged:
        reason = result.get("convergence_reason", "") or "converged"
        at = result.get("converged_at")
        print(f"\nExperiment 41 reached a terminal verdict"
              f"{f' at round {at}' if at is not None else ''}: {reason}")
        return 0

    print("\nExperiment 41 ended without convergence (likely wall-clock).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
