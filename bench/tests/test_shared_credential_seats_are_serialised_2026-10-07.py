#!/usr/bin/env python3
"""Seats sharing one credential are STAGGERED in the runner, not serialised.

★ SUPERSEDED AND RE-POINTED 2026-10-19, ON HIS INSTRUCTION, and the file is kept
rather than deleted because the evidence below is still why the mechanism exists.

HIS INSTRUCTION, 2026-10-19: *"Was this ever implemented? Was t implemented just
in panel reviews, or was it implemented in our runners also? If not, it should be
implemented in both, including our simulated and real runner."* And his reason for
rejecting the full lock: *"if you dispatched seats individually it would quickly
become a nonsense anyway. With 5 or 6 models it might take many dozens of hours to
complete. But with 70, 0r 700, or 7000 models participating, as CDSFL is eventually
envisaged to be able to handle, probably experiments would be unlikely to ever
complete."*

WHAT THIS FILE USED TO ASSERT, AND WHY THAT WAS RIGHT AT THE TIME. It required
that 2 shared-credential seats NEVER overlap, which was the runner's behaviour from
2026-10-07. His stagger ruling of 2026-10-08 changed the panel and left the runners
on the lock, so for 11 days 2 guards asserted OPPOSITE properties on 2 modules:
`test_shared_subscription_seats_are_serialised_2026-10-05.py` required the panel's
seats to overlap, and this file required the runner's not to.

THE COMMITTED MEASUREMENT THAT LICENSES THE CHANGE, which the additive standard
requires before a guarded property may be replaced. Over 102 archived rounds where
both free seats answered, `scripts/serialising_the_free_seats_costs_40_percent_
2026-10-08.py` reports median wall clock of 1779.6 s serialised against 984.4 s
staggered, a mean saving of 0.4001 with a bootstrap interval of (0.3851, 0.4147),
and `never_slower_over_the_record` true. The stagger therefore dominates the lock
on wall clock and loses nothing.

WHAT IS NOW ASSERTED: the starts sit a stagger apart AND the dispatches overlap.
Both halves matter. Without the gap the collision the mechanism exists to avoid is
back; without the overlap it is the lock again under a new name.

THE ORIGINAL EVIDENCE, UNCHANGED AND STILL THE REASON THE GATE EXISTS AT ALL:

THE FOUNDER'S VERDICT, 2026-10-06: *"Then if it can be fixed, you almost certainly
should."*

THE EVIDENCE THAT THERE IS SOMETHING TO FIX. On 2026-10-03 a panel round returned 0
characters from BOTH free seats, at 1956.0 and 1956.2 seconds -- 0.2 seconds apart in 2
separate processes, after UNEQUAL work (37 tool calls and 11). Independent failures do
not land 0.2 seconds apart after unequal work; only a cause outside both processes
does, and both seats authenticate against the same Max subscription. The panel was
serialised on 2026-10-05. The RUNNER was not: `run_experiment` dispatches with
`ThreadPoolExecutor(max_workers=len(eligible))` in 2 places, so every seat went out at
once.

WHY IT BECAME URGENT ON 2026-10-07 rather than being a standing nicety. While the
simulated roster resolved to ONE model the concurrency was harmless. Widening the
ladder to 4 distinct CLI models -- done the same day on the founder's ruling -- is what
made the contention reachable in simulation at all. The fix and the thing that made it
necessary landed together.

THIS IS A SCHEDULING CHANGE WITH A STATED REASON, NOT A DEMONSTRATED CURE, and the
panel's own comment says the same of its version: contention explains the matched
failure times and has not been tested by running a panel both ways.

Every test EXECUTES the real `_dispatch_single_model` against a stubbed inner, so what
is measured is the dispatch path the runner uses rather than a description of it.
"""
import pathlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import bench.reference_runner_v3 as R  # noqa: E402


class _MC:
    def __init__(self, label, api):
        self.label, self.api = label, api


def _run(monkeypatch, seats, hold=0.08):
    """Dispatch `seats` concurrently; return each one's (start, end) window."""
    windows = {}
    lock = threading.Lock()

    def _inner(mc, *a, **kw):
        t0 = time.monotonic()
        time.sleep(hold)
        t1 = time.monotonic()
        with lock:
            windows[mc.label] = (t0, t1)
        return ([], None)

    monkeypatch.setattr(R, "_dispatch_single_model_inner", _inner)
    with ThreadPoolExecutor(max_workers=len(seats)) as pool:
        futs = [pool.submit(R._dispatch_single_model, mc, None, "p", "c", "f",
                            1, "pat", "dom", REPO, True) for mc in seats]
        for f in futs:
            f.result()
    return windows


def _overlap(a, b):
    return min(a[1], b[1]) - max(a[0], b[0])


class TestTheSharedGroupIsStaggered:
    """Both halves: the starts sit a gap apart, AND the dispatches overlap."""

    #: THE HOLD MUST EXCEED THE STAGGER OR OVERLAP IS IMPOSSIBLE BY
    #: CONSTRUCTION, which is how the first version of this class failed: it
    #: used `_run`'s default hold of 0.08 s against a 0.30 s stagger, so seat A
    #: had finished before seat B was allowed to start and the overlap
    #: assertion could never have passed whatever the code did. A test that
    #: cannot pass is not a guard.
    STAGGER = 0.15
    HOLD = 0.50

    def _staggered(self, monkeypatch, labels):
        monkeypatch.setattr(R, "_SHARED_STAGGER_S", self.STAGGER)
        R._SHARED_NEXT_START[0] = 0.0
        return _run(monkeypatch, [_MC(n, "claude_cli") for n in labels],
                    hold=self.HOLD)

    def test_two_cli_seats_start_a_stagger_apart(self, monkeypatch):
        w = self._staggered(monkeypatch, ("A", "B"))
        assert len(w) == 2
        gap = abs(w["A"][0] - w["B"][0])
        assert gap >= self.STAGGER * 0.9, (
            f"2 seats on one credential started {gap:.4f}s apart, under the "
            f"{self.STAGGER}s stagger; the collision this exists to avoid is back")

    def test_two_cli_seats_DO_overlap_which_is_the_point(self, monkeypatch):
        w = self._staggered(monkeypatch, ("A", "B"))
        ov = _overlap(w["A"], w["B"])
        assert ov > 0, (
            "the 2 seats did not overlap, so this is the full lock under a new "
            "name and the measured 40.01% of wall clock is still being spent")

    def test_four_cli_seats_each_start_a_stagger_after_the_last(self, monkeypatch):
        """The roster the widened ladder actually produces."""
        w = self._staggered(monkeypatch, ("A", "B", "C", "D"))
        starts = sorted(v[0] for v in w.values())
        gaps = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
        assert all(g >= self.STAGGER * 0.9 for g in gaps), gaps
        #: and the round costs the MAX rather than the SUM: 4 seats held 0.5 s
        #: each finish well inside 4 x 0.5 s once they overlap.
        span = max(v[1] for v in w.values()) - min(v[0] for v in w.values())
        assert span < 4 * self.HOLD, (
            f"4 staggered seats spanned {span:.3f}s, which is the serial cost; "
            f"they are not overlapping")

    def test_at_zero_stagger_it_falls_back_to_no_wait(self, monkeypatch):
        monkeypatch.setattr(R, "_SHARED_STAGGER_S", 0.0)
        R._SHARED_NEXT_START[0] = 0.0
        assert R._claim_shared_start_slot() == 0.0


class TestTheShippedDefaultIsGuarded:
    """A MUTATION ESCAPED AND THIS CLASS IS WHY IT NO LONGER CAN.

    Every timing test above monkeypatches `_SHARED_STAGGER_S` so it can run in
    milliseconds, which means NONE of them can see the shipped default. Setting
    that default to 0.0 left all 8 green: the stagger could have been switched
    off project-wide with nothing to notice, which is the same shape as a flag
    read by nothing. The panel's guard has carried this assertion since
    2026-10-08; the runner's did not.
    """

    #: Both bounds are committed measurements, not preferences.
    #: `scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py` gives
    #: the floor, and `serialising_the_free_seats_costs_40_percent_2026-10-08.py`
    #: the ceiling.
    FLOOR_S = 18.7
    CEILING_S = 26.7

    def test_the_shipped_default_is_twenty_seconds(self):
        assert R._SHARED_STAGGER_S == 20.0, (
            f"the runner's shipped stagger is {R._SHARED_STAGGER_S}, not 20.0; "
            f"the panel ships 20.0 and the 2 must not drift apart")

    def test_the_default_clears_the_measured_collision(self):
        assert R._SHARED_STAGGER_S > self.FLOOR_S, (
            f"a stagger of {R._SHARED_STAGGER_S}s does not clear the {self.FLOOR_S}s "
            f"establishment collision the mechanism exists to avoid -- which is why "
            f"the 3s he suggested was not used")

    def test_the_default_stays_under_the_shortest_first_seat(self):
        assert R._SHARED_STAGGER_S < self.CEILING_S, (
            f"a stagger of {R._SHARED_STAGGER_S}s exceeds the shortest first-seat "
            f"duration of {self.CEILING_S}s, past which staggering can be SLOWER "
            f"than serialising and the saving is lost")

    def test_the_runner_and_the_panel_agree(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_panel", REPO / "bench" / "confer_maths_panel_2026-09-05.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert m.DEFAULT_STAGGER_S == R._SHARED_STAGGER_S, (
            f"panel ships {m.DEFAULT_STAGGER_S}s and the runner ships "
            f"{R._SHARED_STAGGER_S}s; his instruction was that both carry the "
            f"same mechanism, and 2 different values is how they drift")


class TestIndependentRoutesAreNotSlowedDown:
    """A control that serialises everything is an outage, not a control."""

    def test_two_independent_seats_do_overlap(self, monkeypatch):
        w = _run(monkeypatch, [_MC("A", "openrouter"), _MC("B", "deepseek")])
        assert _overlap(w["A"], w["B"]) > 0, (
            "seats on different credentials were serialised; only the shared "
            "group should be, or a mixed roster gets slower for nothing")

    def test_a_cli_seat_does_not_block_an_independent_one(self, monkeypatch):
        w = _run(monkeypatch, [_MC("CLI", "claude_cli"), _MC("HTTP", "openrouter")])
        assert _overlap(w["CLI"], w["HTTP"]) > 0, (
            "an independent route waited on the shared-credential lock")


class TestTheProbeIsNotVacuous:
    def test_without_the_lock_they_would_overlap(self, monkeypatch):
        """ANTI-VACUITY. If concurrent dispatch did not overlap anyway, the
        serialisation tests would pass on nothing."""
        w = _run(monkeypatch, [_MC("A", "openrouter"), _MC("B", "openrouter")])
        assert _overlap(w["A"], w["B"]) > 0, (
            "2 concurrently submitted seats did not overlap even unserialised, so "
            "this file cannot tell serialisation from a slow machine")

    def test_the_route_set_is_not_empty(self):
        assert R._SHARED_CREDENTIAL_ROUTES, (
            "no route is marked as sharing a credential, so the lock guards nothing")
        assert "claude_cli" in R._SHARED_CREDENTIAL_ROUTES
