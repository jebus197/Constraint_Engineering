"""Regression tests for the Exp 40 continuation DeepSeek/Gemini
Phase-1 zero-char fix (Anomaly 1).

Root cause: Phase-1 per-chunk dispatch capped max_tokens at 4096.
DeepSeek V4 Pro and Gemini 3.1 Pro are reasoning models — they emit a
`reasoning_content` trace before the final `content`. A large chunk +
the full 4-Layer protocol prompt induces a long trace; the 4096
budget is exhausted before `content` is produced, so `content` is
empty and the actual review (in `reasoning_content`) was silently
discarded — the dispatchers only read `.content`.

Fix: (i) raise the Phase-1 cap to `_PHASE1_MAX_TOKENS`; (ii)
`_extract_message_text` falls back to `reasoning_content` (then
`reasoning`) when `content` is empty.

These tests pin the helper's resolution order and that both Phase-1
dispatch paths use the raised cap + the helper (source-truth, so a
refactor cannot silently reintroduce the data loss).
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


class TestExtractMessageText:
    def test_content_present_wins(self):
        m = _Msg(content="real findings", reasoning_content="trace")
        assert _extract_message_text(m) == "real findings"

    def test_empty_content_falls_back_to_reasoning_content(self):
        m = _Msg(content="", reasoning_content="FIND: off-by-one ...")
        assert _extract_message_text(m) == "FIND: off-by-one ..."

    def test_none_content_falls_back(self):
        m = _Msg(content=None, reasoning_content="analysis text")
        assert _extract_message_text(m) == "analysis text"

    def test_reasoning_alt_attribute(self):
        # Some OpenAI-compatible routes expose the trace as `reasoning`.
        m = _Msg(content="", reasoning_content=None, reasoning="alt")
        assert _extract_message_text(m) == "alt"

    def test_whitespace_only_content_treated_empty(self):
        m = _Msg(content="   \n  ", reasoning_content="substantive")
        assert _extract_message_text(m) == "substantive"

    def test_all_empty_returns_empty_string(self):
        assert _extract_message_text(_Msg()) == ""

    def test_missing_attributes_safe(self):
        class Bare:
            pass

        # No content/reasoning attrs at all → empty string, no crash.
        assert _extract_message_text(Bare()) == ""


class TestPhase1CapRaised:
    def test_cap_is_above_old_4096(self):
        assert _PHASE1_MAX_TOKENS > 4096, (
            "Phase-1 cap must exceed the old 4096 that starved "
            "reasoning models of content-token budget"
        )

    def test_both_phase1_paths_use_the_constant(self):
        src = Path(decomposed_dispatch.__file__).read_text()
        # Both Phase-1 loops must pass the constant as the max_tokens
        # argument.
        assert src.count("max_tokens=_PHASE1_MAX_TOKENS") >= 2, (
            "both the OpenRouter and DeepSeek Phase-1 loops must use "
            "_PHASE1_MAX_TOKENS"
        )
        # No LIVE dispatch call may still hardcode 4096. A historical
        # comment may reference the old value for context; only flag
        # an actual `max_tokens=4096` argument (followed by a comma —
        # i.e. a kwargs call-site, not prose).
        assert "max_tokens=4096," not in src, (
            "no Phase-1 dispatch call may still hardcode the old 4096 "
            "cap as a kwarg"
        )

    def test_both_paths_use_extract_helper(self):
        src = Path(decomposed_dispatch.__file__).read_text()
        # Helper must be called in both Phase-1 loops (≥2 call-sites
        # plus the definition = ≥3 occurrences).
        assert src.count("_extract_message_text") >= 3, (
            "both Phase-1 loops must route message text through "
            "_extract_message_text so reasoning-trace fallback "
            "applies symmetrically"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
