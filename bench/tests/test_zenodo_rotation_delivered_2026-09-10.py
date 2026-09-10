"""Task Z1: the commands he asked for on 2026-08-19, finally delivered.

He asked, verbatim: "You need to give me clear instructions how to do this!"
They were never supplied. 22 days.

THE INSTRUMENT MUST NEVER PRINT THE TOKEN. Not in output, not in an error, not in
a traceback. A rotation tool that echoes the credential it is rotating would be
worse than no tool, so that is asserted rather than intended.

IT IS OFFLINE BY DEFAULT. This project's suite runs under --netguard-strict, and
a script that reaches the network unasked cannot run inside it.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "zenodo_token_check.py"
NOTE = ROOT / "experimental_notes" / "Zenodo_Token_Rotation_2026-09-10.md"
TTS = (pathlib.Path.home() / "Desktop" / "CDSFL_tts"
       / "Zenodo_Token_Rotation_2026-09-10.txt")


def _token():
    env = ROOT / ".env"
    if not env.is_file():
        return None
    for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip().removeprefix("export ")
        if line.startswith("ZENODO_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


class TestTheTokenNeverLeaks:
    def test_the_checker_does_not_print_it(self):
        tok = _token()
        if not tok:
            pytest.skip("no ZENODO_TOKEN in .env on this machine")
        r = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        assert tok not in r.stdout and tok not in r.stderr, (
            "the checker printed the token")
        assert tok[8:] not in r.stdout, "it printed most of the token"

    def test_it_prints_only_a_short_prefix(self):
        tok = _token()
        if not tok:
            pytest.skip("no ZENODO_TOKEN in .env on this machine")
        r = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        shown = re.search(r"starts (\w+)\.\.\.", r.stdout)
        assert shown, r.stdout
        assert len(shown.group(1)) <= 6, (
            f"{len(shown.group(1))} characters of the token are shown; that is "
            f"more than 'a paste landed' needs")

    def test_no_delivered_document_contains_it(self):
        tok = _token()
        if not tok:
            pytest.skip("no ZENODO_TOKEN in .env on this machine")
        for f in (NOTE, TTS):
            if f.is_file():
                assert tok not in f.read_text(encoding="utf-8"), f"{f} leaks it"


class TestItIsOfflineUnlessAsked:
    def test_the_default_run_makes_no_network_call(self):
        src = CHECKER.read_text(encoding="utf-8")
        i = src.index("if not a.live:")
        assert "urllib" not in src[:i], (
            "a network import happens before the --live gate, so the default "
            "path can reach out")

    def test_an_unknown_flag_is_refused(self):
        r = subprocess.run([sys.executable, str(CHECKER), "--nope"], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        assert r.returncode != 0
        assert "unrecognized arguments" in r.stderr


class TestHeActuallyGotTheInstructions:
    def test_both_documents_exist(self):
        assert NOTE.is_file(), "the repository copy is missing"
        if not TTS.is_file():
            pytest.skip("no Desktop TTS folder on this machine")

    def test_they_name_the_revoke_step(self):
        """A rotation that only ADDS a token has not rotated anything."""
        t = NOTE.read_text(encoding="utf-8")
        assert "Revoke" in t or "revoke" in t
        assert "Delete" in t or "delete" in t

    def test_they_name_the_scopes(self):
        t = NOTE.read_text(encoding="utf-8")
        assert "deposit:write" in t and "deposit:actions" in t

    def test_the_tts_copy_carries_no_markup(self):
        if not TTS.is_file():
            pytest.skip("no Desktop TTS copy on this machine")
        text = TTS.read_text(encoding="utf-8")
        for ch, name in (("#", "hash"), ("*", "asterisk"), ("`", "backtick"),
                         ("|", "pipe"), ("—", "em-dash")):
            assert ch not in text, f"the spoken copy contains a {name}"

    def test_the_note_says_nothing_here_uses_the_token(self):
        """The measured fact that makes the rotation safe."""
        t = NOTE.read_text(encoding="utf-8")
        assert "0" in t and "cannot break a running process" in t
