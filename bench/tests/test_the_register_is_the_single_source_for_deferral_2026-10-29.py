#!/usr/bin/env python3
"""Deferral is the REGISTER's to state, and the task-list marker is derived from it.

HIS RULING, 2026-10-29, annotation 11 of
`Responses/Decisions_Awaiting_You_2026-10-29.txt`: *"I accept your recommendation.
fr"*, against: *"Make the register the single source and have the marker derived
from it, rather than the reverse. The register already refuses a terminal status
without a verification, so it is the stricter of the 2, and a derived marker
cannot drift from it."*

WHAT THE DISAGREEMENT WAS, MEASURED THE SAME DAY. The 2 representations were
independent: the markers called 2 entries DEFERRED (B20, C33) while the register
deferred 7 (B13, B20, B21, B22, C1, C21, C33). 5 live entries were therefore
deferred in one artefact and due in the other.

AND A SINGLE SOURCE THAT CANNOT BE CORRECTED IS WORSE THAN 2 THAT CAN, which is
why `TicketStore.undefer` was built in the same pass: 3 of the register's 7
deferrals were discharged by rulings he gave that same day and no operation could
say so.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.ticket_store import TicketStore  # noqa: E402

TLM = REPO / "scripts" / "task_list_markers.py"


def _tlm():
    spec = importlib.util.spec_from_file_location("task_list_markers_under_test", TLM)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["task_list_markers_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


tlm = _tlm()

#: THE MARKER MUST SIT ON THE LINE IMMEDIATELY AFTER THE HEADING. The first
#: version of this fixture put prose in between and every state parsed as None,
#: so 9 tests failed against correct code -- `parse_entries` reads `lines[i+1]`
#: and nothing else. The fixture was the defect, which is why each test that
#: depends on the marker asserts the marker's own value first.
LIST_TEXT = """# List

**Z1. An open entry that the register defers**
<!-- task: Z1 | state: OPEN | status: PROPOSED -->
Some prose about it.

**Z2. An entry the marker defers and the register does not**
<!-- task: Z2 | state: DEFERRED | status: PROPOSED -->
Some prose about it.

**Z3. A finished entry that the register also defers**
<!-- task: Z3 | state: DONE | status: COMMITTED | evidence: bench/tests/test_x.py -->
Some prose about it.

**Z4. An ordinary open entry**
<!-- task: Z4 | state: OPEN | status: BUILT -->
Some prose about it.
"""

WHEN = "2026-10-29T17:00:00+00:00"
REASON = "it waits on his ruling and blocks nothing on the list meanwhile"


@pytest.fixture()
def listing(tmp_path):
    p = tmp_path / "LIST.md"
    p.write_text(LIST_TEXT, encoding="utf-8")
    return p


@pytest.fixture()
def store(tmp_path):
    return TicketStore(path=tmp_path / "t.jsonl")


def _defer(store, ref, when=WHEN, reason=REASON):
    t, _ = store.propose("pf", f"a fault on {ref}", f"the verbatim text about {ref}",
                         source="chat", created="2026-10-29T16:00:00", task_ref=ref)
    return store.defer(t.tid, reason, when)


class TestTheRegisterOverridesTheMarker:
    def test_a_registered_deferral_makes_a_live_entry_deferred(self, listing, store):
        _defer(store, "Z1")
        defs = tlm.register_deferrals(store)
        entries = {e.ident: e for e in tlm.parse_entries(listing)}
        assert entries["Z1"].state == "OPEN", "the fixture no longer discriminates"
        assert tlm.effective_state(entries["Z1"], defs) == "DEFERRED"

    def test_an_entry_the_register_does_not_defer_keeps_its_marker(self, listing, store):
        _defer(store, "Z1")
        defs = tlm.register_deferrals(store)
        entries = {e.ident: e for e in tlm.parse_entries(listing)}
        assert tlm.effective_state(entries["Z4"], defs) == "OPEN"

    def test_a_terminal_marker_wins_over_a_deferral(self, listing, store):
        """NOT an exception to the ruling: a deferral says WHEN live work happens.

        An entry already DONE is not "deferred to the end of the list", and
        reporting it so would put closed work back in front of him.
        """
        _defer(store, "Z3")
        defs = tlm.register_deferrals(store)
        entries = {e.ident: e for e in tlm.parse_entries(listing)}
        assert tlm.effective_state(entries["Z3"], defs) == "DONE"

    def test_an_unavailable_register_falls_back_to_the_marker(self, listing):
        """The mapping is empty, so every entry reads exactly as it did before."""
        entries = tlm.parse_entries(listing)
        for e in entries:
            assert tlm.effective_state(e, {}) == e.state


class TestTheDisagreementIsReportedNotHidden:
    def test_both_directions_are_separated(self, listing, store):
        _defer(store, "Z1")
        dis = tlm.deferral_disagreements(listing, store)
        assert dis["register_only"] == ["Z1"]
        assert dis["marker_only"] == ["Z2"]

    def test_a_deferral_on_a_closed_entry_is_named(self, listing, store):
        _defer(store, "Z3")
        dis = tlm.deferral_disagreements(listing, store)
        assert dis["register_defers_a_closed_entry"] == ["Z3"]
        assert "Z3" not in dis["register_only"]

    def test_a_deferral_on_an_unknown_entry_is_named(self, listing, store):
        _defer(store, "ZZ99")
        dis = tlm.deferral_disagreements(listing, store)
        assert dis["register_defers_an_unknown_entry"] == ["ZZ99"]

    def test_the_checker_reports_the_drift(self, listing, store):
        #: STATES the deferrals rather than monkeypatching a module global.
        #: The first version patched `tlm.register_deferrals`, which made the
        #: test depend on HOW `check` obtained its data rather than on WHAT it
        #: does with it -- so a repair that changed the source silenced the test
        #: instead of failing it, and the full board of 2026-10-29 caught that.
        code, problems = tlm.check(listing,
                                   deferrals={"Z1": (WHEN, REASON)})
        joined = "\n".join(problems)
        assert "Z1 is deferred in the register" in joined
        assert "Z2 has marker state DEFERRED" in joined
        assert code != 0


class TestTheDerivationWritesOnlyOneDirection:
    def test_it_sets_a_marker_the_register_defers(self, listing, store):
        _defer(store, "Z1")
        n, changes = tlm.derive_deferred_markers(listing, apply=True, store=store)
        assert n == 1
        entries = {e.ident: e for e in tlm.parse_entries(listing)}
        assert entries["Z1"].state == "DEFERRED"

    def test_it_never_clears_a_marker_the_founder_wrote(self, listing, store):
        """Z2 says DEFERRED with the register silent. Erasing that would be
        destroying a statement of his, not deriving from a source."""
        _defer(store, "Z1")
        tlm.derive_deferred_markers(listing, apply=True, store=store)
        entries = {e.ident: e for e in tlm.parse_entries(listing)}
        assert entries["Z2"].state == "DEFERRED"
        _, changes = tlm.derive_deferred_markers(listing, apply=False, store=store)
        assert any("never auto-cleared" in c for c in changes)

    def test_a_dry_run_writes_nothing(self, listing, store):
        _defer(store, "Z1")
        before = listing.read_text(encoding="utf-8")
        n, _ = tlm.derive_deferred_markers(listing, apply=False, store=store)
        assert n == 1
        assert listing.read_text(encoding="utf-8") == before

    def test_the_derivation_leaves_other_fields_alone(self, listing, store):
        _defer(store, "Z1")
        tlm.derive_deferred_markers(listing, apply=True, store=store)
        entries = {e.ident: e for e in tlm.parse_entries(listing)}
        assert entries["Z1"].status == "PROPOSED"
        assert entries["Z3"].state == "DONE"
        assert entries["Z4"].state == "OPEN"


class TestUndeferIsTheSymmetricOperation:
    def test_it_clears_the_field_and_records_why(self, store):
        t = _defer(store, "Z1")
        assert t.deferred == WHEN
        cleared = store.undefer(t.tid, "his ruling of 2026-10-29 chose the term", WHEN)
        assert cleared.deferred == ""
        assert cleared.deferred_reason == ""
        assert any("undeferred" in n for n in cleared.notes)
        assert any(WHEN in n for n in cleared.notes)
        assert store.deferred_tickets() == []

    def test_it_refuses_without_a_reason(self, store):
        t = _defer(store, "Z1")
        with pytest.raises(ValueError, match="WHAT DISCHARGED"):
            store.undefer(t.tid, "done", WHEN)

    def test_it_refuses_without_a_clock_reading(self, store):
        t = _defer(store, "Z1")
        with pytest.raises(ValueError, match="never reads a clock"):
            store.undefer(t.tid, "his ruling of 2026-10-29 chose the term", "  ")

    def test_it_refuses_a_ticket_that_is_not_deferred(self, store):
        t, _ = store.propose("pf", "not deferred", "the text of an undeferred item",
                             source="chat", created="2026-10-29T16:00:00", task_ref="Z4")
        with pytest.raises(ValueError, match="nothing to clear"):
            store.undefer(t.tid, "his ruling of 2026-10-29 chose the term", WHEN)

    def test_it_refuses_an_unknown_ticket(self, store):
        with pytest.raises(KeyError):
            store.undefer("ffffffffffff", "his ruling of 2026-10-29 chose it", WHEN)
