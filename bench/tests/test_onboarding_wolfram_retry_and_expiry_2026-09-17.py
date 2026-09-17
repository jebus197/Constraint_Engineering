#!/usr/bin/env python3
"""Onboarding's Wolfram check retries, names contention and stale kernels, and warns on expiry.

QUESTION 11, 2026-09-17. Run with fakes, the audit found `wolfram_state` class
kernel contention ("Connection closed by WolframKernel") and a timeout as
NO_KERNEL after 1 call, then offer to reconfigure the kernel path, which repairs
neither; read a licence message as a licence fault without the `ps` check for a
leftover kernel that `.claude/CLAUDE.md` requires first; and never read
`$LicenseExpirationDate`, so the manual renewal due 2026-10-08 never surfaced.

Every kernel and `ps` call is a fake. The real kernel is never started.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "cdsfl_onboard.py"
KERNEL_LINE = "  4242 /Applications/Wolfram Engine.app/Contents/MacOS/WolframKernel -wstp"
LICENCE_MSG = "Your Wolfram Engine installation is not activated or is experiencing a license-related problem."


@pytest.fixture(scope="module")
def onb():
    spec = importlib.util.spec_from_file_location("onb_wolfram_retry", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["onb_wolfram_retry"] = m
    spec.loader.exec_module(m)
    return m


def _world(monkeypatch, onb, kernel_replies, ps_lines=()):
    """A fake machine: kernel calls take `kernel_replies` in order (the last repeats)."""
    calls = {"kernel": [], "ps": 0}
    monkeypatch.setattr(onb.shutil, "which", lambda _c: "/usr/local/bin/wolframscript")

    def run(cmd, *a, **k):
        if cmd[0] == "ps":
            calls["ps"] += 1
            return subprocess.CompletedProcess(cmd, 0, "\n".join(ps_lines) + "\n", "")
        calls["kernel"].append(cmd[-1])
        out, rc = kernel_replies[min(len(calls["kernel"]), len(kernel_replies)) - 1]
        if out is TimeoutError:
            raise subprocess.TimeoutExpired(cmd, 1)
        return subprocess.CompletedProcess(cmd, rc, out, "")
    monkeypatch.setattr(onb.subprocess, "run", run)
    return calls


class TestRetryAndContention:
    def test_contention_twice_is_busy_not_no_kernel(self, onb, monkeypatch):
        calls = _world(monkeypatch, onb, [("Connection closed by WolframKernel", 1)])
        assert onb.wolfram_state() == "BUSY"
        assert len(calls["kernel"]) == 2

    def test_contention_then_success_is_ok(self, onb, monkeypatch):
        calls = _world(monkeypatch, onb, [("Connection closed by WolframKernel", 1), ("2", 0)])
        assert onb.wolfram_state() == "OK" and len(calls["kernel"]) == 2

    def test_a_timeout_then_success_is_ok(self, onb, monkeypatch):
        calls = _world(monkeypatch, onb, [(TimeoutError, None), ("2", 0)])
        assert onb.wolfram_state() == "OK" and len(calls["kernel"]) == 2

    def test_busy_offers_no_reconfiguration(self, onb, monkeypatch, capsys):
        _world(monkeypatch, onb, [("Connection closed by WolframKernel", 1)])
        monkeypatch.setattr(onb, "ask", lambda *a, **k: pytest.fail("BUSY must not offer a repair"))
        assert onb.check_wolfram() == "BUSY"
        assert "-configure" not in capsys.readouterr().out


class TestStaleKernelBeforeLicence:
    def test_a_licence_message_with_a_kernel_running_is_stale(self, onb, monkeypatch):
        calls = _world(monkeypatch, onb, [(LICENCE_MSG, 255)], ps_lines=[KERNEL_LINE])
        assert onb.wolfram_state() == "STALE_KERNEL" and calls["ps"] >= 1

    def test_a_licence_message_with_nothing_running_is_not_activated(self, onb, monkeypatch):
        calls = _world(monkeypatch, onb, [(LICENCE_MSG, 255)], ps_lines=["  1 /sbin/launchd"])
        assert onb.wolfram_state() == "NOT_ACTIVATED" and calls["ps"] >= 1


class TestExpiry:
    def test_the_date_the_kernel_reports_drives_the_warning(self, onb, monkeypatch):
        soon = dt.date.today() + dt.timedelta(days=3)
        _world(monkeypatch, onb, [(f"DateObject[{{{soon.year}, {soon.month}, {soon.day}}}, Day]", 0)])
        warning = onb.wolfram_licence_warning()
        assert warning and soon.isoformat() in warning and "recorded" not in warning

    def test_a_distant_date_warns_nothing(self, onb, monkeypatch):
        far = dt.date.today() + dt.timedelta(days=200)
        _world(monkeypatch, onb, [(f"DateObject[{{{far.year}, {far.month}, {far.day}}}, Day]", 0)])
        assert onb.wolfram_licence_warning() is None

    def test_an_unreadable_date_falls_back_to_the_recorded_one_and_says_so(self, onb, monkeypatch):
        soon = (dt.date.today() + dt.timedelta(days=2)).isoformat()
        monkeypatch.setattr(onb.W, "RECORDED_LICENCE_EXPIRY", soon)
        _world(monkeypatch, onb, [("$Failed", 0)])
        warning = onb.wolfram_licence_warning()
        assert warning and soon in warning and "recorded on 2026-09-15" in warning

    def test_check_wolfram_prints_renew_when_ok_and_near(self, onb, monkeypatch, capsys):
        soon = dt.date.today() + dt.timedelta(days=5)
        _world(monkeypatch, onb, [("2", 0), (f"DateObject[{{{soon.year}, {soon.month}, {soon.day}}}, Day]", 0)])
        assert onb.check_wolfram() == "OK"
        assert "[RENEW]" in capsys.readouterr().out
