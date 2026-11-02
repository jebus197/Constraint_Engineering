#!/usr/bin/env python3
"""The cy Stop gate must REFUSE while a run is live, and be silent otherwise.

HIS INSTRUCTION, 2026-11-02: *"First fix cy so it can't fail again."*

WHY THIS FILE EXECUTES THE HOOK AS A SUBPROCESS rather than importing it. The
thing being guarded is the hook's EXIT CODE -- 2 blocks a stop, 0 allows it --
and an exit code is a property of a process, not of a function. Importing and
calling `main()` would test a different artefact from the one Claude Code runs.
That is the `execute-do-not-grep` rule applied to the deciding layer:
`feedback_verify_the_deciding_layer` records 4 failures in one night where 2 of
the tests verified nothing.

WHY A GUARD MUST NOT NEED A LIVE DEFECT, which is the other half of this file.
`feedback_a_regression_guard_must_not_need_a_live_defect_2026-10-31` records 0
of 625 guards blocking because each waited on a real failure to assert against.
Every state here is PLANTED, so the gate's refusal is proven without a running
experiment -- and the negative cases are proven too, because a gate that refuses
everything is as useless as one that refuses nothing.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time

import pytest

HOOK = pathlib.Path.home() / ".claude" / "hooks" / "cy_monitor_gate.py"
PAYLOAD = json.dumps({"session_id": "test-session", "transcript_path": "/dev/null"})


def run(tmp_path, *, parked=False, state=None, env_extra=None):
    """Execute the hook against a planted log tree. Returns (exit, stderr)."""
    env = dict(os.environ)
    env["CDSFL_CY_LOGS"] = str(tmp_path / "logs")
    env["CDSFL_CY_NO_PGREP"] = "1"
    env["CDSFL_CY_PARKED"] = str(tmp_path / ("PARKED" if parked else "NOT_PARKED"))
    env["CDSFL_CY_STATE"] = str(state or (tmp_path / "state.json"))
    if parked:
        (tmp_path / "PARKED").write_text("")
    if env_extra:
        env.update(env_extra)
    p = subprocess.run([sys.executable, str(HOOK)], input=PAYLOAD,
                       capture_output=True, text=True, env=env, timeout=30)
    return p.returncode, p.stderr


def plant(tmp_path, name="study_run_x", *, age=5.0, ended=False,
          pid=None, rounds=3):
    """Write a pulse file describing a run. `pid` defaults to THIS process,
    which is certainly alive -- a test that planted a made-up pid would be
    testing the pid lookup, not the gate."""
    d = tmp_path / "logs" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "cy_pulse.json").write_text(json.dumps({
        "schema": 1, "written_at": time.time() - age,
        "log": str(d / "console.log"), "pid": pid if pid is not None else os.getpid(),
        "pid_alive": True, "rounds": rounds, "log_bytes": 1234,
        "interval_seconds": 60, "ended": ended, "verdict": None,
    }))
    return d


@pytest.fixture(autouse=True)
def _hook_exists():
    assert HOOK.is_file(), f"the hook is not installed at {HOOK}"


# ---- the refusal, which is the whole point -------------------------------
def test_a_fresh_live_pulse_refuses_the_stop(tmp_path):
    plant(tmp_path, age=5.0)
    code, err = run(tmp_path)
    assert code == 2, f"a live run must block the stop; got {code}\n{err}"
    assert "A RUN IS STILL LIVE" in err
    assert "study_run_x" in err, "the refusal must NAME the run"


def test_the_refusal_names_the_delivery_channel_that_works(tmp_path):
    plant(tmp_path)
    _, err = run(tmp_path)
    assert "Monitor" in err, "it must name the channel that delivers"
    assert "tail -f" in err, "and the one that does not, so it is not re-tried"


def test_a_stale_pulse_with_a_live_pid_says_the_WATCH_is_dead(tmp_path):
    # 600 s > PULSE_STALE_SECONDS (180): the watchdog has stopped writing while
    # the run itself is still going. That is WORSE than a healthy watch.
    plant(tmp_path, age=600.0)
    code, err = run(tmp_path)
    assert code == 2
    assert "WATCH DEAD" in err
    assert "cy_watchdog_2026-10-02.py" in err, "it must say how to re-arm"


# ---- and the silences, because a gate that always refuses is useless -----
def test_no_pulse_at_all_is_silent(tmp_path):
    (tmp_path / "logs").mkdir(parents=True)
    code, err = run(tmp_path)
    assert code == 0 and err.strip() == "", f"must be silent; got {code} {err!r}"


def test_an_ended_run_is_silent(tmp_path):
    plant(tmp_path, ended=True)
    code, err = run(tmp_path)
    assert code == 0, f"the watch said the run ended; got {code}\n{err}"


def test_a_dead_pid_is_silent(tmp_path):
    # pid 1 exists; a pid that cannot exist is what we need. 2**22 is above
    # macOS's pid ceiling, so os.kill raises ProcessLookupError.
    plant(tmp_path, pid=2 ** 22)
    code, err = run(tmp_path)
    assert code == 0, f"the run's process is gone; got {code}\n{err}"


def test_an_unknown_pid_counts_as_LIVE_not_dead(tmp_path):
    """FOUND BY THE MUTATION TEST, 2026-11-02, as a hole in this very file.

    Inverting `pid_alive`'s unknown-pid default from True to False left this
    suite GREEN, so the most dangerous direction was unguarded: a pulse whose
    pid is null would make the gate go SILENT on a run it merely could not
    identify. "I could not tell" must never read as "it is over" --
    `feedback_a_signal_is_not_a_measurement_2026-10-30`: ask what a 0 is a 0 OF.
    """
    d = tmp_path / "logs" / "pid_unknown"
    d.mkdir(parents=True)
    (d / "cy_pulse.json").write_text(json.dumps({
        "schema": 1, "written_at": time.time() - 5,
        "log": str(d / "console.log"), "pid": None, "rounds": 2,
        "log_bytes": 10, "interval_seconds": 60, "ended": False}))
    code, err = run(tmp_path)
    assert code == 2, f"an unidentifiable run must still refuse; got {code}\n{err}"


def test_a_long_abandoned_pulse_is_silent(tmp_path):
    plant(tmp_path, age=40 * 3600)          # > MAX_PULSE_AGE_HOURS (36)
    code, err = run(tmp_path)
    assert code == 0, "an abandoned pulse must not refuse stops for ever"


def test_parking_silences_it_immediately(tmp_path):
    plant(tmp_path)
    code, err = run(tmp_path, parked=True)
    assert code == 0 and err.strip() == ""


def test_the_budget_is_bounded_so_a_session_cannot_be_trapped(tmp_path):
    plant(tmp_path)
    st = tmp_path / "state.json"
    codes = [run(tmp_path, state=st)[0] for _ in range(63)]
    assert codes[0] == 2, "it must refuse at first"
    assert codes[-1] == 0, "and yield once the budget is spent"
    assert 2 in codes and 0 in codes


# ---- the properties the sibling hook failed on ---------------------------
def test_it_is_fast_enough_for_the_fifteen_second_hook_timeout(tmp_path):
    plant(tmp_path)
    t0 = time.perf_counter()
    run(tmp_path)
    dt = time.perf_counter() - t0
    # work_not_narrate.py decided correctly and was killed 153 of 360 times
    # because it read a 653 MiB transcript 3 times. 2 s leaves 7.5x of headroom
    # against the harness's 15 s, including interpreter start-up.
    assert dt < 2.0, f"too slow for a Stop hook: {dt:.3f} s"


def test_it_never_reads_the_transcript(tmp_path):
    src = HOOK.read_text()
    assert "transcript_path" not in src.split("def main")[-1] or \
        "read_text" not in src.split("def main")[-1], \
        "this hook must not read the transcript; that is what killed its sibling"


def test_a_corrupt_pulse_does_not_crash_the_gate(tmp_path):
    d = tmp_path / "logs" / "broken"
    d.mkdir(parents=True)
    (d / "cy_pulse.json").write_text("{not json at all")
    code, err = run(tmp_path)
    assert code == 0, f"a half-written pulse must not refuse or crash; {err}"
    # AND IT MUST BE SKIPPED, NOT CAUGHT. Asserting only on the exit code left
    # this test GREEN when the inner `continue` was mutated to `raise`: the
    # outer handler caught it and still exited 0. An exception that reaches the
    # top is a DIFFERENT outcome from a file being skipped, and the difference
    # is visible only here -- `feedback_a_swallowed_exception_is_not_a_record`.
    assert "internal error" not in err, (
        f"the corrupt pulse must be SKIPPED, not caught at the top: {err!r}")
    assert err.strip() == "", f"and the gate must stay silent: {err!r}"


def test_a_live_run_beside_a_finished_one_still_refuses(tmp_path):
    plant(tmp_path, name="finished", ended=True)
    plant(tmp_path, name="still_going", age=10.0)
    code, err = run(tmp_path)
    assert code == 2
    assert "still_going" in err
    assert "finished" not in err.split("LIVE:")[-1]
