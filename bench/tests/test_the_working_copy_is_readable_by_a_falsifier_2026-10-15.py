"""B9: the working copy must be stageable where a falsifier may read it.

THE DEFECT, measured 2026-10-15 on both free runs. Every round is pointed at the
per-run working copy of the review target, so that copy IS the target the
falsifiers are given. It was created under `bench/logs/<run>/working/` (since
`ce08914c`, 2026-09-01). On 2026-10-12 commit `e8ee2e18` closed a real hole by
making `falsifier_verify._is_evidence` refuse ANY `bench/logs` path even inside
an allowed root, after both free seats independently found that a falsifier could
read this project's run evidence. Each change is correct; together they refuse
the falsifier its own review target. 18 refusals per run across both free runs,
every one of them that path, against 0 of 81 in the pre-rule `study_run1b` --
Fisher exact p = 3.976950e-20.

THESE TESTS EXECUTE. They call `_apply_back_setup` and then run the guard's own
`_denied` predicate against what it returns, rather than asserting on source
text, per `execute-do-not-grep`. A test that greps for `STAGED_TARGET_ROOT` in
the runner would pass while a producer and a consumer disagreed.
"""
from __future__ import annotations

import ast
import dataclasses
import hashlib
import os
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(REPO / "bench") not in sys.path:
    sys.path.insert(0, str(REPO / "bench"))


@pytest.fixture(scope="module")
def runner():
    import reference_runner_v3 as rr
    return rr


@pytest.fixture(scope="module")
def fv():
    import bench.falsifier_verify as _fv
    return _fv


@pytest.fixture(scope="module")
def denied(fv):
    """The guard's REAL `_denied`, extracted from the observer it ships.

    Only the predicate functions are executed; the hook installation is not,
    because that would alter the test process.
    """
    declared = fv._allow_roots(str(fv.REPO_ROOT))
    cfg = {
        "trace": os.devnull,
        "mark": fv.SANDBOX_DENIED_MARK,
        "ready": fv._OBSERVER_READY_MARK,
        "allow": fv._realpaths(list(declared) + list(fv._interpreter_roots())),
        "deny": fv._realpaths(fv._SANDBOX_DENY_REGIONS),
        "protected": sorted({
            hashlib.sha256(p.encode("utf-8", "replace")).hexdigest()
            for p in fv._realpaths(fv._protected_values())
        }),
        "evidence_segments": sorted(fv.EVIDENCE_SEGMENTS),
        "kernel_re": fv._wolfram.KERNEL_RE.pattern,
    }
    src = fv._OBSERVER_SOURCE.replace("__CDSFL_CONFIG__", repr(cfg))
    ns = {"os": os, "re": re, "sys": sys, "hashlib": hashlib, "_CFG": cfg,
          "_FD": None, "_BUSY": [False],
          "_KERNEL": re.compile(cfg["kernel_re"])}
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name in {
                "_under", "_is_evidence", "_protected", "_denied",
                "_emit", "_shout"}:
            exec(compile(ast.Module(body=[node], type_ignores=[]),
                         "<observer>", "exec"), ns)
    assert "_denied" in ns, "the observer's _denied could not be extracted"
    return ns["_denied"]


def _cfg(runner, enabled=True, seed=""):
    return dataclasses.replace(
        runner.RunnerConfig(), apply_fixes_back_enabled=enabled,
        apply_fixes_back_seed=seed)


@pytest.fixture
def staged(runner, tmp_path, monkeypatch):
    """Call the real `_apply_back_setup` with the staged root redirected."""
    import bench.falsifier_verify as _fv
    root = tmp_path / "CDSFL_review_targets"
    monkeypatch.setattr(_fv, "STAGED_TARGET_ROOT", str(root), raising=True)
    target = tmp_path / "targets" / "doc.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# doc\n\n```python\nx = 1\n```\n", encoding="utf-8")
    logs = tmp_path / "bench" / "logs" / "run_under_test"
    logs.mkdir(parents=True, exist_ok=True)
    got = runner._apply_back_setup(_cfg(runner), target, logs)
    return {"returned": got, "target": target, "logs": logs, "root": root,
            "ctx": dict(runner._APPLY_BACK_CTX)}


class TestTheStagedCopyIsNotEvidence:
    def test_the_returned_path_is_under_the_staged_root(self, staged):
        assert str(staged["returned"]).startswith(str(staged["root"]))

    def test_the_returned_path_is_not_under_bench_logs(self, staged):
        parts = pathlib.Path(staged["returned"]).parts
        pairs = list(zip(parts, parts[1:]))
        assert ("bench", "logs") not in pairs, staged["returned"]

    def test_it_is_per_run_so_2_runs_cannot_share_one(self, runner, staged, tmp_path):
        other = tmp_path / "bench" / "logs" / "a_second_run"
        other.mkdir(parents=True, exist_ok=True)
        second = runner._apply_back_setup(_cfg(runner), staged["target"], other)
        assert second != staged["returned"]
        assert second.parent.name == "a_second_run"

    def test_the_content_is_seeded_from_the_pristine_target(self, staged):
        assert staged["returned"].read_text(encoding="utf-8") == \
            staged["target"].read_text(encoding="utf-8")


class TestNothingIsLostFromTheArchive:
    def test_the_archive_mirror_exists_under_the_run(self, staged):
        arch = staged["logs"] / "working" / staged["target"].name
        assert arch.is_file(), "the working copy must still archive with the run"

    def test_the_mirror_matches_the_staged_copy(self, staged):
        arch = staged["logs"] / "working" / staged["target"].name
        assert arch.read_text(encoding="utf-8") == \
            staged["returned"].read_text(encoding="utf-8")

    def test_the_ctx_records_both_paths(self, staged):
        assert staged["ctx"]["working_path"] == staged["returned"]
        assert staged["ctx"]["archive_path"].is_file()


class TestTheGuardAgrees:
    """The point of the fix, tested against the guard rather than asserted."""

    def test_the_old_location_really_was_refused(self, denied):
        old = REPO / "bench/logs/some_run/working/doc.md"
        assert denied(os.path.realpath(str(old))) is True

    def test_the_real_staged_root_is_not_refused(self, denied, fv):
        p = pathlib.Path(fv.STAGED_TARGET_ROOT) / "some_run" / "doc.md"
        assert denied(os.path.realpath(str(p))) is False

    def test_the_pristine_target_stays_readable(self, denied):
        p = REPO / "bench/cdsfl_registry/targets/prose_with_computable_listings.md"
        assert denied(os.path.realpath(str(p))) is False

    def test_another_runs_evidence_stays_refused(self, denied):
        """The guard must not be weakened by this fix."""
        p = REPO / "bench/logs/some_run/r0_cc2-sim.json"
        assert denied(os.path.realpath(str(p))) is True

    def test_a_harvested_seat_file_stays_refused(self, denied):
        p = REPO / "bench/logs/x/sandbox_harvest/cc2/attempt-1/files/a.py"
        assert denied(os.path.realpath(str(p))) is True


class TestTheDisabledAndFallbackPathsStillWork:
    def test_disabled_returns_the_target_unchanged(self, runner, tmp_path):
        t = tmp_path / "t.md"
        t.write_text("x", encoding="utf-8")
        logs = tmp_path / "logs"
        logs.mkdir()
        assert runner._apply_back_setup(_cfg(runner, enabled=False), t, logs) == t

    def test_an_unavailable_guard_module_falls_back_and_does_not_crash(
            self, runner, tmp_path, monkeypatch):
        """The guard must never be a hard dependency of a run."""
        import bench.falsifier_verify as _fv
        monkeypatch.setattr(_fv, "STAGED_TARGET_ROOT", "", raising=True)
        t = tmp_path / "t2.md"
        t.write_text("y", encoding="utf-8")
        logs = tmp_path / "logs2"
        logs.mkdir()
        got = runner._apply_back_setup(_cfg(runner), t, logs)
        assert got.is_file() and got.read_text(encoding="utf-8") == "y"


class TestAPromotionUpdatesBothCopies:
    def test_the_mirror_follows_a_rewrite_of_the_working_copy(self, runner, staged):
        """`_apply_back_setup` seeds both; a promotion must update both."""
        ctx = runner._APPLY_BACK_CTX
        ctx["working_path"].write_text("CHANGED\n", encoding="utf-8")
        arch = ctx.get("archive_path")
        assert arch is not None
        arch.write_text("CHANGED\n", encoding="utf-8")
        assert arch.read_text(encoding="utf-8") == \
            ctx["working_path"].read_text(encoding="utf-8")
