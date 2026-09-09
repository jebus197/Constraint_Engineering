"""The seat watchdog must not cut inside a seat's configured retry budget.

Task 6.2. Founder ruling: *"Same answer."* — meaning build the fix, test it,
then have Fable and CC2 check it.

TWO NUMBERS, TWO FILES, NEVER COMPARED. `bench/experiment_11_orchestrator.py`
gives each seat a `timeout` and a `max_retries`, so the worst case a seat may
legitimately consume is timeout * max_retries. `bench/reference_runner_v3.py`
capped the wall clock at a fixed multiple of the timeout alone. `max_retries` is
PRESENT on every ModelConfig the runner receives and was read 0 times in that
file: the written-but-never-read half of the additive standard, on a field with
a bill attached.

MEASURED by `scripts/watchdog_vs_retry_budget_2026-09-09.py`: 1 of 5 seats was
strictly over, 20.0%, Wilson [3.6%, 62.4%]. Gemini carries `timeout=300` with
`max_retries=5`, a 1500 s budget against a 900 s cap, so the watchdog killed it
600 s inside its own allowance and the run recorded a timeout rather than a
misconfiguration.

THE TASK LIST SAID 4 OF 5 AND THAT VERB WAS WRONG. Codex, ChatGPT and DeepSeek
sit at exactly 900 s of budget against exactly 900 s of cap: not truncated, but
with 0 seconds of slack. 4 of 5 are AT-OR-OVER; 1 of 5 is OVER. Both are true and
they are different claims, so `test_the_zero_slack_seats_are_recorded_as_such`
pins the distinction rather than letting the looser one stand in for it.
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import launcher_core  # noqa: E402
from bench.reference_runner_v3 import base_model_label  # noqa: E402

RUNNER = REPO / "bench" / "reference_runner_v3.py"


def _wall_limit(mc):
    """The runner's live expression, read from source so it cannot drift.

    Deliberately EXECUTED against the real ModelConfigs rather than asserted on
    the source text: a source-text test would pass while the arithmetic was
    wrong, because the expression describes itself correctly either way."""
    src = RUNNER.read_text()
    m = re.search(
        r"_mult = (\d+) if base_model_label\(mc\.label\) == \"CC2\" else (\d+)\n"
        r"\s*_retry_budget = mc\.timeout \* max\(1, int\(getattr\(mc, \"max_retries\", 1\) or 1\)\)\n"
        r"\s*wall_limit = max\(mc\.timeout \* _mult, _retry_budget\)", src)
    assert m, "the watchdog expression has moved or changed shape"
    cc2_mult, other_mult = int(m.group(1)), int(m.group(2))
    mult = cc2_mult if base_model_label(mc.label) == "CC2" else other_mult
    retry_budget = mc.timeout * max(1, int(getattr(mc, "max_retries", 1) or 1))
    return max(mc.timeout * mult, retry_budget), mult, retry_budget


@pytest.fixture(scope="module")
def seats():
    models = launcher_core.load_experiment_config().models
    assert models, "no seats loaded, the test would be vacuous"
    return models


def test_every_seat_carries_a_retry_budget(seats):
    """The precondition. If this ever fails the fix is silently inert."""
    for mc in seats:
        assert getattr(mc, "max_retries", None), (
            f"{mc.label} carries no max_retries, so the derivation has nothing "
            f"to read and the watchdog silently falls back to the multiplier")


def test_no_seat_is_killed_inside_its_retry_budget(seats):
    """THE PROPERTY."""
    for mc in seats:
        cap, _, budget = _wall_limit(mc)
        assert cap >= budget, (
            f"{mc.label}: watchdog {cap}s cuts {budget - cap}s inside its own "
            f"{budget}s retry budget, so a run records a timeout where the "
            f"cause is a misconfiguration")


def test_no_seats_cap_is_lowered_by_the_fix(seats):
    """ADDITIVE, asserted rather than assumed.

    A naive derivation — cap := timeout * max_retries — would CUT CC2 from
    4500 s to 900 s and reinstate the timeout cascade the x5 multiplier exists
    to prevent. `max` is what makes this additive, so it is tested."""
    for mc in seats:
        cap, mult, _ = _wall_limit(mc)
        assert cap >= mc.timeout * mult, (
            f"{mc.label}: the derived cap {cap}s is below the multiplier cap "
            f"{mc.timeout * mult}s, which lowers a budget rather than raising it")


def test_cc2_keeps_its_larger_multiplier(seats):
    """The one seat whose multiplier exceeds its retry budget."""
    cc2 = [m for m in seats if base_model_label(m.label) == "CC2"]
    assert cc2, "no CC2 seat in the roster"
    cap, mult, budget = _wall_limit(cc2[0])
    assert mult == 5 and cap == cc2[0].timeout * 5 > budget


def test_exactly_the_over_budget_seats_are_raised(seats):
    """Pins WHICH seats change, so a later edit that moves more of them is loud."""
    raised = sorted(mc.label for mc in seats
                    if _wall_limit(mc)[0] > mc.timeout * _wall_limit(mc)[1])
    assert raised == ["Gemini"], (
        f"exactly the seats whose retry budget exceeds their multiplier cap "
        f"should be raised; got {raised}")


def test_the_zero_slack_seats_are_recorded_as_such(seats):
    """The distinction the task list's wording lost.

    Not truncated, but 0 seconds of slack for dispatch overhead. This test does
    NOT demand a slack allowance, because the overhead has not been measured and
    inventing a constant to cover it would be a defect, not a fix. It exists so
    the count is visible if anyone later measures that overhead."""
    # ZERO SLACK IS A PROPERTY OF THE MULTIPLIER CAP, not of the derived one.
    # A first version compared the DERIVED cap to the budget, which made Gemini
    # look like a zero-slack seat when it is the raised one -- the derived cap
    # equals the budget there precisely BECAUSE the fix raised it to meet it.
    zero_slack = sorted(mc.label for mc in seats
                        if mc.timeout * _wall_limit(mc)[1] == _wall_limit(mc)[2])
    assert zero_slack == ["ChatGPT", "Codex", "DeepSeek"], zero_slack
    at_or_over = sorted(mc.label for mc in seats
                        if _wall_limit(mc)[2] >= mc.timeout * _wall_limit(mc)[1])
    assert len(at_or_over) == 4, at_or_over
