"""Prove the S* shadow RUNS on the live path, rather than that it is written down.

WHY THIS FILE EXISTS SEPARATELY from test_sk_break_even_2026-09-06.py. That file
proves the mathematics: sk_break_even returns the true fixed point. It says
nothing about whether the recorder is ever reached. Under `execute-do-not-grep`,
a block of code that no test drives is a hypothesis about behaviour, and this
project has shipped exactly that defect before -- boundary_band_sensitivity was
vacuous in 41 of 41 archived reports because its guard asserted on source text
and made 0 calls to the function it guarded.

So this drives _evaluate_sk_for_findings, the real round pipeline, and asserts on
the record it produces.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

PY_TARGET = '''
def clamp(value, lo, hi):
    if value < lo:
        return lo
    return value
'''

PY_FIX = """<<<< SEARCH
    if value < lo:
        return lo
    return value
====
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value
>>>> REPLACE
"""


def _registry_with_a_python_fix():
    from bench.dm._types import Finding
    from bench.reference_runner_v3 import FindingRegistry

    reg = FindingRegistry()
    cid = reg.register(
        Finding(finding_id="f1", model_id="DeepSeek", round_idx=0,
                flaw_class=2, severity=0.9, abstraction_index=0.5,
                description="clamp ignores its upper bound",
                falsifier_code="", proposed_fix=PY_FIX),
        "DeepSeek")
    return reg, cid


@pytest.fixture()
def evaluated(tmp_path):
    from bench.reference_runner_v3 import _evaluate_sk_for_findings

    target = tmp_path / "clamp_target.py"
    target.write_text(PY_TARGET)
    reg, cid = _registry_with_a_python_fix()
    # WITHOUT a baseline the effect gates return None and the finding ESCALATEs
    # before ever reaching the threshold -- correct A2 behaviour ("not scored is
    # not scored zero"), and the reason the first draft of this file skipped all
    # 4 tests instead of failing. A test that switches itself off is the I10
    # defect; it is not allowed to stand here.
    baseline = {"ruff_violations": 0,
                "bandit_findings": {"high": 0, "medium": 0, "low": 0}}
    _evaluate_sk_for_findings(reg, PY_TARGET, str(target), baseline=baseline,
                              round_idx=1)
    return reg.entries[cid]["sk_result"]


def test_the_shadow_is_actually_written(evaluated):
    """If the recorder is never reached, this key is absent and the whole
    correction is invisible in the archive -- which is the failure it exists
    to end."""
    assert evaluated.get("tristate") == "ADMISSIBLE", (
        f"the fixture no longer reaches the gate (tristate="
        f"{evaluated.get('tristate')}), so every assertion below would be vacuous"
    )
    assert "threshold_shadow" in evaluated, (
        "the gate ran but recorded no shadow -- the block at the S* call site "
        "is not on the executed path"
    )


def test_the_shadow_carries_every_field_a_reader_needs(evaluated):
    shadow = evaluated["threshold_shadow"]
    for key in ("shipped_s_star", "shipped_passes", "true_break_even",
                "corrected_passes", "would_flip", "reason"):
        assert key in shadow, f"shadow record is missing {key}"


def test_the_shadow_does_not_move_the_live_verdict(evaluated):
    """NON-DISTORTION on the real path, not on a grid. The shipped fields must
    still be present and must still be what the shipped formula produces."""
    from bench.reference_runner_v3 import check_sk_threshold

    gi = evaluated["gate_inputs"]
    passes, s_star = check_sk_threshold(
        evaluated["sk"], gi["nu_b"], gi["nu_f"], gi["q"], gi["R_old"], gi["s_floor"])
    assert evaluated["s_star"] == s_star
    assert evaluated["passes_threshold"] == passes
    assert evaluated["threshold_shadow"]["shipped_passes"] == passes


def test_gate_inputs_and_shadow_agree_with_each_other(evaluated):
    """The 2 records are written from the same variables; if they ever disagree
    one of them is reading a different operating point than the gate used."""
    assert evaluated["threshold_shadow"]["shipped_s_star"] == evaluated["s_star"]


def test_the_shadow_reports_a_flip_when_the_two_verdicts_differ():
    """The recorder must distinguish, not merely appear. At sk = 0.30 the shipped
    gate passes and the corrected floor rejects -- the exact case that raises
    residual risk from 0.500 to 0.5506."""
    from bench.reference_runner_v3 import sk_threshold_shadow

    rec = sk_threshold_shadow(0.30, 0.05, 0.20, 0.5, 0.5)
    assert rec["shipped_passes"] is True
    assert rec["corrected_passes"] is False
    assert rec["would_flip"] is True
    assert rec["shipped_s_star"] == 0.0
    assert rec["true_break_even"] == pytest.approx(0.504931, abs=1e-6)


def test_the_recorded_gate_inputs_are_the_literal_defaults(evaluated):
    """Corroborates the standing finding that model_params has no writer, so
    nu_b, nu_f and q can only ever be their defaults on a real run."""
    gi = evaluated["gate_inputs"]
    assert (gi["nu_b"], gi["nu_f"], gi["q"], gi["R_old"]) == (0.05, 0.2, 0.5, 0.5)
