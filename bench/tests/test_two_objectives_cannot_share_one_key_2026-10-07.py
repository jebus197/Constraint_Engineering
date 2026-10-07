"""The ladder has 2 objectives, and no single sort key is the optimum of both.

RAISED BY THE FOUNDER, 2026-10-07: *"This leaves the tension in place? My
solution, your solution and Astra's did not dissolve it?"* He was right. This
file holds the reason, so the answer cannot drift back into "what is the ONE
correct order".

Everything here CALLS `bench/why_one_ordering_cannot_serve_both_objectives_2026-10-07.py`
rather than asserting on its text, per `execute-do-not-grep`. The mutation
tests matter most: a guard that passes against a WRONG comparator is not a
guard, so 2 tests below check that the wrong rules genuinely fail.
"""
from __future__ import annotations

import importlib.util
import itertools
import sys
from fractions import Fraction
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def M():
    spec = importlib.util.spec_from_file_location(
        "two_obj", REPO / "bench" /
        "why_one_ordering_cannot_serve_both_objectives_2026-10-07.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["two_obj"] = m
    spec.loader.exec_module(m)
    return m


class TestTheTwoObjectivesAreGenuinelyDifferent:
    def test_coverage_does_not_depend_on_order(self, M):
        d = M.claim_coverage_is_order_invariant()
        assert d["holds"], d
        assert d["sympy_mismatches"] == 0
        assert d["distinct_exact_values"] == 1

    def test_spend_does_depend_on_order(self, M):
        """If spend were order-free too there would be no tension to dissolve."""
        p = {0: Fraction(1, 10), 1: Fraction(9, 10)}
        c = {0: Fraction(100), 1: Fraction(1)}
        spends = {M.expected_spend(o, p, c) for o in itertools.permutations(p)}
        assert len(spends) > 1, "spend must be order-sensitive or the claim is empty"

    def test_the_optimal_sets_differ_under_the_live_cap(self, M):
        d = M.claim_the_two_objectives_have_different_optima(2)
        assert d["sets_differ"], d
        assert d["fold_worse"] > 1.0, (
            "if the spend-optimal set were no worse on coverage, one key would do")


class TestTheComparatorIsTheRightOne:
    def test_z3_finds_no_counterexample_in_either_direction(self, M):
        d = M.claim_spend_is_minimised_by_the_cross_multiplied_key()
        assert d["z3_counterexample_search"] == "unsat", d
        assert d["z3_converse_search"] == "unsat", d
        assert d["brute_force_misses"] == 0, d

    def test_a_probability_only_key_is_NOT_spend_optimal(self, M):
        """MUTATION: order by p descending and spend goes up.

        This is the test that would fail if the two objectives really collapsed
        into one, so it is the load-bearing one in this file.
        """
        p = {"strong": Fraction(9, 10), "weak": Fraction(1, 2)}
        c = {"strong": Fraction(100), "weak": Fraction(1)}
        by_p = ("strong", "weak")
        by_key = ("weak", "strong")
        assert M.expected_spend(by_key, p, c) < M.expected_spend(by_p, p, c)

    def test_a_cost_only_key_is_NOT_coverage_optimal(self, M):
        """MUTATION: pick the cheapest 2 and the finding is likelier to survive."""
        p = {"a": Fraction(5, 100), "b": Fraction(10, 100), "c": Fraction(80, 100)}
        cheapest_two = ("a", "b")
        strongest_two = ("b", "c")
        assert (M.failure_probability(strongest_two, p)
                < M.failure_probability(cheapest_two, p))


class TestFreeSeatsCollapseTheOrderingQuestion:
    def test_every_order_of_free_seats_costs_the_same(self, M):
        d = M.claim_spend_is_vacuous_among_free_seats()
        assert d["all_zero"] and not d["ordering_objective_is_informative"], d


class TestTheLiveConfigurationIsWhatWeThinkItIs:
    def test_the_cap_is_2_and_nothing_overrides_it(self, M):
        d = M.claim_the_cap_is_live()
        assert d["routing_max_rungs_default"] == 2, d
        assert d["configs_pinning_the_cap"] == 0, d
        assert d["experiment_configs"] > 0, (
            "0 configs found means the search is broken, not that none exist -- "
            "this is the exact defect the first version of the script had")

    def test_the_legacy_alias_is_counted(self, M):
        """`take_up_slack_enabled` maps onto `routing_enabled`.

        Counting the literal key alone gives 5; the effective count is larger.
        A regression here silently shrinks the population the finding applies to.
        """
        d = M.claim_the_cap_is_live()
        assert d["configs_with_routing_effectively_on"] > 5, d

    def test_the_cap_leaves_seats_unasked(self, M):
        d = M.claim_the_cap_truncates_the_ladder()
        assert d["seats_never_asked"] == d["ladder_length"] - d["cap"]
        assert d["seats_never_asked"] > 0, (
            "with no truncation the question is sequencing, not selection")

    def test_a_free_seat_is_missing_from_the_ladder(self, M):
        """Recorded as a FACT, not asserted as desirable.

        `fable` is free and is not a rung. Whether it should be is the founder's
        ruling; this test fails if the fact changes, so the note cannot go stale.
        """
        d = M.claim_the_cap_truncates_the_ladder()
        assert d["free_seats_absent_from_the_ladder"] == ["fable"], d
        assert d["free_rungs"] == ["CC2"], d

    def test_free_seats_are_read_from_live_code_not_a_log_copy(self, M):
        d = M.claim_the_cap_is_live()
        decls = d["free_seats_declaration"]
        assert decls, "no live declaration found"
        for rel, _ in decls:
            parts = rel.split("/")
            assert "logs" not in parts and "worktrees" not in parts, (
                f"{rel} is a harvested copy, not live code")
