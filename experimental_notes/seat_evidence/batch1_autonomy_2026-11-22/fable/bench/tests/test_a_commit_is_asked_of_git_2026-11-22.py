# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'batch1_autonomy_2026-11-22', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6f86f5c7f6ad0ad7effbd14546466d25b3060a781066b68907a6dd232c38c587
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A COMMIT IS ASKED OF GIT, NOT MATCHED IN PROSE -- and that claim is now EXECUTED.

★ WHY THIS EXISTS. Entry B205(a), repaired 2026-11-21: `turn_signals` used to set
its commit flag on the literal string `git commit` anywhere in the turn's
transcript, so merely READING `hooks/pre-commit` -- which carries
`git commit --no-verify` as bypass advice -- made the gate report a commit that
never happened, 6 times while HEAD never moved. The repair,
`_a_commit_landed_since`, asks git for HEAD's committer date and compares it to
the turn's start.

THE REPAIR'S OWN COMMENT SAYS "DRIVEN OVER 5 CASES BEFORE BEING WRITTEN, correct
in 5 of 5" -- but that drive was committed nowhere, so the declared figure was
not re-executable and the addition was executed by no test, which is half of
`additive-standard`. This file is that drive, committed, plus the original
defect reproduced end-to-end: a transcript whose only mention of committing is
the literal bypass advice must leave the flag False.

A SCRATCH REPOSITORY, NOT THE LIVE ONE. The predicate reads `REPO`, which is
monkeypatched to a `git init` directory with one commit at a known committer
date, so the test is hermetic: it neither needs the project's history nor can a
concurrent commit move its ground truth. Panel sandboxes carry no `.git` at all,
which is exactly why the comparison cannot lean on the live repository.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HOOK = ROOT / "hooks" / "work_not_narrate.py"

HEAD_AT = dt.datetime(2026, 11, 21, 12, 0, 0, tzinfo=dt.timezone.utc)


def _iso(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("wnn_commit_guard", HOOK)
    m = importlib.util.module_from_spec(spec)
    sys.modules["wnn_commit_guard"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture()
def scratch_repo(hook, tmp_path, monkeypatch):
    """A git repository whose single commit landed at HEAD_AT exactly."""
    env = {
        "GIT_AUTHOR_DATE": "2026-11-21T12:00:00Z",
        "GIT_COMMITTER_DATE": "2026-11-21T12:00:00Z",
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
        "HOME": str(tmp_path), "PATH": __import__("os").environ.get("PATH", ""),
    }

    def g(*a):
        r = subprocess.run(["git", "-C", str(tmp_path)] + list(a),
                           capture_output=True, text=True, env=env, timeout=30)
        if r.returncode != 0:
            pytest.skip(f"git unavailable here: {r.stderr.strip()[:120]}")
    g("init")
    (tmp_path / "f").write_text("x", encoding="utf-8")
    g("add", "f")
    g("commit", "-m", "c1", "--no-verify")
    monkeypatch.setattr(hook, "REPO", tmp_path)
    return tmp_path


class TestTheFiveCaseDrive:
    """The drive the repair's comment declares, now re-executable."""

    @pytest.mark.parametrize("why,turn,want", [
        ("a turn that began after HEAD sees no commit",
         _iso(HEAD_AT + dt.timedelta(hours=2)), False),
        ("a turn predating HEAD sees the commit",
         _iso(HEAD_AT - dt.timedelta(hours=2)), True),
        ("HEAD's own timestamp counts as landed (>=, not >)",
         _iso(HEAD_AT), True),
        ("1 s after HEAD is after HEAD",
         _iso(HEAD_AT + dt.timedelta(seconds=1)), False),
        ("an unparseable timestamp NEVER claims a commit (fail-safe)",
         "not-a-time", False),
        ("an empty timestamp never claims a commit",
         "", False),
    ])
    def test_the_drive(self, hook, scratch_repo, why, turn, want):
        assert hook._a_commit_landed_since(turn) is want, why

    def test_no_repository_never_claims_a_commit(self, hook, tmp_path,
                                                 monkeypatch):
        """The panel-sandbox case: REPO is not a git repository at all."""
        monkeypatch.setattr(hook, "REPO", tmp_path / "nowhere")
        assert hook._a_commit_landed_since(_iso(HEAD_AT)) is False


class TestTheOriginalDefectStaysDead:
    """Reading `hooks/pre-commit` must never again read as having committed."""

    def _transcript(self, tmp_path, turn_iso):
        t = tmp_path / "t.jsonl"
        lines = [
            json.dumps({"type": "user", "timestamp": turn_iso,
                        "message": {"role": "user", "content":
                                    [{"type": "text", "text": "work the list"}]}}),
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Read", "input": {}},
                {"type": "text", "text":
                 "hooks/pre-commit says: bypass deliberately with: "
                 "git commit --no-verify"}]}}),
        ]
        t.write_text("\n".join(lines), encoding="utf-8")
        return t

    def test_the_literal_string_no_longer_sets_the_flag(self, hook,
                                                        scratch_repo, tmp_path):
        t = self._transcript(tmp_path, _iso(HEAD_AT + dt.timedelta(hours=2)))
        _calls, _prose, commit, _d = hook.turn_signals(t)
        assert commit is False, (
            "a transcript carrying the literal 'git commit --no-verify' from "
            "hooks/pre-commit set the commit flag; B205(a) has regressed")

    def test_a_real_commit_is_still_seen(self, hook, scratch_repo, tmp_path):
        """ANTI-VACUITY: the flag must still go True when HEAD genuinely moved
        at or after the turn began -- otherwise the repair fixed the false
        report by never reporting."""
        t = self._transcript(tmp_path, _iso(HEAD_AT - dt.timedelta(hours=2)))
        _calls, _prose, commit, _d = hook.turn_signals(t)
        assert commit is True
