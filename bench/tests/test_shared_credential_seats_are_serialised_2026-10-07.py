#!/usr/bin/env python3
"""Seats sharing one credential are dispatched one at a time, in the runner too.

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


class TestTheSharedGroupIsSerialised:
    def test_two_cli_seats_do_not_overlap(self, monkeypatch):
        w = _run(monkeypatch, [_MC("A", "claude_cli"), _MC("B", "claude_cli")])
        assert len(w) == 2
        ov = _overlap(w["A"], w["B"])
        assert ov <= 0, (
            f"2 seats sharing one credential overlapped by {ov:.4f}s; they must be "
            f"dispatched one at a time")

    def test_four_cli_seats_do_not_overlap(self, monkeypatch):
        """The roster the widened ladder actually produces."""
        seats = [_MC(n, "claude_cli") for n in ("A", "B", "C", "D")]
        w = _run(monkeypatch, seats)
        pairs = [(x, y) for i, x in enumerate(w) for y in list(w)[i + 1:]]
        bad = [(x, y, _overlap(w[x], w[y])) for x, y in pairs
               if _overlap(w[x], w[y]) > 0]
        assert not bad, f"overlapping dispatches on a shared credential: {bad}"


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
