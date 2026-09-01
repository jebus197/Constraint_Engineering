"""A critical is not cleared automatically — but its computed answer is not binned.

FOUNDER RULING, 2026-08-03
--------------------------
The post-convergence sweep cannot clear a critical and structurally never has:
eight dispositions exist in the whole archive and the highest severity any of
them touched is 0.66, against a 0.70 line. So a false alarm scored 0.71 became
permanent human work, decided by a number assigned once at intake by a model and
never recomputed, while an identical finding at 0.69 was cleared.

Three options were offered — accept the ceiling, record the verdict, or allow a
narrow demotion. The founder rejected the framing and gave a fourth:

    "Surely this goes back to the discussion we had very recently, which is
    simply can the solution be computed, regardless of how serious it may or may
    not be? If it can be computed, then why shouldn't the models simply do this?
    ... Nor if an issue is gauged above a certain level does it preclude the
    possibility of both having the models clear it and deal with it, AND raising
    both it and the fix the models devise for HIL review."

Both, not either. So:
  * CONFIRM-only is untouched. A critical is still never retired by a refutation,
    and the Exp 42 evidence behind that rule (2 of 3 REFUTED criticals were
    themselves wrong) still stands.
  * The computed answer, the model that produced it, and the proposed fix are
    RECORDED and travel to the human with the finding.
  * Genuine human-review categories — safety, legal, core functionality, real
    irreducibility — are unaffected. This changes what a human SEES, never what
    the machine decides.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.reference_runner_v3 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD,
    _record_computed_evidence,
    _rejection_lines,
)

RUNNER = Path(__file__).resolve().parents[1] / "reference_runner_v3.py"


class TestTheAnswerIsKeptRatherThanDiscarded:
    def test_a_refuted_critical_records_the_verdict_and_the_fix(self):
        e = {"severity": 0.85, "proposed_fix": "<<<<<<< SEARCH\n0.29\n=======\n0.31\n>>>>>>> REPLACE"}
        _record_computed_evidence(
            e, kind="falsifier_refuted", by="Codex",
            detail="a runnable falsifier ran and did NOT demonstrate the defect",
            falsifier="assert '0.29 mm' in open(p).read()")
        ce = e["computed_evidence"]
        assert len(ce) == 1
        assert ce[0]["by"] == "Codex"
        assert "0.31" in ce[0]["proposed_fix"], (
            "the FIX must travel with the finding — binning a sound fix because "
            "the finding scored 0.71 rather than 0.69 is the whole objection")
        assert ce[0]["falsifier_code"], "the test that produced the answer travels too"

    def test_a_reasoned_withdrawal_on_a_critical_keeps_its_reasoning(self):
        e = {"severity": 0.90}
        _record_computed_evidence(e, kind="reasoned_withdrawal", by="Gemini",
                                  detail="the tolerance table it contradicts is itself the typo")
        assert e["computed_evidence"][0]["detail"].startswith("the tolerance table")

    def test_evidence_accumulates_rather_than_overwriting(self):
        e = {"severity": 0.80}
        _record_computed_evidence(e, kind="falsifier_refuted", by="Codex", detail="one")
        _record_computed_evidence(e, kind="reasoned_withdrawal", by="CC2", detail="two")
        assert [c["by"] for c in e["computed_evidence"]] == ["Codex", "CC2"], (
            "two models disagreeing is information; the second must not erase the first")

    def test_a_human_can_see_it_without_reading_json(self):
        e = {"severity": 0.85}
        _record_computed_evidence(e, kind="falsifier_refuted", by="Codex", detail="x")
        assert e["hil_has_computed_evidence"] is True


class TestNothingIsClearedAutomatically:
    """The rule the founder explicitly did NOT question."""

    def test_recording_evidence_does_not_resolve_or_clear(self):
        e = {"severity": 0.85, "status": "CONFIRMED"}
        _record_computed_evidence(e, kind="falsifier_refuted", by="Codex", detail="x")
        assert e["status"] == "CONFIRMED", "recording is not resolving"
        assert "withdrawn_by_sweep" not in e
        assert "resolved_by_sweep" not in e

    def test_severity_is_not_touched(self):
        e = {"severity": 0.85}
        _record_computed_evidence(e, kind="falsifier_refuted", by="Codex", detail="x")
        assert e["severity"] == 0.85, (
            "this is not the demotion option; the band is unchanged and the "
            "finding stays critical")

    def test_the_sweep_still_refuses_to_retire_a_critical(self):
        src = RUNNER.read_text()
        # The withdrawal path must still `continue` above the line rather than
        # falling through to registry.resolve.
        i = src.index("# Same ruling. A reasoned withdrawal may not RETIRE a critical")
        window = src[i:i + 700]
        assert "continue" in window
        assert "registry.resolve" not in window

    def test_confirm_only_is_named_in_the_helper_so_it_is_not_quietly_relaxed(self):
        src = RUNNER.read_text()
        i = src.index("def _record_computed_evidence")
        doc = src[i:i + 1800]
        assert "CONFIRM-only" in doc and "Exp 42" in doc, (
            "the reason a critical may not be auto-cleared must stay attached to "
            "the code that records the alternative, or a later reader relaxes it")


class TestThePanelIsToldItIsOnFile:
    """A10 renders this; the panel must stop re-proposing into a decided item."""

    def test_the_line_names_the_evidence_and_the_consequence(self):
        e = {"severity": 0.85}
        _record_computed_evidence(e, kind="falsifier_refuted", by="Codex",
                                  detail="the claim may be sound")
        out = _rejection_lines(e)
        assert any("COMPUTED EVIDENCE ON FILE" in x for x in out)
        line = [x for x in out if "COMPUTED EVIDENCE" in x][0]
        assert "Codex" in line
        assert "not cleared automatically" in line
        assert "goes to a human" in line

    def test_a_finding_without_evidence_costs_nothing(self):
        assert _rejection_lines({"severity": 0.85}) == []

    def test_the_threshold_is_the_documented_one(self):
        assert CRITICAL_SEVERITY_THRESHOLD == 0.7
