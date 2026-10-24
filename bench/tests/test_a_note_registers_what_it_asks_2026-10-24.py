"""A note that asks him for a ruling must name the ticket for that ask.

HIS RULING, 2026-10-24: approved, in answer to "should the same rule apply to the
TTS -> list path, so a question in a TTS file must be registered before the file
is delivered?"

THE CASE IT EXISTS FOR. Master_Task_Completion_List_2026-10-19.txt headed a
section "WHAT NEEDS HIS RULING, AND NOTHING ELSE DOES" and listed 4 numbered
items. The stagger value was one of them and was tracked NOWHERE -- no task
entry, no ticket, 0 live tickets naming it. It existed only as prose in a file he
had not re-read.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROD = ROOT / "scripts" / "a_note_registers_what_it_asks_2026-10-24.py"


def _mod():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("_anr", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_anr"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def m():
    return _mod()


def test_it_finds_a_numbered_ask_under_a_ruling_heading(m, tmp_path):
    """The exact shape that lost the stagger value."""
    p = tmp_path / "note.md"
    p.write_text(
        "TITLE\n\nSome prose.\n\nWHAT NEEDS HIS RULING, AND NOTHING ELSE DOES\n\n"
        "1. THE STAGGER VALUE. 20 seconds is shipped, bounded below by 18.7 and "
        "above by 26.7, both measured.\n\n"
        "2. SOMETHING ELSE ENTIRELY that also needs a decision from him.\n\n"
        "WHAT IS STILL RUNNING\n\nmore prose.\n", encoding="utf-8")
    found = m.asks(p)
    assert len(found) == 2, [a["text"][:60] for a in found]
    assert any("STAGGER" in a["text"] for a in found)


def test_a_heading_is_not_an_ask(m, tmp_path):
    """It was counted as one in the first version, which reported 5 asks where 4
    existed. Noise at that level is how a gate gets switched off."""
    p = tmp_path / "note.md"
    p.write_text("TITLE\n\nWHAT NEEDS HIS RULING\n\nnothing numbered here.\n",
                 encoding="utf-8")
    assert m.asks(p) == []


def test_an_inline_marker_with_substance_is_an_ask(m, tmp_path):
    p = tmp_path / "note.md"
    p.write_text("TITLE\n\nThe severity ruler should be measured before either "
                 "panel fix is built. NEEDS YOUR RULING.\n", encoding="utf-8")
    found = m.asks(p)
    assert len(found) == 1 and found[0]["kind"] == "inline"


def test_an_ask_that_names_a_live_ticket_passes(m):
    """THE RULE, and the reason it is id-based: there is no discriminator left to
    get wrong. Similarity was tried and failed in BOTH directions -- it reported
    5 of 5 unregistered when 4 were tracked, and after widening it CLEARED the
    stagger, the one genuinely untracked ask, because entry B38 mentions the
    stagger too. Two asks about one noun are not separable by overlap."""
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    store = TicketStore()
    live = store.workable()
    if not live:
        pytest.skip("no live ticket to reference")
    tid = live[0].tid[:12]
    ok = [{"kind": "section-item", "text": f"A REAL ASK about something. [qs:{tid}]"}]
    assert m.unregistered(ok, store) == []


def test_an_ask_naming_a_ticket_that_does_not_exist_fails(m):
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    store = TicketStore()
    bad = [{"kind": "section-item",
            "text": "AN ASK naming a ticket the register never held. [qs:ffffffffffff]"}]
    out = m.unregistered(bad, store)
    assert len(out) == 1
    assert "does not hold" in out[0]["why"]


def test_an_ask_naming_nothing_fails(m):
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    bad = [{"kind": "section-item", "text": "THE STAGGER VALUE needs a decision."}]
    out = m.unregistered(bad, TicketStore())
    assert len(out) == 1 and out[0]["why"] == "names no ticket"


def test_the_detector_ignores_ordinary_rhetorical_questions(m, tmp_path):
    """These notes are written for a third-party reader and pose questions
    constantly. A question mark must not be the trigger, or the rule fires on
    every note and is worth nothing."""
    p = tmp_path / "note.md"
    p.write_text("TITLE\n\nWhy did the run fail? Because the gate refused. "
                 "Was that right? Yes, and the measurement says so.\n",
                 encoding="utf-8")
    assert m.asks(p) == []


def test_it_reads_a_word_rewritten_file(m, tmp_path):
    """His .txt files are CR-only cp1252 because Word rewrites them; a checker
    that could not read one would pass every file it mattered most for."""
    p = tmp_path / "note.txt"
    # the 0x92 byte is cp1252's right single quote -- the one Word puts in his
    # files -- so it is written as a BYTE rather than encoded from a str.
    p.write_bytes(b"TITLE\rWHAT NEEDS HIS RULING\r1. AN ASK about the "
                  b"\x92stagger\x92 value that is long enough to count.\r")
    found = m.asks(p)
    assert len(found) == 1, found
