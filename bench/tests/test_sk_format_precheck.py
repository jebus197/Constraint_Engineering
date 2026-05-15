"""Tests for the S_k format pre-check (Item 1D.5).

The pre-check must admit well-formed SEARCH/REPLACE blocks, reject prose
and partial markers, and produce diagnostic reasons suitable for embedding
in a reformat-request prompt section.
"""

from __future__ import annotations

import pytest

from bench.dm._sk_format import (
    build_reformat_requests,
    check_sk_format_admissible,
)


class TestAdmissibleBlocks:

    def test_minimal_valid_block(self):
        text = (
            "<<<< SEARCH src/foo.py\n"
            "def bar():\n"
            "    return 1\n"
            "====\n"
            "def bar():\n"
            "    return 2\n"
            ">>>> REPLACE\n"
        )
        ok, reason = check_sk_format_admissible(text)
        assert ok, f"expected admissible; got reason={reason!r}"
        assert reason == ""

    def test_lowercase_search_keyword(self):
        text = (
            "<<<< search src/foo.py\n"
            "old\n"
            "====\n"
            "new\n"
            ">>>> REPLACE\n"
        )
        ok, _ = check_sk_format_admissible(text)
        assert ok

    def test_block_with_surrounding_prose(self):
        text = (
            "Here is the proposed fix:\n"
            "\n"
            "<<<< SEARCH bench/foo.py\n"
            "x = 1\n"
            "====\n"
            "x = 2\n"
            ">>>> REPLACE\n"
            "\n"
            "This should resolve the off-by-one.\n"
        )
        ok, _ = check_sk_format_admissible(text)
        assert ok

    def test_multiple_blocks(self):
        text = (
            "<<<< SEARCH a.py\n"
            "old1\n"
            "====\n"
            "new1\n"
            ">>>> REPLACE\n"
            "<<<< SEARCH b.py\n"
            "old2\n"
            "====\n"
            "new2\n"
            ">>>> REPLACE\n"
        )
        ok, _ = check_sk_format_admissible(text)
        assert ok


class TestRejectedBlocks:

    def test_empty_string(self):
        ok, reason = check_sk_format_admissible("")
        assert not ok
        assert "empty" in reason.lower()

    def test_whitespace_only(self):
        ok, reason = check_sk_format_admissible("   \n\n\t\n")
        assert not ok
        assert "empty" in reason.lower()

    def test_pure_prose(self):
        text = (
            "The bug is in foo.py line 42. Change the assignment from "
            "x = 1 to x = 2 to fix the off-by-one."
        )
        ok, reason = check_sk_format_admissible(text)
        assert not ok
        assert "SEARCH/REPLACE" in reason or "markers" in reason.lower()

    def test_missing_separator(self):
        text = (
            "<<<< SEARCH foo.py\n"
            "old\n"
            "new\n"
            ">>>> REPLACE\n"
        )
        ok, reason = check_sk_format_admissible(text)
        assert not ok
        assert "====" in reason or "separator" in reason.lower()

    def test_missing_opener(self):
        text = (
            "old code here\n"
            "====\n"
            "new code here\n"
            ">>>> REPLACE\n"
        )
        ok, reason = check_sk_format_admissible(text)
        assert not ok
        assert "SEARCH" in reason

    def test_missing_closer(self):
        text = (
            "<<<< SEARCH foo.py\n"
            "old\n"
            "====\n"
            "new\n"
        )
        ok, reason = check_sk_format_admissible(text)
        assert not ok
        assert ">>>>" in reason or "closer" in reason.lower()

    def test_unified_diff_format(self):
        # A common wrong format — unified diff is not the S_k block format.
        text = (
            "--- a/foo.py\n"
            "+++ b/foo.py\n"
            "@@ -1,3 +1,3 @@\n"
            "-x = 1\n"
            "+x = 2\n"
        )
        ok, reason = check_sk_format_admissible(text)
        assert not ok


class TestReformatRequests:

    def test_empty_list_returns_empty(self):
        assert build_reformat_requests([]) == ""

    def test_single_finding(self):
        out = build_reformat_requests(
            [("C0001", "no SEARCH/REPLACE markers")],
        )
        # Exp 40 fix 1e: the soft "REFORMAT REQUEST" header was
        # replaced by an explicit STRUCTURE_VIOLATION header with
        # mandatory framing. Pin the strengthened contract.
        assert "STRUCTURE_VIOLATION" in out
        assert "MANDATORY REFORMAT" in out
        assert "C0001" in out
        assert "no SEARCH/REPLACE markers" in out
        assert "<<<< SEARCH" in out  # canonical template included
        assert ">>>> REPLACE" in out
        # The request must state that an unparseable fix is treated as
        # no fix (the load-bearing motivation signal to the model).
        assert "no fix at all" in out

    def test_multiple_findings(self):
        findings = [
            ("C0001", "no markers"),
            ("C0002", "missing separator"),
            ("C0003", "missing closer"),
        ]
        out = build_reformat_requests(findings)
        for cid in ("C0001", "C0002", "C0003"):
            assert cid in out

    def test_max_entries_truncates(self):
        findings = [(f"C{i:04d}", "no markers") for i in range(20)]
        out = build_reformat_requests(findings, max_entries=5)
        assert "C0004" in out
        assert "C0005" not in out
        assert "and 15 more" in out

    def test_max_chars_truncates(self):
        # A pathological reason string that blows the char budget.
        findings = [("C0001", "x" * 5000)]
        out = build_reformat_requests(findings, max_chars=500)
        assert len(out) <= 500 + len("\n  ... (truncated)") + 1
        assert "truncated" in out

    def test_canonical_template_formatting(self):
        out = build_reformat_requests([("C0001", "test")])
        # Canonical block template must appear in the guidance. Exp 40
        # fix 1e strengthened the placeholder wording from
        # "<exact source text>" to "<exact verbatim source text to
        # find>" and added explicit byte-for-byte / no-elision rules.
        assert "SEARCH <file_path>" in out
        assert "<exact verbatim source text to find>" in out
        assert "<replacement text>" in out
        assert ">>>> REPLACE" in out
        # Strengthened mandatory rules block.
        assert "byte-for-byte" in out
        assert "Do not wrap the block in backticks" in out


class TestIntegrationWithParser:
    """When parse_search_replace_blocks is importable, check_sk_format_admissible
    should also cross-validate that at least one block parses."""

    def test_markers_present_but_unparseable_block(self):
        # SEARCH/separator/closer all present but the block is malformed
        # (no file path after SEARCH). Accept either True (structural-only
        # success) or False with a parser-reported reason.
        text = (
            "<<<< SEARCH\n"
            "====\n"
            ">>>> REPLACE\n"
        )
        ok, reason = check_sk_format_admissible(text)
        if not ok:
            assert "block" in reason.lower() or "parse" in reason.lower() \
                or "path" in reason.lower() or "delimiter" in reason.lower()
