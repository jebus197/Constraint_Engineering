"""External text must not be able to kill a round, a log, or a report.

The three boundaries measured on 2026-07-31 are asserted here as facts about
Python, not as beliefs about it — if any of them stops raising, the guard that
protects it has become dead weight and these tests will say so.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.text_safety import (  # noqa: E402
    has_unencodable, scrub_surrogates, scrub_deep, REPLACEMENT,
)

LONE = "\ud835"  # the one that actually turned up, from PDF-extracted maths


class TestThePremise:
    """Why this module exists. Each is the real failure, reproduced."""

    def test_a_lone_surrogate_cannot_be_encoded(self):
        with pytest.raises(UnicodeEncodeError):
            f"brief: {LONE}(x)".encode("utf-8")

    def test_it_kills_a_subprocess_prompt(self):
        """CC2 and Codex are dispatched by piping the prompt to stdin."""
        with pytest.raises(UnicodeEncodeError):
            subprocess.run(["cat"], input=f"prompt {LONE}", capture_output=True,
                           text=True, timeout=10)

    def test_it_kills_a_log_write(self, tmp_path):
        with pytest.raises(UnicodeEncodeError):
            (tmp_path / "run.log").write_text(f"round 3: {LONE}", encoding="utf-8")

    def test_the_json_body_survives_only_because_of_ensure_ascii(self):
        """The one boundary that does not raise — and why that is not a defence."""
        json.dumps({"content": f"x{LONE}"}).encode("utf-8")  # no raise
        with pytest.raises(UnicodeEncodeError):
            json.dumps({"content": f"x{LONE}"}, ensure_ascii=False).encode("utf-8")

    def test_scrubbing_fixes_all_of_them(self, tmp_path):
        safe = scrub_surrogates(f"brief: {LONE}(x)", "test", log=lambda m: None)
        safe.encode("utf-8")
        subprocess.run(["cat"], input=safe, capture_output=True, text=True, timeout=10)
        (tmp_path / "run.log").write_text(safe, encoding="utf-8")
        json.dumps({"c": safe}, ensure_ascii=False).encode("utf-8")


class TestCleanTextIsUntouched:
    """The guard sits on every piece of external text, so it must cost nothing."""

    CLEAN = [
        "γ_critical rose to 0.621",          # Greek — legitimate, must survive
        "a — b, naïve, £40, 中文",            # assorted non-ASCII
        "𝛾 is the decay curve",              # astral plane, correctly encoded
        "plain ascii",
        "",
    ]

    @pytest.mark.parametrize("text", CLEAN)
    def test_clean_text_is_returned_unchanged(self, text):
        assert scrub_surrogates(text, "t") == text
        assert not has_unencodable(text)

    def test_a_clean_string_is_returned_as_the_same_object(self):
        """Identity, not equality — no allocation on the common path."""
        s = "γ_critical rose to 0.621"
        assert scrub_surrogates(s, "t") is s

    def test_an_astral_character_is_not_mistaken_for_a_surrogate(self):
        """U+1D6FE is stored as ONE codepoint in Python, not as a pair.

        If it were stored as a pair this guard would corrupt every maths symbol
        in the corpus, which is the failure mode worth being certain about.
        """
        gamma = "\U0001d6fe"
        assert len(gamma) == 1
        assert not has_unencodable(gamma)
        assert scrub_surrogates(gamma, "t") is gamma
        gamma.encode("utf-8")


class TestScrubbing:
    def test_the_surrogate_is_replaced_and_the_rest_is_kept(self):
        out = scrub_surrogates(f"The paper defines {LONE}(x) as γ.", "t",
                               log=lambda m: None)
        assert out == f"The paper defines {REPLACEMENT}(x) as γ."
        out.encode("utf-8")

    def test_every_surrogate_is_replaced(self):
        out = scrub_surrogates(f"{LONE}a\udc00b\udbff", "t", log=lambda m: None)
        assert not has_unencodable(out)
        assert out.count(REPLACEMENT) == 3

    def test_the_degradation_is_announced(self):
        seen = []
        scrub_surrogates(f"x{LONE}y", "ouroboros brief", log=seen.append)
        assert len(seen) == 1
        assert "1 unpaired surrogate" in seen[0]
        assert "ouroboros brief" in seen[0], "the warning must name the source"

    def test_nothing_is_announced_for_clean_text(self):
        seen = []
        scrub_surrogates("γ is fine", "t", log=seen.append)
        assert seen == []

    def test_it_is_idempotent(self):
        once = scrub_surrogates(f"x{LONE}y", "t", log=lambda m: None)
        assert scrub_surrogates(once, "t") is once


class TestScrubDeep:
    def test_it_reaches_a_surrogate_at_any_depth(self):
        payload = {"papers": [{"title": "Ok", "body": f"defines {LONE}(x)"}],
                   "count": 1, "ok": None}
        out = scrub_deep(payload, "t", log=lambda m: None)
        json.dumps(out, ensure_ascii=False).encode("utf-8")
        assert out["papers"][0]["body"] == f"defines {REPLACEMENT}(x)"

    def test_non_string_values_are_preserved_exactly(self):
        payload = {"n": 3, "f": 0.621, "b": True, "none": None,
                   "t": (1, 2), "l": [1, {"x": "γ"}]}
        assert scrub_deep(payload, "t") == payload

    def test_a_surrogate_in_a_key_is_scrubbed_too(self):
        out = scrub_deep({f"k{LONE}": "v"}, "t", log=lambda m: None)
        json.dumps(out, ensure_ascii=False).encode("utf-8")
        assert list(out) == [f"k{REPLACEMENT}"]
