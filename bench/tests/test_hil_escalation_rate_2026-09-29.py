"""The HIL escalation producer must read the run's OWN counts, and never read a
rise off 2 small rounds.

WHY IT MATTERS. The founder's standing observation is that an unusually high
human-escalation queue has, across this project's whole record, always indicated
broken machinery, never matched the project's formal escalation criteria, and
always proved computationally reducible. So escalation volume is a FAULT
DETECTOR — and a detector that cries wolf on noise is worse than none, because
the next real signal is discounted.

THE TRAP THIS PINS. On the 2026-09-29 arm 1 run, round 0 escalated 2 of 14 and
round 1 escalated 2 of 6 — 14.2857% to 33.3333%, an apparent doubling that is
nothing at all: Fisher exact p = 0.5492, Wilson intervals [4.0094%, 39.9414%] and
[9.6771%, 70.0007%] overlapping almost entirely. Reporting that as a rise is how a
noise excursion becomes a finding.

These tests EXECUTE the parser and the arithmetic (`execute-do-not-grep`).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "hil_escalation_rate_2026-09-29.py"


def _load():
    spec = importlib.util.spec_from_file_location("hil_rate", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["hil_rate"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def mod():
    assert SCRIPT.is_file(), f"missing {SCRIPT}"
    return _load()


#: A log in the runner's real shape, built here so the test does not depend on a
#: run being present or on any particular archive state.
SYNTHETIC = """
[20:44:28] Round 0/7 (blind)
[21:04:57]   MECHANICAL FAULT C0001: falsifier fires on a CORRECTED copy
[21:06:07]   falsifier gate (tools decide): 12 CONFIRMED, 0 REFUTED, 2 -> HIL
[21:19:10]   routing: 2 resolved by strong writer, 0 dedup'd, 1 -> HIL, 1 deferred
[21:22:50] Round 1/7 (adaptive)
[21:39:15]   falsifier gate (tools decide): 4 CONFIRMED, 0 REFUTED, 2 -> HIL
"""


class TestItReadsTheRunsOwnCounts:

    def test_it_attributes_each_tally_to_its_round(self, mod):
        rounds = mod.parse(SYNTHETIC)
        assert [r["round"] for r in rounds] == [0, 1]
        assert rounds[0]["confirmed"] == 12 and rounds[0]["hil"] == 2
        assert rounds[1]["confirmed"] == 4 and rounds[1]["hil"] == 2

    def test_routing_escalation_is_counted_separately(self, mod):
        rounds = mod.parse(SYNTHETIC)
        assert rounds[0]["routing_hil"] == 1
        assert rounds[1]["routing_hil"] == 0, (
            "routing's escalation must not be folded into the gate's denominator; "
            "they assess different populations")

    def test_the_reason_is_captured_not_only_the_count(self, mod):
        """Volume without cause is not a finding."""
        rounds = mod.parse(SYNTHETIC)
        assert any("MECHANICAL FAULT" in r for r in rounds[0]["reasons"])

    def test_a_log_with_no_rounds_is_a_completed_check_not_a_failure(self, mod):
        assert mod.parse("nothing here") == []


class TestTheArithmeticIsRight:

    def test_the_interval_is_computed_twice_and_agrees(self, mod):
        lo_l, hi_l = mod.wilson_local(2, 14)
        lo_s, hi_s = mod.wilson_sm(2, 14)
        assert abs(lo_l - lo_s) < 1e-12 and abs(hi_l - hi_s) < 1e-12

    def test_it_reproduces_the_recorded_round_figures(self, mod):
        lo, hi = mod.wilson_local(2, 14)
        assert round(100 * 2 / 14, 4) == 14.2857
        assert round(100 * lo, 4) == 4.0094 and round(100 * hi, 4) == 39.9414
        lo, hi = mod.wilson_local(2, 6)
        assert round(100 * 2 / 6, 4) == 33.3333
        assert round(100 * lo, 4) == 9.6771 and round(100 * hi, 4) == 70.0007

    def test_an_empty_denominator_does_not_divide_by_zero(self, mod):
        assert mod.wilson_local(0, 0) == (0.0, 0.0)
        assert mod.wilson_sm(0, 0) == (0.0, 0.0)

    def test_a_rate_of_1_gives_an_interval_not_a_point(self, mod):
        lo, hi = mod.wilson_local(6, 6)
        assert hi == pytest.approx(1.0) and lo < 1.0, (
            "an interval collapsing to a point would let a small round look "
            "certain")


class TestItRefusesToReadARiseOffNoise:
    """The whole point. These two rounds must NOT be reported as a change."""

    def test_the_observed_doubling_is_not_significant(self):
        from scipy.stats import fisher_exact
        _odds, p = fisher_exact([[2, 12], [2, 4]])
        assert p > 0.05, (
            "if this becomes significant the guard below is measuring nothing")
        assert round(p, 4) == 0.5492

    def test_the_two_intervals_overlap(self, mod):
        lo0, hi0 = mod.wilson_local(2, 14)
        lo1, hi1 = mod.wilson_local(2, 6)
        assert lo1 < hi0, "the intervals must overlap for this to be noise"

    def test_the_script_says_so_in_its_output(self, tmp_path):
        """The warning must REACH the reader, not sit in a docstring."""
        log = tmp_path / "r.log"
        log.write_text(SYNTHETIC, encoding="utf-8")
        out = subprocess.run([sys.executable, str(SCRIPT), str(log)],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-500:]
        assert "Fisher exact" in out.stdout
        assert "not distinguishable" in out.stdout
        assert "Do NOT report a rise" in out.stdout

    def test_a_genuinely_high_rate_is_still_reported(self, tmp_path):
        """ANTI-VACUITY: the caution must not suppress a real signal."""
        log = tmp_path / "h.log"
        log.write_text("""
[00:00:00] Round 0/7 (blind)
[00:00:01]   falsifier gate (tools decide): 1 CONFIRMED, 0 REFUTED, 19 -> HIL
""", encoding="utf-8")
        out = subprocess.run([sys.executable, str(SCRIPT), str(log)],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0
        assert "19 of 20 = 95.0000%" in out.stdout


class TestItCostsNothingAndFailsLegibly:

    def test_help_does_no_work(self):
        out = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0
        assert "usage:" in out.stdout
        assert "HIL ESCALATION BY ROUND" not in out.stdout

    def test_a_missing_log_exits_2_with_a_message(self, tmp_path):
        out = subprocess.run([sys.executable, str(SCRIPT),
                              str(tmp_path / "absent.log")],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 2
        assert "no such log" in out.stderr
