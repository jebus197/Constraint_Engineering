"""A bare clock in a note's header is dated from the header, not from the mtime.

THE DEFECT, FOUND 2026-11-03 BY THE RULE BLOCKING A COMMIT. A reply file written
at 23:38 on 2 November, stamped "2 November 2026, 23:40 GMT", was reported as
claiming "2026-11-03 23:40" -- 23 hours in the future -- because the commit hook
lints a temporary copy and the clock had passed midnight before the check ran.

THE CAUSE. `future_stamp` prefers an ISO stamp that `STAMP_LINE` can parse, and
falls back to a bare clock time in the header which it dates FROM THE FILE'S
MTIME. That is right only while a note is never touched again. MEASURED over the
639 notes in experimental_notes/: only 145 carry a stamp `STAMP_LINE` parses
against 205 carrying a bare clock, so the mtime-dated fallback is the branch
that normally runs -- 205 of 350, 0.585714, Wilson 95% [0.533449, 0.636118]. Of
the 53 notes the rule accused, 16 carried a prose date in the very same header
that exonerated them: 0.301887, Wilson 95% [0.195183, 0.435368]. Producer:
`scripts/a_bare_clock_was_dated_from_the_mtime_2026-11-03.py`.

THE FIX IS ADDITIVE. The fallback now reads the prose date already sitting in
the header and uses mtime only when none is present. The comparison against
mtime is unchanged, so a genuine future stamp is still accused -- and the
accusation now quotes the day the note actually names.

WHY BOTH DIRECTIONS ARE TESTED HERE. A rule that stops accusing is
indistinguishable, from the outside, from a rule that has been switched off, and
the standing lesson in this project is that a false positive is how a
report-only linter becomes ignored while a true positive hides behind it. So
these tests pin the silence AND the noise.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LINT = REPO / "scripts" / "note_vagueness_lint.py"
NOTES = REPO / "experimental_notes"


@pytest.fixture(scope="module")
def nvl():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_nvl_guard", LINT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_nvl_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


def _note(tmp_path, name, date, clock, body="body\n"):
    p = tmp_path / name
    p.write_text(f"# A note\n\n{date.day} {date:%B} {date.year}, {clock} GMT\n\n"
                 f"{body}", encoding="utf-8")
    return p


class TestAHeaderDateBeatsTheMtime:
    def test_a_note_edited_on_a_later_day_is_not_accused(self, nvl, tmp_path):
        """THE FIX. The note claims a time on ITS OWN date; touching the file
        later must not turn that into a claim about the later day."""
        then = dt.datetime.now() - dt.timedelta(days=40)
        p = _note(tmp_path, "Edited_Later.md", then, "23:50")
        # mtime is now, 40 days after the date the header states
        assert nvl.future_stamp(p) is None, (
            "a note stamped 40 days ago was accused of claiming today's date "
            f"at its stated time: {nvl.future_stamp(p)}")

    def test_the_accusation_quotes_the_day_the_note_names(self, nvl, tmp_path):
        """When it DOES accuse, the claimed date must be the one in the header,
        not the mtime's. An accusation that misquotes the note is unactionable."""
        tom = dt.datetime.now() + dt.timedelta(days=1)
        p = _note(tmp_path, "Dated_Tomorrow.md", tom, "09:00")
        got = nvl.future_stamp(p)
        assert got is not None, "a header dated tomorrow was not accused"
        assert got[0].startswith(tom.strftime("%Y-%m-%d")), (
            f"the accusation quotes {got[0]!r}, which is not the day the "
            f"header names ({tom:%Y-%m-%d})")


class TestItStillCatchesWhatItIsFor:
    """ANTI-VACUITY. Without these the fix could have switched the rule off."""

    def test_a_same_day_clock_ahead_of_the_write_is_caught(self, nvl, tmp_path):
        now = dt.datetime.now()
        ahead = now + dt.timedelta(hours=2)
        p = _note(tmp_path, "Clock_Ahead.md", now, f"{ahead:%H:%M}")
        assert nvl.future_stamp(p) is not None, (
            "a note claiming a time 2 hours after it was written was not "
            "caught, so the rule no longer does its job")

    def test_an_iso_stamp_is_still_read_in_preference(self, nvl, tmp_path):
        """The ISO branch must be untouched: it carries its own date and must
        not be overridden by a prose date elsewhere in the header."""
        p = tmp_path / "Iso_Stamped.md"
        future = dt.datetime.now() + dt.timedelta(days=2)
        p.write_text(f"# A note\n\n{future:%Y-%m-%d}, 09:00 GMT\n\nbody\n",
                     encoding="utf-8")
        assert nvl.future_stamp(p) is not None, (
            "an ISO stamp dated 2 days ahead was not caught")

    def test_a_note_with_no_date_at_all_still_falls_back_to_the_mtime(self, nvl, tmp_path):
        """The mtime fallback is RETAINED, not replaced. A header with a bare
        clock and no date has nothing else to be dated from."""
        p = tmp_path / "No_Date.md"
        ahead = dt.datetime.now() + dt.timedelta(hours=3)
        p.write_text(f"# A note\n\nFinished at {ahead:%H:%M} GMT\n\nbody\n",
                     encoding="utf-8")
        assert nvl.future_stamp(p) is not None, (
            "a dateless header claiming a time 3 hours ahead was not caught, "
            "so the mtime fallback has been lost rather than narrowed")


class TestTheCorpusFigureIsRecomputed:
    def test_the_rule_accuses_no_more_than_it_did_before_the_fix(self, nvl):
        """The fix may only REMOVE accusations, never add any. 53 was the count
        before it; anything above that means the change made things worse."""
        if not NOTES.is_dir():
            pytest.skip("experimental_notes/ is not present here")
        notes = sorted(NOTES.rglob("*.md"))
        if not notes:
            pytest.skip("no notes present")
        fires = sum(1 for f in notes if nvl.future_stamp(f) is not None)
        assert fires <= 53, (
            f"the rule now accuses {fires} notes against 53 before the fix, so "
            f"reading the header's date has made it MORE accusatory, which is "
            f"the opposite of the intent")

    def test_the_prose_date_pattern_reads_the_form_notes_actually_use(self, nvl):
        """A pattern that matches nothing is an addition nothing reaches."""
        for header in ("15 April 2026, 22:40 GMT", "2 November 2026, 23:40 GMT",
                       "20 September 2026 23:58 BST (Europe/London)"):
            assert nvl._PROSE_DATE_IN_HEADER.search(header), (
                f"the prose-date pattern does not read {header!r}, which is a "
                f"form this project's notes actually use")
