"""The predicate-breadth census must be EXECUTED by something, and this is it.

`scripts/a_guards_predicate_can_be_narrower_than_its_class_2026-11-13.py` counts
live process detectors and reports how many take exactly 1 pattern. It was added
on 2026-11-13 and the suite immediately reported it as a producer reached by no
test -- which is the symmetric half of `additive-standard`, and the SECOND time
in one day I committed that defect: the board-share producer did the same thing
hours earlier and got the same refusal.

★ THE CENSUS'S OWN APPARATUS EXCLUSION IS WHAT THIS GUARD MOSTLY TESTS, because
that is the part most likely to rot. The producer holds the detector pattern
itself, so without naming itself as apparatus it counts ITSELF -- the figure
moved 3 of 3 to 4 of 4 the moment it was committed. The guard asserts BOTH
figures are reported, which is the honest form the 2026-11-13 population lesson
prescribes: print the figure excluded and included so a reader sees the effect
rather than a quietly smaller denominator.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
PROD = REPO / "scripts" / "a_guards_predicate_can_be_narrower_than_its_class_2026-11-13.py"


@pytest.fixture(scope="module")
def mod():
    assert PROD.is_file(), f"the producer is gone: {PROD}"
    spec = importlib.util.spec_from_file_location("breadth_census", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["breadth_census"] = m
    spec.loader.exec_module(m)
    return m


class TestThePopulationIsNamedPositively:
    def test_live_files_excludes_archived_evidence_and_guards(self, mod):
        files = mod.live_files()
        assert files, "the census found no live files; it would be vacuous"
        bad = [p for p in files
               if any(x in str(p.relative_to(REPO)) for x in mod.EXCLUDE)]
        assert not bad, (
            f"{len(bad)} excluded path(s) are in the population anyway: "
            f"{[str(p.relative_to(REPO)) for p in bad][:3]}")

    def test_the_apparatus_names_the_producer_itself(self, mod):
        """Without this the census counts itself and the figure moves."""
        rel = str(PROD.relative_to(REPO))
        assert rel in mod.APPARATUS, (
            f"{rel} is not in APPARATUS, so the census counts its own detector "
            f"pattern. That is the defect recorded on 2026-11-13 as a "
            f"population failing to exclude its own instruments.")


class TestItRunsAndReportsBothFigures:
    def test_it_exits_zero(self):
        r = subprocess.run([sys.executable, str(PROD)], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, f"{r.stdout[-900:]}\n{r.stderr[-400:]}"
        assert "process detector" in r.stdout

    def test_it_prints_the_figure_BOTH_ways(self):
        """Excluding the apparatus must not hide the size of the effect."""
        r = subprocess.run([sys.executable, str(PROD)], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert "excluding apparatus" in r.stdout and "including it" in r.stdout, (
            "the census no longer reports its count both ways, so a reader "
            "cannot see how much the apparatus exclusion moved it:\n"
            f"{r.stdout[:600]}")

    def test_it_refuses_to_score_a_one_pattern_detector_as_a_defect(self):
        """The honest limit, asserted so it cannot be quietly dropped."""
        r = subprocess.run([sys.executable, str(PROD)], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert "NOT AUTOMATICALLY A DEFECT" in r.stdout, (
            "the census stopped stating that a 1-pattern detector may be "
            "correctly scoped. Scoring one as wrong without knowing its "
            "purpose is the flattering measure this project's record names.")


class TestTheHelpFlagIsAnswered:
    @pytest.mark.parametrize("flag", ["-h", "--help"])
    def test_it_answers_rather_than_running(self, flag):
        r = subprocess.run([sys.executable, str(PROD), flag], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0
        assert "usage:" in r.stdout, (
            f"{flag} did not print a usage line, so the flag ran the whole "
            f"census instead of answering it")
