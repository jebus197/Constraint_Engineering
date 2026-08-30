"""The discrimination overlay must not carry the repository's history into itself.

MEASURED 2026-08-30 by the cc2 reviewer, re-verified here on a live overlay. The
overlay symlink-mirrors the repo root, and `.git` was mirrored with everything
else. Every overlay differs from the tracked file by exactly the mutation under
test, so with `.git` reachable:

    git -C <overlay> diff            -> the mutation set
    git -C <overlay> log             -> real history
    git -C <overlay> show HEAD:<tgt> -> the pristine file

That is the planted set at precision 1.000 with no key required -- the same leak
`canary_seeding.seed` refuses a tracked target to prevent, arriving by a route
that guard cannot see, because the overlay is not itself a tracked tree.

It had a second effect: `_in_a_git_worktree` walks for a `.git`, the symlink
satisfied it, and `seed()` therefore REFUSED the overlay -- the one place
in-flight canary seeding could ever have been legitimate.
"""
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

from reference_runner_v2 import _build_discrimination_overlay   # noqa: E402
from bench.canary_seeding import _in_a_git_worktree             # noqa: E402

TARGET = "bench/evidence.py"
MUTATION = "# MUTATED FOR THIS TEST\n"


def _overlay():
    return _build_discrimination_overlay(REPO, TARGET, MUTATION)


def test_the_overlay_carries_no_dot_git():
    ov = _overlay()
    try:
        assert not (ov / ".git").exists(), "the repository's history is reachable from the sandbox"
    finally:
        shutil.rmtree(ov, ignore_errors=True)


def test_git_cannot_resolve_a_repository_from_inside_the_overlay():
    ov = _overlay()
    try:
        for args in (["log", "--oneline", "-1"], ["diff", "--stat"],
                     ["show", f"HEAD:{TARGET}"]):
            r = subprocess.run(["git", "-C", str(ov), *args], capture_output=True, text=True)
            assert r.returncode != 0, (
                f"`git {' '.join(args)}` succeeded inside the overlay and returned "
                f"{r.stdout.strip()[:120]!r}; the plant is recoverable at precision 1.0")
    finally:
        shutil.rmtree(ov, ignore_errors=True)


def test_the_overlay_is_otherwise_intact():
    """The known-GOOD half: removing .git must not break the mirror."""
    ov = _overlay()
    try:
        assert (ov / "bench").exists(), "the symlink mirror was damaged"
        leaf = ov / TARGET
        assert not leaf.is_symlink() and leaf.read_text() == MUTATION, (
            "the substituted leaf is missing or is a symlink into the real tree")
    finally:
        shutil.rmtree(ov, ignore_errors=True)


def test_canary_seeding_now_accepts_the_overlay():
    """The second effect. Before the fix the symlinked .git made seed() refuse
    the overlay, which is the only place in-flight seeding could be legitimate."""
    ov = _overlay()
    try:
        assert _in_a_git_worktree(ov / TARGET) is None, (
            "seed() still treats the overlay as a tracked tree and will refuse it")
    finally:
        shutil.rmtree(ov, ignore_errors=True)
