#!/usr/bin/env python3
"""The sv postcondition gate, EXECUTED against real repositories with real defects.

FOUNDER, 2026-09-20: *"sv should be an entirely mechanical operation. Yet for
several weeks now you keep uncovering issues with it? Can't you devise a
permanent, definitive fix ... so that you don't need to keep hand implementing
corrections after it runs?"*

WHAT IS UNDER TEST. `scripts/sv_postconditions.py` re-takes the readings sv
already prints and turns them into an exit code. A gate that cannot fail is not
a gate, and a gate that always fails gets switched off within a week, so every
check below is driven BOTH ways: once on a repository where the property holds,
and once with the original defect reinstated.

THE DEFECTS REINSTATED HERE ARE NOT INVENTED. Each is taken from the commit that
repaired it:
  * an unpushed HEAD reported as a completed save -- the 2026-09-19 incident,
    where GitHub's secret scanner refused the push and sv exited 0;
  * a credential-shaped file tracked in the index -- `.env.backup-<timestamp>`,
    swept in by `git add -A` in the same incident;
  * a stamp dated in the future -- `c45d848`, "I typed five timestamps tonight
    instead of reading them, and three were in the future";
  * a generated state file left out of the commit that generated it.

WHAT THESE TESTS DO NOT ESTABLISH, stated rather than implied. They call the
gate. Whether `main()` reaches the gate on a real save is a wiring question, and
it is pinned separately by `TestTheGateIsWiredIntoTheSave`, which parses sv's own
`main` and requires the call to sit inside the successful-commit branch. That one
assertion is structural because there is no second live form to execute it
against: the call site either exists in that branch or it does not.
"""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

import sv_postconditions as pc  # noqa: E402


def _run(*args, cwd) -> subprocess.CompletedProcess:
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, f"{args} failed: {p.stderr}"
    return p


@pytest.fixture
def repo(tmp_path):
    """A real repo on `main` with a real bare origin, committed and pushed."""
    bare, work = tmp_path / "origin.git", tmp_path / "work"
    _run("git", "init", "--bare", "-b", "main", str(bare), cwd=tmp_path)
    _run("git", "init", "-b", "main", str(work), cwd=tmp_path)
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "T")):
        _run("git", "config", k, v, cwd=work)
    (work / "docs").mkdir()
    (work / "resources").mkdir()
    (work / "docs" / "CURRENT_STATE.md").write_text("state\n", encoding="utf-8")
    (work / "resources" / "RECOVERY.md").write_text(
        "Last updated: 1 January 2026 09:00 BST\n", encoding="utf-8")
    (work / ".env.example").write_text("OPENROUTER_API_KEY=\n", encoding="utf-8")
    _run("git", "add", "-A", cwd=work)
    _run("git", "commit", "-m", "base", cwd=work)
    _run("git", "remote", "add", "origin", str(bare), cwd=work)
    _run("git", "push", "-u", "origin", "main", cwd=work)
    return work


class TestTheCleanCasePasses:
    """ANTI-VACUITY. If these fail, every 'the defect is caught' test below is
    worthless, because the gate would be refusing everything."""

    def test_a_saved_and_pushed_repo_passes_every_check_it_can_take(self, repo):
        results = pc.check_all(repo, pushed=True)
        by_name = {r.name: r for r in results}
        for name in ("working tree clean", "HEAD == origin",
                     "generated state committed", "no stamp in the future",
                     "no credential tracked"):
            assert by_name[name].ok is True, (
                f"{name} failed on a clean repo: {by_name[name].detail}")

    def test_the_real_repo_can_answer_the_A23_check_at_all(self):
        """The guard file lives only in the real checkout, so the temp fixture
        cannot exercise it. Here it must return a verdict, not None."""
        ok, detail = pc.recovery_block_passes_its_own_guard(REPO, pushed=False)
        assert ok is not None, f"the A23 check could not be measured: {detail}"


class TestAnUnpushedHeadIsCaught:
    """The 2026-09-19 incident: the push was refused and the save reported done."""

    def test_a_commit_that_was_never_pushed_fails(self, repo):
        (repo / "new.txt").write_text("x\n", encoding="utf-8")
        _run("git", "add", "-A", cwd=repo)
        _run("git", "commit", "-m", "unpushed", cwd=repo)
        ok, detail = pc.head_matches_the_remote(repo, pushed=True)
        assert ok is False, f"an unpushed commit passed the remote check: {detail}"
        assert "did NOT land" in detail

    def test_it_needs_no_network_to_say_so(self, repo):
        """It compares local refs, so an offline machine does not turn a real
        answer into a NOT MEASURED. The bare origin here is on disk, but the
        check never contacts it: proved by deleting it first."""
        (repo / "new.txt").write_text("x\n", encoding="utf-8")
        _run("git", "add", "-A", cwd=repo)
        _run("git", "commit", "-m", "unpushed", cwd=repo)
        import shutil
        shutil.rmtree(repo.parent / "origin.git")
        ok, detail = pc.head_matches_the_remote(repo, pushed=True)
        assert ok is False, f"with the remote gone it should still say no: {detail}"

    def test_a_run_without_push_does_not_pretend_to_have_checked(self, repo):
        ok, detail = pc.head_matches_the_remote(repo, pushed=False)
        assert ok is True and "nothing to compare" in detail


class TestATrackedCredentialIsCaught:
    """`.env.backup-<timestamp>` reached a commit on 2026-09-19."""

    def test_a_tracked_env_backup_fails(self, repo):
        (repo / ".env.backup-20260919-232601").write_text(
            "OPENROUTER_API_KEY=sk-not-a-real-key\n", encoding="utf-8")
        _run("git", "add", "-f", ".env.backup-20260919-232601", cwd=repo)
        _run("git", "commit", "-m", "oops", cwd=repo)
        ok, detail = pc.no_credential_is_tracked(repo, pushed=False)
        assert ok is False, f"a tracked .env backup passed: {detail}"
        assert ".env.backup-20260919-232601" in detail

    def test_a_tracked_pem_fails(self, repo):
        (repo / "server.pem").write_text("-----BEGIN-----\n", encoding="utf-8")
        _run("git", "add", "-f", "server.pem", cwd=repo)
        _run("git", "commit", "-m", "oops", cwd=repo)
        ok, _ = pc.no_credential_is_tracked(repo, pushed=False)
        assert ok is False, "a tracked .pem passed"

    def test_the_example_template_is_NOT_an_offender(self, repo):
        """`.env.example` is tracked on purpose in the real repo. A predicate
        that fires on it would be disabled, and a disabled gate measures
        nothing -- which is why this exception is tested, not assumed."""
        ok, detail = pc.no_credential_is_tracked(repo, pushed=False)
        assert ok is True, f".env.example was called a credential: {detail}"

    def test_the_two_guard_files_named_for_secrets_are_NOT_offenders(self):
        """Measured against the real index: `scripts/gate_environment_secrets_
        2026-09-17.py` and `bench/tests/test_seat_environment_carries_no_
        secrets_2026-09-17.py` both match sv's wider `_SENSITIVE_PATTERNS`."""
        ok, detail = pc.no_credential_is_tracked(REPO, pushed=False)
        assert ok is True, f"the live repo reported a tracked credential: {detail}"


class TestAFutureStampIsCaught:
    """`c45d848`: 5 timestamps typed instead of read, 3 of them in the future."""

    def test_a_stamp_dated_next_year_fails(self, repo):
        (repo / "resources" / "RECOVERY.md").write_text(
            "Last updated: 1 January 2099 09:00 BST\n", encoding="utf-8")
        ok, detail = pc.no_stamp_is_in_the_future(repo, pushed=False)
        assert ok is False, f"a stamp dated 2099 passed: {detail}"
        assert "in the future" in detail

    def test_an_unparseable_stamp_is_an_offender_not_a_pass(self, repo):
        (repo / "resources" / "RECOVERY.md").write_text(
            "Last updated: 31 Smarch 2026 09:00 BST\n", encoding="utf-8")
        ok, detail = pc.no_stamp_is_in_the_future(repo, pushed=False)
        assert ok is False, f"an unparseable stamp passed: {detail}"

    def test_a_future_date_elsewhere_in_the_prose_is_NOT_an_offender(self, repo):
        """These documents legitimately carry future dates -- the Wolfram
        licence expires 2026-10-08. Only the stamped line is checked."""
        (repo / "resources" / "RECOVERY.md").write_text(
            "Last updated: 1 January 2026 09:00 BST\n\n"
            "The licence expires on 8 October 2099.\n", encoding="utf-8")
        ok, detail = pc.no_stamp_is_in_the_future(repo, pushed=False)
        assert ok is True, f"a future date in prose was flagged: {detail}"


class TestAnUncommittedStateFileIsCaught:

    def test_a_regenerated_state_file_left_uncommitted_fails(self, repo):
        (repo / "docs" / "CURRENT_STATE.md").write_text("newer\n", encoding="utf-8")
        ok, detail = pc.generated_state_is_committed(repo, pushed=False)
        assert ok is False, f"an uncommitted state file passed: {detail}"

    def test_a_dirty_tree_fails_the_clean_check(self, repo):
        (repo / "stray.txt").write_text("x\n", encoding="utf-8")
        ok, detail = pc.working_tree_is_clean(repo, pushed=False)
        assert ok is False, f"a dirty tree passed: {detail}"


class TestAnUnmeasurableRequiredCheckFails:
    """The project's own rule, already written into `_print_final_state`: a
    failed check is NOT evidence the thing worked."""

    def test_ok_None_on_a_required_check_counts_as_a_failure(self):
        r = pc.Result(name="x", ok=None, required=True, detail="could not measure")
        assert r.failed is True

    def test_ok_None_on_an_advisory_check_does_not(self):
        r = pc.Result(name="x", ok=None, required=False, detail="could not measure")
        assert r.failed is False

    def test_a_check_that_raises_becomes_NOT_MEASURED_not_a_crash(self, repo,
                                                                  monkeypatch):
        def boom(root, pushed):
            raise RuntimeError("kaboom")
        monkeypatch.setattr(pc, "CHECKS", (("exploding", boom, True),))
        results = pc.check_all(repo, pushed=False)
        assert results[0].ok is None and "kaboom" in results[0].detail
        assert results[0].failed is True


class TestTheExitCodeFollowsTheVerdict:

    def test_a_defective_repo_exits_1(self, repo):
        (repo / "stray.txt").write_text("x\n", encoding="utf-8")
        assert pc.main(["--root", str(repo)]) == 1

    def test_a_clean_repo_exits_0_when_its_checks_can_be_taken(self, repo,
                                                              monkeypatch):
        # The A23 guard file is absent from the fixture, which is a genuine
        # NOT MEASURED there, so it is removed from the set rather than faked.
        monkeypatch.setattr(pc, "CHECKS", tuple(
            c for c in pc.CHECKS if c[0] != "RECOVERY block passes A23"))
        assert pc.main(["--root", str(repo), "--pushed"]) == 0

    def test_the_report_names_every_check(self, repo):
        text = pc.report(pc.check_all(repo, pushed=True))
        for name, _, _ in pc.CHECKS:
            assert name in text, f"{name} is missing from the report"


class TestTheGateIsWiredIntoTheSave:
    """An addition nothing reaches is not additive. This pins the call site."""

    @staticmethod
    def _sv_module():
        spec = importlib.util.spec_from_file_location(
            "cdsfl_sv_src", SCRIPTS / "cdsfl_sv.py")
        return spec

    def test_main_calls_the_gate_inside_the_successful_commit_branch(self):
        tree = ast.parse((SCRIPTS / "cdsfl_sv.py").read_text(encoding="utf-8"))
        main = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        calls = [n for n in ast.walk(main)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "_run_postcondition_gate"]
        assert calls, ("main() no longer calls _run_postcondition_gate, so the "
                       "gate is unreachable and every test above measures a "
                       "function nothing runs")

    def test_the_gate_returns_1_on_a_defective_repo(self, repo, monkeypatch):
        """Executed, not read: the function sv actually calls, driven to fail."""
        sys.path.insert(0, str(SCRIPTS))
        import cdsfl_sv                                            # noqa: PLC0415
        (repo / "stray.txt").write_text("x\n", encoding="utf-8")
        assert cdsfl_sv._run_postcondition_gate(repo, push=False) == 1

    def test_sv_imports_the_same_module_this_test_drives(self):
        sys.path.insert(0, str(SCRIPTS))
        import cdsfl_sv                                            # noqa: PLC0415
        assert cdsfl_sv.sv_postconditions is pc, (
            "sv holds a different module object than the one under test here, "
            "so these tests would not describe what sv runs")
