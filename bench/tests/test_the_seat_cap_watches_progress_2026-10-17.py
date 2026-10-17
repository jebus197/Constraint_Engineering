#!/usr/bin/env python3
"""The seat dispatch consumes stream-json incrementally, so progress is visible.

HIS RULING, 2026-10-08: *"clearly the cap doesn't need to be arbitrary, at 900,
or 1800, or however many seconds. We can tell the models to print 'I am done' at
the end of all their outputs, then watch for this signal in their output logs.
Or perhaps there is a better way to do this?"* And on 2026-10-11, after an
adjustable cap had been built instead: *"I also asked if there was better way.
You said there was. I can't remember what that better way was, but you should
try to recover it and to see if your way really is the better option. If so this
is the option you should implement."*

THE BETTER WAY, RECOVERED from `experimental_notes/What_Was_Actually_Implemented_2026-10-11.md`
and then VERIFIED rather than restated: incremental stream-json parsing. It
dominates a completion marker on a named property, which is what the additive
standard requires before choosing between two mechanisms.

  * A COMPLETION MARKER separates "printed" from "not printed", and a dead seat
    never prints it either -- so it cannot tell finished from died.
  * THE CLOCK separates nothing. Measured by
    `scripts/the_cap_was_measured_on_censored_data_2026-10-08.py`: a degraded
    attempt issued 88 tool calls at 20.455 s per call and never converged; a
    healthy one converged in 49 at 20.816 s per call; a third ran at 15.024 s
    per call. A spread of 5.792 s across all 3. The RATE is stable whether a
    seat works or churns; only the COUNT differs.
  * A LIVE CALL COUNT separates all 3 states: working, churning, dead.

WHY IT IS BUILT BEFORE THE BOUND IS SET. All 135 archived per-attempt records
carry a total count and a total elapsed, and NOT ONE carries a time per call. So
the inter-call gap distribution -- the thing a non-arbitrary stall bound has to
be derived from -- is unmeasurable today. This produces that data.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import textwrap

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiment_11_orchestrator as O  # noqa: E402


def _events(n_calls: int, final: str = "DONE") -> str:
    lines = []
    for i in range(n_calls):
        lines.append(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": f"step {i}"}}]}}))
    lines.append(json.dumps({"type": "result", "result": final}))
    return "\n".join(lines) + "\n"


def _fake_cli(tmp_path: pathlib.Path, body: str) -> list:
    """A stand-in for the CLI that emits stream-json lines on a schedule."""
    script = tmp_path / "fake_cli.py"
    script.write_text(body, encoding="utf-8")
    return [sys.executable, str(script)]


# --------------------------------------------------------------- the parser

def test_the_per_line_rule_and_the_whole_capture_agree():
    """ONE expression of the parsing rule, checked by running both forms.

    `_parse_stream_json` now loops over `_stream_json_line`. If someone
    re-spells either, these two counts part company -- which is the drift that
    broke an exemption set in the note linter when one rule had 2 spellings.
    """
    raw = _events(7, final="FINAL")
    whole_text, whole_calls = O._parse_stream_json(raw)
    per_line_calls, per_line_text = [], ""
    for line in raw.splitlines():
        txt, cs = O._stream_json_line(line)
        per_line_calls.extend(cs)
        if txt:
            per_line_text = txt
    assert len(whole_calls) == len(per_line_calls) == 7
    assert whole_text == per_line_text == "FINAL"


def test_a_malformed_line_is_skipped_not_fatal():
    raw = "not json\n" + _events(2)
    text, calls = O._parse_stream_json(raw)
    assert len(calls) == 2 and text == "DONE"


# ------------------------------------------------------- incremental capture

def test_it_returns_what_subprocess_run_would_on_success(tmp_path):
    body = textwrap.dedent(f'''
        import sys
        sys.stdin.read()
        sys.stdout.write({_events(4)!r})
        ''')
    cmd = _fake_cli(tmp_path, body)
    r = O._run_cli_incrementally(cmd, "prompt", 60, None, os.environ.copy())
    assert r.returncode == 0
    text, calls = O._parse_stream_json(r.stdout)
    assert len(calls) == 4 and text == "DONE"


def test_every_call_carries_an_arrival_time(tmp_path):
    """The data that does not exist anywhere in the archive today."""
    body = textwrap.dedent(f'''
        import sys, time
        sys.stdin.read()
        for line in {_events(3)!r}.splitlines():
            sys.stdout.write(line + "\\n"); sys.stdout.flush(); time.sleep(0.05)
        ''')
    cmd = _fake_cli(tmp_path, body)
    r = O._run_cli_incrementally(cmd, "p", 60, None, os.environ.copy())
    timed = r._cdsfl_timed_calls
    assert len(timed) == 3, timed
    assert all("t_offset_s" in c for c in timed), timed
    offs = [c["t_offset_s"] for c in timed]
    assert offs == sorted(offs), f"arrival times are not monotonic: {offs}"
    assert offs[-1] > 0, "every call arrived at offset 0, so nothing was timed"


def test_the_count_is_observable_before_the_process_exits(tmp_path):
    """THE WHOLE POINT. `subprocess.run` cannot do this at all."""
    body = textwrap.dedent(f'''
        import sys, time
        sys.stdin.read()
        for line in {_events(5)!r}.splitlines():
            sys.stdout.write(line + "\\n"); sys.stdout.flush(); time.sleep(0.08)
        ''')
    seen = []
    cmd = _fake_cli(tmp_path, body)
    O._run_cli_incrementally(cmd, "p", 60, None, os.environ.copy(),
                             on_call=lambda c, n: seen.append(n))
    assert seen == [1, 2, 3, 4, 5], (
        f"the progress hook saw {seen}; a mid-flight count is what separates a "
        f"working seat from a churning one")


def test_a_progress_hook_that_raises_cannot_kill_the_dispatch(tmp_path):
    body = textwrap.dedent(f'''
        import sys
        sys.stdin.read()
        sys.stdout.write({_events(3)!r})
        ''')
    cmd = _fake_cli(tmp_path, body)

    def _boom(c, n):
        raise RuntimeError("a progress hook exploded")

    r = O._run_cli_incrementally(cmd, "p", 60, None, os.environ.copy(),
                                 on_call=_boom)
    assert r.returncode == 0
    assert len(O._parse_stream_json(r.stdout)[1]) == 3


# ------------------------------------------------- the timeout keeps the work

def test_a_timeout_preserves_what_had_already_arrived(tmp_path):
    """THE RECORDED DEFECT: 1800 s for 0 words, because nothing was kept.

    `subprocess.run(capture_output=True)` discards its output when it raises,
    and the old handler never read `e.output` either. So a killed attempt left
    no trace of how far the seat had got.
    """
    body = textwrap.dedent(f'''
        import sys, time
        sys.stdin.read()
        for line in {_events(3)!r}.splitlines()[:3]:
            sys.stdout.write(line + "\\n"); sys.stdout.flush()
        time.sleep(30)
        ''')
    cmd = _fake_cli(tmp_path, body)
    with pytest.raises(subprocess.TimeoutExpired) as e:
        O._run_cli_incrementally(cmd, "p", 1.5, None, os.environ.copy())
    partial = e.value.output or ""
    assert partial, "the timeout discarded everything the seat had produced"
    _, calls = O._parse_stream_json(partial)
    assert len(calls) == 3, (
        f"{len(calls)} call(s) recovered from the partial capture; the seat had "
        f"issued 3 before it was killed, and that count is what says it was "
        f"WORKING rather than dead")


def test_the_timeout_still_raises_the_type_the_caller_handles(tmp_path):
    """Strictly additive: the retry path must be unchanged."""
    body = "import sys, time\nsys.stdin.read()\ntime.sleep(30)\n"
    cmd = _fake_cli(tmp_path, body)
    with pytest.raises(subprocess.TimeoutExpired):
        O._run_cli_incrementally(cmd, "p", 1.0, None, os.environ.copy())


def test_the_text_path_is_untouched():
    """It is used only where stream-json is already asked for.

    Parsed rather than grepped: the call to `subprocess.run` must still be
    present in the dispatch, guarded by the sink check, so a run WITHOUT a sink
    behaves exactly as before.
    """
    import ast
    src = (REPO / "bench" / "experiment_11_orchestrator.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    incremental, plain = 0, 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "_run_cli_incrementally":
            incremental += 1
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "run" \
                and isinstance(node.func.value, ast.Name) \
                and node.func.value.id == "subprocess":
            plain += 1
    assert incremental >= 1, "the incremental path is not called at all"
    assert plain >= 1, (
        "subprocess.run has gone entirely; the text path must keep it so a "
        "dispatch without a tool-log sink behaves exactly as before")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
