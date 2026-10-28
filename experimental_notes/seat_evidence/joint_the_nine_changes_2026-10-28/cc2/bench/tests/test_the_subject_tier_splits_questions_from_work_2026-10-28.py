# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_nine_changes_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 50d1c5e7498e540c6e5116f7caa59afcee25832c57a3568003b135608a98f8c8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The subject tier's kind predicate: his ruling, and only as far as it reaches.

WHAT THIS PINS. On 2026-10-28 the subject tier was changed from "any settled
ticket on this subject blocks" to "only a settled ticket OF THE SAME KIND
blocks". The joint panel round of the same day measured the change and found
two things the shipped form did not survive:

  1. It ADMITS a cross-kind duplicate. A settled `pf` stopped blocking the same
     item re-raised as an `fr`. His 2026-10-19 ruling turns on resolutions that
     travel in OPPOSITE directions -- "he answers mine, I answer his" -- which is
     true of a question against a work item and false of `fr` against `pf`: both
     are discharged by implementing the mechanism.

  2. Its stated benefit is not in the realised data. Over the live store of
     2,879 tickets, every realised cross-kind suppression is `qs` blocked by
     `pf`. There is no realised fr<-pf, pf<-wr or any other cross pair. So the
     general form and the question/work split recover the SAME single item and
     the set difference is empty, while the general form alone opens the door in
     (1).

So the predicate is `(b.kind == "qs") == (kind == "qs")`: a question is a
distinct item from work on the same subject, and work items of any kind still
block each other. These tests execute all three behaviours rather than reading
the source for them.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SUBS = ["propose", "subject_tier"]


def _fresh():
    spec = importlib.util.spec_from_file_location(
        "ts_qw", REPO / "bench" / "ticket_store.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ts_qw"] = mod
    spec.loader.exec_module(mod)
    return mod


def _store_with_a_settled_pf():
    ts = _fresh()
    st = ts.TicketStore(pathlib.Path(tempfile.mkdtemp()) / "t.jsonl")
    t, _ = st.propose(
        "pf", "settled fix",
        "The subject tier blocks a proposal that shares one identifier.",
        "chat", subjects=SUBS)
    st.close(t.tid, "done", "verified by this test")
    return st


def test_a_settled_work_item_still_blocks_the_same_item_as_another_work_kind():
    """The defect the general form admitted. fr, pf and wr are one item seen
    from three sides; their resolutions travel the SAME direction."""
    st = _store_with_a_settled_pf()
    _, verdict = st.propose(
        "fr", "same item as a request",
        "Add handling so the subject tier does not block a proposal sharing "
        "one identifier.", "chat", subjects=SUBS)
    assert verdict == "subject-settled", (
        f"a settled pf must still block the same item re-raised as an fr; "
        f"got {verdict!r}")


def test_a_question_is_a_distinct_item_from_settled_work():
    """His ruling of 2026-10-19, which is what the predicate implements."""
    st = _store_with_a_settled_pf()
    _, verdict = st.propose(
        "qs", "a question on the same subject",
        "Does the subject tier still block a proposal that shares one "
        "identifier?", "chat", subjects=SUBS)
    assert verdict == "created", (
        f"a settled pf has no standing to settle a new qs; got {verdict!r}")


def test_a_settled_question_still_blocks_a_rewording_of_itself():
    """The anti-vacuity guard: the split must not disable the tier for qs."""
    st = _fresh().TicketStore(pathlib.Path(tempfile.mkdtemp()) / "t.jsonl")
    t, _ = st.propose(
        "qs", "a question", "Does the subject tier block on one identifier?",
        "chat", subjects=SUBS)
    st.close(t.tid, "answered", "verified by this test")
    _, verdict = st.propose(
        "qs", "the same question reworded",
        "Is a proposal blocked by the subject tier when it shares a single "
        "identifier?", "chat", subjects=SUBS)
    assert verdict == "subject-settled", (
        f"a settled qs must still block its own rewording; got {verdict!r}")


def test_a_settled_work_item_still_blocks_its_own_rewording():
    st = _store_with_a_settled_pf()
    _, verdict = st.propose(
        "pf", "reworded same kind",
        "The subject tier blocks proposals which share a single identifier.",
        "chat", subjects=SUBS)
    assert verdict == "subject-settled", verdict


def test_the_split_recovers_exactly_what_the_general_form_recovers():
    """The dominance claim, as a count on the live store rather than a view.

    Replays the live store's own anchorless proposals under three predicates and
    asserts the question/work split recovers the SAME items as `b.kind == kind`.
    If the store ever grows a realised cross-kind suppression that is not qs<-pf,
    this test fails and the narrowing must be re-argued -- which is the point.
    """
    ts = _fresh()
    hv_spec = importlib.util.spec_from_file_location(
        "ticket_harvester", REPO / "scripts" / "harvest_tickets_2026-10-17.py")
    hv = importlib.util.module_from_spec(hv_spec)
    sys.modules["ticket_harvester"] = hv
    hv_spec.loader.exec_module(hv)

    store = ts.TicketStore()
    store.load()
    if not store.all():
        pytest.skip("no live store in this tree")

    def settled(t):
        return t.status in ts.TERMINAL or t.status == ts.REJECTED

    def blocks(policy, prop_kind, b_kind):
        if policy == "pre":
            return True
        if policy == "general":
            return b_kind == prop_kind
        return (b_kind == "qs") == (prop_kind == "qs")

    def replay(policy):
        out = {}
        for t in store.all():
            if t.task_ref or t.anchor:
                continue
            subs = t.subjects or hv.subjects_in(t.verbatim or t.title or "")
            if not subs:
                continue
            hit = False
            for sub in subs:
                if [b for b in store.by_subject(sub)
                        if settled(b) and b.tid != t.tid
                        and blocks(policy, t.kind, b.kind)]:
                    hit = True
                    break
            out[t.tid] = hit
        return out

    pre, gen, nar = replay("pre"), replay("general"), replay("split")
    rec_gen = {k for k in pre if pre[k] and not gen[k]}
    rec_nar = {k for k in pre if pre[k] and not nar[k]}
    assert rec_gen == rec_nar, (
        "the question/work split and `b.kind == kind` no longer recover the "
        f"same items: only-general={sorted(rec_gen - rec_nar)}, "
        f"only-split={sorted(rec_nar - rec_gen)}")
