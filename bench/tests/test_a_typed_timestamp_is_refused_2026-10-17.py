"""A commit message may not carry a Timestamp the clock never said.

HIS STANDING RULE: never type a timestamp, capture the clock. A typed time is
not a measurement of anything.

I BROKE IT 10 TIMES IN ONE SESSION. Measured over the last 16 commits carrying
a `Timestamp:` line, 10 of 16 -- 62.5000%, Wilson [38.6410%, 81.5188%] --
carry a stamp AHEAD of their own commit date, and the drift GROWS through the
session from +3.1 to +19.6 minutes. That monotone growth is the signature: a
guess falling steadily behind a clock nobody read. It was invisible until the
stamp and the author date were compared, which no test did.

THE CHECK IS ASYMMETRIC, AND THAT IS THE WHOLE DESIGN. A stamp legitimately
PRECEDES its commit, because this repository's pre-commit hook runs over 1,300
tests and takes about 4.5 minutes: capture the clock, run the hook, land the
commit. So a stamp minutes BEHIND the commit is honest and must be allowed. A
stamp AHEAD of the commit cannot be honest, because the future has not
happened yet. A symmetric tolerance would either refuse every honest commit or
permit every typed one.

HISTORY IS NOT REWRITTEN. 12 of those commits are pushed, and his ruling
elsewhere is "I am not suggesting rewriting history". The figures are recorded
in a producer and the recurrence is prevented mechanically.
"""
from __future__ import annotations

import datetime
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "commit-msg"
PRODUCER = REPO / "scripts" / "which_commits_carry_a_typed_timestamp_2026-10-17.py"


def _run(message: str, tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text(message, encoding="utf-8")
    return subprocess.run([sys.executable, str(HOOK), str(f)],
                          capture_output=True, text=True)


def test_the_hook_exists_and_is_where_git_will_find_it():
    assert HOOK.is_file(), "the commit-msg hook does not exist"
    hooks_path = subprocess.run(["git", "config", "core.hooksPath"],
                                capture_output=True, text=True,
                                cwd=str(REPO)).stdout.strip()
    assert hooks_path, (
        "core.hooksPath is unset, so git will look in .git/hooks and never run "
        "this file")
    assert pathlib.Path(hooks_path).resolve() == HOOK.parent.resolve(), (
        f"core.hooksPath is {hooks_path}, not the directory holding the hook")


def test_a_stamp_in_the_future_is_refused(tmp_path):
    """THE TYPED CASE. Every one of the 10 had a stamp ahead of its commit."""
    ahead = (datetime.datetime.now().astimezone()
             + datetime.timedelta(minutes=20)).isoformat()
    r = _run(f"subject\n\nTimestamp: {ahead}\n", tmp_path)
    assert r.returncode != 0, (
        "a stamp 20 minutes in the future was accepted; that is exactly the "
        "shape of all 10 recorded violations")
    assert "FUTURE" in r.stderr.upper()


def test_a_stamp_captured_now_is_accepted(tmp_path):
    now = datetime.datetime.now().astimezone().isoformat()
    r = _run(f"subject\n\nTimestamp: {now}\n", tmp_path)
    assert r.returncode == 0, r.stderr


def test_a_stamp_minutes_behind_is_accepted_because_the_hook_runs_long(tmp_path):
    """THE DIRECTION THAT MUST NOT BE REFUSED. The pre-commit suite takes about
    4.5 minutes, so an honest stamp precedes its commit."""
    behind = (datetime.datetime.now().astimezone()
              - datetime.timedelta(minutes=6)).isoformat()
    r = _run(f"subject\n\nTimestamp: {behind}\n", tmp_path)
    assert r.returncode == 0, (
        f"a stamp 6 minutes old was refused, which would refuse every honest "
        f"commit this repository makes: {r.stderr}")


def test_a_very_stale_stamp_is_refused(tmp_path):
    stale = (datetime.datetime.now().astimezone()
             - datetime.timedelta(hours=4)).isoformat()
    r = _run(f"subject\n\nTimestamp: {stale}\n", tmp_path)
    assert r.returncode != 0


def test_a_message_with_no_stamp_is_left_alone(tmp_path):
    """This hook does not invent a new requirement. A commit without a stamp
    makes no false claim about when it happened."""
    r = _run("just a subject line\n", tmp_path)
    assert r.returncode == 0, r.stderr


def test_an_unparseable_stamp_is_refused_rather_than_ignored(tmp_path):
    r = _run("subject\n\nTimestamp: yesterday afternoon\n", tmp_path)
    assert r.returncode != 0
    assert "ISO" in r.stderr


def test_a_broken_hook_never_blocks_a_commit(tmp_path):
    """A checker that blocks every commit is far worse than a missed stamp, so
    the hook exits 0 on its own failure. Driven by handing it a path that does
    not exist."""
    r = subprocess.run([sys.executable, str(HOOK),
                        str(tmp_path / "nothing-here")],
                       capture_output=True, text=True)
    assert r.returncode == 0, (
        "the hook failed closed on its own error; it must fail open")


def test_the_producer_still_finds_the_recorded_violations():
    """The figure must travel with its script. If this stops finding them, the
    history has been rewritten, which he ruled against."""
    r = subprocess.run([sys.executable, str(PRODUCER)], capture_output=True,
                       text=True, cwd=str(REPO))
    assert r.returncode == 0, r.stderr[-300:]
    assert "AHEAD of their own commit date" in r.stdout
    assert "drift range" in r.stdout, (
        "the producer no longer reports the drift range, so the shape of the "
        "error is no longer visible")
