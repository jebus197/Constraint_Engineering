"""The explorer's per-pass change is NOT the quantity a stopping rule needs.

WHY THIS TEST EXISTS. `explorer/index.html` is PUBLIC, served at
jebus197.github.io/Constraint_Engineering/explorer/. Line 83 labels its slider
`theta  stopping threshold on ΔR` and line 294 colours a pass green exactly when
`dR >= theta`, so a reader is shown dR as a stop/continue decision. The appendix
RETIRED that rule on 2026-09-21 (`docs/MATHEMATICAL_APPENDIX.md:217`): dR is the
change conditional on the non-detection branch, and the decision is taken before
the branch is known.

WHAT IS ASSERTED HERE IS THE PERMANENT MATHEMATICS, NOT THE CURRENT DEFECT. A
test asserting "the explorer is wrong" goes red the moment it is fixed and tells
a later reader nothing. What cannot expire is the RELATIONSHIP between the 2
quantities and its DIRECTION, because that is what makes the substitution unsafe
in one specific way: the explorer can only ever advise stopping too EARLY.

Measured by `scripts/explorer_stopping_rule_is_superseded_2026-09-28.py`:
1309 of 14440 grid points over the explorer's own slider ranges disagree, all in
the premature-stop direction, 0 in the other. Proven over the whole open cube by
z3 (unsat that general < dR) and independently by Wolfram Language
(`Resolve[ForAll[...]] -> True`). Wolfram is used in the REASONING only; this
file calls SymPy and z3, because a committed falsifier may not require an
installed Wolfram kernel.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
EXPLORER = ROOT / "explorer" / "index.html"

R, q, sigma, nu = sp.symbols("R q sigma nu", positive=True)


def _explorer_dR():
    """The published recursion, transcribed from explorer/index.html:171-176."""
    R_det = R * (1 - q) / (1 - q * R)
    R_base = sigma * R_det + (1 - sigma) * R
    R_new = R_base * (1 - nu) + nu
    return R - R_new


def _appendix_expected():
    """MATHEMATICAL_APPENDIX.md:225, the general expected improvement."""
    return R * q * sigma * (1 - nu) - nu * (1 - R)


def test_explorer_file_exists_and_is_the_published_page():
    assert EXPLORER.is_file(), f"missing {EXPLORER}"
    text = EXPLORER.read_text(encoding="utf-8")
    assert "stopping threshold" in text.lower(), (
        "the slider label changed; re-read the page before trusting this test's premise"
    )


def test_the_explorer_still_gates_on_dR_or_the_premise_has_changed():
    """Records the rule this test reasons about, so a silent change is caught.

    EXECUTED, NOT GREPPED FOR ITS OWN SAKE: the assertion below is about the
    page's TEXT because the page is JavaScript this suite cannot call. It exists
    only to invalidate the test's premise loudly if the rule is revised, and the
    mathematical assertions that follow do not depend on it.
    """
    text = EXPLORER.read_text(encoding="utf-8")
    gates = re.findall(r"s\.dR\s*>=\s*o\.theta", text)
    if not gates:
        pytest.skip(
            "explorer no longer gates on `s.dR >= o.theta` -- the stopping rule was "
            "revised; confirm it now uses the general expected improvement"
        )
    assert len(gates) >= 1


def test_dR_at_the_corner_is_the_conditional_quantity():
    """sigma=1, nu=0 reduces the explorer's dR to R*q*(R-1)/(R*q-1) exactly."""
    corner = sp.simplify(_explorer_dR().subs({sigma: 1, nu: 0}))
    conditional = R * q * (R - 1) / (R * q - 1)
    assert sp.simplify(corner - conditional) == 0


def test_general_expectation_strictly_exceeds_dR_everywhere():
    """The difference is strictly positive on the open cube.

    This is the property that makes the substitution unsafe in exactly one
    direction, and it is what a future reviser must preserve.
    """
    diff = sp.simplify(sp.expand(_appendix_expected() - _explorer_dR()))
    assert sp.simplify(diff) != 0, "the 2 quantities are not identical"

    import z3

    zR, zq, zs, zv = z3.Reals("R q sigma nu")
    domain = [zR > 0, zR < 1, zq > 0, zq < 1, zs > 0, zs <= 1, zv >= 0, zv < 1]
    zdet = zR * (1 - zq) / (1 - zq * zR)
    zbase = zs * zdet + (1 - zs) * zR
    znew = zbase * (1 - zv) + zv
    zdR = zR - znew
    zgen = zR * zq * zs * (1 - zv) - zv * (1 - zR)

    s = z3.Solver()
    s.add(domain)
    s.add(zgen < zdR)
    assert s.check() == z3.unsat, (
        "found a point where the general expectation is BELOW the explorer's dR; "
        "the one-sided direction of this defect no longer holds"
    )


def test_the_disagreement_is_one_sided_at_the_explorers_default_theta():
    """At theta=0.005 (index.html:84) the explorer stops where the appendix continues.

    The worked point is the founder's own: R=0.99, q=0.3.
    """
    theta = sp.Rational(5, 1000)
    at = {R: sp.Rational(99, 100), q: sp.Rational(3, 10), sigma: 1, nu: 0}
    d = sp.simplify(_explorer_dR().subs(at))
    e = sp.simplify(_appendix_expected().subs(at))
    assert d < theta, f"explorer dR {float(d)} should fall below theta {float(theta)}"
    assert e > theta, f"appendix expected {float(e)} should exceed theta {float(theta)}"
    ratio = sp.nsimplify(e / d)
    assert float(ratio) > 70, f"ratio {float(ratio)} should exceed 70"


def test_astras_proposed_Rq_is_only_the_corner():
    """`R*q` is the sigma=1, nu=0 corner and overstates elsewhere (appendix:223).

    So the earlier proposed revision is not the fix to apply either, which is the
    founder's own question of 2026-09-28.
    """
    general = _appendix_expected()
    rq = R * q
    assert sp.simplify(general.subs({sigma: 1, nu: 0}) - rq) == 0
    # Overstates at any sigma<1 or nu>0: pick the appendix's own worked point.
    at = {R: sp.Rational(99, 100), q: sp.Rational(3, 10), sigma: 1, nu: sp.Rational(1, 10)}
    assert sp.simplify(rq.subs(at) - general.subs(at)) > 0


class TestTheExplorersOwnBreakEvenIsNotTheModels:
    """A SECOND defect, reached by a separate route, running the SAME direction.

    `explorer/index.html:177` computes `nuStar = sigma*R*q/(1 - q*R*(1-sigma))`,
    the re-injection rate at which it warns that a further pass does net harm.
    The appendix's general expected improvement implies its own break-even,
    `R*q*sigma/(R*q*sigma - R + 1)`. The denominators differ (`- R*q` against
    `- R`), and the explorer's figure is STRICTLY SMALLER everywhere on the open
    domain, so it warns of harm earlier than the model supports.

    Measured 2026-09-28: at R=0.99, q=0.3, sigma=1 the explorer gives 0.297000
    against a true break-even of 0.967427, a ratio of 0.307. Confirmed by z3
    (unsat that the explorer's value can exceed it) and independently by Wolfram
    Language (`Resolve[ForAll[...]] -> True`). Wolfram is used in the REASONING
    only; this file calls SymPy and z3, because a stored falsifier may not require
    an installed kernel.

    ASSERTED AS THE PERMANENT RELATIONSHIP, not the current defect, so it does not
    go red when the explorer is revised.
    """

    @staticmethod
    def _explorer_nustar():
        return sigma * R * q / (1 - q * R * (1 - sigma))

    @staticmethod
    def _appendix_breakeven():
        return sp.solve(sp.Eq(_appendix_expected(), 0), nu)[0]

    def test_the_two_break_evens_are_not_the_same_expression(self):
        d = sp.simplify(self._explorer_nustar() - self._appendix_breakeven())
        assert d != 0, "the 2 break-evens are identical; this finding no longer holds"

    def test_the_explorer_understates_the_break_even_everywhere(self):
        """The direction is what makes it unsafe in one specific way."""
        import z3

        zR, zq, zs = z3.Reals("R q sigma")
        dom = [zR > 0, zR < 1, zq > 0, zq < 1, zs > 0, zs <= 1]
        ze = zR * zq * zs / (zR * zq * zs - zR * zq + 1)
        za = zR * zq * zs / (zR * zq * zs - zR + 1)
        s = z3.Solver()
        s.add(dom)
        s.add(ze > za)
        assert s.check() == z3.unsat, (
            "found a point where the explorer's nuStar exceeds the true break-even; "
            "the one-sided direction of this defect no longer holds"
        )

    def test_the_worked_point_ratio(self):
        at = {R: sp.Rational(99, 100), q: sp.Rational(3, 10), sigma: 1}
        e = sp.simplify(self._explorer_nustar().subs(at))
        a = sp.simplify(self._appendix_breakeven().subs(at))
        assert abs(float(e) - 0.297) < 1e-9, float(e)
        assert abs(float(a) - 0.9674267) < 1e-6, float(a)
        assert float(e / a) < 0.31

    def test_both_explorer_defects_run_the_same_direction(self):
        """Both make the tool stop or warn EARLIER than the model supports.

        Stated as a test because 2 independent defects sharing a direction is a
        stronger claim than either alone, and a future fix to one must not silently
        invert the other.
        """
        at = {R: sp.Rational(99, 100), q: sp.Rational(3, 10), sigma: 1, nu: 0}
        # defect 1: per-pass change understates expected improvement
        assert sp.simplify(_appendix_expected().subs(at) - _explorer_dR().subs(at)) > 0
        # defect 2: nuStar understates the break-even
        at2 = {R: sp.Rational(99, 100), q: sp.Rational(3, 10), sigma: 1}
        assert sp.simplify(self._appendix_breakeven().subs(at2)
                           - self._explorer_nustar().subs(at2)) > 0


class TestTheProducingScriptAgreesWithThisFile:
    """EXECUTE, DO NOT RE-DERIVE. Two transcriptions of one page must be compared.

    THE DEFECT THIS CLOSES, found 2026-09-28 by the stop gate asking what had been
    executed. `scripts/explorer_stopping_rule_is_superseded_2026-09-28.py` produces
    every figure quoted to the founder, and NO test executed it -- it appeared in
    this file only inside a docstring. All 6 of its functions were unreached, which
    the additive standard names as the failure mode responsible for 11 confirmed
    defects in this project.

    The sharper problem is not that it was unreached but that BOTH FILES
    INDEPENDENTLY TRANSCRIBE `explorer/index.html`. If one transcription drifts,
    each remains internally consistent and both stay green while disagreeing about
    what the published page does. `execute-do-not-grep` is explicit: where both
    forms exist as live code, the test must CALL them and compare outputs. So these
    tests import the script and check its functions against this file's own
    derivation, rather than trusting that 2 people typed the same formula twice.
    """

    @pytest.fixture(scope="class")
    def script(self):
        import importlib.util

        path = ROOT / "scripts" / "explorer_stopping_rule_is_superseded_2026-09-28.py"
        assert path.is_file(), f"missing {path}"
        spec = importlib.util.spec_from_file_location("explorer_producer", path)
        m = importlib.util.module_from_spec(spec)
        sys.modules["explorer_producer"] = m
        spec.loader.exec_module(m)
        return m

    def test_the_scripts_dR_matches_this_files_dR(self, script):
        """The 2 transcriptions of the explorer's recursion must be one formula."""
        theirs = script.explorer_dR_sym(R, q, sigma, nu)
        mine = _explorer_dR()
        assert sp.simplify(sp.together(theirs - mine)) == 0, (
            f"the producing script and this test transcribe explorer/index.html "
            f"differently: {sp.simplify(theirs)} vs {sp.simplify(mine)}"
        )

    def test_the_scripts_expected_matches_this_files_expected(self, script):
        theirs = script.appendix_expected(R, q, sigma, nu)
        mine = _appendix_expected()
        assert sp.simplify(sp.together(theirs - mine)) == 0

    def test_the_scripts_checks_run_without_error(self, script, capsys):
        """The functions are CALLED, so a broken one fails here rather than the
        next time a figure is quoted to the founder."""
        script.identity_check()
        script.nustar_check()
        out = capsys.readouterr().out
        assert "symbolically identical         True" in out, out
        assert "identical?                     False" in out, out

    def test_the_script_reports_the_one_sided_z3_result(self, script, capsys):
        """ANTI-VACUITY: the script must actually reach its solver, not print a
        heading and stop."""
        script.nustar_check()
        out = capsys.readouterr().out
        assert "z3: explorer nuStar can EXCEED the true break-even?  unsat" in out, out
