"""B81 half 2: `sv`'s commit timeout must not leave the pytest board running.

THE DEFECT, OBSERVED. On 2026-11-10 at 06:42 and again at 06:46, `sv --commit
--push` raised `subprocess.TimeoutExpired` at 300 s while `hooks/pre-commit`
was running a 1,791 s board. `subprocess` kills only the DIRECT child, so
`git commit` died and the hook and its board did not: they were reparented to
pid 1 and kept running, burning a core they could never produce a commit with,
then competing with the retry for this machine's 8 cores. The founder's
machine is a FIXED RESOURCE of 8 cores and 8 GiB by his ruling of 2026-10-11.

THIS FILE EXECUTES. It does not read `cdsfl_sv.py` for the words
`start_new_session` or `killpg`; a source assertion would pass on a module
that describes itself consistently while leaking in production, which is the
failure `execute-do-not-grep` names. Every test here starts a real process
tree, times it out, and then asks the operating system whether the grandchild
is alive.

IT CARRIES ITS OWN DISCRIMINATION CONTROL. `test_the_old_behaviour_does_leak`
runs the identical scenario through a plain `subprocess.run(timeout=...)` and
requires the grandchild to SURVIVE. Without that, every assertion below could
pass because the grandchild died of something else, and the file would be
green on a machine where the defect was never reproducible -- the vacuity this
project has now measured 3 times.

NOTHING HERE RUNS PYTEST INSIDE PYTEST and nothing touches the network. The
`git` repositories are temporary, their hooks spawn `sleep`, and every
grandchild is reaped in a `finally` whatever the assertions do.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cdsfl_sv as sv  # noqa: E402

#: Long enough that survival is unambiguous; short enough that an escapee
#: cannot outlive a session.
SLEEP_SECONDS = 120
#: Settling time before survival is tested, so a dying process is not read as
#: a living one. The producer uses the same figure.
SETTLE = 0.6


# ── helpers ──────────────────────────────────────────────────────────────────

def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _hard_reap(pid: int | None) -> None:
    if pid is None:
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass


def _await_marker(mark: Path, limit: float = 10.0) -> int:
    deadline = time.time() + limit
    while time.time() < deadline:
        if mark.exists():
            txt = mark.read_text().strip()
            if txt:
                return int(txt)
        time.sleep(0.05)
    raise AssertionError(f"the grandchild never announced itself at {mark}")


def _repo_whose_hook_spawns_a_sleeper(tmp_path: Path) -> tuple[Path, Path]:
    """A real git repo whose pre-commit hook backgrounds a long-lived child.

    This is the exact shape of the live failure: git -> hook -> long job.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    for cmd in (
        ["git", "init", "--quiet"],
        ["git", "config", "user.email", "probe@example.invalid"],
        ["git", "config", "user.name", "probe"],
        ["git", "config", "commit.gpgsign", "false"],
    ):
        subprocess.run(cmd, cwd=repo, check=True, capture_output=True)

    (repo / "a.txt").write_text("a\n")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True,
                   capture_output=True)

    mark = tmp_path / "grandchild.pid"
    ledger = tmp_path / "hook_exit_trap.txt"
    hook = repo / ".git" / "hooks" / "pre-commit"
    # The EXIT trap mirrors the live `hooks/pre-commit`, which records its own
    # elapsed seconds there and is the ONLY source `commit_timeout()` has.
    hook.write_text(
        "#!/bin/sh\n"
        f"rec() {{ echo RECORDED >> {ledger}; }}\n"
        "trap rec EXIT\n"
        f"sh -c 'echo $$ > {mark}; sleep {SLEEP_SECONDS}' &\n"
        "wait\n"
    )
    hook.chmod(0o755)
    return repo, mark


def _exit_trap_ledger(tmp_path: Path) -> Path:
    return tmp_path / "hook_exit_trap.txt"


# ── the discrimination control: the old behaviour MUST leak ─────────────────

def test_the_old_behaviour_does_leak(tmp_path):
    """A plain `subprocess.run` timeout leaves the hook's child running.

    If this ever passes trivially -- grandchild already dead -- then every
    other test in this file is vacuous, so it is asserted rather than assumed.
    """
    repo, mark = _repo_whose_hook_spawns_a_sleeper(tmp_path)
    gpid = None
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            subprocess.run(
                ["git", "commit", "-m", "x"],
                cwd=repo, capture_output=True, text=True, timeout=2,
            )
        gpid = _await_marker(mark)
        time.sleep(SETTLE)
        assert _alive(gpid), (
            "the control did not reproduce the defect, so every other "
            "assertion in this file would be vacuous"
        )
    finally:
        _hard_reap(gpid)


# ── the fix, end to end through the real entry point ───────────────────────

def test_git_timeout_reaps_the_hooks_child(tmp_path):
    repo, mark = _repo_whose_hook_spawns_a_sleeper(tmp_path)
    gpid = None
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            sv._git("commit", "-m", "x", root=repo, timeout=2)
        gpid = _await_marker(mark)
        time.sleep(SETTLE)
        assert not _alive(gpid), (
            f"pid {gpid} survived the timeout: the board the commit abandoned "
            f"is still running, which is the B81 leak"
        )
    finally:
        _hard_reap(gpid)


def test_the_timeout_is_still_a_TimeoutExpired_naming_the_command(tmp_path):
    """The exception contract every existing caller relies on is unchanged."""
    repo, mark = _repo_whose_hook_spawns_a_sleeper(tmp_path)
    gpid = None
    try:
        with pytest.raises(subprocess.TimeoutExpired) as err:
            sv._git("commit", "-m", "x", root=repo, timeout=2)
        assert err.value.cmd[:2] == ["git", "commit"], err.value.cmd
        assert err.value.timeout == 2, err.value.timeout
        gpid = _await_marker(mark)
    finally:
        _hard_reap(gpid)


def test_the_reap_is_recorded_on_stderr(tmp_path, capfd):
    """A swallowed reap is not a record: it must say what it did."""
    repo, mark = _repo_whose_hook_spawns_a_sleeper(tmp_path)
    gpid = None
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            sv._git("commit", "-m", "x", root=repo, timeout=2)
        err = capfd.readouterr().err
        assert "timed out" in err, err
        assert "process group" in err, err
        assert "SIGTERM" in err or "SIGKILL" in err, err
        gpid = _await_marker(mark)
    finally:
        _hard_reap(gpid)


# ── _reap_process_group, called directly ───────────────────────────────────

def test_reap_kills_a_whole_detached_group():
    proc = subprocess.Popen(
        ["sh", "-c", f"sh -c 'sleep {SLEEP_SECONDS}' & wait"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    pgid = os.getpgid(proc.pid)
    try:
        sent = sv._reap_process_group(proc, grace=1.0)
        assert sent, "no signal was delivered to the group"
        assert signal.SIGKILL in sent or signal.SIGTERM in sent, sent
        time.sleep(SETTLE)
        with pytest.raises(ProcessLookupError):
            os.killpg(pgid, 0)
    finally:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except OSError:
            pass


def test_reap_REFUSES_to_signal_our_own_group():
    """The dangerous case, and the reason the group is created deliberately.

    A child started WITHOUT a new session shares this process's group. A
    `killpg` there would take the test runner, `sv`, and the parent shell with
    it. The refusal is asserted by the signals NOT sent, and corroborated by
    this test still being alive to make the assertion.
    """
    own = os.getpgid(0)
    proc = subprocess.Popen(
        ["sleep", str(SLEEP_SECONDS)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    assert os.getpgid(proc.pid) == own, (
        "the probe did not reproduce the shared-group case"
    )
    try:
        sent = sv._reap_process_group(proc, grace=1.0)
        assert sent == [], f"it signalled our OWN group: {sent}"
        # ...and the direct child is still killed, so this is never worse
        # than the behaviour it replaces.
        assert proc.poll() is not None, "the direct child was left running"
        assert os.getpgid(0) == own, "our own process group changed"
    finally:
        _hard_reap(proc.pid)


def test_reap_sends_SIGTERM_BEFORE_SIGKILL():
    """The order is load-bearing and was MEASURED, not preferred.

    `hooks/pre-commit` records its own elapsed seconds in an EXIT trap, and
    that single number is all `commit_timeout()` has to size itself with.
    Measured on this machine's /bin/sh: a group SIGTERM lets the trap run and
    the duration survives; a group SIGKILL does not and the duration is LOST.
    A SIGKILL-only reap would therefore have converted one timeout into a
    permanent 300 s floor -- the fix destroying the record the fix needs.
    """
    proc = subprocess.Popen(
        ["sh", "-c", f"sleep {SLEEP_SECONDS}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        sent = sv._reap_process_group(proc, grace=2.0)
        assert sent, "nothing was sent to the group"
        assert sent[0] == int(signal.SIGTERM), (
            f"the first signal was {signal.Signals(sent[0]).name}, not SIGTERM; "
            f"a group that dies on SIGTERM must never be SIGKILLed first"
        )
        assert int(signal.SIGKILL) not in sent, (
            f"a cooperative group was SIGKILLed anyway: {sent}"
        )
    finally:
        _hard_reap(proc.pid)


def test_the_hooks_exit_trap_still_records_after_the_reap(tmp_path):
    """End to end: the abandoned hook still writes its duration record.

    This is the property `commit_timeout()` depends on, so it is asserted
    against a real hook rather than inferred from the signal order above.
    """
    repo, mark = _repo_whose_hook_spawns_a_sleeper(tmp_path)
    ledger = _exit_trap_ledger(tmp_path)
    gpid = None
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            sv._git("commit", "-m", "x", root=repo, timeout=2)
        gpid = _await_marker(mark)
        time.sleep(SETTLE)
        assert ledger.is_file() and "RECORDED" in ledger.read_text(), (
            "the hook was reaped without its EXIT trap running, so the "
            "duration `commit_timeout()` reads was destroyed by the reap"
        )
    finally:
        _hard_reap(gpid)


def test_reap_tolerates_an_already_dead_child():
    proc = subprocess.Popen(["true"], start_new_session=True)
    proc.wait()
    assert sv._reap_process_group(proc, grace=0.5) == []


# ── the contract on the success and failure paths ───────────────────────────

def test_git_still_returns_stripped_stdout(tmp_path):
    repo = tmp_path / "plain"
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True,
                   capture_output=True)
    out = sv._git("rev-parse", "--is-inside-work-tree", root=repo)
    assert out == "true", repr(out)


def test_git_still_raises_RuntimeError_on_failure(tmp_path):
    repo = tmp_path / "plain2"
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True,
                   capture_output=True)
    with pytest.raises(RuntimeError) as err:
        sv._git("rev-parse", "--verify", "refs/heads/nope", root=repo)
    assert "rev-parse" in str(err.value)


def test_git_check_false_returns_output_rather_than_raising(tmp_path):
    repo = tmp_path / "plain3"
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=repo, check=True,
                   capture_output=True)
    assert sv._git("rev-parse", "--verify", "refs/heads/nope",
                   root=repo, check=False) == ""


def test_the_grace_is_a_named_constant_with_a_sane_value():
    assert isinstance(sv.GIT_REAP_GRACE_SECONDS, float)
    assert 0.0 < sv.GIT_REAP_GRACE_SECONDS <= 10.0


# ── the ROOT CAUSE: an early refusal overwrote the duration ────────────────
#
# These rows are the shape observed in the live ledger on 2026-11-10: boards at
# 1,635 to 2,023 seconds interleaved with note-lint refusals at 30 to 66. They
# are written as a FIXTURE rather than read from `.cdsfl_tmp`, because that
# path is scratch and a guard that depended on it would pass or fail on
# whatever the last commit happened to leave behind.
_BOARDS = (1635, 1853, 1925, 2023, 1697)
_REFUSALS = (30, 63, 64, 66)


def _ledger(root: Path, seconds: tuple[int, ...]) -> None:
    d = root / ".cdsfl_tmp"
    d.mkdir(parents=True, exist_ok=True)
    (d / "precommit_durations.jsonl").write_text(
        "".join('{"at":"2026-11-10T00:00:00Z","seconds":%d,"exit":0,'
                '"head":"deadbeef","why":""}\n' % n for n in seconds)
    )


def _scratch(root: Path, seconds: int) -> None:
    d = root / ".cdsfl_tmp"
    d.mkdir(parents=True, exist_ok=True)
    (d / "precommit_seconds").write_text(str(seconds))


def test_an_early_refusal_no_longer_collapses_the_timeout(tmp_path):
    """The 2026-11-10 state exactly: a 66 s refusal beside 1,769 s boards.

    The old formula read the scratch number alone, got 66, and returned
    `max(300, 4*66) = 300` -- so `sv` waited 300 s for a board that needed
    1,769. That is the whole of why the commit died.
    """
    _scratch(tmp_path, 66)
    _ledger(tmp_path, _BOARDS + _REFUSALS[:1])

    secs, why = sv.recorded_hook_seconds(tmp_path)
    assert secs == max(_BOARDS), f"sized from {secs} ({why}), not a board"
    assert "ledger" in why, why

    got = sv.commit_timeout(tmp_path)
    assert got == sv.COMMIT_TIMEOUT_HEADROOM * max(_BOARDS), got
    # the discriminating comparison: the board that actually failed was 1,769 s
    assert got > 1769, (
        f"the timeout is {got} s, still under the 1,769 s board that failed; "
        f"the old formula gave {max(sv.COMMIT_TIMEOUT_FLOOR, 4 * 66)}"
    )
    assert max(sv.COMMIT_TIMEOUT_FLOOR, 4 * 66) < 1769, (
        "the control is wrong: the old formula did not under-size here"
    )


def test_a_refusal_only_ledger_is_never_worse_than_the_floor(tmp_path):
    """All recent rows short: the floor applies, exactly as before."""
    _scratch(tmp_path, 66)
    _ledger(tmp_path, _REFUSALS)
    secs, _why = sv.recorded_hook_seconds(tmp_path)
    assert secs == max(_REFUSALS)
    assert sv.commit_timeout(tmp_path) == sv.COMMIT_TIMEOUT_FLOOR


def test_no_ledger_falls_back_to_the_scratch_number(tmp_path):
    """Contract preserved for a fresh checkout: identical to the old formula."""
    _scratch(tmp_path, 745)
    secs, why = sv.recorded_hook_seconds(tmp_path)
    assert (secs, why) == (745, "last recorded run")
    assert sv.commit_timeout(tmp_path) == 4 * 745


def test_no_record_at_all_gives_the_floor(tmp_path):
    secs, why = sv.recorded_hook_seconds(tmp_path)
    assert (secs, why) == (0, "no record")
    assert sv.commit_timeout(tmp_path) == sv.COMMIT_TIMEOUT_FLOOR


def test_a_half_written_ledger_row_costs_a_row_and_not_a_commit(tmp_path):
    d = tmp_path / ".cdsfl_tmp"
    d.mkdir(parents=True)
    (d / "precommit_durations.jsonl").write_text(
        '{"seconds": 1700, "exit": 0}\n'
        'not json at all\n'
        '{"seconds": "banana"}\n'
        '\n'
        '{"at":"x","seconds":1800,"exit":0,"head":"h","why":""'   # truncated
    )
    secs, _why = sv.recorded_hook_seconds(tmp_path)
    assert secs == 1700, secs


def test_only_the_recent_window_is_considered(tmp_path):
    """An old worst case must not keep a split-up board set alive forever."""
    stale = 99999
    recent = (100,) * sv.COMMIT_TIMEOUT_LEDGER_ROWS
    _ledger(tmp_path, (stale,) + recent)
    secs, _why = sv.recorded_hook_seconds(tmp_path)
    assert secs == 100, f"the stale {stale} s row was still in the window"


def test_the_window_is_a_named_constant_with_a_sane_value():
    assert isinstance(sv.COMMIT_TIMEOUT_LEDGER_ROWS, int)
    assert 1 <= sv.COMMIT_TIMEOUT_LEDGER_ROWS <= 100


# ── the producer the code comment cites must exist and discriminate ────────

def test_the_producer_runs_and_discriminates():
    prod = REPO_ROOT / "scripts" / (
        "the_commit_timeout_left_the_board_running_2026-11-10.py")
    assert prod.is_file(), f"the cited producer is absent: {prod}"
    r = subprocess.run([sys.executable, str(prod)], capture_output=True,
                       text=True, timeout=180, cwd=str(REPO_ROOT))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "LEAKED" in r.stdout and "reaped" in r.stdout, r.stdout


def test_the_producers_help_costs_nothing():
    prod = REPO_ROOT / "scripts" / (
        "the_commit_timeout_left_the_board_running_2026-11-10.py")
    t0 = time.monotonic()
    r = subprocess.run([sys.executable, str(prod), "--help"],
                       capture_output=True, text=True, timeout=30,
                       cwd=str(REPO_ROOT))
    assert r.returncode == 0, r.stderr
    assert time.monotonic() - t0 < 5.0, "a --help must never cost minutes"
