"""No simulation-only behaviour may reach a paid run.

HIS RULING, 2026-10-12, on restarting the zero-plant control: *"Run it next after
the outstanding simulated run. But take care that the caveats in place for
simulated runs that do not and should not apply to real/paid runs carry over into
this run. We keep all the useful lessons we have learned from the simulated runs
and apply them. But we exclude things that only apply in simulated runs."*

THE READING TAKEN, stated because the first sentence admits two. Read literally
it could ask that the simulation-only caveats DO carry over, which contradicts
its own "do not and should not apply". The 2 sentences after it settle it: keep
the lessons, exclude what is simulation-only.

WHAT IS ASSERTED, and it is the inventory his ruling asks for, mechanised.
Measured by `scripts/what_is_simulation_only_and_what_carries_forward_2026-10-17.py`
using the AST rather than line matching:

  * every branch on `run_is_simulated` in the live harness path only LABELS or
    ANNOTATES output -- 5 of 5 CAVEAT, 0 BEHAVIOUR -- and each keys off the
    `-SIM` suffix, so a paid run turns them off by having no such seat;
  * the stand-in fingerprints cannot inform a paid run, because
    `RunnerConfig.fingerprint_scope` defaults to `experiment` and returns 0
    inherited observations against 11 under `persist`, 6 of them stand-ins.

So the exclusion is STRUCTURAL. The lessons carry forward because they were
never conditional on simulation. This test exists so that a future branch which
CHANGES behaviour on simulation cannot be added without someone deciding to.

THE CLASSIFIER IS CONSERVATIVE BY DESIGN: anything it cannot show to be a
caveat is reported as BEHAVIOUR. A false alarm costs a sentence of explanation;
a missed behaviour branch costs a paid run conducted under simulation rules.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = (REPO / "scripts"
            / "what_is_simulation_only_and_what_carries_forward_2026-10-17.py")


@pytest.fixture(autouse=True)
def _clean_argv(monkeypatch):
    """The producer REFUSES unrecognised arguments, which is correct of it.

    Without this it sees pytest's own argv and declines to run, so the test
    would fail on the harness rather than on the property.
    """
    monkeypatch.setattr(sys, "argv", [str(PRODUCER)])


@pytest.fixture(scope="module")
def probe():
    spec = importlib.util.spec_from_file_location("sim_inventory", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sim_inventory"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def runner():
    import bench.reference_runner_v3 as mod
    return mod


def test_the_inventory_runs_clean(probe, capsys):
    """THE RATCHET. Its exit code is the verdict, so it is called, not read."""
    rc = probe.main()
    out = capsys.readouterr().out
    assert rc == 0, (
        "the simulation inventory refused. Something simulation-only can now "
        "reach a paid run, and his 2026-10-12 ruling says it must not:\n"
        + "\n".join(l for l in out.splitlines()
                    if "BEHAVIOUR" in l or "needs excluding" in l))
    assert "BEHAVIOUR 0" in out, out[-600:]


def test_the_live_scope_excludes_the_producers(probe):
    """A detector that reads its own source reports itself.

    The first version scanned the whole repository and found 5 BEHAVIOUR
    branches, every one a line of its own docstring or another producer's. The
    live path is the code a RUN executes.
    """
    scanned = {rel for _, rel in probe._live_python()}
    assert scanned, "the live scope is empty; the scan would pass vacuously"
    assert all(r.startswith("bench/") for r in scanned)
    assert not any("/tests/" in r or r.startswith("bench/logs/")
                   for r in scanned)
    assert not any(r.startswith("scripts/") for r in scanned), (
        "producers are in scope again, so the detector can report itself")
    # AND IT REALLY SEES THE RUNNER, which is where the branches live.
    assert "bench/reference_runner_v3.py" in scanned


def test_the_fingerprint_default_keeps_stand_ins_out(runner):
    """The one mechanism that could carry a simulated number into a paid run."""
    import dataclasses
    declared = {f.name: f.default
                for f in dataclasses.fields(runner.RunnerConfig)}
    assert declared["fingerprint_scope"] == "experiment", (
        "a paid run would inherit a prior experiment's observations, and the "
        "store holds stand-in records")
    try:
        runner.set_fingerprint_scope("persist")
        persisted = runner._load_fingerprint_cache()
        runner.set_fingerprint_scope("experiment")
        fresh = runner._load_fingerprint_cache()
    finally:
        runner.set_fingerprint_scope(declared["fingerprint_scope"])
    sims = [k for k in persisted if str(k).endswith("-SIM")]
    assert sims, "no stand-in records on disk, so this test proves nothing yet"
    assert not fresh, (
        f"the experiment scope returned {len(fresh)} record(s); stand-ins "
        f"{sims} could reach a paid run")


def test_a_behaviour_branch_would_be_caught(probe, monkeypatch, tmp_path):
    """ANTI-VACUITY, on a planted file rather than on the live tree.

    Asserted by planting a branch that CHANGES a decision on simulation, so
    this holds whether the real tree has 0 such branches or 10. Tying it to the
    live tree being dirty would make it go red on the repair.
    """
    planted = tmp_path / "bench" / "planted.py"
    planted.parent.mkdir(parents=True, exist_ok=True)
    planted.write_text(
        "def go(cfg):\n"
        "    if run_is_simulated(cfg):\n"
        "        return 'take the short path'\n"
        "    return 'take the long path'\n",
        encoding="utf-8")
    real = probe._live_python
    monkeypatch.setattr(
        probe, "_live_python",
        lambda: list(real()) + [(planted, "bench/planted.py")])
    rc = probe.main()
    assert rc == 1, (
        "a planted branch that changes behaviour on simulation was not "
        "reported, so a real one would pass too")
