#!/usr/bin/env python3
"""Option 1 of entry B29: the memory check's baseline is the last save that
FINISHED CLEANLY, recorded as a fact rather than inferred from recency.

HIS RULING, 2026-10-29, annotation 4 of
`Responses/Decisions_Awaiting_You_2026-10-29.txt`: *"Build and implement option
1. fr"*. Option 1 as he was given it, from
`experimental_notes/data/morning_report_decisions.json` key `task:B29`: *"Have
the save record whether its own conditions passed, and have the memory check
skip back to the last save that finished cleanly"*.

THE DEFECT IT CLOSES. `_check_memory_updated` asks whether any memory file is
newer than the previous sv commit. For a FIRST save that is sound. For a
FOLLOW-UP it is wrong: the save it measures against is the very save whose
memory it is asking to see again, so the gate refuses a save for lacking memory
that exists. It cost time 4 times on 2026-10-29 alone, the sharpest being a
refusal of a commit carrying 1 line of bookkeeping.

THE PROPERTY THAT MUST NOT BREAK, and it is tested first: a save with NO
completion record is NOT skipped, so wherever nothing was recorded the resolved
baseline is byte-identical to the pre-2026-10-29 behaviour. The check can become
better informed; it can never become weaker.

EVERY TEST BUILDS A REAL GIT REPOSITORY AND RUNS THE REAL RESOLVER. Nothing here
reads source text.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SV = REPO / "scripts" / "cdsfl_sv.py"


def _sv():
    spec = importlib.util.spec_from_file_location("cdsfl_sv_baseline_under_test", SV)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdsfl_sv_baseline_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


sv = _sv()


def _run(*args, cwd):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, check=True)


@pytest.fixture()
def repo(tmp_path):
    """A repository with 2 sv commits, older then newer, and nothing recorded."""
    r = tmp_path / "repo"
    r.mkdir()
    _run("git", "init", "-q", cwd=r)
    _run("git", "config", "user.email", "t@example.invalid", cwd=r)
    _run("git", "config", "user.name", "T", cwd=r)
    _run("git", "config", "commit.gpgsign", "false", cwd=r)
    shas = {}
    for label in ("older", "newer"):
        (r / f"{label}.txt").write_text(label, encoding="utf-8")
        _run("git", "add", "-A", cwd=r)
        _run("git", "commit", "-q", "-m", f"sv: the {label} save", cwd=r)
        shas[label] = _run("git", "rev-parse", "HEAD", cwd=r).stdout.strip()
    return r, shas


class TestAbsenceIsNotUncleanliness:
    def test_with_no_records_the_baseline_is_unchanged(self, repo):
        r, shas = repo
        assert sv.unclean_sv_commits(r) == set()
        plain = sv._previous_sv_commit(r)
        strict = sv._previous_sv_commit(r, require_clean=True)
        assert plain == strict
        assert strict[0] == shas["newer"][:7]

    def test_a_clean_record_does_not_move_the_baseline(self, repo):
        r, shas = repo
        sv.record_sv_completion(r, shas["newer"], clean=True)
        assert sv.unclean_sv_commits(r) == set()
        assert sv._previous_sv_commit(r, require_clean=True)[0] == shas["newer"][:7]


class TestAnUncleanSaveIsSkipped:
    def test_the_baseline_moves_back_to_the_clean_save(self, repo):
        """THE DISCRIMINATING CASE. Without the skip the answer is 'newer'."""
        r, shas = repo
        sv.record_sv_completion(r, shas["newer"], clean=False,
                                failed=["recovery-block-currency"])
        assert sv.unclean_sv_commits(r) == {shas["newer"][:7]}
        assert sv._previous_sv_commit(r)[0] == shas["newer"][:7], (
            "the unconstrained resolver must still report the newest save, or "
            "this test is not measuring the skip")
        assert sv._previous_sv_commit(r, require_clean=True)[0] == shas["older"][:7]

    def test_a_later_clean_record_supersedes_an_earlier_failure(self, repo):
        """A save that failed and was then verified clean stops being skipped."""
        r, shas = repo
        sv.record_sv_completion(r, shas["newer"], clean=False, failed=["x"])
        assert sv.unclean_sv_commits(r) == {shas["newer"][:7]}
        sv.record_sv_completion(r, shas["newer"], clean=True)
        assert sv.unclean_sv_commits(r) == set()
        assert sv._previous_sv_commit(r, require_clean=True)[0] == shas["newer"][:7]

    def test_every_save_unclean_falls_back_to_none_rather_than_lying(self, repo):
        """With no clean save anywhere the resolver reports NOTHING.

        `_check_memory_updated` treats a `None` baseline as "the check could not
        be performed, which is not the same as passing", so the honest outcome of
        an all-unclean history is a refusal to measure rather than a pass.
        """
        r, shas = repo
        for sha in shas.values():
            sv.record_sv_completion(r, sha, clean=False, failed=["x"])
        assert sv._previous_sv_commit(r, require_clean=True) is None

    def test_the_check_names_the_saves_it_skipped(self, repo, monkeypatch):
        r, shas = repo
        mem = r / "mem"
        mem.mkdir()
        (mem / "MEMORY.md").write_text("# index\n", encoding="utf-8")
        sv.record_sv_completion(r, shas["newer"], clean=False, failed=["x"])
        check = sv._check_memory_updated(r, mem_dir=mem)
        assert "SKIPPED BACK from" in check.expected, check.expected
        assert shas["newer"][:7] in check.expected
        assert shas["older"][:7] in check.expected

    def test_it_does_not_claim_a_skip_that_did_not_happen(self, repo):
        """THE DEFECT MUTATION 4 OF 6 EXPOSED IN THE REPAIR ITSELF.

        The first version built this sentence from the unclean RECORD SET, so it
        announced a skip whenever any save was recorded unclean -- including when
        the resolver had not skipped anything. Here the unclean save is NOT the
        newest, so no skip occurs and the sentence must be absent.
        """
        r, shas = repo
        mem = r / "mem"
        mem.mkdir()
        (mem / "MEMORY.md").write_text("# index\n", encoding="utf-8")
        sv.record_sv_completion(r, shas["older"], clean=False, failed=["x"])
        assert sv.unclean_sv_commits(r) == {shas["older"][:7]}
        check = sv._check_memory_updated(r, mem_dir=mem)
        assert "SKIPPED BACK" not in check.expected, (
            "a skip was announced although the newest save was already clean: "
            + check.expected)


class TestTheRecordItself:
    def test_it_is_append_only_and_parseable(self, repo):
        r, shas = repo
        sv.record_sv_completion(r, shas["older"], clean=True)
        sv.record_sv_completion(r, shas["newer"], clean=False, failed=["b", "a"])
        path = sv._sv_completions_path(r)
        rows = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(rows) == 2
        assert rows[0]["clean"] is True and rows[0]["failed"] == []
        assert rows[1]["clean"] is False and rows[1]["failed"] == ["a", "b"]
        assert all("recorded" in row for row in rows)

    def test_a_corrupt_line_is_skipped_not_fatal(self, repo):
        r, shas = repo
        sv.record_sv_completion(r, shas["newer"], clean=False, failed=["x"])
        path = sv._sv_completions_path(r)
        with path.open("a", encoding="utf-8") as fh:
            fh.write("{not json at all\n")
        assert sv.unclean_sv_commits(r) == {shas["newer"][:7]}

    def test_recording_never_raises_on_an_unwritable_location(self, tmp_path):
        """A save already in the object store must not be failed by bookkeeping."""
        blocked = tmp_path / "blocked"
        blocked.write_text("not a directory", encoding="utf-8")
        assert sv.record_sv_completion(blocked, "deadbeef", clean=True) is None

    def test_an_absent_record_file_reads_as_an_empty_set(self, repo):
        r, _ = repo
        assert not sv._sv_completions_path(r).exists()
        assert sv.unclean_sv_commits(r) == set()


class TestTheRecorderIsActuallyWired:
    """THE GAP MUTATION 5 OF 6 EXPOSED: the recorder was tested and its CALL SITE
    was not, so replacing `clean=not failed` with `clean=True` left every test
    green. Verifying a function without verifying the layer that decides is the
    failure `feedback_verify_the_deciding_layer` names.
    """

    class _Result:
        def __init__(self, name, failed):
            self.name = name
            self.failed = failed

    def _stub_postconditions(self, monkeypatch, results):
        monkeypatch.setattr(sv.sv_postconditions, "check_all",
                            lambda root, pushed: results)
        monkeypatch.setattr(sv.sv_postconditions, "report", lambda r: "(stubbed)")

    def test_a_clean_gate_records_clean(self, repo, monkeypatch, capsys):
        r, shas = repo
        self._stub_postconditions(monkeypatch, [self._Result("a", False)])
        rc = sv._run_postcondition_gate(r, push=False)
        capsys.readouterr()
        assert rc == 0
        assert sv.unclean_sv_commits(r) == set()
        rows = sv._sv_completions_path(r).read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) == 1
        assert json.loads(rows[0])["clean"] is True

    def test_a_failing_gate_records_the_failure_and_its_names(self, repo, monkeypatch, capsys):
        r, shas = repo
        self._stub_postconditions(
            monkeypatch,
            [self._Result("recovery-block-currency", True), self._Result("b", False)])
        rc = sv._run_postcondition_gate(r, push=False)
        capsys.readouterr()
        assert rc == 1
        assert sv.unclean_sv_commits(r) == {shas["newer"][:7]}
        row = json.loads(sv._sv_completions_path(r).read_text(encoding="utf-8").strip())
        assert row["clean"] is False
        assert row["failed"] == ["recovery-block-currency"]

    def test_the_recorded_sha_is_head(self, repo, monkeypatch, capsys):
        r, shas = repo
        self._stub_postconditions(monkeypatch, [self._Result("a", False)])
        sv._run_postcondition_gate(r, push=False)
        capsys.readouterr()
        row = json.loads(sv._sv_completions_path(r).read_text(encoding="utf-8").strip())
        assert row["sha"] == shas["newer"]
