"""The KEY PROPERTY survives every documented severity composition.

WHY THIS EXISTS (2026-11-06 severity panel). A proposed repair to
docs/MATHEMATICAL_APPENDIX.md section 7.7 deleted the KEY PROPERTY paragraph
and the V column and redirected to section 7.8. That deletion enacts a lossy
reading: section 7.8 Approach B's S_v never reaches 0 for finite evidence
(worked example: Lambda = -49/50 gives S_v = 0.27289178365887047, SymPy,
mpmath and Wolfram Language agreeing to 1e-15), so substituting S_v for
confidence * V assigns a disproved finding a positive severity. The appendix
now states the non-lossy substitution, Sev'(f) = W(class) * S_v(f) * V,
with V's hard zero retained. This test pins the hard zero to the REAL
implementation sites so a later edit cannot silently re-enact the deletion.
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

import reference_runner_v3 as rr  # noqa: E402


@pytest.fixture(autouse=True)
def _restore_flag():
    """_SEVERITY_SPEC is module state; save and restore around every test."""
    saved = dict(rr._SEVERITY_SPEC)
    try:
        yield
    finally:
        rr._SEVERITY_SPEC.clear()
        rr._SEVERITY_SPEC.update(saved)


class TestKeyPropertyInComputeSevF:
    def test_appendix_verified_examples_hold(self):
        assert rr.compute_sev_f("HARD", 0.9, "CONFIRMED") == pytest.approx(0.90)
        assert rr.compute_sev_f("HARD", 0.9, "REFUTED") == 0.0

    def test_refuted_annihilates_at_every_confidence_and_class(self):
        for cls in ("HARD", "SOFT", None, "junk"):
            for conf in (0.0, 0.3, 0.7, 1.0, None):
                assert rr.compute_sev_f(cls, conf, "REFUTED") == 0.0


class TestKeyPropertyInSpecVerificationFactor:
    def test_refuted_is_exactly_zero(self):
        assert rr.spec_verification_factor({"falsifier_verdict": "REFUTED"}) == 0.0

    def test_confirmed_and_unresolved(self):
        assert rr.spec_verification_factor({"falsifier_verdict": "CONFIRMED"}) == 1.0
        assert rr.spec_verification_factor({}) == 0.5


class TestKeyPropertyInEffectiveSeverity:
    def test_spec_on_annihilates_refuted(self):
        rr._SEVERITY_SPEC["on"] = True
        e = {"severity": 0.95, "falsifier_verdict": "REFUTED"}
        assert rr.effective_severity(e) == 0.0

    def test_spec_off_is_the_asserted_float(self):
        rr._SEVERITY_SPEC["on"] = False
        e = {"severity": 0.95, "falsifier_verdict": "REFUTED"}
        assert rr.effective_severity(e) == pytest.approx(0.95)


class TestWhySvAloneIsLossy:
    """Documents the number that makes the composition necessary.

    S_v is computed here from the appendix section 7.8 table weights because
    the repository has no S_v implementation yet; the assertion that binds
    repository code is the V annihilation above. This class pins the
    appendix's stated arithmetic so the doc cannot drift from the maths.
    """

    def test_sympy_refuted_sv_is_positive_but_composition_is_zero(self):
        lam = -4.60 + 2.08 + 1.54  # SymPy refutes; dimensional + numerical verify
        s_v = 1.0 / (1.0 + math.exp(-lam))
        assert s_v == pytest.approx(0.27289178365887047, abs=1e-12)
        assert s_v > 0.0  # S_v alone loses the key property...
        # ...while the documented composition W * S_v * V annihilates:
        v = rr.spec_verification_factor({"falsifier_verdict": "REFUTED"})
        assert 1.0 * s_v * v == 0.0

    def test_sv_never_reaches_zero_for_finite_lambda(self):
        for lam in (-50.0, -10.0, -0.98, 0.0, 10.0):
            assert 1.0 / (1.0 + math.exp(-lam)) > 0.0
