"""Regression test: the Phase-2 synthesis chunk-analyses reconstruction
in `_decomposed_openrouter` / `_decomposed_deepseek` is removed
(founder-directed, 2026-05-20).

History. Commit 35c44b6 (15 May 2026) added a fallback in both
dispatchers: when Phase 2 synthesis came back with empty `content`, the
dispatcher concatenated the Phase-1 per-chunk analyses into a synthetic
`result_text` and returned it as the model's answer. The premise was
that this preserved real chunk content rather than losing it to an
empty synthesis. The founder rejected this on the same grounds as the
reasoning-trace bypass: the per-chunk analyses are intermediate working
output, not the model's actual synthesised conclusion, and substituting
them silently bypassed the ITC retry / restart-fresh protocol that
exists for empty responses (see `memory/feedback_no_benching.md`).

These tests pin the corrected behaviour:
  - Empty Phase-2 synthesis → `result.text == ""` (no reconstruction
    from chunk analyses). Empty propagates to the runner, which
    classifies it via ITC and adapts via restart_fresh on the next
    round.
  - Non-empty synthesis is returned unchanged.
  - Whitespace-only synthesis is treated as empty (after .strip()).
  - The reconstruction code paths are absent from source.
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
    from decomposed_dispatch import DecomposedChunk
    return DecomposedChunk(content=content, label=label)


def _make_response(content: str):
    resp = MagicMock()
    choice = MagicMock()
    choice.message.content = content
    # Ensure mock doesn't auto-populate reasoning_content / reasoning;
    # the new helper is content-only but the mock shouldn't accidentally
    # supply attributes that would trip future re-checks.
    choice.message.reasoning_content = None
    choice.message.reasoning = None
    resp.choices = [choice]
    return resp


class TestOpenRouterSynthesisNoReconstruction:
    """OpenRouter dispatcher: empty Phase-2 → empty result.text (no
    chunk-analyses reconstruction)."""

    def _setup_env_and_chunks(self):
        os.environ["OPENROUTER_API_KEY"] = "test_key_dummy"
        chunks = [
            _make_chunk("target_0", "def foo(): pass"),
            _make_chunk("target_1", "def bar(): return 42"),
        ]
        return chunks

    def test_empty_synthesis_returns_empty_text(self):
        """The crucial regression: empty Phase-2 synthesis must NOT be
        silently replaced by concatenated Phase-1 chunk analyses. The
        empty must propagate so the runner's ITC protocol can engage."""
        from decomposed_dispatch import _decomposed_openrouter

        chunks = self._setup_env_and_chunks()
        responses = [
            _make_response("Phase 1 chunk-0 analysis content here."),
            _make_response("Phase 1 chunk-1 analysis content here."),
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

        assert result.text == "", (
            "empty Phase-2 synthesis must propagate as empty result.text "
            "— the chunk-analyses reconstruction was removed because it "
            "silently bypassed ITC"
        )
        # And the fabricated "synthesis returned empty, chunk content
        # preserved" marker must NOT appear:
        assert "chunk content preserved" not in result.text

    def test_non_empty_synthesis_returned_unchanged(self):
        from decomposed_dispatch import _decomposed_openrouter

        chunks = self._setup_env_and_chunks()
        synthesis_output = (
            "## Combined Review\n\nConsolidated synthesis output."
        )
        responses = [
            _make_response("Chunk 1 analysis"),
            _make_response("Chunk 2 analysis"),
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

        assert result.text == synthesis_output
        assert "chunk content preserved" not in result.text

    def test_whitespace_only_synthesis_treated_as_empty(self):
        from decomposed_dispatch import _decomposed_openrouter

        chunks = self._setup_env_and_chunks()
        responses = [
            _make_response("Chunk 1 content"),
            _make_response("Chunk 2 content"),
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

        # After .strip(), whitespace-only is empty — no reconstruction.
        assert result.text == ""
        assert "Chunk 1 content" not in result.text

    def test_all_empty_returns_empty(self):
        from decomposed_dispatch import _decomposed_openrouter

        chunks = self._setup_env_and_chunks()
        responses = [
            _make_response(""),
            _make_response(""),
            _make_response(""),
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

        assert result.text == ""


class TestDeepSeekSynthesisNoReconstruction:
    """DeepSeek dispatcher mirror: empty synthesis → empty result.text."""

    def test_empty_synthesis_returns_empty_text(self):
        from decomposed_dispatch import _decomposed_deepseek

        os.environ["DEEPSEEK_API_KEY"] = "test_key_dummy"
        chunks = [_make_chunk("target_0", "def foo(): pass")]
        responses = [
            _make_response("DeepSeek chunk 1 analysis"),
            _make_response(""),  # Phase 2 synthesis empty
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

        assert result.text == ""
        assert "chunk content preserved" not in result.text


class TestNoReconstructionInSource:
    """Source-truth pin: the synthesis-layer reconstruction must not be
    silently reintroduced."""

    def test_no_chunk_analyses_reconstruction_in_source(self):
        src = Path(REPO_ROOT / "bench" / "decomposed_dispatch.py").read_text()
        # The reconstruction wrote a "synthesis returned empty, chunk
        # content preserved" marker — pin its absence.
        assert "synthesis returned empty, chunk content preserved" not in src
        # The "reconstructed from N chunk analyses" log line was the
        # reconstruction's signature — also pin its absence.
        assert "reconstructed from" not in src or \
            "chunk analyses" not in src, (
                "the chunk-analyses reconstruction (commit 35c44b6) "
                "must not be reintroduced — it silently bypassed ITC"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
