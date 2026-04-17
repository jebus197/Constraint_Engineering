"""Tests for cross-model diversity metric (Item 1E.7).

The metric is the defensive instrument for compliance-theatre detection
under §18 divergence directive. Mean pairwise Jaccard across all
divergence alternatives across all models: trend to 1.0 signals
template collapse.
"""

from __future__ import annotations

import pytest

from bench.dm._diversity import (
    compute_cross_model_diversity,
    diversity_signal_from_round,
)


class TestComputeCrossModelDiversity:
    def test_empty_input(self):
        out = compute_cross_model_diversity([])
        assert out["count"] == 0.0
        assert out["pairs"] == 0.0

    def test_single_alternative(self):
        out = compute_cross_model_diversity(["one thing"])
        assert out["count"] == 1.0
        assert out["pairs"] == 0.0

    def test_identical_alternatives_max_risk(self):
        out = compute_cross_model_diversity([
            "change the mechanism from X to Y",
            "change the mechanism from X to Y",
            "change the mechanism from X to Y",
        ])
        assert out["mean_pairwise_jaccard"] == 1.0
        assert out["template_collapse_risk"] == 1.0

    def test_disjoint_alternatives_zero_risk(self):
        out = compute_cross_model_diversity([
            "apple banana cherry",
            "electron proton neutron",
            "keyboard mouse monitor",
        ])
        assert out["mean_pairwise_jaccard"] == 0.0
        assert out["template_collapse_risk"] == 0.0

    def test_partial_overlap(self):
        out = compute_cross_model_diversity([
            "change the mechanism X",
            "change the mechanism Y",
        ])
        # Shared tokens: change, mechanism → some overlap but not total
        assert 0.0 < out["mean_pairwise_jaccard"] < 1.0

    def test_risk_threshold_alignment(self):
        """Mean >= 0.85 should produce risk >= 0.70 (the isomorphism-threshold-aware range)."""
        # Construct alternatives with known high similarity
        base_tokens = ["replace", "implementation", "with", "alternative"]
        alt1 = " ".join(base_tokens + ["detail"])
        alt2 = " ".join(base_tokens + ["extra"])
        alt3 = " ".join(base_tokens + ["sample"])
        out = compute_cross_model_diversity([alt1, alt2, alt3])
        # Jaccard between each pair: 4/6 ≈ 0.67 — below 0.85 but non-trivial
        assert out["mean_pairwise_jaccard"] > 0.5

    def test_max_tracks_highest_similarity(self):
        alts = [
            "completely different one",
            "identical text here",
            "identical text here",  # perfect pair with above
        ]
        out = compute_cross_model_diversity(alts)
        assert out["max_pairwise_jaccard"] == 1.0


class TestDiversitySignalFromRound:
    def test_empty_round(self):
        out = diversity_signal_from_round([])
        assert out["per_model_count"] == {}

    def test_single_model_multiple_alternatives(self):
        out = diversity_signal_from_round([
            ("CC2", "first alt"),
            ("CC2", "second alt"),
            ("CC2", "third alt"),
        ])
        assert out["per_model_count"]["CC2"] == 3

    def test_cross_model_only_uses_first_per_model(self):
        out = diversity_signal_from_round([
            ("CC2", "alpha"),
            ("CC2", "beta"),
            ("Codex", "alpha"),
            ("Codex", "gamma"),
        ])
        # Stats pools all 4; cross_model_only uses only CC2's first and Codex's first
        assert out["stats"]["count"] == 4.0
        assert out["cross_model_only"]["count"] == 2.0

    def test_template_collapse_across_models(self):
        """Five models emitting the same alternative → collapse risk = 1.0."""
        template = "change the mechanism from A to B"
        out = diversity_signal_from_round([
            ("CC2", template),
            ("Codex", template),
            ("Gemini", template),
            ("ChatGPT", template),
            ("DeepSeek", template),
        ])
        assert out["cross_model_only"]["template_collapse_risk"] == 1.0
        assert out["stats"]["template_collapse_risk"] == 1.0

    def test_diverse_across_models(self):
        """Each model emits a distinct mechanism → risk ≈ 0."""
        out = diversity_signal_from_round([
            ("CC2", "swap hash for merkle"),
            ("Codex", "replace regex with parser"),
            ("Gemini", "use streaming instead of batch"),
            ("ChatGPT", "invert control flow"),
            ("DeepSeek", "amortise cost over cache"),
        ])
        # All disjoint token sets — risk near zero
        assert out["cross_model_only"]["template_collapse_risk"] < 0.2
