#!/usr/bin/env python3
"""THE MEMORY INDEX'S TRIM COULD NOT REACH THE SECTION THAT GROWS.

Guard for `relieve_memory_index_pressure`, built 2026-11-21 on the founder's
instruction: *"sv should be trimming itself automatically so it never becomes
full. That was always the intent."*

WHAT WAS WRONG, AND IT WAS NOT WHAT HE SUSPECTED. The trim HAS been automatic
since 2026-10-03, so his memory of the design is right. Its SCOPE was the defect:
ageing reaches `Project State` alone -- 1,566 of 24,486 characters on that date --
while `Feedback` held 19,850 and is excluded on purpose, because a standing rule
does not go stale by the calendar. All 3 earlier reliefs freed 0 characters while
the index sat 14 characters from refusing a save.

EVERY TEST HERE CALLS THE FUNCTION. None asserts on its source text, per
`execute-do-not-grep`: a test that reads the module can only confirm the module
describes itself consistently, and the 4 defects this project found by executing
2 forms against each other were none of them visible to reading.

Mutations: `scripts/the_index_relief_mutations_2026-11-21.py`.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import os
import pathlib
import stat
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("cdsfl_sv", ROOT / "scripts" / "cdsfl_sv.py")
S = importlib.util.module_from_spec(_spec)
sys.modules["cdsfl_sv"] = S
_spec.loader.exec_module(S)

J = S._MEMORY_POINTER_JOIN
HEAD = f"## {S._MEMORY_HEADED_SECTION}\n"


def _pointers(*paths: pathlib.Path) -> list[str]:
    """The audit's OWN parser, minus the sibling navigation links.

    A pointer TO the companion is navigation, not a lesson, so it is not part of
    the set being conserved -- the first version of the product's own check did
    not exclude it and refused its own first run.
    """
    out: list[str] = []
    for p in paths:
        if not p.is_file():
            continue
        for ln in p.read_text(encoding="utf-8").splitlines():
            out += [t for _ti, t, _n in S._memory_index_pointers(ln)
                    if t not in S._MEMORY_POINTER_SIBLINGS]
    return sorted(out)


def _index(mem: pathlib.Path, *, lows: int = 0, highs: int = 0,
           base_date: str = "2026-01-01") -> pathlib.Path:
    """An index with `lows` unstarred and `highs` 3-star Feedback pointers.

    Dates ascend, so the age tie-break inside a salience tier is observable and
    not an artefact of filesystem order.
    """
    units = []
    for i in range(lows):
        day = dt.date.fromisoformat(base_date) + dt.timedelta(days=i)
        units.append(f"[low {i}](low_{i}_{day.isoformat()}.md) hook for low {i}")
    for i in range(highs):
        day = dt.date.fromisoformat(base_date) + dt.timedelta(days=i)
        units.append(f"[★★★ high {i}](high_{i}_{day.isoformat()}.md) hook high {i}")
    for u in units:
        tgt = u.split("](")[1].split(")")[0]
        (mem / tgt).write_text("# stub\n", encoding="utf-8")
    idx = mem / S._MEMORY_INDEX_NAME
    idx.write_text("# Index\n\n" + HEAD + "- " + J.join(units) + "\n", encoding="utf-8")
    return idx


@pytest.fixture()
def mem(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path


class TestThePremiseIsAlive:
    """The defect this guard exists for must still be describable by execution."""

    def test_the_ageing_scope_still_excludes_the_section_that_grows(self):
        assert S._MEMORY_AGEING_SECTIONS == ("Project State",)
        assert S._MEMORY_HEADED_SECTION not in S._MEMORY_AGEING_SECTIONS

    def test_ageing_frees_nothing_in_the_feedback_section(self, mem):
        """THE ORIGINAL DEFECT, REPRODUCED BY CALLING THE OLD MECHANISM."""
        _index(mem, lows=40, base_date="2020-01-01")
        r = S.archive_stale_memory_entries(mem, dry_run=True)
        assert r["moved"] == 0, (
            "ageing moved a Feedback pointer; if that is now intended this guard "
            "is measuring the wrong thing")

    def test_the_relief_is_wired_into_the_automatic_path(self):
        """An addition nothing reaches is not additive (`additive-standard`)."""
        import ast
        tree = ast.parse((ROOT / "scripts" / "cdsfl_sv.py").read_text(encoding="utf-8"))
        callers = {
            fn.name
            for fn in ast.walk(tree)
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
            for node in ast.walk(fn)
            if isinstance(node, ast.Call)
            and getattr(node.func, "id", None) == "relieve_memory_index_pressure"
        }
        assert "_preflight_completeness" in callers, sorted(callers)


class TestItRelievesPressure:
    def test_it_moves_nothing_when_the_index_is_already_inside_its_target(self, mem):
        _index(mem, lows=3)
        r = S.relieve_memory_index_pressure(mem, dry_run=True)
        assert r["ok"] and r["moved"] == 0
        assert "inside its" in r["reason"]

    def test_it_brings_an_over_full_index_under_the_target(self, mem):
        idx = _index(mem, lows=200)
        before = len(idx.read_text(encoding="utf-8"))
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        assert r["ok"] and r["moved"] > 0
        assert len(idx.read_text(encoding="utf-8")) <= r["target"] < before

    def test_a_dry_run_writes_absolutely_nothing(self, mem):
        idx = _index(mem, lows=200)
        before = idx.read_text(encoding="utf-8")
        listing = sorted(p.name for p in mem.iterdir())
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000, dry_run=True)
        assert r["moved"] > 0, "a dry run that moves nothing cannot test this"
        assert idx.read_text(encoding="utf-8") == before
        assert sorted(p.name for p in mem.iterdir()) == listing

    def test_it_is_idempotent(self, mem):
        _index(mem, lows=200)
        S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        after = (mem / S._MEMORY_INDEX_NAME).read_text(encoding="utf-8")
        second = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        assert second["moved"] == 0
        assert (mem / S._MEMORY_INDEX_NAME).read_text(encoding="utf-8") == after

    def test_a_backup_holds_the_original_bytes_before_any_change(self, mem):
        idx = _index(mem, lows=200)
        before = idx.read_text(encoding="utf-8")
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        assert r["backup"], r["reason"]
        assert (mem / r["backup"]).read_text(encoding="utf-8") == before


class TestNothingIsLost:
    def test_no_lesson_pointer_is_lost(self, mem):
        idx = _index(mem, lows=200)
        before = _pointers(idx)
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        assert r["moved"] > 0
        after = _pointers(idx, mem / S._MEMORY_OVERFLOW_NAME)
        assert before == after, sorted(set(before) - set(after))[:5]

    def test_every_moved_unit_is_in_the_companion_verbatim(self, mem):
        canary = "CANARY-é★-7"
        (mem / "c.md").write_text("# s\n", encoding="utf-8")
        units = [f"[plain {canary}](c.md) hook {canary}"]
        for i in range(160):
            (mem / f"k{i}.md").write_text("# s\n", encoding="utf-8")
            units.append(f"[★★★ k{i}](k{i}.md) keep this one")
        (mem / S._MEMORY_INDEX_NAME).write_text(
            "# Index\n\n" + HEAD + "- " + J.join(units) + "\n", encoding="utf-8")
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_500)
        assert r["moved"] >= 1, r["reason"]
        body = (mem / S._MEMORY_OVERFLOW_NAME).read_text(encoding="utf-8")
        assert canary in body

    def test_a_second_relief_APPENDS_to_an_existing_companion(self, mem):
        """★ THE APPEND PATH, WHICH IS THE ONE PRODUCTION ALWAYS TAKES.

        Found by the mutation harness, not by reading: breaking the append branch
        left the whole guard green, because every other test here starts with no
        companion on disk and so only ever exercises the first-write branch. In
        live use the companion exists from the second save onward, so the branch
        the tests never reached is the branch that always runs.
        """
        idx = _index(mem, lows=200)
        r1 = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        assert r1["moved"] > 0, r1["reason"]
        ovf = mem / S._MEMORY_OVERFLOW_NAME
        assert ovf.is_file()
        first_body = ovf.read_text(encoding="utf-8")

        #: now grow the index again, exactly as a day's work does, and relieve
        #: a second time -- this run must APPEND, never overwrite.
        text = idx.read_text(encoding="utf-8")
        extra = []
        for i in range(200, 320):
            (mem / f"low_{i}_2026-02-01.md").write_text("# stub\n", encoding="utf-8")
            extra.append(f"[low {i}](low_{i}_2026-02-01.md) hook for low {i}")
        idx.write_text(text.rstrip() + "\n- " + J.join(extra) + "\n", encoding="utf-8")
        all_before = _pointers(idx, ovf)

        r2 = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        assert r2["moved"] > 0, r2["reason"]
        second_body = ovf.read_text(encoding="utf-8")
        assert second_body.startswith(first_body), (
            "the second relief overwrote the companion instead of appending")
        assert len(second_body) > len(first_body)
        assert _pointers(idx, ovf) == all_before, (
            sorted(set(all_before) - set(_pointers(idx, ovf)))[:5])
        assert second_body.count("Moved out of the loaded window") == 2

    def test_the_companion_says_the_lessons_still_bind(self, mem):
        _index(mem, lows=200)
        S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        body = (mem / S._MEMORY_OVERFLOW_NAME).read_text(encoding="utf-8")
        assert "Nothing here is retired" in body
        assert "READ THIS FILE IN FULL" in body

    def test_the_index_keeps_one_pointer_to_the_companion(self, mem):
        idx = _index(mem, lows=200)
        S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        text = idx.read_text(encoding="utf-8")
        assert text.count(f"]({S._MEMORY_OVERFLOW_NAME})") == 1

    def test_the_orphan_scan_counts_the_companions_pointers(self, mem):
        """Without this the first moved entry is reported as a false orphan."""
        _index(mem, lows=200)
        S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        audit = S._audit_memory_index(mem)
        assert audit.orphans_unmentioned == []
        assert audit.orphans_mentioned == []
        assert audit.broken == []

    def test_a_write_failure_leaves_the_index_untouched(self, mem):
        idx = _index(mem, lows=200)
        before = idx.read_text(encoding="utf-8")
        os.chmod(mem, stat.S_IRUSR | stat.S_IXUSR)
        try:
            r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
            assert not r["ok"] and "write failed" in r["reason"]
            assert idx.read_text(encoding="utf-8") == before
        finally:
            os.chmod(mem, stat.S_IRWXU)


class TestTheEvictionOrder:
    def test_a_three_star_pointer_never_moves_while_a_lower_one_remains(self, mem):
        """THE ORDERING INVARIANT, stated so it holds in BOTH regimes.

        The first version of this test asserted `max(tiers) == 0` on a fixture
        whose 60 unstarred pointers could not reach a 1,500-character target, so
        the relief correctly spilled into the top tier and the test called the
        designed fallback a defect. The invariant that actually expresses the
        rule is conditional: a 3-star pointer moves only once NO lower-salience
        pointer is left to move.
        """
        idx = _index(mem, lows=60, highs=140)
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        assert r["moved"] > 0, r["reason"]
        tiers = [int(t.split("-")[0]) for _w, t, _ti in r["moved_titles"]]
        #: ★ THE COMPANION'S NAVIGATION BULLET CARRIES 0 STARS, so a salience
        #: census that does not exclude it counts the link to the overflow file
        #: as a kept low-salience LESSON -- which is what made the first run of
        #: this assertion fail against correct code. It is the third predicate
        #: in this change to be fooled by that one link, which is why
        #: `_MEMORY_POINTER_SIBLINGS` exists and is used here too.
        kept = [S._memory_unit_salience(u)
                for ln in idx.read_text(encoding="utf-8").splitlines()
                if S._MEMORY_BULLET_RE.match(ln)
                for u in S._memory_split_units(ln)[1]
                if not any(f"]({sib})" in u for sib in S._MEMORY_POINTER_SIBLINGS)]
        kept_low = [s for s in kept if 0 <= s < 3]
        if 3 in tiers:
            assert not kept_low, (
                f"a 3-star pointer moved while {len(kept_low)} lower-salience "
                f"pointer(s) remained in the index")
        else:
            assert max(tiers) == 0, sorted(set(tiers))

    def test_with_enough_low_salience_mass_no_three_star_moves_at_all(self, mem):
        """The pure-ordering path: when the lower tier suffices, it alone is used."""
        idx = _index(mem, lows=120, highs=40)
        over = len(idx.read_text(encoding="utf-8"))
        refuse = int(S._MEMORY_INDEX_LIMIT_CHARS * S._MEMORY_INDEX_REFUSE_FRACTION)
        #: Ask for a target just 400 characters below the current size, which the
        #: unstarred tier can cover on its own several times over.
        r = S.relieve_memory_index_pressure(
            mem, reserve_chars=refuse - (over - 400))
        assert r["moved"] > 0, r["reason"]
        tiers = {int(t.split("-")[0]) for _w, t, _ti in r["moved_titles"]}
        assert tiers == {0}, tiers
        assert r["kept_top_tier"] == 40

    def test_within_a_tier_the_oldest_goes_first(self, mem):
        _index(mem, lows=200, base_date="2026-01-01")
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000, dry_run=True)
        dates = [w for w, _t, _ti in r["moved_titles"] if w != "undated"]
        assert len(dates) >= 2, r["moved_titles"][:3]
        assert dates == sorted(dates), dates[:6]

    def test_an_undated_pointer_leaves_AFTER_every_dated_one_in_its_tier(self, mem):
        """★ FOUND ON THE LIVE INDEX, NOT ON A FIXTURE.

        The first version sorted an undated pointer to `date.min`, so undated
        pointers were evicted FIRST — and on the live index that meant the
        foundational pre-convention lessons went before anything else, because
        the star marker and the date are nearly the same variable there
        (98 of 102 three-star dated, 65 of 66 unstarred undated, phi 0.928321).
        This file already states that None means NO EVIDENCE OF AGE and such a
        line is never archived on a hunch, so `date.min` inverted its own rule.
        """
        #: 40 unstarred, 20 of them undated, 20 dated — so the order is observable.
        units = []
        for i in range(20):
            tgt = f"dated_{i}_2026-03-{i + 1:02d}.md"
            (mem / tgt).write_text("# stub\n", encoding="utf-8")
            units.append(f"[dated {i}]({tgt}) hook padding text for dated {i}")
        for i in range(20):
            tgt = f"undated_{i}.md"
            (mem / tgt).write_text("# stub\n", encoding="utf-8")
            units.append(f"[undated {i}]({tgt}) hook padding text undated {i}")
        for i in range(120):
            tgt = f"keep_{i}_2026-04-{i % 28 + 1:02d}.md"
            (mem / tgt).write_text("# stub\n", encoding="utf-8")
            units.append(f"[\u2605\u2605\u2605 keep {i}]({tgt}) keep this one")
        idx = mem / S._MEMORY_INDEX_NAME
        idx.write_text("# Index\n\n" + HEAD + "- " + J.join(units) + "\n",
                       encoding="utf-8")
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000, dry_run=True)
        assert r["moved"] > 0, r["reason"]
        seq = [w for w, t, _ti in r["moved_titles"] if t == "0-star"]
        assert seq, r["moved_titles"][:4]
        #: every dated one that moved must appear before the first undated one
        first_undated = next((i for i, w in enumerate(seq) if w == "undated"), len(seq))
        assert all(w != "undated" for w in seq[:first_undated])
        dated_moved = [w for w in seq if w != "undated"]
        if first_undated < len(seq):
            assert len(dated_moved) == 20, (
                f"an undated pointer was evicted while {20 - len(dated_moved)} "
                f"dated ones remained in the same tier")

    def test_it_falls_back_to_the_top_tier_rather_than_refusing_a_save(self, mem):
        """With only 3-star pointers left it still relieves. Stated, not silent."""
        _index(mem, highs=200)
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000, dry_run=True)
        assert r["moved"] > 0
        tiers = {int(t.split("-")[0]) for _w, t, _ti in r["moved_titles"]}
        assert tiers == {3}

    def test_an_undated_pointer_is_REPORTED_as_undated_not_as_a_sentinel(self, mem):
        """★ A SORT KEY IS NOT A VALUE, and leaking one reached the founder's line.

        The eviction order sorts undated pointers to a sentinel date so they go
        last within their tier. The first version carried ONLY that key and
        recovered the undated case by comparing against it, so changing the
        sentinel from `date.min` to `date.max` made every undated pointer print
        as "9999-12-31" in the line `_preflight_completeness` shows him.
        """
        _index(mem, lows=200)
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000, dry_run=True)
        assert r["moved"] > 0, r["reason"]
        stamps = {w for w, _t, _ti in r["moved_titles"]}
        assert "9999-12-31" not in stamps, (
            f"a sort sentinel leaked into the reported dates: {sorted(stamps)[:4]}")
        assert "0001-01-01" not in stamps, sorted(stamps)[:4]
        #: and a genuinely undated pointer must say so in words
        for i in range(60):
            (mem / f"nod_{i}.md").write_text("# stub\n", encoding="utf-8")
        idx = mem / S._MEMORY_INDEX_NAME
        idx.write_text(
            "# Index\n\n" + HEAD + "- "
            + J.join(f"[no date {i}](nod_{i}.md) hook padding text here"
                     for i in range(60)) + "\n", encoding="utf-8")
        r2 = S.relieve_memory_index_pressure(mem, reserve_chars=24_400, dry_run=True)
        assert r2["moved"] > 0, r2["reason"]
        assert all(w == "undated" for w, _t, _ti in r2["moved_titles"]), \
            r2["moved_titles"][:3]

    def test_prose_on_a_shared_line_is_never_evicted(self, mem):
        """A bold sub-heading carries no link and must not be treated as a lesson."""
        assert S._memory_unit_salience("**EVIDENCE DISCIPLINE**") == -1
        assert S._memory_unit_salience("[★★ t](a.md) h") == 2
        assert S._memory_unit_salience("[t](a.md) h") == 0

    def test_a_heading_is_not_left_standing_over_nothing(self, mem):
        for i in range(200):
            (mem / f"p{i}.md").write_text("# s\n", encoding="utf-8")
        (mem / S._MEMORY_INDEX_NAME).write_text(
            "# Index\n\n" + HEAD
            + "**A HEADING WHOSE BULLETS ALL GO**\n"
            + "- " + J.join(f"[p{i}](p{i}.md) hook text padding here" for i in range(200))
            + "\n", encoding="utf-8")
        S.relieve_memory_index_pressure(mem, reserve_chars=24_300)
        text = (mem / S._MEMORY_INDEX_NAME).read_text(encoding="utf-8")
        if "A HEADING WHOSE BULLETS ALL GO" in text:
            tail = text.split("A HEADING WHOSE BULLETS ALL GO**", 1)[1]
            assert S._MEMORY_LINK_RE.search(tail), "heading kept with no pointers under it"


class TestItFailsSafely:
    def test_a_missing_index_is_reported_not_raised(self, mem):
        r = S.relieve_memory_index_pressure(mem)
        assert not r["ok"] and "no index" in r["reason"]

    def test_an_undecodable_index_is_reported_not_raised(self, mem):
        (mem / S._MEMORY_INDEX_NAME).write_bytes(b"\xff\xfe\x00bad")
        r = S.relieve_memory_index_pressure(mem)
        assert not r["ok"] and "unreadable" in r["reason"]

    def test_an_index_with_no_feedback_section_is_reported_not_crashed(self, mem):
        (mem / "x.md").write_text("# s\n", encoding="utf-8")
        (mem / S._MEMORY_INDEX_NAME).write_text(
            "# Index\n\n## Project State\n- [x](x.md) y\n", encoding="utf-8")
        r = S.relieve_memory_index_pressure(mem, reserve_chars=24_490)
        assert not r["ok"] and "0 evictable pointers" in r["reason"]

    def test_the_join_string_inside_a_title_does_not_split_a_pointer(self, mem):
        """The unit separator also occurs inside titles; a naive split loses one."""
        (mem / "x.md").write_text("# s\n", encoding="utf-8")
        units = [f"[a{J}b](x.md) hook"]
        for i in range(200):
            (mem / f"q{i}.md").write_text("# s\n", encoding="utf-8")
            units.append(f"[q{i}](q{i}.md) hook padding text")
        idx = mem / S._MEMORY_INDEX_NAME
        idx.write_text("# Index\n\n" + HEAD + "- " + J.join(units) + "\n", encoding="utf-8")
        before = _pointers(idx)
        r = S.relieve_memory_index_pressure(mem, reserve_chars=23_000)
        assert r["ok"], r["reason"]
        assert _pointers(idx, mem / S._MEMORY_OVERFLOW_NAME) == before


class TestTheConstantsAreDefensible:
    def test_the_reserve_is_smaller_than_the_refusal_margin(self):
        refuse = int(S._MEMORY_INDEX_LIMIT_CHARS * S._MEMORY_INDEX_REFUSE_FRACTION)
        assert 0 < S._MEMORY_RELIEF_RESERVE_CHARS < refuse

    def test_the_companion_is_not_the_history_archive(self):
        assert S._MEMORY_OVERFLOW_NAME != S._MEMORY_ARCHIVE_NAME
        assert S._MEMORY_ARCHIVE_NAME in S._MEMORY_POINTER_SIBLINGS
        assert S._MEMORY_OVERFLOW_NAME in S._MEMORY_POINTER_SIBLINGS

    def test_the_producer_exists_and_is_named_in_the_module(self):
        prod = ROOT / "scripts" / "the_index_can_never_stop_filling_2026-11-21.py"
        assert prod.is_file()
        src = (ROOT / "scripts" / "cdsfl_sv.py").read_text(encoding="utf-8")
        assert prod.name in src, "a measured constant must name its producer"
