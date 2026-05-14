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
import subprocess
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
    """Configuration for a single model participant."""
    label: str
    model_id: str
    api: str  # "openrouter", "codex_exec", "deepseek"
    role: Role
    system_prompt_path: str | None  # None for collator
    max_tokens: int = 32768
    timeout: int = 300
    max_retries: int = 3
    backoff_base: float = 3.0
    extra_body: dict | None = None  # Model-specific API params (e.g. reasoning.effort)


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
        ),
        ModelConfig(
            label="DeepSeek",
            model_id="deepseek/deepseek-v4-pro",
            api="openrouter",
            role="participant",
            system_prompt_path=str(cdsfl_path),
            max_tokens=16384,
            timeout=300,  # R1-0528 via OpenRouter: 25s smoke test (vs 121s direct)
            max_retries=3,
            # Routing change 13 April 2026: switched from direct API
            # (deepseek-reasoner) to OpenRouter (deepseek-r1-0528).
            # Smoke test showed: 2x+ output, 5x faster, R_k adoption intact.
            # Direct API reserved for specialist deep-verification role.
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


def call_openrouter(
    model_id: str,
    system_prompt: str | None,
    user_prompt: str,
    max_tokens: int = 32768,
    timeout: int = 300,
    max_retries: int = 3,
    backoff_base: float = 3.0,
    extra_body: dict | None = None,
) -> str:
    """Call a model via OpenRouter (bare-metal, CDSFL system prompt only)."""
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

    Uses --bare for minimal overhead (no hooks, LSP, auto-memory, CLAUDE.md).
    Uses --system-prompt for native CDSFL delivery (unlike Codex which embeds
    in prompt body). Uses stdin piping for large prompts.
    """
    cli = CLAUDE_CLI
    if not cli:
        raise FileNotFoundError(
            "Claude CLI not found. Expected 'claude' in PATH or in "
            "~/Library/Application Support/Claude/claude-code/*/claude.app/Contents/MacOS/claude"
        )
    cmd = [
        cli, "-p",
        "--model", model_id,
        "--output-format", "text",
        "--no-session-persistence",
        "--allowedTools", "Bash", "Read", "Write", "Edit", "Grep", "Glob", "WebFetch", "WebSearch",  # CC2 full STEM tool access: SymPy/z3/numpy/scipy via Bash, source via Read/Grep/Glob, research via WebFetch/WebSearch, modification via Edit/Write.
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
            )
            elapsed = time.monotonic() - t0
            text = result.stdout.strip()
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
) -> str:
    """Call DeepSeek via their OpenAI-compatible API.

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

    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            _log(f"  [deepseek:{model_id}] retry {attempt}/{max_retries} "
                 f"(max_tokens={current_max_tokens})")
        t0 = time.monotonic()
        try:
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
) -> str:
    """Dispatch a prompt to any model based on its config. Returns response text.

    Args:
        use_output_schema: If True and model is Codex, use --output-schema
            to force structured CDSFL findings JSON output.
    """
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
