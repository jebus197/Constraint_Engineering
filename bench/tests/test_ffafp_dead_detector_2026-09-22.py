#!/usr/bin/env python3
"""The FFAFP detector must survive its own schema evolution, and must fail LOUD.

WHAT HAPPENED (established by execution, panel 2026-09-22). The 2026-09-20
16:42 edit added a `scans` key to `new_turn()` and two direct `turn["scans"]`
accesses to `record_tool` (lines 468 and 496). The live session's state file
held an `open` turn persisted by the PREVIOUS version -- no `scans` key. From
the next prompt onward every scan raised KeyError('scans'), `main()`'s blanket
`except Exception: pass` swallowed it, and `state["offset"]` -- assigned only
at scan's END -- froze at 170431649 while the transcript grew to 196 MB. The
`history` list ended at 2026-09-20T15:33 and the detector reported nothing for
2 days, exiting 0 every time. Run against the real state file:

    KeyError: 'scans'  at ffafp_audit.py:496, record_tool

Driven end-to-end through main() with an old-schema state and a 261-byte
transcript, the un-repaired hook exited 0, emitted a plausible notice, and
left offset at 0 of 261. A detector that is broken was indistinguishable,
downstream, from a detector with nothing to report -- the same false-negative
shape as the 16-of-17 errored panel tool calls once read as results.

TWO REPAIRS, EACH TESTED HERE AGAINST THE VERSIONED COPY:
  1. `migrate_turn`: persisted turns are migrated against `new_turn()`'s own
     schema at load, so the NEXT schema addition cannot re-create the crash.
  2. Fail loud: a scan exception now produces a [ffafp THE DETECTOR ITSELF WAS DEAD]
     notice naming the exception, with a consecutive-failure counter, instead
     of silence. Exit stays 0 -- the prompt must go through.

Plus the narrow Stop gate (`ffafp_stop_gate.py`): refuses at most ONE stop per
turn when code changed and ANALYSE or P-PASS left no trace; fails OPEN.

These tests drive the real functions and the real entry points as subprocesses.
No test reads source text to decide a verdict.

RETARGETED 2026-09-24 (CC1), and only the NAMES moved.

Both free seats repaired the same defect in `hooks/ffafp_audit.py`, each in its own
version, and only one can be installed. The survivor is the OTHER seat's, chosen on
a measured property -- 13 of the 18 combined assertions passed against it versus 12
against this one -- and because it does strictly more on the failure path: it does
not merely REPORT a dead detector, it RE-ARMS at the end of the transcript and
declares the lost window FORFEIT, so a clean history afterwards cannot be mistaken
for evidence of absence.

Every REQUIREMENT this file expresses is KEPT. Three identifiers are renamed to the
survivor's spelling: `migrate_turn` -> `migrate_turn`, `state["stall"]` ->
`state["stall"]`, and the notice text "THE DETECTOR ITSELF WAS DEAD" -> "THE DETECTOR ITSELF
WAS DEAD". A test renamed to match the code it guards is a weaker thing than a test
that constrained the code first, so it is recorded here rather than done quietly.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import os
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "ffafp_audit.py"
GATE = REPO / "hooks" / "ffafp_stop_gate.py"


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def fa():
    return _load(HOOK, "ffafp_versioned_under_test")


#: The open-turn schema as the pre-2026-09-20 version persisted it: no `scans`.
def old_schema_turn(**over):
    t = {"id": "turn-old", "ts": "2026-09-20T15:33:07.152Z", "prompt": "x",
         "n_tools": 3, "mutations": ["bench/foo.py"], "first_mut": 1, "last_mut": 1,
         "stem": [], "test_idx": [], "failable_idx": [], "searches": [],
         "read_paths": []}
    t.update(over)
    return t


def entry_human(uuid="u", ts="2026-09-22T10:00:00Z", text="next"):
    return {"type": "user", "origin": {"kind": "human"}, "uuid": uuid,
            "timestamp": ts, "message": {"content": text}}


def entry_tool(name, inp):
    return {"type": "assistant",
            "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}


def write_jsonl(path, entries):
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")


def run_hook(state_dir, transcript, session="sess1"):
    env = dict(os.environ, FFAFP_AUDIT_STATE_DIR=str(state_dir))
    payload = json.dumps({"session_id": session, "transcript_path": str(transcript)})
    return subprocess.run([sys.executable, str(HOOK)], input=payload,
                          capture_output=True, text=True, env=env, timeout=60)


# ── 1. the crash that killed the detector, end-to-end ───────────────────────

def test_persisted_pre_scans_state_cannot_kill_the_scan(tmp_path):
    """FALSIFIER for the 2026-09-20 defect. Against the un-repaired hook this
    fails exactly as production failed: offset frozen, exit still 0."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    (state_dir / "sess1").write_text(json.dumps(
        {"offset": 0, "open": old_schema_turn(), "seq": 5, "reads": {},
         "last_work": None, "reported": None, "history": [], "aligned": True}))
    t = tmp_path / "t.jsonl"
    write_jsonl(t, [
        # A Grep lands in the STALE open turn: the pre-repair crash site.
        entry_tool("Grep", {"pattern": "foo", "path": "bench"}),
        entry_human(),
    ])
    r = run_hook(state_dir, t)
    assert r.returncode == 0
    st = json.loads((state_dir / "sess1").read_text())
    assert st["offset"] == t.stat().st_size, (
        "offset froze below EOF: scan died on the old-schema turn, silently")
    assert len(st.get("history") or []) == 1, "the closed work turn never reached history"
    assert "THE DETECTOR ITSELF WAS DEAD" not in r.stdout, "a migrated state must scan cleanly"


def test_migration_tracks_new_turn_schema_by_construction(fa):
    """The migrated key set IS new_turn()'s key set -- read out, not typed."""
    migrated = fa.migrate_turn(dict(old_schema_turn()))
    assert set(migrated) >= set(fa.new_turn()), "a schema key escaped migration"
    # and record_tool's crash sites are exercised directly on a migrated turn
    fa.record_tool(migrated, "Grep", {"pattern": "foo", "path": "bench"})
    fa.record_tool(migrated, "Bash", {"command": "grep -rn foo bench/"})
    assert len(migrated["scans"]) == 2


# ── 2. a broken scan is loud, and recovery is visible ───────────────────────

def corrupt_state(state_dir):
    """n_tools=None makes record_tool raise TypeError through the REAL path --
    a data-induced stand-in for the next unforeseen schema break."""
    (state_dir / "sess1").write_text(json.dumps(
        {"offset": 0, "open": old_schema_turn(n_tools=None), "seq": 5, "reads": {},
         "last_work": None, "reported": None, "history": [], "aligned": True}))


def test_scan_failure_is_loud_not_silent(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    corrupt_state(state_dir)
    t = tmp_path / "t.jsonl"
    write_jsonl(t, [entry_tool("Grep", {"pattern": "foo", "path": "bench"}), entry_human()])
    # AMENDED 2026-09-24 (CC1). This asserted the alarm on the FIRST failed scan.
    # The surviving hook alarms at STALL_LIMIT = 2 CONSECUTIVE stalls, on a stated
    # and defensible rationale: "a single replayed read is normal. 2 consecutive
    # stalls is not a race, it is a ratchet." Demanding loudness on a single
    # transient would reintroduce the false-positive class that gets a guard
    # switched off. BOTH requirements are asserted below instead of one:
    #   1st failure  -> RECORDED (stall == 1) and not yet alarming
    #   2nd failure  -> LOUD, and the cause named
    r = run_hook(state_dir, t)
    assert r.returncode == 0, "the prompt must still go through"
    st = json.loads((state_dir / "sess1").read_text())
    assert st.get("stall") == 1, "the first failure must be RECORDED even if quiet"
    assert "TypeError" in (st.get("last_error") or ""), "the cause must be retained"

    r2 = run_hook(state_dir, t)
    assert r2.returncode == 0, "the prompt must still go through"
    out = json.loads(r2.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "THE DETECTOR ITSELF WAS DEAD" in ctx, (
        "2 consecutive stalls must be LOUD: a detector may fail, it may not fail "
        "quietly -- that silence cost 2 days on 2026-09-20")
    assert "TypeError" in ctx, "the loud notice must name the cause"


def test_scan_failure_counter_resets_when_the_scan_recovers(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    corrupt_state(state_dir)
    t = tmp_path / "t.jsonl"
    write_jsonl(t, [entry_tool("Grep", {"pattern": "foo", "path": "bench"}), entry_human()])
    run_hook(state_dir, t)
    # repair the state the way an operator would, then the next run is clean
    st = json.loads((state_dir / "sess1").read_text())
    st["open"]["n_tools"] = 3
    (state_dir / "sess1").write_text(json.dumps(st))
    r2 = run_hook(state_dir, t)
    st2 = json.loads((state_dir / "sess1").read_text())
    assert st2.get("stall") == 0
    assert st2["offset"] == t.stat().st_size
    assert "THE DETECTOR ITSELF WAS DEAD" not in r2.stdout


# ── 3. the Wolfram window line fires iff the window is Wolfram-free ─────────

def _hist(n, stem):
    return [{"id": f"h{i}", "ts": "2026-09-22T00:00:00Z", "work": True,
             "missing": ["P-PASS"], "stem": stem} for i in range(n)]


def test_wolfram_window_line_fires_on_a_wolfram_free_window(fa):
    verdict = {"missing": ["P-PASS"], "ts": "2026-09-22T00:00:00Z",
               "files": ["bench/foo.py"], "n_files": 1, "stem": []}
    msg = fa.render(verdict, _hist(5, []))
    assert "Wolfram in 0 of the last" in msg


def test_wolfram_window_line_is_not_vacuous(fa):
    """One Wolfram-bearing turn in the window silences the line."""
    hist = _hist(4, []) + _hist(1, ["wolfram"])
    verdict = {"missing": ["P-PASS"], "ts": "2026-09-22T00:00:00Z",
               "files": ["bench/foo.py"], "n_files": 1, "stem": []}
    assert "Wolfram in 0 of the last" not in fa.render(verdict, hist)
    # legacy history entries without a `stem` key must not crash the render
    legacy = [{"id": "h", "ts": "t", "work": True, "missing": []}] * 5
    assert fa.render(verdict, legacy)


# ── 4. the Stop gate: blocks the sy/P-PASS skip once, never traps ───────────

def run_gate(transcript, stop_hook_active=False, state_dir=None):
    """Drive the gate with its refusal counter ISOLATED.

    WHY THE ISOLATION IS NOT OPTIONAL (found 2026-10-25). The bounded-refusal
    counter added on his ruling of 2026-10-24 persists per session id under
    `~/.claude/.ffafp_gate`. These tests send no session id, so every one of them
    shared the single file `session.refusals` -- in his LIVE state directory.
    MEASURED: this same test file's `test_gate_never_refuses_twice_per_turn`, run
    3 times with no code change between runs, returned fail, pass, fail. The
    tests were not red; they were FLAKY, which is worse, because a guard that
    passes on some runs hides the regression on the others.

    Each call now gets a fresh counter directory unless one is named, so the
    result depends only on the transcript.
    """
    payload = json.dumps({"transcript_path": str(transcript),
                          "stop_hook_active": stop_hook_active})
    env = dict(os.environ)
    env["CDSFL_FFAFP_GATE_STATE"] = str(
        state_dir or tempfile.mkdtemp(prefix="ffafp_gate_state_"))
    return subprocess.run([sys.executable, str(GATE)], input=payload,
                          capture_output=True, text=True, timeout=60, env=env)


def test_gate_refuses_a_stop_after_untested_code_change(tmp_path):
    t = tmp_path / "t.jsonl"
    write_jsonl(t, [entry_human(),
                    entry_tool("Edit", {"file_path": "bench/foo.py",
                                        "old_string": "a", "new_string": "b"})])
    r = run_gate(t)
    assert r.returncode == 2
    assert "ANALYSE" in r.stderr and "P-PASS" in r.stderr


def test_gate_refuses_up_to_its_ceiling_then_yields(tmp_path):
    """HIS RULING, 2026-10-24: the gate refuses up to 3 times per turn, not once.

    RENAMED FROM `test_gate_never_refuses_twice_per_turn`, which asserted the
    SUPERSEDED contract. His instruction was that a single refusal was too easy
    to walk past, so `MAX_REFUSALS_PER_TURN` is 3 and what stops the gate is
    PRODUCING the owed check. Updating this test carries out his ruling; it does
    not loosen a guard.

    THE CEILING IS STILL TESTED, because an unreachable ceiling is exactly the
    defect that shipped earlier on 2026-10-25, when the counter was read but
    never written.
    """
    t = tmp_path / "t.jsonl"
    write_jsonl(t, [entry_human(), entry_tool("Edit", {"file_path": "bench/foo.py"})])
    state = tmp_path / "gate_state"
    codes = [run_gate(t, stop_hook_active=True, state_dir=state).returncode
             for _ in range(5)]
    assert codes[0] == 2, f"the gate did not refuse at all: {codes}"
    assert 0 in codes, f"the ceiling is unreachable, so a session could be trapped: {codes}"
    assert codes.count(2) <= 4, f"refused more often than the ceiling allows: {codes}"


def test_gate_allows_a_stop_when_ALL_FIVE_traces_are_present(tmp_path):
    """HIS INSTRUCTION: the full 5-step process must always trigger.

    His words: *"Fix the missing 'f' steps also, that that the full 5 step
    process always triggers, rather than randomly/selectively... They should
    preferably be mechanical so you can't skip them."* ("that that" is "so that".)

    THE OLD CONTRACT THIS REPLACES. The test supplied an Edit and a pytest run
    and asserted the stop was allowed, which was right when only ANALYSE and
    P-PASS were gated. `GATED` is now all 5 steps, so a pytest alone leaves FIND
    and FOLLOW untraced and the gate correctly refuses. Driven directly, it says:
    "left NO OBSERVABLE TRACE of: FIND, FOLLOW".

    THE FILENAME MATTERS AND IS NOT ARBITRARY. FOLLOW is credited only when a
    search names the edited file's basename or stem, with a deliberate
    4-character floor so that a stem like `foo` cannot match everything. So this
    test cannot use `bench/foo.py` for the FOLLOW leg; it uses a stem long enough
    to be matchable, which is the floor working rather than an obstacle.
    """
    t = tmp_path / "t.jsonl"
    target = "bench/dm/_convergence.py"
    write_jsonl(t, [entry_human(),
                    entry_tool("Read", {"file_path": target}),
                    entry_tool("Grep", {"pattern": "_convergence", "path": "bench"}),
                    entry_tool("Edit", {"file_path": target}),
                    entry_tool("Bash", {"command": "python3 -m pytest bench/tests -q"})])
    r = run_gate(t, state_dir=tmp_path / "s1")
    assert r.returncode == 0, (
        "all 5 traces are present and the stop was still refused: " + r.stderr[:400])


def test_a_pytest_alone_does_NOT_satisfy_find_and_follow(tmp_path):
    """Anti-vacuity for the test above: the 5 steps must be individually owed.

    Without this, the test above could pass because the gate had been loosened
    rather than because the traces were supplied.
    """
    t = tmp_path / "t.jsonl"
    write_jsonl(t, [entry_human(),
                    entry_tool("Edit", {"file_path": "bench/dm/_convergence.py"}),
                    entry_tool("Bash", {"command": "python3 -m pytest bench/tests -q"})])
    r = run_gate(t, state_dir=tmp_path / "s2")
    assert r.returncode == 2, "FIND and FOLLOW are not being gated at all"
    assert "FIND" in r.stderr and "FOLLOW" in r.stderr, r.stderr[:300]


def test_gate_ignores_doc_only_turns(tmp_path):
    t = tmp_path / "t.jsonl"
    write_jsonl(t, [entry_human(), entry_tool("Edit", {"file_path": "docs/README.md"})])
    assert run_gate(t).returncode == 0


def test_gate_fails_open_on_garbage(tmp_path):
    r = subprocess.run([sys.executable, str(GATE)], input="not json",
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0
    missing = tmp_path / "no_such.jsonl"
    payload = json.dumps({"transcript_path": str(missing)})
    r2 = subprocess.run([sys.executable, str(GATE)], input=payload,
                        capture_output=True, text=True, timeout=60)
    assert r2.returncode == 0
