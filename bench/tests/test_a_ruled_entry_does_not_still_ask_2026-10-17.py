"""An entry recording his ruling may not still ask him to rule.

THE DEFECT CAME BACK ONE LEVEL UP. The `ruled:` marker field was added on
2026-10-16 because the zero-plant control was ruled *"restart it"* on 2026-08-07
and again on 2026-09-06, and 70 days later it was still listed under decisions
that needed him: nothing could express "he has already decided this". The field
fixed the REPORT GENERATOR. It did not fix the ENTRY. A marker records the DATE
he ruled, while the entry's prose still carries whatever question was put to
him, and nothing reconciles the two.

SO A READER TAKES THE PROSE AT ITS WORD AND ASKS AGAIN. That happened on
2026-10-17 with task B12: its 3 options were put to him in a brief, he answered
on 2026-10-16 by rejecting all 3 and naming a fourth -- *"Surely all of those
options still bound models on an arbitrary limit, rather than dynamically in the
first blind round of any given experiment"* -- and because B12's text still read
"NEEDS HIS RULING", the settled question was re-presented to him as open.

MEASURED by `scripts/does_a_ruled_entry_still_ask_for_a_ruling_2026-10-17.py`:
of 151 entries, 45 carry a `ruled:` date and **11 of those 45 still ask --
24.4444%, Wilson [14.2355%, 38.6734%], Clopper-Pearson [12.8823%, 39.5371%]**.
3 of the 11 are marked DONE, so the prose outlived the work as well.

A SET IS PINNED, NOT A TOTAL. A total of 11 cannot distinguish reconciling one
entry and spoiling another from making no change at all, and the project has
already paid for that: a swap of 2 items in and 2 out reads as agreement when
only the total is compared. Reconciling an entry means REMOVING it from `STILL_ASKING` here, which is
the only direction this list is meant to move.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = (REPO / "scripts"
            / "does_a_ruled_entry_still_ask_for_a_ruling_2026-10-17.py")

#: The entries that carried a ruling date AND still asked, as measured on
#: 2026-10-17. Reconciling one means deleting it from here. NOTHING may be
#: added without saying in the task list why a ruled entry still asks.
STILL_ASKING: set[str] = set()
#: ALL RECONCILED 2026-10-17, so the pin is empty and any new member is a
#: regression rather than a backlog item:
#:   B12 -- his 2026-10-16 ruling rejected all 3 options put to him and named a
#:     fourth, and the entry now records WHAT he ruled.
#:   B6 -- its remaining question was the same design decision B12 settled, and
#:     the entry now says so and points at it.
#:   B11 -- he ruled (b) verbatim on 2026-10-16, and the entry now carries that
#:     ruling while naming (c) as the one question still open.
#:   B20 -- it said placement needed his ruling while quoting that ruling 2
#:     paragraphs above its own request for it.
#:
#: AND THE CHECK ITSELF WAS NARROWED, which reduced 11 to 2 before those 2 were
#: reconciled. The first version flagged every ruled entry that asked, and B11
#: showed that is too strong: an entry with 2 questions can be ruled on one and
#: open on the other, so it legitimately carries a ruling date AND asks. The
#: defect is narrower -- an entry that asks while recording NO ruling at all, so
#: a reader cannot tell a settled question from an open one. The stricter
#: measurement is still reported by the producer as "asks at all", and was 10
#: when this was written.
#:
#: A LESSON FROM DOING THE FIRST ONE. Reconciling B12 tripped this detector
#: TWICE on its own correction: once because the correction QUOTED the phrase
#: it was retiring, and once because an earlier addition of the same day had
#: itself said the choice was his. A phrase-based detector cannot tell a
#: question from a quotation of one, so a reconciliation must RETIRE the
#: wording rather than discuss it.


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location("ruled_probe", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ruled_probe"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_no_new_entry_records_a_ruling_while_still_asking(producer):
    """THE RATCHET. A new one is a settled question put to him again."""
    bad, _, _ = producer.still_asking()
    found = {e.ident for e in bad}
    added = sorted(found - STILL_ASKING)
    assert not added, (
        "these entries record a `ruled:` date and their own text still asks him "
        "to rule, which is how a settled question gets re-presented as open: "
        + ", ".join(added)
        + ". Carry WHAT he ruled into the entry, read from "
          "scripts/read_founder_responses_2026-10-11.py and never from a "
          "recollection, then remove it from STILL_ASKING in this test.")


def test_the_pinned_set_does_not_claim_more_than_is_true(producer):
    """An entry reconciled must be removed from the pin, or the pin lies.

    Without this the list could keep naming entries that were fixed long ago,
    and the next reader would believe 11 are outstanding when 2 are. It fails
    LOUDLY on progress, which is the correct direction for a ratchet to be
    noisy in.
    """
    bad, _, _ = producer.still_asking()
    found = {e.ident for e in bad}
    stale = sorted(STILL_ASKING - found)
    assert not stale, (
        "these entries no longer ask for a ruling they already have, so remove "
        "them from STILL_ASKING: " + ", ".join(stale))


def test_the_detector_can_still_see_a_defect(producer, monkeypatch):
    """ANTI-VACUITY, asserted on a SYNTHETIC entry rather than on the live data.

    THE FIRST VERSION ASSERTED `bad` WAS NON-EMPTY, which tied the anti-vacuity
    check to the defect still existing: reconciling the last entry turned it red
    and the test punished the fix. A guard that fails when its subject is
    repaired cannot distinguish a working detector from a clean task list.

    So a known-bad entry is injected -- `ruled:` set, asking, recording no
    ruling -- and the detector must find it. That holds whether the real list
    has 0 such entries or 11.
    """
    assert len(producer.ASKS_FOR_A_RULING) >= 5
    assert "NEEDS HIS RULING" in producer.ASKS_FOR_A_RULING
    assert len(producer.RECORDS_A_RULING) >= 5

    bodies = dict(producer.entry_bodies())
    bodies["ZZ9"] = ("**ZZ9. A synthetic entry for the anti-vacuity check.** "
                     "**NEEDS HIS RULING** on something or other.")
    monkeypatch.setattr(producer, "entry_bodies", lambda: bodies)

    class _E:
        def __init__(self, ident):
            self.ident, self.ruled, self.state = ident, "2026-01-01", "OPEN"

    import types
    fake = types.SimpleNamespace(parse_entries=lambda _p: [_E("ZZ9")])
    monkeypatch.setitem(sys.modules, "task_list_markers", fake)
    bad, n_ruled, _ = producer.still_asking()
    assert {e.ident for e in bad} == {"ZZ9"}, (
        "the detector missed a planted entry that is ruled, asks, and records "
        "no ruling -- so a real one would pass too")
    assert n_ruled == 1


def test_the_live_task_list_parses_at_all(producer):
    """Separate from anti-vacuity: the fixture must not be empty.

    If the task list stopped parsing, every assertion above would pass on 0
    entries and report a clean board. This is the one that would notice.
    """
    _, n_ruled, n_all = producer.still_asking()
    assert n_all > 100, f"only {n_all} entries parsed; the list did not load"
    assert n_ruled > 10, f"only {n_ruled} carry a ruling date"
