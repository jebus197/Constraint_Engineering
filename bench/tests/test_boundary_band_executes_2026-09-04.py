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


def _band_discriminating() -> _Registry:
    """Both edges MEASURED, and they differ. Added 2026-10-16 (CC3).

    This is what `_band_sensitive` was always trying to be. That fixture puts
    every critical INSIDE [0.65, 0.75), so the upper edge sees an all-zero
    series and `_estimate_gamma` returns its 0.0 sentinel: the upper edge is
    not a different slope, it is no slope at all. The pre-2026-10-16 code
    compared the two numbers for equality and called that False, which is the
    "one real edge against a sentinel" false alarm that
    `scripts/the_band_verdict_rests_on_a_sentinel_2026-10-16.py` counts at
    4 of 26 archived blocks.

    Here the above-band series 4,3,2,1 at severity 0.95 keeps the UPPER edge
    estimable on its own, and ONE extra in-band critical in the final round
    moves the LOWER edge only. Executed 2026-10-16: lower 0.2727, upper
    0.3247, both estimable and both non-zero, so the inequality is between two
    MEASURED slopes and `verdict_robust_to_band` is genuinely False.
    """
    return _Registry(
        [_finding(r, 0.95) for r in range(0, 4) for _ in range(4 - r)]
        + [_finding(3, 0.70)]
    )


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
        for name, reg in (("inert", _band_inert()),
                          ("sensitive", _band_sensitive()),
                          ("discriminating", _band_discriminating())):
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

    def test_it_returns_false_for_a_band_discriminating_registry(self):
        """Two MEASURED slopes that differ. The genuine False.

        CORRECTED 2026-10-16 (CC3). This assertion previously ran against
        `_band_sensitive()`, whose upper edge is the `_estimate_gamma` 0.0
        SENTINEL rather than a slope, so it was asserting a verdict on a
        quantity that was never measured -- the defect the estimability gate
        was added to remove. The assertion is not weakened: it is moved onto a
        fixture where both edges are real, and `_band_sensitive()` keeps its
        own assertion immediately below. Both edges are additionally required
        to be estimable and non-zero here, so the test cannot pass by the two
        edges being a clamped zero apiece.
        """
        s = R.gamma_threshold_profile(_band_discriminating(),
                                      max_round=3)["boundary_band_sensitivity"]
        assert s["gamma_estimable_at_lower_edge"] is True, s
        assert s["gamma_estimable_at_upper_edge"] is True, s
        assert s["gamma_at_lower_edge"] not in (None, 0.0), s
        assert s["gamma_at_upper_edge"] not in (None, 0.0), s
        assert s["gamma_at_lower_edge"] != s["gamma_at_upper_edge"], s
        assert s["band_is_readable"] is True, s
        assert s["verdict_robust_to_band"] is False, (
            "one in-band critical is counted at the lower edge and not at the "
            f"upper, and both edges are measured, so the verdict is fragile; got {s}")

    def test_a_sentinel_upper_edge_reports_no_verdict_rather_than_a_false_one(self):
        """`_band_sensitive()` is the false-alarm class, and must now be null.

        Its whole critical set sits inside the band, so at the 0.75 edge the
        novelty series is all zeros and gamma is the sentinel. Reading that as
        "the verdict changed across the band" is a false alarm. The edge values
        are still reported -- only the verdict that cannot rest on them is
        withheld.
        """
        s = R.gamma_threshold_profile(_band_sensitive(),
                                      max_round=3)["boundary_band_sensitivity"]
        assert s["gamma_estimable_at_lower_edge"] is True, s
        assert s["gamma_estimable_at_upper_edge"] is False, s
        assert s["band_is_readable"] is False, s
        assert s["verdict_robust_to_band"] is None, s
        assert s["gamma_at_lower_edge"] is not None, s
        assert s["gamma_at_upper_edge"] is not None, s

    def test_all_three_outcomes_are_reachable(self):
        """The single assertion the source-text guard could never make.

        STRENGTHENED 2026-10-16 (CC3) from {True, False} to {True, False,
        None}. The estimability gate added a third value, and an unreachable
        third value would be exactly the constant this class exists to forbid.
        Every registry here is a REAL one driven through the real series
        reader: `test_the_band_verdict_is_gated_on_estimability_2026-10-16.py`
        reaches the same three values by monkeypatching
        `_settled_novelty_series`, which stubs out one of the two halves this
        file's docstring says must be run against each other.
        """
        got = {
            R.gamma_threshold_profile(r, max_round=3)["boundary_band_sensitivity"]["verdict_robust_to_band"]
            for r in (_band_inert(), _band_sensitive(), _band_discriminating())
        }
        assert got == {True, False, None}, (
            f"verdict_robust_to_band produced only {got}; a diagnostic that "
            "cannot take all three values is reporting a constant")
