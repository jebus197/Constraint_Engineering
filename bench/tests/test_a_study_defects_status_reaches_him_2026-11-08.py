"""A study defect's recorded status must reach the report he reads.

THE CONTRADICTION THIS GUARDS. `experimental_notes/STUDY_IN_FLIGHT.json` and
the generated morning report are produced from the same file, and on 2026-11-08
they disagreed: the record said a defect's mismatch was "FIXED, VERIFIED BY
EXECUTION" while the report said "the work is outstanding". The cause was not a
wrong value anywhere -- it was that section 3 never rendered the `status` field,
which `study_items()` had been carrying all along, cut to 60 characters.

So advancing a record changed nothing he read. That is the mirror of a failure
already recorded here, where an entry was updated and the file was never
touched; this direction leaves him reading that work is outstanding when a
measurement says it is done.

TESTED BY CALLING, not by reading, except for the 1 claim that cannot be
executed without writing his report files. There the SOURCE OF SECTION 3 IS
SLICED between its own heading and the next, and the assertions run inside that
slice -- a bounded window rather than an AST walk, and bounded for the reason
tonight's mutation harness found: an unbounded window reaches into a
neighbouring block and is satisfied by the wrong code. The limit is stated
rather than implied: if the renderer moves OUT of section 3 these tests would
stop seeing it, so `test_the_renderer_reads_the_status` fails loudly rather than
passing vacuously.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
BUILDER = REPO / "scripts" / "morning_report_build_2026-10-12.py"


@pytest.fixture(scope="module")
def M():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("mrb_status", BUILDER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["mrb_status"] = m
    spec.loader.exec_module(m)
    return m


class TestTheStatusIsCarriedWhole:

    def test_study_items_carry_a_status_field(self, M):
        items = M.study_items()
        assert items, "study_items() returned nothing; the premise is gone"
        assert all("status" in i for i in items)

    def test_at_least_one_status_is_longer_than_the_old_60_char_cut(self, M):
        """ANTI-VACUITY. If every status were short, the widening would be
        untestable and this file would pass while deciding nothing."""
        lens = [len(str(i.get("status") or "")) for i in M.study_items()]
        assert any(n > 60 for n in lens), (
            f"no study defect carries a status longer than 60 characters "
            f"(longest {max(lens) if lens else 0}), so the cut this guards "
            f"against cannot be observed. Check whether the records were "
            f"shortened before weakening this test.")

    def test_the_status_is_not_truncated_by_the_extractor(self, M):
        """The RENDERER decides what to show; the extractor must not pre-cut."""
        import json
        raw = json.loads((REPO / "experimental_notes" / "STUDY_IN_FLIGHT.json")
                         .read_text(encoding="utf-8"))
        by_id = {str(d.get("id") or d.get("name", "")): str(d.get("status") or "")
                 for d in raw.get("open_defects", [])}
        for i in M.study_items():
            full = by_id.get(i["ident"])
            if full is None:
                continue
            assert i["status"] == full, (
                f"{i['ident']}: the extractor cut the status to "
                f"{len(i['status'])} of {len(full)} characters, so the renderer "
                f"cannot decide what to show or say what it withheld")


class TestTheRendererShowsItAndSaysWhatItCut:
    """STRUCTURAL: rendering section 3 requires writing his report files.

    ★ BOTH RENDERERS ARE CHECKED, 2026-11-08. The first version of this class
    examined only the WRITTEN section 3, and the fix was applied only there --
    measured immediately after, the written copy carried 7 status lines and the
    SPOKEN copy carried 0. He reads these by text-to-speech, so the spoken file
    is the surface that reaches him, and a guard that watches 1 of 2 renderers
    would have passed while the half he reads stayed wrong. That is the same
    divergence between these 2 copies that an existing entry already records.
    """

    def _section3(self) -> str:
        src = BUILDER.read_text(encoding="utf-8")
        i = src.index('"## 3. Work outstanding, needing no decision"')
        j = src.index('"## 4.', i)
        return src[i:j]

    def _spoken_section3(self) -> str:
        src = BUILDER.read_text(encoding="utf-8")
        i = src.index('"SECTION 3. OUTSTANDING WORK THAT NEEDS NO DECISION"')
        j = src.index('"SECTION 4.', i)
        return src[i:j]

    def test_the_renderer_reads_the_status(self):
        """★ ASSERTS ON THIS RENDER, NOT ON ANY MENTION OF THE FIELD.

        The first version accepted `o.get("status")` OR `o.get('status')`
        anywhere in the slice, and the slice already held the single-quoted
        form at a pre-existing line that renders the status for items marked
        already-built. So a mutation removing THIS read left the test green --
        caught by the reversal harness, which is the only reason it is not
        still vacuous. An assertion must name the thing it is about.
        """
        body = self._section3()
        assert "RECORDED STATUS" in body, (
            "the written section 3 no longer emits a RECORDED STATUS line, so "
            "the record can say a defect is fixed while the report says its "
            "work is outstanding")
        assert '_st = str(o.get("status")' in body, (
            "the RECORDED STATUS label is emitted without reading the status "
            "field, so it would render something else or nothing")

    def test_the_cut_is_announced_rather_than_silent(self):
        body = self._section3()
        assert "more characters in" in body, (
            "the renderer trims the status without saying how much it withheld; "
            "a listing cut under a heading that reads as complete is the defect "
            "class this file's own history repaired 5 times")

    def test_it_is_scoped_to_study_defects(self):
        body = self._section3()
        assert "programme of study" in body, (
            "the status line is not scoped to study defects, so a task-list "
            "item would gain a RECORDED STATUS line it has no field for")

    def test_the_SPOKEN_renderer_reads_the_status_too(self):
        body = self._spoken_section3()
        assert "Recorded status" in body and '_sst = str(o.get("status")' in body, (
            "the SPOKEN section 3 does not read the status field. He reads "
            "these by text-to-speech, so this is the copy that reaches him; "
            "measured 2026-11-08, the written copy carried 7 status lines and "
            "this one carried 0 while the fix was called applied.")

    def test_the_spoken_cut_is_announced_as_a_sentence(self):
        body = self._spoken_section3()
        assert "characters are recorded" in body, (
            "the spoken renderer trims the status without saying how much it "
            "withheld, or says it in a form this file forbids. Parentheses and "
            "ellipses read as noise aloud, so the amount must be a sentence.")

    def test_the_spoken_status_goes_through_the_normaliser(self):
        """★ ASSERTS ON THE LINE, NOT A WINDOW AROUND IT.

        The first version took 200 characters either side, which holds 2
        `_spoken(` calls -- the status one and the `what` one that follows --
        so replacing the status call with `str(` left the test green. This is
        the SAME too-wide-window error the reversal harness caught in a sibling
        guard earlier the same session, repeated here within the hour.
        """
        body = self._spoken_section3()
        line = next(ln for ln in body.splitlines() if "Recorded status" in ln)
        assert "_spoken(" in line, (
            f"the spoken status is emitted without the spoken normaliser, so "
            f"backticks and markdown in a recorded status would be read aloud "
            f"as noise. The line is:\n  {line.strip()}")

    def test_both_renderers_use_the_same_character_cap(self):
        """A difference in the cap would make the 2 copies disagree again."""
        import re
        caps = []
        for body in (self._section3(), self._spoken_section3()):
            m = re.search(r"\[:(\d+)\]", body)
            caps.append(m.group(1) if m else None)
        assert caps[0] is not None and caps[0] == caps[1], (
            f"the written and spoken renderers cut the status at different "
            f"lengths {caps}, so the 2 copies would report different amounts "
            f"withheld for the same defect")
