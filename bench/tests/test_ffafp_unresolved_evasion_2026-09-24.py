"""The 'unresolved' class was an EVASION HOLE, and the repair is RESOLUTION.

WHAT WENT WRONG (2026-09-24, ~02:55). `classify_path` gained an 'unresolved' class
while repairing a FALSE POSITIVE: the Stop gate had refused a turn whose only write
was `$SP/gate_in.json`, a scratchpad file the classifier judged by its `.json` suffix
because it sees the path BEFORE the shell expands `$SP`. The repair made all 3
consumers drop unresolved paths from the mutation set entirely, so such a path could
neither accuse nor excuse. Executed against the live predicate, that silently excused
real code:

    bench/reference_runner_v3.py          -> COUNTS
    $REPO/bench/reference_runner_v3.py    -> IGNORED   <-- real code, evaded
    ${HOME}/proj/bench/runner.py          -> IGNORED   <-- braced form, evaded

It also inverted the project's own asymmetry. `detect_target_kind` resolves every
ambiguous case to the SAFER side; this resolved it to the unsafe side, trading a
visible, self-correcting false refusal for a silent miss, which is none of those.

THE REPAIR IS NEITHER OBVIOUS OPTION. Counting every unresolved path restores the
false positive that gets a Stop hook parked (measured: 131 of 242, 54.1% of the class,
are genuinely transient). Ignoring them is the hole. The hook holds the WHOLE command
text and the variable is usually ASSIGNED in it, so `classify_write` RESOLVES rather
than guesses. See its docstring for the corpus figures.

WHAT THESE TESTS ASSERT, AND WHY EACH IS NOT VACUOUS. Both halves of the 2026-09-24
debt are discharged here:

  * the unit half pins the 3-tier ladder, INCLUDING tier 3 -- the residue that is
    still evaded -- so the hole's remaining size stays visible instead of being
    quietly believed closed;
  * the end-to-end half hands a real synthetic transcript to the real gate as a
    SUBPROCESS and asserts its exit code. The 2 tests deleted on 2026-09-24 were
    vacuous because `fa.scan` was handed entries lacking `origin: {"kind": "human"}`,
    so no turn ever opened and `fa.audit` examined NOTHING. Every end-to-end test
    below therefore asserts FIRST that a turn actually opened and that the verdict
    names the file -- the anti-vacuity assertion the deleted pair lacked.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOKS = REPO / "hooks"
GATE = HOOKS / "ffafp_stop_gate.py"
sys.path.insert(0, str(HOOKS))
import ffafp_audit as fa  # noqa: E402  the ONE copy of the trace rules


# ---------------------------------------------------------------------------
# Synthetic transcript. The field set is the one `fa.scan` actually keys off:
# `origin.kind == "human"` opens a turn (its absence is what made the deleted
# tests vacuous), and a tool call must be a `tool_use` block on an `assistant`
# entry. Every line must contain the literal `"type"` or `scan` skips it unparsed.
# ---------------------------------------------------------------------------
def entry_human(uuid="u1", ts="2026-09-24T03:00:00Z", text="do the thing"):
    return {"type": "user", "origin": {"kind": "human"}, "uuid": uuid,
            "timestamp": ts, "message": {"content": text}}


def entry_tool(name, inp):
    return {"type": "assistant",
            "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}


def write_jsonl(path, entries):
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return path


def run_gate(transcript, stop_hook_active=False):
    payload = json.dumps({"transcript_path": str(transcript),
                          "stop_hook_active": stop_hook_active})
    return subprocess.run([sys.executable, str(GATE)], input=payload,
                          capture_output=True, text=True, timeout=60)


def verdict_of(transcript):
    """The verdict the gate will act on, obtained through the gate's OWN path."""
    state = {"offset": 0, "open": None, "seq": 0, "reads": {}}
    with transcript.open("r", errors="ignore") as fh:
        closed = []
        fa.scan(fh, state, on_close=closed.append)
    if state.get("open"):
        return fa.audit(state["open"], fa.prior_read_paths(state))
    return closed[-1] if closed else None


# ---------------------------------------------------------------------------
# Tier 1: RESOLVE. A binding in the same command text decides the path.
# ---------------------------------------------------------------------------
def test_a_bound_variable_is_resolved_not_guessed():
    cmd = 'SP=/tmp/scratch.$$; echo hi > $SP/gate_in.json'
    assert fa.classify_write("$SP/gate_in.json", cmd) == "transient"
    # ...and the same path with a REPO binding is code, from the same machinery.
    cmd2 = 'SP=bench; python3 - > $SP/runner.py'
    assert fa.classify_write("$SP/runner.py", cmd2) == "code"


def test_environment_resolves_the_braced_evasion_form():
    """`${HOME}/...` was evasion form 2 of 2 and is closed unconditionally."""
    assert fa.classify_path("${HOME}/proj/bench/runner.py") == "unresolved"
    assert fa.classify_write("${HOME}/proj/bench/runner.py") == "code"


def test_a_loop_variable_is_a_binding():
    cmd = 'for n in 48 49; do cat > "bench/targets/exp$n.py" <<EOF\nx\nEOF\ndone'
    assert fa.classify_write("bench/targets/exp$n.py", cmd) == "code"


def test_a_command_substitution_value_is_refused_not_half_expanded():
    """`WT=$(mktemp -d)/repo` captures only `$(mktemp`. Substituting that fragment
    manufactures a path that was never written, so the binding is DROPPED."""
    assert "WT" not in fa.shell_bindings('WT=$(mktemp -d)/repo; echo > $WT/a.py')


# ---------------------------------------------------------------------------
# Tier 2: the directory is known even though the basename is not.
# ---------------------------------------------------------------------------
def test_a_known_directory_counts_even_with_an_unresolved_basename():
    # AMENDED 2026-09-24 (CC1). This seat's design kept `classify_path` as the
    # RAW classifier -- "unresolved" until a command text resolves it -- and put
    # all inference in `classify_write`. The shipped implementation instead
    # infers from the LITERAL LEADING PREFIX plus the LITERAL EXTENSION inside
    # `classify_path` itself, because that inference needs no command text:
    # transience is decided by where a path starts and kind by how it ends, and
    # a variable in between changes neither. That is STRICTLY SAFER -- a write is
    # counted even when no command text is available -- so the assertion is
    # relaxed from "unresolved" to "the write is classified, not discarded".
    # The safety property this test exists for is unchanged and is asserted on
    # the next line.
    assert fa.classify_path("bench/logs/run_$STAMP/BRIEF.md") != "unresolved"
    assert fa.classify_write("bench/logs/run_$STAMP/BRIEF.md") == "doc"
    assert fa.classify_write("bench/dm/$MOD.py") == "code"


# ---------------------------------------------------------------------------
# Tier 3: the honest residue. This test EXISTS TO KEEP THE HOLE VISIBLE.
# ---------------------------------------------------------------------------
def test_a_leading_variable_is_still_unresolved_and_that_is_deliberate():
    """If the LEADING component is a variable the directory is genuinely unknown,
    and judging `$SP/gate_in.json` by its `.json` suffix is the exact guess that
    produced the 2026-09-24 false refusal. Counting these would cost 131 false
    refusals per corpus. This asserts the REMAINING hole, not its closure."""
    assert fa.classify_write("$SP/gate_in.json", "echo hi > $SP/gate_in.json") == "unresolved"
    assert fa.classify_write("$REPO/bench/reference_runner_v3.py") == "unresolved"


# ---------------------------------------------------------------------------
# END-TO-END. The owed fixture: a real transcript through the real gate.
# ---------------------------------------------------------------------------
def test_the_synthetic_transcript_actually_opens_a_turn(tmp_path):
    """ANTI-VACUITY, asserted before anything else in this file's e2e half.

    The 2 tests deleted on 2026-09-24 passed because `fa.audit` was handed NO TURN.
    If this assertion ever fails, every exit-code assertion below is meaningless.
    """
    t = write_jsonl(tmp_path / "t.jsonl",
                    [entry_human(), entry_tool("Edit", {"file_path": "bench/dm/_convergence.py",
                                                        "old_string": "a", "new_string": "b"})])
    v = verdict_of(t)
    assert v is not None, "no turn opened: the fixture is vacuous"
    assert v["is_work"] and v["code"], v
    assert "bench/dm/_convergence.py" in (v.get("files") or []), v


def test_gate_refuses_an_untested_code_change_named_through_a_variable(tmp_path):
    """THE REGRESSION THIS FILE EXISTS FOR. Before `classify_write`, the write below
    was dropped, the turn read as no-work, and the gate allowed the stop in silence."""
    cmd = 'D=bench/dm; cat > $D/_convergence.py <<EOF\nprint(1)\nEOF'
    t = write_jsonl(tmp_path / "t.jsonl", [entry_human(), entry_tool("Bash", {"command": cmd})])
    v = verdict_of(t)
    assert v is not None and v["is_work"], "turn did not open or recorded no work"
    assert v["code"], f"the variable-named code write was evaded: {v}"
    r = run_gate(t)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "ANALYSE" in r.stderr and "P-PASS" in r.stderr, r.stderr


def test_gate_does_not_refuse_a_scratchpad_only_turn(tmp_path):
    """The false positive that prompted the whole 2026-09-24 change must STAY fixed.
    This is the anti-regression on the other side, and it is why the repair had to be
    resolution rather than counting."""
    cmd = 'SP=/tmp/sp.$$; mkdir -p $SP; echo "{}" > $SP/gate_in.json'
    t = write_jsonl(tmp_path / "t.jsonl", [entry_human(), entry_tool("Bash", {"command": cmd})])
    v = verdict_of(t)
    assert v is not None, "no turn opened: the fixture is vacuous"
    assert not v["code"], f"scratchpad write was treated as code: {v}"
    assert run_gate(t).returncode == 0


def test_gate_allows_a_code_change_that_did_leave_traces(tmp_path):
    """ANTI-VACUITY for the refusal test: the gate must be capable of BOTH answers on
    a turn that changed code, or `returncode == 2` above proves nothing."""
    t = write_jsonl(tmp_path / "t.jsonl", [
        entry_human(),
        entry_tool("Grep", {"pattern": "_convergence", "path": "bench"}),
        entry_tool("Edit", {"file_path": "bench/dm/_convergence.py",
                            "old_string": "a", "new_string": "b"}),
        entry_tool("Bash", {"command": "python3 -m pytest bench/tests/test_convergence.py -q"}),
    ])
    v = verdict_of(t)
    assert v is not None and v["code"], v
    r = run_gate(t)
    assert r.returncode == 0, (r.returncode, r.stderr)


def test_gate_never_traps_a_session(tmp_path):
    """Fail-open is load-bearing: a broken gate must not make a session unstoppable."""
    assert run_gate(tmp_path / "missing.jsonl").returncode == 0
    t = write_jsonl(tmp_path / "t.jsonl",
                    [entry_human(), entry_tool("Edit", {"file_path": "bench/dm/_convergence.py"})])
    assert run_gate(t, stop_hook_active=True).returncode == 0
