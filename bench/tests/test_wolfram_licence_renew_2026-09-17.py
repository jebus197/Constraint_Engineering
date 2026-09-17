#!/usr/bin/env python3
"""The Wolfram licence renews itself, and the thing that runs it is really installed.

FOUNDER, 2026-09-17: automate the renewal, and "make sure it still loads on
system reboot whatever you do".

MEASURED THE SAME EVENING, WITH THE LICENCE FILE BACKED UP FIRST: `wolframscript
-activate` with stdin closed returned exit 0 and "Wolfram Engine activated",
prompting for nothing, which refutes the note in `scripts/cdsfl_onboard.py` that
it "cannot be automated from here". The same run showed the expiry did NOT move
while the licence was still valid (2026-10-08 before and after), which is why
the agent runs on a schedule and keeps trying rather than firing once.

Every test here drives the real functions with injected runners. Not 1 of them
starts a kernel or activates anything.
"""
from __future__ import annotations

import importlib.util
import plistlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "wolfram_licence_renew_2026-09-17.py"
COMMITTED_PLIST = ROOT / "resources" / "launchd" / "com.cdsfl.wolfram-licence-renew.plist"
INSTALLED_PLIST = Path.home() / "Library" / "LaunchAgents" / "com.cdsfl.wolfram-licence-renew.plist"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("wolfram_renew", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _runner(out: str, code: int = 0, raises=None, seen: list | None = None):
    def run(cmd, **kw):
        if seen is not None:
            seen.append((list(cmd), kw))
        if raises is not None:
            raise raises
        return subprocess.CompletedProcess(cmd, code, out, "")
    return run


class TestReadingTheExpiry:
    def test_a_date_is_parsed(self, mod):
        got, why = mod.read_expiry(runner=_runner("DateObject[{2026, 10, 8}, Day]"))
        assert got == "2026-10-08", (got, why)

    def test_a_kernel_failure_is_not_a_date(self, mod):
        got, why = mod.read_expiry(runner=_runner("Connection closed by WolframKernel", code=1))
        assert got is None and "did not answer" in why


class TestActivating:
    def test_success_needs_both_exit_zero_and_the_word(self, mod):
        seen = []
        ok, detail = mod.activate(runner=_runner("Wolfram Engine activated.", seen=seen))
        assert ok and "activated" in detail.lower()
        cmd, kw = seen[0]
        assert cmd[-1] == "-activate"
        assert kw.get("stdin") is subprocess.DEVNULL, (
            "activation must run with stdin CLOSED, so a build that prompts fails instead of hanging")

    def test_exit_zero_without_the_word_is_not_success(self, mod):
        ok, _ = mod.activate(runner=_runner("nothing happened"))
        assert not ok

    def test_a_prompt_shows_up_as_a_timeout_and_fails(self, mod):
        ok, detail = mod.activate(runner=_runner("", raises=subprocess.TimeoutExpired("x", 1)))
        assert not ok and "asked for input" in detail

    def test_an_email_never_reaches_the_caller(self, mod):
        _, detail = mod.activate(runner=_runner("activated for someone@example.com"))
        assert "@" not in detail and "<redacted>" in detail


class TestTheDecision:
    """`main` is driven with its own helpers replaced, so the decision is executed."""

    def _wire(self, mod, monkeypatch, expiry, busy=(), ok=True, calls=None):
        calls = calls if calls is not None else []
        monkeypatch.setattr(mod, "read_expiry", lambda **k: (expiry, "stub"))
        monkeypatch.setattr(mod, "kernels_running", lambda **k: list(busy))
        monkeypatch.setattr(mod, "activate", lambda **k: (calls.append("activate"), (ok, "Wolfram Engine activated."))[1])
        return calls

    def test_it_does_nothing_when_the_licence_is_not_due(self, mod, monkeypatch, tmp_path, capsys):
        calls = self._wire(mod, monkeypatch, "2099-01-01")
        assert mod.main(["--run", "--log", str(tmp_path / "l.log")]) == 0
        assert calls == [], "it activated a licence that was not due"
        assert "nothing to do" in capsys.readouterr().out

    def test_it_activates_when_the_licence_is_due(self, mod, monkeypatch, tmp_path):
        calls = self._wire(mod, monkeypatch, "2000-01-01")
        log = tmp_path / "l.log"
        assert mod.main(["--run", "--log", str(log)]) == 0
        assert calls == ["activate"]
        assert "RENEWED" in log.read_text()

    def test_it_waits_while_another_kernel_is_running(self, mod, monkeypatch, tmp_path):
        calls = self._wire(mod, monkeypatch, "2000-01-01", busy=["4242 WolframKernel"])
        log = tmp_path / "l.log"
        assert mod.main(["--run", "--log", str(log)]) == 0
        assert calls == [], "it activated while a kernel was running, against a single-kernel licence"
        assert "SKIP" in log.read_text()

    def test_a_failed_activation_exits_non_zero_and_says_so(self, mod, monkeypatch, tmp_path):
        self._wire(mod, monkeypatch, "2000-01-01", ok=False)
        log = tmp_path / "l.log"
        assert mod.main(["--run", "--log", str(log)]) == 3
        assert "FAILED" in log.read_text()

    def test_an_unreadable_expiry_is_treated_as_due(self, mod, monkeypatch, tmp_path):
        calls = self._wire(mod, monkeypatch, None)
        assert mod.main(["--run", "--log", str(tmp_path / "l.log")]) == 0
        assert calls == ["activate"]

    def test_without_run_it_acts_on_nothing(self, mod, monkeypatch, tmp_path, capsys):
        calls = self._wire(mod, monkeypatch, "2000-01-01")
        assert mod.main(["--log", str(tmp_path / "l.log")]) == 0
        assert calls == [] and "Read-only" in capsys.readouterr().out


def test_help_does_nothing():
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and r.stdout.startswith("usage:") and "RENEWED" not in r.stdout


class TestTheAgentIsReallyInstalled:
    """An addition nothing reaches is not additive: the schedule must exist on disk."""

    def test_the_committed_plist_runs_this_script_at_load_and_on_a_schedule(self):
        p = plistlib.loads(COMMITTED_PLIST.read_bytes())
        assert p["Label"] == "com.cdsfl.wolfram-licence-renew"
        assert str(SCRIPT) in p["ProgramArguments"] and "--run" in p["ProgramArguments"]
        assert p["RunAtLoad"] is True, "it must run at login and after a reboot"
        assert len(p["StartCalendarInterval"]) >= 2, "it must also run on a schedule"
        assert "/usr/local/bin" in p["EnvironmentVariables"]["PATH"], (
            "launchd starts with a minimal PATH and would not find wolframscript")

    def test_the_installed_copy_matches_the_committed_one(self):
        if not INSTALLED_PLIST.exists():
            pytest.skip("no LaunchAgent installed on this machine; install the committed copy to enable it")
        assert INSTALLED_PLIST.read_bytes() == COMMITTED_PLIST.read_bytes(), (
            "the loaded agent differs from the committed definition; copy the committed one and reload it")
