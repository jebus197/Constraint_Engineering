"""Focused test suite for the Exp 40 plan-D decomposition slice
(bench/exp40_baseline/_feedback_slice.parse_admissibility_block).

These are the TestParseAdmissibility cases from test_feedback_channel.py,
re-pointed at the standalone slice. This file is the canonical-suite
gate for the plan-F convergence re-run (config test_cmd): the apply-back
loop promotes a verified fix into the slice working copy only if this
suite still passes cumulatively.
"""
from __future__ import annotations

import pytest

from bench.exp40_baseline._feedback_slice import (
    ADMISSIBILITY_GATES,
    parse_admissibility_block,
)


class TestParseAdmissibility:
    def test_missing_block_all_fail(self):
        assert set(parse_admissibility_block("no block here")) == set(
            ADMISSIBILITY_GATES)

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
        assert set(parse_admissibility_block(text)) == {
            "G-completeness", "σ_measured"}

    def test_case_insensitive_pass_fail(self):
        text = """
        ADMISSIBILITY:
          S_min: pass
          G-completeness: fail
          d_tool: Pass
          σ_measured: FaIl
          q_retest: PASS
        """
        assert set(parse_admissibility_block(text)) == {
            "G-completeness", "σ_measured"}

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
        assert set(parse_admissibility_block(text)) == set(
            ADMISSIBILITY_GATES)

    def test_finding_id_marker_terminates_block(self):
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
        failed = parse_admissibility_block(text)
        assert failed == ["G-completeness"], (
            f"ADMISSIBILITY block leaked across FINDING_ID boundary; "
            f"expected ['G-completeness'], got {failed}"
        )

    def test_missing_gates_count_as_failed(self):
        text = """
        ADMISSIBILITY:
          S_min: PASS
          d_tool: PASS
        """
        assert set(parse_admissibility_block(text)) == {
            "G-completeness", "σ_measured", "q_retest"}

    def test_separator_variants(self):
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
