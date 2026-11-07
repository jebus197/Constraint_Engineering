"""`restate` and `retitle` refused 77% of the register by omitting the anchor.

`tid_of`'s precedence is `task_ref`, then `anchor`, then the content. Both
`TicketStore.restate` and `TicketStore.retitle` recomputed the identity as
`tid_of(kind, text, task_ref)` -- WITHOUT the anchor -- so any ticket addressed
by an anchor fell through to CONTENT addressing, the recomputed digest differed
from the stored identity, and the safety check fired on an operation that was
perfectly safe.

MEASURED 2026-11-07 over the live store: 3,422 tickets, of which 453 are
`task_ref`-addressed, 319 content-addressed, and **2,650 anchor-addressed** --
every ticket raised from his annotations or from chat, because those carry an
anchor and no task reference. For **2,643 of those 2,650**, 0.997358, Wilson 95%
[0.994557, 0.998720], Clopper-Pearson [0.994565, 0.998937],
`tid_of(kind, new_text, task_ref, anchor)` equals the stored tid while
`tid_of(kind, new_text, task_ref)` does not. So the guard was wrong about the
identity in 0.997358 of the cases it was asked about.

WHY THE EXISTING MUTATION HARNESS DID NOT CATCH IT, which is the part worth
keeping. The comment above the check records it being hardened by mutation after
a vacuous form was found -- the first version compared a COPIED field, which
could never fail. That hardening was real and it was incomplete: the harness
exercised the `task_ref` path only, so the omitted `anchor` survived a mutation
suite written to catch exactly this class. A probe that covers 1 of 3 precedence
branches cannot speak for the other 2.

THE CHECK IS NOT WEAKENED BY THE REPAIR, and that is what the discrimination
tests below exist to show: a content-addressed ticket has neither a reference
nor an anchor, so its digest still moves with its text and both methods still
refuse it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
STORE_PY = REPO / "bench" / "ticket_store.py"


def _mod():
    spec = importlib.util.spec_from_file_location("ticket_store", STORE_PY)
    m = importlib.util.module_from_spec(spec)
    sys.modules["ticket_store"] = m          # dataclass needs the module registered
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def ts():
    return _mod()


@pytest.fixture()
def store(ts, tmp_path, monkeypatch):
    """A store in a temp directory, so no test writes the live register."""
    st = ts.TicketStore(tmp_path / "tickets.jsonl") \
        if _takes_path(ts.TicketStore) else ts.TicketStore()
    if not _takes_path(ts.TicketStore):
        pytest.skip("TicketStore does not accept a path; refusing to touch the live store")
    return st


def _takes_path(cls) -> bool:
    import inspect
    try:
        return len(inspect.signature(cls.__init__).parameters) > 1
    except (TypeError, ValueError):
        return False


class TestTheIdentityFunctionItself:
    """The precedence, asked of `tid_of` directly. No store involved."""

    def test_an_anchor_addressed_identity_is_stable_under_a_reword(self, ts):
        a = ts.tid_of("pf", "the original wording", "", "chat#T#deadbeef")
        b = ts.tid_of("pf", "a completely different wording", "", "chat#T#deadbeef")
        assert a == b, (
            "an anchor must fix the identity regardless of the text; if this "
            "fails, `tid_of`'s precedence has changed and both call sites in "
            "restate/retitle need re-reading")

    def test_omitting_the_anchor_changes_the_answer(self, ts):
        """THE DEFECT, in 1 assertion."""
        with_anchor = ts.tid_of("pf", "new text", "", "chat#T#deadbeef")
        without = ts.tid_of("pf", "new text", "")
        assert with_anchor != without, (
            "if these agree the precedence no longer distinguishes an anchor, "
            "and the repair below is no longer load-bearing")

    def test_a_content_addressed_identity_still_moves_with_its_text(self, ts):
        a = ts.tid_of("pf", "the original wording", "", "")
        b = ts.tid_of("pf", "a different wording", "", "")
        assert a != b, (
            "content addressing must remain text-sensitive, or the refusal in "
            "restate becomes vacuous for the tickets it correctly protects")

    def test_a_task_reference_outranks_an_anchor(self, ts):
        a = ts.tid_of("pf", "text one", "B99", "chat#T#aaaaaaaa")
        b = ts.tid_of("pf", "text two", "B99", "chat#T#bbbbbbbb")
        assert a == b, "a task reference must be the whole identity when present"


class TestRestateAcceptsAnAnchoredTicket:
    def test_an_anchored_ticket_can_be_restated_and_keeps_its_id(self, ts, store):
        t, outcome = store.propose_from_chat(
            "pf", "a title", "the original wording", "2026-11-07T00:00:00+00:00")
        assert outcome == "created"
        assert t.anchor and not t.task_ref, "the fixture must be anchor-addressed"
        nt = store.restate(t.tid, "a materially different wording", "a verification")
        assert nt.tid == t.tid, (
            "the identity moved, which would orphan every citation of the old id")
        assert nt.verbatim == "a materially different wording"

    def test_an_anchored_ticket_can_be_retitled_and_keeps_its_id(self, ts, store):
        t, _ = store.propose_from_chat(
            "pf", "the first title", "some wording", "2026-11-07T00:00:01+00:00")
        nt = store.retitle(t.tid, "a corrected title")
        assert nt.tid == t.tid
        assert nt.title and nt.title != t.title

    def test_a_task_referenced_ticket_still_works(self, ts, store):
        """The branch the original harness did cover; it must not regress."""
        t, _ = store.propose("pf", "a title", "wording", "code", task_ref="B99")
        nt = store.restate(t.tid, "different wording", "a verification")
        assert nt.tid == t.tid


class TestTheRefusalStillFiresWhereItShould:
    """THE DISCRIMINATION. A guard that accepts everything is as useless as one
    that accepts nothing, and the repair must not have bought acceptance by
    removing the check."""

    def test_a_content_addressed_ticket_is_still_refused(self, ts, store):
        t, _ = store.propose("pf", "a title", "the original wording", "code")
        assert not t.task_ref and not t.anchor, "the fixture must be content-addressed"
        with pytest.raises(AssertionError) as e:
            store.restate(t.tid, "a completely different wording", "a verification")
        assert "identity" in str(e.value).lower()

    def test_a_restatement_still_needs_a_verification(self, ts, store):
        t, _ = store.propose_from_chat(
            "pf", "a title", "wording", "2026-11-07T00:00:02+00:00")
        with pytest.raises(ValueError):
            store.restate(t.tid, "new wording", "   ")

    def test_a_restatement_still_refuses_to_blank_the_text(self, ts, store):
        t, _ = store.propose_from_chat(
            "pf", "a title", "wording", "2026-11-07T00:00:03+00:00")
        with pytest.raises(ValueError):
            store.restate(t.tid, "   ", "a verification")

    def test_an_unknown_tid_still_raises(self, ts, store):
        with pytest.raises(KeyError):
            store.restate("0" * 12, "anything", "a verification")


class TestBothCallSitesPassTheAnchor:
    """Asked of the PARSED module, not of its text, so a comment mentioning
    `anchor` cannot satisfy it -- the mention-versus-use fault this project has
    recorded twice today."""

    def test_neither_restate_nor_retitle_omits_the_anchor(self):
        import ast
        tree = ast.parse(STORE_PY.read_text(encoding="utf-8"))
        bad = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name not in ("restate", "retitle"):
                continue
            for c in ast.walk(node):
                if not isinstance(c, ast.Call):
                    continue
                nm = getattr(c.func, "id", None) or getattr(c.func, "attr", None)
                if nm != "tid_of":
                    continue
                if len(c.args) + len(c.keywords) < 4:
                    bad.append(f"{node.name}: tid_of called with "
                               f"{len(c.args) + len(c.keywords)} argument(s)")
        assert not bad, (
            f"a tid_of call in restate/retitle does not reach the anchor "
            f"argument, so the identity question is being asked of the wrong "
            f"precedence branch again: {bad}")
