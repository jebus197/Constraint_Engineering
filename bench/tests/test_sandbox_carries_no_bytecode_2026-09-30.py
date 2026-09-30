"""A panel sandbox must carry no compiled bytecode, because a `.pyc` is a route
back into the real repository.

WHY THIS EXISTS. Found 2026-09-30 by the fable seat inspecting its OWN failure
during the calculator-design review: its regression run inside a sandbox produced
tracebacks naming paths in the REAL repository. A `.pyc` embeds in `co_filename`
the absolute path of the source it was compiled from, so a cached module imported
inside the sandbox reports a `__file__` pointing OUTSIDE it, and anything deriving
a path from `__file__` can then import real-repository modules into a panel
measurement. The seat demonstrated it by running `strings` over the `.pyc`,
purging, and re-running.

This is the founder's hard rule at stake, not a tidiness preference: *"none of the
models... should ever be able to reach the real repo, let alone edit it!"*

WHY NO EXISTING GUARD SAW IT, and there are 3 separate reasons, each sufficient:

1. `build` clones with `cp -Rc` for the metadata cost, and a clone takes
   EVERYTHING. `shutil.copytree(..., ignore=...)` is only the fallback when the
   clone fails, so on any filesystem that supports cloning the ignore list never
   runs at all.
2. `_NEVER_COPY` is `frozenset({".git"})`, so even the fallback excluded no cache.
3. The delete loop beside it is NON-RECURSIVE -- it removes `dest / name` only --
   while caches are scattered throughout a tree.

And `secret_ignore`'s docstring CLAIMED the caches were excluded. That paragraph
describes the 4 `copytree` callers, not `build`, which is the same defect shape as
the `e2_regression` docstring corrected the same day: a true sentence about one
path, read as a property of another.

MEASURED BEFORE THE FIX: of the 104 sandboxes still on disk from the 2026-09-30
rounds, individual sandboxes carried 61, 83, 24 and 4 `.pyc` files.

WHAT THIS FILE CHECKS, BY EXECUTION. It stages a real tree that deliberately
contains `__pycache__` directories and `.pyc` files at several depths, CALLS
`panel_sandbox.build`, and asserts none survive. It does not read the source of
the purge, because `execute-do-not-grep` applies most sharply here: the source
already described a property it did not have.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench import panel_sandbox  # noqa: E402


def _seed(root: pathlib.Path) -> int:
    """A tree with bytecode at 3 depths, plus a decoy that must SURVIVE."""
    planted = 0
    for rel in ("__pycache__", "pkg/__pycache__", "pkg/sub/deep/__pycache__"):
        d = root / rel
        d.mkdir(parents=True, exist_ok=True)
        for name in ("mod.cpython-313.pyc", "other.cpython-313.pyc"):
            (d / name).write_bytes(b"\x00\x0f\r\n" + str(REPO).encode())
            planted += 1
    # a loose .pyc outside any __pycache__, and a .pyo
    (root / "pkg").mkdir(parents=True, exist_ok=True)
    (root / "pkg" / "loose.pyc").write_bytes(b"\x00\x0f\r\n"); planted += 1
    (root / "pkg" / "legacy.pyo").write_bytes(b"\x00\x0f\r\n"); planted += 1
    # DECOYS: real source and a file whose name merely contains the substring.
    (root / "pkg" / "real_module.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "pkg" / "notes_about_pyc_files.md").write_text("prose\n", encoding="utf-8")
    (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    return planted


@pytest.fixture
def staged(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    planted = _seed(src)
    dest = panel_sandbox.build(src)
    yield src, dest, planted


class TestNoBytecodeSurvives:
    def test_build_leaves_no_pyc_or_pyo(self, staged):
        _src, dest, planted = staged
        assert planted >= 8, f"the fixture planted only {planted}; it must be non-trivial"
        stale = sorted(str(p.relative_to(dest))
                       for pat in ("*.pyc", "*.pyo") for p in dest.rglob(pat))
        assert not stale, (
            f"{len(stale)} compiled artefact(s) survived into the sandbox: {stale[:6]}. "
            f"A .pyc embeds the absolute path it was compiled from, so an import "
            f"inside the sandbox can resolve to the real repository.")

    def test_build_leaves_no_pycache_directory(self, staged):
        _src, dest, _ = staged
        left = sorted(str(p.relative_to(dest)) for p in dest.rglob("__pycache__"))
        assert not left, f"__pycache__ directories survived: {left[:6]}"

    def test_the_real_source_is_NOT_removed(self, staged):
        """The purge must not be a blunt instrument.

        Without this, deleting the whole tree would pass the 2 tests above, which
        is the shape of a guard that cannot fail in the direction it exists for.
        """
        _src, dest, _ = staged
        assert (dest / "pkg" / "real_module.py").is_file(), "the purge removed real source"
        assert (dest / "pkg" / "__init__.py").is_file(), "the purge removed a package marker"
        assert (dest / "pkg" / "notes_about_pyc_files.md").is_file(), (
            "a file whose NAME merely contains 'pyc' was removed; the purge must key "
            "on the extension and the directory name, not on a substring")


class TestTheFixtureWouldHaveCaughtTheOriginalDefect:
    """The seed must reproduce the pre-fix condition, or the test proves nothing."""

    def test_the_planted_tree_really_contains_bytecode(self, tmp_path):
        src = tmp_path / "s"
        src.mkdir()
        planted = _seed(src)
        found = [p for pat in ("*.pyc", "*.pyo") for p in src.rglob(pat)]
        assert len(found) == planted, (
            f"seeded {planted} but found {len(found)} in the source tree; the "
            f"fixture is not reproducing the condition under test")
        assert any("deep" in str(p) for p in found), (
            "no deeply nested artefact was planted, so a non-recursive purge would "
            "pass this file -- which is exactly the defect that was found")

    def test_a_pyc_really_embeds_an_absolute_path(self, tmp_path):
        """The MECHANISM, not just the presence. This is why it is a containment
        issue and not a size one."""
        src = tmp_path / "s"
        src.mkdir()
        _seed(src)
        blob = (src / "__pycache__" / "mod.cpython-313.pyc").read_bytes()
        assert str(REPO).encode() in blob, (
            "the fixture's .pyc does not carry an absolute path, so it cannot "
            "demonstrate the co_filename mechanism the purge exists to remove")
