"""Focused test suite for the Exp 40 plan-D collision-detector slice
(bench/exp40_baseline/_feedback_collision_slice).

These are the TestDetection cases plus the pure-leaf no-mutation
invariant from test_finding_id_collision_detector.py, re-pointed at the
standalone slice. This file is the canonical-suite gate for the
collision-detector unit's hardened-gate convergence run (config
test_cmd): the apply-back loop promotes a verified fix into the slice
working copy only if this suite still passes cumulatively.

Scope note: the live-module wiring tests (runner accumulator-clear,
collision-safe routing through build_feedback_records, the last-wins
comprehension-behaviour invariant) are deliberately NOT ported here —
they test bench.dm._feedback + the runner, not the detector leaf in
isolation, and including them would couple this slice's apply-back gate
to non-slice code. The slice gate tests exactly what the slice is: a
pure observation-only detector.
"""
from __future__ import annotations

import pytest

from bench.exp40_baseline import _feedback_collision_slice as fb
from bench.exp40_baseline._feedback_collision_slice import (
    detect_finding_id_collisions,
)


class _F:
    """Minimal Finding stand-in (detector only reads
    finding_id/model_id)."""

    def __init__(self, fid, mid):
        self.finding_id = fid
        self.model_id = mid


@pytest.fixture(autouse=True)
def _reset_accumulator():
    fb._finding_id_collisions.clear()
    yield
    fb._finding_id_collisions.clear()


class TestDetection:
    def test_distinct_prefixed_ids_no_collision(self):
        # The panel's empirical point: model-prefixed ids do not
        # collide cross-model.
        out = detect_finding_id_collisions(
            [_F("CC2_F001", "CC2"), _F("Gemini_F001", "Gemini"),
             _F("CC2_F002", "CC2")], 5,
        )
        assert out == []
        assert fb._finding_id_collisions == []

    def test_same_model_duplicate_detected(self):
        out = detect_finding_id_collisions(
            [_F("CC2_F001", "CC2"), _F("CC2_F001", "CC2")], 6,
        )
        assert len(out) == 1
        rec = out[0]
        assert rec["finding_id"] == "CC2_F001"
        assert rec["count"] == 2
        assert rec["model_ids"] == ["CC2"]
        assert rec["cross_model"] is False
        assert rec["round"] == 6

    def test_cross_model_duplicate_detected(self):
        # The exact case UUID-namespace targets — the Exp 41 go/no-go
        # signal.
        out = detect_finding_id_collisions(
            [_F("F001", "CC2"), _F("F001", "Gemini")], 7,
        )
        assert len(out) == 1
        rec = out[0]
        assert rec["cross_model"] is True
        assert rec["model_ids"] == ["CC2", "Gemini"]
        assert rec["count"] == 2

    def test_accumulator_persists_for_postmortem(self):
        detect_finding_id_collisions(
            [_F("F001", "CC2"), _F("F001", "Gemini")], 7,
        )
        detect_finding_id_collisions(
            [_F("X", "DeepSeek"), _F("X", "DeepSeek")], 8,
        )
        assert len(fb._finding_id_collisions) == 2
        rounds = sorted(r["round"] for r in fb._finding_id_collisions)
        assert rounds == [7, 8]

    def test_none_finding_id_ignored(self):
        out = detect_finding_id_collisions(
            [_F(None, "CC2"), _F(None, "Gemini")], 9,
        )
        assert out == []

    def test_triple_collision_counted(self):
        out = detect_finding_id_collisions(
            [_F("F001", "CC2"), _F("F001", "Gemini"),
             _F("F001", "DeepSeek")], 10,
        )
        assert out[0]["count"] == 3
        assert out[0]["cross_model"] is True
        assert len(out[0]["model_ids"]) == 3


class TestPureLeafInvariant:
    """The detector is observation-only: it must never mutate, reorder,
    or drop its input. This is the slice-local contract (the live-module
    last-wins comprehension behaviour is tested against bench.dm in the
    full suite, not here)."""

    def test_detector_does_not_mutate_input(self):
        a = _F("F001", "CC2")
        b = _F("F001", "Gemini")
        findings = [a, b]
        before = list(findings)
        detect_finding_id_collisions(findings, 1)
        assert findings == before
        assert findings[0] is a and findings[1] is b

    def test_detector_returns_new_list_each_call(self):
        out1 = detect_finding_id_collisions([_F("F001", "CC2")], 1)
        out2 = detect_finding_id_collisions([_F("F002", "CC2")], 2)
        assert out1 == [] and out2 == []
        # no-collision calls leave the accumulator empty
        assert fb._finding_id_collisions == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
