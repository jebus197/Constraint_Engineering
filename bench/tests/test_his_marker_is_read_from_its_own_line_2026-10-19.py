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

MEASURED ACROSS EVERY REPLY FILE on 2026-10-19: 30 markers, 30 of them own-line
following an annotation, 0 inline. The rule for that form is unambiguous: skip
blank lines, and the FIRST non-blank line after an annotation either is the
marker or there is none.

★ "THERE IS EXACTLY ONE FORM TO SUPPORT" WAS TRUE WHEN WRITTEN AND IS NOT
TRUE NOW. Corrected 2026-10-30. His style changed: re-measured over all 752
annotations, 59 carry an own-line marker, 693 carry none, and 13 of those 693
END in a marker token -- 0.018759, Wilson [0.010995, 0.031829], exact
[0.010025, 0.031865] -- every one dated 2026-10-29. The 13 include the 2
rulings that closed entries B47 and C1, whose markers were therefore invisible
to this reader and survived only because the harvester re-derives a kind from
the text. The reader now falls back to a TRAILING marker, the own-line form
still being tried first and still winning. The trailing requirement is not a
preference: matching a marker anywhere in a quotation was measured at 4 of 19
hits with 3 of them the bare English article, against exactly 1 true positive
when the marker must trail. Stopping at the first non-blank is what
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



def test_a_trailing_marker_is_read_too(reader):
    """★ ADDED 2026-10-30, with the own-line form still winning.

    His 2 rulings of 2026-10-29 end their own sentence with the marker rather
    than putting it on the next line, and both are rulings this project acted
    on. A reader that cannot see them records his instruction as unmarked.
    """
    assert reader._marker_of("Build and implement option 1. fr") == "fr"
    assert reader._marker_of("answer this one please qs") == "qs"
    assert reader._marker_of("do both. fr, pf") == "fr,pf"


def test_the_fallback_is_WIRED_into_the_real_extraction(reader):
    """★ THE WIRING, NOT THE FUNCTION. Added 2026-10-30 after a mutation ran.

    The 3 tests beside this one called `_marker_of` directly, so deleting the
    `if not _marker: _marker = _marker_of(body)` line in `annotations()` left
    every one of them GREEN. A helper with a caller, tested without its caller,
    is the addition-nothing-reaches defect this project has confirmed 11 times,
    and it appeared in a guard written to close a reading defect.

    So this asserts on the OUTPUT OF THE READER over his real files: the 2
    rulings that closed entries B47 and C1 end their own sentence with `fr`,
    and the reader must report that. Removing the wiring turns this red.
    """
    rows = reader.annotations()
    trailing = [r for r in rows
                if (r.get("text") or "").strip().endswith("option 1. fr")
                or (r.get("text") or "").strip() == "I accept your recommendation. fr"]
    assert trailing, (
        "neither ruling was found in his files at all, so this test can no "
        "longer speak to the wiring; re-derive it from the current corpus")
    for r in trailing:
        assert r["marker"] == "fr", (
            f"the reader reported marker={r['marker']!r} for a ruling that ends "
            f"in a trailing fr, so the trailing fallback is not reached: "
            f"{r['text'][-70:]!r}")


def test_ordinary_prose_endings_are_not_markers(reader):
    """THE CONTROL. Without it, returning a marker for everything would pass.

    `a` is the recorded trap: as a bare MC command it matches the commonest word
    in English, which is why the ticket-kind set here excludes it entirely.
    """
    for text in ["Just do it.", "This is fine for now",
                 "What about the other half?", "a",
                 "Approved, but check the ladder first.",
                 #: MID-PROSE, which is the property that makes "trailing" mean
                 #: something. Without these the pattern could match anywhere
                 #: and every control above would still pass.
                 "the pf ticket was closed yesterday",
                 "raise it as a qs and move on to the next entry",
                 "fr is the marker for a feature request"]:
        assert reader._marker_of(text) == "", text


def test_the_own_line_form_wins_over_a_trailing_one(reader, tmp_path):
    """★ PRECEDENCE, ON A CONSTRUCTED FILE. Rewritten 2026-10-30.

    The first version of this test asserted `_marker_of("something ending fr")
    == "fr"`, which says nothing about precedence: it exercises the fallback
    alone and passes whichever branch the extraction prefers. A mutation that
    made the trailing form OVERRIDE the own-line form left it green.

    The 2 forms cannot be told apart from the reader's output either, because
    the field records a marker's VALUE and not which branch set it, and on his
    real files the 2 forms agree wherever both appear. So the only way to test
    the ordering is a file where they DISAGREE, which is constructed here.
    """
    d = tmp_path / "Responses"
    d.mkdir()
    (d / "Morning_Report_2026-01-03.txt").write_text(
        "report line\r\r# his ruling ends in a trailing marker fr\r\rpf\r\r"
        "# a second ruling with only a trailing marker qs\r\r",
        encoding="utf-8")
    old_dir = reader.RESPONSES
    try:
        reader.RESPONSES = d
        got = {r["text"]: r["marker"] for r in reader.annotations()}
    finally:
        reader.RESPONSES = old_dir
    assert got["his ruling ends in a trailing marker fr"] == "pf", (
        f"the trailing `fr` overrode the own-line `pf`: {got}. The own-line form "
        f"is the one 59 of his markers use and it is unambiguous, so it must win")
    assert got["a second ruling with only a trailing marker qs"] == "qs", (
        f"an annotation with ONLY a trailing marker lost it: {got}")


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
