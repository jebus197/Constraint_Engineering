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
import shutil
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import reference_runner_v3 as R   # noqa: E402

SRC = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")


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


def test_the_simulated_launcher_sets_both_lists(monkeypatch, tmp_path):
    """The 2 panel lists must AGREE — asserted by running the launcher.

    REWRITTEN 2026-09-21. This test used to read the launcher's source and
    require the literal string `models=VENDORS[:args.models]` to appear in it.
    That is the defect class `execute-do-not-grep` names, and it failed in the
    only way a text matcher can: the launcher was changed so that BOTH lists
    read one resolved variable — a STRONGER guarantee than 2 separate
    expressions that happened to agree — and the matcher went red on the
    improvement while never having been able to detect the divergence it
    existed to catch.

    A text matcher cannot compare a producer with a consumer, because each is
    individually consistent with itself. So the launcher is now RUN, with the
    2 config constructors intercepted, and the lists it actually builds are
    compared.
    """
    import importlib.util, sys as _sys

    spec = importlib.util.spec_from_file_location(
        "_rse_under_test", REPO / "bench" / "tools" / "run_simulated_experiment.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    captured = {}

    class _Stop(Exception):
        pass

    def fake_experiment_config(*a, **kw):
        captured["experiment"] = kw
        return object()

    def fake_runner_config(*a, **kw):
        captured["runner"] = kw
        raise _Stop

    monkeypatch.setattr(m.R, "ExperimentConfig", fake_experiment_config)
    monkeypatch.setattr(m.R, "RunnerConfig", fake_runner_config)
    monkeypatch.setattr(
        _sys, "argv",
        ["run_simulated_experiment.py", "--seats", "Codex,ChatGPT",
         "--name", "_panel_lists_agreement_probe"])

    logs_root = REPO / "bench" / "logs"
    before = set(logs_root.glob("_panel_lists_agreement_probe_*"))
    try:
        with pytest.raises(_Stop):
            m.main()
    finally:
        for d in set(logs_root.glob("_panel_lists_agreement_probe_*")) - before:
            shutil.rmtree(d, ignore_errors=True)

    seat_labels = [mc.label for mc in captured["experiment"]["models"]]
    assert seat_labels == captured["runner"]["models"], (
        "ExperimentConfig.models and RunnerConfig.models disagree, so the runner "
        f"would count a different panel than it dispatches: "
        f"{seat_labels} vs {captured['runner']['models']}")
    assert seat_labels == ["Codex-SIM", "ChatGPT-SIM"], seat_labels
