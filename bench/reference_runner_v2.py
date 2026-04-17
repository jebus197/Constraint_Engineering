#!/usr/bin/env python3
"""Parameterised reference runner for CDSFL experiments (Exp 37+, Bench Run 2).

Extracts the parameterised entry point from run_exp36_evidence.py so future
experiments don't need per-experiment runner scripts. The test article,
context files, domain, and convergence parameters are all configurable.

All heavy lifting (dispatch, parsing, immune pipeline, convergence) is in
runner_core.py, immune_agents.py, insect_brain.py, etc. This runner
orchestrates those modules with configurable parameters.

Includes the A1-A5 fixes from Exp 36:
  A1: Registry windowing (OPEN/CONTESTED full detail, settled compact, hidden)
  A2: Rho as C6 convergence condition (discovery efficiency churn detector)
  A3: Contested -> HIL escalation after max_contested_rounds
  A4: Gamma-aware ITC (suppress DEGRADATION restart when rho is healthy)
  A5: Dedup-aware CC2v (skip already-confirmed/escalated findings)

Usage:
    python3 bench/reference_runner.py run --test-article bench/evidence.py
    python3 bench/reference_runner.py run --test-article bench/evidence.py \\
        --context bench/verification_chain.py --topology relay
    python3 bench/reference_runner.py run --config experiment.json
    python3 bench/reference_runner.py preflight
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import os
import py_compile
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from copy import deepcopy
from dataclasses import dataclass, field, replace
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
    get_effective_context_budget,
)
from run_exp17_immune import (
    TASKS,
    TASK_MARKERS,
    REVIEW_AREAS,
    FINDING_FORMAT,
    RoundTelemetry,
    run_layer1_preflight,
    _should_decompose,
    _invalidate_fingerprint_cache,
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
from bench.dm._feedback import (
    FindingFeedback,
    build_feedback_records,
    build_feedback_sections,
    parse_admissibility_block,
)
# Exp 40 fix 1D.1, 1D.2, 1D.4: round-context helpers.
from bench.dm._round_context import (
    build_prior_fix_summary,
    build_consolidation_preamble,
    build_windowed_context,
)
# Exp 40 fix 1D.5: S_k SEARCH/REPLACE format pre-check + reformat request.
from bench.dm._sk_format import (
    check_sk_format_admissible,
    build_reformat_requests as build_sk_reformat_requests,
)
# Exp 40 fix 1E.7: cross-model diversity metric (compliance-theatre detector).
from bench.dm._diversity import diversity_signal_from_round
# Exp 40 fix 1E.7: per-finding alternative extraction for diversity metric.
from bench.dm._divergence import parse_alternative_block


# Exp 40 fix 1E.6: hard payload floor for decomposition decisions.
# Independent of fingerprint observed-capacity values — large monolithic
# dispatches degrade parse yield even when the model accepts them.
DECOMPOSE_HARD_FLOOR_CHARS = 80_000


def should_decompose_v2(
    model_label: str, mgr, payload_chars: int = 0,
) -> bool:
    """v2 decomposition decision with a fingerprint-agnostic hard floor.

    The underlying :func:`_should_decompose` is fingerprint-driven: a model
    whose fingerprint reports high observed capacity will accept large
    monolithic payloads, which in Exp 39-0 caused parse-yield collapse on
    369K dispatches to CC2/ChatGPT/Gemini (their fingerprints reported
    465K observed capacity × 0.9 safety margin = 418K ≥ 369K, no
    decompose, quality crashed).

    Layered decision:

    1. Payload > ``DECOMPOSE_HARD_FLOOR_CHARS`` (80K) → force decompose.
       This overrides the fingerprint's observed-capacity opinion. Even
       if the model has "proven" it can ingest more, quality collapses
       above the floor for ambient-noise reasons independent of
       successful-dispatch outcomes.
    2. Otherwise defer to :func:`_should_decompose` which still honours
       ``pre_decompose_models`` override, observed prompt limits, failure
       ceilings, and the static 80K fallback when fingerprint data is
       absent.

    Returns ``True`` iff the caller should decompose the payload.
    """
    if payload_chars > DECOMPOSE_HARD_FLOOR_CHARS:
        return True
    return _should_decompose(model_label, mgr, payload_chars=payload_chars)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration dataclass
# ─────────────────────────────────────────────────────────────────────────────

MODEL_ROSTER = {
    "CC2": "Claude Opus 4.6 (Anthropic)",
    "Codex": "GPT-5.4 Codex (OpenAI)",
    "Gemini": "Gemini 3.1 Pro (Google)",
    "DeepSeek": "DeepSeek Reasoner (DeepSeek)",
    "ChatGPT": "GPT-5.4 (OpenAI)",
}

# Operational directive — R_k(i) self-assessment equation and working protocol.
# Appended AFTER composer phenotype transforms to bypass char caps. Models MUST
# compute R_k on their own output (§3, §6). Without this directive, models
# produce qualitative findings, not metacognitive self-assessment. Exp 37:
# 88-100% R_k adoption with directive, 0% without. (Exp37 line 185-194, 2195-2196)
_OPERATIONAL_DIRECTIVE_PATH = (
    REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
)
_OPERATIONAL_DIRECTIVE_TEXT = ""
if _OPERATIONAL_DIRECTIVE_PATH.exists():
    _OPERATIONAL_DIRECTIVE_TEXT = _OPERATIONAL_DIRECTIVE_PATH.read_text(encoding="utf-8")

FINGERPRINT_DIR = REPO_ROOT / "bench" / "fingerprints"


@dataclass
class RunnerConfig:
    """All parameters for a reference experiment run."""

    # Target and context
    test_article: str = ""
    context_files: List[str] = field(default_factory=list)

    # Topology
    topology: str = "star"
    relay_mode: str = "directed"

    # Prompt pattern
    pattern: str = "fff"

    # Round limits
    max_rounds: int = 21
    extension_cap: int = 24
    wall_clock_cap_s: int = 28800
    earliest_stop_round: int = 12

    # Models
    models: List[str] = field(
        default_factory=lambda: ["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"]
    )

    # Naming
    experiment_name: str = ""

    # Domain for directive composition
    domain: str = "software"

    # Resume from checkpoint
    resume: bool = False

    # Convergence tuning
    rho_threshold: float = 0.25
    rho_rolling_window: int = 3
    consecutive_rounds_required: int = 2

    # Derived constants (set from the above or left at defaults)
    max_novel_findings: int = 2
    open_ch_stability_window: int = 3
    max_open_crit_high: int = 5  # Was 0 (unreachable). Exp 39-0 fix.
    # γ-alt convergence path (Exp 40 fix, Item 1A.3 remainder from Exp 40 plan).
    # Fires when EITHER gamma >= gamma_alt_threshold OR
    # gamma_alt_consecutive_zero_crit consecutive rounds with zero novel CRITICAL.
    # Documented in Exp 39 sub-experiment configs as pass_condition.
    gamma_alt_threshold: float = 0.30
    gamma_alt_consecutive_zero_crit: int = 3
    gamma_alt_earliest_round: int = 3
    # Round-context helpers (Exp 40 1D.1, 1D.2, 1D.4).
    prior_fix_summary_enabled: bool = True
    prior_fix_summary_max_entries: int = 20
    prior_fix_summary_max_chars: int = 4000
    consolidation_rounds: int = 3
    windowed_context_enabled: bool = True
    windowed_context_full_rounds: int = 2
    windowed_context_max_chars: int = 6000
    rho_earliest_round: int = 12
    stall_window: int = 3
    stall_earliest_round: int = 15
    stall_gamma_advisory: float = 0.30
    stall_gamma_terminate: float = 0.45
    verification_batch_size: int = 6
    verification_min_round: int = 6
    verification_confidence_threshold: float = 0.7
    gamma_telemetry_only_until: int = 14
    gamma_soft_gate_until: int = 19
    gamma_soft_threshold: float = 0.30
    gamma_hard_threshold: float = 0.35
    min_rounds_for_gamma: int = 3
    max_contested_rounds: int = 5
    exhausted_round_threshold: int = 8  # rounds stalled before EXHAUSTED bypass
    multiturn_chunk_target: int = 30_000

    # S_k pipeline
    sk_enabled: bool = False
    test_cmd: Optional[str] = None
    sk_s_floor: float = 0.0  # domain-specific minimum S*

    # Burst decomposition: "auto" (decide based on fingerprints),
    # "on" (always decompose), "off" (monolithic)
    burst_mode: str = "auto"

    # Shadow cell configuration (Macrophage + Ouroboros, cell type split 12 April 2026)
    shadow_cell_config: Dict[str, Any] = field(default_factory=dict)

    # HIL review gate (13 April 2026, agreed scope refinement).
    # When True, the runner saves checkpoint and exits with code 42 after
    # each round (monolithic mode) or phase transition (burst mode).
    # Resume with --resume to continue.  This enables the collaborative
    # test-discover-analyse-fix-fold cycle between the operator and CC.
    hil_review: bool = False

    # Feedback channel (cdsfl_operational.md §17, 15 April 2026).
    # Defaults True — the whole point of CDSFL is corrective feedback, not
    # measurement for its own sake. Set False for controlled ablation only.
    feedback_channel_enabled: bool = True
    feedback_top_k: int = 10
    feedback_max_chars_per_model: int = 8000

    def __post_init__(self):
        if not self.experiment_name and self.test_article:
            stem = Path(self.test_article).stem
            self.experiment_name = f"ref_{stem}"
        # Bug 5 fix: removed silent override of rho_earliest_round.
        # These parameters serve different purposes and must be
        # independently configurable.

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RunnerConfig":
        """Build config from a JSON-compatible dict (ignores unknown keys)."""
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        kwargs = {k: v for k, v in d.items() if k in valid}
        # Capture shadow cell config from underscore-prefixed sections
        shadow = {}
        if "_macrophage" in d:
            shadow["_macrophage"] = d["_macrophage"]
        if "_ouroboros" in d:
            shadow["_ouroboros"] = d["_ouroboros"]
        if shadow:
            kwargs["shadow_cell_config"] = shadow
        return cls(**kwargs)

    @classmethod
    def from_json(cls, path: str) -> "RunnerConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


# ─────────────────────────────────────────────────────────────────────────────
# S_k Solution Verification — Data Structures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class FixBlock:
    """A single SEARCH/REPLACE edit block parsed from model output."""
    file_path: str
    search: str
    replace: str


@dataclass
class SkResult:
    """Result of S_k computation for a proposed fix."""
    sk: float
    A: float  # product of hard gates (binary admissibility)
    E: float  # weighted effect evidence aggregate
    tristate: str  # ADMISSIBLE, REJECTED, ESCALATE
    gate_details: Dict[str, Any] = field(default_factory=dict)
    blocks_parsed: int = 0
    blocks_applied: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# FindingRegistry (identical to Exp 36 — A1 windowing, A3 HIL escalation)
# ─────────────────────────────────────────────────────────────────────────────

class FindingRegistry:
    """Canonical finding registry — runner-owned, models read/propose only.

    A1 fix: windowed build_summary (full detail for active, compact for
    settled, hidden for refuted/duplicate).
    A3 fix: escalate_stale_contested after max_contested_rounds.
    """

    def __init__(self):
        self.entries: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1
        self._alias_map: Dict[str, str] = {}

    def register(self, finding: Finding, model_id: str) -> str:
        canonical_id = f"C{self._next_id:04d}"
        self._next_id += 1
        self._alias_map[f"{model_id}:{finding.finding_id}"] = canonical_id
        self.entries[canonical_id] = {
            "canonical_id": canonical_id,
            "source_model": model_id,
            "source_aliases": [finding.finding_id],
            "severity": finding.severity,
            "description": finding.description[:500],
            "proposed_fix": finding.proposed_fix[:5000] if finding.proposed_fix else "",
            "status": "OPEN",
            "open_since_round": getattr(finding, "round_idx", 0),
            "last_status_change_round": getattr(finding, "round_idx", 0),
            "verdicts": [],
            "verified": finding.verified,
            "escalated": finding.escalated,
            "flaw_class": getattr(finding, "flaw_class", 0),
            "origin_type": getattr(finding, "origin_type", ""),
            "source_ref": getattr(finding, "source_ref", ""),
            "retrieval_query": getattr(finding, "retrieval_query", ""),
            "retrieved_at": getattr(finding, "retrieved_at", ""),
            "source_hash": getattr(finding, "source_hash", ""),
            "source_diversity": getattr(finding, "source_diversity", 0.0),
        }
        return canonical_id

    def add_verdict(
        self, canonical_id: str, model_id: str, verdict: str,
        round_idx: int, evidence: str = "",
    ):
        if canonical_id not in self.entries:
            return
        self.entries[canonical_id]["verdicts"].append({
            "model": model_id, "verdict": verdict,
            "round": round_idx, "evidence": evidence[:200],
        })
        # F2/F5/F9 fix: do NOT update last_status_change_round here.
        # Verdicts are evidence, not status transitions. Only resolve()
        # should update the timer, preventing escalation timer corruption.

    def resolve(
        self, canonical_id: str, status: str, round_idx: int,
        merged_into: Optional[str] = None,
    ):
        if canonical_id in self.entries:
            self.entries[canonical_id]["status"] = status
            self.entries[canonical_id]["last_status_change_round"] = round_idx
            if merged_into:
                self.entries[canonical_id]["merged_into"] = merged_into

    def mark_verified(self, canonical_id: str):
        if canonical_id in self.entries:
            self.entries[canonical_id]["verified"] = True

    def lookup_alias(self, model_id: str, local_id: str) -> Optional[str]:
        return self._alias_map.get(f"{model_id}:{local_id}")

    def open_crit_high_count(self) -> int:
        """Count active non-terminal critical/high findings.

        Pure reader — no state mutation. Exhausted findings (marked by
        _update_finding_statuses) are excluded from the count.
        Gate threshold stays fixed; finding eligibility changes.
        """
        _NON_TERMINAL = ("OPEN", "CONTESTED", "REOPENED")
        count = 0
        for e in self.entries.values():
            if e["status"] not in _NON_TERMINAL or e["severity"] < 0.7:
                continue
            if e.get("exhausted"):
                continue
            count += 1
        return count

    def contested_count(self, current_round: int, grace_period: int = 2) -> int:
        """Count actively contested non-terminal findings.

        Pure reader — no state mutation. UNCONFIRMED reopens are handled
        by _update_finding_statuses() before this is called.

        - MERGED/CLOSED/REFUTED/DUPLICATE: irrecoverable terminal, always excluded.
        - UNCONFIRMED: counted during grace period only.
        """
        _IRRECOVERABLE = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
        count = 0
        for e in self.entries.values():
            if e["status"] in _IRRECOVERABLE:
                continue
            # UNCONFIRMED: grace period read-only check
            if e["status"] == "UNCONFIRMED":
                rounds_in_status = current_round - e.get("last_status_change_round", 0)
                if rounds_in_status < grace_period:
                    count += 1
                # else: grace expired — excluded (reopen handled elsewhere)
                continue
            # Non-terminal, non-UNCONFIRMED: standard contested logic
            challenges = [v for v in e["verdicts"] if v["verdict"] == "CHALLENGE"]
            if not challenges:
                continue
            confirms = [v for v in e["verdicts"] if v["verdict"] == "CONFIRM"]
            latest_confirm_round = max((v["round"] for v in confirms), default=-1)
            unresolved = [v for v in challenges if v["round"] >= latest_confirm_round]
            if unresolved:
                oldest = min(v["round"] for v in unresolved)
                if current_round - oldest >= grace_period:
                    count += 1
        return count

    # Cap full-detail active entries to bound context growth.
    # Overflow entries get compact one-line treatment.
    # (Ported from run_exp37_evidence.py line 227 + 444-478)
    MAX_FULL_DETAIL_OPEN = 20

    def build_summary(self, round_idx: int) -> str:
        """A1 fix: windowed registry summary with overflow cap."""
        if not self.entries:
            return "(No findings registered yet.)"
        full_detail_statuses = ("OPEN", "CONTESTED", "REOPENED")
        compact_statuses = ("CONFIRMED", "UNCONFIRMED", "CLOSED", "MERGED")
        hidden_statuses = ("REFUTED", "DUPLICATE")
        full_detail = [e for e in self.entries.values() if e["status"] in full_detail_statuses]
        compact = [e for e in self.entries.values() if e["status"] in compact_statuses]
        hidden_count = sum(1 for e in self.entries.values() if e["status"] in hidden_statuses)

        lines = [
            f"=== FINDING REGISTRY (Round {round_idx}) ===",
            f"Total: {len(self.entries)} canonical findings",
            f"Active: {len(full_detail)} | Settled: {len(compact)} | Hidden: {hidden_count}",
            f"Open CRIT/HIGH: {self.open_crit_high_count()}",
            "",
        ]
        # Cap full-detail entries by severity to bound context growth.
        all_active_sorted = sorted(full_detail, key=lambda x: -x["severity"])
        full_detail_shown = all_active_sorted[:self.MAX_FULL_DETAIL_OPEN]
        full_detail_overflow = all_active_sorted[self.MAX_FULL_DETAIL_OPEN:]
        for status in full_detail_statuses:
            group = [e for e in full_detail_shown if e["status"] == status]
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
        # Overflow active findings: compact one-line (lower severity)
        if full_detail_overflow:
            lines.append(
                f"--- ACTIVE OVERFLOW ({len(full_detail_overflow)}) "
                f"(lower severity, compact) ---"
            )
            for e in full_detail_overflow:
                lines.append(
                    f"  {e['canonical_id']} (sev {e['severity']:.2f}) "
                    f"[{e['status']}] {e['description'][:80]}"
                )
            lines.append("")
        if compact:
            lines.append(f"--- SETTLED ({len(compact)}) (do not re-describe) ---")
            lines.append(
                "These findings are confirmed, closed, or merged. "
                "Do not CHALLENGE or re-describe them. "
                "To reopen, issue REOPEN <ID> with specific new evidence."
            )
            for e in sorted(compact, key=lambda x: x["canonical_id"]):
                tag = e["status"]
                merged_note = f" -> {e['merged_into']}" if e.get("merged_into") else ""
                lines.append(
                    f"  [{tag}] {e['canonical_id']}{merged_note}: "
                    f"{e['description'][:80]}"
                )
            lines.append("")
        if hidden_count > 0:
            lines.append(f"({hidden_count} findings hidden: refuted or duplicate)")
            lines.append("")
        lines.append("=== END REGISTRY ===")
        return "\n".join(lines)

    def escalate_stale_contested(self, current_round: int, max_contested_rounds: int = 5,
                                 grace_period: int = 2) -> List[str]:
        """A3 fix: escalate stale contested findings to HIL after threshold.

        D2 fix (Exp 38): also covers OPEN findings with old unresolved
        challenges — matching what contested_count() actually reports.
        Previously only checked explicit CONTESTED status, missing findings
        that contested_count counted via verdict history.
        """
        _SKIP = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
        escalated_ids = []
        for fid, entry in self.entries.items():
            if entry["status"] in _SKIP:
                continue
            # Path 1: explicit CONTESTED status (original logic)
            if entry["status"] == "CONTESTED":
                contested_since = entry.get("last_status_change_round", 0)
                rounds_contested = current_round - contested_since
                if rounds_contested >= max_contested_rounds:
                    self.resolve(fid, "UNCONFIRMED", current_round)
                    entry["hil_escalated"] = True
                    entry["hil_reason"] = (
                        f"Contested for {rounds_contested} rounds "
                        f"(threshold: {max_contested_rounds})"
                    )
                    escalated_ids.append(fid)
                    _log(f"  D2 HIL escalation: {fid} CONTESTED for "
                         f"{rounds_contested}r -> UNCONFIRMED + HIL flag")
                continue
            # Path 2: OPEN/REOPENED with stale unresolved challenges
            if entry["status"] in ("OPEN", "REOPENED"):
                challenges = [v for v in entry["verdicts"] if v["verdict"] == "CHALLENGE"]
                if not challenges:
                    continue
                confirms = [v for v in entry["verdicts"] if v["verdict"] == "CONFIRM"]
                latest_confirm = max((v["round"] for v in confirms), default=-1)
                unresolved = [v for v in challenges if v["round"] >= latest_confirm]
                if not unresolved:
                    continue
                oldest = min(v["round"] for v in unresolved)
                if current_round - oldest >= max_contested_rounds:
                    self.resolve(fid, "UNCONFIRMED", current_round)
                    entry["hil_escalated"] = True
                    entry["hil_reason"] = (
                        f"Unresolved challenge from R{oldest}, age "
                        f"{current_round - oldest} rounds "
                        f"(threshold: {max_contested_rounds})"
                    )
                    escalated_ids.append(fid)
                    _log(f"  D2 HIL escalation: {fid} unresolved challenge "
                         f"since R{oldest} -> UNCONFIRMED + HIL flag")
        return escalated_ids

    def auto_resolve_contested(self, current_round: int):
        for fid, entry in self.entries.items():
            if entry.get("status") != "CONTESTED":
                continue
            recent_verdicts = [
                v for v in entry.get("verdicts", [])
                if v.get("round", 0) >= current_round - 2
            ]
            challenges = sum(1 for v in recent_verdicts if v.get("verdict") == "CHALLENGE")
            confirms = sum(1 for v in recent_verdicts if v.get("verdict") == "CONFIRM")
            if challenges >= 3 and confirms == 0:
                # F6 fix: use resolve() instead of direct mutation.
                self.resolve(fid, "REFUTED", current_round)
                _log(f"  Auto-refuted {fid}: {challenges} challenges, 0 defences in last 3 rounds")

    def to_dict(self) -> dict:
        return {
            "entries": self.entries,
            "next_id": self._next_id,
            "alias_map": self._alias_map,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FindingRegistry":
        reg = cls()
        reg.entries = data.get("entries", {})
        reg._next_id = data.get("next_id", 1)
        reg._alias_map = data.get("alias_map", {})
        return reg


# ─────────────────────────────────────────────────────────────────────────────
# Verdict parser
# ─────────────────────────────────────────────────────────────────────────────

_VERDICT_RE = re.compile(
    # F13 fix: C\d{4,} supports IDs beyond 9999
    # F19 fix: bare | inside character class (no backslash needed)
    # 1D.6 fix: broadened Gemini format coverage. Original missed
    # bold-wrapped keyword alone (**CONFIRM**), bullet+bold combinations,
    # numbered-list prefixes (1. / 1)), blockquote prefixes (>), and
    # colon/period separators after the canonical ID.
    r'^[ \t]*'                                  # line start + indent
    r'(?:>[ \t]*)?'                             # optional blockquote
    r'(?:[-*][ \t]+|\d+[.)][ \t]+)?'            # optional bullet or numbered-list prefix
    r'(?:\*{1,2}|_{1,2})?'                      # optional bold/italic opener
    r'(CONFIRM|CHALLENGE|EXTEND|MERGE|REOPEN)'
    r'(?:\*{1,2}|_{1,2})?'                      # optional bold/italic closer on keyword
    r'[ \t]+'
    r'(?:\*{1,2}|_{1,2})?'                      # optional bold opener on canonical ID
    r'(C\d{4,})'
    r'(?:\*{1,2}|_{1,2})?'                      # optional bold closer on canonical ID
    # Optional description separator + description.
    # Separators now include `:` and `.` (Gemini uses both), in addition to
    # `|`, `<`, `-`, em-dash, en-dash, left-arrow.
    r'(?:[ \t]*(?:\*{1,2}|_{1,2})?[ \t]*[|<:.\-\u2014\u2013\u2190]+[ \t]*(.*))?',
    re.MULTILINE,
)


_VERDICT_TRAILING_FORMAT = re.compile(r'[\s*_]+$')


def _parse_verdicts(
    response_text: str, model_id: str, round_idx: int,
) -> List[Tuple[str, str, str]]:
    results: List[Tuple[str, str, str]] = []
    for m in _VERDICT_RE.finditer(response_text):
        description = (m.group(3) or "").strip()
        # Strip trailing markdown format chars (** / __) when the whole
        # verdict line was bold-wrapped.
        description = _VERDICT_TRAILING_FORMAT.sub("", description).strip()
        results.append((m.group(1), m.group(2), description))
    return results


def _resolve_merge_source(
    evidence: str, model_id: str, registry: FindingRegistry,
) -> Optional[str]:
    m = re.search(r'(?:F|C)(\d+)', evidence)
    if not m:
        return None
    local_id = m.group(0)
    canonical = registry.lookup_alias(model_id, local_id)
    if canonical:
        return canonical
    if local_id in registry.entries:
        return local_id
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Gamma estimation and convergence
# ─────────────────────────────────────────────────────────────────────────────

def _estimate_gamma(novelty_counts: List[int], min_rounds: int = 3) -> float:
    n = len(novelty_counts)
    if n < min_rounds:
        return 0.0
    cumulative = []
    total = 0
    for c in novelty_counts:
        total += c
        cumulative.append(total)
    if total == 0:
        return 0.0
    log_x, log_y = [], []
    for i, cum in enumerate(cumulative):
        if cum > 0 and (i + 1) > 0:
            log_x.append(math.log(i + 1))
            log_y.append(math.log(cum))
    if len(log_x) < 2:
        return 0.0
    n_pts = len(log_x)
    sum_x = sum(log_x)
    sum_y = sum(log_y)
    sum_xy = sum(x * y for x, y in zip(log_x, log_y))
    sum_x2 = sum(x * x for x in log_x)
    denom = n_pts * sum_x2 - sum_x * sum_x
    if abs(denom) < 1e-12:
        return 0.0
    beta = (n_pts * sum_xy - sum_x * sum_y) / denom
    return max(0.0, min(1.0, 1.0 - beta))


GAMMA_BANDS = [
    (0.45, float("inf"), "Strong depletion — confirms state-based closure"),
    (0.30, 0.45, "Moderate depletion — consistent with PoC convergence"),
    (0.20, 0.30, "Weak depletion — state closure may be premature"),
    (0.00, 0.20, "Gamma disagrees with state closure — recommend HIL audit"),
]


def _interpret_gamma(gamma: float) -> str:
    for low, high, interpretation in GAMMA_BANDS:
        if low <= gamma < high:
            return interpretation
    return f"Gamma {gamma:.3f} — outside expected range"


def _check_gamma_gate(
    gamma: float, round_idx: int, cfg: RunnerConfig,
) -> Tuple[str, bool]:
    if round_idx <= cfg.gamma_telemetry_only_until:
        return "telemetry", True
    if round_idx <= cfg.gamma_soft_gate_until:
        if gamma < cfg.gamma_soft_threshold:
            return "soft", False
        return "soft", True
    if gamma < cfg.gamma_hard_threshold:
        return "hard", False
    return "hard", True


def _compute_rho(
    novelty_counts: List[int],
    raw_counts: List[int],
    cfg: RunnerConfig,
) -> Tuple[float, float, bool]:
    """A2 fix: discovery efficiency rho with configurable threshold."""
    if not raw_counts:
        return 0.0, 0.0, False
    # Bug 1 fix: compute rolling average even when current round has zero raw.
    # A zero-raw round should drive the average DOWN, not freeze it.
    rho_current = novelty_counts[-1] / raw_counts[-1] if raw_counts[-1] > 0 else 0.0
    rho_values = []
    for i in range(max(0, len(raw_counts) - cfg.rho_rolling_window), len(raw_counts)):
        if raw_counts[i] > 0:
            rho_values.append(novelty_counts[i] / raw_counts[i])
        else:
            rho_values.append(0.0)
    rho_avg = sum(rho_values) / len(rho_values) if rho_values else 0.0
    # Bug 4 fix: len(raw_counts) is 1-based (one entry per completed round).
    # Using len-1 compared against a 1-based threshold delays churn by one round.
    round_number = len(raw_counts)
    churn = rho_avg < cfg.rho_threshold and round_number >= cfg.rho_earliest_round
    return rho_current, rho_avg, churn


# ─────────────────────────────────────────────────────────────────────────────
# Status transitions and convergence gate
# ─────────────────────────────────────────────────────────────────────────────

def _update_finding_statuses(registry: FindingRegistry, round_idx: int,
                             cfg: Optional[RunnerConfig] = None):
    # ── Pre-pass 1: Mark/clear EXHAUSTED on critical/high findings ──
    # Derived fresh each call — not sticky. Requires review activity.
    exhausted_threshold = cfg.exhausted_round_threshold if cfg else 0
    for e in registry.entries.values():
        if e["status"] in ("OPEN", "CONTESTED") and e["severity"] >= 0.7:
            age = round_idx - e.get("last_status_change_round", 0)
            has_reviews = len(e.get("verdicts", [])) > 0
            if exhausted_threshold > 0 and age >= exhausted_threshold and has_reviews:
                e["exhausted"] = True
            else:
                e["exhausted"] = False
        else:
            e.pop("exhausted", None)

    # ── Pre-pass 2: Reopen UNCONFIRMED findings with new evidence ──
    grace_period = 2
    for cid, e in list(registry.entries.items()):
        if e["status"] == "UNCONFIRMED":
            rounds_in_status = round_idx - e.get("last_status_change_round", 0)
            if rounds_in_status >= grace_period:
                status_round = e.get("last_status_change_round", 0)
                new_verdicts = [v for v in e["verdicts"] if v["round"] > status_round]
                if new_verdicts:
                    registry.resolve(cid, "OPEN", round_idx)
                    _log(f"  REOPEN {cid}: new evidence after UNCONFIRMED")

    # ── Main pass ──
    for canonical_id, entry in list(registry.entries.items()):
        # ── Terminal statuses: only CLOSED can be reopened ──
        if entry["status"] in ("MERGED", "CLOSED"):
            if entry["status"] == "CLOSED":
                reopen_verdicts = [
                    v for v in entry["verdicts"]
                    if v["verdict"] == "REOPEN" and v["round"] == round_idx
                ]
                if reopen_verdicts:
                    registry.resolve(canonical_id, "REOPENED", round_idx)
                    entry["escalated"] = True
                    _log(f"  REOPEN {canonical_id}: escalated to HIL")
            continue

        # ── MERGE: contextual quorum (Round 2 confer design) ──
        # Floor: never merge without target consensus. Never merge on 0 votes.
        # Contextual: 2+ models on same target = pass. 1 model on small panel
        # with high confidence = pass + HIL flag. Target disagreement = defer.
        merge_verdicts = [v for v in entry["verdicts"] if v["verdict"] == "MERGE"]
        if merge_verdicts:
            # Extract per-vote targets
            by_target: dict[str, list] = {}
            for v in merge_verdicts:
                m = re.search(r'merged_into=(C\d{4,})', v.get("evidence", ""))
                target = m.group(1) if m else "__unknown__"
                by_target.setdefault(target, []).append(v)

            if len(by_target) > 1:
                # D4 fix: quorum-based merge arbitration.
                # If one target has strictly more votes, merge to it.
                # On genuine tie, defer with HIL escalation after threshold.
                sorted_targets = sorted(by_target.items(),
                                        key=lambda kv: len(kv[1]), reverse=True)
                top_target, top_votes = sorted_targets[0]
                second_votes = len(sorted_targets[1][1]) if len(sorted_targets) > 1 else 0
                if (len(top_votes) > second_votes
                        and top_target != "__unknown__"):
                    distinct = {v["model"] for v in top_votes}
                    if len(distinct) >= 2:
                        registry.resolve(canonical_id, "MERGED", round_idx,
                                         merged_into=top_target)
                        _log(f"  D4 MERGE QUORUM {canonical_id} -> {top_target}: "
                             f"{len(top_votes)} votes vs {second_votes}")
                        continue
                # Genuine tie or insufficient quorum — defer
                defer_count = entry.get("merge_defer_count", 0) + 1
                entry["merge_defer_count"] = defer_count
                max_defer = cfg.max_contested_rounds if cfg else 5
                if defer_count >= max_defer:
                    # Deadlock: escalate to HIL, remove from active merge
                    entry["hil_escalated"] = True
                    entry["hil_reason"] = (
                        f"MERGE deadlock for {defer_count} rounds, "
                        f"targets: {', '.join(by_target.keys())}"
                    )
                    _log(f"  D4 MERGE DEADLOCK {canonical_id}: "
                         f"escalated to HIL after {defer_count} rounds")
                else:
                    _log(f"  MERGE DEFERRED {canonical_id}: target disagreement "
                         f"({', '.join(by_target.keys())}) [{defer_count}/{max_defer}]")
            else:
                target_id = next(iter(by_target))

                # R3-1 fix: block merge on unknown/unparseable targets
                if target_id == "__unknown__":
                    _log(f"  MERGE DEFERRED {canonical_id}: no parseable merge target")
                else:
                    target_votes = by_target[target_id]
                    distinct_models = {v["model"] for v in target_votes}
                    # R3-2 fix: panel size from config, not per-finding verdicts
                    external_panel_size = (
                        len(set(cfg.models) - {entry["source_model"]})
                        if cfg else len({v["model"] for v in entry["verdicts"]} - {entry["source_model"]})
                    )

                    if len(distinct_models) >= 2:
                        # Clear consensus — merge
                        registry.resolve(canonical_id, "MERGED", round_idx, merged_into=target_id)
                        continue
                    elif external_panel_size < 2 and len(distinct_models) == 1:
                        # Small panel: allow single vote + HIL flag + reversion gate
                        registry.resolve(canonical_id, "MERGED", round_idx, merged_into=target_id)
                        entry["hil_escalated"] = True
                        entry["hil_reason"] = (
                            f"Single-model merge (small panel, {external_panel_size} "
                            f"external models). Reversion available."
                        )
                        _log(f"  MERGED {canonical_id} (small panel, HIL flagged)")
                        continue
                    # else: insufficient quorum, do not merge this round

        # ── Collect verdict evidence ──
        confirms = [v for v in entry["verdicts"] if v["verdict"] == "CONFIRM"]
        challenges = [v for v in entry["verdicts"] if v["verdict"] == "CHALLENGE"]
        latest_confirm_round = max((v["round"] for v in confirms), default=-1)
        # F24 fix: use >= so same-round challenges count as unresolved.
        # Previously strict > meant a challenge in the same round as the
        # latest confirm was silently treated as resolved.
        unresolved_challenges = [v for v in challenges if v["round"] >= latest_confirm_round]

        # ── F0/F4 fix: check challenges BEFORE closing ──
        # Previously, CONFIRMED+verified closed immediately, skipping the
        # challenge check. Now: unresolved challenges take priority.
        if entry["status"] == "CONFIRMED" and unresolved_challenges:
            registry.resolve(canonical_id, "CONTESTED", round_idx)
            continue
        if entry["status"] == "CONFIRMED" and entry.get("verified"):
            registry.resolve(canonical_id, "CLOSED", round_idx)
            _log(f"  CLOSED {canonical_id}: verified fix, no unresolved challenges")
            continue

        if entry["status"] == "CONTESTED" and not unresolved_challenges:
            registry.resolve(canonical_id, "CONFIRMED", round_idx)
            continue

        # F18 fix: use resolve() instead of direct mutation for REOPENED → OPEN.
        # Direct entry["status"] = "OPEN" bypassed last_status_change_round update.
        if entry["status"] == "REOPENED":
            registry.resolve(canonical_id, "OPEN", round_idx)

        if entry["status"] in ("OPEN", "CONTESTED"):
            confirm_models = {v["model"] for v in confirms}
            # F11 contextual: severity-based confirmation quorum.
            # Floor: at least 1 independent external confirmation (source excluded).
            # Critical/High: require 2. Medium/Low: require 1.
            # R3-4 fix: cap by available external panel size to prevent stalls.
            independent_count = len(confirm_models - {entry["source_model"]})
            sev = entry.get("severity", 0.5)
            external_panel_size = (
                len(set(cfg.models) - {entry["source_model"]})
                if cfg else 99
            )
            required = min(2, external_panel_size) if sev >= 0.7 else 1
            if independent_count >= required and not unresolved_challenges:
                registry.resolve(canonical_id, "CONFIRMED", round_idx)


def _evaluate_gate_conditions(
    round_idx: int,
    registry: FindingRegistry,
    novel_this_round: int,
    gamma: float,
    cfg: RunnerConfig,
    open_ch_history: Optional[List[int]] = None,
    rho_rolling_avg: float = 1.0,
    rho_churn: bool = False,
) -> Tuple[bool, str]:
    if round_idx < cfg.earliest_stop_round:
        return False, f"Too early (round {round_idx} < {cfg.earliest_stop_round})"
    failures = []
    if rho_churn:
        failures.append(f"rho_avg={rho_rolling_avg:.3f} < {cfg.rho_threshold} (churn)")
    # F7/F23 contextual gate (GE EXHAUSTED design): gate threshold stays fixed.
    # EXHAUSTED marking now done by _update_finding_statuses() pre-pass.
    open_ch = registry.open_crit_high_count()

    # F12 fix: guard against duplicate entries if called multiple times per round.
    if open_ch_history is not None:
        if not open_ch_history or open_ch_history[-1] != open_ch:
            open_ch_history.append(open_ch)

    # F7/F23 fix: enforce cfg.max_open_crit_high threshold (gate stays fixed).
    if open_ch > cfg.max_open_crit_high:
        failures.append(
            f"open_ch={open_ch} > max={cfg.max_open_crit_high}"
        )
    elif open_ch_history is None or len(open_ch_history) < cfg.open_ch_stability_window:
        if open_ch > 0:
            failures.append(f"open_ch={open_ch} (insufficient history)")
    else:
        window = open_ch_history[-cfg.open_ch_stability_window:]
        if window[-1] > window[0]:
            failures.append(
                f"open_ch={open_ch} (increasing: "
                f"{window[0]}->{window[-1]} over {cfg.open_ch_stability_window}r)"
            )
    if novel_this_round > cfg.max_novel_findings:
        failures.append(f"novel={novel_this_round}")
    contested = registry.contested_count(round_idx)
    if contested > 0:
        failures.append(f"contested={contested}")
    gate_level, gamma_passed = _check_gamma_gate(gamma, round_idx, cfg)
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
    cfg: RunnerConfig,
    open_ch_history: Optional[List[int]] = None,
    rho_rolling_avg: float = 1.0,
    rho_churn: bool = False,
) -> Tuple[bool, str]:
    passed, reason = _evaluate_gate_conditions(
        round_idx, registry, novel_this_round, gamma, cfg,
        open_ch_history=open_ch_history,
        rho_rolling_avg=rho_rolling_avg,
        rho_churn=rho_churn,
    )
    gate_history.append(passed)
    if not passed:
        return False, reason
    if len(gate_history) < cfg.consecutive_rounds_required:
        return False, f"Gate passed but need {cfg.consecutive_rounds_required} consecutive"
    recent = gate_history[-cfg.consecutive_rounds_required:]
    if all(recent):
        return True, (
            f"STATE_CONVERGED at round {round_idx} "
            f"({cfg.consecutive_rounds_required} consecutive passes): {reason}"
        )
    return False, f"Gate passed this round but not {cfg.consecutive_rounds_required} consecutive"


def _check_gamma_alt_convergence(
    round_idx: int,
    gamma: float,
    novel_critical_history: List[int],
    cfg: RunnerConfig,
) -> Tuple[bool, str]:
    """γ-based alternative convergence path (Exp 40 fix, Item 1A.3).

    Documented in Exp 39 sub-experiment configs as an alternative pass
    condition but previously never implemented in code. The Exp 39-0
    post-mortem flagged this as P0: the main gate requires
    ``open_ch <= max_open_crit_high`` which was structurally unreachable
    at threshold 0; even with the threshold bumped to 5, depletion on
    high-severity findings can be slow enough to time out on wall clock.

    Fires when EITHER:
      (1) gamma (Duane depletion estimate) >= cfg.gamma_alt_threshold, OR
      (2) cfg.gamma_alt_consecutive_zero_crit consecutive rounds have
          produced zero novel CRITICAL findings (severity >= 0.7).

    These conditions are OR (either is sufficient), matching the config
    text. Condition 1 captures cumulative depletion; condition 2 captures
    round-level critical-severity exhaustion.

    Returns (converged, reason).
    """
    if round_idx < cfg.gamma_alt_earliest_round:
        return False, (
            f"γ-alt too early (round {round_idx} < "
            f"{cfg.gamma_alt_earliest_round})"
        )

    # Condition 1: gamma threshold
    if gamma >= cfg.gamma_alt_threshold:
        return True, (
            f"GAMMA_ALT_CONVERGED: gamma={gamma:.3f} >= "
            f"{cfg.gamma_alt_threshold} at round {round_idx}"
        )

    # Condition 2: consecutive zero novel CRITICAL
    window = cfg.gamma_alt_consecutive_zero_crit
    if len(novel_critical_history) >= window:
        recent = novel_critical_history[-window:]
        if all(n == 0 for n in recent):
            return True, (
                f"GAMMA_ALT_CONVERGED: {window} consecutive rounds "
                f"with zero novel CRITICAL (history tail={recent}) "
                f"at round {round_idx}"
            )

    # Neither condition met
    recent_tail = (
        novel_critical_history[-window:]
        if len(novel_critical_history) >= window
        else novel_critical_history
    )
    return False, (
        f"γ-alt not met: gamma={gamma:.3f} < {cfg.gamma_alt_threshold}; "
        f"novel_crit_recent={recent_tail}"
    )


def _check_stall_convergence(
    round_idx: int,
    registry: FindingRegistry,
    gamma: float,
    stall_history: List[Dict[str, int]],
    cfg: RunnerConfig,
    consecutive_churn_rounds: int = 0,
) -> Dict[str, Any]:
    open_ch = registry.open_crit_high_count()
    contested = registry.contested_count(round_idx)
    stall_history.append({"open_ch": open_ch, "contested": contested})
    result: Dict[str, Any] = {
        "round": round_idx, "open_ch": open_ch, "contested": contested,
        "gamma": round(gamma, 4), "stalled": False,
        "tier": "none", "terminate": False, "reason": "",
    }
    if round_idx < cfg.stall_earliest_round:
        result["reason"] = f"round {round_idx} < {cfg.stall_earliest_round}"
        return result
    if len(stall_history) < cfg.stall_window:
        result["reason"] = f"insufficient history ({len(stall_history)} < {cfg.stall_window})"
        return result

    # D1-B: churn-based stall detection.
    # Persistent churn with high gamma is a stall signal even when
    # open_ch/contested fluctuate — the system is producing re-derivations,
    # not genuine novelty.
    churn_stall_window = max(cfg.stall_window, 4)  # at least 4 rounds of churn
    if (consecutive_churn_rounds >= churn_stall_window
            and gamma >= cfg.stall_gamma_terminate):
        result["stalled"] = True
        result["tier"] = "terminate"
        result["terminate"] = True
        result["reason"] = (
            f"STALL_CONVERGED (churn): {consecutive_churn_rounds} consecutive "
            f"churn rounds, gamma={gamma:.3f} >= {cfg.stall_gamma_terminate}"
        )
        return result
    if (consecutive_churn_rounds >= churn_stall_window
            and gamma >= cfg.stall_gamma_advisory):
        result["stalled"] = True
        result["tier"] = "advisory"
        result["reason"] = (
            f"Stall advisory (churn): {consecutive_churn_rounds} consecutive "
            f"churn rounds, gamma={gamma:.3f} >= {cfg.stall_gamma_advisory}"
        )
        return result

    window = stall_history[-cfg.stall_window:]
    open_values = [s["open_ch"] for s in window]
    contested_values = [s["contested"] for s in window]
    if not (all(v == open_values[0] for v in open_values) and
            all(v == contested_values[0] for v in contested_values)):
        result["reason"] = f"not static — open_ch {open_values}, contested {contested_values}"
        return result
    result["stalled"] = True
    if gamma >= cfg.stall_gamma_terminate:
        result["tier"] = "terminate"
        result["terminate"] = True
        result["reason"] = (
            f"STALL_CONVERGED: open_ch={open_ch} static {cfg.stall_window}r, "
            f"contested={contested} static {cfg.stall_window}r, "
            f"gamma={gamma:.3f} >= {cfg.stall_gamma_terminate}"
        )
    elif gamma >= cfg.stall_gamma_advisory:
        result["tier"] = "advisory"
        result["reason"] = (
            f"Stall advisory: open_ch={open_ch} static {cfg.stall_window}r, "
            f"gamma={gamma:.3f} >= {cfg.stall_gamma_advisory}"
        )
    else:
        result["tier"] = "stalled_low_gamma"
        result["reason"] = (
            f"Stalled but gamma={gamma:.3f} < {cfg.stall_gamma_advisory} "
            f"(discovery space may not be depleted)"
        )
    return result


def _check_budget_extension(
    round_idx: int,
    registry: FindingRegistry,
    gamma: float,
    gamma_prev: float,
) -> Tuple[bool, str]:
    reasons = []
    if registry.open_crit_high_count() > 0:
        reasons.append(f"open CRIT/HIGH: {registry.open_crit_high_count()}")
    if registry.contested_count(round_idx) > 0:
        reasons.append(f"contested: {registry.contested_count(round_idx)}")
    if 0.25 <= gamma <= 0.35 and gamma > gamma_prev:
        reasons.append(f"gamma trending up in caution zone: {gamma:.3f}")
    if reasons:
        return True, f"Budget extended: {'; '.join(reasons)}"
    return False, "No extension triggers"


# ─────────────────────────────────────────────────────────────────────────────
# ITC — Adaptive Recovery (A4: gamma-aware)
# ─────────────────────────────────────────────────────────────────────────────

ITC_CAPABILITY_MISMATCH = "CAPABILITY_MISMATCH"
ITC_TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
ITC_DEGRADATION = "DEGRADATION"

_itc_model_state: Dict[str, Dict[str, Any]] = {}
_itc_hil_flags: List[Dict[str, Any]] = []


_FINDING_DECL_RE = re.compile(
    r'(?:FINDING.ID\s*[:=]|<<<\s*FINDING\b|\(F\d{2,4}[,)])',
    re.IGNORECASE
)


def _itc_detect(
    model_label: str, round_idx: int,
    findings_count: int, response_text: str,
    prior_finding_ids: Set[str], current_finding_ids: Set[str],
    dispatch_error: Optional[str] = None,
    raw_finding_markers: int = 0,
    verdict_count: int = 0,
) -> Optional[str]:
    if dispatch_error and ("context length" in dispatch_error.lower()
                           or "token" in dispatch_error.lower()):
        return ITC_CAPABILITY_MISMATCH
    if not response_text or len(response_text.strip()) < 50:
        return ITC_TRANSIENT_FAILURE
    if findings_count == 0 and len(response_text) > 200:
        history = _itc_model_state.get(model_label, {}).get("history", [])
        recent_empty = sum(1 for h in history[-2:] if h.get("findings") == 0)
        if recent_empty >= 1:
            return ITC_CAPABILITY_MISMATCH
        return ITC_TRANSIENT_FAILURE
    # D5 fix: output quality signal — adaptive, per-model.
    # Parse yield = (findings_count + verdict_count) / raw_finding_markers.
    # In late rounds, models shift from producing new findings to issuing
    # verdicts (CONFIRM/CHALLENGE) on existing findings.  Verdicts are
    # valid structured output that the parser captures, so they count
    # towards productive yield.  Without this, verdict-heavy rounds
    # deflate parse_yield and cause false DEGRADATION flags.
    #
    # Each model's baseline yield is computed from its own history.
    # Degradation = yield drops significantly below the model's own
    # baseline, OR falls below a hard floor (0.5) regardless of baseline.
    # "Significantly" = more than 0.25 below the rolling average.
    #
    # Cold start (< 3 history entries): use hard floor only.
    # This avoids penalising models during the first rounds before
    # a baseline exists, while still catching severe degradation.
    if raw_finding_markers >= 2:
        parse_yield = (findings_count + verdict_count) / raw_finding_markers
        # Record yield in ITC state for baseline computation.
        state = _itc_model_state.setdefault(model_label, {
            "history": [], "adaptation": None, "retry_count": 0,
            "escalation_level": 0,
        })
        yield_history = state.setdefault("parse_yield_history", [])
        yield_history.append(parse_yield)
        if len(yield_history) > 20:
            state["parse_yield_history"] = yield_history[-20:]
            yield_history = state["parse_yield_history"]

        # Hard floor: any model below 0.5 is degraded, no exceptions.
        _HARD_FLOOR = 0.5
        # Adaptive threshold: baseline minus deviation margin.
        _DEVIATION_MARGIN = 0.25

        if len(yield_history) >= 4:
            # Baseline = mean of the best 3 of last 5 yields (excludes
            # worst outliers while tracking recent performance).
            #
            # KNOWN TRADE-OFF: "best 3 of 5" is robust against single
            # bad rounds but blind to sustained gradual degradation.
            # At degradation rates below ~9% per round, the adaptive
            # threshold never fires before the hard floor — the filter
            # absorbs the decline by discarding the worst values, which
            # ARE the signal. At 9%+ per round, the adaptive threshold
            # catches the model 2-3 rounds before the floor would.
            #
            # The adaptive threshold detects sharp drops. The hard
            # floor (0.5) is the safety net for gradual decline.
            # Context overload — models fed more context than they
            # can handle — causes gradual decline, so the floor is
            # load-bearing in that scenario.
            #
            # Verified numerically, Exp 39 R3 confer (2026-04-11).
            recent = yield_history[-5:] if len(yield_history) >= 5 else yield_history[:]
            baseline = sum(sorted(recent, reverse=True)[:3]) / 3
            adaptive_threshold = max(_HARD_FLOOR, baseline - _DEVIATION_MARGIN)
        else:
            # Cold start: hard floor only.
            baseline = None
            adaptive_threshold = _HARD_FLOOR

        # Store threshold for the fingerprint quality gate (DRY:
        # avoids recomputing the same baseline/threshold there).
        state["last_adaptive_threshold"] = adaptive_threshold

        if parse_yield < adaptive_threshold:
            baseline_str = f"baseline={baseline:.2f}, " if baseline is not None else ""
            verdict_str = f", verdicts={verdict_count}" if verdict_count else ""
            _log(f"  ITC [{model_label}]: parse yield {parse_yield:.2f} "
                 f"({findings_count}+{verdict_count}/{raw_finding_markers} markers{verdict_str}, "
                 f"{baseline_str}threshold={adaptive_threshold:.2f}) — DEGRADATION")
            return ITC_DEGRADATION
    if prior_finding_ids and current_finding_ids:
        overlap = len(current_finding_ids & prior_finding_ids)
        if len(current_finding_ids) > 0:
            overlap_rate = overlap / len(current_finding_ids)
            if overlap_rate > 0.4:
                return ITC_DEGRADATION
    return None


def _itc_consecutive_failures(model_label: str) -> int:
    history = _itc_model_state.get(model_label, {}).get("history", [])
    count = 0
    for entry in reversed(history):
        if entry.get("classification"):
            count += 1
        else:
            break
    return count


def _itc_adapt(
    model_label: str, classification: str, round_idx: int,
    rho_rolling_avg: float = 1.0,
    rho_threshold: float = 0.25,
):
    """A4 fix: suppress DEGRADATION restart when rho is healthy."""
    state = _itc_model_state.setdefault(model_label, {
        "history": [], "adaptation": None, "retry_count": 0,
        "escalation_level": 0,
    })
    state["history"].append({
        "round": round_idx, "classification": classification, "findings": 0,
    })
    consecutive = _itc_consecutive_failures(model_label)
    if classification == ITC_TRANSIENT_FAILURE:
        if state["retry_count"] < 1:
            state["adaptation"] = "retry"
            state["retry_count"] += 1
        elif consecutive < 3:
            state["adaptation"] = "strip_context"
            state["retry_count"] = 0
        else:
            state["adaptation"] = "restart_fresh"
            state["retry_count"] = 0
    elif classification == ITC_CAPABILITY_MISMATCH:
        current = state.get("adaptation")
        if current != "strip_context" and current != "section_assign":
            state["adaptation"] = "strip_context"
        elif current == "strip_context":
            state["adaptation"] = "section_assign"
        else:
            state["adaptation"] = "restart_fresh"
    elif classification == ITC_DEGRADATION:
        if rho_rolling_avg >= rho_threshold:
            _log(f"  ITC [{model_label}]: {classification} suppressed — "
                 f"rho_avg={rho_rolling_avg:.3f} >= {rho_threshold} (normal depletion)")
            state["adaptation"] = None
        elif consecutive < 2:
            state["adaptation"] = "change_focus"
        else:
            state["adaptation"] = "restart_fresh"
    if consecutive >= 3:
        _itc_flag_underperformer(model_label, round_idx, classification, consecutive)


def _itc_flag_underperformer(
    model_label: str, round_idx: int, classification: str, consecutive: int,
):
    flag = {
        "model": model_label, "round": round_idx,
        "classification": classification, "consecutive_failures": consecutive,
        "message": (
            f"{model_label} has {consecutive} consecutive ITC interventions "
            f"(latest: {classification}). Flagged for HIL review."
        ),
    }
    _itc_hil_flags.append(flag)
    _log(f"  *** HIL FLAG: {flag['message']} ***")


def _itc_get_adaptation(model_label: str) -> Optional[str]:
    return _itc_model_state.get(model_label, {}).get("adaptation")


def _itc_clear_adaptation(model_label: str):
    state = _itc_model_state.get(model_label)
    if state:
        state["adaptation"] = None
        state["retry_count"] = 0


def _build_change_focus_instruction(registry: FindingRegistry, round_idx: int) -> str:
    status_counts: Dict[str, int] = {}
    for entry in registry.entries.values():
        s = entry["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    open_count = status_counts.get("OPEN", 0) + status_counts.get("CONTESTED", 0)
    confirmed = status_counts.get("CONFIRMED", 0)
    total = len(registry.entries)
    needs_verdict = []
    for cid, entry in registry.entries.items():
        if entry["status"] == "OPEN":
            confirm_count = sum(
                1 for v in entry.get("verdicts", []) if v.get("verdict") == "CONFIRM"
            )
            if confirm_count == 0:
                needs_verdict.append(f"{cid} ({entry['description'][:60]})")
    parts = [
        "=== FOCUS REDIRECT (you are repeating yourself) ===\n",
        f"The registry has {total} canonical findings: {confirmed} CONFIRMED, "
        f"{open_count} OPEN/CONTESTED.\n\nSTOP describing known bugs. Instead:\n",
    ]
    if needs_verdict:
        verdict_list = "\n".join(f"  - {nv}" for nv in needs_verdict[:8])
        parts.append(
            f"1. These {len(needs_verdict)} OPEN findings need verdicts:\n"
            f"{verdict_list}\n\n"
        )
    parts.append(
        "2. Issue MERGE <ID> <- <ID> for same-root-cause findings.\n\n"
        "3. File genuinely new findings only if not already in the registry.\n\n"
        "=== END FOCUS REDIRECT ===\n"
    )
    return "".join(parts)


def _itc_build_recovery_prompt(
    model_label: str, base_prompt: str,
    observed_fingerprints: Dict[str, Dict[str, Any]], round_idx: int,
) -> str:
    fp = observed_fingerprints.get(model_label, {})
    # Fix C: use measured prompt size, not response size.
    # max_successful_context_chars was misnamed — it stored response length.
    # max_successful_prompt_chars stores actual prompt size sent to the model.
    # Fall back to the old field if prompt data hasn't accumulated yet.
    max_ok_chars = fp.get("max_successful_prompt_chars", 0)
    if max_ok_chars == 0:
        max_ok_chars = fp.get("max_successful_context_chars", 0)
    if max_ok_chars > 0 and len(base_prompt) > max_ok_chars:
        artifact_start = base_prompt.find("=== ARTIFACT:")
        if artifact_start > 0:
            preamble = base_prompt[:min(2000, artifact_start)]
            artifact = base_prompt[artifact_start:]
            return (
                f"{preamble}\n\n"
                f"(Recovery dispatch — context reduced to ~{max_ok_chars:,} chars.)\n\n"
                f"Focus on the most impactful findings. Quality over quantity.\n\n"
                f"{artifact}"
            )
    return f"{base_prompt}\n\n(Fresh instance — focus on your strongest area.)\n"


# ─────────────────────────────────────────────────────────────────────────────
# Fingerprints
# ─────────────────────────────────────────────────────────────────────────────

def _load_fingerprints() -> Dict[str, Dict[str, Any]]:
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


def _save_fingerprints(observed: Dict[str, Dict[str, Any]], experiment_name: str):
    FINGERPRINT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    for model_id, obs in observed.items():
        fp_data = {
            "model_id": model_id, "experiment": experiment_name,
            "timestamp": ts, "observed": obs,
        }
        fp_path = FINGERPRINT_DIR / f"{model_id}.json"
        fp_path.write_text(json.dumps(fp_data, indent=2), encoding="utf-8")
    _log(f"  Fingerprints saved: {len(observed)} models -> {FINGERPRINT_DIR}")
    # Invalidate decomposition cache so next _should_decompose() call
    # sees the updated fingerprint data.
    _invalidate_fingerprint_cache()


def _update_observed_fingerprint(
    observed: Dict[str, Dict[str, Any]], model_label: str, round_idx: int,
    findings_count: int, response_chars: int,
    prompt_chars: int = 0,
    raw_finding_markers: int = 0,
    dispatch_error: Optional[str] = None,
):
    fp = observed.setdefault(model_label, {
        "max_successful_context_chars": 0, "max_failed_context_chars": 0,
        "max_successful_prompt_chars": 0, "max_failed_prompt_chars": 0,
        "prompt_chars_history": [],
        "failure_modes": [], "total_findings": 0,
        "rounds_participated": 0, "avg_findings_per_round": 0.0,
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
                fp.get("max_failed_context_chars", 0), response_chars)
            if prompt_chars > 0:
                fp["max_failed_prompt_chars"] = max(
                    fp.get("max_failed_prompt_chars", 0), prompt_chars)
            if "context_overflow" not in fp.get("failure_modes", []):
                fp.setdefault("failure_modes", []).append("context_overflow")
    elif response_chars > 0:
        fp["max_successful_context_chars"] = max(
            fp.get("max_successful_context_chars", 0), response_chars)
        if prompt_chars > 0:
            # Quality gate: compute FIRST, then apply to both
            # max_successful_prompt_chars AND history updates.
            # Exp 40 fix 1B.2: previously max_successful_prompt_chars was
            # updated unconditionally when response_chars > 0. That let
            # DeepSeek chunked-dispatch successes inflate the fingerprint
            # from the 0-char-chunk decomposition trap, causing
            # _should_decompose to re-decompose on subsequent monolithic
            # payloads of similar size. Now the update is gated on the
            # same parse-yield threshold as prompt_chars_history.
            quality_ok = True
            if raw_finding_markers >= 2:
                _py = findings_count / raw_finding_markers
                _state = _itc_model_state.get(model_label, {})
                _thresh = _state.get("last_adaptive_threshold", 0.5)
                if _py < _thresh:
                    quality_ok = False
            if quality_ok:
                fp["max_successful_prompt_chars"] = max(
                    fp.get("max_successful_prompt_chars", 0), prompt_chars)
            history = fp.setdefault("prompt_chars_history", [])
            if quality_ok:
                history.append(prompt_chars)
            # Cap history at 50 entries to bound memory.
            if len(history) > 50:
                fp["prompt_chars_history"] = history[-50:]


# ─────────────────────────────────────────────────────────────────────────────
# Topology instruction templates
# ─────────────────────────────────────────────────────────────────────────────

_POC_CONTEXT_INSTRUCTION = (
    "SYSTEM CONTEXT — PROOF OF CONCEPT (MANDATORY):\n"
    "This codebase is a proof-of-concept, not production software. Focus on "
    "CRITICAL (blocks operation) and HIGH (silently wrong results). File MEDIUM "
    "only if quick to fix. Ignore LOW entirely.\n\n"
)

_MACHINE_COMMS_INSTRUCTION = (
    "INTER-MODEL COMMUNICATION PROTOCOL (MANDATORY):\n"
    "No social pleasantries. For cross-model references, use structured verdicts:\n"
    "  CONFIRM C0001 — you agree the finding and fix are correct\n"
    "  CHALLENGE C0001 | [evidence] — the finding or fix is wrong\n"
    "  EXTEND C0001 | [new consequence or edge case]\n"
    "  MERGE C0001 <- [your_finding_id] — same root cause, combining\n"
    "Reference findings by CANONICAL ID (C0001, C0002, ...) from the registry.\n\n"
)

_GOOD_ENOUGH_INSTRUCTION = (
    "GOOD ENOUGH PRINCIPLE (MANDATORY):\n"
    "Converge on the simplest sufficient fix. Do NOT propose multiple alternatives. "
    "If another model has a correct fix, CONFIRM it. Before filing new findings, "
    "check the registry — CONFIRM or EXTEND instead of duplicating.\n\n"
)

_STAR_TOPOLOGY_INSTRUCTION = (
    "COMMUNICATION TOPOLOGY — STAR/BLACKBOARD (MANDATORY):\n"
    "You see a FINDING REGISTRY maintained by the runner, not other models' prose. "
    "File DISCOVERY findings for new bugs. Issue VERDICT payloads on existing entries. "
    "Do NOT address other models directly.\n\n"
)

_RELAY_TOPOLOGY_INSTRUCTION = (
    "COMMUNICATION TOPOLOGY — RELAY/DIRECT CONVERSATION:\n"
    "You see the FULL analysis from other models. CHALLENGE weak claims, CONFIRM "
    "strong findings, EXTEND insights, file new DISCOVERY findings for bugs nobody "
    "found. Use @ModelName for direct address. Also issue structured VERDICT "
    "payloads for registry tracking.\n\n"
)


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch helpers
# ─────────────────────────────────────────────────────────────────────────────

def _compose_for_model(
    model_label: str, pattern_name: str, domain: str,
) -> ComposedDirectiveSet:
    composer_model = COMPOSER_MODEL_MAP.get(model_label, model_label)
    situation = build_interaction_pattern(pattern_name)
    return compose(task_domain=domain, model=composer_model, situation=situation)


def _multiturn_fallback(
    mc: ModelConfig, prompt: str, cdsfl_text: str,
    full_code: str, round_idx: int, pattern_text: str,
    logs_dir: Path,
) -> Optional[Tuple[str, float]]:
    try:
        chunks = [
            DecomposedChunk(content=part, label=f"target_{i}")
            for i, part in enumerate(
                re.split(r'\n\n===\s+(?:TARGET|CONTEXT)\s+', full_code)
            )
            if part.strip()
        ]
        if not chunks:
            return None
        result = decomposed_dispatch(
            api=mc.api, model_id=mc.model_id, system_prompt=cdsfl_text,
            chunks=chunks, final_instruction=f"{pattern_text}\n\n{prompt}",
            max_tokens=mc.max_tokens, timeout=mc.timeout * 2,
            cdsfl_directives=cdsfl_text,
        )
        save_decomposed_result(result, logs_dir, mc.label, round_idx)
        return result.text, result.elapsed_s
    except Exception as e:
        _log(f"  {mc.label}: multi-turn FAILED — {type(e).__name__}: {e}")
        return None


def _dispatch_single_model(
    mc: ModelConfig, mgr: DynamicManager, prompt: str,
    cdsfl_text: str, full_code: str, round_idx: int,
    pattern_name: str, domain: str, logs_dir: Path,
) -> Tuple[List[Finding], Optional[str]]:
    try:
        composed = _compose_for_model(mc.label, pattern_name, domain)
        model_cdsfl = composed.rendered_text
    except Exception:
        model_cdsfl = cdsfl_text
    # Append operational directive AFTER composer phenotype transforms.
    # The operational directive (R_k self-assessment, MUST-compute instruction)
    # is not subject to phenotype char caps — all models receive it in full.
    # (Mirrors run_exp37_evidence.py lines 2195-2196)
    if _OPERATIONAL_DIRECTIVE_TEXT:
        model_cdsfl += "\n\n" + _OPERATIONAL_DIRECTIVE_TEXT

    pattern_text = INTERACTION_PATTERN_PRESETS[pattern_name][0]

    # Payload-aware decomposition (Exp 39 confound fix, 13 April 2026):
    # total payload = system prompt + user prompt (which already embeds full_code
    # via _build_prompt). Do NOT add full_code again — that double-counts ~64K.
    _total_payload_chars = len(model_cdsfl) + len(prompt)
    if should_decompose_v2(
        mc.label, mgr, payload_chars=_total_payload_chars,
    ):
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text, logs_dir)
        if fallback is not None:
            text, elapsed = fallback
            _record_throughput(mc.label, len(prompt), elapsed)
            model_findings = parse_findings(mc.label, round_idx, text)
            logs_dir.mkdir(parents=True, exist_ok=True)
            save_output(
                logs_dir, f"r{round_idx}", mc.label, prompt[:200] + "...", text,
                metadata={"round": round_idx, "elapsed": round(elapsed, 1),
                          "chars": len(text), "findings_count": len(model_findings),
                          "decomposed": True, "multiturn": True})
            return model_findings, text

    wall_limit = mc.timeout * 5 if mc.label == "CC2" else mc.timeout * 3
    try:
        text, elapsed = dispatch_to_model(mc, prompt, model_cdsfl, wall_clock_limit=wall_limit)
        _record_throughput(mc.label, len(prompt), elapsed)
        model_findings = parse_findings(mc.label, round_idx, text)
        logs_dir.mkdir(parents=True, exist_ok=True)
        save_output(
            logs_dir, f"r{round_idx}", mc.label, prompt[:200] + "...", text,
            metadata={"round": round_idx, "elapsed": round(elapsed, 1),
                      "chars": len(text), "findings_count": len(model_findings),
                      "decomposed": False})
        return model_findings, text
    except (CircuitBreakerTripped, TimeoutError, Exception) as e:
        _log(f"  {mc.label}: {type(e).__name__} — {e}")
        fallback = _multiturn_fallback(
            mc, prompt, model_cdsfl, full_code, round_idx, pattern_text, logs_dir)
        if fallback is not None:
            text, elapsed = fallback
            _record_throughput(mc.label, len(prompt), elapsed)
            model_findings = parse_findings(mc.label, round_idx, text)
            logs_dir.mkdir(parents=True, exist_ok=True)
            save_output(
                logs_dir, f"r{round_idx}", mc.label, prompt[:200] + "...", text,
                metadata={"round": round_idx, "elapsed": round(elapsed, 1),
                          "chars": len(text), "findings_count": len(model_findings),
                          "decomposed": True, "multiturn": True})
            return model_findings, text
        return [], f"__DISPATCH_FAILED__:{type(e).__name__}: {e}"


def _dispatch_round_star(
    exp_config: ExperimentConfig, mgr: DynamicManager, brain: InsectBrain,
    base_prompt: str, registry_summary: str, cdsfl_text: str, full_code: str,
    round_idx: int, cfg: RunnerConfig,
    registry: Optional[FindingRegistry] = None,
    feedback_sections: Optional[Dict[str, str]] = None,
) -> Tuple[List[Finding], Dict[str, str], Dict[str, float]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    per_model_durations: Dict[str, float] = {}
    baseline = set(cfg.models)
    eligible = [mc for mc in exp_config.models
                if mc.label in baseline and mc.role != "collator"]

    # Feedback channel (cdsfl_operational.md §17): close the loop between
    # schema judgment and model behaviour by surfacing per-model flagged
    # findings from round K-1 at the top of round K's prompt. Models must
    # address these before resubmitting — hope-based compliance is over.
    feedback_sections = feedback_sections or {}

    def _make_prompt(mc_label: str) -> str:
        if round_idx == 0:
            return base_prompt
        adaptation = _itc_get_adaptation(mc_label)
        focus_prefix = ""
        if adaptation == "change_focus" and registry is not None:
            focus_prefix = _build_change_focus_instruction(registry, round_idx)
        feedback_prefix = feedback_sections.get(mc_label, "")
        if feedback_prefix:
            feedback_prefix = feedback_prefix + "\n"
        star_section = (
            f"{registry_summary}\n\n"
            f"This is Round {round_idx}. Review the registry above. "
            f"File new DISCOVERY findings. Issue VERDICT payloads on existing entries.\n"
        )
        combined = f"{feedback_prefix}{focus_prefix}{star_section}"
        if "=== ARTIFACT:" in base_prompt:
            return base_prompt.replace("=== ARTIFACT:", f"{combined}=== ARTIFACT:")
        return f"{base_prompt}\n\n{combined}"

    logs_dir = brain.logs_dir
    prompt_lengths: Dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        start_times: Dict[str, float] = {}
        for mc in eligible:
            prompt = _make_prompt(mc.label)
            prompt_lengths[mc.label] = len(prompt) + len(cdsfl_text)
            start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model, mc, mgr, prompt,
                cdsfl_text, full_code, round_idx, cfg.pattern, cfg.domain, logs_dir,
            )] = mc.label

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            elapsed = time.monotonic() - start_times[label]
            per_model_durations[label] = elapsed
            try:
                mf, text = future.result()
                findings.extend(mf)
                if text and not text.startswith("__DISPATCH_FAILED__:"):
                    responses[label] = text
            except Exception as e:
                _log(f"  {label}: thread error — {type(e).__name__}: {e}")

    return findings, responses, per_model_durations, prompt_lengths


def _dispatch_round_relay(
    exp_config: ExperimentConfig, mgr: DynamicManager, brain: InsectBrain,
    base_prompt: str, cdsfl_text: str, full_code: str,
    round_idx: int, cfg: RunnerConfig,
    registry: Optional[FindingRegistry] = None,
) -> Tuple[List[Finding], Dict[str, str], Dict[str, float]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    findings: List[Finding] = []
    responses: Dict[str, str] = {}
    per_model_durations: Dict[str, float] = {}
    baseline = set(cfg.models)
    eligible = [mc for mc in exp_config.models
                if mc.label in baseline and mc.role != "collator"]

    relay_payloads = {}
    if round_idx > 0:
        if cfg.relay_mode == "directed":
            relay_payloads = brain.relay_directed(round_idx)
        elif cfg.relay_mode == "conversational":
            relay_payloads = brain.relay_conversational(round_idx)
        else:
            relay_payloads = brain.relay(round_idx)

    def _make_prompt(mc_label: str) -> str:
        if round_idx == 0 or mc_label not in relay_payloads:
            return base_prompt
        payload = relay_payloads[mc_label]
        if not payload.findings_text:
            return base_prompt
        adaptation = _itc_get_adaptation(mc_label)
        focus_prefix = ""
        if adaptation == "change_focus" and registry is not None:
            focus_prefix = _build_change_focus_instruction(registry, round_idx)
        if adaptation == "strip_context":
            relay_section = (
                f"=== OTHER MODELS' ANALYSIS (Round {round_idx - 1}) ===\n\n"
                f"(Context stripped. Summary of {payload.finding_count} findings.)\n\n"
                f"{payload.convergence_summary}\n\n"
                f"=== END OTHER MODELS' ANALYSIS ===\n\n"
            )
        else:
            relay_section = (
                f"=== OTHER MODELS' ANALYSIS (Round {round_idx - 1}) ===\n\n"
                f"{payload.findings_text}\n\n"
                f"{payload.convergence_summary}\n\n"
                f"=== END OTHER MODELS' ANALYSIS ===\n\n"
                f"Produce YOUR findings. Challenge weak claims, confirm strong ones.\n\n"
            )
        combined = f"{focus_prefix}{relay_section}"
        if "=== ARTIFACT:" in base_prompt:
            return base_prompt.replace("=== ARTIFACT:", f"{combined}=== ARTIFACT:")
        return f"{combined}{base_prompt}"

    logs_dir = brain.logs_dir
    prompt_lengths: Dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=len(eligible)) as pool:
        future_to_label = {}
        start_times: Dict[str, float] = {}
        for mc in eligible:
            prompt = _make_prompt(mc.label)
            prompt_lengths[mc.label] = len(prompt) + len(cdsfl_text)
            start_times[mc.label] = time.monotonic()
            future_to_label[pool.submit(
                _dispatch_single_model, mc, mgr, prompt,
                cdsfl_text, full_code, round_idx, cfg.pattern, cfg.domain, logs_dir,
            )] = mc.label

        for future in as_completed(future_to_label):
            label = future_to_label[future]
            elapsed = time.monotonic() - start_times[label]
            per_model_durations[label] = elapsed
            try:
                mf, text = future.result()
                findings.extend(mf)
                if text and not text.startswith("__DISPATCH_FAILED__:"):
                    responses[label] = text
            except Exception as e:
                _log(f"  {label}: thread error — {type(e).__name__}: {e}")

    return findings, responses, per_model_durations, prompt_lengths


# ─────────────────────────────────────────────────────────────────────────────
# Safety and telemetry helpers
# ─────────────────────────────────────────────────────────────────────────────

def _feedback_channel_enabled(cfg: "RunnerConfig") -> bool:
    """Read the feedback-channel switch from RunnerConfig.

    Defaults to True (feedback channel active) if the attribute is missing
    — the whole point of CDSFL is corrective feedback, so absence is
    interpreted as "run with defaults on". The config knob exists so that
    an experimenter can disable the channel for a controlled ablation
    without editing code.

    See `cdsfl_operational.md` §17 and `bench/dm/_feedback.py`.
    """
    return bool(getattr(cfg, "feedback_channel_enabled", True))


def _build_feedback_for_next_round(
    *,
    round_idx: int,
    findings: List[Finding],
    responses: Dict[str, str],
    immune_result,
    rk_validation: Dict[str, List[Tuple[str, str, str, str]]],
    cfg: "RunnerConfig",
) -> Dict[str, str]:
    """Assemble per-model feedback sections from round-K schema outputs.

    Called at the end of round K. Output is consumed at the top of round
    K+1's prompt. On any exception, returns an empty dict — feedback
    assembly is never allowed to crash the main loop.
    """
    try:
        # Extract duplicate pairs from TriagedFinding — NK Cell populates
        # `is_duplicate=True, duplicate_of=<id>, similarity=<float>` and the
        # triaged list is on the ImmuneResponse.
        duplicate_pairs: List[Tuple[str, str, float]] = []
        for triaged in getattr(immune_result, "triaged", []):
            if getattr(triaged, "is_duplicate", False) and triaged.duplicate_of:
                duplicate_pairs.append(
                    (triaged.finding.finding_id,
                     triaged.duplicate_of,
                     float(getattr(triaged, "similarity", 0.0))),
                )

        # Parse admissibility blocks from each model's raw response. The
        # parser is permissive (see bench/dm/_feedback.py) — missing blocks
        # generate a full-fail list (all 5 gates flagged), so models that
        # haven't yet adopted the §15 format get a clear pointer.
        admissibility_failures: Dict[str, List[str]] = {}
        for f in findings:
            model_text = responses.get(f.model_id, "")
            # Attempt to extract the specific finding's section before parsing
            # — findings are typically separated by "FINDING" markers.
            failed = parse_admissibility_block(_extract_finding_section(model_text, f.finding_id))
            if failed:
                admissibility_failures[f.finding_id] = failed

        records = build_feedback_records(
            round_idx=round_idx,
            findings=findings,
            immune_result=immune_result,
            rk_validation=rk_validation,
            duplicate_pairs=duplicate_pairs,
            admissibility_failures=admissibility_failures,
        )

        top_k = getattr(cfg, "feedback_top_k", 10)
        max_chars = getattr(cfg, "feedback_max_chars_per_model", 8000)
        return build_feedback_sections(
            records,
            round_idx=round_idx,
            top_k=top_k,
            max_chars_per_model=max_chars,
        )
    except Exception as exc:
        # Defensive: the feedback channel must never break the pipeline.
        # If something goes wrong (e.g. a novel immune_result shape), we log
        # once and continue with empty feedback. Next round runs without it.
        _log(f"  [feedback] build failed: {type(exc).__name__}: {exc}")
        return {}


def _extract_finding_section(full_text: str, finding_id: str) -> str:
    """Extract the text of a specific finding from a model's raw response.

    Returns the substring from the finding_id marker up to the next finding
    marker (or end of text). If the finding_id can't be located, returns
    the full text so the parser still has something to work with.

    Heuristic — models use varied phrasing ("FINDING f1", "Finding f1:",
    "f1:", etc.). We look for the id in several common formats.
    """
    if not full_text or not finding_id:
        return full_text
    import re
    # Case-insensitive, tolerant of punctuation around the id
    pattern = re.compile(
        rf"(?:FINDING\s+)?{re.escape(finding_id)}\b",
        re.IGNORECASE,
    )
    match = pattern.search(full_text)
    if not match:
        return full_text
    tail = full_text[match.start():]
    # Find the start of the next FINDING or similar terminator
    next_match = re.search(
        r"(?:^|\n)\s*(?:FINDING\s+\S+|---\s*FINDING|=+\s*FINDING)",
        tail[match.end() - match.start():],
        re.IGNORECASE | re.MULTILINE,
    )
    if next_match:
        return tail[: match.end() - match.start() + next_match.start()]
    return tail


def _safety_check(responses: Dict[str, str]) -> Optional[str]:
    if not responses:
        return "all_models_failed"
    for label, text in list(responses.items()):
        if len(text.strip()) < 50:
            _log(f"  SAFETY: {label} near-empty — queued for ITC recovery")
            responses.pop(label, None)
        elif "[MODEL_REFUSED" in text:
            _log(f"  SAFETY: {label} refused — queued for ITC recovery")
            responses.pop(label, None)
    if not responses:
        return "all_models_failed"
    return None


def _build_round_timings(
    responses: Dict[str, str], per_model_durations: Dict[str, float],
    findings: List[Finding], round_idx: int,
) -> List[RoundTiming]:
    return [
        RoundTiming(
            model_id=label, round_idx=round_idx,
            duration_s=per_model_durations.get(label, 0.0),
            response_chars=len(text),
            finding_count=len([f for f in findings if f.model_id == label]),
        )
        for label, text in responses.items()
    ]


def _summarise_health_scan(scan: HealthScan) -> Dict[str, Any]:
    return {
        "total_diagnostics": scan.total,
        "by_category": dict(scan.counts_by_category),
        "by_severity": dict(scan.counts_by_severity),
        "elapsed_s": round(scan.elapsed_s, 2),
    }


def _summarise_fix_evaluations(evals: List[FixEvaluation]) -> Dict[str, Any]:
    verdict_counts: Dict[str, int] = {}
    for ev in evals:
        verdict_counts[ev.verdict] = verdict_counts.get(ev.verdict, 0) + 1
    return {"total_evaluated": len(evals), "verdicts": verdict_counts}


# ─────────────────────────────────────────────────────────────────────────────
# Shadow cell runner (Macrophage + Ouroboros) — Exp 39
# ─────────────────────────────────────────────────────────────────────────────

# Persistent shadow cell instances (survive across rounds)
_shadow_macrophage = None
_shadow_ouroboros = None
_shadow_stage6_calibrator = None


def _run_shadow_cells(
    round_idx: int,
    immune_result: Any,
    findings: List[Finding],
    exp_config: Any,
    logs_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Run Macrophage and Ouroboros shadow cells after a round.

    SHADOW MODE ONLY: zero effect on the load-bearing verdict path.
    Both cells observe and log but never modify pipeline state.

    Args:
        round_idx: Current round index.
        immune_result: ImmuneResponse from run_immune_pipeline.
        findings: Findings from the current round.
        exp_config: Experiment config (checked for _macrophage/_ouroboros sections).
        logs_dir: Directory for shadow cell logs.

    Returns:
        Dict with shadow cell metrics for round reporting.
    """
    global _shadow_macrophage, _shadow_ouroboros, _shadow_stage6_calibrator

    config = exp_config if isinstance(exp_config, dict) else {}

    has_macrophage = "_macrophage" in config
    has_ouroboros = "_ouroboros" in config

    if not has_macrophage and not has_ouroboros:
        return {}

    shadow_data: Dict[str, Any] = {}

    # ── Macrophage: internal pipeline monitor ──
    if has_macrophage:
        try:
            from bench.macrophage_cell import MacrophageCell, MacrophageMode

            if _shadow_macrophage is None:
                _shadow_macrophage = MacrophageCell(
                    mode=MacrophageMode.PATROL, shadow=True,
                )

            # Extract verdicts from immune result. Exp 40 fix 1B.1:
            # previously the Macrophage saw 0 verdicts across all 6 rounds
            # of Exp 39-0 despite the pipeline producing 16+ per round.
            # Now two-path: primary = cell_verdicts dict (per-finding lists);
            # fallback = synthesise lightweight verdict-like objects from
            # final_verdicts when cell_verdicts is absent or empty, so the
            # Macrophage's cluster/severity/timing checks can still fire.
            all_verdicts: List[Any] = []
            cv_attr = hasattr(immune_result, "cell_verdicts")
            if cv_attr:
                for vid_list in immune_result.cell_verdicts.values():
                    all_verdicts.extend(vid_list)

            if not all_verdicts:
                # Fallback: synthesise from final_verdicts (Dict[str, str]).
                fv = getattr(immune_result, "final_verdicts", None)
                if fv:
                    from types import SimpleNamespace
                    for fid, verdict_str in fv.items():
                        # Mimic CellVerdict-like interface: .verdict, .confidence,
                        # .finding_id, .tool_used, .cell_type — Macrophage only
                        # reads .verdict and .confidence in _patrol_observe.
                        conf = 0.5
                        fc = getattr(immune_result, "final_confidences", None)
                        if fc and fid in fc:
                            conf = float(fc[fid])
                        all_verdicts.append(SimpleNamespace(
                            finding_id=fid,
                            verdict=verdict_str,
                            confidence=conf,
                            tool_used="synthesised_from_final_verdicts",
                            cell_type="synthesised",
                        ))

            if not all_verdicts:
                cv_keys = (
                    len(immune_result.cell_verdicts) if cv_attr else 0
                )
                per_fid_counts = (
                    {k: len(v) for k, v in immune_result.cell_verdicts.items()}
                    if cv_attr else {}
                )
                fv_attr = hasattr(immune_result, "final_verdicts")
                fv_keys = (
                    len(immune_result.final_verdicts) if fv_attr else 0
                )
                _log(
                    f"  Macrophage: 0 verdicts after both primary and "
                    f"fallback paths "
                    f"(cell_verdicts={'present' if cv_attr else 'missing'}, "
                    f"keys={cv_keys}, per_fid={per_fid_counts}, "
                    f"final_verdicts={'present' if fv_attr else 'missing'}, "
                    f"fv_keys={fv_keys}, "
                    f"type={type(immune_result).__name__})"
                )

            triaged = getattr(immune_result, "triaged", None)
            timings = getattr(immune_result, "stage_timings", None)

            # Extract provenance metadata from external-origin findings
            provenance = []
            for f in findings:
                if getattr(f, "origin_type", "") and f.origin_type != "model":
                    provenance.append({
                        "origin_type": f.origin_type,
                        "source_ref": getattr(f, "source_ref", ""),
                        "retrieval_query": getattr(f, "retrieval_query", ""),
                        "retrieved_at": getattr(f, "retrieved_at", ""),
                        "source_hash": getattr(f, "source_hash", ""),
                        "source_diversity": getattr(f, "source_diversity", 0.0),
                    })

            # Derive PE gate pass/fail statistics from immune verdicts
            gate_stats = None
            final_v = getattr(immune_result, "final_verdicts", None)
            if final_v:
                passed = sum(1 for v in final_v.values() if v in ("CONFIRMED", "UNCERTAIN", "UNSCORED"))
                failed = sum(1 for v in final_v.values() if v in ("REJECTED", "DUPLICATE"))
                by_origin: Dict[str, Dict[str, int]] = {}
                for f in findings:
                    ot = getattr(f, "origin_type", "model") or "model"
                    fid = f.finding_id
                    bucket = by_origin.setdefault(ot, {"passed": 0, "failed": 0})
                    v = final_v.get(fid, "UNCERTAIN")
                    if v in ("REJECTED", "DUPLICATE"):
                        bucket["failed"] += 1
                    else:
                        bucket["passed"] += 1
                gate_stats = {
                    "total_passed": passed,
                    "total_failed": failed,
                    "by_origin": by_origin,
                }

            # Ouroboros activity metrics from prior rounds (if available)
            ouroboros_metrics = None
            if _shadow_ouroboros is not None and hasattr(_shadow_ouroboros, "get_activity_metrics"):
                ouroboros_metrics = _shadow_ouroboros.get_activity_metrics()

            macro_summary = _shadow_macrophage.observe(
                verdicts=all_verdicts,
                triaged=triaged,
                timings=timings,
                provenance=provenance or None,
                gate_stats=gate_stats,
                ouroboros_metrics=ouroboros_metrics,
            )

            # Codex 5.3 confer fix (13 April 2026): Macrophage was counts-only
            # while Ouroboros wrote full per-round replay logs.  Now both
            # shadow cells produce equally inspectable output.
            shadow_data["macrophage"] = {
                "observations": len(macro_summary.observations),
                "anomalies": macro_summary.anomaly_count,
                "pipeline_modified": macro_summary.pipeline_modified,
                "mode": macro_summary.mode.value,
                "verdicts_received": len(all_verdicts),
                "observation_details": [
                    obs.to_dict() for obs in macro_summary.observations
                ],
            }

            # Write Macrophage shadow replay log to disk (parity with Ouroboros)
            if logs_dir:
                macro_log_path = logs_dir / f"macrophage_shadow_r{round_idx:02d}.json"
                macro_log_path.write_text(
                    json.dumps({
                        "round_idx": round_idx,
                        "mode": macro_summary.mode.value,
                        "anomaly_count": macro_summary.anomaly_count,
                        "pipeline_modified": macro_summary.pipeline_modified,
                        "verdicts_received": len(all_verdicts),
                        "observations": [
                            obs.to_dict() for obs in macro_summary.observations
                        ],
                    }, indent=2, default=str) + "\n",
                    encoding="utf-8",
                )

        except Exception as exc:
            import logging
            logging.getLogger("cdsfl.shadow_cells").warning(
                "Macrophage shadow cell failed (non-fatal): %s", exc,
            )
            shadow_data["macrophage"] = {"error": str(exc)}

    # ── Ouroboros: external research (between-round) ──
    if has_ouroboros:
        try:
            from bench.ouroboros_cell import OuroborosCell

            if _shadow_ouroboros is None:
                ouroboros_config = config.get("_ouroboros", {})
                allowed = ouroboros_config.get("api_access", ["arxiv", "semantic_scholar"])
                _shadow_ouroboros = OuroborosCell(
                    shadow=True,
                    allowed_sources=allowed if isinstance(allowed, list) else [allowed],
                )

            # Collect Macrophage anomalies as research targets
            anomaly_descriptions = []
            if "macrophage" in shadow_data and _shadow_macrophage is not None:
                macro_summary_ref = _shadow_macrophage._round_history
                if macro_summary_ref:
                    last = macro_summary_ref[-1]
                    if last.get("anomaly_count", 0) > 0:
                        anomaly_descriptions.append(
                            f"round_{round_idx}_anomalies:{last['anomaly_count']}"
                        )

            shadow_log = _shadow_ouroboros.run_between_rounds(
                round_idx=round_idx,
                anomalies=anomaly_descriptions,
                immune_response=immune_result,
                round_findings=findings,
            )

            shadow_data["ouroboros"] = {
                "anomalies_observed": len(shadow_log.anomalies_observed),
                "queries_issued": len(shadow_log.queries_issued),
                "candidate_claims": len(shadow_log.candidate_claims),
                "would_have_injected": shadow_log.would_have_injected,
            }

            # Write shadow replay log to disk
            if logs_dir:
                shadow_log_path = logs_dir / f"ouroboros_shadow_r{round_idx:02d}.json"
                shadow_log_path.write_text(
                    json.dumps(shadow_log.to_dict(), indent=2, default=str) + "\n",
                    encoding="utf-8",
                )

        except Exception as exc:
            import logging
            logging.getLogger("cdsfl.shadow_cells").warning(
                "Ouroboros shadow cell failed (non-fatal): %s", exc,
            )
            shadow_data["ouroboros"] = {"error": str(exc)}

    # ── Stage 6 calibrator: shadow (ν_k, c_ext) data collection ──
    # Runs whenever any shadow cell is active. Collects per-finding
    # novelty triples and per-tool FPR tracking for post-experiment
    # calibration. Zero pipeline effect.
    try:
        from bench.dm._shadow_stage6 import ShadowStage6Calibrator

        if _shadow_stage6_calibrator is None:
            _shadow_stage6_calibrator = ShadowStage6Calibrator()

        # Collect ouroboros data if available (for c_ext and nu_k estimation)
        ouroboros_shadow_data = None
        if "ouroboros" in shadow_data and _shadow_ouroboros is not None:
            # Get the full shadow log from the last run
            if hasattr(_shadow_ouroboros, "_last_shadow_log"):
                last_log = _shadow_ouroboros._last_shadow_log
                if last_log is not None:
                    ouroboros_shadow_data = last_log.to_dict()

        round_log = _shadow_stage6_calibrator.observe_round(
            round_idx=round_idx,
            findings=findings,
            immune_response=immune_result,
            ouroboros_data=ouroboros_shadow_data,
        )

        shadow_data["stage6_calibration"] = {
            "findings_assessed": len(round_log.findings),
            "mean_nu_k_proxy": round_log.mean_nu_k_proxy,
            "mean_c_ext": round_log.mean_c_ext,
            "mean_delta": round_log.mean_delta,
        }

        # Write calibration log to disk
        if logs_dir:
            cal_path = logs_dir / f"stage6_calibration_r{round_idx:02d}.json"
            cal_path.write_text(
                json.dumps(round_log.to_dict(), indent=2, default=str) + "\n",
                encoding="utf-8",
            )

            # Also write cumulative summary
            summary_path = logs_dir / "stage6_calibration_summary.json"
            summary_path.write_text(
                json.dumps(
                    _shadow_stage6_calibrator.get_calibration_summary(),
                    indent=2, default=str,
                ) + "\n",
                encoding="utf-8",
            )

    except Exception as exc:
        import logging
        logging.getLogger("cdsfl.shadow_cells").warning(
            "Stage 6 calibrator failed (non-fatal): %s", exc,
        )
        shadow_data["stage6_calibration"] = {"error": str(exc)}

    return shadow_data


def _summarise_pacing_signals(signals: List[PacingSignal]) -> List[Dict[str, Any]]:
    return [
        {"type": s.signal_type, "detail": s.detail, "model_id": s.model_id,
         "metric_value": round(s.metric_value, 3),
         "threshold": round(s.threshold, 3),
         "suggested_action": s.suggested_action}
        for s in signals
    ]


# ─────────────────────────────────────────────────────────────────────────────
# CC2v verification (A5: dedup-aware)
# ─────────────────────────────────────────────────────────────────────────────

_VERIFICATION_PROMPT_TEMPLATE = """You are a verification agent (CC2v). FFF each finding and produce a verdict.

For each finding:
  CONFIRM <ID> | <confidence 0.0-1.0> | <one-line evidence>
  REJECT <ID> | <confidence 0.0-1.0> | <one-line counterexample>
  DUPLICATE <ID> OF <canonical_id> | <confidence 0.0-1.0> | <evidence>
  ESCALATE <ID> | <reason>

SOURCE CODE:
{source_code}

FINDINGS TO VERIFY:
{findings_block}

One verdict per line, nothing else.
"""


def _verification_step(
    registry: FindingRegistry, round_idx: int,
    source_code: str, model_configs: List[ModelConfig],
    cfg: RunnerConfig,
) -> Dict[str, Any]:
    """A5: dedup-aware CC2v — skip already-confirmed/escalated findings."""
    if round_idx < cfg.verification_min_round:
        return {"skipped": True, "reason": f"round {round_idx} < {cfg.verification_min_round}"}

    open_findings = []
    for cid, entry in registry.entries.items():
        if entry["status"] not in ("OPEN", "CONTESTED"):
            continue
        if entry.get("cc2v_escalated"):
            continue
        confirm_models = {
            v["model"] for v in entry.get("verdicts", [])
            if v.get("verdict") == "CONFIRM"
        }
        if len(confirm_models) >= 2:
            continue
        cc2v_verdicts = [v for v in entry.get("verdicts", []) if v.get("model") == "CC2v"]
        if cc2v_verdicts:
            continue
        open_findings.append((cid, entry))

    if not open_findings:
        return {"skipped": True, "reason": "no open findings"}

    open_findings.sort(key=lambda x: x[1].get("severity", 0), reverse=True)
    batch = open_findings[:cfg.verification_batch_size]

    findings_block = "\n\n".join(
        f"[{cid}] severity={entry.get('severity', 0):.2f}: {entry.get('description', '')[:500]}"
        for cid, entry in batch
    )
    prompt = _VERIFICATION_PROMPT_TEMPLATE.format(
        source_code=source_code[:80_000], findings_block=findings_block,
    )

    cc2_config = None
    for mc in model_configs:
        if mc.label == "CC2":
            cc2_config = mc
            break
    if cc2_config is None:
        return {"skipped": True, "reason": "CC2 config not found"}

    stats: Dict[str, Any] = {
        "round": round_idx, "batch_size": len(batch),
        "batch_ids": [cid for cid, _ in batch], "verdicts": {},
    }
    try:
        text, elapsed = dispatch_to_model(
            cc2_config, prompt, "", wall_clock_limit=cc2_config.timeout * 3)
        stats["elapsed_s"] = round(elapsed, 1)
    except Exception as e:
        _log(f"  CC2v: dispatch failed — {type(e).__name__}: {e}")
        stats["error"] = str(e)
        return stats

    verdict_re = re.compile(
        r"(CONFIRM|REJECT|DUPLICATE|ESCALATE)\s+(C\d+)"
        r"(?:\s+OF\s+(C\d+))?"
        r"(?:\s*\|\s*([\d.]+))?"
        r"(?:\s*\|\s*(.+))?",
        re.IGNORECASE,
    )
    confirmed = rejected = duplicates = escalated = 0
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
            continue
        stats["verdicts"][finding_id] = {
            "action": action, "confidence": confidence, "evidence": evidence[:200],
        }
        if action == "ESCALATE":
            entry = registry.entries.get(finding_id)
            if entry:
                entry["cc2v_escalated"] = True
            escalated += 1
            continue
        if confidence < cfg.verification_confidence_threshold:
            continue
        if action == "CONFIRM":
            entry = registry.entries.get(finding_id)
            if entry and entry["status"] in ("OPEN", "CONTESTED"):
                registry.resolve(finding_id, "CONFIRMED", round_idx)
                confirmed += 1
        elif action == "REJECT":
            entry = registry.entries.get(finding_id)
            if entry and entry["status"] in ("OPEN", "CONTESTED"):
                registry.resolve(finding_id, "UNCONFIRMED", round_idx)
                rejected += 1
        elif action == "DUPLICATE" and merge_target:
            merge_target = merge_target.upper()
            if merge_target in registry.entries:
                entry = registry.entries.get(finding_id)
                if entry and entry["status"] in ("OPEN", "CONTESTED"):
                    registry.resolve(finding_id, "MERGED", round_idx)
                    entry["merged_into"] = merge_target
                    duplicates += 1

    stats.update(confirmed=confirmed, rejected=rejected,
                 duplicates=duplicates, escalated=escalated,
                 total_resolved=confirmed + rejected + duplicates)
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# S_k Solution Verification Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def parse_search_replace_blocks(text: str) -> List[FixBlock]:
    """Parse <<<< SEARCH file_path ... ==== ... >>>> REPLACE blocks.

    Uses a line-oriented state machine instead of regex so that delimiter-
    like content inside payloads (e.g. literal '====' lines) does not
    break parsing.

    P1 fix (Exp 38): falls back to markdown code block extraction when
    no <<<< SEARCH blocks found but ```python blocks with before/after
    structure are present.

    Returns list of FixBlock. Empty list if no valid blocks found.
    """
    blocks: List[FixBlock] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # Look for block start: <<<< SEARCH <filepath>
        if line.strip().startswith("<<<<") and "SEARCH" in line.upper():
            rest = line.strip()[4:].strip()
            # Remove 'SEARCH' keyword
            for prefix in ("SEARCH ", "SEARCH\t"):
                if rest.upper().startswith(prefix.upper()):
                    rest = rest[len(prefix):].strip()
                    break
            file_path = rest
            i += 1
            # Collect search lines until ==== separator (with or without trailing text).
            # The parser in runner_core stores "==== REPLACE" while the prompt
            # specifies bare "====".  Accept both.  (Exp 39-0 confound fix.)
            search_lines: List[str] = []
            while i < len(lines):
                stripped = lines[i].rstrip()
                if stripped == "====" or stripped.startswith("==== "):
                    i += 1
                    break
                search_lines.append(lines[i])
                i += 1
            else:
                # Reached end without finding separator — skip this block
                continue
            # Collect replace lines until >>>> closer (with or without REPLACE).
            # Accept bare ">>>>" AND ">>>> REPLACE".  (Exp 39-0 confound fix.)
            replace_lines: List[str] = []
            while i < len(lines):
                if lines[i].strip().startswith(">>>>"):
                    i += 1
                    break
                replace_lines.append(lines[i])
                i += 1
            else:
                continue
            search = "\n".join(search_lines)
            replace = "\n".join(replace_lines)
            if file_path and search:
                blocks.append(FixBlock(
                    file_path=file_path, search=search, replace=replace,
                ))
        else:
            i += 1

    # P1 fallback: extract from markdown code blocks with file path comments.
    # Models sometimes use ```python\n# file: path/to/file.py\n... instead of
    # <<<< SEARCH blocks. Look for paired "before"/"after" or "current"/"fixed"
    # code blocks.
    #
    # SHADOW MODE (Exp 39): log what the fallback would extract but do not
    # return the blocks. This gives empirical data on firing rate and
    # precision without confounding the Exp 39 fix validation.
    if not blocks:
        _MD_BLOCK_RE = re.compile(
            r'```\w*\n(?:#\s*(?:file|path|target):\s*([^\n]+)\n)?'
            r'(.*?)\n```',
            re.DOTALL
        )
        md_blocks = list(_MD_BLOCK_RE.finditer(text))
        if len(md_blocks) >= 2:
            shadow_blocks: List[FixBlock] = []
            for j in range(len(md_blocks) - 1):
                b1, b2 = md_blocks[j], md_blocks[j + 1]
                between = text[b1.end():b2.start()].lower()
                if any(kw in between for kw in ("after", "replace", "fixed", "corrected", "new")):
                    fp = b1.group(1) or b2.group(1) or ""
                    search = b1.group(2).strip()
                    replace_text = b2.group(2).strip()
                    if fp and search:
                        shadow_blocks.append(FixBlock(
                            file_path=fp.strip(),
                            search=search,
                            replace=replace_text,
                        ))
            if shadow_blocks:
                _log(f"  P1 SHADOW: fallback parser found {len(shadow_blocks)} "
                     f"block(s) from markdown — NOT applied. "
                     f"Files: {[b.file_path for b in shadow_blocks]}, "
                     f"search_lens: {[len(b.search) for b in shadow_blocks]}")
    return blocks


def apply_fix_blocks(
    source: str, blocks: List[FixBlock], target_path: str,
) -> Tuple[Optional[str], int, Optional[str]]:
    """Apply fix blocks to source.

    Returns (modified_source, blocks_applied, error_reason).

    Only applies blocks whose file_path matches target_path (by basename or
    full path). Returns modified_source=None on pre-gate failure with a
    machine-readable error_reason.
    """
    modified = source
    applied = 0
    matched = 0
    for block in blocks:
        # Match by basename or full path
        if not (block.file_path == target_path or
                Path(block.file_path).name == Path(target_path).name):
            continue
        matched += 1
        if block.search not in modified:
            _log(f"  S_k: SEARCH block not found in source "
                 f"(first 60 chars: {block.search[:60]!r})")
            return None, 0, "search_not_found"
        occurrences = modified.count(block.search)
        if occurrences > 1:
            _log(f"  S_k: SEARCH block is ambiguous ({occurrences} "
                 f"occurrences, first 60 chars: {block.search[:60]!r})")
            return None, 0, "search_ambiguous"
        modified = modified.replace(block.search, block.replace, 1)
        applied += 1

    if matched == 0:
        return None, 0, "no_blocks_for_target"

    return modified, applied, None


def _run_hard_gate_ast(modified_source: str) -> Tuple[int, str]:
    """g1: AST parse. Returns (score, detail)."""
    try:
        ast.parse(modified_source)
        return 1, "AST parse succeeded"
    except (SyntaxError, ValueError) as e:
        return 0, f"ParseError: {e}"


def _run_hard_gate_compile(modified_source: str, source_path: str) -> Tuple[int, str]:
    """g2: py_compile (replaces import resolution). Returns (score, detail)."""
    # Anchor to source directory for context parity with ruff/bandit gates
    anchor_dir = str(Path(source_path).parent) if source_path else None
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(modified_source)
        tmp_path = tmp.name
    try:
        py_compile.compile(tmp_path, doraise=True)
        return 1, "py_compile succeeded"
    except py_compile.PyCompileError as e:
        return 0, f"CompileError: {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass


def _run_effect_regression(
    modified_source: str, source_path: str, test_cmd: Optional[str] = None,
) -> Tuple[Optional[float], str]:
    """e2: Regression suite — run existing tests against modified source.

    Returns (score in [0,1] or None if unavailable, detail). Copies the
    entire repo into a sandbox, overlays the modified source, and runs
    tests there so that pytest evaluates the actual proposed fix, not
    the original.
    """
    if not test_cmd:
        return None, "no test command configured"
    target_path = Path(source_path).resolve()
    try:
        rel_target = target_path.relative_to(REPO_ROOT)
    except ValueError:
        return None, f"source not under REPO_ROOT"
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Path(tmpdir) / "sandbox"
        shutil.copytree(
            REPO_ROOT, sandbox,
            symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "*.pyc", "logs",
            ),
        )
        # Overlay the modified source into the sandbox
        sandbox_target = sandbox / rel_target
        sandbox_target.parent.mkdir(parents=True, exist_ok=True)
        sandbox_target.write_text(modified_source, encoding="utf-8")
        try:
            result = subprocess.run(
                shlex.split(test_cmd),
                capture_output=True, text=True, timeout=120,
                cwd=str(sandbox),
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            output = result.stdout + result.stderr

            m = re.search(r'(\d+)\s+passed', output)
            passed = int(m.group(1)) if m else 0
            m = re.search(r'(\d+)\s+failed', output)
            failed = int(m.group(1)) if m else 0
            collected_zero = bool(re.search(r'collected\s+0\s+items', output))

            total = passed + failed
            if total > 0:
                score = passed / total
                return score, f"{passed}/{total} passed (sandbox)"

            # Genuine "no tests" — pytest exit code 5 = no tests collected
            if collected_zero and result.returncode == 5:
                return 1.0, "no tests collected"

            # Unparseable output (collection error, crash, etc.) — unavailable
            return None, (
                f"test results unavailable: rc={result.returncode} "
                f"output={output[:200]!r}"
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            return None, f"test execution failed: {e}"


def _run_effect_ruff(
    modified_source: str, baseline_violations: Optional[int],
    source_path: str = "",
) -> Tuple[Optional[float], str]:
    """e3: Static analysis non-regression via ruff."""
    if baseline_violations is None:
        return None, "ruff baseline unavailable"
    # Anchor temp file to source directory so ruff picks up pyproject.toml
    anchor_dir = str(Path(source_path).parent) if source_path else None
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(modified_source)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", tmp_path,
             "--output-format=json", "--quiet"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode not in (0, 1):
            return None, f"ruff failed: rc={result.returncode} stderr={result.stderr[:200]}"
        try:
            violations = json.loads(result.stdout)
            if not isinstance(violations, list):
                return None, "ruff output was not JSON list"
            total_count = len(violations)
        except (json.JSONDecodeError, TypeError) as e:
            return None, f"ruff output parse failed: {e}"
        # Delta-based: only NEW violations reduce score (0.1 penalty each)
        delta = max(0, total_count - baseline_violations)
        score = max(0.0, 1.0 - delta * 0.1)
        return score, f"{total_count} total, {delta} new (baseline: {baseline_violations})"
    except (subprocess.TimeoutExpired, OSError) as e:
        return None, f"ruff unavailable: {e}"
    finally:
        os.unlink(tmp_path)


def _run_effect_bandit(
    modified_source: str, baseline_findings: Optional[Dict[str, int]],
    source_path: str = "",
) -> Tuple[Optional[float], str]:
    """e4: Security non-regression via bandit.

    Scoring per Python encoding: -0.5 per new HIGH, -0.2 per new MEDIUM.
    baseline_findings is a dict with 'high' and 'medium' keys.
    """
    if baseline_findings is None:
        return None, "bandit baseline unavailable"
    # Anchor temp file to source directory for config discovery
    anchor_dir = str(Path(source_path).parent) if source_path else None
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(modified_source)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", tmp_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode not in (0, 1):
            return None, f"bandit failed: rc={result.returncode} stderr={result.stderr[:200]}"
        try:
            data = json.loads(result.stdout)
            if not isinstance(data, dict):
                return None, "bandit output was not JSON object"
            results_list = data.get("results", [])
            high_count = sum(
                1 for r in results_list
                if r.get("issue_severity", "").upper() == "HIGH"
            )
            med_count = sum(
                1 for r in results_list
                if r.get("issue_severity", "").upper() == "MEDIUM"
            )
        except (json.JSONDecodeError, TypeError) as e:
            return None, f"bandit output parse failed: {e}"
        baseline_high = baseline_findings.get("high", 0)
        baseline_med = baseline_findings.get("medium", 0)
        new_high = max(0, high_count - baseline_high)
        new_med = max(0, med_count - baseline_med)
        score = max(0.0, 1.0 - new_high * 0.5 - new_med * 0.2)
        return score, (
            f"{high_count} HIGH/{med_count} MEDIUM "
            f"(baseline: {baseline_high}H/{baseline_med}M, "
            f"new: {new_high}H/{new_med}M)"
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return None, f"bandit unavailable: {e}"
    finally:
        os.unlink(tmp_path)


def _capture_baseline(source: str, source_path: str = "") -> Dict[str, Any]:
    """Capture baseline gate scores before fix application.

    Values are None when a tool is unavailable, so downstream gates
    can distinguish 'no violations' (0) from 'tool broken' (None).
    """
    baseline: Dict[str, Any] = {
        "ruff_violations": None,
        "bandit_findings": None,
    }
    # Anchor temp files to source directory for config discovery
    anchor_dir = str(Path(source_path).parent) if source_path else None

    # Ruff violations on original source
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(source)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", tmp_path,
             "--output-format=json", "--quiet"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode in (0, 1):
            try:
                violations = json.loads(result.stdout)
                if isinstance(violations, list):
                    baseline["ruff_violations"] = len(violations)
            except (json.JSONDecodeError, TypeError):
                pass
    except (subprocess.TimeoutExpired, OSError):
        pass
    finally:
        os.unlink(tmp_path)

    # Bandit findings on original source
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8",
        dir=anchor_dir,
    ) as tmp:
        tmp.write(source)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", tmp_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode in (0, 1):
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    results_list = data.get("results", [])
                    baseline["bandit_findings"] = {
                        "high": sum(
                            1 for r in results_list
                            if r.get("issue_severity", "").upper() == "HIGH"
                        ),
                        "medium": sum(
                            1 for r in results_list
                            if r.get("issue_severity", "").upper() == "MEDIUM"
                        ),
                    }
            except (json.JSONDecodeError, TypeError):
                pass
    except (subprocess.TimeoutExpired, OSError):
        pass
    finally:
        os.unlink(tmp_path)

    return baseline


def compute_sk(
    fix_text: str,
    source: str,
    source_path: str,
    baseline: Optional[Dict[str, Any]] = None,
    test_cmd: Optional[str] = None,
) -> SkResult:
    """Full S_k computation pipeline for a proposed fix.

    Parses SEARCH/REPLACE blocks, applies them, runs hard gates and
    effect evidence gates. Returns SkResult with tristate.
    """
    blocks = parse_search_replace_blocks(fix_text)
    if not blocks:
        return SkResult(
            sk=0.0, A=0.0, E=0.0, tristate="ESCALATE",
            gate_details={"error": "no SEARCH/REPLACE blocks found"},
            blocks_parsed=0, blocks_applied=0,
        )

    modified, applied, apply_error = apply_fix_blocks(source, blocks, source_path)
    if modified is None or applied == 0:
        return SkResult(
            sk=0.0, A=0.0, E=0.0, tristate="REJECTED",
            gate_details={"error": apply_error or "fix_blocks_not_applied"},
            blocks_parsed=len(blocks), blocks_applied=0,
        )

    # Hard gates
    details: Dict[str, Any] = {}
    g1_score, g1_detail = _run_hard_gate_ast(modified)
    details["g1_ast"] = {"score": g1_score, "detail": g1_detail}

    g2_score, g2_detail = _run_hard_gate_compile(modified, source_path)
    details["g2_compile"] = {"score": g2_score, "detail": g2_detail}

    A = g1_score * g2_score

    if A == 0:
        return SkResult(
            sk=0.0, A=0.0, E=0.0, tristate="REJECTED",
            gate_details=details,
            blocks_parsed=len(blocks), blocks_applied=applied,
        )

    # Effect evidence gates
    if baseline is None:
        baseline = {}

    # Gate weights (from Python expert encoding)
    effect_gates: List[Tuple[str, float, float]] = []  # (name, score, weight)
    unavailable_gates: List[str] = []

    # e2: regression suite
    e2_score, e2_detail = _run_effect_regression(modified, source_path, test_cmd)
    details["e2_regression"] = {"score": e2_score, "detail": e2_detail}
    if e2_score is not None:
        effect_gates.append(("e2_regression", e2_score, 2.0))
    elif test_cmd:  # configured but unavailable
        unavailable_gates.append("e2_regression")

    # e3: ruff non-regression
    e3_score, e3_detail = _run_effect_ruff(
        modified, baseline.get("ruff_violations"), source_path=source_path)
    details["e3_ruff"] = {"score": e3_score, "detail": e3_detail}
    if e3_score is not None:
        effect_gates.append(("e3_ruff", e3_score, 1.0))
    else:
        unavailable_gates.append("e3_ruff")

    # e4: bandit security
    e4_score, e4_detail = _run_effect_bandit(
        modified, baseline.get("bandit_findings"), source_path=source_path)
    details["e4_bandit"] = {"score": e4_score, "detail": e4_detail}
    if e4_score is not None:
        effect_gates.append(("e4_bandit", e4_score, 2.0))
    else:
        unavailable_gates.append("e4_bandit")

    # ESCALATE if no effect gates produced evidence
    if not effect_gates:
        details["_unavailable"] = unavailable_gates
        return SkResult(
            sk=0.0, A=A, E=0.0, tristate="ESCALATE",
            gate_details=details,
            blocks_parsed=len(blocks), blocks_applied=applied,
        )

    # Compute E: renormalised weighted arithmetic mean over available gates.
    # Arithmetic mean preserves graded semantics — a single zero score
    # reduces E proportionally rather than vetoing it entirely. If a gate
    # is genuinely non-negotiable, it belongs in the hard gates (A).
    W = sum(w for _, _, w in effect_gates)
    if W == 0:
        E = 0.0
    else:
        E = sum((w / W) * s for _, s, w in effect_gates)

    if unavailable_gates:
        details["_unavailable"] = unavailable_gates

    sk = A * E
    tristate = "ADMISSIBLE" if sk > 0 else "REJECTED"

    return SkResult(
        sk=round(sk, 4), A=A, E=round(E, 4), tristate=tristate,
        gate_details=details,
        blocks_parsed=len(blocks), blocks_applied=applied,
    )


class ChannelViolationError(RuntimeError):
    """Raised when the divergence modulator is passed in a forbidden channel slot.

    Channel contract (round-2 5/5 unanimous, round-3 converged):

        eta_int_modulated = m_div * eta_int
        eta_combined      = eta_int_modulated * (1 - c_ext * (1 - nu_k))
        q                 = eta_combined * d * p
        R_k update        = compute_rk(R_old, q, sk, ...)

    FORBIDDEN paths:
      * m_div as pre-factor on R_k (e.g. ``m_div * R_old``)
      * m_div entering q as an independent factor outside eta_int
      * m_div contributing to nu_k
    """


def compute_rk(
    R_old: float, q: float, sk: float,
    nu_b: float = 0.05, nu_f: float = 0.20,
) -> float:
    """Three-phase R_k update: detection -> resolution -> re-injection.

    Uses bounded nu_eff = 1 - (1-nu_b)*(1-(1-sk)*nu_f).

    Channel boundary: ``q`` must already include any divergence modulation
    via ``m_div * eta_int`` upstream. This function is the sink, not the
    site where the modulator is applied. Callers that need the channel
    check enforced at composition time should use
    :func:`compute_rk_with_eta_channel` which decomposes q and validates
    the assignment is on eta_int, not on R_k or q directly.
    """
    # Defensive cast and clamp all probability-space inputs to [0, 1]
    R_old = max(0.0, min(1.0, float(R_old)))
    q = max(0.0, min(1.0, float(q)))
    sk = max(0.0, min(1.0, float(sk)))
    nu_b = max(0.0, min(1.0, float(nu_b)))
    nu_f = max(0.0, min(1.0, float(nu_f)))
    # HARD CONSTRAINT: nu_b + nu_f <= 1
    if nu_b + nu_f > 1.0:
        scale = 1.0 / (nu_b + nu_f)
        nu_b *= scale
        nu_f *= scale

    # Phase 1: Detection
    denom = 1.0 - q * R_old
    if abs(denom) < 1e-12:
        R_det = R_old
    else:
        R_det = R_old * (1.0 - q) / denom

    # Phase 2: Resolution (S_k replaces sigma)
    R_base = sk * R_det + (1.0 - sk) * R_old

    # Phase 3: Re-injection (bounded form)
    nu_eff = 1.0 - (1.0 - nu_b) * (1.0 - (1.0 - sk) * nu_f)
    R_k = R_base * (1.0 - nu_eff) + nu_eff

    return max(0.0, min(1.0, R_k))


def compute_rk_with_eta_channel(
    R_old: float, sk: float,
    eta_int: float, m_div: float,
    c_ext: float, nu_k: float,
    d: float, p: float,
    nu_b: float = 0.05, nu_f: float = 0.20,
) -> float:
    """R_k update that enforces the eta_int channel for the divergence modulator.

    Exp 40 fix 1E.10: composes q from primitives with m_div applied ONLY
    as an eta_int multiplier. Ranges are validated at entry; if a caller
    accidentally passes m_div in a forbidden slot (e.g. by computing
    ``R_old_modulated = m_div * R_old`` and then supplying that), the
    range check on R_old catches it when m_div * R_old drifts out of
    [0, 1] and the input-clamp silently coerces it — which itself is a
    regression surface. To defend against that, we validate m_div and
    eta_int as separate inputs *here* before composing q.
    """
    # Explicit channel validation — inputs that would be silently clamped
    # by compute_rk are rejected here as channel violations.
    for name, value in (
        ("m_div", m_div), ("eta_int", eta_int),
        ("c_ext", c_ext), ("nu_k", nu_k), ("d", d), ("p", p),
    ):
        fval = float(value)
        if not (0.0 <= fval <= 1.0):
            raise ChannelViolationError(
                f"{name}={fval} must be in [0, 1]; the divergence modulator "
                f"(m_div) multiplies eta_int only, not R_k or q directly."
            )

    # Canonical channel composition — m_div only on eta_int.
    eta_int_modulated = m_div * eta_int
    eta_combined = eta_int_modulated * (1.0 - c_ext * (1.0 - nu_k))
    q = eta_combined * d * p

    # Final sanity: q is a probability; composition must not produce q > 1.
    # Given each factor is in [0, 1], q ∈ [0, 1] algebraically. If this
    # invariant is ever violated we have a numerical or input-ordering bug.
    if not (0.0 <= q <= 1.0 + 1e-9):
        raise ChannelViolationError(
            f"composed q={q} escaped [0, 1]; channel invariant broken."
        )

    return compute_rk(R_old, q, sk, nu_b=nu_b, nu_f=nu_f)


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic R_k recomputation validation (14 April 2026)
# ─────────────────────────────────────────────────────────────────────────────

# Regex patterns for extracting R_k parameters from model corroboration text.
# Models use varied notation (η vs eta, ν_eff vs nu_eff, × vs * vs ·).
_RK_RE_R_OLD = re.compile(
    r'R_?(?:old|prev|prior)\s*[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
_RK_RE_ETA = re.compile(
    r'(?:[ηη]|eta)\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
_RK_RE_D = re.compile(
    r'\bd\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)')
_RK_RE_P = re.compile(
    r'\bp\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)')
_RK_RE_Q_LINE = re.compile(
    r'^\s*q\s*[=:].*$', re.MULTILINE)
_RK_RE_SK = re.compile(
    r'S_?k\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
_RK_RE_NU_EFF = re.compile(
    r'(?:[νν]_?eff|nu_?eff)\s*(?:\([^)]*\)\s*)?[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
_RK_RE_R_DET = re.compile(
    r'R_?(?:det|base)\s*[=:]\s*([0-9]+\.?[0-9]*)', re.IGNORECASE)
# For R_k final value: match lines starting with R_k and extract the last
# number.  Models write "R_k = 0.272 × (1 - 0.05) + 0.05 = 0.308" —
# the final value is always the last float on the R_k line.
_RK_RE_R_FINAL_LINE = re.compile(
    r'^[^\n]*R_?k\s*[=≈:].*$', re.IGNORECASE | re.MULTILINE)
_RK_RE_TRAILING_FLOAT = re.compile(r'([0-9]+\.?[0-9]*)\s*$')


def _validate_rk_computation(corroboration_text: str) -> Tuple[str, Optional[float], Optional[float]]:
    """Recompute R_k from stated parameters and compare with model's result.

    Returns (status, model_rk, recomputed_rk) where status is one of:
      PASS  — within tolerance 0.01
      WARN  — within tolerance 0.05 but outside 0.01
      FAIL  — beyond tolerance 0.05
      SKIP  — couldn't extract sufficient parameters

    Advisory only — logs discrepancies, never rejects findings.
    """
    if not corroboration_text:
        return "SKIP", None, None

    def _first_float(pattern: re.Pattern, text: str) -> Optional[float]:
        m = pattern.search(text)
        if m:
            try:
                return float(m.group(1))
            except (ValueError, IndexError):
                pass
        return None

    # Extract the model's stated final R_k.
    # Models write "R_k = 0.272 × (1 - 0.05) + 0.05 = 0.308" — the final
    # value is the last float on the last line containing "R_k =".
    model_rk = None
    for line_match in _RK_RE_R_FINAL_LINE.finditer(corroboration_text):
        line = line_match.group()
        trail = _RK_RE_TRAILING_FLOAT.search(line)
        if trail:
            try:
                model_rk = float(trail.group(1))
            except ValueError:
                pass
    if model_rk is None:
        return "SKIP", None, None

    # Extract R_old — required
    R_old = _first_float(_RK_RE_R_OLD, corroboration_text)
    if R_old is None:
        return "SKIP", model_rk, None

    # Extract q directly (trailing float on "q = ..." line), or compute
    # from eta * d * p.  Models write "q = 0.90 × 0.80 × 0.90 = 0.648"
    # where the final value is the trailing float, not the first number.
    q = None
    q_line = _RK_RE_Q_LINE.search(corroboration_text)
    if q_line:
        trail = _RK_RE_TRAILING_FLOAT.search(q_line.group())
        if trail:
            try:
                q = float(trail.group(1))
            except ValueError:
                pass
    if q is None:
        eta = _first_float(_RK_RE_ETA, corroboration_text)
        d = _first_float(_RK_RE_D, corroboration_text)
        p = _first_float(_RK_RE_P, corroboration_text)
        if eta is not None and d is not None and p is not None:
            q = eta * d * p
        else:
            return "SKIP", model_rk, None

    # Phase 1: Detection — R_det = R_old * (1-q) / (1 - q*R_old)
    denom = 1.0 - q * R_old
    if abs(denom) < 1e-12:
        R_det = R_old
    else:
        R_det = R_old * (1.0 - q) / denom

    # Extract S_k and nu_eff for full three-phase computation
    sk = _first_float(_RK_RE_SK, corroboration_text)
    nu_eff = _first_float(_RK_RE_NU_EFF, corroboration_text)

    if sk is not None and nu_eff is not None:
        # Full three-phase: detection -> resolution -> re-injection
        R_base = sk * R_det + (1.0 - sk) * R_old
        recomputed = R_base * (1.0 - nu_eff) + nu_eff
    elif sk is not None:
        # Two-phase only (no re-injection term)
        recomputed = sk * R_det + (1.0 - sk) * R_old
    else:
        # Detection phase only — R_k = R_det
        recomputed = R_det

    recomputed = max(0.0, min(1.0, recomputed))
    delta = abs(model_rk - recomputed)

    if delta <= 0.01:
        return "PASS", model_rk, recomputed
    elif delta <= 0.05:
        return "WARN", model_rk, recomputed
    else:
        return "FAIL", model_rk, recomputed


def _extract_corroboration_sections(response_text: str) -> List[str]:
    """Extract CORROBORATION sections from a model's raw response text.

    Each section runs from 'CORROBORATION' until the next finding boundary
    (FINDING_ID, VERIFIED, ---) or end of text.
    """
    sections: List[str] = []
    # Split on CORROBORATION header
    parts = re.split(r'CORROBORATION\s*[:\-]?\s*', response_text, flags=re.IGNORECASE)
    for part in parts[1:]:  # skip everything before first CORROBORATION
        # Truncate at next finding boundary
        end_match = re.search(
            r'\n\s*(?:FINDING_ID|VERIFIED|---|\n\s*\n\s*FINDING_ID'
            r'|SEVERITY|FIND\s*:|FOLLOW\s*:|\[\s*\{)',
            part, re.IGNORECASE)
        if end_match:
            sections.append(part[:end_match.start()])
        else:
            sections.append(part)
    return sections


def validate_round_rk(
    findings: List[Finding],
    responses: Dict[str, str],
) -> Dict[str, List[Tuple[str, str, Optional[float], Optional[float]]]]:
    """Validate R_k computations for all findings in a round.

    Returns dict keyed by model_id, each value a list of
    (finding_id, status, model_rk, recomputed_rk) tuples.

    Advisory only — logs WARN/FAIL but never rejects findings.
    """
    results: Dict[str, List[Tuple[str, str, Optional[float], Optional[float]]]] = {}

    for model_id, text in responses.items():
        sections = _extract_corroboration_sections(text)
        model_findings = [f for f in findings if f.model_id == model_id]
        model_results: List[Tuple[str, str, Optional[float], Optional[float]]] = []

        # Match sections to findings by position (both are in document order)
        for i, f in enumerate(model_findings):
            if i < len(sections):
                status, model_rk, recomputed = _validate_rk_computation(sections[i])
            else:
                status, model_rk, recomputed = "SKIP", None, None
            model_results.append((f.finding_id, status, model_rk, recomputed))

            if status == "WARN":
                _log(f"  R_k WARN: {f.finding_id} — model={model_rk:.3f}, "
                     f"recomputed={recomputed:.3f}, delta={abs(model_rk - recomputed):.3f}")
            elif status == "FAIL":
                _log(f"  R_k FAIL: {f.finding_id} — model={model_rk:.3f}, "
                     f"recomputed={recomputed:.3f}, delta={abs(model_rk - recomputed):.3f}")

        if model_results:
            results[model_id] = model_results

    return results


def check_sk_threshold(
    sk: float, nu_b: float, nu_f: float,
    q: float, R: float, s_floor: float = 0.0,
) -> Tuple[bool, float]:
    """Check if S_k exceeds the break-even threshold S*.

    Returns (passes, s_star). Fixes below S* do more harm than good
    (Valley of Bad Fixes).
    """
    # Defensive cast and clamp all probability-space inputs to [0, 1]
    sk = max(0.0, min(1.0, float(sk)))
    q = max(0.0, min(1.0, float(q)))
    R = max(0.0, min(1.0, float(R)))
    s_floor = max(0.0, min(1.0, float(s_floor)))
    nu_b = max(0.0, min(1.0, float(nu_b)))
    nu_f = max(0.0, min(1.0, float(nu_f)))
    if nu_b + nu_f > 1.0:
        scale = 1.0 / (nu_b + nu_f)
        nu_b *= scale
        nu_f *= scale

    # Bounded S*: (nu_b + nu_f - nu_b*nu_f - q*R) / (nu_f * (1 - nu_b))
    # Edge cases:
    #   nu_f ≈ 0: fix can't introduce problems → S* = 0 (any fix helps)
    #   nu_b ≈ 1: any modification is risky → S* = 1.0 (no fix good enough)
    if nu_f < 1e-12:
        s_star = 0.0  # no fix-induced re-injection; any positive S_k helps
    elif (1.0 - nu_b) < 1e-12:
        s_star = 1.0  # pathological: any modification introduces full risk
    else:
        denom = nu_f * (1.0 - nu_b)
        s_star = (nu_b + nu_f - nu_b * nu_f - q * R) / denom
        # Clamp to [0, 1]: values outside mean "always pass" or "never pass"
        s_star = max(0.0, min(1.0, s_star))

    effective_threshold = max(s_star, s_floor)
    return sk >= effective_threshold, round(s_star, 4)


def _evaluate_sk_for_findings(
    registry: FindingRegistry,
    source_code: str,
    source_path: str,
    baseline: Dict[str, Any],
    round_idx: int,
    test_cmd: Optional[str] = None,
    s_floor: float = 0.0,
) -> Dict[str, Any]:
    """Evaluate S_k for all findings with proposed fixes in SEARCH/REPLACE format.

    Returns stats dict for round telemetry.
    """
    stats: Dict[str, Any] = {
        "round": round_idx, "evaluated": 0, "admissible": 0,
        "rejected": 0, "escalated": 0, "results": {},
    }

    for cid, entry in registry.entries.items():
        if entry["status"] not in ("OPEN", "CONFIRMED", "CONTESTED"):
            continue
        fix_text = entry.get("proposed_fix", "")
        if not fix_text or "<<<<" not in fix_text:
            continue

        sk_result = compute_sk(
            fix_text, source_code, source_path,
            baseline=baseline, test_cmd=test_cmd,
        )
        stats["evaluated"] += 1

        # Store result on registry entry
        entry["sk_result"] = {
            "sk": sk_result.sk,
            "A": sk_result.A,
            "E": sk_result.E,
            "tristate": sk_result.tristate,
            "blocks_parsed": sk_result.blocks_parsed,
            "blocks_applied": sk_result.blocks_applied,
            "gate_details": sk_result.gate_details,
        }

        # Extract per-finding model parameters (fall back to defaults)
        meta = entry.get("model_params", {})
        nu_b = meta.get("nu_b", 0.05)
        nu_f = meta.get("nu_f", 0.20)
        q = meta.get("q", 0.5)
        R_old = meta.get("R", 0.5)

        # S* threshold check
        if sk_result.tristate == "ADMISSIBLE":
            passes, s_star = check_sk_threshold(
                sk_result.sk, nu_b=nu_b, nu_f=nu_f,
                q=q, R=R_old, s_floor=s_floor,
            )
            entry["sk_result"]["s_star"] = s_star
            entry["sk_result"]["passes_threshold"] = passes
            if passes:
                # Close the R_k loop: compute updated risk
                R_new = compute_rk(
                    R_old=R_old, q=q, sk=sk_result.sk,
                    nu_b=nu_b, nu_f=nu_f,
                )
                entry["sk_result"]["R_old"] = R_old
                entry["sk_result"]["R_new"] = R_new
                stats["admissible"] += 1
                _log(f"  S_k [{cid}]: ADMISSIBLE sk={sk_result.sk:.3f} "
                     f"(S*={s_star:.3f}) R: {R_old:.3f} -> {R_new:.3f}")
            else:
                stats["rejected"] += 1
                entry["sk_result"]["tristate"] = "REJECTED"
                _log(f"  S_k [{cid}]: REJECTED sk={sk_result.sk:.3f} "
                     f"< S*={s_star:.3f} (Valley of Bad Fixes)")
        elif sk_result.tristate == "REJECTED":
            stats["rejected"] += 1
            _log(f"  S_k [{cid}]: REJECTED A={sk_result.A} "
                 f"({sk_result.gate_details})")
        else:
            stats["escalated"] += 1
            _log(f"  S_k [{cid}]: ESCALATE — {sk_result.gate_details}")

        stats["results"][cid] = entry["sk_result"]

    if stats["evaluated"] > 0:
        _log(f"  S_k pipeline: {stats['evaluated']} evaluated, "
             f"{stats['admissible']} ADMISSIBLE, "
             f"{stats['rejected']} REJECTED, "
             f"{stats['escalated']} ESCALATE")
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Preflight
# ─────────────────────────────────────────────────────────────────────────────

def run_preflight(
    exp_config: ExperimentConfig, cdsfl_text: str, cfg: RunnerConfig,
) -> bool:
    _log("=" * 60)
    _log("PREFLIGHT: Testing model connectivity")
    _log("=" * 60)
    test_prompt = (
        "This is a connectivity test. Respond with exactly:\n"
        "STATUS: OK\nMODEL: [your model name]\nNothing else."
    )
    baseline = set(cfg.models)
    all_ok = True
    for mc in exp_config.models:
        if mc.label not in baseline:
            continue
        _log(f"  Testing {mc.label}...")
        try:
            text, elapsed = dispatch_to_model(mc, test_prompt, cdsfl_text)
            ok = len(text.strip()) > 5
            _log(f"  {mc.label}: {'OK' if ok else 'FAILED'} ({elapsed:.1f}s)")
            if not ok:
                all_ok = False
        except Exception as e:
            _log(f"  {mc.label}: FAILED — {e}")
            all_ok = False
    return all_ok


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment loop
# ─────────────────────────────────────────────────────────────────────────────

def _find_or_create_logs_dir(cfg: RunnerConfig) -> Path:
    if cfg.resume:
        logs_root = REPO_ROOT / "bench" / "logs"
        candidates = sorted(
            logs_root.glob(f"{cfg.experiment_name}_*"),
            key=lambda p: p.name, reverse=True,
        )
        for c in candidates:
            if (c / "checkpoint.json").exists():
                return c
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return REPO_ROOT / "bench" / "logs" / f"{cfg.experiment_name}_{ts}"


def run_experiment(
    exp_config: ExperimentConfig,
    cdsfl_text: str,
    cfg: RunnerConfig,
) -> Dict[str, Any]:
    """Run a parameterised CDSFL experiment.

    This is the generic entry point for Exp 37+ and Bench Run 2.
    All experiment-specific parameters come from cfg (RunnerConfig).
    """
    logs_dir = _find_or_create_logs_dir(cfg)
    logs_dir.mkdir(parents=True, exist_ok=True)

    baseline = set(cfg.models)

    topo_desc = (
        f"relay/{cfg.relay_mode}" if cfg.topology == "relay"
        else "star/blackboard"
    )
    _log("=" * 60)
    _log(f"EXPERIMENT: {cfg.experiment_name}")
    _log(f"  Topology: {topo_desc}")
    _log(f"  Pattern: {cfg.pattern}")
    _log(f"  Max rounds: {cfg.max_rounds} (extension to {cfg.extension_cap})")
    _log(f"  Convergence: state-based, earliest R{cfg.earliest_stop_round}")
    _log(f"  Target: {cfg.test_article}")
    _log(f"  Context: {cfg.context_files}")
    _log(f"  Models: {sorted(baseline)}")
    _log(f"  Domain: {cfg.domain}")
    _log(f"  Logs: {logs_dir}")
    _log("=" * 60)

    # Load source files
    target_path = Path(cfg.test_article)
    if not target_path.is_absolute():
        target_path = REPO_ROOT / target_path
    target_text = target_path.read_text(encoding="utf-8")
    try:
        target_rel = target_path.relative_to(REPO_ROOT)
    except ValueError:
        target_rel = target_path

    context_parts = []
    context_paths = []
    for ctx in cfg.context_files:
        ctx_path = Path(ctx)
        if not ctx_path.is_absolute():
            ctx_path = REPO_ROOT / ctx_path
        context_paths.append(ctx_path)
        ctx_text = ctx_path.read_text(encoding="utf-8")
        try:
            ctx_rel = ctx_path.relative_to(REPO_ROOT)
        except ValueError:
            ctx_rel = ctx_path
        context_parts.append(
            f"=== CONTEXT FILE: {ctx_rel} ({len(ctx_text):,} chars) ===\n"
            f"(Read-only context — do NOT review this file)\n{ctx_text}"
        )

    full_code = (
        f"=== TARGET FILE (REVIEW THIS): {target_rel} "
        f"({len(target_text):,} chars) ===\n{target_text}\n\n"
        + "\n\n".join(context_parts)
    )
    source_paths_str = [str(target_path)] + [str(p) for p in context_paths]

    _log(f"  Target: {len(target_text):,} chars")
    _log(f"  Context: {len(context_parts)} files")
    _log(f"  Total: {len(full_code):,} chars with headers")

    # Burst decomposition planning
    burst_plan = None
    burst_state: Optional[Dict[str, Any]] = None
    context_chars = sum(len(p) for p in context_parts)

    if cfg.burst_mode != "off":
        from bench.burst_planner import (
            should_burst, plan_phases, build_phase_code,
            build_integration_code, build_findings_summary,
            phase_convergence_overrides, integration_convergence_overrides,
            extract_signatures,
        )
        need_burst = cfg.burst_mode == "on"
        burst_reason = "burst_mode=on" if need_burst else ""

        if not need_burst:
            need_burst, burst_reason = should_burst(
                len(target_text), context_chars,
                MODEL_SPECS, INITIAL_FINGERPRINTS, sorted(baseline),
            )

        if need_burst:
            burst_plan = plan_phases(
                target_text, MODEL_SPECS, INITIAL_FINGERPRINTS,
                sorted(baseline), str(target_rel),
            )
            # Context file signatures for integration round
            ctx_sigs = ""
            for ctx_path in context_paths:
                try:
                    ctx_text = ctx_path.read_text(encoding="utf-8")
                    ctx_sigs += (
                        f"# === {ctx_path.name} ===\n"
                        + extract_signatures(ctx_text) + "\n"
                    )
                except Exception:
                    pass

            burst_state = {
                "phase_idx": 0,
                "phase_round_offset": 0,
                "phase_findings": {},  # {phase_name: findings_summary}
                "integration_started": False,
                "integration_done": False,
                "original_cfg_overrides": {},
                "context_signatures": ctx_sigs,
            }
            _log(f"\n  BURST MODE: {burst_reason}")
            _log(f"  Phases: {len(burst_plan.phases)} + integration round")
            _log(f"  Budget: {burst_plan.budget_chars_per_phase:,} chars/phase")
            _log(f"  Signatures: {len(burst_plan.signatures):,} chars")
            for p in burst_plan.phases:
                sections = [s.name for s in p.sections]
                _log(f"    Phase {p.index}: {p.name} "
                     f"({p.char_count:,} chars, {len(sections)} sections)")

            # Override full_code and base_prompt for first phase
            phase = burst_plan.phases[0]
            full_code = build_phase_code(
                phase, str(target_rel), burst_plan.signatures)
            _log(f"\n  Starting Phase 0: {phase.name}")

            # Apply Phase 0 convergence overrides at initialisation —
            # without this, Phase 0 runs with base config thresholds
            # and can consume the entire round budget.
            overrides = phase_convergence_overrides(0)
            cfg = replace(cfg, **overrides)
            _log(f"  Phase 0 overrides: earliest_stop={overrides['earliest_stop_round']}, "
                 f"rho_earliest={overrides['rho_earliest_round']}")

    # Build DynamicManager
    dm_config = DynamicManagementConfig(
        # Decomposition is now fingerprint-aware (13 April 2026):
        # _should_decompose() uses per-model observed prompt limits from
        # fingerprints, falling back to LENGTH_THRESHOLD (80K) when no
        # observation data exists. This set is for immune escalation only.
        pre_decompose_models=set(),
        no_exclusion_mode=True,
    )
    dm_config.max_rounds = cfg.max_rounds
    dm_config.domain = cfg.domain  # Exp 39 plumbing fix: propagate domain to InsectBrain → immune pipeline
    model_specs = build_model_specs(exp_config)
    mgr = DynamicManager(model_specs, dm_config)

    # Insect Brain
    brain = InsectBrain(config=dm_config, logs_dir=logs_dir, source_paths=source_paths_str)
    brain.initialise(model_labels=sorted(baseline))

    # Endocrine Layer
    endo = EndocrineLayer(source_paths=source_paths_str, test_cmd=None, max_fix_evals=20)

    # Finding registry
    registry = FindingRegistry()

    # Fingerprints
    observed_fingerprints = _load_fingerprints()

    # Resume
    start_round = 0
    novelty_counts: List[int] = []
    raw_counts: List[int] = []
    rho_history: List[float] = []
    cumulative_context_chars = 0
    per_model_context: Dict[str, int] = {}
    gamma_history: List[float] = []
    gate_history: List[bool] = []
    open_ch_history: List[int] = []
    stall_history: List[Dict[str, int]] = []
    # Exp 40 fix 1A.3: track novel CRITICAL count per round for γ-alt gate.
    novel_critical_history: List[int] = []
    consecutive_churn_rounds: int = 0  # D1: tracks sustained churn for phase transition

    if cfg.resume and brain.load_checkpoint():
        start_round = brain.state.current_round + 1
        _log(f"  RESUMED from round {start_round}")
        runner_ckpt = brain.logs_dir / "runner_state.json"
        if runner_ckpt.exists():
            try:
                ckpt_data = json.loads(runner_ckpt.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as _ckpt_err:
                _log(f"  WARNING: runner_state.json corrupted ({_ckpt_err}), "
                     f"falling back to brain checkpoint only")
                ckpt_data = {}
            registry = FindingRegistry.from_dict(ckpt_data.get("registry", {}))
            novelty_counts = ckpt_data.get("novelty_counts", [])
            raw_counts = ckpt_data.get("raw_counts", [])
            rho_history = ckpt_data.get("rho_history", [])
            gamma_history = ckpt_data.get("gamma_history", [])
            gate_history = ckpt_data.get("gate_history", [])
            open_ch_history = ckpt_data.get("open_ch_history", [])
            stall_history = ckpt_data.get("stall_history", [])
            novel_critical_history = ckpt_data.get("novel_critical_history", [])
            cumulative_context_chars = ckpt_data.get("cumulative_context_chars", 0)
            consecutive_churn_rounds = ckpt_data.get("consecutive_churn_rounds", 0)
            # R39-06: Restore ITC module state for quality tracking continuity
            _restored_itc = ckpt_data.get("itc_model_state")
            if _restored_itc and isinstance(_restored_itc, dict):
                _itc_model_state.clear()
                _itc_model_state.update(_restored_itc)
            _restored_hil = ckpt_data.get("itc_hil_flags")
            if _restored_hil and isinstance(_restored_hil, list):
                _itc_hil_flags.clear()
                _itc_hil_flags.extend(_restored_hil)
            # R39-04: Restore burst_state if it was persisted
            _restored_burst = ckpt_data.get("burst_state")
            if _restored_burst and isinstance(_restored_burst, dict):
                burst_state = _restored_burst
                _log(f"  Burst state restored: phase_idx={burst_state.get('phase_idx', 0)}")
            _log(f"  Registry restored: {len(registry.entries)} entries")

    experiment_start = time.monotonic()
    effective_max = cfg.max_rounds
    loop_cap = cfg.extension_cap
    # Burst mode: extend loop cap to accommodate all phases + integration
    if burst_plan:
        phase_rounds_each = 8  # generous per-phase budget
        burst_total = (len(burst_plan.phases) + 1) * phase_rounds_each
        loop_cap = max(loop_cap, burst_total)
        effective_max = max(effective_max, burst_total)
        _log(f"  Burst loop cap: {loop_cap} rounds "
             f"({len(burst_plan.phases)} phases × {phase_rounds_each} + integration)")
    extended = False
    rho_avg = 1.0
    rho_churn = False

    # S_k baseline capture (before any fixes are applied)
    sk_baseline: Dict[str, Any] = {}
    if cfg.sk_enabled:
        _log("  S_k pipeline: capturing baseline gate scores...")
        sk_baseline = _capture_baseline(target_text, source_path=str(target_path))
        _log(f"  S_k baseline: ruff={sk_baseline.get('ruff_violations', '?')}, "
             f"bandit={sk_baseline.get('bandit_findings', '?')}")

    # Build awareness preamble
    roster_lines = "\n".join(
        f"  - {label}: {MODEL_ROSTER.get(label, label)}"
        for label in sorted(baseline)
    )
    topo_instruction = (
        _RELAY_TOPOLOGY_INSTRUCTION if cfg.topology == "relay"
        else _STAR_TOPOLOGY_INSTRUCTION
    )
    awareness_preamble = (
        f"You are one of {len(baseline)} AI models in a distributed code review "
        f"under CDSFL constraints with FFF methodology. The models are:\n"
        f"{roster_lines}\n\n"
        f"{topo_instruction}"
        f"{_POC_CONTEXT_INSTRUCTION}"
        f"{_MACHINE_COMMS_INSTRUCTION}"
        f"{_GOOD_ENOUGH_INSTRUCTION}"
    )

    def _build_prompt(code_payload: str, artifact_label: str = "") -> str:
        """Build base prompt from awareness preamble + code payload."""
        label = artifact_label or f"{target_rel} + Context"
        return (
            f"{awareness_preamble}"
            f"YOUR TASK:\n"
            f"Review {target_rel} under full CDSFL + FFF constraints.\n\n"
            f"For each finding, provide (keys in this exact order):\n"
            f"  FINDING_ID: unique identifier (e.g., F001). IMPORTANT: your "
            f"finding IDs must be STABLE across rounds. If you filed F001 in "
            f"Round 3, F001 in Round 4 must refer to the same bug.\n"
            f"  SEVERITY: 0.0 to 1.0 (1.0 = critical)\n"
            f"  FLAW_CLASS: integer category (1=logic, 2=interface, 3=notation, "
            f"4=completeness, 5=correctness, 6=edge-case, 7=performance, "
            f"8=documentation)\n"
            f"  ABSTRACTION_INDEX: 0.0 to 1.0 (0=surface, 1=architectural)\n"
            f"  FIND: what is wrong, where, and what is the evidence\n"
            f"  FOLLOW: trace downstream consequences BEFORE proposing a fix\n"
            f"  ANALYSE: classify constraint as HARD or SOFT. State premises "
            f"explicitly, derive conclusion through concrete evidence "
            f"(Meta Structured Reasoning Protocol). "
            f"State CONFIRMED/UNCERTAIN/REJECTED.\n"
            f"  FIX: the simplest sufficient correction addressing root cause "
            f"AND FOLLOW consequences (for CONFIRMED findings only). Express "
            f"as SEARCH/REPLACE blocks so S_k can verify:\n"
            f"    <<<< SEARCH file_path\n"
            f"    [exact current content to replace — copy verbatim from source]\n"
            f"    ====\n"
            f"    [exact replacement content]\n"
            f"    >>>> REPLACE\n"
            f"  FALSIFICATION: (MANDATORY) state the FALSIFIER (what would "
            f"disprove your FIND), your ATTEMPT to satisfy it, and the RESULT. "
            f"Then try to break your FIX. Findings without this section "
            f"will be rejected.\n"
            f"  CORROBORATION: (MANDATORY) compute your residual risk R_k "
            f"using the self-assessment equation in the operational directive. "
            f"Show R_old, your numerical estimates for η, d, p, S_k, ν_eff, "
            f"and the resulting R_k. Qualitative-only assessment will be "
            f"flagged. Example format:\n"
            f"    R_old=0.50, η=0.80, d=0.70, p=0.60, S_k=0.75, ν_eff=0.15\n"
            f"    R_k = 0.50 × (1 - 0.80×0.70×0.60) × 0.75 + 0.15 = 0.32\n"
            f"  ADMISSIBILITY: (MANDATORY, FFAFP §15) state PASS/FAIL for "
            f"each of S_min, G-completeness, d_tool, σ_measured, q_retest. "
            f"Example format:\n"
            f"    S_min: PASS (location=bench/foo.py:42, mechanism=off-by-one, "
            f"evidence=test_case_7)\n"
            f"    G-completeness: PASS (verifier can reproduce from finding text)\n"
            f"    d_tool: PASS (pytest ran, 4 of 5 tests caught the class)\n"
            f"    σ_measured: PASS (pre-fix: 1 failure; post-fix: 0 failures)\n"
            f"    q_retest: PASS (η from similarity, d from pytest, p from domain)\n"
            f"  NOVELTY: (MANDATORY, Stage 6 §16) state (ν_k, c_ext, H/H_max) "
            f"as three independent scores. Do not collapse them. If you did "
            f"not perform an external search, set c_ext = 0 explicitly. "
            f"Example format:\n"
            f"    ν_k: 0.85 — searched arXiv for 'X in Y'; no matches for "
            f"this specific mechanism\n"
            f"    c_ext: 0.60 — arXiv + Semantic Scholar; Google Scholar skipped\n"
            f"    H/H_max: 0.75 — abstraction level is high (architectural)\n"
            f"    Citations: arXiv:2502.09858, 10.1234/example\n"
            f"  VERIFIED: TRUE if proven, FALSE if assertion\n\n"
            f"PRIOR REVIEW CONTEXT: Do not re-report issues already present "
            f"in the registry summary. Duplicate findings waste compute. "
            f"Focus on genuinely new issues and regressions.\n\n"
            f"Produce ALL findings. Do not hold back.\n\n"
            f"=== ARTIFACT: {label} ({len(code_payload):,} chars) ===\n\n"
            f"{code_payload}\n\n"
            f"=== END ARTIFACT ===\n\n"
            f"Produce your findings now."
        )

    base_prompt = _build_prompt(full_code)

    result: Dict[str, Any] = {
        "experiment": cfg.experiment_name,
        "topology": cfg.topology,
        "relay_mode": cfg.relay_mode if cfg.topology == "relay" else None,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "pattern": cfg.pattern,
        "models": sorted(baseline),
        "target_file": str(target_rel),
        "context_files": [str(p) for p in cfg.context_files],
        "max_rounds": cfg.max_rounds,
        "extension_cap": cfg.extension_cap,
        "domain": cfg.domain,
        "convergence_config": {
            "earliest_stop": cfg.earliest_stop_round,
            "consecutive_required": cfg.consecutive_rounds_required,
            "rho_threshold": cfg.rho_threshold,
            "rho_rolling_window": cfg.rho_rolling_window,
        },
        "rounds": [],
    }

    # Feedback channel state — populated at end of round K, consumed at start
    # of round K+1. cdsfl_operational.md §17. See bench/dm/_feedback.py for
    # the constructor; this variable holds the rendered per-model sections.
    feedback_sections_for_next_round: Dict[str, str] = {}
    feedback_enabled = _feedback_channel_enabled(cfg)

    # Exp 40 fix 1D.5 — S_k SEARCH/REPLACE format pre-check.
    # Populated at end of round K with (canonical_id, diagnostic_reason)
    # pairs for findings whose proposed_fix did not parse as an S_k block.
    # Consumed at start of round K+1 as a reformat-request prompt section.
    sk_reformat_requests_for_next_round: List[Tuple[str, str]] = []

    # ── Main loop ──
    for round_idx in range(start_round, loop_cap):
        if round_idx >= effective_max:
            break

        round_start = time.monotonic()
        wall_elapsed = round_start - experiment_start
        if wall_elapsed > cfg.wall_clock_cap_s:
            _log(f"\nWALL CLOCK CAP reached ({wall_elapsed:.0f}s). Stopping.")
            break

        _log(f"\n{'---' * 20}")
        round_type = "blind" if round_idx == 0 else "adaptive"
        _log(f"Round {round_idx}/{effective_max - 1} ({round_type})")
        _log(f"{'---' * 20}")

        # Update relay budgets from fingerprint data before dispatch.
        # Each model's budget adapts to its measured prompt performance.
        for _bl in cfg.models:
            brain.config.context_budget_overrides[_bl] = (
                get_effective_context_budget(_bl, observed_fingerprints)
            )

        # Dispatch — topology-dependent
        if cfg.topology == "relay":
            # Exp 40 fix 1D.5: attach S_k reformat requests to the relay
            # base_prompt so they reach every relay hop. Star branch injects
            # via registry_summary below; relay has no registry_summary slot.
            _relay_prompt = base_prompt
            if sk_reformat_requests_for_next_round:
                _sk_reformat = build_sk_reformat_requests(
                    sk_reformat_requests_for_next_round,
                )
                if _sk_reformat:
                    _relay_prompt = _sk_reformat + "\n\n" + base_prompt
            findings, responses, per_model_durations, prompt_lengths = _dispatch_round_relay(
                exp_config, mgr, brain, _relay_prompt, cdsfl_text, full_code,
                round_idx, cfg, registry=registry,
            )
        else:
            registry_summary = registry.build_summary(round_idx) if round_idx > 0 else ""
            # Per-round metrics injection — models use γ, ρ, registry state to
            # calibrate effort (cdsfl_operational.md §8, §13). Mirrors Exp 37
            # run_exp37_evidence.py lines 2310-2359.
            if round_idx > 0 and registry is not None:
                _rho_val = rho_history[-1] if rho_history else 0.0
                _rho_bar3 = (sum(rho_history[-3:]) / min(3, len(rho_history))
                             if rho_history else 0.0)
                _gamma_val = gamma_history[-1] if gamma_history else 0.0
                _n_open = sum(1 for e in registry.entries.values()
                              if e.get("status") in ("OPEN", "CONTESTED"))
                _n_confirmed = sum(1 for e in registry.entries.values()
                                   if e.get("status") == "CONFIRMED")
                _n_closed = sum(1 for e in registry.entries.values()
                                if e.get("status") in ("CLOSED", "MERGED"))
                _metrics = (
                    f"\n=== PANEL METRICS (Round {round_idx}) ===\n"
                    f"ρ (discovery efficiency / semantic novelty rate) = "
                    f"{_rho_val:.3f}\n"
                    f"ρ̄₃ (3-round rolling average) = {_rho_bar3:.3f}\n"
                    f"γ (Duane reliability growth) = {_gamma_val:.3f}\n"
                    f"Registry: {_n_open} OPEN, {_n_confirmed} CONFIRMED, "
                    f"{_n_closed} CLOSED/MERGED\n"
                    f"\nInterpretation: "
                )
                if _gamma_val >= 0.45:
                    _metrics += (
                        "Strong depletion — novel discoveries are rare. If you "
                        "cannot find genuinely new issues, report that honestly. "
                        "Redundant re-descriptions waste compute.\n"
                    )
                elif _gamma_val >= 0.30:
                    _metrics += (
                        "Moderate depletion — novel discoveries are slowing. "
                        "Focus on areas not yet covered by existing findings. "
                        "Check the registry before submitting.\n"
                    )
                else:
                    _metrics += (
                        "Productive phase — continue finding and falsifying.\n"
                    )
                # Semantic novelty feedback — 3 graduated signals
                # (Ported from run_exp37_evidence.py lines 2354-2371)
                if _rho_val >= 0.5:
                    _metrics += (
                        f"High semantic novelty (ρ={_rho_val:.3f}). Your recent "
                        f"findings are genuinely new. Continue this trajectory.\n"
                    )
                elif _rho_val > 0.0 and _gamma_val >= 0.30:
                    _metrics += (
                        f"Moderate novelty (ρ={_rho_val:.3f}) with depletion "
                        f"(γ={_gamma_val:.3f}). Concentrate on unexplored areas "
                        f"and deeper structural issues.\n"
                    )
                # ρ̄₃ redundancy warning
                if _rho_bar3 < 0.25 and round_idx >= 3:
                    _metrics += (
                        f"⚠ HIGH REDUNDANCY (ρ̄₃={_rho_bar3:.3f}). Your last 3 "
                        f"rounds averaged <25% novelty. Most findings are "
                        f"duplicating existing registry entries. Check the "
                        f"registry carefully before submitting.\n"
                    )
                _metrics += "=== END METRICS ===\n\n"
                registry_summary = _metrics + registry_summary

            # Exp 40 fix 1D.1 / 1D.2 / 1D.4: inject round-context helpers.
            # Consolidation preamble fires during the final
            # cfg.consolidation_rounds rounds. Prior-fix summary lists
            # closed canonical entries so models do not re-surface them.
            # Windowed context compresses older rounds into a one-line
            # summary for long runs.
            _context_prefix = ""
            _consolidation = build_consolidation_preamble(
                round_idx=round_idx,
                max_rounds=effective_max,
                consolidation_rounds=cfg.consolidation_rounds,
            )
            if _consolidation:
                _context_prefix += _consolidation
            if cfg.prior_fix_summary_enabled:
                _fix_summary = build_prior_fix_summary(
                    registry=registry,
                    round_idx=round_idx,
                    max_entries=cfg.prior_fix_summary_max_entries,
                    max_chars=cfg.prior_fix_summary_max_chars,
                )
                if _fix_summary:
                    _context_prefix += _fix_summary
            if cfg.windowed_context_enabled and result.get("rounds"):
                _window = build_windowed_context(
                    per_round_summaries=result["rounds"],
                    round_idx=round_idx,
                    window_full_rounds=cfg.windowed_context_full_rounds,
                    max_chars=cfg.windowed_context_max_chars,
                )
                if _window:
                    _context_prefix += _window
            # Exp 40 fix 1D.5: S_k reformat request — rendered at round K+1
            # from round K's pre-check results. Non-empty only when prior
            # round emitted unparseable proposed_fix entries.
            if sk_reformat_requests_for_next_round:
                _sk_reformat = build_sk_reformat_requests(
                    sk_reformat_requests_for_next_round,
                )
                if _sk_reformat:
                    _context_prefix += _sk_reformat + "\n\n"
            if _context_prefix:
                registry_summary = _context_prefix + registry_summary

            findings, responses, per_model_durations, prompt_lengths = _dispatch_round_star(
                exp_config, mgr, brain, base_prompt, registry_summary,
                cdsfl_text, full_code, round_idx, cfg, registry=registry,
                feedback_sections=(
                    feedback_sections_for_next_round if feedback_enabled else None
                ),
            )

        # Safety check
        problem = _safety_check(responses)
        if problem:
            _log(f"\n*** ALL MODELS FAILED: {problem} ***")
            result["terminated"] = problem
            break

        # R_k recomputation validation (advisory)
        rk_validation = validate_round_rk(findings, responses)
        rk_summary = {
            model: {s: sum(1 for _, st, _, _ in res if st == s)
                    for s in ("PASS", "WARN", "FAIL", "SKIP")}
            for model, res in rk_validation.items()
        }
        for model, counts in rk_summary.items():
            parts = []
            for s in ("PASS", "WARN", "FAIL", "SKIP"):
                if counts.get(s, 0):
                    parts.append(f"{s}={counts[s]}")
            if parts:
                _log(f"  R_k validation [{model}]: {', '.join(parts)}")

        # Register findings
        novel_this_round = 0
        novel_critical_this_round = 0  # Exp 40 1A.3: severity >= 0.7
        # Exp 40 fix 1D.5: collect findings whose proposed_fix is non-empty
        # but does not parse as an S_k block. Fed to next round as a
        # reformat-request prompt section.
        sk_reformat_requests_for_next_round = []
        for f in findings:
            existing = registry.lookup_alias(f.model_id, f.finding_id)
            if existing is None:
                cid = registry.register(f, f.model_id)
                novel_this_round += 1
                if getattr(f, "severity", 0.0) >= 0.7:
                    novel_critical_this_round += 1
                # 1D.5 pre-check: only for novel findings with a proposed fix.
                fix_text = getattr(f, "proposed_fix", "") or ""
                if fix_text.strip():
                    ok, reason = check_sk_format_admissible(fix_text)
                    if not ok:
                        sk_reformat_requests_for_next_round.append((cid, reason))
            else:
                registry.add_verdict(existing, f.model_id, "CONFIRM", round_idx)

        novelty_counts.append(novel_this_round)
        novel_critical_history.append(novel_critical_this_round)  # Exp 40 1A.3
        raw_counts.append(len(findings))

        # A2: Rho
        rho_current, rho_avg, rho_churn = _compute_rho(novelty_counts, raw_counts, cfg)
        rho_history.append(rho_current)
        # D1: track consecutive churn rounds for phase transition
        if rho_churn:
            consecutive_churn_rounds += 1
        else:
            consecutive_churn_rounds = 0
        _log(f"  Registry: {novel_this_round} novel / {len(findings)} raw, "
             f"{len(registry.entries)} total, "
             f"rho={rho_current:.3f}, rho_avg={rho_avg:.3f}"
             f"{' [CHURN]' if rho_churn else ''}"
             f"{f' (churn x{consecutive_churn_rounds})' if consecutive_churn_rounds > 1 else ''}")

        # Parse verdicts
        for model_id, raw_text in responses.items():
            for verdict_type, canonical_id, evidence in _parse_verdicts(raw_text, model_id, round_idx):
                if verdict_type == "MERGE":
                    source = _resolve_merge_source(evidence, model_id, registry)
                    if source and source != canonical_id:
                        registry.add_verdict(source, model_id, "MERGE", round_idx,
                                             f"merged_into={canonical_id}")
                    else:
                        registry.add_verdict(canonical_id, model_id, "CONFIRM", round_idx, evidence)
                else:
                    registry.add_verdict(canonical_id, model_id, verdict_type, round_idx, evidence)

        # Status transitions
        _update_finding_statuses(registry, round_idx, cfg=cfg)
        registry.auto_resolve_contested(round_idx)

        # A3: HIL escalation
        registry.escalate_stale_contested(round_idx, max_contested_rounds=cfg.max_contested_rounds)

        # Persist round
        round_elapsed = time.monotonic() - round_start
        brain.persist(round_idx, responses, findings, duration_s=round_elapsed)

        # Endocrine
        round_timings = _build_round_timings(responses, per_model_durations, findings, round_idx)
        for label, text in responses.items():
            per_model_context[label] = per_model_context.get(label, 0) + len(text)
            cumulative_context_chars += len(text)

        endo_report = endo.run(
            round_idx=round_idx, findings=findings,
            round_timings=round_timings,
            cumulative_context_chars=cumulative_context_chars,
            context_budget=max(CONTEXT_CHAR_BUDGET.values()),
            novelty_counts=novelty_counts,
        )

        # Immune pipeline
        immune_result = brain.run_immune_pipeline(findings)
        for f in findings:
            if f.verified:
                canonical = registry.lookup_alias(f.model_id, f.finding_id)
                if canonical:
                    registry.mark_verified(canonical)

        # Feedback channel (cdsfl_operational.md §17) — close the loop by
        # assembling per-model feedback from round K's schema outputs. The
        # result is injected at the top of round K+1's prompt so flagged
        # findings receive corrective action, not silent repetition.
        # Runs after immune_result is available. Defensive: build failures
        # never crash the loop, they simply yield empty feedback.
        if feedback_enabled:
            feedback_sections_for_next_round = _build_feedback_for_next_round(
                round_idx=round_idx,
                findings=findings,
                responses=responses,
                immune_result=immune_result,
                rk_validation=rk_validation,
                cfg=cfg,
            )
            if feedback_sections_for_next_round:
                _log(
                    f"  [feedback] round {round_idx} → round {round_idx + 1}: "
                    f"{len(feedback_sections_for_next_round)} model(s) flagged"
                )

        # Shadow cells (Macrophage + Ouroboros) — run after main pipeline, zero verdict effect
        shadow_cell_data = _run_shadow_cells(
            round_idx=round_idx,
            immune_result=immune_result,
            findings=findings,
            exp_config=cfg.shadow_cell_config,
            logs_dir=brain.logs_dir,
        )

        # CC2v verification (A5)
        verification_stats = _verification_step(
            registry, round_idx, full_code, exp_config.models, cfg)

        # S_k solution verification pipeline
        sk_stats: Dict[str, Any] = {}
        if cfg.sk_enabled:
            sk_stats = _evaluate_sk_for_findings(
                registry, target_text, str(target_rel),
                baseline=sk_baseline,
                round_idx=round_idx,
                test_cmd=cfg.test_cmd,
                s_floor=cfg.sk_s_floor,
            )

        # ITC per-model
        for model_label in list(baseline):
            model_findings = [f for f in findings if f.model_id == model_label]
            model_text = responses.get(model_label, "")
            prior_ids: Set[str] = set()
            current_ids = {f.finding_id for f in model_findings}
            if brain.state.all_findings and len(brain.state.all_findings) >= 2:
                prior_ids = {
                    f.finding_id for f in brain.state.all_findings[-2]
                    if f.model_id == model_label
                }
            dispatch_err = "no_response" if model_label not in responses else None
            raw_markers = len(_FINDING_DECL_RE.findall(model_text))
            # Count verdicts for this model — verdicts are valid structured
            # output that should count towards parse yield (P2 fix).
            model_verdicts = len(_parse_verdicts(model_text, model_label, round_idx))
            # ORDERING INVARIANT: _itc_detect MUST run before
            # _update_observed_fingerprint. ITC detect populates
            # parse_yield_history in _itc_model_state; the fingerprint
            # quality gate reads it to decide whether to record prompt
            # size in budget history. Reversing the order would cause
            # stale/missing yield data in the quality gate.
            classification = _itc_detect(
                model_label, round_idx, len(model_findings), model_text,
                prior_ids, current_ids, dispatch_error=dispatch_err,
                raw_finding_markers=raw_markers,
                verdict_count=model_verdicts,
            )
            if classification:
                _itc_adapt(model_label, classification, round_idx,
                           rho_rolling_avg=rho_avg, rho_threshold=cfg.rho_threshold)
            elif model_label in _itc_model_state:
                _itc_clear_adaptation(model_label)
            _update_observed_fingerprint(
                observed_fingerprints, model_label, round_idx,
                len(model_findings), len(model_text),
                prompt_chars=prompt_lengths.get(model_label, 0),
                raw_finding_markers=raw_markers,
                dispatch_error=dispatch_err,
            )

        # Directed messages (relay only)
        if cfg.topology == "relay" and cfg.relay_mode == "directed":
            for label, text in responses.items():
                if text:
                    brain.extract_directed_messages(label, text, round_idx)

        # Gamma
        gamma = _estimate_gamma(novelty_counts, cfg.min_rounds_for_gamma)
        gamma_history.append(gamma)
        gate_level, gamma_passed = _check_gamma_gate(gamma, round_idx, cfg)

        _log(f"  gamma: {gamma:.3f} ({gate_level}, "
             f"{'passed' if gamma_passed else 'BLOCKED'}) — {_interpret_gamma(gamma)}")
        _log(f"  Round {round_idx}: {len(findings)} findings, {round_elapsed:.1f}s")

        # Convergence gate
        converged, conv_reason = _check_state_convergence(
            round_idx, registry, novel_this_round, gamma, gate_history, cfg,
            open_ch_history=open_ch_history,
            rho_rolling_avg=rho_avg, rho_churn=rho_churn,
        )
        _log(f"  Convergence: {conv_reason}")

        # Exp 40 fix 1A.3: γ-based alternative convergence path.
        # Documented in Exp 39 sub-experiment configs but previously
        # never implemented. Fires when cumulative depletion (γ ≥ 0.30)
        # or critical-severity exhaustion (3r zero novel CRIT) is reached.
        gamma_alt_converged, gamma_alt_reason = _check_gamma_alt_convergence(
            round_idx, gamma, novel_critical_history, cfg,
        )
        if gamma_alt_converged and not converged:
            _log(f"  γ-alt: {gamma_alt_reason}")
            converged = True
            conv_reason = gamma_alt_reason
        elif not gamma_alt_converged:
            # Log but don't promote — main gate governs until γ-alt fires.
            _log(f"  γ-alt: {gamma_alt_reason}")

        # Stall detector
        stall_result = _check_stall_convergence(
            round_idx, registry, gamma, stall_history, cfg,
            consecutive_churn_rounds=consecutive_churn_rounds)

        # Checkpoint — atomic write to prevent corruption on interrupt
        ckpt_path = brain.logs_dir / "runner_state.json"
        _ckpt_data = json.dumps({
            "registry": registry.to_dict(),
            "novelty_counts": novelty_counts,
            "raw_counts": raw_counts,
            "rho_history": [round(r, 6) for r in rho_history],
            "gamma_history": [round(g, 6) for g in gamma_history],
            "gate_history": gate_history,
            "open_ch_history": open_ch_history,
            "stall_history": stall_history,
            "novel_critical_history": novel_critical_history,
            "cumulative_context_chars": cumulative_context_chars,
            "consecutive_churn_rounds": consecutive_churn_rounds,
            "itc_model_state": _itc_model_state,
            "itc_hil_flags": _itc_hil_flags,
            "burst_state": burst_state if burst_state else None,
        }, indent=2, default=str)
        _ckpt_tmp = ckpt_path.with_suffix(".json.tmp")
        _ckpt_tmp.write_text(_ckpt_data, encoding="utf-8")
        _ckpt_tmp.replace(ckpt_path)

        # Round data for report
        # Gemini 3.1 Pro + Codex 5.3 confer (13 April 2026): round report was
        # counts-only, making HIL review of intermediate rounds impossible.
        # Now includes per-finding summaries with provenance.
        round_findings_detail = [
            {
                "finding_id": f.finding_id,
                "model_id": f.model_id,
                "flaw_class": f.flaw_class,
                "severity": f.severity,
                "description": f.description[:500],
                "verified": f.verified,
                "escalated": f.escalated,
                "origin_type": getattr(f, "origin_type", ""),
                "source_ref": getattr(f, "source_ref", ""),
                "target_file": getattr(f, "target_file", ""),
            }
            for f in findings
        ]
        # Exp 40 fix 1E.7: cross-model diversity (compliance-theatre detector).
        # For each finding, extract the §18 alternative blocks from the
        # emitting model's raw response; pool across the panel; compute mean
        # pairwise Jaccard. Logging-only — does not gate admission or R_k.
        cross_model_diversity: Optional[Dict[str, Any]] = None
        try:
            per_model_alts: List[Tuple[str, str]] = []
            for f in findings:
                raw = responses.get(f.model_id, "")
                if not raw:
                    continue
                alts = parse_alternative_block(
                    raw, f.finding_id, f.description or "",
                )
                for alt in alts:
                    alt_text = getattr(alt, "text", "") or ""
                    if alt_text.strip():
                        per_model_alts.append((f.model_id, alt_text))
            if per_model_alts:
                cross_model_diversity = diversity_signal_from_round(per_model_alts)
        except Exception as _e:
            # Logging-only metric — never crash the loop on parse errors.
            cross_model_diversity = {"error": f"{type(_e).__name__}: {_e}"}

        round_data: Dict[str, Any] = {
            "round": round_idx, "type": round_type,
            "findings_count": len(findings),
            "findings": round_findings_detail,
            "novel_this_round": novel_this_round,
            "registry_total": len(registry.entries),
            "open_crit_high": registry.open_crit_high_count(),
            "models_responded": list(responses.keys()),
            "elapsed_s": round(round_elapsed, 1),
            "gamma": round(gamma, 4),
            "rho": round(rho_current, 4),
            "rho_avg": round(rho_avg, 4),
            "verification": verification_stats,
            "sk_pipeline": sk_stats,
            "stall_detector": stall_result,
            "shadow_cells": shadow_cell_data,
            "cross_model_diversity": cross_model_diversity,
        }
        result["rounds"].append(round_data)

        # ── HIL review gate (13 April 2026, agreed scope refinement) ──
        # In monolithic mode: pause after every round.
        # In burst mode: pause only at phase transitions (handled below).
        # The operator reviews findings with CC, fixes issues, and resumes.
        if cfg.hil_review and not (burst_plan and burst_state):
            _log(f"\n  ═══ HIL REVIEW GATE — Round {round_idx} complete ═══")
            _log(f"  Findings this round: {len(findings)}, novel: {novel_this_round}")
            _log(f"  Registry total: {len(registry.entries)}")
            _log(f"  γ={gamma:.4f}, ρ={rho_current:.4f}, ρ_avg={rho_avg:.4f}")
            _log(f"  Checkpoint saved. Resume with --resume --hil-review")
            _log(f"  ═══════════════════════════════════════════════════\n")
            # Pre-launch review fix: save checkpoint AGAIN here to capture
            # immune pipeline results and convergence stats that occurred
            # after the initial persist() call (which only has raw findings).
            brain._save_checkpoint()
            # Write partial report for review
            result["hil_paused_at_round"] = round_idx
            result["hil_status"] = "paused_for_review"
            partial_report = logs_dir / f"{cfg.experiment_name}_hil_r{round_idx:02d}.json"
            partial_report.write_text(
                json.dumps(result, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            sys.exit(42)

        # ── Phase transition or final convergence ──
        phase_transition = False

        # D1: churn-based phase transition in burst mode.
        # Sustained churn (3+ consecutive rounds) with gamma >= 0.45 signals
        # topic exhaustion — trigger phase transition without waiting for
        # convergence gate or stall detector.
        churn_transition = False
        if (burst_plan and burst_state and not burst_state["integration_done"]
                and consecutive_churn_rounds >= 3 and gamma >= 0.45
                and not converged and not stall_result.get("terminate")):
            churn_transition = True
            _log(f"  D1 churn transition: {consecutive_churn_rounds} consecutive "
                 f"churn rounds, gamma={gamma:.3f} — phase exhausted")

        if converged or stall_result.get("terminate") or churn_transition:
            reason_str = conv_reason if converged else stall_result.get("reason", "stall")
            if churn_transition:
                reason_str = (f"churn x{consecutive_churn_rounds}, gamma={gamma:.3f}")
            reason_type = ("CONVERGED" if converged
                           else "CHURN_EXHAUSTED" if churn_transition
                           else "STALL_CONVERGED")

            if burst_plan and burst_state and not burst_state["integration_done"]:
                # Burst mode: transition to next phase or integration
                phase_idx = burst_state["phase_idx"]
                current_phase_name = burst_plan.phases[phase_idx].name

                # Record phase findings
                burst_state["phase_findings"][current_phase_name] = (
                    build_findings_summary(registry.to_dict(), current_phase_name)
                )

                # ── HIL review gate at burst-mode phase boundary ──
                if cfg.hil_review:
                    _log(f"\n  ═══ HIL REVIEW GATE — Phase '{current_phase_name}' "
                         f"converged ({reason_type}) ═══")
                    _log(f"  Findings summary:\n{burst_state['phase_findings'][current_phase_name]}")
                    _log(f"  Registry total: {len(registry.entries)}")
                    remaining = len(burst_plan.phases) - phase_idx - 1
                    _log(f"  Phases remaining: {remaining} + integration")
                    _log(f"  Checkpoint saved. Resume with --resume --hil-review")
                    _log(f"  ═══════════════════════════════════════════════════\n")
                    result["hil_paused_at_round"] = round_idx
                    result["hil_paused_at_phase"] = current_phase_name
                    result["hil_status"] = "paused_for_review"
                    partial_report = logs_dir / f"{cfg.experiment_name}_hil_phase_{phase_idx}.json"
                    partial_report.write_text(
                        json.dumps(result, indent=2, ensure_ascii=False, default=str),
                        encoding="utf-8",
                    )
                    sys.exit(42)

                if phase_idx + 1 < len(burst_plan.phases):
                    # Transition to next phase
                    next_idx = phase_idx + 1
                    next_phase = burst_plan.phases[next_idx]
                    burst_state["phase_idx"] = next_idx
                    burst_state["phase_round_offset"] = round_idx + 1

                    _log(f"\n  Phase {phase_idx} ({current_phase_name}) "
                         f"{reason_type} at round {round_idx}")
                    _log(f"  Transitioning to Phase {next_idx}: {next_phase.name}")

                    # Build prior findings summary for cross-phase awareness
                    prior_summary = "\n".join(
                        burst_state["phase_findings"].values())

                    full_code = build_phase_code(
                        next_phase, str(target_rel),
                        burst_plan.signatures, prior_summary)
                    base_prompt = _build_prompt(
                        full_code,
                        f"{target_rel} Phase {next_idx}: {next_phase.name}")

                    # Rebase convergence thresholds for new phase
                    overrides = phase_convergence_overrides(round_idx + 1)
                    cfg = replace(cfg, **overrides)

                    # Reset per-phase convergence state
                    gate_history.clear()
                    stall_history.clear()
                    novelty_counts.clear()
                    raw_counts.clear()
                    rho_history.clear()
                    gamma_history.clear()
                    open_ch_history.clear()
                    consecutive_churn_rounds = 0
                    extended = False

                    phase_transition = True
                    _log(f"  Phase {next_idx} starts at round {round_idx + 1}")

                elif not burst_state["integration_started"]:
                    # All phases done — start integration round
                    burst_state["integration_started"] = True
                    burst_state["phase_round_offset"] = round_idx + 1

                    _log(f"\n  Phase {phase_idx} ({current_phase_name}) "
                         f"{reason_type} at round {round_idx}")
                    _log("  All phases converged — starting integration round")

                    all_findings = "\n".join(
                        burst_state["phase_findings"].values())
                    full_code = build_integration_code(
                        target_text, str(target_rel), all_findings,
                        burst_state["context_signatures"])
                    base_prompt = _build_prompt(
                        full_code, f"{target_rel} Integration")

                    # Tight integration convergence
                    overrides = integration_convergence_overrides(
                        round_idx + 1)
                    cfg = replace(cfg, **overrides)

                    gate_history.clear()
                    stall_history.clear()
                    novelty_counts.clear()
                    raw_counts.clear()
                    rho_history.clear()
                    gamma_history.clear()
                    open_ch_history.clear()
                    extended = False

                    phase_transition = True
                    _log(f"  Integration starts at round {round_idx + 1}")

                else:
                    # Integration converged — done
                    burst_state["integration_done"] = True
                    _log(f"\n  INTEGRATION {reason_type} at round {round_idx}")
                    result["converged_at"] = round_idx
                    result["convergence_reason"] = f"BURST_{reason_type}"
                    result["burst_phases"] = len(burst_plan.phases)
                    break
            else:
                # Non-burst mode or integration done: final convergence
                _log(f"\n  {reason_type} at round {round_idx}: {reason_str}")
                result["converged_at"] = round_idx
                result["convergence_reason"] = reason_str
                break

        if not phase_transition:
            # Budget extension (only in non-burst or during integration)
            if (not burst_plan or (burst_state and
                    burst_state.get("integration_started"))) and \
                    round_idx == cfg.max_rounds - 1 and not extended:
                gamma_prev = (gamma_history[-2]
                              if len(gamma_history) >= 2 else 0.0)
                should_extend, ext_reason = _check_budget_extension(
                    round_idx, registry, gamma, gamma_prev)
                if should_extend:
                    effective_max = cfg.extension_cap
                    extended = True
                    _log(f"\n  BUDGET EXTENDED to {cfg.extension_cap}: "
                         f"{ext_reason}")
                    result["budget_extended"] = True

            # Extension stall
            if (extended and round_idx > cfg.max_rounds and
                    len(result["rounds"]) >= 2):
                prev = result["rounds"][-2]
                if (round_data.get("rho_avg", 1) <= prev.get("rho_avg", 0)
                        and round_data.get("open_crit_high", 0) >=
                        prev.get("open_crit_high", 0)):
                    _log("  Extension not improving. Terminating.")
                    result["converged_at"] = round_idx
                    result["convergence_reason"] = "EXTENSION_STALLED"
                    break

    # Finalise
    final_round = len(brain.state.all_findings) - 1
    for canonical_id, entry in list(registry.entries.items()):
        if entry["status"] in ("OPEN", "CONTESTED"):
            registry.resolve(canonical_id, "UNCONFIRMED", final_round)

    _save_fingerprints(observed_fingerprints, cfg.experiment_name)
    signal = brain.signal_complete()

    total_elapsed = time.monotonic() - experiment_start
    total_findings = sum(len(rnd) for rnd in brain.state.all_findings)

    result["total_findings"] = total_findings
    result["total_rounds"] = len(brain.state.all_findings)
    result["total_elapsed_s"] = round(total_elapsed, 1)
    result["end_time"] = datetime.now(timezone.utc).isoformat()
    result["gamma_history"] = [round(g, 4) for g in gamma_history]
    result["registry"] = registry.to_dict()
    result["hil_flags"] = _itc_hil_flags[:]

    # Save report
    report_path = logs_dir / f"{cfg.experiment_name}_report.json"
    report_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    _log(f"\n{'=' * 60}")
    _log(f"EXPERIMENT {cfg.experiment_name} — {len(brain.state.all_findings)} ROUNDS COMPLETE")
    _log(f"  Total findings: {total_findings}")
    _log(f"  Registry: {len(registry.entries)} canonical entries")
    _log(f"  gamma final: {gamma_history[-1]:.3f}" if gamma_history else "  gamma: N/A")
    _log(f"  Elapsed: {total_elapsed:.0f}s")
    _log(f"  Report: {report_path}")
    _log(f"{'=' * 60}")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="CDSFL parameterised reference runner (Exp 37+, Bench Run 2)",
    )
    sub = p.add_subparsers(dest="command")

    # preflight
    sub.add_parser("preflight", help="Test model connectivity")

    # run
    run_p = sub.add_parser("run", help="Run an experiment")
    run_p.add_argument("--test-article",
                       help="Path to the file under review (required unless --config provides it)")
    run_p.add_argument("--context", nargs="*", default=[],
                       help="Paths to read-only context files")
    run_p.add_argument("--topology", default="star", choices=["star", "relay"])
    run_p.add_argument("--relay-mode", default="directed",
                       choices=["directed", "conversational", "findings"])
    run_p.add_argument("--pattern", default="fff")
    run_p.add_argument("--max-rounds", type=int, default=21)
    run_p.add_argument("--extension-cap", type=int, default=24)
    run_p.add_argument("--wall-clock-cap", type=int, default=28800,
                       help="Wall clock limit in seconds")
    run_p.add_argument("--earliest-stop", type=int, default=12)
    run_p.add_argument("--models", nargs="+",
                       default=["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"])
    run_p.add_argument("--experiment-name", default="")
    run_p.add_argument("--domain", default="software")
    run_p.add_argument("--resume", action="store_true")
    run_p.add_argument("--rho-threshold", type=float, default=0.25)
    run_p.add_argument("--rho-rolling-window", type=int, default=3)
    run_p.add_argument("--consecutive-rounds", type=int, default=2)
    run_p.add_argument("--config", help="JSON config file (overrides CLI args)")
    run_p.add_argument("--burst-mode", default=None,
                       choices=["auto", "on", "off"],
                       help="Burst decomposition: auto (fingerprint-driven), "
                            "on (always), off (monolithic)")
    run_p.add_argument("--hil-review", action="store_true",
                       help="HIL review gate: pause after each round/phase, "
                            "save checkpoint, exit 42. Resume with --resume.")

    return p


def main():
    source_env()
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    exp_config = load_default_config()
    cdsfl_path = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
    cdsfl_text = cdsfl_path.read_text(encoding="utf-8")
    # Operational directive — R_k(i) self-assessment equation and working protocol.
    # Models MUST compute R_k on their own output (§3, §6). Without this, models
    # produce qualitative findings — not metacognitive self-assessment. Exp 37
    # demonstrated 88-100% R_k adoption across all 5 models with this directive;
    # zero adoption without it. The equation inside the models' reasoning is the
    # contribution — external scoring alone is just calculation.
    _operational_path = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
    if _operational_path.exists():
        cdsfl_text += "\n\n" + _operational_path.read_text(encoding="utf-8")

    if args.command == "preflight":
        cfg = RunnerConfig(models=["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"])
        ok = run_preflight(exp_config, cdsfl_text, cfg)
        sys.exit(0 if ok else 1)

    # Build config from CLI args or JSON
    if getattr(args, "config", None):
        cfg = RunnerConfig.from_json(args.config)
        # CLI args override JSON for explicitly-provided values
        if args.test_article:
            cfg.test_article = args.test_article
        if args.resume:
            cfg.resume = True
        if getattr(args, "burst_mode", None) is not None:
            cfg.burst_mode = args.burst_mode
        if getattr(args, "hil_review", False):
            cfg.hil_review = True
    else:
        if not args.test_article:
            parser.error("--test-article is required when --config is not provided")
        cfg = RunnerConfig(
            test_article=args.test_article,
            context_files=args.context or [],
            topology=args.topology,
            relay_mode=args.relay_mode,
            pattern=args.pattern,
            max_rounds=args.max_rounds,
            extension_cap=args.extension_cap,
            wall_clock_cap_s=args.wall_clock_cap,
            earliest_stop_round=args.earliest_stop,
            models=args.models,
            experiment_name=args.experiment_name,
            domain=args.domain,
            resume=args.resume,
            rho_threshold=args.rho_threshold,
            rho_rolling_window=args.rho_rolling_window,
            consecutive_rounds_required=args.consecutive_rounds,
            burst_mode=args.burst_mode or "auto",
            hil_review=getattr(args, "hil_review", False),
        )

    if args.pattern not in INTERACTION_PATTERN_PRESETS:
        available = ", ".join(sorted(INTERACTION_PATTERN_PRESETS))
        print(f"Unknown pattern: {args.pattern!r}. Available: {available}",
              file=sys.stderr)
        sys.exit(1)

    if not cfg.resume:
        ok = run_preflight(exp_config, cdsfl_text, cfg)
        if not ok:
            _log("\nPREFLIGHT FAILED. Aborting.")
            sys.exit(1)
        _log(f"\nPreflight passed. Starting in 5s...")
        time.sleep(5)
    else:
        _log(f"\nRESUME mode — skipping preflight")

    result = run_experiment(exp_config, cdsfl_text, cfg)

    if result.get("terminated"):
        _log(f"\nExperiment terminated: {result['terminated']}")
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
