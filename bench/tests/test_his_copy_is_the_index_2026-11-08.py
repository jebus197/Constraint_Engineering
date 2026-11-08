"""The copy he reads is the index; the repository keeps every section.

HIS COMPLAINT, 2026-11-08. He ruled on all 29 decisions from the index and said
of the rest that at over 22,000 words it is an almost impossible workload, and
asked whether the long explanations had been appended to the file or his request
to keep the workload bounded had been ignored.

THE FIRST READING IS REFUTED AND THE SECOND IS RIGHT, measured by
`scripts/what_his_twenty_nine_rulings_actually_say_2026-11-08.py`: these files
ran 18,300 bytes on 2026-10-29 and 25,523 on 2026-10-30, then 151,786 on
2026-11-04 -- LARGER than the one he was sent -- so nothing was appended that
day. The delivered file was 22,902 words with the long tier at 0.927451 of the
characters, and 0.690653 of the morning report's 12-word sequences also appear
in it, because 2 generators each render all 29 in full.

WHAT THESE TESTS HOLD. `render(detail=False)` keeps the header, the index and
the foot-line and drops the per-decision sections; `render(detail=True)` is
unchanged, which matters because the REPOSITORY copy is what
`scripts/do_the_two_decision_surfaces_agree_2026-11-01.py` reads and it needs
the `DECISION n.` headings. The split was checked against 3 dependencies before
it was made: that checker reads the repository glob, `sync_desktop_mirrors`
does not mirror this file, and the module's exit-0 postcondition is computed
from `rows`.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
BUILD = REPO / "scripts/build_decisions_file_2026-11-07.py"
MIRRORS = REPO / "scripts/sync_desktop_mirrors.py"
AGREE = REPO / "scripts/do_the_two_decision_surfaces_agree_2026-11-01.py"


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_bdf", BUILD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_bdf"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rendered(mod):
    try:
        mrb, rows = mod.collect()
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"the decision queue is not collectable here: {exc}")
    if len(rows) < 2:
        pytest.skip(f"only {len(rows)} decision(s); the split is not exercisable")
    return (rows,
            mod.render(mrb, rows, spoken=True, detail=True),
            mod.render(mrb, rows, spoken=True, detail=False))


class TestTheIndexCopyIsShorterAndComplete:
    def test_the_fixture_has_a_long_tier_to_drop(self, rendered):
        """ANTI-VACUITY. If the full render ever stops carrying per-decision
        sections, every assertion below passes while testing nothing."""
        _rows, full, _idx = rendered
        assert len(re.findall(r"^DECISION \d+\.", full, re.M)) >= 2

    def test_his_copy_drops_the_per_decision_sections(self, rendered):
        _rows, _full, idx = rendered
        assert re.search(r"^DECISION \d+\.", idx, re.M) is None, (
            "the index copy still carries a per-decision section")

    def test_his_copy_still_names_every_decision(self, rendered):
        """The point is to shorten the file, never to drop a decision."""
        rows, _full, idx = rendered
        missing = [r["ident"] for r in rows if r["ident"] not in idx]
        assert not missing, f"{len(missing)} decision(s) absent from the index: {missing[:4]}"

    def test_his_copy_carries_a_recommendation_for_each(self, rendered):
        rows, _full, idx = rendered
        n = len(re.findall(r"Recommended option \d+", idx))
        assert n >= len(rows), f"{n} recommendations for {len(rows)} decisions"

    def test_his_copy_is_a_small_fraction_of_the_full_render(self, rendered):
        _rows, full, idx = rendered
        assert len(idx) < 0.25 * len(full), (
            f"the index is {len(idx) / len(full):.4f} of the full render; the "
            f"whole purpose is that it is a small fraction")

    def test_his_copy_says_where_the_rest_is(self, rendered):
        """A file that silently omits the argument is worse than a long one."""
        _rows, _full, idx = rendered
        assert "repository" in idx.lower()

    def test_his_copy_keeps_the_foot_line(self, rendered):
        _rows, _full, idx = rendered
        assert idx.rstrip().endswith("(1 November 2026).")


class TestTheRepositoryCopyIsUntouched:
    def test_the_full_render_keeps_its_headings(self, rendered):
        """`do_the_two_decision_surfaces_agree` parses `DECISION n. <heading>`
        out of the REPOSITORY copy, so those lines may not move."""
        rows, full, _idx = rendered
        got = re.findall(r"^DECISION (\d+)\.", full, re.M)
        assert [int(x) for x in got] == list(range(1, len(rows) + 1))

    def test_the_agreement_checker_reads_the_repository_not_the_desktop(self):
        """PINNED. If this ever changes to the Desktop path, the index copy
        would start failing that checker and the reason would be this split."""
        src = AGREE.read_text(encoding="utf-8")
        assert 'SPOKEN_DIR = REPO / "experimental_notes"' in src

    def test_this_file_is_not_desktop_mirrored(self):
        """PINNED. A mirror entry would copy the full repository text back over
        his index copy, silently undoing the split."""
        src = MIRRORS.read_text(encoding="utf-8")
        assert "Decisions_Awaiting_You" not in src

    def test_the_heading_count_is_derived_not_typed(self, mod):
        """The heading read `THE 29 AT A GLANCE` and would go stale on his first
        ruling.

        ★ ASSERTED BY EXECUTION, NOT BY SOURCE TEXT, and the first version of
        this test proved why. It read `assert "THE 29 AT A GLANCE" not in src`
        and FAILED on the comment that documents the repair -- the fix explains
        itself by quoting the old string, so a text check reads the scar as the
        wound (`feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02`).
        Rendering a SHORTER row list is the behaviour that matters: a typed
        count cannot track it."""
        try:
            mrb, rows = mod.collect()
        except Exception as exc:                               # noqa: BLE001
            pytest.skip(f"the decision queue is not collectable here: {exc}")
        if len(rows) < 3:
            pytest.skip("too few decisions to render a different count")
        few = rows[:3]
        out = mod.render(mrb, few, spoken=True, detail=False)
        assert "THE 3 AT A GLANCE" in out, (
            "the heading does not follow the number of decisions rendered")
        assert f"THE {len(rows)} AT A GLANCE" not in out


MRB = REPO / "scripts/morning_report_build_2026-10-12.py"
PINNED = REPO / "bench/tests/test_the_report_structure_is_pinned_2026-11-03.py"


@pytest.fixture(scope="module")
def mrb():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_mrb_split", MRB)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_mrb_split"] = m
    spec.loader.exec_module(m)
    return m


class TestTheSpokenMorningReportStopsRepeatingTheDecisions:
    """THE SECOND HALF OF HIS COMPLAINT. He was sent 2 files on 2026-11-08,
    22,555 and 22,505 words, and 0.690653 of the morning report's 12-word
    sequences also appear in the decisions file -- because this renderer and
    `build_decisions_file` each render every decision in full from the same
    authored detail. Shortening 1 file alone would have handed him the same
    text under another name."""

    @staticmethod
    def _pair(m):
        try:
            items = m.task_items()
            decs = m.decisions(items)[0]
        except Exception as exc:                               # noqa: BLE001
            pytest.skip(f"the decision queue is not collectable here: {exc}")
        if len(decs) < 2:
            pytest.skip(f"only {len(decs)} decision(s); the split is not exercisable")
        args = (decs, [], [], [], [], None, ())
        return decs, m.render_tts(*args, detail=True), m.render_tts(*args, detail=False)

    def test_the_full_render_carries_the_sections_to_drop(self, mrb):
        """ANTI-VACUITY: without this the assertions below could pass on a
        renderer that never emitted a decision section at all."""
        decs, full, _idx = self._pair(mrb)
        assert len(re.findall(r"^DECISION \d+\.", full, re.M)) == len(decs)

    def test_his_copy_drops_them(self, mrb):
        _decs, _full, idx = self._pair(mrb)
        assert re.search(r"^DECISION \d+\.", idx, re.M) is None

    def test_his_copy_still_states_the_count_and_where_they_are(self, mrb):
        """A silent omission would be worse than the duplication."""
        decs, _full, idx = self._pair(mrb)
        assert str(len(decs)) in idx
        assert "decisions file" in idx.lower()

    def test_his_copy_keeps_the_rest_of_the_report(self, mrb):
        """Sections 2 onward are this report's OWN content and must survive."""
        _decs, _full, idx = self._pair(mrb)
        assert "SECTION 2." in idx and "SECTION 1." in idx

    def test_the_markdown_renderer_is_untouched(self, mrb):
        """PINNED. The verbatim-region markers that
        `test_the_report_structure_is_pinned_2026-11-03.py` balances are emitted
        by `render_md`, which is why the split was made in the spoken renderer
        only. If `render_md` ever grows a `detail` flag, that balance becomes
        reachable from here and this pin should be reconsidered deliberately."""
        src = MRB.read_text(encoding="utf-8")
        sig = [ln for ln in src.splitlines() if ln.startswith("def render_md(")]
        assert sig == ["def render_md(decs, outstanding, done, owed, parked, since, superseded=()) -> str:"], sig
        assert PINNED.is_file(), "the guard this pin defers to has gone"
