"""The founder-responses reader must read every kind, and its fallback must not rot.

★ 3 DEFECTS FOUND 2026-11-14 WHILE VERIFYING B184, the entry on `frx` becoming a
ticket kind of its own. B184 reports that his FIRST USE of `frx` was invisible to
the marker meant to read it, and that the suffix was widened to fix it. **It
widened 1 of the 2 readers.**

  1. `scripts/read_founder_responses_2026-10-11.py` -- the reader that actually
     parses his annotation files -- could not see his first `frx`. His words
     were *"As I said above you should fix both. frx (as you will note this is
     my first use of the fix request ticket classification.)"*: the marker is
     followed by a parenthetical, so it is neither the whole line nor the
     trailing token. Driven: the harvester returned `frx`, both of this file's
     patterns returned None, and `annotations()` reported a blank marker.

  2. **IT WAS MASKED, WHICH IS WHY IT SURVIVED.**
     `scripts/harvest_tickets_2026-10-17.py:432` re-applies its own MARKER when
     the reader's field is empty, so the TICKET was filed correctly as `frx` and
     nothing downstream complained. 3 other production consumers read the
     reader's field directly and saw his fix request as unmarked.

  3. **THE FALLBACK VOCABULARY HAD GONE STALE AND SILENTLY.** `_HIS_KINDS` is
     imported from `ticket_store.KINDS`, with a literal tuple used only when the
     import fails -- and that literal omitted `frx`. So on exactly the run where
     nothing else is available to notice, his newest marker became unreadable.
     A fallback that is stale is worse than no fallback, because it looks like
     coverage.

★ THE REPAIR WAS A DELETION, NOT A CHECKER. 2 of this file's patterns each
spelled the 9 kinds out twice. They now derive from `_KIND_ALT`, which removes 4
re-spellings; a derived pattern cannot diverge, and under `simplicity-default` a
deletion beats a comparator that has to be kept honest.

★ THE WIDENING WAS MEASURED BEFORE IT WAS MADE, because adding to an accepting
pattern is a LOOSENING: over all 895 of his annotations it changes exactly 1
verdict and that 1 is his own sentence; 0 verdicts lost, 0 false positives.

EXECUTES the patterns and the import-failure path. The 1 unavoidable source
assertion is marked as such and says why.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from bench.ticket_store import KINDS  # noqa: E402

READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"

HIS_FRX = ("As I said above you should fix both. frx (as you will note this is "
           "my first use of the fix request ticket classification.)")


def _load(name: str = "rdr_vocab_guard"):
    spec = importlib.util.spec_from_file_location(name, READER)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


R = _load()


def test_his_first_frx_is_read_by_the_reader_too():
    """★ THE LOAD-BEARING ONE. His own sentence, byte-exact."""
    m = R._MARKER_TRAILING.search(HIS_FRX)
    assert m is not None, (
        "the reader cannot see his first use of `frx`. B184 widened the "
        "harvester for this exact sentence; this is the other reader.")
    assert m.group(1).strip().lower() == "frx"


def test_the_annotations_path_reports_it_not_just_the_pattern():
    """A pattern that matches while the public path reports blank fixes nothing."""
    hits = [a for a in R.annotations()
            if "first use of the fix request" in (a.get("text") or "")]
    assert hits, "his frx annotation is no longer being read at all"
    assert all((a.get("marker") or "").strip().lower() == "frx" for a in hits), \
        [a.get("marker") for a in hits]


def test_every_kind_the_store_declares_is_readable_by_the_reader():
    """The reader's job is the OPPOSITE of the harvester's: it must read EVERY
    kind, the default-only ones included, because he writes them explicitly."""
    unreadable = []
    for k in KINDS:
        if not R._MARKER_LINE.match(k):
            unreadable.append((k, "_MARKER_LINE"))
        if not R._MARKER_TRAILING.search(f"some sentence of his. {k}"):
            unreadable.append((k, "_MARKER_TRAILING"))
        if not R._ENDS_IN_HIS_MARKER.search(f"some sentence of his {k}"):
            unreadable.append((k, "_ENDS_IN_HIS_MARKER"))
    assert not unreadable, f"kinds unreadable by a reader pattern: {unreadable}"


def test_the_longer_kind_is_not_swallowed_by_its_own_prefix():
    """`fr` is a prefix of `frx`. Longest-first makes this correct by
    construction rather than correct by the engine backtracking."""
    m = R._MARKER_TRAILING.search("do both. frx")
    assert m and m.group(1).strip().lower() == "frx"
    assert R._MARKER_LINE.match("frx").group(1).lower() == "frx"


def test_a_token_that_merely_starts_with_a_kind_is_not_a_marker():
    for bad in ("frxy", "framework", "disconnect", "stmt"):
        assert not R._MARKER_LINE.match(bad), bad
        assert not R._MARKER_TRAILING.search(f"a sentence about {bad}"), bad


def test_a_WORD_ENDING_IN_A_KIND_IS_NOT_A_MARKER():
    """★ ADDED BECAUSE THE MUTATION HARNESS CAUGHT ITS ABSENCE, not because it
    was foreseen -- the 3rd time tonight a harness found a missing assertion
    rather than a broken fix.

    The test above covers words that START with a kind, and the TRAILING suffix
    already rejects those on its own: `frx` followed by `y` is neither
    end-of-string nor a bracket. So dropping the LEADING boundary left that test
    green while the pattern became wrong in the other direction.

    What the leading boundary actually protects is a word whose last letters ARE
    a kind. Driven: without it, `"this is unfr"` reads as `fr` and `"we codisc"`
    reads as `disc`. Those are ordinary English endings, so an annotation of his
    that happened to finish on one would acquire a marker he never wrote -- and
    a marker he never wrote routes his words to the wrong queue.
    """
    for bad in ("unfr", "codisc", "transfr", "sufferds"):
        assert not R._MARKER_TRAILING.search(f"this is {bad}"), (
            f"{bad!r} was read as a marker; the leading word boundary is gone")
    # and the boundary must not break the legitimate forms it sits beside
    for good, want in (("do both. frx", "frx"), ("no comment pf", "pf"),
                       ("explain it qs", "qs")):
        m = R._MARKER_TRAILING.search(good)
        assert m and m.group(1).strip().lower() == want, (good, m and m.group(1))


def test_a_marker_at_the_very_end_still_reads_after_the_widening():
    """NON-REGRESSION: the widening must ADD a form, never replace one."""
    for probe, want in [("you should do it. fr", "fr"),
                        ("please explain qs", "qs"),
                        ("verdict. yes do both. stm", "stm"),
                        ("fix it pf.", "pf")]:
        m = R._MARKER_TRAILING.search(probe)
        assert m and m.group(1).strip().lower() == want, (probe, m and m.group(1))


def test_the_parenthetical_form_does_not_admit_a_marker_mid_sentence():
    """The widening allows a marker before a TRAILING bracket, not anywhere."""
    assert not R._MARKER_TRAILING.search(
        "the fr request was discussed and then we moved on to other matters")


def test_the_fallback_vocabulary_equals_the_store_EXECUTED_not_grepped():
    """★ THE STALE-FALLBACK DEFECT, driven by making the import fail.

    `_HIS_KINDS` comes from `ticket_store.KINDS` with a literal used only when
    that import raises. The literal had gone stale, omitting `frx`. This test
    forces the failure path and compares what the module then holds against the
    store, so the literal cannot rot again.
    """
    saved = {k: v for k, v in sys.modules.items() if k.startswith("bench.ticket_store")}
    sys.modules["bench.ticket_store"] = None          # import raises TypeError
    try:
        broken = _load("rdr_vocab_guard_nofallback")
        assert set(broken._HIS_KINDS) == set(KINDS), (
            f"the fallback literal is stale: missing {sorted(set(KINDS) - set(broken._HIS_KINDS))}, "
            f"extra {sorted(set(broken._HIS_KINDS) - set(KINDS))}. On a run where "
            f"the import fails, those kinds become unreadable and nothing else "
            f"is available to notice.")
    finally:
        sys.modules.pop("bench.ticket_store", None)
        sys.modules.update(saved)
        sys.modules.pop("rdr_vocab_guard_nofallback", None)


def test_the_alternation_is_derived_rather_than_respelled():
    """A SOURCE assertion, and the only one here, because the thing asserted is
    the ABSENCE of a duplicate -- which no execution can observe. A second
    hardcoded alternation behaves identically until the day it drifts, which is
    the `execute-do-not-grep` shape in the one direction execution cannot see."""
    src = READER.read_text(encoding="utf-8")
    spelled = src.count("frx|fr|pf|qs|wr|stm")
    assert spelled == 0, (
        f"{spelled} hardcoded copies of the kind alternation are back in the "
        f"reader. Derive from `_KIND_ALT`; a re-spelling drifts the next time a "
        f"kind is added, which cost a refused commit board on 2026-11-13.")
    assert "_KIND_ALT" in src


def test_the_live_corpus_still_reads_at_the_expected_shape():
    """NON-VACUITY on his real files: 895 annotations and exactly 1 `frx`."""
    rows = R.annotations()
    assert len(rows) >= 895, f"only {len(rows)} annotations read; the reader regressed"
    frx = [a for a in rows if (a.get("marker") or "").strip().lower() == "frx"]
    assert len(frx) == 1, f"{len(frx)} frx annotations; expected exactly his 1"
