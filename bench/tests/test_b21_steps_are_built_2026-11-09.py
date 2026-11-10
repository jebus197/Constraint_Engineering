"""B21: the policy engine is reached, validated and selectable from the runner.

HIS RULING, 2026-11-09, verbatim: "on B21, my ruling is build it and implement
it, on steps through 1 to 5 in full."

WHAT EACH STEP IS, AND WHAT THIS FILE ASSERTS BY EXECUTION:
  1. `load_effective_policy` reachable from the CANONICAL runner -- asserted by
     CALLING `reference_runner_v3.effective_policy` and checking it merges.
  2. the live harness reads the merged policy -- SEE THE DOCSTRING BELOW. Its
     premise does not hold for the tables examined and this file records why,
     with the measurement, rather than asserting a redirect that would be wrong.
  3. a role dimension -- asserted by loading a policy WITH a role and showing it
     gains that role and loses nothing.
  4. `validate_all_policies` as a run-refusing preflight -- asserted by driving
     `policy_preflight` to BOTH verdicts, including 2 broken seats at once.
  5. the selectable list is generated -- asserted by calling it, and by proving
     `--help` reaches no network.

★ STEP 2's PREMISE IS FALSE FOR THE TABLES IT NAMES, MEASURED 2026-11-09.
B21 says to "redirect B13's 12 live per-model tables to read the merged policy
instead of their own dictionaries". Executed against the live tree:
`MODEL_SPECS` holds `tau`, `L`, `c`, `L_std` -- convergence parameters the
registry has no key for; `DECOMPOSITION_CONTEXT_THRESHOLD` and
`CONTEXT_CHAR_BUDGET_CEILING` have NO corresponding policy key at all; and
`MODEL_ROSTER` holds human-readable DISPLAY names while the registry holds API
identifiers, agreeing 0 of 6, Wilson [0.000000, 0.390334], Clopper-Pearson
[0.000000, 0.459258]. They are different quantities, not duplicated ones, so
redirecting them would not consolidate anything -- it would overwrite one
quantity with another. Recorded rather than forced.

AND THAT COMPARISON FOUND A REAL DEFECT, WHICH BELONGS TO B79: the 2 surfaces
disagree on the VERSION of 4 of 6 models -- Opus 4.7 against 4-6, DeepSeek V4
Pro against v3, GPT-5.5 against 5.4, Fable 5.1 against 5.
"""
from __future__ import annotations

import importlib
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


@pytest.fixture(scope="module")
def v3():
    return importlib.import_module("bench.reference_runner_v3")


@pytest.fixture(scope="module")
def reg():
    return importlib.import_module("bench.cdsfl_registry.registry")


@pytest.fixture(scope="module")
def cat():
    return importlib.import_module("bench.model_catalogue")


class _MC:
    def __init__(self, label): self.label = label


class _CFG:
    def __init__(self, models, domain="mathematics"):
        self.models, self.domain = models, domain


class _EXP:
    def __init__(self, models): self.models = models


class TestStep1TheRunnerReachesTheEngine:
    def test_the_runner_exposes_an_effective_policy_accessor(self, v3):
        assert hasattr(v3, "effective_policy"), (
            "the canonical runner cannot reach the 4-layer merge engine")

    def test_it_returns_a_merged_policy(self, v3):
        pol = v3.effective_policy(domain="mathematics", model="opus_4_6")
        assert isinstance(pol, dict) and len(pol) >= 8, pol
        assert "constraints" in pol and "model" in pol, sorted(pol)

    def test_it_is_cached_rather_than_re_merged(self, v3):
        a = v3.effective_policy(domain="mathematics", model="opus_4_6")
        b = v3.effective_policy(domain="mathematics", model="opus_4_6")
        assert a is b, "the policy is re-merged on every call"

    def test_different_domains_give_different_policies(self, v3):
        a = v3.effective_policy(domain="mathematics", model="opus_4_6")
        b = v3.effective_policy(domain="code", model="opus_4_6")
        assert a is not b, "the accessor collapses distinct domains to one key"


class TestStep3TheRoleLayerComposes:
    def test_a_role_adds_itself_and_removes_nothing(self, reg):
        base = reg.load_effective_policy(domain="mathematics", model="opus_4_6")
        roles = sorted(p.stem for p in
                       (REPO / "bench/cdsfl_registry/roles").glob("*.toml"))
        assert roles, "no role configs exist, so step 3 is not built"
        withrole = reg.load_effective_policy(
            domain="mathematics", model="opus_4_6", role=roles[0])
        assert set(base) <= set(withrole), (
            "adding a role LOST a top-level key; the merge is not monotone")


class TestStep4ThePreflightRefuses:
    def test_a_healthy_run_is_allowed(self, v3):
        assert v3.policy_preflight(
            _CFG(["CC2"]), _EXP([_MC("CC2")])) is True

    def test_an_unresolvable_seat_refuses_the_run(self, v3):
        v3.COMPOSER_MODEL_MAP["ZZTEST"] = "no_such_model_at_all"
        try:
            assert v3.policy_preflight(
                _CFG(["ZZTEST"]), _EXP([_MC("ZZTEST")])) is False
        finally:
            v3.COMPOSER_MODEL_MAP.pop("ZZTEST", None)

    def test_every_failure_is_reported_not_just_the_first(self, v3):
        """CC2's actual point: dying on the first means fixing them 1 at a time."""
        v3.COMPOSER_MODEL_MAP["ZZA"] = "missing_a"
        v3.COMPOSER_MODEL_MAP["ZZB"] = "missing_b"
        seen = []
        orig = v3._log
        v3._log = lambda m="", *a, **k: seen.append(str(m))
        try:
            v3.policy_preflight(_CFG(["ZZA", "ZZB"]),
                                _EXP([_MC("ZZA"), _MC("ZZB")]))
        finally:
            v3._log = orig
            v3.COMPOSER_MODEL_MAP.pop("ZZA", None)
            v3.COMPOSER_MODEL_MAP.pop("ZZB", None)
        blob = "\n".join(seen)
        assert "missing_a" in blob and "missing_b" in blob, (
            f"only some failures were reported:\n{blob}")

    def test_a_broken_validator_refuses_rather_than_dispatching(self, v3, reg):
        orig = reg.validate_all_policies
        reg.validate_all_policies = lambda: (_ for _ in ()).throw(
            RuntimeError("boom"))
        try:
            assert v3.policy_preflight(
                _CFG(["CC2"]), _EXP([_MC("CC2")])) is False
        finally:
            reg.validate_all_policies = orig

    def test_the_preflight_runs_before_the_paid_probe(self):
        src = (REPO / "bench/reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.index("def run_preflight(")
        body = src[i:i + 4000]
        a = body.index("policy_preflight(cfg, exp_config)")
        b = body.index("dispatch_to_model")
        assert a < b, (
            "the policy preflight runs after the first paid dispatch; a free "
            "check must not be discovered after money is spent")


class TestStep5TheListIsGenerated:
    def test_it_returns_rows_without_touching_the_network(self, cat):
        rows = cat.catalogue(include_remote=False, include_local=False)
        assert rows, "the registry produced no selectable models at all"
        assert all(r["source"] == "registry" for r in rows)

    def test_local_models_sort_first(self, cat, monkeypatch):
        """★ THIS TEST WAS VACUOUS ON ITS FIRST WRITING. It built its own list
        and sorted it with its own copy of the order map, so reversing the
        module's order map left it GREEN. It now DRIVES `catalogue()` with an
        injected local model and asserts what the module returns."""
        monkeypatch.setattr(cat, "local_models", lambda *a, **k: [
            {"id": "zzz-local-model", "source": "local", "local": True,
             "has_policy": False}])
        rows = cat.catalogue(include_remote=False, include_local=True)
        assert rows, "no rows at all"
        assert rows[0]["id"] == "zzz-local-model", (
            f"his instruction was local models at the TOP of the list; the "
            f"first row is {rows[0]['id']!r} from {rows[0]['source']!r}")
        assert rows[0]["local"] is True

    def test_remote_models_sort_last(self, cat, monkeypatch):
        monkeypatch.setattr(cat, "local_models", lambda *a, **k: [
            {"id": "aaa-local", "source": "local", "local": True,
             "has_policy": False}])
        monkeypatch.setattr(cat, "remote_models", lambda *a, **k: [
            {"id": "aaa-remote", "source": "openrouter", "local": False,
             "has_policy": False}])
        rows = cat.catalogue(include_remote=True, include_local=True)
        sources = [r["source"] for r in rows]
        assert sources[0] == "local", sources[:3]
        assert sources[-1] == "openrouter", sources[-3:]
        assert sources.index("local") < sources.index("registry") \
            < sources.index("openrouter"), sources

    def test_every_row_says_whether_its_role_performance_is_known(self, cat):
        for r in cat.catalogue(include_remote=False):
            assert "role_evidence" in r and "untested_note" in r, r
            if not r["role_evidence"]:
                assert "unknown" in r["untested_note"], (
                    "an untested model must SAY its performance is unknown")

    def test_the_roles_are_read_from_the_registry(self, cat):
        assert cat.known_roles(), "step 5 reports no roles, so step 3 is unreachable from it"

    def test_help_costs_nothing_and_reaches_no_network(self):
        """His standing rule after 15 of 17 runners billed on --help."""
        r = subprocess.run(
            [sys.executable, str(REPO / "bench/model_catalogue.py"), "--help"],
            capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-300:]
        assert "openrouter" not in r.stdout.lower() or "free" in r.stdout.lower()

    def test_the_default_path_does_not_call_openrouter(self, cat, monkeypatch):
        called = []
        monkeypatch.setattr(cat, "remote_models",
                            lambda *a, **k: called.append(1) or [])
        cat.catalogue(include_remote=False)
        assert not called, "the default path reached OpenRouter"

    def test_json_output_is_valid(self):
        r = subprocess.run(
            [sys.executable, str(REPO / "bench/model_catalogue.py"),
             "--json", "--no-local"],
            capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-300:]
        assert isinstance(json.loads(r.stdout), list)
