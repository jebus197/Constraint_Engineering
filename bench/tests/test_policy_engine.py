"""Tests for the PolicyEngine (bench/cdsfl_registry/engine.py).

Tests schema loading, parameter queries, provenance tracking, validation,
and policy diffing. All tests run against the real TOML configs in the
cdsfl_registry directory.
"""

import pytest

from bench.cdsfl_registry.engine import (
    PolicyEngine,
    ParameterDef,
    ParameterValue,
    PolicyResult,
    load_schema,
    _flatten_dict,
    _flatten_schema,
    _compute_provenance,
    VALID_TYPES,
    VALID_CLASSES,
    VALID_LAYERS,
    LAYER_ORDER,
)
from bench.cdsfl_registry.registry import (
    HARD_CONSTRAINTS,
    HARD_THRESHOLDS,
    HARD_STRINGS,
    PolicyViolationError,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def engine():
    """Module-scoped engine to avoid reloading schema per test."""
    return PolicyEngine()


# =============================================================================
# Test 1: Schema loading
# =============================================================================

class TestSchemaLoading:
    def test_schema_loads(self, engine):
        assert len(engine.schema) > 0

    def test_all_params_have_valid_types(self, engine):
        for dp, defn in engine.schema.items():
            assert defn.type in VALID_TYPES, f"{dp} has invalid type: {defn.type}"

    def test_all_params_have_valid_class(self, engine):
        for dp, defn in engine.schema.items():
            assert defn.constraint_class in VALID_CLASSES, \
                f"{dp} has invalid class: {defn.constraint_class}"

    def test_all_params_have_valid_layer(self, engine):
        for dp, defn in engine.schema.items():
            assert defn.min_layer in VALID_LAYERS, \
                f"{dp} has invalid min_layer: {defn.min_layer}"

    def test_all_params_have_descriptions(self, engine):
        for dp, defn in engine.schema.items():
            assert defn.description, f"{dp} missing description"

    def test_hard_constraints_covered_in_schema(self, engine):
        """Every HARD bool in registry.py must appear in schema as HARD."""
        for dotpath in HARD_CONSTRAINTS:
            defn = engine.get_schema_for(dotpath)
            assert defn is not None, f"Missing from schema: {dotpath}"
            assert defn.constraint_class == "HARD", \
                f"{dotpath} should be HARD in schema"

    def test_hard_thresholds_covered(self, engine):
        for dotpath in HARD_THRESHOLDS:
            defn = engine.get_schema_for(dotpath)
            assert defn is not None, f"Missing from schema: {dotpath}"
            assert defn.constraint_class == "HARD"

    def test_hard_strings_covered(self, engine):
        for dotpath in HARD_STRINGS:
            defn = engine.get_schema_for(dotpath)
            assert defn is not None, f"Missing from schema: {dotpath}"
            assert defn.constraint_class == "HARD"


# =============================================================================
# Test 2: Parameter counts
# =============================================================================

class TestParameterCounts:
    def test_has_hard_parameters(self, engine):
        counts = engine.parameter_count()
        assert counts["HARD"] > 0

    def test_has_soft_parameters(self, engine):
        counts = engine.parameter_count()
        assert counts["SOFT"] > 0

    def test_total_matches_schema(self, engine):
        counts = engine.parameter_count()
        assert counts["HARD"] + counts["SOFT"] == len(engine.schema)


# =============================================================================
# Test 3: Query — effective policy
# =============================================================================

class TestQuery:
    def test_query_returns_policy_result(self, engine):
        result = engine.query("mathematics")
        assert isinstance(result, PolicyResult)
        assert result.domain == "mathematics"
        assert isinstance(result.effective, dict)

    def test_query_with_model(self, engine):
        result = engine.query("mathematics", model="opus_4_6")
        assert result.model == "opus_4_6"
        # Opus config should add model.name
        assert result.effective.get("model", {}).get("name") == "claude-opus-4-6"

    def test_query_provenance_tracks_layers(self, engine):
        result = engine.query("mathematics", model="opus_4_6")
        # Universal params should be from "universal"
        assert result.provenance["constraints.anti_deference"] == "universal"
        # Model params should be from "model/opus_4_6"
        assert result.provenance.get("model.name") == "model/opus_4_6"

    def test_query_domain_params_tracked(self, engine):
        result = engine.query("mathematics")
        # Mathematics adds dimensional_analysis
        assert result.provenance.get("constraints.dimensional_analysis") == "domain/mathematics"

    def test_query_unknown_domain_still_works(self, engine):
        """Unknown domain gets universal-only policy (with warning)."""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = engine.query("made_up_domain")
        assert isinstance(result.effective, dict)
        # Should still have universal constraints
        assert result.effective["constraints"]["anti_deference"] is True


# =============================================================================
# Test 4: Get single parameter
# =============================================================================

class TestGetParameter:
    def test_universal_parameter(self, engine):
        pv = engine.get_parameter("convergence.v_comp_threshold", "mathematics")
        assert isinstance(pv, ParameterValue)
        assert pv.value == 0.5
        assert pv.source_layer == "universal"
        assert pv.constraint_class == "SOFT"

    def test_hard_parameter(self, engine):
        pv = engine.get_parameter("constraints.anti_deference", "code")
        assert pv.value is True
        assert pv.constraint_class == "HARD"

    def test_domain_override(self, engine):
        pv = engine.get_parameter("convergence.advisory_d_after_round", "cross_domain")
        # cross_domain.toml sets this to 2, overriding universal's 3
        assert pv.value == 2
        assert pv.source_layer == "domain/cross_domain"

    def test_model_parameter(self, engine):
        pv = engine.get_parameter("model.timeout", "mathematics", model="opus_4_6")
        assert pv.value == 180
        assert pv.source_layer == "model/opus_4_6"

    def test_unknown_parameter_raises(self, engine):
        with pytest.raises(KeyError):
            engine.get_parameter("nonexistent.param", "mathematics")


# =============================================================================
# Test 5: List parameters
# =============================================================================

class TestListParameters:
    def test_list_all(self, engine):
        params = engine.list_parameters()
        assert len(params) == len(engine.schema)

    def test_filter_by_section(self, engine):
        params = engine.list_parameters(section="constraints")
        assert all(p.dotpath.startswith("constraints.") for p in params)
        assert len(params) > 0

    def test_filter_by_class(self, engine):
        params = engine.list_parameters(constraint_class="HARD")
        assert all(p.constraint_class == "HARD" for p in params)
        assert len(params) == engine.parameter_count()["HARD"]

    def test_filter_combined(self, engine):
        params = engine.list_parameters(section="constraints", constraint_class="HARD")
        assert all(
            p.dotpath.startswith("constraints.") and p.constraint_class == "HARD"
            for p in params
        )

    def test_filter_returns_empty_for_nonexistent_section(self, engine):
        params = engine.list_parameters(section="nonexistent")
        assert params == []


# =============================================================================
# Test 6: Validation
# =============================================================================

class TestValidation:
    def test_all_configs_valid(self, engine):
        results = engine.validate()
        for name, status in results.items():
            assert status == "ok", f"{name}: {status}"

    def test_validation_includes_schema_coverage(self, engine):
        """Validation should check that schema covers all HARD constraints."""
        results = engine.validate()
        # If schema is complete, no coverage errors
        assert "schema_coverage/hard_bools" not in results
        assert "schema_coverage/hard_thresholds" not in results
        assert "schema_coverage/hard_strings" not in results


# =============================================================================
# Test 7: Policy diff
# =============================================================================

class TestPolicyDiff:
    def test_same_policy_no_diff(self, engine):
        diffs = engine.diff_policies("mathematics", "mathematics",
                                     model_a="opus_4_6", model_b="opus_4_6")
        assert diffs == {}

    def test_different_domains_have_diffs(self, engine):
        diffs = engine.diff_policies("mathematics", "code")
        assert len(diffs) > 0
        # Mathematics has dimensional_analysis, code doesn't
        assert "constraints.dimensional_analysis" in diffs

    def test_different_models_have_diffs(self, engine):
        diffs = engine.diff_policies("mathematics", "mathematics",
                                     model_a="opus_4_6", model_b="deepseek_v3")
        assert len(diffs) > 0
        # Different timeouts
        assert "model.timeout" in diffs


# =============================================================================
# Test 8: Helper functions
# =============================================================================

class TestHelpers:
    def test_flatten_dict_simple(self):
        d = {"a": {"b": 1, "c": 2}, "d": 3}
        flat = _flatten_dict(d)
        assert flat == {"a.b": 1, "a.c": 2, "d": 3}

    def test_flatten_dict_nested(self):
        d = {"a": {"b": {"c": 1}}}
        flat = _flatten_dict(d)
        assert flat == {"a.b.c": 1}

    def test_flatten_dict_empty(self):
        assert _flatten_dict({}) == {}

    def test_provenance_universal_only(self):
        prov = _compute_provenance("mathematics", None, None)
        # All should come from universal or domain
        assert "constraints.anti_deference" in prov
        assert prov["constraints.anti_deference"] == "universal"

    def test_provenance_with_domain(self):
        prov = _compute_provenance("mathematics", None, None)
        # Mathematics domain adds these
        assert prov.get("constraints.dimensional_analysis") == "domain/mathematics"


# =============================================================================
# Test 9: ParameterDef frozen
# =============================================================================

class TestParameterDefFrozen:
    def test_parameter_def_is_immutable(self, engine):
        defn = engine.get_schema_for("constraints.anti_deference")
        assert defn is not None
        with pytest.raises(AttributeError):
            defn.type = "int"  # type: ignore[misc]


# =============================================================================
# Test 10: Edge cases
# =============================================================================

class TestEdgeCases:
    def test_get_schema_for_missing(self, engine):
        assert engine.get_schema_for("nonexistent.param") is None

    def test_query_with_task_id_no_file(self, engine):
        """Task ID with no matching file should still produce a valid policy."""
        result = engine.query("mathematics", task_id="nonexistent-task")
        assert isinstance(result.effective, dict)
        assert result.effective["constraints"]["anti_deference"] is True

    def test_query_with_nonexistent_model_raises(self, engine):
        """Missing model config should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            engine.query("mathematics", model="nonexistent_model")
