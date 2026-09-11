"""An ETA from a closure rate is wrong when the list grows while being closed.

The founder asked for an ETA on completing the master task list. A burn-down
figure answers that only if the list is a FIXED target, and this one is not:
**36 of its 95 entries, 37.8947%, were created AFTER it was first populated**,
Wilson [28.7898%, 47.9406%], Clopper-Pearson [28.1364%, 48.4296%]. Closing an
entry keeps turning up defects that become entries.

THE FIRST ATTEMPT AT THIS FIGURE UNDERSTATED IT BY MORE THAN HALF. Measured by
hand from the snapshot at the end of the list's second day, it came out at
16.8421% -- because 20 entries had already been added before that start point. A
figure whose value depends on where the author began measuring is not a
measurement, and that is why the producer is committed.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "task_list_burndown_2026-09-11.py"


@pytest.fixture(scope="module")
def mod():
    if subprocess.run(["git", "rev-parse", "--git-dir"], cwd=REPO,
                      capture_output=True).returncode != 0:
        pytest.skip("the burn-down is read from git history, which is absent here")
    spec = importlib.util.spec_from_file_location("burndown", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestItReadsTheRealHistory:
    def test_the_curve_is_not_empty(self, mod):
        rows = mod.snapshots()
        assert len(rows) > 20, f"only {len(rows)} commits touched the list"

    def test_the_list_only_ever_grew_or_held(self, mod):
        """The count may rise and may hold, but a FALL would mean entries
        vanished rather than being marked WITHDRAWN, which the additive standard
        forbids.

        MEASURED ON DISTINCT IDS, and the first version was not. Counting raw
        marker LINES showed a fall of 2 at `3b2d9a7` -- which was 6 duplicated
        ids being cleaned up, not entries being deleted. A count that reads a
        de-duplication as a deletion would have reported an additive-standard
        violation that never happened.
        """
        totals = [t for _w, _s, t, _d in mod.snapshots() if t]
        drops = [(a, b) for a, b in zip(totals, totals[1:]) if b < a]
        assert not drops, f"the entry count fell at {drops[:3]}; entries were removed"

    def test_the_done_count_never_fell(self, mod):
        dones = [d for _w, _s, t, d in mod.snapshots() if t]
        drops = [(a, b) for a, b in zip(dones, dones[1:]) if b < a]
        assert not drops, f"the DONE count fell at {drops[:3]}"


class TestTheGrowthTermIsReal:
    def test_the_list_grew_while_being_closed(self, mod):
        """The whole point. If this ever reads 0, an ordinary burn-down ETA
        becomes valid and this test should be deleted deliberately."""
        f = mod.figures(mod.snapshots())
        assert f["added"] > 0, (
            "no entries were added while the list was worked; the growth term "
            "this file exists to measure has gone")
        assert f["multiplier"] > 1.0

    def test_the_start_point_is_the_first_populated_snapshot(self, mod):
        """THE DEFECT THAT PRODUCED THE FIRST, WRONG FIGURE. Starting anywhere
        later silently discards the entries added before that point."""
        rows = mod.snapshots()
        f = mod.figures(rows)
        first_populated = next(r for r in rows if r[2] > 0)
        assert f["first"] == first_populated, (
            f"the window starts at {f['first'][0]} but the list was first "
            f"populated at {first_populated[0]}; entries added in between are "
            f"being discarded, which is how 37.8947% was first measured as "
            f"16.8421%")

    def test_a_later_start_point_would_understate_it(self, mod):
        """ANTI-VACUITY for the test above: it only matters if the choice
        actually changes the answer. It does."""
        rows = [r for r in mod.snapshots() if r[2]]
        full = mod.figures(rows)
        later = mod.figures(rows[len(rows) // 2:])
        assert later["added"] < full["added"], (
            "starting halfway through gives the same growth, so the start point "
            "does not matter and the test above is guarding nothing")


class TestItRuns:
    def test_the_script_exits_zero_and_names_its_caveat(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-600:]
        assert "added per closed" in r.stdout, r.stdout[:400]
        assert "WOULD BE WRONG BY THAT MULTIPLIER" in r.stdout, (
            "the script no longer states that a closure-rate ETA is wrong, which "
            "is the one thing a reader must not miss")

    def test_an_unknown_flag_is_refused(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--nope"], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode != 0
        assert "unrecognized arguments" in r.stderr
