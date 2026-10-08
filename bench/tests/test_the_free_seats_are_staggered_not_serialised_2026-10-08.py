"""The 2 shared-subscription seats overlap, and their starts sit a gap apart.

FOUNDER RULING, 2026-10-08: *"launch the outstanding panel brief with my updated
framing under star topology, one blind run first and staggered dispatch as
normal."* The day before, the question that produced it: *"Is back to back
necessary? It doubles the duration of a panel review. Isn't it the case that all
that is needed is a few second[s] between dispatching each model?"*

Staggering was NOT previously the behaviour -- the free seats ran strictly one
after the other -- so this file holds the new property rather than describing it.

WHY IT CALLS THE DISPATCHER INSTEAD OF READING IT. The property under test is a
TIMING one: whether 2 seats on 1 subscription overlap, and how far apart their
starts fall. No assertion over source text can observe either. `execute-do-not-
grep`, and this is the 5th defect class in the project found by executing 2 forms
against each other rather than reading them.

THE 2 BOUNDS THAT CHOSE 20 SECONDS, both from committed measurement:
  * ABOVE 18.7 s, the one genuinely simultaneous co-failure in the record, which
    sits at session-establishment time (`scripts/the_contention_evidence_is_cap_
    confounded_2026-10-07.py`). The other 2 matched co-failures are both seats
    hitting 1 shared deadline, which is arithmetic rather than contention.
  * BELOW 26.7 s, the shortest first-seat duration over the 91 archived rounds
    where both free seats answered. SymPy reduces `max(d1, s+d2) <= d1+d2` to
    exactly `s <= d1` and z3 returns `unsat` on any counterexample, so a stagger
    above the shortest first-seat duration is the one case where staggering
    loses to serialising.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import threading
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

#: The establishment collision the stagger has to clear, and the shortest
#: first-seat duration it has to stay under. Both measured, both committed.
ESTABLISHMENT_COLLISION_S = 18.7
SHORTEST_FIRST_SEAT_S = 26.7


@pytest.fixture(scope="module")
def M():
    # NO `PANEL_BRIEF_UNCHECKED` HERE, AND THAT IS DELIBERATE.
    #
    # A first version of this fixture did `os.environ.setdefault(
    # "PANEL_BRIEF_UNCHECKED", "1")` to get the module imported. `setdefault`
    # NEVER RESTORES, so the variable leaked into every test that ran after it in
    # the same process -- and that variable makes the dispatcher SKIP brief
    # validation. The guard it disabled is
    # `test_panel_brief_format_2026-09-09.py::test_the_dispatcher_REFUSES_a_bad_brief_before_paying_a_seat`,
    # whose whole purpose is to stop money being spent on a defective brief. It
    # passed alone and failed in the batch, which is how the leak was found.
    #
    # A22 moved the brief binding out of import time, so the variable is not needed
    # for an import at all: verified by importing this module with the variable
    # absent from the environment. Setting a flag that disables a money guard, to
    # solve a problem that no longer exists, is the kind of leftover this project's
    # additive standard exists to catch.
    argv = list(sys.argv)
    sys.argv = ["test", "_guard_only"]
    try:
        spec = importlib.util.spec_from_file_location(
            "cmp_stagger", REPO / "bench" / "confer_maths_panel_2026-09-05.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["cmp_stagger"] = m
        spec.loader.exec_module(m)
    finally:
        sys.argv = argv
    return m


class _Recorder:
    """A stub seat that records when it started and finished, per seat."""

    def __init__(self, work_s=0.30):
        self.work_s = work_s
        self.spans: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def __call__(self, name, model, route):
        t0 = time.monotonic()
        time.sleep(self.work_s)
        t1 = time.monotonic()
        with self._lock:
            self.spans[name] = (t0, t1)
        return {"model": name, "route": route, "ok": True}

    def overlap(self, a, b) -> float:
        (a0, a1), (b0, b1) = self.spans[a], self.spans[b]
        return min(a1, b1) - max(a0, b0)

    def start_gap(self, a, b) -> float:
        return abs(self.spans[a][0] - self.spans[b][0])


SHARED = [("cc2", "opus", "claude_cli"), ("fable", "fable", "claude_cli")]


class TestTheStaggeredModeIsGenuinelyConcurrent:
    def test_the_2_shared_seats_overlap(self, M):
        """If they did not overlap this would still be serialisation."""
        rec = _Recorder(work_s=0.40)
        M.run_seat_group(SHARED, [], rec, 0.10)
        assert set(rec.spans) == {"cc2", "fable"}
        assert rec.overlap("cc2", "fable") > 0.0, (
            "the 2 seats did not overlap, so the stagger is serialisation with a "
            f"pause: {rec.spans}")

    def test_the_starts_are_held_at_least_the_stagger_apart(self, M):
        rec = _Recorder(work_s=0.05)
        M.run_seat_group(SHARED, [], rec, 0.25)
        gap = rec.start_gap("cc2", "fable")
        assert gap >= 0.25 * 0.9, (
            f"starts only {gap:.3f}s apart against a 0.25s stagger -- the delay "
            "is not being applied, so 2 establishments can still collide")

    def test_the_wall_clock_is_the_max_not_the_sum(self, M):
        """The founder's actual complaint: serialising doubles a panel."""
        rec = _Recorder(work_s=0.50)
        t0 = time.monotonic()
        M.run_seat_group(SHARED, [], rec, 0.05)
        elapsed = time.monotonic() - t0
        assert elapsed < 0.50 + 0.40, (
            f"{elapsed:.3f}s for 2 x 0.50s seats is closer to the sum than the "
            "max, so the staggered path is not running them together")


class TestStaggerZeroStillSerialises:
    """NOTHING IS REMOVED. The lock behaviour stays reachable, because the
    interventional test the dispatcher admits it never ran needs both arms."""

    def test_zero_runs_them_strictly_one_after_the_other(self, M):
        rec = _Recorder(work_s=0.20)
        M.run_seat_group(SHARED, [], rec, 0.0)
        assert rec.overlap("cc2", "fable") <= 0.0, (
            f"stagger 0 must not overlap: {rec.spans}")
        assert rec.spans["fable"][0] >= rec.spans["cc2"][1] - 1e-6, (
            "roster order was not preserved under serialisation")

    def test_both_modes_dispatch_every_seat_exactly_once(self, M):
        for stagger in (0.0, 0.05):
            rec = _Recorder(work_s=0.02)
            got = M.run_seat_group(SHARED, [], rec, stagger)
            assert len(got) == 2, (stagger, got)
            assert {r["model"] for r in got} == {"cc2", "fable"}, (stagger, got)


class TestSeatsOnOtherRoutesAreUnaffected:
    def test_an_independent_seat_runs_concurrently_in_both_modes(self, M):
        for stagger in (0.0, 0.05):
            rec = _Recorder(work_s=0.30)
            M.run_seat_group(SHARED, [("ge", "gemini", "openrouter")], rec, stagger)
            assert set(rec.spans) == {"cc2", "fable", "ge"}, (stagger, rec.spans)
            assert rec.overlap("cc2", "ge") > 0.0, (
                f"an independent-route seat was serialised against a shared one "
                f"at stagger {stagger}: {rec.spans}")


class TestTheDefaultIsInsideBothMeasuredBounds:
    def test_the_default_clears_the_establishment_collision(self, M):
        assert M.DEFAULT_STAGGER_S > ESTABLISHMENT_COLLISION_S, (
            f"{M.DEFAULT_STAGGER_S}s does not clear the {ESTABLISHMENT_COLLISION_S}s "
            "co-failure, which is the only collision a stagger can prevent")

    def test_the_default_stays_under_the_shortest_first_seat(self, M):
        assert M.DEFAULT_STAGGER_S < SHORTEST_FIRST_SEAT_S, (
            f"{M.DEFAULT_STAGGER_S}s exceeds the shortest observed first-seat "
            f"duration of {SHORTEST_FIRST_SEAT_S}s, so on that round staggering "
            "is SLOWER than serialising -- the condition SymPy reduces to s <= d1")

    def test_an_unset_variable_gives_the_default(self, M, monkeypatch):
        monkeypatch.delenv("PANEL_STAGGER_S", raising=False)
        assert M._stagger_seconds() == M.DEFAULT_STAGGER_S

    def test_an_empty_variable_gives_the_default(self, M, monkeypatch):
        monkeypatch.setenv("PANEL_STAGGER_S", "   ")
        assert M._stagger_seconds() == M.DEFAULT_STAGGER_S

    def test_an_explicit_value_is_honoured(self, M, monkeypatch):
        monkeypatch.setenv("PANEL_STAGGER_S", "7.5")
        assert M._stagger_seconds() == 7.5
        monkeypatch.setenv("PANEL_STAGGER_S", "0")
        assert M._stagger_seconds() == 0.0


class TestAMalformedValueRefusesRatherThanFallingBack:
    """MUTATION-GRADE. A `except ValueError: return DEFAULT` would pass every
    test above and still run a staggered panel for a caller who asked for
    something else. These 2 are the only tests that can tell them apart."""

    def test_a_non_numeric_value_raises(self, M, monkeypatch):
        monkeypatch.setenv("PANEL_STAGGER_S", "abc")
        with pytest.raises(SystemExit):
            M._stagger_seconds()

    def test_a_negative_value_raises(self, M, monkeypatch):
        monkeypatch.setenv("PANEL_STAGGER_S", "-1")
        with pytest.raises(SystemExit):
            M._stagger_seconds()
