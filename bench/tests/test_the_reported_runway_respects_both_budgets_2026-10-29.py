"""The index has 2 truncation budgets and the reported runway must honour both.

WHY THIS FILE EXISTS. The loader truncates the memory index on EITHER too many
characters (PRe=25000) or too many lines (fie=200) -- both read out of the
installed binary, not assumed. `_MemoryIndexAudit.entries_left` divided the
CHARACTER headroom by the median entry size and ignored lines entirely, so on
2026-10-29 it reported **34 entries of runway where the binding line budget
allowed 11**, and `sv` itself would refuse the next save after **1**. The
property's own docstring already said an entry costs a line; only the
arithmetic disagreed.

THE OLD ASSERTION PINNED THE DEFECT. `test_sv_rulings.py` asserted
`entries_left == headroom // (median_entry + 1)` -- the chars-only formula
itself -- so a test existed over this property and could not tell the correct
answer from the wrong one. That assertion now holds the 2 bounds instead. This
file adds the cases that DISCRIMINATE: 1 index where characters bind and 1
where lines bind, each asserted to return its own binding budget and not the
other. Under the old formula the line-bound case returns 463 against a correct
50, so reverting it turns this file red.

THE GROUPING HALF. The trim that exists could free nothing on that date --
"nothing older than 30 days in Project State" -- and 116 of 149 entry-lines
(77.8523%) are beyond its reach at all, `Feedback` alone holding 78 that age
by design never. `group_dated_index_entries` merges same-date `Project State`
lines, which is the key the index already groups on, and is held here to lose
no pointer, to respect section boundaries, and to write nothing on a dry run.

Producer for every figure above:
scripts/the_line_budget_is_the_binding_one_2026-10-29.py
"""
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "cdsfl_sv", REPO / "scripts" / "cdsfl_sv.py")
sv = importlib.util.module_from_spec(_spec)
sys.modules["cdsfl_sv"] = sv           # the dataclasses need it registered
_spec.loader.exec_module(sv)


@pytest.fixture()
def mem(tmp_path: Path) -> Path:
    d = tmp_path / "memory"
    d.mkdir()
    return d


def _write(mem: Path, body: str) -> None:
    (mem / "MEMORY.md").write_text(body, encoding="utf-8")


def _entries(n: int, pad: int) -> str:
    """n pointer lines, each padded so the median entry length is tunable."""
    return "".join(
        f"- [Entry {i}](file_{i}.md) — {'x' * pad}\n" for i in range(n))


def _bounds(audit) -> tuple[int, int]:
    return (max(0, audit.headroom) // (audit.median_entry + 1),
            max(0, audit.lines_headroom))


class TestWhicheverBudgetBindsIsTheOneReported:
    """Both cases are DISCRIMINATING: the 2 bounds differ by design, so a
    formula using the wrong one gives a visibly wrong answer. Two fixtures
    that happened to agree would pass under either formula and prove nothing,
    which is how 2 vacuous fixtures reached this suite on 2026-10-28."""

    def test_when_lines_bind_the_line_budget_is_reported(self, mem: Path):
        _write(mem, _entries(150, 10))          # many short lines
        a = sv._audit_memory_index(mem)
        by_chars, by_lines = _bounds(a)
        assert by_lines < by_chars, (
            f"fixture is not discriminating: chars {by_chars}, lines {by_lines}")
        assert a.entries_left == by_lines
        assert a.entries_left != by_chars

    def test_when_chars_bind_the_char_budget_is_reported(self, mem: Path):
        _write(mem, _entries(20, 1000))         # few very long lines
        a = sv._audit_memory_index(mem)
        by_chars, by_lines = _bounds(a)
        assert by_chars < by_lines, (
            f"fixture is not discriminating: chars {by_chars}, lines {by_lines}")
        assert a.entries_left == by_chars
        assert a.entries_left != by_lines

    @pytest.mark.parametrize("n,pad", [(5, 10), (50, 20), (150, 10), (20, 900),
                                       (190, 5), (10, 2000)])
    def test_it_never_exceeds_either_budget(self, mem: Path, n: int, pad: int):
        _write(mem, _entries(n, pad))
        a = sv._audit_memory_index(mem)
        by_chars, by_lines = _bounds(a)
        assert a.entries_left <= by_chars
        assert a.entries_left <= by_lines
        assert a.entries_left == min(by_chars, by_lines)

    def test_an_unparseable_index_still_reports_unknown(self, mem: Path):
        _write(mem, "no pointers here at all\n")
        assert sv._audit_memory_index(mem).entries_left == -1

    def test_the_live_index_is_not_overstated(self):
        """The regression was LIVE, so the live file is held too. Skips
        rather than fails where the real memory directory is absent, because
        a checkout on another machine must not fail on its absence."""
        if not (sv._MEMORY_DIR / sv._MEMORY_INDEX_NAME).is_file():
            pytest.skip("no live memory index on this machine")
        a = sv._audit_memory_index(sv._MEMORY_DIR)
        by_chars, by_lines = _bounds(a)
        assert a.entries_left <= by_lines, (
            f"reported {a.entries_left} entries of runway against a line "
            f"budget of {by_lines}: the loader truncates on lines too")
        assert a.entries_left == min(by_chars, by_lines)


class TestGroupingFreesLinesAndLosesNothing:
    HEAD = "# Index\n\n## Project State\n"

    def _dated(self, *pairs: tuple[str, int], mem: Path | None = None) -> str:
        """Index body, and -- given `mem` -- the files it points at.

        Creating the targets matters: `broken` means "linked from the index,
        absent from disk", so a fixture that writes no files reports every
        pointer broken and an assertion of `broken == []` fails for a reason
        that has nothing to do with grouping. Caught by running it.
        """
        body = "".join(
            f"- **{d} Oct** — [E{i}](f_{d}_{i}.md) — note {i}\n"
            for d, n in pairs for i in range(n))
        if mem is not None:
            for d, n in pairs:
                for i in range(n):
                    (mem / f"f_{d}_{i}.md").write_text("body\n", encoding="utf-8")
        return body

    def test_same_date_lines_merge_and_free_lines(self, mem: Path):
        _write(mem, self.HEAD + self._dated(("17", 3), ("16", 2), ("15", 1), mem=mem))
        before = sv._audit_memory_index(mem)
        r = sv.group_dated_index_entries(mem)
        after = sv._audit_memory_index(mem)
        assert r["ok"] and r["merged"] == 3          # 2 from the 17th, 1 from the 16th
        assert after.lines == before.lines - 3
        assert r["freed_lines"] == 3
        assert len(after.entries) == len(before.entries)   # every pointer survives
        assert after.broken == before.broken == [], (
            "grouping must not change which pointers resolve")

    def test_it_does_not_merge_across_a_section_boundary(self, mem: Path):
        _write(mem, self.HEAD + self._dated(("17", 1))
               + "\n## Feedback (applies to all work)\n"
               + "- **17 Oct** — [Other](other.md) — a feedback entry\n")
        r = sv.group_dated_index_entries(mem)
        body = (mem / "MEMORY.md").read_text(encoding="utf-8")
        assert r["merged"] == 0, "a date shared across 2 sections must not merge"
        assert "## Feedback (applies to all work)\n- **17 Oct**" in body

    def test_only_the_groupable_section_is_touched(self, mem: Path):
        """Feedback carries no dates today, but the section guard must hold
        even when it does -- otherwise standing guidance gets reordered."""
        _write(mem, "# Index\n\n## Feedback (applies to all work)\n"
               + self._dated(("17", 3)))
        r = sv.group_dated_index_entries(mem)
        assert r["merged"] == 0
        assert r["ok"] and "share a date" in r["reason"]

    def test_a_dry_run_writes_nothing(self, mem: Path):
        _write(mem, self.HEAD + self._dated(("17", 3)))
        original = (mem / "MEMORY.md").read_text(encoding="utf-8")
        r = sv.group_dated_index_entries(mem, dry_run=True)
        assert r["ok"] and r["merged"] == 2
        assert (mem / "MEMORY.md").read_text(encoding="utf-8") == original
        assert not list(mem.glob("MEMORY.backup-*.md"))

    def test_a_real_run_backs_the_index_up_first(self, mem: Path):
        _write(mem, self.HEAD + self._dated(("17", 3)))
        original = (mem / "MEMORY.md").read_text(encoding="utf-8")
        r = sv.group_dated_index_entries(mem)
        assert r["backup"], "no backup recorded"
        assert (mem / r["backup"]).read_text(encoding="utf-8") == original

    def test_it_is_idempotent(self, mem: Path):
        _write(mem, self.HEAD + self._dated(("17", 3), ("16", 2)))
        first = sv.group_dated_index_entries(mem)
        body = (mem / "MEMORY.md").read_text(encoding="utf-8")
        second = sv.group_dated_index_entries(mem)
        assert first["merged"] == 3 and second["merged"] == 0
        assert (mem / "MEMORY.md").read_text(encoding="utf-8") == body

    def test_a_merge_that_would_lose_a_pointer_is_REFUSED(
            self, mem: Path, monkeypatch: pytest.MonkeyPatch):
        """THE POINTER CHECK IS REACHABLE, which is why it is here.

        By construction today's merge cannot drop a pointer, so a check
        against it would be an assertion nothing can reach -- the defect
        already recorded as `pf:b0d8ca44a450`. It guards a FUTURE change to
        the pattern or the join, and this case makes that path execute: the
        pattern is replaced with one whose second group omits the pointer,
        so merging really does lose it and the write must be refused.
        """
        import re as _re
        _write(mem, self.HEAD + self._dated(("17", 3)))
        original = (mem / "MEMORY.md").read_text(encoding="utf-8")
        monkeypatch.setattr(
            sv, "_MEMORY_DATED_ENTRY",
            _re.compile(r'^- \*\*(\d{1,2} \w+(?: [AP]M)?)\*\* — .*?(note \d+)$'))
        r = sv.group_dated_index_entries(mem)
        assert r["ok"] is False
        assert "REFUSED" in r["reason"]
        assert (mem / "MEMORY.md").read_text(encoding="utf-8") == original, (
            "the index was written despite losing a pointer")

    def test_a_missing_index_is_reported_not_raised(self, mem: Path):
        r = sv.group_dated_index_entries(mem)
        assert r["ok"] is False and "no index" in r["reason"]


class TestAnIndexBackupIsNotAnUnreachableMemory:
    """A backup is a copy of the index, not a memory, and cannot be pointed at.

    Until 2026-10-29 the orphan scan subtracted only `MEMORY.md`, so every
    timestamped backup was reported as a memory appearing nowhere in the
    index -- 3 of the 12 orphans on the live directory that day were backups.
    `group_dated_index_entries` writes one on every run that merges, so the
    report would have degraded as the mechanism did its job.
    """

    def test_a_backup_is_not_reported_as_an_orphan(self, mem: Path):
        _write(mem, "# Index\n\n## Project State\n- [E](real.md) — note\n")
        (mem / "real.md").write_text("body\n", encoding="utf-8")
        (mem / "MEMORY.backup-20261029T070000.md").write_text("old\n", encoding="utf-8")
        a = sv._audit_memory_index(mem)
        assert a.orphans_unmentioned == []
        assert a.orphans_mentioned == []

    def test_a_genuine_orphan_is_still_reported(self, mem: Path):
        """The exclusion must not silence the check it narrows."""
        _write(mem, "# Index\n\n## Project State\n- [E](real.md) — note\n")
        (mem / "real.md").write_text("body\n", encoding="utf-8")
        (mem / "MEMORY.backup-20261029T070000.md").write_text("old\n", encoding="utf-8")
        (mem / "genuinely_unreachable.md").write_text("body\n", encoding="utf-8")
        a = sv._audit_memory_index(mem)
        assert a.orphans_unmentioned == ["genuinely_unreachable.md"]

    def test_grouping_does_not_create_an_orphan(self, mem: Path):
        """End to end: the mechanism runs, writes a backup, and the report
        it leaves behind is as clean as the one it started from."""
        body = ("# Index\n\n## Project State\n"
                + "".join(f"- **17 Oct** — [E{i}](f_{i}.md) — note {i}\n" for i in range(3)))
        _write(mem, body)
        for i in range(3):
            (mem / f"f_{i}.md").write_text("body\n", encoding="utf-8")
        before = sv._audit_memory_index(mem)
        r = sv.group_dated_index_entries(mem)
        after = sv._audit_memory_index(mem)
        assert r["ok"] and r["merged"] == 2 and r["backup"]
        assert (mem / r["backup"]).is_file(), "the backup was not written"
        assert after.orphans_unmentioned == before.orphans_unmentioned == []
