"""Tests for Exp 40 1E.9 — cross-round recidivism detection.

Acceptance from the plan:
- On a synthetic two-round run where round-2 resubmits a round-1
  alternative unchanged, the round-2 finding is flagged as recidivism
  and incurs the 0.60 severe tier.

The load-bearing contract: ``check_sibling_admissibility`` accepts a
prior-round list; when any current alternative matches a prior-round
alternative at Jaccard >= ``near_copy_threshold``, the alternative is
demoted to inadmissible with the ``recidivism_near_copy`` reason, and
``eta_int_modulator`` returns 0.60.

§18 previously only detected near-duplicates within a single round; this
extends the check across rounds so a model cannot evade the severe tier
by staggering identical submissions.
"""

from __future__ import annotations

import pytest

from bench.dm._divergence import (
    AlternativeRecord,
    DivergenceConfig,
    build_divergence_record,
    check_sibling_admissibility,
    eta_int_modulator,
)


_ROUND1_ALT_BLOCK = """
Primary solution is X.

## Alternative 1 (dimension: mechanism)
Use recursive Bayesian updates to propagate posterior uncertainty
through R_k rather than treating each round as independent.
Differs from primary on mechanism in that the primary uses multiplicative
decay while this uses explicit Bayesian inference over the full history.
"""

_ROUND1_ALT_BLOCK_B = """
Primary solution is X.

## Alternative 1 (dimension: scope)
Restrict the evaluation to only findings with severity >= HIGH, because
low-severity noise dominates the residual-risk tail.
Differs from primary on scope in that the primary applies uniformly
across all severities while this narrows to HIGH-and-above only.
"""


def _make_alt(text: str, finding_id: str = "f1") -> AlternativeRecord:
    """Construct a synthetic admissible AlternativeRecord for testing."""
    return AlternativeRecord(
        primary_finding_id=finding_id,
        alternative_text=text,
        dimension="mechanism",
        isomorphism_score=0.1,
        admissible=True,
        contrast_statement="differs from primary on mechanism",
        admissibility_gate_passed=True,
    )


class TestAlternativeRecordHasRecidivismField:
    """Sanity check: the new field exists and defaults to 0.0."""

    def test_default_prior_round_isomorphism_is_zero(self):
        alt = _make_alt("some alternative text")
        assert alt.prior_round_isomorphism == 0.0


class TestCheckSiblingAdmissibilityAcceptsPriorRound:
    """Extension: check_sibling_admissibility accepts a prior_round_alternatives
    kwarg and populates prior_round_isomorphism on each alternative."""

    def test_no_prior_round_leaves_field_at_zero(self):
        current = [_make_alt("apples and oranges")]
        check_sibling_admissibility(current)
        assert current[0].prior_round_isomorphism == 0.0

    def test_empty_prior_round_leaves_field_at_zero(self):
        current = [_make_alt("apples and oranges")]
        check_sibling_admissibility(current, prior_round_alternatives=[])
        assert current[0].prior_round_isomorphism == 0.0

    def test_disjoint_prior_round_does_not_demote(self):
        """Completely different prior-round alternative → low Jaccard →
        current alt stays admissible and the field records the low score."""
        prior = [_make_alt("quantum chromodynamics of nuclear forces")]
        current = [_make_alt("apples oranges bananas")]
        check_sibling_admissibility(current, prior_round_alternatives=prior)
        assert current[0].prior_round_isomorphism < 0.5
        assert current[0].admissible is True

    def test_identical_prior_round_demotes_alternative(self):
        text = (
            "Use recursive Bayesian updates to propagate posterior "
            "uncertainty through R_k at each round boundary."
        )
        prior = [_make_alt(text)]
        current = [_make_alt(text)]
        check_sibling_admissibility(current, prior_round_alternatives=prior)
        assert current[0].prior_round_isomorphism == pytest.approx(1.0)
        assert current[0].admissible is False
        assert any(
            "recidivism_near_copy" in r for r in current[0].rejection_reasons
        )


class TestRecidivismTriggersSevereTier:
    """The load-bearing acceptance: recidivism fires the 0.60 tier."""

    def test_round1_alternative_normal_modulator(self):
        """Baseline: a well-formed round-1 alternative does not fire the
        severe tier."""
        rec = build_divergence_record(
            "f1", "primary text goes here", _ROUND1_ALT_BLOCK,
            config=DivergenceConfig(enabled=True),
        )
        m = eta_int_modulator(rec)
        # Synthetic block may fail some secondary gate (contrast format,
        # sibling threshold), but it must not fire the 0.60 tier in
        # round 1 because there are no prior-round alternatives.
        assert m > 0.60

    def test_round2_resubmission_fires_severe_tier(self):
        """Acceptance criterion: resubmitting a round-1 alternative unchanged
        in round 2 triggers the severe 0.60 tier."""
        cfg = DivergenceConfig(enabled=True)
        rec1 = build_divergence_record(
            "f1", "primary text", _ROUND1_ALT_BLOCK, config=cfg,
        )
        # Re-submit the SAME block in round 2.
        rec2 = build_divergence_record(
            "f1", "primary text", _ROUND1_ALT_BLOCK,
            config=cfg,
            prior_round_alternatives=rec1.alternatives,
        )
        assert rec2.alternatives, "round 2 must parse at least one alternative"
        alt = rec2.alternatives[0]
        assert alt.prior_round_isomorphism >= cfg.near_copy_threshold
        m = eta_int_modulator(rec2, cfg)
        assert m == 0.60, (
            f"recidivism must trigger severe 0.60 tier, got {m}"
        )

    def test_round2_novel_alternative_does_not_fire_severe_tier(self):
        """Regression guard: a genuinely different round-2 alternative
        escapes the severe tier. Recidivism must be precise, not a
        blanket penalty."""
        cfg = DivergenceConfig(enabled=True)
        rec1 = build_divergence_record(
            "f1", "primary text", _ROUND1_ALT_BLOCK, config=cfg,
        )
        # Different alternative block for round 2.
        rec2 = build_divergence_record(
            "f1", "primary text", _ROUND1_ALT_BLOCK_B,
            config=cfg,
            prior_round_alternatives=rec1.alternatives,
        )
        if not rec2.alternatives:
            pytest.skip("no alternatives parsed in variant block")
        alt = rec2.alternatives[0]
        assert alt.prior_round_isomorphism < cfg.near_copy_threshold
        m = eta_int_modulator(rec2, cfg)
        assert m > 0.60


class TestRecidivismEscapesDirectivesDisabled:
    """When the directive is disabled, no recidivism check fires —
    compliance path is trivially true."""

    def test_disabled_config_returns_compliant(self):
        cfg = DivergenceConfig(enabled=False)
        rec = build_divergence_record(
            "f1", "primary", _ROUND1_ALT_BLOCK,
            config=cfg,
            prior_round_alternatives=[_make_alt("identical text")],
        )
        assert rec.compliant is True
        assert eta_int_modulator(rec, cfg) == 1.0


class TestBackwardCompatibility:
    """Callers that don't pass prior_round_alternatives must still work
    — the parameter is optional and defaults to None."""

    def test_call_without_prior_round_kwarg(self):
        current = [_make_alt("some text"), _make_alt("other text")]
        # Must not raise, must behave exactly as before.
        check_sibling_admissibility(current)
        assert current[0].admissible is True
        assert current[1].admissible is True

    def test_build_divergence_record_without_prior_round_kwarg(self):
        rec = build_divergence_record(
            "f1", "primary", _ROUND1_ALT_BLOCK,
            config=DivergenceConfig(enabled=True),
        )
        # All alternatives must have prior_round_isomorphism = 0.0 by default
        # when no prior-round list is supplied.
        for alt in rec.alternatives:
            assert alt.prior_round_isomorphism == 0.0


class TestRejectionReasonTextIsInformative:
    """The recidivism rejection reason must name the matched prior-round
    index and the Jaccard score, for log/debug traceability."""

    def test_rejection_reason_names_prior_index_and_score(self):
        text = "recursive Bayesian inference with uniform priors"
        prior = [_make_alt("unrelated text"), _make_alt(text)]
        current = [_make_alt(text)]
        check_sibling_admissibility(current, prior_round_alternatives=prior)
        reasons = current[0].rejection_reasons
        recid = [r for r in reasons if r.startswith("recidivism_near_copy")]
        assert recid, f"expected recidivism reason in {reasons}"
        assert "prior_round_alt_1" in recid[0], (
            f"reason must name matching prior index 1: {recid[0]}"
        )
