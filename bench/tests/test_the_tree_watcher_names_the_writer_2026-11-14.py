"""A write to the tree during a suite run must be attributable to a test file.

★ ENTRY B192. On 2026-11-13, 2 documents were rewritten at 06:27 during a
04:10-to-07:30 suite run and **the writer was unidentifiable**. 4 separate
explanations were each tested and refuted. A clean-tree measurement is only
clean if every writer is accounted for, so an unattributable write means the
next clean run can be spoiled the same way with no warning.

★ WHAT WAS THERE BEFORE WAS A SOURCE-TEXT GUARD, NOT A WATCHER.
`test_tests_do_not_mutate_the_working_tree_2026-08-26.py` scans test FILES for
offending patterns -- 95 lines of text matching, which `execute-do-not-grep`
says asserts only that a module describes itself consistently. It cannot see a
write that arrives through a route no test file spells out, which is how the
06:27 writer escaped. B176 records that same guard being blind twice over.

★ THE WATCHER ATTRIBUTES BY TIME-SLICE. By the time a changed path is noticed
the writing process has usually exited and `lsof` on a closed file returns
nothing. What IS knowable is which test file was executing when the path
appeared, and that is what it records.

★ COST, MEASURED RATHER THAN GUESSED, which is why it is opt-in: `git status
--porcelain -uall` costs a mean of 0.1275 s in this repository, so 933 test
files is **118.9 s, about 0.0737 of a 1612 s board**; 1 snapshot per test across
roughly 15,400 tests would be **32.7 minutes** and is refused. `CDSFL_WATCH_TREE=1`
turns it on for the run that needs it.

EXECUTES the watcher in a child pytest run. It does not read the conftest's text.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
CONFTEST = REPO / "bench" / "tests" / "conftest.py"


def _child(args, env_extra=None, cwd=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, "-m", "pytest", *args, "-q", "--no-header"],
                          cwd=str(cwd or REPO), capture_output=True, text=True,
                          env=env, timeout=300)


def test_the_watcher_is_silent_when_it_is_off():
    """A normal board must gain 0 lines, or the cost is not opt-in at all."""
    r = _child(["bench/tests/test_frx_is_its_own_kind_2026-11-13.py"])
    assert "TREE WATCHER" not in r.stdout, (
        "the watcher reported without being asked; every board would pay the "
        "118.9 s and the 7.37 per cent")


def test_the_watcher_reports_zero_on_a_clean_run():
    r = _child(["bench/tests/test_frx_is_its_own_kind_2026-11-13.py"],
               {"CDSFL_WATCH_TREE": "1"})
    assert "TREE WATCHER" in r.stdout, r.stdout[-1500:]
    assert "0 paths appeared" in r.stdout, r.stdout[-1500:]


def test_the_watcher_NAMES_the_test_file_that_wrote(tmp_path):
    """★ THE LOAD-BEARING TEST. A watcher that can only ever say 0 is useless;
    this proves it can say 1 and say WHO.

    The probe writes into a THROWAWAY git repository, never this one, because a
    test that dirties the real tree to prove a watcher sees dirty trees is the
    fault it is testing for.
    """
    repo = tmp_path / "probe_repo"
    tests = repo / "bench" / "tests"
    tests.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=str(repo), check=True)
    subprocess.run(["git", "config", "user.email", "probe@example.invalid"],
                   cwd=str(repo), check=True)
    subprocess.run(["git", "config", "user.name", "probe"], cwd=str(repo), check=True)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=str(repo), check=True)

    # the watcher half of the real conftest, copied as the subject under test
    src = CONFTEST.read_text(encoding="utf-8")
    start = src.index("_WATCH_TREE = os.environ.get")
    end = src.index("@pytest.hookimpl(hookwrapper=True, tryfirst=True)", start)
    watcher_src = src[start:end]
    assert "_watch_checkpoint" in watcher_src, "the watcher block was not located"

    (tests / "conftest.py").write_text(textwrap.dedent('''
        import json, os, pathlib, subprocess
        import pytest
        _REPO_FOR_WATCH = pathlib.Path(__file__).resolve().parent.parent.parent
        ''') + watcher_src + textwrap.dedent('''

        @pytest.hookimpl(hookwrapper=True, tryfirst=True)
        def pytest_runtest_protocol(item, nextitem):
            _watch_checkpoint(item.nodeid)
            yield

        def pytest_terminal_summary(terminalreporter, exitstatus, config):
            if _WATCH_TREE:
                out = _REPO_FOR_WATCH / "watch_events.json"
                out.write_text(json.dumps(_watch_state["events"]), encoding="utf-8")
        '''), encoding="utf-8")

    (tests / "test_aaa_quiet.py").write_text(
        "def test_quiet():\n    assert True\n", encoding="utf-8")
    (tests / "test_bbb_writes.py").write_text(
        "import pathlib\n"
        "def test_writes():\n"
        "    p = pathlib.Path(__file__).resolve().parent.parent.parent / 'written_by_a_test.txt'\n"
        "    p.write_text('on purpose\\n', encoding='utf-8')\n", encoding="utf-8")
    (tests / "test_ccc_quiet.py").write_text(
        "def test_quiet2():\n    assert True\n", encoding="utf-8")

    r = _child(["bench/tests"], {"CDSFL_WATCH_TREE": "1"}, cwd=repo)
    assert r.returncode == 0, r.stdout[-2000:]
    ledger = repo / "watch_events.json"
    assert ledger.is_file(), f"the watcher wrote no ledger. stdout:\n{r.stdout[-1500:]}"
    events = json.loads(ledger.read_text(encoding="utf-8"))
    paths = {e["path"] for e in events}
    assert "written_by_a_test.txt" in paths, (
        f"the watcher did not see the write. events: {events}")
    attributed = {e["path"]: e["appeared_while_running"] for e in events}
    who = attributed["written_by_a_test.txt"]
    assert who and "test_bbb_writes" in who, (
        f"the write was attributed to {who!r} rather than to the file that made "
        f"it; an attribution that names the wrong test is worse than none")


def test_the_watcher_cannot_fail_a_run():
    """A watcher that breaks a board is worse than no watcher. Driven by
    pointing its root at a directory that is not a git repository at all."""
    r = _child(["bench/tests/test_frx_is_its_own_kind_2026-11-13.py"],
               {"CDSFL_WATCH_TREE": "1", "GIT_DIR": "/nonexistent-9fa3"})
    assert r.returncode == 0, (
        "the watcher failed the run when git was unusable:\n" + r.stdout[-1500:])
