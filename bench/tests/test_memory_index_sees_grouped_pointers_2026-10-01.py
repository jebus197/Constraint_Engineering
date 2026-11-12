"""The memory-index audit must see every pointer, including grouped ones.

THE BLIND SPOT RECURRED IN A SECOND FORM, 2026-10-01. The 2026-09-01 repair
taught `_MEMORY_ENTRY_RE` about `- **[Title](file.md)**`. A GROUPED line --
`- **1 Oct 2026** - [A](a.md) gloss; [B](b.md) gloss` -- still matched nothing,
because `.match()` requires the link to follow the bullet directly. Measured on
the live index: 22 of 161 pointers invisible, 13.6646%, Wilson 95%
[9.2001%, 19.8226%] (statsmodels and mpmath agreeing), across 5 lines.

THREE HOLES, and only the first was visible:
  1. Those 22 files were reported as orphans, "name appears in the index text,
     but not as an entry". Cosmetic.
  2. `broken` could not see them, so a grouped line could point at a DELETED
     memory file in silence. NOT cosmetic.
  3. `over_long` could not see them, so a grouped line could carry unbounded
     prose and evade the rule that REFUSES the save.

THE UNIT IS THE POINTER, AND THAT CHOICE IS THE WHOLE FIX. All 5 grouped lines
run 159 to 655 characters, so charging the line to each pointer would put 5 of
5 over the 150-character limit and refuse EVERY future save. Charging each
pointer its own span gives 22 of 22 under, longest 137. The shared preamble is
measured in its own right, because charging it to the first pointer made `31st`
read 156 characters -- 125 of its own prose plus 31 of a heading shared by 4
pointers -- and charging it to nobody would let a preamble grow unmeasured.

These tests CALL the audit. A test asserting on its source text would only
confirm the module describes itself consistently.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SV = ROOT / "scripts" / "cdsfl_sv.py"


@pytest.fixture(scope="module")
def sv():
    spec = importlib.util.spec_from_file_location("cdsfl_sv_probe", SV)
    m = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_sv_probe"] = m        # dataclass needs it registered
    spec.loader.exec_module(m)
    return m


def _index(tmp_path: Path, body: str) -> Path:
    (tmp_path / "MEMORY.md").write_text(body, encoding="utf-8")
    return tmp_path


class TestGroupedPointersAreSeen:

    def test_a_grouped_line_yields_one_pointer_per_link(self, sv):
        line = "- **1 Oct 2026** — [A](a.md) first; [B](b.md) second; [C](c.md) third"
        got = sv._memory_index_pointers(line)
        assert [p[1] for p in got] == ["a.md", "b.md", "c.md"]

    def test_a_broken_link_on_a_grouped_line_is_detected(self, sv, tmp_path):
        """HOLE 2, the one that was silent. This is the point of the fix."""
        d = _index(tmp_path, "# i\n\n- **1 Oct** — [A](real.md) s; [B](gone.md) s\n")
        (d / "real.md").write_text("x", encoding="utf-8")
        assert sv._audit_memory_index(d).broken == ["gone.md"]

    def test_a_grouped_target_is_not_reported_as_an_orphan(self, sv, tmp_path):
        """HOLE 1, the visible symptom the founder asked about."""
        d = _index(tmp_path, "# i\n\n- **1 Oct** — [A](a.md) s; [B](b.md) s\n")
        for n in ("a.md", "b.md"):
            (d / n).write_text("x", encoding="utf-8")
        audit = sv._audit_memory_index(d)
        assert audit.orphans_mentioned == [] and audit.orphans_unmentioned == []

    def test_a_bloated_pointer_on_a_grouped_line_still_refuses_the_save(self, sv, tmp_path):
        """HOLE 3. The rule must still bite, or this is an exemption not a fix."""
        long = "x" * 200
        d = _index(tmp_path, f"# i\n\n- **1 Oct** — [A](a.md) {long}; [B](b.md) s\n")
        for n in ("a.md", "b.md"):
            (d / n).write_text("x", encoding="utf-8")
        check = sv._check_memory_index_size(sv._audit_memory_index(d))
        assert check.passed is False
        assert check.name == "memory-index-entries-are-one-line"

    def test_an_unbounded_group_preamble_still_refuses_the_save(self, sv, tmp_path):
        d = _index(tmp_path, "# i\n\n- **" + "P" * 200 + "** — [A](a.md) s; [B](b.md) s\n")
        for n in ("a.md", "b.md"):
            (d / n).write_text("x", encoding="utf-8")
        audit = sv._audit_memory_index(d)
        assert audit.over_long == [], "the pointers must not be blamed for shared text"
        assert len(audit.over_long_preambles) == 1
        assert sv._check_memory_index_size(audit).passed is False

    def test_a_short_preamble_does_not_push_its_first_pointer_over(self, sv):
        """THE REGRESSION THE FIRST VERSION OF THIS FIX CAUSED, guarded."""
        line = "- **Late Aug 2026 sessions** — [31st](f.md) " + "y" * 80 + "; [30th](g.md) s"
        got = sv._memory_index_pointers(line)
        assert all(p[2] <= sv._MEMORY_ENTRY_ONE_LINE_CHARS for p in got), (
            f"a pointer was charged the shared heading: {[(p[0], p[2]) for p in got]}")


class TestNothingElseMoved:
    """The 2026-09-01 behaviour must be unchanged, or this is not additive."""

    def test_a_single_pointer_line_is_still_charged_the_whole_line(self, sv):
        line = "- **[Title](f.md)** — a gloss that counts toward the limit."
        assert sv._memory_index_pointers(line)[0][2] == len(line)

    def test_a_long_single_pointer_line_still_refuses(self, sv, tmp_path):
        d = _index(tmp_path, "# i\n\n- **[T](a.md)** — " + "y" * 200 + "\n")
        (d / "a.md").write_text("x", encoding="utf-8")
        assert sv._check_memory_index_size(sv._audit_memory_index(d)).passed is False

    def test_a_single_pointer_line_yields_no_preamble_item(self, sv):
        assert sv._memory_index_group_preamble("- **[T](f.md)** — g.") is None

    @pytest.mark.parametrize("line", [
        "## A heading", "prose carrying [a](b.md) outside any list",
        "- a bullet with no link at all", "", "   ",
    ])
    def test_non_entries_yield_nothing(self, sv, line):
        assert sv._memory_index_pointers(line) == []
        assert sv._memory_index_group_preamble(line) is None


class TestTheLiveIndexPassesUnderTheNewUnit:
    """If the live index fails, every sv is blocked — so this is load-bearing."""

    @pytest.fixture
    def audit(self, sv):
        if not sv._MEMORY_DIR.is_dir():
            pytest.skip("no persistent-memory folder on this machine")
        return sv._audit_memory_index(sv._MEMORY_DIR)

    def test_the_one_line_rule_passes(self, audit):
        assert audit.over_long == [], (
            f"the live index would refuse every save: {audit.over_long[:3]}")
        assert audit.over_long_preambles == []

    def test_every_pointer_on_a_grouped_line_resolves(self, audit):
        assert audit.broken == []

    def test_the_audit_now_sees_more_pointers_than_the_old_regex_could(self, sv, audit):
        text = (sv._MEMORY_DIR / "MEMORY.md").read_text(encoding="utf-8")
        old = sum(1 for ln in text.splitlines() if sv._MEMORY_ENTRY_RE.match(ln))
        assert len(audit.entries) >= old, "the fix lost pointers it used to see"
        if len(audit.entries) == old:
            pytest.skip("this index currently has no grouped lines to find")
        assert len(audit.entries) > old


class TestAnInteriorHeadingIsNotChargedToItsNeighbour:
    """★ THE 4TH SHAPE OF ONE RECURRING BLIND SPOT, closed 2026-11-12.

    `_memory_index_group_preamble` already records the principle: "charging
    shared text to one pointer makes the longest pointer an artefact of where it
    sits in the line." That fix covered a heading at the START of a line. The
    Feedback grouper also merges groups so a heading lands in the MIDDLE, and
    that case was never covered.

    MEASURED ON THE SAVE THIS CLOSED. The entry "3 failed predicates means STOP"
    was charged 186 characters against a 150 limit, of which its own link and
    hook are 143 and the remaining 43 are a heading shared by the 38 pointers
    after it. 15 other entries on that line were genuinely over and were
    shortened; this 1 was an artefact, and shortening it enough would have meant
    DELETING its hook to satisfy a measure that was wrong.

    SPLITTING THE LINE WAS TRIED FIRST AND DOES NOT WORK: the grouper re-merges
    separate lines that share a heading, so a split is undone on the next save.

    AND THE HEADING IS NOT MEASURED BY NOTHING, which the preamble docstring
    names as the opposite error. `test_an_over_long_interior_heading_IS_caught`
    is what holds that half.
    """

    HEAD = "**MY INSTRUMENTS ARE THE WEAK POINT.**"

    def test_the_heading_is_not_charged_to_the_pointer_before_it(self, sv):
        line = f"- [a]({'a'*8}.md) a hook · {self.HEAD} · [b]({'b'*8}.md) a hook"
        charged = {t: n for _ti, t, n in sv._memory_index_pointers(line)}
        bare = "- [a](" + "a"*8 + ".md) a hook"
        bare_charged = {t: n for _ti, t, n in sv._memory_index_pointers(bare)}
        assert charged[f"{'a'*8}.md"] <= bare_charged[f"{'a'*8}.md"] + 2, (
            f"the heading is still charged to the preceding pointer: "
            f"{charged} against {bare_charged}")

    def test_a_pointer_genuinely_over_the_limit_is_STILL_caught(self, sv):
        """★ THE FALSIFIER. A change that simply stopped measuring would pass
        every other test here while removing the check entirely."""
        line = "- [x](x.md) " + "y" * 200
        assert any(n > sv._MEMORY_ENTRY_ONE_LINE_CHARS
                   for _t, _g, n in sv._memory_index_pointers(line))

    def test_an_over_long_interior_heading_IS_caught(self, sv):
        line = f"- [x](x.md) hook · **{'H'*200}** · [y](y.md) hook"
        assert any(n > sv._MEMORY_ENTRY_ONE_LINE_CHARS
                   for _l, n in sv._memory_index_interior_headings(line)), (
            "an interior heading is now measured by nothing, which the preamble "
            "docstring names as the opposite error")

    def test_the_lines_own_leading_heading_is_not_double_counted(self, sv):
        """It belongs to the preamble measure; counting it here too would hold
        one span to the limit twice and report it as 2 faults."""
        line = f"- {self.HEAD} · [a](a.md) hook"
        assert sv._memory_index_interior_headings(line) == [], \
            sv._memory_index_interior_headings(line)

    def test_the_live_index_has_no_over_long_entry_or_heading(self, sv):
        """Not vacuous: this failed at 16 entries, then at 1, before the fix."""
        import pathlib
        idx = pathlib.Path.home() / ".claude" / "projects" \
            / "-Users-georgejackson-Developer-Projects" / "memory" / "MEMORY.md"
        if not idx.is_file():
            import pytest
            pytest.skip("the private memory index is not readable here")
        lim = sv._MEMORY_ENTRY_ONE_LINE_CHARS
        bad = []
        for ln in idx.read_text(encoding="utf-8", errors="replace").splitlines():
            bad += [f"entry {t} at {n}" for _ti, t, n
                    in sv._memory_index_pointers(ln) if n > lim]
            bad += [f"heading {l!r} at {n}" for l, n
                    in sv._memory_index_interior_headings(ln) if n > lim]
        assert not bad, "over the one-line limit:\n  " + "\n  ".join(bad)
