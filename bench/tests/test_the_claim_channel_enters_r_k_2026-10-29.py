#!/usr/bin/env python3
"""The claim channel enters R_k as a multiplier, bounded, and inert by default.

HIS RULING, 2026-10-29, annotation 8 of
`Responses/Decisions_Awaiting_You_2026-10-29.txt`: *"I accept your
recommendation. fr"*, choosing R_k as the term and a multiplier as the form, by
analogy with the section 7.7 verification fact he had already ruled on.

THE PROPERTY THAT MATTERS MOST IS THE FIRST ONE TESTED: at the live weight of 0
the channel changes NOTHING, so promoting it out of `informative_only` remains a
separate decision resting on the commissioning run this module's own header
requires. The arithmetic is built and proved; it is not switched on.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.claim_ledger import (  # noqa: E402
    CLAIM_CHANNEL_MAX_WEIGHT, CLAIM_CHANNEL_WEIGHT, Claim, ClaimLedger,
    apply_claim_channel, claim_channel_coverage, claim_channel_factor)


def _ledger(confirmed: int, refuted: int = 0, routed: int = 0) -> ClaimLedger:
    led = ClaimLedger(target="t")
    for i in range(confirmed):
        led.add(Claim(f"c{i}", f"a confirmed claim number {i} about the target",
                      decidable=True, falsifier="f", verdict="CONFIRMED"))
    for i in range(refuted):
        led.add(Claim(f"r{i}", f"a refuted claim number {i} about the target",
                      decidable=True, falsifier="f", verdict="REFUTED"))
    for i in range(routed):
        led.add(Claim(f"u{i}", f"a claim number {i} nothing could decide",
                      decidable=False))
    return led


class TestTheDefaultPathIsUnchanged:
    def test_the_live_weight_is_zero(self):
        assert CLAIM_CHANNEL_WEIGHT == 0.0, (
            "the channel has been switched on; promotion out of informative_only "
            "needs the commissioning run, not a constant edit")

    def test_at_the_live_weight_r_k_is_untouched(self):
        rep = _ledger(confirmed=3).report()
        assert rep["claim_channel_coverage"] == 1.0
        for r_k in (0.0, 0.1, 0.308, 0.75, 1.0):
            assert apply_claim_channel(r_k, rep) == r_k

    def test_the_ledger_is_still_declared_informative_only(self):
        assert ClaimLedger.informative_only is True


class TestTheFactorsAlgebra:
    def test_full_coverage_at_the_ceiling_halves_the_risk(self):
        rep = _ledger(confirmed=4).report()
        assert claim_channel_factor(rep, CLAIM_CHANNEL_MAX_WEIGHT) == pytest.approx(0.5)
        assert apply_claim_channel(0.308, rep, CLAIM_CHANNEL_MAX_WEIGHT) == pytest.approx(0.154)

    def test_zero_coverage_leaves_risk_unchanged_at_any_weight(self):
        rep = _ledger(confirmed=0, refuted=2, routed=1).report()
        assert rep["claim_channel_coverage"] == 0.0
        assert claim_channel_factor(rep, CLAIM_CHANNEL_MAX_WEIGHT) == 1.0
        assert apply_claim_channel(0.42, rep, CLAIM_CHANNEL_MAX_WEIGHT) == pytest.approx(0.42)

    def test_a_refuted_claim_contributes_no_reduction(self):
        """It does not inflate R_k either: the fault it reveals is already a
        finding carried by the detection term, and adding it here counts twice."""
        only_confirmed = _ledger(confirmed=1).report()
        with_refuted = _ledger(confirmed=1, refuted=3).report()
        assert only_confirmed["claim_channel_coverage"] == 1.0
        assert with_refuted["claim_channel_coverage"] == pytest.approx(0.25)
        assert (apply_claim_channel(0.5, with_refuted, CLAIM_CHANNEL_MAX_WEIGHT)
                > apply_claim_channel(0.5, only_confirmed, CLAIM_CHANNEL_MAX_WEIGHT))
        assert apply_claim_channel(0.5, with_refuted, CLAIM_CHANNEL_MAX_WEIGHT) <= 0.5

    def test_it_can_never_inflate_risk(self):
        """z3 proves this over the box; here it is EXERCISED across a grid."""
        for confirmed in range(0, 5):
            for refuted in range(0, 3):
                rep = _ledger(confirmed, refuted).report()
                for w in (0.0, 0.1, 0.25, CLAIM_CHANNEL_MAX_WEIGHT):
                    for r_k in (0.0, 0.2, 0.5, 1.0):
                        out = apply_claim_channel(r_k, rep, w)
                        assert out <= r_k + 1e-12, (confirmed, refuted, w, r_k, out)
                        assert 0.0 <= out <= 1.0

    def test_a_positive_risk_is_never_driven_to_zero(self):
        rep = _ledger(confirmed=10).report()
        assert apply_claim_channel(1e-9, rep, CLAIM_CHANNEL_MAX_WEIGHT) > 0.0

    def test_it_is_monotone_non_increasing_in_coverage(self):
        prev = None
        for confirmed in range(0, 6):
            rep = _ledger(confirmed, refuted=5 - confirmed).report()
            f = claim_channel_factor(rep, CLAIM_CHANNEL_MAX_WEIGHT)
            if prev is not None:
                assert f <= prev + 1e-12
            prev = f

    def test_an_empty_ledger_is_inert_not_risk_free(self):
        """0 coverage, factor 1: 'nothing was verified', never 'nothing is wrong'."""
        rep = ClaimLedger(target="empty").report()
        assert rep["claim_channel_coverage"] == 0.0
        assert rep["claim_channel_factor"] == 1.0
        assert apply_claim_channel(0.9, rep, CLAIM_CHANNEL_MAX_WEIGHT) == pytest.approx(0.9)


class TestTheCeilingIsEnforced:
    def test_a_weight_above_the_ceiling_is_refused(self):
        rep = _ledger(confirmed=1).report()
        with pytest.raises(ValueError, match="must lie in"):
            claim_channel_factor(rep, weight=CLAIM_CHANNEL_MAX_WEIGHT + 0.01)

    def test_a_weight_of_one_is_refused_because_it_annihilates_risk(self):
        rep = _ledger(confirmed=1).report()
        with pytest.raises(ValueError, match="annihilated"):
            claim_channel_factor(rep, weight=1.0)

    def test_a_negative_weight_is_refused(self):
        rep = _ledger(confirmed=1).report()
        with pytest.raises(ValueError):
            claim_channel_factor(rep, weight=-0.1)

    def test_the_ceiling_itself_is_accepted(self):
        rep = _ledger(confirmed=1).report()
        assert claim_channel_factor(rep, weight=CLAIM_CHANNEL_MAX_WEIGHT) == 0.5


class TestTheReportCarriesItsOwnFactor:
    def test_the_report_fields_are_present_and_consistent(self):
        rep = _ledger(confirmed=2, refuted=1, routed=1).report()
        assert rep["claim_channel_weight"] == CLAIM_CHANNEL_WEIGHT
        assert rep["claim_channel_coverage"] == pytest.approx(0.5)
        assert rep["claim_channel_factor"] == 1.0
        assert rep["claim_channel_factor_at_ceiling"] == pytest.approx(0.75)

    def test_the_factor_is_derived_from_the_reports_own_counts(self):
        """1 definition of numerator and denominator, not a second copy.

        If `claim_channel_coverage` ever read a different field from the one the
        report prints, this would disagree.
        """
        rep = _ledger(confirmed=3, refuted=2, routed=5).report()
        expected = rep["by_verdict"]["CONFIRMED"] / rep["claims_total"]
        assert rep["claim_channel_coverage"] == pytest.approx(expected)
        assert claim_channel_coverage(rep) == pytest.approx(expected)
