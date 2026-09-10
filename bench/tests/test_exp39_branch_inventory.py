"""Known-answer control for scripts/exp39_branch_inventory_2026-09-10.py (round 9, second seat).

Complements test_exp39_inventory_hardening_2026-09-10.py (the other seat's
suite) with the DELETED-THEN-RE-ADDED variant of the cut-off defect: a path
that main held ONLY deep in history and then deleted, so it is absent from
every recent TREE, and the branch re-adds it. A bounded scan of main cannot
see the old add, so it reports the path as "exists nowhere else" -- the exact
shape that would have put a wrong inventory line in front of the founder.

Fixture answer is fixed BEFORE measurement (2026-09-09 vacuous-test ruling):

  main:   c1 adds deep_shared.txt ; c2 DELETES it ; c3..c5 churn
  branch: adds branch_only.txt, 'spaced dir/with space.txt', re-adds deep_shared.txt

  correct unique set  = {branch_only.txt, spaced dir/with space.txt}
  capped-scan (cap=3) = additionally claims deep_shared.txt  (the defect)
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess

import pytest

_SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "exp39_branch_inventory_2026-09-10.py"
_spec = importlib.util.spec_from_file_location("exp39_inventory_ka", _SCRIPT)
inv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inv)

_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
        "GIT_AUTHOR_DATE": "2026-01-01T00:00:00",
        "GIT_COMMITTER_DATE": "2026-01-01T00:00:00",
        "PATH": "/usr/bin:/bin"}


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True,
                   capture_output=True, env=_ENV)


@pytest.fixture()
def ka_repo(tmp_path):
    repo = tmp_path / "ka_fixture"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "deep_shared.txt").write_text("added deep in main history\n")
    _git(repo, "add", "."); _git(repo, "commit", "-qm", "c1 add deep_shared")
    _git(repo, "rm", "-q", "deep_shared.txt")
    _git(repo, "commit", "-qm", "c2 delete deep_shared")
    for i in (3, 4, 5):
        (repo / f"churn{i}.txt").write_text(f"{i}\n")
        _git(repo, "add", "."); _git(repo, "commit", "-qm", f"c{i} churn")
    _git(repo, "checkout", "-qb", "exp-fixture")
    (repo / "branch_only.txt").write_text("unique to branch\n")
    sd = repo / "spaced dir"; sd.mkdir()
    (sd / "with space.txt").write_text("path with spaces\n")
    (repo / "deep_shared.txt").write_text("branch re-adds the deep path\n")
    _git(repo, "add", "."); _git(repo, "commit", "-qm", "b1 branch adds")
    _git(repo, "checkout", "-q", "main")
    return repo


EXPECTED_UNIQUE = ["branch_only.txt", "spaced dir/with space.txt"]


def _unique(repo, cap=None):
    unreachable = inv.unreachable_commits("exp-fixture", "main", repo)
    hist = set()
    for c in unreachable:
        hist |= inv.tree_paths(c, repo)
    main_hist = (inv.history_paths("main", repo) if cap is None
                 else inv.history_paths_capped("main", cap, repo))
    return sorted(hist - main_hist)


def test_full_history_returns_exactly_the_known_answer(ka_repo):
    """A deleted-then-re-added path must NOT be reported unique; the spaced
    path must survive whole; nothing else appears."""
    assert _unique(ka_repo) == EXPECTED_UNIQUE


def test_capped_scan_wrongly_claims_the_deleted_path(ka_repo):
    """RED-CONTROL: the retained defective method (cap=3, analogue of the old
    [:400]) must still manufacture deep_shared.txt. If this fails, the fixture
    has stopped discriminating and the test above proves nothing."""
    got = _unique(ka_repo, cap=3)
    assert "deep_shared.txt" in got
    assert set(EXPECTED_UNIQUE) <= set(got)


def test_history_paths_sees_the_deleted_path_in_no_tree(ka_repo):
    """The core mechanism: deep_shared.txt is in NO tree of main's 3 most
    recent commits, yet full history_paths finds it."""
    recent = set()
    for c in inv.unreachable_commits("main", "main~3", ka_repo):
        recent |= inv.tree_paths(c, ka_repo)
    assert "deep_shared.txt" not in inv.tree_paths("main", ka_repo)
    assert "deep_shared.txt" in inv.history_paths("main", ka_repo)
