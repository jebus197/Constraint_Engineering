#!/usr/bin/env python3
"""
Confer: Expert Encoding S_k Gates — P-Pass by Model Panel
==========================================================
Dispatches to Gemini 3.1 Pro and Codex GPT-5.4 under combined 4-layer schema.
Asks them to P-pass the expert encoding template and Python reference
implementation, identify gaps, and propose domain-specific gate definitions
for mathematics, chemistry, physics, and engineering.

Date: 9 April 2026
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_expert_encodings"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

TEMPLATE_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "expert_encoding_template.md"
TEMPLATE_TEXT = TEMPLATE_PATH.read_text(encoding="utf-8")

PYTHON_SK_PATH = REPO_ROOT / "bench" / "directives" / "software" / "software_python_sk.txt"
PYTHON_SK_TEXT = PYTHON_SK_PATH.read_text(encoding="utf-8")

# Load a sample of existing domain directives for context
SAMPLE_DIRECTIVES = {}
samples = [
    ("mathematics", "mathematics/mathematics_general.txt"),
    ("chemistry_process", "chemistry/chemistry_process.txt"),
    ("software_security", "software/software_security.txt"),
    ("hardware_embedded", "hardware/hardware_embedded.txt"),
    ("structural_bridge", "structural/structural_bridge.txt"),
]
for label, relpath in samples:
    p = REPO_ROOT / "bench" / "directives" / relpath
    if p.exists():
        SAMPLE_DIRECTIVES[label] = p.read_text(encoding="utf-8")

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

# ---------------------------------------------------------------------------
# 4-Layer System Prompt (same as confer_solution_reliability.py)
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

SAMPLE_TEXT = "\n\n---\n\n".join(
    f"### Existing Directive: {label}\n```\n{text}\n```"
    for label, text in SAMPLE_DIRECTIVES.items()
)

USER_PROMPT = f"""
# Context: Expert Encoding S_k Gates — P-Pass Request

## Background

The CDSFL framework has a layered directive structure with 27 domain-specific
constraint directives across 9 domains (software, mathematics, chemistry,
hardware, structural, biomedical, industrial, logistics, product engineering,
cross-domain). Each directive defines HARD constraints, SOFT constraints,
verification procedures, and limitations for its domain.

We have just designed the S_k solution reliability extension to the R_k
mathematical model. S_k = A · E where:
  A = product of hard gates (admissibility, binary veto)
  E = weighted product of effect evidence (graded 0-1)

The S_k framework is domain-invariant — only the gate definitions change
across domains. We need to extend each domain directive with solution
verification gates that define what S_k means in that domain.

## What We've Drafted

### 1. Expert Encoding Template (universal structure)

```
{TEMPLATE_TEXT}
```

### 2. Python/Code Reference Implementation

```
{PYTHON_SK_TEXT}
```

### 3. Sample Existing Domain Directives (for context)

{SAMPLE_TEXT}

## Your Task

1. **P-PASS THE TEMPLATE STRUCTURE.** Is the template complete? Are the six
   sections (hard gates, effect evidence, fix format, tool mapping, S* guidance,
   limitations) sufficient? Is anything missing that would be needed across
   ALL domains? Is anything included that shouldn't be universal?

2. **P-PASS THE PYTHON REFERENCE.** Is the Python S_k encoding correct and
   complete? Are the gates well-defined? Are the weights reasonable? Is the
   SEARCH/REPLACE fix format sufficient? Are there gaps in what can be verified?

3. **PROPOSE S_k ENCODINGS for these domains** (fill in the template structure
   for each). Use the same format as the Python reference. Be specific about
   tools, scoring methods, and pass/fail conditions:

   a. **Mathematics (proofs and derivations)** — What are the hard gates?
      What tools verify a corrected proof step? What is the fix format for
      a mathematical correction?

   b. **Chemistry (process/pharma)** — What are the hard gates? How do you
      tool-verify a corrected reaction scheme or stoichiometric balance?

   c. **Physics / Engineering (dimensional, structural)** — What are the hard
      gates? How do you tool-verify a corrected calculation or design parameter?

   d. **Hardware (embedded, RF, power)** — What are the hard gates? How do
      you tool-verify a corrected schematic or timing constraint?

4. **IDENTIFY CROSS-DOMAIN GAPS.** Are there domains in our existing 27
   directives where S_k solution verification is fundamentally impossible
   with available tools? Where must we honestly state "this requires HIL"?

5. **IDENTIFY STRUCTURAL GAPS.** Is there anything about the template
   structure itself that won't work for certain domains? Does the A · E
   decomposition break down anywhere? Is the fix format concept universal?

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
        out_path = LOGS_DIR / f"expert_encodings_gemini_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"expert_encodings_gemini_{ts}.txt"
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
        out_path = LOGS_DIR / f"expert_encodings_cx_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"expert_encodings_cx_{ts}.txt"
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
    print("CDSFL Confer: Expert Encoding S_k Gates")
    print(f"Started: {_ts()}")
    print("Models: Gemini 3.1 Pro, Codex GPT-5.4")
    print("Protocol: 4-layer (Meta + CDSFL + FFAFP + Conversational)")
    print("=" * 60)
    print()

    results = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(dispatch_gemini, FOUR_LAYER_SYSTEM, USER_PROMPT): "Gemini",
            pool.submit(dispatch_codex, FOUR_LAYER_SYSTEM, USER_PROMPT): "Codex",
        }
        for future in as_completed(futures):
            label = futures[future]
            try:
                results[label] = future.result()
            except Exception as e:
                print(f"[{_ts()}] {label} exception: {e}")
                results[label] = {"model": label, "error": str(e)}

    print()
    print("=" * 60)
    print("CONFER COMPLETE")
    print("=" * 60)
    for label, r in results.items():
        if "error" in r:
            print(f"  {label}: FAILED — {r['error']}")
        else:
            print(f"  {label}: {r['response_length']} chars, {r['elapsed_s']}s")
    print(f"\nLogs: {LOGS_DIR}")


if __name__ == "__main__":
    main()
