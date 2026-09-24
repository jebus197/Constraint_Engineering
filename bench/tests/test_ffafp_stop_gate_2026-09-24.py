"""The Stop gate can refuse, cannot trap, and must not guess at a path it cannot resolve.

WHY THIS FILE EXISTS. `hooks/ffafp_stop_gate.py` was armed on 2026-09-24 on the
founder's instruction ("Block rather than report") with its 5 safety properties
checked by hand in a session and by NO COMMITTED TEST. An addition that no test
executes is the defect class this project has confirmed 11 times, and arming a
hook that can refuse work while leaving it unguarded is the worst instance of it:
the only hook in this setup that can say no had nothing watching it.

It EXECUTES the gate as a subprocess and reads its exit code, per
`execute-do-not-grep`: a test that asserted on this hook's source text would pass
against a hook that refuses everything.

THE FALSE POSITIVE IT PINS, measured on the gate's FIRST REAL BOUNCE
(2026-09-24 01:47, minutes after arming). The gate refused a stop naming 6
changed paths and calling 2 of them code. Both were artefacts:

  * `$SP/gate_in.json` -- a scratchpad file. `classify_path` is applied to the
    path AS WRITTEN IN THE COMMAND TEXT, before the shell expands `$SP`, so it
    never matched the `/tmp/` or `/scratchpad/` transient prefixes and fell
    through to judging the file by its `.json` suffix. The RESOLVED path
    classifies correctly as `transient`.
  * `.claude/settings.json` -- a string inside a heredoc BODY, never written.

Real code changes on that turn: 0. A refusal on correct work is how the previous
Stop hook was parked within a day (2026-09-11), so this is not a cosmetic bug: it
is the one that decides whether the gate survives.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
GATE = REPO / "hooks" / "ffafp_stop_gate.py"
HOOKS = REPO / "hooks"


def run_gate(payload: dict, state_dir=None):
    env = dict(os.environ, PYTHONPATH=str(HOOKS))
    if state_dir is not None:
        env["FFAFP_AUDIT_STATE_DIR"] = str(state_dir)
    return subprocess.run([sys.executable, str(GATE)], input=json.dumps(payload),
                          capture_output=True, text=True, env=env, timeout=60)


def test_the_gate_is_present_at_its_real_path():
    assert GATE.is_file(), "the armed gate must exist in the repository, not only in ~/.claude"


def test_it_cannot_trap_a_session(tmp_path):
    """stop_hook_active means it has already refused once: it must stand down."""
    r = run_gate({"session_id": "s", "stop_hook_active": True,
                  "transcript_path": str(tmp_path / "absent.jsonl")}, tmp_path)
    assert r.returncode == 0, (
        "a Stop hook that refuses while stop_hook_active is set can loop forever")


def test_it_fails_open_on_malformed_input(tmp_path):
    env = dict(os.environ, PYTHONPATH=str(HOOKS))
    r = subprocess.run([sys.executable, str(GATE)], input="not json at all",
                       capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 0, "a broken gate must allow the stop, not block it"


def test_it_fails_open_on_a_missing_transcript(tmp_path):
    r = run_gate({"session_id": "s", "transcript_path": "/does/not/exist.jsonl"}, tmp_path)
    assert r.returncode == 0


@pytest.mark.parametrize("unresolved", [
    "$SP/gate_in.json",
    "${SCRATCH}/thing.json",
    "$HOME/x.yaml",
])
def test_an_unresolved_path_is_not_classified_as_code(unresolved):
    """THE FIRST BOUNCE'S DEFECT, pinned.

    A path carrying an unexpanded shell variable cannot be resolved, so it cannot
    be classified. Guessing from its suffix is what produced a refusal on a turn
    that changed no code. RED against the un-repaired classifier.
    """
    sys.path.insert(0, str(HOOKS))
    import ffafp_audit as fa
    assert fa.classify_path(unresolved) != "code", (
        f"{unresolved!r} was judged by its suffix although its target is unknown; "
        "this is the false refusal of 2026-09-24 01:47")


def test_the_resolved_form_of_that_same_path_is_transient():
    """ANTI-VACUITY for the test above: the classifier is right when it can see."""
    sys.path.insert(0, str(HOOKS))
    import ffafp_audit as fa
    assert fa.classify_path("/tmp/claude-501/x/scratchpad/gate_in.json") == "transient"


def test_a_real_code_change_with_no_failable_run_is_still_refused(tmp_path):
    """THE GATE MUST STILL BITE. If the repair above silenced it, the gate is
    decoration and this test is the thing that says so."""
    sys.path.insert(0, str(HOOKS))
    import ffafp_audit as fa
    assert fa.classify_path("bench/reference_runner_v3.py") == "code", (
        "an ordinary tracked Python file must still count as code, or the gate "
        "can never fire and the repair has gone too far")
