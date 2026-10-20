"""The number the convergence gate reads is not a function of the assessments
beneath it, and the producer that establishes this must not go vacuous.

HIS QUESTION, 2026-10-19, which this came out of answering: whether the severity
wobble means severity is inherently a confidence within a range rather than a
single fixed value, and whether the gate needs changing at all.

WHAT THE MEASUREMENT FOUND. Over 147 entries where 2 or more independent
assessments of 1 defect are recoverable within a single run, the merged severity
equals the median of its inputs only 21.0884% of the time and lies OUTSIDE their
range entirely in 23.8095% of cases, 24 above every assessment and 11 below.

WHY THIS FILE GUARDS THE PRODUCER RATHER THAN THE NUMBERS. The figures will move
as runs are added, so pinning them would make this test a treadmill with no
property behind it. What must not change is that the measurement remains
POSSIBLE and remains HONEST: the join must stay scoped to one run, it must still
find assessments to compare, and it must not report a clean result from an empty
set. 6 instrument errors were made building it and 2 inflated figures reached a
report, so the hazards are named here as assertions.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "is_severity_noise_or_disagreement_2026-10-19.py"


@pytest.fixture(scope="module")
def run():
    if not (ROOT / "bench" / "logs").is_dir():
        pytest.skip("no archive in this checkout")
    return subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                          capture_output=True, text=True, timeout=900)


class TestTheProducerIsSound:
    def test_it_exists(self):
        assert SCRIPT.is_file()

    def test_help_does_no_work(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0
        assert "usage:" in r.stdout
        assert "PART 1" not in r.stdout, "--help ran the measurement"

    def test_it_exits_zero(self, run):
        assert run.returncode == 0, run.stdout[-2000:]


class TestItIsNotVACUOUS:
    """A measurement over 0 entries would also report cleanly."""

    def test_it_finds_assessments_to_compare(self, run):
        line = next(l for l in run.stdout.splitlines()
                    if "independent, SAME-RUN assessments" in l)
        n = int(line.split(":")[1].strip())
        assert n >= 50, (
            f"only {n} comparable entries; the join has probably broken and a "
            f"small set makes every proportion below meaningless")

    def test_it_reports_both_questions(self, run):
        assert "PART 1" in run.stdout and "PART 2" in run.stdout

    def test_every_proportion_carries_two_intervals(self, run):
        """Intervals may sit on the proportion's own line or the line below it.

        A FIRST VERSION OF THIS TEST REQUIRED THEM ON THE SAME LINE and failed
        on a legitimate row: in part 1 the producer prints the proportion and
        then its intervals on the following line, while in part 2 both sit
        together. The property that matters is that no proportion is reported
        WITHOUT intervals, not which line they land on.
        """
        import re
        lines = run.stdout.splitlines()
        shape = re.compile(r"\d+ of \d+ = [\d.]+%")
        rows = [i for i, l in enumerate(lines) if shape.search(l)]
        assert len(rows) >= 5, f"only {len(rows)} proportions reported at all"
        for i in rows:
            here = lines[i]
            below = lines[i + 1] if i + 1 < len(lines) else ""
            got = (("Wilson [" in here and "exact [" in here)
                   or ("Wilson [" in below and "exact [" in below))
            assert got, f"proportion with no adjacent intervals: {here.strip()!r}"


class TestTheHazardsAreStillGuardedAgainst:
    def test_the_join_is_scoped_to_one_run(self):
        #: The error that inflated 2 figures in a delivered report: finding ids
        #: repeat across runs, so a global index joins across them.
        src = SCRIPT.read_text(encoding="utf-8")
        assert "rundir.glob(\"round_*.json\")" in src, (
            "the raw-finding index must be built from ONE run's own round files; "
            "a global index joins a registry entry in one run to a finding in "
            "another, which is the error that inflated the mean spread to 0.1994 "
            "from 0.1786 and the outside-range share to 44.2177% from 23.8095%")

    def test_it_states_what_it_cannot_settle(self, run):
        assert "does NOT settle" in run.stdout, (
            "the producer must say that it cannot decide what severity MEANS, "
            "because that is the half of his question no archive can answer")

    def test_the_outside_range_split_is_reported_both_ways(self, run):
        assert "ABOVE every assessment" in run.stdout
        assert "BELOW every assessment" in run.stdout, (
            "reporting only one direction would read as a systematic discount "
            "when the measurement shows it goes both ways")
