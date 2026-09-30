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
        assert ns.rounds == 10, (
            f"{arm.key}: the cap is 10 rounds on the founder's ruling of "
            f"2026-09-30, got {ns.rounds}. It was 8 until then. The value is a "
            f"BUDGET CAP, not a derived optimum -- both free panel seats "
            f"recommended 10 and both then showed n* cannot justify it, because "
            f"the coefficient pair (4.89, 0.709) reproduces from no archived fit.")
        assert ns.target == arm.target, arm.key
        assert r.resolve_seats(ns.seats, ns.models), arm.key
        # THE CONSUMER'S VIEW OF THE GATE, which is the half that was missing.
        # A producer asserting `test_cmd is None` cannot see that argparse then
        # substitutes its own default; only parsing the argv can.
        if arm.test_cmd is None:
            assert ns.test_cmd == "", (
                f"{arm.key} declares no gate, but the runner received "
                f"{ns.test_cmd!r}. An omitted flag becomes the immune-memory "
                f"suite and FAKES the gate rather than excluding it.")
        else:
            assert ns.test_cmd == arm.test_cmd, arm.key


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


def test_the_prose_arm_targets_prose_and_EMITS_AN_EMPTY_test_command():
    """e2_regression is unavailable on prose; excluding it beats faking it.

    A test command on a prose target would make `e2` score against a suite the
    target cannot affect, which is a gate reporting a result it did not measure.

    THIS TEST PREVIOUSLY ENCODED THE DEFECT IT EXISTS TO CATCH, corrected
    2026-09-30 on the founder's ruling after both free panel seats found it
    independently. It asserted `"--test-cmd" not in arm4.argv()` -- and omitting
    the flag is EXACTLY what let `run_simulated_experiment`'s argparse substitute
    its own default, the immune-memory suite for `bench/dm/_memory.py`. The gate
    then ran against the wrong artefact and returned the constant
    52/55 = 0.9454545454545454 for every scored fix, identical on a document
    whose bytes had been destroyed.

    The test also asserted only on the PRODUCER and never parsed the argv with
    the real consumer, which is why a producer and a consumer that disagreed both
    looked correct. `execute-do-not-grep`. It now checks both ends.
    """
    a = _arms()
    arm4 = next(x for x in a.ARMS if x.key == "arm4")
    assert arm4.target.endswith(".md"), arm4.target
    assert arm4.test_cmd is None, "the declared intent is still 'no gate'"
    v = arm4.argv()
    assert "--test-cmd" in v, (
        "the flag is OMITTED, so argparse will substitute its own default and the "
        "gate will be faked rather than excluded -- the 2026-09-30 defect")
    assert v[v.index("--test-cmd") + 1] == "", (
        f"the flag carries {v[v.index('--test-cmd') + 1]!r}; an empty value is what "
        f"reaches the runner as a genuine absence")


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
