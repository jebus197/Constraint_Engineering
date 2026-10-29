"""The credential redactor does not withhold an ordinary run setting (task B31).

HIS RULING, 2026-10-19: *"Then if I already ruled. Why are you presenting it as a
decision required from me again? Again your fix is approved. Do it."* He had
already approved it on 2026-10-18 in
`Responses/Review_Stop_And_Declared_Modes_2026-10-18.txt` with *"Your fix is
approved."* The approval was needed because the change reduces what a safety
mechanism withholds, even by 1 named field, and his standing pattern is that
loosening a guard's effect is his call.

WHAT WAS WRONG. `_declared_config` exists so a reader can see what a run was
told to do. Every archived report carrying one withheld `location_keyed_convergence`,
because the substring "key" appears in "keyed". Measured: **1 of `RunnerConfig`'s
100 fields** collides with the pattern list, and it is not a secret -- so the
mechanism's precision on this config was **0 true positives against 1 false
one** -- and **5 of 5** archived reports carrying a declared config withhold
exactly that field. Producer:
`scripts/does_the_redactor_withhold_config_2026-10-18.py`.

AND THE PLACEHOLDER WAS WORSE THAN AN ABSENT FIELD. `bool("<withheld: ...>")` is
True, so a check comparing a declared mode against what actually operated read a
withheld value as a declared True. Entry B28 makes exactly that comparison, and
for this field it could not be made at all.

EVERY TEST HERE CALLS `redacted_declared_config`. That function was extracted
from `main` on 2026-10-29 for this reason: while the rule was 20 lines inline
inside a several-hundred-line function, the only available guard was a
source-text scan, which cannot tell a producer and a consumer apart when each
describes itself correctly.

Written under CDSFL note standard v1.8.
"""
from __future__ import annotations

import dataclasses
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
WITHHELD = "<withheld: name matches a credential pattern>"


@pytest.fixture(scope="module")
def rse():
    p = REPO / "bench" / "tools" / "run_simulated_experiment.py"
    spec = importlib.util.spec_from_file_location("_rse_under_test", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rse_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def runner_config():
    sys.path.insert(0, str(REPO))
    from bench.reference_runner_v3 import RunnerConfig
    return RunnerConfig


class TestTheAllowListIsHonest:
    """Each exemption must be a REAL field that the pattern WOULD have hidden.
    An exemption for a field that does not exist, or that the pattern never
    touched, is an addition nothing reaches."""

    def test_every_exempt_name_is_a_real_field(self, rse, runner_config):
        names = {f.name for f in dataclasses.fields(runner_config)}
        unknown = sorted(rse.NEVER_SECRET_FIELDS - names)
        assert not unknown, (
            f"{unknown} are exempted and are not fields of RunnerConfig, so the "
            f"exemption protects nothing and hides a typo")

    def test_every_exempt_name_would_otherwise_be_withheld(self, rse):
        """NO DEAD ENTRIES. An exemption for a name the pattern never matched
        would be an addition nothing reaches, which this project's record names
        11 times over."""
        idle = sorted(n for n in rse.NEVER_SECRET_FIELDS
                      if not any(h in n.lower() for h in rse.CREDENTIAL_NAME_PARTS))
        assert not idle, (
            f"{idle} are exempted but the pattern never withheld them, so the "
            f"exemption does nothing")

    def test_the_list_is_as_small_as_the_measurement_says(self, rse, runner_config):
        """The measurement found exactly 1 collision. If a future field collides
        this FAILS, which is the point: a new collision is a decision, not a
        silent addition to the exemption set."""
        collide = {f.name for f in dataclasses.fields(runner_config)
                   if any(h in f.name.lower() for h in rse.CREDENTIAL_NAME_PARTS)}
        assert collide == set(rse.NEVER_SECRET_FIELDS), (
            f"fields colliding with the credential pattern are {sorted(collide)} "
            f"but the exemption set is {sorted(rse.NEVER_SECRET_FIELDS)}. A new "
            f"collision must be judged -- if it IS a secret leave it withheld "
            f"and widen this test; if it is not, exempt it by exact name.")


class TestTheSettingIsReadableNow:
    def test_the_field_is_not_withheld(self, rse, runner_config):
        got = rse.redacted_declared_config(runner_config())
        assert "location_keyed_convergence" in got
        assert got["location_keyed_convergence"] != WITHHELD, (
            "the run setting is still withheld, so B28's comparison is still blind")
        assert isinstance(got["location_keyed_convergence"], bool), (
            f"expected the declared bool, got "
            f"{got['location_keyed_convergence']!r}")

    def test_no_field_of_the_real_config_is_withheld_any_more(self, rse, runner_config):
        """ANTI-VACUITY in the other direction: the measurement says 1 of 100
        collided and it is exempted, so nothing should be withheld today."""
        got = rse.redacted_declared_config(runner_config())
        still = sorted(k for k, v in got.items() if v == WITHHELD)
        assert not still, (
            f"{still} are still withheld; the measurement said the only "
            f"collision was the exempted one")


class TestItStillWithholdsARealSecret:
    """THE ANTI-WIDENING HALF. The pattern list is untouched and exemption is by
    EXACT name, so a credential-shaped field must still be withheld."""

    @staticmethod
    def _cfg(**fields):
        ns = {"__annotations__": {k: type(v) for k, v in fields.items()}}
        ns.update(fields)
        return dataclasses.dataclass(type("_Cfg", (), ns))()

    @pytest.mark.parametrize("name", [
        "openrouter_api_key", "deepseek_token", "client_secret",
        "scoring_env", "env_file", "admin_password",
        # ★ THE EXEMPT NAME WITH A CREDENTIAL SUFFIX. Exact matching is what
        # makes this safe; a substring allow-list would have leaked it.
        "location_keyed_convergence_api_key",
    ])
    def test_a_credential_shaped_field_is_still_withheld(self, rse, name):
        got = rse.redacted_declared_config(self._cfg(**{name: "s3cret-value"}))
        assert got[name] == WITHHELD, (
            f"{name} was written as {got[name]!r}; the redactor has been widened")
        assert "s3cret-value" not in str(got), "the value reached the report"

    def test_the_exempt_name_is_matched_exactly_not_by_prefix(self, rse):
        cfg = self._cfg(location_keyed_convergence=True,
                        location_keyed_convergence_api_key="s3cret-value")
        got = rse.redacted_declared_config(cfg)
        assert got["location_keyed_convergence"] is True
        assert got["location_keyed_convergence_api_key"] == WITHHELD
        assert "s3cret-value" not in str(got)


class TestTheMarkerStillDistinguishesWithheldFromAbsent:
    def test_a_withheld_field_is_present_with_a_marker(self, rse):
        got = rse.redacted_declared_config(
            TestItStillWithholdsARealSecret._cfg(api_key="x", rounds=4))
        assert got["api_key"] == WITHHELD, "withheld became absent"
        assert got["rounds"] == 4
