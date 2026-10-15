"""Rule 30: a note may not use a compound term that exists nowhere in the project.

THE DEFECT THIS GUARDS, AND IT IS THE FOUNDER'S COMPLAINT TWICE IN ONE DAY. "You
are using non-project terms again. You said you had fixed it so you would stop."
And, separately: "What is the 'discrimination guard'? I am unfamiliar with this
term. Is it official project terminology?"

AND HIS TEST OF WHETHER A FIX IS A FIX: "Is 'the lesson is recorded' the same as
saying the problem that caused it has now been fixed? Because if not you should
probably also fix the cause rather than just record the symptom." Recording the
lesson was what had been done before; this is the cause.

MEASURED, 4 terms used to him on 2026-10-15:
    coherence budget      0 glossary, 4 docs files -> REAL but UNDEFINED
    discrimination guard  0 glossary, 0 docs files -> COINED IN A NOTE
    paired baseline       0 glossary, 0 docs files -> COINED IN A NOTE
    consequence gate      0 glossary, 0 docs files -> COINED IN A NOTE
Both halves are treated: the coined terms are refused, and `coherence budget`
plus `coherence budget recalibration` were written into `docs/GLOSSARY.md` with
code anchors, so using them is legitimate and a reader can look them up.

THE 2 DESIGN DECISIONS THAT MAKE IT WORK, both fitted rather than chosen:

  1. THE VOCABULARY EXCLUDES `experimental_notes/` AND THE LINT'S OWN SOURCE. A
     term invented in a note yesterday must not legitimise itself today. A first
     version read every .py file whole and came out VACUOUS -- all 4 terms were
     "in vocabulary" because this rule's own explanatory comment names them.
  2. THE PATTERN REQUIRES THE DEFINITE ARTICLE. A bare "<word> <noun>" test gave
     2,841 findings over 426 of 523 notes, mostly grammatical accident ("and
     gate", "now gate"). A coined term arrives as a definite noun phrase, which
     is how the founder met all 4. With "the" required: 734 findings over 243 of
     523 notes.

IT IS A RATCHET, NOT A RETROSPECTIVE BLOCK. 734 instances already exist, so
blocking on the absolute count would refuse 46.46% of the project's own archive
and teach its reader that the checker is noise. Notes written from now carry 0.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import note_vagueness_lint as lint  # noqa: E402


def _note(tmp_path: pathlib.Path, body: str) -> pathlib.Path:
    p = tmp_path / "Note_2026-10-15.md"
    p.write_text(
        "A note.\n\n2026-10-15 23:00 BST\n\n" + body
        + "\n\nWritten under CDSFL note standard v1.7 (26 August 2026).\n"
    )
    return p


# --------------------------------------------------------------------------
# It fires on a coined term.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "the discrimination guard",
    "the consequence gate",
    "the speculative tripwire",
])
def test_a_coined_term_is_a_finding(tmp_path, phrase):
    p = _note(tmp_path, f"In round 3 {phrase} refused the copy.")
    found = lint.undefined_project_terms(p)
    assert found, f"{phrase!r} was not flagged"
    assert any(kind == "undefined-project-term" for _, kind, _, _ in found)


# --------------------------------------------------------------------------
# It does NOT fire on the project's own vocabulary.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "the coherence budget",       # defined in GLOSSARY.md on 2026-10-15
    "the skin barrier",           # a real immune-pipeline mechanism
    "the capability ladder",      # a real seat-model mechanism
    "the convergence gate",       # the project's central mechanism
])
def test_real_project_vocabulary_is_not_flagged(tmp_path, phrase):
    p = _note(tmp_path, f"In round 3 {phrase} did its work.")
    flagged = {t for _, _, t, _ in lint.undefined_project_terms(p)}
    bare = phrase.removeprefix("the ")
    assert bare not in flagged, f"{phrase!r} is real and was flagged"


def test_grammatical_accidents_are_not_flagged(tmp_path):
    """The reason the definite article is in the pattern."""
    p = _note(tmp_path, "It passed and gate checks ran. Now gate timing held. "
                        "The test baseline was unchanged.")
    flagged = {t for _, _, t, _ in lint.undefined_project_terms(p)}
    for accident in ("and gate", "now gate", "test baseline"):
        assert accident not in flagged, f"{accident!r} is not a coined term"


# --------------------------------------------------------------------------
# The vocabulary must not be able to legitimise a coinage.
# --------------------------------------------------------------------------

def test_the_vocabulary_excludes_notes():
    """A term coined in a note must not become vocabulary by being in a note.

    Asserted by content, not by reading the function: a phrase that appears in
    `experimental_notes/` and nowhere else must be absent from the vocabulary.
    """
    vocab = lint.project_vocabulary()
    notes_dir = REPO / "experimental_notes"
    if not notes_dir.is_dir():
        pytest.skip("no experimental_notes/ in this checkout")
    # `discrimination guard` is used in the 2026-10-15 notes and nowhere else.
    assert "discrimination guard" not in vocab


def test_the_vocabulary_excludes_the_lints_own_source():
    """This rule's own comment names all 4 terms; admitting it is vacuity."""
    vocab = lint.project_vocabulary()
    own = pathlib.Path(lint.__file__).read_text(errors="ignore").lower()
    assert "discrimination guard" in own, (
        "the rule's own comment should cite the term it was built for"
    )
    assert "discrimination guard" not in vocab, (
        "the lint is reading its own source as vocabulary — the rule is vacuous"
    )


# --------------------------------------------------------------------------
# Wiring. A rule reached by nothing is not additive.
# --------------------------------------------------------------------------

def test_the_rule_is_REPORTED_and_not_blocking(tmp_path):
    """★ SCOPED BY MEASUREMENT AFTER IT REFUSED A COMPLIANT NOTE (2026-10-15).

    Rule 30 was wired into `blocking()` first, and within the hour it blocked
    this session's own technical note on 9 findings of which 1 was a genuine
    coinage. The rest were ordinary descriptive English ending in a term noun:
    "pinned threshold", "committed baseline", "abstract verifier".

    There is no structural difference between "pinned threshold", which is a
    description, and "paired baseline", which is a coinage the founder
    challenged, so the rule cannot separate them. Measured over 523 notes: 869
    instances, of which a suffix heuristic puts 325 in the adjectival class.
    Gating at that precision would refuse roughly 1 note in 2.

    The capability is intact: the rule runs, reports through the command line,
    and carries a committed ratchet. Only the gate coupling changed. It returns
    to `blocking()` when it can tell a coinage from an adjective.
    """
    p = _note(tmp_path, "In round 3 the discrimination guard refused the copy.")
    assert lint.undefined_project_terms(p), "the rule must still FIND it"
    kinds = {k for _, k, _, _ in lint.blocking(p)}
    assert "undefined-project-term" not in kinds, (
        "Rule 30 is back in the blocking set; if that was intended, the comment "
        "in blocking() and this test must be updated together"
    )


def test_the_rule_is_wired_into_the_command_line(tmp_path, capsys):
    """`main()` calls partition() directly, so a rule added only to blocking()
    reports 0 findings to a human reader. That exact defect is recorded in this
    file's own history for the note-standard stamp check."""
    p = _note(tmp_path, "In round 3 the discrimination guard refused the copy.")
    argv = sys.argv
    try:
        sys.argv = ["note_vagueness_lint.py", str(p)]
        rc = lint.main()
    finally:
        sys.argv = argv
    out = capsys.readouterr().out
    assert "undefined-project-term" in out, (
        "the command line does not report Rule 30"
    )
    # ★ THE EXIT CODE IS DELIBERATELY 0, AND THAT IS THE TOOL'S DESIGN, NOT A
    # DEFECT. `main()` is the human-readable report and its own comment states
    # the split: "Findings stay advisory; a file that was never READ does not."
    # Only an unreadable path exits non-zero, so a typo cannot read as a clean
    # note. The BLOCKING surface is `blocking()`, which a guard calls and which
    # Rule 30 is wired into (see the test above).
    #
    # A first version of this test asserted `rc != 0`. That encoded CC1's
    # expectation rather than the design, and changing a shared tool's exit
    # semantics to satisfy a test written minutes earlier would be the wrong way
    # round. If the founder wants the CLI to gate, that is his ruling to give.
    assert rc == 0, (
        "the report path changed its exit semantics; if that was intended, the "
        "comment in main() and this test both need updating together"
    )


def test_the_ratchet_baseline_is_recorded():
    """The historical count is a committed number, so it can only fall."""
    assert lint.RULE30_RATCHET_BASELINE == 869
    assert lint.RULE30_RATCHET_NOTES == 263

def test_deprecating_a_coinage_does_not_legitimise_it():
    """★ THE FOURTH SELF-LEGITIMISING PATH, and it only appears once the rule
    works. Writing in the glossary that a mechanism "had been called the
    confinement guard, which is not its name" ADMITTED that phrase as
    vocabulary, so the rule stopped flagging the very term the entry existed to
    deprecate. A line carrying the coinage marker is dropped from the
    vocabulary, which is the only way the glossary can say "this is not what it
    is called" without making it what it is called.
    """
    vocab = lint.project_vocabulary()
    glossary = (REPO / "docs" / "GLOSSARY.md")
    if not glossary.is_file():
        pytest.skip("no glossary in this checkout")
    raw = glossary.read_text(errors="ignore").lower()
    assert "confinement guard" in raw, (
        "the glossary should still TELL a reader the coinage is not the name"
    )
    assert lint._COINAGE_MARKER in glossary.read_text(errors="ignore"), (
        "the glossary names a coinage without marking it, so the vocabulary "
        "will absorb it"
    )
    assert "confinement guard" not in vocab, (
        "a deprecated coinage was absorbed into the vocabulary; the rule can no "
        "longer flag the term its own glossary entry deprecates"
    )
    assert "audit observer" in vocab, (
        "the REAL name must be vocabulary, or the rule flags correct usage"
    )


def test_the_coinage_marker_drops_only_the_marked_line():
    kept = lint._drop_coinage_lines(
        "real term one\nbogus term [coinage] here\nreal term two")
    assert "real term one" in kept and "real term two" in kept
    assert "bogus term" not in kept
