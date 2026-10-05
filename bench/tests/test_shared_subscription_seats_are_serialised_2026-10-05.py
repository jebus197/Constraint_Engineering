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
    """Build a callable with the dispatcher's real scheduling block.

    The block is lifted verbatim from the source between its own markers and
    executed, so the test runs the shipped control flow rather than a restatement
    of it. If the block cannot be located the test fails loudly rather than
    silently passing over nothing.
    """
    src = DISPATCHER.read_text(encoding="utf-8")
    start = src.find("        _shared = [(n, m, r) for n, m, r in MODELS")
    end = src.find("results.extend(got if isinstance(got, list) else [got])")
    if start < 0 or end < 0:
        pytest.fail(
            "the scheduling block could not be located in "
            f"{DISPATCHER.name}; this guard is testing nothing")
    block = src[start:end + len("results.extend(got if isinstance(got, list) else [got])")]
    block = "\n".join(line[8:] if line.startswith("        ") else line
                      for line in block.split("\n"))

    def run(models, dispatch):
        import concurrent.futures
        ns = {"MODELS": models, "dispatch": dispatch,
              "concurrent": concurrent, "results": None}
        exec(compile(block, "<scheduling-block>", "exec"), ns)  # noqa: S102
        return ns["results"]
    return run


FREE = [("cc2", "opus", "claude_cli"), ("fable", "fable", "claude_cli")]
MIXED = FREE + [("ge", "gemini", "openrouter"), ("ds", "deepseek", "direct")]


class TestTheSharedSeatsDoNotOverlap:
    def test_two_claude_cli_seats_are_never_in_flight_together(self):
        rec = _Recorder()
        _scheduler()(FREE, rec)
        assert rec.max_live_by_route.get("claude_cli", 0) == 1, (
            f"{rec.max_live_by_route.get('claude_cli')} claude_cli seats were in "
            f"flight at once; they share one subscription")

    def test_every_seat_still_returns_a_result(self):
        rec = _Recorder()
        out = _scheduler()(FREE, rec)
        assert len(out) == len(FREE), (
            f"{len(out)} results for {len(FREE)} seats — serialising must not "
            f"drop a seat")
        assert {r["model"] for r in out} == {"cc2", "fable"}

    def test_the_shared_group_runs_in_roster_order(self):
        rec = _Recorder()
        _scheduler()(FREE, rec)
        starts = [n for kind, n, r, _ in rec.order
                  if kind == "start" and r == "claude_cli"]
        assert starts == ["cc2", "fable"], f"roster order not preserved: {starts}"


class TestOtherRoutesStillOverlap:
    """Additive: serialising one group must not serialise the whole panel."""

    def test_non_shared_seats_still_run_concurrently(self):
        rec = _Recorder(hold=0.12)
        out = _scheduler()(MIXED, rec)
        assert len(out) == len(MIXED)
        assert rec.max_live_by_route.get("claude_cli", 0) == 1
        others = max(rec.max_live_by_route.get("openrouter", 0),
                     rec.max_live_by_route.get("direct", 0))
        assert others >= 1
        total_span = rec.order[-1][3] - rec.order[0][3]
        serial_span = len(MIXED) * 0.12
        assert total_span < serial_span * 0.9, (
            f"the whole panel took {total_span:.3f}s against {serial_span:.3f}s "
            f"fully serial — the independent seats are no longer overlapping")


class TestTheProbeIsNotVacuous:
    def test_a_fully_concurrent_scheduler_would_fail_the_overlap_check(self):
        """Anti-vacuity: the recorder must be able to SEE an overlap."""
        import concurrent.futures
        rec = _Recorder()
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(FREE)) as pool:
            list(pool.map(lambda t: rec(*t), FREE))
        assert rec.max_live_by_route.get("claude_cli", 0) == 2, (
            "the recorder did not observe 2 concurrent seats even under a fully "
            "concurrent pool, so the main assertion could pass for the wrong "
            "reason")

    def test_the_dispatcher_no_longer_pools_the_whole_roster(self):
        src = DISPATCHER.read_text(encoding="utf-8")
        assert not re.search(
            r"ThreadPoolExecutor\(max_workers=len\(MODELS\)\)\s*as pool:\s*\n"
            r"\s*futs = \{pool\.submit\(dispatch,", src), (
            "the original whole-roster pool is back")
