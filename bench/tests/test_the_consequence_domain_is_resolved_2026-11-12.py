#!/usr/bin/env python3
"""A task's SUBJECT domain and its CONSEQUENCE domain are 2 answers, not 1.

★ WHY THIS EXISTS, AND A SEAT FOUND IT RATHER THAN A REVIEW. Entry B162. In the
2026-11-12 steering simulation a small model answering as a harness seat
contradicted the orchestrator's own proposer about a pooled hazard ratio drawn
from 3 unlike trial sites. The proposer said statistics. The seat said biology,
reasoning from the manifest's own rule rather than against it: statistics
declares `severity_scale = "none"` with the recorded reason that a statistical
error's consequence belongs to the application it serves, and the application
was a vaccine dosing claim, so the consequence is patient harm.

BOTH ANSWERS WERE CORRECT ABOUT DIFFERENT QUESTIONS. The subject decides which
expert encoding a seat receives. The consequence decides what counts as a
critical finding. A steering surface returning 1 label cannot express that.

★ THE FLAG WAS ALREADY DECLARED AND ALREADY DEAD, which is why this is a
wiring job rather than a new field. `inherits_from_application` was written into
`severity()`'s return by exactly 1 line and read by 0 callers: `may_compose`
infers inheritance from `scale == "none"` instead, and the command-line report
reads only the scale and the critical level. An addition nothing reaches is not
additive, in the symmetric sense this project's standard states.

★ THE CASE THAT MATTERS IS THE UNRESOLVED ONE. A subject that inherits, with no
application given, previously yielded a scale of "none" and nothing noticed.
`test_an_inheriting_subject_with_no_application_is_UNRESOLVED_not_none` pins
that it now says so, because a gate admitting findings on an unresolved scale is
the fault B143 and B144 record from the other side.

Costs nothing: reads the committed manifest, dispatches to no model, runs no
pytest of its own.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


@pytest.fixture(scope="module")
def V():
    from bench.cdsfl_registry import domain_vocabulary as v
    v.load.cache_clear()
    return v


class TestTheEscalationThatStartedIt:
    def test_statistics_about_a_biology_application_is_judged_on_biologys_scale(self, V):
        """The live case, not a construction: the seat's answer and the
        proposer's are both returned, each as the thing it is."""
        r = V.consequence_domain("statistics", "biology")
        assert r["subject"] == "statistics", r
        assert r["consequence"] == "biology", r
        assert r["how"] == "inherited", r
        assert r["resolved"] is True, r
        assert r["scale"] == V.severity("biology")["scale"], r
        assert r["critical_level"] == V.severity("biology")["critical_level"], r

    def test_the_subject_is_NOT_overwritten_by_the_consequence(self, V):
        """★ THE WHOLE POINT. If the resolver returned 1 domain the encoding
        would be chosen from the consequence, which is the proposer's error in
        mirror image and would load the wrong expert box."""
        r = V.consequence_domain("statistics", "biology")
        assert r["subject"] != r["consequence"], (
            "subject and consequence collapsed to 1 answer, which is the defect")


class TestAnUnresolvedConsequenceIsNamed:
    def test_an_inheriting_subject_with_no_application_is_UNRESOLVED_not_none(self, V):
        r = V.consequence_domain("statistics")
        assert r["resolved"] is False, r
        assert r["how"] == "unresolved", r
        assert r["scale"] is None, r
        assert "no application was given" in r["why"], r["why"]

    def test_the_reason_the_manifest_records_is_carried_through(self, V):
        """A refusal that does not say why is the swallowed-exception shape."""
        r = V.consequence_domain("statistics")
        recorded = V.severity("statistics")["reason"] or ""
        assert recorded, "the manifest records no reason for statistics"
        assert recorded[:40] in r["why"], r["why"]

    def test_a_chain_that_does_not_terminate_is_refused(self, V):
        """Both inherit, so there is no scale at the end of the chain."""
        r = V.consequence_domain("statistics", "physics")
        assert r["resolved"] is False, r
        assert "does not terminate" in r["why"], r["why"]

    def test_a_composed_scale_cannot_be_resolved_from_the_subject_alone(self, V):
        r = V.consequence_domain("cross_domain")
        assert r["resolved"] is False and r["how"] == "composed", r


class TestADomainWithItsOwnScale:
    @pytest.mark.parametrize("dom", ["software", "chemistry", "biology", "engineering"])
    def test_it_is_its_own_consequence_domain(self, V, dom):
        r = V.consequence_domain(dom)
        assert r["how"] == "own", r
        assert r["resolved"] is True, r
        assert r["consequence"] == V.resolve(dom), r

    def test_naming_an_application_does_not_override_a_declared_scale(self, V):
        """★ A FALSIFIER. A domain that declares its own scale must not inherit
        a different one just because an application was named, or a CVSS score
        would start being judged on a clinical grade."""
        r = V.consequence_domain("software", "biology")
        assert r["how"] == "own", r
        assert r["scale"] == V.severity("software")["scale"], r


class TestItIsNotVacuousOnTheLiveManifest:
    def test_6_of_the_10_real_domains_do_not_own_their_scale(self, V):
        """The figure B162 rests on, computed rather than asserted. Stated as a
        FLOOR on the inheriting count and a FLOOR on the total, because pinning
        both exactly is the treadmill this project has already recorded."""
        inh = V.inheriting_domains()
        total = [d for d in V.domains() if d != "subdomain_aliases"]
        assert len(inh) >= 5, (
            f"only {len(inh)} domain(s) do not own their scale, so the "
            f"distinction this module draws is close to vacuous: {inh}")
        assert len(inh) < len(total), (
            "every domain inherits, so no domain can terminate a chain and the "
            "resolver can never return a scale")

    def test_every_domain_resolves_to_one_of_the_4_named_outcomes(self, V):
        allowed = {"own", "inherited", "composed", "unresolved"}
        for dom in V.domains():
            if dom == "subdomain_aliases":
                continue
            r = V.consequence_domain(dom)
            assert r["how"] in allowed, (dom, r)
            assert r["why"], f"{dom} resolved with no reason given"

    def test_a_resolved_answer_always_carries_a_scale_and_an_unresolved_never_does(self, V):
        """The invariant a caller depends on. Without it a caller could read a
        scale off an unresolved answer, which is the silent default this entry
        exists to remove."""
        for dom in V.domains():
            if dom == "subdomain_aliases":
                continue
            for app in (None, "biology", "software"):
                r = V.consequence_domain(dom, app)
                if r["resolved"]:
                    assert r["scale"] not in (None, "none", "composed"), (dom, app, r)
                else:
                    assert r["scale"] is None, (dom, app, r)


class TestItRefusesRubbish:
    def test_an_unknown_subject_raises_rather_than_degrading(self, V):
        with pytest.raises(Exception):
            V.consequence_domain("not_a_domain_2026")

    def test_an_unknown_application_raises_rather_than_being_ignored(self, V):
        """Ignoring an unknown application would return UNRESOLVED and read as
        a manifest gap rather than as a caller's typo."""
        with pytest.raises(Exception):
            V.consequence_domain("statistics", "not_a_domain_2026")


class TestTheFLAGIsLoadBEARINGAndNotJustTheScale:
    """★ THIS CLASS EXISTS BECAUSE 2 MUTATIONS SURVIVED, AND THEY SURVIVED FOR
    THE SAME REASON THE DEFECT B162 NAMES WAS INVISIBLE IN THE FIRST PLACE.

    `scripts/the_consequence_resolver_mutations_2026-11-12.py` removed the
    `inherits_from_application` check and this file stayed GREEN. On the live
    manifest every domain declaring `severity_scale = "none"` ALSO declares
    `inherits_from_application = true`, so the flag and the scale are perfectly
    correlated and no live case can separate them. That is exactly why
    `may_compose` gets away with inferring inheritance from the scale: it is
    right today and unfalsifiable today.

    So the flag is load-bearing only for a shape the manifest does not hold --
    a domain declaring no scale that does NOT inherit one. That shape is
    CONSTRUCTED here rather than waited for, which is this project's own rule
    that a mechanism existing for a degraded input cannot be shown load-bearing
    by an input that is not degraded.
    """

    @staticmethod
    def _with_declarations(V, monkeypatch, decls):
        """Drive the resolver over constructed declarations, leaving the real
        manifest untouched. Only `resolve` and `severity` are redirected,
        because those are the 2 the resolver reads."""
        real_sev, real_res = V.severity, V.resolve

        def sev(name):
            n = real_res(name) if name not in decls else name
            return decls.get(n) or real_sev(n)

        def res(name):
            return name if name in decls else real_res(name)

        monkeypatch.setattr(V, "severity", sev)
        monkeypatch.setattr(V, "resolve", res)

    @staticmethod
    def _decl(**kw):
        base = {"domain": "", "scale": None, "levels": [], "critical_level": None,
                "note": None, "reason": None,
                "inherits_from_application": False,
                "composes_from_selected": False}
        base.update(kw)
        return base

    def test_no_scale_and_NOT_inheriting_is_refused_with_its_own_reason(self, V, monkeypatch):
        """★ THE CASE THAT KILLS THE SURVIVING MUTATION. Without the flag check
        this falls through to the inheritance path and would ask for an
        application that the domain never said it wants."""
        decls = {"orphan_domain": self._decl(
            domain="orphan_domain", scale="none",
            reason="constructed: declares nothing and inherits nothing")}
        self._with_declarations(V, monkeypatch, decls)
        r = V.consequence_domain("orphan_domain")
        assert r["resolved"] is False, r
        assert r["how"] == "unresolved", r
        assert "does not declare that it inherits" in r["why"], r["why"]

    def test_the_same_domain_is_STILL_refused_when_an_application_is_named(self, V, monkeypatch):
        """A domain that never said it inherits must not acquire a scale merely
        because a caller supplied an application. Otherwise the flag is
        decorative and the caller decides the scale, which is the inverse of
        the manifest being the one vocabulary."""
        decls = {"orphan_domain": self._decl(
            domain="orphan_domain", scale="none",
            reason="constructed: declares nothing and inherits nothing")}
        self._with_declarations(V, monkeypatch, decls)
        r = V.consequence_domain("orphan_domain", "biology")
        assert r["resolved"] is False, r
        assert "does not declare that it inherits" in r["why"], r["why"]

    def test_an_inheriting_twin_of_that_domain_DOES_resolve(self, V, monkeypatch):
        """The discrimination half: the ONLY difference between this case and
        the 2 above is the flag, so a green here with a red there proves the
        flag decides and not the scale."""
        decls = {"heir_domain": self._decl(
            domain="heir_domain", scale="none", inherits_from_application=True,
            reason="constructed: declares nothing and inherits from the application")}
        self._with_declarations(V, monkeypatch, decls)
        r = V.consequence_domain("heir_domain", "biology")
        assert r["resolved"] is True, r
        assert r["how"] == "inherited", r
        assert r["scale"] == V.severity("biology")["scale"], r

    def test_the_census_counts_a_non_inheriting_scaleless_domain_too(self, V, monkeypatch):
        """★ KILLS THE SECOND SURVIVOR. `inheriting_domains` ORs 3 conditions
        and the scale clause alone catches all 6 on the live manifest, so the
        flag clause decided nothing. A domain that inherits while DECLARING a
        scale separates them."""
        decls = {"odd_domain": self._decl(
            domain="odd_domain", scale="CTCAE v5.0 grade",
            inherits_from_application=True,
            reason="constructed: declares a scale AND says it inherits")}
        self._with_declarations(V, monkeypatch, decls)
        monkeypatch.setattr(V, "domains", lambda: ["odd_domain"])
        assert V.inheriting_domains() == ["odd_domain"], (
            "a domain declaring that it inherits is not counted as inheriting, "
            "so the flag clause of the census decides nothing")
