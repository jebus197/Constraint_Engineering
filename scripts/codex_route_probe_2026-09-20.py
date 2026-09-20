#!/usr/bin/env python3
"""Does the Codex route answer, take tools, and read the revised model? 1 paid call.

FOUNDER, 2026-09-20, approving the probe: *"Do it to check it all works as
expected, including tool calling and its ability to use and interpret the revised
mathematical model. This is purely a test, and not yet an adoption plan. Later/all
future panel reviews will however switch to using 'full fat' Codex 53, and not a
reduced version, given the same tool calling and interpretive constraints."*

WHY A PROBE AT ALL. Everything known about `openai/gpt-5.3-codex` came from
reading OpenRouter's catalogue: the id exists, it lists `tools` and `tool_choice`
among its supported parameters, it costs 1.75 and 14.00 dollars per 1,000,000
tokens. None of that is a call. A catalogue entry is a claim about a route, and
this project's own rule is that a claim about evidence is not evidence.

WHAT IT ASKS, and the question is chosen so a wrong answer cannot look right.
The seat is given the revised model's collapse claim and asked to evaluate it at
1 exact point using a tool. The arithmetic is checked here against SymPy and
mpmath, so the reply is graded rather than admired.

COST. 1 call, a few hundred tokens each way, on a model priced at 1.75 and 14.00
dollars per 1,000,000 tokens: a fraction of 1 penny. It prints its own token
usage and the cost OpenRouter reports, so the figure travels with the call.

Read-only unless `--run` is given. `--help` dispatches nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-5.3-codex"

#: The revised model's core, restricted to the case this probe checks:
#: no action taken, a clean review of sensitivity p, so R_next = R(1-p)/(1-pR).
QUESTION = (
    "A proposed revision states that its residual-risk update, with removal and "
    "introduction both 0 and a clean review of sensitivity p, reduces to "
    "R_next = R(1-p)/(1-p*R). Using the calculator tool, evaluate R_next for "
    "R = 1/2 and p = 1/2. Reply with the numeric value and nothing else.")

TOOLS = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression and return its value.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
}]


def token() -> str | None:
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*(?:export\s+)?OPENROUTER_API_KEY\s*=\s*(.+)$", line)
        if m:
            return m.group(1).strip().strip('"').strip("'")
    return None


def post(key: str, messages: list, tools: list | None) -> dict:
    body = {"model": MODEL, "messages": messages, "max_tokens": 400}
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:   # noqa: S310 - fixed https URL
        return json.loads(r.read().decode("utf-8"))


def expected() -> float:
    """The answer, from 2 independent tools, so the reply is graded not admired."""
    import sympy as sp
    import mpmath as mp
    R, p = sp.Rational(1, 2), sp.Rational(1, 2)
    sym = float(R * (1 - p) / (1 - p * R))
    num = float(mp.mpf(1) / 2 * (1 - mp.mpf(1) / 2) / (1 - mp.mpf(1) / 2 * (mp.mpf(1) / 2)))
    assert abs(sym - num) < 1e-12, (sym, num)
    return sym


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", action="store_true", help="make the 1 paid call")
    ap.add_argument("--json", type=pathlib.Path)
    a = ap.parse_args(argv)

    want = expected()
    if not a.run:
        print(f"read-only. Would call {MODEL} once with 1 tool offered.\n"
              f"The correct answer, from SymPy and mpmath: {want}\n"
              f"Pass --run to dispatch. Nothing has been sent.")
        return 0

    key = token()
    if not key:
        print("OPENROUTER_API_KEY is not in .env. NOT EVIDENCE: nothing was dispatched.")
        return 2

    out = {"model": MODEL, "expected": want}
    msgs = [{"role": "user", "content": QUESTION}]
    try:
        first = post(key, msgs, TOOLS)
    except Exception as exc:                                   # noqa: BLE001
        print(f"the route did not answer ({type(exc).__name__}: {exc}). "
              f"NOT EVIDENCE: nothing is concluded about the model.")
        return 3

    choice = first["choices"][0]["message"]
    calls = choice.get("tool_calls") or []
    out["answered"] = True
    out["offered_a_tool_call"] = bool(calls)
    out["usage_first_call"] = first.get("usage", {})

    if calls:
        args = json.loads(calls[0]["function"]["arguments"])
        out["tool_expression"] = args.get("expression")
        try:
            value = eval(args.get("expression", ""), {"__builtins__": {}}, {})  # noqa: S307
        except Exception:                                      # noqa: BLE001
            value = None
        out["tool_result"] = value
        msgs += [choice, {"role": "tool", "tool_call_id": calls[0]["id"],
                          "content": str(value)}]
        second = post(key, msgs, TOOLS)
        final = second["choices"][0]["message"].get("content", "")
        out["usage_second_call"] = second.get("usage", {})
    else:
        final = choice.get("content", "")

    out["final_text"] = (final or "").strip()[:300]
    nums = re.findall(r"-?\d+(?:\.\d+)?(?:/\d+)?", out["final_text"])
    got = None
    for n in nums:
        try:
            got = eval(n, {"__builtins__": {}}, {})            # noqa: S307
            break
        except Exception:                                      # noqa: BLE001
            continue
    out["parsed_answer"] = got
    out["answer_correct"] = got is not None and abs(float(got) - want) < 1e-9
    print(json.dumps(out, indent=2))
    verdict = ("ROUTE WORKS, TOOLS WORK, ANSWER CORRECT" if out["answer_correct"]
               and out["offered_a_tool_call"] else
               "ROUTE ANSWERED but check the detail above")
    print("\n" + verdict)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return 0 if out["answer_correct"] else 4


if __name__ == "__main__":
    sys.exit(main())
