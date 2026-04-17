"""Tests for Exp 40 1E.7 cross-model diversity metric.

Acceptance from the plan:
- Synthetic round with five identical alternatives → metric reports 1.0
- Synthetic round with five disjoint alternatives → metric close to 0
"""

from __future__ import annotations

import pytest

from bench.dm._diversity import (
    compute_cross_model_diversity,
    diversity_signal_from_round,
)


class TestAcceptance:

    def test_five_identical_alternatives_maps_to_one(self):
        alt = (
            "Increase the retry budget from 3 to 5 to tolerate intermittent "
            "API timeouts under load."
        )
        stats = compute_cross_model_diversity([alt, alt, alt, alt, alt])
        assert stats["count"] == 5.0
        assert stats["pairs"] == 10.0
        assert stats["mean_pairwise_jaccard"] == 1.0
        assert stats["max_pairwise_jaccard"] == 1.0
        assert stats["template_collapse_risk"] == 1.0

    def test_five_disjoint_alternatives_maps_to_zero(self):
        alternatives = [
            "Rotate cryptographic keys quarterly",
            "Deploy telemetry collection across ingestion gateways",
            "Migrate audit logs into a columnar warehouse",
            "Introduce schema versioning for payload envelopes",
            "Harden TLS negotiation against downgrade attacks",
        ]
        stats = compute_cross_model_diversity(alternatives)
        assert stats["count"] == 5.0
        # Disjoint vocabularies → mean Jaccard exactly 0.0
        assert stats["mean_pairwise_jaccard"] == 0.0
        assert stats["template_collapse_risk"] == 0.0

    def test_partial_overlap_intermediate(self):
        # Two identical + three disjoint = some overlap structure.
        alternatives = [
            "Rotate keys quarterly",
            "Rotate keys quarterly",
            "Refactor dispatch queue",
            "Drop stale indices",
            "Harden TLS",
        ]
        stats = compute_cross_model_diversity(alternatives)
        # At least one pair is identical (max = 1.0)
        assert stats["max_pairwise_jaccard"] == 1.0
        # Mean strictly between 0 and 1
        assert 0.0 < stats["mean_pairwise_jaccard"] < 1.0


class TestRoundSignal:

    def test_per_model_counts_recorded(self):
        per_model_alts = [
            ("CC2", "Alt A"),
            ("CC2", "Alt B"),
            ("Gemini", "Alt C"),
            ("Codex", "Alt D"),
        ]
        out = diversity_signal_from_round(per_model_alts)
        assert out["per_model_count"] == {"CC2": 2, "Gemini": 1, "Codex": 1}

    def test_cross_model_only_uses_first_per_model(self):
        per_model_alts = [
            ("CC2", "Keys rotated quarterly"),
            ("CC2", "Totally different text"),
            ("Gemini", "Keys rotated quarterly"),
            ("Codex", "Keys rotated quarterly"),
        ]
        out = diversity_signal_from_round(per_model_alts)
        # cross_model_only picks first alt from each model — all three are
        # identical → mean_pairwise_jaccard = 1.0
        assert out["cross_model_only"]["mean_pairwise_jaccard"] == 1.0

    def test_empty_input(self):
        out = diversity_signal_from_round([])
        assert out["per_model_count"] == {}
        assert out["stats"]["count"] == 0.0

    def test_single_alternative(self):
        out = diversity_signal_from_round([("CC2", "only one")])
        # count=1, pairs=0 → undefined-in-principle. Module returns
        # neutral 1.0 values for count (but 0.0 for mean_jaccard).
        assert out["stats"]["count"] == 1.0
        assert out["stats"]["pairs"] == 0.0


class TestRunnerIntegration:
    """Confirm the runner's round_data dict carries the new field."""

    def test_round_data_key_exists(self):
        # The integration wiring adds `cross_model_diversity` to round_data.
        # Direct dict construction check — the runner populates this key
        # unconditionally (may be None if no alternatives).
        import inspect
        from bench import reference_runner_v2
        src = inspect.getsource(reference_runner_v2)
        assert '"cross_model_diversity": cross_model_diversity' in src, (
            "Runner must include cross_model_diversity key in round_data "
            "for the 1E.7 logging acceptance."
        )
