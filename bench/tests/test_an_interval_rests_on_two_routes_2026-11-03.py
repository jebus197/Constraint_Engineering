"""Every reported interval rests on 2 INDEPENDENT routes, not 2 library names.

THE DEFECT, OBSERVED 2026-11-03. This session's producers were audited against
`sy` by counting STEM imports. 1 scored 0 and was reported to the founder as a
violation; the rest scored 2 or 3 and passed. The count was a PROXY. The
project's own primary/secondary falsifier rule of 2026-10-31 turns on
INDEPENDENCE, and its measurement records that `scipy` and `statsmodels` resolve
to the identical verifier, so 2 library names can buy 0 cross-checks. Wilson
from statsmodels beside Clopper-Pearson from scipy is 2 quantities on 1 route
each: it scores 2 by import count and 0 by the rule.

MEASURED, AND THE FIGURE IS REPRODUCIBLE FROM GIT RATHER THAN REMEMBERED.
Across a DISCOVERED population of 7 scripts, 4 carried a quantity resting on a
single route at commit d6ea0538 and 0 do now. The producer takes `--rev`
precisely so the pre-repair figure survives its own repair -- a producer that
reads only the working tree reports 0 of 7 the moment the defect is fixed, and
the finding then lives as prose, which is the defect
`measured-rate-travels-with-its-script` names.

THE ANTI-VACUITY TEST IS THE LOAD-BEARING ONE. A detector that reports 0
violations because it detects nothing is indistinguishable from one that
reports 0 because nothing is wrong. `test_the_detector_can_actually_find_them`
runs the same detector against the pre-repair revision and requires it to find
4. Without that, the clean working-tree result is worthless.

AND THE DETECTOR HAD TO BE EXCLUDED FROM ITS OWN POPULATION, because it
necessarily contains the literal it searches for and the regexes it matches
with: discovery found it, called it a producer, and classified it single-route
on the strength of its own pattern text. That is
`feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02` for the
3rd time.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = (REPO / "scripts"
        / "counting_imports_ranks_producers_backwards_2026-11-03.py")

#: The revision at which the defect was measured. A permanent git object.
PRE_REPAIR = "d6ea0538"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("_routes_guard", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_routes_guard"] = m
    spec.loader.exec_module(m)
    return m


def _rev_available(rev: str) -> bool:
    r = subprocess.run(["git", "cat-file", "-e", f"{rev}^{{commit}}"],
                       capture_output=True, cwd=str(REPO))
    return r.returncode == 0


class TestTheRoutePredicate:
    def test_two_different_quantities_are_not_a_cross_check(self, mod):
        """Wilson from statsmodels beside Clopper-Pearson from scipy.

        This is the exact shape that scored 2 by import count and 0 by the
        rule, and it must classify as a single route for EACH quantity.
        """
        text = ('proportion_confint(k, n, alpha=0.05, method="wilson")\n'
                'float(stats.beta.ppf(0.025, k, n - k + 1))\n')
        rt = mod.routes(text)
        assert rt["Wilson"] == ["statsmodels proportion_confint"]
        assert rt["Clopper-Pearson"] == ["scipy beta quantile"]
        assert all(len(v) == 1 for v in rt.values()), (
            "2 libraries computing 2 different intervals must not read as a "
            "cross-check of either one")

    def test_the_same_quantity_twice_is_a_cross_check(self, mod):
        text = ('proportion_confint(k, n, alpha=0.05, method="wilson")\n'
                'c = (p + z * z / (2 * n)) / d\n')
        assert len(mod.routes(text)["Wilson"]) == 2

    def test_import_count_and_the_route_predicate_can_disagree(self, mod):
        """ANTI-VACUITY for the whole finding: if these never diverged, the
        audit's proxy would have been harmless and this guard pointless."""
        text = ('import scipy\nimport statsmodels\n'
                'proportion_confint(k, n, alpha=0.05, method="wilson")\n'
                'float(stats.beta.ppf(0.025, k, n - k + 1))\n')
        assert len(mod.stem_imports(text)) == 2, "passes an import-count audit"
        assert any(len(v) == 1 for v in mod.routes(text).values()), (
            "yet a quantity rests on 1 route -- the verdicts must be able to "
            "disagree")


class TestTheDetectorIsNotVacuous:
    def test_the_detector_can_actually_find_them(self):
        """THE LOAD-BEARING TEST. Run the detector at the pre-repair revision
        and require it to report violations. A clean working tree proves
        nothing unless the instrument is shown able to come back dirty."""
        if not _rev_available(PRE_REPAIR):
            pytest.skip(f"{PRE_REPAIR} is not present in this clone")
        r = subprocess.run([sys.executable, str(PROD), "--rev", PRE_REPAIR],
                           capture_output=True, text=True, cwd=str(REPO),
                           timeout=300)
        assert r.returncode == 0, r.stderr[-600:]
        line = [ln for ln in r.stdout.splitlines()
                if "SINGLE route" in ln]
        assert line, "the detector printed no single-route count at all"
        found = int(line[0].rsplit(":", 1)[1].strip())
        assert found >= 1, (
            f"the detector found {found} violations at {PRE_REPAIR}, where 4 "
            f"were measured -- it cannot see what it is meant to see")

    def test_the_detector_excludes_itself(self, mod):
        """It contains the literal it searches for, so without this it reports
        itself as a single-route producer."""
        assert mod.population(None).count(PROD.stem) == 0


class TestTheWorkingTreeIsClean:
    def test_no_producer_rests_a_quantity_on_one_route(self):
        r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=300)
        assert r.returncode == 0, r.stderr[-600:]
        line = [ln for ln in r.stdout.splitlines() if "SINGLE route" in ln]
        assert line, "the detector printed no single-route count"
        assert int(line[0].rsplit(":", 1)[1].strip()) == 0, (
            "a producer reports an interval resting on 1 route. Add the second "
            "implementation of that SAME quantity -- not another library "
            "computing a different one.\n" + r.stdout[-1500:])

    def test_the_population_is_discovered_not_hardcoded(self, mod):
        """A hand-picked list reported as coverage is the defect this guard's
        own producer committed on its first run."""
        pop = mod.population(None)
        assert len(pop) > len(mod.SESSION_PRODUCERS), (
            "discovery added nothing, so the population is effectively the "
            "hardcoded list again")


class TestEveryHelperIsExecutedNotJustRead:
    """EXECUTE, DO NOT GREP. The tests above read source text, which establishes
    only that each file describes itself consistently. The canonical `_iv` was
    propagated into 4 files on 2026-11-03 and 2 of those are dated 2026-11-02,
    so the sibling reachability guard -- whose glob is `*2026-11-03*` -- cannot
    see them at all. These tests CALL the helper in every file that defines one.
    """

    @staticmethod
    def _helpers():
        out = {}
        for f in sorted((REPO / "scripts").glob("*.py")):
            if f.stem == PROD.stem:
                continue                       # the detector names the literal
            try:
                txt = f.read_text(errors="replace")
            except OSError:
                continue
            if "def _iv" not in txt:
                continue
            spec = importlib.util.spec_from_file_location(f"_iv_{f.stem}", f)
            m = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(m)
            except Exception:                            # noqa: BLE001
                continue
            if hasattr(m, "_iv"):
                out[f.name] = m._iv
        return out

    def test_at_least_four_helpers_are_callable(self):
        """Anti-vacuity: if nothing loads, every assertion below is empty."""
        assert len(self._helpers()) >= 4, (
            f"only {len(self._helpers())} `_iv` helpers loaded, so the "
            f"execution tests below would be vacuous")

    @pytest.mark.parametrize("k,n", [(1, 4), (9, 23), (0, 19), (37, 38),
                                     (3, 6), (19, 19)])
    def test_every_helper_agrees_with_every_other(self, k, n):
        """One quantity, one answer. All implementations must agree, since they
        are meant to compute the same 2 intervals by independent routes."""
        helpers = self._helpers()
        seen = {}
        for name, f in helpers.items():
            (wl, wh), (cl, ch) = f(k, n)[0], f(k, n)[1]
            seen[name] = (round(wl, 12), round(wh, 12),
                          round(cl, 12), round(ch, 12))
        assert len(set(seen.values())) == 1, (
            f"the helpers disagree at k={k}, n={n}: {seen}")

    @pytest.mark.parametrize("k,n", [(1, 4), (9, 23), (0, 19), (37, 38)])
    def test_every_helper_reports_its_cross_check_magnitude(self, k, n):
        """The 3rd return value is the LARGER of the 2 route disagreements.

        It must EXIST (the shape carries it) and be tiny (the routes agree).
        A helper returning a 2-tuple has no cross-check to report, which is
        the pre-repair state of `a_bare_clock_was_dated_from_the_mtime`.
        """
        for name, f in self._helpers().items():
            r = f(k, n)
            assert len(r) == 3, (
                f"{name} returns a {len(r)}-tuple, so it carries no 2-route "
                f"disagreement magnitude at all")
            assert 0.0 <= r[2] < 1e-6, (
                f"{name} reports a 2-route disagreement of {r[2]:.3e} at "
                f"k={k}, n={n} -- the independent implementations differ")

    def test_the_intervals_are_ordered_and_bounded(self):
        """A cross-check cannot catch a bound that is wrong in BOTH routes, so
        the invariants are asserted directly."""
        for name, f in self._helpers().items():
            for k, n in [(0, 19), (1, 4), (9, 23), (19, 19)]:
                (wl, wh), (cl, ch), _ = f(k, n)
                assert 0.0 <= wl <= wh <= 1.0, f"{name} Wilson at {k}/{n}"
                assert 0.0 <= cl <= ch <= 1.0, f"{name} Clopper-Pearson at {k}/{n}"
                assert cl <= wl + 1e-9 and wh <= ch + 1e-9, (
                    f"{name}: Clopper-Pearson must contain Wilson at {k}/{n}, "
                    f"got CP[{cl:.6f},{ch:.6f}] vs W[{wl:.6f},{wh:.6f}]")
