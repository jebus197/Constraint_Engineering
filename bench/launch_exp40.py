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
import os
import sys
from pathlib import Path

# Resolve bench/ to sys.path so absolute imports work from any cwd.
_HERE = Path(__file__).resolve().parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# Load .env so API keys (OPENROUTER_API_KEY, DEEPSEEK_API_KEY, etc.) are
# available to the runner and orchestrator subprocesses. Without this,
# the rotated panel's OpenRouter routes (Codex, ChatGPT, Gemini, DeepSeek)
# fail at first dispatch with RuntimeError: OPENROUTER_API_KEY not set.
# Mirrors the .env-loading pattern used by every confer script under
# bench/. Each KEY=VALUE in .env is set via os.environ.setdefault so any
# shell-provided value already in the environment takes precedence.
_ENV_FILE = _HERE.parent / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#"):
            continue
        if _line.startswith("export "):
            _line = _line[7:]
        if "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip().strip("'\""))


def _load_exp40_config() -> dict:
    config_path = _HERE / "exp40_configs" / "40_gate.json"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Expected Exp 40 config at {config_path}"
        )
    return json.loads(config_path.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────
# Gate C — §17 admissibility-parser preflight
# ─────────────────────────────────────────────────────────────────────────────
#
# Folded into Exp 40 launch per the Round 2 plan review (21 April 2026, RQ1
# resolution). The admissibility parser at `bench/dm/_feedback.py` has 10
# offline regression tests at `bench/tests/test_feedback_channel.py` covering
# format tolerance and edge cases. This preflight is the **live-path**
# counterpart: it imports the parser at launch time and runs a small set of
# canonical cases, comparing output against expected values. A mismatch
# blocks the launch and surfaces the failing case.
#
# Protects against:
#   (a) Import failure at launch time (environment drift, missing module)
#   (b) Silent drift in the `ADMISSIBILITY_GATES` tuple (schema change
#       without test update)
#   (c) Environment-specific regex behaviour that escapes offline testing
#
# The preflight does NOT attempt to re-run the full offline suite — those
# tests already guard format tolerance. Gate C's job is a minimal live-path
# confidence check before dispatching to the runner.

_GATE_C_EXPECTED_GATES = {
    "S_min", "G-completeness", "d_tool", "σ_measured", "q_retest",
}


def gate_c_preflight() -> tuple[bool, list[str]]:
    """Run the §17 admissibility-parser live-path preflight.

    Returns
    -------
    (ok, failures) : tuple[bool, list[str]]
        ``ok`` is True iff all canonical cases match expected output and the
        ``ADMISSIBILITY_GATES`` tuple has not drifted.
        ``failures`` is a list of human-readable failure descriptions; empty
        on success.
    """
    try:
        from bench.dm._feedback import (
            parse_admissibility_block,
            ADMISSIBILITY_GATES,
        )
    except ImportError as exc:
        return False, [f"import failed: {exc}"]

    failures: list[str] = []

    # Schema-drift check: the gate set is load-bearing for the rest of the
    # pipeline. Drift here is decision-changing downstream.
    if set(ADMISSIBILITY_GATES) != _GATE_C_EXPECTED_GATES:
        failures.append(
            "ADMISSIBILITY_GATES drift: got "
            f"{sorted(set(ADMISSIBILITY_GATES))}, "
            f"expected {sorted(_GATE_C_EXPECTED_GATES)}"
        )

    # Canonical case matrix. Each case is (label, input_text, expected_set).
    # Cases are drawn from the existing offline test suite to keep the
    # preflight aligned with tested behaviour.
    cases: list[tuple[str, str, set[str]]] = [
        ("missing_block_all_fail", "no admissibility block present",
         set(_GATE_C_EXPECTED_GATES)),
        ("empty_input_all_fail", "", set(_GATE_C_EXPECTED_GATES)),
        (
            "all_pass_no_failures",
            (
                "ADMISSIBILITY:\n"
                "  S_min: PASS\n"
                "  G-completeness: PASS\n"
                "  d_tool: PASS\n"
                "  σ_measured: PASS\n"
                "  q_retest: PASS\n"
            ),
            set(),
        ),
        (
            "one_fail_rest_pass",
            (
                "ADMISSIBILITY:\n"
                "  S_min: PASS\n"
                "  G-completeness: PASS\n"
                "  d_tool: FAIL (pytest not run)\n"
                "  σ_measured: PASS\n"
                "  q_retest: PASS\n"
            ),
            {"d_tool"},
        ),
        (
            "sigma_ascii_variant_accepted",
            (
                "ADMISSIBILITY:\n"
                "  S_min: PASS\n"
                "  G-completeness: PASS\n"
                "  d_tool: PASS\n"
                "  sigma_measured: PASS\n"
                "  q_retest: PASS\n"
            ),
            set(),
        ),
    ]

    for label, text, expected in cases:
        got = set(parse_admissibility_block(text))
        if got != expected:
            failures.append(
                f"case '{label}': expected failed-gate set "
                f"{sorted(expected)}, got {sorted(got)}"
            )

    return len(failures) == 0, failures


def _build_runner_config(exp_cfg: dict, args: argparse.Namespace):
    """Map JSON keys to RunnerConfig fields."""
    from bench.reference_runner_v2 import RunnerConfig  # noqa: E402

    # Only the fields we know RunnerConfig supports; extras preserved in
    # exp_cfg for runner-side use (e.g., _macrophage, _directives_live).
    kwargs = {
        "experiment_name": exp_cfg["experiment_name"],
        "models": exp_cfg["models"],
        # Target article + context files — required by run_experiment to
        # read the source-under-review. Missing these caused an
        # IsADirectoryError on the first real launch attempt 14 May 2026.
        "test_article": exp_cfg["test_article"],
        "context_files": exp_cfg.get("context_files", []),
        "domain": exp_cfg.get("domain", "software"),
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
    parser.add_argument("--skip-gate-c", action="store_true",
                        help="Skip Gate C admissibility-parser preflight "
                             "(debug only; NOT recommended).")
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
        # Gate C admissibility-parser preflight (live-path check). Runs here
        # regardless of --skip-gate-c, because --preflight IS the preflight
        # mode; bypassing the gate in this mode would defeat the flag's
        # purpose.
        ok, failures = gate_c_preflight()
        if not ok:
            print("=" * 60)
            print("GATE C PREFLIGHT FAILED — §17 admissibility parser")
            print("=" * 60)
            for fail in failures:
                print(f"  - {fail}")
            print("")
            print("Investigate bench/dm/_feedback.py and rerun.")
            return 1
        print(f"Gate C preflight: PASS (5 canonical cases, "
              f"{len(_GATE_C_EXPECTED_GATES)} gates verified)")

        # Model-connectivity preflight lives inside reference_runner_v2.
        try:
            from bench.reference_runner_v2 import run_preflight  # noqa: F401
            from bench.reference_runner_v2 import (
                ExperimentConfig,  # noqa: F401
            )
        except ImportError as e:
            print(f"Model-connectivity preflight import failed: {e}")
            return 1
        print("Model-connectivity preflight not wired as stand-alone in v2; "
              "use --dry-run and then run without flags to invoke it in "
              "context.")
        return 0

    # Full run — Gate C preflight runs first unless explicitly skipped.
    if not args.skip_gate_c:
        ok, failures = gate_c_preflight()
        if not ok:
            print("=" * 60)
            print("GATE C PREFLIGHT FAILED — §17 admissibility parser")
            print("=" * 60)
            for fail in failures:
                print(f"  - {fail}")
            print("")
            print("Launch aborted. Investigate bench/dm/_feedback.py and "
                  "rerun. To bypass (debug only, NOT recommended), add "
                  "--skip-gate-c.")
            return 1
        print(f"Gate C preflight: PASS (5 canonical cases, "
              f"{len(_GATE_C_EXPECTED_GATES)} gates verified)")
    else:
        print("WARNING: Gate C preflight skipped (--skip-gate-c). "
              "Launch proceeding without live-path parser verification.")

    try:
        from bench.reference_runner_v2 import run_experiment  # noqa: E402
        from bench.experiment_11_orchestrator import load_default_config  # noqa: E402
    except ImportError as e:
        print(f"ERROR: could not import runner v2 or orchestrator: {e}")
        return 1

    runner_cfg = _build_runner_config(exp_cfg, args)

    # Load the ExperimentConfig (model panel + system prompt) the runner
    # expects. `load_default_config` returns an `ExperimentConfig`
    # populated from `bench/experiment_11_orchestrator.py`'s ModelConfig
    # entries plus the CDSFL system prompt text.
    exp_config_obj = load_default_config()
    cdsfl_path = (Path(__file__).resolve().parent.parent
                  / "bench" / "directives" / "universal"
                  / "cdsfl_core_formal.md")
    cdsfl_text = cdsfl_path.read_text(encoding="utf-8")

    # Delegate to the runner's entry point with the correct signature:
    # run_experiment(exp_config: ExperimentConfig, cdsfl_text: str,
    #                cfg: RunnerConfig)
    result = run_experiment(exp_config_obj, cdsfl_text, runner_cfg)

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
