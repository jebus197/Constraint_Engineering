#!/usr/bin/env python3
"""
Exp 40 Pre-launch Panel Review — Round 2B of 3
==============================================

Five-model yield-or-refute follow-up to Round 2A. Each model receives
the four other models' verbatim Round 2A answers and must, on each
divergent point:

  (1) YIELD WITH EXPLICIT REASONS — which model, what in their reasoning
      made you change position, why their reasoning is stronger.

  (2) REFUTE WITH EXPLICIT REASONS — which model, what in their
      reasoning is wrong or incomplete, why your position is stronger.

Mechanical check (Gemini's proposal, adopted for Round 2B): any yield
quote must be a LITERAL SUBSTRING of the cited model's Round 2A output.
If it is not, the runner post-processing classifies the yield as a
compliance yield.

Protocol: CDSFL + FFAFP, Stage 6 math as arbiter, compelled convergence,
          no qualitative opt-out.
Models:   Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4,
          DeepSeek R1-0528
Dispatch: parallel via ThreadPoolExecutor(max_workers=5)

Round 2A source: confer_exp40_prelaunch_round2a, timestamp loaded at runtime.
"""

from __future__ import annotations

import concurrent.futures
import glob
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_prelaunch_round2b"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

R2A_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_prelaunch_round2a"

MODELS = [
    ("gemini",   "gemini-3.1-pro-preview",     "gemini_native"),
    ("codex",    "openai/gpt-5.4",             "openrouter"),
    ("cc2",      "opus",                       "claude_cli"),
    ("chatgpt",  "openai/gpt-5.4",             "openrouter"),
    ("deepseek", "deepseek/deepseek-r1-0528",  "openrouter"),
]

LABEL_DISPLAY = {
    "gemini":   "Gemini 3.1 Pro",
    "codex":    "Codex GPT-5.4",
    "cc2":      "CC2 (Claude Opus 4.6)",
    "chatgpt":  "ChatGPT GPT-5.4",
    "deepseek": "DeepSeek R1-0528",
}

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Load Round 2A responses
# ---------------------------------------------------------------------------

def _load_round2a() -> dict[str, str]:
    """Return {label: response_text} for all 5 Round 2A models (latest timestamp)."""
    combined_files = sorted(R2A_DIR.glob("combined_*.json"))
    if not combined_files:
        raise FileNotFoundError(f"No Round 2A combined log found in {R2A_DIR}")
    latest = combined_files[-1]
    data = json.loads(latest.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for label, payload in data.items():
        if "response" not in payload:
            raise ValueError(f"Round 2A response for {label} missing: {payload.get('error')}")
        out[label] = payload["response"]
    print(f"  loaded Round 2A responses from {latest.name}", flush=True)
    return out


R2A_RESPONSES = _load_round2a()

# ---------------------------------------------------------------------------
# Prompt components (carry Round 2A preamble and new R2B-specific instruction)
# ---------------------------------------------------------------------------

STAGE6_MATH = r"""
## CDSFL Stage 6 — Unified Self-Assessment Equation (canonical)

    R_k(i) = R_k(i-1) * (1 - q) / (1 - q * R_k(i-1))
    q     = eta * d * p

### Stage 6 eta decomposition

    eta_combined = eta_int * (1 - c_ext * (1 - nu_k))

### Orthogonality (load-bearing)

    R_k    measures VALIDITY
    nu_k   measures NOVELTY
    c_ext  measures SEARCH QUALITY

### Divergence modulator channel

    m_div in {1.00, 0.85, 0.70, 0.60}
    eta_int_modulated = m_div * eta_int
    eta_combined = eta_int_modulated * (1 - c_ext * (1 - nu_k))
    q = eta_combined * d * p

    FORBIDDEN: m_div as pre-factor on R_k.
    FORBIDDEN: m_div counting toward nu_k.
"""

FFAFP = r"""
## FFAFP — Find, Follow, Analyse, Fix, P-pass

FIND, FOLLOW, ANALYSE (use SymPy/z3/NumPy/Wolfram etc.), FIX, P-PASS.
Follow comes before Fix. Tool output IS the evidence.
"""

STANDING_POLICY = r"""
## Standing policy (founder directives, 2026-04-20)

P1. Shadow-promotion-now — activate now, defer only on demonstrable harm.
P2. Runner v1 preservation — v1 default for Exp 40; v2 promotion blocked.
P3. 15 experiments — Exp 40-53 components + Exp 54 integration.
P4. Synthesis qualifier — synthesis only if demonstrably better than best
    single; otherwise pick most robust / most flexible.
"""

R2B_INSTRUCTION = r"""
## Round 2B instruction (yield-or-refute, with mechanical compliance check)

You have your own Round 2A answer (attached below, labelled "YOUR R2A
ANSWER") and the Round 2A answers of the four other panel models
(labelled "PEER R2A ANSWERS"). Your task is to produce a Round 2B answer
for each of the six questions (Q1-Q6).

For each question:

  * If your Round 2A position AGREES with the panel consensus (as
    visible from the four other answers), RESTATE your position briefly
    (one paragraph) and confirm it stands.

  * If your Round 2A position DIFFERS from the panel consensus on any
    point, on each such point you must either:

      (1) YIELD WITH EXPLICIT REASONS — name the specific peer model(s),
          include a LITERAL QUOTED SUBSTRING from that model's R2A
          answer that was load-bearing to your change of position, name
          the reason type (e.g., math_error, logical_gap, unsupported
          assumption, scope_error, corrected_misread, tool_output,
          other), and state your new position.

      (2) REFUTE WITH EXPLICIT REASONS — name the specific peer
          model(s), include a LITERAL QUOTED SUBSTRING from that
          model's R2A answer that is the error, explain why the peer's
          reasoning is wrong or incomplete, and restate your position
          with reasons why it is stronger.

  * If the panel consensus is itself split (e.g., 3-2 or 4-1), identify
    which side you align with (or reject both with a third position)
    and apply the yield-or-refute rule against the side you do NOT
    align with.

Mechanical compliance check (post-processing): any quoted substring you
present as load-bearing to a yield MUST be a LITERAL SUBSTRING of the
cited peer's R2A answer. If it is not, the yield is classified as a
compliance yield in post-processing and flagged for founder review.

Apply P4 (synthesis qualifier) to any composite position you propose.

A yield without reasons is a non-answer. A restatement without addressing
a visible disagreement is a non-answer. Producing a menu of options for
the founder to choose from is not acceptable.
"""

# ---------------------------------------------------------------------------
# Six Round 2A questions (re-stated briefly for Round 2B convenience)
# ---------------------------------------------------------------------------

QUESTIONS_RECAP = r"""
## The six questions (unchanged from Round 2A)

Q1. Activation sequence under shadow-promotion-now:
    items {(i) SMT fix, (ii) 1E.10 wrapper with m_div=1.0 hardcoded,
    (iii) K/L/M flip}, timing (before / between / after Round 2B-3),
    instrumentation for (ii).

Q2. Verdict combination rule — (alpha) first-definitive + veto,
    (beta) confidence-weighted + veto, (gamma) composite. Apply P4.

Q3. Novelty-vs-hallucination boundary — can Stage 6 provide a theoretical
    upper bound? If yes, derive; if no, state why and what data is needed.

Q4. Compelled-convergence instrumentation — fields to distinguish
    reasoned yield from compliance yield.

Q5. Runner v1 preservation — additional Exp 40 log fields + acceptance
    criteria to support/falsify the preservation case for Exp 41-53.

Q6. Exp 40 topology — (a) star for 40, paired-challenge from 41;
    (b) paired-challenge for 40; (c) star at 40, paired-challenge at 41,
    compare deliberately.
"""

# ---------------------------------------------------------------------------
# Prompt builder (per-model; embeds that model's R2A + the 4 peers' R2As)
# ---------------------------------------------------------------------------

def build_prompt(self_label: str) -> str:
    self_display = LABEL_DISPLAY[self_label]
    self_r2a = R2A_RESPONSES[self_label]
    peer_blocks = []
    for peer_label in ("gemini", "codex", "cc2", "chatgpt", "deepseek"):
        if peer_label == self_label:
            continue
        peer_display = LABEL_DISPLAY[peer_label]
        peer_r2a = R2A_RESPONSES[peer_label]
        peer_blocks.append(f"""\
### PEER R2A ANSWER — {peer_display}

{peer_r2a}
""")
    peer_section = "\n---\n\n".join(peer_blocks)

    return f"""\
# Exp 40 Pre-launch Panel Review — Round 2B of 3

You ({self_display}) have completed Round 2A. This is Round 2B: the
yield-or-refute step. You will see your own Round 2A answer and the
Round 2A answers of the four other panel models, verbatim. You must
now converge with the rest of the panel on single definitive positions,
yielding or refuting with reasons on each divergent point.

Protocol: CDSFL + FFAFP, Stage 6 math as arbiter. Formal conclusions in
prose. No qualitative opt-out.

---

{STAGE6_MATH}

---

{FFAFP}

---

{STANDING_POLICY}

---

{R2B_INSTRUCTION}

---

{QUESTIONS_RECAP}

---

## YOUR R2A ANSWER — {self_display}

{self_r2a}

---

{peer_section}

---

## Charge for Round 2B

Produce one definitive position per question with full workings. For
each divergent point, apply yield-or-refute with literal quoted
substrings. Apply P4 where a synthesis is proposed.

Word budget: up to 3,500 words across the six answers.
"""


# ---------------------------------------------------------------------------
# Dispatch (identical structure to Round 2A)
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
                timeout=420,
                max_retries=5,
                backoff_base=3.0,
            )
        elif api == "claude_cli":
            response = call_claude_cli(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=prompt,
                max_tokens=32768,
                timeout=1200,
                max_retries=1,
            )
        elif api == "openrouter":
            response = call_openrouter(
                model_id=model_id,
                system_prompt=CDSFL_TEXT,
                user_prompt=prompt,
                max_tokens=32768,
                timeout=420,
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
            print(f"  [{label}] falling back to Gemini via OpenRouter...", flush=True)
            try:
                t0b = time.monotonic()
                response = call_openrouter(
                    model_id="google/gemini-3.1-pro",
                    system_prompt=CDSFL_TEXT,
                    user_prompt=prompt,
                    max_tokens=32768,
                    timeout=420,
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
                print(f"  [{label}] OpenRouter fallback also FAILED: {e2}", flush=True)

        return {"label": label, "error": str(e), "time_s": round(elapsed, 1)}


def run_confer() -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'=' * 72}")
    print("  EXP 40 PRE-LAUNCH PANEL REVIEW — Round 2B of 3")
    print(f"  Timestamp: {ts}")
    print("  Protocol: CDSFL + FFAFP, Stage 6 math as arbiter")
    print("  Mode: yield-or-refute with mechanical substring-check")
    print("  Models: ge, cx, cc2, cgpt, ds (parallel, star-with-peer-context)")
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
