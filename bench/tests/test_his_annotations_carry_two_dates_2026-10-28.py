#!/usr/bin/env python3
r"""A response file carries 2 dates, and conflating them moved 299 of his words.

FOUND 2026-10-28 by the full-suite baseline, through
`test_the_corpus_count_is_unchanged_by_the_fix`, which pins the annotations dated
on or before 2026-10-13 and read 517 against a pin of 522.

NOTHING WAS LOST. The manifest confirms 0 files lost an annotation.
`The_Directive_Set_2026-10-13.txt` has mtime 2026-10-14 18:07, so its 11
annotations left an mtime-bounded window while other in-window files gained 6.

THE 2 FACTS, AND THEY ARE NOT THE SAME FACT. The date in a response file's NAME
is the date of the report THIS PROJECT wrote. The MTIME is approximately when HE
wrote the annotation on it, necessarily later. "Which report is this against?"
and "when did he write it?" are different questions with different answers.

WHY mtime ALONE CANNOT BOUND A POPULATION. It is mutable: anything touching a
file moves it, and task B42 established that Word rewrites his .txt files on
save -- 35 of 106 carry the CR-only signature. Measured 2026-10-28: of 90
annotated files carrying a date in the name, 37 had an mtime that disagreed with
it, 0.411111 Wilson [0.315132, 0.514368], always LATER, by up to 5 days, with 299
annotations read under the wrong date.

MY FIRST FIX WAS WRONG AND THIS FILE EXISTS BECAUSE OF IT. Replacing mtime with
the name everywhere silently changed the meaning of every `--since` window in the
project and immediately orphaned 12 verdict rows:
`Intelligence_First_Take_Home_2026-09-30.txt` moved from October into September
and left the verdict record's window while its 12 rows stayed behind. Widening
the window to compensate would have surfaced 35 annotations with no verdict row
-- real work created by a change of meaning nobody asked for. So BOTH are
recorded, `date` is unchanged, and `by=` selects which one a window filters on.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"


@pytest.fixture(scope="module")
def R():
    spec = importlib.util.spec_from_file_location("reader_two_dates", READER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["reader_two_dates"] = m
    spec.loader.exec_module(m)
    return m


def test_every_annotation_carries_both_dates(R):
    anns = R.annotations()
    assert anns, "no annotations read at all"
    missing = [a for a in anns if not a.get("report_date") or not a.get("date")]
    assert not missing, (
        f"{len(missing)} annotation(s) lack one of the 2 dates; a field nothing "
        f"populates is an addition nothing reaches")


def test_the_default_window_is_still_mtime(R):
    """THE COMPATIBILITY PROPERTY. Every existing caller passes no `by`, and its
    meaning must not have changed. 517 under mtime against 528 under report."""
    W = dt.date(2026, 10, 13)
    default = len(R.annotations(until=W))
    mtime = len(R.annotations(until=W, by="mtime"))
    assert default == mtime, (
        "the default window no longer filters on mtime, so every --since window "
        "in the project has silently changed meaning")


def test_the_report_window_differs_from_the_mtime_one(R):
    """ANTI-VACUITY. If the 2 agreed, `by=` would be decoration."""
    W = dt.date(2026, 10, 13)
    assert len(R.annotations(until=W, by="report")) != \
        len(R.annotations(until=W, by="mtime")), (
        "the 2 windows agree on this corpus, so this guard proves nothing; pick "
        "a boundary where they differ or the drift has been repaired at source")


def test_the_report_window_survives_an_mtime_change(R, tmp_path):
    """THE PROPERTY THE CORPUS PIN RESTS ON, executed rather than asserted.

    Pushing an in-window file's mtime 30 days forward must not move the
    report-dated population. Under the old code it moved 11 annotations out.
    Only the timestamp is touched; not one byte of his words.
    """
    import os
    W = dt.date(2026, 10, 13)
    target = R.RESPONSES / "Morning_Report_2026-10-13.txt"
    if not target.is_file():
        pytest.skip("that response file is not on this machine")
    before = len(R.annotations(until=W, by="report"))
    st = target.stat()
    try:
        future = st.st_mtime + 86400 * 30
        os.utime(target, (st.st_atime, future))
        after = len(R.annotations(until=W, by="report"))
    finally:
        os.utime(target, (st.st_atime, st.st_mtime))
    assert before == after, (
        f"the report-dated window moved from {before} to {after} when a file's "
        f"mtime changed, so it is not closed and the pin will drift again")


def test_the_mtime_window_is_the_one_that_moves(R):
    """The converse, so the claim above is a measurement and not a hope."""
    import os
    W = dt.date(2026, 10, 13)
    target = R.RESPONSES / "Morning_Report_2026-10-13.txt"
    if not target.is_file():
        pytest.skip("that response file is not on this machine")
    before = len(R.annotations(until=W, by="mtime"))
    st = target.stat()
    try:
        future = st.st_mtime + 86400 * 30
        os.utime(target, (st.st_atime, future))
        after = len(R.annotations(until=W, by="mtime"))
    finally:
        os.utime(target, (st.st_atime, st.st_mtime))
    assert before != after, (
        "an mtime-bounded window did NOT move when an in-window file's mtime "
        "moved, so the whole premise of this repair is wrong")


def test_the_drift_is_real_and_measured(R):
    """The figure quoted in the docstring, recomputed rather than trusted."""
    import re
    NAME = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")
    named = drift = 0
    for p in sorted(R.RESPONSES.glob("*")):
        if not R.is_one_of_his_annotated_responses(p):
            continue
        m = NAME.search(p.name)
        if not m:
            continue
        try:
            nd = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        named += 1
        if nd != dt.date.fromtimestamp(p.stat().st_mtime):
            drift += 1
    assert named >= 80, f"only {named} dated file(s); the figure is not comparable"
    assert drift > 0, (
        "no file's mtime disagrees with its name any more. If the archive was "
        "repaired at source that is good news -- re-measure and update the "
        "docstring rather than deleting this guard")


def test_a_file_with_no_date_in_its_name_falls_back_to_mtime(R, tmp_path):
    """THE FALLBACK PATH, which a mutation test showed nothing reached.

    8 of his 98 annotated files carry no date in the name -- "Astra review.txt",
    "Closing_Report_20260909.txt" and the like. For those, `report_date` has
    nothing to read and must fall back to mtime rather than inventing a date.
    Breaking the fallback left every other test in this file green, which is the
    definition of an unreached branch.
    """
    import os
    f = tmp_path / "No_Date_In_This_Name.txt"
    f.write_text("a line\n# his annotation here\n", encoding="utf-8")
    known = 1762000000.0                       # a fixed instant, not "now"
    os.utime(f, (known, known))
    expected = dt.date.fromtimestamp(known)
    assert R._report_date(f) == expected, (
        f"a name carrying no date gave report_date {R._report_date(f)} instead "
        f"of the mtime {expected}; the fallback is broken or invents a date")
    assert R._written_date(f) == expected


def test_a_name_date_beats_the_mtime_when_present(R, tmp_path):
    """The positive control for the same function, so the test above cannot pass
    by the fallback being the only path ever taken."""
    import os
    f = tmp_path / "Report_2026-03-14.txt"
    f.write_text("a line\n# his annotation here\n", encoding="utf-8")
    known = 1762000000.0
    os.utime(f, (known, known))
    assert R._report_date(f) == dt.date(2026, 3, 14), (
        f"the name's date was ignored; got {R._report_date(f)}")
    assert R._written_date(f) == dt.date.fromtimestamp(known), (
        "the written date must stay the mtime even when the name carries a date")
