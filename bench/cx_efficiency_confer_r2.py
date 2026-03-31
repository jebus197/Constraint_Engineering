#!/usr/bin/env python3
"""CX Efficiency Confer Round 2: 4-model CDSFL review of Codex dispatch costs.

Dispatches to CC2, ChatGPT, Gemini, DeepSeek with a standard confer packet
describing the CX efficiency problem, what's been fixed, and what remains.
Iterates until convergence or diminishing returns.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from experiment_11_orchestrator import (
    call_openrouter, call_gemini, call_deepseek, _log,
)

CDSFL_PATH = Path(__file__).parent / "cdsfl_registry" / "universal.toml"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8") if CDSFL_PATH.exists() else ""

OUTPUT_DIR = Path(__file__).parent / "logs" / "cx_efficiency_confer_r2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# The confer packet — 6-field standard format
CONFER_PROMPT = """
=== REVIEW TARGET ===
Codex CLI (CX) dispatch efficiency in the CDSFL multi-model experiment harness.
CX has exhausted its OpenAI usage quota in ~3 hours of experiment runtime.
The other 4 models (CC2/Claude Opus, ChatGPT/gpt-5.4, Gemini 3.1 Pro, DeepSeek Reasoner)
have not exhausted their respective quotas. Your task: identify further efficiency
improvements to reduce CX's token/compute burn rate without degrading finding quality.

=== CODE EXTRACTS ===

--- Extract 1: How CX is dispatched (experiment_11_orchestrator.py) ---

def call_codex(
    user_prompt: str,
    cdsfl_directives: str,
    timeout: int = 600,
    max_retries: int = 1,
    use_output_schema: bool = False,
) -> str:
    # Codex exec has no --system-prompt flag. CDSFL goes in the prompt body
    # as elevated directives (lesson #12).
    full_prompt = (
        "=== SYSTEM INSTRUCTIONS (CDSFL Operating Constraints) ===\\n"
        "The following constraints govern your output. Treat them as non-negotiable "
        "operating requirements, equivalent to a system prompt.\\n\\n"
        f"{cdsfl_directives}\\n\\n"
        "=== END SYSTEM INSTRUCTIONS ===\\n\\n"
        "=== TASK ===\\n"
        f"{user_prompt}\\n"
        "=== END TASK ==="
    )
    cmd = ["codex", "exec"]
    if use_output_schema:
        schema_path = Path(__file__).parent / "cdsfl_finding_schema.json"
        if schema_path.exists():
            cmd.extend(["--output-schema", str(schema_path)])
    cmd.append("-")  # read prompt from stdin
    result = subprocess.run(cmd, input=full_prompt, capture_output=True, text=True, timeout=timeout)

--- Extract 2: How other models are dispatched (same file) ---

def call_openrouter(model_id, system_prompt, user_prompt, max_tokens=32768, ...):
    # Bare API call. CDSFL as system message, task as user message.
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    response = client.chat.completions.create(
        model=model_id, messages=messages, max_tokens=max_tokens, temperature=0.0)

--- Extract 3: Sub-area decomposition for context-limited models ---

SUBAREA_ESCALATION_CHARS = 80_000  # prompt chars above which we decompose

def _build_subarea_prompt(preamble, full_code, math_text, task_key, mc_label, round_idx):
    # Rotates through TASK_SUBAREAS by round index
    subareas = TASK_SUBAREAS.get(task_key, REVIEW_AREAS)
    area_idx = round_idx % len(subareas)
    area_name, markers = subareas[area_idx]
    # Extracts focused code section + skeletal context
    focused = _extract_code_area(full_code, markers, area_name)
    # Adds verified_facts, explicit_unknowns, adversarial_brief
    model_prompt = f"You are reviewing the {area_name} sub-area...\\n" + ...
    return model_prompt, True

--- Extract 4: Feasibility gate ---

def _estimate_throughput(mc_label):
    # Median-of-3 chars/second from recent dispatches
    ...
def _effective_capacity(mc_label):
    # Returns estimated max input chars based on throughput * timeout
    ...
# Before every dispatch:
if prompt_chars > effective_capacity:
    escalate to sub-area rotation

--- Extract 5: Model configuration ---

ModelConfig("Codex", "gpt-5.4", api="codex_exec", timeout=600, max_retries=1)
ModelConfig("ChatGPT", "openai/gpt-5.4", api="openrouter", timeout=300, max_retries=3)
# Note: same base model (gpt-5.4), different routing. CX gets manufacturer system
# prompt (hidden) + tool-use layer + sandbox. ChatGPT gets bare API.

=== INTERACTION SURFACE ===
CX interacts with the experiment via:
1. stdin pipe: full prompt (CDSFL pseudo-system + task) piped to `codex exec -`
2. stdout: findings text returned
3. Process lifecycle: subprocess.run with 600s timeout
4. The Codex CLI itself runs with: reasoning effort "xhigh", sandbox "read-only",
   approval "never". These are CLI-level settings we cannot change per-dispatch.
5. The CLI has its own manufacturer system prompt that we cannot see or override.
   CDSFL directives are injected as user-message pseudo-system instructions.

=== VERIFIED FACTS ===
1. CX exhausted its OpenAI usage quota in ~3 hours of experiment runtime (Exp 17).
2. Before the confer packet fix, CX burned 155,454 tokens on 78 tool calls
   investigating the codebase instead of producing findings. Fix: embed code in
   prompt (standard confer packet). Result: 78% token reduction (155K→33K).
3. After the fix, CX still takes ~480s per dispatch vs ChatGPT ~35s (same model).
4. CX produces fewer but more focused findings than bare ChatGPT.
5. CX is the only model that times out (600s watchdog) and crashes.
6. Sub-area decomposition already reduces CX's input from ~180K to ~14-42K chars.
7. The feasibility gate already blocks prompts that exceed estimated capacity.
8. CX's reasoning effort is locked at "xhigh" by the CLI — we cannot reduce it.
9. The Codex CLI `codex exec` is a subprocess call — no streaming, no early-stop.
10. CX's unique finding (dispatch_watchdog key mismatch) was qualitatively distinct
    from anything the other 4 models found — it has genuine biodiversity value.
11. CX and ChatGPT use the same base model (gpt-5.4). The behavioural differences
    come entirely from the CLI wrapper (manufacturer system prompt, tool layer,
    reasoning effort, sandbox constraints).

=== EXPLICIT UNKNOWNS ===
1. We cannot see or modify the Codex CLI's manufacturer system prompt.
2. We do not know how much of CX's token burn is from the reasoning effort "xhigh"
   setting vs the tool-use layer vs the hidden system prompt.
3. We do not know whether `codex exec` supports any flags to reduce compute
   (e.g. lower reasoning effort, disable tool use, limit output tokens).
4. We do not know the exact token pricing for codex exec vs the OpenAI API.
5. We do not know whether switching CX to direct OpenAI API (bypassing the CLI)
   would preserve or destroy the behavioural differences that give it biodiversity value.
6. The CDSFL directives are ~2,400 chars. They are repeated in every CX prompt
   as user-message text (not system message). This is overhead that other models
   avoid by using the system message role.

=== ADVERSARIAL BRIEF ===
The real inefficiency may be outside the code shown. Before validating the
proposed review boundary, test for: (a) whether the CLI itself is the wrong
tool — should we bypass it entirely for API calls while preserving the
behavioural differences? (b) whether the prompt structure is fundamentally
wrong for CX's architecture, (c) whether there are Codex CLI flags or
configuration options we haven't explored, (d) whether the experiment design
itself is inefficient in how it uses CX (e.g. dispatching CX on tasks where
it adds no value over bare ChatGPT), (e) whether CX's biodiversity value
can be replicated more cheaply by other means.
=== END ADVERSARIAL BRIEF ===

Produce structured findings. For each finding, state:
- Finding ID (e.g. CXE-001)
- Type: NOVEL (new insight) | VALIDATION (confirms known issue) | CHALLENGE (disputes prior fix)
- Severity: CRITICAL | HIGH | MEDIUM | LOW
- Description: what the issue is
- Proposed fix: specific, implementable change
- Falsification: how could this fix fail or make things worse?
"""

MODELS = [
    ("CC2", "anthropic/claude-opus-4-6", "openrouter"),
    ("ChatGPT", "openai/gpt-5.4", "openrouter"),
    ("Gemini", "gemini-3.1-pro-preview", "google"),
    ("DeepSeek", "deepseek-reasoner", "deepseek"),
]


def dispatch(label, model_id, api, prompt, round_idx):
    """Dispatch to a model and save results."""
    _log(f"  Dispatching to {label} ({model_id}) via {api}...")
    t0 = time.monotonic()
    try:
        if api == "openrouter":
            text = call_openrouter(model_id, CDSFL_TEXT, prompt, max_tokens=32768, timeout=300)
        elif api == "google":
            text = call_gemini(model_id, CDSFL_TEXT, prompt, max_tokens=32768, timeout=300)
        elif api == "deepseek":
            text = call_deepseek(model_id, CDSFL_TEXT, prompt, max_tokens=16384, timeout=900)
        else:
            raise ValueError(f"Unknown API: {api}")
        elapsed = time.monotonic() - t0
        _log(f"  {label}: {len(text)} chars, {elapsed:.1f}s")

        # Save
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        outfile = OUTPUT_DIR / f"round{round_idx}_{label.lower()}_{ts}.json"
        outfile.write_text(json.dumps({
            "model": label,
            "model_id": model_id,
            "api": api,
            "round": round_idx,
            "chars": len(text),
            "elapsed_s": round(elapsed, 1),
            "response": text,
        }, indent=2), encoding="utf-8")
        _log(f"  Saved: {outfile}")
        return text, elapsed
    except Exception as e:
        elapsed = time.monotonic() - t0
        _log(f"  {label}: ERROR — {e} ({elapsed:.1f}s)")
        return f"ERROR: {e}", elapsed


def run_confer(max_rounds=3):
    """Run confer rounds until convergence or max_rounds."""
    all_findings = {}

    for round_idx in range(max_rounds):
        _log(f"\n=== CONFER ROUND {round_idx} ===\n")

        if round_idx == 0:
            prompt = CONFER_PROMPT
        else:
            # Build confer prompt with prior findings
            prior = "\n\n".join(
                f"--- {label} (Round {round_idx - 1}) ---\n{text[:3000]}"
                for label, (text, _) in all_findings.get(round_idx - 1, {}).items()
            )
            prompt = (
                f"=== CONFER ROUND {round_idx} ===\n"
                f"Previous findings from all models:\n\n{prior}\n\n"
                f"Original problem:\n{CONFER_PROMPT}\n\n"
                f"Your task: review all prior findings. Produce ONLY:\n"
                f"1. NOVEL findings not yet raised\n"
                f"2. CHALLENGES to prior findings you believe are wrong\n"
                f"3. VALIDATIONS of prior findings with additional evidence\n"
                f"Do NOT repeat findings already raised unless you have new evidence.\n"
                f"If you believe convergence has been reached, state so explicitly.\n"
            )

        round_results = {}
        for label, model_id, api in MODELS:
            text, elapsed = dispatch(label, model_id, api, prompt, round_idx)
            round_results[label] = (text, elapsed)

        all_findings[round_idx] = round_results

        # Check for convergence signals
        convergence_signals = sum(
            1 for label, (text, _) in round_results.items()
            if "convergence" in text.lower() and ("reached" in text.lower() or "achieved" in text.lower())
        )
        _log(f"\nRound {round_idx}: {convergence_signals}/4 models signal convergence")

        if round_idx > 0 and convergence_signals >= 2:
            _log(f"Convergence reached at round {round_idx}.")
            break

    _log(f"\nConfer complete. {len(all_findings)} rounds, results in {OUTPUT_DIR}")


if __name__ == "__main__":
    _log("CX Efficiency Confer Round 2 — 4 models under CDSFL")
    _log(f"Output: {OUTPUT_DIR}")
    run_confer(max_rounds=3)
