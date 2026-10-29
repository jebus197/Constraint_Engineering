"""A commit message may not carry a Timestamp the clock never said.

HIS STANDING RULE: never type a timestamp, capture the clock. A typed time is
not a measurement of anything.

I BROKE IT 10 TIMES IN ONE SESSION. Measured over the last 16 commits carrying
a `Timestamp:` line, 10 of 16 -- 62.5000%, Wilson [38.6410%, 81.5188%] --
carry a stamp AHEAD of their own commit date, and the drift GROWS through the
session from +3.1 to +19.6 minutes. That monotone growth is the signature: a
guess falling steadily behind a clock nobody read. It was invisible until the
stamp and the author date were compared, which no test did.

THE CHECK IS ASYMMETRIC, AND THAT IS THE WHOLE DESIGN. A stamp AHEAD of the
commit cannot be honest, because the future has not happened yet. A stamp
BEHIND it can be, and must be allowed.

THE REASON WHY WAS WRONG WHEN FIRST WRITTEN HERE, and the correction is worth
keeping. I claimed the 4.5-minute pre-commit run sits between the stamp and the
commit. It does not: GIT SETS THE AUTHOR DATE WHEN `git commit` STARTS, before
the hooks run, which the first commit through this hook demonstrated with a
drift of -0.02 minutes rather than the -4.9 the claim predicted. A stamp
precedes its commit for a duller reason: the clock is read, other work happens,
and the commit is made later. Honest, merely stale.

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


def test_a_stamp_minutes_behind_is_accepted(tmp_path):
    """THE DIRECTION THAT MUST NOT BE REFUSED. A stamp read earlier in a
    session and committed later is honest but stale, and refusing it would
    refuse ordinary work."""
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


#: THE 10 COMMITS THAT CARRY A TYPED TIMESTAMP, PINNED AS A SET.
#:
#: ★ A COUNT IN A SLIDING WINDOW IS NOT A PIN, corrected 2026-10-29. The first
#: version ran the producer with its DEFAULT `--limit 60` and asserted that a
#: "drift range" line appeared. That line prints only when violations are found,
#: and the violations are HISTORICAL: the newest sits exactly 60 commits behind
#: HEAD as of 2026-10-29, so the window had slid past it by 1 and the producer
#: correctly reported 0. The test then accused correct code -- the 9-of-36
#: failure class recorded on 2026-10-28 -- and it would have done so on whatever
#: day HEAD happened to advance far enough, which is not a property of the
#: thing under test.
#:
#: A SET RATHER THAN A COUNT, which is `feedback_pin_a_set_not_a_count`: a count
#: cannot say WHICH commit moved, and 10 would still read 10 if history were
#: rewritten to swap one for another. The window is DERIVED from the oldest
#: pinned sha rather than chosen, so it reaches them however far HEAD advances.
TYPED_TIMESTAMP_SHAS = (
    "27a2a853", "498e4aa1", "8b976bf1", "f75bbaeb", "9afe2ba3",
    "6610da10", "c3c6b83e", "07ce845d", "d5c668bb", "29565256",
)


def _window_reaching(shas) -> int:
    """How many commits back the survey must go to include every pinned sha."""
    depths = []
    for sha in shas:
        r = subprocess.run(["git", "rev-list", "--count", f"{sha}..HEAD"],
                           capture_output=True, text=True, cwd=str(REPO))
        if r.returncode != 0:
            raise AssertionError(
                f"the pinned commit {sha} is not in this history: "
                f"{r.stderr.strip()[:200]}. That is what a rewrite looks like, "
                f"and he ruled against rewriting history.")
        depths.append(int(r.stdout.strip()))
    return max(depths) + 5          # +5 so the oldest is comfortably inside


def test_the_producer_still_finds_the_recorded_violations():
    """The figure must travel with its script. If this stops finding them, the
    history has been rewritten, which he ruled against.

    The window is derived from the pinned set, so this cannot fail merely
    because HEAD advanced -- which is exactly how it failed on 2026-10-29.
    """
    limit = _window_reaching(TYPED_TIMESTAMP_SHAS)
    r = subprocess.run([sys.executable, str(PRODUCER), "--limit", str(limit)],
                       capture_output=True, text=True, cwd=str(REPO))
    assert r.returncode == 0, r.stderr[-300:]
    assert "AHEAD of their own commit date" in r.stdout
    assert "drift range" in r.stdout, (
        "the producer no longer reports the drift range, so the shape of the "
        "error is no longer visible")
    missing = [s for s in TYPED_TIMESTAMP_SHAS if s not in r.stdout]
    assert not missing, (
        f"{len(missing)} of {len(TYPED_TIMESTAMP_SHAS)} pinned violations are no "
        f"longer reported by the producer over a window of {limit}: {missing}. "
        f"Either the history was rewritten or the producer stopped detecting "
        f"them; both matter and a count alone would not say which.")


def test_the_default_window_no_longer_reaches_them_and_that_is_stated():
    """THE REPORTING HAZARD THE SLIDE CREATED, pinned so it cannot go unsaid.

    Run bare, the producer now reports 0 violations, because the newest sits
    outside its default 60. A reader could take that as "this never happened".
    The producer must therefore SAY that its window may not reach the recorded
    violations and name the flag that does.
    """
    r = subprocess.run([sys.executable, str(PRODUCER)], capture_output=True,
                       text=True, cwd=str(REPO))
    assert r.returncode == 0, r.stderr[-300:]
    assert "--limit" in r.stdout, (
        "run with its default window the producer reports 0 violations and does "
        "not tell the reader that a larger --limit reaches the recorded ones, so "
        "a zero here reads as 'it never happened'")

def test_the_pin_itself_is_not_empty_and_every_sha_resolves():
    """THE PIN CANNOT BE GUTTED SILENTLY.

    Mutation testing on 2026-10-29 showed that DELETING the missing-set
    assertion leaves the suite green, because the surviving shape assertions
    pass whenever the producer works. That is true of any deleted assertion and
    chasing it is an infinite regress -- so instead this asserts the PIN, which
    is independent of the producer's output: an emptied or truncated set, or a
    sha that no longer resolves, fails here whatever the producer prints.
    """
    assert len(TYPED_TIMESTAMP_SHAS) == 10, (
        f"the pin holds {len(TYPED_TIMESTAMP_SHAS)} sha(s), not the 10 recorded "
        f"violations; a shortened pin checks less while looking the same")
    assert len(set(TYPED_TIMESTAMP_SHAS)) == len(TYPED_TIMESTAMP_SHAS), \
        "the pin repeats a sha, so it checks fewer commits than it appears to"
    for sha in TYPED_TIMESTAMP_SHAS:
        r = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, (
            f"the pinned commit {sha} does not resolve in this repository, which "
            f"is what a rewritten history looks like")
