"""The derived `what is still owed` must quote a WHOLE statement of the entry.

★ DELIVERED BY THE `cc2` SEAT IN THE FREE ROUND OF 2026-11-10 AND ADOPTED WITH
3 ASSERTIONS CHANGED. The orchestrator had repaired the same 4 defects
independently in the live tree, so this guard was run AGAINST that repair rather
than beside the seat's own. 5 of its assertions failed and only 1 of the 5 was a
defect; the other 4 are a design disagreement and a signature difference, and
they are recorded here rather than smoothed away, because this round carried no
compelled convergence.

  ADOPTED -- THE SEAT WAS RIGHT. Its B103 assertion failed because the
  orchestrator's 320-character cut stopped at *"inside the 660 s limit its own
  header states"* while the NEXT sentence reads *"1.35 times that stated
  limit"*. A cut landing before the clause that reverses it does not shorten a
  statement, it inverts it. Measured: 3 of the 8 live derivations were
  truncated and all 3 dropped the operative ask. The limit is now 900, the
  longest full statement is 759, and 0 of 8 truncate.

  CHANGED -- CASE. The seat asserts the heading's ORIGINAL CAPITALS survive.
  They deliberately do not: an all-caps heading is markdown emphasis, and the
  founder listens to this file through a text-to-speech reader that does not
  whisper. The words are all preserved; only their case is lowered, and
  identifiers, paths, figures and slashed compounds keep theirs. The
  assertions are now case-insensitive, which still catches a DROPPED clause --
  the defect the seat found -- without demanding shouted speech.

  CHANGED -- A SHORT BODY. The seat asserts a body of `his ruling.` must yield
  "" because its defect 3 involved a short body crossing a heading. The cause
  was the 30-character MINIMUM, not the shortness: with the minimum gone, a
  short statement is quoted and the heading is not crossed. Returning "" would
  discard a real answer, so the assertion now requires the heading NOT to
  leak rather than requiring silence.

  CHANGED -- SIGNATURE. `_as_statement` does not exist in the live tree; the
  frame helper is `_owed_sentence`. Renamed, not removed.

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
    assert "1.35 times that stated limit".lower() in out.lower(), out
    assert "open defect".lower() in out.lower(), out
    assert _terminated(out), out
    #: and it must still stop BEFORE the next heading
    assert "3 OPTIONS" not in out, out


def test_the_markers_own_bold_span_is_quoted(mod):
    """Defect 2, in its worst live form: B81's inversion."""
    out = mod.derive_still_owed(B81)
    assert "THE LIMIT RATHER THAN THE ADDITION".lower() in out.lower(), out
    assert "THE NEXT HEADING" not in out, out


def test_a_heading_that_is_the_whole_answer_is_not_discarded(mod):
    """Defect 2, in its other live form: B116's dangling referent."""
    out = mod.derive_still_owed(B116)
    assert "a fresh full suite AFTER the 40 repairs".lower() in out.lower(), out
    assert not out.startswith("That run"), out
    assert "THE LIMITATION" not in out, out


def test_a_short_body_claims_nothing_rather_than_crossing_a_heading(mod):
    """Defect 3. Conservative by design: no statement, no claim."""
    probe = ("**WHAT IS STILL OWED:** his ruling. "
             "**UNRELATED HEADING ABOUT SOMETHING ELSE ENTIRELY.** tail")
    out = mod.derive_still_owed(probe)
    assert "UNRELATED" not in out, out
    assert "**" not in out, out
    assert "UNRELATED" not in out.upper(), out


def test_no_markdown_delimiter_ever_reaches_the_spoken_file(mod):
    """Defect 3's visible symptom, and the single-asterisk case the
    free seat's own P-Pass of the repair found afterwards."""
    probe = ("**WHAT IS OWED:** *a ruling on the stated limit* and on the "
             "scope rule, which cannot both be honoured as things stand.")
    out = mod.derive_still_owed(probe)
    assert "*" not in out, out


def test_the_frame_does_not_coerce_a_copula_or_double_the_stop(mod):
    """Defect 4, and it bites the AUTHORED value too, not only the derived."""
    #: ★ THE SEAT'S `_as_statement` RETURNED THE BARE STATEMENT; the live
    #: helper is `_owed_sentence` and returns the WHOLE sentence including its
    #: lead, so the equality is rewritten against that contract. The seat's
    #: probe earned its place regardless: a VERB-initial value exposed a gap
    #: its author did not name, since the orchestrator's copula test was a
    #: word list of pronouns and determiners and produced "What is still owed
    #: is ends in a stop." A word list cannot enumerate English; the colon
    #: form is now used unconditionally and there is nothing left to classify.
    got = mod._owed_sentence("ends in a stop.")
    assert got == "What is still owed: ends in a stop.", got
    assert " is ends " not in got, got
    #: The same contract difference: the live helper frames, and an EMPTY
    #: value is deliberately not silence -- it falls back to the honest
    #: *"recorded in the entry"*, because an entry he is being asked to decide
    #: must not have nothing said about what it owes.
    assert mod._owed_sentence("no stop") == "What is still owed: no stop."
    for empty in ("", None):
        got = mod._owed_sentence(empty)
        assert got == "What is still owed is recorded in the entry.", got


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
    assert "fresh answer".lower() in out.lower(), out
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


# ─────────────────────────────────────────────────────────────────────────────
# THE SEAT'S OWN PRODUCER MUST BE EXECUTED BY SOMETHING.
#
# ★ THE COMMIT GATE CAUGHT THIS, 2026-11-10. Adopting a seat's producer into
# `scripts/` without a test that runs it makes it an addition nothing reaches,
# which `additive-standard`'s symmetric form forbids. The guard that noticed --
# `test_an_unreached_producer_set_cannot_grow_2026-11-08.py` -- says so in its
# own words: *re-pinning to silence this is how a ratchet becomes a rubber
# stamp*. So the producer is RUN here rather than admitted to an exempt list.
# ─────────────────────────────────────────────────────────────────────────────

def test_the_seats_producer_runs_in_this_tree():
    import subprocess
    import sys as _sys
    prod = (REPO / "scripts"
            / "a_derived_owed_line_is_cut_at_an_emphasis_2026-11-10.py")
    assert prod.is_file(), f"the adopted producer is absent: {prod}"
    r = subprocess.run([_sys.executable, str(prod)], capture_output=True,
                       text=True, timeout=300, cwd=str(REPO))
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-600:]
    assert r.stdout.strip(), "the producer printed nothing"


def test_the_seats_producer_answers_help_for_free():
    import subprocess
    import sys as _sys
    import time as _time
    prod = (REPO / "scripts"
            / "a_derived_owed_line_is_cut_at_an_emphasis_2026-11-10.py")
    t0 = _time.monotonic()
    r = subprocess.run([_sys.executable, str(prod), "--help"],
                       capture_output=True, text=True, timeout=30,
                       cwd=str(REPO))
    assert r.returncode == 0, r.stderr[-600:]
    assert _time.monotonic() - t0 < 5.0, "a --help must never cost minutes"
