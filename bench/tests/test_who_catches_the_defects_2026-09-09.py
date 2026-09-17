"""Task 1.2: the catcher statistics, executed rather than named.

WHY THIS FILE EXISTS. Task 1.2 named `bench/tests/test_operational_scripts.py`
as its evidence. That file reaches `scripts/who_catches_the_defects_2026-09-09.py`
only through its `SCRIPT_PATHS` glob, in 2 parametrised cases: `--help` exits 0
and an unknown flag exits 2. A copy of the script with the FOUNDER and SUITE
labels swapped reverses the conclusion and leaves both exit codes unchanged, so
that file cannot see the analysis. This one calls it.

WHAT IS PINNED, AND FROM WHERE.
  * The table: 19 rows, SUITE 7, SELF 7, FOUNDER 4, LINT 1.
  * The 2 tests the script prints: exact binomial p = 0.1938 for 8 mechanism
    catches against 4 founder catches, and Fisher p = 0.1102, odds 4. Recomputed
    here from the table with scipy, and read back from the script's own stdout,
    so the printed form and the data cannot drift apart.
  * A mutation control that runs the script's `main()` on an altered table and
    shows the pinned figures move.

WHAT IS DELIBERATELY NOT PINNED. The task entry once said the claims-versus-code
split "survives reclassifying every arguable entry in all 16 combinations",
worst case p 0.598. No committed artefact ever typed the rows CLAIM or CODE, and
under a rule where only claim-typed rows may move into FOUNDER, "every FOUNDER
row is a claim" holds by construction. A 16-combination sweep would therefore
test nothing, so none is committed here. `TestTheOld0598IsOnlyArithmetic` pins
what 0.598 actually is -- the tail for 8 against 8 -- so that figure has a
producer without being presented as robustness evidence.
"""
from __future__ import annotations

import collections
import importlib.util
import itertools
import math
import pathlib
import subprocess
import sys
from fractions import Fraction

import pytest
from scipy import stats as sps

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "who_catches_the_defects_2026-09-09.py"

PINNED_COUNTS = {"SUITE": 7, "SELF": 7, "FOUNDER": 4, "LINT": 1}
PINNED_BINOMIAL = "0.1938"
PINNED_FISHER = "0.1102"


@pytest.fixture(scope="module")
def mod():
    # Import is safe: `answer_help` and `main()` both sit behind `__main__`.
    spec = importlib.util.spec_from_file_location("who_catches", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _two_tests(defects) -> tuple[int, int, str, str]:
    """The script's own arithmetic, recomputed from a table: (mech, founder, p, fisher)."""
    by = collections.Counter(c for _, c, _ in defects)
    mech, founder = by["SUITE"] + by["LINT"], by["FOUNDER"]
    p = sps.binomtest(mech, mech + founder, 0.5, alternative="greater").pvalue
    _, pf = sps.fisher_exact([[mech, founder], [founder, mech]], alternative="greater")
    return mech, founder, f"{p:.4f}", f"{pf:.4f}"


class TestTheTableIsPinned:
    def test_nineteen_rows_split_seven_seven_four_one(self, mod):
        assert len(mod.DEFECTS) == 19, len(mod.DEFECTS)
        by = collections.Counter(c for _, c, _ in mod.DEFECTS)
        assert dict(by) == PINNED_COUNTS, (
            f"the catcher split moved: {dict(by)} against pinned {PINNED_COUNTS}; "
            "task 1.2 quotes the pinned split and must be re-dated if this is real")

    def test_the_rows_are_three_wide_with_no_claim_or_code_field(self, mod):
        """If a 4th field ever appears, the 'not recorded as data' reading is stale."""
        assert {len(t) for t in mod.DEFECTS} == {3}


class TestTheTwoTestsReproduce:
    def test_recomputed_from_the_table(self, mod):
        mech, founder, p, pf = _two_tests(mod.DEFECTS)
        assert (mech, founder) == (8, 4), (mech, founder)
        assert (p, pf) == (PINNED_BINOMIAL, PINNED_FISHER), (p, pf)

    def test_the_binomial_agrees_with_an_exact_rational_sum(self, mod):
        """2 tools: scipy above, a closed-form Fraction here sharing none of its code."""
        mech, founder, p, _ = _two_tests(mod.DEFECTS)
        n = mech + founder
        exact = Fraction(sum(math.comb(n, k) for k in range(mech, n + 1)), 2 ** n)
        assert exact == Fraction(397, 2048), exact
        assert f"{float(exact):.4f}" == p

    def test_the_script_prints_what_the_table_gives(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-800:]
        assert "Caught defects in the sample: 19" in r.stdout
        assert "mechanism took 8." in r.stdout
        assert f"p = {PINNED_BINOMIAL}" in r.stdout, r.stdout
        assert f"p = {PINNED_FISHER}, odds 4" in r.stdout, r.stdout


class TestTheMutationControl:
    """The analysis must move when the table moves; otherwise the pins above prove nothing."""

    def _run_main(self, mod, monkeypatch, capsys, table):
        monkeypatch.setattr(mod, "DEFECTS", table)
        assert mod.main() == 0
        return capsys.readouterr().out

    def test_the_live_table_prints_the_pinned_figures(self, mod, monkeypatch, capsys):
        out = self._run_main(mod, monkeypatch, capsys, list(mod.DEFECTS))
        assert f"p = {PINNED_BINOMIAL}" in out and f"p = {PINNED_FISHER}" in out

    def test_relabelling_one_founder_row_moves_the_figures(self, mod, monkeypatch, capsys):
        table = list(mod.DEFECTS)
        i = next(j for j, (_, c, _) in enumerate(table) if c == "FOUNDER")
        table[i] = (table[i][0], "SUITE", table[i][2])
        by = collections.Counter(c for _, c, _ in table)
        assert dict(by) != PINNED_COUNTS
        out = self._run_main(mod, monkeypatch, capsys, table)
        assert f"p = {PINNED_BINOMIAL}" not in out, out
        assert "mechanism took 9." in out, out

    def test_swapping_founder_and_suite_reverses_the_conclusion(self, mod, monkeypatch, capsys):
        """The mutant the audit ran: exit codes identical, conclusion reversed."""
        swap = {"FOUNDER": "SUITE", "SUITE": "FOUNDER"}
        table = [(n, swap.get(c, c), e) for n, c, e in mod.DEFECTS]
        mech, founder, p, _ = _two_tests(table)
        assert (mech, founder, p) == (5, 7, "0.8062"), (mech, founder, p)
        out = self._run_main(mod, monkeypatch, capsys, table)
        assert "mechanism took 5." in out and "p = 0.8062" in out, out


class TestTheOld0598IsOnlyArithmetic:
    """0.598 is the binomial tail for 8 mechanism catches against 8 founder catches.

    It says how p would read if 4 SELF rows were moved to FOUNDER. Which 4 was
    never recorded, and it is not evidence that any split survives reclassification.
    """

    def test_it_is_the_tail_for_eight_against_eight(self):
        exact = Fraction(sum(math.comb(16, k) for k in range(8, 17)), 2 ** 16)
        assert exact == Fraction(39203, 65536)
        scipy_p = sps.binomtest(8, 16, 0.5, alternative="greater").pvalue
        assert abs(scipy_p - float(exact)) < 1e-12
        assert f"{float(exact):.7f}" == "0.5981903"

    def test_no_other_split_of_at_most_nineteen_rounds_to_it(self):
        hits = [(m, f) for m, f in itertools.product(range(20), repeat=2)
                if 0 < m + f <= 19
                and round(sps.binomtest(m, m + f, 0.5, alternative="greater").pvalue, 3) == 0.598]
        assert hits == [(8, 8)], hits

    def test_thirty_five_choices_of_four_self_rows_give_it(self, mod):
        self_rows = [n for n, c, _ in mod.DEFECTS if c == "SELF"]
        assert len(self_rows) == 7
        assert math.comb(len(self_rows), 4) == 35
