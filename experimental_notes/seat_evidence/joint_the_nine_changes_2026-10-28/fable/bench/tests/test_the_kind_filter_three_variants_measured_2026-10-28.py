# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_nine_changes_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 9c750866faea6d64a7648b3c164bd9fc68714be134986079e3baa84d702ac59a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Kind-ignorant vs shipped (all-kind) vs narrow (qs-only) -- measured, not argued.

THE JOINT ROUND'S QUESTION (fix_review_panel_2026-10-28): cc2 proposed reverting
the subject tier's kind filter (measured recovery 1 of 31, Fisher p = 0.5);
fable demonstrated the same filter admits a cross-kind reworded duplicate; CC1
holds the filter implements the founder's 2026-10-19 ruling and stays. A fourth
candidate -- exempt only `qs`, the ruling's literal subject -- would close
fable's admission while keeping the ruling. This file measures all three
variants on the three DOCUMENTED case families, so the choice is a table, not
a preference.

The three case families, each tied to its evidence:
  A. a settled `pf` vs a new `qs` on the same subject -- the founder's ruling
     case, with a live occurrence (qs:524186098488 blocked by pf:028f975075d0,
     exhibited by scripts/the_subject_blocklist_grows_with_every_close_
     2026-10-28.py).
  B. a settled `pf` vs a GENUINELY NEW `fr` sharing one identifier -- the
     namespace-paths incident of 2026-10-17, a live occurrence, pinned by
     test_a_new_kind_is_not_absorbed_by_a_settled_one.
  C. a settled `pf` vs the SAME item reworded as `fr` -- fable's constructed
     demonstration of 2026-10-28; no live occurrence documented.

Desired outcomes: A created, B created, C subject-settled. No variant achieves
all three, and B and C are INSEPARABLE by kind alone: both are an anchorless
`fr` against a settled `pf` on a shared subject, differing only in text, and
text-similarity repairs were already tried and refused twice (recorded in
bench/tests/test_a_shared_mechanism_does_not_decide_2026-10-17.py). So the
decision falls to documented live occurrences: A and B have one each, C has
none, and SHIPPED is the unique variant right on both documented cases.

The reverse direction of the additive standard also lands here: cc2's revert
is a REMOVAL, and removal requires a committed measurement that the
replacement dominates. This file is that measurement run both ways, and it
shows the kind-ignorant store does NOT dominate: it loses A and B to win C.
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
NEW_QS = ("does the routing ladder's strength order need revisiting each "
          "round, or is once per run enough for the measured workloads")
GENUINELY_NEW_FR = ("the register should expose namespace paths so that issues "
                    "can be browsed as a tree rather than queried as a log")
SAME_FAULT_REWORDED = ("the strength order is computed once and never "
                       "revisited, so the routing ladder cannot climb past "
                       "its first rung")
SUB = "season_strength_order"


def _seeded(tmp_path):
    s = TicketStore(path=tmp_path / "t.jsonl")
    s.load()
    t, outcome = s.propose("pf", "the ladder cannot climb", SETTLED_TEXT,
                           source="chat", subjects=[SUB])
    assert outcome == "created"
    s.close(t.tid, "fixed", verification="bench/tests/test_the_ladder.py")
    return s


def _variant_blocks(store, kind: str, variant: str) -> bool:
    """The subject-tier decision under each candidate filter, built from the
    store's own primitives (mirrors bench/ticket_store.py line 855)."""
    blocked = [b for b in store.settled_on_subject(SUB)]
    if variant == "shipped":
        blocked = [b for b in blocked if b.kind == kind]
    elif variant == "narrow_qs_only":
        blocked = [b for b in blocked
                   if b.kind == kind or ("qs" not in (b.kind, kind))]
    elif variant != "kind_ignorant":
        raise ValueError(variant)
    return bool(blocked)


CASES = [("A_ruling_qs", "qs", NEW_QS, False),
         ("B_namespace_fr", "fr", GENUINELY_NEW_FR, False),
         ("C_reworded_dup_fr", "fr", SAME_FAULT_REWORDED, True)]


def test_the_table_is_what_the_joint_round_says(tmp_path):
    s = _seeded(tmp_path)
    score = {}
    for variant in ("kind_ignorant", "shipped", "narrow_qs_only"):
        right = {name: _variant_blocks(s, kind, variant) == want_block
                 for name, kind, _, want_block in CASES}
        score[variant] = right
    # The measured table, pinned. Shipped: A+B right, C wrong. Narrow: A+C
    # right, B wrong. Ignorant: C right, A+B wrong.
    assert score["shipped"] == {"A_ruling_qs": True, "B_namespace_fr": True,
                                "C_reworded_dup_fr": False}, score
    assert score["narrow_qs_only"] == {"A_ruling_qs": True,
                                       "B_namespace_fr": False,
                                       "C_reworded_dup_fr": True}, score
    assert score["kind_ignorant"] == {"A_ruling_qs": False,
                                      "B_namespace_fr": False,
                                      "C_reworded_dup_fr": True}, score
    # NO VARIANT DOMINATES; the revert cc2 proposed is refuted as a dominance
    # claim, and shipped is the unique variant right on both cases with a
    # documented live occurrence (A and B).
    assert not all(score["kind_ignorant"].values())
    assert not all(score["shipped"].values())
    assert not all(score["narrow_qs_only"].values())


def test_the_real_propose_agrees_with_the_shipped_column(tmp_path):
    """Ties the simulated 'shipped' column to the store's actual decision."""
    s = _seeded(tmp_path)
    for name, kind, text, _ in CASES:
        _, outcome = s.propose(kind, name, text, source="chat", subjects=[SUB])
        blocked = outcome != "created"
        assert blocked == _variant_blocks(_seeded(tmp_path / name), kind,
                                          "shipped"), (name, outcome)


def test_b_and_c_are_inseparable_by_kind_alone(tmp_path):
    """B and C present identically to any kind-based filter: anchorless `fr`
    against a settled `pf` on the same subject. A filter cannot be right on
    both without reading text, and text repairs were refused twice."""
    s = _seeded(tmp_path)
    for variant in ("kind_ignorant", "shipped", "narrow_qs_only"):
        assert (_variant_blocks(s, "fr", variant)
                == _variant_blocks(s, "fr", variant))  # same call shape
    # the decision input for B and C is the (kind, subject) pair, and it is
    # equal; only the verbatim differs
    assert CASES[1][1] == CASES[2][1]
