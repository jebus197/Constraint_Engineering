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


def test_the_live_verdict_is_now_the_CORRECTED_one(evaluated):
    """THE PAIR WAS INVERTED, 2026-09-07, on the founder's ruling of 2026-09-06:
    "It is better to run with corrected values and precision, rather than risk
    inaccuracy."

    Until then the SHIPPED ratio decided and the corrected break-even was recorded
    beside it. The shipped ratio is not the break-even of the shipped nu_eff at
    all: the true condition is a quadratic in sigma, the two coincide only on the
    measure-zero surface nu_b == q*R, and the shipped value sits BELOW the true
    floor at 297 of 297 reachable grid points, Wilson [98.72%, 100.00%], with 0
    conservative. So the gate admitted harmful fixes universally.

    The corrected value now decides and the shipped verdict is recorded beside it,
    so every decision stays auditable in both coordinate systems. Measured on
    promotion: over 1100 grid points the corrected gate is LOOSER than shipped at
    0 of them, Wilson [0.000%, 0.348%], and stricter at 215. It can only ever
    reject more.
    """
    from bench.reference_runner_v3 import (
        check_sk_threshold, check_sk_threshold_corrected)

    gi = evaluated["gate_inputs"]
    passes, s_star = check_sk_threshold_corrected(
        evaluated["sk"], gi["nu_b"], gi["nu_f"], gi["q"], gi["R_old"], gi["s_floor"])
    assert evaluated["s_star"] == s_star, "the live verdict is not the corrected one"
    assert evaluated["passes_threshold"] == passes

    shipped_passes, shipped_s_star = check_sk_threshold(
        evaluated["sk"], gi["nu_b"], gi["nu_f"], gi["q"], gi["R_old"], gi["s_floor"])
    assert evaluated["shipped_verdict_now_shadow"] == (shipped_passes, shipped_s_star), (
        "the shipped verdict must still be recorded, or the promotion is not auditable")


def test_the_promotion_can_only_ever_reject_more(evaluated):
    """The one property that makes the promotion safe to ship: it never admits a
    fix the shipped gate would have refused."""
    from bench.reference_runner_v3 import (
        check_sk_threshold, check_sk_threshold_corrected)
    gi = evaluated["gate_inputs"]
    corrected, _ = check_sk_threshold_corrected(
        evaluated["sk"], gi["nu_b"], gi["nu_f"], gi["q"], gi["R_old"], gi["s_floor"])
    shipped, _ = check_sk_threshold(
        evaluated["sk"], gi["nu_b"], gi["nu_f"], gi["q"], gi["R_old"], gi["s_floor"])
    assert not (corrected and not shipped), (
        "the corrected gate admitted something the shipped gate refused")


def test_gate_inputs_and_shadow_agree_with_each_other(evaluated):
    """The records are written from the same variables; if they ever disagree one
    of them is reading a different operating point than the gate used.

    UPDATED 2026-09-07: `s_star` is now the CORRECTED floor, so it is the shadow's
    corrected field that must match it, not its shipped one."""
    from bench.reference_runner_v3 import check_sk_threshold
    gi = evaluated["gate_inputs"]
    _, shipped_s_star = check_sk_threshold(
        evaluated["sk"], gi["nu_b"], gi["nu_f"], gi["q"], gi["R_old"], gi["s_floor"])
    assert evaluated["threshold_shadow"]["shipped_s_star"] == shipped_s_star
    assert evaluated["gate_inputs"]["effective_threshold"] == evaluated["s_star"]


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
