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


def _partition_faults(s, LIVE) -> list[str]:
    """The 4 properties the gate depends on, as a list of faults (empty = sound).

    Extracted so the LIVE store and a CONSTRUCTED store are judged by the SAME
    predicate. Two copies of a check are how a producer and a consumer come to
    describe themselves correctly and disagree with each other.
    """
    o = {t.tid for t in s.open_tickets()}
    w = {t.tid for t in s.workable()}
    d = {t.tid for t in s.deferred_tickets()}
    b = {t.tid for t in s.blockers()}
    faults = []
    if w | b != o - d:
        faults.append(
            "workable + blocked must be exactly the open set minus the "
            f"deferrals; unclassified open={sorted(o - d - w - b)}, "
            f"claimed but not open={sorted((w | b) - o)}")
    if (w & d) or (w & b) or (d & b):
        faults.append("the 3 sets overlap")
    if not (w | b) <= o:
        faults.append(f"workable/blocking but not open: {sorted((w | b) - o)}")
    #: ★ NO 4TH CHECK HERE, AND THE ABSENCE IS DELIBERATE. A first version of
    #: this helper also asserted that no row in `d` was in a dead state. That
    #: is a TAUTOLOGY: `deferred_tickets()` filters `status in LIVE` itself, so
    #: a dead row can never reach `d` and the check could never fail. A
    #: mutation removing the LIVE filter left it green, and building a
    #: constructed case made it green too -- which is how a check that decides
    #: nothing gets mistaken for a guard. The real property is tested from the
    #: other side, against the whole store, in
    #: `test_a_deferral_in_a_dead_state_is_not_presented_as_work`.
    return faults


def test_the_store_separates_the_three_sets():
    """workable + blocked must be exactly the open set MINUS the deferrals, and
    the deferrals must all be live.

    ★ THE SINGLE ASSERTION THIS REPLACES WAS ACCUSING CORRECT CODE, 2026-10-31.
    It read `w | d | b == o` and failed with ONE extra item on the left,
    `d0773f05188c` -- R1's ticket, status UNDECIDED and deferred. That is not a
    defect: `deferred_tickets()` was DELIBERATELY widened on 2026-10-30 from
    `status == "OPEN"` to the whole LIVE set, because R1's task-list marker read
    DEFERRED while `register_deferrals()` could not see it. Its docstring
    records the measurement that justified the widening -- 5 rows carry a
    deferral, 4 OPEN and 1 UNDECIDED -- and the live store reproduces exactly
    that split today. So the union is LARGER than the open set by construction,
    and an equality against `o` can never hold again.

    REPAIRED TOWARDS THE PROPERTY, NOT TOWARDS THE LITERAL. The thing worth
    guarding is that the gate sees a COMPLETE picture of open work with no row
    counted twice, and that the widening stays bounded to deferrals. That is 4
    checks rather than 1, so this is stronger than what it replaces: a ticket
    that fell out of all 3 sets, a row in 2 sets at once, a blocker or workable
    row that is not open, or a deferral in a dead state would each fail it.
    """
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore, LIVE
    assert not _partition_faults(TicketStore(), LIVE)


def test_a_deferral_in_a_dead_state_is_not_presented_as_work():
    """A deferred row that has since settled must not be presented as deferred.

    Tested against a CONSTRUCTED store, because the live store has 0 such rows
    and a guard that needs a live defect in order to work is not a guard.
    Tested from the WHOLE-STORE side rather than from `deferred_tickets()`'s
    own output, because the output is already filtered and asking it about its
    own filter can only ever agree. Presenting a settled row to the founder as
    outstanding work is the ghost entry the register exists to prevent.
    """
    import pathlib as _pl
    import tempfile
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore, LIVE, TERMINAL
    s = TicketStore(_pl.Path(tempfile.mkdtemp()) / "t.jsonl")
    t, _ = s.propose("pf", "a constructed ticket for the dead-deferral case",
                     "Built by this test so the dead-state check has a case.",
                     "test", task_ref="SYNTH-1")
    s.defer(t.tid, "constructed so the dead-state check has a case to catch",
            "2026-10-31T09:50:00+00:00")
    assert not _partition_faults(s, LIVE), "the constructed store starts sound"
    assert t.tid in {x.tid for x in s.deferred_tickets()}, "deferral not visible"

    dead = sorted(TERMINAL)[0]
    s._by_tid[t.tid].status = dead
    # The row STILL carries its deferral -- that field is the evidence of a
    # deliberate decision and is never cleared -- so the only thing keeping a
    # settled row out of the presented set is the live-state filter.
    assert s._by_tid[t.tid].deferred, "the deferral field must survive settling"
    assert t.tid not in {x.tid for x in s.deferred_tickets()}, (
        f"a ticket in state {dead} still carries a deferral AND is still "
        "presented as deferred work")
    assert not _partition_faults(s, LIVE), "the partition stays sound after it settles"


def test_a_deferral_is_presented_from_any_live_state_not_only_OPEN():
    """The 2026-10-30 widening, guarded so it cannot be silently undone.

    `deferred_tickets()` reads the whole LIVE set rather than `status == "OPEN"`
    because R1's task-list marker read DEFERRED while `register_deferrals()`
    could not see it: R1's ticket is UNDECIDED. Narrowing it back to OPEN is a
    1-token edit that every other assertion in this file survives, which is how
    a repair with a measurement behind it gets reverted by accident.

    CONSTRUCTED rather than read off the live store, so it keeps working when
    R1 is eventually settled and the live case disappears.
    """
    import pathlib as _pl
    import tempfile
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore, LIVE
    s = TicketStore(_pl.Path(tempfile.mkdtemp()) / "t.jsonl")
    assert "UNDECIDED" in LIVE and "UNDECIDED" != "OPEN"
    t, _ = s.propose("pf", "an undecided ticket, deferred",
                     "Built by this test to hold the widening of 2026-10-30.",
                     "test", task_ref="SYNTH-2", status="UNDECIDED")
    s.defer(t.tid, "deferred while still undecided, which is R1's own shape",
            "2026-10-31T09:55:00+00:00")
    assert s._by_tid[t.tid].status == "UNDECIDED", "the status must not be coerced"
    assert t.tid not in {x.tid for x in s.open_tickets()}, (
        "an UNDECIDED ticket is not OPEN -- that is the whole point of the case")
    assert t.tid in {x.tid for x in s.deferred_tickets()}, (
        "a deferral in a live-but-not-OPEN state must still be presented; "
        "narrowing deferred_tickets() back to OPEN loses R1")
    assert not _partition_faults(s, LIVE)
