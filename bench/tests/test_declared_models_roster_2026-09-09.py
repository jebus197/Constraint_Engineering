"""Routing and the sweep must dispatch only to seats the running arm declared.

Written 2026-09-09, and the reason it exists in this shape is worth stating.

THE DEFECT. `_apply_routing` and `_post_convergence_sweep` both iterated
`exp_config.models`, the full orchestrator roster, rather than the models the arm
declared. The exp56 1-seat arm declares ['CC2'] while the roster is ['CC2',
'Codex', 'ChatGPT', 'Gemini', 'DeepSeek'], so routing would have dispatched to 4
undeclared seats, all paid. Both arms carried `routing_enabled: false` and
`post_convergence_sweep_rounds: 0` as a mitigation; the founder has now ruled both
ON, which is only safe because the roster is filtered.

WHY THESE TESTS AND NOT THE OBVIOUS ONES. The first attempt at guarding this
called `_declared_models` directly. Mutation testing then showed that reverting
`_apply_routing` to the full roster left every test GREEN -- because the tests
exercised the helper and never the wiring. That is precisely the fault the
predecessor guard had, which exercised `rank_falsifier_writers` rather than its
caller, and repeating it while replacing it would have been a poor joke. So the
wiring tests below drive `_apply_routing` and `_post_convergence_sweep` with a
stub in place of the dispatcher and count the seats actually reached.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
import bench.reference_runner_v3 as rr  # noqa: E402
from bench import launcher_core  # noqa: E402
from bench.launcher_core import build_runner_config_from_dict  # noqa: E402

_M = lambda label: types.SimpleNamespace(label=label)  # noqa: E731
REAL = types.SimpleNamespace(models=[_M(x) for x in
                                     ["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek"]])
SIM = types.SimpleNamespace(models=[_M(x) for x in
                                    ["CC2-SIM", "Codex-SIM", "ChatGPT-SIM",
                                     "Gemini-SIM", "DeepSeek-SIM", "Fable-SIM"]])


def _cfg(models, **kw):
    return types.SimpleNamespace(models=models, **kw)


def _labels(seats):
    return [getattr(m, "label", str(m)) for m in seats]


# --- The helper's own behaviour. ---------------------------------------------

def test_a_declared_subset_is_honoured():
    assert _labels(rr._declared_models(REAL, _cfg(["CC2"]))) == ["CC2"]


def test_no_declaration_returns_the_whole_roster():
    """An arm that names no models is asking for the roster it was launched with;
    that is different from declaring nothing."""
    assert _labels(rr._declared_models(REAL, _cfg([]))) == _labels(REAL.models)
    assert _labels(rr._declared_models(REAL, _cfg(None))) == _labels(REAL.models)


def test_the_SIM_suffix_is_normalised_in_both_directions():
    """THE TRAP. In a simulated run the roster is CC2-SIM while a config may
    declare CC2. A naive intersection returns EMPTY for every simulated run,
    silently disabling the routing the archive shows absorbing 53 of 69 findings
    (76.8%, Wilson [65.6%, 85.2%]). Getting this wrong is worse than the defect."""
    assert _labels(rr._declared_models(SIM, _cfg(["CC2"]))) == ["CC2-SIM"]
    assert _labels(rr._declared_models(SIM, _cfg(["CC2-SIM"]))) == ["CC2-SIM"]
    assert _labels(rr._declared_models(SIM, _cfg(["CC2", "Codex"]))) == \
        ["CC2-SIM", "Codex-SIM"]


def test_a_declaration_matching_nothing_falls_back_to_the_roster():
    """REVERSES this file's own first ruling, which was wrong and shipped red.

    The first version asserted that a declaration matching nothing must return
    EMPTY, reasoning that widening back to the roster would reinstate the leak.
    It does not, and the reasoning confused two different cases. The leak case
    is NOT disjoint -- the exp56 1-seat arm declares ['CC2'] against a roster
    that carries 'CC2', so the intersection is non-empty and the filter binds
    (asserted directly by the leak tests below). Disjoint means the declaration
    is written in a vocabulary the roster does not use, and filtering on it then
    erases the roster rather than restricting it.

    What that cost, executed rather than argued: with cfg.models left at its
    hardcoded default and a roster of ['SIM-A'], the intersection is empty, so
    routing and the post-convergence sweep dispatched to nobody and stamped
    nothing. It took test_corrected_copy_wiring.py red on 2 executing tests.

    ITS ARCHIVE REACH IS 0, and this sentence replaces an overstatement. The
    first draft said it would have disabled routing in every simulated run;
    scripts/roster_disjointness_2026-09-09.py measures 0 of 60 archived runs
    disjoint from the hardcoded default, Wilson [0.0%, 6.0%], because simulated
    seats carry vendor-SIM labels that the normalisation resolves. Real and
    reachable, never suffered."""
    got = rr._declared_models(REAL, _cfg(["Llama", "Mistral"]))
    assert _labels(got) == _labels(REAL.models), (
        f"a disjoint declaration must fall back to the full roster, got "
        f"{_labels(got)}")


def test_the_fallback_says_so_out_loud(capsys):
    rr._declared_models(REAL, _cfg(["Llama"]))
    # ONE readouterr() call. Calling it twice CLEARS the buffer on the first call
    # and returns empty on the second, which made this assert on nothing.
    captured = capsys.readouterr()
    out = captured.out + captured.err
    assert "DOES NOT DESCRIBE THIS ROSTER" in out, (
        "falling back must be announced; an unannounced widening is how a "
        "declaration silently stops binding")


def test_the_hardcoded_default_is_not_read_as_a_declaration():
    """THE ROOT CAUSE of the regression above, pinned as its own case.

    `RunnerConfig.models` defaults to the pre-Fable panel, and the runner's own
    comment in `run_experiment` records that a run leaving it untouched is the
    launcher config-drop class this project has hit 7 times. Reading that stale
    default as an arm's declaration made it 8.

    THE ROSTER HERE IS A STRICT SUPERSET OF THE DEFAULT, and that is the whole
    test. An earlier version used a roster equal to the 5 default labels, so the
    intersection was the whole roster and the assertion held whether or not the
    default was special-cased -- mutation testing caught it surviving while all
    64 tests stayed green. Only a roster carrying a seat the stale default omits
    can tell the two behaviours apart, which is exactly the 2026-08-30 episode:
    6 ModelConfigs supplied, `cfg.models` left at its 5-item default, the run
    reporting a 5-model panel while dispatching a sixth."""
    default = rr._runner_config_models_default()
    assert default, "the dataclass default must be readable, not typed here"
    post_fable = types.SimpleNamespace(
        models=[_M(x) for x in list(default) + ["Fable"]])
    assert "Fable" not in default, (
        "this test's discriminating power depends on Fable being absent from "
        "the stale default; if it has been added, pick another new seat")
    got = rr._declared_models(post_fable, _cfg(list(default)))
    assert _labels(got) == _labels(post_fable.models), (
        f"the untouched default must return the roster unfiltered; got "
        f"{_labels(got)}, silently dropping the seat the default predates")


def test_the_default_is_derived_from_the_dataclass_not_typed():
    """A second typed copy would drift from the field it describes."""
    import dataclasses
    fld = {f.name: f for f in dataclasses.fields(rr.RunnerConfig)}["models"]
    live = list(fld.default_factory()) if fld.default_factory is not dataclasses.MISSING \
        else list(fld.default)
    assert rr._runner_config_models_default() == live


# --- THE WIRING. These are the tests the first attempt lacked. ---------------

def _arm_cfg(name):
    import copy, json
    d = json.loads((REPO / "bench" / "exp56_configs" / name).read_text())
    args = types.SimpleNamespace(dry_run=True, resume=False, models=None)
    return build_runner_config_from_dict(copy.deepcopy(d), args), d["models"]


def test_the_SWEEP_reaches_only_declared_seats(monkeypatch):
    """Driven with a stub in place of dispatch_to_model, counting who is reached."""
    reached: list = []
    monkeypatch.setattr(rr, "dispatch_to_model",
                        lambda mc, *a, **k: (reached.append(getattr(mc, "label", str(mc))), ("", 0.0))[1])
    cfg, declared = _arm_cfg("d9_single_model_with_agents.json")
    cfg.post_convergence_sweep_rounds = 1
    registry = types.SimpleNamespace(entries={
        "C0001": {"status": "OPEN", "severity": 0.8, "description": "a residual"}})
    exp_config = launcher_core.load_experiment_config()
    rr._post_convergence_sweep(registry, exp_config, cfg, 3, repo_root=str(REPO))
    assert reached, "the stub was never called; this test is not exercising the sweep"
    assert set(reached) <= set(declared), (
        f"the sweep reached {sorted(set(reached) - set(declared))}, which the arm "
        f"never declared. cfg.models={declared}")


def test_apply_routing_builds_its_ladder_from_the_DECLARED_roster(monkeypatch):
    """The wiring, not the helper. Reverting `_apply_routing` to the full roster
    must turn this red; a test that calls `_declared_models` directly does not."""
    seen: dict = {}

    real = rr._declared_models

    def _spy(exp_config, cfg):
        out = real(exp_config, cfg)
        seen["roster"] = _labels(out)
        return out

    monkeypatch.setattr(rr, "_declared_models", _spy)
    cfg, declared = _arm_cfg("d9_single_model_with_agents.json")
    cfg.routing_enabled = True
    registry = types.SimpleNamespace(entries={})
    exp_config = launcher_core.load_experiment_config()
    rr._apply_routing(registry, 0, exp_config, cfg=cfg, repo_root=str(REPO))
    assert "roster" in seen, (
        "_apply_routing did not consult _declared_models at all, so its ladder is "
        "built from something else -- which is the original defect")
    assert set(seen["roster"]) <= set(declared), (
        f"the ladder roster {seen['roster']} exceeds the declared {declared}")
