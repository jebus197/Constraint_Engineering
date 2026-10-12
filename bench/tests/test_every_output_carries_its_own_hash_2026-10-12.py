"""Every delivered note and TTS file carries a verifiable hash of its own content.

HIS ORDER, 2026-10-12: *"As for giving each text/tts output its own hash value. Do it.
It will allow you to track these outputs more exactly going forward."*

TWO JUDGEMENTS MADE RATHER THAN PUT TO HIM, because he asked for exactly that: the
FILENAME stays human-readable, since he reads these by speech and a hex filename tells
him nothing; and the digest EXCLUDES its own stamp line, or a hash written into the file
it describes would invalidate itself.

WHAT THIS PINS
  1. The digest is stable: stamping twice does not change it.
  2. It DETECTS an edit -- the whole point of tracking.
  3. An unrecognised flag exits 2 rather than being read as a filename.
  4. The generator stamps its OWN output, because regenerating wipes a stamp applied
     afterwards and a step you must remember is a step that gets forgotten.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
STAMPER = REPO / "scripts" / "stamp_output_hash_2026-10-12.py"
GEN = REPO / "scripts" / "morning_report_build_2026-10-12.py"
LEDGER = REPO / "experimental_notes" / "data" / "output_hashes.json"

pytestmark = pytest.mark.skipif(not STAMPER.is_file(), reason="stamper absent")


def _mod():
    spec = importlib.util.spec_from_file_location("st", str(STAMPER))
    m = importlib.util.module_from_spec(spec)
    sys.modules["st"] = m
    spec.loader.exec_module(m)
    return m


class TestTheDigestIsStable:
    def test_stamping_twice_gives_the_same_digest(self, tmp_path):
        m = _mod()
        f = tmp_path / "note.md"
        f.write_text("# a note\n\nsome content\n", encoding="utf-8")
        first, changed1 = m.stamp(f)
        second, changed2 = m.stamp(f)
        assert first == second, "the digest moved when nothing but the stamp changed"
        assert changed1 is True and changed2 is False

    def test_the_digest_excludes_its_own_stamp_line(self, tmp_path):
        """Otherwise writing the hash in would invalidate the hash."""
        m = _mod()
        f = tmp_path / "n.md"
        body = "# x\n\nbody text\n"
        f.write_text(body, encoding="utf-8")
        before = m.digest(body)
        m.stamp(f)
        after = m.digest(f.read_text(encoding="utf-8"))
        assert before == after

    def test_a_verify_of_an_unstamped_file_reports_no_stamp(self, tmp_path):
        m = _mod()
        f = tmp_path / "u.md"
        f.write_text("plain\n", encoding="utf-8")
        got, was = m.verify(f)
        assert was is None and got


class TestItDetectsAnEdit:
    def test_an_appended_line_changes_the_digest(self, tmp_path):
        m = _mod()
        f = tmp_path / "n.md"
        f.write_text("# x\n\noriginal\n", encoding="utf-8")
        d, _ = m.stamp(f)
        with f.open("a", encoding="utf-8") as fh:
            fh.write("an edit nobody declared\n")
        got, was = m.verify(f)
        assert was == d
        assert got != was, "an edit did not change the digest, so tracking is vacuous"

    def test_verify_exits_non_zero_on_a_changed_file(self, tmp_path):
        f = tmp_path / "n.md"
        f.write_text("# x\n\nbody\n", encoding="utf-8")
        subprocess.run([sys.executable, str(STAMPER), str(f)],
                       capture_output=True, timeout=120, cwd=str(REPO))
        with f.open("a", encoding="utf-8") as fh:
            fh.write("tampered\n")
        r = subprocess.run([sys.executable, str(STAMPER), "--verify", str(f)],
                           capture_output=True, text=True, timeout=120, cwd=str(REPO))
        assert r.returncode != 0
        assert "CHANGED" in r.stdout


class TestItRefusesATypo:
    def test_an_unknown_flag_exits_two_and_is_not_read_as_a_filename(self):
        r = subprocess.run([sys.executable, str(STAMPER), "--bogus"],
                           capture_output=True, text=True, timeout=120, cwd=str(REPO))
        assert r.returncode == 2, f"exit {r.returncode}"
        assert "unrecognised argument" in r.stdout
        assert "MISSING" not in r.stdout, (
            "a flag was reported as a missing file, which reads as an ordinary failure")

    def test_help_is_answered_for_free(self):
        r = subprocess.run([sys.executable, str(STAMPER), "--help"],
                           capture_output=True, text=True, timeout=120, cwd=str(REPO))
        assert r.returncode == 0 and "usage:" in r.stdout


class TestTheGeneratorStampsItsOwnOutput:
    """Regenerating WIPES a stamp applied afterwards, so the generator must do it."""

    def test_the_generator_calls_the_stamper(self):
        src = GEN.read_text(encoding="utf-8")
        assert "stamp_output_hash" in src, (
            "the generator does not stamp its own output, so every regeneration loses "
            "the hash")

    def test_the_live_generated_outputs_verify(self):
        m = _mod()
        for p in (REPO / "experimental_notes" / "Morning_Report_2026-10-12_GENERATED.md",
                  pathlib.Path.home() / "Desktop" / "CDSFL_tts"
                  / "Morning_Report_2026-10-12_GENERATED.txt"):
            if not p.is_file():
                continue
            got, was = m.verify(p)
            assert was is not None, f"{p.name} carries no stamp"
            assert got == was, f"{p.name} does not match its own stamp"


class TestTheLedgerTracksThem:
    def test_the_ledger_records_digest_path_and_commit(self):
        if not LEDGER.is_file():
            pytest.skip("no outputs stamped yet in this clone")
        d = json.loads(LEDGER.read_text(encoding="utf-8"))
        rows = d.get("outputs", [])
        assert rows, "the ledger has no rows"
        for r in rows[:20]:
            for k in ("digest", "path", "bytes", "commit", "stamped"):
                assert k in r, f"a ledger row is missing {k}"
            assert len(r["digest"]) == 12
