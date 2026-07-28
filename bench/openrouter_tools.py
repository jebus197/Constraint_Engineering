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
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ── Constants ──────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent

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
        stopped_reason = "max_iterations"

    return {
        "final_text": final_text,
        "tool_calls": tool_call_log,
        "iterations": iterations,
        "stopped_reason": stopped_reason,
    }
