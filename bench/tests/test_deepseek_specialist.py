"""Tests for Exp 40 1E.12 — DeepSeek R1 as formal-verification specialist.

Acceptance from the plan:
  On a synthetic formal-verification claim, DeepSeek produces a specialist
  verdict that enters the immune pipeline **distinct from its generic
  panel role**.

The load-bearing contracts:
  1. ``_verify_deepseek_formal`` returns a ``CellVerdict`` whose
     ``tool_used`` field is the string ``"deepseek_formal"`` — not the
     bare ``"deepseek"`` used by the panel role — so downstream synthesis
     can tell the specialist verdict apart from a panel finding.
  2. With no ``DEEPSEEK_API_KEY`` environment variable, the verifier
     returns UNCERTAIN gracefully rather than raising — keeping the
     dispatch pipeline flowing on workstations without the key.
  3. The verifier caps confidence at 0.5 regardless of what the model
     claims, so LLM verdicts sit strictly below mechanical proofs in
     any voting scheme.
  4. Response parsing is tolerant of the fenced ```json\\n...\\n``` that
     DeepSeek sometimes wraps JSON in, but strict on the required fields.
     Parse failures degrade to UNCERTAIN, never false CONFIRMED.
  5. The tool is registered in ``tool_manifest.toml`` under the name
     ``deepseek_formal`` with claim_types covering ``logical`` and
     ``mathematical``.
  6. The mathematics domain TOML wires ``deepseek_formal`` AFTER z3 and
     sympy for the ``logical`` claim type, so the dispatch invokes it
     only as a fallback when mechanical verifiers return UNCERTAIN.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from bench.immune_agents import (
    CellType,
    CellVerdict,
    ClaimType,
    TriagedFinding,
    _load_tool_manifest,
    _parse_deepseek_formal_response,
    _specialist_b_cell_dispatch,
    _verify_deepseek_formal,
    load_domain_config,
)
from bench.dm._types import Finding


# ═══════════════════════════════════════════════════════════════════════════
# 1. Response parsing — strict on fields, tolerant on wrapping
# ═══════════════════════════════════════════════════════════════════════════


class TestDeepSeekFormalResponseParsing:
    """The parser must survive real DeepSeek output patterns: code fences,
    leading whitespace, trailing prose. It must refuse to produce dict
    output for malformed inputs."""

    def test_plain_json_object_parsed(self):
        raw = '{"verdict": "CONFIRMED", "reasoning": "ok", "confidence": 0.9}'
        parsed = _parse_deepseek_formal_response(raw)
        assert parsed == {
            "verdict": "CONFIRMED", "reasoning": "ok", "confidence": 0.9,
        }

    def test_fenced_json_parsed(self):
        raw = '```json\n{"verdict": "REJECTED"}\n```'
        parsed = _parse_deepseek_formal_response(raw)
        assert parsed == {"verdict": "REJECTED"}

    def test_fenced_without_language_parsed(self):
        raw = '```\n{"verdict": "UNCERTAIN"}\n```'
        parsed = _parse_deepseek_formal_response(raw)
        assert parsed == {"verdict": "UNCERTAIN"}

    def test_leading_prose_then_json(self):
        raw = 'Here is my analysis:\n{"verdict": "CONFIRMED"}\nEnd.'
        parsed = _parse_deepseek_formal_response(raw)
        assert parsed == {"verdict": "CONFIRMED"}

    def test_empty_string_returns_none(self):
        assert _parse_deepseek_formal_response("") is None

    def test_whitespace_only_returns_none(self):
        assert _parse_deepseek_formal_response("   \n\n  ") is None

    def test_junk_text_returns_none(self):
        assert _parse_deepseek_formal_response("not json at all") is None

    def test_array_returns_none(self):
        # Must be a JSON object, not an array.
        assert _parse_deepseek_formal_response("[1, 2, 3]") is None

    def test_malformed_braces_returns_none(self):
        assert _parse_deepseek_formal_response('{"verdict": "CONFIRMED"') is None


# ═══════════════════════════════════════════════════════════════════════════
# 2. Graceful degradation — missing API key, import failure, network error
# ═══════════════════════════════════════════════════════════════════════════


class TestDeepSeekFormalGracefulDegradation:
    """The specialist lives in a multi-tool dispatch where a raised
    exception would halt the whole pipeline. Every failure path MUST
    produce a valid CellVerdict, never raise."""

    def test_missing_api_key_returns_uncertain(self, monkeypatch):
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        v = _verify_deepseek_formal("x > 0 implies x + 1 > 0")
        assert isinstance(v, CellVerdict)
        assert v.verdict == "UNCERTAIN"
        assert v.confidence == 0.0
        assert v.tool_used == "deepseek_formal"
        assert "DEEPSEEK_API_KEY" in v.evidence

    def test_network_error_returns_uncertain(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")

        def _boom(*args, **kwargs):
            raise RuntimeError("simulated network failure")

        with patch(
            "bench.experiment_11_orchestrator.call_deepseek", side_effect=_boom
        ):
            v = _verify_deepseek_formal("formal claim")
        assert v.verdict == "UNCERTAIN"
        assert v.confidence == 0.0
        assert v.tool_used == "deepseek_formal"
        assert "API error" in v.evidence
        assert "RuntimeError" in v.evidence

    def test_unparseable_response_returns_uncertain(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value="<<< not JSON >>>",
        ):
            v = _verify_deepseek_formal("formal claim")
        assert v.verdict == "UNCERTAIN"
        assert "unparseable" in v.evidence.lower()

    def test_verdict_field_missing_returns_uncertain(self, monkeypatch):
        """Parsed dict without a ``verdict`` key defaults safely."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value='{"reasoning": "I do not know", "confidence": 0.8}',
        ):
            v = _verify_deepseek_formal("formal claim")
        assert v.verdict == "UNCERTAIN"

    def test_invalid_verdict_string_coerced_to_uncertain(self, monkeypatch):
        """The model might hallucinate an out-of-contract verdict value.
        Anything not in {CONFIRMED, REJECTED, UNCERTAIN} must become
        UNCERTAIN rather than slip through."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value='{"verdict": "MAYBE", "confidence": 0.9}',
        ):
            v = _verify_deepseek_formal("formal claim")
        assert v.verdict == "UNCERTAIN"


# ═══════════════════════════════════════════════════════════════════════════
# 3. Happy path — mocked DeepSeek, verify the full verdict shape
# ═══════════════════════════════════════════════════════════════════════════


class TestDeepSeekFormalHappyPath:

    def test_confirmed_verdict_roundtrips(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        response = (
            '{"verdict": "CONFIRMED", '
            '"reasoning": "x + 1 > x for all real x by axiom", '
            '"confidence": 0.4}'
        )
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value=response,
        ):
            v = _verify_deepseek_formal("x + 1 > x")
        assert v.verdict == "CONFIRMED"
        assert v.confidence == pytest.approx(0.4)
        assert "axiom" in v.evidence
        assert v.tool_used == "deepseek_formal"

    def test_rejected_verdict_roundtrips(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        response = (
            '{"verdict": "REJECTED", '
            '"reasoning": "counterexample x=-1 makes x^2 = 1 > 0", '
            '"confidence": 0.45}'
        )
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value=response,
        ):
            v = _verify_deepseek_formal("x^2 <= 0 for all x")
        assert v.verdict == "REJECTED"
        assert "counterexample" in v.evidence

    def test_confidence_capped_at_half(self, monkeypatch):
        """LLM verdicts must not outrank mechanical verdicts. The cap is
        enforced even if the model claims 0.99 confidence."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        response = (
            '{"verdict": "CONFIRMED", "reasoning": "trivial", '
            '"confidence": 0.99}'
        )
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value=response,
        ):
            v = _verify_deepseek_formal("1 = 1")
        assert v.confidence <= 0.5

    def test_negative_confidence_clamped_to_zero(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        response = (
            '{"verdict": "UNCERTAIN", "reasoning": "idk", '
            '"confidence": -0.2}'
        )
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value=response,
        ):
            v = _verify_deepseek_formal("ambiguous claim")
        assert v.confidence >= 0.0

    def test_fenced_response_still_parsed(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        response = (
            '```json\n'
            '{"verdict": "CONFIRMED", "reasoning": "proof by induction", '
            '"confidence": 0.3}\n'
            '```'
        )
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value=response,
        ):
            v = _verify_deepseek_formal("induction claim")
        assert v.verdict == "CONFIRMED"
        assert "induction" in v.evidence


# ═══════════════════════════════════════════════════════════════════════════
# 4. Role distinctness — the specialist tool_used label must NOT collide
#    with the panel-role label, so synthesis can tell them apart.
# ═══════════════════════════════════════════════════════════════════════════


class TestDeepSeekFormalRoleDistinct:

    def test_tool_used_is_deepseek_formal_not_deepseek(self, monkeypatch):
        """Hard contract: the specialist verdict is labelled
        ``deepseek_formal``, never the bare ``deepseek`` used by the
        panel role. Downstream dedup / synthesis relies on this."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")
        with patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value='{"verdict": "CONFIRMED", "confidence": 0.3}',
        ):
            v = _verify_deepseek_formal("claim")
        assert v.tool_used == "deepseek_formal"
        assert v.tool_used != "deepseek"

    def test_evidence_namespaced_deepseek_formal(self, monkeypatch):
        """Evidence string starts with ``deepseek_formal:`` so log greps
        can filter specialist evidence without a false match on the
        panel's ``deepseek`` label."""
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        v = _verify_deepseek_formal("claim")
        assert v.evidence.startswith("deepseek_formal:")


# ═══════════════════════════════════════════════════════════════════════════
# 5. Manifest + domain TOML integration
# ═══════════════════════════════════════════════════════════════════════════


class TestDeepSeekFormalManifestRegistered:

    def test_tool_registered_in_manifest(self):
        manifest = _load_tool_manifest()
        assert "deepseek_formal" in manifest
        entry = manifest["deepseek_formal"]
        assert entry["verifier"] == "_verify_deepseek_formal"
        assert entry["needs_file"] is False
        assert "logical" in entry["claim_types"]

    def test_mathematics_domain_wires_specialist_after_mechanical(self):
        """The TOML list order is load-bearing: z3 / sympy must come
        before ``deepseek_formal`` so the cheaper tools run first and
        DeepSeek is only invoked when both return UNCERTAIN."""
        cfg = load_domain_config("mathematics")
        logical_tools = cfg["immune"]["verification_tools"]["logical"]
        assert "deepseek_formal" in logical_tools
        idx = logical_tools.index("deepseek_formal")
        assert idx > 0, "deepseek_formal should not be first in the list"
        # Specifically: every mechanical tool comes before the LLM.
        for mech in ("z3", "sympy"):
            if mech in logical_tools:
                assert logical_tools.index(mech) < idx, (
                    f"{mech} must come before deepseek_formal"
                )


# ═══════════════════════════════════════════════════════════════════════════
# 6. Dispatch integration — specialist enters the pipeline on logical
#    claims in the mathematics domain when mechanical tools defer.
# ═══════════════════════════════════════════════════════════════════════════


def _mk_triaged_logical(claim: str, fid: str = "F_DS_001") -> TriagedFinding:
    finding = Finding(
        finding_id=fid,
        model_id="Codex",
        round_idx=1,
        flaw_class=2,
        severity=0.6,
        abstraction_index=0.5,
        description=claim,
    )
    return TriagedFinding(
        finding=finding,
        claim_type=ClaimType.LOGICAL,
        extracted_claim=claim,
        is_duplicate=False,
    )


class TestDeepSeekFormalDispatchIntegration:
    """Verify that the specialist dispatch, given a logical claim in the
    mathematics domain, reaches the DeepSeek specialist when mechanical
    verifiers defer. We monkey-patch the mechanical verifiers to return
    UNCERTAIN so the dispatch must fall through to DeepSeek."""

    def test_specialist_verdict_enters_pipeline(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")

        def _mech_uncertain(claim: str) -> CellVerdict:
            return CellVerdict(
                cell_type=CellType.B_CELL, finding_id="", verdict="UNCERTAIN",
                confidence=0.0, evidence="mechanical: no decision",
                tool_used="mechanical_stub", elapsed_s=0.01,
            )

        deepseek_response = (
            '{"verdict": "CONFIRMED", '
            '"reasoning": "reasoning", "confidence": 0.4}'
        )

        cfg = load_domain_config("mathematics")
        triaged = [_mk_triaged_logical(
            "if x is rational then x can be expressed as p/q"
        )]

        with patch(
            "bench.immune_agents._verify_z3", side_effect=_mech_uncertain
        ), patch(
            "bench.immune_agents._verify_sympy", side_effect=_mech_uncertain
        ), patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            return_value=deepseek_response,
        ):
            verdicts = _specialist_b_cell_dispatch(triaged, cfg)

        assert len(verdicts) == 1
        v = verdicts[0]
        assert v.finding_id == "F_DS_001"
        assert v.verdict == "CONFIRMED"
        assert v.tool_used == "deepseek_formal"
        assert "[specialist:deepseek_formal]" in v.evidence

    def test_mechanical_confirm_shortcircuits_before_deepseek(
        self, monkeypatch
    ):
        """If z3 returns CONFIRMED, the dispatch must NOT call DeepSeek.
        This is the cost-control invariant — the expensive LLM only runs
        when the cheap tools cannot decide."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake")

        def _z3_confirmed(claim: str) -> CellVerdict:
            return CellVerdict(
                cell_type=CellType.B_CELL, finding_id="",
                verdict="CONFIRMED", confidence=0.9,
                evidence="z3: proved", tool_used="z3", elapsed_s=0.01,
            )

        cfg = load_domain_config("mathematics")
        triaged = [_mk_triaged_logical("x > 0 implies x + 1 > 0")]

        deepseek_call_count = {"n": 0}

        def _track_deepseek(*args, **kwargs):
            deepseek_call_count["n"] += 1
            return '{"verdict": "CONFIRMED", "confidence": 0.9}'

        with patch(
            "bench.immune_agents._verify_z3", side_effect=_z3_confirmed
        ), patch(
            "bench.experiment_11_orchestrator.call_deepseek",
            side_effect=_track_deepseek,
        ):
            verdicts = _specialist_b_cell_dispatch(triaged, cfg)

        assert len(verdicts) == 1
        assert verdicts[0].tool_used == "z3"
        assert deepseek_call_count["n"] == 0, (
            "DeepSeek must NOT be called when z3 confirms — cost control"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 7. Module constants — guard against silent drift
# ═══════════════════════════════════════════════════════════════════════════


class TestDeepSeekSpecialistConstants:
    """The specialist's cost/latency envelope is encoded in module-level
    constants. Changes here are contract changes and should be reviewed."""

    def test_confidence_cap_is_half(self):
        from bench.immune_agents import _DEEPSEEK_SPECIALIST_CONFIDENCE_CAP
        assert _DEEPSEEK_SPECIALIST_CONFIDENCE_CAP == 0.5

    def test_max_tokens_bounded(self):
        from bench.immune_agents import _DEEPSEEK_SPECIALIST_MAX_TOKENS
        # Keep well below the full DeepSeek 32k budget so cost is capped.
        assert _DEEPSEEK_SPECIALIST_MAX_TOKENS <= 8192

    def test_timeout_bounded(self):
        from bench.immune_agents import _DEEPSEEK_SPECIALIST_TIMEOUT_S
        # A runaway reasoner must not hold up the whole immune pass
        # for more than a couple of minutes.
        assert 30 <= _DEEPSEEK_SPECIALIST_TIMEOUT_S <= 300

    def test_model_id_is_reasoner(self):
        from bench.immune_agents import _DEEPSEEK_SPECIALIST_MODEL_ID
        # The specialist route must target the reasoner — the
        # long-reasoning profile is the whole point of this role.
        assert "reasoner" in _DEEPSEEK_SPECIALIST_MODEL_ID.lower()
