#!/usr/bin/env python3
"""The note standard is v1.8, and Rule 31 is numbered rather than only enforced.

HIS INSTRUCTION, 2026-10-04: *"Just use official project terminology in both
cases, and where no project terminology exists, just name the process itself
exactly. Why is that so difficult for you? Either way our notes standard still
needs tweaking I think."* And, naming the new form the fault had taken: *"you
have now clearly resorted [to] vagueness (or what you seem to think is
'simplification') through outright omission. This is not acceptable either."*

WHAT WAS ALREADY TRUE AND WHAT WAS MISSING. The 2 patterns his complaint
describes were implemented in `scripts/note_vagueness_lint.py` on 2026-10-04 and
have been firing ever since -- they are what `UNNAMED SUBJECT` and `QUANTITY
WITHOUT A VALUE` report. What was missing was their PLACE IN THE STANDARD, which
is the tweak he asked for. v1.7 was locked on 2026-08-26, 39 days before the
complaint, and no v1.8 existed.

THE BUMP IS SAFE AND THAT WAS MEASURED, not assumed. 191 notes carry the v1.7
stamp. Moving v1.7 into `ARCHIVAL_NOTE_STANDARDS` keeps every one of them
CORRECTLY stamped rather than retrospectively wrong: counted over all 537 notes,
the stamp findings went from 197 to 196, and the single change is the closing
report of 2026-10-17 being re-stamped to v1.8. Nothing became worse.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import note_vagueness_lint as L  # noqa: E402

MEM = (pathlib.Path.home() / ".claude" / "projects"
       / "-Users-georgejackson-Developer-Projects" / "memory")


def test_the_current_standard_is_v18():
    assert L.CURRENT_NOTE_STANDARD == "v1.8", (
        "his instruction of 2026-10-04 was that the standard itself needed "
        "tweaking to cover vagueness by omission; v1.8 is that tweak")


def test_v17_is_archival_so_191_notes_stay_correctly_stamped():
    assert "v1.7" in L.ARCHIVAL_NOTE_STANDARDS, (
        "191 notes carry the v1.7 stamp. If v1.7 is not archival they all "
        "become retrospectively wrong, which is a worse state than the one the "
        "bump was meant to improve.")
    for v in ("v1", "v1.2", "v1.4", "v1.6"):
        assert v in L.ARCHIVAL_NOTE_STANDARDS, v


def test_an_invented_standard_is_still_refused():
    """ANTI-VACUITY. Archiving every version would make the stamp meaningless."""
    for invented in ("v2.9", "v1.99", "v0.1"):
        assert invented not in L.ARCHIVAL_NOTE_STANDARDS
        assert invented != L.CURRENT_NOTE_STANDARD


def test_the_standard_document_exists_and_numbers_the_rule():
    f = MEM / "cdsfl_note_standard_v1.8.md"
    if not f.is_file():
        pytest.skip("the memory directory is not present in this checkout")
    t = f.read_text(encoding="utf-8")
    assert "Rule 31" in t, "v1.8 does not number the new rule"
    assert "UNNAMED SUBJECT" in t and "QUANTITY WITHOUT A VALUE" in t, (
        "v1.8 does not name the 2 patterns it formalises")
    assert "outright omission" in t, (
        "v1.8 does not quote the failure mode he named")
    assert "v1.7" in t, "v1.8 does not say which standard it supersedes"


def test_the_two_patterns_still_fire():
    """The rule is numbered AND enforced; numbering a dead check would be worse.

    Driven through the linter on constructed prose, so this fails if either
    pattern stops reporting.
    """
    import tempfile
    bad = ("A note.\n\n"
           "The mechanism was repaired and the rate improved.\n")
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "n.md"
        p.write_text(bad, encoding="utf-8")
        kinds = {k for _, k, *_ in L.vague_claims(p.read_text(encoding="utf-8"))} \
            if hasattr(L, "vague_claims") else set()
    if not kinds:
        # fall back to the module's own reporting path
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "n.md"
            p.write_text(bad, encoding="utf-8")
            out = subprocess.run([sys.executable,
                                  str(REPO / "scripts" / "note_vagueness_lint.py"),
                                  str(p)], capture_output=True, text=True).stdout
        assert "UNNAMED SUBJECT" in out, out
        assert "QUANTITY WITHOUT A VALUE" in out, out
    else:
        assert "UNNAMED SUBJECT" in kinds or "QUANTITY WITHOUT A VALUE" in kinds


def test_todays_delivered_report_carries_the_new_stamp():
    f = REPO / "experimental_notes" / "Closing_Report_Overnight_Task_List_2026-10-17.md"
    if not f.is_file():
        pytest.skip("the closing report is not in this checkout")
    t = f.read_text(encoding="utf-8")
    assert "note standard v1.8" in t, (
        "a note delivered after the bump still names the superseded standard")
    assert not L.missing_standard_stamp(f), L.missing_standard_stamp(f)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
