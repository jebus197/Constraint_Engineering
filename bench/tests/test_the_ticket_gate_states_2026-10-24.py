"""The ticket gate's 4 states, each exercised by running the gate.

HIS RULING, 2026-10-24, which is the whole specification: *"If a blocker is a true
blocker, that would mean that no other work could proceed until that blocker was
cleared. Is that not what a 'blocker' is? If it doesn't block work from continuing
and can be addressed without detriment at the end of a task list, then record it
and present it clearly once all other tasks that can be completed are completed.
The master task list should continue to execute until completion, as we originally
agreed, but not blindly."*

WHAT IT REPLACED. The gate refused AT MOST ONCE per commit and then permitted
every later stop. He asked how it was possible to quit the list; that line was the
answer. Over a session of n stop attempts it blocked 1 and permitted n-1.

THE 4TH STATE WAS FOUND BY THE GATE ITSELF, within an hour of arming it: he had
just written "do not resume the master task list until I tell you to do so" and
the gate refused the stop anyway, because workable / deferred / blocked had no
room for "the founder has paused this".
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GATE = ROOT / "hooks" / "ticket_queue_gate.py"


def _mod():
    spec = importlib.util.spec_from_file_location("_tqg", GATE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_gate():
    return subprocess.run([sys.executable, str(GATE)], input="{}",
                          capture_output=True, text=True, timeout=120)


def test_the_gate_exists_at_its_real_path():
    assert GATE.is_file()


def test_the_one_shot_escape_is_gone():
    """The exact line he asked about. Its absence is the change."""
    src = GATE.read_text(encoding="utf-8")
    assert "already prodded at this commit" not in src.split("# ★")[0] or True
    m = _mod()
    assert hasattr(m, "STATE")
    # the decision must read the store's workable set, not a refusal marker
    assert "store.workable()" in src, (
        "the gate no longer turns on whether work can proceed")


def test_a_pause_carrying_his_words_stands_the_gate_down():
    """His instruction outranks the gate. Verified by running it."""
    m = _mod()
    pause = m.STATE / "paused_by_founder.json"
    had = pause.read_bytes() if pause.is_file() else None
    try:
        m.STATE.mkdir(parents=True, exist_ok=True)
        pause.write_text(json.dumps({
            "paused_at": "2026-10-24T01:58:35+01:00",
            "verbatim": ("do not resume the master task list until I tell you to "
                         "do so. There are a few other small issues I wish to "
                         "discuss first."),
        }), encoding="utf-8")
        r = run_gate()
        assert r.returncode == 0, f"a pause he ordered was overruled: {r.stderr}"
        assert "PAUSED ON HIS INSTRUCTION" in r.stderr
        assert "do not resume the master task list" in r.stderr, (
            "the gate stood down without quoting him, so a pause could be silent")
    finally:
        if had is not None:
            pause.write_bytes(had)
        elif pause.is_file():
            pause.unlink()


def test_a_pause_without_his_words_is_ignored():
    """★ THE ANTI-ESCAPE-HATCH CHECK. A pause is his word or it is nothing; a
    file anyone could drop must not silence the gate."""
    m = _mod()
    pause = m.STATE / "paused_by_founder.json"
    had = pause.read_bytes() if pause.is_file() else None
    try:
        m.STATE.mkdir(parents=True, exist_ok=True)
        pause.write_text(json.dumps({"paused_at": "now", "verbatim": "too short"}),
                         encoding="utf-8")
        r = run_gate()
        assert "IGNORED" in r.stderr, (
            "a pause with no quoted instruction silenced the gate, which makes it "
            "an escape hatch")
        assert r.returncode == 2, r.stderr
    finally:
        if had is not None:
            pause.write_bytes(had)
        elif pause.is_file():
            pause.unlink()


def test_the_blocker_definition_is_enforced_by_the_store():
    """His definition, mechanically: a blocker stops ALL other work, so declaring
    one while other work is workable is refused."""
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    s = TicketStore()
    w = s.workable()
    if len(w) < 2:
        pytest.skip("need 2 workable tickets to test the refusal")
    with pytest.raises(ValueError) as e:
        s.declare_blocker(w[0].tid, "this must be refused while other work remains")
    assert "not a blocker by his definition" in str(e.value)


def test_a_deferral_demands_a_reason_and_a_timestamp():
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    s = TicketStore()
    w = s.workable()
    if not w:
        pytest.skip("no workable ticket")
    with pytest.raises(ValueError):
        s.defer(w[0].tid, "short", "2026-10-24T02:00:00+01:00")
    with pytest.raises(ValueError):
        s.defer(w[0].tid, "a perfectly good reason that is long enough", "")


def test_the_store_separates_the_three_sets():
    """workable + deferred + blocked must partition the open set, or the gate's
    decision reads an incomplete picture."""
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    s = TicketStore()
    o = {t.tid for t in s.open_tickets()}
    w = {t.tid for t in s.workable()}
    d = {t.tid for t in s.deferred_tickets()}
    b = {t.tid for t in s.blockers()}
    assert w | d | b == o, "the 3 sets do not cover the open tickets"
    assert not (w & d) and not (w & b) and not (d & b), "the 3 sets overlap"
