"""CDSFL Evidence Layer — Semantic Query Interface for the Verification Chain.

This module sits between the raw VerificationChain (cryptographic primitive)
and any consumer (UX, CLI, export tools). It provides:

1. Entity-indexed queries: look up records by experiment, model, round,
   finding, or artifact type — without knowing about Merkle trees.
2. Provenance traces: "show me the full lifecycle of finding C0042" as an
   ordered sequence of events with inclusion proofs.
3. Cross-referencing: link a finding record to the policy that was active,
   the health scan from that round, and the verdicts it received.
4. Evidence bundles: self-contained exportable proof packages for external
   audit, verifiable against a published epoch root.
5. Chain management: load, verify, and query chains from experiment
   directories without touching the crypto directly.

The evidence layer never modifies the chain. It builds a read-only index
on load, queries against that index, and generates proofs by delegating
to the VerificationChain. The chain remains the sole source of truth.

Usage::

    store = EvidenceStore.from_experiment_dir("bench/logs/exp33_endocrine_20260405T110345Z")
    store.verify()  # check chain integrity

    # Query by entity
    records = store.query(model="Gemini", round_idx=5)
    records = store.query(artifact_type="experiment_report")
    records = store.query(finding_id="C0042")

    # Provenance trace
    trace = store.trace_finding("C0042")

    # Evidence bundle for external audit
    bundle = store.export_bundle(record_indices=[12, 45, 67])

    # Summary
    print(store.summary())
"""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from bench.verification_chain import (
    VerificationChain,
    Verifier,
    rfc9162_merkle_root,
    _digest_bytes,
)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class EvidenceRecord:
    """A single record from the chain with its index and decoded metadata.

    Wraps the raw chain record dict with typed access to common fields.
    """
    index: int
    artifact_type: str
    recorded_by: str
    timestamp_utc: str
    storage_mode: str
    payload_hash: str
    metadata: Dict[str, Any]
    chain_hash: str
    # Only present for full_payload records
    payload: Optional[Any] = None
    # Extracted entity references (populated by indexer)
    experiment: str = ""
    model: str = ""
    round_idx: int = -1
    finding_ids: List[str] = field(default_factory=list)

    @classmethod
    def from_chain_record(cls, index: int, record: dict) -> "EvidenceRecord":
        """Build an EvidenceRecord from a raw VerificationChain record."""
        body = record["sealed_body"]
        meta = body.get("metadata") or {}

        er = cls(
            index=index,
            artifact_type=body["artifact_type"],
            recorded_by=body["recorded_by"],
            timestamp_utc=body["timestamp_utc"],
            storage_mode=body["storage_mode"],
            payload_hash=body["payload_hash"],
            metadata=meta,
            chain_hash=record["chain_hash"],
            payload=body.get("payload"),
        )

        # Extract entity references from metadata
        er.experiment = meta.get("experiment", "")
        er.model = meta.get("model", "")
        er.round_idx = meta.get("round", -1)

        # Extract finding IDs from payload and metadata
        ids: set = set()
        if er.payload is not None:
            ids.update(_extract_finding_ids(er.payload))
        if meta:
            ids.update(_extract_finding_ids(meta))
        if ids:
            er.finding_ids = sorted(ids)

        return er


@dataclass
class ProvenanceEvent:
    """One event in a finding's provenance trace."""
    record_index: int
    event_type: str     # "submitted", "confirmed", "challenged", "health_scan", "policy"
    timestamp_utc: str
    model: str
    round_idx: int
    detail: str         # human-readable description
    chain_hash: str     # for verification


@dataclass
class EvidenceBundle:
    """Self-contained proof package for external audit.

    Contains the records, their inclusion proofs, and the Merkle root
    they verify against. An external party can verify this bundle
    without access to the full chain.
    """
    experiment: str
    created_at: str
    merkle_root: str
    records: List[Dict[str, Any]]
    inclusion_proofs: List[Dict[str, Any]]
    chain_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_version": "1.0",
            "experiment": self.experiment,
            "created_at": self.created_at,
            "merkle_root": self.merkle_root,
            "record_count": len(self.records),
            "records": self.records,
            "inclusion_proofs": self.inclusion_proofs,
            "chain_metadata": self.chain_metadata,
        }

    def save_json(self, path: str) -> None:
        """Save the bundle to a JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class StoreSummary:
    """Summary statistics for an EvidenceStore."""
    experiment: str
    total_records: int
    records_by_type: Dict[str, int]
    records_by_model: Dict[str, int]
    rounds_covered: List[int]
    chain_verified: Optional[bool]
    epoch_count: int
    merkle_root: str


# ---------------------------------------------------------------------------
# Finding ID extraction
# ---------------------------------------------------------------------------

_FINDING_ID_RE = re.compile(r"\bC\d{4}\b")


def _extract_finding_ids(obj: Any) -> List[str]:
    """Recursively extract finding IDs (C0001-C9999) from a payload.

    Searches dict keys AND values, strings, and list/tuple elements.
    Handles non-dict payloads (strings, lists) directly.
    """
    ids: Set[str] = set()
    if isinstance(obj, str):
        ids.update(_FINDING_ID_RE.findall(obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str):
                ids.update(_FINDING_ID_RE.findall(k))
            ids.update(_extract_finding_ids(v))
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            ids.update(_extract_finding_ids(v))
    return sorted(ids)


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

class _EvidenceIndex:
    """In-memory index over chain records for fast lookups.

    Built once on load, never modified. Rebuilding from the chain
    is the only way to update the index — this guarantees the index
    cannot diverge from the chain.
    """

    def __init__(self, records: List[EvidenceRecord]):
        self._records = records
        # Indexes: each maps a key to a list of record indices
        self.by_experiment: Dict[str, List[int]] = defaultdict(list)
        self.by_model: Dict[str, List[int]] = defaultdict(list)
        self.by_round: Dict[int, List[int]] = defaultdict(list)
        self.by_type: Dict[str, List[int]] = defaultdict(list)
        self.by_finding: Dict[str, List[int]] = defaultdict(list)

        for rec in records:
            i = rec.index
            if rec.experiment:
                self.by_experiment[rec.experiment].append(i)
            if rec.model:
                self.by_model[rec.model].append(i)
            if rec.round_idx >= 0:
                self.by_round[rec.round_idx].append(i)
            self.by_type[rec.artifact_type].append(i)
            for fid in rec.finding_ids:
                self.by_finding[fid].append(i)

    def search(
        self,
        experiment: Optional[str] = None,
        model: Optional[str] = None,
        round_idx: Optional[int] = None,
        artifact_type: Optional[str] = None,
        finding_id: Optional[str] = None,
    ) -> List[int]:
        """Return record indices matching ALL specified criteria (AND logic)."""
        candidates: Optional[Set[int]] = None

        def _intersect(index_map: dict, key: Any) -> None:
            nonlocal candidates
            if key is not None and key in index_map:
                matches = set(index_map[key])
                candidates = matches if candidates is None else candidates & matches
            elif key is not None:
                candidates = set()

        _intersect(self.by_experiment, experiment)
        _intersect(self.by_model, model)
        _intersect(self.by_round, round_idx)
        _intersect(self.by_type, artifact_type)
        _intersect(self.by_finding, finding_id)

        if candidates is None:
            # No filters applied — return all
            return list(range(len(self._records)))

        return sorted(candidates)


# ---------------------------------------------------------------------------
# EvidenceStore
# ---------------------------------------------------------------------------

class EvidenceStore:
    """Semantic query interface over a VerificationChain.

    Load from an experiment directory or an existing chain file.
    All queries are read-only — the chain is never modified.
    """

    def __init__(self, chain: VerificationChain, experiment_name: str = ""):
        self._chain = chain
        self._experiment = experiment_name
        # Build typed records and index
        raw_records = chain.records  # deep copy from chain
        self._records = [
            EvidenceRecord.from_chain_record(i, r)
            for i, r in enumerate(raw_records)
        ]
        self._index = _EvidenceIndex(self._records)
        self._verified: Optional[bool] = None
        self._verified_with_verifier: bool = False
        self._verify_message: str = ""

    @classmethod
    def from_chain_file(cls, path: str) -> "EvidenceStore":
        """Load from an existing chain JSON file."""
        chain = VerificationChain.load_json(path)
        # Infer experiment name from directory or filename
        p = Path(path)
        experiment = p.parent.name if p.parent.name != "." else p.stem
        return cls(chain, experiment)

    @classmethod
    def from_experiment_dir(cls, dir_path: str) -> "EvidenceStore":
        """Load from an experiment directory containing experiment_chain.json."""
        d = Path(dir_path)
        chain_file = d / "experiment_chain.json"
        if not chain_file.exists():
            raise FileNotFoundError(
                f"No experiment_chain.json in {dir_path}. "
                f"Run seal_experiment_logs.py first."
            )
        return cls.from_chain_file(str(chain_file))

    # -- Verification -------------------------------------------------------

    def verify(self, verifier: Optional[Verifier] = None) -> Tuple[bool, str]:
        """Verify the underlying chain integrity.

        Caches by verifier presence: a cached structural-only result is
        discarded if a verifier is supplied (C0008/C0174/C0181).
        """
        needs_verify = (
            self._verified is None
            or (verifier is not None and self._verified_with_verifier is False)
        )
        if needs_verify:
            self._verified, self._verify_message = self._chain.verify_chain(
                verifier=verifier
            )
            if verifier is not None:
                self._verified_with_verifier = True
        return self._verified, self._verify_message

    @property
    def is_verified(self) -> Optional[bool]:
        """True/False if verify() has been called, None otherwise."""
        return self._verified

    # -- Query --------------------------------------------------------------

    def query(
        self,
        experiment: Optional[str] = None,
        model: Optional[str] = None,
        round_idx: Optional[int] = None,
        artifact_type: Optional[str] = None,
        finding_id: Optional[str] = None,
    ) -> List[EvidenceRecord]:
        """Query records by entity. All criteria are AND-combined.

        Args:
            experiment: Filter by experiment name.
            model: Filter by model ID/label.
            round_idx: Filter by round number.
            artifact_type: Filter by artifact type string.
            finding_id: Filter by finding ID (e.g. "C0042").

        Returns:
            List of matching EvidenceRecord objects, ordered by index.
        """
        indices = self._index.search(
            experiment=experiment,
            model=model,
            round_idx=round_idx,
            artifact_type=artifact_type,
            finding_id=finding_id,
        )
        return [self._records[i] for i in indices]

    def get_record(self, index: int) -> EvidenceRecord:
        """Get a single record by index."""
        if not (0 <= index < len(self._records)):
            raise IndexError(f"Record index {index} out of range [0, {len(self._records)})")
        return self._records[index]

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def models(self) -> List[str]:
        """All model IDs found in the chain."""
        return sorted(self._index.by_model.keys())

    @property
    def rounds(self) -> List[int]:
        """All round indices found in the chain."""
        return sorted(self._index.by_round.keys())

    @property
    def artifact_types(self) -> List[str]:
        """All artifact types found in the chain."""
        return sorted(self._index.by_type.keys())

    @property
    def finding_ids(self) -> List[str]:
        """All finding IDs referenced in the chain."""
        return sorted(self._index.by_finding.keys())

    # -- Provenance ---------------------------------------------------------

    def trace_finding(self, finding_id: str) -> List[ProvenanceEvent]:
        """Build a chronological provenance trace for a finding.

        Returns every event related to this finding ID, ordered by
        timestamp, with event types inferred from the artifact type
        and payload content.
        """
        indices = self._index.by_finding.get(finding_id, [])
        if not indices:
            return []

        events: List[ProvenanceEvent] = []
        for i in sorted(indices):
            rec = self._records[i]
            event_type = _classify_event(rec, finding_id)
            detail = _describe_event(rec, finding_id)
            events.append(ProvenanceEvent(
                record_index=i,
                event_type=event_type,
                timestamp_utc=rec.timestamp_utc,
                model=rec.model,
                round_idx=rec.round_idx,
                detail=detail,
                chain_hash=rec.chain_hash,
            ))

        return events

    # -- Evidence bundles ---------------------------------------------------

    def export_bundle(
        self,
        record_indices: Optional[List[int]] = None,
        finding_id: Optional[str] = None,
        model: Optional[str] = None,
        round_idx: Optional[int] = None,
        experiment: Optional[str] = None,
    ) -> EvidenceBundle:
        """Export a self-contained evidence bundle with inclusion proofs.

        Specify records by index, or by entity filter. The bundle includes
        the raw chain records, their Merkle inclusion proofs, and the epoch
        root — enough for independent verification.

        Args:
            record_indices: Explicit record indices to include.
            finding_id: Include all records referencing this finding.
            model: Include all records from this model.
            round_idx: Include all records from this round.
            experiment: Include all records from this experiment.

        Returns:
            EvidenceBundle that can be saved and verified externally.
        """
        if record_indices is not None:
            indices = sorted(set(record_indices))
        else:
            indices = self._index.search(
                experiment=experiment,
                finding_id=finding_id,
                model=model,
                round_idx=round_idx,
            )

        if not indices:
            raise ValueError("No records match the specified criteria")

        from bench.verification_chain import _utc_now

        raw_records = self._chain.records
        records_out = []
        proofs_out = []

        for i in indices:
            if not (0 <= i < len(raw_records)):
                raise IndexError(f"Record index {i} out of range")
            records_out.append(raw_records[i])
            proof = self._chain.build_inclusion_proof(i)
            proofs_out.append(proof)

        # Compute Merkle root from all records — must match the tree
        # used by build_inclusion_proof(), which always covers all records.
        # Using the epoch root would mismatch when records exist after
        # the last seal (C0001/C0005/C0010/C0017).
        epochs = self._chain.epochs
        leaves = [_digest_bytes(r["chain_hash"]) for r in raw_records]
        merkle_root = "sha256:" + rfc9162_merkle_root(leaves).hex()

        return EvidenceBundle(
            experiment=self._experiment,
            created_at=_utc_now(),
            merkle_root=merkle_root,
            records=records_out,
            inclusion_proofs=proofs_out,
            chain_metadata={
                "total_records": len(raw_records),
                "epoch_count": len(epochs),
                "bundle_indices": indices,
            },
        )

    def verify_bundle(self, bundle: EvidenceBundle) -> Tuple[bool, List[str]]:
        """Verify an evidence bundle's inclusion proofs against its Merkle root.

        Returns (all_valid, list_of_error_messages).
        """
        errors: List[str] = []

        # C0009/C0173/C0182: check list lengths match before iterating
        if len(bundle.records) != len(bundle.inclusion_proofs):
            errors.append(
                f"Length mismatch: {len(bundle.records)} records vs "
                f"{len(bundle.inclusion_proofs)} proofs"
            )
            return False, errors

        for i, (record, proof) in enumerate(
            zip(bundle.records, bundle.inclusion_proofs)
        ):
            # C0034/C0060/C0106: verify chain_hash matches before proof check
            record_hash = record.get("chain_hash", "")
            proof_hash = proof.get("chain_hash", "")
            if record_hash and proof_hash and record_hash != proof_hash:
                errors.append(
                    f"Record {i}: chain_hash mismatch "
                    f"(record={record_hash[:16]}... vs proof={proof_hash[:16]}...)"
                )
                continue

            valid = self._chain.verify_inclusion_proof(proof, bundle.merkle_root)
            if not valid:
                errors.append(
                    f"Record {i} (seq={record.get('sealed_body', {}).get('seq', '?')}): "
                    f"inclusion proof invalid"
                )
        return len(errors) == 0, errors

    # -- Summary ------------------------------------------------------------

    def summary(self) -> StoreSummary:
        """Generate summary statistics for the store."""
        by_type: Dict[str, int] = {}
        by_model: Dict[str, int] = {}
        for rec in self._records:
            by_type[rec.artifact_type] = by_type.get(rec.artifact_type, 0) + 1
            if rec.model:
                by_model[rec.model] = by_model.get(rec.model, 0) + 1

        epochs = self._chain.epochs
        # Compute from all records (consistent with export_bundle/proofs)
        raw_records = self._chain.records
        if raw_records:
            leaves = [_digest_bytes(r["chain_hash"]) for r in raw_records]
            merkle_root = "sha256:" + rfc9162_merkle_root(leaves).hex()
        else:
            merkle_root = ""

        return StoreSummary(
            experiment=self._experiment,
            total_records=len(self._records),
            records_by_type=by_type,
            records_by_model=by_model,
            rounds_covered=self.rounds,
            chain_verified=self._verified,
            epoch_count=len(epochs),
            merkle_root=merkle_root,
        )


# ---------------------------------------------------------------------------
# Event classification helpers
# ---------------------------------------------------------------------------

def _classify_event(rec: EvidenceRecord, finding_id: str) -> str:
    """Classify a record's relationship to a finding."""
    atype = rec.artifact_type

    if atype == "model_chat_log":
        # Check if this is a submission or a verdict
        if rec.payload and isinstance(rec.payload, dict):
            payload_str = json.dumps(rec.payload)
            if f"CONFIRM {finding_id}" in payload_str:
                return "confirmed"
            if f"CHALLENGE {finding_id}" in payload_str:
                return "challenged"
            if f"EXTEND {finding_id}" in payload_str:
                return "extended"
            if f"MERGE {finding_id}" in payload_str:
                return "merged"
        return "submitted"

    if atype == "experiment_report":
        return "reported"

    if atype == "experiment_checkpoint":
        return "checkpoint"

    if atype == "health_scan":
        return "health_scan"

    if atype == "policy_snapshot":
        return "policy"

    if atype == "verdict":
        return "verdict"

    return "referenced"


def _describe_event(rec: EvidenceRecord, finding_id: str) -> str:
    """Generate a human-readable description of an event."""
    event_type = _classify_event(rec, finding_id)

    if event_type == "submitted":
        return f"Finding {finding_id} submitted by {rec.model} in round {rec.round_idx}"
    if event_type == "confirmed":
        return f"Finding {finding_id} confirmed by {rec.model} in round {rec.round_idx}"
    if event_type == "challenged":
        return f"Finding {finding_id} challenged by {rec.model} in round {rec.round_idx}"
    if event_type == "extended":
        return f"Finding {finding_id} extended by {rec.model} in round {rec.round_idx}"
    if event_type == "merged":
        return f"Finding {finding_id} merge-linked by {rec.model} in round {rec.round_idx}"
    if event_type == "reported":
        return f"Finding {finding_id} included in experiment report"
    if event_type == "checkpoint":
        return f"Finding {finding_id} present in checkpoint at round {rec.round_idx}"
    if event_type == "health_scan":
        return f"Health scan at round {rec.round_idx} references {finding_id}"
    if event_type == "policy":
        return f"Policy snapshot at round {rec.round_idx}"

    return f"Finding {finding_id} referenced in {rec.artifact_type} record"
