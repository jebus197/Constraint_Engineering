"""The `cy` watchdog must treat SILENCE as an event, not as health.

THE FAILURE THIS GUARDS, and it is the founder's own account of 2026-10-02:
*"last night it meant you let a run carry on for a full 9 hours without
monitoring or repairing anything, so you may have to create a mechanical
trigger for cy to wake you up so this cannot happen again."*

The hole was not a missing alarm. It was an alarm with nothing to say. A watcher
that only greps for trouble stays mute through a hang, a kill, or a crashloop,
and mute is indistinguishable from healthy — the Monitor tool's own
documentation makes the same point: "silence is not success." So the properties
tested here are the ABSENCE signals: a log that stops growing, and a process
that stops existing. Neither depends on the run choosing to write anything.

The assistant's previous explanation — that its monitors cap at 30 minutes — was
half true. The cap bounds ONE arming, and expiry notifies so it can be re-armed.
That is why the cadence belongs in a mechanical poller and the escalation in the
model, which is the split this script implements.

These tests RUN the watchdog as a subprocess. A test asserting on its source
text would only confirm it describes itself consistently.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WD = ROOT / "scripts" / "cy_watchdog_2026-10-02.py"

pytestmark = pytest.mark.skipif(not WD.is_file(), reason="watchdog absent")


def _run(args, timeout=60):
    r = subprocess.run([sys.executable, str(WD), *args],
                       capture_output=True, text=True, timeout=timeout)
    return r


class TestSilenceIsAnEvent:

    def test_a_stalled_log_is_reported(self, tmp_path):
        """THE 9-HOUR HOLE. No new bytes must become a spoken event."""
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")
        time.sleep(1.2)
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "1", "--once", "--interval", "1"])
        assert "STALLED" in r.stdout, r.stdout
        assert "SILENCE IS NOT SUCCESS" in r.stdout

    def test_a_healthy_quiet_run_is_NOT_reported_as_stalled(self, tmp_path):
        """ANTI-FALSE-POSITIVE: quiet inside the threshold is not an alarm."""
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "STALLED" not in r.stdout, r.stdout
        assert "TROUBLE" not in r.stdout

    def test_a_dead_process_is_reported_and_ends_the_watch(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        r = _run(["--log", str(log), "--pid", str(dead.pid),
                  "--once", "--interval", "1"])
        assert "PROCESS GONE" in r.stdout, r.stdout
        assert r.returncode == 0, "a run that ended is a CLEAN watchdog exit"

    def test_a_live_process_is_not_called_gone(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "PROCESS GONE" not in r.stdout
        assert r.returncode == 1, "the watch did not end, so the exit must differ"


class TestTroubleAndProgressAreSpoken:

    @pytest.mark.parametrize("line", [
        "Traceback (most recent call last):",
        "HALTED_IRREDUCIBLE_QUEUE_ALARM at round 0",
        "openai.RateLimitError: 429",
        "Killed",
        "PermissionError: [Errno 1] Operation not permitted",
        "UNRECORDED_STOP (the round loop exited)",
    ])
    def test_each_trouble_signature_wakes_the_model(self, tmp_path, line):
        log = tmp_path / "run.log"
        log.write_text("", encoding="utf-8")
        # the watchdog reads from offset 0 on its first probe
        log.write_text(line + "\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" in r.stdout, f"{line!r} did not wake it: {r.stdout}"

    def test_an_ordinary_line_does_not_wake_the_model(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("dispatching seat cc2-sim, 4 of 5\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "TROUBLE" not in r.stdout, r.stdout

    def test_a_landed_round_is_reported_from_the_artefact_not_the_prose(self, tmp_path):
        """Rounds are counted from round_*.json, so a lying log cannot inflate them."""
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        (tmp_path / "round_00.json").write_text("{}", encoding="utf-8")
        (tmp_path / "round_01.json").write_text("{}", encoding="utf-8")
        r = _run(["--log", str(log), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "ARMED" in r.stdout
        assert "2 round(s) landed" in r.stdout, r.stdout


class TestItCannotItselfBecomeTheSilentWatcher:

    def test_a_missing_log_is_announced_rather_than_tolerated(self, tmp_path):
        r = _run(["--log", str(tmp_path / "never.log"), "--pid", str(os.getpid()),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "does not exist yet" in r.stdout, r.stdout
        assert "a run that never starts is itself an event" in r.stdout

    def test_it_always_announces_that_it_armed(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        r = _run(["--log", str(log), "--once", "--interval", "1"])
        assert r.stdout.splitlines()[0].startswith("[cy "), r.stdout
        assert "ARMED" in r.stdout

    def test_it_always_announces_that_it_closed(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        r = _run(["--log", str(log), "--once", "--interval", "1"])
        assert "CLOSED" in r.stdout, (
            "a watchdog that exits silently is the defect it exists to prevent")

    def test_help_costs_nothing_and_exits_zero(self):
        r = _run(["--help"])
        assert r.returncode == 0 and "usage" in r.stdout.lower()

    def test_an_unreadable_pid_file_does_not_crash_it(self, tmp_path):
        log = tmp_path / "run.log"
        log.write_text("x\n", encoding="utf-8")
        bad = tmp_path / "bad.pid"
        bad.write_text("not-a-pid\n", encoding="utf-8")
        r = _run(["--log", str(log), "--pid-file", str(bad),
                  "--stall-seconds", "3600", "--once", "--interval", "1"])
        assert "ARMED" in r.stdout and "CLOSED" in r.stdout
