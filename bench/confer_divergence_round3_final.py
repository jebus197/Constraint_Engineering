#!/usr/bin/env python3
"""
Round-3 Final Review: §18 Divergence Directive — Implementation Verification
=============================================================================

Round 2 converged 5/5 unanimous on all three divergences (D1, D2, D3) and on
the structural channel-assignment question. The round-2 consensus has been
implemented in bench/dm/_divergence.py, verified by 75 pytest tests (0 fail),
cross-checked by SymPy/z3 (38/38 pass), and linted clean by ruff + mypy.

Round 3 charge: REVIEW THE IMPLEMENTED CODE against the round-2 consensus.
Confirm that the implementation matches the agreed-upon mathematical model,
or identify any deviation. Each model must use the CDSFL Stage 6 math as the
sole arbiter. Full convergence is required.

Date:     16 April 2026
Protocol: CDSFL + FFAFP
Models:   Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4,
          DeepSeek R1-0528
Dispatch: parallel via ThreadPoolExecutor(max_workers=5)
"""

from __future__ import annotations

import concurrent.futures
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (  # noqa: E402
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
            import os  # noqa: E402
            os.environ.setdefault(_k, _v)

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_divergence_round3_final"
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

# Load the round-2 combined log so each model can see the unanimous decision.
R2_LOG_DIR = REPO_ROOT / "bench" / "logs" / "confer_divergence_round2_convergence"
_r2_combined_candidates = sorted(R2_LOG_DIR.glob("combined_*.json"))
if _r2_combined_candidates:
    R2_LOG_PATH = _r2_combined_candidates[-1]  # latest
    R2_DATA = json.loads(R2_LOG_PATH.read_text(encoding="utf-8"))
else:
    R2_DATA = {}

# Load the implementation source code (the models review the actual code).
_divergence_path = REPO_ROOT / "bench" / "dm" / "_divergence.py"
IMPL_CODE = _divergence_path.read_text(encoding="utf-8")

# Load the verification results.
_verify_path = REPO_ROOT / "bench" / "verify_round2_implementation.py"
VERIFY_CODE = _verify_path.read_text(encoding="utf-8")

# Load the updated §18 directive text.
_operational_path = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
_operational_text = _operational_path.read_text(encoding="utf-8")
# Extract §18 section only.
_s18_start = _operational_text.find("## §18 Divergence Directive")
_s18_end = _operational_text.find("\n---", _s18_start + 1)
if _s18_end == -1:
    _s18_end = len(_operational_text)
S18_TEXT = _operational_text[_s18_start:_s18_end].strip()

# ---------------------------------------------------------------------------
# Math context (Stage 6 — canonical, same as round-2)
# ---------------------------------------------------------------------------

STAGE6_MATH = r"""
## CDSFL Stage 6 — Unified Self-Assessment Equation (canonical)

### Recursive state (Stage 4-5 core)

    R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))
    q     = eta * d * p                        (effective detection)

### Stage 6 -- eta decomposition (literature-calibrated novelty)

    eta_combined = eta_int * (1 - c_ext * (1 - nu_k))

where:
    eta_int  in [0,1]  internal novelty (within session)
    nu_k     in [0,1]  literature novelty (per-finding, O1/Ouroboros cell)
    c_ext    in [0,1]  source diversity corroboration = 1 - prod_s (1 - c_s)

### Orthogonality (CRITICAL -- load-bearing constraint)

    R_k    measures VALIDITY       (Bayesian posterior of residual risk)
    nu_k   measures NOVELTY        (literature calibration)
    c_ext  measures SEARCH QUALITY (corroboration product over sources)

These three are independent reporting dimensions and must NEVER be
collapsed into a single score before reporting.

### Continuous suppression w(f) -- separate channel

    w(f) = max(exp(-lambda_s * sum TopK sim), w_floor)
    CRITICAL: w(f) MUST NEVER enter q_eff in the Bayesian update.

### kappa_set (convergence metric)

    kappa_set(r) = 1 - sum(w_c * Sev_novel_c) / (sum Sev_cumulative + eps)
    Numerator: weighted by w(f). Denominator: RAW severity, unweighted.

### Divergence modulator channel assignment (round-2 5/5 unanimous)

    m_div in {1.00, 0.85, 0.70, 0.60}   (eta_int modulation tiers)
    eta_int_modulated = m_div * eta_int
    eta_combined = eta_int_modulated * (1 - c_ext * (1 - nu_k))
    q = eta_combined * d * p
    R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))

    FORBIDDEN: m_div as pre-factor on R_k.
    FORBIDDEN: m_div counting toward nu_k.
    FORBIDDEN: w(f) in q_eff.
"""

# ---------------------------------------------------------------------------
# Round-2 consensus summary
# ---------------------------------------------------------------------------

R2_CONSENSUS = """
## Round-2 unanimous consensus (all five models)

STRUCTURAL: The divergence multiplier belongs on eta_int (internal novelty
channel). It is forbidden from acting as a direct pre-factor on R_k,
forbidden from entering q as a free factor outside eta_int, and
forbidden from crediting nu_k.

D1 (isomorphism metric + threshold):
- Keep Jaccard threshold at 0.85 as a lexical near-duplicate heuristic
  (not semantic equivalence).
- Add mandatory contrast statement ("Differs from primary: ...").
- Add sibling alt-vs-alt isomorphism check (ship-blocker): later
  sibling demoted if Jaccard >= 0.85 against any earlier sibling.
- Embedding backend (sentence-transformers) is a follow-up, not a blocker.

D2 (penalty tiers):
- Four tiers: 1.00 (compliant), 0.85 (soft: engaged but failed gate),
  0.70 (hard: no engagement), 0.60 (severe: near-copy J>=0.98, all
  isomorphic, or recidivism).
- Channel: multiply eta_int, never R_k directly.
- Function renamed to eta_int_modulator (legacy alias retained).

D3 (experimental design):
- 2x2 factorial (feedback x divergence) is the correct design, with
  correction_source tagging for attribution analysis.
- This is deferred to Exp 40 planning, not the implementation concern.
"""

# ---------------------------------------------------------------------------
# Charge
# ---------------------------------------------------------------------------

CHARGE = """
## Round-3 charge: IMPLEMENTATION REVIEW

You have:
  - The CDSFL Stage 6 mathematical framework (above, canonical)
  - The round-2 unanimous consensus (above)
  - The FULL implementation source code of bench/dm/_divergence.py (below)
  - The updated section 18 directive text from cdsfl_operational.md (below)
  - The SymPy/z3 cross-check script and its results: 38/38 pass (below)
  - 75 pytest tests: 75 pass, 0 fail
  - ruff: clean; mypy: clean

Your charge:

  1. VERIFY that the implementation correctly encodes the round-2 consensus.
     For each D1/D2/D3 + structural decision, check the code implements it.

  2. VERIFY that the channel-assignment invariant is maintained:
     m_div multiplies eta_int; it does not pre-multiply R_k; it does not
     enter q as a free factor; it does not credit nu_k.

  3. VERIFY that the SymPy/z3 cross-check script adequately tests the
     load-bearing claims, or identify gaps.

  4. IDENTIFY any remaining deviations, bugs, or ambiguities.

  5. P-PASS your own review against the Stage 6 math.

### Format

  1. STRUCTURAL VERIFY  -- does the code implement the channel assignment?
  2. D1 VERIFY          -- contrast, sibling check, threshold
  3. D2 VERIFY          -- four tiers, eta_int target, backward compat
  4. D3 VERIFY          -- design is documented, deferred correctly
  5. CROSS-CHECK GAPS   -- any missing verification claims?
  6. BUGS / DEVIATIONS  -- any code issues?
  7. VERDICT            -- CONVERGE (implementation matches consensus) or
                           DIVERGE (name the specific issue)
  8. P-PASS             -- falsify your own review

Under 1500 words. Precision over prose.
"""

# ---------------------------------------------------------------------------
# Build per-model prompts
# ---------------------------------------------------------------------------

LABEL_DISPLAY = {
    "gemini":   "Gemini 3.1 Pro",
    "codex":    "Codex GPT-5.4",
    "cc2":      "CC2 (Claude Opus 4.6)",
    "chatgpt":  "ChatGPT GPT-5.4",
    "deepseek": "DeepSeek R1-0528",
}


def build_prompt(self_label: str) -> str:
    self_display = LABEL_DISPLAY[self_label]

    return f"""\
# Round-3 CDSFL/FFAFP Final Review: §18 Divergence Implementation Verification

You ({self_display}) and four other frontier models converged unanimously in
round 2 on the channel-assignment question and on D1/D2/D3. The consensus has
been implemented. This is the final review: does the implementation match?

---

{STAGE6_MATH}

---

{R2_CONSENSUS}

---

## Implementation: bench/dm/_divergence.py (FULL SOURCE)

```python
{IMPL_CODE}
```

---

## Updated §18 directive text (cdsfl_operational.md)

{S18_TEXT}

---

## SymPy/z3 cross-check script (FULL SOURCE)

```python
{VERIFY_CODE}
```

Cross-check result: 38/38 checks passed, 0 failed.
pytest result: 75 passed (52 legacy + 23 round-2 new), 0 failed.
Full suite: 935 passed, 0 failed.
ruff: clean. mypy: clean.

---

{CHARGE}
"""


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def dispatch_model(label: str, model_id: str, api: str) -> dict:
    t0 = time.monotonic()
    prompt = build_prompt(label)
    print(
        f"  [{label}] dispatching ({model_id} via {api}, "
        f"prompt={len(prompt)} chars)...",
        flush=True,
    )

    try:
        if api == "gemini_native":
            response = call_gemini(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=prompt,
                max_tokens=32768,
                timeout=300,
                max_retries=5,
                backoff_base=3.0,
            )
        elif api == "claude_cli":
            response = call_claude_cli(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=prompt,
                max_tokens=32768,
                timeout=900,
                max_retries=1,
            )
        elif api == "openrouter":
            response = call_openrouter(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=prompt,
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
            "prompt_chars": len(prompt),
        }

    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"  [{label}] FAILED after {elapsed:.1f}s: {e}", flush=True)

        if api == "gemini_native":
            print(
                f"  [{label}] falling back to Gemini via OpenRouter...",
                flush=True,
            )
            try:
                t0b = time.monotonic()
                response = call_openrouter(
                    model_id="google/gemini-3.1-pro",
                    system_prompt=CDSFL_TEXT,
                    user_prompt=prompt,
                    max_tokens=32768,
                    timeout=300,
                    max_retries=3,
                )
                elapsed2 = time.monotonic() - t0b
                print(
                    f"  [{label}] (OpenRouter fallback) responded in "
                    f"{elapsed2:.1f}s ({len(response)} chars)",
                    flush=True,
                )
                return {
                    "model": "google/gemini-3.1-pro (via OpenRouter fallback)",
                    "label": label,
                    "api": "openrouter_fallback",
                    "response": response,
                    "time_s": round(elapsed + elapsed2, 1),
                    "chars": len(response),
                    "prompt_chars": len(prompt),
                }
            except Exception as e2:
                print(
                    f"  [{label}] OpenRouter fallback also FAILED: {e2}",
                    flush=True,
                )

        return {"label": label, "error": str(e), "time_s": round(elapsed, 1)}


def run_confer() -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'=' * 72}")
    print("  ROUND-3 FINAL REVIEW: §18 Divergence Implementation Verification")
    print(f"  Timestamp: {ts}")
    print("  Protocol: CDSFL + FFAFP, Stage 6 math as arbiter")
    print("  Models: ge, cx, cc2, cgpt, ds (parallel)")
    print("  Charge: verify implementation matches round-2 consensus")
    print(f"{'=' * 72}\n")

    results: dict[str, dict] = {}

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
