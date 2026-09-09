"""CC2v verification must be reachable in every exp56 arm, or it is a confound.

A panel review on 2026-09-09 found that `_verification_step` receives
`exp_config.models` unfiltered while `_apply_routing` and
`_post_convergence_sweep` had just been repaired to receive
`_declared_models(exp_config, cfg)`, and proposed filtering this call too for
consistency. The observation was right and the prescription was wrong, so this
file pins the reason rather than the fix.

`_verification_step` does not dispatch to the roster. It scans the roster for
the single seat whose base label is CC2, uses it as a verifier, and returns
`{"skipped": True, "reason": "CC2 config not found"}` if that seat is absent.
CC2v is infrastructure held constant across arms -- no exp56 arm config sets any
`verification_*` key, so all 3 inherit the same default -- rather than a panel
seat that varies by arm.

Measured against the 3 real arm configs: filtering would leave CC2v reachable in
d9_single_model_with_agents and d9_multi_model_panel but remove it from
d11_seat_contrast_diversity_arm, which declares ['Codex', 'ChatGPT'] and no CC2.
One arm of three would then run without a verification capability the other two
have -- a confound introduced in the name of removing one, and a disabled
feature, which the additive standard forbids.

These tests EXECUTE the selection rather than reading the source, because a
source-text test cannot tell a roster that reaches CC2 from one that does not.
"""

import json
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    RunnerConfig, _declared_models, _verification_step, base_model_label,
)

ARMS = sorted((REPO / "bench" / "exp56_configs").glob("*.json"))
ROSTER = ["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"]


def _roster(labels=None):
    return types.SimpleNamespace(
        models=[types.SimpleNamespace(label=lbl, timeout=10)
                for lbl in (labels or ROSTER)])


def _cfg_for(arm_path):
    cfg = RunnerConfig(test_article="x")
    cfg.models = json.loads(arm_path.read_text())["models"]
    return cfg


def test_the_arms_exist_so_this_file_is_not_vacuous():
    assert len(ARMS) == 3, [p.name for p in ARMS]


@pytest.mark.parametrize("arm", ARMS, ids=lambda p: p.stem)
def test_cc2v_is_reachable_in_every_arm_as_shipped(arm):
    """The property being protected, stated positively."""
    roster = _roster()
    assert any(base_model_label(mc.label) == "CC2" for mc in roster.models), (
        f"{arm.name}: the roster passed to _verification_step carries no CC2, "
        f"so verification is skipped in this arm while others have it")


@pytest.mark.parametrize("arm", ARMS, ids=lambda p: p.stem)
def test_filtering_this_call_would_break_at_least_one_arm(arm):
    """The refused fix, executed. This is the evidence for the refusal.

    If a future change makes filtering harmless -- every arm declaring CC2, say
    -- this test goes red and the refusal should be revisited rather than
    inherited. It is written to fail LOUDLY on that, not to pass forever."""
    kept = _declared_models(_roster(), _cfg_for(arm))
    reachable = any(
        base_model_label(getattr(mc, "label", mc)) == "CC2" for mc in kept)
    declares_cc2 = "CC2" in json.loads(arm.read_text())["models"]
    assert reachable == declares_cc2, (
        f"{arm.name}: filtering makes CC2v reachability track whether the arm "
        f"happens to declare CC2, which is what makes it a confound")


def test_verification_skips_rather_than_crashes_when_cc2_is_absent():
    """The mechanism behind the confound, executed rather than asserted.

    This is what an arm would silently get if the refused fix were applied: not
    an error, a skip -- which is the shape this project keeps losing capabilities
    to."""
    reg = types.SimpleNamespace(entries={})
    cfg = RunnerConfig(test_article="x")
    cfg.verification_min_round = 0
    out = _verification_step(reg, 9, "print(1)", _roster(["Codex", "ChatGPT"]), cfg)
    assert out.get("skipped") is True, out
