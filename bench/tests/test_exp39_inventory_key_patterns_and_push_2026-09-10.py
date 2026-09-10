"""The exp39 branch inventory reported ANSWER KEYS: 0 over a branch carrying a key,
and reported `git push` as safe while `git push --dry-run` sent that branch.

PANEL ROUND 9, 2026-09-10. Two defects in scripts/exp39_branch_inventory_2026-09-10.py,
both in the machinery that produces the numbers the founder's disposition rests on.

  (1) KEY MARKER TOO NARROW. The script tested `"answer_key" in p`. This project
      already diagnosed and fixed that exact blindness in bench/vault_keys.sh on
      2026-09-06 -- "0 of 29 real keys matched the pattern" -- because the BR2 keys
      are `ft-NNN_KEY.json` and the exp55 pair are `*_KEY.md` / `*GROUND_TRUTH.json`.
      Four days later the inventory reintroduced it. Consequence is not a cosmetic
      undercount: `key_bearing_refs()` feeds `push_exposure()`, so a ref carrying a
      BR2 key is reported as carrying none, and `push_tags_sends_keys` prints False
      over a tag that would publish key material.

  (2) `plain_push_sends_keys` WAS HARDCODED False. It was asserted from the comment
      "`git push` with no args pushes the current branch only" -- true, and not an
      answer. `remote.origin.push` was read into the very same dict on the line
      above and then discarded before the verdict.

These tests are hermetic: each builds a throwaway repository with a real bare remote
whose contents are known in advance, so they assert on the SCRIPT'S BEHAVIOUR and not
on this machine's state. The sandbox the panel runs in has no .git at all, so a test
depending on the real repository could not run here and would prove nothing.

NO REF IS DELETED, CREATED OR PUSHED against any real remote by this file. Every
remote is a bare repository inside pytest's tmp_path.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "exp39_branch_inventory_2026-09-10.py"


def _load():
    spec = importlib.util.spec_from_file_location("exp39_inv", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


inv_mod = _load()


def _git(cwd, *args, check=True):
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout


def _build(tmp_path, keypath: str):
    """The fixture body, parameterised on the filename under test."""
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    _git(tmp_path, "init", "-q", "--bare", str(remote))
    _git(tmp_path, "clone", "-q", str(remote), str(work))
    _git(work, "config", "user.email", "t@t.t")
    _git(work, "config", "user.name", "t")
    (work / "a.txt").write_text("a\n")
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "main1")
    _git(work, "branch", "-M", "main")
    _git(work, "push", "-q", "origin", "main")
    _git(work, "checkout", "-qb", "exp39-experimental")
    f = work / keypath
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text('{"ground_truth_notes": "sentinel"}')
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "branch payload")
    _git(work, "tag", "exp39-experimental-pinned-2026-09-10")
    _git(work, "fetch", "-q", "origin")
    return work


@pytest.fixture
def fixture_repo(tmp_path):
    """main on a real bare remote; a LOCAL branch adding a BR2-style key; a tag on
    that branch. Exactly the shape exp39-experimental has, with a key name the old
    marker cannot see."""
    return _build(tmp_path, KEY)


KEY = "keys/ft-001_KEY.json"


# ---------------------------------------------------------------- defect (1)

def test_a_br2_style_key_on_the_branch_is_counted(fixture_repo):
    inv = inv_mod.inventory(repo=fixture_repo)
    assert KEY in inv["only_hist"], inv["only_hist"]
    assert inv["keys"] == [KEY], (
        f"a plaintext BR2 key unique to the branch was not counted as key "
        f"material: keys={inv['keys']}")


def test_the_tag_is_reported_as_carrying_the_key(fixture_repo):
    """The disposition turns on this. A tag is published by an EASIER command than
    a branch (`git push --tags` sends every tag), so a tag reported as carrying no
    key is the number most likely to license a wrong push."""
    px = inv_mod.inventory(repo=fixture_repo)["push_exposure"]
    assert "refs/tags/exp39-experimental-pinned-2026-09-10" in px["key_bearing_tags"], px
    assert px["push_tags_sends_keys"] is True, px


def test_the_old_marker_would_have_missed_this_key():
    """NON-VACUITY for defect (1). Reproduce the pre-fix test and prove it is blind,
    so this suite cannot pass against the defect it was written for."""
    assert "answer_key" not in KEY, "the old marker was not blind; this fix is unnecessary"
    assert inv_mod.is_key_path(KEY), "the corrected matcher must see what the old one could not"


def test_new_matcher_is_a_strict_superset_of_the_old():
    """THE ADDITIVE STANDARD, as a committed measurement. Widening a detector is only
    safe if it never stops matching something. Includes `answer_keys/x.json`, where
    the marker matches the DIRECTORY and no glob matches the basename -- a
    basename-only marker test would fail here."""
    corpus = [
        "bench/exp48_chemistry_answer_key.json", "answer_keys/x.json",
        "x/exp51_biology_answer_key.json", "keys/ft-001_KEY.json",
        "control_two_distinct_defects_KEY.md",
        "control_two_distinct_defects_GROUND_TRUTH.json",
        "bench/reference_runner_v2.py", "docs/Experiment 40 response.docx",
        "README.md", "a/b/monkey_business.py",
    ]
    old = {p for p in corpus if "answer_key" in p}
    new = {p for p in corpus if inv_mod.is_key_path(p)}
    assert old <= new, f"the new matcher LOST paths the old one caught: {old - new}"
    assert new - old == {
        "keys/ft-001_KEY.json", "control_two_distinct_defects_KEY.md",
        "control_two_distinct_defects_GROUND_TRUTH.json"}, new - old


def test_a_repo_with_no_key_material_reports_none(tmp_path):
    """CONTROL: the matcher must not simply always fire, which would be as useless
    as always missing. Identical fixture, built from the start with an innocuous
    filename.

    NOTE, and it is why this control had to be rebuilt rather than renamed: `git mv`
    followed by a commit does NOT clear the finding, and should not. The path is
    still carried by an earlier reachable commit, which is precisely the exposure
    this script measures -- the branch's own commit eecdb0f names the residual as
    "git-history recovery by deliberate archaeology". A control that passed after a
    rename would have been asserting that the script had gone blind."""
    work = _build(tmp_path, "keys/notes.json")
    inv = inv_mod.inventory(repo=work)
    assert "keys/notes.json" in inv["only_hist"], inv["only_hist"]
    assert inv["keys"] == [], inv["keys"]
    assert inv["push_exposure"]["push_tags_sends_keys"] is False


# ---------------------------------------------------------------- defect (2)

def test_plain_push_is_reported_true_when_a_wildcard_refspec_would_send_the_branch(
        fixture_repo):
    """The decisive case, and the one measured by hand on 2026-09-10:
    `git push --dry-run` printed " * [new branch] exp39-experimental -> ..." while
    the script printed False."""
    _git(fixture_repo, "config", "remote.origin.push", "refs/heads/*:refs/heads/*")
    dry = subprocess.run(["git", "push", "--dry-run"], cwd=str(fixture_repo),
                         capture_output=True, text=True)
    assert "exp39-experimental" in (dry.stdout + dry.stderr), (
        "git itself would not send the branch, so there is nothing to report:\n"
        + dry.stdout + dry.stderr)
    px = inv_mod.inventory(repo=fixture_repo)["push_exposure"]
    assert px["plain_push_sends_keys"] is True, (
        f"git push --dry-run sends the key-bearing branch, but the inventory "
        f"reports plain_push_sends_keys={px['plain_push_sends_keys']} "
        f"({px['plain_push_reason']})")


def test_plain_push_is_reported_true_when_push_default_is_current_on_the_branch(
        fixture_repo):
    """No refspec, but HEAD is the key-bearing branch and push.default=current
    pushes HEAD even with no upstream configured."""
    _git(fixture_repo, "config", "push.default", "current")
    px = inv_mod.inventory(repo=fixture_repo)["push_exposure"]
    assert px["plain_push_sends_keys"] is True, px["plain_push_reason"]


def test_plain_push_is_reported_false_under_simple_with_no_upstream(fixture_repo):
    """CONTROL, and the reason the original hardcoded False looked right. Under
    git's own default (`simple`) a branch with no upstream is not pushed -- the
    field must be able to say False, or it is as useless as the constant it
    replaced."""
    px = inv_mod.inventory(repo=fixture_repo)["push_exposure"]
    assert px["push_default"] == "(unset)"
    assert px["plain_push_sends_keys"] is False, px["plain_push_reason"]


def test_the_field_is_computed_not_a_literal():
    """NON-VACUITY for defect (2). The two tests above disagree on the same
    repository shape, which a hardcoded constant cannot do; this asserts the source
    no longer contains the literal that produced the wrong answer."""
    src = SCRIPT.read_text()
    assert '"plain_push_sends_keys": False' not in src, (
        "plain_push_sends_keys is still a hardcoded literal")
    assert "plain_push_reason" in src, "the reason must be reported, not a bare bool"


# ---------------------------------------------------------- no ref is harmed

def test_this_fix_deletes_no_ref():
    """THE PROHIBITION. Deleting a git ref is reserved to the founder in person."""
    # SCRIPT only. An earlier version of this test also scanned THIS file, which
    # contains every forbidden token below in its own literal list -- so it failed
    # against a perfectly clean script. A guard that cannot pass is not a guard.
    src = SCRIPT.read_text()
    forbidden = ["branch -D", "branch -d", "tag -d", "push --delete",
                 "gc --prune", "reflog expire", "filter-repo"]
    for f in forbidden:
        assert f not in src, f"ref-destroying operation present in the script: {f}"
    # NON-VACUITY: the scan must be capable of firing.
    assert any(f in src + "git branch -D x" for f in forbidden)
