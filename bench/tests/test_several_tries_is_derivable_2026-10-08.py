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


class TestTheSearchIsMinimalAndTheRungCountIsNotFree:
    """P-PASS 2026-10-08, 2 attacks on the derivation itself.

    ATTACK 1: `derive_rung_sample` takes the FIRST feasible (n, k) rather than
    proving it minimal. Exhaustive search confirms n = 19 IS the true minimum at 5
    rungs, and the feasible k-set at that n is contiguous -- in fact a single
    value, 11 -- so scanning k upward returns the smallest feasible one. The
    monotonicity the search relies on holds: the pass rate falls in k for both the
    good and the weak model, so the feasible set is an interval.

    ATTACK 2, AND IT FOUND SOMETHING NOT ASKED FOR. The founder never specified a
    rung count. As rungs increase the PER-RUNG sample falls, because each rung's
    share of the error budget loosens as the n-th root, but the TOTAL cost of
    climbing rises:

        2 rungs   n=26  k=17   52 attempts to the top
        3 rungs   n=21  k=13   63
        5 rungs   n=19  k=11   95
        8 rungs   n=15  k= 8  120
       12 rungs   n=12  k= 6  144
       20 rungs   n=11  k= 5  220

    So rung count is a real trade-off and not a free parameter: few rungs are
    cheap to climb but discriminate difficulty coarsely, many rungs discriminate
    finely but cost 4.2 times as much to climb at 20 against 2. It connects to the
    cap: `rungs_tried` cannot exceed the cap, so at a cap of 2 the difficulty label
    has at most 3 levels, and a fine-grained ladder needs the cap lifted FIRST.
    """

    def test_the_returned_sample_is_the_true_minimum(self, M):
        from scipy.stats import binom
        p_good, p_bad, fn, fp, rungs = 0.80, 0.50, 0.05, 0.01, 5
        a = (1 - fn) ** (1.0 / rungs)
        b = fp ** (1.0 / rungs)

        def ok(n, k):
            return (float(binom.sf(k - 1, n, p_good)) >= a
                    and float(binom.sf(k - 1, n, p_bad)) <= b)

        true_min = next(n for n in range(1, 200)
                        if any(ok(n, k) for k in range(1, n + 1)))
        got = M.derive_rung_sample()["attempts_per_rung"]
        assert got == true_min, (got, true_min)

    def test_the_feasible_success_count_is_an_interval(self, M):
        """The search scans k upward, which is only valid if the set is contiguous."""
        from scipy.stats import binom
        d = M.derive_rung_sample()
        n, rungs = d["attempts_per_rung"], 5
        a, b = (1 - 0.05) ** (1 / rungs), 0.01 ** (1 / rungs)
        ks = [k for k in range(1, n + 1)
              if float(binom.sf(k - 1, n, 0.80)) >= a
              and float(binom.sf(k - 1, n, 0.50)) <= b]
        assert ks, "no feasible k at the returned n"
        assert ks == list(range(min(ks), max(ks) + 1)), ks
        assert d["successes_required"] == min(ks), (d["successes_required"], ks)

    def test_more_rungs_cost_more_in_total_even_as_each_gets_cheaper(self, M):
        few = M.derive_rung_sample(rungs=2)
        many = M.derive_rung_sample(rungs=12)
        assert few["feasible"] and many["feasible"]
        assert many["attempts_per_rung"] < few["attempts_per_rung"], (
            "per-rung sample did not fall as rungs rose, so the budget is not "
            "being divided as the derivation assumes")
        assert many["attempts_per_rung"] * 12 > few["attempts_per_rung"] * 2, (
            "total climbing cost did not rise with rung count; if rungs were free "
            "the count would not be a design decision")


class TestAnIntervalBelongsOnlyOnAMeasurement:
    """A confidence interval on exact arithmetic is nobody's uncertainty.

    FOUND BY THE cc2 SEAT, 2026-10-08, against CC1's own brief and scripts: *"the
    brief applies Wilson intervals to three deterministic quantities (tuple share,
    starved-model count, and by extension any fixed-order/fixed-cap allocation). An
    interval on a quantity with no estimator reads as measured uncertainty to the
    next reader and is nobody's uncertainty."*

    It is right. A 6-name tuple ordering 6 of 70 seats is 3/35 exactly; the
    starvation count under a deterministic rule is the same on every run with every
    seed. Neither is sampled.

    THE CORRECTION MUST NOT BE OVERAPPLIED, which is what these tests hold. An
    interval still belongs on the genuinely measured rates: the intra-round
    correlation, the per-seat per-round critical rate, and the share of archived
    routing records with more than 1 rung available. Those are samples of observed
    runs.
    """

    def test_the_tuple_share_is_reported_as_exact_not_estimated(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cold", REPO / "bench" / "the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["cold"] = m
        spec.loader.exec_module(m)
        d = m.claim_the_tuple_coverage_collapses()
        for n, row in d.items():
            assert "wilson_on_the_share" not in row, (
                f"n={n} still carries an interval on exact arithmetic")
            assert row["is_a_measurement"] is False
            assert "share_exact" in row

    def test_the_share_really_is_deterministic(self):
        """MUTATION: if it varied, an interval would have been appropriate."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cold2", REPO / "bench" / "the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["cold2"] = m
        spec.loader.exec_module(m)
        a = m.claim_the_tuple_coverage_collapses((70,))
        b = m.claim_the_tuple_coverage_collapses((70,))
        assert a == b, "the share varied between calls, so it IS sampled"
        from fractions import Fraction
        assert a[70]["share_exact"] == str(Fraction(6, 70))

    def test_an_interval_is_retained_where_the_quantity_is_sampled(self):
        """The archive share of multi-rung records is a sample and keeps its interval."""
        src = (REPO / "bench" / "tests"
               / "test_the_promotion_criterion_is_the_weak_point_2026-10-08.py").read_text()
        assert "wilson(multi, n)" in src, (
            "the interval was stripped from a genuinely measured archive share; "
            "the correction has been overapplied")
