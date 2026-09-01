"""A simulated run must operate on a COPY of the repo, not the live one.

Founder ruling 2026-09-01: "A simulation is exactly that. It runs in its own
sandbox with a copy of the current/most recent repo to work on, not the live
repo itself."

What prompted it: panel agents wrote fixes straight into bench/dm/_memory.py --
the experiment's own target -- during two separate runs. Panel agents inherit
this repository as their working directory for code experiments by design
(reference_runner_v2.py:9841, "unset for code runs, where the panel legitimately
needs this repo") and they carry a shell. Reading is intended; nothing stopped a
write.

Why a read-only target was rejected. Measured 2026-09-01: chmod a-w on the file
blocks python open('w'), a shell redirect, and `git checkout --`, but NOT
`sed -i`, which unlinks and recreates the file. Three of four routes is not
protection, because permissions on a file cannot defend it inside a writable
directory.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
LAUNCHER = REPO / "bench" / "tools" / "run_simulated_experiment_sandboxed.sh"


class TestTheLauncherExists:

    def test_it_is_present_and_executable(self):
        assert LAUNCHER.is_file(), (
            "the sandboxed launcher is gone; a simulated run would go back to "
            "operating on the live repository")
        assert os.access(LAUNCHER, os.X_OK), f"{LAUNCHER.name} is not executable"

    def test_it_runs_the_experiment_from_inside_the_worktree(self):
        body = LAUNCHER.read_text(encoding="utf-8")
        # Flags between `add` and `--detach` are allowed: since 2026-09-01 the
        # launcher passes --no-checkout so sparse-checkout can blind the sandbox
        # before any file lands. What must hold is that a DETACHED worktree is
        # created, not the exact flag order.
        assert "git worktree add" in body and "--detach" in body
        assert ('cd "$WT"' in body or 'git -C "$WT"' in body), (
            "the launcher must cd INTO the sandbox. Both harnesses derive their "
            "root from __file__, so running from anywhere else leaves the "
            "target, the panel cwd and every derived path pointing at the live "
            "repository.")

    def test_it_extracts_artefacts_before_teardown(self):
        body = LAUNCHER.read_text(encoding="utf-8")
        # The LAST worktree-remove is the teardown. Since 2026-09-01 there is an
        # EARLIER one on the blinding-refusal path, which aborts before any run
        # happens and so has nothing to extract. Indexing the first occurrence
        # compared the copy against the wrong statement.
        copy_at = body.index("cp -R")
        remove_at = body.rindex("worktree remove")
        assert copy_at < remove_at, (
            "artefacts must be copied out BEFORE the sandbox is removed "
            "(founder, 2026-08-30: delete sandboxes after extracting, not "
            "before)")

    def test_it_refuses_a_dirty_tree(self):
        body = LAUNCHER.read_text(encoding="utf-8")
        assert "REFUSING" in body and "git status --porcelain" in body, (
            "a HEAD worktree built from a dirty tree is not a copy of what is "
            "actually being run")


class TestAWorktreeIsGenuinelyIsolated:
    """Not a source grep: build one and try to reach the canonical file."""

    @pytest.fixture
    def worktree(self):
        sb = Path(tempfile.mkdtemp(prefix="cdsfl_test_wt"))
        wt = sb / "repo"
        rc = subprocess.run(["git", "worktree", "add", "--detach", str(wt), "HEAD"],
                            cwd=str(REPO), capture_output=True).returncode
        if rc != 0:
            pytest.skip("could not create a worktree in this environment")
        try:
            yield wt
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                           cwd=str(REPO), capture_output=True)
            subprocess.run(["rm", "-rf", str(sb)], capture_output=True)

    def test_a_write_in_the_sandbox_does_not_touch_the_canonical_file(self, worktree):
        target = worktree / "bench" / "dm" / "_memory.py"
        if not target.is_file():
            pytest.skip("target absent in this checkout")
        before = (REPO / "bench" / "dm" / "_memory.py").read_bytes()
        target.write_bytes(target.read_bytes() + b"\n# AGENT EDIT\n")
        after = (REPO / "bench" / "dm" / "_memory.py").read_bytes()
        assert before == after, "a sandbox write reached the canonical repository"

    def test_the_run_root_inside_a_worktree_is_the_worktree(self, worktree):
        out = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0,'bench');"
             "import reference_runner_v2 as R; print(R.REPO_ROOT)"],
            cwd=str(worktree), capture_output=True, text=True)
        assert out.returncode == 0, out.stderr[-400:]
        root = Path(out.stdout.strip()).resolve()
        assert root != REPO.resolve(), (
            "REPO_ROOT resolved to the live repository from inside the sandbox, "
            "so the target and the panel cwd would both point at it")
        assert str(worktree.resolve()) == str(root)


class TestTheReportSaysWhereThePanelCouldReach:

    def test_the_provenance_block_is_in_the_report(self):
        src = (REPO / "bench" / "reference_runner_v2.py").read_text(
            encoding="utf-8")
        for key in ("panel_confinement", "panel_cwd_config",
                    "panel_cwd_effective", "is_sandbox_worktree", "run_root"):
            assert f'"{key}"' in src, f"the report no longer records {key}"

    def test_the_sandbox_flag_distinguishes_the_two_cases(self):
        """A linked worktree carries a .git FILE; a clone carries a directory."""
        assert (REPO / ".git").is_dir(), "the canonical repo should hold a .git dir"
        sb = Path(tempfile.mkdtemp(prefix="cdsfl_flag"))
        wt = sb / "repo"
        rc = subprocess.run(["git", "worktree", "add", "--detach", str(wt), "HEAD"],
                            cwd=str(REPO), capture_output=True).returncode
        if rc != 0:
            pytest.skip("could not create a worktree")
        try:
            assert (wt / ".git").is_file(), (
                "the sandbox detector relies on a linked worktree carrying a "
                ".git file; if git changes that, every run will report itself "
                "as unsandboxed")
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                           cwd=str(REPO), capture_output=True)
            subprocess.run(["rm", "-rf", str(sb)], capture_output=True)


class TestExtractionDoesNotTrampleTheArchive:
    """Two defects found before this ever ran to completion, 2026-09-01."""

    def test_the_source_path_has_no_trailing_slash(self):
        """`cp -R src/ dest/` copies src's CONTENTS into dest, not src itself.

        The glob `*/` yields trailing slashes, so the first version would have
        scattered every run's files loose into bench/logs, colliding on every
        same-named file with the last one winning.
        """
        body = LAUNCHER.read_text(encoding="utf-8")
        assert 'cp -R "${d%/}"' in body, (
            "the trailing slash must be stripped from the copy source, or the "
            "extraction scatters directory CONTENTS into bench/logs")

    def test_only_new_directories_are_copied(self):
        """bench/logs holds TRACKED report files, so a HEAD worktree checks out
        every archived run -- 148 of them here. Only what the run created is new.
        """
        body = LAUNCHER.read_text(encoding="utf-8")
        assert 'if [ -e "$REPO/bench/logs/$name" ]' in body, (
            "the launcher must skip run directories that already exist "
            "canonically; copying the whole checked-out archive back is at best "
            "pointless and at worst destructive")
        assert "SKIPPED" in body, "the count of skipped directories must be reported"

    def test_the_extraction_logic_behaves(self, tmp_path):
        """Run the logic, do not read it."""
        wt = tmp_path / "wt" / "bench" / "logs"
        repo = tmp_path / "repo" / "bench" / "logs"
        (wt / "existing_run").mkdir(parents=True)
        (wt / "new_run").mkdir(parents=True)
        (repo / "existing_run").mkdir(parents=True)
        (wt / "existing_run" / "report.json").write_text("from-worktree")
        (wt / "new_run" / "report.json").write_text("new")
        (repo / "existing_run" / "report.json").write_text("canonical")
        (repo / "existing_run" / "raw.json").write_text("untracked-and-precious")

        script = (
            'for d in "$WT"/bench/logs/*/; do [ -d "$d" ] || continue; '
            'name="$(basename "${d%/}")"; '
            'if [ -e "$REPO/bench/logs/$name" ]; then continue; fi; '
            'cp -R "${d%/}" "$REPO/bench/logs/"; done'
        )
        subprocess.run(["bash", "-c", script], check=True, env={
            **os.environ, "WT": str(tmp_path / "wt"), "REPO": str(tmp_path / "repo")})

        assert (repo / "new_run" / "report.json").read_text() == "new", (
            "the new run directory was not copied as a directory")
        assert (repo / "existing_run" / "report.json").read_text() == "canonical", (
            "an existing canonical artefact was overwritten from the worktree")
        assert (repo / "existing_run" / "raw.json").is_file(), (
            "a gitignored artefact that only exists canonically was lost")
        loose = [p for p in repo.iterdir() if p.is_file()]
        assert loose == [], f"files were scattered into bench/logs: {loose}"


class TestTheSandboxIsBlinded:
    """The answers must not be in the reviewers' working directory.

    Measured 2026-09-01 before this was closed: a plain worktree exposed 149 run
    directories, 54 report JSONs, 325 experimental_notes files and 29,899
    severity values -- including exp45's 12 criticals WITH their severities --
    to agents armed with Bash, Read, Grep and Glob. Every sim-versus-real
    severity comparison made before the fix was measured through that hole.
    """

    def test_the_launcher_excludes_the_answer_surfaces(self):
        body = LAUNCHER.read_text(encoding="utf-8")
        assert "sparse-checkout" in body, "the sandbox is no longer blinded"
        for path in ("/bench/logs/", "/bench/results/", "/experimental_notes/"):
            assert f"!{path}" in body, f"{path} is no longer excluded"

    def test_it_refuses_to_run_if_the_blinding_failed(self):
        body = LAUNCHER.read_text(encoding="utf-8")
        assert "blinding failed" in body, (
            "a sandbox that silently keeps the answers is worse than no sandbox, "
            "because the numbers it produces look clean")

    def test_it_recreates_the_logs_directory_the_runner_writes_to(self):
        body = LAUNCHER.read_text(encoding="utf-8")
        assert 'mkdir -p "$WT/bench/logs"' in body, (
            "the exclusion removes bench/logs, which the runner writes into")
