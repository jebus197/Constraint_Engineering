#!/usr/bin/env python3
"""A ruling he makes AFTER a dated spoken file is not a divergence.

THE DEFECT, 2026-11-06. `do_the_two_decision_surfaces_agree_2026-11-01.py`
compares a DATED spoken file against LIVE derived state and had no date
awareness at all: no mtime, no filename date, no reading of `ruled`. So the
moment he ruled B122, the heading he had been handed on 2026-11-04 became
"SPOKEN BUT NOT DERIVED" and the comparator returned 3. It was failing with
the passage of his RULINGS rather than with any defect -- the same shape a
sibling guard carried until 2026-10-19, when a frozen `_FALLBACK_SINCE` made
it fail with the passage of time.

WHY AN EXEMPTION IS SAFE ONLY IF IT IS BOUNDED. The comparator exists to
catch a heading the record does not track -- he is asked for something
nothing holds. An unconditional exemption would delete that power entirely.
So the bound is the FILE'S OWN DATE: forgiven only where the file could not
have known, meaning the decision's `ruled` date is strictly later. These
tests hold both halves, and the mutation harness
`scripts/the_date_exemption_mutations_2026-11-06.py` turns each of them red.
"""
from __future__ import annotations
import datetime as dt
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"


@pytest.fixture(scope="module")
def sf():
    spec = importlib.util.spec_from_file_location("sf_guard", SRC)
    m = importlib.util.module_from_spec(spec)
    sys.modules["sf_guard"] = m
    spec.loader.exec_module(m)
    return m


FILE_DATE = dt.date(2026, 11, 4)
DETAIL = {
    "task:AFTER":   {"spoken_heading": "RULED AFTER THE FILE", "ruled": "2026-11-06"},
    "task:BEFORE":  {"spoken_heading": "RULED BEFORE THE FILE", "ruled": "2026-11-01"},
    "task:SAMEDAY": {"spoken_heading": "RULED ON THE FILE'S OWN DATE", "ruled": "2026-11-04"},
    "task:UNRULED": {"spoken_heading": "NEVER RULED AT ALL"},
    "task:JUNK":    {"spoken_heading": "A MALFORMED RULING DATE", "ruled": "soon"},
    "_not_a_dict":  ["a list value, which the real file also contains"],
}


class TestTheExemptionExists:
    def test_both_helpers_are_present(self, sf):
        assert hasattr(sf, "ruled_after") and hasattr(sf, "spoken_file_date")

    def test_the_file_date_comes_from_the_name_he_was_handed(self, sf):
        got = sf.spoken_file_date(pathlib.Path("Decisions_Awaiting_You_2026-11-04.txt"))
        assert got == FILE_DATE
        assert sf.spoken_file_date(pathlib.Path("no_date_here.txt")) is None


class TestItForgivesOnlyWhatTheFileCouldNotKnow:
    def test_a_ruling_after_the_file_is_exempt(self, sf):
        ok, ident, ruled = sf.ruled_after("RULED AFTER THE FILE", FILE_DATE, DETAIL)
        assert ok and ident == "task:AFTER" and ruled == "2026-11-06"

    def test_a_ruling_before_the_file_is_still_caught(self, sf):
        """The file was written AFTER the ruling, so it should not have asked."""
        ok, ident, _r = sf.ruled_after("RULED BEFORE THE FILE", FILE_DATE, DETAIL)
        assert not ok and ident == "task:BEFORE"

    def test_a_ruling_on_the_files_own_date_is_still_caught(self, sf):
        """Same-day is NOT 'could not have known'. This pins > against >=."""
        ok, _i, _r = sf.ruled_after("RULED ON THE FILE'S OWN DATE", FILE_DATE, DETAIL)
        assert not ok

    def test_an_unruled_decision_is_still_caught(self, sf):
        ok, ident, ruled = sf.ruled_after("NEVER RULED AT ALL", FILE_DATE, DETAIL)
        assert not ok and ident == "task:UNRULED" and ruled is None

    def test_a_malformed_date_is_still_caught_rather_than_crashing(self, sf):
        ok, ident, ruled = sf.ruled_after("A MALFORMED RULING DATE", FILE_DATE, DETAIL)
        assert not ok and ident == "task:JUNK" and ruled == "soon"

    def test_a_heading_the_record_never_tracked_is_still_caught(self, sf):
        """THE DEFECT THE COMPARATOR EXISTS FOR. It must survive the exemption."""
        ok, ident, _r = sf.ruled_after("A HEADING NOTHING HOLDS", FILE_DATE, DETAIL)
        assert not ok and ident is None

    def test_a_list_valued_entry_does_not_crash_the_scan(self, sf):
        """The real detail file carries a list under `_what_this_is`."""
        ok, _i, _r = sf.ruled_after("ANYTHING", FILE_DATE, DETAIL)
        assert not ok


class TestTheLiveComparatorAgrees:
    def test_it_exits_zero_on_the_live_tree(self):
        r = subprocess.run([sys.executable, str(SRC)], cwd=REPO,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stdout[-2500:]
        assert "AGREE on all" in r.stdout

    def test_the_exemption_is_reported_rather_than_silent(self, sf):
        """A silent exemption is indistinguishable from a check that passed.

        ★ THE EXPECTATION IS DERIVED, NOT HARDCODED. A first version of this
        test wrapped the assertion in `if "exempted" in stdout`, which made it
        pass whether or not the exemption was ever printed -- silencing the
        print would have gone GREEN. It now computes, from the live record,
        which headings OUGHT to be exempt, and requires each one to be named
        in the output. When the live tree has none, it requires none.
        """
        import json
        detail = json.loads(sf.DETAIL.read_text(encoding="utf-8"))
        path, s = sf.spoken()
        cutoff = sf.spoken_file_date(path) if path else None
        dset = {h.upper() for _i, h in sf.derived() if h}
        expected = []
        if cutoff is not None:
            for head in {h for _n, h in s} - dset:
                ok, ident, ruled = sf.ruled_after(head, cutoff, detail)
                if ok:
                    expected.append((ident, ruled))

        r = subprocess.run([sys.executable, str(SRC)], cwd=REPO,
                           capture_output=True, text=True, timeout=600)
        for ident, ruled in expected:
            assert ident in r.stdout, (
                f"{ident} was exempted silently; a reader cannot tell this "
                f"comparator forgave something from one that found nothing")
            assert str(ruled) in r.stdout, f"{ident} exempted with no date named"
        if not expected:
            assert "exempted, ruled AFTER" not in r.stdout, (
                "an exemption was reported that the record does not justify")
