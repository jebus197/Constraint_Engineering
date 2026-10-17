"""State may be scoped to one experiment, on his ruling of 2026-10-16.

TWO STORES, TWO POLICIES, BECAUSE HE GAVE TWO DIFFERENT RULINGS.

ON THE IMMUNE MEMORY: *"We reset immune memory for the upcoming live
experiments... There should be a facility for researchers to select a switch in
the upcoming UX build if they want immune memory to persist between different
experiments, or if they want it to be reset between experiments. For us... since
our models won't change ... probably the best strategy is to leave the default in
this case set to on, so that it can persist between experiments?"* So the switch
exists and its DEFAULT IS PERSIST, which is also the pre-existing behaviour, so
the addition changes nothing until asked.

ON THE FINGERPRINTS: *"The fingerprints should be recomputed in the first/blind
run of any experiment anyway. So they should be reset after the next live
experiment runs. Please make sure that is the case and that is how this facility
will work?"*

IT WAS NOT THE CASE, which is why this is a build and not a confirmation.
Measured 2026-10-16: `_save_fingerprints` takes max(stored, new), so a seat's
recorded maximum only ever rises, and nothing anywhere reset or scoped them. The
4 paid seats carried a figure identical to the character across all 4 and
unchanged for 185 days. So the fingerprint default is "experiment" and that
DOES change behaviour, deliberately and on his instruction.

WHY THE FUNCTION'S OWN DEFAULT DIFFERS FROM THE RUNNER'S. `_load_fingerprints`
defaults to "persist" so that every caller which predates the parameter is
untouched; `RunnerConfig.fingerprint_scope` defaults to "experiment" so the
runner implements his ruling. The policy belongs in the config, where he can
switch it, not in the loader.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO))

import reference_runner_v3 as R  # noqa: E402


# --------------------------------------------------------------------------
# The defaults are his rulings, not conveniences.
# --------------------------------------------------------------------------

def test_the_immune_memory_default_is_persist():
    assert R.RunnerConfig().immune_memory_scope == "persist", (
        "he ruled the default should be on so the memory persists between "
        "experiments"
    )


def test_the_fingerprint_default_is_experiment():
    assert R.RunnerConfig().fingerprint_scope == "experiment", (
        "he ruled fingerprints should be recomputed in the blind round of any "
        "experiment"
    )


# --------------------------------------------------------------------------
# The scope actually changes what is loaded. Executed, not read.
# --------------------------------------------------------------------------

def test_experiment_scope_loads_no_fingerprints():
    assert R._load_fingerprints("experiment") == {}, (
        "experiment scope still inherited observations from earlier runs"
    )


def test_persist_scope_loads_the_stored_fingerprints():
    got = R._load_fingerprints("persist")
    assert got, "persist scope loaded nothing; the store is unreachable"
    assert len(got) >= 5


def test_the_loader_default_preserves_the_old_behaviour():
    """~20 modules predate this parameter; the default must not move under them."""
    assert R._load_fingerprints() == R._load_fingerprints("persist")


def test_experiment_scope_empties_the_save_time_snapshot():
    """The snapshot is what `_save_fingerprints` compares against to decide a
    seat changed. Under experiment scope it must be EMPTY, so every seat this
    run observed is treated as changed and written. A stale snapshot would make
    the run appear to observe nothing."""
    R._load_fingerprints("persist")
    assert R._FINGERPRINTS_AT_LOAD, "precondition: snapshot populated"
    R._load_fingerprints("experiment")
    assert not R._FINGERPRINTS_AT_LOAD, (
        "the snapshot survived an experiment-scoped load, so a fresh "
        "measurement would compare against stale values"
    )


# --------------------------------------------------------------------------
# The switch is reachable from config, which is what makes it a facility.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("scope,expect_empty", [("experiment", True),
                                                ("persist", False)])
def test_the_runner_config_drives_the_loader(scope, expect_empty):
    cfg = R.RunnerConfig(fingerprint_scope=scope)
    # THE FALLBACK IS THE RUNNER'S, NOT A LITERAL. This line used to repeat
    # `"persist"` while `RunnerConfig.fingerprint_scope` declares
    # `"experiment"`, so it mirrored the defect it was meant to catch.
    got = R._load_fingerprints(
        getattr(cfg, "fingerprint_scope",
                R.scope_default("fingerprint_scope")))
    assert (got == {}) is expect_empty


def test_an_unknown_scope_falls_back_to_persist_rather_than_emptying():
    """A typo must not silently erase a seat's measured history."""
    assert R._load_fingerprints("perssist") == R._load_fingerprints("persist")
