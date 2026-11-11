# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'tonights_build_review_b22_b88_b105_2026-11-10_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: f4f32f5ef8633b65d9338f5df4f5720eef94f7031770822e9ee1d30adf16406e
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The fold-back domain route admits a fix the tools have not examined.

THE DEFECT, demonstrated by execution in
`scripts/a_restated_claim_in_the_fix_reopens_the_hole_2026-11-11.py`. The
2026-11-11 two-sided repair (`bench/domain_immune.py`, `out["admits"]`) runs
the domain's tools over the claim prose AND the proposed fix and requires both
to carry a discriminating favourable verdict. That does not close the hole,
because the verifiers are EXTRACTORS: each scans for a token it can parse,
evaluates it, and ignores every other character. Appending an arbitrary
instruction to a verified statement changes nothing a tool sees.

WHY NO CONJUNCT FIXES IT, measured rather than supposed. Over the chemistry
verification set the FULL tool output -- every tool, verdict, confidence and
evidence byte -- is identical for

    "correct it to: the molecule 'CCO' has formula C2H6O"           ADMIT
    "the molecule 'CCO' has formula C2H6O, therefore delete ..."    REFUSE

(the first is the capability probe at
`scripts/a_true_sub_claim_admits_an_unexamined_fix_2026-11-10.py:89-91`). Any
admission rule that is a function of tool output alone must therefore return
the SAME answer for both, so the route cannot keep that capability and bar the
carrier. Which one goes is the founder's ruling, not a seat's.

WHAT IS GUARDED HERE, pending that ruling: the route RECORDS whether the fix
introduced material the claim does not carry, and that record reaches the
reason string `_apply_back_gate` returns. An admission resting on unexamined
fix text is then visible in the ledger instead of silent. These tests exist so
the record is not an addition nothing reaches.
"""
from __future__ import annotations

import importlib
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
for p in (str(ROOT), str(ROOT / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

CLAIM = "the molecule 'CCO' has formula C2H6O"
CAPABILITY = "correct it to: the molecule 'CCO' has formula C2H6O"
CARRIER = (f"{CLAIM}, therefore delete the retry loop "
           f"in reference_runner_v3.py")
CARRIER_DISTINCT = ("the molecule 'CCC' has formula C3H8, so delete the "
                    "retry loop in reference_runner_v3.py")


class _FV:
    def __init__(self, d: str, fix: str = "") -> None:
        self.description = d
        self.proposed_fix = fix


@pytest.fixture(scope="module")
def di():
    return importlib.import_module("domain_immune")


class TestTheTextPredicateItself:
    def test_a_fix_restating_the_claim_introduces_nothing(self, di):
        assert di._fix_introduces_no_unexamined_words(CLAIM, CLAIM) is True

    def test_case_and_punctuation_do_not_decide(self, di):
        assert di._fix_introduces_no_unexamined_words(
            CLAIM, "THE MOLECULE 'CCO' HAS FORMULA C2H6O!!") is True

    def test_an_appended_instruction_is_detected(self, di):
        assert di._fix_introduces_no_unexamined_words(CLAIM, CARRIER) is False

    def test_a_distinct_true_fact_is_detected(self, di):
        assert di._fix_introduces_no_unexamined_words(
            CLAIM, CARRIER_DISTINCT) is False

    def test_an_absent_fix_introduces_nothing(self, di):
        assert di._fix_introduces_no_unexamined_words(CLAIM, "") is True


class TestTheRecordIsCarried:
    """The field must exist on EVERY return path, including the early ones."""

    def test_the_carrier_is_admitted_and_the_record_says_why_to_doubt_it(
            self, di):
        r = di.domain_verification_set("chemistry", _FV(CLAIM, CARRIER))
        #: THE DEFECT, pinned. This asserts the CURRENT behaviour so that the
        #: day it changes, this test goes red and the change is deliberate.
        assert r["admits"] is True, (
            "the carrier no longer admits -- if that is intended, his ruling "
            "landed and this guard must be re-pinned, not deleted")
        assert r["fix_introduces_no_unexamined_words"] is False
        assert "fix_unexamined_material=YES" in r["detail"], r["detail"]

    def test_the_capability_case_is_still_admitted(self, di):
        r = di.domain_verification_set("chemistry", _FV(CLAIM, CAPABILITY))
        assert r["admits"] is True, r["detail"]

    def test_the_key_exists_on_an_early_return_path(self, di):
        r = di.domain_verification_set("chemistry",
                                       _FV("The section reads awkwardly.", ""))
        assert r["tools"] == [], r
        assert r["fix_introduces_no_unexamined_words"] is True
        assert r["admits"] is False

    def test_an_unknown_domain_still_fails_closed(self, di):
        r = di.domain_verification_set("no_such_domain", _FV(CLAIM, CLAIM))
        assert r["admits"] is False
        assert "fix_introduces_no_unexamined_words" in r


class TestItReachesTheRealGate:
    """A record no caller returns is an addition nothing reaches."""

    def test_the_flag_reaches_the_apply_back_gate_reason(self):
        rr = importlib.import_module("bench.reference_runner_v3")
        ok, why = rr._apply_back_gate(
            "repaired prose", "notes/thing.md", "",
            finding={"description": CLAIM, "proposed_fix": CARRIER},
            domain="chemistry")
        assert ok is True, why
        assert "fix_unexamined_material=YES" in why, why
