"""Tests for the G7 merge-deadlock arbitration module.

Validates the compelled-convergence rule designed in
`experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md`
against the aggregation contract and the continuation's observed
deadlock shapes (C0008 20-way, C0023 14-round, etc.).

Covers:
  1. Query construction (new finding + candidates + single-answer ask).
  2. Vote parsing: clean MERGE_INTO, clean KEEP_DISTINCT, bare-id
     fallback, non-candidate MERGE rejected, contradictory/multi
     unparseable.
  3. Aggregation: ≥3 majority → MERGE; ≥3 KEEP_DISTINCT → distinct;
     plurality-no-majority → DEFER; unparseable votes don't count.
  4. dispatch_merge_arbitration end-to-end with a stub dispatch_fn,
     including graceful degradation when a model dispatch raises.
"""

from __future__ import annotations

import pytest

from bench.merge_arbitration import (
    KEEP_DISTINCT,
    MergeArbitrationVote,
    aggregate_votes,
    build_arbitration_query,
    dispatch_merge_arbitration,
    parse_arbitration_vote,
)


NEW_FINDING = {
    "finding_id": "C0099",
    "description": "off-by-one in window slice drops last element",
    "proposed_fix": "<<<< SEARCH f.py\n a[1:]\n====\n a[0:]\n>>>> REPLACE",
    "target_file": "f.py",
    "severity": 0.8,
}
CANDIDATES = [
    {"canonical_id": "C0008", "description": "slice bound wrong in window"},
    {"canonical_id": "C0010", "description": "unrelated null deref"},
    {"canonical_id": "C0013", "description": "another slice bug variant"},
]


class TestQueryConstruction:
    def test_query_contains_new_finding_and_candidates(self):
        q = build_arbitration_query(NEW_FINDING, CANDIDATES)
        assert "C0099" in q
        assert "C0008" in q and "C0010" in q and "C0013" in q
        assert "MERGE_INTO_" in q
        assert "KEEP_DISTINCT" in q
        assert "single definitive answer" in q.lower()

    def test_query_truncates_long_fix(self):
        big = dict(NEW_FINDING, proposed_fix="X" * 5000)
        q = build_arbitration_query(big, CANDIDATES, fix_truncate=100)
        # The truncated fix segment must not carry all 5000 chars.
        assert "X" * 200 not in q


class TestVoteParsing:
    def test_clean_merge_vote(self):
        v = parse_arbitration_vote(
            "MERGE_INTO_C0008", ["C0008", "C0010"], "CC2", 1.0,
        )
        assert v.vote == "C0008"
        assert v.parse_ok

    def test_clean_keep_distinct(self):
        v = parse_arbitration_vote(
            "KEEP_DISTINCT", ["C0008"], "Gemini", 1.0,
        )
        assert v.vote == KEEP_DISTINCT
        assert v.parse_ok

    def test_keep_distinct_hyphen_space_variants(self):
        for token in ("KEEP-DISTINCT", "KEEP DISTINCT", "keep_distinct"):
            v = parse_arbitration_vote(token, ["C0008"], "m", 1.0)
            assert v.vote == KEEP_DISTINCT, token

    def test_non_candidate_merge_rejected(self):
        # Model votes to merge into an id NOT among the candidates.
        v = parse_arbitration_vote(
            "MERGE_INTO_C9999", ["C0008", "C0010"], "m", 1.0,
        )
        assert not v.parse_ok
        assert v.vote == ""

    def test_contradictory_vote_unparseable(self):
        v = parse_arbitration_vote(
            "MERGE_INTO_C0008 but also KEEP_DISTINCT",
            ["C0008"], "m", 1.0,
        )
        assert not v.parse_ok

    def test_multi_merge_unparseable(self):
        v = parse_arbitration_vote(
            "MERGE_INTO_C0008 MERGE_INTO_C0010",
            ["C0008", "C0010"], "m", 1.0,
        )
        assert not v.parse_ok

    def test_bare_candidate_id_fallback(self):
        # No explicit token, but exactly one candidate id mentioned.
        v = parse_arbitration_vote(
            "I think this is the same as C0013.",
            ["C0008", "C0013"], "m", 1.0,
        )
        assert v.vote == "C0013"
        assert v.parse_ok

    def test_empty_response_unparseable(self):
        v = parse_arbitration_vote("", ["C0008"], "m", 1.0)
        assert not v.parse_ok


class TestAggregation:
    def _votes(self, *vals):
        return [
            MergeArbitrationVote(f"m{i}", v, "", 1.0, parse_ok=bool(v))
            for i, v in enumerate(vals)
        ]

    def test_clear_majority_merges(self):
        r = aggregate_votes(
            "C0099",
            self._votes("C0008", "C0008", "C0008", KEEP_DISTINCT, "C0010"),
        )
        assert r.decision == "MERGE"
        assert r.target == "C0008"

    def test_majority_keep_distinct(self):
        r = aggregate_votes(
            "C0099",
            self._votes(
                KEEP_DISTINCT, KEEP_DISTINCT, KEEP_DISTINCT,
                "C0008", "C0010",
            ),
        )
        assert r.decision == "KEEP_DISTINCT"
        assert r.target is None

    def test_plurality_without_majority_defers(self):
        # 2-2-1 split → DEFER (design's canonical stay-deferred case).
        r = aggregate_votes(
            "C0099",
            self._votes("C0008", "C0008", "C0010", "C0010", KEEP_DISTINCT),
        )
        assert r.decision == "DEFER"
        assert r.target is None

    def test_unparseable_votes_do_not_count(self):
        # 3 valid C0008 + 2 unparseable. 3 ≥ 3 → MERGE.
        r = aggregate_votes(
            "C0099",
            self._votes("C0008", "C0008", "C0008", "", ""),
        )
        assert r.decision == "MERGE"
        assert r.target == "C0008"
        # But 2 valid + 3 unparseable → no majority → DEFER.
        r2 = aggregate_votes(
            "C0099",
            self._votes("C0008", "C0008", "", "", ""),
        )
        assert r2.decision == "DEFER"

    def test_all_unparseable_defers(self):
        r = aggregate_votes("C0099", self._votes("", "", "", "", ""))
        assert r.decision == "DEFER"
        assert "no parseable votes" in r.rationale


class _MC:
    def __init__(self, label):
        self.label = label


class TestDispatchEndToEnd:
    PANEL = [_MC(m) for m in ("CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini")]

    def test_majority_merge_via_stub(self):
        # 3 vote C0008, 1 KEEP_DISTINCT, 1 C0010.
        scripted = {
            "CC2": "MERGE_INTO_C0008",
            "ChatGPT": "MERGE_INTO_C0008",
            "Codex": "MERGE_INTO_C0008",
            "DeepSeek": "KEEP_DISTINCT",
            "Gemini": "MERGE_INTO_C0010",
        }

        def stub(mc, prompt):
            return scripted[mc.label], 0.5

        result = dispatch_merge_arbitration(
            NEW_FINDING, CANDIDATES, self.PANEL, stub,
        )
        assert result.decision == "MERGE"
        assert result.target == "C0008"
        assert len(result.votes) == 5

    def test_graceful_degradation_on_dispatch_error(self):
        def stub(mc, prompt):
            if mc.label == "DeepSeek":
                raise RuntimeError("simulated route failure")
            return "MERGE_INTO_C0008", 0.4

        result = dispatch_merge_arbitration(
            NEW_FINDING, CANDIDATES, self.PANEL, stub,
        )
        # 4 valid C0008 votes ≥ 3 → MERGE even with one model erroring.
        assert result.decision == "MERGE"
        assert result.target == "C0008"
        ds_vote = [v for v in result.votes if v.model == "DeepSeek"][0]
        assert not ds_vote.parse_ok
        assert "__ERROR__" in ds_vote.raw_response

    def test_split_panel_defers(self):
        scripted = {
            "CC2": "MERGE_INTO_C0008",
            "ChatGPT": "MERGE_INTO_C0008",
            "Codex": "MERGE_INTO_C0010",
            "DeepSeek": "MERGE_INTO_C0010",
            "Gemini": "KEEP_DISTINCT",
        }

        def stub(mc, prompt):
            return scripted[mc.label], 0.3

        result = dispatch_merge_arbitration(
            NEW_FINDING, CANDIDATES, self.PANEL, stub,
        )
        assert result.decision == "DEFER"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
