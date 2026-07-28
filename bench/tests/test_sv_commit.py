"""Tests for the sv-script commit path: untracked-file discovery,
commit-message path extraction, and message-vs-staged validation.

These tests regression-guard the fix for the 2026-04-15 defect where
``scripts/cdsfl_sv.py`` produced commit f29d0e9 whose message referenced
three files that had been silently skipped by the hardcoded stager.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from cdsfl_sv import (  # noqa: E402
    _commit_and_push,
    _discover_untracked_in_whitelist,
    _extract_paths_from_message,
    _SAFE_STAGING_DIRS,
    _validate_message_paths,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Minimal git repo with an initial commit, ready for per-test staging."""
    _git("init", "-q", "-b", "main", cwd=tmp_path)
    _git("config", "user.email", "test@example.com", cwd=tmp_path)
    _git("config", "user.name", "Test", cwd=tmp_path)
    _git("config", "commit.gpgsign", "false", cwd=tmp_path)

    # Seed a tracked file so HEAD exists.
    (tmp_path / "README.md").write_text("seed\n")
    _git("add", "README.md", cwd=tmp_path)
    _git("commit", "-q", "-m", "seed", cwd=tmp_path)
    return tmp_path


def _make_file(root: Path, rel: str, content: str = "x\n") -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


# ─────────────────────────────────────────────────────────────────────────────
# _discover_untracked_in_whitelist
# ─────────────────────────────────────────────────────────────────────────────

class TestUntrackedDiscovery:
    def test_discovers_new_file_in_bench(self, git_repo: Path) -> None:
        _make_file(git_repo, "bench/dm/_feedback.py")
        out = _discover_untracked_in_whitelist(git_repo)
        assert "bench/dm/_feedback.py" in out

    def test_discovers_new_test_file(self, git_repo: Path) -> None:
        _make_file(git_repo, "bench/tests/test_feedback_channel.py")
        out = _discover_untracked_in_whitelist(git_repo)
        assert "bench/tests/test_feedback_channel.py" in out

    def test_discovers_markdown_under_experimental_notes(
        self, git_repo: Path,
    ) -> None:
        _make_file(
            git_repo,
            "experimental_notes/Feedback_Channel_Phase10_2026-04-15.md",
        )
        out = _discover_untracked_in_whitelist(git_repo)
        assert (
            "experimental_notes/Feedback_Channel_Phase10_2026-04-15.md" in out
        )

    def test_excludes_gitignored_paths(self, git_repo: Path) -> None:
        (git_repo / ".gitignore").write_text("bench/results/\n")
        _git("add", ".gitignore", cwd=git_repo)
        _git("commit", "-q", "-m", "ignore", cwd=git_repo)
        _make_file(git_repo, "bench/results/secret.json", "{}")
        out = _discover_untracked_in_whitelist(git_repo)
        assert all(not p.startswith("bench/results/") for p in out)

    def test_excludes_top_level_files(self, git_repo: Path) -> None:
        _make_file(git_repo, "NEW_PAPER.md", "# draft\n")
        out = _discover_untracked_in_whitelist(git_repo)
        assert "NEW_PAPER.md" not in out

    def test_excludes_dotfile_caches(self, git_repo: Path) -> None:
        _make_file(git_repo, ".mypy_cache/stuff.json", "{}")
        out = _discover_untracked_in_whitelist(git_repo)
        assert all(not p.startswith(".mypy_cache/") for p in out)

    def test_empty_when_clean(self, git_repo: Path) -> None:
        assert _discover_untracked_in_whitelist(git_repo) == []

    def test_covers_every_advertised_whitelist_dir(
        self, git_repo: Path,
    ) -> None:
        # Regression guard: every directory the module advertises as
        # whitelisted must actually produce a hit when a file is planted.
        for d in _SAFE_STAGING_DIRS:
            _make_file(git_repo, f"{d}probe.txt", "p")
        out = set(_discover_untracked_in_whitelist(git_repo))
        for d in _SAFE_STAGING_DIRS:
            assert f"{d}probe.txt" in out, f"whitelist miss: {d}"


# ─────────────────────────────────────────────────────────────────────────────
# _extract_paths_from_message
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractPathsFromMessage:
    def test_extracts_simple_path(self) -> None:
        msg = "New module: bench/dm/_feedback.py (533 lines)."
        assert _extract_paths_from_message(msg) == ["bench/dm/_feedback.py"]

    def test_extracts_bulleted_path(self) -> None:
        msg = "- bench/dm/_feedback.py (533 lines) — core module"
        assert _extract_paths_from_message(msg) == ["bench/dm/_feedback.py"]

    def test_extracts_backtick_wrapped_path(self) -> None:
        msg = "See `bench/cdsfl_registry/schema.toml` for new blocks."
        assert _extract_paths_from_message(msg) == [
            "bench/cdsfl_registry/schema.toml",
        ]

    def test_strips_trailing_line_suffix(self) -> None:
        msg = "fixed at bench/dm/_feedback.py:120 in the handler"
        assert _extract_paths_from_message(msg) == ["bench/dm/_feedback.py"]

    def test_ignores_non_whitelist_prefix(self) -> None:
        msg = "touched some-vendor/lib/foo.py during debug"
        assert _extract_paths_from_message(msg) == []

    def test_ignores_bare_filename_no_directory(self) -> None:
        msg = "updated cdsfl_operational.md with the new section"
        assert _extract_paths_from_message(msg) == []

    def test_ignores_embedded_path_after_slash(self) -> None:
        # Guards against matching 'bench/foo.py' inside 'other/bench/foo.py'
        msg = "vendor/bench/foo.py is not ours"
        assert _extract_paths_from_message(msg) == []

    def test_extracts_multiple_paths(self) -> None:
        msg = (
            "New module: bench/dm/_feedback.py (533 lines).\n"
            "Tests: bench/tests/test_feedback_channel.py (39 tests).\n"
            "Notes: experimental_notes/Feedback_Channel_Phase10_2026-04-15.md"
        )
        got = _extract_paths_from_message(msg)
        assert got == [
            "bench/dm/_feedback.py",
            "bench/tests/test_feedback_channel.py",
            "experimental_notes/Feedback_Channel_Phase10_2026-04-15.md",
        ]

    def test_deduplicates_preserving_first_order(self) -> None:
        msg = "bench/a.py and bench/b.py; again bench/a.py later"
        assert _extract_paths_from_message(msg) == ["bench/a.py", "bench/b.py"]

    def test_empty_message(self) -> None:
        assert _extract_paths_from_message("") == []

    def test_message_without_paths(self) -> None:
        assert _extract_paths_from_message(
            "sv: schema math zero change, plumbing only"
        ) == []


# ─────────────────────────────────────────────────────────────────────────────
# _validate_message_paths
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateMessagePaths:
    def test_passes_when_all_paths_staged(self, git_repo: Path) -> None:
        _make_file(git_repo, "bench/dm/_feedback.py")
        _git("add", "bench/dm/_feedback.py", cwd=git_repo)
        staged = {"bench/dm/_feedback.py"}
        msg = "- bench/dm/_feedback.py (new module)"
        assert _validate_message_paths(msg, staged, git_repo) == []

    def test_passes_when_path_is_tracked_but_unchanged(
        self, git_repo: Path,
    ) -> None:
        # Prose reference to a pre-existing file: should not abort.
        _make_file(git_repo, "bench/old.py")
        _git("add", "bench/old.py", cwd=git_repo)
        _git("commit", "-q", "-m", "add old.py", cwd=git_repo)
        staged: set[str] = set()
        msg = "follow-up to bench/old.py which now extends..."
        assert _validate_message_paths(msg, staged, git_repo) == []

    def test_reports_missing_untracked_unstaged_path(
        self, git_repo: Path,
    ) -> None:
        # Exact f29d0e9 failure mode: message names path that's neither
        # staged nor tracked.
        staged: set[str] = set()
        msg = "- bench/dm/_feedback.py (533 lines)"
        missing = _validate_message_paths(msg, staged, git_repo)
        assert missing == ["bench/dm/_feedback.py"]

    def test_reports_all_missing(self, git_repo: Path) -> None:
        staged = {"bench/dm/_feedback.py"}  # only one of three staged
        msg = (
            "New: bench/dm/_feedback.py\n"
            "Tests: bench/tests/test_feedback_channel.py\n"
            "Notes: experimental_notes/Feedback_Channel_Phase10_2026-04-15.md"
        )
        missing = _validate_message_paths(msg, staged, git_repo)
        assert missing == [
            "bench/tests/test_feedback_channel.py",
            "experimental_notes/Feedback_Channel_Phase10_2026-04-15.md",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# _commit_and_push integration
# ─────────────────────────────────────────────────────────────────────────────

def _head_files(repo: Path) -> set[str]:
    out = subprocess.run(
        ["git", "show", "--name-only", "--format=", "HEAD"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


class TestCommitAndPushAutoStage:
    def test_regression_f29d0e9_scenario(self, git_repo: Path) -> None:
        """End-to-end: the three files that were silently dropped by the
        pre-fix script now land in the commit.
        """
        _make_file(git_repo, "bench/dm/_feedback.py", "# module\n")
        _make_file(
            git_repo, "bench/tests/test_feedback_channel.py", "# tests\n",
        )
        _make_file(
            git_repo,
            "experimental_notes/Feedback_Channel_Phase10_2026-04-15.md",
            "# notes\n",
        )
        msg = (
            "sv: feedback channel\n\n"
            "New module: bench/dm/_feedback.py\n"
            "Tests: bench/tests/test_feedback_channel.py\n"
            "Notes: experimental_notes/Feedback_Channel_Phase10_2026-04-15.md"
        )
        created = _commit_and_push(
            message=msg, push=False, root=git_repo,
            auto_stage=True, validate_message=True,
        )
        assert created is True
        committed = _head_files(git_repo)
        assert "bench/dm/_feedback.py" in committed
        assert "bench/tests/test_feedback_channel.py" in committed
        assert (
            "experimental_notes/Feedback_Channel_Phase10_2026-04-15.md"
            in committed
        )

    def test_no_auto_stage_skips_untracked(self, git_repo: Path) -> None:
        """With auto_stage=False, an untracked file the message names is
        NOT picked up automatically. If other staged content reaches the
        validation step, validation fires and aborts. This is the design
        intent: the escape hatch disables auto-staging, not correctness.
        """
        # Give the function something unrelated to stage so it reaches
        # validation (otherwise 'nothing to commit' short-circuits earlier).
        _make_file(git_repo, "docs/unrelated.md", "x\n")
        _make_file(git_repo, "bench/dm/_feedback.py")
        # Pre-stage only the unrelated doc; the untracked _feedback.py must
        # NOT be swept up when auto_stage=False.
        _git("add", "docs/unrelated.md", cwd=git_repo)
        msg = "sv: partial\n\nrefers to bench/dm/_feedback.py which is missing"
        with pytest.raises(RuntimeError, match="neither staged nor tracked"):
            _commit_and_push(
                message=msg, push=False, root=git_repo,
                auto_stage=False, validate_message=True,
            )

    def test_validation_failure_aborts_before_commit(
        self, git_repo: Path,
    ) -> None:
        """Message references a path that doesn't exist anywhere. With
        validation on, we must abort without committing.
        """
        # Give the script SOMETHING to stage so we reach validation.
        _make_file(git_repo, "docs/real.md")
        msg = "sv: fix\n\nrefers to bench/ghost/does_not_exist.py"
        before = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        with pytest.raises(RuntimeError, match="neither staged nor tracked"):
            _commit_and_push(
                message=msg, push=False, root=git_repo,
                auto_stage=True, validate_message=True,
            )
        after = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        assert before == after, "HEAD should not advance on validation failure"

    def test_no_validate_message_allows_mismatch(
        self, git_repo: Path,
    ) -> None:
        """Escape hatch: --no-validate-message lets a commit proceed even
        when the message mentions a missing path. Used for rare legacy
        cases. Must still create a commit from whatever IS staged.
        """
        _make_file(git_repo, "docs/real.md")
        msg = "sv: partial\n\nnote: bench/not-here.py is out of scope"
        created = _commit_and_push(
            message=msg, push=False, root=git_repo,
            auto_stage=True, validate_message=False,
        )
        assert created is True
        assert "docs/real.md" in _head_files(git_repo)

    def test_gitignored_file_not_staged(self, git_repo: Path) -> None:
        """.gitignore patterns under a whitelisted directory are honoured."""
        (git_repo / ".gitignore").write_text("bench/results/\n")
        _git("add", ".gitignore", cwd=git_repo)
        _git("commit", "-q", "-m", "ignore", cwd=git_repo)
        _make_file(git_repo, "bench/results/scratch.json", "{}")
        _make_file(git_repo, "bench/real.py", "# real\n")
        msg = "sv: bench/real.py"
        created = _commit_and_push(
            message=msg, push=False, root=git_repo,
            auto_stage=True, validate_message=True,
        )
        assert created is True
        committed = _head_files(git_repo)
        assert "bench/real.py" in committed
        assert "bench/results/scratch.json" not in committed
