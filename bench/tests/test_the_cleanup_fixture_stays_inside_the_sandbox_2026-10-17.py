"""The temp-tree cleanup may not reach a real file through a symlink.

FOUND 2026-10-17 BY EXECUTION, not by reading. `bench/tests/conftest.py` carries
an autouse teardown, written 2026-09-08 for a sound reason: tests that chmod
directories DOWN on purpose left pytest unable to delete its own temp trees, and
11 MB of undeletable `garbage-*` directories had accumulated behind a wall of
warnings. It walked `tmp_path` and set every file to 600 and every directory to
700.

`pathlib.Path.chmod` FOLLOWS A SYMLINK. So for any test that symlinks a real
path into `tmp_path`, the teardown changed the mode of the TARGET:

  * a new test symlinked the repository's `scripts/` tree, and 22 git-tracked
    scripts lost the execute bit git records as 100755;
  * `test_desktop_mirrors_stay_current_2026-09-10` symlinks EVERY entry of
    `Path.home()` into `tmp_path`;
  * `test_canary_seeding_2026-08-28` symlinks the repository ROOT.

THE EVIDENCE IS THE PAIR OF LITERALS. The umask on this machine is 022, so any
file a tool creates here is 644 and any directory 755. Yet `~/.zshrc`,
`~/.gitconfig` and `~/AGENTS.md` stand at exactly 600, 361 of 400 tracked
scripts at exactly 600, and the repository root at exactly 700 -- the two values
this teardown wrote. `/usr/bin/git`, which one test also symlinks, is still 755
because the system protects it and the `OSError` was swallowed.

SKIPPING A SYMLINK LOSES NOTHING, which is why this is a repair and not a
narrowing: `rm_rf` unlinks a symlink without reading its target, so the target's
permissions were never needed to delete the tree, and deleting the tree is the
fixture's whole purpose.

The assertions CALL `restore_modes_for_cleanup` rather than relying on one test
running after another, because an ordering-dependent assertion stops holding the
moment the order changes.
"""
from __future__ import annotations

import os
import pathlib

import pytest

from conftest import restore_modes_for_cleanup

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_a_symlinked_file_keeps_its_own_mode(tmp_path):
    """The target of a symlink inside the sandbox is not touched."""
    outside = tmp_path.parent / "outside_the_sandbox.sh"
    outside.write_text("#!/bin/sh\necho hello\n", encoding="utf-8")
    outside.chmod(0o755)
    sand = tmp_path / "sand"
    sand.mkdir()
    (sand / "link.sh").symlink_to(outside)

    restore_modes_for_cleanup(sand)

    assert oct(outside.stat().st_mode)[-3:] == "755", (
        "the cleanup reached through a symlink and changed a real file")
    # AND IT STILL DOES ITS JOB on a real file inside the sandbox.
    real = sand / "real.txt"
    real.write_text("x", encoding="utf-8")
    real.chmod(0o000)
    restore_modes_for_cleanup(sand)
    assert oct(real.stat().st_mode)[-3:] == "600"


def test_a_symlinked_directory_keeps_its_own_mode(tmp_path):
    """A symlink to a DIRECTORY is the dangerous case: `is_dir()` follows it.

    This is the shape that set the repository root to 700 --
    `test_canary_seeding_2026-08-28` symlinks the repository root into
    `tmp_path`, `p.is_dir()` returned True through the link, and the chmod
    landed on the real directory.
    """
    outside = tmp_path.parent / "outside_dir"
    outside.mkdir(exist_ok=True)
    outside.chmod(0o755)
    sand = tmp_path / "sand"
    sand.mkdir()
    (sand / "dirlink").symlink_to(outside)

    restore_modes_for_cleanup(sand)

    assert oct(outside.stat().st_mode)[-3:] == "755", (
        "the cleanup chmodded a real directory through a symlink")
    # The sandbox's own directories are still made traversable.
    inner = sand / "inner"
    inner.mkdir()
    inner.chmod(0o000)
    restore_modes_for_cleanup(sand)
    assert oct(inner.stat().st_mode)[-3:] == "700"


def test_the_tree_is_still_deletable_afterwards(tmp_path):
    """The purpose it was written for still holds: `rm_rf` can finish.

    Asserted by DELETING, because that is the property the fixture exists to
    provide, and a mode assertion alone would not show it.
    """
    from _pytest.pathlib import rm_rf
    sand = tmp_path / "sand"
    (sand / "deep" / "deeper").mkdir(parents=True)
    (sand / "deep" / "deeper" / "f.txt").write_text("x", encoding="utf-8")
    outside = tmp_path.parent / "survivor.txt"
    outside.write_text("must survive\n", encoding="utf-8")
    outside.chmod(0o644)
    (sand / "deep" / "link.txt").symlink_to(outside)
    (sand / "deep" / "deeper").chmod(0o000)

    restore_modes_for_cleanup(sand)
    rm_rf(sand)

    assert not sand.exists(), "the tree could not be deleted"
    assert outside.is_file() and outside.read_text() == "must survive\n"
    assert oct(outside.stat().st_mode)[-3:] == "644"


def test_the_repo_scripts_executable_bits_match_what_git_records():
    """No tracked script may sit on disk without the mode git records.

    THIS IS THE RATCHET. 22 scripts were found stripped on 2026-10-17; this
    turns red if any tracked file's on-disk execute bit disagrees with the index,
    whatever the cause, so the same silent drift cannot return unnoticed.
    """
    import subprocess
    out = subprocess.run(["git", "ls-files", "-s", "scripts", "bench", "hooks"],
                         capture_output=True, text=True, cwd=str(REPO))
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    wrong = []
    for line in out.stdout.splitlines():
        meta, _, path = line.partition("\t")
        mode = meta.split()[0]
        f = REPO / path
        if not f.is_file() or f.is_symlink():
            continue
        on_disk_x = bool(f.stat().st_mode & 0o111)
        recorded_x = mode == "100755"
        if on_disk_x != recorded_x:
            wrong.append((path, mode, oct(f.stat().st_mode)[-3:]))
    assert not wrong, (
        f"{len(wrong)} tracked file(s) disagree with the index on the execute "
        f"bit:\n" + "\n".join(f"    {p}: git {m}, disk {d}"
                              for p, m, d in wrong[:25]))
