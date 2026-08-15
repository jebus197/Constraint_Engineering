"""A10 — when the machinery declines a fix, the panel is told.

THE MEASUREMENT THAT JUSTIFIES THIS
-----------------------------------
Across four rounds of the Exp 53 control, 50 proposed fixes were rejected at
fix-admission and no model was ever told. So every round the panel re-proposed
into a gate it could not see, and the run's own record described the outcome as
though the panel had failed rather than the channel.

This is the founder's design point, stated 2026-08-01: a claim the machinery
cannot handle should go BACK to the panel, not be quietly filed. A rejection the
panel can read is a rejection it can answer.

The lines are terse on purpose. The panel needs the reason and the gate, not the
evidence bundle — and a healthy finding must cost zero prompt budget, because
this renders for every active finding every round.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.reference_runner_v2 import (  # noqa: E402
    SK_ESCALATE,
    SK_NO_SCORE,
    SK_REJECTED,
    TARGET_KIND_PROSE,
    Finding,
    FindingRegistry,
    _rejection_lines,
)


def _registry_with(entry_updates: dict) -> FindingRegistry:
    r = FindingRegistry()
    r.target_kind = TARGET_KIND_PROSE
    cid = r.register(
        Finding(
            finding_id="F1", model_id="deepseek", round_idx=1, flaw_class=3,
            severity=0.80, abstraction_index=0.5,
            description="The stated clearance contradicts the tolerance table.",
            proposed_fix="<<<<<<< SEARCH\n0.29 mm\n=======\n0.29 mm\n>>>>>>> REPLACE",
        ),
        "deepseek",
    )
    r.entries[cid].update(entry_updates)
    return r


class TestASilentRejectionIsNoLongerSilent:
    def test_a_rejected_fix_says_so_and_names_the_gate(self):
        out = _rejection_lines({
            "sk_result": {"tristate": SK_REJECTED, "sk": 0.0,
                          "gate_details": {"g1_ast": False, "g2_compile": True}},
        })
        assert len(out) == 1
        assert "FIX REJECTED" in out[0]
        assert "g1_ast" in out[0], "name the gate that failed, not just the fact"
        assert "did not close this finding" in out[0], (
            "the consequence matters more than the score — a model that does "
            "not know the fix failed to close will keep proposing fixes")

    def test_it_reaches_the_prompt_the_panel_actually_reads(self):
        reg = _registry_with({
            "sk_result": {"tristate": SK_REJECTED, "sk": 0.0,
                          "gate_details": {"g1_ast": False}},
        })
        summary = reg.build_summary(2)
        assert "FIX REJECTED" in summary, (
            "a rejection recorded on the entry but absent from the round "
            "prompt is exactly the status quo this item exists to end")

    def test_no_score_tells_the_panel_what_to_do_instead(self):
        out = _rejection_lines({"sk_result": {"tristate": SK_NO_SCORE}})
        assert "runnable falsifier" in out[0], (
            "on prose a fix cannot close; saying so without naming the route "
            "that does work leaves the panel with nowhere to go")

    def test_escalate_is_distinguished_from_rejected(self):
        out = _rejection_lines({"sk_result": {"tristate": SK_ESCALATE}})
        assert "NOT SCORED" in out[0] and "REJECTED" not in out[0], (
            "a fix nobody could score is not a fix that failed")


class TestFalsifierFailuresAreAlsoReported:
    def test_an_errored_falsifier_is_named_as_such(self):
        out = _rejection_lines({"falsifier_verdict": "ERROR"})
        assert len(out) == 1 and "FALSIFIER ERROR" in out[0]
        assert "truncation" in out[0], (
            "truncation is one of the measured causes — 2 of 5 fixture "
            "falsifiers carried their own fence and were cut short")

    def test_a_missing_falsifier_is_named_as_such(self):
        out = _rejection_lines({"falsifier_verdict": "UNTOOLABLE"})
        assert "NO FALSIFIER" in out[0]

    def test_a_confirmed_falsifier_produces_nothing(self):
        assert _rejection_lines({"falsifier_verdict": "CONFIRMED"}) == []

    def test_an_escalation_carries_its_real_reason(self):
        out = _rejection_lines({
            "irreducible_escalation": True,
            "hil_reason": "routing ladder exhausted after 2 rung(s) reached a model",
        })
        assert "ESCALATED TO HUMAN" in out[0]
        assert "2 rung(s)" in out[0]

    def test_several_failures_are_all_reported(self):
        out = _rejection_lines({
            "sk_result": {"tristate": SK_NO_SCORE},
            "falsifier_verdict": "ERROR",
            "irreducible_escalation": True,
        })
        assert len(out) == 3, (
            "a finding can fail at more than one stage and the panel needs the "
            "whole picture, not the first thing that went wrong")


class TestAHealthyFindingCostsNothing:
    """This renders for every active finding, every round, to every model."""

    def test_an_untouched_entry_produces_no_lines(self):
        assert _rejection_lines({}) == []
        assert _rejection_lines({"description": "x", "severity": 0.9}) == []

    def test_an_admissible_fix_produces_no_lines(self):
        assert _rejection_lines(
            {"sk_result": {"tristate": "ADMISSIBLE", "sk": 0.94}}) == []

    def test_a_clean_summary_gains_no_rejection_text(self):
        summary = _registry_with({}).build_summary(2)
        for token in ("FIX REJECTED", "NOT SCORED", "FALSIFIER ERROR",
                      "NO FALSIFIER", "ESCALATED TO HUMAN"):
            assert token not in summary
