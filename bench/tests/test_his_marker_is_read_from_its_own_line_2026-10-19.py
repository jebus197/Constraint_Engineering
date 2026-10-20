"""His command markers live on their OWN LINE, and the harvester could not see them.

THE DEFECT, measured 2026-10-19. He marks an annotation by writing `fr`, `pf` or
`qs` on a line of its own BELOW the annotation, never inside it:

    # Why the note standard version bump from 1.7 to 1.8? ... justified?
    <blank>
    qs

An annotation is `#`-prefixed, a marker line is not, so the marker was never part
of any annotation's text. `harvest_tickets_2026-10-17.py` scanned that text for a
marker, found none, and reported "explicitly marked: 0" while his files carried
30. The `qs` kind he asked for on 2026-10-19 would have been INERT against his
real annotations on the day it was built.

MEASURED ACROSS EVERY REPLY FILE: 30 markers, 30 of them own-line following an
annotation, 0 inline. So there is exactly one form to support and the rule is
unambiguous: skip blank lines, and the FIRST non-blank line after an annotation
either is the marker or there is none. Stopping at the first non-blank is what
stops a marker belonging to a LATER annotation being claimed by an earlier one.

A SECOND, SMALLER FAULT IN THE SAME AREA: his files are carriage-return-only in
28 of 37 cases, 75.6757%, Wilson [59.8827%, 86.6386%]. Python's `re.M` makes `$`
match before `\n` and at end-of-string, but NEVER before `\r`, so a marker regex
anchored on `$` cannot fire in those files even when the marker IS in the text.
The reader uses `splitlines()`, which handles CR, LF and CRLF alike, so routing
the association through the reader avoids that trap rather than patching around
it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
READER = ROOT / "scripts" / "read_founder_responses_2026-10-11.py"
HARVEST = ROOT / "scripts" / "harvest_tickets_2026-10-17.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def reader():
    return _load(READER, "_rd")


class TestTheMarkerPatternItself:
    def test_it_matches_a_bare_marker_line(self, reader):
        for line in ("qs", "fr", "pf", " qs ", "qs, fr", "pf,qs"):
            assert reader._MARKER_LINE.match(line), line

    def test_it_does_not_match_prose_that_merely_contains_one(self, reader):
        for line in ("frequently", "the qsort routine", "# qs is a question",
                     "pf: and then some prose", "a qs b"):
            assert not reader._MARKER_LINE.match(line), line


class TestTheReaderAssociatesIt:
    def test_every_annotation_row_carries_the_field(self, reader):
        rows = reader.annotations()
        assert rows, "no annotations read at all"
        assert all("marker" in r for r in rows), (
            "the field must exist on every row, empty when he wrote no marker")

    def test_his_real_files_yield_markers(self, reader):
        rows = reader.annotations()
        marked = [r for r in rows if r.get("marker")]
        assert len(marked) >= 25, (
            f"only {len(marked)} markers recovered; the measurement of "
            f"2026-10-19 found 30 across his reply files")

    def test_qs_is_the_kind_he_uses_most(self, reader):
        kinds = [k for r in reader.annotations() if r.get("marker")
                 for k in r["marker"].split(",")]
        assert kinds.count("qs") >= 20, kinds.count("qs")

    def test_a_marker_is_never_stolen_from_a_later_annotation(self, reader, tmp_path):
        #: EXECUTED on a constructed file: annotation A has no marker, annotation
        #: B does. A must not claim B's.
        d = tmp_path / "Responses"
        d.mkdir()
        f = d / "Morning_Report_2026-01-01.txt"
        f.write_text("report line\r\r# first question with no marker\r\r"
                     "# second question\r\rqs\r\r", encoding="utf-8")
        old = reader.RESPONSES
        try:
            reader.RESPONSES = d
            rows = reader.annotations()
            got = {r["text"]: r["marker"] for r in rows}
            assert got["first question with no marker"] == "", got
            assert got["second question"] == "qs", got
        finally:
            reader.RESPONSES = old

    def test_it_reads_carriage_return_files(self, reader, tmp_path):
        d = tmp_path / "Responses"
        d.mkdir()
        (d / "Morning_Report_2026-01-02.txt").write_text(
            "report\r\r# a question?\r\rqs\r\r", encoding="utf-8")
        old = reader.RESPONSES
        try:
            reader.RESPONSES = d
            rows = reader.annotations()
            assert rows and rows[0]["marker"] == "qs", rows
        finally:
            reader.RESPONSES = old


class TestTheHarvesterConsumesIt:
    def test_the_harvester_reports_his_markers(self):
        h = _load(HARVEST, "_hv")
        rows = h.from_responses(since="2026-01-01") if hasattr(h, "from_responses") else None
        if rows is None:
            pytest.skip("the harvester exposes no direct response-source entry point")
        marked = [r for r in rows if r.get("marked")]
        assert len(marked) >= 25, f"only {len(marked)} marked candidates"

    def test_a_question_is_harvested_as_a_question(self):
        h = _load(HARVEST, "_hv2")
        if not hasattr(h, "from_responses"):
            pytest.skip("no direct entry point")
        kinds = {r["kind"] for r in h.from_responses(since="2026-01-01")
                 if r.get("marked")}
        assert "qs" in kinds, kinds
