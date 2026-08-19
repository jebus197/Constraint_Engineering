"""Tests for bench/dm/_feedback.py — the schema-to-model feedback channel.

Feedback closes the loop between the schema's round-K judgment (B-Cell
verdicts, FFAFP admissibility, near-duplicate detection, R_k validation)
and round K+1's prompt. These tests pin the observable behaviour:

* FindingFeedback priority ordering and action selection
* build_feedback_records aggregation from four independent signal sources
* build_feedback_sections top-K cap, overflow accounting, max-chars cap
* parse_admissibility_block format tolerance (σ/sigma, case, separators)
* Defensive handling of unknown finding_ids, missing inputs, bad floats

Reference: cdsfl_operational.md §17, universal.toml [feedback_channel].

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_feedback_channel.py -v
"""

from __future__ import annotations

import os
import sys

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._feedback import (
    ADMISSIBILITY_GATES,
    FindingFeedback,
    build_feedback_records,
    build_feedback_sections,
    parse_admissibility_block,
)
from bench.dm._types import Finding
from bench.immune_agents import CellType, CellVerdict, ImmuneResponse


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


def _mk_finding(fid: str, model: str = "claude", severity: float = 0.7) -> Finding:
    """Minimal Finding fixture — only the fields the feedback channel touches."""
    return Finding(
        finding_id=fid,
        model_id=model,
        round_idx=1,
        flaw_class=2,
        severity=severity,
        abstraction_index=0.5,
        description=f"test finding {fid}",
    )


def _mk_verdict(
    fid: str,
    verdict: str = "REJECTED",
    tool: str = "sympy",
    evidence: str = "formula does not simplify as claimed",
) -> CellVerdict:
    """Minimal CellVerdict fixture."""
    return CellVerdict(
        cell_type=CellType.B_CELL,
        finding_id=fid,
        verdict=verdict,
        confidence=0.9,
        evidence=evidence,
        tool_used=tool,
    )


def _mk_immune_response(
    *,
    cell_verdicts: dict | None = None,
    final_verdicts: dict | None = None,
) -> ImmuneResponse:
    """Minimal ImmuneResponse fixture — only fields the feedback channel reads."""
    return ImmuneResponse(
        triaged=[],
        cell_verdicts=cell_verdicts or {},
        final_verdicts=final_verdicts or {},
        final_confidences={},
        filtered_findings=[],
        rejected_findings=[],
        rejection_rate=0.0,
        autoimmune_flag=False,
        stage_timings={},
        tool_usage={},
        observation_only=False,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 1. FindingFeedback — priority_score and action
# ═══════════════════════════════════════════════════════════════════════════════


class TestPriorityAndAction:
    def test_action_ordering_refutation_wins(self):
        rec = FindingFeedback(
            finding_id="f1",
            model_origin="claude",
            severity_claimed=0.5,
            final_verdict="REJECTED",
            refutations=[("sympy", "REJECTED", "counterexample found")],
            admissibility_failures=["S_min"],
            duplicates=[("f0", 0.95)],
            rk_discrepancy=(0.8, 0.2),
        )
        assert rec.action == "RECALCULATE"

    def test_action_admissibility_when_no_refutation(self):
        rec = FindingFeedback(
            finding_id="f1",
            model_origin="claude",
            severity_claimed=0.5,
            final_verdict="UNCERTAIN",
            admissibility_failures=["d_tool", "q_retest"],
        )
        assert rec.action == "ADD_ADMISSIBILITY_OR_WITHDRAW"

    def test_action_duplicate_when_no_refutation_or_admissibility(self):
        rec = FindingFeedback(
            finding_id="f1",
            model_origin="claude",
            severity_claimed=0.5,
            final_verdict="UNCERTAIN",
            duplicates=[("f0", 0.88)],
        )
        assert rec.action == "DIFFERENTIATE_OR_WITHDRAW"

    def test_action_rk_last(self):
        rec = FindingFeedback(
            finding_id="f1",
            model_origin="claude",
            severity_claimed=0.5,
            final_verdict="UNCERTAIN",
            rk_discrepancy=(0.9, 0.4),
        )
        assert rec.action == "RECALIBRATE_RK"

    def test_action_none_when_no_flags(self):
        rec = FindingFeedback(
            finding_id="f1",
            model_origin="claude",
            severity_claimed=0.5,
            final_verdict="CONFIRMED",
        )
        assert rec.action == "NONE"

    def test_priority_refutation_beats_admissibility_beats_duplicate_beats_rk(self):
        refuted = FindingFeedback(
            finding_id="a", model_origin="m", severity_claimed=0.0,
            final_verdict="REJECTED",
            refutations=[("sympy", "REJECTED", "x")],
        )
        admissibility = FindingFeedback(
            finding_id="b", model_origin="m", severity_claimed=0.0,
            final_verdict="UNCERTAIN",
            admissibility_failures=list(ADMISSIBILITY_GATES),  # all 5 failed
        )
        duplicate = FindingFeedback(
            finding_id="c", model_origin="m", severity_claimed=0.0,
            final_verdict="UNCERTAIN",
            duplicates=[("prior", 1.0)],  # max similarity
        )
        rk = FindingFeedback(
            finding_id="d", model_origin="m", severity_claimed=0.0,
            final_verdict="UNCERTAIN",
            rk_discrepancy=(1.0, 0.0),  # max delta
        )
        # Refutation gets +3.0; 5×admissibility gets +4.0. Admissibility
        # can outscore a single refutation when many gates fail — this is
        # intentional (many failed gates signals a structurally broken
        # finding). Check the descending-order invariant that was intended:
        # refutation > duplicate > rk, and admissibility scales with count.
        assert refuted.priority_score() > duplicate.priority_score()
        # INVARIANT CHANGED 2026-08-19: was `duplicate > rk`.
        #
        # That ordering was deliberate and is recorded above, but it was set
        # before anyone knew the duplicate detector was flagging 97% of pairs.
        # CC2's audit measured the consequence: the `R_k INCONSISTENT` record
        # fired in 20 of 170 files in exp44 against a 31.7% FAIL rate, because
        # every finding carried a duplicate flag worth >= 1.4 and R_k's
        # `min(1.0, |delta|)` scored ~0.35.
        #
        # Repairing the cosine map does NOT fix this on its own, and simulation
        # shows it makes the specific problem WORSE: once duplicates are rare
        # (21.4%) they stop being a constant and start discriminating, so the
        # minority carrying a duplicate flag outrank every R_k failure. Fraction
        # of R_k-failing findings reaching the prompt: 65.8% before the clamp,
        # 46.3% after it under the old weights, 66.4% after it under these.
        #
        # A FAIL means the model's own arithmetic does not close. That is
        # strictly more damning than a similarity score, so it now sits ABOVE
        # near-duplicate (2.0) and BELOW a refutation (3.0).
        assert rk.priority_score() > duplicate.priority_score()
        # The 5-gate case is an edge — document it explicitly so future
        # changes don't silently flip it:
        assert admissibility.priority_score() > refuted.priority_score()
        # Single-gate admissibility should NOT beat refutation.
        single_admissibility = FindingFeedback(
            finding_id="e", model_origin="m", severity_claimed=0.0,
            final_verdict="UNCERTAIN",
            admissibility_failures=["S_min"],
        )
        assert refuted.priority_score() > single_admissibility.priority_score()

    def test_priority_severity_is_tiebreaker(self):
        hi = FindingFeedback(
            finding_id="a", model_origin="m", severity_claimed=1.0,
            final_verdict="REJECTED",
            refutations=[("sympy", "REJECTED", "x")],
        )
        lo = FindingFeedback(
            finding_id="b", model_origin="m", severity_claimed=0.1,
            final_verdict="REJECTED",
            refutations=[("sympy", "REJECTED", "x")],
        )
        assert hi.priority_score() > lo.priority_score()

    def test_priority_rk_delta_capped_at_one(self):
        # A FAIL-sized delta (> 0.05) now scores a flat 2.5 - see the invariant
        # note above. The CAP still applies below that: a sub-threshold delta
        # must not be inflated, so it stays `min(1.0, |delta|)`.
        capped = FindingFeedback(
            finding_id="a", model_origin="m", severity_claimed=0.0,
            final_verdict="UNCERTAIN",
            rk_discrepancy=(10.0, 0.0),  # absurd delta -> a FAIL
        )
        assert capped.priority_score() == pytest.approx(2.5)

        # Below the FAIL threshold the old cap behaviour is preserved.
        small = FindingFeedback(
            finding_id="b", model_origin="m", severity_claimed=0.0,
            final_verdict="UNCERTAIN",
            rk_discrepancy=(0.52, 0.50),  # delta 0.02, under the 0.05 FAIL line
        )
        assert small.priority_score() == pytest.approx(0.02)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. build_feedback_records
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildFeedbackRecords:
    def test_empty_inputs_yield_empty_list(self):
        records = build_feedback_records(
            round_idx=1,
            findings=[],
            immune_result=_mk_immune_response(),
        )
        assert records == []

    def test_refutation_produces_record(self):
        f1 = _mk_finding("f1")
        ir = _mk_immune_response(
            cell_verdicts={"f1": [_mk_verdict("f1")]},
            final_verdicts={"f1": "REJECTED"},
        )
        records = build_feedback_records(
            round_idx=1,
            findings=[f1],
            immune_result=ir,
        )
        assert len(records) == 1
        rec = records[0]
        assert rec.finding_id == "f1"
        assert rec.model_origin == "claude"
        assert rec.final_verdict == "REJECTED"
        assert len(rec.refutations) == 1
        assert rec.refutations[0][0] == "sympy"
        assert rec.action == "RECALCULATE"

    def test_confirmed_verdict_without_rejections_is_silent(self):
        """A finding the pipeline CONFIRMED — with only CONFIRMED verdicts —
        should not generate feedback. No error to correct."""
        f1 = _mk_finding("f1")
        confirmed_verdict = _mk_verdict("f1", verdict="CONFIRMED")
        ir = _mk_immune_response(
            cell_verdicts={"f1": [confirmed_verdict]},
            final_verdicts={"f1": "CONFIRMED"},
        )
        records = build_feedback_records(
            round_idx=1,
            findings=[f1],
            immune_result=ir,
        )
        assert records == []

    def test_unknown_finding_id_does_not_crash(self):
        """cell_verdicts may reference IDs not in findings (stale, filtered).
        Builder must skip silently rather than KeyError."""
        f1 = _mk_finding("f1")
        ir = _mk_immune_response(
            cell_verdicts={"ghost_id": [_mk_verdict("ghost_id")]},
            final_verdicts={"ghost_id": "REJECTED"},
        )
        records = build_feedback_records(
            round_idx=1,
            findings=[f1],
            immune_result=ir,
        )
        assert records == []

    def test_admissibility_failures_attach_to_existing_record(self):
        f1 = _mk_finding("f1")
        ir = _mk_immune_response(
            cell_verdicts={"f1": [_mk_verdict("f1")]},
            final_verdicts={"f1": "REJECTED"},
        )
        records = build_feedback_records(
            round_idx=1,
            findings=[f1],
            immune_result=ir,
            admissibility_failures={"f1": ["S_min", "d_tool"]},
        )
        assert len(records) == 1
        assert records[0].admissibility_failures == ["S_min", "d_tool"]
        assert records[0].refutations  # still present

    def test_admissibility_only_creates_new_record(self):
        """A finding with no refutation but a failed gate should still be
        flagged — models must supply the block or withdraw."""
        f1 = _mk_finding("f1")
        ir = _mk_immune_response()  # no verdicts
        records = build_feedback_records(
            round_idx=1,
            findings=[f1],
            immune_result=ir,
            admissibility_failures={"f1": ["q_retest"]},
        )
        assert len(records) == 1
        assert records[0].refutations == []
        assert records[0].admissibility_failures == ["q_retest"]
        assert records[0].action == "ADD_ADMISSIBILITY_OR_WITHDRAW"

    def test_empty_admissibility_failures_list_is_ignored(self):
        """An empty list means 'all 5 gates passed' — no feedback needed."""
        f1 = _mk_finding("f1")
        records = build_feedback_records(
            round_idx=1,
            findings=[f1],
            immune_result=_mk_immune_response(),
            admissibility_failures={"f1": []},
        )
        assert records == []

    def test_duplicates_produce_records(self):
        f1 = _mk_finding("f1")
        f2 = _mk_finding("f2")
        records = build_feedback_records(
            round_idx=1,
            findings=[f1, f2],
            immune_result=_mk_immune_response(),
            duplicate_pairs=[("f1", "f2", 0.92)],
        )
        assert len(records) == 1
        rec = records[0]
        assert rec.finding_id == "f1"
        assert rec.duplicates == [("f2", 0.92)]
        assert rec.action == "DIFFERENTIATE_OR_WITHDRAW"

    def test_rk_warn_and_fail_are_flagged(self):
        f1 = _mk_finding("f1")
        f2 = _mk_finding("f2")
        f3 = _mk_finding("f3")
        records = build_feedback_records(
            round_idx=1,
            findings=[f1, f2, f3],
            immune_result=_mk_immune_response(),
            rk_validation={
                "claude": [
                    ("f1", "WARN", 0.8, 0.4),
                    ("f2", "FAIL", 0.9, 0.1),
                    ("f3", "PASS", 0.5, 0.52),  # should be ignored
                ],
            },
        )
        by_id = {r.finding_id: r for r in records}
        assert set(by_id.keys()) == {"f1", "f2"}
        assert by_id["f1"].rk_discrepancy == (0.8, 0.4)
        assert by_id["f2"].rk_discrepancy == (0.9, 0.1)

    def test_rk_skip_and_unparseable_are_ignored(self):
        f1 = _mk_finding("f1")
        records = build_feedback_records(
            round_idx=1,
            findings=[f1],
            immune_result=_mk_immune_response(),
            rk_validation={
                "claude": [
                    ("f1", "SKIP", None, None),
                ],
            },
        )
        assert records == []

    def test_rk_validation_with_none_floats_does_not_crash(self):
        f1 = _mk_finding("f1")
        records = build_feedback_records(
            round_idx=1,
            findings=[f1],
            immune_result=_mk_immune_response(),
            rk_validation={
                "claude": [
                    ("f1", "FAIL", None, 0.4),  # claimed missing
                ],
            },
        )
        # Float(None) → TypeError → caught → skip.
        assert records == []

    def test_all_signals_merge_into_one_record(self):
        f1 = _mk_finding("f1")
        ir = _mk_immune_response(
            cell_verdicts={"f1": [_mk_verdict("f1")]},
            final_verdicts={"f1": "REJECTED"},
        )
        f2 = _mk_finding("f2")  # referenced as duplicate target only
        records = build_feedback_records(
            round_idx=1,
            findings=[f1, f2],
            immune_result=ir,
            admissibility_failures={"f1": ["σ_measured"]},
            duplicate_pairs=[("f1", "f2", 0.85)],
            rk_validation={"claude": [("f1", "WARN", 0.7, 0.5)]},
        )
        merged = [r for r in records if r.finding_id == "f1"]
        assert len(merged) == 1
        rec = merged[0]
        assert rec.refutations
        assert rec.admissibility_failures == ["σ_measured"]
        assert rec.duplicates == [("f2", 0.85)]
        assert rec.rk_discrepancy == (0.7, 0.5)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. build_feedback_sections
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildFeedbackSections:
    def test_empty_records_yield_empty_dict(self):
        assert build_feedback_sections([], round_idx=1) == {}

    def test_section_header_contains_round(self):
        rec = FindingFeedback(
            finding_id="f1", model_origin="claude", severity_claimed=0.5,
            final_verdict="REJECTED",
            refutations=[("sympy", "REJECTED", "bad")],
        )
        sections = build_feedback_sections([rec], round_idx=3)
        assert "claude" in sections
        assert "ROUND 3" in sections["claude"]
        assert "END SCHEMA FEEDBACK" in sections["claude"]

    def test_per_model_routing(self):
        """Feedback for model A must not leak into model B's section."""
        rec_a = FindingFeedback(
            finding_id="f1", model_origin="claude", severity_claimed=0.5,
            final_verdict="REJECTED",
            refutations=[("sympy", "REJECTED", "evidence_A")],
        )
        rec_b = FindingFeedback(
            finding_id="f2", model_origin="gemini", severity_claimed=0.5,
            final_verdict="REJECTED",
            refutations=[("z3", "REJECTED", "evidence_B")],
        )
        sections = build_feedback_sections([rec_a, rec_b], round_idx=1)
        assert set(sections.keys()) == {"claude", "gemini"}
        assert "evidence_A" in sections["claude"]
        assert "evidence_A" not in sections["gemini"]
        assert "evidence_B" in sections["gemini"]
        assert "evidence_B" not in sections["claude"]

    def test_top_k_cap_truncates_with_overflow_notice(self):
        # Zero-padded IDs so "ev_01" is not a substring of "ev_10".
        recs = [
            FindingFeedback(
                finding_id=f"f_{i:02d}", model_origin="claude",
                severity_claimed=0.1 * i,  # higher-indexed = higher severity
                final_verdict="REJECTED",
                refutations=[("sympy", "REJECTED", f"ev_{i:02d}")],
            )
            for i in range(15)
        ]
        sections = build_feedback_sections(recs, round_idx=1, top_k=10)
        section = sections["claude"]
        # Highest-severity items survive: f_14, f_13, ... f_05 — 10 total.
        for i in range(5, 15):
            assert f"ev_{i:02d}" in section, f"expected ev_{i:02d} in top-10"
        for i in range(5):
            assert f"ev_{i:02d}" not in section, f"did not expect ev_{i:02d}"
        assert "5 further flagged finding" in section

    def test_overflow_singular_vs_plural(self):
        recs = [
            FindingFeedback(
                finding_id=f"f{i}", model_origin="claude",
                severity_claimed=0.1 * i,
                final_verdict="REJECTED",
                refutations=[("sympy", "REJECTED", f"ev_{i}")],
            )
            for i in range(11)  # exactly one overflow
        ]
        section = build_feedback_sections(recs, round_idx=1, top_k=10)["claude"]
        assert "1 further flagged finding " in section
        assert "findings" not in section.split("further flagged finding")[1][:20]

    def test_max_chars_cap_enforced(self):
        """Very long evidence strings should still fit within the char cap
        via drop-bottom trimming."""
        long_evidence = "x" * 500  # 500 chars each
        recs = [
            FindingFeedback(
                finding_id=f"f{i}", model_origin="claude",
                severity_claimed=0.1,
                final_verdict="REJECTED",
                refutations=[("sympy", "REJECTED", long_evidence)],
            )
            for i in range(20)
        ]
        sections = build_feedback_sections(
            recs, round_idx=1, top_k=15, max_chars_per_model=2000,
        )
        assert len(sections["claude"]) <= 2000

    def test_rendering_includes_all_signal_types(self):
        rec = FindingFeedback(
            finding_id="f_multi", model_origin="claude", severity_claimed=0.8,
            final_verdict="REJECTED",
            refutations=[("z3", "REJECTED", "unsat core: P ∧ ¬P")],
            admissibility_failures=["S_min", "d_tool"],
            duplicates=[("f_prior", 0.91)],
            rk_discrepancy=(0.85, 0.30),
        )
        section = build_feedback_sections([rec], round_idx=1)["claude"]
        assert "f_multi" in section
        assert "RECALCULATE" in section
        assert "REFUTED by:" in section
        assert "z3" in section
        assert "ADMISSIBILITY FAIL" in section
        assert "S_min" in section
        assert "NEAR-DUPLICATE" in section
        assert "f_prior" in section
        assert "R_k INCONSISTENT" in section

    def test_evidence_truncation_at_400_chars(self):
        """A single runaway tool output should not dominate the prompt."""
        runaway = "a" * 2000
        rec = FindingFeedback(
            finding_id="f1", model_origin="claude", severity_claimed=0.5,
            final_verdict="REJECTED",
            refutations=[("sympy", "REJECTED", runaway)],
        )
        section = build_feedback_sections([rec], round_idx=1)["claude"]
        # The 2000-char blob must not appear verbatim; the truncated marker
        # must be present.
        assert runaway not in section
        assert "…" in section


# ═══════════════════════════════════════════════════════════════════════════════
# 4. parse_admissibility_block
# ═══════════════════════════════════════════════════════════════════════════════


class TestParseAdmissibility:
    def test_missing_block_all_fail(self):
        assert set(parse_admissibility_block("no block here")) == set(ADMISSIBILITY_GATES)

    def test_empty_string_all_fail(self):
        assert set(parse_admissibility_block("")) == set(ADMISSIBILITY_GATES)

    def test_all_pass_no_failures(self):
        text = """
        ADMISSIBILITY:
          S_min: PASS (location=bench/foo.py:42)
          G-completeness: PASS (reproducible)
          d_tool: PASS (pytest ran)
          σ_measured: PASS (post-fix clean)
          q_retest: PASS (η=0.7)
        NOVELTY:
        """
        assert parse_admissibility_block(text) == []

    def test_mixed_pass_fail(self):
        text = """
        ADMISSIBILITY:
          S_min: PASS
          G-completeness: FAIL (verifier cannot reproduce)
          d_tool: PASS
          σ_measured: FAIL (no measurement)
          q_retest: PASS
        """
        failed = set(parse_admissibility_block(text))
        assert failed == {"G-completeness", "σ_measured"}

    def test_case_insensitive_pass_fail(self):
        text = """
        ADMISSIBILITY:
          S_min: pass
          G-completeness: fail
          d_tool: Pass
          σ_measured: FaIl
          q_retest: PASS
        """
        failed = set(parse_admissibility_block(text))
        assert failed == {"G-completeness", "σ_measured"}

    def test_sigma_ascii_variant_accepted(self):
        text = """
        ADMISSIBILITY:
          S_min: PASS
          G-completeness: PASS
          d_tool: PASS
          sigma_measured: PASS
          q_retest: PASS
        """
        assert parse_admissibility_block(text) == []

    def test_g_completeness_space_variant(self):
        text = """
        ADMISSIBILITY:
          S_min: PASS
          G completeness: PASS
          d_tool: PASS
          σ_measured: PASS
          q_retest: PASS
        """
        assert parse_admissibility_block(text) == []

    def test_section_terminator_stops_parse(self):
        """Gates mentioned after the block end should not be parsed."""
        text = """
        ADMISSIBILITY:
          S_min: FAIL
          G-completeness: FAIL
          d_tool: FAIL
          σ_measured: FAIL
          q_retest: FAIL
        NOVELTY:
          S_min: PASS (this is a DIFFERENT section and should not override)
        """
        # All 5 fail, despite a later "S_min: PASS" inside NOVELTY.
        failed = set(parse_admissibility_block(text))
        assert failed == set(ADMISSIBILITY_GATES)

    def test_finding_id_marker_terminates_block(self):
        """Regression for the Exp 40 panel-found parser bug
        (canonical C0008). Before 15 May 2026 fix, FINDING_ID: in the
        next finding did not match the terminator regex (because `_ID`
        appears between FINDING and the colon), so the ADMISSIBILITY
        block consumed text from the subsequent finding.

        Fix: FINDING_ID added to the terminator alternation in
        bench/dm/_feedback.py parse_admissibility_block.
        """
        text = """
        FINDING_ID: F001
        ADMISSIBILITY:
          S_min: PASS
          G-completeness: FAIL (no verifier reproduces)
          d_tool: PASS
          σ_measured: PASS
          q_retest: PASS
        FINDING_ID: F002
        ADMISSIBILITY:
          S_min: FAIL (location missing)
          G-completeness: PASS
          d_tool: PASS
          σ_measured: PASS
          q_retest: PASS
        """
        # Parser should return failures for F001's block only —
        # NOT also pick up F002's "S_min: FAIL".
        failed = parse_admissibility_block(text)
        assert failed == ["G-completeness"], (
            f"ADMISSIBILITY block leaked across FINDING_ID boundary; "
            f"expected ['G-completeness'], got {failed}"
        )

    def test_missing_gates_count_as_failed(self):
        """If the block exists but skips a gate, the skipped gate is FAIL."""
        text = """
        ADMISSIBILITY:
          S_min: PASS
          d_tool: PASS
        """
        failed = set(parse_admissibility_block(text))
        # G-completeness, σ_measured, q_retest missing → all FAIL.
        assert failed == {"G-completeness", "σ_measured", "q_retest"}

    def test_separator_variants(self):
        """':' is canonical; '-' and '=' are tolerated."""
        text_dash = """
        ADMISSIBILITY:
          S_min - PASS
          G-completeness - PASS
          d_tool - PASS
          σ_measured - PASS
          q_retest - PASS
        """
        text_eq = """
        ADMISSIBILITY:
          S_min = PASS
          G-completeness = PASS
          d_tool = PASS
          σ_measured = PASS
          q_retest = PASS
        """
        assert parse_admissibility_block(text_dash) == []
        assert parse_admissibility_block(text_eq) == []


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Smoke test — full pipeline on representative round data
# ═══════════════════════════════════════════════════════════════════════════════


class TestFullPipeline:
    def test_end_to_end_representative_round(self):
        """Build records from realistic multi-model inputs, render sections,
        verify claude and gemini get distinct, non-empty feedback."""
        findings = [
            _mk_finding("f1", model="claude", severity=0.9),
            _mk_finding("f2", model="claude", severity=0.3),
            _mk_finding("f3", model="gemini", severity=0.7),
            _mk_finding("f4", model="deepseek", severity=0.6),  # no flags — silent
        ]
        ir = _mk_immune_response(
            cell_verdicts={
                "f1": [_mk_verdict("f1", evidence="unsat")],
                "f3": [_mk_verdict("f3", tool="z3", evidence="model found")],
            },
            final_verdicts={
                "f1": "REJECTED",
                "f2": "UNCERTAIN",
                "f3": "REJECTED",
                "f4": "CONFIRMED",
            },
        )
        records = build_feedback_records(
            round_idx=2,
            findings=findings,
            immune_result=ir,
            admissibility_failures={"f2": ["q_retest"]},
            duplicate_pairs=[("f2", "f1", 0.72)],
            rk_validation={"gemini": [("f3", "FAIL", 0.8, 0.2)]},
        )
        sections = build_feedback_sections(records, round_idx=2)

        # claude should have f1 (refuted) and f2 (admissibility + duplicate)
        # gemini should have f3 (refuted + rk)
        # deepseek should be absent entirely (f4 was CONFIRMED)
        assert set(sections.keys()) == {"claude", "gemini"}
        assert "f1" in sections["claude"]
        assert "f2" in sections["claude"]
        assert "f3" in sections["gemini"]
        assert "deepseek" not in sections
