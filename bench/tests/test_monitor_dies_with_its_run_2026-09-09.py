"""A monitor must exit when its run exits, and never signal the run.

Task 6.5. Founder ruling: *"So again what's the fix? Did you consult the other
models yet? If not same as the last answer."*

WHY IT MATTERS TO THE FOUNDER DIRECTLY. The standing `cy` directive requires a
terminal kept open on the running experiment's full current output. Nothing tied
that terminal's lifetime to the run: 0 launchers clean up a monitor, and the only
process-id file written -- by `bench/detached_launch.sh:11` -- is read by
`scripts/cdsfl_recover.py` to REPORT whether an experiment is running, never to
stop anything. A monitor therefore outlives its run, and a quiet tail cannot be
told from a finished one.

WHY A WRAPPER. GNU `tail --pid` does exactly this and macOS `tail` has no such
flag: measured, `tail --pid=1 /dev/null` returns "unrecognized option" and the
flag appears 0 times in `man tail`. No `gtail` is installed.

EVERY TEST HERE RUNS THE SCRIPT against a real background process. None reads its
source: a shell script that describes itself correctly and behaves wrongly is
exactly what `execute-do-not-grep` is about, and a monitor's whole contract is
behavioural.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bench" / "tail_until_done.sh"


def _spawn_writer(log: Path, seconds: float):
    """A stand-in run: writes to the log, then exits on its own."""
    code = (
        "import sys,time\n"
        f"end=time.time()+{seconds}\n"
        "i=0\n"
        "while time.time()<end:\n"
        "    i+=1; print(f'round {i}', flush=True); time.sleep(0.2)\n"
        "print('FINAL LINE', flush=True)\n"
    )
    fh = open(log, "w", encoding="utf-8")
    return subprocess.Popen([sys.executable, "-c", code], stdout=fh, stderr=fh), fh


def _run_monitor(log, pid, timeout):
    env = {**os.environ, "POLL_SECONDS": "1", "FLUSH_SECONDS": "1",
           "WAIT_FOR_PIDFILE": "3"}
    return subprocess.run(["bash", str(SCRIPT), str(log), str(pid)],
                          capture_output=True, text=True, timeout=timeout, env=env)


def test_the_script_exists_and_is_executable():
    assert SCRIPT.is_file()
    assert os.access(SCRIPT, os.X_OK), "a monitor nobody can run is not a monitor"


def test_it_exits_when_the_run_exits(tmp_path):
    """THE PROPERTY. Without the tie this call never returns."""
    log = tmp_path / "run.log"
    proc, fh = _spawn_writer(log, 2.0)
    try:
        t0 = time.time()
        r = _run_monitor(log, proc.pid, timeout=30)
        elapsed = time.time() - t0
    finally:
        proc.wait(timeout=10)
        fh.close()
    assert r.returncode == 0, r.stderr
    assert elapsed < 25, f"the monitor outlived its run by {elapsed:.1f}s"
    assert "has exited; monitor closed" in r.stdout


def test_it_shows_the_final_lines_before_closing(tmp_path):
    """The most interesting lines in this project are usually the last ones."""
    log = tmp_path / "run.log"
    proc, fh = _spawn_writer(log, 1.5)
    try:
        r = _run_monitor(log, proc.pid, timeout=30)
    finally:
        proc.wait(timeout=10)
        fh.close()
    assert "FINAL LINE" in r.stdout, (
        "the monitor closed before tail flushed the run's last output")


def test_it_never_signals_the_run(tmp_path):
    """A monitor that can stop an experiment is a hazard, not a feature."""
    # THE WRITER MUST OUTLIVE THE WHOLE INTERACTION BY A CLEAR MARGIN.
    # A first version gave it 3.0s and the assertion failed at about t=3.0s,
    # because bash only runs the TERM trap after the current `sleep` returns.
    # The return code settled which it was: `poll()` gave 0, a clean exit, where
    # a monitor that had killed the run would leave -15. So it was this test's
    # timing, not the script -- but the margin is now wide enough that a real
    # regression is what fails here, not a stopwatch.
    log = tmp_path / "run.log"
    proc, fh = _spawn_writer(log, 12.0)
    try:
        env = {**os.environ, "POLL_SECONDS": "1", "FLUSH_SECONDS": "1"}
        mon = subprocess.Popen(["bash", str(SCRIPT), str(log), str(proc.pid)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, env=env)
        time.sleep(1.5)
        assert proc.poll() is None, "the run died while the monitor was attached"
        mon.send_signal(signal.SIGTERM)          # the founder closing the window
        mon.wait(timeout=15)
        time.sleep(1.0)
        rc = proc.poll()
        assert rc is None, (
            f"killing the monitor ended the run (returncode {rc}); a monitor "
            f"must be read-only. A negative code means it was signalled.")
    finally:
        proc.kill(); proc.wait(timeout=10); fh.close()


def test_a_missing_log_is_refused_not_tailed(tmp_path):
    r = subprocess.run(["bash", str(SCRIPT), str(tmp_path / "nope.log"), "1"],
                       capture_output=True, text=True, timeout=20)
    assert r.returncode == 2, (r.returncode, r.stderr)


def test_an_unresolvable_pid_is_refused_rather_than_tailed_untethered(tmp_path):
    """REFUSING IS THE POINT. Tailing anyway would recreate the defect while
    appearing to fix it -- an untied monitor with a reassuring name."""
    log = tmp_path / "run.log"
    log.write_text("something\n", encoding="utf-8")
    env = {**os.environ, "WAIT_FOR_PIDFILE": "1"}
    r = subprocess.run(["bash", str(SCRIPT), str(log)],
                       capture_output=True, text=True, timeout=20, env=env)
    assert r.returncode == 3, (r.returncode, r.stdout, r.stderr)
    assert "refusing to tail untethered" in r.stderr


def test_a_pidfile_is_read_the_way_the_launcher_writes_it(tmp_path):
    """`bench/detached_launch.sh` writes "${LOG%.log}.pid"; the default must match."""
    log = tmp_path / "run.log"
    proc, fh = _spawn_writer(log, 1.5)
    (tmp_path / "run.pid").write_text(f"{proc.pid}\n", encoding="utf-8")
    try:
        env = {**os.environ, "POLL_SECONDS": "1", "FLUSH_SECONDS": "1"}
        r = subprocess.run(["bash", str(SCRIPT), str(log)],
                           capture_output=True, text=True, timeout=30, env=env)
    finally:
        proc.wait(timeout=10); fh.close()
    assert r.returncode == 0, r.stderr
    assert f"tied to run {proc.pid}" in r.stdout


def test_an_already_finished_run_prints_the_tail_and_exits(tmp_path):
    """The common case after a long break: the run ended hours ago."""
    log = tmp_path / "run.log"
    log.write_text("line 1\nline 2\nlast line\n", encoding="utf-8")
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait(timeout=10)
    r = subprocess.run(["bash", str(SCRIPT), str(log), str(dead.pid)],
                       capture_output=True, text=True, timeout=20)
    assert r.returncode == 0
    assert "last line" in r.stdout and "is not alive" in r.stdout


def test_it_stops_promptly_when_the_founder_closes_the_window(tmp_path):
    """A MONITOR THAT WILL NOT STOP IS THE SAME DEFECT WEARING A NEW NAME.

    The first version of the wrapper used a single trap for EXIT, INT and TERM
    that killed the tail and nothing else. Bash then RESUMED the polling loop,
    so ctrl-C was ignored and the wrapper waited until the run ended on its own.
    Measured: SIGTERM at t=1.5s against a 12-second stand-in run, and the
    wrapper returned at t=13.5s. `test_it_never_signals_the_run` could not see
    this -- it asserts what the monitor must NOT do, and a monitor that does
    nothing passes that test perfectly.

    So this asserts the other half: it must stop, and stop soon."""
    log = tmp_path / "run.log"
    proc, fh = _spawn_writer(log, 12.0)
    try:
        env = {**os.environ, "POLL_SECONDS": "1", "FLUSH_SECONDS": "1"}
        t0 = time.time()
        mon = subprocess.Popen(["bash", str(SCRIPT), str(log), str(proc.pid)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, env=env)
        time.sleep(1.5)
        mon.send_signal(signal.SIGTERM)
        rc = mon.wait(timeout=20)
        elapsed = time.time() - t0
        assert elapsed < 6.0, (
            f"the monitor took {elapsed:.1f}s to honour SIGTERM; it is waiting "
            f"for the run to finish instead of closing")
        assert rc == 143, f"expected the conventional SIGTERM code, got {rc}"
        assert proc.poll() is None, "the run was touched"
    finally:
        proc.kill(); proc.wait(timeout=10); fh.close()


def test_the_launcher_names_the_monitor():
    """WIRED, not merely written.

    An addition nothing reaches is not additive. `bench/detached_launch.sh` is
    the only moment an operator has both the log path and the process id in
    front of them, so that is where the monitor command belongs. This asserts
    the launcher names it; without this the script is a file nobody is told
    about, which is the unwired-addition half of the additive standard."""
    launcher = (REPO / "bench" / "detached_launch.sh").read_text(encoding="utf-8")
    assert "tail_until_done.sh" in launcher, (
        "the launcher does not name the monitor, so nothing tells an operator "
        "it exists")


def test_it_waits_for_the_flush_window_before_closing(tmp_path):
    """THE FLUSH, tested by its timing rather than by hoping to win a race.

    `test_it_shows_the_final_lines_before_closing` does not actually exercise
    this: mutation testing removed the flush entirely and that test stayed green,
    because macOS `tail -f` uses kqueue and usually picks up the last write
    before the 1-second poll notices the process has gone. "Usually" is the word
    this project has learned to distrust, and a run whose final lines land in the
    same instant it exits is exactly the case the flush exists for -- the most
    interesting lines here are nearly always the last ones.

    So this asserts the observable contract: the monitor must still be alive at
    least FLUSH_SECONDS after the run ends. It is a timing assertion, which is
    why the window is set wide (4s) and the bound is checked loosely (3s)."""
    log = tmp_path / "run.log"
    proc, fh = _spawn_writer(log, 1.0)
    try:
        env = {**os.environ, "POLL_SECONDS": "1", "FLUSH_SECONDS": "4"}
        mon = subprocess.Popen(["bash", str(SCRIPT), str(log), str(proc.pid)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, env=env)
        proc.wait(timeout=15)
        t_run_ended = time.time()
        mon.wait(timeout=30)
        held = time.time() - t_run_ended
    finally:
        fh.close()
    assert held >= 3.0, (
        f"the monitor closed {held:.1f}s after the run ended, inside its "
        f"4-second flush window; output written in the run's final instant "
        f"would be lost")
