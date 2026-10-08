"""What "several tries" must mean is derivable, and 19 is a floor not an answer.

THE FOUNDER'S CLARIFICATION, 2026-10-08: *"I didn't originally intend to say
models only needed one successful try. They should demonstrate their capability
over several tries with different problems, before being considered for
promotion."*

THAT WITHDRAWS THE EARLIER CRITICISM. The figures that condemned the rung ladder
-- a 0.90 model kept out of the top rung 0.40951 of the time, 0.59302 once rungs
harden -- were computed for ONE success per rung and do not apply.

WHAT REPLACES IT IS A DERIVATION. Against a 5% false-negative budget for a model
deserving promotion (0.80) and a 1% false-positive budget for one that does not
(0.50), over 5 rungs: 19 attempts per rung with 11 successes required. A 0.80
model then reaches the top 0.967152 of the time and a 0.50 model 0.00355962.

AND THE DERIVATION'S OWN ASSUMPTION IS FALSE HERE, which is what these tests
hold. It assumes INDEPENDENT attempts. This project's measured intra-round
correlation is 0.2360 within-experiment, 0.2753 on real runs, and 0.4060 to 0.4903
pooled. At the real-run figure with 3 attempts per finding the design effect is
1.5506, so 19 independent-equivalent attempts need 30 actual ones -- a 55.06%
inflation. 19 is a FLOOR. The method stands; the number does not.

THE FOOTBALL ANALOGY BREAKS IN ONE PLACE AND IT IS THE PLACE THAT MATTERS.
Football promotion is RELATIVE, so a weak division still promotes somebody.
Measured over 2000 trials with 700 uniformly weak models, relative promotion
elevates one to the hardest rung in 2000 of 2000 trials, Wilson [0.998083,
1.000000], while an absolute capability threshold elevates none, Wilson [0.000000,
0.001917]. Rungs map to task difficulty rather than to a fixed-size division, so
the threshold must be absolute -- otherwise a uniformly weak roster sends its
least-weak member to the hardest problem, which is the founder's Riemann objection
restated.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def M():
    spec = importlib.util.spec_from_file_location(
        "several", REPO / "bench" / "what_several_tries_has_to_mean_2026-10-08.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["several"] = m
    spec.loader.exec_module(m)
    return m


class TestTheRuleIsDerivedNotChosen:
    def test_a_feasible_sample_exists_at_the_stated_budgets(self, M):
        d = M.derive_rung_sample()
        assert d["feasible"], d
        assert d["attempts_per_rung"] > 1, (
            "if 1 attempt satisfied the budgets, the founder's clarification "
            "would have changed nothing")
        assert d["successes_required"] < d["attempts_per_rung"], (
            "requiring every attempt to succeed is the one-success rule in "
            "disguise, scaled up")

    def test_it_meets_both_error_targets(self, M):
        d = M.derive_rung_sample()
        assert d["overall_P_good_model_reaches_top"] >= 0.95, d
        assert d["overall_P_weak_model_reaches_top"] <= 0.01, d

    def test_the_clarification_removes_the_earlier_defect(self, M):
        d = M.claim_one_success_was_the_whole_problem()
        assert d["the_clarification_removes_the_defect"] is True, d
        one = d["one_success_P_reaches_top"][0.80]
        derived = d["derived_rule"]["overall_P_good_model_reaches_top"]
        assert derived > one * 2, (
            f"derived {derived} barely beats one-success {one}; the "
            "clarification would then be cosmetic")

    def test_tightening_the_budget_demands_a_larger_sample(self, M):
        """MUTATION: the derivation must respond to its inputs."""
        loose = M.derive_rung_sample(fn_target=0.20, fp_target=0.10)
        tight = M.derive_rung_sample(fn_target=0.01, fp_target=0.001)
        assert loose["feasible"] and tight["feasible"]
        assert tight["attempts_per_rung"] >= loose["attempts_per_rung"], (
            loose["attempts_per_rung"], tight["attempts_per_rung"])


class TestCorrelationInflatesTheSample:
    @pytest.mark.parametrize("rho,m", [(0.2360, 3), (0.2753, 3), (0.4060, 3)])
    def test_the_design_effect_exceeds_one(self, rho, m):
        deff = 1 + (m - 1) * rho
        assert deff > 1.0
        assert deff > 1.4, (
            f"design effect {deff:.4f} at rho={rho}; if correlation barely "
            "mattered the independent figure could be used as-is")

    def test_nineteen_is_a_floor_not_an_answer(self, M):
        d = M.derive_rung_sample()
        n_ind = d["attempts_per_rung"]
        inflated = n_ind * (1 + (3 - 1) * 0.2753)
        assert math.ceil(inflated) > n_ind, (n_ind, inflated)
        assert math.ceil(inflated) >= 29, (
            "the real-run correlation must demand materially more attempts, or "
            "this whole correction is noise")


class TestTheAnalogyBreaksOnRelativePromotion:
    def test_relative_promotion_elevates_someone_from_a_weak_field(self, M):
        d = M.claim_relative_promotion_fails_a_uniformly_weak_roster(
            n_models=200, trials=400)
        rel = int(d["relative_promotes_someone"].split()[0])
        abs_ = int(d["absolute_promotes_someone"].split()[0])
        assert rel > abs_, d
        assert abs_ == 0, (
            "an absolute threshold promoted from a uniformly weak field, so it "
            "is no safer than the relative rule and the distinction is empty")

    def test_the_season_length_is_the_right_order(self, M):
        d = M.claim_the_football_season_is_the_right_order_of_magnitude()
        assert d["same_order_of_magnitude"] is True, d
