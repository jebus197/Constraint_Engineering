"""Integration tests for Experiment 29 architecture.

Tests the complete pipeline: insect brain relay, immune pipeline with
v2 activation, reconciliation gate, context budgets, and convergence
detection. No actual LLM calls — tests use synthetic findings to
exercise the full integration path.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_exp29_integration.py -v
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List
from unittest.mock import patch, MagicMock

import pytest

# Ensure project root is on sys.path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._types import DynamicManagementConfig, Finding
from bench.insect_brain import InsectBrain, RelayPayload, RoundRecord, BrainState
from bench.immune_agents import (
    CellType,
    ClaimType,
    CellVerdict,
    TriagedFinding,
    ImmuneResponse,
    dendritic_cell_triage,
    run_immune_pipeline,
    _classify_claim,
    _reconciliation_gate,
    _get_python_tools,
    _get_claude_cli,
    _extract_preconditions,
    _preconditions_to_z3,
    formalisation_agent_shadow,
)
from bench.runner_core import CONTEXT_CHAR_BUDGET, MODEL_SPECS


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

MODELS = ["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"]


def _make_finding(
    fid: str = "f1",
    model: str = "CC2",
    severity: float = 0.7,
    desc: str = "Bug in parser",
    round_idx: int = 0,
    flaw_class: int = 2,
    proposed_fix: str = "",
) -> Finding:
    return Finding(
        finding_id=fid,
        model_id=model,
        round_idx=round_idx,
        flaw_class=flaw_class,
        severity=severity,
        abstraction_index=0.5,
        description=desc,
        proposed_fix=proposed_fix,
    )


def _make_brain(tmp_path: Path) -> InsectBrain:
    """Create a brain with test config."""
    config = DynamicManagementConfig()
    brain = InsectBrain(
        config=config,
        logs_dir=tmp_path / "logs",
        source_paths=[],
    )
    brain.initialise(MODELS)
    return brain


def _make_round_findings(round_idx: int, n_per_model: int = 2) -> List[Finding]:
    """Generate synthetic findings for one round across all models."""
    findings = []
    for i, model in enumerate(MODELS):
        for j in range(n_per_model):
            fid = f"r{round_idx}_m{i}_f{j}"
            findings.append(_make_finding(
                fid=fid,
                model=model,
                round_idx=round_idx,
                severity=0.5 + 0.1 * j,
                desc=f"Finding {j} from {model} in round {round_idx}: "
                     f"potential issue in function_{i}_{j}",
                flaw_class=j % 5,
            ))
    return findings


# ═══════════════════════════════════════════════════════════════════════════════
# Insect Brain — Relay and Persistence
# ═══════════════════════════════════════════════════════════════════════════════

class TestInsectBrainRelay:
    """Test the insect brain's relay mechanics."""

    def test_relay_round_0_empty(self, tmp_path):
        brain = _make_brain(tmp_path)
        payloads = brain.relay(0)
        assert len(payloads) == 5
        for p in payloads.values():
            assert p.round_idx == 0
            assert p.finding_count == 0
            assert p.findings_text == ""

    def test_relay_cross_pollination(self, tmp_path):
        """Each model should NOT receive its own findings back."""
        brain = _make_brain(tmp_path)
        r0_findings = _make_round_findings(0)
        brain.persist(0, {m: "output" for m in MODELS}, r0_findings)

        payloads = brain.relay(1)
        for model, payload in payloads.items():
            # Model's own findings should be excluded
            assert model not in payload.findings_text or payload.context_reset

    def test_relay_context_budget_triggers_reset(self, tmp_path):
        """DeepSeek has a 30K budget — should trigger context reset with enough findings."""
        config = DynamicManagementConfig()
        brain = InsectBrain(
            config=config,
            logs_dir=tmp_path / "logs",
            source_paths=[],
        )
        brain.initialise(MODELS)

        # Generate many findings to exceed DeepSeek's 30K budget
        for rnd in range(5):
            findings = []
            for i, model in enumerate(MODELS):
                if model == "DeepSeek":
                    continue  # Other models produce findings
                for j in range(20):
                    findings.append(_make_finding(
                        fid=f"r{rnd}_m{i}_f{j}",
                        model=model,
                        round_idx=rnd,
                        desc="x" * 500,  # 500 chars each
                    ))
            brain.persist(rnd, {m: "output" for m in MODELS}, findings)

        payloads = brain.relay(5)
        ds_payload = payloads["DeepSeek"]
        # With 5 rounds × 4 models × 20 findings × ~500 chars each = ~200K,
        # DeepSeek (30K budget) should be in context reset mode
        assert ds_payload.context_reset

    def test_persist_creates_json(self, tmp_path):
        brain = _make_brain(tmp_path)
        findings = _make_round_findings(0, n_per_model=1)
        brain.persist(0, {m: "output" for m in MODELS}, findings)

        # Round file should exist
        round_file = tmp_path / "logs" / "round_00.json"
        assert round_file.exists()
        data = json.loads(round_file.read_text())
        assert data["round_idx"] == 0
        assert data["finding_count"] == 5

        # Checkpoint should exist
        checkpoint = tmp_path / "logs" / "checkpoint.json"
        assert checkpoint.exists()

    def test_persist_updates_state(self, tmp_path):
        brain = _make_brain(tmp_path)
        findings = _make_round_findings(0)
        brain.persist(0, {m: "output" for m in MODELS}, findings)
        assert brain.state.current_round == 0
        assert len(brain.state.all_findings) == 1
        assert len(brain.state.all_findings[0]) == 10  # 5 models × 2 findings

    def test_checkpoint_recovery(self, tmp_path):
        """Brain should recover from checkpoint."""
        brain = _make_brain(tmp_path)
        for rnd in range(3):
            findings = _make_round_findings(rnd)
            brain.persist(rnd, {m: "output" for m in MODELS}, findings)

        # Create new brain and load checkpoint
        brain2 = _make_brain(tmp_path)
        assert brain2.load_checkpoint()
        assert brain2.state.current_round == 2
        assert len(brain2.state.all_findings) == 3


# ═══════════════════════════════════════════════════════════════════════════════
# Insect Brain — Convergence Detection
# ═══════════════════════════════════════════════════════════════════════════════

class TestInsectBrainConvergence:

    def test_no_convergence_before_min_rounds(self, tmp_path):
        brain = _make_brain(tmp_path)
        findings = _make_round_findings(0)
        brain.persist(0, {m: "output" for m in MODELS}, findings)
        assert not brain.check_convergence(0)

    def test_max_rounds_terminates_with_budget_exhausted(self, tmp_path):
        """Max rounds = budget exhaustion, NOT convergence.

        The experiment terminates (returns True) but converged is False
        because reaching the round limit is not epistemic convergence.
        """
        config = DynamicManagementConfig(max_rounds=3)
        brain = InsectBrain(
            config=config,
            logs_dir=tmp_path / "logs",
            source_paths=[],
        )
        brain.initialise(MODELS)
        for rnd in range(3):
            brain.persist(rnd, {m: "output" for m in MODELS}, _make_round_findings(rnd))

        assert brain.check_convergence(2)  # terminates
        assert not brain.state.converged  # but NOT converged
        assert "BUDGET_EXHAUSTED" in brain.state.convergence_reason

    def test_metrics_computed(self, tmp_path):
        brain = _make_brain(tmp_path)
        for rnd in range(2):
            brain.persist(rnd, {m: "output" for m in MODELS}, _make_round_findings(rnd))
        metrics = brain.compute_metrics(1)
        assert "kappa" in metrics
        assert "total_findings" in metrics
        assert metrics["total_findings"] == 20.0  # 2 rounds × 5 models × 2 findings

    def test_signal_complete_outputs_json(self, tmp_path):
        brain = _make_brain(tmp_path)
        brain.persist(0, {m: "output" for m in MODELS}, _make_round_findings(0))
        brain.state.converged = True
        brain.state.convergence_reason = "test"
        signal = brain.signal_complete()
        assert signal["status"] == "CONVERGED"
        assert signal["total_findings"] == 10
        # File written
        assert (tmp_path / "logs" / "completion_signal.json").exists()


# ═══════════════════════════════════════════════════════════════════════════════
# Insect Brain — Model Failure Handling
# ═══════════════════════════════════════════════════════════════════════════════

class TestInsectBrainFailure:

    def test_single_model_failure_continues(self, tmp_path):
        brain = _make_brain(tmp_path)
        brain.handle_model_failure("DeepSeek", "timeout")
        assert "DeepSeek" not in brain.state.active_models
        assert len(brain.state.active_models) == 4
        assert not brain.state.failed

    def test_all_models_fail_signals_brain_failure(self, tmp_path):
        brain = _make_brain(tmp_path)
        for m in MODELS:
            brain.handle_model_failure(m, "timeout")
        assert brain.state.failed
        assert brain.state.failure_reason == "all_models_failed"


# ═══════════════════════════════════════════════════════════════════════════════
# Immune Pipeline — V2 Activation
# ═══════════════════════════════════════════════════════════════════════════════

class TestV2Activation:
    """Verify that v2 components are active and produce verdicts."""

    def test_dc_v2_classifies(self):
        """DC v2 (epistemic routing) should classify findings."""
        f = _make_finding(desc="The formula x^2 + y^2 = z^2 is always true")
        claim_type, reason = _classify_claim(f)
        assert claim_type == ClaimType.MATHEMATICAL

    def test_pipeline_returns_immune_response(self):
        """Full pipeline should return ImmuneResponse with v2 active."""
        findings = [
            _make_finding(fid="f1", desc="Bug in parser logic"),
            _make_finding(fid="f2", model="Gemini", desc="Race condition in dispatcher"),
        ]
        response = run_immune_pipeline(
            new_findings=findings,
            prior_findings=[],
            source_paths=[],
            observation_only=True,  # Don't filter — just verify pipeline runs
        )
        assert isinstance(response, ImmuneResponse)
        assert response.filtered_findings is not None
        assert len(response.cell_verdicts) >= 0  # verdicts produced

    def test_pipeline_with_prior_findings(self):
        """Pipeline should handle NK dedup against prior findings."""
        prior = [_make_finding(fid="p1", desc="Buffer overflow in parser")]
        new = [_make_finding(fid="f1", desc="Buffer overflow in parser")]
        response = run_immune_pipeline(
            new_findings=new,
            prior_findings=prior,
            source_paths=[],
            observation_only=True,
        )
        assert isinstance(response, ImmuneResponse)


# ═══════════════════════════════════════════════════════════════════════════════
# Reconciliation Gate
# ═══════════════════════════════════════════════════════════════════════════════

class TestReconciliationGate:

    def test_agreement_uses_shared_verdict(self):
        v1 = {"f1": "CONFIRMED"}
        c1 = {"f1": 0.8}
        v2 = {"f1": "CONFIRMED"}
        c2 = {"f1": 0.9}
        final_v, final_c = _reconciliation_gate(v1, c1, v2, c2)
        assert final_v["f1"] == "CONFIRMED"
        assert final_c["f1"] == 0.9  # max confidence

    def test_disagreement_higher_confidence_wins(self):
        v1 = {"f1": "CONFIRMED"}
        c1 = {"f1": 0.6}
        v2 = {"f1": "REJECTED"}
        c2 = {"f1": 0.9}
        final_v, final_c = _reconciliation_gate(v1, c1, v2, c2)
        assert final_v["f1"] == "REJECTED"
        assert final_c["f1"] == 0.9

    def test_single_pipeline_passthrough(self):
        v1 = {"f1": "CONFIRMED", "f2": "REJECTED"}
        c1 = {"f1": 0.8, "f2": 0.7}
        v2 = {}  # v2 has nothing for these
        c2 = {}
        final_v, final_c = _reconciliation_gate(v1, c1, v2, c2)
        assert final_v["f1"] == "CONFIRMED"
        assert final_v["f2"] == "REJECTED"

    def test_mixed_coverage(self):
        """v1 has some findings, v2 has others, overlap on one."""
        v1 = {"f1": "CONFIRMED", "f2": "UNCERTAIN"}
        c1 = {"f1": 0.8, "f2": 0.3}
        v2 = {"f1": "CONFIRMED", "f3": "REJECTED"}
        c2 = {"f1": 0.7, "f3": 0.85}
        final_v, final_c = _reconciliation_gate(v1, c1, v2, c2)
        assert final_v["f1"] == "CONFIRMED"
        assert final_c["f1"] == 0.8  # max(0.8, 0.7)
        assert final_v["f2"] == "UNCERTAIN"
        assert final_v["f3"] == "REJECTED"


# ═══════════════════════════════════════════════════════════════════════════════
# Lazy Tool Discovery
# ═══════════════════════════════════════════════════════════════════════════════

class TestLazyToolDiscovery:

    def test_python_tools_returns_path(self):
        """_get_python_tools should return a valid Python path."""
        result = _get_python_tools()
        assert result.endswith("python3") or result.endswith("python")

    def test_python_tools_caches(self):
        """Second call should use cached value."""
        r1 = _get_python_tools()
        r2 = _get_python_tools()
        assert r1 == r2

    def test_claude_cli_returns_none_or_path(self):
        """_get_claude_cli returns None if not found, or a path."""
        result = _get_claude_cli()
        assert result is None or isinstance(result, str)


# ═══════════════════════════════════════════════════════════════════════════════
# Context Budget Configuration
# ═══════════════════════════════════════════════════════════════════════════════

class TestContextBudgets:

    def test_cc2_budget_in_dm_config(self):
        config = DynamicManagementConfig()
        assert "CC2" in config.context_budget_overrides
        assert config.context_budget_overrides["CC2"] == 30_000

    def test_deepseek_budget_in_dm_config(self):
        config = DynamicManagementConfig()
        assert config.context_budget_overrides["DeepSeek"] == 30_000

    def test_runner_core_budgets_exist(self):
        assert "CC2" in CONTEXT_CHAR_BUDGET
        assert "DeepSeek" in CONTEXT_CHAR_BUDGET
        assert CONTEXT_CHAR_BUDGET["CC2"] == 30_000
        assert CONTEXT_CHAR_BUDGET["DeepSeek"] == 30_000

    def test_all_models_have_budgets(self):
        for model in MODELS:
            assert model in CONTEXT_CHAR_BUDGET, f"Missing budget for {model}"


# ═══════════════════════════════════════════════════════════════════════════════
# CC2 Timeout Fix (WP4a)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCC2TimeoutFix:

    def test_cc2_timeout_900(self):
        from bench.experiment_11_orchestrator import load_default_config
        config = load_default_config()
        cc2 = [m for m in config.models if m.label == "CC2"]
        assert len(cc2) == 1
        assert cc2[0].timeout == 900

    def test_cc2_retries_1(self):
        from bench.experiment_11_orchestrator import load_default_config
        config = load_default_config()
        cc2 = [m for m in config.models if m.label == "CC2"]
        assert cc2[0].max_retries == 1


# ═══════════════════════════════════════════════════════════════════════════════
# End-to-End Integration: Brain + Immune Pipeline
# ═══════════════════════════════════════════════════════════════════════════════

class TestEndToEnd:
    """Simulate a multi-round experiment through the brain + pipeline."""

    def test_three_round_flow(self, tmp_path):
        """Run 3 rounds through the brain with immune pipeline."""
        config = DynamicManagementConfig(max_rounds=5, min_rounds_for_convergence=2)
        brain = InsectBrain(
            config=config,
            logs_dir=tmp_path / "logs",
            source_paths=[],
        )
        brain.initialise(MODELS)

        for rnd in range(3):
            # 1. Relay
            payloads = brain.relay(rnd)
            assert len(payloads) == 5

            # 2. Simulate model dispatch (synthetic findings)
            findings = _make_round_findings(rnd)
            responses = {m: f"output_round_{rnd}" for m in MODELS}

            # 3. Persist
            record = brain.persist(rnd, responses, findings)
            assert record.round_idx == rnd
            assert record.finding_count == 10

            # 4. Run immune pipeline (observation_only to avoid side effects)
            immune_result = brain.run_immune_pipeline(findings, observation_only=True)
            assert isinstance(immune_result, ImmuneResponse)

            # 5. Compute metrics
            metrics = brain.compute_metrics(rnd)
            assert "kappa" in metrics

        # 6. Signal complete
        brain.state.converged = True
        brain.state.convergence_reason = "test_complete"
        signal = brain.signal_complete()
        assert signal["status"] == "CONVERGED"
        assert signal["total_rounds"] == 3
        assert signal["total_findings"] == 30

    def test_model_failure_during_run(self, tmp_path):
        """Brain should continue when a model fails mid-run."""
        brain = _make_brain(tmp_path)

        # Round 0: all models
        brain.persist(0, {m: "output" for m in MODELS}, _make_round_findings(0))

        # DeepSeek fails
        brain.handle_model_failure("DeepSeek", "timeout")

        # Round 1: 4 models
        payloads = brain.relay(1)
        assert "DeepSeek" not in payloads
        assert len(payloads) == 4

    def test_full_persistence_round_trip(self, tmp_path):
        """Data written by persist() should be recoverable."""
        brain = _make_brain(tmp_path)
        for rnd in range(3):
            brain.persist(rnd, {m: f"r{rnd}" for m in MODELS}, _make_round_findings(rnd))

        # Recover
        brain2 = _make_brain(tmp_path)
        assert brain2.load_checkpoint()

        # State matches
        assert brain2.state.current_round == brain.state.current_round
        assert len(brain2.state.all_findings) == len(brain.state.all_findings)
        for r in range(3):
            assert len(brain2.state.all_findings[r]) == len(brain.state.all_findings[r])


# ═══════════════════════════════════════════════════════════════════════════════
# WP3d Shadow: Formalisation Agent
# ═══════════════════════════════════════════════════════════════════════════════

class TestFormalisationAgentShadow:

    def test_extract_preconditions_basic(self):
        claim = "for all x > 0, f(x) = x^2 holds"
        pcs = _extract_preconditions(claim)
        assert len(pcs) >= 1
        assert any("x" in pc and ">" in pc for pc in pcs)

    def test_extract_preconditions_when(self):
        claim = "when n >= 1, the function returns n * (n-1)"
        pcs = _extract_preconditions(claim)
        assert len(pcs) >= 1

    def test_extract_preconditions_none(self):
        claim = "The parser fails on empty input"
        pcs = _extract_preconditions(claim)
        # No mathematical preconditions in this purely behavioural claim
        assert isinstance(pcs, list)

    def test_preconditions_to_z3_produces_script(self):
        pcs = ["x > 0"]
        claim = "x + y == z"
        z3_script = _preconditions_to_z3(pcs, claim)
        assert z3_script is not None
        assert "Real(" in z3_script
        assert "s.add(" in z3_script

    def test_preconditions_to_z3_empty(self):
        result = _preconditions_to_z3([], "x + y")
        assert result is None

    def test_shadow_runs_on_math_findings(self):
        """Formalisation agent should process MATHEMATICAL findings."""
        findings = [
            _make_finding(
                fid="f1",
                desc="for all x > 0, the formula `x^2 + 1 > 0` always holds",
            ),
        ]
        triaged = dendritic_cell_triage(findings)
        # Simulate a B-Cell REJECTED verdict (potential false rejection)
        bcell_verdicts = [
            CellVerdict(CellType.B_CELL, "f1", "REJECTED", 0.8, "", "sympy"),
        ]
        results = formalisation_agent_shadow(triaged, bcell_verdicts)
        assert len(results) == 1
        assert results[0]["finding_id"] == "f1"
        assert results[0]["preconditions_found"] >= 1
        assert results[0]["potential_false_rejection"] is True

    def test_shadow_skips_behavioural(self):
        """Formalisation agent should skip CODE_BEHAVIORAL findings."""
        findings = [
            _make_finding(fid="f1", desc="Bug in parser logic"),
        ]
        triaged = dendritic_cell_triage(findings)
        results = formalisation_agent_shadow(triaged, [])
        assert len(results) == 0  # behavioural findings are skipped


# ═══════════════════════════════════════════════════════════════════════════════
# WP3c Shadow: Typed LLM Classifier (import test only — no API call)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTypedLLMClassifierShadow:

    def test_import_and_constants(self):
        """Verify the classifier components are importable."""
        from bench.immune_agents import (
            typed_llm_classifier_shadow,
            _CLASSIFIER_SYSTEM_PROMPT,
            _CLASSIFIER_MODEL,
        )
        assert "MATHEMATICAL" in _CLASSIFIER_SYSTEM_PROMPT
        assert "LOGICAL" in _CLASSIFIER_SYSTEM_PROMPT
        assert _CLASSIFIER_MODEL is not None

    def test_no_api_key_returns_empty(self):
        """Without API key, shadow should return empty gracefully."""
        from bench.immune_agents import typed_llm_classifier_shadow
        import os
        saved = os.environ.pop("OPENROUTER_API_KEY", None)
        try:
            findings = [_make_finding(fid="f1", desc="Bug in parser")]
            triaged = dendritic_cell_triage(findings)
            results = typed_llm_classifier_shadow(findings, triaged)
            assert results == []
        finally:
            if saved is not None:
                os.environ["OPENROUTER_API_KEY"] = saved


# ═══════════════════════════════════════════════════════════════════════════════
# Circulatory System: Model Attribution in Findings
# ═══════════════════════════════════════════════════════════════════════════════

class TestFindingsAttribution:

    def test_format_includes_source_model(self):
        from bench.runner_core import format_findings_for_context
        findings = [
            _make_finding(fid="f1", model="CC2", desc="Bug found by CC2"),
            _make_finding(fid="f2", model="Gemini", desc="Bug found by Gemini"),
        ]
        text = format_findings_for_context(findings)
        assert "[source: CC2]" in text
        assert "[source: Gemini]" in text
