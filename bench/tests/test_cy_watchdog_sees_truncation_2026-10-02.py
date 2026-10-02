"""A TRUNCATED log must not render the watchdog mute while the run crashloops.

THE STATE THIS GUARDS, found by the 2026-10-02 free panel attacking the new
watchdog on commission: the read branch in ``probe`` fires only when
``size > offset``. A run that dies and is restarted by a supervisor TRUNCATES
its log and rewrites a short tail -- so the new size sits BELOW the offset the
watchdog has already consumed. Three things then compound:

  1. ``size > offset`` is False, so the new bytes -- including the Traceback --
     are NEVER read. TROUBLE cannot fire.
  2. ``size != last_size`` is True, so ``last_change`` refreshes every rewrite.
     STALLED cannot fire either, for as long as the crashloop keeps churning.
  3. The heartbeat then reports "alive", which is affirmatively wrong, not
     merely silent.

A crashlooping run is exactly "dead or wrong", and the watchdog whose design
point is SILENCE IS NOT SUCCESS stays silent through it. These tests RUN the
watchdog as a subprocess; a source-text assertion would only confirm the script
describes itself consistently.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WD = ROOT / "scripts" / "cy_watchdog_2026-10-02.py"

pytestmark = pytest.mark.skipif(not WD.is_file(), reason="watchdog absent")


def _watch(log: Path, seconds: float, interval: int = 1,
           stall: int = 3600) -> str:
    """Run the watchdog continuously for `seconds`, then SIGTERM and collect."""
    proc = subprocess.Popen(
        [sys.executable, str(WD), "--log", str(log),
         "--pid", str(os.getpid()),
         "--interval", str(interval), "--stall-seconds", str(stall)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        time.sleep(seconds)
    finally:
        proc.send_signal(signal.SIGTERM)
    out, _ = proc.communicate(timeout=30)
    return out


class TestTruncationIsAnEvent:

    def test_a_crashloop_that_truncates_the_log_is_spoken(self, tmp_path):
        """THE SILENT STATE. Long healthy log -> truncate -> short Traceback.

        Before the fix: size (short) < offset (long) suppresses the read, and
        the size CHANGE refreshes the stall clock, so the watchdog says nothing
        at all about a run that is dying in a loop.
        """
        log = tmp_path / "run.log"
        log.write_text("dispatching seats\n" * 150, encoding="utf-8")   # ~2.7 kB

        def mutate():
            # Supervisor restart: truncate, rewrite a short crash tail.
            time.sleep(1.8)   # let the first probe consume the healthy bytes
            log.write_text("Traceback (most recent call last):\n"
                           "RuntimeError: seat dispatch died\n",
                           encoding="utf-8")

        t = threading.Thread(target=mutate)
        t.start()
        out = _watch(log, seconds=5.0)
        t.join()

        assert "TRUNCATED" in out, (
            "the log shrank below the consumed offset and the watchdog never "
            f"said so -- the crashloop-silent state is live:\n{out}")
        assert "TROUBLE" in out, (
            "the Traceback written after truncation was never read -- the "
            f"watchdog is blind to everything a restarted run writes:\n{out}")

    def test_truncation_resets_the_offset_so_later_lines_are_read(self, tmp_path):
        """After a truncation the watchdog must keep reading the NEW file."""
        log = tmp_path / "run.log"
        log.write_text("x" * 500 + "\n", encoding="utf-8")

        def mutate():
            time.sleep(1.8)
            log.write_text("restarted\n", encoding="utf-8")       # truncation
            time.sleep(1.8)
            with log.open("a", encoding="utf-8") as fh:            # then growth
                fh.write("FATAL: cannot reach registry\n")

        t = threading.Thread(target=mutate)
        t.start()
        out = _watch(log, seconds=6.5)
        t.join()
        assert "TROUBLE" in out and "FATAL" in out, out

    def test_ordinary_growth_is_not_reported_as_truncation(self, tmp_path):
        """ANTI-FALSE-POSITIVE: append-only growth must stay quiet."""
        log = tmp_path / "run.log"
        log.write_text("starting\n", encoding="utf-8")

        def mutate():
            time.sleep(1.5)
            with log.open("a", encoding="utf-8") as fh:
                fh.write("dispatching seat cc2-sim, 4 of 5\n")

        t = threading.Thread(target=mutate)
        t.start()
        out = _watch(log, seconds=4.0)
        t.join()
        assert "TRUNCATED" not in out, out
        assert "TROUBLE" not in out, out
