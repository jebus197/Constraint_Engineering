"""Task 7.1: a note a reader is pointed at must say where its figures come from.

HIS RULING: "Fix them all, or at least those that a technical reader would be
likely to find insufficient in the interests of reproducibility."

THE SCOPE IS SPLIT AT THE START, not at the debrief. 383 notes exist and most
must not be touched: a FULL_RECORD of a panel session is a TRANSCRIPT, and
rewriting it destroys the thing it preserves. The bounded set is DERIVED rather
than chosen -- a note is LIVE if a canonical document points a reader at it -- and
comes to 118. The other 265 are reported, not repaired.

INSUFFICIENT MEANS ONE FALSIFIABLE THING: the note states a PERCENTAGE or a
P-VALUE and names no script that exists and declares no provenance.

BEFORE: 17 of the 33 live notes carrying such a figure were insufficient,
51.5152%, Wilson [35.2184%, 67.4960%]. AFTER: 0 of 33, Wilson
[0.0000%, 10.4270%].

THE FIGURES WERE NEVER LOST, WHICH IS THE FINDING. 10 of the 17 have surviving
archives in `bench/logs` and simply never named them: the note stated a method in
prose and no artefact, so a reader had nothing to run while the data sat in the
repository. The other 7 have no artefact and now SAY SO, in those words, rather
than carrying figures that read as measurements.

A LOOSER FIRST MEASUREMENT IS NOT QUOTED. Counting "N of M" as a figure returned
110 of 180 notes, 61.1111%, but most matches are ordinary prose -- "1 of 3
rounds". A percentage or a p-value is a claim about a measurement in a way that
"one of three" is not.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCAN = ROOT / "scripts" / "note_reproducibility_2026-09-10.py"
EXP36 = ROOT / "scripts" / "exp36_verification_figures_2026-09-10.py"


@pytest.fixture(scope="module")
def scan():
    spec = importlib.util.spec_from_file_location("note_repro", SCAN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestEveryLiveNoteIsSufficient:
    def test_none_carries_a_figure_without_a_source(self, scan):
        live, _archive = scan.survey()
        bad = [scan.classify(n) for n in live]
        bad = [r for r in bad if r["figures"] and not r["sufficient"]]
        assert not bad, (
            "these live notes carry a percentage or p-value with no live script "
            "and no declared provenance: "
            + ", ".join(r["note"].name for r in bad))

    def test_the_bounded_set_is_derived_not_hand_listed(self, scan):
        live, archive = scan.survey()
        assert len(live) > 50, f"only {len(live)} live notes; the derivation broke"
        assert len(archive) > len(live), (
            "the archive is no longer the larger half, which would mean the "
            "canonical documents now point at nearly everything")

    def test_the_archive_is_reported_rather_than_repaired(self, scan):
        """Rewriting a transcript destroys the thing it preserves."""
        _live, archive = scan.survey()
        touched = [n for n in archive
                   if "FIGURE PROVENANCE" in n.read_text(encoding="utf-8",
                                                         errors="replace")]
        assert not touched, (
            f"provenance blocks were added to archive notes, which are records "
            f"of what was written: {[n.name for n in touched][:5]}")


class TestTheExp36FiguresActuallyReproduce:
    def test_the_script_runs_and_confirms_three_of_three(self):
        r = subprocess.run([sys.executable, str(EXP36)], cwd=ROOT,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-400:]
        assert "3 of 3 headline figures reproduce" in r.stdout, r.stdout[-600:]

    def test_it_reports_the_p_value_that_does_NOT_reproduce(self):
        """The one that failed is the interesting one and must not be buried."""
        r = subprocess.run([sys.executable, str(EXP36)], cwd=ROOT,
                           capture_output=True, text=True, timeout=300)
        assert "one-sided (greater) p = 0.1700" in r.stdout
        assert "two-sided p = 0.3400" in r.stdout
        assert "Anti-conservative by exactly a factor of 2" in r.stdout

    def test_the_note_carries_that_correction(self):
        t = (ROOT / "experimental_notes"
             / "Exp36_Verification_Analysis_2026-04-07.md").read_text(encoding="utf-8")
        assert "0.3400" in t and "ONE-SIDED" in t, (
            "the note no longer records that its p-value is one-sided and "
            "undeclared")
        assert "verdict is unaffected" in t, (
            "the note states the defect without stating that it changes nothing, "
            "which overstates it")
