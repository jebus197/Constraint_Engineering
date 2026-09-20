#!/usr/bin/env python3
"""P-pass for the 2 fixes that recovered the ge and kimi seats, 2026-09-20.

Panel round 3 dispatched 7 seats and 2 returned nothing:
  * ge   -- 1 tool call, a 24,868-character read, then 0 characters, 'finish'.
  * kimi -- 25 successful tool calls over 216 seconds, then 0 characters.

Two DIFFERENT defects, both in code this project owns, neither detectable by
reading either file on its own.

DEFECT 1 (ge): bench/openrouter_tools.py treated empty visible content as a
finished answer. Its sibling loop `_run_openai_tool_loop` has carried a
tool-less retry for that case since 2026-06-06, written against the very model
that failed here. The paid seats run the loop WITHOUT the guard.

DEFECT 2 (kimi): `_run_openai_tool_loop`'s forced-synthesis call hardcoded
`temperature=0.0` while the loop's own `temperature` parameter -- added the same
day for kimi-k3, which refuses any value but 1 -- was threaded only into the
main request. Every forced-synthesis retry raised 400 and a bare `except`
swallowed it.

These tests drive fake clients whose behaviour is known by construction. A test
that asserted on the source text of either file would pass against both the
broken and the fixed version, which is why neither does.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------- fake client

class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, tid, name, arguments="{}"):
        self.id = tid
        self.function = FakeFunction(name, arguments)
        self.type = "function"

    def model_dump(self):
        return {"id": self.id, "type": "function",
                "function": {"name": self.function.name,
                             "arguments": self.function.arguments}}


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class FakeChoice:
    def __init__(self, message):
        self.message = message


class FakeResponse:
    def __init__(self, message):
        self.choices = [FakeChoice(message)]


class FakeCompletions:
    """Returns a scripted sequence; records every call's kwargs."""

    def __init__(self, script, reject_temperature=None):
        self.script = list(script)
        self.calls = []
        self.reject_temperature = reject_temperature

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if (self.reject_temperature is not None
                and kwargs.get("temperature") != self.reject_temperature):
            raise RuntimeError(
                f"400 invalid temperature: only {self.reject_temperature} is "
                f"allowed for this model")
        if not self.script:
            return FakeResponse(FakeMessage(content="fallback"))
        item = self.script.pop(0)
        return FakeResponse(item)


class FakeClient:
    def __init__(self, script, reject_temperature=None):
        self.chat = types.SimpleNamespace(
            completions=FakeCompletions(script, reject_temperature))


# =========================================================== DEFECT 1 (ge)

def _run_or_tools(monkeypatch, script, **kw):
    import bench.openrouter_tools as ot
    client = FakeClient(script)
    fake_openai = types.SimpleNamespace(OpenAI=lambda **_: client)
    monkeypatch.setitem(sys.modules, "openai", fake_openai)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(ot.time, "sleep", lambda *_: None)
    monkeypatch.setattr(ot, "_TOOL_DISPATCH", {"read_file": lambda a: "FILE BODY"},
                        raising=False)
    out = ot.call_openrouter_with_tools(
        model_id="google/gemini-3.1-pro-preview",
        system_prompt="sys", user_prompt="do the review",
        tools=[{"type": "function",
                "function": {"name": "read_file", "description": "d",
                             "parameters": {"type": "object", "properties": {}}}}],
        **kw)
    return out, client.chat.completions


def test_empty_content_is_retried_and_recovered(monkeypatch):
    """BREAK ATTEMPT: the exact ge sequence must no longer return 0 characters.

    Turn 1 asks for a tool. Turn 2 comes back with content=None, which is what
    ge actually did. The loop must NOT accept that as the answer.
    """
    script = [
        FakeMessage(tool_calls=[FakeToolCall("c1", "read_file")]),
        FakeMessage(content=None),                       # the ge failure
        FakeMessage(content="THE FULL REVIEW, recovered."),
    ]
    out, comp = _run_or_tools(monkeypatch, script)
    assert out["final_text"] == "THE FULL REVIEW, recovered.", out
    assert out["stopped_reason"] == "finish_after_empty_retry", out["stopped_reason"]
    # The retry must drop tools, or the model can just call another one.
    assert "tools" not in comp.calls[-1], "retry still offered tools"
    assert comp.calls[-1]["max_tokens"] >= 65536, "retry did not raise the budget"


def test_persistent_emptiness_is_reported_not_disguised_as_finish(monkeypatch):
    """BREAK ATTEMPT: a seat that says nothing must not be recorded as 'finish'.

    The original defect was not only the missing retry -- it was that the record
    read `finish`, which is indistinguishable from a healthy short answer.
    """
    script = [
        FakeMessage(tool_calls=[FakeToolCall("c1", "read_file")]),
        FakeMessage(content=None),
        FakeMessage(content=""),
        FakeMessage(content="   "),
    ]
    out, _ = _run_or_tools(monkeypatch, script)
    assert out["final_text"] == ""
    assert out["stopped_reason"] == "empty_content_after_retry", (
        f"a silent seat was recorded as {out['stopped_reason']!r}")


def test_the_healthy_path_is_unchanged_and_costs_no_extra_call(monkeypatch):
    """BREAK ATTEMPT: a guard that taxes every healthy seat.

    A seat that answers normally must behave exactly as before -- same text,
    same stopped_reason, and NO additional API request. A retry that fires on
    the healthy path would multiply the founder's spend across every seat.
    """
    script = [
        FakeMessage(tool_calls=[FakeToolCall("c1", "read_file")]),
        FakeMessage(content="A normal, complete answer."),
    ]
    out, comp = _run_or_tools(monkeypatch, script)
    assert out["final_text"] == "A normal, complete answer."
    assert out["stopped_reason"] == "finish"
    assert len(comp.calls) == 2, f"healthy path made {len(comp.calls)} calls, expected 2"


# ========================================================= DEFECT 2 (kimi)

def test_forced_synthesis_uses_the_callers_temperature(monkeypatch):
    """BREAK ATTEMPT: the kimi seat, reproduced exactly.

    The fake refuses every temperature but 1.0, as the real kimi-k3 endpoint
    does. Before the fix the forced-synthesis call sent 0.0, raised, was
    swallowed, and the seat returned "". It must now carry 1.0 and come back
    with the synthesis.
    """
    import bench.experiment_11_orchestrator as orch
    # Every turn asks for a tool, so max_iters is exhausted and the forced
    # synthesis fires -- which is exactly the kimi trace: 25 calls, no answer.
    script = [FakeMessage(tool_calls=[FakeToolCall(f"c{i}", "read_file")])
              for i in range(3)]
    script.append(FakeMessage(content="KIMI'S SYNTHESIS, recovered."))
    client = FakeClient(script, reject_temperature=1.0)
    monkeypatch.setattr(orch.time, "sleep", lambda *_: None)

    final = orch._run_openai_tool_loop(
        client=client, model_id="kimi-k3",
        messages=[{"role": "user", "content": "review"}],
        tools=[{"type": "function",
                "function": {"name": "read_file", "description": "d",
                             "parameters": {"type": "object", "properties": {}}}}],
        tool_executor=lambda name, args: "FILE BODY",
        max_iters=3, temperature=1.0,
    )
    assert final == "KIMI'S SYNTHESIS, recovered.", f"seat still returned {final!r}"
    temps = [c.get("temperature") for c in client.chat.completions.calls]
    assert all(t == 1.0 for t in temps), f"a call used the wrong temperature: {temps}"


def test_default_callers_still_send_zero(monkeypatch):
    """BREAK ATTEMPT: the fix silently changing every other seat.

    Every seat but kimi runs pinned at 0.0 for reproducibility. The fix must
    leave the default byte-identical, including on the forced-synthesis call.
    """
    import bench.experiment_11_orchestrator as orch
    script = [FakeMessage(tool_calls=[FakeToolCall(f"c{i}", "read_file")])
              for i in range(2)]
    script.append(FakeMessage(content="done"))
    client = FakeClient(script)
    monkeypatch.setattr(orch.time, "sleep", lambda *_: None)

    orch._run_openai_tool_loop(
        client=client, model_id="openai/gpt-5.5",
        messages=[{"role": "user", "content": "review"}],
        tools=[{"type": "function",
                "function": {"name": "read_file", "description": "d",
                             "parameters": {"type": "object", "properties": {}}}}],
        tool_executor=lambda name, args: "R",
        max_iters=2,
    )
    temps = [c.get("temperature") for c in client.chat.completions.calls]
    assert temps and all(t == 0.0 for t in temps), f"default seat drifted: {temps}"
