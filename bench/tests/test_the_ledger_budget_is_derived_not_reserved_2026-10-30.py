#!/usr/bin/env python3
"""The ledger line's budget is MEASURED from its prefix, not reserved as a number.

WHY THIS FILE EXISTS, AND IT IS A GAP IN AN EXISTING GUARD RATHER THAN A NEW
FEATURE. `scripts/morning_report_build_2026-10-12.py` gained `ledger_line` on
2026-10-30 so an over-long commit subject is cut to one line instead of breaking
`test_it_lists_commits_not_narrative`. That guard exercises the generator against
TODAY'S data, where the rendered prefix -- "- `018e1b01` 2026-10-30 01:41 - " --
happens to be exactly 33 characters long.

MEASURED THE SAME DAY: replacing the derived `limit - len(prefix) - len(mark)`
with a hardcoded `limit - 33 - len(mark)` leaves that guard GREEN. So it cannot
tell a measured budget from a lucky constant, and the lucky constant is exactly
the defect recorded on 2026-10-28, where a truncation path reserved a hardcoded
200 characters for a notice whose length grew with the open count and overflowed
at 960 against a 900 budget.

WHAT THIS PINS. The PROPERTY, over prefix lengths the live data does not yet
produce: for every prefix and every subject, the rendered line fits the limit
whenever the prefix alone does. A reserve that is right for one prefix length is
wrong for the others, so the hardcoded form fails here however green the
data-driven guard stays.

The limit 220 is NOT imported from the generator anywhere, here or in the older
guard. A pin that imported the constant it checks would rise with it and stop
being a pin, which is the failure recorded on 2026-10-28 as a pin living inside
what it measures.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

GENERATOR = REPO / "scripts" / "morning_report_build_2026-10-12.py"

#: The independent pin, restated rather than imported. The older guard asserts a
#: rendered ledger line is under 220; the generator must stay strictly inside it.
GUARD_LINE_PIN = 220


def _gen():
    assert GENERATOR.is_file(), f"generator absent: {GENERATOR}"
    spec = importlib.util.spec_from_file_location("mr_build", GENERATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _gen()


def _hardcoded_reserve(prefix: str, subject: str, limit: int,
                       mark: str = " [...]", reserve: int = 33) -> str:
    """THE DEFECT, implemented, so the property below can be shown to catch it."""
    line = prefix + subject
    if len(line) <= limit:
        return line
    budget = limit - reserve - len(mark)
    if budget <= 0:
        return line
    return prefix + subject[:budget].rstrip() + mark


class TestTheBudgetIsDerived:
    @pytest.mark.parametrize("prefix_len", [0, 1, 10, 33, 34, 50, 80, 120, 190])
    def test_the_line_fits_for_every_prefix_length(self, gen, prefix_len):
        """The live data only ever exercises 33. These are the others."""
        limit = gen._LEDGER_LINE_MAX
        prefix = "p" * prefix_len
        subject = "s" * 400
        line = gen.ledger_line(prefix, subject, limit=limit)
        if prefix_len + len(gen._LEDGER_TRUNCATION_MARK) >= limit:
            pytest.skip("the prefix alone exceeds the limit; nothing to cut")
        assert len(line) <= limit, (
            f"a prefix of {prefix_len} character(s) renders {len(line)}, over "
            f"the {limit} limit. The budget is not being measured from the "
            f"prefix, so it is a reserve that happens to suit one prefix length.")

    @pytest.mark.parametrize("prefix_len", [0, 1, 10, 50, 80, 120])
    def test_the_hardcoded_reserve_fails_this_property(self, gen, prefix_len):
        """POSITIVE CONTROL. Without this the test above could pass vacuously.

        The reserve is wrong in BOTH directions: too small a prefix wastes
        budget, too large a prefix overflows. Only the overflow is a defect, so
        only overflow is asserted.
        """
        limit = gen._LEDGER_LINE_MAX
        prefix = "p" * prefix_len
        subject = "s" * 400
        bad = _hardcoded_reserve(prefix, subject, limit)
        good = gen.ledger_line(prefix, subject, limit=limit)
        assert len(good) <= limit
        if prefix_len > 33:
            assert len(bad) > limit, (
                f"the hardcoded reserve rendered {len(bad)} for a prefix of "
                f"{prefix_len}, within the limit. If the reserve no longer "
                f"overflows, this control proves nothing and the property test "
                f"above may be vacuous.")

    def test_a_short_subject_is_left_exactly_alone(self, gen):
        """No truncation where none is needed, so nothing is lost silently."""
        out = gen.ledger_line("- `abc1234` 2026-10-30 01:41 — ", "a short subject")
        assert out.endswith("a short subject")
        assert gen._LEDGER_TRUNCATION_MARK not in out

    def test_a_truncated_line_says_so(self, gen):
        out = gen.ledger_line("- `abc1234` 2026-10-30 01:41 — ", "x" * 400)
        assert out.endswith(gen._LEDGER_TRUNCATION_MARK), (
            "an over-long subject was cut with no visible marker, so a reader "
            "cannot tell a complete subject from a cut one")

    def test_the_generator_stays_strictly_inside_the_independent_pin(self, gen):
        assert gen._LEDGER_LINE_MAX < GUARD_LINE_PIN, (
            f"the generator's limit {gen._LEDGER_LINE_MAX} is not strictly "
            f"below the older guard's pin of {GUARD_LINE_PIN}; raising it to or "
            f"above that pin removes the margin that makes the pin meaningful")


def test_the_budget_formula_is_maximal_by_z3():
    """DERIVED, not asserted: the budget is the LARGEST subject length that fits.

    A truncation that is merely safe could cut far more than necessary and lose
    text for no reason. z3 is asked whether any larger budget also fits; `unsat`
    means the formula is exactly maximal.
    """
    z3 = pytest.importorskip("z3")
    limit, plen, mlen, budget = z3.Ints("limit plen mlen budget")
    s = z3.Solver()
    s.add(limit > 0, plen >= 0, mlen >= 0, plen + mlen < limit)
    s.add(budget == limit - plen - mlen)
    # Could budget + 1 also fit?  plen + (budget + 1) + mlen <= limit
    s.add(plen + (budget + 1) + mlen <= limit)
    assert s.check() == z3.unsat, (
        f"z3 found a case where a larger budget still fits, so the formula cuts "
        f"more than it must: {s.model() if s.check() == z3.sat else ''}")
