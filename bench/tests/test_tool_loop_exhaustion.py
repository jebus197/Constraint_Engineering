"""Regression: the OpenAI tool loop must never crap out a round to a runaway
tool loop. On max_iters exhaustion (the model keeps requesting tools, e.g. stuck
retrying a bad import) the loop forces ONE final tools-LESS call so the model
returns its synthesis rather than empty text. Found 2026-06-03 while wiring the
execute_python tool into the decomposed synthesis turn; the founder's standing
rule is "don't let models crap out".
"""
from __future__ import annotations

from bench.experiment_11_orchestrator import _run_openai_tool_loop


class _Fn:
    name = "execute_python"
    arguments = '{"code": "print(1)"}'


class _TC:
    id = "tc1"
    function = _Fn()

    def model_dump(self):
        return {"id": self.id, "type": "function",
                "function": {"name": self.function.name,
                             "arguments": self.function.arguments}}


class _Msg:
    def __init__(self, content, tool_calls):
        self.content = content
        self.tool_calls = tool_calls


class _Choice:
    def __init__(self, msg):
        self.message = msg


class _Resp:
    def __init__(self, msg):
        self.choices = [_Choice(msg)]


def test_exhaustion_forces_final_tools_less_answer():
    """Model requests tools on every turn -> after max_iters the loop makes one
    tools-LESS call and returns its synthesis (non-empty), never an empty round."""
    calls = {"with_tools": 0, "without_tools": 0}

    class _Completions:
        def create(self, **kwargs):
            if "tools" in kwargs:            # a loop turn: keep requesting tools
                calls["with_tools"] += 1
                return _Resp(_Msg("", [_TC()]))
            calls["without_tools"] += 1      # the forced final turn: no tools kwarg
            return _Resp(_Msg("SYNTHESIS after exhaustion", None))

    class _Client:
        class chat:
            completions = _Completions()

    out = _run_openai_tool_loop(
        _Client(), "m", [{"role": "user", "content": "go"}],
        tools=[{"type": "function", "function": {"name": "execute_python"}}],
        tool_executor=lambda name, args: "tool output",
        max_iters=3,
    )
    assert calls["with_tools"] == 3                 # looped the full budget
    assert calls["without_tools"] == 1              # exactly one forced final call
    assert out == "SYNTHESIS after exhaustion"      # non-empty -> no crap-out


def test_normal_final_answer_makes_no_forced_call():
    """When the model answers within budget, the loop breaks and makes no extra
    forced call (the exhaustion path must not run on the happy path)."""
    calls = {"n": 0}

    class _Completions:
        def create(self, **kwargs):
            calls["n"] += 1
            return _Resp(_Msg("done", None))        # final answer immediately

    class _Client:
        class chat:
            completions = _Completions()

    out = _run_openai_tool_loop(
        _Client(), "m", [{"role": "user", "content": "go"}],
        tools=[{"type": "function", "function": {"name": "execute_python"}}],
        tool_executor=lambda name, args: "x", max_iters=6,
    )
    assert out == "done"
    assert calls["n"] == 1                          # broke on turn 1, no forced call
