"""A rejected attempt's tool calls were destroyed by the attempt that replaced it.

Found by the cc2 seat on 2026-09-07, with an executed repro, hours after the
sink was wired into `confer_maths_panel_2026-09-05.dispatch` to fix a counter
that had read 0 by construction for every `claude_cli` seat ever dispatched.

The sink write sits INSIDE `call_claude_cli`'s retry loop and `write_text`
replaces rather than appends. So when `accept` rejected attempt 1 and attempt 2
succeeded, the seat record kept only attempt 2's calls.

THE BIAS RUNS THE WRONG WAY, which is what makes it worth a permanent test.
`accept_reply_or_work` rejects a SHORT reply that has no work beside it -- the
holding-note case it was built for. The attempt most likely to be rejected is
therefore the one that spent its clock running tools and then ran short. The
erased attempt is systematically the busiest one, so the loss is not noise: it
biases the record toward under-reporting exactly the tool use the counter exists
to evidence.
"""
from __future__ import annotations

import json
import pathlib
import sys
import types

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import experiment_11_orchestrator as orch  # noqa: E402


def _stream(n_calls: int, final: str) -> str:
    """A stream-json transcript with `n_calls` tool_use blocks."""
    lines = []
    for i in range(n_calls):
        lines.append(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": f"echo {i}"}}]}}))
    lines.append(json.dumps({"type": "result", "result": final}))
    return "\n".join(lines)


def _install(monkeypatch, transcripts):
    """subprocess.run returns each transcript in turn."""
    seq = list(transcripts)

    def fake_run(cmd, **kw):
        return types.SimpleNamespace(returncode=0, stdout=seq.pop(0), stderr="")

    monkeypatch.setattr(orch.subprocess, "run", fake_run)
    monkeypatch.setattr(orch, "CLAUDE_CLI", "/bin/true", raising=False)


def test_a_rejected_attempts_tool_calls_are_kept(tmp_path, monkeypatch):
    sink = tmp_path / "seat.tools.json"
    orch.set_tool_log_sink(str(sink))
    try:
        _install(monkeypatch, [_stream(7, "short"), _stream(2, "a full verdict")])
        # attempt 1 is rejected the way accept_reply_or_work rejects a holding note
        rejects = {"short"}
        out = orch.call_claude_cli(
            "opus", None, "brief", max_retries=2, backoff_base=0,
            accept=lambda t: "holding note" if t in rejects else None,
        )
    finally:
        orch.set_tool_log_sink(None)

    assert out == "a full verdict"
    rec = json.loads(sink.read_text())
    assert rec["tool_calls"] == 9, (
        f"the record kept {rec['tool_calls']} calls; the seat made 7 on the "
        f"rejected attempt and 2 on the accepted one. The rejected attempt's "
        f"work was erased -- the defect this test exists for."
    )
    assert len(rec["calls"]) == 9
    assert rec["attempts"] == 2
    assert [a["tool_calls"] for a in rec["per_attempt"]] == [7, 2], rec["per_attempt"]


def test_a_single_accepted_attempt_is_unchanged(tmp_path, monkeypatch):
    """The fix must not inflate the ordinary case."""
    sink = tmp_path / "seat.tools.json"
    orch.set_tool_log_sink(str(sink))
    try:
        _install(monkeypatch, [_stream(4, "a full verdict")])
        orch.call_claude_cli("opus", None, "brief", max_retries=2, backoff_base=0)
    finally:
        orch.set_tool_log_sink(None)
    rec = json.loads(sink.read_text())
    assert rec["tool_calls"] == 4 and rec["attempts"] == 1


def test_no_sink_means_no_file_and_no_crash(tmp_path, monkeypatch):
    """With no sink the CLI stays on --output-format text; nothing is written."""
    _install(monkeypatch, ["a full verdict"])
    orch.set_tool_log_sink(None)
    out = orch.call_claude_cli("opus", None, "brief", max_retries=1, backoff_base=0)
    assert out == "a full verdict"
    assert not list(tmp_path.glob("*.json"))


# ---------------------------------------------------------------------------
# THE FIX ITSELF WAS UNGUARDED. Added 2026-09-08 after a panel seat mutation-
# tested it: replacing `set_tool_log_sink(str(_sink))` with
# `set_tool_log_sink(None)` in the dispatcher restores the original "0 by
# construction" defect exactly, and 88 of 88 relevant tests still passed. An
# addition that nothing can fail on is not guarded, it is merely present --
# the additive standard's own symmetric clause, violated inside the repair.
# ---------------------------------------------------------------------------
import sys as _sys


def _load_dispatcher(tmp_path):
    """Import the panel dispatcher without dispatching anything."""
    import importlib.util

    repo = REPO
    path = repo / "bench" / "confer_maths_panel_2026-09-05.py"
    logs = repo / "bench" / "logs" / "_toollog_probe"
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "BRIEF.md").write_text("# probe\n", encoding="utf-8")
    # THE BINDING MOVED OUT OF IMPORT TIME (task A22, 2026-09-11). This used to
    # work by setting `sys.argv` and letting the module read it AS IT IMPORTED --
    # which is precisely the import-time side effect A22 removed, so that
    # anything could import the dispatcher at all. `resolve_brief()` is the
    # binding now, and it is called explicitly here.
    #
    # WHAT THE MOVE COST, and it is worth recording: the first version of A22
    # left the module-level `LOGS` as None and code reached it through a bare
    # `LOGS / name`, producing `TypeError: unsupported operand type(s) for /:
    # 'NoneType' and 'str'` -- a message that says nothing about what to do.
    # This test and its sibling found it within the hour. Every such use now
    # goes through `_logs_dir()`, which raises a sentence naming the remedy.
    spec = importlib.util.spec_from_file_location("_toollog_probe_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.resolve_brief(["confer_maths_panel", "_toollog_probe"])
    return mod, logs


def _cleanup(logs):
    for p in sorted(logs.glob("*")):
        p.unlink(missing_ok=True)
    try:
        logs.rmdir()
    except OSError:
        pass


def test_the_dispatcher_actually_arms_the_sink(tmp_path, monkeypatch):
    """Mutating the arming call to None must fail this test.

    Without this, `set_tool_log_sink(str(_sink))` could be deleted and every
    Claude-route seat would silently return to n_tool_calls == 0.
    """
    mod, logs = _load_dispatcher(tmp_path)
    try:
        armed = []
        monkeypatch.setattr(mod, "set_tool_log_sink", lambda p: armed.append(p))

        def fake_cli(model_id, system, prompt, **kw):
            # a real dispatch writes the sink from inside the orchestrator
            (logs / "cc2.tools.json").write_text(
                json.dumps({"model": model_id, "tool_calls": 3,
                            "calls": [{"name": "Bash"}] * 3}), encoding="utf-8")
            return "a full verdict"

        monkeypatch.setattr(mod, "call_claude_cli", fake_cli)
        monkeypatch.setattr(mod, "accept_reply_or_work", lambda _p: (lambda _t: None))
        out = mod.dispatch("cc2", "opus", "claude_cli")

        assert any(a for a in armed if a), (
            "the dispatcher never armed the tool-log sink with a path. Without it "
            "the CLI runs with --output-format text, no tool_use blocks are "
            "emitted, and n_tool_calls is 0 for every Claude seat by construction")
        assert out["n_tool_calls"] == 3, (
            f"sink held 3 calls but the seat record says {out['n_tool_calls']}")
    finally:
        _cleanup(logs)


def test_a_seat_that_CRASHES_still_reports_the_calls_it_made(tmp_path, monkeypatch):
    """The counter read 0 exactly when a seat failed.

    `tool_log` is assigned only after `call_claude_cli` RETURNS, so when it
    raised -- timeout, all attempts rejected, vanished cwd -- the except arm
    recorded n_tool_calls=0 while the sink on disk held the real count. That is
    the case the panel actually hit on 2026-09-06 and 2026-09-07, so the
    original defect survived in the branch where the evidence matters most.
    """
    mod, logs = _load_dispatcher(tmp_path)
    try:
        monkeypatch.setattr(mod, "set_tool_log_sink", lambda p: None)

        def crashing_cli(model_id, system, prompt, **kw):
            (logs / "cc2.tools.json").write_text(
                json.dumps({"model": model_id, "tool_calls": 13,
                            "calls": [{"name": "Bash"}] * 13}), encoding="utf-8")
            raise TimeoutError("seat ran out of clock after doing real work")

        monkeypatch.setattr(mod, "call_claude_cli", crashing_cli)
        monkeypatch.setattr(mod, "accept_reply_or_work", lambda _p: (lambda _t: None))
        out = mod.dispatch("cc2", "opus", "claude_cli")

        assert out["ok"] is False and "TimeoutError" in out.get("error", "")
        assert out["n_tool_calls"] == 13, (
            f"a crashed seat reported {out['n_tool_calls']} tool calls; the sink "
            f"on disk held 13. The counter must not read 0 precisely when a seat "
            f"fails -- that is the case the evidence is most needed for")
    finally:
        _cleanup(logs)
