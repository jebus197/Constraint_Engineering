#!/usr/bin/env python3
"""What `free_parameters_can_fit_any_desired_risk: true` actually means, executed.

FOUNDER, 2026-09-19, asking for this in plain English: is it good or bad?

THE CLAIM UNDER EXAMINATION is the revised model's own self-report, at
`docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_check_results.json`,
produced by `CDSFL_revised_model_checks.py` line 219. Its check is 1 line:

    for z, desired in product(grid, repeat=2):
        assert update(z, 1, 1, 1-desired, desired).risk_after_action == desired

That exhibits 1 point in the parameter space for each target -- pick removal
effectiveness s = 1 - desired and introduction rate b = desired, and the action
step `risk_after = (1-s)z + b(1-z)` returns `desired` whatever the starting risk
was. The package is being honest by reporting it, and the finding is real.

THIS SCRIPT ESTABLISHES SOMETHING STRICTLY STRONGER, WHICH MATTERS FOR HOW BAD IT
IS. The degeneracy is not an isolated point. Solving the same equation for b
given ANY s yields `b = (z - s*z - d)/(z - 1)`, a whole 1-parameter FAMILY: for
every removal rate a reviewer might claim, there is an introduction rate that
lands on any target risk named in advance. A defender of the model cannot
therefore escape by saying the exhibited point is unphysical, because the
freedom runs along a line and crosses the physical region.

THE CONTRAST IS THE POINT, and it is why this is a falsifiability question rather
than an arithmetic one. The existing model's collapse form, `R(1-p)/(1-pR)`, has
1 free parameter, bounded to [0, 1], with a direct operational meaning -- review
sensitivity. Its derivative with respect to p is strictly negative on the open
unit square, so more sensitivity strictly lowers residual risk and NO choice of p
can raise it. That model forbids outcomes. A 2-parameter form with a degenerate
direction forbids none until s and b are pinned by independent measurement.

WHAT WOULD SETTLE IT, stated so this is a test and not a complaint: s and b must
be measured BEFORE the outcome they are used to predict, from data that does not
contain that outcome. Whether the revision's validation plan actually does that,
or only describes doing it, is a question for the panel and is not decided here.

Read-only. Standard library plus SymPy and mpmath. Contacts nothing.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from fractions import Fraction as F
from itertools import product

REPO = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = REPO / "docs" / "maths_revision_review_2026-09-10"
RESULTS = PACKAGE / "outputs" / "CDSFL_revised_model_check_results.json"

#: The revised model's action step, exactly as `CDSFL_revised_core.update` applies
#: it: a fraction `s` of the existing risk is removed, and a fraction `b` of the
#: remaining clean mass is newly introduced.
ACTION = "(1 - s)*z + b*(1 - z)"

#: The existing model's collapse form, for the contrast.
COLLAPSE = "R*(1 - p)/(1 - p*R)"


def the_package_reports_it() -> bool | None:
    """Read the flag from the package's own committed output. None if absent."""
    if not RESULTS.is_file():
        return None
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    return data.get("examples", {}).get("free_parameters_can_fit_any_desired_risk")


def exhibited_point_holds(n: int = 8) -> tuple[bool, int]:
    """The package's own check, re-run in exact rationals. (holds, cases)."""
    grid = [F(k, n) for k in range(n + 1)]
    cases = 0
    for z, d in product(grid, repeat=2):
        s, b = 1 - d, d
        if ((1 - s) * z + b * (1 - z)) != d:
            return False, cases
        cases += 1
    return True, cases


def degeneracy_is_a_line() -> dict:
    """SymPy: solve the action step for b given ANY s, not just the 1 point."""
    import sympy as sp
    z, s, b, d = sp.symbols("z s b d", real=True)
    after = sp.sympify(ACTION, locals={"z": z, "s": s, "b": b})
    at_point = sp.simplify(after.subs({s: 1 - d, b: d}))
    solved = sp.solve(sp.Eq(after, d), b)
    return {
        "action_step": str(after),
        "at_the_exhibited_point": str(at_point),
        "identically_the_target": sp.simplify(at_point - d) == 0,
        "b_as_a_function_of_any_s": str(sp.simplify(solved[0])) if solved else None,
        "free_directions": 1 if solved else 0,
    }


def numerically_independent(n: int = 8) -> float:
    """mpmath, at higher precision, as the second falsifier on the same claim."""
    import mpmath as mp
    mp.mp.dps = 40
    worst = mp.mpf(0)
    for k in range(n + 1):
        for j in range(n + 1):
            zv, dv = mp.mpf(k) / n, mp.mpf(j) / n
            got = (1 - (1 - dv)) * zv + dv * (1 - zv)
            worst = max(worst, abs(got - dv))
    return float(worst)


def the_contrast() -> dict:
    """The existing model forbids outcomes; that is what is being given up."""
    import sympy as sp
    R, p = sp.symbols("R p", positive=True)
    old = sp.sympify(COLLAPSE, locals={"R": R, "p": p})
    d_dp = sp.simplify(sp.diff(old, p))
    # Strictly negative on the open unit square: more sensitivity, less residual
    # risk, with no choice available to a user of the model.
    samples = [(sp.Rational(a, 10), sp.Rational(b_, 10))
               for a in (1, 5, 9) for b_ in (1, 5, 9)]
    signs = {f"R={a}, p={b_}": bool(d_dp.subs({R: a, p: b_}) < 0) for a, b_ in samples}
    return {"derivative_wrt_p": str(d_dp),
            "strictly_negative_at_every_sample": all(signs.values()),
            "samples": signs,
            "free_parameters": 1}


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=pathlib.Path)
    a = ap.parse_args(argv)

    reported = the_package_reports_it()
    holds, cases = exhibited_point_holds()
    line = degeneracy_is_a_line()
    worst = numerically_independent()
    contrast = the_contrast()

    print(f"the package's own flag, as committed: {reported}")
    if reported is None:
        print(f"  (NOT MEASURED: {RESULTS} is not in this tree)")
    print(f"exact-rational re-run of its check: holds={holds} over {cases} cases")
    print(f"mpmath at 40 digits, worst |risk_after - target|: {worst}")
    print()
    print("SYMBOLICALLY, AND THIS IS STRONGER THAN THE PACKAGE'S OWN CHECK:")
    print(f"  action step                     : {line['action_step']}")
    print(f"  at s=1-d, b=d it returns        : {line['at_the_exhibited_point']}")
    print(f"  identically the target, any z   : {line['identically_the_target']}")
    print(f"  for ANY s, b =                  : {line['b_as_a_function_of_any_s']}")
    print(f"  so the freedom is a LINE, not a point: {line['free_directions']} "
          f"free direction")
    print()
    print("THE CONTRAST WITH THE EXISTING MODEL:")
    print(f"  d/dp of {COLLAPSE} = {contrast['derivative_wrt_p']}")
    print(f"  strictly negative at every sample: "
          f"{contrast['strictly_negative_at_every_sample']}")
    print(f"  free parameters: {contrast['free_parameters']}, bounded to [0, 1], "
          f"with an operational meaning")
    print()
    print("READING: the flag is not an error and not, by itself, a verdict. It says "
          "the 2 action\nparameters must be pinned by measurement taken BEFORE the "
          "outcome they predict. Until\nthey are, the action step forbids nothing, "
          "and a model that forbids nothing cannot be\nfalsified. The existing "
          "1-parameter form forbids a great deal, which is what is at stake.")

    out = {"package_flag": reported, "exhibited_point_holds": holds,
           "cases": cases, "mpmath_worst_error": worst,
           "symbolic": line, "contrast": contrast}
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(out, indent=2, default=str) + "\n",
                          encoding="utf-8")
        print(f"\nwritten: {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
