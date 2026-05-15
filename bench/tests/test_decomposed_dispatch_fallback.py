"""Regression tests for the Phase-2-empty-synthesis fallback in
decomposed_dispatch.

Bug class: when Phase 2 synthesis returns empty content (model produces
zero characters despite Phase 1 chunks returning real analyses), the
runner previously recorded the empty as the canonical response and
discarded all Phase 1 content. Fix (15 May 2026): if synthesis is empty,
reconstruct the response from per_chunk_analyses.

Surfaced in Exp 40 Rounds 3 and 7 via Gemini-via-OpenRouter. Same fix
applied across `_decomposed_openrouter` and `_decomposed_deepseek` — both
dispatchers use the same Phase 1 (independent per-chunk analysis) + Phase
2 (synthesis) pattern with `per_chunk_analyses` aggregation.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))


def _make_chunk(label: str, content: str):
    """Construct a DecomposedChunk for testing. `chars` is a property,
    not a constructor argument."""
    from decomposed_dispatch import DecomposedChunk
    return DecomposedChunk(content=content, label=label)


def _make_response(content: str):
    """Construct a mock OpenAI ChatCompletion response with given content."""
    resp = MagicMock()
    choice = MagicMock()
    choice.message.content = content
    resp.choices = [choice]
    return resp


class TestOpenRouterSynthesisFallback:
    """OpenRouter dispatcher: Phase 2 empty → fallback to Phase 1 analyses."""

    def _setup_env_and_chunks(self):
        os.environ["OPENROUTER_API_KEY"] = "test_key_dummy"
        chunks = [
            _make_chunk("target_0", "def foo(): pass"),
            _make_chunk("target_1", "def bar(): return 42"),
        ]
        return chunks

    def test_empty_synthesis_falls_back_to_chunk_analyses(self):
        """When Phase 2 returns empty content but Phase 1 chunks had real
        analyses, the result_text is reconstructed from the chunks."""
        from decomposed_dispatch import _decomposed_openrouter

        chunks = self._setup_env_and_chunks()

        chunk1_analysis = (
            "**CODE REVIEW — SECTION 1 OF 2**\n\n"
            "### FINDING 1: Hypothetical issue in foo\n"
            "Detailed analysis content here for chunk 1."
        )
        chunk2_analysis = (
            "**CODE REVIEW — SECTION 2 OF 2**\n\n"
            "### FINDING 2: Hypothetical issue in bar\n"
            "Detailed analysis content here for chunk 2."
        )

        # Phase 1 responses (per chunk) then Phase 2 synthesis (empty).
        responses = [
            _make_response(chunk1_analysis),
            _make_response(chunk2_analysis),
            _make_response(""),  # Phase 2 synthesis returns empty
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = responses

        with patch("openai.OpenAI", return_value=mock_client):
            result = _decomposed_openrouter(
                model_id="google/gemini-3.1-pro-preview",
                system_prompt="system prompt",
                chunks=chunks,
                final_instruction="please synthesize",
                max_tokens=4096,
                timeout=30,
            )

        # Result must NOT be empty — fallback should have triggered.
        assert result.text, (
            "Phase 2 returned empty content but result.text is empty. "
            "Fallback to per_chunk_analyses did not trigger."
        )
        # Result must contain both chunk analyses.
        assert "target_0" in result.text
        assert "target_1" in result.text
        assert "FINDING 1: Hypothetical issue in foo" in result.text
        assert "FINDING 2: Hypothetical issue in bar" in result.text
        # Result should indicate fallback occurred.
        assert "synthesis returned empty" in result.text

    def test_non_empty_synthesis_uses_synthesis_content(self):
        """When Phase 2 returns real content, it is used as-is (no fallback
        triggered, no chunk-analysis concatenation)."""
        from decomposed_dispatch import _decomposed_openrouter

        chunks = self._setup_env_and_chunks()

        chunk1_analysis = "Chunk 1 analysis"
        chunk2_analysis = "Chunk 2 analysis"
        synthesis_output = (
            "## Combined Review\n\n"
            "Consolidated synthesis across both sections."
        )

        responses = [
            _make_response(chunk1_analysis),
            _make_response(chunk2_analysis),
            _make_response(synthesis_output),
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = responses

        with patch("openai.OpenAI", return_value=mock_client):
            result = _decomposed_openrouter(
                model_id="google/gemini-3.1-pro-preview",
                system_prompt="system prompt",
                chunks=chunks,
                final_instruction="please synthesize",
                max_tokens=4096,
                timeout=30,
            )

        # Result should be exactly the synthesis output (no fallback).
        assert result.text == synthesis_output
        # Should NOT contain the fallback marker.
        assert "synthesis returned empty" not in result.text

    def test_whitespace_only_synthesis_treated_as_empty(self):
        """Whitespace-only synthesis output should trigger fallback the same
        as a truly empty response."""
        from decomposed_dispatch import _decomposed_openrouter

        chunks = self._setup_env_and_chunks()

        chunk1_analysis = "Real chunk 1 content"

        responses = [
            _make_response(chunk1_analysis),
            _make_response("Real chunk 2 content"),
            _make_response("   \n\n  \t  \n"),  # whitespace only
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = responses

        with patch("openai.OpenAI", return_value=mock_client):
            result = _decomposed_openrouter(
                model_id="google/gemini-3.1-pro-preview",
                system_prompt="system prompt",
                chunks=chunks,
                final_instruction="please synthesize",
                max_tokens=4096,
                timeout=30,
            )

        # Result.text should NOT be just whitespace; fallback should have
        # populated it.
        assert result.text.strip(), (
            "Whitespace-only synthesis did not trigger fallback."
        )
        assert "Real chunk 1 content" in result.text

    def test_no_phase1_content_means_no_fallback_to_apply(self):
        """If Phase 1 chunks also returned empty AND synthesis returns
        empty, result.text stays empty (nothing to fall back to)."""
        from decomposed_dispatch import _decomposed_openrouter

        chunks = self._setup_env_and_chunks()

        responses = [
            _make_response(""),  # chunk 1 empty
            _make_response(""),  # chunk 2 empty
            _make_response(""),  # synthesis empty
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = responses

        with patch("openai.OpenAI", return_value=mock_client):
            result = _decomposed_openrouter(
                model_id="google/gemini-3.1-pro-preview",
                system_prompt="system prompt",
                chunks=chunks,
                final_instruction="please synthesize",
                max_tokens=4096,
                timeout=30,
            )

        # Genuine empty result is preserved when nothing to reconstruct.
        assert result.text == ""


class TestDeepSeekSynthesisFallback:
    """DeepSeek dispatcher: same fallback pattern across providers."""

    def test_empty_synthesis_falls_back_to_chunk_analyses(self):
        """Mirror of the openrouter test for the deepseek dispatcher."""
        from decomposed_dispatch import _decomposed_deepseek

        os.environ["DEEPSEEK_API_KEY"] = "test_key_dummy"
        chunks = [
            _make_chunk("target_0", "def foo(): pass"),
        ]

        chunk1_analysis = "DeepSeek analysis content for chunk 1"
        responses = [
            _make_response(chunk1_analysis),
            _make_response(""),  # Phase 2 synthesis returns empty
        ]

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = responses

        with patch("openai.OpenAI", return_value=mock_client):
            result = _decomposed_deepseek(
                model_id="deepseek-v4-pro",
                system_prompt="system prompt",
                chunks=chunks,
                final_instruction="please synthesize",
                max_tokens=4096,
                timeout=30,
            )

        assert result.text, (
            "DeepSeek dispatcher did not apply fallback when synthesis empty."
        )
        assert "DeepSeek analysis content for chunk 1" in result.text
        assert "synthesis returned empty" in result.text
