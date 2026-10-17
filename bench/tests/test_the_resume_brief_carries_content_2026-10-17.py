"""Task B17: the post-compaction notice delivers the work, not a reading list.

HIS QUESTION, 2026-10-16: *"If you can detect compaction mechanically, why
can't you also make rs run mechanically too after compaction?"*

TWO THIRDS WERE ALREADY MECHANICAL. The compaction hook already RUNS
`cdsfl_recover.py --record-restore`, and the task-boundary hook already returns
2 to refuse the stop so the recovery lands. The third that was not: a hook can
run a script, inject text and refuse to end a turn, but it CANNOT make the
assistant open the documents a notice names. On the compaction of 2026-10-16
the notice supplied 10 paths, the restore ran, and the session still spent
hours recovering -- a notice delivers information only if something reads it.

SO THE OPEN WORK IS INJECTED INLINE. The size was measured before the shape was
chosen: the full list is 654,237 characters, the open entries capped at 90 cost
2,009, capped at 120 cost 2,639, with their `ruled` state capped at 110 cost
2,828, and the identifiers alone cost 97. The 2,828 shape is used because the
`ruled` field is the one that separates work he has already decided from work
he has not -- the distinction whose absence left the zero-plant control
appearing as an open decision for 70 days.

THE LOGIC IS IN THE REPOSITORY and the hook is a shim, because a hook under
`~/.claude/` is unversioned and exists on one machine. A fix that lives only in
an unversioned file is one disk failure from never having existed.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "compaction_resume_brief_2026-10-17.py"
HOOK = pathlib.Path.home() / ".claude" / "hooks" / "compaction_watch.py"


def _mod():
    spec = importlib.util.spec_from_file_location("_brief", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _mod()


def test_the_script_exists_in_the_repository_not_only_in_the_hook():
    assert SCRIPT.is_file(), (
        "the brief lives only in an unversioned hook, which is one disk "
        "failure from never having existed")


def test_the_brief_names_every_open_entry():
    """THE POINT OF THE WHOLE ENTRY. A brief that omits an open item silently
    is worse than a path list, because it reads as complete."""
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as markers
    live = [e for e in markers.parse_entries() if e.state in M.LIVE_STATES]
    assert live, "no open entries; this guard would be vacuous"
    text = M.brief()
    missing = [e.ident for e in live if e.ident not in text]
    assert not missing, (
        f"{len(missing)} open entries are absent from the brief: {missing}")


def test_it_distinguishes_ruled_from_unruled():
    """`ruled` is the field whose absence left a decision he had already taken
    appearing in his queue for 70 days."""
    text = M.brief()
    assert "NOT RULED" in text or "ruled 20" in text, (
        "the brief does not carry the ruled state at all, so a question he is "
        "owed is indistinguishable from a decision he already gave")


def test_it_carries_a_resume_pointer_when_the_tracker_has_one():
    if not M.TRACKER.is_file():
        pytest.skip("the operational tracker is not in this checkout")
    assert M.resume_pointer(), (
        "the tracker is present but no resume pointer was found in it; the "
        "brief then names no starting point")
    assert "RESUME POINTER" in M.brief()


def test_it_stays_inside_its_budget():
    text = M.brief(budget=4000)
    assert len(text) <= 4000, f"the brief is {len(text)} characters"


def test_overflow_is_announced_and_the_identifiers_always_survive():
    """TRUNCATION MUST NEVER BE SILENT. Measured: the identifiers alone cost 97
    characters, so the fallback always fits."""
    text = M.brief(budget=900)
    assert len(text) <= 900, f"the budget was exceeded: {len(text)}"
    assert "OMITTED" in text, (
        "the brief was truncated without saying so, which makes a partial "
        "list read as a complete one")
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as markers
    live = [e for e in markers.parse_entries() if e.state in M.LIVE_STATES]
    named = [e.ident for e in live if e.ident in text]
    assert len(named) == len(live), (
        f"only {len(named)} of {len(live)} open identifiers survived "
        f"truncation; an omitted item must still be nameable")


def test_a_tighter_cap_shortens_rather_than_dropping_entries():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as markers
    live = [e for e in markers.parse_entries() if e.state in M.LIVE_STATES]
    tight, loose = M.brief(cap=40), M.brief(cap=160)
    assert len(tight) < len(loose)
    for e in live:
        assert e.ident in tight, f"{e.ident} was dropped by a tighter cap"


def test_the_script_runs_clean_and_refuses_an_unknown_flag():
    ok = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True,
                        text=True, cwd=str(REPO))
    assert ok.returncode == 0, ok.stderr
    assert ok.stdout.strip()
    bad = subprocess.run([sys.executable, str(SCRIPT), "--bogus"],
                         capture_output=True, text=True, cwd=str(REPO))
    assert bad.returncode != 0


@pytest.mark.skipif(not HOOK.is_file(), reason="the hook is not on this machine")
def test_the_hook_calls_the_repository_script():
    """AN ADDITION NOTHING CALLS IS NOT ADDITIVE. The hook is the only caller
    on the path that matters, so its reference is the wiring."""
    src = HOOK.read_text(encoding="utf-8", errors="replace")
    assert SCRIPT.name in src, (
        "the compaction hook does not call the brief, so the brief never "
        "reaches a post-compaction turn and the entry is unfixed")


@pytest.mark.skipif(not HOOK.is_file(), reason="the hook is not on this machine")
def test_the_hook_still_parses_and_degrades_rather_than_failing():
    """A hook that raises is far worse than a missed notice: it can block every
    prompt. The brief is therefore wrapped and falls back to the path list."""
    import ast
    src = HOOK.read_text(encoding="utf-8", errors="replace")
    ast.parse(src)
    i = src.index(SCRIPT.name)
    window = src[max(0, i - 1400):i + 1400]
    assert "except Exception" in window, (
        "the call to the brief is not guarded, so a failure there could fell "
        "the hook that carries the notice")
