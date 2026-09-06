"""The discrimination overlay let a falsifier write into the real working tree.

FOUNDER RULING 35, 2026-09-06: "Do it before the next paid run. This is a
containment fix, not a preference." — "Fully approved."

THE DEFECT. `_build_discrimination_overlay` mirrored every sibling as an ABSOLUTE
SYMLINK. Symlinks are transparent to writes, so a falsifier opening a sibling path
for writing followed the link and modified the REAL repository. The old docstring
said "`shutil.rmtree` does not follow symlinks when deleting, so tearing an overlay
down cannot reach the real tree" — true, and about DELETION only, which is what
made it look safe. Reproduced 2026-09-06: one `open(link, "w")` and the real file
changed. Panel agents were separately caught editing the repo mid-run twice, so the
route was not hypothetical.

THE FIX. Prefer an APFS clone, which yields REAL FILES and therefore real
containment, at metadata cost: measured on this repository (683 MB, 15837 files)
at 2.77 s mean over 3 runs, sd 0.19 s. The control is default-off and runs per
finding, so that is affordable — the old "the repo is large" objection was measured
against copying, not cloning. Where cloning is unavailable the builder now RAISES
rather than degrading, matching its own stated contract.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"


@pytest.fixture(scope="module")
def rr():
    mod = types.ModuleType("_rr_overlay")
    mod.__file__ = str(RUNNER)
    sys.modules["_rr_overlay"] = mod
    try:
        exec(compile(RUNNER.read_text(), str(RUNNER), "exec"), mod.__dict__)
    except SystemExit:
        pass
    return mod


@pytest.fixture()
def fake_repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "bench").mkdir(parents=True)
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
    (repo / "bench" / "target.md").write_text("the target\n")
    (repo / "bench" / "sibling.py").write_text("ORIGINAL CONTENT\n")
    (repo / "toplevel.txt").write_text("TOP ORIGINAL\n")
    return repo


def test_writing_to_a_sibling_does_not_reach_the_real_tree(rr, fake_repo):
    """THE DEFECT ITSELF. This is the test that fails on the pre-fix builder."""
    overlay = rr._build_discrimination_overlay(fake_repo, "bench/target.md", "REPLACED\n")
    with open(overlay / "bench" / "sibling.py", "w") as fh:
        fh.write("WRITTEN BY A FALSIFIER\n")
    assert (fake_repo / "bench" / "sibling.py").read_text() == "ORIGINAL CONTENT\n", (
        "a write inside the overlay modified the REAL repository")


def test_a_top_level_write_does_not_reach_the_real_tree(rr, fake_repo):
    overlay = rr._build_discrimination_overlay(fake_repo, "bench/target.md", "REPLACED\n")
    (overlay / "toplevel.txt").write_text("CLOBBERED\n")
    assert (fake_repo / "toplevel.txt").read_text() == "TOP ORIGINAL\n"


def test_no_sibling_is_a_symlink(rr, fake_repo):
    """Containment is structural: if any sibling is still a link, writes escape."""
    overlay = rr._build_discrimination_overlay(fake_repo, "bench/target.md", "REPLACED\n")
    links = [p for p in overlay.rglob("*") if p.is_symlink()]
    assert not links, f"symlinks survive in the overlay, so writes can escape: {links[:5]}"


def test_the_overlay_still_does_its_actual_job(rr, fake_repo):
    """Containment must not cost correctness: one file replaced, the rest present."""
    overlay = rr._build_discrimination_overlay(fake_repo, "bench/target.md", "REPLACED\n")
    assert (overlay / "bench" / "target.md").read_text() == "REPLACED\n"
    assert (overlay / "bench" / "sibling.py").read_text() == "ORIGINAL CONTENT\n"
    assert (overlay / "toplevel.txt").exists()


def test_git_is_never_mirrored(rr, fake_repo):
    overlay = rr._build_discrimination_overlay(fake_repo, "bench/target.md", "REPLACED\n")
    assert not (overlay / ".git").exists(), "a repository inside the sandbox is a route out of it"


def test_it_raises_rather_than_degrading_when_containment_is_impossible(rr, fake_repo, monkeypatch):
    """The builder's own contract is 'Raises rather than degrading'. An overlay
    that silently failed to CONTAIN is worse than one that failed to replace."""
    def _fail(*a, **k):
        return subprocess.CompletedProcess(a[0] if a else [], 1, "", "clone unavailable")
    monkeypatch.setattr(rr.subprocess, "run", _fail)
    monkeypatch.delenv("CDSFL_ALLOW_UNCONTAINED_OVERLAY", raising=False)
    with pytest.raises(RuntimeError, match="CONTAINED overlay"):
        rr._build_discrimination_overlay(fake_repo, "bench/target.md", "REPLACED\n")


def test_the_escape_hatch_works_but_must_be_deliberate(rr, fake_repo, monkeypatch):
    def _fail(*a, **k):
        return subprocess.CompletedProcess(a[0] if a else [], 1, "", "clone unavailable")
    monkeypatch.setattr(rr.subprocess, "run", _fail)
    monkeypatch.setenv("CDSFL_ALLOW_UNCONTAINED_OVERLAY", "1")
    overlay = rr._build_discrimination_overlay(fake_repo, "bench/target.md", "REPLACED\n")
    assert (overlay / "bench" / "target.md").read_text() == "REPLACED\n"


def test_the_overlay_can_actually_be_deleted(rr, fake_repo):
    """PANEL, 2026-09-06 (fable). `.env` carries the BSD `uchg` immutable flag and
    `cp -Rc` PRESERVES flags, so every clone contained an undeletable file. The
    caller cleans up with `shutil.rmtree(ov, ignore_errors=True)`, which swallows
    the EPERM and returns as though it worked -- leaking ~683 MB per overlay,
    silently. 264 orphaned clones were found in TMPDIR.

    The overlay was verified to BUILD and never verified to be REMOVABLE."""
    import shutil
    import subprocess as sp
    env = fake_repo / ".env"
    env.write_text("SECRET=1")
    sp.run(["chflags", "uchg", str(env)], capture_output=True)
    try:
        overlay = rr._build_discrimination_overlay(fake_repo, "bench/target.md", "R\n")
        shutil.rmtree(overlay, ignore_errors=True)
        assert not overlay.exists(), (
            "the overlay survived rmtree -- every run leaks a full clone of the repo")
    finally:
        sp.run(["chflags", "-R", "nouchg", str(fake_repo)], capture_output=True)


def test_an_absolute_symlink_cannot_write_through_the_overlay(rr, fake_repo):
    """PANEL, 2026-09-06 (cc2). `cp -R` RECREATES symlinks rather than dereferencing
    them, so an ABSOLUTE symlink survives into the clone and still resolves to the
    real tree -- the exact defect the clone was meant to remove. Not exploitable in
    the current repo (all 3 symlinks are relative) but that was an invariant nobody
    stated, enforced or tested."""
    victim = fake_repo / "real"
    victim.mkdir()
    (victim / "v.txt").write_text("ORIGINAL\n")
    os.symlink(str(victim), str(fake_repo / "abs_link"))
    overlay = rr._build_discrimination_overlay(fake_repo, "bench/target.md", "R\n")
    escaped = overlay / "abs_link"
    if escaped.exists() or escaped.is_symlink():
        try:
            (escaped / "v.txt").write_text("WRITTEN VIA OVERLAY\n")
        except OSError:
            pass
    assert (victim / "v.txt").read_text() == "ORIGINAL\n", (
        "an absolute symlink wrote through the overlay into the real tree")
