#!/usr/bin/env python3
"""The index must age itself out on a save, and it must never lose anything.

THE FOUNDER'S DESCRIPTION OF WHAT MEMORY.md IS FOR, verbatim 2026-10-03: "a
resource that keeps all the most recent and critical project information over a
number of days, then trims out any old/stale stuff before this period after a
sv/commit ... its purpose is to give you a clearer take on ongoing events than
your summary often does." And: "I have never had to hand edit before at all."

HE WAS RIGHT THAT A SCRIPT GOVERNS IT AND WRONG THAT THE SCRIPT TRIMMED.
`_check_memory_index_size` is described in its own source as "the one RULING 7
check that can refuse a save", and `_audit_memory_index` carries "READS ONLY --
never writes under mem_dir". So the mechanism measured and refused; the trimming
was done BY HAND -- 2026-07-03 (26.3K to 17.6K, session entries into topic files)
and 2026-08-06 under his ruling 7 (24,268 to 21,456 chars). He never hand-edited
it because the assistant did it inside `sv`, which is exactly why it read as
automatic. Then 58 days passed with no trim, 2026-10-01 bought headroom by
GROUPING entries rather than archiving them, and the index reached 23,255 chars
against a 23,750 refuse line -- 495 characters and 5 lines of runway.

A manual step with no mechanism rots. `archive_stale_memory_entries` is the
mechanism, and these tests hold the four properties that make it safe to run
unattended: it ages only the dated session log, it never touches standing rules,
it never moves a line whose age is unknown, and it deletes nothing.
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

TODAY = date(2026, 10, 3)

INDEX = """# CDSFL — Persistent Memory Index

## Project State
- [Recent work](cdsfl_session_2026-10-01_thing.md) — inside the window.
- [Old work](cdsfl_session_2026-06-07_thing.md) — well outside the window.
- **Grouped** — [newest](cdsfl_session_2026-10-02_a.md); [oldest](cdsfl_session_2026-05-01_b.md)
- [Undated pointer](cdsfl_master_task_list_pointer.md) — no date anywhere in the name.

## Feedback (applies to all work)
- [No model voting](feedback_no_model_voting_2026-01-01.md) — ancient, and STANDING.
"""


@pytest.fixture()
def mem(tmp_path):
    d = tmp_path / "memory"
    d.mkdir()
    (d / "MEMORY.md").write_text(INDEX, encoding="utf-8")
    for name in ("cdsfl_session_2026-10-01_thing.md", "cdsfl_session_2026-06-07_thing.md",
                 "cdsfl_session_2026-10-02_a.md", "cdsfl_session_2026-05-01_b.md",
                 "cdsfl_master_task_list_pointer.md",
                 "feedback_no_model_voting_2026-01-01.md"):
        (d / name).write_text("x", encoding="utf-8")
    return d


class TestThePremiseIsAlive:
    def test_the_function_exists_and_the_window_is_a_real_number(self):
        assert hasattr(sv, "archive_stale_memory_entries")
        assert isinstance(sv._MEMORY_WINDOW_DAYS, int)
        assert sv._MEMORY_WINDOW_DAYS > 0

    def test_the_date_reader_finds_the_newest_date_not_the_first(self):
        line = "- [a](x_2026-05-01_a.md); [b](y_2026-10-02_b.md)"
        assert sv._memory_line_newest_date(line) == date(2026, 10, 2)

    def test_an_undated_line_reads_as_no_evidence_of_age(self):
        assert sv._memory_line_newest_date("- [a](plain_pointer.md)") is None

    def test_an_impossible_date_in_a_filename_is_not_a_date(self):
        assert sv._memory_line_newest_date("- [a](x_2026-13-45_a.md)") is None


class TestWhatMovesAndWhatDoesNot:
    def test_an_aged_session_entry_moves(self, mem):
        r = sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        assert r["ok"], r["reason"]
        out = (mem / "MEMORY.md").read_text()
        assert "cdsfl_session_2026-06-07_thing.md" not in out
        assert "cdsfl_session_2026-06-07_thing.md" in (mem / "MEMORY_ARCHIVE.md").read_text()

    def test_a_recent_entry_stays(self, mem):
        sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        assert "cdsfl_session_2026-10-01_thing.md" in (mem / "MEMORY.md").read_text()

    def test_a_grouped_line_stays_if_ANY_pointer_is_recent(self, mem):
        """Newest-date rule. A group holding one recent pointer is live."""
        sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        out = (mem / "MEMORY.md").read_text()
        assert "cdsfl_session_2026-05-01_b.md" in out, (
            "the 2026-05-01 pointer shares a line with a 2026-10-02 one, so the "
            "line is live and must not be archived"
        )

    def test_an_undated_entry_is_NEVER_moved(self, mem):
        r = sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        assert r["kept_undated"] >= 1
        assert "cdsfl_master_task_list_pointer.md" in (mem / "MEMORY.md").read_text()

    def test_standing_feedback_is_NEVER_moved_however_old(self, mem):
        """A rule that applies to all work does not become stale by the calendar.
        This entry is dated 2026-01-01 — 275 days old — and must stay."""
        sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        out = (mem / "MEMORY.md").read_text()
        assert "feedback_no_model_voting_2026-01-01.md" in out, (
            "a standing rule was archived because it was old; archiving "
            "feedback_no_model_voting would be a defect, not housekeeping"
        )
        assert "Feedback (applies to all work)" in out


class TestNothingIsLost:
    def test_every_moved_line_is_in_the_archive_verbatim(self, mem):
        before = (mem / "MEMORY.md").read_text()
        r = sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        arch = (mem / "MEMORY_ARCHIVE.md").read_text()
        for line in before.splitlines():
            if line.strip() and line not in (mem / "MEMORY.md").read_text():
                if line.startswith("-") or line.startswith("*"):
                    assert line in arch, f"line vanished entirely: {line[:60]}"
        assert r["moved"] >= 1

    def test_a_backup_of_the_index_is_written_before_any_change(self, mem):
        r = sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        assert r["backup"], "no backup path reported"
        b = pathlib.Path(r["backup"])
        assert b.is_file()
        assert "cdsfl_session_2026-06-07_thing.md" in b.read_text(), (
            "the backup must hold the PRE-change index"
        )

    def test_the_index_keeps_a_pointer_to_the_archive(self, mem):
        sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        assert "MEMORY_ARCHIVE.md" in (mem / "MEMORY.md").read_text(), (
            "a reader of the index must be able to find what left it"
        )

    def test_dry_run_writes_absolutely_nothing(self, mem):
        before = (mem / "MEMORY.md").read_bytes()
        r = sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30,
                                            dry_run=True)
        assert r["ok"] and r["moved"] >= 1
        assert (mem / "MEMORY.md").read_bytes() == before
        assert not (mem / "MEMORY_ARCHIVE.md").exists()

    def test_running_twice_is_idempotent(self, mem):
        sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        once = (mem / "MEMORY.md").read_text()
        r2 = sv.archive_stale_memory_entries(mem, today=TODAY, window_days=30)
        assert r2["moved"] == 0, "a second run moved more; the first was incomplete"
        assert (mem / "MEMORY.md").read_text() == once


class TestTheMutation:
    def test_a_window_wide_enough_moves_nothing(self, mem):
        """If the date filter were ignored, this would still move entries. It is
        the check that the filter is doing the work rather than the section."""
        r = sv.archive_stale_memory_entries(mem, today=TODAY, window_days=10_000)
        assert r["moved"] == 0, (
            "with a 10,000-day window nothing is older than the cutoff, so a "
            "non-zero move count means the date filter is not consulted"
        )

    def test_a_zero_day_window_moves_the_dated_session_lines_but_still_not_the_rest(self, mem):
        """The complement: the filter is live in both directions, and the
        section and undated guards hold independently of it."""
        r = sv.archive_stale_memory_entries(mem, today=TODAY, window_days=0)
        out = (mem / "MEMORY.md").read_text()
        assert r["moved"] >= 2
        assert "feedback_no_model_voting_2026-01-01.md" in out
        assert "cdsfl_master_task_list_pointer.md" in out
