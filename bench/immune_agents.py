"""Immune agent pipeline for CDSFL verification (Run 9+).

Maps biological immune cell types to specialised verification agents,
each running in parallel with a distinct toolset:

    Dendritic Cell  — Triage: classify findings, extract testable claims
    Cytotoxic T     — Code FFF: read source, verify bugs exist
    B-Cell          — Math/Logic: SymPy + z3 + statsmodels cross-verification
    NK Cell         — Pattern memory: dedup + known false-positive matching
    Helper T        — Synthesis: aggregate verdicts, confidence-weighted voting
    Regulatory T    — Meta-verification: prevent autoimmune (over-rejection)

Architecture:
    Stage 1 (sequential):  Dendritic Cell triage (~1s)
    Stage 2 (parallel):    CT + B-Cell + NK Cell (~30-60s, bottleneck is CT)
    Stage 3 (sequential):  Helper T synthesis + Regulatory T meta-check (~1s)

Hardware target: M1 8GB Mac. CT uses claude CLI (network-bound).
B-Cell and NK are Python subprocess calls (CPU-light). 6 concurrent
agents observed stable on this hardware.
"""

from __future__ import annotations

import ast
import concurrent.futures
import glob as globmod
import json
import os
import re
import shutil
import subprocess as sp
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from bench.dm._types import Finding
from bench.dm._convergence import _finding_similarity


# ═══════════════════════════════════════════════════════════════════════════════
# Tool discovery
# ═══════════════════════════════════════════════════════════════════════════════

def _find_python_with_tools() -> str:
    """Find Python interpreter that has z3, sympy, statsmodels installed."""
    candidates = [
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
        shutil.which("python3.13") or "",
        shutil.which("python3.12") or "",
        sys.executable,
    ]
    for py in candidates:
        if not py or not os.path.isfile(py):
            continue
        try:
            r = sp.run(
                [py, "-c", "import sympy, z3, statsmodels; print('ok')"],
                capture_output=True, text=True, timeout=10,
            )
            if "ok" in r.stdout:
                return py
        except (sp.TimeoutExpired, OSError):
            continue
    return sys.executable  # fallback


def _find_claude_cli() -> Optional[str]:
    """Find claude CLI binary."""
    # Check standard locations
    if shutil.which("claude"):
        return shutil.which("claude")

    # macOS app bundle locations
    app_support = Path.home() / "Library" / "Application Support" / "Claude"
    patterns = [
        str(app_support / "claude-code" / "*" / "claude.app" / "Contents" / "MacOS" / "claude"),
        str(app_support / "claude-code-vm" / "*" / "claude"),
    ]
    for pattern in patterns:
        matches = sorted(globmod.glob(pattern), reverse=True)  # newest first
        if matches and os.path.isfile(matches[0]):
            return matches[0]

    return None


# WP3e: Lazy tool discovery with per-call retry + caching.
# Module-level static initialisation permanently locks to fallback if first
# import fails (MF-36/C5-24). Lazy discovery retries on each call, caching
# successful results.
_PYTHON_TOOLS_CACHE: Optional[str] = None
_CLAUDE_CLI_CACHE: Optional[str] = None


def _get_python_tools() -> str:
    """Lazy-discovered Python interpreter with tools. Retries on failure."""
    global _PYTHON_TOOLS_CACHE, PYTHON_TOOLS
    if _PYTHON_TOOLS_CACHE is not None:
        return _PYTHON_TOOLS_CACHE
    result = _find_python_with_tools()
    if result != sys.executable:
        _PYTHON_TOOLS_CACHE = result  # Cache only successful discovery
        PYTHON_TOOLS = result  # Bug#14 fix: sync backward-compat variable
    return result


def _get_claude_cli() -> Optional[str]:
    """Lazy-discovered claude CLI. Retries on failure."""
    global _CLAUDE_CLI_CACHE, CLAUDE_CLI
    if _CLAUDE_CLI_CACHE is not None:
        return _CLAUDE_CLI_CACHE
    result = _find_claude_cli()
    if result is not None:
        _CLAUDE_CLI_CACHE = result
        CLAUDE_CLI = result  # Bug#14 fix: sync backward-compat variable
    return result


# Backward compatibility — initial discovery populates cache
PYTHON_TOOLS: str = _find_python_with_tools()
CLAUDE_CLI: Optional[str] = _find_claude_cli()
_PYTHON_TOOLS_CACHE = PYTHON_TOOLS if PYTHON_TOOLS != sys.executable else None
_CLAUDE_CLI_CACHE = CLAUDE_CLI


# ═══════════════════════════════════════════════════════════════════════════════
# Data types
# ═══════════════════════════════════════════════════════════════════════════════

class CellType(Enum):
    """Immune cell types mapped to verification roles."""
    DENDRITIC = "dendritic"
    CYTOTOXIC_T = "cytotoxic_t"
    B_CELL = "b_cell"
    NK_CELL = "nk_cell"
    HELPER_T = "helper_t"
    REGULATORY_T = "regulatory_t"


class ClaimType(Enum):
    """Classification of a finding's testable claim."""
    MATHEMATICAL = "mathematical"      # equations, inequalities, bounds
    LOGICAL = "logical"                # if/then invariants, reachability
    CODE_STRUCTURAL = "code_structural"  # missing method, wrong decorator
    CODE_BEHAVIORAL = "code_behavioral"  # bug in logic, wrong return value
    STATISTICAL = "statistical"        # distribution claims, significance
    UNCATEGORISED = "uncategorised"


@dataclass
class CellVerdict:
    """A single verdict from one immune cell on one finding."""
    cell_type: CellType
    finding_id: str
    verdict: str          # CONFIRMED, REJECTED, UNCERTAIN, DUPLICATE, NOVEL
    confidence: float     # 0.0–1.0
    evidence: str         # explanation
    tool_used: str        # which tool produced this verdict
    elapsed_s: float = 0.0


@dataclass
class TriagedFinding:
    """Finding annotated by Dendritic Cell with claim classification."""
    finding: Finding
    claim_type: ClaimType
    extracted_claim: str = ""       # the testable assertion pulled from description
    is_duplicate: bool = False      # NK Cell flag
    duplicate_of: Optional[str] = None
    similarity: float = 0.0


@dataclass
class ImmuneResponse:
    """Complete immune response for a batch of findings."""
    triaged: List[TriagedFinding]
    cell_verdicts: Dict[str, List[CellVerdict]]  # finding_id → verdicts
    final_verdicts: Dict[str, str]               # finding_id → CONFIRMED/REJECTED/UNCERTAIN
    final_confidences: Dict[str, float]           # finding_id → aggregated confidence
    filtered_findings: List[Finding]              # findings that survived filtering
    rejected_findings: List[Finding]              # findings removed by immune response
    rejection_rate: float
    autoimmune_flag: bool           # True if Regulatory T flagged over-rejection
    stage_timings: Dict[str, float]
    tool_usage: Dict[str, int]      # tool_name → times_used
    observation_only: bool          # if True, filtered_findings == all findings
    barrier_results: List[Any] = field(default_factory=list)  # SkinBarrierResult list


# ═══════════════════════════════════════════════════════════════════════════════
# Claim detection patterns
# ═══════════════════════════════════════════════════════════════════════════════

_MATH_PATTERN = re.compile(
    r"(?:"
    r"[=<>!]=?"
    r"|[+\-*/^]"
    r"|\bsqrt\b|\blog\b|\bexp\b"
    r"|\b\d+\s*[*/+\-]"
    r"|\bEq\(|\bGt\(|\bLt\("
    r"|\bbound\b|\bthreshold\b|\binequality\b"
    r"|\bformula\b|\bequation\b"
    r")"
)

_LOGIC_PATTERN = re.compile(
    r"(?:"
    r"\bif\b.*\bthen\b"
    r"|\breachable\b|\bunreachable\b"
    r"|\binvariant\b|\bprecondition\b|\bpostcondition\b"
    r"|\bimplies\b|\bcontradiction\b"
    r"|\balways\b.*\bnever\b|\bnever\b.*\balways\b"
    r")",
    re.IGNORECASE,
)

_STAT_PATTERN = re.compile(
    r"(?:"
    # MF-31 fix: match p-values with or without leading zero (e.g. .05, 0.05)
    r"\bsignificant\b|\bp-value\b|\bp\s*[<=]\s*0?\.\d"
    r"|\bdistribution\b|\bcorrelation\b|\bregression\b"
    r"|\bmean\b.*\bdiffer\b|\bvariance\b"
    r"|\bKruskal\b|\bWilcoxon\b|\bt-test\b|\bchi-squared\b"
    r")",
    re.IGNORECASE,
)

_STRUCT_PATTERN = re.compile(
    r"(?:"
    r"@\w+\s+decorator"
    r"|\bmissing\b.*\bmethod\b|\bmethod\b.*\bmissing\b"
    r"|\bno\b.*\bclass\b|\bclass\b.*\bnot\s+defined\b"
    r"|\bdecorator\b.*\bnot\s+found\b"
    r")",
    re.IGNORECASE,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DENDRITIC CELL — Triage and classification
# ═══════════════════════════════════════════════════════════════════════════════

def _classify_claim(finding: Finding) -> Tuple[ClaimType, str]:
    """Classify a finding's claim type and extract the testable assertion."""
    desc = finding.description

    # Check specific patterns before generic math (which matches broadly)
    if _STAT_PATTERN.search(desc):
        return ClaimType.STATISTICAL, desc

    if _LOGIC_PATTERN.search(desc):
        return ClaimType.LOGICAL, desc

    if _STRUCT_PATTERN.search(desc):
        return ClaimType.CODE_STRUCTURAL, desc

    if _MATH_PATTERN.search(desc):
        # MF-03/MF-04 fix: extract ALL backtick expressions (not just first)
        # and preserve surrounding context for preconditions
        # Bug#17 fix: use ", " separator instead of " AND " (invalid SymPy syntax)
        eq_matches = re.findall(r'`([^`]+[=<>+\-*/^][^`]+)`', desc)
        if eq_matches:
            claim = ", ".join(eq_matches) if len(eq_matches) > 1 else eq_matches[0]
        else:
            claim = desc
        return ClaimType.MATHEMATICAL, claim

    # Default: behavioural code claim (most findings are about code bugs)
    return ClaimType.CODE_BEHAVIORAL, desc


def dendritic_cell_triage(findings: List[Finding]) -> List[TriagedFinding]:
    """Stage 1: Classify all findings by claim type.

    The Dendritic Cell bridges innate and adaptive immunity by
    determining which verification pathway each finding needs.
    Fast, pure-Python, no external tools.
    """
    triaged = []
    for f in findings:
        claim_type, extracted = _classify_claim(f)
        triaged.append(TriagedFinding(
            finding=f,
            claim_type=claim_type,
            extracted_claim=extracted,
        ))
    return triaged


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CYTOTOXIC T-CELL — Structurally-enforced code investigation
#
# The CT agent is an INVESTIGATOR, not a judge. It reads source code and
# reports what it found at specific file:line locations. Its claims are
# then MECHANICALLY VERIFIED against the actual source by _verify_ct_claim().
# The verdict is determined by code, not by the agent's opinion.
#
# Structural enforcement:
#   1. Output schema (ct_verdict_schema.json) forces structured evidence
#   2. Each evidence item must cite file, line, and code_snippet
#   3. _verify_ct_claim() reads the real file at the real line and checks
#      whether the snippet matches — if it doesn't, confidence drops to 0
#   4. Verdict is computed from verification results, not from agent text
# ═══════════════════════════════════════════════════════════════════════════════

_CT_SCHEMA_PATH = Path(__file__).parent / "ct_verdict_schema.json"


def _build_ct_prompt(findings: List[TriagedFinding], source_paths: List[str]) -> str:
    """Build the CT investigation prompt.

    The prompt instructs the agent to INVESTIGATE, not JUDGE. It must
    produce structured evidence with exact file:line:code citations.

    C5-03 fix: finding descriptions are wrapped in XML boundary tags
    to prevent prompt injection from adversarial finding content.
    """
    files_list = "\n".join(f"  - {p}" for p in source_paths)
    # C5-03: wrap each finding description in XML boundary tags
    findings_block = "\n".join(
        f"  [{tf.finding.finding_id}] severity={tf.finding.severity:.2f} "
        f"type={tf.claim_type.value}: "
        f"<finding_description>{tf.finding.description}</finding_description>"
        for tf in findings
    )

    return (
        "You are an investigator. Your output will be mechanically verified.\n"
        "Do NOT state opinions or verdicts. Report ONLY what you observe.\n\n"
        "For each finding below:\n"
        "1. Read the source file(s) to locate the code the finding describes.\n"
        "2. For each piece of evidence, record:\n"
        "   - file: the absolute path you read\n"
        "   - line: the exact line number\n"
        "   - code_snippet: copy-paste the actual code at that line "
        "(1-5 lines, verbatim)\n"
        "   - observation: what this code does relative to the finding's claim\n"
        "3. Set claim_type to one of: bug_exists, bug_absent, code_missing, "
        "code_present, logic_error, no_error\n\n"
        "Do NOT paraphrase code. Copy it exactly.\n"
        "Do NOT add verdicts like CONFIRMED or REJECTED.\n"
        "Your evidence will be verified against the actual files.\n\n"
        f"Source files:\n{files_list}\n\n"
        f"Findings to investigate:\n{findings_block}\n\n"
        "Output format: a single JSON object matching the schema, with a "
        "'verdicts' array containing one entry per finding.\n"
    )


def _verify_ct_claim(
    evidence: Dict[str, Any],
    allowed_dirs: Optional[List[str]] = None,
) -> Tuple[bool, float, str]:
    """Mechanically verify a single CT evidence item against the real file.

    Reads the cited file at the cited line and checks whether the
    code_snippet actually appears there. This is the structural
    enforcement — the agent's claim is tested against reality.

    C5-01 fix: constrain file reads to allowed_dirs (source_paths parents).
    C5-02 fix: guard against empty string substring bypass.

    Returns:
        (verified, confidence, reason)
        - verified: True if snippet matches code at cited location
        - confidence: 1.0 if exact match, 0.5 if fuzzy, 0.0 if mismatch
        - reason: explanation of verification result
    """
    file_path = evidence.get("file", "")
    line_num = evidence.get("line", 0)
    snippet = evidence.get("code_snippet", "").strip()

    # MF-15 fix: use explicit None/empty checks instead of falsy
    if file_path is None or file_path == "" or line_num is None or line_num == 0 or snippet is None or snippet == "":
        return False, 0.0, "Missing file, line, or code_snippet"

    # C5-01: path traversal protection — resolve to real path, check containment
    real_path = os.path.realpath(file_path)
    if allowed_dirs:
        in_allowed = any(
            real_path.startswith(os.path.realpath(d) + os.sep) or real_path == os.path.realpath(d)
            for d in allowed_dirs
        )
        if not in_allowed:
            return False, 0.0, "Path outside allowed source directories"

    if not os.path.isfile(real_path):
        return False, 0.0, f"File does not exist: {file_path}"

    # C5-23 fix: bounded line streaming to prevent OOM
    try:
        lines: list = []
        with open(real_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 50000:
                    break
                lines.append(line)
    except (OSError, UnicodeDecodeError) as e:
        return False, 0.0, f"Cannot read file: {e}"

    if line_num < 1 or line_num > len(lines):
        return False, 0.0, f"Line {line_num} out of range (file has {len(lines)} lines)"

    # Extract a window around the cited line (±2 lines for fuzzy matching)
    start = max(0, line_num - 3)
    end = min(len(lines), line_num + 2)
    window = "".join(lines[start:end])
    actual_line = lines[line_num - 1].strip()

    # Normalise whitespace for comparison
    snippet_normalised = " ".join(snippet.split())
    actual_normalised = " ".join(actual_line.split())
    window_normalised = " ".join(window.split())

    # C5-02 fix: guard against empty string substring bypass
    # (empty string is a substring of everything)
    if not snippet_normalised or not actual_normalised:
        return False, 0.0, "Empty snippet or empty actual line after normalisation"

    # Exact line match
    if snippet_normalised in actual_normalised or actual_normalised in snippet_normalised:
        return True, 1.0, f"Exact match at line {line_num}"

    # Check if snippet appears anywhere in the ±2 line window
    if snippet_normalised and snippet_normalised in window_normalised:
        return True, 0.8, f"Snippet found within ±2 lines of line {line_num}"

    # Check if first significant token of snippet appears in window
    # (handles minor copy-paste differences)
    # MF-38 fix: require at least 3 significant tokens to prevent trivial matches
    snippet_tokens = [t for t in snippet_normalised.split() if len(t) > 3]
    if len(snippet_tokens) >= 3:
        matches = sum(1 for t in snippet_tokens if t in window_normalised)
        token_ratio = matches / len(snippet_tokens)
        if token_ratio >= 0.6:
            return True, 0.5, (
                f"Partial match ({matches}/{len(snippet_tokens)} tokens) "
                f"near line {line_num}"
            )

    return False, 0.0, (
        f"Snippet does not match code at line {line_num}. "
        f"Cited: '{snippet_normalised[:80]}...' "
        f"Actual: '{actual_normalised[:80]}...'"
    )


def _ct_evidence_to_verdict(
    finding_id: str,
    claim_type: str,
    evidence_items: List[Dict[str, Any]],
    allowed_dirs: Optional[List[str]] = None,
) -> CellVerdict:
    """Convert mechanically-verified CT evidence into a verdict.

    The verdict is determined by the VERIFICATION RESULTS, not by
    the agent's stated claim_type. The agent says "bug_exists" but
    if none of its evidence checks out, the verdict is UNCERTAIN.

    Rules:
        - All evidence verified + claim_type in (bug_exists, logic_error,
          code_missing) → CONFIRMED (the finding is probably real)
        - All evidence verified + claim_type in (bug_absent, no_error,
          code_present) → REJECTED (the finding is probably false)
        - Mixed or no evidence verified → UNCERTAIN
        - No evidence at all → UNCERTAIN
    """
    if not evidence_items:
        return CellVerdict(
            cell_type=CellType.CYTOTOXIC_T,
            finding_id=finding_id,
            verdict="UNCERTAIN",
            confidence=0.0,
            evidence="CT agent provided no evidence",
            tool_used="ct_mechanical",
        )

    verifications = []
    for ev in evidence_items:
        verified, conf, reason = _verify_ct_claim(ev, allowed_dirs=allowed_dirs)
        verifications.append((verified, conf, reason))

    verified_count = sum(1 for v, _, _ in verifications if v)
    total = len(verifications)
    avg_confidence = sum(c for _, c, _ in verifications) / max(total, 1)

    # Build evidence summary from verification results
    evidence_summary = "; ".join(
        f"[{'PASS' if v else 'FAIL'} {c:.1f}] {r}"
        for v, c, r in verifications
    )

    # Determine verdict from verified evidence + structural claim type
    FINDING_SUPPORTS = {"bug_exists", "logic_error", "code_missing"}
    FINDING_REFUTES = {"bug_absent", "no_error", "code_present"}

    if verified_count == 0:
        # No evidence checks out — agent hallucinated or was wrong
        return CellVerdict(
            cell_type=CellType.CYTOTOXIC_T,
            finding_id=finding_id,
            verdict="UNCERTAIN",
            confidence=0.0,
            evidence=f"0/{total} evidence items verified. {evidence_summary}",
            tool_used="ct_mechanical",
        )

    verification_rate = verified_count / total

    if verification_rate >= 0.5 and claim_type in FINDING_SUPPORTS:
        return CellVerdict(
            cell_type=CellType.CYTOTOXIC_T,
            finding_id=finding_id,
            verdict="CONFIRMED",
            confidence=round(avg_confidence * verification_rate, 3),
            evidence=f"{verified_count}/{total} verified. {evidence_summary}",
            tool_used="ct_mechanical",
        )
    elif verification_rate >= 0.5 and claim_type in FINDING_REFUTES:
        return CellVerdict(
            cell_type=CellType.CYTOTOXIC_T,
            finding_id=finding_id,
            verdict="REJECTED",
            confidence=round(avg_confidence * verification_rate, 3),
            evidence=f"{verified_count}/{total} verified. {evidence_summary}",
            tool_used="ct_mechanical",
        )
    else:
        return CellVerdict(
            cell_type=CellType.CYTOTOXIC_T,
            finding_id=finding_id,
            verdict="UNCERTAIN",
            confidence=round(avg_confidence * verification_rate, 3),
            evidence=f"{verified_count}/{total} verified. {evidence_summary}",
            tool_used="ct_mechanical",
        )


def cytotoxic_t_cell(
    triaged: List[TriagedFinding],
    source_paths: List[str],
    timeout: int = 180,
) -> List[CellVerdict]:
    """Stage 2a: Structurally-enforced code investigation via claude CLI.

    The CT agent is an INVESTIGATOR, not a judge:
    1. Schema enforcement forces structured evidence output
    2. Each evidence item cites file:line:code_snippet
    3. _verify_ct_claim() mechanically checks each citation
    4. Verdict is computed from verification results, not agent opinion

    If the agent's citations don't match the actual code, confidence
    drops to zero regardless of what the agent claimed.
    """
    code_findings = [
        tf for tf in triaged
        if tf.claim_type in (ClaimType.CODE_BEHAVIORAL, ClaimType.CODE_STRUCTURAL)
        and not tf.is_duplicate
    ]

    if not code_findings:
        return []

    if not _get_claude_cli():
        return [
            CellVerdict(
                cell_type=CellType.CYTOTOXIC_T,
                finding_id=tf.finding.finding_id,
                verdict="UNCERTAIN",
                confidence=0.0,
                evidence="claude CLI not available",
                tool_used="none",
            )
            for tf in code_findings
        ]

    prompt = _build_ct_prompt(code_findings, source_paths)
    t0 = time.monotonic()

    try:
        cmd = [
            _get_claude_cli(), "-p", prompt,
            "--allowedTools", "Read,Grep,Glob",
            "--max-turns", "4",
        ]
        # Enforce output schema if available
        if _CT_SCHEMA_PATH.exists():
            cmd.extend(["--output-format", "json"])

        # Bug#4 fix: serialise claude CLI calls to prevent contention
        with _CLAUDE_CLI_LOCK:
            result = sp.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.monotonic() - t0
        output = result.stdout.strip()

        # Parse the structured response
        raw_verdicts = _parse_ct_output(output)

        # Mechanically verify each evidence item
        verdicts: List[CellVerdict] = []
        seen: Set[str] = set()
        for rv in raw_verdicts:
            fid = rv.get("finding_id", "")
            if not fid or fid in seen:
                continue
            seen.add(fid)

            # C5-01: pass source_paths as allowed_dirs for path traversal protection
            # Bug#5 fix: filter empty strings from dirname (bare filenames)
            allowed_dirs = [d for d in (os.path.dirname(os.path.abspath(p)) for p in source_paths) if d] if source_paths else None
            verdict = _ct_evidence_to_verdict(
                finding_id=fid,
                claim_type=rv.get("claim_type", ""),
                evidence_items=rv.get("evidence", []),
                allowed_dirs=allowed_dirs,
            )
            verdict.elapsed_s = elapsed
            verdicts.append(verdict)

        # Fill in findings the agent didn't investigate
        for tf in code_findings:
            if tf.finding.finding_id not in seen:
                verdicts.append(CellVerdict(
                    cell_type=CellType.CYTOTOXIC_T,
                    finding_id=tf.finding.finding_id,
                    verdict="UNCERTAIN",
                    confidence=0.0,
                    evidence="CT agent did not investigate this finding",
                    tool_used="ct_mechanical",
                    elapsed_s=elapsed,
                ))

        return verdicts

    except sp.TimeoutExpired:
        return [
            CellVerdict(
                cell_type=CellType.CYTOTOXIC_T,
                finding_id=tf.finding.finding_id,
                verdict="UNCERTAIN",
                confidence=0.0,
                evidence=f"CT agent timeout ({timeout}s)",
                tool_used="ct_mechanical",
                elapsed_s=timeout,
            )
            for tf in code_findings
        ]
    except Exception as e:
        return [
            CellVerdict(
                cell_type=CellType.CYTOTOXIC_T,
                finding_id=tf.finding.finding_id,
                verdict="UNCERTAIN",
                confidence=0.0,
                evidence=f"CT agent error: {e}",
                tool_used="ct_mechanical",
            )
            for tf in code_findings
        ]


def _parse_ct_output(output: str) -> List[Dict[str, Any]]:
    """Parse CT agent output, handling both schema-enforced JSON and fallback.

    Tries four parsing strategies:
    1. Full JSON object with "verdicts" array (schema-enforced)
    1b. C5-05 fix: extract JSON from markdown code blocks (```json...```)
    2. JSON lines (one object per line, legacy format)
    3. Extract JSON from mixed text (agent didn't follow schema perfectly)
    """
    # Strategy 1: Full JSON with verdicts array
    try:
        data = json.loads(output)
        if isinstance(data, dict) and "verdicts" in data:
            return data["verdicts"]
    except json.JSONDecodeError:
        pass

    # Strategy 1b (C5-05 fix): extract JSON from markdown code blocks
    code_block_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', output, re.DOTALL)
    if code_block_match:
        try:
            data = json.loads(code_block_match.group(1))
            if isinstance(data, dict) and "verdicts" in data:
                return data["verdicts"]
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # Strategy 2: JSON lines
    results = []
    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
            if "finding_id" in obj:
                results.append(obj)
        except json.JSONDecodeError:
            continue
    if results:
        return results

    # Strategy 3: Find JSON objects in mixed text
    json_pattern = re.compile(r'\{[^{}]*"finding_id"[^{}]*\}', re.DOTALL)
    for match in json_pattern.finditer(output):
        try:
            obj = json.loads(match.group())
            results.append(obj)
        except json.JSONDecodeError:
            continue

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# 3. B-CELL — Mathematical/Logical verification (SymPy + z3 + statsmodels)
# ═══════════════════════════════════════════════════════════════════════════════

def _run_tool_subprocess(code: str, timeout: int = 15) -> str:
    """Run Python code in a subprocess using the tools-equipped interpreter.

    MF-22 fix: check returncode and capture stderr. Silent error swallowing
    previously masked subprocess failures (e.g. segfaults, import errors).
    """
    try:
        result = sp.run(
            [_get_python_tools(), "-c", code],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            stderr_msg = result.stderr.strip()[:200] if result.stderr else "unknown"
            return f"SUBPROCESS_ERROR(rc={result.returncode}): {stderr_msg}"
        return result.stdout.strip()
    except sp.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"


def _verify_sympy(claim: str) -> CellVerdict:
    """Verify a mathematical claim via SymPy.

    MF-40 fix: AST blocklist rejects dangerous tokens before parse_expr.
    MF-23 fix: removed n=100 numeric fallback (proof-by-example fallacy).
    """
    code = f"""
import sympy
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

claim = {repr(claim)}

# MF-40: AST blocklist — reject claims containing dangerous tokens (RCE vector)
_BLOCKLIST = re.compile(r'(?:__|import|eval|exec|getattr|setattr|delattr|globals|locals|compile|open|__class__|__subclasses__)')
if _BLOCKLIST.search(claim):
    print("BLOCKED: claim contains disallowed token")
else:
    try:
        expr = parse_expr(claim,
            transformations=(standard_transformations + (implicit_multiplication_application,)),
            # MF-30 fix: auto-generate symbols from claim instead of hardcoded 'n'
            local_dict={{
                'pi': sympy.pi, 'E': sympy.E, 'oo': sympy.oo,
                'sqrt': sympy.sqrt, 'cos': sympy.cos, 'sin': sympy.sin,
                'Eq': sympy.Eq, 'Gt': sympy.Gt, 'Lt': sympy.Lt,
                'Ge': sympy.Ge, 'Le': sympy.Le, 'And': sympy.And,
                **{{s: symbols(s) for s in set(re.findall(r'\\b([a-z][a-z0-9_]*)\\b', claim)) if s not in ('e', 'pi', 'oo', 'sqrt', 'cos', 'sin', 'log', 'exp')}}
            }},
            global_dict={{'__builtins__': {{}}}})
        result = sympy.simplify(expr)
        if result == True:
            print("VERIFIED_TRUE")
        elif result == False:
            print("VERIFIED_FALSE")
        else:
            # MF-23: emit UNCERTAIN instead of n=100 numeric fallback
            print(f"SIMPLIFIED: {{result}}")
    except Exception as e:
        print(f"UNVERIFIABLE: {{e}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    # MF-24 fix: exact match prevents substring injection
    # MF-23 fix: NUMERICAL_TRUE/FALSE removed (no more n=100 fallback)
    stripped = output.strip()
    if stripped == "VERIFIED_TRUE":
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.95, evidence=f"SymPy: {output}", tool_used="sympy",
            elapsed_s=elapsed,
        )
    elif stripped == "VERIFIED_FALSE":
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.95, evidence=f"SymPy: {output}", tool_used="sympy",
            elapsed_s=elapsed,
        )
    elif stripped.startswith("BLOCKED:"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.0, evidence=f"SymPy: {output} (MF-40 blocklist)",
            tool_used="sympy", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.3, evidence=f"SymPy: {output}", tool_used="sympy",
            elapsed_s=elapsed,
        )


def _verify_z3(claim: str) -> CellVerdict:
    """Verify a logical invariant claim via z3-solver.

    Attempts to express the claim as a z3 constraint and check
    satisfiability. Useful for if/then invariants, reachability,
    and constraint satisfaction claims.
    """
    code = f"""
import z3
import re

claim = {repr(claim)}

# Try to extract a simple logical structure:
# "if X then Y" -> check if NOT(X implies Y) is unsatisfiable
if_then = re.search(r'if\\s+(.+?)\\s+then\\s+(.+)', claim, re.IGNORECASE)
if if_then:
    # Bug#9 fix: abstract booleans cannot meaningfully encode the actual
    # predicates — return UNCERTAIN instead of false positive/negative
    print("Z3_UNSTRUCTURED: if/then claim requires grounded predicates")
else:
    # Try numeric constraint extraction
    # MF-26 fix: support scientific notation (e.g. 1.5e-3)
    nums = re.findall(r'[-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?', claim)
    if len(nums) >= 2:
        a, b = float(nums[0]), float(nums[1])
        x = z3.Real('x')
        s = z3.Solver()
        if '>=' in claim or 'greater than or equal' in claim.lower():
            s.add(z3.Not(x >= b))
            s.add(x == a)
            result = s.check()
            if result == z3.unsat:
                print(f"VERIFIED_TRUE: {{a}} >= {{b}}")
            else:
                print(f"VERIFIED_FALSE: {{a}} < {{b}}")
        elif '<=' in claim or 'less than or equal' in claim.lower():
            s.add(z3.Not(x <= b))
            s.add(x == a)
            result = s.check()
            if result == z3.unsat:
                print(f"VERIFIED_TRUE: {{a}} <= {{b}}")
            else:
                print(f"VERIFIED_FALSE: {{a}} > {{b}}")
        else:
            print(f"Z3_PARSED: extracted {{len(nums)}} numeric values")
    elif len(nums) == 1:
        # MF-27 fix: handle single-bound comparisons (e.g. "x > 0")
        a = float(nums[0])
        x = z3.Real('x')
        s = z3.Solver()
        if '>' in claim and '>=' not in claim:
            s.add(z3.Not(x > a))
            print(f"Z3_SINGLE_BOUND: x > {{a}}")
        elif '<' in claim and '<=' not in claim:
            s.add(z3.Not(x < a))
            print(f"Z3_SINGLE_BOUND: x < {{a}}")
        elif '>=' in claim:
            s.add(z3.Not(x >= a))
            print(f"Z3_SINGLE_BOUND: x >= {{a}}")
        elif '<=' in claim:
            s.add(z3.Not(x <= a))
            print(f"Z3_SINGLE_BOUND: x <= {{a}}")
        else:
            print(f"Z3_SINGLE_VALUE: {{a}}")
    else:
        print("Z3_UNSTRUCTURED: claim not parseable as constraint")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    # MF-24 fix: use startswith instead of substring 'in' to prevent injection
    stripped = output.strip()
    if stripped.startswith("VERIFIED_TRUE") or stripped == "UNSAT_VALID":
        # Run 11: confidence downgraded from 0.90 to 0.30. z3 proofs use
        # abstract symbols with no code grounding — they prove properties of
        # the LLM's translation, not the actual runtime constraints. Full fix
        # (AST-grounded SMT-LIB encoding) deferred to Run 12.
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.30, evidence=f"z3: {output}", tool_used="z3",
            elapsed_s=elapsed,
        )
    elif stripped.startswith("VERIFIED_FALSE") or stripped == "SATISFIABLE_COUNTEREXAMPLE":
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.30, evidence=f"z3: {output}", tool_used="z3",
            elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"z3: {output}", tool_used="z3",
            elapsed_s=elapsed,
        )


def _verify_statistical(claim: str) -> CellVerdict:
    """Verify a statistical claim via statsmodels/scipy.

    Checks claims about significance, distributions, correlations.
    """
    code = f"""
import re
claim = {repr(claim)}

# Extract p-value claims
# MF-31 fix: match p-values with or without leading zero
p_match = re.search(r'p\\s*[<=]\\s*(0?\\.\\d+)', claim)
if p_match:
    p_val = float(p_match.group(1))
    alpha = 0.05
    if p_val < alpha:
        print(f"STAT_SIGNIFICANT: p={{p_val}} < alpha={{alpha}}")
    else:
        print(f"STAT_NOT_SIGNIFICANT: p={{p_val}} >= alpha={{alpha}}")
else:
    # Check for correlation claims
    r_match = re.search(r'r\\s*=\\s*([-+]?0?\\.\\d+)', claim)
    if r_match:
        r_val = float(r_match.group(1))
        if abs(r_val) > 0.7:
            print(f"STRONG_CORRELATION: r={{r_val}}")
        elif abs(r_val) > 0.3:
            print(f"MODERATE_CORRELATION: r={{r_val}}")
        else:
            print(f"WEAK_CORRELATION: r={{r_val}}")
    else:
        # Bug#72 fix: handle confidence interval claims
        ci_match = re.search(r'(?:CI|confidence\\s+interval)\\s*[=:]?\\s*\\[?([-+]?\\d+\\.?\\d*)\\s*[,;-]\\s*([-+]?\\d+\\.?\\d*)\\]?', claim, re.IGNORECASE)
        if ci_match:
            lo, hi = float(ci_match.group(1)), float(ci_match.group(2))
            if lo < hi:
                print(f"STAT_CI_VALID: CI=[{{lo}}, {{hi}}]")
            else:
                print(f"STAT_CI_INVALID: CI bounds inverted [{{lo}}, {{hi}}]")
        else:
            # Handle mean/median comparison claims
            mean_match = re.search(r'(?:mean|median|average)\\s*[=:]?\\s*([-+]?\\d+\\.?\\d*)', claim, re.IGNORECASE)
            if mean_match:
                val = float(mean_match.group(1))
                print(f"STAT_MEAN: value={{val}}")
            else:
                print("STAT_UNPARSEABLE: no testable statistical claim extracted")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    # MF-29 fix: also match STRONG_CORRELATION and MODERATE_CORRELATION
    stripped_stat = output.strip()
    # Bug#72 fix: also match CI and mean claim types
    if (("SIGNIFICANT" in stripped_stat and "NOT_SIGNIFICANT" not in stripped_stat)
            or stripped_stat.startswith("STRONG_CORRELATION")
            or stripped_stat.startswith("MODERATE_CORRELATION")
            or stripped_stat.startswith("STAT_CI_VALID")
            or stripped_stat.startswith("STAT_MEAN")):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.80, evidence=f"stats: {output}", tool_used="statsmodels",
            elapsed_s=elapsed,
        )
    elif ("NOT_SIGNIFICANT" in stripped_stat
            or stripped_stat.startswith("WEAK_CORRELATION")
            or stripped_stat.startswith("STAT_CI_INVALID")):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.80, evidence=f"stats: {output}", tool_used="statsmodels",
            elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"stats: {output}", tool_used="statsmodels",
            elapsed_s=elapsed,
        )


def b_cell_verify(triaged: List[TriagedFinding]) -> List[CellVerdict]:
    """Stage 2b: Mathematical/logical/statistical verification.

    The B-Cell uses somatic hypermutation — it adapts its verification
    strategy based on the claim type. Mathematical claims get SymPy,
    logical claims get z3, statistical claims get statsmodels.
    Cross-verification (class switching): if SymPy returns UNCERTAIN,
    try z3 as a fallback.
    """
    verdicts: List[CellVerdict] = []

    for tf in triaged:
        if tf.is_duplicate:
            continue

        fid = tf.finding.finding_id
        v: Optional[CellVerdict] = None

        if tf.claim_type == ClaimType.MATHEMATICAL:
            v = _verify_sympy(tf.extracted_claim)
            # Class switching: if SymPy uncertain, try z3
            if v.verdict == "UNCERTAIN":
                v2 = _verify_z3(tf.extracted_claim)
                if v2.verdict != "UNCERTAIN":
                    v = v2
                    v.evidence += " [class-switched from SymPy]"

        elif tf.claim_type == ClaimType.LOGICAL:
            v = _verify_z3(tf.extracted_claim)

        elif tf.claim_type == ClaimType.STATISTICAL:
            v = _verify_statistical(tf.extracted_claim)

        if v is not None:
            v.finding_id = fid
            verdicts.append(v)

    return verdicts


# ═══════════════════════════════════════════════════════════════════════════════
# 4. NK CELL — Pattern recognition, dedup, and immune memory
# ═══════════════════════════════════════════════════════════════════════════════

# Known false-positive patterns from Run 7b analysis
# MF-18 fix: add re.DOTALL to FP patterns for multiline descriptions
_KNOWN_FALSE_POSITIVES: List[Dict[str, Any]] = [
    {
        "pattern": re.compile(r"@dataclass\s+decorator.*missing", re.IGNORECASE | re.DOTALL),
        "source": "Run 7b: Codex hallucinated missing @dataclass 8 times",
        "expected_model": "Codex",
    },
    {
        "pattern": re.compile(r"missing\s+@dataclass", re.IGNORECASE | re.DOTALL),
        "source": "Run 7b: @dataclass false positive cluster",
        "expected_model": "Codex",
    },
]


def nk_cell_verify(
    triaged: List[TriagedFinding],
    prior_findings: List[Finding],
    tau_sim: float = 0.50,  # Raised from 0.33: class_match base (0.30) + shared
                            # vocabulary caused 90-100% false DUPLICATE by mid-run.
                            # At 0.50, same-class needs Jaccard >= 0.286 (real overlap).
    false_positive_db: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[List[TriagedFinding], List[CellVerdict]]:
    """Stage 2c: Pattern recognition and deduplication.

    The NK Cell provides innate-like immunity with adaptive memory.
    It matches findings against:
    1. Prior findings (dedup via similarity)
    2. Known false-positive patterns (memory from prior runs)
    3. Anomaly detection (severity outliers, repeated hallucinations)

    Returns updated triaged findings with duplicate flags set,
    plus verdicts for pattern-matched findings.
    """
    fp_db = false_positive_db or _KNOWN_FALSE_POSITIVES
    verdicts: List[CellVerdict] = []

    for tf in triaged:
        f = tf.finding

        # 1. Dedup against prior findings
        # MF-19 fix: early termination once a match exceeds threshold
        best_sim = 0.0
        best_match: Optional[str] = None
        for pf in prior_findings:
            sim = _finding_similarity(f, pf)
            if sim > best_sim:
                best_sim = sim
                best_match = pf.finding_id
                if best_sim >= tau_sim:
                    break  # MF-19: early termination

        # MF-16 fix: assert best_match is not None (prevent phantom duplicates)
        if best_sim >= tau_sim and best_match is not None:
            # Bug-closed gate (v1 parity with v2): if matched finding
            # already has a programmatically verified fix, this bug is closed.
            matched_pf = next(
                (pf for pf in prior_findings if pf.finding_id == best_match),
                None,
            )
            has_fix = (
                matched_pf is not None
                and bool(matched_pf.proposed_fix.strip())
                and matched_pf.verified
            )
            is_escalated = (
                matched_pf is not None
                and matched_pf.escalated
            )
            tf.is_duplicate = True
            tf.duplicate_of = best_match
            tf.similarity = best_sim
            if has_fix:
                _evidence = f"Bug CLOSED — dup of {best_match} (sim={best_sim:.3f}), fix exists"
                _tool = "bug_closed"
            elif is_escalated:
                _evidence = f"Bug ESCALATED — dup of {best_match} (sim={best_sim:.3f}), awaiting HIL"
                _tool = "escalated"
            else:
                _evidence = f"Duplicate of {best_match} (sim={best_sim:.3f})"
                _tool = "similarity_dedup"
            verdicts.append(CellVerdict(
                cell_type=CellType.NK_CELL,
                finding_id=f.finding_id,
                verdict="DUPLICATE",
                confidence=best_sim,
                evidence=_evidence,
                tool_used=_tool,
            ))
            continue

        # 2. Check against known false-positive patterns
        # Bug#10 fix: track FP match to skip anomaly detection (v1 control flow leak)
        is_fp = False
        for fp in fp_db:
            if fp["pattern"].search(f.description):
                model_match = (
                    not fp.get("expected_model")
                    or fp["expected_model"] == f.model_id
                )
                if model_match:
                    verdicts.append(CellVerdict(
                        cell_type=CellType.NK_CELL,
                        finding_id=f.finding_id,
                        verdict="REJECTED",
                        confidence=0.90,
                        evidence=f"Known FP: {fp['source']}",
                        tool_used="false_positive_db",
                    ))
                    is_fp = True
                    break

        if is_fp:
            continue  # Bug#10 fix: skip anomaly detection for known FPs

        # 3. Anomaly detection: severity outliers
        # MF-17 fix: emit REJECTED (not UNCERTAIN) for anomalous findings
        if f.severity > 0.95 and f.round_idx > 5:
            verdicts.append(CellVerdict(
                cell_type=CellType.NK_CELL,
                finding_id=f.finding_id,
                verdict="REJECTED",
                confidence=0.6,
                evidence=f"Late-round high severity ({f.severity:.2f} at R{f.round_idx}) — possible inflation",
                tool_used="anomaly_detection",
            ))

    return triaged, verdicts


# ═══════════════════════════════════════════════════════════════════════════════
# 5. HELPER T-CELL — Verdict synthesis
# ═══════════════════════════════════════════════════════════════════════════════

def helper_t_cell_synthesize(
    triaged: List[TriagedFinding],
    all_verdicts: List[CellVerdict],
) -> Tuple[Dict[str, str], Dict[str, float]]:
    """Stage 3a: Synthesize all cell verdicts into final judgments.

    The Helper T-Cell coordinates the immune response by aggregating
    verdicts from all cell types. Uses confidence-weighted voting:
    - CONFIRMED verdicts contribute positive weight
    - REJECTED verdicts contribute negative weight
    - UNCERTAIN verdicts contribute nothing
    - DUPLICATE verdicts are auto-rejected

    A finding needs net positive confidence to survive.
    Asymmetric threshold: rejection requires 0.6+ net confidence,
    confirmation requires only 0.4+ (false negatives are costlier
    than false positives).
    """
    # Group verdicts by finding — MF-11 fix: deduplicate by cell type
    # (keep highest-confidence verdict per cell type per finding)
    verdicts_by_finding: Dict[str, List[CellVerdict]] = {}
    for v in all_verdicts:
        verdicts_by_finding.setdefault(v.finding_id, []).append(v)

    # Deduplicate: one verdict per cell type per finding
    for fid in verdicts_by_finding:
        seen_cells: Dict[CellType, CellVerdict] = {}
        for v in verdicts_by_finding[fid]:
            if v.cell_type not in seen_cells or v.confidence > seen_cells[v.cell_type].confidence:
                seen_cells[v.cell_type] = v
        verdicts_by_finding[fid] = list(seen_cells.values())

    final_verdicts: Dict[str, str] = {}
    final_confidences: Dict[str, float] = {}

    for tf in triaged:
        fid = tf.finding.finding_id
        fv = verdicts_by_finding.get(fid, [])

        # Auto-reject duplicates
        if tf.is_duplicate:
            final_verdicts[fid] = "DUPLICATE"
            final_confidences[fid] = tf.similarity
            continue

        # Confidence-weighted voting
        confirm_weight = 0.0
        reject_weight = 0.0

        for v in fv:
            if v.verdict == "CONFIRMED":
                confirm_weight += v.confidence
            elif v.verdict == "REJECTED":
                reject_weight += v.confidence
            elif v.verdict == "DUPLICATE":
                reject_weight += v.confidence
            # UNCERTAIN contributes nothing

        total = confirm_weight + reject_weight
        if total == 0:
            # No verdicts — pass through (precautionary principle)
            final_verdicts[fid] = "UNCERTAIN"
            final_confidences[fid] = 0.0
        elif reject_weight / max(total, 0.001) >= 0.6:
            final_verdicts[fid] = "REJECTED"
            # MF-09 fix: cap confidence by max individual verdict weight
            max_individual = max((v.confidence for v in fv if v.verdict in ("REJECTED", "DUPLICATE")), default=0.0)
            final_confidences[fid] = min(reject_weight / total, max_individual)
        elif confirm_weight / max(total, 0.001) >= 0.4:
            final_verdicts[fid] = "CONFIRMED"
            # MF-09 fix: cap confidence by max individual verdict weight
            max_individual = max((v.confidence for v in fv if v.verdict == "CONFIRMED"), default=0.0)
            final_confidences[fid] = min(confirm_weight / total, max_individual)
        else:
            final_verdicts[fid] = "UNCERTAIN"
            final_confidences[fid] = max(confirm_weight, reject_weight) / max(total, 0.001)

    return final_verdicts, final_confidences


# ═══════════════════════════════════════════════════════════════════════════════
# 6. REGULATORY T-CELL — Meta-verification and autoimmune prevention
# ═══════════════════════════════════════════════════════════════════════════════

def regulatory_t_cell_check(
    final_verdicts: Dict[str, str],
    triaged: List[TriagedFinding],
    max_rejection_rate: float = 0.65,
    min_findings_for_check: int = 5,
) -> Tuple[bool, str]:
    """Stage 3b: Check for autoimmune response (over-rejection).

    The Regulatory T-Cell prevents the immune system from attacking
    valid findings. If the rejection rate exceeds the threshold,
    it flags an autoimmune condition — the verification pipeline
    itself may be miscalibrated.

    Returns:
        (autoimmune_flag, reason)
    """
    total = len(final_verdicts)
    if total < min_findings_for_check:
        return False, f"Too few findings ({total}) for meta-check"

    rejected = sum(1 for v in final_verdicts.values() if v == "REJECTED")
    duplicated = sum(1 for v in final_verdicts.values() if v == "DUPLICATE")
    removed = rejected + duplicated
    removal_rate = removed / total

    reasons = []

    # Check 1: Overall rejection rate
    if rejected / total > max_rejection_rate:
        reasons.append(
            f"Rejection rate {rejected}/{total} ({rejected/total:.1%}) "
            f"exceeds threshold ({max_rejection_rate:.0%})"
        )

    # Check 1b (MF-36 fix): High UNCERTAIN rate indicates fail-open illusion
    uncertain = sum(1 for v in final_verdicts.values() if v == "UNCERTAIN")
    uncertain_rate = uncertain / total
    if uncertain_rate > 0.30:
        reasons.append(
            f"UNCERTAIN rate {uncertain}/{total} ({uncertain_rate:.1%}) "
            f"exceeds 30% — verification tools may be non-functional (fail-open)"
        )

    # Check 2: Single cell type dominating rejections
    # (indicates a miscalibrated tool, not genuine false positives)
    # We'd need per-cell rejection counts here — tracked via verdicts

    # Check 3: All findings from one model rejected
    model_counts: Dict[str, int] = {}
    model_rejected: Dict[str, int] = {}
    for tf in triaged:
        mid = tf.finding.model_id
        model_counts[mid] = model_counts.get(mid, 0) + 1
        if final_verdicts.get(tf.finding.finding_id) == "REJECTED":
            model_rejected[mid] = model_rejected.get(mid, 0) + 1

    for mid, total_m in model_counts.items():
        rej_m = model_rejected.get(mid, 0)
        if total_m >= 3 and rej_m == total_m:
            reasons.append(
                f"All {total_m} findings from {mid} rejected — "
                f"possible systematic bias against this model"
            )

    if reasons:
        return True, "; ".join(reasons)

    return False, f"Pipeline healthy: {removal_rate:.1%} removal rate"


# ═══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR — Run the full immune pipeline
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# V2 IMMUNE COMPONENTS (activated WP6a, Exp 29)
#
# These implement architectural improvements from the Gemini CDSFL
# conversation (3 April 2026). All v2 components are now active in the
# pipeline. DC v2, NK v2, Reg T v2 are PRIMARY. CT v2, B-Cell v2 run
# in parallel with v1. Shadow logging captures v1-vs-v2 comparison data.
# ═══════════════════════════════════════════════════════════════════════════════

import logging as _logging
import threading as _threading

# Bug#4 fix: serialise claude CLI calls to prevent contention
_CLAUDE_CLI_LOCK = _threading.Lock()

_shadow_log = _logging.getLogger("immune.shadow")

# Configure shadow logger to write to file if not already configured.
# This ensures v1-vs-v2 comparison data, formalisation agent output,
# and typed LLM classifier results are persisted for analysis.
if not _shadow_log.handlers:
    _shadow_log.setLevel(_logging.INFO)
    import os as _os
    # Bug#20 fix: removed dead first assignment
    _shadow_log_dir = _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "logs"
    )
    _os.makedirs(_shadow_log_dir, exist_ok=True)
    _shadow_fh = _logging.FileHandler(
        _os.path.join(_shadow_log_dir, "immune_shadow.log"),
        encoding="utf-8",
    )
    _shadow_fh.setLevel(_logging.INFO)
    _shadow_fh.setFormatter(_logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"
    ))
    _shadow_log.addHandler(_shadow_fh)


# ── 0. SKIN BARRIER — deterministic pre-filter ───────────────────────────────
#
# Runs BEFORE the pipeline. Checks whether a finding's code citations
# actually exist in the source files. A finding that cites code that isn't
# there is likely hallucinated. In active mode, these would be dropped
# before reaching the Dendritic Cell.

@dataclass
class SkinBarrierResult:
    """Result of skin barrier check for a single finding."""
    finding_id: str
    passed: bool
    reason: str
    cited_file: str = ""
    cited_line: int = 0


def skin_barrier_check(
    findings: List[Finding],
    source_paths: List[str],
) -> Tuple[List[Finding], List[SkinBarrierResult]]:
    """Deterministic pre-filter: verify that cited code exists.

    Checks each finding for file:line citations. If the cited code doesn't
    exist at the cited location, the finding fails the barrier.

    In shadow mode (Run 11), all findings pass through regardless.
    The results are logged for observation.

    Returns:
        (all_findings, barrier_results) — findings unchanged in shadow mode
    """
    results: List[SkinBarrierResult] = []
    source_set = set(str(p) for p in source_paths)

    # Also build a set of relative paths and basenames for fuzzy matching
    # Bug#69 fix: track ambiguous basenames (multiple paths for same name)
    source_basenames: Dict[str, str] = {}
    _ambiguous_basenames: Set[str] = set()
    for p in source_paths:
        bn = os.path.basename(str(p))
        if bn in source_basenames:
            _ambiguous_basenames.add(bn)
        source_basenames[bn] = str(p)

    for f in findings:
        desc = f.description

        # Extract file:line citations from the description
        # Common patterns: "file.py:123", "line 123 of file.py",
        # "at line 123", "file.py line 123"
        # Bug#5 fix: match any file extension, not just .py
        citations = re.findall(
            r'(\S+\.\w+)(?::|\s+line\s+)(\d+)', desc
        )
        if not citations:
            # Bug#41 fix: line-only citations cannot be verified without a file path.
            # Pass by default rather than creating unresolvable citations.
            pass

        if not citations:
            # No citations to check — passes by default
            results.append(SkinBarrierResult(
                finding_id=f.finding_id, passed=True,
                reason="No file:line citation to verify",
            ))
            continue

        # Check first citation (most findings cite one location)
        cited_file_raw, cited_line_raw = citations[0]
        cited_line = int(cited_line_raw) if isinstance(cited_line_raw, str) else cited_line_raw

        # Resolve the file path
        cited_file = ""
        if cited_file_raw:
            # Try exact match — E31-16 fix: must be in source_set, not
            # arbitrary filesystem. os.path.isfile() alone creates a
            # file-existence oracle (e.g. /etc/passwd would pass).
            if cited_file_raw in source_set:
                cited_file = cited_file_raw
            # Try basename match (Bug#69: skip if ambiguous)
            elif (os.path.basename(cited_file_raw) in source_basenames
                  and os.path.basename(cited_file_raw) not in _ambiguous_basenames):
                cited_file = source_basenames[os.path.basename(cited_file_raw)]
            # Try partial path match
            else:
                for sp_path in source_paths:
                    if str(sp_path).endswith(cited_file_raw):
                        cited_file = str(sp_path)
                        break

        if not cited_file:
            results.append(SkinBarrierResult(
                finding_id=f.finding_id, passed=False,
                reason=f"Cited file not found: {cited_file_raw}",
                cited_file=cited_file_raw, cited_line=cited_line,
            ))
            continue

        # Check the file exists and the line is in range
        if not os.path.isfile(cited_file):
            results.append(SkinBarrierResult(
                finding_id=f.finding_id, passed=False,
                reason=f"File does not exist: {cited_file}",
                cited_file=cited_file, cited_line=cited_line,
            ))
            continue

        # C5-23 fix: bounded line streaming to prevent OOM on large files
        try:
            lines: List[str] = []
            max_lines = 50000  # configurable limit
            with open(cited_file, "r", encoding="utf-8") as fh:
                for i, line in enumerate(fh):
                    if i >= max_lines:
                        break
                    lines.append(line)
        except (OSError, UnicodeDecodeError):
            results.append(SkinBarrierResult(
                finding_id=f.finding_id, passed=False,
                reason=f"Cannot read file: {cited_file}",
                cited_file=cited_file, cited_line=cited_line,
            ))
            continue

        if cited_line < 1 or cited_line > len(lines):
            results.append(SkinBarrierResult(
                finding_id=f.finding_id, passed=False,
                reason=f"Line {cited_line} out of range (file has {len(lines)} lines)",
                cited_file=cited_file, cited_line=cited_line,
            ))
            continue

        # Line exists — passes barrier
        results.append(SkinBarrierResult(
            finding_id=f.finding_id, passed=True,
            reason=f"Citation verified: {os.path.basename(cited_file)}:{cited_line}",
            cited_file=cited_file, cited_line=cited_line,
        ))

    # Log shadow results
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    _shadow_log.info(
        "Skin barrier (v2): %d passed, %d failed out of %d findings",
        passed, failed, len(findings),
    )
    for r in results:
        if not r.passed:
            _shadow_log.info("  BLOCKED: %s — %s", r.finding_id, r.reason)

    # Shadow mode: return all findings unchanged
    return findings, results


# ── SHADOW Cytotoxic T Cell v2 — falsifier architecture ──────────────────────
#
# The v2 CT Cell shifts from investigator (does the cited code exist?) to
# falsifier (what's the strongest condition that breaks this finding?).
# It uses tertiary verdicts: FALSIFIED / CONTESTED / CORROBORATED.
# The search_manifest is mechanically re-verified.

_CT_V2_FALSIFIER_PROMPT = (
    "You are a DEFENSE ATTORNEY for the codebase. Your job is to find "
    "evidence that DISPROVES each finding. You are not neutral — you are "
    "actively trying to show the finding is wrong.\n\n"
    "For each finding:\n"
    "1. Read the cited code and its surrounding context (±20 lines).\n"
    "2. Search for counter-evidence: cases where the alleged bug is "
    "handled, guarded, or irrelevant.\n"
    "3. Check if the finding's premise is correct (does the code actually "
    "do what the finding claims?).\n"
    "4. Record your search_manifest: every file you read and every grep "
    "you ran, with exact arguments.\n\n"
    "For each finding, produce:\n"
    "  - finding_id: the ID from the input\n"
    "  - verdict: FALSIFIED (you found clear counter-evidence), "
    "CONTESTED (partial counter-evidence or ambiguous), or "
    "CORROBORATED (you tried to disprove it and failed)\n"
    "  - counter_evidence: what you found that argues against the finding\n"
    "  - search_manifest: list of {tool, args, result_summary} for each "
    "search you performed\n"
    "  - test_severity: number of distinct search operations performed "
    "(higher = more thorough test)\n\n"
    "Do NOT simply confirm findings. Your VALUE is in finding what's WRONG "
    "with them. A finding that survives your scrutiny is stronger for it.\n\n"
)


def _build_ct_v2_prompt(
    findings: List[TriagedFinding],
    source_paths: List[str],
) -> str:
    """Build the CT v2 falsifier prompt.

    C5-03 fix: finding descriptions wrapped in XML boundary tags.
    """
    files_list = "\n".join(f"  - {p}" for p in source_paths)
    findings_block = "\n".join(
        f"  [{tf.finding.finding_id}] severity={tf.finding.severity:.2f} "
        f"type={tf.claim_type.value}: "
        f"<finding_description>{tf.finding.description}</finding_description>"
        for tf in findings
    )
    return (
        _CT_V2_FALSIFIER_PROMPT
        + f"Source files available:\n{files_list}\n\n"
        + f"Findings to challenge:\n{findings_block}\n\n"
        + "Output: JSON object with 'verdicts' array.\n"
    )


def _verify_search_manifest(
    manifest: List[Dict[str, Any]],
    source_paths: List[str],
) -> Tuple[int, int, List[str]]:
    """Mechanically verify the CT v2 search manifest.

    Checks that the agent's claimed searches could actually have been
    performed (files exist, grep patterns are valid).

    Returns:
        (verified_count, total_count, issues)
    """
    verified = 0
    issues: List[str] = []
    source_set = set(str(p) for p in source_paths)
    source_basenames = {os.path.basename(str(p)): str(p) for p in source_paths}

    for step in manifest:
        tool = step.get("tool", "")
        args = step.get("args", "")

        if tool in ("Read", "read", "cat"):
            # E31-17 fix: reject non-string args early (dict/list → str
            # produces an unparseable path like "{'path': 'main.py'}")
            if not isinstance(args, str):
                issues.append(f"Non-string args for {tool}: {type(args).__name__}")
                continue
            file_arg = args
            # Try exact, then basename
            exists = (
                os.path.isfile(file_arg)
                or file_arg in source_set
                or os.path.basename(file_arg) in source_basenames
            )
            if exists:
                verified += 1
            else:
                issues.append(f"File not found: {file_arg}")

        elif tool in ("Grep", "grep", "rg"):
            # E31-17 fix: reject non-string args (dict cast to string
            # produces valid regex but meaningless pattern)
            if not isinstance(args, str):
                issues.append(f"Non-string args for {tool}: {type(args).__name__}")
                continue
            # E31-10 fix: also extract target file from step if present
            # and verify it exists. Pattern-only syntactic check is
            # insufficient — fabricated grep against nonexistent files
            # should not count as verified.
            pattern = args
            target = step.get("target", step.get("file", ""))
            try:
                re.compile(pattern)
            except re.error:
                issues.append(f"Invalid grep pattern: {pattern}")
                continue
            # If a target file was specified, verify it exists
            if target:
                target_str = target if isinstance(target, str) else str(target)
                target_exists = (
                    target_str in source_set
                    or os.path.basename(target_str) in source_basenames
                    or os.path.isfile(target_str)
                )
                if target_exists:
                    verified += 1
                else:
                    issues.append(f"Grep target not found: {target_str}")
            else:
                # No target specified — pattern is valid, count as partial
                verified += 1

        elif tool in ("Glob", "glob"):
            verified += 1  # Glob patterns are hard to invalidate

        else:
            issues.append(f"Unknown tool: {tool}")

    return verified, len(manifest), issues


def cytotoxic_t_cell_v2(
    triaged: List[TriagedFinding],
    source_paths: List[str],
    timeout: int = 180,
) -> List[CellVerdict]:
    """Cytotoxic T Cell v2: falsifier architecture.

    This implementation now participates in the active pipeline. Its verdicts
    are logged and also returned for Helper-T synthesis and reconciliation.
    """
    code_findings = [
        tf for tf in triaged
        if tf.claim_type in (ClaimType.CODE_BEHAVIORAL, ClaimType.CODE_STRUCTURAL)
        and not tf.is_duplicate
    ]

    if not code_findings:
        _shadow_log.info("CT v2 (v2): no code findings to investigate")
        return []

    if not _get_claude_cli():
        _shadow_log.info("CT v2 (v2): claude CLI not available")
        return []

    prompt = _build_ct_v2_prompt(code_findings, source_paths)
    t0 = time.monotonic()

    try:
        cmd = [
            _get_claude_cli(), "-p", prompt,
            "--allowedTools", "Read,Grep,Glob",
            "--max-turns", "6",
        ]
        if _CT_SCHEMA_PATH.exists():
            cmd.extend(["--output-format", "json"])

        # Bug#4 fix: serialise claude CLI calls to prevent contention
        with _CLAUDE_CLI_LOCK:
            result = sp.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.monotonic() - t0
        output = result.stdout.strip()

        # Parse response (reuse existing parser for structure)
        raw_verdicts = _parse_ct_output(output)

        verdicts: List[CellVerdict] = []
        for rv in raw_verdicts:
            fid = rv.get("finding_id", "")
            if not fid:
                continue

            # Map v2 verdicts to standard pipeline verdicts for logging
            v2_verdict = rv.get("verdict", "CONTESTED").upper()
            manifest = rv.get("search_manifest", [])
            test_severity = rv.get("test_severity", 0)

            # Verify the search manifest mechanically
            if manifest:
                man_verified, man_total, man_issues = _verify_search_manifest(
                    manifest, source_paths,
                )
                # Adjust test_severity: only count verified steps
                test_severity = man_verified
                manifest_note = f"manifest:{man_verified}/{man_total} verified"
                if man_issues:
                    manifest_note += f" issues:{man_issues}"
            else:
                manifest_note = "no manifest provided"

            # Map to standard verdicts
            if v2_verdict == "FALSIFIED":
                std_verdict = "REJECTED"
                confidence = min(0.90, 0.40 + 0.10 * test_severity)
            elif v2_verdict == "CORROBORATED":
                std_verdict = "CONFIRMED"
                confidence = min(0.95, 0.50 + 0.10 * test_severity)
            else:  # CONTESTED or unknown
                std_verdict = "UNCERTAIN"
                confidence = 0.40

            counter_evidence = rv.get("counter_evidence", "")
            verdicts.append(CellVerdict(
                cell_type=CellType.CYTOTOXIC_T,
                finding_id=fid,
                verdict=std_verdict,
                confidence=round(confidence, 3),
                evidence=(
                    f"[CT_v2] {v2_verdict} severity={test_severity} "
                    f"{manifest_note}. {counter_evidence[:200]}"
                ),
                tool_used="ct_v2_falsifier",
                elapsed_s=elapsed,
            ))

        _shadow_log.info(
            "CT v2 (v2): %d verdicts in %.1fs — %s",
            len(verdicts), elapsed,
            {v.verdict: sum(1 for vv in verdicts if vv.verdict == v.verdict)
             for v in verdicts} if verdicts else "none",
        )
        for v in verdicts:
            _shadow_log.info(
                "  %s: %s (%.2f) — %s",
                v.finding_id, v.verdict, v.confidence, v.evidence[:100],
            )

        return verdicts

    except sp.TimeoutExpired:
        _shadow_log.warning("CT v2 (v2): timeout after %ds", timeout)
        return []
    except Exception as e:
        _shadow_log.warning("CT v2 (v2): error: %s: %s", type(e).__name__, e)
        return []


# ── SHADOW B Cell v2 — AST-grounded z3 via SMT-LIB ──────────────────────────
#
# Instead of exec()-ing LLM-generated z3 Python, extract axioms from the
# source code AST and pass them to z3 via parse_smt2_string(). This grounds
# z3 proofs in actual code values, not abstract symbols.

_AST_CONSTANTS_CACHE: Dict[str, Dict[str, Any]] = {}  # Bug#67 fix: cache


def _extract_constants_from_ast(source_path: str) -> Dict[str, Any]:
    """Extract constant assignments from a Python source file's AST.

    Returns a dict of {name: value} for simple assignments like:
        THRESHOLD = 0.5
        MAX_ROUNDS = 20
        tau_sim = 0.33

    Only extracts top-level and class-level constant assignments where
    the value is a literal (number, string, bool, None).
    """
    # Bug#67 fix: cache AST parse results per file
    if source_path in _AST_CONSTANTS_CACHE:
        return _AST_CONSTANTS_CACHE[source_path]

    constants: Dict[str, Any] = {}
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except (OSError, SyntaxError):
        return constants

    def _extract_value(val_node: ast.expr) -> Any:
        """Extract constant value, handling negative literals (E31-15).

        Python parses ``THRESHOLD = -0.5`` as
        ``ast.UnaryOp(ast.USub, ast.Constant(0.5))``, not as a bare
        ast.Constant. Without this, all negative-valued constants are
        invisible to B-Cell v2 Z3 grounding.
        """
        if isinstance(val_node, ast.Constant):
            return val_node.value
        if (isinstance(val_node, ast.UnaryOp)
                and isinstance(val_node.op, ast.USub)
                and isinstance(val_node.operand, ast.Constant)):
            return -val_node.operand.value
        return None  # Not a constant we can extract

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    val = _extract_value(node.value)
                    if val is not None:
                        constants[target.id] = val
        elif isinstance(node, ast.AnnAssign):
            if (isinstance(node.target, ast.Name)
                    and node.value is not None):
                val = _extract_value(node.value)
                if val is not None:
                    constants[node.target.id] = val

    _AST_CONSTANTS_CACHE[source_path] = constants  # Bug#67 fix: cache result
    return constants


def _build_smt2_from_claim(
    claim: str,
    constants: Dict[str, Any],
) -> Optional[str]:
    """Attempt to build an SMT-LIB string from a claim and code constants.

    This is the T_Claim step — translating the natural language claim
    into a formal specification grounded in actual code values.

    Returns None if the claim cannot be translated.
    """
    # Extract variable names and numeric comparisons from the claim
    # Pattern: "VARIABLE OP VALUE" or "VALUE OP VARIABLE"
    comparisons = re.findall(
        r'(\w+)\s*(>=|<=|>|<|==|!=)\s*([-+]?\d*\.?\d+)', claim
    )
    if not comparisons:
        # Try reverse: "VALUE OP VARIABLE"
        comparisons = re.findall(
            r'([-+]?\d*\.?\d+)\s*(>=|<=|>|<|==|!=)\s*(\w+)', claim
        )
        # Swap to normalise: var op value
        comparisons = [(c[2], _flip_op(c[1]), c[0]) for c in comparisons]

    if not comparisons:
        return None

    declared: Set[str] = set()
    declarations: List[str] = []
    assertions: List[str] = []
    has_grounding = False

    for var_name, op, value_str in comparisons:
        try:
            value = float(value_str)
        except ValueError:
            continue

        # Declare each variable only once (SMT-LIB rejects duplicates)
        if var_name not in declared:
            declarations.append(f"(declare-const {var_name} Real)")
            declared.add(var_name)

        smt_op = {">=": ">=", "<=": "<=", ">": ">", "<": "<",
                   "==": "=", "!=": "distinct"}[op]

        # Check if this variable has a grounded value from the AST
        if var_name in constants and isinstance(constants[var_name], (int, float)):
            grounded = float(constants[var_name])
            # Assert the grounded value (only once per variable)
            grounding_assert = f"(assert (= {var_name} {grounded}))"
            if grounding_assert not in assertions:
                assertions.append(grounding_assert)
            # Assert the negation of the claim (to check via UNSAT)
            assertions.append(
                f"(assert (not ({smt_op} {var_name} {value})))"
            )
            has_grounding = True
        else:
            # Ungrounded variable — can only build abstract proof
            assertions.append(
                f"(assert (not ({smt_op} {var_name} {value})))"
            )

    if not assertions:
        return None

    smt2 = "\n".join(declarations + assertions + ["(check-sat)"])
    return smt2 if has_grounding else None  # Only return if grounded


def _flip_op(op: str) -> str:
    """Flip a comparison operator."""
    return {">=": "<=", "<=": ">=", ">": "<", "<": ">",
            "==": "==", "!=": "!="}[op]


def _verify_z3_v2(
    claim: str,
    source_paths: List[str],
) -> CellVerdict:
    """Shadow B Cell z3 v2: AST-grounded verification via SMT-LIB.

    Instead of exec()-ing Python z3 code, this:
    1. Extracts constants from source ASTs (deterministic)
    2. Builds an SMT-LIB string from the claim + grounded values
    3. Passes it to z3.parse_smt2_string() (no exec, no shell)

    Returns a shadow verdict for logging only.
    """
    # Step 1: Extract constants from all source files
    all_constants: Dict[str, Any] = {}
    for sp_path in source_paths:
        file_constants = _extract_constants_from_ast(str(sp_path))
        all_constants.update(file_constants)

    # Step 2: Build SMT-LIB string
    smt2 = _build_smt2_from_claim(claim, all_constants)

    if smt2 is None:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="",
            verdict="UNCERTAIN", confidence=0.15,
            evidence="[B_v2] Cannot ground claim in source AST",
            tool_used="z3_v2_smt2",
        )

    # Step 3: Run z3 via parse_smt2_string (safe — no exec)
    code = f"""
import z3
try:
    assertions = z3.parse_smt2_string({repr(smt2)})
    s = z3.Solver()
    s.set("timeout", 5000)
    s.add(assertions)
    result = s.check()
    if result == z3.unsat:
        print("UNSAT_GROUNDED")
    elif result == z3.sat:
        m = s.model()
        print(f"SAT_COUNTEREXAMPLE: {{m}}")
    else:
        print("UNKNOWN")
except z3.Z3Exception as e:
    print(f"Z3_ERROR: {{e}}")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    # Bug#9 fix: use word-boundary matching instead of substring containment
    grounded_vars = [
        k for k in all_constants
        if re.search(rf'\b{re.escape(str(k))}\b', claim, re.IGNORECASE)
    ]

    if "UNSAT_GROUNDED" in output:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="",
            verdict="CONFIRMED", confidence=0.85,
            evidence=(
                f"[B_v2] z3 SMT-LIB grounded proof. "
                f"Grounded vars: {grounded_vars}. {output}"
            ),
            tool_used="z3_v2_smt2", elapsed_s=elapsed,
        )
    elif "SAT_COUNTEREXAMPLE" in output:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="",
            verdict="REJECTED", confidence=0.85,
            evidence=(
                f"[B_v2] z3 SMT-LIB grounded counterexample. "
                f"Grounded vars: {grounded_vars}. {output}"
            ),
            tool_used="z3_v2_smt2", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="",
            verdict="UNCERTAIN", confidence=0.20,
            evidence=f"[B_v2] z3 SMT-LIB: {output}",
            tool_used="z3_v2_smt2", elapsed_s=elapsed,
        )


def b_cell_v2(
    triaged: List[TriagedFinding],
    source_paths: List[str],
) -> List[CellVerdict]:
    """B Cell v2: AST-grounded z3 verification.

    This implementation now participates in the active pipeline. Its verdicts
    are logged and also returned for Helper-T synthesis and reconciliation.
    """
    verdicts: List[CellVerdict] = []

    for tf in triaged:
        if tf.is_duplicate:
            continue
        if tf.claim_type not in (ClaimType.LOGICAL, ClaimType.MATHEMATICAL):
            continue

        fid = tf.finding.finding_id
        v = _verify_z3_v2(tf.extracted_claim, source_paths)
        v.finding_id = fid
        verdicts.append(v)

    _shadow_log.info(
        "B Cell v2 (v2): %d claims checked, %d grounded proofs",
        len(verdicts),
        sum(1 for v in verdicts if "grounded" in v.evidence.lower()),
    )
    for v in verdicts:
        _shadow_log.info(
            "  %s: %s (%.2f) — %s",
            v.finding_id, v.verdict, v.confidence, v.evidence[:100],
        )

    return verdicts


# ═══════════════════════════════════════════════════════════════════════════════
# V2 COMPONENTS — Gemini CDSFL/FFF Immune Cell Review (4 April 2026)
#
# Each v2 function implements improvements identified through 4 Gemini
# conversations under full CDSFL/FFF (12 rounds, 13 findings, 5/5 proofs).
# All v2 components are now ACTIVE in the pipeline (activated WP6a, Exp 29).
# DC v2, NK v2, Reg T v2 are PRIMARY. CT v2, B-Cell v2 run in parallel with v1.
# ═══════════════════════════════════════════════════════════════════════════════

import math as _math


# ── Dendritic Cell v2 — tightened patterns, citation detection ────────

_MATH_PATTERN_V2 = re.compile(
    r"(?:"
    r"`[^`]*[=<>!]=?[^`]*`"                     # backtick-wrapped: `x >= 0.5`
    r"|\b\d+\.?\d*\s*[<>=!]=?\s*\d"             # numeric: 0.5 >= 0.3
    r"|\b\w+\s*[<>=!]=\s*[-+]?\d"               # named: threshold >= 0.6
    r"|\bsqrt\s*\(|\blog\s*\(|\bexp\s*\("       # math funcs with parens
    r"|\bEq\(|\bGt\(|\bLt\("                    # SymPy constructors
    r"|\bformula\b|\bequation\b|\binequality\b"  # explicit math terms
    r")"
)

_CITATION_PATTERN = re.compile(
    r"(?:"
    r"\b[\w/.-]+\.py[:\s]+(?:line\s+)?\d+"  # file.py:123 or file.py line 123
    r"|\bline\s+\d+\b"                      # line 123
    r"|\bL\d+[-–]L\d+"                      # L10-L20
    r"|\blines?\s+\d+\s*[-–]\s*\d+"         # lines 10-20
    r")",
    re.IGNORECASE,
)


def _classify_claim_v2(finding: Finding) -> Tuple[ClaimType, str, float]:
    """V2 classifier: tightened math pattern, citation-aware routing.

    Changes from v1:
    1. Code-citing findings route to CODE_BEHAVIORAL (not MATH/LOGIC)
    2. Math pattern requires equation context (no bare +/-/=)
    3. Classification order: STAT → STRUCT → CITATION → MATH → LOGIC
    4. Default is UNCATEGORISED (not CODE_BEHAVIORAL garbage-can)
    5. Returns confidence score for downstream gating

    Returns (claim_type, extracted_claim, confidence).
    """
    desc = finding.description

    # 1. Statistical (narrow, specific — check first)
    if _STAT_PATTERN.search(desc):
        return ClaimType.STATISTICAL, desc, 0.85

    # 2. Code structural (decorator/class patterns)
    if _STRUCT_PATTERN.search(desc):
        return ClaimType.CODE_STRUCTURAL, desc, 0.80

    # 3. Code with file:line citations → CODE_BEHAVIORAL
    #    This prevents math-pattern hijacking of code-citing findings
    if _CITATION_PATTERN.search(desc):
        return ClaimType.CODE_BEHAVIORAL, desc, 0.75

    # 4. Mathematical (tightened v2 — requires equation context)
    # Bug#17 fix: use ", " separator instead of " AND " (invalid SymPy syntax)
    if _MATH_PATTERN_V2.search(desc):
        eq_matches = re.findall(r'`([^`]+[=<>+\-*/^][^`]+)`', desc)
        if eq_matches:
            claim = ", ".join(eq_matches) if len(eq_matches) > 1 else eq_matches[0]
        else:
            claim = desc
        return ClaimType.MATHEMATICAL, claim, 0.70

    # 5. Logical (if/then, invariant — only without code context)
    if _LOGIC_PATTERN.search(desc):
        return ClaimType.LOGICAL, desc, 0.65

    # 6. Default: UNCATEGORISED (v1 used CODE_BEHAVIORAL as garbage-can)
    return ClaimType.UNCATEGORISED, desc, 0.30


def dendritic_cell_v2(
    findings: List[Finding],
    v1_triaged: List[TriagedFinding],
) -> List[TriagedFinding]:
    """Dendritic Cell v2: tightened classification with v1 comparison logging.

    Logs every case where v2 would classify differently from v1.
    Returns v2 triaged list for shadow pipeline consumption.
    """
    v2_triaged: List[TriagedFinding] = []
    diffs = 0

    for i, f in enumerate(findings):
        claim_type, extracted, confidence = _classify_claim_v2(f)
        tf = TriagedFinding(
            finding=f,
            claim_type=claim_type,
            extracted_claim=extracted,
        )
        v2_triaged.append(tf)

        # Compare against v1
        if i < len(v1_triaged):
            v1_type = v1_triaged[i].claim_type
            if v1_type != claim_type:
                diffs += 1
                _shadow_log.info(
                    "DC v2 reclassification: %s — v1=%s → v2=%s (conf=%.2f)",
                    f.finding_id, v1_type.value, claim_type.value, confidence,
                )

    _shadow_log.info(
        "DC v2 (v2): %d/%d findings reclassified",
        diffs, len(findings),
    )
    return v2_triaged


# ── NK Cell v2 — FP continue fix + intra-round dedup ─────────────────

def nk_cell_v2(
    triaged: List[TriagedFinding],
    prior_findings: List[Finding],
    tau_sim: float = 0.50,  # Raised from 0.33: class_match base (0.30) + shared
                            # vocabulary caused 90-100% false DUPLICATE by mid-run.
                            # At 0.50, same-class needs Jaccard >= 0.286 (real overlap).
    false_positive_db: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[List[TriagedFinding], List[CellVerdict]]:
    """NK Cell v2: fixes control flow leak + adds intra-round dedup.

    Changes from v1:
    1. FP match now skips anomaly detection (continue after break)
    2. Intra-round dedup: checks against current batch, not just prior
    3. Returned triaged state marks duplicates for downstream synthesis
    4. Bug-closed gate: if a prior finding already has a verified fix,
       new findings about the same bug are closed immediately.
       First verified fix wins (Occam's razor / good-enough principle).
    """
    fp_db = false_positive_db or _KNOWN_FALSE_POSITIVES
    verdicts: List[CellVerdict] = []

    # Intra-round tracking: findings accepted so far in this batch
    accepted_this_round: List[Finding] = []

    for tf in triaged:
        f = tf.finding

        # 1. Dedup against prior findings
        best_sim = 0.0
        best_match: Optional[str] = None
        best_match_finding: Optional[Finding] = None
        for pf in prior_findings:
            sim = _finding_similarity(f, pf)
            if sim > best_sim:
                best_sim = sim
                best_match = pf.finding_id
                best_match_finding = pf

        if best_sim >= tau_sim and best_match is not None:
            # Bug-closed gate: if the matched prior finding already has a
            # VERIFIED fix, this bug is CLOSED. First verified fix wins.
            # "Verified" means programmatically evaluated (pyright/ruff/bandit
            # pass, no new issues introduced) — not model opinion.
            # New findings about the same bug are dead on arrival.
            has_verified_fix = (
                best_match_finding is not None
                and bool(best_match_finding.proposed_fix.strip())
                and best_match_finding.verified
            )
            is_escalated = (
                best_match_finding is not None
                and best_match_finding.escalated
            )
            if has_verified_fix:
                tool = "v2_bug_closed"
                evidence = (
                    f"[NK_v2] Bug CLOSED — duplicate of {best_match} "
                    f"(sim={best_sim:.3f}) which has a programmatically verified fix. "
                    f"First sufficient fix wins. Move on."
                )
            elif is_escalated:
                tool = "v2_escalated"
                evidence = (
                    f"[NK_v2] Bug ESCALATED — duplicate of {best_match} "
                    f"(sim={best_sim:.3f}) which is escalated to human reviewer. "
                    f"No programmatic fix possible. Do not attempt."
                )
            else:
                tool = "v2_similarity_dedup"
                evidence = (
                    f"[NK_v2] Duplicate of {best_match} (sim={best_sim:.3f})"
                )

            tf.is_duplicate = True
            tf.duplicate_of = best_match
            tf.similarity = best_sim
            verdicts.append(CellVerdict(
                cell_type=CellType.NK_CELL,
                finding_id=f.finding_id,
                verdict="DUPLICATE",
                confidence=best_sim,
                evidence=evidence,
                tool_used=tool,
            ))
            continue

        # 1b. Intra-round dedup against already-accepted findings
        intra_best_sim = 0.0
        intra_best_match: Optional[str] = None
        for af in accepted_this_round:
            sim = _finding_similarity(f, af)
            if sim > intra_best_sim:
                intra_best_sim = sim
                intra_best_match = af.finding_id

        if intra_best_sim >= tau_sim and intra_best_match is not None:
            tf.is_duplicate = True
            tf.duplicate_of = intra_best_match
            tf.similarity = intra_best_sim
            verdicts.append(CellVerdict(
                cell_type=CellType.NK_CELL,
                finding_id=f.finding_id,
                verdict="DUPLICATE",
                confidence=intra_best_sim,
                evidence=f"[NK_v2] Intra-round dup of {intra_best_match} (sim={intra_best_sim:.3f})",
                tool_used="v2_intra_round_dedup",
            ))
            continue

        # 2. FP check — with continue fix (v1 bug: fell through to anomaly)
        is_fp = False
        for fp in fp_db:
            if fp["pattern"].search(f.description):
                model_match = (
                    not fp.get("expected_model")
                    or fp["expected_model"] == f.model_id
                )
                if model_match:
                    verdicts.append(CellVerdict(
                        cell_type=CellType.NK_CELL,
                        finding_id=f.finding_id,
                        verdict="REJECTED",
                        confidence=0.90,
                        evidence=f"[NK_v2] Known FP: {fp['source']}",
                        tool_used="v2_false_positive_db",
                    ))
                    is_fp = True
                    break

        if is_fp:
            continue  # v2 FIX: skip anomaly detection for known FPs

        # 3. Anomaly detection
        # E31-07 fix: v2 must match v1 behaviour — emit REJECTED/0.6 so
        # Helper T registers the anomaly signal. UNCERTAIN/0.4 contributed
        # zero weight, effectively neutering anomaly detection in v2.
        if f.severity > 0.95 and f.round_idx > 5:
            verdicts.append(CellVerdict(
                cell_type=CellType.NK_CELL,
                finding_id=f.finding_id,
                verdict="REJECTED",
                confidence=0.6,
                evidence=f"[NK_v2] Late-round high severity ({f.severity:.2f} at R{f.round_idx}) — possible inflation",
                tool_used="v2_anomaly_detection",
            ))

        # Track accepted finding for intra-round dedup
        accepted_this_round.append(f)

    bugs_closed = sum(1 for v in verdicts if v.tool_used == "v2_bug_closed")
    bugs_escalated = sum(1 for v in verdicts if v.tool_used == "v2_escalated")
    intra_dups = sum(1 for v in verdicts if v.tool_used == "v2_intra_round_dedup")
    _shadow_log.info(
        "NK v2 (v2): %d verdicts (%d intra-round dups, %d bugs closed, %d escalated to HIL)",
        len(verdicts), intra_dups, bugs_closed, bugs_escalated,
    )

    # Return updated triaged state — NK v2 now marks duplicates for downstream
    return triaged, verdicts


# ── Helper T v2 — hybrid domain-based synthesis ──────────────────────
#
# Two-level aggregation:
#   Level 1 (within domain): log-odds combines correlated signals
#     e.g., CT v1 + CT v2 examining the same code
#   Level 2 (across domains): max-signal combines independent domains
#     e.g., code verification vs mathematical proof vs dedup
#
# In Run 11 (single signal per domain), Level 1 is an identity operation.
# In Run 12+ (v2 components active), Level 1 becomes load-bearing.
#
# Fixes three proven bugs:
#   - Dead else block: eliminated (no Pr + Pc = 1 constraint)
#   - 1.5x rejection barrier: replaced by explicit 0.7 scaling
#   - Orthogonal ganging: max-signal prevents weak cross-domain stacking

_DOMAIN_CODE = "code"
_DOMAIN_MATH = "math"
_DOMAIN_PATTERN = "pattern"


def _verdict_domain(v: CellVerdict) -> str:
    """Map a verdict to its verification domain."""
    tool = v.tool_used.lower()
    if any(k in tool for k in ("ct", "falsif", "code", "snippet")):
        return _DOMAIN_CODE
    elif any(k in tool for k in ("sympy", "z3", "smt", "stats")):
        return _DOMAIN_MATH
    elif any(k in tool for k in ("dedup", "false_positive", "anomaly", "similar")):
        return _DOMAIN_PATTERN
    return _DOMAIN_CODE  # default


def _confidence_to_log_odds(c: float) -> float:
    """Convert confidence [0,1] to log-odds magnitude, clamped to avoid infinity.

    Bug#33 fix: confidence is a magnitude (how certain the cell is about its
    verdict), not a probability of correctness. A REJECTED verdict with
    confidence 0.3 means "weakly certain it's rejected", not "30% chance".
    We clamp the floor to 0.5 so that low-confidence verdicts contribute
    near-zero log-odds rather than negative (which would invert the signal).
    """
    c = max(0.50, min(0.99, c))
    return _math.log(c / (1.0 - c))


def _log_odds_to_confidence(lo: float) -> float:
    """Convert log-odds back to confidence [0,1]."""
    return 1.0 / (1.0 + _math.exp(-abs(lo)))


def helper_t_v2(
    triaged: List[TriagedFinding],
    all_verdicts: List[CellVerdict],
    rejection_asymmetry: float = 0.7,
) -> Tuple[Dict[str, str], Dict[str, float]]:
    """Helper T Cell v2: hybrid domain-based synthesis.

    Two-level aggregation:
    1. Within each domain (code, math, pattern): log-odds aggregation
       of multiple signals from the same verification method.
    2. Across domains: max effective signal wins, with asymmetric
       scaling on rejection evidence (0.7 factor).
    """
    verdicts_by_finding: Dict[str, List[CellVerdict]] = {}
    for v in all_verdicts:
        verdicts_by_finding.setdefault(v.finding_id, []).append(v)

    final_verdicts: Dict[str, str] = {}
    final_confidences: Dict[str, float] = {}

    for tf in triaged:
        fid = tf.finding.finding_id
        fv = verdicts_by_finding.get(fid, [])

        # Auto-reject duplicates
        if tf.is_duplicate:
            final_verdicts[fid] = "DUPLICATE"
            final_confidences[fid] = tf.similarity
            continue

        if not fv:
            final_verdicts[fid] = "UNCERTAIN"
            final_confidences[fid] = 0.0
            continue

        # ── Level 1: Within-domain aggregation (log-odds) ──
        domain_verdicts: Dict[str, List[CellVerdict]] = {}
        for v in fv:
            d = _verdict_domain(v)
            domain_verdicts.setdefault(d, []).append(v)

        domain_results: Dict[str, Tuple[str, float]] = {}

        for domain, dvs in domain_verdicts.items():
            confirms = [v for v in dvs if v.verdict == "CONFIRMED"]
            rejects = [v for v in dvs if v.verdict in ("REJECTED", "DUPLICATE")]

            if not confirms and not rejects:
                domain_results[domain] = ("UNCERTAIN", 0.0)
                continue

            if len(confirms) + len(rejects) == 1:
                # Single signal: use directly (identity operation)
                v = (confirms or rejects)[0]
                domain_results[domain] = (v.verdict, v.confidence)
            else:
                # Multiple signals: log-odds aggregation
                confirm_lo = sum(
                    _confidence_to_log_odds(v.confidence) for v in confirms
                )
                reject_lo = sum(
                    _confidence_to_log_odds(v.confidence) for v in rejects
                )

                if confirm_lo >= reject_lo:
                    agg_conf = _log_odds_to_confidence(confirm_lo)
                    domain_results[domain] = ("CONFIRMED", agg_conf)
                else:
                    agg_conf = _log_odds_to_confidence(reject_lo)
                    domain_results[domain] = ("REJECTED", agg_conf)

        # ── Level 2: Across-domain (max signal wins) ──
        best_confirm = 0.0
        best_reject = 0.0

        for domain, (verdict, conf) in domain_results.items():
            if verdict == "CONFIRMED":
                best_confirm = max(best_confirm, conf)
            elif verdict in ("REJECTED", "DUPLICATE"):
                best_reject = max(best_reject, conf)

        # Asymmetric scaling: rejection must overcome 0.7 barrier
        effective_reject = best_reject * rejection_asymmetry

        if effective_reject > best_confirm and best_reject > 0:
            final_verdicts[fid] = "REJECTED"
            # E31-05 fix: store effective_reject (after asymmetric scaling),
            # not raw best_reject. The decision uses the scaled value — the
            # stored confidence must match the decision logic.
            final_confidences[fid] = round(effective_reject, 4)
        elif best_confirm > 0:
            final_verdicts[fid] = "CONFIRMED"
            final_confidences[fid] = round(best_confirm, 4)
        else:
            final_verdicts[fid] = "UNCERTAIN"
            final_confidences[fid] = 0.0

    _shadow_log.info(
        "Helper T v2 (v2): %d findings — %d CONFIRMED, %d REJECTED, "
        "%d UNCERTAIN, %d DUPLICATE",
        len(final_verdicts),
        sum(1 for v in final_verdicts.values() if v == "CONFIRMED"),
        sum(1 for v in final_verdicts.values() if v == "REJECTED"),
        sum(1 for v in final_verdicts.values() if v == "UNCERTAIN"),
        sum(1 for v in final_verdicts.values() if v == "DUPLICATE"),
    )

    return final_verdicts, final_confidences


# ── Regulatory T v2 — fixed removal rate + proportional model check ──

def regulatory_t_v2(
    final_verdicts: Dict[str, str],
    triaged: List[TriagedFinding],
    max_rejection_rate: float = 0.65,
    min_findings_for_check: int = 5,
) -> Tuple[bool, str]:
    """Regulatory T Cell v2: fixed math.

    Changes from v1:
    1. Check 1 uses combined removal rate (rejected + duplicated) / total
    2. Check 3 only counts findings present in final_verdicts (intersection)
    3. Check 3 uses proportional threshold (>= 0.85) instead of exact match
    """
    total = len(final_verdicts)
    if total < min_findings_for_check:
        return False, f"[RT_v2] Too few findings ({total}) for meta-check"

    rejected = sum(1 for v in final_verdicts.values() if v == "REJECTED")
    duplicated = sum(1 for v in final_verdicts.values() if v == "DUPLICATE")
    removed = rejected + duplicated
    removal_rate = removed / total

    reasons: List[str] = []

    # Check 1: Combined removal rate (v2: includes duplicates)
    if removal_rate > max_rejection_rate:
        reasons.append(
            f"[RT_v2] Removal rate {removed}/{total} ({removal_rate:.1%}) "
            f"exceeds threshold ({max_rejection_rate:.0%}) "
            f"[rejected={rejected}, duplicated={duplicated}]"
        )

    # Check 3: Per-model removal — proportional, intersection-based
    model_counts: Dict[str, int] = {}
    model_removed: Dict[str, int] = {}
    for tf in triaged:
        fid = tf.finding.finding_id
        if fid not in final_verdicts:
            continue  # v2 fix: only count findings present in final_verdicts
        mid = tf.finding.model_id
        model_counts[mid] = model_counts.get(mid, 0) + 1
        if final_verdicts[fid] in ("REJECTED", "DUPLICATE"):
            model_removed[mid] = model_removed.get(mid, 0) + 1

    for mid, total_m in model_counts.items():
        rem_m = model_removed.get(mid, 0)
        # v2: proportional threshold >= 0.85 instead of exact match
        if total_m >= 3 and rem_m / total_m >= 0.85:
            reasons.append(
                f"[RT_v2] {rem_m}/{total_m} ({rem_m / total_m:.0%}) findings "
                f"from {mid} removed — possible systematic bias"
            )

    if reasons:
        _shadow_log.info(
            "RT v2 (v2): AUTOIMMUNE flagged — %s", "; ".join(reasons),
        )
        return True, "; ".join(reasons)

    _shadow_log.info(
        "RT v2 (v2): healthy — %.1f%% removal rate", removal_rate * 100,
    )
    return False, f"[RT_v2] Pipeline healthy: {removal_rate:.1%} removal rate"


# ═══════════════════════════════════════════════════════════════════════════════
# WP3c SHADOW: Typed LLM Classifier (Dendritic Cell enhancement)
#
# Replaces regex-based claim classification with a lightweight LLM call.
# Regex fundamentally cannot distinguish "x + y = z" (mathematical) from
# "model A + model B = the full team" (natural language with operators).
# MF-01/MF-02/C5-06 showed ~30% misclassification rate from regex.
#
# SHADOW MODE: runs alongside DC v2 (regex), logs comparison data.
# Activated only when shadow data proves improvement over regex.
# ═══════════════════════════════════════════════════════════════════════════════

_CLASSIFIER_SYSTEM_PROMPT = """\
You are a claim type classifier for a code verification pipeline.
Classify the following finding description into exactly ONE category.
Respond with ONLY the category name, nothing else.

Categories:
- MATHEMATICAL: the finding makes a claim about equations, inequalities, \
bounds, or numeric relationships that can be verified symbolically.
- LOGICAL: the finding makes an if/then claim, invariant assertion, or \
reachability argument about code paths.
- STATISTICAL: the finding makes a claim about distributions, p-values, \
confidence intervals, or statistical significance.
- CODE_STRUCTURAL: the finding claims a missing or incorrect code structure \
(missing decorator, wrong class hierarchy, absent method).
- CODE_BEHAVIORAL: the finding describes a bug in runtime behaviour, wrong \
return values, incorrect state transitions, or logic errors.
- UNCATEGORISED: the finding does not clearly fit any of the above."""

_CLASSIFIER_MODEL = "haiku"  # Claude CLI model alias — Max plan


def typed_llm_classifier(
    findings: List[Finding],
    regex_triaged: List[TriagedFinding],
) -> List[Dict[str, Any]]:
    """WP3c shadow: classify findings via lightweight LLM call.

    Runs alongside the DC v2 regex classifier. Logs every case where
    the LLM would classify differently from regex. Returns comparison
    records for analysis.

    Does NOT modify triaged findings — shadow only.

    Rewired from OpenRouter to Claude CLI Haiku (Max plan, local billing).
    Serialised via _CLAUDE_CLI_LOCK to prevent contention with CT cells.
    """
    comparisons: List[Dict[str, Any]] = []

    if not _get_claude_cli():
        _shadow_log.info(
            "LLM classifier: DISABLED (claude CLI not available). "
            "%d findings skipped.", len(findings),
        )
        return comparisons

    _CATEGORY_MAP = {
        "mathematical": ClaimType.MATHEMATICAL,
        "logical": ClaimType.LOGICAL,
        "statistical": ClaimType.STATISTICAL,
        "code_structural": ClaimType.CODE_STRUCTURAL,
        "code_behavioral": ClaimType.CODE_BEHAVIORAL,
        "uncategorised": ClaimType.UNCATEGORISED,
    }

    _shadow_log.info(
        "LLM classifier: ENABLED (CLI Haiku). "
        "%d findings to classify.", len(findings),
    )

    for i, (f, regex_tf) in enumerate(zip(findings, regex_triaged)):
        t0 = time.monotonic()
        try:
            # Build classification prompt — system + user in single -p call
            prompt = (
                f"{_CLASSIFIER_SYSTEM_PROMPT}\n\n"
                f"Finding description:\n{f.description[:500]}"
            )
            cmd = [
                _get_claude_cli(), "-p", prompt,
                "--model", _CLASSIFIER_MODEL,
                "--output-format", "text",
                "--max-turns", "1",
            ]

            with _CLAUDE_CLI_LOCK:
                result = sp.run(
                    cmd, capture_output=True, text=True, timeout=45,
                )
            elapsed = time.monotonic() - t0
            response = result.stdout.strip()

            llm_category = response.strip().lower().replace(" ", "_")
            llm_type = _CATEGORY_MAP.get(llm_category, ClaimType.UNCATEGORISED)

            record = {
                "finding_id": f.finding_id,
                "regex_type": regex_tf.claim_type.value,
                "llm_type": llm_type.value,
                "llm_raw": response.strip(),
                "match": regex_tf.claim_type == llm_type,
                "elapsed_s": round(elapsed, 3),
            }
            comparisons.append(record)

            if regex_tf.claim_type != llm_type:
                _shadow_log.info(
                    "LLM classifier: %s — regex=%s llm=%s (%.1fs)",
                    f.finding_id, regex_tf.claim_type.value,
                    llm_type.value, elapsed,
                )
        except Exception as e:
            elapsed = time.monotonic() - t0
            comparisons.append({
                "finding_id": f.finding_id,
                "regex_type": regex_tf.claim_type.value,
                "llm_type": "ERROR",
                "llm_raw": str(e)[:100],
                "match": False,
                "elapsed_s": round(elapsed, 3),
            })
            _shadow_log.warning(
                "LLM classifier error for %s: %s", f.finding_id, e,
            )

    match_count = sum(1 for c in comparisons if c["match"])
    total = len(comparisons)
    _shadow_log.info(
        "LLM classifier: %d/%d agree with regex (%.1f%%)",
        match_count, total, (match_count / max(total, 1)) * 100,
    )

    return comparisons


# ═══════════════════════════════════════════════════════════════════════════════
# WP3d SHADOW: Formalisation Agent (B-Cell enhancement)
#
# Translates natural language preconditions into formal Z3 invariants before
# B-Cell verification. MF-03/MF-04/C5-07 showed context erasure strips
# preconditions from claims, causing false rejections. E.g., "for all x > 0,
# f(x) = x^2" gets the "x > 0" stripped before Z3, which then tests the
# claim over ALL x (including negative), producing a false rejection.
#
# SHADOW MODE: runs alongside B-Cell, logs what it would have produced.
# If the agent's Z3 constraints would have prevented false rejections,
# the data proves its worth. Activated only when proven.
# ═══════════════════════════════════════════════════════════════════════════════

# Precondition patterns — extract "for all x > 0", "when n >= 1", etc.
_PRECONDITION_PATTERNS = [
    re.compile(r'(?:for\s+all|for\s+every|when|where|if|given\s+that|assuming)\s+([^,;.]+(?:[<>=!]+)[^,;.]+)', re.IGNORECASE),
    re.compile(r'(?:with|under)\s+(?:the\s+)?(?:constraint|condition|assumption)\s+(?:that\s+)?([^,;.]+)', re.IGNORECASE),
    re.compile(r'(\b[a-z]\s*[><=!]+\s*\d+(?:\.\d+)?)', re.IGNORECASE),
]

# Variable binding patterns — "let x = ...", "where n is ..."
_VARIABLE_PATTERNS = [
    re.compile(r'(?:let|define)\s+([a-z])\s*=\s*([^,;.]+)', re.IGNORECASE),
    re.compile(r'(?:where|with)\s+([a-z])\s+(?:is|=)\s+([^,;.]+)', re.IGNORECASE),
]

# Operator mapping for Z3 translation
_OP_MAP = {
    ">=": ">=", "<=": "<=", ">": ">", "<": "<",
    "==": "==", "!=": "!=", "=": "==",
}


def _extract_preconditions(claim: str) -> List[str]:
    """Extract natural language preconditions from a claim string.

    Returns list of precondition strings like "x > 0", "n >= 1".
    """
    preconditions: List[str] = []
    for pat in _PRECONDITION_PATTERNS:
        for match in pat.finditer(claim):
            pc = match.group(1).strip()
            if pc and len(pc) < 100:  # sanity cap
                preconditions.append(pc)
    return preconditions


def _preconditions_to_z3(preconditions: List[str], claim: str) -> Optional[str]:
    """Translate preconditions into a Z3 constraint string.

    Returns a Z3-compatible assertion string, or None if translation fails.
    This is a best-effort mechanical translation — not an LLM call.
    """
    if not preconditions:
        return None

    # Extract variable names from preconditions and claim
    vars_found: Set[str] = set()
    for pc in preconditions:
        vars_found.update(re.findall(r'\b([a-z])\b', pc))
    for v in re.findall(r'\b([a-z])\b', claim):
        if v not in ('e',):  # exclude Euler's number
            vars_found.add(v)

    if not vars_found:
        return None

    # Build Z3 script
    lines = ["from z3 import *"]
    for v in sorted(vars_found):
        lines.append(f"{v} = Real('{v}')")

    lines.append("s = Solver()")

    # Add preconditions as constraints
    for pc in preconditions:
        # Simple translation: replace operators
        z3_pc = pc.strip()
        for nl_op, z3_op in _OP_MAP.items():
            z3_pc = z3_pc.replace(nl_op, z3_op)
        lines.append(f"# Precondition: {pc}")
        lines.append(f"s.add({z3_pc})")

    return "\n".join(lines)


def formalisation_agent(
    triaged: List[TriagedFinding],
    b_cell_verdicts: List[CellVerdict],
) -> List[Dict[str, Any]]:
    """WP3d shadow: extract and formalise preconditions for B-Cell claims.

    For each MATHEMATICAL or LOGICAL finding:
    1. Extract natural language preconditions from the description
    2. Translate to Z3 constraint fragments
    3. Compare: did the B-Cell's verdict change when preconditions are
       accounted for? (i.e., would the Formalisation Agent have prevented
       a false rejection?)

    Does NOT modify verdicts — shadow only. Logs comparison data.
    """
    comparisons: List[Dict[str, Any]] = []

    # Build B-Cell verdict lookup
    bcell_verdicts: Dict[str, CellVerdict] = {}
    for v in b_cell_verdicts:
        if v.cell_type == CellType.B_CELL:
            bcell_verdicts[v.finding_id] = v

    for tf in triaged:
        if tf.claim_type not in (ClaimType.MATHEMATICAL, ClaimType.LOGICAL):
            continue
        if tf.is_duplicate:
            continue

        fid = tf.finding.finding_id
        desc = tf.finding.description

        # Step 1: extract preconditions
        preconditions = _extract_preconditions(desc)

        # Step 2: attempt Z3 translation
        z3_fragment = _preconditions_to_z3(preconditions, tf.extracted_claim)

        # Step 3: compare against B-Cell verdict
        bcell_v = bcell_verdicts.get(fid)
        bcell_verdict = bcell_v.verdict if bcell_v else "NO_VERDICT"

        # Would preconditions have mattered?
        # A REJECTED verdict on a claim with extractable preconditions
        # is a candidate for false rejection (context erasure).
        potential_false_rejection = (
            bcell_verdict == "REJECTED"
            and len(preconditions) > 0
        )

        record = {
            "finding_id": fid,
            "claim_type": tf.claim_type.value,
            "preconditions_found": len(preconditions),
            "preconditions": preconditions,
            "z3_fragment": z3_fragment,
            "z3_translatable": z3_fragment is not None,
            "bcell_verdict": bcell_verdict,
            "potential_false_rejection": potential_false_rejection,
        }
        comparisons.append(record)

        if potential_false_rejection:
            _shadow_log.info(
                "Formalisation agent: %s — REJECTED with %d preconditions "
                "(potential false rejection). Preconditions: %s",
                fid, len(preconditions), preconditions,
            )
        elif preconditions:
            _shadow_log.info(
                "Formalisation agent: %s — %d preconditions extracted, "
                "B-Cell verdict=%s. Z3 translatable=%s",
                fid, len(preconditions), bcell_verdict,
                z3_fragment is not None,
            )

    total = len(comparisons)
    with_pc = sum(1 for c in comparisons if c["preconditions_found"] > 0)
    potential_fr = sum(1 for c in comparisons if c["potential_false_rejection"])
    _shadow_log.info(
        "Formalisation agent: %d math/logic findings, %d with "
        "preconditions, %d potential false rejections",
        total, with_pc, potential_fr,
    )

    return comparisons


def _reconciliation_gate(
    v1_verdicts: Dict[str, str],
    v1_confidences: Dict[str, float],
    v2_verdicts: Dict[str, str],
    v2_confidences: Dict[str, float],
) -> Tuple[Dict[str, str], Dict[str, float], Set[str]]:
    """WP3b: Reconciliation Gate — immutable state transition check.

    Merges v1 and v2 verdicts before Regulatory T meta-check.
    Rules:
    1. If v1 and v2 agree: use that verdict with max confidence.
    2. If v1 and v2 disagree: use the higher-confidence verdict.
    3. If only one pipeline produced a verdict: use it.
    4. REJECTED verdicts from both pipelines are LOCKED — cannot be
       overridden by downstream autoimmune recovery (MF-34/MF-35/C5-25).

    Returns (reconciled_verdicts, reconciled_confidences, locked_ids).
    locked_ids: finding IDs where both pipelines agreed REJECTED.
    These MUST NOT be resurrected by autoimmune override (E31-02).
    """
    reconciled: Dict[str, str] = {}
    reconciled_conf: Dict[str, float] = {}
    locked_ids: Set[str] = set()

    all_fids = set(v1_verdicts) | set(v2_verdicts)
    for fid in all_fids:
        v1v = v1_verdicts.get(fid)
        v1c = v1_confidences.get(fid, 0.0)
        v2v = v2_verdicts.get(fid)
        v2c = v2_confidences.get(fid, 0.0)

        if v1v is None and v2v is not None:
            reconciled[fid] = v2v
            reconciled_conf[fid] = v2c
        elif v2v is None and v1v is not None:
            reconciled[fid] = v1v
            reconciled_conf[fid] = v1c
        elif v1v == v2v:
            # Agreement path — three outcomes based on confidence:
            #
            # 1. HIGH-CONFIDENCE REJECTION (max conf >= 0.5): LOCKED.
            #    Both pipelines independently verified rejection with
            #    meaningful tool evidence. Autoimmune recovery cannot
            #    override. (E31-02 / MF-34 / MF-35 / C5-25)
            #
            # 2. LOW-CONFIDENCE MUTUAL REJECTION (max conf < 0.5): UNSCORED.
            #    Both pipelines returned REJECTED/DUPLICATE but neither had
            #    real evidence — typically UNCERTAIN (0.15) from B-Cell
            #    "can't ground in AST" or NK DUPLICATE (cross-round) at
            #    low similarity. This is absence of evidence, NOT evidence
            #    of absence. Finding passes through unscored for downstream
            #    handling (convergence gate, HIL).
            #
            # 3. AGREEMENT ON NON-REJECTION: use shared verdict, max conf.
            max_conf = max(v1c, v2c)
            if v1v in ("REJECTED", "DUPLICATE"):
                if max_conf >= 0.5:
                    # Tool-verified rejection — LOCK
                    reconciled[fid] = v1v
                    reconciled_conf[fid] = max_conf
                    locked_ids.add(fid)
                    _shadow_log.info(
                        "Reconciliation LOCKED: %s — both pipelines REJECTED "
                        "(v1=%.2f, v2=%.2f, max=%.2f >= 0.5)",
                        fid, v1c, v2c, max_conf,
                    )
                else:
                    # Low-confidence mutual rejection — UNSCORED pass-through
                    reconciled[fid] = "UNSCORED"
                    reconciled_conf[fid] = max_conf
                    _shadow_log.info(
                        "Reconciliation UNSCORED: %s — both pipelines REJECTED "
                        "but low confidence (v1=%.2f, v2=%.2f, max=%.2f < 0.5) "
                        "— absence of evidence, not evidence of absence",
                        fid, v1c, v2c, max_conf,
                    )
            else:
                reconciled[fid] = v1v
                reconciled_conf[fid] = max_conf
        else:
            # Disagreement: higher confidence wins, with minimum margin
            # Bug#16 fix: near-ties fall back to UNCERTAIN
            margin = abs(v1c - v2c)
            if margin < 0.10:
                reconciled[fid] = "UNCERTAIN"
                reconciled_conf[fid] = max(v1c, v2c)
            elif v1c >= v2c:
                reconciled[fid] = v1v
                reconciled_conf[fid] = v1c
            else:
                reconciled[fid] = v2v
                reconciled_conf[fid] = v2c

        # Log reconciliation diffs
        if v1v and v2v and v1v != v2v:
            _shadow_log.info(
                "Reconciliation: %s — v1=%s(%.2f) vs v2=%s(%.2f) → %s(%.2f)",
                fid, v1v, v1c, v2v, v2c,
                reconciled[fid], reconciled_conf[fid],
            )

    return reconciled, reconciled_conf, locked_ids


def run_immune_pipeline(
    new_findings: List[Finding],
    prior_findings: List[Finding],
    source_paths: List[str],
    observation_only: bool = True,
    ct_enabled: bool = True,
    ct_timeout: int = 300,
    tau_sim: float = 0.50,  # Raised from 0.33: class_match base (0.30) + shared
                            # vocabulary caused 90-100% false DUPLICATE by mid-run.
                            # At 0.50, same-class needs Jaccard >= 0.286 (real overlap).
    false_positive_db: Optional[List[Dict[str, Any]]] = None,
    max_rejection_rate: float = 0.65,
) -> ImmuneResponse:
    """Run the full 6-cell immune pipeline.

    Stages:
        1. Dendritic Cell triage (sequential, ~1s)
        2. Cytotoxic T + B-Cell + NK Cell (parallel, ~30-60s)
        3. Helper T synthesis + Regulatory T meta-check (sequential, ~1s)

    Args:
        new_findings: Findings from the current round.
        prior_findings: All findings from previous rounds.
        source_paths: Paths to source files for verification.
        observation_only: If True, all findings pass through regardless.
        ct_enabled: Whether to run Cytotoxic T-Cell (claude CLI).
        ct_timeout: Timeout for CT agent in seconds.
        tau_sim: Similarity threshold for NK Cell dedup.
        false_positive_db: Known false-positive patterns for NK Cell.
        max_rejection_rate: Regulatory T-Cell autoimmune threshold.

    Returns:
        ImmuneResponse with complete pipeline results.
    """
    timings: Dict[str, float] = {}
    tool_usage: Dict[str, int] = {}

    # ── Stage 0: Skin barrier pre-filter (WP6a: now ACTIVE) ────────
    # Deterministic check: do cited files/lines exist? Findings that fail
    # the barrier are filtered out before reaching the Dendritic Cell.
    t0 = time.monotonic()
    passed_findings, barrier_results = skin_barrier_check(new_findings, source_paths)
    timings["skin_barrier"] = round(time.monotonic() - t0, 4)
    # Bug#82 fix: count total executions, not just failures
    tool_usage["skin_barrier"] = len(barrier_results)
    tool_usage["skin_barrier_blocked"] = sum(1 for r in barrier_results if not r.passed)

    # WP6a: filter out findings that failed skin barrier (unless observation_only)
    if not observation_only:
        failed_ids = {r.finding_id for r in barrier_results if not r.passed}
        barrier_filtered = [f for f in new_findings if f.finding_id not in failed_ids]
        barrier_rejected = [f for f in new_findings if f.finding_id in failed_ids]
        new_findings = barrier_filtered
    else:
        barrier_rejected = []

    # ── Stage 1: Dendritic Cell triage ────────────────────────────────
    # WP6a/WP3a: v2 classifier is now PRIMARY (Epistemic Routing Layer)
    # v1 runs alongside for comparison logging only
    t0 = time.monotonic()
    v1_triaged = dendritic_cell_triage(new_findings)
    timings["dendritic_v1"] = round(time.monotonic() - t0, 4)

    t0_dc_v2 = time.monotonic()
    triaged = dendritic_cell_v2(new_findings, v1_triaged)
    timings["dendritic"] = round(time.monotonic() - t0_dc_v2, 4)

    # Log claim type distribution
    type_counts = {}
    for tf in triaged:
        key = tf.claim_type.value
        type_counts[key] = type_counts.get(key, 0) + 1

    # ── Stage 1.5: Typed LLM Classifier shadow (WP3c) ────────────────
    # Runs alongside DC v2 regex — logs comparison data for activation decision
    t0_llm_cls = time.monotonic()
    try:
        llm_classifier_results = typed_llm_classifier(new_findings, triaged)
    except Exception as e:
        _shadow_log.warning("LLM classifier failed: %s", e)
        llm_classifier_results = []
    timings["llm_classifier"] = round(time.monotonic() - t0_llm_cls, 4)

    # ── Stage 2: Parallel verification (WP6a: v2 components active) ──
    all_verdicts: List[CellVerdict] = []
    t0 = time.monotonic()

    # MF-20 fix: deep-copy triaged list for NK to prevent race conditions
    import copy
    triaged_for_nk = copy.deepcopy(triaged)
    nk_triaged_result = None  # Will hold NK v2's returned triaged state

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {}

        # 2a: CT v1 (code FFF investigation)
        if ct_enabled:
            futures["cytotoxic_t"] = pool.submit(
                cytotoxic_t_cell, triaged, source_paths, ct_timeout,
            )

        # 2a': CT v2 falsifier (WP6a: now ACTIVE, verdicts feed pipeline)
        if ct_enabled:
            futures["ct_v2"] = pool.submit(
                cytotoxic_t_cell_v2, triaged, source_paths, ct_timeout,
            )

        # 2b: B-Cell v1 (SymPy + z3 + stats — still primary for non-AST claims)
        futures["b_cell"] = pool.submit(b_cell_verify, triaged)

        # 2b': B-Cell v2 AST-grounded z3 (WP6a: now ACTIVE)
        futures["b_cell_v2"] = pool.submit(
            b_cell_v2, triaged, source_paths,
        )

        # 2c: NK v2 (WP6a: now PRIMARY — FP continue fix + intra-round dedup)
        futures["nk_v2"] = pool.submit(
            nk_cell_v2, triaged_for_nk, prior_findings, tau_sim,
            false_positive_db,
        )

        # Collect results — all active cells feed all_verdicts
        for name, future in futures.items():
            try:
                result = future.result(timeout=ct_timeout + 30)
                if name == "nk_v2":
                    # NK v2 returns (triaged, verdicts) tuple
                    nk_triaged_result, nk_verdicts = result
                    all_verdicts.extend(nk_verdicts)
                    for v in nk_verdicts:
                        tool_usage[v.tool_used] = tool_usage.get(v.tool_used, 0) + 1
                else:
                    cell_verdicts = result
                    all_verdicts.extend(cell_verdicts)
                    for v in cell_verdicts:
                        tool_usage[v.tool_used] = tool_usage.get(v.tool_used, 0) + 1
            except Exception as e:
                # Cell failure is non-fatal — log and continue
                import logging
                logging.getLogger(__name__).warning(
                    "Immune cell %s failed: %s: %s", name, type(e).__name__, e
                )

    timings["parallel_verification"] = round(time.monotonic() - t0, 4)

    # Adopt NK v2's triaged state with duplicate flags if available
    if nk_triaged_result is not None:
        triaged = nk_triaged_result

    # ── Stage 2.5: Formalisation Agent shadow (WP3d) ─────────────────
    # Extracts preconditions, logs whether B-Cell false rejections
    # could have been prevented by preserving context
    t0_formal = time.monotonic()
    try:
        formalisation_results = formalisation_agent(triaged, all_verdicts)
    except Exception as e:
        _shadow_log.warning("Formalisation agent failed: %s", e)
        formalisation_results = []
    timings["formalisation"] = round(time.monotonic() - t0_formal, 4)

    # ── Stage 3a: Helper T v1 synthesis (kept for reconciliation) ────
    t0 = time.monotonic()
    final_verdicts, final_confidences = helper_t_cell_synthesize(triaged, all_verdicts)
    timings["helper_t"] = round(time.monotonic() - t0, 4)

    # ── Stage 3a': Helper T v2 synthesis (WP6a: active) ──────────────
    t0 = time.monotonic()
    v2_final, v2_conf = helper_t_v2(triaged, all_verdicts)
    timings["helper_t_v2"] = round(time.monotonic() - t0, 4)

    # ── Stage 3a.5: RECONCILIATION GATE (WP3b) ──────────────────────
    # Immutable state transition check: once a finding is rejected/confirmed
    # by both v1 and v2, that verdict is locked. Prevents autoimmune recovery
    # from rescuing known garbage (MF-34/MF-35/C5-25).
    t0 = time.monotonic()
    reconciled_verdicts, reconciled_confidences, locked_ids = _reconciliation_gate(
        final_verdicts, final_confidences, v2_final, v2_conf,
    )
    timings["reconciliation_gate"] = round(time.monotonic() - t0, 4)
    if locked_ids:
        _shadow_log.info(
            "Reconciliation locked %d finding(s): %s",
            len(locked_ids), ", ".join(sorted(locked_ids)),
        )

    # Use reconciled verdicts for downstream processing
    final_verdicts = reconciled_verdicts
    final_confidences = reconciled_confidences

    # ── Stage 3b: Regulatory T-Cell meta-check (WP6a: v2 primary) ────
    t0 = time.monotonic()
    v1_autoimmune, v1_reg_reason = regulatory_t_cell_check(
        final_verdicts, triaged, max_rejection_rate,
    )
    v2_autoimmune, v2_reg_reason = regulatory_t_v2(
        final_verdicts, triaged, max_rejection_rate,
    )
    # WP6a: v2 is primary, v1 for comparison logging
    autoimmune_flag = v2_autoimmune
    reg_reason = v2_reg_reason
    timings["regulatory_t"] = round(time.monotonic() - t0, 4)

    if v2_autoimmune != v1_autoimmune:
        _shadow_log.info(
            "RT v1 vs v2: flag differs — v1=%s v2=%s (%s)",
            v1_autoimmune, v2_autoimmune, v2_reg_reason,
        )

    # ── Build response ────────────────────────────────────────────────
    filtered: List[Finding] = []
    rejected: List[Finding] = []

    for tf in triaged:
        fid = tf.finding.finding_id
        verdict = final_verdicts.get(fid, "UNCERTAIN")

        if observation_only:
            # Observation mode: everything passes through
            filtered.append(tf.finding)
        elif verdict in ("CONFIRMED", "UNCERTAIN"):
            filtered.append(tf.finding)
        else:
            rejected.append(tf.finding)

    # If autoimmune flagged, override immune-stage rejections only.
    # Bug#56 fix: barrier rejections are deterministic and survive autoimmune override.
    # E31-02 fix: locked_ids (mutual rejection by both pipelines) are excluded
    # from autoimmune resurrection. The reconciliation gate documents these as
    # "LOCKED — cannot be overridden" and this now enforces it.
    if autoimmune_flag and not observation_only:
        filtered = [
            tf.finding for tf in triaged
            if tf.finding.finding_id not in locked_ids
        ]
        rejected = list(barrier_rejected) + [
            tf.finding for tf in triaged
            if tf.finding.finding_id in locked_ids
        ]
        if locked_ids:
            _shadow_log.info(
                "Autoimmune override: resurrected %d findings, kept %d locked rejections",
                len(filtered), len(locked_ids),
            )

    # ── Stage 4: Programmatic fix verification ───────────────────────
    # For surviving findings with proposed fixes, evaluate the fix in a
    # sandbox (pyright/ruff/bandit before/after). If the fix is SAFE or
    # NEUTRAL, mark finding.verified = True. This enables the bug-closed
    # gate in subsequent rounds: first verified fix wins, bug closed.
    t0_fix_eval = time.monotonic()
    fix_candidates = [f for f in filtered if f.proposed_fix.strip()]
    fix_eval_results: List = []
    if fix_candidates and source_paths:
        try:
            from bench.endocrine import evaluate_fixes
            fix_eval_results = evaluate_fixes(
                fix_candidates, source_paths,
                test_cmd=["python3", "-m", "pytest", "bench/tests/", "-x", "-q",
                          "--tb=no", "--no-header", "-q"],
                max_evals=20,
            )
            for ev in fix_eval_results:
                if ev.verdict in ("SAFE", "NEUTRAL"):
                    # Mark the finding as verified — its fix passed programmatic checks
                    for f in filtered:
                        if f.finding_id == ev.finding_id:
                            object.__setattr__(f, 'verified', True)
                            break
                    _shadow_log.info(
                        "Fix VERIFIED (programmatic): %s — verdict=%s",
                        ev.finding_id, ev.verdict,
                    )
                else:
                    _shadow_log.info(
                        "Fix NOT verified: %s — verdict=%s (%s)",
                        ev.finding_id, ev.verdict, ev.apply_error or "issues introduced",
                    )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                "Fix evaluation stage failed (non-fatal): %s", e
            )
    timings["fix_evaluation"] = round(time.monotonic() - t0_fix_eval, 4)

    # ── Stage 5: Auto-escalation ─────────────────────────────────────
    # Findings that survived the pipeline but have NO proposed fix AND
    # match a prior finding (same bug seen before, still no fix) are
    # auto-escalated to the HIL. They're listed but don't count toward
    # novelty or convergence. Models are told "do not attempt to fix."
    escalated_count = 0
    for f in filtered:
        if f.proposed_fix.strip() or f.verified or f.escalated:
            continue  # Has a fix, is verified, or already escalated — skip
        # Check if this bug was seen in a prior round with no fix
        for pf in prior_findings:
            if _finding_similarity(f, pf) >= tau_sim:
                if not pf.proposed_fix.strip() and not pf.verified:
                    # Same bug, seen before, still no fix → escalate
                    object.__setattr__(f, 'escalated', True)
                    escalated_count += 1
                    _shadow_log.info(
                        "Auto-ESCALATED to HIL: %s (matches %s, no fix after 2+ rounds)",
                        f.finding_id, pf.finding_id,
                    )
                    break
    if escalated_count:
        _shadow_log.info("Auto-escalated %d findings to HIL (no programmatic fix)", escalated_count)

    # ── Stage 5.5: B-Cell UNCERTAIN → HIL escalation ─────────────────
    # If the B Cell returned UNCERTAIN for a finding, the system cannot
    # programmatically confirm the claim exists in the code. UNCERTAIN
    # is measured ignorance — not noise, but signal that a human must
    # review. Escalate these to the HIL rather than letting them churn
    # across rounds as unresolvable ambiguity.
    uncertain_escalated = 0
    for f in filtered:
        if f.verified or f.escalated:
            continue  # Already resolved or already escalated
        fid = f.finding_id
        f_verdict = final_verdicts.get(fid, "")
        if f_verdict == "UNCERTAIN":
            # Check if any B-Cell verdict for this finding was UNCERTAIN
            b_cell_uncertain = any(
                v.cell_type == CellType.B_CELL
                and v.verdict == "UNCERTAIN"
                and v.finding_id == fid
                for v in all_verdicts
            )
            if b_cell_uncertain:
                object.__setattr__(f, 'escalated', True)
                uncertain_escalated += 1
                _shadow_log.info(
                    "UNCERTAIN-ESCALATED to HIL: %s (B-Cell cannot ground claim in source)",
                    fid,
                )
    if uncertain_escalated:
        _shadow_log.info(
            "Escalated %d UNCERTAIN findings to HIL (B-Cell cannot verify)",
            uncertain_escalated,
        )

    # Bug#46 fix: include barrier rejections in rejection rate and rejected list
    total = len(triaged) + len(barrier_rejected)
    rej_count = sum(1 for v in final_verdicts.values() if v in ("REJECTED", "DUPLICATE"))
    total_removed = rej_count + len(barrier_rejected)
    rejection_rate = total_removed / max(total, 1)
    rejected.extend(barrier_rejected)

    # Group verdicts by finding for the response
    verdicts_by_finding: Dict[str, List[CellVerdict]] = {}
    for v in all_verdicts:
        verdicts_by_finding.setdefault(v.finding_id, []).append(v)

    return ImmuneResponse(
        triaged=triaged,
        cell_verdicts=verdicts_by_finding,
        final_verdicts=final_verdicts,
        final_confidences=final_confidences,
        filtered_findings=filtered,
        rejected_findings=rejected,
        rejection_rate=round(rejection_rate, 4),
        autoimmune_flag=autoimmune_flag,
        stage_timings=timings,
        tool_usage=tool_usage,
        observation_only=observation_only,
        barrier_results=barrier_results,
    )
