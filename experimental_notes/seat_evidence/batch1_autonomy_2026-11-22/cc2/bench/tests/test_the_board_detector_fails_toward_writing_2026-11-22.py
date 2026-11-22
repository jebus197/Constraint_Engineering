# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'batch1_autonomy_2026-11-22', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4c98f509c4e435fb95fa14d3e8f4dc44ff873a92fa2a653ca3215085c46747be
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The triage's board detector must fail toward WRITING, as it documents.

ENTRY B205(c) / B180, PANEL FINDING 2026-11-22. `a_commit_board_is_running`
promises "any failure of this predicate returns ''". It leans on 2 exclusions
that both fail the OTHER way by design, because both were written for
`hooks/cy_monitor_gate.py`:

    _own_process_chain  "FAIL-SAFE TOWARD DETECTING A RUN"
    cy._is_shell        "unreadable -> KEEP, fail toward refusing"

Where `ps` is absent or refused by sandbox policy, those go inert and a planted
shell is reported as a running commit board. `hooks/work_not_narrate.py` stands
its entire Stop gate down on this value, so the consequence is a DISABLED gate,
not a noisy one.

These tests pin the direction, not the implementation.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def bt():
    return _load("bt_polarity", REPO / "scripts" / "blocker_triage.py")


class _R:
    def __init__(self, out):
        self.stdout, self.stderr, self.returncode = out, "", 0


def _run_with(bt, shell_pid, deny_ps):
    """The predicate with pgrep stubbed to ONE shell pid, ps optionally denied."""
    real = bt.subprocess.run

    def fake(cmd, *a, **k):
        if cmd and str(cmd[0]) == "pgrep":
            return _R(shell_pid + "\n")
        if cmd and str(cmd[0]) == "ps" and deny_ps:
            raise PermissionError(1, "Operation not permitted: 'ps'")
        return real(cmd, *a, **k)

    bt.subprocess.run = fake
    try:
        return bt.a_commit_board_is_running()
    finally:
        bt.subprocess.run = real


@pytest.fixture()
def planted_shell():
    proc = subprocess.Popen(["/bin/zsh", "-c", "sleep 20"])
    time.sleep(0.3)
    try:
        yield str(proc.pid)
    finally:
        proc.kill()


def test_a_shell_is_not_a_board_even_when_ps_is_denied(bt, planted_shell):
    """THE DEFECT ITSELF. No pytest runs in this test; the only match is a
    shell. The documented answer is '' and it must not depend on `ps`."""
    assert _run_with(bt, planted_shell, deny_ps=True) == "", (
        "a shell was reported as a running commit board while `ps` was denied; "
        "work_not_narrate stands its whole Stop gate down on this value")


def test_the_same_holds_with_ps_available(bt, planted_shell):
    """ANTI-VACUITY in the other direction: the answer is '' either way, so the
    test above is not merely restating the sandbox's `ps` policy."""
    assert _run_with(bt, planted_shell, deny_ps=False) == ""


def test_ps_unavailability_is_distinguishable_from_no_board(bt):
    """The probe that makes the repair possible must actually probe. Without a
    way to tell "cannot tell" from "nothing there", the polarity cannot be
    chosen at all."""
    assert hasattr(bt, "_ps_can_answer"), (
        "the predicate can no longer distinguish an unreadable `ps` from an "
        "absent board; the fail-safe direction is then unchooseable")
    real = bt.subprocess.run

    def deny(cmd, *a, **k):
        if cmd and str(cmd[0]) == "ps":
            raise PermissionError(1, "denied")
        return real(cmd, *a, **k)

    bt.subprocess.run = deny
    try:
        assert bt._ps_can_answer() is False
    finally:
        bt.subprocess.run = real


def test_a_real_board_is_still_detected(bt, monkeypatch):
    """THE WIDENING IS NOT WEAKENED. The repair must not buy its polarity by
    giving up detection -- that would be the removal half of the additive
    standard."""
    monkeypatch.setenv("CDSFL_BT_BOARD", "1")
    assert bt.a_commit_board_is_running() == "forced-by-seam"


def test_the_monitor_gate_keeps_the_opposite_polarity():
    """cy_monitor_gate must NOT be 'fixed' to match. Its cost of over-firing is
    a prod; its cost of under-firing is an unobserved 3-hour run, so failing
    toward detecting is correct THERE and only there."""
    cy = _load("cy_polarity", REPO / "hooks" / "cy_monitor_gate.py")
    real = cy.subprocess.run

    def deny(cmd, *a, **k):
        if cmd and str(cmd[0]) == "ps":
            raise PermissionError(1, "denied")
        return real(cmd, *a, **k)

    cy.subprocess.run = deny
    try:
        assert cy._is_shell("1") is False, (
            "cy_monitor_gate stopped failing toward refusing; that direction is "
            "deliberate and the triage repair must not have propagated here")
    finally:
        cy.subprocess.run = real
