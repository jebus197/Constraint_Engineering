"""How much DONE evidence actually runs when a DONE marker is committed.

TASK V7 closed the V3 incident -- a DONE marker naming a test that was 10 of 10
RED -- with `unsupported_done_entries`, which attributes a session's failures back
to the entries that named them. Its own docstring concedes the limit: it maps
failures a run ALREADY PRODUCED and runs nothing itself.

A DONE MARKER IS WRITTEN IN A COMMIT, and a commit runs `hooks/pre-commit`'s
GUARDS list and nothing else. So the concession has a size, and until 2026-09-11
nobody had measured it. The cc2 seat measured it in panel round 11; this
reproduces it and keeps it true.

MEASURED BY `scripts/done_evidence_commit_coverage_2026-09-11.py`, AND THE FIGURE
IS WHATEVER THAT SCRIPT PRINTS ON THE DAY IT IS RUN. This docstring used to carry
"2 of 52"; the script printed 2/55 at 6c6d053, the commit that wrote it, and
2/82 = 2.4390% at 989f32f on 2026-09-17. A count typed here drifts as DONE
entries are added and no test here can see it, so none is typed.

THE SEAT SAID 3 OF 52 AND THAT IS NOT A DISAGREEMENT. Entries 4.2 and 7.3 named
a GUARD file as their evidence -- so it counted as covered -- while that file
contains zero references to either entry's subject. Re-pointing them the same
night removed the only vacuously-covered file. The figure went DOWN because a lie
left the numerator.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "done_evidence_commit_coverage_2026-09-11.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("dec", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheGuardListIsReadNotTyped:
    def test_it_comes_from_the_hook(self, mod):
        """Two representations of one list with no comparator is what
        `test_precommit_guard_2026-09-09.py` was caught doing on its first pass."""
        got = mod.guard_files()
        hook = (ROOT / "hooks" / "pre-commit").read_text(encoding="utf-8")
        assert got, "no guards parsed"
        for g in got:
            assert g in hook, g
            assert (ROOT / g).is_file(), f"the hook names a guard that is gone: {g}"

    def test_every_guard_is_a_python_test_file(self, mod):
        for g in mod.guard_files():
            assert g.startswith("bench/tests/") and g.endswith(".py"), g


class TestTheGapIsRealAndMeasured:
    def test_coverage_is_a_strict_subset(self, mod):
        guards = set(mod.guard_files())
        evidence = set(mod.done_evidence())
        assert len(evidence) >= 40, f"only {len(evidence)} evidence files"
        covered = evidence & guards
        assert covered, "no DONE evidence runs at commit time at all"
        assert len(covered) < len(evidence), (
            "commit-time coverage has reached 100%. That is the goal, not a "
            "failure -- RETIRE this test with a note rather than deleting it, "
            "so the reason it existed stays on the record.")

    def test_the_interval_is_reported_outward(self, mod):
        """An interval printed narrower than it is overstates confidence, which
        is the one direction that matters for a gap measurement."""
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr[-400:]
        assert "Wilson 95%" in r.stdout and "Clopper-Pearson" in r.stdout

    def test_the_two_tools_agree(self, mod):
        """The script's statsmodels intervals against computations that share no
        code with scipy.

        REPLACED 2026-09-17 (panel round 16). The first version compared
        statsmodels' `beta` interval with `scipy.stats.beta.ppf`, but statsmodels
        0.14 computes that interval BY CALLING `scipy.stats.beta`, so it was 1
        tool computed twice and could not disagree. Wilson is now the closed
        form in `math`, and Clopper-Pearson is solved by bisection on the exact
        binomial tail built from `math.comb`."""
        import math
        from statsmodels.stats.proportion import proportion_confint
        guards = set(mod.guard_files())
        ev = mod.done_evidence()
        k, n = len(set(ev) & guards), len(ev)
        assert 0 < k < n, (k, n)

        z = 1.959963984540054
        p = k / n
        centre = (p + z * z / (2 * n)) / (1 + z * z / n)
        half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        lo_w, hi_w = proportion_confint(k, n, method="wilson")
        assert abs(lo_w - (centre - half)) < 1e-12 and abs(hi_w - (centre + half)) < 1e-12, (
            (lo_w, hi_w), (centre - half, centre + half))

        def tail_at_most(q, j):   # P(X <= j) for X ~ Binomial(n, q)
            return math.fsum(math.comb(n, i) * q ** i * (1 - q) ** (n - i)
                             for i in range(j + 1))

        def bisect(f, lo=0.0, hi=1.0):   # f is decreasing in q; root of f == 0
            for _ in range(200):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
            return (lo + hi) / 2

        hi_cp = bisect(lambda q: tail_at_most(q, k) - 0.025)
        lo_cp = bisect(lambda q: 0.025 - (1 - tail_at_most(q, k - 1)))
        lo_c, hi_c = proportion_confint(k, n, method="beta")
        assert abs(lo_c - lo_cp) < 1e-9 and abs(hi_c - hi_cp) < 1e-9, (
            (lo_c, hi_c), (lo_cp, hi_cp))

        # And the PRINTED Wilson interval is the script's, rounded outward.
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        import re
        m = re.search(r"Wilson 95%\s*:\s*\[([\d.]+)%, ([\d.]+)%\]", r.stdout)
        assert m, r.stdout
        lo_p, hi_p = float(m.group(1)) / 100, float(m.group(2)) / 100
        assert lo_p <= centre - half < lo_p + 1e-6 and hi_p - 1e-6 < centre + half <= hi_p, (
            (lo_p, hi_p), (centre - half, centre + half))


class TestItSaysWhatItDoesNotDo:
    def test_it_names_the_fix_and_declines_to_enact_it(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert "git diff --cached" in r.stdout, (
            "the script no longer names the repair, so the measurement sits "
            "there with nothing to do")
        assert "not enacted" in r.stdout
