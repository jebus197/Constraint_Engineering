"""Regression tests for the Exp 40 finding-ID collision detector and the
2026-05-16 founder-directed collision-SAFE fix.

History: the 2026-05-16 neutral confer deferred the UUID-namespace
change and shipped an OBSERVATION-ONLY detector as an evidence gate.
The founder subsequently directed that the underlying silent-overwrite
defect be fixed outright (it mis-routes a model's corrective feedback to
another model, a churn / non-convergence driver). The prior
`finding_by_id = {f.finding_id: f for f in findings}` last-wins
comprehension is removed: `build_feedback_records` now accumulates a
per-id finding list and keys feedback records by (finding_id,
model_origin), so every model that emitted a colliding id is routed its
own record. The detector remains, now purely as post-mortem accounting.

These tests pin:
  1. No collision on distinct ids (incl. the model-prefixed
     convention CC2_F001 vs Gemini_F001).
  2. Same-model duplicate detected, cross_model=False.
  3. Cross-model duplicate detected, cross_model=True, model_ids
     captured.
  4. Module accumulator records collisions for post-mortem retrieval.
  5. COLLISION-SAFE INVARIANT: the silent-overwrite comprehension is
     gone, the detector is still called, and a cross-model id collision
     yields one correctly-routed feedback record PER model (no silent
     drop) rather than a single last-wins record.
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
    """The runner must clear the accumulator at experiment start; the
    detector must still be called; the silent-overwrite comprehension
    must be gone (collision-safe fix landed)."""

    def test_runner_clears_accumulator_reference(self):
        import bench.reference_runner_v3 as rr
        src = __import__("pathlib").Path(rr.__file__).read_text()
        assert "_feedback_mod._finding_id_collisions.clear()" in src, (
            "runner must clear the collision accumulator at "
            "experiment start (post-mortem reads this run only)"
        )

    def test_collision_safe_fix_landed_detector_still_called(self):
        """Post-fix invariant (supersedes the old comprehension-site
        test): the last-wins comprehension is removed, the detector is
        still called for post-mortem accounting, and the collision-safe
        structures (per-id list + (fid, model) keyed records) exist."""
        src = __import__("pathlib").Path(fb.__file__).read_text()
        assert "detect_finding_id_collisions(findings, round_idx)" in src, (
            "detector must still be called for post-mortem accounting"
        )
        assert "finding_by_id = {f.finding_id: f for f in findings}" \
            not in src, (
            "the silent-overwrite last-wins comprehension must be "
            "removed by the collision-safe fix"
        )
        assert "findings_by_id.setdefault(" in src, (
            "collision-safe per-id finding accumulation must be present"
        )
        assert "records: Dict[Tuple[str, str], FindingFeedback]" in src, (
            "feedback records must be keyed by (finding_id, "
            "model_origin) so colliding models are not dropped"
        )


class _Finding:
    """Finding stand-in for build_feedback_records (reads finding_id,
    model_id, severity)."""

    def __init__(self, fid, mid, sev=0.5):
        self.finding_id = fid
        self.model_id = mid
        self.severity = sev


class TestCollisionSafeRouting:
    """Behavioural guard for the founder-directed fix: a cross-model
    finding_id collision must yield one correctly-routed feedback
    record PER model, never a single last-wins record."""

    def test_cross_model_collision_yields_record_per_model(self):
        a = _Finding("X", "CC2", 0.7)
        b = _Finding("X", "Gemini", 0.4)
        recs = fb.build_feedback_records(
            round_idx=1,
            findings=[a, b],
            immune_result=None,
            admissibility_failures={"X": ["g1_ast"]},
        )
        origins = sorted(r.model_origin for r in recs)
        assert origins == ["CC2", "Gemini"], (
            f"both colliding models must each get a record; got {origins} "
            f"(pre-fix last-wins would yield exactly one)"
        )
        for r in recs:
            assert r.finding_id == "X"
            assert r.admissibility_failures == ["g1_ast"]
        # severity must be each finding's own, not one overwriting both
        sev = {r.model_origin: r.severity_claimed for r in recs}
        assert sev == {"CC2": 0.7, "Gemini": 0.4}

    def test_no_collision_unchanged_one_record(self):
        a = _Finding("A", "CC2", 0.6)
        b = _Finding("B", "Gemini", 0.3)
        recs = fb.build_feedback_records(
            round_idx=1,
            findings=[a, b],
            immune_result=None,
            admissibility_failures={"A": ["g2_compile"]},
        )
        assert len(recs) == 1
        assert recs[0].model_origin == "CC2"
        assert recs[0].finding_id == "A"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
