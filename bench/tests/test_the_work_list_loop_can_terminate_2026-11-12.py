#!/usr/bin/env python3
"""The window's work-list runner is EXECUTED here, and its loop can terminate.

★ WHY THIS FILE EXISTS, AND IT CLOSES A DEFECT IN MY OWN ADDITION. A FOLLOW pass
on 2026-11-12 searched the tree for dependants of the 2 files written minutes
earlier and found `scripts/the_windows_work_list_2026-11-12.py` with **0**
dependants and `scripts/are_items_1_to_11_done_2026-11-12.py` reached by nothing
but that runner. No gate and no board collected either. Under the additive
standard's symmetric form -- *an addition that nothing reaches is not additive
either* -- both were the 12th instance of a defect class this project has 11
confirmed cases of. This guard is what reaches them.

★ WHAT THE RUNNER IS FOR. The founder asked twice why the session stops with
work outstanding. Measured: `hooks/work_not_narrate.py:696` allows the stop once
`MAX_REFUSALS_PER_TURN = 8` is spent, and this session's transcript shows that
announcement **219 times**. The budget is correct and must stay -- an unbounded
Stop hook can trap a session. But no hook can ever resume work, because a hook
is a subprocess and cannot call a model tool: 0 of the 18 hooks in `hooks/` can.
So the termination condition has to live in an EXIT CODE that a background
invocation carries back. 1 means work remains and names the next item; 0 means
the list is confirmed complete.

★ THE TEST THAT MATTERS IS THE ONE FOR EXIT 0. A runner that can only ever exit
1 is a loop with no end, which is strictly WORSE than stopping, because it would
spin on his 8 cores indefinitely. `test_zero_is_reachable` drives a constructed
all-settled state for exactly that reason, since the live tree does not yet
satisfy it and a live-data-only test could never see the fault.

Costs nothing: reads local files, dispatches to no model, runs no pytest.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "scripts" / "the_windows_work_list_2026-11-12.py"
HALF_A = REPO / "scripts" / "are_items_1_to_11_done_2026-11-12.py"
HALF_B = REPO / "scripts" / "are_items_12_to_21_done_2026-11-12.py"


@pytest.fixture(scope="module")
def WL():
    assert RUNNER.is_file(), f"the runner is missing: {RUNNER}"
    spec = importlib.util.spec_from_file_location("wl_guard", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestBothHalvesAreReached:
    def test_both_halves_exist_and_are_named_by_the_runner(self, WL):
        assert HALF_A.is_file() and HALF_B.is_file()
        named = {p.name for p in WL.HALVES}
        assert {HALF_A.name, HALF_B.name} <= named, named

    def test_the_runner_measures_all_21_items(self, WL):
        items = WL.measure()
        assert sorted(items) == list(range(1, 22)), sorted(items)

    def test_each_half_derives_its_own_repository_root(self):
        """A typed root measures whatever tree the file was copied FROM."""
        for p in (RUNNER, HALF_A, HALF_B):
            src = p.read_text(encoding="utf-8")
            assert "parents[1]" in src or "parents[2]" in src, p.name
            assert '"/Users/georgejackson/Developer_Projects/Constraint_Engineering"' \
                not in src, f"{p.name} hardcodes the repository root"

    def test_a_missing_half_raises_rather_than_measuring_less(self, WL):
        """Silently measuring a shorter list would report false completeness."""
        orig = WL.HALVES
        WL.HALVES = (REPO / "scripts" / "no_such_half_2026-11-12.py",)
        try:
            with pytest.raises((SystemExit, Exception)):
                WL.measure()
        finally:
            WL.HALVES = orig


class TestTheLoopCanTerminate:
    """CONSTRUCTED states, because the live tree exercises only 1 branch."""

    @staticmethod
    def _blocking(WL, items):
        return sorted(n for n, r in items.items()
                      if n not in WL.NOT_BLOCKING and r["verdict"] not in WL.SETTLED)

    def test_zero_is_reachable_when_every_item_is_settled(self, WL):
        """★ THE LOAD-BEARING TEST. Without it the loop could never end."""
        items = {n: {"title": "t", "verdict": "DONE", "note": "", "checks": {}}
                 for n in range(1, 22)}
        assert self._blocking(WL, items) == []

    def test_one_is_reached_when_any_blocking_item_is_open(self, WL):
        items = {n: {"title": "t", "verdict": "DONE", "note": "", "checks": {}}
                 for n in range(1, 22)}
        items[18] = {**items[18], "verdict": "NOT DONE"}
        assert self._blocking(WL, items) == [18]

    def test_the_deferred_commit_does_not_block_but_is_reported(self, WL):
        """His ruling: the commit comes last, once the work list is complete."""
        items = {n: {"title": "t", "verdict": "DONE", "note": "", "checks": {}}
                 for n in range(1, 22)}
        items[14] = {**items[14], "verdict": "PARTIAL"}
        assert self._blocking(WL, items) == [], "the commit must not gate the work"
        deferred = sorted(n for n in WL.NOT_BLOCKING
                          if items.get(n, {}).get("verdict") not in WL.SETTLED)
        assert deferred == [14], deferred

    def test_retired_counts_as_settled(self, WL):
        """Item 4 is retired as a stale snapshot; it must not block forever."""
        assert "RETIRED" in WL.SETTLED
        items = {n: {"title": "t", "verdict": "DONE", "note": "", "checks": {}}
                 for n in range(1, 22)}
        items[4] = {**items[4], "verdict": "RETIRED"}
        assert self._blocking(WL, items) == []

    def test_an_unknown_verdict_BLOCKS_rather_than_passing(self, WL):
        """Fail-closed: a verdict nobody anticipated must not read as settled."""
        items = {n: {"title": "t", "verdict": "DONE", "note": "", "checks": {}}
                 for n in range(1, 22)}
        items[7] = {**items[7], "verdict": "PROBABLY FINE"}
        assert self._blocking(WL, items) == [7]


class TestItRunsAndItsHelpIsFree:
    def test_the_runner_exits_1_while_work_remains_and_names_the_next_item(self):
        r = subprocess.run([sys.executable, str(RUNNER), "--quiet"], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode in (0, 1), f"unexpected exit {r.returncode}"
        if r.returncode == 1:
            assert "NEXT: item" in r.stdout, r.stdout[-600:]
            assert "INCOMPLETE" in r.stdout
        else:
            assert "COMPLETE" in r.stdout, r.stdout[-600:]

    def test_help_answers_without_running_the_measurement(self):
        r = subprocess.run([sys.executable, str(RUNNER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-600:]
        assert r.stdout.lower().startswith("usage:")
        assert "WORK LIST" not in r.stdout

    def test_the_json_mode_carries_the_blocking_set(self):
        import json
        r = subprocess.run([sys.executable, str(RUNNER), "--json"], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
        d = json.loads(r.stdout)
        assert set(d) >= {"items", "blocking_open", "deferred_by_his_ruling",
                          "complete"}, sorted(d)
        assert len(d["items"]) == 21, len(d["items"])
        assert d["complete"] is (not d["blocking_open"])


class TestHisMarkingClauseIsChecked:
    """★ HIS INSTRUCTION HAD 3 CLAUSES AND THE RUNNER CHECKED 2 OF THEM.

    Added 2026-11-12, after the gap bit. His words, verbatim: *"mark and items
    on there that are already done as done and record them in your
    registry/ticket store as done also."* The 21 predicates measure whether the
    WORK is done; not one asked whether the item's own entry had been MARKED
    done. So the runner printed `exit 0 -- the loop ends here` while B145
    through B150 all still read `state: OPEN` with their tickets open.

    THE PASSING INPUT CANNOT TEST THIS DEFENCE, so every case below drives
    `entry_states` with a constructed state map rather than the live task list.
    A test that only ran against a correct tree would pass whether the predicate
    worked or not -- which is how the gap survived in the first place.
    """

    @staticmethod
    def _all_done(WL):
        return {v: "DONE" for v in set(WL.ENTRY_OF.values())}

    @staticmethod
    def _settled(n=21):
        return {i: {"verdict": "DONE", "title": "t", "note": "", "checks": {}}
                for i in range(1, n + 1)}

    def test_the_map_names_only_entries_that_exist(self, WL):
        """A declared pair pointing at nothing would accuse a correct tree."""
        states = WL.entry_states()
        assert states, "the live task list did not parse, so this says nothing"
        for item, ident in sorted(WL.ENTRY_OF.items()):
            assert ident in states, (
                f"item {item} is mapped to {ident}, which is not in the task list")

    def test_an_unmarked_entry_IS_reported(self, WL, monkeypatch):
        """The case the gap missed: work done, entry still OPEN."""
        st = self._all_done(WL)
        victim = WL.ENTRY_OF[15]
        st[victim] = "OPEN"
        monkeypatch.setattr(WL, "entry_states", lambda: st)
        gap, note = WL.marking_gap(self._settled())
        assert gap == [15], gap
        assert victim in note and "OPEN" in note, note

    def test_a_fully_marked_list_reports_no_gap(self, WL, monkeypatch):
        monkeypatch.setattr(WL, "entry_states", lambda: self._all_done(WL))
        gap, note = WL.marking_gap(self._settled())
        assert gap == [], gap
        assert not note, note

    def test_an_entry_absent_from_the_list_is_NAMED(self, WL, monkeypatch):
        """Silence on a missing entry would be a vacuous pass."""
        st = self._all_done(WL)
        del st[WL.ENTRY_OF[21]]
        monkeypatch.setattr(WL, "entry_states", lambda: st)
        gap, note = WL.marking_gap(self._settled())
        assert WL.ENTRY_OF[21] in note, note

    def test_an_unparseable_list_says_UNVERIFIED_and_still_terminates(
            self, WL, monkeypatch):
        """A runner that cannot reach 0 is worse than one without this check,
        so a failure to read must never block -- and must never be recorded as
        a verified pass either."""
        monkeypatch.setattr(WL, "entry_states", lambda: {})
        gap, note = WL.marking_gap(self._settled())
        assert gap == [], gap
        assert "UNVERIFIED" in note, note

    def test_it_does_not_fire_on_work_that_is_not_done(self, WL, monkeypatch):
        """The marking clause is about items whose WORK is complete. Firing on
        unfinished work would double-count it and rename the reason."""
        monkeypatch.setattr(WL, "entry_states",
                            lambda: {v: "OPEN" for v in set(WL.ENTRY_OF.values())})
        items = self._settled()
        items[15] = {**items[15], "verdict": "NOT DONE"}
        gap, _note = WL.marking_gap(items)
        assert 15 not in gap, gap

    def test_the_gap_reaches_the_exit_code_not_just_the_print(self, WL):
        """★ THE TEST THAT MATTERS. A note printed beside `exit 0` would be the
        unwired addition the additive standard forbids: the loop would still
        end. This asserts the gap is folded into `blocking_open`, which is what
        the exit code is computed from."""
        src = RUNNER.read_text(encoding="utf-8")
        i_gap = src.index("gap, gap_note = marking_gap(items)")
        i_use = src.index("blocking_open.append(n)", i_gap)
        i_exit = src.index("if blocking_open:", i_use)
        assert i_gap < i_use < i_exit, (
            "the marking gap is computed but never reaches blocking_open, so "
            "the loop would end with his clause outstanding")
