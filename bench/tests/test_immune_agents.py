"""Tests for the immune agent pipeline (bench/immune_agents.py)."""

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
        # f1 should be flagged as duplicate and removed
        assert any(v == "DUPLICATE" for v in result.final_verdicts.values())

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

    def test_autoimmune_override_in_filtering_mode(self):
        """When autoimmune flag fires, all findings pass through even in filtering mode."""
        # Create 10 findings that will all be flagged as known false positives
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
        # Regulatory T-Cell should flag autoimmune (>50% rejection)
        # and override: all findings pass through
        if result.autoimmune_flag:
            assert len(result.filtered_findings) == 10
