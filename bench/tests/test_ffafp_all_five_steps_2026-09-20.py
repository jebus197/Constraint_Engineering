#!/usr/bin/env python3
"""The FFAFP detector must cover all 5 steps, and must FIRE on a heredoc write.

FOUNDER, 2026-09-20: "These p-pass failures are increasingly persistent ... you
have clearly still only hard wired the p-pass element ... You have to make sure
it fires too. Even the p-pass element alone doesn't always fire."

BOTH HALVES WERE REAL, and the second is the one that mattered.

COVERAGE. Measured before the repair, the detector named exactly 3 of the 5
steps -- FOLLOW, ANALYSE, P-PASS -- with no FIND and no FIX detector anywhere.
Its own docstring said so in false-negative item 4: "FIND is not modelled ...
No attempt is made to detect it." So the count in the complaint was wrong (3 of
5, not 1 of 5) and its substance was right.

Worse, the signal LABELLED FOLLOW was computed from "did you read the file you
edited", which is FIND. FOLLOW proper -- who depends on this -- was never
measured, because `_READ_TOOLS` lumped `Read` together with `Grep` and `Glob`.

FIRING. The detector was BLIND to the most common editing shape in this
session. `python3 - <<'PY' ... p.write_text(s) ... PY` leaves no shell redirect
and no Edit tool call, so the turn recorded 0 mutations and `is_work` False:
no FOLLOW, no ANALYSE, no P-PASS, complete silence. An equivalent `sed -i`
recorded 1 mutation and 2 flags. The module called this hole "unavoidable
without executing the body", which is wrong -- the body needs PARSING, not
executing, exactly as the shell redirect scan beside it already does.

THESE TESTS DRIVE THE REAL FUNCTIONS against inputs whose right answer is known
by construction, rather than asserting on the module's source text.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LIVE = pathlib.Path.home() / ".claude" / "hooks" / "ffafp_audit.py"
VERSIONED = REPO / "hooks" / "ffafp_audit.py"


def _load(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location("ffafp_under_test", path)
    m = importlib.util.module_from_spec(spec)
    sys.modules["ffafp_under_test"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def fa():
    if not LIVE.is_file():
        pytest.skip(f"hook absent at {LIVE}")
    return _load(LIVE)


EDIT_PY = ("Edit", {"file_path": "bench/reference_runner_v3.py"})
READ_PY = ("Read", {"file_path": "bench/reference_runner_v3.py"})
GREP_PY = ("Grep", {"pattern": "reference_runner_v3"})
RUN_TESTS = ("Bash", {"command": "python3 -m pytest bench/tests/ -q"})


def turn(fa, *calls):
    t = fa.new_turn("id", "2026-09-20T00:00:00", "p")
    for name, inp in calls:
        fa.record_tool(t, name, inp)
    return t


# ── the copy that runs must be the copy that is reviewed ────────────────────

def test_the_versioned_copy_is_the_one_that_actually_runs():
    """3 of the 4 hooks that preceded this one existed in NO repository at all.

    A hook reviewed in the repository while a different file runs from $HOME is
    a guard nobody has read. Found live on 2026-09-20: the repository copy was
    edited and the tests, which load $HOME, went on passing against the old code.
    """
    if not LIVE.is_file():
        pytest.skip(f"hook absent at {LIVE}")
    assert VERSIONED.is_file(), "the hook is not versioned in this repository"
    assert LIVE.read_bytes() == VERSIONED.read_bytes(), (
        "hooks/ffafp_audit.py and the copy that actually runs at "
        f"{LIVE} have DIVERGED. Sync them: the reviewed file and the running "
        "file must be the same bytes.")


# ── all 5 steps are named ───────────────────────────────────────────────────

def test_every_one_of_the_five_steps_has_a_detector(fa):
    """The complaint, as a test. No step may be unrepresented."""
    for step in ("FIND", "FOLLOW", "ANALYSE", "FIX", "P-PASS"):
        assert step in fa._WHY, f"{step} has no explanation and so no detector"


def test_a_bare_edit_flags_find_and_follow(fa):
    """An edit with no prior look and no prior scan is missing both."""
    v = fa.audit(turn(fa, EDIT_PY, RUN_TESTS))
    assert "FIND" in v["missing"], v["missing"]
    assert "FOLLOW" in v["missing"], v["missing"]


def test_reading_the_file_satisfies_find_but_NOT_follow(fa):
    """THE DISTINCTION THE OLD CODE COULD NOT DRAW.

    Opening the file you are about to change tells you WHAT is there. It cannot
    tell you who CALLS it. Before 2026-09-20 a `Read` satisfied the signal
    labelled FOLLOW, so the blast-radius step was credited by an act that does
    not map a blast radius.
    """
    v = fa.audit(turn(fa, READ_PY, EDIT_PY, RUN_TESTS))
    assert v["found"] is True
    assert "FIND" not in v["missing"], v["missing"]
    assert v["followed"] is False
    assert "FOLLOW" in v["missing"], v["missing"]


def test_a_tree_scan_satisfies_follow(fa):
    """`Grep` for the module name IS the canonical 'who imports this' search."""
    v = fa.audit(turn(fa, GREP_PY, EDIT_PY, RUN_TESTS))
    assert v["followed"] is True
    assert "FOLLOW" not in v["missing"], v["missing"]


def test_a_recursive_shell_grep_also_satisfies_follow(fa):
    scan = ("Bash", {"command": "grep -rn reference_runner_v3 bench/"})
    v = fa.audit(turn(fa, scan, EDIT_PY, RUN_TESTS))
    assert v["followed"] is True, v


def test_catting_one_file_does_NOT_satisfy_follow(fa):
    """A read dressed as a shell command is still a read."""
    v = fa.audit(turn(fa, ("Bash", {"command": "cat bench/reference_runner_v3.py"}),
                      EDIT_PY, RUN_TESTS))
    assert v["followed"] is False, v
    assert "FOLLOW" in v["missing"]


def test_changing_only_tests_is_reported_as_a_FIX_question(fa):
    """Fixing the test instead of the defect is the shape to surface."""
    edit_test = ("Edit", {"file_path": "bench/tests/test_something.py"})
    v = fa.audit(turn(fa, ("Grep", {"pattern": "test_something"}), edit_test, RUN_TESTS))
    assert v["test_only"] is True
    assert "FIX" in v["missing"], v["missing"]


def test_changing_source_as_well_does_not_raise_the_FIX_question(fa):
    edit_test = ("Edit", {"file_path": "bench/tests/test_something.py"})
    v = fa.audit(turn(fa, GREP_PY, EDIT_PY, edit_test, RUN_TESTS))
    assert v["test_only"] is False
    assert "FIX" not in v["missing"], v["missing"]


# ── IT MUST FIRE: the heredoc hole ──────────────────────────────────────────

HEREDOC_WRITE = """python3 - <<'PY'
from pathlib import Path
p = Path("bench/openrouter_tools.py"); s = p.read_text()
p.write_text(s.replace("a", "b"))
PY"""

HEREDOC_OPEN_W = """python3 - <<'PY'
open("scripts/generated.py", "w").write("x")
PY"""

HEREDOC_READONLY = """python3 - <<'PY'
import json
d = json.load(open("bench/logs/x.json"))
print(d["chars"], len(d))
PY"""

HEREDOC_SYMPY = """python3 - <<'PY'
import sympy as sp
print(sp.simplify("x + x"))
PY"""

HEREDOC_MENTIONS_A_PATH = """python3 - <<'PY'
print("see bench/openrouter_tools.py for details")
PY"""


def test_a_heredoc_write_is_detected_as_work(fa):
    """THE FIRING DEFECT, as a test. This returned 0 mutations before today."""
    muts = fa.bash_mutations(HEREDOC_WRITE)
    assert muts == ["bench/openrouter_tools.py"], muts
    v = fa.audit(turn(fa, ("Bash", {"command": HEREDOC_WRITE})))
    assert v["is_work"] is True, "a heredoc write is still invisible"
    assert "P-PASS" in v["missing"], v["missing"]


def test_a_heredoc_open_for_writing_is_detected(fa):
    assert fa.bash_mutations(HEREDOC_OPEN_W) == ["scripts/generated.py"]


@pytest.mark.parametrize("cmd,label", [
    (HEREDOC_READONLY, "a read-only analysis heredoc"),
    (HEREDOC_SYMPY, "a symbolic-maths heredoc"),
    (HEREDOC_MENTIONS_A_PATH, "a heredoc that only mentions a path"),
    ('grep -rn "write_text(" bench/', "write_text in ordinary shell text"),
])
def test_read_only_work_is_NOT_called_a_mutation(fa, cmd, label):
    """THE ANTI-NOISE HALF, and it decides whether the hook survives.

    Analysis heredocs are the most common tool call in this project. If they
    counted as mutations, every analysis turn would demand a P-PASS, the notice
    would fire constantly, and the hook would be switched off within a day --
    which the module's own 'REPORT, NEVER BLOCK' section says is the failure
    mode to avoid.
    """
    assert fa.bash_mutations(cmd) == [], f"{label} was wrongly called a mutation"


def test_the_detector_is_not_vacuous_in_either_direction(fa):
    """It must fire on something and stay silent on something."""
    fires = fa.audit(turn(fa, ("Bash", {"command": HEREDOC_WRITE})))
    silent = fa.audit(turn(fa, GREP_PY, READ_PY, EDIT_PY, RUN_TESTS))
    assert fires["missing"], "fires on nothing"
    assert "FIND" not in silent["missing"] and "FOLLOW" not in silent["missing"], (
        f"a turn that scanned, read, edited and tested still flags: {silent['missing']}")
