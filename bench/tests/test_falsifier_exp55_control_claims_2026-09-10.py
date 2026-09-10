"""Task 2.2: the falsifiers for all 8 exp55 control findings, in one file.

THE 8 ARE 2 FINDINGS FOUND 4 TIMES. Across the 2 exp55_v3_control runs, 3
independent models -- ChatGPT, Codex and CC2 -- each raised the same 2 defects,
and every one was recorded UNCONFIRMED with the verdict UNTOOLABLE and an empty
falsifier_code:

    CT-01: C0005 (ChatGPT, 0.72), C0001 (ChatGPT, 0.78), C0005 (Codex, 0.78),
           C0009 (CC2, 0.75)
    CT-02: C0006 (ChatGPT, 0.88), C0002 (ChatGPT, 0.88), C0006 (Codex, 0.86),
           C0010 (CC2, 0.80)

NOTHING ABOUT THEM IS UNTOOLABLE. They are arithmetic about a 614-byte target
that is IN THIS REPOSITORY, and the whole point of that target is that it carries
exactly 2 planted defects -- its filename says so.

THEY ARE TRUE POSITIVES. Both findings are correct, and this file proves it with
SymPy, NumPy, mpmath and pint rather than by agreeing with 3 models. That matters
more than usual here: agreement among models is what this project refuses to
treat as confirmation, so 4 models agreeing is a reason to CHECK, not to accept.

CT-01. The target says the Nyquist criterion is satisfied "because f_s = 400 Hz
exceeds f_max = 180 Hz". The conclusion is TRUE -- 400 > 2 x 180 = 360 -- and the
STATED REASON IS WRONG, because the criterion is f_s > 2 f_max, not f_s > f_max.
A right answer from a wrong rule. The distinction is falsifiable and this file
falsifies it: at f_s = 250 Hz and f_max = 200 Hz the stated reason holds and
Nyquist fails.

CT-02. The target computes df = f_s/N = 400/256 = 1.5625 Hz, which is correct,
and then concludes the buffer "resolves features separated by 1 Hz". It cannot: 1
Hz is BELOW the 1.5625 Hz bin spacing. Correct arithmetic, false conclusion.

WHY BOTH DEFECTS ARE OF THE SAME SHAPE, which is what makes this target a good
control: in each case the number is right and the inference from it is wrong. A
reviewer checking only the arithmetic passes both.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

TARGET = ROOT / "bench" / "cdsfl_registry" / "targets" / "control_two_distinct_defects.md"

F_S, F_MAX, N = 400, 180, 256


@pytest.fixture(scope="module")
def target_text():
    if not TARGET.is_file():
        pytest.skip("the exp55 control target is not in this clone")
    return TARGET.read_text(encoding="utf-8")



@pytest.fixture(autouse=True)
def _restore_mpmath_precision():
    """Restore mpmath's GLOBAL precision after every test in this file.

    `mp.mp.dps = 30` is a module-level setting that outlives the test that made
    it. On 2026-09-10 it broke `test_sk_break_even_2026-09-06.py` in the full
    suite: `mp.findroot` at 30 digits demanded a tolerance it could not reach and
    raised "Could not find root within given tolerance". The failure appeared
    only in a full run, never in isolation, which is the signature of exactly
    this. A test that changes interpreter state for every test after it is a
    defect whatever it asserts.
    """
    import mpmath as _mp
    _before = _mp.mp.dps
    try:
        yield
    finally:
        _mp.mp.dps = _before

class TestTheTargetStillSaysWhatTheFindingsQuote:
    def test_the_setup_numbers_are_unchanged(self, target_text):
        for token in ("f_s = 400 Hz", "f_max = 180 Hz", "N = 256"):
            assert token in target_text, f"{token} is gone; the findings may be stale"

    def test_ct01_states_the_wrong_reason_verbatim(self, target_text):
        assert "because" in target_text and "exceeds `f_max = 180 Hz`" in target_text, (
            "CT-01 no longer justifies Nyquist by f_s exceeding f_max, so the "
            "4 findings against it may have been fixed")

    def test_ct02_states_the_one_hertz_conclusion_verbatim(self, target_text):
        assert "resolves features" in target_text and "1 Hz" in target_text


class TestCT01RightAnswerWrongRule:
    def test_the_conclusion_is_true(self):
        import sympy as sp
        assert bool(sp.Rational(F_S) > 2 * sp.Rational(F_MAX)), (
            "Nyquist actually FAILS here, which would make the finding about the "
            "reason the smaller half of the problem")

    def test_the_stated_reason_is_not_the_criterion(self):
        """Falsified by counter-example, not by assertion."""
        import sympy as sp
        fs, fmax = sp.Rational(250), sp.Rational(200)
        assert bool(fs > fmax), "the counter-example no longer satisfies the stated reason"
        assert not bool(fs > 2 * fmax), (
            "at f_s = 250 and f_max = 200 the real criterion now holds, so this "
            "case no longer separates the rule from the reason")

    def test_the_margin_is_real_and_not_a_rounding_artefact(self):
        import mpmath as mp
        import numpy as np
        mp.mp.dps = 30
        assert float(mp.mpf(F_S) - 2 * mp.mpf(F_MAX)) == pytest.approx(40.0)
        assert np.isclose(F_S - 2 * F_MAX, 40.0)


class TestCT02RightArithmeticFalseConclusion:
    def test_the_bin_spacing_is_what_the_target_says(self):
        import sympy as sp
        df = sp.Rational(F_S, N)
        assert float(df) == 1.5625, df

    def test_four_tools_agree_on_it(self):
        import mpmath as mp
        import numpy as np
        import pint
        import sympy as sp
        mp.mp.dps = 30
        sym = float(sp.Rational(F_S, N))
        assert np.isclose(sym, F_S / N)
        assert abs(float(mp.mpf(F_S) / N) - sym) < 1e-15
        u = pint.UnitRegistry()
        assert abs(((F_S * u.Hz) / N).to("Hz").magnitude - sym) < 1e-15

    def test_one_hertz_is_below_the_resolution_so_the_claim_is_false(self):
        import pint
        import sympy as sp
        df = sp.Rational(F_S, N)
        assert not bool(sp.Integer(1) >= df), (
            "1 Hz now reaches the bin spacing, so CT-02's conclusion would be "
            "true and the 4 findings against it wrong")
        u = pint.UnitRegistry()
        assert not ((1 * u.Hz) >= (F_S * u.Hz) / N), "pint disagrees with sympy"

    def test_what_separation_the_buffer_actually_resolves(self):
        """Stated positively, so the finding carries a correction and not only a No."""
        import sympy as sp
        df = sp.Rational(F_S, N)
        assert float(df) > 1.0
        assert float(df) == pytest.approx(1.5625)


class TestTheTwoDefectsShareOneShape:
    """Why this target is a good control, asserted rather than remarked."""

    def test_both_defects_have_correct_arithmetic(self):
        import sympy as sp
        assert bool(sp.Rational(F_S) > 2 * sp.Rational(F_MAX))     # CT-01 conclusion
        assert float(sp.Rational(F_S, N)) == 1.5625                # CT-02 number
        # In each the number checks out and the inference from it does not, so a
        # reviewer verifying only arithmetic passes both.
