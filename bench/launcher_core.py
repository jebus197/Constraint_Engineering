"""Shared launcher infrastructure for per-experiment launchers.

Background: launch_exp40.py was the first per-experiment launcher and
shipped with three latent integration bugs that pre-launch panel
review did not catch (because no reviewer was directed to execute the
launcher's full call chain against the runner's actual entry signature):

  1. run_experiment was called with two arguments instead of the three
     its signature requires.
  2. RunnerConfig was missing test_article, context_files, and domain
     mappings from the JSON config.
  3. .env was not loaded at module import, so the runner's subprocesses
     could not reach the API keys for OpenRouter-routed models.

This module factors out the launcher machinery that every per-experiment
launcher needs, so the three bugs above (and others of the same class)
cannot recur. Future launchers — launch_exp41.py, launch_exp42.py, etc. —
should import from here and inherit clean behaviour:

    from bench import launcher_core
    launcher_core.load_env_file()
    exp_cfg = json.loads(Path(THIS_EXP_CONFIG).read_text())
    runner_cfg = launcher_core.build_runner_config_from_dict(exp_cfg, args)
    cdsfl_text = launcher_core.load_cdsfl_directive()
    exp_config_obj = launcher_core.load_experiment_config()
    result = launcher_core.dispatch_experiment(
        exp_config_obj, cdsfl_text, runner_cfg
    )

launch_exp40.py predates this module and continues to work via its own
copy of the same logic; refactoring it mid-experiment is deferred.
Future launchers should use this module instead of copying from
launch_exp40.py.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

# Resolve bench/ to sys.path so absolute imports work from any cwd.
_HERE = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def load_env_file(env_path: Path | None = None) -> dict[str, str]:
    """Load environment variables from .env into os.environ.

    Reads KEY=VALUE lines, ignoring blank lines and comments. Uses
    os.environ.setdefault so shell-provided values take precedence
    over .env file values. Returns a dict of the keys actually set
    (i.e. keys that were not already present in the environment).

    Default path: <repo root>/.env.
    """
    if env_path is None:
        env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return {}
    set_keys: dict[str, str] = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = value
                set_keys[key] = value
    return set_keys


def load_cdsfl_directive(directive_path: Path | None = None) -> str:
    """Load the CDSFL system-prompt text the runner sends to every model.

    Default path: bench/directives/universal/cdsfl_core_formal.md.
    """
    if directive_path is None:
        directive_path = (
            REPO_ROOT / "bench" / "directives" / "universal"
            / "cdsfl_core_formal.md"
        )
    if not directive_path.exists():
        raise FileNotFoundError(
            f"CDSFL directive not found at {directive_path}"
        )
    return directive_path.read_text(encoding="utf-8")


def load_experiment_config():
    """Load the ExperimentConfig (panel composition + model routes) from
    bench/experiment_11_orchestrator.py.

    Returns the orchestrator's load_default_config() result, which is the
    ExperimentConfig the runner's run_experiment expects as its first
    positional argument.
    """
    from bench.experiment_11_orchestrator import load_default_config
    return load_default_config()


def build_runner_config_from_dict(exp_cfg: dict[str, Any], args) -> Any:
    """Map a per-experiment JSON config dict to a RunnerConfig instance.

    This includes the three fields (test_article, context_files, domain)
    that launch_exp40.py originally omitted, plus the convergence and
    feedback config fields the runner accepts.

    Parameters
    ----------
    exp_cfg : dict
        The parsed JSON config from bench/exp{N}_configs/*.json.
    args : argparse.Namespace or similar
        Provides at minimum `resume: bool`. Other attributes are
        consulted via getattr-with-default.

    Returns
    -------
    RunnerConfig
        Fully-populated runner config ready to pass to run_experiment.
    """
    from bench.reference_runner_v2 import RunnerConfig

    kwargs: dict[str, Any] = {
        "experiment_name": exp_cfg["experiment_name"],
        "models": exp_cfg["models"],
        # Target article + context files + domain. Missing these caused
        # the IsADirectoryError on the first launch_exp40.py attempt.
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
        "resume": bool(getattr(args, "resume", False)),
    }

    # γ-alt convergence fields (Exp 40 1A.3)
    for gf in (
        "gamma_alt_threshold",
        "gamma_alt_consecutive_zero_crit",
        "gamma_alt_earliest_round",
    ):
        if gf in exp_cfg:
            kwargs[gf] = exp_cfg[gf]

    # G7 merge-arbitration fields (Exp 40 continuation, 15 May 2026).
    # Future launchers inherit arbitration passthrough; default-
    # disabled unless a config sets merge_arbitration_enabled.
    for af in (
        "merge_arbitration_enabled",
        "merge_arbitration_min_defer_count",
        "merge_arbitration_max_per_round",
        "merge_arbitration_tiebreaker_gamma",
        "inround_reask_enabled",
        "inround_reask_min_markers",
        "apply_fixes_back_enabled",
        "apply_fixes_back_seed",
        "hardened_gate_enabled",
        "gamma_crit_sustain_rounds",
        "gamma_crit_min_cumulative",
        "gamma_crit_loo_tol",
    ):
        if af in exp_cfg:
            kwargs[af] = exp_cfg[af]

    # Round-context helper fields (1D.1, 1D.2, 1D.4)
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

    # Falsifier gate ("tools decide, not votes", 2026-06-03). Default-off:
    # if the key is absent the RunnerConfig default (False) keeps vote-based
    # behaviour byte-identical; a config sets True to let the runner's
    # independent falsifier re-run decide critical findings instead of the
    # CONFIRM/CHALLENGE vote, and to give OpenAI-compatible models the
    # execute_python tool during review.
    if "falsifier_gate_enabled" in exp_cfg:
        kwargs["falsifier_gate_enabled"] = exp_cfg["falsifier_gate_enabled"]
    # Routing (renamed from take_up_slack, 2026-07-12). Accept the new key; fall back
    # to the legacy key as a back-compat alias so existing configs (incl. the frozen
    # Exp 42/43 pre-registrations) keep mapping to RunnerConfig(routing_enabled=...).
    if "routing_enabled" in exp_cfg:
        kwargs["routing_enabled"] = exp_cfg["routing_enabled"]
    elif "take_up_slack_enabled" in exp_cfg:
        kwargs["routing_enabled"] = exp_cfg["take_up_slack_enabled"]
    # Code-location convergence (2026-06-09): shadow telemetry (default True) and the
    # promotion of the location-keyed count to the actual γ-alt convergence trigger.
    if "location_shadow_enabled" in exp_cfg:
        kwargs["location_shadow_enabled"] = exp_cfg["location_shadow_enabled"]
    if "location_keyed_convergence" in exp_cfg:
        kwargs["location_keyed_convergence"] = exp_cfg["location_keyed_convergence"]
    # Contested-handling fields (Exp 43 fix tranche, 2026-07-22). FIX 4 lowers
    # max_contested_rounds per-config; without this passthrough the launcher
    # path silently ran the code default (5) while the runner's own --config
    # path honoured the JSON — the same silent-divergence class as the 12 July
    # routing-alias gap. Caught by the Exp 44 both-paths pre-flight trace.
    if "max_contested_rounds" in exp_cfg:
        kwargs["max_contested_rounds"] = exp_cfg["max_contested_rounds"]
    if "post_convergence_sweep_rounds" in exp_cfg:
        kwargs["post_convergence_sweep_rounds"] = exp_cfg["post_convergence_sweep_rounds"]
    for imf in ("immune_memory_enabled", "immune_memory_path"):
        if imf in exp_cfg:
            kwargs[imf] = exp_cfg[imf]

    # Shadow cell passthrough
    shadow: dict[str, Any] = {}
    if "_macrophage" in exp_cfg:
        shadow["_macrophage"] = exp_cfg["_macrophage"]
    if "_ouroboros" in exp_cfg:
        shadow["_ouroboros"] = exp_cfg["_ouroboros"]
    if shadow:
        kwargs["shadow_cell_config"] = shadow

    return RunnerConfig(**kwargs)


def dispatch_experiment(exp_config_obj, cdsfl_text: str, runner_cfg) -> dict:
    """Dispatch run_experiment with the correct three-argument signature.

    Importing run_experiment from reference_runner_v2 is centralised here
    so future launchers cannot accidentally call it with the wrong
    arity (launch_exp40.py's original two-argument call was the bug
    fixed at commit 22adc0b).
    """
    from bench.reference_runner_v2 import run_experiment
    return run_experiment(exp_config_obj, cdsfl_text, runner_cfg)


# Auto-load .env on import so subprocesses (the runner's model-dispatch
# routes) inherit API keys even if the launcher author forgets to call
# load_env_file() explicitly. This closes the third class of latent
# launcher bug (ae1de45).
load_env_file()
