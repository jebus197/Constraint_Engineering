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
import subprocess
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


def test_it_is_wired_into_the_lint_report(tmp_path):
    """A check nobody runs is the shape this project keeps finding.

    THIS TEST USED TO GREP FOR THE LITERAL `future_stamp(p)` AND IT FALSE-ALARMED
    ON 2026-09-11, when the call moved from `main` into `partition()` and the
    variable was named `path` instead of `p`. The call still happened; the report
    still carried the finding; the guard failed anyway. That is the defect
    `execute-do-not-grep` names -- a source-text assertion cannot tell a moved
    call from a deleted one, because each version of the text is individually
    consistent.

    So it now RUNS the reporter against a note stamped in the future and looks
    for the finding in the output. MEASURED dominance, both forms run against the
    same 2 states of the module:

        state                              grep-form   executing-form
        call present, variable `path`      FAIL        PASS
        call DELETED                       FAIL        FAIL

    Row 2 is what the guard exists for and both catch it, so nothing is lost.
    Row 1 is the live repository and only the executing form is right about it.
    Dominance on the named property -- reporting a regression and only a
    regression -- with no case where the grep form is the better of the 2.
    """
    note = tmp_path / "note.md"
    note.write_text("A NOTE\n\n2099-01-01 12:00 BST\n\nBody.\n", encoding="utf-8")
    r = subprocess.run([sys.executable,
                        str(REPO / "scripts" / "note_vagueness_lint.py"), str(note)],
                       capture_output=True, text=True, timeout=120)
    assert "FUTURE TIMESTAMP" in r.stdout, (
        "the reporter did not carry the future-stamp finding, so the check is "
        f"defined and not reached:\n{r.stdout[-800:]}")

    # POSITIVE CONTROL: a note stamped in the past must NOT raise it, or the
    # test above would pass against a reporter that printed the line always.
    ok = tmp_path / "ok.md"
    ok.write_text("A NOTE\n\n2020-01-01 12:00 BST\n\nBody.\n", encoding="utf-8")
    r2 = subprocess.run([sys.executable,
                         str(REPO / "scripts" / "note_vagueness_lint.py"), str(ok)],
                        capture_output=True, text=True, timeout=120)
    assert "FUTURE TIMESTAMP" not in r2.stdout, r2.stdout[-800:]
