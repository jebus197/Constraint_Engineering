"""OpenRouter function-calling tool support (Exp 40 Item 1E.11).

CC2 has native Bash via the claude CLI and can shell out to SymPy, z3, pytest,
ruff, and mypy directly. The other four panel models — Codex, Gemini, ChatGPT,
DeepSeek — reach OpenRouter (DeepSeek via its own API path) and have no tool
execution unless the host wires structured function-calling.

This module provides:
  * ``TOOL_SPECS``: OpenAI function-calling JSON-schema definitions for each
    verifier. Each spec advertises a single callable to the model.
  * ``dispatch_tool_call``: local dispatcher that routes ``function.name`` and
    ``function.arguments`` to the matching subprocess-isolated verifier.
  * ``call_openrouter_with_tools``: thin wrapper around
    ``experiment_11_orchestrator.call_openrouter`` that adds the tool-call
    loop: the model emits ``tool_calls``, the host executes each, the result
    is appended as a ``role="tool"`` message, and the conversation is
    re-sent until the model produces a final assistant message with no more
    ``tool_calls`` or a max-iteration safety stop is hit.

Safety:
  * SymPy / z3 claims run through the same AST-blocklist subprocess runner as
    ``bench.immune_agents._run_tool_subprocess``.
  * File-based verifiers (pytest / ruff / mypy) accept only paths under the
    project root and reject anything else — no arbitrary path escalation.
  * A hard iteration cap (``MAX_TOOL_ITERATIONS``) prevents pathological
    loops where the model keeps requesting tools without converging.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ── Constants ──────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent

# The sympy/z3 verifiers are reached as ``bench.immune_agents``, which requires
# the REPO ROOT on sys.path, not this file's own directory. Running a caller as
# a script (``python3 bench/confer_*.py``) sets sys.path[0] to ``bench/``, so
# ``bench`` is not an importable package and every sympy_verify / z3_verify call
# returns {"error": "ModuleNotFoundError: No module named 'bench.immune_agents'"}
# instead of a verdict. The model still sees a tool "result" and reasons on,
# so the failure is silent: the panel looks tool-enabled and is not.
# Measured 2026-09-05: 19 such calls in panel_maths_tools_20260905T034234Z.
# test_openrouter_tools.py never caught it because pytest puts rootdir on the
# path, so the test and the script disagree about what is importable.
# Appended, not inserted at 0, so nothing here can shadow an installed package.
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Hard cap on the tool-call loop. At 6 iterations a model can: call a tool,
# read the result, call another, etc. through a short chain. Beyond that we
# suspect a pathology (tool spamming) and force the loop to terminate.
MAX_TOOL_ITERATIONS = 6

# Per-call timeout passed to subprocess.run for each tool invocation.
DEFAULT_TOOL_TIMEOUT_S = 15


# ── Tool specs (OpenAI function-calling JSON schema) ──────────────────────

SYMPY_TOOL_SPEC: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "sympy_verify",
        "description": (
            "Verify a symbolic or algebraic equality/inequality claim "
            "using SymPy. Examples: 'x + 0 = x', '2 + 2 = 4', "
            "'sin(x)^2 + cos(x)^2 = 1'. Returns CONFIRMED, REJECTED, or "
            "UNCERTAIN along with structured evidence."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The mathematical claim, as a plain-text "
                                   "equation or identity.",
                },
            },
            "required": ["claim"],
        },
    },
}


Z3_TOOL_SPEC: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "z3_verify",
        "description": (
            "Check a logical or constraint claim using z3 SMT. Use for "
            "bound-checks, implication, or satisfiability questions. "
            "Returns CONFIRMED (claim holds), REJECTED (claim violates "
            "constraints), or UNCERTAIN."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The constraint claim, e.g. "
                                   "'for all x, y: x > 0 and y > 0 implies "
                                   "x + y > 0'.",
                },
            },
            "required": ["claim"],
        },
    },
}


PYTEST_TOOL_SPEC: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "pytest_run",
        "description": (
            "Run pytest on a specific test file or test node within the "
            "repository. The path must be under the project root. Returns "
            "pytest's short summary output."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "test_path": {
                    "type": "string",
                    "description": "Path to a test file or node "
                                   "(e.g. 'bench/tests/test_immune_agents.py' "
                                   "or 'bench/tests/test_x.py::TestClass').",
                },
            },
            "required": ["test_path"],
        },
    },
}


RUFF_TOOL_SPEC: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "ruff_check",
        "description": (
            "Run ruff lint check on a Python file. Returns any style / bug "
            "violations ruff reports."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to a Python file under the project "
                                   "root.",
                },
            },
            "required": ["file_path"],
        },
    },
}


MYPY_TOOL_SPEC: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "mypy_check",
        "description": (
            "Run mypy static type-check on a Python file. Returns type "
            "errors or 'Success: no issues found'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to a Python file under the project "
                                   "root.",
                },
            },
            "required": ["file_path"],
        },
    },
}


TOOL_SPECS: List[Dict[str, Any]] = [
    SYMPY_TOOL_SPEC,
    Z3_TOOL_SPEC,
    PYTEST_TOOL_SPEC,
    RUFF_TOOL_SPEC,
    MYPY_TOOL_SPEC,
]


# ── Path safety ────────────────────────────────────────────────────────────


def _resolve_repo_path(path_str: str) -> Path:
    """Resolve a path and enforce it lives under ``REPO_ROOT``.

    Raises ``ValueError`` if the path escapes the repo or does not exist.
    """
    candidate = (REPO_ROOT / path_str).resolve() if not os.path.isabs(path_str) \
        else Path(path_str).resolve()
    try:
        candidate.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError(
            f"path {path_str!r} escapes repo root {REPO_ROOT}"
        ) from exc
    return candidate


# ── Local tool dispatchers ────────────────────────────────────────────────


def _run_sympy_verify(claim: str) -> Dict[str, Any]:
    """Subprocess-isolated SymPy verifier. Mirrors the immune-agent path."""
    # Defer to the immune-agent verifier so that the AST blocklist and
    # evidence format stay in one place. The verdict dict is what we ship to
    # the model through the tool-call return.
    from bench.immune_agents import _verify_sympy

    t0 = time.monotonic()
    v = _verify_sympy(claim)
    return {
        "verdict": v.verdict,
        "confidence": round(v.confidence, 3),
        "evidence": v.evidence,
        "tool": v.tool_used,
        "elapsed_s": round(time.monotonic() - t0, 3),
    }


def _run_z3_verify(claim: str) -> Dict[str, Any]:
    """Subprocess-isolated z3 verifier."""
    from bench.immune_agents import _verify_z3

    t0 = time.monotonic()
    v = _verify_z3(claim)
    return {
        "verdict": v.verdict,
        "confidence": round(v.confidence, 3),
        "evidence": v.evidence,
        "tool": v.tool_used,
        "elapsed_s": round(time.monotonic() - t0, 3),
    }


def _run_pytest(test_path: str) -> Dict[str, Any]:
    """Run pytest on a specific file/node under the repo root."""
    path = _resolve_repo_path(test_path.split("::", 1)[0])
    if not path.exists():
        return {"status": "error", "detail": f"path not found: {test_path}"}
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", test_path, "-q", "--no-header"],
            capture_output=True, text=True, timeout=DEFAULT_TOOL_TIMEOUT_S * 10,
            cwd=str(REPO_ROOT),
        )
        elapsed = time.monotonic() - t0
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout_tail": result.stdout.strip()[-1200:],
            "stderr_tail": result.stderr.strip()[-600:],
            "elapsed_s": round(elapsed, 2),
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "elapsed_s": DEFAULT_TOOL_TIMEOUT_S * 10}


def _run_ruff(file_path: str) -> Dict[str, Any]:
    """Run ruff check on a single file."""
    path = _resolve_repo_path(file_path)
    if not path.exists():
        return {"status": "error", "detail": f"path not found: {file_path}"}
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            ["python3", "-m", "ruff", "check", str(path), "--no-fix"],
            capture_output=True, text=True, timeout=DEFAULT_TOOL_TIMEOUT_S,
            cwd=str(REPO_ROOT),
        )
        elapsed = time.monotonic() - t0
        return {
            "status": "clean" if result.returncode == 0 else "violations",
            "returncode": result.returncode,
            "output": result.stdout.strip()[:1500],
            "elapsed_s": round(elapsed, 2),
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "elapsed_s": DEFAULT_TOOL_TIMEOUT_S}


def _run_mypy(file_path: str) -> Dict[str, Any]:
    """Run mypy on a single file."""
    path = _resolve_repo_path(file_path)
    if not path.exists():
        return {"status": "error", "detail": f"path not found: {file_path}"}
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            ["python3", "-m", "mypy", str(path), "--no-error-summary",
             "--ignore-missing-imports"],
            capture_output=True, text=True, timeout=DEFAULT_TOOL_TIMEOUT_S * 2,
            cwd=str(REPO_ROOT),
        )
        elapsed = time.monotonic() - t0
        return {
            "status": "ok" if result.returncode == 0 else "errors",
            "returncode": result.returncode,
            "output": result.stdout.strip()[:1500],
            "elapsed_s": round(elapsed, 2),
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "elapsed_s": DEFAULT_TOOL_TIMEOUT_S * 2}


_TOOL_DISPATCH: Dict[str, Callable[..., Dict[str, Any]]] = {
    "sympy_verify": lambda args: _run_sympy_verify(args["claim"]),
    "z3_verify": lambda args: _run_z3_verify(args["claim"]),
    "pytest_run": lambda args: _run_pytest(args["test_path"]),
    "ruff_check": lambda args: _run_ruff(args["file_path"]),
    "mypy_check": lambda args: _run_mypy(args["file_path"]),
}


def _access_tool(name: str):
    """Route the ACCESS tools -- read_file, grep, list_dir, run_python,
    run_pytest -- to the executor that implements them.

    ADDED 2026-09-20, WITH ITS SPECS, because a spec without a handler is worse
    than no spec: the model calls the tool, gets `unknown tool: read_file`, and
    spends an iteration learning that. The panel's seats previously had 5 tools,
    none of which reads a file or runs a script, so a brief asking them to read
    the artefact under review was asking for something impossible -- and the
    seats burned their iteration budget discovering it.
    """
    def _run(args):
        import build_experiment_tools as _bt
        return {"result": _bt.execute(name, args)}
    return _run


for _access in ("read_file", "grep", "list_dir", "run_python", "run_pytest"):
    _TOOL_DISPATCH[_access] = _access_tool(_access)


def dispatch_tool_call(name: str, arguments_json: str) -> str:
    """Route a tool call to its dispatcher and return a JSON-serialisable
    string result that can be handed back to the model.

    ``arguments_json`` is what the OpenAI tool-call API returns: a JSON-
    encoded string of the function's arguments.
    """
    handler = _TOOL_DISPATCH.get(name)
    if handler is None:
        return json.dumps({"error": f"unknown tool: {name}"})
    try:
        args = json.loads(arguments_json or "{}")
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"malformed arguments: {exc}"})
    try:
        result = handler(args)
    except KeyError as exc:
        return json.dumps({"error": f"missing argument: {exc.args[0]}"})
    except ValueError as exc:
        return json.dumps({"error": f"{exc}"})
    except Exception as exc:  # noqa: BLE001 — return error to model, don't crash
        return json.dumps({
            "error": f"{type(exc).__name__}: {str(exc)[:200]}",
        })
    return json.dumps(result)


# ── Tool-call loop around call_openrouter ─────────────────────────────────


def call_openrouter_with_tools(
    model_id: str,
    system_prompt: Optional[str],
    user_prompt: str,
    tools: Optional[List[Dict[str, Any]]] = None,
    max_tokens: int = 8192,
    timeout: int = 180,
    max_iterations: int = MAX_TOOL_ITERATIONS,
) -> Dict[str, Any]:
    """Call an OpenRouter model with function-calling tools.

    Returns a dict with:
      * ``final_text``  – the final assistant message content
      * ``tool_calls``  – list of (name, arguments, result) tuples recorded
      * ``iterations``  – how many API round-trips it took
      * ``stopped_reason`` – 'finish', 'max_iterations', or 'error'

    When ``tools`` is None, falls back to the tool-free code path so callers
    can opt in incrementally.
    """
    import openai

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=timeout,
    )

    messages: List[Dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    tool_call_log: List[Dict[str, Any]] = []
    stopped_reason = "finish"
    iterations = 0
    final_text = ""

    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        create_kwargs: Dict[str, Any] = dict(
            model=model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.0,
        )
        if tools:
            create_kwargs["tools"] = tools
            create_kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**create_kwargs)
        if not response.choices:
            stopped_reason = "error"
            break

        choice = response.choices[0]
        msg = choice.message
        tool_calls = getattr(msg, "tool_calls", None) or []

        if not tool_calls:
            final_text = (msg.content or "").strip()
            stopped_reason = "finish"
            if not final_text:
                # EMPTY VISIBLE CONTENT IS NOT AN ANSWER, AND THIS LOOP USED TO
                # TREAT IT AS ONE (fixed 2026-09-20).
                #
                # A reasoning model can burn its whole output budget on
                # chain-of-thought and return finish_reason 'stop' with no visible
                # content. Recording that as `finish` reports a seat as having
                # answered when it said nothing.
                #
                # THE GUARD ALREADY EXISTED -- IN THE OTHER LOOP. The sibling
                # `_run_openai_tool_loop` in experiment_11_orchestrator.py has
                # carried a tool-less retry at a raised budget for this exact case
                # since 2026-06-06, written against gemini-3.1-pro-preview. This
                # loop, which is the one the paid OpenRouter seats actually run,
                # never received it. So in panel round 3 the very model the retry
                # was written for hit the very failure it prevents: ge made 1
                # tool call, read 24,868 characters, and returned 0.
                #
                # Two loops doing the same job, each internally consistent, and
                # the divergence invisible to any check that reads only one of
                # them. Dropping `tools` forces a content answer rather than
                # another tool call; the accumulated tool results stay in
                # `messages`, so the model answers with everything it gathered.
                retry_kwargs = dict(create_kwargs)
                retry_kwargs["max_tokens"] = max(max_tokens, 65536)
                retry_kwargs.pop("tools", None)
                retry_kwargs.pop("tool_choice", None)
                messages.append({
                    "role": "user",
                    "content": (
                        "Your last reply returned no visible content. Write your "
                        "COMPLETE findings now as your final answer, using the "
                        "tool results you already have. Do not call any further "
                        "tools. Where a check did not complete, say so and mark "
                        "that claim UNVERIFIED rather than asserting it."
                    ),
                })
                retry_kwargs["messages"] = messages
                for _retry in range(2):
                    try:
                        retry_response = client.chat.completions.create(**retry_kwargs)
                    except Exception:  # noqa: BLE001
                        retry_response = None
                    if retry_response and retry_response.choices:
                        cand = (retry_response.choices[0].message.content or "").strip()
                        if cand:
                            final_text = cand
                            stopped_reason = "finish_after_empty_retry"
                            break
                    time.sleep(2.0)
                else:
                    if not final_text:
                        # Say so rather than reporting a silent seat as finished.
                        stopped_reason = "empty_content_after_retry"
            break

        # Model wants to invoke tools. Append the assistant-with-tool-calls
        # message verbatim, then run each tool and append its result.
        assistant_msg: Dict[str, Any] = {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        }
        messages.append(assistant_msg)

        for tc in tool_calls:
            name = tc.function.name
            args_json = tc.function.arguments
            result_json = dispatch_tool_call(name, args_json)
            tool_call_log.append({
                "name": name,
                "arguments": args_json,
                "result": result_json,
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": name,
                "content": result_json,
            })
    else:
        # THE CAP MUST STOP THE TOOLS, NOT DISCARD THE ANSWER.
        #
        # Measured 2026-09-05: with the sys.path defect above fixed, the tools
        # actually worked, and cx immediately went from 10 calls to 31 -- straight
        # through this cap. It returned final_text="" and ok=False, so a full paid
        # seat produced nothing at all. Before the fix the same seat "succeeded",
        # because every tool errored instantly and it gave up and wrote prose.
        # Repairing the tools is what made the cap bite; the two defects were
        # masking each other.
        #
        # The cap exists to stop pathological tool spam, and exhausting it does
        # that -- no further tool call is permitted below. Throwing away the
        # reasoning as well is a separate, unintended loss. So: one final
        # tool-free round-trip to harvest the verdict from the work already done.
        # Bounded (exactly 1 extra call, only on cap exhaustion) and it cannot
        # loop, because `tools` is omitted so no tool_calls can come back.
        stopped_reason = "max_iterations"
        messages.append({
            "role": "user",
            "content": (
                "You have reached this review's tool-call limit, so no further "
                "tool calls are available. Write your final answer NOW using the "
                "tool results you already have. Where a check did not complete, "
                "say so explicitly and mark that claim UNVERIFIED rather than "
                "asserting it."
            ),
        })
        try:
            final_response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.0,
            )
            if final_response.choices:
                final_text = (final_response.choices[0].message.content or "").strip()
                if final_text:
                    stopped_reason = "max_iterations_harvested"
        except Exception as exc:  # harvest is best-effort; never mask the cap
            stopped_reason = f"max_iterations_harvest_failed: {type(exc).__name__}"

    return {
        "final_text": final_text,
        "tool_calls": tool_call_log,
        "iterations": iterations,
        "stopped_reason": stopped_reason,
    }
