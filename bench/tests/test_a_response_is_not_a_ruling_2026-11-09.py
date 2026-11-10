"""`responded:` records that he REPLIED; `ruled:` SETTLES. They must not merge.

WHY THIS EXISTS. On 2026-11-09, 8 of 14 live task-list entries carried a ruling
in their PROSE that the marker did not hold, so every machine surface believed
he had never replied and the original question was put to him again. The
obvious repair -- write the date into `ruled:` -- was tried and FALSIFIED the
same hour: `morning_report_build.decisions()` routes any entry carrying a
`ruled:` date to `no_ruling_needed` unless `ruling_is_spent` says otherwise, so
backfilling 5 entries REMOVED all 5 from the decision list while each still
asked him something. `bench/tests/test_the_two_decision_surfaces_cannot_diverge_2026-11-01.py`
caught it and all 5 were reverted.

THESE TESTS EXECUTE. None asserts on source text. The suppression test calls
the real routing predicate, and the rendering test calls the real renderer and
reads its output string, because a producer and a consumer that disagree are
each individually correct and only running both can see it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def tlm():
    return _load("tlm_resp", "scripts/task_list_markers.py")


@pytest.fixture(scope="module")
def mrb():
    return _load("mrb_resp", "scripts/morning_report_build_2026-10-12.py")


@pytest.fixture(scope="module")
def bdf():
    return _load("bdf_resp", "scripts/build_decisions_file_2026-11-07.py")


class TestTheFieldExistsAndParses:
    def test_the_marker_pattern_reads_responded(self, tlm):
        m = tlm.MARKER.match(
            "<!-- task: Z9 | state: OPEN | status: PROPOSED | ruled: 2026-01-01 "
            "| responded: 2026-02-02 -->")
        assert m is not None, "the extended marker no longer parses"
        assert m.group(5).strip() == "2026-01-01"
        assert m.group(6).strip() == "2026-02-02", (
            "group 6 must be `responded`; if this is None the field was removed")

    def test_a_marker_without_responded_still_parses(self, tlm):
        m = tlm.MARKER.match("<!-- task: Z9 | state: OPEN | status: PROPOSED -->")
        assert m is not None and (m.group(6) or "") == "", (
            "the field must stay OPTIONAL -- an entry predating it cannot break")

    def test_the_entry_carries_the_field(self, tlm):
        assert "responded" in tlm.Entry.__dataclass_fields__, (
            "Entry lost the `responded` field, so nothing downstream can read it")

    def test_the_live_list_parses_and_some_entry_uses_it(self, tlm):
        es = tlm.parse_entries()
        assert len(es) > 200, "the live list stopped parsing"
        used = [e.ident for e in es if e.responded]
        assert used, (
            "no live entry carries `responded:`, so this field is an addition "
            "nothing reaches -- the failure mode `additive-standard` names")


class TestAResponseNeverSuppresses:
    """The whole point. A `ruled` date silences an entry; a `responded` must not."""

    def test_no_predicate_in_the_routing_reads_responded(self, tlm, mrb):
        es = {e.ident: e for e in tlm.parse_entries()}
        responders = [e for e in es.values()
                      if e.responded and not e.ruled
                      and (e.state or "").upper() not in ("DONE", "WITHDRAWN")]
        assert responders, "no entry exercises this case, so the test is vacuous"
        for e in responders:
            assert e.ruled is None, (
                f"{e.ident} gained a `ruled:` date; a reply is not a ruling")

    def test_every_responder_still_reaches_the_decision_list(self, mrb, tlm):
        es = {e.ident: e for e in tlm.parse_entries()}
        want = {i for i, e in es.items()
                if e.responded and not e.ruled
                and (e.state or "").upper() not in ("DONE", "WITHDRAWN")}
        assert want, "vacuous: nothing to check"
        got = {d.get("ident") for d in mrb.decisions(mrb.task_items())[0]}
        missing = sorted(want - got)
        assert not missing, (
            f"these entries carry a reply and vanished from the decision list, "
            f"which is the suppression this field exists to avoid: {missing}")

    def test_task_items_carries_it_through(self, mrb):
        items = {i["ident"]: i for i in mrb.task_items()}
        assert any("responded" in v for v in items.values()), (
            "task_items dropped `responded`, so the renderer can never see it")


class TestTheRenderedFileSaysSo:
    """Execute the renderer and read its OUTPUT, never its source."""

    def test_the_note_appears_for_an_entry_he_answered(self, bdf):
        mrb_mod, rows = bdf.collect()
        assert any(r.get("responded") for r in rows), (
            "no row carries a reply date, so this assertion cannot fail")
        out = bdf.render(mrb_mod, rows, spoken=True)
        assert "You responded on this on" in out, (
            "the spoken decisions file does not tell him he already answered -- "
            "the exact defect measured on 2026-11-09, when 53,898 bytes carried "
            "0 mentions of his 2026-11-08 replies")

    def test_it_says_the_entry_is_still_open(self, bdf):
        mrb_mod, rows = bdf.collect()
        out = bdf.render(mrb_mod, rows, spoken=True)
        i = out.find("You responded on this on")
        assert i >= 0
        assert "still open" in out[i:i + 200], (
            "the note must say the entry is STILL OPEN, or it reads as a closure")

    def test_both_renders_carry_it(self, bdf):
        mrb_mod, rows = bdf.collect()
        for spoken in (True, False):
            out = bdf.render(mrb_mod, rows, spoken=spoken)
            assert "You responded on this on" in out, (
                f"the {'spoken' if spoken else 'written'} surface lost the note; "
                f"he reads both")

    def test_a_ruling_note_and_a_reply_note_are_different_sentences(self, bdf):
        mrb_mod, rows = bdf.collect()
        out = bdf.render(mrb_mod, rows, spoken=True)
        if "You ruled on this entry on" in out:
            assert "You responded on this on" in out, (
                "both branches must be reachable in the same render")
            assert out.count("You ruled on this entry on") >= 1

class TestTheWritePathKeepsThemApart:
    """★ ADDED AFTER A MUTATION SURVIVED, 2026-11-09.

    The first version of this file read markers from disk and never called
    `set_marker`, so the mutation `new_ruled = new_ruled or responded` -- the
    exact repair that was falsified an hour earlier -- left all 11 tests GREEN.
    A guard that cannot see the defect it was written for is the failure
    `execute-do-not-grep` names. These tests WRITE and read back.
    """

    def _scratch(self, tmp_path, tlm):
        dst = tmp_path / "list.md"
        dst.write_text(
            "**Z9. A planted entry.**\n"
            "<!-- task: Z9 | state: OPEN | status: PROPOSED -->\n",
            encoding="utf-8")
        return dst

    def test_a_reply_lands_in_responded_and_not_in_ruled(self, tlm, tmp_path):
        dst = self._scratch(tmp_path, tlm)
        line = tlm.set_marker("Z9", responded="2026-02-02", path=dst)
        assert "responded: 2026-02-02" in line, (
            f"set_marker did not write the reply date as `responded`: {line}")
        assert "ruled:" not in line, (
            f"A REPLY WAS WRITTEN AS A RULING, which SUPPRESSES the entry. "
            f"This is the repair that was tried and falsified on 2026-11-09: "
            f"{line}")
        e = tlm.parse_entries(dst)[0]
        assert e.responded == "2026-02-02" and e.ruled is None

    def test_a_ruling_still_lands_in_ruled(self, tlm, tmp_path):
        dst = self._scratch(tmp_path, tlm)
        line = tlm.set_marker("Z9", ruled="2026-03-03", path=dst)
        assert "ruled: 2026-03-03" in line and "responded:" not in line, line
        e = tlm.parse_entries(dst)[0]
        assert e.ruled == "2026-03-03" and e.responded is None

    def test_both_can_coexist_and_neither_eats_the_other(self, tlm, tmp_path):
        dst = self._scratch(tmp_path, tlm)
        tlm.set_marker("Z9", ruled="2026-03-03", path=dst)
        tlm.set_marker("Z9", responded="2026-04-04", path=dst)
        e = tlm.parse_entries(dst)[0]
        assert e.ruled == "2026-03-03", "writing a reply dropped his ruling date"
        assert e.responded == "2026-04-04"

    def test_advancing_state_carries_both_over(self, tlm, tmp_path):
        dst = self._scratch(tmp_path, tlm)
        tlm.set_marker("Z9", ruled="2026-03-03", responded="2026-04-04", path=dst)
        tlm.set_marker("Z9", status="TESTED", path=dst)
        e = tlm.parse_entries(dst)[0]
        assert (e.ruled, e.responded) == ("2026-03-03", "2026-04-04"), (
            "advancing status silently dropped a date the founder earned")
