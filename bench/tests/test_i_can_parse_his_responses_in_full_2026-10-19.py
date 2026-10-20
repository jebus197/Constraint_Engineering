"""His responses must parse IN FULL, and the claim must be measured, not asserted.

HIS INSTRUCTION, 2026-10-19: *"You have had several problems parsing my tts
responses recently, but you also said you had fully fixed this? ... Make sure you
can extract/parse my responses fully."*

HE IS RIGHT THAT IT WAS CLAIMED AND WAS NOT TRUE, AND THE RECORD SHOWS WHY. Three
separate gaps have been found, each real, each repaired, and each followed by a
claim of completeness that outran what had actually been measured:

  2026-10-11  DECODING. Word writes plain text with Mac-classic CR line endings
              and smart quotes as high bytes, so `grep` sees one long line, calls
              the file binary and exits silently. 15 of 40 annotated files were
              invisible, carrying 221 of his responses.
  2026-10-13  TRUNCATION. A multi-line annotation returned 97 of its 1,053
              characters, losing the operative clause.
  2026-10-19  MARKERS. His `fr`, `pf` and `qs` markers sit on their OWN LINE
              below an annotation and carry no leading hash, so they were never
              part of any annotation's text. 30 were invisible.

The common cause is not any one of those bugs. It is that COMPLETENESS WAS NEVER
MEASURED, so each repair's scope was mistaken for the whole. This test runs the
measurement, so the claim is falsifiable and goes red the moment it stops holding.

Producer: `scripts/can_i_parse_his_responses_in_full_2026-10-19.py`.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "can_i_parse_his_responses_in_full_2026-10-19.py"
RESPONSES = pathlib.Path("/Users/georgejackson/Developer_Projects/Responses")


@pytest.fixture(scope="module")
def run():
    if not RESPONSES.is_dir():
        pytest.skip("his Responses folder is not present in this checkout")
    return subprocess.run([sys.executable, str(SCRIPT)],
                          cwd=ROOT, capture_output=True, text=True, timeout=600)


class TestTheMeasurementItself:
    def test_the_producer_exists(self):
        assert SCRIPT.is_file(), SCRIPT

    def test_help_does_no_work(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        assert r.returncode == 0
        assert "usage:" in r.stdout
        assert "ANNOTATIONS :" not in r.stdout, (
            "--help ran the measurement; a --help must never cost anything")


class TestItParsesInFull:
    def test_it_exits_zero(self, run):
        assert run.returncode == 0, (
            "the reader no longer parses his responses in full:\n"
            + run.stdout[-3000:])

    def test_every_annotation_is_returned(self, run):
        assert "COMPLETE on all 4 properties" in run.stdout, run.stdout[-2000:]

    def test_it_reports_both_coverage_figures_with_intervals(self, run):
        for label in ("annotations  coverage", "markers      coverage"):
            assert label in run.stdout, run.stdout[-2000:]
        assert "Wilson [" in run.stdout
        assert "exact [" in run.stdout

    def test_the_marker_half_is_not_vacuous(self, run):
        #: A marker coverage of 0 of 0 would also be "complete". It must be
        #: measuring real markers, because the whole `qs` mechanism rests on it.
        line = next(l for l in run.stdout.splitlines() if "MARKERS" in l)
        got, present = line.split(":")[1].split("attached of")
        assert int(present.strip().split()[0]) >= 25, line

    def test_the_annotation_half_is_not_vacuous(self, run):
        line = next(l for l in run.stdout.splitlines() if "ANNOTATIONS" in l)
        assert int(line.split(":")[1].strip().split()[0]) >= 500, line
