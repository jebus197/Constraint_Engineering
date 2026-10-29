"""The runtime timeout check must sum a test's phases, not read its call alone.

WHY THIS PREDICATE AND NOT THE OBVIOUS ONE. `pytest.ini` sets `timeout = 300`
and sets no `timeout_func_only`. pytest-timeout 2.4.0 declares that ini key with
`default=False`, and with `func_only` False it arms the timer in
`pytest_runtest_protocol`, which wraps setup, call AND teardown. Established by
EXECUTION on 2026-10-29, not by reading: a test with a 1.5 s setup and a 1.0 s
call, under a 2 s limit, FAILED on timeout although neither phase alone exceeded
it. So a check comparing the `call` row against 300 under-reports, and task B36
asked for a runtime answer rather than a static one.

THE DISCRIMINATING CASE IS THE FIRST TEST BELOW: a call of 280 s with a setup of
40 s is UNDER the limit on the call row and OVER it on the sum. A fixture whose
call alone already exceeded the limit would pass under either rule and would
prove nothing.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "which_tests_outlive_the_global_timeout_2026-10-18.py"

_spec = importlib.util.spec_from_file_location("outlive", SCRIPT)
mod = importlib.util.module_from_spec(_spec)
sys.modules["outlive"] = mod
_spec.loader.exec_module(mod)


def _log(tmp_path: pathlib.Path, body: str) -> pathlib.Path:
    p = tmp_path / "suite.log"
    p.write_text("=============== slowest durations ===============\n" + body
                 + "=========== short test summary info ===========\n",
                 encoding="utf-8")
    return p


class TestItReadsTheTable:
    def test_it_collects_every_phase_per_test(self, tmp_path):
        p = _log(tmp_path, "280.00s call     a.py::t\n 40.00s setup    a.py::t\n")
        rows = mod.read_durations(p)
        assert rows == {"a.py::t": {"call": 280.0, "setup": 40.0}}

    def test_a_log_with_no_table_yields_nothing(self, tmp_path):
        p = tmp_path / "plain.log"
        p.write_text("1 passed in 0.1s\n", encoding="utf-8")
        assert mod.read_durations(p) == {}

    def test_a_missing_table_is_reported_not_silently_empty(self, tmp_path, capsys):
        p = tmp_path / "plain.log"
        p.write_text("1 passed in 0.1s\n", encoding="utf-8")
        rc = mod.report_durations(p, 30.0)
        out = capsys.readouterr().out
        assert rc == 1, "a log with no durations table must not look like a pass"
        assert "--durations" in out


class TestTheSumIsWhatIsCompared:
    """The predicate under test, and the case that separates the 2 rules."""

    def test_a_call_under_the_limit_whose_sum_is_over_is_reported(
            self, tmp_path, capsys):
        p = _log(tmp_path, "280.00s call     a.py::t_sum\n 40.00s setup    a.py::t_sum\n")
        assert mod.global_timeout() == 300.0, "this fixture is built for a 300 s limit"
        mod.report_durations(p, 30.0)
        out = capsys.readouterr().out
        assert "AT OR OVER THE LIMIT: 1" in out, out
        assert "a.py::t_sum" in out
        assert "320.00s" in out, "the figure reported must be the SUM"

    def test_a_test_comfortably_inside_the_limit_is_not_reported(
            self, tmp_path, capsys):
        p = _log(tmp_path, " 45.00s call     a.py::t_fine\n")
        mod.report_durations(p, 30.0)
        out = capsys.readouterr().out
        assert "AT OR OVER THE LIMIT: 0" in out
        assert "t_fine" not in out.split("WITHIN")[0]

    def test_the_band_below_the_limit_is_reported_too(self, tmp_path, capsys):
        """Unrecorded phases are allowed for, so the sum is a LOWER bound."""
        p = _log(tmp_path, "250.00s call     a.py::t_band\n")
        mod.report_durations(p, 30.0)
        out = capsys.readouterr().out
        assert "WITHIN 60 s OF THE LIMIT" in out
        assert "t_band" in out


class TestAnAdequateMarkerIsRecognised:
    def test_a_test_declaring_more_than_its_runtime_needs_nothing(
            self, tmp_path, capsys):
        """The mirrors test runs over the limit and declares timeout(960)."""
        target = ("bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py"
                  "::TestTheOrderingActuallyHolds"
                  "::test_a_drifted_mirror_does_not_refuse_the_commit")
        if not (REPO / target.split("::")[0]).is_file():
            pytest.skip("the mirrors test is not present in this checkout")
        p = _log(tmp_path, f"309.75s call     {target}\n")
        mod.report_durations(p, 30.0)
        out = capsys.readouterr().out
        assert "AT OR OVER THE LIMIT: 1" in out
        assert "declares timeout(960)" in out, out
        assert "NEEDS:" not in out, (
            "a test already declaring a budget above its runtime must not be "
            "told to add one")

    def test_a_test_with_no_marker_is_given_a_figure(self, tmp_path, capsys):
        p = _log(tmp_path, "320.00s call     nosuchfile.py::t_bare\n")
        mod.report_durations(p, 30.0)
        out = capsys.readouterr().out
        assert "NO EXPLICIT MARKER" in out
        assert "NEEDS: @pytest.mark.timeout(" in out

    def test_the_suggested_figure_says_it_is_a_floor(self, tmp_path, capsys):
        """It ignores the test's own subprocess budget and must say so."""
        p = _log(tmp_path, "320.00s call     nosuchfile.py::t_bare\n")
        mod.report_durations(p, 30.0)
        out = capsys.readouterr().out
        assert "FLOOR" in out and "subprocess budget" in out


class TestTheStaticModeIsUntouched:
    def test_help_costs_nothing(self):
        import subprocess
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0
        assert "usage:" in r.stdout
        assert "global per-test limit" not in r.stdout, (
            "--help ran the measurement; a reader asking what a script does "
            "must never be charged the measurement to find out")

    def test_the_static_scan_still_exists(self):
        assert callable(getattr(mod, "scan", None)), (
            "the runtime mode must ADD to the static scan, not replace it: the "
            "2 answer different questions and B36 names both")
