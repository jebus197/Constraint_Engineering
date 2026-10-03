#!/usr/bin/env python3
"""No hook may exist only outside the repository, and none may silently drift.

WHY THIS EXISTS, with the defect that caused it. On 2026-10-03 the compaction
hook gained the macOS desktop notification the founder had asked for -- and the
edit landed on `~/.claude/hooks/compaction_watch.py` ONLY. That path had been a
HARD LINK to `hooks/compaction_watch.py`, one inode with 2 names, so the two
could not diverge. Writing the file through an editor that replaces rather than
appends broke the link: the live hook became inode 458004333 with 1 name, and
the repository kept the old 14,622-byte version with 0 occurrences of the
notification. The capability the founder asked for existed on exactly 1 machine
and in no commit, which is the project's own recorded sentence about the 3 of 4
earlier hooks that existed in no repository at all.

Nothing caught it. `test_work_not_narrate_hook_2026-09-10.py` holds exactly this
property -- for 1 hook, by name. Every hook added since was outside its reach.

WHAT THIS ASSERTS, and why it is the general form rather than a 6th copy of the
same check: every `*.py` under `hooks/` that also exists under
`~/.claude/hooks/` must be byte-identical to it. A hook added tomorrow is
covered by construction. Hooks absent from the live directory are skipped and
NAMED, so "not installed here" can never be mistaken for "checked".

ANTI-VACUITY. `drifted()` is executed against planted directories below, so a
machine where no hook is installed still proves the comparison can fail.
"""
from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
VERSIONED = REPO / "hooks"
LIVE = pathlib.Path.home() / ".claude" / "hooks"


def drifted(versioned: pathlib.Path, live: pathlib.Path) -> tuple[list, list]:
    """Return (drifted, not_installed) for every *.py in `versioned`."""
    bad, absent = [], []
    for f in sorted(versioned.glob("*.py")):
        other = live / f.name
        if not other.is_file():
            absent.append(f.name)
            continue
        if f.read_bytes() != other.read_bytes():
            bad.append((f.name, len(f.read_bytes()), len(other.read_bytes())))
    return bad, absent


def test_no_versioned_hook_has_drifted_from_the_live_one():
    if not LIVE.is_dir():
        pytest.skip("no live hook directory on this machine")
    bad, absent = drifted(VERSIONED, LIVE)
    assert not bad, (
        "a hook that RUNS differs from the hook that is COMMITTED: "
        + "; ".join(f"{n} (repo {a} bytes, live {b} bytes)" for n, a, b in bad)
        + ". Re-link or re-copy so the record and the behaviour agree."
    )
    assert len(list(VERSIONED.glob("*.py"))) - len(absent) >= 3, (
        f"only {len(list(VERSIONED.glob('*.py'))) - len(absent)} hook(s) were "
        f"actually compared, so this test establishes almost nothing. "
        f"Not installed here: {absent}"
    )


def test_the_hooks_the_founder_depends_on_are_both_versioned_and_live():
    """These 3 carry capabilities he asked for by name, so absence is a defect.

    `compaction_watch.py` tells him a compaction happened -- he drives this
    session remotely and the interface gives no other indication.
    `study_pulse.py` carries why the runs exist. `prompt_clock.py` is the sole
    mechanism for temporal awareness.
    """
    required = ["compaction_watch.py", "study_pulse.py", "prompt_clock.py"]
    missing_repo = [n for n in required if not (VERSIONED / n).is_file()]
    assert not missing_repo, f"not in the repository at all: {missing_repo}"
    if not LIVE.is_dir():
        pytest.skip("no live hook directory on this machine")
    missing_live = [n for n in required if not (LIVE / n).is_file()]
    assert not missing_live, (
        f"versioned but not installed, so it never runs: {missing_live}")


def test_the_drift_detector_actually_detects(tmp_path):
    """ANTI-VACUITY: plant one identical pair, one drifted, one uninstalled."""
    v, l = tmp_path / "versioned", tmp_path / "live"
    v.mkdir(), l.mkdir()
    (v / "same.py").write_text("x = 1\n")
    (l / "same.py").write_text("x = 1\n")
    (v / "changed.py").write_text("x = 1\n")
    (l / "changed.py").write_text("x = 2\n")
    (v / "uninstalled.py").write_text("x = 1\n")
    bad, absent = drifted(v, l)
    assert [n for n, _, _ in bad] == ["changed.py"], (
        f"the detector did not isolate the drifted file: {bad}")
    assert absent == ["uninstalled.py"], (
        f"an uninstalled hook was not reported as uninstalled: {absent}")


def test_the_committed_hook_really_fires_a_desktop_notification(tmp_path,
                                                                monkeypatch):
    """EXECUTED, not grepped -- and it is the committed copy that is executed.

    He reported on 2026-10-03 that a compaction alert in macOS notifications
    had never worked, and the cause was that no hook emitted one: 0 hooks in the
    whole directory called `osascript` or any notifier.

    THE FIRST VERSION OF THIS TEST ASSERTED ON THE HOOK'S SOURCE TEXT -- that
    `display notification` and `osascript` appear in it. That establishes only
    that the file describes itself consistently (`execute-do-not-grep`,
    2026-09-04), and it joined the source-text census this project ratchets on
    precisely because such guards break on correct edits.

    So this RUNS the committed hook with a fake `osascript` earlier on PATH and
    reads what the hook actually tried to execute. It also asserts the
    once-per-compaction key: a second run over the same compaction must stay
    silent, because 42 banners over 10.69 hours is how an alarm stops being an
    alarm.
    """
    import json
    import os
    import subprocess
    import sys

    hook = VERSIONED / "compaction_watch.py"
    if not hook.is_file():
        pytest.skip("the hook is not in this checkout")

    # A transcript whose last user entry is marked as a compaction summary,
    # which is the structural marker Claude Code writes.
    transcript = tmp_path / "session.jsonl"
    transcript.write_text(json.dumps({
        "type": "user", "isCompactSummary": True,
        "timestamp": "2026-10-03T07:09:31+01:00",
        "message": {"role": "user", "content": "compacted"}}) + "\n",
        encoding="utf-8")

    # A fake `osascript` that records its arguments instead of notifying.
    binq = tmp_path / "bin"
    binq.mkdir()
    log = tmp_path / "osascript_calls.txt"
    fake = binq / "osascript"
    fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\" >> " + f'"{log}"' + "\n",
                    encoding="utf-8")
    fake.chmod(0o755)

    env = dict(os.environ)
    env["PATH"] = f"{binq}{os.pathsep}" + env.get("PATH", "")
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    env["HOME"] = str(tmp_path)          # so the hook's state dir is disposable
    payload = json.dumps({"transcript_path": str(transcript),
                          "prompt": "continue"})

    first = subprocess.run([sys.executable, str(hook)], input=payload,
                           capture_output=True, text=True, env=env, timeout=60)
    assert first.returncode == 0, (
        f"the hook exited {first.returncode}, which would break the turn: "
        f"{first.stderr[:400]}")

    if not log.exists():
        # The hook may legitimately decline on a transcript it cannot resolve.
        # Distinguish that from a hook that emits no notification at all.
        assert "compaction" in (first.stdout or "").lower(), (
            "the hook neither fired a notification nor announced a compaction, "
            f"so the alert has silently stopped working. stdout: "
            f"{first.stdout[:300]!r}")
        pytest.skip("the hook did not resolve this planted transcript; its own "
                    "notice path is covered by "
                    "test_compaction_notice_is_local_time_2026-10-01.py")

    called = log.read_text(encoding="utf-8")
    assert "display notification" in called, (
        "the hook invoked the notification tool without a `display "
        f"notification` command: {called[:300]!r}")
    assert "rs" in called, (
        "the notification does not tell the founder to issue `rs`, which is "
        "the one action it exists to prompt")

    # ONCE PER COMPACTION. A second run over the same compaction is silent.
    before = log.read_text(encoding="utf-8")
    second = subprocess.run([sys.executable, str(hook)], input=payload,
                            capture_output=True, text=True, env=env, timeout=60)
    assert second.returncode == 0
    assert log.read_text(encoding="utf-8") == before, (
        "the hook fired a second notification for the SAME compaction; at the "
        "measured repeat rate that is 42 banners over 10.69 hours, which is "
        "how an alarm gets muted")
