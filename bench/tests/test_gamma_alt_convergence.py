"""Tests for the critical-quiescence convergence path in reference_runner_v2.

Originally the γ-alternative path (Item 1A.3, Exp 40). Redesigned by panel
ruling 2026-05-23: γ is REPORTED, NEVER a convergence trigger. The former
γ-threshold trigger is DELETED. Convergence on this path now rests SOLELY on
K consecutive rounds with zero novel CRITICAL (severity >= 0.7) on the
SETTLED/genuine series.

A4 VERIFIER FAIL-SAFE: an UNVERIFIED critical-severity candidate (status
UNCONFIRMED, severity >= 0.7) must NOT silently count as "zero new critical."
When ``unresolved_critical > 0`` the streak does NOT accrue and convergence
is blocked. See ``TestA4VerifierFailSafe`` and
``bench/tests/test_a4_verifier_failsafe.py`` for the registry-level proof.

Earliest round gated by ``cfg.gamma_alt_earliest_round``.
"""

from __future__ import annotations

from bench.reference_runner_v2 import (
    RunnerConfig,
    _check_gamma_alt_convergence,
)


def _default_cfg(**overrides) -> RunnerConfig:
    """Minimal RunnerConfig for tests. Only critical-quiescence fields matter."""
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

    def test_at_earliest_round_evaluates_count(self):
        """round == earliest_round is the first eligible round.

        With the γ-trigger deleted, eligibility is decided purely by the
        zero-critical count tail (here [0,0,0] -> fires). γ is high but
        irrelevant to the decision.
        """
        cfg = _default_cfg(gamma_alt_earliest_round=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=3, gamma=0.50, novel_critical_history=[0, 0, 0, 0], cfg=cfg,
        )
        assert converged is True  # zero-critical tail, not γ
        assert "CRITICAL_QUIESCENCE_CONVERGED" in reason


class TestGammaIsReportedNeverTriggers:
    """γ must NOT trigger convergence (panel ruling 2026-05-23)."""

    def test_high_gamma_does_not_fire_without_zero_critical_tail(self):
        """Former condition 1 (γ >= threshold) is DELETED. A high γ with a
        non-zero critical tail must NOT converge."""
        cfg = _default_cfg(
            gamma_alt_threshold=0.30, gamma_alt_consecutive_zero_crit=3,
        )
        converged, reason = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.95, novel_critical_history=[3, 2, 1], cfg=cfg,
        )
        assert converged is False
        assert "not met" in reason

    def test_gamma_at_or_above_old_threshold_does_not_fire(self):
        cfg = _default_cfg(gamma_alt_threshold=0.30)
        for g in (0.30, 0.461, 1.0):
            converged, _ = _check_gamma_alt_convergence(
                round_idx=5, gamma=g, novel_critical_history=[1, 1, 1], cfg=cfg,
            )
            assert converged is False, f"γ={g} must not trigger convergence"

    def test_gamma_value_reported_in_reason(self):
        """γ appears in the reason string (reported), even though it does
        not affect the decision."""
        cfg = _default_cfg()
        _, reason = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.123, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert "gamma=0.123" in reason
        assert "reported only" in reason

    def test_low_gamma_does_not_block_zero_critical_convergence(self):
        """A low γ must NOT prevent convergence when the critical tail is
        all-zero (γ is not a blocker either)."""
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.001, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert converged is True


class TestZeroNovelCriticalCondition:
    def test_three_consecutive_zeros_fires(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.10, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert converged is True
        assert "consecutive" in reason
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

    def test_late_critical_at_tail_blocks(self):
        """Replay anchor: [3,0,0,0,0,0,1] (terminal) must NOT converge."""
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 1],
            cfg=cfg,
        )
        assert converged is False
        assert "[0, 0, 1]" in reason

    def test_clean_tail_converges(self):
        """Replay anchor: [3,0,0,0,0,0,0] (terminal) must converge."""
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
        )
        assert converged is True
        assert "CRITICAL_QUIESCENCE_CONVERGED" in reason

    def test_short_history_does_not_trigger(self):
        """History shorter than window cannot trigger convergence."""
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


class TestA4VerifierFailSafe:
    """An unverified (UNCONFIRMED) critical candidate must block the count.

    Registry-level proof lives in ``test_a4_verifier_failsafe.py``; here we
    exercise the pure-function contract via the ``unresolved_critical`` arg.
    """

    def test_unresolved_critical_blocks_clean_tail(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        # Tail is all-zero -> would converge, BUT an unverified critical is
        # pending. A4 must block.
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            unresolved_critical=1,
        )
        assert converged is False
        assert "A4 BLOCK" in reason
        assert "HIL review required" in reason

    def test_resolved_then_converges(self):
        """Once the unverified critical is resolved/adjudicated
        (unresolved_critical == 0), convergence proceeds."""
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            unresolved_critical=0,
        )
        assert converged is True

    def test_a4_blocks_before_earliest_is_still_too_early(self):
        """The earliest-round guard precedes A4 (too-early dominates)."""
        cfg = _default_cfg(
            gamma_alt_earliest_round=3, gamma_alt_consecutive_zero_crit=3,
        )
        converged, reason = _check_gamma_alt_convergence(
            round_idx=2,
            gamma=0.20,
            novel_critical_history=[0, 0, 0],
            cfg=cfg,
            unresolved_critical=2,
        )
        assert converged is False
        assert "too early" in reason


class TestReviewCleanGates:
    """Convergence requires review-clean: not contested (c), not churning (d).

    A clean critical tail must not converge while the panel is still
    contesting findings or churning re-derivations.
    """

    def test_contested_blocks_clean_tail(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            contested=2,
        )
        assert converged is False
        assert "contested=2" in reason

    def test_churn_blocks_clean_tail(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            rho_churn=True,
        )
        assert converged is False
        assert "churn" in reason

    def test_clean_and_uncontested_and_no_churn_converges(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            unresolved_critical=0,
            contested=0,
            rho_churn=False,
        )
        assert converged is True

    def test_a4_precedence_over_contested(self):
        """A4 (unverified critical) is reported even alongside contested."""
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            unresolved_critical=1,
            contested=2,
        )
        assert converged is False
        assert "A4 BLOCK" in reason


class TestExp41cAnchor:
    """Non-negotiable: exp41c must converge at round 6 under the new gate.

    Recorded run: settled critical series [3,0,0,0,0,0,0]; at round 6
    gamma=0.2397 (< the deleted 0.30 trigger, so the deletion is inert
    here), zero UNCONFIRMED criticals at check time, zero contested, and
    rho_avg=0.4667 > rho_threshold (not churning).
    """

    def test_exp41c_converges_at_round_6(self):
        cfg = _default_cfg(
            gamma_alt_consecutive_zero_crit=3,
            gamma_alt_earliest_round=3,
            rho_threshold=0.25,
        )
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.2397,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            unresolved_critical=0,
            contested=0,
            rho_churn=False,
        )
        assert converged is True
        assert "CRITICAL_QUIESCENCE_CONVERGED" in reason


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
