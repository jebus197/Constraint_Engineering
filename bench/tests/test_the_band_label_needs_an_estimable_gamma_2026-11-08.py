"""The gamma band label may not be applied to the estimator's 0.0 sentinel.

THE DEFECT: `gamma-band-label-is-applied-to-an-unestimable-gamma`, observed live
2026-10-15 in free run 1, ruled by the founder 2026-10-16 ("Fix it all").
`_estimate_gamma` returns 0.0 as a SENTINEL for 4 distinct non-measurements and
the lowest band reads "Gamma disagrees with state closure -- recommend HIL
audit", so the first 2 rounds of EVERY run referred the founder to a quantity
that had not been measured.

WHY THIS FILE EXISTS BESIDE THE 2026-10-08 GUARD RATHER THAN INSIDE IT.
`bench/tests/test_gamma_gates_wherever_it_exists_2026-10-08.py` holds 30 tests
on the GATE and on the estimator/predicate mirror, and 0 of them reach
`_interpret_gamma`. The gate was taught to separate the sentinel from a slope on
2026-10-08; the human-facing LABEL was not. This file guards the label.

IT ASSERTS BEHAVIOUR BY CALLING, NOT BY READING SOURCE -- except for the 1 claim
that cannot be executed without running a full experiment round, where the call
site is checked STRUCTURALLY through the AST rather than by substring, because a
substring test cannot follow a call when it moves.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
AUDIT_WORDS = ("recommend hil audit", "disagrees with state closure")


@pytest.fixture(scope="module")
def R():
    spec = importlib.util.spec_from_file_location("rr_band", RUNNER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["rr_band"] = m
    spec.loader.exec_module(m)
    return m


class TestTheDefectWasReal:
    """ANTI-VACUITY. If these fail, the thing being guarded never happened."""

    #: Series covering 3 of the 4 sentinel reasons, each a real shape a run hits.
    SENTINELS = [
        ("too few rounds", [1, 1]),
        ("nothing ever found", [0, 0, 0, 0, 0]),
        ("single usable log point", [0, 0, 1]),
    ]

    @pytest.mark.parametrize("label,series", SENTINELS)
    def test_the_estimator_returns_the_sentinel_and_the_predicate_says_so(
            self, R, label, series):
        assert R._estimate_gamma(series) == 0.0, label
        assert R._gamma_is_estimable(series) is False, label

    @pytest.mark.parametrize("label,series", SENTINELS)
    def test_the_unguarded_band_WOULD_have_demanded_an_audit(
            self, R, label, series):
        """The defect, stated as a measurement rather than as a recollection."""
        g = R._estimate_gamma(series)
        unguarded = R._interpret_gamma(g, True)
        assert any(w in unguarded.lower() for w in AUDIT_WORDS), (
            f"{label}: the lowest band no longer demands an audit, so this "
            f"file's premise has changed. Re-read GAMMA_BANDS before trusting "
            f"any verdict here.")


class TestTheLabelNowRefusesTheSentinel:

    @pytest.mark.parametrize("label,series", TestTheDefectWasReal.SENTINELS)
    def test_an_unestimable_gamma_gets_no_band_and_no_audit(
            self, R, label, series):
        g = R._estimate_gamma(series)
        out = R._interpret_gamma(g, R._gamma_is_estimable(series))
        low = out.lower()
        assert not any(w in low for w in AUDIT_WORDS), (
            f"{label}: an unestimable gamma still asks for a human audit:\n"
            f"  {out}")
        assert "estimable" in low, (
            f"{label}: the label does not say WHY no band applies:\n  {out}")

    def test_it_names_the_sentinel_rather_than_merely_staying_silent(self, R):
        out = R._interpret_gamma(0.0, False).lower()
        assert "sentinel" in out or "not a slope" in out, out


class TestNothingThatWorKedBeforeChanged:
    """The additive half: no band removed, no threshold moved, default intact."""

    def test_the_default_is_estimable_so_old_callers_are_unchanged(self, R):
        import inspect
        sig = inspect.signature(R._interpret_gamma)
        assert sig.parameters["estimable"].default is True

    @pytest.mark.parametrize("gamma,fragment", [
        (0.10, "disagrees with state closure"),
        (0.25, "weak depletion"),
        (0.35, "moderate depletion"),
        (0.60, "strong depletion"),
    ])
    def test_every_band_still_returns_its_own_wording(self, R, gamma, fragment):
        assert fragment in R._interpret_gamma(gamma).lower()

    def test_a_low_but_ESTIMABLE_gamma_still_demands_an_audit(self, R):
        """THE DISCRIMINATION TEST. A real low slope must NOT be softened."""
        series = [1, 2, 3, 4, 5]                 # still climbing: a real slope
        assert R._gamma_is_estimable(series) is True
        g = R._estimate_gamma(series)
        assert g < 0.20, g
        out = R._interpret_gamma(g, True).lower()
        assert any(w in out for w in AUDIT_WORDS), (
            "a genuinely low ESTIMABLE gamma stopped recommending an audit, "
            "which would be demoting gamma rather than repairing a label.")

    def test_the_band_table_still_has_all_4_bands(self, R):
        assert len(R.GAMMA_BANDS) == 4


class TestTheCallSitePassesIt:
    """STRUCTURAL, because executing it needs a full experiment round.

    An AST check, not a substring: a substring test cannot follow a call when it
    moves, and this project has 4 recorded defects found by executing 2 forms
    against each other and 0 found by reading.
    """

    def test_every_interpret_gamma_call_in_the_runner_supplies_estimability(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and getattr(n.func, "id", None) == "_interpret_gamma"]
        assert calls, ("no call to _interpret_gamma remains in the runner. If "
                       "the label was removed rather than gated, that is a "
                       "removal and needs its own justification.")
        bare = [c.lineno for c in calls
                if len(c.args) < 2 and not any(k.arg == "estimable"
                                               for k in c.keywords)]
        assert not bare, (
            f"these _interpret_gamma call(s) pass no estimability, so they can "
            f"still label a sentinel: lines {bare}")

    def test_the_estimability_comes_from_the_same_series_as_the_estimate(self):
        """Guards the failure where label and number describe different inputs."""
        src = RUNNER.read_text(encoding="utf-8")
        tree = ast.parse(src)
        est_args, lab_args = set(), set()
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            fid = getattr(n.func, "id", None)
            if fid == "_gamma_is_estimable" and n.args:
                est_args.add(ast.unparse(n.args[0]))
            if fid == "_estimate_gamma" and n.args:
                lab_args.add(ast.unparse(n.args[0]))
        assert est_args, "nothing calls _gamma_is_estimable in the runner"
        assert est_args <= lab_args, (
            f"_gamma_is_estimable is asked about series {est_args - lab_args} "
            f"that _estimate_gamma is never given, so the label and the number "
            f"can describe different inputs.")
