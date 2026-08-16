"""A missing anchor must never establish that two findings computed the same value.

THE DEFECT THIS PINS, found 2026-08-16 by building the similarity function's
operating characteristic rather than by reading the code.

`quantities_agree` used to read:

    if a1 and a2 and a1 != a2:
        return _distinctive(v1)
    return True

so when EITHER anchor was empty the guard was skipped and the function returned
True. An anchorless quantity therefore matched any quantity of equal value — a
wildcard. Tier 3 (`outcome_agreement`) may only MERGE findings, never split them,
so a permissive match costs a real second defect: it is counted once, the gate
stops seeing it, and nothing downstream can tell the difference.

WHY IT WAS INVISIBLE. The tier's recorded justification is its ANSWER
distribution — Fisher exact p = 1.4e-07, and never once calling a same-defect
pair DIFFERENT. Both true, and neither measures the quantity that matters. Routed
through `identity_decision`, tier 3 changed the outcome on only 3 of 318 labelled
pairs, and all 3 were wrong. A statistic about opinions is not a statistic about
effects, and 36 green tests did not distinguish them.

WHY `_distinctive` IS NOT THE FIX. The observed collisions are all on 0.6, and
`_distinctive(0.6)` is True because 0.6 is not an integer. A distinctiveness
fallback passes it straight through. 0.6 in this codebase is a penalty-tier
CONFIGURATION CONSTANT that recurs across findings about the same module, which is
exactly the coincidental agreement the anchor exists to prevent. Distinctiveness
answers "could this value identify a computation?", not "does this value identify
THIS computation?" — and only the second question is the one being asked.

MEASURED COST OF THE FIX: none. See
`scripts/similarity_operating_characteristic.py`.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.convergence_location import (  # noqa: E402
    _distinctive,
    computed_outcomes,
    identity_decision,
    outcome_agreement,
    quantities_agree,
)


class TestAnchorlessCannotEstablishSameness:

    def test_a_missing_anchor_does_not_match_an_anchored_value(self):
        """The exact shape observed: `(0.6, '')` against `(0.6, 'penalty')`."""
        assert not quantities_agree((0.6, ""), (0.6, "penalty"))
        assert not quantities_agree((0.6, "penalty"), (0.6, ""))

    def test_both_anchors_missing_still_does_not_match(self):
        """Two findings that each failed anchor extraction know nothing about
        each other. Symmetric ignorance is not agreement."""
        assert not quantities_agree((0.6, ""), (0.6, ""))

    def test_the_distinctiveness_fallback_would_not_have_caught_this(self):
        """Guards the REASON for the fix, not just its effect.

        If someone later 'simplifies' the guard back to a distinctiveness test,
        this fails and says why: 0.6 passes `_distinctive` and is still a
        configuration constant, so distinctiveness cannot carry the decision.
        """
        assert _distinctive(0.6) is True
        assert not quantities_agree((0.6, ""), (0.6, "penalty"))

    def test_matching_anchors_still_agree(self):
        assert quantities_agree((0.6, "penalty"), (0.6, "penalty"))

    def test_different_anchors_still_agree_when_the_value_identifies_itself(self):
        """The `64 comparisons` / `64 inputs` case the guard was built for is
        untouched: two DIFFERENT anchors are still reconciled by distinctiveness."""
        assert quantities_agree((64.0, "comparisons"), (64.0, "inputs"))
        assert not quantities_agree((2.0, "inputs"), (2.0, "rounds"))

    def test_tolerance_still_applies_to_anchored_values(self):
        assert quantities_agree((109.128, "g/mol"), (109.13, "g/mol"))


class TestTheObservedExp47Collision:
    """The three pairs whose merge this fix removes.

    VERBATIM from the exp47 archive, not paraphrased. A first draft of this class
    used a hand-written approximation of C0063 and every assertion in it passed
    for the wrong reason — the paraphrase happened to carry an anchor the real
    text does not. The precondition test below is what caught that, and it is
    kept for the same reason.

    Note what C0063 actually is: a description CUT OFF MID-WORD at exactly 200
    characters, ending "...escape the 0.60 do". The anchor that would have
    disambiguated the 0.60 — the word following it — was removed by a length cap
    before the similarity function ever saw the finding. The wildcard is the
    proximate cause of the bad merge; the truncation is why there was nothing to
    match against.
    """

    C0063 = ("FINDING_ID: F006\nSEVERITY: 0.80\nFIND: eta_int_modulator's "
             "severe-tier 'all_isomorphic' gate ignores sibling_cosmetic_"
             "isomorphism reasons, allowing compliance-theatre alternatives to "
             "escape the 0.60 do")
    NEIGHBOUR = ("`eta_int_modulator` incorrectly short-circuits and returns "
                 "`1.0` if `record.compliant` is True, completely bypassing the "
                 "severe `0.60` penalty for near-copies and the `0.85` soft "
                 "penalty for mixed-admissibility alternatives.")

    def test_the_c0063_text_is_the_truncated_form_that_was_observed(self):
        """If this ever stops being 200 characters ending mid-word, the archive
        has been re-parsed and every number in this class must be re-derived."""
        assert len(self.C0063) == 200
        assert self.C0063.endswith("escape the 0.60 do")

    def test_the_anchorless_outcome_is_what_it_looks_like(self):
        """Precondition. If extraction changes and C0063 gains an anchor, the
        collision below is no longer the one that was observed and this class
        should be re-derived rather than trusted."""
        outs = computed_outcomes(self.C0063)
        assert any(a == "" for _v, a in outs), (
            f"expected an anchorless quantity in C0063, got {sorted(outs)}")

    def test_the_two_findings_no_longer_agree_on_a_computed_outcome(self):
        assert outcome_agreement(computed_outcomes(self.C0063),
                                 computed_outcomes(self.NEIGHBOUR)) != "SAME"

    def test_the_neighbour_is_therefore_counted_rather_than_merged_away(self):
        """The consequence that matters: a distinct defect keeps its count.

        Routed through `identity_decision` rather than re-implemented, so this
        breaks if the rule changes even when the helper does not.
        """
        syms = frozenset({"eta_int_modulator"})
        d0 = identity_decision(self.C0063, syms, [])
        from bench.convergence_location import Prior
        prior = Prior(d0.locations, d0.signature, d0.outcomes, "C0063")
        d1 = identity_decision(self.NEIGHBOUR, syms, [prior])
        assert d1.reason != "same_computed_outcome", (
            "tier 3 merged these again — the anchorless wildcard is back")


class TestTheGuardIsSymmetric:
    """Agreement is a relation; an asymmetric one would make the rule's answer
    depend on which finding happened to arrive first."""

    @pytest.mark.parametrize("q1,q2", [
        ((0.6, ""), (0.6, "penalty")),
        ((64.0, "comparisons"), (64.0, "inputs")),
        ((2.0, "inputs"), (2.0, "rounds")),
        ((0.85, "soft"), (0.85, "")),
    ])
    def test_order_does_not_change_the_answer(self, q1, q2):
        assert quantities_agree(q1, q2) == quantities_agree(q2, q1)
