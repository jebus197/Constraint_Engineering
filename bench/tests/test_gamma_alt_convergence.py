"""Tests for the critical-quiescence convergence path in reference_runner_v3.

Originally the γ-alternative path (Item 1A.3, Exp 40). The convergence gate is
now a TWO-SIDED GATE (founder ruling 2026-06-10): convergence requires BOTH
  (1) gamma_critical >= cfg.gamma_alt_threshold (0.30) — the critical decay
      curve has flattened (γ is an ACTIVE convergence condition, load-bearing,
      NOT merely "reported"); AND
  (2) K consecutive rounds with zero novel CRITICAL (severity >= 0.7) on the
      SETTLED/genuine series — the strict threshold-free endpoint.
Both are sides of the same diminishing-returns measure; they naturally agree
(verified: exp41c gamma_critical=1.0 and exp42=0.69 both clear 0.30, while the
binding constraint is the count). The legacy ``gamma`` parameter (the
all-findings slope) is NOT in the condition — only ``gamma_critical`` is — and
is accepted purely for backward compatibility. The active two-sided behaviour
is also pinned in ``bench/tests/test_two_sided_gate.py``.

A4 VERIFIER FAIL-SAFE: an UNVERIFIED critical-severity candidate (status
UNCONFIRMED, severity >= 0.7) must NOT silently count as "zero new critical."
When ``unresolved_critical > 0`` the streak does NOT accrue and convergence
is blocked. See ``TestA4VerifierFailSafe`` and
``bench/tests/test_a4_verifier_failsafe.py`` for the registry-level proof.

Earliest round gated by ``cfg.gamma_alt_earliest_round``.
"""

from __future__ import annotations

from bench.reference_runner_v3 import (
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


class TestLegacyGammaParamIsInert:
    """The LEGACY ``gamma`` parameter (all-findings slope) is neither a trigger
    nor a blocker — only ``gamma_critical`` is an active condition (two-sided
    gate). These cases pass only the legacy ``gamma`` and leave ``gamma_critical``
    at its default, proving the legacy param cannot drive the decision either
    way. The ACTIVE gamma_critical behaviour is pinned in
    ``TestGammaCriticalIsActiveCondition`` below and in ``test_two_sided_gate.py``."""

    def test_high_legacy_gamma_does_not_fire_without_zero_critical_tail(self):
        """A high legacy γ with a non-zero critical tail must NOT converge: the
        count side is unmet."""
        cfg = _default_cfg(
            gamma_alt_threshold=0.30, gamma_alt_consecutive_zero_crit=3,
        )
        converged, reason = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.95, novel_critical_history=[3, 2, 1], cfg=cfg,
        )
        assert converged is False
        assert "not met" in reason

    def test_legacy_gamma_does_not_substitute_for_the_count(self):
        """The legacy γ never substitutes for the count: a non-zero tail blocks
        regardless of the legacy γ value."""
        cfg = _default_cfg(gamma_alt_threshold=0.30)
        for g in (0.30, 0.461, 1.0):
            converged, _ = _check_gamma_alt_convergence(
                round_idx=5, gamma=g, novel_critical_history=[1, 1, 1], cfg=cfg,
            )
            assert converged is False, f"legacy γ={g} must not trigger convergence"

    def test_gamma_critical_value_reported_in_reason(self):
        """The ACTIVE gamma_critical appears in the reason string."""
        cfg = _default_cfg()
        _, reason = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.123, novel_critical_history=[0, 0, 0], cfg=cfg,
            gamma_critical=0.55,
        )
        assert "gamma_critical=0.550" in reason

    def test_low_legacy_gamma_does_not_block_zero_critical_convergence(self):
        """A low legacy γ must NOT prevent convergence when the critical tail is
        all-zero and gamma_critical (default 1.0) clears the threshold."""
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, _ = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.001, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert converged is True


class TestGammaCriticalIsActiveCondition:
    """gamma_critical is an ACTIVE, load-bearing condition (two-sided gate,
    founder ruling 2026-06-10): below threshold it BLOCKS convergence even when
    the zero-critical count is satisfied; above threshold with a clean count it
    fires. This is the test-level embodiment of "gamma is load-bearing — do not
    demote it." The full two-sided matrix is in test_two_sided_gate.py."""

    def test_gamma_critical_below_threshold_blocks_despite_zero_tail(self):
        """The directive's guard: a low gamma blocks even on a clean count.

        The history carries a REAL curve (cumulative critical > 0), which is what
        this must pin. A history of all zeros is a different situation — there is
        no curve to fit and gamma is undefined rather than low — and is covered
        separately in test_vacuous_gamma_curve.py.
        """
        cfg = _default_cfg(gamma_alt_threshold=0.30)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6, gamma=0.10, novel_critical_history=[2, 1, 0, 0, 0], cfg=cfg,
            gamma_critical=0.20,  # below 0.30 — decay curve not yet flattened
            total_findings=15,
        )
        assert converged is False
        assert "gamma_critical" in reason
        assert "VACUOUS" not in reason, (
            "a real decay curve exists here; the vacuous-curve path must not apply")

    def test_low_gamma_still_blocks_when_the_panel_returned_nothing(self):
        """All-zero history AND no findings is a dead panel, not an exhausted space.

        It must still block, and the reason must still name gamma_critical so this
        class's guarantee — gamma is an active condition — remains visible.
        """
        cfg = _default_cfg(gamma_alt_threshold=0.30)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6, gamma=0.10, novel_critical_history=[0, 0, 0], cfg=cfg,
            gamma_critical=0.20, total_findings=0,
        )
        assert converged is False
        assert "gamma_critical" in reason
        assert "dead panel" in reason.lower()

    def test_gamma_critical_above_threshold_with_zero_tail_converges(self):
        cfg = _default_cfg(gamma_alt_threshold=0.30)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6, gamma=0.10, novel_critical_history=[0, 0, 0], cfg=cfg,
            gamma_critical=0.45,  # >= 0.30 — curve flattened, count clean
        )
        assert converged is True
        assert "CRITICAL_QUIESCENCE_CONVERGED" in reason


class TestZeroNovelCriticalCondition:
    def test_three_consecutive_zeros_fires(self):
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=5, gamma=0.10, novel_critical_history=[0, 0, 0], cfg=cfg,
        )
        assert converged is True
        assert "consecutive" in reason
        assert "zero-new-critical" in reason

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

    def test_churn_no_longer_blocks_a_clean_tail(self):
        """FOUNDER RULING 2026-08-29: rho is contributory, not a veto.

        This test previously asserted the opposite -- that churn BLOCKS a clean
        critical tail. It was an early return, so it fired before the two-sided
        gate was evaluated at all: a run could satisfy both halves of the gate
        and still be refused for the very quiescence the gate exists to certify.
        The founder's words: "It is a contributory condition of convergence, not
        a veto. It was never intended as this."

        Inverted rather than deleted, so the change of rule is visible in the
        test that used to encode the old one.
        """
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        with_churn, reason_churn = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            unresolved_critical=0,
            contested=0,
            rho_churn=True,
        )
        without_churn, _ = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 0, 0, 0, 0, 0, 0],
            cfg=cfg,
            unresolved_critical=0,
            contested=0,
            rho_churn=False,
        )
        assert with_churn == without_churn, (
            "churn changed the verdict, so it is still acting as a veto")
        assert "churn" in reason_churn, (
            "churn stopped blocking but also stopped being REPORTED; it must stay "
            "visible on the verdict, or the signal is merely hidden rather than demoted")
        assert "contributory" in reason_churn or "not blocking" in reason_churn

    def test_churn_cannot_manufacture_a_convergence_on_its_own(self):
        """The guard that replaces the veto.

        Demoting churn is only safe because the TWO-SIDED GATE is the real
        guard: convergence still needs gamma_critical above threshold AND K
        consecutive zero-new-critical rounds. A churning panel whose critical
        findings are still arriving must not converge.
        """
        cfg = _default_cfg(gamma_alt_consecutive_zero_crit=3)
        converged, reason = _check_gamma_alt_convergence(
            round_idx=6,
            gamma=0.20,
            novel_critical_history=[3, 2, 1, 2, 1, 1, 2],   # critical still arriving
            cfg=cfg,
            unresolved_critical=0,
            contested=0,
            rho_churn=True,
        )
        assert converged is False, (
            "a run still producing critical findings converged; the two-sided gate "
            "is not holding, and it is the only thing left holding")

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

    Recorded run: settled critical series [3,0,0,0,0,0,0]; at round 6 the
    critical decay curve is flat, so gamma_critical = 1.0 (>= the 0.30
    threshold) AND the zero-critical count is satisfied — both sides of the
    two-sided gate agree. (The ALL-FINDINGS gamma was 0.2397, below 0.30, but
    that legacy series is NOT the gate input; gamma_critical on the CRITICAL
    series is — verified via _estimate_gamma([3,0,0,0,0,0,0]) == 1.0.) Zero
    UNCONFIRMED criticals at check time, zero contested, and rho_avg=0.4667 >
    rho_threshold (not churning).
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
            gamma_critical=1.0,  # real value: critical series [3,0,...] is flat
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
            gamma_critical=0.10,
        )
        assert "novel_crit_recent=" in reason
        assert "gamma_critical=0.100" in reason
