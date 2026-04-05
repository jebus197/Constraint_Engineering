"""Tests for the immune agent pipeline (bench/immune_agents.py)."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from bench.dm._types import Finding
from bench.immune_agents import (
    CellType,
    ClaimType,
    CellVerdict,
    TriagedFinding,
    ImmuneResponse,
    dendritic_cell_triage,
    b_cell_verify,
    nk_cell_verify,
    helper_t_cell_synthesize,
    regulatory_t_cell_check,
    run_immune_pipeline,
    _classify_claim,
    _verify_ct_claim,
    _ct_evidence_to_verdict,
    _parse_ct_output,
    _KNOWN_FALSE_POSITIVES,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

def _make_finding(fid="f1", model="CC2", severity=0.7, desc="Bug in parser",
                  round_idx=0, flaw_class=2) -> Finding:
    return Finding(
        finding_id=fid, model_id=model, round_idx=round_idx,
        flaw_class=flaw_class, severity=severity, abstraction_index=0.5,
        description=desc,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Dendritic Cell — triage and classification
# ═══════════════════════════════════════════════════════════════════════════════

class TestDendriticCell:
    def test_math_claim_detected(self):
        f = _make_finding(desc="The formula x >= sqrt(n) is violated")
        claim_type, _ = _classify_claim(f)
        assert claim_type == ClaimType.MATHEMATICAL

    def test_logic_claim_detected(self):
        f = _make_finding(desc="If immune_feedback_enabled is False then self_diagnose should return empty")
        claim_type, _ = _classify_claim(f)
        assert claim_type == ClaimType.LOGICAL

    def test_statistical_claim_detected(self):
        f = _make_finding(desc="Severity distribution has p-value p=0.003 indicating significant difference")
        claim_type, _ = _classify_claim(f)
        assert claim_type == ClaimType.STATISTICAL

    def test_structural_claim_detected(self):
        f = _make_finding(desc="Missing @dataclass decorator on DetectorDiagnosis")
        claim_type, _ = _classify_claim(f)
        assert claim_type == ClaimType.CODE_STRUCTURAL

    def test_behavioral_default(self):
        f = _make_finding(desc="record_round does not handle empty findings list")
        claim_type, _ = _classify_claim(f)
        assert claim_type == ClaimType.CODE_BEHAVIORAL

    def test_triage_all_findings(self):
        findings = [
            _make_finding(fid="f1", desc="x >= 0 always holds"),
            _make_finding(fid="f2", desc="Bug in parser logic"),
            _make_finding(fid="f3", desc="If A then B invariant violated"),
        ]
        triaged = dendritic_cell_triage(findings)
        assert len(triaged) == 3
        assert triaged[0].claim_type == ClaimType.MATHEMATICAL
        assert triaged[1].claim_type == ClaimType.CODE_BEHAVIORAL
        assert triaged[2].claim_type == ClaimType.LOGICAL


# ═══════════════════════════════════════════════════════════════════════════════
# NK Cell — pattern recognition and dedup
# ═══════════════════════════════════════════════════════════════════════════════

class TestNKCell:
    def test_dedup_identical_findings(self):
        f1 = _make_finding(fid="f1", desc="Buffer overflow in parser")
        f2 = _make_finding(fid="f2", desc="Buffer overflow in parser")
        triaged = dendritic_cell_triage([f2])
        updated, verdicts = nk_cell_verify(triaged, [f1], tau_sim=0.8)
        assert updated[0].is_duplicate
        assert any(v.verdict == "DUPLICATE" for v in verdicts)

    def test_novel_finding_passes(self):
        f1 = _make_finding(fid="f1", desc="Buffer overflow in parser")
        f2 = _make_finding(fid="f2", desc="Race condition in dispatcher")
        triaged = dendritic_cell_triage([f2])
        updated, verdicts = nk_cell_verify(triaged, [f1], tau_sim=0.8)
        assert not updated[0].is_duplicate

    def test_known_false_positive_codex_dataclass(self):
        f = _make_finding(
            fid="f1", model="Codex",
            desc="Missing @dataclass decorator on DynamicManagementConfig",
        )
        triaged = dendritic_cell_triage([f])
        _, verdicts = nk_cell_verify(triaged, [], tau_sim=0.8)
        rejected = [v for v in verdicts if v.verdict == "REJECTED"]
        assert len(rejected) == 1
        assert "Known FP" in rejected[0].evidence

    def test_late_round_severity_anomaly(self):
        f = _make_finding(fid="f1", severity=0.98, round_idx=8,
                          desc="Completely new critical bug")
        triaged = dendritic_cell_triage([f])
        _, verdicts = nk_cell_verify(triaged, [], tau_sim=0.8)
        anomaly = [v for v in verdicts if v.tool_used == "anomaly_detection"]
        assert len(anomaly) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Helper T-Cell — verdict synthesis
# ═══════════════════════════════════════════════════════════════════════════════

class TestHelperTCell:
    def test_confirmed_wins(self):
        tf = TriagedFinding(
            finding=_make_finding(fid="f1"),
            claim_type=ClaimType.CODE_BEHAVIORAL,
        )
        verdicts = [
            CellVerdict(CellType.CYTOTOXIC_T, "f1", "CONFIRMED", 0.9, "", "fff"),
            CellVerdict(CellType.B_CELL, "f1", "UNCERTAIN", 0.3, "", "sympy"),
        ]
        final, conf = helper_t_cell_synthesize([tf], verdicts)
        assert final["f1"] == "CONFIRMED"

    def test_rejected_needs_strong_evidence(self):
        tf = TriagedFinding(
            finding=_make_finding(fid="f1"),
            claim_type=ClaimType.CODE_BEHAVIORAL,
        )
        verdicts = [
            CellVerdict(CellType.CYTOTOXIC_T, "f1", "REJECTED", 0.8, "", "fff"),
            CellVerdict(CellType.NK_CELL, "f1", "UNCERTAIN", 0.2, "", "dedup"),
        ]
        final, conf = helper_t_cell_synthesize([tf], verdicts)
        assert final["f1"] == "REJECTED"

    def test_no_verdicts_passes_through(self):
        tf = TriagedFinding(
            finding=_make_finding(fid="f1"),
            claim_type=ClaimType.CODE_BEHAVIORAL,
        )
        final, conf = helper_t_cell_synthesize([tf], [])
        assert final["f1"] == "UNCERTAIN"

    def test_duplicate_auto_rejected(self):
        tf = TriagedFinding(
            finding=_make_finding(fid="f1"),
            claim_type=ClaimType.CODE_BEHAVIORAL,
            is_duplicate=True,
            duplicate_of="f0",
            similarity=0.95,
        )
        final, conf = helper_t_cell_synthesize([tf], [])
        assert final["f1"] == "DUPLICATE"

    def test_asymmetric_threshold(self):
        """Rejection needs 0.6+ net confidence, confirmation only 0.4+."""
        tf = TriagedFinding(
            finding=_make_finding(fid="f1"),
            claim_type=ClaimType.CODE_BEHAVIORAL,
        )
        # 0.5 reject, 0.5 confirm → neither reaches threshold
        verdicts = [
            CellVerdict(CellType.CYTOTOXIC_T, "f1", "REJECTED", 0.5, "", "fff"),
            CellVerdict(CellType.B_CELL, "f1", "CONFIRMED", 0.5, "", "sympy"),
        ]
        final, _ = helper_t_cell_synthesize([tf], verdicts)
        # confirm_weight=0.5, reject_weight=0.5
        # reject ratio = 0.5/1.0 = 0.5 < 0.6 → not rejected
        # confirm ratio = 0.5/1.0 = 0.5 >= 0.4 → confirmed
        assert final["f1"] == "CONFIRMED"


# ═══════════════════════════════════════════════════════════════════════════════
# Regulatory T-Cell — meta-verification
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegulatoryTCell:
    def test_healthy_pipeline(self):
        verdicts = {f"f{i}": "CONFIRMED" for i in range(8)}
        verdicts["f8"] = "REJECTED"
        verdicts["f9"] = "REJECTED"
        triaged = [
            TriagedFinding(finding=_make_finding(fid=f"f{i}"),
                           claim_type=ClaimType.CODE_BEHAVIORAL)
            for i in range(10)
        ]
        flag, reason = regulatory_t_cell_check(verdicts, triaged)
        assert not flag

    def test_autoimmune_detected(self):
        verdicts = {f"f{i}": "REJECTED" for i in range(8)}
        verdicts["f8"] = "CONFIRMED"
        verdicts["f9"] = "CONFIRMED"
        triaged = [
            TriagedFinding(finding=_make_finding(fid=f"f{i}"),
                           claim_type=ClaimType.CODE_BEHAVIORAL)
            for i in range(10)
        ]
        flag, reason = regulatory_t_cell_check(verdicts, triaged, max_rejection_rate=0.5)
        assert flag
        assert "exceeds threshold" in reason

    def test_all_from_one_model_rejected(self):
        triaged = [
            TriagedFinding(
                finding=_make_finding(fid=f"f{i}", model="Gemini"),
                claim_type=ClaimType.CODE_BEHAVIORAL,
            )
            for i in range(5)
        ]
        triaged.extend([
            TriagedFinding(
                finding=_make_finding(fid=f"f{i+5}", model="CC2"),
                claim_type=ClaimType.CODE_BEHAVIORAL,
            )
            for i in range(5)
        ])
        verdicts = {}
        for i in range(5):
            verdicts[f"f{i}"] = "REJECTED"   # all Gemini rejected
        for i in range(5, 10):
            verdicts[f"f{i}"] = "CONFIRMED"  # all CC2 confirmed
        flag, reason = regulatory_t_cell_check(verdicts, triaged)
        assert flag
        assert "Gemini" in reason

    def test_too_few_findings_skips(self):
        verdicts = {"f0": "REJECTED", "f1": "REJECTED"}
        triaged = [
            TriagedFinding(finding=_make_finding(fid=f"f{i}"),
                           claim_type=ClaimType.CODE_BEHAVIORAL)
            for i in range(2)
        ]
        flag, _ = regulatory_t_cell_check(verdicts, triaged, min_findings_for_check=5)
        assert not flag


# ═══════════════════════════════════════════════════════════════════════════════
# Full pipeline — observation-only mode
# ═══════════════════════════════════════════════════════════════════════════════

class TestImmunePipeline:
    def test_observation_mode_passes_everything(self):
        findings = [
            _make_finding(fid="f1", desc="x >= 0 always"),
            _make_finding(fid="f2", desc="Bug in parser logic"),
        ]
        result = run_immune_pipeline(
            findings, [], source_paths=[],
            observation_only=True, ct_enabled=False,
        )
        assert len(result.filtered_findings) == 2
        assert len(result.rejected_findings) == 0
        assert result.observation_only

    def test_filtering_mode_removes_duplicates(self):
        f_prior = _make_finding(fid="f0", desc="Buffer overflow in parser")
        f_new = _make_finding(fid="f1", desc="Buffer overflow in parser")
        result = run_immune_pipeline(
            [f_new], [f_prior], source_paths=[],
            observation_only=False, ct_enabled=False,
        )
        # f1 should be flagged as duplicate and removed.
        # With v2 active + reconciliation gate, NK dedup produces REJECTED
        # (not DUPLICATE) because the reconciliation gate merges verdicts.
        assert any(
            v in ("DUPLICATE", "REJECTED")
            for v in result.final_verdicts.values()
        )

    def test_pipeline_returns_timings(self):
        findings = [_make_finding(fid="f1")]
        result = run_immune_pipeline(
            findings, [], source_paths=[],
            observation_only=True, ct_enabled=False,
        )
        assert "dendritic" in result.stage_timings
        assert "parallel_verification" in result.stage_timings
        assert "helper_t" in result.stage_timings
        assert "regulatory_t" in result.stage_timings

    def test_autoimmune_override_respects_locks(self):
        """E31-02: autoimmune override respects reconciliation locks.

        When both v1 and v2 reject a finding, the rejection is LOCKED
        and autoimmune recovery cannot resurrect it.
        """
        # All 10 findings are known false positives — both pipelines
        # will reject them → locked by reconciliation gate
        findings = [
            _make_finding(fid=f"f{i}", model="Codex",
                          desc="Missing @dataclass decorator on SomeClass")
            for i in range(10)
        ]
        result = run_immune_pipeline(
            findings, [], source_paths=[],
            observation_only=False, ct_enabled=False,
            max_rejection_rate=0.50,
        )
        # Autoimmune should fire (>50% rejection) but locked findings
        # stay rejected — they are not resurrected
        if result.autoimmune_flag:
            assert len(result.filtered_findings) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Cytotoxic T-Cell — mechanical verification (Level 3 enforcement)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCTMechanicalVerification:
    """Tests for _verify_ct_claim — the structural enforcement layer."""

    @pytest.fixture
    def source_file(self, tmp_path):
        """Create a temporary Python file with known content."""
        code = (
            "class Foo:\n"                    # line 1
            "    def bar(self):\n"             # line 2
            "        return 42\n"              # line 3
            "\n"                               # line 4
            "    def baz(self, x):\n"          # line 5
            "        if x > 0:\n"              # line 6
            "            return x * 2\n"       # line 7
            "        return -1\n"              # line 8
        )
        f = tmp_path / "test_source.py"
        f.write_text(code)
        return str(f)

    def test_exact_match(self, source_file):
        evidence = {
            "file": source_file,
            "line": 3,
            "code_snippet": "return 42",
            "observation": "returns constant",
        }
        verified, conf, reason = _verify_ct_claim(evidence)
        assert verified
        assert conf == 1.0
        assert "Exact match" in reason

    def test_near_match_in_window(self, source_file):
        evidence = {
            "file": source_file,
            "line": 5,
            "code_snippet": "if x > 0:",
            "observation": "checks positivity",
        }
        # "if x > 0:" is at line 6, but we cited line 5 — should find in ±2 window
        verified, conf, reason = _verify_ct_claim(evidence)
        assert verified
        assert conf >= 0.5

    def test_mismatch_drops_to_zero(self, source_file):
        evidence = {
            "file": source_file,
            "line": 3,
            "code_snippet": "return self.hallucinated_value",
            "observation": "wrong return",
        }
        verified, conf, reason = _verify_ct_claim(evidence)
        assert not verified
        assert conf == 0.0
        assert "does not match" in reason

    def test_missing_file(self):
        evidence = {
            "file": "/nonexistent/path/to/file.py",
            "line": 1,
            "code_snippet": "anything",
            "observation": "test",
        }
        verified, conf, reason = _verify_ct_claim(evidence)
        assert not verified
        assert conf == 0.0

    def test_line_out_of_range(self, source_file):
        evidence = {
            "file": source_file,
            "line": 999,
            "code_snippet": "return 42",
            "observation": "test",
        }
        verified, conf, reason = _verify_ct_claim(evidence)
        assert not verified
        assert "out of range" in reason

    def test_empty_evidence(self):
        verified, conf, reason = _verify_ct_claim({})
        assert not verified
        assert conf == 0.0


class TestCTEvidenceToVerdict:
    """Tests for _ct_evidence_to_verdict — verdict from mechanical verification."""

    def test_all_verified_bug_exists_confirms(self, tmp_path):
        f = tmp_path / "src.py"
        f.write_text("def broken():\n    return None  # should return int\n")
        evidence = [{
            "file": str(f), "line": 2,
            "code_snippet": "return None  # should return int",
            "observation": "returns None instead of int",
        }]
        v = _ct_evidence_to_verdict("f1", "bug_exists", evidence)
        assert v.verdict == "CONFIRMED"
        assert v.confidence > 0
        assert v.tool_used == "ct_mechanical"

    def test_all_verified_no_error_rejects(self, tmp_path):
        f = tmp_path / "src.py"
        f.write_text("def correct():\n    return 42\n")
        evidence = [{
            "file": str(f), "line": 2,
            "code_snippet": "return 42",
            "observation": "returns correct value",
        }]
        v = _ct_evidence_to_verdict("f1", "no_error", evidence)
        assert v.verdict == "REJECTED"
        assert v.confidence > 0

    def test_no_evidence_verified_returns_uncertain(self):
        evidence = [{
            "file": "/nonexistent.py", "line": 1,
            "code_snippet": "hallucinated",
            "observation": "made up",
        }]
        v = _ct_evidence_to_verdict("f1", "bug_exists", evidence)
        assert v.verdict == "UNCERTAIN"
        assert v.confidence == 0.0
        assert "0/1 evidence items verified" in v.evidence

    def test_empty_evidence_list(self):
        v = _ct_evidence_to_verdict("f1", "bug_exists", [])
        assert v.verdict == "UNCERTAIN"
        assert "no evidence" in v.evidence.lower()


class TestCTOutputParsing:
    """Tests for _parse_ct_output — parsing agent output."""

    def test_schema_enforced_json(self):
        output = '{"verdicts": [{"finding_id": "f1", "claim_type": "bug_exists", "evidence": []}]}'
        results = _parse_ct_output(output)
        assert len(results) == 1
        assert results[0]["finding_id"] == "f1"

    def test_json_lines_fallback(self):
        output = (
            'Some text\n'
            '{"finding_id": "f1", "claim_type": "bug_exists", "evidence": []}\n'
            '{"finding_id": "f2", "claim_type": "no_error", "evidence": []}\n'
        )
        results = _parse_ct_output(output)
        assert len(results) == 2

    def test_embedded_json_fallback(self):
        output = (
            'Here is my analysis:\n'
            'Finding f1: {"finding_id": "f1", "claim_type": "bug_absent"}\n'
        )
        results = _parse_ct_output(output)
        assert len(results) == 1
        assert results[0]["finding_id"] == "f1"

    def test_empty_output(self):
        results = _parse_ct_output("")
        assert results == []

    def test_garbage_output(self):
        results = _parse_ct_output("This is just rambling text with no JSON at all.")
        assert results == []
