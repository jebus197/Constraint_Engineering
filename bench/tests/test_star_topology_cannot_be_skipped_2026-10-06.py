#!/usr/bin/env python3
"""A blind round each, then a joint round — enforced by the machinery.

THE FOUNDER'S RULING, 2026-10-06, verbatim: *"I didn't just state it as a 'preference',
I stated that it should be built into all confer round machinery going forward so it
couldn't be skipped."* The preference it corrects: *"Remember panel review runs in star
topology format, with a blind round each and a joint round once the blind round is in."*

WHAT WAS SKIPPABLE. Blindness was opt-in through `PANEL_BLIND_OF` and nothing checked
it. On 2026-10-06 the cc2 blind round was dispatched while the fable round's entire
reply sat in the live tree, and the only thing between them was the operator remembering
1 environment variable. The purge worked. The discipline was unenforced, and a control
that depends on remembering is not a control.
`test_tonights_dispatch_would_have_been_refused_without_the_variable` runs the check
against the 2 real round directories.

THE GROUPING KEY IS THE BRIEF. Rounds asking the same question carry a byte-identical
`BRIEF.md`, so sha256 over it finds the siblings with nothing to label and nothing to
forget. A joint round cannot be grouped that way -- its brief carries the blind replies
-- so it declares its parents and is refused unless every seat it dispatches has a
landed blind reply among them.

"LANDED" MEANS A NON-EMPTY `response`, DEFINED IN ONE PLACE. cc2's failed round wrote a
9280-byte reply file carrying `ok: False` and 0 words; a file-existence test would have
called that a landed blind round and let a joint round be built on nothing. The
watchdog previously carried a SECOND copy of that predicate, which is how a producer
and a consumer drift while each remains individually correct;
`test_the_watchdog_does_not_carry_a_second_definition` holds the collapse.
"""
import ast
import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PANEL = REPO / "bench" / "confer_maths_panel_2026-09-05.py"
WATCHDOG = REPO / "scripts" / "panel_round_watchdog_2026-10-06.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def ST():
    return _load("st_under_test", REPO / "bench" / "star_topology_2026-10-06.py")


def _round(logs, name, brief, replies=None):
    d = logs / name
    d.mkdir(parents=True)
    (d / "BRIEF.md").write_text(brief, encoding="utf-8")
    for seat, resp in (replies or {}).items():
        (d / f"{seat}.json").write_text(
            json.dumps({"model": seat, "ok": bool(resp), "response": resp}),
            encoding="utf-8")
    return d


class TestLandedIsNonEmpty:
    def test_a_real_reply_counts_its_words(self, ST, tmp_path):
        d = _round(tmp_path, "r", "Q", {"fable": "one two three"})
        assert ST.seat_reply_words(d, "fable") == 3

    def test_an_empty_response_is_not_landed(self, ST, tmp_path):
        """THE REAL CASE. cc2 wrote 9280 bytes with 0 words of response."""
        d = _round(tmp_path, "r", "Q", {"cc2": ""})
        assert ST.seat_reply_words(d, "cc2") == 0
        assert ST.landed_seats(d) == set()

    def test_a_missing_file_is_not_landed(self, ST, tmp_path):
        d = _round(tmp_path, "r", "Q")
        assert ST.seat_reply_words(d, "cc2") == 0

    def test_an_unreadable_file_is_not_landed(self, ST, tmp_path):
        d = _round(tmp_path, "r", "Q")
        (d / "cc2.json").write_text("{not json", encoding="utf-8")
        assert ST.seat_reply_words(d, "cc2") == 0

    def test_metadata_files_are_not_mistaken_for_seats(self, ST, tmp_path):
        d = _round(tmp_path, "r", "Q", {"fable": "hello there"})
        for junk in ("canonical_touched", "sandbox_manifest", "watchdog_status"):
            (d / f"{junk}.json").write_text('{"response": "x y"}', encoding="utf-8")
        (d / "fable.tools.json").write_text('{"response": "x y"}', encoding="utf-8")
        assert ST.landed_seats(d) == {"fable"}


class TestTheBriefGroupsTheQuestion:
    def test_identical_briefs_are_siblings(self, ST, tmp_path):
        _round(tmp_path, "a", "SAME", {"fable": "answered here"})
        _round(tmp_path, "b", "SAME")
        assert ST.sibling_rounds_on_the_same_question(tmp_path, "b") == ["a"]

    def test_a_different_brief_is_not_a_sibling(self, ST, tmp_path):
        _round(tmp_path, "a", "ONE QUESTION", {"fable": "answered here"})
        _round(tmp_path, "b", "A DIFFERENT QUESTION")
        assert ST.sibling_rounds_on_the_same_question(tmp_path, "b") == []

    def test_an_unanswered_sibling_is_not_a_hazard(self, ST, tmp_path):
        """A failed sibling must not block its own re-dispatch: there is nothing
        to leak from a round that produced no reply. cc2's first attempt is
        exactly this case."""
        _round(tmp_path, "a", "SAME", {"cc2": ""})
        _round(tmp_path, "b", "SAME")
        assert ST.sibling_rounds_on_the_same_question(tmp_path, "b") == []
        assert ST.check_blind_round(tmp_path, "b", []) is None


class TestTheBlindRoundIsChecked:
    def test_an_undeclared_answered_sibling_is_refused(self, ST, tmp_path):
        _round(tmp_path, "a", "SAME", {"fable": "my whole position"})
        _round(tmp_path, "b", "SAME")
        msg = ST.check_blind_round(tmp_path, "b", [])
        assert msg and "REFUSED" in msg and "a" in msg

    def test_the_refusal_prints_the_fixing_command(self, ST, tmp_path):
        _round(tmp_path, "a", "SAME", {"fable": "my whole position"})
        _round(tmp_path, "b", "SAME")
        msg = ST.check_blind_round(tmp_path, "b", [])
        assert "PANEL_BLIND_OF=a" in msg, (
            "the refusal does not tell the operator how to proceed correctly")

    def test_declaring_the_sibling_allows_the_round(self, ST, tmp_path):
        _round(tmp_path, "a", "SAME", {"fable": "my whole position"})
        _round(tmp_path, "b", "SAME")
        assert ST.check_blind_round(tmp_path, "b", ["a"]) is None

    def test_a_round_with_no_brief_is_not_grouped(self, ST, tmp_path):
        (tmp_path / "b").mkdir()
        assert ST.check_blind_round(tmp_path, "b", []) is None


class TestTheJointRoundIsChecked:
    def test_a_joint_round_must_declare_its_parents(self, ST, tmp_path):
        _round(tmp_path, "j", "JOINT BRIEF")
        msg = ST.check_joint_round(tmp_path, "j", [], ["cc2", "fable"])
        assert msg and "PANEL_JOINT_OF" in msg

    def test_a_seat_with_no_landed_blind_reply_is_refused(self, ST, tmp_path):
        _round(tmp_path, "a", "Q", {"fable": "fable answered"})
        _round(tmp_path, "j", "JOINT BRIEF")
        msg = ST.check_joint_round(tmp_path, "j", ["a"], ["cc2", "fable"])
        assert msg and "cc2" in msg, (
            "a seat joining the joint round without answering blind has seen the "
            "others' positions before forming its own")

    def test_all_seats_answered_allows_the_joint_round(self, ST, tmp_path):
        _round(tmp_path, "a", "Q", {"fable": "fable answered"})
        _round(tmp_path, "b", "Q", {"cc2": "cc2 answered"})
        _round(tmp_path, "j", "JOINT BRIEF")
        assert ST.check_joint_round(tmp_path, "j", ["a", "b"],
                                    ["cc2", "fable"]) is None

    def test_an_empty_blind_reply_does_not_satisfy_the_joint_gate(self, ST, tmp_path):
        """THE CASE THAT MATTERS. A 9280-byte file with 0 words is not an answer."""
        _round(tmp_path, "a", "Q", {"fable": "fable answered"})
        _round(tmp_path, "b", "Q", {"cc2": ""})
        _round(tmp_path, "j", "JOINT BRIEF")
        msg = ST.check_joint_round(tmp_path, "j", ["a", "b"], ["cc2", "fable"])
        assert msg and "cc2" in msg

    def test_a_nonexistent_parent_is_refused(self, ST, tmp_path):
        _round(tmp_path, "j", "JOINT BRIEF")
        msg = ST.check_joint_round(tmp_path, "j", ["no_such_round"], ["cc2"])
        assert msg and "does not exist" in msg


class TestAgainstTonightsRealRounds:
    def test_tonights_dispatch_would_have_been_refused_without_the_variable(self, ST):
        """REGRESSION against the live tree, not a fixture.

        Skips rather than passes vacuously if the rounds have been archived away.
        """
        logs = REPO / "bench" / "logs"
        a = "capability_ladder_design_blind_2026-10-06"
        b = "capability_ladder_design_blind_cc2_2026-10-06"
        if not (logs / a / "BRIEF.md").is_file() or not (logs / b / "BRIEF.md").is_file():
            pytest.skip("the 2026-10-06 ladder rounds are no longer on disk")
        assert ST.brief_fingerprint(logs / a) == ST.brief_fingerprint(logs / b), (
            "the 2 rounds no longer carry byte-identical briefs, so this test is "
            "not measuring the condition it was written for")
        if not ST.landed_seats(logs / a):
            pytest.skip("the fable round carries no landed reply any more")
        assert ST.check_blind_round(logs, b, []) is not None, (
            "dispatching cc2 with no PANEL_BLIND_OF would have been ALLOWED while "
            "fable's whole reply was reachable from its sandbox")
        assert ST.check_blind_round(logs, b, [a]) is None


class TestTheMachineryRunsIt:
    def test_the_panel_calls_the_topology_check(self):
        tree = ast.parse(PANEL.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and (getattr(n.func, "id", None)
                      or getattr(n.func, "attr", None))
                 == "_refuse_if_topology_is_skipped"]
        assert calls, "the dispatcher never checks the topology"

    def test_the_topology_check_precedes_the_aliveness_probe(self):
        """A refusal that needs no network should cost no network."""
        tree = ast.parse(PANEL.read_text(encoding="utf-8"))

        def line_of(fn):
            return min(n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
                       and (getattr(n.func, "id", None)
                            or getattr(n.func, "attr", None)) == fn)
        assert line_of("_refuse_if_topology_is_skipped") < line_of(
            "_refuse_if_a_seat_is_not_alive"), (
            "the aliveness probe runs before the topology check, so a round that "
            "must be refused anyway still spends a network call first")

    def test_the_joint_declaration_is_read_from_the_environment(self):
        src = PANEL.read_text(encoding="utf-8")
        assert 'PANEL_JOINT_OF' in src

    def test_a_check_that_cannot_load_refuses(self):
        src = PANEL.read_text(encoding="utf-8")
        i = src.index("def _refuse_if_topology_is_skipped")
        body = src[i:i + 2200]
        assert "could not be loaded" in body and "return 2" in body


class TestNoSecondDefinition:
    def test_the_watchdog_does_not_carry_a_second_definition(self):
        """2 correct definitions of 1 predicate still drift apart."""
        src = WATCHDOG.read_text(encoding="utf-8")
        assert "seat_reply_words" in src, (
            "the watchdog does not delegate to the single definition of 'landed'")
        assert 'd.get("response")' not in src, (
            "the watchdog still re-implements the emptiness test, so the project "
            "has 2 definitions of 'landed' that can disagree")

    def test_both_agree_on_the_live_rounds(self, ST):
        logs = REPO / "bench" / "logs"
        a = logs / "capability_ladder_design_blind_2026-10-06"
        if not a.is_dir():
            pytest.skip("the 2026-10-06 fable round is no longer on disk")
        wd = _load("wd_under_test", WATCHDOG)
        ok, _ = wd.reply_has_landed(a, ["fable"])
        assert ok == bool(ST.landed_seats(a)), (
            "the watchdog and the star-topology module disagree about whether the "
            "same round landed")
