"""How much DONE evidence actually runs when a DONE marker is committed.

TASK V7 closed the V3 incident -- a DONE marker naming a test that was 10 of 10
RED -- with `unsupported_done_entries`, which attributes a session's failures back
to the entries that named them. Its own docstring concedes the limit: it maps
failures a run ALREADY PRODUCED and runs nothing itself.

A DONE MARKER IS WRITTEN IN A COMMIT, and a commit runs `hooks/pre-commit`'s
GUARDS list and nothing else. So the concession has a size, and until 2026-09-11
nobody had measured it. The cc2 seat measured it in panel round 11; this
reproduces it and keeps it true.

MEASURED HERE: 2 of 52 DONE-evidence files run at commit time, 3.8462%, Wilson
[1.0611%, 12.9812%], Clopper-Pearson [0.4692%, 13.2128%]. The V3 window is
therefore open for 50 of 52 entries.

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
        from statsmodels.stats.proportion import proportion_confint
        from scipy.stats import beta as sbeta
        guards = set(mod.guard_files())
        ev = mod.done_evidence()
        k, n = len(set(ev) & guards), len(ev)
        _lo, hi_c = proportion_confint(k, n, method="beta")
        hi_s = sbeta.ppf(0.975, k + 1, n - k)
        assert abs(hi_s - hi_c) < 1e-12, (hi_s, hi_c)


class TestItSaysWhatItDoesNotDo:
    def test_it_names_the_fix_and_declines_to_enact_it(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert "git diff --cached" in r.stdout, (
            "the script no longer names the repair, so the measurement sits "
            "there with nothing to do")
        assert "not enacted" in r.stdout
