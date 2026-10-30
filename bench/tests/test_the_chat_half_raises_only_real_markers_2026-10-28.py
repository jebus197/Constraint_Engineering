#!/usr/bin/env python3
r"""The chat half of the harvester: reachable, and not a channel for its own echo.

HIS INSTRUCTION, 2026-10-28: fix the ticket store's over-matching, and close the
ticket only if the fix is reliable. The root cause was that `from_chat` passed no
anchor, so every chat-sourced proposal reached the subject tier with no identity.
Repairing that exposed that `from_chat` returned 0 rows for every window back to
2026-08-01, because its fast prefilter required a leading double quote and knew
only 2 of the 4 KINDS.

WHAT THIS FILE HOLDS, each property with the mutation that turns it red:

  1. The prefilter IS `MARKER`, so it cannot be narrower than the decision.
     Mutation: restore `r'"(fr|pf)[:\]]'` -> the reachability test fails.
  2. Every chat row carries an anchor, and anchors are distinct.
     Mutation: drop `anchor` from the emitted dict -> fails.
  3. An anchor escapes the subject tier, which is the whole point of 2.
     Mutation: remove the anchor -> `created` becomes `subject-settled`.
  4. A CITATION of a ticket id does not raise a new one.
     Mutation: drop CITATION -> `pf:bc80040e3b48` raises a `pf`.
  5. Harness output is not a proposal.
     Mutation: drop HARNESS_ECHO -> the Stop gate files its own prodding.
  6. A backticked marker is a quotation.
     Mutation: drop CODE_SPAN -> the literal `[qs:...]` raises a `qs`.
  7. All 4 kinds are reachable, `qs` and `wr` included.

PROPERTY 7 IS THE ONE THAT MATTERED MOST AND WAS LEAST VISIBLE. `qs` is the kind
he instructed on 2026-10-19 and it could never have been harvested from chat.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

HARVEST = REPO / "scripts" / "harvest_tickets_2026-10-17.py"


@pytest.fixture(scope="module")
def hv():
    spec = importlib.util.spec_from_file_location("ticket_harvester", HARVEST)
    m = importlib.util.module_from_spec(spec)
    sys.modules["ticket_harvester"] = m
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ 1, 7

def test_the_prefilter_is_the_decision_itself(hv, tmp_path, monkeypatch):
    """A 2nd predicate for 1 question is free to drift. It drifted for 11 days.

    EXECUTED, NOT GREPPED, and the first version of this test WAS a grep -- it
    asserted the old regex's absence from the source and then tripped on the
    comment that documents it. A source-text assertion cannot tell a live
    predicate from a described one, which is this project's own
    `execute-do-not-grep` rule, broken here by its own guard.

    So: a synthetic transcript carrying a marker MID-STRING, where the old
    quote-anchored prefilter is blind by construction. If from_chat returns it,
    the prefilter is not narrower than the decision.
    """
    import json
    line = json.dumps({
        "timestamp": "2026-10-28T02:00:00.000Z",
        "message": {"role": "user", "content":
                    "the convergence gate reads the wrong field here pf"},
    })
    (tmp_path / "synthetic.jsonl").write_text(line + "\n", encoding="utf-8")
    monkeypatch.setattr(hv, "TRANSCRIPTS", tmp_path)
    rows = hv.from_chat("2026-10-01")
    assert len(rows) == 1, (
        f"a mid-string marker was discarded before the decision saw it, which "
        f"is the 0.92 discard rate this repair closes; got {rows!r}")
    assert rows[0]["kind"] == "pf"
    assert rows[0]["anchor"], "the row carries no anchor"

    # And the old predicate really is blind to this line, so the test is not
    # vacuously passing on a line both would accept.
    import re as _re
    assert not _re.search(r'"(fr|pf)[:\]]', line, _re.IGNORECASE), (
        "this synthetic line does not actually discriminate the 2 predicates, "
        "so the test proves nothing")


def test_every_chat_raisable_kind_can_be_raised(hv):
    """`qs` and `wr` were unreachable from chat entirely.

    ★ NARROWED 2026-10-30, AND THE NARROWING IS THE POINT RATHER THAN A
    RELAXATION. `ds` became the 5th kind on his ruling of that day, and it is
    DELIBERATELY not raisable from chat: `ds` is also the DeepSeek seat in the
    dispatch table, and 46 of 53 user-role transcript entries carrying the
    token use it as a seat name, Wilson [0.751597, 0.934521], against 0 of his
    794 annotations, Wilson [0.000000, 0.004815]. Raising on chat would file
    dispatch prompts as discussion requests. Measured by
    `scripts/the_ds_label_and_the_kind_allowlist_2026-10-30.py`.

    So the property is no longer "every declared kind" but "every
    CHAT-RAISABLE kind", and the exclusion is asserted below rather than
    assumed, so a kind cannot quietly leave the raisable set.
    """
    raisable = [k for k in hv.KINDS if k not in hv.CHAT_EXCLUDED_KINDS]
    assert len(raisable) == 4, (
        f"{len(raisable)} chat-raisable kinds; the exclusion set has changed "
        "and this test's own figure is stale")
    for kind in raisable:
        assert hv.raises_a_marker(kind) == kind, (
            f"kind {kind!r} cannot be raised from chat, and 2 of the 4 could "
            f"not before 2026-10-28")


def test_the_excluded_kinds_are_refused_from_chat(hv):
    """The other half, so the exclusion is a property and not an absence."""
    assert hv.CHAT_EXCLUDED_KINDS, "nothing is excluded; the pair above is vacuous"
    for kind in hv.CHAT_EXCLUDED_KINDS:
        assert kind in hv.KINDS, f"{kind!r} is excluded but is not a kind"
        assert hv.raises_a_marker(kind) is None, (
            f"kind {kind!r} is in CHAT_EXCLUDED_KINDS yet chat raised it")


# ------------------------------------------------------------------ 4, 5, 6

@pytest.mark.parametrize("text,expected", [
    ("pf", "pf"),
    ("qs", "qs"),
    ("fr", "fr"),
    ("wr", "wr"),
    ("pf: the convergence gate reads the wrong field", "pf"),
    ("wr - the joint half is still owed", "wr"),
    # citations
    ("see pf:bc80040e3b48 for the heredoc repair", None),
    ("closing qs:524186098488 with his words as verification", None),
    # harness echo
    ("Stop hook feedback: pf tickets remain outstanding", None),
    ("This session is being continued from a previous conversation pf", None),
    ("[mc] STANDING HARD CONSTRAINT pf", None),
    # quotation
    ("the `[qs:...]` reference the ask-checker wants", None),
    ("see `pf` in the marker table", None),
    # plain prose
    ("performance is acceptable and the frame rate is fine", None),
])
def test_raises_a_marker_truth_table(hv, text, expected):
    assert hv.raises_a_marker(text) == expected


def test_a_register_cannot_file_its_own_prodding(hv):
    """THE CIRCULARITY. 24 of 31 rows were this session's own Stop-gate output."""
    echo = ("Stop hook feedback: [python3 ~/.claude/hooks/ticket_queue_gate.py]: "
            "[tickets] 3 OPEN pf awaiting resolution")
    assert hv.raises_a_marker(echo) is None, (
        "the harvester would file the ticket gate's own output as a new "
        "ticket, so the register becomes its own source")


# ------------------------------------------------------------------ 2, 3

def test_every_chat_row_carries_a_distinct_anchor(hv, tmp_path, monkeypatch):
    """SYNTHETIC, because the live archive contains 0 bare chat markers.

    A skipped guard guards nothing, which is the unwired-addition half of the
    additive standard. 3 messages at 3 timestamps, 2 of them with identical
    text, so the anchor's distinctness is actually put under strain rather than
    asserted over an empty list.
    """
    import json
    lines = [
        {"timestamp": "2026-10-28T02:00:00.000Z",
         "message": {"role": "user", "content":
                     "the gate reads a field that no seat writes pf"}},
        {"timestamp": "2026-10-28T02:05:00.000Z",
         "message": {"role": "user", "content":
                     "the gate reads a field that no seat writes pf"}},
        {"timestamp": "2026-10-28T02:10:00.000Z",
         "message": {"role": "user", "content":
                     "should the quiet run adapt to the signal instead qs"}},
    ]
    (tmp_path / "s.jsonl").write_text(
        "\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")
    monkeypatch.setattr(hv, "TRANSCRIPTS", tmp_path)
    rows = hv.from_chat("2026-10-01")
    assert len(rows) == 3, f"expected 3 harvested rows, got {len(rows)}"
    assert {r["kind"] for r in rows} == {"pf", "qs"}
    assert all(r.get("anchor") for r in rows), (
        "a chat row without an anchor reaches the subject tier with no "
        "identity, which is the root cause this repair closes")
    anchors = [r["anchor"] for r in rows]
    assert len(set(anchors)) == len(anchors), "anchors collide"


def test_an_anchor_escapes_the_subject_tier(tmp_path):
    """Property 3, and it holds whether or not the archive has a chat marker.

    This is the mechanism the missing anchor was defeating: without one, a
    different question on a settled mechanism is absorbed; with one, it is its
    own item. Executed against the real store class, not described.
    """
    from bench.ticket_store import TicketStore
    s = TicketStore(path=tmp_path / "t.jsonl")
    s.load()
    first, o = s.propose("pf", "first", "the loader ignores the declared scope",
                         "chat", subjects=["mod.fn"])
    assert o == "created"
    s.close(first.tid, "fixed", verification="test_x passed")
    _, without = s.propose("pf", "second", "a different question on that loader",
                           "chat", subjects=["mod.fn"])
    _, with_anchor = s.propose("pf", "third", "a different question on that loader",
                               "chat", subjects=["mod.fn"],
                               anchor="chat#2026-10-28T01:00:00#deadbeef")
    assert without == "subject-settled", (
        "anti-vacuity: with no identity named, the tier must still decide")
    assert with_anchor == "created", (
        "an anchor is an explicit identity and must escape the subject tier; "
        "from_chat supplied none for 11 days")


def test_the_kind_check_does_not_disable_deduplication(tmp_path):
    """The store-side half of the same repair, with its anti-vacuity guard."""
    from bench.ticket_store import TicketStore
    s = TicketStore(path=tmp_path / "t.jsonl")
    s.load()
    a, _ = s.propose("pf", "a", "the strength order is computed once",
                     "chat", subjects=["season_strength_order"])
    s.close(a.tid, "fixed", verification="test_y passed")
    _, same_kind = s.propose("pf", "b", "the order is computed once and never "
                             "revisited", "chat",
                             subjects=["season_strength_order"])
    _, other_kind = s.propose("qs", "c", "is the order still right after the "
                              "change", "chat",
                              subjects=["season_strength_order"])
    assert same_kind in ("subject-settled", "reworded-match"), (
        f"same-kind deduplication was disabled; got {same_kind!r}")
    assert other_kind == "created", (
        f"a settled fix answered a question nobody asked it; got {other_kind!r}")
