"""Guards for scripts/task_list_markers.py, the task-list marker engine.

Written 2026-09-09. Every test CALLS the module against a temporary list rather
than asserting on its source, per `execute-do-not-grep`.

WHY THE MODULE EXISTS, restated so these tests cannot be read as busywork: on
2026-09-09 three different regular expressions over the master task list counted
23, 29 and 48 entries. The true figure is 59. The most dangerous of those was the
one that reported the list "coherent" while silently skipping 16 entries -- a
parser that omits is worse than one that fails, because it reports success. The
first test below exists specifically to make that failure impossible to repeat.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("tlm_under_test",
                                               REPO / "scripts" / "task_list_markers.py")
tlm = importlib.util.module_from_spec(_spec)
sys.modules["tlm_under_test"] = tlm          # dataclass needs the module registered
_spec.loader.exec_module(tlm)

# The 3 heading styles genuinely in use in the list. All 3 must parse, because the
# defect was a pattern that matched 1 of them and quietly dropped the rest.
THREE_STYLES = """# t

**R1. Bolded identifier with a period.** Body.

**0.1 Numeric identifier, no period, space follows.** Body.

**6.1** Identifier wrapped in bold, then the title. Body.

**11 tests, and 3 of 4 mutations were caught.** This is PROSE, not an entry.
"""


def _write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "LIST.md"
    p.write_text(text)
    return p


# --- The failure that motivated the module. ----------------------------------

def test_all_three_heading_styles_parse_and_prose_does_not(tmp_path):
    p = _write(tmp_path, THREE_STYLES)
    idents = [e.ident for e in tlm.parse_entries(p)]
    assert idents == ["R1", "0.1", "6.1"], (
        f"all 3 styles must parse and the prose line must not; got {idents}")


def test_the_real_list_parses_every_entry():
    """A regression pin on the true count. If a future edit introduces a 4th
    heading style, this drops and says so instead of silently under-reporting."""
    entries = tlm.parse_entries()
    assert len(entries) >= 59, f"only {len(entries)} entries parsed from the real list"
    unmarked = [e.ident for e in entries if e.state is None]
    assert unmarked == [], f"entries with no marker: {unmarked}"


# --- The cross-check, which is the whole reason for 2 vocabularies. -----------

@pytest.mark.parametrize("state,status,contradictory", [
    ("DONE", "PROPOSED", True),
    ("DONE", "BUILT", True),
    ("DONE", "TESTED", True),
    ("DONE", "COMMITTED", False),
    ("DONE", "ENABLED", False),
    ("OPEN", "COMMITTED", False),      # committed but not enabled is legitimate
    ("WITHDRAWN", "PROPOSED", False),  # closed by ruling, no work product
])
def test_the_cross_check_flags_exactly_the_contradictory_cells(tmp_path, state, status, contradictory):
    p = _write(tmp_path, f"# t\n\n**R1. Title.** Body.\n<!-- task: R1 | state: {state} | status: {status} -->\n")
    code, problems = tlm.check(p)
    if contradictory:
        assert code == 1 and problems, f"state={state} status={status} must be flagged"
        assert "cannot be done before" in problems[0]
    else:
        assert code == 0 and not problems, f"state={state} status={status} must be accepted: {problems}"


def test_an_unknown_state_is_rejected(tmp_path):
    p = _write(tmp_path, "# t\n\n**R1. T.** B.\n<!-- task: R1 | state: MAYBE | status: PROPOSED -->\n")
    code, problems = tlm.check(p)
    assert code == 1 and "not one of" in problems[0]


def test_a_duplicate_identifier_is_caught(tmp_path):
    p = _write(tmp_path, "# t\n\n**R1. A.** B.\n<!-- task: R1 | state: OPEN | status: PROPOSED -->\n\n"
                         "**R1. B.** B.\n<!-- task: R1 | state: OPEN | status: PROPOSED -->\n")
    code, problems = tlm.check(p)
    assert code == 1 and any("already used" in x for x in problems)


def test_an_empty_list_is_a_problem_not_a_pass(tmp_path):
    """A parser that finds nothing must not report coherence."""
    p = _write(tmp_path, "# a document with no entries at all\n")
    code, problems = tlm.check(p)
    assert code == 1 and "no entries parsed" in problems[0]


# --- apply(), and its idempotence. -------------------------------------------

def test_apply_is_idempotent(tmp_path):
    p = _write(tmp_path, THREE_STYLES)
    first = tlm.apply_markers(p)
    assert first == 3, f"3 entries needed markers, added {first}"
    second = tlm.apply_markers(p)
    assert second == 0, "running it twice must not double-mark"
    assert tlm.check(p)[0] == 0


def test_a_ruling_closed_entry_infers_WITHDRAWN_not_DONE(tmp_path):
    p = _write(tmp_path, "# t\n\n**1.3 CLOSED BY FOUNDER RULING 2026-09-09** and no work follows.\n")
    tlm.apply_markers(p)
    e = tlm.parse_entries(p)[0]
    assert e.state == "WITHDRAWN", (
        f"an item closed by ruling has no work product, so DONE would falsely "
        f"imply work was completed; got {e.state}")


# --- summarise() must not lie by omission. -----------------------------------

def test_the_summary_accounts_for_every_entry(tmp_path):
    p = _write(tmp_path, "# t\n\n**R1. A.** B.\n<!-- task: R1 | state: WITHDRAWN | status: PROPOSED -->\n\n"
                         "**R2. B.** B.\n<!-- task: R2 | state: OPEN | status: PROPOSED -->\n")
    line = tlm.summarise(p)
    assert "2 entries" in line
    assert "withdrawn" in line, f"a state with a nonzero count must appear: {line}"


def test_the_summary_names_the_next_open_entry(tmp_path):
    p = _write(tmp_path, "# t\n\n**R1. Done thing.** B.\n<!-- task: R1 | state: DONE | status: ENABLED -->\n\n"
                         "**R2. The next real job.** B.\n<!-- task: R2 | state: OPEN | status: PROPOSED -->\n")
    assert "The next real job" in tlm.summarise(p)


# --- The pulse hook, executed exactly as the harness executes it. ------------

HOOK = REPO / "hooks" / "task_list_pulse.py"


def _run_hook(payload: dict, cwd: Path | None = None):
    import json as _json
    import subprocess
    return subprocess.run(["python3", str(HOOK)], input=_json.dumps(payload),
                          capture_output=True, text=True, timeout=60,
                          cwd=str(cwd) if cwd else None)


def test_the_hook_emits_the_task_line_and_exits_zero():
    r = _run_hook({"session_id": "t", "cwd": str(REPO)})
    assert r.returncode == 0
    import json as _json
    out = _json.loads(r.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert ctx.startswith("[tasks] "), ctx
    assert "entries" in ctx and "next:" in ctx


def test_the_hook_finds_the_repository_from_an_unrelated_directory(tmp_path):
    r = _run_hook({"session_id": "t", "cwd": str(tmp_path)}, cwd=tmp_path)
    assert r.returncode == 0
    assert "[tasks]" in r.stdout, "the fallback path must locate the checkout"


def test_the_hook_never_blocks_a_prompt_whatever_it_is_given():
    """A hook that blocks a prompt is far worse than a missing context line, so
    every failure path must still exit 0. Checked with 4 hostile inputs."""
    import subprocess
    for bad in ["not json", "", "[]", '{"cwd": "/nonexistent/nowhere"}']:
        r = subprocess.run(["python3", str(HOOK)], input=bad,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, f"input {bad!r} produced exit {r.returncode}"


def test_the_hook_surfaces_a_contradiction_rather_than_hiding_it(tmp_path):
    """The cross-check is the reason for 2 vocabularies; if the pulse swallowed
    the disagreement it would be a reminder rather than a guard."""
    p = tmp_path / "LIST.md"
    p.write_text("# t\n\n**R1. A.** B.\n<!-- task: R1 | state: DONE | status: PROPOSED -->\n")
    line = tlm.summarise(p)
    assert "MARKER PROBLEM" in line, f"the contradiction must reach the line: {line}"
