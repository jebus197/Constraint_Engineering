"""Guards for scripts/remote_bridge_recovery_2026-09-09.py.

The claim this script carries is load-bearing: it says the host side of the
remote session recovers unaided, which redirects the whole remote-access remedy
away from the Mac. An instrument that cannot fail its own hypothesis must not be
allowed to support a claim like that, so the tests below construct logs where
the answer SHOULD be "no" and check that it is.

Written after the P-pass found the first version pairing each restart with the
first reconnect at ANY later time -- a reconnect 6.3 hours later, which is what
the founder physically returning would look like, scored as unaided recovery.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "remote_bridge_recovery",
    Path(__file__).resolve().parents[2] / "scripts" / "remote_bridge_recovery_2026-09-09.py")
rbr = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rbr)

SID = "cse_018W1WGDnyD49P2dDARjTpVU"


def quit_line(t: str) -> str:
    return f"{t} [info] [updater] Auto-restarting app after update pending for 85 hours"


def back_line(t: str, sid: str = SID) -> str:
    return f"{t} [info] [sessions-bridge] Session {sid} reconnected successfully"


def test_a_prompt_reconnect_counts_as_unaided_recovery():
    log = "\n".join([quit_line("2026-09-08 16:52:11"), back_line("2026-09-08 16:52:51")])
    rows = rbr.recoveries(log)
    assert len(rows) == 1
    assert rows[0][1] == 40.0
    assert rows[0][2] == SID


def test_a_reconnect_hours_later_does_NOT_count():
    """This is the defect the P-pass found. A reconnect 6.3 hours after the
    restart is what the founder driving home and touching the machine looks
    like. Scoring it as unaided recovery would confirm the hypothesis by
    construction."""
    log = "\n".join([quit_line("2026-09-08 16:52:11"), back_line("2026-09-08 23:10:00")])
    rows = rbr.recoveries(log)
    assert rows[0][1] is None, "a 6.3-hour gap must not be scored as unaided recovery"


@pytest.mark.parametrize("gap_s,window,expected_hit", [
    (40, 600, True), (75, 600, True), (601, 600, False), (599, 600, True),
    (40, 30, False),
])
def test_the_window_boundary_is_respected(gap_s, window, expected_hit):
    import datetime as dt
    q = dt.datetime(2026, 9, 8, 16, 52, 11)
    b = q + dt.timedelta(seconds=gap_s)
    log = "\n".join([quit_line(q.strftime("%Y-%m-%d %H:%M:%S")),
                     back_line(b.strftime("%Y-%m-%d %H:%M:%S"))])
    rows = rbr.recoveries(log, window_s=window)
    assert (rows[0][1] is not None) is expected_hit


def test_a_different_session_is_not_credited():
    log = "\n".join([quit_line("2026-09-08 16:52:11"),
                     back_line("2026-09-08 16:52:51", sid="cse_SOMEONE_ELSE")])
    assert rbr.recoveries(log, session_id=SID)[0][1] is None
    # ...but with no session filter it is reported, WITH the id, so a reader can see.
    assert rbr.recoveries(log)[0][2] == "cse_SOMEONE_ELSE"


def test_a_reconnect_BEFORE_the_restart_is_not_credited():
    log = "\n".join([back_line("2026-09-08 16:00:00"), quit_line("2026-09-08 16:52:11")])
    assert rbr.recoveries(log)[0][1] is None


def test_a_restart_that_never_recovers_is_reported_as_such():
    assert rbr.recoveries(quit_line("2026-09-08 16:52:11"))[0][1] is None


def test_a_log_with_no_restart_says_so_rather_than_dividing_by_zero():
    with pytest.raises(rbr.NoRestarts):
        rbr.recoveries(back_line("2026-09-08 16:52:51"))
    with pytest.raises(rbr.NoRestarts):
        rbr.recoveries("")


def test_two_restarts_each_get_their_own_nearest_reconnect():
    log = "\n".join([
        quit_line("2026-09-04 23:10:45"), back_line("2026-09-04 23:12:00"),
        quit_line("2026-09-08 16:52:11"), back_line("2026-09-08 16:52:51"),
    ])
    rows = rbr.recoveries(log)
    assert [r[1] for r in rows] == [75.0, 40.0]
