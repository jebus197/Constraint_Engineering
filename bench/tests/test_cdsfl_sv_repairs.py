"""Regression tests for the 2026-08-05 repairs to ``scripts/cdsfl_sv.py``.

Repairs pinned here (S1–S5), all of the same family: sv was reporting
successes it had not verified.

  S1  the ``Co-Authored-By`` trailer was the literal string "Claude Opus 4.8",
      which had rotted — the session was Opus 5 — so every sv commit carried a
      false model attribution.
  S2  docs/CURRENT_STATE.md is generated BEFORE the sv commit and can never
      describe it, yet labelled the parent as "Last commit" and the
      about-to-be-committed files as merely "DIRTY".
  S3  the sv spec names an Open Brain session summary FIRST; the script had no
      Open Brain code at all, so the store silently fell behind.
  S4  the closing summary always claimed ONBOARDING.md and RECOVERY.md were
      "auto-generated", including right after preserving manual content and
      including under --dry-run where nothing is written.
  S5  the Desktop/repo operational-tracker mirror parity was policy only, with
      no code behind it.

Everything here is offline: no git network, no pytest-in-pytest, no real Open
Brain capture. The subprocess call is stubbed in every S3 test.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import cdsfl_sv as sv  # noqa: E402

SV_SOURCE = (REPO_ROOT / "scripts" / "cdsfl_sv.py").read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Shared fixtures / helpers
# ─────────────────────────────────────────────────────────────────────────────

GS = {
    "branch": "exp39-experimental",
    "clean": False,
    "uncommitted": [
        "M  docs/CURRENT_STATE.md",
        "M  resources/ONBOARDING.md",
        "?? experimental_notes/Note_2026-08-05.md",
    ],
    "last_hash": "624b39a",
    "last_message": "sv: PROVENANCE CORRECTION",
    "last_date": "2026-08-05 14:20:11 +0100",
    "recent_log": ["624b39a sv: PROVENANCE CORRECTION"],
    "remote_sync": "up to date with origin/exp39-experimental",
}

EXP = {
    "name": "exp49_engineering_exam_live",
    "number": 49,
    "status": "STATE_CONVERGED",
    "topology": "full-mesh",
    "target": "bench/reference_runner_v3.py",
    "total_rounds": 7,
    "total_findings": 61,
    "gamma": 0.5123,
    "models": ["cc2", "cx", "ge"],
    "per_model": {"cc2": 25, "cx": 20, "ge": 16},
    "log_dir": "",
    "canonical_count": 44,
}


@pytest.fixture
def clean_model_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove every environment variable the trailer derivation reads."""
    for var in ("CDSFL_SV_CO_AUTHOR", "ANTHROPIC_MODEL", "CLAUDECODE"):
        monkeypatch.delenv(var, raising=False)


class _StubRunner:
    """Stand-in for ``subprocess.run``. Records the call; never spawns."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "",
                 raises: BaseException | None = None) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.raises = raises
        self.calls: list[tuple[tuple, dict]] = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.raises is not None:
            raise self.raises
        return subprocess.CompletedProcess(
            args=args[0], returncode=self.returncode,
            stdout=self.stdout, stderr=self.stderr,
        )


# ─────────────────────────────────────────────────────────────────────────────
# S1 — co-author trailer must not assert a model version it cannot verify
# ─────────────────────────────────────────────────────────────────────────────

class TestS1CoAuthorTrailer:
    def test_no_hardcoded_model_version_anywhere_in_source(self) -> None:
        """The defect itself: a literal model version in the source."""
        assert "Opus 4.8" not in SV_SOURCE.replace(
            'the literal string "Claude Opus 4.8"', ""
        ), "a hardcoded model version is back in cdsfl_sv.py"
        # No `Co-Authored-By: <something>` f-string with a baked-in name.
        assert "Co-Authored-By: Claude Opus" not in SV_SOURCE

    def test_explicit_operator_override_wins(
        self, clean_model_env: None, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("CDSFL_SV_CO_AUTHOR", "Claude Opus 5")
        monkeypatch.setenv("ANTHROPIC_MODEL", "claude-something-else")
        assert sv._co_author_trailer() == (
            "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
        )

    def test_uses_anthropic_model_verbatim(
        self, clean_model_env: None, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("ANTHROPIC_MODEL", "claude-opus-5")
        trailer = sv._co_author_trailer()
        assert "claude-opus-5" in trailer
        assert trailer.startswith("Co-Authored-By: ")

    def test_asserts_no_version_when_environment_exposes_none(
        self, clean_model_env: None, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The live case: Claude Code sets CLAUDECODE=1 but no model id.

        The trailer must say what it knows — Claude Code — and claim no
        version. This is the anti-rot property: there is no digit to go stale.
        """
        monkeypatch.setenv("CLAUDECODE", "1")
        trailer = sv._co_author_trailer()
        assert trailer == "Co-Authored-By: Claude Code <noreply@anthropic.com>"
        assert not any(ch.isdigit() for ch in trailer)

    def test_no_trailer_at_all_outside_a_claude_session(
        self, clean_model_env: None,
    ) -> None:
        """A human running sv by hand must not be given an AI co-author."""
        assert sv._co_author_trailer() is None


class TestS1TrailerAtTheCommitSite:
    """The helper is only half the fix — pin what actually reaches a commit.

    These commit into a throwaway tmp_path repo, never the project repo.
    """

    def _stage_one_file(self, repo: Path) -> None:
        (repo / "docs").mkdir(exist_ok=True)
        (repo / "docs" / "real.md").write_text("x\n")

    @pytest.fixture(autouse=True)
    def _no_tracker_io(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Keep these tests off the real Desktop; S5 is pinned separately."""
        monkeypatch.setattr(sv, "_check_tracker_mirror", lambda root, desktop=None: True)

    def test_commit_carries_the_derived_trailer(
        self, git_repo: Path, clean_model_env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("CDSFL_SV_CO_AUTHOR", "Claude Opus 5")
        monkeypatch.setattr(sv, "repo_root", lambda: git_repo)
        self._stage_one_file(git_repo)
        assert sv._commit_and_push(
            message="sv: docs/real.md", push=False, root=git_repo,
            auto_stage=True, validate_message=True,
        ) is True
        body = subprocess.run(
            ["git", "log", "-1", "--format=%B"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        ).stdout
        assert "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" in body
        assert "Opus 4.8" not in body

    def test_commit_omits_the_trailer_when_no_session_is_detectable(
        self, git_repo: Path, clean_model_env: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sv, "repo_root", lambda: git_repo)
        self._stage_one_file(git_repo)
        sv._commit_and_push(
            message="sv: docs/real.md", push=False, root=git_repo,
            auto_stage=True, validate_message=True,
        )
        body = subprocess.run(
            ["git", "log", "-1", "--format=%B"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        ).stdout
        assert "Co-Authored-By" not in body


# ─────────────────────────────────────────────────────────────────────────────
# S2 — CURRENT_STATE.md must not present a pre-commit snapshot as current truth
# ─────────────────────────────────────────────────────────────────────────────

def _git_section(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        if line.startswith("## Tests"):
            break
        out.append(line)
    return "\n".join(out)


class TestS2PreCommitSnapshotLabelling:
    def test_commit_run_states_the_snapshot_is_pre_commit(
        self, tmp_path: Path,
    ) -> None:
        block = _git_section(
            sv.generate_current_state(GS, 2602, None, tmp_path, will_commit=True)
        )
        assert "SNAPSHOT TAKEN IMMEDIATELY BEFORE THE sv COMMIT" in block
        assert "NOT CURRENT TRUTH" in block

    def test_commit_run_names_last_commit_as_the_parent(
        self, tmp_path: Path,
    ) -> None:
        block = _git_section(
            sv.generate_current_state(GS, 2602, None, tmp_path, will_commit=True)
        )
        assert "PARENT" in block
        # The bare, mistakable label must be gone on a committing run.
        assert "- **Last commit:**" not in block

    def test_commit_run_does_not_claim_the_list_is_the_commits_file_list(
        self, tmp_path: Path,
    ) -> None:
        """The first S2 repair over-corrected: it replaced the mislabelled
        'DIRTY' with the assertion that the listed files are 'precisely the
        ones that commit is about to contain'. That is false in both
        directions — sv rewrites CURRENT_STATE.md / ONBOARDING.md /
        RECOVERY.md *after* this snapshot (so the commit contains files the
        list omits) and stages only ``_SAFE_STAGING_DIRS`` (so the list can
        name files the commit omits). A confident false claim is worse than
        the vague one it replaced.
        """
        block = _git_section(
            sv.generate_current_state(GS, 2602, None, tmp_path, will_commit=True)
        )
        assert "about to contain" not in block
        assert "NOT that commit's file list" in block
        for rel in GS["uncommitted"]:
            assert rel in block

    def test_truncated_file_list_says_it_was_truncated(
        self, tmp_path: Path,
    ) -> None:
        """The list is capped at 15. With 19 uncommitted files — the real
        count on 2026-08-05 — four were dropped with no indication at all.
        """
        gs = dict(GS)
        gs["uncommitted"] = [f"M  file_{i:02d}.py" for i in range(19)]
        block = _git_section(
            sv.generate_current_state(gs, 2602, None, tmp_path, will_commit=True)
        )
        assert "M  file_14.py" in block
        assert "M  file_15.py" not in block, "still capped at 15 — that part is fine"
        assert "and 4 more, not shown" in block
        assert "capped at 15 of 19" in block

    def test_untruncated_list_carries_no_truncation_note(
        self, tmp_path: Path,
    ) -> None:
        block = _git_section(
            sv.generate_current_state(GS, 2602, None, tmp_path, will_commit=True)
        )
        assert "not shown" not in block

    def test_non_committing_run_is_an_unqualified_snapshot(
        self, tmp_path: Path,
    ) -> None:
        """No commit follows, so there is nothing to disclaim."""
        block = _git_section(
            sv.generate_current_state(GS, 2602, None, tmp_path, will_commit=False)
        )
        assert "SNAPSHOT TAKEN IMMEDIATELY BEFORE" not in block
        assert "- **Last commit:**" in block

    def test_default_is_non_committing(self, tmp_path: Path) -> None:
        assert (
            sv.generate_current_state(GS, 2602, None, tmp_path)
            == sv.generate_current_state(GS, 2602, None, tmp_path, will_commit=False)
        )


# ─────────────────────────────────────────────────────────────────────────────
# S3 — Open Brain capture: correct command, loud failure, never under --dry-run
# ─────────────────────────────────────────────────────────────────────────────

class TestS3OpenBrainCommand:
    def test_command_targets_the_canonical_cli_with_project_scope(self) -> None:
        cmd = sv._open_brain_command("summary text")
        assert cmd[0] == sys.executable
        assert cmd[1:4] == ["-m", "open_brain.cli", "capture"]
        assert cmd[-1] == "summary text"
        # --project is the whole point: rows without it are invisible to the
        # project filter.
        assert "--project" in cmd
        assert cmd[cmd.index("--project") + 1] == "CDSFL"
        assert cmd[cmd.index("--agent") + 1] == "cc"
        assert cmd[cmd.index("--type") + 1] == "session_summary"

    def test_capture_does_not_inject_an_environment(
        self, tmp_path: Path,
    ) -> None:
        """No PYTHONPATH, no env override — the child inherits the ambient
        environment so the editable install resolves normally."""
        runner = _StubRunner()
        sv._open_brain_capture("s", tmp_path, runner=runner)
        _args, kwargs = runner.calls[0]
        assert "env" not in kwargs

    def test_open_brain_resolves_to_the_canonical_install(self) -> None:
        """The stale fork at Project_Genesis/open_brain/ must not win.

        ``find_spec`` locates the module without executing it, so this stays
        offline.
        """
        import importlib.util

        spec = importlib.util.find_spec("open_brain")
        if spec is None or not spec.origin:
            pytest.skip("open_brain is not installed in this environment")
        origin = Path(spec.origin).resolve()
        assert "Project_Genesis" not in origin.parts
        assert origin.parent.name == "open_brain"


class TestS3CaptureBehaviour:
    def test_success_returns_true_and_reports(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        runner = _StubRunner(returncode=0, stdout="Stored: abc-123")
        assert sv._open_brain_capture("s", tmp_path, runner=runner) is True
        captured = capsys.readouterr()
        assert "Open Brain: session summary captured" in captured.out
        assert "FAILED" not in captured.err

    def test_passes_a_timeout(self, tmp_path: Path) -> None:
        runner = _StubRunner()
        sv._open_brain_capture("s", tmp_path, timeout=42, runner=runner)
        _args, kwargs = runner.calls[0]
        assert kwargs["timeout"] == 42
        assert kwargs["capture_output"] is True

    def test_nonzero_exit_is_loud_and_not_fatal(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        runner = _StubRunner(returncode=1, stderr="could not connect to database")
        assert sv._open_brain_capture("s", tmp_path, runner=runner) is False
        err = capsys.readouterr().err
        assert "OPEN BRAIN CAPTURE FAILED" in err
        assert "could not connect to database" in err
        assert "!!!!" in err, "the warning must be unmissable"

    def test_timeout_is_loud_and_not_fatal(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        runner = _StubRunner(
            raises=subprocess.TimeoutExpired(cmd="open_brain", timeout=180),
        )
        assert sv._open_brain_capture("s", tmp_path, runner=runner) is False
        err = capsys.readouterr().err
        assert "OPEN BRAIN CAPTURE FAILED" in err
        assert "TimeoutExpired" in err

    def test_missing_interpreter_is_loud_and_not_fatal(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        runner = _StubRunner(raises=FileNotFoundError(2, "No such file"))
        assert sv._open_brain_capture("s", tmp_path, runner=runner) is False
        assert "OPEN BRAIN CAPTURE FAILED" in capsys.readouterr().err

    def test_failure_warning_carries_a_runnable_recovery_command(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        runner = _StubRunner(returncode=2)
        sv._open_brain_capture("the summary", tmp_path, runner=runner)
        err = capsys.readouterr().err
        assert "--project CDSFL" in err
        assert "--type session_summary" in err

    def test_summary_names_the_commit_and_labels_the_test_count(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sv, "_git", lambda *a, **k: "deadbee sv: state save")
        text = sv._open_brain_summary(
            "sv: repairs", GS, 2602, EXP, tmp_path, pushed=True,
        )
        assert "deadbee" in text
        assert "NOT a pass count" in text
        assert "exp49_engineering_exam_live" in text
        assert "Pushed: yes" in text


# ─────────────────────────────────────────────────────────────────────────────
# main() harness — fully offline: git, pytest collection and the log scan are
# all replaced. Nothing is written outside tmp_path, and no commit is made.
# ─────────────────────────────────────────────────────────────────────────────

def _run_main(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    argv: list[str],
    *,
    exp: dict | None = EXP,
    onboarding_ret: bool = False,
    recovery_ret: bool = False,
) -> None:
    monkeypatch.setattr(sv, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(sv, "git_state", lambda: GS)
    monkeypatch.setattr(sv, "test_count", lambda: 2602)
    monkeypatch.setattr(sv, "latest_experiment", lambda: exp)
    monkeypatch.setattr(sv, "update_timestamp", lambda p, **kw: False)
    monkeypatch.setattr(
        sv, "update_onboarding_experiment", lambda *a, **k: onboarding_ret,
    )
    monkeypatch.setattr(
        sv, "update_recovery_pending", lambda *a, **k: recovery_ret,
    )
    monkeypatch.setattr(sys, "argv", ["cdsfl_sv.py", *argv])
    sv.main()


def _write_preserved(path: Path, start: str, end: str) -> None:
    """Write a doc whose marked section holds manual (non-placeholder) text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"Last updated: whenever\n\n{start}\n"
        + "Hand-written qualitative observations that sv must never clobber, "
        + "long enough to clear the fifty-character manual-content threshold.\n"
        + f"{end}\n",
        encoding="utf-8",
    )


# ─────────────────────────────────────────────────────────────────────────────
# S4 — the closing summary must report the update functions' actual results
# ─────────────────────────────────────────────────────────────────────────────

class TestS4ClosingSummaryHonesty:
    def test_preserved_manual_content_is_not_reported_as_regenerated(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """The defect: 'Preserved manual content' followed by
        'summary auto-generated' for the same file, in the same output."""
        _write_preserved(
            tmp_path / "resources" / "ONBOARDING.md",
            sv._ONBOARDING_MARKER_START, sv._ONBOARDING_MARKER_END,
        )
        _write_preserved(
            tmp_path / "resources" / "RECOVERY.md",
            sv._RECOVERY_MARKER_START, sv._RECOVERY_MARKER_END,
        )
        _run_main(monkeypatch, tmp_path, ["--dry-run"])
        out = capsys.readouterr().out

        assert "Preserved manual content" in out
        assert "auto-generated" not in out
        assert "ONBOARDING.md: manual content preserved, auto-block NOT regenerated" in out
        assert "RECOVERY.md: manual content preserved, auto-block NOT regenerated" in out

    def test_regenerated_is_reported_as_regenerated(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        _run_main(
            monkeypatch, tmp_path, ["--dry-run"],
            onboarding_ret=True, recovery_ret=True,
        )
        out = capsys.readouterr().out
        assert "ONBOARDING.md: regenerated" in out
        assert "RECOVERY.md: regenerated" in out

    def test_unchanged_is_reported_as_unchanged(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        _run_main(monkeypatch, tmp_path, ["--dry-run"])
        out = capsys.readouterr().out
        assert "ONBOARDING.md: unchanged" in out
        assert "RECOVERY.md: unchanged" in out

    def test_absent_experiment_is_not_reported_as_a_summary(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        _run_main(monkeypatch, tmp_path, ["--dry-run"], exp=None)
        out = capsys.readouterr().out
        assert "ONBOARDING.md: not attempted (no experiment data found)" in out

    def test_dry_run_is_banner_prefixed_and_claims_no_write(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        _run_main(monkeypatch, tmp_path, ["--dry-run"], onboarding_ret=True)
        out = capsys.readouterr().out
        assert "DRY RUN — NOTHING WAS WRITTEN TO DISK." in out
        assert "no files written" in out
        # The banner must precede the summary body it qualifies.
        assert out.index("DRY RUN — NOTHING WAS WRITTEN") < out.index("  Branch:")
        assert not (tmp_path / "docs" / "CURRENT_STATE.md").exists()

    def test_real_run_has_no_dry_run_banner(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        _run_main(monkeypatch, tmp_path, [])
        out = capsys.readouterr().out
        assert "DRY RUN" not in out
        assert "State save complete." in out
        assert (tmp_path / "docs" / "CURRENT_STATE.md").exists()


class TestS3NotUnderDryRun:
    def test_open_brain_capture_does_not_fire_under_dry_run(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        fired: list[str] = []
        monkeypatch.setattr(
            sv, "_open_brain_capture",
            lambda *a, **k: fired.append("capture") or True,
        )
        monkeypatch.setattr(
            sv, "_commit_and_push",
            lambda **k: pytest.fail("sv must not commit under --dry-run"),
        )
        _run_main(monkeypatch, tmp_path, ["--commit", "--push", "--dry-run"])
        assert fired == [], "Open Brain must not be written on a dry run"

    def test_open_brain_capture_does_not_fire_without_commit(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        fired: list[str] = []
        monkeypatch.setattr(
            sv, "_open_brain_capture",
            lambda *a, **k: fired.append("capture") or True,
        )
        _run_main(monkeypatch, tmp_path, [])
        assert fired == []


# ─────────────────────────────────────────────────────────────────────────────
# S5 — operational-tracker mirror parity: warn loudly, never copy
# ─────────────────────────────────────────────────────────────────────────────

class TestS5TrackerMirror:
    def test_paths_match_the_documented_policy(self) -> None:
        """A typo here would make the whole check a permanent no-op."""
        assert sv._TRACKER_DESKTOP == (
            Path.home() / "Desktop" / "CDSFL_Agent_Operational_Plan.md"
        )
        assert sv._TRACKER_MIRROR_REL == (
            "experimental_notes/CDSFL_Agent_Operational_Plan.md"
        )

    def _pair(self, tmp_path: Path, desk_text: str, mirror_text: str) -> tuple[Path, Path]:
        desk = tmp_path / "Desktop" / "CDSFL_Agent_Operational_Plan.md"
        desk.parent.mkdir(parents=True, exist_ok=True)
        desk.write_text(desk_text, encoding="utf-8")
        mirror = tmp_path / "repo" / sv._TRACKER_MIRROR_REL
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_text(mirror_text, encoding="utf-8")
        return desk, mirror

    def test_identical_files_pass_quietly(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        desk, _ = self._pair(tmp_path, "same\n", "same\n")
        assert sv._check_tracker_mirror(tmp_path / "repo", desktop=desk) is True
        captured = capsys.readouterr()
        assert "in sync" in captured.out
        assert captured.err == ""

    def test_divergence_warns_loudly_and_names_the_newer_side(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        desk, mirror = self._pair(
            tmp_path, "line one\nDESKTOP ONLY\n", "line one\n",
        )
        import os
        os.utime(mirror, (1_700_000_000, 1_700_000_000))  # mirror is older
        assert sv._check_tracker_mirror(tmp_path / "repo", desktop=desk) is False
        err = capsys.readouterr().err
        assert "OPERATIONAL TRACKER OUT OF SYNC" in err
        assert "NEWER BY MTIME: Desktop canonical" in err
        assert "DESKTOP ONLY" in err, "the warning must show HOW they differ"
        assert "!!!!" in err

    def test_divergence_names_the_mirror_when_the_mirror_is_newer(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        desk, _mirror = self._pair(tmp_path, "a\n", "a\nb\n")
        import os
        os.utime(desk, (1_700_000_000, 1_700_000_000))  # desktop is older
        assert sv._check_tracker_mirror(tmp_path / "repo", desktop=desk) is False
        assert "NEWER BY MTIME: repo mirror" in capsys.readouterr().err

    def test_never_copies_in_either_direction(self, tmp_path: Path) -> None:
        """The conservative rule: the founder has not ruled on which side wins."""
        desk, mirror = self._pair(tmp_path, "desktop\n", "mirror\n")
        sv._check_tracker_mirror(tmp_path / "repo", desktop=desk)
        assert desk.read_text() == "desktop\n"
        assert mirror.read_text() == "mirror\n"

    def test_missing_mirror_warns(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        desk = tmp_path / "Desktop" / "CDSFL_Agent_Operational_Plan.md"
        desk.parent.mkdir(parents=True, exist_ok=True)
        desk.write_text("canonical\n", encoding="utf-8")
        assert sv._check_tracker_mirror(tmp_path / "repo", desktop=desk) is False
        err = capsys.readouterr().err
        assert "Repo mirror is MISSING" in err

    def test_missing_desktop_canonical_warns(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        mirror = tmp_path / "repo" / sv._TRACKER_MIRROR_REL
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_text("mirror\n", encoding="utf-8")
        desk = tmp_path / "Desktop" / "absent.md"
        assert sv._check_tracker_mirror(tmp_path / "repo", desktop=desk) is False
        assert "Canonical Desktop copy is MISSING" in capsys.readouterr().err

    def test_neither_present_is_not_a_cdsfl_tree(
        self, tmp_path: Path, capsys: pytest.CaptureFixture,
    ) -> None:
        desk = tmp_path / "Desktop" / "absent.md"
        assert sv._check_tracker_mirror(tmp_path / "repo", desktop=desk) is True
        assert capsys.readouterr().err == ""


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Minimal git repo with an initial commit (mirrors test_sv_commit.py)."""
    def g(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, capture_output=True,
                       text=True, check=True)
    g("init", "-q", "-b", "main")
    g("config", "user.email", "test@example.com")
    g("config", "user.name", "Test")
    g("config", "commit.gpgsign", "false")
    (tmp_path / "README.md").write_text("seed\n")
    g("add", "README.md")
    g("commit", "-q", "-m", "seed")
    return tmp_path


class TestS5RunsBeforeStaging:
    def test_mirror_check_precedes_the_first_git_add(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Policy says 'refreshed before commit'; the check must run before
        anything is staged, so the operator sees it while it still matters."""
        order: list[str] = []
        monkeypatch.setattr(sv, "repo_root", lambda: git_repo)

        def fake_check(root, desktop=None):
            order.append("tracker-check")
            return True

        real_git = sv._git

        def spy_git(*args, **kwargs):
            order.append(f"git {args[0]}")
            return real_git(*args, **kwargs)

        monkeypatch.setattr(sv, "_check_tracker_mirror", fake_check)
        monkeypatch.setattr(sv, "_git", spy_git)

        (git_repo / "docs").mkdir()
        (git_repo / "docs" / "real.md").write_text("x\n")
        created = sv._commit_and_push(
            message="sv: docs/real.md", push=False, root=git_repo,
            auto_stage=True, validate_message=True,
        )
        assert created is True
        assert order[0] == "tracker-check"
        assert order[1].startswith("git add")
