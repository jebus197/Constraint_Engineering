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
import os
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
        """★ THE WRITE TIME IS PINNED, NOT TAKEN FROM THE WALL CLOCK (2026-11-03).

        This read `now = datetime.now()` and `ahead = now + 2 hours`. Between
        22:00 and 23:59 that addition WRAPS PAST MIDNIGHT, so the header carried
        a clock like `00:42` while the prose date still named the write day --
        a claimed time about 22 hours in the PAST, which the rule correctly
        stays silent about. The test then failed, and it failed for 2 of every
        24 hours. Measured by driving the same case at 8 hours of the day:
        ACCUSE at 00, 06, 10, 14, 18 and 21; SILENT at 22 and 23.

        THE SUBJECT WAS NEVER WRONG, and that distinction is the point. Nothing
        in `future_stamp` changed; the probe manufactured the failure. Repairing
        the rule here would have broken correct code to satisfy a broken test,
        which is the shape the record already names twice.

        The write time is now pinned by setting the file's own mtime, so the
        '2 hours ahead' relation holds whatever time this suite runs at.
        """
        base = dt.datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        ahead = base + dt.timedelta(hours=2)
        p = _note(tmp_path, "Clock_Ahead.md", base, f"{ahead:%H:%M}")
        os.utime(p, (base.timestamp(), base.timestamp()))
        assert nvl.future_stamp(p) is not None, (
            "a note claiming a time 2 hours after it was written was not "
            "caught, so the rule no longer does its job")

    def test_the_pinned_probe_is_not_itself_time_of_day_dependent(self, nvl, tmp_path):
        """THE REGRESSION GUARD FOR THE FLAKE, driven at every hour of the day.

        ★ THE LAST 2 HOURS ARE EXCLUDED, AND THE EXCLUSION IS ASSERTED RATHER
        THAN SKIPPED. At 22:00 and 23:00 a clock '2 hours ahead' falls on the
        NEXT day, and a bare clock beside a same-day prose date cannot express a
        next-day time at all -- `00:00` beside `3 November 2026` means midnight
        at the START of the 3rd. So the rule's silence there is CORRECT, and a
        test that demanded an accusation would be demanding a wrong answer.

        An excluded case that is merely missed is the defect the record names,
        so the 2 degenerate hours are checked for the silence the structure
        implies instead of being dropped from the loop.
        """
        expressible, degenerate = [], []
        for hour in range(24):
            base = dt.datetime.now().replace(hour=hour, minute=0, second=0,
                                             microsecond=0)
            ahead = base + dt.timedelta(hours=2)
            p = _note(tmp_path, f"Clock_Ahead_{hour:02d}.md", base,
                      f"{ahead:%H:%M}")
            os.utime(p, (base.timestamp(), base.timestamp()))
            fired = nvl.future_stamp(p) is not None
            (degenerate if ahead.date() != base.date() else expressible).append(
                (hour, fired))

        assert [h for h, _ in degenerate] == [22, 23], (
            f"the wrap-around hours are {[h for h, _ in degenerate]}, not "
            f"[22, 23]. The arithmetic this test reasons about has changed.")
        missed = [h for h, fired in expressible if not fired]
        assert not missed, (
            f"the rule stays silent for a clock 2 hours ahead when the note is "
            f"written at hour(s) {missed}, where that time IS expressible. A "
            f"guard whose verdict depends on the hour it runs at is worse than "
            f"a red one, because its green means nothing.")
        wrongly_fired = [h for h, fired in degenerate if fired]
        assert not wrongly_fired, (
            f"hour(s) {wrongly_fired} produced an accusation from a clock that "
            f"wrapped to the next day, i.e. a time ~22 hours in the PAST. That "
            f"is a false accusation, not a catch.")

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
        clock and no date has nothing else to be dated from.

        ★ THE WRITE TIME IS PINNED (2026-11-03), for the same reason as the
        sibling case above: `now + 3 hours` wraps past midnight after 21:00, so
        the header claimed a time in the PAST and the rule was right to stay
        silent. Pinning the mtime to 10:00 makes the '3 hours ahead' relation
        hold whatever hour this suite runs at.
        """
        p = tmp_path / "No_Date.md"
        base = dt.datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        ahead = base + dt.timedelta(hours=3)
        p.write_text(f"# A note\n\nFinished at {ahead:%H:%M} GMT\n\nbody\n",
                     encoding="utf-8")
        os.utime(p, (base.timestamp(), base.timestamp()))
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
