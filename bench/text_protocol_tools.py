"""Tool use for a seat whose API route has no native function calling.

FOUNDER RULING 21, 2026-09-06. The founder's first reading of "text-protocol
fallback" was that it lets a model SKIP tools, and his reaction to that reading was
correct. It is the opposite. The model writes its tool calls as structured TEXT,
this module parses them, executes them through the SAME dispatcher the native path
uses, and feeds the real results back. It ENFORCES tool use on a seat that
currently cannot demonstrate any.

WHY IT IS NEEDED. `call_openrouter_with_tools` uses OpenRouter's function-calling
interface. The DeepSeek seat is configured with `api="deepseek"` -- its own direct
interface -- so it never reaches that loop, and nothing in the archive can show
whether it ran a tool at all. An unverified seat in a 5-seat panel is worse than a
slower one: its agreement carries the weight of a checked opinion while being an
unchecked one.

THE PROTOCOL, deliberately ugly and unmistakable. The model emits, on its own line:

    <<<TOOL name=sympy_verify>>>
    {"expression": "x**2 - 1", "claim": "factors as (x-1)(x+1)"}
    <<<END>>>

Chosen over JSON-in-a-fence because fenced JSON collides with ordinary answer
prose -- a model discussing a JSON example would have it executed. The sentinel is
non-collidable, which is the same reasoning the sweep prompt uses after a
collidable delimiter cost a whole arc of prose findings.

WHAT THIS DOES NOT DO. It does not make an unverified seat a verified one by
itself: a model that ignores the protocol still runs no tools. It makes the
DIFFERENCE VISIBLE, because `calls` is empty and `protocol_followed` is False,
which is a fact the archive can carry. Whether a seat that ignores it should be
dropped is a separate decision and is not taken here.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple

TOOL_BLOCK = re.compile(
    r"<<<TOOL\s+name=([A-Za-z_][A-Za-z0-9_]*)\s*>>>\s*(.*?)\s*<<<END>>>",
    re.DOTALL)

MAX_TEXT_TOOL_ITERATIONS = 10


def protocol_instructions(tool_specs: List[Dict[str, Any]]) -> str:
    """The fragment appended to a seat's system prompt. Names every tool it may
    call and the exact shape of a call, because a protocol a model has to guess
    is a protocol it will get wrong."""
    lines = [
        "TOOL PROTOCOL. Your route does not carry native tool calling, so you call",
        "tools by writing them as text. A call is EXACTLY this, on its own lines:",
        "",
        "<<<TOOL name=THE_TOOL_NAME>>>",
        '{"argument": "value"}',
        "<<<END>>>",
        "",
        "The arguments are a single JSON object. Emit as many calls as you need.",
        "Each one is executed and its REAL output is returned to you before you",
        "answer. Do not describe what a tool would return: call it and read it.",
        "",
        "Available tools:",
    ]
    for spec in tool_specs:
        fn = spec.get("function", spec)
        params = (fn.get("parameters") or {}).get("properties") or {}
        lines.append(f"  {fn.get('name')} — {fn.get('description', '')[:120]}")
        if params:
            lines.append(f"      arguments: {', '.join(sorted(params))}")
    return "\n".join(lines)


def parse_tool_calls(text: str) -> List[Tuple[str, str]]:
    """Extract (name, arguments_json) pairs. Malformed JSON is NOT silently
    dropped -- it is returned verbatim so the dispatcher reports the error back to
    the model, which is how a model learns it got the shape wrong."""
    return [(m.group(1), m.group(2)) for m in TOOL_BLOCK.finditer(text or "")]


def strip_tool_calls(text: str) -> str:
    """The seat's prose with its call blocks removed, for recording the answer."""
    return TOOL_BLOCK.sub("", text or "").strip()


def run_text_protocol(
    send: Callable[[List[Dict[str, str]]], str],
    system_prompt: Optional[str],
    user_prompt: str,
    tool_specs: List[Dict[str, Any]],
    dispatch: Callable[[str, str], str],
    max_iterations: int = MAX_TEXT_TOOL_ITERATIONS,
) -> Dict[str, Any]:
    """Drive a text-protocol tool conversation.

    `send` takes a message list and returns the assistant's text, so this module
    stays independent of which vendor interface the seat actually uses.

    Mirrors the native loop's contract, including the CAP HARVEST: on exhausting
    the iteration budget it asks once more, tool-free, rather than discarding the
    seat's reasoning. A full paid seat returning nothing because it was still
    working is a defect this project has already paid for once.
    """
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system",
                         "content": system_prompt + "\n\n" + protocol_instructions(tool_specs)})
    messages.append({"role": "user", "content": user_prompt})

    known = {(s.get("function", s)).get("name") for s in tool_specs}
    calls: List[Tuple[str, str, str]] = []
    final_text, stopped = "", "finish"

    for _ in range(max_iterations):
        reply = send(messages) or ""
        requested = parse_tool_calls(reply)
        if not requested:
            final_text = reply.strip()
            break
        messages.append({"role": "assistant", "content": reply})
        results = []
        for name, args in requested:
            if name not in known:
                out = (f"ERROR: no tool named {name!r}. Available: "
                       f"{', '.join(sorted(known))}")
            else:
                try:
                    out = dispatch(name, args)
                except Exception as exc:      # a tool that raises is a RESULT
                    out = f"ERROR: {type(exc).__name__}: {exc}"
            calls.append((name, args, out))
            results.append(f"<<<RESULT name={name}>>>\n{out}\n<<<END>>>")
        messages.append({"role": "user", "content": "\n".join(results)})
    else:
        stopped = "max_iterations"
        messages.append({"role": "user", "content": (
            "You have reached this review's tool-call limit. Give your final answer "
            "now using only what you have already verified, and mark any claim you "
            "could not check as UNVERIFIED rather than asserting it.")})
        try:
            final_text = (send(messages) or "").strip()
            if final_text:
                stopped = "max_iterations_harvested"
        except Exception as exc:
            stopped = f"max_iterations_harvest_failed: {type(exc).__name__}"

    return {
        "final_text": strip_tool_calls(final_text),
        "tool_calls": calls,
        "n_tool_calls": len(calls),
        "protocol_followed": bool(calls),
        "stopped_reason": stopped,
    }
