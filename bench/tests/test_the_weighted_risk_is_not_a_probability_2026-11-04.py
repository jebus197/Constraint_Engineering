"""R_n is an expected-loss scale, not a probability, and 3 surfaces said it was.

GUARD FOR ENTRY B126. A panel seat reported that
`bench/directives/universal/cdsfl_operational.md` defines

    R_n = sum_k w_k . R_k(n)

without stating that the w_k are unnormalised, while section 3 of the same
file gates on `R_k > 0.5`. A reader who carries R_n into that gate compares a
harm-weighted loss against a probability. Following the seat's citation found
the same conflation in `docs/MATHEMATICAL_APPENDIX.md` and in
`experimental_notes/Mathematical_Model_Audit_2026-04-08.md`, the latter
recording it as PROVED.

THIS FILE EXECUTES, IT DOES NOT READ ABOUT. The mathematical claims are
re-derived here on SymPy and z3 rather than asserted against a stored string,
because a test that only greps the prose asserts that the prose is
self-consistent -- which it was throughout the defect. The 3 textual surfaces
ARE pinned, but each is pinned in BOTH states, so fixing one cannot make its
check silent.

The producer is `scripts/the_weighted_risk_is_not_a_probability_2026-11-04.py`
and the mutation harness `scripts/the_weighted_risk_mutations_2026-11-04.py`,
which takes 7 of 7 mutations red.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
DIRECTIVE = REPO / "bench/directives/universal/cdsfl_operational.md"
APPENDIX = REPO / "docs/MATHEMATICAL_APPENDIX.md"
AUDIT = REPO / "experimental_notes/Mathematical_Model_Audit_2026-04-08.md"
PRODUCER = REPO / "scripts/the_weighted_risk_is_not_a_probability_2026-11-04.py"
MUTATIONS = REPO / "scripts/the_weighted_risk_mutations_2026-11-04.py"


# --------------------------------------------------------------------------
# THE MATHS, RE-DERIVED RATHER THAN QUOTED
# --------------------------------------------------------------------------

class TestTheRangeOfTheWeightedSum:
    """Two independent engines, per the project's cross-verification rule."""

    def test_the_seats_witness_is_exact_on_sympy(self):
        sp = pytest.importorskip("sympy")
        R_n = sp.Integer(3) * sp.Rational(1, 2) + sp.Integer(4) * sp.Rational(1, 2)
        assert R_n == sp.Rational(7, 2), R_n
        assert R_n > 1, "the witness must exceed 1 or it shows nothing"

    def test_mpmath_agrees_with_sympy_exactly(self):
        mpmath = pytest.importorskip("mpmath")
        mpmath.mp.dps = 40
        got = mpmath.mpf(3) * mpmath.mpf("0.5") + mpmath.mpf(4) * mpmath.mpf("0.5")
        assert got == mpmath.mpf("3.5"), got

    @pytest.mark.parametrize("label,extra,expect", [
        ("convex weights keep R_n inside [0,1]", "convex_outside", "unsat"),
        ("non-convex weights let R_n exceed 1", "nonconvex_over", "sat"),
        ("R_n never exceeds the sum of the weights", "over_sum", "unsat"),
        ("R_n is never negative", "negative", "unsat"),
        ("R_n can trip 0.5 while every R_k passes", "category_error", "sat"),
    ])
    def test_z3_settles_the_quantified_statements(self, label, extra, expect):
        """A witness cannot establish a `for all`; only a solver can."""
        z3 = pytest.importorskip("z3")
        w1, w2, R1, R2 = z3.Reals("w1 w2 R1 R2")
        Rn = w1 * R1 + w2 * R2
        s = z3.Solver()
        s.add(R1 >= 0, R1 <= 1, R2 >= 0, R2 <= 1, w1 > 0, w2 > 0)
        half = z3.RealVal(1) / 2
        if extra == "convex_outside":
            s.add(w1 + w2 <= 1, z3.Or(Rn < 0, Rn > 1))
        elif extra == "nonconvex_over":
            s.add(w1 + w2 > 1, Rn > 1)
        elif extra == "over_sum":
            s.add(Rn > w1 + w2)
        elif extra == "negative":
            s.add(Rn < 0)
        elif extra == "category_error":
            s.add(Rn > half, R1 <= half, R2 <= half)
        assert str(s.check()) == expect, f"{label}: expected {expect}"


class TestThePerClassQuantityIsStillAProbability:
    """The directive's own words are right about R_k; [0, pi_k] is not."""

    def test_the_appendix_readout_tops_out_at_the_prior(self):
        sp = pytest.importorskip("sympy")
        pi, m = sp.symbols("pi m", positive=True)
        R = pi * m / ((1 - pi) + pi * m)
        assert sp.simplify(R.subs(m, 1)) == pi
        assert sp.simplify(R.subs(m, 0)) == 0

    def test_re_injection_pushes_rk_above_the_prior_but_never_above_one(self):
        """So [0, pi_k] is wrong for the DIRECTIVE's form of R_k, which is why
        the seat's own proposed wording was corrected before being applied."""
        z3 = pytest.importorskip("z3")
        pi, m, nb, nf, S = z3.Reals("pi m nb nf S")
        R_base = pi * m / ((1 - pi) + pi * m)
        nu = 1 - (1 - nb) * (1 - (1 - S) * nf)
        R_k = R_base * (1 - nu) + nu
        dom = [pi > 0, pi < 1, m >= 0, m <= 1, nb >= 0, nb <= 1,
               nf >= 0, nf <= 1, S >= 0, S <= 1, nb + nf <= 1]
        over_prior = z3.Solver()
        over_prior.add(dom + [R_k > pi])
        assert str(over_prior.check()) == "sat"
        over_one = z3.Solver()
        over_one.add(dom + [R_k > 1])
        assert str(over_one.check()) == "unsat", (
            "R_k must remain a probability; the directive says 'bounded in "
            "[0, 1]' and that claim is load-bearing for the 0.5 gate")


# --------------------------------------------------------------------------
# THE 3 SURFACES, EACH PINNED IN BOTH STATES
# --------------------------------------------------------------------------

def _text(p: pathlib.Path) -> str:
    assert p.is_file(), f"{p} is missing"
    return p.read_text(encoding="utf-8")


class TestTheSurfacesStayCorrected:
    """Each check names the DEFECT and the FIX, and requires exactly 1.

    A test that searches only for the defect goes silent the moment the
    defect is fixed, and silence is indistinguishable from never having run.
    """

    def test_the_directive_states_the_scale(self):
        t = _text(DIRECTIVE)
        assert "R_n = Σ_k w_k · R_k(n)" in t, (
            "the definition this guard exists for is gone; re-derive the entry")
        assert "expected-loss SCALE with range [0, Σ_k w_k]" in t, (
            "the scale note was removed from the directive, so a reader can "
            "again carry R_n into the 0.5 gate")
        assert "never compare" in t.lower() or "Never carry" in t

    def test_the_directive_still_gates_the_per_class_quantity(self):
        t = _text(DIRECTIVE)
        assert re.search(r"R_k\s*>\s*0\.5", t), (
            "the section 3 gate moved; the scale note's last sentence names "
            "0.5 explicitly and would now be stale")

    def test_the_appendix_attributes_the_prior_range_to_the_per_class_term(self):
        t = _text(APPENDIX)
        bad = "R_n reports residual risk, whose range"
        good = "per-class R_k reports residual risk, whose range"
        assert (bad in t) + (good in t) == 1, (
            "expected exactly 1 of the defective and corrected wordings")
        assert good in t, "the appendix regressed to attributing [0, pi_k] to R_n"

    def test_the_audit_row_carries_its_scope_correction(self):
        t = _text(AUDIT)
        assert "| R_n ∈ [0, 1] for" in t, (
            "the dated audit row was altered; it is a record of what was run "
            "and is meant to stay as written")
        assert "SCOPE CORRECTION ADDED 2026-11-04" in t, (
            "the correction beneath the row is gone, so the row again reads "
            "as an unconditional proof")


# --------------------------------------------------------------------------
# THE PRODUCER AND ITS HARNESS ARE EXECUTED, NOT DESCRIBED
# --------------------------------------------------------------------------

class TestTheProducerRuns:
    def test_the_producer_exits_zero_and_runs_its_controls(self):
        r = subprocess.run([sys.executable, str(PRODUCER)],
                           capture_output=True, text=True, cwd=str(REPO))
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
        m = re.search(r"predicate controls: (\d+) run, (\d+) failed", r.stdout)
        assert m, "the producer no longer reports its predicate controls"
        run, failed = int(m.group(1)), int(m.group(2))
        assert failed == 0, f"{failed} of {run} predicate controls failed"
        assert run >= 16, (
            f"only {run} controls; each was added for a measured false "
            f"positive and removing one removes a pin")
        assert "VERIFIED" in r.stdout, (
            "the appendix identity the directive note cites is no longer "
            "verifiable against the appendix")

    def test_the_predicate_discriminates_negation_from_requirement(self):
        """The decisive pair, run through the producer's OWN function.

        The predicate read its own remedy as the defect 3 times: the
        summation bound in `sum_{k=1}^{K}`, the scale note's "NOT required
        to sum to 1", and the appendix correction's "nothing ... normalises".
        The window is the enclosing clause THROUGH the match.
        """
        # the filename carries hyphens, so it is loaded by path
        import importlib.util
        spec = importlib.util.spec_from_file_location("_wrisk", PRODUCER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert mod.normalises("The w_k sum to 1.") is True
        assert mod.normalises(
            "and what it may not be compared to.** The w_k are NOT required "
            "to sum to 1.") is False
        assert mod.normalises(
            "and what it may not be compared to.** The w_k are required "
            "to sum to 1.") is True, (
            "an INVERTED scale note must be detected; a flat look-behind "
            "picked up the `not` of the neighbouring clause and missed it")
        assert mod.normalises(
            "> **G_n = Σ_{k=1}^{K} w_k · x**") is False, (
            "the summation bound k=1 is not a normalisation requirement")

    def test_every_mutation_goes_red(self):
        """The harness restores from bytes it read, so this is safe to run."""
        r = subprocess.run([sys.executable, str(MUTATIONS)],
                           capture_output=True, text=True, cwd=str(REPO))
        m = re.search(r"VERDICT: (\d+) of (\d+) mutations detected", r.stdout)
        assert m, r.stdout[-1500:] + r.stderr[-1500:]
        got, total = int(m.group(1)), int(m.group(2))
        assert got == total, (
            f"only {got} of {total} mutations detected; the blind spots are "
            f"named in the harness output")
        assert r.returncode == 0
