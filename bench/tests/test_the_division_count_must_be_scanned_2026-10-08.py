"""The division count is bounded, its cost is not monotone, and 5 prose figures were wrong.

THE FOUNDER'S INSIGHT, 2026-10-07: *"we clearly don't have infinit[e] divisions, we
have division 1, division 2, division 3, the Premier League. So the number of
possible leagues is finite."* And: *"either way the number is bounded, not
infinite."*

THIS FILE EXISTS BECAUSE THE FIGURES CAME FIRST AND THE PRODUCER CAME SECOND.
`experimental_notes/Rung_Promotion_Panel_Analysis_2026-10-08.md` was committed at
b4c897fb carrying 5 figures about the division scan -- a 52-to-182 range, 7 tiers
at 91 against 5 at 95, and 4 divisions as a local optimum at 68 -- with no script
behind any of them. When the scan was written, NONE reproduced. The guard below
pins the reproducing values so the same thing cannot happen again by the same
route, which is the founder's ruling of 2026-09-04: a number that exists only as
prose is a claim about evidence, not evidence.

Everything here CALLS the producer. `execute-do-not-grep`.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PRODUCER = (REPO / "bench" /
            "the_division_count_is_bounded_and_the_cost_is_not_monotone_2026-10-08.py")

#: The 5 figures the analysis note asserted, none of which reproduce. Kept as
#: data so the withdrawal is executable rather than narrated.
WITHDRAWN_FROM_THE_NOTE = {
    "cheapest_total_attempts": 52,
    "dearest_total_attempts": 182,
    "seven_divisions": 91,
    "five_divisions": 95,
    "four_divisions": 68,
}


@pytest.fixture(scope="module")
def M():
    spec = importlib.util.spec_from_file_location("div_scan", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["div_scan"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def scan(M):
    return M.claim_the_cost_of_climbing_is_bounded()


class TestTheScanIsBoundedAndFeasible:
    def test_every_division_count_in_range_meets_the_budget(self, scan):
        assert scan["every_tier_count_is_feasible"], scan
        assert scan["tier_range"] == [2, 14], scan["tier_range"]

    def test_both_tools_agree_at_every_division_count(self, scan):
        """SciPy's binomial tail against an exact mpmath sum, 13 times over."""
        assert scan["mpmath_agrees_everywhere"], scan

    def test_the_end_to_end_budget_actually_holds_at_every_count(self, scan):
        """The budget is the whole point; a scan that violates it is decoration."""
        for tiers, row in scan["per_tier_count"].items():
            assert row["end_to_end_capable"] >= 0.95 - 1e-9, (tiers, row)
            assert row["end_to_end_weak"] <= 0.01 + 1e-9, (tiers, row)


class TestTheCostCurveIsNotMonotoneUNDERTHERESTRICTION:
    """★ THE CONCLUSION THIS CLASS ONCE DEFENDED IS WITHDRAWN, 2026-10-08.

    It read: "THE LOAD-BEARING CLAIM. If the curve were monotone the answer would
    be 'as few divisions as possible' or 'as many as the bound allows', and no
    scan would be needed. Both of those are wrong."

    'As few as possible' is RIGHT. The non-monotonicity is real but is a property
    of the IDENTICAL-GATE restriction `smallest_gate` imposes, not of the problem:
    the budget constrains only the products of per-gate pass probabilities, so
    heterogeneous gates are admissible, and optimised over them the curve has 0
    downward steps. Found by the `fable` seat; re-derived independently in
    `scripts/the_division_count_is_derivable_2026-10-08.py`, which is where the
    live claim now lives.

    THE TESTS BELOW ARE KEPT AND NOT DELETED, with their scope corrected in the
    class name: they pin a true fact about the restricted family, which is what
    makes the restriction's cost measurable. What they must no longer be read as
    is evidence about how many divisions a ladder should have."""

    def test_the_curve_steps_both_ways_under_identical_gates(self, M):
        """True of the restricted family only. See the class docstring."""
        d = M.claim_the_cost_curve_is_not_monotone()
        assert not d["is_monotone"], d["costs"]
        assert d["steps_down"] > 0, (
            "no downward step means more divisions always cost more, and the "
            "scan would be unnecessary")
        assert d["steps_up"] > 0, d

    def test_more_divisions_sometimes_cost_strictly_less(self, M):
        d = M.claim_the_cost_curve_is_not_monotone()
        assert d["inversions_more_tiers_cost_less"] > 0, d
        for a, ca, b, cb in d["example_inversions"]:
            assert b > a and cb < ca, (a, ca, b, cb)


class TestTheFiveNoteFiguresAreWithdrawn:
    """MUTATION-GRADE IN THE OTHER DIRECTION: these assert the OLD values are
    WRONG. If a future edit made the producer print them, this file turns red and
    the note would be right after all -- which is the only honest way to pin a
    withdrawal."""

    def test_the_cheapest_is_not_52(self, scan):
        assert scan["cheapest_total_attempts"] != WITHDRAWN_FROM_THE_NOTE[
            "cheapest_total_attempts"]
        assert scan["cheapest_total_attempts"] == 19, scan

    def test_the_dearest_is_not_182(self, scan):
        assert scan["dearest_total_attempts"] != WITHDRAWN_FROM_THE_NOTE[
            "dearest_total_attempts"]
        assert scan["dearest_total_attempts"] == 72, scan

    def test_seven_divisions_do_not_cost_91_nor_undercut_five(self, scan):
        costs = scan["total_attempts_by_tier_count"]
        assert costs[7] != WITHDRAWN_FROM_THE_NOTE["seven_divisions"]
        assert costs[5] != WITHDRAWN_FROM_THE_NOTE["five_divisions"]
        assert costs[7] == 48 and costs[5] == 36, costs
        assert costs[7] > costs[5], (
            "the note's headline example had 7 divisions UNDERCUTTING 5; the "
            "scan has it the other way round, so that example was wrong even "
            "though non-monotonicity holds elsewhere")


class TestHisOwnFourDivisionsArePricedHonestly:
    def test_four_divisions_cost_30_and_are_not_a_local_minimum(self, M):
        d = M.claim_his_four_division_instinct()
        assert d["his_named_divisions"] == 4
        assert d["total_attempts_at_his_count"] == 30, d
        assert d["total_attempts_at_his_count"] != WITHDRAWN_FROM_THE_NOTE[
            "four_divisions"]
        assert not d["is_a_local_minimum"], (
            "the note said his instinct landed on a local optimum; 3 divisions "
            f"cost less, so it does not: {d['neighbours']}")
        assert 3 in d["tier_counts_strictly_cheaper"], d


class TestThePPassResultIsNotHiddenBecauseItIsAwkward:
    """A single gate is CHEAPEST on total attempts. That undercuts the tiered
    idea the brief is built on, so it must be asserted rather than left in prose
    where it can quietly disappear."""

    def test_a_single_gate_wins_on_total_attempts(self, M):
        d = M.claim_a_single_gate_cannot_meet_the_budget_cheaply()
        assert d["one_gate_is_cheapest"], d
        assert d["tiered_counts_that_beat_one_gate"] == [], d
        assert d["single_gate_total_attempts"] == 19, d

    def test_the_argmin_does_not_depend_on_scan_order(self, M):
        d = M.claim_the_bound_is_what_makes_this_answerable()
        assert d["argmin_is_order_free"], d
        assert d["distinct_argmins_over_shuffled_scans"] == 1, d


class TestTheProducerRunsFromTheCommandLine:
    def test_help_is_free_and_exits_clean(self):
        """A --help must never cost money, and must never dispatch."""
        import subprocess
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        assert "division" in (r.stdout + r.stderr).lower()
