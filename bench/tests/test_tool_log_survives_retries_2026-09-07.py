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
