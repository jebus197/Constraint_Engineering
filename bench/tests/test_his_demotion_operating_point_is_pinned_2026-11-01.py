"""His chosen false-alarm rate for the demotion rule must not drift back.

HIS RULING, 2026-10-30, verbatim: *"I accept your recommendation."* -- against a
recommendation of 1 in 50, given in answer to his own challenge: *"Can we
improve on this statistic? A 1 in 20 chance of demoting a model that is
performing just fine seems unreasonably high?"*

WHY A TEST AND NOT A COMMENT. `CHOSEN_TARGET = 0.02` was recorded as a named
constant and a census found it in exactly 1 file -- the script that defines it.
Nothing read it and no test reached it, so his decision was a value in a
docstring's worth of code: it could revert to 0.05 with nothing to say so. Under
this project's additive standard an addition nothing reaches is not additive, and
the record holds 11 confirmed defects of that exact shape against 0 removals of
something needed.

THE 1 IN 20 WAS NEVER A LIVE SETTING, WHICH IS WHY HIS PUSHBACK WAS RIGHT
WITHOUT THE PROJECT HAVING BEEN WRONG. 0.05 is the common false-alarm level that
3 candidate rules were calibrated to on the 2026-10-08 relegation panel, so
their detection rates could be compared on equal footing. It is a COMPARISON
SIZE, not a configured threshold, and nothing in the live tree reads it. This
test pins the distinction so a later reader cannot mistake the comparison size
for the operating point and "restore" it.

WHAT THIS TEST DELIBERATELY DOES NOT DO. It does not wire the demotion rule to
anything. The rule is still connected to nothing, which this file asserts rather
than hides, and wiring it would change which models the harness uses on the
strength of a SIMULATED degradation model rather than this project's own runs.
That is a behaviour change for the founder to authorise, not a tidy-up. Pinning
the number is additive and changes nothing; wiring it is neither.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "can_we_do_better_than_one_in_twenty_2026-10-30.py"

#: His decision. Changing this line requires a ruling of his, not a judgement.
HIS_CHOICE = 0.02
#: The comparison size from the 2026-10-08 panel. NOT an operating point.
COMPARISON_SIZE = 0.05


def _load():
    spec = importlib.util.spec_from_file_location("cwdbt_2026_10_30", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    assert PRODUCER.exists(), f"the producer is gone: {PRODUCER}"
    return _load()


def test_the_chosen_target_is_his_ruling(mod):
    assert hasattr(mod, "CHOSEN_TARGET"), (
        "CHOSEN_TARGET is gone. His decision of 2026-10-30 then exists nowhere "
        "in code and the next reader re-derives it or defaults to the "
        "comparison size.")
    assert mod.CHOSEN_TARGET == pytest.approx(HIS_CHOICE), (
        f"CHOSEN_TARGET is {mod.CHOSEN_TARGET}, not his ruled {HIS_CHOICE}. "
        "He accepted 1 in 50 after challenging 1 in 20; only a further ruling "
        "of his may change it.")


def test_it_has_not_reverted_to_the_comparison_size(mod):
    assert mod.CHOSEN_TARGET != pytest.approx(COMPARISON_SIZE), (
        "CHOSEN_TARGET has reverted to 0.05, which is the 2026-10-08 panel's "
        "COMPARISON SIZE and never an operating point. This is the specific "
        "drift the test exists to catch.")


def test_the_chosen_target_is_inside_the_measured_set(mod):
    assert hasattr(mod, "TARGETS"), "TARGETS is gone"
    assert mod.CHOSEN_TARGET in mod.TARGETS, (
        f"CHOSEN_TARGET {mod.CHOSEN_TARGET} is not among the TARGETS actually "
        f"measured {mod.TARGETS}. An operating point outside the measured set "
        "is an extrapolation presented as a result.")


def test_the_comparison_size_is_still_measured_alongside_it(mod):
    """His pushback is only checkable while both numbers are reported."""
    assert COMPARISON_SIZE in mod.TARGETS, (
        "0.05 was dropped from TARGETS. It must stay measured: the whole "
        "argument for 1 in 50 is the comparison against 1 in 20, and removing "
        "the baseline would leave the recommendation unfalsifiable.")


def test_the_constant_is_reachable_from_outside_its_own_module(mod):
    """The symmetric additive standard: an addition nothing reaches is not one."""
    assert isinstance(mod.CHOSEN_TARGET, float), (
        "CHOSEN_TARGET is not a plain float, so a consumer cannot read it "
        "without parsing. It exists to be READ by whoever wires the rule.")
    # This test file IS the reach. Before it, the symbol had 0 consumers.


def test_the_rule_is_still_unwired_and_says_so(mod):
    """Pinning the number must not be mistaken for having shipped the rule.

    If the demotion rule is ever connected, this test should FAIL and be
    rewritten deliberately -- a silent transition from 'measured but unwired' to
    'live' is how a consequential gate arrives without a decision.
    """
    live = []
    for path in list((REPO / "bench").rglob("*.py")):
        if "logs/" in str(path) or "/tests/" in str(path):
            continue
        try:
            if "CHOSEN_TARGET" in path.read_text(errors="ignore"):
                live.append(str(path.relative_to(REPO)))
        except OSError:
            continue
    assert not live, (
        "CHOSEN_TARGET is now read by live bench code: "
        f"{live}. That means the demotion rule has been WIRED. This test must "
        "be rewritten to assert the wiring is correct, and the founder must "
        "have authorised it -- the calibration comes from a simulated "
        "degradation model, not from this project's own runs.")
