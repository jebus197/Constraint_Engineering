"""Regression tests for bench/bugzilla_loop.py — the CONFIRMED -> CLOSED
state transition via verified fix.

The module is intentionally standalone (not yet wired into the runner).
Tests cover the four-step pipeline:

  1. extract_search_replace — parse proposed_fix into old/new code
  2. apply_fix_to_sandbox — replace exactly-once in a sandbox copy
  3. run_verification — ruff + mypy + bandit + test_cmd against sandbox
  4. attempt_close / verify_and_close_fixes — orchestration
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

import bugzilla_loop


# ---------------------------------------------------------------------------
# Step 1: extract_search_replace
# ---------------------------------------------------------------------------

class TestExtractSearchReplace:
    """Parsing SEARCH/REPLACE and OLD/NEW blocks from proposed_fix text."""

    def test_search_replace_block_extracts_correctly(self):
        text = (
            "<<<< SEARCH bench/dm/_feedback.py\n"
            "def foo():\n"
            "    return None\n"
            "==== REPLACE\n"
            "def foo():\n"
            "    return 42\n"
            ">>>>"
        )
        r = bugzilla_loop.extract_search_replace(text)
        assert r.success
        assert "def foo()" in r.old_code
        assert "return None" in r.old_code
        assert "return 42" in r.new_code
        assert r.file_hint == "bench/dm/_feedback.py"

    def test_old_new_block_extracts_correctly(self):
        text = (
            "<<<< OLD\n"
            "x = 1\n"
            "==== NEW\n"
            "x = 2\n"
            ">>>>"
        )
        r = bugzilla_loop.extract_search_replace(text)
        assert r.success
        assert r.old_code == "x = 1"
        assert r.new_code == "x = 2"

    def test_empty_input_fails(self):
        r = bugzilla_loop.extract_search_replace("")
        assert not r.success
        assert "empty" in r.reason.lower()

    def test_whitespace_input_fails(self):
        r = bugzilla_loop.extract_search_replace("   \n\t\n   ")
        assert not r.success

    def test_no_markers_fails(self):
        text = (
            "Just some free-form description of a bug. "
            "No SEARCH/REPLACE blocks here."
        )
        r = bugzilla_loop.extract_search_replace(text)
        assert not r.success
        assert "no SEARCH/REPLACE" in r.reason

    def test_empty_search_segment_fails(self):
        text = (
            "<<<< SEARCH\n"
            "\n"
            "==== REPLACE\n"
            "new_code\n"
            ">>>>"
        )
        r = bugzilla_loop.extract_search_replace(text)
        assert not r.success
        assert "empty SEARCH segment" in r.reason


# ---------------------------------------------------------------------------
# Step 2: apply_fix_to_sandbox
# ---------------------------------------------------------------------------

class TestApplyFixToSandbox:
    """Sandbox-copy + exactly-once replacement semantics."""

    def test_happy_path_writes_modified_sandbox(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("def hello():\n    return 1\n")
        sandbox, reason = bugzilla_loop.apply_fix_to_sandbox(
            target, "return 1", "return 2"
        )
        assert sandbox is not None
        assert reason == ""
        content = sandbox.read_text()
        assert "return 2" in content
        assert "return 1" not in content
        # cleanup
        sandbox.unlink()

    def test_target_missing_returns_none(self, tmp_path):
        target = tmp_path / "nonexistent.py"
        sandbox, reason = bugzilla_loop.apply_fix_to_sandbox(
            target, "x", "y"
        )
        assert sandbox is None
        assert "does not exist" in reason

    def test_old_code_not_in_target_returns_none(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("def hello():\n    return 1\n")
        sandbox, reason = bugzilla_loop.apply_fix_to_sandbox(
            target, "this string is not in the file", "replacement"
        )
        assert sandbox is None
        assert "not found" in reason

    def test_old_code_ambiguous_match_returns_none(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text(
            "x = 1\n"
            "y = 1\n"
            "z = 1\n"
        )
        sandbox, reason = bugzilla_loop.apply_fix_to_sandbox(
            target, "= 1", "= 2"
        )
        assert sandbox is None
        assert "matches" in reason
        assert "ambiguous" in reason


# ---------------------------------------------------------------------------
# Step 3: run_verification (mocked subprocess)
# ---------------------------------------------------------------------------

class TestRunVerification:
    """Verification tool aggregation. Uses mocked subprocess to avoid
    needing ruff/mypy/bandit installed during test."""

    def test_all_tools_pass_returns_passed_true(self, tmp_path):
        sandbox = tmp_path / "sb.py"
        sandbox.write_text("def f(): return 1\n")
        with patch("bugzilla_loop._run_tool", return_value=(True, "")):
            r = bugzilla_loop.run_verification(sandbox, test_cmd=None)
        assert r.passed
        assert r.ruff_passed and r.mypy_passed and r.bandit_passed
        assert r.test_skipped  # no test_cmd provided

    def test_ruff_failure_blocks_pass(self, tmp_path):
        sandbox = tmp_path / "sb.py"
        sandbox.write_text("def f(): return 1\n")

        def mock_run_tool(cmd, timeout=60):
            if "ruff" in cmd[2] if len(cmd) > 2 else False:
                return False, "ruff: error E501 line too long"
            return True, ""

        with patch("bugzilla_loop._run_tool", side_effect=mock_run_tool):
            r = bugzilla_loop.run_verification(sandbox, test_cmd=None)
        assert not r.passed
        assert not r.ruff_passed
        assert any("ruff" in f for f in r.failures)

    def test_test_cmd_run_when_provided(self, tmp_path):
        sandbox = tmp_path / "sb.py"
        sandbox.write_text("def f(): return 1\n")
        with patch("bugzilla_loop._run_tool", return_value=(True, "")):
            r = bugzilla_loop.run_verification(
                sandbox, test_cmd="python3 -m pytest somefile.py"
            )
        assert r.passed
        assert r.test_passed
        assert not r.test_skipped

    def test_bandit_informational_treated_as_pass(self, tmp_path):
        sandbox = tmp_path / "sb.py"
        sandbox.write_text("def f(): return 1\n")

        def mock_run_tool(cmd, timeout=60):
            if "bandit" in cmd[2] if len(cmd) > 2 else False:
                return False, "Code scanned: No issues identified."
            return True, ""

        with patch("bugzilla_loop._run_tool", side_effect=mock_run_tool):
            r = bugzilla_loop.run_verification(sandbox, test_cmd=None)
        assert r.bandit_passed  # No issues identified -> treated as pass
        assert r.passed


# ---------------------------------------------------------------------------
# Step 4: attempt_close + verify_and_close_fixes (orchestration)
# ---------------------------------------------------------------------------

class TestAttemptClose:
    """End-to-end: parse proposed_fix, apply, verify, decide."""

    def test_full_happy_path_closes_finding(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("def add(a, b):\n    return a + b + 1\n")
        finding = {
            "finding_id": "TEST_F001",
            "proposed_fix": (
                "<<<< OLD\n"
                "    return a + b + 1\n"
                "==== NEW\n"
                "    return a + b\n"
                ">>>>"
            ),
        }
        with patch("bugzilla_loop._run_tool", return_value=(True, "")):
            attempt = bugzilla_loop.attempt_close(finding, target)
        assert attempt.closed
        assert attempt.finding_id == "TEST_F001"
        assert attempt.extract.success
        assert attempt.verification is not None
        assert attempt.verification.passed

    def test_extract_failure_does_not_attempt_sandbox(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("def f(): pass\n")
        finding = {
            "finding_id": "TEST_F002",
            "proposed_fix": "no markers in this fix text",
        }
        attempt = bugzilla_loop.attempt_close(finding, target)
        assert not attempt.closed
        assert "extract failed" in attempt.reason
        assert attempt.verification is None  # never ran

    def test_sandbox_apply_failure_does_not_attempt_verification(
        self, tmp_path
    ):
        target = tmp_path / "target.py"
        target.write_text("def hello(): return 1\n")
        finding = {
            "finding_id": "TEST_F003",
            "proposed_fix": (
                "<<<< OLD\n"
                "this code is not in the target\n"
                "==== NEW\n"
                "replacement\n"
                ">>>>"
            ),
        }
        attempt = bugzilla_loop.attempt_close(finding, target)
        assert not attempt.closed
        assert "sandbox apply failed" in attempt.reason
        assert attempt.verification is None  # never ran


class TestVerifyAndCloseFixes:
    """Status-filtered iteration over a finding list."""

    def test_filters_by_status(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("def f(): pass\n")
        findings = [
            {"finding_id": "A", "status": "OPEN", "proposed_fix": ""},
            {"finding_id": "B", "status": "CONFIRMED", "proposed_fix": ""},
            {"finding_id": "C", "status": "CLOSED", "proposed_fix": ""},
            {"finding_id": "D", "status": "CONFIRMED", "proposed_fix": ""},
        ]
        attempts = bugzilla_loop.verify_and_close_fixes(
            findings, target, status_filter=("CONFIRMED",)
        )
        ids = [a.finding_id for a in attempts]
        assert ids == ["B", "D"]

    def test_empty_findings_returns_empty(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("def f(): pass\n")
        attempts = bugzilla_loop.verify_and_close_fixes([], target)
        assert attempts == []

    def test_no_matching_status_returns_empty(self, tmp_path):
        target = tmp_path / "target.py"
        target.write_text("def f(): pass\n")
        findings = [
            {"finding_id": "A", "status": "OPEN", "proposed_fix": ""},
        ]
        attempts = bugzilla_loop.verify_and_close_fixes(
            findings, target, status_filter=("CONFIRMED",)
        )
        assert attempts == []
