"""Regression tests for Exp 40 continuation fix 1d — ITC γ-regime
gate + suppressed-DEGRADATION HIL-flag exclusion.

ITC = the project's "IT Crowd fix": on degradation, restart the model
fresh with fingerprint-informed scope (never bench/skip). The deeper
rationale is burst reasoning — a fresh instance surfaces what a
long-running instance has stopped seeing.

Continuation Anomaly 5: the run reached deep convergence by γ-decay
(terminal γ≈0.034) yet every panel member was flagged DEGRADATION
every round, because in the converged regime the panel naturally
produces low-yield verdict-heavy output. The pre-existing A4 rho-gate
suppressed the restart *adaptation* but the DEGRADATION was still
recorded as a classification BEFORE the suppression check, so it still
fed `_itc_consecutive_failures` and still fired the per-round HIL
underperformer flag.

Fix 1d:
  (i)  γ-regime gate: DEGRADATION is also suppressed when γ is in the
       converged regime (γ < gamma_converged_threshold, default 0.10),
       independently of rho.
  (ii) A suppressed DEGRADATION is recorded with classification=None
       (+ a `suppressed` marker), so it neither feeds the
       consecutive-failure streak nor the HIL flag.

These tests pin:
  1. γ converged + unhealthy rho → suppressed (γ gate independent of rho).
  2. Suppressed round records classification=None, suppressed=DEGRADATION.
  3. Suppressed rounds never raise a HIL underperformer flag, even
     across many consecutive converged rounds (the core bug).
  4. γ active + unhealthy rho → NOT suppressed (no false negative);
     genuine degradation still escalates to restart_fresh + HIL flag.
  5. Backward compat: default gamma_current=1.0 leaves rho-only
     behaviour unchanged.
"""

from __future__ import annotations

import pytest

from bench.reference_runner_v3 import (
    ITC_DEGRADATION,
    _itc_adapt,
    _itc_consecutive_failures,
    _itc_hil_flags,
    _itc_model_state,
)


@pytest.fixture(autouse=True)
def _reset_itc_state():
    _itc_model_state.clear()
    _itc_hil_flags.clear()
    yield
    _itc_model_state.clear()
    _itc_hil_flags.clear()


class TestGammaGate:
    def test_converged_gamma_suppresses_even_with_low_rho(self):
        # rho 0.05 (collapsed — would normally trigger change_focus)
        # but γ=0.034 (deep converged regime). γ gate must suppress.
        _itc_adapt(
            "Gemini", ITC_DEGRADATION, round_idx=12,
            rho_rolling_avg=0.05, rho_threshold=0.25,
            gamma_current=0.034, gamma_converged_threshold=0.10,
        )
        assert _itc_model_state["Gemini"]["adaptation"] is None, (
            "converged-γ regime must suppress the DEGRADATION restart "
            "even when rho is collapsed"
        )

    def test_suppressed_round_records_classification_none(self):
        _itc_adapt(
            "Gemini", ITC_DEGRADATION, round_idx=12,
            rho_rolling_avg=0.05, rho_threshold=0.25,
            gamma_current=0.034, gamma_converged_threshold=0.10,
        )
        hist = _itc_model_state["Gemini"]["history"]
        assert len(hist) == 1
        assert hist[0]["classification"] is None, (
            "suppressed DEGRADATION must not be a counted classification"
        )
        assert hist[0]["suppressed"] == ITC_DEGRADATION, (
            "suppressed marker must record the original classification "
            "for observability"
        )

    def test_suppressed_rounds_never_raise_hil_flag(self):
        # The core continuation bug: 6 consecutive converged-regime
        # DEGRADATION rounds. Pre-fix, this raised a HIL flag every
        # round from round 3 onward. Post-fix: zero HIL flags.
        for rnd in range(10, 16):
            _itc_adapt(
                "Gemini", ITC_DEGRADATION, round_idx=rnd,
                rho_rolling_avg=0.05, rho_threshold=0.25,
                gamma_current=0.034, gamma_converged_threshold=0.10,
            )
        assert _itc_consecutive_failures("Gemini") == 0, (
            "suppressed rounds must not accumulate a consecutive "
            "failure streak"
        )
        gemini_flags = [
            f for f in _itc_hil_flags if f["model"] == "Gemini"
        ]
        assert gemini_flags == [], (
            f"no HIL flag should be raised for a model that is merely "
            f"converged; got {gemini_flags}"
        )


class TestGammaGateNoFalseNegative:
    def test_active_gamma_low_rho_still_degrades(self):
        # γ=0.40 (active regime) + rho 0.05 (collapsed). This is a
        # GENUINE degradation — the γ gate must NOT suppress it.
        _itc_adapt(
            "SickModel", ITC_DEGRADATION, round_idx=3,
            rho_rolling_avg=0.05, rho_threshold=0.25,
            gamma_current=0.40, gamma_converged_threshold=0.10,
        )
        assert _itc_model_state["SickModel"]["adaptation"] == (
            "change_focus"
        ), "active-γ + collapsed-rho must remain a real DEGRADATION"

    def test_genuine_degradation_still_escalates_to_restart_and_hil(
        self,
    ):
        # Three consecutive genuine degradations (active γ, low rho).
        for rnd in (3, 4, 5):
            _itc_adapt(
                "SickModel", ITC_DEGRADATION, round_idx=rnd,
                rho_rolling_avg=0.05, rho_threshold=0.25,
                gamma_current=0.40, gamma_converged_threshold=0.10,
            )
        # 3rd consecutive → restart_fresh adaptation + HIL flag.
        assert _itc_model_state["SickModel"]["adaptation"] == (
            "restart_fresh"
        )
        sick_flags = [
            f for f in _itc_hil_flags if f["model"] == "SickModel"
        ]
        assert sick_flags, (
            "a genuinely degrading model must still raise a HIL flag "
            "(burst-reasoning restart path preserved)"
        )


class TestBackwardCompat:
    def test_default_gamma_leaves_rho_behaviour_unchanged(self):
        # No gamma args → default gamma_current=1.0 (active). Healthy
        # rho still suppresses; collapsed rho still triggers
        # change_focus. Identical to pre-1d A4 behaviour.
        _itc_adapt(
            "H", ITC_DEGRADATION, round_idx=5, rho_rolling_avg=0.55,
        )
        assert _itc_model_state["H"]["adaptation"] is None

        _itc_adapt(
            "S", ITC_DEGRADATION, round_idx=5, rho_rolling_avg=0.05,
        )
        assert _itc_model_state["S"]["adaptation"] == "change_focus"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
