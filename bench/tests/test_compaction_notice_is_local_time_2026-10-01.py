"""The compaction notice must announce LOCAL time, and an age that is not an hour out.

THE DEFECT, measured 2026-10-01. `hooks/compaction_watch.py` computed the age
of a compaction with `time.mktime(time.strptime(ts[:19], ...))`. Claude Code
writes transcript timestamps in UTC ("...Z"); `mktime` interprets a struct_time
as LOCAL, so the stamp was taken an hour early under BST. Two effects:

  1. The age was inflated by exactly the UTC offset. A compaction 791 s old was
     announced as "73m ago" -- 3600 s of inflation, exact in mpmath.
  2. The notice printed the UTC wall clock with NO zone label, directly beside
     `prompt_clock.py` printing local time WITH one.

IT INVERTED AN ORDERING, which is why this is guarded rather than tidied. Asked
whether a compaction fell before or after a save, the notice's "22:04" placed
it before a commit timestamped 22:58, when the truth was 23:04:19 BST and so
after it. The same hour reached a delivered report, whose elapsed-time
denominator was 1 hour too long.

THESE TESTS EXECUTE THE HOOK. They do not read its source: a test asserting on
source text would only confirm the module describes itself consistently, and
both the old and the new code describe themselves perfectly well.
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPO_HOOK = ROOT / "hooks" / "compaction_watch.py"
LIVE_HOOK = Path.home() / ".claude" / "hooks" / "compaction_watch.py"
STATE = Path.home() / ".claude" / ".compaction_watch"
SID = "zz-test-compaction-tz"


def _run(hook: Path, ts: str, tmp_path: Path) -> str:
    """Run the hook against a one-entry transcript and return its notice."""
    (STATE / SID).unlink(missing_ok=True)
    t = tmp_path / "t.jsonl"
    t.write_text(json.dumps({"type": "user", "isCompactSummary": True,
                             "timestamp": ts}) + "\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(hook)],
        input=json.dumps({"session_id": SID, "prompt": "hello",
                          "transcript_path": str(t)}),
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, "the hook must ALWAYS exit 0; blocking a prompt is worse"
    if not r.stdout.strip():
        return ""
    return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]


@pytest.fixture(autouse=True)
def _clean():
    yield
    (STATE / SID).unlink(missing_ok=True)


@pytest.mark.skipif(not REPO_HOOK.is_file(), reason="hook absent in this clone")
class TestTheNoticeSpeaksLocalTime:

    def test_age_is_not_inflated_by_the_utc_offset(self, tmp_path):
        when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5)
        ts = when.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        notice = _run(REPO_HOOK, ts, tmp_path)
        assert notice, "a fresh unacknowledged compaction must produce a notice"
        head = notice.splitlines()[0]
        assert "(5m ago)" in head or "(4m ago)" in head, (
            f"age is wrong; under the old arithmetic this reads ~65m: {head}")

    def test_the_old_arithmetic_would_fail_this_very_test(self, tmp_path):
        """THE MUTATION. If this passes, the test above cannot detect the bug."""
        when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5)
        ts = when.isoformat(timespec="seconds").replace("+00:00", "")
        old_age = time.time() - time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%S"))
        offset = -time.timezone if time.daylight == 0 else -time.altzone
        if offset == 0:
            pytest.skip("machine is at UTC; the defect is unobservable here")
        assert int(old_age) // 60 != 5, (
            "the old form agrees with the new one on this machine, so the "
            "guard above proves nothing")

    def test_the_wall_clock_shown_is_local_and_carries_a_zone_label(self, tmp_path):
        when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=3)
        ts = when.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        head = _run(REPO_HOOK, ts, tmp_path).splitlines()[0]
        local = when.astimezone()
        assert local.strftime("%H:%M:%S") in head, (
            f"the notice shows a non-local wall clock: {head}")
        label = local.strftime("%Z")
        if label:
            assert label in head, f"the stamp carries no zone label: {head}"

    def test_a_naive_stamp_is_taken_as_utc_not_local(self, tmp_path):
        """Claude Code writes UTC. A stamp without an offset must mean UTC."""
        when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=4)
        head = _run(REPO_HOOK, when.strftime("%Y-%m-%dT%H:%M:%S"), tmp_path).splitlines()[0]
        assert when.astimezone().strftime("%H:%M:%S") in head, head

    def test_an_explicit_offset_is_honoured_rather_than_assumed(self, tmp_path):
        when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=6)
        shifted = when.astimezone(dt.timezone(dt.timedelta(hours=5, minutes=30)))
        head = _run(REPO_HOOK, shifted.isoformat(timespec="seconds"), tmp_path).splitlines()[0]
        assert when.astimezone().strftime("%H:%M:%S") in head, (
            f"an explicit +05:30 offset was not honoured: {head}")

    def test_an_unparseable_stamp_neither_crashes_nor_asserts_a_time(self, tmp_path):
        notice = _run(REPO_HOOK, "not-a-timestamp", tmp_path)
        assert "UNPARSED" in notice or "unknown" in notice, (
            "a stamp that could not be read must say so, not print a guess")

    def test_the_live_copy_matches_the_versioned_one(self):
        """3 of this project's 4 earliest hooks existed in no repository at all."""
        if not LIVE_HOOK.is_file():
            pytest.skip("no live hook on this machine")
        assert LIVE_HOOK.read_bytes() == REPO_HOOK.read_bytes(), (
            "the running hook and the committed hook have diverged, so the "
            "tests below guard a file that is not the one in use")


@pytest.mark.skipif(not REPO_HOOK.is_file(), reason="hook absent in this clone")
class TestTheArmingPathComparesInstants:
    """A restore marker and a transcript stamp must be compared as INSTANTS."""

    def _hook_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("cw_probe", REPO_HOOK)
        m = importlib.util.module_from_spec(spec)
        sys.modules["cw_probe"] = m
        spec.loader.exec_module(m)
        return m

    def test_a_local_time_marker_cannot_pass_for_an_earlier_utc_compaction(self):
        """THE LATENT TWIN of the repaired fault, guarded before it can bite.

        Both writers emit UTC today, so the old lexicographic compare was
        correct. It was one edit away from silently disarming the alarm: a
        marker in BST is lexicographically LARGER than the UTC stamp of the
        same instant, so a restore an hour BEFORE a compaction would read as
        after it.
        """
        m = self._hook_module()
        base = dt.datetime(2026, 10, 1, 22, 4, 19, tzinfo=dt.timezone.utc)
        earlier_local = (base - dt.timedelta(minutes=30)).astimezone(
            dt.timezone(dt.timedelta(hours=1)))
        a = m.parse_transcript_ts(earlier_local.isoformat(timespec="seconds"))
        b = m.parse_transcript_ts("2026-10-01T22:04:19.096Z")
        assert a is not None and b is not None
        assert a < b, "a restore 30 minutes BEFORE the compaction read as after it"
        assert earlier_local.isoformat()[:19] > "2026-10-01T22:04:19", (
            "the string compare does NOT invert here, so this test is vacuous")

    def test_a_genuine_later_utc_marker_still_acknowledges(self):
        m = self._hook_module()
        a = m.parse_transcript_ts("2026-10-01T22:19:39+00:00")
        b = m.parse_transcript_ts("2026-10-01T22:04:19.096Z")
        assert a >= b, "a real restore after the compaction must still disarm"

    @pytest.mark.parametrize("junk", ["", "   ", None, "not-a-time", "2026-13-45T99:99:99"])
    def test_junk_parses_to_none_rather_than_raising(self, junk):
        assert self._hook_module().parse_transcript_ts(junk) is None
