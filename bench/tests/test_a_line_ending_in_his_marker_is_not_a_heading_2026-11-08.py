"""A single-hash line ending in one of his ticket markers is never a heading. B105.

HIS RULING, 2026-11-08: adopt the marker rule.

THE DEFECT WAS THE WORST SHAPE A HEURISTIC CAN HAVE. The reader called a
single-hash line a markdown heading when it was short AND did not end in
sentence punctuation. His commonest annotation -- "I accept your
recommendation. stm" -- ends in a MARKER, so it is not sentence punctuation,
and it is short. Both conditions held for the single most frequent thing he
writes, so it was dropped as not his. 57 lines across 67 response files were
being lost, and they were INSTRUCTIONS: "Permission is granted. stm", "Build
and implement option 1. fr", "Has that task already been run? If not you should
run it. qs".

MEASURED AGAINST GROUND TRUTH, NOT AGAINST A SHAPE. A response file is a copy
of a generated report with his '#' insertions, so the surviving original is an
exact oracle. All 57 recoveries fall in oracle-backed files: 57 of 57 are his
and 0 are report lines, precision 1.000000, Wilson 95% [0.936861, 1.000000].
Producer: ``scripts/his_commonest_annotation_was_read_as_a_heading_2026-11-08.py``.

THE CONTROL IS THE HALF THAT MAKES THIS NOT A FLATTERING MEASURE. A rule this
permissive could start reading real headings as his, so 5 heading shapes that
contain a marker-like substring without ending in a marker -- "Methods",
"Discussion", "discard", "disclose", "Next steps" -- must STAY headings. Without
the word boundary, "Methods" ends in "ds" and "Discussion" starts with "disc".
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts/read_founder_responses_2026-10-11.py"
PRODUCER = REPO / "scripts/his_commonest_annotation_was_read_as_a_heading_2026-11-08.py"


def _reader():
    spec = importlib.util.spec_from_file_location("_cdsfl_rfr_guard", READER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: His real forms, lifted from the corpus rather than invented.
HIS_LINES = (
    "# I accept your recommendation. stm",
    "# Permission is granted. stm",
    "# Repair the gate. stm",
    "# Build and implement option 1. fr",
    "# Has that task already been run? If not you should run it. qs",
    "# What would this mean in real terms? Qs",
    "# Use the first fix and not the cheaper second. disc",
    "# Leave it as history. ds",
)

#: Headings that CONTAIN a marker substring but do not END in a marker. Each
#: one would be misread as his if the word boundary were dropped.
CONTROL_HEADINGS = (
    "# Methods",
    "# Discussion",
    "# discard",
    "# disclose",
    "# Next steps",
    "# Findings",
    "# Discrimination control",
)


@pytest.mark.parametrize("line", HIS_LINES)
def test_his_annotation_is_not_classified_as_a_heading(line):
    assert not _reader()._looks_like_a_markdown_heading(line), (
        f"{line!r} is his, and it is being discarded as a markdown heading")


@pytest.mark.parametrize("line", CONTROL_HEADINGS)
def test_a_real_heading_is_still_a_heading(line):
    """THE CONTROL. A rule that admits everything proves nothing."""
    assert _reader()._looks_like_a_markdown_heading(line), (
        f"{line!r} is a report heading and is now being read as his writing; "
        f"the word boundary is not holding")


def test_two_or_more_hashes_is_still_always_a_heading():
    """The 2026-11-02 rule must survive this one.

    A marker-ending line with 2 hashes is a heading, because his convention is
    exactly 1 hash -- measured at 583 of his annotations opening with 1 and 0
    with 2 or more.
    """
    mod = _reader()
    assert mod._looks_like_a_markdown_heading("## Something. stm"), (
        "a 2-hash line ending in a marker is now read as his, which reverses "
        "the 2026-11-02 fix that stopped 2 external headings leaking through")


def test_the_marker_set_comes_from_the_ticket_store():
    """ONE DECLARATION. A hand-copied marker list would drift from KINDS."""
    import sys
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from bench.ticket_store import KINDS
    assert tuple(_reader()._HIS_KINDS) == tuple(KINDS), (
        "the reader's marker set has drifted from ticket_store.KINDS, so a "
        "kind added there is not recognised in his annotations")


def test_the_match_is_case_insensitive():
    """3 of his annotations carry `Qs` and `Stm` capitalised."""
    mod = _reader()
    for v in ("stm", "Stm", "STM", "qs", "Qs", "QS"):
        assert not mod._looks_like_a_markdown_heading(f"# Do the thing. {v}"), (
            f"a marker spelled {v!r} is not recognised, so his capitalised "
            f"annotations are still discarded")


def test_the_recovery_is_real_and_admits_no_report_line():
    """EXECUTED over the live corpus, against the oracle."""
    if not PRODUCER.is_file():
        pytest.skip("the producer is not in this checkout")
    spec = importlib.util.spec_from_file_location("_cdsfl_b105", PRODUCER)
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    if not P.RESPONSES.is_dir():
        pytest.skip(f"{P.RESPONSES} is not on this machine")
    recovered, his, report, files = P.survey()
    assert not report, (
        f"{len(report)} generated report line(s) are now read as his: "
        f"{report[:5]}")
    assert len(his) >= 50, (
        f"only {len(his)} of his lines are recovered; it was 57 of 57 when the "
        f"rule was adopted, so either the corpus shrank or the rule stopped "
        f"matching")
