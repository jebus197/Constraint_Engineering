"""The note-standard stamp rule must participate in the ratchet, and not as noise.

HIS RULING, 2026-10-17, on whether the 73 historical notes were in scope: "We fix
going forward and leave the archive alone. Going back and rewriting the archive,
as I have said before could potentially be seen as dishonest, and as an attempt
to rewrite history."

THE DEFECT. The pre-commit ratchet copies the staged and HEAD versions of each
note into a `mktemp -d` directory and lints THOSE paths. The stamp rule's scope
test asks whether the path sits under `experimental_notes/` or a `*_tts/` folder,
and a temporary path does neither -- so it returned nothing for BOTH sides of
every comparison and never participated in the ratchet at all. A note could lose
its standard stamp with nothing to say so.

THE FIX IS `--as`, which declares the path the bytes REPRESENT, for the
path-sensitive rules only. The ratchet now passes it on both sides, so a
pre-existing stamp cancels out and cannot cause a false refusal, while a stamp
REMOVED by an edit shows up as the file getting worse.

AND THE RULE WAS NARROWED IN THE SAME CHANGE, because reaching the archive is
not the same as judging it. Measured when `--as` first let it through: 357 of 536
notes produced a finding, 66.6045%, Wilson [62.5061%, 70.4665%], of which 161
were WRONG VERSION on notes that are CORRECTLY stamped -- a note written in April
under v1.3 and stamped v1.3 is doing exactly what he asked for, which is
traceability rather than uniformity. Grandfathering the real earlier standards
leaves 196, 36.5672%, Wilson [32.5989%, 40.7266%], all of them a genuine absence
of any stamp, and those are archive notes he has ruled are to be left alone.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LINT = REPO / "scripts" / "note_vagueness_lint.py"
sys.path.insert(0, str(REPO / "scripts"))


@pytest.fixture()
def lint():
    import importlib
    import note_vagueness_lint as m
    importlib.reload(m)
    yield m
    m._LOGICAL_PATH = ""


STAMPED = ("A note about a mechanism.\n\n"
           "Written under CDSFL note standard v1.7, 26 August 2026.\n")
UNSTAMPED = "A note about a mechanism, with no standard named anywhere.\n"
OLD_STAMP = ("A note from April.\n\n"
             "Written under CDSFL note standard v1.3, 12 April 2026.\n")
INVENTED = ("A note claiming a standard that never existed.\n\n"
            "Written under CDSFL note standard v9.9.\n")


def _check(lint, body: str, logical: str) -> list:
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "copy_at_a_temporary_path.md"
        f.write_text(body, encoding="utf-8")
        lint._LOGICAL_PATH = logical
        return lint.missing_standard_stamp(f)


def test_without_a_declared_path_a_copy_is_not_treated_as_a_note(lint):
    """The old behaviour, kept: an arbitrary file is not a delivered note."""
    assert _check(lint, UNSTAMPED, "") == [], (
        "a file at a temporary path with no declared logical path is not a "
        "delivered note and must not be held to the stamp rule")


def test_with_a_declared_path_the_rule_reaches_the_copy(lint):
    """The defect: this returned [] and so never entered the ratchet."""
    found = _check(lint, UNSTAMPED, "experimental_notes/Something_2026-10-17.md")
    assert found, (
        "declaring the logical path must let the stamp rule see a copy. Without "
        "this the rule returned nothing for both sides of every ratchet "
        "comparison and a note could lose its stamp silently.")
    assert "MISSING" in found[0][1]


def test_a_current_stamp_is_clean(lint):
    assert _check(lint, STAMPED, "experimental_notes/x.md") == []


def test_an_earlier_real_standard_is_compliant_not_a_defect(lint):
    """HIS RULING: leave the archive alone. A v1.3 stamp on an April note is
    doing the job the stamp exists for."""
    assert _check(lint, OLD_STAMP, "experimental_notes/April_2026-04-12.md") == [], (
        "a note correctly stamped with an earlier standard must NOT be a "
        "finding. 161 archive notes were flagged this way, which is the noise "
        "this module's docstring warns gets a rule switched off, and it would "
        "have buried the 196 that are a real absence.")


def test_an_invented_standard_is_still_a_defect(lint):
    """Anti-vacuity: grandfathering real standards must not accept any string."""
    found = _check(lint, INVENTED, "experimental_notes/x.md")
    assert found, "a stamp naming a standard this project never used tells him nothing"
    assert "NOT A STANDARD" in found[0][1]


def test_a_tts_folder_counts_as_a_delivered_note(lint):
    found = _check(lint, UNSTAMPED, "CDSFL_tts/Report_2026-10-17.txt")
    assert found, "a TTS file is a delivered artefact and is stamped"


def test_a_source_file_is_not_a_note(lint):
    assert _check(lint, UNSTAMPED, "bench/reference_runner_v3.py") == []
    assert _check(lint, UNSTAMPED, "docs/GLOSSARY.md") == []


def test_the_cli_accepts_the_declared_path_and_help_is_free():
    r = subprocess.run([sys.executable, str(LINT), "--help"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and "--as" in r.stdout, (
        "`--as` must be documented in the usage, and --help must cost nothing")
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "c.md"
        f.write_text(UNSTAMPED, encoding="utf-8")
        bare = subprocess.run([sys.executable, str(LINT), str(f)],
                              capture_output=True, text=True, timeout=60)
        declared = subprocess.run([sys.executable, str(LINT), "--as",
                                   "experimental_notes/n.md", str(f)],
                                  capture_output=True, text=True, timeout=60)
    assert "MISSING NOTE STANDARD" not in bare.stdout
    assert "MISSING NOTE STANDARD" in declared.stdout


def test_the_ratchet_passes_the_logical_path_on_both_sides():
    """A one-sided declaration would be WORSE than none: HEAD would score lower
    than staged on every note, and every commit touching a note would refuse."""
    hook = (REPO / "hooks" / "pre-commit").read_text(encoding="utf-8")
    calls = [ln for ln in hook.splitlines() if "_lint_count " in ln and "$STAGED_COPY" in ln]
    assert len(calls) >= 2, f"expected both ratchet sides to call the linter; got {calls}"
    for ln in calls:
        assert '"$f"' in ln, (
            f"this ratchet side does not declare the logical path: {ln.strip()}. "
            "Declaring it on one side only makes HEAD score lower than staged on "
            "every note, so every commit touching a note would refuse.")
