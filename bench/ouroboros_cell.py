"""CDSFL Ouroboros Cell (O1) — External research and self-improvement.

In mythology, the ouroboros is the snake consuming its own tail, representing
cyclical self-reference and self-improvement. In CDSFL, the Ouroboros gathers
external research from sources like arXiv and Semantic Scholar, and can gather
data from other CDSFL-linked network systems. It processes what it finds and
presents candidate claims back to the pipeline for verification by other cells.

Key design decisions (confer 12 April 2026, Gemini 3.1 Pro + Codex 5.3):

1. **Between-round placement**: Ouroboros runs AFTER each round completes,
   not during verification. Stage 2 assumes the batch already exists.
   Inserting a cell that creates new claims during verification is
   architecturally confused. One-round lag is acceptable because the
   Macrophage monitors in real time for emergencies.

2. **Disjoint evidence paths**: If the Ouroboros proposes a finding based
   on a paper, the B-Cell must verify it through a completely different
   method (computation, execution, or a strictly different data source).

3. **Provenance**: All external-origin claims carry explicit provenance
   tags: origin_type, source_ref, retrieval_query, retrieved_at,
   source_hash, source_diversity. Mandatory falsification_debt: high.

CRITICAL: O1 runs in SHADOW mode for Exp 39. It logs what it WOULD have
injected into the pipeline but does NOT actually inject claims. Promotion
to active mode requires explicit HIL approval.

Hard caps for Exp 39: max 3 queries per round, max 2 candidate claims.

Refactored from ouroboros_cell.py: 12 April 2026 (cell type split).
The original ouroboros_cell.py was renamed to macrophage_cell.py (internal
monitor). This file is the NEW external research cell.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("cdsfl.ouroboros")


@dataclass
class ProvenancePacket:
    """Provenance metadata for an external-origin claim.

    Every claim the Ouroboros produces must carry a complete provenance
    packet. The Macrophage monitors these for source monoculture and
    missing fields.
    """
    origin_type: str = "external_ouroboros"  # Always external for O1
    source_ref: str = ""       # Paper DOI, URL, or identifier
    retrieval_query: str = ""  # The search query that found this source
    retrieved_at: str = ""     # ISO 8601 timestamp of retrieval
    source_hash: str = ""      # SHA-256 of source content
    source_diversity: float = 0.0  # Diversity metric (0-1)

    def to_dict(self) -> dict:
        return {
            "origin_type": self.origin_type,
            "source_ref": self.source_ref,
            "retrieval_query": self.retrieval_query,
            "retrieved_at": self.retrieved_at,
            "source_hash": self.source_hash,
            "source_diversity": str(self.source_diversity),
        }


@dataclass
class OuroborosCandidateClaim:
    """A candidate claim produced by the Ouroboros for pipeline injection.

    In shadow mode, these are logged but NOT injected. In active mode,
    they enter the normal intake and go through standard triage and
    verification gates like any other finding.
    """
    claim_id: str
    description: str
    provenance: ProvenancePacket
    relevance_score: float = 0.0   # How relevant to observed anomalies (0-1)
    falsification_debt: str = "high"  # External claims always start high
    round_observed: int = 0        # Which round triggered this research
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "description": self.description,
            "provenance": self.provenance.to_dict(),
            "relevance_score": str(self.relevance_score),
            "falsification_debt": self.falsification_debt,
            "round_observed": self.round_observed,
            "timestamp": str(self.timestamp),
        }


@dataclass
class OuroborosShadowLog:
    """Shadow replay log: records what the Ouroboros WOULD have done.

    For Exp 39, the Ouroboros does not inject claims. Instead, it logs
    what it noticed, what it queried, what came back, and what claims
    it would have created. This allows evaluation without pipeline risk.
    """
    round_idx: int
    anomalies_observed: List[str] = field(default_factory=list)
    queries_issued: List[Dict[str, str]] = field(default_factory=list)
    metadata_retrieved: List[Dict[str, Any]] = field(default_factory=list)
    candidate_claims: List[OuroborosCandidateClaim] = field(default_factory=list)
    would_have_injected: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "round_idx": self.round_idx,
            "anomalies_observed": self.anomalies_observed,
            "queries_issued": self.queries_issued,
            "metadata_retrieved": self.metadata_retrieved,
            "candidate_claims": [c.to_dict() for c in self.candidate_claims],
            "would_have_injected": self.would_have_injected,
            "timestamp": str(self.timestamp),
        }


class OuroborosCell:
    """O1 cell: external research and self-improvement engine.

    Runs between rounds. Observes what happened in the completed round,
    queries external sources based on anomalies, and produces candidate
    claims for the next round's normal intake.

    Shadow mode (Exp 39): logs only, no pipeline injection.

    Example::

        o1 = OuroborosCell(shadow=True)
        shadow_log = o1.run_between_rounds(
            round_idx=3,
            anomalies=["verdict_cluster detected"],
            immune_response=response,
        )
        # In shadow mode, shadow_log records what O1 would have done
    """

    # Hard caps for Exp 39
    MAX_QUERIES_PER_ROUND: int = 3
    MAX_CANDIDATE_CLAIMS: int = 2

    def __init__(
        self,
        shadow: bool = True,
        allowed_sources: Optional[List[str]] = None,
    ) -> None:
        self.shadow = shadow  # MUST be True for Exp 39
        self.allowed_sources = allowed_sources or ["arxiv", "semantic_scholar"]
        self._claim_counter = 0
        self._round_logs: List[OuroborosShadowLog] = []

    def _next_claim_id(self) -> str:
        self._claim_counter += 1
        return f"o1_claim_{self._claim_counter:04d}"

    def run_between_rounds(
        self,
        round_idx: int,
        anomalies: Optional[List[str]] = None,
        immune_response: Optional[Any] = None,
        round_findings: Optional[List[Any]] = None,
    ) -> OuroborosShadowLog:
        """Execute Ouroboros between-round research cycle.

        This is the main entry point. Called AFTER a round completes.

        Args:
            round_idx: Index of the just-completed round.
            anomalies: Anomaly descriptions from Macrophage observations.
            immune_response: The ImmuneResponse from the completed round.
            round_findings: Findings from the completed round.

        Returns:
            OuroborosShadowLog recording what O1 did (or would have done).
        """
        shadow_log = OuroborosShadowLog(round_idx=round_idx)

        # Step 1: Target selection — identify what to research based on anomalies
        targets = self._select_targets(
            anomalies or [],
            immune_response,
            round_findings,
        )
        shadow_log.anomalies_observed = targets

        if not targets:
            self._round_logs.append(shadow_log)
            return shadow_log

        # Step 2: Structured metadata fetch (mocked in shadow/Exp 39)
        queries = self._build_queries(targets)
        shadow_log.queries_issued = queries[:self.MAX_QUERIES_PER_ROUND]

        metadata = self._fetch_metadata(
            shadow_log.queries_issued,
        )
        shadow_log.metadata_retrieved = metadata

        # Step 3: Candidate claim generation
        candidates = self._generate_candidates(
            targets, metadata, round_idx,
        )
        shadow_log.candidate_claims = candidates[:self.MAX_CANDIDATE_CLAIMS]
        shadow_log.would_have_injected = len(candidates) > 0

        # In shadow mode, log only — no pipeline injection
        if shadow_log.would_have_injected:
            logger.info(
                "Ouroboros [shadow] round %d: would inject %d candidate claims "
                "(capped at %d). Queries: %d. Targets: %s",
                round_idx, len(candidates),
                self.MAX_CANDIDATE_CLAIMS,
                len(shadow_log.queries_issued),
                targets[:3],
            )

        self._round_logs.append(shadow_log)
        return shadow_log

    def _select_targets(
        self,
        anomalies: List[str],
        immune_response: Optional[Any],
        round_findings: Optional[List[Any]],
    ) -> List[str]:
        """Select research targets based on round anomalies and findings.

        Prioritises:
        1. Macrophage-flagged anomalies (direct signal)
        2. Recurring disputed findings (convergence failures)
        3. High-severity unresolved claims
        """
        targets = []

        # Macrophage anomalies are direct research triggers
        for anomaly in anomalies:
            targets.append(anomaly)

        # Check for disputed/uncertain findings
        if immune_response:
            final_verdicts = getattr(immune_response, "final_verdicts", {})
            for fid, verdict in final_verdicts.items():
                if verdict == "UNCERTAIN":
                    targets.append(f"uncertain_finding:{fid}")

        return targets[:5]  # Cap targets

    def _build_queries(
        self,
        targets: List[str],
    ) -> List[Dict[str, str]]:
        """Build structured search queries from targets."""
        queries = []
        for target in targets[:self.MAX_QUERIES_PER_ROUND]:
            # Extract search terms from the target description
            query = {
                "target": target,
                "source": self.allowed_sources[0] if self.allowed_sources else "arxiv",
                "query": self._target_to_query(target),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            queries.append(query)
        return queries

    def _target_to_query(self, target: str) -> str:
        """Convert a target description to a search query.

        For Exp 39 shadow mode, this produces the query string that
        WOULD be sent to the API. No actual API call is made.
        """
        # Strip prefixes
        if ":" in target:
            target = target.split(":", 1)[1]
        # Basic keyword extraction (sufficient for shadow mode logging)
        return target.strip()

    def _fetch_metadata(
        self,
        queries: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Fetch structured metadata from external sources.

        For Exp 39: MOCKED. Returns empty results with provenance stubs.
        Real implementation will use arXiv and Semantic Scholar APIs.
        """
        results = []
        for query in queries:
            # Shadow mode: log the query, return mock metadata
            result = {
                "query": query["query"],
                "source": query["source"],
                "status": "shadow_mock",
                "results_count": 0,
                "papers": [],
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            results.append(result)
        return results

    def _generate_candidates(
        self,
        targets: List[str],
        metadata: List[Dict[str, Any]],
        round_idx: int,
    ) -> List[OuroborosCandidateClaim]:
        """Generate candidate claims from retrieved metadata.

        For Exp 39: generates shadow candidates based on targets.
        Real implementation will parse paper metadata and extract claims.
        """
        candidates = []

        for target in targets[:self.MAX_CANDIDATE_CLAIMS]:
            provenance = ProvenancePacket(
                origin_type="external_ouroboros",
                retrieval_query=self._target_to_query(target),
                retrieved_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                source_diversity=0.0,  # No real sources in shadow mode
            )

            candidate = OuroborosCandidateClaim(
                claim_id=self._next_claim_id(),
                description=f"Shadow candidate for target: {target}",
                provenance=provenance,
                relevance_score=0.5,
                falsification_debt="high",
                round_observed=round_idx,
            )
            candidates.append(candidate)

        return candidates

    def get_activity_metrics(self) -> Dict[str, Any]:
        """Return activity metrics for Macrophage monitoring.

        The Macrophage monitors these metrics to detect Ouroboros
        pathologies (source monoculture, excessive querying, etc.).
        """
        if not self._round_logs:
            return {
                "queries_total": 0,
                "claims_proposed_total": 0,
                "rounds_active": 0,
                "diversity_score": 1.0,
            }

        total_queries = sum(len(log.queries_issued) for log in self._round_logs)
        total_claims = sum(len(log.candidate_claims) for log in self._round_logs)

        # Compute source diversity across all queries
        all_sources = []
        for log in self._round_logs:
            for q in log.queries_issued:
                all_sources.append(q.get("source", "unknown"))

        if all_sources:
            unique = len(set(all_sources))
            diversity = unique / len(all_sources)
        else:
            diversity = 1.0

        return {
            "queries_total": total_queries,
            "claims_proposed_total": total_claims,
            "rounds_active": len(self._round_logs),
            "diversity_score": diversity,
            "queries_this_round": (
                len(self._round_logs[-1].queries_issued) if self._round_logs else 0
            ),
            "claims_this_round": (
                len(self._round_logs[-1].candidate_claims) if self._round_logs else 0
            ),
        }

    def sign_shadow_log(
        self,
        shadow_log: OuroborosShadowLog,
        chain: Any,  # VerificationChain
    ) -> Optional[dict]:
        """Sign a shadow log entry into the verification chain.

        L1 (provenance): proves this research cycle was executed at this
        time by the Ouroboros. L2/L3 operate downstream.

        Returns the chain record, or None if signing fails.
        """
        try:
            record = chain.append_record(
                artifact_type="ouroboros_shadow_log",
                payload=shadow_log.to_dict(),
                recorded_by="ouroboros_o1",
                metadata={
                    "shadow": self.shadow,
                    "round_idx": shadow_log.round_idx,
                    "would_have_injected": shadow_log.would_have_injected,
                },
            )
            return record
        except Exception as exc:
            logger.warning("Failed to sign shadow log for round %d: %s",
                          shadow_log.round_idx, exc)
            return None
