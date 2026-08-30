"""One reviewer finishing must not unsandbox another that is still running.

MEASURED FAILURE, 2026-08-30. `_PANEL_CWD` was a module-level global, and the
confer dispatcher runs its reviewers concurrently in a ThreadPoolExecutor. Each
sets the cwd to its own throwaway worktree and clears it in a `finally`, so the
first to finish cleared it for the other:

    01:01:49  both worktrees created, cwd set twice
    01:30:34  fable finishes -> its finally sets the shared cwd to None
    01:41:49  cc2 times out and RETRIES with cwd None -- the CANONICAL repository,
              with Bash in its allowed tools

The reviewer caught it itself and no damage was done. CC1 had examined the same
log line earlier and cleared it as a false alarm, having verified the worktrees
were CREATED and never that the shared state survived a concurrent completion.
"""
import pathlib
import sys
import threading

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

from experiment_11_orchestrator import get_panel_cwd, set_panel_cwd  # noqa: E402


def test_one_threads_cleanup_cannot_clear_anothers_sandbox(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(); b.mkdir()
    started, a_cleared, seen = threading.Event(), threading.Event(), {}

    def first():
        set_panel_cwd(str(a))
        started.wait(5)
        set_panel_cwd(None)          # the `finally` that used to clear both
        a_cleared.set()

    def second():
        set_panel_cwd(str(b))
        started.set()
        a_cleared.wait(5)
        seen["after"] = get_panel_cwd()   # must STILL be b

    t1, t2 = threading.Thread(target=first), threading.Thread(target=second)
    t1.start(); t2.start(); t1.join(5); t2.join(5)

    assert seen.get("after") == str(b.resolve()), (
        f"a concurrent reviewer's cleanup changed this thread's sandbox to "
        f"{seen.get('after')!r}; with None that is the canonical repository")


def test_the_default_is_still_none_for_single_threaded_callers():
    def check(out):
        out["v"] = get_panel_cwd()
    out = {}
    t = threading.Thread(target=check, args=(out,)); t.start(); t.join(5)
    assert out["v"] is None, "a fresh thread inherited another thread's sandbox"


def test_setting_and_clearing_still_works_within_one_thread(tmp_path):
    d = tmp_path / "wt"; d.mkdir()
    set_panel_cwd(str(d))
    assert get_panel_cwd() == str(d.resolve())
    set_panel_cwd(None)
    assert get_panel_cwd() is None


def test_a_nonexistent_path_is_still_refused(tmp_path):
    import pytest
    with pytest.raises(NotADirectoryError):
        set_panel_cwd(str(tmp_path / "does_not_exist"))
