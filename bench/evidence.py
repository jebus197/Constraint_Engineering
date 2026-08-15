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

import hashlib
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
        try:
            er.round_idx = int(meta.get("round", -1))
        except (ValueError, TypeError):
            er.round_idx = -1

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

_FINDING_ID_RE = re.compile(r"\b[A-Za-z]\d{3,5}\b")


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

        # Sort by timestamp for true chronological order (C0207)
        events.sort(key=lambda e: e.timestamp_utc)
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


# ---------------------------------------------------------------------------
# Survived-falsification ledger (2026-08-08)
# ---------------------------------------------------------------------------
#
# WHY THIS EXISTS
# ---------------
# Before this ledger the harness held no positive record that a claim had been
# TESTED AND STOOD. Every artefact a run produced recorded something going
# WRONG — a finding, an escalation, a HIL item. A run in which nothing was
# wrong therefore produced an ABSENCE, and an absence is unusable as a result.
# "No findings" is indistinguishable from all of:
#     * the panel read the document and found it sound;
#     * dispatch failed and no model answered;
#     * the target file was never loaded;
#     * the falsifier gate was switched off.
# The zero-plant control — a target document with no planted defects, where
# every claim is true — is exactly the experiment whose correct outcome is that
# absence. Its positive result was, until this ledger, unrecordable.
#
# NAMING, DELIBERATE AND NOT TO BE "CORRECTED" BACK
# -------------------------------------------------
# This is NOT called a "confirmed true" or "verified true" ledger, and no field
# in it uses those words. A falsifier that fails to fire licenses the statement
# "survived that test" and nothing stronger. Naming the artefact after the
# stronger statement would hand a reviewer a worse problem than the one the
# ledger solves, because the name would then travel into summaries, abstracts
# and headline counts where the caveat does not follow it.
#
# WHAT IT MUST NEVER DO
# ---------------------
# It must not touch convergence. It records; it does not gate. Nothing here
# returns a blocker, a severity aggregate, or any quantity the two-sided gate
# (gamma_critical >= threshold AND K consecutive zero-new-critical rounds)
# consumes. See test_verified_true_ledger.py, which pins that isolation.
#
# HOW IT FAILS
# ------------
# Loudly, on the principle that the expensive defect in this harness is the one
# that renders as a confident success. Specifically:
#   * A ledger that was never fed reports NEVER_INVOKED, never a serene "0
#     claims survived" — those two states are opposite in meaning and must
#     never share a rendering.
#   * A verdict string it does not recognise raises, because the only source of
#     verdicts is reverify_falsifier's five literals; anything else is
#     miswiring, and a silently dropped verdict corrupts the denominator.
#   * A survival whose claim text is missing is still RECORDED (dropping it
#     would under-count silently) but carries a sentinel and raises an alarm,
#     so it confesses rather than presenting as a well-formed row.

# Verdict literals returned by bench.falsifier_verify.reverify_falsifier. This
# ledger recognises these and only these; see _VERDICT_MEANING below.
VERDICT_CONFIRMED = "CONFIRMED"
VERDICT_REFUTED = "REFUTED"
VERDICT_ERROR = "ERROR"
VERDICT_UNTOOLABLE = "UNTOOLABLE"
# The fifth literal. NOT a verdict on the claim: the falsifier reached for the
# material that decides the answer (a key, a manifest, a protected path), so it
# was refused and never ran. Duplicated from
# bench.falsifier_verify.INTEGRITY_VIOLATION to keep this module a leaf; pinned
# against drift by test_verified_true_ledger.py.
#
# ADDED 2026-08-08 AFTER AN ADVERSARIAL REPRODUCTION. It was omitted, and the
# omission was not cosmetic: record() raises on an unrecognised verdict, so the
# wiring this module prescribes — record() called on the result of every
# reverify_falsifier — would have raised ValueError inside the round loop the
# first time the integrity gate fired, killing the run at exactly the moment a
# falsifier tried to read the scoring key. The raise also misdiagnosed it,
# naming a wiring fault that did not exist.
VERDICT_INTEGRITY_VIOLATION = "INTEGRITY_VIOLATION"

KNOWN_VERDICTS = frozenset({
    VERDICT_CONFIRMED, VERDICT_REFUTED, VERDICT_ERROR, VERDICT_UNTOOLABLE,
    VERDICT_INTEGRITY_VIOLATION,
})

# Which verdicts are evidence of what. The mapping is deliberately asymmetric
# and mirrors reverify_falsifier's own asymmetry.
_VERDICT_MEANING = {
    VERDICT_REFUTED: (
        "the falsifier ran to a clean exit and did NOT demonstrate the alleged "
        "defect — the claim survived this test"
    ),
    VERDICT_CONFIRMED: (
        "the falsifier demonstrated the alleged defect — the claim did NOT "
        "survive; no survival entry is written"
    ),
    VERDICT_ERROR: (
        "the falsifier could not be trusted to decide (timeout, harness fault, "
        "or a broken falsifier) — evidence in NEITHER direction"
    ),
    VERDICT_UNTOOLABLE: (
        "no falsifier was supplied — nothing was tested, so nothing is recorded"
    ),
    VERDICT_INTEGRITY_VIOLATION: (
        "the falsifier reached for the material that decides the answer, so it "
        "was refused and never ran — a MACHINERY fault, evidence in NEITHER "
        "direction, and never a survival"
    ),
}

# The sentence that must travel with every count taken from this ledger. It is
# emitted inside report_section() rather than left in a docstring precisely so
# that it cannot be stripped by a consumer reading the JSON.
SURVIVAL_MEANING = (
    "A falsifier that ran to a clean exit is evidence that the claim survived "
    "THAT test, written by THAT model, on THAT round. It is NOT proof the claim "
    "is true. Absence of a demonstration is not a demonstration of absence: the "
    "test may have been too weak to find a real defect, may have probed the "
    "wrong property, or may have been broken in a way that still exits cleanly. "
    "The only reading an entry licenses is 'not refuted by the tests put to it "
    "so far'. Any reading of the form 'verified true', 'confirmed correct', "
    "'validated' or 'proven' overstates the evidence and misreports the result."
)

# Measured, not assumed. Recorded here because it is the single most likely way
# a reader would over-read this ledger.
WEAK_EVIDENCE_CAVEAT = (
    "Survivals on CRITICAL-severity findings are the weak case and must not be "
    "counted as equivalent to the rest. The Exp 42 audit measured 2 of 3 "
    "clean-exit verdicts on critical findings to be FALSE — the falsifier "
    "cleared a defect that was real (C0028, C0040). This is why the runner "
    "escalates a clean-exit critical to a human rather than dropping it. A "
    "critical-severity row here is a prompt for human review, not a clearance."
)

# The symmetric hazard, named because this ledger CANNOT detect it.
#
# A falsifier can be valid, runnable code and still test nothing at all. The
# discrimination control (founder ruling 2026-08-08) catches the case where such
# a falsifier FIRES for a reason unrelated to the claim, wrongly closing a
# finding. The mirror case is this ledger's blind spot: a falsifier that goes
# QUIET for a reason unrelated to the claim exits cleanly and writes a survival
# row here, and nothing in this module can tell that apart from a genuine
# survival. "It did not fire" and "it never tested anything" are indistinguishable
# from the exit status alone.
#
# This is why every row retains its full falsifier text and digest: a human, or
# a later discrimination pass, can inspect what was actually probed. The ledger
# does not apply the discrimination control itself and must not be read as
# though it had.
DISCRIMINATION_LIMITATION = (
    "This ledger records that a falsifier did not fire. It does NOT establish "
    "that the falsifier tested the claim at all — a falsifier that probes the "
    "wrong property, or nothing whatever, also exits cleanly and is recorded "
    "here identically to a sound one. The full falsifier text and its digest "
    "are retained on every row so that this can be checked by inspection. Rows "
    "are a starting point for review, not a substitute for it."
)

# Kept in step with reference_runner_v2.CRITICAL_SEVERITY_THRESHOLD. Duplicated
# rather than imported so this module stays a leaf (it imports only
# verification_chain); the duplication is pinned against drift by
# test_verified_true_ledger.py::test_critical_threshold_matches_the_runner.
LEDGER_CRITICAL_SEVERITY = 0.7

# Written into a row whose claim text was missing, so the row confesses instead
# of rendering as a well-formed survival with an empty description.
MISSING_CLAIM_SENTINEL = "(NO CLAIM TEXT SUPPLIED — MALFORMED ROW, DO NOT COUNT AS CLEAN)"


@dataclass
class SurvivedTest:
    """One record of a claim surviving one falsification attempt.

    An instance asserts exactly this and nothing more: on ``round_idx``, the
    falsifier in ``falsifier_code`` — written by ``authored_by`` — was
    re-executed independently by the runner against the claim in
    ``claim_under_test``, and it did not fire.

    It does NOT assert that the claim is true. See ``SURVIVAL_MEANING``.
    """

    finding_id: str
    claim_under_test: str
    falsifier_code: str
    authored_by: str
    runner_verdict: str
    round_idx: int
    severity: float = 0.0
    # When the ledger ROW was written — not when the falsifier ran. Named for
    # what it actually measures; a stamp that records the save rather than the
    # event is a known failure mode in this project.
    recorded_at_utc: str = ""
    # Set when a later round demonstrated the defect after all, i.e. this
    # survival was wrong. The row is never deleted: it remains historically
    # true that the falsifier of that round did not fire.
    overturned_at_round: Optional[int] = None
    # True when the claim text was missing at record time.
    malformed: bool = False

    @property
    def is_critical(self) -> bool:
        """Critical severity — the weak-evidence band. See WEAK_EVIDENCE_CAVEAT."""
        return self.severity >= LEDGER_CRITICAL_SEVERITY

    @property
    def still_standing(self) -> bool:
        """True while no later round has demonstrated the defect."""
        return self.overturned_at_round is None

    @property
    def falsifier_sha256(self) -> str:
        """Digest of the exact falsifier text that was re-executed.

        Lets a reader confirm that the falsifier quoted in a report is the one
        that actually ran, and survives a consumer truncating the code for
        display.
        """
        return "sha256:" + hashlib.sha256(
            self.falsifier_code.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "claim_under_test": self.claim_under_test,
            "falsifier_code": self.falsifier_code,
            "falsifier_sha256": self.falsifier_sha256,
            "authored_by": self.authored_by,
            "runner_verdict": self.runner_verdict,
            "round_idx": self.round_idx,
            "severity": self.severity,
            "recorded_at_utc": self.recorded_at_utc,
            "still_standing": self.still_standing,
            "overturned_at_round": self.overturned_at_round,
            "weak_evidence": self.is_critical,
            "malformed": self.malformed,
        }


class SurvivedFalsificationLedger:
    """Positive record of claims that were tested and were not refuted.

    Fed one falsifier verdict at a time via :meth:`record`. A clean exit
    (``REFUTED``) writes a row; a demonstration (``CONFIRMED``) writes none and
    overturns any earlier row for the same finding; ``ERROR``,
    ``UNTOOLABLE`` and ``INTEGRITY_VIOLATION`` write nothing and confirm
    nothing.

    The ledger counts every verdict it is shown, not only the ones that produce
    rows. That is what lets an empty ledger say WHY it is empty — "I was never
    called" and "40 falsifiers ran and all of them fired" are opposite results
    and must never render alike.

    Read :data:`SURVIVAL_MEANING` before quoting any count from this object.

    Usage::

        ledger = SurvivedFalsificationLedger(experiment="exp53_zero_plant")
        ledger.record(
            finding_id="C0042",
            claim_under_test="Section 3 states the decay constant is 0.30",
            falsifier_code="assert ...",
            authored_by="CC2-SIM",
            runner_verdict="REFUTED",
            round_idx=4,
            severity=0.8,
        )
        report["survived_falsification"] = ledger.report_section()
    """

    #: Key this section takes in the run report.
    REPORT_KEY = "survived_falsification"

    def __init__(self, experiment: str = ""):
        self._experiment = experiment
        self._entries: List[SurvivedTest] = []
        self._tally: Dict[str, int] = {v: 0 for v in sorted(KNOWN_VERDICTS)}
        # finding_id -> round of the first CONFIRMED demonstration.
        self._demonstrated: Dict[str, int] = {}
        self._malformed_count = 0

    # -- Recording ----------------------------------------------------------

    def record(
        self,
        finding_id: str,
        claim_under_test: str,
        falsifier_code: str,
        authored_by: str,
        runner_verdict: str,
        round_idx: int,
        severity: float = 0.0,
    ) -> Optional[SurvivedTest]:
        """Record one falsifier re-execution result.

        Args:
            finding_id: Canonical registry id of the allegation under test
                (e.g. "C0042"). Stable across rounds, so it is the key on which
                a later demonstration overturns an earlier survival.
            claim_under_test: What was alleged to be wrong and therefore what
                stands if the falsifier does not fire.
            falsifier_code: The exact snippet the runner re-executed.
            authored_by: The model that wrote the falsifier.
            runner_verdict: The RUNNER's independent re-execution result, one of
                CONFIRMED / REFUTED / ERROR / UNTOOLABLE /
                INTEGRITY_VIOLATION. Never the model's
                prose verdict.
            round_idx: Round on which the re-execution happened.
            severity: Finding severity, used only to mark the weak-evidence
                band (see WEAK_EVIDENCE_CAVEAT). Never aggregated into anything
                the convergence gate reads.

        Returns:
            The :class:`SurvivedTest` row on a clean exit, else ``None``.

        Raises:
            ValueError: on a verdict this ledger does not recognise, a negative
                round, a missing finding id, or a REFUTED with no falsifier
                text. Each of these can only arise from miswiring, and silently
                absorbing them would corrupt the counts this ledger exists to
                make trustworthy. Malformed MODEL output — a missing claim
                description — does NOT raise; it is recorded with a sentinel so
                a live run is never killed by a model's empty field.
        """
        verdict = (runner_verdict or "").strip().upper()
        if verdict not in KNOWN_VERDICTS:
            raise ValueError(
                f"SurvivedFalsificationLedger.record: unrecognised verdict "
                f"{runner_verdict!r} for {finding_id!r}. Expected one of "
                f"{sorted(KNOWN_VERDICTS)} — the literals returned by "
                f"bench.falsifier_verify.reverify_falsifier. An empty string "
                f"usually means a finding that the falsifier gate never "
                f"re-ran was passed in; feed the ledger only findings the "
                f"gate actually executed, or the survival rate is measured "
                f"against the wrong denominator."
            )
        if not str(finding_id or "").strip():
            raise ValueError(
                "SurvivedFalsificationLedger.record: finding_id is required — "
                "it is the key on which a later demonstration overturns an "
                "earlier survival, so an unkeyed row could never be corrected."
            )
        if not isinstance(round_idx, int) or isinstance(round_idx, bool) or round_idx < 0:
            raise ValueError(
                f"SurvivedFalsificationLedger.record: round_idx must be a "
                f"non-negative int, got {round_idx!r}."
            )

        self._tally[verdict] += 1

        # A demonstration. No survival row, and it retrospectively overturns any
        # earlier survival of the same allegation: a falsifier that cleared this
        # claim on an earlier round was wrong, and the ledger must say so rather
        # than leave a stale clean row queryable.
        if verdict == VERDICT_CONFIRMED:
            self._demonstrated.setdefault(finding_id, round_idx)
            for row in self._entries:
                if row.finding_id == finding_id and row.overturned_at_round is None:
                    row.overturned_at_round = round_idx
            return None

        # An error is not evidence in either direction, an absent falsifier
        # tested nothing, and a refused falsifier never ran at all. All three are
        # counted (so the denominator stays honest) and none writes a row or
        # confirms anything. INTEGRITY_VIOLATION belongs here and NOT with
        # REFUTED: the gate's whole point is that a refusal resolves the finding
        # in neither direction, so recording it as a survival would enter "the
        # claim stood" for a test that was never permitted to run.
        if verdict in (VERDICT_ERROR, VERDICT_UNTOOLABLE,
                       VERDICT_INTEGRITY_VIOLATION):
            return None

        # verdict == REFUTED: a clean exit. This is the survival case.
        if not (falsifier_code or "").strip():
            raise ValueError(
                f"SurvivedFalsificationLedger.record: REFUTED with no falsifier "
                f"text for {finding_id!r}. This pairing is impossible from "
                f"reverify_falsifier, which returns UNTOOLABLE when there is "
                f"nothing to run — so the arguments are crossed. Recording it "
                f"would enter 'a claim survived a test' where no test exists."
            )

        claim = (claim_under_test or "").strip()
        malformed = not claim
        if malformed:
            claim = MISSING_CLAIM_SENTINEL
            self._malformed_count += 1

        from bench.verification_chain import _utc_now

        row = SurvivedTest(
            finding_id=finding_id,
            claim_under_test=claim,
            falsifier_code=falsifier_code,
            authored_by=authored_by,
            runner_verdict=verdict,
            round_idx=round_idx,
            severity=float(severity or 0.0),
            recorded_at_utc=_utc_now(),
            malformed=malformed,
        )
        # Born overturned: the defect was already demonstrated on an earlier
        # round, so this clean exit is the known false-REFUTED shape (a broken
        # falsifier exiting 0) rather than new evidence that the claim stands.
        prior = self._demonstrated.get(finding_id)
        if prior is not None:
            row.overturned_at_round = prior
        self._entries.append(row)
        return row

    # -- Query --------------------------------------------------------------

    @property
    def entries(self) -> List[SurvivedTest]:
        """Every survival row ever written, append-only, in record order.

        Overturned rows are RETAINED: it remains historically true that the
        falsifier of that round did not fire, and deleting the row would erase
        the evidence that the harness once cleared a claim it should not have.
        """
        return list(self._entries)

    @property
    def observations(self) -> int:
        """Total falsifier verdicts shown to this ledger, of any kind.

        Zero here means the ledger was never fed — a wiring fault — and is a
        categorically different statement from "no claims survived".
        """
        return sum(self._tally.values())

    @property
    def verdict_tally(self) -> Dict[str, int]:
        return dict(self._tally)

    def standing(self) -> List[SurvivedTest]:
        """Rows not overturned by a later demonstration."""
        return [r for r in self._entries if r.still_standing]

    def overturned(self) -> List[SurvivedTest]:
        """Rows a later round contradicted — the harness cleared these wrongly."""
        return [r for r in self._entries if not r.still_standing]

    def weak_evidence(self) -> List[SurvivedTest]:
        """Standing rows at critical severity. See WEAK_EVIDENCE_CAVEAT."""
        return [r for r in self.standing() if r.is_critical]

    def malformed(self) -> List[SurvivedTest]:
        """Rows recorded with no claim text."""
        return [r for r in self._entries if r.malformed]

    def by_finding(self, finding_id: str) -> List[SurvivedTest]:
        return [r for r in self._entries if r.finding_id == finding_id]

    def by_round(self, round_idx: int) -> List[SurvivedTest]:
        return [r for r in self._entries if r.round_idx == round_idx]

    def by_model(self, authored_by: str) -> List[SurvivedTest]:
        return [r for r in self._entries if r.authored_by == authored_by]

    def distinct_claims_standing(self) -> List[str]:
        """Finding ids with at least one un-overturned survival."""
        return sorted({r.finding_id for r in self.standing()})

    # -- Reporting ----------------------------------------------------------

    def alarms(self) -> List[str]:
        """Conditions a reader must be told about, in plain words.

        Always consulted by :meth:`report_section`; empty means clean. This is
        the loud channel — anything that would otherwise render as a confident
        zero appears here as a sentence.
        """
        out: List[str] = []
        if self.observations == 0:
            out.append(
                "NEVER INVOKED: this ledger was not shown a single falsifier "
                "verdict. That is a WIRING FAULT, not a result. It does not "
                "mean no claim survived — it means nothing was measured, and "
                "no conclusion of any kind may be drawn from this section."
            )
        elif not self._entries:
            out.append(
                f"NO SURVIVALS: {self.observations} falsifier verdict(s) were "
                f"observed and none was a clean exit "
                f"(tally={dict(self._tally)}). The ledger ran; it simply has "
                f"nothing positive to record."
            )
        refused = self._tally.get(VERDICT_INTEGRITY_VIOLATION, 0)
        if refused:
            out.append(
                f"INTEGRITY VIOLATIONS: {refused} falsifier(s) were refused "
                f"before execution because they reached for the material that "
                f"decides the answer. Those claims were NOT tested and appear "
                f"nowhere in the rows below — they are neither survivals nor "
                f"demonstrations. A run containing any of these has a "
                f"compromised measurement until a human has looked at each one."
            )
        if self._malformed_count:
            out.append(
                f"MALFORMED ROWS: {self._malformed_count} survival row(s) were "
                f"recorded with no claim text and carry a sentinel. They are "
                f"counted but are not usable evidence — a survival whose claim "
                f"is unknown states nothing."
            )
        overturned = self.overturned()
        if overturned:
            out.append(
                f"OVERTURNED: {len(overturned)} survival row(s) were later "
                f"contradicted by a demonstration of the very defect the "
                f"falsifier had cleared "
                f"(findings: {sorted({r.finding_id for r in overturned})}). "
                f"Each is direct evidence that a falsifier in this run was too "
                f"weak to find a real defect, and is a reason to distrust the "
                f"remaining rows written by the same model."
            )
        weak = self.weak_evidence()
        if weak:
            out.append(
                f"WEAK EVIDENCE: {len(weak)} standing row(s) are at critical "
                f"severity. {WEAK_EVIDENCE_CAVEAT}"
            )
        return out

    def report_section(self) -> Dict[str, Any]:
        """The block a run report embeds under :attr:`REPORT_KEY`.

        Carries its own epistemics. ``meaning`` and ``not_proof_of_truth``
        travel with the numbers so a consumer reading only the JSON cannot pick
        up a count without the caveat attached to it.
        """
        standing = self.standing()
        return {
            "ledger": self.REPORT_KEY,
            "experiment": self._experiment,
            "meaning": SURVIVAL_MEANING,
            "not_proof_of_truth": True,
            "weak_evidence_caveat": WEAK_EVIDENCE_CAVEAT,
            "discrimination_limitation": DISCRIMINATION_LIMITATION,
            "verdict_semantics": dict(_VERDICT_MEANING),
            "status": "NEVER_INVOKED" if self.observations == 0 else "ACTIVE",
            "alarms": self.alarms(),
            "falsifier_verdicts_observed": self.observations,
            "verdict_tally": dict(self._tally),
            # UNITS ARE IN THE NAMES, DELIBERATELY. The runner re-runs every
            # open finding's falsifier EVERY ROUND, so one claim that survives
            # five rounds writes FIVE rows. A count of rows is therefore not a
            # count of claims, and a headline of the form "N claims survived"
            # must be taken from `standing_claims`, never from `standing_rows`.
            "rows_recorded": len(self._entries),
            "standing_rows": len(standing),
            "standing_claims": len(self.distinct_claims_standing()),
            "distinct_claims_standing": self.distinct_claims_standing(),
            "rows_note": (
                "A row is one falsifier re-execution, not one claim. Several "
                "rows may attest the same claim across rounds. Use "
                "'standing_claims' for a count of claims."
            ),
            "overturned_rows": len(self.overturned()),
            "weak_evidence_standing_rows": len(self.weak_evidence()),
            "malformed_rows": self._malformed_count,
            "rows": [r.to_dict() for r in self._entries],
        }

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return (
            f"SurvivedFalsificationLedger(experiment={self._experiment!r}, "
            f"observations={self.observations}, rows={len(self._entries)}, "
            f"standing={len(self.standing())}, "
            f"overturned={len(self.overturned())})"
        )
