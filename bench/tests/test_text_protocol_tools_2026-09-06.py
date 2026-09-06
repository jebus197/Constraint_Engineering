"""The text protocol must ENFORCE tool use, not excuse it.

FOUNDER RULING 21. His first reading was that a text-protocol fallback lets a seat
skip tools, and he was right to object to that. It is the opposite: the model
writes calls as text, they are parsed and EXECUTED through the same dispatcher the
native path uses, and the real output is fed back. These tests pin that, and pin
the failure modes that would quietly turn it back into an excuse.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO / "bench") not in sys.path:
    sys.path.insert(0, str(REPO / "bench"))

import text_protocol_tools as tpt  # noqa: E402

SPECS = [
    {"function": {"name": "sympy_verify", "description": "check an algebraic claim",
                  "parameters": {"properties": {"expression": {}, "claim": {}}}}},
    {"function": {"name": "z3_verify", "description": "check a constraint claim",
                  "parameters": {"properties": {"constraints": {}}}}},
]


def _scripted(replies):
    """A model that says exactly these things, in order."""
    it = iter(replies)
    seen = []

    def send(messages):
        seen.append(messages[-1]["content"])
        try:
            return next(it)
        except StopIteration:
            return "done"
    send.seen = seen
    return send


def test_a_call_is_parsed_and_actually_dispatched():
    executed = []

    def dispatch(name, args):
        executed.append((name, args))
        return "REAL TOOL OUTPUT: 42"

    send = _scripted(['<<<TOOL name=sympy_verify>>>\n{"expression": "x+x"}\n<<<END>>>',
                      "final answer"])
    out = tpt.run_text_protocol(send, "sys", "prompt", SPECS, dispatch)
    assert executed == [("sympy_verify", '{"expression": "x+x"}')]
    assert out["n_tool_calls"] == 1
    assert out["protocol_followed"] is True
    assert out["final_text"] == "final answer"


def test_the_real_result_is_fed_back_to_the_model():
    """If the output is not returned, the model is not using the tool -- it is
    being watched using one."""
    send = _scripted(['<<<TOOL name=z3_verify>>>\n{"constraints": "x>0"}\n<<<END>>>',
                      "done"])
    tpt.run_text_protocol(send, None, "p", SPECS, lambda n, a: "UNSAT")
    fed_back = [m for m in send.seen if "UNSAT" in m]
    assert fed_back, "the tool's real output never reached the model"


def test_a_seat_that_ignores_the_protocol_is_VISIBLY_unverified():
    """The point of the ruling. A model that emits no calls must not look the same
    as one that ran tools."""
    out = tpt.run_text_protocol(_scripted(["I am confident the claim holds."]),
                                None, "p", SPECS, lambda n, a: "x")
    assert out["n_tool_calls"] == 0
    assert out["protocol_followed"] is False


def test_an_unknown_tool_name_is_reported_back_not_silently_dropped():
    send = _scripted(['<<<TOOL name=make_it_true>>>\n{}\n<<<END>>>', "ok"])
    out = tpt.run_text_protocol(send, None, "p", SPECS, lambda n, a: "never called")
    assert out["n_tool_calls"] == 1
    assert "ERROR: no tool named" in out["tool_calls"][0][2]
    assert any("no tool named" in m for m in send.seen)


def test_a_tool_that_raises_returns_an_error_rather_than_killing_the_seat():
    def boom(name, args):
        raise ValueError("sympy exploded")
    send = _scripted(['<<<TOOL name=sympy_verify>>>\n{}\n<<<END>>>', "ok"])
    out = tpt.run_text_protocol(send, None, "p", SPECS, boom)
    assert "ERROR: ValueError: sympy exploded" in out["tool_calls"][0][2]
    assert out["final_text"] == "ok"


def test_malformed_json_reaches_the_dispatcher_rather_than_being_dropped():
    """A silently dropped bad call teaches the model nothing."""
    got = []
    send = _scripted(['<<<TOOL name=sympy_verify>>>\n{not json at all\n<<<END>>>', "ok"])
    tpt.run_text_protocol(send, None, "p", SPECS, lambda n, a: got.append(a) or "err")
    assert got == ["{not json at all"]


def test_the_cap_harvests_the_answer_instead_of_discarding_it():
    """The defect this project already paid for once: a full seat returning
    nothing because it was still working when the budget ran out."""
    always_calls = ['<<<TOOL name=sympy_verify>>>\n{}\n<<<END>>>'] * 3 + ["HARVESTED ANSWER"]
    send = _scripted(always_calls)
    out = tpt.run_text_protocol(send, None, "p", SPECS, lambda n, a: "ok", max_iterations=3)
    assert out["stopped_reason"] == "max_iterations_harvested"
    assert out["final_text"] == "HARVESTED ANSWER"


def test_prose_that_merely_mentions_json_is_not_executed():
    """The delimiter is non-collidable on purpose. A fenced-JSON protocol would
    execute a model's own worked example."""
    reply = 'Here is an example: ```json\n{"expression": "x+x"}\n```  I did not call it.'
    assert tpt.parse_tool_calls(reply) == []


def test_the_instructions_name_every_available_tool():
    text = tpt.protocol_instructions(SPECS)
    assert "sympy_verify" in text and "z3_verify" in text
    assert "<<<TOOL name=" in text and "<<<END>>>" in text
