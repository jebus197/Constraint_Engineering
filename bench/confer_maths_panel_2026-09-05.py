#!/usr/bin/env python3
"""Six-model paid panel: does the mathematical model need new mathematics?

Founder-authorised 2026-09-05. Roster: CC1 (the operator, participating with its
own position and synthesising the range), Codex, ChatGPT and DeepSeek on paid
routes, CC2 and Fable on the Max subscription.

NO COMPELLED CONVERGENCE. Each seat returns an independent verdict and its
strongest falsification. Disagreement is preserved as information rather than
smoothed into consensus.

A DISCLOSURE THAT BELONGS IN THE DISPATCHER, NOT ONLY THE BRIEF. The Codex and
ChatGPT seats currently share weights, route and system prompt. The designed
contrast between them -- Codex carrying OpenAI's own agent prompt via `codex
exec`, ChatGPT bare via OpenRouter -- was lost at Run 6 when the Codex seat moved
to OpenRouter to eliminate a 45-to-80-minute-per-round fallback. Recorded in
`project_model_panel_config.md` as "Not yet resolved". Measured 2026-09-05: 5 of
8 differentiating dimensions survive (phenotype, capability fingerprint, delivery
parameters, context budget, temperature); 3 do not (model_id, route, system
prompt). The panel is therefore closer to 4 distinct conditions than 5, and the
brief says so to the seats themselves.
"""
from __future__ import annotations
import concurrent.futures, json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli, call_deepseek, call_openrouter)
from openrouter_tools import (  # noqa: E402
    TOOL_SPECS, call_openrouter_with_tools)

_REPO = Path(__file__).resolve().parent.parent
_env = _REPO / ".env"
if _env.is_file():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if not _l or _l.startswith("#") or "=" not in _l:
            continue
        if _l.startswith("export "):
            _l = _l[len("export "):].lstrip()
        _k, _, _v = _l.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

if len(sys.argv) < 2:
    print("usage: confer_maths_panel_2026-09-05.py <log-dir-name>", file=sys.stderr)
    raise SystemExit(2)
LOGS = _REPO / "bench" / "logs" / sys.argv[1]
BRIEF = LOGS / "BRIEF.md"
if not BRIEF.is_file():
    print(f"no BRIEF.md in {LOGS}", file=sys.stderr)
    raise SystemExit(2)
PROMPT = BRIEF.read_text(encoding="utf-8")

import os as _os
_ONLY = _os.environ.get("PANEL_ONLY", "")
_ALL = [
    ("cx",    "openai/gpt-5.5",  "openrouter"),   # PAID
    ("cgpt",  "openai/gpt-5.5",  "openrouter"),   # PAID
    ("ds",    "deepseek-v4-pro", "deepseek"),     # PAID
    ("cc2",   "opus",            "claude_cli"),   # Max, free
    ("fable", "fable",           "claude_cli"),   # Max, free
]
# PANEL_ONLY re-dispatches a SUBSET, so a briefing defect that broke 2 seats does
# not cost a second full paid round for the 3 that worked.
MODELS = [m for m in _ALL if not _ONLY or m[0] in _ONLY.split(",")]

SYSTEM = (
    "You are on a six-seat review panel for CDSFL, a research framework that uses "
    "structured Popperian falsification and a multi-model panel to find defects in "
    "STEM artefacts. Biological component names are ANALOGY ONLY -- module names, "
    "not biology.\n\n"
    "CDSFL's founding principle is TOOLS DECIDE, NOT VOTES. A finding is confirmed "
    "when a tool independently re-executes a falsifier, never by model agreement. "
    "Hold yourself to it: prefer a claim you can check to one that sounds right. "
    "Where you assert a mathematical result, DERIVE it.\n\n"
    "NO COMPELLED CONVERGENCE. Return YOUR verdict and YOUR strongest falsification. "
    "Do not attempt to agree with the other seats. Disagreement is preserved as "
    "information.\n\n"
    "You are expected to declare the reasoning SOUND where it is. This panel is not "
    "scored on finding faults, and a clean verdict backed by derivation is as useful "
    "as a refutation.\n\n"
    "Do not pad. Every word is read."
)


def dispatch(name, model_id, route):
    """EVERY SEAT GETS TOOLS. Founder ruling 2026-09-05: "Tool use is at the core
    of what CDSFL is."

    The first dispatch of this panel used the tool-FREE OpenRouter and DeepSeek
    paths, so 3 of 5 seats could only reason. That inverts the founding principle
    -- a seat that cannot execute cannot decide by execution, and the panel
    degenerates toward exactly the model agreement CDSFL exists to reject.

    `bench/openrouter_tools.py` was built for precisely this (Exp 40 item 1E.11)
    and its own docstring says so: the non-Anthropic seats "have no tool execution
    unless the host wires structured function-calling". It was built and not used.

    Tools offered: sympy_verify, z3_verify, pytest_run, ruff_check, mypy_check.
    Every tool call made by every seat is recorded in the seat's JSON, so the
    claim "this panel used tools" is itself checkable rather than asserted.
    """
    t0 = time.time()
    tool_log = []
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, SYSTEM, PROMPT)      # native Bash
        elif route == "deepseek":
            resp = call_deepseek(model_id, SYSTEM, PROMPT, tools=TOOL_SPECS)
        else:
            r = call_openrouter_with_tools(model_id, SYSTEM, PROMPT,
                                           tools=TOOL_SPECS, max_tokens=32768,
                                           timeout=300)
            resp = r.get("final_text", "")
            tool_log = r.get("tool_calls", [])
        ok = bool(resp and resp.strip())
        out = {"model": name, "route": route, "ok": ok, "chars": len(resp or ""),
               "tool_calls": tool_log, "n_tool_calls": len(tool_log),
               "elapsed_s": round(time.time() - t0, 1), "response": resp or ""}
    except Exception as e:  # noqa: BLE001
        out = {"model": name, "route": route, "ok": False,
               "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time() - t0, 1), "response": ""}
    (LOGS / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars', 0)} "
          f"tools={out.get('n_tool_calls', 'native')} {out['elapsed_s']}s"
          + (f" ERR={out.get('error')}" if not out["ok"] else ""), flush=True)
    return out


def main() -> int:
    paid = [m for m in MODELS if m[2] != "claude_cli"]
    print(f"=== maths panel — {len(MODELS)} dispatched seats + CC1 ===")
    print(f"    PAID seats: {', '.join(n for n, _, _ in paid)}  "
          f"(brief {len(PROMPT):,} chars, about {len(PROMPT)//4:,} tokens each)")
    print(f"    free seats: cc2, fable (Max subscription)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
        futs = {pool.submit(dispatch, n, m, r): n for n, m, r in MODELS}
        results = [f.result() for f in concurrent.futures.as_completed(futs)]
    ok = sum(1 for r in results if r["ok"])
    print(f"\n  {ok}/{len(MODELS)} responded. Logs: {LOGS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
