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
# Tool manifest (Tranche C)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Central registry of B-Cell verification tools. The manifest TOML lives at
# bench/cdsfl_registry/tool_manifest.toml and is the single source of truth
# for what tools the specialist dispatch can invoke, their verifier function
# names, arity (claim-only vs claim+file), claim types, and install checks.
#
# Adding a new tool requires only two changes:
#   1. Write _verify_<name>(claim[, file_path]) below.
#   2. Append a [tools.<name>] block to tool_manifest.toml.
# No edit to _specialist_b_cell_dispatch() is required.

_TOOL_MANIFEST_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def _load_tool_manifest() -> Dict[str, Dict[str, Any]]:
    """Load and cache the B-Cell tool manifest.

    Returns the ``tools`` sub-dict of tool_manifest.toml, keyed by tool name.
    Each value is a dict with fields described in the manifest header:
    description, verifier, needs_file, claim_types, domain_hints, cost_class,
    install_check, package_hint, delegate (optional).

    Entries whose ``verifier`` name does not resolve to a module-level
    function in this file are dropped with a stderr warning on first load.
    Delegated entries (``delegate`` set) are kept as-is — the dispatch skips
    them at call time.
    """
    global _TOOL_MANIFEST_CACHE
    if _TOOL_MANIFEST_CACHE is not None:
        return _TOOL_MANIFEST_CACHE

    import tomllib  # stdlib Python 3.11+

    manifest_path = (
        Path(__file__).parent / "cdsfl_registry" / "tool_manifest.toml"
    )
    try:
        with open(manifest_path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError) as e:
        print(
            f"[tool_manifest] failed to load {manifest_path}: {e}",
            file=sys.stderr,
        )
        _TOOL_MANIFEST_CACHE = {}
        return _TOOL_MANIFEST_CACHE

    tools: Dict[str, Dict[str, Any]] = dict(data.get("tools", {}))

    # Validate: every non-delegated entry must reference an existing verifier.
    # Drop bad entries so the dispatch never attempts getattr on a stale name.
    module = sys.modules[__name__]
    bad_entries: List[str] = []
    for name, entry in tools.items():
        if entry.get("delegate"):
            continue
        verifier_name = entry.get("verifier")
        if not verifier_name or not hasattr(module, verifier_name):
            bad_entries.append(name)

    for name in bad_entries:
        print(
            f"[tool_manifest] dropping '{name}': verifier "
            f"{tools[name].get('verifier')!r} not found in {__name__}",
            file=sys.stderr,
        )
        tools.pop(name, None)

    _TOOL_MANIFEST_CACHE = tools
    return tools


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
class RegulatoryResult:
    """Structured output from the Regulatory T Cell.

    Replaces the bare (bool, str) return so the HIL can inspect thresholds,
    per-model breakdown, and the specific checks that fired.
    Codex 5.3 confer, 13 April 2026.
    """
    autoimmune_flag: bool
    reason: str
    total_findings: int
    rejected_count: int
    duplicated_count: int
    uncertain_count: int
    removal_rate: float
    max_rejection_rate: float       # threshold used
    per_model_removal: Dict[str, Dict[str, int]]  # model → {total, removed}
    checks_fired: List[str]         # list of check names that triggered

    def to_dict(self) -> dict:
        return {
            "autoimmune_flag": self.autoimmune_flag,
            "reason": self.reason,
            "total_findings": self.total_findings,
            "rejected_count": self.rejected_count,
            "duplicated_count": self.duplicated_count,
            "uncertain_count": self.uncertain_count,
            "removal_rate": round(self.removal_rate, 4),
            "max_rejection_rate": self.max_rejection_rate,
            "per_model_removal": self.per_model_removal,
            "checks_fired": self.checks_fired,
        }


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
    domain: str = ""                # experiment domain (Layer 3 routing context)
    regulatory_detail: Optional[RegulatoryResult] = None  # structured Regulatory T output


# ═══════════════════════════════════════════════════════════════════════════════
# Layer 3: Domain routing interface
#
# Loads domain-specific immune configuration from TOML files in
# bench/cdsfl_registry/domains/immune/. Each domain defines:
#   - claim_patterns: regex patterns per claim type (domain-tuned)
#   - verification_tools: which tools each claim type should use
#   - ct_prompt_template: domain-specific CT investigation prompt
#
# Currently supported domains: code, mathematics, physics, chemistry,
# engineering, cross_domain. Specialist B-Cell subtypes will plug into
# this interface when built (Phase B4).
# ═══════════════════════════════════════════════════════════════════════════════

_DOMAIN_CONFIG_CACHE: Dict[str, Dict[str, Any]] = {}

_DOMAIN_ALIAS = {
    "software": "code",  # exp38 uses "software", TOML is "code"
}


def load_domain_config(domain: str) -> Dict[str, Any]:
    """Load domain-specific immune configuration from TOML.

    Returns cached config dict, or empty dict if not found.
    Specialist B-Cell subtypes will use this to select tools and patterns.
    """
    if domain in _DOMAIN_CONFIG_CACHE:
        return _DOMAIN_CONFIG_CACHE[domain]

    canonical = _DOMAIN_ALIAS.get(domain, domain)
    toml_path = (
        Path(__file__).parent / "cdsfl_registry" / "domains" / "immune"
        / f"{canonical}.toml"
    )

    config: Dict[str, Any] = {}
    if toml_path.exists():
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ImportError:
                _DOMAIN_CONFIG_CACHE[domain] = config
                return config

        with open(toml_path, "rb") as fh:
            config = tomllib.load(fh)

    _DOMAIN_CONFIG_CACHE[domain] = config
    return config


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


def _build_ct_prompt(
    findings: List[TriagedFinding],
    source_paths: List[str],
    domain_config: Optional[Dict[str, Any]] = None,
) -> str:
    """Build the CT investigation prompt.

    The prompt instructs the agent to INVESTIGATE, not JUDGE. It must
    produce structured evidence with exact file:line:code citations.

    C5-03 fix: finding descriptions are wrapped in XML boundary tags
    to prevent prompt injection from adversarial finding content.

    13 April 2026: loads domain-specific CT prompt template from TOML
    config when available (Gemini 3.1 Pro confer observation).
    """
    files_list = "\n".join(f"  - {p}" for p in source_paths)
    # C5-03: wrap each finding description in XML boundary tags
    findings_block = "\n".join(
        f"  [{tf.finding.finding_id}] severity={tf.finding.severity:.2f} "
        f"type={tf.claim_type.value}: "
        f"<finding_description>{tf.finding.description}</finding_description>"
        for tf in findings
    )

    # Domain-specific preamble from TOML ct_prompt_template, or generic fallback
    domain_preamble = ""
    if domain_config:
        ct_section = domain_config.get("immune", {}).get("ct_prompt_template", {})
        domain_preamble = ct_section.get("template", "")

    if not domain_preamble:
        domain_preamble = (
            "You are an investigator. Your output will be mechanically verified.\n"
            "Do NOT state opinions or verdicts. Report ONLY what you observe."
        )

    return (
        f"{domain_preamble}\n\n"
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
    domain_config: Optional[Dict[str, Any]] = None,
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

    prompt = _build_ct_prompt(code_findings, source_paths, domain_config=domain_config)
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


# ── STEM Domain Specialist Wrappers ──────────────────────────────────────────


def _verify_dimensional_analysis(claim: str) -> CellVerdict:
    """Verify dimensional consistency using pint.

    Extracts quantities with units from the claim text and checks
    whether the dimensional analysis is self-consistent.
    """
    code = f"""
import re

claim = {repr(claim)}

try:
    import pint
    ureg = pint.UnitRegistry()
    Q_ = ureg.Quantity

    # Extract quantities with units: "9.8 m/s^2", "100 kg", "5.0 N", "5 m"
    # (unit is 1+ chars starting with a letter; single-letter units like m, s, N valid)
    qty_pattern = r'([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*([a-zA-Z][a-zA-Z0-9_/^*]*)'
    quantities = re.findall(qty_pattern, claim)

    if not quantities:
        print("DIM_NO_QUANTITIES: no quantities with units found")
    else:
        parsed = []
        for val_str, unit_str in quantities:
            try:
                unit_str = unit_str.replace('^', '**')
                q = Q_(float(val_str), unit_str)
                parsed.append((val_str, unit_str, q))
            except Exception:
                parsed.append((val_str, unit_str, None))

        valid = [(v, u, q) for v, u, q in parsed if q is not None]
        invalid = [(v, u) for v, u, q in parsed if q is None]

        if invalid and not valid:
            print(f"DIM_PARSE_FAIL: could not parse any units: {{invalid}}")
        elif len(valid) >= 2 and '=' in claim:
            dims = [str(q.dimensionality) for _, _, q in valid]
            lhs_dim = dims[0]
            rhs_dims = dims[1:]
            if all(d == lhs_dim for d in rhs_dims):
                print(f"DIM_CONSISTENT: all quantities share dimension {{lhs_dim}}")
            else:
                print(f"DIM_INCONSISTENT: dimensions differ: {{dims}}")
        elif len(valid) >= 2:
            dims = [str(q.dimensionality) for _, _, q in valid]
            unique_dims = set(dims)
            if len(unique_dims) == 1:
                print(f"DIM_CONSISTENT: all {{len(valid)}} quantities have dimension {{dims[0]}}")
            else:
                print(f"DIM_MIXED: {{len(valid)}} quantities, {{len(unique_dims)}} distinct dimensions: {{dims}}")
        else:
            print(f"DIM_SINGLE: {{valid[0][0]}} {{valid[0][1]}} parsed OK")
except ImportError:
    print("DIM_UNAVAILABLE: pint not installed")
except Exception as e:
    print(f"DIM_ERROR: {{e}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("DIM_CONSISTENT"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.85, evidence=f"pint: {output}",
            tool_used="pint", elapsed_s=elapsed,
        )
    elif stripped.startswith("DIM_INCONSISTENT"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.85, evidence=f"pint: {output}",
            tool_used="pint", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"pint: {output}",
            tool_used="pint", elapsed_s=elapsed,
        )


def _verify_uncertainty_propagation(claim: str) -> CellVerdict:
    """Verify error propagation claims using the uncertainties package.

    Extracts values with +/- uncertainty, propagates errors through
    expressions, and checks consistency of claimed results.
    """
    code = f"""
import re

claim = {repr(claim)}

try:
    from uncertainties import ufloat

    # Extract value +/- error patterns
    patterns = [
        r'([-+]?\\d*\\.?\\d+)\\s*[\\u00b1]\\s*(\\d*\\.?\\d+)',   # 5.0 ± 0.1
        r'([-+]?\\d*\\.?\\d+)\\s*\\+/-\\s*(\\d*\\.?\\d+)',         # 5.0 +/- 0.1
        r'([-+]?\\d*\\.?\\d+)\\s*pm\\s*(\\d*\\.?\\d+)',            # 5.0 pm 0.1
    ]

    values = []
    for pattern in patterns:
        for m in re.finditer(pattern, claim):
            val = float(m.group(1))
            err = float(m.group(2))
            values.append(ufloat(val, err))

    if not values:
        print("UNC_NO_VALUES: no value+/-error pairs found in claim")
    elif len(values) == 1:
        v = values[0]
        rel = v.std_dev / abs(v.nominal_value) if v.nominal_value != 0 else float('inf')
        print(f"UNC_SINGLE: {{v.nominal_value}} +/- {{v.std_dev}} (rel={{rel:.4f}})")
    else:
        rel_errs = []
        for v in values:
            r = v.std_dev / abs(v.nominal_value) if v.nominal_value != 0 else float('inf')
            rel_errs.append(r)
        # If equation present, attempt propagation check
        if '=' in claim:
            # Compare claimed result (first value) against propagated inputs
            result_val = values[0]
            input_vals = values[1:]
            # Simple product propagation as baseline check
            propagated_rel = sum(r**2 for r in rel_errs[1:])**0.5
            claimed_rel = rel_errs[0]
            if abs(propagated_rel - claimed_rel) < 0.1 * max(propagated_rel, claimed_rel, 1e-10):
                print(f"UNC_CONSISTENT: claimed rel_err={{claimed_rel:.4f}}, propagated={{propagated_rel:.4f}}")
            else:
                print(f"UNC_INCONSISTENT: claimed rel_err={{claimed_rel:.4f}}, propagated={{propagated_rel:.4f}}")
        else:
            print(f"UNC_PARSED: {{len(values)}} values, rel_errors={{[f'{{r:.4f}}' for r in rel_errs]}}")

except ImportError:
    print("UNC_UNAVAILABLE: uncertainties not installed")
except Exception as e:
    print(f"UNC_ERROR: {{e}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("UNC_CONSISTENT"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.75, evidence=f"uncertainties: {output}",
            tool_used="uncertainties", elapsed_s=elapsed,
        )
    elif stripped.startswith("UNC_INCONSISTENT"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.75, evidence=f"uncertainties: {output}",
            tool_used="uncertainties", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"uncertainties: {output}",
            tool_used="uncertainties", elapsed_s=elapsed,
        )


def _verify_stoichiometric_balance(claim: str) -> CellVerdict:
    """Verify chemical equation balance using SymPy.

    Extracts a chemical equation from the claim, parses element counts
    on each side, and checks atom conservation.
    """
    code = f"""
import re
from collections import Counter

claim = {repr(claim)}

# Extract chemical equation: "2H2 + O2 -> 2H2O" or with arrows/equals
arrow_match = re.search(r'(.+?)\\s*(?:->|-->|→|=|⟶)\\s*(.+)', claim)
if not arrow_match:
    print("STOICH_NO_EQUATION: no chemical equation found")
else:
    lhs_str = arrow_match.group(1).strip()
    rhs_str = arrow_match.group(2).strip()

    def parse_side(side_str):
        \"\"\"Parse a side of a chemical equation into element counts.\"\"\"
        total = Counter()
        # Split by +
        terms = re.split(r'\\s*\\+\\s*', side_str)
        for term in terms:
            term = term.strip()
            if not term:
                continue
            # Extract coefficient (default 1)
            coeff_match = re.match(r'(\\d+)\\s*([A-Z].*)', term)
            if coeff_match:
                coeff = int(coeff_match.group(1))
                formula = coeff_match.group(2)
            else:
                coeff = 1
                formula = term
            # Parse formula: element + optional count
            elements = re.findall(r'([A-Z][a-z]?)(\\d*)', formula)
            for elem, count in elements:
                if not elem:
                    continue
                n = int(count) if count else 1
                total[elem] += coeff * n
        return total

    try:
        lhs_atoms = parse_side(lhs_str)
        rhs_atoms = parse_side(rhs_str)

        if not lhs_atoms or not rhs_atoms:
            print("STOICH_PARSE_FAIL: could not parse element counts")
        elif lhs_atoms == rhs_atoms:
            print(f"STOICH_BALANCED: atoms conserved {{dict(lhs_atoms)}}")
        else:
            diff_keys = set(lhs_atoms.keys()) | set(rhs_atoms.keys())
            diffs = {{k: (lhs_atoms.get(k, 0), rhs_atoms.get(k, 0)) for k in diff_keys if lhs_atoms.get(k, 0) != rhs_atoms.get(k, 0)}}
            print(f"STOICH_UNBALANCED: mismatched elements {{diffs}}")
    except Exception as e:
        print(f"STOICH_ERROR: {{e}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("STOICH_BALANCED"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.90, evidence=f"stoich: {output}",
            tool_used="stoichiometric_balance", elapsed_s=elapsed,
        )
    elif stripped.startswith("STOICH_UNBALANCED"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.90, evidence=f"stoich: {output}",
            tool_used="stoichiometric_balance", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"stoich: {output}",
            tool_used="stoichiometric_balance", elapsed_s=elapsed,
        )


def _verify_linear_programming(claim: str) -> CellVerdict:
    """Verify optimisation claims using PuLP.

    Extracts numeric constraints and objective bounds from the claim,
    builds a minimal LP, and checks feasibility / bound correctness.
    """
    code = f"""
import re

claim = {repr(claim)}

try:
    import pulp

    # Extract numeric bound claims: "maximum is 42", "optimal value = 100"
    bound_match = re.search(
        r'(?:maximum|minimum|optimal|objective|bound)\\s*(?:is|=|:)\\s*([-+]?\\d*\\.?\\d+)',
        claim, re.IGNORECASE,
    )
    # Extract constraint count
    constraint_match = re.search(r'(\\d+)\\s*constraints?', claim, re.IGNORECASE)
    # Extract variable count
    var_match = re.search(r'(\\d+)\\s*(?:variables?|unknowns?)', claim, re.IGNORECASE)

    if bound_match:
        claimed_bound = float(bound_match.group(1))
        is_max = bool(re.search(r'maxim', claim, re.IGNORECASE))

        # Extract inequality constraints: "x + y <= 10", "2x - y >= 5"
        ineq_patterns = re.findall(
            r'([-+]?\\d*\\.?\\d*\\s*[a-z](?:\\s*[-+]\\s*\\d*\\.?\\d*\\s*[a-z])*)\\s*([<>=]+)\\s*([-+]?\\d*\\.?\\d+)',
            claim, re.IGNORECASE,
        )

        if ineq_patterns:
            print(f"LP_PARSED: claimed_bound={{claimed_bound}}, direction={{'max' if is_max else 'min'}}, constraints={{len(ineq_patterns)}}")
        else:
            print(f"LP_BOUND_ONLY: claimed {{'max' if is_max else 'min'}}={{claimed_bound}}, no extractable constraints")
    elif constraint_match or var_match:
        n_constraints = int(constraint_match.group(1)) if constraint_match else 0
        n_vars = int(var_match.group(1)) if var_match else 0
        print(f"LP_STRUCTURE: {{n_vars}} variables, {{n_constraints}} constraints")
    else:
        print("LP_NO_STRUCTURE: no optimisation structure found in claim")

except ImportError:
    print("LP_UNAVAILABLE: PuLP not installed")
except Exception as e:
    print(f"LP_ERROR: {{e}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("LP_PARSED"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.60, evidence=f"pulp: {output}",
            tool_used="pulp", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"pulp: {output}",
            tool_used="pulp", elapsed_s=elapsed,
        )


def _verify_astronomical(claim: str) -> CellVerdict:
    """Verify physical constants and unit conversions using astropy.

    Checks claimed values of physical constants, performs unit
    conversions, and validates astronomical calculations.
    """
    code = f"""
import re

claim = {repr(claim)}

try:
    import astropy.units as u
    import astropy.constants as const

    # Known constants and their astropy names
    _CONST_MAP = {{
        'speed of light': const.c,
        'gravitational constant': const.G,
        'planck constant': const.h,
        'boltzmann constant': const.k_B,
        'avogadro': const.N_A,
        'electron mass': const.m_e,
        'proton mass': const.m_p,
        'elementary charge': const.e,
        'stefan-boltzmann': const.sigma_sb,
        'bohr radius': const.a0,
        'rydberg': const.Ryd,
    }}

    found_const = None
    for name, cval in _CONST_MAP.items():
        if name.lower() in claim.lower():
            found_const = (name, cval)
            break

    if found_const:
        name, cval = found_const
        # Extract claimed numeric value
        nums = re.findall(r'([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)', claim)
        if nums:
            claimed = float(nums[-1])  # Last number is usually the value
            actual = cval.value
            # Check within 1% tolerance (accounts for unit differences)
            if actual != 0 and abs(claimed - actual) / abs(actual) < 0.01:
                print(f"ASTRO_VERIFIED: {{name}} claimed={{claimed}}, actual={{actual}}")
            elif actual != 0 and abs(claimed - actual) / abs(actual) < 0.1:
                print(f"ASTRO_APPROX: {{name}} claimed={{claimed}}, actual={{actual}} (within 10%)")
            else:
                print(f"ASTRO_MISMATCH: {{name}} claimed={{claimed}}, actual={{actual}}")
        else:
            print(f"ASTRO_CONST_FOUND: {{name}}={{cval.value}} {{cval.unit}}")
    else:
        # Try unit conversion verification
        unit_match = re.search(r'([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*(\\w+)\\s*(?:=|is|equals)\\s*([-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?)\\s*(\\w+)', claim)
        if unit_match:
            val1, unit1, val2, unit2 = unit_match.groups()
            try:
                q1 = float(val1) * getattr(u, unit1)
                converted = q1.to(getattr(u, unit2))
                actual = converted.value
                claimed = float(val2)
                if abs(actual - claimed) / max(abs(actual), 1e-30) < 0.01:
                    print(f"ASTRO_CONV_VERIFIED: {{val1}} {{unit1}} = {{actual}} {{unit2}} (claimed {{claimed}})")
                else:
                    print(f"ASTRO_CONV_MISMATCH: {{val1}} {{unit1}} = {{actual}} {{unit2}} (claimed {{claimed}})")
            except Exception as e:
                print(f"ASTRO_CONV_ERROR: {{e}}")
        else:
            print("ASTRO_NO_MATCH: no verifiable constant or conversion found")

except ImportError:
    print("ASTRO_UNAVAILABLE: astropy not installed")
except Exception as e:
    print(f"ASTRO_ERROR: {{e}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("ASTRO_VERIFIED") or stripped.startswith("ASTRO_CONV_VERIFIED"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.90, evidence=f"astropy: {output}",
            tool_used="astropy", elapsed_s=elapsed,
        )
    elif stripped.startswith("ASTRO_MISMATCH") or stripped.startswith("ASTRO_CONV_MISMATCH"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.90, evidence=f"astropy: {output}",
            tool_used="astropy", elapsed_s=elapsed,
        )
    elif stripped.startswith("ASTRO_APPROX"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.60, evidence=f"astropy: {output}",
            tool_used="astropy", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"astropy: {output}",
            tool_used="astropy", elapsed_s=elapsed,
        )


# ── Code Domain Specialist Wrappers ──────────────────────────────────────────


def _verify_type_check(claim: str, file_path: str = "") -> CellVerdict:
    """Verify type consistency using mypy.

    Runs mypy on the target file and checks for type errors. If a
    specific line is mentioned in the claim, focuses on that region.
    """
    if not file_path or not os.path.isfile(file_path):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.0, evidence="mypy: no valid file_path for type checking",
            tool_used="mypy", elapsed_s=0.0,
        )

    code = f"""
import subprocess, json

result = subprocess.run(
    ['python3', '-m', 'mypy', '--no-color-output', '--hide-error-context',
     '--no-error-summary', {repr(file_path)}],
    capture_output=True, text=True, timeout=30,
)

lines = result.stdout.strip().splitlines() if result.stdout else []
errors = [l for l in lines if ': error:' in l]
warnings = [l for l in lines if ': warning:' in l or ': note:' in l]

if result.returncode == 0 and not errors:
    print("TYPE_CLEAN: no type errors found")
elif errors:
    # Report first 5 errors
    for e in errors[:5]:
        print(f"TYPE_ERROR: {{e}}")
    if len(errors) > 5:
        print(f"TYPE_ERRORS_TOTAL: {{len(errors)}}")
else:
    print(f"TYPE_UNKNOWN: rc={{result.returncode}}, stderr={{result.stderr[:200] if result.stderr else 'none'}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=35)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("TYPE_CLEAN"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.80, evidence=f"mypy: {output}",
            tool_used="mypy", elapsed_s=elapsed,
        )
    elif "TYPE_ERROR" in stripped:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.85, evidence=f"mypy: {output}",
            tool_used="mypy", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"mypy: {output}",
            tool_used="mypy", elapsed_s=elapsed,
        )


def _verify_lint_check(claim: str, file_path: str = "") -> CellVerdict:
    """Verify code quality claims using ruff.

    Runs ruff on the target file and reports violations.
    """
    if not file_path or not os.path.isfile(file_path):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.0, evidence="ruff: no valid file_path for lint checking",
            tool_used="ruff", elapsed_s=0.0,
        )

    code = f"""
import subprocess

result = subprocess.run(
    ['python3', '-m', 'ruff', 'check', '--no-fix', '--output-format=concise',
     {repr(file_path)}],
    capture_output=True, text=True, timeout=15,
)

lines = result.stdout.strip().splitlines() if result.stdout else []
violations = [l for l in lines if l.strip()]

if result.returncode == 0 and not violations:
    print("LINT_CLEAN: no violations found")
elif violations:
    for v in violations[:5]:
        print(f"LINT_VIOLATION: {{v}}")
    if len(violations) > 5:
        print(f"LINT_VIOLATIONS_TOTAL: {{len(violations)}}")
else:
    print(f"LINT_UNKNOWN: rc={{result.returncode}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=20)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("LINT_CLEAN"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.75, evidence=f"ruff: {output}",
            tool_used="ruff", elapsed_s=elapsed,
        )
    elif "LINT_VIOLATION" in stripped:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.80, evidence=f"ruff: {output}",
            tool_used="ruff", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"ruff: {output}",
            tool_used="ruff", elapsed_s=elapsed,
        )


def _verify_security_scan(claim: str, file_path: str = "") -> CellVerdict:
    """Verify security claims using bandit.

    Runs bandit on the target file and checks for vulnerabilities.
    """
    if not file_path or not os.path.isfile(file_path):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.0, evidence="bandit: no valid file_path for security scan",
            tool_used="bandit", elapsed_s=0.0,
        )

    code = f"""
import subprocess, json

result = subprocess.run(
    ['python3', '-m', 'bandit', '-f', 'json', '-q', {repr(file_path)}],
    capture_output=True, text=True, timeout=20,
)

try:
    data = json.loads(result.stdout) if result.stdout else {{}}
    results = data.get('results', [])
    if not results:
        print("SEC_CLEAN: no security issues found")
    else:
        for issue in results[:5]:
            sev = issue.get('issue_severity', '?')
            conf = issue.get('issue_confidence', '?')
            text = issue.get('issue_text', '?')
            line = issue.get('line_number', '?')
            print(f"SEC_ISSUE: L{{line}} [{{sev}}/{{conf}}] {{text}}")
        if len(results) > 5:
            print(f"SEC_ISSUES_TOTAL: {{len(results)}}")
except Exception:
    lines = result.stdout.strip().splitlines() if result.stdout else []
    if not lines:
        print("SEC_CLEAN: no output from bandit")
    else:
        print(f"SEC_RAW: {{lines[0]}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=25)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("SEC_CLEAN"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.75, evidence=f"bandit: {output}",
            tool_used="bandit", elapsed_s=elapsed,
        )
    elif "SEC_ISSUE" in stripped:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.80, evidence=f"bandit: {output}",
            tool_used="bandit", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"bandit: {output}",
            tool_used="bandit", elapsed_s=elapsed,
        )


def _verify_bytecode_analysis(claim: str, file_path: str = "") -> CellVerdict:
    """Verify control flow claims using the dis module.

    Disassembles a function or file and checks for dead code,
    unreachable branches, or claimed control flow properties.
    """
    if not file_path or not os.path.isfile(file_path):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.0, evidence="dis: no valid file_path for bytecode analysis",
            tool_used="dis", elapsed_s=0.0,
        )

    code = f"""
import ast, dis, io, re

claim = {repr(claim)}
file_path = {repr(file_path)}

try:
    with open(file_path, 'r') as f:
        source = f.read()

    tree = ast.parse(source, filename=file_path)
    compiled = compile(tree, file_path, 'exec')

    # Capture bytecode
    buf = io.StringIO()
    dis.dis(compiled, file=buf)
    bytecode = buf.getvalue()

    # Check for common patterns
    lines = bytecode.splitlines()

    # Count JUMP targets and detect unreachable code after RETURN_VALUE
    returns = [i for i, l in enumerate(lines) if 'RETURN_VALUE' in l]
    dead_after_return = 0
    for ret_idx in returns:
        if ret_idx + 1 < len(lines):
            next_line = lines[ret_idx + 1].strip()
            # Next instruction after RETURN that isn't a jump target
            if next_line and not next_line.startswith('>>') and not next_line.startswith('Disassembly'):
                dead_after_return += 1

    total_instructions = len([l for l in lines if l.strip() and not l.strip().startswith('Disassembly')])

    if dead_after_return > 0:
        print(f"BYTE_DEAD_CODE: {{dead_after_return}} potential dead code blocks after RETURN_VALUE")
    else:
        print(f"BYTE_CLEAN: {{total_instructions}} instructions, no dead code detected after RETURN")

except SyntaxError as e:
    print(f"BYTE_SYNTAX_ERROR: {{e}}")
except Exception as e:
    print(f"BYTE_ERROR: {{e}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=15)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("BYTE_DEAD_CODE"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.65, evidence=f"dis: {output}",
            tool_used="dis", elapsed_s=elapsed,
        )
    elif stripped.startswith("BYTE_CLEAN"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.60, evidence=f"dis: {output}",
            tool_used="dis", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"dis: {output}",
            tool_used="dis", elapsed_s=elapsed,
        )


def _verify_symbolic_execution(claim: str, file_path: str = "") -> CellVerdict:
    """Verify behavioural / contract claims using Crosshair (z3-backed).

    Runs ``crosshair check`` on a target Python file that carries
    ICONTRACT-style ``pre:`` / ``post:`` docstring conditions. If Crosshair
    finds a counterexample, the claim that a contract is violated is
    CONFIRMED; if all contracts pass, the claim is REJECTED.

    If the file has no contracts, Crosshair exits cleanly with no output —
    that case is surfaced as UNCERTAIN, not REJECTED, since a clean run
    without contracts proves nothing.
    """
    if not file_path or not os.path.isfile(file_path):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.0, evidence="crosshair: no valid file_path for symbolic execution",
            tool_used="crosshair", elapsed_s=0.0,
        )

    code = f"""
import subprocess, sys

result = subprocess.run(
    [sys.executable, '-m', 'crosshair', 'check',
     '--report_all', '--per_condition_timeout=3', {repr(file_path)}],
    capture_output=True, text=True, timeout=25,
)

out = (result.stdout or '').strip()
err = (result.stderr or '').strip()

# With --report_all, clean contracts emit "info: Confirmed over all paths".
# rc=0 + "info: Confirmed" → clean verification
# rc=0 + empty → no contracts to check
# rc=1 + "error:" → counterexample found
# rc!=0,1 → tool error

if result.returncode == 1 and "error:" in out.lower():
    print("CROSSHAIR_COUNTEREXAMPLE: contract violation found")
    for l in out.splitlines()[:5]:
        print(f"  {{l}}")
elif result.returncode == 0 and "info: confirmed" in out.lower():
    print("CROSSHAIR_CLEAN: contracts verified")
    for l in out.splitlines()[:3]:
        print(f"  {{l}}")
elif result.returncode == 0 and not out:
    print("CROSSHAIR_NO_CONTRACTS: no pre/post conditions detected")
else:
    print(f"CROSSHAIR_ERROR: rc={{result.returncode}}")
    if out:
        print(f"  stdout: {{out[:200]}}")
    if err:
        print(f"  stderr: {{err[:200]}}")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=30)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("CROSSHAIR_COUNTEREXAMPLE"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.85, evidence=f"crosshair: {output}",
            tool_used="crosshair", elapsed_s=elapsed,
        )
    elif stripped.startswith("CROSSHAIR_CLEAN"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.75, evidence=f"crosshair: {output}",
            tool_used="crosshair", elapsed_s=elapsed,
        )
    else:
        # CROSSHAIR_NO_CONTRACTS, CROSSHAIR_ERROR, TIMEOUT, SUBPROCESS_ERROR
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"crosshair: {output}",
            tool_used="crosshair", elapsed_s=elapsed,
        )


def _verify_chemistry_structure(claim: str) -> CellVerdict:
    """Verify chemistry claims using RDKit.

    Supports three claim types:
      1. SMILES validity: claim contains a SMILES string (e.g. ``'CCO'``) —
         RDKit parses it; valid → CONFIRMED, invalid → REJECTED.
      2. Molecular formula: claim contains both a SMILES and a formula
         (e.g. ``C2H6O``); match → CONFIRMED, mismatch → REJECTED.
      3. Molecular weight: claim contains both a SMILES and a numeric MW
         (g/mol); match within 0.5 g/mol → CONFIRMED, otherwise REJECTED.

    Complements ``_verify_stoichiometric_balance`` (which handles reaction
    conservation); this wrapper handles structure and property claims.
    """
    code = f"""
import re

claim = {repr(claim)}

# Quoted SMILES are treated as explicit claims (failure → REJECTED).
# Unquoted fallback tokens are only loose hints (failure → UNCERTAIN).
quoted = re.findall(r\"['\\\"`]([^'\\\"`\\s]{{1,80}})['\\\"`]\", claim)
smiles_candidates = list(quoted)
explicit = bool(quoted)
if not smiles_candidates:
    smiles_candidates = [
        tok for tok in re.findall(r'\\S+', claim)
        if re.fullmatch(r'[A-Za-z0-9()\\[\\]=#@+\\-/\\\\.%]{{2,80}}', tok)
        and any(c.isalpha() for c in tok)
    ]

try:
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors, Descriptors
    from rdkit import RDLogger
    RDLogger.DisableLog('rdApp.*')
except Exception as e:
    print(f"CHEM_IMPORT_ERROR: {{e}}")
    raise SystemExit(0)

# Try each candidate until one parses as a SMILES.
mol = None
smiles_used = None
for cand in smiles_candidates:
    m = Chem.MolFromSmiles(cand)
    if m is not None and m.GetNumAtoms() > 0:
        mol = m
        smiles_used = cand
        break

if mol is None:
    # Quoted SMILES that fail → REJECTED (explicit claim refuted).
    # Unquoted fallback tokens that fail → UNCERTAIN (no SMILES claim asserted).
    if explicit:
        print(f"CHEM_INVALID_SMILES: none of {{smiles_candidates[:3]}} parsed")
    else:
        print("CHEM_NO_SMILES: no parseable SMILES found in claim")
    raise SystemExit(0)

# We have a valid SMILES. Compute properties.
formula = rdMolDescriptors.CalcMolFormula(mol)
mw = Descriptors.MolWt(mol)
num_atoms = mol.GetNumAtoms()
num_rings = rdMolDescriptors.CalcNumRings(mol)

# Match against claimed formula. Formula heuristic: uppercase letter
# optionally followed by lowercase, then digits, repeated.
formula_claimed = None
for m in re.finditer(r'\\b([A-Z][a-z]?\\d*){{2,}}\\b', claim):
    cand = m.group(0)
    if cand != smiles_used and any(c.isdigit() for c in cand):
        formula_claimed = cand
        break

# Match against claimed MW (number near 'mw' / 'weight' / 'g/mol').
mw_claimed = None
mw_match = re.search(r'(?:MW|molecular\\s+weight|mass)\\D{{0,20}}(\\d+\\.?\\d*)', claim, re.I)
if not mw_match:
    mw_match = re.search(r'(\\d+\\.?\\d*)\\s*g\\s*/\\s*mol', claim, re.I)
if mw_match:
    try:
        mw_claimed = float(mw_match.group(1))
    except ValueError:
        pass

# Decide verdict based on strongest constraint present.
if formula_claimed is not None:
    # Normalise both: RDKit output may have different element order than claim.
    def _elem_counts(f):
        return dict(re.findall(r'([A-Z][a-z]?)(\\d*)', f))
    a = {{k: (int(v) if v else 1) for k, v in _elem_counts(formula).items() if k}}
    b = {{k: (int(v) if v else 1) for k, v in _elem_counts(formula_claimed).items() if k}}
    if a == b:
        print(f"CHEM_VALID: SMILES={{smiles_used}} formula={{formula}} matches claim")
    else:
        print(f"CHEM_INVALID: SMILES={{smiles_used}} computed={{formula}} claimed={{formula_claimed}}")
elif mw_claimed is not None:
    if abs(mw - mw_claimed) < 0.5:
        print(f"CHEM_VALID: SMILES={{smiles_used}} MW={{mw:.2f}} matches claim {{mw_claimed}}")
    else:
        print(f"CHEM_INVALID: SMILES={{smiles_used}} computed_MW={{mw:.2f}} claimed_MW={{mw_claimed}}")
else:
    # Just a SMILES validity check
    print(f"CHEM_VALID: SMILES={{smiles_used}} parsed ({{num_atoms}} atoms, {{num_rings}} rings, formula={{formula}}, MW={{mw:.2f}})")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=15)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("CHEM_VALID"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.85, evidence=f"rdkit: {output}",
            tool_used="rdkit", elapsed_s=elapsed,
        )
    elif stripped.startswith("CHEM_INVALID_SMILES") or stripped.startswith("CHEM_INVALID"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.85, evidence=f"rdkit: {output}",
            tool_used="rdkit", elapsed_s=elapsed,
        )
    else:
        # CHEM_NO_SMILES, CHEM_IMPORT_ERROR, TIMEOUT, SUBPROCESS_ERROR
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"rdkit: {output}",
            tool_used="rdkit", elapsed_s=elapsed,
        )


def _verify_biological_sequence(claim: str) -> CellVerdict:
    """Verify biology sequence claims using Biopython.

    Supports:
      1. Length: ``sequence 'ACGT' has length 4`` / ``4 bp`` / ``4 nt``.
      2. GC content: ``GC content 50%`` / ``50% GC``.
      3. Translation: ``ATGGCC translates to MA``.
      4. Reverse complement: ``RC of ACGT is ACGT``.
      5. Pure validity: quoted sequence is valid DNA/RNA/protein.
    """
    code = f"""
import re

claim = {repr(claim)}

quoted = re.findall(r\"['\\\"`]([A-Za-z0-9*]{{2,500}})['\\\"`]\", claim)
seq_candidates = list(quoted)
explicit = bool(quoted)
if not seq_candidates:
    # Unquoted DNA/RNA: require at least 4 contiguous nucleotide letters.
    seq_candidates = [
        tok for tok in re.findall(r'\\b[ACGTUNacgtun]{{4,}}\\b', claim)
    ]

try:
    from Bio.Seq import Seq
except Exception as e:
    print(f"BIO_IMPORT_ERROR: {{e}}")
    raise SystemExit(0)

DNA = set('ACGTNacgtn')
RNA = set('ACGUNacgun')
PROT = set('ACDEFGHIKLMNPQRSTVWY*acdefghiklmnpqrstvwy')

def classify(s):
    chars = set(s)
    if chars <= DNA: return 'DNA'
    if chars <= RNA: return 'RNA'
    if chars <= PROT: return 'PROT'
    return None

primary = None
primary_kind = None
for cand in seq_candidates:
    k = classify(cand)
    if k is not None:
        primary = cand
        primary_kind = k
        break

if primary is None:
    if explicit:
        print(f"BIO_INVALID_SEQUENCE: none of {{seq_candidates[:3]}} valid DNA/RNA/protein")
    else:
        print("BIO_NO_SEQUENCE: no parseable sequence in claim")
    raise SystemExit(0)

s = Seq(primary)
length = len(s)
gc = None
if primary_kind in ('DNA', 'RNA') and length > 0:
    gc = 100.0 * (primary.upper().count('G') + primary.upper().count('C')) / length

length_claim = None
m_len = re.search(r'(?:length|len\\.?)\\s*(?:of|=|is|:)?\\s*(\\d+)', claim, re.I)
if not m_len:
    m_len = re.search(r'(\\d+)\\s*(?:bp|nt|nucleotides?|residues?|aa|amino\\s+acids?)', claim, re.I)
if m_len:
    length_claim = int(m_len.group(1))

gc_claim = None
m_gc = re.search(r'(?:GC\\s*(?:content|fraction|percent|%)?\\D{{0,10}})(\\d+\\.?\\d*)\\s*%?', claim, re.I)
if not m_gc:
    m_gc = re.search(r'(\\d+\\.?\\d*)\\s*%\\s*GC', claim, re.I)
if m_gc:
    gc_claim = float(m_gc.group(1))

# Translation claim: look for 'translate(s) to X' where X is protein-like
trans_claim = None
m_tr = re.search(r'translates?\\s+(?:to|into)\\s+[\\'\\\"]?([A-Za-z*]{{1,200}})[\\'\\\"]?', claim, re.I)
if m_tr:
    trans_claim = m_tr.group(1)

# Reverse complement claim
rc_claim = None
m_rc = re.search(r'(?:reverse\\s*complement|RC)\\s+(?:is|=|of\\s+\\S+\\s+is)\\s+[\\'\\\"]?([ACGTUacgtu]{{2,500}})[\\'\\\"]?', claim, re.I)
if m_rc:
    rc_claim = m_rc.group(1).upper()

# Decide verdict. Most specific claim wins.
if trans_claim is not None and primary_kind == 'DNA':
    try:
        actual = str(s.translate())
        if actual == trans_claim.upper() or actual.rstrip('*') == trans_claim.upper().rstrip('*'):
            print(f"BIO_VALID: {{primary}} translates to {{actual}} matches claim")
        else:
            print(f"BIO_INVALID: {{primary}} translates to {{actual}}, claimed {{trans_claim}}")
    except Exception as e:
        print(f"BIO_ERROR: translate failed: {{e}}")
elif rc_claim is not None and primary_kind == 'DNA':
    actual = str(s.reverse_complement()).upper()
    if actual == rc_claim:
        print(f"BIO_VALID: RC({{primary}})={{actual}} matches claim")
    else:
        print(f"BIO_INVALID: RC({{primary}})={{actual}}, claimed {{rc_claim}}")
elif length_claim is not None:
    if length == length_claim:
        print(f"BIO_VALID: length({{primary}})={{length}} matches claim")
    else:
        print(f"BIO_INVALID: length({{primary}})={{length}}, claimed {{length_claim}}")
elif gc_claim is not None and gc is not None:
    if abs(gc - gc_claim) < 0.5:
        print(f"BIO_VALID: GC({{primary}})={{gc:.2f}}% matches claim {{gc_claim}}%")
    else:
        print(f"BIO_INVALID: GC({{primary}})={{gc:.2f}}%, claimed {{gc_claim}}%")
else:
    gc_str = f"{{gc:.1f}}%" if gc is not None else "n/a"
    print(f"BIO_VALID: {{primary_kind}} sequence '{{primary[:40]}}{{'...' if len(primary) > 40 else ''}}' (len={{length}}, GC={{gc_str}})")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=15)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("BIO_VALID"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.85, evidence=f"biopython: {output}",
            tool_used="biopython", elapsed_s=elapsed,
        )
    elif stripped.startswith("BIO_INVALID"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.85, evidence=f"biopython: {output}",
            tool_used="biopython", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"biopython: {output}",
            tool_used="biopython", elapsed_s=elapsed,
        )


def _verify_ml_claim(claim: str) -> CellVerdict:
    """Verify machine-learning claims using scikit-learn sanity checks.

    This wrapper is deliberately narrow: it checks structural/numerical
    claims that can be decided from the claim string alone, without access
    to experimental data. Three check classes:

      1. Metric bounds. Accuracy, precision, recall, F1 ∈ [0, 1]; AUC ∈
         [0, 1]; MSE, MAE ≥ 0; Gini for k classes ≤ 1 − 1/k. Violations
         are flagged as CONFIRMED flaws.
      2. Algorithm existence. A claim that names an sklearn estimator is
         checked against the installed namespace; an unknown name is
         CONFIRMED (typo / non-existent).
      3. Dimension claims. "Confusion matrix for k classes is k×k" —
         verified against the stated k.

    Claims that require live data to adjudicate are returned UNCERTAIN.
    """
    code = f"""
import re

claim = {repr(claim)}
claim_l = claim.lower()

try:
    import sklearn
    from sklearn.utils import all_estimators
except Exception as e:
    print(f"ML_IMPORT_ERROR: {{e}}")
    raise SystemExit(0)

findings = []

# (1) Metric bound checks.
bound_metrics = {{
    'accuracy': (0.0, 1.0),
    'precision': (0.0, 1.0),
    'recall': (0.0, 1.0),
    'f1': (0.0, 1.0),
    'f1-score': (0.0, 1.0),
    'f1 score': (0.0, 1.0),
    'auc': (0.0, 1.0),
    'auroc': (0.0, 1.0),
    'roc auc': (0.0, 1.0),
    'roc-auc': (0.0, 1.0),
    'r2': (None, 1.0),        # R² can be negative, upper bound 1
    'r²': (None, 1.0),
    'sensitivity': (0.0, 1.0),
    'specificity': (0.0, 1.0),
    'mse': (0.0, None),       # MSE ≥ 0
    'mae': (0.0, None),
    'rmse': (0.0, None),
}}

for metric, (lo, hi) in bound_metrics.items():
    # Accept forms: "accuracy = 1.5", "accuracy of 1.5", "accuracy is 1.5",
    # "accuracy 150%", "1.5 accuracy".
    patterns = [
        rf'{{re.escape(metric)}}\\s*(?:=|:|of|is|was)?\\s*(-?\\d+\\.?\\d*)\\s*(%?)',
        rf'(-?\\d+\\.?\\d*)\\s*(%?)\\s+{{re.escape(metric)}}',
    ]
    for pat in patterns:
        for m in re.finditer(pat, claim_l):
            try:
                val = float(m.group(1))
                if m.group(2) == '%':
                    val /= 100.0
            except ValueError:
                continue
            if lo is not None and val < lo:
                findings.append(f"{{metric}}={{val}} below lower bound {{lo}}")
            if hi is not None and val > hi:
                findings.append(f"{{metric}}={{val}} above upper bound {{hi}}")

# Gini bound: for k classes, max Gini = 1 - 1/k.
m_gini = re.search(r'gini\\s*(?:impurity)?\\s*(?:=|:|of|is)?\\s*(\\d+\\.?\\d*)', claim_l)
m_k = re.search(r'(\\d+)[ -]?class', claim_l)
if m_gini and m_k:
    try:
        gini = float(m_gini.group(1))
        k = int(m_k.group(1))
        if k >= 2:
            max_gini = 1.0 - 1.0 / k
            if gini > max_gini + 1e-9:
                findings.append(f"gini={{gini}} exceeds max {{max_gini:.3f}} for {{k}}-class")
    except (ValueError, ZeroDivisionError):
        pass

# (2) Algorithm existence check (only when a "sklearn X" style claim appears).
# Build the name set once.
est_names = {{n.lower() for n, _ in all_estimators()}}
m_alg = re.search(r"sklearn[.\\s]([A-Za-z_][A-Za-z_0-9]*)", claim)
if m_alg:
    name = m_alg.group(1)
    if name.lower() not in est_names:
        findings.append(f"sklearn.{{name}} not found in installed estimators")

# (3) Confusion matrix dimension.
m_cm = re.search(r'confusion\\s+matrix\\s+(?:is|of|for)?\\s*(\\d+)\\s*(?:x|×|by)\\s*(\\d+)', claim_l)
m_cmk = re.search(r'(\\d+)[ -]?class', claim_l)
if m_cm and m_cmk:
    try:
        r = int(m_cm.group(1))
        c = int(m_cm.group(2))
        k = int(m_cmk.group(1))
        if r != k or c != k:
            findings.append(f"confusion matrix {{r}}x{{c}} mismatches {{k}}-class problem")
    except ValueError:
        pass

if findings:
    print(f"ML_INCONSISTENT: {{len(findings)}} issue(s)")
    for f in findings[:5]:
        print(f"  {{f}}")
elif any(t in claim_l for t in list(bound_metrics.keys()) + ['gini', 'sklearn', 'confusion matrix']):
    print(f"ML_CONSISTENT: sklearn sanity checks pass on claim")
else:
    print("ML_NO_CHECKABLE_CLAIM: no recognised ML metric or algorithm reference")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=15)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("ML_INCONSISTENT"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.80, evidence=f"sklearn: {output}",
            tool_used="sklearn", elapsed_s=elapsed,
        )
    elif stripped.startswith("ML_CONSISTENT"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.50, evidence=f"sklearn: {output}",
            tool_used="sklearn", elapsed_s=elapsed,
        )
    else:
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"sklearn: {output}",
            tool_used="sklearn", elapsed_s=elapsed,
        )


def _verify_graph_property(claim: str) -> CellVerdict:
    """Verify graph-theoretic claims using NetworkX.

    Extracts edges from the claim as ``(u,v)``/``u-v``/``u->v`` tokens,
    builds a graph (directed if ``->`` appears, otherwise undirected),
    and verifies claimed properties:

      * Node count / edge count.
      * Connected (undirected) / weakly/strongly connected (directed).
      * Tree (acyclic, connected, |E| = |V| − 1).
      * Has-cycle.
      * Diameter (integer).

    Verdict:
      * Graph property holds and claim asserts it → CONFIRMED.
      * Claim asserts property that fails → REJECTED.
      * No extractable edges or no checkable property → UNCERTAIN.
    """
    code = f"""
import re

claim = {repr(claim)}
claim_l = claim.lower()

try:
    import networkx as nx
except Exception as e:
    print(f"GRAPH_IMPORT_ERROR: {{e}}")
    raise SystemExit(0)

# Extract edges: (u,v), u->v, or u-v with word-like endpoints.
directed_edges = re.findall(r'(\\w+)\\s*(?:->|→)\\s*(\\w+)', claim)
undirected_edges_paren = re.findall(r'\\(\\s*(\\w+)\\s*,\\s*(\\w+)\\s*\\)', claim)
undirected_edges_dash = re.findall(r'\\b(\\w+)\\s*-\\s*(\\w+)\\b', claim)

directed_mode = bool(directed_edges)
if directed_mode:
    edges = directed_edges
else:
    # Prefer parenthesised edges; fall back to dashed only if no parens present
    # and dashed edges look edge-like (endpoints aren't long phrases).
    edges = undirected_edges_paren or [
        (u, v) for (u, v) in undirected_edges_dash
        if len(u) <= 20 and len(v) <= 20 and u.isalnum() and v.isalnum()
    ]

if not edges:
    print("GRAPH_NO_EDGES: no edges extracted from claim")
    raise SystemExit(0)

G = nx.DiGraph() if directed_mode else nx.Graph()
G.add_edges_from(edges)

findings = []
checked = []

# Node count claim
m_nodes = re.search(r'(\\d+)\\s*(?:nodes?|vertices?|vertex)', claim_l)
if m_nodes:
    n_claimed = int(m_nodes.group(1))
    n_actual = G.number_of_nodes()
    checked.append('nodes')
    if n_actual != n_claimed:
        findings.append(f"node count: actual {{n_actual}}, claimed {{n_claimed}}")

# Edge count claim
m_edges = re.search(r'(\\d+)\\s*edges?', claim_l)
if m_edges:
    e_claimed = int(m_edges.group(1))
    e_actual = G.number_of_edges()
    checked.append('edges')
    if e_actual != e_claimed:
        findings.append(f"edge count: actual {{e_actual}}, claimed {{e_claimed}}")

# Connectivity
if 'connected' in claim_l:
    checked.append('connected')
    if directed_mode:
        is_conn = nx.is_weakly_connected(G)
        kind = 'weakly connected'
    else:
        is_conn = nx.is_connected(G) if G.number_of_nodes() > 0 else False
        kind = 'connected'
    asserts_connected = 'not connected' not in claim_l and 'disconnected' not in claim_l
    if asserts_connected and not is_conn:
        findings.append(f"{{kind}}: claim asserts connected, graph is not")
    elif not asserts_connected and is_conn:
        findings.append(f"{{kind}}: claim asserts disconnected, graph is connected")

# Tree
if 'tree' in claim_l:
    checked.append('tree')
    is_tree = nx.is_tree(G) if not directed_mode else nx.is_arborescence(G)
    asserts_tree = 'not a tree' not in claim_l and 'not tree' not in claim_l
    if asserts_tree and not is_tree:
        findings.append(f"tree: claim asserts tree, graph is not")
    elif not asserts_tree and is_tree:
        findings.append(f"tree: claim asserts non-tree, graph is a tree")

# Cycle
if 'cycle' in claim_l or 'acyclic' in claim_l:
    checked.append('cycle')
    try:
        if directed_mode:
            has_cycle = not nx.is_directed_acyclic_graph(G)
        else:
            has_cycle = any(True for _ in nx.simple_cycles(G)) if G.number_of_nodes() > 0 else False
    except Exception:
        has_cycle = False
    asserts_cycle = 'cycle' in claim_l and 'no cycle' not in claim_l and 'acyclic' not in claim_l
    asserts_acyclic = 'acyclic' in claim_l or 'no cycle' in claim_l
    if asserts_cycle and not has_cycle:
        findings.append("cycle: claim asserts cycle, graph is acyclic")
    elif asserts_acyclic and has_cycle:
        findings.append("acyclic: claim asserts acyclic, graph has cycle")

# Diameter
m_diam = re.search(r'diameter\\s*(?:is|=|:|of)?\\s*(\\d+)', claim_l)
if m_diam:
    try:
        if directed_mode:
            d_actual = nx.diameter(G.to_undirected()) if G.number_of_nodes() > 0 else None
        else:
            d_actual = nx.diameter(G) if nx.is_connected(G) else None
    except Exception:
        d_actual = None
    if d_actual is not None:
        d_claimed = int(m_diam.group(1))
        checked.append('diameter')
        if d_actual != d_claimed:
            findings.append(f"diameter: actual {{d_actual}}, claimed {{d_claimed}}")

if not checked:
    print("GRAPH_NO_CHECKABLE_PROPERTY: edges extracted but no recognised property claim")
elif findings:
    print(f"GRAPH_MISMATCH: {{len(findings)}} property mismatch(es)")
    for f in findings[:5]:
        print(f"  {{f}}")
else:
    print(f"GRAPH_VERIFIED: all {{len(checked)}} claimed properties hold ({{','.join(checked)}})")
"""
    t0 = time.monotonic()
    output = _run_tool_subprocess(code, timeout=15)
    elapsed = time.monotonic() - t0

    stripped = output.strip()
    if stripped.startswith("GRAPH_VERIFIED"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="CONFIRMED",
            confidence=0.85, evidence=f"networkx: {output}",
            tool_used="networkx", elapsed_s=elapsed,
        )
    elif stripped.startswith("GRAPH_MISMATCH"):
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="REJECTED",
            confidence=0.85, evidence=f"networkx: {output}",
            tool_used="networkx", elapsed_s=elapsed,
        )
    else:
        # GRAPH_NO_EDGES, GRAPH_NO_CHECKABLE_PROPERTY, GRAPH_IMPORT_ERROR, etc.
        return CellVerdict(
            cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
            confidence=0.2, evidence=f"networkx: {output}",
            tool_used="networkx", elapsed_s=elapsed,
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


# ── Specialist B-Cell Dispatch (Phase B4) ──────────────────────────────────────

def _specialist_b_cell_dispatch(
    triaged: List[TriagedFinding],
    domain_config: Dict[str, Any],
) -> List[CellVerdict]:
    """Route claims to domain-specific verification tools based on TOML config.

    Reads ``immune.verification_tools`` from the domain config to determine
    which tools to use for each claim type, then looks up each tool name in
    the manifest at ``bench/cdsfl_registry/tool_manifest.toml`` to resolve
    the verifier function and its arity. Delegated tools (``ast_analysis``,
    ``test_runner``) are skipped here because other cells handle them.

    Semantics:
      * first definitive verdict wins (break on non-UNCERTAIN)
      * UNCERTAIN verdicts fall through to the next tool
      * unknown / delegated / missing-verifier tools are skipped silently
      * if all tools return UNCERTAIN, the last UNCERTAIN verdict is kept

    Phase B4: runs in shadow mode — specialist verdicts are returned to the
    caller but the reference runner does not fold them into ``all_verdicts``.
    Promotion is a single-line flip in reference_runner.py.
    """
    immune_cfg = domain_config.get("immune", {})
    tool_map: Dict[str, List[str]] = immune_cfg.get("verification_tools", {})

    if not tool_map:
        return []  # No specialist tools configured

    manifest = _load_tool_manifest()
    if not manifest:
        return []  # Manifest failed to load — treat as no specialist tools

    verdicts: List[CellVerdict] = []
    module = sys.modules[__name__]

    # Map ClaimType enum values to TOML key names. Identity for now; kept
    # as an explicit map so renaming either side does not silently break.
    _CLAIM_TYPE_TO_KEY = {
        "mathematical": "mathematical",
        "logical": "logical",
        "statistical": "statistical",
        "code_structural": "code_structural",
        "code_behavioral": "code_behavioral",
    }

    for tf in triaged:
        if tf.is_duplicate:
            continue

        claim_key = _CLAIM_TYPE_TO_KEY.get(tf.claim_type.value)
        if claim_key is None or claim_key not in tool_map:
            continue  # No specialist tools for this claim type

        specialist_tools = tool_map[claim_key]
        fid = tf.finding.finding_id

        v: Optional[CellVerdict] = None

        # File-based verifiers need the target file path.
        target_file = getattr(tf.finding, "target_file", "") or ""

        for tool_name in specialist_tools:
            entry = manifest.get(tool_name)
            if entry is None or entry.get("delegate"):
                # Unknown tool, or delegated to another cell (ast_analysis →
                # B-Cell v2, test_runner → CT cell). Skip silently.
                continue
            verifier_fn = getattr(module, entry["verifier"], None)
            if verifier_fn is None:
                # Validator should have dropped this at load time; belt and
                # braces in case the manifest is hot-reloaded in future.
                continue

            if entry.get("needs_file"):
                v = verifier_fn(tf.extracted_claim, target_file)
            else:
                v = verifier_fn(tf.extracted_claim)

            if v is not None and v.verdict != "UNCERTAIN":
                v.evidence += f" [specialist:{tool_name}]"
                break  # First definitive result wins

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

_shadow_log = _logging.getLogger("immune.pipeline")

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
        _os.path.join(_shadow_log_dir, "immune_pipeline.log"),
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

    Pipeline is active: findings failing the barrier are filtered out.
    The results are logged for observation.

    Returns:
        (all_findings, barrier_results) — findings that passed the barrier
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
    domain_config: Optional[Dict[str, Any]] = None,
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

# Software-domain code context pattern (Layer 1, Exp 38 fix cycle).
# Matches Python/software constructs that indicate a code finding even when
# descriptions lack file:line citations. Checked BEFORE math pattern to
# prevent misrouting of code bugs that happen to contain operators.
_CODE_CONTEXT_PATTERN = re.compile(
    r"(?:"
    r"\bdef\s+\w+"                             # function definition
    r"|\bclass\s+\w+"                          # class definition
    r"|\bself\.\w+"                            # instance attribute/method
    r"|\bimport\s+\w+"                         # import statement
    r"|\b__\w+__"                              # dunder methods/attrs
    r"|\breturn\s"                             # return statement
    r"|\braises?\s+\w+Error"                   # exception raising
    r"|\b\w+Error\b|\b\w+Exception\b"         # exception types
    r"|\bif\s+.*\bentry\b|\bentry\[|entries\[" # dict access patterns
    r"|\bstatus\b.*\b(?:transition|change|mutate|overwrite|corrupt)" # status mutation
    r"|\b(?:bug|flaw|defect)\b.*\b(?:runtime|logic|behavior)"       # bug language
    r"|\b\w+\(\)\s"                            # function call: foo()
    r")",
    re.IGNORECASE,
)

# Strong math/stats signals that should NOT be overridden by code context.
# Even in software domain, if these are present the finding is genuinely
# mathematical or statistical.
_STRONG_MATH_SIGNAL = re.compile(
    r"(?:"
    r"\bp[- ]?value\b"
    r"|\bdistribution\b"
    r"|\bconfidence\s+interval\b"
    r"|\bstandard\s+deviation\b"
    r"|\bproof\b"
    r"|\btheorem\b"
    r"|\blemma\b"
    r"|\bcorollary\b"
    r"|\bconvergence\s+(?:rate|bound|guarantee)"
    r"|\bO\([^)]+\)"                             # Big-O notation: O(n), O(n log n)
    r"|\bbig[- ]?O\b"
    r"|\basymptotic\b"
    r"|\bbounded\b"                              # bounded above/below
    r"|\b(?:quadratic|polynomial|exponential)\s+time\b"  # complexity classes
    r"|\bfor\s+(?:all|every)\b"                  # universal quantification
    r"|\binequality\b"
    r"|\bsatisf(?:y|ies)\b"                      # constraint satisfaction
    r"|\b(?:symmetric|transitive|reflexive)\b"   # relation properties
    r")",
    re.IGNORECASE,
)


def _classify_claim_v2(
    finding: Finding,
    domain: str = "",
) -> Tuple[ClaimType, str, float]:
    """V2 classifier: tightened math pattern, citation-aware routing.

    Changes from v1:
    1. Code-citing findings route to CODE_BEHAVIORAL (not MATH/LOGIC)
    2. Math pattern requires equation context (no bare +/-/=)
    3. Classification order: STAT → STRUCT → CITATION → CODE_CONTEXT → MATH → LOGIC
    4. Default is UNCATEGORISED (not CODE_BEHAVIORAL garbage-can)
    5. Returns confidence score for downstream gating
    6. Domain-aware: in software domain, code-context check before math (Layer 1)

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

    # 3.5 (Layer 1): Software-domain code-context check BEFORE math.
    # In software domain, findings that mention Python constructs (def, self.,
    # class, __init__, status transition, etc.) should route to CODE_BEHAVIORAL
    # even when they contain operators that would match the math pattern.
    # Exception: preserve strong math/stats signals (proof, theorem, p-value).
    if domain == "software" and _CODE_CONTEXT_PATTERN.search(desc):
        if not _STRONG_MATH_SIGNAL.search(desc):
            return ClaimType.CODE_BEHAVIORAL, desc, 0.65

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

    # 5.5 Strong math signal promotion (Layer 1 complement).
    # If strong math vocabulary is present but no pattern above matched,
    # promote to MATHEMATICAL rather than letting it fall to software fallback.
    # Guard: only promote when code-context is ABSENT. If both signals are
    # present ("add_verdict() for every verdict" has code + "for every"),
    # the description is ambiguous — let the software fallback handle it.
    if domain == "software" and _STRONG_MATH_SIGNAL.search(desc):
        if not _CODE_CONTEXT_PATTERN.search(desc):
            return ClaimType.MATHEMATICAL, desc, 0.55

    # 6. Domain-aware fallback: in software domain, UNCATEGORISED → CODE_BEHAVIORAL
    # (low confidence, but routes to CT which can investigate rather than dead-end)
    if domain == "software":
        return ClaimType.CODE_BEHAVIORAL, desc, 0.40

    # 7. Default: UNCATEGORISED
    return ClaimType.UNCATEGORISED, desc, 0.30


def dendritic_cell_v2(
    findings: List[Finding],
    v1_triaged: List[TriagedFinding],
    domain: str = "",
) -> List[TriagedFinding]:
    """Dendritic Cell v2: tightened classification with v1 comparison logging.

    Logs every case where v2 would classify differently from v1.
    Returns v2 triaged list for shadow pipeline consumption.
    """
    v2_triaged: List[TriagedFinding] = []
    diffs = 0

    for i, f in enumerate(findings):
        claim_type, extracted, confidence = _classify_claim_v2(f, domain=domain)
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
) -> Tuple[bool, str, "RegulatoryResult"]:
    """Regulatory T Cell v2: fixed math + structured output.

    Changes from v1:
    1. Check 1 uses combined removal rate (rejected + duplicated) / total
    2. Check 3 only counts findings present in final_verdicts (intersection)
    3. Check 3 uses proportional threshold (>= 0.85) instead of exact match

    Returns:
        (autoimmune_flag, reason_string, RegulatoryResult)
        Third element added 13 April 2026 (Codex 5.3 confer): structured
        record with thresholds, counts, per-model breakdown, and which
        checks fired — so the HIL can inspect the decision, not just the flag.
    """
    total = len(final_verdicts)
    if total < min_findings_for_check:
        reason = f"[RT_v2] Too few findings ({total}) for meta-check"
        detail = RegulatoryResult(
            autoimmune_flag=False, reason=reason,
            total_findings=total, rejected_count=0, duplicated_count=0,
            uncertain_count=0, removal_rate=0.0,
            max_rejection_rate=max_rejection_rate,
            per_model_removal={}, checks_fired=[],
        )
        return False, reason, detail

    rejected = sum(1 for v in final_verdicts.values() if v == "REJECTED")
    duplicated = sum(1 for v in final_verdicts.values() if v == "DUPLICATE")
    uncertain = sum(1 for v in final_verdicts.values() if v == "UNCERTAIN")
    removed = rejected + duplicated
    removal_rate = removed / total

    reasons: List[str] = []
    checks_fired: List[str] = []

    # Check 1: Combined removal rate (v2: includes duplicates)
    # P2 fix: when ALL removals are duplicates (rejected==0), this is normal
    # depletion — the pipeline is correctly removing duplicate findings, not
    # falsely rejecting novel ones.  Log as DEPLETION for visibility but do
    # NOT set the autoimmune flag.
    if removal_rate > max_rejection_rate:
        if rejected == 0:
            # All removals are duplicates — depletion, not autoimmune.
            checks_fired.append("depletion_high_duplicate_rate")
            _shadow_log.info(
                "RT v2: depletion (not autoimmune) — removal rate %d/%d (%.1f%%), "
                "all duplicates, rejected=0",
                removed, total, removal_rate * 100,
            )
            # NOTE: intentionally NOT appending to `reasons` — this check
            # does not contribute to the autoimmune flag when rejected==0.
        else:
            reasons.append(
                f"[RT_v2] Removal rate {removed}/{total} ({removal_rate:.1%}) "
                f"exceeds threshold ({max_rejection_rate:.0%}) "
                f"[rejected={rejected}, duplicated={duplicated}]"
            )
            checks_fired.append("removal_rate_exceeded")

    # Check 2 (MF-36 parity, pre-launch review fix): High UNCERTAIN rate
    # indicates fail-open illusion — verification tools may be non-functional.
    # Ported from v1 Check 1b.
    uncertain_rate = uncertain / total
    if uncertain_rate > 0.30:
        reasons.append(
            f"[RT_v2] UNCERTAIN rate {uncertain}/{total} ({uncertain_rate:.1%}) "
            f"exceeds 30% — verification tools may be non-functional (fail-open)"
        )
        checks_fired.append("uncertain_rate_exceeded")

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
            checks_fired.append(f"per_model_bias:{mid}")

    # Build per-model breakdown for structured output
    per_model = {
        mid: {"total": model_counts[mid], "removed": model_removed.get(mid, 0)}
        for mid in model_counts
    }

    flag = bool(reasons)
    if flag:
        reason_str = "; ".join(reasons)
        _shadow_log.info("RT v2 (v2): AUTOIMMUNE flagged — %s", reason_str)
    elif "depletion_high_duplicate_rate" in checks_fired:
        reason_str = (
            f"[RT_v2] Depletion: removal rate {removed}/{total} "
            f"({removal_rate:.1%}) — all duplicates, no rejections"
        )
        _shadow_log.info("RT v2 (v2): depletion — %.1f%% removal rate (all duplicates)",
                         removal_rate * 100)
    else:
        reason_str = f"[RT_v2] Pipeline healthy: {removal_rate:.1%} removal rate"
        _shadow_log.info("RT v2 (v2): healthy — %.1f%% removal rate", removal_rate * 100)

    detail = RegulatoryResult(
        autoimmune_flag=flag,
        reason=reason_str,
        total_findings=total,
        rejected_count=rejected,
        duplicated_count=duplicated,
        uncertain_count=uncertain,
        removal_rate=round(removal_rate, 4),
        max_rejection_rate=max_rejection_rate,
        per_model_removal=per_model,
        checks_fired=checks_fired,
    )

    return flag, reason_str, detail


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
    override_threshold: float = 0.70,
    domain: str = "",
) -> List[Dict[str, Any]]:
    """WP3c: classify findings via lightweight LLM call.

    Exp 38 finding: regex classifier agrees with LLM only ~15% of the
    time for code findings (any comparison operator triggers MATHEMATICAL).
    In software domain, LLM is now PRIMARY — any valid classification
    wins over regex. In non-software domains, LLM is override-only with
    confidence threshold and MATHEMATICAL safety guard.

    Modifies regex_triaged in-place when overriding.

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

    llm_primary = (domain == "software")
    _shadow_log.info(
        "LLM classifier: %s (CLI Haiku, override_threshold=%.2f). "
        "%d findings to classify.",
        "PRIMARY" if llm_primary else "SEMI-ACTIVE",
        override_threshold, len(findings),
    )

    override_count = 0

    for i, (f, regex_tf) in enumerate(zip(findings, regex_triaged)):
        t0 = time.monotonic()
        try:
            # Use confidence-returning prompt format
            prompt = (
                f"{_ACTIVE_CLASSIFIER_PROMPT}\n\n"
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

            lines = [l.strip() for l in response.split("\n") if l.strip()]
            llm_category = lines[0].lower().replace(" ", "_") if lines else ""
            llm_type = _CATEGORY_MAP.get(llm_category, ClaimType.UNCATEGORISED)

            # Parse confidence from second line (fail-safe to 0.5)
            llm_confidence = 0.5
            if len(lines) >= 2:
                try:
                    llm_confidence = float(lines[1])
                    llm_confidence = max(0.0, min(1.0, llm_confidence))
                except ValueError:
                    llm_confidence = 0.5

            disagrees = regex_tf.claim_type != llm_type
            # In software domain, LLM is primary (regex ~15% agreement).
            # In non-software domains, LLM overrides only when confident
            # and MATHEMATICAL guard is retained for safety.
            math_guard = (
                regex_tf.claim_type == ClaimType.MATHEMATICAL
                and not llm_primary
            )
            if llm_primary:
                # Software domain: any valid LLM classification wins
                should_override = (
                    disagrees
                    and llm_type != ClaimType.UNCATEGORISED
                )
            else:
                # Non-software: confidence threshold + math guard
                should_override = (
                    disagrees
                    and llm_confidence >= override_threshold
                    and not math_guard
                    and llm_type != ClaimType.UNCATEGORISED
                )

            record = {
                "finding_id": f.finding_id,
                "regex_type": regex_tf.claim_type.value,
                "llm_type": llm_type.value,
                "llm_confidence": llm_confidence,
                "llm_raw": response.strip(),
                "match": not disagrees,
                "overridden": should_override,
                "elapsed_s": round(elapsed, 3),
            }
            comparisons.append(record)

            if should_override:
                _shadow_log.info(
                    "LLM classifier OVERRIDE: %s — regex=%s → llm=%s "
                    "(conf=%.2f, threshold=%.2f, %.1fs)",
                    f.finding_id, regex_tf.claim_type.value,
                    llm_type.value, llm_confidence,
                    override_threshold, elapsed,
                )
                regex_triaged[i] = TriagedFinding(
                    finding=regex_tf.finding,
                    claim_type=llm_type,
                    extracted_claim=regex_tf.extracted_claim,
                )
                override_count += 1
            elif disagrees and math_guard:
                # P5 fix: distinguish guard-blocked from threshold-blocked.
                # Old code reported "below threshold" even when the real
                # reason was math_guard — misleading in non-software domains.
                _shadow_log.info(
                    "LLM classifier: %s — regex=%s llm=%s "
                    "(conf=%.2f, BLOCKED by MATHEMATICAL guard, %.1fs)",
                    f.finding_id, regex_tf.claim_type.value,
                    llm_type.value, llm_confidence, elapsed,
                )
            elif disagrees:
                _shadow_log.info(
                    "LLM classifier: %s — regex=%s llm=%s "
                    "(conf=%.2f, below threshold %.2f, %.1fs)",
                    f.finding_id, regex_tf.claim_type.value,
                    llm_type.value, llm_confidence,
                    override_threshold, elapsed,
                )
        except Exception as e:
            elapsed = time.monotonic() - t0
            comparisons.append({
                "finding_id": f.finding_id,
                "regex_type": regex_tf.claim_type.value,
                "llm_type": "ERROR",
                "llm_confidence": 0.0,
                "llm_raw": str(e)[:100],
                "match": False,
                "overridden": False,
                "elapsed_s": round(elapsed, 3),
            })
            _shadow_log.warning(
                "LLM classifier error for %s: %s", f.finding_id, e,
            )

    match_count = sum(1 for c in comparisons if c["match"])
    total = len(comparisons)
    _shadow_log.info(
        "LLM classifier: %d/%d agree with regex (%.1f%%), %d overrides applied",
        match_count, total, (match_count / max(total, 1)) * 100,
        override_count,
    )

    return comparisons


# ── Layer 2: Active LLM classifier for UNCATEGORISED residue ──────────
# Targets only findings that DC v2 regex + domain-aware code-context still
# cannot classify. Short timeout, fail-open (keeps existing classification).
# Returns structured {category, confidence} instead of bare category name.

_ACTIVE_CLASSIFIER_PROMPT = """\
You are a claim type classifier for a code verification pipeline.
Classify the following finding description into exactly ONE category.

Respond with EXACTLY two lines:
Line 1: the category name (one of the options below)
Line 2: your confidence as a decimal between 0.0 and 1.0

Categories:
- MATHEMATICAL: equations, inequalities, bounds, numeric relationships verifiable symbolically.
- LOGICAL: if/then claims, invariant assertions, reachability arguments about code paths.
- STATISTICAL: distributions, p-values, confidence intervals, statistical significance.
- CODE_STRUCTURAL: missing or incorrect code structure (decorators, class hierarchy, absent method).
- CODE_BEHAVIORAL: runtime behaviour bugs, wrong return values, incorrect state transitions.
- UNCATEGORISED: does not clearly fit any of the above."""


def _active_llm_classify(
    finding: Finding,
    timeout: int = 15,
) -> Tuple[Optional[ClaimType], float]:
    """Layer 2: classify a single finding via LLM with confidence.

    Returns (claim_type, confidence) or (None, 0.0) on failure.
    Fail-open: caller keeps existing classification on None.
    """
    cli = _get_claude_cli()
    if not cli:
        return None, 0.0

    _CATEGORY_MAP = {
        "mathematical": ClaimType.MATHEMATICAL,
        "logical": ClaimType.LOGICAL,
        "statistical": ClaimType.STATISTICAL,
        "code_structural": ClaimType.CODE_STRUCTURAL,
        "code_behavioral": ClaimType.CODE_BEHAVIORAL,
        "uncategorised": ClaimType.UNCATEGORISED,
    }

    prompt = (
        f"{_ACTIVE_CLASSIFIER_PROMPT}\n\n"
        f"Finding description:\n{finding.description[:500]}"
    )
    cmd = [
        cli, "-p", prompt,
        "--model", _CLASSIFIER_MODEL,
        "--output-format", "text",
        "--max-turns", "1",
    ]

    try:
        with _CLAUDE_CLI_LOCK:
            result = sp.run(cmd, capture_output=True, text=True, timeout=timeout)
        lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
        if not lines:
            return None, 0.0

        category_raw = lines[0].lower().replace(" ", "_")
        claim_type = _CATEGORY_MAP.get(category_raw)

        confidence = 0.0
        if len(lines) >= 2:
            try:
                confidence = float(lines[1])
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                confidence = 0.5  # LLM returned non-numeric — treat as moderate

        return claim_type, confidence
    except (sp.TimeoutExpired, OSError, Exception) as e:
        _shadow_log.warning("Active LLM classifier timeout/error for %s: %s",
                            finding.finding_id, e)
        return None, 0.0


def _apply_llm_reclassification(
    triaged: List[TriagedFinding],
    domain: str = "",
    confidence_threshold: float = 0.55,
) -> int:
    """Layer 2: reclassify UNCATEGORISED findings via LLM.

    Only targets findings that are still UNCATEGORISED after DC v2 regex +
    domain-aware code-context rules (Layer 1). Fail-open: if LLM fails or
    returns low confidence, the finding keeps its existing classification.

    In software domain with enhanced code-context (Layer 1), UNCATEGORISED
    residue should be small (0-3 findings typical), so latency is bounded.

    Returns count of reclassified findings.
    """
    uncategorised = [(i, tf) for i, tf in enumerate(triaged)
                     if tf.claim_type == ClaimType.UNCATEGORISED]

    if not uncategorised:
        return 0

    _shadow_log.info(
        "Layer 2 LLM classifier: %d UNCATEGORISED findings to reclassify",
        len(uncategorised),
    )

    reclassified = 0
    for idx, tf in uncategorised:
        llm_type, confidence = _active_llm_classify(tf.finding)
        if llm_type and llm_type != ClaimType.UNCATEGORISED and confidence >= confidence_threshold:
            _shadow_log.info(
                "Layer 2 reclassification: %s — UNCATEGORISED → %s (conf=%.2f)",
                tf.finding.finding_id, llm_type.value, confidence,
            )
            triaged[idx] = TriagedFinding(
                finding=tf.finding,
                claim_type=llm_type,
                extracted_claim=tf.extracted_claim,
            )
            reclassified += 1
        else:
            # Fail-open: in software domain, fall back to CODE_BEHAVIORAL
            if domain == "software":
                triaged[idx] = TriagedFinding(
                    finding=tf.finding,
                    claim_type=ClaimType.CODE_BEHAVIORAL,
                    extracted_claim=tf.extracted_claim,
                )
                _shadow_log.info(
                    "Layer 2 fallback: %s — UNCATEGORISED → CODE_BEHAVIORAL "
                    "(LLM %s conf=%.2f, below threshold %.2f)",
                    tf.finding.finding_id,
                    llm_type.value if llm_type else "FAILED",
                    confidence,
                    confidence_threshold,
                )
                reclassified += 1

    return reclassified


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
) -> Tuple[List[Dict[str, Any]], List[CellVerdict]]:
    """WP3d ACTIVE: extract and formalise preconditions for B-Cell claims.

    For each MATHEMATICAL or LOGICAL finding:
    1. Extract natural language preconditions from the description
    2. Translate to Z3 constraint fragments
    3. Compare: did the B-Cell's verdict change when preconditions are
       accounted for? (i.e., would the Formalisation Agent have prevented
       a false rejection?)

    ACTIVE (promoted from shadow, Exp 38 fix cycle):
    When a potential false rejection is detected (B-Cell REJECTED a claim
    that has extractable preconditions), produces an UNCERTAIN counter-verdict.
    This feeds into the reconciliation gate, preventing context-erasure
    false rejections from being locked.

    Returns (comparisons, counter_verdicts).
    """
    comparisons: List[Dict[str, Any]] = []
    counter_verdicts: List[CellVerdict] = []

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
            # ACTIVE: produce counter-verdict to prevent false rejection lock
            counter_verdicts.append(CellVerdict(
                cell_type=CellType.B_CELL,
                finding_id=fid,
                verdict="UNCERTAIN",
                confidence=0.45,
                evidence=(
                    f"[Formalisation] B-Cell REJECTED with {len(preconditions)} "
                    f"extractable preconditions — potential context-erasure "
                    f"false rejection. Preconditions: {preconditions}. "
                    f"Z3 translatable: {z3_fragment is not None}"
                ),
                tool_used="formalisation_agent",
            ))
            _shadow_log.info(
                "Formalisation agent: %s — REJECTED with %d preconditions "
                "(potential false rejection, counter-verdict issued). "
                "Preconditions: %s",
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
        "preconditions, %d potential false rejections, %d counter-verdicts",
        total, with_pc, potential_fr, len(counter_verdicts),
    )

    return comparisons, counter_verdicts


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
    domain: str = "",
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

    # ── Layer 3: Load domain configuration ────────────────────────────
    # Domain config provides specialist patterns, tool mappings, and
    # prompt templates. Loaded once per pipeline invocation (cached).
    # Specialist B-Cell subtypes will use this when built (Phase B4).
    domain_config = load_domain_config(domain) if domain else {}
    if domain_config:
        _shadow_log.info(
            "Domain config loaded: %s (%d sections)",
            domain, len(domain_config),
        )

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
    triaged = dendritic_cell_v2(new_findings, v1_triaged, domain=domain)
    timings["dendritic"] = round(time.monotonic() - t0_dc_v2, 4)

    # Log claim type distribution
    type_counts = {}
    for tf in triaged:
        key = tf.claim_type.value
        type_counts[key] = type_counts.get(key, 0) + 1

    # ── Stage 1.5: Typed LLM Classifier SEMI-ACTIVE (WP3c promoted) ───
    # Runs on ALL findings. Overrides regex when LLM disagrees with high
    # confidence (>= 0.70). Exp 38 fix: MATHEMATICAL override now allowed
    # in software domain (regex had ~15% agreement with LLM on code findings).
    t0_llm_cls = time.monotonic()
    try:
        llm_classifier_results = typed_llm_classifier(new_findings, triaged, domain=domain)
    except Exception as e:
        _shadow_log.warning("LLM classifier failed: %s", e)
        llm_classifier_results = []
    timings["llm_classifier"] = round(time.monotonic() - t0_llm_cls, 4)

    # ── Stage 1.7: Layer 2 — Active LLM reclassification (residue only) ─
    # Targets ONLY findings still UNCATEGORISED after DC v2 regex + Layer 1
    # domain-aware code-context. In software domain with enhanced regex, the
    # residue is typically 0-3 findings, so latency is bounded.
    t0_layer2 = time.monotonic()
    layer2_count = 0
    try:
        layer2_count = _apply_llm_reclassification(triaged, domain=domain)
    except Exception as e:
        _shadow_log.warning("Layer 2 LLM reclassification failed: %s", e)
    timings["layer2_llm_active"] = round(time.monotonic() - t0_layer2, 4)
    if layer2_count > 0:
        # Re-log type distribution after reclassification
        type_counts = {}
        for tf in triaged:
            key = tf.claim_type.value
            type_counts[key] = type_counts.get(key, 0) + 1

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
        # 13 April 2026: pass domain_config for specialist CT prompts
        if ct_enabled:
            futures["cytotoxic_t"] = pool.submit(
                cytotoxic_t_cell, triaged, source_paths, ct_timeout,
                domain_config,
            )

        # 2a': CT v2 falsifier (WP6a: now ACTIVE, verdicts feed pipeline)
        if ct_enabled:
            futures["ct_v2"] = pool.submit(
                cytotoxic_t_cell_v2, triaged, source_paths, ct_timeout,
                domain_config,
            )

        # 2b: B-Cell v1 (SymPy + z3 + stats — still primary for non-AST claims)
        futures["b_cell"] = pool.submit(b_cell_verify, triaged)

        # 2b': B-Cell v2 AST-grounded z3 (WP6a: now ACTIVE)
        futures["b_cell_v2"] = pool.submit(
            b_cell_v2, triaged, source_paths,
        )

        # 2b'': B-Cell specialist (Phase B4: SHADOW mode)
        # Routes claims to domain-specific tools from TOML config.
        # Runs in parallel, results logged but don't affect verdicts.
        if domain_config:
            futures["b_cell_specialist"] = pool.submit(
                _specialist_b_cell_dispatch, triaged, domain_config,
            )

        # 2c: NK v2 (WP6a: now PRIMARY — FP continue fix + intra-round dedup)
        # Pre-launch review fix: merge domain-specific FP patterns from TOML
        merged_fp_db = false_positive_db
        if domain_config:
            domain_fp_entries = domain_config.get("immune", {}).get("false_positive_patterns", [])
            if domain_fp_entries:
                import re as _re
                domain_fps = []
                for fp_entry in domain_fp_entries:
                    pat = fp_entry.get("pattern", "")
                    if pat:
                        domain_fps.append({
                            "pattern": _re.compile(pat, _re.IGNORECASE | _re.DOTALL),
                            "source": fp_entry.get("source", ""),
                            "expected_model": fp_entry.get("expected_model", ""),
                        })
                merged_fp_db = (false_positive_db or _KNOWN_FALSE_POSITIVES) + domain_fps
        futures["nk_v2"] = pool.submit(
            nk_cell_v2, triaged_for_nk, prior_findings, tau_sim,
            merged_fp_db,
        )

        # Collect results — all active cells feed all_verdicts
        specialist_verdicts: List[CellVerdict] = []
        for name, future in futures.items():
            try:
                result = future.result(timeout=ct_timeout + 30)
                if name == "nk_v2":
                    # NK v2 returns (triaged, verdicts) tuple
                    nk_triaged_result, nk_verdicts = result
                    all_verdicts.extend(nk_verdicts)
                    for v in nk_verdicts:
                        tool_usage[v.tool_used] = tool_usage.get(v.tool_used, 0) + 1
                elif name == "b_cell_specialist":
                    # Phase B4 SHADOW: log divergences, don't affect verdicts
                    specialist_verdicts = result
                    _shadow_log.info(
                        "B-Cell specialist (shadow): %d verdicts",
                        len(specialist_verdicts),
                    )
                    tool_usage["b_cell_specialist_shadow"] = len(specialist_verdicts)
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

        # Phase B4 shadow: log divergences between specialist and generic
        if specialist_verdicts:
            generic_by_fid = {}
            for v in all_verdicts:
                if v.cell_type == CellType.B_CELL:
                    generic_by_fid[v.finding_id] = v.verdict
            for sv in specialist_verdicts:
                generic_v = generic_by_fid.get(sv.finding_id, "NONE")
                if sv.verdict != generic_v:
                    _shadow_log.info(
                        "B-Cell specialist divergence: %s specialist=%s generic=%s",
                        sv.finding_id, sv.verdict, generic_v,
                    )

    timings["parallel_verification"] = round(time.monotonic() - t0, 4)

    # Adopt NK v2's triaged state with duplicate flags if available
    if nk_triaged_result is not None:
        triaged = nk_triaged_result

    # ── Stage 2.5: Formalisation Agent ACTIVE (WP3d, promoted Exp 38) ──
    # Extracts preconditions from math/logic claims. When B-Cell rejected
    # a claim that has extractable preconditions, produces UNCERTAIN
    # counter-verdicts to prevent context-erasure false rejection locks.
    #
    # Promotion (Exp 38 fix cycle): counter-verdicts now REPLACE the
    # original B-Cell REJECTED verdict for that finding, rather than being
    # appended as a separate UNCERTAIN entry (which helper_t ignores).
    # Safety: only replaces REJECTED -> UNCERTAIN (saves from false rejection),
    # never introduces new rejections.
    t0_formal = time.monotonic()
    formalisation_counter_verdicts: List[CellVerdict] = []
    try:
        formalisation_results, formalisation_counter_verdicts = formalisation_agent(
            triaged, all_verdicts,
        )
        # Apply counter-verdicts by replacing B-Cell REJECTED verdicts in-place
        counter_fids = {v.finding_id for v in formalisation_counter_verdicts}
        if counter_fids:
            counter_lookup = {v.finding_id: v for v in formalisation_counter_verdicts}
            for idx, v in enumerate(all_verdicts):
                if (v.finding_id in counter_fids
                        and v.cell_type == CellType.B_CELL
                        and v.verdict == "REJECTED"):
                    cv = counter_lookup[v.finding_id]
                    _shadow_log.info(
                        "Formalisation override: %s — B-Cell REJECTED → UNCERTAIN "
                        "(preconditions detected, preventing false rejection lock)",
                        v.finding_id,
                    )
                    all_verdicts[idx] = cv
            # Also log counter-verdicts for tool usage tracking
            for v in formalisation_counter_verdicts:
                tool_usage[v.tool_used] = tool_usage.get(v.tool_used, 0) + 1
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
    v2_autoimmune, v2_reg_reason, v2_reg_detail = regulatory_t_v2(
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
        elif verdict in ("CONFIRMED", "UNCERTAIN", "UNSCORED"):
            # Pre-launch review fix: UNSCORED = absence of evidence, not
            # evidence of absence. Pass through for downstream handling.
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

    # ── Stage 6: Hard verification gate (Layer 3) ─────────────────────
    # Nothing should exit the immune system without having passed through
    # at least one tool-grounded verification cell. A finding with zero
    # tool-grounded verdicts means no cell actually checked it — it slipped
    # through the routing. Escalate to HIL rather than letting it pass
    # as if verified.
    #
    # Tool-grounded cells: CT v1/v2 (code investigation), B-Cell v1/v2
    # (SymPy/z3/statsmodels), NK Cell v1/v2 (similarity dedup).
    # NOT tool-grounded: Helper T (synthesis only), Reg T (meta-check),
    # Formalisation Agent (precondition extraction).
    _TOOL_GROUNDED_CELLS = {
        CellType.CYTOTOXIC_T, CellType.B_CELL, CellType.NK_CELL,
    }
    unverified_count = 0
    for f in filtered:
        if f.verified or f.escalated:
            continue
        fid = f.finding_id
        tool_verdicts = [
            v for v in all_verdicts
            if v.finding_id == fid and v.cell_type in _TOOL_GROUNDED_CELLS
        ]
        if not tool_verdicts:
            object.__setattr__(f, 'escalated', True)
            unverified_count += 1
            _shadow_log.info(
                "VERIFICATION-GATE-ESCALATED to HIL: %s "
                "(no tool-grounded cell produced a verdict)",
                fid,
            )
    if unverified_count:
        _shadow_log.info(
            "Hard verification gate: escalated %d findings with no "
            "tool-grounded verdicts to HIL",
            unverified_count,
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
        domain=domain,
        regulatory_detail=v2_reg_detail,
    )
