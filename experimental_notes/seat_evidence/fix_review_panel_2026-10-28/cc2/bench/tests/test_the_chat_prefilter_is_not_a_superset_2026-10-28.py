# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fix_review_panel_2026-10-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b53ebb44bb38e572c0fa7470a6ff54214f2653afedffdeeb9fadbe3a1e6e91c7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""FALSIFIER + REGRESSION for CHANGE 4: `\\b(fr|pf|qs|wr)\\b` was NOT a superset
of the decision, and the form it dropped is the commonest one.

THE ARGUMENT UNDER TEST, from `from_chat`'s own note: "MARKER can only fire if a
kind token appears literally in the decoded text, JSON never escapes ASCII
letters, and MARKER's own left and right contexts each imply a word boundary."

THE LAST CLAUSE IS FALSE ON THE RAW LINE. `MARKER` is compiled with
`re.MULTILINE` and its left context is `(?<=^)|(?<=[\\s(\\[])`, so a NEWLINE is
an accepted left neighbour. In the raw JSON line that newline is the 2
characters `\\` and `n`; the character immediately left of the token is then the
WORD character `n`, and `\\b` fails. The decision accepts, the prefilter rejects,
and the dropped shape is a marker at the start of a line inside a multi-line
message -- which is how a marker on its own line is written.

CONSEQUENCE FOR THE BRIEF'S HEADLINE. CHANGE 4 reports that, with all filters,
"the number of messages whose text actually RAISES a marker is 0". That 0 was
produced by a reader that provably cannot see a newline-prefixed marker, so it
is not yet evidence that the chat half harvests nothing.

Run: python3 -m pytest bench/tests/test_the_chat_prefilter_is_not_a_superset_2026-10-28.py -q
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re

HARVESTER = (pathlib.Path(__file__).resolve().parents[2]
             / "scripts" / "harvest_tickets_2026-10-17.py")


def _harvester():
    spec = importlib.util.spec_from_file_location("_harvest", HARVESTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _raw(text: str) -> str:
    """The transcript line shape: one JSON object per line."""
    return json.dumps({"role": "user",
                       "content": [{"type": "text", "text": text}]})


#: Decoded texts the DECISION accepts. Each puts the marker after a whitespace
#: character that JSON encodes as a 2-character escape.
ESCAPED_LEFT_NEIGHBOURS = [
    ("newline", "I have been thinking about the gate.\nqs: should K be adaptive?"),
    ("tab",     "see below:\n\tfr: add a completion barrier reader"),
    ("return",  "first\rwr: finish the harvester"),
]
PLAIN = ("space", "and so qs: does the gate hold?")


def test_the_old_boundary_prefilter_rejects_what_the_decision_accepts():
    """The defect itself, demonstrated against the OLD pattern verbatim."""
    h = _harvester()
    old = re.compile(r"\b(?:fr|pf|qs|wr)\b", re.IGNORECASE)
    violations = []
    for name, text in ESCAPED_LEFT_NEIGHBOURS:
        assert h.MARKER.search(text), f"{name}: the decision must accept this"
        if not old.search(_raw(text)):
            violations.append(name)
    print(f"old prefilter rejects {len(violations)} of "
          f"{len(ESCAPED_LEFT_NEIGHBOURS)} decided cases: {violations}")
    assert violations == ["newline", "tab", "return"], (
        "the superset claim holds after all -- this falsifier is refuted")
    # control: the plain-space form was never the problem
    assert old.search(_raw(PLAIN[1])), "control case should pass the old filter"


def test_the_live_prefilter_is_now_a_superset_on_the_same_cases():
    """The repair: a bare substring, which encoding cannot move."""
    h = _harvester()
    for name, text in ESCAPED_LEFT_NEIGHBOURS + [PLAIN]:
        assert h.MARKER.search(text), name
        assert h.CANDIDATE_LINE.search(_raw(text)), (
            f"{name}: the live prefilter still drops a decided marker")


def test_the_superset_property_holds_over_a_generated_sweep():
    """Every whitespace left-neighbour, every kind, every marker punctuation."""
    h = _harvester()
    lefts = ["\n", "\t", "\r", " ", "\f", "\v", "(", "["]
    rights = [":", "]", ")", " - "]
    checked = failures = 0
    for kind in ("fr", "pf", "qs", "wr"):
        for L in lefts:
            for R in rights:
                text = f"preamble{L}{kind}{R}the body of the proposal"
                if not h.MARKER.search(text):
                    continue
                checked += 1
                if not h.CANDIDATE_LINE.search(_raw(text)):
                    failures += 1
    print(f"decided cases {checked}; prefilter misses {failures}")
    assert checked > 0, "the sweep decided nothing -- the test proves nothing"
    assert failures == 0, f"{failures} decided cases still rejected by the prefilter"
