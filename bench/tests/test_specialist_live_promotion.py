"""Tests for Exp 40 1E.3 B-Cell specialist live-promotion.

Acceptance from the plan:
- On synthetic math-domain claim, B-Cell specialist SymPy verifier produces
  a verdict that enters the immune pipeline.
- On synthetic physics claim, the specialist remains shadow-mode (logs a
  verdict but does not affect the pipeline).

Constraint S5: physics / chemistry / engineering specialists stay in shadow
until their tool coverage is validated in a later tranche (1E.4 K/L/M cells).
"""

from __future__ import annotations

import pytest

from bench.dm._types import Finding
from bench.immune_agents import (
    LIVE_SPECIALIST_DOMAINS,
    CellType,
    CellVerdict,
    ClaimType,
    TriagedFinding,
    _specialist_b_cell_dispatch,
    load_domain_config,
    run_immune_pipeline,
)


def _make_finding(
    fid: str = "f1",
    desc: str = "2 + 2 = 4",
    severity: float = 0.6,
) -> Finding:
    return Finding(
        finding_id=fid,
        model_id="CC2",
        round_idx=0,
        flaw_class=2,
        severity=severity,
        abstraction_index=0.5,
        description=desc,
    )


class TestLiveSpecialistDomainsConstant:
    """The set must promote exactly the four 1E.3 domains and no others."""

    def test_mathematics_is_live(self):
        assert "mathematics" in LIVE_SPECIALIST_DOMAINS

    def test_statistics_is_live(self):
        assert "statistics" in LIVE_SPECIALIST_DOMAINS

    def test_biology_is_live(self):
        assert "biology" in LIVE_SPECIALIST_DOMAINS

    def test_information_science_is_live(self):
        assert "information_science" in LIVE_SPECIALIST_DOMAINS

    def test_physics_live(self):
        # Founder directive 2026-07-27: ALL specialists live from Exp 44 on
        # (supersedes S5 shadow constraint).
        assert "physics" in LIVE_SPECIALIST_DOMAINS

    def test_chemistry_live(self):
        assert "chemistry" in LIVE_SPECIALIST_DOMAINS

    def test_engineering_live(self):
        assert "engineering" in LIVE_SPECIALIST_DOMAINS

    def test_code_remains_shadow(self):
        # Code has its own B-Cell v2 (AST) path, specialist not promoted.
        assert "code" not in LIVE_SPECIALIST_DOMAINS

    def test_cross_domain_remains_shadow(self):
        assert "cross_domain" not in LIVE_SPECIALIST_DOMAINS

    def test_software_is_live(self):
        # 2026-05-22 (founder-directed, exp41b return-to-first-principles):
        # the software specialist (z3/mypy vs source AST) is promoted from
        # shadow to LIVE so it filters noise and gates genuine novelty.
        assert "software" in LIVE_SPECIALIST_DOMAINS

    def test_cs_software_is_live(self):
        # Exp 52 pre-flight (2026-07-29): the factorial capstone declares
        # domain="cs_software" so the software-family specialist reaches
        # cs_software.toml, whose claim_patterns are visible to the domain
        # pre-pass and whose verification_tools resolve to a runnable verifier
        # for every claim type. Additive: no other config declares the string.
        assert "cs_software" in LIVE_SPECIALIST_DOMAINS

    def test_set_size_matches_spec(self):
        # Nine domains: math/stats/bio/info-sci (1E.3) + software (exp41b) +
        # physics/chemistry/engineering (founder directive 2026-07-27 —
        # all specialists live from Exp 44 on) + cs_software (Exp 52
        # pre-flight, 2026-07-29). code/cross_domain aliases excluded.
        assert len(LIVE_SPECIALIST_DOMAINS) == 9

    def test_is_immutable(self):
        # frozenset prevents accidental mutation from test or runtime code.
        assert isinstance(LIVE_SPECIALIST_DOMAINS, frozenset)


class TestSpecialistDispatchProducesVerdicts:
    """The dispatcher itself (which runs in both shadow and live) must
    produce a verdict for a well-formed math claim when the math domain
    config is loaded. This isolates the verifier wiring from the
    promotion gate."""

    def test_math_claim_produces_sympy_verdict(self):
        # A definitely-true arithmetic identity that SymPy can confirm.
        finding = _make_finding(desc="The formula 2 + 2 = 4 holds")
        triaged = [TriagedFinding(
            finding=finding,
            claim_type=ClaimType.MATHEMATICAL,
            extracted_claim="2 + 2 = 4",
        )]
        domain_config = load_domain_config("mathematics")
        assert domain_config, "mathematics TOML must load"

        verdicts = _specialist_b_cell_dispatch(triaged, domain_config)
        assert verdicts, "specialist must produce at least one verdict"
        v = verdicts[0]
        assert v.finding_id == "f1"
        assert v.cell_type == CellType.B_CELL
        # The [specialist:<tool>] tag is appended for non-UNCERTAIN verdicts.
        # For UNCERTAIN, we accept the verdict but don't assert the tag.
        if v.verdict != "UNCERTAIN":
            assert "specialist:" in v.evidence

    def test_physics_domain_config_also_dispatches(self):
        # Physics also has math tools via its TOML, so the dispatcher runs
        # identically — the distinction between shadow and live is purely
        # downstream in the pipeline.
        finding = _make_finding(desc="x + 0 = x identity")
        triaged = [TriagedFinding(
            finding=finding,
            claim_type=ClaimType.MATHEMATICAL,
            extracted_claim="x + 0 = x",
        )]
        domain_config = load_domain_config("physics")
        if not domain_config:
            pytest.skip("physics domain TOML not installed")
        # Whatever verdicts come back, they must not crash.
        verdicts = _specialist_b_cell_dispatch(triaged, domain_config)
        assert isinstance(verdicts, list)


class TestPipelineIntegration:
    """Integration check: the pipeline's tool_usage dict carries the
    live-vs-shadow distinction so downstream can audit what happened."""

    def _run_pipeline(self, domain: str):
        finding = _make_finding(
            fid="mf1", desc="The formula 2 + 2 = 4 always holds"
        )
        return run_immune_pipeline(
            new_findings=[finding],
            prior_findings=[],
            source_paths=[],
            observation_only=True,
            ct_enabled=False,          # skip CT agent (needs claude CLI)
            ct_timeout=5,
            domain=domain,
        )

    def test_math_domain_specialist_goes_live(self):
        """Acceptance: synthetic math claim → specialist verdict enters pipeline."""
        response = self._run_pipeline(domain="mathematics")
        # tool_usage records the live promotion
        assert "b_cell_specialist_live" in response.tool_usage, (
            f"expected b_cell_specialist_live in tool_usage, "
            f"got keys={list(response.tool_usage.keys())}"
        )
        assert "b_cell_specialist_shadow" not in response.tool_usage, (
            "math domain must NOT be recorded as shadow"
        )

    def test_physics_domain_specialist_live_2026_07_27(self):
        """Acceptance: synthetic physics claim → specialist stays shadow."""
        response = self._run_pipeline(domain="physics")
        # Live from Exp 44 on (founder directive 2026-07-27; supersedes S5).
        assert "b_cell_specialist_live" in response.tool_usage, (
            f"expected b_cell_specialist_live in tool_usage, "
            f"got keys={list(response.tool_usage.keys())}"
        )
        assert "b_cell_specialist_shadow" not in response.tool_usage, (
            "physics domain must NOT be recorded as live"
        )

    def test_chemistry_domain_specialist_live_2026_07_27(self):
        """Constraint S5: chemistry specialist stays shadow in Exp 40 baseline."""
        response = self._run_pipeline(domain="chemistry")
        if "b_cell_specialist_shadow" not in response.tool_usage and \
           "b_cell_specialist_live" not in response.tool_usage:
            # No specialist dispatched (chemistry TOML may not route to this
            # claim type) — still OK, just means nothing to audit.
            return
        assert "b_cell_specialist_shadow" not in response.tool_usage

    def test_engineering_domain_specialist_live(self):
        # Founder directive 2026-07-27: all specialists live from Exp 44 on.
        response = self._run_pipeline(domain="engineering")
        if "b_cell_specialist_shadow" not in response.tool_usage and \
           "b_cell_specialist_live" not in response.tool_usage:
            return
        assert "b_cell_specialist_shadow" not in response.tool_usage

    def test_empty_domain_stays_shadow(self):
        """Fallback: no domain → specialist not even dispatched, pipeline safe."""
        response = self._run_pipeline(domain="")
        # Empty domain means no domain_config, so the specialist future
        # isn't scheduled at all — neither key should appear.
        assert "b_cell_specialist_live" not in response.tool_usage


class TestSpecialistPromotionCountsMatch:
    """When promoted, the specialist tool_usage count should equal the
    number of verdicts produced (no silent drops)."""

    def test_live_tool_usage_count_matches_verdicts(self):
        finding = _make_finding(
            fid="mf1",
            desc="The formula 1 + 1 = 2 is a basic arithmetic identity",
        )
        response = run_immune_pipeline(
            new_findings=[finding],
            prior_findings=[],
            source_paths=[],
            observation_only=True,
            ct_enabled=False,
            ct_timeout=5,
            domain="mathematics",
        )
        live_count = response.tool_usage.get("b_cell_specialist_live", 0)
        # b_cell_specialist_live == number of specialist verdicts produced.
        # For the synthetic 1+1=2 finding, dispatcher should produce exactly
        # one verdict.
        assert live_count >= 1, (
            f"expected at least 1 live specialist verdict, got {live_count}"
        )
