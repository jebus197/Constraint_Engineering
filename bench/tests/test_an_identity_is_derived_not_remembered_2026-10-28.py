#!/usr/bin/env python3
"""A ticket raised from chat carries an identity, and the count without one may
not grow.

HIS INSTRUCTION, 2026-10-28: fix the ticket store's over-matching and close the
ticket only if the fix is reliable. Kind-awareness and the chat anchor fix the
mechanism; THIS file is what makes the fix reliable rather than remembered.

THE EVIDENCE THAT IT IS NEEDED. On 2026-10-27 5 questions were raised by hand --
qs:524186098488, qs:08cf82f5081c, qs:f9a93f52b7d8, qs:c2e25a1e79c1 and
qs:92f807974742 -- and all 5 carry neither a `task_ref` nor an `anchor`. 4 were
then decided by the subject tier on 1 shared code identifier and had to be
re-raised with invented subjects. `_distinct` already provided the escape hatch.
It was documented and not used, which is a discipline failure, and this project's
record is that discipline failures recur until a mechanism catches them.

THE RATCHET. 317 of 2,858 tickets, 0.110917 Wilson [0.099922, 0.122956], carry no
identity as of 2026-10-28T02:10:18Z. That number may fall and may not rise. A
ratchet is the device `test_additive_standard_2026-09-07` already uses for config
fields no test reaches, so this is the existing instrument rather than a new one.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.ticket_store import TicketStore  # noqa: E402

#: Measured 2026-10-28T02:10:18+00:00. Lower is better; this may never rise.
IDENTITYLESS_CEILING = 317


def test_the_identityless_count_does_not_grow():
    s = TicketStore()
    s.load()
    bare = [t for t in s.all() if not t.task_ref and not t.anchor]
    assert len(bare) <= IDENTITYLESS_CEILING, (
        f"{len(bare)} tickets carry neither a task_ref nor an anchor, up from "
        f"the ceiling of {IDENTITYLESS_CEILING}. Every one of them can be "
        f"decided by the subject tier on a single shared identifier. Raise "
        f"chat items with TicketStore.propose_from_chat, which derives the "
        f"anchor, rather than calling propose by hand.\n"
        f"newest offenders: "
        f"{[(t.kind, t.tid[:12], t.title[:40]) for t in bare[-5:]]}")


def test_propose_from_chat_derives_an_anchor(tmp_path):
    """EXECUTED. The helper's whole purpose is that nothing must be remembered."""
    s = TicketStore(path=tmp_path / "t.jsonl")
    s.load()
    t, outcome = s.propose_from_chat(
        "qs", "a question raised in chat",
        "whether the chat half can capture an unmarked question at all",
        when="2026-10-28T02:10:00", subjects=["raises_a_marker"])
    assert outcome == "created"
    assert t.anchor, "no anchor was derived, so the helper adds nothing"
    assert t.anchor.startswith("chat#2026-10-28T02:10:00#")
    assert len(t.anchor.rsplit("#", 1)[1]) == 8, "the digest is not 8 hex"


def test_the_derived_anchor_escapes_the_subject_tier(tmp_path):
    """The property the anchor exists for, end to end through the helper."""
    s = TicketStore(path=tmp_path / "t.jsonl")
    s.load()
    a, _ = s.propose("pf", "the fix", "the gate reads a field no seat writes",
                     "chat", subjects=["_check_gamma_alt_convergence"])
    s.close(a.tid, "fixed", verification="test_two_sided_gate.py passed")
    _, o = s.propose_from_chat(
        "pf", "a different fault on the same gate",
        "the gate converges without consulting gamma when nothing is critical",
        when="2026-10-28T02:11:00",
        subjects=["_check_gamma_alt_convergence"])
    assert o == "created", (
        f"a derived anchor failed to escape the subject tier; got {o!r}, so "
        f"the helper does not deliver the property it exists for")


def test_the_same_item_twice_does_not_duplicate(tmp_path):
    """Idempotence: the anchor is content-and-time addressed, so re-raising the
    identical item at the identical moment must not make a 2nd ticket."""
    s = TicketStore(path=tmp_path / "t.jsonl")
    s.load()
    text = "the chat half cannot capture an unmarked question"
    first, o1 = s.propose_from_chat("qs", "q", text, when="2026-10-28T02:12:00")
    second, o2 = s.propose_from_chat("qs", "q", text, when="2026-10-28T02:12:00")
    assert o1 == "created"
    assert o2 == "exists", f"the same item raised twice gave {o2!r}"
    assert first.tid == second.tid
