"""B21 step 4 is wired; step 1 was measured and refused.

HIS DIRECTION on B21, 2026-10-17, in dependency order: *"(1) wire
`load_effective_policy` into v3, which is the single change that makes every
later step declarative"* ... *"(4) wire `validate_all_policies()` as the
run-level preflight CC2 recommended, reporting every missing registration at
once and refusing the run"*, with both described as *"each a handful of
lines"*.

STEP 4 IS DONE AND IS SAFE. The validator only ever refuses a run whose policy
layers do not merge, so it cannot change what a passing run does. It lands
GREEN -- 17 of 17 layers merge -- which is stated plainly rather than dressed
up: a check that lands green is not evidence it was needed, only that it is not
yet earning its keep. It is a ratchet.

STEP 1 WAS MEASURED AND REFUSED, and the plan it contradicts was mine. Three
figures, from
scripts/would_wiring_the_policy_engine_change_a_run_2026-10-17.py:

  * THE VOCABULARIES BARELY OVERLAP. The merged policy for domain=mathematics
    has 46 leaves and exactly 1 shares a name with a `RunnerConfig` field:
    `protocol.max_rounds`. Wiring needs a correspondence, and for the other 45
    there is none -- so "wire the policy in" cannot be a handful of lines.
  * THE ONE OVERLAP CONFLICTS: the runner's default is 21, the policy says 5,
    and both mean the same thing (the schema's own description is "Maximum
    rounds for CDSFL experiments").
  * AND THE POLICY'S VALUE MATCHES NO EXPERIMENT. Across 47 shipped configs, 0
    leave `max_rounds` unset (0.0000%, Wilson [0.0000%, 7.5558%]), so the
    runner's 21 is dead and the configs always decide. The values are 2, 6, 8,
    10, 12, 15, 16, 20 and 29. Letting the policy decide would CAP 46 of 47 --
    97.8723%, Wilson [88.8870%, 99.6234%] -- below their configured round
    count, truncating the experimental programme.

SO STEP 1 IS NOT A WIRING TASK. It is the question of WHICH LAYER OWNS
`max_rounds`, and 2 sources of truth for 1 quantity already disagree with every
experiment. That is his decision: make the policy the owner and raise its
value, make the config the owner and delete the policy key, or let a config
override a policy ceiling and record when it does -- each with a different
consequence for replay against the archive.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PREFLIGHT = REPO / "scripts" / "preflight_health_check_2026-10-06.py"
POST = REPO / "scripts" / "post_semantics_2026-10-06.py"
PRODUCER = REPO / "scripts" / "would_wiring_the_policy_engine_change_a_run_2026-10-17.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PF = _load(PREFLIGHT, "_pf")
PS = _load(POST, "_ps")


def test_the_check_exists_and_is_in_the_checks_list():
    """AN ADDITION NOTHING RUNS IS NOT ADDITIVE."""
    assert hasattr(PF, "check_policy_layers_merge")
    names = {n for n, _, _ in PF.CHECKS}
    assert "policy layers merge" in names, (
        "the check is defined and not registered, so the preflight never "
        "runs it")


def test_it_is_registered_in_the_boot_order_as_well():
    """The post-semantics boot halts at the first failure, so a check absent
    from POST_ORDER is a check the boot never reaches."""
    names = {n for n, _, _ in PF.CHECKS}
    assert names <= set(PS.POST_ORDER), (
        f"checks missing from POST_ORDER: {names - set(PS.POST_ORDER)}")
    assert names <= set(PS.DEPENDENCIES), (
        f"checks missing from DEPENDENCIES: {names - set(PS.DEPENDENCIES)}")


def test_it_passes_on_the_live_layers_and_says_how_many():
    status, message, extra = PF.check_policy_layers_merge()
    assert status == PF.PASS, f"{message} {extra}"
    assert "17" in message or "layers merge" in message


def test_it_refuses_when_a_layer_does_not_merge(monkeypatch):
    """EXECUTED, not assumed: the failure path is driven."""
    import bench.cdsfl_registry.registry as reg
    monkeypatch.setattr(reg, "validate_all_policies",
                        lambda: {"universal": "ok",
                                 "domains/mathematics": "weakens a HARD key"})
    status, message, extra = PF.check_policy_layers_merge()
    assert status == PF.FAIL
    assert "1 of 2" in message
    assert any("mathematics" in e for e in extra), (
        "the failing layer is not named, so a reader cannot act on it")


def test_an_empty_validator_result_is_a_failure_not_a_pass():
    """THE VACUITY GUARD. A validator that validated nothing must not read as
    a clean bill of health -- that is the checker-that-decides-nothing shape."""
    import bench.cdsfl_registry.registry as reg
    original = reg.validate_all_policies
    try:
        reg.validate_all_policies = lambda: {}
        status, message, _ = PF.check_policy_layers_merge()
        assert status == PF.FAIL
        assert "validated nothing" in message
    finally:
        reg.validate_all_policies = original


# ------------------------------------------------- why step 1 was refused

def test_the_policy_value_for_max_rounds_matches_no_shipped_config():
    """THE MEASUREMENT THAT REFUSED STEP 1, recomputed here so it cannot rot."""
    from bench.cdsfl_registry.registry import load_effective_policy
    policy = load_effective_policy("mathematics")
    policy_rounds = (policy.get("protocol") or {}).get("max_rounds")
    assert policy_rounds is not None, (
        "the policy no longer carries protocol.max_rounds; the conflict this "
        "entry describes may be resolved, and B21 needs re-deriving")

    values = []
    for path in sorted((REPO / "bench").glob("exp*_configs/*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue

        def dig(obj):
            if isinstance(obj, dict):
                if "max_rounds" in obj:
                    return obj["max_rounds"]
                for v in obj.values():
                    got = dig(v)
                    if got is not None:
                        return got
            elif isinstance(obj, list):
                for v in obj:
                    got = dig(v)
                    if got is not None:
                        return got
            return None

        values.append(dig(data))

    assert values, "no shipped configs found; this measurement is vacuous"
    unset = [v for v in values if v is None]
    assert not unset, (
        f"{len(unset)} configs now leave max_rounds unset, so the runner "
        f"default is live again and the 'dead default' finding is stale")
    capped = [v for v in values if v > policy_rounds]
    assert len(capped) > len(values) / 2, (
        f"only {len(capped)} of {len(values)} configs exceed the policy's "
        f"{policy_rounds}; the conflict has narrowed and B21's step 1 should "
        f"be re-measured before it is refused again")


def test_only_one_policy_leaf_shares_a_name_with_a_runner_field():
    """If this count rises, a correspondence is appearing and step 1 becomes a
    real wiring task. The test exists to notice that, not to freeze it."""
    from bench.cdsfl_registry.registry import load_effective_policy
    from bench.reference_runner_v3 import RunnerConfig

    def flat(d, pre=""):
        out = {}
        for k, v in (d or {}).items():
            key = f"{pre}{k}"
            if isinstance(v, dict):
                out.update(flat(v, key + "."))
            else:
                out[key] = v
        return out

    leaves = flat(load_effective_policy("mathematics"))
    fields = set(RunnerConfig.__dataclass_fields__)
    shared = [k for k in leaves if k.split(".")[-1] in fields]
    assert len(leaves) > 10, "the merged policy is suspiciously small"
    assert shared == ["protocol.max_rounds"], (
        f"the shared-name set is now {shared}, not just protocol.max_rounds. A "
        f"correspondence is emerging, so B21 step 1 should be re-measured: it "
        f"may now be a wiring task rather than an ownership question.")


def test_the_producer_runs_and_refuses_an_unknown_flag():
    import subprocess
    ok = subprocess.run([sys.executable, str(PRODUCER)], capture_output=True,
                        text=True, cwd=str(REPO))
    assert ok.returncode == 0, ok.stderr[-400:]
    assert "WHICH LAYER OWNS" in ok.stdout
    bad = subprocess.run([sys.executable, str(PRODUCER), "--bogus"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert bad.returncode != 0
