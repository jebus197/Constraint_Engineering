"""Task R10: the reading his own precondition required, delivered as a file.

He deferred the references selection to a discussion CONDITIONAL on both parties
having read the sources first, then the reading was delivered in conversation
only. A condition that cannot be met is not a deferral, it is a stall.

THE CLAIMS ARE EXECUTED, NOT QUOTED. The note asserts that all 4 reduction
branches are regular limits. That is not taken on the note's word: the test runs
`scripts/verify_paper_reduction_properties.py` and requires it to pass. A reading
put in front of the founder whose central claim had quietly gone stale would be
worse than no reading.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
NOTE = ROOT / "experimental_notes" / "Reductionism_Reading_2026-09-10.md"
TTS = pathlib.Path.home() / "Desktop" / "CDSFL_tts" / "Reductionism_Reading_2026-09-10.txt"
VERIFY = ROOT / "scripts" / "verify_paper_reduction_properties.py"


def test_the_note_exists_in_the_repository():
    assert NOTE.is_file(), (
        "the reading exists only in conversation again, which is the defect R10 "
        "was raised for")


def test_all_three_traditions_are_named_with_their_roles():
    """Naming only the chosen one would hide the reasoning behind the choice."""
    t = NOTE.read_text(encoding="utf-8")
    for who in ("Nagel", "Nickles", "Batterman"):
        assert who in t, f"{who} is not named"
    assert "1973" in t and "181" in t, "the Nickles citation is not resolvable"


def test_the_central_claim_still_executes():
    """The 4 branches are REGULAR limits, or the Batterman objection lands."""
    r = subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-500:]
    assert "REGULAR limit" in r.stdout, (
        "the script no longer reports on regularity, so the note's central "
        "claim is no longer discharged by it")
    assert r.stdout.count("[PASS]") >= 7


def test_the_note_does_not_overstate_what_was_confirmed():
    """2 of the 5 paper claims were REFUTED. A reading that hid that would be
    advocacy, not a reading."""
    t = NOTE.read_text(encoding="utf-8")
    assert "2 were refuted" in t or "2 refuted" in t, (
        "the note no longer records that 2 of the 5 executed claims failed")
    assert "0.58016" in t, "the concrete counter-example was dropped"


class TestTheSpokenCopy:
    """Skipped where the Desktop is absent; the .txt is deliberately unversioned."""

    def test_it_exists(self):
        if not TTS.is_file():
            pytest.skip("no Desktop TTS copy on this machine")
        assert TTS.stat().st_size > 2000

    def test_it_carries_no_markup_a_reader_would_speak_aloud(self):
        """The founder is dyslexic and this file is read aloud by software.

        A hash, an asterisk or a backtick is either spoken as a noise or
        swallowed. This is checked rather than trusted, because the rule has been
        stated repeatedly and the checker is what actually enforces it.
        """
        if not TTS.is_file():
            pytest.skip("no Desktop TTS copy on this machine")
        text = TTS.read_text(encoding="utf-8")
        for ch, name in (("#", "hash"), ("*", "asterisk"), ("`", "backtick"),
                         ("|", "pipe"), ("—", "em-dash"), ("_", "underscore")):
            assert ch not in text, (
                f"the spoken copy contains a {name}, which text-to-speech "
                f"either voices as noise or drops")
