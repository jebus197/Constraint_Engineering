"""Task V4: every figure on the task list must name a script that exists.

`measured-rate-travels-with-its-script` is a founder ruling this project quotes
constantly and has broken repeatedly. The reviewers named 5 entries; a mechanical
sweep on 2026-09-10 found 4 entry HEADING LINES still carrying a percentage or
p-value with no live script -- 4 of 18 heading lines, 22.2222%, Wilson [9.0009%,
45.2146%]. After the repair: 0 of 18 heading lines, Wilson [0.0000%, 17.5879%].

THE 18 WERE HEADING LINES, NOT ENTRIES (panel round 16, 2026-09-17).
`parse_entries` sets `Entry.text` to the heading line, and this guard read only
that. Over whole entry blocks the same list held 38 figure-carrying entries at
90cabb3, the repair commit, and 1 of them, W1, still named no script in the
paragraph carrying its p-value. `scripts/task_list_figure_population_2026-09-17.py`
prints all of these at any revision (`--rev 90cabb3^`, `--rev 90cabb3`) and is now
the one definition of the sweep this file runs, over blocks.

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

POPULATION = ROOT / "scripts" / "task_list_figure_population_2026-09-17.py"

#: Entries whose figures are backed ONLY by a script named in their marker's
#: `evidence:` field, measured at 989f32f on 2026-09-17 by
#: `task_list_figure_population_2026-09-17.py` ("blocks without markers"). The
#: marker-inclusive sweep passes them, because it tests co-occurrence: a
#: `bench/tests/` path in the marker satisfies it whatever the figure is. The
#: stronger rule, excluding marker lines, would report these 6 today, and each
#: needs its producing script named in its body. Until then the set may shrink and
#: may not grow.
# SHRUNK 2026-09-17, as the ratchet requires: P3, R3 and A6 gained a producing
# script path in their own bodies when panel round 16's corrections landed, so
# they no longer rest on the marker's evidence field alone.
EVIDENCE_FIELD_ONLY = frozenset({"R4", "2.1", "7.2"})

#: An invented figure with no script beside it, for the positive controls.
_INJECTED = "An invented measurement, p = 0.01234567, with nothing that produced it."


def _load_population():
    spec = importlib.util.spec_from_file_location("figure_population", POPULATION)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _exists(rel: str) -> bool:
    return (ROOT / rel).is_file()


def _sweep(text: str, unit: str) -> tuple[list[str], list[str]]:
    return _load_population().sweep(text, _exists, unit)


def _with_witness(text: str, ident: str, evidence: str | None) -> str:
    """The real list with 1 SYNTHETIC entry inserted before its first entry: a
    heading with no figure and no script, a marker (with `evidence` if given),
    then `_INJECTED` in the body.

    THE WITNESS IS BUILT, NOT FOUND IN THE LIVE LIST. On 2026-09-17 a sibling
    guard failed because the last live entry of the kind it needed gained
    evidence; a property of the SWEEP must not be read off the list's contents."""
    tlm = _load_population()._tlm()
    lines = text.splitlines()
    assert not any(tlm._is_entry(ln) and tlm.ENTRY.match(ln).group(1) == ident
                   for ln in lines), f"{ident} already exists in the list"
    first = next(i for i, ln in enumerate(lines) if tlm._is_entry(ln))
    field = f" | evidence: {evidence}" if evidence else ""
    witness = [f"**{ident}. A synthetic entry that names no script in its body.**",
               f"<!-- task: {ident} | state: OPEN | status: PROPOSED{field} -->",
               _INJECTED, ""]
    return "\n".join(lines[:first] + witness + lines[first:]) + "\n"


class TestEveryFigureHasAProducer:
    """Runs over ENTRY BLOCKS, heading to next heading, marker line included.

    Until 2026-09-17 this read `Entry.text`, the heading line only, and an
    invented p-value injected into an entry's body passed it. The sweep itself
    lives in `scripts/task_list_figure_population_2026-09-17.py`, so the guard
    and the producer of its figures are 1 definition. WHAT IT CHECKS IS
    CO-OCCURRENCE OF AN EXISTING SCRIPT PATH, NOT PRODUCTION."""

    def test_no_entry_cites_a_figure_without_a_live_script(self):
        text = LIST.read_text(encoding="utf-8")
        _, orphans = _sweep(text, "entry blocks")
        assert not orphans, (
            "these entries carry a percentage or p-value somewhere in their block "
            f"and name no script that exists: {orphans}. "
            "measured-rate-travels-with-its-script.")
        # THE HEADING-LINE RULE IS KEPT, not replaced. A block is a superset of
        # its heading, so a heading figure whose script is named only further
        # down passes the block sweep; the original guard required it on the
        # heading line itself, and that stricter case must not be lost.
        _, heading_orphans = _sweep(text, "heading lines")
        assert not heading_orphans, (
            "these entries carry a figure on their HEADING LINE with no existing "
            f"script on that line: {heading_orphans}")

    def test_entries_resting_on_the_evidence_field_alone_do_not_grow(self):
        text = LIST.read_text(encoding="utf-8")
        _, with_markers = _sweep(text, "entry blocks")
        _, without = _sweep(text, "blocks without markers")
        only_field = set(without) - set(with_markers)
        new = sorted(only_field - EVIDENCE_FIELD_ONLY)
        stale = sorted(EVIDENCE_FIELD_ONLY - only_field)
        assert not new, (
            f"{new} carry a figure whose only script path is the marker's "
            f"evidence field. Name the script that PRINTS the figure in the "
            f"entry's body.")
        assert not stale, (
            f"{stale} no longer rest on the evidence field alone; remove them "
            f"from EVIDENCE_FIELD_ONLY so the ratchet does not keep their slack")

    def test_the_sweep_is_not_vacuous(self):
        """If no entry carried a figure, the tests above would pass on nothing;
        and a regression to heading lines must go red, not quietly shrink."""
        text = LIST.read_text(encoding="utf-8")
        blocks, _ = _sweep(text, "entry blocks")
        headings, _ = _sweep(text, "heading lines")
        assert len(blocks) >= 40, f"only {len(blocks)} entry blocks carry a figure"
        assert len(blocks) > len(headings), (
            f"blocks ({len(blocks)}) no larger than heading lines "
            f"({len(headings)}): the sweep has regressed to heading lines")

    def test_a_figure_injected_into_a_body_is_reported(self):
        """POSITIVE CONTROL. The heading-line guard passed exactly this."""
        injected = _with_witness(LIST.read_text(encoding="utf-8"), "QQ99", None)
        _, orphans = _sweep(injected, "entry blocks")
        assert "QQ99" in orphans, (
            f"an unproduced p-value in an entry's body was not reported: {orphans}")
        carrying, heading_orphans = _sweep(injected, "heading lines")
        assert "QQ99" not in carrying and "QQ99" not in heading_orphans, (
            "the heading-line sweep saw a body figure; the control no longer "
            "separates the 2 populations")

    def test_the_evidence_field_masks_a_body_figure_and_the_ratchet_sees_it(self):
        """The stated limit, executed: in an entry whose marker names existing
        evidence, a body figure with no script passes the block sweep and shows
        up only when marker lines are excluded, which is what the ratchet reads."""
        evidence = "bench/tests/test_task_list_figures_have_producers_2026-09-10.py"
        assert _exists(evidence)
        injected = _with_witness(LIST.read_text(encoding="utf-8"), "QQ98", evidence)
        _, with_markers = _sweep(injected, "entry blocks")
        _, without = _sweep(injected, "blocks without markers")
        assert "QQ98" not in with_markers, with_markers
        assert "QQ98" in without, without


class TestThePopulationScriptRuns:
    """The producer of the V4 correction's figures, executed at the revisions it
    is cited for."""

    @staticmethod
    def _run(*args):
        return subprocess.run([sys.executable, str(POPULATION), *args], cwd=ROOT,
                              capture_output=True, text=True, timeout=300)

    def test_it_answers_help_and_refuses_an_unknown_revision(self):
        h = self._run("--help")
        assert h.returncode == 0 and h.stdout.startswith("usage:"), h
        assert "carry a figure" not in h.stdout
        bad = self._run("--rev", "no-such-revision-2026-09-17")
        assert bad.returncode == 2 and "REFUSING" in bad.stderr, bad

    def test_it_reproduces_the_entrys_own_figure_before_the_repair(self):
        if subprocess.run(["git", "cat-file", "-e", "90cabb3^:experimental_notes/"
                           "CDSFL_MASTER_TASK_LIST.md"], cwd=ROOT,
                          capture_output=True).returncode != 0:
            pytest.skip("revision 90cabb3^ is not in this clone")
        r = self._run("--rev", "90cabb3^")
        assert r.returncode == 0, r.stderr
        assert re.search(r"heading lines\s*: 18 carry a figure, 4 name no existing "
                         r"script \['0\.2', '6\.1', 'A8', 'A19'\] = 22\.2222%, "
                         r"Wilson \[9\.0009%, 45\.2146%\]", r.stdout), r.stdout
        assert re.search(r"entry blocks\s*: 38 carry a figure, 3 name no existing "
                         r"script \['A8', 'A19', 'W1'\]", r.stdout), r.stdout

    def test_the_repair_left_w1_unseen(self):
        if subprocess.run(["git", "cat-file", "-e", "90cabb3:experimental_notes/"
                           "CDSFL_MASTER_TASK_LIST.md"], cwd=ROOT,
                          capture_output=True).returncode != 0:
            pytest.skip("revision 90cabb3 is not in this clone")
        r = self._run("--rev", "90cabb3")
        assert r.returncode == 0, r.stderr
        assert re.search(r"heading lines\s*: 18 carry a figure, 0 name no existing "
                         r"script \[\]", r.stdout), r.stdout
        assert re.search(r"entry blocks\s*: 38 carry a figure, 1 name no existing "
                         r"script \['W1'\]", r.stdout), r.stdout


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
