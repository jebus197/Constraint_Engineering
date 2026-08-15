#!/usr/bin/env python3
"""Experiment 33: Endocrine Layer Code Review — Star/Blackboard Topology.

Reviews endocrine.py as the 4th test article. This is the first experiment
to use the star/blackboard topology (runner owns all state, no model-to-model
relay) and the corrected convergence parameters from Exp 32 meta-analysis.

Key design changes from Exp 31:
  1. Star/blackboard: runner maintains canonical finding registry, models
     submit structured DISCOVERY/VERDICT payloads, no model-to-model prose.
  2. 21-round budget (was 15). Extension to 24 on trigger conditions.
     Prior mathematical modelling predicted 20 rounds for this complexity.
  3. Scale-dependent gamma: telemetry R1-14, soft gate R15-19, hard gate R20+.
  4. State-based convergence gate: earliest trigger R12.
  5. Structured verdict protocol: CONFIRM/CHALLENGE/EXTEND/MERGE only.
  7. Neutral framing: no convergence hypothesis, no efficiency rankings.
  8. All 5 models retained for diversity testing.

Subject under review: endocrine.py (whole-body health monitor).
Context files: insect_brain.py, immune_agents.py (read-only context).

Architecture:
  - Insect brain handles persistence, metrics, convergence
  - EndocrineLayer is UNDER REVIEW (not running as infrastructure)
  - 5-model parallel dispatch (CC2, Codex, Gemini, DeepSeek, ChatGPT)
  - Star topology: runner compiles registry summary per round
  - Immune pipeline called through brain.run_immune_pipeline()
  - Convergence: state-based gate + scale-dependent gamma

Models:
  - CC2 (Claude Opus 4.6 via OpenRouter)
  - Codex (GPT-5.4 Codex via codex exec CLI)
  - Gemini (Gemini 3.1 Pro via Google SDK)
  - DeepSeek (DeepSeek Reasoner via DeepSeek API)
  - ChatGPT (GPT-5.4 via OpenRouter)

Usage:
    python3 bench/run_exp33_endocrine.py [preflight|run|--resume]
    python3 bench/run_exp33_endocrine.py run --pattern fff
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
    """Find existing exp33 logs dir for resume, or create a new one."""
    if resume:
        logs_root = REPO_ROOT / "bench" / "logs"
        candidates = sorted(
            logs_root.glob("exp33_endocrine_*"),
            key=lambda p: p.name,
            reverse=True,
        )
        for c in candidates:
            if (c / "checkpoint.json").exists():
                return c
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "bench" / "logs" / f"exp33_endocrine_{ts}"


LOGS_DIR = REPO_ROOT / "bench" / "logs" / "exp33_endocrine_latest"

MAX_ROUNDS = 21              # Mathematical model: 20 rounds for this complexity
EXTENSION_CAP = 24           # Budget extension ceiling
WALL_CLOCK_CAP_S = 8 * 3600  # 8 hours (longer than Exp 31 due to 21 rounds)

# Test article: endocrine.py (4th file, never reviewed by models before)
TARGET_FILE = REPO_ROOT / "bench" / "endocrine.py"

# Context files: models read these for interface understanding, not review
CONTEXT_FILES = [
    REPO_ROOT / "bench" / "insect_brain.py",
    REPO_ROOT / "bench" / "immune_agents.py",
]

# 5-model set — all retained for diversity testing
BASELINE_MODELS = {"CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"}

DEFAULT_PATTERN = "fff"

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
MAX_OPEN_CRIT_HIGH = 0           # Zero open CRITICAL/HIGH to qualify

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
        self._alias_map: Dict[str, str] = {}  # model_local_id -> canonical_id

    def register(self, finding: Finding, model_id: str) -> str:
        """Register a new finding. Returns canonical ID."""
        canonical_id = f"C{self._next_id:04d}"
        self._next_id += 1

        self._alias_map[finding.finding_id] = canonical_id

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

    def resolve(self, canonical_id: str, status: str, round_idx: int):
        """Update finding status (OPEN, CONFIRMED, UNCONFIRMED, MERGED)."""
        if canonical_id in self.entries:
            self.entries[canonical_id]["status"] = status
            self.entries[canonical_id]["last_status_change_round"] = round_idx

    def lookup_alias(self, model_local_id: str) -> Optional[str]:
        """Resolve a model-local ID to canonical ID."""
        return self._alias_map.get(model_local_id)

    def open_crit_high_count(self) -> int:
        """Count open findings with severity >= 0.7 (CRITICAL/HIGH)."""
        return sum(
            1 for e in self.entries.values()
            if e["status"] == "OPEN" and e["severity"] >= 0.7
        )

    def contested_count(self, current_round: int) -> int:
        """Count findings with unresolved CHALLENGE verdicts for >1 round."""
        count = 0
        for e in self.entries.values():
            if e["status"] != "OPEN":
                continue
            challenges = [
                v for v in e["verdicts"] if v["verdict"] == "CHALLENGE"
            ]
            confirms = [
                v for v in e["verdicts"] if v["verdict"] == "CONFIRM"
            ]
            if challenges and not confirms:
                oldest_challenge = min(v["round"] for v in challenges)
                if current_round - oldest_challenge > 1:
                    count += 1
        return count

    def build_summary(self, round_idx: int) -> str:
        """Build the structured registry summary for model consumption.

        This is the blackboard — what models read each round.
        """
        if not self.entries:
            return "(No findings registered yet.)"

        lines = [
            f"=== FINDING REGISTRY (Round {round_idx}) ===",
            f"Total: {len(self.entries)} canonical findings",
            f"Open: {sum(1 for e in self.entries.values() if e['status'] == 'OPEN')}",
            f"Open CRIT/HIGH: {self.open_crit_high_count()}",
            "",
        ]

        # Group by status
        for status in ("OPEN", "CONFIRMED", "UNCONFIRMED", "MERGED"):
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

        lines.append("=== END REGISTRY ===")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise for JSON persistence."""
        return {
            "entries": dict(self.entries),
            "next_id": self._next_id,
            "alias_map": dict(self._alias_map),
        }



# ─────────────────────────────────────────────────────────────────────────────
# Verdict parser
# ─────────────────────────────────────────────────────────────────────────────

_VERDICT_RE = re.compile(
    r'^(CONFIRM|CHALLENGE|EXTEND|MERGE)\s+(C\d{4})(?:\s*[\|<\-]+\s*(.*))?$',
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


# ─────────────────────────────────────────────────────────────────────────────
# Gamma estimation
# ─────────────────────────────────────────────────────────────────────────────

def _estimate_gamma(all_findings: List[List[Finding]]) -> float:
    """Estimate Duane gamma from per-round finding counts."""
    n = len(all_findings)
    if n < MIN_ROUNDS_FOR_GAMMA:
        return 0.0
    per_round = [len(rnd) for rnd in all_findings]
    cumulative = []
    total = 0
    for c in per_round:
        total += c
        cumulative.append(total)
    if cumulative[0] <= 0 or cumulative[-1] <= cumulative[0]:
        return 0.0 if cumulative[-1] == 0 else 1.0
    try:
        beta = (math.log(cumulative[-1]) - math.log(cumulative[0])) / math.log(n)
        return 1.0 - beta
    except (ValueError, ZeroDivisionError):
        return 0.0


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

    CONFIRMED: source model + 1 independent CONFIRM = 2 independent models.
    MERGED: any accepted MERGE verdict.
    Remaining OPEN findings become UNCONFIRMED at experiment end (caller's job).
    """
    for canonical_id, entry in list(registry.entries.items()):
        if entry["status"] != "OPEN":
            continue

        # MERGE takes priority — finding subsumed into another
        merge_verdicts = [v for v in entry["verdicts"] if v["verdict"] == "MERGE"]
        if merge_verdicts:
            registry.resolve(canonical_id, "MERGED", round_idx)
            continue

        # Programmatic confirmation: source model is 1, each distinct
        # confirming model from a different source adds 1.  Total >= 2 = CONFIRMED.
        confirm_models = {
            v["model"] for v in entry["verdicts"] if v["verdict"] == "CONFIRM"
        }
        independent_count = 1 + len(confirm_models - {entry["source_model"]})
        if independent_count >= 2:
            registry.resolve(canonical_id, "CONFIRMED", round_idx)


def _check_state_convergence(
    round_idx: int,
    registry: FindingRegistry,
    novel_counts: List[int],
    gamma: float,
) -> Tuple[bool, str]:
    """Compound state-based convergence gate.

    Returns (converged, reason).

    Conditions (ALL must hold for CONSECUTIVE_ROUNDS_REQUIRED consecutive rounds):
      1. round >= EARLIEST_STOP_ROUND
      2. Zero open CRITICAL/HIGH findings
      3. Novel findings <= MAX_NOVEL_FINDINGS
      4. No finding contested (unresolved CHALLENGE) for >1 round
      5. Gamma gate passes (scale-dependent)
    """
    if round_idx < EARLIEST_STOP_ROUND:
        return False, f"Too early (round {round_idx} < {EARLIEST_STOP_ROUND})"

    # Check the last CONSECUTIVE_ROUNDS_REQUIRED rounds
    if len(novel_counts) < CONSECUTIVE_ROUNDS_REQUIRED:
        return False, "Insufficient rounds for consecutive check"

    recent_novel = novel_counts[-CONSECUTIVE_ROUNDS_REQUIRED:]

    # Condition 2: zero open CRIT/HIGH
    open_ch = registry.open_crit_high_count()
    if open_ch > 0:
        return False, f"Open CRIT/HIGH: {open_ch}"

    # Condition 3: novel findings <= threshold for consecutive rounds
    if any(n > MAX_NOVEL_FINDINGS for n in recent_novel):
        return False, (
            f"Novel findings too high: {recent_novel} "
            f"(need <= {MAX_NOVEL_FINDINGS} for {CONSECUTIVE_ROUNDS_REQUIRED} rounds)"
        )

    # Condition 4: no contested findings
    contested = registry.contested_count(round_idx)
    if contested > 0:
        return False, f"Contested findings: {contested}"

    # Condition 5: gamma gate (scale-dependent)
    gate_level, gamma_passed = _check_gamma_gate(gamma, round_idx)
    if not gamma_passed:
        if gate_level == "soft":
            return False, (
                f"Gamma soft gate: {gamma:.3f} < {GAMMA_SOFT_THRESHOLD} "
                f"(state conditions met but gamma flags HIL review)"
            )
        else:
            return False, (
                f"Gamma hard gate: {gamma:.3f} < {GAMMA_HARD_THRESHOLD} "
                f"(state conditions met but gamma blocks convergence)"
            )

    return True, (
        f"STATE_CONVERGED at round {round_idx}: "
        f"novel={recent_novel}, open_ch={open_ch}, "
        f"gamma={gamma:.3f} ({gate_level})"
    )


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


# ─────────────────────────────────────────────────────────────────────────────
# PoC context and instructions
# ─────────────────────────────────────────────────────────────────────────────

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
        "and verification_chain.py. Those experiments found ~96 distinct bugs "
        "and applied 50+ fixes. The endocrine layer (your review target) was "
        "NOT reviewed in those experiments — it ran as infrastructure.\n\n"
        "The endocrine layer integrates with the immune pipeline and insect "
        "brain. You have those files as read-only context so you can "
        "understand the interfaces. Focus your review on endocrine.py.\n\n"
        "11 additional infrastructure fixes were applied after Exp 31 audit:\n"
        "  - E31-01: Flag propagation through immune pipeline\n"
        "  - E31-02: Reconciliation lock enforcement\n"
        "  - E31-05: Confidence inflation (effective_reject)\n"
        "  - E31-06: Directed message temporal leak\n"
        "  - E31-07: NK v2 anomaly detection alignment\n"
        "  - E31-10/17: Search manifest validation\n"
        "  - E31-13: Checkpoint after immune pipeline\n"
        "  - E31-14: Truncation marker attribution\n"
        "  - E31-15: AST negative literal handling\n"
        "  - E31-16: Skin barrier path containment\n"
        "  - E31-18: Epoch schema validation\n\n"
        "Do NOT re-report these. They are fixed.\n\n"
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
            for i, part in enumerate(full_code.split("\n\n=== FILE:"))
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

        # Star topology: inject registry summary, not other models' prose
        return (
            f"{base_prompt}\n\n"
            f"{registry_summary}\n\n"
            f"This is Round {round_idx}. Review the registry above. "
            f"File new DISCOVERY findings for bugs not yet registered. "
            f"Issue VERDICT payloads (CONFIRM/CHALLENGE/EXTEND/MERGE) "
            f"on existing entries where you have evidence. "
            f"Do not repeat registered findings.\n"
        )

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
        brain.handle_model_failure(label, detail)

    return findings, responses, per_model_durations


# ─────────────────────────────────────────────────────────────────────────────
# Safety checks
# ─────────────────────────────────────────────────────────────────────────────

def _safety_check(
    responses: Dict[str, str],
    round_idx: int,
    brain: InsectBrain,
) -> Optional[str]:
    """Check for problems that warrant stopping."""
    if not responses:
        return "all_models_failed"

    failed_labels = []
    for label, text in responses.items():
        if len(text.strip()) < 50:
            _log(f"  SAFETY: {label} near-empty response ({len(text)} chars) — benching")
            brain.handle_model_failure(label, f"empty_response_round_{round_idx}")
            failed_labels.append(label)
        elif "[MODEL_REFUSED" in text:
            _log(f"  SAFETY: {label} refused — benching")
            brain.handle_model_failure(label, f"refused_round_{round_idx}")
            failed_labels.append(label)

    for label in failed_labels:
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
) -> Dict[str, Any]:
    """Run Experiment 33: Endocrine Layer Code Review (Star/Blackboard)."""
    _log("=" * 60)
    _log("EXPERIMENT 33: Endocrine Layer Code Review")
    _log(f"  Topology: star/blackboard (runner owns all state)")
    _log(f"  Pattern: {pattern_name}")
    _log(f"  Max rounds: {MAX_ROUNDS} (extension to {EXTENSION_CAP})")
    _log(f"  Convergence: state-based, earliest R{EARLIEST_STOP_ROUND}")
    _log(f"  Gamma: telemetry→R{GAMMA_TELEMETRY_ONLY_UNTIL}, "
         f"soft→R{GAMMA_SOFT_GATE_UNTIL}, hard→R{GAMMA_SOFT_GATE_UNTIL + 1}+")
    _log(f"  Target: endocrine.py")
    _log(f"  Context: insect_brain.py, immune_agents.py")
    _log(f"  Models: {sorted(BASELINE_MODELS)}")
    _log(f"  Logs: {LOGS_DIR}")
    _log("=" * 60)

    # Load source files
    target_text = TARGET_FILE.read_text(encoding="utf-8")
    target_rel = TARGET_FILE.relative_to(REPO_ROOT)

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
        + "\n\n".join(context_parts)
    )

    total_raw = len(target_text) + sum(
        len(p.read_text(encoding="utf-8")) for p in CONTEXT_FILES
    )
    source_paths_str = [str(TARGET_FILE)] + [str(p) for p in CONTEXT_FILES]

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
    # but endocrine.py itself is the review target)
    endo = EndocrineLayer(
        source_paths=source_paths_str,
        test_cmd=None,
        max_fix_evals=20,
    )
    _log(f"  Endocrine layer initialised (runs for pacing, also under review)")

    # Finding registry (star/blackboard canonical state)
    registry = FindingRegistry()

    # Resume from checkpoint if available
    start_round = 0
    if resume and brain.load_checkpoint():
        start_round = brain.state.current_round + 1
        total_restored = sum(len(rnd) for rnd in brain.state.all_findings)
        _log(f"  RESUMED from round {start_round} "
             f"({total_restored} findings, {len(brain.state.all_findings)} rounds)")

    experiment_start = time.monotonic()
    novelty_counts: List[int] = []
    cumulative_context_chars = 0
    gamma_history: List[float] = []

    # Build multi-model awareness preamble (star topology)
    roster_lines = "\n".join(
        f"  - {label}: {desc}" for label, desc in sorted(MODEL_ROSTER.items())
    )

    awareness_preamble = (
        "You are one of 5 AI models participating in a distributed code review "
        "under full CDSFL constraints with FFF methodology. The models are:\n"
        f"{roster_lines}\n\n"
        f"{_STAR_TOPOLOGY_INSTRUCTION}"
        f"{_POC_CONTEXT_INSTRUCTION}"
        f"{_MACHINE_COMMS_INSTRUCTION}"
        f"{_GOOD_ENOUGH_INSTRUCTION}"
    )

    prior_fix_summary = _build_prior_fix_summary()

    base_prompt = (
        f"{awareness_preamble}"
        f"{prior_fix_summary}"
        "YOUR TASK:\n"
        "Review endocrine.py — the whole-body health monitor for the CDSFL "
        "bench system. This module has been running as infrastructure since "
        "Experiment 30 but has never been independently reviewed.\n\n"
        "The endocrine layer provides:\n"
        "  1. Health scan — static analysis (pyright/ruff/bandit) between rounds\n"
        "  2. Defect detection — classify findings by defect category\n"
        "  3. Fix evaluation — sandbox-test proposed fixes (SAFE/HARMFUL/NEUTRAL)\n"
        "  4. Pacing signals — timing, context growth, novelty plateau monitoring\n\n"
        "Focus areas:\n"
        "  - Does the health scan correctly run tools and parse their output?\n"
        "  - Does fix evaluation actually sandbox correctly (no source modification)?\n"
        "  - Are pacing signal thresholds reasonable and correctly triggered?\n"
        "  - Are there dead code paths or features that never fire?\n"
        "  - Interface correctness with insect_brain.py and immune_agents.py\n\n"
        "For each finding, provide (keys in this exact order):\n"
        "  FINDING_ID: unique identifier (e.g., F001). IMPORTANT: your finding IDs "
        "must be STABLE across rounds. If you filed F001 in Round 3, F001 in Round 4 "
        "must refer to the same bug. To replace a finding, use SUPERSEDES: old_ID.\n"
        "  SEVERITY: 0.0 to 1.0 (1.0 = critical)\n"
        "  FLAW_CLASS: integer category (1=logic, 2=interface, 3=notation, "
        "4=completeness, 5=correctness, 6=edge-case, 7=performance, 8=documentation)\n"
        "  ABSTRACTION_INDEX: 0.0 to 1.0 (0=surface, 1=architectural)\n"
        "  DESCRIPTION: FIND — what is wrong, where, and what is the evidence\n"
        "  FOLLOW: trace downstream consequences BEFORE proposing a fix\n"
        "  PROPOSED_FIX: FIX — the simplest sufficient correction\n"
        "  VERIFIED: TRUE if you have a proof/test, FALSE if this is an assertion\n\n"
        "Produce ALL findings you can identify. Do not hold back.\n\n"
        f"=== ARTIFACT: Endocrine Layer + Context ({len(full_code):,} chars) ===\n\n"
        f"{full_code}\n\n"
        "=== END ARTIFACT ===\n\n"
        "Produce your findings now."
    )

    n_files = full_code.count("=== ")
    if n_files > 1:
        base_prompt += (
            f"\n\nIMPORTANT: This prompt contains {n_files} code sections. "
            f"The TARGET file is endocrine.py — review ONLY that file. "
            f"The other files are read-only context for understanding interfaces.\n"
        )

    _log(f"  Base prompt: {len(base_prompt):,} chars")

    result: Dict[str, Any] = {
        "experiment": "exp33_endocrine",
        "topology": "star_blackboard",
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

        # Build registry summary for this round (star topology)
        registry_summary = registry.build_summary(round_idx) if round_idx > 0 else ""

        # Dispatch to all models
        findings, responses, per_model_durations = _dispatch_round(
            exp_config, mgr, brain,
            base_prompt, registry_summary, cdsfl_text, full_code,
            round_idx, pattern_name,
        )

        # Safety check
        problem = _safety_check(responses, round_idx, brain)
        if problem:
            _log(f"\n*** PULL THE PLUG: {problem} ***")
            result["terminated"] = problem
            break

        # Register findings in canonical registry
        novel_this_round = 0
        for f in findings:
            existing = registry.lookup_alias(f.finding_id)
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
                registry.add_verdict(
                    canonical_id, model_id, verdict_type, round_idx, evidence,
                )
                if verdict_type == "CONFIRM":
                    n_confirm += 1
                elif verdict_type == "CHALLENGE":
                    n_challenge += 1
                elif verdict_type == "EXTEND":
                    n_extend += 1
                elif verdict_type == "MERGE":
                    n_merge += 1
        if n_confirm + n_challenge + n_extend + n_merge > 0:
            _log(f"  Verdicts: {n_confirm} CONFIRM, {n_challenge} CHALLENGE, "
                 f"{n_extend} EXTEND, {n_merge} MERGE")

        # Status transitions: programmatic confirmation / merge
        _update_finding_statuses(registry, round_idx)
        confirmed = sum(
            1 for e in registry.entries.values() if e["status"] == "CONFIRMED"
        )
        merged = sum(
            1 for e in registry.entries.values() if e["status"] == "MERGED"
        )
        if confirmed + merged > 0:
            _log(f"  Status: {confirmed} CONFIRMED, {merged} MERGED, "
                 f"{len(registry.entries) - confirmed - merged} OPEN")

        # Persist round via brain (still using brain for persistence)
        round_elapsed = time.monotonic() - round_start
        brain.persist(round_idx, responses, findings, duration_s=round_elapsed)

        # Endocrine cycle (for pacing — the module is under review but still runs)
        round_timings = _build_round_timings(
            responses, per_model_durations, findings, round_idx,
        )
        for text in responses.values():
            cumulative_context_chars += len(text)

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

        # Run immune pipeline
        immune_result = brain.run_immune_pipeline(findings)

        # Compute metrics
        metrics = brain.compute_metrics(round_idx)

        # Gamma
        gamma = _estimate_gamma(brain.state.all_findings)
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
        result["rounds"].append(round_data)

        _log(f"\n  Round {round_idx}: {len(findings)} valid findings from "
             f"{len(responses)} models ({round_elapsed:.1f}s)")
        for label in sorted(responses.keys()):
            model_count = len([f for f in findings if f.model_id == label])
            _log(f"    {label}: {model_count} findings")

        # Check state-based convergence
        converged, conv_reason = _check_state_convergence(
            round_idx, registry, novelty_counts, gamma,
        )
        _log(f"  Convergence: {conv_reason}")

        if converged:
            _log(f"\n  CONVERGED at round {round_idx}: {conv_reason}")
            result["converged_at"] = round_idx
            result["convergence_reason"] = conv_reason
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
    report_path = LOGS_DIR / "exp33_report.json"
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
                recorded_by="exp33_runner",
                metadata={
                    "experiment": "exp33",
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
                    recorded_by="exp33_runner",
                    metadata={
                        "source_file": rf.name,
                        "experiment": "exp33",
                    },
                    storage_mode="hash_only",
                )
            except Exception:
                pass

        chain.append_record(
            artifact_type="experiment_report",
            payload=_floats_to_strings(result),
            recorded_by="exp33_runner",
            metadata={
                "experiment": "exp33",
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
    _log(f"EXPERIMENT 33 — {len(brain.state.all_findings)} ROUNDS COMPLETE")
    _log(f"  Topology: star/blackboard")
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
    # Refuse a paid run on `--help` or a typo. Must be the FIRST thing
    # main() does: everything below this line can reach a paid model.
    from bench.runner_argv_guard import guard_argv
    guard_argv(['--pattern', '--resume', 'preflight', 'run'], 'python3 bench/run_exp33_endocrine.py [preflight|run|--resume]')
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

    i = 0
    while i < len(args):
        if args[i] == "--resume":
            resume = True
            mode = "run"
        elif args[i] == "--pattern" and i + 1 < len(args):
            pattern = args[i + 1]
            i += 1
        elif args[i] in ("preflight", "run"):
            mode = args[i]
        i += 1

    if pattern not in INTERACTION_PATTERN_PRESETS:
        available = ", ".join(sorted(INTERACTION_PATTERN_PRESETS))
        print(f"Unknown pattern: {pattern!r}. Available: {available}",
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
            _log(f"\nPreflight passed. Starting Exp 33 in 5s... "
                 f"(pattern={pattern})")
            time.sleep(5)
        else:
            _log(f"\nRESUME mode — skipping preflight (pattern={pattern})")

        result = run_experiment(
            exp_config, cdsfl_text,
            pattern_name=pattern, resume=resume)

        if result.get("terminated"):
            _log(f"\nExperiment terminated: {result['terminated']}")
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
