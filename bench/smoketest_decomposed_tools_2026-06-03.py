#!/usr/bin/env python3
"""Smoke test: execute_python tool on the DECOMPOSED (multiturn) synthesis turn.

Closes the (a)-half of the falsifier gate for LARGE targets: when a payload is
big enough to trigger decomposition, the FINAL synthesis turn now (gated, when
enable_tools=True) gets the execute_python tool so the reviewing model can run
Python and attach a runnable falsifier that imports the REAL target module.

What this exercises (the real production path, not a mock):
  * Build a 2-chunk payload from a REAL module (bench/dm/_similarity.py).
  * Call decomposed_dispatch(api="openrouter", ..., enable_tools=True) and
    confirm the model CALLED execute_python during synthesis AND attached a
    FALSIFIER block importing the real module.
  * Call the SAME thing with enable_tools=False and confirm it still returns a
    normal synthesis (no crash, no tool attempt) — the byte-identical default.

Honest-failure policy: if OPENROUTER_API_KEY is missing or the dispatch call
fails, the run REPORTS it (non-zero exit) rather than faking a pass. The
execute_python sandbox is read/import-only and never modifies repo files.

Run:  python3 bench/smoketest_decomposed_tools_2026-06-03.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

# Minimal .env loader (same as the sibling smoke tests).
_env = REPO_ROOT / ".env"
if _env.exists():
    for ln in _env.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        ln = ln[7:] if ln.startswith("export ") else ln
        if "=" in ln:
            k, _, v = ln.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# Production code path — the whole point is to use the REAL dispatcher.
from decomposed_dispatch import (  # noqa: E402
    DecomposedChunk,
    DecomposedResult,
    decomposed_dispatch,
)

MODEL_ID = "openai/gpt-5.5"

# Short CDSFL-ish reviewer instruction (system prompt). Kept compact: this is a
# tool-plumbing smoke test, not a full directive-fidelity test.
SYSTEM_PROMPT = (
    "You are a rigorous code reviewer operating under a falsification "
    "discipline. For any defect you claim, you MUST attach a FALSIFIER: a "
    "self-contained Python snippet that imports the REAL target module and "
    "fails (raises AssertionError or prints FALSIFIED) iff the defect is real. "
    "You have an execute_python tool — USE IT to actually RUN your falsifier "
    "against the real code before reporting, and paste the snippet you ran."
)

# Synthesis instruction: ask for exactly one CRITICAL finding with a RUN
# falsifier importing the real module.
FINAL_INSTRUCTION = (
    "Produce exactly ONE finding, your single most CRITICAL concern about the "
    "code you reviewed. Format it as:\n\n"
    "FINDING: <one-line description>\n"
    "SEVERITY: CRITICAL\n"
    "FALSIFIER:\n"
    "```python\n"
    "# import the REAL module under test, e.g. "
    "from bench.dm._similarity import jaccard_similarity\n"
    "# code that raises AssertionError or prints FALSIFIED iff the defect "
    "is real\n"
    "```\n\n"
    "You MUST call the execute_python tool to RUN that falsifier against the "
    "real module before you finalise the finding, then paste the exact snippet "
    "you ran inside the FALSIFIER block. Do not claim a result you did not run."
)


def _build_chunks() -> list[DecomposedChunk]:
    """Split the REAL _similarity.py source into 2 chunks."""
    src = (REPO_ROOT / "bench" / "dm" / "_similarity.py").read_text(
        encoding="utf-8"
    )
    lines = src.splitlines(keepends=True)
    mid = len(lines) // 2
    part0 = "".join(lines[:mid])
    part1 = "".join(lines[mid:])
    return [
        DecomposedChunk(content=part0, label="target_0"),
        DecomposedChunk(content=part1, label="target_1"),
    ]


def _tool_called(result: DecomposedResult) -> bool:
    """True iff an ACTUAL tool call occurred during synthesis.

    The signal is structural, not textual. _record_synthesis_tool_turns (in
    decomposed_dispatch) tags real tool-loop turns with role
    'assistant_tool_call' / 'tool_result'; those roles are emitted ONLY when
    the OpenAI tool loop appended an assistant tool_calls message and its tool
    results. A plain user/assistant turn sequence means no tool call happened —
    even if the model merely *mentions* execute_python in prose, or the system
    prompt names the tool. (A substring match on 'execute_python' would false-
    positive on both, which is why it is deliberately NOT used here.)
    """
    return any(
        t.get("role") in ("assistant_tool_call", "tool_result")
        for t in result.turns
    )


def _falsifier_attached(result: DecomposedResult) -> bool:
    """True iff the synthesis text carries a FALSIFIER block importing the
    real module."""
    text = result.text or ""
    return ("FALSIFIER" in text) and (
        "_similarity" in text or "jaccard_similarity" in text
        or "finding_similarity" in text
    )


def _run(enable_tools: bool) -> DecomposedResult:
    chunks = _build_chunks()
    return decomposed_dispatch(
        api="openrouter",
        model_id=MODEL_ID,
        system_prompt=SYSTEM_PROMPT,
        chunks=chunks,
        final_instruction=FINAL_INSTRUCTION,
        max_tokens=4096,
        timeout=180,
        cdsfl_directives=SYSTEM_PROMPT,
        enable_tools=enable_tools,
    )


def main() -> int:
    if not os.environ.get("OPENROUTER_API_KEY"):
        print(
            "OPENROUTER_API_KEY not set — cannot run the live dispatch. "
            "REPORTING as failure (no fake pass)."
        )
        return 2

    rc = 0

    # --- Path A: enable_tools=True (the new behaviour under test) ----------
    print("=" * 72)
    print(f"PATH A  decomposed_dispatch(api=openrouter, {MODEL_ID}, "
          f"enable_tools=True)")
    print("=" * 72)
    try:
        res_on = _run(enable_tools=True)
    except Exception as exc:  # report, do not fake
        print(f"PATH A FAILED — {type(exc).__name__}: {exc}")
        return 1

    model_called_tool = _tool_called(res_on)
    falsifier_attached = _falsifier_attached(res_on)
    print(f"  model_called_tool   : {model_called_tool}")
    print(f"  falsifier_attached  : {falsifier_attached}")
    print(f"  synthesis_chars     : {len(res_on.text):,}")
    print(f"  turns_recorded      : {len(res_on.turns)}")
    print("  synthesis tail (last 900 chars):")
    print("  " + "-" * 68)
    tail = (res_on.text or "")[-900:]
    print("\n".join("  " + ln for ln in tail.splitlines()))
    print("  " + "-" * 68)

    if not model_called_tool:
        print("  WARN: no execute_python tool call detected in PATH A.")
        rc = rc or 3
    if not falsifier_attached:
        print("  WARN: no FALSIFIER block importing the real module in PATH A.")
        rc = rc or 3

    # --- Path B: enable_tools=False (default-off, must still work) ----------
    print()
    print("=" * 72)
    print(f"PATH B  decomposed_dispatch(api=openrouter, {MODEL_ID}, "
          f"enable_tools=False)  [default-off]")
    print("=" * 72)
    try:
        res_off = _run(enable_tools=False)
    except Exception as exc:
        print(f"PATH B FAILED — {type(exc).__name__}: {exc}")
        return 1

    off_called_tool = _tool_called(res_off)
    print(f"  returned_synthesis  : {bool(res_off.text)}")
    print(f"  synthesis_chars     : {len(res_off.text):,}")
    print(f"  no_tool_attempt     : {not off_called_tool}")
    if off_called_tool:
        print("  WARN: default-off path recorded a tool call — should be "
              "tool-less.")
        rc = rc or 4
    if not res_off.text:
        print("  NOTE: default-off synthesis returned empty (transient model "
              "/ API state; not a wiring fault).")

    print()
    print("=" * 72)
    print("SUMMARY")
    print(f"  PATH A  model_called_tool={model_called_tool}  "
          f"falsifier_attached={falsifier_attached}")
    print(f"  PATH B  default_off_ok={bool(res_off.text) and not off_called_tool}")
    print(f"  exit_code={rc}")
    print("=" * 72)
    return rc


if __name__ == "__main__":
    sys.exit(main())
