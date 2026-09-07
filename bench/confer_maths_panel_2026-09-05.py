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
import panel_sandbox  # noqa: E402
_PANEL_SANDBOX_CWD: str | None = None
from experiment_11_orchestrator import set_panel_cwd  # noqa: E402
from experiment_11_orchestrator import accept_reply_or_work  # noqa: E402
from experiment_11_orchestrator import set_tool_log_sink  # noqa: E402
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
    # THE ADDITIVE STANDARD REACHES EVERY SEAT BY CONSTRUCTION (2026-09-07).
    # It had been pasted into ONE brief, on 2026-08-31, and into no standing
    # file and no system prompt -- so the rule governing whether work is
    # additive was itself an addition wired to nothing. Here it cannot be
    # omitted by whoever writes the next brief.
    "\n\n" "THE ADDITIVE STANDARD (founder, standing). Work is additive: it adds to the reliability, functionality, accuracy, robustness and stated aims of the project. NEVER disable or remove a feature -- removal ONLY when something better renders it redundant, and 'better' means a COMMITTED MEASUREMENT showing the replacement dominates on a named property. A judgement that something is better is not evidence that it is. Symmetrically: an addition that nothing reaches is not additive either -- every new flag, gate or entry point must be wired to a caller and executed by a test. Measured over this project's own record since 2026-08-01: 11 confirmed defects were additions that did nothing, and 0 were removals of something needed."
    # THE SEAT GETS ONE TURN (2026-09-07). Diagnosed after fable spent 647 s,
    # made 0 tool calls, and returned "I'll hold until the completion
    # notification" -- a reply only reachable in a multi-turn session.
    # `claude -p` is one-shot: the turn that ends IS the answer. Nothing we
    # sent corrected that belief, because the prompt never said so.
    "\n\n"
    "THIS IS A ONE-SHOT DISPATCH. You will NOT be re-invoked and there is no "
    "later turn. Do not end your turn waiting for a background task or a "
    "notification: whatever you have written when the turn ends IS your answer. "
    "Do not start the full test suite -- it takes over 8 minutes and you will "
    "lose the budget waiting. Run targeted tests instead. If you run short of "
    "time, WRITE YOUR FINDINGS SO FAR. A partial answer carrying evidence is "
    "worth everything; a holding note is worth nothing."
)


def dispatch(name, model_id, route):
    # SET THE SANDBOX CWD ON *THIS* THREAD (2026-09-06). `_PANEL_CWD_TLS` is a
    # `threading.local()`, and this function runs inside a ThreadPoolExecutor, so a
    # value set on the main thread is invisible here -- each worker reads its own,
    # which is None. Proven: main sees the path, both pool workers see None.
    #
    # That is why the first attempt at founder ruling 35's second half FAILED
    # SILENTLY: main logged "seats confined to a copy", every worker passed
    # cwd=None, and the seats ran in the live repository. cc2 caught it by running
    # `pwd`, and fable had already written a file into the canonical tree.
    if _PANEL_SANDBOX_CWD:
        set_panel_cwd(_PANEL_SANDBOX_CWD)
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
    Every tool call made by a `claude_cli` or `openrouter` seat is recorded in
    the seat's JSON, so the claim "this panel used tools" is checkable rather
    than asserted. The `deepseek` branch is the remaining gap: it is passed
    TOOL_SPECS but returns only text, so its n_tool_calls is still structurally
    0 and must be read as "not recorded", never as "ran nothing".
    """
    t0 = time.time()
    tool_log = []
    try:
        if route == "claude_cli":
            # 900s, NOT the 300s default. THE PROJECT ALREADY LEARNED THIS AND I
            # DID NOT CARRY IT ACROSS. experiment_11_orchestrator.py:136 sets
            # `timeout=900,  # WP4a: 300->900s to prevent CC2 timeout cascade`
            # for exactly this seat. This dispatcher took the function default
            # instead, so on 2026-09-06 the cc2 seat failed 3 attempts at 300s
            # each -- 900s of wall clock producing nothing -- on a brief that
            # fable completed in 237s. The seat did not fail on merit; it ran out
            # of clock while executing the tool work the brief demanded, and the
            # seat that was asked to DEFEND the proposal was the one lost.
            # 1800s, raised from 900 on 2026-09-07: BOTH seats hit the 900 s wall
            # with 0 chars on a brief that asked them to run archive-scanning
            # work. The clock, not the task, was the binding constraint.
            # THE SUBSTANCE TEST WAS BUILT AND NEVER PASSED HERE.
            # accept_reply_or_work (experiment_11_orchestrator.py:781) exists for
            # exactly this and takes the sandbox path: it accepts a SHORT reply
            # only when real work sits beside it, and rejects a holding note.
            # Without it a 168-character "I'll hold until..." was recorded as
            # ok=True and counted as a seat that answered. max_retries=2 bounds
            # the cost.
            # THE TOOL-CALL COUNTER WAS 0 BY CONSTRUCTION, NOT BY MEASUREMENT.
            # 2026-09-07. `tool_log` is initialised empty and, on this branch,
            # was never assigned again -- only the `openrouter` branch below
            # ever set it. So `n_tool_calls` read 0 for cc2 and fable on every
            # panel ever run here, however much work the seats actually did,
            # while the docstring above promised the opposite: "Every tool call
            # made by every seat is recorded in the seat's JSON, so the claim
            # 'this panel used tools' is itself checkable rather than asserted."
            # It was not checkable. It was 0 with no way to be anything else.
            #
            # Concretely, fable.json of 2026-09-06 23:01 carries n_tool_calls 0
            # beside a reply quoting verbatim `pwd` output and a real sandbox
            # path -- unreadable as either proof or fabrication, because the
            # only field that could tell them apart was hard-wired to 0.
            #
            # BUILT AND UNWIRED, again, and this file NAMES that shape 40 lines
            # below about `set_panel_cwd`: "carried this at HIGH ... describing
            # the confinement half as unbuilt when in fact it was built and
            # unwired -- the project's most repeated failure shape." The sibling
            # mechanism, in the same file, had the same defect at the same time.
            #
            # `set_tool_log_sink` (experiment_11_orchestrator.py:331) is thread-
            # local, which is what makes it safe under the ThreadPoolExecutor
            # below, and setting it also switches the CLI from --output-format
            # text to stream-json, which is the ONLY format carrying tool_use
            # blocks. Pattern copied from confer_panel_2026-08-28.py:173, the 1
            # of 37 dispatchers that had it right.
            _sink = LOGS / f"{name}.tools.json"
            # A STALE SINK WOULD BE READ AS THIS RUN'S (cc2, 2026-09-07). Two
            # dispatches into the same LOGS directory -- exactly what a
            # PANEL_ONLY re-dispatch does -- would otherwise report the earlier
            # run's tool calls as belonging to this one.
            _sink.unlink(missing_ok=True)
            set_tool_log_sink(str(_sink))
            try:
                resp = call_claude_cli(
                    model_id, SYSTEM, PROMPT, timeout=1800, max_retries=2,
                    accept=accept_reply_or_work(_PANEL_SANDBOX_CWD or str(_REPO)),
                )  # native Bash
            finally:
                set_tool_log_sink(None)
            # Read the sink BACK into the seat record. The reference dispatcher
            # leaves it in a side file, which keeps n_tool_calls wrong in the
            # record a reader actually opens.
            if _sink.is_file():
                try:
                    tool_log = json.loads(_sink.read_text(encoding="utf-8")).get("calls", [])
                except (OSError, ValueError) as _e:  # noqa: BLE001
                    print(f"  [{name}] tool log unreadable: {_e}", flush=True)
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
        # KEEP THE COUNTER KEYS ON THE FAILURE PATH (cc2, 2026-09-07). Without
        # them the log line printed `tools=native` for a seat that CRASHED,
        # which reads as "this route has no counter" rather than "this seat
        # failed", and any calls made before the failure were dropped.
        out = {"model": name, "route": route, "ok": False,
               "error": f"{type(e).__name__}: {e}",
               "tool_calls": tool_log, "n_tool_calls": len(tool_log),
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

    # SEATS WORK IN A COPY, NOT THE LIVE TREE (founder ruling 35, second half,
    # 2026-09-06). `--allowedTools` already withholds Write and Edit and says "No
    # file modification", and a seat still edited 4 tracked files -- through Bash,
    # which no tool list can restrain. Confinement has to be positional.
    #
    # The cwd mechanism has existed since August (`set_panel_cwd`, fail-closed on a
    # bad path) and was never called. Runway 0C.9 has carried this at HIGH since
    # then, describing the confinement half as unbuilt when in fact it was built
    # and unwired -- the project's most repeated failure shape.
    global _PANEL_SANDBOX_CWD
    baseline = panel_sandbox.fingerprint(_REPO)
    # THE CONTROL PLANE IS OUTSIDE THE REPO AND WAS UNWATCHED (2026-09-07).
    # A seat wrote to the operator's real ~/.claude/settings.json at 15:04:45
    # and `canonical_was_touched` did not fire, because it digests the repo's
    # tracked files and $HOME is not among them. That write appended a hook --
    # code that then runs on every turn of every unrelated session.
    home_baseline = panel_sandbox.control_plane_fingerprint()
    sandbox = panel_sandbox.build(_REPO)
    _PANEL_SANDBOX_CWD = str(sandbox)      # workers read this and set their own TLS
    print(f"    seats confined to a copy: {sandbox}")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
            futs = {pool.submit(dispatch, n, m, r): n for n, m, r in MODELS}
            results = [f.result() for f in concurrent.futures.as_completed(futs)]
    finally:
        _PANEL_SANDBOX_CWD = None
        set_panel_cwd(None)
        # KEEP what a seat changed rather than discarding it. The 2026-09-06 seat's
        # edit was CORRECT -- it repaired a real false-convergence path -- so
        # throwing such work away to enforce hygiene would be its own loss. It
        # returns as a PROPOSAL for CC1 to test under f and sy, which is what the
        # founder asked for.
        proposals = panel_sandbox.changes(sandbox, _REPO)
        if proposals:
            (LOGS / "seat_proposals.diff").write_text(
                "\n".join(f"### {rel}\n{d}" for rel, d in sorted(proposals.items())),
                encoding="utf-8")
            print(f"    seats proposed edits to {len(proposals)} file(s) IN THE COPY "
                  f"-> {LOGS / 'seat_proposals.diff'} (untested; not applied)")
        # DETECTION for what a sandbox cannot prevent: a seat writing to an
        # absolute path it already knows. vault_keys.sh records that limit exactly.
        home_touched = panel_sandbox.control_plane_was_touched(home_baseline)
        if home_touched:
            print(f"    *** OPERATOR CONTROL PLANE MODIFIED DURING THE PANEL: "
                  f"{home_touched} ***")
            (LOGS / "control_plane_touched.json").write_text(
                json.dumps(home_touched, indent=2), encoding="utf-8")
        touched = panel_sandbox.canonical_was_touched(baseline, _REPO)
        if touched:
            print(f"    *** CANONICAL TREE MODIFIED DURING THE PANEL: {touched} ***")
            (LOGS / "canonical_touched.json").write_text(
                json.dumps(touched, indent=2), encoding="utf-8")
        else:
            print("    canonical tree unchanged (7900 tracked files re-hashed)")
        panel_sandbox.teardown(sandbox)

    ok = sum(1 for r in results if r["ok"])
    print(f"\n  {ok}/{len(MODELS)} responded. Logs: {LOGS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
