"""sv must survive a memory directory it can see but cannot read.

WHAT HAPPENED. 2026-08-26 ~01:45 BST, mid-session, this process lost read access
to ~/.claude/projects/.../memory. Edits to files in it had succeeded forty
minutes earlier. Under that state:

    exists() -> True    is_dir() -> True
    iterdir() -> PermissionError
    read_text() -> PermissionError
    glob(...) -> []     <-- EMPTY LIST, does not raise

sv guarded every memory access with is_dir(), so no guard fired, and
_update_memory_exclusions_ledger crashed the whole save with a traceback and
exit 1. Measured: `python3 scripts/cdsfl_sv.py` exited 1 at 01:52 having exited
0 at 00:53 on the same tree.

THE DISTINCTION THIS ENFORCES. Absent and unreadable are not the same:

    ABSENT      -> there is nothing to count. Skip is honest.
    UNREADABLE  -> the count DID NOT HAPPEN. It must be reported as a failed
                   measurement, must not crash the save, must not write 0, and
                   above all must NOT refresh the "counted <date>" stamp --
                   because that stamp is a claim about when the number was last
                   verified, and refreshing it after a failure is a lie about
                   provenance.

The glob() branch is the nastiest of the three, because an empty list is a
plausible answer. A denial that returns a plausible answer is the failure class
this project keeps finding.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import cdsfl_sv as sv  # noqa: E402


@pytest.fixture
def denied_dir(tmp_path):
    """A directory that exists, is_dir()s, and cannot be enumerated."""
    d = tmp_path / "memory"
    d.mkdir()
    (d / "MEMORY.md").write_text("# index\n")
    (d / "a_memory.md").write_text("x\n")
    os.chmod(d, 0o000)
    yield d
    os.chmod(d, 0o755)


@pytest.fixture
def readable_dir(tmp_path):
    d = tmp_path / "memory_ok"
    d.mkdir()
    (d / "MEMORY.md").write_text("# index\n")
    (d / "a_memory.md").write_text("x\n")
    return d


@pytest.mark.skipif(os.geteuid() == 0, reason="running as root bypasses chmod")
class TestMemoryFilesDiscriminates:
    def test_known_good_a_readable_directory_lists(self, readable_dir):
        names = {p.name for p in sv._memory_files(readable_dir)}
        assert names == {"MEMORY.md", "a_memory.md"}

    def test_known_bad_a_denied_directory_RAISES(self, denied_dir):
        """It must raise, NOT return []. An empty list is a plausible answer and
        would be recorded as a real count of zero."""
        with pytest.raises(sv.MemoryUnreadable):
            sv._memory_files(denied_dir)

    def test_the_two_answers_differ(self, readable_dir, denied_dir):
        good = sv._memory_files(readable_dir)
        try:
            bad = sv._memory_files(denied_dir)
        except sv.MemoryUnreadable:
            bad = "RAISED"
        assert good and bad == "RAISED", (
            "readable and denied produce the same answer; the distinction is lost"
        )

    def test_the_message_says_the_count_did_not_happen(self, denied_dir):
        with pytest.raises(sv.MemoryUnreadable) as ei:
            sv._memory_files(denied_dir)
        msg = str(ei.value)
        assert "did not happen" in msg and "not evidence" in msg, (
            f"the message does not distinguish a failed measurement from an "
            f"empty directory: {msg}"
        )


@pytest.mark.skipif(os.geteuid() == 0, reason="running as root bypasses chmod")
class TestTheLedgerIsNotFalselyStamped:
    def _ledger(self, tmp_path, stamp="2026-01-01 00:00 GMT", total=118):
        root = tmp_path / "repo"
        (root / "resources").mkdir(parents=True)
        (root / "resources" / "MEMORY_EXCLUSIONS.md").write_text(
            f"# Ledger\n\n## Accounting (counted {stamp})\n\n"
            "The directory holds **119 files**, of which one is `MEMORY.md` itself\n"
            "(the index), leaving **118 individual memory files**.\n\n"
            f"| bucket | n |\n|---|---|\n| total | {total} |\n\n"
            "## Excluded Entries\n\n## Unclassified — awaiting review\n",
            encoding="utf-8")
        return root

    def test_a_denied_directory_raises_rather_than_writing(self, tmp_path, denied_dir):
        root = self._ledger(tmp_path)
        before = (root / "resources/MEMORY_EXCLUSIONS.md").read_text()
        with pytest.raises(sv.MemoryUnreadable):
            sv._update_memory_exclusions_ledger(root, mem_dir=denied_dir)
        after = (root / "resources/MEMORY_EXCLUSIONS.md").read_text()
        assert before == after, (
            "the ledger was rewritten despite the count failing; the counted "
            "date would then assert a freshness the run cannot support"
        )

    def test_the_counted_stamp_is_not_advanced_on_failure(self, tmp_path, denied_dir):
        root = self._ledger(tmp_path, stamp="2026-01-01 00:00 GMT")
        with pytest.raises(sv.MemoryUnreadable):
            sv._update_memory_exclusions_ledger(root, mem_dir=denied_dir)
        assert "counted 2026-01-01 00:00 GMT" in (
            root / "resources/MEMORY_EXCLUSIONS.md").read_text(), (
            "the 'counted' stamp moved after a failed recount"
        )

    def test_a_readable_directory_still_recounts(self, tmp_path, readable_dir):
        """KNOWN-GOOD: the guard must not have disabled the feature."""
        root = self._ledger(tmp_path, total=999)
        changed = sv._update_memory_exclusions_ledger(
            root, mem_dir=readable_dir, counted_at="2026-08-26 02:00 BST")
        text = (root / "resources/MEMORY_EXCLUSIONS.md").read_text()
        assert changed is True, "a readable directory produced no recount"
        assert "| total | 1 |" in text, f"count not rewritten:\n{text}"
        assert "counted 2026-08-26 02:00 BST" in text


@pytest.mark.skipif(os.geteuid() == 0, reason="running as root bypasses chmod")
def test_sv_exits_zero_and_says_so_when_memory_is_unreadable(denied_dir):
    """END TO END. This is the regression proper: sv exited 1 with a traceback."""
    env = dict(os.environ)
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys, pathlib; sys.path.insert(0, 'scripts'); "
         "import cdsfl_sv as sv; sv._MEMORY_DIR = pathlib.Path(sys.argv[1]); "
         "sys.argv = ['cdsfl_sv.py']; sys.exit(sv.main())",
         str(denied_dir)],
        capture_output=True, text=True, cwd=REPO, env=env, timeout=300)
    assert r.returncode == 0, (
        f"sv exited {r.returncode} on an unreadable memory directory.\n"
        f"STDERR tail:\n{r.stderr[-800:]}"
    )
    assert "NOT RECOUNTED" in r.stdout, (
        "sv survived but said nothing; a silent survival is indistinguishable "
        f"from a successful recount.\nSTDOUT tail:\n{r.stdout[-800:]}"
    )
    assert "failed measurement" in r.stdout
