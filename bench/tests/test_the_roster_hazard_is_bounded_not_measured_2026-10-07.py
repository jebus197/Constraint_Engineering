"""The spurious-convergence ratio is an upper bound, and its guard says so.

P-PASS OF THIS SESSION'S OWN WORK. `a_shrinking_roster_converges_sooner_2026-10-07.py`
reports a factor of 8.49986 for the 6-seat-to-4-seat change, and that figure was
carried into a dispatched panel brief. It assumes INDEPENDENT seats, which is the
most favourable case for the claim -- and seats in a round receive a
byte-identical brief and the same target, so they are not independent.

These tests CALL both scripts. The mutation tests are the load-bearing ones: a
guard that passes whether or not the correlation matters would establish nothing.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def S():
    return _load("shrink_r", "bench/a_shrinking_roster_converges_sooner_2026-10-07.py")


@pytest.fixture(scope="module")
def C():
    return _load(
        "corr_r",
        "bench/the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py")


class TestTheHazardIsRealAtEveryCorrelation:
    """The direction must never reverse, or the design argument collapses."""

    @pytest.mark.parametrize("rho", [0.0, 0.1, 0.3, 0.5, 0.8])
    def test_a_smaller_roster_always_goes_quiet_sooner(self, C, rho):
        assert C.ratio_exact_beta_binomial(rho) > 1.0, (
            f"at rho={rho} a 4-seat roster is no quicker to go quiet than a "
            "6-seat one, which would retire the whole hazard")

    def test_the_independent_case_is_the_largest(self, C):
        """Independence is the upper bound, so no correlation can inflate it."""
        base = C.ratio_exact_beta_binomial(0.0)
        for rho in (0.1, 0.3, 0.5, 0.8):
            assert C.ratio_exact_beta_binomial(rho) <= base + 1e-9, (
                f"rho={rho} exceeded the independent ratio, so independence is "
                "not the bound this claim was reported as")


class TestTheQuantitativeClaimIsSensitive:
    """MUTATION: if correlation did not matter, the brief's figure would stand."""

    def test_correlation_shrinks_the_ratio_substantially(self, C):
        hi = C.ratio_exact_beta_binomial(0.0)
        lo = C.ratio_exact_beta_binomial(0.5)
        assert hi / lo > 3.0, (
            "if correlation barely moved the ratio, reporting 8.49986 without a "
            "rho would be harmless -- it is not")

    def test_two_tools_agree_at_the_midpoint(self, C):
        exact = C.ratio_exact_beta_binomial(0.3)
        sim, _, _ = C.ratio_simulated(0.3, batches=120, seed=7)
        assert abs(exact - sim) / exact < 0.10, (exact, sim)

    def test_the_independent_closed_form_matches_the_shrink_script(self, S, C):
        """The 2 scripts must not disagree about the same quantity."""
        d = S.claim_a_smaller_roster_goes_quiet_sooner()
        assert abs(d["fold_increase_6_to_4"] - C.ratio_independent()) < 1e-6


class TestTheNecessityDoesNotDependOnTheRatio:
    """The design argument must survive even if rho turns out to be high."""

    def test_the_count_alone_cannot_separate_the_two_causes(self, S):
        d = S.claim_the_gate_cannot_distinguish_the_two_causes()
        assert d["distinguishable_from_the_count_alone"] is False, d
        assert d["search_for_a_distinguishing_value"] == "unsat"

    def test_recording_the_live_roster_makes_them_exclusive(self, S):
        d = S.claim_declaring_the_roster_restores_the_distinction()
        assert d["the_two_are_mutually_exclusive"] is True, d

    def test_dropout_is_not_a_rare_event(self, S):
        """If dropout were rare the whole requirement would be low priority."""
        d = S.claim_dropout_probability_over_a_run(trials=4000)
        assert d[0.01]["closed_form"] > 0.30, d[0.01]
        assert all(v["all_three_agree"] for v in d.values()), d


class TestTheDispatchedBriefWasNotRewritten:
    """Editing a dispatched brief would break the star-topology grouping key.

    The key is the sha256 of BRIEF.md, so a mid-flight rewrite makes the recorded
    brief differ from the one the seats received. The amendment travels to the
    joint round instead, and this test fails if the brief is ever quietly changed
    to carry the correlation caveat.
    """

    def test_the_brief_still_states_the_independent_figure(self):
        b = (REPO / "bench" / "logs"
             / "dynamic_roster_and_derived_ladder_2026-10-07" / "BRIEF.md")
        if not b.is_file():
            pytest.skip("brief directory not present in this checkout")
        text = b.read_text()
        assert "8.49986" in text, (
            "the dispatched brief no longer carries the figure the seats were "
            "actually given; the blind round's record and its brief disagree")

    def test_the_amendment_exists_as_its_own_committed_script(self):
        p = (REPO / "bench"
             / "the_spurious_convergence_ratio_depends_on_correlation_2026-10-07.py")
        assert p.is_file(), (
            "the correction must travel with a script, or it is a claim about "
            "evidence rather than evidence")
