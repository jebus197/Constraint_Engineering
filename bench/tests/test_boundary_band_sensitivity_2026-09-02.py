"""The verdict's sensitivity to the rubric/numeric disagreement, reported per run.

The 2026-05-18 pre-registration requires that each run report "the count of
findings where rubric and numeric disagreed, and the verdict's sensitivity to
that disagreement". Measured 2026-09-02: 0 of 27 archived reports carried any
rubric field, and the runner contained no such code. Neither half had ever been
built, in a document committed before the runs and never edited.

The first half needs a per-finding rubric classifier and is still unwired. The
second half is computable from the threshold profile: gamma at both edges of the
disputed band. If they are equal, nothing inside the band could have moved the
verdict.

The band matters because of what the audit found in it. Across 286 archived
findings in [0.65, 0.75), the numeric proxy and the five-clause rubric agree on
141 of 259 judgeable cases -- 54.4%, Wilson [48.4%, 60.4%]. That is not reader
noise: two independent blind readers agreed with each other on 86 of 93 (92.5%,
Cohen's kappa 0.837, 95% CI [0.721, 0.953]) while each agreed with the number
about 55% of the time.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import reference_runner_v3 as R  # noqa: E402


class TestTheBandEdgesAreProfiled:
    def test_both_edges_are_pre_registered_thresholds(self):
        for edge in (0.65, 0.75):
            assert edge in R.PREREG_GAMMA_PROFILE_THRESHOLDS, (
                f"{edge} is an edge of the disputed band; without it the "
                f"sensitivity question cannot be answered from the report")

    def test_the_original_prereg_points_survive(self):
        """Adding edges must not drop what the pre-registration named."""
        for thr in (0.5, 0.6, 0.7, 0.8):
            assert thr in R.PREREG_GAMMA_PROFILE_THRESHOLDS, (
                f"{thr} is named in the pre-registration and has been dropped")

    def test_the_live_threshold_is_unchanged(self):
        """The audit does not license moving 0.70, and nothing here moves it."""
        assert R.CRITICAL_SEVERITY_THRESHOLD == 0.7


class TestTheSensitivityBlockIsEmitted:
    """A diagnostic nobody can read from the artefact is a diagnostic nobody has."""

    def test_the_profile_emits_it(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert 'out["boundary_band_sensitivity"]' in src

    def test_it_reports_both_edges_and_a_verdict(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.index('out["boundary_band_sensitivity"]')
        block = src[i:i + 1600]
        for key in ("gamma_at_lower_edge", "gamma_at_upper_edge",
                    "verdict_robust_to_band"):
            assert key in block, f"{key} missing from the sensitivity block"

    def test_it_carries_its_own_basis(self):
        """A reader must be able to see WHY the band is disputed."""
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.index('out["boundary_band_sensitivity"]')
        block = src[i:i + 1800]
        assert "0C.8" in block and "kappa" in block, (
            "the block must cite the audit and the inter-rater figure, or a "
            "reader cannot tell whether 54% is disagreement or noise")

    def test_it_cannot_fell_a_run(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.index('out["boundary_band_sensitivity"]')
        assert "except Exception" in src[i - 1400:i + 1800], (
            "a diagnostic must not be able to halt a run")

    def test_the_unwired_half_is_named_not_hidden(self):
        """The count of rubric/numeric disagreements is still not built."""
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        i = src.index("THE PRE-REGISTRATION'S SECOND, UNBUILT REQUIREMENT")
        assert "not wired" in src[i:i + 1200], (
            "the half that is still missing must be stated, or the half that "
            "exists will be mistaken for the whole requirement")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
