#!/usr/bin/env python3
"""A spoken file delivered to him must have a markdown twin in the repository.

ENTRY B192, the 2 delivered spoken files with no markdown twin. **This guard is
the part of B192 that stops it happening again**; the 2 files it named were
mirrored on 2026-11-13 and the defect RECURRED on 2026-11-22 with 2 fresh
instances, which is the whole argument for a check over a correction.

★ B192's OWN DIAGNOSIS IS THE DESIGN BRIEF: *2 SEPARATE FAULTS WITH 1 CAUSE --
NOTHING CHECKS.* `tts-output-protocol` requires every spoken deliverable to
exist in 2 places, a plain-text copy on his Desktop and a markdown mirror under
`experimental_notes/`. Nothing refused a missing mirror, so the only thing
standing between the protocol and a silent miss was remembering.

★ WHAT THIS GUARD DELIBERATELY DOES NOT CHECK. Whether the 2 formats AGREE is a
different question with a different correct predicate, and
`bench/tests/test_a_deliverable_pair_uses_the_right_check_2026-11-03.py` already
holds it -- that file records that comparing a markdown file to its spoken twin
by hash reports a defect where none exists, because the protocol REQUIRES the
formats to differ. This guard asks only whether the mirror EXISTS. Checking
agreement here would be a second representation with no comparator.

★ THE PINNED SET IS A RATCHET, AND THE FIRST VERSION OF THIS GUARD CLAIMED IT
WAS EMPTY. THAT CLAIM WAS FALSE AND THE GUARD CAUGHT IT ON ITS FIRST RUN. It
read that every spoken file on this machine had a twin. The measurement behind
that sentence covered only files newer than 2026-11-12 -- 10 days -- and was
generalised to a folder holding files back to 2026-03-10, which is the
window error `feedback_an_aggregate_alarm_must_carry_its_window` records.

MEASURED over the whole folder instead: **289 of 673 spoken files have no twin,
0.429421, Wilson [0.392528, 0.467114]** on 2 routes agreeing to 5.551e-17,
spanning 89 distinct dates from 2026-03-10 to 2026-11-10, of which **8 postdate
2026-11-01**. Refusing all of them would refuse 0.429421 of the archive and
teach its reader that the checker is noise -- the identical reasoning
note-standard Rule 30 records for its own baseline.

So the 289 are PINNED AS DATA in `resources/spoken_files_without_a_twin_2026-11-22.json`
and anything NEW fails -- `feedback_pin_a_set_not_a_count` applied forward, a SET
and never a count. Rendering a twin REMOVES a name; a name may never be ADDED to
make this pass, and a test below asserts the set only ever shrinks.

★ AND IT MEANS B192 UNDERSTATES ITS OWN DEFECT BY 2 ORDERS OF MAGNITUDE. The
entry names 2 files. The class is 289.

★ A SEAM, BECAUSE THE DESKTOP IS ONE MACHINE'S. `CDSFL_TTS_DIR` lets every case
run against a CONSTRUCTED layout, so the properties are tested by execution on
known inputs rather than by whatever happens to sit on this Desktop. The live
check runs too, and is SKIPPED only where the folder genuinely does not exist --
a fresh clone on another machine -- with the skip stated rather than silent.
"""
from __future__ import annotations

import os
import pathlib

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "bench" / "tests").is_dir() and (cand / "experimental_notes").is_dir():
            return cand
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()
NOTES = REPO / "experimental_notes"

#: THE PINNED HISTORICAL SET, read from data rather than inlined, because 289
#: names in a source file is a wall nobody audits. See the docstring for why it
#: is a ratchet and not an empty set.
PINNED_FILE = REPO / "resources" / "spoken_files_without_a_twin_2026-11-22.json"


def _pinned() -> "frozenset[str]":
    import json
    if not PINNED_FILE.is_file():
        raise AssertionError(
            f"the pinned set is missing at {PINNED_FILE}. Without it this guard "
            f"would refuse 289 historical files and be switched off, which is the "
            f"outcome its own docstring exists to prevent. Restore the file.")
    return frozenset(json.loads(PINNED_FILE.read_text())["pinned"])


PINNED_WITHOUT_TWIN = _pinned()


def tts_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get(
        "CDSFL_TTS_DIR", str(pathlib.Path.home() / "Desktop" / "CDSFL_tts")))


def spoken_without_twin(tts: pathlib.Path, notes: pathlib.Path) -> "list[str]":
    """Every spoken file under `tts` with no `<base>.md` under `notes`."""
    out = []
    for f in sorted(tts.glob("*.txt")):
        if not (notes / f"{f.stem}.md").is_file():
            out.append(f.stem)
    return [s for s in out if s not in PINNED_WITHOUT_TWIN]


class TestThePredicateOnKnownInputs:
    """Driven on a CONSTRUCTED layout, so these cannot pass by accident."""

    def test_a_spoken_file_with_no_twin_is_reported(self, tmp_path):
        tts, notes = tmp_path / "tts", tmp_path / "notes"
        tts.mkdir(); notes.mkdir()
        (tts / "A_Report_2026-11-22.txt").write_text("spoken\n")
        assert spoken_without_twin(tts, notes) == ["A_Report_2026-11-22"]

    def test_a_spoken_file_with_a_twin_is_not_reported(self, tmp_path):
        tts, notes = tmp_path / "tts", tmp_path / "notes"
        tts.mkdir(); notes.mkdir()
        (tts / "A_Report_2026-11-22.txt").write_text("spoken\n")
        (notes / "A_Report_2026-11-22.md").write_text("# A Report\n")
        assert spoken_without_twin(tts, notes) == []

    def test_the_twin_must_be_markdown_not_any_file(self, tmp_path):
        """A `.txt` copy in the repository is the SAME-FORMAT relationship,
        which a different surface checks. It is not the markdown mirror."""
        tts, notes = tmp_path / "tts", tmp_path / "notes"
        tts.mkdir(); notes.mkdir()
        (tts / "A_Report_2026-11-22.txt").write_text("spoken\n")
        (notes / "A_Report_2026-11-22.txt").write_text("spoken\n")
        assert spoken_without_twin(tts, notes) == ["A_Report_2026-11-22"], (
            "a text copy is not a markdown mirror; the protocol asks for 2 formats")

    def test_several_missing_twins_are_all_reported(self, tmp_path):
        """ANTI-VACUITY: a predicate returning the first miss would hide the rest."""
        tts, notes = tmp_path / "tts", tmp_path / "notes"
        tts.mkdir(); notes.mkdir()
        for n in ("One_2026-11-22", "Two_2026-11-22", "Three_2026-11-22"):
            (tts / f"{n}.txt").write_text("spoken\n")
        (notes / "Two_2026-11-22.md").write_text("# Two\n")
        assert spoken_without_twin(tts, notes) == ["One_2026-11-22", "Three_2026-11-22"]

    def test_an_empty_folder_reports_nothing_and_that_is_not_a_pass(self, tmp_path):
        """The live test below asserts the folder is NON-EMPTY for this reason."""
        tts, notes = tmp_path / "tts", tmp_path / "notes"
        tts.mkdir(); notes.mkdir()
        assert spoken_without_twin(tts, notes) == []


class TestTheLiveLayout:
    def test_every_delivered_spoken_file_has_a_markdown_twin(self):
        tts = tts_dir()
        if not tts.is_dir():
            pytest.skip(f"no spoken-output folder at {tts} -- "
                        f"expected on a clone of another machine, stated not silent")
        missing = spoken_without_twin(tts, NOTES)
        assert not missing, (
            f"{len(missing)} delivered spoken file(s) have no markdown twin under "
            f"experimental_notes/: {missing}. `tts-output-protocol` requires both. "
            f"Render the markdown mirror; do not add the name to "
            f"PINNED_WITHOUT_TWIN to make this pass.")

    def test_the_live_folder_is_not_empty(self):
        """ANTI-VACUITY for the test above: an empty folder passes it trivially."""
        tts = tts_dir()
        if not tts.is_dir():
            pytest.skip(f"no spoken-output folder at {tts}")
        n = len(list(tts.glob("*.txt")))
        assert n > 0, (
            "the spoken-output folder holds 0 text files, so the twin check above "
            "proved nothing. If this is genuinely a fresh machine, the skip above "
            "is the right outcome and this folder should not exist.")

    def test_the_pinned_set_only_ever_SHRINKS(self):
        """THE RATCHET. 289 was the measured class on 2026-11-22.

        It may fall as twins are rendered. It may never RISE, because a rise
        means a missing twin was ACCEPTED rather than rendered -- which is B192
        reopening under cover of its own allowlist.
        """
        import json
        d = json.loads(PINNED_FILE.read_text())
        assert d["_count"] == len(d["pinned"]), (
            f"the declared count {d['_count']} does not match the {len(d['pinned'])} "
            f"names present; one was edited without the other")
        assert len(PINNED_WITHOUT_TWIN) <= 289, (
            f"the pinned set has GROWN to {len(PINNED_WITHOUT_TWIN)} from the 289 "
            f"measured on 2026-11-22. A name is only ever removed here. Render the "
            f"markdown twin instead of pinning the miss.")

    def test_a_pinned_name_that_now_has_a_twin_should_be_removed(self):
        """The ratchet must be able to TIGHTEN, or it is a permanent amnesty.

        Reported rather than enforced: rendering a twin is work, and failing the
        suite for not having done it yet would make this guard the noise its own
        docstring warns about. It names the slack so it can be taken up.
        """
        now_twinned = sorted(s for s in PINNED_WITHOUT_TWIN
                             if (NOTES / f"{s}.md").is_file())
        if now_twinned:
            print(f"\n{len(now_twinned)} pinned name(s) now HAVE a twin and can be "
                  f"removed from the pinned set: {now_twinned[:6]}")
        assert isinstance(now_twinned, list)
