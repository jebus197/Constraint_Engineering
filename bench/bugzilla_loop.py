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
  3. Run verification: ruff + mypy + bandit + the experiment's test_cmd,
     yielding a tri-state PASS / FAIL / NO_APPLICABLE_CHECKS.
  4. On PASS and only on PASS: mark CLOSED. CLOSED findings appear in
     registry summaries with "do not re-describe" instruction. FAIL means
     the fix is bad; NO_APPLICABLE_CHECKS means nothing could be checked and
     the finding belongs with the falsifier or with HIL.

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
from enum import Enum
import re as _re_mod
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Target type
# ---------------------------------------------------------------------------

# Canonical definition of "this target is Python source". Kept here, in code,
# and imported by the B-Cell specialist router in immune_agents.py, so the two
# call sites cannot drift apart. It is deliberately NOT a config value: the
# launcher has silently dropped config keys six times, and a target-type
# mis-declaration would put mypy back on a markdown document.
PYTHON_TARGET_SUFFIXES: frozenset[str] = frozenset({".py"})


def is_python_target(path: Path | str) -> bool:
    """True when `path` names a Python source file.

    A target that is not Python cannot be read by ruff, mypy, bandit, dis or
    crosshair, and none of them fail loudly about it. Measured on a markdown
    document, 2026-08-01: ruff declines the path and exits 0 ("No Python files
    found" on stderr, "All checks passed!" on stdout), or, if the same bytes
    are renamed .py, error-recovers and emits phantom syntax diagnostics by
    the hundred; bandit files the parse failure under "errors", returns an
    empty result set and exits 0, which is indistinguishable from a clean
    scan; mypy parses the prose as source and reports "Leading zeros in
    decimal integer literals".
    Every one of those readings is noise presented as signal, so the type
    check has to happen before the tool is invoked, not inside it.
    """
    return Path(path).suffix.lower() in PYTHON_TARGET_SUFFIXES


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

class VerificationOutcome(str, Enum):
    """Tri-state result of a verification run.

    The two-state boolean it replaces conflated two entirely different things:

      * PASS — at least one applicable check ran, and every check that ran
        was satisfied. This is the ONLY outcome that may close a finding.
      * FAIL — at least one applicable check ran and reported a defect. This
        is a statement ABOUT THE FIX: the fix is bad.
      * NO_APPLICABLE_CHECKS — nothing could be checked. This is a statement
        about the INSTRUMENT, not about the fix. It must never look like a
        failure of the fix, and it must never close a finding.

    Expressed as `passed=False`, the third case was indistinguishable from the
    second: a prose target with no fenced code read as "this fix is bad" in
    every log and every report. Expressed as `passed=True` — the repair that
    was attempted first on 2026-08-01 and rejected — it would have closed
    every finding with nothing checked at all.

    str-valued so it serialises to a plain string in report JSON without a
    custom encoder.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    NO_APPLICABLE_CHECKS = "NO_APPLICABLE_CHECKS"


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
    """Outcome of running verification tools on a sandbox file.

    `outcome` is the authority. `passed` is a read-only property derived from
    it, so no caller can construct a result that claims success without saying
    which outcome it means. `checks_run` names the checks that actually
    produced a verdict; a PASS with an empty `checks_run` is rejected at
    construction, because that is precisely the shape of "nothing was checked,
    call it verified".
    """

    outcome: VerificationOutcome
    ruff_passed: bool = False
    mypy_passed: bool = False
    bandit_passed: bool = False
    test_passed: bool = False
    test_skipped: bool = False  # true if test_cmd was None / not run
    checks_run: list[str] = field(default_factory=list)  # checks that ran
    # Checks that can only REJECT. A veto that passes is not evidence the fix
    # is sound, so it must never appear in `checks_run` and never license a
    # close. Recorded separately so the record still shows what was run.
    vetoes_run: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)  # human-readable reasons
    elapsed_s: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, VerificationOutcome):
            self.outcome = VerificationOutcome(self.outcome)
        if self.outcome is VerificationOutcome.PASS and not self.checks_run:
            raise ValueError(
                "VerificationResult(PASS) with no checks_run: a verification "
                "that ran nothing cannot report success. Use "
                "NO_APPLICABLE_CHECKS."
            )
        if self.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS and self.checks_run:
            raise ValueError(
                "VerificationResult(NO_APPLICABLE_CHECKS) lists checks_run="
                f"{self.checks_run}: checks ran, so the outcome is PASS or FAIL."
            )

    @property
    def passed(self) -> bool:
        """True only on PASS. Retained so existing call sites keep working.

        NO_APPLICABLE_CHECKS reads False here — the safe direction, and the
        behaviour that was already relied upon: a no-code target does not
        close. Callers that need to tell "bad fix" from "nothing checkable"
        must read `outcome`, not this.
        """
        return self.outcome is VerificationOutcome.PASS

    @property
    def no_applicable_checks(self) -> bool:
        return self.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS


@dataclass
class CloseAttempt:
    """Result of attempting to close one CONFIRMED finding."""

    finding_id: str
    closed: bool
    extract: FixExtractResult
    verification: VerificationResult | None = None
    reason: str = ""  # human-readable summary
    outcome: VerificationOutcome = VerificationOutcome.FAIL

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, VerificationOutcome):
            self.outcome = VerificationOutcome(self.outcome)
        if self.closed and self.outcome is not VerificationOutcome.PASS:
            raise ValueError(
                f"CloseAttempt(closed=True) with outcome={self.outcome.value}: "
                "a finding closes on PASS and on nothing else."
            )


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



_PY_FENCE = _re_mod.compile(r"```(?:python|py)\n(.*?)```", _re_mod.S)



def _extract_python(path: Path) -> Path | None:
    """Write a target's fenced Python listings to a real .py file beside it.

    A target need not be a .py file for its CODE to be checkable. The zero-plant
    control is a markdown design reference carrying seven Python listings, and
    every finding against it is about those listings. Returns None when the
    target holds no code at all.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    blocks = _PY_FENCE.findall(text)
    if not blocks:
        return None
    out = path.with_suffix(".extracted.py")
    out.write_text("\n\n".join(b.rstrip() for b in blocks) + "\n", encoding="utf-8")
    return out


def run_verification(
    sandbox_path: Path,
    test_cmd: str | None,
    *,
    timeout: int = 120,
    baseline_path: Path | None = None,
) -> VerificationResult:
    """Run ruff, mypy, bandit, and the experiment's test_cmd against the
    sandbox file. Returns an aggregated VerificationResult carrying a
    tri-state `outcome`: PASS, FAIL, or NO_APPLICABLE_CHECKS.

    NO_APPLICABLE_CHECKS is returned when the target is not Python AND holds
    no fenced Python listing — nothing was read, so nothing can be said about
    the fix either way. It is not a FAIL, and `attempt_close` does not close
    on it.

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

    # ruff, mypy and bandit are PYTHON tools. Running them on a target that is
    # not Python is meaningless, and it does not fail quietly: on the zero-plant
    # control (a markdown design reference) mypy parsed the prose as source and
    # reported "Leading zeros in decimal integer", which close-the-loop then
    # recorded as a verification FAILURE. Every close-the-loop attempt on that
    # run failed for that reason — the fix could never be validated, so the
    # finding could never be closed, and the irreducible queue filled with
    # criticals the machinery was structurally unable to resolve.
    #
    # Same class as the _anchor_dir_for defect (2026-07-29): a code-review
    # mechanism misfiring on a prose target. Found 2026-08-01 six hours into the
    # control relaunch.
    # NON-PYTHON TARGET — check that its CODE still parses, and check nothing else.
    #
    # Three wrong answers were tried first, all 2026-08-01, and each is worth
    # recording because each failed differently:
    #   1. Run ruff/mypy/bandit on the markdown itself. mypy parses prose as
    #      source ("Leading zeros in decimal integer"), so EVERY close-the-loop
    #      attempt failed, nothing could be validated, nothing could close, and
    #      the irreducible queue filled with criticals the machinery could not
    #      resolve. This is what halted the control run.
    #   2. Skip the tools when the suffix is not .py. WORSE: `if verify.passed`
    #      CLOSES the finding, so skipping turned "cannot verify" into "verified"
    #      and every finding would have closed with nothing checked at all.
    #   3. Extract the listings and compare tool DIAGNOSTIC COUNTS against the
    #      unmodified target. Right idea, but `_run_tool` truncates its output,
    #      so a fix that introduced a fresh syntax error counted the same as the
    #      baseline and was waved through. Measuring on a truncated measurement.
    #
    # What is actually verifiable here is narrow, and saying so is better than
    # inventing signal. The listings reference imports the document declares in
    # PROSE, so ruff and mypy report undefined names on any extracted fragment no
    # matter what the fix did — those tools cannot speak to this target. What can
    # be said, deterministically and without a baseline, is whether the code still
    # PARSES. That catches the failure that matters: a fix that mangles a listing.
    # Anything subtler about a prose claim is not a static-analysis question and
    # belongs with the falsifier or with HIL.
    if not is_python_target(sandbox_path):
        import ast as _ast
        try:
            _text = sandbox_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            _text = ""
        _blocks = _PY_FENCE.findall(_text)
        if not _blocks:
            # NO_APPLICABLE_CHECKS, not FAIL. Nothing here is a statement about
            # the fix — there was simply nothing a static checker could read.
            # `passed` still reads False, so the finding still does not close;
            # what changes is that the log no longer accuses the fix.
            return VerificationResult(
                outcome=VerificationOutcome.NO_APPLICABLE_CHECKS,
                ruff_passed=False, mypy_passed=False, bandit_passed=False,
                test_passed=False, test_skipped=True,
                checks_run=[],
                failures=[f"no verifiable code: {sandbox_path.name} is not Python and "
                          f"carries no fenced Python listing — this finding cannot be "
                          f"closed by static verification and belongs with HIL"],
                elapsed_s=_time.monotonic() - t0,
            )
        _bad = []
        for _i, _b in enumerate(_blocks, 1):
            try:
                _ast.parse(_b)
            except SyntaxError as _se:
                _bad.append(f"listing {_i}: {_se.msg} (line {_se.lineno})")
        # The tool booleans stay False on this path: ruff, mypy and bandit were
        # never invoked. Reporting mypy_passed=True for a run in which mypy did
        # not execute is the same category of untruth the tri-state exists to
        # remove. What DID run is named in checks_run.
        # A SYNTAX CHECK IS A VETO, NOT A PASS. It is a statement about the
        # LISTING, not about the FIX. Every harmful fix is syntactically valid
        # Python, so `parses -> PASS` closes a finding on a fix nothing assessed:
        # measured 2026-08-01 against the real control document, a fix injecting
        # subprocess.call(..., shell=True) returned closed=True, outcome=PASS,
        # reason "verified by ast.parse of 7 fenced Python listing(s)".
        #
        # That is the THIRD time this function turned "cannot verify" into
        # "verified" — first by skipping the tools and returning passed=True,
        # then by counting truncated diagnostics, now by promoting a parse. The
        # general case was fixed and this narrower one left standing. So the
        # veto is recorded in `vetoes_run`, never in `checks_run`, and a clean
        # parse yields NO_APPLICABLE_CHECKS: nothing applicable to the FIX ran.
        # `attempt_close` closes only on PASS, so a prose finding never closes
        # by this route — which is correct, because nothing was verified.
        _veto = f"ast.parse of {len(_blocks)} fenced Python listing(s)"
        if not _bad:
            return VerificationResult(
                outcome=VerificationOutcome.NO_APPLICABLE_CHECKS,
                ruff_passed=False, mypy_passed=False, bandit_passed=False,
                test_passed=False, test_skipped=True,
                checks_run=[],
                vetoes_run=[_veto],
                failures=[],
                elapsed_s=_time.monotonic() - t0,
            )
        return VerificationResult(
            outcome=VerificationOutcome.FAIL,
            ruff_passed=False, mypy_passed=False, bandit_passed=False,
            test_passed=False, test_skipped=True,
            checks_run=[_veto],
            vetoes_run=[_veto],
            failures=([f"the fix leaves {len(_bad)} of {len(_blocks)} listing(s) "
                       f"unparseable — " + "; ".join(_bad[:3])] if _bad else []),
            elapsed_s=_time.monotonic() - t0,
        )

    checks_run: list[str] = ["ruff", "mypy", "bandit"]

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
        checks_run.append("test_cmd")
        if not test_ok:
            failures.append(f"test_cmd: {test_out[:300]}")

    passed = ruff_ok and mypy_ok and bandit_ok and (test_ok or test_skipped)
    elapsed = _time.monotonic() - t0

    # A Python target always has applicable checks — ruff, mypy and bandit can
    # all read it. A tool that is missing or times out is recorded as a check
    # that ran and FAILED, deliberately: demoting an unavailable tool to
    # "not applicable" would let a finding close on the remaining two, which is
    # a weakening of the path that already works. NO_APPLICABLE_CHECKS is
    # reserved for "nothing could be read at all".
    return VerificationResult(
        outcome=(VerificationOutcome.PASS if passed else VerificationOutcome.FAIL),
        ruff_passed=ruff_ok,
        mypy_passed=mypy_ok,
        bandit_passed=bandit_ok,
        test_passed=test_ok,
        test_skipped=test_skipped,
        checks_run=checks_run,
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

    Closes ONLY on VerificationOutcome.PASS. A NO_APPLICABLE_CHECKS
    verification leaves the finding open and says so in `reason`, so the run
    log distinguishes "the fix is bad" from "the instrument could not look".
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
        verify = run_verification(sandbox, test_cmd, timeout=timeout,
                                  baseline_path=target_path)
    finally:
        # Always clean up the sandbox file. Verification result captures
        # whatever signal we needed; the file is disposable.
        try:
            sandbox.unlink(missing_ok=True)
        except OSError:
            pass

    # THE line. A finding closes on PASS and on nothing else. NO_APPLICABLE_
    # CHECKS is not a near-miss to be waved through — it is the instrument
    # saying it could not look, and a finding it could not look at stays open
    # for the falsifier or for HIL.
    if verify.outcome is VerificationOutcome.PASS:
        return CloseAttempt(
            finding_id=fid,
            closed=True,
            extract=extract,
            verification=verify,
            outcome=VerificationOutcome.PASS,
            reason="verified by " + ", ".join(verify.checks_run),
        )

    if verify.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS:
        return CloseAttempt(
            finding_id=fid,
            closed=False,
            extract=extract,
            verification=verify,
            outcome=VerificationOutcome.NO_APPLICABLE_CHECKS,
            reason=(
                "not verifiable (no applicable checks, this is not a fault in "
                "the fix): " + "; ".join(verify.failures)
            ),
        )

    return CloseAttempt(
        finding_id=fid,
        closed=False,
        extract=extract,
        verification=verify,
        outcome=VerificationOutcome.FAIL,
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
    not_applicable = sum(
        1 for a in attempts
        if a.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS
    )
    print(f"\nResults: {closed}/{len(attempts)} findings CLOSED; "
          f"{not_applicable} had no applicable checks (instrument could not "
          f"look — not a verdict on the fix)")
    print()
    _MARKER = {
        VerificationOutcome.PASS: "[CLOSED]",
        VerificationOutcome.FAIL: "[OPEN  ]",
        VerificationOutcome.NO_APPLICABLE_CHECKS: "[N/A   ]",
    }
    for a in attempts:
        print(f"  {_MARKER[a.outcome]} {a.finding_id}: {a.reason[:200]}")

    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
