#!/usr/bin/env python3
"""The claim is the unit of record, and the channel is actually on.

WHAT THIS GUARDS. The free panel of 2026-09-30 found, on both seats
independently, that nothing in the harness judged a CLAIM as its unit: `S_k`
classifies a proposed FIX, one level above task A19's own title. The founder:
"Build it, apply it and test it before the next simulated run."

THE DESIGN IS THE SEATS', and `bench/claim_ledger.py` implements its 4 pieces:
a ledger per target, decidable claims carrying falsifiers into the EXISTING
verify path, undecidable claims ROUTED rather than discarded, and file-level
admissibility as an AGGREGATE. `compute_sk` is untouched.

THE TESTS THAT MATTER MOST ARE THE LAST 2 CLASSES. A ledger that is defined and
never populated would be the exact defect this project has 11 confirmed
instances of -- an addition nothing reaches. One of them was nearly shipped
here: the wiring first read `cfg.target_file`, which `RunnerConfig` does not
have, so it would have raised AttributeError, been swallowed by the section's
own exception guard, and left every report carrying a plausible
`{"written": false}` while the channel did nothing.

Run:  python3 -m pytest bench/tests/test_claim_ledger_2026-10-01.py -q
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.claim_ledger import (  # noqa: E402
    CLAIM_ADDRESSABLE,
    CLAIM_VERDICTS,
    NO_DECIDABLE_CLAIMS,
    ROUTE_HIL,
    ROUTE_VERIFY_CURRENT,
    ROUTED_ONLY,
    UNVERIFIED,
    Claim,
    ClaimLedger,
    claim_from_entry,
    ledger_from_registry,
)


class TestAClaimCannotBeDiscarded:
    """The March 2026 one-character near-miss is the standing warning."""

    def test_an_undecidable_claim_is_routed_by_construction(self):
        c = Claim(tag="C1", statement="the reader should feel reassured")
        assert c.decidable is False
        assert c.routed_to == ROUTE_HIL, (
            "an undecidable claim with no route is a discarded claim")

    def test_an_explicit_route_is_not_overwritten(self):
        c = Claim(tag="C1", statement="the current version is 3.13",
                  routed_to=ROUTE_VERIFY_CURRENT)
        assert c.routed_to == ROUTE_VERIFY_CURRENT

    def test_the_ledger_reports_discarded_as_zero(self):
        led = ClaimLedger("t")
        led.add(Claim(tag="a", statement="x"))
        led.add(Claim(tag="b", statement="y", decidable=True, falsifier="assert 1"))
        assert led.discarded() == []
        assert led.report()["discarded"] == 0

    def test_an_invented_verdict_is_refused(self):
        """No second taxonomy. The vocabulary is the falsifier path's own."""
        with pytest.raises(ValueError) as e:
            Claim(tag="C1", statement="x", decidable=True, verdict="INADMISSIBLE")
        assert "not a claim verdict" in str(e.value)
        # And the real vocabulary is accepted.
        for v in CLAIM_VERDICTS:
            Claim(tag="C1", statement="x", decidable=True, verdict=v)


class TestTheAggregateIsThreeValued:
    def test_claims_with_one_decidable_are_claim_addressable(self):
        led = ClaimLedger("t")
        led.add(Claim(tag="a", statement="x"))
        led.add(Claim(tag="b", statement="2+2=5", decidable=True,
                      falsifier="assert 2 + 2 == 5"))
        assert led.aggregate() == CLAIM_ADDRESSABLE

    def test_claims_with_none_decidable_are_routed_only(self):
        led = ClaimLedger("t")
        led.extend([Claim(tag="a", statement="x"), Claim(tag="b", statement="y")])
        assert led.aggregate() == ROUTED_ONLY, (
            "claims that exist but cannot be computed are ROUTED, which is not "
            "the same as the target having no claims")

    def test_no_claims_at_all_is_the_only_non_computable_state(self):
        assert ClaimLedger("t").aggregate() == NO_DECIDABLE_CLAIMS

    def test_the_three_states_are_distinct_and_each_carries_a_meaning(self):
        seen = set()
        for led in (ClaimLedger("t"),
                    _routed_only_ledger(),
                    _addressable_ledger()):
            rep = led.report()
            seen.add(rep["aggregate"])
            assert len(rep["aggregate_meaning"]) > 60, rep["aggregate"]
        assert len(seen) == 3, seen

    def test_the_absence_of_fences_is_not_the_absence_of_claims(self):
        """THE WHOLE POINT. A prose target with decidable claims is
        claim-addressable even though `_gateable_source` sees nothing."""
        led = _addressable_ledger()
        assert led.aggregate() == CLAIM_ADDRESSABLE
        assert all("```" not in c.statement for c in led.claims)


def _routed_only_ledger() -> ClaimLedger:
    led = ClaimLedger("prose.md")
    led.extend([Claim(tag="a", statement="the tone is confident"),
                Claim(tag="b", statement="the section order reads well")])
    return led


def _addressable_ledger() -> ClaimLedger:
    led = ClaimLedger("prose.md")
    led.add(Claim(tag="a", statement="the mean of 2, 4 and 6 is 4.5",
                  decidable=True, kind="arithmetic",
                  falsifier="assert statistics.mean([2,4,6]) == 4.5",
                  verdict="REFUTED", tools=["sympy", "numpy"]))
    led.add(Claim(tag="b", statement="the prose is persuasive"))
    return led


class TestReadingARegistryEntryAsTheClaimItAlreadyIs:
    def test_an_entry_with_a_falsifier_is_decidable(self):
        c = claim_from_entry("C0001", {
            "description": "the stated total is wrong",
            "falsifier_code": "assert total == 124",
            "falsifier_verdict": "CONFIRMED",
            "severity": 0.8, "source_model": "cc2-sim"})
        assert c.decidable is True
        assert c.verdict == "CONFIRMED"
        assert c.severity == 0.8 and c.source == "cc2-sim"
        assert c.routed_to == "", "a decidable claim does not need a route"

    def test_an_entry_without_a_falsifier_is_routed_to_a_human(self):
        c = claim_from_entry("C0002", {"description": "the design is unclear"})
        assert c.decidable is False and c.routed_to == ROUTE_HIL

    def test_a_claim_about_present_day_state_is_routed_to_verify_current(self):
        c = claim_from_entry("C0003", {"description": "the library is at 2.0",
                                       "finding_category": "state"})
        assert c.routed_to == ROUTE_VERIFY_CURRENT

    def test_an_unrecognised_verdict_string_becomes_unverified(self):
        """A verdict nobody minted must not be read as a verdict."""
        c = claim_from_entry("C0004", {"description": "x",
                                       "falsifier_code": "assert 1",
                                       "falsifier_verdict": "PROBABLY"})
        assert c.verdict == UNVERIFIED

    def test_a_malformed_severity_does_not_raise(self):
        for bad in ("high", None, [], {}):
            c = claim_from_entry("C", {"description": "x", "severity": bad})
            assert c.severity is None, bad


class TestItIsPopulatedByRealRuns:
    """ANTI-UNREACHED-ADDITION, part 1: it runs on the real archive."""

    ARCHIVES = (
        "commissioning_arm1_panel_20260921T215405Z",
        "commissioning_arm4_prose_20260930T064044Z",
    )

    def _entries(self, run: str):
        f = REPO / "bench" / "logs" / run / "runner_state.json"
        if not f.is_file():
            pytest.skip(f"archive absent: {run}")
        return (json.loads(f.read_text(encoding="utf-8")).get("registry")
                or {}).get("entries") or {}

    @pytest.mark.parametrize("run", ARCHIVES)
    def test_a_real_run_yields_a_populated_ledger(self, run):
        led = ledger_from_registry(self._entries(run), target=run)
        rep = led.report()
        assert rep["claims_total"] > 0, (
            "the ledger is empty on a real run, so it would report nothing "
            "about every target")
        assert rep["discarded"] == 0
        assert rep["decidable"] + rep["routed"] == rep["claims_total"], (
            "a claim is neither decidable nor routed, which is the discard "
            "this design exists to prevent")

    def test_the_prose_arm_is_claim_addressable_where_sk_has_no_opinion(self):
        """THE CASE THAT JUSTIFIES THE CHANNEL, on real archived data.

        `compute_sk` returns NO_SCORE on this target -- the machinery holds no
        opinion on anything in it -- while the claim channel finds decidable
        claims in it.
        """
        run = "commissioning_arm4_prose_20260930T064044Z"
        led = ledger_from_registry(self._entries(run), target=run)
        rep = led.report()
        assert rep["aggregate"] == CLAIM_ADDRESSABLE, rep["aggregate"]
        assert rep["decidable"] >= 1, rep
        assert rep["routed"] >= 1, (
            "if nothing is routed, the routing half of the design is untested "
            "on real data")

    def test_the_ledger_declares_what_it_does_not_cover(self):
        run = "commissioning_arm1_panel_20260921T215405Z"
        rep = ledger_from_registry(self._entries(run)).report()
        assert "not_covered" in rep and "UNSTATED" in rep["not_covered"], (
            "the artefact must say that v1 does not manufacture claims for a "
            "target no finding names; a reader should not have to find that in "
            "a module docstring")

    def test_it_is_informative_only_in_v1(self):
        """The seat's own recommendation, and the founder's shadow-promotion
        rule: on now, promoted only on evidence."""
        assert ClaimLedger.informative_only is True
        rep = ClaimLedger("t").report()
        assert rep["informative_only"] is True


class TestItIsOnTheRunnersLivePath:
    """ANTI-UNREACHED-ADDITION, part 2, and the near-miss this file was
    written for.

    The first wiring read `cfg.target_file`. `RunnerConfig` has no such field,
    so it would have raised AttributeError, the report section's own exception
    guard would have swallowed it, and every report would have carried a
    plausible `{"written": false}` while the channel did nothing at all.
    """

    def test_the_runner_imports_and_calls_the_ledger(self):
        """PARSED, NOT SEARCHED. A substring check here would pass on a comment
        mentioning the ledger, and `scripts/source_text_assertions_2026-09-11.py`
        counts source-text assertions precisely because 4 guards of that class
        broke on CORRECT changes in a single day."""
        import ast as _ast

        tree = _ast.parse((REPO / "bench" / "reference_runner_v3.py").read_text(
            encoding="utf-8"))
        # A real CALL to the builder, under whatever local name it is bound to.
        calls = [n for n in _ast.walk(tree)
                 if isinstance(n, _ast.Call)
                 and isinstance(n.func, _ast.Name)
                 and "claim_ledger" in n.func.id]
        assert calls, (
            "nothing calls the claim-ledger builder, so no report carries a "
            "ledger and the module is an addition nothing reaches")
        # And a real ASSIGNMENT of it into the report dict.
        targets = [
            n for n in _ast.walk(tree)
            if isinstance(n, _ast.Subscript)
            and isinstance(n.value, _ast.Name) and n.value.id == "result"
            and isinstance(n.slice, _ast.Constant)
            and n.slice.value == "claim_ledger"
        ]
        assert targets, (
            "the ledger is built but never attached to `result`, so the report "
            "is unchanged")

    def test_the_runner_does_not_read_a_config_field_that_does_not_exist(self):
        """EXECUTED, not read: the attribute is checked against the real class."""
        import dataclasses

        from bench.reference_runner_v3 import RunnerConfig
        names = {f.name for f in dataclasses.fields(RunnerConfig)}
        assert "target_file" not in names, (
            "RunnerConfig gained a target_file field; the comment at the "
            "wiring site now misstates why it reads from `result` instead")
        # PARSED, NOT GREPPED. The first version of this assertion searched
        # the source text for "cfg.target_file" and failed on the explanatory
        # COMMENT at the wiring site, which names the attribute in order to say
        # why it is not used. A predicate that matches a word rather than a
        # live expression is the defect `execute-do-not-grep` names, and it
        # misfired 3 times in one day before this.
        import ast as _ast

        tree = _ast.parse((REPO / "bench" / "reference_runner_v3.py").read_text(
            encoding="utf-8"))
        live = [n for n in _ast.walk(tree)
                if isinstance(n, _ast.Attribute)
                and n.attr == "target_file"
                and isinstance(n.value, _ast.Name)
                and n.value.id == "cfg"]
        assert live == [], (
            f"the runner evaluates cfg.target_file at line(s) "
            f"{[n.lineno for n in live]}, and RunnerConfig has no such field. "
            f"The ledger would raise, be swallowed by the section's exception "
            f"guard, and be silently disabled on every run.")

    def test_the_ledger_builder_accepts_what_the_runner_passes_it(self):
        """The runner passes `registry.entries` and a string target."""
        class _Reg:
            entries = {"C1": {"description": "x", "falsifier_code": "assert 1"}}

        led = ledger_from_registry(_Reg().entries, target="some/target.md")
        assert led.report()["claims_total"] == 1
        assert led.target == "some/target.md"
        # And a registry OBJECT, not just its .entries, also works.
        assert ledger_from_registry(_Reg()).report()["claims_total"] == 1
