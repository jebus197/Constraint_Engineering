"""A marker must be compared LIKE WITH LIKE: own-line against own-line.

WHY THIS FILE EXISTS. `can_i_parse_his_responses_in_full_2026-10-19.py` is the
measurement that says whether the founder's replies are read in full, and
`Responses/` is a FIRST READ resource precisely because 221 of 691 annotations
were once invisible to a naive scan. On 2026-10-31 that measurement reported the
reader as attaching 97 markers where only 59 were "present", and the gap was
entirely in the instrument:

  1. The raw side counted own-line marker LINES. The reader's side counted
     own-line AND trailing markers -- a second form added 2026-10-30 when his
     style changed. An equality between those two is apples to oranges, and it
     went red the moment 4 files carried 38 trailing markers and no own-line
     ones.
  2. The measurement kept its OWN copy of the marker vocabulary, `(fr|pf|qs|wr)`,
     which never learned `disc` -- the kind he ruled on 2026-10-30 -- nor its
     legacy spellings. 2 declarations of 1 fact, drifted.

THE REPAIR IS NOT AN INEQUALITY. Relaxing the check to "attached >= present"
would have silenced it and lost the invention half: a marker read under the
wrong form, or attached to no text at all, is as much a defect as one dropped.
The comparison is split BY FORM and compared AS SETS, because a count cannot say
WHICH marker moved and two errors in opposite directions cancel in a total.

WHAT IS GUARDED WHERE. The vocabulary is now BORROWED from the reader, so a
vocabulary error is invisible to the measurement by construction. That is
deliberate and it is safe only because the vocabulary has its own guard:
removing `disc` from `_MARKER_LINE` turns
`test_the_ds_kind_is_confined_to_his_annotations_2026-10-30.py` red, verified by
execution on 2026-10-31 (1 failed, 62 passed). This file guards the ASSOCIATION
RULE -- which form a marker was written in -- which is the part that stays
independent.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
READER = ROOT / "scripts" / "read_founder_responses_2026-10-11.py"
MEASURE = ROOT / "scripts" / "can_i_parse_his_responses_in_full_2026-10-19.py"

VALID_FORMS = {"", "own_line", "trailing"}


def _load(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rd():
    return _load(READER)


@pytest.fixture(scope="module")
def rows(rd):
    return rd.annotations()


class TestTheFieldExistsAndIsHonest:
    def test_every_row_carries_a_marker_form(self, rows):
        missing = [r for r in rows if "marker_form" not in r]
        assert not missing, f"{len(missing)} row(s) have no marker_form field"

    def test_the_form_vocabulary_is_closed(self, rows):
        bad = sorted({r["marker_form"] for r in rows} - VALID_FORMS)
        assert not bad, f"unexpected marker_form value(s): {bad}"

    def test_a_form_is_present_exactly_when_a_marker_is(self, rows):
        # Neither direction may slip: a form without a marker would make the
        # measurement count a marker that is not there, and a marker without a
        # form would make it count none.
        form_no_marker = [r for r in rows if r["marker_form"] and not r["marker"]]
        marker_no_form = [r for r in rows if r["marker"] and not r["marker_form"]]
        assert not form_no_marker, f"{len(form_no_marker)} form(s) with no marker"
        assert not marker_no_form, f"{len(marker_no_form)} marker(s) with no form"


class TestBothFormsAreActuallyPresent:
    """A control. If either form were absent from the corpus the split would be
    vacuous, and a vacuous check reads as a passing one."""

    def test_the_own_line_form_is_exercised(self, rows):
        n = sum(1 for r in rows if r["marker_form"] == "own_line")
        assert n > 0, "no own-line marker in the corpus: the split is vacuous"

    def test_the_trailing_form_is_exercised(self, rows):
        n = sum(1 for r in rows if r["marker_form"] == "trailing")
        assert n > 0, "no trailing marker in the corpus: the split is vacuous"


class TestTheFormIsReadFromTheCharacters:
    """Executed against the real reader over a synthetic directory, so the
    classification is checked rather than described."""

    def _run(self, rd, tmp_path, body, monkeypatch):
        f = tmp_path / "Synthetic_Report_2026-10-31.txt"
        f.write_text(body, encoding="utf-8")
        monkeypatch.setattr(rd, "RESPONSES", tmp_path)
        return rd.annotations()

    def test_an_own_line_marker_is_classified_own_line(self, rd, tmp_path, monkeypatch):
        rows = self._run(rd, tmp_path, "# Build it this way.\nfr\n", monkeypatch)
        assert len(rows) == 1 and rows[0]["marker"] == "fr"
        assert rows[0]["marker_form"] == "own_line"

    def test_a_trailing_marker_is_classified_trailing(self, rd, tmp_path, monkeypatch):
        rows = self._run(rd, tmp_path, "# I accept your recommendation. fr\n", monkeypatch)
        assert len(rows) == 1 and rows[0]["marker"] == "fr"
        assert rows[0]["marker_form"] == "trailing"

    def test_an_unmarked_annotation_has_no_form(self, rd, tmp_path, monkeypatch):
        rows = self._run(rd, tmp_path, "# Just a comment with no marker.\n", monkeypatch)
        assert len(rows) == 1 and rows[0]["marker"] == ""
        assert rows[0]["marker_form"] == ""

    def test_the_own_line_form_wins_when_both_are_present(self, rd, tmp_path, monkeypatch):
        # The reader prefers the own-line form, and the measurement's trailing
        # comparison excludes own-line rows on exactly that ground. If the
        # precedence ever flipped, the trailing set would gain a row the raw
        # side also finds and the check would stay green while the field lied.
        rows = self._run(rd, tmp_path, "# Do it, and discuss. qs\npf\n", monkeypatch)
        assert len(rows) == 1
        assert rows[0]["marker_form"] == "own_line", rows[0]
        assert rows[0]["marker"] == "pf"

    def test_a_legacy_spelling_is_normalised_in_both_forms(self, rd, tmp_path, monkeypatch):
        # Both readers must normalise. Until 2026-10-31 only the trailing path
        # did, so an own-line `ds` came back raw -- and the own-line form is the
        # one 59 of his markers use.
        a, b = tmp_path / "a", tmp_path / "b"
        a.mkdir(); b.mkdir()
        own = self._run(rd, a, "# Talk this through.\nds\n", monkeypatch)
        assert own[0]["marker"] == "disc"
        assert own[0]["marker_form"] == "own_line"
        trail = self._run(rd, b, "# Talk this through. ds\n", monkeypatch)
        assert trail[0]["marker"] == "disc"
        assert trail[0]["marker_form"] == "trailing"


class TestTheMeasurementUsesOneVocabulary:
    def test_the_patterns_are_the_readers_own_objects(self, rd):
        mod = _load(MEASURE)
        line, trailing = mod._marker_patterns(rd)
        # IDENTITY, not equality. A copied pattern can drift; a borrowed one
        # cannot, and drift is the defect this file was written for.
        assert line is rd._MARKER_LINE
        assert trailing is rd._MARKER_TRAILING

    def test_the_measurement_exits_zero_today(self):
        r = subprocess.run([sys.executable, str(MEASURE)],
                           capture_output=True, text=True, cwd=str(ROOT))
        assert r.returncode == 0, r.stdout[-2000:]
        assert "COMPLETE on all 4 properties" in r.stdout
