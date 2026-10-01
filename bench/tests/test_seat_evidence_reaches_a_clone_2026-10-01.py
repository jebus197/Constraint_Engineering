#!/usr/bin/env python3
"""Seat-written evidence leaves the ignored tree automatically.

THE RECURRING FAULT. A panel harvest lands under
`bench/logs/<run>/.../files/<rel>`, and `.gitignore:48` ignores
`bench/logs/**`, so every seat-written file is invisible to git BY
CONSTRUCTION. Measured by `scripts/seat_evidence_is_gitignored_2026-09-30.py`,
which calls `git check-ignore` and `git ls-files` rather than reading the ignore
file: 251 seat `.py` files across 22 rounds, 251 of 251 = 100% ignored, 46 of
251 = 18.3267% UNPRESERVED (Wilson [14.0302%, 23.5781%]) -- existing nowhere a
clone could reach -- across 11 rounds.

12 scripts and 2 design notes were rescued BY HAND on 2026-09-30. The founder's
ruling on being shown it was a recurring fault: "clearly that also needs to be
repaired." `preserve_seat_evidence` is that repair, called from `harvest()`.

WHAT IT DELIBERATELY DOES NOT DO. It does not un-ignore the harvest. That was
tried and reverted for cause: the harvest also holds copies of files already
tracked at their canonical paths, and un-ignoring it staged 20 byte-identical
duplicates totalling 47 MB while still leaving the unique evidence out. Only
files with NO tracked counterpart are copied, and `.scratch/` is excluded
because the stranding measurement calls it the one group that SHOULD be
unpreserved.

EVERY TEST HERE BUILDS A REAL TREE AND CALLS THE REAL FUNCTION. A test that
read the source would prove only that the module describes itself
(`execute-do-not-grep`). Nothing is written to the canonical repository: every
case uses a temporary repo root.

Run:  python3 -m pytest bench/tests/test_seat_evidence_reaches_a_clone_2026-10-01.py -q
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import panel_sandbox as PS  # noqa: E402


@pytest.fixture
def tree(tmp_path):
    """A fake repo and a harvest laid out exactly as a real one is."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "bench" / "tests").mkdir(parents=True)
    # An EXISTING tracked file, which a seat then edits.
    (repo / "scripts" / "already_here.py").write_text("print('canonical')\n",
                                                      encoding="utf-8")
    dest = (repo / "bench" / "logs" / "round_2026-10-01"
            / "sandbox_harvest" / "cc2" / "attempt-1")
    files = dest / "files"
    (files / "scripts").mkdir(parents=True)
    (files / "bench" / "tests").mkdir(parents=True)
    (files / ".scratch").mkdir(parents=True)
    # 1. NEW seat-written script, tracked nowhere -> must be preserved.
    (files / "scripts" / "seat_new_falsifier.py").write_text(
        "assert 2 + 2 == 4\n", encoding="utf-8")
    # 2. NEW seat-written test -> must be preserved.
    (files / "bench" / "tests" / "test_seat_wrote_this.py").write_text(
        "def test_x():\n    assert True\n", encoding="utf-8")
    # 3. NEW seat-written note -> must be preserved, with a comment header.
    (files / "DESIGN_NOTE.md").write_text("# Finding\n\nBody.\n",
                                          encoding="utf-8")
    # 4. An EDIT to a tracked file -> must NOT be duplicated out.
    (files / "scripts" / "already_here.py").write_text("print('edited')\n",
                                                       encoding="utf-8")
    # 5. Scratch residue -> must NOT be preserved.
    (files / ".scratch" / "notes.py").write_text("# junk\n", encoding="utf-8")
    # 6. A data file -> not source evidence, not preserved.
    (files / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    return repo, dest


class TestTheUniqueEvidenceIsPreserved:
    def test_a_seat_written_file_with_no_tracked_counterpart_is_copied_out(
            self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        kept = {p["rel"] for p in out["preserved"]}
        assert "scripts/seat_new_falsifier.py" in kept, out
        assert "bench/tests/test_seat_wrote_this.py" in kept, out
        assert "DESIGN_NOTE.md" in kept, out

    def test_it_lands_somewhere_git_does_not_ignore(self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        for p in out["preserved"]:
            landed = repo / p["path"]
            assert landed.is_file(), p
            assert "bench/logs" not in p["path"], (
                f"preserved INTO the ignored tree, which preserves nothing: "
                f"{p['path']}")
            assert p["path"].startswith("experimental_notes/seat_evidence/")

    def test_the_round_and_the_seat_are_in_the_path(self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        assert out["round"] == "round_2026-10-01", out["round"]
        assert out["seat"] == "cc2", out["seat"]
        for p in out["preserved"]:
            assert "round_2026-10-01" in p["path"] and "cc2" in p["path"]

    def test_the_body_survives_byte_for_byte_under_the_header(self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        original = (dest / "files" / "scripts"
                    / "seat_new_falsifier.py").read_bytes()
        rec = next(p for p in out["preserved"]
                   if p["rel"] == "scripts/seat_new_falsifier.py")
        landed = (repo / rec["path"]).read_bytes()
        assert landed.endswith(original), (
            "the seat's bytes were altered, not merely prefixed")
        assert rec["sha256"] == hashlib.sha256(original).hexdigest(), (
            "the recorded digest is not the digest of the seat's original, so "
            "byte-identity cannot be checked later")

    def test_a_note_gets_a_comment_header_not_a_python_one(self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        rec = next(p for p in out["preserved"] if p["rel"] == "DESIGN_NOTE.md")
        text = (repo / rec["path"]).read_text(encoding="utf-8")
        assert text.startswith("<!--"), text[:80]
        assert "# Finding" in text, "the note's own first heading was destroyed"

    def test_a_manifest_records_what_was_preserved(self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        man = repo / out["dir"] / "PROVENANCE.json"
        assert man.is_file()
        doc = json.loads(man.read_text(encoding="utf-8"))
        assert doc["round"] == "round_2026-10-01" and doc["seat"] == "cc2"
        assert len(doc["preserved"]) == len(out["preserved"])


class TestWhatMustNotBeCopied:
    def test_an_edit_to_a_tracked_file_is_not_duplicated_out(self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        kept = {p["rel"] for p in out["preserved"]}
        assert "scripts/already_here.py" not in kept, (
            "a file that already reaches a clone was copied out again; this is "
            "the 47 MB of byte-identical duplicates the earlier attempt staged")
        assert "scripts/already_here.py" in out["already_tracked"]

    def test_scratch_residue_is_not_evidence(self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        kept = {p["rel"] for p in out["preserved"]}
        assert not any(k.startswith(".scratch") for k in kept), kept

    def test_a_data_file_is_not_treated_as_source_evidence(self, tree):
        repo, dest = tree
        out = PS.preserve_seat_evidence(dest, repo)
        kept = {p["rel"] for p in out["preserved"]}
        assert "data.csv" not in kept

    def test_the_canonical_repository_is_never_written(self, tree):
        """This whole file must not leave anything in the real tree."""
        repo, dest = tree
        PS.preserve_seat_evidence(dest, repo)
        assert not (REPO / PS.SEAT_EVIDENCE_DIR
                    / "round_2026-10-01").exists(), (
            "the test wrote into the canonical repository")


class TestItIsOnTheLivePath:
    def test_harvest_calls_it(self, tree):
        """ANTI-UNREACHED-ADDITION: wired into harvest(), not merely defined."""
        repo, dest = tree
        sandbox = repo.parent / "sandbox"
        sandbox.mkdir()
        res = PS.harvest(sandbox, repo, dest)
        assert "seat_evidence_preserved" in res, (
            "harvest() does not report preservation, so no caller can know "
            "whether it happened")

    def test_it_never_raises_on_a_harvest_with_no_files_dir(self, tmp_path):
        out = PS.preserve_seat_evidence(tmp_path / "nothing", tmp_path)
        assert out["preserved"] == [] and out["failed"] == []

    def test_a_second_run_over_the_same_harvest_is_idempotent(self, tree):
        repo, dest = tree
        first = PS.preserve_seat_evidence(dest, repo)
        second = PS.preserve_seat_evidence(dest, repo)
        assert len(second["preserved"]) == len(first["preserved"])
        for p in second["preserved"]:
            text = (repo / p["path"]).read_text(encoding="utf-8")
            assert text.count("PRESERVED SEAT EVIDENCE") == 1, (
                "the provenance header was prepended twice")
