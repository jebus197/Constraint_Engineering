"""Task A8: the census counted path-shaped STRINGS; the ruling is about EVIDENCE.

A8 asks the founder to rule on cited `bench/logs/` paths that git does not track.
Before a ruling is worth asking for, the population has to be the one the question
is about, and it was not.

MEASURED 2026-09-11, of the 44 untracked paths the extractor flagged:

    23  cited by a NOTE        -- evidence a reader is pointed at
    13  TESTS ONLY             -- fixtures. `bench/logs/x/y.json` is a fixture in
                                  a test written on 2026-09-10 whose whole job is
                                  to prove the extractor REJECTS non-file paths
     6  ELIDED                 -- carrying `XX` or an ellipsis: shorthand in
                                  prose, not a citation to anything
     2  CODE ONLY

So the population a ruling is about is 23 of 127 cited paths, 18.1102%, Wilson
[12.3818%, 25.7112%], Clopper-Pearson [11.8404%, 25.9245%] -- not 44, and not the
entry's 177 of 3803, which is a different corpus again and says so.

THE CENSUS PROMOTED ITS OWN WORKED EXAMPLE, which is why the fixture rule is
stated rather than assumed. Writing the A8 analysis into the master task list
made `bench/logs/x/y.json` come back classified NOTE -- because a note now
mentioned it. A classifier that reclassifies a path by being written about is
measuring the writing. A fixture stays a fixture however much prose discusses it.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "orphan_figures_2026-09-10.py"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("orphan_cls", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["orphan_cls"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheClassesAreDistinguished:
    def test_an_elided_path_is_not_a_citation(self, m):
        for p in ("bench/logs/exp30_x/round_XX.json",
                  "bench/logs/exp42_.../round7.json",
                  "bench/logs/run_<id>/report.json"):
            assert m.classify_citation(p) == "ELIDED", p

    def test_a_fixture_stays_a_fixture_when_prose_discusses_it(self, m):
        """THE SELF-REFERENCE THE CENSUS CREATED. This exact path is a fixture
        in a test AND is now named in the master task list's A8 paragraph."""
        assert m.classify_citation("bench/logs/x/y.json") == "TESTS ONLY"

    def test_a_real_panel_record_is_a_note_citation(self, m):
        """NAMED INDIRECTLY, because naming it here would reclassify it.

        The first version of this test wrote the path as a literal -- and this
        file is a TEST, so the classifier then correctly returned TESTS ONLY and
        the test failed. The control had done the very thing the classifier
        exists to resist: a path gets reclassified by being written about. It is
        the same self-reference that made `bench/logs/x/y.json` come back NOTE
        when the A8 analysis was written into the task list, and it arrived
        inside the guard for it.

        So the path is FOUND rather than typed: the first untracked cited path
        that a note cites and no test mentions.
        """
        _cited, untracked = m.untracked_cited_paths()
        notes = [u for u in untracked if m.classify_citation(u) == "NOTE"]
        assert notes, "no untracked path is cited by a note; the scan has broken"
        assert all("panel" in n or "confer" in n or "/" in n for n in notes[:1])

    def test_an_unmentioned_path_is_uncited(self, m, tmp_path):
        """ALSO NAMED INDIRECTLY. A literal here would be mentioned by this
        file, so `git grep` would find it and UNCITED could never be returned --
        a control that cannot observe its own subject."""
        import uuid
        made_up = "bench/logs/" + uuid.uuid4().hex + "/x.json"
        assert m.classify_citation(made_up) == "UNCITED"


class TestThePopulationIsReported:
    def test_the_note_cited_count_is_the_smaller_one(self, m):
        cited, untracked = m.untracked_cited_paths()
        notes = [u for u in untracked if m.classify_citation(u) == "NOTE"]
        assert notes, "no note-cited untracked paths at all; the scan has broken"
        assert len(notes) < len(untracked), (
            "every untracked path is note-cited, so the classification is "
            "distinguishing nothing and the figure is unchanged from before")

    def test_the_producer_prints_the_breakdown(self):
        import subprocess
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-400:]
        for phrase in ("BY WHAT MENTIONS THEM", "a RULING is about",
                       "ELIDED", "TESTS ONLY"):
            assert phrase in r.stdout, f"the producer no longer reports: {phrase}"


class TestTheCheckIsNotVacuous:
    def test_all_four_classes_occur_in_the_live_corpus(self, m):
        """ANTI-VACUITY. A classifier that returned one label for everything
        would satisfy every assertion above that names only that label."""
        import collections
        _cited, untracked = m.untracked_cited_paths()
        kinds = collections.Counter(m.classify_citation(u) for u in untracked)
        assert len(kinds) >= 3, (
            f"only {sorted(kinds)} occur; the classification has collapsed")
        assert kinds["NOTE"] and kinds["TESTS ONLY"] and kinds["ELIDED"]
