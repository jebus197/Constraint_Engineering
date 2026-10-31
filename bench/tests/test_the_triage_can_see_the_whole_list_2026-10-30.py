#!/usr/bin/env python3
"""The blocker triage must be able to see every entry, not the first 114 of 186.

THE DEFECT, OBSERVED 2026-10-30 RATHER THAN PREDICTED. `blocker_triage.blocks_progress`
opened with `lines = lines[:end_of_entries(lines)]`. `end_of_entries` searches the
file from line 0 for the heading `# SUPPLEMENTARY LIST`, which sits at index 865 --
and 72 of the 186 entries begin AFTER it, every one carrying a real task marker,
including all 6 that were OPEN that day (B21, B22, C1, B41, B50, R1). So the
dependency scan answered "no entry declares a dependency on it; nothing is waiting"
for 6 entries it had never read. z3 returns `unsat` for "an entry at or beyond the
cut is scanned", so the loss was structural, not intermittent.

A SECOND CONSEQUENCE IN 5 OTHER CALL SITES. The idiom copied into each of them --
next entry's line, else `end_of_entries` -- INVERTS for the final entry, because
1403 > 865. R1's body came out as 0 characters where its true body is 5,967.

WHY IT WAS INVISIBLE FOR 6 WEEKS. The cut was correct when it was written on
2026-09-17: the supplementary section was then the LAST thing in the file, so
cutting at it stopped the final canonical entry absorbing it. Entries were
afterwards appended BEYOND that heading -- the first is B3, added 2026-10-14 --
and the boundary silently became an amputation.

THE REPAIR. `next_section_start(lines, after)` searches from the entry's own start
instead of from the file's, so the 2026-09-17 property is preserved exactly for an
entry before the sentinel while an entry after it gets the right answer.
`body_bounds` is the single definition of an entry's extent, replacing the idiom
that had been copied 6 times.

AND THE REPAIR UNMASKED A THIRD DEFECT, which is why the term filter is here too:
with the window corrected the scan reached the OPEN entries and reported ALL 6 as
blocking, on matches like `cross-verified`, `byte-identical` and `stand-in`. The
extractor's kebab alternative matches any hyphenated word, and 1,028 of 2,686
distinct terms across the 186 bodies were hyphenated English. Restricting the
kebab form to CLI flags takes the 6 back to 3, and those 3 read correctly.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

import blocker_triage as BT          # noqa: E402
import task_list_markers as TLM      # noqa: E402

LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


@pytest.fixture(scope="module")
def lines() -> list[str]:
    return LIST.read_text(encoding="utf-8").splitlines()


class TestThe2026_09_17_PropertyIsUnchanged:
    """The repair must not reopen the defect the boundary was built for."""

    def test_the_supplementary_section_is_still_outside_the_canonical_prefix(self, lines):
        prefix = "\n".join(lines[:TLM.end_of_entries(lines)])
        assert TLM.SUPPLEMENTARY not in prefix

    def test_end_of_entries_still_stops_at_the_sentinel(self):
        synthetic = ["**A1. x** y", "<!-- task: A1 | state: OPEN | status: PROPOSED -->",
                     TLM.SUPPLEMENTARY + " - 59 entries", "a row"]
        assert TLM.end_of_entries(synthetic) == 2

    def test_the_last_canonical_entry_does_not_absorb_the_section_heading(self, lines):
        """Sliced by `body_bounds`, not by the idiom it replaces."""
        starts = [i for i, l in enumerate(lines) if TLM._is_entry(l)]
        sentinel = TLM.end_of_entries(lines)
        before = [n for n, i in enumerate(starts) if i < sentinel]
        _, end = TLM.body_bounds(lines, starts, before[-1])
        assert end <= sentinel, (
            "the last entry of the canonical section runs past the supplementary "
            "heading again, which is the 2026-09-17 defect")


class TestTheBoundaryIsNowRelative:

    def test_an_origin_past_the_sentinel_reaches_the_end_of_the_file(self, lines):
        assert TLM.next_section_start(lines, TLM.end_of_entries(lines) + 1) == len(lines)

    def test_an_origin_before_the_sentinel_is_unchanged(self, lines):
        assert TLM.next_section_start(lines, 0) == TLM.end_of_entries(lines)

    def test_every_entry_in_the_live_list_has_a_non_empty_body(self):
        """R1's body was 0 characters. A slice that inverts must not recur."""
        lines = LIST.read_text(encoding="utf-8").splitlines()
        starts = [i for i, l in enumerate(lines) if TLM._is_entry(l)]
        empty = []
        for n, i in enumerate(starts):
            s, e = TLM.body_bounds(lines, starts, n)
            if e <= s:
                empty.append(TLM.ENTRY.match(lines[i]).group(1))
        assert empty == [], f"{len(empty)} entries slice to an empty body: {empty[:5]}"


class TestTheTriageReachesEntriesBeyondTheSentinel:
    """THE REGRESSION GUARD. Restoring the truncation must turn this red.

    ★ IT NOW USES A FIXTURE RATHER THAN THE LIVE LIST, repaired 2026-10-31, and
    the reason is the more interesting half.

    These tests probed `_RECORDING_RUNS`, a symbol that lived only in B50's
    entry past the sentinel, and asserted the triage reported it as blocking.
    They went red tonight. The cause is NOT truncation and it is not a defect
    in the triage: the founder ruled on B50, the ruling was carried out, the
    entry is DONE, and a DONE entry correctly declares no dependency. Measured
    at that moment: **0 of 625 symbols anywhere in the live list are reported
    as blocking -- 0 of 414 before the sentinel and 0 of 211 past it -- and the
    list carries 0 entries in state BLOCKED.** So nothing is blocking, which is
    a true and welcome statement about the project and a fatal one about a test
    that needs a blocker to exist.

    A REGRESSION GUARD MUST NOT DEPEND ON THE PROJECT HAVING A PROBLEM. The
    property under test is that the SCAN REACHES past the supplementary
    heading; whether the live list happens to contain a declared dependency is
    a separate and changing fact. The fixture below carries one on purpose, so
    the guard measures the scan. The live list is still exercised, by the
    symbol is still refused.

    THE PROBE'S SHAPE MATTERS AND COST A PASS TO FIND. The first fixture used
    `PastSentinelSymbol`, and the predicate answered "no distinctive term to
    match against the entries" -- it extracts an IDENTIFIER-shaped term from the
    item text, and CamelCase without underscores does not qualify. The original
    probe was `_RECORDING_RUNS`, so the shape was carried by the old literal and
    not by any stated requirement. Using an underscored, upper-case name keeps
    the fixture honest about what the predicate actually accepts.
    """

    #: ★ IMPORTED, NEVER TYPED. The first fixture hardcoded "# SUPPLEMENTARY"
    #: while the real sentinel is "# SUPPLEMENTARY LIST", so `next_section_start`
    #: never found it, the truncation did not bite on the fixture, and RESTORING
    #: THE DEFECT LEFT THIS FILE GREEN -- a guard that cannot catch the thing it
    #: was written for. Taking the string from its owner means a future change to
    #: the sentinel moves the fixture with it.
    SENTINEL = TLM.SUPPLEMENTARY

    @staticmethod
    def _fixture(tmp_path):
        """A minimal list: 1 entry BEFORE the sentinel, 1 declared-dependency
        entry AFTER it. If the scan truncates at the sentinel it cannot see the
        second, and the probe comes back False."""
        body = "\n".join([
            "# TASKS",
            "",
            "**Z1. An ordinary entry before the sentinel.** It mentions "
            "`_BEFORE_SENTINEL_SYMBOL` in passing.",
            "<!-- task: Z1 | state: DONE | status: COMMITTED -->",
            "",
            TLM.SUPPLEMENTARY,
            "",
            "**Z2. An entry that DECLARES a dependency, past the sentinel.** "
            "This entry is BLOCKED and cannot proceed until "
            "`_PAST_SENTINEL_SYMBOL` is settled; it waits on it.",
            "<!-- task: Z2 | state: BLOCKED | status: PROPOSED -->",
            "",
        ])
        p = tmp_path / "FIXTURE_TASK_LIST.md"
        p.write_text(body, encoding="utf-8")
        return p

    def test_the_fixture_itself_puts_the_entry_past_the_sentinel(self, tmp_path):
        """Or the 2 tests below prove nothing."""
        f = self._fixture(tmp_path)
        text = f.read_text(encoding="utf-8")
        i = text.index(self.SENTINEL)
        assert "_PAST_SENTINEL_SYMBOL" in text[i:]
        assert "_PAST_SENTINEL_SYMBOL" not in text[:i]

    def test_a_term_living_only_past_the_sentinel_is_still_found(self, tmp_path):
        f = self._fixture(tmp_path)
        probe = "A question about _PAST_SENTINEL_SYMBOL that must be settled."
        blocks, why = BT.blocks_progress(probe, tasks=f)
        assert blocks, (
            "a symbol that appears only in an entry BEYOND the supplementary "
            "heading was not found, so the scan is truncating the list again: "
            + why)

    def test_the_predicate_can_return_true_at_all(self, tmp_path):
        """Six identical False answers are what hid the defect. Discrimination
        first -- and now the discrimination does not depend on the live list
        having a blocker in it."""
        f = self._fixture(tmp_path)
        probe = "A question about _PAST_SENTINEL_SYMBOL that must be settled."
        assert BT.blocks_progress(probe, tasks=f)[0] is True

    def test_and_it_can_still_return_false(self, tmp_path):
        f = self._fixture(tmp_path)
        blocks, _ = BT.blocks_progress(
            "Zzqqxx_wibble_frobnicate, a symbol appearing nowhere.", tasks=f)
        assert blocks is False

    def test_the_live_list_is_still_exercised_and_refuses_an_absent_symbol(self):
        """The live list keeps a test, narrowed to what is true of it whatever
        the project's state: the predicate runs, and an absent symbol is
        refused."""
        blocks, why = BT.blocks_progress(
            "Zzqqxx_wibble_frobnicate, a symbol appearing nowhere.", tasks=LIST)
        assert blocks is False
        assert why, "the predicate gave no reason at all"


class TestHyphenatedEnglishIsNotAnIdentifier:

    @pytest.mark.parametrize("word", ["cross-verified", "Agresti-Coull",
                                      "BYTE-IDENTICAL", "stand-in", "AI-powered"])
    def test_ordinary_hyphenated_prose_is_rejected(self, word):
        assert BT._looks_like_an_identifier(word, "a body with no flag in it") is False

    @pytest.mark.parametrize("sym", ["_RECORDING_RUNS", "bench/routing.py",
                                     "exp53-control", "free_run1_directive_whole"])
    def test_real_symbols_are_kept(self, sym):
        assert BT._looks_like_an_identifier(sym, "x") is True

    def test_a_cli_flag_is_kept_by_its_own_dashes_not_by_shape(self):
        assert BT._looks_like_an_identifier("check-only", "run it with --check-only") is True
        assert BT._looks_like_an_identifier("check-only", "no flag here") is False


def test_body_bounds_is_the_only_definition_the_triage_uses():
    """EXECUTED, not grepped: the two agree on every entry of the live list."""
    lines = LIST.read_text(encoding="utf-8").splitlines()
    starts = [i for i, l in enumerate(lines) if TLM._is_entry(l)]
    for n in range(len(starts)):
        s, e = TLM.body_bounds(lines, starts, n)
        assert s < e
        assert e <= len(lines)
        nxt = starts[n + 1] if n + 1 < len(starts) else len(lines)
        assert e <= nxt, "a body overran the next entry's heading"
