"""A simulated run must outlive the session that launched it.

THE LOST RUN THIS EXISTS TO PREVENT RECURRING. The founder's detached-launch
directive has stood since 2026-07-29: every experiment runner launches so that it
survives the Claude Code host, and "logs are the only tether".
`bench/detached_launch.sh` implements it -- but only for `bench/launch_exp42.py`,
whose config argument and flags it hardcodes at line 8. The SIMULATED path runs
through `bench/tools/run_simulated_experiment_sandboxed.sh`, and nothing detached
it: `commissioning_arms_2026-09-21.py --run` used `subprocess.call`, which blocks
and dies with its parent.

Measured, 2026-09-29: the shakedown's arm 1 reached round 5 of 8 and died at
18:53:47 when the launching session ended. 50 evidence files were harvested, so
rounds 0 to 4 survived as data, but the run did not finish. The directive was in
force the whole time and had no wrapper for the path actually being used -- the
same shape as `boundary_band_sensitivity` and `EXTEND`: a rule with no executing
caller on the route that matters.

THIS FILE EXECUTES THE MECHANISM (`execute-do-not-grep`, founder ruling
2026-09-04). It detaches a real child process with a harmless payload and then
checks the properties that matter -- new session, pidfile, log tether, survival of
the parent's own process group being signalled. A test that read the source for
the string "start_new_session" would pass against a call that was never made.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LAUNCHER = REPO / "bench" / "tools" / "commissioning_arms_2026-09-21.py"
sys.path.insert(0, str(REPO / "bench" / "tools"))

import importlib.util  # noqa: E402


def _load(path: Path, name: str):
    """Register in sys.modules BEFORE exec_module.

    `dataclasses` resolves a class's own module through `sys.modules` while
    processing the decorator, so a module loaded by path without being registered
    raises `AttributeError: 'NoneType' object has no attribute '__dict__'` from
    inside dataclasses.py. It reads like a bug in the module under test and is a
    bug in the loader. The same helper and the same comment already sit in
    `test_commissioning_arms_carry_their_settings_2026-09-21.py`, which is where
    this was first hit.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


_mod = _load(LAUNCHER, "commissioning_arms")


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _reap(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGKILL)
    except Exception:                                         # noqa: BLE001
        pass


@pytest.fixture
def detached(tmp_path):
    """A real detached child whose payload is a print and a sleep."""
    log = tmp_path / "arms.log"
    pid = _mod.detach(
        [sys.executable, "-u", "-c",
         "import time,sys; print('DETACHED-OK'); sys.stdout.flush(); time.sleep(30)"],
        log)
    deadline = time.time() + 20
    while time.time() < deadline:
        if log.is_file() and b"DETACHED-OK" in log.read_bytes():
            break
        time.sleep(0.1)
    yield pid, log
    _reap(pid)


class TestTheChildOutlivesItsLauncher:

    def test_it_leads_its_own_session(self, detached):
        """setsid. A signal to THIS process's group must not reach it."""
        pid, _log = detached
        assert _alive(pid)
        assert os.getsid(pid) != os.getsid(0), (
            "the child shares this process's session, so it dies with it -- "
            "which is exactly how the 2026-09-29 shakedown run was lost")

    def test_it_leads_its_own_process_group(self, detached):
        pid, _log = detached
        assert os.getpgid(pid) != os.getpgid(0)

    def test_a_group_signal_to_the_launcher_does_not_kill_it(self, detached):
        """The failure mode in the field: the host goes, the run goes with it."""
        pid, _log = detached
        os.killpg(os.getpgid(0), signal.SIGCONT)   # harmless, group-wide
        time.sleep(0.3)
        assert _alive(pid)

    def test_it_does_not_block_the_caller(self, tmp_path):
        log = tmp_path / "b.log"
        t0 = time.time()
        pid = _mod.detach([sys.executable, "-c", "import time; time.sleep(30)"], log)
        elapsed = time.time() - t0
        _reap(pid)
        assert elapsed < 5.0, (
            f"detach blocked for {elapsed:.1f}s; subprocess.call blocking is the "
            f"defect being repaired")


class TestTheLogIsTheTether:

    def test_the_child_output_reaches_the_log(self, detached):
        _pid, log = detached
        assert log.is_file()
        assert b"DETACHED-OK" in log.read_bytes(), (
            "with no log there is no tether and a detached run is unobservable")

    def test_the_log_is_appended_not_truncated(self, tmp_path):
        """A resumed arm must not erase the earlier arm's output."""
        log = tmp_path / "c.log"
        log.write_bytes(b"EARLIER-ARM\n")
        pid = _mod.detach([sys.executable, "-u", "-c", "print('LATER-ARM')"], log)
        deadline = time.time() + 20
        while time.time() < deadline:
            if b"LATER-ARM" in log.read_bytes():
                break
            time.sleep(0.1)
        _reap(pid)
        body = log.read_bytes()
        assert b"EARLIER-ARM" in body and b"LATER-ARM" in body

    def test_stderr_is_captured_too(self, tmp_path):
        log = tmp_path / "d.log"
        pid = _mod.detach(
            [sys.executable, "-u", "-c",
             "import sys; print('ON-STDERR', file=sys.stderr); sys.stderr.flush()"],
            log)
        deadline = time.time() + 20
        while time.time() < deadline:
            if b"ON-STDERR" in log.read_bytes():
                break
            time.sleep(0.1)
        _reap(pid)
        assert b"ON-STDERR" in log.read_bytes(), (
            "a traceback on stderr would vanish, and a silent failure is worse "
            "than a loud one")

    def test_the_child_cannot_consume_the_launchers_stdin(self, tmp_path):
        """stdin=DEVNULL: a detached run must never sit waiting for a keystroke."""
        log = tmp_path / "e.log"
        pid = _mod.detach(
            [sys.executable, "-u", "-c",
             "import sys; print('EOF' if sys.stdin.read()=='' else 'DATA')"], log)
        deadline = time.time() + 20
        while time.time() < deadline:
            if b"EOF" in log.read_bytes():
                break
            time.sleep(0.1)
        _reap(pid)
        assert b"EOF" in log.read_bytes()


class TestThePidfileMatchesTheProjectsOwnConvention:
    """`bench/tail_until_done.sh` derives the pidfile from the log path. If the
    two conventions disagree the monitor cannot tell a quiet run from a dead one,
    which is the defect `test_monitor_dies_with_its_run_2026-09-09` was written for."""

    def test_the_pidfile_sits_beside_the_log_with_a_pid_suffix(self, detached):
        pid, log = detached
        pf = log.with_suffix(".pid")
        assert pf.is_file()
        assert int(pf.read_text().strip()) == pid

    def test_it_uses_the_same_convention_as_detached_launch_sh(self):
        """detached_launch.sh writes ${LOG%.log}.pid -- so arms.log -> arms.pid."""
        sh = (REPO / "bench" / "detached_launch.sh").read_text(encoding="utf-8")
        assert '"${LOG%.log}.pid"' in sh
        assert Path("/x/y/arms.log").with_suffix(".pid") == Path("/x/y/arms.pid")

    def test_the_monitor_can_find_it_with_no_second_argument(self):
        mon = (REPO / "bench" / "tail_until_done.sh").read_text(encoding="utf-8")
        assert ".pid" in mon

    def test_the_pid_is_written_before_detach_returns(self, tmp_path):
        """Otherwise a caller that prints the monitor line races the file."""
        log = tmp_path / "f.log"
        pid = _mod.detach([sys.executable, "-c", "import time; time.sleep(20)"], log)
        assert log.with_suffix(".pid").is_file()
        _reap(pid)


class TestTheLauncherSpendsNothingAndSequencesTheArms:

    def test_help_launches_nothing(self):
        """`A --help must never cost money` -- 15 of 17 runners once billed on an
        unrecognised argument."""
        before = {p.name for p in (REPO / "bench" / "logs").glob("*")}
        r = subprocess.run([sys.executable, str(LAUNCHER), "--help"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0
        assert "--detach" in r.stdout
        # `run_simulated_experiment_sandboxed.sh` announces a real sandbox as
        # "    sandbox  <path>". Its absence is the evidence nothing ran; the
        # word "sandboxed" in --run's own help text is not.
        assert "    sandbox  " not in r.stdout
        assert "detached PID" not in r.stdout
        after = {p.name for p in (REPO / "bench" / "logs").glob("*")}
        assert after == before, f"--help created {after - before}"

    def test_print_is_still_the_default_and_runs_nothing(self):
        r = subprocess.run([sys.executable, str(LAUNCHER)],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0
        assert r.stdout.count("run_simulated_experiment_sandboxed.sh") == len(_mod.ARMS)

    def test_detach_delegates_to_run_rather_than_copying_the_order(self):
        """2 copies of the sequencing is how a producer and consumer drift apart.
        The arms MUST be sequential: 4 in parallel is 17 concurrent seats."""
        src = LAUNCHER.read_text(encoding="utf-8")
        i = src.index("if args.detach:")
        j = src.index("if not args.run:")
        block = src[i:j]
        assert '"--run"' in block, "the detached child must re-enter --run"
        assert "subprocess.call" not in block, (
            "the detach path must not sequence the arms itself")
        # and --run itself is still the one place that iterates
        assert src.count("rc = subprocess.call(command(a), cwd=REPO)") == 1

    def test_the_arms_still_all_carry_sim_seats_only(self):
        """No detach flag may turn a simulated arm into a paid one."""
        for a in _mod.ARMS:
            assert a.seats, a.key
            assert "--seats" in a.argv()
        src = LAUNCHER.read_text(encoding="utf-8")
        assert "--api" not in src and "paid" not in src.lower().replace(
            "unpaid", "")

    def test_detach_is_reported_with_its_pid_and_monitor(self):
        src = LAUNCHER.read_text(encoding="utf-8")
        assert "detached PID" in src
        assert "tail_until_done.sh" in src
