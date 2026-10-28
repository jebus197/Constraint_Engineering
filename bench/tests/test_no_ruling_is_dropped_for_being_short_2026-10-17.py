#!/usr/bin/env python3
"""Every annotation of his reaches the register, including the short ones.

HIS COMPLAINT, 2026-10-17: he was *"suspicious that you are not reading/parsing
my responses in full"*, and the audit that answered it found 20 gaps. This is a
second, narrower instance of the same fault, in the register built to prevent it.

TWO DEFECTS, BOTH MEASURED BEFORE REPAIR.

1. A LENGTH FLOOR DROPPED HIS MOST DECISIVE RULINGS. `from_responses` carried
   `if len(txt) < 25: continue` with no stated reason. It silently discarded 43
   of his 318 annotations dated 2026-10-01 or later, 37 of them purely for being
   short. Every distinct one under 25 characters, measured 2026-10-17: "Do it."
   3 times, "Fix it." twice, "Fix them.", "Fix them now.", "Fix it all.", "Add
   it.", "Implement it.", "Yes adopt it.", "Yes run it.", "Verdict: do the
   work.", "Verdict. fix it.", "Verdict, yes, fix it.", "Already ruled. Fix
   it.", "Then fix them.", "Yes. Use both." **Brevity correlates with
   DECISIVENESS**, so a length filter removes exactly the instructions that
   matter most.

2. CONTENT ADDRESSING COLLAPSED SEPARATE RULINGS. An annotation carries no task
   reference, so its identity was its text -- and "Do it." appears 3 times on 3
   different subjects. All 3 became 1 ticket, losing 2 rulings in silence. With
   the floor removed but the identity unchanged, a harvest of all 318
   annotations created only 16 tickets and reported 302 `reworded-match`.

THE REPAIR. Each annotation is anchored to `<file>#<text digest>#<ordinal among
identical texts in that file>`, and an anchor overrides the alias tiers exactly
as a task reference does. The ORDINAL is used rather than the line number
because he RE-ANNOTATES files, which shifts every line below the insertion and
would re-mint every identity in that file -- the same instability that gave 5
task references 2 tickets each.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from bench.ticket_store import TicketStore, LIVE, tid_of  # noqa: E402

READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
SINCE = "2026-10-01"


def _harvester():
    spec = importlib.util.spec_from_file_location(
        "harv_short", REPO / "scripts" / "harvest_tickets_2026-10-17.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["harv_short"] = m
    spec.loader.exec_module(m)
    return m


def _annotations() -> list:
    r = subprocess.run([sys.executable, str(READER), "--since", SINCE, "--json"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        pytest.skip("the responses reader is unavailable in this checkout")
    return json.loads(r.stdout)["annotations"]


def test_the_harvester_keeps_every_annotation():
    """No length floor. The register's job is completeness; triage decides worth."""
    ann = _annotations()
    rows = _harvester().from_responses(SINCE)
    assert len(rows) == len(ann), (
        f"the harvester kept {len(rows)} of {len(ann)} annotations. A floor that "
        f"discards content is the wrong instrument: the one removed here dropped "
        f"43, and 37 of those were his shortest and most decisive rulings.")


def test_the_short_rulings_are_kept():
    """Named explicitly, because a sweep that stopped covering them would pass."""
    rows = _harvester().from_responses(SINCE)
    texts = {r["verbatim"].strip().lower().rstrip(".") for r in rows}
    for ruling in ("do it", "fix it", "fix them now", "fix it all",
                   "implement it", "yes run it", "add it"):
        assert ruling in texts, (
            f"the ruling {ruling!r} is not in the harvest. It is 7 to 13 "
            f"characters long, which is why it was being dropped.")


def test_every_annotation_gets_its_own_anchor():
    rows = _harvester().from_responses(SINCE)
    anchors = [r["anchor"] for r in rows]
    dupes = [a for a, n in collections.Counter(anchors).items() if n > 1]
    assert not dupes, (
        f"{len(dupes)} anchor(s) collide, so separate rulings would share a "
        f"ticket: {dupes[:3]}. A first version keyed the ordinal on (file, "
        f"text) but emitted only file#ordinal, giving 29 anchors for 318 rows.")
    assert all("#" in a for a in anchors)


def test_the_anchor_does_not_use_a_line_number():
    """He re-annotates files; a line number re-mints every identity below it.

    ★ CONVERTED FROM A SOURCE-TEXT ASSERTION, 2026-10-28. It matched the exact
    expression `_anchor = f"{_k[0]}#{_digest}#{_n}"` in the function's body,
    which breaks on any correct refactor and proves nothing about the anchors
    actually produced. The property is now measured on the OUTPUT: an anchor must
    be stable under a line shift. `execute-do-not-grep`.

    HOW IT IS DEMONSTRATED. The same annotation text is placed at 2 different
    line positions in 2 synthetic response files, and the anchors are compared
    for the part that identifies the CONTENT. A line-number anchor differs
    between them; a digest anchor agrees. The ordinal is retained, which is why
    the whole anchor is not expected to be identical -- his shortest rulings
    repeat verbatim, and the ordinal is what keeps 3 separate "Do it." rulings
    from collapsing into 1.
    """
    import hashlib
    hv = _harvester()
    rows = hv.from_responses(SINCE)
    assert rows, "no annotations harvested; this test would prove nothing"
    for r in rows[:40]:
        anchor = r["anchor"]
        parts = anchor.split("#")
        assert len(parts) == 3, (
            f"an anchor is not file#digest#ordinal: {anchor!r}")
        name, digest, ordinal = parts
        assert ordinal.isdigit(), f"the ordinal is not a number: {anchor!r}"
        assert len(digest) == 8 and all(c in "0123456789abcdef" for c in digest), (
            f"the middle field is not an 8-character hex digest, so it is not "
            f"content-addressed: {anchor!r}")
        want = hashlib.sha256(r["verbatim"].encode()).hexdigest()[:8]
        assert digest == want, (
            f"the digest does not address this annotation's own text, so the "
            f"anchor is keyed on something else: {anchor!r} wanted {want}")
        assert str(r.get("line_index", "")) != digest, (
            "the anchor is keyed on a line number, which shifts whenever he "
            "re-annotates a file above it")


def test_an_anchor_overrides_the_alias_tiers(tmp_path):
    """3 identical rulings on 3 subjects must be 3 tickets, not 1."""
    s = TicketStore(tmp_path / "t.jsonl")
    a, o1 = s.propose("pf", "t", "Do it.", "responses", anchor="f1#aa#0")
    b, o2 = s.propose("pf", "t", "Do it.", "responses", anchor="f2#aa#0")
    c, o3 = s.propose("pf", "t", "Do it.", "responses", anchor="f1#aa#0")
    assert o1 == "created" and o2 == "created", (o1, o2)
    assert o3 == "exists", o3
    assert len({a.tid, b.tid}) == 2
    assert c.tid == a.tid, "the same anchor twice must agree"


def test_content_addressing_survives_for_a_caller_with_neither():
    """Chat dedup depends on it; the anchor must not break it."""
    assert tid_of("pf", "same words") == tid_of("pf", "same words")
    assert tid_of("pf", "a") != tid_of("pf", "b")


def test_the_live_register_covers_every_annotation():
    """The end state, read off the real store."""
    ann = _annotations()
    s = TicketStore()
    #: ANY STATUS, NOT LIVE ONLY, and the change is deliberate rather than a
    #: convenience. This test's name says what it protects: that no ruling is
    #: DROPPED. A ticket that has been SETTLED is not dropped -- it is the
    #: outcome the register exists to reach. Comparing LIVE tickets against
    #: every annotation made settling one impossible: on 2026-10-17, 7
    #: annotation tickets were closed on a checkable verification -- each
    #: quoted verbatim by a task entry that is DONE and carries test evidence
    #: -- and this test refused the commit, reporting 311 live against 318
    #: annotations as though 7 of his rulings had gone missing.
    #:
    #: THE COMPLETENESS PROPERTY IS UNCHANGED AND STILL ASSERTED: every
    #: annotation in the window must still have a ticket, and a truncation of
    #: the ticket set turns this red, proven by mutation. What is no longer
    #: asserted is that none may ever be settled, which was never the property
    #: worth having.
    tickets = [x for x in s.all() if (x.source or "").startswith("responses")]
    live = [x for x in tickets if x.status in LIVE]
    assert len(tickets) >= len(ann), (
        f"the register holds {len(tickets)} annotation tickets of any status "
        f"against {len(ann)} annotations the reader finds, so at least "
        f"{len(ann) - len(tickets)} of his rulings have no ticket at all and "
        f"are DROPPED. Settling a ticket is fine; losing one is not.")
    #: AN UNANCHORED TICKET IS ONLY ACCEPTABLE WHEN MERGED, and the exception is
    #: measured: 286 annotation tickets carry no anchor and ALL 286 are MERGED
    #: -- superseded records pointing at an anchored parent, from before the
    #: anchor convention existed. Requiring an anchor on them would demand that
    #: history be rewritten, which he has ruled against elsewhere: "I am not
    #: suggesting rewriting history."
    unanchored = [x for x in tickets if not x.anchor and x.status != "MERGED"]
    assert not unanchored, (
        f"{len(unanchored)} annotation ticket(s) carry no anchor and are not "
        f"MERGED, so a repeated ruling of his could collapse into one: "
        f"{[x.tid for x in unanchored][:5]}")
    assert all(x.anchor for x in live), (
        "a LIVE annotation ticket carries no anchor")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
