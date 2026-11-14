"""The ordered pair's SECOND coordinate still carries the consequence weight.

★ WHAT THIS GUARDS, AND IT GUARDS A CORRECTION RATHER THAN A REPAIR. The panel
brief of 2026-11-14 asserted that a 3rd consequence weight (R2) and the ordered
pair (R3) are mutually exclusive because a 3rd weight would decide nothing the
pair reads. The `cc2` seat refuted that in the joint round: a pair is compared
LEXICOGRAPHICALLY, the appendix keeps section 7.7's product as the definition of
`credence`, and that product contains the weight -- so a tie in the first
coordinate hands the decision to a quantity the weight still ranks.

★ THE CONCLUSION THE BRIEF DREW SURVIVES. R2 is still REJECTED, on 2 grounds
neither of which is this one. What is guarded here is that the REASON stays
refuted, because a future reader meeting the brief's sentence without this
record would rebuild the same wrong argument.

★ IT IS A MATHEMATICAL FACT, NOT A CODE PATH, so the guard proves it rather
than calling a module. That is deliberate: `severity_d(f) = ( c_d(f),
credence(f) )` is written in `docs/MATHEMATICAL_APPENDIX.md` and is NOT yet
wired into the runner -- R3 is held for the founder. A guard asserting on a
runner path would be asserting on something that does not exist.

EXECUTES SymPy and z3. It does not read any source text.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import sympy as sp
import z3

REPO = Path(__file__).resolve().parent.parent.parent


def _producer():
    spec = importlib.util.spec_from_file_location(
        "credence_coord",
        REPO / "scripts" / "the_credence_coordinate_still_carries_consequence_2026-11-14.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["credence_coord"] = m
    spec.loader.exec_module(m)
    return m


P = _producer()


def test_the_two_weight_table_has_exactly_two_values():
    assert set(P.W2.values()) == {sp.Integer(1), sp.Rational(1, 2)}
    assert len(set(P.W2.values())) == 2


def test_the_third_weight_lies_strictly_inside_the_admissible_interval():
    w = P.W3["MEDIUM"]
    assert sp.Rational(1, 2) < w < sp.Integer(1), (
        "a 3rd weight outside (1/2, 1) is not the proposal under test")


def test_sympy_shows_the_ordering_flips_in_exact_rationals():
    two, three, flipped = P.sympy_witness()
    assert two[0] > two[1], "the 2-weight case must rank A above B or there is no flip to see"
    assert three[0] < three[1], "the 3-weight case must reverse it"
    assert flipped is True


def test_the_witness_uses_no_floating_point():
    """Exact arithmetic, because a float comparison here would prove nothing."""
    two, three, _ = P.sympy_witness()
    for v in (*two, *three):
        assert isinstance(v, sp.Rational), f"{v!r} is not an exact rational"


def test_z3_finds_the_flip_and_refuses_its_negation():
    r, witness, neg = P.z3_existence()
    assert r == z3.sat, "z3 found no flip, so the refutation does not hold"
    assert witness and set(witness) == {"bA", "bB", "w3"}
    assert neg == z3.unsat


def test_the_two_tools_agree():
    """NON-VACUITY: 1 tool agreeing with itself is not a cross-check."""
    _two, _three, flipped = P.sympy_witness()
    r, _w, neg = P.z3_existence()
    assert flipped and r == z3.sat and neg == z3.unsat, (
        "SymPy and z3 disagree about whether a 3rd weight can flip a "
        "lexicographic ordering; the finding is unsettled until they do not")


def test_the_producer_exits_zero():
    assert P.main() == 0
