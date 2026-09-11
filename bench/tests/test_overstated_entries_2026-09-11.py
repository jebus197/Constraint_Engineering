"""Task V2: the 11 entries a reviewer called overstated, checked rather than believed.

AN ENTRY THAT SAYS ANOTHER ENTRY IS WRONG IS ITSELF A CLAIM. This project's record
holds several reviewer claims that did not survive measurement: the "80.95%
incidental" proxy that had selected genuine clinical constraints, the "silent
failure" in a function that warns, the 55.56% harm rate that conflated *absent*
with *deleted* and was 20.00%. So V2's list was measured, not acted on.

WHAT THE SWEEP FOUND, 2026-09-11.

  - The figure-with-no-producer class (1.1, 5.1, 6.2, 6.5, M1) was closed by task
    V4 the day before: 0 of 18 entries now carry a figure with no live script.
  - 6.4, 6.7, 7.2 and 8.1 already carry dated CORRECTED paragraphs answering the
    reviewer in place. 6.3 was a live regression, already fixed at `25e5b34`.
  - 4.2's defect was real and unrepaired: it said "Status COMMITTED" and nothing
    else, while the repaired artefact is a file in CC1's PRIVATE memory
    directory that this repository does not carry and cannot --
    `git log --all` returns 0 commits touching it across the full history.
  - AND THE SWEEP FOUND A 12TH THE REVIEWER DID NOT NAME: 7.3, the same shape.
    That is why it was mechanised instead of worked off the list. The project's
    own lesson is [[feedback_check_the_whole_set]] -- a universal asserted after
    checking one member.

A POPULATION ERROR IN MY OWN INSTRUMENT, caught before it became the answer. The
first version measured over `Entry.text`, which is the entry LINE only -- an
entry's continuation paragraphs are separate lines that `parse_entries` does not
carry -- and reported "25 of 67 DONE entries name no artefact at all", 37.3134%,
Wilson [26.7182%, 49.2846%]. Read over the whole BLOCK, and counting the marker's
own `evidence:` field, the figure is 0 of 67, Wilson [0.0000%, 5.4226%]. The
wrong number was the alarming one.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import task_list_markers as tlm  # noqa: E402

SCRIPT = ROOT / "scripts" / "overstated_entries_2026-09-11.py"
LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: V2's own list, so a change to the entry cannot quietly shrink what was checked.
NAMED = ("6.3", "7.2", "6.7", "6.4", "4.2", "8.1", "1.1", "5.1", "6.2", "6.5", "M1")


def _mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("overstated", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestEveryNamedEntryStillExists:
    def test_all_eleven_are_present(self):
        ids = {e.ident for e in tlm.parse_entries(LIST)}
        missing = [i for i in NAMED if i not in ids]
        assert not missing, f"V2 names entries that no longer exist: {missing}"

    def test_the_script_agrees_with_this_list(self):
        assert set(_mod().CLAIMS) == set(NAMED), (
            "the script's list and this test's list have drifted apart; 2 "
            "representations of one truth with no comparator")


class TestNoCommittedEntryHidesAPrivateArtefact:
    def test_none_remain(self):
        """4.2 and 7.3 were the 2 instances; both now say what is committed HERE."""
        m = _mod()
        by_id = m.entries()
        bad = m.check_committed_names_a_tracked_artefact(by_id, m.blocks(by_id))
        assert not bad, (
            f"these entries claim COMMITTED while their artefact lives only in "
            f"the private memory directory, and do not say so: {bad}")

    def test_the_check_can_still_fire(self, tmp_path):
        """POSITIVE CONTROL. Narrowing a check is how a check stops checking."""
        m = _mod()
        by_id = m.entries()
        fake = dict(m.blocks(by_id))
        victim = next(i for i, e in by_id.items() if e.status == "COMMITTED")
        fake[victim] = "**X** recorded as `memory/feedback_x.md` and indexed."
        bad = m.check_committed_names_a_tracked_artefact(by_id, fake)
        assert [b[0] for b in bad] == [victim], bad

    def test_the_two_repaired_entries_say_what_is_committed_here(self):
        blocks = _mod().blocks(_mod().entries())
        for ident in ("4.2", "7.3"):
            assert "does not carry" in blocks[ident], (
                f"{ident} no longer states that this repository does not hold "
                f"the artefact, so COMMITTED reads as a promise it cannot keep")


class TestTheFigureClassStaysClosed:
    def test_no_named_entry_carries_a_figure_without_a_script(self):
        m = _mod()
        orphans = m.check_figures_have_producers(m.entries())
        assert not orphans, (
            f"the V4 repair has regressed; these entries carry a percentage or "
            f"p-value and name no script that exists: {orphans}")


class TestTheBlockReaderIsUsedNotTheLine:
    def test_a_blocks_entry_is_longer_than_its_line(self):
        """THE POPULATION ERROR, pinned. If `blocks` ever returned the entry line
        again, "25 of 67" would come back and it is the alarming direction."""
        m = _mod()
        by_id = m.entries()
        blocks = m.blocks(by_id)
        longer = sum(1 for i, e in by_id.items() if len(blocks[i]) > len(e.text))
        assert longer >= 30, (
            f"only {longer} entries have a block longer than their first line; "
            f"`blocks` is probably returning lines again")

    def test_every_done_entry_names_evidence(self):
        done = [e for e in tlm.parse_entries(LIST)
                if e.state == "DONE" and e.status in ("COMMITTED", "ENABLED")]
        assert len(done) >= 50, len(done)
        bare = [e.ident for e in done if not e.evidence]
        assert not bare, bare


class TestTheScriptRuns:
    def test_it_exits_zero_and_reports_every_section(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-400:]
        for heading in ("the 11 named by V2", "NOT tracked by git",
                        "no live producing script", "does not carry"):
            assert heading in r.stdout, f"the script no longer reports: {heading}"

    def test_it_says_an_unchecked_claim_is_not_a_refuted_one(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert "UNCHECKED, not refuted" in r.stdout, (
            "the script no longer states its own boundary, so a reader could "
            "take a silent section for a cleared one")
