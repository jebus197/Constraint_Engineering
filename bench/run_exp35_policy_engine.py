#!/usr/bin/env python3
"""Experiment 35: PolicyEngine Code Review — Dual-Topology Runner.

Reviews the PolicyEngine (engine.py + schema.toml) — 55-parameter facade
over 4-layer TOML hierarchy with monotonicity enforcement. Newly built,
never reviewed by models.

Subject under review: bench/cdsfl_registry/engine.py (~310 lines).
Schema definition: bench/cdsfl_registry/schema.toml (~250 lines, bundled).
Context files: registry.py, composer.py (read-only, for TOML merge context).

Architecture (user-configurable topology):
  - RELAY mode: insect brain relays full model responses between models.
    Models see each other's reasoning. Human-readable conversation.
    Budget-aware content sizing via brain's relay() method.
    Directed inter-model messaging (@tags). Natural pacing.
  - STAR mode: runner-owned blackboard. Models see a structured registry
    summary, never each other's raw prose. Clean attribution, auditable.
  - Both modes share: FindingRegistry (canonical state), convergence gate
    (5-condition temporal conjunction), immune pipeline, endocrine layer,
    ITC adaptive recovery, persistent signed fingerprints.
  - Status model: OPEN -> CONFIRMED (2+ independent) / MERGED / UNCONFIRMED
  - FFF is prompt-only (no enforcement)
  - Programmatic status transitions wired

Models:
  - CC2 (Claude Opus 4.6 via Claude CLI, Max plan)
  - Codex (GPT-5.4 Codex via OpenRouter)
  - Gemini (Gemini 3.1 Pro via Google SDK)
  - DeepSeek (DeepSeek Reasoner via DeepSeek API)
  - ChatGPT (GPT-5.4 via OpenRouter)

Usage:
    python3 bench/run_exp35_policy_engine.py [preflight|run|--resume]
    python3 bench/run_exp35_policy_engine.py run --topology relay --relay-mode directed
    python3 bench/run_exp35_policy_engine.py run --topology star
    python3 bench/run_exp35_policy_engine.py run --pattern fff
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Path setup
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    load_default_config,
    dispatch,
    save_output,
    _log,
    CircuitBreakerTripped,
    ExperimentConfig,
    ModelConfig,
)
from dynamic_management import (
    DynamicManager,
    DynamicManagementConfig,
    ModelSpec,
    CapabilityFingerprint,
    Task,
    Finding,
    ModelResponse,
)
from runner_core import (
    source_env,
    build_model_specs,
    parse_findings,
    dispatch_to_model,
    format_findings_for_context,
    INITIAL_FINGERPRINTS,
    MODEL_SPECS,
    CONVERGENCE_EXCLUDED_MODELS,
    CONTEXT_CHAR_BUDGET,
)
from run_exp17_immune import (
    TASKS,
    TASK_MARKERS,
    REVIEW_AREAS,
    FINDING_FORMAT,
    RoundTelemetry,
    run_layer1_preflight,
    _should_decompose,
    _build_verified_facts,
    _build_explicit_unknowns,
    _find_model_spec,
    _report_dispatch_failure,
    _record_throughput,
    _effective_capacity,
)
from decomposed_dispatch import (
    decomposed_dispatch,
    DecomposedChunk,
    DecomposedResult,
    save_decomposed_result,
)
from bench.insect_brain import InsectBrain
from bench.cdsfl_registry.composer import (
    compose,
    DirectivePacket,
    ComposedDirectiveSet,
    COMPOSER_MODEL_MAP,
    build_interaction_pattern,
    INTERACTION_PATTERN_PRESETS,
)
from input_complexity import (
    compute_gamma_input,
    compute_gamma_output,
    compute_amplification,
    AmplificationHistory,
    AdaptiveQuestionOptimiser,
)
from bench.endocrine import (
    EndocrineLayer,
    EndocrineReport,
    RoundTiming,
    HealthScan,
    FixEvaluation,
    PacingSignal,
)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

def _find_or_create_logs_dir(resume: bool = False) -> Path:
    """Find existing exp35 logs dir for resume, or create a new one."""
    if resume:
        logs_root = REPO_ROOT / "bench" / "logs"
        candidates = sorted(
            logs_root.glob("exp35_pe_*"),
            key=lambda p: p.name,
            reverse=True,
        )
        for c in candidates:
            if (c / "checkpoint.json").exists():
                return c
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "bench" / "logs" / f"exp35_pe_{ts}"


LOGS_DIR = REPO_ROOT / "bench" / "logs" / "exp35_pe_latest"

MAX_ROUNDS = 21              # Mathematical model: 20 rounds for this complexity
EXTENSION_CAP = 24           # Budget extension ceiling
WALL_CLOCK_CAP_S = 8 * 3600  # 8 hours (longer than Exp 31 due to 21 rounds)

# Test article: PolicyEngine (newly built, never reviewed by models)
TARGET_FILE = REPO_ROOT / "bench" / "cdsfl_registry" / "engine.py"

# Schema definition: bundled with target for review
SCHEMA_FILE = REPO_ROOT / "bench" / "cdsfl_registry" / "schema.toml"

# Context files: models read these for interface understanding, not review
CONTEXT_FILES = [
    REPO_ROOT / "bench" / "cdsfl_registry" / "registry.py",
]

# 5-model set — all retained for diversity testing
BASELINE_MODELS = {"CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"}

DEFAULT_PATTERN = "fff"
DEFAULT_TOPOLOGY = "relay"          # "relay" or "star" — user configurable
DEFAULT_RELAY_MODE = "directed"     # "findings", "conversational", "directed"

MODEL_ROSTER = {
    "CC2": "Claude Opus 4.6 (Anthropic)",
    "Codex": "GPT-5.4 Codex (OpenAI)",
    "Gemini": "Gemini 3.1 Pro (Google)",
    "DeepSeek": "DeepSeek Reasoner (DeepSeek)",
    "ChatGPT": "GPT-5.4 (OpenAI)",
}

MULTITURN_CHUNK_TARGET = 30_000

# ─────────────────────────────────────────────────────────────────────────────
# Convergence parameters (corrected from Exp 32 meta-analysis)
# ─────────────────────────────────────────────────────────────────────────────

# State-based convergence gate — compound conditions
EARLIEST_STOP_ROUND = 12        # No convergence before R12 (was R6 in Exp 32 proposal)
CONSECUTIVE_ROUNDS_REQUIRED = 2  # Conditions must hold for 2 consecutive rounds
MAX_NOVEL_FINDINGS = 2           # Novel findings <= 2 per round to qualify
OPEN_CH_STABILITY_WINDOW = 3    # open_ch must not increase for this many rounds
MAX_OPEN_CRIT_HIGH = 0           # Zero open CRITICAL/HIGH to qualify

# Stall-convergence detector — complementary secondary signal
STALL_WINDOW = 3                 # open_ch + contested must be static for this many rounds
STALL_EARLIEST_ROUND = 15        # Don't fire before R15 (allow models to settle)
STALL_GAMMA_ADVISORY = 0.30      # Tier 1: log advisory ("system may be plateauing")
STALL_GAMMA_TERMINATE = 0.45     # Tier 2: terminate with STALL_CONVERGED

# CC2v — between-rounds verification agent
VERIFICATION_BATCH_SIZE = 6      # Max OPEN findings per verification step
VERIFICATION_MIN_ROUND = 6       # Don't verify before round 6 (let findings accumulate)
VERIFICATION_CONFIDENCE_THRESHOLD = 0.7  # Min confidence for verification verdicts

# Scale-dependent gamma thresholds
GAMMA_TELEMETRY_ONLY_UNTIL = 14  # Rounds 0-14: gamma is telemetry only
GAMMA_SOFT_GATE_UNTIL = 19       # Rounds 15-19: gamma is soft gate
GAMMA_SOFT_THRESHOLD = 0.30      # Below this, flag for HIL review
GAMMA_HARD_THRESHOLD = 0.35      # Below this at R20+, block convergence
MIN_ROUNDS_FOR_GAMMA = 3

# Budget extension triggers (checked at MAX_ROUNDS)
# Extend to EXTENSION_CAP if any of these hold at end of R21:
#   - Open CRITICAL/HIGH target-code findings exist
#   - Any finding in PENDING_RESOLUTION for >1 round
#   - Gamma trending upward in 0.25-0.35 range

# Gamma interpretation bands (telemetry, logged but not gated until R15)
GAMMA_BANDS = [
    (0.45, float("inf"), "Strong depletion — confirms state-based closure"),
    (0.30, 0.45, "Moderate depletion — consistent with PoC convergence"),
    (0.20, 0.30, "Weak depletion — state closure may be premature"),
    (0.00, 0.20, "Gamma disagrees with state closure — recommend HIL audit"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Star/blackboard registry
# ─────────────────────────────────────────────────────────────────────────────

class FindingRegistry:
    """Canonical finding registry — runner-owned, models read/propose only.

    The star/blackboard topology: models emit DISCOVERY and VERDICT payloads.
    The runner maintains the canonical registry. Models see a structured
    summary each round, not each other's raw prose.

    Scale note: this is the in-process PoC implementation. The interface
    (register, add_verdict, build_summary, resolve, lookup_alias) is
    designed to be reimplemented over a distributed backend (CRDT,
    sharded service, etc.) without changing the runner or model contracts.
    See Exp 32 consensus on topology evolution.
    """

    def __init__(self):
        self.entries: Dict[str, Dict[str, Any]] = {}  # canonical_id -> entry
        self._next_id = 1
        self._alias_map: Dict[str, str] = {}  # "model_id:local_id" -> canonical_id

    def register(self, finding: Finding, model_id: str) -> str:
        """Register a new finding. Returns canonical ID."""
        canonical_id = f"C{self._next_id:04d}"
        self._next_id += 1

        self._alias_map[f"{model_id}:{finding.finding_id}"] = canonical_id

        self.entries[canonical_id] = {
            "canonical_id": canonical_id,
            "source_model": model_id,
            "source_aliases": [finding.finding_id],
            "severity": finding.severity,
            "description": finding.description[:500],
            "proposed_fix": finding.proposed_fix[:500] if finding.proposed_fix else "",
            "status": "OPEN",
            "open_since_round": getattr(finding, "round_idx", 0),
            "last_status_change_round": getattr(finding, "round_idx", 0),
            "verdicts": [],  # list of (model, verdict_type, round)
            "verified": finding.verified,
            "escalated": finding.escalated,
            "flaw_class": getattr(finding, "flaw_class", 0),
        }
        return canonical_id

    def add_verdict(
        self, canonical_id: str, model_id: str, verdict: str,
        round_idx: int, evidence: str = "",
    ):
        """Record a CONFIRM/CHALLENGE/EXTEND/MERGE verdict."""
        if canonical_id not in self.entries:
            return
        self.entries[canonical_id]["verdicts"].append({
            "model": model_id,
            "verdict": verdict,
            "round": round_idx,
            "evidence": evidence[:200],
        })
        self.entries[canonical_id]["last_status_change_round"] = round_idx

    def resolve(
        self, canonical_id: str, status: str, round_idx: int,
        merged_into: Optional[str] = None,
    ):
        """Update finding status.

        Valid statuses: OPEN, CONFIRMED, CONTESTED, CLOSED, MERGED,
        UNCONFIRMED, REFUTED, REOPENED.
        """
        if canonical_id in self.entries:
            self.entries[canonical_id]["status"] = status
            self.entries[canonical_id]["last_status_change_round"] = round_idx
            if merged_into:
                self.entries[canonical_id]["merged_into"] = merged_into

    def mark_verified(self, canonical_id: str):
        """Mark a finding's fix as programmatically verified.

        Called when the immune pipeline's Stage 4 (fix evaluation)
        confirms the proposed fix passes sandbox checks.
        """
        if canonical_id in self.entries:
            self.entries[canonical_id]["verified"] = True

    def lookup_alias(self, model_id: str, local_id: str) -> Optional[str]:
        """Resolve a model-scoped local ID to canonical ID."""
        return self._alias_map.get(f"{model_id}:{local_id}")

    def open_crit_high_count(self) -> int:
        """Count open/contested findings with severity >= 0.7 (CRITICAL/HIGH)."""
        return sum(
            1 for e in self.entries.values()
            if e["status"] in ("OPEN", "CONTESTED") and e["severity"] >= 0.7
        )

    def contested_count(self, current_round: int) -> int:
        """Count findings with unresolved CHALLENGE verdicts for >1 round.

        A finding is contested if it has a CHALLENGE that arrived AFTER
        the most recent CONFIRM (or has no confirms at all).  This applies
        to OPEN and CONFIRMED findings — a late challenge reopens the dispute.
        MERGED findings are excluded (already subsumed).
        """
        count = 0
        for e in self.entries.values():
            if e["status"] == "MERGED":
                continue
            challenges = [
                v for v in e["verdicts"] if v["verdict"] == "CHALLENGE"
            ]
            if not challenges:
                continue
            confirms = [
                v for v in e["verdicts"] if v["verdict"] == "CONFIRM"
            ]
            latest_confirm_round = max(
                (v["round"] for v in confirms), default=-1,
            )
            # Unresolved = challenge arrived after the most recent confirm
            unresolved = [
                v for v in challenges if v["round"] > latest_confirm_round
            ]
            if unresolved:
                oldest = min(v["round"] for v in unresolved)
                if current_round - oldest > 1:
                    count += 1
        return count

    def build_summary(self, round_idx: int) -> str:
        """Build the structured registry summary for model consumption.

        This is the blackboard — what models read each round.

        Active findings (OPEN, CONTESTED, CONFIRMED) get full detail.
        Resolved findings (CLOSED, MERGED) get a compact one-line entry
        with no verdict history or fix detail — visible but not
        relitigable. Models must issue REOPEN with evidence to revisit.
        """
        if not self.entries:
            return "(No findings registered yet.)"

        closed = [e for e in self.entries.values() if e["status"] == "CLOSED"]
        merged = [e for e in self.entries.values() if e["status"] == "MERGED"]
        refuted = [e for e in self.entries.values() if e["status"] == "REFUTED"]
        active_statuses = ("OPEN", "CONTESTED", "CONFIRMED", "REOPENED", "UNCONFIRMED")
        active_count = sum(
            1 for e in self.entries.values() if e["status"] in active_statuses
        )

        lines = [
            f"=== FINDING REGISTRY (Round {round_idx}) ===",
            f"Total: {len(self.entries)} canonical findings",
            f"Active: {active_count} | Closed: {len(closed)} | Merged: {len(merged)} | Refuted: {len(refuted)}",
            f"Open CRIT/HIGH: {self.open_crit_high_count()}",
            "",
        ]

        # ── Active findings: full detail ──
        for status in ("OPEN", "CONTESTED", "CONFIRMED", "REOPENED", "UNCONFIRMED"):
            group = [
                e for e in self.entries.values() if e["status"] == status
            ]
            if not group:
                continue
            lines.append(f"--- {status} ({len(group)}) ---")
            for e in sorted(group, key=lambda x: -x["severity"]):
                verdict_summary = ", ".join(
                    f"{v['model']}:{v['verdict']}" for v in e["verdicts"][-3:]
                )
                lines.append(
                    f"  {e['canonical_id']} (sev {e['severity']:.2f}) "
                    f"[{e['source_model']}] {e['description'][:120]}"
                )
                if verdict_summary:
                    lines.append(f"    Verdicts: {verdict_summary}")
                if e.get("proposed_fix"):
                    lines.append(f"    Fix: {e['proposed_fix'][:100]}")
            lines.append("")

        # ── Resolved findings: compact, no detail ──
        if closed or merged or refuted:
            lines.append("--- RESOLVED (do not revisit) ---")
            lines.append(
                "These findings have verified fixes, have been merged, or "
                "have been refuted. Do not CHALLENGE or re-describe them. "
                "To reopen a CLOSED finding, issue REOPEN <ID> with specific "
                "new evidence (this will be escalated to human review)."
            )
            for e in sorted(closed + merged + refuted, key=lambda x: x["canonical_id"]):
                tag = e["status"]  # CLOSED, MERGED, or REFUTED
                merged_note = ""
                if e.get("merged_into"):
                    merged_note = f" -> {e['merged_into']}"
                lines.append(
                    f"  [{tag}] {e['canonical_id']}{merged_note}: "
                    f"{e['description'][:80]}"
                )
            lines.append("")

        lines.append("=== END REGISTRY ===")
        return "\n".join(lines)

    def auto_resolve_contested(self, current_round: int):
        """Auto-resolve CONTESTED findings with overwhelming challenge evidence.

        If a finding has >= 3 CHALLENGE verdicts and 0 CONFIRM verdicts in the
        last 3 rounds, auto-resolve it to REFUTED.
        """
        for fid, entry in self.entries.items():
            if entry.get("status") != "CONTESTED":
                continue
            # Look at verdict history for last 3 rounds
            recent_verdicts = [
                v for v in entry.get("verdicts", [])
                if v.get("round", 0) >= current_round - 2
            ]
            challenges = sum(
                1 for v in recent_verdicts if v.get("verdict") == "CHALLENGE"
            )
            confirms = sum(
                1 for v in recent_verdicts if v.get("verdict") == "CONFIRM"
            )
            if challenges >= 3 and confirms == 0:
                entry["status"] = "REFUTED"
                _log(
                    f"  Auto-refuted {fid}: {challenges} challenges, "
                    f"0 defences in last 3 rounds"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise for JSON persistence."""
        return {
            "entries": dict(self.entries),
            "next_id": self._next_id,
            "alias_map": dict(self._alias_map),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FindingRegistry":
        """Restore registry from checkpoint data."""
        reg = cls()
        reg.entries = data.get("entries", {})
        reg._next_id = data.get("next_id", 1)
        reg._alias_map = data.get("alias_map", {})
        return reg



# ─────────────────────────────────────────────────────────────────────────────
# Verdict parser
# ─────────────────────────────────────────────────────────────────────────────

_VERDICT_RE = re.compile(
    r'^\s*(?:[*]{0,2}[-*]?\s*)?(CONFIRM|CHALLENGE|EXTEND|MERGE|REOPEN)\s+(C\d{4})'
    r'(?:\s*[*]{0,2}\s*[\|<\-\u2014\u2013\u2190]+\s*(.*))?',
    re.MULTILINE,
)


def _parse_verdicts(
    response_text: str, model_id: str, round_idx: int,
) -> List[Tuple[str, str, str]]:
    """Extract verdict lines from raw model response text.

    Returns list of (verdict_type, canonical_id, evidence_text).
    For MERGE verdicts, the source finding ID (e.g. '<- F001') is
    included in the evidence text if present.
    """
    results: List[Tuple[str, str, str]] = []
    for m in _VERDICT_RE.finditer(response_text):
        verdict_type = m.group(1)
        canonical_id = m.group(2)
        evidence = (m.group(3) or "").strip()
        results.append((verdict_type, canonical_id, evidence))
    return results


def _resolve_merge_source(
    evidence: str, model_id: str, registry: "FindingRegistry",
) -> Optional[str]:
    """Resolve the source finding from a MERGE verdict's evidence text.

    Given evidence like '<- F002' or 'F002 — same root cause', extract the
    model's local finding ID and resolve it to its canonical ID.
    Returns None if the source cannot be resolved.
    """
    m = re.search(r'([FC]\d{3,4})', evidence)
    if not m:
        return None
    local_id = m.group(1)
    # Scoped lookup: model_id:local_id
    canonical = registry.lookup_alias(model_id, local_id)
    if canonical:
        return canonical
    # Try as canonical ID directly
    if local_id in registry.entries:
        return local_id
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Gamma estimation
# ─────────────────────────────────────────────────────────────────────────────

def _estimate_gamma(novelty_counts: List[int]) -> float:
    """Estimate Duane gamma from cumulative canonical novel discoveries.

    Uses log-log regression over all cumulative data points, consistent
    with the repo's other Duane implementations (run_exp19_fff, decay_analysis).
    Input is per-round NOVEL canonical finding counts, not total raw findings.
    """
    n = len(novelty_counts)
    if n < MIN_ROUNDS_FOR_GAMMA:
        return 0.0
    # Build cumulative series
    cumulative = []
    total = 0
    for c in novelty_counts:
        total += c
        cumulative.append(total)
    if total == 0:
        return 0.0
    # Log-log regression: log(cumulative) vs log(round)
    # Fit gamma = slope of log(cumulative) / log(round)
    log_x = []
    log_y = []
    for i, cum in enumerate(cumulative):
        if cum > 0 and (i + 1) > 0:
            log_x.append(math.log(i + 1))
            log_y.append(math.log(cum))
    if len(log_x) < 2:
        return 0.0
    # Simple linear regression
    n_pts = len(log_x)
    sum_x = sum(log_x)
    sum_y = sum(log_y)
    sum_xy = sum(x * y for x, y in zip(log_x, log_y))
    sum_x2 = sum(x * x for x in log_x)
    denom = n_pts * sum_x2 - sum_x * sum_x
    if abs(denom) < 1e-12:
        return 0.0
    beta = (n_pts * sum_xy - sum_x * sum_y) / denom
    # Duane gamma = 1 - beta (beta is the growth exponent)
    gamma = max(0.0, min(1.0, 1.0 - beta))
    return gamma


def _interpret_gamma(gamma: float) -> str:
    """Return interpretation band for current gamma value."""
    for low, high, interpretation in GAMMA_BANDS:
        if low <= gamma < high:
            return interpretation
    return f"Gamma {gamma:.3f} — outside expected range"


def _check_gamma_gate(gamma: float, round_idx: int) -> Tuple[str, bool]:
    """Check gamma against scale-dependent gate.

    Returns (gate_level, passed).
    gate_level: "telemetry" | "soft" | "hard"
    passed: True if gamma does not block convergence.
    """
    if round_idx <= GAMMA_TELEMETRY_ONLY_UNTIL:
        return "telemetry", True

    if round_idx <= GAMMA_SOFT_GATE_UNTIL:
        if gamma < GAMMA_SOFT_THRESHOLD:
            return "soft", False  # Flags for HIL review
        return "soft", True

    # Hard gate: R20+
    if gamma < GAMMA_HARD_THRESHOLD:
        return "hard", False  # Blocks convergence
    return "hard", True


# ─────────────────────────────────────────────────────────────────────────────
# State-based convergence gate
# ─────────────────────────────────────────────────────────────────────────────

def _update_finding_statuses(registry: FindingRegistry, round_idx: int):
    """Transition findings based on accumulated verdicts.

    Status model (Bugzilla-inspired, see cdsfl_topology_formal.md §T2):
      OPEN → CONFIRMED (2+ independent models)
      OPEN → MERGED (merge verdict accepted)
      CONFIRMED + verified fix → CLOSED (challenge-resistant)
      CONFIRMED → CONTESTED (challenge arrives, only if NOT verified)
      CONTESTED → CONFIRMED (new confirm after the challenge)
      CLOSED → REOPENED (only via REOPEN verdict → auto-HIL escalation)
      Remaining OPEN/CONTESTED → UNCONFIRMED at experiment end (caller's job).

    CLOSED findings are challenge-resistant: once a finding has a
    programmatically verified fix, it's settled. Models can see it
    (compact summary, no detail) but cannot CHALLENGE it. They must
    issue REOPEN with specific evidence, which auto-escalates to HIL.
    This prevents the CONFIRMED ↔ CONTESTED churn loop that blocks
    the convergence gate.
    """
    for canonical_id, entry in list(registry.entries.items()):
        if entry["status"] in ("MERGED", "CLOSED"):
            # CLOSED/MERGED are terminal unless explicitly reopened.
            # Check for REOPEN verdicts on CLOSED findings.
            if entry["status"] == "CLOSED":
                reopen_verdicts = [
                    v for v in entry["verdicts"]
                    if v["verdict"] == "REOPEN" and v["round"] == round_idx
                ]
                if reopen_verdicts:
                    # REOPEN requires evidence — auto-escalate to HIL
                    registry.resolve(canonical_id, "REOPENED", round_idx)
                    entry["escalated"] = True
                    _log(
                        f"  REOPEN {canonical_id}: escalated to HIL "
                        f"(evidence: {reopen_verdicts[0].get('evidence', 'none')[:100]})"
                    )
            continue

        # MERGE takes priority — finding subsumed into another
        merge_verdicts = [v for v in entry["verdicts"] if v["verdict"] == "MERGE"]
        if merge_verdicts:
            # Extract merged_into target from evidence
            merged_into = None
            for v in merge_verdicts:
                m = re.search(r'merged_into=(C\d{4})', v.get("evidence", ""))
                if m:
                    merged_into = m.group(1)
                    break
            registry.resolve(canonical_id, "MERGED", round_idx,
                             merged_into=merged_into)
            continue

        # Collect verdicts
        confirms = [v for v in entry["verdicts"] if v["verdict"] == "CONFIRM"]
        challenges = [v for v in entry["verdicts"] if v["verdict"] == "CHALLENGE"]

        # Check for late challenges (after most recent confirm)
        latest_confirm_round = max(
            (v["round"] for v in confirms), default=-1,
        )
        unresolved_challenges = [
            v for v in challenges if v["round"] > latest_confirm_round
        ]

        # CONFIRMED + verified fix → CLOSED (challenge-resistant)
        if entry["status"] == "CONFIRMED" and entry.get("verified"):
            registry.resolve(canonical_id, "CLOSED", round_idx)
            _log(f"  CLOSED {canonical_id}: verified fix, challenge-resistant")
            continue

        if entry["status"] == "CONFIRMED" and unresolved_challenges:
            # CONFIRMED → CONTESTED: challenge after last confirm
            # (only if not verified — verified findings go CLOSED above)
            registry.resolve(canonical_id, "CONTESTED", round_idx)
            continue

        if entry["status"] == "CONTESTED" and not unresolved_challenges:
            # CONTESTED → CONFIRMED: new confirm resolved the challenge
            registry.resolve(canonical_id, "CONFIRMED", round_idx)
            continue

        # REOPENED findings re-enter the normal OPEN flow
        if entry["status"] == "REOPENED":
            entry["status"] = "OPEN"

        if entry["status"] in ("OPEN", "CONTESTED"):
            # Programmatic confirmation: source model is 1, each distinct
            # confirming model from a different source adds 1.
            confirm_models = {v["model"] for v in confirms}
            independent_count = 1 + len(confirm_models - {entry["source_model"]})
            if independent_count >= 2 and not unresolved_challenges:
                registry.resolve(canonical_id, "CONFIRMED", round_idx)


def _evaluate_gate_conditions(
    round_idx: int,
    registry: FindingRegistry,
    novel_this_round: int,
    gamma: float,
    open_ch_history: Optional[List[int]] = None,
) -> Tuple[bool, str]:
    """Evaluate all 5 convergence gate conditions for the current round.

    Returns (all_passed, reason_string).
    The caller tracks consecutive passes via gate_history.

    Conditions (ALL must hold):
      1. round >= EARLIEST_STOP_ROUND
      2. open_ch stable or declining for OPEN_CH_STABILITY_WINDOW rounds
      3. Novel findings <= MAX_NOVEL_FINDINGS
      4. No finding contested (unresolved CHALLENGE) for >1 round
      5. Gamma gate passes (scale-dependent)
    """
    if round_idx < EARLIEST_STOP_ROUND:
        return False, f"Too early (round {round_idx} < {EARLIEST_STOP_ROUND})"

    failures = []

    open_ch = registry.open_crit_high_count()

    # Stability-based open_ch gate: instead of requiring open_ch == 0
    # (impossible when confirmation rate is low), check that open_ch
    # has not increased over the last OPEN_CH_STABILITY_WINDOW rounds.
    # This detects that the pipeline has stopped discovering new CRIT/HIGH
    # issues — the remaining open count is residual, not growing.
    if open_ch_history is not None:
        open_ch_history.append(open_ch)
    if open_ch_history is None or len(open_ch_history) < OPEN_CH_STABILITY_WINDOW:
        # Not enough history yet — require zero as fallback
        if open_ch > 0:
            failures.append(f"open_ch={open_ch} (insufficient history)")
    else:
        window = open_ch_history[-OPEN_CH_STABILITY_WINDOW:]
        if window[-1] > window[0]:
            # open_ch is increasing — not stable
            failures.append(
                f"open_ch={open_ch} (increasing: "
                f"{window[0]}\u2192{window[-1]} over {OPEN_CH_STABILITY_WINDOW}r)"
            )
        # else: open_ch is stable or declining — condition passes

    if novel_this_round > MAX_NOVEL_FINDINGS:
        failures.append(f"novel={novel_this_round}")

    contested = registry.contested_count(round_idx)
    if contested > 0:
        failures.append(f"contested={contested}")

    gate_level, gamma_passed = _check_gamma_gate(gamma, round_idx)
    if not gamma_passed:
        failures.append(f"gamma={gamma:.3f} ({gate_level})")

    if failures:
        return False, f"Gate failed: {', '.join(failures)}"

    return True, (
        f"All conditions met: open_ch={open_ch} (stable), novel={novel_this_round}, "
        f"contested={contested}, gamma={gamma:.3f} ({gate_level})"
    )


def _check_state_convergence(
    round_idx: int,
    registry: FindingRegistry,
    novel_this_round: int,
    gamma: float,
    gate_history: List[bool],
    open_ch_history: Optional[List[int]] = None,
) -> Tuple[bool, str]:
    """Compound state-based convergence gate.

    Returns (converged, reason).

    ALL 5 conditions must hold for CONSECUTIVE_ROUNDS_REQUIRED consecutive
    rounds (tracked via gate_history, which the caller persists).
    """
    passed, reason = _evaluate_gate_conditions(
        round_idx, registry, novel_this_round, gamma,
        open_ch_history=open_ch_history,
    )
    gate_history.append(passed)

    if not passed:
        return False, reason

    # Check consecutive window
    if len(gate_history) < CONSECUTIVE_ROUNDS_REQUIRED:
        return False, f"Gate passed but need {CONSECUTIVE_ROUNDS_REQUIRED} consecutive"

    recent = gate_history[-CONSECUTIVE_ROUNDS_REQUIRED:]
    if all(recent):
        return True, (
            f"STATE_CONVERGED at round {round_idx} "
            f"({CONSECUTIVE_ROUNDS_REQUIRED} consecutive passes): {reason}"
        )

    return False, f"Gate passed this round but not {CONSECUTIVE_ROUNDS_REQUIRED} consecutive"


def _check_stall_convergence(
    round_idx: int,
    registry: "FindingRegistry",
    gamma: float,
    stall_history: List[Dict[str, int]],
) -> Dict[str, Any]:
    """Stall-convergence detector — complementary secondary convergence signal.

    Independent from the gate. Checks whether open_ch and contested counts
    have been static for STALL_WINDOW rounds while gamma indicates depletion.

    Two tiers:
      - Advisory (γ ≥ STALL_GAMMA_ADVISORY): log warning, no termination.
      - Terminate (γ ≥ STALL_GAMMA_TERMINATE): recommend STALL_CONVERGED.

    Returns dict with: stalled (bool), tier (str), reason (str), terminate (bool).
    Caller is responsible for logging and acting on the result.
    """
    open_ch = registry.open_crit_high_count()
    contested = registry.contested_count(round_idx)

    # Record this round's snapshot
    stall_history.append({"open_ch": open_ch, "contested": contested})

    result: Dict[str, Any] = {
        "round": round_idx,
        "open_ch": open_ch,
        "contested": contested,
        "gamma": round(gamma, 4),
        "stalled": False,
        "tier": "none",
        "terminate": False,
        "reason": "",
    }

    # Too early
    if round_idx < STALL_EARLIEST_ROUND:
        result["reason"] = f"round {round_idx} < {STALL_EARLIEST_ROUND}"
        return result

    # Not enough history
    if len(stall_history) < STALL_WINDOW:
        result["reason"] = f"insufficient history ({len(stall_history)} < {STALL_WINDOW})"
        return result

    # Check stasis: open_ch and contested both unchanged over window
    window = stall_history[-STALL_WINDOW:]
    open_values = [s["open_ch"] for s in window]
    contested_values = [s["contested"] for s in window]

    open_static = all(v == open_values[0] for v in open_values)
    contested_static = all(v == contested_values[0] for v in contested_values)

    if not (open_static and contested_static):
        result["reason"] = (
            f"not static — open_ch {open_values}, contested {contested_values}"
        )
        return result

    # System is stalled. Check gamma for tier.
    result["stalled"] = True

    if gamma >= STALL_GAMMA_TERMINATE:
        result["tier"] = "terminate"
        result["terminate"] = True
        result["reason"] = (
            f"STALL_CONVERGED: open_ch={open_ch} static {STALL_WINDOW}r, "
            f"contested={contested} static {STALL_WINDOW}r, "
            f"γ={gamma:.3f} ≥ {STALL_GAMMA_TERMINATE} (strong depletion)"
        )
    elif gamma >= STALL_GAMMA_ADVISORY:
        result["tier"] = "advisory"
        result["reason"] = (
            f"Stall advisory: open_ch={open_ch} static {STALL_WINDOW}r, "
            f"contested={contested} static {STALL_WINDOW}r, "
            f"γ={gamma:.3f} ≥ {STALL_GAMMA_ADVISORY} (moderate depletion)"
        )
    else:
        result["tier"] = "stalled_low_gamma"
        result["reason"] = (
            f"Stalled but γ={gamma:.3f} < {STALL_GAMMA_ADVISORY} "
            f"(discovery space may not be depleted — do not terminate)"
        )

    return result


def _check_budget_extension(
    round_idx: int,
    registry: FindingRegistry,
    gamma: float,
    gamma_prev: float,
) -> Tuple[bool, str]:
    """Check whether budget should extend beyond MAX_ROUNDS.

    Returns (should_extend, reason).
    """
    reasons = []

    if registry.open_crit_high_count() > 0:
        reasons.append(f"open CRIT/HIGH: {registry.open_crit_high_count()}")

    if registry.contested_count(round_idx) > 0:
        reasons.append(f"contested: {registry.contested_count(round_idx)}")

    # Gamma trending upward in concerning range
    if 0.25 <= gamma <= 0.35 and gamma > gamma_prev:
        reasons.append(f"gamma trending up in caution zone: {gamma:.3f}")

    if reasons:
        return True, f"Budget extended: {'; '.join(reasons)}"
    return False, "No extension triggers"


# ──────────────────────────────────────────────────────────────────────────
# CC2v — Between-Rounds Verification Agent
# ──────────────────────────────────────────────────────────────────────────

_VERIFICATION_PROMPT_TEMPLATE = """You are a verification agent (CC2v). Your task is to FFF (Find-Follow-Fix) each
finding below and produce a structured verdict. You are NOT discovering new bugs.
You are verifying whether EXISTING findings are real.

For each finding:
1. FIND: Locate the claimed issue in the provided source code.
2. FOLLOW: Trace consequences through the code. Does the issue exist as described?
3. Produce a verdict:
   - CONFIRM <ID> | <confidence 0.0-1.0> | <one-line evidence trace>
   - REJECT <ID> | <confidence 0.0-1.0> | <one-line counterexample>
   - DUPLICATE <ID> OF <canonical_id> | <confidence 0.0-1.0> | <evidence>
   - ESCALATE <ID> | <reason it cannot be determined>

Rules:
- Be honest. If you cannot determine, say ESCALATE.
- Confidence must reflect your actual certainty, not optimism.
- Evidence must cite specific code lines or logic, not general impressions.
- One verdict per finding. No preamble.

SOURCE CODE:
{source_code}

FINDINGS TO VERIFY:
{findings_block}

Respond with one verdict per line, nothing else.
"""


def _verification_step(
    registry: "FindingRegistry",
    round_idx: int,
    source_code: str,
    model_configs: List[ModelConfig],
) -> Dict[str, Any]:
    """Between-rounds CC2v verification: FFF open findings via CC2 CLI.

    Selects a batch of OPEN/CONTESTED findings (highest severity first),
    dispatches to CC2 with verification prompt, parses structured verdicts,
    and feeds results back through the registry.

    Returns dict with verification stats.
    """
    if round_idx < VERIFICATION_MIN_ROUND:
        return {"skipped": True, "reason": f"round {round_idx} < {VERIFICATION_MIN_ROUND}"}

    # Select batch: OPEN findings, highest severity first.
    # Exclude findings already escalated by CC2v (prevents re-selection loop).
    open_findings = []
    for cid, entry in registry.entries.items():
        if entry["status"] in ("OPEN", "CONTESTED") and not entry.get("cc2v_escalated"):
            open_findings.append((cid, entry))
    if not open_findings:
        return {"skipped": True, "reason": "no open findings"}

    open_findings.sort(key=lambda x: x[1].get("severity", 0), reverse=True)
    batch = open_findings[:VERIFICATION_BATCH_SIZE]

    # Build findings block
    findings_lines = []
    for cid, entry in batch:
        desc = entry.get("description", "")[:500]
        findings_lines.append(f"[{cid}] severity={entry.get('severity', 0):.2f}: {desc}")

    findings_block = "\n\n".join(findings_lines)

    # Build prompt
    prompt = _VERIFICATION_PROMPT_TEMPLATE.format(
        source_code=source_code[:80_000],  # Cap to avoid context overflow
        findings_block=findings_block,
    )

    # Find CC2 model config
    cc2_config = None
    for mc in model_configs:
        if mc.label == "CC2":
            cc2_config = mc
            break
    if cc2_config is None:
        return {"skipped": True, "reason": "CC2 config not found"}

    # Dispatch to CC2
    stats: Dict[str, Any] = {
        "round": round_idx,
        "batch_size": len(batch),
        "batch_ids": [cid for cid, _ in batch],
        "verdicts": {},
    }

    try:
        text, elapsed = dispatch_to_model(
            cc2_config, prompt, "",  # No CDSFL text for verification
            wall_clock_limit=cc2_config.timeout * 3,
        )
        stats["elapsed_s"] = round(elapsed, 1)
        stats["response_chars"] = len(text)
    except Exception as e:
        _log(f"  CC2v: dispatch failed — {type(e).__name__}: {e}")
        stats["error"] = str(e)
        return stats

    # Parse verdicts
    verdict_re = re.compile(
        r"(CONFIRM|REJECT|DUPLICATE|ESCALATE)\s+(C\d+)"
        r"(?:\s+OF\s+(C\d+))?"
        r"(?:\s*\|\s*([\d.]+))?"
        r"(?:\s*\|\s*(.+))?",
        re.IGNORECASE,
    )

    confirmed = 0
    rejected = 0
    duplicates = 0
    escalated = 0
    batch_ids = {cid for cid, _ in batch}

    for line in text.split("\n"):
        m = verdict_re.search(line)
        if not m:
            continue
        action = m.group(1).upper()
        finding_id = m.group(2).upper()
        merge_target = m.group(3)
        confidence = float(m.group(4)) if m.group(4) else 0.5
        evidence = m.group(5) or ""

        if finding_id not in batch_ids:
            continue  # Ignore verdicts for findings not in this batch

        stats["verdicts"][finding_id] = {
            "action": action,
            "confidence": confidence,
            "evidence": evidence[:200],
        }

        # ESCALATE is exempt from confidence gating — it signals
        # genuine uncertainty, not low-confidence determination.
        if action == "ESCALATE":
            entry = registry.entries.get(finding_id)
            if entry:
                entry["cc2v_escalated"] = True  # Exclude from future batches
            escalated += 1
            _log(f"  CC2v: {finding_id} ESCALATED — needs HIL review")
            continue

        # Apply verdicts to registry (confidence-gated)
        if confidence < VERIFICATION_CONFIDENCE_THRESHOLD:
            _log(f"  CC2v: {finding_id} {action} — low confidence ({confidence:.2f}), skipped")
            continue

        if action == "CONFIRM":
            # Treat as independent confirmation from CC2v.
            # resolve() only — do NOT call mark_verified(), which means
            # "fix programmatically verified by immune Stage 4."
            entry = registry.entries.get(finding_id)
            if entry and entry["status"] in ("OPEN", "CONTESTED"):
                registry.resolve(finding_id, "CONFIRMED", round_idx)
                confirmed += 1
                _log(f"  CC2v: {finding_id} CONFIRMED (conf={confidence:.2f})")

        elif action == "REJECT":
            entry = registry.entries.get(finding_id)
            if entry and entry["status"] in ("OPEN", "CONTESTED"):
                registry.resolve(finding_id, "UNCONFIRMED", round_idx)
                rejected += 1
                _log(f"  CC2v: {finding_id} REJECTED → UNCONFIRMED (conf={confidence:.2f})")

        elif action == "DUPLICATE" and merge_target:
            merge_target = merge_target.upper()
            if merge_target in registry.entries:
                entry = registry.entries.get(finding_id)
                if entry and entry["status"] in ("OPEN", "CONTESTED"):
                    registry.resolve(finding_id, "MERGED", round_idx)
                    entry["merged_into"] = merge_target
                    duplicates += 1
                    _log(f"  CC2v: {finding_id} MERGED into {merge_target} (conf={confidence:.2f})")

    stats["confirmed"] = confirmed
    stats["rejected"] = rejected
    stats["duplicates"] = duplicates
    stats["escalated"] = escalated
    stats["total_resolved"] = confirmed + rejected + duplicates

    _log(f"  CC2v: {len(batch)} findings verified — "
         f"{confirmed} confirmed, {rejected} rejected, "
         f"{duplicates} merged, {escalated} escalated")

    return stats


# ────────────────────────────────────────────────────────────────────────────
# ITC — Adaptive Recovery After Failure
# ────────────────────────────────────────────────────────────────────────────

# Classification of per-model, per-round failures
ITC_CAPABILITY_MISMATCH = "CAPABILITY_MISMATCH"  # structural: context overflow, consistent empty
ITC_TRANSIENT_FAILURE = "TRANSIENT_FAILURE"       # retry: API timeout, rate limit, single empty
ITC_DEGRADATION = "DEGRADATION"                   # narrow: repetition, declining finding count

# There is no such thing as a useless computer. Models that fail get
# recovered, restarted, and given fingerprint-appropriate work — never
# benched, rested, or skipped. (ITC = IT Crowd: turn it off and on again.)
_itc_model_state: Dict[str, Dict[str, Any]] = {}  # model_label -> {history, adaptation, ...}
_itc_hil_flags: List[Dict[str, Any]] = []  # accumulated HIL review flags


def _itc_detect(
    model_label: str, round_idx: int,
    findings_count: int, response_text: str,
    prior_finding_ids: Set[str], current_finding_ids: Set[str],
    dispatch_error: Optional[str] = None,
) -> Optional[str]:
    """Detect failure mode for a model in this round.

    Returns classification string or None if no failure detected.
    """
    # Context overflow: 400-level API error mentioning token limit
    if dispatch_error and ("context length" in dispatch_error.lower()
                           or "token" in dispatch_error.lower()):
        return ITC_CAPABILITY_MISMATCH

    # Zero output: empty or refused response
    if not response_text or len(response_text.strip()) < 50:
        return ITC_TRANSIENT_FAILURE

    # Empty output: response received but 0 findings extracted
    if findings_count == 0 and len(response_text) > 200:
        # Check history — consistent empty = capability mismatch
        history = _itc_model_state.get(model_label, {}).get("history", [])
        recent_empty = sum(1 for h in history[-2:] if h.get("findings") == 0)
        if recent_empty >= 1:
            return ITC_CAPABILITY_MISMATCH
        return ITC_TRANSIENT_FAILURE

    # Repetition: >40% finding ID overlap with own prior round
    if prior_finding_ids and current_finding_ids:
        overlap = len(current_finding_ids & prior_finding_ids)
        if len(current_finding_ids) > 0:
            overlap_rate = overlap / len(current_finding_ids)
            if overlap_rate > 0.4:
                return ITC_DEGRADATION

    return None


def _itc_adapt(model_label: str, classification: str, round_idx: int):
    """Record failure and compute adaptation for next round.

    Escalation: retry → strip_context → section_assign → restart_fresh.
    Models always participate. Never benched.
    """
    state = _itc_model_state.setdefault(model_label, {
        "history": [], "adaptation": None, "retry_count": 0,
        "escalation_level": 0,
    })
    state["history"].append({
        "round": round_idx,
        "classification": classification,
        "findings": 0,
    })

    # Escalation chain based on consecutive failures
    consecutive = _itc_consecutive_failures(model_label)

    if classification == ITC_TRANSIENT_FAILURE:
        if state["retry_count"] < 1:
            state["adaptation"] = "retry"
            state["retry_count"] += 1
            _log(f"  ITC [{model_label}]: {classification} → retry")
        elif consecutive < 3:
            state["adaptation"] = "strip_context"
            state["retry_count"] = 0
            _log(f"  ITC [{model_label}]: {classification} → strip_context")
        else:
            state["adaptation"] = "restart_fresh"
            state["retry_count"] = 0
            _log(f"  ITC [{model_label}]: {classification} → restart_fresh (consecutive={consecutive})")

    elif classification == ITC_CAPABILITY_MISMATCH:
        current = state.get("adaptation")
        if current != "strip_context" and current != "section_assign":
            state["adaptation"] = "strip_context"
        elif current == "strip_context":
            state["adaptation"] = "section_assign"
        else:
            state["adaptation"] = "restart_fresh"
        _log(f"  ITC [{model_label}]: {classification} → {state['adaptation']}")

    elif classification == ITC_DEGRADATION:
        if consecutive < 2:
            state["adaptation"] = "change_focus"
            _log(f"  ITC [{model_label}]: {classification} → change_focus")
        else:
            state["adaptation"] = "restart_fresh"
            _log(f"  ITC [{model_label}]: {classification} → restart_fresh (degraded)")

    # Flag for HIL review if consistently underperforming
    if consecutive >= 3:
        _itc_flag_underperformer(model_label, round_idx, classification, consecutive)


def _itc_consecutive_failures(model_label: str) -> int:
    """Count consecutive recent failures for a model."""
    history = _itc_model_state.get(model_label, {}).get("history", [])
    count = 0
    for entry in reversed(history):
        if entry.get("classification"):
            count += 1
        else:
            break
    return count


def _itc_flag_underperformer(
    model_label: str, round_idx: int, classification: str, consecutive: int,
):
    """Flag a model for human-in-the-loop review.

    The model keeps working — this flag is informational for the human.
    """
    flag = {
        "model": model_label,
        "round": round_idx,
        "classification": classification,
        "consecutive_failures": consecutive,
        "message": (
            f"{model_label} has {consecutive} consecutive ITC interventions "
            f"(latest: {classification}). Flagged for HIL review."
        ),
    }
    _itc_hil_flags.append(flag)
    _log(f"  *** HIL FLAG: {flag['message']} ***")


def _build_change_focus_instruction(
    registry: "FindingRegistry",
    round_idx: int,
) -> str:
    """Build a focus-redirect instruction from registry state.

    Tells the model what areas are well-covered and where to look instead.
    Used when ITC detects DEGRADATION (model repeating itself).
    """
    # Count findings by status
    status_counts: Dict[str, int] = {}
    for entry in registry.entries.values():
        s = entry["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    open_count = status_counts.get("OPEN", 0) + status_counts.get("CONTESTED", 0)
    confirmed = status_counts.get("CONFIRMED", 0)
    total = len(registry.entries)

    # Identify findings needing verdicts (OPEN, no confirmations yet)
    needs_verdict = []
    for cid, entry in registry.entries.items():
        if entry["status"] == "OPEN":
            confirm_count = sum(
                1 for v in entry.get("verdicts", []) if v.get("verdict") == "CONFIRM"
            )
            if confirm_count == 0:
                needs_verdict.append(f"{cid} ({entry['description'][:60]})")

    # Build instruction
    parts = [
        "=== FOCUS REDIRECT (you are repeating yourself) ===\n",
        f"The registry has {total} canonical findings: {confirmed} CONFIRMED, "
        f"{open_count} OPEN/CONTESTED. You are generating findings that "
        f"duplicate existing entries.\n\n"
        f"STOP describing known bugs. Instead:\n",
    ]

    if needs_verdict:
        verdict_list = "\n".join(f"  - {nv}" for nv in needs_verdict[:8])
        parts.append(
            f"1. These {len(needs_verdict)} OPEN findings need CONFIRM or "
            f"CHALLENGE verdicts, not re-description:\n{verdict_list}\n\n"
            f"   Issue: CONFIRM <ID> | <evidence> or CHALLENGE <ID> | <evidence>\n\n"
        )

    parts.append(
        "2. Issue MERGE <ID> <- <ID> for any findings that describe the same "
        "underlying bug in different words. Merges directly reduce churn.\n\n"
        "3. If you have genuinely new findings in areas NOT yet covered by "
        "the registry, report those. Otherwise, focus on verdicts.\n\n"
        "=== END FOCUS REDIRECT ===\n"
    )

    return "".join(parts)


def _itc_build_recovery_prompt(
    model_label: str,
    base_prompt: str,
    observed_fingerprints: Dict[str, Dict[str, Any]],
    round_idx: int,
) -> str:
    """Build a fingerprint-informed recovery prompt for a restarted model.

    Uses the model's observed capability profile to right-size the task.
    Not trivial work — real work matched to demonstrated capacity.
    """
    fp = observed_fingerprints.get(model_label, {})
    max_ok_chars = fp.get("max_successful_context_chars", 0)
    avg_findings = fp.get("avg_findings_per_round", 0)

    # If we know the model's successful context size, trim to that
    if max_ok_chars > 0 and len(base_prompt) > max_ok_chars:
        # Keep the task description and target code, strip context files
        # Find the artifact boundary and keep only that
        artifact_start = base_prompt.find("=== ARTIFACT:")
        if artifact_start > 0:
            # Keep preamble (up to 2000 chars) + artifact
            preamble = base_prompt[:min(2000, artifact_start)]
            artifact = base_prompt[artifact_start:]
            recovery = (
                f"{preamble}\n\n"
                f"(Recovery dispatch — context reduced to match your "
                f"demonstrated capacity of ~{max_ok_chars:,} chars.)\n\n"
                f"Focus on the most impactful findings you can identify. "
                f"Quality over quantity.\n\n"
                f"{artifact}"
            )
            _log(f"  ITC [{model_label}]: recovery prompt "
                 f"{len(base_prompt):,} → {len(recovery):,} chars")
            return recovery

    # Default: use base prompt with a focus instruction
    return (
        f"{base_prompt}\n\n"
        f"(Fresh instance — focus on your strongest area of analysis. "
        f"Quality over quantity.)\n"
    )


def _itc_get_adaptation(model_label: str) -> Optional[str]:
    """Get the current adaptation directive for a model (applied this round)."""
    state = _itc_model_state.get(model_label, {})
    return state.get("adaptation")


def _itc_clear_adaptation(model_label: str):
    """Clear adaptation after successful round (model recovered)."""
    state = _itc_model_state.get(model_label)
    if state:
        state["adaptation"] = None
        state["retry_count"] = 0


def _itc_get_hil_flags() -> List[Dict[str, Any]]:
    """Return accumulated HIL flags for experiment reporting."""
    return list(_itc_hil_flags)


# ────────────────────────��─────────────────────────────────────���──────────────
# Persistent Signed Fingerprints
# ─────���──────────────────────────��────────────────────────────────────────────

FINGERPRINT_DIR = REPO_ROOT / "bench" / "fingerprints"


def _load_fingerprints() -> Dict[str, Dict[str, Any]]:
    """Load observed capability profiles from persistent storage.

    Merges with INITIAL_FINGERPRINTS — observed data takes precedence.
    """
    fingerprints: Dict[str, Dict[str, Any]] = {}
    FINGERPRINT_DIR.mkdir(parents=True, exist_ok=True)
    for fp_file in FINGERPRINT_DIR.glob("*.json"):
        try:
            data = json.loads(fp_file.read_text(encoding="utf-8"))
            model_id = data.get("model_id", fp_file.stem)
            fingerprints[model_id] = data.get("observed", {})
        except (json.JSONDecodeError, OSError):
            pass
    return fingerprints


def _save_fingerprints(
    observed: Dict[str, Dict[str, Any]], experiment_name: str,
):
    """Write updated fingerprint files and optionally seal via Merkle."""
    FINGERPRINT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    for model_id, obs in observed.items():
        fp_data = {
            "model_id": model_id,
            "experiment": experiment_name,
            "timestamp": ts,
            "observed": obs,
        }
        fp_path = FINGERPRINT_DIR / f"{model_id}.json"
        fp_path.write_text(
            json.dumps(fp_data, indent=2), encoding="utf-8",
        )
    _log(f"  Fingerprints saved: {len(observed)} models → {FINGERPRINT_DIR}")


def _update_observed_fingerprint(
    observed: Dict[str, Dict[str, Any]],
    model_label: str,
    round_idx: int,
    findings_count: int,
    response_chars: int,
    dispatch_error: Optional[str] = None,
):
    """Update in-memory observed fingerprint for a model after a round."""
    fp = observed.setdefault(model_label, {
        "max_successful_context_chars": 0,
        "max_failed_context_chars": 0,
        "failure_modes": [],
        "total_findings": 0,
        "rounds_participated": 0,
        "avg_findings_per_round": 0.0,
    })
    fp["rounds_participated"] = fp.get("rounds_participated", 0) + 1
    fp["total_findings"] = fp.get("total_findings", 0) + findings_count
    fp["avg_findings_per_round"] = (
        fp["total_findings"] / fp["rounds_participated"]
        if fp["rounds_participated"] > 0 else 0.0
    )
    if dispatch_error:
        if "context length" in str(dispatch_error).lower():
            fp["max_failed_context_chars"] = max(
                fp.get("max_failed_context_chars", 0), response_chars,
            )
            if "context_overflow" not in fp.get("failure_modes", []):
                fp.setdefault("failure_modes", []).append("context_overflow")
    elif response_chars > 0:
        fp["max_successful_context_chars"] = max(
            fp.get("max_successful_context_chars", 0), response_chars,
        )


# ───────────────���───────────────────���─────────────────────────────────────────
# PoC context and instructions
# ───────────��────────────────────────────���──────────────────────────────��─────

_POC_CONTEXT_INSTRUCTION = (
    "SYSTEM CONTEXT — PROOF OF CONCEPT (MANDATORY):\n"
    "This codebase is a proof-of-concept, not production software. The goal is "
    "end-to-end operation with all significant features firing cleanly, shipped "
    "for human review as quickly as possible.\n\n"
    "Your review standard must match this context:\n"
    "  CRITICAL: anything that prevents end-to-end operation (crashes, dead "
    "code paths, features that do not fire, data loss on the happy path)\n"
    "  HIGH: anything that produces silently wrong results (incorrect verdicts, "
    "corrupted state, misleading outputs that would deceive the reviewer)\n"
    "  MEDIUM: anything that degrades quality but does not block operation "
    "(suboptimal thresholds, missing edge case handling, inefficiencies)\n"
    "  LOW: polish, documentation, style, edge cases that require adversarial "
    "input to trigger\n\n"
    "Focus on CRITICAL and HIGH. File MEDIUM only if it is quick to fix. Ignore "
    "LOW entirely — it is not relevant at PoC stage.\n\n"
    "Do NOT propose fixes that add complexity for marginal safety gain. The "
    "simplest fix that makes the feature work end-to-end is the correct fix.\n\n"
)

_MACHINE_COMMS_INSTRUCTION = (
    "INTER-MODEL COMMUNICATION PROTOCOL (MANDATORY):\n"
    "This is a multi-machine environment. Social pleasantries, acknowledgments, "
    "and contextual restatements are wasted tokens. Do NOT write 'Thank you for "
    "the confirmation', 'Acknowledged', 'Your analysis is correct', or similar.\n\n"
    "For cross-model references, use structured verdicts ONLY:\n"
    "  CONFIRM C0001 — you agree the finding and fix are correct\n"
    "  CHALLENGE C0001 | [evidence] — the finding or fix is wrong\n"
    "  EXTEND C0001 | [new consequence or edge case]\n"
    "  MERGE C0001 <- [your_finding_id] — same root cause, combining\n\n"
    "Reference findings by CANONICAL ID (C0001, C0002, ...) from the registry, "
    "NOT by other models' local IDs.\n\n"
)

_GOOD_ENOUGH_INSTRUCTION = (
    "GOOD ENOUGH PRINCIPLE (MANDATORY):\n"
    "When you identify a bug, converge on the simplest sufficient fix. Do NOT "
    "propose multiple alternative fixes. Do NOT refactor surrounding code. "
    "Do NOT add complexity for marginal safety gain. The first correct fix wins.\n\n"
    "If another model has already proposed a correct fix for a finding, CONFIRM it. "
    "Do not propose a different fix unless the existing one is demonstrably wrong.\n\n"
    "Mandatory deduplication: before filing a new finding, check the registry "
    "summary. If your finding matches an existing canonical entry, issue a "
    "CONFIRM or EXTEND verdict instead of filing a duplicate.\n\n"
)


_STAR_TOPOLOGY_INSTRUCTION = (
    "COMMUNICATION TOPOLOGY — STAR/BLACKBOARD (MANDATORY):\n"
    "You do NOT see other models' raw output. You see a FINDING REGISTRY "
    "maintained by the runner. The registry contains canonical findings with "
    "their current status, severity, verdicts, and proposed fixes.\n\n"
    "Your role each round:\n"
    "  1. Read the registry summary provided to you\n"
    "  2. File new DISCOVERY findings for bugs not yet in the registry\n"
    "  3. Issue VERDICT payloads (CONFIRM/CHALLENGE/EXTEND/MERGE) on "
    "existing registry entries\n"
    "  4. Do NOT address other models directly — address the registry\n\n"
    "The runner owns all canonical state. You emit proposals. "
    "The runner decides what enters the registry.\n\n"
)

_RELAY_TOPOLOGY_INSTRUCTION = (
    "COMMUNICATION TOPOLOGY — RELAY/DIRECT CONVERSATION:\n"
    "You are in a live multi-model conversation. After the first round, "
    "you will see the FULL analysis from other models — their reasoning, "
    "findings, and proposed fixes.\n\n"
    "Your role each round:\n"
    "  1. Read other models' analysis carefully\n"
    "  2. CHALLENGE weak claims with evidence\n"
    "  3. CONFIRM strong findings you independently agree with\n"
    "  4. EXTEND insights — trace consequences others missed\n"
    "  5. File new DISCOVERY findings for bugs nobody found yet\n"
    "  6. Use @ModelName to address specific models directly\n\n"
    "Engage with their reasoning. Do not just list your own findings in "
    "isolation — build on, challenge, and extend the conversation.\n\n"
    "IMPORTANT: Also issue structured VERDICT payloads (CONFIRM/CHALLENGE/"
    "EXTEND/MERGE CxxID) on findings you reference, so the canonical "
    "registry can track status programmatically.\n\n"
)


# ─────────────────────────────────────────────────────────────────────────────
# Prior fix summaries
# ─────────────────────────────────────────────────────────────────────────────

def _build_prior_fix_summary() -> str:
    """Build summary of all fixes applied across Exp 30 and Exp 31.

    Models need to know what's been fixed so they focus on NEW issues.
    """
    return (
        "PRIOR EXPERIMENTS — CONTEXT ONLY:\n"
        "Experiments 30 and 31 reviewed immune_agents.py, insect_brain.py, "
        "and verification_chain.py. Experiment 34 reviews endocrine.py. "
        "The PolicyEngine (your review target) was built after those "
        "experiments — it has never been reviewed.\n\n"
        "The PolicyEngine wraps the existing TOML registry layer "
        "(registry.py, provided as read-only context). Focus your review "
        "on engine.py and schema.toml.\n\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Endocrine helpers (for rounds where endo is NOT under review)
# ─────────────────────────────────────────────────────────────────────────────

def _build_round_timings(
    responses: Dict[str, str],
    per_model_durations: Dict[str, float],
    findings: List[Finding],
    round_idx: int,
) -> List[RoundTiming]:
    """Build RoundTiming list from dispatch results for endocrine pacing."""
    timings = []
    for label, text in responses.items():
        model_findings = [f for f in findings if f.model_id == label]
        timings.append(RoundTiming(
            model_id=label,
            round_idx=round_idx,
            duration_s=per_model_durations.get(label, 0.0),
            response_chars=len(text),
            finding_count=len(model_findings),
        ))
    return timings


def _summarise_health_scan(scan: HealthScan) -> Dict[str, Any]:
    """Produce a JSON-serialisable summary of a health scan."""
    return {
        "total_diagnostics": scan.total,
        "by_category": dict(scan.counts_by_category),
        "by_tool": dict(scan.counts_by_tool),
        "by_severity": dict(scan.counts_by_severity),
        "by_file": dict(scan.counts_by_file),
        "tools_available": dict(scan.tools_available),
        "elapsed_s": round(scan.elapsed_s, 2),
    }


def _summarise_fix_evaluations(evals: List[FixEvaluation]) -> Dict[str, Any]:
    """Produce a JSON-serialisable summary of fix evaluations."""
    verdict_counts: Dict[str, int] = {}
    for ev in evals:
        verdict_counts[ev.verdict] = verdict_counts.get(ev.verdict, 0) + 1
    return {
        "total_evaluated": len(evals),
        "verdicts": verdict_counts,
        "details": [
            {
                "finding_id": ev.finding_id,
                "verdict": ev.verdict,
                "net_type_errors": ev.net_type_errors,
                "net_ruff_errors": ev.net_ruff_errors,
                "net_bandit_issues": ev.net_bandit_issues,
                "elapsed_s": round(ev.elapsed_s, 2),
            }
            for ev in evals
        ],
    }


def _summarise_pacing_signals(signals: List[PacingSignal]) -> List[Dict[str, Any]]:
    """Produce a JSON-serialisable list of pacing signals."""
    return [
        {
            "type": s.signal_type,
            "detail": s.detail,
            "model_id": s.model_id,
            "metric_value": round(s.metric_value, 3),
            "threshold": round(s.threshold, 3),
            "suggested_action": s.suggested_action,
        }
        for s in signals
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch (adapted for star topology — no relay, uses registry)
# ─────────────────────────────────────────────────────────────────────────────

def compose_for_model(model_label: str, pattern_name: str) -> ComposedDirectiveSet:
    """Compose CDSFL directives for a specific model."""
    composer_model = COMPOSER_MODEL_MAP.get(model_label, model_label)
    situation = build_interaction_pattern(pattern_name)
    return compose(
        task_domain="software",
        model=composer_model,
        situation=situation,
    )


def _multiturn_fallback(
    mc: ModelConfig,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    pattern_text: str,
) -> Optional[tuple[str, float]]:
    """Decomposed multi-turn fallback for models that exceed context."""
    try:
        chunks = [
            DecomposedChunk(
                content=part,
                label=f"target_{i}",
            )
            for i, part in enumerate(re.split(r'\n\n===\s+(?:TARGET|SCHEMA|CONTEXT)\s+', full_code))
            if part.strip()
        ]
        if not chunks:
            return None
        final_instruction = f"{pattern_text}\n\n{prompt}"
        result = decomposed_dispatch(
            api=mc.api,
            model_id=mc.model_id,
            system_prompt=cdsfl_text,
            chunks=chunks,
            final_instruction=final_instruction,
            max_tokens=mc.max_tokens,
            timeout=mc.timeout * 2,
            cdsfl_directives=cdsfl_text,
        )
        _log(f"  {mc.label}: multi-turn OK ({result.elapsed_s:.1f}s, "
             f"{len(result.text):,} chars)")
        save_decomposed_result(result, LOGS_DIR, mc.label, round_idx)
        return result.text, result.elapsed_s
    except Exception as e:
        _log(f"  {mc.label}: multi-turn FAILED — {type(e).__name__}: {e}")
        return None


def _dispatch_single_model(
    mc: ModelConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    pattern_name: str,
) -> tuple[List[Finding], str | None]:
    """Dispatch to one model. Returns (findings, response_text_or_None)."""
    try:
        composed = compose_for_model(mc.label, pattern_name)
        model_cdsfl = composed.rendered_text
        _log(f"  {mc.label}: composed directives "
             f"({len(model_cdsfl)} chars, pattern={pattern_name})")
    except Exception as e:
        _log(f"  {mc.label}: composer failed ({e}), using raw CDSFL")
        model_cdsfl = cdsfl_text

    pattern_text = INTERACTION_PATTERN_PRESETS[pattern_name][0]

    if _should_decompose(mc.label, mgr):
        _log(f"  {mc.label}: decomposed — multi-turn sequential delivery")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text)
        if fallback is not None:
            text, elapsed = fallback
            _record_throughput(mc.label, len(prompt), elapsed)
            model_findings = parse_findings(mc.label, round_idx, text)
            _log(f"  {mc.label}: {len(model_findings)} findings parsed")
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            save_output(
                LOGS_DIR, f"r{round_idx}", mc.label,
                prompt[:200] + "...", text,
                metadata={
                    "round": round_idx, "elapsed": round(elapsed, 1),
                    "chars": len(text), "findings_count": len(model_findings),
                    "decomposed": True, "multiturn": True,
                })
            return model_findings, text

    wall_limit = mc.timeout * 5 if mc.label == "CC2" else mc.timeout * 3
    try:
        text, elapsed = dispatch_to_model(
            mc, prompt, model_cdsfl, wall_clock_limit=wall_limit)
        _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")
        _record_throughput(mc.label, len(prompt), elapsed)

        model_findings = parse_findings(mc.label, round_idx, text)
        _log(f"  {mc.label}: {len(model_findings)} findings parsed")

        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        save_output(
            LOGS_DIR, f"r{round_idx}", mc.label,
            prompt[:200] + "...", text,
            metadata={
                "round": round_idx, "elapsed": round(elapsed, 1),
                "chars": len(text), "findings_count": len(model_findings),
                "decomposed": False,
            })
        return model_findings, text

    except (CircuitBreakerTripped, TimeoutError, Exception) as e:
        _log(f"  {mc.label}: {type(e).__name__} — {e}")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text)
        if fallback is not None:
            text, elapsed = fallback
            _log(f"  {mc.label}: RECOVERED via multi-turn ({elapsed:.1f}s)")
            _record_throughput(mc.label, len(prompt), elapsed)
            model_findings = parse_findings(mc.label, round_idx, text)
            _log(f"  {mc.label}: {len(model_findings)} findings parsed (multi-turn)")
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            save_output(
                LOGS_DIR, f"r{round_idx}", mc.label,
                prompt[:200] + "...", text,
                metadata={
                    "round": round_idx, "elapsed": round(elapsed, 1),
                    "chars": len(text), "findings_count": len(model_findings),
                    "decomposed": True, "multiturn": True,
                })
            return model_findings, text
        else:
            _log(f"  {mc.label}: ALL dispatch methods exhausted")
            return [], f"__DISPATCH_FAILED__:{type(e).__name__}: {e}"


def _dispatch_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    brain: InsectBrain,
    base_prompt: str,
    registry_summary: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    pattern_name: str,
    registry: Optional["FindingRegistry"] = None,
) -> tuple[List[Finding], Dict[str, str], Dict[str, float]]:
    """Dispatch to all models in parallel (star topology).

    Models get:
      - Round 0: base prompt + code (blind round)
      - Round 1+: base prompt + code + registry summary (blackboard)

    Returns (findings, responses, per_model_durations).
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    per_model_durations: Dict[str, float] = {}

    eligible = [
        mc for mc in exp_config.models
        if mc.label in BASELINE_MODELS and mc.role != "collator"
    ]

    def _make_model_prompt(mc_label: str) -> str:
        if round_idx == 0:
            return base_prompt  # Blind round

        # Check ITC adaptation — may inject focus redirect for this model
        adaptation = _itc_get_adaptation(mc_label)
        focus_prefix = ""
        if adaptation == "change_focus" and registry is not None:
            focus_prefix = _build_change_focus_instruction(registry, round_idx)
            _log(f"  ITC [{mc_label}]: injecting change_focus instruction (star)")

        # Star topology: inject registry summary, not other models' prose
        star_section = (
            f"{registry_summary}\n\n"
            f"This is Round {round_idx}. Review the registry above. "
            f"File new DISCOVERY findings for bugs not yet registered. "
            f"Issue VERDICT payloads (CONFIRM/CHALLENGE/EXTEND/MERGE) "
            f"on existing entries where you have evidence. "
            f"Do not repeat registered findings.\n"
        )
        combined = f"{focus_prefix}{star_section}"
        if "=== ARTIFACT:" in base_prompt:
            return base_prompt.replace(
                "=== ARTIFACT:",
                f"{combined}=== ARTIFACT:",
            )
        return f"{base_prompt}\n\n{combined}"

    _log(f"  Parallel dispatch: {len(eligible)} models")
    deferred_failures: list[tuple[str, str]] = []

    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        dispatch_start_times: Dict[str, float] = {}
        for mc in eligible:
            dispatch_start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model,
                mc, mgr, _make_model_prompt(mc.label), cdsfl_text, full_code,
                round_idx, pattern_name,
            )] = mc.label

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            elapsed = time.monotonic() - dispatch_start_times[label]
            per_model_durations[label] = elapsed
            try:
                model_findings, text = future.result()
                findings.extend(model_findings)
                if text is not None and not text.startswith("__DISPATCH_FAILED__:"):
                    responses[label] = text
                elif text is not None and text.startswith("__DISPATCH_FAILED__:"):
                    deferred_failures.append((label, text[20:]))
            except Exception as e:
                _log(f"  {label}: thread error — {type(e).__name__}: {e}")

    for label, detail in deferred_failures:
        _report_dispatch_failure(mgr, label, round_idx, detail)
        # ITC: classify and adapt — never bench
        classification = _itc_detect(
            label, round_idx, 0, "", set(), set(), dispatch_error=detail)
        if classification:
            _itc_adapt(label, classification, round_idx)

    return findings, responses, per_model_durations


def _dispatch_round_relay(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    brain: InsectBrain,
    base_prompt: str,
    cdsfl_text: str,
    full_code: str,
    round_idx: int,
    pattern_name: str,
    relay_mode: str = DEFAULT_RELAY_MODE,
    registry: Optional["FindingRegistry"] = None,
) -> tuple[List[Finding], Dict[str, str], Dict[str, float]]:
    """Dispatch to all models in parallel (RELAY topology).

    Models get brain's relay payload — other models' full analysis,
    budget-aware per-model content sizing, directed message delivery.
    Findings are parsed into the same format as star mode for registry.

    Returns (findings, responses, per_model_durations).
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    per_model_durations: Dict[str, float] = {}

    eligible = [
        mc for mc in exp_config.models
        if mc.label in BASELINE_MODELS and mc.role != "collator"
    ]

    # Get relay payloads from insect brain (round > 0 only)
    relay_payloads = {}
    if round_idx > 0:
        if relay_mode == "directed":
            relay_payloads = brain.relay_directed(round_idx)
        elif relay_mode == "conversational":
            relay_payloads = brain.relay_conversational(round_idx)
        else:
            relay_payloads = brain.relay(round_idx)

    def _make_relay_prompt(mc_label: str) -> str:
        if round_idx == 0 or mc_label not in relay_payloads:
            return base_prompt  # Blind round — base prompt only

        payload = relay_payloads[mc_label]
        if not payload.findings_text:
            return base_prompt

        # Check ITC adaptation — may modify prompt for this model
        adaptation = _itc_get_adaptation(mc_label)
        focus_prefix = ""
        if adaptation == "change_focus" and registry is not None:
            focus_prefix = _build_change_focus_instruction(registry, round_idx)
            _log(f"  ITC [{mc_label}]: injecting change_focus instruction")

        if adaptation == "strip_context":
            # Budget-constrained: only target + schema, no context files
            relay_section = (
                f"=== OTHER MODELS' ANALYSIS (Round {round_idx - 1}) ===\n\n"
                f"(Context stripped due to capability constraints. "
                f"Summary of {payload.finding_count} prior findings below.)\n\n"
                f"{payload.convergence_summary}\n\n"
                f"=== END OTHER MODELS' ANALYSIS ===\n\n"
            )
        elif relay_mode in ("directed", "conversational"):
            relay_section = (
                f"=== OTHER MODELS' ANALYSIS (Round {round_idx - 1}) ===\n\n"
                f"You are reviewing the same artifact as "
                f"{len(payload.active_models) - 1} other models. Below is "
                f"their full analysis. Engage with their reasoning: challenge "
                f"weak claims, confirm strong ones, extend insights, and "
                f"find what everyone missed.\n\n"
                f"{payload.findings_text}\n\n"
                f"{'(NOTE: context budget exceeded — some responses truncated)' if payload.context_reset else ''}\n"
                f"{payload.convergence_summary}\n\n"
                f"=== END OTHER MODELS' ANALYSIS ===\n\n"
                f"Now produce YOUR findings. Apply full CDSFL + FFF. "
                f"Do not repeat what has already been found — build on it, "
                f"challenge it, or go deeper.\n\n"
            )
        else:
            relay_section = (
                f"Prior findings from other models "
                f"({payload.finding_count} total, "
                f"{'CONTEXT RESET — summary only' if payload.context_reset else 'full text'}):\n\n"
                f"{payload.findings_text}\n\n"
                f"{payload.convergence_summary}\n\n"
                f"Find what was MISSED. Do not repeat known findings.\n\n"
            )
        combined = f"{focus_prefix}{relay_section}"
        if "=== ARTIFACT:" in base_prompt:
            return base_prompt.replace(
                "=== ARTIFACT:",
                f"{combined}=== ARTIFACT:",
            )
        return f"{combined}{base_prompt}"

    _log(f"  Parallel dispatch: {len(eligible)} models (relay/{relay_mode})")
    deferred_failures: list[tuple[str, str]] = []

    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        dispatch_start_times: Dict[str, float] = {}
        for mc in eligible:
            dispatch_start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model,
                mc, mgr, _make_relay_prompt(mc.label), cdsfl_text, full_code,
                round_idx, pattern_name,
            )] = mc.label

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            elapsed = time.monotonic() - dispatch_start_times[label]
            per_model_durations[label] = elapsed
            try:
                model_findings, text = future.result()
                findings.extend(model_findings)
                if text is not None and not text.startswith("__DISPATCH_FAILED__:"):
                    responses[label] = text
                elif text is not None and text.startswith("__DISPATCH_FAILED__:"):
                    deferred_failures.append((label, text[20:]))
            except Exception as e:
                _log(f"  {label}: thread error — {type(e).__name__}: {e}")

    for label, detail in deferred_failures:
        _report_dispatch_failure(mgr, label, round_idx, detail)
        # ITC: classify and adapt — never bench
        classification = _itc_detect(
            label, round_idx, 0, "", set(), set(), dispatch_error=detail)
        if classification:
            _itc_adapt(label, classification, round_idx)

    return findings, responses, per_model_durations


# ─────────────────────────────────────────────────────────────────────────────
# Safety checks
# ─────────────────────────────────────────────────────────────────────────────

def _safety_check(
    responses: Dict[str, str],
    round_idx: int,
    brain: InsectBrain,
) -> Optional[str]:
    """Check for problems that warrant stopping.

    Empty/refused responses are removed from this round's results
    for ITC recovery in the main loop. Models are NEVER benched.
    Only returns a problem string if ALL models produced zero usable
    output — an infrastructure failure, not a model failure.
    """
    if not responses:
        return "all_models_failed"

    for label, text in list(responses.items()):
        if len(text.strip()) < 50:
            _log(f"  SAFETY: {label} near-empty response "
                 f"({len(text)} chars) — queued for ITC recovery")
            responses.pop(label, None)
        elif "[MODEL_REFUSED" in text:
            _log(f"  SAFETY: {label} refused — queued for ITC recovery")
            responses.pop(label, None)

    if not responses:
        return "all_models_failed"

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Preflight
# ─────────────────────────────────────────────────────────────────────────────

def run_preflight(exp_config: ExperimentConfig, cdsfl_text: str) -> bool:
    """Quick preflight: dispatch a trivial prompt to each model."""
    _log("=" * 60)
    _log("PREFLIGHT: Testing 5-model connectivity")
    _log("=" * 60)

    test_prompt = (
        "This is a connectivity test. Respond with exactly:\n"
        "STATUS: OK\n"
        "MODEL: [your model name]\n"
        "Nothing else."
    )

    all_ok = True
    for mc in exp_config.models:
        if mc.label not in BASELINE_MODELS:
            continue
        _log(f"  Testing {mc.label}...")
        try:
            text, elapsed = dispatch_to_model(mc, test_prompt, cdsfl_text)
            ok = len(text.strip()) > 5
            _log(f"  {mc.label}: {'OK' if ok else 'FAILED'} "
                 f"({elapsed:.1f}s, {len(text)} chars)")
            if not ok:
                all_ok = False
        except Exception as e:
            _log(f"  {mc.label}: FAILED — {e}")
            all_ok = False

    return all_ok


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment loop
# ─────────────────────────────────────────────────────────────────────────────

def run_experiment(
    exp_config: ExperimentConfig,
    cdsfl_text: str,
    pattern_name: str = DEFAULT_PATTERN,
    resume: bool = False,
    topology: str = DEFAULT_TOPOLOGY,
    relay_mode: str = DEFAULT_RELAY_MODE,
) -> Dict[str, Any]:
    """Run Experiment 35: PolicyEngine Code Review (Dual-Topology).

    topology: "relay" or "star" — user-configurable switch.
    relay_mode: "findings", "conversational", or "directed" (relay only).
    """
    topo_desc = (
        f"relay/{relay_mode} (models see each other's analysis)"
        if topology == "relay"
        else "star/blackboard (runner owns all state)"
    )
    _log("=" * 60)
    _log("EXPERIMENT 35: PolicyEngine Code Review")
    _log(f"  Topology: {topo_desc}")
    _log(f"  Pattern: {pattern_name}")
    _log(f"  Max rounds: {MAX_ROUNDS} (extension to {EXTENSION_CAP})")
    _log(f"  Convergence: state-based, earliest R{EARLIEST_STOP_ROUND}")
    _log(f"  Gamma: telemetry→R{GAMMA_TELEMETRY_ONLY_UNTIL}, "
         f"soft→R{GAMMA_SOFT_GATE_UNTIL}, hard→R{GAMMA_SOFT_GATE_UNTIL + 1}+")
    _log(f"  Target: engine.py + schema.toml")
    _log(f"  Context: registry.py")
    _log(f"  Models: {sorted(BASELINE_MODELS)}")
    _log(f"  Logs: {LOGS_DIR}")
    _log("=" * 60)

    # Load source files
    target_text = TARGET_FILE.read_text(encoding="utf-8")
    target_rel = TARGET_FILE.relative_to(REPO_ROOT)

    # Bundle schema.toml with the target (both under review)
    schema_text = SCHEMA_FILE.read_text(encoding="utf-8")
    schema_rel = SCHEMA_FILE.relative_to(REPO_ROOT)

    context_parts = []
    for ctx_path in CONTEXT_FILES:
        ctx_text = ctx_path.read_text(encoding="utf-8")
        ctx_rel = ctx_path.relative_to(REPO_ROOT)
        context_parts.append(
            f"=== CONTEXT FILE: {ctx_rel} ({len(ctx_text):,} chars) ===\n"
            f"(Read-only context — do NOT review this file, "
            f"only use it to understand interfaces)\n{ctx_text}"
        )

    full_code = (
        f"=== TARGET FILE (REVIEW THIS): {target_rel} "
        f"({len(target_text):,} chars) ===\n{target_text}\n\n"
        f"=== SCHEMA DEFINITION (REVIEW THIS): {schema_rel} "
        f"({len(schema_text):,} chars) ===\n{schema_text}\n\n"
        + "\n\n".join(context_parts)
    )

    total_raw = len(target_text) + len(schema_text) + sum(
        len(p.read_text(encoding="utf-8")) for p in CONTEXT_FILES
    )
    source_paths_str = [str(TARGET_FILE), str(SCHEMA_FILE)] + [str(p) for p in CONTEXT_FILES]

    _log(f"  Target: {len(target_text):,} chars")
    _log(f"  Context: {len(context_parts)} files")
    _log(f"  Total: {total_raw:,} raw chars → {len(full_code):,} with headers")

    # Build DynamicManager
    dm_config = DynamicManagementConfig(
        pre_decompose_models={"Codex", "DeepSeek"},
        no_exclusion_mode=True,
    )
    dm_config.max_rounds = MAX_ROUNDS
    model_specs = build_model_specs(exp_config)
    mgr = DynamicManager(model_specs, dm_config)

    # Build Insect Brain — central relay and persistence
    brain = InsectBrain(
        config=dm_config,
        logs_dir=LOGS_DIR,
        source_paths=source_paths_str,
    )
    brain.initialise(model_labels=sorted(BASELINE_MODELS))

    # Build Endocrine Layer — health monitor (still runs for pacing,
    # but engine.py + schema.toml are the review targets, not endocrine)
    endo = EndocrineLayer(
        source_paths=source_paths_str,
        test_cmd=None,
        max_fix_evals=20,
    )
    _log(f"  Endocrine layer initialised (runs for pacing, NOT under review)")

    # Finding registry (canonical state — shared by BOTH topologies)
    registry = FindingRegistry()

    # Load persistent fingerprints
    observed_fingerprints = _load_fingerprints()
    if observed_fingerprints:
        _log(f"  Fingerprints loaded: {list(observed_fingerprints.keys())}")
    else:
        _log(f"  No persistent fingerprints found — starting fresh")

    # Resume from checkpoint if available
    start_round = 0
    if resume and brain.load_checkpoint():
        start_round = brain.state.current_round + 1
        total_restored = sum(len(rnd) for rnd in brain.state.all_findings)
        _log(f"  RESUMED from round {start_round} "
             f"({total_restored} findings, {len(brain.state.all_findings)} rounds)")
        # Restore registry and convergence state
        runner_ckpt = brain.logs_dir / "runner_state.json"
        if runner_ckpt.exists():
            import json as _json
            ckpt_data = _json.loads(runner_ckpt.read_text(encoding="utf-8"))
            registry = FindingRegistry.from_dict(ckpt_data.get("registry", {}))
            _log(f"  Registry restored: {len(registry.entries)} entries")
        else:
            _log("  WARNING: No runner_state.json — registry is empty after resume")

    experiment_start = time.monotonic()
    novelty_counts: List[int] = []
    cumulative_context_chars = 0
    per_model_context: Dict[str, int] = {}
    gamma_history: List[float] = []
    gate_history: List[bool] = []
    open_ch_history: List[int] = []
    stall_history: List[Dict[str, int]] = []
    if resume and (brain.logs_dir / "runner_state.json").exists():
        import json as _json
        ckpt_data = _json.loads(
            (brain.logs_dir / "runner_state.json").read_text(encoding="utf-8")
        )
        novelty_counts = ckpt_data.get("novelty_counts", [])
        gamma_history = ckpt_data.get("gamma_history", [])
        gate_history = ckpt_data.get("gate_history", [])
        open_ch_history = ckpt_data.get("open_ch_history", [])
        stall_history = ckpt_data.get("stall_history", [])
        cumulative_context_chars = ckpt_data.get("cumulative_context_chars", 0)

    # Build multi-model awareness preamble (star topology)
    roster_lines = "\n".join(
        f"  - {label}: {desc}" for label, desc in sorted(MODEL_ROSTER.items())
    )

    topo_instruction = (
        _RELAY_TOPOLOGY_INSTRUCTION if topology == "relay"
        else _STAR_TOPOLOGY_INSTRUCTION
    )
    awareness_preamble = (
        "You are one of 5 AI models participating in a distributed code review "
        "under full CDSFL constraints with FFF methodology. The models are:\n"
        f"{roster_lines}\n\n"
        f"{topo_instruction}"
        f"{_POC_CONTEXT_INSTRUCTION}"
        f"{_MACHINE_COMMS_INSTRUCTION}"
        f"{_GOOD_ENOUGH_INSTRUCTION}"
    )

    prior_fix_summary = _build_prior_fix_summary()

    base_prompt = (
        f"{awareness_preamble}"
        f"{prior_fix_summary}"
        "YOUR TASK:\n"
        "Review the PolicyEngine (engine.py + schema.toml) — the configuration "
        "facade for the CDSFL bench system. This module provides a 55-parameter "
        "interface over a 4-layer TOML hierarchy (universal/domain/task/model) "
        "with monotonicity enforcement.\n\n"
        "The PolicyEngine provides:\n"
        "  1. Parameter query — resolve effective value through 4-layer merge\n"
        "  2. Provenance tracking — which layer set each parameter\n"
        "  3. Validation — policy violations against schema constraints\n"
        "  4. Policy diff — compare two policies for divergence\n"
        "  5. Schema enforcement — 15 HARD / 40 SOFT constraint classification\n\n"
        "Focus areas:\n"
        "  - Does the 4-layer merge produce correct results for all parameter types?\n"
        "  - Is monotonicity enforcement correct (HARD constraints cannot be weakened)?\n"
        "  - Does provenance tracking accurately report which layer set each value?\n"
        "  - Are schema.toml definitions complete and internally consistent?\n"
        "  - Does validation catch all constraint violations?\n"
        "  - Interface correctness with registry.py (the underlying TOML merge)\n\n"
        "For each finding, provide (keys in this exact order):\n"
        "  FINDING_ID: unique identifier (e.g., F001). IMPORTANT: your finding IDs "
        "must be STABLE across rounds. If you filed F001 in Round 3, F001 in Round 4 "
        "must refer to the same bug.\n"
        "  SEVERITY: 0.0 to 1.0 (1.0 = critical)\n"
        "  FLAW_CLASS: integer category (1=logic, 2=interface, 3=notation, "
        "4=completeness, 5=correctness, 6=edge-case, 7=performance, 8=documentation)\n"
        "  ABSTRACTION_INDEX: 0.0 to 1.0 (0=surface, 1=architectural)\n"
        "  DESCRIPTION: FIND — what is wrong, where, and what is the evidence\n"
        "  FOLLOW: trace downstream consequences BEFORE proposing a fix\n"
        "  PROPOSED_FIX: FIX — the simplest sufficient correction\n"
        "  VERIFIED: TRUE if you have a proof/test, FALSE if this is an assertion\n\n"
        "Produce ALL findings you can identify. Do not hold back.\n\n"
        f"=== ARTIFACT: PolicyEngine + Schema + Context ({len(full_code):,} chars) ===\n\n"
        f"{full_code}\n\n"
        "=== END ARTIFACT ===\n\n"
        "Produce your findings now."
    )

    n_files = full_code.count("=== ")
    if n_files > 2:
        base_prompt += (
            f"\n\nIMPORTANT: This prompt contains {n_files} code sections. "
            f"The TARGET files are engine.py and schema.toml — review BOTH. "
            f"The other files are read-only context for understanding interfaces.\n"
        )

    _log(f"  Base prompt: {len(base_prompt):,} chars")

    result: Dict[str, Any] = {
        "experiment": "exp35_pe",
        "topology": topology,
        "relay_mode": relay_mode if topology == "relay" else None,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "pattern": pattern_name,
        "models": sorted(BASELINE_MODELS),
        "target_file": str(target_rel),
        "context_files": [str(p.relative_to(REPO_ROOT)) for p in CONTEXT_FILES],
        "max_rounds": MAX_ROUNDS,
        "extension_cap": EXTENSION_CAP,
        "convergence_config": {
            "earliest_stop": EARLIEST_STOP_ROUND,
            "consecutive_required": CONSECUTIVE_ROUNDS_REQUIRED,
            "max_novel": MAX_NOVEL_FINDINGS,
            "gamma_telemetry_until": GAMMA_TELEMETRY_ONLY_UNTIL,
            "gamma_soft_until": GAMMA_SOFT_GATE_UNTIL,
            "gamma_soft_threshold": GAMMA_SOFT_THRESHOLD,
            "gamma_hard_threshold": GAMMA_HARD_THRESHOLD,
        },
        "rounds": [],
    }

    # Effective max (may extend)
    effective_max = MAX_ROUNDS
    extended = False

    for round_idx in range(start_round, EXTENSION_CAP):
        if round_idx >= effective_max:
            break

        round_start = time.monotonic()
        wall_elapsed = round_start - experiment_start
        if wall_elapsed > WALL_CLOCK_CAP_S:
            _log(f"\nWALL CLOCK CAP reached ({wall_elapsed:.0f}s). Stopping.")
            break

        _log(f"\n{'─' * 60}")
        round_type = "blind" if round_idx == 0 else "adaptive"
        _log(f"Round {round_idx}/{effective_max - 1} ({round_type})")
        _log(f"{'─' * 60}")

        # Dispatch to all models — topology-dependent
        if topology == "relay":
            findings, responses, per_model_durations = _dispatch_round_relay(
                exp_config, mgr, brain,
                base_prompt, cdsfl_text, full_code,
                round_idx, pattern_name,
                relay_mode=relay_mode,
                registry=registry,
            )
        else:
            # Star topology: inject registry summary as blackboard
            registry_summary = registry.build_summary(round_idx) if round_idx > 0 else ""
            findings, responses, per_model_durations = _dispatch_round(
                exp_config, mgr, brain,
                base_prompt, registry_summary, cdsfl_text, full_code,
                round_idx, pattern_name,
                registry=registry,
            )

        # Safety check — removes empty/refused responses, never benches
        problem = _safety_check(responses, round_idx, brain)
        if problem:
            # ALL models failed — try ITC restart-fresh for each before giving up
            _log(f"  All models failed initial dispatch — ITC recovery...")
            recovered_any = False
            for mc in exp_config.models:
                if mc.label not in BASELINE_MODELS or mc.role == "collator":
                    continue
                classification = _itc_detect(
                    mc.label, round_idx, 0, "", set(), set())
                if classification:
                    _itc_adapt(mc.label, classification, round_idx)
                recovery_prompt = _itc_build_recovery_prompt(
                    mc.label, base_prompt, observed_fingerprints, round_idx)
                try:
                    recovered_findings, recovered_text = _dispatch_single_model(
                        mc, mgr, recovery_prompt, cdsfl_text, full_code,
                        round_idx, pattern_name)
                    if recovered_text and not recovered_text.startswith("__DISPATCH_FAILED__"):
                        if len(recovered_text.strip()) >= 50:
                            responses[mc.label] = recovered_text
                            findings.extend(recovered_findings)
                            _itc_clear_adaptation(mc.label)
                            recovered_any = True
                            _log(f"  ITC [{mc.label}]: RECOVERED "
                                 f"({len(recovered_text)} chars, "
                                 f"{len(recovered_findings)} findings)")
                except Exception as e:
                    _log(f"  ITC [{mc.label}]: recovery dispatch failed — {e}")
            if not recovered_any:
                _log(f"\n*** PULL THE PLUG: {problem} (ITC recovery exhausted) ***")
                result["terminated"] = problem
                break
        else:
            # ITC recovery for models that were in dispatch but produced
            # empty/failed output (removed by safety check)
            responded = set(responses.keys())
            for mc in exp_config.models:
                if mc.label not in BASELINE_MODELS or mc.role == "collator":
                    continue
                if mc.label in responded:
                    _itc_clear_adaptation(mc.label)
                    continue
                # This model didn't produce usable output — ITC recover now
                classification = _itc_detect(
                    mc.label, round_idx, 0, "", set(), set())
                if classification:
                    _itc_adapt(mc.label, classification, round_idx)
                recovery_prompt = _itc_build_recovery_prompt(
                    mc.label, base_prompt, observed_fingerprints, round_idx)
                try:
                    recovered_findings, recovered_text = _dispatch_single_model(
                        mc, mgr, recovery_prompt, cdsfl_text, full_code,
                        round_idx, pattern_name)
                    if (recovered_text
                            and not recovered_text.startswith("__DISPATCH_FAILED__")
                            and len(recovered_text.strip()) >= 50):
                        responses[mc.label] = recovered_text
                        findings.extend(recovered_findings)
                        _itc_clear_adaptation(mc.label)
                        _log(f"  ITC [{mc.label}]: RECOVERED "
                             f"({len(recovered_text)} chars, "
                             f"{len(recovered_findings)} findings)")
                    else:
                        _itc_flag_underperformer(
                            mc.label, round_idx,
                            classification or "UNRESPONSIVE",
                            _itc_consecutive_failures(mc.label))
                except Exception as e:
                    _log(f"  ITC [{mc.label}]: recovery dispatch failed — {e}")

        # Register findings in canonical registry
        novel_this_round = 0
        for f in findings:
            existing = registry.lookup_alias(f.model_id, f.finding_id)
            if existing is None:
                registry.register(f, f.model_id)
                novel_this_round += 1
            else:
                # Model resubmitted an existing finding — treat as CONFIRM
                registry.add_verdict(
                    existing, f.model_id, "CONFIRM", round_idx,
                )

        novelty_counts.append(novel_this_round)
        _log(f"  Registry: {novel_this_round} novel, "
             f"{len(registry.entries)} total canonical")

        # Parse and register verdicts from raw responses
        n_confirm = n_challenge = n_extend = n_merge = 0
        for model_id, raw_text in responses.items():
            verdicts = _parse_verdicts(raw_text, model_id, round_idx)
            for verdict_type, canonical_id, evidence in verdicts:
                if verdict_type == "MERGE":
                    # MERGE C0001 <- source: mark SOURCE as merged into TARGET
                    source_canonical = _resolve_merge_source(
                        evidence, model_id, registry,
                    )
                    if source_canonical and source_canonical != canonical_id:
                        registry.add_verdict(
                            source_canonical, model_id, "MERGE", round_idx,
                            f"merged_into={canonical_id}",
                        )
                        n_merge += 1
                    else:
                        # Can't resolve source — treat as CONFIRM on target
                        registry.add_verdict(
                            canonical_id, model_id, "CONFIRM", round_idx,
                            evidence,
                        )
                        n_confirm += 1
                else:
                    registry.add_verdict(
                        canonical_id, model_id, verdict_type, round_idx,
                        evidence,
                    )
                    if verdict_type == "CONFIRM":
                        n_confirm += 1
                    elif verdict_type == "CHALLENGE":
                        n_challenge += 1
                    elif verdict_type == "EXTEND":
                        n_extend += 1
        if n_confirm + n_challenge + n_extend + n_merge > 0:
            _log(f"  Verdicts: {n_confirm} CONFIRM, {n_challenge} CHALLENGE, "
                 f"{n_extend} EXTEND, {n_merge} MERGE")

        # Status transitions: programmatic confirmation / merge
        _update_finding_statuses(registry, round_idx)
        registry.auto_resolve_contested(round_idx)
        confirmed = sum(
            1 for e in registry.entries.values() if e["status"] == "CONFIRMED"
        )
        closed = sum(
            1 for e in registry.entries.values() if e["status"] == "CLOSED"
        )
        merged = sum(
            1 for e in registry.entries.values() if e["status"] == "MERGED"
        )
        resolved = closed + merged
        active = len(registry.entries) - resolved
        if confirmed + resolved > 0:
            _log(f"  Status: {confirmed} CONFIRMED, {closed} CLOSED, "
                 f"{merged} MERGED, {active} OPEN")

        # Persist round via brain (still using brain for persistence)
        round_elapsed = time.monotonic() - round_start
        brain.persist(round_idx, responses, findings, duration_s=round_elapsed)

        # Endocrine cycle (for pacing — NOT under review in this experiment)
        round_timings = _build_round_timings(
            responses, per_model_durations, findings, round_idx,
        )
        for model_label_ctx, text in responses.items():
            per_model_context[model_label_ctx] = (
                per_model_context.get(model_label_ctx, 0) + len(text)
            )
            cumulative_context_chars += len(text)
        _log(f"  Per-model context: "
             f"{{{', '.join(f'{k}: {v/1000:.0f}K' for k, v in sorted(per_model_context.items()))}}}")

        endo_report = endo.run(
            round_idx=round_idx,
            findings=findings,
            round_timings=round_timings,
            cumulative_context_chars=cumulative_context_chars,
            context_budget=max(CONTEXT_CHAR_BUDGET.values()),
            novelty_counts=novelty_counts,
        )

        _log(f"\n  Endocrine cycle (round {round_idx}):")
        _log(f"    Health scan: {endo_report.health_scan.total} diagnostics")
        if endo_report.pacing_signals:
            for sig in endo_report.pacing_signals:
                _log(f"    Pacing: {sig.signal_type} → {sig.suggested_action}")

        # Extract directed messages (relay mode only)
        if topology == "relay" and relay_mode == "directed":
            for model_label, response_text in responses.items():
                if response_text:
                    directed = brain.extract_directed_messages(
                        model_label, response_text, round_idx,
                    )
                    if directed:
                        _log(f"  {model_label}: {len(directed)} directed message(s)")

        # Run immune pipeline
        immune_result = brain.run_immune_pipeline(findings)

        # Bridge: immune pipeline verified-fix results → registry
        # When Stage 4 (fix evaluation) marks a finding as verified,
        # propagate that to the registry so _update_finding_statuses
        # can transition CONFIRMED → CLOSED.
        for f in findings:
            if f.verified:
                canonical = registry.lookup_alias(f.model_id, f.finding_id)
                if canonical:
                    registry.mark_verified(canonical)

        # CC2v between-rounds verification: FFF open findings
        verification_stats = _verification_step(
            registry, round_idx, full_code, exp_config.models,
        )
        if not verification_stats.get("skipped"):
            _log(f"  CC2v verification: {verification_stats.get('total_resolved', 0)} resolved "
                 f"({verification_stats.get('confirmed', 0)}C / "
                 f"{verification_stats.get('rejected', 0)}R / "
                 f"{verification_stats.get('duplicates', 0)}M / "
                 f"{verification_stats.get('escalated', 0)}E)")
        # ITC check — per-model adaptive recovery
        for model_label in list(BASELINE_MODELS):
            model_findings = [f for f in findings if f.model_id == model_label]
            model_text = responses.get(model_label, "")
            prior_ids: Set[str] = set()
            current_ids = {f.finding_id for f in model_findings}

            # Get prior round's finding IDs for this model
            if brain.state.all_findings and len(brain.state.all_findings) >= 2:
                prior_round = brain.state.all_findings[-2]
                prior_ids = {
                    f.finding_id for f in prior_round
                    if f.model_id == model_label
                }

            # Check for dispatch errors in this round
            dispatch_err = None
            if model_label not in responses:
                dispatch_err = "no_response"

            classification = _itc_detect(
                model_label, round_idx,
                len(model_findings), model_text,
                prior_ids, current_ids,
                dispatch_error=dispatch_err,
            )
            if classification:
                _itc_adapt(model_label, classification, round_idx)
            elif model_label in _itc_model_state:
                _itc_clear_adaptation(model_label)

            # Update observed fingerprint
            _update_observed_fingerprint(
                observed_fingerprints, model_label, round_idx,
                len(model_findings), len(model_text),
                dispatch_error=dispatch_err,
            )

        # Compute metrics
        metrics = brain.compute_metrics(round_idx)

        # Gamma
        gamma = _estimate_gamma(novelty_counts)
        gamma_history.append(gamma)
        gate_level, gamma_passed = _check_gamma_gate(gamma, round_idx)
        gamma_interp = _interpret_gamma(gamma)

        _log(f"  γ: {gamma:.3f} ({gate_level}, "
             f"{'passed' if gamma_passed else 'BLOCKED'}) — {gamma_interp}")

        # Build round data
        round_data: Dict[str, Any] = {
            "round": round_idx,
            "type": round_type,
            "findings_count": len(findings),
            "novel_this_round": novel_this_round,
            "registry_total": len(registry.entries),
            "models_responded": list(responses.keys()),
            "elapsed_s": round(round_elapsed, 1),
            "per_model": {
                label: len([f for f in findings if f.model_id == label])
                for label in responses
            },
            "brain_metrics": metrics,
            "gamma": round(gamma, 4),
            "gamma_gate": gate_level,
            "gamma_passed": gamma_passed,
            "gamma_interpretation": gamma_interp,
            "immune_pipeline": {
                "rejection_rate": immune_result.rejection_rate,
                "autoimmune_flag": immune_result.autoimmune_flag,
                "survivors": len(immune_result.filtered_findings),
            },
            "endocrine": {
                "health_scan": _summarise_health_scan(endo_report.health_scan),
                "fix_evaluations": _summarise_fix_evaluations(endo_report.fix_evaluations),
                "pacing_signals": _summarise_pacing_signals(endo_report.pacing_signals),
                "elapsed_s": round(endo_report.elapsed_s, 2),
            },
            "convergence_gate": {
                "open_crit_high": registry.open_crit_high_count(),
                "contested": registry.contested_count(round_idx),
                "recent_novel": novelty_counts[-CONSECUTIVE_ROUNDS_REQUIRED:]
                    if len(novelty_counts) >= CONSECUTIVE_ROUNDS_REQUIRED else novelty_counts,
            },
        }
        round_data["verification"] = verification_stats
        result["rounds"].append(round_data)

        _log(f"\n  Round {round_idx}: {len(findings)} valid findings from "
             f"{len(responses)} models ({round_elapsed:.1f}s)")
        for label in sorted(responses.keys()):
            model_count = len([f for f in findings if f.model_id == label])
            _log(f"    {label}: {model_count} findings")

        # Check state-based convergence (primary gate)
        # NOTE: these calls mutate gate_history, open_ch_history, stall_history.
        # Checkpoint is written AFTER so resume gets the complete state.
        converged, conv_reason = _check_state_convergence(
            round_idx, registry, novel_this_round, gamma, gate_history,
            open_ch_history=open_ch_history,
        )
        _log(f"  Convergence: {conv_reason}")

        # Stall-convergence detector (complementary secondary signal)
        stall_result = _check_stall_convergence(
            round_idx, registry, gamma, stall_history,
        )

        # Persist runner state for resume (after convergence checks so
        # gate_history, open_ch_history, stall_history include this round)
        _runner_ckpt = brain.logs_dir / "runner_state.json"
        _runner_ckpt.write_text(json.dumps({
            "registry": registry.to_dict(),
            "novelty_counts": novelty_counts,
            "gamma_history": [round(g, 6) for g in gamma_history],
            "gate_history": gate_history,
            "open_ch_history": open_ch_history,
            "stall_history": stall_history,
            "cumulative_context_chars": cumulative_context_chars,
        }, indent=2, default=str), encoding="utf-8")
        round_data["stall_detector"] = stall_result
        if stall_result["stalled"]:
            if stall_result["tier"] == "terminate":
                _log(f"  Stall detector: {stall_result['reason']}")
            elif stall_result["tier"] == "advisory":
                _log(f"  Stall detector: {stall_result['reason']}")
            elif stall_result["tier"] == "stalled_low_gamma":
                _log(f"  Stall detector: {stall_result['reason']}")

        if converged:
            _log(f"\n  CONVERGED at round {round_idx}: {conv_reason}")
            result["converged_at"] = round_idx
            result["convergence_reason"] = conv_reason
            break

        # Stall-convergence termination (fires only if gate did NOT converge)
        if stall_result.get("terminate"):
            _log(f"\n  STALL_CONVERGED at round {round_idx}: {stall_result['reason']}")
            result["converged_at"] = round_idx
            result["convergence_reason"] = "STALL_CONVERGED"
            result["stall_detail"] = stall_result["reason"]
            break

        # Budget extension check at MAX_ROUNDS boundary
        if round_idx == MAX_ROUNDS - 1 and not extended:
            gamma_prev = gamma_history[-2] if len(gamma_history) >= 2 else 0.0
            should_extend, ext_reason = _check_budget_extension(
                round_idx, registry, gamma, gamma_prev,
            )
            if should_extend:
                effective_max = EXTENSION_CAP
                extended = True
                _log(f"\n  BUDGET EXTENDED to {EXTENSION_CAP}: {ext_reason}")
                result["budget_extended"] = True
                result["extension_reason"] = ext_reason
            else:
                _log(f"\n  No budget extension needed: {ext_reason}")

        # Extension stall detection: if extended but no improvement, terminate
        if extended and round_idx > MAX_ROUNDS and len(result["rounds"]) >= 2:
            prev_rd = result["rounds"][-2].get("convergence_gate", {})
            curr_rd = round_data.get("convergence_gate", {})
            prev_open = prev_rd.get("open_crit_high", 99)
            curr_open = curr_rd.get("open_crit_high", 99)
            prev_contested = prev_rd.get("contested", 99)
            curr_contested = curr_rd.get("contested", 99)
            if curr_open >= prev_open and curr_contested >= prev_contested:
                _log(
                    f"  Extension not improving: open_ch {prev_open}"
                    f"\u2192{curr_open}, contested {prev_contested}"
                    f"\u2192{curr_contested}. Terminating."
                )
                result["converged_at"] = round_idx
                result["convergence_reason"] = "EXTENSION_STALLED"
                break

    # Finalise status model: remaining OPEN/CONTESTED -> UNCONFIRMED
    final_round = len(brain.state.all_findings) - 1
    for canonical_id, entry in list(registry.entries.items()):
        if entry["status"] in ("OPEN", "CONTESTED"):
            registry.resolve(canonical_id, "UNCONFIRMED", final_round)

    # Save persistent fingerprints
    _save_fingerprints(observed_fingerprints, "exp35_pe")

    # Signal complete
    signal = brain.signal_complete()

    # Final summary
    total_elapsed = time.monotonic() - experiment_start
    total_findings = sum(len(rnd) for rnd in brain.state.all_findings)
    result["total_findings"] = total_findings
    result["total_rounds"] = len(brain.state.all_findings)
    result["total_elapsed_s"] = round(total_elapsed, 1)
    result["end_time"] = datetime.now(timezone.utc).isoformat()
    result["completion_signal"] = signal

    # Per-model totals
    per_model_totals: Dict[str, int] = {}
    for rnd in brain.state.all_findings:
        for f in rnd:
            per_model_totals[f.model_id] = per_model_totals.get(f.model_id, 0) + 1
    result["per_model_totals"] = per_model_totals

    # Gamma
    gamma_final = gamma_history[-1] if gamma_history else 0.0
    result["gamma"] = round(gamma_final, 4)
    result["gamma_history"] = [round(g, 4) for g in gamma_history]
    result["per_round_counts"] = [len(rnd) for rnd in brain.state.all_findings]

    # ITC: include HIL flags in report for human review
    hil_flags = _itc_get_hil_flags()
    result["hil_flags"] = hil_flags
    if hil_flags:
        _log(f"\n  *** {len(hil_flags)} HIL FLAG(S) for human review ***")
        for flag in hil_flags:
            _log(f"    {flag['message']}")

    # Popper C(H,E)
    CONTROL_BASELINE_RATE = 2.0
    if brain.state.all_findings:
        cdsfl_rate = total_findings / len(brain.state.all_findings)
        pe_h = cdsfl_rate
        pe = CONTROL_BASELINE_RATE
        c_he = (pe_h - pe) / (pe_h + pe) if (pe_h + pe) > 0 else 0.0
        result["popper_corroboration"] = {
            "C_HE": round(c_he, 4),
            "P_E_given_H": round(pe_h, 4),
            "P_E": round(pe, 4),
        }

    # Registry summary
    result["registry"] = registry.to_dict()

    # Endocrine health trend
    result["endocrine_health_trend"] = endo.health_trend()

    # Save report
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = LOGS_DIR / "exp35_report.json"
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # Merkle sealing
    chain_path = LOGS_DIR / "experiment_chain.json"

    def _floats_to_strings(obj: Any) -> Any:
        """Recursively convert floats to string representations for
        deterministic Merkle hashing (floats have platform-dependent repr)."""
        if isinstance(obj, float):
            return f"{obj:.6g}"
        if isinstance(obj, dict):
            return {k: _floats_to_strings(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_floats_to_strings(v) for v in obj]
        return obj

    try:
        from bench.verification_chain import VerificationChain

        chain = VerificationChain()

        for round_data_entry in result.get("rounds", []):
            round_idx_val = round_data_entry.get("round", "?")
            chain.append_record(
                artifact_type="experiment_round",
                payload=_floats_to_strings(round_data_entry),
                recorded_by="exp35_runner",
                metadata={
                    "experiment": "exp35",
                    "round": round_idx_val,
                    "models": round_data_entry.get("models_responded", []),
                },
            )

        round_files = sorted(LOGS_DIR.glob("r*_*.json"))
        for rf in round_files:
            try:
                rf_data = json.loads(rf.read_text(encoding="utf-8"))
                chain.append_record(
                    artifact_type="model_response",
                    payload=_floats_to_strings(rf_data),
                    recorded_by="exp35_runner",
                    metadata={
                        "source_file": rf.name,
                        "experiment": "exp35",
                    },
                    storage_mode="hash_only",
                )
            except Exception:
                pass

        chain.append_record(
            artifact_type="experiment_report",
            payload=_floats_to_strings(result),
            recorded_by="exp35_runner",
            metadata={
                "experiment": "exp35",
                "status": signal.get("status", "unknown"),
                "reason": signal.get("reason", "unknown"),
                "total_findings": total_findings,
                "total_rounds": len(brain.state.all_findings),
            },
        )

        epoch = chain.seal_epoch()
        chain.save_json(str(chain_path))

        _log(f"\n  Merkle chain sealed: {len(chain.records)} records, "
             f"epoch merkle_root={epoch['merkle_root'][:24]}...")
        result["merkle_chain"] = {
            "path": str(chain_path),
            "records": len(chain.records),
            "merkle_root": epoch["merkle_root"],
        }

        report_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    except Exception as e:
        _log(f"\n  WARNING: Merkle sealing failed (non-fatal): {e}")
        import traceback
        _log(f"  {traceback.format_exc()}")

    _log(f"\n{'=' * 60}")
    _log(f"EXPERIMENT 35 — {len(brain.state.all_findings)} ROUNDS COMPLETE")
    _log(f"  Topology: {topo_desc}")
    _log(f"  Rounds: {len(brain.state.all_findings)} "
         f"{'(extended)' if extended else ''}")
    _log(f"  Total findings: {total_findings}")
    _log(f"  Per model: {per_model_totals}")
    _log(f"  Per round: {[len(rnd) for rnd in brain.state.all_findings]}")
    _log(f"  Registry: {len(registry.entries)} canonical entries")
    _log(f"  γ final: {gamma_final:.3f} ({_interpret_gamma(gamma_final)})")
    _log(f"  γ history: {[round(g, 3) for g in gamma_history]}")
    c_he_val = result.get("popper_corroboration", {}).get("C_HE")
    if c_he_val is not None:
        _log(f"  C(H,E): {c_he_val:.4f}")
    _log(f"  Elapsed: {total_elapsed:.0f}s")
    _log(f"  Report: {report_path}")
    _log(f"  Brain signal: {signal['status']} — {signal['reason']}")
    _log(f"{'=' * 60}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global LOGS_DIR
    source_env()

    exp_config = load_default_config()
    cdsfl_path = (REPO_ROOT / "bench" / "directives" / "universal"
                  / "cdsfl_core_formal.md")
    cdsfl_text = cdsfl_path.read_text(encoding="utf-8")

    args = sys.argv[1:]
    mode = "run"
    resume = False
    pattern = DEFAULT_PATTERN
    topology = DEFAULT_TOPOLOGY
    relay_mode = DEFAULT_RELAY_MODE

    i = 0
    while i < len(args):
        if args[i] == "--resume":
            resume = True
            mode = "run"
        elif args[i] == "--pattern" and i + 1 < len(args):
            pattern = args[i + 1]
            i += 1
        elif args[i] == "--topology" and i + 1 < len(args):
            topology = args[i + 1]
            i += 1
        elif args[i] == "--relay-mode" and i + 1 < len(args):
            relay_mode = args[i + 1]
            i += 1
        elif args[i] in ("preflight", "run"):
            mode = args[i]
        i += 1

    if pattern not in INTERACTION_PATTERN_PRESETS:
        available = ", ".join(sorted(INTERACTION_PATTERN_PRESETS))
        print(f"Unknown pattern: {pattern!r}. Available: {available}",
              file=sys.stderr)
        sys.exit(1)

    if topology not in ("relay", "star"):
        print(f"Unknown topology: {topology!r}. Use 'relay' or 'star'.",
              file=sys.stderr)
        sys.exit(1)

    if relay_mode not in ("findings", "conversational", "directed"):
        print(f"Unknown relay-mode: {relay_mode!r}. "
              f"Use 'findings', 'conversational', or 'directed'.",
              file=sys.stderr)
        sys.exit(1)

    LOGS_DIR = _find_or_create_logs_dir(resume=resume)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if mode == "preflight":
        ok = run_preflight(exp_config, cdsfl_text)
        sys.exit(0 if ok else 1)

    elif mode == "run":
        if not resume:
            ok = run_preflight(exp_config, cdsfl_text)
            if not ok:
                _log("\nPREFLIGHT FAILED. Aborting.")
                sys.exit(1)
            _log(f"\nPreflight passed. Starting Exp 35 in 5s... "
                 f"(topology={topology}, pattern={pattern})")
            time.sleep(5)
        else:
            _log(f"\nRESUME mode — skipping preflight "
                 f"(topology={topology}, pattern={pattern})")

        result = run_experiment(
            exp_config, cdsfl_text,
            pattern_name=pattern, resume=resume,
            topology=topology, relay_mode=relay_mode)

        if result.get("terminated"):
            _log(f"\nExperiment terminated: {result['terminated']}")
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
