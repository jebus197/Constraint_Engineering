#!/usr/bin/env python3
"""
Full 5-Model Panel Review: §17 Feedback Channel + §18 Divergence Directive
==========================================================================

All five panel models review the coupled work landed in the last 24 hours:

1. §17 — Feedback Channel (critic / severe-tests arm)
2. §18 — Divergence Directive (generator / bold-conjectures arm)
3. The decision to defer R_k wiring of the divergence penalty

Date:     15 April 2026
Protocol: CDSFL + FFAFP
Models:   Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Claude Opus 4.6),
          ChatGPT GPT-5.4, DeepSeek R1-0528
Dispatch: parallel via ThreadPoolExecutor (max_workers=5)
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    call_claude_cli,
    call_gemini,
    call_openrouter,
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

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_divergence_directive"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("gemini",   "gemini-3.1-pro-preview",     "gemini_native"),
    ("codex",    "openai/gpt-5.4",             "openrouter"),
    ("cc2",      "opus",                       "claude_cli"),
    ("chatgpt",  "openai/gpt-5.4",             "openrouter"),
    ("deepseek", "deepseek/deepseek-r1-0528",  "openrouter"),
]

# ---------------------------------------------------------------------------
# Load artefacts
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

OPERATIONAL_PATH = (
    REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
)
OPERATIONAL_TEXT = OPERATIONAL_PATH.read_text(encoding="utf-8")

DIVERGENCE_CODE = (
    REPO_ROOT / "bench" / "dm" / "_divergence.py"
).read_text(encoding="utf-8")

FEEDBACK_CODE = (
    REPO_ROOT / "bench" / "dm" / "_feedback.py"
).read_text(encoding="utf-8")

DIVERGENCE_TESTS = (
    REPO_ROOT / "bench" / "tests" / "test_divergence_directive.py"
).read_text(encoding="utf-8")


def extract_section(text: str, start_marker: str, end_marker: str | None = None) -> str:
    """Extract a section of the operational directive by string match."""
    start = text.find(start_marker)
    if start == -1:
        return f"[SECTION NOT FOUND: {start_marker!r}]"
    if end_marker:
        end = text.find(end_marker, start + len(start_marker))
        return text[start:end] if end != -1 else text[start:]
    # Default: read ~160 lines
    chunk = text[start:]
    lines = chunk.splitlines()[:160]
    return "\n".join(lines)


SEC_17 = extract_section(OPERATIONAL_TEXT, "## §17", "## §18")
SEC_18 = extract_section(OPERATIONAL_TEXT, "## §18 Divergence Directive")


# ---------------------------------------------------------------------------
# Confer prompt
# ---------------------------------------------------------------------------

CONFER_PROMPT = f"""\
# 5-Panel CDSFL/FFAFP Review — §17 Feedback Channel + §18 Divergence Directive

You are one of five frontier models being asked to review two coupled pieces
of work landed in the last 24 hours on the CDSFL (Constraint-Driven Structured
Falsification Loop) framework. Your review runs under **CDSFL directives
(system prompt) + FFAFP protocol (below)**.

## Context — the missing symmetry

Karl Popper's method has two arms: **bold conjectures** and **severe tests**.
CDSFL has, until now, developed the severe-tests arm to a ferocious degree —
the falsification pipeline, the admissibility gates, cross-model
corroboration, tool enforcement. The bold-conjectures arm was implicit,
inherited from whatever the models happened to produce unprompted.

Two interventions, one day apart, close that asymmetry:

* **§17 Feedback Channel** (landed earlier 15 April): closes the
  measurement-to-correction loop. The schema's per-round judgment (B-Cell
  verdicts, FFAFP admissibility, near-duplicate detection, R_k discrepancies)
  was previously logged and discarded — models never saw it and could
  resubmit the same refuted claim unchanged. §17 routes that judgment into
  round K+1's prompt as imperative per-model feedback.

* **§18 Divergence Directive** (landed later 15 April): closes the
  generation-side gap. Every non-trivial finding must now supply either
  (a) ≥1 alternative differing from the primary on a named dimension —
  mechanism, assumption, scope, timescale, or tradeoff — or (b) a scoped
  null-alternative justification. Cosmetic rewordings are rejected by an
  isomorphism check (Jaccard MVP) and incur a double penalty.

§17 is the critic. §18 is the generator. The project's originator framed
CDSFL as an "invention engine" inspired by the unresolved *Lance McLane*
sci-fi cartoon strip — this pair of directives is the explicit engineering
of that intuition.

The directive multiplier on R_k (1.0 / 0.85 / 0.70 / 0.60 per tier) is
**exposed as a library function but not yet wired into `compute_rk()`**.
Reason: Exp 39 baseline (§17 only) and Exp 40 (§17 + §18) are intended to
isolate each intervention's signal cleanly before penalty calibration.

---

## §17 directive (full text)

{SEC_17}

---

## §18 directive (full text)

{SEC_18}

---

## §17 implementation — `bench/dm/_feedback.py`

```python
{FEEDBACK_CODE}
```

---

## §18 implementation — `bench/dm/_divergence.py`

```python
{DIVERGENCE_CODE}
```

---

## §18 tests — `bench/tests/test_divergence_directive.py` (52 tests, all green; full regression 912/912)

```python
{DIVERGENCE_TESTS}
```

---

## Five explicit review questions

Please answer each under **FFAFP** (Find, Follow, Analyse, Fix, P-pass):

### Q1 — Is the dimension set (mechanism / assumption / scope / timescale / tradeoff) sufficient and non-overlapping?

Are five dimensions too few, too many, well-carved? Is "tradeoff" secretly a
hyperset of the others? Is "mechanism" ambiguous with "assumption" at
implementation-level? Under what class of problem does the carving leak?

### Q2 — Is Jaccard-over-stopword-filtered-token-sets an adequate isomorphism metric for MVP?

The module uses Jaccard on normalised token sets with a default threshold of
0.85. Consider:

* False positives: reject genuine alternatives that happen to share vocabulary
  (e.g. "Newton method with Hessian" vs "quasi-Newton with BFGS approximation
  of Hessian" — different algorithms, heavy lexical overlap).
* False negatives: accept cosmetic rewordings that paraphrase (e.g. "CG
  descent" vs "iterative conjugate-direction minimisation").
* Stopword list is minimal and English-only — domain-specific function words
  (e.g. "theorem", "lemma", "proof" in maths) inflate overlap.

Should the MVP ship with Jaccard, or should it ship disabled until
sentence-transformer embeddings land in Phase 2?

### Q3 — Are the penalty tiers (1.0 / 0.85 / 0.70 / 0.60) coherent with the rest of the R_k equation?

The divergence penalty is defined but unwired. Consider:

* When wired in as a pre-factor, does 0.60 for isomorphism-only risk
  dominating genuine corroboration signal at small round counts?
* Does 0.85 for "engaged but failed" under-penalise the case where a model
  games the directive by submitting one dimension-tagged but low-quality
  alternative per finding?
* Is "null-justification too short" really at the same severity tier as
  "missing dimension"?

### Q4 — Does the sequencing plan (Exp 39 baseline §17, Exp 40 §17+§18) actually isolate the signal, or do §17 and §18 interact confoundingly?

The interaction section in §18 says prior-round refuted alternatives
resurfacing unchanged are treated as resubmitted flagged findings per §17.
That means §17 absorbs part of §18's enforcement. If §17 is already
suppressing repeated refuted claims (which include prior alternatives), can
we attribute novelty-yield delta cleanly to §18 alone? If not, what is the
right factorial experimental design?

### Q5 — P-pass the whole pair

What is the most plausible scenario under which §17 + §18 make CDSFL *worse*
— either by measurably degrading R_k / nu_k, by triggering compliance-theatre
in models, or by collapsing to a degenerate equilibrium (e.g. all models
learn to emit the same "safe" alternative shape)?

---

## Format — structure your response as:

1. **FIND** — concrete issues, with file/line references where possible
2. **FOLLOW** — downstream consequences of each issue
3. **ANALYSE** — classify each issue HARD (mathematical, structural, safety)
   vs SOFT (calibration, naming, style)
4. **FIX** — simplest sufficient correction per issue
5. **P-PASS** — actively falsify your own recommendations

Cite specific code lines, directive paragraphs, or equations where
applicable. If the design is sound as-is, state which properties you
verified and how. If you find no issues in a question, say so explicitly —
do not fabricate critique for its own sake.

Under 2500 words. Prioritise precision over completeness.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def dispatch_model(label: str, model_id: str, api: str) -> dict:
    """Dispatch to one model and return result dict."""
    t0 = time.monotonic()
    print(f"  [{label}] dispatching ({model_id} via {api})...", flush=True)

    try:
        if api == "gemini_native":
            response = call_gemini(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=300,
                max_retries=5,
                backoff_base=3.0,
            )
        elif api == "claude_cli":
            response = call_claude_cli(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=900,
                max_retries=1,
            )
        elif api == "openrouter":
            response = call_openrouter(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=CONFER_PROMPT,
                max_tokens=32768,
                timeout=300,
                max_retries=3,
            )
        else:
            raise ValueError(f"Unknown API: {api}")

        elapsed = time.monotonic() - t0
        print(
            f"  [{label}] responded in {elapsed:.1f}s ({len(response)} chars)",
            flush=True,
        )
        return {
            "model": model_id,
            "label": label,
            "api": api,
            "response": response,
            "time_s": round(elapsed, 1),
            "chars": len(response),
        }

    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"  [{label}] FAILED after {elapsed:.1f}s: {e}", flush=True)

        # Fallback: Gemini native → OpenRouter
        if api == "gemini_native":
            print(f"  [{label}] falling back to Gemini via OpenRouter...", flush=True)
            try:
                t0b = time.monotonic()
                response = call_openrouter(
                    model_id="google/gemini-3.1-pro",
                    system_prompt=CDSFL_TEXT,
                    user_prompt=CONFER_PROMPT,
                    max_tokens=32768,
                    timeout=300,
                    max_retries=3,
                )
                elapsed2 = time.monotonic() - t0b
                print(
                    f"  [{label}] (OpenRouter fallback) responded in {elapsed2:.1f}s "
                    f"({len(response)} chars)",
                    flush=True,
                )
                return {
                    "model": "google/gemini-3.1-pro (via OpenRouter fallback)",
                    "label": label,
                    "api": "openrouter_fallback",
                    "response": response,
                    "time_s": round(elapsed + elapsed2, 1),
                    "chars": len(response),
                }
            except Exception as e2:
                print(f"  [{label}] OpenRouter fallback also FAILED: {e2}", flush=True)

        return {"label": label, "error": str(e), "time_s": round(elapsed, 1)}


def run_confer() -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'=' * 72}")
    print("  5-PANEL CONFER: §17 Feedback Channel + §18 Divergence Directive")
    print(f"  Timestamp: {ts}")
    print("  Protocol: CDSFL + FFAFP")
    print("  Models: ge, cx, cc2, cgpt, ds (parallel)")
    print(f"{'=' * 72}\n")

    results: dict[str, dict] = {}

    # Parallel dispatch
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(dispatch_model, label, model_id, api): label
            for label, model_id, api in MODELS
        }
        for future in concurrent.futures.as_completed(futures):
            label = futures[future]
            try:
                result = future.result()
            except Exception as e:
                result = {"label": label, "error": f"future exception: {e}"}
            results[label] = result

            log_path = LOGS_DIR / f"{label}_{ts}.json"
            log_path.write_text(
                json.dumps(result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"  saved: {log_path}", flush=True)

    combined_path = LOGS_DIR / f"combined_{ts}.json"
    combined_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n  combined log: {combined_path}", flush=True)

    return results


if __name__ == "__main__":
    run_confer()
