#!/usr/bin/env python3
"""Closing a task entry must change 3 surfaces or none. 3 refusals in 1 day say so.

★ WHY: 6 entries were closed on 2026-11-02 and the pre-commit board REFUSED 3
times, every time the same guard, every time because 1 of 3 surfaces was left
behind -- the task-list MARKER, the register TICKET, and the AUTHORED DETAIL in
`experimental_notes/data/morning_report_decisions.json`. Attempt 1 left B61,
C0036 and C0037 stale; attempt 2 left B60 stale and named producers where a
runnable test path is required; attempt 3 left B41 stale. Each refusal cost a
12-minute board. That is a mechanism gap, and his standing instruction is to
mechanise rather than rely on the author remembering.

AND A 4TH TRAP, MET TWICE: the marker FORM varies. B60's already carried an
`evidence:` field and B41's a different `status:`, so an exact-string
replacement built from a guess failed on both. The closer matches by PATTERN,
and that is asserted below against both shapes.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

SCRIPT = REPO / "scripts" / "close_an_entry_2026-11-02.py"


@pytest.fixture(scope="module")
def mod():
    assert SCRIPT.is_file(), f"the closer is missing at {SCRIPT}"
    spec = importlib.util.spec_from_file_location("closer", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_marker_is_matched_by_pattern_not_by_a_literal(mod):
    """Both forms that defeated a constructed literal must match.

    A bare marker, and one already carrying evidence and a ruling date. The
    second is the shape that failed twice on 2026-11-02.
    """
    bare = "<!-- task: X9 | state: OPEN | status: PROPOSED -->"
    rich = ("<!-- task: X9 | state: OPEN | status: TESTED | evidence: "
            "bench/tests/a.py, bench/tests/b.py | ruled: 2026-10-30 -->")
    pat = mod._marker_re("X9")
    for form in (bare, rich):
        m = pat.search(form)
        assert m, f"the pattern does not match {form!r}"
    m = pat.search(rich)
    assert m.group(2) == "TESTED"
    assert m.group(4).strip() == "2026-10-30", "the ruling date must be preserved"


def test_a_contradictory_status_is_REFUSED(mod):
    """DONE with PROPOSED/BUILT/TESTED is refused by task_list_markers, whose
    message is 'A task cannot be done before its work was committed.'"""
    for bad in ("PROPOSED", "BUILT", "TESTED"):
        rec = mod.close_entry("B20", evidence="x", resolution="r",
                              verification="v", status=bad, dry_run=True)
        assert rec["refused"], f"status {bad} with DONE should be refused"
        assert "CONTRADICTORY" in rec["refused"]


def test_an_unknown_entry_is_REFUSED(mod):
    rec = mod.close_entry("ZZ999", evidence="x", resolution="r",
                          verification="v", dry_run=True)
    assert rec["refused"] and "no marker" in rec["refused"]


def test_an_already_DONE_entry_is_REFUSED(mod):
    """Re-closing would overwrite a settled record with a later one, which is
    the fault the register's own guard names."""
    from task_list_markers import parse_entries
    done = [e.ident for e in parse_entries(
        REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
        if e.state == "DONE"]
    if not done:
        pytest.skip("no DONE entry to try")
    rec = mod.close_entry(done[0], evidence="x", resolution="r",
                          verification="v", dry_run=True)
    assert rec["refused"] and "already DONE" in rec["refused"]


def test_a_dry_run_changes_NOTHING_on_disk(mod):
    """The default is a dry run, because a tool that closes by default closes
    by accident."""
    lst = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
    det = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
    before = (lst.read_text(), det.read_text())
    from task_list_markers import parse_entries
    openish = [e.ident for e in parse_entries(lst) if e.state == "OPEN"]
    if not openish:
        pytest.skip("no OPEN entry to try")
    mod.close_entry(openish[0], evidence="x", resolution="r",
                    verification="v", dry_run=True)
    assert (lst.read_text(), det.read_text()) == before, (
        "a dry run wrote to disk")


def test_it_reports_all_three_surfaces_for_a_live_entry(mod):
    """The whole point: 1 call names the marker change, the tickets and the
    detail keys, so none can be forgotten."""
    from task_list_markers import parse_entries
    openish = [e.ident for e in parse_entries(
        REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
        if e.state == "OPEN"]
    if not openish:
        pytest.skip("no OPEN entry to try")
    rec = mod.close_entry(openish[0], evidence="bench/tests/x.py",
                          resolution="r", verification="v", dry_run=True)
    assert not rec["refused"], rec["refused"]
    assert rec["marker"] and "state: DONE" in rec["marker"]["now"]
    assert "status: COMMITTED" in rec["marker"]["now"]
    assert isinstance(rec["tickets"], list)
    assert rec["detail_removed"], "the detail keys must be named"


def test_the_staleness_check_calls_the_GUARDS_OWN_PRODUCER(mod):
    """Not a second spelling of the rule.

    A first version treated every non-DONE entry as live and reported 22 stale
    keys where the guard had named 5. 22 was a wrong predicate, not a finding.
    """
    src = SCRIPT.read_text()
    assert "morning_report_build" in src, (
        "the staleness check must import the guard's own producer rather than "
        "re-deriving what counts as live")
    assert "task_items() + m.study_items()" in src, (
        "it must reproduce the producer's own call site; 2 guesses at the "
        "function name failed before it was looked up")
    out = mod.stale_detail()
    assert isinstance(out, list)
    assert not any("could not" in str(x) for x in out), (
        f"the producer could not be called: {out}")
