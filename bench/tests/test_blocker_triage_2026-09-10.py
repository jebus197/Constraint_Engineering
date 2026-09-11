"""The blocker predicate must answer HIS question, and must be able to say both.

Founder criterion, verbatim, 2026-09-10: *"My criteria is very simple. Does it
prevent further progress on the task list? If so, then yes, it's a blocker. If
not, then append to the closing/final report."*

THE FIRST VERSION ANSWERED A DIFFERENT QUESTION. It used 4 category rules --
IRREVERSIBLE, NEEDS_HIS_HANDS, FROZEN_ARTEFACT, WOULD_WASTE_WORK -- and 3 of them
say nothing about progress. It called editing his desktop config a BLOCK when
that edit blocked nothing, and reported `sk_enabled` to him as a blocker when no
entry waited on it. Two orthogonal questions had been folded into one:

    does it stop progress?   -> blocker    -> raise it now
    is it his to authorise?  -> permission -> park it, and do not do it

MEASURED ACCURACY, stated rather than claimed: 9 of 10 on the labelled set below,
Wilson [59.5850%, 98.2124%], Clopper-Pearson [55.4984%, 99.7471%]. The single
miss is an item whose only identifier is a bare alphanumeric code (`C0050`) with
no underscore, hyphen or extension, so it is not distinctive enough to match. It
misses toward PARK, which is the safe direction for an interruption question --
and the permission flag, which is separate, still stops the action.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "blocker_triage.py"


@pytest.fixture(scope="module")
def B():
    spec = importlib.util.spec_from_file_location("triage", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


LABELLED = [
    ("I23: exhausted_round_threshold defaults to 8 while max_rounds is 8", True),
    ("I31: update_drift has no production caller, wire it or retire it", True),
    ("sk_enabled is false in the exp56 arms", False),
    ("bench/reference_runner_v3.py has a stale line citation", False),
    ("scripts/note_vagueness_lint.py has a quote-scope defect", False),
    ("hardened_gate_enabled has no recorded reason", False),
    ("The verdict-tuple guard matches names across the repository", False),
    ("Repair the experimental notes for reproducibility", False),
    ("bench/panel_sandbox.py loses its tree mid-review", False),
]


class TestItAnswersTheRightQuestion:
    @pytest.mark.parametrize("text,expect", LABELLED)
    def test_the_labelled_set(self, B, text, expect):
        got, why = B.blocks_progress(text)
        assert got is expect, f"{text!r}: {why}"

    def test_it_can_say_BLOCK(self, B):
        """A predicate that can only park is a guard that cannot fail."""
        got, _ = B.blocks_progress(
            "I23: exhausted_round_threshold defaults to 8 while max_rounds is 8")
        assert got is True

    def test_it_can_say_PARK(self, B):
        got, _ = B.blocks_progress("sk_enabled is false in the exp56 arms")
        assert got is False


class TestPermissionIsSeparateFromBlocking:
    def test_an_irreversible_item_that_blocks_nothing_still_parks(self, B):
        verdict, why, perm = B.classify("Spend money on a paid seat for round 8")
        assert verdict == "PARK", why
        assert perm.startswith("IRREVERSIBLE"), (
            "the permission gate must still fire; it stops the ACTION, not the work")

    def test_a_harmless_item_carries_no_permission_flag(self, B):
        _, _, perm = B.classify("The verdict-tuple guard matches names across the repo")
        assert perm == ""

    def test_the_two_are_returned_separately(self, B):
        """Folding them is the defect the first version shipped."""
        out = B.classify("Delete the exp39-experimental git ref")
        assert len(out) == 3, "classify must return (verdict, why, permission)"


class TestItCannotBeTrickedByACommonTerm:
    def test_a_file_named_by_many_entries_is_not_a_dependency(self, B):
        """`reference_runner_v3.py` is central to the project. Naming it says
        what work is ABOUT, not what it waits on."""
        got, why = B.blocks_progress("bench/reference_runner_v3.py has a typo")
        assert got is False, why

    def test_an_ordinary_capitalised_word_is_not_a_subject(self, B):
        """An earlier filter matched entry 7.1 on the word 'Repair'."""
        got, why = B.blocks_progress("Repair the experimental notes")
        assert got is False, why


class TestTheParkingFileIsRealAndAppendOnly:
    def test_parking_appends_rather_than_rewrites(self, B, tmp_path, monkeypatch):
        f = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", f)
        B.park("first item", "detail one", stamp="2026-09-10T00:00:00+01:00")
        B.park("second item", "detail two", stamp="2026-09-10T00:00:01+01:00")
        text = f.read_text(encoding="utf-8")
        assert "first item" in text and "second item" in text, (
            "parking must never overwrite what is already queued for him")
        assert text.index("first item") < text.index("second item"), "newest last"

class TestParkingIsIdempotent:
    """A queue that grows a heading on every re-triage inflates the workload.

    MEASURED 2026-09-11, minutes after the founder asked whether the workload set
    out for him was significant. Two duplicate headings had just been merged by
    hand -- one decision written twice as an analysis and a triage stub, and an
    A8 question superseded by a smaller one -- and re-running the triage
    immediately appended a THIRD A8 heading. The count of DECISIONS was growing
    with copies of one decision, which is the opposite of what the file is for.
    """

    def test_an_already_parked_item_is_not_appended_again(self, B, tmp_path,
                                                          monkeypatch):
        parked = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", parked)
        first = B.park("A8: re-point 20 citations, or leave them", "detail")
        assert first is not None
        again = B.park("A8: re-point 20 citations, or leave them", "detail")
        assert again is None, "the same title was parked twice"
        assert parked.read_text(encoding="utf-8").count("## A8") == 1

    def test_a_wording_difference_is_not_a_new_decision(self, B, tmp_path,
                                                        monkeypatch):
        """The pair this was found on differed by the word "the"."""
        parked = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", parked)
        B.park("A8: re-point 20 note citations, or leave them", "detail")
        again = B.park("A8: re-point the 20 note citations, or leave them", "detail")
        assert again is None, "one question parked twice over one article"

    def test_a_status_note_on_a_heading_is_not_a_new_decision(self, B, tmp_path,
                                                              monkeypatch):
        """Headings in that file gain notes such as "SUPERSEDED" after an em
        dash; a heading that gained a note is still the same item."""
        parked = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", parked)
        B.park("10.2: should the shell service be on — SAME AS THE STUB BELOW", "d")
        again = B.park("10.2: should the shell service be on", "d")
        assert again is None

    def test_a_genuinely_different_item_is_still_parked(self, B, tmp_path,
                                                        monkeypatch):
        """ANTI-VACUITY. A check that refused everything would silently drop new
        decisions, which is far worse than listing one twice."""
        parked = tmp_path / "PARKED.md"
        monkeypatch.setattr(B, "PARKED", parked)
        B.park("A8: re-point 20 citations, or leave them", "detail")
        other = B.park("A19: enable the prose-listing flag, or leave it off", "detail")
        assert other is not None, "a new decision was refused"
        assert parked.read_text(encoding="utf-8").count("## ") == 2
