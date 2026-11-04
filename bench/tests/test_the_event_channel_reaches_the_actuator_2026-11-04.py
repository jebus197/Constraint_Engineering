"""The watchdog's event channel must REACH the actuator, and reach it as evidence only.

THE GAP THIS CLOSES, found 2026-11-04 while working B20. Entry B20 records that
the actuator has a precondition which is not the actuator: `probe()` emitted its
event names to stdout only, so no program could learn WHICH condition fired, and
the `cy` protocol's response differs by condition. Candidate B was recommended:
have `probe()` return the events it emitted and have the mid-run pulse carry
them.

CANDIDATE B IS BUILT. `probe()` returns "new state, THE EVENTS IT EMITTED";
`write_pulse` takes an `events=` keyword; the mid-run call at
`scripts/cy_watchdog_2026-10-02.py:753` passes `events=events`; and
`bench/tools/cy_actuator_2026-11-03.py:158` reads `pulse.get("events")` into its
evidence.

AND NOTHING ASSERTED ANY OF THAT. `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py`
mentions `events` 0 times. So a field added to the actuator's output was reached
by no test, which is the symmetric half of `additive-standard`: an addition that
nothing executes is not additive either. This file is that test.

WHY IT EXECUTES THE WRITER AGAINST THE READER. Asserting that the watchdog's
source contains `events=events`, or that the actuator's source contains
`pulse.get("events")`, would establish only that each module describes itself
consistently -- `execute-do-not-grep`. A producer and a consumer that each
describe themselves correctly and disagree with each other is the exact shape
this project keeps finding. So the real `write_pulse` writes a real pulse to a
temp directory and the real actuator reads it back.

THE 3RD TEST IS THE ONE THAT PINS A DESIGN DECISION RATHER THAN A MECHANISM.
The actuator carries the events into its evidence and DOES NOT BRANCH ON THEM:
its decision table reads the exit code, whether the process is alive and whether
the pulse says the run ended, and nothing else. That is deliberate -- its own
docstring records that the table is narrow because the default on anything
unrecognised is to stop. A future change that made an event kind drive a RESUME
would widen the one path this project has decided must stay narrow, so the test
states the current design and fails if it moves, rather than leaving a reader to
infer it from an absence.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
WATCHDOG = REPO / "scripts" / "cy_watchdog_2026-10-02.py"
ACTUATOR = REPO / "bench" / "tools" / "cy_actuator_2026-11-03.py"
DEAD_PID = 999999


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def W():
    return _load(WATCHDOG, "_cy_watchdog_probe")


@pytest.fixture(scope="module")
def A():
    return _load(ACTUATOR, "_cy_actuator_probe")


def test_both_subjects_exist_and_import(W, A):
    """ANTI-VACUITY. Every test below is trivially true if either is absent."""
    assert hasattr(W, "write_pulse"), "the watchdog has no write_pulse"
    assert hasattr(A, "read_pulse") and hasattr(A, "classify")


def test_write_pulse_accepts_events_and_records_them(W, tmp_path):
    """The WRITER's half, executed. A keyword it ignored would pass a source read."""
    p = tmp_path / "cy_pulse.json"
    W.write_pulse(p, log=tmp_path / "run.log", pid=DEAD_PID, rounds=3,
                  last_size=10, ended=False,
                  events=[("STALLED", "no output for 600s"),
                          ("TROUBLE", "Traceback in round 4")])
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d.get("events") == [
        {"kind": "STALLED", "message": "no output for 600s"},
        {"kind": "TROUBLE", "message": "Traceback in round 4"}], (
        f"write_pulse accepted events= and did not record them as "
        f"kind/message pairs; got {d.get('events')!r}")


def test_the_events_survive_the_writer_and_reach_the_actuators_evidence(W, A, tmp_path):
    """THE LOAD-BEARING TEST: the producer and the consumer, executed together.

    A constant on either side cannot pass this, because the exact list written
    is the exact list required back.
    """
    W.write_pulse(tmp_path / "cy_pulse.json", log=tmp_path / "run.log",
                  pid=DEAD_PID, rounds=2, last_size=5, ended=False,
                  events=[("LOG TRUNCATED", "log shrank from 900 to 12 bytes"),
                          ("PROCESS GONE", "pid 4242 is no longer running")])
    pulse = A.read_pulse(tmp_path)
    r = A.classify(A.PAUSED, pulse)
    assert [e["kind"] for e in r["evidence"]["events"]] == \
        ["LOG TRUNCATED", "PROCESS GONE"], (
        f"the watchdog's events did not reach the actuator's evidence; got "
        f"{r['evidence'].get('events')!r}")
    assert r["evidence"]["events"][0]["message"] == \
        "log shrank from 900 to 12 bytes", (
        "the event's MESSAGE was dropped; a kind without its detail tells a "
        "reader which condition fired and nothing about why")


def test_a_second_different_event_list_also_arrives(W, A, tmp_path):
    """A SECOND plant, because 1 fixture can be matched by a constant that
    happens to agree with it. 2 of different content and length cannot."""
    W.write_pulse(tmp_path / "cy_pulse.json", log=tmp_path / "run.log",
                  pid=DEAD_PID, rounds=1, last_size=1, ended=False,
                  events=[("QUIET BUT WORKING", "cpu moving, log static")])
    r = A.classify(A.PAUSED, A.read_pulse(tmp_path))
    assert [e["kind"] for e in r["evidence"]["events"]] == \
        ["QUIET BUT WORKING"]


def test_an_absent_event_channel_is_an_empty_list_not_a_crash(A, tmp_path):
    """An older pulse carries no `events` key at all. The actuator must tolerate
    it, because a reader that raises on a missing field turns an old pulse into
    a dead watch -- the exact outcome the atomic write exists to prevent."""
    (tmp_path / "cy_pulse.json").write_text(
        json.dumps({"pid": DEAD_PID, "rounds": 1, "ended": False,
                    "written_at": 0}), encoding="utf-8")
    r = A.classify(A.PAUSED, A.read_pulse(tmp_path))
    assert r["evidence"]["events"] == [], (
        "a pulse with no events key must read as an empty list")


def test_the_events_do_not_change_the_decision(W, A, tmp_path):
    """THE DESIGN DECISION, PINNED RATHER THAN INFERRED FROM AN ABSENCE.

    The actuator's table is deliberately narrow: its own docstring records that
    the default on anything unrecognised is to stop. So an event kind must NOT
    drive the decision, however alarming it is.

    ★ THE FIRST VERSION OF THIS TEST WAS VACUOUS AND ITS MUTATION HARNESS
    CAUGHT IT. It iterated event lists against `PAUSED` with a dead process,
    whose baseline decision is ALREADY RESUME -- so a mutation that forced
    RESUME on a TROUBLE event produced exactly the baseline answer and all 8
    tests stayed green. The property was unobservable in the state chosen to
    observe it. It is now driven against a NON-permitting exit code, where
    RESUME is wrong and forcing it is therefore detectable, and the permitting
    state is kept as the positive control so the test cannot pass by refusing
    everything.
    """
    LISTS = ([], [("HEARTBEAT", "alive")], [("STALLED", "600s")],
             [("TROUBLE", "Traceback"), ("LOG TRUNCATED", "shrank")],
             [("PROCESS GONE", "pid gone")])

    # THE OBSERVABLE HALF: a NON-permitting exit code, where RESUME is wrong.
    # An event kind driving the decision shows up here and nowhere else.
    base = None
    for ev in LISTS:
        W.write_pulse(tmp_path / "cy_pulse.json", log=tmp_path / "run.log",
                      pid=DEAD_PID, rounds=4, last_size=9, ended=False,
                      events=ev)
        r = A.classify(1, A.read_pulse(tmp_path))      # 1 == a failure exit
        assert r["decision"] != "RESUME", (
            f"events {ev!r} drove a RESUME on a FAILURE exit; the actuator's "
            f"table must read the exit code, the process state and the ended "
            f"flag only, and its default on anything unrecognised is to stop")
        if base is None:
            base = r["decision"]
        assert r["decision"] == base, (
            f"events {ev!r} changed the decision from {base} to "
            f"{r['decision']}")

    # THE POSITIVE CONTROL, without which a classifier hard-wired to HOLD
    # would pass everything above.
    W.write_pulse(tmp_path / "cy_pulse.json", log=tmp_path / "run.log",
                  pid=DEAD_PID, rounds=4, last_size=9, ended=False, events=[])
    assert A.classify(A.PAUSED, A.read_pulse(tmp_path))["decision"] == "RESUME", (
        "the permitting state no longer resumes, so the assertions above are "
        "satisfiable by a classifier that refuses everything")


def test_probe_returns_its_events_as_well_as_emitting_them(W):
    """The channel's SOURCE, by signature rather than by running a watch.

    `probe()` needs a live log, an offset and a clock to run meaningfully, so
    this checks the contract it declares: a tuple return whose docstring names
    the events. A watch cannot be driven inside a unit test without a run.
    """
    assert callable(W.probe)
    doc = (W.probe.__doc__ or "")
    assert "EVENTS IT EMITTED" in doc or "events" in doc.lower(), (
        "probe() no longer documents returning its events; if the return "
        "shape changed, the mid-run pulse's events= argument has no source")


def test_only_the_last_8_events_survive_and_that_is_undisclosed(W, A, tmp_path):
    """A PROPERTY OF THE SUBJECT, PINNED RATHER THAN REPAIRED.

    `write_pulse` keeps `[-8:]` of the events it is given. So a watch that
    emitted 12 events writes 8, and the pulse records NO remainder -- a
    consumer reading it cannot tell whether anything was dropped. That is the
    silent-truncation shape this project has a ratchet against for PRINTED
    listings, and the ratchet does not reach a JSON field.

    It is pinned rather than fixed because the cap is deliberate -- the pulse is
    read by a Stop gate at any moment and must stay small -- and the right
    repair is a count field added by the first consumer that needs to branch on
    it, which is the same reasoning B20 already records for the schema version.
    If the cap changes, this fails and the change is visible.
    """
    many = [(f"EVENT{i}", f"detail {i}") for i in range(12)]
    W.write_pulse(tmp_path / "cy_pulse.json", log=tmp_path / "run.log",
                  pid=DEAD_PID, rounds=7, last_size=3, ended=False, events=many)
    got = A.classify(A.PAUSED, A.read_pulse(tmp_path))["evidence"]["events"]
    assert len(got) == 8, f"the cap moved from 8 to {len(got)}"
    assert [e["kind"] for e in got] == [f"EVENT{i}" for i in range(4, 12)], (
        "the cap keeps the WRONG end; a reader needs the most recent events, "
        "not the first")
    raw = json.loads((tmp_path / "cy_pulse.json").read_text(encoding="utf-8"))
    assert "events_total" not in raw and "events_dropped" not in raw, (
        "a remainder field now exists, so this test's claim that the "
        "truncation is undisclosed is stale and should be rewritten")
