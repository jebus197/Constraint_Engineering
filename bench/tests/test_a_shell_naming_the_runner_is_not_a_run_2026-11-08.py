"""`pgrep -f` matched the `git commit` shell whose message named the runner.

THE DEFECT, OBSERVED TWICE WITH 2 DIFFERENT PIDS. `cy_monitor_gate.runner_processes`
finds runs that began before the pulse file existed with
`pgrep -f run_simulated_experiment.py`. `-f` matches the WHOLE COMMAND LINE, so
a process whose arguments merely NAME the runner is reported as a live run and
the gate refuses the stop up to `MAX_REFUSALS` times. On 2026-11-04T05:40 it
named pid 21974, which was the `git commit` shell itself -- its command line
carried a commit message describing this very blocker. Writing about the runner
was indistinguishable from running it. It recurred on the NEXT commit at
05:54:24 with pid 28697, `comm` `/bin/zsh`, whose command line named the runner
twice.

WHY SHELLS ARE EXCLUDED RATHER THAN PYTHON REQUIRED. The author's intent is kept:
ANY match counts, because over-refusing is recoverable and under-refusing is the
defect being closed. So what is removed is not a doubtful match but a
CATEGORICALLY IMPOSSIBLE one -- a shell cannot execute a `.py` in-process, and a
shell that SPAWNED a runner has a child that matches on its own with a non-shell
`comm`. Requiring python would instead UNDER-refuse for a runner started by any
other route, which is the failure the gate exists to prevent. A pid whose `comm`
cannot be read is KEPT, for the same reason.

WHY THIS FILE EXISTS AT ALL. `runner_processes` appeared in 0 test files. The 1
guard that existed, `test_the_cy_gate_refuses_while_a_run_is_live_2026-11-02.py`,
sets `CDSFL_CY_NO_PGREP` to switch this path OFF so it can isolate the pulse
path -- so the seam that made 1 path testable left the other covered by nothing.
That is the addition-nothing-reaches half of `additive-standard` applied to a
code path rather than a feature.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "cy_monitor_gate.py"
LIVE = pathlib.Path.home() / ".claude" / "hooks" / "cy_monitor_gate.py"
NAME = "run_simulated_experiment.py"


@pytest.fixture(scope="module")
def gate():
    spec = importlib.util.spec_from_file_location("cy_gate_under_test", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _wait_for_pgrep(pid: int, timeout: float = 5.0) -> bool:
    """Poll until `pgrep -f` can see this pid, so the test is not a race."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        out = subprocess.run(["pgrep", "-f", NAME], capture_output=True, text=True)
        if str(pid) in (out.stdout or "").split():
            return True
        time.sleep(0.1)
    return False


@pytest.fixture
def shell_naming_the_runner():
    """A SHELL whose command line names the runner -- the false positive.

    ★ TWO COMMANDS, NOT ONE, AND THE ANTI-VACUITY TEST FOUND THIS BEFORE THE
    GUARD WAS EVEN PLACED. `sh -c 'sleep 20 # name'` EXECS `sleep` in place, so
    the process loses the whole comment from its command line and `pgrep -f`
    cannot see it -- measured 2026-11-08: comm became `sleep` and pgrep
    returned nothing. A second statement forces the shell to stay resident,
    comm `/bin/sh`. Without the anti-vacuity check this fixture would have
    passed the exclusion test by being invisible rather than by being excluded.
    """
    p = subprocess.Popen(["/bin/sh", "-c", f"sleep 20; true # {NAME}"])
    yield p
    p.kill()
    p.wait(timeout=5)


@pytest.fixture
def python_naming_the_runner():
    """A PYTHON process whose command line names the runner -- a true positive."""
    p = subprocess.Popen(["python3", "-c", f"import time; time.sleep(20)  # {NAME}"])
    yield p
    p.kill()
    p.wait(timeout=5)


class TestTheProbeIsFaithful:
    """ANTI-VACUITY. If `pgrep` cannot see the planted process, every assertion
    below passes while testing nothing -- the probe-manufactured failure of
    2026-11-02 in reverse."""

    def test_pgrep_sees_the_planted_shell(self, shell_naming_the_runner):
        assert _wait_for_pgrep(shell_naming_the_runner.pid), (
            "pgrep cannot see the planted shell, so the exclusion test is vacuous")

    def test_pgrep_sees_the_planted_python(self, python_naming_the_runner):
        assert _wait_for_pgrep(python_naming_the_runner.pid), (
            "pgrep cannot see the planted python, so the retention test is vacuous")


class TestAShellIsNotARun:
    def test_a_shell_naming_the_runner_is_not_reported(self, gate,
                                                       shell_naming_the_runner):
        """THE LIVE CASE: pids 21974 and 28697, both `git commit` shells."""
        assert _wait_for_pgrep(shell_naming_the_runner.pid)
        os.environ.pop("CDSFL_CY_NO_PGREP", None)
        assert str(shell_naming_the_runner.pid) not in gate.runner_processes()

    def test_a_python_naming_the_runner_is_still_reported(self, gate,
                                                          python_naming_the_runner):
        """NEGATIVE CONTROL. Excluding shells must not stop the gate working."""
        assert _wait_for_pgrep(python_naming_the_runner.pid)
        os.environ.pop("CDSFL_CY_NO_PGREP", None)
        assert str(python_naming_the_runner.pid) in gate.runner_processes()


class TestTheChoiceIsPinned:
    """★ `ps -o comm=` RETURNS A FULL PATH ON THIS MACHINE, measured 2026-11-08:
    `/bin/sh`, `/bin/zsh`, and for python
    `/Library/Frameworks/Python.framework/.../MacOS/Python`. So taking the
    BASENAME is load-bearing rather than tidy: comparing the raw string against
    a set of bare shell names would match nothing and the exclusion would be
    silently inert -- an addition nothing reaches."""

    def test_the_comm_is_read_as_a_basename(self, gate):
        """A full path must still classify, since that is what ps returns."""
        assert gate._shell_name("/bin/zsh") == "zsh"
        assert gate._shell_name("-zsh") == "zsh"
        assert gate._shell_name(
            "/Library/Frameworks/Python.framework/Versions/3.13/"
            "Resources/Python.app/Contents/MacOS/Python") == "Python"

    def test_a_dead_pid_keeps_the_pid(self, gate):
        """`ps` EXITS NON-ZERO for a pid that is gone, which is a different
        branch from an exception. Both must keep the pid."""
        assert gate._is_shell("99999999") is False

    def test_a_raising_ps_keeps_the_pid(self, gate, monkeypatch):
        """★ THE EXCEPT ARM HAD NO TEST REACHING IT, found 2026-11-08 by the
        mutation harness: inverting `except -> return True` left this guard
        GREEN, because `ps -p 99999999` exits non-zero rather than raising, so
        the test above exercises the returncode branch and never the handler.
        An untested arm is the addition-nothing-reaches half of
        `additive-standard` applied to error handling."""
        def _boom(*a, **k):
            raise subprocess.TimeoutExpired(cmd="ps", timeout=4)
        monkeypatch.setattr(gate.subprocess, "run", _boom)
        assert gate._is_shell("1") is False

    def test_the_exclusion_is_by_shell_not_by_interpreter(self, gate):
        """PINNED. Requiring python would UNDER-refuse for a runner started by
        any other route, which is the failure this gate exists to prevent."""
        assert "zsh" in gate._SHELLS and "bash" in gate._SHELLS
        assert "python3" not in gate._SHELLS and "python" not in gate._SHELLS

    def test_the_test_seam_still_isolates_the_pulse_path(self, gate, monkeypatch):
        """The older guard depends on this seam; it must keep working."""
        monkeypatch.setenv("CDSFL_CY_NO_PGREP", "1")
        assert gate.runner_processes() == []


def test_the_committed_hook_is_the_one_that_runs():
    """3 of the 4 earlier hooks existed in no repository at all."""
    assert HOOK.read_bytes() == LIVE.read_bytes()
    assert HOOK.stat().st_ino == LIVE.stat().st_ino, (
        "the repo copy and the live hook are no longer the same inode")
