#!/usr/bin/env python3
"""THE BUILD EXPERIMENT. Six models fix; a mechanical gate decides; CC1 monitors.

This experiment exists to FIX, not to find. Models are not forbidden from noticing
other things, but anything outside the approved list in
`bench/build_experiment_tasks.py` is RECORDED, NOT APPLIED.

ACCEPTANCE IS MECHANICAL and lives in `bench/build_acceptance.py`, commissioned
2026-08-22 against known-good and known-bad inputs, 8 of 8:
    (1) the model's test FAILS at the parent commit
    (2) the same test PASSES with the model's patch applied
    (3) the FULL SUITE stays green
No model vote and no CC1 adjudication appears anywhere in that path.

THE LADDER (founder ruling 2026-08-22: use the mechanism that already exists).
Rung 1 is a metered model, round-robin for source diversity. Rung 2 is CC2 and
rung 3 is Fable -- both Max-plan and free, so every escalation costs nothing and
the cost ceiling binds only the first attempt. A task rejected at every rung goes
to HIL, which is exactly what the runner's own routing ladder does with a critical
it cannot resolve.

ACCEPTED PATCHES GO TO A BRANCH, NOT TO MAIN. `feedback_fixes_hil_only` stands:
the gate proves a patch works, the founder decides whether it ships.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO))

_env = REPO / ".env"
if _env.is_file():                       # parse, never source: zsh executes values
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if not _l or _l.startswith("#") or "=" not in _l:
            continue
        if _l.startswith("export "):
            _l = _l[len("export "):].lstrip()
        _k, _, _v = _l.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from experiment_11_orchestrator import (call_claude_cli, call_deepseek,  # noqa: E402
                                        call_openrouter, set_panel_cwd)
import build_experiment_tools as TOOLS                                   # noqa: E402
from build_experiment_tasks import TASKS                                 # noqa: E402
from bench import build_acceptance as BA                                 # noqa: E402

LOGS = REPO / "bench/logs/build_experiment_2026-08-22"
CY = LOGS / "CY_LIVE.log"

LADDER = [
    [("cx", "openai/gpt-5.5", "openrouter"), ("ge", "google/gemini-3.1-pro-preview", "openrouter"),
     ("cgpt", "openai/gpt-5.5", "openrouter"), ("ds", "deepseek-v4-pro", "deepseek")],
    [("cc2", "opus", "claude_cli")],
    [("fable", "fable", "claude_cli")],
]

_SYSTEM_TEMPLATE = (
    "You are fixing defects in CDSFL, a research framework that uses structured "
    "Popperian falsification and a multi-model panel to find defects in STEM artefacts. "
    "Biological component names (B-Cell, immune pipeline, NK cell, macrophage, ouroboros) "
    "are ANALOGY ONLY -- module names, not biology.\n\n"
    "THIS IS NOT A REVIEW. Six review panels in the last week returned problems because "
    "every brief asked for problems. This one asks you to FIX something. Deliver working "
    "code, not an assessment.\n\n"
    "YOUR OUTPUT IS JUDGED MECHANICALLY. No model votes on it and no assistant adjudicates "
    "it. A harness applies your patch in a throwaway git worktree and accepts it if and "
    "ONLY if:\n"
    "  (1) your new test FAILS at the parent commit,\n"
    "  (2) the same test PASSES with your patch applied,\n"
    "  (3) the full suite (~3600 tests) stays green.\n"
    "A test that always passes fails (1). A test that always fails fails (2). That "
    "two-sidedness is deliberate: this project's falsifier gate accepts a falsifier merely "
    "for FIRING, which is why `reverify_falsifier(\"print('FALSIFIED')\")` returns "
    "CONFIRMED and why half its archived confirmations cannot be demonstrated.\n\n"
    "{TOOLS_PARAGRAPH}"
    "REQUIRED OUTPUT FORMAT, exactly:\n\n"
    "<<<< SEARCH path/to/file.py\n<the exact existing text, copied verbatim>\n"
    "==== REPLACE\n<the replacement text>\n>>>>\n\n"
    "(repeat for each edit, and the SEARCH text must match the file byte for byte)\n\n"
    "TEST_FILE: bench/tests/test_<something>.py\n\n"
    "```python\n<the complete test file>\n```\n\n"
    "Then at most 10 lines saying what you changed and why the test could not pass before.\n"
    "Documentation tasks still need a test -- assert the document's content; this project "
    "already does that for its memory ledger and its qc checks.\n\n"
    "Do not pad. The founder is dyslexic and reads every word."
)

# TWO VARIANTS, because the routes differ. Sending one SYSTEM to every route is the
# defect recorded on 2026-08-19 in bench/confer_enforcement_ds_retry.py and
# reintroduced here on 2026-08-22: DeepSeek has no tool loop on its API route, read
# "USE YOUR TOOLS", and hallucinated a <tool_calls> block instead of answering.
_TOOLS_YES = (
    "USE YOUR TOOLS, AND USE grep FIRST. bench/reference_runner_v2.py is 10,510 lines "
    "and 527,304 characters; read_file returns at most 24,000 characters, so paging it "
    "whole would exhaust your budget before you reach the code. grep for the symbol "
    "named in the task, then read_file the surrounding 200 lines -- read_file returns "
    "RAW text, so what you copy from it can go straight into a SEARCH block byte for "
    "byte. Never paste numbered output (numbered=true) into a SEARCH block. Run the "
    "existing "
    "tests. Check a claim rather than asserting it -- the standard here is TOOLS DECIDE, "
    "NOT VOTES, and it applies to you.\n\n")
_TOOLS_NO = (
    "YOU HAVE NO TOOLS ON THIS ROUTE. Do not emit tool calls; they will not execute and "
    "a response that is mostly a tool-call block is discarded. Work from the task text, "
    "and say plainly where you would need to read a file you have not been given.\n\n")

SYSTEM_TOOLS = _SYSTEM_TEMPLATE.replace("{TOOLS_PARAGRAPH}", _TOOLS_YES)
SYSTEM_NOTOOLS = _SYSTEM_TEMPLATE.replace("{TOOLS_PARAGRAPH}", _TOOLS_NO)
assert "{TOOLS_PARAGRAPH}" not in SYSTEM_TOOLS and "grep FIRST" in SYSTEM_TOOLS
assert "NO TOOLS ON THIS ROUTE" in SYSTEM_NOTOOLS


def _cy(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S')}  {msg}"
    with CY.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    print(line, flush=True)


def _prompt(task: dict) -> str:
    p = [f"# TASK {task['id']}: {task['title']}", "",
         "## Why this needs doing", task["why"], "",
         "## Where to look", task["where"], "",
         "## What done looks like", task["done"], ""]
    if task.get("report_only"):
        p += ["## NOTE", "This task accepts a REPORT rather than a patch. Run the "
              "components, report what they did, and name what you could not verify.", ""]
    p += ["## Repository",
          "Your working directory is a DISPOSABLE COPY of the repository at the "
          "commit under test. Read it and run tests in it freely. Anything you write "
          "there is discarded -- the only thing that leaves this session is the patch "
          "and test you return in the required format below.", "",
          "Read before you write. Run the existing tests. Then produce the patch and the "
          "test in the required format."]
    return "\n".join(p)


def dispatch(tag: str, model_id: str, route: str, prompt: str, timeout: int = 1800,
             parent: str = "HEAD") -> str:
    if route == "claude_cli":
        # SANDBOXED. The Claude CLI route grants Bash, and BASH IS A SUPERSET OF
        # WRITE. On 2026-08-22 a model working T01 edited bench/reference_runner_v2.py
        # in the live tree instead of returning a patch, and a blanket `git add -A`
        # committed 157 lines of unreviewed, ungated code under a commit message that
        # did not mention it. The 2026-07-29 ruling "remove Write/Edit from panel
        # dispatch" was verified DONE by checking --allowedTools for Write and Edit;
        # Bash was left in place and defeats it.
        #
        # set_panel_cwd() already existed for exactly this and had never been called
        # by any dispatch in this project. Its own docstring: "failing open here would
        # put the panel back in the repo, which is the exposure this exists to close."
        # The model gets a full disposable worktree: reads work, writes cannot escape.
        wt = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_panel_")) / "repo"
        try:
            rc = subprocess.run(["git", "worktree", "add", "--detach", str(wt), parent],
                                cwd=str(REPO), capture_output=True, text=True).returncode
            if rc != 0:
                raise RuntimeError("could not create the panel sandbox worktree")
            set_panel_cwd(str(wt))
            return call_claude_cli(model_id, SYSTEM_TOOLS, prompt,
                                   timeout=timeout, max_retries=2) or ""
        finally:
            set_panel_cwd(None)
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                           cwd=str(REPO), capture_output=True)
            shutil.rmtree(wt.parent, ignore_errors=True)
    if route == "deepseek":                         # NO tool loop on this route
        return call_deepseek(model_id, SYSTEM_NOTOOLS, prompt) or ""
    # 30, not 8. Measured: the target file needs 22 read_file calls at the 24,000-char
    # cap, so a budget of 8 cannot reach the code the task names. ChatGPT said exactly
    # that and was right.
    return call_openrouter(model_id, SYSTEM_TOOLS, prompt, tools=TOOLS.TOOL_SPECS,
                           tool_executor=TOOLS.execute, max_tool_iters=30) or ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated task ids")
    ap.add_argument("--max-rungs", type=int, default=3)
    args = ap.parse_args()
    want = {t.strip() for t in args.only.split(",") if t.strip()} or None

    parent = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                            capture_output=True, text=True).stdout.strip()
    tasks = [t for t in TASKS if not want or t["id"] in want]
    _cy(f"=== BUILD EXPERIMENT START — {len(tasks)} tasks, parent {parent[:8]} ===")
    _cy(f"    ladder: rung1 metered round-robin, rung2 cc2 (free), rung3 fable (free)")

    results = []
    for i, task in enumerate(tasks):
        rec = {"task": task["id"], "title": task["title"], "attempts": [],
               "outcome": "NOT_ATTEMPTED"}
        prompt = _prompt(task)
        for rung_i, rung in enumerate(LADDER[:args.max_rungs]):
            tag, model_id, route = rung[i % len(rung)]
            _cy(f"[{task['id']}] rung {rung_i+1}: dispatching to {tag}")
            t0 = time.time()
            try:
                resp = dispatch(tag, model_id, route, prompt, parent=parent)
            except Exception as exc:                     # noqa: BLE001
                _cy(f"[{task['id']}] {tag} DISPATCH ERROR {type(exc).__name__}: {exc}")
                rec["attempts"].append({"rung": rung_i + 1, "model": tag,
                                        "outcome": "DISPATCH_ERROR", "error": str(exc)})
                continue
            el = round(time.time() - t0, 1)
            # NOT "{task}_{tag}_response.md". A model's response legitimately contains
            # SIM-A / SIM-B fixtures (this project's own simulated-agent convention),
            # which makes the file structurally self-declare as a simulated artefact --
            # and a bare vendor name in the filename of such a file is a provenance
            # failure under the 2026-08-08 ruling. Caught red by
            # test_sim_naming_and_integrity_directive.py on 2026-08-22. The guard is
            # right and the naming was wrong; -LIVE marks these as real dispatches.
            # NO VENDOR NAME IN THE PATH. The 2026-08-08 ruling forbids a bare vendor
            # name anywhere in an artefact that self-declares as simulated, and a
            # model's response legitimately contains SIM-A / SIM-B fixtures, which is
            # exactly such a self-declaration. Two renames were needed before this was
            # right: adding "-LIVE" did not help, because the guard matches the TOKEN.
            # Model identity lives in RESPONSE_MODEL_INDEX.json and results.json, which
            # is better provenance than a filename anyway.
            (LOGS / f"{task['id']}_rung{rung_i + 1}_response.md").write_text(
                resp, encoding="utf-8")
            _idx = LOGS / "RESPONSE_MODEL_INDEX.json"
            _m = json.loads(_idx.read_text()) if _idx.is_file() else {}
            _m[f"{task['id']}_rung{rung_i + 1}_response.md"] = tag
            _idx.write_text(json.dumps(_m, indent=1), encoding="utf-8")

            if task.get("report_only"):
                ok = len(resp.strip()) > 800
                _cy(f"[{task['id']}] {tag} report {len(resp)} chars in {el}s — "
                    f"{'RECORDED' if ok else 'TOO SHORT'}")
                rec["attempts"].append({"rung": rung_i + 1, "model": tag, "elapsed_s": el,
                                        "outcome": "REPORT_RECORDED" if ok else "REPORT_TOO_SHORT",
                                        "chars": len(resp)})
                if ok:
                    rec["outcome"] = "REPORT_RECORDED"
                    break
                continue

            if resp.count("<invoke") or resp.strip().startswith("<tool_calls>"):
                _cy(f"[{task['id']}] {tag} emitted a TOOL-CALL BLOCK, not an answer — "
                    f"CONFIGURATION failure, not a model failure")
                rec["attempts"].append({"rung": rung_i + 1, "model": tag, "elapsed_s": el,
                                        "chars": len(resp),
                                        "outcome": "CONFIG_ERROR_TOOLCALL_BLOCK"})
                continue
            _cy(f"[{task['id']}] {tag} returned {len(resp)} chars in {el}s — evaluating")
            v = BA.evaluate(resp, parent=parent)
            _cy(f"[{task['id']}] {tag} -> {v.outcome}  {v.detail}")
            if v.test_at_parent:
                _cy(f"[{task['id']}]      at parent: {v.test_at_parent}")
            if v.test_with_patch:
                _cy(f"[{task['id']}]      w/ patch : {v.test_with_patch}")
            rec["attempts"].append({
                "rung": rung_i + 1, "model": tag, "elapsed_s": el, "chars": len(resp),
                "outcome": v.outcome, "detail": v.detail,
                "test_at_parent": v.test_at_parent, "test_with_patch": v.test_with_patch,
                "suite_after": v.suite_after, "files": list(v.files_touched)})
            if v.accepted:
                rec["outcome"] = "ACCEPTED"
                rec["accepted_by"] = tag
                rec["files"] = list(v.files_touched)
                _cy(f"[{task['id']}] *** ACCEPTED from {tag} — {v.suite_after} ***")
                break
        else:
            rec["outcome"] = "HIL — rejected at every rung"
            _cy(f"[{task['id']}] HIL: rejected at every rung")
        if rec["outcome"] == "NOT_ATTEMPTED":
            rec["outcome"] = "HIL — rejected at every rung"
        results.append(rec)
        (LOGS / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")

    acc = sum(1 for r in results if r["outcome"] == "ACCEPTED")
    rep = sum(1 for r in results if r["outcome"] == "REPORT_RECORDED")
    n = len(results) - rep
    _cy(f"=== BUILD EXPERIMENT END — {acc} of {n} patch tasks ACCEPTED"
        f"{f', {rep} report(s) recorded' if rep else ''} ===")
    if n:
        rate = acc / n * 100
        _cy(f"    acceptance rate {rate:.0f}%. PRE-REGISTERED TELL: near 100% means the "
            f"checks are not binding; near 0% means the models cannot do the task; a "
            f"healthy result is a mix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
