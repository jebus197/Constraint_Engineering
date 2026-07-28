"""Regression tests for Exp 40 continuation fix 1c — Regulatory T v2
per-model-bias multi-round windowing.

Bug class (continuation Anomaly 4): the per-model-bias check in
`regulatory_t_v2` fired AUTOIMMUNE every round a model hit ≥85%
removal. In a converged-state run one model (the continuation's
Gemini) reasonably produces mostly already-canonicalised findings and
hits 100% removal every round — generating a recurring HIL flag that
needs no action and forcing per-round resurrection churn.

Fix: optional `bias_window_state` dict (caller-owned, persists across
rounds). When None (default) behaviour is byte-identical to before
(backward compat). When supplied, the per-model-bias reason is only
promoted to a flag after the model sustains the condition for
`bias_window_rounds` consecutive rounds. Combined-removal-rate and
uncertain-rate checks are NOT windowed.

These tests pin:
  1. Legacy path (state=None) fires immediately — unchanged.
  2. Windowed path suppresses the flag for rounds 1..N-1.
  3. Windowed path fires the flag at round N.
  4. A broken streak resets the counter.
  5. Combined-removal-rate (Check 1) still fires immediately even
     under windowing (only Check 3 is windowed).
"""

from __future__ import annotations

import pytest

from bench.dm._types import Finding
from bench.immune_agents import (
    ClaimType,
    TriagedFinding,
    regulatory_t_v2,
)


def _mk(fid: str, model_id: str) -> TriagedFinding:
    f = Finding(
        finding_id=fid,
        model_id=model_id,
        round_idx=1,
        flaw_class=3,
        severity=0.7,
        abstraction_index=0.5,
        description="d",
    )
    return TriagedFinding(finding=f, claim_type=ClaimType.CODE_BEHAVIORAL)


def _scenario_one_model_all_removed():
    """Model 'Gemini' contributes 4 findings, all DUPLICATE; model
    'CC2' contributes 4 findings, all CONFIRMED. Gemini hits the
    per-model-bias condition (4/4 = 100% ≥ 85%); overall combined
    removal rate is 4/8 = 50% (below the 65% Check-1 threshold) so
    only Check 3 is in play."""
    triaged = []
    final_verdicts = {}
    for i in range(4):
        fid = f"Gemini_F{i:03d}"
        triaged.append(_mk(fid, "Gemini"))
        final_verdicts[fid] = "DUPLICATE"
    for i in range(4):
        fid = f"CC2_F{i:03d}"
        triaged.append(_mk(fid, "CC2"))
        final_verdicts[fid] = "CONFIRMED"
    return final_verdicts, triaged


class TestLegacyPathUnchanged:
    def test_state_none_fires_immediately(self):
        fv, tr = _scenario_one_model_all_removed()
        flag, reason, detail = regulatory_t_v2(fv, tr)
        assert flag is True
        assert "Gemini" in reason
        assert "systematic bias" in reason
        assert any(
            c.startswith("per_model_bias:Gemini")
            for c in detail.checks_fired
        )
        # No windowed marker in the legacy path.
        assert not any(
            "per_model_bias_windowed" in c
            for c in detail.checks_fired
        )


class TestWindowedPathSuppressesThenFires:
    def test_first_two_rounds_suppressed_third_fires(self):
        state: dict = {}
        fv, tr = _scenario_one_model_all_removed()

        # Round 1 — streak 1/3, suppressed.
        flag1, reason1, d1 = regulatory_t_v2(
            fv, tr, bias_window_state=state, bias_window_rounds=3,
        )
        assert flag1 is False, "round 1 must not flag (1/3)"
        assert state["Gemini"] == 1
        assert any(
            "per_model_bias_windowed:Gemini:1/3" in c
            for c in d1.checks_fired
        )

        # Round 2 — streak 2/3, suppressed.
        flag2, reason2, d2 = regulatory_t_v2(
            fv, tr, bias_window_state=state, bias_window_rounds=3,
        )
        assert flag2 is False, "round 2 must not flag (2/3)"
        assert state["Gemini"] == 2

        # Round 3 — streak 3/3, fires.
        flag3, reason3, d3 = regulatory_t_v2(
            fv, tr, bias_window_state=state, bias_window_rounds=3,
        )
        assert flag3 is True, "round 3 must flag (3/3)"
        assert "3 consecutive rounds" in reason3
        assert any(
            c == "per_model_bias:Gemini" for c in d3.checks_fired
        )

    def test_broken_streak_resets(self):
        state: dict = {}
        fv_bias, tr_bias = _scenario_one_model_all_removed()

        # Round 1 — streak 1.
        regulatory_t_v2(
            fv_bias, tr_bias,
            bias_window_state=state, bias_window_rounds=3,
        )
        assert state["Gemini"] == 1

        # Round 2 — Gemini findings now all CONFIRMED (no removal).
        # Streak must reset to 0.
        fv_clean = dict(fv_bias)
        for fid in list(fv_clean):
            if fid.startswith("Gemini_"):
                fv_clean[fid] = "CONFIRMED"
        regulatory_t_v2(
            fv_clean, tr_bias,
            bias_window_state=state, bias_window_rounds=3,
        )
        assert state["Gemini"] == 0, (
            "streak must reset when the model drops below the "
            "removal threshold"
        )

        # Round 3 — biased again; streak should be 1 (fresh), not 2.
        regulatory_t_v2(
            fv_bias, tr_bias,
            bias_window_state=state, bias_window_rounds=3,
        )
        assert state["Gemini"] == 1


class TestOtherChecksNotWindowed:
    def test_combined_removal_rate_still_immediate(self):
        # All 8 findings removed → combined removal rate 100% > 65%.
        # Check 1 must fire immediately even under windowing (only
        # Check 3 is windowed).
        triaged = []
        fv = {}
        for i in range(8):
            fid = f"M_F{i:03d}"
            triaged.append(_mk(fid, "M"))
            fv[fid] = "REJECTED"
        state: dict = {}
        flag, reason, detail = regulatory_t_v2(
            fv, triaged,
            bias_window_state=state, bias_window_rounds=3,
        )
        assert flag is True, (
            "combined-removal-rate check must fire immediately "
            "regardless of per-model windowing"
        )
        assert "removal rate" in reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
