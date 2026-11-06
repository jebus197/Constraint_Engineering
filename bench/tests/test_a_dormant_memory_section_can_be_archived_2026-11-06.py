#!/usr/bin/env python3
"""A whole dormant section must be reachable by the archive mechanism.

THE GAP THIS CLOSES, MEASURED 2026-11-06. The index stood at 23,797
characters against a 23,750 refuse line -- 47 over, so `sv` refused the
commit. `archive_stale_memory_entries` is the only mechanism that trims the
index and it ages BY DATE within `_MEMORY_AGEING_SECTIONS`, which is
`('Project State',)` alone. A dry run at every window from 30 days down to 7
moved 0 entries. Two whole sections sat unreachable: `Session Handoffs`
(March 2026, the index itself marks it "read only if relevant") and `Metis`
(a separate, blocked project), both undated and so un-ageable at any window.

TIGHTENING THE WINDOW IS NOT THE FIX AND THE MEASUREMENT SAYS SO. At 5 days
the mechanism DID fire -- by selecting the 2 FRESHEST session entries, which
is the opposite of what the index is for. Grouping is not the fix either: it
joins lines and ADDS separators, so it buys line headroom at a cost in
characters, and characters were the binding limit.

So the mechanism was scoped to the wrong axis for this failure, not broken.
`dormant_sections` adds the missing axis. These tests hold the properties
that make it safe to run unattended: it moves a named section wholesale, it
withdraws a heading only when the section is genuinely empty, it keeps a
heading that still has content, it loses nothing, and it is INERT at its
default so all 12 pre-existing call sites behave exactly as before.
"""
import importlib.util
import pathlib
import sys
from datetime import date

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

_spec = importlib.util.spec_from_file_location("cdsfl_sv", REPO / "scripts" / "cdsfl_sv.py")
sv = importlib.util.module_from_spec(_spec)
sys.modules["cdsfl_sv"] = sv
try:
    _spec.loader.exec_module(sv)
except SystemExit:  # the module answers --help and exits
    pass

TODAY = date(2026, 11, 6)
DORMANT = "Session Handoffs (historical, read only if relevant)"
KEEPS = "Half Dormant"

INDEX = """# CDSFL — Persistent Memory Index

## Project State
- [Recent work](cdsfl_session_2026-11-05_thing.md) — inside the window.
- [Old work](cdsfl_session_2026-06-07_thing.md) — well outside the window.

## Session Handoffs (historical, read only if relevant)

- March 2026 handoffs — [23rd](handoff_2026-03-23.md) architecture.
- [Another](handoff_2026-03-19.md) QC sweep.

## Half Dormant

Standing prose that is not a bullet and must survive.
- [A pointer](handoff_2026-03-20.md) that moves out.

## Feedback (applies to all work)
- [No model voting](feedback_no_model_voting_2026-01-01.md) — ancient, and STANDING.
"""

FILES = ("cdsfl_session_2026-11-05_thing.md", "cdsfl_session_2026-06-07_thing.md",
         "handoff_2026-03-23.md", "handoff_2026-03-19.md", "handoff_2026-03-20.md",
         "feedback_no_model_voting_2026-01-01.md")


@pytest.fixture()
def mem(tmp_path):
    d = tmp_path / "memory"
    d.mkdir()
    (d / "MEMORY.md").write_text(INDEX, encoding="utf-8")
    for name in FILES:
        (d / name).write_text("x", encoding="utf-8")
    return d


def _run(mem, **kw):
    kw.setdefault("today", TODAY)
    kw.setdefault("window_days", 30)
    return sv.archive_stale_memory_entries(mem, **kw)


class TestTheCapabilityExists:
    def test_the_parameter_is_accepted(self):
        import inspect
        sig = inspect.signature(sv.archive_stale_memory_entries)
        assert "dormant_sections" in sig.parameters
        assert sig.parameters["dormant_sections"].default == ()


class TestItIsInertAtItsDefault:
    def test_the_default_moves_only_dated_entries(self, mem):
        """All 12 pre-existing call sites must behave exactly as before."""
        r = _run(mem)
        idx = (mem / "MEMORY.md").read_text()
        assert DORMANT in idx, "the dormant heading moved with no section named"
        assert "handoff_2026-03-23.md" in idx, "an undated bullet moved by default"
        assert r["moved"] == 1, f"expected only the dated entry, moved {r['moved']}"


class TestItMovesANamedSectionWholesale:
    def test_every_bullet_leaves_and_the_heading_is_withdrawn(self, mem):
        r = _run(mem, dormant_sections=(DORMANT,))
        idx = (mem / "MEMORY.md").read_text()
        assert DORMANT not in idx, "an emptied section kept its heading"
        assert "handoff_2026-03-23.md" not in idx
        assert "handoff_2026-03-19.md" not in idx
        assert r["moved"] == 3, f"1 dated + 2 dormant expected, got {r['moved']}"

    def test_a_section_with_surviving_prose_keeps_its_heading(self, mem):
        r = _run(mem, dormant_sections=(KEEPS,))
        idx = (mem / "MEMORY.md").read_text()
        assert f"## {KEEPS}" in idx, "a heading over surviving prose was withdrawn"
        assert "Standing prose that is not a bullet" in idx, "non-bullet prose was lost"
        assert "handoff_2026-03-20.md" not in idx, "the bullet did not move"

    def test_both_at_once(self, mem):
        r = _run(mem, dormant_sections=(DORMANT, KEEPS))
        idx = (mem / "MEMORY.md").read_text()
        assert DORMANT not in idx and f"## {KEEPS}" in idx
        assert r["moved"] == 4


class TestNothingIsLost:
    def test_every_moved_line_is_in_the_archive(self, mem):
        before = (mem / "MEMORY.md").read_text()
        _run(mem, dormant_sections=(DORMANT, KEEPS))
        arc = (mem / sv._MEMORY_ARCHIVE_NAME).read_text()
        for name in ("handoff_2026-03-23.md", "handoff_2026-03-19.md",
                     "handoff_2026-03-20.md", "cdsfl_session_2026-06-07_thing.md"):
            assert name in arc, f"{name} left the index and is in no archive"
        after = (mem / "MEMORY.md").read_text()
        assert len(after) < len(before), "nothing was freed"

    def test_the_backup_is_the_index_as_it_was_found(self, mem):
        before = (mem / "MEMORY.md").read_text()
        r = _run(mem, dormant_sections=(DORMANT,))
        assert r["backup"], "no backup path reported"
        assert pathlib.Path(r["backup"]).read_text() == before, \
            "the backup is not byte-identical to what was found"

    def test_dry_run_writes_nothing(self, mem):
        before = (mem / "MEMORY.md").read_text()
        r = _run(mem, dormant_sections=(DORMANT,), dry_run=True)
        assert r["moved"] == 3 and r["ok"]
        assert (mem / "MEMORY.md").read_text() == before
        assert not (mem / sv._MEMORY_ARCHIVE_NAME).exists()
        assert r["backup"] is None


class TestTheRecordSaysWhichRouteMovedThem:
    def test_the_reason_names_the_dormant_sections(self, mem):
        r = _run(mem, dormant_sections=(DORMANT,))
        assert DORMANT in r["reason"], f"the reason hides the route: {r['reason']}"

    def test_the_archive_heading_names_them(self, mem):
        _run(mem, dormant_sections=(DORMANT,))
        arc = (mem / sv._MEMORY_ARCHIVE_NAME).read_text()
        assert DORMANT in arc, "the archive does not record why these rows moved"

    def test_undated_entries_sort_after_dated_ones(self, mem):
        _run(mem, dormant_sections=(DORMANT,))
        arc = (mem / sv._MEMORY_ARCHIVE_NAME).read_text()
        dated = arc.index("cdsfl_session_2026-06-07_thing.md")
        undated = arc.index("handoff_2026-03-23.md")
        assert dated < undated, "an undated row sorted ahead of a dated one"

    def test_an_undated_only_run_still_reports_a_reason(self, mem):
        r = _run(mem, window_days=36500, dormant_sections=(DORMANT,))
        assert r["ok"] and r["moved"] == 2
        assert "undated" in str(r["moved_titles"]), \
            "an undated row must be labelled undated, not crash or claim a date"


class TestTheWiredCaller:
    def test_the_caller_exists_and_answers_help_without_touching_the_index(self):
        import subprocess
        caller = REPO / "scripts" / "archive_a_dormant_memory_section_2026-11-06.py"
        assert caller.exists(), "the capability has no caller; it is an unwired addition"
        r = subprocess.run([sys.executable, str(caller), "--help"],
                           cwd=REPO, capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-800:]
        assert "--section" in r.stdout and "--dry-run" in r.stdout
