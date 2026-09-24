"""Guard for the 2026-09-22 defect: the FFAFP detector died silently for 2 days.

WHAT DIED, AND HOW IT WAS ESTABLISHED. The hook persists `state["open"]` -- an
in-flight turn -- as JSON between prompts. `new_turn()` gained a `"scans"` key when
the hook was rewritten on 2026-09-20 16:42. The state file written at 15:33 that day
held a turn WITHOUT that key. On the next prompt `record_tool` evaluated
`turn["scans"]` and raised KeyError on the first tool line it saw. Because `scan()`
assigns `state["offset"] = fh.tell()` on its LAST line, the abort left the offset
unchanged; `main()`'s bare `except` swallowed the traceback; the state was rewritten
with the SAME offset. Every subsequent prompt replayed the same bytes and died in the
same place. Replayed against the live state file the failure is deterministic:

    File "ffafp_audit.py", line 496, in record_tool
      if _TREE_SCAN.search(cmd) and len(turn["scans"]) < SEARCH_CAP:
    KeyError: 'scans'

    offset before 170431649 after 170431649

WHY 67 PASSING TESTS DID NOT CATCH IT. Every one of them builds turns through
`new_turn()`, so every turn they test has the current key set. The only input that
triggers this is a turn serialised by an OLDER BUILD, which no test supplied. The gap
was in the INPUT SPACE, not in the assertions.

WHY THE SECOND HALF OF THIS FILE TESTS THE INSTRUMENT AND NOT THE VERDICT. A detector
reporting "nothing missing" because it is dead is indistinguishable, downstream, from
one reporting "nothing missing" because nothing was missing -- the same false negative
this project recorded when 16 of 17 panel tool calls errored and were read as results.
The two differ in exactly one mechanically checkable way: a live detector's byte offset
ADVANCES when the transcript grows. `test_liveness_*` asserts that, and asserts the
alarm is LOUD, because a silent recovery would reproduce the original defect one level
up. The poison used there is NOT the schema one -- it is a `reads` list where a dict
belongs -- precisely so the liveness check is shown to catch a fault the migration
cannot foresee.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

HOOK = pathlib.Path.home() / ".claude" / "hooks" / "ffafp_audit.py"
REPO_HOOK = pathlib.Path(__file__).resolve().parents[2] / "hooks" / "ffafp_audit.py"
SRC = REPO_HOOK if REPO_HOOK.is_file() else HOOK
if not SRC.is_file():                                        # pragma: no cover
    pytest.skip("ffafp_audit.py not present", allow_module_level=True)

_spec = importlib.util.spec_from_file_location("ffafp_mig", SRC)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

#: The exact key set the live state file held on 2026-09-20, read from disk.
LEGACY_KEYS = ["failable_idx", "first_mut", "id", "last_mut", "mutations", "n_tools",
               "prompt", "read_paths", "searches", "stem", "test_idx", "ts"]


def legacy_turn() -> dict:
    t = mod.new_turn("u1", "2026-09-20T15:33:07.152Z", "p")
    return {k: v for k, v in t.items() if k in LEGACY_KEYS}


def test_the_legacy_turn_really_is_the_poison():
    """The two forms must DISAGREE, or this file proves nothing.

    An unmigrated legacy turn must raise where a migrated one must not. If both
    survived, the migration would be inert and this suite would pass on a hook with
    the defect still in it.
    """
    call = ("Bash", {"command": "rg -n 'sympy' bench/"})
    with pytest.raises(KeyError):
        mod.record_tool(legacy_turn(), *call)
    mod.record_tool(mod.migrate_turn(legacy_turn()), *call)     # must not raise


def test_migrate_turn_backfills_every_current_key_and_keeps_recorded_data():
    t = legacy_turn()
    t["n_tools"] = 7
    t["mutations"] = ["bench/x.py"]
    out = mod.migrate_turn(t)
    assert set(out) == set(mod.new_turn())
    assert out["n_tools"] == 7 and out["mutations"] == ["bench/x.py"]
    assert mod.migrate_turn(None) is None


def test_scan_over_a_legacy_state_advances_the_offset(tmp_path):
    """The whole defect in one assertion: the offset must MOVE."""
    tr = tmp_path / "t.jsonl"
    tr.write_text("\n".join([
        json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash",
             "input": {"command": "rg -n 'sympy' bench/"}}]}}),
        json.dumps({"type": "user", "origin": {"kind": "human"}, "uuid": "u2",
                    "timestamp": "2026-09-22T10:00:00.000Z",
                    "message": {"content": "next"}}),
    ]) + "\n")
    state = {"offset": 0, "open": mod.migrate_turn(legacy_turn()), "seq": 1,
             "reads": {}, "last_work": None, "reported": None, "history": []}
    with tr.open("r", errors="ignore") as fh:
        mod.scan(fh, state)
    assert state["offset"] == tr.stat().st_size


def _run_hook(tmp_path, transcript, state, env_extra=None):
    sdir = tmp_path / "state"
    sdir.mkdir(exist_ok=True)
    (sdir / "sess").write_text(json.dumps(state))
    env = {"FFAFP_AUDIT_STATE_DIR": str(sdir), "PATH": "/usr/bin:/bin",
           "HOME": str(pathlib.Path.home())}
    env.update(env_extra or {})
    proc = subprocess.run(
        [sys.executable, str(SRC)],
        input=json.dumps({"session_id": "sess", "transcript_path": str(transcript),
                          "hook_event_name": "UserPromptSubmit"}),
        capture_output=True, text=True, env=env, timeout=60)
    return proc, json.loads((sdir / "sess").read_text()), sdir


def _transcript(tmp_path) -> pathlib.Path:
    tr = tmp_path / "live.jsonl"
    tr.write_text("\n".join([
        json.dumps({"type": "user", "origin": {"kind": "human"}, "uuid": "u9",
                    "timestamp": "2026-09-22T11:00:00.000Z",
                    "message": {"content": "do the thing"}}),
        json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Edit",
             "input": {"file_path": "bench/x.py", "old_string": "a",
                       "new_string": "b"}}]}}),
    ]) + "\n")
    return tr


def test_liveness_alarms_and_rearms_on_a_poison_migration_cannot_foresee(tmp_path):
    """`reads` as a list breaks close_turn with TypeError -- nothing to do with schema.

    Invocation 1 stalls quietly (a single replay can be a flush race). Invocation 2
    must declare the detector dead, re-arm at end of file, and SAY SO on stdout.
    """
    tr = _transcript(tmp_path)
    open_turn = mod.new_turn("u0", "2026-09-20T15:33:07Z", "p")
    open_turn["read_paths"] = ["bench/x.py"]     # close_turn folds these INTO `reads`
    poisoned = {"offset": 0, "open": open_turn,
                "seq": 1, "reads": [], "last_work": None, "reported": None,
                "history": [], "aligned": True}

    proc1, st1, sdir = _run_hook(tmp_path, tr, poisoned)
    assert proc1.returncode == 0
    assert st1["offset"] == 0, "the stall must be real, or the test is vacuous"
    assert st1["stall"] == 1 and "TypeError" in st1["last_error"]
    assert "DETECTOR ITSELF WAS DEAD" not in proc1.stdout, "one stall is not a ratchet"

    proc2, st2, _ = _run_hook(tmp_path, tr, st1)
    assert proc2.returncode == 0
    assert st2["offset"] == tr.stat().st_size, "must re-arm at end of file"
    assert st2["recovered"] == 1 and st2["stall"] == 0
    assert "DETECTOR ITSELF WAS DEAD" in proc2.stdout
    assert json.loads(proc2.stdout)["suppressOutput"] is False, "an alarm is never silent"


def test_liveness_is_silent_when_the_detector_is_healthy(tmp_path):
    """The other half of the false-negative pair: a HEALTHY run must not alarm.

    Without this, an alarm that fired unconditionally would pass the test above.
    """
    tr = _transcript(tmp_path)
    clean = {"offset": 0, "open": None, "seq": 0, "reads": {}, "last_work": None,
             "reported": None, "history": [], "aligned": True}
    proc, st, _ = _run_hook(tmp_path, tr, clean)
    assert proc.returncode == 0
    assert st["offset"] == tr.stat().st_size
    assert st.get("stall", 0) == 0 and not st.get("last_error")
    assert st.get("recovered", 0) == 0
    assert "DETECTOR ITSELF WAS DEAD" not in proc.stdout


def test_end_to_end_the_unfixed_hook_freezes_and_the_fixed_one_does_not(tmp_path):
    """The defect and the fix in one comparison, driven as the harness drives it.

    The ordering matters and is the real one: the open turn's tool calls stream BEFORE
    the next human prompt, so `record_tool` reaches the legacy turn first. Measured on
    the live state file, the unfixed hook held offset 170431649 across 2 days; measured
    here it holds offset 0 across 3 invocations, exit 0 every time, history empty. The
    test is skipped rather than failed when no unfixed copy is around to compare with,
    because its value is the DISAGREEMENT and an absent baseline proves nothing.
    """
    installed = HOOK
    if not installed.is_file() or installed.resolve() == SRC.resolve():
        pytest.skip("no separate installed copy to compare against")
    legacy = legacy_turn()
    tr = tmp_path / "e2e.jsonl"
    tr.write_text("\n".join([
        json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash",
             "input": {"command": "rg -n 'sympy' bench/"}}]}}),
        json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Edit",
             "input": {"file_path": "bench/x.py", "old_string": "a",
                       "new_string": "b"}}]}}),
        json.dumps({"type": "user", "origin": {"kind": "human"}, "uuid": "u9",
                    "timestamp": "2026-09-22T11:00:00.000Z",
                    "message": {"content": "go"}}),
    ]) + "\n")

    def drive(hook_path, tag):
        sdir = tmp_path / ("sd_" + tag)
        sdir.mkdir()
        st = json.loads(json.dumps(
            {"offset": 0, "open": legacy, "seq": 1, "reads": {}, "last_work": None,
             "reported": None, "history": [], "aligned": True}))
        for _ in range(3):
            (sdir / "sess").write_text(json.dumps(st))
            proc = subprocess.run(
                [sys.executable, str(hook_path)],
                input=json.dumps({"session_id": "sess", "transcript_path": str(tr),
                                  "hook_event_name": "UserPromptSubmit"}),
                capture_output=True, text=True, timeout=60,
                env={"FFAFP_AUDIT_STATE_DIR": str(sdir), "PATH": "/usr/bin:/bin",
                     "HOME": str(pathlib.Path.home())})
            assert proc.returncode == 0, "the hook must never fail the prompt"
            st = json.loads((sdir / "sess").read_text())
        return st

    if not hasattr(_load(installed), "migrate_turn"):
        old = drive(installed, "old")
        assert old["offset"] == 0, "baseline must actually be frozen"
        assert old["history"] == []
    new = drive(SRC, "new")
    assert new["offset"] == tr.stat().st_size
    assert len(new["history"]) == 1


def _load(path):
    spec = importlib.util.spec_from_file_location("ffafp_probe_" + path.stem, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_liveness_script_runs_and_reports_stale_for_a_stale_state(tmp_path):
    """The ADDITIVE check: the new script has a caller, and this is it.

    A script nothing reaches is not an addition. This executes it end to end and
    asserts both branches of its exit code exist as behaviour, not as prose.
    """
    script = pathlib.Path(__file__).resolve().parents[2] / "scripts" / \
        "ffafp_liveness_check_2026-09-22.py"
    assert script.is_file(), "the fix must be delivered at its real repository path"
    proc = subprocess.run([sys.executable, str(script), "no-such-session"],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 1
    assert "no transcript found" in proc.stdout
