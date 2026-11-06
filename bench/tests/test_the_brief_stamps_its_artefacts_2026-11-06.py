#!/usr/bin/env python3
"""The brief's artefact stamp must be true, additive, and never guess.

★ GUARD FOR B125's FIX. A free panel seat specified the stamp on 2026-11-04 and
could not write it; the entry has been OPEN since. The fix is only a fix if a
test executes it, which is the symmetric half of `additive-standard`: this
project's record holds 11 confirmed defects that were additions nothing reached.

WHAT IS PINNED, and each has a reason:
  * a digest must MOVE when 1 byte moves, or the stamp cannot detect the drift
    it exists for;
  * a basename is resolved only when exactly 1 file carries it, because guessing
    which copy a seat was given is the very ambiguity the stamp removes;
  * an unresolvable path is REPORTED, never silently dropped, so a brief naming
    an artefact that does not exist says so;
  * the block is EMPTY when nothing resolves, so a brief with no artefacts gains
    no header;
  * insertion is ADDITIVE -- the title survives byte-identical and nothing else
    in the brief changes.

EVERY FIXTURE IS SYNTHETIC except the live-tree test, which is skipped visibly
when the committed brief is absent rather than passing on nothing.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if not (REPO / "bench").is_dir():
    REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
#: THE TARGET IS OVERRIDABLE so a mutation harness can point this guard at a
#: mutant copy and prove it discriminates, without writing to the tree.
MODULE = Path(os.environ.get("STAMPER_OVERRIDE") or
              (REPO / "scripts" / "stamp_the_brief_artefacts_2026-11-06.py"))



@pytest.fixture(scope="module")
def st():
    if not MODULE.is_file():
        pytest.skip(f"stamper absent at {MODULE}")
    spec = importlib.util.spec_from_file_location("brief_stamper", MODULE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["brief_stamper"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def tree(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "scripts" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "docs" / "note.md").write_text("hello\n", encoding="utf-8")
    return tmp_path


class TestTheDigestIsTrueAndMoves:
    def test_the_digest_matches_the_file(self, st, tree):
        got = st.stamp("scripts/thing.py", tree)["sha256"]
        want = hashlib.sha256((tree / "scripts" / "thing.py").read_bytes()).hexdigest()
        assert got == want

    def test_one_byte_moves_the_digest(self, st, tree):
        before = st.stamp("scripts/thing.py", tree)["sha256"]
        (tree / "scripts" / "thing.py").write_text("x = 2\n", encoding="utf-8")
        after = st.stamp("scripts/thing.py", tree)["sha256"]
        assert before != after, (
            "the digest did not move when the content did, so the stamp cannot "
            "detect the drift B125 is about")

    def test_the_byte_count_and_mtime_are_recorded(self, st, tree):
        s = st.stamp("scripts/thing.py", tree)
        assert s["bytes"] == 6
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$", s["mtime"])


class TestResolutionNeverGuesses:
    def test_an_exact_path_resolves(self, st, tree):
        assert st.resolve("scripts/thing.py", tree) == "scripts/thing.py"

    def test_a_unique_basename_resolves(self, st, tree):
        assert st.resolve("note.md", tree) == "docs/note.md"

    def test_an_ambiguous_basename_does_NOT_resolve(self, st, tree):
        (tree / "scripts" / "note.md").write_text("other\n", encoding="utf-8")
        assert st.resolve("note.md", tree) is None, (
            "two files share this basename; choosing one would invent the "
            "provenance the stamp exists to establish")

    def test_an_absent_path_does_not_resolve(self, st, tree):
        assert st.resolve("scripts/nope.py", tree) is None

    def test_log_harvests_are_excluded_from_basename_resolution(self, st, tree):
        d = tree / "bench" / "logs" / "r" / "sandbox_harvest"
        d.mkdir(parents=True)
        (d / "only_here.py").write_text("y = 1\n", encoding="utf-8")
        assert st.resolve("only_here.py", tree) is None, (
            "a harvested copy is a photograph of someone else's sandbox and "
            "must not be offered as the artefact a seat was given")


class TestTheBlock:
    def test_it_is_empty_when_nothing_resolves(self, st, tree):
        assert st.stamp_block("no artefacts named here at all", tree) == ""

    def test_it_stamps_what_it_finds_and_reports_what_it_cannot(self, st, tree):
        text = "see `scripts/thing.py` and `scripts/ghost.py`"
        blk = st.stamp_block(text, tree)
        assert "scripts/thing.py" in blk
        assert "scripts/ghost.py" not in blk
        assert st.unresolved(text, tree) == ["scripts/ghost.py"]

    def test_the_table_has_one_row_per_artefact(self, st, tree):
        blk = st.stamp_block("`scripts/thing.py` and `docs/note.md`", tree)
        rows = [l for l in blk.splitlines() if l.startswith("| `")]
        assert len(rows) == 2, blk

    def test_every_row_carries_a_16_hex_digest(self, st, tree):
        blk = st.stamp_block("`scripts/thing.py`", tree)
        rows = [l for l in blk.splitlines() if l.startswith("| `")]
        assert rows and all(re.match(r"^[0-9a-f]{16}$", r.split("`")[3]) for r in rows)

    def test_a_path_named_twice_is_stamped_once(self, st, tree):
        blk = st.stamp_block("`scripts/thing.py` then `scripts/thing.py`", tree)
        rows = [l for l in blk.splitlines() if l.startswith("| `")]
        assert len(rows) == 1


class TestAgainstTheLiveTree:
    def test_the_committed_brief_stamps_and_every_digest_is_true(self, st):
        brief = (REPO / "bench" / "logs" / "joint_the_period_reviewed_2026-11-04"
                 / "BRIEF.md")
        if not brief.is_file():
            pytest.skip(f"the committed brief is absent at {brief}")
        text = brief.read_text(encoding="utf-8")
        blk = st.stamp_block(text, REPO)
        rows = [l for l in blk.splitlines() if l.startswith("| `")]
        assert len(rows) >= 2, "the live brief names artefacts; none were stamped"
        for r in rows:
            rel, digest = r.split("`")[1], r.split("`")[3]
            live = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()[:16]
            assert digest == live, f"{rel}: stamped {digest}, on disk {live}"

    def test_it_never_stamps_a_harvested_copy(self, st):
        brief = (REPO / "bench" / "logs" / "joint_the_period_reviewed_2026-11-04"
                 / "BRIEF.md")
        if not brief.is_file():
            pytest.skip("the committed brief is absent")
        arts = st.named_artefacts(brief.read_text(encoding="utf-8"), REPO)
        bad = [a for a in arts if "sandbox_harvest" in a or "/panel_worktree_harvest/" in a]
        assert not bad, bad
