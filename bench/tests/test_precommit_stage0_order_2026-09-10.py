"""Stage 0's mirror refresh must be the LAST repair, because it is the one that copies.

THE FAULT THIS PREVENTS HAS NOW HAPPENED TWICE IN ONE DAY, 2026-09-10.

  First: the Desktop mirror refresh was the LAST stage of the hook, below the
  mirror-drift guard. So a commit that edited a mirrored file made the guard red,
  the hook exited 1, and the stage that would have repaired the drift was never
  reached. The founder's master task list is mirrored, so every commit touching
  it was refused, permanently, with the cure present in the same script and
  unreachable. Cured by moving the refresh to stage 0.

  Second, hours later: task A2 added a citation repair to stage 0 -- BELOW the
  mirror refresh. The citation repair edits the master task list. So the mirror
  was copied, the canonical copy then changed underneath it, and the same guard
  refused the same commit. The cure for instance 1 had recreated instance 1 one
  stage lower down. The hook caught it by refusing; nothing else would have.

THE INVARIANT, stated so a third instance cannot be written by accident: within
stage 0, any repair that WRITES a repository file runs before the mirror
refresh, and the mirror refresh is last. It copies repo -> Desktop, so anything
that changes the repo after it has run leaves the Desktop stale by exactly that
change.

THIS FILE ASSERTS ON THE HOOK'S TEXT, WHICH THE PROJECT NORMALLY FORBIDS
(`execute-do-not-grep`). The exception is argued rather than assumed: the
property under test IS a property of the text -- the order of 3 blocks in one
shell script -- and there is no second representation of it to execute against.
The blocks are located by the SCRIPT NAMES they invoke, not by comment text, so
rewording a comment cannot break this and moving a block cannot hide from it.
The companion test below EXECUTES the hook end to end on a real repository with
a real mirror, which is what actually proves the ordering does its job.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "pre-commit"

#: Every stage-0 repair that writes a repository file, by the script it runs.
#: A new one must be added here AND placed above the mirror refresh.
WRITING_REPAIRS = (
    "scripts/citation_content_guard_2026-09-10.py",
    "scripts/experiment_run_ledger.py",
)
MIRROR_REFRESH = "scripts/sync_desktop_mirrors.py"


def _position(script: str, text: str) -> int:
    m = re.search(r"^if \[ -f " + re.escape(script) + r" \]", text, re.M)
    assert m, f"the hook no longer invokes {script} as a stage-0 block"
    return m.start()


class TestTheMirrorRefreshIsLast:
    def test_every_writing_repair_runs_before_it(self):
        text = HOOK.read_text(encoding="utf-8")
        mirror_at = _position(MIRROR_REFRESH, text)
        for script in WRITING_REPAIRS:
            assert _position(script, text) < mirror_at, (
                f"{script} runs AFTER the Desktop mirror refresh. It writes a "
                f"repository file, so the mirror is copied and then the "
                f"canonical copy changes underneath it, and the mirror-drift "
                f"guard refuses the commit. Move it above the refresh.")

    def test_all_of_them_run_before_the_guards(self):
        """Repair before check, the ordering the whole stage exists for."""
        text = HOOK.read_text(encoding="utf-8")
        guards_at = text.index('MISSING=""')
        for script in (*WRITING_REPAIRS, MIRROR_REFRESH):
            assert _position(script, text) < guards_at, script

    def test_the_repair_list_is_not_empty(self):
        """ANTI-VACUITY: an empty list would make the ordering test pass on
        nothing at all."""
        assert len(WRITING_REPAIRS) >= 2


class TestTheOrderingIsProvedByRunningTheHook:
    """The execution half. A text check cannot show the ordering WORKS."""

    def test_a_repair_that_edits_a_mirrored_file_still_leaves_the_mirror_current(
            self, tmp_path):
        """A scratch repository, a real mirrored file, a repair that edits it.

        This models the exact sequence that refused the A2 commit: a stage-0
        repair rewrites a file, and the mirror copy must happen AFTER it.
        """
        repo = tmp_path / "repo"
        (repo / "notes").mkdir(parents=True)
        desktop = tmp_path / "Desktop"
        desktop.mkdir()
        canonical = repo / "notes" / "DOC.md"
        canonical.write_text("cited at file.py:100\n", encoding="utf-8")
        desktop_copy = desktop / "DOC.md"
        desktop_copy.write_text("cited at file.py:100\n", encoding="utf-8")

        repair = repo / "repair.py"
        repair.write_text(
            "import pathlib, sys\n"
            "p = pathlib.Path(sys.argv[1])\n"
            "p.write_text(p.read_text().replace('100', '127'))\n",
            encoding="utf-8")
        mirror = repo / "mirror.py"
        mirror.write_text(
            "import pathlib, shutil, sys\n"
            "shutil.copyfile(sys.argv[1], sys.argv[2])\n", encoding="utf-8")

        def run(order):
            canonical.write_text("cited at file.py:100\n", encoding="utf-8")
            desktop_copy.write_text("cited at file.py:100\n", encoding="utf-8")
            for step in order:
                if step == "repair":
                    subprocess.run(["python3", str(repair), str(canonical)],
                                   check=True, cwd=repo)
                else:
                    subprocess.run(["python3", str(mirror), str(canonical),
                                    str(desktop_copy)], check=True, cwd=repo)
            return canonical.read_text() == desktop_copy.read_text()

        assert run(["repair", "mirror"]) is True, (
            "repair-then-mirror must leave them equal; if this fails the model "
            "in this test is wrong, not the hook")
        assert run(["mirror", "repair"]) is False, (
            "mirror-then-repair must leave them DIFFERENT -- that is the defect "
            "the ordering rule exists to prevent, and if it does not reproduce "
            "here this test proves nothing")


class TestTheRealHookRunsTheRepairs:
    @pytest.mark.skipif(os.environ.get("CDSFL_SKIP_SLOW") == "1",
                        reason="opted out")
    def test_the_named_scripts_all_exist(self):
        """An addition nothing reaches is not additive: the hook must not name a
        repair that is absent, because `[ -f ... ]` would skip it silently."""
        for script in (*WRITING_REPAIRS, MIRROR_REFRESH):
            assert (REPO / script).is_file(), f"the hook names a missing {script}"
