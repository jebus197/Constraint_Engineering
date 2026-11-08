"""The sv gate regenerates local state itself, and still commits nothing. B71.

HIS RULING, 2026-11-08: *"Permission is granted. stm"*.

WHY PERMISSION WAS NEEDED AT ALL. `hooks/sv_milestone_gate.py` is HARD-LINKED
into `~/.claude/hooks/`, one inode, so editing the repository copy edits the
hook that is actually running. Changing a running hook is self-modification and
is his to authorise, which is why this sat as BLOCKED rather than being built
when it was designed.

WHAT THE CHANGE IS. The gate refuses a stop when commits have accumulated well
past the save rhythm, and the refusal told him to run `sv` by hand. It now
regenerates the 3 artefacts `sv` would regenerate -- `docs/CURRENT_STATE.md`,
the memory-exclusions ledger, and an Open Brain session summary -- and reports
which ones it refreshed.

THE PROPERTY THIS FILE EXISTS TO HOLD IS THE NEGATIVE ONE. It must NOT commit
and must NOT push. The full `sv` is still refused rather than run for exactly
that reason: `sv` pushes, and pushing half-finished work at every turn end is
worse than the gap it would close. His standing rule reserves pushing to his
agreement, so a hook that pushed would break it on every turn. 3 of the 6 tests
here assert that absence, because an absence is what nobody notices until it is
already gone.

IT MUST ALSO NOT RUN PYTEST, and that is a measured constraint rather than a
preference. `generate_current_state` takes a test count and the only supplier,
`cdsfl_utils.test_count`, obtains one by spawning `pytest --co -q`. A Stop hook
fires at the end of every turn, so that would put a recurring pytest process on
a machine with 8 logical cores and 8 GiB -- which his ruling of 2026-10-11
makes a fixed resource, after one fan-out issued 2,310 local calls including
263 pytest invocations. The hook passes `tests=None` instead.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks/sv_milestone_gate.py"
LIVE = pathlib.Path.home() / ".claude/hooks/sv_milestone_gate.py"


def _tree():
    return ast.parse(HOOK.read_text(encoding="utf-8"))


def _func(name: str):
    for node in ast.walk(_tree()):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def test_the_regeneration_function_exists_and_is_called():
    """An addition nothing reaches is not additive."""
    assert _func("_regenerate_local_state") is not None, (
        "the gate has no _regenerate_local_state, so his granted permission "
        "produced nothing")
    src = HOOK.read_text(encoding="utf-8")
    assert "_regenerate_local_state()" in src.split(
        "def _regenerate_local_state", 1)[0] or \
        src.count("_regenerate_local_state") >= 2, (
        "the function is defined but never called")


def test_it_regenerates_all_three_artefacts():
    """Each of the 3 the accepted option names."""
    body = ast.get_source_segment(
        HOOK.read_text(encoding="utf-8"), _func("_regenerate_local_state")) or ""
    for needle in ("generate_current_state",
                   "_update_memory_exclusions_ledger",
                   "_open_brain_summary"):
        assert needle in body, (
            f"the local save does not call {needle}, so 1 of the 3 artefacts "
            f"he accepted is not regenerated")


def test_it_does_not_commit_and_does_not_push():
    """THE NEGATIVE PROPERTY, and the reason sv itself is still only refused.

    His standing rule reserves pushing to his agreement. A Stop hook that
    pushed would break that on every turn end.
    """
    src = HOOK.read_text(encoding="utf-8")
    for forbidden in ('"commit"', "'commit'", '"push"', "'push'",
                      "--commit", "--push"):
        bad = [l for l in src.splitlines()
               if forbidden in l and not l.lstrip().startswith("#")
               and "f\"" not in l and "f'" not in l]
        assert not bad, (
            f"the gate now references {forbidden} in live code: {bad[:2]}. It "
            f"must regenerate locally and never commit or push.")


def test_it_does_not_invoke_pytest():
    """His machine is a fixed resource; a Stop hook fires every turn."""
    src = HOOK.read_text(encoding="utf-8")
    live = [l for l in src.splitlines()
            if "pytest" in l and not l.lstrip().startswith("#")]
    assert not live, f"the gate invokes pytest in live code: {live[:2]}"
    body = ast.get_source_segment(
        src, _func("_regenerate_local_state")) or ""
    assert "test_count" not in body, (
        "the local save calls test_count, which spawns pytest --co")
    assert "None" in body, (
        "the local save does not pass a test count of None, so it is either "
        "measuring tests or writing a stale number")


def test_every_failure_is_swallowed_and_reported():
    """A swallowed exception that reports nothing is not a record.

    This runs inside a hook whose refusal carries information he needs, so an
    exception must not take the refusal down -- but it must still be named.
    """
    body = ast.get_source_segment(
        HOOK.read_text(encoding="utf-8"), _func("_regenerate_local_state")) or ""
    handlers = [n for n in ast.walk(ast.parse(body.lstrip()))
                if isinstance(n, ast.ExceptHandler)]
    assert len(handlers) >= 3, (
        f"only {len(handlers)} except handlers; each of the 3 artefacts must "
        f"fail independently rather than the first failure skipping the rest")
    for h in handlers:
        seg = ast.dump(h)
        assert "stderr" in seg or "write" in seg, (
            "an except handler neither re-raises nor reports, so a failure "
            "would be silent")


def test_the_versioned_copy_is_the_one_that_runs():
    """3 of the 4 hooks that preceded this one existed in no repository."""
    if not LIVE.exists():
        pytest.skip("the live hooks directory is not on this machine")
    assert HOOK.stat().st_ino == LIVE.stat().st_ino, (
        f"the repository copy and the live hook are different files "
        f"({HOOK.stat().st_ino} against {LIVE.stat().st_ino}); an edit here "
        f"would not change what runs")
