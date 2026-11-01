"""R1, the zero-plant control, must have a NAMED POSITION in the runway document.

WHY THIS GUARD EXISTS, AND IT DOES NOT NEED A LIVE DEFECT TO BE WORTH HAVING.
The founder gave the same ruling on R1 5 times across 2026-08-07, 2026-09-06,
2026-10-19, 2026-10-30 and 2026-11-01, and each time a report scanned the
outstanding work and put it to him again as though a decision were owed. The
cause was structural rather than careless: R1 lived in the master task list,
which is a WORK QUEUE, and had no position in `RUNWAY_to_BR2_2026-08-18.md`,
which is the RUN ORDER. An item with no position in the run order is an item
that gets re-presented as a decision, so the position is the fix and this test
is what keeps it.

WHAT THIS DOES NOT ASSERT. It does not assert that R1 has RUN, and it must not:
the run spends real money and its launch authorisation is the founder's. The
subject here is whether the SCHEDULE records where R1 sits, which is a property
of a document and mechanically checkable.

THE SECOND THING IT PINS, WHICH IS THE EASIER ONE TO BREAK BY BEING HELPFUL.
The section sits at the END of the file although its stage number places it
after 4B. That is deliberate. 5 live line citations point into this document
from `experimental_notes/Research_FULL_RECORD_2026-09-09.md`, a VERBATIM panel
transcript that may not be edited, and `test_line_citations_resolve_2026-09-01.py`
checks only that a cited line is IN RANGE -- its own docstring says so -- never
that the line still says what the citation claims. So a future editor who
"tidies" the file by moving STAGE 4C up to sit beside STAGE 4B would silently
move all 5 citations onto the wrong content and no existing test would fail.
This one pins the prefix instead: everything above the append point must stay
where it is. The convention is already the file's own -- STAGE 0C is logically
the earliest stage and sits physically near the end.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNWAY = REPO / "experimental_notes" / "RUNWAY_to_BR2_2026-08-18.md"
TRANSCRIPT = REPO / "experimental_notes" / "Research_FULL_RECORD_2026-09-09.md"

#: The line count of the runway at the commit that added STAGE 4C. Every line
#: at or below this index must be byte-stable, because the citations land there.
PREFIX_LINES = 849


def runway_text() -> str:
    return RUNWAY.read_text(errors="ignore")


def r1_section() -> str:
    """The STAGE 4C section body, or '' if there is no such section."""
    text = runway_text()
    m = re.search(r"^## STAGE 4C\b.*?$", text, re.M)
    if not m:
        return ""
    start = m.start()
    nxt = re.search(r"^## ", text[m.end():], re.M)
    return text[start:m.end() + nxt.start()] if nxt else text[start:]


def test_r1_has_a_named_stage_section():
    sec = r1_section()
    assert sec, (
        "No `## STAGE 4C` section in the runway. R1 has no position in the run "
        "order, which is the condition that caused it to be re-presented to the "
        "founder as an open decision 5 times.")


def test_the_section_names_r1_and_the_control():
    sec = r1_section().lower()
    assert "r1" in sec, "STAGE 4C does not name R1."
    assert "zero-plant" in sec or "zero plant" in sec, (
        "STAGE 4C does not name the zero-plant control, so a reader cannot tell "
        "which experiment it schedules.")
    assert "exp 53" in sec or "exp53" in sec, (
        "STAGE 4C does not name Exp 53, which is the experiment R1 restarts.")


def test_the_section_states_a_mechanical_gate_not_a_judgement():
    sec = r1_section()
    assert "CDSFL_MASTER_TASK_LIST.md" in sec, (
        "STAGE 4C must name the master task list as its gate, because the "
        "founder's ruling is that R1 runs once that list is complete.")
    assert "task_list_markers.py" in sec, (
        "STAGE 4C must name the instrument that decides the gate. 'When the "
        "list is clear' is a judgement; `effective_state()` is a measurement.")
    assert re.search(r"\b0 OPEN\b", sec), (
        "STAGE 4C must state the gate threshold as 0 OPEN entries.")


def test_the_section_records_that_it_is_not_a_decision_awaiting_him():
    sec = r1_section()
    low = sec.lower()
    assert "not a decision" in low or "must not be put to him again" in low, (
        "STAGE 4C must say plainly that R1 is NOT a decision awaiting the "
        "founder. That sentence is the whole purpose of the section.")
    # His own words must be present, not a paraphrase of them.
    assert "it should probably be the next task on our runway" in low, (
        "STAGE 4C must carry his 2026-11-01 instruction verbatim. A paraphrase "
        "inside quotation marks is forbidden by his ruling of 2026-10-19.")


def test_the_section_does_not_claim_the_spend_is_authorised():
    sec = r1_section().lower()
    assert "authorisation" in sec or "authorization" in sec, (
        "STAGE 4C must record that launch authorisation is still the founder's, "
        "because R1 spends real money.")
    for wrong in ("spend approved", "authorised to spend", "funding approved"):
        assert wrong not in sec, (
            f"STAGE 4C must not imply the spend is authorised (found {wrong!r}). "
            "Scheduling an item is not releasing money for it.")


def test_the_citation_prefix_is_byte_stable():
    """Everything above the append point must not move."""
    r = subprocess.run(
        ["git", "show", f"HEAD:experimental_notes/RUNWAY_to_BR2_2026-08-18.md"],
        capture_output=True, text=True, cwd=str(REPO))
    if r.returncode != 0 or not r.stdout:
        return  # nothing to compare against; not a failure of the subject
    head_lines = r.stdout.splitlines()
    now_lines = runway_text().splitlines()
    n = min(PREFIX_LINES, len(head_lines))
    assert len(now_lines) >= n, (
        f"The runway lost lines: {len(now_lines)} now against {n} expected in "
        "the citation prefix. Line citations from the verbatim transcript land "
        "in that region.")
    for i in range(n):
        assert now_lines[i] == head_lines[i], (
            f"Runway line {i + 1} changed. Content above the STAGE 4C append "
            "point must stay byte-stable: 5 line citations from "
            "Research_FULL_RECORD_2026-09-09.md point into this region, that "
            "file is a verbatim transcript and may not be edited to follow, and "
            "test_line_citations_resolve_2026-09-01.py checks only that a cited "
            "line is in range -- so a shift here fails silently.")


def test_the_transcript_citations_into_the_runway_still_resolve():
    """The citations this arrangement protects must actually be in range."""
    if not TRANSCRIPT.exists():
        return
    text = TRANSCRIPT.read_text(errors="ignore")
    cited = [int(m) for m in re.findall(
        r"RUNWAY_to_BR2_2026-08-18\.md:(\d+)", text)]
    assert cited, (
        "No line citations into the runway were found in the transcript. This "
        "test's premise is that they exist; if they have genuinely gone, "
        "PREFIX_LINES and the append-only rule should be revisited rather than "
        "left asserting a constraint nothing needs.")
    total = len(runway_text().splitlines())
    out_of_range = [n for n in cited if n > total]
    assert not out_of_range, (
        f"Citations point beyond the end of the runway ({total} lines): "
        f"{sorted(set(out_of_range))}")


def test_stage_0c_still_sits_physically_late():
    """The convention STAGE 4C relies on must still hold in the file."""
    text = runway_text()
    lines = text.splitlines()
    pos = {}
    for i, line in enumerate(lines, start=1):
        m = re.match(r"^## STAGE ([0-9]+[A-Z]?)\b", line)
        if m and m.group(1) not in pos:
            pos[m.group(1)] = i
    assert "0C" in pos, "STAGE 0C heading not found."
    assert "1" in pos, "STAGE 1 heading not found."
    assert pos["0C"] > pos["1"], (
        "STAGE 0C no longer sits physically after STAGE 1. STAGE 4C's placement "
        "argument cites that as the file's existing convention, so if the file "
        "has been reordered, re-derive the argument rather than trusting it.")
