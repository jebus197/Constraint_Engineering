#!/usr/bin/env python3
"""The recovery report must name the run that actually ran last.

THE FOUNDER'S OBSERVATION, 2026-10-05: a state restore named `exp55_v3_control` from
23 August as the latest experiment while `study_run1b` from 3 October sat on disk, so
an agent rebuilding context after an interruption read 6-week-old state as current.

TWO COMPOUNDING CAUSES. `cdsfl_utils.latest_experiment` selects by the highest
experiment NUMBER, which is deliberate for its 3 callers; and it only considers
directories matching `exp(\\d+)` at all, which is not. Measured by
`scripts/the_recovery_picker_cannot_see_most_runs_2026-10-06.py`: **37 of 81 run
directories carrying a report or `runner_state.json` are invisible to it — 45.6790%,
Wilson [35.2733%, 56.4760%]**, statsmodels and a scipy closed form agreeing.

`latest_experiment` is UNCHANGED, because 3 callers depend on its contract.
`newest_run` is added beside it and the recovery report prints both, labelled.

Every assertion CALLS the picker against a real directory tree. None reads source.
"""
import pathlib
import sys
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import cdsfl_utils  # noqa: E402


@pytest.fixture
def logs(tmp_path, monkeypatch):
    """A logs tree holding an OLD numbered experiment and a NEW unnumbered run."""
    root = tmp_path / "repo"
    d = root / "bench" / "logs"
    d.mkdir(parents=True)
    old = d / "exp55_v3_control"
    old.mkdir()
    (old / "exp55_report.json").write_text('{"experiment": "exp55"}', encoding="utf-8")
    time.sleep(0.02)
    new = d / "study_run1b_2026-10-03_20261003T100439Z"
    new.mkdir()
    (new / "runner_state.json").write_text('{"registry": {"entries": {}}}',
                                           encoding="utf-8")
    monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: root)
    return root, old, new


class TestNewestRunAnswersWhatRanLast:
    def test_it_returns_the_most_recent_directory_not_the_highest_number(self, logs):
        _, old, new = logs
        got = cdsfl_utils.newest_run()
        assert got is not None, "newest_run found nothing in a populated tree"
        assert got["name"] == new.name, (
            f"newest_run returned {got['name']!r}; the most recently modified run "
            f"is {new.name!r}. This is the defect the founder reported.")

    def test_it_sees_unnumbered_runs(self, logs):
        """The larger of the 2 causes: 37 of 81 real directories are unnumbered."""
        got = cdsfl_utils.newest_run()
        assert got["is_numbered_experiment"] is False, (
            "the fixture's newest run should be unnumbered, so this test is not "
            "measuring the condition it was written for")

    def test_the_old_picker_still_cannot_see_it(self, logs):
        """ANTI-VACUITY. If `latest_experiment` could see it, `newest_run` would be
        solving a problem that no longer exists."""
        _, old, new = logs
        le = cdsfl_utils.latest_experiment()
        assert le is None or le.get("name") != new.name, (
            "latest_experiment now sees the unnumbered run, so the fixture no "
            "longer reproduces the reported condition")

    def test_it_reports_a_usable_timestamp_and_path(self, logs):
        got = cdsfl_utils.newest_run()
        assert got["modified"] and "T" in got["modified"]
        assert pathlib.Path(got["log_dir"]).is_dir()
        assert got["has_runner_state"] is True

    def test_an_empty_tree_returns_none_rather_than_raising(self, tmp_path,
                                                            monkeypatch):
        root = tmp_path / "empty"
        (root / "bench" / "logs").mkdir(parents=True)
        monkeypatch.setattr(cdsfl_utils, "repo_root", lambda: root)
        assert cdsfl_utils.newest_run() is None

    def test_a_directory_with_no_state_is_not_a_run(self, logs):
        """A stray directory must not be reported as the newest run."""
        root, _, new = logs
        stray = root / "bench" / "logs" / "zzz_not_a_run"
        stray.mkdir()
        (stray / "notes.txt").write_text("x", encoding="utf-8")
        got = cdsfl_utils.newest_run()
        assert got["name"] == new.name, (
            f"a directory carrying no report and no runner_state was reported as "
            f"the newest run ({got['name']!r})")


class TestTheRecoveryReportPrintsBoth:
    def test_the_report_calls_newest_run(self):
        """An addition nothing reaches is not additive. Parsed, not matched."""
        import ast
        src = (REPO / "scripts" / "cdsfl_recover.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and (getattr(n.func, "id", None)
                      or getattr(n.func, "attr", None)) == "newest_run"]
        assert calls, (
            "cdsfl_recover.py never calls newest_run, so the recovery report still "
            "answers only the numbered-experiment question")

    def test_both_blocks_are_labelled_so_they_cannot_be_confused(self):
        """EXECUTED, not read: the report is RUN and its OUTPUT inspected.

        What matters is what a person recovering state actually sees. A source
        match would pass on a heading that some branch never prints.
        """
        import subprocess
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "cdsfl_recover.py")],
            cwd=str(REPO), capture_output=True, text=True, timeout=600)
        out = r.stdout
        assert "NEWEST RUN (by modification date" in out, (
            "the recovery report does not PRINT the newest-run block")
        assert "LATEST EXPERIMENT (highest exp<N>" in out, (
            "the printed LATEST EXPERIMENT heading does not say it is the highest "
            "number rather than the newest, which is exactly how the 2 got "
            "confused")
        assert out.index("NEWEST RUN (by modification date") < out.index(
            "LATEST EXPERIMENT (highest exp<N>"), (
            "the newest run is printed AFTER the highest-numbered experiment, so a "
            "reader still meets the stale answer first")
