"""Task V4: every figure on the task list must name a script that exists.

`measured-rate-travels-with-its-script` is a founder ruling this project quotes
constantly and has broken repeatedly. The reviewers named 5 entries; a mechanical
sweep on 2026-09-10 found 4 still carrying a percentage or p-value with no live
script -- 4 of 18, 22.2222%, Wilson [9.0009%, 45.2146%]. After the repair: 0 of
18, Wilson [0.0000%, 17.5879%].

WHAT THE REPAIR ACTUALLY WAS, per entry, because they were not the same problem.

  0.2 cited `change_point()` -- a FUNCTION -- and never named the file it lives
      in, so a reader could not find it. Repaired by naming the script.
  6.1 had no producer at all, and the figure HAD DRIFTED: "23 of 41" measured
      2026-09-09 is 24 of 42 today across every run directory, because the
      archive grows. A typed figure over a growing corpus is not merely
      unverifiable; it is guaranteed to go stale.
  A8 had no producer. The new one measures a DIFFERENT population from the
      entry's and says so rather than pretending to reproduce 4.65%.
  A19 had no producer. The new one CONFIRMS the claim over a smaller population,
      with a wider interval, which is the honest report of a smaller sample.

A DEFECT IN MY OWN PRODUCER, caught before it became the answer: the A8 extractor
first matched anything after `bench/logs/` and swept in `bench/logs/--help` and
bare directory names, giving 206 of 290 -- a figure about the extractor rather
than the corpus. Requiring a real file extension gives 42 of 125.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
PRODUCER = ROOT / "scripts" / "orphan_figures_2026-09-10.py"

FIGURE = re.compile(r"\b\d{1,3}\.\d+\s*%|\bp\s*=\s*[\d.]+e?-?\d*")
SCRIPT = re.compile(r"(scripts/[\w./-]+\.py|bench/tests/[\w./-]+\.py)")


def _entries():
    sys.path.insert(0, str(ROOT / "scripts"))
    import task_list_markers as tlm
    return tlm.parse_entries(LIST)


class TestEveryFigureHasAProducer:
    def test_no_entry_cites_a_figure_without_a_live_script(self):
        orphans = []
        for e in _entries():
            if not FIGURE.findall(e.text):
                continue
            live = [s for s in SCRIPT.findall(e.text) if (ROOT / s).is_file()]
            if not live:
                orphans.append(e.ident)
        assert not orphans, (
            "these entries carry a percentage or p-value and name no script that "
            f"exists: {orphans}. measured-rate-travels-with-its-script.")

    def test_the_sweep_is_not_vacuous(self):
        """If no entry carried a figure, the test above would pass on nothing."""
        n = sum(1 for e in _entries() if FIGURE.findall(e.text))
        assert n >= 10, f"only {n} entries carry a figure; the sweep is too thin"


class TestTheProducerRuns:
    def test_it_produces_all_three_figures(self):
        r = subprocess.run([sys.executable, str(PRODUCER)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stdout[-600:] + r.stderr[-400:]
        for marker in ("ENTRY 6.1", "ENTRY A8", "ENTRY A19"):
            assert marker in r.stdout, f"{marker} is not produced"

    def test_it_states_where_its_population_differs_from_the_entry(self):
        r = subprocess.run([sys.executable, str(PRODUCER)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert "different population" in r.stdout, (
            "the A8 figure no longer says its denominator differs from the "
            "entry's, so the 2 could be quoted against each other")
        assert "guaranteed to drift" in r.stdout or "go stale" in r.stdout


class TestTheExtractorIsNotTheMeasurement:
    def test_a_non_file_path_is_not_counted(self):
        """The defect that gave 206 of 290."""
        spec = importlib.util.spec_from_file_location("orphan", PRODUCER)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert m._LOOKS_LIKE_A_FILE.search("bench/logs/x/y.json")
        for junk in ("bench/logs/--help", "bench/logs/.", "bench/logs/analysis/"):
            assert not m._LOOKS_LIKE_A_FILE.search(junk), junk

    def test_the_cited_count_is_plausible(self):
        spec = importlib.util.spec_from_file_location("orphan", PRODUCER)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        cited, untracked = m.untracked_cited_paths()
        assert 20 < len(cited) < 1000, len(cited)
        assert len(untracked) <= len(cited)
