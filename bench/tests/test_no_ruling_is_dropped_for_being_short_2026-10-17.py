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
    """He re-annotates files; a line number re-mints every identity below it."""
    src = (REPO / "scripts" / "harvest_tickets_2026-10-17.py").read_text(encoding="utf-8")
    i = src.find("def from_responses")
    j = src.find("\ndef ", i + 10)
    body = src[i:j]
    assert "_anchor = f\"{_k[0]}#{_digest}#{_n}\"" in body, (
        "the anchor is no longer file + digest + ordinal")
    assert "line_index}\"" not in body.split("_anchor =")[1][:200], (
        "the anchor has gone back to a line number, which shifts whenever he "
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
    live = [t for t in s.all()
            if (t.source or "").startswith("responses") and t.status in LIVE]
    assert len(live) == len(ann), (
        f"the register holds {len(live)} live annotation tickets against "
        f"{len(ann)} annotations the reader finds")
    assert all(t.anchor for t in live), (
        "an annotation ticket carries no anchor, so a repeated ruling could "
        "collapse into it again")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
