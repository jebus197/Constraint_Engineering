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


class TestExhaustionDissolvesTheSelectionQuestion:
    """P-PASS, 2026-10-07: the attempt to BREAK the decomposition, and what it found.

    The decomposition assumes the tried set is "the first K rungs in the order".
    If an ERRORED rung did not consume its slot, a later seat would be reached
    instead and the realised SET would depend on which seats errored -- at which
    point coverage stops being order-invariant and the whole split collapses.

    It does not collapse: `route` applies the budget as a SLICE,
    `list(rungs)[:_budget]`, so an errored rung is already inside the slice and
    `continue` does not buy a replacement.

    THE SAME LINES CARRY THE FOUNDER'S RULING OF 2026-10-06, verbatim in
    `bench/routing.py`: *"I don't think there should be a cap at all. If it's a
    measured statistic, along with capability fingerprinting then the problem
    should run until it is either resolved, or the ladder is exhausted."*

    Under `max_rungs=0` the tried set IS the whole ladder. Coverage is then a
    CONSTANT, the selection question disappears, and only spend remains -- which
    is exactly the problem the cross-multiplied key solves optimally. So his
    ruling dissolves the tension; the cap of 2 is what keeps it alive.

    These tests CALL `route` with stub seats. No network, no spend.
    """

    @staticmethod
    def _route(max_rungs, erroring=()):
        import importlib.util
        spec = importlib.util.spec_from_file_location("rt_pp", REPO / "bench" / "routing.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["rt_pp"] = mod
        spec.loader.exec_module(mod)
        ladder = list(mod.DEFAULT_FALSIFIER_STRENGTH)
        seen = []

        def resolve(model, _f):
            seen.append(model)
            return "" if model in erroring else "assert False"

        res = mod.route(
            {"id": "PP", "description": "d", "model": "Nobody", "falsifier_code": ""},
            ladder, [], resolve, lambda _c: "REFUTED", lambda _a, _b: 0.0,
            max_rungs=max_rungs, self_rung_enabled=False)
        return ladder, seen, res

    def test_an_errored_rung_does_not_free_a_slot(self):
        """The falsification attempt. If this fails, the decomposition is wrong."""
        ladder, seen, _ = self._route(2, erroring=("Codex",))
        assert seen == ladder[:2], (
            "an errored rung bought a replacement, so the realised set depends on "
            "WHO errored and coverage is no longer order-invariant")

    def test_two_errors_still_consume_exactly_two_rungs(self):
        """Both of the 2 available slots error, and no 3rd seat is reached.

        The erroring set is read from the ladder this call actually uses, so the
        test cannot pass because it named seats that were never on it.
        """
        ladder, _, _ = self._route(2)
        ladder2, seen, res = self._route(2, erroring=tuple(ladder[:2]))
        assert ladder2 == ladder
        assert len(seen) == 2 and res.rungs_tried == 2, (seen, res.rungs_tried)
        assert seen == ladder[:2]

    def test_the_cap_truncates_to_exactly_K(self):
        ladder, seen, res = self._route(2)
        assert seen == ladder[:2] and res.rungs_tried == 2
        assert len(ladder) > 2, "with no truncation there is no selection question"

    def test_max_rungs_zero_reaches_every_rung(self):
        """His ruling, executed: 0 means exhaust, not 'try nothing'."""
        ladder, seen, res = self._route(0)
        assert seen == ladder, (seen, ladder)
        assert res.rungs_tried == len(ladder)

    def test_under_exhaustion_coverage_is_constant_so_only_spend_remains(self, M):
        """The set is fixed, so prod(1-p_i) cannot be influenced by any ordering."""
        from fractions import Fraction
        import itertools as it
        ladder, seen, _ = self._route(0)
        p = {s: Fraction(50 + 7 * i, 100) for i, s in enumerate(ladder)}
        vals = {M.failure_probability(o, p) for o in it.permutations(seen)}
        assert len(vals) == 1, (
            "coverage varied under exhaustion, which would mean the set is not fixed")
