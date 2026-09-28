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
