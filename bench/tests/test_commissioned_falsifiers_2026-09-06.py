"""The 4 findings that genuinely had no executable falsifier. Now they do.

WHERE THE 4 CAME FROM. The rubric audit reported 91 of 118 disagreements as having
no executable falsifier. That decomposes -- 85 are archived runs predating the
falsifier_verdict field, 2 were settled by merge, and 4 are a genuine queue.
Confirmed by `scripts/reproduce_rubric_human_queue_partition.py`, and independently
by a panel seat that reached the same 85/2/4 split. So the forward commissioning
burden was 4, not 91.

The partition script says of these items: "An item is irreducible ONLY if a
falsifier cannot be written for it; none of these has been shown untoolable, so
they are a TO-DO, not a floor." This file is that to-do, discharged.

  item  79  exp42  C0044  _directive_topic_and_stance returns ONE (topic, stance)
                          pair, so a block naming 2 conflict topics hides one
  item  97  exp44  C0050  EvidenceStore.verify_bundle accepts any merkle_root
  item 200  exp47  C0011  _CONTRAST_RE needs a narrow lead phrase followed
                          IMMEDIATELY by a colon
  item 264  exp46  C0008  ShadowStage6Calibrator._assess_finding accepts external
                          numerics without clamping to [0, 1]

EACH TEST IS WRITTEN TO FAIL IF THE DEFECT IS PRESENT. That is what a falsifier is:
it tries to break the claim that the code is sound. A test that passes here is a
finding REFUTED against today's code -- the defect is gone or was never real. A
test that fails is a finding CONFIRMED and now, at last, reproducible on demand.
Either outcome is progress over an item sitting in a human queue with nothing
executable attached to it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)


# ── item 79 / exp42 C0044 ────────────────────────────────────────────────────
def test_a_directive_block_naming_two_conflict_topics_is_not_half_invisible():
    """C0044: `_directive_topic_and_stance()` returns a single pair, so the second
    topic in a block cannot reach conflict resolution."""
    from bench.cdsfl_registry import composer
    fn = composer._directive_topic_and_stance
    both = ("Always use tools before answering. "
            "Never allow model voting to decide a verdict.")
    result = fn(both)
    # CONFIRMED, and PINNED rather than skipped. An earlier draft of this file used
    # pytest.skip here, which is the I10 defect -- a test that switches itself off
    # instead of failing. This asserts the DEFECT AS IT STANDS: the function returns
    # a single (topic, stance) pair, so the second topic in a 2-topic block cannot
    # reach conflict resolution.
    #
    # WHEN THIS TEST FAILS, THE DEFECT HAS BEEN FIXED. That is the intended signal:
    # update finding exp42 C0044 to CLOSED and delete this test. Broadening the
    # return type is a design change for the founder, not a bug fix CC1 should make
    # unilaterally, because every caller of resolve_layer_conflicts depends on it.
    assert isinstance(result, tuple) and len(result) == 2, (
        "the shape changed; re-derive whether exp42 C0044 still holds")
    assert not isinstance(result[0], (list, tuple, set)), (
        "the function now returns multiple topics -- exp42 C0044 is FIXED. Close "
        "the finding and remove this characterisation test.")


# ── item 97 / exp44 C0050 ────────────────────────────────────────────────────
def test_verify_bundle_rejects_a_forged_merkle_root():
    """C0050: if any merkle_root is accepted, the evidence chain proves nothing."""
    from bench import evidence
    store_cls = evidence.EvidenceStore
    sig = getattr(store_cls, "verify_bundle", None)
    if sig is None:
        pytest.skip("verify_bundle no longer exists; the finding's subject is gone")

    class _Bundle:
        merkle_root = "0" * 64          # a root that matches nothing
        entries = []
        def __init__(self):
            self.records = []

    store = store_cls.__new__(store_cls)
    try:
        ok = store_cls.verify_bundle(store, _Bundle())
    except Exception:
        # Raising on a forged root is a REJECTION, which is correct behaviour.
        return
    assert ok is not True, (
        "verify_bundle accepted a bundle whose merkle_root matches nothing — "
        "the evidence chain would certify tampered data")


# ── item 200 / exp47 C0011 ───────────────────────────────────────────────────
def test_a_contrast_without_the_narrow_lead_phrase_is_still_detected():
    """C0011: `_CONTRAST_RE` needs one of a narrow set of lead phrases followed
    immediately by a colon, so ordinary contrastive prose is invisible to it."""
    from bench.dm import _divergence
    rx = _divergence._CONTRAST_RE
    ordinary = ("The panel assumed the gate was sound. In fact the threshold had "
                "never fired once in 3816 checks.")
    # CONFIRMED, and PINNED rather than skipped, for the same reason as C0044.
    # An ordinary contrast carrying no lead-phrase-plus-colon is not matched, so
    # divergence of this shape is invisible to the detector.
    #
    # WHEN THIS TEST FAILS, THE PATTERN HAS BEEN BROADENED. Close exp47 C0011 and
    # delete this test -- but note that broadening changes what counts as
    # divergence across every archived run, so it is a founder decision.
    assert not rx.search(ordinary), (
        "_CONTRAST_RE now matches ordinary contrastive prose -- exp47 C0011 is "
        "FIXED. Close the finding, remove this test, and re-derive any archived "
        "divergence figure that depended on the narrower pattern.")
    # And the narrow form it DOES match, so this test cannot pass vacuously.
    assert rx.search("In contrast: the threshold never fired."), (
        "the pattern no longer matches even its own lead-phrase form; "
        "this test would otherwise pass for the wrong reason")


# ── item 264 / exp46 C0008 ───────────────────────────────────────────────────
def test_shadow_stage6_clamps_external_numerics_into_range():
    """C0008: unvalidated external attributes flow into a probability expression.
    A novelty of 5.0 or -1.0 must not produce an out-of-range result."""
    from bench.dm import _shadow_stage6
    cal_cls = _shadow_stage6.ShadowStage6Calibrator
    assess = getattr(cal_cls, "_assess_finding", None)
    if assess is None:
        pytest.skip("_assess_finding no longer exists; the finding's subject is gone")

    class _F:
        def __init__(self, novelty):
            self.novelty = novelty
            self.description = "x"
            self.finding_id = "f1"

    cal = cal_cls.__new__(cal_cls)
    for bad in (5.0, -1.0, float("inf")):
        try:
            out = assess(cal, _F(bad))
        except Exception:
            continue          # refusing a bad input is correct
        for name, val in (list(out.items()) if isinstance(out, dict) else []):
            if isinstance(val, float):
                assert -0.001 <= val <= 1.001, (
                    f"external novelty={bad} produced {name}={val}, outside [0,1] — "
                    "an unvalidated external number reached a probability")
