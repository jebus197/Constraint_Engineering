"""His autonomy handover must reach every turn, including the turn after a compaction.

WHAT THIS GUARDS. On 2026-11-21 the founder handed the remaining work up to the
bounded orchestrator run to this instance, and asked in the same breath for the
instruction to be implemented "in a way that will survive every compaction event
from now on". A compaction discards the conversation. It does not discard what a
UserPromptSubmit hook injects, which is the same reasoning that put the master
task list in `hooks/task_list_pulse.py` in the first place.

WHY THE TESTS EXECUTE THE HOOK RATHER THAN READ IT. `execute-do-not-grep`: a test
asserting on the SOURCE TEXT of a hook asserts only that the hook describes
itself consistently, and cannot detect a producer and a consumer that disagree.
Four defects in this project were found by running two forms against each other
and none by reading. So the integration tests run the real hook as a subprocess
with a real payload and parse the JSON it emits.

WHY THE LIVE COPY IS CHECKED. `hooks/task_list_pulse.py` is HARD LINKED to
`~/.claude/hooks/task_list_pulse.py`, and the Edit tool breaks that link by
writing a new inode -- measured on this very file's sibling earlier the same
night, where the live gate went on running old code while the repository copy
showed the fix. A test that only reads the repository copy cannot see that.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "task_list_pulse.py"
LIVE = pathlib.Path.home() / ".claude" / "hooks" / "task_list_pulse.py"
GOAL = REPO / "experimental_notes" / "THE_STANDING_GOAL.md"

BEGIN = "<!-- INJECT-BEGIN -->"
END = "<!-- INJECT-END -->"


def _load_hook_module():
    """Import the hook for unit access to its functions.

    THE HOOK IS A SCRIPT, NOT A LIBRARY. Its last two statements call main()
    and then sys.exit(0) unconditionally -- deliberately, because a hook that
    fails to exit 0 is worse than a hook that emits nothing. So importing it
    runs it once and raises SystemExit. Both function definitions execute
    BEFORE that trailing block, so the module object is fully populated by the
    time the exit fires and catching it is sufficient.

    The hook is NOT reshaped with an `if __name__ == "__main__"` guard to make
    this tidier: that would be a change to code which runs on every turn, made
    for the convenience of a test, and the cost of getting it wrong is that the
    task list silently stops reaching the session.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("tlp_guard", HOOK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tlp_guard"] = mod
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    assert hasattr(mod, "standing_goal"), "import did not bind standing_goal"
    return mod


def _run_hook(cwd):
    """Run the LIVE hook exactly as the harness does, and return its context."""
    proc = subprocess.run(
        [sys.executable, str(LIVE)],
        input=json.dumps({"cwd": str(cwd)}),
        capture_output=True, text=True, timeout=120,
    )
    return proc


# ---------------------------------------------------------------- the file

def test_the_goal_file_exists():
    assert GOAL.is_file(), f"{GOAL} is the source of the injected instruction"


def test_the_goal_file_carries_both_markers():
    t = GOAL.read_text()
    assert BEGIN in t and END in t
    assert t.index(BEGIN) < t.index(END), "markers out of order"


def test_the_injected_block_names_all_four_reserved_categories():
    """His 4 categories are the whole content of the handover's HIL clause."""
    t = GOAL.read_text()
    block = t[t.index(BEGIN) + len(BEGIN):t.index(END)].lower()
    for phrase in ("irreducible", "safety", "legal", "fundamental change"):
        assert phrase in block, f"the injected block never says {phrase!r}"


def test_the_injected_block_requires_testing_what_the_panel_proposes():
    """Adopting a panel's proposal untested is the failure he named explicitly."""
    t = GOAL.read_text()
    block = t[t.index(BEGIN) + len(BEGIN):t.index(END)].lower()
    assert "panel" in block
    assert "test" in block, "the block must say the panel's fixes are tested first"


def test_the_file_holds_his_words_verbatim_outside_the_block():
    """The short form is derived; the verbatim quotation is what it derives from."""
    t = GOAL.read_text()
    assert "computationally irreducible" in t
    assert "orchestrator run" in t


# ------------------------------------------------------- the reader function

def test_standing_goal_reads_between_the_markers(tmp_path):
    mod = _load_hook_module()
    d = tmp_path / "experimental_notes"
    d.mkdir(parents=True)
    (d / "THE_STANDING_GOAL.md").write_text(
        f"preamble\n{BEGIN}\nTHE PAYLOAD\n{END}\npostamble\n")
    assert mod.standing_goal(tmp_path) == "THE PAYLOAD"


def test_standing_goal_is_fail_safe_when_the_file_is_absent(tmp_path):
    """A missing file costs one context line. It must never cost the turn."""
    mod = _load_hook_module()
    assert mod.standing_goal(tmp_path) == ""


def test_standing_goal_is_fail_safe_when_a_marker_is_missing(tmp_path):
    mod = _load_hook_module()
    d = tmp_path / "experimental_notes"
    d.mkdir(parents=True)
    (d / "THE_STANDING_GOAL.md").write_text(f"{BEGIN}\nno closing marker\n")
    assert mod.standing_goal(tmp_path) == ""


def test_standing_goal_is_fail_safe_when_the_markers_are_inverted(tmp_path):
    mod = _load_hook_module()
    d = tmp_path / "experimental_notes"
    d.mkdir(parents=True)
    (d / "THE_STANDING_GOAL.md").write_text(f"{END}\nbackwards\n{BEGIN}\n")
    assert mod.standing_goal(tmp_path) == ""


def test_standing_goal_tracks_the_file_rather_than_a_constant(tmp_path):
    """The text must come FROM the file, so he can amend it without a code edit."""
    mod = _load_hook_module()
    d = tmp_path / "experimental_notes"
    d.mkdir(parents=True)
    f = d / "THE_STANDING_GOAL.md"
    f.write_text(f"{BEGIN}\nFIRST\n{END}\n")
    first = mod.standing_goal(tmp_path)
    f.write_text(f"{BEGIN}\nSECOND\n{END}\n")
    second = mod.standing_goal(tmp_path)
    assert first == "FIRST" and second == "SECOND", (first, second)


# ------------------------------------------------------------- end to end

@pytest.mark.skipif(not LIVE.is_file(), reason="no live hook on this machine")
def test_the_live_hook_emits_the_goal():
    proc = _run_hook(REPO)
    assert proc.returncode == 0, proc.stderr
    ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "\n[goal] " in ctx, "the live hook injected no goal line"


@pytest.mark.skipif(not LIVE.is_file(), reason="no live hook on this machine")
def test_the_live_hook_still_opens_with_the_tasks_prefix():
    """test_task_list_markers_2026-09-09.py asserts this. Adding must not break it."""
    proc = _run_hook(REPO)
    ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    assert ctx.startswith("[tasks] ")


@pytest.mark.skipif(not LIVE.is_file(), reason="no live hook on this machine")
def test_every_injected_line_identifies_itself():
    """An unmarked continuation line is indistinguishable from unrelated context."""
    proc = _run_hook(REPO)
    ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    stray = [l for l in ctx.split("\n")
             if l.strip() and not l.startswith(("[tasks]", "[entries]", "[goal]"))]
    assert stray == [], f"{len(stray)} unlabelled line(s): {stray[:3]}"


@pytest.mark.skipif(not LIVE.is_file(), reason="no live hook on this machine")
def test_the_goal_reaches_the_turn_whole():
    """Every non-blank line of the block must arrive, not just the first."""
    t = GOAL.read_text()
    block = t[t.index(BEGIN) + len(BEGIN):t.index(END)].strip()
    want = [l for l in block.splitlines() if l.strip()]
    proc = _run_hook(REPO)
    ctx = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    got = [l[len("[goal] "):] for l in ctx.split("\n") if l.startswith("[goal] ")]
    assert got == want, f"{len(got)} line(s) injected of {len(want)}"


@pytest.mark.skipif(not LIVE.is_file(), reason="no live hook on this machine")
def test_the_live_hook_and_the_repo_copy_are_the_same_file():
    """The Edit tool breaks this hard link; a fix in the repo then runs nowhere."""
    assert os.stat(LIVE).st_ino == os.stat(HOOK).st_ino, (
        "hooks/task_list_pulse.py and ~/.claude/hooks/task_list_pulse.py have "
        "diverged -- re-link with: ln -f hooks/task_list_pulse.py "
        "~/.claude/hooks/task_list_pulse.py")
