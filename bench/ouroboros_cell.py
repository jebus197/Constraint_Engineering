"""CDSFL Ouroboros Cell (O1) — Self-referential pipeline observer.

The ouroboros cell is a new immune cell type that observes the pipeline's
own behaviour, looking for patterns that individual cells cannot detect:
systemic bias, correlated false positives, declining verification quality,
and emergent pathologies.

Two modes (from biological analogy):

- **Macrophage mode**: Active hunting. Scans pipeline output for anomalies
  (verdict clusters, severity distribution shifts, tool-output correlations).
  Would eventually propose interventions (future: active mode).

- **Microglia mode**: Self-referential. Monitors whether the pipeline's own
  assumptions still hold (e.g., are findings truly independent across models?
  Is the similarity function producing sensible clusters?).

CRITICAL: O1 runs in SHADOW mode for Exp 39. It observes and logs but
NEVER modifies pipeline state or verdicts. Promotion to active mode
requires: precision threshold + novelty yield threshold + explicit HIL
approval.

Evidence capture uses VerificationChain: every observation is signed as
{content, R_k_score, pass_count, falsification_debt} per the L1/L2/L3
architecture (L1 = signing/provenance, L2 = correctness/falsification,
L3 = HIL arbitration).

Audit logging is exception-based: only anomalies are highlighted for HIL
review, not routine observations (prevents cognitive overload, per Gemini
confer finding 12 April 2026).

Created: 12 April 2026 (Phase 7 — O1 Shadow Prototype).
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

logger = logging.getLogger("cdsfl.ouroboros")


class OuroborosMode(enum.Enum):
    """Operating mode for the ouroboros cell."""
    MACROPHAGE = "macrophage"  # Active hunting for pipeline anomalies
    MICROGLIA = "microglia"    # Self-referential pipeline health checks


@dataclass
class OuroborosObservation:
    """A single observation from the ouroboros cell.

    Observations are always advisory — they flag potential issues
    but never override pipeline decisions.
    """
    observation_id: str
    mode: OuroborosMode
    category: str  # e.g. "verdict_cluster", "severity_shift", "correlation"
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
class OuroborosSummary:
    """Summary of O1 cell observations for a pipeline invocation."""
    observations: List[OuroborosObservation] = field(default_factory=list)
    anomaly_count: int = 0
    mode: OuroborosMode = OuroborosMode.MACROPHAGE
    pipeline_modified: bool = False  # MUST always be False in shadow mode

    @property
    def anomalies(self) -> List[OuroborosObservation]:
        return [o for o in self.observations if o.is_anomaly]


class OuroborosCell:
    """O1 cell: self-referential pipeline observer.

    Shadow mode only for Exp 39. Observes pipeline output and logs
    anomalies without modifying pipeline state.

    Example::

        o1 = OuroborosCell(mode=OuroborosMode.MACROPHAGE)
        summary = o1.observe(verdicts, triaged, timings)
        for anomaly in summary.anomalies:
            print(f"ANOMALY: {anomaly.description}")
    """

    # Anomaly thresholds
    VERDICT_CLUSTER_THRESHOLD: float = 0.8  # >80% same verdict = cluster
    SEVERITY_SHIFT_THRESHOLD: float = 0.3   # >0.3 shift between rounds
    TIMING_SPIKE_FACTOR: float = 3.0        # >3x median = spike
    MIN_FINDINGS_FOR_ANALYSIS: int = 3      # Need at least 3 findings

    def __init__(
        self,
        mode: OuroborosMode = OuroborosMode.MACROPHAGE,
        shadow: bool = True,
    ) -> None:
        self.mode = mode
        self.shadow = shadow  # MUST be True for Exp 39
        self._observation_counter = 0
        self._round_history: List[Dict[str, Any]] = []

    def _next_id(self) -> str:
        self._observation_counter += 1
        return f"o1_{self._observation_counter:04d}"

    def observe(
        self,
        verdicts: List[Any],
        triaged: Optional[List[Any]] = None,
        timings: Optional[Dict[str, float]] = None,
        prior_observations: Optional[List[OuroborosObservation]] = None,
    ) -> OuroborosSummary:
        """Run O1 observation on pipeline output.

        SHADOW MODE: observes and logs only, never modifies pipeline state.

        Args:
            verdicts: CellVerdict objects from pipeline Stage 2.
            triaged: TriagedFinding objects from Stage 1 (optional).
            timings: Pipeline stage timings (optional).
            prior_observations: Observations from prior rounds (optional).

        Returns:
            OuroborosSummary with all observations.
        """
        summary = OuroborosSummary(mode=self.mode)

        if self.mode == OuroborosMode.MACROPHAGE:
            self._macrophage_observe(verdicts, triaged, timings, summary)
        else:
            self._microglia_observe(verdicts, triaged, timings, summary)

        summary.anomaly_count = len(summary.anomalies)

        # Exception-based audit: only log anomalies (prevents HIL overload)
        if summary.anomaly_count > 0:
            logger.warning(
                "O1 [%s] detected %d anomalies (shadow mode — advisory only)",
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
        })

        # CRITICAL: shadow mode guarantee
        summary.pipeline_modified = False
        return summary

    def _macrophage_observe(
        self,
        verdicts: List[Any],
        triaged: Optional[List[Any]],
        timings: Optional[Dict[str, float]],
        summary: OuroborosSummary,
    ) -> None:
        """Macrophage mode: hunt for pipeline anomalies."""

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
                obs = OuroborosObservation(
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
                obs = OuroborosObservation(
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

        # 3. Timing spikes: is any stage disproportionately slow?
        if timings and len(timings) >= 2:
            values = [v for v in timings.values() if v > 0]
            if values:
                median_t = sorted(values)[len(values) // 2]
                for stage, t in timings.items():
                    if t > median_t * self.TIMING_SPIKE_FACTOR and median_t > 0.1:
                        obs = OuroborosObservation(
                            observation_id=self._next_id(),
                            mode=self.mode,
                            category="timing_spike",
                            description=(
                                f"Stage '{stage}' took {t:.2f}s "
                                f"({t/median_t:.1f}x median {median_t:.2f}s)"
                            ),
                            severity=min(1.0, t / (median_t * 10)),
                            evidence={"stage": stage, "time": t, "median": median_t},
                            is_anomaly=t > median_t * self.TIMING_SPIKE_FACTOR * 2,
                        )
                        summary.observations.append(obs)

    def _microglia_observe(
        self,
        verdicts: List[Any],
        triaged: Optional[List[Any]],
        timings: Optional[Dict[str, float]],
        summary: OuroborosSummary,
    ) -> None:
        """Microglia mode: self-referential pipeline health checks."""

        if len(verdicts) < self.MIN_FINDINGS_FOR_ANALYSIS:
            return

        # 1. Tool diversity: are verdicts all coming from one tool?
        tools_used: Dict[str, int] = {}
        for v in verdicts:
            tool = getattr(v, "tool_used", "unknown")
            tools_used[tool] = tools_used.get(tool, 0) + 1

        if len(tools_used) == 1 and len(verdicts) > 5:
            tool_name = list(tools_used.keys())[0]
            obs = OuroborosObservation(
                observation_id=self._next_id(),
                mode=self.mode,
                category="tool_monoculture",
                description=(
                    f"All {len(verdicts)} verdicts from single tool '{tool_name}' "
                    f"— verification diversity compromised"
                ),
                severity=0.7,
                evidence={"tool": tool_name, "count": len(verdicts)},
                is_anomaly=True,
            )
            summary.observations.append(obs)

        # 2. Round-over-round stability: is O1 finding the same anomalies?
        if len(self._round_history) >= 3:
            recent = self._round_history[-3:]
            all_had_anomalies = all(r["anomaly_count"] > 0 for r in recent)
            if all_had_anomalies:
                obs = OuroborosObservation(
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

        # 3. Verdict-to-triage consistency: do verdicts match claim types?
        if triaged:
            claim_types = set()
            for tf in triaged:
                ct = getattr(tf, "claim_type", None)
                if ct is not None:
                    claim_types.add(getattr(ct, "value", str(ct)))

            tool_types = set(tools_used.keys())
            # Flag if mathematical claims exist but no sympy/z3 used
            math_claims = any("math" in ct.lower() for ct in claim_types)
            math_tools = any(t in tool_types for t in ("sympy", "z3"))
            if math_claims and not math_tools and len(verdicts) > 0:
                obs = OuroborosObservation(
                    observation_id=self._next_id(),
                    mode=self.mode,
                    category="tool_claim_mismatch",
                    description=(
                        "Mathematical claims present but no SymPy/z3 verdicts — "
                        "verification may not be grounded"
                    ),
                    severity=0.6,
                    evidence={
                        "claim_types": list(claim_types),
                        "tools_used": list(tool_types),
                    },
                    is_anomaly=True,
                )
                summary.observations.append(obs)

    def sign_observation(
        self,
        observation: OuroborosObservation,
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
                artifact_type="ouroboros_observation",
                payload=observation.to_dict(),
                recorded_by=f"o1_{self.mode.value}",
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
