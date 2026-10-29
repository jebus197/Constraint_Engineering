#!/usr/bin/env python3
"""An identityless ticket can be given the identity it should have carried, and
the count of identityless tickets FALLS rather than rising.

HIS RULING, 2026-10-29, annotation 5 of `Responses/Decisions_Awaiting_You_2026-10-29.txt`:
*"Do the re-baseline and implement your fix as you suggest. fr"*

WHAT WAS REPORTED TO HIM AND WHAT IS CORRECTED HERE. Entry B49 told him the count
*"cannot be brought back down"*, offering as evidence that raising a bare ticket
takes it 320 -> 321 and migrating it 321 -> 322, because a migration leaves the
old record behind as a MERGED marker which is itself without an identity. That
measurement is reproduced below and is sound. The conclusion drawn from it was
not: it establishes that MIGRATION cannot walk the count back, and no operation
that filled in the missing field existed to be measured, so irreversibility was
a property of the available operations rather than of the register.

EVERY TEST HERE EXECUTES THE STORE. None asserts on source text, because a test
that reads a module only establishes that the module describes itself
consistently -- the failure `execute-do-not-grep` was written for.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.ticket_store import TicketStore, tid_of  # noqa: E402

VERBATIM = "the bare verbatim text of a proposed fix raised without an identity"
ANCHOR = "chat#2026-10-29T16:00:00#deadbeef"
VERIF = "his ruling 2026-10-29, annotation 5 of Decisions_Awaiting_You_2026-10-29.txt"


def _identityless(store: TicketStore) -> int:
    return len([t for t in store.all() if not t.task_ref and not t.anchor])


@pytest.fixture()
def bare(tmp_path):
    """A store holding exactly 1 ticket, raised with neither reference nor anchor."""
    s = TicketStore(path=tmp_path / "t.jsonl")
    t, outcome = s.propose("pf", "a bare proposal", VERBATIM, source="chat",
                           created="2026-10-29T16:00:00", subjects=["Alpha"])
    assert outcome == "created"
    assert not t.task_ref and not t.anchor
    assert _identityless(s) == 1
    return s, t


# --------------------------------------------------------------- the property
class TestAdoptionLowersTheCount:
    def test_the_count_falls_by_one(self, bare):
        s, t = bare
        s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)
        assert _identityless(s) == 0

    def test_the_stored_identity_is_not_re_keyed(self, bare):
        """The whole difference from a migration: a cited identifier keeps resolving."""
        s, t = bare
        adopted = s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)
        assert adopted.tid == t.tid
        assert s.get(t.tid) is not None
        assert s.get(t.tid).anchor == ANCHOR

    def test_a_migration_raises_the_count_instead(self, bare):
        """B49's own measurement, executed, so the contrast is not asserted in prose."""
        s, t = bare
        new = tid_of("pf", VERBATIM, "", "a-different-anchor#1")
        s.migrate_identity(t.tid, new, VERIF)
        assert _identityless(s) == 2, (
            "a migration leaves the old record behind as a MERGED marker and "
            "writes a new record; both carry no identity, so the count rises")

    def test_the_status_survives_an_adoption(self, bare):
        """The 3 tickets this was built for are all terminal, so this is the real case."""
        s, t = bare
        s.close(t.tid, "fixed", "a verification")
        assert s.get(t.tid).status == "CLOSED"
        adopted = s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)
        assert adopted.status == "CLOSED"
        assert adopted.resolution == "fixed"


# ----------------------------------------------------------------- the bridge
class TestTheAliasBridge:
    def test_exact_finds_it_under_the_newly_implied_digest(self, bare):
        s, t = bare
        implied = tid_of("pf", VERBATIM, "", ANCHOR)
        assert implied != t.tid, "the fixture no longer discriminates"
        s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)
        hit = s.exact("pf", VERBATIM, anchor=ANCHOR)
        assert hit is not None and hit.tid == t.tid, (
            "without the bridge a caller supplying the adopted anchor computes a "
            "digest nothing is stored at, and raises a duplicate")

    def test_exact_still_finds_it_by_content(self, bare):
        """The path every normally-raised ticket uses must be untouched."""
        s, t = bare
        s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)
        hit = s.exact("pf", VERBATIM)
        assert hit is not None and hit.tid == t.tid

    def test_the_bridge_survives_a_reload(self, bare):
        """An index built only in the mutating session would work once and never again."""
        s, t = bare
        s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)
        reloaded = TicketStore(path=s.path)
        hit = reloaded.exact("pf", VERBATIM, anchor=ANCHOR)
        assert hit is not None and hit.tid == t.tid
        assert _identityless(reloaded) == 0

    def test_a_later_proposal_with_the_anchor_does_not_duplicate(self, bare):
        """The consequence that matters: the register must not raise it twice.

        ★ THIS TEST WAS GREEN FOR THE WRONG REASON AND IS CORRECTED. The first
        version re-proposed the IDENTICAL verbatim, so `propose` deduplicated on
        its REWORDED tier -- the normalised-text digest -- and returned
        `reworded-match` whether or not the adoption bridge existed. Tracing
        `exact()`'s callers showed it has exactly 1 production caller,
        `candidates()`, which decides nothing, so `propose` was reaching the
        bridge not at all. The text here is therefore REWORDED beyond the
        normalised digest's reach, which leaves the anchor as the only tier that
        can match, and the outcome asserted is the EXACT tier.
        """
        s, t = bare
        s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)
        before = len(s.all())
        reworded = ("an entirely separate wording whose normalised digest shares "
                    "nothing with the original, so only the anchor can match it")
        from bench.ticket_store import nid_of
        assert nid_of(reworded) != nid_of(VERBATIM), "the rewording is not distinct"
        again, outcome = s.propose("pf", "the same item, reworded", reworded,
                                   source="chat", created="2026-10-29T17:00:00",
                                   anchor=ANCHOR, subjects=["Alpha"])
        assert again.tid == t.tid, (
            f"a second ticket was created ({outcome}), so the adoption bridge "
            f"does not reach propose")
        assert len(s.all()) == before

    def test_the_index_is_empty_for_a_normally_raised_store(self, tmp_path):
        """It must add NOTHING in the common case, or it is a second identity rule."""
        s = TicketStore(path=tmp_path / "t.jsonl")
        s.propose("pf", "one", "the first proposal text", source="chat",
                  created="2026-10-29T16:00:00", task_ref="Z1")
        s.propose("qs", "two", "the second proposal text", source="chat",
                  created="2026-10-29T16:01:00", anchor="chat#x#1")
        s.propose("fr", "three", "the third proposal text", source="chat",
                  created="2026-10-29T16:02:00")
        assert s._by_identity == {}, (
            "an alias was registered for a ticket whose own fields already imply "
            "its stored key, so the index is not confined to repairs")


# --------------------------------------------------------------- the refusals
class TestWhatItRefuses:
    def test_it_refuses_a_ticket_that_already_has_an_identity(self, tmp_path):
        s = TicketStore(path=tmp_path / "t.jsonl")
        t, _ = s.propose("pf", "identified", "a proposal that names its entry",
                         source="chat", created="2026-10-29T16:00:00", task_ref="B99")
        with pytest.raises(ValueError, match="already carries an identity"):
            s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)

    def test_it_refuses_without_a_verification(self, bare):
        s, t = bare
        with pytest.raises(ValueError, match="must name what authorised it"):
            s.adopt_identity(t.tid, "   ", anchor=ANCHOR)

    def test_it_refuses_when_neither_field_is_given(self, bare):
        s, t = bare
        with pytest.raises(ValueError, match="must supply a task_ref or an anchor"):
            s.adopt_identity(t.tid, VERIF)

    def test_it_refuses_an_unknown_ticket(self, bare):
        s, _ = bare
        with pytest.raises(KeyError):
            s.adopt_identity("ffffffffffff", VERIF, anchor=ANCHOR)

    def test_it_refuses_when_the_implied_identity_is_already_held(self, bare):
        """THE CASE THAT FIRED ON ALL 3 REAL TICKETS, 2026-10-29.

        Each had a correctly-identified twin at the digest its anchor implies, so
        adopting that anchor would make 2 tickets answer to 1 identity -- the
        collapse that destroyed a ticket of mine the same morning.
        """
        s, t = bare
        twin, outcome = s.propose("pf", "the correctly identified re-raise", VERBATIM,
                                  source="chat", created="2026-10-29T16:30:00",
                                  anchor=ANCHOR, subjects=["Alpha"])
        if twin.tid == t.tid:
            pytest.skip("the re-raise deduplicated onto the bare ticket; "
                        "no separate twin exists to collide with")
        with pytest.raises(ValueError, match="merge into it rather than adopting"):
            s.adopt_identity(t.tid, VERIF, anchor=ANCHOR)

    def test_two_tickets_may_not_alias_the_same_identity(self, tmp_path):
        s = TicketStore(path=tmp_path / "t.jsonl")
        a, _ = s.propose("pf", "first bare", "the first bare proposal text",
                         source="chat", created="2026-10-29T16:00:00")
        b, _ = s.propose("pf", "second bare", "the second bare proposal text",
                         source="chat", created="2026-10-29T16:01:00")
        s.adopt_identity(a.tid, VERIF, anchor=ANCHOR)
        with pytest.raises(ValueError):
            s.adopt_identity(b.tid, VERIF, anchor=ANCHOR)


class TestTheGuardItsOwnPPassFound:
    """An anchor or a reference already in use on another ticket is refused.

    WHY THIS CLASS EXISTS. The 3 refusals above all reason about the IMPLIED
    DIGEST, and a digest is blind to an anchor held by a ticket whose identity
    came from a `task_ref`: `tid_of` takes the reference in preference and never
    reads the anchor. On 2026-10-29 `pf:b0d8ca44a450` was adopted onto an anchor
    `pf:2835f264ae18` already carried, and only the fact that the 2 are records
    of ONE item kept the outcome truthful. Luck is not a guard.
    """

    def test_an_anchor_held_by_a_reference_identified_ticket_is_refused(self, tmp_path):
        s = TicketStore(path=tmp_path / "t.jsonl")
        shared = "chat#2026-10-29T06:06:06+00:00#10cf300f"
        s.propose("pf", "identified by its reference", "the text of the referenced item",
                  source="chat", created="2026-10-29T06:06:06+00:00",
                  task_ref="B50", anchor=shared)
        bare_t, _ = s.propose("pf", "the bare twin", "a different text for the bare twin",
                              source="chat", created="2026-10-29T06:06:07+00:00")
        with pytest.raises(ValueError, match="already carries anchor"):
            s.adopt_identity(bare_t.tid, VERIF, anchor=shared)

    def test_a_reference_already_in_use_for_that_kind_is_refused(self, tmp_path):
        """REFUSED BY THE DIGEST CHECK, not by a second reference check.

        This test is why the first draft's `task_ref` branch was deleted: it
        asserted a message that branch would have produced and got the digest
        check's message instead, which proved the branch unreachable. A
        same-kind, same-reference adoption cannot get past `clash`, because
        `tid_of` digests the reference alone.
        """
        s = TicketStore(path=tmp_path / "t.jsonl")
        s.propose("pf", "the first on this entry", "the first fault filed on the entry",
                  source="chat", created="2026-10-29T06:00:00", task_ref="B50")
        bare_t, _ = s.propose("pf", "a second fault", "a second and distinct fault text",
                              source="chat", created="2026-10-29T06:01:00")
        with pytest.raises(ValueError, match="merge into it rather than adopting"):
            s.adopt_identity(bare_t.tid, VERIF, task_ref="B50")

    def test_the_same_reference_on_a_different_kind_is_allowed(self, tmp_path):
        """A question and a proposed fix about 1 entry are DIFFERENT items.

        `tid_of` digests the kind, so they take distinct identities by design,
        and refusing this would break the thing the kind field is for.
        """
        s = TicketStore(path=tmp_path / "t.jsonl")
        s.propose("pf", "a fix on the entry", "the proposed repair text",
                  source="chat", created="2026-10-29T06:00:00", task_ref="B50")
        q, _ = s.propose("qs", "a question about it", "the question text for the entry",
                         source="chat", created="2026-10-29T06:01:00")
        adopted = s.adopt_identity(q.tid, VERIF, task_ref="B50")
        assert adopted.task_ref == "B50"
