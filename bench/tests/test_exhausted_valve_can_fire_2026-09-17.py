"""I23: the exhausted-round valve must be able to open inside the run it governs.

FOUNDER RULING 2026-09-16: *"Set it to 6 in the next simulated run ... There is
no point having machinery that in effect does nothing."*

THE DEFECT. `exhausted_round_threshold` defaults to 8 and all 3 experiment 56
arms set `max_rounds: 8`. The runner marks a finding EXHAUSTED when
`age >= exhausted_threshold`, where age counts rounds since the last status
change. A finding cannot be 8 rounds stale inside an 8-round run, so the valve
could never open and the repaired routing valve stayed inert.

These tests LOAD the real configs through the real loader and evaluate the
runner's own predicate. They do not assert on source text: `from_dict` silently
drops unknown keys, so a config could carry the key and the runner still never
see it, and only loading proves otherwise.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CONFIGS = sorted((REPO / "bench" / "exp56_configs").glob("*.json"))


@pytest.fixture(scope="module")
def runner():
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(
        "rrv3", REPO / "bench" / "reference_runner_v3.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["rrv3"] = m
    spec.loader.exec_module(m)
    return m


def test_there_are_three_arms():
    assert len(CONFIGS) == 3, [p.name for p in CONFIGS]


@pytest.mark.parametrize("path", CONFIGS, ids=lambda p: p.name)
def test_the_loader_actually_carries_the_threshold(runner, path):
    """THE KEY MUST SURVIVE `from_dict`, which drops unknown keys silently."""
    cfg = runner.RunnerConfig.from_json(str(path))
    assert cfg.exhausted_round_threshold == 6, (
        f"{path.name}: the runner sees {cfg.exhausted_round_threshold}, not 6")


@pytest.mark.parametrize("path", CONFIGS, ids=lambda p: p.name)
def test_the_valve_can_open_inside_the_run(runner, path):
    """The runner's own condition, evaluated: `age >= threshold` must be reachable."""
    cfg = runner.RunnerConfig.from_json(str(path))
    t, r = cfg.exhausted_round_threshold, cfg.max_rounds
    reachable = [age for age in range(r + 1) if t > 0 and age >= t]
    assert reachable, (
        f"{path.name}: threshold {t} against max_rounds {r} -- unsatisfiable, "
        f"the valve is inert exactly as it was before this fix")
    assert min(reachable) < r, (
        f"{path.name}: the valve first opens at round {min(reachable)} of {r}, "
        f"leaving no round in which the bypass can act")


def test_the_old_setting_would_still_fail(runner):
    """POSITIVE CONTROL. A test that cannot fail proves nothing.

    With the previous default of 8 against `max_rounds: 8`, a finding reaches
    age 8 only at the final round boundary, so the bypass has no round left to
    act in. This reproduces that, so the test above is not vacuous.
    """
    t, r = 8, 8
    reachable = [age for age in range(r + 1) if age >= t]
    assert reachable == [8]
    assert min(reachable) >= r, "the old setting left a usable round after all"


@pytest.mark.parametrize("path", CONFIGS, ids=lambda p: p.name)
def test_the_file_on_disk_is_valid_json_and_unchanged_elsewhere(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    assert d["max_rounds"] == 8
    assert d["exhausted_round_threshold"] == 6
    assert len(d) >= 64, "keys were lost while editing"
