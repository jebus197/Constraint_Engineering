"""The 2 convergence-gate arms are POSITIVELY DEPENDENT, so one cannot cover the other.

THE FOUNDER'S RULING, 2026-10-07, on a figure a panel seat produced and nobody
could reproduce: *"the absolute false quiet chance of 0.1159 at full roster,
which no roster aware fix addresses. # Fix it."*

THIS FILE IS NOT AN ARGUMENT FOR DEMOTING GAMMA AND MUST NEVER BE READ AS ONE.
Gamma is load-bearing in this project and remains a REQUIRED arm of the gate. The
finding is narrower and is about INDEPENDENCE, not about worth: gamma measures the
flattening of the critical-finding curve, and quiet rounds are what flatten it, so
the 2 arms rise together. A gate whose arms are dependent is still a 2-armed gate;
what it is not is a gate whose false-positive rate is the product of 2 small
numbers. The practical consequence is that the quiet-window arm's rate is the
gate's rate, so the only levers on it are the required quiet run and the seat
count -- which is what the seat who found the figure said, now measured.

EVERYTHING HERE CALLS THE PRODUCER AND THE PRODUCER CALLS THE REAL GATE. A test
that read `_check_gamma_alt_convergence`'s source could only establish that the
gate describes itself consistently; it could not see that gamma was above its
threshold in every premature window the archive contains. `execute-do-not-grep`.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PRODUCER = REPO / "bench" / "the_false_quiet_rate_is_not_the_gates_rate_2026-10-08.py"


@pytest.fixture(scope="module")
def M():
    spec = importlib.util.spec_from_file_location("fq_rate", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["fq_rate"] = m
    spec.loader.exec_module(m)
    return m


class TestTheFigureNowTravelsWithItsScript:
    """0.1159 reached the founder in prose with no producer. It has one now."""

    def test_the_closed_form_and_a_simulation_both_give_it(self, M):
        d = M.claim_the_0_1159_figure_reproduces()
        assert d["reproduces_0_1159"], d
        assert d["two_tools_agree_to"] < 1e-3, d

    def test_a_smaller_roster_goes_quiet_more_easily(self, M):
        """The ordering is the whole hazard; if it inverted, nothing would hold."""
        by = M.claim_the_0_1159_figure_reproduces()["by_roster_size"]
        seq = [by[n] for n in (6, 5, 4, 3, 2, 1)]
        assert seq == sorted(seq), by


class TestTheArchiveAgreesWithoutAnyModel:
    def test_the_model_value_sits_inside_the_measured_interval(self, M):
        """2 independent routes to the same number is what makes it a figure."""
        d = M.claim_the_empirical_rate_agrees_and_needs_no_model()
        assert d["model_sits_inside_the_empirical_interval"], d
        at3 = d["by_required_quiet_run"][3]
        assert at3["opportunities"] > 50, (
            f"only {at3['opportunities']} opportunities -- too few to carry a "
            "rate, so the collector has probably stopped matching the archive")

    def test_lengthening_the_quiet_run_monotonically_lowers_the_rate(self, M):
        d = M.claim_the_empirical_rate_agrees_and_needs_no_model()
        rows = d["by_required_quiet_run"]
        rates = [rows[k]["rate"] for k in sorted(rows)]
        assert all(b <= a + 1e-9 for a, b in zip(rates, rates[1:])), rates
        assert d["first_k_with_no_premature_window"] is not None, rows


class TestGammaBlockedNoneOfThem:
    """THE LOAD-BEARING TEST. If gamma had blocked even some of the premature
    windows, the joint rate would be below the quiet arm's rate and the founder's
    'fix it' could be answered by doing nothing."""

    def test_the_real_gate_fires_on_every_premature_window(self, M):
        d = M.claim_gamma_does_not_cut_the_joint_rate()
        assert d["with_a_recorded_gamma"] >= 20, (
            f"only {d['with_a_recorded_gamma']} windows carry a gamma; a smaller "
            "set cannot support the claim")
        assert d["gamma_blocked_none"], d
        assert d["gate_fire_rate"] == 1.0, d

    def test_gamma_was_above_its_threshold_in_all_of_them(self, M):
        d = M.claim_gamma_does_not_cut_the_joint_rate()
        assert d["gamma_above_threshold_on"] == d["with_a_recorded_gamma"], d
        assert d["gamma_alt_threshold"] == 0.3, (
            "the threshold moved; the whole measurement is relative to it")

    def test_every_window_names_the_report_it_came_from(self, M):
        """A rate with no traceable members is not evidence."""
        d = M.claim_gamma_does_not_cut_the_joint_rate()
        assert len(d["detail"]) == d["with_a_recorded_gamma"], d
        for row in d["detail"]:
            assert row["report"].endswith(".json"), row
            assert isinstance(row["round"], int), row


class TestTheMechanismIsMeasuredNotAsserted:
    """WHY gamma does not bite, so the finding cannot be waved away as a fluke
    of 23 rounds."""

    def test_gamma_is_higher_inside_a_quiet_run(self, M):
        d = M.claim_the_two_arms_are_positively_dependent()
        assert d["gamma_is_higher_inside_a_quiet_run"], d
        assert d["median_gamma_in_a_quiet_run"] > d["median_gamma_elsewhere"], d
        assert d["p_one_sided_greater"] < 0.05, d

    def test_both_rank_computations_agree(self, M):
        d = M.claim_the_two_arms_are_positively_dependent()
        assert d["manual_u_agrees"], d


class TestTheProposalIsAProposal:
    def test_it_names_a_k_and_refuses_to_apply_it(self, M):
        d = M.claim_the_required_run_that_would_hold_a_target(0.05)
        assert d["current_required_run"] == 3
        assert d["smallest_k_meeting_the_target_on_the_point_estimate"] == 5, d
        assert d["smallest_k_whose_upper_confidence_bound_meets_it"] == 7, d
        assert "PROPOSED" in d["status"] and "Not applied" in d["status"], d

    def test_the_conservative_answer_is_never_cheaper_than_the_point_estimate(self, M):
        """If the upper bound asked for LESS than the point estimate, one of the
        2 is being read off the wrong end of the interval."""
        d = M.claim_the_required_run_that_would_hold_a_target(0.05)
        assert (d["smallest_k_whose_upper_confidence_bound_meets_it"]
                >= d["smallest_k_meeting_the_target_on_the_point_estimate"]), d


class TestTheProducerIsRunnableAndFree:
    def test_help_costs_nothing_and_exits_clean(self):
        import subprocess
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        assert "quiet" in (r.stdout + r.stderr).lower()
