#!/usr/bin/env python3
"""
Confer: Experiment 38 Runner Fitness Review
============================================
Dispatches to Gemini 3.1 Pro and Codex GPT-5.4 SEQUENTIALLY under
combined 4-layer schema. Focused question: is the runner fit for
purpose? Will Exp 38 run cleanly end to end?

Sends:
  1. Runner S_k pipeline (data structures + pipeline functions + main loop integration)
  2. RunnerConfig
  3. Updated operational directive
  4. Expert encoding template (with new sections: baseline, domain knowledge,
     verification status, epistemological boundary)
  5. Python reference encoding (with baseline capture, domain knowledge,
     verification status)
  6. Exp 38 plan (for context on what the runner needs to do)

Date: 10 April 2026
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import call_openrouter, call_gemini

# Load .env (handles 'export KEY=val' format)
_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#"):
            continue
        if _line.startswith("export "):
            _line = _line[7:]
        if "=" in _line:
            _k, _, _v = _line.partition("=")
            _k = _k.strip()
            _v = _v.strip().strip("'\"")
            os.environ.setdefault(_k, _v)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp38_fitness"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

# ---------------------------------------------------------------------------
# Load all artifacts
# ---------------------------------------------------------------------------

# CDSFL core directives (system prompt base)
CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Exp 38 plan (context only)
EXP38_PLAN_PATH = REPO_ROOT / "experimental_notes" / "Exp38_Plan_2026-04-09.md"
EXP38_PLAN = EXP38_PLAN_PATH.read_text(encoding="utf-8")

# Updated operational directive
OPERATIONAL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
OPERATIONAL_TEXT = OPERATIONAL_PATH.read_text(encoding="utf-8")

# Full runner
RUNNER_PATH = REPO_ROOT / "bench" / "reference_runner.py"
RUNNER_FULL = RUNNER_PATH.read_text(encoding="utf-8")

# Extract S_k data structures + pipeline + main loop integration
_ds_start = RUNNER_FULL.find("# S_k Solution Verification — Data Structures")
_ds_end = RUNNER_FULL.find("class FindingRegistry:", _ds_start)
_pipeline_start = RUNNER_FULL.find("# S_k Solution Verification Pipeline")
_pipeline_end = RUNNER_FULL.find("# Preflight", _pipeline_start)

# Also extract main loop S_k integration points
_main_start = RUNNER_FULL.find("sk_baseline: Dict[str, Any] = {}")
if _main_start > 0:
    _main_end = RUNNER_FULL.find("round_data[", _main_start + 500)
    if _main_end > 0:
        _main_end = RUNNER_FULL.find("\n\n", _main_end)
        RUNNER_MAIN_INTEGRATION = RUNNER_FULL[_main_start:_main_end].strip()
    else:
        RUNNER_MAIN_INTEGRATION = RUNNER_FULL[_main_start:_main_start + 1000].strip()
else:
    RUNNER_MAIN_INTEGRATION = "(main loop integration not found)"

if _ds_start > 0 and _pipeline_end > 0:
    RUNNER_SK_SECTION = (
        RUNNER_FULL[_ds_start:_ds_end].rstrip() + "\n\n"
        + RUNNER_FULL[_pipeline_start:_pipeline_end].rstrip()
    )
else:
    RUNNER_SK_SECTION = "(S_k section not found — check runner)"

# RunnerConfig
_cfg_start = RUNNER_FULL.find("class RunnerConfig:")
_cfg_end = RUNNER_FULL.find("# S_k Solution Verification — Data Structures", _cfg_start)
if _cfg_start > 0 and _cfg_end > 0:
    RUNNER_CONFIG_SECTION = RUNNER_FULL[_cfg_start:_cfg_end]
else:
    RUNNER_CONFIG_SECTION = "(RunnerConfig not found)"

# Expert encoding template
TEMPLATE_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "expert_encoding_template.md"
TEMPLATE_TEXT = TEMPLATE_PATH.read_text(encoding="utf-8")

# Python reference encoding
PYTHON_SK_PATH = REPO_ROOT / "bench" / "directives" / "software" / "software_python_sk.txt"
PYTHON_SK_TEXT = PYTHON_SK_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# 4-Layer System Prompt
# ---------------------------------------------------------------------------

FOUR_LAYER_SYSTEM = f"""{CDSFL_TEXT}

---

## Interaction Protocol: Combined 4-Layer Schema

You are operating under a combined 4-layer interaction schema. Apply ALL four
layers simultaneously. They are complementary, not alternatives.

### Layer 1 — Meta Structured Prompting (arXiv 2603.01896)

For EVERY claim, finding, or proposed extension, you MUST provide:

1. **STRUCTURED CERTIFICATE:** State your premises explicitly. Trace execution
   through concrete examples (with specific inputs and expected outputs). Derive
   a formal conclusion.

2. **FIND-FOLLOW-ANALYSE-FIX (FFAF):** For every issue —
   FIND: State the issue, its location, and your evidence.
   FOLLOW: Before proposing any change, trace consequences.
   ANALYSE: State dispassionately whether this is CONFIRMED, UNCERTAIN, or
   REJECTED based on evidence, not intuition.
   FIX: For CONFIRMED issues only, propose the simplest sufficient correction.

3. **SELF-FALSIFICATION:** Actively try to disprove your own conclusions.

4. **RIGOUR:** Provide formal justification for every structural claim.

### Layer 2 — CDSFL Constraints
The full CDSFL core formal directives above apply.

### Layer 3 — FFAFP with Iterated P-Pass
P-pass your own results up to 5 times or until convergence.

### Layer 4 — Conversational Fallback
Where structured format does not naturally apply, use natural prose.
"""

# ---------------------------------------------------------------------------
# User Prompt — Fitness Review
# ---------------------------------------------------------------------------

USER_PROMPT = f"""
# Experiment 38 Runner — Fitness Review

## The Question

The S_k pipeline has been implemented in the reference runner. Nine confer
findings from the previous round have been applied and verified (690 tests
pass). The question now is simple:

**Is this runner fit for purpose? Will Experiment 38 run cleanly from end
to end?**

This is not a general review. This is a go/no-go assessment. Trace the
execution path that Exp 38 will follow, from preflight through round loop
through S_k evaluation, and identify anything that would cause a crash,
incorrect result, or silent failure.

---

## What Exp 38 Does (Context)

{EXP38_PLAN}

---

## Artifact 1: Runner S_k Pipeline (data structures + functions)

```python
{RUNNER_SK_SECTION}
```

---

## Artifact 2: Runner Configuration

```python
{RUNNER_CONFIG_SECTION}
```

---

## Artifact 3: Main Loop S_k Integration Points

```python
{RUNNER_MAIN_INTEGRATION}
```

---

## Artifact 4: Operational Directive (S_k sections)

{OPERATIONAL_TEXT}

---

## Artifact 5: Expert Encoding Template (universal)

```
{TEMPLATE_TEXT}
```

---

## Artifact 6: Python Reference Encoding

```
{PYTHON_SK_TEXT}
```

---

## Your Task — Go/No-Go

Trace the Exp 38 execution path and answer these specific questions:

1. **PARSE PATH:** A model returns a finding with SEARCH/REPLACE blocks in
   the proposed_fix field. Walk through parse_search_replace_blocks(). Will
   it correctly parse blocks with: (a) single file, (b) multiple files,
   (c) multi-line search/replace content, (d) content containing delimiter-
   like strings (e.g., lines starting with "====")? What breaks?

2. **APPLY PATH:** The parsed blocks are passed to apply_fix_blocks(). The
   source file may be referenced by full path or basename. Walk through the
   matching logic. What happens when (a) the search string has trailing
   whitespace differences, (b) the file path uses a different prefix than
   the source, (c) multiple blocks target the same file?

3. **GATE PATH:** Modified source enters the gate pipeline. Walk through
   each gate: g1 (AST), g2 (py_compile), e2 (regression), e3 (ruff),
   e4 (bandit). For each: what inputs does it receive, what can go wrong,
   what does it return on success/failure/unavailable?

4. **THRESHOLD PATH:** S_k is computed, check_sk_threshold is called.
   Walk through the nu clamping, S* computation, and R_k loop closure.
   Are there parameter combinations that produce mathematically invalid
   results?

5. **INTEGRATION PATH:** The main loop calls _evaluate_sk_for_findings
   after CC2v. Walk through: which findings are selected, how are results
   stored, what gets logged, what feeds back into the next round?

6. **CONFIGURATION:** What RunnerConfig values must be set for S_k to
   activate? Is there anything that defaults to off/None that would
   silently skip the entire pipeline?

7. **CRASH SCENARIOS:** What combination of model output, file state, or
   environment condition would cause an unhandled exception in the S_k
   pipeline? Be specific: function name, line, input that triggers it.

For CONFIRMED issues, propose SEARCH/REPLACE fixes targeting
bench/reference_runner.py. This tests the fix format itself.

Do NOT re-raise findings from the previous confer round (regression sandbox,
parser rewrite, E aggregation, ruff delta, nu clamping, ESCALATE semantics,
S* edge cases, directive residue, encoding alignment). Those are applied and
verified. Focus on what remains.

Apply FFAFP to ALL findings. P-pass up to 5 times. Only present survivors.
"""

# ---------------------------------------------------------------------------
# Dispatch Functions
# ---------------------------------------------------------------------------

def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def dispatch_gemini(system: str, user: str) -> dict:
    ts = _ts()
    print(f"[{ts}] Dispatching to Gemini 3.1 Pro...", flush=True)
    t0 = time.monotonic()
    try:
        response = call_gemini(
            model_id=GEMINI_MODEL,
            system_prompt=system,
            user_prompt=user,
        )
        elapsed = time.monotonic() - t0
        result = {
            "model": "Gemini",
            "model_id": GEMINI_MODEL,
            "timestamp": ts,
            "elapsed_s": round(elapsed, 1),
            "response": response,
            "response_length": len(response),
        }
        out_path = LOGS_DIR / f"exp38_fitness_gemini_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"exp38_fitness_gemini_{ts}.txt"
        txt_path.write_text(response, encoding="utf-8")
        print(f"[{_ts()}] Gemini done ({elapsed:.0f}s, {len(response)} chars)")
        return result
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"[{_ts()}] Gemini FAILED after {elapsed:.0f}s: {e}")
        return {"model": "Gemini", "error": str(e), "elapsed_s": round(elapsed, 1)}


def dispatch_codex(system: str, user: str) -> dict:
    ts = _ts()
    print(f"[{ts}] Dispatching to Codex GPT-5.4...", flush=True)
    t0 = time.monotonic()
    try:
        response = call_openrouter(
            model_id=CX_MODEL,
            system_prompt=system,
            user_prompt=user,
        )
        elapsed = time.monotonic() - t0
        result = {
            "model": "Codex",
            "model_id": CX_MODEL,
            "timestamp": ts,
            "elapsed_s": round(elapsed, 1),
            "response": response,
            "response_length": len(response),
        }
        out_path = LOGS_DIR / f"exp38_fitness_cx_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"exp38_fitness_cx_{ts}.txt"
        txt_path.write_text(response, encoding="utf-8")
        print(f"[{_ts()}] Codex done ({elapsed:.0f}s, {len(response)} chars)")
        return result
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"[{_ts()}] Codex FAILED after {elapsed:.0f}s: {e}")
        return {"model": "Codex", "error": str(e), "elapsed_s": round(elapsed, 1)}


# ---------------------------------------------------------------------------
# Main — Sequential dispatch (Gemini first, then Codex)
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("CDSFL Confer: Experiment 38 Runner Fitness Review")
    print(f"Started: {_ts()}")
    print("Models: Gemini 3.1 Pro (first), Codex GPT-5.4 (second)")
    print("Protocol: 4-layer (Meta + CDSFL + FFAFP + Conversational)")
    print(f"Prompt size: ~{len(USER_PROMPT):,} chars")
    print("=" * 60)
    print()

    # Sequential dispatch
    print("--- Phase 1: Gemini 3.1 Pro ---")
    gemini_result = dispatch_gemini(FOUR_LAYER_SYSTEM, USER_PROMPT)
    print()

    print("--- Phase 2: Codex GPT-5.4 ---")
    codex_result = dispatch_codex(FOUR_LAYER_SYSTEM, USER_PROMPT)
    print()

    print("=" * 60)
    print("CONFER COMPLETE")
    print("=" * 60)
    gemini_chars = gemini_result.get("response_length", 0)
    codex_chars = codex_result.get("response_length", 0)
    print(f"  Gemini: {gemini_chars} chars, {gemini_result.get('elapsed_s', '?')}s")
    print(f"  Codex: {codex_chars} chars, {codex_result.get('elapsed_s', '?')}s")
    print(f"\nLogs: {LOGS_DIR}")


if __name__ == "__main__":
    main()
