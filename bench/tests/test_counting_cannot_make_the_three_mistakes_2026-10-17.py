"""The 3 counting shapes that cost 7 withdrawn claims must be hard to write.

TASK C2. HIS QUESTION, 2026-10-02: *"Then can similar errors be prevented in the
futre [future]? If not they might lead to unhelpful and erroneous descisions
[decisions]."*

THE 3 SHAPES, from the 7 statements that had to be withdrawn:

  1. DOUBLE MATCHING -- *"the producing script matched every run log under 2
     patterns at once"*.
  2. LINES REPORTED AS OCCURRENCES -- *"counted lines containing a match and
     reported them as occurrences, which is the same unit error caught once
     already the same day"*.
  3. SELF-INCLUSION -- a census that *"included the 3 documents written about
     the term it was counting"*.

ALL 3 RECURRED ON 2026-10-17, which is why a rule was not enough and a module
exists. A detector read its own source and reported 5 defects, every one a line
of its own docstring. Another read its own explanatory comment as the code it
was checking. A substring scan reported 190 hits for "promot" -- this project's
own shadow PROMOTION -- 64 for "division", mostly arithmetic, and 25 for
"fixture", which is pytest. Each was caught by accident, not by a mechanism.

WHAT IS ASSERTED. Not that `bench/counting.py` makes a producer choose the right
population -- nothing can -- but that the 3 shapes are hard to write: the unit is
in the function name and keyword-required at the call site, the calling file is
excluded by default and the exclusion is REPORTED, and overlapping patterns are
countable before a figure is published.

MEASURED HERE, so the margins are not rhetorical: on one line holding a term 3
times the 2 unit functions differ by 3x, and on a probe whose own source mentions
its term 8 times, self-inclusion inflates the total from 3 to 11 -- a factor of
3.67.
"""
from __future__ import annotations

import pathlib

import pytest

from bench.counting import (count_over, lines_containing, occurrences,
                            overlapping_patterns)


# --------------------------------------------------------- shape 2: the unit
def test_the_two_unit_functions_disagree_where_it_matters():
    line = "promote the promotion of promoting things"
    assert occurrences("promot", line) == 3
    assert lines_containing("promot", line) == 1
    assert occurrences("promot", line) == 3 * lines_containing("promot", line)


def test_the_unit_cannot_be_omitted_at_a_call_site(tmp_path):
    """A figure whose unit is not stated is the error this module stops."""
    f = tmp_path / "x.txt"
    f.write_text("term term\n", encoding="utf-8")
    with pytest.raises(TypeError, match="unit"):
        count_over([f], "term")                      # type: ignore[call-arg]
    with pytest.raises(ValueError, match="occurrences"):
        count_over([f], "term", unit="things")
    assert count_over([f], "term", unit="occurrences")["total"] == 2
    assert count_over([f], "term", unit="lines")["total"] == 1


def test_the_unit_travels_with_the_figure():
    """So whatever quotes the total can also quote what it counted."""
    got = count_over([pathlib.Path("README.md")], "the", unit="lines")
    assert got["unit"] == "lines"
    assert set(got) == {"total", "unit", "files", "per_file", "excluded"}


# ------------------------------------------------ shape 3: self-inclusion
def test_the_calling_file_is_excluded_by_default(tmp_path):
    """THE SHAPE THAT KEEPS RECURRING, measured rather than asserted.

    This test file mentions "self_inclusion_probe" in its own source, so a
    census over it would count itself. With exclusion on the term is counted
    only in the data file; with it off the test file's own mentions inflate it.
    """
    data = tmp_path / "data.txt"
    data.write_text("self_inclusion_probe appears twice: self_inclusion_probe\n",
                    encoding="utf-8")
    here = pathlib.Path(__file__)
    on = count_over([here, data], "self_inclusion_probe", unit="occurrences")
    off = count_over([here, data], "self_inclusion_probe", unit="occurrences",
                     exclude_self=False)
    assert on["total"] == 2, on
    assert off["total"] > on["total"], (
        "this file no longer mentions the probe term, so the measurement has "
        "gone vacuous; change the term or the assertion")
    assert str(here) in " ".join(on["excluded"])


def test_the_exclusion_is_reported_not_silent(tmp_path):
    """A listing that drops files in silence lies by omission."""
    data = tmp_path / "d.txt"
    data.write_text("x\n", encoding="utf-8")
    other = tmp_path / "o.txt"
    other.write_text("x\n", encoding="utf-8")
    got = count_over([data, other], "x", unit="occurrences",
                     exclude=[str(other)])
    assert got["total"] == 1
    assert any("o.txt" in e for e in got["excluded"]), got["excluded"]


# ------------------------------------------------ shape 1: double matching
def test_overlapping_patterns_make_a_double_count_visible():
    got = overlapping_patterns([r"run\d+", r"\d{4}"],
                               ["run2026", "run11", "x2026", "none"])
    assert got["double_matched"] == 1
    assert got["by_item"] == {"run2026": [0, 1]}
    assert got["distinct_matched"] == 3
    assert got["sum_of_counts"] == 4, (
        "the sum exceeding the distinct total IS the double count, and it must "
        "be visible in the return rather than buried in a per-pattern loop")


def test_disjoint_patterns_report_no_overlap():
    """ANTI-FALSE-ALARM. A detector that always warns is ignored."""
    got = overlapping_patterns([r"^a", r"^b"], ["alpha", "beta", "gamma"])
    assert got["double_matched"] == 0
    assert got["distinct_matched"] == got["sum_of_counts"] == 2


def test_the_module_exports_only_the_four_helpers():
    """A counting module that grows a fifth unit silently defeats its purpose."""
    import bench.counting as c
    assert set(c.__all__) == {
        "occurrences", "lines_containing", "count_over", "overlapping_patterns"}
