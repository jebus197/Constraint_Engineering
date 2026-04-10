#!/usr/bin/env python3
"""
Confer: Experiment 38 Fix Review (Round 2)
==========================================
Dispatches to Gemini 3.1 Pro and Codex GPT-5.4 SEQUENTIALLY under
combined 4-layer schema. Reviews 6 fixes applied after the fitness
confer round and checks mathematical model consistency.

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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp38_fix_review"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------

# CDSFL core directives (system prompt base)
CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Full runner (post-fix)
RUNNER_PATH = REPO_ROOT / "bench" / "reference_runner.py"
RUNNER_FULL = RUNNER_PATH.read_text(encoding="utf-8")

# Extract S_k pipeline section
_ds_start = RUNNER_FULL.find("# S_k Solution Verification — Data Structures")
_ds_end = RUNNER_FULL.find("class FindingRegistry:", _ds_start)
_pipeline_start = RUNNER_FULL.find("# S_k Solution Verification Pipeline")
_pipeline_end = RUNNER_FULL.find("# Preflight", _pipeline_start)

if _ds_start > 0 and _pipeline_end > 0:
    RUNNER_SK_SECTION = (
        RUNNER_FULL[_ds_start:_ds_end].rstrip() + "\n\n"
        + RUNNER_FULL[_pipeline_start:_pipeline_end].rstrip()
    )
else:
    RUNNER_SK_SECTION = "(S_k section not found — check runner)"

# Main loop integration
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

# RunnerConfig
_cfg_start = RUNNER_FULL.find("class RunnerConfig:")
_cfg_end = RUNNER_FULL.find("# S_k Solution Verification — Data Structures", _cfg_start)
if _cfg_start > 0 and _cfg_end > 0:
    RUNNER_CONFIG_SECTION = RUNNER_FULL[_cfg_start:_cfg_end]
else:
    RUNNER_CONFIG_SECTION = "(RunnerConfig not found)"

# Operational directive
OPERATIONAL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
OPERATIONAL_TEXT = OPERATIONAL_PATH.read_text(encoding="utf-8")

# Python encoding
PYTHON_SK_PATH = REPO_ROOT / "bench" / "directives" / "software" / "software_python_sk.txt"
PYTHON_SK_TEXT = PYTHON_SK_PATH.read_text(encoding="utf-8")

# Expert encoding template
TEMPLATE_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "expert_encoding_template.md"
TEMPLATE_TEXT = TEMPLATE_PATH.read_text(encoding="utf-8")

# Exp 38 plan
EXP38_PLAN_PATH = REPO_ROOT / "experimental_notes" / "Exp38_Plan_2026-04-09.md"
EXP38_PLAN = EXP38_PLAN_PATH.read_text(encoding="utf-8")

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
# User Prompt — Fix Review
# ---------------------------------------------------------------------------

USER_PROMPT = f"""
# Experiment 38 Runner — Fix Review (Round 2)

## Context

After the first fitness confer round, 7 confirmed findings were identified by
Gemini 3.1 Pro and Codex GPT-5.4 (1 false positive excluded — @dataclass IS
present at line 144). These 7 findings have been applied as 6 fixes (F1+F2
merged) to the runner. All 690 existing tests pass after each fix.

## The 6 Fixes Applied

**F1+F2 (merged): Context-anchored temp files + tool failure returns None**
- `_run_effect_ruff`, `_run_effect_bandit`: Now take `source_path` parameter,
  anchor temp files to `Path(source_path).parent` so ruff/bandit see
  pyproject.toml. Accept `Optional[int]` baseline (None = tool unavailable).
  Check `result.returncode not in (0, 1)` — failure returns None. Validate
  JSON structure (`isinstance` check) — wrong type returns None.
- `_capture_baseline`: Now takes `source_path`, anchors temp files, stores
  None (not 0) when tool unavailable or JSON invalid.
- `compute_sk`: Passes `source_path` through to effect gates. Uses
  `baseline.get("ruff_violations")` (no default) — returns None when
  baseline unavailable, propagating correctly to ESCALATE.

**F3: Regression gate mis-score fix**
- `_run_effect_regression`: Unparseable output no longer returns 1.0.
  Only explicit "collected 0 items" with exit code 5 returns 1.0.
  All other unparseable output returns None (unavailable).

**F4: Ambiguous block uniqueness check**
- `apply_fix_blocks`: Before `.replace()`, checks
  `modified.count(block.search) > 1`. Ambiguous blocks (>1 occurrence)
  return `(None, 0)` — REJECTED tristate.

**F5: Input validation for risk math**
- `compute_rk`: Now clamps R_old, q, sk to [0,1] before nu clamping.
- `check_sk_threshold`: Now clamps sk, q, R, s_floor to [0,1] before nu
  clamping.

**F6: Filter relaxation**
- `_evaluate_sk_for_findings`: Filter changed from `"<<<< SEARCH" not in
  fix_text` to `"<<<<" not in fix_text` — matches parser tolerance.

**F7: Parser delimiter cleanup**
- `parse_search_replace_blocks`: Duplicate condition
  `lines[i].rstrip() == "====" or lines[i].rstrip() == "===="` reduced
  to single `lines[i].rstrip() == "===="`.

---

## Your Task — Review the Fixed Runner

These fixes address the previous round's findings. Your task is now:

1. **VERIFY FIXES:** Trace each fix through the code. Does it actually solve
   the problem it was meant to solve? Are there edge cases the fix misses?
   Are there regressions introduced?

2. **MATHEMATICAL MODEL CONSISTENCY:** The S_k model is:
   - S_k = A * E where A = product of hard gates, E = weighted arithmetic
     mean of effect evidence (renormalised over available gates)
   - R_k update: three-phase (detection, resolution, re-injection) with
     bounded nu_eff = 1 - (1-nu_b)*(1-(1-S_k)*nu_f)
   - S* break-even threshold: (nu_b + nu_f - nu_b*nu_f - q*R) / (nu_f*(1-nu_b))
   - Tristate: ADMISSIBLE (S_k >= S*), REJECTED (hard gate fail or S_k < S*),
     ESCALATE (no evidence available)
   Does the code implementation match these definitions? Are there any
   algebraic errors, edge case mismatches, or semantic inconsistencies
   between the math and the code?

3. **END-TO-END FIT:** Given all 15 fixes (9 original + 6 new), is the
   runner now fit for purpose for Experiment 38? Trace the full execution
   path: config load -> preflight -> round loop -> model dispatch ->
   finding evaluation -> S_k pipeline -> threshold check -> R_k update ->
   convergence check. What would cause a crash, silent error, or incorrect
   result?

4. **GO/NO-GO:** Deliver a clear go/no-go verdict.

---

## Artifact 1: Full S_k Pipeline (post-fix)

```python
{RUNNER_SK_SECTION}
```

---

## Artifact 2: Runner Configuration

```python
{RUNNER_CONFIG_SECTION}
```

---

## Artifact 3: Main Loop S_k Integration

```python
{RUNNER_MAIN_INTEGRATION}
```

---

## Artifact 4: Operational Directive

{OPERATIONAL_TEXT}

---

## Artifact 5: Expert Encoding Template

```
{TEMPLATE_TEXT}
```

---

## Artifact 6: Python Reference Encoding

```
{PYTHON_SK_TEXT}
```

---

## Artifact 7: Exp 38 Plan

{EXP38_PLAN}

---

For CONFIRMED issues only, propose SEARCH/REPLACE fixes targeting
bench/reference_runner.py. Apply FFAFP to ALL findings. P-pass up to
5 times. Only present survivors.
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
        out_path = LOGS_DIR / f"exp38_fix_review_gemini_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"exp38_fix_review_gemini_{ts}.txt"
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
        out_path = LOGS_DIR / f"exp38_fix_review_cx_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"exp38_fix_review_cx_{ts}.txt"
        txt_path.write_text(response, encoding="utf-8")
        print(f"[{_ts()}] Codex done ({elapsed:.0f}s, {len(response)} chars)")
        return result
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"[{_ts()}] Codex FAILED after {elapsed:.0f}s: {e}")
        return {"model": "Codex", "error": str(e), "elapsed_s": round(elapsed, 1)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("CDSFL Confer: Experiment 38 Fix Review (Round 2)")
    print(f"Started: {_ts()}")
    print("Models: Gemini 3.1 Pro (first), Codex GPT-5.4 (second)")
    print("Protocol: 4-layer (Meta + CDSFL + FFAFP + Conversational)")
    print(f"Prompt size: ~{len(USER_PROMPT):,} chars")
    print("=" * 60)
    print()

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
