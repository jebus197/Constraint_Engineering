"""The cy watch must start when a run starts and end when the run ends.

FOUNDER, 2026-10-02: *"The cy monitor should run automatically when a run starts
and end when the run ends."*

WHY IT LIVES IN THE RUNNER. The watchdog needs 3 things and the runner is the
only process that knows all 3 at once: its own pid, the TIMESTAMPED outcome
directory it names itself, and a console log that grows. Arming it by hand from
outside got the outcome directory wrong twice on 2026-10-02 -- `058dfae` ("the
watchdog looked for the run's verdict in the wrong directory") and its twin in
`_round_count`, `cd0b5f3` -- because the artefacts live in the run's own
directory while the console log is wherever the operator redirected it. The
sandboxed launcher redirects nothing at all, so before this there was no console
log unless somebody made one, and the watchdog's stall detector reads byte
growth.

FAIL-OPEN IS THE SAFETY PROPERTY. A monitoring process must never be able to
stop an experiment, so every failure path returns None and the run proceeds
unwatched -- worse than watched, far better than halted.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(REPO / "bench") not in sys.path:
    sys.path.insert(0, str(REPO / "bench"))

import importlib.util  # noqa: E402

RUNNER = REPO / "bench" / "tools" / "run_simulated_experiment.py"
pytestmark = pytest.mark.skipif(not RUNNER.is_file(), reason="runner absent")


def _mod():
    spec = importlib.util.spec_from_file_location("rse_under_test", str(RUNNER))
    m = importlib.util.module_from_spec(spec)
    sys.modules["rse_under_test"] = m
    spec.loader.exec_module(m)
    return m


class TestFailOpen:
    """A watch that cannot start must never stop the run."""

    def test_the_opt_out_suppresses_it(self, tmp_path, monkeypatch):
        m = _mod()
        monkeypatch.setenv("CDSFL_NO_CY_WATCHDOG", "1")
        assert m._start_cy_watchdog(tmp_path, tmp_path / "console.log") is None

    def test_a_missing_watchdog_script_returns_None_rather_than_raising(
            self, tmp_path, monkeypatch):
        m = _mod()
        monkeypatch.delenv("CDSFL_NO_CY_WATCHDOG", raising=False)
        monkeypatch.setattr(m, "REPO", tmp_path)       # no scripts/ here
        assert m._start_cy_watchdog(tmp_path, tmp_path / "console.log") is None


class TestTheTeeGivesTheWatchdogALog:

    def test_it_mirrors_writes_into_the_file(self, tmp_path):
        m = _mod()
        log = tmp_path / "console.log"

        class _Sink:
            def __init__(self): self.seen = ""
            def write(self, d): self.seen += d; return len(d)
            def flush(self): pass
            def isatty(self): return False

        sink = _Sink()
        tee = m._Tee(sink, log)
        tee.write("round 0 landed\n")
        tee.flush()
        assert sink.seen == "round 0 landed\n", "the real stream lost output"
        assert "round 0 landed" in log.read_text(), "the mirror lost output"

    def test_unknown_attributes_delegate(self, tmp_path):
        """ANTI-REGRESSION: `isatty` and friends must still reach the stream,
        or anything asking whether stdout is a terminal breaks."""
        m = _mod()

        class _Sink:
            def write(self, d): return len(d)
            def flush(self): pass
            def isatty(self): return True

        assert m._Tee(_Sink(), tmp_path / "c.log").isatty() is True

    def test_a_failed_mirror_does_not_break_the_run(self, tmp_path):
        """The mirror is best-effort: the run's own output must survive it."""
        m = _mod()

        class _Sink:
            def __init__(self): self.seen = ""
            def write(self, d): self.seen += d; return len(d)
            def flush(self): pass

        sink = _Sink()
        tee = m._Tee(sink, tmp_path / "nonexistent_dir" / "c.log")
        tee.write("still printed\n")
        assert sink.seen == "still printed\n"


class TestItReallySpawns:

    def test_the_watch_is_armed_against_this_process_and_this_outcome_dir(
            self, tmp_path, monkeypatch):
        """NOT A MOCK. The 3 arguments that were wrong twice today are checked
        against a REAL spawned process."""
        m = _mod()
        monkeypatch.delenv("CDSFL_NO_CY_WATCHDOG", raising=False)
        log = tmp_path / "console.log"
        log.write_text("starting\n")
        proc = m._start_cy_watchdog(tmp_path, log)
        assert proc is not None, "no watchdog spawned"
        try:
            args = " ".join(proc.args)
            assert f"--pid {os.getpid()}" in args, args
            assert f"--outcome-dir {tmp_path}" in args, args
            assert f"--log {log}" in args, args
            # WAIT FOR CONTENT, NOT FOR EXISTENCE. The redirect creates the
            # file at spawn, so breaking on `.exists()` races the first write
            # and asserts against an empty string -- which is how the first
            # version of this test failed while the watchdog was working.
            wd_log = tmp_path / "cy_watchdog.log"
            for _ in range(40):
                if wd_log.exists() and wd_log.stat().st_size:
                    break
                time.sleep(0.25)
            assert "ARMED" in wd_log.read_text(), wd_log.read_text()[:200]
        finally:
            # KILL, NOT TERMINATE. The watchdog's SIGTERM handler only sets a
            # stop flag; the loop then finishes its current `sleep(interval)`
            # before noticing, so with a 60 s interval a polite terminate can
            # take a full minute. That is harmless in production -- the watch
            # exits on PROCESS GONE when the run dies, which is the contract --
            # but a test must not wait for it.
            proc.kill()
            proc.wait(timeout=20)
