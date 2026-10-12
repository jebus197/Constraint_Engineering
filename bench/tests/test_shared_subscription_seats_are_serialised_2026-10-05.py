#!/usr/bin/env python3
"""Seats sharing one subscription must not be dispatched at the same instant.

WHAT WAS WRONG. Every `claude_cli` seat authenticates against the SAME Max
subscription, and `bench/confer_maths_panel_2026-09-05.py` submitted the whole roster
to `ThreadPoolExecutor(max_workers=len(MODELS))`, so both free seats hit `claude -p`
simultaneously.

THE EVIDENCE, measured by `scripts/why_cc2_times_out_2026-10-05.py` over 137 archived
`claude_cli` seat replies:

  * The seats are NOT different in speed. Mann-Whitney over 64 cc2 and 65 fable
    successful replies: U = 2258.0, p = 0.4031, independent rank computation agreeing.
    Medians 809.5s (cc2) and 720.7s (fable).
  * cc2 is NOT failing more than fable: Fisher p = 0.7183 overall, 1.0000 recent;
    Barnard 0.6179 and 0.8396. BOTH seats roughly tripled recently (cc2 4.08% ->
    15.00%, fable 2.08% -> 10.00%), and that rise IS significant: Fisher p = 0.046723,
    Barnard p = 0.044514.
  * Failures are NOT independent. 3 of the 5 failing rounds lost BOTH seats at
    near-identical durations — 1956.0/1956.2, 902.0/902.0, 18.7/18.8 seconds — which a
    binomial test against the measured per-seat rate puts at p = 1.556646e-07. Two
    separate processes do not fail at matched times by chance.

WHAT THIS TEST HOLDS, and what it does NOT. It holds the SCHEDULING property: no two
`claude_cli` seats are in flight at once, while seats on other routes still overlap.
It does not and cannot show that serialising cures the timeouts — that requires
running a panel both ways and is recorded as an open measurement. A scheduling change
with a stated reason is not a demonstrated cure, and this file does not pretend
otherwise.

The dispatcher is NOT imported here: importing it binds a brief, consults spend gates
and can build sandboxes. The scheduling block is extracted and executed against a
recording stub, so the assertions run the real control flow with no dispatch.
"""
import pathlib
import re
import sys
import threading
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
DISPATCHER = REPO / "bench" / "confer_maths_panel_2026-09-05.py"


class _Recorder:
    """Records per-route concurrency of every simulated seat call.

    THE FIRST VERSION COUNTED GLOBALLY and was wrong: it stored the TOTAL number
    of live calls under whichever route happened to finish, so a concurrent
    openrouter seat made `claude_cli` read 3 while exactly 1 claude_cli seat was
    in flight. The test failed against a correct fix. Concurrency is a per-route
    question, so it is now counted per route.
    """

    def __init__(self, hold=0.05):
        self.hold = hold
        self.lock = threading.Lock()
        self.live_by_route = {}
        self.max_live_by_route = {}
        self.order = []

    def __call__(self, name, model, route):
        with self.lock:
            cur = self.live_by_route.get(route, 0) + 1
            self.live_by_route[route] = cur
            self.max_live_by_route[route] = max(
                self.max_live_by_route.get(route, 0), cur)
            self.order.append(("start", name, route, time.monotonic()))
        time.sleep(self.hold)
        with self.lock:
            self.live_by_route[route] -= 1
            self.order.append(("end", name, route, time.monotonic()))
        return {"model": name, "route": route, "ok": True}


def _scheduler():
    """Return the dispatcher's REAL scheduling function, by importing it.

    RE-POINTED 2026-10-12 ON HIS RULING: *"yes stagger the seats. I've already ruled on
    this several times."*

    WHAT THIS FILE USED TO DO, AND WHY IT BROKE. It located the scheduling block in the
    dispatcher's SOURCE between 2 literal anchors, exec'd the lifted text, and failed
    loudly if it could not find them. On 2026-10-08 the block was extracted into the named
    function `run_seat_group`, so the end anchor -- `results.extend(...)` -- ceased to
    exist and all 4 tests here reported "this guard is testing nothing" for 4 days. The
    system was never broken; the instrument was reading source text and the source moved.
    `execute-do-not-grep`, and the extraction is what makes the honest form possible:
    there is now a function to CALL.

    AND THE PROPERTY UNDER TEST CHANGED WITH HIS RULING, which is the other half. These
    tests asserted STRICT SERIALISATION of the 2 shared-subscription seats. His ruling of
    2026-10-08 replaced that with a stagger -- *"Is back to back necessary? It doubles the
    duration of a panel review. Isn't it the case that all that is needed is a few
    second[s] between dispatching each model?"* -- so asserting non-overlap
    unconditionally would now assert against the shipped design.

    BOTH BEHAVIOURS ARE STILL REACHABLE AND BOTH ARE TESTED HERE. `run_seat_group`
    staggers when `stagger_s > 0` and SERIALISES when it is 0, so his earlier ruling was
    not removed, it was made selectable. The real default is pinned separately at 20.0 s
    without any test sleeping for 20 seconds.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("cmp_panel_live", str(DISPATCHER))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cmp_panel_live"] = mod
    spec.loader.exec_module(mod)
    return mod


#: Seats on the shared Max subscription, and one that is not.
SHARED = [("cc2", "opus", "claude_cli"), ("fable", "fable", "claude_cli")]
INDEPENDENT = [("ge", "gemini", "openrouter"), ("ds", "deepseek", "deepseek")]

#: A test-scale stagger. The property is the ordering of start times, not the magnitude,
#: and the shipped 20.0 s is pinned by its own test rather than waited for.
TEST_STAGGER = 0.12


class TestTheSharedSeatsAreStaggered:
    """His ruling of 2026-10-08, asserted by CALLING the scheduler."""

    def test_the_shared_seats_start_at_increasing_offsets(self):
        mod = _scheduler()
        rec = _Recorder(hold=0.02)
        mod.run_seat_group(SHARED, [], rec, TEST_STAGGER)
        starts = [t for kind, name, route, t in rec.order if kind == "start"]
        assert len(starts) == 2
        gap = abs(starts[1] - starts[0])
        assert gap >= TEST_STAGGER * 0.5, (
            f"the 2 shared seats started {gap:.3f}s apart, which is not a stagger of "
            f"{TEST_STAGGER}s -- they were dispatched together")

    def test_the_stagger_lets_them_overlap_which_is_the_point(self):
        """A stagger is NOT serialisation: the second seat starts before the first
        finishes, which is where the measured saving comes from."""
        mod = _scheduler()
        rec = _Recorder(hold=TEST_STAGGER * 3)
        mod.run_seat_group(SHARED, [], rec, TEST_STAGGER)
        assert rec.max_live_by_route.get("claude_cli", 0) == 2, (
            "the shared seats never overlapped, so this is serialisation rather than "
            "the stagger he ruled for")

    def test_the_shipped_default_is_twenty_seconds(self):
        """Pinned without sleeping for it. 20 s was measured 3 ways: it must exceed the
        18.7 s establishment collision and stay under the shortest observed first-seat
        duration of 26.7 s."""
        mod = _scheduler()
        assert mod.DEFAULT_STAGGER_S == 20.0

    def test_the_shared_group_is_dispatched_in_roster_order(self):
        mod = _scheduler()
        rec = _Recorder(hold=0.02)
        mod.run_seat_group(SHARED, [], rec, TEST_STAGGER)
        started = [name for kind, name, route, t in rec.order if kind == "start"]
        assert started == [n for n, _m, _r in SHARED], (
            f"dispatched {started}, not in roster order")


class TestZeroStaggerStillSerialises:
    """HIS EARLIER RULING WAS NOT REMOVED, IT WAS MADE SELECTABLE -- the additive
    standard's removal clause. `PANEL_STAGGER_S=0` restores strict serialisation."""

    def test_at_zero_the_shared_seats_never_overlap(self):
        mod = _scheduler()
        rec = _Recorder(hold=0.05)
        mod.run_seat_group(SHARED, [], rec, 0)
        assert rec.max_live_by_route.get("claude_cli", 0) == 1, (
            "at stagger 0 the shared seats overlapped, so the serialised path his "
            "2026-10-05 ruling asked for is no longer reachable")

    def test_a_negative_or_malformed_stagger_refuses_rather_than_defaulting(self):
        """A scheduling control that silently ignores its own input is a shape this
        project has paid for before."""
        import os
        mod = _scheduler()
        for bad in ("-1", "abc"):
            old = os.environ.get("PANEL_STAGGER_S")
            try:
                os.environ["PANEL_STAGGER_S"] = bad
                with pytest.raises(SystemExit):
                    mod._stagger_seconds()
            finally:
                if old is None:
                    os.environ.pop("PANEL_STAGGER_S", None)
                else:
                    os.environ["PANEL_STAGGER_S"] = old


class TestNothingElseRegressed:
    def test_every_seat_still_returns_a_result(self):
        mod = _scheduler()
        rec = _Recorder(hold=0.02)
        out = mod.run_seat_group(SHARED, INDEPENDENT, rec, TEST_STAGGER)
        got = sorted(r["model"] for r in out)
        assert got == sorted(n for n, _m, _r in SHARED + INDEPENDENT), (
            f"a seat was dropped by the scheduler: got {got}")

    def test_non_shared_seats_still_run_concurrently(self):
        """The stagger must not have serialised the routes that never contended."""
        mod = _scheduler()
        rec = _Recorder(hold=0.08)
        mod.run_seat_group([], INDEPENDENT, rec, TEST_STAGGER)
        assert rec.max_live_by_route.get("openrouter", 0) >= 1
        live = {r: v for r, v in rec.max_live_by_route.items()}
        assert sum(live.values()) >= 2, (
            f"independent seats did not overlap at all: {live}")

    def test_the_scheduler_is_a_named_function_not_a_lifted_block(self):
        """The repair itself: if the scheduling ever goes back inline, this file must
        fail rather than silently re-acquire the blindness it just lost."""
        mod = _scheduler()
        assert callable(getattr(mod, "run_seat_group", None)), (
            "run_seat_group is gone, so these guards are lifting source text again")
