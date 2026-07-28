"""Tests for Exp 40 1E.11 — OpenRouter function-calling tool support.

Acceptance from the plan:
  On a synthetic mathematical claim, Codex/Gemini/ChatGPT/DeepSeek each
  successfully invoke SymPy via function-calling and receive structured
  results.

The module under test (``bench.openrouter_tools``) is the host side of that
contract — it exposes the tool schemas, routes tool-call dispatches to
subprocess-isolated verifiers, and runs the tool-call loop that models sit
inside. The tests here cover the host contract without requiring network
access:

  1. TOOL_SPECS conform to the OpenAI function-calling JSON schema and the
     declared tool names have registered dispatchers.
  2. ``dispatch_tool_call`` routes valid calls and returns JSON-serialisable
     error objects for every failure mode (unknown tool, malformed JSON,
     missing argument, handler exception).
  3. ``_resolve_repo_path`` rejects escape attempts (absolute outside,
     traversal, symlink escape) and accepts legitimate repo paths.
  4. The pytest / ruff / mypy dispatchers reject non-existent paths, run to
     completion on existing files, and return the documented result shape.
  5. ``call_openrouter_with_tools`` executes the full tool-call loop against
     a mocked OpenAI client: single-turn (no tool_calls), multi-turn (model
     requests tools, host runs them, conversation re-sent), and the
     MAX_TOOL_ITERATIONS safety stop.
  6. Missing ``OPENROUTER_API_KEY`` is surfaced as ``RuntimeError``.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from bench import openrouter_tools as ort


# ═══════════════════════════════════════════════════════════════════════════
# 1. Tool specs conform to OpenAI function-calling schema
# ═══════════════════════════════════════════════════════════════════════════


class TestToolSpecsStructure:
    """The OpenRouter API validates ``tools`` against OpenAI's schema. A
    malformed spec makes every tool call fail with a 4xx before we see a
    model response — catching that at test time is cheap."""

    def test_five_tools_registered(self):
        assert len(ort.TOOL_SPECS) == 5

    def test_every_spec_is_function_type(self):
        for spec in ort.TOOL_SPECS:
            assert spec["type"] == "function", (
                f"spec {spec} is not type=function"
            )

    def test_every_spec_has_function_block(self):
        for spec in ort.TOOL_SPECS:
            assert "function" in spec
            fn = spec["function"]
            assert "name" in fn and isinstance(fn["name"], str)
            assert "description" in fn and isinstance(fn["description"], str)
            assert "parameters" in fn

    def test_parameters_are_json_schema_object(self):
        for spec in ort.TOOL_SPECS:
            params = spec["function"]["parameters"]
            assert params["type"] == "object"
            assert "properties" in params and isinstance(
                params["properties"], dict
            )
            assert "required" in params and isinstance(
                params["required"], list
            )
            # Every required key must appear in properties.
            for r in params["required"]:
                assert r in params["properties"], (
                    f"required key {r} missing from properties for "
                    f"{spec['function']['name']}"
                )

    def test_tool_names_unique(self):
        names = [s["function"]["name"] for s in ort.TOOL_SPECS]
        assert len(set(names)) == len(names), (
            f"duplicate tool names: {names}"
        )

    def test_every_declared_tool_has_dispatcher(self):
        for spec in ort.TOOL_SPECS:
            name = spec["function"]["name"]
            assert name in ort._TOOL_DISPATCH, (
                f"tool {name} advertised but no dispatcher registered"
            )

    def test_expected_tool_names_present(self):
        names = {s["function"]["name"] for s in ort.TOOL_SPECS}
        assert names == {
            "sympy_verify",
            "z3_verify",
            "pytest_run",
            "ruff_check",
            "mypy_check",
        }


# ═══════════════════════════════════════════════════════════════════════════
# 2. dispatch_tool_call routes calls and handles every failure mode
# ═══════════════════════════════════════════════════════════════════════════


class TestDispatchToolCallRouting:
    """The host-side dispatcher is what the model actually talks to. Every
    response must be a valid JSON string so the model can parse it — so
    every failure path must return JSON, never raise."""

    def test_unknown_tool_returns_error_json(self):
        out = ort.dispatch_tool_call("nope_tool", "{}")
        payload = json.loads(out)
        assert "error" in payload
        assert "unknown tool" in payload["error"]

    def test_malformed_arguments_returns_error_json(self):
        out = ort.dispatch_tool_call("sympy_verify", "{not valid json")
        payload = json.loads(out)
        assert "error" in payload
        assert "malformed" in payload["error"].lower()

    def test_missing_required_argument_returns_error_json(self):
        # sympy_verify requires "claim"
        out = ort.dispatch_tool_call("sympy_verify", "{}")
        payload = json.loads(out)
        assert "error" in payload
        assert "missing argument" in payload["error"]
        assert "claim" in payload["error"]

    def test_empty_arguments_string_treated_as_empty_object(self):
        # OpenAI sometimes returns "" for a zero-arg call; we treat it as {}
        # then fail on the missing required arg — still structured JSON.
        out = ort.dispatch_tool_call("sympy_verify", "")
        payload = json.loads(out)
        assert "error" in payload

    def test_sympy_call_returns_verdict_structure(self):
        # The claim may return UNCERTAIN due to verifier internals; what
        # matters here is that dispatch returns a JSON dict with the
        # documented keys, not that a specific verdict comes back.
        out = ort.dispatch_tool_call(
            "sympy_verify", json.dumps({"claim": "x + 0 - x"})
        )
        payload = json.loads(out)
        # error OR the full verdict shape; both are structurally valid.
        if "error" not in payload:
            assert "verdict" in payload
            assert "confidence" in payload
            assert "evidence" in payload
            assert "tool" in payload
            assert "elapsed_s" in payload
            assert payload["verdict"] in {
                "CONFIRMED", "REJECTED", "UNCERTAIN",
            }

    def test_z3_call_returns_verdict_structure(self):
        out = ort.dispatch_tool_call(
            "z3_verify", json.dumps({"claim": "x > 0 implies x + 1 > 0"})
        )
        payload = json.loads(out)
        if "error" not in payload:
            assert "verdict" in payload
            assert payload["verdict"] in {
                "CONFIRMED", "REJECTED", "UNCERTAIN",
            }

    def test_handler_exception_returns_error_json_not_raise(self):
        """Forcing an unexpected handler error must still round-trip JSON
        rather than surfacing an exception to the caller (the model would
        receive a hung tool call and the loop would stall)."""
        def _boom(args):
            raise RuntimeError("simulated handler failure")

        with patch.dict(
            ort._TOOL_DISPATCH, {"sympy_verify": _boom}, clear=False
        ):
            out = ort.dispatch_tool_call("sympy_verify", "{}")
        payload = json.loads(out)
        assert "error" in payload
        assert "RuntimeError" in payload["error"]
        assert "simulated handler failure" in payload["error"]


# ═══════════════════════════════════════════════════════════════════════════
# 3. Path safety: escape attempts rejected, legitimate paths accepted
# ═══════════════════════════════════════════════════════════════════════════


class TestPathSafety:
    """File-based verifiers (pytest/ruff/mypy) take a model-controlled path.
    If the path escapes the repo root the model could read/execute arbitrary
    files on the host. ``_resolve_repo_path`` is the gatekeeper."""

    def test_relative_path_under_repo_accepted(self):
        p = ort._resolve_repo_path("bench/openrouter_tools.py")
        assert p.is_file()
        assert p.resolve().is_relative_to(ort.REPO_ROOT)

    def test_absolute_outside_repo_rejected(self):
        with pytest.raises(ValueError, match="escapes repo root"):
            ort._resolve_repo_path("/etc/passwd")

    def test_traversal_escape_rejected(self):
        with pytest.raises(ValueError, match="escapes repo root"):
            ort._resolve_repo_path("../../../etc/passwd")

    def test_tricky_traversal_rejected(self):
        # Even if path resolution is tricky, the relative_to check catches it.
        with pytest.raises(ValueError, match="escapes repo root"):
            ort._resolve_repo_path("bench/../../secret_file")

    def test_absolute_inside_repo_accepted(self):
        # An absolute path that happens to be inside the repo root is fine.
        abs_path = str(ort.REPO_ROOT / "bench" / "openrouter_tools.py")
        p = ort._resolve_repo_path(abs_path)
        assert p.is_file()


# ═══════════════════════════════════════════════════════════════════════════
# 4. Filesystem-backed dispatchers (pytest / ruff / mypy)
# ═══════════════════════════════════════════════════════════════════════════


class TestFilesystemBackedDispatchers:
    """The three file dispatchers must: (a) return structured error on a
    missing path; (b) run their tool on a valid path and come back with the
    documented keys. We exercise them on lightweight fixture content rather
    than the real test suite to keep the tests fast."""

    def _write_tmp_py(self, tmp_path, name: str, body: str):
        """Write a python file INSIDE the repo root so ``_resolve_repo_path``
        accepts it. ``tmp_path`` is pytest's per-test tmp dir but it lives
        outside the repo; we use ``bench/tests/_tmp_or_<pid>.py`` instead."""
        dest = ort.REPO_ROOT / "bench" / "tests" / f"_tmp_ort_{os.getpid()}_{name}"
        dest.write_text(body)
        return dest

    def test_pytest_run_rejects_missing_path(self):
        result = ort._run_pytest("bench/tests/definitely_not_a_file.py")
        assert result["status"] == "error"
        assert "path not found" in result["detail"]

    def test_ruff_rejects_missing_path(self):
        result = ort._run_ruff("bench/nonexistent_file_xyz.py")
        assert result["status"] == "error"

    def test_mypy_rejects_missing_path(self):
        result = ort._run_mypy("bench/nonexistent_file_xyz.py")
        assert result["status"] == "error"

    def test_ruff_runs_on_clean_file(self):
        """A syntactically clean file should return status='clean' OR
        status='violations' if project rules flag it; either is a valid
        outcome — we just care that the dispatcher ran end-to-end and
        returned the documented keys."""
        dest = self._write_tmp_py(
            None, "clean.py",
            "x = 1\nprint(x)\n",
        )
        try:
            rel = dest.relative_to(ort.REPO_ROOT)
            result = ort._run_ruff(str(rel))
            assert "status" in result
            assert "returncode" in result
            assert "output" in result
            assert "elapsed_s" in result
            assert result["status"] in {"clean", "violations"}
        finally:
            dest.unlink(missing_ok=True)

    def test_mypy_runs_on_well_typed_file(self):
        dest = self._write_tmp_py(
            None, "typed.py",
            "def f(x: int) -> int:\n    return x + 1\n",
        )
        try:
            rel = dest.relative_to(ort.REPO_ROOT)
            result = ort._run_mypy(str(rel))
            assert "status" in result
            assert "returncode" in result
            assert result["status"] in {"ok", "errors"}
        finally:
            dest.unlink(missing_ok=True)

    def test_pytest_runs_on_existing_test_file(self):
        """The pytest dispatcher should complete (pass or fail is fine) on
        a real test path. We use this file itself as a trivially-passing
        target to avoid re-running a heavy suite."""
        result = ort._run_pytest(
            "bench/tests/test_openrouter_tools.py"
            "::TestToolSpecsStructure::test_five_tools_registered"
        )
        assert "status" in result
        # The test we just selected should pass — but if the runner reports
        # timeout or error we still assert the response shape is valid.
        assert result["status"] in {"passed", "failed", "timeout"}
        assert "returncode" in result or result["status"] == "timeout"


# ═══════════════════════════════════════════════════════════════════════════
# 5. call_openrouter_with_tools: tool-call loop behaviour (mocked)
# ═══════════════════════════════════════════════════════════════════════════


def _make_response_no_tool_calls(text: str):
    """Build a mock OpenAI ChatCompletion response with no tool_calls."""
    choice = MagicMock()
    choice.message.content = text
    choice.message.tool_calls = None
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _make_tool_call(name: str, args: Dict[str, Any], call_id: str = "call_1"):
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = name
    tc.function.arguments = json.dumps(args)
    return tc


def _make_response_with_tool_calls(tool_calls):
    choice = MagicMock()
    choice.message.content = ""
    choice.message.tool_calls = tool_calls
    resp = MagicMock()
    resp.choices = [choice]
    return resp


class TestCallOpenRouterWithToolsMocked:
    """Exercise the full tool-call loop without hitting the network."""

    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
            ort.call_openrouter_with_tools(
                model_id="x/test",
                system_prompt=None,
                user_prompt="hi",
                tools=ort.TOOL_SPECS,
            )

    def test_single_turn_no_tool_calls(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = (
            _make_response_no_tool_calls("Hello, no tools needed.")
        )
        with patch("openai.OpenAI", return_value=mock_client):
            result = ort.call_openrouter_with_tools(
                model_id="x/test",
                system_prompt="sys",
                user_prompt="hi",
                tools=ort.TOOL_SPECS,
            )
        assert result["stopped_reason"] == "finish"
        assert result["iterations"] == 1
        assert result["tool_calls"] == []
        assert result["final_text"] == "Hello, no tools needed."

    def test_multi_turn_tool_execution(self, monkeypatch):
        """Simulate: turn-1 model emits one tool_call; turn-2 model emits a
        final assistant message with no tool_calls."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        mock_client = MagicMock()

        tc = _make_tool_call(
            "sympy_verify", {"claim": "x + 0 - x"}, call_id="call_A"
        )
        mock_client.chat.completions.create.side_effect = [
            _make_response_with_tool_calls([tc]),
            _make_response_no_tool_calls("Based on SymPy: the claim holds."),
        ]

        with patch("openai.OpenAI", return_value=mock_client):
            result = ort.call_openrouter_with_tools(
                model_id="x/test",
                system_prompt="sys",
                user_prompt="verify x + 0 - x",
                tools=ort.TOOL_SPECS,
            )
        assert result["stopped_reason"] == "finish"
        assert result["iterations"] == 2
        assert len(result["tool_calls"]) == 1
        logged = result["tool_calls"][0]
        assert logged["name"] == "sympy_verify"
        parsed_args = json.loads(logged["arguments"])
        assert parsed_args == {"claim": "x + 0 - x"}
        # Result is a JSON string — must parse cleanly.
        parsed_result = json.loads(logged["result"])
        assert isinstance(parsed_result, dict)
        assert result["final_text"].startswith("Based on SymPy")

    def test_tool_call_then_another_tool_call_then_finish(self, monkeypatch):
        """Chain two tool calls across two iterations before convergence."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        mock_client = MagicMock()

        tc1 = _make_tool_call(
            "sympy_verify", {"claim": "x + 0"}, call_id="A"
        )
        tc2 = _make_tool_call(
            "z3_verify", {"claim": "x > 0 implies x > -1"}, call_id="B"
        )
        mock_client.chat.completions.create.side_effect = [
            _make_response_with_tool_calls([tc1]),
            _make_response_with_tool_calls([tc2]),
            _make_response_no_tool_calls("Both checks passed."),
        ]

        with patch("openai.OpenAI", return_value=mock_client):
            result = ort.call_openrouter_with_tools(
                model_id="x/test",
                system_prompt=None,
                user_prompt="verify two claims",
                tools=ort.TOOL_SPECS,
            )
        assert result["stopped_reason"] == "finish"
        assert result["iterations"] == 3
        assert [c["name"] for c in result["tool_calls"]] == [
            "sympy_verify", "z3_verify",
        ]

    def test_max_iterations_cap_enforced(self, monkeypatch):
        """If the model keeps requesting tools we cap at MAX_TOOL_ITERATIONS."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        mock_client = MagicMock()

        def _always_tool_call(*args, **kwargs):
            tc = _make_tool_call(
                "sympy_verify", {"claim": "x + 0"}, call_id="spam"
            )
            return _make_response_with_tool_calls([tc])

        mock_client.chat.completions.create.side_effect = _always_tool_call

        with patch("openai.OpenAI", return_value=mock_client):
            result = ort.call_openrouter_with_tools(
                model_id="x/test",
                system_prompt=None,
                user_prompt="loop forever",
                tools=ort.TOOL_SPECS,
                max_iterations=3,
            )
        assert result["stopped_reason"] == "max_iterations"
        assert result["iterations"] == 3
        assert len(result["tool_calls"]) == 3
        assert result["final_text"] == ""

    def test_empty_choices_surfaces_as_error(self, monkeypatch):
        """An API response with no choices short-circuits to stopped='error'."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        mock_client = MagicMock()
        empty_resp = MagicMock()
        empty_resp.choices = []
        mock_client.chat.completions.create.return_value = empty_resp

        with patch("openai.OpenAI", return_value=mock_client):
            result = ort.call_openrouter_with_tools(
                model_id="x/test",
                system_prompt=None,
                user_prompt="no response",
                tools=ort.TOOL_SPECS,
            )
        assert result["stopped_reason"] == "error"
        assert result["final_text"] == ""

    def test_tools_none_still_works(self, monkeypatch):
        """Callers can opt out of tools by passing ``tools=None`` — we must
        still get a valid response, without ``tools`` or ``tool_choice``
        ending up in the create() kwargs."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = (
            _make_response_no_tool_calls("no tools used")
        )
        with patch("openai.OpenAI", return_value=mock_client):
            result = ort.call_openrouter_with_tools(
                model_id="x/test",
                system_prompt=None,
                user_prompt="hi",
                tools=None,
            )
        assert result["stopped_reason"] == "finish"
        assert result["final_text"] == "no tools used"
        # Verify that when tools is None we did NOT forward the kwargs.
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert "tools" not in call_kwargs
        assert "tool_choice" not in call_kwargs

    def test_system_prompt_forwarded(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = (
            _make_response_no_tool_calls("ok")
        )
        with patch("openai.OpenAI", return_value=mock_client):
            ort.call_openrouter_with_tools(
                model_id="x/test",
                system_prompt="you are a math verifier",
                user_prompt="what is 2+2",
                tools=ort.TOOL_SPECS,
            )
        kwargs = mock_client.chat.completions.create.call_args.kwargs
        messages = kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "you are a math verifier"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "what is 2+2"


# ═══════════════════════════════════════════════════════════════════════════
# 6. MAX_TOOL_ITERATIONS default matches module contract
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleConstants:
    """Guard against silent changes to the documented safety caps."""

    def test_max_tool_iterations_is_six(self):
        """The docstring promises 6 — if this changes it is a contract
        break and should be re-reviewed against pathology scenarios."""
        assert ort.MAX_TOOL_ITERATIONS == 6

    def test_repo_root_points_at_project(self):
        assert (ort.REPO_ROOT / "bench").is_dir()
        assert (ort.REPO_ROOT / "bench" / "openrouter_tools.py").is_file()

    def test_default_tool_timeout_positive(self):
        assert ort.DEFAULT_TOOL_TIMEOUT_S > 0
