# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'tonights_build_review_b22_b88_b105_2026-11-10', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: af18fb6784170991c6bc8a445f2c121b5ea149bd6e3bf01a1c12a4e26a6424c9
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The derived `what is still owed` must quote a WHOLE statement of the entry.

WHAT THIS GUARDS, and why it is worth a guard. `derive_still_owed` in
`scripts/build_decisions_file_2026-11-07.py` puts DERIVED prose in front of the
founder, under the heading "what is still owed", in a file he reads aloud and
decides from. Nothing crashes when it extracts the wrong span; a human decision
is misinformed instead, which is the most expensive failure this harness can
produce. The free-seat round of 2026-11-10 measured 4 defects in it, all of them
on the live task list, and this file holds each one down as a FIXTURE so the
regression is caught in any clone rather than only on the machine that holds
today's notes:

  1. THE QUOTE WAS CUT AT AN INLINE EMPHASIS. The capture stopped at the next
     `**` of any kind, and in this corpus a `**` is more often emphasis inside
     a sentence than a new heading, so B103 reached him ending "taking it to
     about 891 s --", dropping both the magnitude and the consequence.
  2. THE MARKER'S OWN BOLD SPAN WAS DISCARDED. Words the author wrote between
     OWED and the closing `**` never reached him: 8 of 8 markers carry such
     words, and on B81 they are the answer -- the entry says what is owed is
     the LIMIT rather than the ADDITION, and he was read that the addition
     stands.
  3. A SHORT BODY CARRIED THE QUOTE ACROSS THE NEXT HEADING, because the
     capture carried a 30-character minimum, so an unrelated heading was
     quoted as the answer with its `**` intact.
  4. THE FRAME COERCED A COPULA. "What is still owed is {value}." assumed a
     noun phrase and received a clause, giving "is he ruled the addition" and
     a doubled full stop -- including on `task:B77`, the one entry whose value
     is AUTHORED, so the frame defect was never only in the derivation.

A DECLARED BOUND, recorded rather than defended against. The heading break is
positional: a bold span opening immediately after a sentence terminator ends the
statement. An ABBREVIATION with a trailing stop ("e.g.") immediately followed by
a bold span therefore breaks early. Measured over the live list on 2026-11-10,
that pattern occurs 0 times, so no abbreviation table is added -- an addition
nothing reaches is not additive, and this project has shipped 11 of them.
`test_the_abbreviation_bound_is_declared` pins the bound so it cannot be
forgotten, and asserts the output is still a whole sentence when it fires.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TARGET = REPO / "scripts" / "build_decisions_file_2026-11-07.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("bdf_guard", TARGET)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


#: Real spans from `experimental_notes/CDSFL_MASTER_TASK_LIST.md`, 2026-11-10,
#: shortened only by dropping text after the assertion's reach.
B103 = (
    "**WHAT IS OWED TO YOU, AND IT IS A COST QUESTION RATHER THAN A "
    "CORRECTNESS ONE.** The gate ran 2,427 passed and 1 failed in 598.13 s "
    "tonight, inside the 660 s limit its own header states. Adding the 54 "
    "adds 292.97 s, taking it to about 891 s - **1.35 times that stated "
    "limit**, which is the overrun B81 already reports as an open defect. "
    "**3 OPTIONS, each with its number.** (a) Add all 54."
)
B81 = (
    "**WHAT IS OWED IS HIS, AND IT IS THE LIMIT RATHER THAN THE ADDITION:** "
    "he ruled the addition with the 26-minute figure in hand, so it stands. "
    "**THE NEXT HEADING.** Unrelated."
)
B116 = (
    "**WHAT IS OWED: a fresh full suite AFTER the 40 repairs, recorded by the "
    "tool at the commit it ran on.** That run would also settle whether the "
    "repairs hold, which no board has yet tested. **THE LIMITATION IS WORTH "
    "HIS ATTENTION** because it means the record is narrow."
)


def _terminated(text: str) -> bool:
    return bool(re.search(r"[.!?][\"'’)]?$", text))


def test_an_inline_emphasis_does_not_cut_the_quote(mod):
    """Defect 1. The figures the decision turns on must survive."""
    out = mod.derive_still_owed(B103)
    assert "1.35 times that stated limit" in out, out
    assert "open defect" in out, out
    assert _terminated(out), out
    #: and it must still stop BEFORE the next heading
    assert "3 OPTIONS" not in out, out


def test_the_markers_own_bold_span_is_quoted(mod):
    """Defect 2, in its worst live form: B81's inversion."""
    out = mod.derive_still_owed(B81)
    assert "THE LIMIT RATHER THAN THE ADDITION" in out, out
    assert "THE NEXT HEADING" not in out, out


def test_a_heading_that_is_the_whole_answer_is_not_discarded(mod):
    """Defect 2, in its other live form: B116's dangling referent."""
    out = mod.derive_still_owed(B116)
    assert "a fresh full suite AFTER the 40 repairs" in out, out
    assert not out.startswith("That run"), out
    assert "THE LIMITATION" not in out, out


def test_a_short_body_claims_nothing_rather_than_crossing_a_heading(mod):
    """Defect 3. Conservative by design: no statement, no claim."""
    probe = ("**WHAT IS STILL OWED:** his ruling. "
             "**UNRELATED HEADING ABOUT SOMETHING ELSE ENTIRELY.** tail")
    out = mod.derive_still_owed(probe)
    assert "UNRELATED" not in out, out
    assert out == "", out


def test_no_markdown_delimiter_ever_reaches_the_spoken_file(mod):
    """Defect 3's visible symptom, and the single-asterisk case the
    free seat's own P-Pass of the repair found afterwards."""
    probe = ("**WHAT IS OWED:** *a ruling on the stated limit* and on the "
             "scope rule, which cannot both be honoured as things stand.")
    out = mod.derive_still_owed(probe)
    assert "*" not in out, out


def test_the_frame_does_not_coerce_a_copula_or_double_the_stop(mod):
    """Defect 4, and it bites the AUTHORED value too, not only the derived."""
    assert mod._as_statement("ends in a stop.") == "ends in a stop."
    assert mod._as_statement("no stop") == "no stop."
    assert mod._as_statement("") == ""
    assert mod._as_statement(None) == ""


def test_every_derived_statement_ends_on_a_sentence(mod):
    """The length rule must never emit a fragment or an ellipsis.

    The pre-repair code appended " ..." when no sentence boundary fell
    inside 260 characters, and rendered "...tells every model to classify
    ..." to him on B84.
    """
    long_one = ("**WHAT IS OWED:** "
                + "a ruling on the limit and on the scope rule together, " * 6
                + "and that is the whole of it.")
    out = mod.derive_still_owed(long_one)
    assert not out.endswith("..."), out
    assert _terminated(out), out


def test_the_last_marker_wins(mod):
    """Entries are appended to, so the freshest statement is operative."""
    probe = ("**WHAT IS OWED: the stale answer superseded on the 8th.** "
             "padding text to carry it past the floor comfortably. "
             "**AND WHAT IS STILL OWED: the fresh answer.** This is the "
             "operative statement and it supersedes the one above.")
    out = mod.derive_still_owed(probe)
    assert "fresh answer" in out, out
    assert "stale answer" not in out, out


def test_no_marker_claims_nothing(mod):
    assert mod.derive_still_owed("**B99.** Nothing states what is owed.") == ""
    assert mod.derive_still_owed("") == ""


def test_the_abbreviation_bound_is_declared(mod):
    """THE DECLARED BOUND, pinned so it cannot be quietly forgotten.

    An abbreviation's stop immediately before a bold span reads as a
    sentence end, so the quote stops there. 0 live instances measured
    2026-11-10. What is REQUIRED even when it fires is that the result is
    still a whole sentence and still carries no delimiter -- a short true
    quote, never a fragment.
    """
    probe = ("**WHAT IS OWED:** a ruling on the baseline, e.g. "
             "**the extra suite run**, which is his to release.")
    out = mod.derive_still_owed(probe)
    assert _terminated(out), out
    assert "*" not in out, out
