"""The dispatched panel and the counted panel must not silently differ.

FOUND 2026-08-30 by the first simulated run to drive `run_experiment()` itself.

There are TWO panel lists. `exp_config.models` holds the ModelConfigs actually
dispatched. `cfg.models` is a separate `List[str]` whose default is a hardcoded
FIVE — ['CC2', 'Codex', 'Gemini', 'DeepSeek', 'ChatGPT'] — dating from before
Fable joined the panel. Every count, every per-model denominator and every
`set(cfg.models) - {source}` in the runner reads the SECOND list.

Six ModelConfigs were supplied, `cfg.models` was left at its default, and the run
logged `Models: [...five...]` while dispatching a sixth. Nothing warned.

This is the launcher config-drop class the project has now hit seven times
(`feedback_launcher_config_drop`), and it is silent by construction because the
two lists were never compared.
"""
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v2 as R   # noqa: E402

SRC = (REPO / "bench" / "reference_runner_v2.py").read_text(encoding="utf-8")


def _run_body() -> str:
    fn = next(n for n in ast.walk(ast.parse(SRC))
              if isinstance(n, ast.FunctionDef) and n.name == "run_experiment")
    return ast.unparse(fn).replace('"', "'")


def test_run_experiment_compares_the_two_panel_lists():
    body = _run_body()
    assert "PANEL MISMATCH" in body, (
        "run_experiment does not compare exp_config.models with cfg.models, so a "
        "model can be dispatched and never counted, silently")


def test_the_guard_names_both_directions():
    body = _run_body()
    assert "dispatched but NOT counted" in body
    assert "counted but NOT dispatched" in body


def test_the_default_panel_is_still_the_old_five_and_that_is_recorded():
    """Not a defect to fix blindly — changing a default changes every run that
    relies on it. What must NOT happen is the mismatch going unreported."""
    import dataclasses as dc
    f = next(x for x in dc.fields(R.RunnerConfig) if x.name == "models")
    default = f.default_factory() if f.default_factory is not dc.MISSING else f.default
    assert isinstance(default, list)
    assert "Fable" not in default, (
        "the default panel now includes Fable — update this test and confirm every "
        "per-model denominator still means what it did")
    assert len(default) == 5, f"default panel size changed to {len(default)}"


def test_the_simulated_launcher_sets_both_lists():
    launcher = (REPO / "bench" / "tools" / "run_simulated_experiment.py").read_text()
    assert "models=VENDORS[:args.models]" in launcher, (
        "the launcher sets ExperimentConfig.models but not RunnerConfig.models, "
        "which is exactly how this was found")
