#!/usr/bin/env python3
"""The 3 capability lookups in `runner_core` announce a default instead of taking it silently.

C18's SECOND CLAUSE, from the panel design of 2026-10-18: *"An identity absent
from the tables must be LOUD, never defaulted."* It was implemented as
`routing.resolve_or_alarm`, which RECORDS a miss and still returns the default --
behaviour deliberately unchanged, because raising would turn a degradation into a
dead run.

IT REACHED 4 LIVE SITES AND NOT THESE 3. `reference_runner_v3:12369`,
`composer:765`, `composer:1833` and `composer:1899` were routed through it;
`runner_core`'s 3 were left as bare `.get(key, default)` calls.

THE REALISED COST, measured 2026-10-29. `Fable` has a `MODEL_SPECS` entry and no
`INITIAL_FINGERPRINTS` entry, so the fingerprint lookup substituted
`CapabilityFingerprint(0.2, 0.7, 0.7, 0.5)` silently -- and that substitute is
worse than EVERY measured seat on all 3 capability axes (`v_bar` 0.7 against a
measured floor of 0.75, `A` 0.7 against 0.75, `C` 0.5 against 0.65). Its sibling
table records a borrowed value: `MODEL_SPECS['Fable']` carries
`_provenance: 'inherited from CC2 2026-08-30; not measured'`. The discipline had
reached 1 of the 2 tables.

EVERY TEST HERE EXECUTES THE LIVE FUNCTIONS. The point of the change is that an
instrument reading the table could not see it, so a test reading the source would
be the same mistake.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for extra in (REPO, REPO / "bench"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from bench import routing as R  # noqa: E402
from bench import runner_core as rc  # noqa: E402
from experiment_11_orchestrator import ModelConfig  # noqa: E402

ABSENT = "KimiNotInAnyTable"


def _mc(label):
    return ModelConfig(label=label, model_id=label, api="none",
                       role="reviewer", system_prompt_path="")


def _cfg(label):
    return rc.ExperimentConfig(models=[_mc(label)],
                               logs_dir=str(REPO / "bench" / "logs" / "_t"),
                               budget_limit=0.0, cdsfl_system_prompt="")


@pytest.fixture(autouse=True)
def _clean():
    R.reset_lookup_misses()
    yield
    R.reset_lookup_misses()


class TestTheSameModuleObjectIsUsedThroughout:
    def test_runner_core_binds_the_package_module(self):
        """★ `routing` and `bench.routing` are DIFFERENT objects with SEPARATE
        ledgers. Verified 2026-10-29: `top is pkg` is False and
        `top._LOOKUP_MISSES is pkg._LOOKUP_MISSES` is False. A caller that binds
        one and a reader that binds the other see different ledgers, and the
        producer did exactly that -- reading an empty ledger and reporting
        SILENT for steps that had just been taught to announce.
        """
        assert rc._cap_identity is R, (
            "runner_core bound a different routing module object from this test, "
            "so a miss it records would be invisible here and to any reader that "
            "imports it the other way")

    def test_the_two_import_paths_really_are_distinct(self):
        """The hazard itself, pinned, so nobody concludes it is theoretical."""
        import importlib
        top = importlib.import_module("routing")
        pkg = importlib.import_module("bench.routing")
        assert top is not pkg, (
            "the 2 import paths now resolve to 1 object; if that is a deliberate "
            "change, this test should be removed with the measurement that "
            "justified it")
        assert top._LOOKUP_MISSES is not pkg._LOOKUP_MISSES


class TestARegisteredSeatIsUnaffected:
    def test_the_fingerprint_is_the_tables_own_value(self):
        specs = rc.build_model_specs(_cfg("CC2"))
        assert specs, "no spec was built for a registered seat"
        assert R.lookup_misses() == [], (
            f"a registered seat was recorded as a miss: {R.lookup_misses()}")

    def test_the_ceiling_is_the_tables_own_value(self):
        assert rc.model_context_ceiling(_mc("CC2")) == rc.MODEL_SPECS[
            rc._spec_key("CC2")]["L"]
        assert R.lookup_misses() == []


class TestAnAbsentSeatIsRecordedAndNotChanged:
    def test_the_ceiling_still_defaults_to_infinity(self):
        """BEHAVIOUR MUST NOT CHANGE. C18 chose to record and still default."""
        assert rc.model_context_ceiling(_mc(ABSENT)) == float("inf")

    def test_the_absent_ceiling_is_recorded(self):
        rc.model_context_ceiling(_mc(ABSENT))
        rows = [r for r in R.lookup_misses() if r["key"] == ABSENT]
        assert rows, "the absent ceiling defaulted and nothing recorded it"
        assert any("context-budget ceiling" in r["what"] for r in rows)

    def test_the_absent_fingerprint_and_spec_are_both_recorded(self):
        rc.build_model_specs(_cfg(ABSENT))
        whats = {r["what"] for r in R.lookup_misses() if r["key"] == ABSENT}
        assert any("initial capability fingerprint" in w for w in whats), whats
        assert any("model spec" in w for w in whats), whats

    def test_every_recorded_row_carries_a_capability_identity(self):
        rc.build_model_specs(_cfg(ABSENT))
        rows = [r for r in R.lookup_misses() if r["key"] == ABSENT]
        assert rows
        for r in rows:
            assert r["identity"] and r["identity"] != "unresolved", (
                f"a row carries no usable identity: {r}")


class TestFableIsTheRealisedCase:
    def test_fable_has_a_spec_and_no_fingerprint(self):
        """If this ever fails, the gap was closed and the rest is history."""
        if "Fable" in rc.INITIAL_FINGERPRINTS:
            pytest.skip("Fable now has a fingerprint entry; the gap is closed")
        assert "Fable" in rc.MODEL_SPECS

    def test_fables_spec_records_that_it_is_borrowed(self):
        """The asymmetry: the spec table records a borrowed value."""
        spec = rc.MODEL_SPECS.get("Fable", {})
        notes = [v for k, v in spec.items() if k.startswith("_")]
        assert notes, "the spec table no longer records Fable's borrowed origin"
        assert any("not measured" in str(v) for v in notes), notes

    def test_fables_fingerprint_default_is_now_recorded(self):
        if "Fable" in rc.INITIAL_FINGERPRINTS:
            pytest.skip("Fable now has a fingerprint entry; the gap is closed")
        rc.build_model_specs(_cfg("Fable"))
        rows = [r for r in R.lookup_misses()
                if r["key"] == "Fable" and "fingerprint" in r["what"]]
        assert rows, (
            "Fable's fingerprint still defaults with nothing recording it, which "
            "is the whole finding this file guards")

    def test_the_substitute_is_worse_than_every_measured_seat(self):
        """The consequence, asserted rather than described."""
        sub = rc.CapabilityFingerprint(0.2, 0.7, 0.7, 0.5)
        measured = list(rc.INITIAL_FINGERPRINTS.values())
        assert measured, "no measured fingerprints to compare against"
        for axis in ("v_bar", "A", "C"):
            lo = min(getattr(m, axis) for m in measured)
            assert getattr(sub, axis) < lo, (
                f"the silent substitute's {axis} is no longer below every "
                f"measured seat, so the finding's premise has changed")
