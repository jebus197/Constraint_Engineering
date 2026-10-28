# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fix_review_panel_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 753d942c9452d0cce53a994b98ce5aecb622350e271b215cae15a93fdf2971b5
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""FALSIFIER for CHANGE 3: the kind filter on the subject tier.

THE CASE THE SUITE DOES NOT COVER, which is what the brief asked for by name.
Every one of the 4 known-rediscovery cases in
`bench/tests/test_ticket_store_2026-10-17.py` seeds with kind `pf` and proposes
with kind `pf` (see `_seeded` and `CASES`). The suite is therefore blind to the
cross-kind axis BY CONSTRUCTION and cannot detect a weakening along it.

The founder's ruling of 2026-10-19 distinguishes a QUESTION from a PROPOSED FIX
-- "he answers mine, I answer his". The committed change generalises that to all
6 unordered kind pairs, including `fr` against `pf` and `wr` against `pf`, where
the resolutions do NOT travel in opposite directions: a feature request he
raised, a proposed fix against the same mechanism, and the work-remaining entry
for it are the SAME work item seen from 3 sides.

The motivating rediscovery of 2026-10-17 is exactly of that shape: HIS wording
about the routing ladder settled, and the assistant later re-proposed the same
change. `from_chat` types a ticket from the MARKER the author wrote, not from
the content, so his `fr` and the assistant's `pf` land on different kinds while
naming the same subject.

Run: python3 -m pytest bench/tests/test_the_kind_filter_reopens_the_cross_kind_rediscovery_2026-10-28.py -q -s
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from ticket_store import TicketStore  # noqa: E402

HIS_LADDER = (
    "Routing should be blind to what a models name is anyway, it should just "
    "look at the available resources and if it can't climb, then it should "
    "climb sideways, to the next highest rated available model, even if that "
    "is another version of Opus 4.8.")
MY_LADDER_PARAPHRASE = (
    "Models can use up and down, as well as sideways, according to their "
    "measured capability and a sane distribution of the available resources, "
    "so that no model sits idle when it is still capable of doing useful work.")
SUBJECT = "routing.rank_falsifier_writers"


def _settled_store(path, kind: str) -> TicketStore:
    s = TicketStore(path)
    t, _ = s.propose(kind, "side-steps over available resources", HIS_LADDER,
                     "chat", subjects=[SUBJECT])
    s.close(t.tid, "already implemented",
            "executed rank_falsifier_writers: 3 of 3 exclusions dropped")
    return s


def test_the_same_kind_rediscovery_is_still_blocked(tmp_path):
    """Control: the case the suite DOES cover is unaffected."""
    s = _settled_store(tmp_path / "same.jsonl", "pf")
    _, outcome = s.propose("pf", "candidate", MY_LADDER_PARAPHRASE, "chat",
                           subjects=[SUBJECT])
    print(f"settled pf -> proposed pf : {outcome}")
    assert outcome == "subject-settled"


def test_a_settled_fr_no_longer_blocks_the_same_work_raised_as_pf(tmp_path):
    """THE UNCOVERED CASE. The rediscovery the tier was built for returns."""
    s = _settled_store(tmp_path / "cross.jsonl", "fr")
    _, outcome = s.propose("pf", "candidate", MY_LADDER_PARAPHRASE, "chat",
                           subjects=[SUBJECT])
    print(f"settled fr -> proposed pf : {outcome}")
    assert outcome == "created", (
        "if this is 'subject-settled' the kind filter did not reach this path "
        "and the falsifier is refuted")


def test_a_settled_pf_no_longer_blocks_the_same_work_raised_as_wr(tmp_path):
    """`wr` is work REMAINING on a fix -- the same item, not an opposite one."""
    s = _settled_store(tmp_path / "wr.jsonl", "pf")
    _, outcome = s.propose("wr", "candidate", MY_LADDER_PARAPHRASE, "chat",
                           subjects=[SUBJECT])
    print(f"settled pf -> proposed wr : {outcome}")
    assert outcome == "created"


def test_the_known_case_suite_is_single_kind_and_cannot_see_this(tmp_path):
    """Why the suite passing is not evidence that nothing broke."""
    src = (pathlib.Path(__file__).resolve().parents[0]
           / "test_ticket_store_2026-10-17.py").read_text()
    seeded = src[src.index("def _seeded"):src.index("def _word_overlap_blocks")]
    kinds = {k for k in ("fr", "pf", "qs", "wr")
             if f'propose("{k}"' in seeded or f"propose('{k}'" in seeded}
    print(f"kinds used by the known-rediscovery seeding: {sorted(kinds)}")
    assert kinds == {"pf"}, (
        "the known-case suite now exercises more than one kind; re-read this "
        "falsifier's premise")
