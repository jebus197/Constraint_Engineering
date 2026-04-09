#!/usr/bin/env python3
"""
Confer: Expert Encoding Enrichment — From Thin Constraints to Domain Expertise
==============================================================================
Dispatches to Gemini 3.1 Pro and Codex GPT-5.4 under combined 4-layer schema.
Asks them to assess the current domain directives, propose enrichment strategies,
and address the verification status question for Bench Run 2.

Date: 9 April 2026
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import call_openrouter, call_gemini

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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_encoding_enrichment"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Load ALL existing domain directives for full context
ALL_DIRECTIVES = {}
directives_root = REPO_ROOT / "bench" / "directives"
for txt in sorted(directives_root.rglob("*.txt")):
    if txt.name == "cdsfl_core.txt":
        continue
    label = txt.stem
    ALL_DIRECTIVES[label] = txt.read_text(encoding="utf-8")

GEMINI_MODEL = "gemini-3.1-pro-preview"
CX_MODEL = "openai/gpt-5.4"

FOUR_LAYER_SYSTEM = f"""{CDSFL_TEXT}

---

## Interaction Protocol: Combined 4-Layer Schema

You are operating under a combined 4-layer interaction schema. Apply ALL four
layers simultaneously.

### Layer 1 — Meta Structured Prompting (arXiv 2603.01896)
For EVERY claim: STRUCTURED CERTIFICATE, FFAF, SELF-FALSIFICATION, RIGOUR.

### Layer 2 — CDSFL Constraints
The full CDSFL core formal directives above apply.

### Layer 3 — FFAFP with Iterated P-Pass
P-pass your own results up to 5 times or until convergence.

### Layer 4 — Conversational Fallback
Where structured format does not naturally apply, use natural prose.
"""

# Build directive listing
DIRECTIVE_LISTING = "\n\n---\n\n".join(
    f"### {label}\n```\n{text}\n```"
    for label, text in ALL_DIRECTIVES.items()
)

USER_PROMPT = f"""
# Context: Expert Encoding Enrichment — From Thin Constraints to Domain Expertise

## The Problem

The CDSFL framework has 27 domain-specific constraint directives across 9
domains. Here they all are:

{DIRECTIVE_LISTING}

## Assessment

These directives are THIN. They cover hard safety constraints, standards
references, and general verification protocols. They are what you'd get from
reading the first chapter of a standards manual. They are NOT what a real
domain expert with 15 years of experience would write.

What's missing is the EXPERTISE layer — the diagnostic patterns, failure mode
knowledge, heuristics, edge case catalogs, and tacit knowledge that
distinguish a domain expert from someone who has read the manual.

Examples of what a real expert would add:

- A process chemist would know that DIERS two-phase methodology consistently
  overestimates vent sizes for tempered reactions by 20-40%, that the real
  danger is the tempered-to-untempered transition at high conversion, and
  that mixing-sensitive reactions at 5m3 fail due to feed-point micromixing,
  not bulk Re number.

- A mathematician would know that uniform convergence is the hidden assumption
  that breaks most term-by-term integration arguments, that Fubini requires
  absolute integrability (buried in textbook footnotes), and that dominated
  convergence should be reached for before pointwise convergence.

- A structural engineer would know that punching shear around columns is the
  failure mode that kills people in flat-slab buildings, not flexure; that
  progressive collapse analysis matters more than individual member checks;
  and that connection design is where 80% of structural failures originate.

## Your Task

You are being asked to address five questions. Apply FFAFP to all proposals.

### 1. ENRICHMENT STRATEGY

How should we enrich these thin directives into expert-quality encodings?
For each of the 9 domains, identify:

a. What categories of expert knowledge are missing (failure modes, heuristics,
   diagnostic patterns, edge cases, tool-specific expertise, literature
   awareness)?

b. What would a senior practitioner in that domain add that is NOT in the
   current directive? Give concrete examples — not abstract categories, but
   actual domain knowledge.

c. Which of these additions are TOOL-VERIFIABLE (can contribute to S_k gate
   scores) and which require HUMAN JUDGMENT (must be escalated to HIL)?

### 2. SYNTHETIC EXPERTISE QUALITY

You — frontier AI models — have training data spanning the STEM literature.
You can act as synthetic domain experts. But how reliable is that expertise?

a. For which domains in our 27 directives do you have STRONG domain coverage
   (high confidence that your training data includes sufficient expert-level
   material)?

b. For which domains is your coverage WEAK or PATCHY (training data may be
   thin, outdated, or skewed toward textbook content rather than practitioner
   knowledge)?

c. What are the specific FAILURE MODES of synthetic domain expertise? Where
   are you most likely to produce plausible-sounding but subtly wrong
   domain knowledge?

Be honest. This is not a test of your capabilities — it is a calibration
exercise. Overconfidence here directly undermines the system.

### 3. VERIFICATION STATUS FRAMEWORK

We propose a three-tier verification status for expert encodings:

  DRAFT: Model-generated, not yet cross-verified
  CROSS-VERIFIED: Survived multi-model P-pass (minimum 3 models)
  VALIDATED: Reviewed and approved by a human domain expert (HIL)

a. Is this framework sufficient? Should there be additional tiers?

b. For Bench Run 2 (27 tasks across 9 domains), which domains can proceed
   at CROSS-VERIFIED status and which MUST have VALIDATED status before
   operational use?

c. What is the minimum cross-verification protocol for moving from DRAFT
   to CROSS-VERIFIED? How many models? What kind of P-pass? What criteria
   for acceptance?

### 4. ENRICHMENT PROCESS DESIGN

How should the enrichment process itself be structured?

a. Should each model independently draft a rich encoding, then cross-falsify?
   Or should one model draft and others review? Or should models collaborate
   iteratively?

b. How do we detect when synthetic expertise is wrong? What signals indicate
   that a model is producing plausible-but-incorrect domain knowledge?

c. Can the S_k framework itself be used to verify expert encodings? (The
   ouroboros: using the system to improve its own constraint definitions.)

### 5. PRIORITY ORDERING

Given finite time and resources:

a. Which domains should be enriched FIRST for maximum impact on Bench Run 2?

b. Which domains have the highest risk from thin encodings (where getting
   the constraints wrong has the worst consequences)?

c. Propose a concrete ordering for the enrichment work, with rationale.

Apply FFAFP to ALL proposals. P-pass up to 5 times. Only present survivors.
"""


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
        out_path = LOGS_DIR / f"encoding_enrichment_gemini_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"encoding_enrichment_gemini_{ts}.txt"
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
        out_path = LOGS_DIR / f"encoding_enrichment_cx_{ts}.json"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        txt_path = LOGS_DIR / f"encoding_enrichment_cx_{ts}.txt"
        txt_path.write_text(response, encoding="utf-8")
        print(f"[{_ts()}] Codex done ({elapsed:.0f}s, {len(response)} chars)")
        return result
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"[{_ts()}] Codex FAILED after {elapsed:.0f}s: {e}")
        return {"model": "Codex", "error": str(e), "elapsed_s": round(elapsed, 1)}


def main():
    print("=" * 60)
    print("CDSFL Confer: Expert Encoding Enrichment")
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
