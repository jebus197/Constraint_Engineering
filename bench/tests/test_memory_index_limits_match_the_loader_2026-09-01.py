"""The index guard must measure the index the way the loader actually does.

The guard refuses a save when MEMORY.md is close to being truncated. It is
therefore only as good as its model of the loader, and that model was wrong in
three ways at once until 2026-09-01:

  * it knew ONE of the loader's two truncation triggers. The loader cuts on
    character count OR line count; the guard watched characters only, so a save
    could pass every check while the index was being cut on lines.
  * it measured untrimmed Python code points. The loader trims first and counts
    UTF-16 code units. On this file the three candidate units span 24,451 UTF-8
    bytes to 24,040 code points, so the unit is not a detail.
  * its stated reason was falsified: truncation is announced by the loader, and
    the tail it drops on this index is the oldest archival material, not the
    newest entries.

These tests read the constants out of the installed binary rather than
restating them, so a version bump that moves a limit fails here instead of
silently making the guard wrong again.
"""
from __future__ import annotations

import mmap
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import cdsfl_sv as sv  # noqa: E402

_BINARY = Path("/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code"
               "/bin/claude.exe")


def _constant(pattern: str) -> int | None:
    """Read one `name=<digits>` constant out of the installed binary."""
    if not _BINARY.is_file():
        return None
    with _BINARY.open("rb") as fh:
        with mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            m = re.search(pattern.encode(), mm)
            return int(m.group(1)) if m else None


class TestTheConstantsComeFromTheLoaderNotFromMemory:

    def test_the_character_limit_matches_the_binary(self):
        found = _constant(r"PRe=(\d+)")
        if found is None:
            pytest.skip(f"claude binary not readable at {_BINARY}")
        assert found == sv._MEMORY_INDEX_LIMIT_CHARS, (
            f"the loader's character limit is {found}, the guard uses "
            f"{sv._MEMORY_INDEX_LIMIT_CHARS}. The guard is now measuring "
            f"against a limit that does not exist.")

    def test_the_line_limit_matches_the_binary(self):
        found = _constant(r"fie=(\d+)")
        if found is None:
            pytest.skip(f"claude binary not readable at {_BINARY}")
        assert found == sv._MEMORY_INDEX_LIMIT_LINES, (
            f"the loader's line limit is {found}, the guard uses "
            f"{sv._MEMORY_INDEX_LIMIT_LINES}.")


class TestTheMeasurementMirrorsEDt:
    """EDt: t = e.trim(); lineCount = count('\\n', t) + 1; byteCount = t.length"""

    def _edt(self, text: str) -> tuple[int, int]:
        t = text.strip()
        utf16 = sum(2 if ord(c) > 0xFFFF else 1 for c in t)
        return utf16, (t.count("\n") + 1 if t else 0)

    def _audit(self, memory_dir: Path, body: str):
        (memory_dir / "MEMORY.md").write_text(body, encoding="utf-8")
        return sv._audit_memory_index(memory_dir)

    @pytest.mark.parametrize("body", [
        "- [A](a.md) — hook\n",
        "\n\n- [A](a.md) — hook\n\n\n",             # trimming matters
        "- [A](a.md) — ★ γ — em dash\n",            # multi-byte, single UTF-16
        "- [A](a.md) — 🧬 astral\n",                 # surrogate pair: 2 units
        "x" * 300 + "\n",
    ])
    def test_chars_and_lines_agree_with_the_loader(self, tmp_path, body):
        audit = self._audit(tmp_path, body)
        want_chars, want_lines = self._edt(body)
        assert audit.chars == want_chars, f"chars disagree on {body!r}"
        assert audit.lines == want_lines, f"lines disagree on {body!r}"

    def test_an_astral_character_costs_two_units_not_one(self, tmp_path):
        """Python len() would say 1. The loader counts 2. That gap is the bug
        this measurement exists to avoid."""
        audit = self._audit(tmp_path, "🧬")
        assert audit.chars == 2
        assert len("🧬") == 1

    def test_trailing_blank_lines_are_not_counted(self, tmp_path):
        tight = self._audit(tmp_path, "- [A](a.md)\n")
        padded = self._audit(tmp_path, "- [A](a.md)\n\n\n\n\n")
        assert tight.chars == padded.chars
        assert tight.lines == padded.lines


class TestTheLineLimitCanRefuseOnItsOwn:

    def test_a_short_but_long_lined_index_is_refused(self, tmp_path):
        """The case the guard could not see: far under the character limit,
        over the line limit."""
        body = "".join(f"- [E{i}](f{i}.md)\n" for i in range(199))
        (tmp_path / "MEMORY.md").write_text(body, encoding="utf-8")
        audit = sv._audit_memory_index(tmp_path)
        assert audit.chars < sv._MEMORY_INDEX_LIMIT_CHARS * 0.5, (
            "fixture is not testing the line limit in isolation")
        check = sv._check_memory_index_size(audit)
        assert check.passed is False
        assert "line" in check.observed.lower()

    def test_a_small_index_still_passes(self, tmp_path):
        (tmp_path / "MEMORY.md").write_text("- [A](a.md) — hook\n",
                                            encoding="utf-8")
        check = sv._check_memory_index_size(sv._audit_memory_index(tmp_path))
        assert check.passed is True
        assert "lines" in check.observed


class TestTheRationaleStatesWhatTheLoaderDoes:

    def test_the_falsified_claims_are_not_reintroduced(self, tmp_path):
        body = "x" * int(sv._MEMORY_INDEX_LIMIT_CHARS
                         * sv._MEMORY_INDEX_REFUSE_FRACTION)
        (tmp_path / "MEMORY.md").write_text(body, encoding="utf-8")
        why = sv._check_memory_index_size(sv._audit_memory_index(tmp_path)).why
        # Assert the CLAIMS are absent, not the words. The current text says
        # "housekeeping rather than silent loss" -- it uses "silent" precisely
        # in order to deny it, and a bare substring test failed on that,
        # which is how this assertion got sharpened.
        low = " ".join(why.lower().split())
        for claim in ("truncated silently", "silently truncated",
                      "newest entries", "nothing reports"):
            assert claim not in low, (
                f"the falsified claim {claim!r} is back in the rationale. "
                f"Measured 2026-09-01: the loader announces truncation, and "
                f"the tail it drops on this index is the March 2026 handoffs, "
                f"the oldest material in the file.")
        assert "announced" in low or "announces" in low, (
            "the rationale should say the loader announces truncation, since "
            "that is what makes this housekeeping rather than silent loss")


class TestBoldTitlesAreEntriesToo:
    """The audit's own blind spot, 2026-09-01.

    _MEMORY_ENTRY_RE required "[" to follow the bullet directly, so every entry
    written `- **[Title](file.md)**` was invisible to it. On the live index that
    was 15 of 132 entries (11.4%, Wilson [7.0%, 17.9%]) -- and all 15 were over
    the 150-character rule, carrying 4,050 characters of excess against 1,135 in
    the entries the audit could see. The check for over-long entries could not
    see the longest entries in the file, which were also the newest, because a
    session note reaches for bold to mark itself important.
    """

    def _audit(self, tmp_path, body):
        (tmp_path / "MEMORY.md").write_text(body, encoding="utf-8")
        return sv._audit_memory_index(tmp_path)

    def test_a_bold_titled_entry_is_counted(self, tmp_path):
        (tmp_path / "a.md").write_text("body\n")
        audit = self._audit(tmp_path, "- **[Bold](a.md)** — hook\n")
        assert len(audit.entries) == 1, (
            "an entry with a bold title was not counted as an entry")

    def test_plain_and_bold_are_counted_together(self, tmp_path):
        for n in ("a.md", "b.md"):
            (tmp_path / n).write_text("body\n")
        audit = self._audit(
            tmp_path, "- [Plain](a.md) — hook\n- **[Bold](b.md)** — hook\n")
        assert len(audit.entries) == 2
        assert {t for _title, t, _n in audit.entries} == {"a.md", "b.md"}

    def test_an_over_long_bold_entry_is_reported(self, tmp_path):
        (tmp_path / "a.md").write_text("body\n")
        line = "- **[Bold](a.md)** — " + "x" * 200
        audit = self._audit(tmp_path, line + "\n")
        assert audit.over_long, (
            "a bold-titled entry over 150 chars was not reported. This is the "
            "exact case that hid the five longest entries in the live index.")

    def test_a_bold_entrys_broken_link_is_detected(self, tmp_path):
        audit = self._audit(tmp_path, "- **[Bold](missing.md)** — hook\n")
        assert audit.broken == ["missing.md"], (
            "a bold-titled entry pointing at a missing file was not flagged")

    def test_the_live_index_has_no_over_long_entries(self):
        """Trimmed 2026-09-01: 40 entries rewritten, 24,040 -> 18,239 chars."""
        audit = sv._audit_memory_index(sv._MEMORY_DIR)
        if audit.error:
            pytest.skip(audit.error)
        assert not audit.over_long, (
            f"{len(audit.over_long)} entries exceed the 150-character rule: "
            + ", ".join(t for _n, t in audit.over_long[:5]))
