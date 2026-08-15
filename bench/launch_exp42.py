#!/usr/bin/env python3
"""Experiment 42 launcher (runner v2, shared launcher_core).

Exp 42 is the FIRST experiment under the "tools decide, not votes" methodology
(divergence study, 3 June 2026). Target: bench/cdsfl_registry/composer.py
(S_k expert encodings, the four-layer composer).

Methodology (relative to Exp 41):

  1. FALSIFIER GATE ON — falsifier_gate_enabled=true. Each CRITICAL finding
     carries a runnable falsifier that IMPORTS THE REAL target module; the
     runner independently re-runs it (bench/falsifier_verify.reverify_falsifier)
     and that verdict decides CONFIRMED/REFUTED — NEVER the model's prose claim.
     Un-toolable / broken / missing-falsifier criticals -> HIL, never auto-
     confirmed. This replaces the CONFIRM/CHALLENGE per-finding vote diagnosed
     as the project's first divergence from truth-by-tools.
  2. ACTIVE TOOL USE — OpenAI-compatible routes are given the execute_python
     tool during review (gated by the same flag), so models check and iterate
     their findings against the real code before reporting.
  3. STATIC TEST ARTICLE — apply_fixes_back_enabled=false (frozen target).
  4. GAMMA UNCHANGED + NOT DEMOTED — gamma_alt_threshold=0.30, telemetry/
     advisory, trigger-not-blocker. The convergence layer (R_k / gamma) and the
     §10 sufficiency assessment are retained; only the per-finding TRUTH vote is
     retired. Convergence is never made impossible and never faked.
  5. PRIMARY/SECONDARY ROUTE FALLBACK — every model has a secondary; no model
     misses a round (feedback_no_benching.md).

cy monitoring applies while this runs: watch ~every 60 s, and on anything
screwy pause -> diagnose with tools -> fix -> resume.

Usage:
    python3 bench/launch_exp42.py --config 42_composer.json
    python3 bench/launch_exp42.py --config 42_composer.json --dry-run
    python3 bench/launch_exp42.py --config 42_composer.json --resume
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

EXP42_CONFIGS = REPO_ROOT / "bench" / "exp42_configs"


def _load_exp42_config(config_arg: str) -> dict:
    """Resolve config name -> dict. Accepts a bare filename under
    exp42_configs/ or an absolute path."""
    if "/" in config_arg or config_arg.startswith("."):
        config_path = Path(config_arg).resolve()
    else:
        config_path = EXP42_CONFIGS / config_arg
    if not config_path.exists():
        raise FileNotFoundError(f"Exp 42 config not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Experiment 42 launcher (runner v2; falsifier gate + "
                    "active tool use + static target)."
    )
    parser.add_argument("--config", default="42_composer.json",
                        help="Config file under exp42_configs/ (or absolute "
                             "path). Default 42_composer.json.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show the execution plan and exit.")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from checkpoint.")
    args = parser.parse_args()

    # launcher_core.load_env_file() runs at import; re-invoke for safety on
    # repeat-launch / test contexts.
    launcher_core.load_env_file()

    exp_cfg = _load_exp42_config(args.config)

    if args.dry_run:
        print("=" * 60)
        print("EXPERIMENT 42 — DRY RUN")
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
        # The headline for this experiment: the falsifier gate must be ON, and
        # it must survive the launcher_core passthrough into RunnerConfig.
        gate_in_json = exp_cfg.get("falsifier_gate_enabled", "unspecified")
        runner_cfg_preview = launcher_core.build_runner_config_from_dict(
            exp_cfg, args)
        gate_in_cfg = getattr(
            runner_cfg_preview, "falsifier_gate_enabled", "ABSENT")
        print(f"  falsifier_gate_enabled (JSON): {gate_in_json}")
        print(f"  falsifier_gate_enabled (RunnerConfig): {gate_in_cfg}  "
              f"<- MUST be True for tools-decide; "
              f"{'OK' if gate_in_cfg is True else 'MISWIRED'}")
        print(f"  gamma_alt_threshold: "
              f"{exp_cfg.get('gamma_alt_threshold', 'unspecified')} "
              f"(load-bearing, not demoted)")
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
        print(f"\nExperiment 42 terminated: {result['terminated']}")
        return 1

    converged = (
        result.get("converged_at") is not None
        or bool(result.get("convergence_reason"))
    )
    if converged:
        reason = result.get("convergence_reason", "") or "converged"
        at = result.get("converged_at")
        # The launcher is shared across the whole arc, so the label must come
        # from the config — a hardcoded "Experiment 42" mislabels every other
        # run's terminal line in its own log (founder-reported 2026-07-29).
        _label = exp_cfg.get("experiment_name", "Experiment")
        print(f"\n{_label} reached a terminal verdict"
              f"{f' at round {at}' if at is not None else ''}: {reason}")
        return 0

    print(f"\n{exp_cfg.get('experiment_name', 'Experiment')} ended without "
          f"convergence (likely wall-clock).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
