"""Rule 6 forbids phonetic path spelling in a TTS file, and nothing checked it.

WHY THIS FILE EXISTS. Ticket `pf:c31e41410ec2` records a delivered TTS note
carrying `python3 scripts slash register.py minus minus kind wr minus minus
status OPEN minus minus limit 0`. The note standard's Rule 6 forbids exactly
that -- a path is named as a noun with a brief locator, never spelled out -- and
`scripts/note_vagueness_lint.py` reported 0 findings on it, because it had no
check for phonetic punctuation at all. His own annotation on it asked whether
this was a weird new kind of word numbering and, if not justified, to fix it.
The rule actually broken is Rule 6 rather than `no-word-numbers`: no number is
spelled in that string.

WHY A NARROW PATTERN, AND HOW THAT WAS ESTABLISHED BEFORE THE RULE WAS WRITTEN.
Rule 30, `undefined-project-term`, is REPORTED and deliberately NOT blocking,
because its own measurement showed it cannot separate a coinage from ordinary
noun-plus-noun English: 544 of 869 instances across 523 notes, 62.6007 per cent.
A rule that accuses correct prose gets switched off, which is the failure this
project has already paid for once. So this pattern was measured against the
whole corpus FIRST, on 2026-11-08:

  * 82 of 913 TTS files fire, 0.089814, Wilson 95% [0.072946, 0.110119],
    Clopper-Pearson [0.072068, 0.110256], over 926 match instances.
  * 12 of 12 randomly sampled instances are GENUINE violations -- `bench slash
    immune underscore agents dot py`, `home slash dot claude slash CLAUDE dot
    md`, `40 gate dot j s o n` -- and not one is ordinary prose. Phonetic
    punctuation is simply not something English prose does, which is why this
    pattern separates where Rule 30's cannot.
  * 0 files both FIRE and discuss Rule 6 or phonetic spelling, so the
    self-accusation trap recorded in
    `feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02` does
    not arise in the corpus -- and the check runs on QUOTE-MASKED text, so a
    future note quoting a bad form in order to correct it stays exempt.

THE RATCHET CONSEQUENCE WAS CHECKED RATHER THAN ASSUMED. `hooks/pre-commit`
counts every finding, not only the blocking partition -- that mismatch is open
as `pf:71b0c675fa22` -- so a new rule becomes effectively blocking. It does NOT
retroactively block the 82, because the ratchet compares HEAD's lint against the
staged lint with the SAME rule set, so the delta on an untouched note is 0.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LINT = REPO / "scripts/note_vagueness_lint.py"

#: The exact string from the delivered note the ticket was raised on.
HIS_CASE = ("python3 scripts slash register.py minus minus kind wr "
            "minus minus status OPEN minus minus limit 0")
LABEL = "PHONETIC PATH"


def _module():
    """A fresh copy, so setting the logical-path global cannot leak."""
    spec = importlib.util.spec_from_file_location("_lint_under_test", LINT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _findings(body: str, name: str, tmp_path) -> list:
    """Lint `body` as though it were the note at `name`."""
    mod = _module()
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    #: THE LOGICAL PATH MUST CARRY `experimental_notes`, because `_is_tts`
    #: requires that component or a `*_tts` directory. A bare filename makes
    #: the gate refuse and every positive assertion below fail for the wrong
    #: reason -- which is exactly what the first version of this file did.
    mod._LOGICAL_PATH = f"experimental_notes/{name}"
    return [f for f in mod.lint(p) if LABEL in str(f[1])]


class TestThePatternSeesHisCase:
    def test_the_fixture_is_the_string_from_the_ticket(self):
        """ANTI-VACUITY ON THE FIXTURE. If this string ever stops carrying
        phonetic punctuation, every assertion below passes while testing
        nothing -- the probe-manufactured failure of 2026-11-02 in reverse."""
        assert "minus minus" in HIS_CASE
        assert "slash" in HIS_CASE

    def test_a_tts_note_spelling_a_path_is_flagged(self, tmp_path):
        got = _findings(f"A line.\n\n{HIS_CASE}\n", "N_2026-11-08.txt", tmp_path)
        assert got, f"Rule 6 violation not flagged in a .txt note: {HIS_CASE!r}"

    @pytest.mark.parametrize("bad", [
        "the file at bench slash immune underscore agents dot py",
        "the config is 40 gate dot json",
        "run it with minus minus write",
    ])
    def test_each_phonetic_form_is_flagged(self, bad, tmp_path):
        assert _findings(f"Context.\n\n{bad}\n", "N_2026-11-08.txt", tmp_path)


class TestItDoesNotAccuseCorrectProse:
    @pytest.mark.parametrize("ok", [
        "The producer reports 13 of 165 invisible, and the count is the figure to read.",
        "A guard that accuses correct prose gets switched off.",
        "The entry names its evidence and the evidence resolves in HEAD.",
    ])
    def test_ordinary_prose_is_not_flagged(self, ok, tmp_path):
        """NEGATIVE CONTROL. Without this the rule above could match anything."""
        assert not _findings(f"Context.\n\n{ok}\n", "N_2026-11-08.txt", tmp_path)

    def test_a_markdown_note_is_out_of_scope(self, tmp_path):
        """Rule 6 governs the SPOKEN file. A markdown note writes real paths in
        backticks by design, and flagging those would make the rule absurd."""
        assert not _findings(f"Context.\n\n{HIS_CASE}\n",
                             "N_2026-11-08.md", tmp_path)

    def test_a_quoted_bad_form_is_exempt(self, tmp_path):
        """A note naming the fault in order to correct it is not committing it.
        `feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02`."""
        body = f'Context.\n\nThe note carried "{HIS_CASE}", which Rule 6 forbids.\n'
        assert not _findings(body, "N_2026-11-08.txt", tmp_path)
