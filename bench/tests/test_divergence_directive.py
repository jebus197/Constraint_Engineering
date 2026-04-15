"""Tests for bench/dm/_divergence.py — the §18 divergence directive validator.

The divergence directive is CDSFL's bold-conjectures arm: every non-trivial
finding must supply either ≥1 alternative on a named dimension (mechanism,
assumption, scope, timescale, tradeoff) or a scoped null-alternative
justification. This suite pins the observable behaviour:

* ALLOWED_DIMENSIONS canonical set + synonym normalisation
* Alternative header parsing (inline tag, dash tag, follow-up Dimension line)
* Jaccard isomorphism scoring bounds and symmetry
* validate_alternative admissibility gates (dimension, length, isomorphism)
* Null-justification parsing and minimum-length gate
* build_divergence_record end-to-end compliance logic
* divergence_penalty_multiplier tiers
* Disabled-directive bypass
* Config loading from TOML-shaped dict

Reference: cdsfl_operational.md §18, universal.toml [divergence],
schema.toml [divergence.*].

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_divergence_directive.py -v
"""

from __future__ import annotations

import os
import sys

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._divergence import (
    ALLOWED_DIMENSIONS,
    AlternativeRecord,
    DivergenceConfig,
    DivergenceRecord,
    build_divergence_record,
    divergence_config_from_dict,
    divergence_penalty_multiplier,
    parse_alternative_block,
    parse_null_justification_block,
    score_isomorphism,
    validate_alternative,
    validate_null_justification,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


PRIMARY_TEXT = (
    "Use conjugate gradient descent with Polak-Ribiere updates and "
    "Armijo backtracking line search."
)


def _alt_with_dim_inline(dim: str, body: str) -> str:
    return f"Alternative 1 (dimension: {dim})\n{body}\n"


def _alt_with_dim_dash(dim: str, body: str) -> str:
    return f"Alternative — dimension: {dim}\n{body}\n"


def _alt_with_followup_dim(dim: str, body: str) -> str:
    return f"Alternative:\nDimension: {dim}\n{body}\n"


def _null_block(body: str) -> str:
    return f"No alternative found:\n{body}\n"


# ═══════════════════════════════════════════════════════════════════════════════
# TestAllowedDimensions
# ═══════════════════════════════════════════════════════════════════════════════


class TestAllowedDimensions:
    """The five canonical dimensions are fixed and synonyms map onto them."""

    def test_canonical_set_is_five(self):
        assert ALLOWED_DIMENSIONS == (
            "mechanism",
            "assumption",
            "scope",
            "timescale",
            "tradeoff",
        )

    def test_each_canonical_name_accepted(self):
        for dim in ALLOWED_DIMENSIONS:
            raw = _alt_with_dim_inline(dim, "Some alternative text differing substantially.")
            records = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
            assert len(records) == 1, f"dimension {dim!r} did not parse"
            assert records[0].dimension == dim

    def test_synonym_plural_normalises(self):
        # "mechanisms" → "mechanism"
        raw = _alt_with_dim_inline("mechanisms", "Newton method replacing CG.")
        records = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert records[0].dimension == "mechanism"

    def test_synonym_premise_maps_to_assumption(self):
        raw = _alt_with_dim_inline("premise", "Assume convex not merely Lipschitz.")
        records = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert records[0].dimension == "assumption"

    def test_unknown_dimension_is_none(self):
        raw = _alt_with_dim_inline("flavour", "Something unrelated.")
        records = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert records[0].dimension is None

    def test_hyphenated_variant_normalises(self):
        # "trade-off" → "tradeoff"
        raw = _alt_with_dim_inline("trade-off", "Accept slower convergence for lower memory.")
        records = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert records[0].dimension == "tradeoff"


# ═══════════════════════════════════════════════════════════════════════════════
# TestParseAlternativeBlock
# ═══════════════════════════════════════════════════════════════════════════════


class TestParseAlternativeBlock:
    """Header tolerance and body capture across several common formats."""

    def test_empty_text_yields_empty_list(self):
        assert parse_alternative_block("", "f1", PRIMARY_TEXT) == []

    def test_no_header_yields_empty_list(self):
        text = "Just some prose with no alternative header at all."
        assert parse_alternative_block(text, "f1", PRIMARY_TEXT) == []

    def test_inline_parenthetical_tag(self):
        raw = "Alternative (dimension: mechanism)\nNewton-Raphson replacement.\n"
        recs = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert len(recs) == 1
        assert recs[0].dimension == "mechanism"
        assert "Newton" in recs[0].alternative_text

    def test_inline_bracket_tag(self):
        raw = "Alternative [dim: scope]\nNarrow to convex problems only.\n"
        recs = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert recs[0].dimension == "scope"

    def test_dash_dimension_header(self):
        raw = "Alternative — dimension: assumption\nDrop Lipschitz continuity assumption.\n"
        recs = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert recs[0].dimension == "assumption"

    def test_followup_dimension_line(self):
        raw = "Alternative:\nDimension: timescale\nAsymptotic analysis only, ignore transient.\n"
        recs = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert recs[0].dimension == "timescale"
        # Dimension line must be stripped from body so it does not inflate
        # isomorphism scoring.
        assert "Dimension:" not in recs[0].alternative_text

    def test_multiple_alternatives_one_finding(self):
        raw = (
            "Alternative 1 (dimension: mechanism)\nNewton method.\n\n"
            "Alternative 2 (dimension: assumption)\nAssume strong convexity.\n"
        )
        recs = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert len(recs) == 2
        assert {r.dimension for r in recs} == {"mechanism", "assumption"}

    def test_bold_markdown_header_accepted(self):
        raw = "**Alternative (dimension: tradeoff)**\nLower precision for lower latency.\n"
        recs = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert len(recs) == 1
        assert recs[0].dimension == "tradeoff"

    def test_heading_hash_accepted(self):
        raw = "### Alternative 1 (dimension: scope)\nApply only in R^n with n<100.\n"
        recs = parse_alternative_block(raw, "f1", PRIMARY_TEXT)
        assert len(recs) == 1
        assert recs[0].dimension == "scope"


# ═══════════════════════════════════════════════════════════════════════════════
# TestIsomorphismScoring
# ═══════════════════════════════════════════════════════════════════════════════


class TestIsomorphismScoring:
    """Jaccard behaviour: bounds, symmetry, extreme cases."""

    def test_identical_text_scores_one(self):
        assert score_isomorphism("Newton method here.", "Newton method here.") == 1.0

    def test_disjoint_vocab_scores_zero(self):
        # Force disjoint meaningful tokens; stopwords filtered.
        a = "Newton Raphson Hessian quadratic convergence"
        b = "Armijo backtracking Wolfe stepsize heuristic"
        assert score_isomorphism(a, b) == 0.0

    def test_symmetry(self):
        a = "gradient descent with momentum"
        b = "stochastic momentum descent"
        assert score_isomorphism(a, b) == score_isomorphism(b, a)

    def test_both_empty_returns_one(self):
        # Two empty strings are trivially identical under Jaccard convention.
        assert score_isomorphism("", "") == 1.0

    def test_one_empty_returns_zero(self):
        assert score_isomorphism("Newton method", "") == 0.0
        assert score_isomorphism("", "Newton method") == 0.0

    def test_partial_overlap_in_unit_interval(self):
        a = "conjugate gradient descent Polak Ribiere"
        b = "conjugate gradient descent with Fletcher Reeves"
        score = score_isomorphism(a, b)
        assert 0.0 < score < 1.0

    def test_stopwords_do_not_inflate_score(self):
        # Pure stopword text should tokenise to empty and return the
        # "both empty" convention rather than a spurious perfect match
        # against arbitrary content.
        stopword_only = "the a an and or but"
        content = "Newton Raphson Hessian"
        assert score_isomorphism(stopword_only, content) == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# TestValidateAlternative
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidateAlternative:
    """Admissibility gates: dimension, length, isomorphism threshold."""

    def test_valid_alternative_admissible(self):
        alt = AlternativeRecord(
            primary_finding_id="f1",
            alternative_text="Newton-Raphson with Hessian storage.",
            dimension="mechanism",
            isomorphism_score=0.2,
        )
        ok, reasons = validate_alternative(alt)
        assert ok is True
        assert reasons == []
        assert alt.admissible is True

    def test_missing_dimension_rejected(self):
        alt = AlternativeRecord(
            primary_finding_id="f1",
            alternative_text="Some alternative.",
            dimension=None,
            isomorphism_score=0.1,
        )
        ok, reasons = validate_alternative(alt)
        assert ok is False
        assert any("dimension" in r for r in reasons)

    def test_isomorphic_alternative_rejected(self):
        alt = AlternativeRecord(
            primary_finding_id="f1",
            alternative_text="clone of primary",
            dimension="mechanism",
            isomorphism_score=0.95,
        )
        ok, reasons = validate_alternative(alt)
        assert ok is False
        assert any("cosmetic_isomorphism" in r for r in reasons)

    def test_over_length_rejected(self):
        long_body = "x" * 5000
        alt = AlternativeRecord(
            primary_finding_id="f1",
            alternative_text=long_body,
            dimension="mechanism",
            isomorphism_score=0.0,
        )
        cfg = DivergenceConfig(max_chars_per_alternative=2000)
        ok, reasons = validate_alternative(alt, cfg)
        assert ok is False
        assert any("exceeds_max_chars" in r for r in reasons)

    def test_multiple_failures_all_reported(self):
        alt = AlternativeRecord(
            primary_finding_id="f1",
            alternative_text="",
            dimension=None,
            isomorphism_score=0.99,
        )
        ok, reasons = validate_alternative(alt)
        assert ok is False
        # At minimum: empty body + missing dimension. Isomorphism on an empty
        # body is vacuous here but the gate is independent.
        assert any("empty_alternative_body" in r for r in reasons)
        assert any("dimension" in r for r in reasons)


# ═══════════════════════════════════════════════════════════════════════════════
# TestParseNullJustification
# ═══════════════════════════════════════════════════════════════════════════════


class TestParseNullJustification:
    """Null-alternative block extraction and length gating."""

    def test_no_null_block_returns_none(self):
        assert parse_null_justification_block("plain text, no null header") is None

    def test_empty_text_returns_none(self):
        assert parse_null_justification_block("") is None

    def test_basic_null_block_extracted(self):
        body = (
            "Searched across mechanism, assumption, scope, timescale, tradeoff. "
            "No candidate survived the isomorphism check against the primary."
        )
        raw = _null_block(body)
        result = parse_null_justification_block(raw)
        assert result is not None
        assert "mechanism" in result
        assert "isomorphism" in result

    def test_alternate_header_forms_accepted(self):
        for header in ("Null alternative", "No distinct alternative", "Alternative search result"):
            raw = f"{header}:\nScope was exhaustively searched.\n"
            assert parse_null_justification_block(raw) is not None

    def test_validate_null_ok(self):
        body = "x" * 100
        ok, reasons = validate_null_justification(body)
        assert ok is True
        assert reasons == []

    def test_validate_null_too_short(self):
        body = "too short"
        ok, reasons = validate_null_justification(body)
        assert ok is False
        assert any("too_short" in r for r in reasons)

    def test_validate_null_missing(self):
        ok, reasons = validate_null_justification(None)
        assert ok is False
        assert any("missing" in r for r in reasons)


# ═══════════════════════════════════════════════════════════════════════════════
# TestBuildDivergenceRecord
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildDivergenceRecord:
    """End-to-end compliance: what the pipeline actually reads."""

    def test_valid_alt_compliant(self):
        raw = _alt_with_dim_inline(
            "mechanism",
            "Replace CG with truncated-Newton using matrix-vector Hessian products only."
        )
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        assert rec.compliant is True
        assert len(rec.alternatives) == 1
        assert rec.alternatives[0].admissible is True
        assert rec.failure_reasons == []

    def test_null_only_compliant(self):
        body = (
            "Searched mechanism (only CG-class converges at required rate), "
            "assumption (Lipschitz is minimal), scope (problem is fixed R^n), "
            "timescale (single regime), tradeoff (memory floor is binding). "
            "No admissible alternative exists under these constraints."
        )
        raw = _null_block(body)
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        assert rec.compliant is True
        assert rec.null_justification is not None
        assert len(rec.null_justification) >= 60

    def test_isomorphic_alt_non_compliant(self):
        # Alternative text identical to primary → iso=1.0 → rejected.
        raw = _alt_with_dim_inline("mechanism", PRIMARY_TEXT)
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        assert rec.compliant is False
        assert any(
            "cosmetic_isomorphism" in r for r in rec.alternatives[0].rejection_reasons
        )

    def test_no_alt_no_null_non_compliant(self):
        rec = build_divergence_record("f1", PRIMARY_TEXT, "just the primary")
        assert rec.compliant is False
        assert "no_alternative_or_null_block" in rec.failure_reasons

    def test_alt_missing_dimension_non_compliant(self):
        raw = "Alternative:\nNewton method with explicit Hessian.\n"
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        assert rec.compliant is False
        # Dimension is None → admissibility fails with missing_or_invalid_dimension.
        assert len(rec.alternatives) == 1
        assert rec.alternatives[0].admissible is False

    def test_too_short_null_non_compliant(self):
        raw = "No alternative found:\nNone.\n"
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        assert rec.compliant is False
        assert any("null:" in r for r in rec.failure_reasons)

    def test_multiple_alternatives_one_admissible_compliant(self):
        raw = (
            "Alternative 1 (dimension: mechanism)\n"
            "Replace CG with truncated-Newton using matvec Hessian products only.\n\n"
            "Alternative 2:\n"
            "Some other vague suggestion without a dimension.\n"
        )
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        # With default min_alternatives=1, one admissible alternative is enough.
        assert rec.compliant is True
        admissible = [a for a in rec.alternatives if a.admissible]
        assert len(admissible) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TestDivergencePenalty
# ═══════════════════════════════════════════════════════════════════════════════


class TestDivergencePenalty:
    """Penalty multiplier tiers per the §18 design."""

    def test_compliant_no_penalty(self):
        raw = _alt_with_dim_inline(
            "mechanism",
            "Truncated-Newton with matrix-vector Hessian products.",
        )
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        assert divergence_penalty_multiplier(rec) == 1.0

    def test_isomorphic_only_double_penalty(self):
        raw = _alt_with_dim_inline("mechanism", PRIMARY_TEXT)
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        assert divergence_penalty_multiplier(rec) == 0.60

    def test_no_engagement_hard_penalty(self):
        rec = build_divergence_record("f1", PRIMARY_TEXT, "just primary")
        assert divergence_penalty_multiplier(rec) == 0.70

    def test_engaged_but_failed_soft_penalty(self):
        # Alternative present but missing dimension → soft penalty.
        raw = "Alternative:\nNewton method with Hessian storage.\n"
        rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
        assert rec.compliant is False
        assert divergence_penalty_multiplier(rec) == 0.85

    def test_penalty_always_in_unit_interval(self):
        cases = [
            "just primary",
            _alt_with_dim_inline("mechanism", PRIMARY_TEXT),  # iso
            _alt_with_dim_inline("mechanism", "Truncated Newton."),  # ok
            "Alternative:\nNewton.\n",  # missing dim
        ]
        for raw in cases:
            rec = build_divergence_record("f1", PRIMARY_TEXT, raw)
            p = divergence_penalty_multiplier(rec)
            assert 0.0 < p <= 1.0, f"penalty {p} out of range for: {raw!r}"


# ═══════════════════════════════════════════════════════════════════════════════
# TestDisabledDirective
# ═══════════════════════════════════════════════════════════════════════════════


class TestDisabledDirective:
    """When the directive is off the pipeline must see a compliant neutral record."""

    def test_disabled_yields_compliant_empty_record(self):
        cfg = DivergenceConfig(enabled=False)
        rec = build_divergence_record("f1", PRIMARY_TEXT, "anything or nothing", cfg)
        assert rec.compliant is True
        assert rec.alternatives == []
        assert rec.null_justification is None

    def test_disabled_penalty_is_identity(self):
        cfg = DivergenceConfig(enabled=False)
        rec = build_divergence_record("f1", PRIMARY_TEXT, "anything", cfg)
        assert divergence_penalty_multiplier(rec, cfg) == 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# TestConfigFromDict
# ═══════════════════════════════════════════════════════════════════════════════


class TestConfigFromDict:
    """TOML → DivergenceConfig loading helper."""

    def test_empty_dict_yields_disabled(self):
        cfg = divergence_config_from_dict({})
        assert cfg.enabled is False

    def test_none_yields_disabled(self):
        cfg = divergence_config_from_dict(None)
        assert cfg.enabled is False

    def test_full_payload_loaded(self):
        payload = {
            "enabled": True,
            "min_alternatives": 2,
            "max_chars_per_alternative": 1500,
            "mode": "advisory",
            "isomorphism_threshold": 0.75,
            "null_justification_min_chars": 80,
        }
        cfg = divergence_config_from_dict(payload)
        assert cfg.enabled is True
        assert cfg.min_alternatives == 2
        assert cfg.max_chars_per_alternative == 1500
        assert cfg.mode == "advisory"
        assert cfg.isomorphism_threshold == 0.75
        assert cfg.null_justification_min_chars == 80

    def test_partial_payload_uses_defaults(self):
        cfg = divergence_config_from_dict({"enabled": True})
        assert cfg.enabled is True
        assert cfg.min_alternatives == 1  # default
        assert cfg.max_chars_per_alternative == 2000  # default
