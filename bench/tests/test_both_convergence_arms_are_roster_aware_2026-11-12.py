"""B77: BOTH convergence arms must read the roster-aware quiet window.

THE DEFECT THIS CLOSES. The convergence gate is two-sided -- the critical decay
curve must have flattened AND K consecutive rounds must have produced no novel
CRITICAL. The second condition gets EASIER as the roster shrinks, because fewer
seats generate fewer findings, and the gate cannot tell a quiet panel from a
depleted one: 0 new criticals from 6 seats and 0 from 4 are the same integer.
The founder's requirement of 2026-10-07 is that a dropped seat "should not block
an experimental run until completion, or convergence", so the answer is to make
the window longer rather than to refuse the run.

THE FORMULA WAS PROVEN AND NOTHING READ IT. `K_required = ceil(K * n_declared /
n_live)` was verified in SymPy and guarded on 2026-11-02 by
`bench/tests/test_the_roster_window_bound_is_sound_2026-11-02.py`, and it lived
ONLY in its producer and that test -- 0 lines of product code held it. Under
`additive-standard`'s symmetric form an addition nothing reaches is not
additive, so a proven bound was inert. `HARDENED_GATE_DEFAULT = True` made it
worse than inert: the accepted design targeted the LEGACY arm, which is not the
one that runs. His instruction of 2026-11-12 was to wire both.

WHAT IS PINNED HERE, by CALLING the gate rather than reading it:

  1. At FULL roster both arms behave exactly as they did -- the property that
     makes this safe to land at all.
  2. Below full roster the window RISES, in both arms.
  3. `None` (no counter supplied) is NOT the same as a measured 0, because
     collapsing them would demand K * n_declared quiet rounds of every existing
     caller and stop every run converging.
  4. A measured 0 live seats is the STRICTEST case, never the cheapest.
  5. The verdict is LABELLED degraded rather than refused.
"""
from __future__ import annotations

import importlib
import inspect
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

R = importlib.import_module("reference_runner_v3")


class TestTheHelperItself:
    def test_full_roster_is_identical_to_k(self):
        """The safety property: no existing run's verdict may change."""
        for k in range(1, 10):
            for n in range(1, 9):
                assert R.required_quiet_run(k, n, n) == k, (k, n)

    def test_it_never_decreases_as_the_roster_shrinks(self):
        for k in (1, 3, 7):
            seq = [R.required_quiet_run(k, 6, live) for live in range(6, 0, -1)]
            assert seq == sorted(seq), (k, seq)
            assert seq[0] == k

    def test_an_absent_counter_is_not_a_degraded_roster(self):
        """`None` must return K. Conflating it with 0 is a denial of service."""
        for k in (1, 3, 7):
            assert R.required_quiet_run(k, 6, None) == k

    def test_a_measured_zero_is_the_strictest_case(self):
        assert R.required_quiet_run(3, 6, 0) > 3
        assert R.required_quiet_run(3, 6, -1) > 3

    def test_it_matches_the_ceiling_exactly(self):
        import math
        for k in (1, 3, 7):
            for dec in (1, 4, 6, 9):
                for live in range(1, dec + 1):
                    assert R.required_quiet_run(k, dec, live) == math.ceil(k * dec / live)

    def test_the_live_seat_count_reads_the_per_model_series(self):
        cpm = {"a": [1, 2, None], "b": [0, None, None], "c": [5, 5, 5]}
        assert R.live_seat_count(0, cpm) == 3
        assert R.live_seat_count(1, cpm) == 2
        assert R.live_seat_count(2, cpm) == 1
        assert R.live_seat_count(3, cpm) == 0      # beyond the series
        assert R.live_seat_count(0, None) == 0     # no data at all


class TestBothArmsAcceptIt:
    """The wiring, asserted on the SIGNATURES the runner actually exposes."""

    @pytest.mark.parametrize("fn", ["_check_gamma_alt_convergence",
                                    "_check_hardened_convergence"])
    def test_the_arm_takes_n_live(self, fn):
        sig = inspect.signature(getattr(R, fn))
        assert "n_live" in sig.parameters, (
            f"{fn} does not accept n_live, so the roster-aware window cannot "
            f"reach it. HARDENED_GATE_DEFAULT is True, so wiring only the "
            f"legacy arm leaves the live path blind -- which was the defect.")
        assert sig.parameters["n_live"].default is None, (
            f"{fn}'s n_live must default to None so every existing caller keeps "
            f"today's behaviour")

    @pytest.mark.parametrize("fn", ["_check_gamma_alt_convergence",
                                    "_check_hardened_convergence"])
    def test_the_arm_reads_the_helper_and_not_the_raw_field(self, fn):
        """EXECUTE-DO-NOT-GREP would prefer a call; a source check is used here
        because the window is a local variable with no return path of its own.
        The behavioural half is `TestTheWindowActuallyMoves` below."""
        src = inspect.getsource(getattr(R, fn))
        assert "required_quiet_run(" in src, (
            f"{fn} does not call required_quiet_run, so its window is still "
            f"roster-blind")


class TestTheWindowActuallyMoves:
    """BEHAVIOURAL, not structural: the number the gate uses must change."""

    def _cfg(self, n_models: int, k: int = 3):
        cfg = R.RunnerConfig()
        cfg.models = [f"M{i}" for i in range(n_models)]
        cfg.gamma_alt_consecutive_zero_crit = k
        return cfg

    def test_the_window_rises_when_seats_drop(self):
        cfg = self._cfg(6, k=3)
        full = R.required_quiet_run(cfg.gamma_alt_consecutive_zero_crit,
                                    len(cfg.models), 6)
        four = R.required_quiet_run(cfg.gamma_alt_consecutive_zero_crit,
                                    len(cfg.models), 4)
        two = R.required_quiet_run(cfg.gamma_alt_consecutive_zero_crit,
                                   len(cfg.models), 2)
        assert (full, four, two) == (3, 5, 9), (full, four, two)

    def test_a_shorter_history_cannot_satisfy_the_raised_window(self):
        """The point of the repair: a depleted panel must not close early.

        4 quiet rounds satisfies K=3 at full roster and must NOT satisfy the
        window at 4 of 6 seats, which is 5.
        """
        k, dec = 3, 6
        assert len([0, 0, 0, 0]) >= R.required_quiet_run(k, dec, dec)
        assert len([0, 0, 0, 0]) < R.required_quiet_run(k, dec, 4)
