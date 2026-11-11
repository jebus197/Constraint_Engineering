#!/usr/bin/env python3
"""The dimensional refusal feeds back to the harness; HIL only on repeated failure.

★ FOUNDER RULING 2026-11-11, verbatim: *"I accept the dimensional check fix to
feed back to the harness and HIL escalation only on repeated failure."*

★ IT REVERSES CC1'S OWN B136 RECOMMENDATION, which is why this file pins the
DIRECTION and not merely the plumbing. B136 proposed moving
`dimensional_analysis` to `secondary_only` so it could *corroborate but never
refuse*. Measured 2026-11-11 the tool is one-sided the other way: pint shows
all 4 probe claims homogeneous while only 2 are numerically true, so a
CONFIRMED carries 0 bits about correctness; z3 returns `unsat` for the
dimension constraints of an inhomogeneous sum, so a REFUSAL is a proof. The
recommendation would have kept the worthless half and discarded the sound one.
Producer: `scripts/the_dimensional_repair_is_underdetermined_2026-11-11.py`.

★ AND THE ADMISSION SIDE NEEDED NOTHING, which the FOLLOW step established
before any edit: `CANNOT_ADMIT_ALONE` already bars this tool from admitting a
fix by itself, and the comment above it already records that it has 0 comparing
branches. Building a second bar would have been the duplicate mechanism
`additive-standard` forbids.

★ THE ESCALATION VOCABULARY IS NOT NEW EITHER: `bench/cc2_manager.py` already
carries CONFIRM / REJECT / DUPLICATE / ESCALATE, where ESCALATE means it needs
HIL review. This route emits the same token rather than inventing one.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))

import domain_immune as di                                   # noqa: E402


def _homogeneous(text: str) -> bool:
    """A stub verifier: sound iff every unit agrees. Injected so the whole
    suite runs with 0 dispatch, 0 spend and 0 subprocess."""
    return len(set(di.dimensional_units(text))) <= 1


class TestTheNonUniquenessDetector:
    def test_two_of_three_agreeing_gives_a_unique_repair(self):
        assert di.repair_is_unique("3 m + 2 s = 5 m")

    def test_all_three_differing_is_not_unique(self):
        assert not di.repair_is_unique("3 m + 2 s = 5 kg")

    def test_fewer_than_two_quantities_is_trivially_unique(self):
        assert di.repair_is_unique("5 m")
        assert di.repair_is_unique("no quantities here at all")

    def test_the_units_are_read_in_order(self):
        assert di.dimensional_units("3 m + 2 s = 5 kg") == ["m", "s", "kg"]


class TestTheRouteHonoursHisRuling:
    def test_a_sound_claim_is_not_sent_to_the_harness(self):
        calls = []
        out = di.dimensional_repair_route(
            "3 m + 2 m = 5 m",
            lambda c, r: calls.append(c) or c, verify=_homogeneous)
        assert out["action"] == "REPAIRED"
        assert out["attempts"] == 0
        assert not calls, "a sound claim was sent to a model for repair"

    def test_a_repairable_claim_is_fixed_on_the_first_attempt(self):
        out = di.dimensional_repair_route(
            "3 m + 2 s = 5 m",
            lambda c, r: "3 m + 2 m = 5 m", verify=_homogeneous)
        assert out["action"] == "REPAIRED"
        assert out["attempts"] == 1
        assert out["claim"] == "3 m + 2 m = 5 m"

    def test_repeated_failure_escalates_and_not_before(self):
        """★ HIS WORDS: HIL escalation only on REPEATED failure. A single
        failed candidate must RETRY, not escalate."""
        seen = []

        def always_bad(c, r):
            seen.append(r)
            return "3 m + 2 s = 5 m"

        out = di.dimensional_repair_route("3 m + 2 s = 5 m", always_bad,
                                          verify=_homogeneous)
        assert out["action"] == "ESCALATE"
        assert out["attempts"] == di.MAX_REPAIR_ATTEMPTS >= 2, (
            "escalation happened before the failure was REPEATED, which is "
            "stricter than his ruling and costs him an interruption")
        assert len(seen) == di.MAX_REPAIR_ATTEMPTS

    def test_an_empty_candidate_is_a_failure_not_a_crash(self):
        out = di.dimensional_repair_route("3 m + 2 s = 5 m",
                                          lambda c, r: "", verify=_homogeneous)
        assert out["action"] == "ESCALATE"
        assert "no candidate" in out["reason"]

    def test_the_reason_is_carried_back_to_the_model(self):
        """A repair request with no reason is a guess request."""
        reasons = []
        di.dimensional_repair_route("3 m + 2 s = 5 m",
                                    lambda c, r: reasons.append(r) or "3 m + 2 m = 5 m",
                                    verify=_homogeneous)
        assert reasons and reasons[0].strip(), "the model was asked to repair with no reason given"
        assert "inhomogeneous" in reasons[0]


class TestNonUniqueGoesStraightToTheHuman:
    def test_it_escalates_without_asking_a_model(self):
        """★ Asking a model to choose among 3 equally minimal repairs invites
        it to assert an intent the evidence does not contain. Measured: 24 of
        60 inhomogeneous 3-term cases, 0.400000, Wilson [0.285695, 0.526339]."""
        calls = []
        out = di.dimensional_repair_route(
            "3 m + 2 s = 5 kg",
            lambda c, r: calls.append(c) or "3 m + 2 m = 5 m",
            verify=_homogeneous)
        assert out["action"] == "ESCALATE"
        assert out["attempts"] == 0
        assert not calls, (
            "a model was asked to choose among equally minimal repairs, which "
            "is a vote on intent wearing the clothes of a proposal")
        assert "not unique" in out["reason"]


class TestItIsNotAModelVote:
    def test_the_tool_decides_not_the_model(self):
        """The model's candidate is REJECTED when the tool refuses it, however
        confidently the model offered it."""
        out = di.dimensional_repair_route(
            "3 m + 2 s = 5 m",
            lambda c, r: "3 m + 2 s = 5 m  # I am certain this is correct",
            verify=_homogeneous)
        assert out["action"] == "ESCALATE", (
            "a model's assertion was accepted without the tool agreeing")


class TestTheProducerStillSupportsTheFigures:
    def test_the_underdetermination_rate_reproduces(self):
        import importlib.util
        p = ROOT / "scripts" / "the_dimensional_repair_is_underdetermined_2026-11-11.py"
        assert p.is_file(), f"{p} is missing; the cited rate has no producer"
        spec = importlib.util.spec_from_file_location("_dimprod", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        m = mod.measure()
        assert len(m["rows"]) == 60
        assert len(m["amb"]) == 24, (
            f"the underdetermination count moved to {len(m['amb'])}; the "
            f"0.400000 quoted to the founder must be re-derived before reuse")
        assert m["z3"] == "unsat", "inhomogeneity is no longer provably unsatisfiable"
