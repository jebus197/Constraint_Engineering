#!/usr/bin/env python3
"""Blind round first, joint round second — enforced, not remembered.

THE FOUNDER'S RULING, 2026-10-05/06: *"Remember panel review runs in star topology
format, with a blind round each and a joint round once the blind round is in."* And,
when it was recorded as a preference: *"I didn't just state it as a 'preference', I
stated that it should be built into all confer round machinery going forward so it
couldn't be skipped."*

WHAT COULD BE SKIPPED, AND WAS NEARLY SKIPPED TONIGHT. Blindness was opt-in through the
`PANEL_BLIND_OF` environment variable. Nothing checked it. On 2026-10-06 the cc2 blind
round was dispatched while the fable round's whole reply sat in the live tree, and the
only thing standing between the 2 was the operator remembering to set 1 variable. The
purge worked; the DISCIPLINE was unenforced. A control that depends on remembering is
not a control.

THE GROUPING KEY IS THE BRIEF ITSELF, not an operator-supplied label. 2 rounds asking
the SAME question have a byte-identical `BRIEF.md`, so sha256 over the brief groups
them with no bookkeeping to forget and nothing to get wrong. This is exactly the check
performed by hand tonight -- the 2 briefs' hashes were compared before dispatch -- made
mechanical.

A JOINT ROUND CANNOT BE GROUPED THAT WAY, because its brief necessarily differs: it
carries the blind replies. So a joint round declares its parents with
`PANEL_JOINT_OF=<blind_round>,<blind_round>` and is refused unless every seat it
dispatches has a LANDED blind reply among them.

LANDED MEANS A NON-EMPTY `response`, and that definition lives here once. The cc2 round
wrote a 9280-byte `cc2.json` carrying `ok: False` and a response of 0 words; a check for
file existence would have called that a landed blind round and permitted a joint round
built on nothing.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

#: Reply keys a seat's answer may live under. `response` is what the dispatcher
#: writes; `reply` DOES NOT EXIST and reading it returns 0 characters, which is how
#: a landed 1693-word fable reply was first misread as empty.
_REPLY_KEYS = ("response", "reply", "text")


def brief_fingerprint(round_dir: pathlib.Path) -> str | None:
    """sha256 of the round's BRIEF.md, or None if it has none."""
    b = round_dir / "BRIEF.md"
    if not b.is_file():
        return None
    return hashlib.sha256(b.read_bytes()).hexdigest()


def seat_reply_words(round_dir: pathlib.Path, seat: str) -> int:
    """How many words that seat actually returned in that round. 0 if none.

    THE SINGLE DEFINITION OF "LANDED" in this project. Callers must not re-derive
    it: a producer and a consumer that each define it correctly can still disagree.
    """
    f = round_dir / f"{seat}.json"
    if not f.is_file():
        return 0
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    for k in _REPLY_KEYS:
        v = d.get(k)
        if isinstance(v, str) and v.split():
            return len(v.split())
    return 0


def landed_seats(round_dir: pathlib.Path) -> set:
    """Every seat in that round directory that returned a non-empty reply."""
    out = set()
    for f in round_dir.glob("*.json"):
        seat = f.stem
        if seat.endswith(".tools") or "." in seat:
            continue
        if seat in ("canonical_attribution", "canonical_touched",
                    "sandbox_manifest", "watchdog_status"):
            continue
        if seat_reply_words(round_dir, seat) > 0:
            out.add(seat)
    return out


def sibling_rounds_on_the_same_question(logs: pathlib.Path,
                                        round_name: str) -> list:
    """Other rounds whose BRIEF.md is byte-identical AND which have a landed reply.

    A sibling with no landed reply is not a blindness hazard: there is nothing to
    leak. That keeps a failed sibling (cc2's first attempt) from blocking its own
    re-dispatch.
    """
    me = logs / round_name
    fp = brief_fingerprint(me)
    if fp is None:
        return []
    out = []
    for d in sorted(logs.iterdir()):
        if not d.is_dir() or d.name == round_name:
            continue
        if brief_fingerprint(d) != fp:
            continue
        if landed_seats(d):
            out.append(d.name)
    return out


def check_blind_round(logs: pathlib.Path, round_name: str, blind_of) -> str | None:
    """Refusal message if a sibling holding a landed reply is not purged.

    Returns None to proceed.
    """
    declared = {x.strip() for x in (blind_of or ()) if str(x).strip()}
    siblings = sibling_rounds_on_the_same_question(logs, round_name)
    missing = [s for s in siblings if s not in declared]
    if not missing:
        return None
    return (
        "REFUSED: star topology requires this blind round to be blind to every "
        "round already answered on the SAME question.\n"
        f"  this round      : {round_name}\n"
        f"  same brief, answered: {missing}\n"
        f"  declared blind of   : {sorted(declared) or '(nothing)'}\n"
        "  The briefs are byte-identical, so these rounds ask the same question and\n"
        "  their replies are reachable from this seat's sandbox copy.\n"
        f"  Re-run with: PANEL_BLIND_OF={','.join(siblings)}")


def check_joint_round(logs: pathlib.Path, round_name: str, joint_of,
                      roster) -> str | None:
    """Refusal message if a joint round is dispatched before its blind rounds land.

    Every seat about to be dispatched must have a landed blind reply among the
    declared parents. Returns None to proceed.
    """
    parents = [x.strip() for x in (joint_of or ()) if str(x).strip()]
    seats = [s for s in roster]
    if not parents:
        return (
            "REFUSED: a joint round must declare the blind rounds it follows.\n"
            f"  this round: {round_name}\n"
            "  Set PANEL_JOINT_OF=<blind_round>[,<blind_round>...]\n"
            "  The founder's ruling is a blind round each, THEN a joint round once\n"
            "  the blind round is in. A joint round with no declared parents cannot\n"
            "  be checked against that.")
    answered = set()
    detail = []
    for p in parents:
        d = logs / p
        if not d.is_dir():
            return (f"REFUSED: joint round {round_name} names a parent that does "
                    f"not exist: {p}")
        got = landed_seats(d)
        answered |= got
        detail.append(f"  {p}: landed {sorted(got) or '(none)'}")
    missing = [s for s in seats if s not in answered]
    if not missing:
        return None
    return (
        "REFUSED: star topology requires every seat's BLIND round to be in before "
        "the joint round.\n"
        f"  this round : {round_name}\n"
        f"  roster     : {seats}\n"
        f"  no landed blind reply for: {missing}\n"
        + "\n".join(detail) + "\n"
        "  A seat joining the joint round without having answered blind has seen\n"
        "  the others' positions before forming its own, which is the whole thing\n"
        "  the blind round exists to prevent.")
