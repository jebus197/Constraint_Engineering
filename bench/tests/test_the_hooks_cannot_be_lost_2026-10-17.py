"""Every session hook must be ONE file reachable from the repository.

WHY. The hooks that enforce this project's discipline run from
`~/.claude/hooks/`, outside the repository. Measured 2026-10-17: of 12 live
hooks, 5 were hard-linked to a repository copy, 6 were separate files that
happened to be identical, and 1 -- the ticket queue gate written that morning --
was absent from the repository altogether. 41.6667% linked, Wilson [19.3260%,
68.0489%].

A SEPARATE COPY CAN DIVERGE SILENTLY and an absent one can be lost outright. The
danger is not hypothetical: while mutation-testing the negation fix to
`local_resource_budget.py` that same morning, a stale backup was copied back over
the live hook, removing the fix. That file happened to be hard-linked, so git saw
it; had it been one of the 6 separate copies, nothing would have.

A HARD LINK MAKES THE 2 PATHS ONE FILE. Editing either edits both, so git sees
every change and no copy can drift. That is why this is checked by INODE and not
by comparing contents: identical contents today says nothing about tomorrow.
"""
from __future__ import annotations

import os
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
REPO_HOOKS = REPO / "hooks"
LIVE_HOOKS = pathlib.Path.home() / ".claude" / "hooks"


def _live_hooks() -> list[pathlib.Path]:
    if not LIVE_HOOKS.is_dir():
        return []
    return sorted(LIVE_HOOKS.glob("*.py"))


def test_there_are_live_hooks_to_check():
    """Anti-vacuity: every assertion below is empty if this is empty."""
    hooks = _live_hooks()
    if not hooks:
        pytest.skip("no live hooks on this machine")
    assert len(hooks) >= 5, f"only {len(hooks)} live hooks found; expected the full set"


@pytest.mark.parametrize("name", [p.name for p in _live_hooks()] or ["none"])
def test_every_live_hook_has_a_repository_copy(name):
    if name == "none":
        pytest.skip("no live hooks on this machine")
    repo_copy = REPO_HOOKS / name
    assert repo_copy.is_file(), (
        f"the live hook {name} has no copy at hooks/{name}, so it is unversioned "
        "and a careless overwrite loses it with nothing in git to show it. This "
        "is how the ticket queue gate sat unversioned on the morning it was "
        "written.")


@pytest.mark.parametrize("name", [p.name for p in _live_hooks()] or ["none"])
def test_every_live_hook_is_the_same_file_as_its_repository_copy(name):
    if name == "none":
        pytest.skip("no live hooks on this machine")
    live = LIVE_HOOKS / name
    repo_copy = REPO_HOOKS / name
    if not repo_copy.is_file():
        pytest.skip("covered by the previous test")
    assert os.stat(live).st_ino == os.stat(repo_copy).st_ino, (
        f"{name} exists at both paths as SEPARATE files. They may be identical "
        "today, which says nothing about tomorrow: an edit to one will not reach "
        "the other and git will show nothing. Hard-link them so the 2 paths are "
        f"1 file:\n    ln -f hooks/{name} ~/.claude/hooks/{name}\n"
        "Check the contents match before linking, because linking silently keeps "
        "one of the 2 versions.")


def test_the_refusing_gates_are_all_present():
    """The hooks that can REFUSE are the ones whose loss would be invisible.

    A prompt-submit hook that vanishes merely stops advising, and the advice was
    being ignored anyway. A Stop gate that vanishes stops REFUSING, and every
    Stop refusal over 2026-10-16 and 2026-10-17 found a real defect. So these 4
    are named individually rather than left to the general rule.
    """
    required = ("compaction_task_boundary.py", "ffafp_stop_gate.py",
                "sv_milestone_gate.py", "ticket_queue_gate.py")
    missing = [n for n in required if not (REPO_HOOKS / n).is_file()]
    assert not missing, (
        f"these Stop gates have no versioned copy: {missing}. Each of them can "
        "refuse a turn, and a refusal that silently stops happening is "
        "indistinguishable from compliance.")
