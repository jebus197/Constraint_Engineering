"""A blinded sandbox must not be able to read the archive out of git.

The sandbox excludes bench/logs, bench/results and experimental_notes by sparse
checkout, and prints "blinded: 0 files" once it has verified the working tree is
empty of them.

That verification was insufficient and hid a live leak. Sparse checkout removes
files from the WORKING TREE. A linked worktree's `.git` file points at the main
repository's object store, so the whole archive stays reachable by `git show`.
Measured on 2026-09-01, inside a sandbox that had just printed "blinded: 0
files":

    git -C <sandbox> show HEAD:bench/logs/exp45_..._report.json
      -> 39 entries, 39 severities, 12 critical at >= 0.7
      -> exact values 0.82, 0.80, 0.80, 0.80, 0.80, 0.78, 0.78, 0.78

exp45 is the reference outcome the simulation is compared against, and panel
agents carry Bash. Its answer key was one command away in every simulated run to
date, including the one that converged at round 4 that day.

The run now happens in a plain copy with no git linkage. That also unblocks
canary seeding, whose `seed()` refuses a target inside a git work tree for the
same reason: `git diff` returns the planted set at precision 1.000.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bench" / "tools" / "run_simulated_experiment_sandboxed.sh"


@pytest.fixture(scope="module")
def script():
    return SCRIPT.read_text(encoding="utf-8")


class TestTheScriptSeversHistory:
    def test_the_run_happens_in_a_copy_not_the_worktree(self, script):
        assert 'RUN="$SANDBOX/run"' in script
        assert 'cd "$RUN" && python3 bench/tools/run_simulated_experiment.py' in script, (
            "the run must execute in the severed copy, not the git worktree")

    def test_the_copy_excludes_git(self, script):
        assert "--exclude=.git" in script

    def test_it_refuses_to_run_if_history_is_reachable(self, script):
        assert 'git -C "$RUN" rev-parse --git-dir' in script, (
            "nothing checks that history is actually unreachable; the "
            "file-counting guard passed a sandbox with the whole archive "
            "readable")
        i = script.index('git -C "$RUN" rev-parse --git-dir')
        assert "exit 1" in script[i:i + 400], (
            "reachable history must abort the run, not warn")

    def test_the_worktree_is_removed_before_the_run(self, script):
        run_at = script.index('cd "$RUN" && python3')
        removes = [m.start() for m in
                   re.finditer(r'git worktree remove --force "\$WT"', script)]
        assert any(r < run_at for r in removes), (
            "the worktree must be gone before the panel starts, or its .git "
            "file is still there to follow")

    def test_extraction_reads_the_run_directory(self, script):
        assert 'for d in "$RUN"/bench/logs/*/' in script, (
            "results are extracted from the worktree, which no longer exists "
            "at that point -- the run's output would be silently discarded")


class TestTheLeakItself:
    """Pin the mechanism, so a future change that reintroduces it fails here."""

    def test_a_linked_worktree_can_read_excluded_paths_from_history(self, tmp_path):
        """The defect, reproduced from first principles on a throwaway repo."""
        origin = tmp_path / "origin"
        origin.mkdir()
        run = lambda *a, **k: subprocess.run(  # noqa: E731
            a, cwd=str(k.get("cwd", origin)), capture_output=True, text=True,
            timeout=120)
        run("git", "init", "-q")
        run("git", "config", "user.email", "t@t")
        run("git", "config", "user.name", "t")
        secret = origin / "answers"
        secret.mkdir()
        (secret / "key.json").write_text('{"severity": 0.82}')
        (origin / "code.py").write_text("x = 1\n")
        run("git", "add", "-A")
        run("git", "commit", "-qm", "seed")

        wt = tmp_path / "wt"
        run("git", "worktree", "add", "--no-checkout", "--detach", str(wt), "HEAD")
        gitdir = subprocess.run(["git", "-C", str(wt), "rev-parse", "--git-dir"],
                                capture_output=True, text=True, timeout=60).stdout.strip()
        subprocess.run(["git", "-C", str(wt), "sparse-checkout", "init", "--no-cone"],
                       capture_output=True, timeout=60)
        Path(gitdir, "info", "sparse-checkout").write_text("/*\n!/answers/\n")
        subprocess.run(["git", "-C", str(wt), "checkout", "HEAD"],
                       capture_output=True, timeout=60)

        assert not (wt / "answers").exists(), "sparse checkout did not exclude"
        leaked = subprocess.run(
            ["git", "-C", str(wt), "show", "HEAD:answers/key.json"],
            capture_output=True, text=True, timeout=60)
        assert "0.82" in leaked.stdout, (
            "this test can no longer demonstrate the leak it guards against")

        # And the fix: a plain copy with no .git cannot do it.
        copy = tmp_path / "copy"
        copy.mkdir()
        subprocess.run(f'tar -C "{wt}" --exclude=.git -cf - . | tar -C "{copy}" -xf -',
                       shell=True, timeout=120)
        (copy / ".git").unlink(missing_ok=True)
        sealed = subprocess.run(["git", "-C", str(copy), "show", "HEAD:answers/key.json"],
                                capture_output=True, text=True, timeout=60)
        assert "0.82" not in sealed.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
