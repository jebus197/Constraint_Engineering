"""Section R: a ruling he gave must not still be recorded as a question.

THE DEFECT THIS SECTION EXISTS FOR, measured 2026-09-09: all 5 sources an
inventory read were written BEFORE at least 1 later message from him -- 5 of 5,
Wilson [56.6%, 100.0%]. `OUTSTANDING_QUEUE_to_BR2.md` was 16 days old with all
311 of his typed messages arriving since. A document written before he spoke
cannot record what he said. The remedy is to write his rulings back into the
documents that still ask for them.

These tests hold the write-backs, so a document cannot drift back to asking a
settled question. They assert on document TEXT deliberately -- the property under
test IS what a document says, which is the one case where reading is the right
instrument rather than the wrong one.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _text(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        pytest.skip(f"{rel} not present in this clone")
    return p.read_text(encoding="utf-8", errors="replace")


class TestR4SeverityIsNoLongerOpen:
    def test_the_runway_no_longer_calls_it_unactionable(self):
        t = _text("experimental_notes/RUNWAY_to_BR2_2026-08-18.md")
        i = t.index("| FW.7 |")
        row = t[i:t.index("\n", i)]
        assert "Not actionable without a design decision" not in row, row[:200]
        assert "RULED AND BUILT" in row

    def test_the_research_record_no_longer_says_needs_founder(self):
        t = _text("experimental_notes/Research_FULL_RECORD_2026-09-09.md")
        i = t.index("102. FW.7")
        entry = t[i:t.index("\n", i)]
        assert "NO LONGER NEEDS THE FOUNDER" in entry, entry[:200]

    def test_the_decisions_file_is_annotated_not_rewritten(self):
        """It records what was ASKED. Rewriting it would erase that he was asked."""
        t = _text("experimental_notes/DECISIONS_AWAITING_YOU_2026-09-06.md")
        assert "My recommendation: Replace with the consequence-class rubric" in t, (
            "the original recommendation is gone; this file is a record of what "
            "the assistant proposed and he rejected")
        assert "THE RECOMMENDATION WAS REJECTED" in t

    def test_the_measurement_that_settled_it_travels_with_the_ruling(self):
        """kappa = -0.0227 is why the rubric swap was refused, not a preference."""
        t = _text("experimental_notes/RUNWAY_to_BR2_2026-08-18.md")
        assert "-0.0227" in t and "0.78" in t


class TestR5MaterialityIsNotPending:
    def test_recovery_no_longer_says_pending(self):
        t = _text("resources/RECOVERY.md")
        assert "PENDING — HIL materiality confirmation (founder)." not in t or \
               "RULED 2026-09-06" in t, (
            "RECOVERY still carries the materiality check as pending")


class TestR7TheSealingIsRecordedAsHisOwnWork:
    def test_the_tracker_credits_him_and_the_time(self):
        t = _text("experimental_notes/CDSFL_Agent_Operational_Plan.md")
        assert "DONE BY THE FOUNDER HIMSELF, 2026-09-07 at 22:03" in t, (
            "the tracker no longer records that he sealed the keys himself; it "
            "once listed this as awaiting his passphrase while he had already "
            "driven home to do it")


class TestR8TheBlindValidityQuestionIsAnswered:
    def test_the_docstring_carries_his_answer(self):
        t = _text("bench/tests/test_br2_keys_are_split_out_2026-08-27.py")
        assert "is a founder decision and it is open" not in t, (
            "the test still calls a question open that he answered 6 minutes "
            "and 46 seconds after it was written")
        assert "never been ran" in t, "his actual words are not recorded"

    def test_the_reason_survives_the_answer(self):
        """His answer did not make splitting the keys pointless."""
        t = _text("bench/tests/test_br2_keys_are_split_out_2026-08-27.py")
        assert "stops the exposure growing" in t


class TestR9TheLoadBalancerIsShelvedNotRetired:
    def test_the_runway_row_carries_the_ruling(self):
        t = _text("experimental_notes/RUNWAY_to_BR2_2026-08-18.md")
        i = t.index("| 6 | the **load balancer**")
        row = t[i:t.index("\n", i)]
        assert "SHELVED, NOT RETIRED" in row, row[:200]

    def test_the_findings_behind_it_are_kept(self):
        """He rejected the disposition, not the evidence."""
        t = _text("experimental_notes/RUNWAY_to_BR2_2026-08-18.md")
        i = t.index("| 6 | the **load balancer**")
        row = t[i:t.index("\n", i)]
        for fact in ("never ran outside its own tests",
                     "impossible allocations as successes",
                     "4.5 months"):
            assert fact in row, f"the finding {fact!r} was dropped with the recommendation"
