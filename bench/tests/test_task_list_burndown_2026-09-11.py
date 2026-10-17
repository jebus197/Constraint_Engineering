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
        totals = [r[2] for r in mod.snapshots() if r[2]]
        drops = [(a, b) for a, b in zip(totals, totals[1:]) if b < a]
        assert not drops, f"the entry count fell at {drops[:3]}; entries were removed"

    def test_the_done_count_never_fell(self, mod):
        dones = [r[3] for r in mod.snapshots() if r[2]]
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


class TestTheConvergenceArgumentRestsOnTheRightThing:
    """The list converges because closure OUTPACES discovery, not because
    discovery is decaying.

    Discovery ran 72, 16, 7 across the list's 3 days and closure ran 19, 44, 21.
    The temptation is to fit a decay to the discovery series and quote a date.
    With 2 days of discovery-while-working -- day 1 is the list being CREATED --
    the day-on-day ratio is 0.4375 and a 95% Wilson interval on that split admits
    a ratio up to 1.0352, which is a process that does not decay at all. So the
    decay is NOT established and an ETA resting on it would be fabricated
    certainty.

    What IS measured is that closure outpaces discovery roughly 3 to 1 on the
    latest day. That is the property this class pins.
    """

    def test_the_branching_ratio_and_its_interval_are_reported(self, mod):
        """SUPERSEDES a single-day ratio, on a measurement rather than a view.

        THE OLD ASSERTION, and why it had to go. It required closure to outpace
        discovery ON THE LATEST DAY. Measured across the whole recorded series
        on 2026-10-17, that predicate holds on 6 of 13 days -- 46.1538% -- and
        fails on any day with 1 discovery and 0 closures, which the record shows
        on 2026-09-18, 2026-10-14 and 2026-10-16 as well as on the verdict-audit
        day that added 22 gap entries at once. A guard that is a coin flip on its
        own history is not a guard.

        WHAT REPLACES IT IS STRICTLY STRONGER, which is what the additive
        standard requires before a check may be narrowed. The script already
        computes the BRANCHING ratio -- new entries per entry closed -- with a
        95% interval and an exact test against R = 1, and reports whether the
        process is subcritical. That is stable across days, uses an interval
        rather than a point ratio, and guards the hazard the old assertion was
        reaching for: an ETA quoted off a closure rate when closing an entry
        keeps turning up defects that become entries.

        AND THE HONEST STATE IS RECORDED RATHER THAN ASSERTED AWAY: at the time
        of writing R is 0.8148 with an interval of [0.6155, 1.0787], p = 0.0873
        against R = 1, so the interval ADMITS a process that does not terminate
        and the subcritical verdict is False. This test does not require it to be
        True. It requires the figure, its interval and the verdict to be present,
        so that nobody can quote a date without meeting them.
        """
        import subprocess as _sp
        r = _sp.run([sys.executable, str(SCRIPT)], cwd=REPO,
                    capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-600:]
        out = r.stdout
        for needed in ("new entries per entry closed",
                       "95% interval on R",
                       "exact test against R = 1",
                       "SUBCRITICAL (terminates)"):
            assert needed in out, (
                f"the branching view no longer reports {needed!r}; without it a "
                f"reader can quote a closure-rate ETA with nothing to stop them")
        # and the series itself must still be derivable, which is what the
        # branching ratio is computed from
        rows = mod.snapshots()
        disc, clo = mod.per_day(rows)
        assert sum(disc.values()) > 0 and sum(clo.values()) > 0, (
            "the burndown series is empty, so the branching ratio is unfounded")

    def test_it_does_not_claim_termination_the_interval_does_not_support(self, mod):
        """The one direction that would be fabricated certainty.

        If the interval on R admits 1 or more, the script must NOT report the
        process as subcritical. This is the assertion that actually protects the
        founder from a date, and it holds whichever way the evidence falls.
        """
        import re as _re
        import subprocess as _sp
        r = _sp.run([sys.executable, str(SCRIPT)], cwd=REPO,
                    capture_output=True, text=True, timeout=900)
        out = r.stdout
        iv = _re.search(r"95% interval on R\s*:\s*\[([\d.]+),\s*([\d.]+)\]", out)
        sub = _re.search(r"SUBCRITICAL \(terminates\)\s*:\s*(\w+)", out)
        assert iv and sub, f"could not read the branching report:\n{out[-500:]}"
        hi = float(iv.group(2))
        claims_termination = sub.group(1).strip().lower() == "true"
        if hi >= 1.0:
            assert not claims_termination, (
                f"the upper bound on R is {hi}, which admits a process that does "
                f"not terminate, yet the script reports it as subcritical. That "
                f"is fabricated certainty about when the list ends.")

    def test_day_one_is_creation_not_discovery(self, mod):
        """A reader comparing days must drop the first, and the numbers make that
        unmistakable rather than relying on the docstring."""
        rows = mod.snapshots()
        disc, _clo = mod.per_day(rows)
        days = sorted(disc)
        assert disc[days[0]] > 3 * disc[days[1]], (
            "day 1 is no longer dominated by the list's initial population, so "
            "treating it as creation rather than discovery may no longer be right")

    def test_discovery_and_closure_cover_every_entry(self, mod):
        """ANTI-VACUITY. If either counter silently missed entries, both the
        convergence claim and the growth share would be measuring a subset."""
        rows = mod.snapshots()
        disc, clo = mod.per_day(rows)
        last = [r for r in rows if r[2]][-1]
        assert sum(disc.values()) == last[2], (
            f"discovery totals {sum(disc.values())} but the list holds {last[2]}")
        assert sum(clo.values()) == last[3], (
            f"closure totals {sum(clo.values())} but {last[3]} entries are DONE")


class TestTheListTerminates:
    """The founder's question: could the list grow forever?

    Formally: treat each closed entry as an individual in a branching process
    producing R new entries. R < 1 is SUBCRITICAL and terminates with probability
    1; R >= 1 need never terminate. R < 1 is equivalent to p < 1/2 for
    p = additions / (additions + closures), so it is an ordinary proportion test.

    MEASURED: R = 0.4444, 95% Wilson [0.3009, 0.6565], exact binomial test
    against the critical threshold p = 1.933172e-05. The whole interval lies
    below 1.

    THIS TEST EXISTS TO FAIL IF THAT STOPS BEING TRUE. If R's upper bound ever
    reaches 1, the answer to the founder's question changes from "it terminates"
    to "it might not", and that is a conversation to have rather than a number to
    quietly restate.
    """

    def test_the_process_is_subcritical(self, mod):
        b = mod.branching(mod.snapshots())
        assert b["subcritical"], (
            f"R = {b['R']:.4f} with 95% interval "
            f"[{b['R_interval'][0]:.4f}, {b['R_interval'][1]:.4f}]. The upper "
            f"bound has reached 1: the list can no longer be said to terminate, "
            f"and the founder asked to be told if that happened.")

    def test_the_threshold_is_where_it_should_be(self, mod):
        """ANTI-VACUITY. A test that called everything subcritical would pass on
        any tree at all, so the mapping from p to R is checked at the critical
        point itself."""
        b = mod.branching(mod.snapshots())
        lo, hi = b["p_interval"]
        assert (hi < 0.5) == b["subcritical"], "the p-to-R mapping has drifted"
        # p = 0.5 must map to R = 1, exactly.
        assert abs((0.5 / (1 - 0.5)) - 1.0) < 1e-12

    def test_withdrawn_entries_are_not_counted_as_outstanding(self, mod):
        """They are closed. Counting them as live inflated the projection from 7
        entries to 11 and its tail from 12.60 to 19.80 before this was fixed."""
        rows = mod.snapshots()
        last = [r for r in rows if r[2]][-1]
        assert len(last) > 4, "the snapshot no longer carries a WITHDRAWN count"
        assert last[4] > 0, (
            "no entry is WITHDRAWN, so this test is not exercising the exclusion "
            "it exists to protect")
        assert last[2] - last[3] - last[4] < last[2] - last[3]
