"""Tests for the broadened verdict parser (Item 1D.6).

The parser must cover Gemini format variations (bold-wrapped keyword,
bullet+bold, numbered lists, blockquotes, colon/period separators) while
still rejecting prose mentions of verdicts (backtick-wrapped examples,
mid-line references inside FOLLOW/FALSIFIER/ATTEMPT sections).
"""

from __future__ import annotations

import pytest

from bench.reference_runner_v3 import _VERDICT_RE, _parse_verdicts


def _match(line: str):
    return _VERDICT_RE.match(line)


class TestBaselineFormats:
    """Regression coverage for formats that already worked."""

    def test_ascii_dash(self):
        m = _match("CONFIRM C0001 - description")
        assert m is not None
        assert m.groups() == ("CONFIRM", "C0001", "description")

    def test_em_dash(self):
        m = _match("CONFIRM C0001 \u2014 description")
        assert m is not None
        assert m.group(3) == "description"

    def test_pipe_separator(self):
        m = _match("CONFIRM C0001 | description")
        assert m is not None
        assert m.group(3) == "description"

    def test_merge_with_arrow_evidence(self):
        m = _match("MERGE C0024 <- C0012 \u2014 Duplicate of settled finding.")
        assert m is not None
        assert m.group(1) == "MERGE"
        assert m.group(2) == "C0024"
        assert m.group(3).startswith("C0012")

    def test_indented(self):
        m = _match("  CONFIRM C0001 \u2014 description")
        assert m is not None
        assert m.group(2) == "C0001"


class TestBoldWrappedKeyword:
    """Gemini frequently wraps the keyword in bold/italic."""

    def test_double_asterisk_keyword_only(self):
        m = _match("**CONFIRM** C0001 \u2014 description")
        assert m is not None
        assert m.group(1) == "CONFIRM"
        assert m.group(2) == "C0001"
        assert m.group(3) == "description"

    def test_double_asterisk_whole_header(self):
        m = _match("**CONFIRM C0001** \u2014 description")
        assert m is not None
        assert m.group(3) == "description"

    def test_whole_line_bold(self):
        m = _match("**CONFIRM C0001 \u2014 description**")
        assert m is not None
        # Trailing ** must be stripped from description.
        results = _parse_verdicts("**CONFIRM C0001 \u2014 description**", "Gemini", 0)
        assert len(results) == 1
        assert results[0] == ("CONFIRM", "C0001", "description")

    def test_underscore_italic(self):
        m = _match("_CONFIRM_ C0001 \u2014 description")
        assert m is not None
        assert m.group(1) == "CONFIRM"

    def test_double_underscore_bold(self):
        m = _match("__CONFIRM__ C0001 \u2014 description")
        assert m is not None
        assert m.group(1) == "CONFIRM"


class TestListPrefixes:

    def test_bullet_dash_plain(self):
        m = _match("- CONFIRM C0001 \u2014 description")
        assert m is not None
        assert m.group(2) == "C0001"

    def test_bullet_asterisk(self):
        m = _match("* CONFIRM C0001 \u2014 description")
        assert m is not None

    def test_bullet_dash_bold_keyword(self):
        m = _match("- **CONFIRM** C0001: description")
        assert m is not None
        assert m.group(3) == "description"

    def test_numbered_list_dot(self):
        m = _match("1. CONFIRM C0001 \u2014 description")
        assert m is not None
        assert m.group(2) == "C0001"

    def test_numbered_list_paren(self):
        m = _match("1) CONFIRM C0001 \u2014 description")
        assert m is not None

    def test_numbered_list_multi_digit(self):
        m = _match("42. CONFIRM C0042 \u2014 description")
        assert m is not None
        assert m.group(2) == "C0042"

    def test_blockquote(self):
        m = _match("> CONFIRM C0001 \u2014 description")
        assert m is not None
        assert m.group(2) == "C0001"

    def test_blockquote_with_bold(self):
        m = _match("> **CONFIRM** C0001 \u2014 description")
        assert m is not None


class TestDescriptionSeparators:
    """Colon, period, space-only separators must capture description."""

    def test_colon_separator(self):
        m = _match("CONFIRM C0001: description")
        assert m is not None
        assert m.group(3) == "description"

    def test_period_separator(self):
        m = _match("CONFIRM C0001. description")
        assert m is not None
        assert m.group(3) == "description"

    def test_em_dash_unicode(self):
        m = _match("CONFIRM C0001 \u2014 description")
        assert m is not None

    def test_en_dash_unicode(self):
        m = _match("CONFIRM C0001 \u2013 description")
        assert m is not None


class TestNonMatches:
    """Prose mentions must not parse as verdicts."""

    def test_backtick_wrapped_verdict_in_prose(self):
        # The FOLLOW/FALSIFIER pattern — inline code mentions of verdicts.
        text = "FOLLOW: The `_VERDICT_AS_FINDING` check only works in marker parser. "\
               "If a model outputs `CONFIRM C0042` inside JSON, it will fail."
        assert _match(text) is None
        assert _parse_verdicts(text, "Gemini", 0) == []

    def test_mid_line_reference(self):
        text = "The verdict was CONFIRM C0042 but review suggests otherwise."
        assert _match(text) is None

    def test_json_string_literal(self):
        text = '"DESCRIPTION": "CONFIRM C0042"'
        assert _match(text) is None

    def test_non_verdict_keyword(self):
        assert _match("CONFIRMED C0001 \u2014 description") is None
        assert _match("CHALLENGES C0001 \u2014 description") is None

    def test_id_too_short(self):
        # C\d{4,} requires at least 4 digits.
        assert _match("CONFIRM C001 \u2014 description") is None


class TestParseVerdictsMultiline:
    """End-to-end parse on multi-line response."""

    def test_finds_all_gemini_format_variants(self):
        text = """
Summary of verdicts:

- **CONFIRM** C0001: description A
1. **CONFIRM** C0002 \u2014 description B
> CHALLENGE C0003 | reason
**MERGE C0024** <- C0012 \u2014 duplicate

Some prose mentioning `CONFIRM C0999` in an example.
"""
        results = _parse_verdicts(text, "Gemini", 0)
        verdict_ids = {(r[0], r[1]) for r in results}
        assert ("CONFIRM", "C0001") in verdict_ids
        assert ("CONFIRM", "C0002") in verdict_ids
        assert ("CHALLENGE", "C0003") in verdict_ids
        assert ("MERGE", "C0024") in verdict_ids
        # C0999 is inside backticks mid-prose; must not match.
        assert ("CONFIRM", "C0999") not in verdict_ids

    def test_exp39_r2_gemini_sample(self):
        """Synthetic from the r2 Gemini log structure."""
        text = (
            "CONFIRM C0001 \u2014 `source_env()` naive split is a confirmed bug.\n"
            "CONFIRM C0005 \u2014 `hash()` randomisation breaks deterministic mapping.\n"
            "MERGE C0024 <- C0012 \u2014 duplicate of the already settled C0012.\n"
            "FOLLOW: The `_VERDICT_AS_FINDING` check only lives in marker parser.\n"
            "- FALSIFIER: `CONFIRM C0042` in JSON would not create Finding.\n"
        )
        results = _parse_verdicts(text, "Gemini", 0)
        ids = {r[1] for r in results}
        # Real verdicts present, backtick-wrapped example excluded.
        assert "C0001" in ids
        assert "C0005" in ids
        assert "C0024" in ids
        assert "C0042" not in ids

    def test_whole_line_bold_strips_trailing_format(self):
        text = "**CONFIRM C0001 \u2014 fully wrapped**"
        results = _parse_verdicts(text, "Gemini", 0)
        assert len(results) == 1
        assert results[0] == ("CONFIRM", "C0001", "fully wrapped")


class TestCrossVerdictTypes:
    """All five verdict types must parse under the new format variants."""

    @pytest.mark.parametrize("verdict", ["CONFIRM", "CHALLENGE", "EXTEND", "MERGE", "REOPEN"])
    def test_bold_with_colon(self, verdict):
        m = _match(f"**{verdict}** C0007: description")
        assert m is not None
        assert m.group(1) == verdict

    @pytest.mark.parametrize("verdict", ["CONFIRM", "CHALLENGE", "EXTEND", "MERGE", "REOPEN"])
    def test_numbered_em_dash(self, verdict):
        m = _match(f"3. {verdict} C0042 \u2014 description")
        assert m is not None
        assert m.group(1) == verdict
