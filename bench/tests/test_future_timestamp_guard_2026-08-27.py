"""A note may not claim a time it has not reached.

WHY, AND WHY IT IS NOT THE DEFECT ALREADY FIXED. On 2026-08-26 five timestamps
were TYPED rather than read, three of them in the future, and the response was a
UserPromptSubmit clock hook that supplies the time at turn start. That hook
worked: on 2026-08-27 it supplied 00:40.

The failure that night was different. The time was known once, at turn start,
and then extrapolated forward across a thirty-minute turn. Two notes were
stamped 01:30 and 01:35 while the clock read 01:11 -- 18 and 23 minutes in the
future. A hook that fires at turn START cannot fix a turn that RUNS for half an
hour.

So this check compares the note's own stated stamp against the file's mtime,
which is the only witness that does not depend on remembering to look.

Two minutes of slack: writing takes a moment and minute-rounding can legitimately
land one minute ahead.
"""
import datetime as dt
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import note_vagueness_lint as lint  # noqa: E402


def _write(tmp_path, name, stamp_dt, mtime_dt=None):
    p = tmp_path / name
    p.write_text(f"A NOTE\n\n{stamp_dt:%Y-%m-%d} {stamp_dt:%H:%M} BST (UTC+1)\n\n"
                 "Body text long enough to be a sentence for the linter.\n",
                 encoding="utf-8")
    if mtime_dt is not None:
        ts = mtime_dt.timestamp()
        import os
        os.utime(p, (ts, ts))
    return p


class TestItDiscriminates:
    def test_known_bad_a_stamp_ahead_of_the_file_is_reported(self, tmp_path):
        """The actual defect: note says 01:30, file written at 01:11."""
        now = dt.datetime(2026, 8, 27, 1, 11)
        p = _write(tmp_path, "future.txt", now + dt.timedelta(minutes=19), now)
        hit = lint.future_stamp(p)
        assert hit is not None, "a stamp 19 minutes in the future was not reported"
        assert hit[0].endswith("01:30") and hit[1].endswith("01:11")

    def test_known_good_a_stamp_matching_the_file_passes(self, tmp_path):
        now = dt.datetime(2026, 8, 27, 1, 11)
        p = _write(tmp_path, "ok.txt", now, now)
        assert lint.future_stamp(p) is None, "a correct stamp was reported as future"

    def test_known_good_a_stamp_in_the_PAST_passes(self, tmp_path):
        """Notes are often written up after the fact. Only the future is wrong."""
        now = dt.datetime(2026, 8, 27, 1, 11)
        p = _write(tmp_path, "past.txt", now - dt.timedelta(hours=6), now)
        assert lint.future_stamp(p) is None

    def test_one_minute_of_rounding_is_tolerated(self, tmp_path):
        """A linter that fires on minute-rounding gets ignored."""
        now = dt.datetime(2026, 8, 27, 1, 11)
        p = _write(tmp_path, "round.txt", now + dt.timedelta(minutes=1), now)
        assert lint.future_stamp(p) is None

    def test_the_two_answers_differ(self, tmp_path):
        now = dt.datetime(2026, 8, 27, 1, 11)
        bad = lint.future_stamp(_write(tmp_path, "b.txt", now + dt.timedelta(minutes=19), now))
        good = lint.future_stamp(_write(tmp_path, "g.txt", now, now))
        assert (bad is None) != (good is None), "the check answers the same way to both"


class TestItNeverRaises:
    def test_a_note_with_no_stamp_is_not_an_error(self, tmp_path):
        p = tmp_path / "nostamp.txt"
        p.write_text("A NOTE\n\nNo date line at all here.\n", encoding="utf-8")
        assert lint.future_stamp(p) is None

    def test_a_missing_file_is_not_an_error(self, tmp_path):
        assert lint.future_stamp(tmp_path / "absent.txt") is None

    def test_an_unparseable_date_is_not_an_error(self, tmp_path):
        p = tmp_path / "bad.txt"
        p.write_text("A NOTE\n\n2026-13-45 99:99 BST\n\nBody.\n", encoding="utf-8")
        assert lint.future_stamp(p) is None


def test_it_is_wired_into_the_lint_report():
    """A check nobody runs is the shape this project keeps finding."""
    src = (REPO / "scripts" / "note_vagueness_lint.py").read_text(encoding="utf-8")
    assert "future_stamp(p)" in src, "the check is defined but never called by main"
    assert "FUTURE TIMESTAMP" in src
