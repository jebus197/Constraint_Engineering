"""The directive tells every model how our own stages relate. Execute its claims.

WHY. `bench/directives/universal/cdsfl_core_formal.md` is read IN FULL by
`reference_runner_v3.py:13251` and shipped to every model dispatched through the
runner -- measured 2026-09-06: 26909 characters, verbatim. (The composer path is
clean: it extracts a packet that excludes this note, verified for opus_4_6,
deepseek_v3 and gemini_3_1_pro.) So a false mathematical claim here is not a
documentation blemish; it is an input to the experiment.

It carried one. It said "C(n) is a special case of R_k(i) with π = 0". At π = 0
the recursion is identically 0 at every step, because 0 is a fixed point of the
update -- so the stated parameter yields the constant 0 and never C(n).

These tests do NOT assert on the directive's prose alone. They pull the parameter
value the directive claims and EXECUTE the recursion at it, so any future edit that
reinstates a wrong number fails here rather than reaching a model.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

sp = pytest.importorskip("sympy")

REPO = Path(__file__).resolve().parents[2]
DIRECTIVE = REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"


def _recursion(prior, q, steps):
    """R_k(i) = R_k(i-1)(1-q)/(1 - q R_k(i-1)), run `steps` times from `prior`."""
    r = sp.nsimplify(prior)
    for _ in range(steps):
        r = sp.simplify(r * (1 - q) / (1 - q * r))
    return r


@pytest.fixture(scope="module")
def directive_text():
    return DIRECTIVE.read_text(encoding="utf-8")


def test_pi_zero_is_a_fixed_point_so_it_cannot_yield_C_n():
    """The refuted claim, executed. This is why the directive was wrong."""
    q = sp.Symbol("q", positive=True)
    for steps in (1, 2, 3, 5, 10):
        assert _recursion(0, q, steps) == 0, (
            f"at pi=0 the recursion should be identically 0 after {steps} steps"
        )
    p, n = sp.Symbol("p", positive=True), sp.Symbol("n", positive=True, integer=True)
    C_n = 1 - (1 - p) ** n
    assert sp.simplify(C_n) != 0, "C(n) is not the zero function, so pi=0 cannot give it"


def test_the_prior_the_directive_now_claims_actually_works():
    """Pull pi from the directive's own sentence and EXECUTE the recursion at it."""
    text = DIRECTIVE.read_text(encoding="utf-8")
    m = re.search(r"at\s*π\s*=\s*([0-9]+/[0-9]+|[0-9.]+)\s*,\s*K\s*=\s*1", text)
    assert m, "the directive no longer states the prior it claims; this test cannot be vacuous"
    prior = sp.nsimplify(m.group(1))

    p = sp.Symbol("p", positive=True)
    n_steps = 4
    got = sp.simplify(_recursion(prior, p, n_steps))
    want = (1 - p) ** n_steps / (1 + (1 - p) ** n_steps)
    assert sp.simplify(got - want) == 0, (
        f"the directive claims pi = {prior} gives (1-p)^n/(1+(1-p)^n); executing it gives {got}"
    )


def test_the_stated_risk_to_coverage_map_is_the_one_that_holds():
    """The directive now says R = (1-C)/(2-C) per class. Execute the round trip."""
    C = sp.Symbol("C", positive=True)
    R = (1 - C) / (2 - C)
    inv = sp.solve(sp.Eq(sp.Symbol("R_s"), R), C)
    assert len(inv) == 1
    assert sp.simplify(R.subs(C, inv[0]) - sp.Symbol("R_s")) == 0, "round trip must be exact"
    # And it agrees with the general per-class form at pi = 1/2.
    pi_h = sp.Rational(1, 2)
    general = pi_h * (1 - C) / ((1 - pi_h) + pi_h * (1 - C))
    assert sp.simplify(general - R) == 0


def test_the_directive_no_longer_carries_the_refuted_claim(directive_text):
    """A document IS its text, so for the retired claim the text is the artefact."""
    assert "special case of R_k(i) with" not in directive_text
    assert "π = 0 and all pass-specific factors" not in directive_text


def test_the_directive_no_longer_calls_all_five_links_strict_generalisations(directive_text):
    note = directive_text[directive_text.index("Stage-awareness note"):]
    note = note[:note.index("termination accounting")]
    assert "Each\n> stage is a strict generalisation" not in note
    assert "not all of one kind" in note, "the corrected distinction must be stated, not merely the error removed"


def test_the_six_row_table_is_called_six(directive_text):
    """The off-by-one cc2 found: 'five stages' printed above a 6-row lineage."""
    note = directive_text[directive_text.index("Stage-awareness note"):]
    note = note[:note.index("termination accounting")]
    assert "six-stage" in note and "five-stage" not in note
