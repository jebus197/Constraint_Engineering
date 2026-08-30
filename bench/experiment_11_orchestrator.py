#!/usr/bin/env python3
"""Experiment 11: Five-Model Distributed Compute Orchestrator.

Dispatches prompts to CC2, ChatGPT (via OpenRouter), Codex (via codex exec),
Gemini (via Google API), and DeepSeek (via DeepSeek API). CC1 (this script's
caller) is collator only — no synthesis, no P-passes, no stop decisions.

All settings from EXECUTION_PLAN_EXPERIMENT_11.md.
"""

from __future__ import annotations

import glob as globmod
import json
import os
import shutil
import pathlib
import subprocess
import threading
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional


# ---------------------------------------------------------------------------
# Claude CLI discovery (shared by all dispatch code)
# ---------------------------------------------------------------------------

def _find_claude_cli() -> Optional[str]:
    """Find claude CLI binary — checks PATH then macOS app bundle locations."""
    found = shutil.which("claude")
    if found:
        return found

    # macOS app bundle locations (newest version first)
    app_support = Path.home() / "Library" / "Application Support" / "Claude"
    patterns = [
        str(app_support / "claude-code" / "*" / "claude.app" / "Contents" / "MacOS" / "claude"),
        str(app_support / "claude-code-vm" / "*" / "claude"),
    ]
    for pattern in patterns:
        matches = sorted(globmod.glob(pattern), reverse=True)
        if matches and os.path.isfile(matches[0]):
            return matches[0]

    return None


CLAUDE_CLI: Optional[str] = _find_claude_cli()


# ---------------------------------------------------------------------------
# Configuration dataclasses (UX-readiness: all config is parameterised)
# ---------------------------------------------------------------------------

Role = Literal["collator", "player_manager", "participant"]


@dataclass
class ModelConfig:
    """Configuration for a single model participant.

    Primary/secondary routing (2026-05-22, founder-directed): every model
    may carry a secondary route (`secondary_api` + `secondary_model_id`)
    used as a one-shot fallback when the primary route returns empty
    content for a given turn. The fallback is in-round (the model never
    misses a round per `feedback_no_benching.md`), and the next turn
    reverts to primary unless empty again. Secondary fields are optional
    — models without a secondary fail honestly when the primary fails.
    """
    label: str
    model_id: str
    api: str  # "openrouter", "claude_cli", "codex_exec", "google", "deepseek"
    role: Role
    system_prompt_path: str | None  # None for collator
    max_tokens: int = 32768
    timeout: int = 300
    max_retries: int = 3
    backoff_base: float = 3.0
    extra_body: dict | None = None  # Model-specific API params (e.g. reasoning.effort)
    secondary_api: str | None = None  # Fallback route on primary empty
    secondary_model_id: str | None = None  # Fallback model id (route-specific)


@dataclass
class ExperimentConfig:
    """Full experiment configuration — drives the orchestrator."""
    models: list[ModelConfig]
    logs_dir: Path = Path("bench/logs/experiment_11")
    budget_limit: float = 20.0
    cdsfl_system_prompt: str = ""

    def get_by_role(self, role: Role) -> list[ModelConfig]:
        return [m for m in self.models if m.role == role]

    def get_by_label(self, label: str) -> ModelConfig | None:
        for m in self.models:
            if m.label == label:
                return m
        return None


# ---------------------------------------------------------------------------
# Default configuration for Experiment 11
# ---------------------------------------------------------------------------

def load_default_config() -> ExperimentConfig:
    """Load the Experiment 11 configuration from environment and files."""
    repo_root = Path(__file__).resolve().parent.parent
    cdsfl_path = repo_root / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"

    if not cdsfl_path.exists():
        raise FileNotFoundError(f"CDSFL system prompt not found: {cdsfl_path}")

    cdsfl_text = cdsfl_path.read_text(encoding="utf-8")

    # Primary/secondary routing (2026-05-22, founder-directed): every
    # model carries a secondary route used as a one-shot in-round
    # fallback when its primary route returns empty / raises after
    # retries. The secondary is selected to (a) hit the same underlying
    # model where possible (consistency), (b) keep billing consolidated
    # (founder is intentionally limiting multi-vendor subscriptions).
    # ChatGPT and Codex both share `codex_exec` as secondary — both
    # target GPT-5.5 and `codex` CLI is already subscribed and auth-ed.
    models = [
        ModelConfig(
            label="CC2",
            model_id="opus",
            api="claude_cli",
            role="player_manager",
            system_prompt_path=str(cdsfl_path),
            max_tokens=32768,
            timeout=900,       # WP4a: 300→900s to prevent CC2 timeout cascade
            max_retries=1,     # WP4a: 3→1 to avoid 3× timeout cascade
            secondary_api="openrouter",
            secondary_model_id="anthropic/claude-opus-4.7",
        ),
        ModelConfig(
            label="Codex",
            model_id="openai/gpt-5.5",
            api="openrouter",
            role="participant",
            system_prompt_path=str(cdsfl_path),
            max_tokens=32768,
            timeout=300,
            max_retries=3,
            # Run 6: switched from codex_exec to openrouter. Eliminates the
            # catastrophic decomposed fallback (45-80 min/round) and the
            # brittle CLI auth dependency. Same model, direct API.
            secondary_api="codex_exec",
            secondary_model_id="gpt-5.5",
        ),
        ModelConfig(
            label="ChatGPT",
            model_id="openai/gpt-5.5",
            api="openrouter",
            role="participant",
            system_prompt_path=str(cdsfl_path),
            max_tokens=32768,
            timeout=300,
            max_retries=3,
            secondary_api="codex_exec",
            secondary_model_id="gpt-5.5",
        ),
        ModelConfig(
            label="Gemini",
            model_id="google/gemini-3.1-pro-preview",
            api="openrouter",
            role="participant",
            system_prompt_path=str(cdsfl_path),
            max_tokens=32768,
            timeout=300,
            max_retries=5,
            backoff_base=3.0,
            extra_body={"reasoning": {"effort": "high"}},
            secondary_api="google",
            secondary_model_id="gemini-3.1-pro-preview",
        ),
        ModelConfig(
            label="DeepSeek",
            model_id="deepseek-v4-pro",
            api="deepseek",
            role="participant",
            system_prompt_path=str(cdsfl_path),
            max_tokens=32768,
            timeout=300,
            max_retries=3,
            secondary_api="openrouter",
            secondary_model_id="deepseek/deepseek-v4-pro",
            # Routing change 2026-05-20 (founder-directed): reverted
            # from OpenRouter slug `deepseek/deepseek-v4-pro` back to
            # the direct DeepSeek API (`deepseek-v4-pro`, base_url
            # api.deepseek.com). The direct path has reasoning-budget
            # mitigation (max_tokens halving on empty + reasoning_content
            # diagnostic logging, see call_deepseek) that the OpenRouter
            # path lacks; the confers already use this route and it
            # works. Cheaper than OpenRouter for DeepSeek. max_tokens
            # raised from 16384 to match the call_deepseek default
            # (which is what the confers use successfully).
        ),
    ]

    return ExperimentConfig(
        models=models,
        logs_dir=repo_root / "bench" / "logs" / "experiment_11",
        budget_limit=20.0,
        cdsfl_system_prompt=cdsfl_text,
    )


# ---------------------------------------------------------------------------
# API dispatch functions
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")  # local time (was UTC — Run 7 fix)
    print(f"[{ts}] {msg}", file=sys.stderr)


class CircuitBreakerTripped(Exception):
    """Raised when a halt condition is detected."""
    def __init__(self, condition: str, model: str, phase: str, detail: str = ""):
        self.condition = condition
        self.model = model
        self.phase = phase
        self.detail = detail
        super().__init__(f"HALT [{condition}] model={model} phase={phase}: {detail}")

    def __reduce__(self):
        # Pickle-safe across the multiprocessing.Queue boundary in
        # runner_core.dispatch_to_model. Default Exception pickling
        # reconstructs from self.args (the single super().__init__()
        # string) -> a 1-arg __init__ call -> "TypeError: missing 2
        # required positional arguments: 'model' and 'phase'", which the
        # runner's broad except then masked as a generic failure and the
        # circuit breaker became silently inoperative arc-wide.
        # Reconstruct from the 4 original args instead. (Exp 40 Unit
        # B->C seam, 2026-05-18; root-caused + P-passed via real
        # multiprocessing.Queue round-trip.)
        return (self.__class__,
                (self.condition, self.model, self.phase, self.detail))


# ---------------------------------------------------------------------------
# Tool-calling support ("tools decide" integration, 3 June 2026)
# ---------------------------------------------------------------------------
# GATED + DEFAULT OFF. The OpenAI-compatible routes (call_openrouter,
# call_deepseek) gain an OPTIONAL tool-call loop so a reviewing model can run
# Python during analysis and attach runnable falsifiers (smoke-tested in
# bench/smoketest_toolcall_2026-06-03.py + bench/smoketest_falsifier_2026-06-03.py).
# When tools=None (the default) the routes behave byte-identically to before:
# none of this code executes. claude_cli already exposes tools natively via
# --allowedTools (Bash/Read/...); see call_claude_cli.

# Single execute_python tool the reviewing model calls. The executor behind it
# (bench/falsifier_verify.execute_python) sandboxes the run: 30 s timeout, temp
# cwd, repo importable via PYTHONPATH, read/import only.
EXECUTE_PYTHON_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_python",
        "description": (
            "Execute a Python 3 snippet and return its stdout/stderr. The full "
            "local STEM toolset is importable: sympy, numpy, scipy, statsmodels, "
            "mpmath, z3, sklearn, networkx, pandas, plus stdlib (ast, math, etc.). "
            "The repository is importable, so you can `from bench.dm... import ...` "
            "to test the REAL target code. Print results you want to see."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source to run."}
            },
            "required": ["code"],
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Panel working directory
#
# The shell-bearing routes (claude_cli, codex_exec) inherit the runner's cwd.
# For code experiments that is correct — the panel reviews code in this repo and
# needs to reach it. For the exam experiments it is not: the target is staged
# outside the tree precisely so the panel cannot reach the scoring key, and a cwd
# of the repo hands back a filesystem that names the key's location (config
# notes), holds superseded keys in git history, and sits one `cd` from anything.
#
# Confirmed live on 2026-07-29: during Exp 48 a routed model wrote a falsifier
# that opened the answer key and printed the full planted set. The key had been
# moved out of the repo that morning; the note recording WHERE it moved to was
# committed inside the repo 76 minutes before the run. The fix advertised what
# it hid, and the panel's cwd is what made the note reachable.
#
# Exam configs set panel_cwd to the staged target directory. Unset (None) keeps
# the previous behaviour exactly, so code experiments are unaffected.
# THREAD-LOCAL, NOT GLOBAL. Measured failure, 2026-08-30.
#
# This was a module-level global, and `confer_panel_2026-08-28.py` dispatches its
# reviewers concurrently through a ThreadPoolExecutor. Each reviewer sets the cwd
# to its own throwaway worktree and clears it in a `finally`. So the FIRST
# reviewer to finish cleared the cwd for the one still running:
#
#   01:01:49  both worktrees created, cwd set twice
#   01:30:34  fable finishes -> its finally sets the shared cwd to None
#   01:41:49  cc2 times out and RETRIES -- now with cwd None, i.e. THE CANONICAL
#             REPOSITORY, with Bash in its allowed tools
#
# cc2 caught it itself (`git worktree list` said `main`), built its own worktree
# and verified the tracked tree byte-clean either side. CC1 had examined the same
# "(inherited -- repo)" log line earlier that night and cleared it as a false
# alarm, having checked that the worktrees were CREATED and never that the shared
# state survived a concurrent completion. Checked one member, again.
#
# A thread-local makes each dispatch own its own value, so one reviewer's cleanup
# cannot unsandbox another. Single-threaded callers are unaffected: the default is
# still None and the semantics are identical.
_PANEL_CWD_TLS = threading.local()

#: Where to write a dispatch's tool-call log, or None. Thread-local for the same
#: reason the cwd is: the confer dispatcher runs reviewers concurrently, and a
#: module global would let one reviewer's cleanup clobber another's (measured
#: 2026-08-30 -- it unsandboxed a live reviewer).
_TOOL_LOG_TLS = threading.local()


def set_tool_log_sink(path: "str | None") -> None:
    """Record this thread's dispatch tool calls to `path` (JSON), or stop."""
    _TOOL_LOG_TLS.value = path


def _get_tool_log_sink() -> "str | None":
    return getattr(_TOOL_LOG_TLS, "value", None)


def _parse_stream_json(raw: str):
    """(final_text, [{"name":..., "input_preview":...}, ...]) from a stream-json run."""
    final, calls = "", []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        for blk in ((rec.get("message") or {}).get("content") or []):
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "tool_use":
                calls.append({"name": blk.get("name"),
                              "input_preview": json.dumps(blk.get("input") or {})[:400]})
            elif blk.get("type") == "text" and rec.get("type") == "assistant":
                final = blk.get("text") or final
        if rec.get("type") == "result" and isinstance(rec.get("result"), str):
            final = rec["result"] or final
    return final.strip(), calls



def _get_panel_cwd_raw() -> str | None:
    return getattr(_PANEL_CWD_TLS, "value", None)


def set_panel_cwd(path: str | None) -> None:
    """Set the working directory for shell-bearing panel dispatches.

    None restores inheritance of the runner's cwd (the code-experiment default).
    A non-existent path is refused rather than silently ignored: failing open
    here would put the panel back in the repo, which is the exposure this
    exists to close.
    """
    if path is not None:
        p = Path(path).expanduser()
        if not p.is_dir():
            raise NotADirectoryError(f"panel_cwd is not a directory: {path}")
        path = str(p.resolve())
    _PANEL_CWD_TLS.value = path
    _log(f"[panel] working directory: {path or '(inherited — repo)'}")


def get_panel_cwd() -> str | None:
    """Current panel working directory, or None if inherited."""
    return _get_panel_cwd_raw()


def default_tool_executor(name: str, args: dict) -> str:
    """Default dispatcher for tool calls: maps the execute_python tool to the
    sandboxed executor in bench/falsifier_verify. Returns the tool result text.

    Imported lazily so the orchestrator has no import-time dependency on the
    falsifier module (keeps existing non-tool dispatch unaffected).
    """
    if name == "execute_python":
        from falsifier_verify import execute_python as _exec
        code = args.get("code", "")
        return _exec(code) if code else "[no code provided]"
    return f"[unknown tool: {name}]"


# ─────────────────────────────────────────────────────────────────────────────
# DeepSeek content-emitted tool-call recovery
#
# deepseek-v4-pro, when called through its direct OpenAI-compatible endpoint
# (base_url https://api.deepseek.com) with the OpenAI tools/tool_choice="auto"
# params, does NOT return its tool invocation in the structured
# message.tool_calls field. Under the heavy CDSFL system prompt it instead
# emits its native internal tool-call special tokens as plain message CONTENT.
# The leaked markup uses U+FF5C (FULLWIDTH VERTICAL LINE, the character ｜,
# NOT ASCII |) as the delimiter, in this exact shape:
#   <｜｜DSML｜｜tool_calls>
#     <｜｜DSML｜｜invoke name="execute_python">
#       <｜｜DSML｜｜parameter name="code" string="true"> <python> </…parameter>
#     </｜｜DSML｜｜invoke>
#   </｜｜DSML｜｜tool_calls>
# _run_openai_tool_loop reads only message.tool_calls; for DeepSeek that is
# empty, so without recovery the loop returns the raw markup as the "final
# answer" and never runs the model's intended falsifier. The fullwidth-pipe
# sentinel cannot occur in genuine ASCII prose, so detection is false-positive
# safe and the recovery only fires inside the gated tool loop.
import re as _re  # noqa: E402

_DSML_PIPE = "｜"  # U+FF5C FULLWIDTH VERTICAL LINE — DeepSeek special-token delimiter
_DSML_SENTINEL = f"<{_DSML_PIPE * 2}DSML{_DSML_PIPE * 2}tool_calls>"
_DSML_INVOKE_RE = _re.compile(
    rf"<{_DSML_PIPE}{_DSML_PIPE}DSML{_DSML_PIPE}{_DSML_PIPE}invoke name=\"(?P<name>[^\"]+)\">"
    rf"(?P<body>.*?)</{_DSML_PIPE}{_DSML_PIPE}DSML{_DSML_PIPE}{_DSML_PIPE}invoke>",
    _re.DOTALL,
)
_DSML_PARAM_RE = _re.compile(
    rf"<{_DSML_PIPE}{_DSML_PIPE}DSML{_DSML_PIPE}{_DSML_PIPE}parameter name=\"(?P<pname>[^\"]+)\""
    rf"(?: string=\"[^\"]*\")?>(?P<pval>.*?)</{_DSML_PIPE}{_DSML_PIPE}DSML{_DSML_PIPE}{_DSML_PIPE}parameter>",
    _re.DOTALL,
)


def _parse_deepseek_content_toolcalls(content: str):
    """Return list[(name, args_dict)] if DeepSeek leaked tool-call markup into
    content (U+FF5C-delimited DSML tokens), else None. Detection sentinel uses
    the fullwidth pipe, which never appears in genuine ASCII prose answers.
    """
    if not content or _DSML_SENTINEL not in content:
        return None
    calls = []
    for m in _DSML_INVOKE_RE.finditer(content):
        args = {
            pm.group("pname"): pm.group("pval").strip("\n")
            for pm in _DSML_PARAM_RE.finditer(m.group("body"))
        }
        calls.append((m.group("name"), args))
    return calls or None


# Strip any DeepSeek DSML special-token tag (U+FF5C-delimited) from text,
# leaving the underlying plain content. Used as a last-resort cleanup so raw
# special-token markup is never returned to the caller as a "final answer"
# when the model emitted markup on a turn the loop treats as terminal (the
# structured parser handles the in-loop tool-execution case; this only cleans
# residual delimiters out of a final string).
_DSML_TAG_RE = _re.compile(rf"</?{_DSML_PIPE}{_DSML_PIPE}DSML{_DSML_PIPE}{_DSML_PIPE}[^>]*>")


def _strip_dsml_markup(text: str) -> str:
    """Remove DeepSeek DSML special-token tags, returning the inner content."""
    return _DSML_TAG_RE.sub("", text)


def _run_openai_tool_loop(
    client,
    model_id: str,
    messages: list[dict],
    tools: list[dict],
    tool_executor,
    max_iters: int = 6,
    max_tokens: int = 32768,
    timeout: int = 300,
    extra_body: dict | None = None,
) -> str:
    """Run an OpenAI-compatible tool-call loop and return the model's final text.

    Loop shape reused from the validated smoke tests: on each turn, if the model
    requests tool calls, run them via ``tool_executor(name, args)``, append the
    results, and continue; otherwise return the assistant's content. Bounded by
    ``max_iters`` (default 6) so a model that loops on tools cannot run forever.

    ``tool_executor`` is ``Callable[[str, dict], str]`` — the orchestrator's
    sandboxed default is :func:`default_tool_executor`.
    """
    final = ""
    for _ in range(max_iters):
        create_kwargs = dict(
            model=model_id,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=max_tokens,
            temperature=0.0,
            timeout=timeout,
        )
        if extra_body:
            create_kwargs["extra_body"] = extra_body
        # Retry transient empty-choices (observed 2026-06-06: gemini-3.1 via
        # OpenRouter returned no choices on ONE mid-loop iteration after 500s of
        # healthy turns — an intermittent upstream blip, not a real failure). Retry
        # the same request a couple of times before tripping the breaker, so a
        # single flaky response cannot crap out a whole round.
        resp = None
        for _attempt in range(3):
            resp = client.chat.completions.create(**create_kwargs)
            if resp.choices:
                break
            time.sleep(2.0)
        if not resp or not resp.choices:
            raise CircuitBreakerTripped(
                "empty_response", model_id, "dispatch",
                "API returned no choices during tool loop (after retries)",
            )
        msg = resp.choices[0].message
        tcs = getattr(msg, "tool_calls", None) or []
        if not tcs:
            content = msg.content or ""
            parsed = _parse_deepseek_content_toolcalls(content)
            if parsed:
                # DeepSeek leaked its tool call into content as DSML markup
                # (no structured tool_calls). Run it through the same executor
                # and continue the loop so the model gets results and can
                # synthesise a real final answer. The result is fed as a user
                # turn rather than a role:tool message because there is no valid
                # tool_call_id to reference (the API never produced one).
                messages.append({"role": "assistant", "content": content})
                for name, args in parsed:
                    result = tool_executor(name, args)
                    messages.append({
                        "role": "user",
                        "content": f"[tool:{name} result]\n{(result or '')[:4000]}",
                    })
                continue
            final = content.strip()
            if not final:
                # Empty visible content: a reasoning model (Gemini, DeepSeek) burned
                # the whole output budget on chain-of-thought (finish_reason
                # 'length'), leaving no room for the answer. Retry TOOL-LESS with a
                # large budget so visible content has room, keeping the caller's
                # reasoning config (only nudge one in if none was supplied). This
                # MUST fire even when extra_body is set — Gemini ALWAYS sets
                # reasoning.effort, and the prior `not extra_body` gate meant Gemini
                # never got this retry, so its synthesis emptied intermittently on
                # BOTH the whole and decomposed paths (2026-06-06 fix). Dropping
                # tools forces a content answer rather than another tool call. A few
                # transient empties (empty body) also resolve on a re-request.
                bumped = dict(create_kwargs)
                bumped["max_tokens"] = max(max_tokens, 65536)
                bumped.pop("tools", None)
                bumped.pop("tool_choice", None)
                if not extra_body:
                    bumped["extra_body"] = {"reasoning": {"effort": "medium"}}
                for _retry in range(2):
                    try:
                        resp2 = client.chat.completions.create(**bumped)
                    except Exception:  # noqa: BLE001
                        resp2 = None
                    if resp2 and resp2.choices:
                        m2 = resp2.choices[0].message
                        if not (getattr(m2, "tool_calls", None) or []):
                            cand = (m2.content or "").strip()
                            if cand:
                                final = cand
                                break
                    time.sleep(2.0)
            break
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in tcs],
        })
        for tc in tcs:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = tool_executor(tc.function.name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": (result or "")[:4000],
            })
    else:
        # max_iters exhausted while the model was STILL requesting tools — either
        # stuck retrying a bad import, OR (Gemini-3.1) a thorough reasoner that
        # calls a tool every turn and never volunteers a final answer. Force one
        # final answer WITHOUT tools so the model returns its synthesis rather
        # than empty text — a model must never crap out a whole round to a
        # runaway tool loop ("don't let models crap out"). Two requirements, both
        # empirically established 2026-06-06 against gemini-3.1-pro-preview:
        #   (1) an EXPLICIT stop-and-synthesise instruction — without it Gemini
        #       does not emit its findings on the forced turn;
        #   (2) a GENEROUS token budget — reasoning-heavy models burn ~20K+
        #       reasoning tokens on the final synthesis, so a small max_tokens
        #       leaves no room for visible content (the empty-response failure).
        # With both, gemini produced a 16.5K-char synthesis incl. a runnable
        # FALSIFIER at 6 tool exchanges. The accumulated tool results remain in
        # `messages`, so the model answers with full context.
        try:
            messages.append({
                "role": "user",
                "content": (
                    "Tool-use budget reached. Stop calling tools now and write "
                    "your COMPLETE findings as your final answer, in the required "
                    "format — each critical finding with its runnable FALSIFIER "
                    "python block."
                ),
            })
            final_kwargs = dict(
                model=model_id, messages=messages,
                max_tokens=max(max_tokens, 65536),
                temperature=0.0, timeout=max(timeout, 300),
            )
            if extra_body:
                final_kwargs["extra_body"] = extra_body
            # Retry the forced synthesis until it yields visible content — a
            # transient empty body or a budget-starved first attempt must not crap
            # out the round (2026-06-06).
            for _retry in range(3):
                resp = client.chat.completions.create(**final_kwargs)
                if resp.choices:
                    cand = (resp.choices[0].message.content or "").strip()
                    if cand:
                        final = cand
                        break
                time.sleep(2.0)
        except Exception:  # noqa: BLE001
            pass  # leave final as-is; the caller's empty-handling / re-ask covers it
    # Residual-markup guard: DeepSeek can emit DSML tool-call markup as content
    # on a turn the loop treats as final — either the forced-final tool-less call
    # above, OR an in-loop turn whose markup the structured parser could not
    # decompose into invoke/param pairs (sentinel present but no parseable call).
    # Raw fullwidth-pipe special-token markup must NEVER be returned as the final
    # answer: it is unparseable noise to the runner/scorer. If `final` still
    # carries the DSML sentinel, strip the special-token wrapper so the caller
    # receives the model's plain content (its prose/code) rather than the raw
    # delimiters. Only fires when the fullwidth-pipe sentinel is present, so
    # prose answers and native-tool_calls models are byte-identically unaffected.
    if final and _DSML_SENTINEL in final:
        final = _strip_dsml_markup(final).strip()
    return final


def call_openrouter(
    model_id: str,
    system_prompt: str | None,
    user_prompt: str,
    max_tokens: int = 32768,
    timeout: int = 300,
    max_retries: int = 3,
    backoff_base: float = 3.0,
    extra_body: dict | None = None,
    tools: list[dict] | None = None,
    tool_executor=None,
    max_tool_iters: int = 6,
) -> str:
    """Call a model via OpenRouter (bare-metal, CDSFL system prompt only).

    Tool-calling (GATED, default OFF): when ``tools`` is provided, the call runs
    an OpenAI tool-call loop (max ``max_tool_iters`` iterations) so the model can
    execute Python during analysis; tool calls are dispatched through
    ``tool_executor(name, args)`` (defaults to :func:`default_tool_executor`,
    which sandboxes execute_python). When ``tools`` is None the behaviour is
    byte-identical to the original single-shot completion path.
    """
    try:
        import openai
    except ImportError:
        raise RuntimeError("openai package not installed: pip install openai")

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    # Explicit httpx timeout prevents indefinite hangs when TCP connections
    # drop to CLOSED state (Exp15 fix: PID 39633 hung for >1 hour).
    try:
        import httpx
        http_timeout = httpx.Timeout(
            connect=30.0,
            read=float(timeout),
            write=30.0,
            pool=30.0,
        )
    except ImportError:
        http_timeout = timeout

    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=http_timeout,
    )

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    last_error = None
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            _log(f"  [openrouter:{model_id}] retry {attempt}/{max_retries}")
        t0 = time.monotonic()
        try:
            if tools:
                # GATED tool-call path: fresh message copy per attempt (the
                # loop appends tool turns; a retry must restart from seed).
                executor = tool_executor or default_tool_executor
                text = _run_openai_tool_loop(
                    client, model_id, list(messages), tools, executor,
                    max_iters=max_tool_iters, max_tokens=max_tokens,
                    timeout=timeout, extra_body=extra_body,
                ).strip()
                elapsed = time.monotonic() - t0
                _log(f"  [openrouter:{model_id}] done (tools, {elapsed:.1f}s, {len(text)} chars)")
                if not text:
                    raise CircuitBreakerTripped(
                        "empty_response", model_id, "dispatch",
                        f"Empty response body after {elapsed:.1f}s (tool loop)"
                    )
                return text
            create_kwargs = dict(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.0,
                timeout=timeout,
            )
            if extra_body:
                create_kwargs["extra_body"] = extra_body
            response = client.chat.completions.create(**create_kwargs)
            elapsed = time.monotonic() - t0
            if not response.choices:
                raise CircuitBreakerTripped(
                    "empty_response", model_id, "dispatch",
                    f"API returned no choices after {elapsed:.1f}s "
                    f"(possible upstream 500 error)"
                )
            text = response.choices[0].message.content or ""
            text = text.strip()
            _log(f"  [openrouter:{model_id}] done ({elapsed:.1f}s, {len(text)} chars)")
            if not text:
                raise CircuitBreakerTripped(
                    "empty_response", model_id, "dispatch",
                    f"Empty response body after {elapsed:.1f}s"
                )
            return text
        except CircuitBreakerTripped:
            raise
        except Exception as e:
            elapsed = time.monotonic() - t0
            last_error = e
            _log(f"  [openrouter:{model_id}] attempt {attempt} failed ({elapsed:.1f}s): {str(e)[:120]}")
            if attempt < max_retries and backoff_base > 0:
                time.sleep(backoff_base * (2 ** (attempt - 1)))

    raise RuntimeError(
        f"OpenRouter call failed after {max_retries} attempts for {model_id}. "
        f"Last error: {last_error}"
    )


def call_claude_cli(
    model_id: str,
    system_prompt: str | None,
    user_prompt: str,
    max_tokens: int = 32768,
    timeout: int = 300,
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> str:
    """Call Claude via claude CLI (Max subscription — no API credits needed).

    Does NOT use --bare: that flag skips keychain reads and demands an API key,
    which breaks OAuth outright (2026-07-29). See the note in the cmd list.
    Uses --system-prompt for native CDSFL delivery (unlike Codex which embeds
    in prompt body). Uses stdin piping for large prompts.

    Tool-calling: this route ALREADY exposes tools natively via --allowedTools
    (Bash/Read/Write/Edit/Grep/Glob/WebFetch/WebSearch below), so a reviewing
    model can run Python (via Bash) and import the real target during analysis.
    No gated parameter is needed here — unlike the OpenAI-compatible routes
    (call_openrouter, call_deepseek) which take an optional ``tools`` argument.
    """
    cli = CLAUDE_CLI
    if not cli:
        raise FileNotFoundError(
            "Claude CLI not found. Expected 'claude' in PATH or in "
            "~/Library/Application Support/Claude/claude-code/*/claude.app/Contents/MacOS/claude"
        )
    cmd = [
        cli, "-p",
        # --bare WAS ADDED HERE AND HAS BEEN REMOVED. 2026-07-29, same evening.
        #
        # It was added because an adversarial audit confirmed the operator's
        # auto-loaded ~/.claude/CLAUDE.md reaches every panel model, and that file
        # names this project's operational tracker as the first resource to
        # consult. The flag's stated purpose is to skip CLAUDE.md auto-discovery.
        #
        # But its help also says it skips KEYCHAIN READS and that "Anthropic auth
        # is strictly ANTHROPIC_API_KEY or apiKeyHelper". This operator is on a Max
        # subscription with OAuth and no API key, so --bare could never
        # authenticate: CC2 returned "Not logged in" for every headless dispatch
        # while interactive sessions worked perfectly. The flag did not break a
        # session, it selected an auth mode the account does not have. Adding a
        # confinement control switched off the credential store it depended on.
        #
        # The residual it was meant to close is smaller than it looked, and is
        # covered: ~/.claude/CLAUDE.md contains ZERO references to answer keys,
        # planted claims or the key store — verified by grep. All it does is NAME a
        # tracker at a Desktop path. To learn anything from that the panel must
        # READ that path, which is a home path outside the staged corpus, which
        # key_access_forensics scores as an out-of-scope open and which halts the
        # chain. Pointer in context, detected on use, exactly the layered position
        # taken everywhere else.
        "--model", model_id,
        # stream-json, not text, WHEN A TOOL-LOG SINK IS SET. `text` returns only
        # the final message, so a dispatch left NO EVIDENCE that the reviewer ran
        # anything at all. The founder, 2026-08-30: "I have yet to see any
        # evidence of them using tools either." That was not a doubt about the
        # models -- it was a real gap in what we record. Verified the same day:
        # stream-json surfaces `tool_use` blocks, text does not.
        *(["--output-format", "stream-json", "--verbose"]
          if _get_tool_log_sink() else ["--output-format", "text"]),
        "--no-session-persistence",
        # Write/Edit REMOVED 2026-07-29 (founder directive). A reviewing model
        # must not be able to modify the artefact it is reviewing: on 2026-07-29
        # Exp 47's frozen target was edited on disk and restored inside ~2 min,
        # leaving no trace in git or the round files. This also restores the
        # standing rule that fixes are SUGGESTED to HIL and never auto-applied
        # (feedback_fixes_hil_only) — fixes arrive as SEARCH/REPLACE text, which
        # the runner applies under its own control, not the model's.
        # NOTE: this alone is not sufficient — Bash can still write via shell
        # redirection, and Bash is required for the falsifier tool loop. The
        # enforcing control is the read-only staged target (stage_targets.sh);
        # the detecting control is the per-round target hash guard in
        # reference_runner_v2.py. Three layers, none of them relied on alone.
        "--allowedTools", "Bash", "Read", "Grep", "Glob", "WebFetch", "WebSearch",  # STEM tools via Bash (SymPy/z3/numpy/scipy); source via Read/Grep/Glob; research via WebFetch/WebSearch. No file modification.
    ]
    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    last_error = None
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            _log(f"  [claude-cli:{model_id}] retry {attempt}/{max_retries}")
        t0 = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
                input=user_prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=_get_panel_cwd_raw(),
            )
            elapsed = time.monotonic() - t0
            text = result.stdout.strip()
            _sink = _get_tool_log_sink()
            if _sink and text:
                text, _calls = _parse_stream_json(text)
                try:
                    pathlib.Path(_sink).write_text(json.dumps(
                        {"model": model_id, "elapsed_s": round(elapsed, 1),
                         "tool_calls": len(_calls), "calls": _calls}, indent=2),
                        encoding="utf-8")
                    _log(f"  [claude-cli:{model_id}] {len(_calls)} tool call(s) logged")
                except OSError as _e:                       # noqa: BLE001
                    _log(f"  [claude-cli:{model_id}] tool log not written: {_e}")
            if result.returncode != 0:
                stderr = result.stderr.strip()[:200]
                raise RuntimeError(
                    f"claude CLI returned {result.returncode}: {stderr}")
            _log(f"  [claude-cli:{model_id}] done ({elapsed:.1f}s, {len(text)} chars)")
            if not text:
                raise CircuitBreakerTripped(
                    "empty_response", model_id, "dispatch",
                    f"Empty stdout after {elapsed:.1f}s",
                )
            return text
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - t0
            last_error = TimeoutError(
                f"claude CLI timed out after {elapsed:.1f}s")
            _log(f"  [claude-cli:{model_id}] attempt {attempt} failed "
                 f"({elapsed:.1f}s): {last_error}")
        except CircuitBreakerTripped:
            raise
        except Exception as e:
            elapsed = time.monotonic() - t0
            last_error = e
            _log(f"  [claude-cli:{model_id}] attempt {attempt} failed "
                 f"({elapsed:.1f}s): {str(e)[:120]}")
            if attempt < max_retries and backoff_base > 0:
                time.sleep(backoff_base * (2 ** (attempt - 1)))

    raise RuntimeError(
        f"Claude CLI call failed after {max_retries} attempts for {model_id}. "
        f"Last error: {last_error}"
    )


def call_codex(
    user_prompt: str,
    cdsfl_directives: str,
    timeout: int = 600,
    max_retries: int = 1,
    use_output_schema: bool = False,
) -> str:
    """Call Codex via codex exec with CDSFL as elevated directives in prompt body.

    Uses stdin piping (CC2 confer F001: removes shell arg size limit) and
    optionally --output-schema (CC2 confer F006: forces structured findings).
    """
    # Codex exec has no --system-prompt flag. CDSFL goes in the prompt body
    # as elevated directives (lesson #12).
    full_prompt = (
        "=== SYSTEM INSTRUCTIONS (CDSFL Operating Constraints) ===\n"
        "The following constraints govern your output. Treat them as non-negotiable "
        "operating requirements, equivalent to a system prompt.\n\n"
        f"{cdsfl_directives}\n\n"
        "=== END SYSTEM INSTRUCTIONS ===\n\n"
        "=== TASK ===\n"
        f"{user_prompt}\n"
        "=== END TASK ==="
    )

    # Build command: stdin piping via "-" (CX confer F001)
    # Efficiency overrides (CX confer R2): disable MCP servers and plugins
    # (Linear/Notion/Figma/Playwright not needed for bench dispatch),
    # ephemeral mode (no session persistence overhead).
    # NOTE: reasoning_effort stays at default (xhigh) — founder decision
    # 2026-03-31: max capability required for complex tasks. Do not throttle.
    cmd = [
        "codex", "exec",
        "-c", "mcp_servers={}",
        "-c", "plugins={}",
        "--ephemeral",
    ]
    if use_output_schema:
        schema_path = Path(__file__).parent / "cdsfl_finding_schema.json"
        if schema_path.exists():
            cmd.extend(["--output-schema", str(schema_path)])
    cmd.append("-")  # read prompt from stdin

    last_error = None
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            _log(f"  [codex] retry {attempt}/{max_retries}")
        t0 = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=_get_panel_cwd_raw(),
            )
            elapsed = time.monotonic() - t0
            text = result.stdout.strip()
            if result.returncode != 0:
                stderr = result.stderr.strip()[:200]
                raise RuntimeError(f"codex exec returned {result.returncode}: {stderr}")
            _log(f"  [codex] done ({elapsed:.1f}s, {len(text)} chars)")
            if not text:
                raise CircuitBreakerTripped(
                    "empty_response", "Codex", "dispatch",
                    f"Empty stdout after {elapsed:.1f}s"
                )
            return text
        except CircuitBreakerTripped:
            raise
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - t0
            last_error = TimeoutError(f"codex exec timed out after {elapsed:.1f}s")
            _log(f"  [codex] timeout after {elapsed:.1f}s")
        except Exception as e:
            elapsed = time.monotonic() - t0
            last_error = e
            _log(f"  [codex] attempt {attempt} failed ({elapsed:.1f}s): {str(e)[:120]}")

    raise RuntimeError(f"Codex call failed after {max_retries} attempts. Last error: {last_error}")


def call_gemini(
    model_id: str,
    system_prompt: str | None,
    user_prompt: str,
    max_tokens: int = 32768,
    timeout: int = 300,
    max_retries: int = 5,
    backoff_base: float = 3.0,
) -> str:
    """Call Gemini via Google API with CDSFL as system_instruction."""
    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError:
        raise RuntimeError("google-genai package not installed: pip install google-genai")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY / GOOGLE_API_KEY not set")

    # Google genai uses httpx internally. Set explicit request timeout
    # to prevent indefinite hangs on dead TCP connections (Exp15 fix).
    try:
        import httpx as _httpx
        _http_client = _httpx.Client(timeout=_httpx.Timeout(
            connect=30.0, read=float(timeout), write=30.0, pool=30.0,
        ))
        client = genai.Client(api_key=api_key, http_options={"client": _http_client})
    except (ImportError, TypeError, ValueError) as _exc:
        # Fallback: if httpx not available, Client doesn't accept http_options,
        # or Pydantic ValidationError on newer genai versions
        client = genai.Client(api_key=api_key)

    last_error = None
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            _log(f"  [gemini:{model_id}] retry {attempt}/{max_retries}")
        t0 = time.monotonic()
        try:
            config = genai_types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                system_instruction=system_prompt if system_prompt else None,
            )
            response = client.models.generate_content(
                model=model_id,
                contents=user_prompt,
                config=config,
            )
            elapsed = time.monotonic() - t0
            if response.text is not None:
                text = response.text.strip()
                _log(f"  [gemini:{model_id}] done ({elapsed:.1f}s, {len(text)} chars)")
                if not text:
                    raise CircuitBreakerTripped(
                        "empty_response", model_id, "dispatch",
                        f"Empty response text after {elapsed:.1f}s"
                    )
                return text
            reason = "unknown"
            if response.candidates:
                reason = str(response.candidates[0].finish_reason)
            raise CircuitBreakerTripped(
                "empty_response", model_id, "dispatch",
                f"Response text is None, finish_reason={reason}"
            )
        except CircuitBreakerTripped:
            raise
        except Exception as e:
            elapsed = time.monotonic() - t0
            last_error = e
            _log(f"  [gemini:{model_id}] attempt {attempt} failed ({elapsed:.1f}s): {str(e)[:120]}")
            if attempt < max_retries:
                time.sleep(backoff_base)

    raise RuntimeError(
        f"Gemini call failed after {max_retries} attempts for {model_id}. "
        f"Last error: {last_error}"
    )


def call_deepseek(
    model_id: str,
    system_prompt: str | None,
    user_prompt: str,
    max_tokens: int = 32768,
    timeout: int = 300,
    max_retries: int = 3,
    backoff_base: float = 3.0,
    tools: list[dict] | None = None,
    tool_executor=None,
    max_tool_iters: int = 6,
) -> str:
    """Call DeepSeek via their OpenAI-compatible API.

    Tool-calling (GATED, default OFF): when ``tools`` is provided the call runs
    an OpenAI tool-call loop (max ``max_tool_iters`` iterations) via
    ``tool_executor(name, args)`` (default :func:`default_tool_executor`,
    sandboxed). The tool path uses the same hard per-attempt wall-clock cap as
    the non-tool path. When ``tools`` is None the behaviour is byte-identical to
    the original reasoning-content-salvage path below.

    DeepSeek Reasoner has a known failure mode: its chain-of-thought can
    consume the entire output token budget, leaving 0 tokens for the visible
    response. The API returns 200 OK with empty content. This is NOT an API
    error — the model genuinely ran out of output budget.

    Mitigation strategy:
    1. On empty response, check reasoning_content for salvageable output
    2. Retry with halved max_tokens (forces less internal reasoning budget)
    3. Only circuit-break after all retries produce empty responses
    """
    try:
        import openai
    except ImportError:
        raise RuntimeError("openai package not installed: pip install openai")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    # DeepSeek Reasoner can hold connections open for very long during
    # chain-of-thought.  Use explicit httpx timeout with:
    # - read timeout per chunk (prevents individual read hangs)
    # - HARD per-attempt wall clock via threading (prevents indefinite total)
    # Run 7 fix: read=timeout was per-chunk, not total. DeepSeek streamed
    # 85K chars of reasoning over 470s with each chunk succeeding, then
    # the retry hung indefinitely. Now: read=300s per chunk, total capped
    # at 2× timeout via threading.
    per_attempt_wall_cap = timeout * 2  # hard total per API call
    try:
        import httpx
        http_timeout = httpx.Timeout(
            connect=30.0,
            read=min(300.0, float(timeout)),  # per-chunk read cap
            write=30.0,
            pool=30.0,
        )
    except ImportError:
        http_timeout = timeout

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=http_timeout,
    )

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    last_error = None
    empty_response_count = 0
    current_max_tokens = max_tokens

    # DeepSeek-v4-pro's OpenAI tool-translation is broken (it leaks tool calls as
    # DSML markup, so the tool loop returns exploration code, not findings). Never
    # run the tool loop for it: generate text-only and format-repair the result so
    # its prose/ATTEMPT-style falsifiers become runnable blocks the runner re-runs
    # (the (b) gate — self-execution was never required). 2026-06-06. Gate-off
    # (tools is None) leaves this a no-op, byte-identical to before.
    _ds_repair = bool(tools)
    tools = None

    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            _log(f"  [deepseek:{model_id}] retry {attempt}/{max_retries} "
                 f"(max_tokens={current_max_tokens})")
        t0 = time.monotonic()
        try:
            if tools:
                # GATED tool-call path: run the whole tool loop under the same
                # hard wall-clock cap (fresh message copy per attempt). Falls
                # through to the standard retry/error handling below on failure.
                import concurrent.futures
                executor_fn = tool_executor or default_tool_executor
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as _pool:
                    _future = _pool.submit(
                        _run_openai_tool_loop,
                        client, model_id, list(messages), tools, executor_fn,
                        max_tool_iters, current_max_tokens, timeout, None,
                    )
                    try:
                        text = (_future.result(timeout=per_attempt_wall_cap) or "").strip()
                    except concurrent.futures.TimeoutError:
                        elapsed = time.monotonic() - t0
                        _log(f"  [deepseek:{model_id}] HARD WALL CAP hit "
                             f"({elapsed:.0f}s > {per_attempt_wall_cap:.0f}s cap, tools)")
                        raise TimeoutError(
                            f"DeepSeek tool attempt {attempt} exceeded hard wall "
                            f"cap of {per_attempt_wall_cap:.0f}s"
                        )
                elapsed = time.monotonic() - t0
                _log(f"  [deepseek:{model_id}] done (tools, {elapsed:.1f}s, "
                     f"{len(text)} chars)")
                if not text:
                    empty_response_count += 1
                    current_max_tokens = max(4096, current_max_tokens // 2)
                    if attempt < max_retries and backoff_base > 0:
                        time.sleep(backoff_base)
                    continue
                return text
            # Hard wall-clock cap per attempt: run the API call in a thread
            # so we can kill it if it exceeds per_attempt_wall_cap.
            # This catches the case where DeepSeek streams reasoning tokens
            # slowly (each read succeeds) but the total call takes forever.
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as _pool:
                _future = _pool.submit(
                    client.chat.completions.create,
                    model=model_id,
                    messages=messages,
                    max_tokens=current_max_tokens,
                    temperature=0.0,
                    timeout=timeout,
                )
                try:
                    response = _future.result(timeout=per_attempt_wall_cap)
                except concurrent.futures.TimeoutError:
                    elapsed = time.monotonic() - t0
                    _log(f"  [deepseek:{model_id}] HARD WALL CAP hit "
                         f"({elapsed:.0f}s > {per_attempt_wall_cap:.0f}s cap)")
                    raise TimeoutError(
                        f"DeepSeek attempt {attempt} exceeded hard wall cap "
                        f"of {per_attempt_wall_cap:.0f}s"
                    )
            elapsed = time.monotonic() - t0

            # Extract visible content
            if not response.choices:
                raise CircuitBreakerTripped(
                    "empty_response", model_id, "dispatch",
                    f"API returned no choices after {elapsed:.1f}s "
                    f"(possible upstream 500 error)"
                )
            choice = response.choices[0]
            text = (choice.message.content or "").strip()

            # Check for reasoning_content (DeepSeek Reasoner's CoT output)
            reasoning = ""
            if hasattr(choice.message, "reasoning_content"):
                reasoning = (choice.message.reasoning_content or "").strip()

            _log(f"  [deepseek:{model_id}] done ({elapsed:.1f}s, "
                 f"{len(text)} chars content, "
                 f"{len(reasoning)} chars reasoning)")

            if text:
                if _ds_repair:
                    try:
                        from decomposed_dispatch import _falsifier_format_repair
                        text = _falsifier_format_repair(
                            client, model_id, text, current_max_tokens, timeout)
                    except Exception:  # noqa: BLE001
                        pass
                return text

            # Empty content — the model exhausted its token budget on CoT.
            empty_response_count += 1
            _log(f"  [deepseek:{model_id}] empty response "
                 f"(attempt {attempt}, {elapsed:.1f}s, "
                 f"reasoning={len(reasoning)} chars)")

            if reasoning and len(reasoning) > 500:
                # Reasoning exists — the model DID process the prompt but
                # ran out of output tokens for the visible response.
                # Log the reasoning length for diagnostics.
                _log(f"  [deepseek:{model_id}] has {len(reasoning)} chars "
                     f"of reasoning_content (CoT consumed output budget)")

            # Strategy: halve max_tokens for next attempt.
            # This forces DeepSeek to allocate less to internal reasoning
            # and more to the visible response.
            # Floor at 4096 — below that the response would be too truncated.
            current_max_tokens = max(4096, current_max_tokens // 2)
            _log(f"  [deepseek:{model_id}] reducing max_tokens to "
                 f"{current_max_tokens} for next attempt")

            if attempt < max_retries and backoff_base > 0:
                time.sleep(backoff_base)
            continue

        except Exception as e:
            elapsed = time.monotonic() - t0
            last_error = e
            _log(f"  [deepseek:{model_id}] attempt {attempt} failed "
                 f"({elapsed:.1f}s): {str(e)[:120]}")
            if attempt < max_retries and backoff_base > 0:
                time.sleep(backoff_base * (2 ** (attempt - 1)))

    # All retries exhausted
    if empty_response_count > 0:
        raise CircuitBreakerTripped(
            "empty_response", model_id, "dispatch",
            f"Empty response after {max_retries} attempts "
            f"({empty_response_count} empty). DeepSeek Reasoner CoT "
            f"exhausted output budget each time."
        )

    raise RuntimeError(
        f"DeepSeek call failed after {max_retries} attempts for {model_id}. "
        f"Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Unified dispatch (UX-readiness: single entry point, config-driven)
# ---------------------------------------------------------------------------

def dispatch(
    config: ModelConfig,
    user_prompt: str,
    cdsfl_system_prompt: str,
    use_output_schema: bool = False,
    use_secondary: bool = False,
    enable_tools: bool = False,
) -> str:
    """Dispatch a prompt to any model based on its config. Returns response text.

    Args:
        use_output_schema: If True and model is Codex, use --output-schema
            to force structured CDSFL findings JSON output.
        use_secondary: If True, route via config.secondary_api +
            config.secondary_model_id (the model's one-shot fallback
            route). Raises RuntimeError if no secondary is configured.
            Used by the runner's in-round fallback path
            (2026-05-22, founder-directed: "every model has a
            secondary; no model misses a round").
        enable_tools: GATED, default OFF (2026-06-03 "tools decide"
            integration). When True, the OpenAI-compatible routes
            (openrouter, deepseek) are given the execute_python tool +
            sandboxed default_tool_executor so a reviewing model can run
            Python during analysis and attach runnable falsifiers. The
            runner sets this from cfg.falsifier_gate_enabled. claude_cli
            already exposes tools natively (--allowedTools); codex_exec /
            google branches are unchanged. When False the dispatch is
            byte-identical to the pre-integration behaviour.
    """
    if use_secondary:
        if not (config.secondary_api and config.secondary_model_id):
            raise RuntimeError(
                f"No secondary route configured for {config.label}; "
                f"cannot dispatch with use_secondary=True"
            )
        # Swap primary fields for secondary; primary extra_body is
        # route-specific (e.g. reasoning.effort for openrouter) so it
        # does not carry over.
        import dataclasses
        config = dataclasses.replace(
            config,
            api=config.secondary_api,
            model_id=config.secondary_model_id,
            extra_body=None,
        )
        _log(f"Dispatching to {config.label} ({config.model_id}) via "
             f"{config.api} [SECONDARY]...")
    else:
        _log(f"Dispatching to {config.label} ({config.model_id}) via {config.api}...")

    if config.api == "claude_cli":
        return call_claude_cli(
            model_id=config.model_id,
            system_prompt=cdsfl_system_prompt if config.system_prompt_path else None,
            user_prompt=user_prompt,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries,
            backoff_base=config.backoff_base,
        )
    elif config.api == "openrouter":
        return call_openrouter(
            model_id=config.model_id,
            system_prompt=cdsfl_system_prompt if config.system_prompt_path else None,
            user_prompt=user_prompt,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries,
            backoff_base=config.backoff_base,
            extra_body=config.extra_body,
            tools=([EXECUTE_PYTHON_TOOL] if enable_tools else None),
            tool_executor=(default_tool_executor if enable_tools else None),
        )
    elif config.api == "codex_exec":
        return call_codex(
            user_prompt=user_prompt,
            cdsfl_directives=cdsfl_system_prompt,
            timeout=config.timeout,
            max_retries=config.max_retries,
            use_output_schema=use_output_schema,
        )
    elif config.api == "google":
        return call_gemini(
            model_id=config.model_id,
            system_prompt=cdsfl_system_prompt if config.system_prompt_path else None,
            user_prompt=user_prompt,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries,
            backoff_base=config.backoff_base,
        )
    elif config.api == "deepseek":
        return call_deepseek(
            model_id=config.model_id,
            system_prompt=cdsfl_system_prompt if config.system_prompt_path else None,
            user_prompt=user_prompt,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries,
            backoff_base=config.backoff_base,
            tools=([EXECUTE_PYTHON_TOOL] if enable_tools else None),
            tool_executor=(default_tool_executor if enable_tools else None),
        )
    else:
        raise ValueError(f"Unknown API type: {config.api}")


# ---------------------------------------------------------------------------
# Output persistence (UX-readiness: all outputs saved as structured JSON)
# ---------------------------------------------------------------------------

def save_output(
    logs_dir: Path,
    phase: str,
    model_label: str,
    prompt: str,
    response: str,
    metadata: dict[str, Any] | None = None,
) -> Path:
    """Save a model's output to the experiment logs directory."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{phase}_{model_label.lower()}_{ts}.json"
    filepath = logs_dir / filename

    record = {
        "timestamp": ts,
        "phase": phase,
        "model_label": model_label,
        "prompt_length": len(prompt),
        "response_length": len(response),
        "response": response,
        "metadata": metadata or {},
    }
    filepath.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    _log(f"  Saved: {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# Preflight verification
# ---------------------------------------------------------------------------

IDENTITY_PROMPT = (
    "Identify yourself. What model are you? "
    "What is your model version? Respond in one sentence."
)

COMPLIANCE_PROMPT = (
    "Evaluate this claim under CDSFL: "
    "'The sum of interior angles in a Euclidean triangle is 180 degrees.' "
    "Use the structured output format: VERDICT, EVIDENCE, CONSTRAINT_CLASS, "
    "CONFIDENCE, STRONGEST_OBJECTION, RESPONSE."
)

IDENTITY_CHECKS: dict[str, dict[str, Any]] = {
    # Accept criteria relaxed: models rarely report exact version strings.
    # The model ID in the API call ensures the correct model. The identity
    # check verifies we're hitting the right VENDOR and not getting a
    # completely wrong model. Rejection criteria are the critical guard.
    "CC2": {
        "accept": ["claude", "anthropic"],
        "reject": ["sonnet", "claude-sonnet", "haiku"],
    },
    "Codex": {
        "accept": ["gpt-5", "gpt5", "codex", "openai"],
        "reject": ["gpt-4o", "gpt-3", "gpt-4-turbo"],
    },
    "ChatGPT": {
        "accept": ["chatgpt", "gpt-5", "gpt5", "openai"],
        "reject": ["gpt-4o", "gpt-3", "gpt-4-turbo"],
    },
    "Gemini": {
        "accept": ["gemini", "google"],
        "reject": ["flash", "bard"],
    },
    "DeepSeek": {
        "accept": ["deepseek", "deep seek"],
        "reject": [],  # empty response is the known issue, caught by circuit breaker
    },
}

STRUCTURED_FIELDS = [
    "VERDICT", "EVIDENCE", "CONSTRAINT_CLASS",
    "CONFIDENCE", "STRONGEST_OBJECTION", "RESPONSE",
]


def run_preflight(config: ExperimentConfig) -> dict[str, dict[str, Any]]:
    """Run identity and compliance checks on all models. Returns results dict."""
    results: dict[str, dict[str, Any]] = {}

    for model in config.models:
        if model.role == "collator":
            continue  # CC1 is us, skip

        _log(f"\n=== Preflight: {model.label} ===")
        result: dict[str, Any] = {"identity_pass": False, "compliance_pass": False}

        # Step 1: Identity check
        try:
            identity_response = dispatch(model, IDENTITY_PROMPT, "")
            result["identity_response"] = identity_response
            response_lower = identity_response.lower()

            checks = IDENTITY_CHECKS.get(model.label, {})
            accept_terms = checks.get("accept", [])
            reject_terms = checks.get("reject", [])

            has_accept = any(term in response_lower for term in accept_terms)
            has_reject = any(term in response_lower for term in reject_terms)

            if has_accept and not has_reject:
                result["identity_pass"] = True
                _log(f"  Identity: PASS")
            else:
                _log(f"  Identity: FAIL (accept={has_accept}, reject={has_reject})")
                _log(f"  Response: {identity_response[:200]}")
        except Exception as e:
            result["identity_error"] = str(e)
            _log(f"  Identity: ERROR — {str(e)[:200]}")

        # Step 2: Structured output compliance (only if identity passed)
        if result["identity_pass"]:
            try:
                compliance_response = dispatch(
                    model, COMPLIANCE_PROMPT, config.cdsfl_system_prompt
                )
                result["compliance_response"] = compliance_response
                response_upper = compliance_response.upper()

                found_fields = [f for f in STRUCTURED_FIELDS if f in response_upper]
                if len(found_fields) >= 4:  # require at least 4 of 6 fields
                    result["compliance_pass"] = True
                    _log(f"  Compliance: PASS ({len(found_fields)}/6 fields)")
                else:
                    _log(f"  Compliance: FAIL (only {len(found_fields)}/6 fields: {found_fields})")
            except Exception as e:
                result["compliance_error"] = str(e)
                _log(f"  Compliance: ERROR — {str(e)[:200]}")

        results[model.label] = result
        save_output(
            config.logs_dir, "preflight", model.label,
            IDENTITY_PROMPT, result.get("identity_response", "ERROR"),
            metadata={"identity_pass": result["identity_pass"],
                      "compliance_pass": result["compliance_pass"]},
        )

    return results


# ---------------------------------------------------------------------------
# Entry point (for testing infrastructure before full experiment)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Source .env
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()

    config = load_default_config()
    config.logs_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == "preflight":
        _log("Running preflight verification...")
        results = run_preflight(config)
        _log("\n=== Preflight Summary ===")
        all_pass = True
        for label, result in results.items():
            id_ok = "PASS" if result["identity_pass"] else "FAIL"
            comp_ok = "PASS" if result["compliance_pass"] else "FAIL"
            _log(f"  {label}: identity={id_ok}, compliance={comp_ok}")
            if not result["identity_pass"] or not result["compliance_pass"]:
                all_pass = False
        if all_pass:
            _log("\nAll models passed preflight. Ready to execute.")
        else:
            _log("\nPREFLIGHT FAILED. Do not proceed until all models pass.")
        sys.exit(0 if all_pass else 1)
    else:
        _log("Usage: python3 experiment_11_orchestrator.py preflight")
        _log("       (Full experiment dispatched by CC1 interactively)")
