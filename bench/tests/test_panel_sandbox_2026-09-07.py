"""Panel seats work in a copy of the repo, not the live one. Founder ruling 35.

THE HISTORY MATTERS, because the first attempt at this failed silently and said it
had worked.

`--allowedTools` already withholds Write and Edit and its comment says "No file
modification". A seat wrote to the canonical tree anyway, through Bash, which no
tool list can restrain — so confinement has to be POSITIONAL, not permissional.

The cwd machinery (`set_panel_cwd`, fail-closed on a bad path) had existed since
August and was never called. Runway 0C.9 carried it at HIGH, describing the
confinement half as unbuilt when it was in fact BUILT AND UNWIRED.

The first wiring then failed for a reason worth pinning: `_PANEL_CWD_TLS` is a
`threading.local()` and the dispatcher runs seats in a ThreadPoolExecutor, so a
value set on the MAIN thread is invisible to every worker. Main logged "seats
confined to a copy"; every worker passed cwd=None; both seats ran in the live repo;
one created a file there. cc2 caught it by running `pwd` and refusing the test.

And the detector meant to backstop all this was blind in the same direction: it
fingerprinted `git ls-files`, which lists TRACKED files only, so a NEW UNTRACKED
file — the most likely form of write — was invisible and it reported "unchanged".
"""
from __future__ import annotations

import concurrent.futures
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import panel_sandbox as ps  # noqa: E402


def test_the_sandbox_is_not_the_repo_and_carries_no_git(tmp_path):
    sb = ps.build(REPO)
    try:
        assert sb.resolve() != REPO.resolve()
        assert not (sb / ".git").exists(), "a repository inside the sandbox is a way back out"
        assert (sb / "bench" / "reference_runner_v3.py").is_file(), "the copy must be usable"
    finally:
        ps.teardown(sb)


def test_a_write_inside_the_sandbox_does_not_reach_the_canonical_tree():
    before = ps.fingerprint(REPO)
    sb = ps.build(REPO)
    try:
        (sb / "SEAT_WAS_HERE.txt").write_text("seat: test")
        (sb / "bench" / "reference_runner_v3.py").write_text("CLOBBERED")
        touched = ps.canonical_was_touched(before, REPO)
        assert not touched, f"the canonical tree changed during a sandboxed run: {touched}"
        assert not (REPO / "SEAT_WAS_HERE.txt").exists()
    finally:
        ps.teardown(sb)


def test_the_detector_sees_a_CREATED_file_not_only_a_modified_one(tmp_path):
    """THE BLIND SPOT. `git ls-files` alone lists tracked files, so a brand-new file
    was invisible and the tree was reported unchanged — on the very run meant to
    prove containment."""
    repo = tmp_path / "r"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=str(repo))
    (repo / "tracked.txt").write_text("x")
    subprocess.run(["git", "add", "-A"], cwd=str(repo))
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "i"], cwd=str(repo))
    before = ps.fingerprint(repo)
    (repo / "SEAT_WAS_HERE.txt").write_text("seat: intruder")     # untracked, new
    touched = ps.canonical_was_touched(before, repo)
    assert "SEAT_WAS_HERE.txt" in touched, (
        "a newly CREATED untracked file is invisible to the detector again")
    assert touched["SEAT_WAS_HERE.txt"] == "CREATED"


def test_the_detector_also_sees_modified_and_deleted(tmp_path):
    repo = tmp_path / "r2"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=str(repo))
    (repo / "a.txt").write_text("a")
    (repo / "b.txt").write_text("b")
    subprocess.run(["git", "add", "-A"], cwd=str(repo))
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "i"], cwd=str(repo))
    before = ps.fingerprint(repo)
    (repo / "a.txt").write_text("CHANGED")
    (repo / "b.txt").unlink()
    touched = ps.canonical_was_touched(before, repo)
    assert touched.get("a.txt") == "modified"
    assert touched.get("b.txt") == "deleted"


def test_a_thread_local_set_on_the_main_thread_does_not_reach_a_pool_worker():
    """THE BUG THAT MADE THE FIRST WIRING FAIL SILENTLY. Pinned so nobody sets the
    panel cwd from main again and believes the log line."""
    from experiment_11_orchestrator import _get_panel_cwd_raw, set_panel_cwd
    import tempfile
    d = tempfile.mkdtemp()
    set_panel_cwd(d)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        seen = list(pool.map(lambda _: _get_panel_cwd_raw(), range(2)))
    set_panel_cwd(None)
    assert seen == [None, None], (
        "thread-locals now propagate to pool workers; the per-worker set in "
        "dispatch() may be redundant, but verify before removing it")


def test_setting_it_inside_the_worker_does_reach_the_subprocess_call():
    from experiment_11_orchestrator import _get_panel_cwd_raw, set_panel_cwd
    import tempfile
    d = tempfile.mkdtemp()
    want = str(Path(d).resolve())

    def worker(_):
        set_panel_cwd(d)
        return _get_panel_cwd_raw()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        seen = list(pool.map(worker, range(2)))
    set_panel_cwd(None)
    assert all(v == want for v in seen), f"workers saw {seen}, wanted {want}"


def test_the_dispatcher_sets_the_cwd_per_worker_not_on_main():
    """Guard the wiring itself: if the set moves back out of dispatch(), the
    containment silently stops working and the log line still says it worked."""
    src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text()
    body = src[src.index("def dispatch("):src.index("def main(")]
    assert "set_panel_cwd(_PANEL_SANDBOX_CWD)" in body, (
        "dispatch() no longer sets the sandbox cwd on its own thread")
