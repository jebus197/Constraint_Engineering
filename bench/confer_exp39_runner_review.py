#!/usr/bin/env python3
"""
Confer: Exp 39 Runner Review — 5-Panel Post-Confound Analysis
=============================================================
Dispatches to ALL 5 models: CC2, Codex, Gemini, ChatGPT, DeepSeek.
Full CDSFL + FFAFP protocol.

Purpose: After Exp 39-0 was declared CONFOUNDED (3 independent causes),
fixes were applied. This confer asks all 5 models to compare the fixed
reference_runner.py against the Exp 37 gold standard that achieved ~100%
R_k adoption, and identify any remaining gaps.

Date: 13 April 2026
Protocol: CDSFL + FFAFP
"""

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    call_gemini,
    call_openrouter,
    call_deepseek,
    call_codex,
)

# Load .env
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp39_runner_review"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Model identifiers
GEMINI_MODEL = "gemini-3.1-pro-preview"
CODEX_MODEL = "codex-5.6"
CHATGPT_MODEL = "openai/gpt-5.4"
DEEPSEEK_MODEL = "deepseek-reasoner"
CC2_MODEL = "cc2-opus-4.6"


def _log(msg: str) -> None:
    print(msg, flush=True)


def extract_code_section(filepath: str, start_line: int, end_line: int) -> str:
    """Extract lines start_line..end_line (1-indexed) from a file."""
    p = REPO_ROOT / filepath
    lines = p.read_text(encoding="utf-8").splitlines()
    section = lines[start_line - 1:end_line]
    return "\n".join(f"{i + start_line:4d}  {line}" for i, line in enumerate(section))


def build_comparison_prompt() -> str:
    """Build the detailed comparison prompt for the review."""

    # ── Extract current reference_runner.py sections ──
    rr_prompt = extract_code_section("bench/reference_runner.py", 3023, 3067)
    rr_metrics = extract_code_section("bench/reference_runner.py", 3122, 3190)

    # ── Extract Exp 37 gold standard sections ──
    e37_prompt = extract_code_section("bench/run_exp37_evidence.py", 2829, 2873)
    e37_metrics = extract_code_section("bench/run_exp37_evidence.py", 2310, 2373)
    e37_prior_fix = extract_code_section("bench/run_exp37_evidence.py", 2029, 2043)

    # ── Extract decomposed_dispatch.py FFAFP sections ──
    dd_path = REPO_ROOT / "bench" / "decomposed_dispatch.py"
    dd_text = dd_path.read_text(encoding="utf-8")
    # Find the per-chunk and synthesis instruction sections
    dd_excerpt_lines = []
    in_section = False
    for i, line in enumerate(dd_text.splitlines(), 1):
        if "CORROBORATION" in line or "FALSIFICATION" in line or "R_k" in line:
            start = max(1, i - 3)
            end = min(len(dd_text.splitlines()), i + 3)
            for j in range(start, end + 1):
                dd_excerpt_lines.append(f"{j:4d}  {dd_text.splitlines()[j-1]}")
            dd_excerpt_lines.append("     ...")
    dd_excerpt = "\n".join(dd_excerpt_lines[:60])  # cap

    # ── Subagent findings summary ──
    subagent_findings = """
SUBAGENT REVIEW FINDINGS (5 agents, returned before this confer):

1. PROMPT SCHEMA DIFFERENCES (Agent 1):
   - FINDING_ID stability instruction weakened: Exp 37 has full sentence
     with example ("If you filed F001 in Round 3, F001 in Round 4 must
     refer to the same bug"), reference_runner has only "STABLE across rounds."
   - SEVERITY missing scale anchor: Exp 37 has "(1.0 = critical)",
     reference_runner has only "0.0 to 1.0"
   - ABSTRACTION_INDEX missing scale anchor: Exp 37 has "(0=surface, 1=architectural)"
     — reference_runner also has this, so this finding may be stale
   - Key name mismatch: Exp 37 uses "FIND", reference_runner uses
     "DESCRIPTION: FIND — ..." (parser may expect either)
   - Key name mismatch: Exp 37 uses "FIX", reference_runner uses "PROPOSED_FIX"

2. STALE CALL SITES (Agent 2):
   - 11 call sites of _should_decompose() in legacy runners
     (run_exp31/34/35/36/37/38) don't pass payload_chars parameter
   - Not blocking for Exp 39 (uses reference_runner.py) but technical debt

3. METRICS INJECTION (Agent 3):
   - Exp 37 has === END METRICS === delimiter after metrics section
   - reference_runner has no closing delimiter
   - Exp 37 injects metrics BEFORE registry summary
   - reference_runner appends metrics AFTER registry summary
   - This means models see: [registry entries] [metrics] vs Exp 37's
     [metrics] [registry entries]

4. MISSING FILE CHECK (Agent 4):
   - No graceful handling if config points to non-existent test article
   - Stale docstring in reference_runner still references evidence.py

5. PARSER GAP (Agent 5):
   - Parser does not enforce CORROBORATION independently from FALSIFICATION
   - If a model provides FALSIFICATION but omits CORROBORATION, the finding
     still passes parse validation
   - User prompt parameter names imprecise: "sigma" and "nu" in prompt vs
     "S_k" and "nu_b/nu_f" in the operational directive equation
"""

    return f"""## Exp 39 Runner Review — Post-Confound Fix Analysis

### Background

Experiment 39-0 was declared CONFOUNDED on 13 April 2026 after forensic analysis
revealed 3 independent confounds that invalidated R_k adoption data:

C1 (CRITICAL): User prompt in reference_runner.py had 7-field schema — missing
ANALYSE, FALSIFICATION (MANDATORY), and CORROBORATION (MANDATORY). Exp 37 had a
10-field schema with mandatory R_k computation, and achieved ~100% R_k adoption
across all 5 models. The reference_runner NEVER ASKED for R_k.

C2 (CRITICAL): Total payload was 369K chars (reference_runner.py 163K + runner_core.py
38K + immune_agents.py 167K) = 4.6x the system's own 80K decomposition threshold.
Models compressed output under context pressure.

C3 (HIGH): Monolithic dispatch to CC2/ChatGPT/Gemini despite payload > threshold.
Only Codex/DeepSeek received decomposed dispatch.

Root cause: LESSON ATTRITION. 11 hard-won lessons from Exp 36-38 were silently
dropped when moving from the bespoke run_exp37_evidence.py to the generic
reference_runner.py. The bespoke script encoded lessons as code. The generic
script didn't carry them forward.

### Fixes Applied

1. _build_prompt() rewritten with 10-field schema matching Exp 37
2. All 14 exp39 configs rewritten with fresh unique test articles (all under 80K)
3. _should_decompose() made payload-aware (80K threshold, 200K for CC2)
4. Semantic novelty feedback + rho_bar3 warning ported from Exp 37
5. K/L/M configs corrected from fake domain labels to honest "software"

### Your Task

Compare the FIXED reference_runner.py against the Exp 37 gold standard.
Identify ANY remaining gaps that could cause R_k adoption to fail again.
Also review the subagent findings below and assess which are genuine risks
vs noise.

Apply FFAFP to every finding. Compute R_k for significant findings.

---

### SECTION A: Current reference_runner.py _build_prompt() (FIXED)

```python
{rr_prompt}
```

### SECTION B: Exp 37 Gold Standard _build_prompt() (achieved ~100% R_k adoption)

```python
{e37_prompt}
```

### SECTION C: Current reference_runner.py Metrics Injection (FIXED)

```python
{rr_metrics}
```

### SECTION D: Exp 37 Gold Standard Metrics Injection

```python
{e37_metrics}
```

### SECTION E: Exp 37 Prior Fix Summary (NOT in reference_runner)

```python
{e37_prior_fix}
```

### SECTION F: Subagent Findings
{subagent_findings}

---

### Review Questions

1. Are there remaining field-name mismatches between what the prompt asks for
   and what the parser expects? Which key names does the parser use?

2. Is the metrics injection order (registry-then-metrics vs metrics-then-registry)
   likely to affect model behaviour? Does the missing === END METRICS === delimiter
   matter?

3. The reference_runner uses PROPOSED_FIX with detailed SEARCH/REPLACE format
   instructions. Exp 37 uses bare FIX. Which is better for parser compatibility
   and model compliance?

4. Should the reference_runner have a prior-fix-summary equivalent? The Exp 37
   version is article-specific. What would a generic equivalent look like?

5. Are there any OTHER lessons from Exp 37 that are still missing?

6. The prompt says "sigma" and "nu" for the R_k parameters. The operational
   directive uses S_k, nu_b, nu_f. Does this mismatch matter?

7. Any additional issues not covered by the subagent findings?

End with a clear assessment: is the runner NOW ready for Exp 39 re-launch,
or are there remaining blockers?
"""


def dispatch_cc2(system_prompt: str, user_prompt: str) -> str:
    """CC2 via claude CLI piped mode."""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "claude-sonnet-4-20250514"],
            input=full_prompt,
            capture_output=True, text=True, timeout=600,
            cwd=str(REPO_ROOT),
        )
        return result.stdout.strip() or result.stderr.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "(CC2 timed out after 600s)"
    except FileNotFoundError:
        return "(claude CLI not found)"


def dispatch_codex(system_prompt: str, user_prompt: str) -> str:
    """Codex via codex exec."""
    return call_codex(user_prompt, system_prompt, timeout=600)


def dispatch_gemini(system_prompt: str, user_prompt: str) -> str:
    """Gemini 3.1 Pro via Google API."""
    return call_gemini(GEMINI_MODEL, system_prompt, user_prompt, timeout=300)


def dispatch_chatgpt(system_prompt: str, user_prompt: str) -> str:
    """ChatGPT 5.4 via OpenRouter."""
    return call_openrouter(CHATGPT_MODEL, system_prompt, user_prompt, timeout=300)


def dispatch_deepseek(system_prompt: str, user_prompt: str) -> str:
    """DeepSeek Reasoner via DeepSeek API."""
    return call_deepseek(DEEPSEEK_MODEL, system_prompt, user_prompt, timeout=600)


MODEL_DISPATCHERS = {
    "cc2": ("CC2 (Opus 4.6)", dispatch_cc2),
    "codex": ("Codex 5.6", dispatch_codex),
    "gemini": ("Gemini 3.1 Pro", dispatch_gemini),
    "chatgpt": ("ChatGPT 5.4", dispatch_chatgpt),
    "deepseek": ("DeepSeek Reasoner", dispatch_deepseek),
}


def run_single_review(model_key: str, system_prompt: str, user_prompt: str, ts: str) -> dict:
    """Run a single model review and save logs."""
    name, dispatcher = MODEL_DISPATCHERS[model_key]
    _log(f"  [{ts}] Dispatching to {name}...")
    t0 = time.monotonic()
    try:
        response = dispatcher(system_prompt, user_prompt)
    except Exception as e:
        response = f"(Error: {e})"
    elapsed = time.monotonic() - t0
    _log(f"  [{model_key}] responded in {elapsed:.1f}s ({len(response)} chars)")

    log_entry = {
        "model": name,
        "model_key": model_key,
        "timestamp": ts,
        "elapsed_s": round(elapsed, 1),
        "response_chars": len(response),
        "response": response,
    }

    # Save individual logs
    (LOGS_DIR / f"review_{model_key}_{ts}.json").write_text(
        json.dumps(log_entry, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (LOGS_DIR / f"review_{model_key}_{ts}.txt").write_text(
        response, encoding="utf-8"
    )

    return log_entry


def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    _log(f"=== Exp 39 Runner Review Confer — {ts} ===")
    _log(f"Protocol: CDSFL + FFAFP")
    _log(f"Models: {', '.join(n for n, _ in MODEL_DISPATCHERS.values())}")

    system_prompt = CDSFL_TEXT
    user_prompt = build_comparison_prompt()

    _log(f"\nPrompt size: {len(user_prompt):,} chars")
    _log(f"System prompt size: {len(system_prompt):,} chars")

    results = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {
            pool.submit(run_single_review, key, system_prompt, user_prompt, ts): key
            for key in MODEL_DISPATCHERS
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                _log(f"  [{key}] FAILED: {e}")
                results[key] = {
                    "model_key": key,
                    "error": str(e),
                    "response": f"(Error: {e})",
                }

    # Summary
    _log(f"\n{'=' * 60}")
    _log("CONFER SUMMARY")
    _log(f"{'=' * 60}")
    for key in ["cc2", "codex", "gemini", "chatgpt", "deepseek"]:
        entry = results.get(key, {})
        chars = entry.get("response_chars", 0)
        elapsed = entry.get("elapsed_s", 0)
        name = entry.get("model", key)
        # Check for READY/NOT READY verdict
        resp = entry.get("response", "")
        if "NOT READY" in resp.upper() or "NO-GO" in resp.upper() or "BLOCKER" in resp.upper():
            verdict = "BLOCKERS FOUND"
        elif "READY" in resp.upper() or "GO" in resp.upper():
            verdict = "READY"
        else:
            verdict = "UNCLEAR"
        _log(f"  {name}: {chars} chars, {elapsed}s — {verdict}")

    # Save summary
    summary = {
        "timestamp": ts,
        "confer_type": "exp39_runner_review",
        "models": list(MODEL_DISPATCHERS.keys()),
        "results": {k: {
            "model": v.get("model", k),
            "chars": v.get("response_chars", 0),
            "elapsed_s": v.get("elapsed_s", 0),
        } for k, v in results.items()},
    }
    (LOGS_DIR / f"review_summary_{ts}.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    _log(f"\nLogs saved to: {LOGS_DIR}")
    _log("Done.")


if __name__ == "__main__":
    main()
