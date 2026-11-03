"""The watchdog's events reach a machine-readable channel, not just stdout.

B20's PRECONDITION, built 2026-11-03 on his authorisation: *"You can go ahead
with the orchestrator build"* and *"The actuator is something you should
probably build and implement first I suspect however."*

THE DEFECT. `probe()` is documented as returning new state and emitting events
for what changed, and that is exactly what it did: an event name reached stdout
through `say()` and NEITHER the return value NOR the pulse file. The mid-run
`write_pulse` passed no `verdict` and no `detail`, so while a run was live the
pulse carried liveness alone and only the FINAL write after the loop exited
carried an outcome. An actuator had no machine-readable way to learn WHICH
event fired, and would have had to parse prose.

WHY NOT PARSE STDOUT. This project has a recorded defect of exactly that shape:
a verdict reader matched `NOT FALSIFIED` as `FALSIFIED`. An actuator that pauses
a live experiment on a regex over prose is the worst place to put that risk.

THE LOAD-BEARING TEST IS `test_stdout_and_the_return_value_agree`. It executes
both forms against each other rather than trusting either, which is the positive
form of `execute-do-not-grep`. A future `say()` added inside `probe()` without
recording would leave an event on stdout and absent from the return, and ONLY a
comparison of the 2 can see that. Asserting that the list is non-empty cannot.

ANTI-VACUITY. A quiet tick must return an EMPTY list, so the non-empty
assertions elsewhere are not trivially satisfied by a recorder that appends
unconditionally.

AND THE GATE'S VERDICT MUST NOT MOVE. `hooks/cy_monitor_gate.py` reads the pulse
for LIVENESS ONLY -- written age, the ended flag, whether the pid is alive -- and
has no use for which event fired. Adding a key must not change what it decides,
which is the `additive` half of this change and is asserted rather than assumed.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import re
import sys
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
WD = REPO / "scripts" / "cy_watchdog_2026-10-02.py"


@pytest.fixture(scope="module")
def wd():
    spec = importlib.util.spec_from_file_location("_wd_events", WD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_wd_events"] = m
    spec.loader.exec_module(m)
    return m


def _probe(wd, log, **kw):
    return wd.probe(log, kw.pop("pid", os.getpid()), kw.pop("offset", 0),
                    kw.pop("last_size", 0), kw.pop("last_change", time.time()),
                    kw.pop("rounds", 0), kw.pop("stall_s", 3600),
                    None, None, first=kw.pop("first", False))


class TestProbeReturnsItsEvents:
    def test_the_return_carries_a_seventh_element(self, wd, tmp_path):
        log = tmp_path / "r.log"
        log.write_text("RuntimeError: seat crashed\n")
        r = _probe(wd, log)
        assert len(r) == 7, (
            f"probe returned {len(r)} elements; the events channel is the 7th "
            f"and an actuator has nothing to read without it")
        assert isinstance(r[6], list)

    def test_an_emitted_event_is_in_the_return(self, wd, tmp_path):
        log = tmp_path / "r.log"
        log.write_text("Traceback (most recent call last):\n")
        events = _probe(wd, log)[6]
        assert events, "an event was emitted and nothing came back"
        assert all(isinstance(e, tuple) and len(e) == 2 for e in events), events
        assert any(k == "TROUBLE" for k, _ in events), events

    def test_a_quiet_tick_returns_an_empty_list(self, wd, tmp_path):
        """ANTI-VACUITY. A recorder that appends unconditionally would make
        every other assertion here pass for the wrong reason."""
        log = tmp_path / "quiet.log"
        log.write_text("round 1 fine\n")
        r = _probe(wd, log, stall_s=10 ** 6)
        quiet = [e for e in r[6] if e[0] not in ("PROGRESS",)]
        assert quiet == [], f"a quiet tick emitted {quiet}"

    def test_stdout_and_the_return_value_agree(self, wd, tmp_path, capsys):
        """THE LOAD-BEARING TEST: the 2 forms are executed against each other.

        Every event on stdout must appear in the return and vice versa. A
        `say()` added inside probe without recording is invisible to any test
        that only checks the list is non-empty.
        """
        log = tmp_path / "r.log"
        log.write_text("Traceback (most recent call last):\n"
                       "RuntimeError: seat crashed\n"
                       "AssertionError: another\n")
        capsys.readouterr()
        events = _probe(wd, log)[6]
        out = capsys.readouterr().out
        on_stdout = re.findall(r"^\[cy \d\d:\d\d:\d\d\] ([A-Z][A-Z ]*): ", out, re.M)
        returned = [k for k, _ in events]
        assert on_stdout, f"nothing reached stdout at all: {out!r}"
        assert sorted(on_stdout) == sorted(returned), (
            f"stdout and the return DISAGREE.\n  stdout  : {sorted(on_stdout)}\n"
            f"  returned: {sorted(returned)}\n"
            f"An event on one and not the other means an emission inside "
            f"probe() is not recorded, which is the defect this guard exists "
            f"to catch.")

    def test_the_process_gone_path_also_returns_events(self, wd, tmp_path):
        """probe() has 2 return statements and both must carry the channel."""
        log = tmp_path / "r.log"
        log.write_text("x\n")
        r = _probe(wd, log, pid=2 ** 22)     # a pid that cannot be running
        assert len(r) == 7, "the PROCESS GONE return dropped the events"
        assert any(k == "PROCESS GONE" for k, _ in r[6]), r[6]


class TestThePulseCarriesThem:
    def test_the_pulse_holds_the_events(self, wd, tmp_path):
        p = tmp_path / "cy_pulse.json"
        wd.write_pulse(p, log=tmp_path / "r.log", pid=os.getpid(), rounds=2,
                       last_size=9, ended=False,
                       events=[("TROUBLE", "a"), ("STALLED", "b")])
        body = json.loads(p.read_text())
        assert [e["kind"] for e in body["events"]] == ["TROUBLE", "STALLED"]

    def test_verdict_is_not_overloaded_by_a_mid_run_event(self, wd, tmp_path):
        """`verdict` means the FINAL outcome. A mid-run event is not a result,
        and conflating the 2 is how a reader treats one as the other."""
        p = tmp_path / "cy_pulse.json"
        wd.write_pulse(p, log=tmp_path / "r.log", pid=os.getpid(), rounds=1,
                       last_size=1, ended=False, events=[("TROUBLE", "a")])
        body = json.loads(p.read_text())
        assert body["verdict"] is None, (
            "a mid-run event was written into `verdict`, which means the final "
            "outcome")
        assert body["events"], "and the events channel was left empty"

    def test_no_events_still_writes_a_valid_pulse(self, wd, tmp_path):
        p = tmp_path / "cy_pulse.json"
        wd.write_pulse(p, log=tmp_path / "r.log", pid=os.getpid(), rounds=0,
                       last_size=0, ended=False)
        body = json.loads(p.read_text())
        assert body["events"] == []

    def test_the_channel_is_bounded(self, wd, tmp_path):
        """A pulse a Stop gate reads on every stop must not grow without
        bound, and a message must not carry an unbounded line either."""
        p = tmp_path / "cy_pulse.json"
        wd.write_pulse(p, log=tmp_path / "r.log", pid=os.getpid(), rounds=0,
                       last_size=0, ended=False,
                       events=[("TROUBLE", "x" * 5000)] * 50)
        body = json.loads(p.read_text())
        assert len(body["events"]) <= 8, len(body["events"])
        assert all(len(e["message"]) <= 300 for e in body["events"])


class TestTheGateVerdictIsUnchanged:
    """The additive half: adding a key must not move what the gate decides."""

    @pytest.fixture(scope="class")
    def gate(self):
        g = REPO / "hooks" / "cy_monitor_gate.py"
        if not g.is_file():
            pytest.skip("the gate is not present in this checkout")
        spec = importlib.util.spec_from_file_location("_gate_events", g)
        m = importlib.util.module_from_spec(spec)
        sys.modules["_gate_events"] = m
        spec.loader.exec_module(m)
        return m

    def test_a_pulse_with_and_without_events_reads_the_same(self, gate, wd,
                                                            tmp_path, monkeypatch):
        logs = tmp_path / "logs"
        run = logs / "run_a"
        run.mkdir(parents=True)
        monkeypatch.setenv("CDSFL_CY_LOGS", str(logs))
        monkeypatch.setenv("CDSFL_CY_NO_PGREP", "1")

        pulse = run / "cy_pulse.json"
        wd.write_pulse(pulse, log=run / "r.log", pid=os.getpid(), rounds=3,
                       last_size=10, ended=False)
        bare_live, bare_unwatched = gate.live_runs()

        wd.write_pulse(pulse, log=run / "r.log", pid=os.getpid(), rounds=3,
                       last_size=10, ended=False,
                       events=[("TROUBLE", "a"), ("STALLED", "b")])
        rich_live, rich_unwatched = gate.live_runs()

        assert len(bare_live) == len(rich_live) == 1, (bare_live, rich_live)
        assert not bare_unwatched and not rich_unwatched
        assert ([(r["dir"], r["rounds"], r["pid"]) for r in bare_live]
                == [(r["dir"], r["rounds"], r["pid"]) for r in rich_live]), (
            "the gate's reading of a live run changed when the events key was "
            "added, so the change is not additive")
