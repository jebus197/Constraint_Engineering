"""The founder reads 3 files from his Desktop. They must not silently diverge.

MEASURED, not anticipated. On 2026-09-10 at 10:30 BST he asked whether the
outcomes companion "on my desktop (which I presume you have been updating)" was
current. It was not: the master task list was 29,044 bytes short and 3.45 h
behind its canonical copy, and the outcomes log 5,016 bytes short and 3.40 h
behind. 1 of 3 mirrors was current.

The same class of staleness had already cost him a journey. On 2026-09-09 a
restore read a stale line and reported that an answer-key sealing awaited him; he
had driven home from his hotel and done it himself on 2026-09-07 at 22:03. Task
V5 fixed the ORDER in which documents are read. It could not stop a mirror
drifting, and `cdsfl_recover.py` could not even SEE 2 of the 3 mirrors.

Three things are held here: the sync exists and works, the restore names all 3
and reports divergence, and the commit hook refreshes them without ever being
able to refuse a commit for it.
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SYNC = ROOT / "scripts" / "sync_desktop_mirrors.py"
HOOK = ROOT / "hooks" / "pre-commit"


def _load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def sync():
    return _load(SYNC)


class TestTheSyncWorks:
    def test_it_names_the_three_files_the_founder_reads(self, sync):
        assert set(sync.MIRRORED) == {
            "CDSFL_MASTER_TASK_LIST.md",
            "CDSFL_OUTCOMES_LOG.md",
            "CDSFL_Agent_Operational_Plan.md",
        }

    def test_drift_is_detected_and_repaired(self, sync, tmp_path, monkeypatch):
        """Drive it against a fake Desktop, so the real one is not touched."""
        fake = tmp_path / "Desktop"
        fake.mkdir()
        monkeypatch.setattr(sync, "DESKTOP", fake)
        assert len(sync.drift()) == 3, "an empty Desktop must report all 3 missing"
        assert sync.main.__call__ is not None
        monkeypatch.setattr(sys, "argv", ["sync"])
        assert sync.main() == 0
        assert sync.drift() == [], "after a sync, nothing should be adrift"

    def test_a_diverged_copy_is_detected(self, sync, tmp_path, monkeypatch):
        fake = tmp_path / "Desktop"
        fake.mkdir()
        monkeypatch.setattr(sync, "DESKTOP", fake)
        monkeypatch.setattr(sys, "argv", ["sync"])
        sync.main()
        victim = fake / "CDSFL_OUTCOMES_LOG.md"
        victim.write_text(victim.read_text(encoding="utf-8") + "\ndrifted\n",
                          encoding="utf-8")
        d = sync.drift()
        assert [n for n, _, _ in d] == ["CDSFL_OUTCOMES_LOG.md"], d

    def test_check_mode_writes_nothing(self, sync, tmp_path, monkeypatch):
        """--check must be safe to run anywhere, including in a test."""
        fake = tmp_path / "Desktop"
        fake.mkdir()
        monkeypatch.setattr(sync, "DESKTOP", fake)
        monkeypatch.setattr(sys, "argv", ["sync", "--check"])
        assert sync.main() == 1
        assert list(fake.iterdir()) == [], "--check created files"

    def test_it_never_copies_desktop_back_over_the_repository(self):
        """The repository copy is canonical by founder ruling of 2026-08-05."""
        src = SYNC.read_text(encoding="utf-8")
        assert "shutil.copy2(src, dst)" in src
        assert "copy2(dst, src)" not in src and "copy(dst, src)" not in src


class TestTheRestoreCanSeeThem:
    def test_first_read_names_all_three_mirrors(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "cdsfl_recover.py")],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr[-800:]
        first = r.stdout.split("## RUNNING NOW")[0]
        for name in ("CDSFL_MASTER_TASK_LIST.md", "CDSFL_OUTCOMES_LOG.md",
                     "CDSFL_Agent_Operational_Plan.md"):
            assert f"Desktop/{name}" in first, (
                f"the restore does not name the Desktop copy of {name}, so it "
                f"cannot warn that what the founder is reading is stale")

    def test_a_diverged_mirror_is_announced_loudly(self, sync, tmp_path, monkeypatch):
        """The load-bearing case: silence about divergence is the whole defect."""
        R = _load(ROOT / "scripts" / "cdsfl_recover.py")
        fake = tmp_path / "Desktop"
        fake.mkdir()
        (fake / "CDSFL_MASTER_TASK_LIST.md").write_text("stale", encoding="utf-8")
        monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
        out = "\n".join(R.first_read_lines(ROOT))
        assert "DIVERGED" in out, "a diverged Desktop copy was reported as ordinary"


class TestTheHookRefreshesButCannotRefuse:
    def test_the_hook_calls_the_sync(self):
        src = HOOK.read_text(encoding="utf-8")
        assert "sync_desktop_mirrors.py" in src, (
            "the hook does not refresh the mirrors, so they will drift again")

    def test_the_refresh_stage_cannot_exit_non_zero(self):
        """A convenience copy must never block a commit.

        Parsed as a block rather than grepped for `exit 1`: the hook contains
        many legitimate refusals earlier, and this asserts only about the stage
        that was added for the mirrors.
        """
        src = HOOK.read_text(encoding="utf-8")
        i = src.index("STAGE 6")
        stage = src[i:]
        assert "exit 1" not in stage, (
            "the mirror-refresh stage can refuse a commit; it must not")
        assert stage.rstrip().endswith("exit 0")
