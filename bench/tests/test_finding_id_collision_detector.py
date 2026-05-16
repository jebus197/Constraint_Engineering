"""Regression tests for the Exp 40 timing re-confer (2026-05-16)
finding-ID collision detector.

Context: the neutral confer converged that the UUID-namespace
architectural change is real but unobserved, and deferred it to
pre-Exp-41 ON CONDITION that R17-R21 is instrumented to turn the
theoretical collision-overwrite into an observable. This detector is
that instrument. It is OBSERVATION-ONLY: it must detect and record a
shared-finding_id collision (the silent-overwrite condition the panel
diagnosed at `_feedback.py` `{f.finding_id: f for f in findings}`)
WITHOUT changing that comprehension or any dedup/merge behaviour.

These tests pin:
  1. No collision on distinct ids (incl. the model-prefixed
     convention CC2_F001 vs Gemini_F001 — the panel's "rare in
     practice" point).
  2. Same-model duplicate detected, cross_model=False.
  3. Cross-model duplicate detected, cross_model=True, model_ids
     captured (the exact case UUID-namespace targets; the Exp 41
     go/no-go signal).
  4. Module accumulator records collisions for post-mortem retrieval.
  5. OBSERVATION-ONLY INVARIANT: build_feedback_records produces a
     byte-identical result whether or not a collision is present in
     the way the detector would have to NOT perturb — i.e. the
     `finding_by_id` comprehension behaviour is unchanged (last
     finding wins, exactly as before the detector existed).
"""

from __future__ import annotations

import pytest

from bench.dm import _feedback as fb
from bench.dm._feedback import detect_finding_id_collisions


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


class TestObservationOnlyInvariant:
    """The detector must NOT change the
    `{f.finding_id: f for f in findings}` behaviour. The comprehension
    keeps last-wins semantics exactly as before the detector existed;
    the detector only records that this happened."""

    def test_comprehension_behaviour_unchanged(self):
        # Reproduce the exact comprehension the production code runs
        # immediately after the detector call.
        a = _F("F001", "CC2")
        b = _F("F001", "Gemini")
        findings = [a, b]
        # Detector runs first (as in build_feedback_records).
        detect_finding_id_collisions(findings, 1)
        finding_by_id = {f.finding_id: f for f in findings}
        # Last-wins is preserved: b overwrote a, exactly as it would
        # have WITHOUT the detector. The detector did not mutate
        # findings, reorder them, or alter the map.
        assert finding_by_id["F001"] is b
        assert len(finding_by_id) == 1
        # And the collision was recorded (observation happened).
        assert len(fb._finding_id_collisions) == 1

    def test_detector_does_not_mutate_input(self):
        a = _F("F001", "CC2")
        b = _F("F001", "Gemini")
        findings = [a, b]
        before = list(findings)
        detect_finding_id_collisions(findings, 1)
        assert findings == before
        assert findings[0] is a and findings[1] is b


class TestRunnerWiring:
    """The runner must clear the accumulator at experiment start and
    call the detector at the comprehension site."""

    def test_runner_clears_accumulator_reference(self):
        import bench.reference_runner_v2 as rr
        src = __import__("pathlib").Path(rr.__file__).read_text()
        assert "_feedback_mod._finding_id_collisions.clear()" in src, (
            "runner must clear the collision accumulator at "
            "experiment start (post-mortem reads this run only)"
        )

    def test_detector_called_at_comprehension_site(self):
        src = __import__("pathlib").Path(fb.__file__).read_text()
        i_det = src.index("detect_finding_id_collisions(findings, round_idx)")
        i_comp = src.index("finding_by_id = {f.finding_id: f for f in findings}")
        assert i_det < i_comp, (
            "detector must run immediately BEFORE the collision-prone "
            "comprehension"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
