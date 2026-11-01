"""A brief must state composability as he defines it, and may not state it weakly.

HIS RULING, 2026-11-01: *"I remember this. Yes do it as instructed. stm"* — and
the half he had already instructed was done. His definition of 2026-10-02 is in
both instruction files verbatim and in the dispatcher's SYSTEM prompt, held by a
guard of 6 tests.

THE TEMPLATE WAS THE OTHER HALF AND IT DISAGREED WITH ALL OF THEM. A brief
author is prompted by what `scripts/panel_brief_validate.py` requires, and that
list required NOTHING about composability — so the one brief that addressed it
stated the standard in full as *"say whether the repairs compose, conflict, or
are independent"*, the weak non-interference form his definition explicitly
excludes. Measured 2026-10-31: 10 of 10 uses of the word across the decisions
file and the morning report took that weak sense, Wilson [0.722467, 1.000000].

BOTH DIRECTIONS ARE NEEDED AND THAT IS THE POINT. Requiring the strong form
alone leaves a brief free to carry BOTH, and the weak sentence is the one a seat
acts on. So the weak form is refused outright rather than merely unrequired.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

WEAK = ("3. **COMPOSABILITY** — say whether the 3 repairs compose, conflict, or "
        "are independent. If 2 of them touch the same path, say which wins.")
STRONG = ("3. **COMPOSABILITY** — compose only where the composed fix "
          "demonstrably provides a better result than either fix in isolation, "
          "and show the measurement. Where a single fix performs as well, "
          "prefer it.")


@pytest.fixture(scope="module")
def V():
    spec = importlib.util.spec_from_file_location(
        "pbv_t", REPO / "scripts" / "panel_brief_validate.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["pbv_t"] = m
    spec.loader.exec_module(m)
    return m


def _composability_check(V):
    hits = [c for c in V.CHECKS if "composab" in c[0].lower()]
    assert hits, ("the brief template carries no composability requirement, so "
                  "a brief author is prompted for nothing and the weak form is "
                  "what gets written")
    return hits[0]


class TestTheStrongFormIsRequired:
    def test_a_composability_check_exists(self, V):
        _composability_check(V)

    def test_it_is_satisfied_by_his_form(self, V):
        _label, pats, _remedy = _composability_check(V)
        assert any(re.search(p, STRONG, re.M | re.I) for p in pats), (
            "a brief stating the standard as he defines it does not satisfy "
            "the check, so the check asks for something else")

    def test_it_is_NOT_satisfied_by_the_weak_form(self, V):
        """ANTI-VACUITY. A check both forms satisfy requires nothing."""
        _label, pats, _remedy = _composability_check(V)
        assert not any(re.search(p, WEAK, re.M | re.I) for p in pats), (
            "the weak non-interference wording satisfies the check, so the "
            "check cannot tell his standard from the form he excludes")


class TestTheWeakFormIsRefused:
    def test_the_weak_wording_is_matched(self, V):
        assert V._WEAK_COMPOSABILITY.search(WEAK)

    def test_his_wording_is_not_matched(self, V):
        """A refusal that fired on his own definition would make every correct
        brief defective — the guard-accusing-correct-material class."""
        assert not V._WEAK_COMPOSABILITY.search(STRONG)

    def test_the_refusal_is_REACHED_by_the_validator_not_merely_defined(self, V):
        """THE WIRING. A pattern defined and never consulted is the
        addition-reaching-nothing defect confirmed 11 times here."""
        src = (REPO / "scripts" / "panel_brief_validate.py").read_text(encoding="utf-8")
        import ast
        tree = ast.parse(src)
        used = [n for n in ast.walk(tree)
                if isinstance(n, ast.Attribute) and n.attr == "finditer"
                and isinstance(n.value, ast.Name)
                and n.value.id == "_WEAK_COMPOSABILITY"]
        assert used, ("_WEAK_COMPOSABILITY is defined and never iterated, so no "
                      "brief is ever checked against it")

    def test_ordinary_prose_about_independence_is_not_accused(self, V):
        """The words composable and independent appear legitimately. A refusal
        keyed on them alone would fire on a correct brief."""
        for ok in ("The 2 falsifiers are independent of each other.",
                   "Say whether the finding is independent of the roster.",
                   "Composability requires a measurement, so show one."):
            assert not V._WEAK_COMPOSABILITY.search(ok), ok
