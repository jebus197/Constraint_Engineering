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


# --------------------------------------------------------------------------
# The containment fix CREATED a credential exposure. These pin the repair.
# --------------------------------------------------------------------------

def test_the_sandbox_does_not_carry_the_credentials():
    """Confining a seat to a copy is worthless if the copy holds the keys.

    Measured on the first working sandbox: `.env` arrived readable, 1264 bytes,
    declaring 10 live API keys. A seat has shell access -- that is precisely why
    positional confinement was needed -- so it could simply `cat` it."""
    sb = ps.build(REPO)
    try:
        assert not (sb / ".env").exists(), "the seat's copy still holds .env"
        assert ps._surviving_secrets(sb) == [], (
            f"credential-bearing files survived: {ps._surviving_secrets(sb)}")
        assert (sb / "bench" / "reference_runner_v3.py").is_file(), (
            "the scrub must not break the copy it is protecting")
    finally:
        ps.teardown(sb)


def test_an_example_env_is_kept_because_it_holds_names_not_values():
    sb = ps.build(REPO)
    try:
        if (REPO / ".env.example").exists():
            assert (sb / ".env.example").exists(), (
                "the scrub removed a values-free example file for no gain")
    finally:
        ps.teardown(sb)


def test_the_scrub_is_verified_not_assumed(tmp_path, monkeypatch):
    """A scrub that silently missed a file would leave the sandbox looking safe
    while it is not -- worse than no scrub, because it would be trusted. build()
    re-scans and raises."""
    fake = tmp_path / "repo"
    (fake / "sub").mkdir(parents=True)
    (fake / ".env").write_text("export OPENAI_API_KEY=sk-live-should-not-travel")
    (fake / "sub" / "deep.pem").write_text("-----BEGIN PRIVATE KEY-----")
    (fake / "keep.py").write_text("x = 1")
    sb = ps.build(fake)
    try:
        assert not (sb / ".env").exists()
        assert not (sb / "sub" / "deep.pem").exists(), "nested secrets must go too"
        assert (sb / "keep.py").is_file()
    finally:
        ps.teardown(sb)

    # And the verification itself fires when the scrub is defeated.
    monkeypatch.setattr(ps, "_scrub_secrets", lambda dest: 0)
    with pytest.raises(RuntimeError, match="credential-bearing"):
        ps.build(fake)


def test_secret_ignore_keeps_the_existing_exclusions_and_adds_credentials(tmp_path):
    """EXECUTED through a real copytree, not asserted about. The 5 other places
    in bench/ that copy the repo passed an exclusion list about SIZE and NOISE
    ('.git', '__pycache__', '*.pyc', 'logs') that said nothing about secrets, so
    every one of them materialised `.env` into TMPDIR."""
    import shutil
    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / ".git").mkdir()
    (src / ".git" / "HEAD").write_text("ref: refs/heads/main")
    (src / ".env").write_text("export OPENAI_API_KEY=sk-live")
    (src / ".env.example").write_text("OPENAI_API_KEY=")
    (src / "sub" / "deep.pem").write_text("-----BEGIN PRIVATE KEY-----")
    (src / "keep.py").write_text("x = 1")
    (src / "junk.pyc").write_bytes(b"\x00")

    dst = tmp_path / "dst"
    shutil.copytree(src, dst, symlinks=True,
                    ignore=ps.secret_ignore(".git", "__pycache__", "*.pyc", "logs"))

    assert not (dst / ".env").exists(), "the credential file still travels"
    assert not (dst / "sub" / "deep.pem").exists(), "nested secrets still travel"
    assert not (dst / ".git").exists(), "an existing exclusion was lost"
    assert not (dst / "junk.pyc").exists(), "an existing exclusion was lost"
    assert (dst / "keep.py").is_file(), "the copy lost real content"
    assert (dst / ".env.example").is_file(), "a values-free example was dropped"


def test_no_repo_copy_in_bench_still_uses_the_secret_blind_exclusion_list():
    """WIRING GUARD, deliberately structural. The behaviour is executed above;
    this stops the old pattern being pasted back into a new copy site, which is
    how the same leak reached 6 places."""
    import re
    offenders = []
    for path in (REPO / "bench").rglob("*.py"):
        if "/tests/" in str(path) or "/logs/" in str(path):
            continue
        text = path.read_text(errors="replace")
        for m in re.finditer(r"ignore_patterns\(([^)]*)\)", text, re.S):
            args = m.group(1)
            if '".git"' in args and "secret_ignore" not in text[max(0, m.start() - 200):m.start()]:
                # panel_sandbox's own fallback is followed by _scrub_secrets +
                # verification, so it is covered by construction.
                if path.name != "panel_sandbox.py":
                    offenders.append(f"{path.relative_to(REPO)}:{text[:m.start()].count(chr(10)) + 1}")
    assert not offenders, (
        "these repo copies exclude .git but not credentials: " + ", ".join(offenders))


# --------------------------------------------------------------------------
# The falsifier overlay: built 3x per finding, so what it carries costs 3x.
# --------------------------------------------------------------------------

def test_the_falsifier_overlay_does_not_carry_the_log_archive():
    """`bench/logs` is 432 MB of the repo's 689 MB and 7108 of its 15511 files,
    and the overlay is built THREE times per finding -- baseline, tripwire,
    corrected. Those are separate clones on purpose, so a falsifier writing in one
    stage cannot contaminate the next; the isolation is worth keeping, carrying
    the archive into it three times is not. Safe by evidence: of 99 archived
    falsifiers carrying code, 0 reference a logs path, Wilson [0.00%, 3.74%]."""
    import shutil as _sh
    import subprocess as _sp
    rrv3 = __import__("reference_runner_v3")
    ov = rrv3._build_discrimination_overlay(REPO, "bench/panel_sandbox.py", "# probe\n")
    try:
        assert (ov / "bench" / "logs").is_dir(), (
            "the directory must still EXIST, so a falsifier that only checks the "
            "path behaves as before")
        assert not any((ov / "bench" / "logs").iterdir()), "the archive was cloned"
        assert not (ov / ".git").exists(), "git history reached the overlay"
        assert not (ov / ".env").exists(), "credentials reached the overlay"
        assert (ov / "bench" / "reference_runner_v3.py").is_file(), "overlay unusable"
        assert (ov / "bench" / "panel_sandbox.py").read_text().strip() == "# probe", (
            "the whole point of the overlay -- replacing one file -- broke")
    finally:
        _sp.run(["chflags", "-R", "nouchg,noschg", str(ov.parent)], capture_output=True)
        _sh.rmtree(ov.parent, ignore_errors=True)
