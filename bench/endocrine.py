"""Endocrine Layer — Whole-body health monitor for CDSFL bench system.

The endocrine layer runs static analysis tools between rounds and produces
structured health signals that the insect brain uses for round decisions.
Like the insect brain and immune pipeline, it is mechanical: no deliberation,
no evaluation of content quality, only tool execution and metric extraction.

Core functions:
1. Health scan     — run pyright, ruff, bandit on source files, produce metrics
2. Defect detect   — classify findings by defect category (type safety, null
                     deref, off-by-one, race conditions, security, dead code)
3. Fix evaluation  — sandbox-test proposed fixes from findings (the key new
                     capability that closes the immune pipeline's blind spot)
4. Pacing signals  — monitor timing, context growth, novelty plateau

Tool binaries (Python 3.13, subprocess only — never imported as modules):
    /Library/Frameworks/Python.framework/Versions/3.13/bin/pyright
    /Library/Frameworks/Python.framework/Versions/3.13/bin/ruff
    /Library/Frameworks/Python.framework/Versions/3.13/bin/bandit
    /Library/Frameworks/Python.framework/Versions/3.13/bin/mypy
    /Library/Frameworks/Python.framework/Versions/3.13/bin/crosshair

Design principles (matching insect brain):
1. Mechanical: tool invocation -> structured output, no reasoning
2. Independently testable: every function has defined inputs/outputs
3. Runs between rounds, never during model dispatch
4. Fix evaluation is sandboxed (tempdir, never modifies actual source)
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess as sp
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from bench.dm._types import Finding

logger = logging.getLogger("endocrine")


# =============================================================================
# Tool binary paths
# =============================================================================

_TOOL_BIN = "/Library/Frameworks/Python.framework/Versions/3.13/bin"

PYRIGHT_BIN = os.path.join(_TOOL_BIN, "pyright")
RUFF_BIN = os.path.join(_TOOL_BIN, "ruff")
BANDIT_BIN = os.path.join(_TOOL_BIN, "bandit")
MYPY_BIN = os.path.join(_TOOL_BIN, "mypy")
CROSSHAIR_BIN = os.path.join(_TOOL_BIN, "crosshair")
PYTHON_313 = os.path.join(_TOOL_BIN, "python3")

# Timeout for individual tool invocations (seconds).
_TOOL_TIMEOUT = 60
_CROSSHAIR_TIMEOUT = 120  # symbolic execution is slow


# =============================================================================
# Data types
# =============================================================================

class DefectCategory:
    """Defect category constants. Not an enum — used as string tags."""
    TYPE_SAFETY = "type_safety"
    NULL_DEREF = "null_deref"
    OFF_BY_ONE = "off_by_one"
    RACE_CONDITION = "race_condition"
    SECURITY = "security"
    DEAD_CODE = "dead_code"
    STYLE = "style"
    UNKNOWN = "unknown"


@dataclass
class ToolDiagnostic:
    """A single diagnostic from a static analysis tool.

    One pyright error, one ruff violation, one bandit finding, etc.
    """
    tool: str               # "pyright", "ruff", "bandit", "mypy", "crosshair"
    file_path: str          # source file
    line: int               # line number (0 if unknown)
    column: int             # column number (0 if unknown)
    code: str               # tool-specific error code (e.g. "E501", "B101")
    message: str            # human-readable message
    severity: str           # "error", "warning", "info"
    category: str           # DefectCategory value


@dataclass
class HealthScan:
    """Result of a full health scan across all source files.

    Produced by scan_health(). Consumed by the insect brain.
    """
    diagnostics: List[ToolDiagnostic] = field(default_factory=list)
    # Aggregate counts by category
    counts_by_category: Dict[str, int] = field(default_factory=dict)
    # Aggregate counts by tool
    counts_by_tool: Dict[str, int] = field(default_factory=dict)
    # Aggregate counts by severity
    counts_by_severity: Dict[str, int] = field(default_factory=dict)
    # Per-file error counts (path -> count)
    counts_by_file: Dict[str, int] = field(default_factory=dict)
    # Total diagnostics
    total: int = 0
    # Scan duration
    elapsed_s: float = 0.0
    # Tool availability (tool -> bool)
    tools_available: Dict[str, bool] = field(default_factory=dict)


@dataclass
class FixEvaluation:
    """Result of evaluating a single proposed fix in a sandbox.

    The key new capability: does the proposed fix break anything?
    """
    finding_id: str
    original_file: str
    fix_applied: bool = False   # whether the fix could be applied
    apply_error: str = ""       # error message if fix could not be applied
    # Post-fix analysis
    tests_passed: Optional[bool] = None    # None if not run
    test_output: str = ""
    new_type_errors: int = 0               # type errors introduced by fix
    new_ruff_errors: int = 0               # ruff errors introduced by fix
    new_bandit_issues: int = 0             # security issues introduced by fix
    pre_type_errors: int = 0               # type errors before fix
    pre_ruff_errors: int = 0               # ruff errors before fix
    pre_bandit_issues: int = 0             # bandit issues before fix
    net_type_errors: int = 0               # change in type errors
    net_ruff_errors: int = 0               # change in ruff errors
    net_bandit_issues: int = 0             # change in bandit issues
    verdict: str = "UNKNOWN"               # SAFE, HARMFUL, NEUTRAL, UNEVALUABLE
    elapsed_s: float = 0.0


@dataclass
class PacingSignal:
    """Pacing signal for the insect brain.

    Emitted between rounds to guide timing and convergence decisions.
    """
    signal_type: str       # "slow_model", "context_growth", "novelty_plateau"
    detail: str            # human-readable explanation
    model_id: str = ""     # relevant model (if applicable)
    metric_value: float = 0.0
    threshold: float = 0.0
    suggested_action: str = ""  # e.g. "increase_timeout", "degrade_relay", "check_convergence"


@dataclass
class EndocrineReport:
    """Complete endocrine report for one inter-round interval.

    Assembled by EndocrineLayer.report() and handed to the insect brain.
    """
    round_idx: int
    health_scan: HealthScan
    fix_evaluations: List[FixEvaluation] = field(default_factory=list)
    pacing_signals: List[PacingSignal] = field(default_factory=list)
    elapsed_s: float = 0.0


# =============================================================================
# Tool runners (subprocess-based, mechanical)
# =============================================================================

def _run_tool(
    cmd: List[str],
    timeout: int = _TOOL_TIMEOUT,
    cwd: Optional[str] = None,
) -> sp.CompletedProcess:
    """Run a tool binary via subprocess. Returns CompletedProcess.

    Never raises on non-zero exit code (static analysis tools exit non-zero
    when they find issues — that's normal, not an error).
    """
    try:
        return sp.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except sp.TimeoutExpired:
        logger.warning("Tool timed out after %ds: %s", timeout, cmd[0])
        return sp.CompletedProcess(cmd, returncode=-1, stdout="", stderr="TIMEOUT")
    except FileNotFoundError:
        logger.warning("Tool not found: %s", cmd[0])
        return sp.CompletedProcess(cmd, returncode=-1, stdout="", stderr="NOT_FOUND")


def run_pyright(paths: List[str]) -> List[ToolDiagnostic]:
    """Run pyright on given source files. Returns diagnostics."""
    if not paths:
        return []
    cmd = [PYRIGHT_BIN, "--outputjson"] + paths
    result = _run_tool(cmd)

    if result.stderr == "NOT_FOUND":
        return []

    diagnostics = []
    try:
        data = json.loads(result.stdout)
        for diag in data.get("generalDiagnostics", []):
            rng = diag.get("range", {}).get("start", {})
            severity_raw = diag.get("severity", "error")
            msg = diag.get("message", "")
            rule = diag.get("rule", "")

            category = _categorise_pyright(msg, rule)

            diagnostics.append(ToolDiagnostic(
                tool="pyright",
                file_path=diag.get("file", ""),
                line=rng.get("line", 0),
                column=rng.get("character", 0),
                code=rule,
                message=msg,
                severity=severity_raw,
                category=category,
            ))
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to parse pyright output: %s", e)

    return diagnostics


def _categorise_pyright(message: str, rule: str) -> str:
    """Categorise a pyright diagnostic into a DefectCategory."""
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ("none", "optional", "could be none", "is not callable")):
        return DefectCategory.NULL_DEREF
    if any(kw in msg_lower for kw in ("type", "incompatible", "cannot assign", "argument")):
        return DefectCategory.TYPE_SAFETY
    return DefectCategory.TYPE_SAFETY  # pyright is primarily a type checker


def run_ruff(paths: List[str]) -> List[ToolDiagnostic]:
    """Run ruff on given source files. Returns diagnostics."""
    if not paths:
        return []
    cmd = [RUFF_BIN, "check", "--output-format=json"] + paths
    result = _run_tool(cmd)

    if result.stderr == "NOT_FOUND":
        return []

    diagnostics = []
    try:
        issues = json.loads(result.stdout) if result.stdout.strip() else []
        for issue in issues:
            code = issue.get("code", "")
            msg = issue.get("message", "")
            loc = issue.get("location", {})

            category = _categorise_ruff(code, msg)

            diagnostics.append(ToolDiagnostic(
                tool="ruff",
                file_path=issue.get("filename", ""),
                line=loc.get("row", 0),
                column=loc.get("column", 0),
                code=code,
                message=msg,
                severity="warning",
                category=category,
            ))
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to parse ruff output: %s", e)

    return diagnostics


def _categorise_ruff(code: str, message: str) -> str:
    """Categorise a ruff diagnostic into a DefectCategory."""
    # F-codes: pyflakes (dead code, unused imports)
    if code.startswith("F"):
        return DefectCategory.DEAD_CODE
    # E-codes: pycodestyle (style)
    if code.startswith("E") or code.startswith("W"):
        return DefectCategory.STYLE
    # S-codes: bandit-derived security
    if code.startswith("S"):
        return DefectCategory.SECURITY
    # B-codes: bugbear
    msg_lower = message.lower()
    if "unused" in msg_lower or "never used" in msg_lower:
        return DefectCategory.DEAD_CODE
    return DefectCategory.STYLE


def run_bandit(paths: List[str]) -> List[ToolDiagnostic]:
    """Run bandit on given source files. Returns diagnostics."""
    if not paths:
        return []
    cmd = [BANDIT_BIN, "-f", "json", "-q"] + paths
    result = _run_tool(cmd)

    if result.stderr == "NOT_FOUND":
        return []

    diagnostics = []
    try:
        data = json.loads(result.stdout) if result.stdout.strip() else {}
        for issue in data.get("results", []):
            sev_map = {"LOW": "info", "MEDIUM": "warning", "HIGH": "error"}

            diagnostics.append(ToolDiagnostic(
                tool="bandit",
                file_path=issue.get("filename", ""),
                line=issue.get("line_number", 0),
                column=0,
                code=issue.get("test_id", ""),
                message=issue.get("issue_text", ""),
                severity=sev_map.get(issue.get("issue_severity", ""), "warning"),
                category=DefectCategory.SECURITY,
            ))
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to parse bandit output: %s", e)

    return diagnostics


def run_mypy(paths: List[str]) -> List[ToolDiagnostic]:
    """Run mypy on given source files. Returns diagnostics."""
    if not paths:
        return []
    cmd = [MYPY_BIN, "--no-color-output", "--show-column-numbers",
           "--no-error-summary"] + paths
    result = _run_tool(cmd)

    if result.stderr == "NOT_FOUND":
        return []

    # mypy output format: file.py:line:col: severity: message  [error-code]
    pattern = re.compile(
        r"^(.+?):(\d+):(\d+):\s+(error|warning|note):\s+(.+?)(?:\s+\[(.+?)\])?$"
    )

    diagnostics = []
    for line in result.stdout.splitlines():
        m = pattern.match(line)
        if m:
            msg = m.group(5)
            code = m.group(6) or ""
            msg_lower = msg.lower()

            if "none" in msg_lower or "optional" in msg_lower:
                category = DefectCategory.NULL_DEREF
            else:
                category = DefectCategory.TYPE_SAFETY

            diagnostics.append(ToolDiagnostic(
                tool="mypy",
                file_path=m.group(1),
                line=int(m.group(2)),
                column=int(m.group(3)),
                code=code,
                message=msg,
                severity=m.group(4),
                category=category,
            ))

    return diagnostics


# =============================================================================
# Health scan (function 1)
# =============================================================================

def scan_health(source_paths: List[str]) -> HealthScan:
    """Run all static analysis tools on source files. Produce HealthScan.

    Mechanical: invokes tools, aggregates results. No evaluation.
    This is the primary health signal for the insect brain.

    Args:
        source_paths: Absolute paths to Python source files to analyse.

    Returns:
        HealthScan with all diagnostics and aggregate counts.
    """
    t0 = time.monotonic()

    # Filter to files that actually exist
    existing = [p for p in source_paths if os.path.isfile(p)]
    if not existing:
        return HealthScan(elapsed_s=time.monotonic() - t0)

    # Run tools (sequentially — they're fast enough on a single file set)
    all_diags: List[ToolDiagnostic] = []
    tools_available: Dict[str, bool] = {}

    for tool_name, runner in [
        ("pyright", run_pyright),
        ("ruff", run_ruff),
        ("bandit", run_bandit),
        ("mypy", run_mypy),
    ]:
        try:
            diags = runner(existing)
            all_diags.extend(diags)
            tools_available[tool_name] = True
        except Exception as e:
            logger.warning("Tool %s failed: %s", tool_name, e)
            tools_available[tool_name] = False

    # Aggregate
    counts_category: Dict[str, int] = {}
    counts_tool: Dict[str, int] = {}
    counts_severity: Dict[str, int] = {}
    counts_file: Dict[str, int] = {}

    for d in all_diags:
        counts_category[d.category] = counts_category.get(d.category, 0) + 1
        counts_tool[d.tool] = counts_tool.get(d.tool, 0) + 1
        counts_severity[d.severity] = counts_severity.get(d.severity, 0) + 1
        counts_file[d.file_path] = counts_file.get(d.file_path, 0) + 1

    elapsed = time.monotonic() - t0

    logger.info(
        "Health scan: %d diagnostics from %d tools in %.1fs",
        len(all_diags), sum(tools_available.values()), elapsed,
    )

    return HealthScan(
        diagnostics=all_diags,
        counts_by_category=counts_category,
        counts_by_tool=counts_tool,
        counts_by_severity=counts_severity,
        counts_by_file=counts_file,
        total=len(all_diags),
        elapsed_s=elapsed,
        tools_available=tools_available,
    )


# =============================================================================
# Fix evaluation (function 3 — the KEY new capability)
# =============================================================================

def _apply_fix_to_source(source_text: str, proposed_fix: str) -> Optional[str]:
    """Attempt to apply a proposed fix to source text.

    Tries multiple strategies:
    1. If proposed_fix looks like a diff (contains --- or +++), skip (not supported yet)
    2. If proposed_fix is valid Python, replace the entire file (whole-file fix)
    3. If proposed_fix contains a recognisable search-replace pattern, apply it

    Returns patched source text, or None if the fix cannot be applied.
    """
    if not proposed_fix or not proposed_fix.strip():
        return None

    fix = proposed_fix.strip()

    # Strategy 1: search-replace pattern
    # Look for patterns like "Replace X with Y" or "Change X to Y"
    replace_pattern = re.compile(
        r"(?:replace|change)\s+[`'\"](.+?)[`'\"]\s+(?:with|to)\s+[`'\"](.+?)[`'\"]",
        re.IGNORECASE | re.DOTALL,
    )
    m = replace_pattern.search(fix)
    if m:
        old, new = m.group(1), m.group(2)
        if old in source_text:
            return source_text.replace(old, new, 1)

    # Strategy 2: if the fix is valid Python and looks like a complete replacement
    # (starts with import or def or class), treat it as a whole-file replacement
    try:
        compile(fix, "<fix>", "exec")
        # Only apply if it's substantial (>5 lines) — single expressions are
        # likely descriptions, not replacements
        if fix.count("\n") >= 5:
            return fix
    except SyntaxError:
        pass

    # Strategy 3: line-level replacement hints
    # Pattern: "Line N: old_code -> new_code"
    line_pattern = re.compile(r"[Ll]ine\s+(\d+):\s*(.+?)\s*->\s*(.+)")
    lines = source_text.splitlines(keepends=True)
    modified = False
    for lm in line_pattern.finditer(fix):
        lineno = int(lm.group(1)) - 1  # 0-indexed
        old_frag = lm.group(2).strip()
        new_frag = lm.group(3).strip()
        if 0 <= lineno < len(lines) and old_frag in lines[lineno]:
            lines[lineno] = lines[lineno].replace(old_frag, new_frag, 1)
            modified = True
    if modified:
        return "".join(lines)

    return None


def _count_tool_issues(tool_runner, file_path: str) -> int:
    """Run a tool on a single file and return the number of issues found."""
    try:
        diags = tool_runner([file_path])
        return len(diags)
    except Exception:
        return 0


def evaluate_fix(
    finding: Finding,
    source_paths: List[str],
    test_cmd: Optional[List[str]] = None,
) -> FixEvaluation:
    """Evaluate a single proposed fix in a sandbox.

    The process:
    1. Find the source file the finding refers to (or use first source_path)
    2. Copy it to a temp directory
    3. Apply the proposed fix
    4. Run type checkers and linters on the patched version
    5. Compare before/after diagnostic counts
    6. Optionally run tests

    Args:
        finding: The finding with a proposed_fix to evaluate.
        source_paths: Source files being analysed.
        test_cmd: Optional test command (e.g. ["python", "-m", "pytest", "test_file.py"]).

    Returns:
        FixEvaluation with before/after comparison.
    """
    t0 = time.monotonic()

    eval_result = FixEvaluation(
        finding_id=finding.finding_id,
        original_file="",
    )

    if not finding.proposed_fix or not finding.proposed_fix.strip():
        eval_result.verdict = "UNEVALUABLE"
        eval_result.apply_error = "No proposed fix text"
        eval_result.elapsed_s = time.monotonic() - t0
        return eval_result

    # Find the target file. Try to match from finding description,
    # fall back to first source path.
    target_path = _find_target_file(finding, source_paths)
    if not target_path or not os.path.isfile(target_path):
        eval_result.verdict = "UNEVALUABLE"
        eval_result.apply_error = f"Target file not found: {target_path}"
        eval_result.elapsed_s = time.monotonic() - t0
        return eval_result

    eval_result.original_file = target_path

    try:
        source_text = Path(target_path).read_text(encoding="utf-8")
    except OSError as e:
        eval_result.verdict = "UNEVALUABLE"
        eval_result.apply_error = f"Cannot read source: {e}"
        eval_result.elapsed_s = time.monotonic() - t0
        return eval_result

    # Pre-fix baselines
    eval_result.pre_type_errors = _count_tool_issues(run_pyright, target_path)
    eval_result.pre_ruff_errors = _count_tool_issues(run_ruff, target_path)
    eval_result.pre_bandit_issues = _count_tool_issues(run_bandit, target_path)

    # Apply fix in sandbox
    patched = _apply_fix_to_source(source_text, finding.proposed_fix)
    if patched is None:
        eval_result.fix_applied = False
        eval_result.apply_error = "Could not apply proposed fix to source"
        eval_result.verdict = "UNEVALUABLE"
        eval_result.elapsed_s = time.monotonic() - t0
        return eval_result

    eval_result.fix_applied = True

    # Write patched file to temp directory
    with tempfile.TemporaryDirectory(prefix="endocrine_fix_") as tmpdir:
        patched_path = os.path.join(tmpdir, os.path.basename(target_path))
        Path(patched_path).write_text(patched, encoding="utf-8")

        # Post-fix analysis
        eval_result.new_type_errors = _count_tool_issues(run_pyright, patched_path)
        eval_result.new_ruff_errors = _count_tool_issues(run_ruff, patched_path)
        eval_result.new_bandit_issues = _count_tool_issues(run_bandit, patched_path)

        # Net changes
        eval_result.net_type_errors = eval_result.new_type_errors - eval_result.pre_type_errors
        eval_result.net_ruff_errors = eval_result.new_ruff_errors - eval_result.pre_ruff_errors
        eval_result.net_bandit_issues = eval_result.new_bandit_issues - eval_result.pre_bandit_issues

        # Run tests if command provided
        if test_cmd:
            try:
                test_result = _run_tool(
                    test_cmd, timeout=_TOOL_TIMEOUT, cwd=tmpdir,
                )
                eval_result.tests_passed = test_result.returncode == 0
                eval_result.test_output = (
                    test_result.stdout[-2000:] + test_result.stderr[-500:]
                )
            except Exception as e:
                eval_result.tests_passed = None
                eval_result.test_output = f"Test execution failed: {e}"

    # Verdict
    eval_result.verdict = _compute_fix_verdict(eval_result)
    eval_result.elapsed_s = time.monotonic() - t0

    logger.info(
        "Fix eval %s: verdict=%s net_type=%+d net_ruff=%+d net_bandit=%+d (%.1fs)",
        finding.finding_id,
        eval_result.verdict,
        eval_result.net_type_errors,
        eval_result.net_ruff_errors,
        eval_result.net_bandit_issues,
        eval_result.elapsed_s,
    )

    return eval_result


def _find_target_file(finding: Finding, source_paths: List[str]) -> Optional[str]:
    """Find the source file a finding refers to.

    Looks for file paths mentioned in the finding description, then falls
    back to the first source path.
    """
    # Extract file paths from description
    path_pattern = re.compile(r"[\w/\\]+\.py\b")
    desc = finding.description + " " + finding.proposed_fix
    matches = path_pattern.findall(desc)

    for match in matches:
        # Check if any source path ends with this match
        for sp_path in source_paths:
            if sp_path.endswith(match) or match in sp_path:
                return sp_path

    # Fall back to first source path
    return source_paths[0] if source_paths else None


def _compute_fix_verdict(result: FixEvaluation) -> str:
    """Compute a verdict for a fix evaluation. Mechanical threshold comparison.

    SAFE: no new issues introduced, tests pass (if run)
    HARMFUL: new issues introduced or tests fail
    NEUTRAL: no change in issue counts, tests not run
    UNEVALUABLE: fix could not be applied
    """
    if not result.fix_applied:
        return "UNEVALUABLE"

    # Tests failed = harmful
    if result.tests_passed is False:
        return "HARMFUL"

    # New issues introduced = harmful
    total_net = result.net_type_errors + result.net_ruff_errors + result.net_bandit_issues
    if total_net > 0:
        return "HARMFUL"

    # Issues reduced and tests passed (or not run) = safe
    if total_net < 0:
        return "SAFE"

    # No change
    if result.tests_passed is True:
        return "SAFE"

    return "NEUTRAL"


def evaluate_fixes(
    findings: Sequence[Finding],
    source_paths: List[str],
    test_cmd: Optional[List[str]] = None,
    max_evals: int = 20,
) -> List[FixEvaluation]:
    """Evaluate proposed fixes for a batch of findings.

    Only evaluates findings that have a non-empty proposed_fix field.
    Caps at max_evals to prevent runaway tool invocations.

    Args:
        findings: Findings from a round.
        source_paths: Source files under analysis.
        test_cmd: Optional test command.
        max_evals: Maximum number of fixes to evaluate per batch.

    Returns:
        List of FixEvaluation results.
    """
    to_eval = [f for f in findings if f.proposed_fix and f.proposed_fix.strip()]
    to_eval = to_eval[:max_evals]

    results = []
    for finding in to_eval:
        result = evaluate_fix(finding, source_paths, test_cmd)
        results.append(result)

    logger.info(
        "Fix batch: %d/%d evaluated, %d SAFE, %d HARMFUL, %d NEUTRAL",
        len(results),
        len(findings),
        sum(1 for r in results if r.verdict == "SAFE"),
        sum(1 for r in results if r.verdict == "HARMFUL"),
        sum(1 for r in results if r.verdict == "NEUTRAL"),
    )

    return results


# =============================================================================
# Pacing signals (function 4)
# =============================================================================

@dataclass
class RoundTiming:
    """Timing data for one model in one round. Fed to pacing analysis."""
    model_id: str
    round_idx: int
    duration_s: float
    response_chars: int
    finding_count: int


def compute_pacing_signals(
    round_timings: List[RoundTiming],
    cumulative_context_chars: int,
    context_budget: int,
    novelty_counts: List[int],
    round_idx: int,
) -> List[PacingSignal]:
    """Compute pacing signals for the insect brain.

    Mechanical threshold comparisons — no deliberation.

    Args:
        round_timings: Timing data for each model in the current round.
        cumulative_context_chars: Total chars accumulated across all rounds.
        context_budget: Per-model context budget from config.
        novelty_counts: List of novel finding counts per round (index = round).
        round_idx: Current round index.

    Returns:
        List of PacingSignal (may be empty if everything is healthy).
    """
    signals: List[PacingSignal] = []

    # 1. Slow model detection
    if round_timings:
        durations = [rt.duration_s for rt in round_timings]
        median_duration = sorted(durations)[len(durations) // 2]
        for rt in round_timings:
            if rt.duration_s > median_duration * 2.5 and rt.duration_s > 30.0:
                signals.append(PacingSignal(
                    signal_type="slow_model",
                    detail=f"{rt.model_id} took {rt.duration_s:.1f}s (median {median_duration:.1f}s)",
                    model_id=rt.model_id,
                    metric_value=rt.duration_s,
                    threshold=median_duration * 2.5,
                    suggested_action="increase_timeout",
                ))

    # 2. Context growth rate
    if context_budget > 0:
        context_fraction = cumulative_context_chars / context_budget
        if context_fraction > 0.8:
            signals.append(PacingSignal(
                signal_type="context_growth",
                detail=f"Context at {context_fraction:.0%} of budget ({cumulative_context_chars}/{context_budget} chars)",
                metric_value=context_fraction,
                threshold=0.8,
                suggested_action="degrade_relay",
            ))

    # 3. Novelty plateau detection
    # If novelty has been zero or near-zero for 2+ consecutive rounds
    if len(novelty_counts) >= 3 and round_idx >= 2:
        recent = novelty_counts[-3:]
        if all(n <= 1 for n in recent):
            signals.append(PacingSignal(
                signal_type="novelty_plateau",
                detail=f"Novel findings in last 3 rounds: {recent}",
                metric_value=float(sum(recent)),
                threshold=3.0,
                suggested_action="check_convergence",
            ))

    # 4. Response size anomaly (model producing unusually large output)
    if round_timings:
        char_counts = [rt.response_chars for rt in round_timings if rt.response_chars > 0]
        if char_counts:
            median_chars = sorted(char_counts)[len(char_counts) // 2]
            for rt in round_timings:
                if rt.response_chars > median_chars * 3 and rt.response_chars > 10000:
                    signals.append(PacingSignal(
                        signal_type="context_growth",
                        detail=f"{rt.model_id} produced {rt.response_chars} chars (median {median_chars})",
                        model_id=rt.model_id,
                        metric_value=float(rt.response_chars),
                        threshold=float(median_chars * 3),
                        suggested_action="degrade_relay",
                    ))

    return signals


# =============================================================================
# Endocrine Layer (coordinator)
# =============================================================================

class EndocrineLayer:
    """Whole-body health monitor for the CDSFL bench system.

    Runs between rounds. Produces structured data for the insect brain.
    Mechanical — no deliberation, no content evaluation.

    Usage::

        endo = EndocrineLayer(
            source_paths=["bench/immune_agents.py", "bench/dynamic_management.py"],
        )

        # Between rounds:
        report = endo.run(
            round_idx=2,
            findings=round_findings,
            round_timings=timings,
            cumulative_context_chars=45000,
            context_budget=80000,
            novelty_counts=[5, 3, 1],
        )

        # Feed to insect brain:
        brain.endocrine_report = report
    """

    def __init__(
        self,
        source_paths: List[str],
        test_cmd: Optional[List[str]] = None,
        max_fix_evals: int = 20,
    ):
        self.source_paths = source_paths
        self.test_cmd = test_cmd
        self.max_fix_evals = max_fix_evals
        # History for trend detection
        self._scan_history: List[HealthScan] = []

    def run(
        self,
        round_idx: int,
        findings: Sequence[Finding],
        round_timings: Optional[List[RoundTiming]] = None,
        cumulative_context_chars: int = 0,
        context_budget: int = 80_000,
        novelty_counts: Optional[List[int]] = None,
    ) -> EndocrineReport:
        """Execute full endocrine cycle for one inter-round interval.

        Sequence:
        1. Health scan (static analysis)
        2. Fix evaluation (sandbox test proposed fixes)
        3. Pacing signals (timing and convergence checks)

        Args:
            round_idx: Current round.
            findings: Findings from the just-completed round.
            round_timings: Per-model timing data.
            cumulative_context_chars: Total context chars so far.
            context_budget: Per-model context budget.
            novelty_counts: Novel finding counts per round.

        Returns:
            EndocrineReport with all results.
        """
        t0 = time.monotonic()

        # 1. Health scan
        health = scan_health(self.source_paths)
        self._scan_history.append(health)

        # 2. Fix evaluation
        fix_evals = evaluate_fixes(
            findings,
            self.source_paths,
            self.test_cmd,
            self.max_fix_evals,
        )

        # 3. Pacing signals
        pacing = compute_pacing_signals(
            round_timings=round_timings or [],
            cumulative_context_chars=cumulative_context_chars,
            context_budget=context_budget,
            novelty_counts=novelty_counts or [],
            round_idx=round_idx,
        )

        elapsed = time.monotonic() - t0

        logger.info(
            "Endocrine cycle round %d: %d diagnostics, %d fix evals, %d pacing signals (%.1fs)",
            round_idx, health.total, len(fix_evals), len(pacing), elapsed,
        )

        return EndocrineReport(
            round_idx=round_idx,
            health_scan=health,
            fix_evaluations=fix_evals,
            pacing_signals=pacing,
            elapsed_s=elapsed,
        )

    def health_trend(self) -> Dict[str, List[int]]:
        """Return diagnostic count trends across rounds (by category).

        For the insect brain to detect worsening/improving code health.
        """
        trend: Dict[str, List[int]] = {}
        for scan in self._scan_history:
            for cat, count in scan.counts_by_category.items():
                trend.setdefault(cat, []).append(count)
        return trend
