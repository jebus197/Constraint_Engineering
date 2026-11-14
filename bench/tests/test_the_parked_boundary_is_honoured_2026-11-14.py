"""The parked file's SETTLED boundary must stop the live reader, and must fail OPEN.

★ WHAT WAS WRONG. `parked_items()` in `scripts/morning_report_build_2026-10-12.py`
collected every `## ` heading in `experimental_notes/PARKED_FOR_THE_FOUNDER.md`
with no regard for the file's own h1 boundary, `# Settled - kept for the record,
not for his attention`. Measured 2026-11-13 under B181, the entry on
`parked_items()` being blind to numerically-identified entries: 38 headings
above the line and 38 below, and the reader took all 76.

★ B181 DESCRIBED THIS REPAIR AS PART OF A COMPOSED FIX ALREADY IN PLACE. It was
not: only the identifier widening had shipped. The entry also told a reader to
run a `--measure` flag that does not exist. Both were found by looking.

★ FAILING OPEN IS THE DESIGNED BEHAVIOUR, NOT AN OVERSIGHT. If the boundary
heading is renamed, no match is found and EVERY heading is returned. That
over-reports what needs his attention rather than hiding something from him,
which is the direction `parked_items` already takes when it cannot parse an
identifier, and the direction this project had to restore once after a
suppression removed live questions from his list.

★ AND THE COMPOSITION IS NOT JUSTIFIED, which this file does not assert but
which is why the widening is still here. Measured by
`scripts/does_the_parked_composition_beat_either_half_2026-11-14.py`: with both
repairs on and with the boundary alone, the filter returns the SAME 34 headings.
The boundary subsumes the widening on today's corpus. The widening is KEPT
because tying is not dominating and the removal clause needs dominance.

EXECUTES the reader. It does not read its source text.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"


def _mrb():
    spec = importlib.util.spec_from_file_location(
        "mrb_parked_guard", REPO / "scripts" / "morning_report_build_2026-10-12.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["mrb_parked_guard"] = m
    spec.loader.exec_module(m)
    return m


M = _mrb()

ABOVE = "## live one\n\nbody\n\n## live two\n\nbody\n"
BOUNDARY = "# Settled — kept for the record, not for his attention (2)\n"
BELOW = "\n## settled one\n\nbody\n\n## settled two\n\nbody\n"


def test_the_reader_stops_at_the_settled_boundary():
    assert M._parked_headings(ABOVE + BOUNDARY + BELOW) == ["live one", "live two"]


def test_everything_below_the_boundary_is_excluded():
    got = M._parked_headings(ABOVE + BOUNDARY + BELOW)
    assert "settled one" not in got and "settled two" not in got


def test_it_fails_OPEN_when_the_boundary_heading_is_renamed():
    """The load-bearing one: a renamed boundary must over-report, never hide."""
    renamed = BOUNDARY.replace("Settled", "Archived")
    got = M._parked_headings(ABOVE + renamed + BELOW)
    assert got == ["live one", "live two", "settled one", "settled two"], (
        "a renamed boundary silently hid headings from him; the reader must "
        "fail OPEN, because over-reporting is visible to him and omission is not")


def test_it_fails_OPEN_when_there_is_no_boundary_at_all():
    assert M._parked_headings(ABOVE + BELOW.lstrip("\n")) == [
        "live one", "live two", "settled one", "settled two"]


def test_the_boundary_match_is_case_insensitive_and_count_insensitive():
    for variant in ("# settled - whatever\n", "# SETTLED (99)\n",
                    "# Settled — kept for the record, not for his attention (12345)\n"):
        assert M._parked_headings(ABOVE + variant + BELOW) == ["live one", "live two"], variant


def test_a_level_2_settled_heading_is_an_ITEM_not_the_boundary():
    """`## Settled ...` is a parked item whose subject is settlement, not the line."""
    got = M._parked_headings("## Settled the question of X\n\nbody\n" + BOUNDARY + BELOW)
    assert got == ["Settled the question of X"]


def test_only_level_2_headings_are_collected():
    got = M._parked_headings("### deeper\n\n## real\n\n#### deepest\n")
    assert got == ["real"]


def test_the_live_file_has_a_boundary_and_the_reader_uses_it():
    """NON-VACUITY on the real corpus: if the live file lost its boundary, the
    tests above would still pass on fixtures while the report regressed."""
    text = PARKED.read_text(encoding="utf-8")
    every = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
    live = M._parked_headings(text)
    assert len(live) < len(every), (
        f"the reader returned all {len(every)} headings, so the live file has no "
        f"recognised settled boundary and nothing is being excluded")
    assert live == every[:len(live)], "the live portion is not a prefix of the file"


def test_parked_items_is_a_subset_of_the_live_portion():
    """The identifier filter may only ever REMOVE from what the boundary allows."""
    live = set(M._parked_headings(PARKED.read_text(encoding="utf-8")))
    assert set(M.parked_items()) <= live
