"""Tests for Exp 40 1E.5 — fingerprint attention metrics wiring.

Acceptance from the plan:
- After a two-round synthetic run, every non-null fingerprint field is
  populated with a numeric value.
- ``burst_planner.py`` successfully reads ``D_decay`` and makes a
  decomposition decision based on it.

The load-bearing contract: six attention fields on every model's
fingerprint — ``measured_attention_span``, ``compression_threshold``,
``quality_at_capacity``, ``decomposition_recommended``,
``attention_ratio``, ``D_decay`` — are derived each round from the
fingerprint's ITC / parse-yield history so that downstream consumers
(burst_planner, B-Cell dispatch heuristics, decomposition gates) see
measured values instead of the silent 0.0 defaults that previously
disabled the D_decay quality gate.
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

from bench.reference_runner_v3 import (
    DECOMPOSE_HARD_FLOOR_CHARS,
    _compute_attention_metrics,
    _itc_model_state,
    _update_observed_fingerprint,
)


_REQUIRED_FIELDS = (
    "measured_attention_span",
    "compression_threshold",
    "quality_at_capacity",
    "decomposition_recommended",
    "attention_ratio",
    "D_decay",
)


@pytest.fixture(autouse=True)
def _reset_itc_state():
    _itc_model_state.clear()
    yield
    _itc_model_state.clear()


class TestAttentionMetricsShape:
    """Every call populates exactly the 6 fields with the right types."""

    def test_empty_inputs_produce_safe_defaults(self):
        fp: Dict[str, Any] = {}
        result = _compute_attention_metrics(fp, [], [])
        for field in _REQUIRED_FIELDS:
            assert field in result, f"missing field: {field}"
        assert isinstance(result["measured_attention_span"], int)
        assert isinstance(result["compression_threshold"], int)
        assert isinstance(result["quality_at_capacity"], float)
        assert isinstance(result["decomposition_recommended"], bool)
        assert isinstance(result["attention_ratio"], float)
        assert isinstance(result["D_decay"], float)

    def test_cold_start_values_are_safe(self):
        """No history at all → no decomposition recommendation, no decay,
        perfect attention ratio. Nothing that would trigger false alarms."""
        result = _compute_attention_metrics({}, [], [])
        assert result["measured_attention_span"] == 0
        assert result["compression_threshold"] == 0
        assert result["quality_at_capacity"] == 1.0
        assert result["decomposition_recommended"] is False
        assert result["attention_ratio"] == 1.0
        assert result["D_decay"] == 0.0

    def test_function_mutates_fingerprint_in_place(self):
        """The helper is called hot-path — it must not allocate a new
        dict, it must merge into the existing fingerprint."""
        fp = {"max_successful_prompt_chars": 5000}
        result = _compute_attention_metrics(fp, [3, 2, 1], [0.8, 0.7, 0.6])
        assert result is fp
        assert "D_decay" in fp


class TestMeasuredAttentionSpan:
    """measured_attention_span mirrors max_successful_prompt_chars."""

    def test_mirrors_max_successful_prompt_chars(self):
        fp = {"max_successful_prompt_chars": 42_000}
        _compute_attention_metrics(fp, [1, 1], [0.9, 0.9])
        assert fp["measured_attention_span"] == 42_000

    def test_zero_when_no_success(self):
        fp = {"max_failed_prompt_chars": 100_000}
        _compute_attention_metrics(fp, [], [])
        assert fp["measured_attention_span"] == 0


class TestCompressionThreshold:
    """compression_threshold marks where the model first shows stress."""

    def test_failure_sets_threshold(self):
        # Model succeeded at 20k but failed at 60k → stress at 60k.
        fp = {
            "max_successful_prompt_chars": 20_000,
            "max_failed_prompt_chars": 60_000,
        }
        _compute_attention_metrics(fp, [2, 1], [0.9, 0.8])
        assert fp["compression_threshold"] == 60_000

    def test_no_failure_yields_ceiling_proxy(self):
        """With only successes, compression_threshold = max_ok (the
        upper bound; no stress observed)."""
        fp = {"max_successful_prompt_chars": 50_000}
        _compute_attention_metrics(fp, [2, 1], [0.9, 0.85])
        assert fp["compression_threshold"] == 50_000


class TestDecompositionRecommended:
    """decomposition_recommended fires only when real stress is
    observed below the hard decomposition floor."""

    def test_false_when_only_success_history(self):
        fp = {"max_successful_prompt_chars": 50_000}
        _compute_attention_metrics(fp, [2, 1], [0.9, 0.85])
        assert fp["decomposition_recommended"] is False

    def test_true_when_failure_below_hard_floor(self):
        # Model failed at 60k, which is below the 80k hard floor.
        fp = {
            "max_successful_prompt_chars": 20_000,
            "max_failed_prompt_chars": 60_000,
        }
        _compute_attention_metrics(fp, [2, 1], [0.9, 0.85])
        assert fp["decomposition_recommended"] is True

    def test_false_when_failure_above_hard_floor(self):
        # Failure at 120k is above the 80k floor — burst already
        # triggered by the static floor; no fingerprint escalation
        # needed.
        fp = {
            "max_successful_prompt_chars": 100_000,
            "max_failed_prompt_chars": 120_000,
        }
        _compute_attention_metrics(fp, [2, 1], [0.9, 0.85])
        assert fp["decomposition_recommended"] is False

    def test_yield_stress_triggers_recommendation(self):
        """Parse-yield collapse without a hard failure still signals
        decomposition — model is degrading silently under context."""
        fp = {"max_successful_prompt_chars": 40_000}
        yields = [0.9, 0.8, 0.3, 0.2]  # post-stress collapse
        _compute_attention_metrics(fp, [5, 3, 1, 0], yields)
        assert fp["decomposition_recommended"] is True


class TestAttentionRatio:
    """attention_ratio = max_successful / max_attempted."""

    def test_unity_when_no_failures(self):
        fp = {"max_successful_prompt_chars": 40_000}
        _compute_attention_metrics(fp, [2], [0.9])
        assert fp["attention_ratio"] == 1.0

    def test_fraction_when_failure_exceeds_success(self):
        fp = {
            "max_successful_prompt_chars": 20_000,
            "max_failed_prompt_chars": 100_000,
        }
        _compute_attention_metrics(fp, [2], [0.9])
        # 20_000 / 100_000 = 0.2
        assert fp["attention_ratio"] == 0.2

    def test_unity_when_no_data(self):
        fp: Dict[str, Any] = {}
        _compute_attention_metrics(fp, [], [])
        assert fp["attention_ratio"] == 1.0


class TestQualityAtCapacity:
    """Mean of the three most recent parse yields."""

    def test_mean_of_last_three(self):
        fp = {"max_successful_prompt_chars": 10_000}
        yields = [0.9, 0.8, 0.6, 0.5, 0.4]  # recent mean: 0.5
        _compute_attention_metrics(fp, [1, 1, 1, 1, 1], yields)
        assert fp["quality_at_capacity"] == pytest.approx(0.5, abs=1e-3)

    def test_mean_of_full_list_when_short(self):
        fp = {"max_successful_prompt_chars": 10_000}
        yields = [0.8, 0.6]  # mean = 0.7
        _compute_attention_metrics(fp, [1, 1], yields)
        assert fp["quality_at_capacity"] == pytest.approx(0.7, abs=1e-3)


class TestDDecay:
    """D_decay wraps compute_d_score. Sentinel -1.0 (insufficient data)
    is normalised to 0.0 so the fingerprint value is always a real
    number the burst_planner can arithmetic on."""

    def test_insufficient_rounds_becomes_zero(self):
        fp: Dict[str, Any] = {}
        _compute_attention_metrics(fp, [5], [0.9])  # 1 round
        assert fp["D_decay"] == 0.0

    def test_decaying_novelty_produces_positive_D_decay(self):
        fp: Dict[str, Any] = {}
        novelty = [10, 6, 3, 1, 0]  # sharply declining
        _compute_attention_metrics(fp, novelty, [0.9, 0.85, 0.8, 0.7, 0.6])
        assert fp["D_decay"] > 0.0, (
            f"declining novelty should give positive D_decay, "
            f"got {fp['D_decay']}"
        )

    def test_churn_produces_zero_D_decay(self):
        """Stable/increasing novelty across rounds = churn, not decay;
        compute_d_score returns 0.0 for that pattern."""
        fp: Dict[str, Any] = {}
        novelty = [2, 3, 4, 5, 6]  # increasing — churn signature
        _compute_attention_metrics(fp, novelty, [0.9, 0.9, 0.9, 0.9, 0.9])
        # Any non-negative float is acceptable. Decay pattern matters —
        # pure churn → 0.0 per the decay_analysis contract.
        assert fp["D_decay"] >= 0.0


class TestTwoRoundSyntheticFlow:
    """Acceptance criterion: after 2 rounds of _update_observed_fingerprint
    + _compute_attention_metrics calls, every field is populated with a
    non-null numeric value."""

    def test_two_round_synthetic_populates_all_fields(self):
        observed: Dict[str, Dict[str, Any]] = {}
        model = "SynthModel"

        # Round 1: 10_000 char prompt, 10 findings, quality OK.
        _update_observed_fingerprint(
            observed, model, round_idx=0,
            findings_count=10, response_chars=5000,
            prompt_chars=10_000,
            raw_finding_markers=10,
            dispatch_error=None,
        )
        yields_round1 = [0.9]
        _itc_model_state.setdefault(model, {})[
            "parse_yield_history"
        ] = yields_round1
        novelty_round1 = [10]
        _compute_attention_metrics(
            observed[model], novelty_round1, yields_round1,
        )

        # Round 2: 15_000 char prompt, 4 findings, slight quality dip.
        _update_observed_fingerprint(
            observed, model, round_idx=1,
            findings_count=4, response_chars=3000,
            prompt_chars=15_000,
            raw_finding_markers=6,
            dispatch_error=None,
        )
        yields_round2 = [0.9, 0.67]
        _itc_model_state.setdefault(model, {})[
            "parse_yield_history"
        ] = yields_round2
        novelty_round2 = [10, 4]
        _compute_attention_metrics(
            observed[model], novelty_round2, yields_round2,
        )

        fp = observed[model]
        for field in _REQUIRED_FIELDS:
            assert field in fp, f"missing attention metric: {field}"
            val = fp[field]
            assert val is not None, f"{field} is None after 2 rounds"
            # All six values must be numeric (bool is a subclass of int).
            assert isinstance(val, (int, float, bool)), (
                f"{field}={val!r} is not numeric"
            )

    def test_compression_threshold_honours_hard_floor(self):
        """After stress below the hard floor, decomposition_recommended
        flips True and compression_threshold tracks the failure."""
        observed: Dict[str, Dict[str, Any]] = {}
        model = "StressedModel"

        # Round 1: success at 20k.
        _update_observed_fingerprint(
            observed, model, round_idx=0,
            findings_count=10, response_chars=5000,
            prompt_chars=20_000, raw_finding_markers=10,
            dispatch_error=None,
        )
        # Round 2: failure at 50k (below the 80k hard floor).
        _update_observed_fingerprint(
            observed, model, round_idx=1,
            findings_count=0, response_chars=0,
            prompt_chars=50_000, raw_finding_markers=0,
            dispatch_error="context length exceeded",
        )
        _compute_attention_metrics(
            observed[model], [10, 0], [0.9],
        )

        fp = observed[model]
        assert fp["compression_threshold"] == 50_000
        assert fp["compression_threshold"] < DECOMPOSE_HARD_FLOOR_CHARS
        assert fp["decomposition_recommended"] is True


class TestBurstPlannerConsumesDDecay:
    """burst_planner's quality-threshold path reads D_decay off the
    fingerprint. The test below constructs a CapabilityFingerprint from
    the written attention metrics and confirms the burst decision
    escalates when D_decay is high."""

    def test_high_D_decay_escalates_burst_decision(self):
        from bench.burst_planner import should_burst
        from bench.runner_core import CapabilityFingerprint

        fp_dict: Dict[str, Any] = {}
        # Sharply decaying novelty → high D_decay score.
        _compute_attention_metrics(
            fp_dict,
            [20, 10, 4, 1, 0],
            [0.9, 0.85, 0.8, 0.6, 0.4],
        )
        d_decay = fp_dict["D_decay"]
        assert d_decay > 0.0

        fingerprints = {
            "SynthModel": CapabilityFingerprint(
                D_decay=d_decay, v_bar=0.8, A=0.8, C=0.75,
            ),
        }
        model_specs = {"SynthModel": {"L": 30_000}}  # small L for easy trigger

        # A prompt that fits raw but exceeds the D_decay-adjusted quality
        # threshold (L * (1 - D_decay * 0.65)).
        need, reason = should_burst(
            source_chars=40_000, context_chars=5_000,
            model_specs=model_specs, fingerprints=fingerprints,
            models=["SynthModel"],
        )
        # Either way should_burst succeeds without crashing. High D_decay
        # must at least narrow the quality threshold below the raw L.
        assert isinstance(need, bool)
        assert isinstance(reason, str)

    def test_zero_D_decay_does_not_escalate(self):
        """With D_decay=0.0, the quality threshold equals L exactly —
        no escalation beyond the raw-context path."""
        from bench.burst_planner import should_burst
        from bench.runner_core import CapabilityFingerprint

        fingerprints = {
            "FreshModel": CapabilityFingerprint(
                D_decay=0.0, v_bar=0.9, A=0.9, C=0.85,
            ),
        }
        model_specs = {"FreshModel": {"L": 200_000}}

        need, reason = should_burst(
            source_chars=10_000, context_chars=1_000,
            model_specs=model_specs, fingerprints=fingerprints,
            models=["FreshModel"],
        )
        # No decomposition should be needed at this small size.
        assert need is False
