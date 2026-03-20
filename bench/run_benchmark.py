#!/usr/bin/env python3
"""
Seeded-fault benchmark harness for CDSFL methodology evaluation.

Runs each task under two conditions:
  - Control:      prompt sent with no system prompt.
  - Experimental: prompt sent with CDSFL directives as system prompt,
                  then iteratively revised across n P-Passes.

Outputs raw results as JSON to stdout (or --output file).
Progress and diagnostics go to stderr.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# CDSFL core directives (Part IV, Section 4.1 of the paper)
# ---------------------------------------------------------------------------

CDSFL_DIRECTIVES = """\
Before producing any output, classify every constraint in the problem as \
HARD (physics, mathematics, law, safety - non-negotiable) or SOFT (economic, \
preference, convenience - negotiable). Ambiguous constraints default to HARD.

For every claim you make:
1. Identify the claim.
2. State the strongest falsifying condition - what observation or argument \
would prove this claim wrong?
3. Attempt to satisfy that condition. Actively try to disprove your own \
conclusion.
4. If the claim survives, mark it as provisionally accepted and state the \
residual uncertainty.
5. If the claim fails, revise or retract it before proceeding.

This is iterative: after revising, re-examine downstream claims that depended \
on the revised one. Continue until you reach genuine diminishing returns - \
not until you feel comfortable, but until further passes produce no new \
failures or revisions.

Mark any claim that depends on present-day market conditions, technology \
availability, or regulatory state as [VERIFY:current]. Mark any untested \
inference as [SPECULATIVE]. Both inline, at point of claim.

Push back on impossible, contradictory, or ill-advised requirements. Say \
"no" or "I don't know" when either is the honest answer. Never fabricate \
certainty.

Default to the simplest sufficient solution. Justified complexity is \
complexity the user cannot do without.\
"""

# Placebo: same length/structure as CDSFL, but generic "be careful" advice.
# No constraint classification, no falsification methodology, no HARD/SOFT.
# This controls for prompt quality vs methodology.
PLACEBO_DIRECTIVES = """\
Before producing any output, read the problem carefully and identify all \
requirements. Make sure you understand what is being asked before you begin \
working on your answer. Take your time and think through each step.

For every part of your answer:
1. Think carefully about whether your reasoning is correct.
2. Consider whether there might be a better approach or an alternative \
way to solve the problem.
3. Check your arithmetic, units, and logical steps for errors.
4. If you find a mistake, fix it before moving on to the next part.
5. Make sure your final answer is consistent with all parts of your work.

Be thorough: after completing your answer, review it from the beginning \
and look for any errors or gaps. Continue reviewing until you are confident \
in your answer and further review would not improve it.

If any part of your answer depends on assumptions, state those assumptions \
clearly. If you are uncertain about any aspect, note your uncertainty and \
explain your reasoning.

If the problem contains contradictory or impossible requirements, point \
them out clearly. Do not guess or make up information. If you do not know \
something, say so.

Aim for a clear, well-organized answer that addresses all parts of the \
problem completely and correctly.\
"""

INITIAL_PASS_TEMPLATE = """This is P-Pass {n} of {total}. Perform the full CDSFL loop on the task below.

Original task:
{task_prompt}

Instructions:
- Produce the strongest answer you can to the original task.
- Then attack that answer adversarially for errors, contradictions, physical impossibilities, logical flaws, legal or safety issues, and HARD or SOFT misclassification.
- Revise the answer to fix every issue you can justify fixing.
- Surface uncertainty honestly.
- Do not hide issues merely because you managed to revise them.

Return exactly these sections:
INITIAL_ANSWER:
...

ISSUES_FOUND:
- ...

REVISED_ANSWER:
...
"""

ADVERSARIAL_PASS_TEMPLATE = """You are an independent reviewer. This output was produced by another system \
and has not been independently verified. It may contain:

- Errors at interfaces between subsystems
- Unstated assumptions that conflict across components
- Constraint violations visible only at system level
- Conclusions that are internally consistent but physically or logically wrong

Your task is to find what is wrong, not to confirm what is right.

Original task:
{task_prompt}

Output to review:
{current_draft}

Instructions:
- Examine the complete output as an integrated system.
- Focus on cross-module interactions, shared assumptions, and emergent contradictions.
- Stop when all hard-constraint assumptions are sound and remaining findings represent \
genuinely diminishing returns. The threshold: would this finding, if missed, cause a \
real-world failure, violation, or unsafe condition? If not, it is below threshold.

Return exactly these sections:
ISSUES_FOUND:
- ...

REVISED_ANSWER:
...
"""

FOLLOWUP_PASS_TEMPLATE = """This is P-Pass {n} of {total}. Continue the CDSFL loop by attacking and revising the current draft.

Original task:
{task_prompt}

Current draft from the previous pass:
{current_draft}

Issues identified on the previous pass:
{prior_issues}

Instructions:
- Start from the current draft, not from scratch.
- Try to break the current draft harder than before.
- Look for newly introduced downstream problems caused by earlier fixes.
- Identify every additional issue you find.
- Revise the draft to fix what survives scrutiny.
- Preserve any parts that still survive attack.

Return exactly these sections:
ISSUES_FOUND:
- ...

REVISED_ANSWER:
...
"""

def _call_with_retry(call_fn, *args, max_retries: int = 10, base_delay: float = 8.0, **kwargs) -> str:
    """Wrap an API call with exponential backoff retry for transient errors.

    Fix 3 (CX remediation): fatal errors (insufficient_quota, auth, invalid_request)
    are raised immediately without retry.
    """
    # Fatal patterns — never retry these
    _FATAL_PATTERNS = [
        "insufficient_quota", "invalid_api_key", "authentication",
        "permission", "invalid_request_error", "model_not_found",
        "billing_not_active", "account_deactivated",
    ]
    # Transient patterns — retry with backoff
    _TRANSIENT_PATTERNS = [
        "429", "rate_limit", "ResourceExhausted",
        "504", "DeadlineExceeded", "503", "overloaded",
        "529", "InternalServerError",
        "timeout", "Timeout", "connection",
        "GEMINI_FAILURE", "gemini_failure",
    ]
    for attempt in range(max_retries + 1):
        try:
            return call_fn(*args, **kwargs)
        except Exception as exc:
            exc_str = str(exc).lower()
            # Check fatal first — never retry
            is_fatal = any(p in exc_str for p in _FATAL_PATTERNS)
            if is_fatal:
                _err(f"  [FATAL] non-recoverable error: {str(exc)[:120]}")
                raise
            # Check transient — retry with backoff
            is_transient = any(p.lower() in exc_str for p in _TRANSIENT_PATTERNS)
            if is_transient and attempt < max_retries:
                delay = min(base_delay * (2 ** attempt), 300)
                _err(f"  [retry] transient error: {str(exc)[:80]}...")
                _err(f"  [retry] waiting {delay:.0f}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            raise


TASKS_DIR = Path(__file__).parent / "tasks"
REQUIRED_TASK_FIELDS = {"id", "domain", "prompt", "seeded_faults", "ground_truth_notes"}
REQUIRED_FAULT_FIELDS = {"id", "type", "description", "location_hint"}


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------


def _err(msg: str) -> None:
    """Print to stderr."""
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# Task loading
# ---------------------------------------------------------------------------


def load_tasks(tasks_dir: Path) -> list[dict[str, Any]]:
    """Recursively load all .json task files from tasks_dir."""
    tasks: list[dict[str, Any]] = []
    if not tasks_dir.is_dir():
        _err(f"Tasks directory not found: {tasks_dir}")
        return tasks

    for json_path in sorted(tasks_dir.rglob("*.json")):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                task = json.load(f)
            task["_source_file"] = str(json_path.relative_to(tasks_dir))
            tasks.append(task)
        except (json.JSONDecodeError, OSError) as exc:
            _err(f"WARNING: skipping {json_path}: {exc}")
    return tasks



def validate_task(task: dict[str, Any]) -> list[str]:
    """Return a list of validation errors (empty = valid)."""
    errors = []
    source = task.get("_source_file", "<unknown>")

    missing = REQUIRED_TASK_FIELDS - task.keys()
    if missing:
        errors.append(f"{source}: missing top-level fields: {missing}")

    faults = task.get("seeded_faults", [])
    if not isinstance(faults, list):
        errors.append(f"{source}: seeded_faults must be an array")
    else:
        for i, fault in enumerate(faults):
            if not isinstance(fault, dict):
                errors.append(f"{source}: seeded_faults[{i}] is not an object")
                continue
            fault_missing = REQUIRED_FAULT_FIELDS - fault.keys()
            if fault_missing:
                errors.append(
                    f"{source}: seeded_faults[{i}] missing fields: {fault_missing}"
                )
    return errors


# ---------------------------------------------------------------------------
# API callers
# ---------------------------------------------------------------------------


def call_anthropic(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a single request via the Anthropic SDK."""
    try:
        import anthropic
    except ImportError:
        _err("ERROR: `anthropic` package not installed. pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(timeout=180.0)  # 3-min timeout
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)
    return response.content[0].text



def call_openai(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a single request via the OpenAI SDK."""
    try:
        import openai
    except ImportError:
        _err("ERROR: `openai` package not installed. pip install openai")
        sys.exit(1)

    client = openai.OpenAI()
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=4096,
        messages=messages,
    )
    return response.choices[0].message.content or ""


def call_openai_reasoning(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a request via OpenAI SDK for reasoning models (o3-mini, o4-mini).

    Reasoning models use max_completion_tokens instead of max_tokens,
    and use developer messages instead of system messages.
    """
    try:
        import openai
    except ImportError:
        _err("ERROR: `openai` package not installed. pip install openai")
        sys.exit(1)

    client = openai.OpenAI()
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "developer", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=16000,
        messages=messages,
    )
    return response.choices[0].message.content or ""


def call_anthropic_thinking(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a request via Anthropic SDK with extended thinking enabled."""
    try:
        import anthropic
    except ImportError:
        _err("ERROR: `anthropic` package not installed. pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(timeout=300.0)  # 5-min timeout for thinking
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": 16000,
        "thinking": {"type": "enabled", "budget_tokens": 10000},
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)
    # Extract text blocks only (skip thinking blocks)
    text_parts = [b.text for b in response.content if b.type == "text"]
    return "\n".join(text_parts)


def _truncate_prompt_for_gemini(system_prompt: str | None, user_prompt: str) -> tuple[str | None, str]:
    """Progressively reduce prompt size for Gemini when it can't cope.

    Strategy: trim the system prompt first (it's the directives — large but
    less task-specific), then trim the user prompt's prior-pass chain (keeping
    the original task and the most recent pass). Returns the trimmed pair.
    """
    # Step 1: halve system prompt if it's over 4k chars
    if system_prompt and len(system_prompt) > 4000:
        # Keep first 2000 (core directives) + last 1000 (closing instructions)
        system_prompt = (
            system_prompt[:2000]
            + "\n\n[...directive content trimmed for context limits...]\n\n"
            + system_prompt[-1000:]
        )
        _err(f"  [gemini-adapt] trimmed system prompt to {len(system_prompt)} chars")

    # Step 2: if user prompt is very long (multi-pass chain), keep task + latest pass
    if len(user_prompt) > 12000:
        # Try to find pass boundaries and keep first + last
        parts = user_prompt.split("---")
        if len(parts) >= 3:
            # Keep first part (original task) and last part (most recent pass)
            user_prompt = (
                parts[0]
                + "\n---\n[...intermediate passes trimmed for context limits...]\n---\n"
                + parts[-1]
            )
            _err(f"  [gemini-adapt] trimmed user prompt to {len(user_prompt)} chars")

    return system_prompt, user_prompt


def call_gemini(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a request via the Google GenAI SDK (google-genai).

    Adapts to GEMINI_FAILURE / infrastructure errors by progressively
    truncating prompts and retrying, per Google's own troubleshooting
    guidance (simplify the prompt when the model can't process it).
    """
    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError:
        _err("ERROR: `google-genai` package not installed. pip install google-genai")
        sys.exit(1)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        _err("ERROR: GOOGLE_API_KEY not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Throttle handled externally by AdaptiveThrottle — do not double-sleep here

    # Attempt with full prompt first, then adapt if Gemini can't cope
    current_system = system_prompt
    current_user = user_prompt
    max_adapt_attempts = 3

    for adapt_attempt in range(max_adapt_attempts):
        try:
            config = genai_types.GenerateContentConfig(
                max_output_tokens=4096,
                system_instruction=current_system if current_system else None,
                http_options=genai_types.HttpOptions(timeout=300_000),  # 5 min
            )
            response = client.models.generate_content(
                model=model,
                contents=current_user,
                config=config,
            )
            # Check for refusal (safety filter, recitation, etc.)
            if response.text is not None:
                if adapt_attempt > 0:
                    _err(f"  [gemini-adapt] succeeded after {adapt_attempt} adaptation(s)")
                return response.text
            reason = "unknown"
            if response.candidates:
                reason = str(response.candidates[0].finish_reason)
            return f"[MODEL_REFUSED: finish_reason={reason}] Model declined to respond to this prompt."

        except Exception as exc:
            exc_str = str(exc)
            exc_lower = exc_str.lower()
            # Identify Gemini infrastructure / prompt-too-large failures
            is_gemini_infra = any(p in exc_lower for p in [
                "gemini_failure", "internal", "500",
                "resource_exhausted", "invalid_argument",
                "request payload size exceeds", "token",
            ])
            if is_gemini_infra and adapt_attempt < max_adapt_attempts - 1:
                _err(f"  [gemini-adapt] infrastructure error: {exc_str[:100]}")
                _err(f"  [gemini-adapt] adapting prompt (attempt {adapt_attempt + 1}/{max_adapt_attempts - 1})")
                current_system, current_user = _truncate_prompt_for_gemini(
                    current_system, current_user,
                )
                time.sleep(5)  # brief pause before retry
                continue
            # Not adaptable or final attempt — re-raise for _call_with_retry
            raise


def call_groq(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a request via Groq (OpenAI-compatible endpoint)."""
    try:
        import openai
    except ImportError:
        _err("ERROR: `openai` package not installed. pip install openai")
        sys.exit(1)

    token = os.environ.get("GROQ_API_KEY")
    if not token:
        _err("ERROR: GROQ_API_KEY not set.")
        sys.exit(1)

    client = openai.OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=token,
    )
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=messages,
    )
    return response.choices[0].message.content or ""


def call_github_models(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a request via GitHub Models (OpenAI-compatible endpoint)."""
    try:
        import openai
    except ImportError:
        _err("ERROR: `openai` package not installed. pip install openai")
        sys.exit(1)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        _err("ERROR: GITHUB_TOKEN not set.")
        sys.exit(1)

    client = openai.OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=token,
    )
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=messages,
    )
    return response.choices[0].message.content or ""


def call_codex(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Run a benchmark task via codex exec (Codex Business subscription).

    Uses the default gpt-5.3-codex model. The --skip-git-repo-check flag
    avoids requiring a git repo. Output captured via -o tempfile.
    """
    import subprocess as _sp
    import tempfile

    # Combine system + user prompt (codex exec takes a single prompt)
    full_prompt = ""
    if system_prompt:
        full_prompt += f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
    full_prompt += f"TASK:\n{user_prompt}"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="codex_bench_"
    ) as f:
        output_path = f.name

    try:
        result = _sp.run(
            [
                "codex", "exec",
                "--skip-git-repo-check",
                "-o", output_path,
                "-",
            ],
            input=full_prompt,
            capture_output=True, text=True, timeout=600,
        )
        # Fix 2 (CX finding 5): check returncode
        if result.returncode != 0:
            Path(output_path).unlink(missing_ok=True)
            raise RuntimeError(
                f"codex exec failed (exit code {result.returncode}): "
                f"{result.stderr[:200] if result.stderr else '(no stderr)'}"
            )
        output_file = Path(output_path)
        if output_file.exists():
            response = output_file.read_text().strip()
            output_file.unlink()
            if response:
                return response
        # Fallback to stdout if output file is empty
        stdout = result.stdout.strip()
        if not stdout:
            raise RuntimeError("codex exec returned empty output")
        return stdout
    except _sp.TimeoutExpired:
        Path(output_path).unlink(missing_ok=True)
        raise RuntimeError("codex exec timed out after 600s")
    except FileNotFoundError:
        Path(output_path).unlink(missing_ok=True)  # EPP M1 fix 10: clean up temp file
        raise RuntimeError("codex CLI not found — install via: npm i -g @openai/codex")
    except OSError:
        Path(output_path).unlink(missing_ok=True)  # EPP M1 fix 10: clean up temp file
        raise


PROVIDERS = {
    "anthropic": call_anthropic,
    "anthropic-thinking": call_anthropic_thinking,
    "openai": call_openai,
    "openai-reasoning": call_openai_reasoning,
    "gemini": call_gemini,
    "groq": call_groq,
    "github": call_github_models,
    "codex": call_codex,
}


# ---------------------------------------------------------------------------
# Experimental prompt construction
# ---------------------------------------------------------------------------


SECTION_LABELS = ("INITIAL_ANSWER", "ISSUES_FOUND", "REVISED_ANSWER")


def _extract_section(text: str, label: str) -> str | None:
    """Extract a labelled section from a model response.

    Case-insensitive matching (Gemini R2 fix 6): LLMs frequently vary case
    (e.g. "Revised Answer:" vs "REVISED_ANSWER:"). Also uses word-boundary
    anchoring to avoid truncating answers that mention label names in prose
    (Gemini R4 fix 2: recursive label truncation).
    """
    # Build stop pattern with case-insensitive label variants
    stop_labels = []
    for item in SECTION_LABELS:
        if item != label:
            # Match both UPPER_SNAKE and Title Case variants
            escaped = re.escape(item)
            # Also match space-separated title case: "REVISED_ANSWER" -> "Revised Answer"
            title_variant = re.escape(item.replace("_", " ").title())
            stop_labels.append(escaped)
            if title_variant != escaped:
                stop_labels.append(title_variant)

    if stop_labels:
        # Require stop labels to be at start of line (not embedded in prose).
        # EPP M1 fix 1: removed (?:\n|$) after colon — models often put content
        # on the same line as the label (e.g. "REVISED_ANSWER: The answer is...").
        # Old pattern only stopped when label was followed by empty line or EOF,
        # causing section leakage.
        stop_pattern = rf"(?=\n(?:{'|'.join(stop_labels)}):\s*|\Z)"
    else:
        stop_pattern = r"\Z"

    # Match the label itself case-insensitively, with optional underscore/space
    label_pattern = re.escape(label).replace(r"\_", r"[_ ]")
    pattern = rf"(?:^|\n){label_pattern}:\s*\n?(.*?){stop_pattern}"
    match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None



def _safe_format(template: str, **kwargs: str) -> str:
    """Format a template without crashing on curly braces in values.

    Gemini R3 fix 3: Python's str.format() raises KeyError/ValueError if
    task prompts or model-generated drafts contain literal {} (e.g. math
    notation like "Given the set {x, y}..."). This uses $-style substitution.
    """
    import string
    # Convert {name} placeholders to $name for safe substitution
    safe_template = template.replace("{", "${")
    return string.Template(safe_template).safe_substitute(**kwargs)


def _build_pass_prompt(
    task_prompt: str,
    pass_number: int,
    total_passes: int,
    current_draft: str | None,
    prior_issues: str | None,
) -> str:
    """Build the user prompt for the current experimental pass."""
    if current_draft is None:
        return _safe_format(
            INITIAL_PASS_TEMPLATE,
            n=str(pass_number),
            total=str(total_passes),
            task_prompt=task_prompt,
        )

    return _safe_format(
        FOLLOWUP_PASS_TEMPLATE,
        n=str(pass_number),
        total=str(total_passes),
        task_prompt=task_prompt,
        current_draft=current_draft.strip(),
        prior_issues=(prior_issues or "- No explicit issues listed on the prior pass."),
    )


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------


def run_control(
    task: dict[str, Any],
    model: str,
    provider: str,
) -> dict[str, Any]:
    """Run the control condition: bare prompt, no system instructions."""
    call = PROVIDERS[provider]
    _err(f"  [control] calling {provider}/{model} ...")
    t0 = time.monotonic()
    response = _call_with_retry(call, model, None, task["prompt"])
    elapsed = time.monotonic() - t0
    _err(f"  [control] done ({elapsed:.1f}s)")
    return {
        "condition": "control",
        "model": model,
        "provider": provider,
        "response": response,
        "elapsed_seconds": round(elapsed, 2),
    }



def run_experimental(
    task: dict[str, Any],
    model: str,
    provider: str,
    directives: str,
    num_passes: int,
) -> dict[str, Any]:
    """Run the experimental condition: CDSFL directives + iterative P-Passes."""
    call = PROVIDERS[provider]
    passes: list[dict[str, Any]] = []
    current_draft: str | None = None
    prior_issues: str | None = None

    for i in range(1, num_passes + 1):
        user_prompt = _build_pass_prompt(
            task_prompt=task["prompt"],
            pass_number=i,
            total_passes=num_passes,
            current_draft=current_draft,
            prior_issues=prior_issues,
        )

        _err(f"  [experimental] P-Pass {i}/{num_passes}, calling {provider}/{model} ...")
        t0 = time.monotonic()
        response = _call_with_retry(call, model, directives, user_prompt)
        elapsed = time.monotonic() - t0
        _err(f"  [experimental] P-Pass {i}/{num_passes} done ({elapsed:.1f}s)")

        extracted_issues = _extract_section(response, "ISSUES_FOUND")
        extracted_revision = _extract_section(response, "REVISED_ANSWER")
        extracted_initial = _extract_section(response, "INITIAL_ANSWER")

        # EPP M1 fix 7: include severity_counts for consistency with run_adaptive
        trivial, moderate, severe = classify_issue_severity(extracted_issues or "")

        pass_record: dict[str, Any] = {
            "pass_number": i,
            "response": response,
            "elapsed_seconds": round(elapsed, 2),
            "severity_counts": {"trivial": trivial, "moderate": moderate, "severe": severe},
        }
        if extracted_initial is not None:
            pass_record["initial_answer"] = extracted_initial
        if extracted_issues is not None:
            pass_record["issues_found"] = extracted_issues
        if extracted_revision is not None:
            pass_record["revised_answer"] = extracted_revision

        passes.append(pass_record)

        # Gemini R1 fix 3 / R2 fix 6: avoid draft pollution.
        # If extraction failed, keep the previous draft rather than using the
        # raw response (which contains metadata, labels, and issues that would
        # contaminate the next pass's "draft" field).
        if extracted_revision is not None:
            current_draft = extracted_revision
        elif current_draft is None:
            # First pass with no extracted revision — use initial answer or raw
            current_draft = extracted_initial or response
        # else: keep previous current_draft unchanged
        prior_issues = extracted_issues

    return {
        "condition": "experimental",
        "model": model,
        "provider": provider,
        "num_passes": num_passes,
        "passes": passes,
        "final_response": current_draft or "",
    }



def run_extended(
    task: dict[str, Any],
    model: str,
    provider: str,
    directives: str,
    num_passes: int,
) -> dict[str, Any]:
    """Run the final-pass-isolation condition.

    Passes 1 to (num_passes - 1) run as standard iterative P-Passes in one
    context chain.  The final pass runs in an isolated context containing only
    the original task and the current draft — no prior P-Pass conclusions.

    NOTE: This is NOT the full Extended P-Pass protocol from CLAUDE.md, which
    specifies 4 module-scoped passes + 1 isolated adversarial pass. This mode
    tests final-pass context isolation only — module-aware decomposition would
    require per-task module maps that the current task schema does not provide.
    """
    call = PROVIDERS[provider]
    passes: list[dict[str, Any]] = []
    current_draft: str | None = None
    prior_issues: str | None = None

    # Modular passes (1 through n-1)
    modular_count = max(num_passes - 1, 1)
    for i in range(1, modular_count + 1):
        user_prompt = _build_pass_prompt(
            task_prompt=task["prompt"],
            pass_number=i,
            total_passes=num_passes,
            current_draft=current_draft,
            prior_issues=prior_issues,
        )

        _err(f"  [extended] iterative P-Pass {i}/{num_passes}, calling {provider}/{model} ...")
        t0 = time.monotonic()
        response = _call_with_retry(call, model, directives, user_prompt)
        elapsed = time.monotonic() - t0
        _err(f"  [extended] iterative P-Pass {i}/{num_passes} done ({elapsed:.1f}s)")

        extracted_issues = _extract_section(response, "ISSUES_FOUND")
        extracted_revision = _extract_section(response, "REVISED_ANSWER")
        extracted_initial = _extract_section(response, "INITIAL_ANSWER")

        # EPP M1 fix 7: include severity_counts for consistency with run_adaptive
        trivial, moderate, severe = classify_issue_severity(extracted_issues or "")

        pass_record: dict[str, Any] = {
            "pass_number": i,
            "pass_type": "iterative",
            "response": response,
            "elapsed_seconds": round(elapsed, 2),
            "severity_counts": {"trivial": trivial, "moderate": moderate, "severe": severe},
        }
        if extracted_initial is not None:
            pass_record["initial_answer"] = extracted_initial
        if extracted_issues is not None:
            pass_record["issues_found"] = extracted_issues
        if extracted_revision is not None:
            pass_record["revised_answer"] = extracted_revision

        passes.append(pass_record)
        # Gemini R1 fix 3: avoid draft pollution (same logic as run_experimental)
        if extracted_revision is not None:
            current_draft = extracted_revision
        elif current_draft is None:
            current_draft = extracted_initial or response
        prior_issues = extracted_issues

    # Isolated adversarial pass (final pass — fresh context, no prior P-Pass data)
    # NOTE (Gemini R3 fix 1): This pass omits issue history, which introduces a
    # "history deletion" confound — any performance delta conflates isolation
    # benefit with distraction removal. Interpret Extended vs Standard comparison
    # with this caveat. See CE_Gemini_Review_Round3_2026-03-18.txt.
    adversarial_prompt = _safe_format(
        ADVERSARIAL_PASS_TEMPLATE,
        task_prompt=task["prompt"],
        current_draft=(current_draft or "").strip(),
    )

    _err(f"  [extended] adversarial P-Pass {num_passes}/{num_passes}, calling {provider}/{model} (isolated context) ...")
    t0 = time.monotonic()
    # No system prompt for the adversarial pass — it operates without CDSFL
    # directives to avoid anchoring on the methodology that produced the draft.
    response = _call_with_retry(call, model, None, adversarial_prompt)
    elapsed = time.monotonic() - t0
    _err(f"  [extended] adversarial P-Pass {num_passes}/{num_passes} done ({elapsed:.1f}s)")

    extracted_issues = _extract_section(response, "ISSUES_FOUND")
    extracted_revision = _extract_section(response, "REVISED_ANSWER")
    # EPP M1 fix 7: severity_counts for adversarial pass too
    trivial, moderate, severe = classify_issue_severity(extracted_issues or "")

    pass_record = {
        "pass_number": num_passes,
        "pass_type": "adversarial_isolated",
        "response": response,
        "elapsed_seconds": round(elapsed, 2),
        "severity_counts": {"trivial": trivial, "moderate": moderate, "severe": severe},
    }
    if extracted_issues is not None:
        pass_record["issues_found"] = extracted_issues
    if extracted_revision is not None:
        pass_record["revised_answer"] = extracted_revision

    passes.append(pass_record)
    # Gemini R1 fix 3: prefer extracted revision, fall back to previous draft
    final_draft = extracted_revision if extracted_revision is not None else (current_draft or "")

    return {
        "condition": "extended",
        "model": model,
        "provider": provider,
        "num_passes": num_passes,
        "iterative_passes": modular_count,
        "adversarial_passes": 1,
        "passes": passes,
        "final_response": final_draft,
    }


# ---------------------------------------------------------------------------
# Phase 2 additions: adaptive throttle, placebo, cross-model, termination
# ---------------------------------------------------------------------------


class AdaptiveThrottle:
    """Per-provider adaptive rate limiter.

    Starts at *initial_delay*.  On a 429, doubles the delay (up to *max_delay*).
    After *success_streak* consecutive successes, halves the delay (down to
    *min_delay*).
    """

    def __init__(
        self,
        initial_delay: float = 4.0,
        min_delay: float = 0.5,
        max_delay: float = 30.0,
        success_streak: int = 5,
    ):
        self.delay = initial_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.success_streak = success_streak
        self._consecutive_ok = 0

    def wait(self) -> None:
        if self.delay > 0:
            time.sleep(self.delay)

    def record_success(self) -> None:
        self._consecutive_ok += 1
        if self._consecutive_ok >= self.success_streak:
            self.delay = max(self.delay / 2, self.min_delay)
            self._consecutive_ok = 0

    def record_rate_limit(self) -> None:
        self._consecutive_ok = 0
        self.delay = min(self.delay * 2, self.max_delay)


# Provider-specific default throttle settings
PROVIDER_THROTTLES: dict[str, dict[str, float]] = {
    "anthropic": {"initial": 2.0, "min": 1.0, "max": 30.0},
    "anthropic-thinking": {"initial": 4.0, "min": 2.0, "max": 60.0},
    "openai": {"initial": 2.0, "min": 1.0, "max": 30.0},
    "openai-reasoning": {"initial": 3.0, "min": 1.0, "max": 30.0},
    "gemini": {"initial": 8.0, "min": 4.0, "max": 60.0},
    "groq": {"initial": 0.5, "min": 0.2, "max": 10.0},
    "github": {"initial": 2.0, "min": 1.0, "max": 15.0},
}


def make_throttle(provider: str) -> AdaptiveThrottle:
    """Create an AdaptiveThrottle with provider-appropriate defaults."""
    cfg = PROVIDER_THROTTLES.get(provider, {"initial": 2.0, "min": 0.5, "max": 15.0})
    return AdaptiveThrottle(
        initial_delay=cfg["initial"],
        min_delay=cfg["min"],
        max_delay=cfg["max"],
    )


def _call_throttled(
    call_fn,
    model: str,
    system_prompt: str | None,
    user_prompt: str,
    throttle: AdaptiveThrottle | None = None,
) -> str:
    """Call an API function with adaptive throttle + retry."""
    if throttle:
        throttle.wait()
    try:
        result = _call_with_retry(call_fn, model, system_prompt, user_prompt)
        if throttle:
            throttle.record_success()
        return result
    except Exception:
        if throttle:
            throttle.record_rate_limit()
        raise


def classify_issue_severity(issues_text: str) -> tuple[int, int, int]:
    """Classify issues from a P-pass into severity counts.

    Returns (trivial, moderate, severe) counts.
    Heuristic: lines with keywords like 'error', 'wrong', 'incorrect',
    'impossible', 'violates', 'fails', 'invalid' → severe.
    Lines with 'missing', 'incomplete', 'unclear', 'should' → moderate.
    Everything else → trivial.
    """
    if not issues_text:
        return (0, 0, 0)

    severe_kw = {"error", "wrong", "incorrect", "impossible", "violates",
                 "fails", "failed", "invalid", "fatal", "contradicts",
                 "physically", "broken", "crash", "undefined", "infinite",
                 "diverge", "diverges", "unsound", "bogus", "fabricat"}
    moderate_kw = {"missing", "incomplete", "unclear", "should", "could",
                   "might", "gap", "omits", "assumes", "oversight",
                   "lacks", "lacking", "inadequate", "insufficient",
                   "unverified", "unproven", "hand-wave", "handwave",
                   "not", "no", "without", "doesn't", "does not"}

    trivial = moderate = severe = 0
    for line in issues_text.split("\n"):
        line_lower = line.strip().lower()
        if not line_lower:
            continue
        # Accept lines starting with -, *, numbered lists, or bold markers
        # EPP M1 fix 5: strip leading whitespace before checking markers
        # (LLMs frequently indent list items)
        line_stripped = line_lower.lstrip()
        if not any(line_stripped.startswith(p) for p in ("-", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9", "•", "**")):
            continue
        words = set(line_lower.split())
        if words & severe_kw:
            severe += 1
        elif words & moderate_kw:
            moderate += 1
        else:
            trivial += 1

    return (trivial, moderate, severe)


# ---------------------------------------------------------------------------
# CE Confer mechanism — CC + CX assess diminishing returns via IM
# ---------------------------------------------------------------------------

# Path to the IM service (Project Genesis coordination channel)
_IM_SERVICE = Path.home() / "Developer_Projects" / "Project_Genesis" / "cw_handoff" / "im_service.py"

# Confer prompts — CX gets task context but NOT the overarching hypothesis
_CC_CONFER_PROMPT = """\
You are assessing iterative P-pass output for a methodology benchmark.

Task: {task_id} ({category})
Model under test: {model}
Passes completed: {num_passes}

Below are the issues found in each pass. Your job: determine whether the \
passes have reached genuine diminishing returns — i.e., later passes are \
NOT finding novel, substantive issues that earlier passes missed.

Criteria for CONTINUE:
- Later passes found genuinely new issues (not rephrasing of earlier ones)
- Issues found are substantive (would affect correctness, not just style)
- There is reason to believe another pass would find something new

Criteria for STOP:
- Later passes are rehashing earlier findings in different words
- New findings are trivial (formatting, style, minor preferences)
- The output has converged — further passes would not change the substance

{pass_summaries}

Respond with exactly one line:
VERDICT: CONTINUE or VERDICT: STOP
Then a brief (2-3 sentence) justification.
"""

_CX_CONFER_PROMPT = """\
You are independently assessing P-pass output for a benchmark experiment.

Task: {task_id} ({category})
Model under test: {model}
Passes completed: {num_passes}

Below are the issues found in each pass. Your job: determine whether the \
passes have reached genuine diminishing returns — i.e., later passes are \
NOT finding novel, substantive issues that earlier passes missed.

Criteria for CONTINUE:
- Later passes found genuinely new issues (not rephrasing of earlier ones)
- Issues found are substantive (would affect correctness, not just style)
- There is reason to believe another pass would find something new

Criteria for STOP:
- Later passes are rehashing earlier findings in different words
- New findings are trivial (formatting, style, minor preferences)
- The output has converged — further passes would not change the substance

{pass_summaries}

Respond with exactly one line:
VERDICT: CONTINUE or VERDICT: STOP
Then a brief (2-3 sentence) justification.
"""


def _format_pass_summaries(passes: list[dict[str, Any]]) -> str:
    """Format pass data for confer prompts."""
    lines = []
    for p in passes:
        pn = p["pass_number"]
        sev = p.get("severity_counts", {})
        issues = p.get("issues_found", "(no structured issues extracted)")
        # Truncate long issue text to keep confer prompts focused
        if isinstance(issues, str) and len(issues) > 800:
            issues = issues[:800] + "\n[...truncated...]"
        lines.append(
            f"--- Pass {pn} ---\n"
            f"Severity: trivial={sev.get('trivial',0)}, "
            f"moderate={sev.get('moderate',0)}, "
            f"severe={sev.get('severe',0)}\n"
            f"Issues:\n{issues}\n"
        )
    return "\n".join(lines)


def confer_diminishing_returns(
    task: dict[str, Any],
    model: str,
    passes: list[dict[str, Any]],
    project_dir: str | None = None,
) -> tuple[bool, str, dict[str, bool]]:
    """Invoke CC CLI + CX CLI via IM to confer on diminishing returns.

    Returns (should_stop, confer_log, cli_failures) where:
      - should_stop: True if CC+CX consensus is STOP
      - confer_log: full transcript of the CC/CX exchange
      - cli_failures: dict with 'cc_failed' and 'cx_failed' booleans

    INFRA_FAIL on either assessor defaults to CONTINUE (never consensus).

    NOTE (P5 adversarial finding 4): These CLI calls consume tokens via the
    CC/CX subscriptions but are NOT metered through the CostLedger. They are
    infrastructure costs separate from the experiment's API budget. With
    confer_after=3 and max_passes=5, up to 6 CLI calls per task-config pair
    (2 per confer invocation × 3 invocations). Budget impact is negligible
    relative to frontier model calls but should be accounted for in total
    experiment cost reporting.
    """
    import subprocess as sp

    task_id = task.get("id", "unknown")
    category = task.get("category", "unknown")
    pass_summaries = _format_pass_summaries(passes)

    proj_dir = project_dir or str(
        Path.home() / "Developer_Projects" / "Constraint_Engineering"
    )
    genesis_dir = str(Path.home() / "Developer_Projects" / "Project_Genesis")

    confer_log_parts: list[str] = []

    # --- Step 1: CC assessment via claude CLI ---
    cc_prompt = _safe_format(
        _CC_CONFER_PROMPT,
        task_id=task_id,
        category=category,
        model=model,
        num_passes=str(len(passes)),
        pass_summaries=pass_summaries,
    )

    _err(f"  [confer] invoking CC CLI for diminishing-returns assessment ...")
    cc_verdict = "INFRA_FAIL"  # Fix 2: explicit infra-failure, not silent default
    cc_response = ""
    cc_failed = False
    try:
        cc_result = sp.run(
            ["claude", "-p", "--no-session-persistence", "--tools", "", cc_prompt],
            capture_output=True, text=True, timeout=120, cwd=proj_dir,
        )
        # Fix 2: check returncode
        if cc_result.returncode != 0:
            _err(f"  [confer] CC CLI exited with code {cc_result.returncode}")
            cc_failed = True
            confer_log_parts.append(
                f"CC CLI failed (exit code {cc_result.returncode}): "
                f"{cc_result.stderr[:200] if cc_result.stderr else '(no stderr)'}"
            )
        else:
            cc_response = cc_result.stdout.strip()
            confer_log_parts.append(f"CC assessment:\n{cc_response}")

            # Fix 2: strict verdict parsing — must contain exact pattern
            cc_upper = cc_response.upper()
            if "VERDICT: STOP" in cc_upper and "VERDICT: CONTINUE" not in cc_upper:
                cc_verdict = "STOP"
            elif "VERDICT: CONTINUE" in cc_upper and "VERDICT: STOP" not in cc_upper:
                cc_verdict = "CONTINUE"
            else:
                # Ambiguous or missing verdict — infra failure
                _err(f"  [confer] CC verdict ambiguous or missing — marking INFRA_FAIL")
                cc_verdict = "INFRA_FAIL"
                cc_failed = True

            if not cc_failed:
                _err(f"  [confer] CC verdict: {cc_verdict}")
    except (sp.TimeoutExpired, FileNotFoundError, OSError) as e:
        _err(f"  [confer] CC CLI failed ({e}), marking INFRA_FAIL")
        confer_log_parts.append(f"CC CLI failed: {e}")
        cc_verdict = "INFRA_FAIL"
        cc_failed = True

    # --- Step 2: Post CC verdict to IM ---
    cc_im_msg = (
        f"CE confer: task {task_id}, model {model}, "
        f"after {len(passes)} passes. "
        f"Verdict: {cc_verdict}. "
        f"{cc_response[:200] if cc_response else '(CLI fallback)'}"
    )
    try:
        sp.run(
            ["python3", str(_IM_SERVICE), "post", "cc", cc_im_msg],
            capture_output=True, timeout=10, cwd=genesis_dir,
        )
    except (sp.TimeoutExpired, OSError) as e:
        _err(f"  [confer] IM post failed ({e}), continuing with CC-only verdict")

    # --- Step 3: CX assessment via codex exec ---
    cx_prompt = _safe_format(
        _CX_CONFER_PROMPT,
        task_id=task_id,
        category=category,
        model=model,
        num_passes=str(len(passes)),
        pass_summaries=pass_summaries,
    )

    _err(f"  [confer] invoking CX CLI for counter-assessment ...")
    cx_verdict = "INFRA_FAIL"  # Fix 2: explicit infra-failure
    cx_response = ""
    cx_failed = False
    cx_output_file = Path("/tmp") / f"cx_confer_{task_id}_{int(time.time())}.txt"
    try:
        cx_result = sp.run(
            [
                "codex", "exec",
                "--skip-git-repo-check",
                "-o", str(cx_output_file),
                "-",
            ],
            input=cx_prompt,
            capture_output=True, text=True, timeout=180,
        )
        # Fix 2: check returncode
        if cx_result.returncode != 0:
            _err(f"  [confer] CX CLI exited with code {cx_result.returncode}")
            cx_failed = True
            confer_log_parts.append(
                f"CX CLI failed (exit code {cx_result.returncode}): "
                f"{cx_result.stderr[:200] if cx_result.stderr else '(no stderr)'}"
            )
        else:
            if cx_output_file.exists():
                cx_response = cx_output_file.read_text().strip()
            else:
                cx_response = cx_result.stdout.strip()
            confer_log_parts.append(f"CX assessment:\n{cx_response}")

            # EPP M3 fix 2: CX now gives independent STOP/CONTINUE verdict
            # (was AGREE/DISAGREE — anchored CX to CC's opinion)
            cx_upper = cx_response.upper()
            if "VERDICT: STOP" in cx_upper and "VERDICT: CONTINUE" not in cx_upper:
                cx_verdict = "STOP"
            elif "VERDICT: CONTINUE" in cx_upper and "VERDICT: STOP" not in cx_upper:
                cx_verdict = "CONTINUE"
            else:
                _err(f"  [confer] CX verdict ambiguous or missing — marking INFRA_FAIL")
                cx_verdict = "INFRA_FAIL"
                cx_failed = True

            if not cx_failed:
                _err(f"  [confer] CX verdict: {cx_verdict}")
    except (sp.TimeoutExpired, FileNotFoundError, OSError) as e:
        _err(f"  [confer] CX CLI failed ({e}), marking INFRA_FAIL")
        confer_log_parts.append(f"CX CLI failed: {e}")
        cx_verdict = "INFRA_FAIL"
        cx_failed = True

    # --- Step 4: Post CX verdict to IM ---
    cx_im_msg = (
        f"CE confer: task {task_id}, model {model}. "
        f"CX verdict: {cx_verdict}. "
        f"{cx_response[:200] if cx_response else '(CLI fallback)'}"
    )
    try:
        sp.run(
            ["python3", str(_IM_SERVICE), "post", "cx", cx_im_msg],
            capture_output=True, timeout=10, cwd=genesis_dir,
        )
    except (sp.TimeoutExpired, OSError):
        pass

    # Clean up temp file
    if cx_output_file.exists():
        cx_output_file.unlink()

    # --- Step 5: Determine outcome ---
    # Fix 2: INFRA_FAIL is a distinct outcome — never interpreted as consensus.
    # Consensus STOP = both CC and CX explicitly agree to stop.
    # Any disagreement, CONTINUE, or INFRA_FAIL = run next pass (conservative).
    # No machine-only extension beyond max_passes — that's a human decision.
    confer_log = "\n---\n".join(confer_log_parts)
    cli_failures = {"cc_failed": cc_failed, "cx_failed": cx_failed}

    # If either assessor hit infra failure, mark it and default CONTINUE
    if cc_verdict == "INFRA_FAIL" or cx_verdict == "INFRA_FAIL":
        infra_note = []
        if cc_verdict == "INFRA_FAIL":
            infra_note.append("CC")
        if cx_verdict == "INFRA_FAIL":
            infra_note.append("CX")
        _err(f"  [confer] INFRA_FAIL ({'+'.join(infra_note)}) — defaulting to CONTINUE")
        return (False, confer_log, cli_failures)

    # EPP M3 fix 2: Both assessors now give independent STOP/CONTINUE verdicts.
    # Consensus STOP requires BOTH to say STOP. Any disagreement → CONTINUE (conservative).
    if cc_verdict == "STOP" and cx_verdict == "STOP":
        _err(f"  [confer] CONSENSUS: both CC and CX say STOP — diminishing returns reached")
        return (True, confer_log, cli_failures)
    elif cc_verdict == "CONTINUE" and cx_verdict == "CONTINUE":
        _err(f"  [confer] CONSENSUS: both CC and CX say CONTINUE — running next pass")
        return (False, confer_log, cli_failures)
    elif cc_verdict == "STOP" and cx_verdict == "CONTINUE":
        _err(f"  [confer] SPLIT: CC says STOP, CX says CONTINUE — running next pass (conservative)")
        return (False, confer_log, cli_failures)
    else:
        # CC says CONTINUE, CX says STOP
        _err(f"  [confer] SPLIT: CC says CONTINUE, CX says STOP — running next pass (conservative)")
        return (False, confer_log, cli_failures)


def run_adaptive(
    task: dict[str, Any],
    model: str,
    provider: str,
    directives: str,
    max_passes: int = 5,
    throttle: AdaptiveThrottle | None = None,
    confer_after: int = 3,
    cost_check_fn=None,
) -> dict[str, Any]:
    """Run CE with intelligent termination via CC+CX confer.

    Up to *max_passes* passes (hard cap, no machine-only extension).
    After *confer_after* passes (default 3), invokes CC CLI + CX CLI
    via IM to confer on whether genuine diminishing returns have been
    reached. Re-confers after each subsequent pass.

    Termination statuses:
      RESOLVED — CC+CX consensus that diminishing returns reached (pass 3-5)
      DEFERRED — pass 5 hard cap reached without consensus to stop.
                 Full transcript preserved for human review (Tier 2).
    """
    call = PROVIDERS[provider]
    passes: list[dict[str, Any]] = []
    current_draft: str | None = None
    prior_issues: str | None = None
    status = "DEFERRED"  # default: if we exhaust all passes without consensus
    confer_logs: list[str] = []
    total_cc_failures = 0
    total_cx_failures = 0
    total_confer_calls = 0
    last_confer_outcome = ""

    for i in range(1, max_passes + 1):
        user_prompt = _build_pass_prompt(
            task_prompt=task["prompt"],
            pass_number=i,
            total_passes=max_passes,
            current_draft=current_draft,
            prior_issues=prior_issues,
        )

        _err(f"  [adaptive] P-Pass {i}/{max_passes}, calling {provider}/{model} ...")
        t0 = time.monotonic()
        response = _call_throttled(call, model, directives, user_prompt, throttle)
        elapsed = time.monotonic() - t0
        _err(f"  [adaptive] P-Pass {i}/{max_passes} done ({elapsed:.1f}s)")

        extracted_issues = _extract_section(response, "ISSUES_FOUND")
        extracted_revision = _extract_section(response, "REVISED_ANSWER")
        extracted_initial = _extract_section(response, "INITIAL_ANSWER")

        trivial, moderate, severe = classify_issue_severity(extracted_issues or "")

        pass_record: dict[str, Any] = {
            "pass_number": i,
            "response": response,
            "elapsed_seconds": round(elapsed, 2),
            "severity_counts": {"trivial": trivial, "moderate": moderate, "severe": severe},
        }
        if extracted_initial is not None:
            pass_record["initial_answer"] = extracted_initial
        if extracted_issues is not None:
            pass_record["issues_found"] = extracted_issues
        if extracted_revision is not None:
            pass_record["revised_answer"] = extracted_revision

        passes.append(pass_record)
        # Gemini R1 fix 3: avoid draft pollution
        if extracted_revision is not None:
            current_draft = extracted_revision
        elif current_draft is None:
            current_draft = extracted_initial or response
        prior_issues = extracted_issues

        # Gemini R4 fix 3: check cost cap between passes (if callback provided)
        if cost_check_fn and not cost_check_fn():
            _err(f"  [adaptive] cost cap reached after pass {i} — stopping early")
            status = "COST_CAP"
            last_confer_outcome = f"cost cap hit after pass {i}"
            break

        # After confer_after passes, invoke CC+CX confer for termination
        if i >= confer_after:
            _err(f"  [adaptive] pass {i} complete — invoking CC+CX confer ...")
            total_confer_calls += 1
            should_stop, confer_log, cli_failures = confer_diminishing_returns(
                task, model, passes,
            )
            if cli_failures.get("cc_failed"):
                total_cc_failures += 1
            if cli_failures.get("cx_failed"):
                total_cx_failures += 1
            confer_logs.append(f"After pass {i}:\n{confer_log}")

            if should_stop:
                status = "RESOLVED"
                last_confer_outcome = f"consensus STOP at pass {i}"
                _err(f"  [adaptive] RESOLVED: CC+CX consensus at pass {i}")
                break
            else:
                last_confer_outcome = f"no consensus at pass {i} — continuing"
                if i < max_passes:
                    _err(f"  [adaptive] CC+CX: continue to pass {i+1}")
                else:
                    # Hard cap reached — distinguish infra failure from genuine disagreement
                    # CX R2 fix 5: ANY confer call with infra failure on either side → DEFERRED_INFRA
                    if total_confer_calls > 0 and (total_cc_failures + total_cx_failures) > 0:
                        # At least one confer call had an infra failure
                        status = "DEFERRED_INFRA"
                        last_confer_outcome = (
                            f"pass {i} hard cap — DEFERRED_INFRA "
                            f"({total_cc_failures} CC + {total_cx_failures} CX failures "
                            f"across {total_confer_calls} confer calls)"
                        )
                        _err(f"  [adaptive] DEFERRED_INFRA: hard cap at pass {i}, "
                             f"{total_cc_failures + total_cx_failures} infra failures across "
                             f"{total_confer_calls} confer calls")
                    else:
                        status = "DEFERRED"
                        last_confer_outcome = f"pass {i} hard cap — DEFERRED for human review"
                        _err(f"  [adaptive] DEFERRED: hard cap at pass {i}, no consensus — marked for human review")

    result = {
        "condition": "experimental_adaptive",
        "model": model,
        "provider": provider,
        "max_passes": max_passes,
        "actual_passes": len(passes),
        "status": status,
        "last_confer_outcome": last_confer_outcome,
        "confer_stats": {
            "total_confer_calls": total_confer_calls,
            "cc_cli_failures": total_cc_failures,
            "cx_cli_failures": total_cx_failures,
        },
        "confer_logs": confer_logs,
        "passes": passes,
        "final_response": current_draft or "",
    }

    return result


def run_placebo(
    task: dict[str, Any],
    model: str,
    provider: str,
    max_passes: int = 5,
    throttle: AdaptiveThrottle | None = None,
    cost_check_fn=None,
) -> dict[str, Any]:
    """Run placebo condition: generic 'be careful' instructions, same pass count."""
    return run_adaptive(
        task, model, provider,
        directives=PLACEBO_DIRECTIVES,
        max_passes=max_passes,
        throttle=throttle,
        cost_check_fn=cost_check_fn,
    )


def run_cross_model(
    task: dict[str, Any],
    model_a: str,
    provider_a: str,
    model_b: str,
    provider_b: str,
    directives: str,
    max_passes: int = 5,
    throttle_a: AdaptiveThrottle | None = None,
    throttle_b: AdaptiveThrottle | None = None,
    cost_check_fn=None,
) -> dict[str, Any]:
    """Schema C: cross-model adversarial.

    Pass 1: Model A generates solution (with CDSFL directives)
    Pass 2: Model B falsifies Model A's output
    Pass 3: Model A responds to Model B's findings
    Pass 4: Model B re-checks
    Pass 5: Isolated adversarial (Model B, fresh context, no CDSFL)
    """
    call_a = PROVIDERS[provider_a]
    call_b = PROVIDERS[provider_b]
    passes: list[dict[str, Any]] = []
    current_draft: str | None = None
    prior_issues: str | None = None

    pass_sequence = [
        ("A", model_a, provider_a, call_a, throttle_a, True),   # pass 1: generate
        ("B", model_b, provider_b, call_b, throttle_b, True),   # pass 2: falsify
        ("A", model_a, provider_a, call_a, throttle_a, True),   # pass 3: respond
        ("B", model_b, provider_b, call_b, throttle_b, True),   # pass 4: re-check
    ]

    for i, (role, model, provider, call, throttle, use_directives) in enumerate(pass_sequence, 1):
        if i > max_passes:
            break

        user_prompt = _build_pass_prompt(
            task_prompt=task["prompt"],
            pass_number=i,
            total_passes=max_passes,
            current_draft=current_draft,
            prior_issues=prior_issues,
        )

        sys_prompt = directives if use_directives else None
        _err(f"  [cross-model] P-Pass {i}/{max_passes} (Model {role}: {provider}/{model}) ...")
        t0 = time.monotonic()
        response = _call_throttled(call, model, sys_prompt, user_prompt, throttle)
        elapsed = time.monotonic() - t0
        _err(f"  [cross-model] P-Pass {i}/{max_passes} done ({elapsed:.1f}s)")

        extracted_issues = _extract_section(response, "ISSUES_FOUND")
        extracted_revision = _extract_section(response, "REVISED_ANSWER")
        extracted_initial = _extract_section(response, "INITIAL_ANSWER")

        trivial, moderate, severe = classify_issue_severity(extracted_issues or "")

        pass_record: dict[str, Any] = {
            "pass_number": i,
            "model_role": role,
            "model": model,
            "provider": provider,
            "response": response,
            "elapsed_seconds": round(elapsed, 2),
            "severity_counts": {"trivial": trivial, "moderate": moderate, "severe": severe},
        }
        if extracted_initial is not None:
            pass_record["initial_answer"] = extracted_initial
        if extracted_issues is not None:
            pass_record["issues_found"] = extracted_issues
        if extracted_revision is not None:
            pass_record["revised_answer"] = extracted_revision

        passes.append(pass_record)
        # Gemini R1 fix 3: avoid draft pollution
        if extracted_revision is not None:
            current_draft = extracted_revision
        elif current_draft is None:
            current_draft = extracted_initial or response
        prior_issues = extracted_issues

        # EPP M4 fix 2: check cost cap between cross-model passes
        if cost_check_fn and not cost_check_fn():
            _err(f"  [cross-model] cost cap reached after pass {i} — stopping early")
            break

    # Final pass: isolated adversarial (Model B, fresh context, no directives)
    # EPP M4 fix 2: also check cost cap before adversarial pass
    if len(passes) < max_passes and (not cost_check_fn or cost_check_fn()):
        adversarial_prompt = _safe_format(
            ADVERSARIAL_PASS_TEMPLATE,
            task_prompt=task["prompt"],
            current_draft=(current_draft or "").strip(),
        )
        _err(f"  [cross-model] adversarial P-Pass {max_passes}/{max_passes} (Model B: {provider_b}/{model_b}, isolated) ...")
        t0 = time.monotonic()
        response = _call_throttled(call_b, model_b, None, adversarial_prompt, throttle_b)
        elapsed = time.monotonic() - t0
        _err(f"  [cross-model] adversarial P-Pass {max_passes}/{max_passes} done ({elapsed:.1f}s)")

        extracted_issues = _extract_section(response, "ISSUES_FOUND")
        extracted_revision = _extract_section(response, "REVISED_ANSWER")
        trivial, moderate, severe = classify_issue_severity(extracted_issues or "")

        passes.append({
            "pass_number": max_passes,
            "model_role": "B_adversarial",
            "model": model_b,
            "provider": provider_b,
            "pass_type": "adversarial_isolated",
            "response": response,
            "elapsed_seconds": round(elapsed, 2),
            "severity_counts": {"trivial": trivial, "moderate": moderate, "severe": severe},
            **({"issues_found": extracted_issues} if extracted_issues else {}),
            **({"revised_answer": extracted_revision} if extracted_revision else {}),
        })
        current_draft = extracted_revision or current_draft

    return {
        "condition": "cross_model",
        "model_a": model_a,
        "provider_a": provider_a,
        "model_b": model_b,
        "provider_b": provider_b,
        "max_passes": max_passes,
        "actual_passes": len(passes),
        "passes": passes,
        "final_response": current_draft or "",
    }


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

# Approximate pricing per 1M tokens (input/output) in USD
PROVIDER_PRICING: dict[str, dict[str, float]] = {
    "anthropic": {"input": 3.0, "output": 15.0},
    "anthropic-thinking": {"input": 3.0, "output": 15.0},
    "openai": {"input": 5.0, "output": 15.0},       # GPT-5.4
    "openai-reasoning": {"input": 2.5, "output": 10.0},  # o4-mini
    "gemini": {"input": 2.0, "output": 12.0},        # Gemini 3.1 Pro
    "groq": {"input": 0.05, "output": 0.08},         # Llama 4 Scout
    "github": {"input": 0.0, "output": 0.0},
    "codex": {"input": 0.0, "output": 0.0},          # Codex Business subscription
}


def estimate_call_cost(
    provider: str,
    prompt_chars: int,
    response_chars: int,
) -> float:
    """Rough cost estimate for a single API call, in USD.

    Uses ~4 chars per token as a rough approximation.
    """
    pricing = PROVIDER_PRICING.get(provider, {"input": 5.0, "output": 15.0})
    input_tokens = prompt_chars / 4
    output_tokens = response_chars / 4
    cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    return cost


def run_benchmark(
    tasks: list[dict[str, Any]],
    model: str,
    provider: str,
    directives: str,
    num_passes: int,
    mode: str = "standard",
    domain_directives_dir: Path | None = None,
    condition: str = "universal-only",
    variant: str | None = None,
) -> list[dict[str, Any]]:
    """Run all tasks under both conditions."""
    results = []
    total = len(tasks)

    for idx, task in enumerate(tasks, 1):
        task_id = task.get("id", "<no-id>")
        domain = task.get("domain", "<no-domain>")
        _err(f"\n[{idx}/{total}] Task {task_id} (domain: {domain})")

        # Compose directives for this task's domain
        domain_specific = None
        if domain_directives_dir and condition != "universal-only":
            domain_specific = load_domain_directives(
                domain_directives_dir, domain, variant
            )
            if domain_specific:
                _err(f"  [directives] loaded domain-specific directives for {domain}")
            else:
                _err(f"  [directives] no domain-specific directives found for {domain}")

        task_directives = compose_directives(directives, domain_specific, condition)

        if mode == "extended":
            experimental_result = run_extended(
                task, model, provider, task_directives, num_passes
            )
        elif mode == "adaptive":
            experimental_result = run_adaptive(
                task, model, provider, task_directives, num_passes
            )
        elif mode == "placebo":
            experimental_result = run_placebo(
                task, model, provider, num_passes
            )
        else:
            experimental_result = run_experimental(
                task, model, provider, task_directives, num_passes
            )

        task_result: dict[str, Any] = {
            "task_id": task_id,
            "domain": domain,
            "prompt": task["prompt"],
            "source_file": task.get("_source_file", ""),
            "seeded_faults": task.get("seeded_faults", []),
            "ground_truth_notes": task.get("ground_truth_notes", ""),
            "control": run_control(task, model, provider),
            "experimental": experimental_result,
        }
        results.append(task_result)

    return results



def load_directives(path: str | None) -> str:
    """Load directives from a file, or return the built-in constant."""
    if path is None:
        return CDSFL_DIRECTIVES
    p = Path(path)
    if not p.is_file():
        _err(f"ERROR: directives file not found: {path}")
        sys.exit(1)
    return p.read_text(encoding="utf-8").strip()


def load_domain_directives(
    directives_dir: Path, domain: str, variant: str | None = None
) -> str | None:
    """Load domain-specific directives for a given domain.

    If *variant* is given, load that specific file (e.g. 'building' loads
    structural_building.txt from the domain folder).  Otherwise, load the
    first available .txt file alphabetically.

    Returns None if no matching file exists.
    """
    domain_dir = directives_dir / domain
    if not domain_dir.is_dir():
        return None

    if variant:
        # Try exact match first, then prefix match
        for txt_file in sorted(domain_dir.glob("*.txt")):
            stem = txt_file.stem  # e.g. "structural_building"
            if variant == stem or stem.endswith(f"_{variant}"):
                return txt_file.read_text(encoding="utf-8").strip()
        return None

    # Default: first available .txt file
    txt_files = sorted(domain_dir.glob("*.txt"))
    if txt_files:
        return txt_files[0].read_text(encoding="utf-8").strip()
    return None


def compose_directives(
    universal: str,
    domain_specific: str | None,
    condition: str,
) -> str:
    """Compose the system prompt from universal and domain-specific directives.

    Conditions:
      - universal-only:  universal directives only (default)
      - universal+domain: universal + domain-specific layered
      - domain-only:     domain-specific only (for ablation studies)
    """
    if condition == "domain-only":
        return domain_specific or universal  # fall back if no domain file
    if condition == "universal+domain" and domain_specific:
        return universal + "\n\n" + domain_specific
    return universal  # universal-only or no domain file available



def main() -> None:
    parser = argparse.ArgumentParser(
        description="CDSFL seeded-fault benchmark harness.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-20250514",
        help="Model identifier (default: claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "anthropic-thinking", "openai", "openai-reasoning", "gemini", "groq", "github", "codex"],
        default="anthropic",
        help="API provider: anthropic, anthropic-thinking (extended thinking), "
             "openai, openai-reasoning (o3/o4-mini), gemini, groq, github, "
             "codex (Codex Business subscription). Default: anthropic",
    )
    parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Number of P-Passes for experimental condition (default: 3)",
    )
    parser.add_argument(
        "--directives",
        type=str,
        default=None,
        help="Path to a text file containing CDSFL directives (default: built-in constant)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write JSON results to this file instead of stdout",
    )
    parser.add_argument(
        "--tasks-dir",
        type=str,
        default=None,
        help="Path to tasks directory (default: bench/tasks/)",
    )
    parser.add_argument(
        "--mode",
        choices=["standard", "extended", "adaptive", "placebo", "cross_model"],
        default="standard",
        help="P-Pass mode: 'standard' (all passes in same context), "
             "'extended' (iterative + final-pass isolation), "
             "'adaptive' (CC+CX confer termination), "
             "'placebo' (generic instructions baseline), "
             "'cross_model' (Schema C adversarial). Default: standard",
    )
    parser.add_argument(
        "--domain-directives",
        type=str,
        default=None,
        help="Path to domain directives directory (e.g. bench/directives/). "
             "Each subdirectory contains domain-specific directive files.",
    )
    parser.add_argument(
        "--condition",
        choices=["universal-only", "universal+domain", "domain-only"],
        default="universal-only",
        help="Directive condition: 'universal-only' (default), "
             "'universal+domain' (layers domain-specific on top of universal), "
             "or 'domain-only' (domain-specific only, for ablation studies).",
    )
    parser.add_argument(
        "--variant",
        type=str,
        default=None,
        help="Select a specific variant within each domain (e.g. 'building' "
             "selects structural_building.txt). If omitted, uses the first "
             "available variant alphabetically.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and validate tasks only - no API calls",
    )

    args = parser.parse_args()

    # Gemini R4 fix 9: extended mode requires >= 2 passes (1 iterative + 1 adversarial)
    if args.mode == "extended" and args.passes < 2:
        _err("ERROR: extended mode requires at least 2 passes (1 iterative + 1 adversarial)")
        sys.exit(1)

    tasks_dir = Path(args.tasks_dir) if args.tasks_dir else TASKS_DIR

    _err(f"Loading tasks from {tasks_dir} ...")
    tasks = load_tasks(tasks_dir)

    if not tasks:
        _err("No task files found. Nothing to do.")
        sys.exit(0)

    _err(f"Loaded {len(tasks)} task(s).")

    all_errors = []
    for task in tasks:
        all_errors.extend(validate_task(task))

    if all_errors:
        _err("Validation errors:")
        for err in all_errors:
            _err(f"  - {err}")
        sys.exit(1)

    _err("All tasks valid.")

    domain_directives_dir = Path(args.domain_directives) if args.domain_directives else None

    if args.dry_run:
        domains: dict[str, int] = {}
        for task in tasks:
            domain = task.get("domain", "<unknown>")
            domains[domain] = domains.get(domain, 0) + 1
        fault_count = sum(len(t.get("seeded_faults", [])) for t in tasks)

        _err("\nDry run summary:")
        _err(f"  Tasks:     {len(tasks)}")
        _err(f"  Faults:    {fault_count}")
        _err(f"  Mode:      {args.mode}")
        _err(f"  Condition: {args.condition}")
        if domain_directives_dir:
            _err(f"  Domain directives: {domain_directives_dir}")
            for domain_name in sorted(domains.keys()):
                dd = load_domain_directives(
                    domain_directives_dir, domain_name, args.variant
                )
                status = f"loaded ({len(dd)} chars)" if dd else "not found"
                _err(f"    {domain_name}: {status}")
        if args.variant:
            _err(f"  Variant:   {args.variant}")
        for domain_name, count in sorted(domains.items()):
            _err(f"  {domain_name}: {count} task(s)")
        sys.exit(0)

    directives = load_directives(args.directives)

    env_requirements = {
        "anthropic": "ANTHROPIC_API_KEY",
        "anthropic-thinking": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "openai-reasoning": "OPENAI_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "github": "GITHUB_TOKEN",
        # codex: no env key needed (Codex Business subscription)
    }
    required_key = env_requirements.get(args.provider)
    if required_key and not os.environ.get(required_key):
        _err(f"ERROR: {required_key} not set in environment.")
        sys.exit(1)

    _err(
        f"\nRunning benchmark: model={args.model}, provider={args.provider}, "
        f"passes={args.passes}, mode={args.mode}, condition={args.condition}"
    )
    results = run_benchmark(
        tasks, args.model, args.provider, directives, args.passes, args.mode,
        domain_directives_dir=domain_directives_dir,
        condition=args.condition,
        variant=args.variant,
    )

    meta: dict[str, Any] = {
        "schema_version": "cdsfl-bench-v2",
        "model": args.model,
        "provider": args.provider,
        "num_passes": args.passes,
        "mode": args.mode,
        "directive_condition": args.condition,
        "task_count": len(tasks),
        "directives_source": args.directives or "built-in",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "domains": sorted({task.get("domain", "<unknown>") for task in tasks}),
    }
    if args.domain_directives:
        meta["domain_directives_source"] = args.domain_directives
    if args.variant:
        meta["variant"] = args.variant

    benchmark_output = {
        "benchmark_meta": meta,
        "results": results,
    }
    output_json = json.dumps(benchmark_output, indent=2)

    if args.output:
        Path(args.output).write_text(output_json + "\n", encoding="utf-8")
        _err(f"\nResults written to {args.output}")
    else:
        print(output_json)

    _err("\nDone.")


if __name__ == "__main__":
    main()
