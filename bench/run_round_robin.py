#!/usr/bin/env python3
"""
Round-robin distributed compute test — Experiment 4.

Tests the biodiversity hypothesis: does heterogeneous multi-architecture
review under CDSFL find more defects than monoculture review?

FOUR-CONDITION 2×2 FACTORIAL DESIGN:
  Condition 1 (control):   Raw prompt only — no CDSFL directives, no expert
                           guidance. Baseline capability measurement.
  Condition 2 (hil):       Structured domain-expert guidance from CC as
                           simulated HIL — pointed questions, steering, but
                           no formal CDSFL framework.
  Condition 3 (cdsfl):     Full CDSFL framework — G_n formula, HARD/SOFT
                           classification, Bayesian expertise parameter,
                           cryptographic hashing per full schema. NO expert
                           guidance (tests formal structure in isolation).
  Condition 4 (cdsfl_hil): Full CDSFL framework PLUS domain-expert guidance.
                           This is the complete methodology as practiced:
                           structure + expertise. Subsumes both conditions
                           2 and 3.

  2×2 factorial:
                    No Structure    Full CDSFL Structure
  No Guidance       1. control      3. cdsfl
  Expert Guidance   2. hil          4. cdsfl_hil

What this tests:
  Control vs HIL      = what does expert guidance alone add?
  Control vs CDSFL    = what does formal structure alone add?
  HIL vs CDSFL_HIL    = what does structure add on top of guidance?
  CDSFL vs CDSFL_HIL  = what does guidance add on top of structure?
  (HIL+CDSFL) vs CDSFL_HIL = is the combination more than the sum?
  All four × 3 architectures = biodiversity interaction effect.

Topology:
  - CC (Opus 4.6): Orchestrator, simulated domain expert, final arbiter.
  - DeepSeek V3.2: Heterogeneous falsifier #1 (OpenAI-compatible API).
  - CX (Codex 5.3): Heterogeneous falsifier #2 (codex exec CLI).

Protocol per task per condition:
  Round 1 (blind):   CC generates solution; DeepSeek and Codex independently
                     review (neither sees the other's findings).
  Rounds 2-5 (confer): Each reviewer receives the OTHER reviewer's
                        findings. CC assesses combined output.
  Stop rule:         Two consecutive rounds with zero novel HARD findings
                     AND both DeepSeek and Codex concur → stop.
  Hard cap:          5 rounds total.

DeepSeek failure policy:
  1. Retry with exponential backoff (3 attempts)
  2. After 3 failures: raise DeepSeekExhausted, stop-and-diagnose with CX

Verification chain (CDSFL layers 1-3):
  Layer 1: SHA-256 content hash of every artifact.
  Layer 2: Hash chain — each record links to its predecessor.
  Layer 3: Epoch Merkle tree — per-task Merkle root over all round hashes.

Usage:
    # Phase 2 smoke test (3 tasks × 4 conditions, persistent conversations)
    python3 bench/run_round_robin.py --phase2 --smoke

    # Phase 2 smoke with custom tasks
    python3 bench/run_round_robin.py --phase2 --smoke --tasks ft-001,ft-006,ft-013

    # Phase 2 full run (25 tasks × 4 conditions = 100 runs)
    python3 bench/run_round_robin.py --phase2

    # Phase 2 resume after crash
    python3 bench/run_round_robin.py --phase2 --resume

    # Phase 1 (legacy stateless — retained for backward compatibility)
    python3 bench/run_round_robin.py --smoke

    # Dry run (validate tasks and config only)
    python3 bench/run_round_robin.py --dry-run

    # Single condition only
    python3 bench/run_round_robin.py --phase2 --condition cdsfl
"""

import argparse
import hashlib
import json
import os
import subprocess as sp
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Load .env file at import time — ensures API keys are available.
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                if _line.startswith("export "):
                    _line = _line[7:]
                _key, _, _val = _line.partition("=")
                os.environ.setdefault(_key.strip(), _val.strip())

# Safety guard: ANTHROPIC_API_KEY forces claude -p to use pay-per-token API
# instead of subscription auth. This burned API credits in Phase 2 smoke test 1.
# If it's set, warn and remove it. CC must use subscription auth.
if "ANTHROPIC_API_KEY" in os.environ:
    print("WARNING: ANTHROPIC_API_KEY is set — removing to force subscription auth. "
          "claude -p must use CLI subscription, not API credits.",
          file=sys.stderr, flush=True)
    del os.environ["ANTHROPIC_API_KEY"]

from experiment_11_orchestrator import CLAUDE_CLI
from run_benchmark import (
    ADVERSARIAL_PASS_TEMPLATE,
    CDSFL_DIRECTIVES,
    INITIAL_PASS_TEMPLATE,
    FOLLOWUP_PASS_TEMPLATE,
    _err,
    _extract_section,
    _safe_format,
    classify_issue_severity,
    compose_directives,
    load_directives,
    load_domain_directives,
    load_tasks,
)

from cdsfl_registry.registry import (
    load_effective_policy,
    validate_all_policies,
    PolicyViolationError,
)
from cdsfl_registry.refinements import (
    classify_finding_support,
    count_independent_confirmations,
    structural_canon_hash,
    MODEL_FAMILIES,
)

# Override _err with timestamped version — founder needs timestamps to
# distinguish "stuck" from "slow" during long runs.
def _err(msg: str) -> None:
    """Print to stderr with timestamp and forced flush."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


# Frontier tasks have a different schema than seeded-fault tasks.
REQUIRED_FRONTIER_FIELDS = {"id", "domain", "prompt", "ground_truth_notes"}


def validate_frontier_task(task: dict[str, Any]) -> list[str]:
    """Validate a frontier task (no seeded_faults required)."""
    errors = []
    source = task.get("_source_file", "<unknown>")
    missing = REQUIRED_FRONTIER_FIELDS - task.keys()
    if missing:
        errors.append(f"{source}: missing fields: {missing}")
    return errors


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESULTS_DIR = Path(__file__).parent / "results" / "round_robin"
RESULTS_DIR_PHASE2 = Path(__file__).parent / "results" / "round_robin_phase2"
LOGS_DIR = Path(__file__).parent / "logs"
TASKS_DIR = Path(__file__).parent / "tasks_frontier"
SMOKE_TASK_IDS = ["ft-001"]  # Phase 1: single task
SMOKE_TASK_IDS_PHASE2 = ["ft-001", "ft-006", "ft-013"]  # Phase 2: 3 tasks (maths, code, cross-domain)
ALL_CONDITIONS = ("control", "hil", "cdsfl", "cdsfl_hil")
MAX_ROUNDS = 5
DEEPSEEK_MAX_ATTEMPTS = 3  # DeepSeek: 3 attempts with exponential backoff
CONFER_START_ROUND = 1  # blind review IS round 1

# Canonical reviewer list — all loops that iterate over reviewers use this.
REVIEWERS = ("cc", "deepseek", "cx", "gemini", "chatgpt")

# Timeout constants — FALLBACK defaults, used when registry policy load fails.
# When registry policies are available, model-specific timeouts are read from
# policy["model"]["timeout"] and passed to each chat class / call function.
DEEPSEEK_TIMEOUT = 300  # DeepSeek: 5 min per call (fallback)
CX_TIMEOUT = 600       # CX: 10 min (fallback)
CC_TIMEOUT = 1200      # CC per-step: 20 min (fallback)
CC_ARBITER_TIMEOUT = 120  # CC arbiter assessment: 2 min (bounded, non-fatal)
SAFETY_MARGIN = 60     # Budget safety margin (seconds)
PROMPT_SIZE_WARN = 50_000  # Warn if prompt exceeds this many chars

# Finding schema fields (normalised record)
FINDING_FIELDS = (
    "finding_id", "claim", "evidence_span", "constraint_class",
    "severity", "confidence", "proposed_check", "verifiable_claim",
)

# Registry model name mapping: script internal name -> registry filename (without .toml)
REGISTRY_MODEL_MAP = {
    "cc": "opus_4_6",
    "deepseek": "deepseek_v3",
    "cx": "codex_5_3",
    "gemini": "gemini_3_1_pro",
    "chatgpt": "chatgpt_5_4",
}

# Verified confer protocol constants (CDSFL conditions only)
VERIFY_CONTINUE_THRESHOLD = 0.8  # if aggregate >= this AND counting says stop, continue
VERIFY_MIN_SAMPLE = 3            # need at least this many determinate verifications to override


# ---------------------------------------------------------------------------
# Verification chain — CDSFL layers 1-3
# Canonical implementation: bench/verification_chain.py
# This section provides a compatibility adapter for the benchmark runner.
# ---------------------------------------------------------------------------

from verification_chain import (  # noqa: E402
    VerificationChain as _CanonicalChain,
    canonical_json as _canonical_json,
    sha256_digest as _sha256_digest,
    rfc9162_merkle_root as _rfc9162_root,
)


def _content_hash(data: str) -> str:
    """SHA-256 content hash of a string (bare hex, no prefix)."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class VerificationChain:
    """CDSFL verification chain — compatibility adapter.

    Wraps bench/verification_chain.py (the canonical implementation)
    to preserve the runner's existing call-site API. One implementation,
    one source of truth.
    """

    def __init__(self):
        self._chain = _CanonicalChain()
        self.entries: list[dict[str, str]] = []

    def record(self, artifact_type: str, content: str, metadata: dict | None = None) -> dict[str, str]:
        """Record an artifact in the chain. Returns the chain entry."""
        payload = {"content": content, "metadata": metadata}
        rec = self._chain.append_record(
            artifact_type=artifact_type,
            payload=payload,
            recorded_by="benchmark",
            metadata=metadata,
        )
        # Build a backward-compatible entry dict for the runner
        entry = {
            "seq": rec["sealed_body"]["seq"],
            "artifact_type": artifact_type,
            "content_hash": rec["sealed_body"]["payload_hash"],
            "chain_hash": rec["chain_hash"],
            "prev_hash": rec["prev_hash"],
            "entry_hash": rec["entry_hash"],
            "timestamp": rec["sealed_body"]["timestamp_utc"],
        }
        if metadata:
            entry["metadata"] = metadata
        self.entries.append(entry)
        return entry

    def merkle_root(self) -> str:
        """Layer 3: Compute RFC 9162 Merkle root over all chain hashes."""
        epoch = self._chain.seal_epoch()
        return epoch["merkle_root"]

    def verify_chain(self) -> tuple[bool, str]:
        """Verify the entire chain is intact. Returns (valid, message)."""
        return self._chain.verify_chain()

    def to_dict(self) -> dict:
        epoch = self._chain.seal_epoch()
        return {
            "entries": self.entries,
            "merkle_root": epoch["merkle_root"],
            "chain_length": len(self.entries),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VerificationChain":
        """Reconstruct chain from serialised form (for resume)."""
        chain = cls()
        chain.entries = data.get("entries", [])
        # Note: the canonical chain cannot be reconstructed from legacy
        # entries alone; this preserves the entry list for display purposes.
        return chain


# ---------------------------------------------------------------------------
# Canonical defect key (for dedup/novelty tracking)
# ---------------------------------------------------------------------------


def _defect_key(task_id: str, constraint_class: str, claim: str,
                finding: dict | None = None) -> str:
    """Canonical defect key using structural_canon_hash when structural fields exist.

    CX P-pass fix (SOFT 1): use full hash, not truncated 16-char.
    Finding 5 fix: prefer structural_canon_hash from refinements module
    for findings with structural fields. Falls back to raw claim hash
    only when structural fields are empty (which structural_canon_hash
    already handles internally).
    """
    if finding is not None:
        s_hash = structural_canon_hash(finding)
        # structural_canon_hash returns claim-based fallback when structural
        # fields are empty, so we always prefix with task_id for uniqueness.
        return hashlib.sha256(
            f"{task_id}:{constraint_class}:{s_hash}".encode("utf-8")
        ).hexdigest()
    # Legacy path: no finding dict available — raw claim hash
    normalised = claim.strip().lower()
    return hashlib.sha256(
        f"{task_id}:{constraint_class}:{normalised}".encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------------------
# Finding schema
# ---------------------------------------------------------------------------


BLIND_REVIEW_PROMPT = """\
You are an independent reviewer performing a CDSFL P-Pass. This output was \
produced by another system and has not been independently verified.

Original task:
{task_prompt}

Solution to review:
{solution}

Instructions:
1. Classify every constraint in the task as HARD (physics, mathematics, law, \
safety — non-negotiable) or SOFT (economic, preference, convenience — negotiable).
2. For each issue you find, produce a structured finding record with these fields:
   - finding_id: a short unique identifier (e.g. F1, F2, ...)
   - claim: what the solution claims or assumes
   - evidence_span: the relevant text from the solution
   - constraint_class: HARD or SOFT
   - severity: critical, major, or minor
   - confidence: 0.0 to 1.0 — your confidence this is a genuine error
   - proposed_check: how to verify whether this is actually wrong
   - verifiable_claim: (optional) for findings involving a mathematical claim, \
provide a SymPy-verifiable structured object with fields: "op" (eq/gt/lt/ge/le/eval), \
"lhs" (SymPy expression string), "rhs" (SymPy expression string), \
"symbols" (dict of symbol names to assumptions e.g. {{"a": "positive"}}), \
"description" (human-readable claim text). \
Example: {{"op": "gt", "lhs": "a*b", "rhs": "1 + 3*pi/2", \
"symbols": {{"a": "positive", "b": "positive"}}, \
"description": "product ab exceeds 1 + 3pi/2"}}
3. Focus on what is WRONG, not what is right.
4. Stop when all HARD constraint assumptions have been tested and remaining \
findings are below the real-world-consequence threshold.

Return your response in exactly this format:

CONSTRAINT_CLASSIFICATION:
- [list each constraint as HARD or SOFT with one-line justification]

FINDINGS:
[
  {{"finding_id": "F1", "claim": "...", "evidence_span": "...", \
"constraint_class": "HARD", "severity": "critical", "confidence": 0.9, \
"proposed_check": "...", "verifiable_claim": {{"op": "gt", "lhs": "a*b", \
"rhs": "1 + 3*pi/2", "symbols": {{"a": "positive", "b": "positive"}}, \
"description": "product ab exceeds 1 + 3pi/2"}}}},
  ...
]

SUMMARY:
[2-3 sentence summary of the most important issues found]
"""

CONFER_REVIEW_PROMPT = """\
You are reviewing another reviewer's findings on the same solution. Your task \
is to assess each finding and add any NEW issues they missed.

Original task:
{task_prompt}

Solution under review:
{solution}

Other reviewer's findings:
{other_findings}

Instructions:
1. For each of the other reviewer's findings, respond with:
   - finding_id: (matching theirs)
   - verdict: confirm / refute / uncertain
   - justification: one sentence explaining your assessment
2. Add any NEW findings they missed (use IDs starting after their highest). \
For each new finding involving a mathematical claim, include a 'verifiable_claim' \
field with a SymPy-verifiable structured object: {{"op": "eq"|"gt"|"lt"|"ge"|"le"|"eval", \
"lhs": "expression", "rhs": "expression", "symbols": {{"x": "positive"}}, \
"description": "human-readable"}}.
3. State whether you believe diminishing returns have been reached.

Return your response in exactly this format:

ASSESSMENTS:
[
  {{"finding_id": "F1", "verdict": "confirm", "justification": "..."}},
  ...
]

NEW_FINDINGS:
[
  {{"finding_id": "F10", "claim": "...", "evidence_span": "...", \
"constraint_class": "HARD", "severity": "major", "confidence": 0.8, \
"proposed_check": "..."}},
  ...
]

CONCUR_STOP: true/false
JUSTIFICATION: [1-2 sentences on whether diminishing returns are reached]
"""


# ---------------------------------------------------------------------------
# Condition-specific prompts
# ---------------------------------------------------------------------------

# CONTROL: Raw prompt only — no framework, no expert guidance
CONTROL_BLIND_PROMPT = """\
Review the following solution for errors, omissions, or incorrect assumptions.

Original task:
{task_prompt}

Solution to review:
{solution}

List any issues you find. For each issue, provide:
- finding_id: a short identifier (F1, F2, ...)
- claim: what the solution claims or assumes
- evidence_span: the relevant text
- constraint_class: HARD or SOFT
- severity: critical, major, or minor
- confidence: 0.0 to 1.0
- proposed_check: how to verify
- verifiable_claim: (optional) if the issue involves a mathematical or \
computational claim, express it as a SymPy-parseable object, e.g. \
{{"op": "gt", "lhs": "a*b", "rhs": "1 + 3*pi/2"}}

Return findings as a JSON array under a FINDINGS: heading.

FINDINGS:
[...]

SUMMARY:
[2-3 sentence summary]
"""

CONTROL_CONFER_PROMPT = """\
Another reviewer examined the same solution. Review their findings and add \
anything they missed.

Original task:
{task_prompt}

Solution under review:
{solution}

Other reviewer's findings:
{other_findings}

For each of their findings, state: confirm / refute / uncertain.
Add any NEW findings they missed.
State whether further review would be productive.

ASSESSMENTS:
[{{"finding_id": "F1", "verdict": "confirm", "justification": "..."}}, ...]

NEW_FINDINGS:
[{{"finding_id": "F10", "claim": "...", "evidence_span": "...", \
"constraint_class": "HARD", "severity": "major", "confidence": 0.8, \
"proposed_check": "...", \
"verifiable_claim": {{"op": "...", "lhs": "...", "rhs": "..."}} }}, ...]

CONCUR_STOP: true/false
JUSTIFICATION: [1-2 sentences]
"""

# HIL: Structured domain-expert guidance from CC (no formal CDSFL framework)
HIL_BLIND_PROMPT = """\
You are an independent reviewer with domain expertise relevant to this task. \
A domain expert has provided the following guidance for your review.

DOMAIN EXPERT GUIDANCE:
{expert_guidance}

Original task:
{task_prompt}

Solution to review:
{solution}

Instructions:
1. Use the expert guidance to focus your review on the most critical aspects.
2. For each issue found, produce a structured finding record:
   - finding_id: a short unique identifier (F1, F2, ...)
   - claim: what the solution claims or assumes
   - evidence_span: the relevant text from the solution
   - constraint_class: HARD or SOFT
   - severity: critical, major, or minor
   - confidence: 0.0 to 1.0
   - proposed_check: how to verify whether this is actually wrong
   - verifiable_claim: (optional) if the issue involves a mathematical or \
computational claim, express it as a SymPy-parseable object, e.g. \
{{"op": "gt", "lhs": "a*b", "rhs": "1 + 3*pi/2"}}
3. Focus on what is WRONG, not what is right.

FINDINGS:
[...]

SUMMARY:
[2-3 sentence summary of the most important issues found]
"""

HIL_CONFER_PROMPT = """\
You are reviewing another reviewer's findings with domain-expert guidance.

DOMAIN EXPERT GUIDANCE:
{expert_guidance}

Original task:
{task_prompt}

Solution under review:
{solution}

Other reviewer's findings:
{other_findings}

Instructions:
1. For each finding, respond with: confirm / refute / uncertain + justification.
2. Add any NEW findings they missed, informed by the expert guidance.
3. State whether diminishing returns have been reached.

ASSESSMENTS:
[{{"finding_id": "F1", "verdict": "confirm", "justification": "..."}}, ...]

NEW_FINDINGS:
[{{"finding_id": "F10", "claim": "...", "evidence_span": "...", \
"constraint_class": "HARD", "severity": "major", "confidence": 0.8, \
"proposed_check": "...", \
"verifiable_claim": {{"op": "...", "lhs": "...", "rhs": "..."}} }}, ...]

CONCUR_STOP: true/false
JUSTIFICATION: [1-2 sentences]
"""

# CDSFL + HIL: Full CDSFL framework PLUS domain-expert guidance.
# This is the complete methodology as practiced — subsumes both HIL and CDSFL.
CDSFL_HIL_BLIND_PROMPT = """\
You are an independent reviewer performing a CDSFL P-Pass. This output was \
produced by another system and has not been independently verified.

A domain expert has provided the following guidance for your review.

DOMAIN EXPERT GUIDANCE:
{expert_guidance}

Original task:
{task_prompt}

Solution to review:
{solution}

Instructions:
1. Classify every constraint in the task as HARD (physics, mathematics, law, \
safety — non-negotiable) or SOFT (economic, preference, convenience — negotiable).
2. Use the expert guidance to focus on the most critical domain-specific aspects.
3. For each issue you find, produce a structured finding record with these fields:
   - finding_id: a short unique identifier (e.g. F1, F2, ...)
   - claim: what the solution claims or assumes
   - evidence_span: the relevant text from the solution
   - constraint_class: HARD or SOFT
   - severity: critical, major, or minor
   - confidence: 0.0 to 1.0 — your confidence this is a genuine error
   - proposed_check: how to verify whether this is actually wrong
   - verifiable_claim: (optional) for findings involving a mathematical claim, \
provide a SymPy-verifiable structured object with fields: "op" (eq/gt/lt/ge/le/eval), \
"lhs" (SymPy expression string), "rhs" (SymPy expression string), \
"symbols" (dict of symbol names to assumptions e.g. {{"a": "positive"}}), \
"description" (human-readable claim text). \
Example: {{"op": "gt", "lhs": "a*b", "rhs": "1 + 3*pi/2", \
"symbols": {{"a": "positive", "b": "positive"}}, \
"description": "product ab exceeds 1 + 3pi/2"}}
4. Focus on what is WRONG, not what is right.
5. Stop when all HARD constraint assumptions have been tested and remaining \
findings are below the real-world-consequence threshold.

Return your response in exactly this format:

CONSTRAINT_CLASSIFICATION:
- [list each constraint as HARD or SOFT with one-line justification]

FINDINGS:
[
  {{"finding_id": "F1", "claim": "...", "evidence_span": "...", \
"constraint_class": "HARD", "severity": "critical", "confidence": 0.9, \
"proposed_check": "...", "verifiable_claim": {{"op": "gt", "lhs": "a*b", \
"rhs": "1 + 3*pi/2", "symbols": {{"a": "positive", "b": "positive"}}, \
"description": "product ab exceeds 1 + 3pi/2"}}}},
  ...
]

SUMMARY:
[2-3 sentence summary of the most important issues found]
"""

CDSFL_HIL_CONFER_PROMPT = """\
You are reviewing another reviewer's findings on the same solution, performing \
a CDSFL confer pass. A domain expert has provided guidance for this review.

DOMAIN EXPERT GUIDANCE:
{expert_guidance}

Original task:
{task_prompt}

Solution under review:
{solution}

Other reviewer's findings:
{other_findings}

Instructions:
1. For each of the other reviewer's findings, respond with:
   - finding_id: (matching theirs)
   - verdict: confirm / refute / uncertain
   - justification: one sentence explaining your assessment
2. Add any NEW findings they missed, informed by both the CDSFL constraint \
classification framework and the expert guidance. For each new finding involving \
a mathematical claim, include a 'verifiable_claim' field with a SymPy-verifiable \
structured object: {{"op": "eq"|"gt"|"lt"|"ge"|"le"|"eval", "lhs": "expression", \
"rhs": "expression", "symbols": {{"x": "positive"}}, "description": "human-readable"}}.
3. State whether you believe diminishing returns have been reached.

Return your response in exactly this format:

ASSESSMENTS:
[
  {{"finding_id": "F1", "verdict": "confirm", "justification": "..."}},
  ...
]

NEW_FINDINGS:
[
  {{"finding_id": "F10", "claim": "...", "evidence_span": "...", \
"constraint_class": "HARD", "severity": "major", "confidence": 0.8, \
"proposed_check": "..."}},
  ...
]

CONCUR_STOP: true/false
JUSTIFICATION: [1-2 sentences on whether diminishing returns are reached]
"""

# CC generates expert guidance for HIL condition (one-shot per task)
HIL_EXPERT_GUIDANCE_PROMPT = """\
You are a senior domain expert — the person a PhD student would go to \
when stuck. You have deep research-level knowledge in this problem domain. \
Your job is to provide SPECIFIC, TECHNICAL review guidance that only a \
genuine expert would know. Do NOT solve the task yourself.

Provide:

1. HARD CONSTRAINTS: The specific mathematical, physical, or logical \
constraints that MUST hold. Not generic ("check correctness") but specific \
("the Weierstrass M-test requires uniform convergence, not just pointwise — \
verify the reviewer checks |a^n cos(b^n pi x)| <= a^n and sum a^n < inf"). \
Name the theorems, cite the conditions, state what breaks if they fail.

2. KNOWN PITFALLS: What do practitioners in this domain commonly get wrong? \
What subtle errors do students make? What looks right but is wrong? Be \
specific — cite the exact step or technique where errors hide.

3. VERIFICATION TARGETS: Specific numerical values, bounds, or properties \
that can be independently checked. If a proof claims C = 2/3, what should \
C actually be? If an algorithm claims O(n log n), what is the actual \
recurrence? If an engineering design claims 500W, what does the physics say?

4. EDGE CASES AND BOUNDARY CONDITIONS: What happens at the extremes of the \
parameter space? What degenerate cases does the solution need to handle? \
What assumptions might silently fail at boundaries?

5. CROSS-REFERENCES: What related results, theorems, or known solutions \
should the reviewer compare against? What would a textbook say about this \
problem class?

Task:
{task_prompt}

Be precise, technical, and domain-specific. Generic advice ("check for \
errors") is worthless — provide the kind of pointed guidance that changes \
what a reviewer actually looks for.
"""


HIL_SIMPLE_GUIDANCE_PROMPT = """\
You are simulating a competent human expert giving brief review guidance \
to a colleague. This must be realistic — a short paragraph, the kind of \
thing someone says in passing or writes in a brief message.

Give 2-3 specific, pointed observations from your domain knowledge. \
What would an experienced practitioner mention if asked "anything I \
should watch out for?" Not an exhaustive briefing — just the one or \
two things that experience tells you matter most.

Task:
{task_prompt}

HARD CONSTRAINT: Your response MUST be under 500 characters. This \
simulates realistic human expert input — most researchers provide \
a sentence or two, not a comprehensive review guide.
"""


# ---------------------------------------------------------------------------
# Iterative HIL guidance templates (evidence-based, arXiv:2603.18740)
# Each round has a fixed GOAL but CC fills content from previous findings.
# Guidance is questions/checks only — never declarative answers.
# Character limits enforced in code, not just prompt.
# ---------------------------------------------------------------------------

ITERATIVE_HIL_ROUND_GOALS = {
    1: {
        "goal": "broad_context",
        "max_chars": 500,
        "template": """\
You are simulating a competent human expert starting a review conversation. \
Give 2-3 specific observations from your domain knowledge about this task. \
Consider these among other issues — do NOT restrict your search to only these.

Task:
{task_prompt}

RULES: Under {max_chars} characters. Questions and observations only. \
Do NOT solve the task or state answers. Do NOT say "focus on" — say \
"consider" or "watch for".""",
    },
    2: {
        "goal": "gap_followup",
        "max_chars": 200,
        "template": """\
The reviewers found these issues in round 1:
{findings_summary}

As a domain expert, what did they MISS? What gap is most concerning? \
Ask ONE targeted question about something they haven't checked yet.

RULES: Under {max_chars} characters. One question only. No answers.""",
    },
    3: {
        "goal": "targeted_risk",
        "max_chars": 250,
        "template": """\
Round 2 findings:
{findings_summary}

Point the reviewers at ONE specific risk or edge case that hasn't been \
examined yet. Something that your experience tells you matters but that \
reviewers often overlook.

RULES: Under {max_chars} characters. One specific check. No answers.""",
    },
    4: {
        "goal": "counter_check",
        "max_chars": 250,
        "template": """\
Round 3 findings:
{findings_summary}

Ask the reviewers to assume their strongest finding is WRONG. What would \
disprove it? What alternative explanation exists?

RULES: Under {max_chars} characters. Adversarial question only. No answers.""",
    },
    5: {
        "goal": "synthesis",
        "max_chars": 100,
        "template": """\
Final round. Ask the reviewers to state their top 3 findings with \
confidence levels and what remains uncertain.

RULES: Under {max_chars} characters.""",
    },
}

# Banned phrases in HIL guidance (prevents CC from solving instead of guiding)
# Banned phrases in HIL guidance (prevents CC from solving instead of guiding)
# CX P-pass: removed "= " (false-flags equations). Added more specific patterns.
HIL_GUIDANCE_BANNED = [
    "the answer is", "the bug is", "the error is", "the fix is",
    "you should change", "replace with", "the correct value is",
    "the result is", "the solution is", "should be changed to",
    "here is the fix", "the correct answer",
]

# Safe fallback guidance when leakage persists after retries
HIL_SAFE_FALLBACK = "Review the solution carefully. Are there any issues you haven't examined yet?"


def _generate_iterative_hil_guidance(
    task: dict, round_num: int, prev_findings: list[dict],
    max_retries: int = 1,
) -> tuple[str, bool]:
    """Generate iterative HIL guidance for a specific round.

    Returns (guidance_text, leakage_detected).
    Leakage means CC injected an answer despite being told not to.
    """
    round_config = ITERATIVE_HIL_ROUND_GOALS.get(round_num)
    if not round_config:
        return "", False

    # Summarise previous findings compactly
    if prev_findings:
        summary_parts = []
        for f in prev_findings[:10]:  # cap at 10 to keep prompt small
            if isinstance(f, dict):
                claim = f.get("claim", "")[:100]
                sev = f.get("severity", "?")
                summary_parts.append(f"- [{sev}] {claim}")
        findings_summary = "\n".join(summary_parts) if summary_parts else "(none)"
    else:
        findings_summary = "(no findings yet — this is round 1)"

    prompt = _safe_format(
        round_config["template"],
        task_prompt=task.get("prompt", "")[:1000],  # cap task prompt in later rounds
        findings_summary=findings_summary,
        max_chars=round_config["max_chars"],
    )

    for attempt in range(max_retries + 1):
        guidance = _call_cc(None, prompt)

        # Hard character limit
        max_c = round_config["max_chars"]
        if len(guidance) > max_c:
            guidance = guidance[:max_c].rsplit(" ", 1)[0]

        # Leakage check — did CC inject answers?
        leakage = any(banned in guidance.lower() for banned in HIL_GUIDANCE_BANNED)
        if leakage:
            if attempt < max_retries:
                _err(f"  [hil] guidance leakage detected, regenerating (attempt {attempt + 2})")
                prompt += "\n\nYour previous response contained answer content. Questions ONLY."
                continue
            else:
                # CX P-pass fix: leakage persisted — use safe fallback
                _err(f"  [hil] leakage persisted after {max_retries + 1} attempts — using safe fallback")
                return HIL_SAFE_FALLBACK, True

        return guidance, False


def _summarise_round_findings(round_data: dict) -> list[dict]:
    """Extract a flat list of findings from a round's data for HIL guidance."""
    findings = []
    for r in REVIEWERS:
        r_data = round_data.get(r, {})
        findings.extend(r_data.get("findings", []))
        if round_data.get("round_type") == "confer":
            findings.extend(
                r_data.get("confer_response", {}).get("new_findings", [])
            )
    return findings


HIL_RESEARCH_PROMPT = """\
You are preparing to provide expert review guidance on the following task. \
Before generating guidance, you need to identify what should be researched \
and verified externally.

Task:
{task_prompt}

List the specific things that need to be looked up or verified:

1. THEOREMS TO VERIFY: Name specific theorems, lemmas, or results that \
are relevant. For each, state the exact conditions/hypotheses that must \
hold. What are the standard references?

2. NUMERICAL BOUNDS TO CHECK: List any specific constants, bounds, or \
values that should be computationally verified (e.g. "verify that \
ab > 1 + 3*pi/2 is the correct sufficient condition for the Weierstrass \
function").

3. KNOWN RESULTS TO CROSS-REFERENCE: What is the strongest known result \
in this area? Who proved it? What year? What are the key search terms \
for finding it?

4. COMPUTATIONAL CHECKS: What specific calculations could be run in \
SymPy (or equivalent computer algebra system) to verify claims?

Be specific. Give exact search queries, exact computational queries (SymPy-compatible expressions), \
exact theorem names. Do not be vague.
"""


def _verify_sympy(claim: dict, timeout: int = 10) -> dict:
    """SymPy verification kernel — OSS replacement for Wolfram Alpha.

    Runs SymPy in a subprocess sandbox to prevent code injection from
    untrusted model output (CX P-pass critical finding).

    Input claim format (structured, not free text):
        {"op": "eq"|"gt"|"lt"|"ge"|"le"|"eval",
         "lhs": "a*b",
         "rhs": "1 + 3*pi/2",
         "symbols": {"a": "positive", "b": "positive,odd"},
         "description": "human-readable claim text"}

    Returns:
        {"verified": True|False|None,
         "result": "computed result or explanation",
         "method": "symbolic"|"numeric"|"counterexample"|"unverifiable",
         "expression": "the claim as evaluated"}

    CDSFL and CDSFL_HIL conditions ONLY. Control and HIL never call this.
    """
    # Validate claim structure
    if not isinstance(claim, dict) or "op" not in claim:
        return {"verified": None, "result": "invalid claim format",
                "method": "unverifiable", "expression": str(claim)}

    op = claim.get("op", "")
    lhs = claim.get("lhs", "")
    rhs = claim.get("rhs", "")
    description = claim.get("description", "")

    # Size guards (CX P-pass hardening)
    if len(lhs) > 500 or len(rhs) > 500:
        return {"verified": None, "result": "expression too long",
                "method": "unverifiable", "expression": f"{lhs} {op} {rhs}"}

    # Reject anything that looks like code injection
    for danger in ["__", "import", "exec", "eval", "open(", "os.", "sys.",
                    "lambda", "getattr", "setattr", "delattr", "globals",
                    "locals", "compile", "breakpoint"]:
        if danger in lhs or danger in rhs:
            return {"verified": None, "result": f"rejected: contains '{danger}'",
                    "method": "unverifiable", "expression": f"{lhs} {op} {rhs}"}

    # Build the sandboxed verification script
    verify_script = f'''
import json, sys
try:
    from sympy import (symbols, pi, E, oo, sqrt, cos, sin, log, exp,
                       Eq, Gt, Lt, Ge, Le, Ne, And, Or, Not, Implies,
                       Sum, Product, Integral, Limit, factorial, binomial,
                       simplify, N, S, solve, oo, zoo, nan, Rational, Integer,
                       Float, reduce_inequalities, Symbol)
    from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                             implicit_multiplication_application)

    ALLOWED = {{
        "pi": pi, "E": E, "oo": oo, "sqrt": sqrt, "cos": cos, "sin": sin,
        "log": log, "exp": exp, "Eq": Eq, "Gt": Gt, "Lt": Lt, "Ge": Ge,
        "Le": Le, "Ne": Ne, "And": And, "Or": Or, "Not": Not,
        "Implies": Implies, "Sum": Sum, "Product": Product, "Rational": Rational,
        "Integral": Integral, "Limit": Limit, "factorial": factorial,
        "binomial": binomial, "S": S, "simplify": simplify, "N": N,
        "Integer": Integer, "Float": Float,
    }}

    # Add declared symbols
    sym_defs = {json.dumps(claim.get("symbols", {}))}
    for name in json.loads('{json.dumps(list(claim.get("symbols", {}).keys()))}'):
        ALLOWED[name] = Symbol(name, positive="positive" in sym_defs.get(name, ""))

    transforms = standard_transformations + (implicit_multiplication_application,)

    lhs_expr = parse_expr({json.dumps(lhs)}, local_dict=ALLOWED,
                          global_dict={{"__builtins__": {{}}}},
                          transformations=transforms)
    rhs_expr = parse_expr({json.dumps(rhs)}, local_dict=ALLOWED,
                          global_dict={{"__builtins__": {{}}}},
                          transformations=transforms)

    op = {json.dumps(op)}
    result = {{"verified": None, "result": "", "method": "unverifiable",
              "expression": f"{{lhs_expr}} {{op}} {{rhs_expr}}"}}

    if op == "eval":
        val = N(lhs_expr)
        result = {{"verified": None, "result": str(val), "method": "numeric",
                  "expression": str(lhs_expr)}}
    elif op in ("eq", "gt", "lt", "ge", "le"):
        diff = simplify(lhs_expr - rhs_expr)
        num_diff = N(diff)
        if op == "eq":
            is_true = diff == 0 or abs(num_diff) < 1e-12
            result = {{"verified": bool(is_true), "result": f"diff = {{diff}} (numeric: {{num_diff}})",
                      "method": "symbolic" if diff == 0 else "numeric",
                      "expression": f"{{lhs_expr}} = {{rhs_expr}}"}}
        elif op == "gt":
            result = {{"verified": bool(num_diff > 0), "result": f"lhs - rhs = {{num_diff}}",
                      "method": "numeric", "expression": f"{{lhs_expr}} > {{rhs_expr}}"}}
        elif op == "lt":
            result = {{"verified": bool(num_diff < 0), "result": f"lhs - rhs = {{num_diff}}",
                      "method": "numeric", "expression": f"{{lhs_expr}} < {{rhs_expr}}"}}
        elif op == "ge":
            result = {{"verified": bool(num_diff >= 0), "result": f"lhs - rhs = {{num_diff}}",
                      "method": "numeric", "expression": f"{{lhs_expr}} >= {{rhs_expr}}"}}
        elif op == "le":
            result = {{"verified": bool(num_diff <= 0), "result": f"lhs - rhs = {{num_diff}}",
                      "method": "numeric", "expression": f"{{lhs_expr}} <= {{rhs_expr}}"}}

    print(json.dumps(result))

except Exception as exc:
    print(json.dumps({{"verified": None, "result": f"sympy error: {{exc}}",
                      "method": "unverifiable", "expression": ""}}))
'''

    # Run in subprocess with timeout (CX P-pass: signal.alarm is brittle)
    try:
        proc = sp.run(
            [sys.executable, "-c", verify_script],
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout.strip())
        else:
            return {"verified": None,
                    "result": f"subprocess error: {proc.stderr[:200]}",
                    "method": "unverifiable",
                    "expression": f"{lhs} {op} {rhs}"}
    except sp.TimeoutExpired:
        return {"verified": None, "result": f"verification timed out ({timeout}s)",
                "method": "unverifiable", "expression": f"{lhs} {op} {rhs}"}
    except Exception as exc:
        return {"verified": None, "result": f"verification failed: {exc}",
                "method": "unverifiable", "expression": f"{lhs} {op} {rhs}"}


def _compute_sympy(query: str) -> str:
    """Research computation — evaluates a mathematical expression via SymPy.

    This is RESEARCH COMPUTATION (available to HIL and CDSFL_HIL):
    looking up what an expression evaluates to. Equivalent to using a
    calculator or CAS during literature review.

    NOT to be confused with _verify_findings() which is METHODOLOGY
    VERIFICATION (CDSFL and CDSFL_HIL only): checking whether a
    reviewer's claim is mathematically correct.

    The distinction: research_compute = "what is 1 + 3*pi/2?"
                     methodology_verify = "is this reviewer's bound correct?"
    """
    result = _verify_sympy({"op": "eval", "lhs": query, "rhs": "0",
                            "symbols": {}, "description": query})
    return f"  SymPy result: {result.get('result', 'no result')}"


def _search_arxiv(query: str, max_results: int = 3) -> str:
    """Search arXiv for relevant papers. Returns titles + abstracts + DOIs."""
    try:
        import arxiv
        search = arxiv.Search(query=query, max_results=max_results,
                              sort_by=arxiv.SortCriterion.Relevance)
        client = arxiv.Client()
        results = []
        for paper in client.results(search):
            doi_str = f"  DOI: {paper.doi}" if paper.doi else "  DOI: (none)"
            results.append(
                f"  Title: {paper.title}\n"
                f"  Authors: {', '.join(a.name for a in paper.authors[:3])}\n"
                f"  Year: {paper.published.year}\n"
                f"  Abstract: {paper.summary[:300]}...\n"
                f"  URL: {paper.entry_id}\n"
                f"{doi_str}"
            )
        return "\n\n".join(results) if results else "(no arXiv results)"
    except Exception as exc:
        return f"(arxiv error: {exc})"


def _search_semantic_scholar(query: str, max_results: int = 5) -> str:
    """Search Semantic Scholar for papers by query.

    Returns titles, years, citation counts, and truncated abstracts.
    Uses the semanticscholar Python package with a 10-second timeout.
    Gracefully handles rate limits (429) and all other errors.
    """
    try:
        from semanticscholar import SemanticScholar
        sch = SemanticScholar(timeout=10)
        results = sch.search_paper(
            query,
            limit=max_results,
            fields=["title", "year", "citationCount", "abstract", "externalIds"],
        )
        if not results or len(results) == 0:
            return "(no Semantic Scholar results)"
        output = []
        for paper in results:
            title = getattr(paper, "title", "(no title)") or "(no title)"
            year = getattr(paper, "year", "?") or "?"
            cites = getattr(paper, "citationCount", 0) or 0
            abstract = getattr(paper, "abstract", "") or ""
            ext_ids = getattr(paper, "externalIds", {}) or {}
            doi = ext_ids.get("DOI", "(none)") if isinstance(ext_ids, dict) else "(none)"
            output.append(
                f"  Title: {title}\n"
                f"  Year: {year} | Citations: {cites}\n"
                f"  DOI: {doi}\n"
                f"  Abstract: {abstract[:300]}..."
            )
        return "\n\n".join(output)
    except Exception as exc:
        exc_str = str(exc)
        if "429" in exc_str or "rate" in exc_str.lower():
            return "(Semantic Scholar rate-limited — skipping)"
        return f"(Semantic Scholar error: {exc_str[:200]})"


def _fetch_scihub(doi: str, max_pages: int = 3) -> str:
    """Fetch full-text PDF from Sci-Hub for a given DOI.

    Attempts to find PDF URL from sci-hub.red, download it, and extract
    text from the first max_pages pages. Falls back gracefully if Sci-Hub
    is unavailable or the PDF cannot be parsed.

    Timeout: 15 seconds for network operations.
    """
    if not doi or doi == "(none)":
        return "(no DOI provided)"

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return "(requests/beautifulsoup4 not available)"

    # Step 1: Get the PDF URL from Sci-Hub
    try:
        scihub_url = f"https://sci-hub.red/{doi}"
        resp = requests.get(scihub_url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (research bot)"
        })
        if resp.status_code != 200:
            return f"(Sci-Hub returned HTTP {resp.status_code} for {doi})"

        soup = BeautifulSoup(resp.text, "html.parser")
        # Sci-Hub embeds the PDF in an iframe or a direct link
        pdf_url = None
        iframe = soup.find("iframe", {"id": "pdf"})
        if iframe and iframe.get("src"):
            pdf_url = iframe["src"]
        else:
            embed = soup.find("embed", {"type": "application/pdf"})
            if embed and embed.get("src"):
                pdf_url = embed["src"]
        if not pdf_url:
            # Try finding any .pdf link — restrict to known academic domains
            _SAFE_DOMAINS = ("sci-hub", "libgen", "arxiv.org", "unpaywall", "core.ac.uk")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if ".pdf" in href and any(d in href for d in _SAFE_DOMAINS):
                    pdf_url = href
                    break
        if not pdf_url:
            return f"(Sci-Hub: no PDF link found for {doi})"

        # Normalise URL
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url
        elif pdf_url.startswith("/"):
            pdf_url = "https://sci-hub.red" + pdf_url
    except requests.exceptions.Timeout:
        return f"(Sci-Hub timed out for {doi})"
    except Exception as exc:
        return f"(Sci-Hub lookup error: {str(exc)[:150]})"

    # Step 2: Download the PDF
    try:
        pdf_resp = requests.get(pdf_url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (research bot)"
        })
        if pdf_resp.status_code != 200:
            return f"(PDF download failed: HTTP {pdf_resp.status_code})"
        # Size limits: reject < 1KB (not a real PDF) and > 20MB (too large)
        MAX_PDF_BYTES = 20 * 1024 * 1024  # 20MB
        content_length = int(pdf_resp.headers.get("Content-Length", 0))
        if content_length > MAX_PDF_BYTES:
            return f"(PDF too large: {content_length} bytes, max {MAX_PDF_BYTES})"
        pdf_bytes = pdf_resp.content
        if len(pdf_bytes) > MAX_PDF_BYTES:
            return f"(PDF too large: {len(pdf_bytes)} bytes)"
        if len(pdf_bytes) < 1000:
            return f"(PDF too small — likely not a real PDF: {len(pdf_bytes)} bytes)"
    except requests.exceptions.Timeout:
        return "(PDF download timed out)"
    except Exception as exc:
        return f"(PDF download error: {str(exc)[:150]})"

    # Step 3: Extract text from the first N pages
    import io
    text = ""

    # Try pdfplumber first (better extraction), fall back to PyPDF2
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages_to_read = min(max_pages, len(pdf.pages))
            parts = []
            for i in range(pages_to_read):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    parts.append(page_text)
            text = "\n\n".join(parts)
    except Exception:
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            pages_to_read = min(max_pages, len(reader.pages))
            parts = []
            for i in range(pages_to_read):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    parts.append(page_text)
            text = "\n\n".join(parts)
        except Exception as exc:
            return f"(PDF text extraction failed: {str(exc)[:150]})"

    if not text.strip():
        return f"(PDF downloaded but no text extracted from first {max_pages} pages)"

    return f"  [Full text, first {max_pages} pages, DOI: {doi}]\n{text[:5000]}"


def _delegate_research_to_cx(topic: str, timeout: int = 120) -> str:
    """Delegate a focused research query to CX (Codex 5.3) via CLI.

    Called only for cdsfl_hil condition — leverages CX's independent
    knowledge base for citation-aware research.

    Returns CX's research findings as a string, or a fallback message
    on any error.
    """
    prompt = (
        f"Find the 3 most cited papers on: {topic}\n\n"
        f"Return titles, years, citation counts, and one-sentence summaries. "
        f"If you cannot find exact citation counts, estimate from your knowledge. "
        f"Format as a numbered list."
    )
    try:
        result = sp.run(
            ["codex", "exec", prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        output = result.stdout.strip()
        if result.returncode != 0 or not output:
            stderr = result.stderr[:200] if result.stderr else "(no stderr)"
            return f"(CX research delegation failed: exit {result.returncode}, {stderr})"
        return output
    except sp.TimeoutExpired:
        return f"(CX research delegation timed out after {timeout}s)"
    except FileNotFoundError:
        return "(codex CLI not found on PATH — CX delegation unavailable)"
    except Exception as exc:
        return f"(CX research delegation error: {str(exc)[:200]})"


def _search_web(query: str, max_results: int = 5) -> str:
    """Search the web via DuckDuckGo. Returns titles + snippets."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    f"  Title: {r['title']}\n"
                    f"  URL: {r['href']}\n"
                    f"  Snippet: {r['body'][:200]}"
                )
            return "\n\n".join(results) if results else "(no web results)"
    except Exception as exc:
        return f"(web search error: {exc})"


def _read_page(url: str, max_chars: int = 3000) -> str:
    """Read a web page and extract text content.

    Tries lightweight requests+BeautifulSoup first (static HTML).
    Falls back to headless Chromium via Playwright for JS-rendered pages.
    Caps output to max_chars to avoid flooding the guidance prompt.
    """
    # Try lightweight approach first
    try:
        import requests
        from bs4 import BeautifulSoup
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (research bot)"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        if len(text) > 200:
            return text[:max_chars]
    except Exception:
        pass  # fall through to Playwright

    # Fallback: headless Chromium for JS-rendered pages
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            page.wait_for_load_state("networkidle", timeout=10000)
            text = page.inner_text("body")
            browser.close()
            return text[:max_chars] if text else "(page rendered but no text)"
    except Exception as exc:
        return f"(could not read page: {exc})"


def _search_and_read(query: str, max_results: int = 3, read_top_n: int = 2) -> str:
    """Search the web, then READ the top results.

    This is what a real researcher does: find relevant pages, then read them.
    Not just snippets — actual content with theorem statements, conditions,
    bounds, and proofs.
    """
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=max_results))
    except Exception as exc:
        return f"(web search error: {exc})"

    if not search_results:
        return "(no web results)"

    output = []
    for i, r in enumerate(search_results):
        output.append(f"  [{i+1}] {r['title']}\n  URL: {r['href']}")
        if i < read_top_n:
            _err(f"    [research/read] reading {r['href'][:60]}...")
            content = _read_page(r['href'], max_chars=2000)
            output.append(f"  Content:\n{content}\n")
        else:
            output.append(f"  Snippet: {r['body'][:200]}\n")

    return "\n".join(output)


def _do_external_research(task: dict, research_needs: str,
                          condition: str = "cdsfl_hil") -> str:
    """Perform external research using multiple sources.

    Pipeline order:
      (a) SymPy computation (mathematical queries)
      (b) arXiv search (with DOI extraction)
      (c) Semantic Scholar search (citation counts + reference context)
      (d) Sci-Hub full-text fetch (top 2 most relevant papers by DOI)
      (e) Web search + page reading
      (f) CX delegation (cdsfl_hil condition only)

    CC has already identified specific queries in research_needs.
    Each source failure is logged but doesn't stop the pipeline.
    Total output is capped at 15000 chars to prevent context overflow.
    """
    RESEARCH_OUTPUT_CAP = 15000
    results = []
    collected_dois = []  # DOIs gathered from arXiv and Semantic Scholar
    task_title = task.get("title", "")

    # Parse CC's research needs into categorised queries
    wolfram_queries = []
    arxiv_queries = []
    web_queries = []

    lines = research_needs.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lower = stripped.lower()

        # Lines with mathematical verification keywords → SymPy
        if any(kw in lower for kw in ["verify", "compute", "calculate",
                                       "evaluate", "solve", "simplify",
                                       "what is", "check that", "confirm"]):
            clean = stripped.lstrip("-*0123456789.) ")
            if clean:
                wolfram_queries.append(clean)

        # Lines mentioning theorems, papers, proofs → arXiv
        if any(kw in lower for kw in ["theorem", "proved", "paper",
                                       "result", "conjecture", "lemma",
                                       "known", "published", "reference"]):
            clean = stripped.lstrip("-*0123456789.) ")
            if clean:
                arxiv_queries.append(clean)

        # Lines with search/lookup intent → web
        if any(kw in lower for kw in ["search", "look up", "find",
                                       "check", "standard", "textbook"]):
            clean = stripped.lstrip("-*0123456789.) ")
            if clean:
                web_queries.append(clean)

    # Always add a baseline web search for the task domain
    web_queries.append(f"{task_title} known results best bounds proof techniques")

    # --- (a) SymPy computational queries (cap at 5) ---
    for i, wq in enumerate(wolfram_queries[:5]):
        _err(f"    [research/sympy] query {i+1}/{min(len(wolfram_queries), 5)}: "
             f"{wq[:80]}...")
        try:
            answer = _compute_sympy(wq)
            results.append(f"SYMPY COMPUTATION: {wq}\n{answer}\n")
        except Exception as exc:
            _err(f"    [research/sympy] error: {exc}")
            results.append(f"SYMPY COMPUTATION: {wq}\n  (error: {exc})\n")

    # --- (b) arXiv searches (cap at 3) — now extracts DOIs ---
    for i, aq in enumerate(arxiv_queries[:3]):
        _err(f"    [research/arxiv] query {i+1}/{min(len(arxiv_queries), 3)}: "
             f"{aq[:80]}...")
        try:
            answer = _search_arxiv(aq)
            results.append(f"ARXIV SEARCH: {aq}\n{answer}\n")
            # Extract DOIs from arXiv results
            for result_line in answer.split("\n"):
                if result_line.strip().startswith("DOI:"):
                    doi_val = result_line.strip().replace("DOI:", "").strip()
                    if doi_val and doi_val != "(none)":
                        collected_dois.append(doi_val)
        except Exception as exc:
            _err(f"    [research/arxiv] error: {exc}")
            results.append(f"ARXIV SEARCH: {aq}\n  (error: {exc})\n")

    # --- (c) Semantic Scholar search (cap at 3 queries) ---
    for i, aq in enumerate(arxiv_queries[:3]):
        _err(f"    [research/semantic_scholar] query {i+1}/{min(len(arxiv_queries), 3)}: "
             f"{aq[:80]}...")
        try:
            answer = _search_semantic_scholar(aq, max_results=5)
            results.append(f"SEMANTIC SCHOLAR: {aq}\n{answer}\n")
            # Extract DOIs from Semantic Scholar results
            for result_line in answer.split("\n"):
                if result_line.strip().startswith("DOI:"):
                    doi_val = result_line.strip().replace("DOI:", "").strip()
                    if doi_val and doi_val != "(none)":
                        collected_dois.append(doi_val)
        except Exception as exc:
            _err(f"    [research/semantic_scholar] error: {exc}")
            results.append(f"SEMANTIC SCHOLAR: {aq}\n  (error: {exc})\n")

    # --- (d) Sci-Hub full-text fetch (top 2 unique DOIs) ---
    unique_dois = list(dict.fromkeys(collected_dois))  # deduplicate, preserve order
    for i, doi in enumerate(unique_dois[:2]):
        _err(f"    [research/scihub] fetching DOI {i+1}/2: {doi[:60]}...")
        try:
            answer = _fetch_scihub(doi, max_pages=3)
            results.append(f"SCIHUB FULL TEXT: {doi}\n{answer}\n")
        except Exception as exc:
            _err(f"    [research/scihub] error: {exc}")
            results.append(f"SCIHUB FULL TEXT: {doi}\n  (error: {exc})\n")

    # --- (e) Web searches — search AND read top results (cap at 3) ---
    for i, wq in enumerate(web_queries[:3]):
        _err(f"    [research/web] query {i+1}/{min(len(web_queries), 3)}: "
             f"{wq[:80]}...")
        try:
            answer = _search_and_read(wq, max_results=3, read_top_n=2)
            results.append(f"WEB RESEARCH: {wq}\n{answer}\n")
        except Exception as exc:
            _err(f"    [research/web] error: {exc}")
            results.append(f"WEB RESEARCH: {wq}\n  (error: {exc})\n")

    # --- (f) CX delegation (cdsfl_hil only) ---
    if condition == "cdsfl_hil":
        topic = task_title or task.get("prompt", "")[:200]
        _err(f"    [research/cx] delegating research to CX: {topic[:80]}...")
        try:
            cx_answer = _delegate_research_to_cx(topic, timeout=120)
            results.append(f"CX RESEARCH DELEGATION: {topic}\n{cx_answer}\n")
        except Exception as exc:
            _err(f"    [research/cx] error: {exc}")
            results.append(f"CX RESEARCH DELEGATION: {topic}\n  (error: {exc})\n")

    if not results:
        return "(No external research queries extracted from CC's research needs.)"

    # Cap total output to prevent context overflow
    combined = "\n".join(results)
    if len(combined) > RESEARCH_OUTPUT_CAP:
        _err(f"    [research] output capped: {len(combined)} -> {RESEARCH_OUTPUT_CAP} chars")
        combined = combined[:RESEARCH_OUTPUT_CAP]  # strict cap, no suffix that exceeds it
    return combined


def _get_condition_prompts(condition: str) -> tuple[str, str]:
    """Return (blind_prompt_template, confer_prompt_template) for a condition."""
    if condition == "control":
        return CONTROL_BLIND_PROMPT, CONTROL_CONFER_PROMPT
    elif condition == "hil":
        return HIL_BLIND_PROMPT, HIL_CONFER_PROMPT
    elif condition == "cdsfl":
        return BLIND_REVIEW_PROMPT, CONFER_REVIEW_PROMPT
    elif condition == "cdsfl_hil":
        return CDSFL_HIL_BLIND_PROMPT, CDSFL_HIL_CONFER_PROMPT
    else:
        raise ValueError(f"Unknown condition: {condition}")


# ---------------------------------------------------------------------------
# Cost ledger (reused pattern from run_phase2.py)
# ---------------------------------------------------------------------------


class CostLedger:
    """Track cumulative API spend with a hard cap."""

    def __init__(self, cap_usd: float = 100.0, ledger_path: Path | None = None):
        self.cap = cap_usd
        self.total = 0.0
        self.by_provider: dict[str, float] = {}
        self.ledger_path = ledger_path

    def load_existing(self) -> bool:
        if self.ledger_path and self.ledger_path.exists():
            try:
                data = json.loads(self.ledger_path.read_text())
                self.total = data.get("total_usd", 0.0)
                self.by_provider = data.get("by_provider", {})
                return True
            except (json.JSONDecodeError, KeyError):
                _err("  [ledger] WARNING: corrupt ledger, starting fresh")
                return False
        return True

    def record(self, provider: str, cost: float) -> None:
        self.total += cost
        self.by_provider[provider] = self.by_provider.get(provider, 0.0) + cost
        self._save()

    def check_cap(self) -> bool:
        return self.total < self.cap

    def _save(self) -> None:
        if self.ledger_path:
            data = {
                "total_usd": round(self.total, 4),
                "cap_usd": self.cap,
                "remaining_usd": round(self.cap - self.total, 4),
                "by_provider": {k: round(v, 4) for k, v in self.by_provider.items()},
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            _atomic_write(self.ledger_path, json.dumps(data, indent=2) + "\n")

    def summary(self) -> str:
        return f"Cost: ${self.total:.4f} / ${self.cap:.2f} (${self.cap - self.total:.4f} remaining)"


def _atomic_write(path: Path, data: str) -> None:
    """Write data atomically via temp file + rename."""
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp", prefix=path.stem + "_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(data)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Checkpoint (task-level, with verification chain state)
# ---------------------------------------------------------------------------


class Checkpoint:
    """Persist completed task results for crash-safe resume."""

    def __init__(self, checkpoint_path: Path, manifest: str = ""):
        self.path = checkpoint_path
        self.manifest = manifest
        self.completed: dict[str, dict[str, Any]] = {}

    def load(self) -> bool:
        if not self.path.exists():
            return True
        try:
            data = json.loads(self.path.read_text())
        except (json.JSONDecodeError, OSError):
            _err("  [checkpoint] WARNING: corrupt checkpoint, starting fresh")
            return True
        stored_manifest = data.get("manifest", "")
        if stored_manifest and stored_manifest != self.manifest:
            _err(f"  [checkpoint] WARNING: manifest changed (tasks/directives updated)")
            _err(f"  [checkpoint] Resuming anyway — completed runs are preserved")
            # Don't block resume on manifest change. Completed runs used the
            # old config; new runs use the new config. Both are recorded.
        self.completed = data.get("completed", {})
        _err(f"  [checkpoint] resumed {len(self.completed)} completed task(s)")
        return True

    def save(self, task_id: str, result: dict) -> None:
        self.completed[task_id] = result
        self._write()

    def _write(self) -> None:
        data = {
            "manifest": self.manifest,
            "completed": self.completed,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        _atomic_write(self.path, json.dumps(data, indent=2) + "\n")


def _compute_manifest(task_ids: list[str], directives_hash: str, corpus_hash: str = "") -> str:
    """Deterministic hash of run configuration.

    CX P-pass fix (HARD 6): includes corpus_hash so changed task content
    with same task IDs is detected as incompatible on resume.
    """
    manifest_data = json.dumps({
        "experiment": "round_robin",
        "task_ids": sorted(task_ids),
        "directives_hash": directives_hash,
        "corpus_hash": corpus_hash,
        "max_rounds": MAX_ROUNDS,
        "models": ["claude-cli/opus-4.6", "deepseek-api/deepseek-v3.2", "codex-cli/gpt-5.3-codex"],
    }, sort_keys=True)
    return hashlib.sha256(manifest_data.encode()).hexdigest()[:32]


# ---------------------------------------------------------------------------
# Input corpus freezing
# ---------------------------------------------------------------------------


def freeze_corpus(tasks: list[dict], output_dir: Path) -> dict:
    """Freeze the input corpus: write each task + compute manifest hash.

    Returns the manifest dict with per-task hashes and overall hash.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    task_hashes = {}
    for task in tasks:
        task_id = task["id"]
        task_json = json.dumps(task, sort_keys=True, indent=2)
        task_path = output_dir / f"{task_id}.json"
        _atomic_write(task_path, task_json + "\n")
        task_hashes[task_id] = _content_hash(task_json)

    manifest = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "task_count": len(tasks),
        "task_hashes": task_hashes,
        "corpus_hash": _content_hash(json.dumps(task_hashes, sort_keys=True)),
    }
    _atomic_write(output_dir / "corpus_manifest.json", json.dumps(manifest, indent=2) + "\n")
    return manifest


# ---------------------------------------------------------------------------
# Global deadline budget — prevents outer-process kill from truncating runs
# ---------------------------------------------------------------------------


class DeadlineBudget:
    """Track wall-clock time remaining. Clamp per-call timeouts to budget."""

    def __init__(self, max_seconds: int):
        self.max_seconds = max_seconds
        self.start = time.monotonic()

    def remaining(self) -> float:
        return max(0.0, self.max_seconds - (time.monotonic() - self.start))

    def exhausted(self) -> bool:
        return self.remaining() <= SAFETY_MARGIN

    def clamp_timeout(self, desired: int) -> int:
        """Return the desired timeout unchanged.

        Budget no longer clamps individual subprocess timeouts — each model
        gets its full allocated time on every call. Budget exhaustion is
        checked only at task/condition boundaries (gate, not clamp).

        Bug fix (2026-03-21): budget clamping was strangling reviewer retries
        to 10s, guaranteeing failure. CLI-only runs have no per-call cost,
        so clamping individual timeouts serves no purpose.
        """
        return desired

    def elapsed(self) -> float:
        return time.monotonic() - self.start

    def summary(self) -> str:
        r = self.remaining()
        e = self.elapsed()
        return f"Elapsed: {e:.0f}s, Remaining: {r:.0f}s / {self.max_seconds}s"


# Global instance — set in main()
_budget: DeadlineBudget | None = None

# Per-task CC timeout from registry policy — set in run_task(), falls back to CC_TIMEOUT
_cc_policy_timeout: int | None = None


def _prompt_size_check(prompt: str, label: str) -> None:
    """Log prompt size and warn if exceeding threshold."""
    chars = len(prompt)
    est_tokens = chars // 4  # rough estimate
    if chars > PROMPT_SIZE_WARN:
        _err(f"  [WARN] {label} prompt size: {chars} chars (~{est_tokens} tokens) — exceeds {PROMPT_SIZE_WARN}")
    else:
        _err(f"  [telemetry] {label} prompt: {chars} chars (~{est_tokens} tokens)")


# ---------------------------------------------------------------------------
# Legacy Gemini code removed (2026-03-22). Gemini 3.1 Pro replaced by
# DeepSeek V3.2. Gemini proved non-functional as a reviewer: zero novel
# findings in confer rounds across all conditions. See EXPERIMENTAL_RESULTS.md.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CC (Opus 4.6) caller — via claude CLI
# ---------------------------------------------------------------------------


def _call_cli(cmd: list[str], input_text: str | None = None,
              timeout: int = 600, label: str = "cli") -> str:
    """Run a CLI subprocess with optional stdin. Returns stdout text.

    Deterministic failure policy: caller wraps with _with_retry (1 retry).
    """
    try:
        result = sp.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            # Known Claude Code bug: claude -p can return exit 1 with empty
            # stderr even on success. If stdout has content, use it.
            if output:
                _err(f"  [{label}] WARNING: exit {result.returncode} but stdout "
                     f"has {len(output)} chars — using output (known CLI bug)")
            else:
                stderr = result.stderr[:300] if result.stderr else "(no stderr)"
                raise RuntimeError(f"{label} failed (exit {result.returncode}): {stderr}")
        if not output:
            raise RuntimeError(f"{label} returned empty output")
        return output
    except sp.TimeoutExpired:
        raise RuntimeError(f"{label} timed out after {timeout}s")
    except FileNotFoundError:
        raise RuntimeError(f"{label} CLI not found on PATH")


# Module-level flag: whether CC should run in --bare mode with explicit system prompt.
# Set per-condition in run_task(). When True, CC ignores CLAUDE.md and uses only
# the methodology reference file (CDSFL conditions) or nothing (Control/HIL).
_cc_bare_mode: bool = False
_cc_system_prompt_file: str | None = None

METHODOLOGY_FILE = str(
    Path(__file__).resolve().parent.parent / "resources" / "configs" / "methodology_reference.md"
)


def _call_cc_inner(system_prompt: str | None, user_prompt: str) -> str:
    """CC (Opus 4.6) via claude CLI (inner, no retry).

    Uses --bare mode to strip CLAUDE.md auto-loading, ensuring CC operates
    under the same directive conditions as other models. System-level
    directives are injected via --system-prompt (CDSFL) or omitted (Control/HIL).
    """
    _cli = CLAUDE_CLI or "claude"
    cmd = [_cli, "-p", "--model", "claude-opus-4-6", "--output-format", "text"]

    if _cc_bare_mode:
        cmd.append("--bare")
        if _cc_system_prompt_file:
            cmd.extend(["--system-prompt-file", _cc_system_prompt_file])

    if system_prompt:
        combined = f"SYSTEM DIRECTIVES:\n{system_prompt}\n\nTASK:\n{user_prompt}"
    else:
        combined = user_prompt

    effective_cc_timeout = _cc_policy_timeout if _cc_policy_timeout is not None else CC_TIMEOUT
    timeout = _budget.clamp_timeout(effective_cc_timeout) if _budget else effective_cc_timeout
    _prompt_size_check(combined, "cc")
    return _call_cli(cmd, input_text=combined, timeout=timeout, label="claude")


def _call_cc(system_prompt: str | None, user_prompt: str) -> str:
    """CC with deterministic failure policy (1 retry)."""
    return _with_retry(_call_cc_inner, system_prompt, user_prompt)


# ---------------------------------------------------------------------------
# CX (Codex 5.3) caller — via codex exec CLI
# ---------------------------------------------------------------------------


def _call_cx_reviewer_inner(user_prompt: str, task_id: str) -> str:
    """CX (Codex 5.3) as blind/confer reviewer via codex exec CLI (inner, no retry)."""
    output_path = Path(f"/tmp/cx_rr_{task_id}_{int(time.time())}.txt")
    proj_dir = str(Path.home() / "Developer_Projects" / "Constraint_Engineering")
    timeout = _budget.clamp_timeout(CX_TIMEOUT) if _budget else CX_TIMEOUT
    _prompt_size_check(user_prompt, "cx")

    try:
        result = sp.run(
            [
                "codex", "exec",
                "-o", str(output_path),
                "-C", proj_dir,
                user_prompt,
            ],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            output_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"codex exec failed (exit {result.returncode}): "
                f"{result.stderr[:200] if result.stderr else '(no stderr)'}"
            )
        if output_path.exists():
            response = output_path.read_text().strip()
            output_path.unlink()
            if response:
                return response
        stdout = result.stdout.strip()
        if not stdout:
            raise RuntimeError("codex exec returned empty output")
        return stdout
    except sp.TimeoutExpired:
        output_path.unlink(missing_ok=True)
        raise RuntimeError("codex exec timed out after 600s")
    except FileNotFoundError:
        output_path.unlink(missing_ok=True)
        raise RuntimeError("codex CLI not found")


def _call_cx_reviewer(user_prompt: str, task_id: str) -> str:
    """CX reviewer with deterministic failure policy (1 retry)."""
    return _with_retry(_call_cx_reviewer_inner, user_prompt, task_id)


def _extract_verifiable_claims_from_text(text: str) -> list[dict]:
    """Extract verifiable_claim JSON objects from raw response text.

    Finding 3 fix: when context capping summarises older responses, structured
    verifiable_claim data must survive. This function scans for JSON objects
    containing the "op" field (the signature of a verifiable_claim) and returns
    a compact list of them.
    """
    import re
    claims = []
    # Find JSON objects that look like verifiable_claim (contain "op" key)
    # CX C3 fix: increased scan window from 500 to 2000 for complex claims
    for match in re.finditer(r'\{[^{}]*"op"\s*:', text):
        start = match.start()
        depth = 0
        for i in range(start, min(start + 2000, len(text))):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:i + 1])
                        if isinstance(obj, dict) and "op" in obj:
                            # Keep only the essential fields
                            compact = {k: obj[k] for k in ("op", "lhs", "rhs") if k in obj}
                            if compact:
                                claims.append(compact)
                    except (json.JSONDecodeError, ValueError):
                        pass
                    break
    return claims


# ---------------------------------------------------------------------------
# Phase 2: Persistent conversation wrappers
#
# Each reviewer maintains context across all rounds of a task. The blind
# review is the first message; each confer round is a subsequent message
# in the same conversation. The reviewer builds on its own prior analysis
# rather than starting from scratch each round.
#
# DeepSeek: native multi-turn chat via OpenAI-compatible API
# CX: accumulated conversation history prefixed to each codex exec call
# ---------------------------------------------------------------------------


class DeepSeekReviewChat:
    """Multi-turn review conversation with DeepSeek V3.2 via OpenAI-compatible API.

    Native multi-turn chat — messages list accumulates naturally.
    No process management, no zombie cleanup, no CLI auth issues.
    Replaces Gemini 3.1 Pro which proved non-functional as a reviewer
    (zero novel findings in confer rounds across all conditions).

    Retry policy: 3 attempts with exponential backoff.
    """

    DEEPSEEK_TIMEOUT = 300  # 5 min per call (class-level fallback)
    DEEPSEEK_MAX_ATTEMPTS = 3

    def __init__(self, timeout: int | None = None, system_prompt: str | None = None):
        from openai import OpenAI
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set")
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.messages: list[dict[str, str]] = []
        # System-level directive injection (CDSFL conditions only).
        # This is a true system message — persists across all turns.
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        self._timeout = timeout if timeout is not None else self.DEEPSEEK_TIMEOUT

    def send(self, prompt: str, timeout: int | None = None) -> str:
        """Send a message in the ongoing review conversation.

        Messages accumulate natively — DeepSeek sees all prior exchanges.
        3-attempt retry with backoff. Raises DeepSeekExhausted on failure.
        """
        timeout = timeout if timeout is not None else self._timeout
        _prompt_size_check(prompt, "deepseek_chat")
        self.messages.append({"role": "user", "content": prompt})
        last_error = None

        for attempt in range(1, self.DEEPSEEK_MAX_ATTEMPTS + 1):
            if attempt > 1:
                _err(f"    [deepseek retry] attempt {attempt}/{self.DEEPSEEK_MAX_ATTEMPTS}")
            t0 = time.monotonic()
            try:
                response = self.client.chat.completions.create(
                    # deepseek-v4-pro is the panel's DeepSeek; `deepseek-chat` is a
                    # different, weaker model (founder directive 2026-07-31).
                    model="deepseek-v4-pro",
                    messages=self.messages,
                    max_tokens=8192,
                    temperature=0.0,
                    timeout=timeout,
                )
                elapsed = time.monotonic() - t0
                if not response.choices:
                    raise RuntimeError(
                        f"API returned no choices after {elapsed:.1f}s "
                        f"(possible upstream 500 error)"
                    )
                text = response.choices[0].message.content or ""
                text = text.strip()
                self.messages.append({"role": "assistant", "content": text})
                _err(f"  [deepseek_chat] done ({elapsed:.1f}s, {len(text)} chars)")
                return text
            except Exception as e:
                elapsed = time.monotonic() - t0
                last_error = e
                _err(f"    [deepseek retry] attempt {attempt} failed "
                     f"({elapsed:.1f}s): {str(e)[:100]}")
                # Remove the user message on failure so we can retry cleanly
                if attempt < self.DEEPSEEK_MAX_ATTEMPTS:
                    time.sleep(3 * attempt)  # exponential backoff

        # All attempts failed — remove the unanswered user message
        self.messages.pop()
        exc = DeepSeekExhausted(
            f"DeepSeek failed all {self.DEEPSEEK_MAX_ATTEMPTS} attempts. "
            f"Last error: {last_error}"
        )
        exc.prompt_size = len(prompt)
        raise exc


class DeepSeekExhausted(Exception):
    """Raised when DeepSeek fails all retry attempts."""
    prompt_size: int = 0


class GeminiReviewChat:
    """Multi-turn review conversation with Gemini 3.1 Pro via SDK.

    Re-added for 5-model ecosystem test. Native multi-turn chat via
    client.chats.create(). 5-attempt retry with timeout enforcement.
    """

    GEMINI_TIMEOUT = 300  # class-level fallback
    GEMINI_MAX_ATTEMPTS = 5

    def __init__(self, timeout: int | None = None, system_prompt: str | None = None):
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY / GOOGLE_API_KEY not set")
        self.client = genai.Client(api_key=api_key)
        # System-level directive injection via system_instruction parameter.
        # This persists across all turns in the chat session.
        config_kwargs = {"max_output_tokens": 32768, "temperature": 0.0}
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt
        self.chat = self.client.chats.create(
            model="gemini-3.1-pro-preview",
            config=genai.types.GenerateContentConfig(**config_kwargs),
        )
        self._timeout = timeout if timeout is not None else self.GEMINI_TIMEOUT

    def _send_once(self, prompt: str, timeout: int) -> str:
        """Single send attempt with hard timeout enforcement."""
        import concurrent.futures
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = pool.submit(self.chat.send_message, prompt)
        try:
            response = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            future.cancel()
            pool.shutdown(wait=False, cancel_futures=True)
            raise
        pool.shutdown(wait=False)
        text = response.text or ""
        return text.strip()

    def send(self, prompt: str, timeout: int | None = None) -> str:
        """Send with 5-attempt retry. Raises GeminiExhausted on failure."""
        timeout = timeout if timeout is not None else self._timeout
        _prompt_size_check(prompt, "gemini_chat")
        last_error = None
        for attempt in range(1, self.GEMINI_MAX_ATTEMPTS + 1):
            if attempt > 1:
                _err(f"    [gemini_chat retry] attempt {attempt}/{self.GEMINI_MAX_ATTEMPTS}")
            t0 = time.monotonic()
            try:
                text = self._send_once(prompt, timeout)
                elapsed = time.monotonic() - t0
                _err(f"  [gemini_chat] done ({elapsed:.1f}s, {len(text)} chars)")
                return text
            except Exception as e:
                elapsed = time.monotonic() - t0
                last_error = e
                _err(f"    [gemini_chat retry] attempt {attempt} failed "
                     f"({elapsed:.1f}s): {str(e)[:100]}")
                time.sleep(3)

        exc = GeminiExhausted(
            f"Gemini chat failed all {self.GEMINI_MAX_ATTEMPTS} attempts. "
            f"Last error: {last_error}"
        )
        exc.prompt_size = len(prompt)
        raise exc


class GeminiExhausted(Exception):
    """Raised when Gemini fails all retry attempts."""
    prompt_size: int = 0


class ChatGPTReviewChat:
    """Multi-turn review conversation with GPT-5.4 via chatgpt CLI.

    Uses kardolus/chatgpt-cli in pipe mode. Stateless per call,
    so we accumulate conversation history manually (same approach as CX).
    """

    CHATGPT_TIMEOUT = 600  # 10 min — GPT-5.4 can be slow (class-level fallback)
    CHATGPT_MAX_ATTEMPTS = 3
    MAX_CONTEXT_CHARS = 8000  # ~2000 tokens — leaves room for current prompt
    MAX_FULL_RESPONSES = 2    # keep last 2 reviewer responses in full

    def __init__(self, task_id: str, timeout: int | None = None, system_prompt: str | None = None):
        self.task_id = task_id
        self.history: list[tuple[str, str]] = []  # (role, text)
        self.responses: list[str] = []  # reviewer responses only (for summarisation)
        self._timeout = timeout if timeout is not None else self.CHATGPT_TIMEOUT
        # Context-level methodology injection (best available for chatgpt CLI pipe mode).
        self._system_prompt = system_prompt

    def _summarise_response(self, resp: str, round_num: int) -> str:
        """One-line summary of a prior response for context cap.

        Finding 3 fix: preserves verifiable_claim JSON objects from truncated
        responses. Structured data survives context capping.
        """
        import re
        count = len(re.findall(r'"finding_id"', resp))
        claims = _extract_verifiable_claims_from_text(resp)
        claims_str = f" Claims: {json.dumps(claims[:3])}" if claims else ""  # CX C3: cap at 3 claims per summary
        topic = resp[:150].replace("\n", " ").strip()
        return f"Round {round_num}: ~{count} findings.{claims_str} Topics: {topic}..."

    def send(self, prompt: str, timeout: int | None = None) -> str:
        """Send a message with capped context to prevent overflow."""
        timeout = timeout if timeout is not None else self._timeout
        self.history.append(("orchestrator", prompt))

        # Build context with cap — same pattern as CXReviewChat
        if len(self.history) == 1:
            # First message: prepend system prompt if available (context-level injection)
            if self._system_prompt:
                full_prompt = f"METHODOLOGY DIRECTIVES:\n{self._system_prompt}\n\nTASK:\n{prompt}"
            else:
                full_prompt = prompt
        else:
            context_parts = [
                "This is a continuing review conversation. "
                "Build on YOUR OWN prior findings — do not repeat them.\n"
            ]

            # Older responses: summarised one-liners
            if len(self.responses) > self.MAX_FULL_RESPONSES:
                for i, resp in enumerate(self.responses[:-self.MAX_FULL_RESPONSES]):
                    context_parts.append(self._summarise_response(resp, i + 1))

            # Recent responses: full text, newest-first budget priority
            recent = self.responses[-self.MAX_FULL_RESPONSES:]
            recent_start = max(0, len(self.responses) - self.MAX_FULL_RESPONSES)
            total_chars = sum(len(p) for p in context_parts)
            recent_entries = []
            for i in range(len(recent) - 1, -1, -1):  # newest first
                resp = recent[i]
                round_num = recent_start + i + 1
                entry = f"--- YOUR RESPONSE (round {round_num}) ---\n{resp}\n"
                if total_chars + len(entry) > self.MAX_CONTEXT_CHARS:
                    remaining = self.MAX_CONTEXT_CHARS - total_chars
                    if remaining > 200:
                        recent_entries.append(
                            f"--- YOUR RESPONSE (round {round_num}, truncated) ---\n{resp[:remaining]}...\n"
                        )
                    break
                recent_entries.append(entry)
                total_chars += len(entry)
            context_parts.extend(reversed(recent_entries))  # chronological

            # Current prompt
            context_parts.append(f"--- ORCHESTRATOR (current round) ---\n{prompt}\n")
            context_parts.append("Respond now.")
            full_prompt = "\n".join(context_parts)

        _prompt_size_check(full_prompt, "chatgpt_chat")
        last_error = None

        for attempt in range(1, self.CHATGPT_MAX_ATTEMPTS + 1):
            if attempt > 1:
                _err(f"    [chatgpt retry] attempt {attempt}/{self.CHATGPT_MAX_ATTEMPTS}")
            t0 = time.monotonic()
            try:
                result = sp.run(
                    ["chatgpt", "-q", "--model", "gpt-5.4"],
                    input=full_prompt,
                    capture_output=True, text=True, timeout=timeout,
                )
                elapsed = time.monotonic() - t0
                text = result.stdout.strip()
                if not text:
                    raise RuntimeError(
                        f"chatgpt returned empty output "
                        f"(exit {result.returncode}, stderr: {result.stderr[:200]})"
                    )
                _err(f"  [chatgpt_chat] done ({elapsed:.1f}s, {len(text)} chars)")
                self.history.append(("reviewer", text))
                self.responses.append(text)
                return text
            except sp.TimeoutExpired:
                elapsed = time.monotonic() - t0
                last_error = RuntimeError(f"chatgpt timed out after {timeout}s")
                _err(f"    [chatgpt retry] attempt {attempt} timed out ({elapsed:.1f}s)")
                time.sleep(3 * attempt)
            except Exception as e:
                elapsed = time.monotonic() - t0
                last_error = e
                _err(f"    [chatgpt retry] attempt {attempt} failed "
                     f"({elapsed:.1f}s): {str(e)[:100]}")
                time.sleep(3 * attempt)

        # Remove unanswered orchestrator message
        self.history.pop()
        raise ChatGPTExhausted(
            f"ChatGPT failed all {self.CHATGPT_MAX_ATTEMPTS} attempts. "
            f"Last error: {last_error}"
        )


class ChatGPTExhausted(Exception):
    """Raised when ChatGPT fails all retry attempts."""
    prompt_size: int = 0


class CXReviewChat:
    """Simulated multi-turn review conversation with Codex via codex exec.

    codex exec is stateless, so we carry forward context manually.
    To avoid context overflow (CX P-pass: 52K chars at round 2 with
    research-enriched HIL prompts), we carry only CX's OWN prior
    responses — not the full orchestrator prompts, which contain
    redundant task descriptions, expert guidance, and research results
    that CX already processed in round 1.

    MAX_CONTEXT_CHARS caps the total prior context to prevent overflow.
    Oldest responses are summarised if the cap is exceeded.
    """

    MAX_CONTEXT_CHARS = 6000   # ~1500 tokens — tight cap to conserve CX quota
    MAX_FULL_RESPONSES = 2     # keep last 2 responses in full, summarise older

    def __init__(self, task_id: str, timeout: int | None = None, system_prompt: str | None = None):
        self.task_id = task_id
        self.responses: list[str] = []  # CX's own prior responses only
        self.summaries: list[str] = []  # compact summaries of older rounds
        self._timeout = timeout if timeout is not None else CX_TIMEOUT
        # Context-level methodology injection (best available for codex exec).
        # Prepended to the first prompt. Weaker than true system prompt.
        self._system_prompt = system_prompt

    def _summarise_response(self, resp: str, round_num: int) -> str:
        """Compact summary of a prior response — topics, finding count, and claims.

        Finding 3 fix: preserves verifiable_claim JSON objects from truncated
        responses. Structured data survives context capping.
        """
        import re
        finding_markers = re.findall(r'(?:Finding|HARD|SOFT|Claim|Issue)\b', resp, re.I)
        count = len(finding_markers) if finding_markers else 1
        # Extract verifiable_claim objects before summarisation
        claims = _extract_verifiable_claims_from_text(resp)
        claims_str = f" Claims: {json.dumps(claims[:3])}" if claims else ""  # CX C3: cap at 3 claims per summary
        topic = resp[:150].replace('\n', ' ').strip()
        return f"Round {round_num}: ~{count} findings.{claims_str} Topics: {topic}..."

    def send(self, prompt: str, timeout: int | None = None) -> str:
        """Send a message with aggressively capped context.

        Keeps last 2 responses in full. Older responses become one-line
        summaries. Total context capped at MAX_CONTEXT_CHARS.
        This conserves CX's token quota while preserving recent context.
        """
        timeout = timeout if timeout is not None else self._timeout

        if not self.responses:
            # First message: prepend system prompt if available (context-level injection)
            if self._system_prompt:
                full_prompt = f"METHODOLOGY DIRECTIVES:\n{self._system_prompt}\n\nTASK:\n{prompt}"
            else:
                full_prompt = prompt
        else:
            context_parts = []

            # Older rounds: compact summaries only
            if len(self.responses) > self.MAX_FULL_RESPONSES:
                older = self.responses[:-self.MAX_FULL_RESPONSES]
                summary_lines = [
                    self._summarise_response(r, i + 1)
                    for i, r in enumerate(older)
                ]
                context_parts.append(
                    "PRIOR ROUNDS (summarised):\n" + "\n".join(summary_lines) + "\n"
                )

            # Recent rounds: full text, newest-first budget priority.
            # Build in REVERSE (newest first) so the most recent gets budget
            # priority. Then reverse for chronological display.
            recent = self.responses[-self.MAX_FULL_RESPONSES:]
            recent_start = max(0, len(self.responses) - self.MAX_FULL_RESPONSES)
            total_chars = sum(len(p) for p in context_parts)
            recent_entries = []
            for i in range(len(recent) - 1, -1, -1):  # newest first
                resp = recent[i]
                round_num = recent_start + i + 1
                label = f"YOUR RESPONSE (round {round_num})"
                entry = f"--- {label} ---\n{resp}\n"
                if total_chars + len(entry) > self.MAX_CONTEXT_CHARS:
                    remaining = self.MAX_CONTEXT_CHARS - total_chars
                    if remaining > 200:
                        recent_entries.append(
                            f"--- {label} (truncated) ---\n{resp[:remaining]}...\n"
                        )
                    break
                recent_entries.append(entry)
                total_chars += len(entry)
            context_parts.extend(reversed(recent_entries))  # chronological

            full_prompt = (
                "This is a continuing review. "
                "Build on YOUR OWN prior findings — do not repeat them.\n\n"
                + "\n".join(context_parts)
                + f"\n--- CURRENT ROUND ---\n{prompt}\n"
                + "Respond now."
            )

        _prompt_size_check(full_prompt, "cx_chat")
        t0 = time.monotonic()

        output_path = Path(f"/tmp/cx_rr_{self.task_id}_{int(time.time())}.txt")
        proj_dir = str(Path.home() / "Developer_Projects" / "Constraint_Engineering")
        try:
            result = sp.run(
                ["codex", "exec", "-o", str(output_path), "-C", proj_dir, full_prompt],
                capture_output=True, text=True, timeout=timeout,
            )
            elapsed = time.monotonic() - t0

            text = ""
            if output_path.exists():
                text = output_path.read_text().strip()
                output_path.unlink(missing_ok=True)

            if not text:
                text = result.stdout.strip() if result.stdout else ""

            if not text:
                raise RuntimeError(
                    f"codex exec returned empty output "
                    f"(exit {result.returncode}, stderr: {result.stderr[:200]})"
                )

            _err(f"  [cx_chat] done ({elapsed:.1f}s, {len(text)} chars)")
            self.responses.append(text)
            return text

        except sp.TimeoutExpired:
            output_path.unlink(missing_ok=True)
            raise RuntimeError(f"codex exec timed out after {timeout}s")


# ---------------------------------------------------------------------------
# Finding extraction and normalisation
# ---------------------------------------------------------------------------


def _normalise_finding(f: dict) -> dict:
    """Normalise a finding record: enforce schema, normalise constraint_class.

    CX P-pass fix (HARD 4): validates and normalises findings so formatting
    drift (e.g. 'hard ' with trailing space) doesn't suppress HARD detection.
    """
    normalised = {}
    normalised["finding_id"] = str(f.get("finding_id", "F_UNKNOWN")).strip()
    normalised["claim"] = str(f.get("claim", "")).strip()
    normalised["evidence_span"] = str(f.get("evidence_span", "")).strip()

    # Normalise constraint_class: strip whitespace, uppercase, default SOFT.
    # Finding 4 fix: default to SOFT not HARD — prevents phantom HARD findings
    # when models omit the field. Explicit "HARD" must be stated, not assumed.
    raw_class = str(f.get("constraint_class", "SOFT")).strip().upper()
    normalised["constraint_class"] = raw_class if raw_class in ("HARD", "SOFT") else "SOFT"

    # Normalise severity
    raw_sev = str(f.get("severity", "major")).strip().lower()
    normalised["severity"] = raw_sev if raw_sev in ("critical", "major", "minor") else "major"

    # Normalise confidence
    try:
        conf = float(f.get("confidence", 0.5))
        normalised["confidence"] = max(0.0, min(1.0, conf))
    except (ValueError, TypeError):
        normalised["confidence"] = 0.5

    normalised["proposed_check"] = str(f.get("proposed_check", "")).strip()
    normalised["verifiable_claim"] = f.get("verifiable_claim")  # preserve if present

    # CX extended P-pass: preserve structural fields for structural_canon_hash.
    # Also preserve _source_model for cross-model tracking.
    for extra_field in ("artifact", "assumption", "violation_mode", "witness", "_source_model"):
        if extra_field in f:
            normalised[extra_field] = f[extra_field]

    return normalised


CLAIM_EXTRACTION_PROMPT = """\
Extract mathematical claims from the following review findings. For each \
finding that contains a mathematical assertion (a bound, inequality, equality, \
convergence claim, or computational result), express it as a SymPy-parseable \
structured object.

FINDINGS:
{findings_json}

Return a JSON array. For EVERY finding_id, produce an entry:
- If it contains a mathematical claim: {{"finding_id": "F1", "expression": {{"op": "gt", "lhs": "a*b", "rhs": "1 + 3*pi/2"}}, "claim_text": "the bound ab > 1+3pi/2"}}
- If it contains NO mathematical claim: {{"finding_id": "F1", "expression": null, "claim_text": null}}

Use SymPy-parseable expressions. Valid ops: eq, gt, lt, ge, le, ne.
Return ONLY the JSON array, nothing else.
"""


def _extract_verifiable_claims(findings: list[dict]) -> dict:
    """CC extracts mathematical claims from raw findings (blinded).

    This is the 'team captain' role: actively processing model output
    rather than passively hoping for structured fields. Model names are
    NOT included in the extraction prompt to prevent selective bias.

    Returns: {finding_id: {"expression": dict|None, "claim_text": str|None}}
    """
    if not findings:
        return {}

    # Blind the findings — strip model identity
    blinded = []
    for f in findings:
        blinded.append({
            "finding_id": f.get("finding_id", ""),
            "claim": f.get("claim", ""),
            "evidence_span": f.get("evidence_span", "")[:500],
        })

    prompt = _safe_format(
        CLAIM_EXTRACTION_PROMPT,
        findings_json=json.dumps(blinded, indent=2)[:8000],
    )

    try:
        raw = _call_cc(None, prompt)
        # Parse JSON array from response — try progressively to handle
        # CC appending commentary after the JSON array
        import re
        # Find all potential JSON array starts
        for match in re.finditer(r'\[', raw):
            start = match.start()
            # Try to parse from this [ to find matching ]
            depth = 0
            for i in range(start, len(raw)):
                if raw[i] == '[':
                    depth += 1
                elif raw[i] == ']':
                    depth -= 1
                    if depth == 0:
                        candidate = raw[start:i+1]
                        try:
                            extracted = json.loads(candidate)
                            if isinstance(extracted, list):
                                return {
                                    item["finding_id"]: {
                                        "expression": item.get("expression"),
                                        "claim_text": item.get("claim_text"),
                                    }
                                    for item in extracted
                                    if isinstance(item, dict) and "finding_id" in item
                                }
                        except json.JSONDecodeError:
                            continue  # try next [
                        break
    except Exception as exc:
        _err(f"  [extract] claim extraction failed: {exc}")

    return {}


def _verify_findings(findings: list[dict], condition: str, sympy_timeout: int = 10) -> dict:
    """Verify mathematical claims in findings using SymPy kernel.

    Runs on ALL conditions as a MEASUREMENT tool (cross-condition quality
    comparison). For findings lacking verifiable_claim, CC extracts claims
    (blinded). Feedback to models is CDSFL-exclusive (confer path only).

    Returns:
        {"scores": [float], "aggregate": float, "determinate_count": int,
         "details": [dict]}

    Verification metadata is kept in orchestrator records ONLY — it is
    NOT attached to findings passed to reviewers (CX P-pass: would
    contaminate next round's reviewer behaviour).
    """
    # SymPy verification runs on ALL conditions as a MEASUREMENT tool
    # (scoring finding quality for cross-condition comparison).
    # It is only fed BACK to models as a METHODOLOGY tool under CDSFL.
    # This distinction was identified by the founder on 2026-03-24:
    # without v-bar on Control/HIL, we cannot compare quality across conditions.

    # Hybrid approach (CC-CX confer, 2026-03-24):
    # 1. Trust model-provided verifiable_claim when present
    # 2. For findings missing the field, CC extracts claims (blinded)
    # 3. Track both sources: v_bar_provided and v_bar_augmented
    extracted_claims = {}
    findings_missing_vc = [f for f in findings if not f.get("verifiable_claim") or not isinstance(f.get("verifiable_claim"), dict)]
    if findings_missing_vc:
        _err(f"  [verify] {len(findings_missing_vc)}/{len(findings)} findings lack verifiable_claim — CC extracting ...")
        extracted_claims = _extract_verifiable_claims(findings_missing_vc)
        _err(f"  [verify] CC extracted {sum(1 for v in extracted_claims.values() if v.get('expression'))} claims from {len(findings_missing_vc)} findings")

    scores = []
    scores_provided = []
    scores_extracted = []
    details = []
    for f in findings:
        vc = f.get("verifiable_claim")
        source = "provided"

        # If no model-provided claim, try CC-extracted
        if not vc or not isinstance(vc, dict):
            fid = f.get("finding_id", "")
            extracted = extracted_claims.get(fid, {})
            vc = extracted.get("expression")
            source = "extracted"

        if not vc or not isinstance(vc, dict):
            continue  # genuinely no mathematical claim — skip, don't penalise

        result = _verify_sympy(vc, timeout=sympy_timeout)
        if result["verified"] is True:
            scores.append(1.0)
        elif result["verified"] is False:
            scores.append(0.0)
        # verified=None → unverifiable, not scored (CX P-pass: don't count unknowns)

        score_val = scores[-1] if scores and result["verified"] is not None else None
        details.append({
            "finding_id": f.get("finding_id", ""),
            "source_model": f.get("_source_model", ""),
            "claim": vc,
            "source": source,
            "verification": result,
            "score": score_val,
        })

        # Track by source for separate v_bar reporting
        if score_val is not None:
            if source == "provided":
                scores_provided.append(score_val)
            else:
                scores_extracted.append(score_val)

    determinate = [s for s in scores]  # only True/False scores
    aggregate = sum(determinate) / len(determinate) if determinate else 0.0
    agg_provided = sum(scores_provided) / len(scores_provided) if scores_provided else 0.0
    agg_extracted = sum(scores_extracted) / len(scores_extracted) if scores_extracted else 0.0

    return {
        "scores": scores,
        "aggregate": round(aggregate, 3),
        "v_bar_provided": round(agg_provided, 3),
        "v_bar_extracted": round(agg_extracted, 3),
        "determinate_count": len(determinate),
        "provided_count": len(scores_provided),
        "extracted_count": len(scores_extracted),
        "details": details,
    }


def _should_override_stop(verification: dict) -> bool:
    """Asymmetric override: prevent premature stop if high-quality findings
    are still emerging.

    Returns True if counting says stop but verification says continue.
    Does NOT implement reverse override (early stop) — deferred until
    calibration data exists (CX P-pass recommendation).

    Gate conditions:
    - At least VERIFY_MIN_SAMPLE determinate verifications (avoid small-sample noise)
    - Aggregate score >= VERIFY_CONTINUE_THRESHOLD
    """
    if verification["determinate_count"] < VERIFY_MIN_SAMPLE:
        return False  # not enough data to override
    return verification["aggregate"] >= VERIFY_CONTINUE_THRESHOLD


def _extract_findings_json(response: str) -> list[dict]:
    """Extract structured findings from model response.

    Attempts JSON parse first; falls back to heuristic extraction.
    All findings are normalised through _normalise_finding.
    """
    import re

    # Try to find a JSON array in FINDINGS section
    findings_text = _extract_section(response, "FINDINGS")
    if findings_text:
        # Try direct JSON parse
        try:
            parsed = json.loads(findings_text)
            if isinstance(parsed, list):
                return [_normalise_finding(f) for f in parsed if isinstance(f, dict)]
        except json.JSONDecodeError:
            pass
        # Try to find embedded JSON array
        json_match = re.search(r'\[.*\]', findings_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list):
                    return [_normalise_finding(f) for f in parsed if isinstance(f, dict)]
            except json.JSONDecodeError:
                pass

    # Fallback: create a single finding from the full response
    return [_normalise_finding({
        "finding_id": "F_UNSTRUCTURED",
        "claim": "Response did not contain structured findings",
        "evidence_span": response[:500],
        "constraint_class": "SOFT",
        "severity": "minor",
        "confidence": 0.5,
        "proposed_check": "Manual review required",
    })]


def _extract_confer_response(response: str) -> dict:
    """Extract structured confer response (assessments + new findings + concur)."""
    result: dict[str, Any] = {
        "assessments": [],
        "new_findings": [],
        "concur_stop": False,
        "justification": "",
    }

    # Try ASSESSMENTS
    assessments_text = _extract_section(response, "ASSESSMENTS")
    if assessments_text:
        try:
            import re
            json_match = re.search(r'\[.*\]', assessments_text, re.DOTALL)
            if json_match:
                result["assessments"] = json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

    # Try NEW_FINDINGS — normalise through _normalise_finding (CX HARD 4 residual fix)
    # CX extended P-pass cycle 4: fallback chain when primary parse fails.
    new_findings_text = _extract_section(response, "NEW_FINDINGS")
    if new_findings_text:
        try:
            import re
            json_match = re.search(r'\[.*\]', new_findings_text, re.DOTALL)
            if json_match:
                raw_findings = json.loads(json_match.group())
                result["new_findings"] = [
                    _normalise_finding(f) for f in raw_findings if isinstance(f, dict)
                ]
        except (json.JSONDecodeError, AttributeError):
            pass

    # Fallback: if NEW_FINDINGS parse failed, try extracting any JSON array from full response.
    # Finding 4 fix: validate that extracted arrays contain finding-like dicts
    # (must have "claim" field), not assessment-like dicts. Reject arrays where
    # most items lack both "claim" and "evidence_span". Default constraint_class
    # to SOFT (not HARD) for fallback-extracted findings where model didn't specify.
    if not result["new_findings"]:
        try:
            import re
            json_arrays = re.findall(r'\[[\s\S]*?\]', response)
            for arr_str in json_arrays:
                try:
                    parsed = json.loads(arr_str)
                    if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
                        # Validate: majority of items must look like findings, not assessments
                        finding_like = sum(
                            1 for f in parsed
                            if isinstance(f, dict) and ("claim" in f or "evidence_span" in f)
                        )
                        if finding_like < len(parsed) * 0.5:
                            continue  # mostly assessment-like — skip this array
                        # Default constraint_class to SOFT for fallback-extracted findings
                        for f in parsed:
                            if isinstance(f, dict) and "constraint_class" not in f:
                                f["constraint_class"] = "SOFT"
                        result["new_findings"] = [
                            _normalise_finding(f) for f in parsed if isinstance(f, dict)
                        ]
                        break
                except (json.JSONDecodeError, TypeError):
                    continue
        except Exception:
            pass

    # CONCUR_STOP
    import re
    concur_match = re.search(r'CONCUR_STOP:\s*(true|false)', response, re.IGNORECASE)
    if concur_match:
        result["concur_stop"] = concur_match.group(1).lower() == "true"

    # JUSTIFICATION
    just_text = _extract_section(response, "JUSTIFICATION")
    if just_text:
        result["justification"] = just_text.strip()

    return result


# ---------------------------------------------------------------------------
# Round execution
# ---------------------------------------------------------------------------


def _run_blind_round(
    task: dict,
    solution: str,
    chain: VerificationChain,
    ledger: CostLedger,
    condition: str = "cdsfl",
    expert_guidance: str = "",
    deepseek_chat: "DeepSeekReviewChat | None" = None,
    cx_chat: "CXReviewChat | None" = None,
    gemini_chat: "GeminiReviewChat | None" = None,
    chatgpt_chat: "ChatGPTReviewChat | None" = None,
) -> dict:
    """Round 1: 5-way blind review — CC, DeepSeek, Codex, Gemini, ChatGPT independently review.

    CC is captain of the team, not just the referee. It participates as a
    full reviewer alongside all others, contributing findings through
    the same CDSFL loop. Phase 2 only: persistent conversations via chat objects.
    """
    task_id = task["id"]
    phase = "phase2" if deepseek_chat else "phase1"
    _err(f"  [round 1/blind/{phase}] starting 5-way blind review for {task_id} [{condition}]")

    blind_template, _ = _get_condition_prompts(condition)

    fmt_kwargs = {"task_prompt": task["prompt"], "solution": solution}
    if condition in ("hil", "cdsfl_hil"):
        fmt_kwargs["expert_guidance"] = expert_guidance

    blind_prompt = _safe_format(blind_template, **fmt_kwargs)

    # Hash the input bundle
    input_bundle = json.dumps({
        "task_id": task_id,
        "round": 1,
        "round_type": "blind",
        "solution_hash": _content_hash(solution),
        "prompt_hash": _content_hash(blind_prompt),
    }, sort_keys=True)
    input_hash = _content_hash(input_bundle)
    chain.record("round_input", input_bundle, {"task_id": task_id, "round": 1})

    # DeepSeek blind review
    deepseek_findings_raw = ""
    deepseek_findings: list[dict] = []
    deepseek_error = None
    _err(f"  [round 1/blind] calling DeepSeek V3.2 ...")
    t0 = time.monotonic()
    try:
        if not deepseek_chat:
            raise RuntimeError("Phase 2 requires DeepSeekReviewChat — no stateless fallback")
        deepseek_findings_raw = deepseek_chat.send(blind_prompt)
        deepseek_findings = _extract_findings_json(deepseek_findings_raw)
        elapsed = time.monotonic() - t0
        _err(f"  [round 1/blind] DeepSeek done ({elapsed:.1f}s, {len(deepseek_findings)} findings)")
        ledger.record("deepseek_api", 0.0)  # free tier / prepaid
    except DeepSeekExhausted:
        raise  # non-skippable — propagate for stop-and-diagnose
    except Exception as exc:
        elapsed = time.monotonic() - t0
        deepseek_error = str(exc)
        _err(f"  [round 1/blind] DeepSeek FAILED ({elapsed:.1f}s): {deepseek_error[:100]}")

    chain.record("deepseek_blind", deepseek_findings_raw or f"ERROR: {deepseek_error}",
                 {"task_id": task_id, "round": 1})

    # CX blind review
    cx_findings_raw = ""
    cx_findings: list[dict] = []
    cx_error = None
    _err(f"  [round 1/blind] calling Codex 5.3 ...")
    t0 = time.monotonic()
    try:
        if cx_chat:
            cx_findings_raw = cx_chat.send(blind_prompt)
        else:
            cx_findings_raw = _call_cx_reviewer(blind_prompt, task_id)
        cx_findings = _extract_findings_json(cx_findings_raw)
        elapsed = time.monotonic() - t0
        _err(f"  [round 1/blind] CX done ({elapsed:.1f}s, {len(cx_findings)} findings)")
        ledger.record("codex", 0.0)  # subscription-based, no per-call cost
    except Exception as exc:
        elapsed = time.monotonic() - t0
        cx_error = str(exc)
        _err(f"  [round 1/blind] CX FAILED ({elapsed:.1f}s): {cx_error[:100]}")

    chain.record("cx_blind", cx_findings_raw or f"ERROR: {cx_error}",
                 {"task_id": task_id, "round": 1})

    # CC blind review — captain participates, not just arbitrates
    cc_findings_raw = ""
    cc_findings: list[dict] = []
    cc_error = None
    _err(f"  [round 1/blind] calling Opus 4.6 (CC) ...")
    t0 = time.monotonic()
    try:
        cc_findings_raw = _call_cc(None, blind_prompt)
        cc_findings = _extract_findings_json(cc_findings_raw)
        elapsed = time.monotonic() - t0
        _err(f"  [round 1/blind] CC done ({elapsed:.1f}s, {len(cc_findings)} findings)")
        ledger.record("cc_review", 0.0)  # subscription-based
    except Exception as exc:
        elapsed = time.monotonic() - t0
        cc_error = str(exc)
        _err(f"  [round 1/blind] CC FAILED ({elapsed:.1f}s): {cc_error[:100]}")

    chain.record("cc_blind", cc_findings_raw or f"ERROR: {cc_error}",
                 {"task_id": task_id, "round": 1})

    # Gemini blind review
    gemini_findings_raw = ""
    gemini_findings: list[dict] = []
    gemini_error = None
    _err(f"  [round 1/blind] calling Gemini 3.1 Pro ...")
    t0 = time.monotonic()
    try:
        if not gemini_chat:
            raise RuntimeError("Phase 2 requires GeminiReviewChat")
        gemini_findings_raw = gemini_chat.send(blind_prompt)
        gemini_findings = _extract_findings_json(gemini_findings_raw)
        elapsed = time.monotonic() - t0
        _err(f"  [round 1/blind] Gemini done ({elapsed:.1f}s, {len(gemini_findings)} findings)")
        ledger.record("gemini_api", 0.0)
    except GeminiExhausted:
        raise
    except Exception as exc:
        elapsed = time.monotonic() - t0
        gemini_error = str(exc)
        _err(f"  [round 1/blind] Gemini FAILED ({elapsed:.1f}s): {gemini_error[:100]}")

    chain.record("gemini_blind", gemini_findings_raw or f"ERROR: {gemini_error}",
                 {"task_id": task_id, "round": 1})

    # ChatGPT 5.4 blind review
    chatgpt_findings_raw = ""
    chatgpt_findings: list[dict] = []
    chatgpt_error = None
    _err(f"  [round 1/blind] calling ChatGPT 5.4 ...")
    t0 = time.monotonic()
    try:
        if not chatgpt_chat:
            raise RuntimeError("Phase 2 requires ChatGPTReviewChat")
        chatgpt_findings_raw = chatgpt_chat.send(blind_prompt)
        chatgpt_findings = _extract_findings_json(chatgpt_findings_raw)
        elapsed = time.monotonic() - t0
        _err(f"  [round 1/blind] ChatGPT done ({elapsed:.1f}s, {len(chatgpt_findings)} findings)")
        ledger.record("chatgpt_api", 0.0)
    except ChatGPTExhausted:
        raise
    except Exception as exc:
        elapsed = time.monotonic() - t0
        chatgpt_error = str(exc)
        _err(f"  [round 1/blind] ChatGPT FAILED ({elapsed:.1f}s): {chatgpt_error[:100]}")

    chain.record("chatgpt_blind", chatgpt_findings_raw or f"ERROR: {chatgpt_error}",
                 {"task_id": task_id, "round": 1})

    return {
        "round": 1,
        "round_type": "blind",
        "input_hash": input_hash,
        "cc": {
            "raw_response": cc_findings_raw,
            "findings": cc_findings,
            "error": cc_error,
        },
        "deepseek": {
            "raw_response": deepseek_findings_raw,
            "findings": deepseek_findings,
            "error": deepseek_error,
        },
        "cx": {
            "raw_response": cx_findings_raw,
            "findings": cx_findings,
            "error": cx_error,
        },
        "gemini": {
            "raw_response": gemini_findings_raw,
            "findings": gemini_findings,
            "error": gemini_error,
        },
        "chatgpt": {
            "raw_response": chatgpt_findings_raw,
            "findings": chatgpt_findings,
            "error": chatgpt_error,
        },
    }


SELF_ITERATE_PROMPT = """\
You previously reviewed a solution and produced findings. Here are YOUR \
OWN findings from the previous round:

{own_findings}

Look at the solution again. Are there issues you MISSED in your previous \
review? Focus on what you overlooked, not on restating what you already found. \
If you genuinely have nothing new to add, state that explicitly with a brief \
justification for why you believe your review is complete.

Solution under review:
{solution_excerpt}

Output your NEW findings (if any) as a JSON array in a FINDINGS block:
```FINDINGS
[
  {{"finding_id": "F1", "claim": "...", "evidence_span": "...", \
"constraint_class": "HARD or SOFT", "severity": "critical/major/minor", \
"confidence": 0.9, "proposed_check": "...", \
"verifiable_claim": {{"op": "eq", "lhs": "...", "rhs": "..."}} }}
]
```
The verifiable_claim field is optional but encouraged for any finding \
involving a mathematical or computational claim. Use SymPy-parseable \
expressions (e.g. {{"op": "gt", "lhs": "a*b", "rhs": "1 + 3*pi/2"}}).

If you have nothing new, output:
```FINDINGS
[]
```
"""


def _run_self_iteration_round(
    task: dict,
    solution: str,
    chain: "VerificationChain",
    ledger: "CostLedger",
    round_num: int,
    prev_round: dict,
    condition: str = "control",
    expert_guidance: str = "",
    deepseek_chat=None,
    cx_chat=None,
    gemini_chat=None,
    chatgpt_chat=None,
) -> dict:
    """Self-iteration round for Control/HIL.

    Each model sees only its OWN prior findings and is asked to look again.
    No cross-model confer. Simulates a user saying 'check again, anything else?'
    """
    task_id = task["id"]
    _err(f"  [round {round_num}/self-iterate] starting for {task_id} [{condition}]")

    solution_excerpt = solution[:6000]
    results = {
        "round": round_num,
        "round_type": "self_iterate",
    }

    chat_map = {
        "deepseek": deepseek_chat,
        "cx": cx_chat,
        "cc": None,  # CC uses claude -p
        "gemini": gemini_chat,
        "chatgpt": chatgpt_chat,
    }

    for reviewer in REVIEWERS:
        # Get this model's OWN prior findings
        prev_data = prev_round.get(reviewer, {})
        if prev_round["round_type"] == "blind":
            own_findings = prev_data.get("findings", [])
        else:
            own_findings = prev_data.get("confer_response", {}).get("new_findings", [])
            if not own_findings:
                own_findings = prev_data.get("findings", [])

        own_str = json.dumps(own_findings, indent=2)[:3000] if own_findings else "(no prior findings)"

        prompt = _safe_format(
            SELF_ITERATE_PROMPT,
            own_findings=own_str,
            solution_excerpt=solution_excerpt,
        )

        if condition == "hil" and expert_guidance:
            prompt += f"\n\nExpert guidance: {expert_guidance}"

        _err(f"  [round {round_num}/self-iterate] calling {reviewer} ...")
        t0 = time.monotonic()
        raw = ""
        findings = []
        error = None

        try:
            chat = chat_map.get(reviewer)
            if reviewer == "cc":
                raw = _call_cc(None, prompt)
            elif chat:
                raw = chat.send(prompt)
            else:
                raw = ""
                error = f"{reviewer} chat not available"

            findings = _extract_findings_json(raw)
            elapsed = time.monotonic() - t0
            _err(f"  [round {round_num}/self-iterate] {reviewer} done "
                 f"({elapsed:.1f}s, {len(findings)} new findings)")
            ledger.record(f"{reviewer}_cli", 0.0)
        except Exception as exc:
            elapsed = time.monotonic() - t0
            error = str(exc)
            _err(f"  [round {round_num}/self-iterate] {reviewer} FAILED "
                 f"({elapsed:.1f}s): {error[:100]}")

        results[reviewer] = {
            "raw_response": raw[:5000],
            "findings": findings,
            "error": error,
        }

    chain.record("self_iterate_round", json.dumps({
        "round": round_num, "task_id": task_id,
    }), {"task_id": task_id, "round": round_num})

    return results


def _run_confer_round(
    task: dict,
    solution: str,
    round_num: int,
    cc_prev_findings: list[dict],
    deepseek_prev_findings: list[dict],
    cx_prev_findings: list[dict],
    gemini_prev_findings: list[dict],
    chatgpt_prev_findings: list[dict],
    chain: VerificationChain,
    ledger: CostLedger,
    output_dir: Path | None = None,
    condition: str = "cdsfl",
    expert_guidance: str = "",
    deepseek_chat: "DeepSeekReviewChat | None" = None,
    cx_chat: "CXReviewChat | None" = None,
    gemini_chat: "GeminiReviewChat | None" = None,
    chatgpt_chat: "ChatGPTReviewChat | None" = None,
    sympy_feedback: str = "",
) -> dict:
    """Rounds 2-5: Confer — each reviewer sees the OTHER FOUR's findings.

    Five-way cross-pollination. Each model sees all other models' findings
    plus SymPy verification feedback (CDSFL conditions only).
    CX P-pass fix (HARD 5): findings written to files.
    """
    task_id = task["id"]
    _err(f"  [round {round_num}/confer] starting confer round for {task_id} [{condition}]")

    _, confer_template = _get_condition_prompts(condition)

    # Write findings to artifact files (CX HARD fix 5: file-path payloads)
    artifacts_dir = (output_dir or RESULTS_DIR) / "artifacts" / task_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Map reviewer names to their previous findings
    prev_findings_map = {
        "cc": cc_prev_findings,
        "deepseek": deepseek_prev_findings,
        "cx": cx_prev_findings,
        "gemini": gemini_prev_findings,
        "chatgpt": chatgpt_prev_findings,
    }

    # Write findings to artifact files (CX HARD fix 5: file-path payloads)
    for reviewer_name, findings in prev_findings_map.items():
        fpath = artifacts_dir / f"round_{round_num}_{reviewer_name}_prev_findings.json"
        _atomic_write(fpath, json.dumps(findings, indent=2, sort_keys=True) + "\n")

    # Each reviewer sees the OTHER FOUR's combined findings
    confer_prompts: dict[str, str] = {}
    for reviewer_name in REVIEWERS:
        others = []
        for other_name in REVIEWERS:
            if other_name != reviewer_name:
                others.extend(prev_findings_map[other_name])
        others_json = json.dumps(others, indent=2, sort_keys=True)
        fmt_kwargs_r = {"task_prompt": task["prompt"], "solution": solution, "other_findings": others_json}
        if condition in ("hil", "cdsfl_hil"):
            fmt_kwargs_r["expert_guidance"] = expert_guidance
        confer_prompts[reviewer_name] = _safe_format(confer_template, **fmt_kwargs_r)

    # Hash the input bundle
    prompt_hashes = {f"{r}_prompt_hash": _content_hash(confer_prompts[r]) for r in REVIEWERS}
    input_bundle = json.dumps({
        "task_id": task_id,
        "round": round_num,
        "round_type": "confer",
        "solution_hash": _content_hash(solution),
        **prompt_hashes,
    }, sort_keys=True)
    input_hash = _content_hash(input_bundle)
    chain.record("round_input", input_bundle, {"task_id": task_id, "round": round_num})

    # Map reviewer names to their chat objects and ledger labels
    chat_map = {
        "cc": None,  # CC uses _call_cc, not a chat object
        "deepseek": deepseek_chat,
        "cx": cx_chat,
        "gemini": gemini_chat,
        "chatgpt": chatgpt_chat,
    }
    ledger_labels = {
        "cc": "cc_review",
        "deepseek": "deepseek_api",
        "cx": "codex",
        "gemini": "gemini_api",
        "chatgpt": "chatgpt_api",
    }
    reviewer_labels = {
        "cc": "Opus 4.6 (CC)",
        "deepseek": "DeepSeek",
        "cx": "CX",
        "gemini": "Gemini 3.1 Pro",
        "chatgpt": "ChatGPT 5.4",
    }
    # Exhausted exception types that must propagate (non-skippable)
    exhausted_types = (DeepSeekExhausted, GeminiExhausted, ChatGPTExhausted)

    confer_results: dict[str, dict] = {}
    for reviewer_name in REVIEWERS:
        raw = ""
        response: dict = {}
        error = None
        label = reviewer_labels[reviewer_name]
        _err(f"  [round {round_num}/confer] calling {label} (reviewing others' findings) ...")
        t0 = time.monotonic()
        try:
            if reviewer_name == "cc":
                raw = _call_cc(None, confer_prompts["cc"])
            elif reviewer_name == "cx":
                if cx_chat:
                    raw = cx_chat.send(confer_prompts["cx"])
                else:
                    raw = _call_cx_reviewer(confer_prompts["cx"], task_id)
            else:
                chat_obj = chat_map[reviewer_name]
                if not chat_obj:
                    raise RuntimeError(f"Phase 2 requires {label} chat — no stateless fallback")
                raw = chat_obj.send(confer_prompts[reviewer_name])
            response = _extract_confer_response(raw)
            elapsed = time.monotonic() - t0
            _err(f"  [round {round_num}/confer] {label} done ({elapsed:.1f}s, "
                 f"{len(response.get('new_findings', []))} new findings, "
                 f"concur_stop={response.get('concur_stop')})")
            ledger.record(ledger_labels[reviewer_name], 0.0)
        except exhausted_types:
            raise  # non-skippable — propagate for stop-and-diagnose
        except Exception as exc:
            elapsed = time.monotonic() - t0
            error = str(exc)
            _err(f"  [round {round_num}/confer] {label} FAILED ({elapsed:.1f}s): {error[:100]}")

        chain.record(f"{reviewer_name}_confer", raw or f"ERROR: {error}",
                     {"task_id": task_id, "round": round_num})
        confer_results[reviewer_name] = {
            "raw_response": raw,
            "confer_response": response,
            "error": error,
        }

    return {
        "round": round_num,
        "round_type": "confer",
        "input_hash": input_hash,
        **confer_results,
    }


# ---------------------------------------------------------------------------
# Novelty and stop-rule assessment
# ---------------------------------------------------------------------------


def _classify_round_findings(round_data: dict, verification_data: dict) -> dict:
    """Classify each finding's support level using CX refinements.

    Uses independence-aware peer confirmation, structural canonicalisation,
    and the validated-novelty channel. Runs on all conditions as measurement.

    Returns: {finding_id: {support_class, independent_families, canon_hash}}
    """
    # Collect all findings by model for cross-model comparison
    all_findings_by_model = {}
    for source in REVIEWERS:
        source_data = round_data.get(source, {})
        if round_data.get("round_type") == "blind":
            findings = source_data.get("findings", [])
        elif round_data.get("round_type") == "self_iterate":
            findings = source_data.get("findings", [])
        else:
            findings = source_data.get("confer_response", {}).get("new_findings", [])
        all_findings_by_model[source] = findings if isinstance(findings, list) else []

    # Classify each finding using the refinements module
    classifications = {}
    for source, findings in all_findings_by_model.items():
        for f in findings:
            if not isinstance(f, dict):
                continue
            fid = f.get("finding_id", "unknown")
            # Unique key: model + finding_id (prevents cross-model collision)
            unique_key = f"{source}:{fid}"

            # Use the classify_finding_support function from refinements
            support = classify_finding_support(
                f, all_findings_by_model, MODEL_FAMILIES
            )

            # Count independent families for peer support detail
            indep_count = count_independent_confirmations(f, all_findings_by_model)
            canon = structural_canon_hash(f)

            # Override with SymPy data if available
            # Match on both finding_id AND source model to prevent cross-model collision
            if verification_data and verification_data.get("details"):
                for d in verification_data["details"]:
                    d_fid = d.get("finding_id", "")
                    d_source = d.get("source_model", "")
                    if d_fid == fid and (not d_source or d_source == source):
                        if d.get("score") == 1.0:
                            support = "sympy_verified"
                        elif d.get("score") == 0.0:
                            support = "refuted"
                        break

            classifications[unique_key] = {
                "support_class": support,
                "independent_families": indep_count,
                "canon_hash": canon,
                "source_model": source,
                "finding_id": fid,
            }

    return classifications


def _count_novel_hard_findings(
    current_round: dict,
    all_known_keys: set[str],
    task_id: str,
) -> tuple[int, set[str]]:
    """Count novel HARD findings in this round. Returns (count, new_keys).

    CX P-pass fix (HARD 3): deduplicates WITHIN a round so the same HARD
    claim found by both models counts once (round-level accounting, not
    per-model accounting).
    """
    round_keys: set[str] = set()  # deduplicate within this round first

    for source in REVIEWERS:
        source_data = current_round.get(source, {})
        if current_round["round_type"] == "blind":
            findings = source_data.get("findings", [])
        elif current_round["round_type"] == "self_iterate":
            # Self-iteration rounds store findings directly (no confer_response)
            findings = source_data.get("findings", [])
        else:
            findings = source_data.get("confer_response", {}).get("new_findings", [])

        for f in findings:
            if not isinstance(f, dict):
                continue
            constraint = f.get("constraint_class", "SOFT").upper()
            if constraint != "HARD":
                continue
            claim = f.get("claim", "")
            key = _defect_key(task_id, constraint, claim, finding=f)
            round_keys.add(key)

    # Novel = keys in this round that aren't already known
    new_keys = round_keys - all_known_keys
    return len(new_keys), new_keys


def _all_concur_stop(round_data: dict, consecutive_zero_novel: int = 0) -> bool:
    """Check if all five reviewers concur that diminishing returns are reached.

    Five-way concurrence: CC, DeepSeek, CX, Gemini, and ChatGPT must all agree.
    Auto-concur applies to any reviewer with zero findings for 2+
    consecutive zero-novel rounds. Can't block with nothing to say.
    """
    concur_results = {}
    for source in REVIEWERS:
        findings_count = len(
            round_data.get(source, {})
            .get("confer_response", {})
            .get("new_findings", [])
        )
        concur = (
            round_data.get(source, {})
            .get("confer_response", {})
            .get("concur_stop", False)
        )
        # Auto-concur: zero findings + sustained zero-novel rounds
        if consecutive_zero_novel >= 2 and findings_count == 0 and not concur:
            _err(f"  [concur] {source} auto-concur (0 findings, {consecutive_zero_novel} zero-novel rounds)")
            concur = True
        concur_results[source] = concur

    return all(concur_results.values())


# ---------------------------------------------------------------------------
# Deterministic failure policy
# ---------------------------------------------------------------------------


def _with_retry(fn, *args, max_retries: int = 1, **kwargs):
    """Deterministic failure policy: one identical retry, then defer.

    Bug fix (2026-03-21): budget no longer gates retries. Each model gets
    its full timeout on every attempt. Budget exhaustion is checked only
    at task/condition boundaries.
    """
    for attempt in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            if attempt < max_retries:
                _err(f"  [retry] attempt {attempt + 1} failed: {str(exc)[:80]}, retrying...")
                time.sleep(5)
            else:
                raise


# ---------------------------------------------------------------------------
# CC solution generation (full CDSFL directives)
# ---------------------------------------------------------------------------


RAW_GENERATION_PROMPT = """\
Solve the following task. Provide a clear, complete, well-organised answer.

Task:
{task_prompt}
"""

# ---------------------------------------------------------------------------
# Decomposed generation — break complex problems into sequential steps
#
# Bug fix (2026-03-22): single-shot generation timed out at 20 minutes on
# complex mathematical tasks (ft-004, ft-002). Decomposing into 3 sequential
# calls (solve → attack → revise) keeps each step within timeout and mirrors
# how a human expert approaches complex problems.
#
# Applied to ALL models, not just CC — the principle is universal.
# ---------------------------------------------------------------------------

DECOMPOSED_STEP1_SOLVE = """\
Solve the following task. Focus only on producing the strongest, most \
complete answer you can. Do NOT self-critique yet — just solve it.

Task:
{task_prompt}
"""

DECOMPOSED_STEP2_ATTACK = """\
You produced the following answer to a task. Now attack it adversarially. \
Look for errors, contradictions, physical impossibilities, logical flaws, \
unstated assumptions, and constraint violations.

Original task:
{task_prompt}

Your answer:
{solution}

List every issue you find, each on its own line starting with "- ".
"""

DECOMPOSED_STEP3_CLASSIFY = """\
You found these issues with a solution. Classify each as HARD \
(physics, maths, logic, safety — must fix) or SOFT (style, preference, \
minor improvement — nice to fix). Return each issue on its own line \
prefixed with [HARD] or [SOFT].

Issues:
{issues}
"""

DECOMPOSED_STEP3_REVISE_BATCH = """\
Revise this solution to fix ONLY the issues listed below. Do not change \
anything else. Surface any remaining uncertainty. Return the complete \
revised solution.

Solution to revise:
{solution}

Issues to fix in this batch:
{issues_batch}
"""


def _split_issues(issues_text: str, max_per_batch: int = 5) -> list[str]:
    """Split a list of issues into batches of max_per_batch lines.

    CX P-pass: handles bullet lists, prose paragraphs, and empty input.
    """
    import re

    if not issues_text or not issues_text.strip():
        return []

    text = issues_text.strip()

    # Try bullet-style splitting first (lines starting with -, *, [HARD], [SOFT], etc.)
    bullet_lines = [l.strip() for l in text.split("\n")
                    if l.strip() and re.match(r'^[-*•\[]', l.strip())]
    if len(bullet_lines) >= 2:
        lines = bullet_lines
    elif len(text.split("\n")) >= 2:
        # Multiple lines but no bullets — use all non-empty lines
        lines = [l.strip() for l in text.split("\n") if l.strip()]
    else:
        # Single prose line — split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        lines = [s.strip() for s in sentences if s.strip()]

    # Filter out "no issues" variants (CX cycle 2)
    no_issue_patterns = ["no issues", "no contradictions", "none found", "all correct",
                         "no errors", "no problems", "nothing to fix"]
    lines = [l for l in lines
             if not any(p in l.lower() for p in no_issue_patterns)]

    if not lines:
        return []

    batches = []
    for i in range(0, len(lines), max_per_batch):
        batch = "\n".join(lines[i:i + max_per_batch])
        if batch:
            batches.append(batch)
    return batches


def _generate_cc_solution(task: dict, directives: str, condition: str = "cdsfl") -> str:
    """CC generates the initial solution using decomposed sequential steps.

    All conditions use 4-step decomposition: solve → attack → classify → revise.
    Revision is batched — issues are fed in groups of 5, each revision
    building on the previous, avoiding the monolithic prompt that caused
    timeouts on cross-domain tasks (ft-013).

    Bug fix (2026-03-22): replaces monolithic step 3 that concatenated
    task + solution + all issues into a single 20,000+ char prompt.
    """
    task_id = task["id"]
    _err(f"  [generate] CC generating solution for {task_id} [{condition}] ...")

    use_directives = directives if condition in ("cdsfl", "cdsfl_hil") else None

    # Step 1: Solve
    _err(f"  [generate/step1] solving ...")
    step1_prompt = _safe_format(DECOMPOSED_STEP1_SOLVE, task_prompt=task["prompt"])
    t0 = time.monotonic()
    solution = _call_cc(use_directives, step1_prompt)
    _err(f"  [generate/step1] done ({time.monotonic() - t0:.1f}s)")

    # Control and HIL: single-shot generation only. No self-falsification.
    # The P-pass (attack → classify → revise) IS the CDSFL methodology.
    # A real user under Control gets the first draft, not a revised one.
    if condition in ("control", "hil"):
        elapsed = time.monotonic() - t0
        _err(f"  [generate] CC solution complete ({elapsed:.1f}s total, 1 step — "
             f"{condition} has no self-falsification)")
        return solution

    # Step 2: Attack (CDSFL and CDSFL+HIL only)
    _err(f"  [generate/step2] self-falsifying ...")
    step2_prompt = _safe_format(
        DECOMPOSED_STEP2_ATTACK,
        task_prompt=task["prompt"],
        solution=solution,
    )
    t1 = time.monotonic()
    issues = _call_cc(use_directives, step2_prompt)
    _err(f"  [generate/step2] done ({time.monotonic() - t1:.1f}s)")

    # Step 3: Classify issues (small prompt — just the issues)
    _err(f"  [generate/step3] classifying issues ...")
    step3_prompt = _safe_format(DECOMPOSED_STEP3_CLASSIFY, issues=issues)
    t2 = time.monotonic()
    classified = _call_cc(use_directives, step3_prompt)
    _err(f"  [generate/step3] done ({time.monotonic() - t2:.1f}s)")

    # Step 4: Revise in batches — each batch is max 5 issues
    # Only the solution + current batch are in each prompt (no task, no full issues list)
    batches = _split_issues(classified)
    if not batches:
        _err(f"  [generate/step4] no actionable issues found — skipping revision")
        elapsed = time.monotonic() - t0
        _err(f"  [generate] CC solution complete ({elapsed:.1f}s total, 3 steps — no revision needed)")
        return solution
    _err(f"  [generate/step4] revising in {len(batches)} batch(es) ...")
    revised = solution
    for i, batch in enumerate(batches):
        _err(f"  [generate/step4/{i+1}] batch {i+1}/{len(batches)} ...")
        # CX P-pass: solution is source of truth — never truncate it.
        # Cap the issues batch to control total prompt size.
        batch_capped = batch
        batch_prompt = _safe_format(
            DECOMPOSED_STEP3_REVISE_BATCH,
            solution=revised,
            issues_batch=batch_capped,
        )
        # Hard cap: if the assembled prompt exceeds 20K, truncate batch and reassemble.
        # CX cycle 3: if batch is empty after truncation, skip this batch entirely.
        if len(batch_prompt) > 20000:
            excess = len(batch_prompt) - 20000
            batch_capped = batch[:max(0, len(batch) - excess - 100)]
            if not batch_capped.strip():
                _err(f"  [generate/step4/{i+1}] prompt {len(batch_prompt)} > 20K and "
                     f"no room for batch — skipping (deferred)")
                continue
            _err(f"  [generate/step4/{i+1}] prompt {len(batch_prompt)} > 20K — batch capped to {len(batch_capped)} chars")
            batch_prompt = _safe_format(
                DECOMPOSED_STEP3_REVISE_BATCH,
                solution=revised,
                issues_batch=batch_capped,
            )
        t3 = time.monotonic()
        candidate = _call_cc(use_directives, batch_prompt)
        _err(f"  [generate/step4/{i+1}] done ({time.monotonic() - t3:.1f}s)")

        # CX cycle 5: validate revised output before accepting.
        # Reject malformed tiny replies, refusals, or drastically oversized outputs.
        min_ratio = 0.3  # revised should be at least 30% of original length
        max_ratio = 3.0  # and at most 300%
        if len(candidate) < len(revised) * min_ratio:
            _err(f"  [generate/step4/{i+1}] WARNING: revised output suspiciously short "
                 f"({len(candidate)} vs {len(revised)}) — keeping previous version")
        elif len(candidate) > len(revised) * max_ratio:
            _err(f"  [generate/step4/{i+1}] WARNING: revised output suspiciously large "
                 f"({len(candidate)} vs {len(revised)}) — keeping previous version")
        else:
            revised = candidate

        # Per-chunk verification: check for cascading contradictions
        _err(f"  [generate/step4/{i+1}] checking for contradictions ...")
        # Include the revised content so CC can actually check it
        # Include enough of the revised solution for CC to check contradictions.
        # Use first 3000 + last 3000 to cover both ends without exceeding 8K.
        if len(revised) > 8000:
            check_context = revised[:3000] + "\n\n[...]\n\n" + revised[-3000:]
        else:
            check_context = revised
        check_prompt = (
            "You just revised a solution. Here is your revised version:\n\n"
            f"{check_context}\n\n"
            "Check: did your revision introduce any NEW contradictions, "
            "inconsistencies, or errors elsewhere in the solution?\n\n"
            "Reply with EXACTLY one of:\n"
            "STATUS: CLEAN\n"
            "STATUS: ISSUES\n[list each issue on its own line]\n\n"
            "Use STATUS: CLEAN only if you found zero new problems."
        )
        t4 = time.monotonic()
        check = _call_cc(use_directives, check_prompt)
        _err(f"  [generate/step4/{i+1}] check done ({time.monotonic() - t4:.1f}s)")

        # CX cycle 4: structured detection — look for STATUS: CLEAN/ISSUES
        check_clean = "status: clean" in check.lower() or "no contradiction" in check.lower()
        if not check_clean:
            # Contradiction detected — feed it as an additional issue in next batch
            _err(f"  [generate/step4/{i+1}] contradiction detected — "
                 f"adding to revision queue")
            if i + 1 < len(batches):
                batches[i + 1] += f"\n\nADDITIONAL (from prior batch check):\n{check}"
            else:
                # Last batch — do one more revision pass
                _err(f"  [generate/step4/fix] final contradiction fix ...")
                fix_prompt = _safe_format(
                    DECOMPOSED_STEP3_REVISE_BATCH,
                    solution=revised,
                    issues_batch=f"Fix these contradictions introduced by prior revision:\n{check}",
                )
                t5 = time.monotonic()
                revised = _call_cc(use_directives, fix_prompt)
                _err(f"  [generate/step4/fix] done ({time.monotonic() - t5:.1f}s)")

    elapsed = time.monotonic() - t0
    _err(f"  [generate] CC solution complete ({elapsed:.1f}s total, "
         f"{3 + len(batches)} steps)")

    return revised


# ---------------------------------------------------------------------------
# Main task runner
# ---------------------------------------------------------------------------


def run_task(
    task: dict,
    directives: str,
    ledger: CostLedger,
    existing_solution: str | None = None,
    output_dir: Path | None = None,
    checkpoint: "Checkpoint | None" = None,
    condition: str = "cdsfl",
    phase2: bool = False,
) -> dict:
    """Run the full round-robin protocol for one task under one condition.

    Returns the complete task result with verification chain.
    Per-round snapshots are saved via checkpoint for crash-safe resume.
    """
    task_id = task["id"]
    run_id = f"{task_id}/{condition}"
    _err(f"\n{'='*60}")
    _err(f"  TASK: {task_id} — {task.get('title', '(no title)')}")
    _err(f"  CONDITION: {condition.upper()}")
    _err(f"{'='*60}")

    chain = VerificationChain()

    # Load effective CDSFL policy for this task (base: no model-specific layer)
    task_domain = task.get("domain", "cross-domain")
    try:
        base_policy = load_effective_policy(domain=task_domain, task_id=task_id, model=None)
    except (FileNotFoundError, PolicyViolationError) as exc:
        _err(f"  [registry] WARNING: could not load base policy: {exc}")
        base_policy = {}

    # Apply policy-controlled overrides
    policy_max_rounds = base_policy.get("protocol", {}).get("max_rounds", MAX_ROUNDS)
    policy_sympy_timeout = base_policy.get("verification", {}).get("sympy_timeout_seconds", 10)

    _err(f"  [registry] base policy loaded for domain={task_domain}, task_id={task_id}")
    _err(f"  [registry] max_rounds={policy_max_rounds}, sympy_timeout={policy_sympy_timeout}s")

    # Load model-specific policies for each reviewer and log them
    model_policies: dict[str, dict] = {}
    for model_alias, registry_name in REGISTRY_MODEL_MAP.items():
        try:
            mp = load_effective_policy(domain=task_domain, task_id=task_id, model=registry_name)
            model_policies[model_alias] = mp
            model_timeout = mp.get("model", {}).get("timeout", "default")
            _err(f"  [registry] {model_alias} policy: timeout={model_timeout}s")
        except (FileNotFoundError, PolicyViolationError) as exc:
            _err(f"  [registry] WARNING: {model_alias} policy failed: {exc}")
            model_policies[model_alias] = base_policy

    # Set CC directive mode per condition.
    # Control/HIL: --bare with NO system prompt (level playing field).
    # CDSFL/CDSFL+HIL: --bare with methodology reference as system prompt.
    # This eliminates the directive asymmetry confound: CC no longer gets
    # CLAUDE.md advantages under Control/HIL, and all models get the same
    # methodology directives under CDSFL conditions.
    global _cc_bare_mode, _cc_system_prompt_file
    _cc_bare_mode = True  # always strip CLAUDE.md auto-loading
    if condition in ("cdsfl", "cdsfl_hil"):
        _cc_system_prompt_file = METHODOLOGY_FILE
        _err(f"  [directives] CC: --bare + methodology reference ({METHODOLOGY_FILE})")
    else:
        _cc_system_prompt_file = None
        _err(f"  [directives] CC: --bare only (no methodology directives — level playing field)")

    # CX P-pass fix (HARD 7): check cost cap BEFORE expensive generation
    if not ledger.check_cap():
        _err(f"  [cost] cap reached before generation — skipping task")
        return {
            "task_id": task_id,
            "condition": condition,
            "title": task.get("title", ""),
            "domain": task.get("domain", ""),
            "status": "COST_CAP",
            "rounds_completed": 0,
            "total_unique_hard_findings": 0,
            "rounds": [],
            "deferred_items": [],
            "verification_chain": chain.to_dict(),
            "chain_valid": True,
            "merkle_root": chain.merkle_root(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Step 1: Generate or reuse solution
    # Control and HIL conditions generate WITHOUT CDSFL directives
    if existing_solution:
        solution = existing_solution
        _err(f"  [generate] reusing frozen solution ({len(solution)} chars)")
    elif condition in ("cdsfl", "cdsfl_hil"):
        solution = _generate_cc_solution(task, directives, condition=condition)
        ledger.record("claude_cli", 0.0)
    else:
        # Control and HIL: raw generation, no CDSFL directives
        solution = _generate_cc_solution(task, "", condition=condition)
        ledger.record("claude_cli", 0.0)

    chain.record("solution", solution, {"task_id": task_id, "generator": "cc", "condition": condition})

    # Step 1b: Generate HIL expert guidance (if HIL or CDSFL_HIL condition)
    # This is a multi-step pipeline:
    #   (a) CC identifies what needs to be researched
    #   (b) Script performs external research (SymPy, arXiv, web search)
    #   (c) CC generates final guidance incorporating research results
    # This mirrors what a real domain expert does: they don't just know
    # things from memory — they look things up, verify, cross-reference.
    expert_guidance = ""
    if condition == "hil":
        # HIL: Iterative guidance — CC generates a new prompt each round
        # based on what models found in the previous round. Evidence-based
        # pattern from arXiv:2603.18740, arXiv:2405.01470, arXiv:2402.04568.
        # Round 1 guidance generated here; rounds 2-5 updated in the loop.
        _err(f"  [hil] Iterative HIL: generating round 1 guidance ...")
        t0 = time.monotonic()
        try:
            expert_guidance, leakage = _generate_iterative_hil_guidance(
                task, round_num=1, prev_findings=[],
            )
            elapsed = time.monotonic() - t0
            _err(f"  [hil] round 1 guidance done ({elapsed:.1f}s, {len(expert_guidance)} chars"
                 f"{', LEAKAGE' if leakage else ''})")
            chain.record("expert_guidance_r1", expert_guidance, {
                "task_id": task_id, "round": 1,
                "guidance_goal": "broad_context", "leakage": leakage,
            })
        except Exception as exc:
            _err(f"  [hil] expert guidance FAILED: {exc} — cannot run HIL without guidance")
            return {
                "task_id": task_id,
                "condition": condition,
                "title": task.get("title", ""),
                "domain": task.get("domain", ""),
                "status": "HIL_GUIDANCE_FAILED",
                "error": str(exc),
                "rounds_completed": 0,
                "total_unique_hard_findings": 0,
                "rounds": [],
                "deferred_items": [{"reason": "expert_guidance_failed", "error": str(exc)}],
                "verification_chain": chain.to_dict(),
                "chain_valid": True,
                "merkle_root": chain.merkle_root(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    elif condition == "cdsfl_hil":
        # CDSFL+HIL: Full research pipeline — the complete methodology.
        # CC identifies research needs, performs external research (SymPy,
        # arXiv, web), then generates guidance incorporating verified results.
        # This is the CDSFL methodology at full strength.
        _err(f"  [cdsfl_hil] Step 1: CC identifying research needs ...")
        t0 = time.monotonic()
        try:
            # Step (a): CC identifies what needs researching
            research_prompt = _safe_format(HIL_RESEARCH_PROMPT, task_prompt=task["prompt"])
            research_needs = _call_cc(None, research_prompt)
            elapsed_a = time.monotonic() - t0
            _err(f"  [cdsfl_hil] research needs identified ({elapsed_a:.1f}s, {len(research_needs)} chars)")
            chain.record("research_needs", research_needs, {"task_id": task_id})

            # Step (b): External research — SymPy, arXiv, web search
            _err(f"  [cdsfl_hil] Step 2: External research (SymPy, arXiv, web) ...")
            external_research = _do_external_research(task, research_needs, condition=condition)
            elapsed_b = time.monotonic() - t0
            _err(f"  [cdsfl_hil] external research done ({elapsed_b:.1f}s, {len(external_research)} chars)")

            # Step (c): CC generates final expert guidance WITH research results
            _err(f"  [cdsfl_hil] Step 3: CC generating expert guidance with research ...")
            guidance_prompt = _safe_format(
                HIL_EXPERT_GUIDANCE_PROMPT,
                task_prompt=task["prompt"],
            )
            # Append research results to the guidance prompt
            guidance_prompt += (
                f"\n\nEXTERNAL RESEARCH RESULTS (verified via SymPy computation and web search):\n"
                f"{external_research}\n\n"
                f"Incorporate these verified results into your guidance. Cite specific "
                f"theorems, bounds, and conditions from the research. Flag any claims "
                f"you cannot verify from these results."
            )
            expert_guidance = _call_cc(None, guidance_prompt)
            elapsed = time.monotonic() - t0
            _err(f"  [cdsfl_hil] expert guidance done ({elapsed:.1f}s total, {len(expert_guidance)} chars)")
            chain.record("external_research", external_research, {"task_id": task_id})
            chain.record("expert_guidance", expert_guidance, {"task_id": task_id})
        except Exception as exc:
            _err(f"  [cdsfl_hil] expert guidance FAILED: {exc} — cannot run CDSFL+HIL without guidance")
            return {
                "task_id": task_id,
                "condition": condition,
                "title": task.get("title", ""),
                "domain": task.get("domain", ""),
                "status": "HIL_GUIDANCE_FAILED",
                "error": str(exc),
                "rounds_completed": 0,
                "total_unique_hard_findings": 0,
                "rounds": [],
                "deferred_items": [{"reason": "expert_guidance_failed", "error": str(exc)}],
                "verification_chain": chain.to_dict(),
                "chain_valid": True,
                "merkle_root": chain.merkle_root(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    # Step 2: Run rounds
    rounds: list[dict] = []
    all_known_keys: set[str] = set()
    consecutive_zero_novel = 0
    status = "DEFERRED"  # default if we exhaust all rounds
    deferred_items: list[dict] = []

    # Set CC policy timeout for _call_cc_inner (Finding 1 fix: registry-sourced timeouts)
    global _cc_policy_timeout
    _cc_policy_timeout = model_policies.get("cc", {}).get("model", {}).get("timeout")

    # Phase 2: create persistent conversations for ALL 5 reviewers.
    # Each reviewer maintains context across all rounds of this task.
    # Timeouts are sourced from registry model policies (Finding 1 fix).
    # Fallback to class-level defaults when policy is absent.
    deepseek_chat = None
    cx_chat = None
    gemini_chat = None
    chatgpt_chat = None
    cc_chat = None  # CC reviews via claude -p (stateless but decomposed)
    if phase2:
        _err(f"  [phase2] creating persistent conversations for 5 reviewers")
        ds_timeout = model_policies.get("deepseek", {}).get("model", {}).get("timeout")
        cx_timeout = model_policies.get("cx", {}).get("model", {}).get("timeout")
        gm_timeout = model_policies.get("gemini", {}).get("model", {}).get("timeout")
        cg_timeout = model_policies.get("chatgpt", {}).get("model", {}).get("timeout")

        # Load methodology directives for CDSFL conditions.
        # Control/HIL: no directives (level playing field).
        # CDSFL/CDSFL+HIL: all models get identical methodology reference.
        methodology_text = None
        if condition in ("cdsfl", "cdsfl_hil"):
            try:
                methodology_text = Path(METHODOLOGY_FILE).read_text().strip()
                _err(f"  [directives] Methodology loaded ({len(methodology_text)} chars) for all models")
            except FileNotFoundError:
                _err(f"  [directives] WARNING: {METHODOLOGY_FILE} not found — no methodology injection")
        else:
            _err(f"  [directives] No methodology injection ({condition} — level playing field)")

        # System-level injection where supported (DeepSeek, Gemini — true system prompt).
        # Context-level for CX and ChatGPT (prepended to first message — weaker persistence,
        # documented as platform limitation, not a design choice).
        deepseek_chat = DeepSeekReviewChat(timeout=ds_timeout, system_prompt=methodology_text)
        gemini_chat = GeminiReviewChat(timeout=gm_timeout, system_prompt=methodology_text)
        # CX and ChatGPT: inject methodology as context prefix (best available mechanism)
        cx_system = methodology_text if methodology_text else None
        cx_chat = CXReviewChat(task_id, timeout=cx_timeout, system_prompt=cx_system)
        chatgpt_chat = ChatGPTReviewChat(task_id, timeout=cg_timeout, system_prompt=cx_system)
        # CC (Opus) reviews are handled via _call_cc in the blind/confer functions
        # — it uses claude -p which is stateless, but findings accumulate in the protocol

    effective_max_rounds = policy_max_rounds if base_policy else MAX_ROUNDS
    for round_num in range(1, effective_max_rounds + 1):
        if not ledger.check_cap():
            _err(f"  [cost] cap reached — stopping at round {round_num}")
            status = "COST_CAP"
            break

        # Budget exhaustion no longer interrupts mid-task. Once a task starts,
        # it runs to completion. Budget is checked at task/condition boundaries only.

        if round_num == 1:
            # Blind round — all 5 reviewers independently
            round_data = _run_blind_round(task, solution, chain, ledger,
                                          condition=condition, expert_guidance=expert_guidance,
                                          deepseek_chat=deepseek_chat, cx_chat=cx_chat,
                                          gemini_chat=gemini_chat, chatgpt_chat=chatgpt_chat)

            # Control and HIL: no cross-model confer (CDSFL-exclusive).
            # But models DO get 5 rounds of independent self-iteration —
            # simulating a user saying "look again, anything else?" to the
            # same model. Each model is re-prompted with its OWN prior findings
            # only. No model sees any other model's work.
            # This gives comparable 5-point decay curves while accurately
            # modelling real-world usage. Founder directive, 2026-03-24.
        elif condition in ("control", "hil"):
            # Self-iteration round — each model sees only its OWN prior findings
            _err(f"  [round {round_num}/self-iterate] {condition}: each model re-examining independently ...")
            prev_round = rounds[-1]

            # Iterative HIL: update guidance each round based on previous findings
            if condition == "hil" and round_num <= len(ITERATIVE_HIL_ROUND_GOALS):
                prev_findings = _summarise_round_findings(prev_round)
                _err(f"  [hil] Iterative HIL: generating round {round_num} guidance ...")
                try:
                    expert_guidance, leakage = _generate_iterative_hil_guidance(
                        task, round_num=round_num, prev_findings=prev_findings,
                    )
                    _err(f"  [hil] round {round_num} guidance: {len(expert_guidance)} chars, "
                         f"goal={ITERATIVE_HIL_ROUND_GOALS.get(round_num, {}).get('goal', '?')}"
                         f"{', LEAKAGE' if leakage else ''}")
                    chain.record(f"expert_guidance_r{round_num}", expert_guidance, {
                        "task_id": task_id, "round": round_num,
                        "guidance_goal": ITERATIVE_HIL_ROUND_GOALS.get(round_num, {}).get("goal", ""),
                        "leakage": leakage,
                    })
                except Exception as exc:
                    _err(f"  [hil] round {round_num} guidance failed: {exc} — using previous")

            round_data = _run_self_iteration_round(
                task, solution, chain, ledger, round_num,
                prev_round=prev_round, condition=condition,
                expert_guidance=expert_guidance,
                deepseek_chat=deepseek_chat, cx_chat=cx_chat,
                gemini_chat=gemini_chat, chatgpt_chat=chatgpt_chat,
            )
        else:
            # Confer round — each sees the OTHER FOUR's previous findings
            prev_round = rounds[-1]

            # Finding 2 fix: iterative HIL guidance for CDSFL+HIL confer rounds.
            # Round 1 guidance was research-based (full pipeline). Rounds 2-5 get
            # iterative follow-up guidance based on confer findings, same pattern
            # as plain HIL but applied to the CDSFL+HIL condition.
            if condition == "cdsfl_hil" and round_num <= len(ITERATIVE_HIL_ROUND_GOALS):
                prev_findings = _summarise_round_findings(prev_round)
                _err(f"  [cdsfl_hil] Iterative guidance: generating round {round_num} follow-up ...")
                try:
                    iterative_guidance, leakage = _generate_iterative_hil_guidance(
                        task, round_num=round_num, prev_findings=prev_findings,
                    )
                    # CX Turn 1 C2 fix: cap base, keep all follow-ups (they're small).
                    # Split on first FOLLOW-UP marker to get base only.
                    base_only = expert_guidance.split("\n\nFOLLOW-UP")[0]
                    base_cap = 3000 if round_num >= 2 else len(base_only)
                    capped_base = base_only[:base_cap]
                    if len(base_only) > base_cap:
                        capped_base += "\n[base guidance truncated]"
                    # Append ONLY the new follow-up (older ones are in the chain record)
                    expert_guidance = (
                        capped_base
                        + f"\n\nFOLLOW-UP (round {round_num}):\n"
                        + iterative_guidance
                    )
                    _err(f"  [cdsfl_hil] round {round_num} guidance: {len(iterative_guidance)} chars, "
                         f"goal={ITERATIVE_HIL_ROUND_GOALS.get(round_num, {}).get('goal', '?')}"
                         f"{', LEAKAGE' if leakage else ''}")
                    chain.record(f"expert_guidance_r{round_num}", iterative_guidance, {
                        "task_id": task_id, "round": round_num,
                        "guidance_goal": ITERATIVE_HIL_ROUND_GOALS.get(round_num, {}).get("goal", ""),
                        "leakage": leakage, "condition": "cdsfl_hil",
                    })
                except Exception as exc:
                    _err(f"  [cdsfl_hil] round {round_num} guidance failed: {exc} — using previous")

            if prev_round["round_type"] == "blind":
                cc_prev = prev_round.get("cc", {}).get("findings", [])
                deepseek_prev = prev_round.get("deepseek", {}).get("findings", [])
                cx_prev = prev_round.get("cx", {}).get("findings", [])
                gemini_prev = prev_round.get("gemini", {}).get("findings", [])
                chatgpt_prev = prev_round.get("chatgpt", {}).get("findings", [])
            else:
                cc_prev = prev_round.get("cc", {}).get("confer_response", {}).get("new_findings", [])
                deepseek_prev = prev_round.get("deepseek", {}).get("confer_response", {}).get("new_findings", [])
                cx_prev = prev_round.get("cx", {}).get("confer_response", {}).get("new_findings", [])
                gemini_prev = prev_round.get("gemini", {}).get("confer_response", {}).get("new_findings", [])
                chatgpt_prev = prev_round.get("chatgpt", {}).get("confer_response", {}).get("new_findings", [])

            round_data = _run_confer_round(
                task, solution, round_num,
                cc_prev, deepseek_prev, cx_prev, gemini_prev, chatgpt_prev,
                chain, ledger,
                output_dir=output_dir,
                condition=condition,
                expert_guidance=expert_guidance,
                deepseek_chat=deepseek_chat,
                cx_chat=cx_chat,
                gemini_chat=gemini_chat,
                chatgpt_chat=chatgpt_chat,
            )

        rounds.append(round_data)

        # Per-round checkpoint snapshot (bug fix 2026-03-21)
        if checkpoint:
            in_progress = {
                "task_id": task_id,
                "status": "IN_PROGRESS",
                "rounds_completed": len(rounds),
                "total_unique_hard_findings": len(all_known_keys),
                "last_round": round_num,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            checkpoint.save(f"{task_id}__in_progress", in_progress)

        # Defer on ANY reviewer failure — breaks the five-way topology.
        reviewer_errors = {
            r: round_data.get(r, {}).get("error") for r in REVIEWERS
        }
        failed = [r.upper() for r, err in reviewer_errors.items() if err]
        if failed:
            _err(f"  [round {round_num}] reviewer(s) failed: {', '.join(failed)} — deferring")
            deferred_items.append({
                "round": round_num,
                "reason": "reviewer_failed",
                "failed_reviewers": failed,
                **{f"{r}_error": reviewer_errors[r] for r in REVIEWERS},
            })
            # HARD STOP: any model failure halts the entire bench run.
            # Graceful degradation is useful in production but not during
            # controlled experiments where all 5 models must participate.
            status = "DEFERRED_INFRA"
            _err(f"\n  [HARD STOP] Model failure detected. Halting bench run.")
            _err(f"  Failed reviewers: {failed}")
            _err(f"  Fix the issue and resume with --resume flag.")
            _err(f"  Completed runs are checkpointed and will not re-run.")
            # Save checkpoint before exit
            break

        # Novelty assessment
        novel_count, new_keys = _count_novel_hard_findings(round_data, all_known_keys, task_id)
        all_known_keys.update(new_keys)
        _err(f"  [round {round_num}] novel HARD findings: {novel_count} (total unique: {len(all_known_keys)})")

        if novel_count == 0:
            consecutive_zero_novel += 1
        else:
            consecutive_zero_novel = 0

        # SymPy verification scoring — runs on ALL conditions as MEASUREMENT.
        # Feedback to models is CDSFL-exclusive (confer path).
        # Gate removed from call site on 2026-03-24 (was incorrectly restricting
        # verification to CDSFL only, preventing cross-condition quality comparison).
        round_verification = {"scores": [], "aggregate": 0.0, "determinate_count": 0, "details": []}
        if True:  # universal measurement — all conditions
            # Extract findings from ALL reviewers in both blind and confer round structures
            # Blind rounds: findings under "findings" key
            # Confer rounds: new findings under "confer_response.new_findings"
            all_round_findings = []
            for r in REVIEWERS:
                r_data = round_data.get(r, {})
                # Collect from all round types: blind, self-iterate, and confer
                # Tag each finding with source_model for verification-to-classification mapping
                for f in r_data.get("findings", []):
                    if isinstance(f, dict):
                        f["_source_model"] = r
                    all_round_findings.append(f)
                if round_data.get("round_type") == "confer":
                    for f in r_data.get("confer_response", {}).get("new_findings", []):
                        if isinstance(f, dict):
                            f["_source_model"] = r
                        all_round_findings.append(f)
            # Verify only the findings (all are novel by this point — dedup already happened)
            round_verification = _verify_findings(all_round_findings, condition,
                                                    sympy_timeout=policy_sympy_timeout)
            round_data["verification"] = round_verification
            if round_verification["determinate_count"] > 0:
                _err(f"  [verify] {round_verification['determinate_count']} claims verified, "
                     f"aggregate score: {round_verification['aggregate']}")
            chain.record("verification", json.dumps(round_verification),
                         {"task_id": task_id, "round": round_num})

            # Classify findings using CX refinements (independence, canonicalisation, novelty)
            round_classifications = _classify_round_findings(round_data, round_verification)
            round_data["classifications"] = round_classifications
            support_counts = {}
            for cls in round_classifications.values():
                sc = cls["support_class"]
                support_counts[sc] = support_counts.get(sc, 0) + 1
            if support_counts:
                _err(f"  [classify] {support_counts}")

        # Pre-registered stop rule: 2 consecutive rounds with 0 novel HARD + all three concur
        if round_num >= 2 and consecutive_zero_novel >= 2:
            if round_data["round_type"] == "confer" and _all_concur_stop(round_data, consecutive_zero_novel):
                # Check for asymmetric override (CDSFL only: prevent premature stop)
                if _should_override_stop(round_verification):
                    _err(f"  [verify/override] counting says stop but verification score "
                         f"{round_verification['aggregate']:.2f} >= {VERIFY_CONTINUE_THRESHOLD} "
                         f"with {round_verification['determinate_count']} verified claims "
                         f"— continuing one more round")
                else:
                    _err(f"  [stop] pre-registered stop rule met at round {round_num}: "
                         f"2+ consecutive zero-novel-HARD + all five concur")
                    status = "RESOLVED"
                    break
            elif round_data["round_type"] == "confer":
                _err(f"  [stop] 2+ consecutive zero-novel-HARD but no concurrence — "
                     f"recording disagreement")
                deferred_items.append({
                    "round": round_num,
                    "reason": "no_concurrence_on_stop",
                    **{f"{r}_concur": round_data.get(r, {}).get("confer_response", {}).get("concur_stop")
                       for r in REVIEWERS},
                })

        # CC arbiter assessment — bounded Claude CLI call (non-fatal on timeout)
        if round_num < effective_max_rounds:
            _err(f"  [arbiter] CC assessing — round {round_num} complete, "
                 f"consecutive_zero_novel={consecutive_zero_novel}")
            try:
                arbiter_timeout = _budget.clamp_timeout(CC_ARBITER_TIMEOUT) if _budget else CC_ARBITER_TIMEOUT
                arbiter_prompt = (
                    f"You are the CC arbiter in a CDSFL round-robin test. "
                    f"Task: {task_id}. Round {round_num} of {effective_max_rounds} complete. "
                    f"Total unique HARD findings so far: {len(all_known_keys)}. "
                    f"Novel HARD findings this round: {novel_count}. "
                    f"Consecutive zero-novel rounds: {consecutive_zero_novel}. "
                    f"Assess: should the next round proceed or are diminishing returns reached? "
                    f"Reply in one sentence."
                )
                arbiter_response = _call_cli(
                    [CLAUDE_CLI or "claude", "-p", "--model", "claude-opus-4-6", "--output-format", "text"],
                    input_text=arbiter_prompt,
                    timeout=arbiter_timeout,
                    label="cc_arbiter",
                )
                _err(f"  [arbiter] assessment: {arbiter_response[:200]}")
            except Exception as exc:
                _err(f"  [arbiter] assessment failed (non-fatal): {str(exc)[:80]}")

    # Finalise verification chain
    chain_valid, chain_msg = chain.verify_chain()
    merkle = chain.merkle_root()
    _err(f"  [chain] verification: {chain_msg}")
    _err(f"  [chain] Merkle root: {merkle[:16]}...")

    # Build result
    result = {
        "task_id": task_id,
        "condition": condition,
        "title": task.get("title", ""),
        "domain": task.get("domain", ""),
        "status": status,
        "rounds_completed": len(rounds),
        "total_unique_hard_findings": len(all_known_keys),
        "rounds": rounds,
        "deferred_items": deferred_items,
        "verification_chain": chain.to_dict(),
        "chain_valid": chain_valid,
        "merkle_root": merkle,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "effective_policy": {
            "max_rounds": effective_max_rounds,
            "sympy_timeout": policy_sympy_timeout,
            "convergence_method": base_policy.get("convergence", {}).get("method", ""),
            "hard_veto": base_policy.get("convergence", {}).get("hard_veto", True),
            "anti_deference": base_policy.get("constraints", {}).get("anti_deference", True),
        },
    }

    return result


# ---------------------------------------------------------------------------
# Aggregate analysis
# ---------------------------------------------------------------------------


def compute_biodiversity_metrics(results: list[dict]) -> dict:
    """Compute biodiversity hypothesis metrics across all tasks and conditions.

    Key metric: proportion of unique findings found by only one
    architecture (novel) vs found by multiple (corroborated).
    Per-condition breakdown enables 2×2 factorial comparison
    (control vs HIL vs CDSFL vs CDSFL+HIL).
    """
    total_unique = 0
    total_rounds = 0
    tasks_resolved = 0
    tasks_deferred = 0

    per_condition: dict[str, dict] = {}
    for cond in ALL_CONDITIONS:
        per_condition[cond] = {"runs": 0, "resolved": 0, "unique_hard": 0, "total_rounds": 0}

    for r in results:
        total_unique += r.get("total_unique_hard_findings", 0)
        total_rounds += r.get("rounds_completed", 0)
        if r.get("status") == "RESOLVED":
            tasks_resolved += 1
        elif r.get("status", "").startswith("DEFERRED"):
            tasks_deferred += 1

        cond = r.get("condition", "unknown")
        if cond in per_condition:
            per_condition[cond]["runs"] += 1
            per_condition[cond]["unique_hard"] += r.get("total_unique_hard_findings", 0)
            per_condition[cond]["total_rounds"] += r.get("rounds_completed", 0)
            if r.get("status") == "RESOLVED":
                per_condition[cond]["resolved"] += 1

    # Compute per-condition averages
    for cond in per_condition:
        n = max(per_condition[cond]["runs"], 1)
        per_condition[cond]["avg_unique_hard"] = round(per_condition[cond]["unique_hard"] / n, 2)
        per_condition[cond]["avg_rounds"] = round(per_condition[cond]["total_rounds"] / n, 2)

    return {
        "total_runs": len(results),
        "tasks_resolved": tasks_resolved,
        "tasks_deferred": tasks_deferred,
        "total_unique_hard_findings": total_unique,
        "total_rounds": total_rounds,
        "avg_rounds_per_run": round(total_rounds / max(len(results), 1), 2),
        "avg_unique_hard_per_run": round(total_unique / max(len(results), 1), 2),
        "per_condition": per_condition,
    }


# ---------------------------------------------------------------------------
# Deferred items file
# ---------------------------------------------------------------------------


def save_deferred_items(results: list[dict], output_dir: Path) -> Path:
    """Save all deferred items to a single file for founder review."""
    deferred_path = output_dir / "deferred_items.json"
    all_deferred: list[dict] = []
    for r in results:
        task_deferred = r.get("deferred_items", [])
        if task_deferred:
            all_deferred.append({
                "task_id": r["task_id"],
                "status": r["status"],
                "items": task_deferred,
            })
    _atomic_write(deferred_path, json.dumps(all_deferred, indent=2) + "\n")
    return deferred_path


# ---------------------------------------------------------------------------
# Log tee — write all _err output to both stderr and a log file
# ---------------------------------------------------------------------------


class _TeeWriter:
    """Write to both stderr and a log file simultaneously."""

    def __init__(self, log_file):
        self._stderr = sys.__stderr__
        self._log = log_file

    def write(self, msg):
        self._stderr.write(msg)
        self._log.write(msg)
        self._log.flush()

    def flush(self):
        self._stderr.flush()
        self._log.flush()


def _setup_log_tee(log_path: Path) -> None:
    """Redirect stderr to both terminal and a log file."""
    log_file = open(log_path, "a", buffering=1)  # line-buffered
    sys.stderr = _TeeWriter(log_file)
    _err(f"[log] writing to {log_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Round-robin distributed compute test (Experiment 4).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--smoke", action="store_true",
        help=f"Smoke test: run {len(SMOKE_TASK_IDS)} tasks only ({', '.join(SMOKE_TASK_IDS)})",
    )
    parser.add_argument(
        "--cost-cap", type=float, default=100.0,
        help="Hard cost cap in USD (default: $100)",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from checkpoint (validates manifest compatibility)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate tasks and configuration only — no API calls",
    )
    parser.add_argument(
        "--tasks-dir", type=str, default=None,
        help="Path to frontier tasks directory",
    )
    parser.add_argument(
        "--directives", type=str, default=None,
        help="Path to CDSFL directives file (default: built-in)",
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Output directory for results (default: bench/results/round_robin/)",
    )
    parser.add_argument(
        "--log-file", type=str, default=None,
        help="Write all activity to a log file (in addition to stderr). "
             "Auto-generated if not specified.",
    )
    parser.add_argument(
        "--max-runtime", type=int, default=None,
        help="Global deadline budget in seconds (default: unlimited — runs until complete)",
    )
    parser.add_argument(
        "--condition", type=str, default=None,
        choices=ALL_CONDITIONS,
        help="Run a single condition only (default: all four)",
    )
    parser.add_argument(
        "--phase2", action="store_true",
        help="Phase 2: persistent-conversation delivery mechanism. "
             "Each reviewer maintains context across all rounds of a task.",
    )
    parser.add_argument(
        "--tasks", type=str, default=None,
        help="Comma-separated task IDs for smoke test (e.g. ft-001,ft-006,ft-013). "
             "Overrides default smoke task selection.",
    )
    parser.add_argument(
        "--max-rounds", type=int, default=None,
        help="Override MAX_ROUNDS (default: 5). Use --max-rounds 1 for wiring smoke tests.",
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Run CDSFL registry policy validation and exit (no experiment run).",
    )
    # NOTE: close any active Claude Code session before running.
    # claude -p subprocess calls fail if CC is already running.

    args = parser.parse_args()

    # Override MAX_ROUNDS if specified
    global MAX_ROUNDS
    if args.max_rounds is not None:
        MAX_ROUNDS = args.max_rounds
        print(f"[config] MAX_ROUNDS overridden to {MAX_ROUNDS}", file=sys.stderr, flush=True)

    # --validate-only: run registry validation and exit
    if args.validate_only:
        print("=" * 60, file=sys.stderr)
        print("CDSFL Registry — Policy Validation (pre-flight)", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        results = validate_all_policies()
        all_ok = True
        for name, status in results.items():
            indicator = "PASS" if status == "ok" else "FAIL"
            if status != "ok":
                all_ok = False
            print(f"  [{indicator}] {name}", file=sys.stderr)
            if status != "ok":
                for line in status.split("\n"):
                    print(f"         {line}", file=sys.stderr)
        if all_ok:
            print("\nAll CDSFL registry policies valid.", file=sys.stderr)
            sys.exit(0)
        else:
            print("\nVALIDATION FAILED — fix the above before running experiments.", file=sys.stderr)
            sys.exit(1)

    # Pre-flight: validate all CDSFL registry policies before any experiment run
    _preflight_results = validate_all_policies()
    _preflight_failures = {k: v for k, v in _preflight_results.items() if v != "ok"}
    if _preflight_failures:
        print("CDSFL Registry pre-flight FAILED:", file=sys.stderr, flush=True)
        for name, err in _preflight_failures.items():
            print(f"  [{name}] {err}", file=sys.stderr, flush=True)
        sys.exit(1)
    print(f"[registry] pre-flight: {len(_preflight_results)} policies validated OK",
          file=sys.stderr, flush=True)

    # Set up log file — always enabled (auto-generate if not specified)
    if args.log_file:
        log_path = Path(args.log_file)
    else:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        mode = "smoke" if args.smoke else "full"
        phase = "phase2" if args.phase2 else "phase1"
        log_path = LOGS_DIR / f"round_robin_{phase}_{mode}_{timestamp}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    _setup_log_tee(log_path)
    _err(f"[log] activity log: {log_path}")

    # Set up global deadline budget
    # Default: no deadline — all runs (smoke and full) run until complete or killed.
    # Use --max-runtime to impose a limit if needed.
    global _budget
    if args.max_runtime:
        max_runtime = args.max_runtime
    else:
        max_runtime = 0  # no deadline — runs until complete or killed
    if max_runtime > 0:
        _budget = DeadlineBudget(max_runtime)
        _err(f"[budget] deadline: {max_runtime}s ({max_runtime // 60}m)")
    else:
        _budget = None
        _err("[budget] no deadline — runs until complete")

    # Load directives
    directives = load_directives(args.directives)
    directives_hash = _content_hash(directives)[:16]

    # Load tasks
    tasks_dir = Path(args.tasks_dir) if args.tasks_dir else TASKS_DIR
    _err(f"Loading frontier tasks from {tasks_dir} ...")
    tasks = load_tasks(tasks_dir)
    if not tasks:
        _err("No task files found.")
        sys.exit(1)

    # Validate
    all_errors = []
    for task in tasks:
        all_errors.extend(validate_frontier_task(task))
    if all_errors:
        _err("Validation errors:")
        for err in all_errors:
            _err(f"  - {err}")
        sys.exit(1)
    _err(f"Loaded and validated {len(tasks)} task(s).")

    # Filter for smoke test
    if args.smoke:
        if args.tasks:
            smoke_ids = [t.strip() for t in args.tasks.split(",")]
        elif args.phase2:
            smoke_ids = SMOKE_TASK_IDS_PHASE2
        else:
            smoke_ids = SMOKE_TASK_IDS
        tasks = [t for t in tasks if t["id"] in smoke_ids]
        _err(f"Smoke test: {len(tasks)} task(s) selected ({', '.join(t['id'] for t in tasks)})")
        if not tasks:
            _err(f"ERROR: smoke task IDs {smoke_ids} not found in {tasks_dir}")
            sys.exit(1)

    # Output directory — Phase 2 uses separate results dir
    if args.output_dir:
        output_dir = Path(args.output_dir)
    elif args.phase2:
        output_dir = RESULTS_DIR_PHASE2
    else:
        output_dir = RESULTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dry run
    if args.dry_run:
        _err(f"\nDry run summary:")
        _err(f"  Tasks:      {len(tasks)}")
        _err(f"  Max rounds: {MAX_ROUNDS}")
        _err(f"  Cost cap:   ${args.cost_cap:.2f}")
        _err(f"  Output:     {output_dir}")
        _err(f"  Directives: {'custom' if args.directives else 'built-in'} ({directives_hash})")
        if args.phase2:
            _err(f"  Models:     CC (claude CLI, Opus 4.6), DeepSeek V3.2 (API), CX (codex CLI, GPT-5.3)")
        else:
            _err(f"  Models:     CC (claude CLI, Opus 4.6), DeepSeek V3.2 (API), CX (codex CLI, GPT-5.3)")

        # Validate environment — required CLIs must be available
        env_ok = True
        required_clis = {"claude": CLAUDE_CLI or "claude", "codex": "codex"}
        for cli_name, cli_path in required_clis.items():
            try:
                sp.run([cli_path, "--version"], capture_output=True, timeout=10)
            except (FileNotFoundError, sp.TimeoutExpired):
                _err(f"  WARNING: {cli_name} CLI not found or not responding")
                env_ok = False
        # Validate DeepSeek API key
        if not os.environ.get("DEEPSEEK_API_KEY"):
            _err(f"  WARNING: DEEPSEEK_API_KEY not set")
            env_ok = False
        else:
            _err(f"  DeepSeek API: key present")

        if env_ok:
            _err("  Environment: OK")
        sys.exit(0)

    # Validate environment (non-dry-run) — required CLIs must be available
    required_clis = {"claude": CLAUDE_CLI or "claude", "codex": "codex"}
    for cli_name, cli_path in required_clis.items():
        try:
            sp.run([cli_path, "--version"], capture_output=True, timeout=10)
        except (FileNotFoundError, sp.TimeoutExpired):
            _err(f"ERROR: {cli_name} CLI not found or not responding")
            sys.exit(1)
    if not os.environ.get("DEEPSEEK_API_KEY"):
        _err("ERROR: DEEPSEEK_API_KEY not set")
        sys.exit(1)

    # Startup: DeepSeek uses API — no process cleanup needed
    _err("[startup] DeepSeek uses API — no process cleanup needed")

    # Freeze corpus
    corpus_dir = output_dir / "frozen_corpus"
    task_ids = [t["id"] for t in tasks]
    corpus_manifest = freeze_corpus(tasks, corpus_dir)
    _err(f"Corpus frozen: {corpus_manifest['task_count']} tasks, hash: {corpus_manifest['corpus_hash'][:16]}")

    # Manifest and checkpoint (CX HARD fix 6: corpus_hash in manifest)
    manifest = _compute_manifest(task_ids, directives_hash, corpus_manifest["corpus_hash"])
    checkpoint_path = output_dir / "checkpoint.json"
    ledger_path = output_dir / "cost_ledger.json"

    checkpoint = Checkpoint(checkpoint_path, manifest)
    ledger = CostLedger(cap_usd=args.cost_cap, ledger_path=ledger_path)

    if args.resume:
        if not checkpoint.load():
            _err("Cannot resume: manifest incompatible. Use fresh run (no --resume).")
            sys.exit(1)
        ledger.load_existing()
        _err(f"Resumed. {ledger.summary()}")
    else:
        # Fresh run: clear any existing checkpoint
        if checkpoint_path.exists():
            checkpoint_path.unlink()
        if ledger_path.exists():
            ledger_path.unlink()

    # Determine conditions to run
    conditions = (args.condition,) if args.condition else ALL_CONDITIONS
    total_runs = len(tasks) * len(conditions)
    _err(f"Running {len(tasks)} task(s) × {len(conditions)} condition(s) = {total_runs} runs")

    # Run tasks × conditions
    results: list[dict] = []
    completed = 0
    skipped = 0
    deepseek_stopped = False  # if True, DeepSeek exhausted — test halted

    run_idx = 0
    for task in tasks:
        task_id = task["id"]

        for condition in conditions:
            run_idx += 1
            run_key = f"{task_id}/{condition}"

            # Skip if already completed (resume)
            if run_key in checkpoint.completed:
                results.append(checkpoint.completed[run_key])
                skipped += 1
                _err(f"[{run_idx}/{total_runs}] {run_key} — skipped (already completed)")
                continue

            if not ledger.check_cap():
                _err(f"[{run_idx}/{total_runs}] {run_key} — skipped (cost cap reached)")
                deepseek_stopped = True  # use as general halt flag
                break

            if _budget and _budget.exhausted():
                _err(f"[{run_idx}/{total_runs}] {run_key} — skipped (deadline budget exhausted)")
                _err(f"  [budget] {_budget.summary()}")
                deepseek_stopped = True
                break

            _err(f"[{run_idx}/{total_runs}] {run_key}")
            _err(f"  [budget] {_budget.summary()}" if _budget else "")
            try:
                result = run_task(
                    task, directives, ledger,
                    output_dir=output_dir, checkpoint=checkpoint,
                    condition=condition,
                    phase2=args.phase2,
                )
                results.append(result)
                # Clean up in-progress snapshot, save final result
                checkpoint.completed.pop(f"{task_id}__in_progress", None)
                checkpoint.save(run_key, result)
                completed += 1

                # Save per-run result
                run_result_path = output_dir / f"{task_id}_{condition}_result.json"
                _atomic_write(run_result_path, json.dumps(result, indent=2) + "\n")

                _err(f"  [{run_key}] {result['status']} — {result['rounds_completed']} rounds, "
                     f"{result['total_unique_hard_findings']} unique HARD findings")
                _err(f"  {ledger.summary()}")

                # HARD STOP on infra failure — all 5 models must participate
                if result.get("status") == "DEFERRED_INFRA":
                    _err(f"\n{'='*60}")
                    _err(f"  BENCH RUN HALTED — model failure on {run_key}")
                    _err(f"  Fix the issue and resume with: --resume")
                    _err(f"  {completed} runs completed, {len(tasks) * len(conditions) - completed} remaining")
                    _err(f"{'='*60}")
                    sys.exit(1)

            except DeepSeekExhausted as exc:
                _err(f"  [{run_key}] DEEPSEEK EXHAUSTED — stopping test for diagnosis")
                prompt_size = getattr(exc, 'prompt_size', 0) or len(str(exc))
                error_result = {
                    "task_id": task_id,
                    "condition": condition,
                    "status": "DEEPSEEK_EXHAUSTED",
                    "error": str(exc),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                results.append(error_result)
                checkpoint.save(f"{run_key}__deepseek_diag", error_result)
                diag_path = output_dir / f"{task_id}_{condition}_deepseek_diagnostic.json"
                _atomic_write(diag_path, json.dumps(error_result, indent=2) + "\n")
                _err(f"  [DIAG] saved to {diag_path}")
                deepseek_stopped = True
                break

            except Exception as exc:
                _err(f"  [{run_key}] FATAL ERROR: {exc}")
                error_result = {
                    "task_id": task_id,
                    "condition": condition,
                    "status": "FATAL_ERROR",
                    "error": str(exc),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                results.append(error_result)
                checkpoint.save(run_key, error_result)

        if deepseek_stopped:
            _err("[HALT] Test halted — see diagnostic output above")
            break

    # Summary
    _err(f"\n{'='*60}")
    _err(f"  ROUND-ROBIN COMPLETE")
    _err(f"{'='*60}")
    _err(f"  Completed: {completed}, Skipped (resumed): {skipped}")
    _err(f"  {ledger.summary()}")

    # Compute metrics
    metrics = compute_biodiversity_metrics(results)
    _err(f"  Resolved: {metrics['tasks_resolved']}/{metrics['total_runs']}")
    _err(f"  Deferred: {metrics['tasks_deferred']}/{metrics['total_runs']}")
    _err(f"  Total unique HARD findings: {metrics['total_unique_hard_findings']}")
    _err(f"  Avg rounds/run: {metrics['avg_rounds_per_run']}")
    for cond, cdata in metrics.get("per_condition", {}).items():
        if cdata["runs"] > 0:
            _err(f"  [{cond.upper()}] {cdata['runs']} runs, "
                 f"{cdata['unique_hard']} HARD findings (avg {cdata['avg_unique_hard']}), "
                 f"avg {cdata['avg_rounds']} rounds")

    # Save aggregate results
    aggregate = {
        "experiment": "round_robin",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "phase": "phase2" if args.phase2 else "phase1",
            "delivery_mechanism": "persistent_conversation" if args.phase2 else "stateless",
            "max_rounds": MAX_ROUNDS,
            "cost_cap_usd": args.cost_cap,
            "directives_hash": directives_hash,
            "corpus_hash": corpus_manifest["corpus_hash"],
            "models": {
                "orchestrator": "claude-cli/opus-4.6",
                "falsifier_1": "deepseek-api/deepseek-v3.2",
                "falsifier_2": "codex-cli/gpt-5.3-codex",
            },
        },
        "metrics": metrics,
        "results": results,
        "cost_ledger": {
            "total_usd": round(ledger.total, 4),
            "by_provider": {k: round(v, 4) for k, v in ledger.by_provider.items()},
        },
    }

    output_path = output_dir / "round_robin_results.json"
    _atomic_write(output_path, json.dumps(aggregate, indent=2) + "\n")
    _err(f"\n  Results written to {output_path}")

    # Save deferred items
    deferred_path = save_deferred_items(results, output_dir)
    _err(f"  Deferred items written to {deferred_path}")

    # Print summary to stdout
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
