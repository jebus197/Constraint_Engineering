#!/usr/bin/env python3
"""A small PAID test that Gemini's tool switch actually operates.

FOUNDER RULING 2026-08-30: "There is to be no exceptions from tool use... Set up
a small paid test for Gemini of some problem or other from the project (again
that is small), simply to test that this switch when turned on operates as
intended. Presumably this test can be very cheap and it might give an
interesting answer in any case."

WHAT IT DOES. One dispatch, on the `google` route -- Gemini's FAILOVER route and
the one `decomposed_dispatch` uses, which until 2026-08-31 dropped tools
silently. The prompt asks a real project question whose answer cannot be
recalled: the Wilson 95% interval for 126/246, the measured proportion of
archived fixes that do NOT silence their own falsifier.

WHY THAT QUESTION. It is a genuine project number, it is small, and it
DISCRIMINATES. A model answering from memory produces a plausible interval; a
model that actually ran statsmodels produces [0.4500, 0.5740] to four places.
So the test does not ask whether a tool was offered -- it checks whether the
answer could only have come from running one.

COST. One call, one small prompt, 2,048 output tokens. Pennies.

Run:  python3 bench/tools/gemini_tool_switch_test.py
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

_env = REPO / ".env"
if _env.is_file():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if not _l or _l.startswith("#") or "=" not in _l:
            continue
        if _l.startswith("export "):
            _l = _l[len("export "):].lstrip()
        _k, _, _v = _l.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from experiment_11_orchestrator import (  # noqa: E402
    EXECUTE_PYTHON_TOOL, ModelConfig, dispatch,
)

#: The answer only a tool run produces, to 4 decimal places.
EXPECTED = ("0.4500", "0.5740")

PROMPT = (
    "In this project, 126 of 246 archived findings have a proposed fix that does "
    "NOT silence that finding's own falsifier.\n\n"
    "Compute the Wilson 95% confidence interval for that proportion using "
    "statsmodels.stats.proportion.proportion_confint with method='wilson'. "
    "Run the code with the execute_python tool -- do not estimate.\n\n"
    "Reply with exactly one line:\n"
    "WILSON: <lower to 4dp>, <upper to 4dp>\n"
)


def main() -> int:
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        print("BLOCKED: neither GEMINI_API_KEY nor GOOGLE_API_KEY is set.")
        return 2

    mc = ModelConfig(
        label="Gemini", model_id="gemini-3.1-pro-preview", api="google",
        role="player", system_prompt_path=None, max_tokens=2048, timeout=180,
        max_retries=1,
    )
    print("  dispatching ONE paid Gemini call on the google route, tools ON ...")
    text = dispatch(mc, PROMPT, "", enable_tools=True)
    print(f"  reply ({len(text)} chars):\n    {text.strip()[:400]}")

    m = re.search(r"WILSON:\s*([0-9.]+)\s*,\s*([0-9.]+)", text or "")
    if not m:
        print("\n  RESULT: no parsable interval returned — INCONCLUSIVE.")
        return 1
    got = (m.group(1), m.group(2))
    exact = got == EXPECTED
    print(f"\n  expected (tool-derived): {EXPECTED}")
    print(f"  received               : {got}")
    if exact:
        print("  RESULT: EXACT MATCH — the tool switch operates. Gemini ran code.")
        return 0
    print("  RESULT: MISMATCH — the model answered without running the tool, or "
          "the loop did not deliver the result back. Tool switch NOT confirmed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
