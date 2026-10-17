"""The 20 confirmed coverage gaps must stay in the task list, with his words intact.

WHY THIS TEST EXISTS. The verdict-coverage audit of 2026-10-17 examined 302 of the
founder's annotations and confirmed 20 gaps: instructions and rulings of his that no
task entry tracked. The audit's own finding about the SHAPE of that failure is the
reason for this guard: not one of the 20 was lost because it was hard. Each was
answered in conversation, or partly built, and then never written into the list that
survives a compaction.

So the entries themselves are now the thing at risk. A guard that only counted them
would pass while an entry was silently emptied of his words, which is the defect class
`feedback_pin_a_set_not_a_count` names -- a count cannot say what moved, and a set
catches a swap. This test therefore pins the SET of identifiers AND requires each one
to carry founder text, the verifier's refutation attempt, and a coherent marker.

It asserts on the task list because the task list IS the artefact under test here; it
is not standing in for executable behaviour elsewhere, so `execute-do-not-grep` is
satisfied by calling the marker parser rather than pattern-matching the markers.
"""
from __future__ import annotations

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TASKLIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
sys.path.insert(0, str(REPO / "scripts"))

#: The audit confirmed exactly 20 gaps. Pinned as a SET, not a count.
CONFIRMED = {f"C{i}" for i in range(1, 21)}
#: C0 is the measurement record that produced them.
MEASUREMENT = "C0"

#: Severity counts the audit reported, which the entry headings must still reflect.
EXPECTED_SEVERITY_TOTALS = {
    "A RULING HE GAVE, NOT CARRIED OUT": 12,
    "AN INSTRUCTION NOTHING TRACKS": 4,
    "A DIRECT QUESTION NEVER ANSWERED": 4,
}


def _entries():
    import task_list_markers as t
    return {e.ident: e for e in t.parse_entries(TASKLIST)}


def _paragraph(ident: str) -> str:
    text = TASKLIST.read_text(encoding="utf-8")
    for para in text.split("\n\n"):
        if re.match(rf"\*\*{re.escape(ident)}\.", para.strip()):
            return para
    return ""


def test_the_task_list_still_parses():
    """Anti-vacuity: every assertion below is meaningless if parsing fails."""
    entries = _entries()
    assert len(entries) > 100, f"only {len(entries)} entries parsed; the list is broken"


def test_all_20_confirmed_gaps_are_present_as_a_set():
    present = set(_entries()) & (CONFIRMED | {MEASUREMENT})
    missing = (CONFIRMED | {MEASUREMENT}) - present
    assert not missing, (
        f"{len(missing)} audit entries have left the task list: {sorted(missing)}. "
        "These are founder instructions the 2026-10-17 audit confirmed were untracked; "
        "removing an entry re-creates the exact defect the audit measured."
    )


@pytest.mark.parametrize("ident", sorted(CONFIRMED))
def test_each_gap_entry_carries_his_words_and_the_refutation(ident):
    para = _paragraph(ident)
    assert para, f"{ident} has no paragraph in the task list"
    assert "**HIS WORDS:**" in para, f"{ident} no longer quotes the founder"
    assert "TRIED TO REFUTE THIS AND FAILED" in para, (
        f"{ident} no longer records the adversarial verifier's failed refutation, so a "
        "reader cannot tell a verified gap from an unverified claim"
    )
    # His quoted words must not be empty, nor a bare ellipsis.
    #
    # THE FIRST VERSION OF THIS ASSERTION WAS VACUOUS, found by mutation on
    # 2026-10-17. It captured a fixed 40-character window after the heading, which
    # runs PAST a short quotation and into the next bold heading, so replacing his
    # words with an ellipsis still left 40 characters of the NEXT heading to
    # measure and the assertion passed. The window must stop at the next heading.
    m = re.search(r"\*\*HIS WORDS:\*\*(.*?)\*\*", para, re.DOTALL)
    assert m, f"{ident} has no HIS WORDS section followed by a heading"
    quoted = m.group(1).strip().strip('"\u201c\u201d').strip(" .\u2026")
    # THRESHOLD CHOSEN FROM THE DATA, not guessed. His shortest genuine quotation
    # among the 20 is 34 characters ("Are the 12 skipped safe to ignore?"), and an
    # emptied quotation strips to 0, so any threshold from 1 to 33 discriminates.
    # 12 leaves margin on both sides. A first attempt used 40 and failed on C6,
    # which is a real instruction of his and not a defect.
    assert len(quoted) > 12, (
        f"{ident} carries a HIS WORDS heading whose quotation is {len(quoted)} "
        f"characters: {quoted[:60]!r}. His words are the only reason the entry can "
        "be recognised as his instruction rather than a paraphrase of it."
    )


@pytest.mark.parametrize("ident", sorted(CONFIRMED))
def test_each_gap_entry_has_a_coherent_marker(ident):
    e = _entries().get(ident)
    assert e is not None, f"{ident} has no marker"
    assert e.state in ("OPEN", "DONE", "BLOCKED", "DEFERRED", "WITHDRAWN")
    assert (e.state, e.status) not in {("DONE", "PROPOSED"), ("DONE", "BUILT"),
                                       ("DONE", "TESTED")}, (
        f"{ident} is marked DONE with a build status that contradicts it"
    )


def test_a_ruling_gap_records_the_date_he_ruled():
    """A ruling not carried out must carry its ruling date, or it re-enters the queue.

    This is the defect the `ruled:` field was added on 2026-10-16 to close, and which
    was measured reopening on 2026-10-17 at 10 of 15 open items.
    """
    entries = _entries()
    offenders = []
    for ident in sorted(CONFIRMED):
        para = _paragraph(ident)
        if "A RULING HE GAVE, NOT CARRIED OUT" in para:
            e = entries.get(ident)
            if e is None or not e.ruled:
                offenders.append(ident)
    assert not offenders, (
        f"{len(offenders)} entries record a ruling he gave but carry no ruled date, so "
        f"the morning report will ask him again: {offenders}"
    )


def test_the_severity_mix_still_matches_what_the_audit_reported():
    counts = {k: 0 for k in EXPECTED_SEVERITY_TOTALS}
    for ident in sorted(CONFIRMED):
        para = _paragraph(ident)
        for label in counts:
            if label in para:
                counts[label] += 1
                break
    assert counts == EXPECTED_SEVERITY_TOTALS, (
        f"the severity mix changed: {counts} against the audit's "
        f"{EXPECTED_SEVERITY_TOTALS}. 12 of the 20 were rulings he had already given; "
        "if that number falls without entries closing, the record has been softened."
    )


def test_the_measurement_entry_states_the_rate_and_its_interval():
    para = _paragraph(MEASUREMENT)
    assert para, "C0, the measurement record, is missing"
    assert "20 of 266" in para, "C0 no longer states the measured rate"
    assert "7.5188" in para, "C0 no longer states the point estimate"
    assert "4.9197" in para and "11.3274" in para, (
        "C0 no longer carries its confidence interval; a rate without one is a claim "
        "about evidence rather than evidence"
    )
    assert "54.5455" in para, (
        "C0 no longer records that the adversarial pass refuted 24 of 44 claimed gaps, "
        "which is the figure that makes the surviving 20 credible"
    )
