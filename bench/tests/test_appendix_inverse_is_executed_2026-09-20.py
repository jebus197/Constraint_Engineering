#!/usr/bin/env python3
"""The coverage-to-risk map and its inverse, EXECUTED against the appendix's own text.

FOUNDER, 2026-09-20, on the guard proposed after the sign error was found:
*"Verdict: build and implement it."*

WHAT WENT WRONG, AND WHY A GUARD FOR IT DID NOT EXIST. `docs/MATHEMATICAL_APPENDIX.md`
stated the inverse of the Mobius readout TWICE and the 2 disagreed. Line 119 had
`C = (pi-R)/(pi-pi R)`, which round-trips. Line 169 had `C_k = (pi_k-R_k)/(pi_k(R_k-1))`,
exactly its NEGATIVE: it does not round-trip, and at pi = 1/2, R = 1/5 it returns
a coverage of -3/4, which is not a coverage at all. That same line claimed, in its
own words, a "round-trip residual exactly 0".

`test_appendix_reduction_properties_2026-09-05.py` was written for this class --
the appendix's verification lived in prose -- and has 35 tests. Not 1 of them
touched this inversion, so the error walked past the instrument built to catch it.

THIS FILE CLOSES THAT GAP BY EXECUTION, NOT BY READING. It extracts every inverse
formula the appendix states, turns each into a callable, and requires it to
round-trip over a grid of exact rationals. A formula that is off by a sign, or
that returns a value outside [0, 1], fails here regardless of what the prose
beside it claims.
"""
from __future__ import annotations

import pathlib
import re
from fractions import Fraction as F

import pytest
import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parents[2]
APPENDIX = ROOT / "docs" / "MATHEMATICAL_APPENDIX.md"

#: Every shape the appendix uses to state the inverse, ASCII and Greek, with or
#: without the `_k` subscripts. This locates the `/(` that opens the DENOMINATOR;
#: the denominator itself is then read by balancing parentheses, because a regex
#: cannot: line 119's is `π−πR` and line 169's is `π_k(1−R_k)`, and a lazy or
#: greedy class either stops inside the second or runs past the first into the
#: prose that follows it.
INVERSE = re.compile(
    r"C(?:_k)?\s*=\s*\(\s*(?:π|pi)(?:_k)?\s*[−-]\s*R(?:_k)?\s*\)\s*/\s*\(")

#: The forward map, which is not in dispute and is the thing the inverse must undo.
FORWARD = "pi*(1-C)/((1-pi)+pi*(1-C))"

GRID = [(F(1, 2), F(1, 5)), (F(1, 3), F(1, 10)), (F(9, 10), F(1, 2)),
        (F(1, 4), F(1, 100)), (F(2, 3), F(1, 3)), (F(99, 100), F(1, 2))]


def _appendix_text() -> str:
    return APPENDIX.read_text(encoding="utf-8")


def _balanced(text: str, start: int) -> str:
    """The contents of the parenthesis group opening at `start`-1, balanced."""
    depth, i = 1, start
    while i < len(text) and depth:
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if not depth:
                return text[start:i]
        i += 1
    raise ValueError(f"unbalanced denominator from offset {start}")


def _inverse_denominators() -> list:
    """Every inverse denominator the appendix states, normalised for SymPy."""
    text = _appendix_text()
    out = []
    for m in INVERSE.finditer(text):
        d = _balanced(text, m.end())
        d = d.replace("π", "pi").replace("−", "-").replace("·", "*").replace("_k", "")
        # Implicit multiplication is fine in prose and fatal to SymPy: `pi(1-R)`
        # and `pi R` both need an explicit operator.
        d = re.sub(r"(pi)\s*\(", r"\1*(", d)
        d = re.sub(r"(pi)\s*R\b", r"\1*R", d)
        out.append(d.strip())
    return out


def _as_callable(denominator: str):
    pi, R = sp.symbols("pi R", positive=True)
    expr = (pi - R) / sp.sympify(denominator, locals={"pi": pi, "R": R})
    return sp.lambdify((pi, R), expr, "math"), expr


class TestTheAppendixStatesTheInverseAtAll:
    """ANTI-VACUITY. If the formulas ever stop being stated in a shape this file
    recognises, every test below would pass on an empty list."""

    def test_at_least_2_statements_are_found(self):
        found = _inverse_denominators()
        assert len(found) >= 2, (
            f"found {len(found)} inverse statement(s) in the appendix: "
            f"{found}. Either the appendix stopped stating it, or the pattern "
            f"here no longer matches the notation, and both need a human.")


class TestEveryStatedInverseRoundTrips:
    """The property the sign error broke, checked by CALLING each formula."""

    def test_each_one_undoes_the_forward_map(self):
        pi_s, R_s, C_s = sp.symbols("pi R C", positive=True)
        forward = sp.sympify(FORWARD, locals={"pi": pi_s, "C": C_s})
        offenders = []
        for denominator in _inverse_denominators():
            _, inverse_expr = _as_callable(denominator)
            residual = sp.simplify(forward.subs(C_s, inverse_expr) - R_s)
            if residual != 0:
                offenders.append((denominator, str(residual)[:80]))
        assert not offenders, (
            "an inverse stated in the appendix does NOT undo the forward map; "
            "this is the 2026-09-19 sign error's exact shape: " + str(offenders))

    def test_each_one_returns_a_coverage_on_a_grid_of_real_values(self):
        """A sign error shows up as a NEGATIVE coverage long before anyone
        notices the algebra. -3/4 was what line 169 returned at pi=1/2, R=1/5."""
        offenders = []
        for denominator in _inverse_denominators():
            fn, _ = _as_callable(denominator)
            for pi_v, R_v in GRID:
                if R_v >= pi_v:
                    continue           # R <= pi by construction; skip the undefined corner
                got = fn(float(pi_v), float(R_v))
                if not 0.0 <= got <= 1.0:
                    offenders.append((denominator, f"pi={pi_v}, R={R_v} -> {got}"))
        assert not offenders, ("an inverse returned a value outside [0, 1], so it "
                               "is not a coverage: " + str(offenders))


class TestTheGuardCanFail:
    """A guard that cannot fail measures nothing. These drive the SAME code with
    the defect reinstated and require it to be caught."""

    WRONG = "pi*(R-1)"          # the exact denominator from line 169, before the fix

    def test_the_2026_09_19_defect_is_caught_by_the_round_trip(self):
        pi_s, R_s, C_s = sp.symbols("pi R C", positive=True)
        forward = sp.sympify(FORWARD, locals={"pi": pi_s, "C": C_s})
        _, wrong = _as_callable(self.WRONG)
        residual = sp.simplify(forward.subs(C_s, wrong) - R_s)
        assert residual != 0, "the known-bad inverse passed the round trip"

    def test_the_2026_09_19_defect_is_caught_by_the_range_check(self):
        fn, _ = _as_callable(self.WRONG)
        got = fn(0.5, 0.2)
        assert got == pytest.approx(-0.75), got
        assert not 0.0 <= got <= 1.0

    def test_the_correct_form_passes_both(self):
        pi_s, R_s, C_s = sp.symbols("pi R C", positive=True)
        forward = sp.sympify(FORWARD, locals={"pi": pi_s, "C": C_s})
        fn, right = _as_callable("pi*(1-R)")
        assert sp.simplify(forward.subs(C_s, right) - R_s) == 0
        assert fn(0.5, 0.2) == pytest.approx(0.75)


class TestTheProseClaimMatchesTheArithmetic:
    """Line 169 claimed a round-trip residual of exactly 0 for a formula that had
    none. A claim about a measurement is not the measurement."""

    def test_a_zero_residual_claim_is_backed_by_a_zero_residual(self):
        text = _appendix_text()
        if "round-trip residual exactly 0" not in text:
            pytest.skip("the appendix no longer makes that claim anywhere")
        pi_s, R_s, C_s = sp.symbols("pi R C", positive=True)
        forward = sp.sympify(FORWARD, locals={"pi": pi_s, "C": C_s})
        for denominator in _inverse_denominators():
            _, inverse_expr = _as_callable(denominator)
            assert sp.simplify(forward.subs(C_s, inverse_expr) - R_s) == 0, (
                f"the appendix claims a 0 round-trip residual while stating an "
                f"inverse with denominator {denominator!r} that does not have one")
