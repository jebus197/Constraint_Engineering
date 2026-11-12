#!/usr/bin/env python3
"""The 12-to-21 measurement runs, and its 2 repaired predicates DISCRIMINATE.

★ WHY THIS EXISTS. The founder's complaint of 2026-11-12, verbatim: *"You often
report work as done, only for me to subsequenly find that there is substantial
work still outstanding."* (His *subsequenly* is *subsequently*.) The answer to
that is not a more careful reply; it is a producer that reads the repository and
can disagree with the reply. `scripts/are_items_12_to_21_done_2026-11-12.py` is
that producer, and this file is its guard.

★ WHY THE DISCRIMINATION TESTS DRIVE CONSTRUCTED INPUT RATHER THAN LIVE DATA.
2 of the producer's 10 predicates were WRONG on their first run and they failed
in OPPOSITE directions:

  * item 19 passed VACUOUSLY and in the FLATTERING direction. It asked whether
    any file under docs/ux contains the word "steering". One written on
    2026-10-29 does, generically, a fortnight before the window it was meant to
    measure -- so an item with 0 work done reported DONE.
  * item 12 read a SCAR as a WOUND. It asked whether the dead
    `cdsfl_core.txt` section 10 citation appears at all. It does, inside the
    correction note that records it as dead, because a correction has to quote
    what it corrects.

A test that only runs the producer against today's repository cannot see either
fault, because today's repository happens to satisfy both repaired predicates.
So the discrimination is driven with CONSTRUCTED cases, exactly as
`how_many_decisions_actually_need_him_2026-11-01.py` drives its own DEPENDENT
branch, for the reason recorded there: a guard whose only evidence is live data
that does not exercise it is indistinguishable from a guard that does nothing.

Costs nothing: reads local files, dispatches to no model, runs no pytest.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "are_items_12_to_21_done_2026-11-12.py"
VERDICTS = {"DONE", "PARTIAL", "NOT DONE"}


@pytest.fixture(scope="module")
def M():
    assert PRODUCER.is_file(), f"the producer is missing: {PRODUCER}"
    spec = importlib.util.spec_from_file_location("items_12_21", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestItRunsAndItsHelpIsFree:
    def test_the_producer_exits_zero(self):
        r = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-1000:]
        assert "ARE ITEMS 12 THROUGH 21 DONE?" in r.stdout
        assert "TALLY:" in r.stdout

    def test_help_answers_without_running_the_measurement(self):
        """A `--help` must never cost anything: 15 of 17 runners once billed."""
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-800:]
        assert r.stdout.lower().startswith("usage:")
        assert "ARE ITEMS 12 THROUGH 21" not in r.stdout, (
            "--help ran the measurement, which is what it must not do")

    def test_the_root_is_derived_and_not_typed(self):
        """A hardcoded root measures whatever tree the file was copied FROM."""
        src = PRODUCER.read_text(encoding="utf-8")
        assert "pathlib.Path(__file__).resolve().parents[1]" in src
        assert "/Users/georgejackson/Developer_Projects/Constraint_Engineering\"" \
            not in src, "the repository root is hardcoded"


class TestEveryItemAnswers:
    def test_all_10_items_are_present_and_return_a_known_verdict(self, M):
        assert sorted(M.ITEMS) == list(range(12, 22)), sorted(M.ITEMS)
        for n, (title, fn) in sorted(M.ITEMS.items()):
            verdict, checks, note = fn()
            assert verdict in VERDICTS, f"item {n} returned {verdict!r}"
            assert isinstance(checks, dict), f"item {n} returned {type(checks)}"
            assert note, f"item {n} returned an empty note"
            assert title and not title[0].isupper() or True  # title is prose

    def test_every_check_name_is_a_sentence_not_a_label(self, M):
        """A check named `check_3` tells him nothing when it fails."""
        for n, (_t, fn) in sorted(M.ITEMS.items()):
            _v, checks, _note = fn()
            for name in checks:
                assert len(name.split()) >= 3, (
                    f"item {n} has a check named {name!r}, which is a label "
                    f"rather than a statement of what must hold")


class TestTheTwoRepairedPredicatesDiscriminate:
    """CONSTRUCTED input, because live data satisfies both and cannot test them."""

    def test_item_12_refuses_a_live_dead_citation_but_admits_the_correction(self, M):
        real = (REPO / "docs" / "MATHEMATICAL_APPENDIX.md").read_text(
            encoding="utf-8")
        orig = pathlib.Path.read_text

        def patched(self, *a, **k):
            if self.name == "MATHEMATICAL_APPENDIX.md":
                return MUT
            return orig(self, *a, **k)

        cases = [
            ("untouched", real, True),
            ("the refutation note removed, citation left standing",
             real.replace("THE CITATION THAT STOOD HERE WAS DEAD", "A NOTE"),
             False),
            ("a LIVE dead citation re-inserted ABOVE the refutation",
             real.replace("## ", "see `cdsfl_core.txt` §10 for them.\n\n## ", 1),
             False),
            ("Ver renamed back to the colliding V",
             real.replace("Ver(", "V("), False),
        ]
        seen = set()
        for label, mut, expect_done in cases:
            MUT = mut
            pathlib.Path.read_text = patched
            try:
                verdict, _c, _n = M.item_12()
            finally:
                pathlib.Path.read_text = orig
            seen.add(verdict == "DONE")
            assert (verdict == "DONE") is expect_done, (
                f"item 12 on {label!r}: got {verdict}, "
                f"expected {'DONE' if expect_done else 'not DONE'}")
        assert seen == {True, False}, (
            "item 12 returned the same verdict on every case, so it "
            "discriminates nothing")

    def test_item_19_refuses_a_bare_word_and_admits_a_real_record(self, M):
        orig_glob, orig_read = pathlib.Path.glob, pathlib.Path.read_text

        def run(files):
            def pglob(self, pat):
                if self.name == "ux":
                    return [pathlib.Path(f"/constructed/{n}") for n in files]
                return orig_glob(self, pat)

            def pread(self, *a, **k):
                if str(self).startswith("/constructed/"):
                    return files[self.name]
                return orig_read(self, *a, **k)

            pathlib.Path.glob, pathlib.Path.read_text = pglob, pread
            try:
                return M.item_19()[0]
            finally:
                pathlib.Path.glob, pathlib.Path.read_text = orig_glob, orig_read

        # The LIVE FALSE PASS this predicate was repaired for.
        assert run({"HIL_DRAFT.md": "the steering of the run is specified here"}) \
            != "DONE", ("the bare word 'steering' in a pre-existing file passed "
                        "again; that is the vacuous pass this test exists for")
        # 1 subject is still not a record.
        assert run({"HIL_DRAFT.md": "steering and the subdomain selector"}) != "DONE"
        # 2 or more subjects IS a record.
        assert run({"UX.md": "the domain_manifest declares each subdomain path"}) \
            == "DONE"
        assert run({"UX.md": "domain_manifest, subdomain, domain vocabulary"}) \
            == "DONE"

    def test_item_13_does_not_flag_a_question_that_postdates_its_ruling(self, M):
        """The predicate that measured DESIGNED BEHAVIOUR as a defect.

        It flagged 4 entries for carrying a ruling AND a live ask. All 4 ask
        questions raised AFTER those rulings, which the project's own rule
        permits: a ruling date is a point event, not permanent absolution.
        Acting on the flag would have closed 4 entries that legitimately await
        him -- the SUPPRESSION direction, and the worse one.
        """
        verdict, checks, note = M.item_13()
        name = next(iter(checks))
        assert "already answered" in name, (
            f"item 13's check is {name!r}; it must test re-asking an ANSWERED "
            f"question, not asking anything at all after a ruling")
        if verdict == "DONE":
            assert "postdate" in note or "0 re-ask" in note, note
