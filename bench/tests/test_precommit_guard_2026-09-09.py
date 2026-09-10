"""The pre-commit guard must actually REFUSE a commit, proven by committing.

Written 2026-09-09. This file EXECUTES `hooks/pre-commit` inside a throwaway git
repository and checks what `git commit` does, per `execute-do-not-grep`: asserting
on the hook's source text would prove only that the hook describes itself
consistently, which is exactly the fault that let commit 57d5a0e reach HEAD with
the suite red.

Every test here builds a real repository, installs the real hook file, and runs
real git. The guard files inside the scratch repo are stubs whose pass or fail is
under the test's control, because the point under test is the HOOK'S CONTROL FLOW,
not the content of the 4 production guards -- those have their own tests.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "pre-commit"

def _guards_from_the_hook() -> list[str]:
    """Read the guard list OUT OF THE HOOK rather than restating it here.

    FOUND ON THE SECOND FFAFP PASS, 2026-09-09. The first version hardcoded the
    same 4 paths the hook hardcodes, so editing the hook's list left this file
    green and the 2 lists could drift apart silently. Two representations of one
    truth with no comparator is the shape `execute-do-not-grep` names, and it had
    been introduced by the fix for another instance of it.
    """
    hook = REPO / "hooks" / "pre-commit"
    text = hook.read_text()
    marker = 'GUARDS="'
    if marker not in text:
        # FOUND ON THE THIRD FFAFP PASS. The first version indexed [1] straight
        # after split() and raised IndexError if the block were ever renamed --
        # failing obscurely instead of saying what was wrong, which is the third
        # instance of that class found today.
        raise AssertionError(
            f"{hook} carries no {marker!r} block, so the guard list cannot be read. "
            f"If the hook was restructured, update this parser deliberately.")
    block = text.split(marker, 1)[1].split('"', 1)[0]
    return [ln.strip() for ln in block.splitlines() if ln.strip()]


GUARDS = _guards_from_the_hook()

PASSING = "def test_ok():\n    assert True\n"
FAILING = "def test_broken():\n    assert False, 'deliberately red'\n"


def _git(*args, cwd, check=True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          check=check, timeout=120)


def _scratch(tmp_path: Path, guard_body: str, omit: list[str] | None = None) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git("init", "-q", cwd=root)
    _git("config", "user.email", "t@example.invalid", cwd=root)
    _git("config", "user.name", "test", cwd=root)
    (root / "hooks").mkdir()
    shutil.copy2(HOOK, root / "hooks" / "pre-commit")
    os.chmod(root / "hooks" / "pre-commit", 0o755)
    _git("config", "core.hooksPath", "hooks", cwd=root)
    for rel in GUARDS:
        if omit and rel in omit:
            continue
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(guard_body)
    (root / "thing.txt").write_text("content\n")
    _git("add", "-A", cwd=root)
    return root


def _commit(root: Path, extra=()):
    return subprocess.run(["git", "commit", *extra, "-m", "attempt"],
                          cwd=root, capture_output=True, text=True, timeout=180)


# --- The two directions that matter. -----------------------------------------

def test_a_green_tree_commits(tmp_path):
    root = _scratch(tmp_path, PASSING)
    r = _commit(root)
    assert r.returncode == 0, f"a green tree must commit. stderr:\n{r.stderr}"
    assert _git("log", "--oneline", cwd=root).stdout.strip()


def test_a_red_tree_is_REFUSED(tmp_path):
    """The whole point. If this passes vacuously the guard is theatre."""
    root = _scratch(tmp_path, FAILING)
    r = _commit(root)
    assert r.returncode != 0, "a red tree MUST NOT commit"
    assert "REFUSED" in r.stderr, f"the refusal must say so. stderr:\n{r.stderr}"
    log = _git("log", "--oneline", cwd=root, check=False)
    assert not log.stdout.strip(), "nothing may have been committed"


# --- Fail-closed, because a guard that cannot fail is not a guard. -----------

def test_a_missing_guard_file_refuses_rather_than_passing(tmp_path):
    root = _scratch(tmp_path, PASSING, omit=[GUARDS[0]])
    r = _commit(root)
    assert r.returncode != 0, "an absent check must not read as a passing check"
    assert "missing" in r.stderr.lower()


def test_no_python_refuses_rather_than_passing(tmp_path):
    """An infrastructure fault must block, not wave the commit through.

    CORRECTED 2026-09-09 by mutation testing, which is the only reason the fault
    was visible. The first version set PATH to git's own directory, reasoning that
    git must stay reachable. On this machine git is /opt/homebrew/bin/git and
    python3 is /opt/homebrew/bin/python3 -- THE SAME DIRECTORY -- so the
    restriction never removed python3 at all. The test passed because the hook
    refused for an unrelated reason, and it survived deleting the very check it
    claimed to guard. A test that cannot fail in the direction it exists to check
    is the fault this project names as "a guard that cannot fail is not a guard".

    The fix is a PATH containing exactly 1 entry: a scratch directory holding a
    symlink to git and nothing else. Then python3 is genuinely absent, and the
    assertion is on the hook's SPECIFIC message rather than on a substring both
    code paths happen to produce.
    """
    root = _scratch(tmp_path, PASSING)
    only_git = tmp_path / "only-git"
    only_git.mkdir()
    (only_git / "git").symlink_to(shutil.which("git"))
    assert shutil.which("python3", path=str(only_git)) is None, (
        "the isolation must actually remove python3, or this test proves nothing")
    env = dict(os.environ, PATH=str(only_git))
    r = subprocess.run(["git", "commit", "-m", "attempt"], cwd=root, env=env,
                       capture_output=True, text=True, timeout=180)
    assert r.returncode != 0, "no python3 must refuse"
    assert "python3 not on PATH" in r.stderr, (
        "the hook must name the specific cause, not merely fail somewhere. "
        f"stderr:\n{r.stderr}")


# --- The escape hatch is deliberate and must keep working. -------------------

def test_no_verify_bypasses_deliberately(tmp_path):
    root = _scratch(tmp_path, FAILING)
    r = _commit(root, extra=("--no-verify",))
    assert r.returncode == 0, "the documented escape hatch must work"


# --- Mutation guard on the test itself. --------------------------------------

def test_the_failing_stub_really_fails_under_pytest(tmp_path):
    """If the stub silently passed, test_a_red_tree_is_REFUSED would be vacuous."""
    f = tmp_path / "stub_test.py"
    f.write_text(FAILING)
    r = subprocess.run(["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", str(f)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode != 0, "the failing stub must actually be red"


def test_the_real_hook_is_executable_and_is_the_file_under_test():
    assert HOOK.is_file(), "hooks/pre-commit must exist"
    assert os.access(HOOK, os.X_OK), "hooks/pre-commit must be executable or git ignores it"


# --- The installer, executed rather than described. --------------------------

def _load_onboard():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cdsfl_onboard_under_test", REPO / "scripts" / "cdsfl_onboard.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_wire_git_hooks_sets_an_unset_hookspath(tmp_path):
    """A fresh clone has no core.hooksPath, so it has no guard until this runs."""
    onb = _load_onboard()
    root = tmp_path / "fresh"
    root.mkdir()
    _git("init", "-q", cwd=root)
    (root / "hooks").mkdir()
    shutil.copy2(HOOK, root / "hooks" / "pre-commit")
    before = _git("config", "--get", "core.hooksPath", cwd=root, check=False).stdout.strip()
    assert before == "", "a fresh repository must start with it unset"
    assert onb.wire_git_hooks(root) is True
    after = _git("config", "--get", "core.hooksPath", cwd=root).stdout.strip()
    assert after == "hooks", f"must be set to hooks, got {after!r}"


def test_wire_git_hooks_restores_the_executable_bit(tmp_path):
    """git silently ignores a non-executable hook, which is a guard that cannot fire."""
    onb = _load_onboard()
    root = tmp_path / "fresh2"
    root.mkdir()
    _git("init", "-q", cwd=root)
    (root / "hooks").mkdir()
    dest = root / "hooks" / "pre-commit"
    shutil.copy2(HOOK, dest)
    os.chmod(dest, 0o644)
    assert not os.access(dest, os.X_OK)
    assert onb.wire_git_hooks(root) is True
    assert os.access(dest, os.X_OK), "the hook must be made executable"


def test_wire_git_hooks_reports_failure_when_the_hook_is_absent(tmp_path):
    onb = _load_onboard()
    root = tmp_path / "fresh3"
    root.mkdir()
    _git("init", "-q", cwd=root)
    (root / "hooks").mkdir()
    assert onb.wire_git_hooks(root) is False, "an absent hook must not report success"


def test_the_live_repository_is_actually_wired():
    """The claim that matters on a working machine, checked rather than assumed.

    CORRECTED 2026-09-09 by FFAFP pass 6, which ran the whole suite inside a fresh
    clone. This test asserted a property of the DEVELOPER'S environment, so it
    failed in the clone -- correctly, since a fresh clone genuinely is unguarded
    until onboarding runs, but uselessly, because it made an unavoidable condition
    look like a defect. A fresh clone is now detected and skipped WITH THE REASON
    STATED, which is the true fact rather than a silenced one.

    CORRECTED AGAIN 2026-09-10, task A2. THAT SKIP COULD NEVER FIRE. It asked
    whether `git config --get user.email` was empty, and `--get` searches local,
    then global, then system. `git clone` inherits the machine's global identity,
    so in the fresh clone at /tmp/ce_fresh the command returned
    `jebus.2504@gmail.com` and the branch was unreachable on any machine with a
    git identity -- which is every machine that can clone and commit. The fix for
    a fresh-clone failure was itself an addition nothing reached, the exact shape
    the additive standard's symmetric half names.

    THE DISCRIMINATOR IS NOW A MARKER ONBOARDING WRITES, `cdsfl.onboarded` in
    `--local` config, because the 2 states have opposite remedies. Never
    onboarded is "run 1 command"; onboarded and then unwired is "the guard was
    turned off", and that must stay RED. `--local` config is not carried by a
    clone and is not removed by unsetting `core.hooksPath`, so it separates them.
    """
    got = _git("config", "--get", "core.hooksPath", cwd=REPO, check=False).stdout.strip()
    if not got:
        stamp = _git("config", "--local", "--get", "cdsfl.onboarded",
                     cwd=REPO, check=False).stdout.strip()
        if not stamp:
            pytest.skip(
                "this clone has never been onboarded: core.hooksPath is unset and "
                "cdsfl.onboarded carries no stamp. A fresh clone IS unguarded until "
                "onboarding runs; that is expected, not a defect. Fix it with: "
                "python3 scripts/cdsfl_onboard.py")
    assert got == "hooks", (
        f"core.hooksPath is {got!r}, so commits here are unguarded -- and this "
        f"clone HAS been onboarded, so the guard was removed after setup rather "
        f"than never installed")


# --- The versioned hooks must not rot away from the ones that actually run. ---

LIVE_HOOKS = Path.home() / ".claude" / "hooks"


def test_the_guard_list_was_read_from_the_hook_and_is_not_empty():
    """If the parser silently returned [], every commit test above would be
    vacuous: pytest with no arguments collects the whole suite or nothing."""
    assert len(GUARDS) >= 4, f"parsed {GUARDS!r} out of hooks/pre-commit"
    for g in GUARDS:
        assert g.startswith("bench/tests/"), g
        assert (REPO / g).is_file(), f"the hook names a guard that does not exist: {g}"


@pytest.mark.parametrize("name", ["mc_commands.py", "prompt_clock.py",
                                  "compaction_watch.py", "ffafp_audit.py",
                                  "task_list_pulse.py"])
def test_the_versioned_hook_matches_the_one_that_actually_runs(name):
    """FOUND ON THE SECOND FFAFP PASS, 2026-09-09.

    The first pass copied 3 unversioned hooks into the repository, which was
    right: they had existed only under the home directory and were a single
    point of failure. But nothing then compared the 2 copies. The live copy is
    what `~/.claude/settings.json` executes; the repository copy is what survives
    a machine loss. With no comparator the repository copy rots into a
    comforting fiction -- a backup that no longer matches what runs -- which is
    the 'addition nothing reaches' half of the additive standard, introduced by
    the fix for an instance of that same standard.
    """
    live = LIVE_HOOKS / name
    versioned = REPO / "hooks" / name
    assert versioned.is_file(), f"hooks/{name} is missing from the repository"
    if not live.is_file():
        pytest.skip(f"{name} is not installed under ~/.claude/hooks on this machine")
    assert versioned.read_bytes() == live.read_bytes(), (
        f"hooks/{name} has DRIFTED from ~/.claude/hooks/{name}. The live copy is "
        f"what runs; the versioned copy is what survives. Reconcile them, and note "
        f"which direction is correct before copying either way."
    )


def test_a_commit_is_refused_in_a_clone_of_this_actual_repository(tmp_path):
    """FOUND ON THE THIRD FFAFP PASS, 2026-09-09.

    Every other refusal test builds a synthetic repository with stub guards, so
    all of them together prove only that the hook's CONTROL FLOW works. None
    proves that this repository's REAL guards, run by this repository's real
    hook, refuse a real breakage. The live test above checks core.hooksPath and
    stops there.

    A clone is used rather than the working repository because a test must not
    create commits in the tree it is run from.
    """
    clone = tmp_path / "clone"
    r = subprocess.run(["git", "clone", "-q", "--no-hardlinks", "--depth", "1",
                        str(REPO), str(clone)], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        pytest.skip(f"could not clone the repository: {r.stderr[:200]}")
    _git("config", "user.email", "t@example.invalid", cwd=clone)
    _git("config", "user.name", "test", cwd=clone)
    _git("config", "core.hooksPath", "hooks", cwd=clone)
    cloned_hook = clone / "hooks" / "pre-commit"
    assert cloned_hook.is_file(), (
        "hooks/pre-commit is absent from a fresh clone, which means it is not "
        "COMMITTED. An uncommitted hook protects this working tree and nothing "
        "else: every other clone, and this one after any reset, is unguarded. "
        "Commit the hook.")
    os.chmod(cloned_hook, 0o755)

    ledger = clone / "resources" / "MEMORY_EXCLUSIONS.md"
    if not ledger.is_file():
        pytest.skip("MEMORY_EXCLUSIONS.md absent in the clone")
    import re as _re
    text = ledger.read_text()
    m = _re.search(r"(\| *total *\| *)(\d+)( *\|)", text)
    if not m:
        pytest.skip("no total row to corrupt")
    ledger.write_text(text[:m.start()] + m.group(1) + str(int(m.group(2)) - 1)
                      + m.group(3) + text[m.end():])
    _git("add", "resources/MEMORY_EXCLUSIONS.md", cwd=clone)
    out = _commit(clone)
    assert out.returncode != 0, (
        "the REAL guards must refuse a REAL corruption in a real clone. "
        f"stdout:\n{out.stdout}\nstderr:\n{out.stderr}")
    assert "REFUSED" in out.stderr
