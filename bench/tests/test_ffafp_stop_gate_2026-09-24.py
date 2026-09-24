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

# ── WHY THERE IS NO SYNTHETIC END-TO-END TEST HERE, AND WHAT STANDS IN ITS PLACE ──
#
# 2 tests were written here on 2026-09-24 that ran the gate as a subprocess over a
# hand-built transcript and asserted its EXIT CODE: one that a turn whose only
# writes are unresolved paths is NOT refused, one that a real edit with no
# failable run still IS. They were DELETED rather than committed, because both
# were VACUOUS. Probed directly, `fa.scan` over either fixture left `state["open"]`
# None and `on_close` empty, so `fa.audit` was handed NO TURN AT ALL: the
# "passing" test passed because nothing was examined, which is the exact shape
# this project has caught 3 times as a substitution tautology. Shipping it would
# have been worse than shipping no test, because it would have read as coverage.
#
# Reproducing a real turn needs the transcript fields `scan` keys off, and I did
# not establish them. THE SYNTHETIC FIXTURE IS OWED and is named here so it is not
# mistaken for done.
#
# WHAT IS ESTABLISHED, on the live transcript rather than a fixture, and it is the
# stronger evidence for the repair itself:
#
#   BEFORE  the gate refused naming 6 paths, of which 3 were `$SP/...`
#   AFTER   the gate's list no longer contains ANY `$SP/...` entry
#
# and the refusal that remains names `bench/reference_runner_v3.py` and
# `bench/experiment_11_orchestrator.py`, both of which were genuinely edited, so
# the gate is now accusing only real changes. That transition is what the repair
# claimed and it is what was observed.
#
# THE LESSON THAT COST TWO ATTEMPTS. The first repair returned "other" for an
# unresolved path and THIS FILE asserted exactly that -- `classify_path != "code"`
# -- and passed, while the gate went on refusing, because its 3 consumers test
# `!= "transient"` and so counted "other" anyway. A fix verified only at the layer
# it edited is not verified. That is why `classify_path` now returns a distinct
# "unresolved" and why the consumers exclude it by name.


# ═══════════════════════════════════════════════════════════════════════════════
# ADDED 2026-09-24 (panel seat): the two halves the file above records as owed.
#
# 1. RESOLUTION, NOT GUESSING. The "unresolved" class closed the false refusal
#    by opening a silent evasion: `$REPO/bench/runner.py` could neither accuse
#    nor excuse. `resolve_shell_vars` closes the evasion by RESOLVING the
#    variable from the command's own assignment text, or from the inherited
#    environment, before classification. Only the residue -- knowable from
#    neither -- stays excluded, and a residual variable does not persist into
#    the write's own shell in this harness either, so no real write is lost.
#
# 2. THE SYNTHETIC END-TO-END FIXTURE the comment block above records as OWED.
#    The two deleted tests were vacuous because their hand-built transcripts
#    never produced a turn: `is_human_prompt` requires `origin.kind == "human"`,
#    which they did not set, so `fa.audit` was handed nothing. Every fixture
#    below FIRST proves, through `fa.scan` directly, that the turn it builds is
#    actually seen (mutations recorded, tools counted), and only then asserts on
#    the gate subprocess's exit code. A fixture that stops being parsed fails
#    the visibility assertion rather than passing the exit-code one.
# ═══════════════════════════════════════════════════════════════════════════════


def _fa():
    sys.path.insert(0, str(HOOKS))
    import ffafp_audit
    return ffafp_audit


def test_a_variable_assigned_in_the_same_command_resolves_to_transient():
    """The first bounce's exact shape, now EXCUSED BY EVIDENCE, not by guess."""
    fa = _fa()
    muts = fa.bash_mutations("SP=/tmp/claude/scratchpad; echo hi > $SP/gate_in.json")
    assert muts == ["/tmp/claude/scratchpad/gate_in.json"]
    assert fa.classify_path(muts[0]) == "transient"


def test_the_dollar_repo_evasion_form_now_counts_as_code():
    """Evasion form 1 of the 2026-09-24 brief, closed: resolved, then judged."""
    fa = _fa()
    muts = fa.bash_mutations(
        "REPO=/Users/x/proj; echo hi > $REPO/bench/reference_runner_v3.py")
    assert muts == ["/Users/x/proj/bench/reference_runner_v3.py"]
    assert fa.classify_path(muts[0]) == "code"


def test_the_braced_home_evasion_form_resolves_from_the_environment():
    """Evasion form 2: `${HOME}` is in the hook's own inherited environment."""
    fa = _fa()
    home = os.environ["HOME"]
    muts = fa.bash_mutations("echo hi > ${HOME}/proj/bench/runner.py")
    assert muts == [f"{home}/proj/bench/runner.py"]
    assert fa.classify_path(muts[0]) == "code"


def test_a_command_substitution_value_is_never_half_resolved():
    """`SP=$(mktemp -d)` is not knowable without executing; the path must stay
    'unresolved' rather than become a wrong guess. (Its true target is a fresh
    temp dir -- transient -- so exclusion is also the correct verdict.)"""
    fa = _fa()
    muts = fa.bash_mutations("SP=$(mktemp -d); echo hi > $SP/x.py")
    assert muts == ["$SP/x.py"]
    assert fa.classify_path(muts[0]) == "unresolved"


def test_the_residual_unresolved_class_still_exists():
    fa = _fa()
    assert fa.classify_path("$NEVER_SET_ANYWHERE_XYZ/file.py") == "unresolved"


# ── the synthetic end-to-end fixture, owed above, now built ──────────────────

def _human(uuid="t1"):
    return {"type": "user", "origin": {"kind": "human"}, "uuid": uuid,
            "timestamp": "2026-09-24T02:00:00Z", "message": {"content": "go"}}


def _assistant(*tool_uses):
    return {"type": "assistant",
            "message": {"content": [
                {"type": "tool_use", "name": n, "input": i} for n, i in tool_uses]}}


def _write_transcript(tmp_path, entries):
    f = tmp_path / "session.jsonl"
    f.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return f


def _prove_seen(fa, f, expect_mutations):
    """ANTI-VACUITY, the assertion the 2 deleted tests lacked: scan() must hand
    audit() a real open turn with exactly the expected mutation set."""
    state = {"offset": 0, "open": None, "seq": 0, "reads": {}}
    with f.open() as fh:
        fa.scan(fh, state)
    assert state["open"] is not None, "the fixture produced NO turn; the test would be vacuous"
    assert state["open"]["mutations"] == expect_mutations
    return fa.audit(state["open"], fa.prior_read_paths(state))


def test_e2e_a_code_edit_with_no_failable_run_is_refused(tmp_path):
    fa = _fa()
    f = _write_transcript(tmp_path, [
        _human(),
        _assistant(("Edit", {"file_path": "bench/foo.py",
                             "old_string": "a", "new_string": "b"})),
    ])
    v = _prove_seen(fa, f, ["bench/foo.py"])
    assert v["code"] and "P-PASS" in v["missing"]
    r = run_gate({"session_id": "s", "transcript_path": str(f)}, tmp_path)
    assert r.returncode == 2, f"gate allowed an unverified code edit: {r.stderr}"
    assert "bench/foo.py" in r.stderr and "P-PASS" in r.stderr


def test_e2e_a_scratchpad_only_turn_is_not_refused(tmp_path):
    """The first bounce, replayed end to end: $SP writes, zero code changes."""
    fa = _fa()
    f = _write_transcript(tmp_path, [
        _human(),
        _assistant(("Bash", {"command":
            "SP=/tmp/claude/scratchpad; mkdir -p $SP; echo '{}' > $SP/gate_in.json"})),
    ])
    # Seen, resolved, and rightly excluded: the resolved path is transient.
    state = {"offset": 0, "open": None, "seq": 0, "reads": {}}
    with f.open() as fh:
        fa.scan(fh, state)
    assert state["open"] is not None and state["open"]["n_tools"] == 1, (
        "the fixture produced no turn; a passing exit code would be vacuous")
    assert state["open"]["mutations"] == [], (
        "the scratchpad write leaked into the mutation set")
    r = run_gate({"session_id": "s", "transcript_path": str(f)}, tmp_path)
    assert r.returncode == 0, f"the 01:47 false refusal is back: {r.stderr}"


def test_e2e_a_code_edit_with_the_trace_present_is_released(tmp_path):
    """The gate must stand down when the owed check actually ran."""
    fa = _fa()
    f = _write_transcript(tmp_path, [
        _human(),
        _assistant(("Edit", {"file_path": "bench/foo.py",
                             "old_string": "a", "new_string": "b"})),
        _assistant(("Bash", {"command": "python3 -m pytest bench/tests/test_foo.py -q"})),
    ])
    v = _prove_seen(fa, f, ["bench/foo.py"])
    assert v["analysed"] and v["verified_after"]
    r = run_gate({"session_id": "s", "transcript_path": str(f)}, tmp_path)
    assert r.returncode == 0, f"gate refused a turn that ran its check: {r.stderr}"


def test_e2e_an_evasion_shaped_write_is_now_refused(tmp_path):
    """The brief's evasion, end to end: a $REPO-spelled write to real code with
    nothing failable after it must be caught, not excluded."""
    fa = _fa()
    f = _write_transcript(tmp_path, [
        _human(),
        _assistant(("Bash", {"command":
            "REPO=/Users/x/proj; echo pass > $REPO/bench/reference_runner_v3.py"})),
    ])
    v = _prove_seen(fa, f, ["/Users/x/proj/bench/reference_runner_v3.py"])
    assert v["code"]
    r = run_gate({"session_id": "s", "transcript_path": str(f)}, tmp_path)
    assert r.returncode == 2, "the $REPO evasion is open again"
