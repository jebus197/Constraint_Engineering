"""Regression tests for the gated "tools decide, not votes" falsifier gate
(2026-06-03). Pins:
  - reverify_falsifier truth-decider: genuine demonstration -> CONFIRMED; clean
    run -> REFUTED; BROKEN falsifier (import/typo/syntax) -> ERROR, never an
    auto-CONFIRM; empty -> UNTOOLABLE.
  - apply_falsifier_verdicts override: gated-off is a no-op; gated-on lets the
    runner's re-run decide and routes broken / un-toolable criticals to HIL,
    never auto-confirming, demoting a vote-confirmed un-toolable critical.
"""
from __future__ import annotations

import pytest

from bench.falsifier_verify import reverify_falsifier
from bench.reference_runner_v3 import (
    FindingRegistry, RunnerConfig, apply_falsifier_verdicts,
)
from bench.dm._types import Finding


# ── reverify_falsifier (the deterministic truth-decider) ──────────────────────

@pytest.mark.parametrize("code,expected", [
    ("assert False, 'defect'", "CONFIRMED"),       # designed demonstration
    ("print('FALSIFIED')", "CONFIRMED"),           # explicit token
    ("assert True", "REFUTED"),                     # clean run, no defect
    ("import nonexistent_module_xyz", "ERROR"),     # BROKEN — must NOT confirm
    ("print(undefined_name_xyz)", "ERROR"),         # BROKEN (NameError)
    ("def (:", "ERROR"),                            # BROKEN (SyntaxError)
    ("", "UNTOOLABLE"),                             # nothing to run
])
def test_reverify_verdicts(code, expected):
    assert reverify_falsifier(code) == expected


def test_broken_falsifier_never_autoconfirms():
    """The bug this whole fix exists to prevent: a crashing falsifier must not
    be read as a confirmed defect."""
    for broken in ("import nope_xyz", "1/0", "raise RuntimeError('boom')"):
        assert reverify_falsifier(broken) != "CONFIRMED"


# ── apply_falsifier_verdicts (the gated override) ─────────────────────────────

def _mk(fid, sev, fcode):
    return Finding(finding_id=fid, model_id="m", round_idx=0, flaw_class=2,
                   severity=sev, abstraction_index=0.5, description=f"f{fid}",
                   falsifier_code=fcode)


def _registry_with_cases():
    reg = FindingRegistry()
    ids = {
        "confirm": reg.register(_mk("f1", 0.8, "assert False, 'real'"), "m"),
        "refute":  reg.register(_mk("f2", 0.8, "assert True"), "m"),   # critical
        "refute_minor": reg.register(_mk("f5", 0.5, "assert True"), "m"),  # non-crit
        "broken":  reg.register(_mk("f3", 0.8, "import nope_xyz"), "m"),
        "nofals":  reg.register(_mk("f4", 0.8, ""), "m"),
    }
    reg.resolve(ids["nofals"], "CONFIRMED", 0)  # simulate the vote confirming it
    return reg, ids


def test_gated_off_is_noop():
    reg, ids = _registry_with_cases()
    apply_falsifier_verdicts(reg, 1, cfg=RunnerConfig(falsifier_gate_enabled=False))
    assert reg.entries[ids["confirm"]]["status"] == "OPEN"
    assert reg.entries[ids["refute"]]["status"] == "OPEN"


def test_gated_on_tools_decide():
    reg, ids = _registry_with_cases()
    apply_falsifier_verdicts(
        reg, 1, cfg=RunnerConfig(falsifier_gate_enabled=True), repo_root=".")
    e = reg.entries
    # genuine defect -> CONFIRMED by the runner's re-run
    assert e[ids["confirm"]]["status"] == "CONFIRMED"
    assert e[ids["confirm"]]["falsifier_verdict"] == "CONFIRMED"
    # CONFIRM-only: a clean run on a CRITICAL is NOT trusted to drop it (a broken
    # falsifier also clean-exits, so a false REFUTED would mask a real defect) -> the
    # critical is escalated to HIL, never auto-REFUTED.
    assert e[ids["refute"]]["falsifier_verdict"] == "REFUTED"
    assert e[ids["refute"]]["status"] != "REFUTED"
    assert e[ids["refute"]]["escalated"] is True
    # a clean run on a NON-critical IS trusted to drop it (no masking risk).
    assert e[ids["refute_minor"]]["status"] == "REFUTED"
    # broken falsifier -> HIL, NEVER auto-confirmed
    assert e[ids["broken"]]["status"] != "CONFIRMED"
    assert e[ids["broken"]]["escalated"] is True
    assert e[ids["broken"]]["falsifier_verdict"] == "ERROR"
    # un-toolable critical that the vote had CONFIRMED -> demoted + HIL
    assert e[ids["nofals"]]["status"] == "UNCONFIRMED"
    assert e[ids["nofals"]]["escalated"] is True
    assert e[ids["nofals"]]["falsifier_verdict"] == "UNTOOLABLE"
