#!/usr/bin/env python3
"""
Round-2 Convergence Confer: §17 + §18 Divergence Resolution
===========================================================

Round 1 (bench/confer_divergence_directive.py) produced 5-panel responses
with consensus on core findings but genuine divergence on three axes:

  D1: Jaccard threshold — raise / lower / reframe / ship-and-log / fine-as-is
  D2: Penalty tiers — keep / flatten / mild / gated / recidivism-add
  D3: Experimental design — 2×2 factorial / accept coupling / attribute-tag

Round 2 charge: USE the CDSFL Stage 6 mathematical framework (R_k(i),
η_combined = η_int · (1 − c_ext · (1 − ν_k)), continuous suppression,
the ν_k / c_ext / R_k channel orthogonality) to REACH convergence on a
single definitive answer per divergence. The answer may be a synthesis of
what was already offered, OR an entirely novel solution. Constraints:

  (i)  scientific rigour must be preserved
  (ii) detectability of genuine novelty must be preserved
  (iii) trade as little of (i)+(ii) as possible for anything else

Date:     15 April 2026
Protocol: CDSFL + FFAFP
Models:   Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4, DeepSeek R1
Dispatch: parallel via ThreadPoolExecutor(max_workers=5)
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_divergence_round2_convergence"
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

# Load the round-1 combined log so we carry every model's own prior position.
R1_LOG_PATH = (
    REPO_ROOT
    / "bench"
    / "logs"
    / "confer_divergence_directive"
    / "combined_20260415T220231Z.json"
)
R1_DATA = json.loads(R1_LOG_PATH.read_text(encoding="utf-8"))


def _r1_response(label: str) -> str:
    entry = R1_DATA.get(label, {})
    return entry.get("response", f"[MISSING: round-1 response for {label}]")


# ---------------------------------------------------------------------------
# Math context (Stage 6 — verbatim relevant sections)
# ---------------------------------------------------------------------------

STAGE6_MATH = r"""
## CDSFL Stage 6 — Unified Self-Assessment Equation (canonical)

### Recursive state (Stage 4–5 core)

    R_k(i) = R_k(i-1) · (1 − q) / (1 − q · R_k(i-1))
    q     = η · d · p                        (effective detection)

Three-phase per cycle:
    Phase 1 (detection):    R_det  = R_old · (1 − q) / (1 − q · R_old)
    Phase 2 (resolution):   R_base = σ · R_det + (1 − σ) · R_old
    Phase 3 (re-injection): R_k(i) = R_base · (1 − ν) + ν

    σ = fix efficacy, ν = re-injection rate (NB: ν is re-injection here,
    NOT to be confused with ν_k literature novelty below).

Break-even re-injection:  ν*  = σ · R · q / (1 − q · R · (1 − σ))
If ν > ν* the cycle is net harmful — HARD exit.

### Stage 6 — η decomposition (literature-calibrated novelty)

    η_combined = η_int · (1 − c_ext · (1 − ν_k))

where:
    η_int  ∈ [0,1]  internal novelty (within session, existing _finding_similarity)
    ν_k    ∈ [0,1]  literature novelty (per-finding, O1/Ouroboros cell)
    c_ext  ∈ [0,1]  source diversity corroboration = 1 − Π_s (1 − c_s)

### Orthogonality (CRITICAL — load-bearing constraint)

    R_k    measures VALIDITY       (Bayesian posterior of residual risk)
    ν_k    measures NOVELTY        (literature calibration)
    c_ext  measures SEARCH QUALITY (corroboration product over sources)

These three are independent reporting dimensions and must NEVER be
collapsed into a single score before reporting. The η_combined formula
projects (ν_k, c_ext) into a scalar for the state equation only; the
raw triple (ν_k, c_ext, H/H_max) is always retained for interpretation.

Boundary conditions (SymPy + Wolfram verified, 14 April 2026):
    ν_k = 1              → η_combined = η_int              (novel, no penalty)
    ν_k = 0, c_ext = 1   → η_combined = 0                  (known + coverage)
    ν_k = 0, c_ext = 0   → η_combined = η_int              (no evidence: degrade)
    c_ext = 0            → Stage 6 reduces to Stage 5      (graceful degradation)

Monotonicity (Wolfram confirmed):
    ∂η/∂ν_k   = c_ext · η_int > 0    (more novelty strengthens detection)
    ∂η/∂c_ext = η_int · (ν_k − 1) < 0 when ν_k < 1
                                     (more coverage penalises non-novel harder)

### Continuous suppression w(f) — separate channel

    w(f) = max(exp(−λ_s · Σ_{g ∈ TopK(f, G)} sim(f, g)), w_floor)
    λ_s = 1.5, w_floor = 0.05, k = 3

CRITICAL CONSTRAINT (Error 1, 12 April 2026, 113× residual-risk overestimate):
    w(f) MUST NEVER enter q_eff in the Bayesian update.
    Applies to: kappa_set numerator, report ordering, triage priority.
    Does NOT apply to: q_eff, R_k(i), Bayesian posterior, kappa_set denominator.

### Similarity backend (§1.3)

    s(f1, f2) = (1 − β) · content_sim(f1, f2) + β · b_class(f1, f2)
    β = 0.2, b_class = 0.3 if same flaw_class else 0
    s ∈ [0, 0.86] by construction (no two findings score 1.0 — even same-class)

    content_sim (primary) = (cos(emb(f1), emb(f2)) + 1) / 2       (MiniLM-L6-v2)
    content_sim (fallback) = 0.6 · J_unigram + 0.4 · J_bigram     (Jaccard)

### kappa_set (convergence metric, §7.13)

    kappa_set(r) = 1 − Σ(w_c · Sev_novel_c) / (Σ Sev_cumulative + ε)

Numerator: weighted by w(f) per class (conservative = least-suppressed member).
Denominator: RAW severity, unweighted. (Phase 1 fix, 12 April 2026.)

### Substrate ceiling

    lim_{n→∞} R_{n,k} ≥ ν_k       (re-injection rate, NOT literature novelty)

### Empirical calibration base-rate

Experiments 12–37 empirically: 0–13% of model-submitted findings survive
independent falsification without structural admissibility enforcement.
FFAFP (§1.2) closes this gap.
"""

# ---------------------------------------------------------------------------
# The three divergences (explicit positions)
# ---------------------------------------------------------------------------

DIVERGENCES = """
## The three divergences from round 1

### D1 — Jaccard threshold for §18 isomorphism detection

  Gemini    raise to 0.95               (protect genuine math from FP rejection)
  DeepSeek  lower to 0.75               (catch more duplicates)
  Codex     threshold is not the fix    (reframe semantic claim + add sibling check)
  ChatGPT   threshold is not the fix    (first-pass flag + contrast-marker exemption)
  CC2       ship at 0.85 with logging   (recalibrate from empirical FP/FN rates)

### D2 — Penalty tier structure (1.0 / 0.85 / 0.70 / 0.60)

  Gemini    gated 0.85 / 0.98           (near-perfect lexical match → 0.60; else 0.85)
  Codex     lower 0.60 → 0.85           (evidence is lexical-only, reserve harshness)
  ChatGPT   milder 1.0/0.90/0.80/0.70   (or apply penalty to novelty channel only)
  CC2       keep as-is                  (0.60 correctly harsh; add min_tokens=15)
  DeepSeek  wire post-Exp 40 + recidivism 0.50
                                        (escalate for repeated low-quality alt)

### D3 — Experimental design for signal isolation

  Codex     2×2 factorial (A/B/C/D)     (§17 × §18 main effects and interaction)
  ChatGPT   2×2 factorial               (rename claim if single-arm; run-level randomise)
  DeepSeek  Exp 39 + 40 + 41            (add §18-only arm to isolate generator)
  Gemini    §18-only is invalid         (structurally coupled; falsified own Exp 39b)
  CC2      soft confound, tag source   (correction_source = {§17 | §18 | ambiguous})
"""

# ---------------------------------------------------------------------------
# Charge
# ---------------------------------------------------------------------------

CHARGE = """
## The round-2 charge

You are being asked to CONVERGE, not to restate. You have:

  - your own round-1 position on each divergence (below, full text)
  - the other four models' round-1 positions (below, full text)
  - the CDSFL Stage 6 mathematical framework (above, canonical)

Use the framework to produce a SINGLE DEFINITIVE ANSWER per divergence.
The answer may be:

  (a) a synthesis of existing positions (name the ones you combine and why);
  (b) an ENTIRELY NOVEL solution that none of the five offered (preferred if
      the framework supports it — that is the whole point of §18);
  (c) a structural argument that one position subsumes all others under the
      Stage 6 math (state which, and prove via the equations above).

Binding constraints (non-negotiable, enforced by the math):

  C1 — ν_k, c_ext, R_k orthogonality must be preserved. Any mechanism that
       collapses novelty into validity (or vice versa) is REJECTED.
  C2 — w(f) must NOT enter q_eff. Error 1 from 12 April 2026.
  C3 — detectability of genuine novelty must be preserved. Any mechanism
       that makes genuinely novel alternatives indistinguishable from
       compliance theatre is REJECTED.
  C4 — scientific rigour must be preserved. FFAFP admissibility set (§1.2)
       and the 0–13% empirical base-rate must be respected.

Hint (not a spoiler — verify for yourself): the §18 directive is
generator-side enforcement. In Stage 6, the generator channel is η — split
into η_int (within-session) and ν_k (cross-literature) via η_combined =
η_int · (1 − c_ext · (1 − ν_k)). The validity channel is R_k(i). The
convergence-metric channel is w(f). Ask where each divergence's answer
mathematically belongs.

### Structural question to answer first

Where in the Stage 6 math does the divergence multiplier (currently a
"pre-factor on R_k contribution" per the §18 implementation) actually
belong? Your answer to this determines everything downstream — threshold
calibration, penalty severity, factorial design.

Possible answers:
  (i)   pre-factor on R_k(i) (validity channel — current spec)
  (ii)  modulator of η_int in η_combined (novelty channel, internal)
  (iii) modulator of ν_k (novelty channel, literature — would require O1)
  (iv)  modulator of w(f) in kappa_set (convergence metric only)
  (v)   admissibility gate (FFAFP, S_min — binary, outside R_k)
  (vi)  some combination — specify channels explicitly.

Argue via the math, not via prose intuition.

### Then answer D1, D2, D3

Given your answer to the structural question, resolve:

  D1 — isomorphism metric + threshold (and/or additional detectors)
  D2 — penalty tier structure (numbers, channel, when wired)
  D3 — experimental design

Each D-answer must derive from the structural answer. If D1 is a novelty-
channel problem, threshold calibration follows tau_sim methodology (§1.3).
If D2 is a channel-assignment problem, the penalty numbers become less
important than the channel. If D3 is an orthogonality question (§17 and
§18 act on different channels), factorial decomposition is mathematically
natural, not optional.

### Format

Structure your response as:

  1. STRUCTURAL  — where does the multiplier belong? (answer the six-way
                   question above; cite Stage 6 equations by name)
  2. D1          — definitive Jaccard / isomorphism answer
  3. D2          — definitive penalty tier answer
  4. D3          — definitive experimental design answer
  5. CONVERGENCE — identify which of the 5 positions (incl. your own)
                   is now subsumed by your answer, and which must be
                   explicitly dropped
  6. P-PASS      — falsify your own definitive answer against C1-C4

Under 2000 words. Precision over prose. If you cannot converge — if the
math genuinely does not disambiguate — say so, and name the unresolved
residue precisely.
"""

# ---------------------------------------------------------------------------
# Build per-model prompts (each model sees its own round-1 response framed as
# "your position" and the other four framed as "other models' positions")
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
    self_resp = _r1_response(self_label)
    others = [lbl for lbl in ["gemini", "codex", "cc2", "chatgpt", "deepseek"] if lbl != self_label]

    other_block_parts = []
    for lbl in others:
        disp = LABEL_DISPLAY[lbl]
        resp = _r1_response(lbl)
        other_block_parts.append(f"### {disp} — round 1\n\n{resp}")
    other_block = "\n\n---\n\n".join(other_block_parts)

    return f"""\
# Round-2 CDSFL/FFAFP Convergence Confer — §17 + §18 Divergence Resolution

You ({self_display}) and four other frontier models reviewed §17 Feedback
Channel + §18 Divergence Directive in round 1. Consensus was reached on
core findings. The panel diverged on three axes. The founder's charge for
round 2 is to reach FULL CONVERGENCE on a single definitive answer per
divergence, using the CDSFL Stage 6 mathematical framework as the
arbiter.

---

{STAGE6_MATH}

---

{DIVERGENCES}

---

## Your own round-1 response (verbatim)

{self_resp}

---

## The other four models' round-1 responses (verbatim, in full)

{other_block}

---

{CHARGE}
"""


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def dispatch_model(label: str, model_id: str, api: str) -> dict:
    """Dispatch to one model and return result dict."""
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

        # Fallback: Gemini native → OpenRouter
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
    print("  ROUND-2 CONVERGENCE CONFER: §17 + §18 Divergence Resolution")
    print(f"  Timestamp: {ts}")
    print("  Protocol: CDSFL + FFAFP, Stage 6 math as arbiter")
    print("  Models: ge, cx, cc2, cgpt, ds (parallel)")
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
