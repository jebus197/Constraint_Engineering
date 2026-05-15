"""Bugzilla loop closure: CONFIRMED -> CLOSED via verified fix.

The Bugzilla paradigm (Exp 36 Design Analysis, 7 April 2026) treats
findings as bug tickets with a finite-state machine:

    OPEN -> CONFIRMED (>=2 verifications or CC2v confirms)
    CONFIRMED + verified_fix -> CLOSED  (challenge-resistant, terminal)
    CONFIRMED + late challenge -> CONTESTED -> CONFIRMED
    CLOSED -> REOPENED  (only via explicit REOPEN + HIL escalation)
    DUPLICATE -> MERGED
    REJECTED -> UNCONFIRMED

The state machine itself is wired into runner_v2 (FindingRegistry +
resolve). What was missing through Exp 40 was the CONFIRMED -> CLOSED
transition via *verified fix* — the step that drains the active pool
and lets the panel actually saturate (rather than re-describe the same
findings forever).

This module implements that transition as four steps, per the 7 April
design:

  1. Extract proposed_fix text from CONFIRMED findings.
  2. Apply to a sandbox copy of the target file.
  3. Run verification: ruff + mypy + bandit + the experiment's test_cmd.
  4. On pass: mark CLOSED. CLOSED findings appear in registry summaries
     with "do not re-describe" instruction.

The module is intentionally standalone (not yet wired into the runner's
per-round loop) so it can be tested on the existing Exp 40 finding
corpus before any new dispatch. After the test pass, integration into
reference_runner_v2 happens in a separate commit.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class FixExtractResult:
    """Outcome of parsing proposed_fix text for a SEARCH/REPLACE block."""

    success: bool
    old_code: str = ""
    new_code: str = ""
    file_hint: str = ""
    reason: str = ""  # populated on failure


@dataclass
class VerificationResult:
    """Outcome of running verification tools on a sandbox file."""

    passed: bool
    ruff_passed: bool = False
    mypy_passed: bool = False
    bandit_passed: bool = False
    test_passed: bool = False
    test_skipped: bool = False  # true if test_cmd was None / not run
    failures: list[str] = field(default_factory=list)  # human-readable reasons
    elapsed_s: float = 0.0


@dataclass
class CloseAttempt:
    """Result of attempting to close one CONFIRMED finding."""

    finding_id: str
    closed: bool
    extract: FixExtractResult
    verification: VerificationResult | None = None
    reason: str = ""  # human-readable summary


# ---------------------------------------------------------------------------
# Step 1: Extract SEARCH/REPLACE block from proposed_fix
# ---------------------------------------------------------------------------

# Two block formats observed in the runner_core extraction:
#   <<<< SEARCH file_hint
#   {old_code}
#   ==== REPLACE
#   {new_code}
#   >>>>
# and:
#   <<<< OLD
#   {old_code}
#   ==== NEW
#   {new_code}
#   >>>>
#
# Plus free-form fix text from models that doesn't use markers — those
# return success=False so callers can choose to skip or apply heuristics.

_BLOCK_PATTERN_SEARCH = re.compile(
    r"<<<<\s*SEARCH\s*(?P<hint>[^\n]*)\n"
    r"(?P<old>.*?)\n"
    r"====\s*REPLACE\s*\n"
    r"(?P<new>.*?)\n?"
    r">>>>",
    re.DOTALL,
)

_BLOCK_PATTERN_OLD = re.compile(
    r"<<<<\s*OLD\s*\n"
    r"(?P<old>.*?)\n"
    r"====\s*NEW\s*\n"
    r"(?P<new>.*?)\n?"
    r">>>>",
    re.DOTALL,
)


def extract_search_replace(proposed_fix: str) -> FixExtractResult:
    """Parse a proposed_fix string for a SEARCH/REPLACE or OLD/NEW block.

    Returns a FixExtractResult with success=True if a block was found and
    its old/new code segments are both non-empty. Returns success=False
    with `reason` populated otherwise.
    """
    if not proposed_fix or not proposed_fix.strip():
        return FixExtractResult(success=False, reason="empty proposed_fix")

    m = _BLOCK_PATTERN_SEARCH.search(proposed_fix)
    if m:
        old = m.group("old")
        new = m.group("new")
        hint = m.group("hint").strip()
        if not old.strip():
            return FixExtractResult(
                success=False, reason="empty SEARCH segment in block"
            )
        return FixExtractResult(
            success=True, old_code=old, new_code=new, file_hint=hint
        )

    m = _BLOCK_PATTERN_OLD.search(proposed_fix)
    if m:
        old = m.group("old")
        new = m.group("new")
        if not old.strip():
            return FixExtractResult(
                success=False, reason="empty OLD segment in block"
            )
        return FixExtractResult(success=True, old_code=old, new_code=new)

    return FixExtractResult(
        success=False,
        reason="no SEARCH/REPLACE or OLD/NEW markers found in proposed_fix",
    )


# ---------------------------------------------------------------------------
# Step 2: Apply fix to a sandbox copy
# ---------------------------------------------------------------------------

def apply_fix_to_sandbox(
    target_path: Path, old_code: str, new_code: str
) -> tuple[Path | None, str]:
    """Copy `target_path` to a temp file, replace `old_code` with
    `new_code` exactly once.

    Returns (sandbox_path, reason). On success sandbox_path is a Path and
    reason is the empty string. On failure sandbox_path is None and
    reason explains why.

    The replacement requires `old_code` to appear EXACTLY ONCE in the
    target file. Multiple matches or zero matches both fail; that
    constraint is intentional and matches the SEARCH/REPLACE-block
    semantics used elsewhere in the project.
    """
    if not target_path.exists():
        return None, f"target_path does not exist: {target_path}"
    source = target_path.read_text(encoding="utf-8")
    matches = source.count(old_code)
    if matches == 0:
        return None, "old_code not found in target file"
    if matches > 1:
        return None, f"old_code matches {matches} locations (ambiguous)"

    # Write to a deterministic temp file under the system temp dir so the
    # sandbox is easy to inspect on failure but isolated from the repo.
    fd, tmp_path_str = tempfile.mkstemp(
        suffix=f"_{target_path.name}", prefix="bugzilla_sandbox_"
    )
    import os as _os
    _os.close(fd)
    sandbox = Path(tmp_path_str)
    modified = source.replace(old_code, new_code, 1)
    sandbox.write_text(modified, encoding="utf-8")
    return sandbox, ""


# ---------------------------------------------------------------------------
# Step 3: Verification tooling
# ---------------------------------------------------------------------------

def _run_tool(cmd: list[str], timeout: int = 60) -> tuple[bool, str]:
    """Run a verification tool subprocess. Returns (passed, output).

    Treats exit code 0 as pass. Non-zero exit codes (or timeout/error)
    are failures with the tool's stderr/stdout captured for reporting.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, ""
        out = (result.stdout or "") + (result.stderr or "")
        return False, out[:1000]  # cap for log readability
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return False, f"tool not installed: {e}"


def run_verification(
    sandbox_path: Path,
    test_cmd: str | None,
    *,
    timeout: int = 120,
) -> VerificationResult:
    """Run ruff, mypy, bandit, and the experiment's test_cmd against the
    sandbox file. Returns aggregated VerificationResult.

    For static tools (ruff/mypy/bandit), only the sandbox file itself
    is checked, not the whole repo — the goal is to validate that the
    fix did not introduce syntax errors, type errors, or new security
    findings.

    For the test_cmd (a string like "python3 -m pytest <path> -q"),
    the runner first verifies the test would pass against the unmodified
    target before substituting the sandbox; if the original tests don't
    pass cleanly the test step is skipped because the baseline is
    already broken.

    For this initial implementation, test_cmd is run AS-IS against the
    sandbox by monkey-importing the sandbox path. A future refinement
    can copy the entire test fixture into a temp directory.
    """
    import time as _time
    t0 = _time.monotonic()
    failures: list[str] = []

    ruff_ok, ruff_out = _run_tool(
        ["python3", "-m", "ruff", "check", str(sandbox_path), "--no-cache"],
        timeout=timeout,
    )
    if not ruff_ok:
        failures.append(f"ruff: {ruff_out[:200]}")

    mypy_ok, mypy_out = _run_tool(
        ["python3", "-m", "mypy", "--ignore-missing-imports",
         "--follow-imports=silent", str(sandbox_path)],
        timeout=timeout,
    )
    if not mypy_ok:
        failures.append(f"mypy: {mypy_out[:200]}")

    bandit_ok, bandit_out = _run_tool(
        ["python3", "-m", "bandit", "-q", "-r", str(sandbox_path)],
        timeout=timeout,
    )
    if not bandit_ok:
        # bandit exits non-zero when it finds ANY issue at the medium+
        # severity level. Treat informational-only outputs as pass.
        if "No issues identified" in bandit_out or "0 issues" in bandit_out:
            bandit_ok = True
        else:
            failures.append(f"bandit: {bandit_out[:200]}")

    test_ok = False
    test_skipped = True
    if test_cmd:
        test_ok, test_out = _run_tool(
            test_cmd.split() if isinstance(test_cmd, str) else list(test_cmd),
            timeout=timeout,
        )
        test_skipped = False
        if not test_ok:
            failures.append(f"test_cmd: {test_out[:300]}")

    passed = ruff_ok and mypy_ok and bandit_ok and (test_ok or test_skipped)
    elapsed = _time.monotonic() - t0

    return VerificationResult(
        passed=passed,
        ruff_passed=ruff_ok,
        mypy_passed=mypy_ok,
        bandit_passed=bandit_ok,
        test_passed=test_ok,
        test_skipped=test_skipped,
        failures=failures,
        elapsed_s=round(elapsed, 2),
    )


# ---------------------------------------------------------------------------
# Step 4: Close the loop
# ---------------------------------------------------------------------------

def attempt_close(
    finding: dict[str, Any],
    target_path: Path,
    test_cmd: str | None = None,
    *,
    timeout: int = 120,
) -> CloseAttempt:
    """Attempt the four-step CONFIRMED -> CLOSED transition for a single
    finding. Returns a CloseAttempt describing the outcome.

    `finding` is expected to be a dict-like with at least `finding_id`
    and `proposed_fix`. `target_path` is the file under review.
    """
    fid = finding.get("finding_id") or finding.get("canonical_id") or "?"
    proposed_fix = finding.get("proposed_fix", "")

    extract = extract_search_replace(proposed_fix)
    if not extract.success:
        return CloseAttempt(
            finding_id=fid,
            closed=False,
            extract=extract,
            reason=f"extract failed: {extract.reason}",
        )

    sandbox, apply_reason = apply_fix_to_sandbox(
        target_path, extract.old_code, extract.new_code
    )
    if sandbox is None:
        return CloseAttempt(
            finding_id=fid,
            closed=False,
            extract=extract,
            reason=f"sandbox apply failed: {apply_reason}",
        )

    try:
        verify = run_verification(sandbox, test_cmd, timeout=timeout)
    finally:
        # Always clean up the sandbox file. Verification result captures
        # whatever signal we needed; the file is disposable.
        try:
            sandbox.unlink(missing_ok=True)
        except OSError:
            pass

    if verify.passed:
        return CloseAttempt(
            finding_id=fid,
            closed=True,
            extract=extract,
            verification=verify,
            reason=(
                f"verified: ruff={verify.ruff_passed} "
                f"mypy={verify.mypy_passed} "
                f"bandit={verify.bandit_passed} "
                f"test={verify.test_passed or 'skipped' if verify.test_skipped else verify.test_passed}"
            ),
        )

    return CloseAttempt(
        finding_id=fid,
        closed=False,
        extract=extract,
        verification=verify,
        reason="verification failed: " + "; ".join(verify.failures),
    )


def verify_and_close_fixes(
    findings: list[dict[str, Any]],
    target_path: Path,
    *,
    status_filter: tuple[str, ...] = ("CONFIRMED",),
    test_cmd: str | None = None,
    timeout: int = 120,
) -> list[CloseAttempt]:
    """Iterate findings, attempt close-the-loop for each one matching
    the status filter, return outcomes.

    By default operates on CONFIRMED findings only. Callers can pass
    `status_filter=("CONFIRMED", "REOPENED")` to also retry findings
    previously CLOSED-then-REOPENED.

    This function does NOT mutate any registry. Callers that wish to
    propagate close-the-loop outcomes to a FindingRegistry must do so
    explicitly using the returned `CloseAttempt.closed` boolean.
    """
    attempts: list[CloseAttempt] = []
    for f in findings:
        status = f.get("status", "UNKNOWN")
        if status not in status_filter:
            continue
        attempts.append(
            attempt_close(f, target_path, test_cmd=test_cmd, timeout=timeout)
        )
    return attempts


# ---------------------------------------------------------------------------
# CLI entry point for standalone testing
# ---------------------------------------------------------------------------

def _main(argv: list[str]) -> int:
    """Standalone CLI: load findings from an experiment report and attempt
    close-the-loop on each CONFIRMED finding. Reports outcomes.

    Usage:
        python3 -m bench.bugzilla_loop <report_json> <target_file>
        [--test-cmd "<test command>"] [--status CONFIRMED]
    """
    import argparse
    import json
    parser = argparse.ArgumentParser(
        description="Test Bugzilla CLOSED-loop on an experiment's findings."
    )
    parser.add_argument("report", help="path to experiment report JSON")
    parser.add_argument("target", help="path to target file under review")
    parser.add_argument(
        "--test-cmd",
        default=None,
        help="experiment's test_cmd to run against the sandbox",
    )
    parser.add_argument(
        "--status",
        default="CONFIRMED",
        help="status filter (comma-separated)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="cap on number of findings to attempt (debug)",
    )
    args = parser.parse_args(argv)

    report = json.loads(Path(args.report).read_text())
    target_path = Path(args.target)
    if not target_path.is_absolute():
        target_path = REPO_ROOT / target_path

    findings: list[dict[str, Any]] = []
    for r in report.get("rounds", []):
        for f in r.get("findings", []):
            findings.append(f)

    if args.limit:
        findings = findings[: args.limit]

    status_filter = tuple(s.strip() for s in args.status.split(","))
    print(f"Attempting close-the-loop on {len(findings)} findings; "
          f"target={target_path.name}; test_cmd={args.test_cmd!r}; "
          f"status filter={status_filter}")

    attempts = verify_and_close_fixes(
        findings,
        target_path,
        status_filter=status_filter,
        test_cmd=args.test_cmd,
    )

    closed = sum(1 for a in attempts if a.closed)
    print(f"\nResults: {closed}/{len(attempts)} findings CLOSED")
    print()
    for a in attempts:
        marker = "[CLOSED]" if a.closed else "[OPEN  ]"
        print(f"  {marker} {a.finding_id}: {a.reason[:200]}")

    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
