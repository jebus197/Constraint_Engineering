"""A recorded dispatch failure cannot lower a paid seat's routing ceiling.

THIS IS A CHANGE DETECTOR, NOT A CORRECTNESS GUARD, and the distinction matters
for whoever reads a failure here. It pins a behaviour the founder has NOT yet
ruled on, so that the behaviour cannot change without someone noticing.

WHAT IS PINNED, measured by execution on 2026-10-17 through
`scripts/can_a_measured_failure_ever_lower_the_ceiling_2026-10-17.py`. A paid
seat's effective ceiling is 418,686 characters, from
`max_successful_prompt_chars` of 465,206 taken at 90%. Injecting a recorded
FAILURE at 80,000 characters, or at 10,000, leaves it at 418,686 -- UNCHANGED.
The failure applies only when the success field is 0, where the ceiling becomes
80,001. The cause is the shape of the consumer in
`bench/reference_runner_v3.py`: `max_failed_prompt_chars` is read inside the
`else` of `if observed > 0`, and all 5 paid seats have a non-zero observed
maximum.

SO `max_failed_prompt_chars` CAN NEVER REACH THE CEILING at all, rather
than merely not having done so yet. Task B12
recorded that it *"has never fired"*; this is the stronger statement, and it
changes which of the founder's 3 options is available: bounding the ceiling by a
measured failure needs the CONSUMER changed, not only the recorder.

IF THIS TEST GOES RED, THE FIRST QUESTION IS WHETHER HIS RULING LANDED. A red
here after a deliberate change to the routing ceiling is the ruling taking
effect and the test should be rewritten to pin the new behaviour. A red with no
such change is a routing ceiling that moved by accident, which is the case worth
catching -- it alters what every paid seat is sent.
"""
from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

#: 90% of 465,206, as the live predicate computes it.
CEILING_TODAY = 418_686
PAID_SEAT = {"max_successful_prompt_chars": 465_206,
             "max_failed_prompt_chars": 0}


class _Cfg:
    pre_decompose_models = ()


class _Mgr:
    config = _Cfg()


@pytest.fixture(scope="module")
def runner():
    import bench.reference_runner_v3 as mod
    return mod


def _ceiling(runner, fingerprint: dict) -> int:
    """The largest size the LIVE routing predicate admits, by bisection.

    Bisected rather than re-derived from the formula: re-deriving would assert
    that this test and the runner agree about arithmetic, which is not the
    property in question.
    """
    original = runner._load_fingerprint_cache
    runner._load_fingerprint_cache = lambda: {"PROBE": dict(fingerprint)}
    try:
        lo, hi = 0, 4_000_000
        for _ in range(48):
            mid = (lo + hi) // 2
            if runner._decomposition_is_futile("PROBE", _Mgr(), mid):
                hi = mid
            else:
                lo = mid
        return hi
    finally:
        runner._load_fingerprint_cache = original


def test_the_paid_ceiling_is_where_the_measurement_says(runner):
    assert _ceiling(runner, PAID_SEAT) == CEILING_TODAY


@pytest.mark.parametrize("failure_chars", [10_000, 80_000, 200_000, 465_205])
def test_a_recorded_failure_is_ignored_while_a_success_exists(
        runner, failure_chars):
    """Every size of failure, including one just under the success, is ignored.

    Parametrised rather than asserted once, because "ignored" must hold across
    the range for the claim to be about the STRUCTURE of the consumer rather
    than about one convenient number.
    """
    fp = dict(PAID_SEAT, max_failed_prompt_chars=failure_chars)
    assert _ceiling(runner, fp) == CEILING_TODAY, (
        f"a failure recorded at {failure_chars:,} moved the ceiling. If his "
        f"ruling on task B12 has landed, rewrite this test to pin the new "
        f"behaviour; if not, the paid routing ceiling has moved by accident.")


def test_the_failure_does_apply_when_no_success_is_recorded(runner):
    """The arm is not dead code -- it is unreachable only while a success exists.

    Asserted so the finding is not overstated. The recorder and the consumer
    both work; what fails is that they can never both be in play at once on a
    seat that has ever succeeded.
    """
    fp = {"max_successful_prompt_chars": 0, "max_failed_prompt_chars": 80_000}
    assert _ceiling(runner, fp) == 80_001


def test_the_failure_detector_still_tests_one_literal_phrase():
    """The recorder fires only on the words "context length".

    PINNED RATHER THAN WIDENED. A narrow phrase was the obvious suspect for why
    the arm never fired, and the archive refuted it: across 172 archived json
    files carrying an error field and 37 distinct error strings, 0 are
    overflow-shaped under a deliberately broad pattern. No dispatch has ever hit
    a context limit, so the phrase is UNTESTED rather than wrong, and widening
    an untested predicate on no evidence is the shape of fix the founder
    objected to on 2026-10-13 and 2026-10-14.

    This asserts the source text deliberately, which is the exception to
    `execute-do-not-grep` rather than a breach of it: the property is that NO
    ONE HAS QUIETLY WIDENED the predicate, and there is no execution that
    distinguishes a wider predicate from a narrower one without an overflow
    error to feed it, which the archive does not contain.
    """
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    assert '"context length" in str(dispatch_error).lower()' in src, (
        "the overflow detector changed. If it was widened deliberately, say so "
        "in task B12 and record what evidence justified it -- the archive holds "
        "0 overflow errors of any phrasing to test it against.")
