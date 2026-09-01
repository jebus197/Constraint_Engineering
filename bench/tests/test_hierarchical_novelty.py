"""Hierarchical novelty: location decides the coarse call, signature splits within it.

WHY IT EXISTS
-------------
Location keying answers "is this somewhere new?" and is right about that. Its
known blind spot is a SECOND genuinely different defect at an already-flagged
location, which it merges by construction. Two attempts to replace it with a
prose-similarity measure failed in opposite directions: embeddings scored two
genuinely different defects at 0.684 and 0.781 (merging them), and lexical
overlap separated them but destroyed convergence on all six runs it was replayed
against, because rewording read as a new defect.

The founder asked whether two reasonably reliable measures could be KEPT rather
than one replacing the other. Measured on a constructed case with proven ground
truth — two distinct defects on one listing, each re-worded by different models:

    location alone      re-wordings [2,0,0,0]   blind spot [1,0,0,0]  merges
    signature alone     [2,0,0,0]               [1,0,0,0]             merges
    both, AND           [2,0,0,0]               [1,0,0,0]             merges
    both, OR            [2,0,0,0]               [1,0,0,0]             merges
    both, HIERARCHICAL  [2,0,0,0]               [2,0,0,0]             CORRECT

Voting fails because AND and OR treat the two rules as interchangeable opinions
about one question. They answer different questions.

GROUND TRUTH FOR THE BLIND-SPOT CASE, established by execution not assertion:
both defects sit on `dedup` in ALG-02-REF-01.md.
  D1  the comparison-count claim: 2016 comparisons on 64 distinct inputs, not k.
  D2  equality conflation: dedup([1, 1.0, True]) returns one element.
Repairing D1 (set membership) leaves D2 intact — so by the counterfactual
definition the panel converged on, they are genuinely different defects.

SHADOW ONLY. `hierarchical_novelty_convergence` defaults False.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests/fixtures/stem"))

from bench.convergence_location import (  # noqa: E402
    WITHIN_LOCATION_THRESHOLD,
    hierarchical_novelty_series,
    signature_similarity,
    stem_signature,
)
from bench.reference_runner_v3 import RunnerConfig  # noqa: E402


def _symbols():
    import stem_fixtures as S
    doc = (S.DOC_DIR / "ALG-02-REF-01.md").read_text()
    return sorted(set(re.findall(r"\b([A-Z]{2,3}-\d{2})\b", doc))
                  | set(re.findall(r"^\s*def\s+(\w+)", doc, re.M)))


def _entries(rows):
    return {f"C{i}": dict(canonical_id=f"C{i}", open_since_round=r,
                          severity=sev, description=d)
            for i, (r, sev, d) in enumerate(rows, 1)}


D1_A = ("VERDICT: CONFIRM. AL-03 overstates the comparison count: `dedup` performs "
        "2016 comparisons on 64 distinct inputs, not the at-most-k the document claims. "
        "Listing A.")
D1_B = ("AL-03: the linear-time claim for `dedup` fails. Membership on a list is O(n), "
        "so Listing A is quadratic — 2016 comparisons at n=64.")
D1_C = ("Re-raising: `dedup` in Listing A is not linear; the stated comparison bound "
        "of k is exceeded at 64 inputs.")
D2_A = ("Listing A's `dedup` conflates equal-but-distinct values: `1`, `1.0` and `True` "
        "compare equal, so dedup([1, 1.0, True]) returns a single element and silently "
        "drops two distinct inputs.")
D2_B = ("Listing A `dedup` uses `==` for membership, so numerically-equal values of "
        "different types (1 vs 1.0 vs True) are treated as duplicates and lost.")


class TestTheBlindSpotIsClosed:
    """The case location keying gets wrong, and the reason the rule exists."""

    def test_two_distinct_defects_at_one_location_are_separated(self):
        s = hierarchical_novelty_series(
            _entries([(0, 0.85, D1_A), (0, 0.82, D1_B), (0, 0.88, D2_A),
                      (1, 0.80, D1_C), (1, 0.81, D2_B)]), 3, _symbols())
        assert s == [2, 0, 0, 0], (
            "two genuinely different defects on one listing must count as two, and "
            "all five wordings must collapse to those two")

    def test_location_keying_alone_merges_them(self):
        """The comparison that justifies the change. If this ever stops failing,
        the blind spot has gone away and this rule may be unnecessary."""
        from bench.convergence_location import finding_locations
        syms = _symbols()
        a = finding_locations(D1_A, syms)
        b = finding_locations(D2_A, syms)
        assert a and b and (a & b), (
            "both defects name the same location — which is exactly why location "
            "keying cannot tell them apart")


class TestRewordingsStillCollapse:
    """The property the previous candidate destroyed on all six replayed runs."""

    def test_three_wordings_of_one_defect_count_once(self):
        s = hierarchical_novelty_series(
            _entries([(0, 0.85, D1_A), (0, 0.82, D1_B), (1, 0.80, D1_C)]),
            3, _symbols())
        assert sum(s) == 1, f"one defect, three wordings, got {s}"

    def test_a_new_location_is_always_new(self):
        rows = [(0, 0.85, D1_A),
                (0, 0.85, "STA-04 misstates the confidence interval for `variance`.")]
        s = hierarchical_novelty_series(_entries(rows), 2, _symbols() + ["variance"])
        assert sum(s) == 2, "a finding at an unflagged location is new, always"


class TestTheThresholdIsWithinLocationOnly:
    """0.10 maximised separation across all archive pairs but FAILS here, because
    two defects on one listing share its vocabulary. Both numbers were right for
    the population they were measured on."""

    def test_the_loose_threshold_reproduces_the_blind_spot(self):
        s = hierarchical_novelty_series(
            _entries([(0, 0.85, D1_A), (0, 0.88, D2_A)]), 1, _symbols(),
            within_threshold=0.10)
        assert sum(s) == 1, "0.10 merges them — this is why the default is not 0.10"

    def test_the_shipped_default_separates_them(self):
        s = hierarchical_novelty_series(
            _entries([(0, 0.85, D1_A), (0, 0.88, D2_A)]), 1, _symbols())
        assert sum(s) == 2
        assert WITHIN_LOCATION_THRESHOLD == 0.20


class TestTheSignatureItself:
    def test_it_captures_hard_content_not_prose(self):
        sig = stem_signature(D1_A)
        assert "2016" in sig and "64" in sig and "AL-03" in sig and "dedup" in sig

    def test_rewordings_of_one_defect_are_similar(self):
        assert signature_similarity(stem_signature(D1_A), stem_signature(D1_B)) >= 0.20

    def test_distinct_defects_are_not(self):
        assert signature_similarity(stem_signature(D1_A), stem_signature(D2_A)) < 0.20

    def test_empty_input_is_not_similar_to_anything(self):
        assert signature_similarity(frozenset(), frozenset()) == 0.0


class TestItIsShadowUntilPromoted:
    def test_gating_defaults_off(self):
        assert RunnerConfig().hierarchical_novelty_convergence is False, (
            "this must not change any run's behaviour until a config promotes it")

    def test_the_threshold_is_configurable(self):
        assert RunnerConfig().hierarchical_within_threshold == 0.20

    def test_no_shipped_config_enables_it(self):
        import glob, json
        on = [f for f in glob.glob(str(Path(__file__).resolve().parents[1] /
                                       "exp*_configs/*.json"))
              if json.load(open(f)).get("hierarchical_novelty_convergence")]
        assert not on, f"promoted without evidence from a live run: {on}"

    def test_the_runner_records_it_in_shadow(self):
        src = (Path(__file__).resolve().parents[1] / "reference_runner_v3.py").read_text()
        assert 'result["hierarchical_crit_series"]' in src
        assert 'result["hierarchical_crit_series_is_gating"]' in src, (
            "a series recorded without saying whether it gated is how "
            "location_crit_shadow_history came to be actively misleading")

    def test_shadow_failure_cannot_kill_a_run(self):
        src = (Path(__file__).resolve().parents[1] / "reference_runner_v3.py").read_text()
        i = src.index('result["hierarchical_crit_series"]')
        window = src[max(0, i - 900):i + 900]
        assert "except Exception" in window and "hierarchical_crit_series_error" in window
