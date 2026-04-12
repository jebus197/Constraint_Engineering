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


# ═══════════════════════════════════════════════════════════════════════════════
# Layer 1: Domain-aware DC v2 classification (Exp 38 fix cycle)
# ═══════════════════════════════════════════════════════════════════════════════

from bench.immune_agents import (
    _classify_claim_v2,
    _CODE_CONTEXT_PATTERN,
    _STRONG_MATH_SIGNAL,
    dendritic_cell_v2,
    load_domain_config,
)


class TestLayer1CodeContext:
    """Layer 1: software-domain code-context routing before math."""

    def test_code_bug_with_operators_routes_to_code(self):
        """Code finding with >= operator should NOT be misrouted to MATHEMATICAL."""
        f = _make_finding(
            desc="FIND: add_verdict() unconditionally overwrites "
                 "`self.entries[canonical_id]['last_status_change_round'] = round_idx` "
                 "on every verdict, corrupting the escalation timer"
        )
        ct, _, conf = _classify_claim_v2(f, domain="software")
        assert ct == ClaimType.CODE_BEHAVIORAL

    def test_code_bug_status_transition_routes_to_code(self):
        """Status transition bugs should route to CODE_BEHAVIORAL in software domain."""
        f = _make_finding(
            desc="The status transition from REOPENED to OPEN directly mutates "
                 "entry['status'] = 'OPEN' bypassing resolve(), so "
                 "last_status_change_round is never updated"
        )
        ct, _, conf = _classify_claim_v2(f, domain="software")
        assert ct == ClaimType.CODE_BEHAVIORAL

    def test_function_def_routes_to_code(self):
        """Finding mentioning def function_name routes to CODE_BEHAVIORAL."""
        f = _make_finding(
            desc="def escalate_stale_contested bypasses resolve() and does "
                 "a direct entry['status'] = 'CONFIRMED' mutation"
        )
        ct, _, conf = _classify_claim_v2(f, domain="software")
        assert ct == ClaimType.CODE_BEHAVIORAL

    def test_real_math_preserved_in_software_domain(self):
        """Strong math signals should NOT be overridden even in software domain.

        When code-context AND strong-math both match, math wins.
        Description must also trigger code-context for the guard to apply.
        """
        f = _make_finding(
            desc="The function compute_bound returns sqrt(n) but the proof "
                 "shows the equation requires n^2 for correctness"
        )
        ct, _, conf = _classify_claim_v2(f, domain="software")
        # "function" triggers code-context, but "proof" + "equation" trigger
        # _STRONG_MATH_SIGNAL, so code-context yield is suppressed.
        # Then _MATH_PATTERN_V2 catches "sqrt(" and "equation".
        assert ct == ClaimType.MATHEMATICAL

    def test_statistical_preserved_in_software_domain(self):
        """Statistical findings should route to STATISTICAL regardless of domain."""
        f = _make_finding(
            desc="The p-value of the distribution test is 0.003"
        )
        ct, _, conf = _classify_claim_v2(f, domain="software")
        assert ct == ClaimType.STATISTICAL

    def test_no_domain_falls_to_uncategorised(self):
        """Without domain, ambiguous findings should be UNCATEGORISED."""
        f = _make_finding(desc="Something vague with no clear indicators")
        ct, _, conf = _classify_claim_v2(f, domain="")
        assert ct == ClaimType.UNCATEGORISED

    def test_software_domain_uncategorised_residue_to_code(self):
        """In software domain, UNCATEGORISED residue defaults to CODE_BEHAVIORAL."""
        f = _make_finding(desc="Something vague with no clear indicators")
        ct, _, conf = _classify_claim_v2(f, domain="software")
        assert ct == ClaimType.CODE_BEHAVIORAL
        assert conf == 0.40  # Low confidence fallback

    def test_code_context_pattern_matches_expected(self):
        """Verify _CODE_CONTEXT_PATTERN matches Python constructs."""
        assert _CODE_CONTEXT_PATTERN.search("def escalate_stale_contested")
        assert _CODE_CONTEXT_PATTERN.search("self.entries[id]")
        assert _CODE_CONTEXT_PATTERN.search("class FindingRegistry")
        assert _CODE_CONTEXT_PATTERN.search("import json")
        assert _CODE_CONTEXT_PATTERN.search("__init__")
        assert _CODE_CONTEXT_PATTERN.search("raises ValueError when")
        assert _CODE_CONTEXT_PATTERN.search("bug in runtime logic errors")
        # CX-F1: bare words removed — "function", "method", "attribute",
        # "variable" no longer match (they appear in math vocabulary)
        assert not _CODE_CONTEXT_PATTERN.search("the function f(x) is bounded")
        assert not _CODE_CONTEXT_PATTERN.search("the attribute is symmetric")

    def test_strong_math_signal_matches_expected(self):
        """Verify _STRONG_MATH_SIGNAL matches genuine math indicators."""
        assert _STRONG_MATH_SIGNAL.search("p-value of 0.05")
        assert _STRONG_MATH_SIGNAL.search("standard deviation is too high")
        assert _STRONG_MATH_SIGNAL.search("proof by induction")
        assert _STRONG_MATH_SIGNAL.search("theorem 3.2 states")
        assert _STRONG_MATH_SIGNAL.search("O(n^2) complexity")
        assert _STRONG_MATH_SIGNAL.search("asymptotic bound on the function")
        # CX-F2: expanded coverage
        assert _STRONG_MATH_SIGNAL.search("bounded above by 1")
        assert _STRONG_MATH_SIGNAL.search("quadratic time algorithm")
        assert _STRONG_MATH_SIGNAL.search("for all x > 0")
        assert _STRONG_MATH_SIGNAL.search("the inequality holds")
        assert _STRONG_MATH_SIGNAL.search("satisfies the constraint")
        assert _STRONG_MATH_SIGNAL.search("the relation is transitive")
        assert not _STRONG_MATH_SIGNAL.search("entry status = OPEN")

    def test_cx_f1_math_with_function_word_not_misrouted(self):
        """CX-F1 regression: 'the function f(x)' should NOT route to CODE_BEHAVIORAL."""
        f = _make_finding(
            desc="The function f(x) = x^2 is bounded below by 0"
        )
        ct, _, conf = _classify_claim_v2(f, domain="software")
        # Should NOT be CODE_BEHAVIORAL — "function" is math vocabulary here
        assert ct != ClaimType.CODE_BEHAVIORAL

    def test_dendritic_v2_passes_domain(self):
        """DC v2 should use domain when classifying."""
        f = _make_finding(
            desc="def add_verdict overwrites the timer, "
                 "self.entries[id]['last_status_change_round'] = round_idx"
        )
        v1 = [TriagedFinding(finding=f, claim_type=ClaimType.CODE_BEHAVIORAL)]
        v2 = dendritic_cell_v2([f], v1, domain="software")
        assert v2[0].claim_type == ClaimType.CODE_BEHAVIORAL

    def test_exp38_code_bug_misroute_fixed(self):
        """Regression: Exp 38 code bugs should NOT go to MATHEMATICAL.

        In R0, 17/26 code findings were misrouted to MATHEMATICAL because
        descriptions contained operators like >=, ==, = in code context.
        Layer 1 code-context check should prevent this.
        """
        # Real Exp 38 finding descriptions (abbreviated)
        descs = [
            "add_verdict() mutates last_status_change_round for every verdict, "
            "even when no status has changed. self.entries[canonical_id]"
            "['last_status_change_round'] = round_idx",

            "escalate_stale_contested and auto_resolve_contested bypass resolve() "
            "and directly mutate entry['status']",

            "CONFIRMED+verified close before challenge check. "
            "if entry['status'] == 'CONFIRMED' and entry.get('verified')",
        ]
        for desc in descs:
            f = _make_finding(desc=desc)
            ct, _, _ = _classify_claim_v2(f, domain="software")
            assert ct == ClaimType.CODE_BEHAVIORAL, (
                f"Expected CODE_BEHAVIORAL for: {desc[:60]}..."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Layer 2: LLM classifier residue reclassification
# ═══════════════════════════════════════════════════════════════════════════════

from bench.immune_agents import _apply_llm_reclassification


class TestLayer2LLMReclassification:
    """Layer 2: targeted LLM reclassification of UNCATEGORISED residue."""

    def test_no_uncategorised_is_noop(self):
        """If no findings are UNCATEGORISED, Layer 2 does nothing."""
        triaged = [
            TriagedFinding(finding=_make_finding(), claim_type=ClaimType.CODE_BEHAVIORAL),
            TriagedFinding(finding=_make_finding(fid="f2"), claim_type=ClaimType.MATHEMATICAL),
        ]
        count = _apply_llm_reclassification(triaged, domain="software")
        assert count == 0
        assert triaged[0].claim_type == ClaimType.CODE_BEHAVIORAL
        assert triaged[1].claim_type == ClaimType.MATHEMATICAL

    @patch("bench.immune_agents._active_llm_classify")
    def test_uncategorised_reclassified_by_llm(self, mock_llm):
        """UNCATEGORISED finding reclassified when LLM returns confident result."""
        mock_llm.return_value = (ClaimType.LOGICAL, 0.75)
        triaged = [
            TriagedFinding(
                finding=_make_finding(desc="some ambiguous finding"),
                claim_type=ClaimType.UNCATEGORISED,
            ),
        ]
        count = _apply_llm_reclassification(triaged, domain="software")
        assert count == 1
        assert triaged[0].claim_type == ClaimType.LOGICAL

    @patch("bench.immune_agents._active_llm_classify")
    def test_low_confidence_falls_back_to_code_in_software(self, mock_llm):
        """Low LLM confidence in software domain falls back to CODE_BEHAVIORAL."""
        mock_llm.return_value = (ClaimType.LOGICAL, 0.30)
        triaged = [
            TriagedFinding(
                finding=_make_finding(desc="ambiguous"),
                claim_type=ClaimType.UNCATEGORISED,
            ),
        ]
        count = _apply_llm_reclassification(triaged, domain="software")
        assert count == 1
        assert triaged[0].claim_type == ClaimType.CODE_BEHAVIORAL

    @patch("bench.immune_agents._active_llm_classify")
    def test_llm_failure_falls_back_to_code_in_software(self, mock_llm):
        """LLM failure in software domain falls back to CODE_BEHAVIORAL."""
        mock_llm.return_value = (None, 0.0)
        triaged = [
            TriagedFinding(
                finding=_make_finding(desc="ambiguous"),
                claim_type=ClaimType.UNCATEGORISED,
            ),
        ]
        count = _apply_llm_reclassification(triaged, domain="software")
        assert count == 1
        assert triaged[0].claim_type == ClaimType.CODE_BEHAVIORAL

    @patch("bench.immune_agents._active_llm_classify")
    def test_uncategorised_stays_without_software_domain(self, mock_llm):
        """Without software domain, UNCATEGORISED stays if LLM fails."""
        mock_llm.return_value = (None, 0.0)
        triaged = [
            TriagedFinding(
                finding=_make_finding(desc="ambiguous"),
                claim_type=ClaimType.UNCATEGORISED,
            ),
        ]
        count = _apply_llm_reclassification(triaged, domain="")
        assert count == 0
        assert triaged[0].claim_type == ClaimType.UNCATEGORISED


# ═══════════════════════════════════════════════════════════════════════════════
# Layer 3: Domain routing + hard verification gate
# ═══════════════════════════════════════════════════════════════════════════════


class TestLayer3DomainRouting:
    """Layer 3: domain config loading and verification gate."""

    def test_load_software_domain_config(self):
        """Software domain should load code.toml (via alias)."""
        config = load_domain_config("software")
        assert "immune" in config
        assert "claim_patterns" in config["immune"]
        assert "verification_tools" in config["immune"]

    def test_load_mathematics_domain_config(self):
        """Mathematics domain should load mathematics.toml."""
        config = load_domain_config("mathematics")
        assert "immune" in config
        assert "mathematical" in config["immune"]["claim_patterns"]

    def test_load_unknown_domain_returns_empty(self):
        """Unknown domain returns empty dict, no error."""
        config = load_domain_config("unknown_domain_xyz")
        assert config == {}

    def test_domain_config_cached(self):
        """Second load should return cached result."""
        c1 = load_domain_config("software")
        c2 = load_domain_config("software")
        assert c1 is c2  # Same object from cache

    def test_immune_response_includes_domain(self):
        """ImmuneResponse should carry domain field."""
        response = ImmuneResponse(
            triaged=[], cell_verdicts={}, final_verdicts={},
            final_confidences={}, filtered_findings=[], rejected_findings=[],
            rejection_rate=0.0, autoimmune_flag=False, stage_timings={},
            tool_usage={}, observation_only=True, domain="software",
        )
        assert response.domain == "software"


class TestHardVerificationGate:
    """Stage 6: nothing exits without a tool-grounded verdict."""

    def test_finding_with_ct_verdict_passes(self):
        """Finding with CT verdict should not be escalated by gate."""
        f = _make_finding()
        verdicts = [
            CellVerdict(
                cell_type=CellType.CYTOTOXIC_T, finding_id="f1",
                verdict="CONFIRMED", confidence=0.8,
                evidence="Bug exists at line 305", tool_used="ct_v1",
            ),
        ]
        # Simulate gate check
        _TOOL_GROUNDED = {CellType.CYTOTOXIC_T, CellType.B_CELL, CellType.NK_CELL}
        tool_v = [v for v in verdicts if v.finding_id == "f1" and v.cell_type in _TOOL_GROUNDED]
        assert len(tool_v) > 0  # Has tool-grounded verdict

    def test_finding_with_only_helper_t_escalated(self):
        """Finding with only Helper T verdict should be escalated."""
        verdicts = [
            CellVerdict(
                cell_type=CellType.HELPER_T, finding_id="f1",
                verdict="UNCERTAIN", confidence=0.3,
                evidence="No cell could verify", tool_used="helper_t",
            ),
        ]
        _TOOL_GROUNDED = {CellType.CYTOTOXIC_T, CellType.B_CELL, CellType.NK_CELL}
        tool_v = [v for v in verdicts if v.finding_id == "f1" and v.cell_type in _TOOL_GROUNDED]
        assert len(tool_v) == 0  # No tool-grounded verdict → escalate

    def test_finding_with_b_cell_verdict_passes(self):
        """Finding with B-Cell verdict should not be escalated."""
        verdicts = [
            CellVerdict(
                cell_type=CellType.B_CELL, finding_id="f1",
                verdict="REJECTED", confidence=0.7,
                evidence="z3 counterexample", tool_used="z3",
            ),
        ]
        _TOOL_GROUNDED = {CellType.CYTOTOXIC_T, CellType.B_CELL, CellType.NK_CELL}
        tool_v = [v for v in verdicts if v.finding_id == "f1" and v.cell_type in _TOOL_GROUNDED]
        assert len(tool_v) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Phase B4: Specialist B-Cell Dispatch
# ═══════════════════════════════════════════════════════════════════════════════


class TestSpecialistBCellDispatch:

    def test_specialist_selects_correct_tools(self):
        """Specialist dispatch routes mathematical claims to sympy."""
        from bench.immune_agents import _specialist_b_cell_dispatch
        tf = TriagedFinding(
            finding=_make_finding(fid="f1", desc="sqrt(4) = 3"),
            claim_type=ClaimType.MATHEMATICAL,
            extracted_claim="sqrt(4) = 3",
        )
        domain_config = {
            "immune": {
                "verification_tools": {
                    "mathematical": ["sympy", "z3"],
                    "logical": ["z3"],
                },
            },
        }
        verdicts = _specialist_b_cell_dispatch([tf], domain_config)
        assert len(verdicts) >= 1
        assert verdicts[0].finding_id == "f1"

    def test_specialist_fallback_empty_config(self):
        """Specialist dispatch returns empty on missing tool config."""
        from bench.immune_agents import _specialist_b_cell_dispatch
        tf = TriagedFinding(
            finding=_make_finding(fid="f1", desc="x > 0"),
            claim_type=ClaimType.MATHEMATICAL,
            extracted_claim="x > 0",
        )
        verdicts = _specialist_b_cell_dispatch([tf], {})
        assert verdicts == []

    def test_specialist_domain_patterns_override(self):
        """Domain config routes statistical claims to statsmodels."""
        from bench.immune_agents import _specialist_b_cell_dispatch
        tf = TriagedFinding(
            finding=_make_finding(fid="f1", desc="convergence test"),
            claim_type=ClaimType.STATISTICAL,
            extracted_claim="p-value < 0.05 significant",
        )
        domain_config = {
            "immune": {
                "verification_tools": {
                    "statistical": ["statsmodels"],
                },
            },
        }
        verdicts = _specialist_b_cell_dispatch([tf], domain_config)
        assert len(verdicts) >= 1

    def test_specialist_shadow_no_pipeline_mutation(self):
        """Specialist and generic B-Cell produce independent results."""
        from bench.immune_agents import _specialist_b_cell_dispatch
        tf = TriagedFinding(
            finding=_make_finding(fid="f1", desc="2 + 2 = 5"),
            claim_type=ClaimType.MATHEMATICAL,
            extracted_claim="2 + 2 = 5",
        )
        domain_config = {
            "immune": {
                "verification_tools": {"mathematical": ["sympy"]},
            },
        }
        specialist = _specialist_b_cell_dispatch([tf], domain_config)
        generic = b_cell_verify([tf])
        assert isinstance(specialist, list)
        assert isinstance(generic, list)


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 7: Ouroboros Cell (O1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestOuroborosCell:

    def test_shadow_mode_no_pipeline_mutation(self):
        """O1 shadow mode must never modify pipeline state."""
        from bench.ouroboros_cell import OuroborosCell, OuroborosMode
        o1 = OuroborosCell(mode=OuroborosMode.MACROPHAGE, shadow=True)
        # Create mock verdicts
        verdicts = [
            CellVerdict(
                cell_type=CellType.B_CELL, finding_id=f"f{i}",
                verdict="CONFIRMED", confidence=0.8,
                evidence="test", tool_used="sympy",
            )
            for i in range(5)
        ]
        summary = o1.observe(verdicts)
        assert summary.pipeline_modified is False

    def test_macrophage_detects_verdict_cluster(self):
        """Macrophage mode flags when >80% verdicts are the same."""
        from bench.ouroboros_cell import OuroborosCell, OuroborosMode
        o1 = OuroborosCell(mode=OuroborosMode.MACROPHAGE)
        # 9/10 REJECTED = 90% cluster
        verdicts = [
            CellVerdict(
                cell_type=CellType.B_CELL, finding_id=f"f{i}",
                verdict="REJECTED", confidence=0.7,
                evidence="test", tool_used="z3",
            )
            for i in range(9)
        ] + [
            CellVerdict(
                cell_type=CellType.B_CELL, finding_id="f9",
                verdict="CONFIRMED", confidence=0.8,
                evidence="test", tool_used="sympy",
            )
        ]
        summary = o1.observe(verdicts)
        anomalies = [o for o in summary.observations if o.category == "verdict_cluster"]
        assert len(anomalies) >= 1

    def test_microglia_detects_tool_monoculture(self):
        """Microglia mode flags when all verdicts come from one tool."""
        from bench.ouroboros_cell import OuroborosCell, OuroborosMode
        o1 = OuroborosCell(mode=OuroborosMode.MICROGLIA)
        # All verdicts from same tool
        verdicts = [
            CellVerdict(
                cell_type=CellType.B_CELL, finding_id=f"f{i}",
                verdict="CONFIRMED", confidence=0.8,
                evidence="test", tool_used="sympy",
            )
            for i in range(6)
        ]
        summary = o1.observe(verdicts)
        monoculture = [o for o in summary.observations if o.category == "tool_monoculture"]
        assert len(monoculture) >= 1

    def test_signed_chain_verifiable(self):
        """O1 observations can be signed into verification chain."""
        from bench.ouroboros_cell import OuroborosCell, OuroborosMode, OuroborosObservation
        from bench.verification_chain import VerificationChain
        o1 = OuroborosCell(mode=OuroborosMode.MACROPHAGE)
        chain = VerificationChain()
        obs = OuroborosObservation(
            observation_id="o1_test",
            mode=OuroborosMode.MACROPHAGE,
            category="test",
            description="Test observation",
            severity=0.5,
            is_anomaly=True,
        )
        record = o1.sign_observation(obs, chain)
        assert record is not None
        assert record["sealed_body"]["artifact_type"] == "ouroboros_observation"
        assert len(chain._records) == 1
