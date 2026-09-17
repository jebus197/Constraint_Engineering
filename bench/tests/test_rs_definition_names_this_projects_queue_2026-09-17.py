"""Task 8.1: the `rs` definition names this project's real queue.

WHY THIS FILE EXISTS. Task 8.1 named `bench/tests/test_operational_scripts.py`
as its evidence. That file never mentions `SHORTCUTS.md`, `RECOVERY.md`,
`ACTION_QUEUE` or `QWERTY`, and no file under `bench/tests` named
`SHORTCUTS.md`, so reverting the sweep would have left the suite green. This
file asserts on the committed bytes the entry actually changed (commit
`dd297ec`).

DELIBERATELY NOT ASSERTED: that `ACTION_QUEUE.md` or `QWERTY_CHECKPOINT.md` are
absent from the row. They legitimately appear inside the amendment clause that
explains why they were replaced.

DELIBERATELY NOT READ: the global `~/.claude/CLAUDE.md`, which carries the other
half of 8.1. It lives outside this repository and on 1 machine, so a test on it
would pass there and skip or fail everywhere else. The task list records that
half instead, and `test_out_of_tree_records_are_committed_here_2026-09-11.py`
holds the record.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"

RS_ROW = re.compile(r"\|\s*`rs`\s*\|")


def _rs_rows(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if RS_ROW.match(ln)]


def _rs_row() -> str:
    rows = _rs_rows((RESOURCES / "SHORTCUTS.md").read_text(encoding="utf-8"))
    assert len(rows) == 1, f"expected exactly 1 `rs` row in SHORTCUTS.md, found {len(rows)}"
    return rows[0]


def _resolution_paragraph() -> str:
    text = (RESOURCES / "RECOVERY.md").read_text(encoding="utf-8")
    hits = [p for p in text.split("\n\n")
            if re.search(r"RESOLVED 2026-09-09 \(task 8\.1\)", p)]
    assert len(hits) == 1, (
        f"expected exactly 1 RECOVERY.md paragraph recording the 8.1 resolution, "
        f"found {len(hits)}")
    return hits[0]


class TestTheRsRowNamesTheRealQueue:
    def test_the_row_routes_through_the_real_queue(self):
        row = _rs_row()
        for real in ("experimental_notes/OUTSTANDING_QUEUE_to_BR2.md",
                     "experimental_notes/CDSFL_MASTER_TASK_LIST.md"):
            assert real in row, (
                f"the `rs` row no longer names {real}; the 8.1 sweep has regressed")

    def test_the_row_carries_the_amendment_and_its_provenance(self):
        row = _rs_row()
        assert "Amended 2026-09-09" in row, (
            "the amendment clause is gone, so the row no longer says why the "
            "generic names were replaced")
        assert "Project_Genesis" in row, (
            "the row no longer records where the absent artefacts come from")


class TestRecoveryRecordsTheResolution:
    def test_the_resolution_paragraph_says_project_conditional(self):
        para = _resolution_paragraph()
        assert "PROJECT-CONDITIONAL" in para, (
            "the 8.1 resolution no longer says the global definition became "
            "project-conditional")
        assert "experimental_notes/OUTSTANDING_QUEUE_to_BR2.md" in para


class TestTheRowMatcherCanFail:
    """Positive control on synthetic text, so the matcher is shown to discriminate."""

    def test_a_reverted_row_lacks_what_the_live_row_has(self):
        reverted = "| `rs` | Restore state — action queue + checkpoints |"
        rows = _rs_rows(reverted)
        assert len(rows) == 1
        assert "experimental_notes/OUTSTANDING_QUEUE_to_BR2.md" not in rows[0]
        assert "Amended 2026-09-09" not in rows[0]

    def test_a_duplicated_row_is_counted(self):
        assert len(_rs_rows("| `rs` | a |\n| `rs` | b |\n| `rt` | c |")) == 2
