#!/usr/bin/env python3
"""B211's checker must detect a moved index and must fall open on every doubt.

SUBJECT: `scripts/the_preboard_evidence_matches_the_tree_2026-11-23.py`.

★ IT IS DRIVEN, NOT READ. `execute-do-not-grep`: a test asserting on that
script's source would establish only that the file describes itself
consistently. Every case here builds a real git repository in a `tmp_path`,
stages real content, and calls the real `verdict()`.

★ THE CASE THAT MATTERS IS THE FAILING ONE.
`feedback_the_passing_input_cannot_test_a_defence_2026-11-09`: a defence
exercised only on the input it is meant to pass proves nothing. `TestItSeesAMovedIndex`
is therefore the load-bearing class, and `test_unstaging_returns_to_fresh` is
the one that discriminates this design from the mtime design B211 rejected --
a timestamp can only move forward, so an mtime checker would stay STALE after
the change is reverted, while a content digest returns to FRESH.

★ EVERY PATH MUST EXIT 0 AND EVERY DOUBT MUST BE `UNKNOWN`. This ships as a
REPORTED line in the gate, in the same shape as the panel line, because
`feedback_a_false_positive_can_be_why_a_rule_is_unenforced_2026-11-02` records
that a semantic false positive is how a rule ends up switched off. A checker
that can refuse a commit for a condition it cannot decide is worse than no
checker.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for cand in [here.parent, *here.parents]:
        if (cand / "scripts").is_dir() and (cand / "bench" / "tests").is_dir():
            return cand
    fb = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
    if (fb / "scripts").is_dir():
        return fb
    raise SystemExit("cannot locate the repository from " + str(here))


REPO = _find_repo()
SUBJECT = REPO / "scripts" / "the_preboard_evidence_matches_the_tree_2026-11-23.py"


@pytest.fixture(scope="module")
def mod():
    assert SUBJECT.is_file(), SUBJECT
    spec = importlib.util.spec_from_file_location("preboard_evidence", SUBJECT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["preboard_evidence"] = m
    spec.loader.exec_module(m)
    return m


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, timeout=120)


@pytest.fixture
def sandbox(tmp_path):
    """A REAL git repository with 1 commit, so the index can genuinely move."""
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@example.invalid")
    _git(r, "config", "user.name", "t")
    (r / "seed.txt").write_text("seed\n")
    _git(r, "add", "seed.txt")
    _git(r, "commit", "-q", "-m", "seed")
    return r


class TestItSeesAMovedIndex:
    """★ THE LOAD-BEARING CLASS. Without it the others pass on anything."""

    def test_an_unchanged_index_is_fresh(self, mod, sandbox):
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        assert mod.record(sandbox, 31, "1767 passed") is not None
        state, why = mod.verdict(sandbox)
        assert state == "FRESH", (state, why)

    def test_staging_more_goes_stale(self, mod, sandbox):
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        mod.record(sandbox, 31, "1767 passed")
        (sandbox / "b.txt").write_text("two\n")       # the edit after the run
        _git(sandbox, "add", "b.txt")
        state, why = mod.verdict(sandbox)
        assert state == "STALE", (
            f"the index moved and the checker said {state!r}. This is the exact "
            f"gap B211 names: a pre-board run that passed before the last edit "
            f"is not evidence about the tree being committed, and missing it "
            f"cost a 47 min 19 s refusal on 2026-11-22.")
        assert "INDEX HAS MOVED" in why

    def test_editing_an_already_staged_file_goes_stale(self, mod, sandbox):
        """A CHANGED FILE, not just an added one -- the 2026-11-22 case."""
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        mod.record(sandbox, 31, "x")
        (sandbox / "a.txt").write_text("one, reworded\n")
        _git(sandbox, "add", "a.txt")
        assert mod.verdict(sandbox)[0] == "STALE"

    def test_unstaging_returns_to_fresh(self, mod, sandbox):
        """★ THIS DISCRIMINATES THIS DESIGN FROM THE mtime DESIGN B211 REJECTED.

        A timestamp only moves forward, so an mtime checker stays STALE once
        anything is touched, even after the change is reverted. A CONTENT
        digest returns to FRESH, which is why B211's own falsifier -- "a tool
        that rewrites a staged file without changing it would defeat a
        timestamp" -- selects content over time.
        """
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        mod.record(sandbox, 31, "x")
        (sandbox / "b.txt").write_text("two\n")
        _git(sandbox, "add", "b.txt")
        assert mod.verdict(sandbox)[0] == "STALE"
        _git(sandbox, "rm", "--cached", "-q", "b.txt")
        assert mod.verdict(sandbox)[0] == "FRESH", (
            "the digest did not return to FRESH after the staged change was "
            "reverted, so it is behaving like a timestamp rather than a "
            "content hash -- which is the design B211 rejected")


class TestEveryDoubtFallsOpen:
    """UNKNOWN on anything undecidable. It must never say STALE on a doubt."""

    def test_no_evidence_file_is_unknown(self, mod, sandbox):
        state, why = mod.verdict(sandbox)
        assert state == "UNKNOWN" and "no pre-board evidence" in why

    def test_unreadable_record_is_unknown(self, mod, sandbox):
        p = sandbox / mod.EVIDENCE
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("not json at all")
        assert mod.verdict(sandbox)[0] == "UNKNOWN"

    def test_a_record_with_no_digest_is_unknown(self, mod, sandbox):
        p = sandbox / mod.EVIDENCE
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"guards": 3}))
        assert mod.verdict(sandbox)[0] == "UNKNOWN"

    def test_outside_a_git_repository_is_unknown(self, mod, tmp_path):
        bare = tmp_path / "not_a_repo"
        bare.mkdir()
        p = bare / mod.EVIDENCE
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"digest": "deadbeef"}))
        assert mod.verdict(bare)[0] == "UNKNOWN", (
            "with no git available the digest cannot be computed, and an "
            "undecidable condition must never be reported as STALE")


class TestItCannotRefuseACommit:
    """It ships as a REPORT. A non-zero exit would make it a gate."""

    def test_every_mode_exits_zero(self, sandbox):
        for args in (["--quiet"], ["--record", "--guards", "1"], []):
            r = subprocess.run(
                [sys.executable, str(SUBJECT), "--repo", str(sandbox), *args],
                capture_output=True, text=True, timeout=300)
            assert r.returncode == 0, (args, r.returncode, r.stderr[-400:])

    def test_it_exits_zero_even_when_stale(self, mod, sandbox):
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        mod.record(sandbox, 1, "x")
        (sandbox / "b.txt").write_text("two\n")
        _git(sandbox, "add", "b.txt")
        assert mod.verdict(sandbox)[0] == "STALE"
        r = subprocess.run(
            [sys.executable, str(SUBJECT), "--repo", str(sandbox), "--quiet"],
            capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, (
            "a STALE verdict exited non-zero. This ships as a REPORT: a "
            "checker that can refuse a commit for a condition it may have "
            "decided wrongly is how a rule gets switched off")
        assert "STALE" in r.stdout


class TestItWritesNothingItShouldNot:
    def test_a_check_does_not_create_the_evidence_file(self, mod, sandbox):
        mod.verdict(sandbox)
        assert not (sandbox / mod.EVIDENCE).exists(), (
            "a read-only check created the evidence file, so the next check "
            "would compare against a record the check itself wrote")

    def test_the_digest_is_read_only(self, mod, sandbox):
        """`git write-tree` would create an object; `diff --cached` does not."""
        before = _git(sandbox, "count-objects", "-v").stdout
        mod.staged_digest(sandbox)
        assert _git(sandbox, "count-objects", "-v").stdout == before


class TestTheStageZeroSnapshotFixesTheFalsePositive:
    """★ ADDED 2026-11-23 AFTER THE FIRST LIVE USE FAILED ON 4 OF 4 COMMITS.

    The reported line sits below the gate's repair stages, which rewrite tracked
    files and RE-STAGE them. So the index moves on the GATE's account and the
    line accused the operator of an edit the gate had made. Measured: a staged
    stale ledger digests f16746db6bb17a37, survives the refresh UNCHANGED --
    the refresh leaves it unstaged -- and becomes 072e2b9d6a60440a once the
    repairs are re-staged. **It is the RE-STAGING that moves it.**

    AN EARLIER ATTEMPT TO FALSIFY THAT ACCOUNT APPEARED TO REFUTE IT, and the
    attempt was VACUOUS: it ran the repair on an already-repaired tree, where
    nothing could move. A falsifier run on an already-satisfied precondition
    proves nothing, and that is recorded here because the same shape -- testing
    a defence with the input it is meant to pass -- has now bitten twice.

    THE FIX IS LIKE-FOR-LIKE COMPARISON, not a looser threshold: `--snapshot`
    at the gate's stage 0 records the index AS THE OPERATOR LEFT IT. The
    discriminating requirement is that it must NOT mask a genuine operator
    edit, which `test_it_does_not_mask_an_operator_edit` holds.
    """

    def test_a_gate_caused_move_reads_fresh_with_a_snapshot(self, mod, sandbox):
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        mod.record(sandbox, 9, "probe run")
        # the operator's index, snapshotted at stage 0
        d = mod.staged_digest(sandbox)
        p = sandbox / mod.SNAPSHOT
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"digest": d}))
        # now the GATE repairs and re-stages on its own account
        (sandbox / "ledger.txt").write_text("refreshed by the gate\n")
        _git(sandbox, "add", "ledger.txt")
        state, why = mod.verdict(sandbox)
        assert state == "FRESH", (
            f"a gate-caused index move was reported {state!r}; the snapshot "
            f"exists precisely so the gate's own re-staging is not read as an "
            f"operator edit. why={why}")
        assert "snapshot" in why

    def test_it_does_not_mask_an_operator_edit(self, mod, sandbox):
        """★ THE DISCRIMINATING CASE. A fix that silenced everything would pass
        the test above and be worthless."""
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        mod.record(sandbox, 9, "probe run")
        # the OPERATOR edits after the run, and THEN the gate snapshots
        (sandbox / "b.txt").write_text("edited after the run\n")
        _git(sandbox, "add", "b.txt")
        d = mod.staged_digest(sandbox)
        p = sandbox / mod.SNAPSHOT
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"digest": d}))
        assert mod.verdict(sandbox)[0] == "STALE", (
            "the snapshot masked a genuine operator edit, which would make the "
            "whole check vacuous -- the stage-0 snapshot must capture the "
            "operator's index INCLUDING any edit made after the pre-board run")

    def test_a_corrupt_snapshot_falls_back_to_the_live_index(self, mod, sandbox):
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        mod.record(sandbox, 9, "x")
        p = sandbox / mod.SNAPSHOT
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("not json")
        assert mod.verdict(sandbox)[0] == "FRESH"       # live index, unchanged

    def test_recording_clears_a_previous_snapshot(self, sandbox):
        """A snapshot left by an earlier attempt must not outlive new evidence."""
        (sandbox / "a.txt").write_text("one\n")
        _git(sandbox, "add", "a.txt")
        subprocess.run([sys.executable, str(SUBJECT), "--repo", str(sandbox),
                        "--snapshot", "--quiet"], capture_output=True, timeout=300)
        snap = sandbox / "" / ".cdsfl_tmp" / "preboard_snapshot.json"
        assert snap.exists()
        subprocess.run([sys.executable, str(SUBJECT), "--repo", str(sandbox),
                        "--record", "--guards", "1"], capture_output=True, timeout=300)
        assert not snap.exists(), (
            "a stale snapshot survived a new --record, so fresh evidence would "
            "be compared against an old index -- the stale-verdict defect in "
            "mirror image")
