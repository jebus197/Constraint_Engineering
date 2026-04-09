"""CC2 Manager — bounded-authority router with five mechanical sub-agents.

Phase B2-B3 of the CDSFL canonical execution plan. CC2 becomes a
manager/router only. It does NOT generate findings. Its authority:
  - Route findings to appropriate sub-agents
  - Assess team performance against capability fingerprints
  - Escalate to human-in-the-loop
  - CANNOT inject findings, override tool-backed verdicts, or make
    convergence decisions

Parallels the Guardian layer from Genesis: bounded authority, rejection
only, cannot generate.

Five sub-agents (all closed-constraint-space, all mechanical):
  1. Citation Verifier   — Haiku  — code citation accuracy
  2. Fix Extractor       — Opus   — natural-language fix to code diff
  3. Dedup Assessor      — Haiku  — finding deduplication
  4. Programmatic Verifier — Opus  — tool-backed claim verification
  5. CC2v Verdict        — Opus   — LLM fallback for ambiguous cases

Usage:
    from cc2_manager import cc2_verification_step

    stats = cc2_verification_step(registry, round_idx, source_code)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Path setup
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

VERIFICATION_MIN_ROUND = 6
VERIFICATION_BATCH_SIZE = 8       # Slightly larger than old CC2v — parallel agents
VERIFICATION_CONFIDENCE_THRESHOLD = 0.7
DEDUP_SIMILARITY_THRESHOLD = 0.35  # Lowered from 0.65 — Exp 36 showed 4:1 redundancy with semantic duplicates slipping through at higher thresholds

# Model IDs for claude -p dispatch
SONNET_MODEL = "claude-sonnet-4-6"
OPUS_MODEL = "claude-opus-4-6"
HAIKU_MODEL = "haiku"  # Kept for dedup (sufficient for similarity)

# Per-agent timeouts (seconds)
CITATION_TIMEOUT = 60
FIX_TIMEOUT = 120
DEDUP_TIMEOUT = 45
PROGRAMMATIC_TIMEOUT = 120
CC2V_TIMEOUT = 90

# Source code cap per agent (characters) to avoid context overflow
SOURCE_CAP_CITATION = 60_000
SOURCE_CAP_FIX = 80_000
SOURCE_CAP_PROGRAMMATIC = 60_000
SOURCE_CAP_CC2V = 60_000


# ─────────────────────────────────────────────────────────────────────────────
# CLI discovery (reuse orchestrator pattern)
# ─────────────────────────────────────────────────────────────────────────────

def _find_claude_cli() -> Optional[str]:
    """Find claude CLI binary."""
    found = shutil.which("claude")
    if found:
        return found
    import glob as globmod
    app_support = Path.home() / "Library" / "Application Support" / "Claude"
    patterns = [
        str(app_support / "claude-code" / "*" / "claude.app" / "Contents" / "MacOS" / "claude"),
        str(app_support / "claude-code-vm" / "*" / "claude"),
    ]
    for pattern in patterns:
        matches = sorted(globmod.glob(pattern), reverse=True)
        if matches and os.path.isfile(matches[0]):
            return matches[0]
    return None


CLAUDE_CLI: Optional[str] = _find_claude_cli()


def _log(msg: str) -> None:
    """Timestamped stderr log."""
    from datetime import datetime
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sub-agent dispatch (low-level CLI call)
# ─────────────────────────────────────────────────────────────────────────────

def _dispatch_cli(
    model_id: str,
    prompt: str,
    timeout: int,
    allowed_tools: Optional[List[str]] = None,
    max_turns: int = 1,
) -> Tuple[str, float]:
    """Dispatch a prompt to claude -p and return (response_text, elapsed_s).

    Uses --bare to minimise overhead. Restricted tools per agent.
    Raises RuntimeError on failure.
    """
    cli = CLAUDE_CLI
    if not cli:
        raise FileNotFoundError("Claude CLI not found")

    cmd = [
        cli, "-p",
        "--model", model_id,
        "--output-format", "text",
        "--no-session-persistence",
        "--max-turns", str(max_turns),
    ]
    if allowed_tools:
        cmd.extend(["--allowedTools", ",".join(allowed_tools)])
    else:
        # Analysis only — no file mutation
        cmd.extend(["--disallowed-tools", "Bash", "Edit", "Write"])

    t0 = time.monotonic()
    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = time.monotonic() - t0
    text = result.stdout.strip()

    # Known CLI bug: exit 1 with content is sometimes spurious
    if result.returncode != 0 and not text:
        stderr = result.stderr.strip()[:200]
        raise RuntimeError(f"claude CLI returned {result.returncode}: {stderr}")

    return text, elapsed


# ─────────────────────────────────────────────────────────────────────────────
# Agent result dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AgentResult:
    """Result from a single sub-agent for a single finding."""
    agent: str                        # "citation", "fix", "dedup", "programmatic", "cc2v"
    finding_id: str
    verdict: str                      # Agent-specific verdict string
    confidence: float = 0.5
    evidence: str = ""
    diff: str = ""                    # Fix extractor only
    duplicate_of: str = ""            # Dedup assessor only
    tool_output: str = ""             # Programmatic verifier only
    elapsed_s: float = 0.0
    error: str = ""


@dataclass
class AggregatedResult:
    """Aggregated results from all agents for a single finding."""
    finding_id: str
    agent_results: List[AgentResult] = field(default_factory=list)
    final_action: str = ""            # CONFIRM / REJECT / DUPLICATE / ESCALATE
    final_confidence: float = 0.0
    final_evidence: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Prompt templates (closed constraint space — structured I/O only)
# ─────────────────────────────────────────────────────────────────────────────

_CITATION_PROMPT = """You are a Citation Verifier. Your ONLY task is to check whether the
finding accurately describes the cited code.

You have access to: Read, Grep, Glob. Use them to verify file:line references
in the finding against the actual source code. Do not rely on the source excerpt
alone — read the referenced files directly when the finding cites specific
locations.

Rules:
- Check ONLY whether the description matches what the code actually does.
- Do NOT assess severity, importance, or whether the issue matters.
- You MUST use tools to read the cited code. Do not reason without evidence.
- Cite specific line numbers and actual code content as evidence.
- One verdict only. No preamble, no explanation beyond the evidence field.

SOURCE CODE (excerpt):
{source_code}

FINDING:
[{finding_id}] {description}

Respond with EXACTLY one line in this format:
VERIFIED | <confidence 0.0-1.0> | <evidence citing specific code lines from tool output>
UNVERIFIED | <confidence 0.0-1.0> | <what the code actually does vs what the finding claims>
UNCLEAR | <confidence 0.0-1.0> | <what cannot be determined and why>
"""

_FIX_PROMPT = """You are a Fix Extractor. Your ONLY task is to convert the natural-language
proposed fix into an applicable code change.

Rules:
- Output a unified diff that can be applied with `patch -p1`.
- If the fix is too vague, ambiguous, or requires design decisions, say NOT_EXTRACTABLE.
- Do NOT improve, extend, or rewrite the fix. Extract what is described, nothing more.
- The diff must be syntactically valid and apply cleanly to the source code provided.

SOURCE CODE:
{source_code}

FINDING:
[{finding_id}] {description}

PROPOSED FIX:
{proposed_fix}

Respond with EXACTLY one of:
1. A unified diff block (starting with --- and +++), OR
2. NOT_EXTRACTABLE | <reason>
"""

_DEDUP_PROMPT = """You are a Dedup Assessor. Your ONLY task is to determine whether the
new finding describes the same issue as one of the candidate duplicates.

Rules:
- Same ROOT CAUSE = duplicate, even if described differently.
- Similar symptoms but different root causes = NOT duplicate.
- One verdict only. No preamble.

NEW FINDING:
[{finding_id}] {description}

CANDIDATE DUPLICATES:
{candidates_block}

Respond with EXACTLY one line:
DUPLICATE_OF <candidate_id> | <confidence 0.0-1.0> | <evidence of same root cause>
NOVEL | <confidence 0.0-1.0> | <why root causes differ>
"""

_PROGRAMMATIC_PROMPT = """You are a Programmatic Verifier. Your ONLY task is to determine whether
the claim in this finding can be verified using formal or computational tools.

You have access to: Read, Bash, Grep, Glob.

The tool output IS your evidence. Your reasoning selects and interprets tool
output — it does not substitute for it. If the tools cannot verify the claim,
the claim is UNVERIFIABLE. Do not guess.

Available verification methods (use via Bash):
- `import ast` — parse Python source, verify structure, trace call graphs
- `import sympy` — verify mathematical claims symbolically
- `import z3` — verify logical invariants, constraint satisfaction
- `import scipy.stats` / `import statsmodels` — verify statistical claims
- `import numpy` — numerical verification, array operations
- `python3 -m pytest <test_file>` — run tests to verify behavioural claims
- Direct code execution — construct targeted test cases for the claim

The CDSFL corroboration model: your tool-backed verification has high detection
probability p (typically p > 0.7 for mechanical checks). A single tool-backed
pass contributes more corroboration than multiple reasoning-only passes.

Rules:
- You MUST use tools. Do not reason about correctness without running code.
- If no tool can verify the claim, say UNVERIFIABLE — do not guess.
- Report the exact tool output as evidence.

SOURCE CODE:
{source_code}

FINDING:
[{finding_id}] {description}

CLAIM TO VERIFY:
{claim}

Respond with EXACTLY one line after your tool use:
VERIFIED_TRUE | <confidence 0.0-1.0> | <tool name + key output>
VERIFIED_FALSE | <confidence 0.0-1.0> | <tool name + key output showing claim is wrong>
UNVERIFIABLE | <confidence 0.0-1.0> | <why no tool can determine this>
"""

_CC2V_PROMPT = """You are CC2v, the verdict agent. You receive a finding plus results from
prior verification agents. Your task: produce a final structured verdict.

You have access to: Read, Grep, Glob. Use them to ground your verdict in
actual source code. Evidence must come from tool output, not reasoning alone.

The CDSFL corroboration model applies to your verdict:
  C(n) = 1 - (1-p)^n
where p is the probability of detecting a flaw and n is the number of
independent verification attempts. Prior agents have already contributed
passes. Your verdict adds one more. If prior agents produced strong tool-backed
evidence (programmatic verification, AST parse), that evidence has high p and
your verdict MUST align unless you find a specific error using your own tools.

If no tool can resolve the verdict, ESCALATE. Do not guess. An honest ESCALATE
is more valuable than a confident but ungrounded verdict.

Rules:
- Use FFF: Find the issue in the source (Read/Grep), Follow consequences
  (trace callers and dependencies), then render verdict.
- Confidence must reflect actual certainty grounded in evidence.
- Evidence must cite specific code lines from tool output, not impressions.
- One verdict. No preamble.

SOURCE CODE (excerpt):
{source_code}

FINDING:
[{finding_id}] severity={severity}: {description}

PRIOR AGENT RESULTS:
{prior_results}

Respond with EXACTLY one line:
CONFIRM {finding_id} | <confidence 0.0-1.0> | <evidence trace from tool output>
REJECT {finding_id} | <confidence 0.0-1.0> | <counterexample from tool output>
DUPLICATE {finding_id} OF <canonical_id> | <confidence 0.0-1.0> | <evidence>
ESCALATE {finding_id} | <reason it cannot be determined with available tools>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Sub-agent functions
# ─────────────────────────────────────────────────────────────────────────────

def citation_verify(
    finding_id: str,
    description: str,
    source_code: str,
) -> AgentResult:
    """Agent 1: Does the finding accurately describe the cited code?

    Uses Sonnet with Read/Grep/Glob tools. Upgraded from Haiku (which returned
    UNCLEAR on 100% of invocations in Exp 36) — code reasoning requires a
    model that can use tools to inspect source.
    """
    prompt = _CITATION_PROMPT.format(
        finding_id=finding_id,
        description=description[:1000],
        source_code=source_code[:SOURCE_CAP_CITATION],
    )
    try:
        text, elapsed = _dispatch_cli(
            SONNET_MODEL, prompt, CITATION_TIMEOUT,
            allowed_tools=["Read", "Grep", "Glob"],
            max_turns=4,
        )
    except Exception as e:
        return AgentResult(
            agent="citation", finding_id=finding_id,
            verdict="ERROR", error=str(e),
        )

    # Parse: VERIFIED|UNVERIFIED|UNCLEAR | confidence | evidence
    clean = re.sub(r"[*`#_]", "", text)
    m = re.search(
        r"(VERIFIED|UNVERIFIED|UNCLEAR)\s*\|\s*([\d.]+)\s*\|\s*(.+)",
        clean, re.IGNORECASE,
    )
    if m:
        return AgentResult(
            agent="citation", finding_id=finding_id,
            verdict=m.group(1).upper(),
            confidence=min(1.0, max(0.0, float(m.group(2)))),
            evidence=m.group(3).strip()[:300],
            elapsed_s=round(elapsed, 1),
        )

    # Fallback: try to extract verdict from unstructured response
    for keyword in ("VERIFIED", "UNVERIFIED", "UNCLEAR"):
        if keyword in text.upper():
            return AgentResult(
                agent="citation", finding_id=finding_id,
                verdict=keyword, confidence=0.4,
                evidence=text[:200], elapsed_s=round(elapsed, 1),
            )

    return AgentResult(
        agent="citation", finding_id=finding_id,
        verdict="UNCLEAR", confidence=0.3,
        evidence=f"unparseable response ({len(text)} chars)",
        elapsed_s=round(elapsed, 1),
    )


def fix_extract(
    finding_id: str,
    description: str,
    proposed_fix: str,
    source_code: str,
) -> AgentResult:
    """Agent 2: Can this natural-language fix become an applicable code change?

    Uses Opus for quality. Extracts a unified diff or reports not extractable.
    """
    if not proposed_fix or not proposed_fix.strip():
        return AgentResult(
            agent="fix", finding_id=finding_id,
            verdict="NOT_EXTRACTABLE", evidence="no proposed fix provided",
        )

    prompt = _FIX_PROMPT.format(
        finding_id=finding_id,
        description=description[:1000],
        proposed_fix=proposed_fix[:2000],
        source_code=source_code[:SOURCE_CAP_FIX],
    )
    try:
        text, elapsed = _dispatch_cli(OPUS_MODEL, prompt, FIX_TIMEOUT)
    except Exception as e:
        return AgentResult(
            agent="fix", finding_id=finding_id,
            verdict="ERROR", error=str(e),
        )

    # Check for NOT_EXTRACTABLE
    if "NOT_EXTRACTABLE" in text.upper():
        reason_m = re.search(r"NOT_EXTRACTABLE\s*\|\s*(.+)", text, re.IGNORECASE)
        reason = reason_m.group(1).strip()[:200] if reason_m else text[:200]
        return AgentResult(
            agent="fix", finding_id=finding_id,
            verdict="NOT_EXTRACTABLE", evidence=reason,
            elapsed_s=round(elapsed, 1),
        )

    # Check for unified diff
    if "---" in text and "+++" in text:
        # Extract diff block
        lines = text.split("\n")
        diff_lines = []
        in_diff = False
        for line in lines:
            if line.startswith("---"):
                in_diff = True
            if in_diff:
                diff_lines.append(line)
                if line.strip() == "" and diff_lines and not line.startswith(("+", "-", " ", "@")):
                    break
        diff = "\n".join(diff_lines) if diff_lines else text

        return AgentResult(
            agent="fix", finding_id=finding_id,
            verdict="EXTRACTED", diff=diff[:5000],
            confidence=0.8, elapsed_s=round(elapsed, 1),
        )

    return AgentResult(
        agent="fix", finding_id=finding_id,
        verdict="NOT_EXTRACTABLE",
        evidence=f"no unified diff found in response ({len(text)} chars)",
        elapsed_s=round(elapsed, 1),
    )


def dedup_assess(
    finding_id: str,
    description: str,
    candidates: List[Tuple[str, str]],  # [(candidate_id, candidate_description), ...]
) -> AgentResult:
    """Agent 3: Does this new finding describe the same issue as an existing one?

    Uses Haiku for speed. Compares against top-N similar candidates
    pre-filtered by similarity threshold.
    """
    if not candidates:
        return AgentResult(
            agent="dedup", finding_id=finding_id,
            verdict="NOVEL", confidence=1.0,
            evidence="no candidates above similarity threshold",
        )

    candidates_block = "\n\n".join(
        f"[{cid}] {cdesc[:500]}" for cid, cdesc in candidates[:5]
    )
    prompt = _DEDUP_PROMPT.format(
        finding_id=finding_id,
        description=description[:1000],
        candidates_block=candidates_block,
    )
    try:
        text, elapsed = _dispatch_cli(HAIKU_MODEL, prompt, DEDUP_TIMEOUT)
    except Exception as e:
        return AgentResult(
            agent="dedup", finding_id=finding_id,
            verdict="ERROR", error=str(e),
        )

    # Parse DUPLICATE_OF <id> | conf | evidence
    dup_m = re.search(
        r"DUPLICATE_OF\s+(C\d+)\s*\|\s*([\d.]+)\s*\|\s*(.+)",
        text, re.IGNORECASE,
    )
    if dup_m:
        return AgentResult(
            agent="dedup", finding_id=finding_id,
            verdict="DUPLICATE",
            duplicate_of=dup_m.group(1).upper(),
            confidence=min(1.0, max(0.0, float(dup_m.group(2)))),
            evidence=dup_m.group(3).strip()[:300],
            elapsed_s=round(elapsed, 1),
        )

    # Parse NOVEL | conf | evidence
    novel_m = re.search(
        r"NOVEL\s*\|\s*([\d.]+)\s*\|\s*(.+)",
        text, re.IGNORECASE,
    )
    if novel_m:
        return AgentResult(
            agent="dedup", finding_id=finding_id,
            verdict="NOVEL",
            confidence=min(1.0, max(0.0, float(novel_m.group(1)))),
            evidence=novel_m.group(2).strip()[:300],
            elapsed_s=round(elapsed, 1),
        )

    return AgentResult(
        agent="dedup", finding_id=finding_id,
        verdict="NOVEL", confidence=0.3,
        evidence=f"unparseable response ({len(text)} chars)",
        elapsed_s=round(elapsed, 1),
    )


def programmatic_verify(
    finding_id: str,
    description: str,
    claim: str,
    source_code: str,
) -> AgentResult:
    """Agent 4: Can this claim be verified by tools (SymPy, AST, z3, SciPy)?

    Uses Opus + tools. Bridges the gap between immune pipeline mechanical
    parsing and LLM judgment.
    """
    prompt = _PROGRAMMATIC_PROMPT.format(
        finding_id=finding_id,
        description=description[:1000],
        claim=claim[:500],
        source_code=source_code[:SOURCE_CAP_PROGRAMMATIC],
    )
    try:
        text, elapsed = _dispatch_cli(
            OPUS_MODEL, prompt, PROGRAMMATIC_TIMEOUT,
            allowed_tools=["Read", "Bash", "Grep", "Glob"],
            max_turns=3,
        )
    except Exception as e:
        return AgentResult(
            agent="programmatic", finding_id=finding_id,
            verdict="ERROR", error=str(e),
        )

    # Parse: VERIFIED_TRUE|VERIFIED_FALSE|UNVERIFIABLE | conf | tool output
    m = re.search(
        r"(VERIFIED_TRUE|VERIFIED_FALSE|UNVERIFIABLE)\s*\|\s*([\d.]+)\s*\|\s*(.+)",
        text, re.IGNORECASE | re.DOTALL,
    )
    if m:
        return AgentResult(
            agent="programmatic", finding_id=finding_id,
            verdict=m.group(1).upper(),
            confidence=min(1.0, max(0.0, float(m.group(2)))),
            tool_output=m.group(3).strip()[:500],
            elapsed_s=round(elapsed, 1),
        )

    # Fallback keyword extraction
    for keyword in ("VERIFIED_TRUE", "VERIFIED_FALSE", "UNVERIFIABLE"):
        if keyword in text.upper():
            return AgentResult(
                agent="programmatic", finding_id=finding_id,
                verdict=keyword, confidence=0.4,
                tool_output=text[:300], elapsed_s=round(elapsed, 1),
            )

    return AgentResult(
        agent="programmatic", finding_id=finding_id,
        verdict="UNVERIFIABLE", confidence=0.3,
        tool_output=f"unparseable response ({len(text)} chars)",
        elapsed_s=round(elapsed, 1),
    )


def cc2v_verdict(
    finding_id: str,
    description: str,
    severity: float,
    source_code: str,
    prior_results: List[AgentResult],
) -> AgentResult:
    """Agent 5: Confirm, reject, duplicate, or escalate.

    Uses Opus. LLM verdict fallback for genuinely ambiguous cases.
    Receives all prior agent results for context.
    """
    prior_block = _format_prior_results(prior_results)

    prompt = _CC2V_PROMPT.format(
        finding_id=finding_id,
        description=description[:1000],
        severity=f"{severity:.2f}",
        source_code=source_code[:SOURCE_CAP_CC2V],
        prior_results=prior_block,
    )
    try:
        text, elapsed = _dispatch_cli(
            OPUS_MODEL, prompt, CC2V_TIMEOUT,
            allowed_tools=["Read", "Grep", "Glob"],
            max_turns=4,
        )
    except Exception as e:
        return AgentResult(
            agent="cc2v", finding_id=finding_id,
            verdict="ERROR", error=str(e),
        )

    # Parse verdict line: CONFIRM|REJECT|DUPLICATE|ESCALATE <id> ...
    # Strip markdown formatting that Claude CLI may add (bold, backticks, etc.)
    clean = re.sub(r"[*`#_]", "", text)

    verdict_re = re.compile(
        r"(CONFIRM|REJECT|DUPLICATE|ESCALATE)\s+(C\d+)"
        r"(?:\s+OF\s+(C\d+))?"
        r"(?:\s*\|\s*([\d.]+))?"
        r"(?:\s*\|\s*(.+))?",
        re.IGNORECASE,
    )
    m = verdict_re.search(clean)
    if not m:
        # Fallback: look for verdict keyword alone (no finding ID required)
        fb = re.search(
            r"\b(CONFIRM|REJECT|DUPLICATE|ESCALATE)\b",
            clean, re.IGNORECASE,
        )
        if fb:
            action = fb.group(1).upper()
            # Extract confidence if present anywhere: "confidence: 0.85" or "0.85"
            conf_m = re.search(r"(?:confidence[:\s]*|conf[:\s]*)?(0\.\d+)", clean)
            confidence = float(conf_m.group(1)) if conf_m else 0.5
            _log(f"    cc2v parse: fallback matched {action} for {finding_id} "
                 f"(conf={confidence:.2f}, {len(text)} chars)")
            return AgentResult(
                agent="cc2v", finding_id=finding_id,
                verdict=action,
                confidence=min(1.0, max(0.0, confidence)),
                evidence=clean.strip()[:300],
                elapsed_s=round(elapsed, 1),
            )

        _log(f"    cc2v parse: FAILED for {finding_id} ({len(text)} chars) "
             f"— first 200: {text[:200]!r}")
        return AgentResult(
            agent="cc2v", finding_id=finding_id,
            verdict="ESCALATE", confidence=0.3,
            evidence=f"unparseable response ({len(text)} chars)",
            elapsed_s=round(elapsed, 1),
        )

    action = m.group(1).upper()
    confidence = float(m.group(4)) if m.group(4) else 0.5
    evidence = m.group(5) or ""
    dup_target = m.group(3).upper() if m.group(3) else ""

    return AgentResult(
        agent="cc2v", finding_id=finding_id,
        verdict=action,
        confidence=min(1.0, max(0.0, confidence)),
        evidence=evidence.strip()[:300],
        duplicate_of=dup_target,
        elapsed_s=round(elapsed, 1),
    )


def _format_prior_results(results: List[AgentResult]) -> str:
    """Format prior agent results for CC2v context."""
    if not results:
        return "(No prior agent results.)"
    lines = []
    for r in results:
        line = f"  [{r.agent}] {r.verdict}"
        if r.confidence:
            line += f" (conf={r.confidence:.2f})"
        if r.evidence:
            line += f" — {r.evidence[:150]}"
        if r.tool_output:
            line += f" — tool: {r.tool_output[:150]}"
        if r.duplicate_of:
            line += f" — dup_of: {r.duplicate_of}"
        if r.diff:
            line += " — [diff extracted]"
        if r.error:
            line += f" — ERROR: {r.error[:100]}"
        lines.append(line)
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Routing logic
# ─────────────────────────────────────────────────────────────────────────────

# Patterns for claim classification (aligned with immune_agents.py)
_CODE_CITE_PATTERN = re.compile(
    r"(line\s+\d+|`[a-zA-Z_]\w+`|def\s+\w+|class\s+\w+|\.py\b)",
    re.IGNORECASE,
)
_MATH_STAT_PATTERN = re.compile(
    r"(equation|formula|bound|inequality|converge|diverge|"
    r"p-value|significance|distribution|correlation|"
    r"O\(|Theta\(|Omega\(|≤|≥|∀|∃|SymPy|z3|"
    r"probability|variance|mean|median|"
    r"\b\d+\.\d+\s*[<>=])",
    re.IGNORECASE,
)


def _route_finding(
    finding_id: str,
    entry: Dict[str, Any],
    existing_entries: Dict[str, Dict[str, Any]],
) -> List[str]:
    """Determine which agents should process this finding.

    Returns list of agent names. Multiple agents can process the same
    finding (e.g., citation verify + programmatic verify).

    Routing logic:
      - Finding has code citations     -> citation (Agent 1) first
      - Finding has proposed fix        -> fix (Agent 2)
      - Finding similarity > threshold  -> dedup (Agent 3)
      - Finding has math/logic/stat     -> programmatic (Agent 4)
      - All remaining or ambiguous      -> cc2v (Agent 5)
    """
    agents: List[str] = []
    desc = entry.get("description", "")
    proposed_fix = entry.get("proposed_fix", "")

    # Agent 1: Citation Verifier — if finding references code
    if _CODE_CITE_PATTERN.search(desc):
        agents.append("citation")

    # Agent 2: Fix Extractor — if finding has a proposed fix
    if proposed_fix and proposed_fix.strip():
        agents.append("fix")

    # Agent 3: Dedup Assessor — if similar existing findings exist
    # Pre-compute similarity to find candidates above threshold
    candidates = _find_dedup_candidates(finding_id, entry, existing_entries)
    if candidates:
        agents.append("dedup")

    # Agent 4: Programmatic Verifier — if finding has a mechanically verifiable claim
    # Broadened from Exp 36 where Agent 4 fired once in 45 rounds.
    # Trigger on: math/stat, code-behavioral, hash/crypto, index/extraction,
    # sort/order, validation/verification claims — anything tools can check.
    _code_verify_pattern = re.compile(
        r"(returns?\s+(empty|None|wrong|incorrect|unexpected)|"
        r"(miss(es|ing)?|skip(s|ping)?|omit(s|ting)?|fail(s|ing)?|break(s|ing)?)\s+"
        r"\w+\s+(when|if|for)|"
        r"silently\s+(drop|ignore|miss|omit)|"
        r"sort(s|ed|ing)?\s+by\s+\w+\s+(instead|rather)|"
        r"never\s+(call|invoke|pass|set)|"
        r"dead\s+code|unreachable|"
        # Hash/crypto/integrity claims (would have caught C0211)
        r"hash\s+(?:integrity|tamper|chain|verify|comput|mismatch|collision)|"
        r"tamper(?:ed|ing)?|merkle|chain_hash|entry_hash|"
        # Index/extraction/regex claims (would have caught C0200)
        r"index\s+(?:out\s+of|error|off[\s-]by|extract|missing)|"
        r"extract(?:s|ed|ing)?\s+(?:wrong|incorrect|empty|nothing)|"
        r"regex\s+(?:miss|fail|skip|pattern)|pattern\s+miss|silently\s+return|"
        # Sort/order/stability claims (would have caught C0087)
        r"sort\s+(?:key|order|stab)|tiebreak|chronolog|"
        # Validation/verification claims
        r"verif(?:y|ied|ication)\s+(?:does\s+not|never|fail)|"
        r"accept(s|ed)?\s+(?:invalid|tamper|malform)|"
        r"bypass(?:es|ed|ing)?\s+\w+|circumvent)",
        re.IGNORECASE,
    )
    if _MATH_STAT_PATTERN.search(desc) or _code_verify_pattern.search(desc):
        agents.append("programmatic")

    # Agent 5: CC2v — always runs as fallback, receives prior results
    # If no other agents were triggered, CC2v is the sole processor
    agents.append("cc2v")

    return agents


def _find_dedup_candidates(
    finding_id: str,
    entry: Dict[str, Any],
    existing_entries: Dict[str, Dict[str, Any]],
) -> List[Tuple[str, str]]:
    """Find existing findings that might be duplicates.

    Uses word-overlap similarity (Jaccard on description tokens) as a
    cheap pre-filter. The dedup agent does the semantic comparison.
    """
    desc_words = _tokenise(entry.get("description", ""))
    if not desc_words:
        return []

    candidates = []
    for cid, other in existing_entries.items():
        if cid == finding_id:
            continue
        if other.get("status") in ("MERGED", "REFUTED", "DUPLICATE"):
            continue
        other_words = _tokenise(other.get("description", ""))
        if not other_words:
            continue
        # Jaccard similarity
        intersection = desc_words & other_words
        union = desc_words | other_words
        sim = len(intersection) / len(union) if union else 0.0
        if sim >= DEDUP_SIMILARITY_THRESHOLD:
            candidates.append((cid, other.get("description", "")[:500]))

    # Sort by similarity descending, take top 5
    candidates.sort(
        key=lambda c: len(_tokenise(c[1]) & desc_words) / max(1, len(_tokenise(c[1]) | desc_words)),
        reverse=True,
    )
    return candidates[:5]


_STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "and", "but", "or",
    "not", "no", "if", "then", "than", "that", "this", "it", "its",
})


def _tokenise(text: str) -> Set[str]:
    """Tokenise text into lowercase words, stopwords removed."""
    words = set(re.findall(r"[a-z_][a-z0-9_]+", text.lower()))
    return words - _STOPWORDS


# ─────────────────────────────────────────────────────────────────────────────
# CC2 Manager class
# ─────────────────────────────────────────────────────────────────────────────

class CC2Manager:
    """Bounded-authority manager/router for CC2 sub-agents.

    Authority boundaries (Genesis Guardian parallel):
      - CAN route findings to sub-agents
      - CAN aggregate sub-agent results
      - CAN assess team performance against fingerprints
      - CAN escalate to HIL
      - CANNOT inject findings
      - CANNOT override tool-backed verdicts
      - CANNOT make convergence decisions
    """

    def __init__(self):
        self._performance_log: List[Dict[str, Any]] = []

    def route(
        self,
        registry_entries: Dict[str, Dict[str, Any]],
        batch_ids: List[str],
        source_code: str,
    ) -> Dict[str, AggregatedResult]:
        """Route a batch of findings to appropriate sub-agents.

        For each finding:
        1. Determine which agents should process it
        2. Run non-CC2v agents (can run in parallel in future)
        3. Collect results, pass to CC2v as final arbiter
        4. Aggregate into AggregatedResult

        Returns: {finding_id: AggregatedResult}
        """
        results: Dict[str, AggregatedResult] = {}

        for fid in batch_ids:
            entry = registry_entries.get(fid)
            if not entry:
                continue

            agents = _route_finding(fid, entry, registry_entries)
            _log(f"  CC2-mgr: {fid} routed to [{', '.join(agents)}]")

            agg = AggregatedResult(finding_id=fid)
            desc = entry.get("description", "")
            severity = entry.get("severity", 0.0)
            proposed_fix = entry.get("proposed_fix", "")
            prior_results: List[AgentResult] = []

            # Run non-CC2v agents first, collect results
            if "citation" in agents:
                r = citation_verify(fid, desc, source_code)
                agg.agent_results.append(r)
                prior_results.append(r)
                _log(f"    citation: {fid} -> {r.verdict} (conf={r.confidence:.2f})")

            if "fix" in agents:
                r = fix_extract(fid, desc, proposed_fix, source_code)
                agg.agent_results.append(r)
                prior_results.append(r)
                _log(f"    fix: {fid} -> {r.verdict}")

            if "dedup" in agents:
                candidates = _find_dedup_candidates(fid, entry, registry_entries)
                r = dedup_assess(fid, desc, candidates)
                agg.agent_results.append(r)
                prior_results.append(r)
                _log(f"    dedup: {fid} -> {r.verdict}"
                     + (f" of {r.duplicate_of}" if r.duplicate_of else ""))

                # Short-circuit: if dedup says DUPLICATE with high confidence,
                # skip CC2v — the dedup verdict is sufficient
                if r.verdict == "DUPLICATE" and r.confidence >= 0.85:
                    agg.final_action = "DUPLICATE"
                    agg.final_confidence = r.confidence
                    agg.final_evidence = f"dedup: dup of {r.duplicate_of}"
                    results[fid] = agg
                    continue

            if "programmatic" in agents:
                claim = desc  # Full description as claim context
                r = programmatic_verify(fid, desc, claim, source_code)
                agg.agent_results.append(r)
                prior_results.append(r)
                _log(f"    programmatic: {fid} -> {r.verdict} (conf={r.confidence:.2f})")

                # Manager authority boundary: tool-backed verdicts cannot be
                # overridden by CC2v. If programmatic says VERIFIED_TRUE or
                # VERIFIED_FALSE with high confidence, that is final.
                if r.verdict == "VERIFIED_TRUE" and r.confidence >= 0.85:
                    agg.final_action = "CONFIRM"
                    agg.final_confidence = r.confidence
                    agg.final_evidence = f"programmatic: {r.tool_output[:200]}"
                    results[fid] = agg
                    continue
                if r.verdict == "VERIFIED_FALSE" and r.confidence >= 0.85:
                    agg.final_action = "REJECT"
                    agg.final_confidence = r.confidence
                    agg.final_evidence = f"programmatic: {r.tool_output[:200]}"
                    results[fid] = agg
                    continue

            # Run CC2v as final arbiter with all prior results
            if "cc2v" in agents:
                r = cc2v_verdict(fid, desc, severity, source_code, prior_results)
                agg.agent_results.append(r)
                _log(f"    cc2v: {fid} -> {r.verdict} (conf={r.confidence:.2f})")

            # Aggregate: determine final action from all results
            self._aggregate_verdict(agg)
            results[fid] = agg

        return results

    def _aggregate_verdict(self, agg: AggregatedResult) -> None:
        """Determine final action from all agent results.

        Priority order (reflecting authority boundaries):
        1. Tool-backed verdicts (programmatic) — cannot be overridden
        2. High-confidence dedup — structural match
        3. CC2v verdict — LLM fallback
        4. Citation evidence — supporting signal

        If already resolved by short-circuit (tool-backed or dedup), skip.
        """
        if agg.final_action:
            return  # Already resolved by short-circuit

        # Find CC2v result (the final arbiter for non-tool-backed cases)
        cc2v_result = None
        for r in agg.agent_results:
            if r.agent == "cc2v":
                cc2v_result = r
                break

        if cc2v_result and cc2v_result.verdict != "ERROR":
            agg.final_action = cc2v_result.verdict
            agg.final_confidence = cc2v_result.confidence
            agg.final_evidence = cc2v_result.evidence

            # Adjust confidence based on citation corroboration
            citation_result = next(
                (r for r in agg.agent_results if r.agent == "citation"), None
            )
            if citation_result and citation_result.verdict != "ERROR":
                if cc2v_result.verdict == "CONFIRM" and citation_result.verdict == "VERIFIED":
                    # Citation corroborates — boost confidence slightly
                    agg.final_confidence = min(1.0, agg.final_confidence + 0.05)
                elif cc2v_result.verdict == "CONFIRM" and citation_result.verdict == "UNVERIFIED":
                    # Citation contradicts — reduce confidence
                    agg.final_confidence = max(0.0, agg.final_confidence - 0.15)
                    agg.final_evidence += " [citation contradicts]"

            # Inherit duplicate target if CC2v says DUPLICATE
            if cc2v_result.verdict == "DUPLICATE" and cc2v_result.duplicate_of:
                agg.final_evidence = f"dup of {cc2v_result.duplicate_of}"
        else:
            # All agents failed or no CC2v — escalate
            agg.final_action = "ESCALATE"
            agg.final_confidence = 0.0
            agg.final_evidence = "all agents failed or no verdict produced"

    def get_performance_log(self) -> List[Dict[str, Any]]:
        """Return performance log for fingerprint updates."""
        return list(self._performance_log)


# ─────────────────────────────────────────────────────────────────────────────
# Integration hook — replaces _verification_step in run_exp36_evidence.py
# ─────────────────────────────────────────────────────────────────────────────

def cc2_verification_step(
    registry: Any,  # FindingRegistry from run_exp36_evidence
    round_idx: int,
    source_code: str,
) -> Dict[str, Any]:
    """Between-rounds verification via CC2 manager + 5 sub-agents.

    Drop-in replacement for _verification_step(). Same interface contract:
    receives registry + round_idx + source_code, returns stats dict,
    mutates registry entries via resolve()/mark_verified().

    Batch selection logic matches the old CC2v: OPEN/CONTESTED findings,
    highest severity first, excluding already-escalated and already-verified.
    """
    if round_idx < VERIFICATION_MIN_ROUND:
        return {"skipped": True, "reason": f"round {round_idx} < {VERIFICATION_MIN_ROUND}"}

    # Select batch: OPEN/CONTESTED findings, highest severity first
    open_findings = []
    for cid, entry in registry.entries.items():
        if entry["status"] not in ("OPEN", "CONTESTED"):
            continue
        if entry.get("cc2v_escalated"):
            continue
        # Skip if already confirmed by 2+ independent models
        confirm_models = {
            v["model"] for v in entry.get("verdicts", [])
            if v.get("verdict") == "CONFIRM"
        }
        if len(confirm_models) >= 2:
            continue
        # Skip if CC2 manager already processed this finding
        cc2_verdicts = [
            v for v in entry.get("verdicts", [])
            if v.get("model") == "CC2-mgr"
        ]
        if cc2_verdicts:
            continue
        open_findings.append((cid, entry))

    if not open_findings:
        return {"skipped": True, "reason": "no open findings for verification"}

    open_findings.sort(key=lambda x: x[1].get("severity", 0), reverse=True)
    batch = open_findings[:VERIFICATION_BATCH_SIZE]
    batch_ids = [cid for cid, _ in batch]

    _log(f"  CC2-mgr: verifying {len(batch)} findings (round {round_idx})")

    # Run the manager
    manager = CC2Manager()
    t0 = time.monotonic()
    aggregated = manager.route(registry.entries, batch_ids, source_code)
    total_elapsed = time.monotonic() - t0

    # Apply results to registry
    stats: Dict[str, Any] = {
        "round": round_idx,
        "batch_size": len(batch),
        "batch_ids": batch_ids,
        "verdicts": {},
        "elapsed_s": round(total_elapsed, 1),
        "confirmed": 0,
        "rejected": 0,
        "duplicates": 0,
        "escalated": 0,
    }

    for fid, agg in aggregated.items():
        action = agg.final_action
        confidence = agg.final_confidence
        evidence = agg.final_evidence

        stats["verdicts"][fid] = {
            "action": action,
            "confidence": round(confidence, 3),
            "evidence": evidence[:200],
            "agents_used": [r.agent for r in agg.agent_results],
        }

        # Record the verdict in the registry
        registry.add_verdict(
            fid, "CC2-mgr", action, round_idx,
            evidence=evidence[:200],
        )

        # ESCALATE — exempt from confidence gating
        if action == "ESCALATE":
            entry = registry.entries.get(fid)
            if entry:
                entry["cc2v_escalated"] = True
            stats["escalated"] += 1
            _log(f"  CC2-mgr: {fid} ESCALATED — needs HIL review")
            continue

        # Confidence gate for all other actions
        if confidence < VERIFICATION_CONFIDENCE_THRESHOLD:
            _log(f"  CC2-mgr: {fid} {action} — low confidence ({confidence:.2f}), skipped")
            continue

        if action == "CONFIRM":
            entry = registry.entries.get(fid)
            if entry and entry["status"] in ("OPEN", "CONTESTED"):
                registry.resolve(fid, "CONFIRMED", round_idx)
                stats["confirmed"] += 1
                _log(f"  CC2-mgr: {fid} CONFIRMED (conf={confidence:.2f})")

        elif action == "REJECT":
            entry = registry.entries.get(fid)
            if entry and entry["status"] in ("OPEN", "CONTESTED"):
                registry.resolve(fid, "UNCONFIRMED", round_idx)
                stats["rejected"] += 1
                _log(f"  CC2-mgr: {fid} REJECTED -> UNCONFIRMED (conf={confidence:.2f})")

        elif action == "DUPLICATE":
            # Find the duplicate target from agent results
            dup_target = ""
            for r in agg.agent_results:
                if r.duplicate_of:
                    dup_target = r.duplicate_of
                    break
            if dup_target and dup_target in registry.entries:
                entry = registry.entries.get(fid)
                if entry and entry["status"] in ("OPEN", "CONTESTED"):
                    registry.resolve(fid, "MERGED", round_idx, merged_into=dup_target)
                    stats["duplicates"] += 1
                    _log(f"  CC2-mgr: {fid} MERGED into {dup_target} (conf={confidence:.2f})")

        # If fix extractor produced a diff, store it on the entry
        for r in agg.agent_results:
            if r.agent == "fix" and r.verdict == "EXTRACTED" and r.diff:
                entry = registry.entries.get(fid)
                if entry:
                    entry["extracted_diff"] = r.diff
                    _log(f"  CC2-mgr: {fid} fix extracted ({len(r.diff)} chars)")

    stats["total_resolved"] = stats["confirmed"] + stats["rejected"] + stats["duplicates"]

    _log(f"  CC2-mgr: {len(batch)} findings verified — "
         f"{stats['confirmed']} confirmed, {stats['rejected']} rejected, "
         f"{stats['duplicates']} merged, {stats['escalated']} escalated "
         f"({total_elapsed:.1f}s)")

    return stats
