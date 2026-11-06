#!/usr/bin/env python3
"""The severity factor VALUES and the 7.11 conjunction must be pinned.

WHY THIS EXISTS, AND IT IS A GAP IN WORK ACCEPTED FROM A PANEL SEAT. The free
round of 2026-11-06 delivered 2 guards, 60 tests, all passing. Mutating the
appendix they read showed 3 of 4 mutations go GREEN
(`scripts/the_folded_back_seat_guards_mutations_2026-11-06.py`):

  * raising `W(SOFT)` from 0.5 to 1.0 -- which collapses the premise of the
    seat's own shape theorem, since the theorem's interval is `(W(SOFT),
    W(HARD)]` and an equal pair empties it -- was not caught;
  * changing `V(False)` from 0.0 to 0.1 -- which destroys the KEY PROPERTY the
    other seat's guard is NAMED for, a disproved finding scoring exactly 0 --
    was not caught;
  * deleting the conjunction in 7.11 -- the single fact that refuted this
    session's own brief, that `Sev` and `S_v` are used TOGETHER rather than
    competing -- was not caught.

The seats pinned the PROSE they added and not the NUMBERS their argument rests
on. That is `execute-do-not-grep` in its own words: a test asserting on source
text asserts only that the text is self-consistent. These assertions read the
factor tables and the selection predicate and CHECK THE VALUES, so a silent
edit to either cannot pass.
"""
from __future__ import annotations
import pathlib
import re

import pytest
from z3 import Real, Reals, Solver, And, Or, Not, unsat, sat
import sympy as sp

REPO = pathlib.Path(__file__).resolve().parents[2]
APPENDIX = REPO / "docs" / "MATHEMATICAL_APPENDIX.md"


@pytest.fixture(scope="module")
def text():
    assert APPENDIX.is_file(), "the appendix is missing"
    return APPENDIX.read_text(encoding="utf-8")


def _factor(text: str, name: str) -> float:
    """Read a factor's value out of the 7.7 table rather than assuming it."""
    m = re.search(rf"^\|\s*{re.escape(name)}\s*\|\s*([0-9.]+)\s*\|", text, re.M)
    assert m, f"{name} has no row in the 7.7 factor table"
    return float(m.group(1))


class TestTheFactorValuesThemselves:
    def test_the_two_classes_differ(self, text):
        """The shape theorem's interval is (W(SOFT), W(HARD)]. If the 2 are
        equal that interval is EMPTY and the theorem says nothing."""
        soft, hard = _factor(text, "W(SOFT)"), _factor(text, "W(HARD)")
        assert soft < hard, (
            f"W(SOFT) = {soft} and W(HARD) = {hard}. The interval "
            f"({soft}, {hard}] is empty, so caution 3's theorem is vacuous.")
        assert (soft, hard) == (0.5, 1.0), (
            f"the class weights moved to {(soft, hard)}. Every figure in "
            f"caution 3 and every cut argument is stated for (0.5, 1.0); "
            f"re-derive them before changing these.")

    def test_a_disproved_finding_scores_exactly_zero(self, text):
        """THE KEY PROPERTY. Anything but 0.0 here and a refuted finding can
        carry severity, which is the veto the whole section exists for."""
        v_false = _factor(text, "V(False)")
        assert v_false == 0.0, (
            f"V(False) = {v_false}, not 0.0. A computationally disproved "
            f"finding would then score W.confidence.{v_false} > 0 and the "
            f"veto is gone.")

    def test_the_product_really_is_zero_by_two_tools(self, text):
        """EXECUTED, not read: the table's own values put through the formula."""
        hard = _factor(text, "W(HARD)")
        v_false = _factor(text, "V(False)")
        conf = Real("confidence")
        s = Solver()
        s.add(conf >= 0, conf <= 1, hard * conf * v_false > 0)
        assert s.check() == unsat, "z3 finds a positive severity for a refuted finding"
        c = sp.symbols("c", nonnegative=True)
        assert sp.simplify(sp.Float(hard) * c * sp.Float(v_false)) == 0, \
            "SymPy does not reduce the refuted product to 0"


class TestTheSelectionPredicateStillConjoins:
    def test_7_11_requires_both_quantities(self, text):
        """THE FACT THAT REFUTED THIS SESSION'S BRIEF. If 7.11 stops requiring
        both, `Sev` and `S_v` really would be competing specifications and the
        brief's headline would become arguable again."""
        m = re.search(r"selected\(f\)\s*≡\s*(.+)", text)
        assert m, "7.11's selection predicate is gone"
        pred = m.group(1)
        assert "Sev(f)" in pred, "the predicate no longer mentions Sev(f)"
        assert "S_v(f)" in pred, (
            "the predicate no longer mentions S_v(f), so the appendix no "
            "longer conjoins the severity and the credence -- the refutation "
            "of the 2026-11-06 brief rested on exactly this")
        assert "∧" in pred, "the predicate is no longer a conjunction"

    def test_the_credence_is_named_as_one(self, text):
        """7.8 derives P(claim true) while 2 places call it a severity."""
        assert "`S_v` is a credence, not a severity" in text, (
            "the clarification is gone. `S_v` is called 'multi-verifier "
            "Bayesian severity' at 2 sites while 7.8 derives P(claim true), "
            "and that naming is what seeded the brief's type confusion.")


class TestTheseAssertionsAreNotVacuous:
    def test_the_table_is_actually_parsed(self, text):
        """If the regex matched nothing every test above would error rather
        than pass, but a reader cannot tell. State the parse explicitly."""
        got = {n: _factor(text, n) for n in
               ("W(HARD)", "W(SOFT)", "V(True)", "V(None)", "V(False)")}
        assert len(set(got.values())) >= 3, (
            f"only {len(set(got.values()))} distinct factor values parsed: "
            f"{got}. The table is probably not being read.")
