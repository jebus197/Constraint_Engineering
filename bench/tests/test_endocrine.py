"""Tests for the endocrine layer (bench/endocrine.py)."""

import json
import os
import tempfile
import textwrap
from unittest.mock import patch, MagicMock

import pytest
import subprocess as sp

from bench.dm._types import Finding
from bench.endocrine import (
    DefectCategory,
    ToolDiagnostic,
    HealthScan,
    FixEvaluation,
    PacingSignal,
    EndocrineReport,
    RoundTiming,
    EndocrineLayer,
    scan_health,
    evaluate_fix,
    evaluate_fixes,
    compute_pacing_signals,
    run_pyright,
    run_ruff,
    run_bandit,
    run_mypy,
    _apply_fix_to_source,
    _compute_fix_verdict,
    _find_target_file,
    _categorise_pyright,
    _categorise_ruff,
    _run_tool,
)


# =============================================================================
# Fixtures
# =============================================================================

def _make_finding(
    fid="f1", model="CC2", severity=0.7, desc="Bug in parser",
    proposed_fix="", round_idx=0, flaw_class=2,
) -> Finding:
    return Finding(
        finding_id=fid, model_id=model, round_idx=round_idx,
        flaw_class=flaw_class, severity=severity, abstraction_index=0.5,
        description=desc, proposed_fix=proposed_fix,
    )


def _make_source_file(content: str) -> str:
    """Write content to a temp .py file, return its path."""
    fd, path = tempfile.mkstemp(suffix=".py", prefix="endocrine_test_")
    os.write(fd, content.encode("utf-8"))
    os.close(fd)
    return path


# =============================================================================
# Test 1: ToolDiagnostic and HealthScan data types
# =============================================================================

class TestDataTypes:
    def test_tool_diagnostic_fields(self):
        d = ToolDiagnostic(
            tool="pyright", file_path="foo.py", line=10, column=5,
            code="reportGeneralClassIssues", message="Type mismatch",
            severity="error", category=DefectCategory.TYPE_SAFETY,
        )
        assert d.tool == "pyright"
        assert d.category == DefectCategory.TYPE_SAFETY
        assert d.line == 10

    def test_health_scan_empty(self):
        hs = HealthScan()
        assert hs.total == 0
        assert hs.diagnostics == []
        assert hs.elapsed_s == 0.0

    def test_fix_evaluation_defaults(self):
        fe = FixEvaluation(finding_id="f1", original_file="foo.py")
        assert fe.verdict == "UNKNOWN"
        assert fe.fix_applied is False
        assert fe.net_type_errors == 0

    def test_pacing_signal_fields(self):
        ps = PacingSignal(
            signal_type="slow_model",
            detail="CC2 took 120s",
            model_id="CC2",
            metric_value=120.0,
            threshold=60.0,
            suggested_action="increase_timeout",
        )
        assert ps.signal_type == "slow_model"
        assert ps.suggested_action == "increase_timeout"


# =============================================================================
# Test 2: Pyright categorisation
# =============================================================================

class TestCategorisation:
    def test_pyright_null_deref(self):
        assert _categorise_pyright("Object could be None", "") == DefectCategory.NULL_DEREF

    def test_pyright_type_safety(self):
        assert _categorise_pyright("Type int is incompatible with str", "") == DefectCategory.TYPE_SAFETY

    def test_pyright_optional(self):
        assert _categorise_pyright("Optional[int] not callable", "") == DefectCategory.NULL_DEREF

    def test_ruff_dead_code(self):
        assert _categorise_ruff("F401", "unused import") == DefectCategory.DEAD_CODE

    def test_ruff_style(self):
        assert _categorise_ruff("E501", "line too long") == DefectCategory.STYLE

    def test_ruff_security(self):
        assert _categorise_ruff("S101", "assert used") == DefectCategory.SECURITY


# =============================================================================
# Test 3: _apply_fix_to_source strategies
# =============================================================================

class TestApplyFix:
    def test_empty_fix_returns_none(self):
        assert _apply_fix_to_source("x = 1", "") is None
        assert _apply_fix_to_source("x = 1", "   ") is None

    def test_search_replace_pattern(self):
        source = "x = foo(bar)\ny = 2\n"
        fix = 'Replace `foo(bar)` with `foo(baz)`'
        result = _apply_fix_to_source(source, fix)
        assert result is not None
        assert "foo(baz)" in result
        assert "foo(bar)" not in result

    def test_line_replacement_pattern(self):
        source = "line1\nold_value = 42\nline3\n"
        fix = "Line 2: old_value = 42 -> old_value = 99"
        result = _apply_fix_to_source(source, fix)
        assert result is not None
        assert "old_value = 99" in result

    def test_unfixable_returns_none(self):
        source = "x = 1\n"
        fix = "This is just a description of what to do, no actionable pattern."
        result = _apply_fix_to_source(source, fix)
        assert result is None

    def test_whole_file_replacement(self):
        source = "old code\n"
        fix = textwrap.dedent("""\
            import os
            import sys

            def main():
                print("hello")
                return 0

            if __name__ == "__main__":
                main()
        """)
        result = _apply_fix_to_source(source, fix)
        assert result is not None
        assert "def main():" in result


# =============================================================================
# Test 4: Fix verdict computation
# =============================================================================

class TestFixVerdict:
    def test_unevaluable_when_not_applied(self):
        fe = FixEvaluation(finding_id="f1", original_file="x.py", fix_applied=False)
        assert _compute_fix_verdict(fe) == "UNEVALUABLE"

    def test_harmful_when_tests_fail(self):
        fe = FixEvaluation(
            finding_id="f1", original_file="x.py", fix_applied=True,
            tests_passed=False, net_type_errors=0, net_ruff_errors=0,
            net_bandit_issues=0,
        )
        assert _compute_fix_verdict(fe) == "HARMFUL"

    def test_harmful_when_new_errors(self):
        fe = FixEvaluation(
            finding_id="f1", original_file="x.py", fix_applied=True,
            tests_passed=None, net_type_errors=3, net_ruff_errors=0,
            net_bandit_issues=0,
        )
        assert _compute_fix_verdict(fe) == "HARMFUL"

    def test_safe_when_errors_reduced(self):
        fe = FixEvaluation(
            finding_id="f1", original_file="x.py", fix_applied=True,
            tests_passed=None, net_type_errors=-2, net_ruff_errors=0,
            net_bandit_issues=0,
        )
        assert _compute_fix_verdict(fe) == "SAFE"

    def test_safe_when_tests_pass_no_change(self):
        fe = FixEvaluation(
            finding_id="f1", original_file="x.py", fix_applied=True,
            tests_passed=True, net_type_errors=0, net_ruff_errors=0,
            net_bandit_issues=0,
        )
        assert _compute_fix_verdict(fe) == "SAFE"

    def test_neutral_when_no_change_no_tests(self):
        fe = FixEvaluation(
            finding_id="f1", original_file="x.py", fix_applied=True,
            tests_passed=None, net_type_errors=0, net_ruff_errors=0,
            net_bandit_issues=0,
        )
        assert _compute_fix_verdict(fe) == "NEUTRAL"


# =============================================================================
# Test 5: _find_target_file
# =============================================================================

class TestFindTargetFile:
    def test_matches_path_in_description(self):
        finding = _make_finding(desc="Bug in bench/immune_agents.py line 42")
        paths = ["/src/bench/immune_agents.py", "/src/bench/other.py"]
        assert _find_target_file(finding, paths) == "/src/bench/immune_agents.py"

    def test_falls_back_to_first(self):
        finding = _make_finding(desc="Some abstract description")
        paths = ["/src/bench/main.py"]
        assert _find_target_file(finding, paths) == "/src/bench/main.py"

    def test_empty_paths_returns_none(self):
        finding = _make_finding()
        assert _find_target_file(finding, []) is None


# =============================================================================
# Test 6: Pacing signals
# =============================================================================

class TestPacingSignals:
    def test_slow_model_detected(self):
        timings = [
            RoundTiming("CC2", 0, 20.0, 5000, 3),
            RoundTiming("Gemini", 0, 15.0, 4000, 4),
            RoundTiming("DeepSeek", 0, 120.0, 8000, 2),
        ]
        signals = compute_pacing_signals(timings, 0, 80000, [], 0)
        slow = [s for s in signals if s.signal_type == "slow_model"]
        assert len(slow) == 1
        assert slow[0].model_id == "DeepSeek"

    def test_context_growth_warning(self):
        signals = compute_pacing_signals([], 70000, 80000, [], 2)
        ctx = [s for s in signals if s.signal_type == "context_growth"]
        assert len(ctx) == 1
        assert ctx[0].suggested_action == "degrade_relay"

    def test_novelty_plateau(self):
        signals = compute_pacing_signals([], 0, 80000, [5, 3, 0, 1, 0], 4)
        plateau = [s for s in signals if s.signal_type == "novelty_plateau"]
        assert len(plateau) == 1
        assert plateau[0].suggested_action == "check_convergence"

    def test_no_signals_when_healthy(self):
        timings = [
            RoundTiming("CC2", 0, 20.0, 5000, 3),
            RoundTiming("Gemini", 0, 18.0, 4000, 4),
        ]
        signals = compute_pacing_signals(timings, 10000, 80000, [5, 4], 1)
        assert signals == []

    def test_response_size_anomaly(self):
        timings = [
            RoundTiming("CC2", 0, 20.0, 5000, 3),
            RoundTiming("Gemini", 0, 20.0, 5000, 3),
            RoundTiming("Verbose", 0, 20.0, 50000, 3),
        ]
        signals = compute_pacing_signals(timings, 0, 80000, [], 0)
        ctx = [s for s in signals if s.signal_type == "context_growth" and s.model_id == "Verbose"]
        assert len(ctx) == 1


# =============================================================================
# Test 7: Tool runners with mocked subprocess
# =============================================================================

class TestToolRunners:
    @patch("bench.endocrine._run_tool")
    def test_run_pyright_parses_json(self, mock_run):
        mock_run.return_value = sp.CompletedProcess(
            args=[], returncode=1, stderr="",
            stdout=json.dumps({
                "generalDiagnostics": [{
                    "file": "test.py",
                    "range": {"start": {"line": 10, "character": 5}},
                    "severity": "error",
                    "rule": "reportMissingImports",
                    "message": "Import \"foo\" could not be resolved",
                }],
            }),
        )
        diags = run_pyright(["test.py"])
        assert len(diags) == 1
        assert diags[0].tool == "pyright"
        assert diags[0].line == 10

    @patch("bench.endocrine._run_tool")
    def test_run_ruff_parses_json(self, mock_run):
        mock_run.return_value = sp.CompletedProcess(
            args=[], returncode=1, stderr="",
            stdout=json.dumps([{
                "code": "F401",
                "message": "'os' imported but unused",
                "filename": "test.py",
                "location": {"row": 1, "column": 1},
            }]),
        )
        diags = run_ruff(["test.py"])
        assert len(diags) == 1
        assert diags[0].category == DefectCategory.DEAD_CODE

    @patch("bench.endocrine._run_tool")
    def test_run_bandit_parses_json(self, mock_run):
        mock_run.return_value = sp.CompletedProcess(
            args=[], returncode=0, stderr="",
            stdout=json.dumps({
                "results": [{
                    "filename": "test.py",
                    "line_number": 5,
                    "test_id": "B101",
                    "issue_text": "Use of assert detected",
                    "issue_severity": "LOW",
                }],
            }),
        )
        diags = run_bandit(["test.py"])
        assert len(diags) == 1
        assert diags[0].category == DefectCategory.SECURITY

    @patch("bench.endocrine._run_tool")
    def test_run_mypy_parses_output(self, mock_run):
        mock_run.return_value = sp.CompletedProcess(
            args=[], returncode=1, stderr="",
            stdout="test.py:10:5: error: Incompatible types in assignment [assignment]\n",
        )
        diags = run_mypy(["test.py"])
        assert len(diags) == 1
        assert diags[0].tool == "mypy"
        assert diags[0].line == 10
        assert diags[0].code == "assignment"

    def test_run_tool_timeout_handled(self):
        """Verify timeout produces a clean result, not an exception."""
        with patch("bench.endocrine.sp.run", side_effect=sp.TimeoutExpired(cmd=["test"], timeout=1)):
            result = _run_tool(["test"], timeout=1)
            assert result.returncode == -1
            assert "TIMEOUT" in result.stderr

    def test_run_tool_not_found_handled(self):
        """Verify missing binary produces a clean result."""
        with patch("bench.endocrine.sp.run", side_effect=FileNotFoundError):
            result = _run_tool(["/nonexistent/tool"], timeout=1)
            assert result.returncode == -1
            assert "NOT_FOUND" in result.stderr

    def test_empty_paths_returns_empty(self):
        assert run_pyright([]) == []
        assert run_ruff([]) == []
        assert run_bandit([]) == []
        assert run_mypy([]) == []


# =============================================================================
# Test 8: scan_health integration (mocked tools)
# =============================================================================

class TestScanHealth:
    @patch("bench.endocrine.run_mypy", return_value=[])
    @patch("bench.endocrine.run_bandit", return_value=[])
    @patch("bench.endocrine.run_ruff", return_value=[
        ToolDiagnostic("ruff", "x.py", 1, 1, "F401", "unused", "warning", DefectCategory.DEAD_CODE),
    ])
    @patch("bench.endocrine.run_pyright", return_value=[
        ToolDiagnostic("pyright", "x.py", 5, 1, "rule", "type err", "error", DefectCategory.TYPE_SAFETY),
    ])
    def test_scan_aggregates_tools(self, *mocks):
        # Need a real file for os.path.isfile check
        path = _make_source_file("x = 1\n")
        try:
            result = scan_health([path])
            assert result.total == 2
            assert result.counts_by_tool.get("pyright", 0) == 1
            assert result.counts_by_tool.get("ruff", 0) == 1
            assert result.tools_available["pyright"] is True
            assert result.tools_available["ruff"] is True
        finally:
            os.unlink(path)

    def test_scan_nonexistent_files(self):
        result = scan_health(["/nonexistent/path.py"])
        assert result.total == 0


# =============================================================================
# Test 9: Fix evaluation with mocked tools
# =============================================================================

class TestFixEvaluation:
    def test_no_fix_is_unevaluable(self):
        finding = _make_finding(proposed_fix="")
        result = evaluate_fix(finding, ["/some/file.py"])
        assert result.verdict == "UNEVALUABLE"

    @patch("bench.endocrine.run_bandit", return_value=[])
    @patch("bench.endocrine.run_ruff", return_value=[])
    @patch("bench.endocrine.run_pyright", return_value=[])
    def test_fix_applied_successfully(self, *mocks):
        source = "x = foo(bar)\ny = 2\n"
        path = _make_source_file(source)
        try:
            finding = _make_finding(
                desc=f"Bug in {path}",
                proposed_fix='Replace `foo(bar)` with `foo(baz)`',
            )
            result = evaluate_fix(finding, [path])
            assert result.fix_applied is True
            # With all tools returning empty, net change is zero -> NEUTRAL
            assert result.verdict in ("NEUTRAL", "SAFE")
        finally:
            os.unlink(path)

    def test_evaluate_fixes_caps_at_max(self):
        findings = [
            _make_finding(fid=f"f{i}", proposed_fix="Replace `x` with `y`")
            for i in range(30)
        ]
        with patch("bench.endocrine.evaluate_fix") as mock_eval:
            mock_eval.return_value = FixEvaluation(
                finding_id="test", original_file="x.py",
                fix_applied=True, verdict="NEUTRAL",
            )
            results = evaluate_fixes(findings, ["x.py"], max_evals=5)
            assert mock_eval.call_count == 5
            assert len(results) == 5


# =============================================================================
# Test 10: EndocrineLayer full cycle
# =============================================================================

class TestEndocrineLayer:
    @patch("bench.endocrine.evaluate_fixes", return_value=[])
    @patch("bench.endocrine.scan_health")
    def test_full_cycle(self, mock_scan, mock_eval):
        mock_scan.return_value = HealthScan(
            total=3,
            diagnostics=[],
            counts_by_category={"type_safety": 2, "dead_code": 1},
            counts_by_tool={"pyright": 2, "ruff": 1},
            counts_by_severity={"error": 2, "warning": 1},
            tools_available={"pyright": True, "ruff": True},
        )

        endo = EndocrineLayer(source_paths=["x.py"])
        findings = [_make_finding()]
        timings = [
            RoundTiming("CC2", 0, 20.0, 5000, 3),
            RoundTiming("Gemini", 0, 18.0, 4000, 4),
        ]

        report = endo.run(
            round_idx=0,
            findings=findings,
            round_timings=timings,
            cumulative_context_chars=10000,
            context_budget=80000,
            novelty_counts=[5],
        )

        assert isinstance(report, EndocrineReport)
        assert report.round_idx == 0
        assert report.health_scan.total == 3
        assert report.elapsed_s > 0

    @patch("bench.endocrine.evaluate_fixes", return_value=[])
    @patch("bench.endocrine.scan_health")
    def test_health_trend_tracking(self, mock_scan, mock_eval):
        endo = EndocrineLayer(source_paths=["x.py"])

        # Round 0: 3 type errors
        mock_scan.return_value = HealthScan(
            total=3,
            counts_by_category={"type_safety": 3},
            tools_available={"pyright": True},
        )
        endo.run(round_idx=0, findings=[])

        # Round 1: 1 type error
        mock_scan.return_value = HealthScan(
            total=1,
            counts_by_category={"type_safety": 1},
            tools_available={"pyright": True},
        )
        endo.run(round_idx=1, findings=[])

        trend = endo.health_trend()
        assert trend["type_safety"] == [3, 1]

    def test_endocrine_report_fields(self):
        report = EndocrineReport(
            round_idx=2,
            health_scan=HealthScan(),
            fix_evaluations=[],
            pacing_signals=[],
            elapsed_s=1.5,
        )
        assert report.round_idx == 2
        assert report.elapsed_s == 1.5
