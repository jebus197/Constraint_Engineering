"""Regression test: the reasoning-trace bypass in
`_extract_message_text` is removed (founder-directed, 2026-05-20).

History. A prior session (Exp 40 continuation, 2026-05-15) added a
fallback in `_extract_message_text` so that when a reasoning model's
visible `content` came back empty the function returned the model's
`reasoning_content` (chain-of-thought) instead. The rationale at the
time was that the trace contained substantive analysis. The founder
subsequently rejected that approach on two grounds: (1) reasoning
traces are often weakly coupled to the model's actual conclusion (the
visible trace is partly performative and not a faithful causal record
of the answer-generating computation), so substituting it for the
answer is methodologically unsound; (2) it silently bypassed the
established ITC retry / restart-fresh protocol that exists for empty
responses (see `memory/feedback_no_benching.md`).

These tests pin the corrected behaviour:
  - `_extract_message_text` returns content only (no `reasoning_content`
    or `reasoning` fallback).
  - Empty `content` returns the empty string and propagates to the
    runner, where it is classified by ITC as TRANSIENT_FAILURE and
    triggers restart_fresh.
  - The `_PHASE1_MAX_TOKENS` cap is preserved (structurally useful for
    reasoning models, not a bypass).
  - The helper is still routed through both Phase-1 dispatch loops.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bench import decomposed_dispatch
from bench.decomposed_dispatch import (
    _PHASE1_MAX_TOKENS,
    _extract_message_text,
)


class _Msg:
    def __init__(self, content=None, reasoning_content=None, reasoning=None):
        self.content = content
        self.reasoning_content = reasoning_content
        self.reasoning = reasoning


class TestExtractMessageTextContentOnly:
    """Pin the content-only contract — no fallback to reasoning_content
    or reasoning, regardless of whether they are populated."""

    def test_content_present_returns_content(self):
        m = _Msg(content="real findings", reasoning_content="trace")
        assert _extract_message_text(m) == "real findings"

    def test_empty_content_returns_empty_not_reasoning(self):
        # The crucial regression: even when reasoning_content is rich,
        # an empty `content` must return "" so the empty propagates to
        # ITC, not a substituted trace.
        m = _Msg(content="", reasoning_content="FIND: off-by-one ...")
        assert _extract_message_text(m) == "", (
            "empty content must not be silently replaced by "
            "reasoning_content — that is the bypass that was removed"
        )

    def test_none_content_returns_empty_not_reasoning(self):
        m = _Msg(content=None, reasoning_content="analysis text")
        assert _extract_message_text(m) == ""

    def test_reasoning_alt_attribute_not_consulted(self):
        # Some OpenAI-compatible routes expose the trace as `reasoning`;
        # that path must also not be used as a content substitute.
        m = _Msg(content="", reasoning_content=None, reasoning="alt trace")
        assert _extract_message_text(m) == ""

    def test_whitespace_only_content_treated_empty(self):
        # Whitespace-only content is empty after .strip(); must not
        # fall back to reasoning_content.
        m = _Msg(content="   \n  ", reasoning_content="substantive")
        assert _extract_message_text(m) == ""

    def test_all_empty_returns_empty_string(self):
        assert _extract_message_text(_Msg()) == ""

    def test_missing_attributes_safe(self):
        class Bare:
            pass
        # No content/reasoning attrs at all → empty string, no crash.
        assert _extract_message_text(Bare()) == ""


class TestPhase1CapRetained:
    """The Phase-1 max_tokens cap (raised from 4096 → 8192) is retained
    as structurally useful for reasoning models. It is not the bypass —
    the bypass was the trace-substitution in `_extract_message_text`."""

    def test_cap_is_above_old_4096(self):
        assert _PHASE1_MAX_TOKENS > 4096, (
            "Phase-1 cap must exceed the old 4096 that starved "
            "reasoning models of content-token budget"
        )

    def test_both_phase1_paths_use_the_constant(self):
        """Both Phase-1 loops must derive their budget from the constant.

        This asserted a source substring (`max_tokens=_PHASE1_MAX_TOKENS`,
        twice) until the falsifier-gate work routed both call sites through
        `_gate_turn_budget`, which returns the constant when the gate is off.
        The invariant held; the string test broke. Rewritten to check the
        behaviour and the call sites via the AST, so a future refactor that
        preserves the cap does not fail and one that drops it does.
        """
        import ast

        src = Path(decomposed_dispatch.__file__).read_text()

        # Gate OFF must still yield exactly the legacy per-turn cap.
        assert decomposed_dispatch._gate_turn_budget(8192, False) == _PHASE1_MAX_TOKENS
        assert decomposed_dispatch._gate_turn_budget(999999, False) == _PHASE1_MAX_TOKENS
        # Gate ON must never drop BELOW the caller's own budget.
        assert decomposed_dispatch._gate_turn_budget(65536, True) >= 65536

        # Both Phase-1 dispatch sites must take their budget from the helper
        # (or the constant directly) — not from an inlined literal.
        tree = ast.parse(src)
        derived = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.keyword) or node.arg != "max_tokens":
                continue
            text = ast.unparse(node.value)
            if "_gate_turn_budget" in text or "_PHASE1_MAX_TOKENS" in text:
                derived += 1
        assert derived >= 2, (
            "both the OpenRouter and DeepSeek Phase-1 loops must derive "
            f"max_tokens from _gate_turn_budget/_PHASE1_MAX_TOKENS; found {derived}"
        )

        # No LIVE dispatch call may still hardcode the starving 4096 budget.
        assert "max_tokens=4096," not in src

    def test_both_paths_still_use_extract_helper(self):
        # The helper survives (centralised content extraction); only
        # its fallback was removed.
        src = Path(decomposed_dispatch.__file__).read_text()
        assert src.count("_extract_message_text") >= 3, (
            "both Phase-1 loops must route message text through "
            "_extract_message_text"
        )


class TestNoReasoningFallbackInSource:
    """Source-truth pin: the removed bypass cannot be silently
    reintroduced by a future refactor."""

    def test_no_reasoning_content_in_extract_helper_body(self):
        import inspect
        src = inspect.getsource(_extract_message_text)
        # The body must not reference `reasoning_content` or `reasoning`
        # as response sources. (Comments / docstrings can mention them
        # historically; check for actual attribute access patterns.)
        assert 'getattr(message, "reasoning_content"' not in src, (
            "reasoning_content fallback must not be reintroduced — it "
            "was the bypass the founder rejected"
        )
        assert 'getattr(message, "reasoning"' not in src, (
            "reasoning fallback must not be reintroduced"
        )

    def test_phase1_log_lines_do_not_mention_recovery(self):
        # The "recovered N chars from reasoning trace" log lines were
        # dead code after the helper became content-only — pin their
        # absence so they don't return.
        src = Path(decomposed_dispatch.__file__).read_text()
        assert "recovered" not in src or \
            "chars from reasoning trace" not in src, (
                "recovery-from-reasoning-trace log lines must not be "
                "reintroduced — they only logged the bypass that was "
                "removed"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
