"""Task 2.2: the falsifier exp42 C0037 never got. It deleted a formula.

THE FINDING, DeepSeek, severity 0.70, recorded UNCONFIRMED / UNTOOLABLE with an
empty falsifier_code: "The function `_semantically_duplicate` uses a containment
check: if the Jaccard is >= 0.95 with respect to [the shorter side]".

CONFIRMED, WITH A DEMONSTRATED AND QUANTIFIED HARM.

The rule is `intersection / min(len(left), len(right)) >= 0.95`. A short line
whose tokens are contained in a longer one is therefore a "duplicate" of it, no
matter how much more the longer line says -- and the dedup keeps whichever came
FIRST, so the survivor is decided by position, not by content.

MEASURED over the real directive corpus: 14 of 1,677 lines are dropped as
duplicates (0.8348%, Wilson [0.4979%, 1.3964%]), and 11 of those 14 are dropped
by CONTAINMENT ALONE with a Jaccard below the 0.85 bar (78.5714%, Wilson
[52.4108%, 92.4286%], Clopper-Pearson [49.2024%, 95.3421%]). It runs for 4 of the
5 models -- every `concise` and `minimal` phenotype.

THE CASE THAT MAKES IT REAL. In `logistics_supply_chain.txt` the dedup DROPS

    SS = z * sqrt(LT * sigma_d^2 + d_bar^2 * sigma_LT^2)

and KEEPS

    SS = z * sigma_d * sqrt(LT)

The kept line is the dropped line at `sigma_LT = 0`: a strict special case,
constant lead time. SymPy: `general**2 - simple**2 = d_bar**2 * sigma_LT**2 *
z**2`, positive for positive quantities, and z3 returns UNSAT for "can general be
less than simple". At z = 1.645, LT = 9, sigma_d = 20, d_bar = 100,
sigma_LT = 0.5 the surviving formula understates safety stock by 29.778607 units,
128.478607 against 98.700000 -- 23.1770%.

So the dedup deleted the general formula and kept the special case, and a model
reading that directive is told to size safety stock with a formula that cannot
see lead-time variability at all.

NO FIX IS APPLIED HERE. Changing which lines survive changes the directive text
every model receives and invalidates replay of archived runs -- the same class as
C0040 and as the S* threshold promotion, which this project ruled needs the
founder. The proposed patch is 1 line and is recorded in
`experimental_notes/PARKED_FOR_THE_FOUNDER.md`: when containment fires, keep the
line with MORE tokens rather than the earlier one. That never loses information,
and it changes only which of a pair survives, not which pairs are matched.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry.composer import (  # noqa: E402
    DIRECTIVES_DIR,
    PHENOTYPE_TRANSFORMS,
    _normalise_tokens,
    _semantically_duplicate,
)

GENERAL = "SS = z * sqrt(LT * sigma_d^2 + d_bar^2 * sigma_LT^2)."
SPECIAL = "SS = z * sigma_d * sqrt(LT)"


class TestTheMechanism:
    def test_a_short_contained_line_is_called_a_duplicate(self):
        short = "Never delete a git ref without the founder present."
        long_ = ("When handling repository history you should be careful. Never "
                 "delete a git ref without the founder present in the room, and "
                 "note that refs may be recreated from the reflog within the gc "
                 "window, that tags behave differently from branches, and that a "
                 "force push rewrites remote state for every other clone.")
        assert _semantically_duplicate(short, long_), (
            "containment no longer fires; C0037's mechanism is gone")
        lt, rt = _normalise_tokens(short), _normalise_tokens(long_)
        jac = len(lt & rt) / len(lt | rt)
        assert jac < 0.85, (
            f"these 2 lines are genuine Jaccard duplicates at {jac:.4f}, so this "
            f"case no longer isolates the containment rule")

    def test_it_runs_for_most_of_the_roster(self):
        styles = [t.format_style for t in PHENOTYPE_TRANSFORMS.values()]
        dedup = [s for s in styles if s in ("concise", "minimal")]
        assert len(dedup) >= 3, (
            f"only {len(dedup)} of {len(styles)} models run the dedup; the "
            f"finding's reach has shrunk")


class TestTheFormulaCase:
    """The one that turns a mechanism into a harm."""

    def test_the_two_formulas_are_still_in_the_corpus(self):
        f = pathlib.Path(DIRECTIVES_DIR) / "logistics" / "logistics_supply_chain.txt"
        if not f.is_file():
            candidates = list(pathlib.Path(DIRECTIVES_DIR).rglob("logistics_supply_chain.txt"))
            if not candidates:
                pytest.skip("the logistics directive is no longer present")
            f = candidates[0]
        text = f.read_text(encoding="utf-8")
        assert "sigma_LT" in text, "the general formula is gone from the corpus"

    def test_the_dedup_calls_them_duplicates(self):
        assert _semantically_duplicate(GENERAL, SPECIAL), (
            "the 2 safety-stock formulas are no longer matched, so this harm "
            "may be closed -- re-measure before removing this test")

    def test_the_kept_line_is_a_strict_special_case_of_the_dropped_one(self):
        """SymPy AND z3, because a claim this load-bearing needs 2 tools."""
        import sympy as sp
        z, LT, sd, dbar, sLT = sp.symbols(
            "z LT sigma_d d_bar sigma_LT", positive=True)
        general = z * sp.sqrt(LT * sd**2 + dbar**2 * sLT**2)
        special = z * sd * sp.sqrt(LT)
        assert sp.simplify(general.subs(sLT, 0) - special) == 0, (
            "the kept formula is not the dropped one at sigma_LT = 0")
        gap = sp.simplify(sp.expand(general**2 - special**2))
        assert gap == dbar**2 * sLT**2 * z**2, gap

        from z3 import Reals, Solver, unsat
        zz, ll, ss, dd, tt = Reals("z LT sd dbar sLT")
        s = Solver()
        s.add(zz > 0, ll > 0, ss > 0, dd > 0, tt > 0)
        s.add(zz * zz * (ll * ss * ss + dd * dd * tt * tt) < zz * zz * ll * ss * ss)
        assert s.check() == unsat, (
            "z3 found a case where the general formula is smaller than the "
            "special one, which would refute the domination claim")

    def test_the_understatement_is_material_at_a_realistic_point(self):
        """A strict inequality that is 1e-9 wide would not be worth reporting."""
        import mpmath as mp
        import numpy as np
        mp.mp.dps = 30
        z, LT, sd, dbar, sLT = 1.645, 9, 20, 100, 0.5
        gen = float(mp.mpf(z) * mp.sqrt(LT * mp.mpf(sd)**2 + mp.mpf(dbar)**2 * mp.mpf(sLT)**2))
        spc = float(mp.mpf(z) * mp.mpf(sd) * mp.sqrt(LT))
        gen_np = z * np.sqrt(LT * sd**2 + dbar**2 * sLT**2)
        assert abs(gen - gen_np) < 1e-9, "mpmath and numpy disagree"
        assert gen > spc
        assert (gen - spc) / gen > 0.2, (
            f"the understatement is only {(gen - spc) / gen:.4%}; recheck whether "
            f"this case is still worth citing")


class TestTheDropRateIsBounded:
    def test_it_is_rare_and_the_rarity_is_stated(self):
        """0.8348% of lines. Reporting the harm without the rate would inflate it."""
        dropped = total = 0
        for f in sorted(pathlib.Path(DIRECTIVES_DIR).rglob("*.txt")):
            kept: list[str] = []
            for line in f.read_text(encoding="utf-8", errors="replace").split("\n"):
                if not line.strip():
                    continue
                total += 1
                if any(_semantically_duplicate(line, e) for e in kept):
                    dropped += 1
                else:
                    kept.append(line)
        assert total > 1000, total
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(dropped, total, method="wilson")
        assert dropped > 0, "nothing is dropped at all; the finding is closed"
        assert hi < 0.05, (
            f"the drop rate rose to [{lo:.4%}, {hi:.4%}]; this is no longer a "
            f"rare event and the disposition should be revisited")
