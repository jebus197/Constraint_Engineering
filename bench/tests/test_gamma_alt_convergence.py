"""Tests for γ-alternative convergence path in reference_runner_v2.

Item 1A.3 remainder from Exp 40 execution plan. Documented in Exp 39
sub-experiment configs as ``pass_condition`` but never implemented in
code until 17 April 2026.

Gate fires when EITHER:
  (1) gamma >= cfg.gamma_alt_threshold, OR
  (2) cfg.gamma_alt_consecutive_zero_crit consecutive rounds
      with zero novel CRITICAL (severity >= 0.7) findings.

Earliest round gated by ``cfg.gamma_alt_earliest_round``.
"""

from __future__ import annotations

import pytest

from bench.reference_runner_v2 import (
    RunnerConfig,
    _check_gamma_alt_convergence,
)


def _default_cfg(**overrides) -> RunnerConfig:
    """Minimal RunnerConfig for tests. Only gamma-alt fields matter here."""
    cfg = RunnerConfig(
        experiment_name="test",
        models=["cc2"],
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


class TestEarliestRound:
    def test_before_earliest_round_returns_false(self):
        cfg = _default_cfg(gamma_alt_earliest_round=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=2, gamma=0.50, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert converged is False
        assert "too early" in reason

    def test_at_earliest_round_evaluates(self):
        """round == earliest_round is the first eligible round."""
        cfg = _default_cfg(gamma_alt_earliest_round=3)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=3, gamma=0.50, novel_critical_history=[0, 0, 0, 0], cfg=cfg,
        )
        assert converged is True  # γ above threshold


class TestGammaThreshold:
    def test_gamma_above_threshold_fires(self):
        cfg = _default_cfg(gamma_alt_threshold=0.30)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.461, novel_critical_history=[3, 2, 1], cfg=cfg,
        )
        assert converged is True
        assert "gamma=0.461" in reason
        assert "GAMMA_ALT_CONVERGED" in reason

    def test_gamma_exactly_at_threshold_fires(self):
        """Boundary case: γ == threshold triggers (per >= semantics)."""
        cfg = _default_cfg(gamma_alt_threshold=0.30)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.30, novel_critical_history=[1, 1, 1], cfg=cfg,
        )
        assert converged is True

    def test_gamma_below_threshold_does_not_fire_on_condition_1(self):
        cfg = _default_cfg(gamma_alt_threshold=0.30)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.299, novel_critical_history=[1, 1, 1], cfg=cfg,
        )
        assert converged is False

    def test_custom_threshold_respected(self):
        cfg = _default_cfg(gamma_alt_threshold=0.45)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.40, novel_critical_history=[1, 1, 1], cfg=cfg,
        )
        assert converged is False
        converged2, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.50, novel_critical_history=[1, 1, 1], cfg=cfg,
        )
        assert converged2 is True


class TestZeroNovelCriticalCondition:
    def test_three_consecutive_zeros_fires(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.10, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert converged is True
        assert "consecutive rounds" in reason
        assert "zero novel CRITICAL" in reason

    def test_three_zeros_at_tail_of_longer_history_fires(self):
        """Only the last `window` entries matter."""
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=7,
            gamma=0.10,
            novel_critical_history=[5, 3, 2, 0, 0, 0],
            cfg=cfg,
        )
        assert converged is True

    def test_non_zero_within_tail_window_blocks(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=7,
            gamma=0.10,
            novel_critical_history=[0, 0, 1, 0, 0],
            cfg=cfg,
        )
        # last 3 are [1, 0, 0]; not all zero
        assert converged is False
        assert "not met" in reason

    def test_short_history_does_not_trigger_condition_2(self):
        """History shorter than window cannot trigger condition 2 alone."""
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.10, novel_critical_history=[0, 0], cfg=cfg,
        )
        assert converged is False

    def test_window_of_one_fires_on_single_zero(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=1)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.10, novel_critical_history=[0], cfg=cfg,
        )
        assert converged is True


class TestOrLogic:
    def test_either_condition_sufficient(self):
        cfg = _default_cfg(
            gamma_alt_threshold=0.30,
            gamma_alt_consecutive_zero_crit=3,
        )
        # Only condition 1
        c1, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.40, novel_critical_history=[5, 3, 2], cfg=cfg,
        )
        assert c1 is True
        # Only condition 2
        c2, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.10, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert c2 is True
        # Both
        c3, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.40, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert c3 is True
        # Neither
        c4, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.10, novel_critical_history=[5, 3, 2], cfg=cfg,
        )
        assert c4 is False


class TestReasonFormatting:
    def test_converged_reason_contains_round_idx(self):
        cfg = _default_cfg()
        _, reason = _check_gamma_alt_convergence(
            round_idx=7, gamma=0.50, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert "round 7" in reason

    def test_not_met_reason_contains_recent_history(self):
        cfg = _default_cfg()
        _, reason = _check_gamma_alt_convergence(
            round_idx=7, gamma=0.10, novel_critical_history=[2, 1, 3], cfg=cfg,
        )
        assert "novel_crit_recent=" in reason
        assert "gamma=0.100" in reason


class TestExp390Replay:
    """Would γ-alt have converged Exp 39-0?

    Post-mortem data: final γ=0.461 at R5. If γ-alt had been active,
    condition 1 would have fired at R5 (0.461 >= 0.30) — or earlier,
    once γ first crossed 0.30. This validates that 39-0 would have
    terminated cleanly instead of hitting wall-clock cap.
    """

    def test_exp390_final_state_converges(self):
        cfg = _default_cfg()
        # From analysis_immune_convergence.md: R5 open_ch=13, gamma=0.461
        converged, reason = _check_gamma_alt_convergence(
            round_idx=5,
            gamma=0.461,
            novel_critical_history=[16, 9, 4, 9, 1, 2],
            cfg=cfg,
        )
        assert converged is True
        assert "0.461" in reason
        assert "0.3" in reason  # threshold mentioned
