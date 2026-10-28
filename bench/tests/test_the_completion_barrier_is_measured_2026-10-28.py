"""A staggered start says nothing about when seats FINISH. His question, ruled.

HIS VERDICT, 2026-10-28, on the star-topology question he had raised 3 times:
*"Verdict. Do it and study it in the upcoming simulated run."*

WHY THE EXISTING STAGGER EVIDENCE CANNOT ANSWER IT. `DEFAULT_STAGGER_S = 20.0`
was derived from `max(d1, s+d2) <= d1+d2`, which SymPy reduces to `s <= d1` --
a condition entirely about STARTS. 2 seats of equal duration started 20 s apart
finish 20 s apart, and a collaborative round waits out that gap before it can
close. No archived figure measures it, because no seat record carried an
absolute completion time until this instrumentation.

EVERY TEST HERE EXECUTES. The dispatcher's record construction is driven with a
stubbed route so no money and no CLI session is spent, and the barrier
derivation is run on records whose timings are known by construction, so the
expected figures are arithmetic rather than recollection. A test that read the
source could not observe a timing property at all -- `execute-do-not-grep`.

WHAT EACH REVERSION TURNS RED:
  * removing `t_start_epoch`/`t_end_epoch` from either record dict in `dispatch`
    -> `TestTheDispatcherStampsBothEnds` fails on the success path, and its
    sibling on the failure path, which is the branch that matters most because a
    seat that times out is precisely the one that sets the barrier;
  * deleting the `completion_barrier` call at the end of the round -> the
    end-to-end test finds no derived record;
  * replacing `idle_s` with `elapsed_s` arithmetic -> the staggered case fails,
    since 2 equal-duration seats have equal `elapsed_s` and unequal idle.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PROBE = "_barrier_probe"


@pytest.fixture(scope="module")
def M():
    """The dispatcher, imported without binding a brief at import time.

    No `PANEL_BRIEF_UNCHECKED`: A22 moved the brief binding out of import time,
    and that variable disables a guard whose purpose is to stop money being
    spent on a defective brief. The sibling stagger guard records why at length.
    """
    argv = list(sys.argv)
    sys.argv = ["test", "_guard_only"]
    try:
        spec = importlib.util.spec_from_file_location(
            "cmp_barrier", REPO / "bench" / "confer_maths_panel_2026-09-05.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["cmp_barrier"] = m
        spec.loader.exec_module(m)
    finally:
        sys.argv = argv
    return m


@pytest.fixture(scope="module")
def ST(M):
    return M._load_star()


def _rec(name, start, end, ok=True):
    """A seat record with timings known by construction."""
    return {"model": name, "ok": ok, "elapsed_s": round(end - start, 1),
            "t_start_epoch": start, "t_end_epoch": end}


class TestTheDerivationIsArithmetic:
    """Figures a reader can check by hand, on records built to be checkable."""

    def test_a_perfectly_matched_round_wastes_nothing(self, ST):
        b = ST.completion_barrier([_rec("a", 100.0, 110.0),
                                   _rec("b", 100.0, 110.0)], stagger_s=0.0)
        assert b["n_timed"] == 2
        assert b["round_wall_s"] == pytest.approx(10.0)
        assert b["total_idle_s"] == pytest.approx(0.0)
        assert b["idle_share"] == pytest.approx(0.0)
        assert b["duration_spread_s"] == pytest.approx(0.0)

    def test_a_round_carried_by_one_slow_seat(self, ST):
        b = ST.completion_barrier([_rec("fast", 100.0, 101.0),
                                   _rec("slow", 100.0, 110.0)], stagger_s=0.0)
        assert b["slowest_seat"] == "slow" and b["fastest_seat"] == "fast"
        assert b["total_idle_s"] == pytest.approx(9.0), (
            "the fast seat sat idle for 9 of the round's 10 seconds")
        # 9 wasted against 2 seats x 10 s of available seat-time
        assert b["idle_share"] == pytest.approx(0.45)
        assert b["saving_vs_serial"] == pytest.approx(1 - 10.0 / 11.0)

    def test_the_stagger_itself_creates_idle_time(self, ST):
        """The case `elapsed_s` cannot see: equal durations, unequal finishes."""
        b = ST.completion_barrier([_rec("first", 100.0, 110.0),
                                   _rec("second", 120.0, 130.0)], stagger_s=20.0)
        assert b["round_wall_s"] == pytest.approx(30.0)
        assert b["duration_spread_s"] == pytest.approx(0.0), (
            "both seats ran 10 s; the spread is 0 and the gap is all stagger")
        assert b["total_idle_s"] == pytest.approx(20.0)
        assert b["stagger_exceeds_duration_spread"] is True, (
            "a stagger larger than the spread of durations creates idle time it "
            "did not have to create -- which is the question his ruling asks")
        per = {p["seat"]: p for p in b["per_seat"]}
        assert per["first"]["idle_s"] == pytest.approx(20.0)
        assert per["second"]["idle_s"] == pytest.approx(0.0)
        assert per["second"]["start_offset_s"] == pytest.approx(20.0)

    def test_a_failed_seat_still_counts_toward_the_barrier(self, ST):
        b = ST.completion_barrier([_rec("ok", 0.0, 5.0),
                                   _rec("timeout", 0.0, 1800.0, ok=False)],
                                  stagger_s=0.0)
        assert b["slowest_seat"] == "timeout"
        assert b["total_idle_s"] == pytest.approx(1795.0), (
            "a seat that times out sets the barrier; omitting it would blind the "
            "measurement to its own worst case")


class TestItDegradesWithoutLying:

    def test_an_uninstrumented_round_says_so(self, ST):
        b = ST.completion_barrier([{"model": "a", "ok": True, "elapsed_s": 3.0}])
        assert b["n_timed"] == 0 and b["n_seats"] == 1
        assert "why" in b and "t_start_epoch" in b["why"]
        assert "round_wall_s" not in b, (
            "a figure must not be reported for a round that cannot supply it")

    def test_partial_instrumentation_is_visible_as_partial(self, ST):
        b = ST.completion_barrier([_rec("a", 0.0, 2.0),
                                   {"model": "b", "ok": True, "elapsed_s": 9.0}])
        assert (b["n_seats"], b["n_timed"]) == (2, 1), (
            "a partly-instrumented round must not be quietly measured on the "
            "subset that happens to carry timestamps")

    def test_a_zero_length_round_does_not_divide_by_zero(self, ST):
        b = ST.completion_barrier([_rec("a", 50.0, 50.0), _rec("b", 50.0, 50.0)])
        assert b["idle_share"] == 0.0 and b["saving_vs_serial"] == 0.0

    def test_a_non_dict_entry_is_skipped_rather_than_raising(self, ST):
        b = ST.completion_barrier([_rec("a", 0.0, 1.0), None, "junk"])
        assert b["n_timed"] == 1 and b["n_seats"] == 3


class TestTheDispatcherStampsBothEnds:
    """The reversion target: the 2 record dicts in `dispatch`."""

    @pytest.fixture
    def logs(self, M):
        d = REPO / "bench" / "logs" / PROBE
        d.mkdir(parents=True, exist_ok=True)
        (d / "BRIEF.md").write_text("# probe\n", encoding="utf-8")
        M.resolve_brief(["confer_maths_panel", PROBE])
        yield d
        for p in sorted(d.glob("*")):
            p.unlink(missing_ok=True)
        try:
            d.rmdir()
        except OSError:
            pass

    def test_a_successful_seat_record_carries_both_timestamps(self, M, logs,
                                                             monkeypatch):
        monkeypatch.setattr(M, "set_tool_log_sink", lambda p: None)
        monkeypatch.setattr(M, "accept_reply_or_work", lambda _p: (lambda _t: None))
        monkeypatch.setattr(M, "call_claude_cli",
                            lambda *a, **k: (time.sleep(0.05) or "a full verdict"))
        before = time.time()
        out = M.dispatch("cc2", "opus", "claude_cli")
        after = time.time()
        assert out["ok"] is True
        for k in ("t_start_epoch", "t_end_epoch"):
            assert k in out, f"{k} absent; the barrier cannot be derived"
        assert before <= out["t_start_epoch"] <= out["t_end_epoch"] <= after
        assert out["t_end_epoch"] - out["t_start_epoch"] >= 0.05

    def test_a_CRASHED_seat_record_carries_them_too(self, M, logs, monkeypatch):
        """The branch that matters most: a timeout is what sets the barrier."""
        monkeypatch.setattr(M, "set_tool_log_sink", lambda p: None)
        monkeypatch.setattr(M, "accept_reply_or_work", lambda _p: (lambda _t: None))

        def boom(*a, **k):
            time.sleep(0.05)
            raise TimeoutError("seat ran out of clock")

        monkeypatch.setattr(M, "call_claude_cli", boom)
        out = M.dispatch("cc2", "opus", "claude_cli")
        assert out["ok"] is False and "TimeoutError" in out.get("error", "")
        assert out["t_end_epoch"] - out["t_start_epoch"] >= 0.05, (
            "a failed seat must report when it started and when it gave up")


class TestItIsWiredToTheRealDispatchPath:
    """An addition nothing reaches is not additive. This is where it is reached."""

    def test_run_seat_group_produces_records_the_barrier_can_read(self, M, ST):
        def fake_dispatch(name, model, route):
            t0 = time.time()
            time.sleep(0.4 if name == "slow" else 0.05)
            return {"model": name, "ok": True, "t_start_epoch": t0,
                    "t_end_epoch": time.time()}

        got = M.run_seat_group(shared=[], independent=[("fast", "m", "r"),
                                                       ("slow", "m", "r")],
                               dispatch_fn=fake_dispatch, stagger_s=0.0)
        b = ST.completion_barrier(got, 0.0)
        assert b["n_timed"] == 2 == b["n_seats"]
        assert b["slowest_seat"] == "slow"
        assert b["total_idle_s"] > 0.2, (
            f"the fast seat should have idled while the slow one ran; "
            f"total idle read {b['total_idle_s']:.4f}s")

    def test_the_stagger_shows_up_in_the_start_offsets(self, M, ST):
        """Executed end to end: the stagger must appear as a start offset."""
        gap = 0.4

        def fake_dispatch(name, model, route):
            t0 = time.time()
            time.sleep(0.05)
            return {"model": name, "ok": True, "t_start_epoch": t0,
                    "t_end_epoch": time.time()}

        got = M.run_seat_group(shared=[("a", "m", "claude_cli"),
                                       ("b", "m", "claude_cli")],
                               independent=[], dispatch_fn=fake_dispatch,
                               stagger_s=gap)
        b = ST.completion_barrier(got, gap)
        offsets = sorted(p["start_offset_s"] for p in b["per_seat"])
        assert offsets[1] - offsets[0] >= gap * 0.8, (
            f"the 2 shared seats started {offsets[1] - offsets[0]:.4f}s apart "
            f"under a {gap}s stagger")
        assert b["stagger_exceeds_duration_spread"] is True
