#!/usr/bin/env python3
"""The alarm channel must speak on a queue OVER its bound, not on the word.

THE DEFECT, measured. The runner prints the static HIL queue at every round
close, and the line carries the word ALARM whether or not an alarm is
warranted:

    static HIL queue: 2 unresolved critical(s) (...) ; HALT ALARM if > 2

That is a THRESHOLD STATEMENT. The watchdog's `TROUBLE` pattern matched the
word, so the line woke the model at every round close of every run. Measured
2026-10-03 over 291 archived log files: 74 lines contain `ALARM` or `HALTED`,
21 of them are this conditional line, and in only 2 of those 21 was the queue
actually over its bound -- so 19 of 74 alarm-channel wakes, 25.6757%, Wilson
[17.0977%, 36.6544%], were the line saying nothing was wrong.

This is the FOURTH pattern-calibration defect in that file and the same shape as
the other 3: a pattern matching more than it means, in a channel whose only
value is being believed.

NOT DELETED, PROMOTED, and the distinction matters. `CRITICAL` was dropped
because it had 0 true matches. This token has 2, so dropping it would lose a
real signal. Reading the 2 numbers gives the channel a precision the word never
had: it can tell a queue AT its bound from one OVER it, which is exactly the
distinction the founder's rule turns on -- "an unusually high irreducible queue
is invariably a signal of mechanical failure", and "unusually high" is a
comparison, not a word.

WHAT THESE TESTS HOLD. The decision is EXECUTED on planted lines rather than
asserted about the file's text, and the cases cover both directions: a queue
over its bound must still wake the model, a queue at or under it must not, an
unparseable line must wake it rather than be guessed at, and every other true
token -- HALTED, a traceback, a red suite -- must be untouched.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "cy_watchdog_2026-10-02.py"

QUEUE_LINE = ("[10:19:44]   static HIL queue: {q} unresolved critical(s) "
              "({x} ladder-exhausted, {y} never assessed — no runnable "
              "falsifier) — excluded from the A4 blocker; HALT ALARM if > {b}")


@pytest.fixture(scope="module")
def cy() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("cy_under_test", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def _channel(cy, line: str, tmp_path=None) -> str:
    """What the REAL probe says about this line: silent, figure, or trouble.

    THIS RUNS THE WATCHDOG. The first version of this helper reimplemented the
    decision -- `TROUBLE.search` then `queue_alarm_warranted` -- and a mutation
    that made the probe IGNORE the queue reader left all 16 tests green,
    because nothing here touched the probe. That is `execute-do-not-grep`
    (2026-09-04) in a fresh disguise, and "verify the DECIDING layer" is the
    standing correction for it. The watchdog has a `--once` mode built for this
    purpose; it is used.
    """
    import subprocess
    import tempfile
    d = pathlib.Path(tmp_path or tempfile.mkdtemp())
    log = d / "console.log"
    log.write_text(line + "\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--log", str(log), "--once",
         "--pid", str(__import__("os").getpid())],
        capture_output=True, text=True, timeout=120)
    out = r.stdout + r.stderr
    if "TROUBLE" in out or "BACKLOG LINE" in out:
        return "trouble"
    if "QUEUE" in out:
        return "figure"
    return "silent"


class TestTheQueueIsReadNotMatched:
    def test_a_queue_at_its_bound_does_not_cry_wolf(self, cy):
        line = QUEUE_LINE.format(q=2, x=0, y=2, b=2)
        assert _channel(cy, line) == "figure", (
            "a queue AT its bound still reaches the trouble channel, so the "
            "channel wakes the model at every round close of every run")

    def test_a_queue_under_its_bound_does_not_cry_wolf(self, cy):
        assert _channel(cy, QUEUE_LINE.format(q=0, x=0, y=0, b=2)) == "figure"

    def test_a_queue_over_its_bound_still_wakes_the_model(self, cy):
        """ANTI-VACUITY. This is the signal the founder's rule turns on."""
        line = QUEUE_LINE.format(q=3, x=1, y=2, b=2)
        assert _channel(cy, line) == "trouble", (
            "a queue OVER its bound no longer wakes anyone; the fix has "
            "silenced the very signal it was meant to sharpen")

    def test_a_large_queue_over_a_large_bound_is_read_numerically(self, cy):
        """Not a special case for 2 and 3: the comparison is arithmetic."""
        assert _channel(cy, QUEUE_LINE.format(q=11, x=5, y=6, b=10)) == "trouble"
        assert _channel(cy, QUEUE_LINE.format(q=10, x=5, y=5, b=10)) == "figure"

    def test_an_unparseable_line_wakes_rather_than_guesses(self, cy):
        """A reading that cannot be taken is not a reading of safety."""
        line = "static HIL queue: ? unresolved critical(s) HALT ALARM if > ?"
        assert _channel(cy, line) == "trouble"

    def test_the_helper_says_when_a_line_is_not_its_business(self, cy):
        for line in ("HALTED: the irreducible queue exceeded its bound",
                     "Traceback (most recent call last):",
                     "9868 passed, 0 failed"):
            assert cy.queue_alarm_warranted(line) is None, (
                f"the queue reader claimed a verdict on an unrelated line: "
                f"{line!r}")


class TestEveryOtherTrueTokenIsUntouched:
    @pytest.mark.parametrize("line", [
        "HALTED: the irreducible queue exceeded its bound",
        "Traceback (most recent call last):",
        "3 failed, 9372 passed in 3217.53s",
        "corrected copy REFUSED C0002 from DeepSeek-SIM",
        "PermissionError: [Errno 13]",
        "API Error: Response stalled mid-stream",
    ])
    def test_it_still_speaks(self, cy, line):
        assert _channel(cy, line) == "trouble", (
            f"a true token stopped speaking: {line!r}")

    @pytest.mark.parametrize("line", [
        "8,878 passed, 0 failed, 6 skipped",
        "corrected copies: 4 derived, 0 refused",
        "gamma_critical 0.336 >= 0.30, critical-quiescence 3",
        "the control cannot reach the target it reads",
    ])
    def test_it_still_stays_silent(self, cy, line):
        assert _channel(cy, line) == "silent", (
            f"a known-noise line started speaking again: {line!r}")
