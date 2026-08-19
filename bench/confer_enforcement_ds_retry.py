#!/usr/bin/env python3
"""DeepSeek-only retry. It did not answer: it emitted a tool-call block instead.

ROOT CAUSE, and it is the brief's fault. The SYSTEM prompt says "If you have
file-reading tools, USE THEM: the repository is at <path>". That line is aimed at
cc2, the only panellist with tool access. DeepSeek read it, has no tools on the
API route, and emitted a hallucinated <tool_calls> block trying to comply.

It returned ok=True with 199 chars and no verdict -- a failure rendering as a
success, the same shape as the record assembler that counted a failure file as a
response yesterday. A non-empty string is not an answer.

Fix: address the tool instruction to cc2 explicitly, and reject a response that is
predominantly a tool-call block.
"""
from __future__ import annotations
import importlib.util
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

# Load .env IN PYTHON, never by shell sourcing. Sourcing it with `. ./.env` makes
# zsh try to execute unquoted values: on 2026-08-19 that echoed a token into a
# shell error. A parser cannot execute what it reads.
import os
_env = pathlib.Path(__file__).resolve().parent.parent / ".env"
if _env.is_file():
    for _line in _env.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        if _line.startswith("export "):
            _line = _line[len("export "):].lstrip()
        _k, _, _v = _line.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from experiment_11_orchestrator import call_deepseek  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "panel", pathlib.Path(__file__).resolve().parent / "confer_enforcement_prose_pr_2026-08-19.py")
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)

SYSTEM = panel.SYSTEM.replace(
    "If you have file-reading tools, USE THEM: the repository is at "
    "/Users/georgejackson/Developer_Projects/Constraint_Engineering and the primary "
    "source pack below is an extract, not a substitute. Verify rather than accept.\n\n",
    "You have NO tools on this route. Do not emit tool calls; they will not execute. "
    "Answer from the brief and the appended sources, and say plainly where you would "
    "need to read a file you have not been given.\n\n",
)
assert "NO tools on this route" in SYSTEM, "system-prompt patch did not apply"

t0 = time.time()
resp = call_deepseek("deepseek-v4-pro", SYSTEM, panel.PROMPT)
txt = resp or ""
looks_like_toolcall = txt.count("<invoke") or txt.strip().startswith("<tool_calls>")
ok = bool(txt.strip()) and not looks_like_toolcall and len(txt) > 1000
out = {"model": "ds", "ok": ok, "chars": len(txt),
       "elapsed_s": round(time.time() - t0, 1), "response": txt,
       "note": "retry; system prompt corrected to state no tool access"}
if not ok:
    out["error"] = ("response is a tool-call block or too short to be a verdict"
                    if txt.strip() else "empty response")
(panel.LOGS / "ds.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"  [ds] ok={out['ok']} chars={out['chars']} {out['elapsed_s']}s"
      + (f"  ERR={out.get('error')}" if not ok else ""))
