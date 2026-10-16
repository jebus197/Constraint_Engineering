"""A task entry the founder has already ruled on must not be put to him again.

HIS QUESTION, 2026-10-16: *"Of the 13 decisions, are you certain none of these
are items I have previously ruled on? This seems an unusually large HIL queue,
which traditionally has been a strong indicator of mechanical, and/or
implementation/process failure."* It was a process failure, and he diagnosed it
from the symptom alone.

MEASURED BEFORE THE FIX: of the 13 decisions in the 2026-10-16 report, 5 should
not have been put to him, 38.4615%, 95% Wilson [17.7097%, 64.4771%],
Clopper-Pearson [13.8579%, 68.4222%]. 7 of 13 were wrong AS FRAMED.

THE CAUSE WAS THE MARKER SCHEMA. Across 108 markers the fields were exactly
`task`, `state`, `status` and `evidence`. `state` is lifecycle
(OPEN/DONE/BLOCKED/WITHDRAWN) and `status` is build state
(PROPOSED/BUILT/TESTED/COMMITTED/ENABLED). BOTH describe the WORK. Nothing
recorded whether the FOUNDER HAD RULED, so a ruling he gave that was not
immediately executed left its entry indistinguishable from one he had never
seen. R1 is the proof: he ruled "Restart it" on 2026-08-07 and again on
2026-09-06, and 70 days later the entry still appeared under "decisions that
need you".

AND NO CANONICAL REGISTER EXISTED TO CONSULT INSTEAD. Rulings live in 29 dated
documents in `experimental_notes/`, created at 1.1469 per week across 177 days,
and the one named `CDSFL_Founder_Decision_Register_2026-07-06.md` has 3 commits
and was last touched 2026-08-15. So the per-entry field is the record, not a
duplicate of one.

IT MOVES, IT DOES NOT VANISH. A ruled entry is routed to section 3 carrying the
DATE he ruled, in both the markdown and the spoken form, so he reads "you ruled
this on X, the work is outstanding". Silently dropping it would replace a queue
that over-asks with one that under-reports, which is worse and harder to notice.

A SECOND DEFECT FOUND ON THE WAY, in the same generator. `_spoken()`'s docstring
has always promised that "FILE PATHS ... are dropped entirely, because note
standard Rule 6 forbids spelling paths phonetically". The body never stripped a
path. Measured on the file actually delivered to him: 12 path-like tokens, which
a text-to-speech reader pronounces character by character. The guard did not
catch it either, because it asserted on ONE literal prefix, `bench/tests/`, and
11 of the 12 do not start with it. Both are repaired here.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as tlm  # noqa: E402

PATH_RE = re.compile(r"[\w./-]*/[\w.-]+\.(?:py|json|md|txt|toml)")


def _gen():
    spec = importlib.util.spec_from_file_location(
        "_mrb", REPO / "scripts" / "morning_report_build_2026-10-12.py")
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


# --------------------------------------------------------------------------
# The field parses, and it is backward compatible.
# --------------------------------------------------------------------------

def test_the_marker_regex_accepts_ruled_with_and_without_evidence():
    with_ev = ("<!-- task: R1 | state: BLOCKED | status: PROPOSED "
               "| evidence: a.py, b.py | ruled: 2026-08-07 -->")
    m = tlm.MARKER.match(with_ev)
    assert m and m.group(4).strip() == "a.py, b.py" and m.group(5).strip() == "2026-08-07"
    without = "<!-- task: X9 | state: OPEN | status: PROPOSED | ruled: 2026-09-10 -->"
    m2 = tlm.MARKER.match(without)
    assert m2 and m2.group(4) is None and m2.group(5).strip() == "2026-09-10"


def test_a_marker_with_no_ruled_field_still_parses():
    """The field is optional for the same reason `evidence` is: adding it must
    not break an entry that predates it. 0 of 107 markers parsed differently."""
    legacy = "<!-- task: A1 | state: DONE | status: COMMITTED | evidence: x.py -->"
    m = tlm.MARKER.match(legacy)
    assert m and m.group(5) is None
    assert tlm.MARKER.match(
        "<!-- task: A2 | state: OPEN | status: PROPOSED -->") is not None


def test_entry_can_still_be_built_with_six_positional_arguments():
    """~20 modules import this parser; a 7th field without a default would
    break all of them at once."""
    e = tlm.Entry("X", 1, "text", "OPEN", "PROPOSED", ())
    assert e.ruled is None


def test_the_live_list_parses_and_carries_the_seeded_rulings():
    entries = tlm.parse_entries()
    assert len(entries) > 100, "the parser lost entries"
    ruled = {e.ident: e.ruled for e in entries if e.ruled}
    assert ruled.get("R1") == "2026-08-07", ruled
    assert ruled.get("A19") == "2026-09-10", ruled


# --------------------------------------------------------------------------
# A ruled entry leaves the decision list and arrives, visibly, in section 3.
# --------------------------------------------------------------------------

def test_task_items_carries_the_ruled_field():
    g = _gen()
    items = {i["ident"]: i for i in g.task_items()}
    assert "ruled" in next(iter(items.values())), (
        "task_items() dropped the field, so the routing below cannot see it"
    )
    assert items["R1"]["ruled"] == "2026-08-07"


def test_a_ruled_entry_is_not_in_the_decision_list():
    md = (REPO / "experimental_notes"
          / "Morning_Report_2026-10-16_GENERATED.md")
    if not md.is_file():
        pytest.skip("no generated report in this checkout")
    t = md.read_text(errors="replace")
    # ★ ANCHORED ON THE NEWLINE. `"## 2."` is a SUBSTRING of `"### 2."`, the
    # second DECISION heading, so splitting on it cut the document in the wrong
    # place and this test passed for the wrong reason. Same predicate error the
    # session has already made twice.
    head = t.split("\n## 2.")[0]
    for ident in ("R1 —", "A19 —"):
        assert ident not in head, (
            f"{ident} is back in the decision list; he has already ruled on it"
        )


def test_a_ruled_entry_appears_in_section_3_with_its_date():
    md = (REPO / "experimental_notes"
          / "Morning_Report_2026-10-16_GENERATED.md")
    if not md.is_file():
        pytest.skip("no generated report in this checkout")
    t = md.read_text(errors="replace")
    sec3 = t.split("\n## 3.")[1].split("\n## 4.")[0]
    assert "YOU RULED THIS ON 2026-08-07" in sec3, (
        "a ruled item vanished instead of moving — that under-reports"
    )
    assert "YOU RULED THIS ON 2026-09-10" in sec3


def test_the_spoken_form_says_the_ruling_aloud():
    tts = pathlib.Path.home() / "Desktop" / "CDSFL_tts" / \
        "Morning_Report_2026-10-16_GENERATED.txt"
    if not tts.is_file():
        pytest.skip("no TTS companion in this checkout")
    t = tts.read_text(errors="replace")
    assert "You ruled on this on 2026-08-07" in t
    assert "The work is outstanding, not the decision." in t


# --------------------------------------------------------------------------
# The path strip that was described and never implemented.
# --------------------------------------------------------------------------

def test_spoken_strips_a_bare_path():
    g = _gen()
    out = g._spoken("Producer: scripts/a_thing_2026-10-16.py and the rest.")
    assert not PATH_RE.search(out), out


@pytest.mark.parametrize("label", ["Producer", "Guard", "Evidence", "Script"])
def test_spoken_drops_a_labelled_path_clause_whole(label):
    """Deleting only the path leaves wreckage like 'guard: , 13 tests', which
    `feedback_no_mechanical_tts` forbids."""
    out = g_out = _gen()._spoken(
        f"The cause is fixed. {label}: bench/tests/test_x_2026-10-16.py, 13 tests.")
    assert not PATH_RE.search(out), out
    assert ": ," not in out and "  " not in out, f"wreckage left: {g_out!r}"


def test_the_delivered_tts_contains_no_path_at_all():
    """★ THE PREDICATE THAT THE OLD GUARD GOT WRONG. It asserted on the single
    literal prefix `bench/tests/`, and 11 of the 12 tokens that actually leaked
    do not start with it, so it passed while the defect shipped."""
    tts = pathlib.Path.home() / "Desktop" / "CDSFL_tts" / \
        "Morning_Report_2026-10-16_GENERATED.txt"
    if not tts.is_file():
        pytest.skip("no TTS companion in this checkout")
    found = PATH_RE.findall(tts.read_text(errors="replace"))
    assert not found, f"{len(found)} path(s) would be spelled aloud: {sorted(set(found))[:6]}"


def test_the_markdown_keeps_its_locators():
    """A listener needs to DECIDE; a reader needs to ACT. Stripping both would
    make the fix a removal rather than a repair."""
    md = (REPO / "experimental_notes"
          / "Morning_Report_2026-10-16_GENERATED.md")
    if not md.is_file():
        pytest.skip("no generated report in this checkout")
    # The threshold was 10, set when section 1 carried 13 decisions each with
    # its evidence paths. With the queue cleared the document is 96 lines rather
    # than 261, so the absolute count is far lower while the PROPERTY is
    # unchanged: the markdown keeps locators the spoken form drops.
    md_paths = PATH_RE.findall(md.read_text(errors="replace"))
    tts = pathlib.Path.home() / "Desktop" / "CDSFL_tts" / \
        "Morning_Report_2026-10-16_GENERATED.txt"
    assert md_paths, "the markdown lost every locator; a reader cannot act on it"
    if tts.is_file():
        assert not PATH_RE.findall(tts.read_text(errors="replace")), \
            "the spoken form gained a path"


# --------------------------------------------------------------------------
# The permanent strike. "Permanently" has to be mechanical, not an intention.
# --------------------------------------------------------------------------

def test_the_severity_gate_provenance_question_is_struck_permanently():
    """★ HIS INSTRUCTION, 2026-10-16: "This is an issue we have gone over many
    times ... please strike this permanently from your list of outstanding
    decisions."

    HE WAS RIGHT AND THE PROJECT'S OWN RECORD SAYS SO. The memory note of
    2026-10-06 reads "THE REMOVAL IS REVERTED, ON HIS 3rd OR 4th REJECTION OF
    IT", quoting him: "This is now at least the 3rd or 4th time I have rejected
    this change." It also records that commit 6c10fe4 quoted him approving the
    removal and that the quote existed ONLY in the code comment and in 5 panel
    diffs all dated AFTER the commit -- no source for the approval ever existed.
    Re-presenting it on 2026-10-16 made it the 5TH time.

    AND THE REPAIR WORKS: 20 tests in test_severity_calibration.py pass, and by
    EXECUTION rather than grep `FindingRegistry.unverified_critical_count`
    contains `severity_is_proven`.

    WHY IT GOT THROUGH the `ruled:` marker field shipped the same morning: that
    field covers TASK-LIST ENTRIES, and 9 of the 13 decisions had no marker.
    """
    import json
    study = json.loads((REPO / "experimental_notes" / "STUDY_IN_FLIGHT.json")
                       .read_text())
    struck = [x for x in study.get("open_defects", [])
              if x.get("struck_permanently")]
    assert struck, "the permanent strike is gone from the record"

    # ★ THIS CALLS THE GENERATOR RATHER THAN READING ITS OUTPUT, and the first
    # version did the opposite and was VACUOUS. Removing the escape in
    # `decisions()` makes the generator ABORT at exit 3 on orphan detail, so the
    # report file is never rewritten and a test reading that file sees the last
    # GOOD output and passes. The mutation proved it: 17 passed with the escape
    # deleted. A guard that reads a stale artefact cannot detect the code that
    # failed to produce a new one.
    g = _gen()
    items = g.task_items() + g.study_items()
    decs, _missing, _orphan = g.decisions(items)
    live = [d for d in decs if not d.get("no_ruling_needed")]
    struck_keys = {f"defect:{x.get('id') or str(x.get('name',''))[:40]}"
                   for x in struck}
    for d in live:
        assert d["key"] not in struck_keys, (
            f"{d['key']} is STRUCK yet reached the live decision list; he has "
            f"settled it 5 times"
        )
    # and nothing he has ruled on may be live either
    for d in live:
        assert not d.get("ruled"), (
            f"{d['key']} carries a ruling of {d.get('ruled')} yet is still a "
            f"live decision"
        )
    assert not live, (
        f"{len(live)} live decision(s) remain though he ruled on all of them "
        f"on 2026-10-16: {[d['key'] for d in live]}"
    )


def test_the_severity_gate_itself_still_functions():
    """His question: "The severity gate now functions as specified, as fa as
    your recent tests indicate? So our repairs worked?" Answered by execution,
    so a future removal cannot pass while this test reads a stale claim."""
    import inspect
    sys.path.insert(0, str(REPO / "bench"))
    import reference_runner_v3 as R  # noqa: E402
    src = inspect.getsource(R.FindingRegistry.unverified_critical_count)
    assert "severity_is_proven" in src, (
        "the severity test has left the blocker counter again — this is the "
        "change he has now rejected 4 times"
    )
