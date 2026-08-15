"""The panel's shell-bearing routes must be confinable to a directory.

Exp 48, 2026-07-29: a routed model wrote a falsifier that opened the exam
answer key and printed the whole planted set. The key had been moved out of the
repository that morning; the config note recording where it moved to was
committed INSIDE the repository 76 minutes before the run started. The panel is
dispatched with Bash/Read/Grep/Glob and inherited the runner's cwd — this repo —
so the note was one grep away, and superseded keys were one `git show` away.

Two controls are pinned here:
  * claude_cli and codex_exec dispatches honour the configured panel cwd;
  * a missing directory RAISES instead of falling back to the repo. Failing open
    would silently reinstate the exposure, which is exactly how it went unnoticed
    the first time.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

import bench.experiment_11_orchestrator as orch  # noqa: E402


@pytest.fixture(autouse=True)
def _restore_panel_cwd():
    before = orch.get_panel_cwd()
    yield
    orch.set_panel_cwd(before)


class TestPanelCwd:
    def test_default_is_inherited(self):
        orch.set_panel_cwd(None)
        assert orch.get_panel_cwd() is None

    def test_missing_directory_raises_rather_than_failing_open(self):
        with pytest.raises(NotADirectoryError):
            orch.set_panel_cwd("/nonexistent/staged/targets")
        assert orch.get_panel_cwd() is None

    def test_file_path_is_refused(self, tmp_path):
        f = tmp_path / "exp50_physics.md"
        f.write_text("x", encoding="utf-8")
        with pytest.raises(NotADirectoryError):
            orch.set_panel_cwd(str(f))

    def test_resolves_and_expands(self, tmp_path):
        orch.set_panel_cwd(str(tmp_path))
        assert orch.get_panel_cwd() == str(tmp_path.resolve())

    @pytest.mark.parametrize(
        "fn,kwargs",
        [
            ("call_claude_cli", dict(model_id="opus", system_prompt=None,
                                     user_prompt="p", max_retries=1)),
            ("call_codex", dict(user_prompt="p", cdsfl_directives="d", max_retries=1)),
        ],
    )
    def test_dispatch_passes_cwd_to_subprocess(self, monkeypatch, tmp_path, fn, kwargs):
        """Both shell-bearing routes must hand the cwd to subprocess.run."""
        target = getattr(orch, fn, None)
        if target is None:
            pytest.skip(f"{fn} not present in this orchestrator revision")
        orch.set_panel_cwd(str(tmp_path))
        seen = {}

        def fake_run(cmd, **kw):
            seen.update(kw)
            return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

        monkeypatch.setattr(orch.subprocess, "run", fake_run)
        monkeypatch.setattr(orch, "CLAUDE_CLI", "/bin/true", raising=False)
        try:
            target(**kwargs)
        except Exception:  # route-specific post-processing is not under test
            pass
        assert seen.get("cwd") == str(tmp_path.resolve()), (
            f"{fn} did not confine the panel: cwd={seen.get('cwd')!r}"
        )


class TestExamConfigsAreConfined:
    """Every exam config must confine the panel; code configs must not."""

    def test_exam_configs_set_panel_cwd_outside_the_repo(self):
        import glob
        import json
        from pathlib import Path

        repo = Path(_root)
        missing = []
        for pattern in ("bench/exp4[89]_configs/*exam*.json",
                        "bench/exp5[0-3]_configs/*.json"):
            for path in glob.glob(str(repo / pattern)):
                cfg = json.loads(Path(path).read_text(encoding="utf-8"))
                cwd = cfg.get("panel_cwd", "")
                if not cwd:
                    missing.append(f"{Path(path).name}: panel_cwd unset")
                    continue
                resolved = Path(cwd).expanduser().resolve()
                if repo.resolve() in resolved.parents or resolved == repo.resolve():
                    missing.append(f"{Path(path).name}: panel_cwd inside the repo ({cwd})")
        assert not missing, "EXAM PANEL NOT CONFINED:\n  " + "\n  ".join(missing)

    def test_confinement_survives_a_resume(self):
        """A resumed run that loses confinement silently reinstates the exposure.

        Config keys being dropped on one path but not another is the failure class
        that has now bitten this project five times, and a resume is a third path
        through the same seam.
        """
        import glob
        import json
        from types import SimpleNamespace
        from pathlib import Path

        from bench.launcher_core import build_runner_config_from_dict

        checked = 0
        for pattern in ("bench/exp4[89]_configs/*exam*.json", "bench/exp5[0-3]_configs/*.json"):
            for path in glob.glob(str(Path(_root) / pattern)):
                cfg = json.loads(Path(path).read_text(encoding="utf-8"))
                want = cfg.get("panel_cwd", "")
                for resume in (False, True):
                    got = build_runner_config_from_dict(
                        dict(cfg), SimpleNamespace(resume=resume)).panel_cwd
                    assert got == want, (
                        f"{Path(path).name}: panel_cwd lost with resume={resume} "
                        f"({got!r} != {want!r})")
                checked += 1
        assert checked, "no exam configs found to check"
