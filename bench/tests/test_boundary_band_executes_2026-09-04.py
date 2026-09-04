"""The band-sensitivity diagnostic must be EXECUTED, not grepped.

WHY THIS FILE EXISTS. `test_boundary_band_sensitivity_2026-09-02.py` guarded
this diagnostic with assertions over the runner's SOURCE TEXT -- it checked that
the string `out["boundary_band_sensitivity"]` appears in the file. It never
called the function. Under that guard the diagnostic shipped broken and stayed
broken: `gamma_threshold_profile` wrote its keys with `f"{thr:.1f}"`, which maps
0.65 -> "0.7" and 0.75 -> "0.8", so both band edges were silently overwritten by
the neighbouring thresholds. The consumer then looked up the literal "0.65" and
"0.75", found neither, and emitted `gamma_at_lower_edge: None`,
`gamma_at_upper_edge: None`, `verdict_robust_to_band: False` -- unconditionally,
for every registry that can exist. A constant wearing the costume of a
measurement, and worse than the honest "not wired here" the runner says about
the other half of the same pre-registration requirement.

Found 2026-09-04 by cc2 and fable independently, both executing the function
rather than reading it. Fix: `f"{thr:g}"`, two sites. Both reviewers verified it.

THE RULE THIS ENCODES. A test that asserts on source text asserts that the code
describes itself consistently. It cannot detect a producer and a consumer that
disagree about what a key looks like, because both descriptions are individually
correct. Only running both halves against each other finds that class, which is
this project's own founding principle applied to its own test suite.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import reference_runner_v3 as R  # noqa: E402


class _Registry:
    """Minimal stand-in: the series reader needs only `.entries`."""

    def __init__(self, entries):
        self.entries = {f"C{i:04d}": e for i, e in enumerate(entries)}


def _finding(round_idx: int, severity: float) -> dict:
    return {"open_since_round": round_idx, "severity": severity, "status": "OPEN"}


def _band_sensitive() -> _Registry:
    """Criticals sitting INSIDE [0.65, 0.75): counted at the lower edge, not the upper."""
    return _Registry([_finding(r, 0.70) for r in range(0, 4) for _ in range(4 - r)])


def _band_inert() -> _Registry:
    """Criticals well ABOVE the band: counted identically at both edges."""
    return _Registry([_finding(r, 0.95) for r in range(0, 4) for _ in range(4 - r)])


class TestTheProfileActuallyProducesTheBandEdges:
    def test_both_band_edge_keys_exist_in_the_output(self):
        prof = R.gamma_threshold_profile(_band_inert(), max_round=3)
        keys = set(prof["thresholds"])
        for edge in ("0.65", "0.75"):
            assert edge in keys, (
                f"band edge {edge!r} missing from the profile keys {sorted(keys)}. "
                "This is the key-collision regression: a .1f format maps 0.65 and "
                "0.75 onto their neighbours and the edges are overwritten.")

    def test_the_edges_are_not_none(self):
        for name, reg in (("inert", _band_inert()), ("sensitive", _band_sensitive())):
            s = R.gamma_threshold_profile(reg, max_round=3)["boundary_band_sensitivity"]
            assert s.get("gamma_at_lower_edge") is not None, f"{name}: lower edge None"
            assert s.get("gamma_at_upper_edge") is not None, f"{name}: upper edge None"


class TestTheVerdictDiscriminates:
    """A diagnostic that can only return one value is a constant, not a measurement."""

    def test_it_returns_true_for_a_band_inert_registry(self):
        s = R.gamma_threshold_profile(_band_inert(), max_round=3)["boundary_band_sensitivity"]
        assert s["verdict_robust_to_band"] is True, (
            "criticals well above the band must give identical gamma at both "
            f"edges, so the verdict is robust; got {s}")

    def test_it_returns_false_for_a_band_sensitive_registry(self):
        s = R.gamma_threshold_profile(_band_sensitive(), max_round=3)["boundary_band_sensitivity"]
        assert s["verdict_robust_to_band"] is False, (
            "criticals inside the band are counted at the lower edge and not at "
            f"the upper, so gamma must differ; got {s}")

    def test_both_outcomes_are_reachable(self):
        """The single assertion the source-text guard could never make."""
        got = {
            R.gamma_threshold_profile(r, max_round=3)["boundary_band_sensitivity"]["verdict_robust_to_band"]
            for r in (_band_inert(), _band_sensitive())
        }
        assert got == {True, False}, (
            f"verdict_robust_to_band produced only {got}; a diagnostic that "
            "cannot take both values is reporting a constant")
