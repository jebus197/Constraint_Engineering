#!/usr/bin/env python3
"""Rule 30 must not refuse a record for a SEAT's vocabulary -- measured defect.

TASK V8 exists so a seat's words reach the record unedited, and the verbatim
exemption in `scripts/note_vagueness_lint.py` carries that. Its own comment
records why, from 2026-09-10: a panel record carrying 2 seats in full held 4
findings, all inside quoted model output, and *"the record could not be
committed without editing what the models actually said. Editing it would
falsify the record, which is worse than any vagueness in it."*

THE DEFECT, MEASURED 2026-10-18 on
`Panel_FULL_RECORD_Severity_Ruler_Coarseness_2026-10-18.md`. Rule 30, the
undefined-compound-term check, was computed on a SEPARATE path from `lint()` and
appended to the counted list AFTER `partition()` split the exemption. So
`partition()` exempted 4 of 4 findings it could see while 6 further findings --
every one inside a seat's own reply -- bypassed the exemption entirely, and the
commit ratchet refused the record for the seats' vocabulary.

WHY THE TEST IS ON TEXT AND NOT A PARAGRAPH NUMBER, which is the subtle half.
The 2 paragraph splitters DISAGREE: on that file `paragraphs()` yields 119 and
`verbatim_paragraphs()` 99. Filtering Rule 30 by the `marked` paragraph set
would therefore have exempted the WRONG paragraphs -- which is how the same
paragraph came to show one finding counted and another exempted in the same
report. Containment in the region's own text is numbering-independent.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import note_vagueness_lint as L  # noqa: E402

RECORD = (REPO / "experimental_notes"
          / "Panel_FULL_RECORD_Severity_Ruler_Coarseness_2026-10-18.md")


def test_text_inside_a_region_is_recognised_without_paragraph_numbers():
    text = ("outside one\n\n<!-- verbatim-begin: a seat -->\n\n"
            "inside the region\n\n<!-- verbatim-end -->\n\nafter it\n")
    assert L.verbatim_spans(text), "no span found between the markers"
    assert L.inside_verbatim(text, "inside the region") is True
    assert L.inside_verbatim(text, "outside one") is False
    assert L.inside_verbatim(text, "after it") is False


def test_an_unclosed_region_runs_to_the_end_rather_than_vanishing():
    """An unclosed marker must not silently exempt NOTHING."""
    text = "before\n\n<!-- verbatim-begin: a seat -->\n\ntrailing words\n"
    assert L.inside_verbatim(text, "trailing words") is True
    assert L.inside_verbatim(text, "before") is False


def test_a_note_with_no_region_is_untouched():
    """The repair must not loosen an ordinary note."""
    text = "a plain note with a severity band and a blocking gate in it\n"
    assert L.verbatim_spans(text) == []
    assert L.inside_verbatim(text, "a plain note") is False


def test_rule_30_exempts_a_seats_words_and_still_counts_the_notes_own():
    """Both halves, on a constructed file this test owns."""
    body = (
        "# A record\n\n"
        "This note's own prose mentions a coherence budget ceiling here.\n\n"
        "<!-- verbatim-begin: cc2 -->\n\n"
        "The population filter inside the expected critical series mirrors it.\n\n"
        "<!-- verbatim-end -->\n\n"
        "Written under CDSFL note standard v1.8.\n"
    )
    tmp = REPO / "experimental_notes" / "_rule30_probe_2026-10-18.md"
    try:
        tmp.write_text(body, encoding="utf-8")
        counted, exempted = L.split_reported_terms(tmp)
        c_txt = " ".join(h[3] for h in counted)
        e_txt = " ".join(h[3] for h in exempted)
        # ★ A VACUOUS ASSERTION WAS WRITTEN HERE AND REMOVED. It read
        # `assert "population filter" in e_txt or not exempted or True`, which
        # is `assert True` -- the exact shape this project removes elsewhere.
        # The real contract has 2 halves and both are now asserted.
        assert "population filter" in e_txt, (
            "the seat's own term was not exempted, so the region is not reaching "
            "Rule 30 at all")
        assert "population filter" not in c_txt, (
            "a term inside the seat's region was COUNTED: the exemption that "
            "task V8 depends on is not reaching Rule 30")
        assert L.inside_verbatim(body, "The population filter inside the "
                                       "expected critical series mirrors it.")
        assert not L.inside_verbatim(body, "This note's own prose mentions a "
                                           "coherence budget ceiling here.")
    finally:
        tmp.unlink(missing_ok=True)


@pytest.mark.skipif(not RECORD.is_file(), reason="the record is not present")
def test_the_real_record_is_committable_without_editing_the_seats():
    """The file the defect was found on, end to end."""
    counted, exempted = L.split_reported_terms(RECORD)
    assert exempted, (
        "the record carries seat replies and should exempt something; if it "
        "exempts nothing the markers have been lost")
    assert counted == [], (
        f"Rule 30 still counts {len(counted)} finding(s) inside the seats' "
        f"replies: {[h[2] for h in counted]}. Committing would require editing "
        f"what the models actually said, which falsifies the record")


def test_the_command_line_and_the_split_agree_on_the_record():
    """One implementation, two callers -- the defect was two paths disagreeing."""
    import subprocess
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "note_vagueness_lint.py"),
                        str(RECORD)], cwd=REPO, capture_output=True, text=True,
                       timeout=600)
    counted, _ = L.split_reported_terms(RECORD)
    other = L.partition(RECORD)[0] + L.missing_standard_stamp(RECORD)
    expected = len(counted) + len(other)
    # ★ ANCHORED TO THE PER-FILE LINE, NOT A BARE SUBSTRING. The first version
    # asserted `f"{expected} finding(s)" in r.stdout`, and a mutation escaped it:
    # with expected 0 the needle "0 finding(s)" is a SUBSTRING of the verbatim
    # heading's "10 finding(s)", so the check passed while the CLI reported 6.
    # A loose predicate is the defect class this file exists to repair.
    needle = f"{RECORD.name}: {expected} finding(s)"
    assert needle in r.stdout, (
        f"the command line and split_reported_terms disagree: expected the line "
        f"{needle!r}, and the CLI said\n{r.stdout[-500:]}")
