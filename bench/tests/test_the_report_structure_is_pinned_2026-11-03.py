"""The morning report's 3 structural repairs of 2026-11-03, pinned.

WHY THIS EXISTS, AND IT IS THE ADDITIVE STANDARD APPLIED TO MY OWN FIXES. 3
changes were made to `scripts/morning_report_build_2026-10-12.py` on 2026-11-03
and **nothing in the suite reached any of them**, measured by grep over
`bench/tests/`: revert all 3 and the suite stays green. That is the
addition-nothing-reaches half of the standard, and it is the 2nd time in 1 night
the same rule caught work written while citing it -- the 1st being 5 producers
run by no test.

THE 3 REPAIRS.

  1. THE REGION BALANCE, and this is the one that matters most. The report
     carried 4 `verbatim-begin` markers against 5 `verbatim-end` -- 1 stray
     close, which the note standard calls malformed. His `pf` of 2026-11-01
     stopped printing the parked headings verbatim and correctly dropped the
     OPENING marker so Rule 27 would bind that prose, leaving the close behind.
     The report had been emitting malformed output from then until 2026-11-03,
     and NOTHING caught it: the file is gitignored so the pre-commit note
     ratchet never sees it, and the test that would catch it is not among the
     board's 120 guard files. A repair that removes an opening marker must
     remove its close in the same edit.

  2. AN EMPTY REGION IS NOT EMITTED. With 0 explanations owed the markers were
     written around nothing, costing 4 lines and leaving a region that exempts
     no text while still having to be accounted for in the balance.

  3. SECTION 4 FOLDS SETTLED BUSINESS AND NAMES WHAT REMAINS. Under a heading
     reading "Explanations owed -- 0" it spent 33 of 49 lines enumerating 11
     struck questions, 9 of them repeating an identical retirement sentence.
     That is the re-presenting of settled business his 2026-11-01 ruling names,
     applied to the parked section and never to this one. THE FOLD KEEPS WHAT
     MATTERS: collapsing all 11 was the plan and would have hidden 2 live items,
     because grouping by what each leaves behind gives 3 distinct values and 2
     declare REMAINING WORK. So the nothing-remains group is COUNTED and every
     other item is NAMED.

WHAT THIS DOES NOT DO. It does not assert the report's LENGTH. Both copies are
over Rule 10's ceiling and that is a structural question for the founder -- the
ceiling was written for a note and this is a generated digest whose length is
driven by how many decisions are open. `test_the_morning_report_is_generated`
already asserts the limits and already fails on them; duplicating that here
would be a 2nd declaration of 1 fact.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
MD = REPO / "experimental_notes"
GEN = REPO / "scripts" / "morning_report_build_2026-10-12.py"


@pytest.fixture(scope="module")
def report() -> str:
    """The newest generated report on disk, or a skip.

    IT IS GITIGNORED ON PURPOSE AND THAT IS WHY THIS SKIPS RATHER THAN FAILS.
    A test whose verdict depends on an untracked file being present would be
    green in a fresh clone and red only on a machine that had generated one,
    which is the probe-location failure this project records. So the structural
    assertions below run when a report exists and the SOURCE assertions, which
    need no artefact, always run.
    """
    cands = sorted(MD.glob("Morning_Report_*_GENERATED.md"))
    if not cands:
        pytest.skip("no generated report in this checkout; the source tests "
                    "below still run")
    return cands[-1].read_text(errors="replace")


class TestTheRegionsBalance:
    def test_begin_and_end_markers_match(self, report):
        """THE DEFECT OF 1 NOVEMBER TO 3 NOVEMBER, pinned."""
        b = report.count("verbatim-begin")
        e = report.count("verbatim-end")
        assert b == e, (
            f"{b} verbatim-begin against {e} verbatim-end. A stray close is "
            f"malformed under the note standard, and an unclosed open exempts "
            f"every paragraph after it from Rule 27.")

    def test_the_linters_own_region_state_is_clean(self, report):
        """Asserted with the linter's OWN predicate, not a recount of markers,
        so a tally that balances while a region is open still fails."""
        sys.path.insert(0, str(REPO / "scripts"))
        spec = importlib.util.spec_from_file_location(
            "_nvl_struct", REPO / "scripts" / "note_vagueness_lint.py")
        nvl = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nvl)
        st = nvl.region_state(report)
        assert not st["unclosed"], "a verbatim region is left open"
        assert not st["stray_closes"], (
            f"{st['stray_closes']} stray close(s); this is exactly the shape "
            f"that went unnoticed from 2026-11-01")
        assert st["opens"] == st["closes"]

    def test_no_region_is_emitted_empty(self, report):
        """An empty region exempts nothing and still has to be accounted for."""
        empties = re.findall(
            r"<!-- verbatim-begin:[^>]*-->\s*<!-- verbatim-end -->", report)
        assert not empties, (
            f"{len(empties)} verbatim region(s) are emitted around no content")


class TestSectionFourFoldsSettledBusinessOnly:
    def test_the_generator_counts_the_struck_and_names_the_rest(self):
        """SOURCE-LEVEL, so it holds with no artefact present.

        This is deliberately an assertion about the generator rather than its
        output: with 0 struck questions the output would show neither branch,
        and a test that only read the artefact would pass vacuously.
        """
        src = GEN.read_text(errors="replace")
        assert "_struck = [r for r in superseded" in src, (
            "the fold is gone; section 4 would enumerate every struck question "
            "again, which is the re-presenting of settled business his ruling "
            "of 2026-11-01 names")
        assert "struck rather than deferred" in src, (
            "the counted group no longer states that it was struck")
        assert "leave something behind" in src, (
            "the fold no longer NAMES the items that leave work behind; "
            "collapsing all of them would hide live work behind a count")

    def test_the_owed_region_is_conditional(self):
        src = GEN.read_text(errors="replace")
        i = src.index("the founder's own words")
        window = src[max(0, i - 400):i]
        assert "if owed:" in window, (
            "the owed verbatim region is emitted unconditionally again, so a "
            "report with 0 explanations owed carries a region around nothing")

    def test_the_fold_keeps_both_branches_reachable(self):
        """ANTI-VACUITY. A fold that counted everything would satisfy the
        assertions above while hiding live work, so both branches must exist."""
        src = GEN.read_text(errors="replace")
        assert "if _struck:" in src and "if _live_sup:" in src, (
            "one branch of the fold is missing; the count and the naming must "
            "both be reachable")
