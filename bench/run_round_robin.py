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
  - Gemini 3: Heterogeneous falsifier #1 (gemini CLI).
  - CX (Codex 5.3): Heterogeneous falsifier #2 (codex exec CLI).

Protocol per task per condition:
  Round 1 (blind):   CC generates solution; Gemini and CX independently
                     review (neither sees the other's findings).
  Rounds 2-5 (confer): Each reviewer receives the OTHER reviewer's
                        findings. CC assesses combined output.
  Stop rule:         Two consecutive rounds with zero novel HARD findings
                     AND both Gemini and CX concur → stop.
  Hard cap:          5 rounds total.

Gemini failure policy (non-skippable):
  1. Kill → retry same prompt (attempt 2)
  2. Progressively reduce prompt complexity (attempts 3-5)
  3. After 5 failures: STOP test, diagnose with CX, decide:
     (a) Fix identified → apply, resume
     (b) Fix uncertain → apply, resume, monitor
     (c) No viable fix → stop, save diagnostic, inform founder
  Gemini may NOT be skipped or replaced with a different model.

Verification chain (CDSFL layers 1-3):
  Layer 1: SHA-256 content hash of every artifact.
  Layer 2: Hash chain — each record links to its predecessor.
  Layer 3: Epoch Merkle tree — per-task Merkle root over all round hashes.

Usage:
    # Smoke test (1 task × 4 conditions, validates wiring + output quality)
    python3 bench/run_round_robin.py --smoke

    # Full run (25 tasks × 4 conditions = 100 runs)
    python3 bench/run_round_robin.py

    # Resume after crash
    python3 bench/run_round_robin.py --resume

    # Dry run (validate tasks and config only)
    python3 bench/run_round_robin.py --dry-run

    # Single condition only
    python3 bench/run_round_robin.py --condition cdsfl
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

# Load .env file at import time — ensures GEMINI_API_KEY is available
# for subprocess calls to gemini CLI.
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

from run_benchmark import (
    ADVERSARIAL_PASS_TEMPLATE,
    CDSFL_DIRECTIVES,
    INITIAL_PASS_TEMPLATE,
    FOLLOWUP_PASS_TEMPLATE,
    _err,
    _extract_section,
    _safe_format,
    call_gemini as _call_gemini_sdk,
    classify_issue_severity,
    compose_directives,
    load_directives,
    load_domain_directives,
    load_tasks,
)

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
LOGS_DIR = Path(__file__).parent / "logs"
TASKS_DIR = Path(__file__).parent / "tasks_frontier"
SMOKE_TASK_IDS = ["ft-001"]  # single task × 3 conditions for smoke
ALL_CONDITIONS = ("control", "hil", "cdsfl", "cdsfl_hil")
MAX_ROUNDS = 5
GEMINI_MAX_ATTEMPTS = 5  # non-skippable: 5 attempts before stop-and-diagnose
CONFER_START_ROUND = 1  # blind review IS round 1

# Timeout constants
GEMINI_TIMEOUT = 300   # Gemini: 5 min hard cap (was 600s — if it can't respond in 5, it won't in 10)
CX_TIMEOUT = 600       # CX: 10 min (consistently fast, but buffer for large prompts)
CC_TIMEOUT = 300       # CC generation: 5 min
CC_ARBITER_TIMEOUT = 120  # CC arbiter assessment: 2 min (bounded, non-fatal)
SAFETY_MARGIN = 60     # Budget safety margin (seconds)
PROMPT_SIZE_WARN = 50_000  # Warn if prompt exceeds this many chars

# Finding schema fields (normalised record)
FINDING_FIELDS = (
    "finding_id", "claim", "evidence_span", "constraint_class",
    "severity", "confidence", "proposed_check",
)


# ---------------------------------------------------------------------------
# Verification chain — CDSFL layers 1-3
# ---------------------------------------------------------------------------


def _content_hash(data: str) -> str:
    """Layer 1: SHA-256 content hash of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _chain_hash(content_hash: str, prev_hash: str) -> str:
    """Layer 2: Hash chain — link to predecessor."""
    return hashlib.sha256(
        f"{prev_hash}:{content_hash}".encode("utf-8")
    ).hexdigest()


def _merkle_root(hashes: list[str]) -> str:
    """Layer 3: Compute Merkle root from a list of hashes.

    Uses a standard binary Merkle tree. If the list has an odd number
    of elements, the last element is duplicated.
    """
    if not hashes:
        return _content_hash("")
    level = list(hashes)
    while len(level) > 1:
        next_level: list[str] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            next_level.append(
                hashlib.sha256(f"{left}:{right}".encode("utf-8")).hexdigest()
            )
        level = next_level
    return level[0]


class VerificationChain:
    """CDSFL verification chain — layers 1-3.

    Every artifact is hashed (layer 1), chained to its predecessor
    (layer 2), and combined into a Merkle root per epoch (layer 3).
    """

    def __init__(self):
        self.entries: list[dict[str, str]] = []
        self.prev_hash: str = _content_hash("GENESIS")  # chain anchor

    def record(self, artifact_type: str, content: str, metadata: dict | None = None) -> dict[str, str]:
        """Record an artifact in the chain. Returns the chain entry.

        CX P-pass fix (SOFT): metadata and artifact_type are now included
        in the chain hash so they cannot be altered without detection.
        """
        # Include metadata + type in the hashed content (CX SOFT fix 2)
        full_content = json.dumps({
            "artifact_type": artifact_type,
            "content": content,
            "metadata": metadata,
        }, sort_keys=True)
        content_h = _content_hash(full_content)
        chain_h = _chain_hash(content_h, self.prev_hash)
        entry = {
            "seq": len(self.entries),
            "artifact_type": artifact_type,
            "content_hash": content_h,
            "chain_hash": chain_h,
            "prev_hash": self.prev_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if metadata:
            entry["metadata"] = metadata
        self.entries.append(entry)
        self.prev_hash = chain_h
        return entry

    def merkle_root(self) -> str:
        """Layer 3: Compute Merkle root over all chain hashes."""
        return _merkle_root([e["chain_hash"] for e in self.entries])

    def verify_chain(self) -> tuple[bool, str]:
        """Verify the entire chain is intact. Returns (valid, message)."""
        if not self.entries:
            return True, "empty chain"
        expected_prev = _content_hash("GENESIS")
        for i, entry in enumerate(self.entries):
            if entry["prev_hash"] != expected_prev:
                return False, f"broken at entry {i}: prev_hash mismatch"
            recomputed = _chain_hash(entry["content_hash"], expected_prev)
            if recomputed != entry["chain_hash"]:
                return False, f"broken at entry {i}: chain_hash mismatch"
            expected_prev = entry["chain_hash"]
        return True, f"valid ({len(self.entries)} entries)"

    def to_dict(self) -> dict:
        return {
            "entries": self.entries,
            "merkle_root": self.merkle_root(),
            "chain_length": len(self.entries),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VerificationChain":
        """Reconstruct chain from serialised form (for resume)."""
        chain = cls()
        chain.entries = data.get("entries", [])
        if chain.entries:
            chain.prev_hash = chain.entries[-1]["chain_hash"]
        return chain


# ---------------------------------------------------------------------------
# Canonical defect key (for dedup/novelty tracking)
# ---------------------------------------------------------------------------


def _defect_key(task_id: str, constraint_class: str, claim: str) -> str:
    """Canonical defect key: full SHA-256 hash of (task_id, constraint_class, normalised claim).

    CX P-pass fix (SOFT 1): use full hash, not truncated 16-char.
    """
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
"proposed_check": "..."}},
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
2. Add any NEW findings they missed (use IDs starting after their highest).
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
"proposed_check": "..."}}, ...]

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
"proposed_check": "..."}}, ...]

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
"proposed_check": "..."}},
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
classification framework and the expert guidance.
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
You are a domain expert providing review guidance for the following task. \
Do NOT solve the task yourself. Instead, provide:

1. The 3-5 most critical constraints a reviewer should check.
2. Common failure modes in this problem domain.
3. Specific things to look for that a non-expert might miss.
4. Any domain-specific knowledge needed to evaluate correctness.

Task:
{task_prompt}

Provide your guidance in clear, actionable bullet points.
"""


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
        if stored_manifest != self.manifest:
            _err(f"  [checkpoint] INCOMPATIBLE: manifest mismatch")
            return False
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
        "models": ["claude-cli/opus-4.6", "gemini-sdk/gemini-3.1-pro-preview", "codex-cli/gpt-5.3-codex"],
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

        Bug fix (2026-03-21): budget clamping was strangling Gemini retries
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


def _prompt_size_check(prompt: str, label: str) -> None:
    """Log prompt size and warn if exceeding threshold."""
    chars = len(prompt)
    est_tokens = chars // 4  # rough estimate
    if chars > PROMPT_SIZE_WARN:
        _err(f"  [WARN] {label} prompt size: {chars} chars (~{est_tokens} tokens) — exceeds {PROMPT_SIZE_WARN}")
    else:
        _err(f"  [telemetry] {label} prompt: {chars} chars (~{est_tokens} tokens)")


# ---------------------------------------------------------------------------
# Gemini process cleanup — prevents zombie/orphan node processes
#
# Bug fix (2026-03-21): Gemini CLI spawns node processes that can hang
# and block subsequent calls. Three-layer defence:
#   1. Startup sweep: kill any pre-existing orphans from prior runs
#   2. Popen + process group: track and kill the exact process tree
#   3. Post-call sweep: verify no orphans remain
# ---------------------------------------------------------------------------

def _kill_gemini() -> None:
    """Kill all gemini node processes. Each call is stateless — kill before
    and after every invocation to prevent orphans accumulating."""
    sp.run(["pkill", "-f", "/opt/homebrew/bin/gemini"],
           capture_output=True, timeout=5)


def _call_gemini_simple(user_prompt: str) -> str:
    """Call Gemini 3.1 Pro Preview via Google GenAI SDK.

    Switched from gemini CLI (Gemini 3) to SDK (Gemini 3.1 Pro Preview)
    for stronger model capability and built-in prompt adaptation.
    The SDK call in run_benchmark.py handles context window issues via
    progressive prompt truncation (_truncate_prompt_for_gemini).

    Bug fix (2026-03-21): CLI used Gemini 3 (weaker model) and suffered
    persistent auth/zombie process issues. SDK uses API key directly,
    no subprocess, no orphans possible.
    """
    _prompt_size_check(user_prompt, "gemini")
    return _call_gemini_sdk(
        model="gemini-3.1-pro-preview",
        system_prompt=None,
        user_prompt=user_prompt,
    )


# ---------------------------------------------------------------------------
# Model callers — all via CLI subprocesses (no API SDKs)
#
# CC:     claude -p "..." --output-format text
# Gemini: gemini -p "..." --output-format text
# CX:     codex exec -o output_file "..."
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
        if result.returncode != 0:
            stderr = result.stderr[:300] if result.stderr else "(no stderr)"
            raise RuntimeError(f"{label} failed (exit {result.returncode}): {stderr}")
        output = result.stdout.strip()
        if not output:
            raise RuntimeError(f"{label} returned empty output")
        return output
    except sp.TimeoutExpired:
        raise RuntimeError(f"{label} timed out after {timeout}s")
    except FileNotFoundError:
        raise RuntimeError(f"{label} CLI not found on PATH")


def _call_cc_inner(system_prompt: str | None, user_prompt: str) -> str:
    """CC (Opus 4.6) via claude CLI (inner, no retry).

    Pipes the combined prompt via stdin. System prompt (CDSFL directives)
    is prepended to the user prompt to stay within ARG_MAX limits.
    """
    cmd = ["claude", "-p", "--output-format", "text"]

    if system_prompt:
        combined = f"SYSTEM DIRECTIVES:\n{system_prompt}\n\nTASK:\n{user_prompt}"
    else:
        combined = user_prompt

    timeout = _budget.clamp_timeout(CC_TIMEOUT) if _budget else CC_TIMEOUT
    _prompt_size_check(combined, "cc")
    return _call_cli(cmd, input_text=combined, timeout=timeout, label="claude")


def _call_cc(system_prompt: str | None, user_prompt: str) -> str:
    """CC with deterministic failure policy (1 retry)."""
    return _with_retry(_call_cc_inner, system_prompt, user_prompt)


def _reduce_prompt_complexity(prompt: str, attempt: int) -> str:
    """Progressively reduce prompt complexity for Gemini retries.

    Attempt 1-2: full prompt (no reduction).
    Attempt 3: strip supplementary context (evidence spans in prior findings).
    Attempt 4: strip confidence/proposed_check fields from findings.
    Attempt 5: strip everything except core task + solution + bare findings list.

    The core adversarial brief and task always stay intact.
    """
    if attempt <= 2:
        return prompt

    import re

    if attempt == 3:
        # Strip evidence_span values (keep the key for schema compliance)
        prompt = re.sub(
            r'"evidence_span"\s*:\s*"[^"]*"',
            '"evidence_span": "(reduced)"',
            prompt,
        )
        return prompt

    if attempt == 4:
        # Strip evidence_span + confidence + proposed_check
        prompt = re.sub(r'"evidence_span"\s*:\s*"[^"]*"', '"evidence_span": "(reduced)"', prompt)
        prompt = re.sub(r'"confidence"\s*:\s*[\d.]+', '"confidence": 0.5', prompt)
        prompt = re.sub(r'"proposed_check"\s*:\s*"[^"]*"', '"proposed_check": "(reduced)"', prompt)
        return prompt

    # attempt >= 5: strip to bare minimum
    prompt = re.sub(r'"evidence_span"\s*:\s*"[^"]*"', '"evidence_span": "(reduced)"', prompt)
    prompt = re.sub(r'"confidence"\s*:\s*[\d.]+', '"confidence": 0.5', prompt)
    prompt = re.sub(r'"proposed_check"\s*:\s*"[^"]*"', '"proposed_check": "(reduced)"', prompt)
    prompt = re.sub(r'"justification"\s*:\s*"[^"]*"', '"justification": "(reduced)"', prompt)
    return prompt


def _call_gemini_with_retry(user_prompt: str) -> str:
    """Gemini reviewer with 5-attempt progressive retry policy.

    Gemini may NOT be skipped. If all 5 attempts fail, raises
    GeminiExhausted which triggers stop-and-diagnose with CX.
    """
    last_error = None
    for attempt in range(1, GEMINI_MAX_ATTEMPTS + 1):
        reduced = _reduce_prompt_complexity(user_prompt, attempt)
        if attempt > 1:
            _err(f"    [gemini retry] attempt {attempt}/{GEMINI_MAX_ATTEMPTS}"
                 f"{' (prompt reduced)' if attempt >= 3 else ''}")
        try:
            return _call_gemini_simple(reduced)
        except Exception as exc:
            last_error = exc
            _err(f"    [gemini retry] attempt {attempt} failed: {str(exc)[:100]}")
            time.sleep(3)

    exc = GeminiExhausted(
        f"Gemini failed all {GEMINI_MAX_ATTEMPTS} attempts. "
        f"Last error: {last_error}"
    )
    exc.prompt_size = len(user_prompt)  # CX P-pass fix (HARD 4)
    raise exc


class GeminiExhausted(Exception):
    """Raised when Gemini fails all retry attempts. Triggers stop-and-diagnose."""
    prompt_size: int = 0


def _diagnose_gemini_with_cx(task_id: str, error: str, prompt_size: int) -> dict:
    """Stop-and-diagnose: ask CX to help diagnose the Gemini failure.

    Returns a diagnostic dict with CX's assessment and recommendation.
    """
    _err(f"  [STOP] Gemini exhausted all {GEMINI_MAX_ATTEMPTS} attempts — diagnosing with CX")

    diag_prompt = (
        f"CX, Gemini has failed all {GEMINI_MAX_ATTEMPTS} attempts on task {task_id}. "
        f"Last error: {error[:500]}. "
        f"Prompt size was {prompt_size} chars (~{prompt_size // 4} tokens). "
        f"Progressive prompt reduction was applied on attempts 3-5. "
        f"Diagnose: is this (a) a prompt size issue, (b) a Gemini service issue, "
        f"(c) a content issue (something in the prompt Gemini can't handle), or "
        f"(d) something else? "
        f"Recommend: (1) a specific fix to try, (2) whether to resume or stop, "
        f"(3) whether this is likely to recur on other tasks. Be direct."
    )

    try:
        cx_response = _call_cx_reviewer(diag_prompt, f"diag_{task_id}")
        _err(f"  [DIAG] CX response: {cx_response[:300]}")
        return {
            "cx_diagnosis": cx_response,
            "recommendation": "see_cx_response",
            "task_id": task_id,
            "error": error,
            "prompt_size": prompt_size,
        }
    except Exception as cx_exc:
        _err(f"  [DIAG] CX also failed: {cx_exc}")
        return {
            "cx_diagnosis": f"CX diagnostic also failed: {cx_exc}",
            "recommendation": "stop_and_inform_founder",
            "task_id": task_id,
            "error": error,
            "prompt_size": prompt_size,
        }


def _call_gemini_reviewer(user_prompt: str) -> str:
    """Gemini reviewer — 5-attempt progressive retry, non-skippable."""
    return _call_gemini_with_retry(user_prompt)


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

    # Normalise constraint_class: strip whitespace, uppercase, default HARD
    raw_class = str(f.get("constraint_class", "HARD")).strip().upper()
    normalised["constraint_class"] = "HARD" if raw_class not in ("HARD", "SOFT") else raw_class

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
    return normalised


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
) -> dict:
    """Round 1: Dual blind review — Gemini and CX independently review."""
    task_id = task["id"]
    _err(f"  [round 1/blind] starting dual blind review for {task_id} [{condition}]")

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

    # Gemini blind review
    gemini_findings_raw = ""
    gemini_findings: list[dict] = []
    gemini_error = None
    _err(f"  [round 1/blind] calling Gemini 3.1 Pro ...")
    t0 = time.monotonic()
    try:
        gemini_findings_raw = _call_gemini_reviewer(blind_prompt)
        gemini_findings = _extract_findings_json(gemini_findings_raw)
        elapsed = time.monotonic() - t0
        _err(f"  [round 1/blind] Gemini done ({elapsed:.1f}s, {len(gemini_findings)} findings)")
        ledger.record("gemini_cli", 0.0)  # subscription-based
    except GeminiExhausted:
        raise  # non-skippable — propagate for stop-and-diagnose
    except Exception as exc:
        elapsed = time.monotonic() - t0
        gemini_error = str(exc)
        _err(f"  [round 1/blind] Gemini FAILED ({elapsed:.1f}s): {gemini_error[:100]}")

    chain.record("gemini_blind", gemini_findings_raw or f"ERROR: {gemini_error}",
                 {"task_id": task_id, "round": 1})

    # CX blind review
    cx_findings_raw = ""
    cx_findings: list[dict] = []
    cx_error = None
    _err(f"  [round 1/blind] calling Codex 5.3 ...")
    t0 = time.monotonic()
    try:
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

    return {
        "round": 1,
        "round_type": "blind",
        "input_hash": input_hash,
        "gemini": {
            "raw_response": gemini_findings_raw,
            "findings": gemini_findings,
            "error": gemini_error,
        },
        "cx": {
            "raw_response": cx_findings_raw,
            "findings": cx_findings,
            "error": cx_error,
        },
    }


def _run_confer_round(
    task: dict,
    solution: str,
    round_num: int,
    gemini_prev_findings: list[dict],
    cx_prev_findings: list[dict],
    chain: VerificationChain,
    ledger: CostLedger,
    output_dir: Path | None = None,
    condition: str = "cdsfl",
    expert_guidance: str = "",
) -> dict:
    """Rounds 2-5: Confer — each reviewer sees the OTHER's findings.

    CX P-pass fix (HARD 5): findings are written to files; prompts reference
    file-path payloads for auditability and hashability.
    """
    task_id = task["id"]
    _err(f"  [round {round_num}/confer] starting confer round for {task_id} [{condition}]")

    _, confer_template = _get_condition_prompts(condition)

    # Write findings to artifact files (CX HARD fix 5: file-path payloads)
    artifacts_dir = (output_dir or RESULTS_DIR) / "artifacts" / task_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    cx_findings_path = artifacts_dir / f"round_{round_num}_cx_prev_findings.json"
    gemini_findings_path = artifacts_dir / f"round_{round_num}_gemini_prev_findings.json"
    _atomic_write(cx_findings_path, json.dumps(cx_prev_findings, indent=2, sort_keys=True) + "\n")
    _atomic_write(gemini_findings_path, json.dumps(gemini_prev_findings, indent=2, sort_keys=True) + "\n")

    # Gemini gets CX's findings (from file)
    cx_findings_json = cx_findings_path.read_text()
    fmt_kwargs_g = {"task_prompt": task["prompt"], "solution": solution, "other_findings": cx_findings_json}
    if condition in ("hil", "cdsfl_hil"):
        fmt_kwargs_g["expert_guidance"] = expert_guidance
    gemini_confer_prompt = _safe_format(confer_template, **fmt_kwargs_g)

    # CX gets Gemini's findings (from file)
    gemini_findings_json = gemini_findings_path.read_text()
    fmt_kwargs_c = {"task_prompt": task["prompt"], "solution": solution, "other_findings": gemini_findings_json}
    if condition in ("hil", "cdsfl_hil"):
        fmt_kwargs_c["expert_guidance"] = expert_guidance
    cx_confer_prompt = _safe_format(confer_template, **fmt_kwargs_c)

    # Hash the input bundle
    input_bundle = json.dumps({
        "task_id": task_id,
        "round": round_num,
        "round_type": "confer",
        "solution_hash": _content_hash(solution),
        "gemini_prompt_hash": _content_hash(gemini_confer_prompt),
        "cx_prompt_hash": _content_hash(cx_confer_prompt),
    }, sort_keys=True)
    input_hash = _content_hash(input_bundle)
    chain.record("round_input", input_bundle, {"task_id": task_id, "round": round_num})

    # Gemini confer
    gemini_raw = ""
    gemini_response: dict = {}
    gemini_error = None
    _err(f"  [round {round_num}/confer] calling Gemini (reviewing CX findings) ...")
    t0 = time.monotonic()
    try:
        gemini_raw = _call_gemini_reviewer(gemini_confer_prompt)
        gemini_response = _extract_confer_response(gemini_raw)
        elapsed = time.monotonic() - t0
        _err(f"  [round {round_num}/confer] Gemini done ({elapsed:.1f}s, "
             f"{len(gemini_response.get('new_findings', []))} new findings, "
             f"concur_stop={gemini_response.get('concur_stop')})")
        ledger.record("gemini_cli", 0.0)  # subscription-based
    except GeminiExhausted:
        raise  # non-skippable — propagate for stop-and-diagnose
    except Exception as exc:
        elapsed = time.monotonic() - t0
        gemini_error = str(exc)
        _err(f"  [round {round_num}/confer] Gemini FAILED ({elapsed:.1f}s): {gemini_error[:100]}")

    chain.record("gemini_confer", gemini_raw or f"ERROR: {gemini_error}",
                 {"task_id": task_id, "round": round_num})

    # CX confer
    cx_raw = ""
    cx_response: dict = {}
    cx_error = None
    _err(f"  [round {round_num}/confer] calling CX (reviewing Gemini findings) ...")
    t0 = time.monotonic()
    try:
        cx_raw = _call_cx_reviewer(cx_confer_prompt, task_id)
        cx_response = _extract_confer_response(cx_raw)
        elapsed = time.monotonic() - t0
        _err(f"  [round {round_num}/confer] CX done ({elapsed:.1f}s, "
             f"{len(cx_response.get('new_findings', []))} new findings, "
             f"concur_stop={cx_response.get('concur_stop')})")
        ledger.record("codex", 0.0)
    except Exception as exc:
        elapsed = time.monotonic() - t0
        cx_error = str(exc)
        _err(f"  [round {round_num}/confer] CX FAILED ({elapsed:.1f}s): {cx_error[:100]}")

    chain.record("cx_confer", cx_raw or f"ERROR: {cx_error}",
                 {"task_id": task_id, "round": round_num})

    return {
        "round": round_num,
        "round_type": "confer",
        "input_hash": input_hash,
        "gemini": {
            "raw_response": gemini_raw,
            "confer_response": gemini_response,
            "error": gemini_error,
        },
        "cx": {
            "raw_response": cx_raw,
            "confer_response": cx_response,
            "error": cx_error,
        },
    }


# ---------------------------------------------------------------------------
# Novelty and stop-rule assessment
# ---------------------------------------------------------------------------


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

    for source in ("gemini", "cx"):
        source_data = current_round.get(source, {})
        if current_round["round_type"] == "blind":
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
            key = _defect_key(task_id, constraint, claim)
            round_keys.add(key)

    # Novel = keys in this round that aren't already known
    new_keys = round_keys - all_known_keys
    return len(new_keys), new_keys


def _both_concur_stop(round_data: dict) -> bool:
    """Check if both Gemini and CX concur that diminishing returns are reached."""
    gemini_concur = (
        round_data.get("gemini", {})
        .get("confer_response", {})
        .get("concur_stop", False)
    )
    cx_concur = (
        round_data.get("cx", {})
        .get("confer_response", {})
        .get("concur_stop", False)
    )
    return gemini_concur and cx_concur


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


def _generate_cc_solution(task: dict, directives: str, condition: str = "cdsfl") -> str:
    """CC generates the initial solution.

    CX P-pass fix (HARD 1): control and hil conditions use a raw prompt
    (no CDSFL template, no P-Pass language). cdsfl and cdsfl_hil use INITIAL_PASS_TEMPLATE.
    """
    task_id = task["id"]
    _err(f"  [generate] CC generating solution for {task_id} [{condition}] ...")

    if condition in ("cdsfl", "cdsfl_hil"):
        user_prompt = _safe_format(
            INITIAL_PASS_TEMPLATE,
            n="1",
            total="3",
            task_prompt=task["prompt"],
        )
    else:
        # Control and HIL: raw generation — no CDSFL framework language
        user_prompt = _safe_format(RAW_GENERATION_PROMPT, task_prompt=task["prompt"])

    t0 = time.monotonic()
    response = _call_cc(directives, user_prompt)
    elapsed = time.monotonic() - t0
    _err(f"  [generate] CC solution done ({elapsed:.1f}s)")

    if condition in ("cdsfl", "cdsfl_hil"):
        revised = _extract_section(response, "REVISED_ANSWER")
        initial = _extract_section(response, "INITIAL_ANSWER")
        return revised or initial or response
    else:
        return response


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

    # CX P-pass fix (HARD 7): check cost cap BEFORE expensive generation
    if not ledger.check_cap():
        _err(f"  [cost] cap reached before generation — skipping task")
        return {
            "task_id": task_id,
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
    expert_guidance = ""
    if condition in ("hil", "cdsfl_hil"):
        _err(f"  [hil] CC generating domain expert guidance ...")
        t0 = time.monotonic()
        try:
            guidance_prompt = _safe_format(HIL_EXPERT_GUIDANCE_PROMPT, task_prompt=task["prompt"])
            expert_guidance = _call_cc(None, guidance_prompt)
            elapsed = time.monotonic() - t0
            _err(f"  [hil] expert guidance done ({elapsed:.1f}s, {len(expert_guidance)} chars)")
            chain.record("expert_guidance", expert_guidance, {"task_id": task_id})
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

    # Step 2: Run rounds
    rounds: list[dict] = []
    all_known_keys: set[str] = set()
    consecutive_zero_novel = 0
    status = "DEFERRED"  # default if we exhaust all rounds
    deferred_items: list[dict] = []

    for round_num in range(1, MAX_ROUNDS + 1):
        if not ledger.check_cap():
            _err(f"  [cost] cap reached — stopping at round {round_num}")
            status = "COST_CAP"
            break

        # Budget exhaustion no longer interrupts mid-task. Once a task starts,
        # it runs to completion. Budget is checked at task/condition boundaries only.

        if round_num == 1:
            # Blind round
            round_data = _run_blind_round(task, solution, chain, ledger,
                                          condition=condition, expert_guidance=expert_guidance)
        else:
            # Confer round — each sees the OTHER's previous findings
            prev_round = rounds[-1]
            if prev_round["round_type"] == "blind":
                gemini_prev = prev_round["gemini"].get("findings", [])
                cx_prev = prev_round["cx"].get("findings", [])
            else:
                # CX P-pass fix (SOFT 3): pass only new_findings, not mixed
                # assessment objects — keeps schema consistent for reviewer context.
                gemini_prev = prev_round["gemini"].get("confer_response", {}).get("new_findings", [])
                cx_prev = prev_round["cx"].get("confer_response", {}).get("new_findings", [])

            round_data = _run_confer_round(
                task, solution, round_num,
                gemini_prev, cx_prev,
                chain, ledger,
                output_dir=output_dir,
                condition=condition,
                expert_guidance=expert_guidance,
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

        # CX P-pass fix (HARD 2): defer on ANY reviewer failure, not just both.
        # Single-reviewer failure breaks the topology (need both for biodiversity).
        gemini_err = round_data.get("gemini", {}).get("error")
        cx_err = round_data.get("cx", {}).get("error")
        if gemini_err or cx_err:
            failed = []
            if gemini_err:
                failed.append("Gemini")
            if cx_err:
                failed.append("CX")
            _err(f"  [round {round_num}] reviewer(s) failed: {', '.join(failed)} — deferring")
            deferred_items.append({
                "round": round_num,
                "reason": "reviewer_failed",
                "failed_reviewers": failed,
                "gemini_error": gemini_err,
                "cx_error": cx_err,
            })
            # Deterministic failure policy: one retry already happened inside callers
            status = "DEFERRED_INFRA"
            break

        # Novelty assessment
        novel_count, new_keys = _count_novel_hard_findings(round_data, all_known_keys, task_id)
        all_known_keys.update(new_keys)
        _err(f"  [round {round_num}] novel HARD findings: {novel_count} (total unique: {len(all_known_keys)})")

        if novel_count == 0:
            consecutive_zero_novel += 1
        else:
            consecutive_zero_novel = 0

        # Pre-registered stop rule: 2 consecutive rounds with 0 novel HARD + both concur
        if round_num >= 2 and consecutive_zero_novel >= 2:
            if round_data["round_type"] == "confer" and _both_concur_stop(round_data):
                _err(f"  [stop] pre-registered stop rule met at round {round_num}: "
                     f"2+ consecutive zero-novel-HARD + both concur")
                status = "RESOLVED"
                break
            elif round_data["round_type"] == "confer":
                _err(f"  [stop] 2+ consecutive zero-novel-HARD but no concurrence — "
                     f"recording disagreement")
                deferred_items.append({
                    "round": round_num,
                    "reason": "no_concurrence_on_stop",
                    "gemini_concur": round_data.get("gemini", {}).get("confer_response", {}).get("concur_stop"),
                    "cx_concur": round_data.get("cx", {}).get("confer_response", {}).get("concur_stop"),
                })

        # CC arbiter assessment — bounded Claude CLI call (non-fatal on timeout)
        if round_num < MAX_ROUNDS:
            _err(f"  [arbiter] CC assessing — round {round_num} complete, "
                 f"consecutive_zero_novel={consecutive_zero_novel}")
            try:
                arbiter_timeout = _budget.clamp_timeout(CC_ARBITER_TIMEOUT) if _budget else CC_ARBITER_TIMEOUT
                arbiter_prompt = (
                    f"You are the CC arbiter in a CDSFL round-robin test. "
                    f"Task: {task_id}. Round {round_num} of {MAX_ROUNDS} complete. "
                    f"Total unique HARD findings so far: {len(all_known_keys)}. "
                    f"Novel HARD findings this round: {novel_count}. "
                    f"Consecutive zero-novel rounds: {consecutive_zero_novel}. "
                    f"Assess: should the next round proceed or are diminishing returns reached? "
                    f"Reply in one sentence."
                )
                arbiter_response = _call_cli(
                    ["claude", "-p", "--output-format", "text"],
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
        help="Global deadline budget in seconds (default: 5400 for smoke, 43200 for full)",
    )
    parser.add_argument(
        "--condition", type=str, default=None,
        choices=ALL_CONDITIONS,
        help="Run a single condition only (default: all four)",
    )

    args = parser.parse_args()

    # Set up log file — always enabled (auto-generate if not specified)
    if args.log_file:
        log_path = Path(args.log_file)
    else:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        mode = "smoke" if args.smoke else "full"
        log_path = LOGS_DIR / f"round_robin_{mode}_{timestamp}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    _setup_log_tee(log_path)
    _err(f"[log] activity log: {log_path}")

    # Set up global deadline budget
    global _budget
    if args.max_runtime:
        max_runtime = args.max_runtime
    else:
        max_runtime = 5400 if args.smoke else 43200  # 90 min smoke (4 conditions), 12 hr full
    _budget = DeadlineBudget(max_runtime)
    _err(f"[budget] deadline: {max_runtime}s ({max_runtime // 60}m)")

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
        tasks = [t for t in tasks if t["id"] in SMOKE_TASK_IDS]
        _err(f"Smoke test: {len(tasks)} task(s) selected")
        if not tasks:
            _err(f"ERROR: smoke task IDs {SMOKE_TASK_IDS} not found in {tasks_dir}")
            sys.exit(1)

    # Output directory
    output_dir = Path(args.output_dir) if args.output_dir else RESULTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dry run
    if args.dry_run:
        _err(f"\nDry run summary:")
        _err(f"  Tasks:      {len(tasks)}")
        _err(f"  Max rounds: {MAX_ROUNDS}")
        _err(f"  Cost cap:   ${args.cost_cap:.2f}")
        _err(f"  Output:     {output_dir}")
        _err(f"  Directives: {'custom' if args.directives else 'built-in'} ({directives_hash})")
        _err(f"  Models:     CC (claude CLI, Opus 4.6), Gemini (gemini CLI, Gemini 3), CX (codex CLI, GPT-5.3)")

        # Validate environment — all three CLIs must be available
        env_ok = True
        for cli_name in ("claude", "gemini", "codex"):
            try:
                sp.run([cli_name, "--version"], capture_output=True, timeout=10)
            except (FileNotFoundError, sp.TimeoutExpired):
                _err(f"  WARNING: {cli_name} CLI not found or not responding")
                env_ok = False

        if env_ok:
            _err("  Environment: OK (claude, gemini, codex all available)")
        sys.exit(0)

    # Validate environment (non-dry-run) — all three CLIs must be available
    for cli_name in ("claude", "gemini", "codex"):
        try:
            sp.run([cli_name, "--version"], capture_output=True, timeout=10)
        except (FileNotFoundError, sp.TimeoutExpired):
            _err(f"ERROR: {cli_name} CLI not found or not responding")
            sys.exit(1)

    # Startup: kill any stale gemini processes from prior runs
    _kill_gemini()
    _err("[startup] gemini cleanup done")

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
    gemini_stopped = False  # if True, Gemini exhausted — test halted

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
                gemini_stopped = True  # use as general halt flag
                break

            if _budget and _budget.exhausted():
                _err(f"[{run_idx}/{total_runs}] {run_key} — skipped (deadline budget exhausted)")
                _err(f"  [budget] {_budget.summary()}")
                gemini_stopped = True
                break

            _err(f"[{run_idx}/{total_runs}] {run_key}")
            _err(f"  [budget] {_budget.summary()}" if _budget else "")
            try:
                result = run_task(
                    task, directives, ledger,
                    output_dir=output_dir, checkpoint=checkpoint,
                    condition=condition,
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

            except GeminiExhausted as exc:
                _err(f"  [{run_key}] GEMINI EXHAUSTED — stopping test for diagnosis")
                # Track last failed prompt size for diagnosis
                prompt_size = getattr(exc, 'prompt_size', 0) or len(str(exc))
                diagnostic = _diagnose_gemini_with_cx(
                    task_id, str(exc), prompt_size,
                )
                error_result = {
                    "task_id": task_id,
                    "condition": condition,
                    "status": "GEMINI_EXHAUSTED",
                    "error": str(exc),
                    "diagnostic": diagnostic,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                results.append(error_result)
                # CX P-pass fix (HARD 3): do NOT checkpoint under run_key —
                # that would block resume. Save under a diagnostic key instead
                # so the run can be retried after fixes are applied.
                checkpoint.save(f"{run_key}__gemini_diag", error_result)

                # Save diagnostic for founder review
                diag_path = output_dir / f"{task_id}_{condition}_gemini_diagnostic.json"
                _atomic_write(diag_path, json.dumps(diagnostic, indent=2) + "\n")
                _err(f"  [DIAG] saved to {diag_path}")

                # STOP the entire test — Gemini is non-skippable
                gemini_stopped = True
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

        if gemini_stopped:
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
            "max_rounds": MAX_ROUNDS,
            "cost_cap_usd": args.cost_cap,
            "directives_hash": directives_hash,
            "corpus_hash": corpus_manifest["corpus_hash"],
            "models": {
                "orchestrator": "claude-cli/opus-4.6",
                "falsifier_1": "gemini-sdk/gemini-3.1-pro-preview",
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
