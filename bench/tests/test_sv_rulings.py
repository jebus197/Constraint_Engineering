"""Tests for the founder rulings of 2026-08-05 applied to ``scripts/cdsfl_sv.py``.

Three rulings are pinned here.

  RULING 4  sv refuses to commit when the save is not complete, and prints an
            alert that says WHY it fired and WHAT to look at — not merely that
            something is missing. An override flag exists for deliberate
            omissions. "Complete" means: a memory file has changed since the
            previous sv commit, the Open Brain capture path is reachable, and
            the tracker's two copies agree.

  RULING 3  the operational-tracker direction is inverted: the REPO copy is
            canonical, the Desktop copy is the mirror. sv refreshes the Desktop
            copy from the repo — EXCEPT when the Desktop copy is newer, which is
            the signature of a hand edit that has not been carried into the
            repo. Overwriting that would be data loss, so sv refuses and demands
            an explicit flag.

  RULING 7  the persistent-memory index is CHECKED, not written: size against
            the loader limit, broken links, orphaned memory files, and the
            one-line rule. All are reports except the size check, which refuses
            inside 5% of the limit, because the failure mode there is silent
            truncation of the newest entries.

Everything here is offline and hermetic. No real Open Brain call is made (the
subprocess runner is injected in every test), no real Desktop or persistent
memory folder is touched (every path is a tmp_path), and no commit is created
outside a throwaway git repo. sv is never run with --commit or --push.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cdsfl_sv as sv  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

class _Result:
    """Stand-in for subprocess.CompletedProcess."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class _FakeRunner:
    """Records every command and replies from a scripted list.

    Nothing is executed. The recorded commands are themselves an assertion
    target: the pre-flight must never invoke a writing subcommand.
    """

    def __init__(self, *replies: Any) -> None:
        self.replies = list(replies)
        self.commands: list[list[str]] = []

    def __call__(self, cmd, **kwargs) -> _Result:
        self.commands.append([str(c) for c in cmd])
        reply = self.replies.pop(0) if self.replies else _Result()
        if isinstance(reply, BaseException):
            raise reply
        return reply


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-q", "-b", "main", cwd=repo)
    _git("config", "user.email", "test@example.com", cwd=repo)
    _git("config", "user.name", "Test", cwd=repo)
    _git("config", "commit.gpgsign", "false", cwd=repo)
    (repo / "seed.txt").write_text("seed\n")
    _git("add", "seed.txt", cwd=repo)
    _git("commit", "-q", "-m", "seed", cwd=repo)
    return repo


def _commit(repo: Path, message: str, name: str = "f.txt") -> None:
    (repo / name).write_text(f"{message}\n")
    _git("add", name, cwd=repo)
    _git("commit", "-q", "-m", message, cwd=repo)


@pytest.fixture
def memory_dir(tmp_path: Path) -> Path:
    mem = tmp_path / "memory"
    mem.mkdir()
    return mem


def _set_mtime(path: Path, epoch: float) -> None:
    os.utime(path, (epoch, epoch))


def _snapshot(directory: Path) -> set[tuple[str, int, float]]:
    return {
        (p.name, p.stat().st_size, p.stat().st_mtime)
        for p in directory.rglob("*") if p.is_file()
    }


# ─────────────────────────────────────────────────────────────────────────────
# RULING 4 (a) — a save with no memory change is not a complete save
# ─────────────────────────────────────────────────────────────────────────────

class TestMemoryUpdatedCheck:
    def test_memory_untouched_since_the_previous_sv_commit_fails(
        self, git_repo: Path, memory_dir: Path,
    ) -> None:
        note = memory_dir / "MEMORY.md"
        note.write_text("index\n")
        _set_mtime(note, 1_700_000_000)  # 2023 — long before any commit here
        _commit(git_repo, "sv: previous state save")

        check = sv._check_memory_updated(git_repo, mem_dir=memory_dir)
        assert check.passed is False
        assert check.name == "memory-updated"
        assert "MEMORY.md" in check.observed
        assert "BEFORE the previous sv commit" in check.observed
        assert check.override == "--allow-incomplete-save"

    def test_memory_touched_after_the_previous_sv_commit_passes(
        self, git_repo: Path, memory_dir: Path,
    ) -> None:
        _commit(git_repo, "sv: previous state save")
        note = memory_dir / "cdsfl_session.md"
        note.write_text("this session\n")  # written now, i.e. after the commit

        check = sv._check_memory_updated(git_repo, mem_dir=memory_dir)
        assert check.passed is True
        assert "cdsfl_session.md" in check.observed

    def test_no_previous_sv_commit_is_reported_as_unperformed_not_as_a_pass(
        self, git_repo: Path, memory_dir: Path,
    ) -> None:
        """An unverifiable check must not read as a verified one."""
        (memory_dir / "MEMORY.md").write_text("index\n")
        check = sv._check_memory_updated(git_repo, mem_dir=memory_dir)
        assert check.passed is False
        assert "could not be performed" in check.observed
        assert "not the same as passing" in check.observed

    def test_missing_memory_folder_fails(self, git_repo: Path, tmp_path: Path) -> None:
        check = sv._check_memory_updated(git_repo, mem_dir=tmp_path / "absent")
        assert check.passed is False
        assert "no such folder" in check.observed

    def test_a_folder_with_no_markdown_fails(
        self, git_repo: Path, memory_dir: Path,
    ) -> None:
        _commit(git_repo, "sv: previous state save")
        (memory_dir / "notes.txt").write_text("not markdown\n")
        check = sv._check_memory_updated(git_repo, mem_dir=memory_dir)
        assert check.passed is False
        assert "no .md files" in check.observed

    def test_a_touched_non_markdown_file_does_not_satisfy_the_check(
        self, git_repo: Path, memory_dir: Path,
    ) -> None:
        """A Finder artefact must not be able to certify a session as saved."""
        stale = memory_dir / "MEMORY.md"
        stale.write_text("index\n")
        _set_mtime(stale, 1_700_000_000)
        _commit(git_repo, "sv: previous state save")
        (memory_dir / ".DS_Store").write_bytes(b"\x00")  # newest file in the folder

        check = sv._check_memory_updated(git_repo, mem_dir=memory_dir)
        assert check.passed is False

    def test_sv_prefix_inside_a_commit_body_is_not_an_sv_commit(
        self, git_repo: Path,
    ) -> None:
        """``git log --grep`` matches the whole message; the subject decides."""
        _commit(git_repo, "sv: the real one")
        (git_repo / "g.txt").write_text("x\n")
        _git("add", "g.txt", cwd=git_repo)
        subprocess.run(
            ["git", "commit", "-q", "-m", "chore: unrelated\n\nsv: mentioned in the body"],
            cwd=git_repo, capture_output=True, text=True, check=True,
        )
        found = sv._previous_sv_commit(git_repo)
        assert found is not None
        assert found[1] == "sv: the real one"

    def test_no_sv_commit_at_all_returns_none(self, git_repo: Path) -> None:
        assert sv._previous_sv_commit(git_repo) is None


# ─────────────────────────────────────────────────────────────────────────────
# RULING 4 (b) — the Open Brain capture path, pre-flighted without writing
# ─────────────────────────────────────────────────────────────────────────────

class TestOpenBrainPreflight:
    def _ok_runner(self, resolved: Path) -> _FakeRunner:
        return _FakeRunner(
            _Result(0, f"{resolved}\n"),
            _Result(0, "Database connection: OK\n  Host: localhost:5432\n"),
        )

    def test_passes_when_the_import_resolves_inside_the_canonical_checkout(
        self, tmp_path: Path,
    ) -> None:
        expected = tmp_path / "OpenBrain"
        runner = self._ok_runner(expected / "open_brain")
        check = sv._check_open_brain(tmp_path, runner=runner, expected_root=expected)
        assert check.passed is True
        assert "Database connection: OK" in check.observed

    def test_the_preflight_never_writes_to_the_store(self, tmp_path: Path) -> None:
        """The capture is a WRITE and happens post-commit. The pre-flight must
        prove the path with read-only probes only."""
        expected = tmp_path / "OpenBrain"
        runner = self._ok_runner(expected / "open_brain")
        sv._check_open_brain(tmp_path, runner=runner, expected_root=expected)
        assert len(runner.commands) == 2
        for cmd in runner.commands:
            assert "capture" not in cmd
            assert "import" not in cmd  # the CLI's import subcommand
            assert "update-task" not in cmd
            assert "seal-epoch" not in cmd
        assert runner.commands[1][-1] == "status"

    def test_fails_when_the_import_resolves_to_another_checkout(
        self, tmp_path: Path,
    ) -> None:
        """The defect this closes: a stale fork of the same package elsewhere
        on the machine takes the import, and captures land in its store."""
        expected = tmp_path / "OpenBrain"
        stale = tmp_path / "Project_Genesis" / "open_brain"
        runner = _FakeRunner(_Result(0, f"{stale}\n"))
        check = sv._check_open_brain(tmp_path, runner=runner, expected_root=expected)
        assert check.passed is False
        assert str(stale) in check.observed
        assert "different checkout" in check.observed
        assert len(runner.commands) == 1, "must not probe the store of the wrong install"

    def test_fails_when_the_package_cannot_be_imported(self, tmp_path: Path) -> None:
        runner = _FakeRunner(_Result(1, "", "ModuleNotFoundError: No module named 'open_brain'"))
        check = sv._check_open_brain(tmp_path, runner=runner, expected_root=tmp_path / "OpenBrain")
        assert check.passed is False
        assert "ModuleNotFoundError" in check.observed

    def test_fails_when_the_import_prints_nothing(self, tmp_path: Path) -> None:
        runner = _FakeRunner(_Result(0, "   \n"))
        check = sv._check_open_brain(tmp_path, runner=runner, expected_root=tmp_path / "OpenBrain")
        assert check.passed is False
        assert "install location is unknown" in check.observed

    def test_fails_when_the_store_does_not_answer(self, tmp_path: Path) -> None:
        expected = tmp_path / "OpenBrain"
        runner = _FakeRunner(
            _Result(0, f"{expected / 'open_brain'}\n"),
            _Result(1, "", "Database connection: FAILED"),
        )
        check = sv._check_open_brain(tmp_path, runner=runner, expected_root=expected)
        assert check.passed is False
        assert "the store did not answer" in check.observed
        assert "FAILED" in check.observed

    def test_fails_when_the_probe_cannot_be_launched(self, tmp_path: Path) -> None:
        runner = _FakeRunner(OSError("no interpreter"))
        check = sv._check_open_brain(tmp_path, runner=runner, expected_root=tmp_path / "OpenBrain")
        assert check.passed is False
        assert "OSError" in check.observed

    def test_a_store_timeout_fails_rather_than_propagating(self, tmp_path: Path) -> None:
        expected = tmp_path / "OpenBrain"
        runner = _FakeRunner(
            _Result(0, f"{expected / 'open_brain'}\n"),
            subprocess.TimeoutExpired(cmd="status", timeout=30),
        )
        check = sv._check_open_brain(tmp_path, runner=runner, expected_root=expected)
        assert check.passed is False
        assert "TimeoutExpired" in check.observed

    def test_the_canonical_root_is_the_documented_install(self) -> None:
        """A typo here would silently accept the stale fork."""
        assert sv._OPEN_BRAIN_ROOT == Path.home() / "Developer_Projects" / "OpenBrain"


# ─────────────────────────────────────────────────────────────────────────────
# RULING 3 — the repo copy is canonical; the Desktop copy is never clobbered
#            when it is the newer of the two
# ─────────────────────────────────────────────────────────────────────────────

OLD = 1_700_000_000.0
NEW = 1_800_000_000.0


class TestTrackerReconciliation:
    def _pair(
        self, tmp_path: Path, repo_text: str, desk_text: str,
        repo_time: float = OLD, desk_time: float = OLD,
    ) -> tuple[Path, Path, Path]:
        root = tmp_path / "repo"
        repo_copy = root / sv._TRACKER_MIRROR_REL
        repo_copy.parent.mkdir(parents=True, exist_ok=True)
        repo_copy.write_text(repo_text, encoding="utf-8")
        _set_mtime(repo_copy, repo_time)
        desk = tmp_path / "Desktop" / "CDSFL_Agent_Operational_Plan.md"
        desk.parent.mkdir(parents=True, exist_ok=True)
        desk.write_text(desk_text, encoding="utf-8")
        _set_mtime(desk, desk_time)
        return root, repo_copy, desk

    def test_repo_copy_newer_refreshes_the_desktop_mirror(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        root, repo_copy, desk = self._pair(
            tmp_path, "canonical\nnew line\n", "stale\n",
            repo_time=NEW, desk_time=OLD,
        )
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is True
        assert desk.read_text() == repo_copy.read_text()
        out = capsys.readouterr().out
        assert "MIRROR-REFRESHED" in out

    def test_desktop_copy_newer_refuses_and_writes_nothing(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        """The hand-edited Desktop copy is the case this ruling exists to
        protect. Silently overwriting it would be data loss."""
        root, repo_copy, desk = self._pair(
            tmp_path, "canonical\n", "hand edit made on the Desktop\n",
            repo_time=OLD, desk_time=NEW,
        )
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is False
        assert desk.read_text() == "hand edit made on the Desktop\n"
        assert repo_copy.read_text() == "canonical\n"
        assert check.override == "--overwrite-newer-desktop-tracker"
        captured = capsys.readouterr()
        assert "REFUSED-DESKTOP-NEWER" in captured.out
        assert "--overwrite-newer-desktop-tracker" in captured.err

    def test_the_refusal_prints_both_mtimes_and_a_diffstat(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        root, _repo_copy, desk = self._pair(
            tmp_path, "shared\nONLY-IN-REPO\n", "shared\nONLY-ON-DESKTOP\n",
            repo_time=OLD, desk_time=NEW,
        )
        sv._reconcile_tracker(root, desktop=desk)
        err = capsys.readouterr().err
        assert "modified 2023-11-14" in err or "modified 20" in err
        assert err.count("modified ") >= 2, "both mtimes must be shown"
        assert "Differing lines:" in err
        assert "ONLY-IN-REPO" in err
        assert "ONLY-ON-DESKTOP" in err

    def test_differing_copies_with_the_same_mtime_also_refuse(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        """The ruling authorises a sync when the repo copy is newer OR they
        already agree. A tie is neither: nothing shows which side holds the
        later edit, so writing would be a guess with data loss as its downside.
        """
        root, repo_copy, desk = self._pair(
            tmp_path, "canonical\n", "different\n", repo_time=OLD, desk_time=OLD,
        )
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is False
        assert desk.read_text() == "different\n"
        assert repo_copy.read_text() == "canonical\n"
        captured = capsys.readouterr()
        assert "REFUSED-SAME-MTIME" in captured.out
        assert "SAME MODIFICATION TIME" in captured.err
        assert "same modification time" in check.observed

    def test_a_same_mtime_tie_can_still_be_overridden(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        root, _repo_copy, desk = self._pair(
            tmp_path, "canonical\n", "different\n", repo_time=OLD, desk_time=OLD,
        )
        check = sv._reconcile_tracker(root, desktop=desk, allow_overwrite=True)
        assert check.passed is True
        assert desk.read_text() == "canonical\n"
        assert len(list(desk.parent.glob("*.superseded-*"))) == 1
        assert "OVERWROTE-DESKTOP" in capsys.readouterr().out

    def test_the_explicit_flag_overwrites_and_keeps_the_discarded_content(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        root, _repo_copy, desk = self._pair(
            tmp_path, "canonical\n", "hand edit\n", repo_time=OLD, desk_time=NEW,
        )
        check = sv._reconcile_tracker(root, desktop=desk, allow_overwrite=True)
        assert check.passed is True
        assert desk.read_text() == "canonical\n"
        backups = list(desk.parent.glob("*.superseded-*"))
        assert len(backups) == 1, "an override must remain reversible"
        assert backups[0].read_text() == "hand edit\n"
        out = capsys.readouterr().out
        assert "OVERWROTE-DESKTOP" in out
        assert "newer Desktop copy" in out

    def test_a_missing_desktop_mirror_is_created_from_the_repo(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        root, repo_copy, desk = self._pair(tmp_path, "canonical\n", "x\n")
        desk.unlink()
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is True
        assert desk.read_text() == repo_copy.read_text()
        assert "MIRROR-CREATED" in capsys.readouterr().out

    def test_a_missing_repo_copy_fails_and_does_not_promote_the_desktop_copy(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        """Inverting the sync would stage unreviewed content into the repo."""
        root, repo_copy, desk = self._pair(tmp_path, "canonical\n", "desktop\n")
        repo_copy.unlink()
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is False
        assert not repo_copy.exists(), "sv must not write the repo copy for you"
        assert desk.read_text() == "desktop\n"
        assert "CANONICAL-MISSING" in capsys.readouterr().out

    def test_identical_copies_pass_and_nothing_is_rewritten(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        root, repo_copy, desk = self._pair(tmp_path, "same\n", "same\n")
        before = (desk.stat().st_mtime, repo_copy.stat().st_mtime)
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is True
        assert (desk.stat().st_mtime, repo_copy.stat().st_mtime) == before
        assert "IN-SYNC" in capsys.readouterr().out

    def test_neither_copy_present_is_not_a_cdsfl_tree(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        root, repo_copy, desk = self._pair(tmp_path, "a\n", "a\n")
        repo_copy.unlink()
        desk.unlink()
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is True
        assert "NEITHER-PRESENT" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "repo_text,desk_text,repo_time,desk_time,allow",
        [
            ("canonical\n", "stale\n", NEW, OLD, False),   # would refresh
            ("canonical\n", "edited\n", OLD, NEW, False),  # would refuse
            ("canonical\n", "edited\n", OLD, NEW, True),   # would overwrite
            ("canonical\n", "edited\n", OLD, OLD, False),  # tie: would refuse
            ("canonical\n", "edited\n", OLD, OLD, True),   # tie: would overwrite
        ],
    )
    def test_check_only_mode_never_writes(
        self, tmp_path: Path, repo_text: str, desk_text: str,
        repo_time: float, desk_time: float, allow: bool,
    ) -> None:
        root, _repo_copy, desk = self._pair(
            tmp_path, repo_text, desk_text, repo_time=repo_time, desk_time=desk_time,
        )
        before = _snapshot(tmp_path)
        sv._reconcile_tracker(root, desktop=desk, apply=False, allow_overwrite=allow)
        assert _snapshot(tmp_path) == before

    def test_every_outcome_names_its_case(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        """'Say which case fired, every time.'"""
        root, repo_copy, desk = self._pair(
            tmp_path, "canonical\n", "stale\n", repo_time=NEW, desk_time=OLD,
        )
        sv._reconcile_tracker(root, desktop=desk, apply=False)
        assert "Tracker: MIRROR-STALE [check only" in capsys.readouterr().out
        desk.unlink()
        sv._reconcile_tracker(root, desktop=desk, apply=False)
        assert "Tracker: MIRROR-MISSING" in capsys.readouterr().out
        repo_copy.unlink()
        sv._reconcile_tracker(root, desktop=desk, apply=False)
        assert "Tracker: NEITHER-PRESENT" in capsys.readouterr().out


# ─────────────────────────────────────────────────────────────────────────────
# RULING 7 — the persistent-memory index is audited, never edited
# ─────────────────────────────────────────────────────────────────────────────

def _index(mem: Path, body: str) -> Path:
    path = mem / "MEMORY.md"
    path.write_text(body, encoding="utf-8")
    return path


def _entries(n: int, pad: int = 40) -> str:
    return "".join(
        f"- [Entry {i}](file_{i}.md) — {'x' * pad}\n" for i in range(n)
    )


class TestMemoryIndexAudit:
    def test_size_check_refuses_inside_the_five_percent_band(
        self, memory_dir: Path,
    ) -> None:
        threshold = int(sv._MEMORY_INDEX_LIMIT_CHARS * sv._MEMORY_INDEX_REFUSE_FRACTION)
        _index(memory_dir, "x" * threshold)
        check = sv._check_memory_index_size(sv._audit_memory_index(memory_dir))
        assert check.passed is False
        assert str(threshold) in check.expected
        # WAS: assert "silently" in check.why and "NEWEST" in check.why
        # Both claims were falsified on 2026-09-01 and the rationale was
        # rewritten. The loader announces truncation, and the tail it cuts is
        # this index's OLDEST material (the March 2026 handoffs), not the
        # newest. What must stay asserted is that the reason names both loader
        # limits, since guarding only one of them was the actual defect.
        assert str(sv._MEMORY_INDEX_LIMIT_CHARS) in check.why
        assert str(sv._MEMORY_INDEX_LIMIT_LINES) in check.why

    def test_size_check_passes_one_character_below_the_band(
        self, memory_dir: Path,
    ) -> None:
        threshold = int(sv._MEMORY_INDEX_LIMIT_CHARS * sv._MEMORY_INDEX_REFUSE_FRACTION)
        _index(memory_dir, "x" * (threshold - 1))
        check = sv._check_memory_index_size(sv._audit_memory_index(memory_dir))
        assert check.passed is True

    def test_size_is_measured_in_characters_not_bytes(
        self, memory_dir: Path,
    ) -> None:
        """The index is full of stars, gammas and em-dashes. Measuring bytes
        would refuse a file that is comfortably inside the loader limit."""
        text = "★" * 20_000  # 20k characters, 60k bytes
        _index(memory_dir, text)
        audit = sv._audit_memory_index(memory_dir)
        assert audit.chars == 20_000
        assert audit.byte_len == 60_000
        assert sv._check_memory_index_size(audit).passed is True

    def test_headroom_is_reported_in_characters_and_in_entries(
        self, memory_dir: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        _index(memory_dir, _entries(10))
        for i in range(10):
            (memory_dir / f"file_{i}.md").write_text("body\n")
        audit = sv._audit_memory_index(memory_dir)
        assert audit.headroom == sv._MEMORY_INDEX_LIMIT_CHARS - audit.chars
        assert audit.median_entry > 0
        assert audit.entries_left == audit.headroom // (audit.median_entry + 1)
        sv._print_memory_index_report(audit)
        out = capsys.readouterr().out
        assert f"Headroom: {audit.headroom} characters" in out
        assert f"~{audit.entries_left} more entries" in out
        assert f"median entry size of {audit.median_entry} chars" in out

    def test_a_broken_link_is_reported(
        self, memory_dir: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        _index(memory_dir, "- [Gone](vanished.md) — was deleted\n")
        audit = sv._audit_memory_index(memory_dir)
        assert audit.broken == ["vanished.md"]
        sv._print_memory_index_report(audit)
        assert "BROKEN LINK: vanished.md" in capsys.readouterr().out

    def test_orphans_are_reported_and_split_by_whether_they_are_mentioned(
        self, memory_dir: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        """An orphan is a memory that exists but will never be recalled. One
        whose name appears in the prose is a weaker fault than one that appears
        nowhere, so they are not lumped together."""
        _index(memory_dir, "- [Kept](kept.md) — linked\n\nSee also mentioned.md\n")
        for name in ("kept.md", "mentioned.md", "invisible.md"):
            (memory_dir / name).write_text("body\n")
        audit = sv._audit_memory_index(memory_dir)
        assert audit.orphans_unmentioned == ["invisible.md"]
        assert audit.orphans_mentioned == ["mentioned.md"]
        sv._print_memory_index_report(audit)
        out = capsys.readouterr().out
        assert "invisible.md — name appears nowhere" in out
        assert "mentioned.md — name appears in the index text, but not as an entry" in out

    def test_no_orphans_is_stated_positively(
        self, memory_dir: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        _index(memory_dir, "- [Kept](kept.md) — linked\n")
        (memory_dir / "kept.md").write_text("body\n")
        sv._print_memory_index_report(sv._audit_memory_index(memory_dir))
        assert "Orphans: none" in capsys.readouterr().out

    def test_over_long_entries_are_counted_and_the_cap_is_disclosed(
        self, memory_dir: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        _index(memory_dir, _entries(8, pad=400) + _entries(2, pad=5))
        audit = sv._audit_memory_index(memory_dir)
        assert len(audit.over_long) == 8
        sv._print_memory_index_report(audit)
        out = capsys.readouterr().out
        assert f"8 of {len(audit.entries)} entries exceed 150 chars" in out
        assert "and 3 more, not shown (capped at 5)" in out

    def test_entry_lengths_are_per_line_not_swallowed_across_newlines(
        self, memory_dir: Path,
    ) -> None:
        """A multiline regex lets ``\\s`` eat newlines and mis-measure entries."""
        line = "- [A](a.md) — short"
        _index(memory_dir, f"\n\n{line}\n\n\n{line}\n")
        audit = sv._audit_memory_index(memory_dir)
        assert [n for _t, _g, n in audit.entries] == [len(line), len(line)]
        assert len(line) == 19, "guards the guard: a blank-line-swallowing "\
                                "regex would report far more than the line length"

    def test_an_unreadable_index_fails_rather_than_passing_silently(
        self, memory_dir: Path,
    ) -> None:
        (memory_dir / "MEMORY.md").write_bytes(b"\xff\xfe not utf-8")
        audit = sv._audit_memory_index(memory_dir)
        assert audit.error
        check = sv._check_memory_index_size(audit)
        assert check.passed is False
        assert "could not be measured" in check.observed

    def test_a_missing_index_fails(self, memory_dir: Path) -> None:
        check = sv._check_memory_index_size(sv._audit_memory_index(memory_dir))
        assert check.passed is False
        assert "does not exist" in check.observed

    def test_the_audit_writes_nothing_under_the_memory_folder(
        self, memory_dir: Path,
    ) -> None:
        """The persistent-memory folder is the live store: read only."""
        _index(memory_dir, _entries(5))
        (memory_dir / "orphan.md").write_text("body\n")
        before = _snapshot(memory_dir)
        audit = sv._audit_memory_index(memory_dir)
        sv._print_memory_index_report(audit)
        sv._check_memory_index_size(audit)
        assert _snapshot(memory_dir) == before


# ─────────────────────────────────────────────────────────────────────────────
# RULING 4 — the alert itself
# ─────────────────────────────────────────────────────────────────────────────

def _failed_check() -> sv._Check:
    return sv._Check(
        name="memory-updated",
        passed=False,
        why="the session's memory would be lost",
        expected="a memory file newer than the last sv commit",
        observed="nothing has changed since 9c88fa1",
        look_at="/some/path/memory",
    )


class TestAlert:
    def test_the_alert_names_check_expected_observed_look_at_and_override(
        self, capsys: pytest.CaptureFixture,
    ) -> None:
        """'Something is missing' gives nobody anything to fix."""
        sv._print_save_alert([_failed_check()], total=4, refusing=True)
        err = capsys.readouterr().err
        assert "[FAIL] memory-updated" in err
        assert "WHY IT FIRED:" in err
        assert "EXPECTED:" in err
        assert "OBSERVED:" in err
        assert "LOOK AT:" in err
        assert "OVERRIDE:" in err
        assert "--allow-incomplete-save" in err
        assert "the session's memory would be lost" in err
        assert "nothing has changed since 9c88fa1" in err

    def test_the_alert_is_unmissable_and_on_stderr(
        self, capsys: pytest.CaptureFixture,
    ) -> None:
        sv._print_save_alert([_failed_check()], total=4, refusing=True)
        captured = capsys.readouterr()
        assert "######" in captured.err
        assert captured.out == ""

    def test_refusing_says_nothing_was_committed(
        self, capsys: pytest.CaptureFixture,
    ) -> None:
        sv._print_save_alert([_failed_check()], total=4, refusing=True)
        err = capsys.readouterr().err
        assert "sv REFUSED TO SAVE — 1 of 4 completeness checks FAILED" in err
        assert "NOTHING WAS COMMITTED" in err

    def test_an_override_run_says_so_instead_of_claiming_a_refusal(
        self, capsys: pytest.CaptureFixture,
    ) -> None:
        sv._print_save_alert([_failed_check()], total=4, refusing=False)
        err = capsys.readouterr().err
        assert "INCOMPLETE SAVE ALLOWED" in err
        assert "REFUSED" not in err

    def test_a_rehearsal_reports_rather_than_announcing_a_refusal(
        self, capsys: pytest.CaptureFixture,
    ) -> None:
        """--check-save neither refuses nor allows anything. Claiming either
        would report an event that did not happen."""
        sv._print_save_alert([_failed_check()], total=4, refusing=True, checking=True)
        err = capsys.readouterr().err
        assert "--check-save: THE SAVE IS INCOMPLETE — 1 of 4 checks FAILED" in err
        assert "REFUSED" not in err
        assert "ALLOWED" not in err
        assert "Nothing was written and nothing was committed." in err

    def test_a_refusal_that_did_rewrite_a_file_says_so_and_names_it(
        self, capsys: pytest.CaptureFixture,
    ) -> None:
        """ADVERSARIAL VERIFICATION, 2026-08-06.

        The tracker reconciliation of ruling 3 runs INSIDE the pre-flight and
        legitimately rewrites the Desktop mirror. A later check can then fail,
        at which point the alert used to print "NO DOCUMENT WAS REWRITTEN"
        unconditionally — asserting a property it had never checked, over a
        file it had just written. Reproduced end to end: repo tracker newer
        than the Desktop copy plus a stale memory folder rewrote
        CDSFL_Agent_Operational_Plan.md on the Desktop and then said nothing
        had been rewritten.
        """
        sv._print_save_alert(
            [_failed_check()], total=4, refusing=True,
            wrote=["/some/Desktop/CDSFL_Agent_Operational_Plan.md"],
        )
        err = capsys.readouterr().err
        assert "NO DOCUMENT WAS REWRITTEN" not in err
        assert "NOTHING WAS COMMITTED" in err
        assert "DID write 1 file(s) before refusing" in err
        assert "/some/Desktop/CDSFL_Agent_Operational_Plan.md" in err

    def test_a_refusal_that_wrote_nothing_still_says_nothing_was_rewritten(
        self, capsys: pytest.CaptureFixture,
    ) -> None:
        """The claim is now conditional on the measurement, not on the mood."""
        sv._print_save_alert([_failed_check()], total=4, refusing=True, wrote=[])
        err = capsys.readouterr().err
        assert "NOTHING WAS COMMITTED AND NO DOCUMENT WAS REWRITTEN." in err

    def test_the_reconciler_records_the_file_it_wrote(self, tmp_path: Path) -> None:
        """The alert can only report a write if the check reports it upward."""
        root = tmp_path / "repo"
        repo_copy = root / sv._TRACKER_MIRROR_REL
        repo_copy.parent.mkdir(parents=True, exist_ok=True)
        repo_copy.write_text("canonical\n")
        _set_mtime(repo_copy, NEW)
        desk = tmp_path / "Desktop" / "CDSFL_Agent_Operational_Plan.md"
        desk.parent.mkdir(parents=True, exist_ok=True)
        desk.write_text("stale\n")
        _set_mtime(desk, OLD)

        assert sv._reconcile_tracker(root, desktop=desk, apply=True).wrote == str(desk)
        # A check-only pass writes nothing, so it must claim nothing.
        desk.write_text("stale\n")
        _set_mtime(desk, OLD)
        assert sv._reconcile_tracker(root, desktop=desk, apply=False).wrote == ""

    def test_a_pre_flight_that_refreshed_the_mirror_reports_it_in_the_alert(
        self, tmp_path: Path, git_repo: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """The whole path, assembled: mirror refreshed, memory stale, refuse."""
        mem = tmp_path / "memory"
        mem.mkdir()
        _index(mem, _entries(2))
        for i in range(2):
            (mem / f"file_{i}.md").write_text("body\n")
        _commit(git_repo, "sv: previous state save")
        for path in mem.rglob("*.md"):
            _set_mtime(path, OLD)  # nothing saved this session -> refusal

        tracker = git_repo / sv._TRACKER_MIRROR_REL
        tracker.parent.mkdir(parents=True, exist_ok=True)
        tracker.write_text("canonical\n")
        _set_mtime(tracker, NEW)
        desk = tmp_path / "Desktop" / "CDSFL_Agent_Operational_Plan.md"
        desk.parent.mkdir(parents=True, exist_ok=True)
        desk.write_text("stale\n")
        _set_mtime(desk, OLD)

        ob = tmp_path / "OpenBrain"
        monkeypatch.setattr(sv, "_OPEN_BRAIN_ROOT", ob)
        runner = _FakeRunner(
            _Result(0, f"{ob / 'open_brain'}\n"),
            _Result(0, "Database connection: OK\n"),
        )
        assert sv._preflight_completeness(
            git_repo, mem_dir=mem, desktop=desk, runner=runner,
        ) is False
        err = capsys.readouterr().err
        assert desk.read_text() == "canonical\n", "the mirror really was rewritten"
        assert "NO DOCUMENT WAS REWRITTEN" not in err, \
            "the alert claimed nothing was rewritten over a file it had just written"
        assert str(desk) in err

    def test_the_alert_says_a_false_alarm_is_a_defect_in_the_check(
        self, capsys: pytest.CaptureFixture,
    ) -> None:
        """The founder's second sentence: an alert is an opportunity to find
        out why, not a nuisance to be flagged past."""
        sv._print_save_alert([_failed_check()], total=4, refusing=True)
        err = capsys.readouterr().err
        assert "the CHECK is the defect" in err
        assert "scripts/cdsfl_sv.py" in err


# ─────────────────────────────────────────────────────────────────────────────
# RULING 4 — the pre-flight, assembled
# ─────────────────────────────────────────────────────────────────────────────

class TestPreflightAssembly:
    def _complete_world(self, tmp_path: Path, git_repo: Path) -> dict:
        mem = tmp_path / "memory"
        mem.mkdir()
        _index(mem, _entries(4))
        for i in range(4):
            (mem / f"file_{i}.md").write_text("body\n")
        _commit(git_repo, "sv: previous state save")
        _set_mtime(mem / "MEMORY.md", os.path.getmtime(git_repo / "f.txt") + 60)
        tracker = git_repo / sv._TRACKER_MIRROR_REL
        tracker.parent.mkdir(parents=True, exist_ok=True)
        tracker.write_text("tracker\n")
        desk = tmp_path / "Desktop" / "CDSFL_Agent_Operational_Plan.md"
        desk.parent.mkdir(parents=True, exist_ok=True)
        desk.write_text("tracker\n")
        ob = tmp_path / "OpenBrain"
        return {
            "mem_dir": mem,
            "desktop": desk,
            "runner": _FakeRunner(
                _Result(0, f"{ob / 'open_brain'}\n"),
                _Result(0, "Database connection: OK\n"),
            ),
        }

    def test_a_complete_save_passes_all_four_checks(
        self, tmp_path: Path, git_repo: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        world = self._complete_world(tmp_path, git_repo)
        monkeypatch.setattr(sv, "_OPEN_BRAIN_ROOT", tmp_path / "OpenBrain")
        assert sv._preflight_completeness(git_repo, **world) is True
        out = capsys.readouterr().out
        assert "All 4 completeness checks passed." in out
        for name in ("memory-updated", "open-brain-reachable",
                     "tracker-copies-agree", "memory-index-headroom"):
            assert f"[PASS] {name}" in out

    def test_one_failure_fails_the_pre_flight_and_raises_the_alert(
        self, tmp_path: Path, git_repo: Path, monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        world = self._complete_world(tmp_path, git_repo)
        monkeypatch.setattr(sv, "_OPEN_BRAIN_ROOT", tmp_path / "OpenBrain")
        for path in world["mem_dir"].rglob("*.md"):  # nothing saved this session
            _set_mtime(path, OLD)
        assert sv._preflight_completeness(git_repo, **world) is False
        captured = capsys.readouterr()
        assert "[FAIL] memory-updated" in captured.out
        assert "sv REFUSED TO SAVE" in captured.err

    def test_check_only_mode_touches_nothing(
        self, tmp_path: Path, git_repo: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        world = self._complete_world(tmp_path, git_repo)
        monkeypatch.setattr(sv, "_OPEN_BRAIN_ROOT", tmp_path / "OpenBrain")
        world["desktop"].write_text("diverged on the desktop\n")
        _set_mtime(world["desktop"], OLD)  # repo copy is newer, so a real run would sync
        before = _snapshot(tmp_path)
        sv._preflight_completeness(git_repo, apply=False, **world)
        assert _snapshot(tmp_path) == before


# ─────────────────────────────────────────────────────────────────────────────
# RULING 4 — main() wiring: when the pre-flight runs, and what a failure costs
# ─────────────────────────────────────────────────────────────────────────────

GS = {
    "branch": "exp39-experimental",
    "clean": True,
    "uncommitted": [],
    "last_hash": "49d2473",
    "last_message": "seed",
    "last_date": "2026-08-05 20:28:54 +0100",
    "recent_log": ["49d2473 seed"],
    "remote_sync": "up to date with origin/exp39-experimental",
}


def _run_main(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, argv: list[str],
) -> None:
    monkeypatch.setattr(sv, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(sv, "git_state", lambda: GS)
    monkeypatch.setattr(sv, "test_count", lambda: 2776)
    monkeypatch.setattr(sv, "latest_experiment", lambda: None)
    # **kwargs deliberately: this stub stands in for a real function, and a
    # stub that pins the caller's exact keyword list turns every future
    # signature change into a false failure. update_timestamp gained
    # body_regenerated on 2026-08-07 and broke 13 tests that had nothing
    # to do with timestamps.
    monkeypatch.setattr(sv, "update_timestamp", lambda p, **kw: False)
    monkeypatch.setattr(sv, "update_onboarding_experiment", lambda *a, **k: False)
    monkeypatch.setattr(sv, "update_recovery_pending", lambda *a, **k: False)
    monkeypatch.setattr(sys, "argv", ["cdsfl_sv.py", *argv])
    sv.main()


class TestMainWiring:
    def test_a_failed_pre_flight_refuses_the_commit_and_writes_nothing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(sv, "_preflight_completeness", lambda root, **k: False)
        monkeypatch.setattr(
            sv, "_commit_and_push",
            lambda **k: pytest.fail("sv committed an incomplete save"),
        )
        with pytest.raises(SystemExit) as exc:
            _run_main(monkeypatch, tmp_path, ["--commit"])
        assert exc.value.code == 1
        assert not (tmp_path / "docs" / "CURRENT_STATE.md").exists(), \
            "a refusal must leave the tree exactly as it found it"

    def test_a_passing_pre_flight_lets_the_commit_proceed(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        called: list[str] = []
        monkeypatch.setattr(sv, "_preflight_completeness", lambda root, **k: True)
        monkeypatch.setattr(
            sv, "_commit_and_push",
            lambda **k: called.append("commit") or False,
        )
        _run_main(monkeypatch, tmp_path, ["--commit"])
        assert called == ["commit"]
        assert (tmp_path / "docs" / "CURRENT_STATE.md").exists()

    def test_the_override_flag_proceeds_despite_a_failed_pre_flight(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        called: list[str] = []
        seen: dict = {}

        def fake_preflight(root, **kwargs):
            seen.update(kwargs)
            return False

        monkeypatch.setattr(sv, "_preflight_completeness", fake_preflight)
        monkeypatch.setattr(
            sv, "_commit_and_push", lambda **k: called.append("commit") or False,
        )
        _run_main(monkeypatch, tmp_path, ["--commit", "--allow-incomplete-save"])
        assert called == ["commit"]
        assert seen["allow_incomplete"] is True, \
            "the pre-flight must know it is being overridden, so it can say so"

    def test_the_desktop_overwrite_flag_is_passed_through_separately(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        """The destructive flag must never be implied by the proceed flag."""
        seen: dict = {}

        def fake_preflight(root, **kwargs):
            seen.update(kwargs)
            return True

        monkeypatch.setattr(sv, "_preflight_completeness", fake_preflight)
        monkeypatch.setattr(sv, "_commit_and_push", lambda **k: False)
        _run_main(monkeypatch, tmp_path, ["--commit", "--allow-incomplete-save"])
        assert seen["allow_overwrite_desktop"] is False

    def test_a_dry_run_never_runs_the_pre_flight(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        """A dry run cannot produce the incomplete commit the checks prevent,
        and must not touch the Desktop or the live memory folder to find out."""
        monkeypatch.setattr(
            sv, "_preflight_completeness",
            lambda root, **k: pytest.fail("pre-flight ran under --dry-run"),
        )
        _run_main(monkeypatch, tmp_path, ["--commit", "--push", "--dry-run"])

    def test_a_plain_run_without_commit_never_runs_the_pre_flight(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(
            sv, "_preflight_completeness",
            lambda root, **k: pytest.fail("pre-flight ran without --commit"),
        )
        _run_main(monkeypatch, tmp_path, [])

    def test_check_save_reports_and_exits_without_writing_or_committing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        seen: dict = {}

        def fake_preflight(root, **kwargs):
            seen.update(kwargs)
            return True

        monkeypatch.setattr(sv, "_preflight_completeness", fake_preflight)
        monkeypatch.setattr(
            sv, "_commit_and_push",
            lambda **k: pytest.fail("--check-save must not commit"),
        )
        with pytest.raises(SystemExit) as exc:
            _run_main(monkeypatch, tmp_path, ["--check-save"])
        assert exc.value.code == 0
        assert seen["apply"] is False, "--check-save must be read-only"
        assert seen["checking"] is True
        assert not (tmp_path / "docs" / "CURRENT_STATE.md").exists()

    def test_check_save_exits_nonzero_when_the_save_is_incomplete(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.setattr(sv, "_preflight_completeness", lambda root, **k: False)
        with pytest.raises(SystemExit) as exc:
            _run_main(monkeypatch, tmp_path, ["--check-save"])
        assert exc.value.code == 1

    def test_the_override_flag_does_not_make_an_incomplete_rehearsal_exit_zero(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        """--check-save reports the measurement. An override changes what a
        commit would do, not whether the save is in fact complete."""
        monkeypatch.setattr(sv, "_preflight_completeness", lambda root, **k: False)
        with pytest.raises(SystemExit) as exc:
            _run_main(
                monkeypatch, tmp_path, ["--check-save", "--allow-incomplete-save"],
            )
        assert exc.value.code == 1


# ─────────────────────────────────────────────────────────────────────────────
# The MIRROR-REFRESHED data-loss path. Found by the 2026-08-06 gate, fixed the
# same night. Ruling 3 inverted the tracker so the repo copy wins, and that
# introduced a WRITE where none existed before. The overwrite-under-override
# branch took a `.superseded-` backup; the ordinary refresh branch did not — and
# its only guard is mtime ordering, which `git checkout`, `git pull`, `git stash`
# or any agent editing the repo tracker defeats. A hand edit to the Desktop copy
# could therefore be destroyed while the run reported success.
# ─────────────────────────────────────────────────────────────────────────────


class TestTheMirrorRefreshNeverDiscardsWithoutABackup:
    """Every branch that OVERWRITES the Desktop copy must leave it recoverable."""

    def test_repo_newer_refresh_keeps_the_discarded_desktop_content(
        self, tmp_path: Path,
    ) -> None:
        root, repo_copy, desk = TestTrackerReconciliation()._pair(
            tmp_path, "canonical\n", "HAND EDIT NEVER CARRIED ACROSS\n",
            repo_time=NEW, desk_time=OLD,
        )
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is True, "the ruling-3 direction must still refresh"
        assert desk.read_text() == repo_copy.read_text()
        backups = list(desk.parent.glob(desk.name + ".superseded-*"))
        assert len(backups) == 1, (
            "the refresh overwrote the Desktop copy and kept NO backup. mtime "
            "ordering does not mean the Desktop copy held nothing worth keeping: "
            "git checkout/pull/stash, or any agent editing the repo tracker, "
            "makes the repo copy newer without the Desktop edit being carried."
        )
        assert "HAND EDIT NEVER CARRIED ACROSS" in backups[0].read_text()

    def test_a_refusal_writes_nothing_and_leaves_no_backup(
        self, tmp_path: Path,
    ) -> None:
        root, _repo_copy, desk = TestTrackerReconciliation()._pair(
            tmp_path, "canonical\n", "hand edit\n", repo_time=OLD, desk_time=NEW,
        )
        check = sv._reconcile_tracker(root, desktop=desk)
        assert check.passed is False
        assert desk.read_text() == "hand edit\n"
        assert not list(desk.parent.glob(desk.name + ".superseded-*")), (
            "a refusal writes nothing at all, so it must not leave a backup either"
        )

    def test_check_only_mode_writes_neither_mirror_nor_backup(
        self, tmp_path: Path,
    ) -> None:
        root, _repo_copy, desk = TestTrackerReconciliation()._pair(
            tmp_path, "canonical\n", "desktop\n", repo_time=NEW, desk_time=OLD,
        )
        sv._reconcile_tracker(root, desktop=desk, apply=False)
        assert desk.read_text() == "desktop\n"
        assert not list(desk.parent.glob(desk.name + ".superseded-*"))
