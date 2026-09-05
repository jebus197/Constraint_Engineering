"""Hitting the tool-call cap must not throw away the model's answer.

WHY THIS FILE EXISTS
--------------------
2026-09-05, and it is a two-defect interaction worth recording precisely.

Defect 1 (fixed separately): every sympy/z3 tool call from a script-run caller
returned ModuleNotFoundError. Seats gave up after a few useless calls and wrote
their prose, so they "succeeded".

Defect 2 (this file): with defect 1 fixed, the tools worked -- and cx immediately
went from 10 tool calls to 31, straight through MAX_TOOL_ITERATIONS. The loop in
``call_openrouter_with_tools`` exhausted its ``for`` and fell into the ``else``,
which set stopped_reason='max_iterations' and returned ``final_text=""``. A full
paid seat produced ok=False, chars=0. Nothing.

THE TWO DEFECTS WERE MASKING EACH OTHER. Repairing the tools is what made the cap
bite. This is the same shape as the 2026-08-17 session note -- two defects, each
hiding the other, where fixing one alone made things worse.

THE FIX. The cap exists to stop pathological tool spam, and exhausting the loop
already achieves that: no further tool call is issued. Discarding the reasoning
too was an unintended second effect. So on exhaustion the module now makes ONE
final round-trip with ``tools`` omitted, asking for the verdict from work already
done. It cannot loop, because with no tools advertised no tool_calls can return.

WHY THIS TEST MOCKS INSTEAD OF DISPATCHING. The re-dispatch that proved defect 2
existed did NOT re-exercise it -- cx used 9 calls the second time and stayed under
the cap. A live run reaches this branch only by luck, and a branch tested by luck
is untested. The mock forces the exact condition every time, for free.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench import openrouter_tools as ot  # noqa: E402


class _FakeToolCall:
    def __init__(self, idx: int):
        self.id = f"call_{idx}"
        self.type = "function"
        self.function = SimpleNamespace(
            name="sympy_verify",
            arguments='{"claim": "Eq(x + 0, x)"}',
        )


class _FakeCompletions:
    """A model that ALWAYS asks for another tool -- i.e. never terminates.

    ``calls_with_tools`` / ``calls_without_tools`` record how the host drove it,
    which is what distinguishes a harvest from an ordinary finish.
    """

    def __init__(self, harvest_text: str = "FINAL VERDICT: derived under cap.",
                 harvest_raises: bool = False):
        self.calls_with_tools = 0
        self.calls_without_tools = 0
        self.harvest_text = harvest_text
        self.harvest_raises = harvest_raises
        self.last_messages = None

    def create(self, **kwargs):
        self.last_messages = kwargs.get("messages")
        if "tools" in kwargs:
            self.calls_with_tools += 1
            msg = SimpleNamespace(content="", tool_calls=[_FakeToolCall(self.calls_with_tools)])
            return SimpleNamespace(choices=[SimpleNamespace(message=msg)])
        # No tools advertised => this is the harvest round-trip.
        self.calls_without_tools += 1
        if self.harvest_raises:
            raise RuntimeError("simulated upstream failure")
        msg = SimpleNamespace(content=self.harvest_text, tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


@pytest.fixture
def fake_openai(monkeypatch):
    """Install a fake OpenAI client and neutralise real tool execution."""
    holder = {}

    def _make(**_kwargs):
        comp = _FakeCompletions()
        holder["completions"] = comp
        return SimpleNamespace(chat=SimpleNamespace(completions=comp))

    fake_module = SimpleNamespace(OpenAI=_make)
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-not-real")
    monkeypatch.setattr(ot, "dispatch_tool_call",
                        lambda name, args: '{"verdict": "CONFIRMED"}')
    return holder


class TestCapExhaustionHarvestsTheAnswer:

    def test_final_text_is_not_empty_when_the_cap_is_hit(self, fake_openai):
        out = ot.call_openrouter_with_tools(
            "test/model", "sys", "user",
            tools=ot.TOOL_SPECS, max_iterations=3,
        )
        assert out["final_text"] == "FINAL VERDICT: derived under cap.", (
            "the cap discarded the answer -- this is the 2026-09-05 defect where "
            "a full paid seat returned ok=False, chars=0 after 31 successful "
            "tool calls."
        )
        assert out["stopped_reason"] == "max_iterations_harvested"

    def test_the_cap_still_bounds_tool_calls(self, fake_openai):
        """The safety property must survive the fix.

        Without this, 'harvest the answer' could be satisfied by simply raising
        or removing the cap, which is the opposite of what it is for.
        """
        out = ot.call_openrouter_with_tools(
            "test/model", "sys", "user",
            tools=ot.TOOL_SPECS, max_iterations=3,
        )
        comp = fake_openai["completions"]
        assert comp.calls_with_tools == 3, (
            f"tool-bearing round-trips = {comp.calls_with_tools}, expected exactly "
            f"the cap (3). The cap is no longer bounding tool use."
        )
        assert len(out["tool_calls"]) == 3
        assert out["iterations"] == 3

    def test_the_harvest_is_exactly_one_extra_call(self, fake_openai):
        ot.call_openrouter_with_tools(
            "test/model", "sys", "user",
            tools=ot.TOOL_SPECS, max_iterations=3,
        )
        comp = fake_openai["completions"]
        assert comp.calls_without_tools == 1, (
            f"harvest made {comp.calls_without_tools} tool-free calls; it must "
            f"make exactly 1 so the cost of the fix is bounded and it cannot loop."
        )

    def test_the_harvest_request_forbids_asserting_unchecked_claims(self, fake_openai):
        """The harvest must not silently convert unfinished checks into assertions.

        A model cut off mid-verification could otherwise present a half-checked
        claim as verified -- which would be a worse failure than returning
        nothing, because it looks like a result.
        """
        ot.call_openrouter_with_tools(
            "test/model", "sys", "user",
            tools=ot.TOOL_SPECS, max_iterations=2,
        )
        final_msg = fake_openai["completions"].last_messages[-1]
        assert final_msg["role"] == "user"
        assert "UNVERIFIED" in final_msg["content"], (
            "the harvest prompt no longer instructs the model to mark "
            "incomplete checks UNVERIFIED."
        )


class TestTheNormalPathIsUnaffected:

    def test_a_model_that_finishes_normally_does_not_trigger_a_harvest(self, monkeypatch):
        class _Finishes:
            def __init__(self):
                self.calls_with_tools = 0
                self.calls_without_tools = 0

            def create(self, **kwargs):
                if "tools" in kwargs:
                    self.calls_with_tools += 1
                else:
                    self.calls_without_tools += 1
                msg = SimpleNamespace(content="done immediately", tool_calls=None)
                return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

        comp = _Finishes()
        monkeypatch.setitem(
            sys.modules, "openai",
            SimpleNamespace(OpenAI=lambda **k: SimpleNamespace(
                chat=SimpleNamespace(completions=comp))),
        )
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-not-real")

        out = ot.call_openrouter_with_tools(
            "test/model", "sys", "user", tools=ot.TOOL_SPECS, max_iterations=6)
        assert out["final_text"] == "done immediately"
        assert out["stopped_reason"] == "finish"
        assert comp.calls_without_tools == 0, (
            "a harvest fired on a run that terminated normally -- the fix is "
            "costing an extra API call on every ordinary dispatch."
        )
        assert out["iterations"] == 1


class TestAFailedHarvestIsReportedNotMasked:

    def test_harvest_failure_leaves_a_named_stop_reason(self, monkeypatch):
        comp = _FakeCompletions(harvest_raises=True)
        monkeypatch.setitem(
            sys.modules, "openai",
            SimpleNamespace(OpenAI=lambda **k: SimpleNamespace(
                chat=SimpleNamespace(completions=comp))),
        )
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-not-real")
        monkeypatch.setattr(ot, "dispatch_tool_call",
                            lambda name, args: '{"verdict": "CONFIRMED"}')

        out = ot.call_openrouter_with_tools(
            "test/model", "sys", "user", tools=ot.TOOL_SPECS, max_iterations=2)
        assert out["final_text"] == ""
        assert out["stopped_reason"].startswith("max_iterations_harvest_failed"), (
            f"a failed harvest reported {out['stopped_reason']!r}. It must name "
            f"itself, so an empty seat is never mistaken for a model that had "
            f"nothing to say -- the Wolfram rule: a failed call is not a result."
        )
