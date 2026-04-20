#!/usr/bin/env python3
"""
Exp 40 Pre-launch Panel Review — Round 3 of 3
=============================================

Final lock. Round 2B achieved substantive convergence on all six original
questions. This round closes the four remaining narrow questions:

  Q3-wiring: is Codex's conditional admissibility ceiling on novelty wired
             into the Exp 40 runtime, into post-hoc analysis only, or not
             at all?
  Q4-lock:   exact field names, types, and value constraints for the
             unified reason-trace schema (was description-level in R2B).
  Q5-lock:   exact log field names, types, numeric thresholds, and
             machine-checkable predicates for each of the four
             preservation property families (was property-level in R2B).
  Q6-lock:   formal label — (a) star for Exp 40, or (c) star at 40 +
             paired-challenge at 41 compared deliberately. Operationally
             identical; only the label remains.

Round 3 constraint box additions (founder, 2026-04-20):
  * Most computationally efficient where applicable.
  * Rational in both human and machine terms.
  * Robust.
  * Most effective.
  * Humans will use the system — seamless and painless human UX.
  * "Demonstrably" means: stands up to third-party human scrutiny,
    internally and externally self-consistent, fits the rest of the
    CDSFL schema seamlessly.

Protocol: CDSFL + FFAFP, Stage 6 math as arbiter, compelled convergence,
          no qualitative opt-out, P4 synthesis qualifier.
Models:   Gemini 3.1 Pro, Codex GPT-5.4, CC2 (Opus 4.6), ChatGPT GPT-5.4,
          DeepSeek R1-0528
Dispatch: parallel via ThreadPoolExecutor(max_workers=5)

Round 2B source: confer_exp40_prelaunch_round2b, timestamp loaded at runtime.
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_prelaunch_round3"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

R2B_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_prelaunch_round2b"

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
# Load Round 2B responses
# ---------------------------------------------------------------------------

def _load_round2b() -> dict[str, str]:
    """Return {label: response_text} for all 5 Round 2B models (latest timestamp)."""
    combined_files = sorted(R2B_DIR.glob("combined_*.json"))
    if not combined_files:
        raise FileNotFoundError(f"No Round 2B combined log found in {R2B_DIR}")
    latest = combined_files[-1]
    data = json.loads(latest.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for label, payload in data.items():
        if "response" not in payload:
            raise ValueError(f"Round 2B response for {label} missing: {payload.get('error')}")
        out[label] = payload["response"]
    print(f"  loaded Round 2B responses from {latest.name}", flush=True)
    return out


R2B_RESPONSES = _load_round2b()

# ---------------------------------------------------------------------------
# Prompt components
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

NEW_CONSTRAINTS = r"""
## Round 3 additional constraints (founder, 2026-04-20, tightening the box)

In addition to all prior constraints, every answer you produce in Round 3
must satisfy ALL of the following. Constraint space is narrower than in
Round 2.

C1. Computationally efficient where computation is applicable — minimum
    instrumentation overhead, minimum redundant fields, deterministic
    checks over probabilistic ones where both are available, O(1) or
    O(n) predicates rather than nested loops on hot paths.

C2. Rational in both human and machine terms — machine-parseable
    (deterministic schema, explicit types, explicit enum domains) AND
    human-readable (field names and predicates that a competent outside
    reader understands without a glossary).

C3. Robust — cannot be gamed by an LLM filling fields with surface
    tokens. Predicates must test causal / structural properties, not
    cosmetic ones.

C4. Most effective — closes the epistemic gap the field/predicate was
    designed to close, end-to-end.

C5. Human UX seamlessness — humans (the founder, reviewers, future
    researchers) will USE the system. Logs they read, reports they
    audit, and failures they debug must be painless. No cryptic
    identifiers, no unexplained enums, no schemas that require a
    separate legend to interpret a single row. Error messages point to
    the causing field.

C6. Third-party defensibility — "demonstrably" means an outside reviewer
    (another scientist, another engineer, a peer model) can read your
    answer and verify the claim from your answer + the CDSFL schema
    alone, without privileged context.

C7. Internally and externally self-consistent — your answer does not
    contradict your earlier-in-this-answer claims, does not contradict
    the rest of Round 2B's convergent positions, and uses the same
    Stage 6 symbols / CDSFL identifiers / field-naming conventions as
    the rest of the codebase and directives.

C8. Fits the rest of the CDSFL schema seamlessly — new fields slot
    into the existing telemetry layout, predicates compose with existing
    P-pass infrastructure, enum values extend existing enum families
    rather than introducing parallel vocabularies.

Under these tighter constraints, the panel must converge on the single
most demonstrably efficient, rational, robust, effective, human-usable,
third-party-defensible, and CDSFL-coherent answer per question. P4
applies: no composite unless demonstrably better than the best single.
Otherwise, the most robust / most flexible single answer wins.
"""

R3_INSTRUCTION = r"""
## Round 3 instruction

Round 2A and Round 2B converged on the substance of all six original
questions. Four narrow items remain. Round 3 closes them.

You are given your own Round 2B answer (labelled "YOUR R2B ANSWER") and
the four other models' Round 2B answers (labelled "PEER R2B ANSWERS").
Answer only the four Round 3 questions below.

For each Round 3 question:

  * Give ONE definitive answer consistent with the Round 3 constraints
    (C1-C8 above).
  * If any peer's Round 2B answer is inconsistent with the Round 3
    constraints on this specific point, REFUTE WITH EXPLICIT REASONS:
    name the model, include a LITERAL QUOTED SUBSTRING from that
    model's R2B answer, name which constraint(s) it fails, and state
    your position.
  * If a peer has a Round 2B position stronger than yours on this
    specific point under the Round 3 constraints, YIELD WITH EXPLICIT
    REASONS: name the model, include a LITERAL QUOTED SUBSTRING from
    that model's R2B answer, name which constraint(s) it satisfies
    better, and state your new position.
  * Producing a menu of options for the founder is not acceptable.
  * Omissions are refutations of absent content. Each of the four
    questions MUST be answered.

Mechanical compliance check: yield quotes MUST be literal substrings of
the cited R2B answer. Non-literal-substring quotes are post-processed
as compliance yields.

Apply P4 where a synthesis is proposed. No qualitative opt-out.
"""

QUESTIONS_R3 = r"""
## Round 3 questions — the four residuals

### Q3-wiring (conditional novelty ceiling, operational placement)

Codex derived a conditional upper bound on admissible novelty nu_k for a
chosen residual-validity floor R_min, given eta_int, d, p, c_ext. Round
2B converged 4-1 that this bound is real but explicitly NOT the
novelty/hallucination boundary. Round 3 question: where does this
conditional ceiling live in Exp 40?

  (w1) Wired as a runtime guard-rail inside the v1 runner (flag
       findings exceeding nu_max given session R_min and parameters).
  (w2) Computed only in post-hoc analysis after Exp 40 completes, not
       wired into runtime.
  (w3) Not operationalised in Exp 40 at all; ceiling stays a theoretical
       property of Stage 6 until empirical data motivates a use.

State the single correct choice under C1-C8. If (w1), specify the
runtime check and its cost. If (w2), specify what the post-hoc report
uses it for. If (w3), justify why the operational value does not yet
beat the instrumentation cost.

### Q4-lock (unified reason-trace schema — exact fields)

Round 2B converged on an approximately ten-field unified per-divergence
reason-trace schema with literal-substring enforcement for yield quotes.
Round 3 question: lock the exact field list. For each field provide:

  * EXACT field name (snake_case, consistent with CDSFL schema
    conventions).
  * TYPE (string, int, enum[list of values], hash, bool, float, dict).
  * VALUE CONSTRAINT or validator (e.g., "literal substring of cited
    peer's R2 answer"; "sha256 of canonical JSON of prior position";
    "one of {yield, refute, unchanged}").
  * REQUIRED condition (e.g., "always"; "required if stance=yield";
    "required if a quantitative claim was revised").
  * HUMAN GLOSS (one short clause; what this means for a human reader).

Deliver the list as a single table or single block, with no alternative
schemas. If any peer's R2B proposed field fails C1-C8, refute it by
name and literal-substring quote. If any peer's R2B proposed field is
stronger than yours under C1-C8, yield.

### Q5-lock (v1 preservation predicates — exact thresholds)

Round 2B converged on four property families for v1 preservation:
math-path fidelity, correction fidelity, counterfactual sensitivity,
convergence stability. Round 3 question: lock the exact log fields and
machine-checkable predicates.

For each of the four families, provide:

  * LOG FIELD(S): exact names, types, and per-dispatch vs per-round
    vs per-experiment granularity.
  * PREDICATE(S): the machine-checkable accept/reject rule as a
    Python-ish expression using only the declared field names and
    numeric constants. E.g.,
    "accept <=> forbidden_pattern_hits_on_accepted_findings == 0".
  * HUMAN GLOSS: one short clause explaining what a pass / fail means
    for an outside reader.
  * COUNTERFACTUAL SENSITIVITY: specify the perturbation protocol
    (which parameters perturbed, by how much, on what fraction of
    dispatches, acceptance threshold).

Deliver as a single block. No alternative predicate sets. Apply
yield-or-refute against peer R2B predicates where they fail C1-C8 or
beat yours under C1-C8.

### Q6-lock (topology label)

Round 2B: 4 models select (a) star for Exp 40; 1 model (Codex) selects
(c) star at 40 + paired-challenge at 41, compare deliberately.
Operationally identical. Round 3 question: lock the label that appears
in the Exp 40 design document, runner config, and experiment registry.

Under C5 (human UX seamlessness), C7 (internal/external consistency),
C8 (CDSFL schema fit), and P4 (robust single preferred over composite
absent demonstrated superiority), state the single correct label. If
you are Codex, yield or refute against the 4-model majority under
these specific constraints.
"""

# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_prompt(self_label: str) -> str:
    self_display = LABEL_DISPLAY[self_label]
    self_r2b = R2B_RESPONSES[self_label]
    peer_blocks = []
    for peer_label in ("gemini", "codex", "cc2", "chatgpt", "deepseek"):
        if peer_label == self_label:
            continue
        peer_display = LABEL_DISPLAY[peer_label]
        peer_r2b = R2B_RESPONSES[peer_label]
        peer_blocks.append(f"""\
### PEER R2B ANSWER — {peer_display}

{peer_r2b}
""")
    peer_section = "\n---\n\n".join(peer_blocks)

    return f"""\
# Exp 40 Pre-launch Panel Review — Round 3 of 3

You ({self_display}) have completed Round 2A and Round 2B. This is
Round 3: the final lock. Four narrow residuals remain. The founder has
tightened the constraint box: see C1-C8 below. Under those tighter
constraints, the panel must converge on single definitive answers.

Protocol: CDSFL + FFAFP, Stage 6 math as arbiter. Formal conclusions in
prose. No qualitative opt-out.

---

{STAGE6_MATH}

---

{FFAFP}

---

{STANDING_POLICY}

---

{NEW_CONSTRAINTS}

---

{R3_INSTRUCTION}

---

{QUESTIONS_R3}

---

## YOUR R2B ANSWER — {self_display}

{self_r2b}

---

{peer_section}

---

## Charge for Round 3

Produce one definitive answer per Round 3 question (Q3-wiring, Q4-lock,
Q5-lock, Q6-lock) under constraints C1-C8. Apply yield-or-refute with
literal quoted substrings. Apply P4 where a synthesis is proposed.

Word budget: up to 3,000 words across the four answers. Be precise and
short rather than broad and long.
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
    print("  EXP 40 PRE-LAUNCH PANEL REVIEW — Round 3 of 3")
    print(f"  Timestamp: {ts}")
    print("  Protocol: CDSFL + FFAFP, Stage 6 math as arbiter")
    print("  Mode: final lock under tightened constraints C1-C8")
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
