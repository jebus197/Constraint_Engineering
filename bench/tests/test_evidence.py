"""Tests for the Evidence Layer (bench/evidence.py).

Tests the semantic query interface, index construction, provenance tracing,
evidence bundle export/verification, and summary generation. All tests use
synthetic chain data — no dependency on sealed experiment files.
"""

import json
import os
import tempfile

import pytest

from bench.verification_chain import VerificationChain
from bench.evidence import (
    EvidenceStore,
    EvidenceRecord,
    EvidenceBundle,
    ProvenanceEvent,
    StoreSummary,
    _EvidenceIndex,
    _extract_finding_ids,
    _classify_event,
    _describe_event,
)


# =============================================================================
# Fixtures — build a realistic synthetic chain
# =============================================================================

def _floats_to_strings(obj):
    """Convert floats to strings for chain compatibility."""
    if isinstance(obj, float):
        return f"{obj:.6g}"
    if isinstance(obj, dict):
        return {k: _floats_to_strings(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_floats_to_strings(v) for v in obj]
    return obj


def _build_test_chain() -> VerificationChain:
    """Build a chain with realistic experiment data: 3 rounds, 3 models."""
    chain = VerificationChain()

    # Round 0: three model responses with findings
    chain.append_record(
        artifact_type="model_chat_log",
        payload=_floats_to_strings({
            "response": "Found issue C0001 in endocrine.py: sandbox uses flat tmpdir",
            "findings": [{"id": "C0001", "severity": 0.8}],
        }),
        recorded_by="exp34_runner",
        metadata={"experiment": "exp34a_endocrine", "round": 0, "model": "CC2"},
        storage_mode="full_payload",
    )
    chain.append_record(
        artifact_type="model_chat_log",
        payload=_floats_to_strings({
            "response": "Found C0002: _compute_fix_verdict nets across tools",
            "findings": [{"id": "C0002", "severity": 0.7}],
        }),
        recorded_by="exp34_runner",
        metadata={"experiment": "exp34a_endocrine", "round": 0, "model": "Gemini"},
        storage_mode="full_payload",
    )
    chain.append_record(
        artifact_type="model_chat_log",
        payload=_floats_to_strings({
            "response": "Found C0001 in sandbox isolation and C0003 in pacing",
            "findings": [{"id": "C0001", "severity": 0.9}, {"id": "C0003", "severity": 0.5}],
        }),
        recorded_by="exp34_runner",
        metadata={"experiment": "exp34a_endocrine", "round": 0, "model": "DeepSeek"},
        storage_mode="full_payload",
    )

    # Round 1: verdicts and new findings
    chain.append_record(
        artifact_type="model_chat_log",
        payload=_floats_to_strings({
            "response": "CONFIRM C0001 — independently verified. CHALLENGE C0002 — not reproducible",
            "findings": [],
        }),
        recorded_by="exp34_runner",
        metadata={"experiment": "exp34a_endocrine", "round": 1, "model": "CC2"},
        storage_mode="full_payload",
    )
    chain.append_record(
        artifact_type="model_chat_log",
        payload=_floats_to_strings({
            "response": "CONFIRM C0001 — confirmed. Found C0004 in health_trend",
            "findings": [{"id": "C0004", "severity": 0.6}],
        }),
        recorded_by="exp34_runner",
        metadata={"experiment": "exp34a_endocrine", "round": 1, "model": "Gemini"},
        storage_mode="full_payload",
    )

    # Round 2: convergence
    chain.append_record(
        artifact_type="model_chat_log",
        payload=_floats_to_strings({
            "response": "CONFIRM C0003 — pacing signal confirmed. EXTEND C0001 — additional impact found",
            "findings": [],
        }),
        recorded_by="exp34_runner",
        metadata={"experiment": "exp34a_endocrine", "round": 2, "model": "DeepSeek"},
        storage_mode="full_payload",
    )

    # Checkpoint and report
    chain.append_record(
        artifact_type="experiment_checkpoint",
        payload=_floats_to_strings({
            "round": 2,
            "findings_total": 4,
            "confirmed": ["C0001", "C0003"],
            "unconfirmed": ["C0002", "C0004"],
        }),
        recorded_by="exp34_runner",
        metadata={"experiment": "exp34a_endocrine"},
        storage_mode="full_payload",
    )
    chain.append_record(
        artifact_type="experiment_report",
        payload=_floats_to_strings({
            "experiment": "exp34a_endocrine",
            "total_findings": 4,
            "confirmed": ["C0001", "C0003"],
            "gamma": "0.72",
            "convergence": "partial",
        }),
        recorded_by="exp34_runner",
        metadata={"experiment": "exp34a_endocrine"},
        storage_mode="full_payload",
    )

    chain.seal_epoch()
    return chain


@pytest.fixture(scope="module")
def chain():
    return _build_test_chain()


@pytest.fixture(scope="module")
def store(chain):
    return EvidenceStore(chain, experiment_name="exp34a_endocrine")


# =============================================================================
# Test 1: EvidenceRecord construction
# =============================================================================

class TestEvidenceRecord:
    def test_from_chain_record(self, chain):
        raw = chain.records[0]
        rec = EvidenceRecord.from_chain_record(0, raw)
        assert rec.index == 0
        assert rec.artifact_type == "model_chat_log"
        assert rec.model == "CC2"
        assert rec.round_idx == 0
        assert rec.experiment == "exp34a_endocrine"
        assert "C0001" in rec.finding_ids

    def test_finding_ids_extracted(self, chain):
        raw = chain.records[2]  # DeepSeek round 0 with C0001 and C0003
        rec = EvidenceRecord.from_chain_record(2, raw)
        assert "C0001" in rec.finding_ids
        assert "C0003" in rec.finding_ids

    def test_record_with_no_findings(self, chain):
        raw = chain.records[3]  # CC2 round 1 — verdicts, no new findings
        rec = EvidenceRecord.from_chain_record(3, raw)
        # Should still find IDs from verdict text
        assert "C0001" in rec.finding_ids
        assert "C0002" in rec.finding_ids


# =============================================================================
# Test 2: Finding ID extraction
# =============================================================================

class TestFindingIdExtraction:
    def test_from_string(self):
        assert _extract_finding_ids("Found C0001 and C0042") == ["C0001", "C0042"]

    def test_from_nested_dict(self):
        obj = {"a": {"b": "Bug C0010 in x.py"}, "c": ["C0020"]}
        assert _extract_finding_ids(obj) == ["C0010", "C0020"]

    def test_no_matches(self):
        assert _extract_finding_ids("No findings here") == []

    def test_deduplication(self):
        assert _extract_finding_ids("C0001 repeated C0001") == ["C0001"]


# =============================================================================
# Test 3: Query by entity
# =============================================================================

class TestQuery:
    def test_query_by_model(self, store):
        results = store.query(model="CC2")
        assert all(r.model == "CC2" for r in results)
        assert len(results) == 2  # rounds 0 and 1

    def test_query_by_round(self, store):
        results = store.query(round_idx=0)
        assert all(r.round_idx == 0 for r in results)
        assert len(results) == 3  # CC2, Gemini, DeepSeek

    def test_query_by_artifact_type(self, store):
        results = store.query(artifact_type="experiment_report")
        assert len(results) == 1
        assert results[0].artifact_type == "experiment_report"

    def test_query_by_finding_id(self, store):
        results = store.query(finding_id="C0001")
        assert len(results) > 0
        assert all("C0001" in r.finding_ids for r in results)

    def test_query_combined_filters(self, store):
        # CC2 records mentioning C0001
        results = store.query(model="CC2", finding_id="C0001")
        assert all(r.model == "CC2" and "C0001" in r.finding_ids for r in results)

    def test_query_no_matches(self, store):
        results = store.query(model="nonexistent")
        assert results == []

    def test_query_no_filters_returns_all(self, store):
        results = store.query()
        assert len(results) == store.record_count


# =============================================================================
# Test 4: Properties
# =============================================================================

class TestProperties:
    def test_models(self, store):
        assert set(store.models) == {"CC2", "DeepSeek", "Gemini"}

    def test_rounds(self, store):
        assert store.rounds == [0, 1, 2]

    def test_artifact_types(self, store):
        types = store.artifact_types
        assert "model_chat_log" in types
        assert "experiment_report" in types
        assert "experiment_checkpoint" in types

    def test_finding_ids(self, store):
        fids = store.finding_ids
        assert "C0001" in fids
        assert "C0002" in fids
        assert "C0003" in fids

    def test_record_count(self, store):
        assert store.record_count == 8  # 6 model logs + checkpoint + report

    def test_get_record(self, store):
        rec = store.get_record(0)
        assert rec.index == 0
        assert rec.model == "CC2"

    def test_get_record_out_of_range(self, store):
        with pytest.raises(IndexError):
            store.get_record(999)


# =============================================================================
# Test 5: Provenance tracing
# =============================================================================

class TestProvenanceTrace:
    def test_trace_c0001(self, store):
        trace = store.trace_finding("C0001")
        assert len(trace) > 0
        assert all(isinstance(e, ProvenanceEvent) for e in trace)
        # Should be in chronological order (by record index)
        indices = [e.record_index for e in trace]
        assert indices == sorted(indices)

    def test_trace_includes_submissions_and_verdicts(self, store):
        trace = store.trace_finding("C0001")
        event_types = [e.event_type for e in trace]
        assert "submitted" in event_types
        assert "confirmed" in event_types

    def test_trace_c0001_has_extension(self, store):
        trace = store.trace_finding("C0001")
        event_types = [e.event_type for e in trace]
        assert "extended" in event_types

    def test_trace_c0002_has_challenge(self, store):
        trace = store.trace_finding("C0002")
        event_types = [e.event_type for e in trace]
        assert "challenged" in event_types

    def test_trace_nonexistent_finding(self, store):
        trace = store.trace_finding("C9999")
        assert trace == []

    def test_trace_events_have_chain_hashes(self, store):
        trace = store.trace_finding("C0001")
        for event in trace:
            assert event.chain_hash.startswith("sha256:")

    def test_trace_event_descriptions(self, store):
        trace = store.trace_finding("C0001")
        for event in trace:
            assert "C0001" in event.detail


# =============================================================================
# Test 6: Evidence bundle export
# =============================================================================

class TestEvidenceBundle:
    def test_export_by_indices(self, store):
        bundle = store.export_bundle(record_indices=[0, 1, 2])
        assert len(bundle.records) == 3
        assert len(bundle.inclusion_proofs) == 3
        assert bundle.merkle_root.startswith("sha256:")

    def test_export_by_finding(self, store):
        bundle = store.export_bundle(finding_id="C0001")
        assert len(bundle.records) > 0

    def test_export_by_model(self, store):
        bundle = store.export_bundle(model="Gemini")
        assert len(bundle.records) == 2  # rounds 0 and 1

    def test_bundle_to_dict(self, store):
        bundle = store.export_bundle(record_indices=[0])
        d = bundle.to_dict()
        assert d["bundle_version"] == "1.0"
        assert d["record_count"] == 1
        assert "records" in d
        assert "inclusion_proofs" in d

    def test_bundle_save_and_load(self, store):
        bundle = store.export_bundle(record_indices=[0, 1])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            bundle.save_json(path)
            with open(path) as f:
                loaded = json.load(f)
            assert loaded["record_count"] == 2
            assert loaded["merkle_root"] == bundle.merkle_root
        finally:
            os.unlink(path)

    def test_bundle_verification(self, store):
        bundle = store.export_bundle(record_indices=[0, 1, 2])
        valid, errors = store.verify_bundle(bundle)
        assert valid is True
        assert errors == []

    def test_export_empty_raises(self, store):
        with pytest.raises(ValueError):
            store.export_bundle(finding_id="C9999")


# =============================================================================
# Test 7: Chain verification through store
# =============================================================================

class TestStoreVerification:
    def test_verify_passes(self, store):
        valid, msg = store.verify()
        assert valid is True
        assert "verified" in msg.lower()

    def test_is_verified_cached(self, store):
        store.verify()
        assert store.is_verified is True

    def test_new_store_not_verified(self, chain):
        fresh = EvidenceStore(chain)
        assert fresh.is_verified is None


# =============================================================================
# Test 8: Summary
# =============================================================================

class TestSummary:
    def test_summary_fields(self, store):
        s = store.summary()
        assert isinstance(s, StoreSummary)
        assert s.experiment == "exp34a_endocrine"
        assert s.total_records == 8
        assert s.epoch_count == 1
        assert s.merkle_root.startswith("sha256:")

    def test_summary_records_by_type(self, store):
        s = store.summary()
        assert s.records_by_type["model_chat_log"] == 6
        assert s.records_by_type["experiment_report"] == 1

    def test_summary_records_by_model(self, store):
        s = store.summary()
        assert s.records_by_model["CC2"] == 2
        assert s.records_by_model["Gemini"] == 2
        assert s.records_by_model["DeepSeek"] == 2

    def test_summary_rounds(self, store):
        s = store.summary()
        assert s.rounds_covered == [0, 1, 2]


# =============================================================================
# Test 9: Loading from files
# =============================================================================

class TestFileLoading:
    def test_from_chain_file(self, chain):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            chain.save_json(path)
            store = EvidenceStore.from_chain_file(path)
            assert store.record_count == 8
        finally:
            os.unlink(path)

    def test_from_experiment_dir(self, chain):
        with tempfile.TemporaryDirectory() as d:
            chain_path = os.path.join(d, "experiment_chain.json")
            chain.save_json(chain_path)
            store = EvidenceStore.from_experiment_dir(d)
            assert store.record_count == 8

    def test_from_experiment_dir_missing_chain(self):
        with tempfile.TemporaryDirectory() as d:
            with pytest.raises(FileNotFoundError):
                EvidenceStore.from_experiment_dir(d)


# =============================================================================
# Test 10: Index internals
# =============================================================================

class TestIndex:
    def test_search_intersection(self, store):
        # Round 0 + model CC2 should return exactly 1
        results = store.query(round_idx=0, model="CC2")
        assert len(results) == 1
        assert results[0].model == "CC2"
        assert results[0].round_idx == 0

    def test_search_with_type_filter(self, store):
        results = store.query(artifact_type="model_chat_log", round_idx=1)
        assert len(results) == 2  # CC2 and Gemini in round 1
        assert all(r.artifact_type == "model_chat_log" for r in results)


# =============================================================================
# Test 11: Event classification
# =============================================================================

class TestEventClassification:
    def test_classify_submission(self, chain):
        raw = chain.records[0]
        rec = EvidenceRecord.from_chain_record(0, raw)
        assert _classify_event(rec, "C0001") == "submitted"

    def test_classify_confirm(self, chain):
        raw = chain.records[3]  # CC2 round 1: CONFIRM C0001
        rec = EvidenceRecord.from_chain_record(3, raw)
        assert _classify_event(rec, "C0001") == "confirmed"

    def test_classify_challenge(self, chain):
        raw = chain.records[3]  # CC2 round 1: CHALLENGE C0002
        rec = EvidenceRecord.from_chain_record(3, raw)
        assert _classify_event(rec, "C0002") == "challenged"

    def test_classify_extend(self, chain):
        raw = chain.records[5]  # DeepSeek round 2: EXTEND C0001
        rec = EvidenceRecord.from_chain_record(5, raw)
        assert _classify_event(rec, "C0001") == "extended"

    def test_classify_report(self, chain):
        raw = chain.records[7]  # experiment report
        rec = EvidenceRecord.from_chain_record(7, raw)
        assert _classify_event(rec, "C0001") == "reported"
