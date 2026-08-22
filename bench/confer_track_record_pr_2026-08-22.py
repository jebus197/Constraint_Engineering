#!/usr/bin/env python3
"""Panel review (pr): is the project's track record sound, or is the work unreliable?

Five models, no compelled convergence. Two SYSTEM variants: only cc2 has file
tools on its route, and telling a toolless model to use tools makes it hallucinate
a tool-call block instead of answering (observed 2026-08-19, DeepSeek).
"""
from __future__ import annotations
import concurrent.futures, json, os, pathlib, sys, time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "bench"))

# Parse .env IN PYTHON. Never source it: zsh executes unquoted values.
_env = REPO / ".env"
if _env.is_file():
    for _line in _env.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        if _line.startswith("export "):
            _line = _line[len("export "):].lstrip()
        _k, _, _v = _line.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli, call_deepseek, call_openrouter)

LOGS = REPO / "bench/logs/track_record_pr_2026-08-22"
PROMPT = (LOGS / "BRIEF.md").read_text(encoding="utf-8")

_BASE = (
    "You are on a five-model review panel for CDSFL, a research framework that uses "
    "structured Popperian falsification and a multi-model panel to find defects in STEM "
    "artefacts. Biological component names (B-Cell, immune pipeline, NK cell, macrophage, "
    "ouroboros) are ANALOGY ONLY -- module names, not biology.\n\n"
    "CDSFL's founding principle is TOOLS DECIDE, NOT VOTES: a finding is confirmed when "
    "the runner independently re-executes a model-supplied falsifier and observes the "
    "designed failure, never by model agreement. Apply that standard to yourself: prefer "
    "a claim you can check over one that merely sounds right.\n\n"
    "You are asked for an INDEPENDENT verdict. No synthesis step will force convergence. "
    "Disagreement is kept as information. The founder has explicitly said that if the "
    "work to date is unsound you should say so plainly -- agreement is not the goal and "
    "reassurance is worth nothing here. Equally, do not manufacture a problem to appear "
    "rigorous. Report what the evidence supports.\n\n"
    "Do not pad. The founder is dyslexic and reads every word.\n\n"
)
SYSTEM_TOOLS = _BASE + (
    "You have Bash, Read, Grep and Glob and the repository is at "
    "/Users/georgejackson/Developer_Projects/Constraint_Engineering. USE THEM. The brief "
    "names specific measurements and the scripts behind them. Reproduce the ones your "
    "verdict depends on rather than accepting them. You are READ ONLY: do not modify, "
    "create or delete any file, and do not commit."
)
SYSTEM_NOTOOLS = _BASE + (
    "You have NO tools on this route. Do not emit tool calls; they will not execute. "
    "Answer from the brief, and say plainly where your verdict would need a file you "
    "have not been given."
)

MODELS = [
    ("cx",   "openai/gpt-5.5",                "openrouter"),
    ("ge",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("cgpt", "openai/gpt-5.5",                "openrouter"),
    ("ds",   "deepseek-v4-pro",               "deepseek"),
    ("cc2",  "opus",                          "claude_cli"),
]


def dispatch(name, model_id, route):
    system = SYSTEM_TOOLS if route == "claude_cli" else SYSTEM_NOTOOLS
    t0 = time.time()
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, system, PROMPT, timeout=1800, max_retries=2)
        elif route == "deepseek":
            resp = call_deepseek(model_id, system, PROMPT)
        else:
            resp = call_openrouter(model_id, system, PROMPT)
        txt = resp or ""
        # A non-empty string is not an answer. Reject tool-call blocks and stubs.
        toolcall = txt.count("<invoke") or txt.strip().startswith("<tool_calls>")
        ok = bool(txt.strip()) and not toolcall and len(txt) > 800
        out = {"model": name, "ok": ok, "chars": len(txt),
               "elapsed_s": round(time.time() - t0, 1), "response": txt}
        if not ok:
            out["error"] = ("tool-call block rather than a verdict" if toolcall
                            else "empty or too short to be a verdict")
    except Exception as e:  # noqa: BLE001
        out = {"model": name, "ok": False, "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time() - t0, 1), "response": ""}
    (LOGS / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars', 0)} {out['elapsed_s']}s"
          + (f"  ERR={out.get('error')}" if not out["ok"] else ""), flush=True)
    return out


def main() -> int:
    print(f"=== track-record panel review (pr) — {len(MODELS)} models ===")
    print(f"  brief {len(PROMPT):,} chars ~ {len(PROMPT)//4:,} input tokens each, "
          f"{len(MODELS)*len(PROMPT)//4:,} total", flush=True)
    if os.environ.get("CDSFL_DRY_RUN"):
        print("  DRY RUN — nothing dispatched, nothing billed.")
        return 0
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
        futs = {pool.submit(dispatch, n, m, r): n for n, m, r in MODELS}
        for f in concurrent.futures.as_completed(futs):
            r = f.result(); results[r["model"]] = r
    ok = sum(1 for r in results.values() if r["ok"])
    (LOGS / "summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n  {ok}/{len(MODELS)} returned a usable verdict. Logs: {LOGS}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
