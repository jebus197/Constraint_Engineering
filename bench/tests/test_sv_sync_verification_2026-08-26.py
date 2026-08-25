"""Commissioning test for sv's post-push sync verification.

FOUNDER INSTRUCTION 2026-08-26, verbatim: "a push/commit should cause both local
and remote to be *fully* in sync. Surely that is the point of the entire
exercise? Whatever you are doing that might be preventing this, you should fix
it." And separately: sv must finish with "zero errors and zero ambiguity about
the completed sv state".

WHAT WAS WRONG. The session summary read:

    Branch: <b>. Remote before this sv: <N ahead>. Pushed: yes.

Both facts true; neither is the state after the save. A push that pushed a branch
nobody reads produced the same two lines as a push that put the work where the
public can see it. The before-state plus a boolean is not an after-state.

WHAT THIS ASSERTS. Not that the function returns a dict. That it gives DIFFERENT
answers to a synced remote, an unsynced remote, and a branch that was never
pushed -- and that the third is reported as a FAILED MEASUREMENT rather than as
either of the first two, because "could not check" reading as "fine" is the
reassuring-direction failure this project keeps finding.
"""
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import cdsfl_sv as sv  # noqa: E402


def _run(*args, cwd):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=30)


@pytest.fixture
def repo_with_remote(tmp_path):
    """A real git repo on 'main' with a real bare origin, pushed and level."""
    bare = tmp_path / "origin.git"
    work = tmp_path / "work"
    _run("git", "init", "--bare", "-b", "main", str(bare), cwd=tmp_path)
    _run("git", "init", "-b", "main", str(work), cwd=tmp_path)
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "T")):
        _run("git", "config", k, v, cwd=work)
    (work / "a.txt").write_text("one\n")
    _run("git", "add", "-A", cwd=work)
    _run("git", "commit", "-m", "one", cwd=work)
    _run("git", "remote", "add", "origin", str(bare), cwd=work)
    _run("git", "push", "-u", "origin", "main", cwd=work)
    return work


class TestItDiscriminates:
    def test_known_good_a_pushed_branch_reports_in_sync(self, repo_with_remote):
        s = sv._verify_remote_sync(repo_with_remote)
        assert s["in_sync"] is True, f"a level branch did not report in sync: {s}"
        assert s["upstream_ahead"] == 0 and s["upstream_behind"] == 0
        assert not s["error"], f"a clean case reported an error: {s['error']}"

    def test_known_bad_an_unpushed_commit_reports_NOT_in_sync(self, repo_with_remote):
        (repo_with_remote / "b.txt").write_text("two\n")
        _run("git", "add", "-A", cwd=repo_with_remote)
        _run("git", "commit", "-m", "two", cwd=repo_with_remote)
        s = sv._verify_remote_sync(repo_with_remote)
        assert s["in_sync"] is False, "an unpushed commit reported as fully in sync"
        assert s["upstream_ahead"] == 1, f"expected 1 ahead, got {s['upstream_ahead']}"

    def test_known_bad_a_never_pushed_branch_is_a_FAILED_MEASUREMENT(self, repo_with_remote):
        """The case that bit this project: it must not read as either verdict."""
        _run("git", "checkout", "-b", "sidebranch", cwd=repo_with_remote)
        (repo_with_remote / "c.txt").write_text("three\n")
        _run("git", "add", "-A", cwd=repo_with_remote)
        _run("git", "commit", "-m", "three", cwd=repo_with_remote)
        s = sv._verify_remote_sync(repo_with_remote)
        assert s["in_sync"] is False, "an unpushed BRANCH reported as in sync"
        assert s["upstream_ahead"] is None, (
            "a branch with no remote counterpart returned a NUMBER for divergence; "
            "an unmeasurable quantity must be None, not 0"
        )
        assert "never been pushed" in s["error"]

    def test_it_reports_how_far_main_trails_a_side_branch(self, repo_with_remote):
        """The finding that mattered on 2026-08-26: pushing the working branch
        would have left public main 58 commits behind, and sv said nothing."""
        _run("git", "checkout", "-b", "sidebranch", cwd=repo_with_remote)
        for i in range(3):
            (repo_with_remote / f"x{i}.txt").write_text(f"{i}\n")
            _run("git", "add", "-A", cwd=repo_with_remote)
            _run("git", "commit", "-m", f"x{i}", cwd=repo_with_remote)
        s = sv._verify_remote_sync(repo_with_remote)
        assert s["main_behind"] == 3, (
            f"expected main 3 behind, got {s['main_behind']}. Without this the "
            "summary cannot say the public repo is stale."
        )

    def test_on_main_it_does_not_invent_a_main_gap(self, repo_with_remote):
        s = sv._verify_remote_sync(repo_with_remote)
        assert not s.get("main_behind"), (
            f"on main itself, main_behind should be absent/0, got {s['main_behind']}"
        )

    def test_the_three_verdicts_are_not_the_same(self, repo_with_remote, tmp_path):
        synced = sv._verify_remote_sync(repo_with_remote)
        (repo_with_remote / "b.txt").write_text("two\n")
        _run("git", "add", "-A", cwd=repo_with_remote)
        _run("git", "commit", "-m", "two", cwd=repo_with_remote)
        behind = sv._verify_remote_sync(repo_with_remote)
        _run("git", "checkout", "-b", "never", cwd=repo_with_remote)
        (repo_with_remote / "d.txt").write_text("four\n")
        _run("git", "add", "-A", cwd=repo_with_remote)
        _run("git", "commit", "-m", "four", cwd=repo_with_remote)
        unpushed = sv._verify_remote_sync(repo_with_remote)
        triples = [(x["in_sync"], x["upstream_ahead"], bool(x["error"]))
                   for x in (synced, behind, unpushed)]
        assert len(set(triples)) == 3, f"verdicts collapse: {triples}"


class TestTheSentenceSaysTheState:
    def test_the_summary_sentence_names_the_AFTER_state(self, repo_with_remote):
        line = sv._sync_sentence(repo_with_remote, {"branch": "main", "remote_sync": "x"},
                                 pushed=True)
        assert "AFTER" in line, f"summary still reports only a before-state: {line}"
        assert "before this sv" not in line

    def test_an_unverifiable_sentence_says_NOT_VERIFIED_not_in_sync(self, repo_with_remote):
        _run("git", "checkout", "-b", "never", cwd=repo_with_remote)
        (repo_with_remote / "e.txt").write_text("five\n")
        _run("git", "add", "-A", cwd=repo_with_remote)
        _run("git", "commit", "-m", "five", cwd=repo_with_remote)
        line = sv._sync_sentence(repo_with_remote, {"branch": "never", "remote_sync": "x"},
                                 pushed=True)
        assert "NOT VERIFIED" in line, f"an unmeasurable state read as a verdict: {line}"
        assert "fully in sync" not in line


def test_sync_verification_never_raises_on_a_non_repo(tmp_path):
    """It runs after the save has already succeeded; a traceback here would turn
    a successful sv into a non-zero exit."""
    s = sv._verify_remote_sync(tmp_path)
    assert isinstance(s, dict) and s["in_sync"] is False


class TestTheFinalStateBlockIsTheOnlyCompletionClaim:
    """sv printed "State save complete." and a pre-commit `Remote:` line BEFORE
    it committed and pushed. Same defect one level up: a before-state under a
    final-sounding heading. The completion claim now runs last and re-measures.
    """

    def test_a_pushed_save_ends_saying_fully_in_sync(self, repo_with_remote, capsys):
        sv._print_final_state(repo_with_remote, push=True)
        out = capsys.readouterr().out
        assert "SV COMPLETE" in out
        assert "Fully in sync" in out, f"a level remote did not report in sync:\n{out}"
        assert "NOT PUSHED" not in out

    def test_an_unpushed_save_says_NOT_PUSHED_not_in_sync(self, repo_with_remote, capsys):
        """KNOWN-BAD: without --push the work is local only, and the block must
        never imply otherwise."""
        sv._print_final_state(repo_with_remote, push=False)
        out = capsys.readouterr().out
        assert "NOT PUSHED" in out, f"an unpushed save did not say so:\n{out}"
        assert "Fully in sync" not in out

    def test_it_names_the_public_main_gap_on_a_side_branch(self, repo_with_remote, capsys):
        """The case that bit this project on 2026-08-26: the branch push
        succeeds and the public repository still shows nothing."""
        _run("git", "checkout", "-b", "sidework", cwd=repo_with_remote)
        for i in range(2):
            (repo_with_remote / f"s{i}.txt").write_text(f"{i}\n")
            _run("git", "add", "-A", cwd=repo_with_remote)
            _run("git", "commit", "-m", f"s{i}", cwd=repo_with_remote)
        _run("git", "push", "-q", "origin", "sidework", cwd=repo_with_remote)
        sv._print_final_state(repo_with_remote, push=True)
        out = capsys.readouterr().out
        assert "Fully in sync" in out, "the branch itself IS synced and should say so"
        assert "PUBLIC main" in out and "2 COMMITS BEHIND" in out, (
            f"a synced side branch reported success without saying the public "
            f"repository is stale:\n{out}"
        )

    def test_a_never_pushed_branch_reads_as_NOT_VERIFIED(self, repo_with_remote, capsys):
        _run("git", "checkout", "-b", "never", cwd=repo_with_remote)
        (repo_with_remote / "n.txt").write_text("n\n")
        _run("git", "add", "-A", cwd=repo_with_remote)
        _run("git", "commit", "-m", "n", cwd=repo_with_remote)
        sv._print_final_state(repo_with_remote, push=True)
        out = capsys.readouterr().out
        assert "NOT VERIFIED" in out, f"an unmeasurable remote read as a verdict:\n{out}"
        assert "Fully in sync" not in out

    def test_it_reports_a_still_dirty_tree(self, repo_with_remote, capsys):
        """A save that left files uncommitted must not print 'clean'."""
        (repo_with_remote / "left_behind.txt").write_text("x\n")
        sv._print_final_state(repo_with_remote, push=True)
        out = capsys.readouterr().out
        assert "DIRTY" in out, f"an uncommitted path was reported as clean:\n{out}"

    def test_it_never_raises_outside_a_repo(self, tmp_path, capsys):
        sv._print_final_state(tmp_path, push=True)
        assert "SV COMPLETE" in capsys.readouterr().out
