"""The two-sided gate must not confuse "no curve" with "a flat curve".

GAMMA REMAINS AN ACTIVE, LOAD-BEARING CONVERGENCE CONDITION. Nothing here demotes
it. What is narrowed is the ESTIMATOR'S DOMAIN.

_estimate_gamma fits a Duane decay to the cumulative critical series. Two opposite
situations both drive it to ~0.0:

    [0, 0, 0, 0, 0, 0]   no critical was ever found — there is no curve to fit
    [2, 2, 2, 2, 2, 2]   criticals arriving at a constant rate — no decay at all

The first is the best possible outcome and the second is the worst. Comparing an
undefined estimate against a threshold as though it were a measurement means a
panel that reviewed a genuinely clean document perfectly could never converge: it
would burn its full round budget, report non-convergence, and halt the arc on a
document with nothing in it. That was found pre-launch, on the zero-plant control
built for Exp 53, whose entire purpose is to be clean.

Two guards keep the narrowing honest, and both are pinned below:
  * cumulative critical over the WHOLE history must be zero, so a constant-rate
    series stays blocked — that is the case this must never be confused with;
  * the panel must have returned findings of SOME severity, so a clean target is
    distinguishable from a dead panel or a severity classifier that never fires.

Verified inert against every completed run at the time of the change (Exp 44-49
carry 34, 12, 12, 44, 32 and 31 critical findings respectively, so the branch
cannot fire on any of them).
"""
from __future__ import annotations

import os
import sys

import pytest

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from bench.reference_runner_v2 import (  # noqa: E402
    RunnerConfig, _check_gamma_alt_convergence, _estimate_gamma,
)


def _cfg(**over):
    base = {"experiment_name": "t", "models": ["CC2"], "test_article": "x.md",
            "gamma_alt_threshold": 0.30, "gamma_alt_consecutive_zero_crit": 3,
            "gamma_alt_earliest_round": 3}
    base.update(over)
    return RunnerConfig.from_dict(base)


def _check(series, total_findings, round_idx=5, cfg=None):
    cfg = cfg or _cfg()
    g = _estimate_gamma(series, cfg.min_rounds_for_gamma)
    return _check_gamma_alt_convergence(round_idx, g, series, cfg,
                                        gamma_critical=g,
                                        total_findings=total_findings) + (g,)


class TestTheDegeneracyIsReal:
    def test_both_opposite_series_drive_the_estimator_to_zero(self):
        """The premise. If this ever stops holding, the branch can go."""
        cfg = _cfg()
        clean = _estimate_gamma([0] * 6, cfg.min_rounds_for_gamma)
        constant = _estimate_gamma([2] * 6, cfg.min_rounds_for_gamma)
        assert clean == pytest.approx(0.0, abs=1e-9)
        assert constant == pytest.approx(0.0, abs=1e-9)
        assert clean < cfg.gamma_alt_threshold and constant < cfg.gamma_alt_threshold


class TestVacuousCurveConverges:
    def test_clean_target_with_a_working_panel_converges(self):
        conv, reason, _ = _check([0] * 6, total_findings=18)
        assert conv is True
        assert "VACUOUS CURVE" in reason

    def test_the_reason_carries_both_counts_for_a_human_to_judge(self):
        _, reason, _ = _check([0] * 6, total_findings=18)
        assert "18" in reason, "the finding count must be visible in the verdict"
        assert "REVIEW THIS RUN" in reason, (
            "a clean target and a broken severity classifier look alike here; "
            "the run must say so rather than converge quietly")

    def test_a_single_finding_is_enough_to_show_the_panel_worked(self):
        conv, _, _ = _check([0] * 6, total_findings=1)
        assert conv is True


class TestTheGuardsHold:
    def test_dead_panel_is_refused(self):
        conv, reason, _ = _check([0] * 6, total_findings=0)
        assert conv is False
        assert "dead panel" in reason.lower()

    @pytest.mark.parametrize("series", [[2] * 6, [1] * 6, [5, 5, 5, 5, 5, 5]])
    def test_constant_arrival_rate_stays_blocked(self, series):
        """The case that must never be confused with an empty series."""
        conv, reason, gamma = _check(series, total_findings=30)
        assert gamma < 0.30, "premise: this series also estimates near zero"
        assert conv is False
        assert "VACUOUS" not in reason

    def test_a_late_critical_still_blocks(self):
        conv, _, _ = _check([1, 0, 0, 0, 0, 1], total_findings=12)
        assert conv is False

    def test_one_early_critical_is_not_vacuous_and_uses_the_ordinary_path(self):
        conv, reason, _ = _check([1, 0, 0, 0, 0, 0], total_findings=12)
        assert conv is True
        assert "VACUOUS" not in reason, (
            "a real curve exists here; it must converge on the ordinary gamma path")


class TestOrdinaryPathUnchanged:
    def test_normal_decay_then_quiet_is_untouched(self):
        conv, reason, gamma = _check([3, 2, 1, 0, 0, 0], total_findings=25)
        assert conv is True and gamma >= 0.30
        assert "VACUOUS" not in reason

    def test_too_early_still_blocks_regardless_of_vacuity(self):
        conv, reason, _ = _check([0] * 6, total_findings=18, round_idx=1)
        assert conv is False
        assert "too early" in reason

    @pytest.mark.parametrize("kwargs,marker", [
        ({"unresolved_critical": 1}, "A4 BLOCK"),
        ({"contested": 2}, "contested"),
    ])
    def test_the_other_gates_still_bind_on_a_vacuous_series(self, kwargs, marker):
        """Vacuity satisfies the gamma side only. Every other BLOCKING gate applies.

        `rho_churn` was a third case here until the founder ruling of 2026-08-29
        made churn contributory rather than a veto. It is covered below by its
        own test instead of being silently dropped from this list.
        """
        cfg = _cfg()
        conv, reason = _check_gamma_alt_convergence(
            5, 0.0, [0] * 6, cfg, gamma_critical=0.0, total_findings=18, **kwargs)
        assert conv is False
        assert marker.lower() in reason.lower()

    def test_churn_is_reported_but_does_not_bind_on_a_vacuous_series(self):
        """The case removed from the list above, kept rather than dropped.

        Churn must no longer change the verdict, and must still appear on it.
        """
        cfg = _cfg()
        with_churn, reason = _check_gamma_alt_convergence(
            5, 0.0, [0] * 6, cfg, gamma_critical=0.0, total_findings=18, rho_churn=True)
        without_churn, _ = _check_gamma_alt_convergence(
            5, 0.0, [0] * 6, cfg, gamma_critical=0.0, total_findings=18, rho_churn=False)
        assert with_churn == without_churn, "churn is still acting as a veto"
        assert "churn" in reason.lower(), "churn stopped being reported as well as blocking"
