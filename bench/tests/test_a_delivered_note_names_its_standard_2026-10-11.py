"""A delivered note or TTS file must name the CDSFL note standard it was written under.

HIS INSTRUCTION, 2026-10-11: *"You have returned again to not printing the CDSFL notes standard
used to produce these files. This is a small glitch, but meaningful and should be fixed
(prerably mechanically so you don't forget again), as it helps me to track which notes standards
you are using across files."*

MECHANICAL IS THE POINT. The stamp was on the notes of 2026-10-08 and 2026-10-09 and absent from
BOTH files delivered on 2026-10-11 -- the forget-again he describes. A first fix added the check
to `blocking()` only and reported 0 findings on plainly unstamped files, because `main()` calls
`partition()` directly: an UNWIRED ADDITION, the exact defect the additive standard names. This
guard therefore exercises the CLI, not the helper.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LINT = REPO / "scripts" / "note_vagueness_lint.py"


def _lint(path: Path) -> str:
    r = subprocess.run([sys.executable, str(LINT), str(path)],
                       capture_output=True, text=True, timeout=180)
    return r.stdout + r.stderr


class TestTheStampCheckIsWiredIntoTheCommandLine:
    def test_it_fires_on_a_delivered_note_with_no_stamp(self, tmp_path):
        d = tmp_path / "experimental_notes"
        d.mkdir()
        f = d / "Unstamped_Note_2026-10-11.md"
        f.write_text("# A note\n\nIt says 3 things and names no standard.\n", encoding="utf-8")
        assert "NOTE STANDARD" in _lint(f), "the CLI did not report a missing stamp"

    def test_it_fires_on_a_tts_file_with_no_stamp(self, tmp_path):
        d = tmp_path / "CDSFL_tts"
        d.mkdir()
        f = d / "Unstamped_2026-10-11.txt"
        f.write_text("A spoken file naming no standard at all.\n", encoding="utf-8")
        assert "NOTE STANDARD" in _lint(f)

    def test_it_is_silent_when_the_stamp_is_present_and_current(self, tmp_path):
        d = tmp_path / "experimental_notes"
        d.mkdir()
        f = d / "Stamped_2026-10-11.md"
        f.write_text("# A note\n\nWritten under CDSFL note standard v1.7.\n", encoding="utf-8")
        assert "NOTE STANDARD" not in _lint(f)

    def test_an_archival_stamp_is_accepted_and_an_invented_one_is_not(self, tmp_path):
        """REWRITTEN 2026-10-28, because the assertion contradicted a ruled design.

        This asserted that a note stamped v1.4 is REPORTED for being older than
        the current standard. The lint deliberately does the opposite, and says
        so where `ARCHIVAL_NOTE_STANDARDS` is defined: "A note stamped with one
        of these is correctly stamped, whatever the current standard is." The
        reason is recorded with its measurement -- 191 notes carry the v1.7 stamp
        and every one of them is correctly stamped, so flagging an earlier
        standard would make the archive retrospectively wrong and produce exactly
        the noise that gets a rule switched off. His ruling of 2026-10-17 is the
        same: "We fix going forward and leave the archive alone".

        So the discriminating property is not OLD versus CURRENT. It is REAL
        versus INVENTED, and that is what this now checks -- which keeps the test
        failable: dropping the version check entirely makes the second half red.
        """
        d = tmp_path / "experimental_notes"
        d.mkdir()
        archival = d / "Archival_2026-10-11.md"
        archival.write_text(
            "# A note\n\nWritten under CDSFL note standard v1.4.\n",
            encoding="utf-8")
        assert "NOTE STANDARD" not in _lint(archival), (
            "a genuine earlier standard was reported as a fault; that is how he "
            "tracks which standard produced which file")

        invented = d / "Invented_2026-10-11.md"
        invented.write_text(
            "# A note\n\nWritten under CDSFL note standard v2.3.\n",
            encoding="utf-8")
        out = _lint(invented)
        assert "NOT A STANDARD THIS PROJECT HAS USED" in out, (
            f"an invented stamp was accepted, so the check cannot tell a real "
            f"standard from a made-up one: {out}")

    def test_it_does_not_police_files_that_are_not_delivered_notes(self, tmp_path):
        """A source file, a registry or a README is not a note. Policing them would make the
        rule noise, and a noisy rule gets switched off."""
        f = tmp_path / "some_producer.py"
        f.write_text("# a script, not a note\nprint(1)\n", encoding="utf-8")
        assert "NOTE STANDARD" not in _lint(f)

    def test_the_files_delivered_today_now_carry_it(self):
        here = REPO / "experimental_notes" / "What_Was_Actually_Implemented_2026-10-11.md"
        if not here.is_file():
            pytest.skip("the note is not in this checkout")
        assert "NOTE STANDARD" not in _lint(here), (
            "a file already delivered to the founder still lacks its standard stamp")
