"""Tests for Exp 40 1D.3 — per-model rho tracking with targeted ITC.

Acceptance from the plan:
- Unit test with two synthetic models of different rho decay rates
  confirms ITC targets each correctly.

The load-bearing contract: ``_itc_adapt`` uses the supplied
``rho_rolling_avg`` to decide whether DEGRADATION should be suppressed or
should trigger a restart_fresh adaptation.

The 1D.3 change moves rho from a panel-pooled scalar to a per-model
rolling average so that a degraded model is not shielded by the healthy
panel average, and a healthy model is not restarted because of panel-wide
churn.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

import pytest

from bench.reference_runner_v2 import (
    ITC_DEGRADATION,
    RunnerConfig,
    _compute_rho,
    _itc_adapt,
    _itc_model_state,
)


@pytest.fixture(autouse=True)
def _reset_itc_state():
    """Isolate each test from global ITC state."""
    _itc_model_state.clear()
    yield
    _itc_model_state.clear()


@pytest.fixture
def cfg() -> RunnerConfig:
    # rho_threshold 0.25 is the default from RunnerConfig; make it explicit
    # here so the test is self-contained.
    return RunnerConfig(
        models=["CC2", "Gemini"],
        max_rounds=8,
        rho_threshold=0.25,
        rho_rolling_window=3,
        rho_earliest_round=2,
    )


class TestPerModelRhoComputation:
    """Verify the rho-per-model scalar comes out right for synthetic data.

    These are direct ``_compute_rho`` invocations on per-model lists,
    matching how the runner feeds per-model arrays to the helper.
    """

    def test_healthy_model_stays_above_threshold(self, cfg):
        # Novelty trending flat at ~60% — a productive model.
        novelty = [6, 7, 6, 6]
        raw = [10, 10, 10, 10]
        _, rho_avg, churn = _compute_rho(novelty, raw, cfg)
        assert rho_avg > cfg.rho_threshold, (
            f"healthy model rho_avg={rho_avg} must exceed threshold"
        )
        assert not churn, "healthy model must not flag churn"

    def test_collapsed_model_falls_below_threshold(self, cfg):
        # Decaying novelty: 60% → 30% → 10% → 5%. By round 4 the
        # rolling-3 window should drop below 0.25.
        novelty = [6, 3, 1, 0]
        raw = [10, 10, 10, 10]
        _, rho_avg, churn = _compute_rho(novelty, raw, cfg)
        assert rho_avg < cfg.rho_threshold, (
            f"collapsed model rho_avg={rho_avg} must fall below threshold"
        )
        assert churn, "collapsed model must flag churn"

    def test_two_models_diverge(self, cfg):
        """Same panel-wide pool, two different per-model histories → two
        different rho_avg values. This is the core claim of 1D.3."""
        healthy_n, healthy_r = [6, 7, 6, 6], [10, 10, 10, 10]
        sick_n, sick_r = [5, 2, 1, 0], [10, 10, 10, 10]
        _, rho_healthy, churn_h = _compute_rho(healthy_n, healthy_r, cfg)
        _, rho_sick, churn_s = _compute_rho(sick_n, sick_r, cfg)
        assert rho_healthy > rho_sick
        assert not churn_h
        assert churn_s


class TestItcAdaptTargetsPerModelRho:
    """``_itc_adapt`` receives ``rho_rolling_avg`` and acts on it.

    The load-bearing contract for 1D.3: when the per-model rho is passed,
    DEGRADATION suppression fires for the healthy model and restart_fresh
    fires for the sick model — even though both are in the same panel.
    """

    def test_healthy_model_degradation_is_suppressed(self, cfg):
        # rho_avg above threshold → DEGRADATION suppressed, adaptation cleared.
        _itc_adapt(
            "ModelH", ITC_DEGRADATION, round_idx=5,
            rho_rolling_avg=0.55,   # well above 0.25 threshold
            rho_threshold=cfg.rho_threshold,
        )
        assert _itc_model_state["ModelH"]["adaptation"] is None, (
            "healthy rho must suppress ITC adaptation"
        )

    def test_sick_model_degradation_triggers_change_focus_then_restart(self, cfg):
        # rho_avg below threshold → ITC fires (change_focus, then restart_fresh
        # on the 3rd consecutive failure).
        # One call at low rho: change_focus (consecutive=1 < 2)
        _itc_adapt(
            "ModelS", ITC_DEGRADATION, round_idx=5,
            rho_rolling_avg=0.05,
            rho_threshold=cfg.rho_threshold,
        )
        assert _itc_model_state["ModelS"]["adaptation"] == "change_focus"

        # Second consecutive failure → restart_fresh
        _itc_adapt(
            "ModelS", ITC_DEGRADATION, round_idx=6,
            rho_rolling_avg=0.05,
            rho_threshold=cfg.rho_threshold,
        )
        assert _itc_model_state["ModelS"]["adaptation"] == "restart_fresh"

    def test_same_round_two_models_diverge_in_adaptation(self, cfg):
        """The core claim: with per-model rho routing, one model in the
        panel can be suppressed while another is adapted — in the SAME
        round."""
        _itc_adapt(
            "ModelH", ITC_DEGRADATION, round_idx=5,
            rho_rolling_avg=0.60,   # healthy
            rho_threshold=cfg.rho_threshold,
        )
        _itc_adapt(
            "ModelS", ITC_DEGRADATION, round_idx=5,
            rho_rolling_avg=0.05,   # collapsed
            rho_threshold=cfg.rho_threshold,
        )
        assert _itc_model_state["ModelH"]["adaptation"] is None
        assert _itc_model_state["ModelS"]["adaptation"] == "change_focus"


class TestPooledRhoMasksSickModel:
    """Regression guard: if we were still using pooled rho, a sick model
    would be protected by the healthy panel-average. This test encodes
    that failure mode so the fix cannot silently regress.
    """

    def test_pooled_rho_would_mask_one_sick_model(self, cfg):
        """With pooled inputs (healthy + sick combined), rho_avg stays
        above threshold even though one model is collapsed — exactly the
        pre-1D.3 blindspot."""
        pooled_novel = [6 + 5, 7 + 2, 6 + 1, 6 + 0]   # healthy + sick
        pooled_raw   = [10 + 10, 10 + 10, 10 + 10, 10 + 10]
        _, rho_pooled, churn = _compute_rho(pooled_novel, pooled_raw, cfg)
        # Panel-average is still ~0.33, above threshold — the sick model
        # is masked. This is the bug 1D.3 fixes.
        assert rho_pooled > cfg.rho_threshold, (
            "pooled rho masks sick model — this is exactly why per-model "
            "rho is load-bearing"
        )
        assert not churn
        # But the sick-only rho is clearly below threshold:
        _, rho_sick, churn_s = _compute_rho(
            [5, 2, 1, 0], [10, 10, 10, 10], cfg,
        )
        assert rho_sick < cfg.rho_threshold
        assert churn_s


class TestRhoHistoryZeroFill:
    """The runner zero-fills per-model history so arrays stay aligned.

    This test verifies the invariant that when a model produces no findings
    in a round, its per-model novel count is 0, not a gap."""

    def test_zero_novelty_contributes_zero_to_rho(self, cfg):
        # Silent round (novel=0, raw=0) should not crash, and should drag
        # the rolling average DOWN, not freeze it.
        novelty = [5, 0, 0, 0]
        raw = [10, 0, 0, 0]  # model produced nothing after round 0
        _, rho_avg, churn = _compute_rho(novelty, raw, cfg)
        # rho for rounds 2-4 is 0 (no raw) → rho_avg falls toward zero.
        assert rho_avg < cfg.rho_threshold
        assert churn
