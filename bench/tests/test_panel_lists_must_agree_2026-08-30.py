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


DRIVER_SRC = '''import importlib.util, json, sys, pathlib, shutil
REPO = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location(
    '_rse', REPO / 'bench' / 'tools' / 'run_simulated_experiment.py')
m = importlib.util.module_from_spec(spec); sys.modules['_rse'] = m
spec.loader.exec_module(m)
cap = {}
class _Stop(Exception): pass
def fake_exp(*a, **kw):
    cap['experiment'] = [mc.label for mc in kw['models']]; return object()
def fake_run(*a, **kw):
    cap['runner'] = list(kw['models']); raise _Stop
m.R.ExperimentConfig = fake_exp
m.R.RunnerConfig = fake_run
sys.argv = ['x', '--seats', 'Codex,ChatGPT', '--name', '_probe_lists']
rc = None
try:
    rc = m.main()
except _Stop:
    rc = 'STOPPED'
for d in (REPO / 'bench' / 'logs').glob('_probe_lists_*'):
    shutil.rmtree(d, ignore_errors=True)
print('RESULT ' + json.dumps({'rc': str(rc), **cap}))
'''


def test_the_simulated_launcher_sets_both_lists(tmp_path):
    """The 2 panel lists must AGREE — asserted by RUNNING the launcher.

    REWRITTEN TWICE ON 2026-09-21, and the second rewrite is the instructive one.

    It began as a source-text check requiring the literal
    `models=VENDORS[:args.models]` to appear in the launcher. That is the defect
    class `execute-do-not-grep` names, and it failed in the only way a text
    matcher can: the launcher was changed so that BOTH lists read one resolved
    variable — a STRONGER guarantee than 2 expressions that happen to agree —
    and the matcher went red on the improvement, while never having been able to
    detect the divergence it existed to catch.

    The first rewrite called `main()` IN-PROCESS. It passed alone and FAILED in
    the full suite, for a reason worth keeping: the launcher REFUSES to start
    when `immune_agents` was imported before `CDSFL_SHADOW_LOG_DIR` was set,
    because a simulated run would then append to the archival record and mix
    simulated output into it. In a full suite another test has already imported
    it, so `main()` correctly returned 2 and never reached the config
    construction. The guard was right; the test was wrong to be defeated by it,
    and wrong again to be "fixed" by weakening it.

    So the launcher now runs in a FRESH SUBPROCESS, where nothing has imported
    `immune_agents` yet and that guard passes on its own terms. The 2 config
    constructors are intercepted there, and the lists they actually receive are
    compared.
    """
    import json
    import subprocess as sp

    driver = tmp_path / "driver.py"
    driver.write_text(DRIVER_SRC)
    r = sp.run([sys.executable, str(driver), str(REPO)],
               capture_output=True, text=True, timeout=300)
    line = [ln for ln in r.stdout.splitlines() if ln.startswith("RESULT ")]
    assert line, (
        f"the driver produced no result.\nstdout:\n{r.stdout[-3000:]}"
        f"\nstderr:\n{r.stderr[-2000:]}")
    got = json.loads(line[-1][len("RESULT "):])

    assert got.get("rc") == "STOPPED", (
        "the launcher returned before building its configs, so the 2 lists were "
        f"never compared: {got}\n{r.stdout[-2000:]}")
    assert got["experiment"] == got["runner"], (
        "ExperimentConfig.models and RunnerConfig.models disagree, so the runner "
        f"would count a different panel than it dispatches: "
        f"{got['experiment']} vs {got['runner']}")
    assert got["experiment"] == ["Codex-SIM", "ChatGPT-SIM"], got
