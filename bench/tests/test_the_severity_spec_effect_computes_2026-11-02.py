"""`_severity_spec_effect` must COMPUTE, not record an exception.

WHY. The severity specification's distinguishing claim is that a DISPROVED
finding is annihilated rather than reduced, and `mode_effects` carries the field
that witnesses it. That field had never once been computed: the producer iterated
`registry.entries`, which is a dict keyed by finding id, so the loop variable was
the id STRING and `.get` raised `AttributeError: 'str' object has no attribute
'get'` on the first entry. The surrounding `except` wrote the message into the
report and the run continued, so the failure was PRESERVED IN THE EVIDENCE and
read by nobody.

MEASURED: of the archived reports carrying the field, 2 of 2 hold the
AttributeError and 0 hold a computed count, Wilson 95% [0.342380, 1.000000]. The
field arrived on 2026-10-28, so the mode effect was unobservable for every run of
its existence.

WHY THIS GUARD DOES NOT NEED A LIVE DEFECT, per
`feedback_a_regression_guard_must_not_need_a_live_defect_2026-10-31`. It does not
scan the archive for errors, because once the producer is fixed the archive stops
supplying the case and the guard goes vacuous without anyone noticing. It CALLS
the helper on constructed registries of both shapes and asserts the counts, so it
keeps testing the property after the defect is gone.

AND IT IS A CALL, NOT A READ, per `execute-do-not-grep`. The reason the defect
survived is that 6 lines inside a 3,400-line function could not be called by
anything. Extracting them is what makes this file possible.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(REPO / "bench") not in sys.path:
    sys.path.insert(0, str(REPO / "bench"))

import bench.reference_runner_v3 as rrv3                       # noqa: E402


def _entry(cid: str, verdict: str, severity: float) -> dict:
    return {"cid": cid, "falsifier_verdict": verdict, "severity": severity}


class TestItComputesInsteadOfRaising:

    def test_a_dict_keyed_registry_is_read_by_value(self):
        """THE EXACT SHAPE THAT BROKE IT. `registry.entries` is a dict."""
        entries = {
            "C0001": _entry("C0001", "CONFIRMED", 0.8),
            "C0002": _entry("C0002", "REFUTED", 0.5),
            "C0003": _entry("C0003", "REFUTED", 0.5),
        }
        out = rrv3._severity_spec_effect(entries)
        assert out["refuted_findings"] == 2, (
            f"a dict-keyed registry gave {out}; iterating a dict yields its KEYS, "
            f"which is the defect this guard exists for")

    def test_it_never_raises_on_a_dict(self):
        """The old code raised here, and the raise was swallowed into the report."""
        try:
            rrv3._severity_spec_effect({"C1": _entry("C1", "REFUTED", 0.5)})
        except AttributeError as e:                            # pragma: no cover
            pytest.fail(f"still raises on the real shape: {e}")

    def test_a_sequence_is_also_accepted(self):
        """Accepting either shape is deliberate: a shape assumption is what failed."""
        out = rrv3._severity_spec_effect([_entry("C1", "REFUTED", 0.5)])
        assert out["refuted_findings"] == 1

    def test_none_and_empty_are_zero_not_an_error(self):
        for empty in (None, {}, []):
            out = rrv3._severity_spec_effect(empty)
            assert out == {"refuted_findings": 0, "refuted_scored_zero": 0}, \
                f"{empty!r} gave {out}"

    def test_a_non_mapping_member_is_skipped_not_fatal(self):
        """A stray id in a sequence must not kill the telemetry for the rest."""
        out = rrv3._severity_spec_effect(["C0001", _entry("C2", "REFUTED", 0.5)])
        assert out["refuted_findings"] == 1


class TestTheVerdictPredicate:

    def test_only_refuted_counts(self):
        entries = {
            "a": _entry("a", "CONFIRMED", 0.9),
            "b": _entry("b", "UNCONFIRMED", 0.9),
            "c": _entry("c", "", 0.9),
            "d": _entry("d", "REFUTED", 0.9),
        }
        assert rrv3._severity_spec_effect(entries)["refuted_findings"] == 1

    def test_the_verdict_match_is_case_and_space_insensitive(self):
        entries = {"a": _entry("a", "  refuted  ", 0.5)}
        assert rrv3._severity_spec_effect(entries)["refuted_findings"] == 1

    def test_a_missing_verdict_key_does_not_raise(self):
        assert rrv3._severity_spec_effect({"a": {"severity": 0.5}}) == \
            {"refuted_findings": 0, "refuted_scored_zero": 0}


class TestItCallsEffectiveSeverityRatherThanReadingTheField:
    """The distinction the producer's own comment insists on: the STORED field
    holds the asserted number and the specification does not mutate it."""

    def test_scored_zero_follows_effective_severity_not_the_stored_field(self, monkeypatch):
        entries = {"a": _entry("a", "REFUTED", 0.5)}
        monkeypatch.setattr(rrv3, "effective_severity", lambda e: 0.0)
        out = rrv3._severity_spec_effect(entries)
        assert out == {"refuted_findings": 1, "refuted_scored_zero": 1}, (
            "with effective severity 0.0 a refuted finding must count as "
            "annihilated, whatever its stored severity says")

    def test_a_refuted_finding_that_does_not_annihilate_is_counted_but_not_zeroed(
            self, monkeypatch):
        entries = {"a": _entry("a", "REFUTED", 0.5)}
        monkeypatch.setattr(rrv3, "effective_severity", lambda e: 0.5)
        out = rrv3._severity_spec_effect(entries)
        assert out == {"refuted_findings": 1, "refuted_scored_zero": 0}, (
            "this is the case that would show the specification NOT working, so "
            "it must be distinguishable from the working one")


class TestTheCallSiteUsesIt:

    def test_run_experiment_calls_the_helper(self):
        """Otherwise the extraction is an addition nothing reaches."""
        import inspect
        src = inspect.getsource(rrv3.run_experiment)
        assert "_severity_spec_effect(registry.entries)" in src, (
            "run_experiment no longer calls the helper, so the repaired "
            "computation reaches no run")
