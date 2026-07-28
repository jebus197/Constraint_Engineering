#!/usr/bin/env python3
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
from __future__ import annotations

import json
import os
import re
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
# Synthesis-turn tool loop (GATED, default OFF — "tools decide" on the
# decomposed path, 3 June 2026)
# ─────────────────────────────────────────────────────────────────────────────
# Reuses the validated OpenAI tool-call loop + sandboxed executor from the
# orchestrator. Applied ONLY to the FINAL synthesis create() of the OpenAI-
# compatible decomposed routes (openrouter, deepseek). Per-chunk delivery
# turns never touch this. Imported lazily so the non-tool decomposed paths
# keep zero import-time dependency on the falsifier module.

# Gated falsifier-format override (I1 fix, 2026-06-06). Appended to the
# DECOMPOSED synthesis prompt ONLY when enable_tools is on, to overrule the
# legacy prose "FALSIFICATION (FALSIFIER/ATTEMPT/RESULT)" triad that the live run
# proved steers models to prose falsifiers (zero testable). Default-off: when
# enable_tools is False this string is never appended, so behaviour is
# byte-identical. Includes a worked example (panel/Gemini point: a few-shot
# example beats abstract rules).
_RUNNABLE_FALSIFIER_OVERRIDE = (
    "\n\n=== CRITICAL FALSIFIER OVERRIDE (tools enabled) ===\n"
    "This OVERRIDES the prose 'FALSIFICATION (FALSIFIER/ATTEMPT/RESULT)' format "
    "named above. For EVERY finding you mark CRITICAL, the falsifier MUST be a "
    "RUNNABLE code block, never prose. Write the literal line 'FALSIFIER:' on its "
    "own line, then a fenced ```python block that:\n"
    "  1. imports the REAL target module (e.g. 'from bench.cdsfl_registry.composer "
    "import compose') -- never a retyped copy of the code under review;\n"
    "  2. raises AssertionError, or prints the token FALSIFIED, IF AND ONLY IF the "
    "claimed defect is genuinely present; exits cleanly if the claim is false.\n"
    "Run it with the execute_python tool first to confirm it behaves. The runner "
    "RE-RUNS this exact ```python block and ITS result decides the verdict -- your "
    "prose does not. A prose-only or missing FALSIFIER cannot be confirmed and is "
    "sent to a human. Required form (worked example):\n"
    "FALSIFIER:\n"
    "```python\n"
    "from bench.dm._similarity import jaccard_similarity\n"
    "from bench.dm._types import Finding\n"
    "f = Finding('a', 'm', 0, 2, 0.8, 0.5, 'desc')\n"
    "# claimed defect: self-similarity is not maximal\n"
    "assert jaccard_similarity(f, f) < 1.0, 'defect present: self-sim < 1.0'\n"
    "print('FALSIFIED: self-similarity is not 1.0')\n"
    "```"
)


def _openai_synthesis_with_tools(
    client,
    model_id: str,
    synthesis_messages: list[dict],
    max_tokens: int,
    timeout: int,
    extra_body: dict | None = None,
) -> str:
    """Run the synthesis turn with execute_python tool access and return the
    model's final (no-tool-call) text.

    Thin wrapper over the orchestrator's :func:`_run_openai_tool_loop`
    (max 6 iterations, ``tool_choice="auto"``, sandboxed
    ``default_tool_executor``). Used only when ``enable_tools=True`` on the
    OpenAI-compatible decomposed routes; the byte-identical default path never
    calls this.

    ``extra_body`` (default None) is forwarded so the synthesis turn honours
    the same reasoning.effort the rest of the dispatch path already passes via
    dispatch(); previously it was silently dropped here, starving reasoning
    models of visible-content budget on the synthesis turn.
    """
    from experiment_11_orchestrator import (
        EXECUTE_PYTHON_TOOL,
        default_tool_executor,
        _run_openai_tool_loop,
    )
    return _run_openai_tool_loop(
        client=client,
        model_id=model_id,
        messages=synthesis_messages,
        tools=[EXECUTE_PYTHON_TOOL],
        tool_executor=default_tool_executor,
        max_iters=6,
        # Gate-on synthesis budget floor: this wrapper is enable_tools-only, so a
        # reasoning model must not be starved of visible-content budget on the
        # synthesis turn (DeepSeek/Gemini burn 18K-35K reasoning tokens).
        max_tokens=max(max_tokens, _PHASE1_GATE_TOKENS),
        timeout=timeout,
        extra_body=extra_body,
    )


def _record_synthesis_tool_turns(
    turns: list[dict[str, str]], synthesis_messages: list[dict],
) -> None:
    """Append the synthesis tool-call/result turns into the conversation log.

    ``_run_openai_tool_loop`` mutates ``synthesis_messages`` in place: any
    assistant message carrying ``tool_calls`` and any subsequent ``role:tool``
    result message is appended during the loop. This copies those into
    ``turns`` (the DecomposedResult conversation) so a downstream consumer —
    the smoke test, a live-run audit — can see that the model invoked
    execute_python during synthesis. No-op when the loop made no tool calls.
    """
    for m in synthesis_messages:
        role = m.get("role")
        if role == "assistant" and m.get("tool_calls"):
            names = ", ".join(
                tc.get("function", {}).get("name", "?")
                for tc in m.get("tool_calls", [])
            )
            turns.append({
                "role": "assistant_tool_call",
                "content": f"[tool_calls: {names}] {m.get('content') or ''}",
            })
        elif role == "tool":
            turns.append({
                "role": "tool_result",
                "content": str(m.get("content") or "")[:2000],
            })


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


# Phase-1 chunk budget cap for reasoning models.
#
# Reasoning models (DeepSeek V4 Pro, Gemini 3.1 Pro) emit a
# chain-of-thought into a separate channel before the final answer.
# With a 4096 max_tokens cap, the reasoning consumed the budget and
# the visible `content` came back empty (continuation Anomaly 1,
# 15 May 2026). The cap was raised to 8192 to give reasoning models
# room to emit final content after the trace. The cap is retained.
#
# UPDATE 2026-05-20 (founder-directed): the prior session also added
# a `reasoning_content` fallback in `_extract_message_text` so the
# trace would be returned when `content` came back empty. That fallback
# silently substituted the model's chain-of-thought for its actual
# answer (the two are often weakly coupled — visible reasoning traces
# are partly performative and unfaithful to the answer-generating
# computation), and it short-circuited the established ITC retry /
# restart-fresh protocol that exists for exactly this failure class.
# REMOVED. Content is now content-only; empty propagates honestly to
# the runner's CircuitBreakerTripped handler and engages ITC as the
# protocol was designed to do.
_PHASE1_MAX_TOKENS = 8192

# Gate-on per-turn budget floor (2026-06-06). Reasoning models (Gemini-3.1-pro,
# DeepSeek-v4-pro) burn 18K-35K tokens on private reasoning; at the 8192 default
# their visible content truncates to empty (finish=length, content=0), which
# blinds the synthesis turn. When the falsifier gate is ON, lift each turn's
# budget (Phase-1 chunk analysis AND synthesis) to at least this floor so
# reasoning models leave room for content. Gate OFF keeps the 8192 default
# byte-identically, so existing non-gate experiments are unchanged.
_PHASE1_GATE_TOKENS = 32768


def _gate_turn_budget(max_tokens: int, enable_tools: bool) -> int:
    """Per-turn output budget for a decomposed Phase-1 chunk analysis. Gate ON:
    at least _PHASE1_GATE_TOKENS so reasoning models are not starved. Gate OFF:
    the legacy _PHASE1_MAX_TOKENS (byte-identical to pre-2026-06-06)."""
    return max(max_tokens, _PHASE1_GATE_TOKENS) if enable_tools else _PHASE1_MAX_TOKENS


# Synthesis safety-net (2026-06-06): if a Phase-1 chunk analysis comes back empty
# or too thin to be usable (reasoning-budget exhaustion, lost tool-call markup, a
# transient empty), the synthesis turn would otherwise be blind to that section
# and declare "no code provided" (the Gemini decomposed crap-out). When an
# analysis is below this threshold, fall back to the chunk's RAW content so the
# synthesis can assess the code directly. Bounded: only failed chunks carry raw
# content, so a multi-chunk payload does not balloon to the full original size.
_MIN_ANALYSIS_CHARS = 200


def _synthesis_analyses_text(per_chunk_analyses: list[dict]) -> str:
    """Build the synthesis prompt's analyses section, substituting raw chunk
    content for any Phase-1 analysis that came back empty/thin so synthesis is
    never blind. Each entry must carry 'label', 'analysis', and 'content'."""
    blocks = []
    for a in per_chunk_analyses:
        label = a.get("label", "chunk")
        analysis = (a.get("analysis") or "").strip()
        if len(analysis) >= _MIN_ANALYSIS_CHARS:
            blocks.append(f"=== YOUR ANALYSIS OF {label} ===\n{analysis}")
        else:
            blocks.append(
                f"=== {label}: PHASE-1 ANALYSIS UNAVAILABLE — RAW SECTION FOLLOWS ===\n"
                f"(Your per-section analysis was empty or incomplete. Analyse this "
                f"section directly as part of your synthesis.)\n\n"
                f"{a.get('content', '')}"
            )
    return "\n\n".join(blocks)


# Gate-on falsifier format-repair (2026-06-06). A model can find real issues but
# attach its falsifier in a non-runnable form — DeepSeek-v4-pro ignores the §2
# runnable instruction and writes the legacy prose "FALSIFIER: <prose> / ATTEMPT:
# ```python ...```" shape, so the runner's extractor finds no runnable block and
# the finding cannot be tool-adjudicated. This re-prompts ONCE for the strict
# runnable form. It fires only when a response HAS findings but NO extractable
# runnable falsifier, so the tool-loop routes (which already emit runnable
# falsifiers via execute_python) are untouched. The repair is accepted only if it
# actually produced a runnable falsifier; otherwise the original is kept. The
# prompt explicitly forbids inventing defects / inflating severity (no faking).
_RUNNABLE_FALSIFIER_RE = re.compile(r"FALSIFIER:\s*\n?\s*```python", re.IGNORECASE)
_FINDING_PRESENT_RE = re.compile(r"(?im)FINDING_ID|^###\s+Finding\b|^\**F\d{2,3}\b")
_FORMAT_REPAIR_PROMPT = (
    "Your prior review (below) found real issues but did NOT attach RUNNABLE "
    "falsifiers — it used prose or an ATTEMPT/RESULT shape. Rewrite it so EACH "
    "finding carries a runnable falsifier. Output each finding EXACTLY as:\n"
    "FINDING_ID: Fxxx\nSEVERITY: <0.0-1.0, your HONEST rating — do not inflate>\n"
    "FIND: <one line>\nFALSIFIER:\n```python\n"
    "# standalone script: import the REAL target module, reproduce the defect,\n"
    "# raise AssertionError or print FALSIFIED IF AND ONLY IF the defect is present;\n"
    "# exit cleanly (returncode 0, no AssertionError, no FALSIFIED) otherwise.\n"
    "```\n"
    "Rules: the FALSIFIER section contains ONLY the fenced python block — no prose, "
    "no ATTEMPT/RESULT. The python MUST import the real module and run as-is. Do NOT "
    "invent defects and do NOT change your honest severities. Output ONLY the "
    "findings.\n\n=== YOUR PRIOR REVIEW ===\n"
)


def _falsifier_format_repair(
    client, model_id: str, response: str, max_tokens: int, timeout: int,
    extra_body: dict | None = None,
) -> str:
    """Re-prompt ONCE for runnable falsifiers when a response has findings but no
    extractable runnable falsifier block. No-op otherwise; original kept unless
    the repair genuinely yields a runnable block. See module comment above."""
    if not response:
        return response
    if _RUNNABLE_FALSIFIER_RE.search(response) or not _FINDING_PRESENT_RE.search(response):
        return response
    kwargs = dict(
        model=model_id,
        messages=[{"role": "user", "content": _FORMAT_REPAIR_PROMPT + response[:12000]}],
        max_tokens=max_tokens, temperature=0.0, timeout=timeout,
    )
    if extra_body:
        kwargs["extra_body"] = extra_body
    try:
        r = client.chat.completions.create(**kwargs)
        repaired = (r.choices[0].message.content or "").strip() if r.choices else ""
    except Exception:  # noqa: BLE001
        return response
    if repaired and _RUNNABLE_FALSIFIER_RE.search(repaired):
        _log(f"  [{model_id}] falsifier format-repair applied "
             f"({len(response):,} -> {len(repaired):,} chars)")
        return repaired
    return response


def _extract_message_text(message) -> str:
    """Return `content` from a chat completion message — content only.

    Empty content is honestly empty. Prior versions fell back to
    `reasoning_content` / `reasoning` to "recover" an answer from the
    model's chain-of-thought; that substitution is methodologically
    unsound (reasoning traces are often weakly coupled to conclusions)
    and bypassed the ITC protocol that handles empty responses by
    design. Removed 2026-05-20. Empty `content` returns "" and
    propagates to the runner, which classifies it via ITC as a
    TRANSIENT_FAILURE → restart_fresh adaptation.
    """
    return (getattr(message, "content", None) or "").strip()


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
    enable_tools: bool = False,
) -> DecomposedResult:
    """Multi-turn decomposed delivery via Gemini chat API.

    enable_tools is accepted for signature consistency with the other
    decomposed impls but is intentionally NOT acted on here: no Gemini
    tool loop is wired for the synthesis turn, so the synthesis stays
    tool-less regardless of the flag.
    """
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
    enable_tools: bool = False,
    extra_body: dict | None = None,
) -> DecomposedResult:
    """Independent-session decomposed delivery via OpenRouter.

    Same independent-session pattern as DeepSeek: each chunk gets its own
    conversation to prevent context accumulation from exceeding model limits.
    GPT-5.4 via OpenRouter has a 128K-token hard limit; with 350K+ char
    payloads, multi-turn accumulation consistently exceeded this by R1
    (Exp 39 Round 1: ChatGPT refused on chunk 3 of accumulated context).

    Fix (13 April 2026): independent sessions per chunk + synthesis.
    """
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

    wait_responses: list[str] = []
    turns: list[dict[str, str]] = []
    per_chunk_analyses: list[dict[str, str]] = []
    t0 = time.monotonic()

    # Phase 1: Independent per-chunk analysis sessions
    for i, chunk in enumerate(chunks):
        n = i + 1
        chunk_messages: list[dict[str, str]] = []
        if system_prompt:
            chunk_messages.append({"role": "system", "content": system_prompt})

        chunk_prompt = (
            f"=== CODE REVIEW — SECTION {n} OF {len(chunks)} ===\n"
            f"Section: {chunk.label or f'chunk_{n}'} "
            f"({chunk.chars:,} chars)\n"
            f"You are reviewing section {n} of {len(chunks)} code sections. "
            f"Analyse this section thoroughly for bugs, logic errors, "
            f"race conditions, security issues, and correctness problems.\n\n"
            f"Follow the complete 4-Layer Review Protocol and operational "
            f"directive from your system instructions. For each finding, "
            f"include ALL six mandatory sections:\n"
            f"  FIND — the issue, location, and evidence.\n"
            f"  FOLLOW — trace consequences before fixing. What depends on "
            f"this? What breaks downstream?\n"
            f"  ANALYSE — classify constraint as HARD or SOFT. State premises "
            f"explicitly, derive conclusion through concrete evidence "
            f"(Meta Structured Reasoning Protocol).\n"
            f"  FIX — simplest sufficient correction addressing root cause "
            f"and FOLLOW consequences. Express as SEARCH/REPLACE blocks.\n"
            f"  FALSIFICATION — mandatory. State: FALSIFIER (what would "
            f"disprove your FIND), ATTEMPT (what you tested), RESULT "
            f"(did the claim hold?). Then try to break your FIX.\n"
            f"  CORROBORATION — compute R_k(i) numerically using the "
            f"self-assessment equation. Show your working: R_old (default "
            f"0.5), η (novelty, 0-1), d (independence, 0-1), p (capability, "
            f"0-1), q=η·d·p, R_det=R_old·(1-q)/(1-q·R_old), S_k (fix "
            f"quality, 0-1), ν_b, ν_f, ν_eff, final R_k. Qualitative "
            f"labels alone are insufficient — show the numbers.\n\n"
            f"Findings missing any section will be rejected. "
            f"Do NOT synthesise across sections yet — "
            f"a synthesis step follows.\n"
            f"=== CONTENT ===\n\n{chunk.content}"
        )
        chunk_messages.append({"role": "user", "content": chunk_prompt})

        _log(f"  [openrouter:{model_id}] independent session {n}/{len(chunks)}"
             f" ({chunk.chars:,} chars, {chunk.label or 'unlabelled'})")

        # Phase-1 budget fix (2026-06-06): gate-on, lift the chunk-analysis budget
        # to the reasoning-aware floor so Gemini/DeepSeek leave room for visible
        # content (otherwise content=0 -> blind synthesis). Forward any reasoning
        # config (e.g. Gemini reasoning.effort) too. Gate-off keeps 8192.
        _p1_kwargs = dict(
            model=model_id,
            messages=chunk_messages,
            max_tokens=_gate_turn_budget(max_tokens, enable_tools),
            temperature=0.0,
            timeout=timeout,
        )
        if extra_body:
            _p1_kwargs["extra_body"] = extra_body
        response = client.chat.completions.create(**_p1_kwargs)
        if not response.choices:
            raise CircuitBreakerTripped(
                "empty_response", model_id, "dispatch",
                f"API returned no choices after chunk {n} "
                f"(possible upstream 500 error)"
            )
        resp_text = _extract_message_text(response.choices[0].message)
        # Empty resp_text propagates honestly — runner-level ITC will
        # classify it as TRANSIENT_FAILURE on round close and adapt.
        wait_responses.append(resp_text)
        turns.append({"role": "user", "content": chunk_prompt})
        turns.append({"role": "assistant", "content": resp_text})
        per_chunk_analyses.append({
            "label": chunk.label or f"chunk_{n}",
            "analysis": resp_text,
            "content": chunk.content,
        })

        _log(f"  [openrouter:{model_id}] section {n} analysis complete "
             f"({len(resp_text):,} chars)")

    # Phase 2: Synthesis from per-chunk analyses
    synthesis_messages: list[dict[str, str]] = []
    if system_prompt:
        synthesis_messages.append({"role": "system", "content": system_prompt})

    analyses_text = _synthesis_analyses_text(per_chunk_analyses)

    synthesis_prompt = (
        f"You have just reviewed {len(chunks)} code sections independently. "
        f"Below are your per-section analyses.\n\n"
        f"{analyses_text}\n\n"
        f"=== SYNTHESIS INSTRUCTION ===\n"
        f"Now combine your findings into a single comprehensive review. "
        f"Include cross-section issues that span multiple files. "
        f"Deduplicate findings that appear in multiple sections. "
        f"Preserve ALL six sections for every finding: FIND, FOLLOW, "
        f"ANALYSE, FIX, FALSIFICATION (FALSIFIER/ATTEMPT/RESULT), and "
        f"CORROBORATION (numerical R_k). For cross-section findings, "
        f"compute a new R_k reflecting the broader context. "
        f"Run a global P-pass across your complete output — look for "
        f"cross-finding contradictions and missed interactions. "
        f"Every finding MUST retain numerical R_k and structured "
        f"FALSIFICATION — do not reduce to qualitative labels.\n\n"
        f"{final_instruction}"
        + (_RUNNABLE_FALSIFIER_OVERRIDE if enable_tools else "")
    )
    synthesis_messages.append({"role": "user", "content": synthesis_prompt})

    _log(f"  [openrouter:{model_id}] delivering synthesis instruction "
         f"(chunk {total}/{total})"
         f"{' [tools-on]' if enable_tools else ''}")

    if enable_tools:
        # GATED synthesis-turn tool loop: the model may run execute_python
        # during synthesis to attach a runnable falsifier. Per-chunk turns
        # above stayed tool-less. The loop raises CircuitBreakerTripped on an
        # empty-choices response internally, mirroring the no-tools guard.
        result_text = (_openai_synthesis_with_tools(
            client, model_id, synthesis_messages, max_tokens, timeout,
            extra_body=extra_body,
        ) or "").strip()
        elapsed = time.monotonic() - t0
    else:
        create_kwargs = dict(
            model=model_id,
            messages=synthesis_messages,
            max_tokens=max_tokens,
            temperature=0.0,
            timeout=timeout,
        )
        if extra_body:
            create_kwargs["extra_body"] = extra_body
        response = client.chat.completions.create(**create_kwargs)
        if not response.choices:
            elapsed = time.monotonic() - t0
            raise CircuitBreakerTripped(
                "empty_response", model_id, "dispatch",
                f"API returned no choices after {elapsed:.1f}s "
                f"(possible upstream 500 error)"
            )
        result_text = (response.choices[0].message.content or "").strip()
        elapsed = time.monotonic() - t0

    # 2026-05-20 (founder-directed): the synthesis-layer chunk-analyses
    # reconstruction (commit 35c44b6) was removed. It concatenated the
    # Phase-1 per-chunk analyses when Phase 2 synthesis came back empty
    # and presented the result as the model's answer. That was a
    # methodologically unsound salvage (it returned the model's
    # intermediate per-chunk thinking, not its actual synthesis) and it
    # bypassed the runner's ITC protocol which is designed to handle
    # exactly this failure (retry → restart-fresh → HIL-flag). Empty
    # synthesis now propagates honestly and engages ITC as designed.
    if not result_text:
        _log(f"  [openrouter:{model_id}] WARN: synthesis returned 0 chars "
             f"(propagating empty — runner ITC will classify as "
             f"TRANSIENT_FAILURE and adapt next round)")

    turns.append({"role": "user", "content": synthesis_prompt})
    # When the synthesis tool loop ran, record the intermediate tool-call
    # turns (assistant tool_calls + tool results) so tool use is observable
    # in DecomposedResult.turns. _openai_synthesis_with_tools mutates
    # synthesis_messages in place; everything after the initial system/user
    # entries is loop-appended.
    if enable_tools:
        _record_synthesis_tool_turns(turns, synthesis_messages)
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
    enable_tools: bool = False,
) -> DecomposedResult:
    """Independent-session decomposed delivery via DeepSeek API.

    DeepSeek Reasoner has a 131K token hard limit. The original multi-turn
    accumulation approach sends ALL prior chunks in every API call, which
    exceeds this limit when the total payload is >350K chars (Exp 39 hit
    201K tokens on the final turn, causing 100% failure rate).

    Fix (13 April 2026): independent sessions per chunk + synthesis.
    Each chunk gets its own conversation (no history accumulation), then
    a final synthesis call combines the per-chunk analyses. Token budget
    per call never exceeds ~55K tokens even for the largest chunks.
    """
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

    wait_responses: list[str] = []
    turns: list[dict[str, str]] = []
    per_chunk_analyses: list[dict[str, str]] = []
    t0 = time.monotonic()

    # Phase 1: Independent per-chunk analysis sessions
    for i, chunk in enumerate(chunks):
        n = i + 1
        chunk_messages: list[dict[str, str]] = []
        if system_prompt:
            chunk_messages.append({"role": "system", "content": system_prompt})

        chunk_prompt = (
            f"=== CODE REVIEW — SECTION {n} OF {len(chunks)} ===\n"
            f"Section: {chunk.label or f'chunk_{n}'} "
            f"({chunk.chars:,} chars)\n"
            f"You are reviewing section {n} of {len(chunks)} code sections. "
            f"Analyse this section thoroughly for bugs, logic errors, "
            f"race conditions, security issues, and correctness problems.\n\n"
            f"Follow the complete 4-Layer Review Protocol and operational "
            f"directive from your system instructions. For each finding, "
            f"include ALL six mandatory sections:\n"
            f"  FIND — the issue, location, and evidence.\n"
            f"  FOLLOW — trace consequences before fixing. What depends on "
            f"this? What breaks downstream?\n"
            f"  ANALYSE — classify constraint as HARD or SOFT. State premises "
            f"explicitly, derive conclusion through concrete evidence "
            f"(Meta Structured Reasoning Protocol).\n"
            f"  FIX — simplest sufficient correction addressing root cause "
            f"and FOLLOW consequences. Express as SEARCH/REPLACE blocks.\n"
            f"  FALSIFICATION — mandatory. State: FALSIFIER (what would "
            f"disprove your FIND), ATTEMPT (what you tested), RESULT "
            f"(did the claim hold?). Then try to break your FIX.\n"
            f"  CORROBORATION — compute R_k(i) numerically using the "
            f"self-assessment equation. Show your working: R_old (default "
            f"0.5), η (novelty, 0-1), d (independence, 0-1), p (capability, "
            f"0-1), q=η·d·p, R_det=R_old·(1-q)/(1-q·R_old), S_k (fix "
            f"quality, 0-1), ν_b, ν_f, ν_eff, final R_k. Qualitative "
            f"labels alone are insufficient — show the numbers.\n\n"
            f"Findings missing any section will be rejected. "
            f"Do NOT synthesise across sections yet — "
            f"a synthesis step follows.\n"
            f"=== CONTENT ===\n\n{chunk.content}"
        )
        chunk_messages.append({"role": "user", "content": chunk_prompt})

        _log(f"  [deepseek:{model_id}] independent session {n}/{len(chunks)}"
             f" ({chunk.chars:,} chars, {chunk.label or 'unlabelled'})")

        response = client.chat.completions.create(
            model=model_id,
            messages=chunk_messages,
            # Gate-on reasoning-aware budget: DeepSeek-v4-pro is a reasoning model
            # (burns ~35K reasoning tokens); at 8192 its Phase-1 content empties
            # (finish=length, content=0). Gate-off keeps 8192 byte-identically.
            max_tokens=_gate_turn_budget(max_tokens, enable_tools),
            timeout=timeout,
        )
        if not response.choices:
            raise CircuitBreakerTripped(
                "empty_response", model_id, "dispatch",
                f"API returned no choices after chunk {n} "
                f"(possible upstream 500 error)"
            )
        resp_text = _extract_message_text(response.choices[0].message)
        # Empty resp_text propagates honestly — runner-level ITC will
        # classify it as TRANSIENT_FAILURE on round close and adapt.
        wait_responses.append(resp_text)
        turns.append({"role": "user", "content": chunk_prompt})
        turns.append({"role": "assistant", "content": resp_text})
        per_chunk_analyses.append({
            "label": chunk.label or f"chunk_{n}",
            "analysis": resp_text,
            "content": chunk.content,
        })

        _log(f"  [deepseek:{model_id}] section {n} analysis complete "
             f"({len(resp_text):,} chars)")

    # Phase 2: Synthesis from per-chunk analyses
    synthesis_messages: list[dict[str, str]] = []
    if system_prompt:
        synthesis_messages.append({"role": "system", "content": system_prompt})

    analyses_text = _synthesis_analyses_text(per_chunk_analyses)

    synthesis_prompt = (
        f"You have just reviewed {len(chunks)} code sections independently. "
        f"Below are your per-section analyses.\n\n"
        f"{analyses_text}\n\n"
        f"=== SYNTHESIS INSTRUCTION ===\n"
        f"Now combine your findings into a single comprehensive review. "
        f"Include cross-section issues that span multiple files. "
        f"Deduplicate findings that appear in multiple sections. "
        f"Preserve ALL six sections for every finding: FIND, FOLLOW, "
        f"ANALYSE, FIX, FALSIFICATION (FALSIFIER/ATTEMPT/RESULT), and "
        f"CORROBORATION (numerical R_k). For cross-section findings, "
        f"compute a new R_k reflecting the broader context. "
        f"Run a global P-pass across your complete output — look for "
        f"cross-finding contradictions and missed interactions. "
        f"Every finding MUST retain numerical R_k and structured "
        f"FALSIFICATION — do not reduce to qualitative labels.\n\n"
        f"{final_instruction}"
        + (_RUNNABLE_FALSIFIER_OVERRIDE if enable_tools else "")
    )
    synthesis_messages.append({"role": "user", "content": synthesis_prompt})

    _log(f"  [deepseek:{model_id}] delivering synthesis instruction "
         f"(chunk {total}/{total})"
         f"{' [tools-on]' if enable_tools else ''}")

    # DeepSeek text-only synthesis (2026-06-06). DeepSeek-v4-pro's OpenAI
    # tool-translation is broken: it leaks tool calls as DSML markup and, inside
    # the synthesis tool loop, emits exploration code instead of findings (260
    # chars vs 12.8K text-only). The runner re-runs the written FALSIFIER block
    # (the (b) gate), so DeepSeek never needs to execute its own falsifier — so it
    # always synthesises TEXT-ONLY. Gate-on lifts the budget to the reasoning floor
    # (DeepSeek burns ~35K reasoning tokens) and the prompt already carries the
    # runnable-falsifier override; gate-off keeps max_tokens, byte-identical.
    synth_tokens = max(max_tokens, _PHASE1_GATE_TOKENS) if enable_tools else max_tokens
    response = client.chat.completions.create(
        model=model_id,
        messages=synthesis_messages,
        max_tokens=synth_tokens,
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
    if enable_tools and result_text:
        # DeepSeek can leak DSML tool-call markup into content even tool-less;
        # strip it so the runner/scorer receives plain findings (gate-on only,
        # so gate-off stays byte-identical).
        from experiment_11_orchestrator import _DSML_SENTINEL, _strip_dsml_markup
        if _DSML_SENTINEL in result_text:
            result_text = _strip_dsml_markup(result_text).strip()
        # DeepSeek writes prose/ATTEMPT-style falsifiers ignoring the §2 runnable
        # instruction; re-prompt once for the runnable form so its findings can be
        # tool-adjudicated (the runner re-runs the block). No-op if already runnable.
        result_text = _falsifier_format_repair(
            client, model_id, result_text, synth_tokens, timeout)
    elapsed = time.monotonic() - t0

    # 2026-05-20 (founder-directed): synthesis-layer chunk-analyses
    # reconstruction removed (see _decomposed_openrouter comment for
    # rationale). Empty synthesis now propagates honestly so the
    # runner's ITC protocol can classify and adapt as designed.
    if not result_text:
        _log(f"  [deepseek:{model_id}] WARN: synthesis returned 0 chars "
             f"(propagating empty — runner ITC will classify as "
             f"TRANSIENT_FAILURE and adapt next round)")

    turns.append({"role": "user", "content": synthesis_prompt})
    if enable_tools:
        _record_synthesis_tool_turns(turns, synthesis_messages)
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
    enable_tools: bool = False,
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
    ) + final_instruction + (_RUNNABLE_FALSIFIER_OVERRIDE if enable_tools else "")

    cmd_final = [
        cli, "-p",
        "--output-format", "text",
        "--resume", session_id,
    ]
    if enable_tools:
        # GATED: grant the SYNTHESIS turn (only) Bash + Read so the model can
        # run python (via Bash) and import the real target to attach a runnable
        # falsifier — mirroring call_claude_cli's native --allowedTools surface,
        # narrowed to the two tools the falsifier needs. The per-chunk delivery
        # turns above ran tool-less (chunk 0 created the session with Bash/Edit/
        # Write disallowed); only this final --resume invocation carries tools.
        cmd_final.extend(["--allowedTools", "Bash", "Read"])

    _log(f"  [claude-cli] delivering final instruction (chunk {total}/{total})"
         f"{' [tools-on]' if enable_tools else ''}")

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
    enable_tools: bool = False,
) -> DecomposedResult:
    """Decomposed delivery via Codex CLI — per-chunk independent calls.

    enable_tools is accepted for signature consistency but intentionally
    NOT acted on: codex exec runs here with mcp_servers={} and plugins={}
    (tool surface disabled), so the synthesis stays tool-less regardless
    of the flag.

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
    enable_tools: bool = False,
    extra_body: dict | None = None,
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
        enable_tools: GATED, default OFF. When True, the FINAL synthesis turn
            (only) gives the model the execute_python tool so it can run Python
            during synthesis and attach runnable falsifiers — closing the
            (a)-half of the falsifier gate on the decomposed (LARGE-target)
            path. The per-chunk delivery turns ALWAYS stay tool-less so
            decomposition (the Exp 39 quality-collapse fix) is preserved.
            Wired for openrouter, deepseek, claude_cli (the Exp 42 routes);
            threaded into gemini/codex for signature consistency but those two
            stay tool-less (noted at their call sites). Default OFF =>
            byte-identical to the prior decomposed path (no tools kwarg sent).
        extra_body: GATED, default None. OpenAI-compatible extra_body (e.g.
            {"reasoning": {"effort": "high"}}) forwarded to the OpenRouter
            synthesis turn so reasoning models get adequate visible-content
            budget. Previously dropped on the synthesis path. None => no extra
            body sent (byte-identical to prior behaviour).

    Returns:
        DecomposedResult with the synthesis response and conversation history.
    """
    _log(f"  Decomposed dispatch: {api}/{model_id or 'codex'}, "
         f"{len(chunks)} chunks, ~{sum(c.chars for c in chunks):,} chars"
         f"{' [tools-on synthesis]' if enable_tools else ''}")

    if api == "claude_cli":
        # Claude CLI is single-shot like Codex — use per-chunk independent calls
        return _decomposed_claude_cli(
            model_id or "opus", chunks, cdsfl_directives or system_prompt or "",
            final_instruction, timeout, enable_tools=enable_tools,
        )
    elif api == "google":
        # Gemini: param threaded for signature consistency; synthesis stays
        # tool-less (no OpenAI-compatible tool loop wired here).
        return _decomposed_gemini(
            model_id, system_prompt, chunks, final_instruction,
            max_tokens, timeout, enable_tools=enable_tools,
        )
    elif api == "openrouter":
        return _decomposed_openrouter(
            model_id, system_prompt, chunks, final_instruction,
            max_tokens, timeout, enable_tools=enable_tools,
            extra_body=extra_body,
        )
    elif api == "deepseek":
        return _decomposed_deepseek(
            model_id, system_prompt, chunks, final_instruction,
            max_tokens, timeout, enable_tools=enable_tools,
        )
    elif api == "codex_exec":
        # Codex exec: param threaded for signature consistency; synthesis stays
        # tool-less (codex exec runs with mcp_servers/plugins disabled here).
        return _decomposed_codex(
            chunks, cdsfl_directives or system_prompt or "",
            final_instruction, timeout, enable_tools=enable_tools,
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
