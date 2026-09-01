"""One model challenging three times is one dissenter, not three.

`FindingRegistry.auto_resolve_contested` refutes a contested finding when it sees
three challenges and no defences in the recent-round window.  Until 2026-09-01 it
counted *verdict rows*, so a single model that challenged the same finding in
three consecutive rounds refuted it on its own.  That is a self-consensus path:
the finding is deleted by one voice repeating itself.

Measured against the archive at the time of the fix: of 66 archived findings
carrying three or more CHALLENGE rows, 1 was REFUTED or CONTESTED with fewer
than three distinct challengers (1.5%, Wilson [0.3%, 8.1%]).  Small, but the
mechanism is a vote-deletion path and the project does not confirm or delete
findings by vote at all -- see MEMORY `feedback_no_model_voting`.

The fix counts distinct `model` values.  These tests pin both directions: the
lone repeater must not refute, and three genuine dissenters still must.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import reference_runner_v3 as R  # noqa: E402


def _contested_finding(verdicts):
    """Build a CONTESTED finding carrying `verdicts` as (model, round) pairs.

    Returns the registry status after `auto_resolve_contested(2)`.  Only
    CONTESTED entries are considered by that method, so the status is set
    explicitly -- a finding left OPEN is skipped and every case would pass
    vacuously.
    """
    registry = R.FindingRegistry()
    finding = R.Finding(
        finding_id="M_F001",
        model_id="M",
        round_idx=0,
        flaw_class=1,
        severity=0.9,
        abstraction_index=0.5,
        description="a finding that several rounds argue about",
        verified=False,
        origin_type="model",
    )
    registry.register(finding, "M")
    cid = next(iter(registry.entries))
    registry.entries[cid]["status"] = "CONTESTED"
    for model, round_idx in verdicts:
        registry.add_verdict(cid, model, "CHALLENGE", round_idx, evidence="e")
    registry.auto_resolve_contested(2)
    return registry.entries[cid].get("status")


class TestOneVoiceRepeatingIsNotAPanel:
    def test_one_model_across_three_rounds_does_not_refute(self):
        """The defect this file exists for: three rows, one dissenter."""
        assert _contested_finding(
            [("Solo", 0), ("Solo", 1), ("Solo", 2)]
        ) == "CONTESTED"

    def test_two_models_with_four_rows_do_not_refute(self):
        """Row count clears the bar; distinct-model count does not."""
        assert _contested_finding(
            [("CC2", 1), ("CC2", 2), ("Gemini", 1), ("Gemini", 2)]
        ) == "CONTESTED"


class TestThreeGenuineDissentersStillRefute:
    def test_three_distinct_models_refute(self):
        """The legitimate path must survive the fix."""
        assert _contested_finding(
            [("CC2", 1), ("Gemini", 1), ("Codex", 1)]
        ) == "REFUTED"

    def test_three_distinct_models_spread_across_rounds_refute(self):
        assert _contested_finding(
            [("CC2", 0), ("Gemini", 1), ("Codex", 2)]
        ) == "REFUTED"


class TestSeatsAreNotModels:
    """Two seats can run one model. Counting seats over-counts dissent.

    Found by CC2 in panel review on 2026-09-01, against the distinct-model fix
    made the same day. In the live config `Codex` and `ChatGPT` both declare
    `model_id="openai/gpt-5.5"`. Measured over the archive: of 103 findings
    challenged by three or more distinct seat LABELS, 21 had fewer than three
    distinct underlying models -- 20.4%, Wilson [13.7%, 29.2%].
    """

    def _with_identity(self, identity, verdicts):
        registry = R.FindingRegistry()
        finding = R.Finding(
            finding_id="M_F001", model_id="M", round_idx=0, flaw_class=1,
            severity=0.9, abstraction_index=0.5,
            description="a finding challenged by seats, not models",
            verified=False, origin_type="model")
        registry.register(finding, "M")
        cid = next(iter(registry.entries))
        registry.entries[cid]["status"] = "CONTESTED"
        registry.model_identity = identity
        for model, round_idx in verdicts:
            registry.add_verdict(cid, model, "CHALLENGE", round_idx, evidence="e")
        registry.auto_resolve_contested(2)
        return registry.entries[cid].get("status")

    LIVE_SEATS = {"Codex": "openai/gpt-5.5", "ChatGPT": "openai/gpt-5.5",
                  "CC2": "anthropic/claude-opus", "Gemini": "google/gemini"}

    def test_two_seats_on_one_model_are_one_dissenter(self):
        assert self._with_identity(
            self.LIVE_SEATS,
            [("Codex", 1), ("ChatGPT", 1), ("CC2", 1)]) == "CONTESTED", (
            "Codex and ChatGPT run the same model; that is two voices, not three")

    def test_three_genuinely_distinct_models_still_refute(self):
        assert self._with_identity(
            self.LIVE_SEATS,
            [("Codex", 1), ("CC2", 1), ("Gemini", 1)]) == "REFUTED"

    def test_an_empty_identity_map_falls_back_to_seat_labels(self):
        """Unknown identity must not invent distinctness, nor lose the old path."""
        assert self._with_identity(
            {}, [("Codex", 1), ("ChatGPT", 1), ("CC2", 1)]) == "REFUTED"

    def test_an_unknown_seat_resolves_to_itself(self):
        registry = R.FindingRegistry()
        registry.model_identity = self.LIVE_SEATS
        assert registry.resolve_model("Fable") == "Fable"
        assert registry.resolve_model("Codex") == "openai/gpt-5.5"
        assert registry.resolve_model("codex") == "openai/gpt-5.5"
        assert registry.resolve_model(None) == ""


class TestTheTallyReadsTheModelField:
    def test_verdicts_without_a_model_field_do_not_stack(self):
        """A missing model is one bucket (None), not N anonymous dissenters.

        Verdicts arriving without provenance must not be able to refute a
        finding by weight of numbers.  They collapse to a single `None` key.
        """
        registry = R.FindingRegistry()
        finding = R.Finding(
            finding_id="M_F001",
            model_id="M",
            round_idx=0,
            flaw_class=1,
            severity=0.9,
            abstraction_index=0.5,
            description="a finding challenged by nobody in particular",
            verified=False,
            origin_type="model",
        )
        registry.register(finding, "M")
        cid = next(iter(registry.entries))
        registry.entries[cid]["status"] = "CONTESTED"
        registry.entries[cid]["verdicts"] = [
            {"verdict": "CHALLENGE", "round": 1, "evidence": "e"},
            {"verdict": "CHALLENGE", "round": 1, "evidence": "e"},
            {"verdict": "CHALLENGE", "round": 2, "evidence": "e"},
        ]
        registry.auto_resolve_contested(2)
        assert registry.entries[cid].get("status") == "CONTESTED"


class TestADefenceStillBlocksRefutation:
    def test_three_challengers_and_one_defender_do_not_refute(self):
        """The `confirms == 0` half of the condition is untouched by the fix."""
        registry = R.FindingRegistry()
        finding = R.Finding(
            finding_id="M_F001",
            model_id="M",
            round_idx=0,
            flaw_class=1,
            severity=0.9,
            abstraction_index=0.5,
            description="a finding with one defender left standing",
            verified=False,
            origin_type="model",
        )
        registry.register(finding, "M")
        cid = next(iter(registry.entries))
        registry.entries[cid]["status"] = "CONTESTED"
        for model in ("CC2", "Gemini", "Codex"):
            registry.add_verdict(cid, model, "CHALLENGE", 1, evidence="e")
        registry.add_verdict(cid, "Fable", "CONFIRM", 1, evidence="e")
        registry.auto_resolve_contested(2)
        assert registry.entries[cid].get("status") == "CONTESTED"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
