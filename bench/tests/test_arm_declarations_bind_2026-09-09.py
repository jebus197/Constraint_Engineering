"""Every exp56 arm must dispatch to exactly the seats it declares — measured
against the LIVE orchestrator roster, so the day a 6th seat joins is loud.

FOUND INDEPENDENTLY BY BOTH SEATS in panel review 2026-09-09, and confirmed here
by execution. `_declared_models` treats a `cfg.models` that is list-equal to the
hardcoded `RunnerConfig.models` default as "no declaration made", because a stale
default left untouched must not be read as an arm's choice. Arm B
(`d9_multi_model_panel.json`) declares `['CC2', 'Codex', 'Gemini', 'DeepSeek',
'ChatGPT']`, which is byte-equal to that default.

TODAY THE LEAK IS 0, executed: the live roster is the same 5 labels, so the
filter is a no-op either way. It goes live the day a 6th seat joins the
orchestrator default — the exact "before Fable joined" drift this project's own
runner comment records having hit 7 times. Executed with a 6-seat roster,
`_declared_models` returns all 6 for Arm B, so a frozen 5-seat arm silently
becomes a 6-seat arm while `post_convergence_sweep_rounds: 2` iterates every one
of them.

WHY A TEST RATHER THAN A CONFIG EDIT. The reorder both seats proposed — same set,
different order, so list-equality breaks — is a 1-line change to a FROZEN
pre-registration file, and both seats independently said it needs the founder's
sign-off. This closes the same exposure without touching the freeze: the day the
roster grows, this goes red before anything is launched.

`PANEL MISMATCH` in `run_experiment` already notices the same condition and only
LOGS it, which is a warning rather than confinement.
"""

import json
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import launcher_core  # noqa: E402
from bench.reference_runner_v3 import (  # noqa: E402
    RunnerConfig, _declared_models, _runner_config_models_default,
    base_model_label,
)

ARMS = sorted((REPO / "bench" / "exp56_configs").glob("*.json"))


def _declared(arm):
    return json.loads(arm.read_text())["models"]


def _cfg(models):
    c = RunnerConfig(test_article="x")
    c.models = list(models)
    return c


def _labels(kept):
    return sorted(base_model_label(getattr(m, "label", m)) for m in kept)


def test_the_arms_exist():
    assert len(ARMS) == 3, [p.name for p in ARMS]


@pytest.mark.parametrize("arm", ARMS, ids=lambda p: p.stem)
def test_the_arm_reaches_exactly_what_it_declares_today(arm):
    """THE PROPERTY, against the live roster."""
    declared = _declared(arm)
    kept = _declared_models(launcher_core.load_experiment_config(), _cfg(declared))
    assert _labels(kept) == sorted(base_model_label(m) for m in declared), (
        f"{arm.name} declares {declared} but would reach {_labels(kept)}")


#: The arm whose declaration is byte-equal to the stale hardcoded default, and
#: which therefore does NOT bind if the roster grows. Recorded as a strict
#: expected failure rather than asserted away: `strict=True` means the day it
#: starts passing -- because the config was reordered, or the default changed --
#: the suite goes RED and this marker must be removed deliberately. A comment
#: would rot; an xfail cannot.
EXPOSED_PENDING_FOUNDER_RULING = {"d9_multi_model_panel.json"}


def _maybe_xfail(arm):
    if arm.name in EXPOSED_PENDING_FOUNDER_RULING:
        return pytest.param(arm, id=arm.stem, marks=pytest.mark.xfail(
            strict=True,
            reason="OPEN EXPOSURE, awaiting a founder ruling. This arm declares "
                   "the same 5 labels as the stale hardcoded default, so a 6th "
                   "seat joining the roster would silently widen it. The fix "
                   "both panel seats proposed -- reorder the same set so "
                   "list-equality breaks -- edits a FROZEN pre-registration "
                   "file, which is the founder's decision and not this file's."))
    return pytest.param(arm, id=arm.stem)


@pytest.mark.parametrize("arm", [_maybe_xfail(a) for a in ARMS])
def test_it_would_still_bind_if_a_sixth_seat_joined(arm):
    """THE EXPOSURE, made loud BEFORE a launch rather than after one.

    This is the test that goes red the day the roster grows. When it does, the
    fix is to make the affected arm's declaration distinguishable from the
    hardcoded default — the reorder both seats proposed — which is a change to a
    frozen pre-registration file and therefore the founder's decision, not this
    file's. Do not weaken this test to make it pass."""
    declared = _declared(arm)
    live = [m.label for m in launcher_core.load_experiment_config().models]
    grown = types.SimpleNamespace(
        models=[types.SimpleNamespace(label=lbl, timeout=10)
                for lbl in live + ["Fable"]])
    kept = _declared_models(grown, _cfg(declared))
    assert _labels(kept) == sorted(base_model_label(m) for m in declared), (
        f"{arm.name} declares {len(declared)} seat(s) but would reach "
        f"{_labels(kept)} once a 6th seat joins the roster, because its "
        f"declaration is indistinguishable from the stale hardcoded default "
        f"{_runner_config_models_default()}")


def test_at_least_one_arm_is_currently_exposed_so_this_file_is_not_vacuous():
    """Records the state that motivated the file.

    If this ever fails, the exposure was closed — by a config reorder or by a
    change to the default — and the sibling test above becomes the only guard
    needed. Update this to assert the new state rather than deleting it."""
    default = _runner_config_models_default()
    equal = [a.name for a in ARMS if _declared(a) == default]
    assert equal == ["d9_multi_model_panel.json"], equal
