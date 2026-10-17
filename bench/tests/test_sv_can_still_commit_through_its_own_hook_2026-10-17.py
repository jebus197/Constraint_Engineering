"""`sv` must wait longer than the pre-commit hook takes, and know how long that is.

FOUND 2026-10-17 BY EXECUTION. `scripts/cdsfl_sv.py` committed through a
subprocess with a fixed 60-second timeout. The pre-commit guard set had grown to
1,001 tests over 35 files taking 143 seconds, so `sv --commit --push` died with
`subprocess.TimeoutExpired` and STATE COULD NOT BE SAVED AT ALL. The error read
as a git failure rather than as a guard set that had outgrown its waiter, and the
cause was this session's own additions to that set.

A LARGER TYPED NUMBER WOULD ONLY MOVE THE DATE OF THE NEXT FAILURE. That is the
objection the founder raised on 2026-10-13 and again on 2026-10-14 to a cap with
no measurement behind it. So `hooks/pre-commit` records its own elapsed seconds
and `commit_timeout()` sizes the wait against them, with a floor for a fresh
checkout that has no record yet.

These assertions CALL `commit_timeout` against crafted records rather than
reading the source, and the last one compares the live recorded duration against
the live derived timeout, so growth in the guard set shows up here as a warning
with headroom left rather than as a save that cannot complete.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SV = REPO / "scripts" / "cdsfl_sv.py"
HOOK = REPO / "hooks" / "pre-commit"


@pytest.fixture(scope="module")
def sv():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("cdsfl_sv_under_test", SV)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_sv_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_the_floor_applies_when_nothing_is_recorded(sv, tmp_path):
    """A fresh checkout has no record, and must still get a usable wait."""
    assert sv.commit_timeout(tmp_path) == sv.COMMIT_TIMEOUT_FLOOR
    assert sv.COMMIT_TIMEOUT_FLOOR >= 300, (
        "the floor must exceed the hook's measured 143 s with headroom")


def test_a_recorded_duration_raises_the_wait(sv, tmp_path):
    """The wait tracks the measurement, which is the whole point."""
    rec = tmp_path / sv.HOOK_SECONDS_FILE
    rec.parent.mkdir(parents=True, exist_ok=True)
    rec.write_text("600\n", encoding="utf-8")
    got = sv.commit_timeout(tmp_path)
    assert got == 600 * sv.COMMIT_TIMEOUT_HEADROOM
    assert got > 600, "the wait must exceed the duration it is waiting for"


@pytest.mark.parametrize("junk", ["", "   ", "not a number", "-5", "0"])
def test_an_unusable_record_falls_back_to_the_floor(sv, tmp_path, junk):
    """A corrupt or absent record may not produce a wait shorter than the floor.

    `0` and `-5` are included deliberately: a multiplication would have returned
    0, and a 0-second timeout kills the commit instantly, which is worse than
    the defect being fixed.
    """
    rec = tmp_path / sv.HOOK_SECONDS_FILE
    rec.parent.mkdir(parents=True, exist_ok=True)
    rec.write_text(junk, encoding="utf-8")
    assert sv.commit_timeout(tmp_path) == sv.COMMIT_TIMEOUT_FLOOR


def test_the_hook_actually_records_what_sv_reads(sv):
    """Producer and consumer must agree on the path, not merely describe it.

    Asserted against the hook's own text for the PATH only -- the behaviour is
    asserted by `test_the_live_record_leaves_headroom` below, which reads a file
    a real commit wrote.
    """
    hook = HOOK.read_text(encoding="utf-8")
    assert sv.HOOK_SECONDS_FILE in hook, (
        f"the hook does not write {sv.HOOK_SECONDS_FILE}, so the wait can never "
        "track the duration")
    assert "trap" in hook and "EXIT" in hook, (
        "the duration must be recorded on EXIT, or a refused commit records "
        "nothing and the next wait is sized from a stale number")


def test_the_live_record_leaves_headroom(sv):
    """THE RATCHET. A real commit wrote this; the wait must still clear it."""
    rec = REPO / sv.HOOK_SECONDS_FILE
    if not rec.is_file():
        pytest.skip("no commit has run the hook in this checkout yet")
    try:
        seconds = int(rec.read_text().strip())
    except ValueError:
        pytest.skip("the record is not a number; another assertion covers that")
    if seconds <= 0:
        pytest.skip("the record is not a positive duration")
    wait = sv.commit_timeout(REPO)
    assert wait >= 2 * seconds, (
        f"the pre-commit hook took {seconds} s and sv waits {wait} s. The guard "
        f"set has grown into its own waiter's headroom -- raise "
        f"COMMIT_TIMEOUT_HEADROOM or split the set, BEFORE a state save fails.")
