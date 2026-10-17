"""An absorbed proposal keeps its own words.

FOUND BY THE REGISTER REFUSING MY OWN WORK, 2026-10-17. A genuinely new feature
request from the design brief he attached -- namespace paths -- was NOT
CREATED. `propose` returned `subject-settled` and handed back the ticket for
the register's new command-line entry point, closed minutes earlier. The two
share exactly 1 code identifier, `area_of`. The proposal's text was discarded.

TWO REPAIRS WERE TRIED AND MEASURED BEFORE THIS ONE, and both are recorded
because the reasoning is the evidence:

  1. REQUIRE THE WORD LAYER TO CORROBORATE A SUBJECT MATCH. Refuted by the
     suite: the subject tier exists to catch rewordings the word layer MISSES,
     so demanding its agreement is circular. The store fell from 4 of 4 to
     1 of 4 on the known rediscovery cases.
  2. REQUIRE A PARTIAL VOCABULARY OVERLAP. The 3 true rediscoveries score
     0.1429 to 0.2500 and the 2 genuinely-new items score 0.0000 to 0.1111, so
     a threshold in (0.1111, 0.1429) separates them -- a margin of 0.0318
     fitted to 5 data points. Refused as a tuned constant pretending to be a
     finding.

SO THE DECISION IS LEFT ALONE AND THE LOSS IS FIXED. `_distinct` already
provides the designed escape hatch: a caller naming a `task_ref` or `anchor`
the matched ticket does not own gets a separate ticket. The call that lost the
proposal simply omitted one. What was never acceptable is that omitting it
DISCARDED HIS WORDS, so the text is now recorded on the settled ticket.

THIS PATH IS REACHED OFTEN, NOT RARELY: 291 of 907 tickets, 32.0838% Wilson
[29.1269%, 35.1918%], carry neither a task_ref nor an anchor, and the
historical backfill will reach it for every item it raises. Measured by
scripts/can_a_shared_mechanism_hide_a_new_item_2026-10-17.py.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.ticket_store import TicketStore  # noqa: E402

SETTLED_TEXT = ("the routing ladder cannot climb past its first rung because "
                "the strength order is computed once and never revisited")
DIFFERENT_TEXT = ("the register should expose namespace paths so that issues "
                  "can be browsed as a tree rather than queried as a log")
SAME_FAULT_REWORDED = ("the strength order is computed once and never "
                       "revisited, so the routing ladder cannot climb past "
                       "its first rung")


@pytest.fixture
def store(tmp_path):
    s = TicketStore(path=tmp_path / "tickets.jsonl")
    s.load()
    t, outcome = s.propose("pf", "the ladder cannot climb", SETTLED_TEXT,
                           source="chat",
                           subjects=["season_strength_order", "area_of"])
    assert outcome == "created"
    s.close(t.tid, "fixed by recomputing the order each round",
            verification="bench/tests/test_the_ladder.py")
    return s, t


def test_an_absorbed_proposal_keeps_its_own_words(store):
    """THE DEFECT. The text was discarded entirely before this fix."""
    s, settled = store
    hit, outcome = s.propose("fr", "namespace paths", DIFFERENT_TEXT,
                             source="responses", subjects=["area_of"])
    assert outcome == "subject-settled"
    again = TicketStore(path=s.path)
    again.load()
    kept = again.get(settled.tid)
    assert kept is not None
    body = " ".join(kept.notes)
    assert "namespace paths" in body, (
        f"the absorbed proposal's TITLE is nowhere in the settled ticket's "
        f"notes, so nothing can later ask what was proposed: {kept.notes}")
    assert "browsed as a tree" in body, (
        f"the absorbed proposal's TEXT was discarded. His words are the one "
        f"thing this register exists to keep: {kept.notes}")
    assert "area_of" in body, (
        f"the note does not say which shared mechanism caused the absorption, "
        f"so a reader cannot judge whether it was right: {kept.notes}")


def test_the_absorbed_text_is_findable_by_word_search(store):
    """A note nobody can search for is barely better than a discarded one."""
    s, _ = store
    s.propose("fr", "namespace paths", DIFFERENT_TEXT, source="responses",
              subjects=["area_of"])
    again = TicketStore(path=s.path)
    again.load()
    # OPT-IN, because folding notes into the default search would invalidate
    # the measured operating characteristic the register's merge rule rests on.
    found = again.similar_by_words(DIFFERENT_TEXT, threshold=0.5,
                                   include_notes=True)
    assert found, (
        "the absorbed text cannot be found even with include_notes, so the "
        "record is write-only")
    # And the default must NOT find it, or the characteristic has moved.
    assert not again.similar_by_words(DIFFERENT_TEXT, threshold=0.5), (
        "the default word search now reaches notes, which changes the "
        "98.1132% / 86.3636% figures the merge rule is calibrated on")


def test_recording_the_text_twice_does_not_duplicate_the_note(store):
    """Idempotence: the parked-file generator wrote 28 marks for 14 items on
    this same day by failing exactly this property."""
    s, settled = store
    for _ in range(3):
        s.propose("fr", "namespace paths", DIFFERENT_TEXT, source="responses",
                  subjects=["area_of"])
    again = TicketStore(path=s.path)
    again.load()
    notes = again.get(settled.tid).notes
    absorbed = [n for n in notes if "browsed as a tree" in n]
    assert len(absorbed) == 1, (
        f"the same absorbed proposal was recorded {len(absorbed)} times")


def test_a_corroborated_repeat_is_still_caught(store):
    """THE DIRECTION NO REPAIR MAY LOSE. The subject tier exists because it
    would have caught the routing-ladder rediscovery; a reworded restatement
    of the same fault must still be recognised as settled."""
    s, settled = store
    hit, outcome = s.propose("pf", "ladder stuck on rung one",
                             SAME_FAULT_REWORDED, source="chat",
                             subjects=["season_strength_order"])
    assert outcome != "created", (
        "a reworded restatement of a settled fault was raised as new work, "
        "which is the rediscovery this register exists to prevent")
    assert hit.tid == settled.tid


def test_an_explicit_anchor_gets_its_own_ticket(store):
    """THE DESIGNED ESCAPE HATCH, which the losing call omitted. A caller that
    names a distinct identity is telling the register these are 2 items, and
    an explicit identifier beats an inferred similarity."""
    s, settled = store
    new, outcome = s.propose("fr", "namespace paths", DIFFERENT_TEXT,
                             source="responses", subjects=["area_of"],
                             anchor="design_brief.txt#namespace-paths#0")
    assert outcome == "created", (
        f"naming an anchor the settled ticket does not own still did not "
        f"produce a separate ticket (outcome {outcome!r}), so there is no way "
        f"to raise a genuinely new item that happens to touch a settled "
        f"mechanism")
    assert new.tid != settled.tid


def test_an_explicit_task_reference_also_gets_its_own_ticket(store):
    s, _ = store
    new, outcome = s.propose("pf", "a distinct task item", SETTLED_TEXT,
                             source="task_list", task_ref="Z9",
                             subjects=["season_strength_order"])
    assert outcome == "created"
    assert new.task_ref == "Z9"
