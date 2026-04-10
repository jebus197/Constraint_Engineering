#!/usr/bin/env python3
"""
Confer: Experiment 38 Plan + Runner — P-Pass by Model Panel
============================================================
Dispatches to Gemini 3.1 Pro and Codex GPT-5.4 SEQUENTIALLY under
combined 4-layer schema. Sends:
  1. The complete Exp 38 plan (ouroboros: system reviews itself)
  2. The updated runner with S_k pipeline
  3. The updated operational directive with S_k
  4. The Cell Type Architecture analysis for commentary
  5. All prior confer findings folded in

Sequential dispatch: Gemini first, then Codex. Each receives the same
artifacts under full CDSFL + FFAFP.

Date: 9 April 2026
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp38_plan"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

# ---------------------------------------------------------------------------
# Load all artifacts
# ---------------------------------------------------------------------------

# CDSFL core directives (system prompt base)
CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Exp 38 plan
EXP38_PLAN_PATH = REPO_ROOT / "experimental_notes" / "Exp38_Plan_2026-04-09.md"
EXP38_PLAN = EXP38_PLAN_PATH.read_text(encoding="utf-8")

# Updated operational directive
OPERATIONAL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
OPERATIONAL_TEXT = OPERATIONAL_PATH.read_text(encoding="utf-8")

# Updated runner (S_k pipeline section only — full runner is too large)
RUNNER_PATH = REPO_ROOT / "bench" / "reference_runner.py"
RUNNER_FULL = RUNNER_PATH.read_text(encoding="utf-8")

# Extract S_k-related sections from the runner (not the entire middle)
_ds_start = RUNNER_FULL.find("# S_k Solution Verification — Data Structures")
_ds_end = RUNNER_FULL.find("# FindingRegistry", _ds_start)
_pipeline_start = RUNNER_FULL.find("# S_k Solution Verification Pipeline")
_pipeline_end = RUNNER_FULL.find("# Preflight", _pipeline_start)
if _ds_start > 0 and _pipeline_end > 0:
    RUNNER_SK_SECTION = (
        RUNNER_FULL[_ds_start:_ds_end].rstrip() + "\n\n"
        + RUNNER_FULL[_pipeline_start:_pipeline_end].rstrip()
    )
else:
    RUNNER_SK_SECTION = "(S_k section not found — check runner)"

# Also extract RunnerConfig for context
_cfg_start = RUNNER_FULL.find("class RunnerConfig:")
_cfg_end = RUNNER_FULL.find("# S_k Solution Verification — Data Structures", _cfg_start)
if _cfg_start > 0 and _cfg_end > 0:
    RUNNER_CONFIG_SECTION = RUNNER_FULL[_cfg_start:_cfg_end]
else:
    RUNNER_CONFIG_SECTION = "(RunnerConfig not found)"

# Cell type architecture TTS
CELL_ARCH_PATH = (
    Path.home() / "Desktop" / "CDSFL_tts" / "Cell_Type_Architecture_2026-04-09.txt"
)
CELL_ARCH_TEXT = CELL_ARCH_PATH.read_text(encoding="utf-8") if CELL_ARCH_PATH.exists() else ""

# Expert encoding template + Python reference
TEMPLATE_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "expert_encoding_template.md"
TEMPLATE_TEXT = TEMPLATE_PATH.read_text(encoding="utf-8")

PYTHON_SK_PATH = REPO_ROOT / "bench" / "directives" / "software" / "software_python_sk.txt"
PYTHON_SK_TEXT = PYTHON_SK_PATH.read_text(encoding="utf-8")

# Prior confer synthesis (for context)
PRIOR_CONFER_PATH = (
    REPO_ROOT / "experimental_notes" / "Expert_Encoding_Confer_2026-04-09.md"
)
PRIOR_CONFER = PRIOR_CONFER_PATH.read_text(encoding="utf-8") if PRIOR_CONFER_PATH.exists() else ""

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
# User Prompt
# ---------------------------------------------------------------------------

USER_PROMPT = f"""
# Context: Experiment 38 Plan and Runner — Full P-Pass Request

## Background

Experiment 38 is the ouroboros: the CDSFL system reviews and improves itself
under structured falsification. The five-model panel reviews the system's own
encodings, mathematical model, and runner, proposes improvements as
machine-verifiable SEARCH/REPLACE fixes, and those fixes are evaluated through
the S_k tool gate pipeline. Surviving improvements are applied. The system
uses itself to improve itself.

This confer request asks you to P-pass the complete Exp 38 plan and the
updated runner implementation. All observations from the prior confer rounds
(S_k solution reliability, expert encodings, encoding enrichment) have been
folded into this plan and these code changes.

---

## Artifact 1: Experiment 38 Plan

{EXP38_PLAN}

---

## Artifact 2: Updated Operational Directive (S_k replaces sigma)

{OPERATIONAL_TEXT}

---

## Artifact 3: Runner S_k Pipeline (new code)

```python
{RUNNER_SK_SECTION}
```

---

## Artifact 4: Runner Configuration (updated)

```python
{RUNNER_CONFIG_SECTION}
```

---

## Artifact 5: Expert Encoding Template

```
{TEMPLATE_TEXT}
```

---

## Artifact 6: Python Reference S_k Encoding

```
{PYTHON_SK_TEXT}
```

---

## Artifact 7: Cell Type Architecture for Domain Generalisation

{CELL_ARCH_TEXT}

---

## Artifact 8: Prior Confer Findings (already folded in — for reference)

{PRIOR_CONFER}

---

## Your Task

1. **P-PASS THE EXP 38 PLAN.** Is the plan complete? Are there gaps in the
   experimental design? Is the ouroboros framing sound (can the system
   meaningfully review itself)? Are the success criteria measurable? Is
   anything missing that would be needed to run the experiment?

2. **P-PASS THE RUNNER S_k PIPELINE.** Is the implementation correct?
   - Does parse_search_replace_blocks handle edge cases (nested blocks,
     multiline content, whitespace sensitivity)?
   - Does compute_sk correctly implement A * E with renormalised geometric
     mean?
   - Does compute_rk correctly implement the three-phase update with bounded
     nu_eff?
   - Does check_sk_threshold correctly implement the Valley of Bad Fixes?
   - Are there race conditions or state corruption risks in gate evaluation?
   - Is the temp file handling safe (cleanup, no persistent state)?

3. **P-PASS THE OPERATIONAL DIRECTIVE.** Is the S_k update to the directive
   mathematically consistent with the runner implementation? Does the
   directive correctly explain the Valley of Bad Fixes? Is the fix format
   section sufficient for models to produce parseable output? Are there
   any contradictions between the new sections and the existing sections?

4. **P-PASS THE CELL TYPE ARCHITECTURE.** Is the biological mapping sound?
   Does multi-cell S_k composition work as described? Is hybrid activation
   routing robust? Where does the architecture break down?

5. **IDENTIFY IMPLEMENTATION GAPS.** What is missing from the runner that
   would be needed for Exp 38 to actually run? What configuration changes
   are needed? Are there integration points between the S_k pipeline and
   the existing immune/endocrine/brain systems that are not yet wired?

6. **PROPOSE SPECIFIC FIXES.** For any issues found, propose fixes as
   SEARCH/REPLACE blocks targeting the specific files. This is both useful
   and a test of the fix format itself — if you cannot express your fix
   as a SEARCH/REPLACE block, that is a finding about the fix format.

Apply FFAFP to ALL proposals. P-pass up to 5 times. Only present survivors.
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
        out_path = LOGS_DIR / f"exp38_plan_gemini_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"exp38_plan_gemini_{ts}.txt"
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
        out_path = LOGS_DIR / f"exp38_plan_cx_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"exp38_plan_cx_{ts}.txt"
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
    print("CDSFL Confer: Experiment 38 Plan + Runner")
    print(f"Started: {_ts()}")
    print("Models: Gemini 3.1 Pro (first), Codex GPT-5.4 (second)")
    print("Protocol: 4-layer (Meta + CDSFL + FFAFP + Conversational)")
    print(f"Prompt size: ~{len(USER_PROMPT):,} chars")
    print("=" * 60)
    print()

    # Sequential dispatch as requested
    print("--- Phase 1: Gemini 3.1 Pro ---")
    gemini_result = dispatch_gemini(FOUR_LAYER_SYSTEM, USER_PROMPT)
    print()

    print("--- Phase 2: Codex GPT-5.4 ---")
    codex_result = dispatch_codex(FOUR_LAYER_SYSTEM, USER_PROMPT)
    print()

    print("=" * 60)
    print("CONFER COMPLETE")
    print("=" * 60)
    for label, r in [("Gemini", gemini_result), ("Codex", codex_result)]:
        if "error" in r:
            print(f"  {label}: FAILED — {r['error']}")
        else:
            print(f"  {label}: {r['response_length']} chars, {r['elapsed_s']}s")
    print(f"\nLogs: {LOGS_DIR}")


if __name__ == "__main__":
    main()
