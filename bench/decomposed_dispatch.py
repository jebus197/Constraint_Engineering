#!/usr/bin/env python3
from __future__ import annotations
"""Decomposed Dispatch: multi-turn staged context loading for AI models.

Implements the "tutor" pattern: split large payloads into ordered chunks,
deliver each with a "wait" instruction, verify acknowledgement, then trigger
synthesis with the final instruction chunk.

Mathematical basis: if attention yield α(L) decays exponentially past threshold
L₀, staged delivery keeps each chunk below L₀ so the model processes each at
α ≈ 1. Monolithic delivery of the same total length would get α(L_total) ≪ 1.

    α_staged(L_total, n) ≈ Π α(Lᵢ) where each Lᵢ < L₀
    α_monolithic(L_total) = exp(−β(L_total − L₀))  for L_total > L₀

This is a testable prediction: staged delivery should empirically preserve
finding quality compared to monolithic delivery at the same total length.

Usage:
    chunks = [
        DecomposedChunk("Section 1 content", label="§1-6 Base framework"),
        DecomposedChunk("Section 2 content", label="§7 Cognitive measurement"),
        ...
    ]
    result = decomposed_dispatch(
        api="google",
        model_id="gemini-3.1-pro-preview",
        system_prompt=cdsfl_text,
        chunks=chunks,
        final_instruction="You now have the complete model. Proceed with...",
        max_tokens=32768,
    )
"""

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

# Import shared logging and circuit breaker from orchestrator
import sys
sys.path.insert(0, str(Path(__file__).parent))
from experiment_11_orchestrator import _log, CircuitBreakerTripped, CLAUDE_CLI


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DecomposedChunk:
    """One segment of a decomposed payload."""
    content: str
    label: str = ""  # human-readable label for logging

    @property
    def chars(self) -> int:
        return len(self.content)


@dataclass
class DecomposedResult:
    """Result of a decomposed dispatch."""
    text: str                          # final synthesis response
    model_id: str
    api: str
    chunks_delivered: int
    total_chars_delivered: int
    wait_responses: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0
    turns: list[dict[str, str]] = field(default_factory=list)  # full conversation


# ─────────────────────────────────────────────────────────────────────────────
# Wait instruction templates
# ─────────────────────────────────────────────────────────────────────────────

WAIT_PREFIX = (
    "=== STAGED DELIVERY — CHUNK {n} OF {total} ===\n"
    "This is part {n} of a {total}-part payload.{label_line}\n"
    "DO NOT analyse. DO NOT synthesise. DO NOT act on this content yet.\n"
    "Acknowledge receipt by responding with exactly: WAITING\n"
    "You will receive the complete problem and explicit instruction to proceed.\n"
    "=== CONTENT ===\n\n"
)

FINAL_PREFIX = (
    "=== FINAL CHUNK — CHUNK {n} OF {total} ===\n"
    "You now have the complete payload ({total} chunks, ~{total_chars:,} characters).{label_line}\n"
    "=== INSTRUCTION ===\n\n"
)


def _format_wait(n: int, total: int, label: str = "") -> str:
    label_line = f"\nLabel: {label}" if label else ""
    return WAIT_PREFIX.format(n=n, total=total, label_line=label_line)


def _format_final(n: int, total: int, total_chars: int, label: str = "") -> str:
    label_line = f"\nLabel: {label}" if label else ""
    return FINAL_PREFIX.format(
        n=n, total=total, total_chars=total_chars, label_line=label_line,
    )


def _is_waiting(response: str) -> bool:
    """Check if model acknowledged with WAITING."""
    cleaned = response.strip().upper()
    return "WAITING" in cleaned and len(cleaned) < 200


# ─────────────────────────────────────────────────────────────────────────────
# API-specific multi-turn implementations
# ─────────────────────────────────────────────────────────────────────────────

def _decomposed_gemini(
    model_id: str,
    system_prompt: str | None,
    chunks: Sequence[DecomposedChunk],
    final_instruction: str,
    max_tokens: int,
    timeout: int,
) -> DecomposedResult:
    """Multi-turn decomposed delivery via Gemini chat API."""
    from google import genai
    from google.genai import types as genai_types

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY / GOOGLE_API_KEY not set")

    try:
        import httpx
        http_client = httpx.Client(timeout=httpx.Timeout(
            connect=30.0, read=float(timeout), write=30.0, pool=30.0,
        ))
        client = genai.Client(api_key=api_key, http_options={"client": http_client})
    except (ImportError, TypeError, ValueError):
        client = genai.Client(api_key=api_key)

    total = len(chunks) + 1  # chunks + final instruction
    total_chars = sum(c.chars for c in chunks) + len(final_instruction)

    # Build conversation as list of Content parts for multi-turn
    contents: list[genai_types.Content] = []
    wait_responses: list[str] = []
    turns: list[dict[str, str]] = []

    config = genai_types.GenerateContentConfig(
        max_output_tokens=max_tokens,
        system_instruction=system_prompt if system_prompt else None,
    )

    t0 = time.monotonic()

    # Deliver each chunk, get WAITING response
    for i, chunk in enumerate(chunks):
        n = i + 1
        user_msg = _format_wait(n, total, chunk.label) + chunk.content
        contents.append(genai_types.Content(
            role="user", parts=[genai_types.Part(text=user_msg)],
        ))

        _log(f"  [gemini:{model_id}] delivering chunk {n}/{total}"
             f" ({chunk.chars:,} chars, {chunk.label or 'unlabelled'})")

        response = client.models.generate_content(
            model=model_id, contents=contents, config=config,
        )
        resp_text = (response.text or "").strip()
        wait_responses.append(resp_text)
        turns.append({"role": "user", "content": user_msg})
        turns.append({"role": "assistant", "content": resp_text})

        contents.append(genai_types.Content(
            role="model", parts=[genai_types.Part(text=resp_text)],
        ))

        if not _is_waiting(resp_text):
            _log(f"  [gemini:{model_id}] WARNING: chunk {n} got non-WAITING "
                 f"response ({len(resp_text)} chars): {resp_text[:80]}...")

    # Final instruction — trigger synthesis
    final_msg = _format_final(total, total, total_chars, "Synthesis instruction") + final_instruction
    contents.append(genai_types.Content(
        role="user", parts=[genai_types.Part(text=final_msg)],
    ))

    _log(f"  [gemini:{model_id}] delivering final instruction (chunk {total}/{total})")

    response = client.models.generate_content(
        model=model_id, contents=contents, config=config,
    )
    result_text = (response.text or "").strip()
    elapsed = time.monotonic() - t0
    turns.append({"role": "user", "content": final_msg})
    turns.append({"role": "assistant", "content": result_text})

    _log(f"  [gemini:{model_id}] synthesis complete ({elapsed:.1f}s, {len(result_text):,} chars)")

    return DecomposedResult(
        text=result_text,
        model_id=model_id,
        api="google",
        chunks_delivered=len(chunks),
        total_chars_delivered=total_chars,
        wait_responses=wait_responses,
        elapsed_s=round(elapsed, 1),
        turns=turns,
    )


def _decomposed_openrouter(
    model_id: str,
    system_prompt: str | None,
    chunks: Sequence[DecomposedChunk],
    final_instruction: str,
    max_tokens: int,
    timeout: int,
) -> DecomposedResult:
    """Multi-turn decomposed delivery via OpenRouter (CC2, ChatGPT)."""
    import openai

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    try:
        import httpx
        http_timeout = httpx.Timeout(
            connect=30.0, read=float(timeout), write=30.0, pool=30.0,
        )
    except ImportError:
        http_timeout = timeout

    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=http_timeout,
    )

    total = len(chunks) + 1
    total_chars = sum(c.chars for c in chunks) + len(final_instruction)

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    wait_responses: list[str] = []
    turns: list[dict[str, str]] = []
    t0 = time.monotonic()

    # Deliver chunks
    for i, chunk in enumerate(chunks):
        n = i + 1
        user_msg = _format_wait(n, total, chunk.label) + chunk.content
        messages.append({"role": "user", "content": user_msg})

        _log(f"  [openrouter:{model_id}] delivering chunk {n}/{total}"
             f" ({chunk.chars:,} chars, {chunk.label or 'unlabelled'})")

        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=256,  # only need "WAITING"
            temperature=0.0,
            timeout=timeout,
        )
        if not response.choices:
            raise CircuitBreakerTripped(
                "empty_response", model_id, "dispatch",
                f"API returned no choices after chunk {n} "
                f"(possible upstream 500 error)"
            )
        resp_text = (response.choices[0].message.content or "").strip()
        wait_responses.append(resp_text)
        turns.append({"role": "user", "content": user_msg})
        turns.append({"role": "assistant", "content": resp_text})
        messages.append({"role": "assistant", "content": resp_text})

        if not _is_waiting(resp_text):
            _log(f"  [openrouter:{model_id}] WARNING: chunk {n} got non-WAITING "
                 f"response ({len(resp_text)} chars): {resp_text[:80]}...")

    # Final instruction
    final_msg = _format_final(total, total, total_chars, "Synthesis instruction") + final_instruction
    messages.append({"role": "user", "content": final_msg})

    _log(f"  [openrouter:{model_id}] delivering final instruction (chunk {total}/{total})")

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.0,
        timeout=timeout,
    )
    if not response.choices:
        elapsed = time.monotonic() - t0
        raise CircuitBreakerTripped(
            "empty_response", model_id, "dispatch",
            f"API returned no choices after {elapsed:.1f}s "
            f"(possible upstream 500 error)"
        )
    result_text = (response.choices[0].message.content or "").strip()
    elapsed = time.monotonic() - t0
    turns.append({"role": "user", "content": final_msg})
    turns.append({"role": "assistant", "content": result_text})

    _log(f"  [openrouter:{model_id}] synthesis complete ({elapsed:.1f}s, {len(result_text):,} chars)")

    return DecomposedResult(
        text=result_text,
        model_id=model_id,
        api="openrouter",
        chunks_delivered=len(chunks),
        total_chars_delivered=total_chars,
        wait_responses=wait_responses,
        elapsed_s=round(elapsed, 1),
        turns=turns,
    )


def _decomposed_deepseek(
    model_id: str,
    system_prompt: str | None,
    chunks: Sequence[DecomposedChunk],
    final_instruction: str,
    max_tokens: int,
    timeout: int,
) -> DecomposedResult:
    """Multi-turn decomposed delivery via DeepSeek API."""
    import openai

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    client = openai.OpenAI(
        base_url="https://api.deepseek.com",
        api_key=api_key,
        timeout=timeout,
    )

    total = len(chunks) + 1
    total_chars = sum(c.chars for c in chunks) + len(final_instruction)

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    wait_responses: list[str] = []
    turns: list[dict[str, str]] = []
    t0 = time.monotonic()

    for i, chunk in enumerate(chunks):
        n = i + 1
        user_msg = _format_wait(n, total, chunk.label) + chunk.content
        messages.append({"role": "user", "content": user_msg})

        _log(f"  [deepseek:{model_id}] delivering chunk {n}/{total}"
             f" ({chunk.chars:,} chars, {chunk.label or 'unlabelled'})")

        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=256,
            timeout=timeout,
        )
        if not response.choices:
            raise CircuitBreakerTripped(
                "empty_response", model_id, "dispatch",
                f"API returned no choices after chunk {n} "
                f"(possible upstream 500 error)"
            )
        resp_text = (response.choices[0].message.content or "").strip()
        wait_responses.append(resp_text)
        turns.append({"role": "user", "content": user_msg})
        turns.append({"role": "assistant", "content": resp_text})
        messages.append({"role": "assistant", "content": resp_text})

        if not _is_waiting(resp_text):
            _log(f"  [deepseek:{model_id}] WARNING: chunk {n} got non-WAITING "
                 f"response ({len(resp_text)} chars): {resp_text[:80]}...")

    # Final instruction
    final_msg = _format_final(total, total, total_chars, "Synthesis instruction") + final_instruction
    messages.append({"role": "user", "content": final_msg})

    _log(f"  [deepseek:{model_id}] delivering final instruction (chunk {total}/{total})")

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    if not response.choices:
        elapsed = time.monotonic() - t0
        raise CircuitBreakerTripped(
            "empty_response", model_id, "dispatch",
            f"API returned no choices after {elapsed:.1f}s "
            f"(possible upstream 500 error)"
        )
    result_text = (response.choices[0].message.content or "").strip()
    elapsed = time.monotonic() - t0
    turns.append({"role": "user", "content": final_msg})
    turns.append({"role": "assistant", "content": result_text})

    _log(f"  [deepseek:{model_id}] synthesis complete ({elapsed:.1f}s, {len(result_text):,} chars)")

    return DecomposedResult(
        text=result_text,
        model_id=model_id,
        api="deepseek",
        chunks_delivered=len(chunks),
        total_chars_delivered=total_chars,
        wait_responses=wait_responses,
        elapsed_s=round(elapsed, 1),
        turns=turns,
    )


def _decomposed_claude_cli(
    model_id: str,
    chunks: Sequence[DecomposedChunk],
    cdsfl_directives: str,
    final_instruction: str,
    timeout: int,
) -> DecomposedResult:
    """Decomposed delivery via Claude CLI — true multi-turn via --resume.

    Uses session persistence: first chunk creates a session (--session-id),
    subsequent chunks continue it (--resume). Each WAIT-step chunk is
    acknowledged before the next is sent. The final turn triggers synthesis.

    This gives CC2 full cross-chunk context — unlike Codex's per-chunk
    independent calls, CC2 can reference earlier chunks when analysing
    later ones. Free on Max subscription.
    """
    import uuid

    cli = CLAUDE_CLI
    if not cli:
        raise FileNotFoundError(
            "Claude CLI not found. Expected 'claude' in PATH or in "
            "~/Library/Application Support/Claude/claude-code/*/claude.app/Contents/MacOS/claude"
        )

    total = len(chunks) + 1  # chunks + final instruction
    total_chars = sum(c.chars for c in chunks) + len(final_instruction)
    session_id = str(uuid.uuid4())

    wait_responses: list[str] = []
    turns: list[dict[str, str]] = []
    t0 = time.monotonic()

    _log(f"  [claude-cli] multi-turn dispatch: {len(chunks)} chunks + final, "
         f"session={session_id[:8]}..., ~{total_chars:,} chars total")

    # Deliver each chunk with WAIT instruction
    for i, chunk in enumerate(chunks):
        n = i + 1
        user_msg = _format_wait(n, total, chunk.label) + chunk.content

        if i == 0:
            # First chunk: create session with --session-id and --system-prompt
            cmd = [
                cli, "-p",
                "--model", model_id,
                "--output-format", "text",
                "--session-id", session_id,
                "--disallowed-tools", "Bash", "Edit", "Write",
                "--system-prompt", cdsfl_directives,
            ]
        else:
            # Subsequent chunks: resume existing session
            cmd = [
                cli, "-p",
                "--output-format", "text",
                "--resume", session_id,
            ]

        _log(f"  [claude-cli] delivering chunk {n}/{total}"
             f" ({chunk.chars:,} chars, {chunk.label or 'unlabelled'})")

        try:
            result = subprocess.run(
                cmd,
                input=user_msg,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0:
                stderr = result.stderr.strip()[:200]
                _log(f"  [claude-cli] chunk {n} failed (rc={result.returncode}): {stderr}")
                wait_responses.append(f"FAILED: {stderr}")
                turns.append({"role": "user", "content": f"[chunk {n}: {chunk.chars} chars]"})
                turns.append({"role": "assistant", "content": f"FAILED: {stderr}"})
                # Session may be broken — can't continue
                break

            resp_text = result.stdout.strip()
            wait_responses.append(resp_text)
            turns.append({"role": "user", "content": user_msg[:200] + "..."})
            turns.append({"role": "assistant", "content": resp_text})

            if not _is_waiting(resp_text):
                _log(f"  [claude-cli] WARNING: chunk {n} got non-WAITING "
                     f"response ({len(resp_text)} chars): {resp_text[:80]}...")

        except subprocess.TimeoutExpired:
            _log(f"  [claude-cli] chunk {n} timed out after {timeout}s")
            wait_responses.append(f"TIMEOUT ({timeout}s)")
            turns.append({"role": "user", "content": f"[chunk {n}: {chunk.chars} chars]"})
            turns.append({"role": "assistant", "content": f"TIMEOUT after {timeout}s"})
            break

    # Final instruction — trigger synthesis via --resume
    final_msg = _format_final(
        total, total, total_chars, "Synthesis instruction"
    ) + final_instruction

    cmd_final = [
        cli, "-p",
        "--output-format", "text",
        "--resume", session_id,
    ]

    _log(f"  [claude-cli] delivering final instruction (chunk {total}/{total})")

    try:
        result = subprocess.run(
            cmd_final,
            input=final_msg,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - t0

        if result.returncode != 0:
            stderr = result.stderr.strip()[:200]
            raise RuntimeError(f"claude CLI final turn failed (rc={result.returncode}): {stderr}")

        result_text = result.stdout.strip()
        if not result_text:
            raise CircuitBreakerTripped(
                "empty_response", "Claude CLI", "dispatch",
                f"Empty synthesis after {elapsed:.1f}s",
            )

        turns.append({"role": "user", "content": final_msg[:200] + "..."})
        turns.append({"role": "assistant", "content": result_text})

        _log(f"  [claude-cli] synthesis complete ({elapsed:.1f}s, {len(result_text):,} chars)")

    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - t0
        raise CircuitBreakerTripped(
            "timeout", "Claude CLI", "dispatch",
            f"Synthesis timed out after {elapsed:.1f}s",
        )

    return DecomposedResult(
        text=result_text,
        model_id=f"claude-cli/{model_id}",
        api="claude_cli",
        chunks_delivered=len(chunks),
        total_chars_delivered=total_chars,
        wait_responses=wait_responses,
        elapsed_s=round(elapsed, 1),
        turns=turns,
    )


def _decomposed_codex(
    chunks: Sequence[DecomposedChunk],
    cdsfl_directives: str,
    final_instruction: str,
    timeout: int,
) -> DecomposedResult:
    """Decomposed delivery via Codex CLI — per-chunk independent calls.

    codex exec is single-shot (no session persistence), so true multi-turn
    is impossible. Instead of accumulating all chunks into one giant prompt
    (which caused 189K payloads and timeouts), we dispatch each chunk as an
    independent codex exec call with its own findings request, then merge
    all findings at the end.

    Each chunk gets:
    - The CDSFL system directives
    - A brief context header (what the chunk is, what round, chunk N of M)
    - The chunk content itself
    - The FFF synthesis instruction

    This keeps each call under ~40K chars, well within Codex's comfort zone.
    The trade-off is that Codex can't cross-reference between chunks within
    a single call — but the confer rounds handle cross-chunk synthesis anyway.
    """
    total = len(chunks) + 1
    total_chars = sum(c.chars for c in chunks) + len(final_instruction)

    all_responses: list[str] = []
    wait_responses: list[str] = []
    turns: list[dict[str, str]] = []
    t0 = time.monotonic()

    cmd_base = [
        "codex", "exec",
        "-c", 'model_reasoning_effort="xhigh"',
        "-c", "mcp_servers={}",
        "-c", "plugins={}",
        "--ephemeral",
        "-",
    ]

    _log(f"  [codex] per-chunk dispatch: {len(chunks)} independent calls, "
         f"~{total_chars:,} chars total")

    for i, chunk in enumerate(chunks):
        n = i + 1
        # Build a self-contained prompt for this chunk
        chunk_prompt = (
            "=== SYSTEM INSTRUCTIONS (CDSFL Operating Constraints) ===\n"
            f"{cdsfl_directives}\n"
            "=== END SYSTEM INSTRUCTIONS ===\n\n"
            f"=== CHUNK {n} OF {len(chunks)} ({chunk.label or 'unlabelled'}) ===\n"
            f"You are reviewing one section of a larger codebase. This is chunk "
            f"{n} of {len(chunks)}. Other chunks are being reviewed in parallel.\n"
            f"Focus your analysis on the code in THIS chunk only.\n\n"
            f"{chunk.content}\n"
            f"=== END CHUNK ===\n\n"
            f"=== INSTRUCTION ===\n"
            f"{final_instruction}\n"
            f"=== END INSTRUCTION ==="
        )

        _log(f"  [codex] dispatching chunk {n}/{len(chunks)}"
             f" ({chunk.chars:,} chars, {chunk.label or 'unlabelled'},"
             f" prompt={len(chunk_prompt):,} chars)")

        try:
            result = subprocess.run(
                cmd_base,
                input=chunk_prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0:
                stderr = result.stderr.strip()[:200]
                _log(f"  [codex] chunk {n} failed (rc={result.returncode}): {stderr}")
                wait_responses.append(f"FAILED (rc={result.returncode})")
                turns.append({"role": "user", "content": f"[chunk {n}: {chunk.chars} chars]"})
                turns.append({"role": "assistant", "content": f"FAILED: {stderr}"})
                continue

            resp_text = result.stdout.strip()
            chunk_elapsed = time.monotonic() - t0

            if resp_text:
                all_responses.append(
                    f"=== FINDINGS FROM CHUNK {n}/{len(chunks)}"
                    f" ({chunk.label or 'unlabelled'}) ===\n{resp_text}"
                )
                _log(f"  [codex] chunk {n} done ({chunk_elapsed:.1f}s cumulative,"
                     f" {len(resp_text):,} chars response)")
            else:
                _log(f"  [codex] chunk {n} returned empty response")

            wait_responses.append(f"OK ({len(resp_text)} chars)")
            turns.append({"role": "user", "content": f"[chunk {n}: {chunk.chars} chars]"})
            turns.append({"role": "assistant", "content": resp_text[:500] if resp_text else "(empty)"})

        except subprocess.TimeoutExpired:
            _log(f"  [codex] chunk {n} timed out after {timeout}s — skipping")
            wait_responses.append(f"TIMEOUT ({timeout}s)")
            turns.append({"role": "user", "content": f"[chunk {n}: {chunk.chars} chars]"})
            turns.append({"role": "assistant", "content": f"TIMEOUT after {timeout}s"})

    elapsed = time.monotonic() - t0

    if not all_responses:
        raise CircuitBreakerTripped(
            "empty_response", "Codex", "dispatch",
            f"All {len(chunks)} chunk calls failed or returned empty after {elapsed:.1f}s",
        )

    # Merge all chunk responses into one combined output
    result_text = "\n\n".join(all_responses)

    _log(f"  [codex] all chunks complete ({elapsed:.1f}s total,"
         f" {len(all_responses)}/{len(chunks)} succeeded,"
         f" {len(result_text):,} chars merged)")

    return DecomposedResult(
        text=result_text,
        model_id="codex-exec/gpt-5.4",
        api="codex_exec",
        chunks_delivered=len(chunks),
        total_chars_delivered=total_chars,
        wait_responses=wait_responses,
        elapsed_s=round(elapsed, 1),
        turns=turns,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public interface
# ─────────────────────────────────────────────────────────────────────────────

def decomposed_dispatch(
    api: str,
    model_id: str | None,
    system_prompt: str | None,
    chunks: Sequence[DecomposedChunk],
    final_instruction: str,
    max_tokens: int = 32768,
    timeout: int = 600,
    cdsfl_directives: str | None = None,
) -> DecomposedResult:
    """Dispatch a decomposed payload to any supported API.

    Args:
        api: One of "google", "openrouter", "deepseek", "codex_exec".
        model_id: Model identifier (not needed for codex_exec).
        system_prompt: CDSFL system prompt (used as system_instruction for
            Gemini, system message for OpenRouter/DeepSeek).
        chunks: Ordered sequence of content chunks to deliver.
        final_instruction: The synthesis instruction sent after all chunks.
        max_tokens: Max tokens for the final synthesis response.
        timeout: Per-call timeout in seconds.
        cdsfl_directives: Raw CDSFL text for Codex (which embeds it in prompt).

    Returns:
        DecomposedResult with the synthesis response and conversation history.
    """
    _log(f"  Decomposed dispatch: {api}/{model_id or 'codex'}, "
         f"{len(chunks)} chunks, ~{sum(c.chars for c in chunks):,} chars")

    if api == "claude_cli":
        # Claude CLI is single-shot like Codex — use per-chunk independent calls
        return _decomposed_claude_cli(
            model_id or "opus", chunks, cdsfl_directives or system_prompt or "",
            final_instruction, timeout,
        )
    elif api == "google":
        return _decomposed_gemini(
            model_id, system_prompt, chunks, final_instruction,
            max_tokens, timeout,
        )
    elif api == "openrouter":
        return _decomposed_openrouter(
            model_id, system_prompt, chunks, final_instruction,
            max_tokens, timeout,
        )
    elif api == "deepseek":
        return _decomposed_deepseek(
            model_id, system_prompt, chunks, final_instruction,
            max_tokens, timeout,
        )
    elif api == "codex_exec":
        return _decomposed_codex(
            chunks, cdsfl_directives or system_prompt or "",
            final_instruction, timeout,
        )
    else:
        raise ValueError(f"Unknown API: {api}")


def save_decomposed_result(
    result: DecomposedResult,
    output_dir: str | Path,
    label: str,
    round_idx: int = 0,
) -> Path:
    """Save a decomposed dispatch result to JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    filename = f"round{round_idx}_{label.lower()}_{ts}.json"
    outfile = output_dir / filename

    outfile.write_text(json.dumps({
        "model": label,
        "model_id": result.model_id,
        "api": result.api,
        "round": round_idx,
        "chunks_delivered": result.chunks_delivered,
        "total_chars_delivered": result.total_chars_delivered,
        "response_chars": len(result.text),
        "elapsed_s": result.elapsed_s,
        "wait_responses": result.wait_responses,
        "response": result.text,
        "turns": result.turns,
    }, indent=2), encoding="utf-8")

    _log(f"  Saved: {outfile}")
    return outfile
