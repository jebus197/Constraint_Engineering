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
    """STRUCTURAL: rendering section 3 requires writing his report files."""

    def _section3(self) -> str:
        src = BUILDER.read_text(encoding="utf-8")
        i = src.index('"## 3. Work outstanding, needing no decision"')
        j = src.index('"## 4.', i)
        return src[i:j]

    def test_the_renderer_reads_the_status(self):
        body = self._section3()
        assert 'o.get("status")' in body or "o.get('status')" in body, (
            "section 3 does not read the status field, so the record can say a "
            "defect is fixed while the report says its work is outstanding")

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
