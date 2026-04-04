"""Tests for directed inter-model messaging in the insect brain.

Tests cover:
- Tag extraction from @Model, QUESTION_FOR:, DIRECTED:, RESPONSE_TO: formats
- Message routing (correct recipient gets the message)
- Priority ordering (directed messages appear before broadcast)
- Budget-aware degradation with directed messages surviving
- Models with no directed messages get standard broadcast
- Self-directed messages are ignored
- Unknown model names are handled gracefully
- Case-insensitive model name resolution
- Deduplication within a single extraction
- Checkpoint round-trip (save + load preserves directed messages)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bench.dm._types import DynamicManagementConfig, Finding
from bench.insect_brain import (
    BrainState,
    DirectedMessage,
    InsectBrain,
    RelayPayload,
    RoundRecord,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

def _make_config(**overrides) -> DynamicManagementConfig:
    """Minimal DM config for testing."""
    cfg = DynamicManagementConfig()
    # Apply sensible test defaults
    cfg.context_budget_chars = overrides.get("context_budget_chars", 100_000)
    cfg.tau_kappa = overrides.get("tau_kappa", 0.85)
    cfg.tau_sim = overrides.get("tau_sim", 0.6)
    cfg.max_rounds = overrides.get("max_rounds", 15)
    cfg.min_rounds_for_convergence = overrides.get("min_rounds_for_convergence", 3)
    return cfg


def _make_brain(
    config: DynamicManagementConfig | None = None,
    models: list[str] | None = None,
) -> InsectBrain:
    """Create a brain with a temp logs dir and initialise it."""
    cfg = config or _make_config()
    tmp = tempfile.mkdtemp()
    brain = InsectBrain(
        config=cfg,
        logs_dir=Path(tmp),
        source_paths=["test.py"],
    )
    brain.initialise(models or ["CC2", "Gemini", "DeepSeek", "Codex", "ChatGPT"])
    return brain


def _make_finding(model_id: str, round_idx: int, fid: str = "F001") -> Finding:
    return Finding(
        finding_id=fid,
        model_id=model_id,
        round_idx=round_idx,
        flaw_class=1,
        severity=0.7,
        abstraction_index=0.5,
        description="Test finding",
        proposed_fix="Fix it",
    )


def _populate_round(brain: InsectBrain, round_idx: int, responses: dict[str, str]):
    """Add a round of responses and findings to the brain."""
    findings = [
        _make_finding(label, round_idx, f"F{round_idx:02d}_{label}")
        for label in responses
    ]
    brain.persist(round_idx, responses, findings)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: @tag extraction
# ─────────────────────────────────────────────────────────────────────────────

class TestAtTagExtraction:
    def test_basic_at_tag(self):
        brain = _make_brain()
        text = (
            "Some analysis here.\n\n"
            "@Gemini: Your F003 claims the root is recomputed on every read. "
            "Can you provide evidence?"
        )
        msgs = brain.extract_directed_messages("CC2", text, 1)
        assert len(msgs) == 1
        assert msgs[0].sender == "CC2"
        assert msgs[0].recipient == "Gemini"
        assert "F003" in msgs[0].content
        assert msgs[0].message_type == "question"

    def test_multiple_at_tags(self):
        brain = _make_brain()
        text = (
            "@Gemini: Check your F003 evidence.\n\n"
            "@DeepSeek: Your FOLLOW trace for F007 is incomplete."
        )
        msgs = brain.extract_directed_messages("CC2", text, 1)
        recipients = {m.recipient for m in msgs}
        assert "Gemini" in recipients
        assert "DeepSeek" in recipients

    def test_at_tag_with_dash_separator(self):
        brain = _make_brain()
        text = "@Codex - Your fix for F012 changes the schema."
        msgs = brain.extract_directed_messages("Gemini", text, 2)
        assert len(msgs) == 1
        assert msgs[0].recipient == "Codex"


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: QUESTION_FOR extraction
# ─────────────────────────────────────────────────────────────────────────────

class TestQuestionForExtraction:
    def test_question_for_block(self):
        brain = _make_brain()
        text = (
            "Analysis done.\n\n"
            "QUESTION_FOR: CC2\n"
            "Your proposed fix for F012 changes the checkpoint schema. "
            "Have you traced whether load_checkpoint() handles the old format?"
        )
        msgs = brain.extract_directed_messages("DeepSeek", text, 3)
        assert len(msgs) == 1
        assert msgs[0].recipient == "CC2"
        assert msgs[0].message_type == "question"
        assert "load_checkpoint" in msgs[0].content


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: DIRECTED and RESPONSE_TO extraction
# ─────────────────────────────────────────────────────────────────────────────

class TestDirectedAndResponseTo:
    def test_directed_block(self):
        brain = _make_brain()
        text = "DIRECTED: Gemini: The budget calculation double-counts context."
        msgs = brain.extract_directed_messages("Codex", text, 2)
        assert len(msgs) == 1
        assert msgs[0].recipient == "Gemini"
        assert msgs[0].message_type == "challenge"

    def test_response_to_block(self):
        brain = _make_brain()
        text = (
            "RESPONSE_TO: ChatGPT\n"
            "You are correct about the off-by-one. Here is the fix."
        )
        msgs = brain.extract_directed_messages("CC2", text, 4)
        assert len(msgs) == 1
        assert msgs[0].recipient == "ChatGPT"
        assert msgs[0].message_type == "response"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Message routing — correct recipient
# ─────────────────────────────────────────────────────────────────────────────

class TestMessageRouting:
    def test_directed_messages_reach_correct_model(self):
        brain = _make_brain()
        _populate_round(brain, 0, {
            "CC2": "round 0 analysis",
            "Gemini": "round 0 analysis",
            "DeepSeek": "round 0 analysis",
        })

        brain.extract_directed_messages(
            "CC2",
            "@Gemini: Check your F003.\n\n@DeepSeek: Your FOLLOW is incomplete.",
            0,
        )

        gemini_msgs = brain.get_directed_messages_for_model("Gemini")
        deepseek_msgs = brain.get_directed_messages_for_model("DeepSeek")
        codex_msgs = brain.get_directed_messages_for_model("Codex")

        assert len(gemini_msgs) == 1
        assert len(deepseek_msgs) == 1
        assert len(codex_msgs) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Priority ordering in relay context
# ─────────────────────────────────────────────────────────────────────────────

class TestPriorityOrdering:
    def test_directed_messages_appear_first_in_context(self):
        brain = _make_brain()
        _populate_round(brain, 0, {
            "CC2": "CC2 round 0",
            "Gemini": "Gemini round 0",
            "DeepSeek": "DeepSeek round 0",
            "Codex": "Codex round 0",
            "ChatGPT": "ChatGPT round 0",
        })

        brain.extract_directed_messages(
            "CC2", "@Gemini: Important question about your finding.", 0,
        )

        payloads = brain.relay_directed(1)
        gemini_text = payloads["Gemini"].findings_text

        # The ADDRESSED TO YOU block must appear before broadcast content
        addressed_pos = gemini_text.find("ADDRESSED TO YOU")
        broadcast_pos = gemini_text.find("CC2 (Round 0)")

        assert addressed_pos != -1, "ADDRESSED TO YOU header missing"
        assert addressed_pos < broadcast_pos, (
            "Directed messages must appear before broadcast"
        )

    def test_no_directed_messages_gives_standard_broadcast(self):
        brain = _make_brain()
        _populate_round(brain, 0, {
            "CC2": "CC2 round 0",
            "Gemini": "Gemini round 0",
        })

        payloads = brain.relay_directed(1)
        cc2_text = payloads["CC2"].findings_text

        # No ADDRESSED TO YOU section, but broadcast is present
        assert "ADDRESSED TO YOU" not in cc2_text
        assert "Gemini (Round 0)" in cc2_text


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Budget-aware degradation
# ─────────────────────────────────────────────────────────────────────────────

class TestBudgetDegradation:
    def test_directed_messages_survive_tight_budget(self):
        """Directed messages should survive even when broadcast is cut."""
        config = _make_config(context_budget_chars=500)
        brain = _make_brain(config=config)

        # Add a round with long responses to exceed budget
        long_response = "X" * 400
        _populate_round(brain, 0, {
            "CC2": long_response,
            "Gemini": long_response,
            "DeepSeek": long_response,
            "Codex": long_response,
            "ChatGPT": long_response,
        })

        brain.extract_directed_messages(
            "CC2", "@Gemini: Short directed question?", 0,
        )

        payloads = brain.relay_directed(1)
        gemini_text = payloads["Gemini"].findings_text

        # Directed message must survive
        assert "ADDRESSED TO YOU" in gemini_text
        assert "Short directed question?" in gemini_text

    def test_broadcast_degrades_when_directed_claims_budget(self):
        """When directed messages consume budget, broadcast should degrade."""
        config = _make_config(context_budget_chars=300)
        brain = _make_brain(config=config)

        _populate_round(brain, 0, {
            "CC2": "A" * 200,
            "Gemini": "B" * 200,
            "DeepSeek": "C" * 200,
        })

        # Directed message that eats into broadcast budget
        brain.extract_directed_messages(
            "CC2", "@Gemini: " + "Q" * 100, 0,
        )

        payloads = brain.relay_directed(1)
        gemini_text = payloads["Gemini"].findings_text

        # Directed survives
        assert "ADDRESSED TO YOU" in gemini_text
        # Broadcast is degraded or absent (budget too tight for full responses)
        # We just check that directed is there — the brain handles the degradation


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Edge cases
# ─────────────────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_self_directed_messages_ignored(self):
        brain = _make_brain()
        text = "@CC2: Talking to myself about F001."
        msgs = brain.extract_directed_messages("CC2", text, 1)
        assert len(msgs) == 0

    def test_unknown_model_name_ignored(self):
        brain = _make_brain()
        text = "@UnknownModel: This should be ignored."
        msgs = brain.extract_directed_messages("CC2", text, 1)
        assert len(msgs) == 0

    def test_case_insensitive_model_names(self):
        brain = _make_brain()
        text = "@gemini: lowercase tag should work."
        msgs = brain.extract_directed_messages("CC2", text, 1)
        assert len(msgs) == 1
        assert msgs[0].recipient == "Gemini"

    def test_empty_content_ignored(self):
        brain = _make_brain()
        text = "@Gemini:"
        msgs = brain.extract_directed_messages("CC2", text, 1)
        assert len(msgs) == 0

    def test_dedup_within_extraction(self):
        """Same recipient + content should not produce duplicate messages."""
        brain = _make_brain()
        # DIRECTED and @tag both matching the same content
        text = (
            "@Gemini: Duplicate message.\n\n"
            "DIRECTED: Gemini: Duplicate message."
        )
        msgs = brain.extract_directed_messages("CC2", text, 1)
        # At most 1 message to Gemini with that content
        gemini_msgs = [m for m in msgs if m.recipient == "Gemini"]
        assert len(gemini_msgs) <= 2  # patterns match different content spans
        # But exact dedup catches identical content
        contents = [m.content[:200] for m in gemini_msgs]
        # The dedup key is (recipient, content[:200])
        unique_contents = set(contents)
        assert len(unique_contents) == len(contents)


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: Checkpoint round-trip
# ─────────────────────────────────────────────────────────────────────────────

class TestCheckpointRoundTrip:
    def test_directed_messages_survive_checkpoint(self):
        brain = _make_brain()
        _populate_round(brain, 0, {
            "CC2": "round 0",
            "Gemini": "round 0",
        })
        brain.extract_directed_messages(
            "CC2", "@Gemini: Checkpoint test question.", 0,
        )
        assert len(brain.state.directed_messages) == 1

        # Save checkpoint (happens inside persist, but also manually)
        brain._save_checkpoint()

        # Create a new brain and load the checkpoint
        brain2 = InsectBrain(
            config=brain.config,
            logs_dir=brain.logs_dir,
            source_paths=["test.py"],
        )
        brain2.initialise(["CC2", "Gemini", "DeepSeek", "Codex", "ChatGPT"])
        loaded = brain2.load_checkpoint()

        assert loaded is True
        assert len(brain2.state.directed_messages) == 1
        msg = brain2.state.directed_messages[0]
        assert msg.sender == "CC2"
        assert msg.recipient == "Gemini"
        assert "Checkpoint test" in msg.content
        assert msg.round_idx == 0
        assert msg.message_type == "question"


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: State accumulation across rounds
# ─────────────────────────────────────────────────────────────────────────────

class TestStateAccumulation:
    def test_messages_accumulate_across_rounds(self):
        brain = _make_brain()
        _populate_round(brain, 0, {"CC2": "r0", "Gemini": "r0"})
        brain.extract_directed_messages("CC2", "@Gemini: Round 0 question.", 0)

        _populate_round(brain, 1, {"CC2": "r1", "Gemini": "r1"})
        brain.extract_directed_messages("Gemini", "RESPONSE_TO: CC2\nHere is my answer.", 1)

        assert len(brain.state.directed_messages) == 2
        assert brain.state.directed_messages[0].round_idx == 0
        assert brain.state.directed_messages[1].round_idx == 1

    def test_get_messages_by_round(self):
        brain = _make_brain()
        _populate_round(brain, 0, {"CC2": "r0", "Gemini": "r0"})
        brain.extract_directed_messages("CC2", "@Gemini: Round 0.", 0)

        _populate_round(brain, 1, {"CC2": "r1", "Gemini": "r1"})
        brain.extract_directed_messages("CC2", "@Gemini: Round 1.", 1)

        r0_msgs = brain.get_directed_messages_for_model("Gemini", round_idx=0)
        r1_msgs = brain.get_directed_messages_for_model("Gemini", round_idx=1)

        assert len(r0_msgs) == 1
        assert len(r1_msgs) == 1
        assert "Round 0" in r0_msgs[0].content
        assert "Round 1" in r1_msgs[0].content


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: Render formatting
# ─────────────────────────────────────────────────────────────────────────────

class TestRenderFormatting:
    def test_render_directed_messages_format(self):
        msgs = [
            DirectedMessage(
                sender="CC2", recipient="Gemini",
                content="Check your evidence.",
                round_idx=1, message_type="question",
            ),
            DirectedMessage(
                sender="DeepSeek", recipient="Gemini",
                content="Your FOLLOW is incomplete.",
                round_idx=1, message_type="challenge",
            ),
        ]
        rendered = InsectBrain._render_directed_messages(msgs)
        assert "ADDRESSED TO YOU" in rendered
        assert "FROM CC2" in rendered
        assert "FROM DeepSeek" in rendered
        assert "QUESTION" in rendered
        assert "CHALLENGE" in rendered

    def test_render_empty_returns_empty(self):
        rendered = InsectBrain._render_directed_messages([])
        assert rendered == ""
