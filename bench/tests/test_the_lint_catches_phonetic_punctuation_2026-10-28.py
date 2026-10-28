#!/usr/bin/env python3
r"""Rule 14a is reached for the first time: phonetic punctuation in a TTS file.

HIS FINDING, 2026-10-28, reading a TTS file of mine that carried "python3
scripts slash register.py minus minus kind wr minus minus status OPEN minus
minus limit 0": *"This is a weird new kind of 'word numbering'? Is it justified
here for some reason? If not you should probably look at it and fix it, as per
our 'no word numbers' rule."*

HIS DIAGNOSIS NAMES THE WRONG RULE AND HIS FINDING IS STILL CORRECT, and the
distinction is load-bearing because the 2 rules want different fixes. Nothing in
that line spells a NUMBER, so `no-word-numbers` does not apply to it. What is
spelled is PUNCTUATION, which Rule 14a of v1.3 governs -- *"identifiers keep
their name, lose the punctuation"* -- together with the standing TTS
no-underscores rule. The file passed the lint at 0 findings because no check
could see phonetic punctuation at all, which is why this file exists rather than
a restatement of the rule.

MEASURED BEFORE THE RULE WAS ADDED, because a rule that reddens the corpus on
the day it lands is a rule that gets switched off: 802 occurrences across 86 of
1,392 scanned files, 0.061782 Wilson [0.050300, 0.075675]. It is a long habit.
`minus minus` is the one genuinely new form -- 3 occurrences in 1 file, the one
he was reading. The commit ratchet is per file, so the 86 are grandfathered
until something edits them.

SCOPED TO TTS DELIBERATELY. A markdown companion writes a path literally and
must keep doing so; firing there would be a false positive on correct work. The
companion to the very file he objected to still carries
`python3 scripts/register.py --kind wr --status OPEN --limit 0` verbatim, and
that is right.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LINT = REPO / "scripts" / "note_vagueness_lint.py"


@pytest.fixture(scope="module")
def nl():
    spec = importlib.util.spec_from_file_location("note_lint_phon", LINT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["note_lint_phon"] = m
    spec.loader.exec_module(m)
    return m


def _tts(tmp_path: pathlib.Path, body: str) -> pathlib.Path:
    d = tmp_path / "CDSFL_tts"
    d.mkdir(exist_ok=True)
    p = d / "Probe_2026-10-28.txt"
    p.write_text(body, encoding="utf-8")
    return p


def _labels(findings):
    return [f[1] for f in findings]


@pytest.mark.parametrize("body,shape", [
    ("The count is reproducible with python3 scripts slash register.py today.",
     "a spoken path separator"),
    ("Run it with minus minus status OPEN and read the result.",
     "a spoken double dash"),
    ("The producer is the register dot py file in the tree.",
     "a spoken file extension"),
    ("The checker is called note underscore vagueness underscore lint today.",
     "a spoken underscore"),
])
def test_each_phonetic_shape_is_caught(nl, tmp_path, body, shape):
    found = nl.lint(_tts(tmp_path, body))
    phon = [f for f in found if "PHONETIC PUNCTUATION" in f[1]]
    assert phon, f"{shape} was not caught in {body!r}; findings: {_labels(found)}"
    assert shape in phon[0][1], f"caught, but labelled {phon[0][1]!r}"


def test_the_exact_line_he_objected_to_is_caught(nl, tmp_path):
    """The regression case, in his own words rather than a paraphrase."""
    body = ("That count is reproducible from the register itself with the "
            "command: python3 scripts slash register.py minus minus kind wr "
            "minus minus status OPEN minus minus limit 0.")
    found = nl.lint(_tts(tmp_path, body))
    assert any("PHONETIC PUNCTUATION" in f[1] for f in found), (
        f"the line he objected to still passes; findings: {_labels(found)}")


def test_a_markdown_companion_is_not_touched(nl, tmp_path):
    """FALSE-POSITIVE GUARD, and it is DISCRIMINATING -- a mutation test proved
    the first version was not.

    That version used a markdown file carrying a LITERAL path, which the rule
    correctly ignores whatever its scope is, so inverting `_is_tts` to fire on
    markdown left this test GREEN. A guard that cannot fail in the direction it
    exists to guard is an addition nothing reaches. The body below now carries
    text that WOULD match a phonetic shape, so only the TTS scope test can be
    what suppresses it.
    """
    d = tmp_path / "experimental_notes"
    d.mkdir(exist_ok=True)
    p = d / "Probe_2026-10-28.md"
    p.write_text(
        "The producer is register dot py and the flag is minus minus status, "
        "written out here because a markdown note discusses the forms a TTS "
        "file may not use.\n", encoding="utf-8")
    found = nl.lint(p)
    assert not [f for f in found if "PHONETIC PUNCTUATION" in f[1]], (
        f"the rule fired on a markdown file. Rule 14a governs TTS; a markdown "
        f"note writes paths and flags literally and discusses the banned forms "
        f"by name: {found}")


def test_a_literal_path_in_a_tts_file_is_not_the_target(nl, tmp_path):
    """Rule 6 is a separate rule. This one is only about SPOKEN punctuation,
    so a literal path must not trip THIS check and produce 2 findings for 1
    fault."""
    body = "The producer is scripts/register.py in the tree.\n"
    found = nl.lint(_tts(tmp_path, body))
    assert not [f for f in found if "PHONETIC PUNCTUATION" in f[1]], (
        f"a literal path tripped the phonetic check: {found}")


def test_a_quoted_violation_is_not_a_violation(nl, tmp_path):
    """The standing exemption. A note naming a bad form in order to correct it
    is doing the opposite of committing the fault -- this linter's own header
    warns that firing on the document explaining the rule gets it ignored."""
    body = ('He objected to "python3 scripts slash register.py" in the file.\n')
    found = nl.lint(_tts(tmp_path, body))
    assert not [f for f in found if "PHONETIC PUNCTUATION" in f[1]], (
        f"a quoted example was counted as a violation: {found}")


def test_the_delivered_file_he_read_is_now_clean(nl):
    """END TO END on the real artefact, not a fixture."""
    p = pathlib.Path.home() / "Desktop" / "CDSFL_tts" / \
        "Overnight_Work_Blocked_On_Login_2026-10-28.txt"
    if not p.is_file():
        pytest.skip("the delivered TTS file is not on this machine")
    found = nl.lint(p)
    assert not [f for f in found if "PHONETIC PUNCTUATION" in f[1]], (
        f"the file he objected to still carries phonetic punctuation: {found}")


def test_the_rule_is_wired_into_the_dispatcher(nl):
    """ANTI-VACUITY. A rule table nothing reads is an addition nothing reaches."""
    assert hasattr(nl, "PHONETIC_PUNCT"), "the rule table is gone"
    assert len(nl.PHONETIC_PUNCT) >= 4, (
        f"only {len(nl.PHONETIC_PUNCT)} shape(s) declared; 4 were measured in "
        f"the corpus")
    assert hasattr(nl, "_is_tts"), "the TTS scope test is gone"
