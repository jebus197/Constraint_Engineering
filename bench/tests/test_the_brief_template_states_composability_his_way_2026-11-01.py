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
    """The patterns that recognise his DEMONSTRATED form, wherever they live.

    ★ AMENDED 2026-11-01, LATER THE SAME DAY, ON A MEASUREMENT. This looked the
    check up in `V.CHECKS`, the REQUIRED set, and that is where it was first
    shipped. As a REQUIRED check it refused **134 of 139** archived briefs,
    0.964029, Wilson 95% [0.918560, 0.984539] -- and refused
    `bench/directives/universal/panel_brief_template.md` ITSELF, which failed
    exactly 1 check and that check was this one. A brief written exactly as
    instructed would have been rejected at dispatch. The check is now REPORTED
    through `composability_advisory`, following `check_declared_figures`, which
    is advisory for the identical reason.

    THE 3 PROPERTIES THESE TESTS DEFEND ARE UNCHANGED: a composability check
    exists, his form satisfies it, and the weak form does NOT. Only the lookup
    moved. What is no longer asserted -- deliberately, and with the figure above
    as the reason -- is that it REFUSES.
    """
    pats = getattr(V, "_DEMONSTRATED_COMPOSABILITY", None)
    if pats is None:
        hits = [c for c in V.CHECKS if "composab" in c[0].lower()]
        assert hits, (
            "the validator carries no composability patterns at all, in CHECKS "
            "or as _DEMONSTRATED_COMPOSABILITY, so a brief author is prompted "
            "for nothing and the weak form is what gets written")
        return hits[0]
    assert callable(getattr(V, "composability_advisory", None)), (
        "_DEMONSTRATED_COMPOSABILITY exists with no reader: an addition "
        "nothing reaches is not an addition")
    return ("states composability as a DEMONSTRATED advantage", pats, "")


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


class TestItIsReportedRatherThanRefused:
    """★ PINNED 2026-11-01 so the demotion cannot be silently reversed.

    Shipping it as a REQUIRED check refused 134 of 139 archived briefs and the
    template itself. Anyone restoring it to `CHECKS` must first show the archive
    refusal rate is in the class the project accepts -- the disagreement check's
    12 of 95 = 0.126316 -- rather than 0.964029.
    """

    def test_it_is_not_in_the_required_set(self, V):
        labels = [c[0] for c in V.CHECKS]
        assert not any("composab" in l.lower() for l in labels), (
            "the composability check is REQUIRED again. As a refusal it rejects "
            "134 of 139 archived briefs and the template itself; report it "
            "instead. See scripts/the_brief_template_mutations_2026-11-01.py.")

    def test_the_template_satisfies_it(self, V):
        """The half his ruling actually asked for."""
        tpl = (pathlib.Path(__file__).resolve().parents[2] / "bench"
               / "directives" / "universal" / "panel_brief_template.md")
        assert V.composability_advisory(tpl.read_text(encoding="utf-8")) == [], (
            "the TEMPLATE does not state composability his way, so an author is "
            "never prompted and the advisory points at nothing")


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
