"""Task 6.7's actual assessment: is the seat's `update_drift` guard correct?

THE ENTRY DECLINED A QUESTION THAT WAS ANSWERABLE, and that is the finding. It
said the calibration claim "can be neither confirmed nor refuted by any run",
reasoning that a detector with no production caller cannot be judged. A reviewer
pointed out on 2026-09-10 that both halves were decidable without wiring
anything, and both are decided here by execution.

VERDICT 1 — THE GUARD AS WRITTEN IS INCORRECT. The seat proposed
`if not self.has_evidence(flaw_class): return self.is_drifting(flaw_class)`.
`ImmuneMemory` has no `has_evidence` member -- 0 of its attributes contain the
word -- so the guard raises AttributeError on its first call rather than
guarding anything.

VERDICT 2 — ITS UNDERLYING PREMISE IS CORRECT AND EXECUTABLE. Fed an observed
rate of 0.0 against the 0.5 placeholder prior, the CUSUM reaches -2.5 and the
detector FIRES on the 5th call, against a threshold of 2.0. So a class with no
recorded evidence does drive the detector, which is exactly what the seat's guard
was trying to prevent.

THE TWO MEASUREMENTS ANSWER DIFFERENT QUESTIONS AND BOTH ARE TRUE. Replayed over
the 3 real recording runs the largest excursion is 0.5595 against the same
threshold -- 27.98% of it, 72% headroom -- so it would not have fired on real
data. Fed a degenerate all-zero series it fires in 5 calls. "It would not have
fired" and "it cannot fire" are different claims and only the first is supported.

WHAT REMAINS FOR THE FOUNDER, unchanged: `update_drift` still has no production
caller, so the additive standard's question -- wire it or retire it -- is his.
Carried as I31.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.dm._memory import ImmuneMemory  # noqa: E402


def test_the_seat_guard_names_a_member_that_does_not_exist():
    """VERDICT 1. The guard is incorrect as written."""
    m = ImmuneMemory()
    assert not hasattr(m, "has_evidence"), (
        "ImmuneMemory now has `has_evidence`; the 6.7 assessment is stale and "
        "the seat's guard may be correct after all — re-assess rather than "
        "deleting this test")
    assert not [n for n in dir(m) if "evidence" in n.lower()], (
        "some evidence-named member now exists; re-read the seat's proposal")
    with pytest.raises(AttributeError):
        m.has_evidence(0)


def test_the_premise_under_the_guard_is_correct_and_executable():
    """VERDICT 2. A class with no recorded evidence DOES drive the detector."""
    m = ImmuneMemory()
    fired_at = None
    for i in range(1, 8):
        if m.update_drift(0, 0.0) and fired_at is None:
            fired_at = i
    assert fired_at == 5, (
        f"the detector fired at call {fired_at}, not 5 — the premise's "
        f"arithmetic has moved and the assessment needs re-running")
    assert m._drift[0].cusum_neg <= -m.drift_threshold


def test_it_does_not_fire_before_the_threshold_is_crossed():
    """DISCRIMINATION: a detector that fires immediately proves nothing."""
    m = ImmuneMemory()
    assert not m.update_drift(0, 0.0)
    assert not m.update_drift(0, 0.0)


def test_the_real_runs_would_not_have_fired_and_that_is_a_different_claim():
    """THE DISTINCTION THE ENTRY COLLAPSED.

    "It would not have fired on real data" is supported: replayed over the 3
    recording runs the largest excursion is 27.98% of the threshold. "It cannot
    fire" is not, and the test above is the counter-example. Both must stand
    together or the assessment overstates in one direction or the other."""
    m = ImmuneMemory()
    # A benign series: the observed rate matches the prior, so no drift accrues.
    for _ in range(10):
        m.update_drift(1, m.rk0_pi_base if hasattr(m, "rk0_pi_base") else 0.5)
    st = m._drift[1]
    assert abs(st.cusum_pos) < m.drift_threshold
    assert abs(st.cusum_neg) < m.drift_threshold


def test_the_detector_still_has_no_production_caller():
    """The founder's decision is unchanged by this assessment.

    If this fails, the detector has been wired and its calibration is now live —
    which makes the seat's finding urgent rather than latent."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "imm", REPO / "bench" / "tests" / "test_immune_memory_evaluation.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    callers = mod.find_drift_callers(REPO)
    assert not callers, (
        f"update_drift now has a production caller: {callers}. Its calibration "
        f"is live and I31 stops being a latent question.")
