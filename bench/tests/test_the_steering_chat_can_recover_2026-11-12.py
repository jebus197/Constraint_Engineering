#!/usr/bin/env python3
"""The steering chat must recover when the researcher says the category is wrong.

★ ENTRY B161, AND THE DESIGN IS HIS RATHER THAN MINE. The 4 simulated steering
chats of 2026-11-12 exercised selecting a domain and escalating to a dialogue,
and never the case where the researcher simply rejects the proposal. His words:
the classifier *"can be told to say some thing like 'Oh sorry about that. What
category of problem would you like to discuss today. Would you like me to search
again for you, or would you like to specify one exactly?' There can be a few
allowed variations of this, so the response doesn't always seem too mechanical."*

★ 3 SEPARABLE PIECES, TESTED SEPARATELY. The repair phrasings are a
user-experience choice with no falsifiable criterion, so what is checked is
FITNESS -- that there are several, that they are reproducible, and that they
offer both routes he named. The profile is checked for being ADDITIVE. The
mismatch test is the only piece with a measurable criterion and gets the most
tests.

★ THE MISMATCH TEST MUST REUSE `propose`, NOT DECIDE AGAIN.
`test_it_delegates_to_propose_rather_than_deciding_again` flips `propose` and
requires the answer to move. A second predicate for "which domain is this" would
be a second steering surface, and 2026-11-11 was spent removing exactly that:
2 domain vocabularies agreeing on 3 names of 17, with every routing decision
depending on which one a caller happened to read.

Costs nothing: reads the committed manifest and encodings, dispatches to no
model, runs no pytest of its own.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


@pytest.fixture(scope="module")
def DP():
    from bench.cdsfl_registry import domain_proposer as dp
    return dp


class TestTheRepairTurnIsFitForPurpose:
    def test_there_are_several_phrasings_so_it_does_not_read_as_a_script(self, DP):
        """His words: a few allowed variations so the response does not always
        seem too mechanical."""
        assert len(DP.REPAIR_PHRASINGS) >= 3, DP.REPAIR_PHRASINGS
        assert len(set(DP.REPAIR_PHRASINGS)) == len(DP.REPAIR_PHRASINGS), (
            "a phrasing is duplicated, so the variation is smaller than it looks")

    def test_every_phrasing_offers_BOTH_routes_he_named(self, DP):
        """Search again, or specify it exactly. A phrasing offering only one
        would quietly narrow his design."""
        for p in DP.REPAIR_PHRASINGS:
            low = p.lower()
            assert any(w in low for w in ("search", "look")), p
            assert any(w in low for w in ("name", "specify", "tell me")), p

    def test_every_phrasing_apologises_without_grovelling(self, DP):
        for p in DP.REPAIR_PHRASINGS:
            low = p.lower()
            assert any(w in low for w in ("sorry", "apolog", "my mistake")), p
            assert len(p) < 240, f"too long to say aloud: {p}"

    def test_the_variant_is_REPRODUCIBLE_and_any_integer_is_safe(self, DP):
        """A random phrasing could not be pinned by a test or by a transcript."""
        assert DP.repair_turn(0) == DP.repair_turn(0)
        n = len(DP.REPAIR_PHRASINGS)
        assert DP.repair_turn(n) == DP.repair_turn(0), "it does not wrap"
        for i in (-7, 0, 1, 999999):
            assert DP.repair_turn(i) in DP.REPAIR_PHRASINGS, i

    def test_a_repeated_repair_does_not_say_the_same_thing_twice(self, DP):
        assert DP.repair_turn(0) != DP.repair_turn(1)

    def test_the_explainer_says_why_rather_than_merely_apologising(self, DP):
        e = DP.explainer().lower()
        assert "profile" in e or "constraint" in e, DP.explainer()
        assert len(DP.explainer()) < 400, "too long for an aside"


class TestTheProfileIsAdditive:
    def test_accepting_a_second_domain_keeps_the_first(self, DP):
        """His design: the new OR ADDITIONAL encoding is loaded. A researcher
        moving between 2 fields keeps both, so the 2nd chat does not undo the 1st."""
        p = DP.accept(DP.accept(None, "statistics"), "biology")
        assert p["domains"] == ["statistics", "biology"], p

    def test_accepting_the_same_domain_twice_does_not_duplicate_it(self, DP):
        p = DP.accept(DP.accept(None, "biology"), "biology")
        assert p["domains"] == ["biology"], p

    def test_an_alias_is_normalised_through_the_ONE_vocabulary(self, DP):
        """`bio` must be stored as `biology`, or the profile holds 2 names for
        1 domain and the mismatch test misses on the spelling."""
        p = DP.accept(None, "bio")
        assert p["domains"] == ["biology"], p

    def test_it_does_not_mutate_the_profile_it_was_given(self, DP):
        before = DP.accept(None, "statistics")
        snapshot = list(before["domains"])
        DP.accept(before, "biology")
        assert before["domains"] == snapshot, (
            "accept mutated its argument, so a caller holding the old profile "
            "would see it change underneath")


class TestTheMismatchTest:
    def test_no_profile_loaded_asks_for_the_first_steering_chat(self, DP, monkeypatch):
        """★ THE REASON IS ASSERTED, NOT JUST THE BOOLEAN, and a mutation
        forced that. Removing the no-profile branch still returns resteer=True,
        because the final branch also asks -- the property is protected twice,
        so no single-site mutation can change the boolean. What it DOES change
        is the reason: the fall-through blames a domain that is 'not in the
        loaded profile []' rather than naming that no profile exists. Those are
        2 different conversations with the researcher, a FIRST steering chat
        against ADDING an encoding, so the distinction is load-bearing and is
        what this test now pins."""
        monkeypatch.setattr(DP, "propose",
                            lambda t, v=None: {"domain": "biology", "subdomain": "x",
                                               "ambiguous": False, "reason": "",
                                               "top": [], "margin": 0.9})
        for prof in (None, {}, {"domains": []}):
            r = DP.profile_mismatch("a task about enzyme kinetics", prof)
            assert r["resteer"] is True, (prof, r)
            assert "no profile is loaded" in r["why"], (
                f"with profile {prof!r} the reason given was {r['why']!r}, which "
                f"blames a domain rather than naming the absent profile")

    def test_an_absent_profile_and_a_WRONG_profile_give_different_reasons(self, DP, monkeypatch):
        """The discrimination half: if both said the same thing the branch above
        would decide nothing."""
        monkeypatch.setattr(DP, "propose",
                            lambda t, v=None: {"domain": "biology", "subdomain": "x",
                                               "ambiguous": False, "reason": "",
                                               "top": [], "margin": 0.9})
        absent = DP.profile_mismatch("anything", None)["why"]
        wrong = DP.profile_mismatch("anything", {"domains": ["chemistry"]})["why"]
        assert absent != wrong, absent
        assert "no profile is loaded" in absent, absent
        assert "not in the loaded profile" in wrong, wrong

    def test_a_domain_already_in_the_profile_does_not_ask_again(self, DP, monkeypatch):
        monkeypatch.setattr(DP, "propose",
                            lambda t, v=None: {"domain": "biology", "subdomain": "x",
                                               "ambiguous": False, "reason": "",
                                               "top": [], "margin": 0.9})
        r = DP.profile_mismatch("anything", {"domains": ["biology"]})
        assert r["mismatch"] is False and r["resteer"] is False, r

    def test_a_domain_outside_the_profile_asks(self, DP, monkeypatch):
        monkeypatch.setattr(DP, "propose",
                            lambda t, v=None: {"domain": "chemistry", "subdomain": "x",
                                               "ambiguous": False, "reason": "",
                                               "top": [], "margin": 0.9})
        r = DP.profile_mismatch("anything", {"domains": ["biology"]})
        assert r["resteer"] is True and r["proposed"] == "chemistry", r

    def test_an_AMBIGUOUS_proposal_asks_rather_than_keeping_the_profile(self, DP, monkeypatch):
        """★ THE CASE THAT MATTERS. Keeping the loaded profile on an ambiguous
        proposal would judge a finding on a scale nobody chose, which is the
        silent default `consequence_domain` exists to remove."""
        monkeypatch.setattr(DP, "propose",
                            lambda t, v=None: {"domain": "biology", "subdomain": "x",
                                               "ambiguous": True,
                                               "reason": "2 domains within the margin",
                                               "top": [], "margin": 0.01})
        r = DP.profile_mismatch("anything", {"domains": ["biology"]})
        assert r["resteer"] is True, (
            "an ambiguous proposal was absorbed by the loaded profile")
        assert "ambiguous" in r["why"], r["why"]

    def test_it_delegates_to_propose_rather_than_deciding_again(self, DP, monkeypatch):
        """Flip `propose` and the answer must move. A second predicate would not."""
        prof = {"domains": ["biology"]}
        monkeypatch.setattr(DP, "propose",
                            lambda t, v=None: {"domain": "biology", "ambiguous": False,
                                               "subdomain": "x", "reason": "", "top": [],
                                               "margin": 0.9})
        a = DP.profile_mismatch("identical text", prof)["resteer"]
        monkeypatch.setattr(DP, "propose",
                            lambda t, v=None: {"domain": "physics", "ambiguous": False,
                                               "subdomain": "x", "reason": "", "top": [],
                                               "margin": 0.9})
        b = DP.profile_mismatch("identical text", prof)["resteer"]
        assert (a, b) == (False, True), (
            f"the same text gave resteer={a} then {b}; the mismatch test is not "
            f"consulting propose()")

    def test_every_answer_carries_a_reason(self, DP):
        for prof in (None, {"domains": []}, {"domains": ["biology"]}):
            r = DP.profile_mismatch("a task about enzyme kinetics", prof)
            assert r["why"], (prof, r)
            assert set(r) >= {"mismatch", "resteer", "proposed", "loaded",
                              "proposal", "why"}, r


class TestItIsNotVacuousOnTheLiveVocabulary:
    """Every case above monkeypatches `propose`, so without this the whole file
    could pass against a vocabulary that scores nothing at all."""

    def test_the_live_proposer_returns_a_usable_proposal(self, DP):
        pr = DP.propose("Prove that the sum of two even integers is even")
        assert set(pr) >= {"domain", "subdomain", "ambiguous", "reason"}, pr
        assert pr["domain"] or pr["ambiguous"], pr

    def test_the_live_mismatch_test_runs_end_to_end_without_a_double(self, DP):
        prof = DP.accept(None, "mathematics")
        r = DP.profile_mismatch("Prove that the sum of two even integers is even",
                                prof)
        assert r["why"], r
        assert isinstance(r["resteer"], bool), r

    def test_the_escalation_THAT_STARTED_THIS_asks_rather_than_guessing(self, DP):
        """★ NOT A CONSTRUCTION. The 2026-11-12 escalation was a pooled hazard
        ratio from 3 unlike trial sites for a vaccine dosing claim. With only
        statistics loaded, the surface must ASK rather than load whatever it
        scored -- and measured on the live vocabulary it scores neither
        statistics nor biology, which is precisely why asking is the fix."""
        prof = DP.accept(None, "statistics")
        r = DP.profile_mismatch(
            "Pooled hazard ratio across three unlike trial sites for a vaccine "
            "dosing claim", prof)
        assert r["resteer"] is True, (
            "the surface kept a profile that does not cover the task, which is "
            "the silent default this entry exists to remove")
