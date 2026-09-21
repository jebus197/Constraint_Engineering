"""The arms must carry the settings the programme specifies, checked by parsing.

`CDSFL_Programme_of_Study_2026-09-17.txt` asks for exactly this: a caller for the
arms "and a test that asserts the settings the runner actually received".

The arms are DATA in `bench/tools/commissioning_arms_2026-09-21.py`, and this
test feeds each one's own argv through the runner's own `build_parser()`. So the
settings asserted are the ones the runner would really receive, not a second copy
of the intent that could drift from the first -- the failure `execute-do-not-grep`
names, and the same failure that put a source-text matcher in
`test_panel_lists_must_agree_2026-08-30.py` where an executing check belonged.

Nothing here launches an experiment or spends anything: every seat resolves to a
`-SIM` stand-in and no dispatch is constructed.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ARMS_MODULE = REPO / "bench" / "tools" / "commissioning_arms_2026-09-21.py"
RUNNER = REPO / "bench" / "tools" / "run_simulated_experiment.py"


def _load(path: Path, name: str):
    """Load by path, REGISTERING IN sys.modules before executing.

    The registration is not optional here. The arms module uses
    `from __future__ import annotations`, so its dataclass field types are
    strings, and `dataclasses` resolves them by looking the class's module up in
    `sys.modules`. Without the registration that lookup returns None and class
    creation dies with "'NoneType' object has no attribute '__dict__'" -- which
    reads like a bug in the module under test and is a bug in the loader.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def _arms():
    return _load(ARMS_MODULE, "commissioning_arms")


def _runner():
    return _load(RUNNER, "run_simulated_experiment_for_arms")


def test_the_arms_module_exists_and_imports():
    assert ARMS_MODULE.is_file(), f"the arm caller is gone: {ARMS_MODULE}"
    _arms()


def test_every_arm_parses_through_the_runners_own_parser():
    """The settings the runner ACTUALLY receives, not a restatement of them."""
    a, r = _arms(), _runner()
    parser = r.build_parser()
    for arm in a.ARMS:
        ns = parser.parse_args(arm.argv())
        assert ns.rounds == 8, f"{arm.key}: the programme specifies 8 rounds, got {ns.rounds}"
        assert ns.target == arm.target, arm.key
        assert r.resolve_seats(ns.seats, ns.models), arm.key


def test_every_arm_resolves_to_simulated_seats_only():
    """Provenance: no arm may dispatch anything but a `-SIM` stand-in."""
    a, r = _arms(), _runner()
    for arm in a.ARMS:
        seats = r.resolve_seats(arm.seats, 6)
        assert seats, arm.key
        for s in seats:
            assert s.endswith("-SIM"), f"{arm.key} would dispatch {s}, which is not simulated"


def test_the_seat_contrast_arm_is_the_pair_the_programme_names():
    a, r = _arms(), _runner()
    arm3 = next(x for x in a.ARMS if x.key == "arm3")
    assert r.resolve_seats(arm3.seats, 6) == ["Codex-SIM", "ChatGPT-SIM"]


def test_the_panel_arm_is_five_seats_and_excludes_fable():
    """The 17 September programme lists CC2, Codex, Gemini, DeepSeek, ChatGPT."""
    a, r = _arms(), _runner()
    arm1 = next(x for x in a.ARMS if x.key == "arm1")
    seats = r.resolve_seats(arm1.seats, 6)
    assert len(seats) == 5, seats
    assert "Fable-SIM" not in seats, seats


def test_the_prose_arm_targets_prose_and_passes_no_test_command():
    """e2_regression is unavailable on prose; excluding it beats faking it.

    A test command on a prose target would make `e2` score against a suite the
    target cannot affect, which is a gate reporting a result it did not measure.
    """
    a = _arms()
    arm4 = next(x for x in a.ARMS if x.key == "arm4")
    assert arm4.target.endswith(".md"), arm4.target
    assert arm4.test_cmd is None
    assert "--test-cmd" not in arm4.argv()


def test_the_code_bearing_arms_run_a_test_command_that_exercises_their_target():
    """The runner's default suite is tied to a module these arms never touch."""
    a = _arms()
    for arm in a.ARMS:
        if arm.target.endswith(".py"):
            assert arm.test_cmd and "test_policy_engine" in arm.test_cmd, (
                f"{arm.key} would measure regressions in a module it does not touch: "
                f"{arm.test_cmd}")


def test_every_named_target_exists():
    a = _arms()
    for arm in a.ARMS:
        assert (REPO / arm.target).is_file(), f"{arm.key}: missing target {arm.target}"


def test_the_arms_have_distinct_names_so_logs_cannot_collide():
    a = _arms()
    names = [arm.name for arm in a.ARMS]
    assert len(names) == len(set(names)), names


def test_every_arm_launches_through_the_sandboxed_wrapper():
    """Founder ruling 2026-09-01: a simulation never runs on the live repository."""
    a = _arms()
    for arm in a.ARMS:
        cmd = a.command(arm)
        assert cmd[0] == "bash" and cmd[1] == a.SANDBOXED, cmd


def test_printing_is_the_default_so_nothing_runs_by_accident():
    a = _arms()
    assert a.main.__module__
    # `--run` must be explicit; the module must not execute arms on import.
    assert "--run" in ARMS_MODULE.read_text()


@pytest.mark.parametrize("key", ["arm1", "arm2", "arm3", "arm4"])
def test_each_expected_arm_is_present(key):
    a = _arms()
    assert any(x.key == key for x in a.ARMS), key


def test_arm_five_is_deliberately_absent():
    """It needs a checkout of `a2a0197`, not a flag, and must not be implied."""
    a = _arms()
    assert not any(x.key == "arm5" for x in a.ARMS), (
        "arm 5 is the paired baseline against a pre-window commit; listing it here "
        "would imply this launcher can produce it, and it cannot"
    )
