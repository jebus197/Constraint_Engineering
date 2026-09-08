"""The compaction alarm must clear on the RESTORE EVENT, not on a text pattern.

WHY THIS FILE EXISTS. `scripts/cdsfl_recover.py --full` writes
`~/.claude/.compaction_watch/last_recovery`, and `~/.claude/hooks/compaction_watch.py`
reads it. That marker was written three times before it worked once:

1. `_record_recovery_ran()` was defined and never called -- the patch that added it
   targeted a `return 0` that `main()` does not have. It read as done.
2. Once called, it raised `AttributeError: type object 'datetime.datetime' has no
   attribute 'datetime'`, because line 22 binds `datetime` to the CLASS.
3. The repair for that used `timezone.utc` without importing `timezone`, and a
   blanket `except Exception: pass` swallowed the `NameError` and reported success.

Every one of those three passed a reading. None survived an execution. So this file
EXECUTES the script and asserts on the file system, per `execute-do-not-grep`.

HOME is redirected to a temporary directory for every subprocess, so the suite never
touches the founder's real alarm state.
"""
import json, os, pathlib, subprocess, sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RECOVER = REPO / "scripts" / "cdsfl_recover.py"
HOOK = pathlib.Path.home() / ".claude" / "hooks" / "compaction_watch.py"


def _run_recover(home, *args):
    env = dict(os.environ, HOME=str(home))
    return subprocess.run([sys.executable, str(RECOVER), *args], cwd=str(REPO),
                          env=env, capture_output=True, text=True, timeout=300)


def _marker(home):
    return home / ".claude" / ".compaction_watch" / "last_recovery"


def test_full_restore_writes_the_marker(tmp_path):
    proc = _run_recover(tmp_path, "--full")
    assert proc.returncode == 0, proc.stderr[-2000:]
    m = _marker(tmp_path)
    assert m.is_file(), (
        "--full completed but recorded nothing. This is the exact shape that shipped "
        "three times: the run looks successful and the alarm never clears.\n"
        f"stderr: {proc.stderr[-2000:]}"
    )
    stamp = m.read_text(encoding="utf-8").strip()
    assert len(stamp) >= 19 and stamp[4] == "-" and stamp[10] == "T", stamp


def test_a_partial_report_does_not_count_as_a_restore(tmp_path):
    """Without --full the script prints a report; a report is not a restore."""
    proc = _run_recover(tmp_path)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert not _marker(tmp_path).exists(), "a partial run silenced the alarm"


def test_the_marker_is_not_written_silently_on_failure(tmp_path):
    """A write failure must be REPORTED, not swallowed.

    The third defect above was `except Exception: pass`. Here the marker's parent is
    made a FILE, so mkdir raises OSError; the run must still succeed (bookkeeping
    never breaks a recovery) but must say so on stderr.
    """
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / ".compaction_watch").write_text("not a directory")
    proc = _run_recover(tmp_path, "--full")
    assert proc.returncode == 0, "bookkeeping must not break the recovery run"
    assert "could not record the restore marker" in proc.stderr, (
        "the failure was swallowed -- silent failure is what hid the bug twice.\n"
        f"stderr: {proc.stderr[-2000:]}"
    )


@pytest.mark.skipif(not HOOK.is_file(), reason="operator hook not installed on this machine")
@pytest.mark.parametrize(
    "compaction_ts,prompt,expect_alarm,why",
    [
        ("2000-01-01T00:00:00.000Z", "", False, "restore is newer than the compaction"),
        ("2999-01-01T00:00:00.000Z", "", True, "compaction is newer than the restore"),
        ("2999-01-01T00:00:00.000Z", "rs", False, "`rs` issued directly"),
        ("2999-01-01T00:00:00.000Z", "When was your last compaction, so I can run `rs` as needed?",
         True, "PROSE mentioning rs must not disarm the alarm"),
        ("2999-01-01T00:00:00.000Z", "a, d (Do the rs first.)", False,
         "a real MC command line must disarm it"),
    ],
)
def test_hook_decision_tracks_the_marker(tmp_path, compaction_ts, prompt, expect_alarm, why):
    """END TO END: the marker the script writes is the one the hook reads.

    Two halves shipped separately and neither proved the other. This runs the real
    hook over a synthetic transcript, with HOME redirected, after a real `--full`.
    """
    assert _run_recover(tmp_path, "--full").returncode == 0
    tr = tmp_path / "transcript.jsonl"
    tr.write_text(json.dumps({"type": "user", "isCompactSummary": True,
                              "timestamp": compaction_ts}) + "\n")
    payload = json.dumps({"session_id": "pytest_marker", "prompt": prompt,
                          "transcript_path": str(tr)})
    proc = subprocess.run([sys.executable, str(HOOK)], input=payload, env=dict(os.environ, HOME=str(tmp_path)),
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, "a hook must never block a prompt"
    alarmed = "[compaction]" in proc.stdout
    assert alarmed is expect_alarm, f"{why}: expected alarm={expect_alarm}, got {alarmed!r}\n{proc.stdout}"


@pytest.mark.skipif(not HOOK.is_file(), reason="operator hook not installed on this machine")
def test_removing_the_marker_re_arms_the_alarm(tmp_path):
    """MUTATION TEST. Break what the guard protects and watch it go red.

    Three guards written on 2026-09-07 passed their own suites while protecting
    nothing. A guard that cannot fail is not a guard, so this deletes the marker and
    requires the alarm to come back.
    """
    assert _run_recover(tmp_path, "--full").returncode == 0
    tr = tmp_path / "transcript.jsonl"
    tr.write_text(json.dumps({"type": "user", "isCompactSummary": True,
                              "timestamp": "2000-01-01T00:00:00.000Z"}) + "\n")

    def hook(sid):
        payload = json.dumps({"session_id": sid, "prompt": "", "transcript_path": str(tr)})
        return subprocess.run([sys.executable, str(HOOK)], input=payload,
                              env=dict(os.environ, HOME=str(tmp_path)),
                              capture_output=True, text=True, timeout=60).stdout

    assert "[compaction]" not in hook("mut_a"), "marker present but the alarm fired anyway"
    _marker(tmp_path).unlink()
    assert "[compaction]" in hook("mut_b"), (
        "the alarm stayed silent with the marker DELETED, so the marker is decorative"
    )
