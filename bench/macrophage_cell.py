"""CDSFL Macrophage Cell — Internal pipeline monitor.

The Macrophage cell is the immune pipeline's internal observer. In biology,
macrophages are patrol cells that operate inside the body, engulfing
pathogens and presenting them to other immune cells. In CDSFL, the
Macrophage watches the entire pipeline from within, detecting systemic
pathologies that individual cells cannot see.

Two detection modes:

- **Patrol mode**: Active hunting. Scans pipeline output for anomalies
  (verdict clusters, severity distribution shifts, timing spikes).

- **Self-check mode**: Self-referential. Monitors whether the pipeline's own
  assumptions still hold (e.g., are findings truly independent across models?
  Is source diversity maintained? Are methods matched to claim types?).

CRITICAL: The Macrophage is ADVISORY ONLY. It NEVER modifies pipeline state
or verdicts. It has NO external API access — strict isolation from external
systems to prevent confirmation bias.

The Macrophage has:
- Sensitivity dial (1-11 UX, 0-1 internal) controlling observation output
- Circuit breaker preventing alert flooding during systemic events
- Semantic clustering grouping identical observations by root cause

Evidence capture uses VerificationChain: every observation is signed as
{content, R_k_score, pass_count, falsification_debt} per the L1/L2/L3
architecture.

Audit logging is exception-based: only anomalies are highlighted for HIL
review, not routine observations (prevents cognitive overload).

Refactored from ouroboros_cell.py: 12 April 2026 (cell type split).
Original creation: 12 April 2026 (Phase 7 — O1 Shadow Prototype).
"""

from __future__ import annotations

import enum
import hashlib
import json
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger("cdsfl.macrophage")


class MacrophageMode(enum.Enum):
    """Operating mode for the Macrophage cell."""
    PATROL = "patrol"          # Active hunting for pipeline anomalies
    SELF_CHECK = "self_check"  # Self-referential pipeline health checks


@dataclass
class MacrophageObservation:
    """A single observation from the Macrophage cell.

    Observations are always advisory — they flag potential issues
    but never override pipeline decisions.
    """
    observation_id: str
    mode: MacrophageMode
    category: str  # e.g. "verdict_cluster", "severity_shift", "source_monoculture"
    description: str
    severity: float  # 0-1, how concerning this observation is
    evidence: Dict[str, Any] = field(default_factory=dict)
    is_anomaly: bool = False  # Only anomalies are surfaced to HIL
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Serialise to dict. Floats are stringified for VerificationChain
        cross-platform determinism (canonical_json requirement)."""
        return {
            "observation_id": self.observation_id,
            "mode": self.mode.value,
            "category": self.category,
            "description": self.description,
            "severity": str(self.severity),
            "evidence": {
                k: str(v) if isinstance(v, float) else v
                for k, v in self.evidence.items()
            },
            "is_anomaly": self.is_anomaly,
            "timestamp": str(self.timestamp),
        }


@dataclass
class MacrophageSummary:
    """Summary of Macrophage cell observations for a pipeline invocation."""
    observations: List[MacrophageObservation] = field(default_factory=list)
    anomaly_count: int = 0
    mode: MacrophageMode = MacrophageMode.PATROL
    pipeline_modified: bool = False  # MUST always be False — advisory only

    @property
    def anomalies(self) -> List[MacrophageObservation]:
        return [o for o in self.observations if o.is_anomaly]


class MacrophageCell:
    """Macrophage cell: internal pipeline monitor.

    Advisory only — observes pipeline output and logs anomalies without
    modifying pipeline state. No external API access.

    The Macrophage monitors:
    - Pipeline verdicts, triaged findings, and timing data
    - Source provenance metadata (origin tags on claims)
    - PE gate pass/fail statistics
    - Ouroboros activity metrics (external research cell)

    Example::

        macro = MacrophageCell(mode=MacrophageMode.PATROL)
        summary = macro.observe(verdicts, triaged, timings)
        for anomaly in summary.anomalies:
            print(f"ANOMALY: {anomaly.description}")
    """

    # Anomaly thresholds
    VERDICT_CLUSTER_THRESHOLD: float = 0.8  # >80% same verdict = cluster
    SEVERITY_SHIFT_THRESHOLD: float = 0.3   # >0.3 shift between rounds
    TIMING_SPIKE_FACTOR: float = 3.0        # >3x median = spike
    #: Rounds of history a stage needs before it can raise a timing alarm.
    #: CC2, 2026-08-31: with 1 prior round the "median" IS that round, and at
    #: n=2 `vals[len//2]` returns the UPPER value -- measured, a resumed cell
    #: fired at 4.2x off a single observation. Calibrated by Fable against 62
    #: real stage-rounds from 7 paid experiments: the largest genuine ratio
    #: against a stage's own prior median is 1.9x, so the 3.0 factor keeps
    #: ~1.6x headroom and fired 0 false alarms on that data.
    TIMING_MIN_HISTORY: int = 3
    MIN_FINDINGS_FOR_ANALYSIS: int = 3      # Need at least 3 findings

    def __init__(
        self,
        mode: MacrophageMode = MacrophageMode.PATROL,
        shadow: bool = True,
    ) -> None:
        self.mode = mode
        self.shadow = shadow  # MUST be True for Exp 39
        self._observation_counter = 0
        self._round_history: List[Dict[str, Any]] = []

    def _next_id(self) -> str:
        self._observation_counter += 1
        return f"macro_{self._observation_counter:04d}"

    def observe(
        self,
        verdicts: List[Any],
        triaged: Optional[List[Any]] = None,
        timings: Optional[Dict[str, float]] = None,
        prior_observations: Optional[List[MacrophageObservation]] = None,
        provenance: Optional[List[Dict[str, Any]]] = None,
        gate_stats: Optional[Dict[str, Any]] = None,
        ouroboros_metrics: Optional[Dict[str, Any]] = None,
    ) -> MacrophageSummary:
        """Run Macrophage observation on pipeline output.

        ADVISORY ONLY: observes and logs, never modifies pipeline state.

        Args:
            verdicts: CellVerdict objects from pipeline Stage 2.
            triaged: TriagedFinding objects from Stage 1 (optional).
            timings: Pipeline stage timings (optional).
            prior_observations: Observations from prior rounds (optional).
            provenance: Source provenance metadata for claims (optional).
                Each dict should contain: origin_type, source_ref,
                retrieval_query, retrieved_at, source_hash, source_diversity.
            gate_stats: PE gate pass/fail statistics (optional).
                Expected keys: total_passed, total_failed, by_origin (dict).
            ouroboros_metrics: Ouroboros cell activity metrics (optional).
                Expected keys: queries_this_round, claims_proposed,
                sources_used, diversity_score.

        Returns:
            MacrophageSummary with all observations.
        """
        summary = MacrophageSummary(mode=self.mode)

        if self.mode == MacrophageMode.PATROL:
            self._patrol_observe(verdicts, triaged, timings, summary)
        else:
            self._self_check_observe(verdicts, triaged, timings, summary)

        # Provenance monitoring (both modes)
        if provenance:
            self._check_provenance(provenance, summary)

        # PE gate monitoring (both modes)
        if gate_stats:
            self._check_gate_stats(gate_stats, summary)

        # Ouroboros activity monitoring (both modes)
        if ouroboros_metrics:
            self._check_ouroboros_metrics(ouroboros_metrics, summary)

        summary.anomaly_count = len(summary.anomalies)

        # Exception-based audit: only log anomalies (prevents HIL overload)
        if summary.anomaly_count > 0:
            logger.warning(
                "Macrophage [%s] detected %d anomalies (advisory only)",
                self.mode.value, summary.anomaly_count,
            )
            for anomaly in summary.anomalies:
                logger.warning(
                    "  ANOMALY %s [%s]: %s (sev=%.2f)",
                    anomaly.observation_id, anomaly.category,
                    anomaly.description, anomaly.severity,
                )

        # Store round history for cross-round analysis
        self._round_history.append({
            "observation_count": len(summary.observations),
            "anomaly_count": summary.anomaly_count,
            "verdict_count": len(verdicts),
            "timestamp": time.time(),
            # Retained so `_stage_baselines` can compare a stage against its
            # OWN prior rounds rather than against the round's cross-stage
            # median, which is a category error on a bimodal population.
            "timings": dict(timings or {}),
        })

        # CRITICAL: advisory-only guarantee
        summary.pipeline_modified = False
        return summary

    def _patrol_observe(
        self,
        verdicts: List[Any],
        triaged: Optional[List[Any]],
        timings: Optional[Dict[str, float]],
        summary: MacrophageSummary,
    ) -> None:
        """Patrol mode: hunt for pipeline anomalies."""

        if len(verdicts) < self.MIN_FINDINGS_FOR_ANALYSIS:
            return

        # 1. Verdict clustering: are too many verdicts the same?
        verdict_counts: Dict[str, int] = {}
        for v in verdicts:
            vstr = getattr(v, "verdict", str(v))
            verdict_counts[vstr] = verdict_counts.get(vstr, 0) + 1

        total = len(verdicts)
        for verdict_type, count in verdict_counts.items():
            ratio = count / total
            if ratio > self.VERDICT_CLUSTER_THRESHOLD:
                obs = MacrophageObservation(
                    observation_id=self._next_id(),
                    mode=self.mode,
                    category="verdict_cluster",
                    description=(
                        f"{ratio:.0%} of verdicts are {verdict_type} "
                        f"({count}/{total}) — possible systemic bias"
                    ),
                    severity=min(1.0, ratio),
                    evidence={"verdict_type": verdict_type, "count": count, "total": total},
                    is_anomaly=True,
                )
                summary.observations.append(obs)

        # 2. Severity distribution: is severity concentrated?
        severities = []
        for v in verdicts:
            sev = getattr(v, "confidence", None)
            if sev is not None:
                severities.append(sev)

        if len(severities) >= self.MIN_FINDINGS_FOR_ANALYSIS:
            mean_sev = sum(severities) / len(severities)
            variance = sum((s - mean_sev) ** 2 for s in severities) / len(severities)
            if variance < 0.01 and mean_sev > 0.5:
                obs = MacrophageObservation(
                    observation_id=self._next_id(),
                    mode=self.mode,
                    category="severity_concentration",
                    description=(
                        f"Confidence variance very low ({variance:.4f}) with mean "
                        f"{mean_sev:.2f} — models may be over-confident uniformly"
                    ),
                    severity=0.6,
                    evidence={"mean": mean_sev, "variance": variance, "n": len(severities)},
                    is_anomaly=variance < 0.005,
                )
                summary.observations.append(obs)

        # 3. Timing spikes: is a stage disproportionately slow FOR ITSELF?
        #
        # AGAINST ITS OWN HISTORY, not the round's cross-stage median
        # (2026-08-31). The cross-stage median is a CATEGORY ERROR: stage costs
        # here are bimodal -- bookkeeping stages take microseconds, model-calling
        # stages take tens of seconds -- so one median across both compares a
        # model call against a dictionary update.
        #
        # MEASURED, and NOT a simulation artefact: across exp45, 46, 47, 48, 49,
        # 53 and 55 -- real, paid experiments since 2026-07-27 -- this produced
        # 92 timing alarms. 92 of 92 had ratios above 1000x (up to 526,986x) and
        # 92 of 92 carried severity exactly 1.00: ONE distinct value in the whole
        # dataset, so severity carried no information at all.
        #
        # The 2026-07-27 repair removed a `median_t > 0.1` guard that had made
        # the check structurally BLIND and replaced it with `t > 0.5`, which made
        # it structurally NOISY. Neither is useful. A stage against its own prior
        # median is the statistic the question actually asks.
        #
        # ADDITIVE, not a removal: the check keeps its factor, its floor, its
        # severity formula and its output shape. Only the baseline changes, from
        # a meaningless one to a meaningful one.
        #
        # No new storage: `_round_history` already holds a dict per round. A
        # stage with no history raises no alarm, because an anomaly cannot be
        # called on a sample of one. The cell is a module-level singleton and
        # does not survive checkpoint-resume, so history restarts afterwards and
        # the first post-resume round is silent for that stage.
        if timings:
            baselines = self._stage_baselines()
            counts = self._stage_sample_counts()
            for stage, t in timings.items():
                median_t = baselines.get(stage)
                if (median_t
                        and counts.get(stage, 0) >= self.TIMING_MIN_HISTORY
                        and t > median_t * self.TIMING_SPIKE_FACTOR and t > 0.5):
                    obs = MacrophageObservation(
                        observation_id=self._next_id(),
                        mode=self.mode,
                        category="timing_spike",
                        description=(
                            f"Stage '{stage}' took {t:.2f}s "
                            f"({t/median_t:.1f}x its own median {median_t:.2f}s)"
                        ),
                        severity=min(1.0, t / (median_t * 10)),
                        evidence={"stage": stage, "time": t, "median": median_t,
                                  "baseline": "own_prior_rounds"},
                        is_anomaly=t > median_t * self.TIMING_SPIKE_FACTOR * 2,
                    )
                    summary.observations.append(obs)

    def _stage_sample_counts(self) -> Dict[str, int]:
        """How many prior rounds each stage has been seen in."""
        out: Dict[str, int] = {}
        for rec in self._round_history:
            for stage, t in (rec.get("timings") or {}).items():
                try:
                    if float(t) > 0:
                        out[stage] = out.get(stage, 0) + 1
                except (TypeError, ValueError):
                    continue
        return out

    def rehydrate_timings(self, rounds: List[Dict[str, Any]]) -> int:
        """Restore stage-timing history after a checkpoint resume.

        The cell is a module-level singleton and does not survive a resume, so
        without this every stage restarts at zero history and the detector is
        silent for TIMING_MIN_HISTORY rounds. Fable, 2026-08-31, also noted the
        baseline change removed the only raw-timing record the project had --
        the old alarms WERE that record -- so timings are now persisted per
        round and can be read back.
        """
        n = 0
        for rec in rounds or []:
            t = rec.get("timings") or rec.get("stage_timings")
            if t:
                self._round_history.append({"timings": dict(t)})
                n += 1
        return n

    def _stage_baselines(self) -> Dict[str, float]:
        """Median duration per stage across this cell's PRIOR rounds.

        Empty for a stage seen for the first time, so no alarm is raised on a
        sample of one. Uses only rounds already recorded, never the current one,
        so a slow round cannot raise its own baseline and mask itself.
        """
        per: Dict[str, List[float]] = {}
        for rec in self._round_history:
            for stage, t in (rec.get("timings") or {}).items():
                try:
                    v = float(t)
                except (TypeError, ValueError):
                    continue
                if v > 0:
                    per.setdefault(stage, []).append(v)
        out: Dict[str, float] = {}
        for stage, vals in per.items():
            vals.sort()
            out[stage] = vals[len(vals) // 2]
        return out

    def _self_check_observe(
        self,
        verdicts: List[Any],
        triaged: Optional[List[Any]],
        timings: Optional[Dict[str, float]],
        summary: MacrophageSummary,
    ) -> None:
        """Self-check mode: self-referential pipeline health checks."""

        if len(verdicts) < self.MIN_FINDINGS_FOR_ANALYSIS:
            return

        # 1. Source diversity: are verdicts all coming from one source/tool?
        # Renamed from tool_monoculture for domain-agnostic use.
        sources_used: Dict[str, int] = {}
        for v in verdicts:
            source = getattr(v, "tool_used", "unknown")
            sources_used[source] = sources_used.get(source, 0) + 1

        if len(sources_used) == 1 and len(verdicts) > 5:
            source_name = list(sources_used.keys())[0]
            obs = MacrophageObservation(
                observation_id=self._next_id(),
                mode=self.mode,
                category="source_monoculture",
                description=(
                    f"All {len(verdicts)} verdicts from single source '{source_name}' "
                    f"— verification diversity compromised"
                ),
                severity=0.7,
                evidence={"source": source_name, "count": len(verdicts)},
                is_anomaly=True,
            )
            summary.observations.append(obs)

        # 2. Round-over-round stability: persistent anomalies across rounds
        if len(self._round_history) >= 3:
            recent = self._round_history[-3:]
            all_had_anomalies = all(r["anomaly_count"] > 0 for r in recent)
            if all_had_anomalies:
                obs = MacrophageObservation(
                    observation_id=self._next_id(),
                    mode=self.mode,
                    category="persistent_anomaly",
                    description=(
                        "Anomalies detected in 3+ consecutive rounds — "
                        "possible systemic issue not being addressed"
                    ),
                    severity=0.8,
                    evidence={
                        "rounds_with_anomalies": len(recent),
                        "anomaly_counts": [r["anomaly_count"] for r in recent],
                    },
                    is_anomaly=True,
                )
                summary.observations.append(obs)

        # 3. Method-claim consistency: do verification methods match claim types?
        # Renamed from tool_claim_mismatch for domain-agnostic use.
        if triaged:
            claim_types = set()
            for tf in triaged:
                ct = getattr(tf, "claim_type", None)
                if ct is not None:
                    claim_types.add(getattr(ct, "value", str(ct)))

            source_types = set(sources_used.keys())
            # Flag if mathematical claims exist but no sympy/z3 used
            math_claims = any("math" in ct.lower() for ct in claim_types)
            math_sources = any(t in source_types for t in ("sympy", "z3"))
            if math_claims and not math_sources and len(verdicts) > 0:
                obs = MacrophageObservation(
                    observation_id=self._next_id(),
                    mode=self.mode,
                    category="method_claim_mismatch",
                    description=(
                        "Mathematical claims present but no SymPy/z3 verdicts — "
                        "verification may not be grounded"
                    ),
                    severity=0.6,
                    evidence={
                        "claim_types": list(claim_types),
                        "sources_used": list(source_types),
                    },
                    is_anomaly=True,
                )
                summary.observations.append(obs)

    def _check_provenance(
        self,
        provenance: List[Dict[str, Any]],
        summary: MacrophageSummary,
    ) -> None:
        """Check source provenance metadata for Ouroboros-origin claims."""
        if not provenance:
            return

        # Source diversity check
        sources = [p.get("source_ref", "") for p in provenance if p.get("source_ref")]
        if len(sources) >= 3:
            unique_sources = set(sources)
            diversity = len(unique_sources) / len(sources)
            if diversity <= 0.5:
                obs = MacrophageObservation(
                    observation_id=self._next_id(),
                    mode=self.mode,
                    category="source_monoculture",
                    description=(
                        f"Ouroboros source diversity low ({diversity:.0%}) — "
                        f"{len(unique_sources)} unique sources from {len(sources)} claims"
                    ),
                    severity=0.7,
                    evidence={
                        "unique_sources": len(unique_sources),
                        "total_claims": len(sources),
                        "diversity": diversity,
                    },
                    is_anomaly=True,
                )
                summary.observations.append(obs)

        # Missing provenance fields
        required_fields = {"origin_type", "source_ref", "source_hash"}
        for p in provenance:
            missing = required_fields - set(p.keys())
            if missing:
                obs = MacrophageObservation(
                    observation_id=self._next_id(),
                    mode=self.mode,
                    category="provenance_incomplete",
                    description=(
                        f"External claim missing provenance fields: {', '.join(sorted(missing))}"
                    ),
                    severity=0.5,
                    evidence={"missing_fields": list(sorted(missing))},
                    is_anomaly=True,
                )
                summary.observations.append(obs)

    def _check_gate_stats(
        self,
        gate_stats: Dict[str, Any],
        summary: MacrophageSummary,
    ) -> None:
        """Monitor PE gate pass/fail statistics for pathologies."""
        total_passed = gate_stats.get("total_passed", 0)
        total_failed = gate_stats.get("total_failed", 0)
        total = total_passed + total_failed

        if total == 0:
            return

        # Zero rejection rate = immune deficiency
        if total_failed == 0 and total >= 5:
            obs = MacrophageObservation(
                observation_id=self._next_id(),
                mode=self.mode,
                category="immune_deficiency",
                description=(
                    f"PE gates passed all {total} claims with 0% rejection — "
                    f"gates may not be functioning"
                ),
                severity=0.9,
                evidence={"total_passed": total_passed, "total_failed": total_failed},
                is_anomaly=True,
            )
            summary.observations.append(obs)

        # Check by-origin stats for Ouroboros-specific acceptance rates
        by_origin = gate_stats.get("by_origin", {})
        ouroboros_stats = by_origin.get("external_ouroboros", {})
        if ouroboros_stats:
            o_passed = ouroboros_stats.get("passed", 0)
            o_failed = ouroboros_stats.get("failed", 0)
            o_total = o_passed + o_failed
            if o_total >= 3 and o_failed == 0:
                obs = MacrophageObservation(
                    observation_id=self._next_id(),
                    mode=self.mode,
                    category="immune_deficiency",
                    description=(
                        f"Ouroboros-origin claims have 0% rejection rate "
                        f"({o_passed}/{o_total} passed) — immune deficiency for external claims"
                    ),
                    severity=0.9,
                    evidence={
                        "ouroboros_passed": o_passed,
                        "ouroboros_total": o_total,
                    },
                    is_anomaly=True,
                )
                summary.observations.append(obs)

    def _check_ouroboros_metrics(
        self,
        ouroboros_metrics: Dict[str, Any],
        summary: MacrophageSummary,
    ) -> None:
        """Monitor Ouroboros cell activity for pathologies."""
        diversity = ouroboros_metrics.get("diversity_score", 1.0)
        if diversity < 0.3:
            obs = MacrophageObservation(
                observation_id=self._next_id(),
                mode=self.mode,
                category="source_monoculture",
                description=(
                    f"Ouroboros source diversity score {diversity:.2f} "
                    f"(below 0.3 threshold) — research may be too narrow"
                ),
                severity=0.6,
                evidence={"diversity_score": diversity},
                is_anomaly=True,
            )
            summary.observations.append(obs)

    def sign_observation(
        self,
        observation: MacrophageObservation,
        chain: Any,  # VerificationChain
    ) -> Optional[dict]:
        """Sign an observation into the verification chain.

        L1 (provenance): the signed record proves this observation was made
        at this time by this cell. L2 (correctness) and L3 (HIL) operate
        on the signed records downstream.

        Returns the chain record, or None if signing fails.
        """
        try:
            record = chain.append_record(
                artifact_type="macrophage_observation",
                payload=observation.to_dict(),
                recorded_by=f"macrophage_{self.mode.value}",
                metadata={
                    "shadow": self.shadow,
                    "is_anomaly": observation.is_anomaly,
                },
            )
            return record
        except Exception as exc:
            logger.warning("Failed to sign observation %s: %s",
                          observation.observation_id, exc)
            return None
